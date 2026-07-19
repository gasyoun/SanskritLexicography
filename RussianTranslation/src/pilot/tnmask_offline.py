#!/usr/bin/env python
r"""Offline reader for the H1226 pre-restore {Tn} pairing persisted on promoted store rows.

Background (H1150 -> H1226). TNMASK's real check, in gen_opt_harness2.py `accept()` BEFORE
`restoreCard`, compares the pre-restore candidate's {Tn} multiset (`got`, `cardTokens(c)`) to
the masked source skeleton's (`want`, `tokensOf(INPUTS[k].skeleton)`). It is SOFT
(TNMASK_HARD_REJECT=false): a mismatch is kept as telemetry, not rejected. The promoted store
used to keep only POST-restore text, so that pairing was dropped on every card and the
false-flag rate could not be recomputed offline -- H1150 returned DO_NOT_ARM on denominator 1.

H1226 stamps the pairing onto each promoted row's provenance as
`row['provenance']['tnmask'] = {'got': '<sorted candidate multiset>', 'want': '<sorted skeleton
multiset>'}` (braces stripped: 'T1 T2', never '{T1} {T2}', so it never reads as a raw {Tn}
residue -- equality is preserved because the same bijection is applied to both sides). This
module is the READER: it applies the SAME equality `accept()` applies (`got != want`). The
multiset COMPUTATION already happened at accept() time and is persisted; nothing is recomputed
here (so this cannot drift from a hand-rolled re-implementation -- Uprava FINDINGS §82).

Only the main `accept()` path stamps the field; the heal path hard-rejects fragment {Tn}
mismatches (acceptFrag), so a healed/cached card carries no un-rejected expansion to measure and
simply has no `tnmask` -> reported as NOT MEASURABLE (honest), never as a clean 0.

  python src/pilot/tnmask_offline.py --store src/pwg_ru_translated.jsonl   # rate over the store
  python src/pilot/tnmask_offline.py --selftest

A future H1150-style re-measurement computes the false-flag rate as #mismatch / #measurable over
promoted rows carrying the field, then hand-inspects each flag (expansion vs. benign reorder)
from the stored got/want before revisiting the DO_NOT_ARM verdict. This module never arms
anything; TNMASK_HARD_REJECT stays a human @DECIDE at the const.
"""
import argparse
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def tnmask_pairing(row):
    """Return (got, want) -- the persisted pre-restore {Tn} multisets -- or None when the row
    carries no well-formed pairing (a pre-H1226 promotion, or a passthrough/heal card that never
    stamped one). None means NOT MEASURABLE, deliberately distinct from a measured got==want."""
    prov = row.get('provenance') or {}
    tn = prov.get('tnmask')
    if not isinstance(tn, dict):
        return None
    got, want = tn.get('got'), tn.get('want')
    if not isinstance(got, str) or not isinstance(want, str):
        return None
    return got, want


def tnmask_measurable(row):
    """True iff this promoted row carries the pairing a TNMASK measurement can read."""
    return tnmask_pairing(row) is not None


def tnmask_mismatch(row):
    """The offline TNMASK verdict for one promoted row:
      - True  : candidate multiset != skeleton multiset (a flag: a dropped/expanded {Tn});
      - False : the multisets match (clean);
      - None  : not measurable (no persisted pairing).
    This is exactly the equality accept() applies (`tok !== want`), read off the store."""
    pair = tnmask_pairing(row)
    if pair is None:
        return None
    got, want = pair
    return got != want


def rate_over_rows(rows):
    """Aggregate the offline TNMASK signal over an iterable of promoted rows.

    Returns a dict: total rows, measurable (carry the pairing), mismatches (flags among the
    measurable), and the flag rate over the measurable denominator (None when nothing is
    measurable yet -- the honest H1150 state, not a fabricated 0/0=0)."""
    total = measurable = mismatches = 0
    for row in rows:
        total += 1
        verdict = tnmask_mismatch(row)
        if verdict is None:
            continue
        measurable += 1
        if verdict:
            mismatches += 1
    rate = (mismatches / measurable) if measurable else None
    return {'total': total, 'measurable': measurable, 'mismatches': mismatches,
            'flag_rate_over_measurable': rate}


def _iter_store(path):
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def selftest():
    # GREEN: a promoted row carrying an expansion pairing (candidate short one {Tn}) is flagged.
    expansion = {'ru': 'x', 'provenance': {'tnmask': {'got': 'T1', 'want': 'T1 T2'}}}
    assert tnmask_measurable(expansion) is True
    assert tnmask_mismatch(expansion) is True, 'an expansion (got != want) must be detected'
    # clean: got == want -> measurable, not a flag.
    clean = {'ru': 'x', 'provenance': {'tnmask': {'got': 'T1 T2', 'want': 'T1 T2'}}}
    assert tnmask_mismatch(clean) is False
    # empty multisets are a legitimate clean, measurable pairing (a card with no masked spans).
    empty = {'ru': 'x', 'provenance': {'tnmask': {'got': '', 'want': ''}}}
    assert tnmask_measurable(empty) is True and tnmask_mismatch(empty) is False
    # RED: an otherwise-identical row WITHOUT the field is NOT measurable (the pre-H1226 state)
    # -- the same expansion is invisible, which is exactly what H1226 makes measurable.
    no_field = {'ru': 'x', 'provenance': {'model': 'sonnet'}}
    assert tnmask_pairing(no_field) is None
    assert tnmask_measurable(no_field) is False
    assert tnmask_mismatch(no_field) is None, 'no field -> not measurable, never a silent clean 0'
    # malformed pairings are treated as not measurable, never crash.
    for bad in ({'provenance': {'tnmask': {'got': 'T1'}}},           # missing want
                {'provenance': {'tnmask': {'got': 1, 'want': 2}}},   # non-string
                {'provenance': {'tnmask': 'T1 T2'}},                 # not a dict
                {'provenance': {}}, {}):
        assert tnmask_mismatch(bad) is None
    # aggregate: 2 measurable of 3 rows, 1 flag -> rate 0.5; a no-field-only set -> rate None.
    agg = rate_over_rows([expansion, clean, no_field])
    assert agg == {'total': 3, 'measurable': 2, 'mismatches': 1,
                   'flag_rate_over_measurable': 0.5}, agg
    assert rate_over_rows([no_field])['flag_rate_over_measurable'] is None
    print('tnmask_offline selftest OK '
          '(green: expansion flagged; red: no field -> not measurable, not a silent clean)')
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--store', help='promoted store jsonl to aggregate the TNMASK signal over')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    if not args.store:
        ap.error('pass --store <jsonl> or --selftest')
    agg = rate_over_rows(_iter_store(args.store))
    print(json.dumps(agg, ensure_ascii=False, indent=2))
    if not agg['measurable']:
        print('NOTE: 0 rows carry the H1226 {Tn} pairing yet — the store predates the field or no '
              'window has promoted since it landed. The rate is UNMEASURABLE (H1150 DO_NOT_ARM '
              'stands) until real windows accrue it; it is NOT 0.', file=sys.stderr)


if __name__ == '__main__':
    main()
