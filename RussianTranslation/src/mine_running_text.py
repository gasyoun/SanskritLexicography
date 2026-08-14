#!/usr/bin/env python
"""H186 Track B — running-text term mining (SEPARATE, lower-confidence `mined` TM layer).

Russian scholarly prose (monographs, term-encyclopedias, lecture transcripts) mentions
Sanskrit terms *in passing* and glosses some of them inline — but carries NO verse-level
Sanskrit↔Russian alignment, so `build_corpus_lexicon.py` (which needs aligned sa/ru
verse pairs) cannot touch it. This miner asks DeepSeek to pull ONLY the Sanskrit→Russian
term glosses that a passage EXPLICITLY states, and lands them in a quarantined
`corpus_lexicon.mined.jsonl` tagged `tier: mined` — NEVER the clean 1.09M
`corpus_lexicon.jsonl`. Mined pairs are noisier; harvest/QA weight them below the
dictionaries and the verse-aligned corpus.

Reuses build_corpus_lexicon.deepseek() (retry/backoff), .to_slp1(), .has_cyr() — no new
aligner, no new HTTP client. The never-invent / has_cyr / ru!=sa guards are mandatory
(the 166k-hallucination lesson applies here too — a "gloss" DeepSeek fabricates from
world-knowledge instead of the passage is exactly the failure mode we refuse).

  python mine_running_text.py test  <textfile> [N]   extract, print (no write)
  python mine_running_text.py mine  <textfile> [N] [workers]   → corpus_lexicon.mined.jsonl
  python mine_running_text.py mineall [--min-tb 15] [--include a,b] [--exclude c] [--plan] [--workers 8]
                                                     scan the whole SM folder, apply the
                                                     deterministic selection rule, mine each
                                                     selected running-text source (resumable;
                                                     H224 works and *.raw skipped unless --include)
  python mine_running_text.py status                 mined rows + distinct keys + per-source
  python mine_running_text.py sample-new [--n 30]    stratified precision sample of NEW sources
  python mine_running_text.py selftest               offline selection-rule checks
  python mine_running_text.py aligned-works          print the 116 aligned works (needs corpus)

Empty 0-pair successes are recorded in corpus_lexicon.mined.done.jsonl so
resume does not remine them. API failures stay pending. Never writes
corpus_lexicon.jsonl.
"""
import datetime, json, os, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import build_corpus_lexicon as bcl   # to_slp1(), has_cyr(), SM, REJECT_RU — not the clean lexicon writer

HERE = os.path.dirname(os.path.abspath(__file__))
SM = bcl.SM
OUT = os.path.join(HERE, 'corpus_lexicon.mined.jsonl')
CALL_LOG = os.path.join(HERE, 'mine_running_text.calls.jsonl')
DONE_LOG = os.path.join(HERE, 'corpus_lexicon.mined.done.jsonl')
ALIGNED_WORKS_FILE = os.path.join(HERE, '..', 'pwg_ru', 'aligned_works.txt')
MODEL = os.environ.get('DEEPSEEK_MODEL', 'deepseek-v4-flash')
# Pre-16-08-2026 16:00 UTC Flash card (USD / 1M). After that, off-peak/peak rows.
_PRICE = {
    'pre-1608': {'cache_miss_in': 0.14, 'cache_hit_in': 0.0028, 'out': 0.28},
    'after-1608-offpeak': {'cache_miss_in': 0.22, 'cache_hit_in': 0.007, 'out': 0.66},
    'after-1608-peak': {'cache_miss_in': 0.44, 'cache_hit_in': 0.014, 'out': 1.32},
}
_PEAK_START = datetime.datetime(2026, 8, 16, 16, 0, tzinfo=datetime.timezone.utc)
_LOG_LOCK = threading.Lock()

# ── mineall selection rule (H224 — baked in so no future session re-derives it) ──
# (2) verse-aligned works (in corpus_lexicon.jsonl) are Track A's domain → skipped via
#     load_aligned_works(); (3) registered dictionaries / glossaries / non-Sanskrit →
#     DENYLIST; (4) an explicit index file skipped by name → SKIP_INDEX; other low-yield
#     sources fall out of the < --min-tb term-bearing gate. Every skip is logged.
DENYLIST = {
    'kochergina', 'knauer', 'frish', 'slovar-smirnova', 'kossovich', 'kewa', 'dic_mw',
    'dic_apte', 'dsg', 'erman-temkin', 'fasmer-dr-ind', 'slovar-potapovoy',
    'slovar-grintsera-iz-ramayany-1-2', 'slovar-grintsera-iz-bada-kadambari',
    'ramayana-3-slovar', 'toporov', 'warnemyr', 'iliada_gnedich',
}
SKIP_INDEX = {'ukazateli-makhabkharaty'}   # 17,915-line MBh index, 29 term-bearing (0%)
# H224 scale already mined these 8; local mined.jsonl is gitignored and often
# absent in a fresh worktree. Delta-only (H2679): skip unless --include.
H224_MINED = {
    'induizm-dzhaynizm-sikkhizm',
    'mify_759_ind',
    'syrkin_tom_1_utf',
    'biruni',
    'stati-makhabkharaty',
    'stepanyants',
    'yoga-bessmertie-i-cvoboda-mircha-eliade-per-pakhomova',
    'kommentarii-k-makhabkharate',
}
# the 6,291-passage MBh commentary — always mined LAST (dominant cost)
MINE_LAST = 'kommentarii-k-makhabkharate'


def _utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def _price_card(now=None):
    now = now or _utcnow()
    if now < _PEAK_START:
        return 'pre-1608'
    hour = now.hour
    if (1 <= hour < 4) or (6 <= hour < 10):
        return 'after-1608-peak'
    return 'after-1608-offpeak'


def _usd(usage, card):
    prices = _PRICE[card]
    prompt = int(usage.get('prompt_tokens') or 0)
    completion = int(usage.get('completion_tokens') or 0)
    cached = int((usage.get('prompt_tokens_details') or {}).get('cached_tokens') or 0)
    miss = max(0, prompt - cached)
    return (miss * prices['cache_miss_in'] + cached * prices['cache_hit_in']
            + completion * prices['out']) / 1_000_000.0


def _log_call(rec):
    with _LOG_LOCK:
        with open(CALL_LOG, 'a', encoding='utf-8', newline='') as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n')


def mine_deepseek(user, work=None, passage=None):
    """One DeepSeek JSON-object call with per-HTTP JSONL (spend-auth). Never writes
    the clean 1.09M lexicon — that path stays in build_corpus_lexicon.py unused."""
    key = bcl.KEY
    if key is None:
        bcl.KEY = bcl._key()
        key = bcl.KEY
    last = None
    for a in range(bcl.RETRIES):
        now = _utcnow()
        card = _price_card(now)
        rec = {
            'utc': now.isoformat(),
            'model': MODEL,
            'served_model': None,
            'effort': None,
            'work': work,
            'passage': passage,
            'attempt': a + 1,
            'price_card': card,
            'prompt_tokens': None,
            'completion_tokens': None,
            'reasoning_tokens': None,
            'cache_tokens': None,
            'usd': None,
            'finish_reason': None,
            'error': None,
        }
        if card == 'after-1608-peak' and not os.environ.get('ALLOW_DEEPSEEK_PEAK'):
            rec['error'] = 'refuse_if_peak'
            _log_call(rec)
            return None
        try:
            r = requests.post(
                bcl.API, headers={'Authorization': 'Bearer ' + key},
                json={'model': MODEL, 'temperature': 0,
                      'response_format': {'type': 'json_object'},
                      'messages': [{'role': 'system', 'content': SYS_MINE},
                                   {'role': 'user', 'content': user}]},
                timeout=(bcl.CONNECT_TIMEOUT, bcl.READ_TIMEOUT))
            body = r.json() if r.content else {}
            usage = body.get('usage') or {}
            rec['served_model'] = body.get('model')
            rec['prompt_tokens'] = usage.get('prompt_tokens')
            rec['completion_tokens'] = usage.get('completion_tokens')
            rec['reasoning_tokens'] = (usage.get('completion_tokens_details') or {}).get(
                'reasoning_tokens')
            rec['cache_tokens'] = (usage.get('prompt_tokens_details') or {}).get('cached_tokens')
            rec['usd'] = _usd(usage, card) if usage else None
            rec['finish_reason'] = ((body.get('choices') or [{}])[0]).get('finish_reason')
            if r.status_code >= 400 and bcl.transient_http(r.status_code):
                rec['error'] = 'transient HTTP %s' % r.status_code
                _log_call(rec)
                raise requests.HTTPError('transient HTTP %s: %s' %
                                         (r.status_code, r.text[:200]), response=r)
            if r.status_code >= 400:
                rec['error'] = 'HTTP %s' % r.status_code
                _log_call(rec)
                r.raise_for_status()
            _log_call(rec)
            return ((body.get('choices') or [{}])[0].get('message') or {}).get('content')
        except Exception as ex:
            last = ex
            if rec.get('error') is None:
                rec['error'] = str(ex)[:300]
                _log_call(rec)
            if a == bcl.RETRIES - 1:
                sys.stderr.write('deepseek fail: %s\n' % ex)
                return None
            retry_after = getattr(getattr(ex, 'response', None), 'headers', {}).get('Retry-After')
            wait = bcl.backoff(a, retry_after=retry_after)
            sys.stderr.write('deepseek retry %d/%d after %.1fs: %s\n' %
                             (a + 1, bcl.RETRIES, wait, ex))
            time.sleep(wait)
    return None


def load_aligned_works():
    """The 116 verse-aligned works to skip. Prefer the live corpus (authoritative);
    fall back to the committed frozen list (corpus is gitignored, absent in fresh
    worktrees). Errors loudly if neither is available."""
    corpus = os.path.join(HERE, 'corpus_lexicon.jsonl')
    if os.path.exists(corpus):
        seen = set()
        for line in open(corpus, encoding='utf-8'):
            try:
                w = json.loads(line).get('work')
            except Exception:
                continue
            if w:
                seen.add(w)
        return seen
    if os.path.exists(ALIGNED_WORKS_FILE):
        return {ln.strip() for ln in open(ALIGNED_WORKS_FILE, encoding='utf-8')
                if ln.strip() and not ln.startswith('#')}
    raise SystemExit('no corpus_lexicon.jsonl and no %s — cannot determine aligned works'
                     % ALIGNED_WORKS_FILE)


def count_term_bearing(textfile):
    """Term-bearing Russian passage count for one work (drives the --min-tb gate)."""
    return sum(1 for _ in entries(textfile))

# A passage is worth an API call only if it plausibly carries a Sanskrit term to gloss:
# a Latin token with IAST diacritics, Devanagari, or an explicit Sanskrit-origin marker.
IAST = re.compile('[āīūṛṝḷḹṃṁḥṅñṭḍṇśṣ]', re.I)
DEV = re.compile('[ऀ-ॿ]')
MARKER = re.compile(r'санскр|древнеинд\.|от\s+корня|от\s+санскр|букв\.|IAST|деванагар', re.I)


def term_bearing(text):
    return bool(text) and (bool(IAST.search(text)) or bool(DEV.search(text))
                           or bool(MARKER.search(text)))


SYS_MINE = (
    'You extract Sanskrit→Russian TERM GLOSSES from a passage of Russian scholarly '
    'prose that discusses Sanskrit terms. For each Sanskrit term the passage '
    'EXPLICITLY glosses or translates, output {"sa": <the Sanskrit term in IAST '
    'transliteration, dictionary/citation form>, "ru": <the Russian meaning/equivalent '
    'AS STATED IN THIS PASSAGE>}. HARD RULES: '
    '(1) The Russian gloss MUST be literally present or directly stated in THIS passage '
    '— never invent, infer, or add outside knowledge; if the passage names a term but '
    'gives no Russian meaning for it, OMIT that term. '
    '(2) "sa" must be a genuine Sanskrit word in IAST (Latin letters + diacritics), not '
    'a Russified Cyrillic spelling; if the passage gives only a Cyrillic form with no '
    'Latin/IAST and no unambiguous transliteration, OMIT it. '
    '(3) Give the short lexical gloss, not a whole sentence. '
    'Output ONLY JSON: {"pairs":[{"sa":"...","ru":"..."}]}. Empty list if nothing '
    'qualifies. Never echo the Sanskrit as its own gloss.')


def mine_passage(text, work=None, passage=None):
    out = mine_deepseek('Passage (Russian):\n%s' % text[:2400], work=work, passage=passage)
    if not out:
        return None          # None = API/JSON failure (distinct from "0 pairs found")
    try:
        return json.loads(out).get('pairs', [])
    except Exception:
        return []


def entries(textfile):
    """Yield (passage_ref, group, text) for term-bearing Russian passages of a work."""
    work = textfile.replace('.jsonl', '')
    for line in open(os.path.join(SM, textfile), encoding='utf-8'):
        e = json.loads(line)
        if e.get('deleted') or e.get('lang') not in (None, 'ru'):
            continue
        t = e.get('text') or ''
        if term_bearing(t):
            yield e.get('passage', e.get('group', '')), e.get('group', ''), t, work


def done_refs():
    s = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding='utf-8'):
            try:
                r = json.loads(line)
                s.add((r.get('work'), r.get('passage')))
            except Exception:
                pass
    if os.path.exists(DONE_LOG):
        for line in open(DONE_LOG, encoding='utf-8'):
            try:
                r = json.loads(line)
                if r.get('status') in ('pairs', 'empty'):
                    s.add((r.get('work'), r.get('passage')))
            except Exception:
                pass
    return s


def mark_done(work, passage, n_rows):
    rec = {
        'work': work,
        'passage': passage,
        'status': 'pairs' if n_rows else 'empty',
        'n_rows': n_rows,
        'utc': _utcnow().isoformat(),
    }
    with _LOG_LOCK:
        with open(DONE_LOG, 'a', encoding='utf-8', newline='') as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n')


def rows_from(passage, group, text, work):
    pairs = mine_passage(text, work=work, passage=passage)
    if pairs is None:
        return None
    rows, seen = [], set()
    for p in pairs:
        sa_w = (p.get('sa') or '').strip()
        ru_w = (p.get('ru') or '').strip()
        slp1 = bcl.to_slp1(sa_w)
        if not (slp1 and bcl.has_cyr(ru_w)):          # gloss must be real Russian
            continue
        if ru_w == sa_w or ru_w in bcl.REJECT_RU:      # echo / refusal string
            continue
        # the extracted Cyrillic gloss must actually occur in the source passage —
        # a cheap, deterministic anti-hallucination check on top of the model prompt.
        if ru_w not in text:
            continue
        key = (slp1, ru_w)
        if key in seen:
            continue
        seen.add(key)
        rows.append({'slp1': slp1, 'sa': sa_w, 'ru': ru_w, 'work': work,
                     'passage': passage, 'group': group,
                     'kind': 'mined', 'tier': 'mined'})
    return rows


def cmd_test(args):
    tf = args[0]
    n = int(args[1]) if len(args) > 1 else 5
    for i, (passage, group, text, work) in enumerate(entries(tf)):
        if i >= n:
            break
        print('=' * 20, work, passage)
        print(' ', text[:200])
        rows = rows_from(passage, group, text, work)
        for r in (rows or []):
            print('    %-20s → slp1=%-14s → %s' % (r['sa'], r['slp1'], r['ru']))


def cmd_mine(args):
    tf = args[0]
    n = int(args[1]) if len(args) > 1 else 10**9
    workers = int(args[2]) if len(args) > 2 else 8
    done = done_refs()
    work0 = tf.replace('.jsonl', '')
    items = [(p, g, t, w) for p, g, t, w in entries(tf) if (work0, p) not in done][:n]
    wrote = failed = empty = 0
    with open(OUT, 'a', encoding='utf-8', newline='') as out, ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(rows_from, p, g, t, w): (p, w) for p, g, t, w in items}
        for fut in as_completed(futs):
            passage, work = futs[fut]
            rows = fut.result()
            if rows is None:
                failed += 1
                continue
            for r in rows:
                out.write(json.dumps(r, ensure_ascii=False) + '\n')
                wrote += 1
            out.flush()
            mark_done(work, passage, len(rows))
            if not rows:
                empty += 1
    print('%s: %d term-bearing passages → %d mined pairs, %d empty, %d API failures → %s'
          % (work0, len(items), wrote, empty, failed, os.path.basename(OUT)))


def select_sources(min_tb=15, include=None, exclude=None):
    """Apply the deterministic selection rule to the whole SM folder.

    Returns (selected, skips) where `selected` is a list of (work, tb_count) ordered
    cheap-first with MINE_LAST forced to the end, and `skips` is a list of
    (work, reason) for every file NOT mined — so nothing is silently dropped.
    `include` forces a work in (still counted); `exclude` forces it out.
    """
    aligned = load_aligned_works()
    include = set(include or [])
    exclude = set(exclude or [])
    files = sorted(f for f in os.listdir(SM) if f.endswith('.jsonl'))
    selected, skips = [], []
    for f in files:
        work = f[:-len('.jsonl')]
        if work in exclude:
            skips.append((work, 'excluded (--exclude)'))
            continue
        forced = work in include
        if not forced:
            if work in aligned:
                skips.append((work, 'verse-aligned (Track A domain)'))
                continue
            if work in DENYLIST:
                skips.append((work, 'dictionary/glossary/non-Sanskrit (denylist)'))
                continue
            if work in SKIP_INDEX:
                skips.append((work, 'index file (skip-by-name)'))
                continue
            if work.endswith('.raw'):
                skips.append((work, 'raw companion (duplicate of processed jsonl)'))
                continue
            if work in H224_MINED:
                skips.append((work, 'already mined (H224 scale; local mined.jsonl often absent — delta only)'))
                continue
        tb = count_term_bearing(f)
        if not forced and tb < min_tb:
            skips.append((work, 'low-yield: %d term-bearing < min-tb %d' % (tb, min_tb)))
            continue
        selected.append((work, tb))
    # cheap-first, then MINE_LAST forced to the very end (dominant cost)
    selected.sort(key=lambda wt: (wt[0] == MINE_LAST, wt[1]))
    return selected, skips


def cmd_mineall(args):
    min_tb, include, exclude, workers, plan = 15, None, None, 8, False
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--min-tb':
            i += 1; min_tb = int(args[i])
        elif a == '--include':
            i += 1; include = [x for x in args[i].split(',') if x]
        elif a == '--exclude':
            i += 1; exclude = [x for x in args[i].split(',') if x]
        elif a == '--workers':
            i += 1; workers = int(args[i])
        elif a == '--plan':
            plan = True
        else:
            print('unknown arg:', a); return
        i += 1

    selected, skips = select_sources(min_tb, include, exclude)
    done = done_refs()
    print('=== mineall selection (min-tb=%d) ===' % min_tb)
    for work, reason in skips:
        print('  SKIP  %-52s %s' % (work, reason))
    print('  ---')
    tot = pending_tot = 0
    planned = []
    for work, tb in selected:
        n_done = sum(1 for r in done if r[0] == work)
        pending = max(0, tb - n_done)
        tot += tb
        pending_tot += pending
        tag = 'MINE' if pending else 'DONE'
        print('  %-4s  %-52s %d term-bearing  pending=%d done_refs=%d'
              % (tag, work, tb, pending, n_done))
        planned.append((work, tb, pending))
    print('  === %d sources selected, %d term-bearing, %d pending (done_refs-missing) ==='
          % (len(selected), tot, pending_tot))
    if plan:
        print('(--plan: no API calls made)')
        return

    mineable = [(w, tb, p) for w, tb, p in planned if p]
    skipped_done = len(planned) - len(mineable)
    if skipped_done:
        print('skipping %d already-mined selected sources (done_refs complete)' % skipped_done)
    for idx, (work, tb, pending) in enumerate(mineable, 1):
        print('\n[%d/%d] mining %s (%d pending of %d term-bearing) ...'
              % (idx, len(mineable), work, pending, tb), flush=True)
        cmd_mine([work + '.jsonl', str(10**9), str(workers)])


def cmd_aligned_works(args):
    for w in sorted(load_aligned_works()):
        print(w)


def cmd_status(args):
    import collections
    if not os.path.exists(OUT):
        print('no', OUT); return
    per = collections.Counter(); keys = set(); n = 0
    for line in open(OUT, encoding='utf-8'):
        try:
            r = json.loads(line); n += 1
            per[r.get('work')] += 1; keys.add((r.get('slp1'), r.get('ru')))
        except Exception:
            pass
    print('mined rows: %d | distinct (slp1,ru): %d' % (n, len(keys)))
    for w, c in per.most_common():
        print('  %6d  %s' % (c, w))


def cmd_sample_new(args):
    """Deterministic stratified 30-row sample of NEW (non-H224) mined pairs — H224 method."""
    n = 30
    outp = os.path.join(HERE, '..', 'pwg_ru', 'running_text_mining_precision_sample_h2679.jsonl')
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--n':
            i += 1; n = int(args[i])
        elif a == '--out':
            i += 1; outp = args[i]
        else:
            print('unknown arg:', a); return
        i += 1
    if not os.path.exists(OUT):
        print('no', OUT); return
    by = {}
    for line in open(OUT, encoding='utf-8'):
        try:
            r = json.loads(line)
        except Exception:
            continue
        w = r.get('work') or ''
        if w in H224_MINED or w.endswith('.raw'):
            continue
        by.setdefault(w, []).append(r)
    works = sorted(by)
    if not works:
        print('no new-source rows to sample'); return
    for w in works:
        by[w].sort(key=lambda r: (r.get('passage') or '', r.get('slp1') or '', r.get('ru') or ''))
    quota, rem = divmod(n, len(works))
    picked = []
    for i, w in enumerate(works):
        take = quota + (1 if i < rem else 0)
        rows = by[w]
        if take <= 0 or not rows:
            continue
        if take >= len(rows):
            picked.extend(rows)
            continue
        step = max(1, len(rows) // take)
        for k in range(take):
            picked.append(rows[min(k * step, len(rows) - 1)])
    picked = picked[:n]
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    with open(outp, 'w', encoding='utf-8', newline='') as fh:
        for r in picked:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('wrote %d rows from %d new sources → %s' % (len(picked), len(works), outp))


def cmd_selftest(args):
    """Offline selection-rule checks (no API). Needs the SM jsonl folder."""
    failed = 0

    def check(cond, msg):
        nonlocal failed
        if cond:
            print('PASS', msg)
        else:
            print('FAIL', msg)
            failed += 1

    selected, skips = select_sources()
    skip_d = {w: r for w, r in skips}
    sel_d = {w: tb for w, tb in selected}
    check('ukazateli-makhabkharaty' in skip_d, 'index skip-by-name')
    check(skip_d.get('ukazateli-makhabkharaty', '').startswith('index'), 'index reason')
    raws = [w for w in skip_d if w.endswith('.raw')]
    check(len(raws) >= 1, 'raw companions skipped (%d)' % len(raws))
    check(all('raw companion' in skip_d[w] for w in raws), 'raw skip reason')
    for w in H224_MINED:
        check(w in skip_d, 'H224 already-mined skip: %s' % w)
        check(w not in sel_d, 'H224 not selected: %s' % w)
    check(MINE_LAST not in sel_d, 'kommentarii not in delta (H224 already-mined)')
    if selected:
        check(selected[-1][0] != MINE_LAST or selected[-1][0] == selected[-1][0],
              'sort stable')
        tbs = [tb for w, tb in selected if w != MINE_LAST]
        check(tbs == sorted(tbs), 'cheap-first order on delta')
    check('corpus_lexicon.jsonl' not in OUT, 'mined OUT is not the clean lexicon')
    check(os.path.basename(OUT) == 'corpus_lexicon.mined.jsonl', 'mined filename')
    check(os.path.basename(DONE_LOG) == 'corpus_lexicon.mined.done.jsonl', 'done sidecar name')
    check(os.path.abspath(OUT) != os.path.abspath(bcl.OUT), 'mined path != clean lexicon')
    print('selftest %s (%d fail)' % ('PASS' if failed == 0 else 'FAIL', failed))
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    rest = sys.argv[2:]
    {'test': cmd_test, 'mine': cmd_mine, 'mineall': cmd_mineall,
     'aligned-works': cmd_aligned_works, 'status': cmd_status,
     'sample-new': cmd_sample_new, 'selftest': cmd_selftest}.get(cmd, cmd_status)(rest)
