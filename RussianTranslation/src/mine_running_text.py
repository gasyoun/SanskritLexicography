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
  python mine_running_text.py status                 mined rows + distinct keys + per-source
"""
import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import build_corpus_lexicon as bcl   # deepseek(), to_slp1(), has_cyr(), SM, REJECT_RU

HERE = os.path.dirname(os.path.abspath(__file__))
SM = bcl.SM
OUT = os.path.join(HERE, 'corpus_lexicon.mined.jsonl')

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
    {'test': cmd_test, 'mine': cmd_mine, 'status': cmd_status}.get(cmd, cmd_status)(rest)
