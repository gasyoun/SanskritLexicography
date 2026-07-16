#!/usr/bin/env python3
"""Fill the A31 origin-axis validation sample with the annotator's judgments
and compute per-class precision (papers/a31/a31_origin_validation_metrics.csv).

Annotator of record for this pass: Fable 5 (claude-fable-5), 17-07-2026,
single-annotator — reading each row's full evidence (old/new strings, the
corrector's comment, the OBS-T location and edit-type). A second human
annotator is the standing org gate (same recruit as the A12 gold pass).
"""

import csv
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
SAMPLE = HERE / 'a31_origin_validation_sample.csv'
METRICS = HERE / 'a31_origin_validation_metrics.csv'

# row_id -> (judged_origin, note). Rows not listed: judgment agrees with the
# rule label and the evidence is unambiguous.
DISAGREE = {
    17: ('editorial-normalization',
         "comment says 'print error' but substance is 'reformat for "
         "consistency' — a citation-format normalization, not a print defect"),
    34: ('editorial-normalization',
         "adds 'ed.Calc.' for consistency — editorial normalization filed "
         "under the form's 'typo' token"),
    44: ('editorial-normalization',
         "'BOṃB' -> 'ed.Bomb.' citation-format normalization, not a typo"),
    71: ('digitization',
         'empty <lang n="greek"> filled with συμπαραβἀλλω — untranscribed '
         'print content, a transcription omission, not a tag-layer error'),
    72: ('editorial-addition',
         '<chg> block adds new bracketed content ([land-measure, Inscr.]) — '
         'an editorial supplement, not a conversion error'),
    87: ('unverifiable',
         'old == new in the shown evidence (edit_type none); nothing '
         'verifiable at row level'),
}

# undetermined rows where fuller evidence (the commit-message campaign) WOULD
# support a class — abstention misses, counted against abstention correctness,
# not against classified precision.
ABSTAIN_MISS = {
    94: ('conversion-markup', "adds <ab> tags — git-era markup-enrichment campaign"),
    99: ('conversion-markup', "[greek] placeholder -> <lang> tag — conversion-era artifact repair"),
    101: ('conversion-markup', "stray {{Lbody=...}} conversion artifact removed"),
    103: ('conversion-markup', "<ls> splitting campaign (VID link targets)"),
    104: ('conversion-markup', "<ls> splitting campaign (Spr. literary sources)"),
    105: ('conversion-markup', "{AV. m,h,v} link-markup campaign"),
    116: ('conversion-markup', "adds <ab>Ppr.</ab> — abbreviation-markup campaign"),
    117: ('conversion-markup', "<ls> splitting campaign (an. link targets)"),
    118: ('conversion-markup', "adds <listinfo n=\"sup\"/> — markup insertion"),
}

rows = list(csv.DictReader(open(SAMPLE, encoding='utf-8', newline='')))
for r in rows:
    rid = int(r['row_id'])
    if rid in DISAGREE:
        r['judged_origin'], r['judge_notes'] = DISAGREE[rid]
    elif rid in ABSTAIN_MISS:
        r['judged_origin'], r['judge_notes'] = ABSTAIN_MISS[rid]
    else:
        r['judged_origin'] = r['origin_class']
        r['judge_notes'] = 'agrees'

with open(SAMPLE, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

hit = Counter()
tot = Counter()
for r in rows:
    c = r['origin_class']
    tot[c] += 1
    if r['judged_origin'] == c:
        hit[c] += 1

with open(METRICS, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['origin_class', 'sample_n', 'judged_correct', 'precision',
                'annotator', 'date'])
    classified_hit = classified_tot = 0
    for c in ('print-source', 'digitization', 'conversion-markup'):
        w.writerow([c, tot[c], hit[c], f'{hit[c] / tot[c]:.3f}',
                    'Fable 5 (claude-fable-5), single-annotator', '17-07-2026'])
        classified_hit += hit[c]
        classified_tot += tot[c]
    w.writerow(['ALL-CLASSIFIED (micro)', classified_tot, classified_hit,
                f'{classified_hit / classified_tot:.3f}',
                'Fable 5 (claude-fable-5), single-annotator', '17-07-2026'])
    w.writerow(['undetermined (abstention correctness)', tot['undetermined'],
                hit['undetermined'],
                f'{hit["undetermined"] / tot["undetermined"]:.3f}',
                'Fable 5 (claude-fable-5), single-annotator', '17-07-2026'])

print('per-class precision:')
for c in tot:
    print(f'  {c:20s} {hit[c]}/{tot[c]} = {hit[c] / tot[c]:.3f}')
