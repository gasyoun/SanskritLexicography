#!/usr/bin/env python
"""Harvest reader — corpus_lexicon.jsonl → attested Russian senses per headword.

Turns the raw word-alignment rows into the reuse signal the pwg_ru harvest
consumes: given a Sanskrit headword (SLP1 key) it returns the Russian renderings
ACTUALLY ATTESTED in the parallel corpus, grouped by stratum (period/genre),
counted, and split translation-vs-commentary. When the PWG sense's <ls> citation
is known, ls_source_map.json resolves it to a stratum so that stratum's
renderings surface first (a Ṛgvedic citation → the Vedic Russian).

  python corpus_harvest.py top [N]                   most-attested keys
  python corpus_harvest.py coverage                  per-stratum coverage (honesty check)
  python corpus_harvest.py <slp1> [LS_KEY] [--raw]   attested Russian for a headword
      LS_KEY  PWG <ls> source (e.g. M, MBH) → its stratum surfaces first
      --raw   keep function-word renderings (for particle/pronoun headwords)
"""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, 'corpus_lexicon.jsonl')
LSMAP = os.path.join(HERE, 'ls_source_map.json')
LS_SOURCES = json.load(open(LSMAP, encoding='utf-8')) if os.path.exists(LSMAP) else {}

# period ordering oldest→newest for stable stratum sort
PERIOD_ORDER = {'Vedic': 1, 'Epic / early-Classical': 2, 'Classical': 3, 'Medieval': 4}


def norm_period(p):
    """Ṛgvedic is part of the Vedic period → one Vedic stratum (Ṛgveda + Saṃhitās
    + Brāhmaṇas + Upaniṣads). Folds the older labels onto a single 'Vedic'."""
    if p in ('Ṛgvedic', 'Vedic (Brāhmaṇa–Upaniṣad)', 'Vedic (Brāhmaṇa-Upaniṣad)'):
        return 'Vedic'
    return p or '?'

# optional Russian lemmatizer: collapse inflected variants (царя/царю→царь) under
# the lemma. Falls back to lowercased surface form if pymorphy3 is not installed.
try:
    import pymorphy3
    _MORPH = pymorphy3.MorphAnalyzer()
except Exception:
    _MORPH = None
_lemcache = {}
_surface_names = set()
_CYR_TOKEN = re.compile(r'^[А-Яа-яЁё-]+$')
_FUNC = {'CONJ', 'PREP', 'PRCL', 'NPRO', 'INTJ', 'PRED'}
_NAME = {'Name', 'Surn', 'Patr', 'Geox', 'Orgn'}
_SURFACE_NAME_OVERRIDES = {'агни', 'вишну'}


def _preserve_surface_name(ru, parsed):
    """Avoid false Russian lemmata for Sanskrit names.

    pymorphy3 parses Агни/агни as the Russian verb "агнуть"; Вишну can become
    "вишн". For corpus-harvest evidence, a false common-Russian lemma is worse
    than keeping the surface Sanskrit name.
    """
    token = (ru or '').strip()
    lo = token.lower()
    if not token or ' ' in token or not _CYR_TOKEN.match(token):
        return False
    if lo in _SURFACE_NAME_OVERRIDES:
        return True
    tag = parsed.tag
    if any(g in tag for g in _NAME) and parsed.normal_form != lo:
        return True
    return False


def lemma_key(ru):
    if not _MORPH or ' ' in ru:          # phrases kept as-is (head-lemma is unreliable)
        return ru.lower()
    if ru not in _lemcache:
        try:
            parsed = _MORPH.parse(ru)[0]
            if _preserve_surface_name(ru, parsed):
                _lemcache[ru] = ru.lower()
                _surface_names.add(_lemcache[ru])
            else:
                _lemcache[ru] = parsed.normal_form
        except Exception:
            _lemcache[ru] = ru.lower()
    return _lemcache[ru]


# classify a rendering so alignment noise (particles, pronouns) is separable from
# real lexical senses; proper names are kept but tagged (they may be the correct
# rendering of a name-headword, or leakage from the verse's referent).
_posc = {}


def pos_class(lemma):
    if not _MORPH or ' ' in lemma:       # multi-word gloss = content
        return 'content'
    if lemma not in _posc:
        cls = 'content'
        try:
            tag = _MORPH.parse(lemma)[0].tag
            if lemma in _surface_names:
                cls = 'name'
            elif tag.POS in _FUNC:
                cls = 'func'
            elif any(g in tag for g in _NAME):
                cls = 'name'
        except Exception:
            pass
        _posc[lemma] = cls
    return _posc[lemma]


def index():
    idx = collections.defaultdict(list)
    if os.path.exists(LEX):
        for line in open(LEX, encoding='utf-8'):
            try:
                r = json.loads(line)
            except Exception:
                continue
            idx[r['slp1']].append(r)
    return idx


def harvest(rows, prefer_period=None):
    """rows for one slp1 key → strata, each with Russian renderings grouped by
    lemma (inflected surface forms collapsed, counted, kept as evidence)."""
    by_stratum = collections.defaultdict(lambda: collections.defaultdict(
        lambda: {'n': 0, 'kinds': set(), 'works': set(), 'forms': collections.Counter()}))
    for r in rows:
        ru = (r.get('ru') or '').strip()
        if not ru:
            continue
        cell = by_stratum[(norm_period(r.get('period')), r.get('genre') or '?')][lemma_key(ru)]
        cell['n'] += 1
        cell['kinds'].add(r.get('kind'))
        cell['works'].add(r.get('work'))
        cell['forms'][ru] += 1
    out = []
    for (period, genre), rends in by_stratum.items():
        renderings = sorted(
            ({'lemma': lem, 'count': c['n'], 'kinds': sorted(c['kinds']),
              'works': len(c['works']), 'pos': pos_class(lem),
              'forms': [f for f, _ in c['forms'].most_common(6)]} for lem, c in rends.items()),
            key=lambda x: -x['count'])
        out.append({'period': period, 'genre': genre,
                    'total': sum(r['count'] for r in renderings),
                    'renderings': renderings})
    out.sort(key=lambda s: (s['period'] != prefer_period,
                            PERIOD_ORDER.get(s['period'], 9)))
    return out


def resolve_period(ls_key):
    rec = LS_SOURCES.get(ls_key)
    return rec.get('period') if rec else None


def cmd_coverage():
    """Per-stratum coverage of the lexicon vs the corpus's translatable total.
    Exposes which strata are still thin/empty so a cited sense is not silently
    given another era's Russian (the build is biggest-first, so strata fill
    unevenly)."""
    spath = os.path.join(HERE, 'corpus_strata.json')
    strata = json.load(open(spath, encoding='utf-8')) if os.path.exists(spath) else {}
    pot = collections.Counter()
    for st in strata.values():
        pot[norm_period(st.get('period'))] += st.get('groups', 0)
    rows = collections.Counter()
    keys = collections.defaultdict(set)
    groups = collections.defaultdict(set)
    works = collections.defaultdict(set)
    if os.path.exists(LEX):
        for line in open(LEX, encoding='utf-8'):
            try:
                r = json.loads(line)
            except Exception:
                continue
            p = norm_period(r.get('period'))
            rows[p] += 1; keys[p].add(r['slp1']); groups[p].add(r['group']); works[p].add(r['work'])
    allp = sorted(set(pot) | set(rows), key=lambda p: PERIOD_ORDER.get(p, 9))
    print('%-30s %9s %8s %18s %6s %6s' % ('stratum (period)', 'rows', 'keys', 'groups done/total', 'pct', 'works'))
    for p in allp:
        done, tot = len(groups[p]), pot.get(p, 0)
        pct = (100.0 * done / tot) if tot else 0.0
        flag = '  ◀ EMPTY' if done == 0 else ('  ◀ thin' if pct < 15 else '')
        print('%-30s %9d %8d %8d/%-8d %5.1f%% %5d%s'
              % (p, rows[p], len(keys[p]), done, tot, pct, len(works[p]), flag))


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    if sys.argv[1] == 'coverage':
        cmd_coverage(); return
    idx = index()
    if sys.argv[1] == 'top':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        rank = sorted(((k, len(v)) for k, v in idx.items()), key=lambda x: -x[1])
        print('%d distinct SLP1 keys; top %d by attestation count:' % (len(idx), n))
        for k, c in rank[:n]:
            print('  %-18s %5d' % (k, c))
        return
    slp1 = sys.argv[1]
    rest = sys.argv[2:]
    raw = '--raw' in rest             # particle/pronoun headwords: don't filter function words
    rest = [a for a in rest if a != '--raw']
    ls_key = rest[0] if rest else None
    pref = norm_period(resolve_period(ls_key)) if ls_key else None
    rows = idx.get(slp1, [])
    if not rows:
        print('no corpus attestation for key %r' % slp1); return
    print('=== %s : %d attestations across the corpus%s ==='
          % (slp1, len(rows), (' | <ls>=%s → prefer %s' % (ls_key, pref)) if ls_key else ''))
    for s in harvest(rows, pref):
        star = ' ◀ cited stratum' if s['period'] == pref else ''
        print('· %s · %s (%d)%s' % (s['period'], s['genre'], s['total'], star))
        shown = s['renderings'] if raw else [r for r in s['renderings'] if r['pos'] != 'func']
        if not shown:                 # pure function-word headword → the func words ARE the senses
            shown = s['renderings']
        hid = len(s['renderings']) - len(shown)
        for r in shown[:8]:
            tag = '+comm' if 'commentary' in r['kinds'] else ''
            nm = ' (name)' if r['pos'] == 'name' else ''
            var = [f for f in r['forms'] if f.lower() != r['lemma']]
            variants = ('  [' + ', '.join(var[:5]) + ']') if var else ''
            print('     %4d  %-16s%s%s %s' % (r['count'], r['lemma'] + nm, variants, '', tag))
        if hid:
            print('       (+%d function-word rendering(s) suppressed as noise)' % hid)


if __name__ == '__main__':
    main()
