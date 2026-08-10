#!/usr/bin/env python
"""probe_key_scheme.py — why does koch x DCS join at only ~13%?

H2401: `probe_gold_strata.py` found only 3,775 of 29,006 standalone Kochergina
lemmas carry a DCS frequency signal from `dcs_freq_dims.json` (90,349 lemmas).
Before that number becomes a protocol assumption ("the frame is 3.7k"), find out
whether it is a real vocabulary gap or a transliteration-scheme mismatch: koch
keys are SLP1 (`ASrama`, `AKyA`), and if DCS keys are IAST (`āśrama`) the join is
silently discarding most of the overlap.

Read-only. Prints diagnostics only; writes nothing.

Usage: python probe_key_scheme.py --koch <koch.jsonl> --dcs <dcs_freq_dims.json>
"""
import argparse
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# SLP1 uses ASCII capitals for long vowels / retroflexes / sibilants.
SLP1_MARKERS = re.compile(r'[AIUFXEOTDNSRZKGJPBMHYVLCcqwWQ]')
IAST_MARKERS = re.compile(r'[āīūṛṝḷḹṅñṭḍṇśṣṃḥ]')
DEVA_MARKERS = re.compile(r'[ऀ-ॿ]')

# Minimal IAST -> SLP1 map, longest-first, for a join-recovery estimate only.
IAST_TO_SLP1 = [
    ('ā', 'A'), ('ī', 'I'), ('ū', 'U'), ('ṛ', 'f'), ('ṝ', 'F'),
    ('ḷ', 'x'), ('ḹ', 'X'), ('ai', 'E'), ('au', 'O'),
    ('ṅ', 'N'), ('ñ', 'Y'), ('ṭ', 'w'), ('ḍ', 'q'), ('ṇ', 'R'),
    ('ś', 'S'), ('ṣ', 'z'), ('ṃ', 'M'), ('ḥ', 'H'),
    ('kh', 'K'), ('gh', 'G'), ('ch', 'C'), ('jh', 'J'),
    ('ṭh', 'W'), ('ḍh', 'Q'), ('th', 'T'), ('dh', 'D'),
    ('ph', 'P'), ('bh', 'B'),
]


def iast_to_slp1(s):
    """Order matters: aspirates and diphthongs before single letters."""
    out = s
    for src, dst in sorted(IAST_TO_SLP1, key=lambda p: -len(p[0])):
        out = out.replace(src, dst)
    return out


def classify(keys):
    counts = {'slp1_like': 0, 'iast_diacritic': 0, 'devanagari': 0, 'plain_ascii': 0}
    for k in keys:
        if DEVA_MARKERS.search(k):
            counts['devanagari'] += 1
        elif IAST_MARKERS.search(k):
            counts['iast_diacritic'] += 1
        elif SLP1_MARKERS.search(k):
            counts['slp1_like'] += 1
        else:
            counts['plain_ascii'] += 1
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--koch', required=True)
    ap.add_argument('--dcs', required=True)
    args = ap.parse_args()

    with open(args.dcs, encoding='utf-8-sig') as f:
        dcs = json.load(f)
    dcs_keys = list((dcs.get('by_lemma') or dcs).keys())

    koch_keys = []
    with open(args.koch, encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            k = rec.get('slp1') or rec.get('key') or rec.get('lemma')
            if isinstance(k, str) and k and not k.startswith('-'):
                koch_keys.append(k)

    print('koch keys           :', len(koch_keys), classify(koch_keys[:5000]))
    print('koch sample         :', koch_keys[:8])
    print('dcs keys            :', len(dcs_keys), classify(dcs_keys[:5000]))
    print('dcs sample          :', dcs_keys[:8])

    koch_set, dcs_set = set(koch_keys), set(dcs_keys)
    direct = koch_set & dcs_set
    print('direct join         :', len(direct))

    # If DCS is IAST, converting it to SLP1 should raise the join materially.
    converted = {iast_to_slp1(k) for k in dcs_set}
    via_iast = koch_set & converted
    print('join after IAST->SLP1 of DCS keys:', len(via_iast),
          '(delta %+d)' % (len(via_iast) - len(direct)))

    # And the reverse direction, case-insensitively, as a crude sanity bound.
    lower_join = {k.lower() for k in koch_set} & {k.lower() for k in dcs_set}
    print('case-folded join    :', len(lower_join))

    only_koch = sorted(koch_set - dcs_set)[:10]
    print('koch-only sample    :', only_koch)
    return 0


if __name__ == '__main__':
    sys.exit(main())
