#!/usr/bin/env python
"""build_surface_glossary.py — Stage A: surface-form -> Russian glossary.

Direct group-by on corpus_lexicon.jsonl (1.09M word-aligned Sa->Ru tokens). No lemmatizer
needed: every attested SLP1 surface form -> all its Russian renderings with counts and
provenance. This is the "all forms / all words" layer; the lemma & root rollups (Stage D)
consume it.

Scope (per MG): EVERYTHING, all n>=1 — hapax kept, both kind=translation and kind=commentary
kept (a `kinds` field records the split so downstream can filter).

Outputs (in ../glossary/):
  surface_glossary.jsonl   nested: one record per form, translations[] sorted by n desc
                           (140 MB > GitHub's 100 MB limit -> not committed; see split below)
  surface_glossary.tsv     flat:   one row per (form, ru) pair — queryable master
  surface/<X>.jsonl        the JSONL split per initial SLP1 letter (max ~17 MB, committable)
  md/surface/<X>.md        human-readable, one file per initial SLP1 letter

Per (form, ru) we keep a work-count map and a capped sample of `work:passage` sources
(SRC_CAP) with a total; the raw corpus remains the exhaustive provenance.

  python build_surface_glossary.py [corpus_lexicon.jsonl]
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.normpath(os.path.join(HERE, '..', 'glossary'))
MD_DIR = os.path.join(OUT_DIR, 'md', 'surface')
# per-initial-letter JSONL split: the whole surface_glossary.jsonl is 140 MB (> GitHub's
# 100 MB file limit); the per-letter parts (max ~17 MB) are the committable raw form.
JSONL_DIR = os.path.join(OUT_DIR, 'surface')
os.makedirs(MD_DIR, exist_ok=True)
os.makedirs(JSONL_DIR, exist_ok=True)

SRC_CAP = 25                      # sample sources kept per (form, ru)
_reg = re.compile(r'^\d+_')
def register(work):
    return _reg.sub('', work or '')

def letter_bucket(slp1):
    """First SLP1 char as a filesystem-safe bucket name. Case-FOLDED to upper: SLP1 is
    case-significant (a≠A, s≠S) but Windows' filesystem is case-insensitive, so distinct
    files 'a'/'A' collide and truncate each other — fold them into one shard (a+A -> 'A').
    The phonemic distinction is preserved in the data's `slp1` field, not the shard name."""
    if not slp1:
        return '_'
    ch = slp1[0]
    return ch.upper() if re.match(r'[A-Za-z]', ch) else '_other'

def main():
    corpus = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'corpus_lexicon.jsonl')

    # form -> aggregate
    forms = {}   # slp1 -> {sa:Counter, ru:Counter, kinds:Counter, periods:Counter,
                 #          genres:Counter, works:Counter, tr:{ru->{works:Counter,src:list,total:int}}}
    n = 0
    with open(corpus, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            d = json.loads(line)
            slp1 = d.get('slp1') or ''
            ru = (d.get('ru') or '').strip()
            if not slp1 or not ru:
                continue
            e = forms.get(slp1)
            if e is None:
                e = forms[slp1] = {
                    'sa': collections.Counter(), 'ru': collections.Counter(),
                    'kinds': collections.Counter(), 'periods': collections.Counter(),
                    'genres': collections.Counter(), 'works': collections.Counter(),
                    'tr': {}}
            e['sa'][d.get('sa') or slp1] += 1
            e['ru'][ru] += 1
            e['kinds'][d.get('kind') or ''] += 1
            e['periods'][d.get('period') or ''] += 1
            e['genres'][d.get('genre') or ''] += 1
            work = d.get('work') or ''
            e['works'][work] += 1
            t = e['tr'].get(ru)
            if t is None:
                t = e['tr'][ru] = {'works': collections.Counter(), 'src': [], 'total': 0}
            t['works'][work] += 1
            t['total'] += 1
            if len(t['src']) < SRC_CAP:
                t['src'].append(f"{work}:{d.get('passage','')}")
            n += 1
            if n % 200000 == 0:
                print(f'  ...{n} tokens, {len(forms)} forms', file=sys.stderr)
    print(f'[A] {n} tokens -> {len(forms)} distinct surface forms', file=sys.stderr)

    # ---- emit JSONL + TSV ----
    jpath = os.path.join(OUT_DIR, 'surface_glossary.jsonl')
    tpath = os.path.join(OUT_DIR, 'surface_glossary.tsv')
    buckets = collections.defaultdict(list)   # letter -> list of (slp1, record)
    with open(jpath, 'w', encoding='utf-8', newline='\n') as jf, \
         open(tpath, 'w', encoding='utf-8', newline='\n') as tf:
        tf.write('form_slp1\tsa\tru\tn\tn_form_total\tworks\n')
        for slp1 in sorted(forms):
            e = forms[slp1]
            sa = e['sa'].most_common(1)[0][0]
            total = sum(e['ru'].values())
            translations = []
            for ru, cnt in e['ru'].most_common():
                t = e['tr'][ru]
                translations.append({
                    'ru': ru, 'n': cnt,
                    'works': dict(t['works'].most_common()),
                    'src_sample': t['src'], 'src_total': t['total']})
                tf.write(f"{slp1}\t{sa}\t{ru}\t{cnt}\t{total}\t"
                         f"{'|'.join(f'{w}:{c}' for w,c in t['works'].most_common())}\n")
            rec = {
                'slp1': slp1, 'sa': sa, 'n': total,
                'kinds': dict(e['kinds']),
                'periods': dict(e['periods'].most_common()),
                'genres': dict(e['genres'].most_common()),
                'registers': dict(collections.Counter(
                    {register(w): c for w, c in e['works'].items()}).most_common()),
                'translations': translations}
            jf.write(json.dumps(rec, ensure_ascii=False) + '\n')
            buckets[letter_bucket(slp1)].append((slp1, rec))
    print(f'[A] wrote {jpath} and {tpath}', file=sys.stderr)

    # ---- per-letter Markdown + per-letter JSONL split ----
    for letter, items in sorted(buckets.items()):
        mp = os.path.join(MD_DIR, f'{letter}.md')
        with open(mp, 'w', encoding='utf-8', newline='\n') as mf:
            mf.write(f'# Surface glossary — SLP1 `{letter}`\n\n')
            mf.write(f'{len(items)} forms. Format: `form` (sa) — total n → '
                     'ru (n) · registers.\n\n')
            for slp1, rec in items:
                mf.write(f"### `{slp1}` — {rec['sa']}  (n={rec['n']})\n\n")
                for t in rec['translations']:
                    regs = ', '.join(register(w) for w in t['works'])
                    mf.write(f"- {t['ru']}  · n={t['n']}  · {regs}\n")
                mf.write('\n')
        jp = os.path.join(JSONL_DIR, f'{letter}.jsonl')
        with open(jp, 'w', encoding='utf-8', newline='\n') as jlf:
            for _slp1, rec in items:
                jlf.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print(f'[A] wrote {len(buckets)} Markdown letter files -> {MD_DIR}', file=sys.stderr)
    print(f'[A] wrote {len(buckets)} JSONL letter parts -> {JSONL_DIR}', file=sys.stderr)

if __name__ == '__main__':
    main()
