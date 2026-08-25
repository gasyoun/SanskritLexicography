#!/usr/bin/env python
"""probe_wsd_strata.py — measure the candidate pool for the C1 token-in-context WSD gold.

Read-only. This is the WSD counterpart of probe_gold_strata.py (which measures the
BLI pool): it answers "what can a WSD gold set actually be drawn from?" BEFORE a
frame is sampled, so the design in
docs/WSD_GOLD_SET_ANNOTATION_PROTOCOL_2026.md rests on measured numbers rather than
assumptions. It also hosts the helpers sample_wsd_frame.py imports.

The unit of a WSD gold row is ONE TOKEN OCCURRENCE — a DCS token whose lemma is
covered by the pwg_ru store — presented in its sentence. The label (which PWG sense
fits this token) is what the annotation passes produce; nothing here emits one.

WHAT COUNTS AS A SENSE — the measurement this whole design turns on
------------------------------------------------------------------
A store row is a SUBCARD, not a sense, and the naive count (distinct `sense_tag`
over all of a lemma's rows) is wrong in three compounding ways:

  1. THE STORE SPANS FIVE DICTIONARY LAYERS — pwg 5594 rows, pw 5205, nws 432,
     sch 210, pwkvn 162 — and 97 of 254 lemmas straddle more than one. Counting
     across layers asks an annotator to choose between DICTIONARIES ("sense 2 as
     printed in PWG" vs "as printed in PW"), which is not a semantic judgment.
  2. MANY TAGS ARE NOT SENSES. Inside the pwg layer alone the tag vocabulary
     includes structural apparatus (`main`, `intro`, `head`, `tail`, `header`,
     `note`, `addendum`, `cross-ref`, `Nachtrag`) and derived-stem slots (`caus`,
     `desid`, `caus-1`, `*_verb`), alongside real numbered senses.
  3. TAGS ARE NOT NORMALIZED: `1` and `1)` are stored as different tags, so 23
     lemmas' inventories are inflated by pure punctuation.

Correcting all three collapses the picture completely, and the correction matters
because an earlier cut of this design was built on the naive count:

     lemma   rows   all-layer tags   pwg tags   pwg NUMERIC senses
     han      597        430             90            11
     gam      673        410             69             8
     viś      537        397             96            14
     store max            430             96            16  (vah)

The naive count says PWG inventories are bimodal, with a tail of 300-430-sense
verb roots that no human could pick among — which would force a separate
free-gloss tier for them, with all the shortlist-bias problems that brings. That
tail does not exist. Under the corrected definition the LARGEST inventory in the
whole store is 16, every lemma is hand-checkable, and one uniform pick-one frame
covers the entire pool.

So: A SENSE IS A PURE-NUMERIC `sense_tag` WITHIN A SINGLE LAYER (default `pwg`),
after tag normalization. What that excludes is counted and reported, never dropped
silently — see `lemma_pool()`'s rejection ledger.

Usage:
  python probe_wsd_strata.py --store <pwg_ru_translated.jsonl> --db <dcs_full.sqlite>
                             [--layer pwg] [--json out.json] [--counts-cache c.json]
  python probe_wsd_strata.py selftest
"""
import argparse
import collections
import json
import os
import re
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
from terminology_build import GLOSS_RE, clean_gloss  # noqa: E402  (reused {%...%} extractor)

# A usable sense menu entry must show the annotator actual Russian. clean_gloss()
# falls back to a markup-stripped snippet when a subcard carries no {%...%} span,
# which turns a citation-only sense ("<ls>MBh. 1, 2</ls>") into the pseudo-gloss
# "MBh. 1, 2" — a menu entry nobody can choose against. Require either a real gloss
# span or, failing that, some Cyrillic; a bare citation is Latin and digits.
CYRILLIC_RE = re.compile(r'[а-яёА-ЯЁ]')

DEFAULT_LAYER = 'pwg'
NUMERIC_TAG_RE = re.compile(r'\d+')
_TAG_TAIL_RE = re.compile(r'[)\.\s]+$')
# Leading bracketed apparatus on a gloss: "[NWS 1] [NWS: Sen 1952 : 26] [Эп.] слеза"
_APPARATUS_RE = re.compile(r'^(?:\s*\[[^\]]*\])+')
_PUNCT_RE = re.compile(r'[^\w\s]+', re.UNICODE)

# Inventory bands, cut from the measured pool (48 lemmas with >= 2 numeric senses,
# spread 2..16) so the three bands carry comparable numbers of lemmas rather than
# comparable-looking edges.
BAND_EDGES = (('I2-5', 2, 5), ('I6-9', 6, 9), ('I10+', 10, 10 ** 6))
BANDS = tuple(b[0] for b in BAND_EDGES)

# A token is only annotatable if its sentence gives real context but stays readable.
MIN_SENT_TOKENS = 5
MAX_SENT_TOKENS = 60
# A lemma needs enough occurrences that a seeded draw is a sample, not a census.
MIN_TOKENS_PER_LEMMA = 20

_NULLS = ('', 'None', 'null')


def _nz(value):
    """DCS exports write missing values as the STRING 'None'; treat those as empty."""
    if value is None:
        return ''
    s = str(value).strip()
    return '' if s in _NULLS else s


def normalize_tag(tag):
    """`1)` / `1.` / ` 1 ` -> `1`. Without this, 23 lemmas count punctuation as sense."""
    return ' '.join(_TAG_TAIL_RE.sub('', _nz(tag)).split())


def is_sense_tag(tag):
    """A sense is a pure number. `caus`, `main`, `Nachtrag`, `1a` are not.

    Derived-stem slots (`caus`, `desid`) are real PWG material but not a sense
    disambiguation task: DCS already annotates the token's morphology, so "is this
    the causative?" is read off the analysis rather than judged from context.
    Sub-senses (`1a`, `1b`) are excluded to keep the rule crisp; both classes are
    counted in the rejection ledger.
    """
    return bool(tag) and NUMERIC_TAG_RE.fullmatch(tag) is not None


def normalize_gloss(gloss):
    """Comparison form, for deciding whether two menu options are distinguishable."""
    return ' '.join(_PUNCT_RE.sub(' ', _APPARATUS_RE.sub('', gloss).lower()).split())


def sense_inventory(rows, layer=DEFAULT_LAYER):
    """Distinct PWG senses for one lemma, in the dictionary's own printed order.

    Keyed by normalized numeric `sense_tag`, valued by the cleaned Russian core
    gloss. Order is store order, which is PWG citation order — NOT sorted, because
    the lowest-numbered sense is the lexicographer's primary sense and that ordering
    is itself the MFS baseline's prediction (card 5).

    Citation-only subcards are dropped: an annotator cannot choose a sense that
    shows them no gloss. The first subcard yielding a real gloss wins a repeated tag.
    """
    inv = collections.OrderedDict()
    for r in rows:
        if layer and _nz(r.get('layer')) != layer:
            continue
        tag = normalize_tag(r.get('sense_tag'))
        if not is_sense_tag(tag) or tag in inv:
            continue
        raw = r.get('ru') or ''
        gloss = ' '.join(clean_gloss(raw).split())
        if not gloss:
            continue
        if not GLOSS_RE.search(raw) and not CYRILLIC_RE.search(gloss):
            continue
        inv[tag] = gloss
    return inv


def distinct_glosses(inv):
    """How many menu options are actually TELLABLE APART.

    Two senses whose glosses are textually identical ("[1] раздувание, вздутие" vs
    "[PW] раздувание, вздутие") are not a choice: two annotators pick between them
    at random and the kappa that results measures coin-flips, not agreement.
    """
    return len({g for g in (normalize_gloss(v) for v in inv.values()) if g})


def inventory_band(n_senses):
    """Which band an inventory of `n_senses` senses falls in."""
    for name, lo, hi in BAND_EDGES:
        if lo <= n_senses <= hi:
            return name
    return None


def load_store(path):
    """pwg_ru store -> {key1: [rows]}, preserving file order within a lemma."""
    by_lemma = collections.OrderedDict()
    with open(path, encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            key = _nz(rec.get('key1'))
            if key:
                by_lemma.setdefault(key, []).append(rec)
    return by_lemma


def lemma_pool(by_lemma, layer=DEFAULT_LAYER):
    """Store lemmas that can carry a WSD row, plus a ledger of why the rest cannot.

    Returns {key1: {'iast', 'inv', 'n_senses', 'band'}} and a Counter of exclusions.
    """
    pool, rejected = collections.OrderedDict(), collections.Counter()
    for key, rows in by_lemma.items():
        iast = _nz(rows[0].get('iast'))
        if not iast:
            rejected['no_iast'] += 1
            continue
        inv = sense_inventory(rows, layer)
        if len(inv) < 2:
            rejected['under_2_numeric_senses_in_layer'] += 1
            continue
        if distinct_glosses(inv) < 2:
            rejected['degenerate_menu_identical_glosses'] += 1
            continue
        band = inventory_band(len(inv))
        if band is None:
            rejected['unbanded'] += 1
            continue
        pool[key] = {'iast': iast, 'inv': inv, 'n_senses': len(inv), 'band': band}
    return pool, rejected


def dcs_token_counts(db_path, iast_forms, cache_path=None):
    """Tokens per lemma, in ONE table scan.

    token.lemma is NOT indexed (only lemma_id is), so a per-lemma
    `WHERE lemma = ?` is a full 5.7M-row scan EACH TIME — 250 lemmas that way costs
    minutes. One GROUP BY pass costs one scan. The result is cacheable because
    dcs_full.sqlite is a frozen corpus release.
    """
    wanted = set(iast_forms)
    if cache_path and os.path.exists(cache_path):
        with open(cache_path, encoding='utf-8') as f:
            cached = json.load(f)
        if wanted <= set(cached):
            return {k: cached[k] for k in wanted}

    con = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    counts = {k: 0 for k in wanted}
    for lemma, n in con.execute('SELECT lemma, COUNT(*) FROM token GROUP BY lemma'):
        if lemma in wanted:
            counts[lemma] = n
    con.close()

    if cache_path:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(counts, f, ensure_ascii=False, indent=1, sort_keys=True)
    return counts


def fetch_tokens(con, iast, min_sent=MIN_SENT_TOKENS, max_sent=MAX_SENT_TOKENS):
    """Every annotatable token occurrence of one lemma, with its sentence + citation.

    Sentence length is measured in DCS tokens, not characters: a 3-token sentence
    gives an annotator nothing to disambiguate from, and a 60+-token one is a
    reading task rather than a judgment.
    """
    rows = con.execute(
        'SELECT t.id, t.occ_id, t.sent_id, t.form, t.upos, t.idx, t.sentence_id,'
        '       s.text_sandhied, s.sent_counter, c.ref, x.name '
        '  FROM token t '
        '  JOIN sentence s ON s.id = t.sentence_id '
        '  LEFT JOIN chapter c ON c.chapter_id = s.chapter_id '
        '  LEFT JOIN text x ON x.text_id = c.text_id '
        ' WHERE t.lemma = ? ORDER BY t.id', (iast,)).fetchall()
    out = []
    for (tid, occ, sent_id, form, upos, idx, sentence_id,
         text, counter, ref, work) in rows:
        text = ' '.join(_nz(text).split())
        if not text:
            continue
        n_words = len(text.split())
        if not (min_sent <= n_words <= max_sent):
            continue
        citation = _nz(ref) or _nz(work) or f'sent {sent_id}'
        counter = _nz(counter)
        if counter:
            citation = f'{citation}, {counter}'
        out.append({
            'token_id': tid, 'occ_id': occ, 'sent_id': _nz(sent_id),
            'sentence_id': sentence_id, 'form': _nz(form), 'upos': _nz(upos) or 'X',
            'idx': idx, 'sentence': text, 'citation': citation,
            'work': _nz(work), 'n_words': n_words,
        })
    return out


def probe(store_path, db_path, layer=DEFAULT_LAYER, cache_path=None):
    by_lemma = load_store(store_path)
    pool, rejected = lemma_pool(by_lemma, layer)
    counts = dcs_token_counts(db_path, [v['iast'] for v in pool.values()], cache_path)

    for key, meta in pool.items():
        meta['n_tokens'] = counts.get(meta['iast'], 0)

    attested = collections.OrderedDict(
        (k, v) for k, v in pool.items() if v['n_tokens'] >= MIN_TOKENS_PER_LEMMA)
    unattested = [k for k, v in pool.items() if v['n_tokens'] == 0]

    by_band = collections.defaultdict(list)
    for key, meta in attested.items():
        by_band[meta['band']].append(key)

    layer_rows = collections.Counter(
        _nz(r.get('layer')) or '(empty)' for v in by_lemma.values() for r in v)

    return {
        'layer': layer,
        'store_lemmas': len(by_lemma),
        'layer_rows': dict(layer_rows.most_common()),
        'pool_lemmas': len(pool),
        'rejected': dict(rejected),
        'unattested_in_dcs': len(unattested),
        'unattested_sample': sorted(unattested)[:20],
        'attested_lemmas': len(attested),
        'min_tokens_per_lemma': MIN_TOKENS_PER_LEMMA,
        'max_inventory': max((v['n_senses'] for v in pool.values()), default=0),
        'by_band': {b: {'lemmas': len(v),
                        'tokens': sum(attested[k]['n_tokens'] for k in v)}
                    for b, v in sorted(by_band.items())},
        'pool': {k: {kk: vv for kk, vv in v.items() if kk != 'inv'}
                 for k, v in attested.items()},
    }


def selftest():
    import tempfile

    failures = []

    def check(label, got, want):
        if got != want:
            failures.append(f'{label}: got {got!r}, want {want!r}')

    check('band 2', inventory_band(2), 'I2-5')
    check('band 5', inventory_band(5), 'I2-5')
    check('band 9', inventory_band(9), 'I6-9')
    check('band 16', inventory_band(16), 'I10+')
    check('band 1 unbanded', inventory_band(1), None)

    check("'None' is empty", _nz('None'), '')
    check('tag normalized', normalize_tag('1)'), '1')
    check('tag normalized (dot)', normalize_tag(' 2. '), '2')
    check('numeric tag accepted', is_sense_tag('12'), True)
    check('derived-stem slot rejected', is_sense_tag('caus'), False)
    check('apparatus tag rejected', is_sense_tag('main'), False)
    check('sub-sense rejected', is_sense_tag('1a'), False)
    check('gloss apparatus stripped',
          normalize_gloss('[NWS 1] [Эп.] слеза, слёзы'), 'слеза слёзы')

    rows = [
        {'key1': 'x', 'iast': 'x', 'layer': 'pwg', 'sense_tag': '1',
         'ru': '1) {%первый%}; <lex>m.</lex>'},
        {'key1': 'x', 'iast': 'x', 'layer': 'pwg', 'sense_tag': '1)',
         'ru': '1) {%тот же тег после нормализации%}'},
        {'key1': 'x', 'iast': 'x', 'layer': 'pwg', 'sense_tag': '2',
         'ru': '2) {%второй%}'},
        {'key1': 'x', 'iast': 'x', 'layer': 'pwg', 'sense_tag': '3',
         'ru': '<ls>MBh. 1, 2</ls>'},
        {'key1': 'x', 'iast': 'x', 'layer': 'pwg', 'sense_tag': 'caus',
         'ru': 'caus) {%каузатив%}'},
        {'key1': 'x', 'iast': 'x', 'layer': 'pw', 'sense_tag': '9',
         'ru': '9) {%другой словарь%}'},
    ]
    inv = sense_inventory(rows)
    check('normalized duplicate tag collapses', len(inv), 2)
    check('first gloss wins for a repeated tag', inv['1'], 'первый')
    check('citation-only sense dropped', '3' in inv, False)
    check('derived-stem slot dropped', 'caus' in inv, False)
    check('other layer dropped', '9' in inv, False)
    check('dictionary order preserved', list(inv), ['1', '2'])

    degen = [
        {'key1': 'd', 'iast': 'd', 'layer': 'pwg', 'sense_tag': '1',
         'ru': '1) {%раздувание, вздутие%}'},
        {'key1': 'd', 'iast': 'd', 'layer': 'pwg', 'sense_tag': '2',
         'ru': '2) {%раздувание, вздутие%}'},
    ]
    check('identical glosses are not 2 distinct options',
          distinct_glosses(sense_inventory(degen)), 1)

    tmp = tempfile.mkdtemp()
    store = os.path.join(tmp, 'store.jsonl')
    with open(store, 'w', encoding='utf-8') as f:
        for r in rows + degen:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
        f.write(json.dumps({'key1': 'y', 'iast': 'y', 'layer': 'pwg',
                            'sense_tag': '1', 'ru': '1) {%один%}'},
                           ensure_ascii=False) + '\n')
        for tag in ('1', '2'):
            f.write(json.dumps({'key1': 'z', 'iast': '', 'layer': 'pwg',
                                'sense_tag': tag, 'ru': f'{tag}) {{%нет иаст{tag}%}}'},
                               ensure_ascii=False) + '\n')
    loaded = load_store(store)
    check('store lemmas', len(loaded), 4)
    pool, rejected = lemma_pool(loaded)
    check('pool keeps only the usable lemma', list(pool), ['x'])
    check('monosemous rejection logged', rejected['under_2_numeric_senses_in_layer'], 1)
    check('degenerate rejection logged', rejected['degenerate_menu_identical_glosses'], 1)
    check('no-iast rejection logged', rejected['no_iast'], 1)

    # A tiny in-memory DCS: proves the sentence-length gate and the citation join.
    db = os.path.join(tmp, 'dcs.sqlite')
    con = sqlite3.connect(db)
    con.executescript(
        'CREATE TABLE text (text_id INTEGER PRIMARY KEY, name TEXT);'
        'CREATE TABLE chapter (chapter_id INTEGER PRIMARY KEY, text_id INTEGER, ref TEXT);'
        'CREATE TABLE sentence (id INTEGER PRIMARY KEY, sent_id TEXT, chapter_id INTEGER,'
        '                       sent_counter TEXT, text_sandhied TEXT);'
        'CREATE TABLE token (id INTEGER PRIMARY KEY, sentence_id INTEGER, occ_id INTEGER,'
        '                    sent_id TEXT, idx INTEGER, form TEXT, lemma TEXT, upos TEXT);')
    con.execute("INSERT INTO text VALUES (1, 'Mahābhārata')")
    con.execute("INSERT INTO chapter VALUES (10, 1, 'MBh, 1')")
    con.execute("INSERT INTO sentence VALUES (100, 's100', 10, '7', "
                "'ekaṃ dve trīṇi catvāri pañca ṣaṭ')")          # 6 words -> kept
    con.execute("INSERT INTO sentence VALUES (101, 's101', 10, '8', 'x y')")  # 2 -> dropped
    con.execute("INSERT INTO sentence VALUES (102, 's102', 10, 'None', 'None')")  # dropped
    con.execute("INSERT INTO token VALUES (1, 100, 900, 's100', 2, 'dve', 'x', 'NUM')")
    con.execute("INSERT INTO token VALUES (2, 101, 901, 's101', 1, 'x', 'x', 'NOUN')")
    con.execute("INSERT INTO token VALUES (3, 102, 902, 's102', 1, 'x', 'x', 'NOUN')")
    con.commit()

    toks = fetch_tokens(con, 'x')
    check('short and empty sentences dropped', len(toks), 1)
    check('citation joins chapter.ref + counter', toks[0]['citation'], 'MBh, 1, 7')
    check('upos carried', toks[0]['upos'], 'NUM')
    con.close()

    counts = dcs_token_counts(db, ['x', 'absent'])
    check('one-pass counts', counts['x'], 3)
    check('absent lemma counts 0', counts['absent'], 0)

    cache = os.path.join(tmp, 'counts.json')
    dcs_token_counts(db, ['x'], cache)
    check('counts cache written', os.path.exists(cache), True)

    if failures:
        print('SELFTEST FAIL')
        for f_ in failures:
            print('  -', f_)
        return 1
    print('SELFTEST PASS (band edges, tag normalization, layer + apparatus filters, '
          'degenerate menus, sentence gate, citation join, one-pass counts)')
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--store', required=True, help='pwg_ru_translated.jsonl')
    ap.add_argument('--db', required=True, help='dcs_full.sqlite')
    ap.add_argument('--layer', default=DEFAULT_LAYER,
                    help="dictionary layer to confine senses to (default 'pwg'; "
                         "'' mixes layers and is NOT a sense task)")
    ap.add_argument('--counts-cache', default=None)
    ap.add_argument('--json', default=None)
    args = ap.parse_args()

    rep = probe(args.store, args.db, args.layer, args.counts_cache)
    print(f'layer confined to           : {rep["layer"]!r}')
    print(f'store rows by layer         : {rep["layer_rows"]}')
    print(f'store lemmas                : {rep["store_lemmas"]}')
    print(f'usable pool                 : {rep["pool_lemmas"]}  rejected={rep["rejected"]}')
    print(f'largest inventory in pool   : {rep["max_inventory"]} senses')
    print(f'absent from DCS             : {rep["unattested_in_dcs"]}')
    print(f'attested (>= {rep["min_tokens_per_lemma"]} tokens)      : {rep["attested_lemmas"]}')
    print('\nby inventory band:')
    print(f'  {"band":<8}{"lemmas":>8}{"tokens":>10}')
    for band, v in rep['by_band'].items():
        print(f'  {band:<8}{v["lemmas"]:>8}{v["tokens"]:>10}')
    thin = [b for b, v in rep['by_band'].items() if v['lemmas'] < 12]
    if thin:
        print(f'\nNOTE: bands resting on < 12 lemmas — report pooled, never as a '
              f'per-band rate: {thin}')
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(rep, f, ensure_ascii=False, indent=1)
        print(f'\nwrote {args.json}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
