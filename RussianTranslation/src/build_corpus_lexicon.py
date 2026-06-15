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


KEY = _key()
SYS = ('You align a Sanskrit verse to its Russian translation at the WORD level. '
       'For each notable Sanskrit CONTENT word (noun, verb, adjective; skip pure '
       'particles/conjunctions), give the Russian word or phrase that renders it '
       'in THIS translation. Output ONLY JSON: '
       '{"pairs":[{"sa":"<sanskrit content word, IAST>","ru":"<russian equivalent '
       'from the translation>"}]}. Omit Sanskrit words with no clear Russian '
       'counterpart. Use the dictionary/citation form of the Sanskrit word.')


def deepseek(user, retries=3):
    for a in range(retries):
        try:
            r = requests.post(API, headers={'Authorization': 'Bearer ' + KEY},
                              json={'model': 'deepseek-chat', 'temperature': 0,
                                    'response_format': {'type': 'json_object'},
                                    'messages': [{'role': 'system', 'content': SYS},
                                                 {'role': 'user', 'content': user}]},
                              timeout=120)
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


def pairs_of(textfile):
    by_group = {}
    for line in open(os.path.join(SM, textfile), encoding='utf-8'):
        e = json.loads(line)
        if e.get('deleted'):
            continue
        by_group.setdefault(e.get('group'), {})[e.get('lang')] = e
    work = textfile.replace('.jsonl', '')
    for g, d in by_group.items():
        if 'sa' in d and 'ru' in d and d['sa'].get('text') and d['ru'].get('text'):
            yield g, work, d['sa']['passage'], d['sa']['text'], d['ru']['text']


def to_slp1(sa_iast):
    return cg.form_key(build_src.iast_to_slp1(sa_iast))


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
    for g, work, passage, sa, ru in pairs_of(tf):
        print('work=%s group=%s passage=%s' % (work, g, passage))
        print('SA:', sa[:170])
        print('RU:', ru[:170])
        print('--- DeepSeek word alignment ---')
        for p in align(sa, ru):
            print('  %-16s → slp1=%-12s → %s' % (p.get('sa', ''), to_slp1(p.get('sa', '')), p.get('ru', '')))
        break


def cmd_build(args):
    tf = args[0]
    n = int(args[1]) if len(args) > 1 else 10**9
    done = done_groups()
    work = tf.replace('.jsonl', '')
    processed = wrote = 0
    with open(OUT, 'a', encoding='utf-8', newline='') as out:
        for g, _, passage, sa, ru in pairs_of(tf):
            if g in done:
                continue
            for p in align(sa, ru):
                slp1 = to_slp1(p.get('sa', ''))
                if slp1 and p.get('ru'):
                    out.write(json.dumps({'group': g, 'work': work, 'passage': passage,
                                          'slp1': slp1, 'sa': p.get('sa'), 'ru': p.get('ru')},
                                         ensure_ascii=False) + '\n')
                    wrote += 1
            out.flush()
            processed += 1
            if processed % 20 == 0:
                print('  %s: %d pairs, %d alignments' % (work, processed, wrote))
            if processed >= n:
                break
    print('%s: processed %d pairs → %d alignments appended to %s'
          % (work, processed, wrote, os.path.basename(OUT)))


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


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    {'test': cmd_test, 'build': cmd_build, 'status': cmd_status}.get(
        sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:])


if __name__ == '__main__':
    main()
