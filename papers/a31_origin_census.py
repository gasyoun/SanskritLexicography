#!/usr/bin/env python3
"""A31 origin-axis census over the OBS-T correction-event corpus.

Consumes the released OBS-T corpus (csl-observatory,
observatory/site/src/data/correction_events_release.csv, 52,498 events) and
attributes each correction event to the production-chain ORIGIN of the error it
repairs — a third axis on top of OBS-T's location x edit-type design, never a
replacement for it (A31 <-> A12 schema alignment).

Origin classes (output column `origin_class`):
  print-source        error present in the printed dictionary itself
  digitization        error introduced at transcription/keyboarding/OCR
                      (subtypes carried by origin_rule: typo/ocr/scan/coding)
  conversion-markup   error in the project's own tag/id layer (no print analog)
  undetermined        no explicit evidence; NEVER guessed (Renou-classifier lesson:
                      unanchored heuristics produced >=7.1% wrong classes)

An editorial-variant class was considered and dropped: the only candidate
evidence (89 form events noted 'variant') sits under the corrector's own 'typo'
type token, so no anchored rule separates editorial intent from a transcription
slip — recorded in the paper's limitations, not guessed here.

Rules are anchored: comment-evidence rules match word-bounded tokens in the
correction-form free text (`comment_raw`, form layer only, where the corrector
states the error's genesis); one structural rule uses the fact that the markup/
meta layer does not exist in the printed book. Every classified row carries the
`origin_rule` id that fired. Git-layer commit messages are generic and are NOT
used as origin evidence.

Outputs (papers/a31/):
  a31_origin_census.csv             origin distribution, overall and by layer
  a31_origin_by_dict.csv            origin x dictionary (>=30 origin-classified events)
  a31_origin_by_edit_type.csv       origin x OBS-T edit-type axis
  a31_origin_rules.csv              per-rule fire counts (provenance)
  a31_origin_validation_sample.csv  stratified sample for the hand-check
                                    (`judged_origin` column to be filled by a
                                    human/agent reading full evidence)

Run:  python papers/a31_origin_census.py  (data path auto-discovered from the
sibling csl-observatory clone; override with --data)
"""

import argparse
import csv
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = (REPO_ROOT.parent / 'csl-observatory' / 'observatory' / 'site'
                / 'src' / 'data' / 'correction_events_release.csv')
OUT_DIR = REPO_ROOT / 'papers' / 'a31'

# ---------------------------------------------------------------------------
# Anchored origin rules. Order matters: first match wins. Each rule is
# (rule_id, origin_class, compiled word-bounded regex over the lowercased
# comment). Comment evidence is only trusted on the form layer, where
# comment_raw is the corrector's own per-event description.
# ---------------------------------------------------------------------------
COMMENT_RULES = [
    # -- print-source: the corrector states the printed book is wrong --------
    ('c_print_error', 'print-source',
     re.compile(r'\b(?:print(?:ing)? error|misprint(?:ed|s)?|error in (?:the )?print)\b')),
    ('c_print_missing', 'print-source',
     re.compile(r'\bprint (?:partially )?(?:missing|unclear|blurr?ed|damaged)\b')),
    # -- digitization: transcription slip, OCR, or scan misreading -----------
    ('c_ocr', 'digitization',
     re.compile(r'\bocr\b')),
    ('c_scan', 'digitization',
     re.compile(r'\b(?:scan(?:ning)? error|poor scan|bad scan)\b')),
    ('c_typo', 'digitization',
     re.compile(r'^typo\b')),
    ('c_coding', 'digitization',
     re.compile(r'^coding\b')),
    # -- conversion-markup: the corrector names the tag/markup layer ---------
    ('c_markup', 'conversion-markup',
     re.compile(r'^markup\b|\bmarkup error\b')),
]

# Structural rule (any layer): the markup/meta layer is created by the
# digitization project; a printed dictionary has no <tags> or record ids, so an
# error whose OBS-T location is markup or meta originated in the project's own
# conversion/tagging layer. Applied only on derived (join-backed) locations.
STRUCTURAL_COMPONENTS = {'markup': 's_markup', 'meta': 's_meta'}

ORIGIN_CLASSES = ['print-source', 'digitization', 'conversion-markup',
                  'undetermined']


def classify(row):
    """Return (origin_class, rule_id) for one OBS-T event row."""
    comment = (row.get('comment_raw') or '').strip().lower()
    if row.get('source_layer') == 'form' and comment:
        # print-source evidence outranks the leading 'typo' token: many form
        # comments read 'typo  print error ...' where the second clause is the
        # substantive judgment.
        for rule_id, origin, rx in COMMENT_RULES:
            if origin == 'print-source' and rx.search(comment):
                return origin, rule_id
        for rule_id, origin, rx in COMMENT_RULES:
            if rx.search(comment):
                return origin, rule_id
    if (row.get('evidence_level') == 'derived'
            and row.get('error_component') in STRUCTURAL_COMPONENTS):
        return 'conversion-markup', STRUCTURAL_COMPONENTS[row['error_component']]
    return 'undetermined', ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', type=Path, default=DEFAULT_DATA)
    ap.add_argument('--sample-per-class', type=int, default=30)
    ap.add_argument('--seed', type=int, default=1074)
    args = ap.parse_args()

    if not args.data.is_file():
        sys.exit(f'OBS-T release CSV not found: {args.data} '
                 '(clone csl-observatory as a sibling repo or pass --data)')

    csv.field_size_limit(10_000_000)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    totals = Counter()
    by_layer = Counter()
    by_dict = Counter()
    dict_events = Counter()
    by_edit = Counter()
    rules = Counter()
    ps_corrector = defaultdict(Counter)   # dict -> corrector counts, print-source rows
    pool = defaultdict(list)      # origin -> reservoir of sample candidates
    rng = random.Random(args.seed)
    n = 0

    sample_fields = ['event_id', 'source_layer', 'dict', 'headword_iast',
                     'old_iast', 'new_iast', 'comment_raw', 'error_component',
                     'edit_type', 'origin_class', 'origin_rule']

    with open(args.data, encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            n += 1
            origin, rule = classify(row)
            totals[origin] += 1
            by_layer[(row['source_layer'], origin)] += 1
            by_dict[(row['dict'], origin)] += 1
            dict_events[row['dict']] += 1
            by_edit[(row['edit_type'], origin)] += 1
            if rule:
                rules[rule] += 1
            if origin == 'print-source':
                ps_corrector[row['dict']][row.get('corrector_name') or '?'] += 1
            # reservoir sample per class
            bucket = pool[origin]
            keep = {k: (row.get(k) or '')[:300] for k in sample_fields[:-2]}
            keep['origin_class'] = origin
            keep['origin_rule'] = rule
            if len(bucket) < args.sample_per_class:
                bucket.append(keep)
            else:
                j = rng.randrange(totals[origin])
                if j < args.sample_per_class:
                    bucket[j] = keep

    # -- census: overall + per layer ----------------------------------------
    with open(OUT_DIR / 'a31_origin_census.csv', 'w', encoding='utf-8',
              newline='') as f:
        w = csv.writer(f)
        w.writerow(['scope', 'origin_class', 'events', 'share_pct'])
        for origin in ORIGIN_CLASSES:
            w.writerow(['all', origin, totals[origin],
                        f'{100.0 * totals[origin] / n:.1f}'])
        for layer in ('form', 'git'):
            layer_n = sum(v for (l, _), v in by_layer.items() if l == layer)
            for origin in ORIGIN_CLASSES:
                v = by_layer[(layer, origin)]
                w.writerow([layer, origin, v,
                            f'{100.0 * v / layer_n:.1f}' if layer_n else '0.0'])

    # -- origin x dictionary (dicts with >=30 origin-classified events) ------
    with open(OUT_DIR / 'a31_origin_by_dict.csv', 'w', encoding='utf-8',
              newline='') as f:
        w = csv.writer(f)
        w.writerow(['dict', 'events_total', 'origin_classified',
                    'print_source', 'digitization', 'conversion_markup',
                    'print_source_share_of_classified_pct',
                    'top_corrector_share_of_print_source_pct'])
        for d in sorted(dict_events, key=dict_events.get, reverse=True):
            cls = {o: by_dict[(d, o)] for o in ORIGIN_CLASSES}
            classified = sum(v for o, v in cls.items() if o != 'undetermined')
            if classified < 30:
                continue
            ps = cls['print-source']
            top_c = (max(ps_corrector[d].values()) if ps_corrector[d] else 0)
            w.writerow([d, dict_events[d], classified, ps,
                        cls['digitization'], cls['conversion-markup'],
                        f'{100.0 * ps / classified:.1f}',
                        f'{100.0 * top_c / ps:.1f}' if ps else ''])

    # -- origin x edit-type ---------------------------------------------------
    edit_types = sorted({e for (e, _) in by_edit})
    with open(OUT_DIR / 'a31_origin_by_edit_type.csv', 'w', encoding='utf-8',
              newline='') as f:
        w = csv.writer(f)
        w.writerow(['edit_type'] + ORIGIN_CLASSES)
        for e in edit_types:
            w.writerow([e] + [by_edit[(e, o)] for o in ORIGIN_CLASSES])

    # -- rule provenance ------------------------------------------------------
    with open(OUT_DIR / 'a31_origin_rules.csv', 'w', encoding='utf-8',
              newline='') as f:
        w = csv.writer(f)
        w.writerow(['origin_rule', 'origin_class', 'events'])
        rule_class = {rid: oc for rid, oc, _ in COMMENT_RULES}
        rule_class.update({'s_markup': 'conversion-markup',
                           's_meta': 'conversion-markup'})
        for rid, v in rules.most_common():
            w.writerow([rid, rule_class.get(rid, '?'), v])

    # -- stratified validation sample ----------------------------------------
    with open(OUT_DIR / 'a31_origin_validation_sample.csv', 'w',
              encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['row_id'] + sample_fields
                           + ['judged_origin', 'judge_notes'])
        w.writeheader()
        rid = 0
        for origin in ORIGIN_CLASSES:
            for item in pool[origin]:
                rid += 1
                item.update(row_id=rid, judged_origin='', judge_notes='')
                w.writerow(item)

    print(f'events: {n}')
    for origin in ORIGIN_CLASSES:
        print(f'  {origin:20s} {totals[origin]:6d}  '
              f'{100.0 * totals[origin] / n:5.1f}%')
    print(f'rules fired: {dict(rules.most_common())}')
    print(f'outputs -> {OUT_DIR}')


if __name__ == '__main__':
    main()
