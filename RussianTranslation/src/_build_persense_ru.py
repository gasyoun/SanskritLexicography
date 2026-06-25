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

# where a headword's own theonym should land (specific referent, not generic)
ROUTE = {'agni': r'бог огня|\bбог\b', 'ananta': r'Шеша', 'aksara': r'Высшее Существо', 'anya': None}

# Max-LLM residual assignment (2026-06-25). Each surface rendering the
# deterministic matcher could not hang under a PD sense was adjudicated by an
# Opus-4.8 pass against the full bilingual sense skeleton and routed to a sense
# *ordinal* (0-based row order in <w>.pd-min.ru.md) — or left in the residual as
# genuine "other" (function-word / context leakage / off-headword name). Keyed by
# the surface form exactly as `a['forms'].most_common(1)[0][0]` emits it.
LLM_ASSIGN = {
 'agni': {
   'жертвах':72, 'пылающей':127, 'Рождаемый топливом':13, 'Агни-Джатаведас':29,
   'Агни-Джатаведаса':29, 'Анги':32, 'головня':0, 'пламень':0, 'Агни-Вайшванару':30,
   'желудок':53, 'Индра-Агни':35, 'очага':5, 'Агни-бог':13, 'Агни-риши':109,
   'огненномъ':127,
 },
 'aksara': {
   'не гибнет':0, 'буква-слог':4, 'не гибнущий':0, 'Бесконечное':12,
   'необманчивымъ':0, 'невредимомъ':0, 'невредимости':0, 'вечно':0,
   'вечность бессмертья':0, 'вне смерти':0, 'неизмѣннаго':0,
   'нерожденный, безначальный, и безконечный':12, 'сознанье':12, 'неизмѣнное':1,
   'высочайшій духъ':12, 'неизмѣнный':1, 'неизреченномъ':12, 'непроявленное':12,
   'стоитъ незыблемо отъ вѣка':0, 'недѣлимымъ':0, 'неистребимый':0, 'Атмана':12,
   'неистощимо':0, '«непреходящий»':0, 'невредимымъ':0,
 },
 'anya': {
   'никого':5, 'ничего':2, 'каким-нибудь':2, 'кроме':63, 'кто-то':17, 'нет':5,
   'какой-либо':2, 'схожие':47, 'прочем':30, 'больше никто':5, 'простых воинов':49,
   'иныхъ':1, 'другіе':1, 'инаго':1, 'прочим':30, 'помимо':63, 'кроме тебя':63,
   'чуждый':31,
 },
 'ananta': {
   'завершенности не знает':4, 'Ананте':12, 'вездесущий':0, 'нескончаемы':1,
   'вѣчнаго':1, 'безпредѣльное':0, 'вѣчный':1, 'безпредѣльнымъ':0, 'неизмѣнный':1,
   'всевечного':1, 'чрезмерные':4, 'пожизненными':1,
 },
}
_word = re.compile(r'[А-Яа-яЁё]+')
_COUNT = re.compile(r'\bодн(?:ого|ой|ому|им|ом|а|о|у|и)?\s+из\b', re.I)  # "one of" scaffolding
def gloss_lemmas(ru_gloss):
    """content lemmas of a Russian sense-gloss (drop 1-2 char tokens, func words,
    scaffolding 'имя/название/эпитет' and the counting phrase 'один из …')"""
    ru_gloss = _COUNT.sub(' ', ru_gloss)
    STOP = {'имя', 'название', 'эпитет', 'разновидность'}
    out = set()
    for tok in _word.findall(ru_gloss):
        if tok.lower() in STOP:
            continue
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

def assign(ru, lemma, pos, senses, theos, route):
    """return list of sense indices this rendering supports"""
    mls = match_lemmas(ru, lemma)
    if route and ((pos == 'name' and lemma in theos) or (mls & theos)):
        # route the headword's own theonym to its specific referent sense
        for i,(lbl,en,ru2,ls) in enumerate(senses):
            if re.search(route, ru2):
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
    persense = collections.defaultdict(list)   # sense_idx -> [(lemma,a,is_llm)]
    residual = []
    mapped_det = 0; mapped_llm = 0; total_occ = sum(a['n'] for a in agg.values())
    for lem,a in sorted(agg.items(), key=lambda kv:-kv[1]['n']):
        ru_form = a['forms'].most_common(1)[0][0]
        sidx = assign(ru_form, lem, a["pos"], senses, THEONYM[w], ROUTE[w])
        if sidx:
            for i in sidx: persense[i].append((lem,a,False))
            mapped_det += a['n']
        else:
            j = LLM_ASSIGN.get(w, {}).get(ru_form)
            if j is not None and 0 <= j < len(senses):
                persense[j].append((lem,a,True))
                mapped_llm += a['n']
            else:
                residual.append((lem,a))
    mapped_occ = mapped_det + mapped_llm
    # write per-sense section
    pct = lambda n: 100*n/max(total_occ,1)
    lines = [f'## Корпус по значениям (привязка к PD-смыслам)\n',
        f'_Засвидетельствованные русские соответствия ({total_occ} вхождений) из DeepSeek-лексикона, '
        f'привязанные к конкретному значению PD. Покрытие: **{mapped_occ}/{total_occ} = {pct(mapped_occ):.0f}%** '
        f'(детерминированно {mapped_det} = {pct(mapped_det):.0f}%, + Max-LLM {mapped_llm} = {pct(mapped_llm):.0f}%). '
        f'Рендеринги, привязанные пассом Max-LLM (Opus 4.8, 2026-06-25), помечены **°**._\n',
        '| Значение | English (PD) | Русский (глосса) | Засвидетельствовано в корпусе |',
        '|:--|:--|:--|:--|']
    for i,(lbl,en,ru,ls) in enumerate(senses):
        cell=''
        if persense.get(i):
            parts=[]
            for lem,a,is_llm in sorted(persense[i], key=lambda x:-x[1]['n'])[:8]:
                top=a['forms'].most_common(1)[0][0]
                loc=a['loci'][0][0] if a['loci'] else ''
                parts.append(f'{top}{"°" if is_llm else ""} ×{a["n"]}' + (f' _{loc}_' if loc else ''))
            cell=' · '.join(parts)
        lines.append(f'| **{lbl}** | {en} | {ru} | {cell} |')
    if residual:
        lines += ['', '### Не привязано к значению (после пасса Max-LLM — остаточная утечка)\n',
                  '_Прогнан пасс Max-LLM (Opus 4.8) по значениям; оставшееся ниже — '
                  'служебные слова, контекстные обрывки и имена вне заголовка, у которых нет '
                  'значения PD для привязки:_\n',
                  '_'+(', '.join(f'{a["forms"].most_common(1)[0][0]}×{a["n"]}' for lem,a in residual[:30]))+'_']
    open(os.path.join(OUT, f'{w}.persense-ru.md'),'w',encoding='utf-8').write('\n'.join(lines))
    REPORT.append((w, total_occ, mapped_det, mapped_llm, len(residual)))
    print(f'{w}: {mapped_occ}/{total_occ} occ mapped ({pct(mapped_occ):.0f}%; det {mapped_det} + LLM {mapped_llm}), {len(residual)} residual lemmas')
