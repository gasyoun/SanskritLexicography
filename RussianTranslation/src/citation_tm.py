#!/usr/bin/env python
r"""Citation translation-memory lookup — reuse an existing translation of record
for a PWG `<ls>` source citation instead of re-translating it (H1304 RU; H2334 EN).

MG's ask (H178 vote N1/N6/N9/N11/N18): whenever a PWG card cites a passage of a
text that ALREADY has a published/aligned Russian translation (R., MBH., ṚV.,
KATHĀS., …), the card's citation rendering must **reuse that translation** — for
every covered text, everywhere. This module is the lookup that makes that
possible: `lookup(prefix, locus, lang="ru")` maps a PWG citation to a corpus
passage and returns its translation-of-record segment, or a clean/typed miss.

`lang="en"` (H2334) is a **pilot**: only ṚV./RV. is wired, of-record =
Griffith 1896 PD from `pwg_ru/griffith_en_1896.json` (DB-independent). Other
prefixes miss as text-not-covered / en-translation-unpublished.

TWO layers, deliberately separate:

  1. RESOLVER (DB-independent) — maps a PWG abbreviation + locus to a
     SamudraManthanam corpus `canonical_id` passage, using the per-text
     locus-mapping scheme documented in `pwg_ru/COVERED_TEXTS_RU.md`. This is
     pure arithmetic on the citation; it runs anywhere, including CI without the
     742 MB corpus.

  2. CORPUS FETCH (DB-gated) — reads the `#ru` line for that `canonical_id` from
     SamudraManthanam's `corpus.db` (read-only; the SAME db corpus_gate reuses).
     Absent in CI / a fresh worktree by design; the lookup then reports
     `evidence_unavailable`, never a fabricated hit.

`status` is one of:
  'hit'                  — resolver mapped it AND the corpus has that passage's RU.
  'miss'                 — a clean, honest non-hit, with a `reason`:
        'text-not-covered'    the text has no RU asset at all (TS., SUŚR., …).
        'locus-not-in-corpus' the text IS covered but this passage isn't ingested
                              — a real coverage hole, closable by ingestion.
        'ru-translation-unpublished'
                              the text is covered elsewhere but THIS kāṇḍa has no
                              Russian translation of record anywhere — Rāmāyaṇa
                              kāṇḍas 4 (kiṣkindhā), 6 (yuddha), 7 (uttara), which
                              carry a `blocker` field naming the kāṇḍa. Split off
                              from 'locus-not-in-corpus' 27-07-2026 (H1705): the
                              two had shared one reason string, and reading book
                              7's miss as an ingest/numbering gap is what got a
                              Bombay-concordance handoff minted for a book whose
                              real blocker is that nobody has translated it.
        'locus-parse-failed'  the citation locus didn't parse.
  'unmapped_locus_scheme'— the text is covered but its PWG citation scheme does
                           NOT map 1:1 to the corpus keying, so no lookup is
                           possible without an external concordance. Remaining
                           case: MBH. (PWG cites continuous Calcutta ślokas;
                           corpus keys critical parvan.adhyaya.verse). H1652
                           built and MEASURED the cumulative-adhyāya candidate
                           map and REJECTED it — see `_mbh_unmapped`.
                           R. GORR. + plain R. books 3-6 (Gorresio-keyed per
                           pwgbib 1.247) LEFT this bucket 26-07-2026: they now
                           resolve through the content-based Gorresio-Southern
                           verse concordance (reuse ON per MG), with two typed
                           miss reasons instead of a scheme gap:
                             'no-southern-counterpart' - Bengal-only verse, the
                                Southern text genuinely lacks it;
                             'gorresio-etext-gap' - sarga not in the e-text.
                                Extinct since 26-07-2026 (H1689 OCRed the
                                vols 2/4/uk scans; all 672 sargas covered) —
                                the branch stays as a defensive guard.
  'evidence_unavailable' — the corpus DB is absent, so a resolved hit could not be
                           confirmed (distinct from 'miss': we simply couldn't look).

**Rights (load-bearing).** Every RU translation of record here (Elizarenkova,
Leonov, «Океан сказаний», …) is in-copyright. The returned `ru` text is for a
GENERATION-TIME consult only — fed to the translator model so it does not
re-translate a covered citation — and MUST NOT be written to any committed file
or public artifact. `rights_flag='metadata-only'` marks this on every hit. The
166k-hallucination lesson stands: a MISS stays a miss; a model never fills a
missing translation-of-record from world knowledge.

  python src/citation_tm.py lookup "R." "2,91,26"     # one lookup (loci+status)
  python src/citation_tm.py selftest                   # CI gate — see below
"""
import argparse
import json
import os
import re
import sqlite3
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
from sibling_root import sibling_root  # noqa: E402
GITHUB = sibling_root(HERE)
CORPUS_DB = os.environ.get(
    'SAMUDRA_CORPUS_DB', os.path.join(GITHUB, 'SamudraManthanam', 'web', 'corpus.db'))
# EN of-record for Ṛgveda (H2334): Griffith 1896 PD, committed under pwg_ru/.
GRIFFITH_EN_JSON = os.path.join(
    os.path.dirname(HERE), 'pwg_ru', 'griffith_en_1896.json')
_GRIFFITH_BY_LOC = None  # lazy dict location -> text
# Prefixes that have an EN of-record in this pilot (Griffith only).
_EN_RV_PREFIXES = frozenset(('ṚV.', 'RV.'))

# Sentinel returned by a resolver when the text is covered but its citation scheme
# cannot map to the corpus keying (needs an external concordance).
UNMAPPED = object()

# --- per-text locus resolvers ------------------------------------------------
# Each maps a PWG citation locus (comma-separated coordinate string) to a corpus
# `canonical_id` passage (without the #ru/#sa suffix), per COVERED_TEXTS_RU.md.
# Return None on a parse failure; return UNMAPPED for a documented scheme gap.

_RAMA_KANDA = {  # PWG book number -> corpus kāṇḍa file (Schlegel books only; see below)
    1: '01_ramayana-balakanda', 2: '02_ramayana-ayodhyakanda',
}
# PWG's plain "R." is a THREE-edition composite (pwgbib 1.247): books 1-2 cite
# SCHLEGEL (numbering ~vulgate; the R. 2,91,26 fixture is human-validated),
# books 3-6 cite GORRESIO — the Gauḍīya/Bengal recension, NOT the Southern
# text Leonov translated — and book 7 the Bombay edition (~vulgate uttara).
# Verified empirically (H1656): store citations reach R. 3,79 / 4,63 / 5,94 —
# exactly the Gorresio sarga counts (79/63/95), far past the Southern ones
# (75/–/68). So books 3-6 MUST NOT key into the Southern corpus: an in-range
# locus would return the WRONG verse's translation silently. They stay
# UNMAPPED until the Gorresio<->Southern concordance validates
# (src/build_ramayana_concordance.py, DRAFT-STRUCTURAL).
_RAMA_GORRESIO_BOOKS = {3, 4, 5, 6}

# Kāṇḍas for which NO Russian translation of record exists anywhere — not in the
# corpus, not in the archive, not in print. Gryntser's academic translation
# stopped after book 3, Leonov's covers Sundara (5); kiṣkindhā (4) is blocked on
# Serebryany's introduction, yuddha (6) is a literary draft targeted at ~2029 and
# uttara (7) is not in the pipeline at all (RussianRamayana `project-status`).
# These are NOT corpus-coverage holes, and saying `locus-not-in-corpus` for them
# invites exactly the wrong fix — H1705 was minted to "bridge the numbering" for
# book 7 on that reading, when the numbering was never the blocker.
_RAMA_NO_RU_KANDA = {4: 'kiṣkindhā', 6: 'yuddha', 7: 'uttara'}


def _nums(locus):
    return [int(x) for x in re.findall(r'\d+', locus or '')]


def _rama(locus):
    n = _nums(locus)
    if len(n) != 3:
        return None
    book, sarga, verse = n
    if book in _RAMA_GORRESIO_BOOKS:   # Gorresio-keyed loci -> content concordance
        return _rama_gorresio(locus)
    work = _RAMA_KANDA.get(book)
    if work is None:
        # book 7 — cited from the Bombay ed. (111 sargas + 13 interpolated),
        # measured NOT ≈1:1 against the 100-sarga corpus text under H1705, and
        # with no Russian uttarakāṇḍa to reuse either way.
        return ('__ramayana_no_ru_kanda__', book) if book in _RAMA_NO_RU_KANDA \
            else ('__ramayana_absent_kanda__', book)
    return '%s:%d.%d' % (work, sarga, verse)


def _rigveda(locus):
    n = _nums(locus)
    if len(n) != 3:
        return None
    mandala, sukta, verse = n
    if not 1 <= mandala <= 10:
        return None
    return '%02d_rigveda:%d.%d' % (mandala, sukta, verse)


def _atharva(locus):
    n = _nums(locus)
    if len(n) != 3:
        return None
    kanda, sukta, verse = n
    if not 1 <= kanda <= 19:
        return None
    return '%02d_atharvaveda:%d.%d' % (kanda, sukta, verse)


def _manu(locus):
    n = _nums(locus)
    if len(n) != 2:
        return None
    return 'manavadharmashastra:%d.%d' % (n[0], n[1])


def _mbh_unmapped(locus):
    # PWG cites the Calcutta edition's continuous per-parvan śloka number
    # (e.g. MBH. 5,7331); corpus keys the critical edition's parvan.adhyaya.verse.
    # H1652 BUILT the obvious candidate map — a cumulative adhyāya-length table
    # over the eighteen-parvan Nīlakaṇṭha-vulgate<->critical concordances that
    # CommentaryStrategies already ships — and MEASURED it against the store:
    # 11.2% of 1,327 locatable citations land within ±2 verses (random null
    # 2.5%), 16% under a fitted per-parvan rescale, 1/43 on the anchors whose
    # true verse is unambiguous. The vulgate witness is also shorter than the
    # text PWG counts in 8/18 parvans, so 145 citations have no ordinal at all.
    # REJECTED: numbers + method in `build_mbh_concordance.py` and
    # pwg_ru/H1652_MBH_CALCUTTA_VALIDATION_2026-07-26.md. Closing this needs the
    # Calcutta text itself, not arithmetic over a different witness.
    return UNMAPPED


# Gorresio kāṇḍa -> corpus work. ONLY kāṇḍas the corpus actually carries may
# appear here: `corpus.db` holds Rāmāyaṇa 1, 2, 3 (Gryntser 2006/2014) and 5
# (Leonov 2024) and nothing else, because no Russian translation of record for
# kiṣkindhā (4), yuddha (6) or uttara (7) exists at all — Gryntser's academic
# translation stopped after book 3, Leonov's covers Sundara (H1652 census of
# `sources`). Naming an absent work here does not fail loudly; it fabricates a
# `canonical_id` for a passage that cannot be fetched, so a consumer reading
# that field sees a resolution where there is none. Kāṇḍas 4/6/7 therefore fall
# through to the covered-but-absent branch below — a typed miss, no id.
_RAMA_GORR_WORK = {
    1: '01_ramayana-balakanda', 2: '02_ramayana-ayodhyakanda',
    3: '03_ramayana-aranyakanda', 5: '05_ramayana-sundarakanda',
}

_GORR_MAP = None


def _gorr_map():
    """Lazy-load the CONTENT-BASED Gorresio->Southern verse concordance
    (`ramayana_gorresio_southern_verse_map.tsv`, built by
    `build_ramayana_concordance.py build-gorresio` from the Gorresio e-text
    recovered out of the Cologne scan PDFs' embedded Google text layer).
    Only `matched`/`fuzzy` rows key reuse; `moved` (off-backbone formulaic
    repeats) deliberately does NOT — that was the disagreement class in the
    H783 cross-validation."""
    global _GORR_MAP
    if _GORR_MAP is None:
        rows, covered = {}, set()
        path = os.path.join(HERE, 'ramayana_gorresio_southern_verse_map.tsv')
        if os.path.exists(path):
            import csv
            with open(path, encoding='utf-8') as fh:
                for r in csv.DictReader(fh, delimiter='\t'):
                    key = (int(r['g_kanda']), int(r['g_sarga']), int(r['g_verse']))
                    covered.add(key[:2])
                    if r['class'] in ('matched', 'fuzzy') and r['s_sarga']:
                        rows[key] = (int(r['s_sarga']), int(r['s_verse']),
                                     r['score'], r['class'])
        _GORR_MAP = (rows, covered)
    return _GORR_MAP


def _rama_gorresio(locus):
    # Reuse ON by default (MG ruling 26-07-2026): a Gorresio locus resolves via
    # the content-based verse concordance; where the Bengal recension has no
    # Southern counterpart the lookup stays an HONEST miss
    # ('no-southern-counterpart') — never an invented offset (166k lesson).
    n = _nums(locus)
    if len(n) != 3:
        return None
    k, s, v = n
    if k not in _RAMA_GORR_WORK:      # kiṣkindhā (4), yuddha (6) — no RU exists
        return ('__ramayana_no_ru_kanda__', k) if k in _RAMA_NO_RU_KANDA \
            else ('__ramayana_absent_kanda__', k)
    rows, covered = _gorr_map()
    row = rows.get((k, s, v))
    if row is None:
        # e-text covers a sarga -> a missing verse is a REAL recension gap;
        # an uncovered sarga (vols 2/4/uk have no PDF text layer yet) is an
        # e-text acquisition gap, not evidence about the recension.
        if (k, s) in covered:
            return ('__gorresio_unmatched__', k)
        return ('__gorresio_etext_gap__', k)
    ss, sv, score, cls = row
    return ('__gorresio_mapped__',
            '%s:%d.%d' % (_RAMA_GORR_WORK[k], ss, sv),
            {'map': 'gorresio_southern_verse_map', 'class': cls, 'score': score,
             'g_locus': '%d,%d,%d' % (k, s, v)})


# PWG abbreviation (normalized, trailing dot/space-insensitive) -> (resolver, meta).
# meta: (text, translator/source, rights_flag). Only texts with an RU asset appear;
# anything not here is 'text-not-covered' (a clean miss: TS., SUŚR., HARIV., ŚAT. BR.).
RESOLVERS = {
    'R.':        (_rama,      ('Rāmāyaṇa (Southern)', 'Leonov', 'metadata-only')),
    'R. GORR.':  (_rama_gorresio, ('Rāmāyaṇa (Gauḍīya, Gorresio)', 'Leonov via H1656 concordance', 'metadata-only')),
    'R. ed. GORR.': (_rama_gorresio, ('Rāmāyaṇa (Gauḍīya, Gorresio)', 'Leonov via H1656 concordance', 'metadata-only')),
    'GORR.':     (_rama_gorresio, ('Rāmāyaṇa (Gauḍīya, Gorresio)', 'Leonov via H1656 concordance', 'metadata-only')),
    'MBH.':      (_mbh_unmapped, ('Mahābhārata', 'SamudraManthanam', 'metadata-only')),
    'ṚV.':       (_rigveda,   ('Ṛgveda', 'Elizarenkova (1:1)', 'metadata-only')),
    'RV.':       (_rigveda,   ('Ṛgveda', 'Elizarenkova (1:1)', 'metadata-only')),
    'AV.':       (_atharva,   ('Atharvaveda', 'corpus RU', 'metadata-only')),
    'M.':        (_manu,      ('Mānava-dharmaśāstra', 'corpus RU', 'metadata-only')),
}


def _norm_prefix(prefix):
    """Collapse whitespace; keep the trailing dot form used as the RESOLVERS key."""
    p = re.sub(r'\s+', ' ', (prefix or '').strip())
    return p


def _fetch_ru(canonical):
    """DB-gated: return (ru_text, db_status). db_status in {'ok','db_absent','db_error'}."""
    if not os.path.exists(CORPUS_DB):
        return None, 'db_absent'
    try:
        con = sqlite3.connect('file:%s?mode=ro' % CORPUS_DB, uri=True)
        try:
            row = con.execute(
                "SELECT line_text FROM corpus_lines WHERE canonical_id = ? LIMIT 1",
                (canonical + '#ru',)).fetchone()
        finally:
            con.close()
    except Exception as ex:
        sys.stderr.write('corpus query FAILED (evidence NOT confirmed empty): %s\n' % ex)
        return None, 'db_error'
    return (row[0] if row else None), 'ok'


def _load_griffith_index():
    """Lazy-load Griffith 1896 location → text (stdlib JSON; once per process)."""
    global _GRIFFITH_BY_LOC
    if _GRIFFITH_BY_LOC is not None:
        return _GRIFFITH_BY_LOC
    if not os.path.exists(GRIFFITH_EN_JSON):
        _GRIFFITH_BY_LOC = {}
        return _GRIFFITH_BY_LOC
    data = json.load(open(GRIFFITH_EN_JSON, encoding='utf-8'))
    contents = data.get('contents') if isinstance(data, dict) else data
    idx = {}
    for row in contents or []:
        loc = row.get('location')
        text = row.get('text')
        if loc and text:
            idx[loc] = text
    _GRIFFITH_BY_LOC = idx
    return _GRIFFITH_BY_LOC


def _canonical_to_griffith_loc(canonical):
    """Map resolver canonical_id `01_rigveda:1.1` → Griffith location `1.1.1`.

    Mandala is zero-padded in the work id; Griffith keys drop the pad
    (mandala.sukta.verse). Unit-pinned in selftest EN block (H2334).
    """
    if not canonical or not isinstance(canonical, str):
        return None
    m = re.match(r'^(\d{2})_rigveda:(\d+)\.(\d+)$', canonical)
    if not m:
        return None
    return '%d.%s.%s' % (int(m.group(1)), m.group(2), m.group(3))


def _fetch_en_rv(canonical):
    """DB-independent EN of-record for ṚV.: Griffith 1896 by location.

    Returns (en_text_or_None, griffith_location_or_None, asset_status).
    asset_status in {'ok', 'asset_absent'}.
    """
    loc = _canonical_to_griffith_loc(canonical)
    if loc is None:
        return None, None, 'ok'
    if not os.path.exists(GRIFFITH_EN_JSON):
        return None, loc, 'asset_absent'
    idx = _load_griffith_index()
    return idx.get(loc), loc, 'ok'


def lookup(prefix, locus, lang='ru'):
    """Resolve a PWG `<ls>` citation to a translation of record.

    `lang` defaults to ``ru`` (all existing callers unchanged). ``lang="en"``
    (H2334) returns Griffith 1896 for ṚV./RV. only; other prefixes miss.

    Returns a dict: status, prefix, locus, canonical_id, text, source, rights_flag,
    reason (on miss), and either `ru` or `en` (ONLY populated for a hit).
    RU hits are generation-time consult only (in-copyright, never persist).
    EN Griffith hits are public domain (`rights_flag=pd`) but selftest still
    prints char-count only — never full verse bodies in CI logs.
    """
    lang = (lang or 'ru').strip().lower()
    p = _norm_prefix(prefix)
    base = {'prefix': p, 'locus': locus, 'canonical_id': None, 'ru': None, 'en': None}

    if lang not in ('ru', 'en'):
        return {**base, 'status': 'miss', 'reason': 'invalid-lang',
                'text': None, 'source': None, 'rights_flag': None}

    # --- EN pilot path (H2334): Griffith for ṚV./RV. only; no corpus.db -----
    if lang == 'en':
        if p not in _EN_RV_PREFIXES:
            # RU-covered texts without an EN of-record (R., MBH., AV., M., …)
            # vs texts with no asset at all (TS., …) — honest split.
            if p in RESOLVERS:
                return {**base, 'status': 'miss',
                        'reason': 'en-translation-unpublished',
                        'text': RESOLVERS[p][1][0], 'source': None,
                        'rights_flag': None}
            return {**base, 'status': 'miss', 'reason': 'text-not-covered',
                    'text': None, 'source': None, 'rights_flag': None}
        base.update({'text': 'Ṛgveda', 'source': 'Griffith 1896',
                     'rights_flag': 'pd'})
        resolved = _rigveda(locus)
        if resolved is None:
            return {**base, 'status': 'miss', 'reason': 'locus-parse-failed'}
        en, g_loc, asset_status = _fetch_en_rv(resolved)
        base['canonical_id'] = resolved
        if g_loc is not None:
            base['griffith_location'] = g_loc
        if asset_status == 'asset_absent':
            return {**base, 'status': 'evidence_unavailable',
                    'reason': 'griffith_en_1896.json absent'}
        if en:
            return {**base, 'status': 'hit', 'en': en}
        return {**base, 'status': 'miss', 'reason': 'locus-not-in-corpus'}

    # --- RU path (H1304): unchanged behaviour --------------------------------
    entry = RESOLVERS.get(p)
    if entry is None:
        return {**base, 'status': 'miss', 'reason': 'text-not-covered',
                'text': None, 'source': None, 'rights_flag': None}
    resolver, (text, source, rights) = entry
    base.update({'text': text, 'source': source, 'rights_flag': rights})
    resolved = resolver(locus)
    if resolved is UNMAPPED:
        return {**base, 'status': 'unmapped_locus_scheme',
                'reason': 'citation scheme has no 1:1 corpus map (needs a concordance)'}
    if resolved is None:
        return {**base, 'status': 'miss', 'reason': 'locus-parse-failed'}
    if isinstance(resolved, tuple) and resolved[0] == '__ramayana_no_ru_kanda__':
        # The blocker is the TRANSLATION, not the corpus and not the locus map:
        # no Russian kiṣkindhā/yuddha/uttara exists to reuse. Typed apart from
        # `locus-not-in-corpus` (a real coverage hole, closable by ingestion) so
        # the two never again get one fix aimed at the other — H1705.
        return {**base, 'status': 'miss', 'reason': 'ru-translation-unpublished',
                'canonical_id': None,
                'blocker': {'kanda': resolved[1],
                            'name': _RAMA_NO_RU_KANDA[resolved[1]]}}
    if isinstance(resolved, tuple) and resolved[0] == '__ramayana_absent_kanda__':
        return {**base, 'status': 'miss', 'reason': 'locus-not-in-corpus',
                'canonical_id': None}
    if isinstance(resolved, tuple) and resolved[0] == '__gorresio_unmatched__':
        # Bengal-recension verse with no Southern counterpart in the content
        # concordance — an honest, typed miss, NOT a scheme gap.
        return {**base, 'status': 'miss', 'reason': 'no-southern-counterpart'}
    if isinstance(resolved, tuple) and resolved[0] == '__gorresio_etext_gap__':
        # Sarga not yet in the Gorresio e-text (vols 2/4/uk scans carry no
        # text layer) — reuse pending e-text completion, not a recension verdict.
        return {**base, 'status': 'miss', 'reason': 'gorresio-etext-gap'}
    if isinstance(resolved, tuple) and resolved[0] == '__gorresio_mapped__':
        base['map'] = resolved[2]
        resolved = resolved[1]
    ru, db_status = _fetch_ru(resolved)
    base['canonical_id'] = resolved
    if db_status == 'db_absent':
        return {**base, 'status': 'evidence_unavailable', 'reason': 'corpus.db absent'}
    if db_status == 'db_error':
        return {**base, 'status': 'evidence_unavailable', 'reason': 'corpus query failed'}
    if ru:
        return {**base, 'status': 'hit', 'ru': ru}
    return {**base, 'status': 'miss', 'reason': 'locus-not-in-corpus'}


# --- <ls> card consult (generation-time integration point) -------------------
_LS = re.compile(r'<ls\b([^>]*)>(.*?)</ls>', re.S)
_N_ATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')
_ABBR = re.compile(r'^\s*([^0-9]*?)\s*[0-9]')


def _split_citation(n_attr, visible):
    """From an <ls n="..."> attr + visible text, return (prefix, locus) or None.
    Mirrors build_citation_index.abbr_of: prefer the n= attribute (it carries the
    inherited work for bare-number continuation refs)."""
    for s in (n_attr, visible):
        if not s:
            continue
        m = _ABBR.match(s)
        if m and m.group(1).strip():
            prefix = m.group(1).strip()
            locus = s[m.end(1):].strip().rstrip('.').strip()
            return prefix, locus
    return None


def consult_card(*fields, lang='ru'):
    """Generation-time consult: given a card's DE/RU/EN text field(s) carrying
    `<ls>` citations, return one lookup() record per DISTINCT citation whose text
    is covered by a translation of record for ``lang`` (default ``ru``).
    Intended for corpus_gate.build_card() (and EN generation) so a covered
    citation surfaces its of-record rendering instead of being retranslated.
    Uncovered citations are omitted (a clean miss needs no consult).
    ``lang`` is keyword-only after *fields so existing positional callers stay safe.
    """
    seen, out = set(), []
    for fld in fields:
        for m in _LS.finditer(fld or ''):
            nm = _N_ATTR.search(m.group(1) or '')
            parsed = _split_citation(nm.group(1) if nm else None, (m.group(2) or '').strip())
            if not parsed:
                continue
            key = (parsed[0], parsed[1], lang)
            if key in seen:
                continue
            seen.add(key)
            rec = lookup(parsed[0], parsed[1], lang=lang)
            if rec['status'] in ('hit', 'unmapped_locus_scheme'):
                out.append(rec)
    return out


# --- selftest (CI gate) ------------------------------------------------------
def selftest():
    """Two layers, matching the module design:

      MAPPING checks (DB-independent — always run, incl. CI without the corpus):
        R. 2,91,26  -> resolves to 02_ramayana-ayodhyakanda:91.26
        TS. 2,3,1,4 -> text-not-covered (clean miss; TS. has no RU asset, MG N18)
        MBH. 5,7331 -> unmapped_locus_scheme (Calcutta<->critical concordance GAP, MG N1)

      LIVE checks (DB-gated — skipped, not failed, when corpus.db is absent):
        R. 2,91,26  -> a non-empty RU line exists in the corpus (MG N1)

    Prints status + canonical_id + RU char-count only — never the in-copyright RU
    text itself (this runs in CI)."""
    fails = []

    def check(cond, msg):
        print(('  ok   ' if cond else '  FAIL ') + msg)
        if not cond:
            fails.append(msg)

    print('MAPPING checks (DB-independent):')
    r = lookup('R.', '2,91,26')
    check(r['canonical_id'] == '02_ramayana-ayodhyakanda:91.26',
          'R. 2,91,26 -> %s' % r['canonical_id'])
    ts = lookup('TS.', '2,3,1,4')
    check(ts['status'] == 'miss' and ts['reason'] == 'text-not-covered',
          'TS. 2,3,1,4 -> %s/%s (clean miss, N18)' % (ts['status'], ts.get('reason')))
    mbh = lookup('MBH.', '5,7331')
    check(mbh['status'] == 'unmapped_locus_scheme',
          'MBH. 5,7331 -> %s (Calcutta<->critical GAP, N1)' % mbh['status'])
    gorr = lookup('R. GORR.', '2,5,27')
    check(gorr['canonical_id'] == '02_ramayana-ayodhyakanda:6.27',
          'R. GORR. 2,5,27 -> %s via content concordance (reuse ON, MG 26-07)'
          % gorr['canonical_id'])
    r3 = lookup('R.', '3,79,10')
    check(r3['status'] == 'miss' and r3['reason'] == 'no-southern-counterpart',
          'R. 3,79,10 -> %s/%s (Bengal-only verse, honest miss)'
          % (r3['status'], r3.get('reason')))
    gap = lookup('R. GORR.', '2,16,46')
    check(gap['status'] == 'miss' and gap['reason'] == 'no-southern-counterpart',
          'R. GORR. 2,16,46 -> %s/%s (H1689 OCR closed the vol-2 e-text gap; '
          'the verse itself is Bengal-only — best Southern score 0.109 < 0.25 floor)'
          % (gap['status'], gap.get('reason')))
    sun = lookup('R. GORR.', '5,10,1')
    check(sun.get('canonical_id') == '05_ramayana-sundarakanda:2.51',
          'R. GORR. 5,10,1 -> %s (Sundara live via the H1689 OCR e-text)'
          % sun.get('canonical_id'))
    # H1652: kāṇḍas 4/6/7 have NO Russian translation of record, so no corpus
    # work exists for them. The failure mode being pinned is a resolution that
    # LOOKS real — a canonical_id naming a work `corpus.db` does not carry.
    # H1705 retyped the reason: these are a TRANSLATION gap, and the old shared
    # 'locus-not-in-corpus' string read like an ingestion/numbering one.
    for locus, name in (('4,10,1', 'kiṣkindhā'), ('6,20,1', 'yuddha'),
                        ('7,5,1', 'uttara')):
        ab = lookup('R. GORR.', locus)
        check(ab['status'] == 'miss'
              and ab['reason'] == 'ru-translation-unpublished'
              and ab.get('blocker', {}).get('name') == name
              and ab['canonical_id'] is None,
              'R. GORR. %s (%s) -> %s/%s, no canonical_id (no RU translation exists)'
              % (locus, name, ab['status'], ab.get('reason')))
    # H1705, plain `R.` book 7 — the Bombay ed. PWG cites there runs to sarga 111
    # (+13 interpolated); the corpus text stops at 100, so 127 of the 1,781 R.-7
    # citations name a sarga no corpus verse can carry. Both a low and an
    # out-of-range sarga must land on the same honest, typed miss.
    for locus in ('7,5,1', '7,108,3'):
        b7 = lookup('R.', locus)
        check(b7['status'] == 'miss'
              and b7['reason'] == 'ru-translation-unpublished'
              and b7['canonical_id'] is None,
              'R. %s -> %s/%s, no canonical_id (Bombay uttara, no RU)'
              % (locus, b7['status'], b7.get('reason')))

    print('LIVE corpus checks (DB-gated):')
    if not os.path.exists(CORPUS_DB):
        print('  skip  corpus.db absent (%s) — live-hit checks skipped, not failed' % CORPUS_DB)
    else:
        r2 = lookup('R.', '2,91,26')
        check(r2['status'] == 'hit' and r2['ru'],
              'R. 2,91,26 -> hit, RU %d chars (N1)' % (len(r2['ru']) if r2['ru'] else 0))
        m = lookup('M.', '1,1')
        check(m['status'] == 'hit' and m['ru'], 'M. 1,1 -> hit, RU %d chars' % (len(m['ru']) if m['ru'] else 0))
        g = lookup('R. GORR.', '1,22,1')
        check(g['status'] == 'hit' and g['ru'] and g.get('map', {}).get('class') == 'matched',
              'R. GORR. 1,22,1 -> hit via concordance, RU %d chars, class %s'
              % (len(g['ru']) if g['ru'] else 0, g.get('map', {}).get('class')))

    # H2334: EN citation-TM pilot — Griffith 1896 for ṚV. only. Fully
    # DB-independent (committed JSON); char-count only in CI logs, never verse body.
    print('EN Griffith checks (DB-independent, H2334):')
    check(_canonical_to_griffith_loc('01_rigveda:1.1') == '1.1.1',
          "canonical 01_rigveda:1.1 -> Griffith location 1.1.1")
    check(_canonical_to_griffith_loc('10_rigveda:90.1') == '10.90.1',
          "canonical 10_rigveda:90.1 -> Griffith location 10.90.1")
    en1 = lookup('ṚV.', '1,1,1', lang='en')
    check(en1['status'] == 'hit'
          and en1.get('en')
          and en1.get('rights_flag') == 'pd'
          and en1.get('source') == 'Griffith 1896'
          and en1.get('griffith_location') == '1.1.1'
          and en1.get('canonical_id') == '01_rigveda:1.1',
          'ṚV. 1,1,1 lang=en -> hit, Griffith 1.1.1, EN %d chars, rights=pd'
          % (len(en1['en']) if en1.get('en') else 0))
    en10 = lookup('ṚV.', '10,90,1', lang='en')
    check(en10['status'] == 'hit'
          and en10.get('en')
          and en10.get('griffith_location') == '10.90.1',
          'ṚV. 10,90,1 lang=en -> hit, Griffith 10.90.1, EN %d chars'
          % (len(en10['en']) if en10.get('en') else 0))
    en_ts = lookup('TS.', '2,3,1,4', lang='en')
    check(en_ts['status'] == 'miss' and en_ts.get('reason') == 'text-not-covered',
          'TS. 2,3,1,4 lang=en -> %s/%s (no EN of-record, clean miss)'
          % (en_ts['status'], en_ts.get('reason')))
    en_r = lookup('R.', '2,91,26', lang='en')
    check(en_r['status'] == 'miss' and en_r.get('reason') == 'en-translation-unpublished',
          'R. 2,91,26 lang=en -> %s/%s (RU-covered, EN not wired this pilot)'
          % (en_r['status'], en_r.get('reason')))
    # RU path unchanged for ṚV. (may be evidence_unavailable without corpus.db)
    ru_rv = lookup('ṚV.', '1,1,1', lang='ru')
    check(ru_rv.get('canonical_id') == '01_rigveda:1.1'
          and ru_rv['status'] in ('hit', 'evidence_unavailable', 'miss'),
          'ṚV. 1,1,1 lang=ru -> %s, canonical %s (RU path unchanged)'
          % (ru_rv['status'], ru_rv.get('canonical_id')))
    # Default lang remains ru (no kwarg)
    def_ru = lookup('TS.', '2,3,1,4')
    check(def_ru['status'] == 'miss' and def_ru.get('reason') == 'text-not-covered',
          'lookup default lang=ru still clean-misses TS.')

    print()
    if fails:
        sys.exit('%d selftest check(s) FAILED' % len(fails))
    print('citation_tm selftest: all checks green')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    lk = sub.add_parser('lookup')
    lk.add_argument('prefix')
    lk.add_argument('locus')
    lk.add_argument('--lang', default='ru',
                    help='ru (default) or en (ṚV. Griffith pilot, H2334)')
    sub.add_parser('selftest')
    args = ap.parse_args()
    if args.cmd == 'selftest':
        selftest()
    elif args.cmd == 'lookup':
        rec = lookup(args.prefix, args.locus, lang=args.lang)
        redacted = dict(rec)
        if redacted.get('ru'):
            redacted['ru'] = '<%d RU chars — metadata-only, not printed>' % len(rec['ru'])
        if redacted.get('en'):
            redacted['en'] = '<%d EN chars — not printed in CLI log>' % len(rec['en'])
        print(json.dumps(redacted, ensure_ascii=False, indent=1))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
