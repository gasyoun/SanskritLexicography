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
                                                     selected running-text source (resumable)
  python mine_running_text.py status                 mined rows + distinct keys + per-source
  python mine_running_text.py aligned-works          print the 116 aligned works (needs corpus)
"""
import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import build_corpus_lexicon as bcl   # deepseek(), to_slp1(), has_cyr(), SM, REJECT_RU

HERE = os.path.dirname(os.path.abspath(__file__))
SM = bcl.SM
OUT = os.path.join(HERE, 'corpus_lexicon.mined.jsonl')
ALIGNED_WORKS_FILE = os.path.join(HERE, '..', 'pwg_ru', 'aligned_works.txt')

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
# the 6,291-passage MBh commentary — always mined LAST (dominant cost)
MINE_LAST = 'kommentarii-k-makhabkharate'


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


def mine_passage(text):
    out = bcl.deepseek('Passage (Russian):\n%s' % text[:2400], system=SYS_MINE)
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
    return s


def rows_from(passage, group, text, work):
    pairs = mine_passage(text)
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
    wrote = failed = 0
    with open(OUT, 'a', encoding='utf-8', newline='') as out, ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(rows_from, p, g, t, w): p for p, g, t, w in items}
        for fut in as_completed(futs):
            rows = fut.result()
            if rows is None:
                failed += 1
                continue
            for r in rows:
                out.write(json.dumps(r, ensure_ascii=False) + '\n')
                wrote += 1
            out.flush()
    print('%s: %d term-bearing passages → %d mined pairs, %d API failures → %s'
          % (work0, len(items), wrote, failed, os.path.basename(OUT)))


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
    print('=== mineall selection (min-tb=%d) ===' % min_tb)
    for work, reason in skips:
        print('  SKIP  %-52s %s' % (work, reason))
    print('  ---')
    tot = 0
    for work, tb in selected:
        print('  MINE  %-52s %d term-bearing' % (work, tb))
        tot += tb
    print('  === %d sources selected, %d term-bearing passages total ===' % (len(selected), tot))
    if plan:
        print('(--plan: no API calls made)')
        return

    done = done_refs()
    for idx, (work, tb) in enumerate(selected, 1):
        pending = tb - sum(1 for r in done if r[0] == work)  # rough; cmd_mine is exact
        print('\n[%d/%d] mining %s (~%d term-bearing, resuming) ...'
              % (idx, len(selected), work, tb), flush=True)
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


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    rest = sys.argv[2:]
    {'test': cmd_test, 'mine': cmd_mine, 'mineall': cmd_mineall,
     'aligned-works': cmd_aligned_works, 'status': cmd_status}.get(cmd, cmd_status)(rest)
