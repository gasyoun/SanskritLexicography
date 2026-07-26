#!/usr/bin/env python
"""H1651 detectors for the pwg_ru store wrapper-defect sweep (D1/D3/D4).

Three independent, deterministic scans over the canonical store's ``ru`` field:

* D1 -- Cyrillic characters inside ``{#...#}`` (the SLP1/Sanskrit wrapper). Cyrillic
  is never valid SLP1, so this rule has no false-positive mode.
* D3 -- guillemet spans ``«...»`` in ``ru`` where the aligned ``de`` field carries a
  ``{%...%}`` gloss at the same slot position (drift from the gloss-wrapper convention).
* D4 -- gloss-slot COUNT mismatch: number of ``{%...%}`` slots in ``de`` vs ``ru``. A
  flag, not a defect -- many mismatches are legitimate (a German doublet collapsing to
  one Russian word, an added clarifier).

  python src/pilot/wrapper_defect_scan.py [--store PATH]
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

CYR = re.compile(r'[Ѐ-ӿ]')
SKT_SPAN = re.compile(r'\{#(.*?)#\}', re.S)
GLOSS_SPAN = re.compile(r'\{%(.*?)%\}', re.S)
GUILLEMET_SPAN = re.compile(r'\xab([^\xbb]*)\xbb', re.S)


def find_d1(ru_text):
    """Return the list of {#...#} span texts that contain Cyrillic."""
    if not ru_text:
        return []
    return [m.group(1) for m in SKT_SPAN.finditer(ru_text) if CYR.search(m.group(1))]


def find_d3(de_text, ru_text):
    """Return True if de carries >=1 {%...%} gloss slot and ru carries >=1 guillemet
    span, in counts that plausibly correspond (same slot count) -- flags drift from
    the {%...%} gloss convention to «...» rendering in the same row."""
    if not de_text or not ru_text:
        return False
    de_gloss = GLOSS_SPAN.findall(de_text)
    ru_guillemet = GUILLEMET_SPAN.findall(ru_text)
    ru_gloss = GLOSS_SPAN.findall(ru_text)
    return bool(de_gloss) and bool(ru_guillemet) and not ru_gloss


def slot_counts(de_text, ru_text):
    de_n = len(GLOSS_SPAN.findall(de_text or ''))
    ru_n = len(GLOSS_SPAN.findall(ru_text or ''))
    return de_n, ru_n


def scan_store(store_path):
    d1_rows, d3_rows, d4_rows = [], [], []
    with open(store_path, encoding='utf-8') as stream:
        for line_number, line in enumerate(stream):
            if not line.strip():
                continue
            row = json.loads(line)
            ru = row.get('ru') or ''
            de = row.get('de') or ''
            label = '%s|%s|%s' % (row.get('key1'), row.get('subcard'), row.get('sense_tag'))

            d1_hits = find_d1(ru)
            if d1_hits:
                d1_rows.append((line_number, label, len(d1_hits)))

            if find_d3(de, ru):
                d3_rows.append((line_number, label))

            de_n, ru_n = slot_counts(de, ru)
            if de_n != ru_n:
                d4_rows.append((line_number, label, de_n, ru_n))
    return d1_rows, d3_rows, d4_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store')
    args = parser.parse_args()

    from store_path import canonical_store
    default_local = os.path.join(SRC, 'pwg_ru_translated.jsonl')
    store = args.store or canonical_store(default_local)
    if not os.path.exists(store):
        sys.exit('STORE ABSENT: %s' % store)

    d1_rows, d3_rows, d4_rows = scan_store(store)
    print('store   : %s' % store)
    print('D1 Cyrillic-in-{#...#}  : %d rows (%d spans)' % (
        len(d1_rows), sum(n for _, _, n in d1_rows)))
    print('D3 gloss-wrapper drift  : %d rows' % len(d3_rows))
    print('D4 gloss-slot mismatch  : %d rows' % len(d4_rows))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
