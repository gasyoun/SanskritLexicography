#!/usr/bin/env python
r"""Citation translation-memory lookup — reuse an existing Russian translation of
record for a PWG `<ls>` source citation instead of re-translating it (H1304).

MG's ask (H178 vote N1/N6/N9/N11/N18): whenever a PWG card cites a passage of a
text that ALREADY has a published/aligned Russian translation (R., MBH., ṚV.,
KATHĀS., …), the card's citation rendering must **reuse that translation** — for
every covered text, everywhere. This module is the lookup that makes that
possible: `lookup(prefix, locus)` maps a PWG citation to a corpus passage and
returns its Russian translation-of-record segment, or a clean/typed miss.

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
                              (e.g. Rāmāyaṇa kiṣkindhā/yuddha kāṇḍas — absent).
        'locus-parse-failed'  the citation locus didn't parse.
  'unmapped_locus_scheme'— the text is covered but its PWG citation scheme does
                           NOT map 1:1 to the corpus keying, so no lookup is
                           possible without an external concordance. The two
                           documented cases: MBH. (PWG cites continuous Calcutta
                           ślokas; corpus keys critical parvan.adhyaya.verse) and
                           R. GORR. (Gorresio Bengal recension ≠ Leonov Southern).
                           NOT a miss — a GAP awaiting a concordance (see the doc).
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
import os
import re
import sqlite3
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
GITHUB = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
CORPUS_DB = os.environ.get(
    'SAMUDRA_CORPUS_DB', os.path.join(GITHUB, 'SamudraManthanam', 'web', 'corpus.db'))

# Sentinel returned by a resolver when the text is covered but its citation scheme
# cannot map to the corpus keying (needs an external concordance).
UNMAPPED = object()

# --- per-text locus resolvers ------------------------------------------------
# Each maps a PWG citation locus (comma-separated coordinate string) to a corpus
# `canonical_id` passage (without the #ru/#sa suffix), per COVERED_TEXTS_RU.md.
# Return None on a parse failure; return UNMAPPED for a documented scheme gap.

_RAMA_KANDA = {  # PWG book number -> corpus kāṇḍa file (04 kiṣkindhā / 06 yuddha absent)
    1: '01_ramayana-balakanda', 2: '02_ramayana-ayodhyakanda',
    3: '03_ramayana-aranyakanda', 5: '05_ramayana-sundarakanda',
}


def _nums(locus):
    return [int(x) for x in re.findall(r'\d+', locus or '')]


def _rama(locus):
    n = _nums(locus)
    if len(n) != 3:
        return None
    book, sarga, verse = n
    work = _RAMA_KANDA.get(book)
    if work is None:  # kiṣkindhā (4) / yuddha (6) not ingested -> covered-but-absent
        return ('__ramayana_absent_kanda__', book)
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
    # No 1:1 map without a Calcutta<->critical concordance (see the doc GAP + @DECIDE).
    return UNMAPPED


def _rama_gorresio_unmapped(locus):
    # Gorresio Gauḍīya/Bengal recension != Leonov Southern (only ~1/3 verse-for-verse;
    # no published concordance). Documented GAP + @DECIDE.
    return UNMAPPED


# PWG abbreviation (normalized, trailing dot/space-insensitive) -> (resolver, meta).
# meta: (text, translator/source, rights_flag). Only texts with an RU asset appear;
# anything not here is 'text-not-covered' (a clean miss: TS., SUŚR., HARIV., ŚAT. BR.).
RESOLVERS = {
    'R.':        (_rama,      ('Rāmāyaṇa (Southern)', 'Leonov', 'metadata-only')),
    'R. GORR.':  (_rama_gorresio_unmapped, ('Rāmāyaṇa (Gauḍīya, Gorresio)', '—', 'metadata-only')),
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


def lookup(prefix, locus):
    """Resolve a PWG `<ls>` citation to its Russian translation of record.

    Returns a dict: status, prefix, locus, canonical_id, text, source, rights_flag,
    reason (on miss), and `ru` (ONLY populated for a hit; generation-time consult
    only — never persist it to a committed/public artifact)."""
    p = _norm_prefix(prefix)
    entry = RESOLVERS.get(p)
    base = {'prefix': p, 'locus': locus, 'canonical_id': None, 'ru': None}
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
    if isinstance(resolved, tuple) and resolved[0] == '__ramayana_absent_kanda__':
        return {**base, 'status': 'miss', 'reason': 'locus-not-in-corpus',
                'canonical_id': None}
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


def consult_card(*fields):
    """Generation-time consult: given a card's DE/RU/EN text field(s) carrying
    `<ls>` citations, return one lookup() record per DISTINCT citation whose text
    is covered by an RU translation of record. Intended to be called where
    corpus_gate.build_card() assembles the LLM verdict input, so a covered
    citation surfaces its RU rendering to the translator model instead of being
    retranslated. Uncovered citations are omitted (a clean miss needs no consult)."""
    seen, out = set(), []
    for fld in fields:
        for m in _LS.finditer(fld or ''):
            nm = _N_ATTR.search(m.group(1) or '')
            parsed = _split_citation(nm.group(1) if nm else None, (m.group(2) or '').strip())
            if not parsed:
                continue
            key = parsed
            if key in seen:
                continue
            seen.add(key)
            rec = lookup(*parsed)
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
    check(gorr['status'] == 'unmapped_locus_scheme',
          'R. GORR. 2,5,27 -> %s (Gorresio Bengal GAP, N11)' % gorr['status'])

    print('LIVE corpus checks (DB-gated):')
    if not os.path.exists(CORPUS_DB):
        print('  skip  corpus.db absent (%s) — live-hit checks skipped, not failed' % CORPUS_DB)
    else:
        r2 = lookup('R.', '2,91,26')
        check(r2['status'] == 'hit' and r2['ru'],
              'R. 2,91,26 -> hit, RU %d chars (N1)' % (len(r2['ru']) if r2['ru'] else 0))
        m = lookup('M.', '1,1')
        check(m['status'] == 'hit' and m['ru'], 'M. 1,1 -> hit, RU %d chars' % (len(m['ru']) if m['ru'] else 0))

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
    sub.add_parser('selftest')
    args = ap.parse_args()
    if args.cmd == 'selftest':
        selftest()
    elif args.cmd == 'lookup':
        rec = lookup(args.prefix, args.locus)
        redacted = dict(rec)
        if redacted.get('ru'):
            redacted['ru'] = '<%d RU chars — metadata-only, not printed>' % len(rec['ru'])
        import json
        print(json.dumps(redacted, ensure_ascii=False, indent=1))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
