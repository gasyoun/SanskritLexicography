#!/usr/bin/env python
"""P1 — corpus word-alignment lexicon (DeepSeek).

Reads the verse-aligned Sanskrit↔Russian corpus bundled in SamudraManthanam and,
per aligned verse pair, asks DeepSeek to map each Sanskrit content word to its
Russian rendering in that translation. Accumulates a durable, SLP1-keyed
Sanskrit→Russian lexicon (the reuse multiplier for the pwg_ru harvest).

CODE is committed; the API key (src/.env) and the output (corpus_lexicon.jsonl)
are gitignored. Append-only + resumable (skips verse groups already processed).

  python build_corpus_lexicon.py test  [textfile]      align 1 pair, print
  python build_corpus_lexicon.py build <textfile> [N]  align N pairs → lexicon
  python build_corpus_lexicon.py status                 entries + distinct keys
"""
import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import build_src
import corpus_gate as cg

HERE = os.path.dirname(os.path.abspath(__file__))
SM = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'SamudraManthanam',
                                   'web', 'corpus_builder', 'jsonl'))
OUT = os.path.join(HERE, 'corpus_lexicon.jsonl')
ENV = os.path.join(HERE, '.env')
API = 'https://api.deepseek.com/chat/completions'


def _key():
    for line in open(ENV, encoding='utf-8'):
        if line.strip().startswith('DEEPSEEK_API_KEY='):
            return line.split('=', 1)[1].strip()
    sys.exit('no DEEPSEEK_API_KEY in .env')


KEY = None
_STRATA_PATH = os.path.join(HERE, 'corpus_strata.json')
STRATA = json.load(open(_STRATA_PATH, encoding='utf-8')) if os.path.exists(_STRATA_PATH) else {}

# A Russian segment with NO Cyrillic letter is an UNTRANSLATED placeholder
# (e.g. '…' / '—' in works the corpus has not yet rendered). Feeding such a
# segment to DeepSeek makes it HALLUCINATE fluent alignments against a
# translation that does not exist — pure invention. We refuse to align, or to
# write, any Russian that carries no Cyrillic.
CYR = re.compile('[Ѐ-ӿԀ-ԯⷠ-ⷿꙀ-ꚟ]')
REJECT_RU = {'(no clear counterpart)', 'нет соответствия', '—', '…', '...'}


def has_cyr(s):
    return bool(s) and bool(CYR.search(s))
SYS = ('You align a Sanskrit verse to its Russian translation at the WORD level. '
       'For each notable Sanskrit CONTENT word (noun, verb, adjective; skip pure '
       'particles/conjunctions), give the Russian word or phrase that renders it '
       'in THIS translation. Output ONLY JSON: '
       '{"pairs":[{"sa":"<sanskrit content word, IAST>","ru":"<russian equivalent '
       'from the translation>"}]}. Omit Sanskrit words with no clear Russian '
       'counterpart. Use the dictionary/citation form of the Sanskrit word.')


def deepseek(user, retries=3, system=None):
    global KEY
    if KEY is None:
        KEY = _key()
    for a in range(retries):
        try:
            r = requests.post(API, headers={'Authorization': 'Bearer ' + KEY},
                              json={'model': 'deepseek-chat', 'temperature': 0,
                                    'response_format': {'type': 'json_object'},
                                    'messages': [{'role': 'system', 'content': system or SYS},
                                                 {'role': 'user', 'content': user}]},
                              timeout=(10, 60))   # (connect, read) — fail fast, never hang a worker
            r.raise_for_status()
            return r.json()['choices'][0]['message']['content']
        except Exception as ex:
            if a == retries - 1:
                sys.stderr.write('deepseek fail: %s\n' % ex)
                return None
            time.sleep(2 * (a + 1))


def align(sa_text, ru_text):
    out = deepseek('Sanskrit (IAST): %s\n\nRussian: %s' % (sa_text[:1200], ru_text[:1500]))
    if not out:
        return []
    try:
        return json.loads(out).get('pairs', [])
    except Exception:
        return []


SYS_BATCH = ('You word-align Sanskrit to Russian. You are given N items; each has a '
             'Sanskrit text and a Russian rendering. For EACH item INDEPENDENTLY, map '
             'each Sanskrit content word (noun, verb, adjective; skip pure particles) to '
             'its Russian equivalent in THAT item only — NEVER carry a word between items. '
             'Use the dictionary/citation form of the Sanskrit word. Items marked [NOTE] '
             'are sparse commentary footnotes, NOT full translations: for those align ONLY '
             'the words the note actually glosses and OMIT verse words it does not mention. '
             'CRITICAL: if a Sanskrit word has no genuine Russian counterpart in the '
             'item, OMIT it — never invent a rendering, never output a placeholder, never '
             'echo the Sanskrit. Output ONLY JSON: '
             '{"items":[{"i":<0-based item index>,"pairs":[{"sa":"<sanskrit word, IAST>",'
             '"ru":"<russian equivalent>"}]}]} — exactly one entry per item index i.')


def align_batch(units):
    """units = [(sa_text, ru_text, kind), …] → list of pairs-lists, aligned by index."""
    body = '\n\n'.join('ITEM %d %s\nSanskrit: %s\nRussian: %s'
                       % (i, '[NOTE]' if k == 'commentary' else '[TRANSLATION]', sa[:700], ru[:900])
                       for i, (sa, ru, k) in enumerate(units))
    out = deepseek(body, system=SYS_BATCH)
    res = [[] for _ in units]
    if out:
        try:
            for it in json.loads(out).get('items', []):
                i = it.get('i')
                if isinstance(i, int) and 0 <= i < len(units):
                    res[i] = it.get('pairs') or []
        except Exception:
            pass
    return res


def pairs_of(textfile, with_comm=True):
    # key by `seg`: a group has seg=sa (verse), seg=ru (the translation), and
    # seg=comm1/comm2/… (commentary notes, also lang=ru). We align BOTH — the
    # translation tagged kind='translation', the notes kind='commentary' (they
    # carry valuable lexical evidence) — never confusing one for the other.
    by_group = {}
    for line in open(os.path.join(SM, textfile), encoding='utf-8'):
        e = json.loads(line)
        if e.get('deleted'):
            continue
        by_group.setdefault(e.get('group'), {})[e.get('seg')] = e
    work = textfile.replace('.jsonl', '')
    for g, d in by_group.items():
        sa = d.get('sa')
        if not (sa and sa.get('text')):
            continue
        targets = []
        # only align a Russian segment that actually carries Cyrillic — an
        # untranslated placeholder ('…') would otherwise make DeepSeek fabricate.
        if d.get('ru') and has_cyr(d['ru'].get('text')):
            targets.append((d['ru']['text'], 'translation'))
        if with_comm:
            for seg in sorted(s for s in d if s and s.startswith('comm')):
                if has_cyr(d[seg].get('text')):
                    targets.append((d[seg]['text'], 'commentary'))
        if targets:
            yield g, work, sa.get('passage', ''), sa['text'], targets


def to_slp1(sa_iast):
    # DeepSeek sometimes emits dhātu citation notation (√gam); strip the √ so the
    # key is a clean SLP1 token that can match a verse form and join the lexicon.
    return cg.form_key(build_src.iast_to_slp1((sa_iast or '').replace('√', '').strip()))


def done_groups():
    s = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding='utf-8'):
            try:
                s.add(json.loads(line)['group'])
            except Exception:
                pass
    return s


def cmd_test(args):
    tf = args[0] if args else 'bhagavadgita-sementsov.jsonl'
    for g, work, passage, sa, targets in pairs_of(tf):
        st = STRATA.get(work, {})
        print('work=%s group=%s passage=%s | %s · ~%s · %s'
              % (work, g, passage, st.get('genre'), st.get('date_median'), st.get('period')))
        print('SA:', sa[:170])
        for text, kind in targets:
            print('--- %s ---' % kind.upper())
            print('  ', text[:150])
            for p in align(sa, text):
                print('    %-16s → slp1=%-12s → %s' % (p.get('sa', ''), to_slp1(p.get('sa', '')), p.get('ru', '')))
        break


def cmd_build(args):
    tf = args[0]
    n = int(args[1]) if len(args) > 1 else 10**9
    workers = int(args[2]) if len(args) > 2 else 12
    done = done_groups()
    work = tf.replace('.jsonl', '')
    st = STRATA.get(work, {})
    groups = [(g, passage, sa, targets) for g, _, passage, sa, targets in pairs_of(tf) if g not in done][:n]

    # batch consecutive groups until ~BATCH align-units per DeepSeek call; never
    # split a group across batches → group-level resumability holds.
    BATCH = 8
    batches, cur, curn = [], [], 0
    for item in groups:
        cur.append(item); curn += len(item[3])
        if curn >= BATCH:
            batches.append(cur); cur, curn = [], 0
    if cur:
        batches.append(cur)

    def proc(batch):
        meta, units = [], []                     # meta[i] ↔ units[i]
        for g, passage, sa, targets in batch:
            for text, kind in targets:
                meta.append((g, passage, kind)); units.append((sa, text, kind))
        rows, seen = [], set()
        for (g, passage, kind), pairs in zip(meta, align_batch(units)):
            for p in pairs:
                sa_w = (p.get('sa') or '').strip()
                ru_w = (p.get('ru') or '').strip()
                slp1 = to_slp1(sa_w)
                if not (slp1 and has_cyr(ru_w)):       # gloss must be real Russian
                    continue
                if ru_w == sa_w or ru_w in REJECT_RU:  # untranslated / refusal string
                    continue
                key = (g, slp1, ru_w, kind)
                if key in seen:                        # dedup repeated commentary units
                    continue
                seen.add(key)
                rows.append({'group': g, 'work': work, 'passage': passage, 'slp1': slp1,
                             'sa': sa_w, 'ru': ru_w, 'kind': kind,
                             'genre': st.get('genre'), 'period': st.get('period'),
                             'date': st.get('date_median')})
        return rows

    wrote = doneb = 0
    with open(OUT, 'a', encoding='utf-8', newline='') as out, ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(proc, b) for b in batches]
        for fut in as_completed(futs):
            for r in fut.result():
                out.write(json.dumps(r, ensure_ascii=False) + '\n')
                wrote += 1
            out.flush()
            doneb += 1
            if doneb % 20 == 0:
                print('  %s: %d/%d batches, %d alignments' % (work, doneb, len(batches), wrote))
    print('%s [%s · ~%s]: %d groups in %d batches → %d alignments (x%d) → %s'
          % (work, st.get('genre'), st.get('date_median'), len(groups), len(batches), wrote, workers, os.path.basename(OUT)))


def cmd_status(args):
    if not os.path.exists(OUT):
        print('lexicon empty'); return
    keys, works, n = set(), set(), 0
    for line in open(OUT, encoding='utf-8'):
        r = json.loads(line)
        n += 1
        keys.add(r['slp1'])
        works.add(r['work'])
    print('corpus_lexicon: %d alignments, %d distinct SLP1 keys, %d works'
          % (n, len(keys), len(works)))


def cmd_buildall(args):
    workers = args[0] if args else '8'
    texts = sorted(STRATA.keys(), key=lambda w: -STRATA[w].get('groups', 0))   # biggest first
    print('building %d corpus texts biggest-first (workers=%s) …' % (len(texts), workers))
    for i, work in enumerate(texts, 1):
        tf = work + '.jsonl'
        if not os.path.exists(os.path.join(SM, tf)):
            continue
        print('[%d/%d] %s' % (i, len(texts), work))
        try:
            cmd_build([tf, str(10**9), str(workers)])
        except Exception as ex:
            sys.stderr.write('ERROR %s: %s\n' % (work, ex))


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    {'test': cmd_test, 'build': cmd_build, 'buildall': cmd_buildall,
     'status': cmd_status}.get(sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:])


if __name__ == '__main__':
    main()
