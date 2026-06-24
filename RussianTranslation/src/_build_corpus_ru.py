# -*- coding: utf-8 -*-
"""Reuse the DeepSeek corpus word-alignment lexicon + verse-level parallel corpus
to produce a corpus-grounded Russian section per headword, for the
article-comparison study. Reads existing assets only (no API calls)."""
import json, os, sys, sqlite3, collections
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, 'corpus_lexicon.jsonl')
DB  = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'SamudraManthanam', 'web', 'corpus.db'))
OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'article-comparison'))

WORDS = {
    'agni':   ['agni', 'agniH'],
    'anya':   ['anya', 'anyaH'],
    'aksara': ['akzara', 'akzaraH'],
    'ananta': ['ananta', 'anantaH'],
}
HEAD = {'agni':'agni «огонь»','anya':'anya «другой»','aksara':'akṣara «непреходящее / слог»','ananta':'ananta «бесконечный / Ананта»'}

# 1) distribution + example loci from the DeepSeek lexicon
agg = {w: {'ru': collections.Counter(), 'occ': 0, 'loci': collections.defaultdict(list)} for w in WORDS}
keyset = {k: w for w, ks in WORDS.items() for k in ks}
for line in open(LEX, encoding='utf-8'):
    r = json.loads(line)
    w = keyset.get(r.get('slp1'))
    if not w:
        continue
    ru = (r.get('ru') or '').strip()
    if not ru:
        continue
    agg[w]['ru'][ru] += 1
    agg[w]['occ'] += 1
    agg[w]['loci'][ru].append((r.get('group'), r.get('genre'), r.get('period')))

# 2) verse pairs (Sanskrit + published Russian) from corpus.db, chosen from lexicon loci
db = sqlite3.connect(DB)
def verse(group):
    sa = db.execute("SELECT line_text FROM corpus_lines WHERE canonical_id=?", (group + '#sa',)).fetchone()
    ru = db.execute("SELECT line_text FROM corpus_lines WHERE canonical_id=?", (group + '#ru',)).fetchone()
    src = None
    row = db.execute("SELECT source_id FROM corpus_lines WHERE canonical_id=? LIMIT 1", (group + '#ru',)).fetchone()
    if row:
        s = db.execute("SELECT title FROM sources WHERE id=?", (row[0],)).fetchone()
        src = s[0] if s else None
    return (sa[0] if sa else None, ru[0] if ru else None, src)

def pick_loci(w, n=4):
    # collect distinct groups across the top renderings, prefer ones with a real verse pair
    seen, out = set(), []
    for ru, _ in agg[w]['ru'].most_common():
        for grp, genre, period in agg[w]['loci'][ru]:
            if grp in seen:
                continue
            seen.add(grp)
            sa, rru, src = verse(grp)
            if sa and rru and len(rru) > 15:
                out.append((grp, sa, rru, src))
            if len(out) >= n:
                return out
    return out

for w, ks in WORDS.items():
    a = agg[w]
    lines = [f'## Корпусная опора: засвидетельствованные русские соответствия\n',
             f'_Источник: DeepSeek-выравнивание параллельного корпуса (`corpus_lexicon.jsonl`, пословное Sa→Ru). '
             f'Ключи SLP1 `{", ".join(ks)}` — **{a["occ"]} выровненных вхождений**, {len(a["ru"])} различных русских соответствий._\n',
             '| Русское соответствие | Частота | Пример (локус · жанр) |',
             '|:--|--:|:--|']
    for ru, c in a['ru'].most_common(15):
        grp, genre, period = a['loci'][ru][0]
        lines.append(f'| {ru} | {c} | {grp} · {genre} |')
    lines += ['', '### Стихи параллельного корпуса (санскрит + опубликованный русский)\n',
              '_Существующие академические переводы (Елизаренкова РВ/АВ, акад. Махабхарата и др.), '
              'привязанные к стиху по локусу из выравнивания. Не перевожу заново — цитирую изданное._\n']
    for grp, sa, rru, src in pick_loci(w):
        lines.append(f'> **{grp}**  ')
        lines.append(f'> _Sa._ {sa}  ')
        lines.append(f'> _Ru._ {rru}  ')
        lines.append(f'> — {src}\n')
    frag = os.path.join(OUT, f'{w}.corpus-ru.md')
    open(frag, 'w', encoding='utf-8').write('\n'.join(lines))
    print(f'{w}: {a["occ"]} occ, {len(a["ru"])} distinct RU -> {w}.corpus-ru.md')
