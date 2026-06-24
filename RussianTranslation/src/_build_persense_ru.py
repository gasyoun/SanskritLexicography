# -*- coding: utf-8 -*-
"""Per-sense corpus RU: hang each attested Russian rendering (DeepSeek
corpus_lexicon) under the PD sense it supports, by matching the rendering's
Russian lemma against the (already hand-authored) Russian sense-glosses.
Reuses corpus_harvest.lemma_key / pos_class / index — no re-alignment."""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8')
import corpus_harvest as ch   # lemma_key(), pos_class(), index()

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'article-comparison'))
WORDS = {'agni':['agni','agniH'], 'anya':['anya','anyaH'],
         'aksara':['akzara','akzaraH'], 'ananta':['ananta','anantaH']}
# headword's own theonym/name surface forms → route to its principal name sense
THEONYM = {'agni':{'агни'}, 'ananta':{'ананта','шеша'}, 'aksara':{'акшара','акшар'}, 'anya':set()}

# synonym normalization: corpus rendering-lemma → the canonical lemma that the
# PD Russian glosses actually use (so synonyms land on the right sense).
SYN = {
 # akṣara — "imperishable" cluster → непреходящий (glosses A / 2A)
 'нетленный':'непреходящий','негибнуть':'непреходящий','негибнущий':'непреходящий',
 'неразрушимый':'непреходящий','неуничтожимый':'непреходящий','нерушимый':'непреходящий',
 'невредимый':'непреходящий','не гибнет':'непреходящий','неисчерпаемый':'непреходящий',
 # agni — "fire" cluster → огонь (gloss 1)
 'пламя':'огонь','костёр':'огонь','костер':'огонь','пожар':'огонь','огнѣ':'огонь',
 # ananta — "endless" cluster → бесконечный (glosses 1A/1C)
 'безмерный':'бесконечный','безконечный':'бесконечный','бесконечно':'бесконечный',
 # anya
 'друг':'другой','прочий':'остальной','пришелец':'чужой','чужое':'чужой',
 'отличие':'отличный','отлично':'отличный',
}
_w2 = re.compile(r'[А-Яа-яЁё]+')
def match_lemmas(ru, lemma):
    """canonical lemmas a rendering carries (phrase-aware + synonym-normalized)"""
    if ' ' in ru:
        out = set()
        for t in _w2.findall(ru):
            if len(t) >= 3:
                l = ch.lemma_key(t)
                out.add(SYN.get(l, l))
        return out
    return {SYN.get(lemma, lemma)}

_word = re.compile(r'[А-Яа-яЁё]+')
def gloss_lemmas(ru_gloss):
    """content lemmas of a Russian sense-gloss (drop 1-2 char tokens, func words)"""
    out = set()
    for tok in _word.findall(ru_gloss):
        if len(tok) < 3:
            continue
        lem = ch.lemma_key(tok)
        if ch.pos_class(lem) != 'func':
            out.add(lem)
    return out

def load_senses(w):
    """[(label, en, ru, lemmaset)] from the bilingual skeleton table"""
    senses = []
    for l in open(os.path.join(OUT, f'{w}.pd-min.ru.md'), encoding='utf-8'):
        m = re.match(r'\| \*\*(.+?)\*\* \| (.*?) \| (.*?) \|\s*$', l.rstrip('\n'))
        if m and m.group(1) != 'Значение':
            lbl, en, ru = m.group(1), m.group(2).strip(), m.group(3).strip()
            senses.append((lbl, en, ru, gloss_lemmas(ru)))
    return senses

def assign(ru, lemma, pos, senses, theos):
    """return list of sense indices this rendering supports"""
    mls = match_lemmas(ru, lemma)
    if (pos == 'name' and lemma in theos) or (mls & theos):
        # principal name/deva sense: first sense whose RU gloss names a god/имя/бог
        for i,(lbl,en,ru2,ls) in enumerate(senses):
            if re.search(r'\bбог\b|божество|имя |Высшее Существо|Шеша|Вишну', ru2):
                return [i]
    return [i for i,(lbl,en,ru2,ls) in enumerate(senses) if mls & ls]

REPORT = []
for w, keys in WORDS.items():
    senses = load_senses(w)
    idx = ch.index()
    rows = [r for k in keys for r in idx.get(k, [])]
    # aggregate renderings by lemma
    agg = collections.defaultdict(lambda: {'n':0,'forms':collections.Counter(),'loci':[],'pos':'content'})
    for r in rows:
        ru = (r.get('ru') or '').strip()
        if not ru:
            continue
        lem = ch.lemma_key(ru)
        a = agg[lem]; a['n'] += 1; a['forms'][ru]+=1; a['pos']=ch.pos_class(lem)
        if len(a['loci'])<3: a['loci'].append((r.get('group'),r.get('genre')))
    # assign
    persense = collections.defaultdict(list)   # sense_idx -> [(lemma,n,forms,loci)]
    residual = []
    mapped_occ = 0; total_occ = sum(a['n'] for a in agg.values())
    for lem,a in sorted(agg.items(), key=lambda kv:-kv[1]['n']):
        ru_form = a['forms'].most_common(1)[0][0]
        sidx = assign(ru_form, lem, a['pos'], senses, THEONYM[w])
        if sidx:
            for i in sidx: persense[i].append((lem,a))
            mapped_occ += a['n']
        else:
            residual.append((lem,a))
    # write per-sense section
    lines = [f'## Корпус по значениям (привязка к PD-смыслам)\n',
        f'_Засвидетельствованные русские соответствия ({total_occ} вхождений) из DeepSeek-лексикона, '
        f'привязанные к конкретному значению PD по совпадению русской леммы с глоссой. '
        f'Покрытие: **{mapped_occ}/{total_occ} = {100*mapped_occ/max(total_occ,1):.0f}%** привязано._\n',
        '| Значение | English (PD) | Русский (глосса) | Засвидетельствовано в корпусе |',
        '|:--|:--|:--|:--|']
    for i,(lbl,en,ru,ls) in enumerate(senses):
        cell=''
        if persense.get(i):
            parts=[]
            for lem,a in sorted(persense[i], key=lambda x:-x[1]['n'])[:8]:
                top=a['forms'].most_common(1)[0][0]
                loc=a['loci'][0][0] if a['loci'] else ''
                parts.append(f'{top} ×{a["n"]}' + (f' _{loc}_' if loc else ''))
            cell=' · '.join(parts)
        lines.append(f'| **{lbl}** | {en} | {ru} | {cell} |')
    if residual:
        lines += ['', '### Не привязано к значению (синонимы/перифразы/контекст → этап Max-LLM)\n',
                  '_'+(', '.join(f'{a["forms"].most_common(1)[0][0]}×{a["n"]}' for lem,a in residual[:30]))+'_']
    open(os.path.join(OUT, f'{w}.persense-ru.md'),'w',encoding='utf-8').write('\n'.join(lines))
    REPORT.append((w, total_occ, mapped_occ, len(residual)))
    print(f'{w}: {mapped_occ}/{total_occ} occ mapped ({100*mapped_occ/max(total_occ,1):.0f}%), {len(residual)} residual lemmas')
