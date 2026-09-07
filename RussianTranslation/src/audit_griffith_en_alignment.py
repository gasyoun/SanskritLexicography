#!/usr/bin/env python
r"""Audit the Griffith 1896 EN of-record against the Sanskrit at the SAME key (H2361).

`citation_tm.lookup(prefix, locus, lang='en')` (H2334) assumes the Griffith JSON
`location` key `m.s.v` addresses the same stanza as the corpus `canonical_id`
`%02d_rigveda:s.v` — i.e. that the only difference is the zero-pad on the
mandala. That assumption is unit-pinned at 1.1.1 and 10.90.1 only, and it is
FALSE for RV mandala 8 from sūkta 49 on (the vālakhilya block), where the EN
column of `pwg_ru/griffith_en_1896.json` is offset against its own key.

The check is language-independent: a stanza whose SANSKRIT opens with a deity
stem (agni-, indra-, soma-, …) should carry that deity's name in Griffith's
English at the SAME location. Agreement runs ~94% on aligned material (the
residue is ordinary translation looseness) and collapses where the columns
drift, so the rate localises the damage without anyone reading 10,552 stanzas.

Needs the corpus DB for the Sanskrit side (`SAMUDRA_CORPUS_DB`, default
`SamudraManthanam/web/corpus.db`); exits 0 with a SKIP when it is absent. CI
does not check out the ~600 MB real corpus.db (separate repo) -- it points
`SAMUDRA_CORPUS_DB` at `RussianTranslation/tests/fixtures/rigveda_sa_fixture.db`
instead, a committed, unmodified copy of just the Rigveda `#sa` rows (~4.6 MB,
H3949 07-09-2026) that reproduces the real DB's numbers exactly, so the gate
actually executes in CI rather than permanently SKIPping.

  python src/audit_griffith_en_alignment.py            # per-mandala report
  python src/audit_griffith_en_alignment.py --selftest # gate: exit 1 on a NEW broken block

H3949 (07-09-2026) wired this into CI. 8.49-8.103 (and the derived full-mandala-8
row) stay broken and are GRANDFATHERED by name and date in `GRANDFATHERED` below
rather than silently passed: repair attempts found the drift is NOT a constant
vālakhilya-sized (11-hymn) offset -- Griffith's published hymn boundaries diverge
from the critical/PWG numbering hymn-by-hymn across the whole 49-92 stretch of his
own numbering, so a blind rekey would relabel most stanzas with the wrong content.
The gate still fails hard on any block outside the grandfathered list.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from sibling_root import sibling_root  # noqa: E402

GITHUB = sibling_root(HERE)
CORPUS_DB = os.environ.get(
    'SAMUDRA_CORPUS_DB', os.path.join(GITHUB, 'SamudraManthanam', 'web', 'corpus.db'))
GRIFFITH_EN_JSON = os.path.join(os.path.dirname(HERE), 'pwg_ru', 'griffith_en_1896.json')

# (Sanskrit stem regex, English name regex). First match wins, so the order is
# the order of anchor strength, not frequency.
ANCHORS = [
    (r'agn', r'agni'),
    (r'indr', r'indra'),
    (r'som', r'soma'),
    (r'varuṇ', r'varuna'),
    (r'marut', r'marut'),
    (r'uṣas|uṣo', r'dawn|usas'),
    (r'mitr', r'mitra'),
    (r'sūry|surya', r'surya|sun'),
]

# Agreement below this on a block of ≥100 anchored stanzas means the EN column
# is not addressing the same stanzas as the key. Aligned material sits ~90-96%.
FLOOR = 0.70

# H3949, 07-09-2026: investigated re-keying mandala 8 sukta >=49 by the constant
# vālakhilya offset (11 hymns). That constant shift is FALSE beyond the first few
# hymns: checked hymn-by-hymn against corpus.db verse counts, only 13 of the 44
# hymns in Griffith's own 49-92 range land on the same verse count as the
# corpus hymn a constant +11 shift predicts (e.g. Griffith 81 has 9 verses,
# corpus 92 -- the shift target -- has 33; Griffith's published hymn boundaries
# diverge from the critical/PWG numbering throughout this stretch, not only at
# the vālakhilya insertion). Re-keying on the constant shift would relabel most
# of the block with the WRONG stanza, which the ambiguity policy rules out ("a
# wrong alignment is worse than a declared gap"). Grandfathered until someone
# does the hymn-by-hymn philological correspondence work; the gate still fails
# on any block outside this named, dated list.
GRANDFATHERED = {
    'mandala 8': 'H3949 07-09-2026: sukta 49-103 hymn-boundary drift is not a '
                 'constant offset, see  8.49-8.103 below',
    '  8.49-8.103': 'H3949 07-09-2026: Griffith hymn numbering diverges from the '
                     'critical/PWG numbering across this whole stretch (verified '
                     'not a constant vālakhilya-sized shift); no reliable EN '
                     'stanza mapping exists yet, left unaligned per the '
                     'ambiguity policy rather than guessed',
}


def load_en():
    """location `m.s.v` -> Griffith English."""
    with open(GRIFFITH_EN_JSON, encoding='utf-8') as fh:
        data = json.load(fh)
    contents = data.get('contents') if isinstance(data, dict) else data
    return {r['location']: r['text'] for r in (contents or [])
            if r.get('location') and r.get('text')}


def load_sa():
    """Same key shape, from the corpus `#sa` lines. Empty dict if the DB is absent."""
    if not os.path.exists(CORPUS_DB):
        return {}
    con = sqlite3.connect('file:%s?mode=ro' % CORPUS_DB, uri=True)
    try:
        out = {}
        for cid, txt in con.execute(
                "SELECT canonical_id, line_text FROM corpus_lines "
                "WHERE canonical_id LIKE '%_rigveda:%#sa'"):
            work, rest = cid.split(':')
            out['%d.%s' % (int(work.split('_')[0]), rest[:-3])] = txt
        return out
    finally:
        con.close()


def agreement(en, sa, keep=lambda m, s: True):
    """(agreed, anchored, [(loc, expected_en_name) …]) over the kept stanzas."""
    agreed = anchored = 0
    misses = []
    for loc, s_txt in sa.items():
        parts = loc.split('.')
        if len(parts) != 3:
            continue
        m, s = int(parts[0]), int(parts[1])
        if not keep(m, s):
            continue
        e_txt = en.get(loc)
        if not e_txt:
            continue
        low_s, low_e = s_txt.lower(), e_txt.lower()
        for stem, name in ANCHORS:
            if re.search(r'(^|\s)' + stem, low_s):
                anchored += 1
                if re.search(name, low_e):
                    agreed += 1
                elif len(misses) < 6:
                    misses.append((loc, name))
                break
    return agreed, anchored, misses


def report(en, sa):
    rows = []
    for m in range(1, 11):
        a, n, _ = agreement(en, sa, lambda mm, _s, m=m: mm == m)
        rows.append((('mandala %d' % m), a, n))
    for lo, hi in ((1, 48), (49, 103)):
        a, n, _ = agreement(
            en, sa, lambda mm, ss, lo=lo, hi=hi: mm == 8 and lo <= ss <= hi)
        rows.append(('  8.%d-8.%d' % (lo, hi), a, n))
    print('block          agreed/anchored    rate')
    for label, a, n in rows:
        print('%-14s %6d/%-6d %9s' % (label, a, n, '%.1f%%' % (100.0 * a / n) if n else 'n/a'))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--selftest', action='store_true',
                    help='exit 1 if any anchored block of >=100 stanzas falls below the floor')
    args = ap.parse_args()

    if not os.path.exists(GRIFFITH_EN_JSON):
        print('SKIP: %s absent' % GRIFFITH_EN_JSON)
        return
    sa = load_sa()
    if not sa:
        print('SKIP: corpus.db absent (%s) — the Sanskrit side of the check is unavailable'
              % CORPUS_DB)
        return
    en = load_en()
    print('Griffith EN stanzas: %d   corpus SA stanzas: %d\n' % (len(en), len(sa)))
    rows = report(en, sa)

    if not args.selftest:
        return
    below_floor = [(label, a, n) for label, a, n in rows
                   if n >= 100 and (a / float(n)) < FLOOR]
    bad = [row for row in below_floor if row[0] not in GRANDFATHERED]
    grandfathered_hits = [row for row in below_floor if row[0] in GRANDFATHERED]
    print()
    for label, a, n in grandfathered_hits:
        print('GRANDFATHERED %s: %d/%d = %.1f%% < %.0f%% floor — %s'
              % (label, a, n, 100.0 * a / n, 100 * FLOOR, GRANDFATHERED[label]))
    if bad:
        for label, a, n in bad:
            print('FAIL %s: %d/%d = %.1f%% < %.0f%% floor — the EN column does not address '
                  'the stanzas its own key names' % (label, a, n, 100.0 * a / n, 100 * FLOOR))
        sys.exit('%d block(s) below the alignment floor (H2361)' % len(bad))
    if grandfathered_hits:
        print('alignment gate: no anchored block below the %.0f%% floor outside the '
              'grandfathered list (H3949)' % (100 * FLOOR))
    else:
        print('alignment gate: no anchored block below the %.0f%% floor' % (100 * FLOOR))


if __name__ == '__main__':
    main()
