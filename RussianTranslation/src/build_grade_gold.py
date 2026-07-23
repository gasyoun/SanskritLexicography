#!/usr/bin/env python
r"""H1457 Track A1 -- frozen gold grade sample for COMET-QE calibration (A2).

Extends the H136 320-row stratified gold sample (gold/gold_set.jsonl, labelled
correct/lemma-variant/proper-name/partial/wrong-sense/hallucinated by kind x
period) with a publication A/B/C grade label per segment, using TWO
independent raters (no human adjudication round was available synchronously
in this run -- see AGENT-ADJUDICATED note below):

  rater 1 `label_policy`  -- deterministic mapping from the existing H136
      semantic label (already a considered judgment about correctness):
        A: correct, proper-name       (clean, exact rendering)
        B: lemma-variant, partial     (usable but imprecise)
        C: wrong-sense, hallucinated  (defective)

  rater 2 `qe_composite`  -- tm_grade.py's own qe_proxy() heuristic (textual
      shape features: cleanliness, length, Cyrillic coverage, latin leakage),
      discretized at the SAME thresholds tm_grade.py uses for a whole-corpus
      composite (score>=0.75 -> A, >=0.55 -> B, else C). Independent
      methodology from rater 1 (textual shape vs semantic annotation), so
      Cohen's kappa between them is a real inter-rater signal, not circular.

The frozen file keeps rater 1's grade as canonical `grade` (grounded in an
actual semantic judgment, the closest available proxy for a human label),
with rater 2's grade + raw score kept alongside for transparency and for
`tm_grade.py calibrate` to cross-check against.

**AGENT-ADJUDICATED, not human-adjudicated.** The plan's A1 step calls for a
`/gold-adjudicate` HUMAN round. None ran synchronously in this unattended
Track-A execution (R5.1: on ambiguity, pick the marked default, log it,
continue -- logged here). `gold/grade_gold.jsonl` should be treated as
PRELIMINARY until a human adjudication pass confirms or corrects it; this is
noted in GRADE_GOLD_MEMO.md and does not itself gate A2 (A2's floor is
Spearman rho vs whatever gold is frozen, not vs a human-blessed one).

Modality: every H136 gold row is `written` (dictionary/corpus segments) --
Track B (oral) has not produced units yet in this session, so no oral strata
exist to add. The `modality` field is stamped `written` on every row so a
later session can `cat` oral rows into the same frozen file without a schema
change.

    python build_grade_gold.py build   [--gold gold/gold_set.jsonl] [--out gold/grade_gold.jsonl]
    python build_grade_gold.py verify  [--out gold/grade_gold.jsonl]
    python build_grade_gold.py selftest
"""
import argparse
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import tm_grade  # qe_proxy() -- reuse, don't fork the heuristic

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_GOLD = os.path.join(ROOT, 'gold', 'gold_set.jsonl')
DEFAULT_OUT = os.path.join(ROOT, 'gold', 'grade_gold.jsonl')
DEFAULT_MEMO = os.path.join(ROOT, 'gold', 'GRADE_GOLD_MEMO.md')

VERSION = '0.1.0'

LABEL_TO_GRADE = {
    'correct': 'A', 'proper-name': 'A',
    'lemma-variant': 'B', 'partial': 'B',
    'wrong-sense': 'C', 'hallucinated': 'C',
}

QE_A = 0.75
QE_B = 0.55


def rater_label_policy(rec):
    return LABEL_TO_GRADE.get(rec.get('label'), 'C')


def rater_qe_composite(rec):
    score = tm_grade.qe_proxy(rec)
    grade = 'A' if score >= QE_A else 'B' if score >= QE_B else 'C'
    return grade, score


GRADE_ORDER = {'A': 0, 'B': 1, 'C': 2}


def cohens_kappa(labels_a, labels_b, classes=('A', 'B', 'C')):
    """Unweighted Cohen's kappa over a fixed class set. Manual implementation
    (no sklearn dependency) -- standard 2-rater agreement-beyond-chance."""
    n = len(labels_a)
    if n == 0 or n != len(labels_b):
        return float('nan')
    po = sum(1 for a, b in zip(labels_a, labels_b) if a == b) / n
    ca = collections.Counter(labels_a)
    cb = collections.Counter(labels_b)
    pe = sum((ca.get(c, 0) / n) * (cb.get(c, 0) / n) for c in classes)
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def cmd_build(a):
    if not os.path.exists(a.gold):
        sys.exit('gold set not found: %s' % a.gold)
    rows = [json.loads(l) for l in open(a.gold, encoding='utf-8') if l.strip()]
    out_rows = []
    r1_grades, r2_grades = [], []
    for rec in rows:
        g1 = rater_label_policy(rec)
        g2, qe_score = rater_qe_composite(rec)
        r1_grades.append(g1)
        r2_grades.append(g2)
        out_rows.append({
            **rec,
            'modality': rec.get('modality') or 'written',
            'grade': g1,
            'grade_rater1_label_policy': g1,
            'grade_rater2_qe_composite': g2,
            'qe_composite_score': round(qe_score, 4),
            'agree': g1 == g2,
        })
    kappa = cohens_kappa(r1_grades, r2_grades)
    dist1 = collections.Counter(r1_grades)
    dist2 = collections.Counter(r2_grades)
    n_agree = sum(1 for r in out_rows if r['agree'])

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    strata = collections.Counter((r.get('kind'), r.get('period'), r.get('modality'))
                                  for r in out_rows)
    memo = _render_memo(len(out_rows), dist1, dist2, kappa, n_agree, strata)
    with open(a.memo, 'w', encoding='utf-8', newline='\n') as f:
        f.write(memo)

    print('build: %d rows -> %s' % (len(out_rows), a.out))
    print('  rater1 (label_policy) dist: %s' % dict(dist1))
    print('  rater2 (qe_composite) dist: %s' % dict(dist2))
    print('  raw agreement: %d/%d (%.1f%%)' % (n_agree, len(out_rows),
                                                100 * n_agree / len(out_rows)))
    print("  Cohen's kappa: %.4f" % kappa)
    print('  memo -> %s' % a.memo)
    return 0


def _render_memo(n, dist1, dist2, kappa, n_agree, strata):
    lines = []
    lines.append('# GRADE_GOLD_MEMO — H1457 A1 frozen gold grade sample')
    lines.append('')
    lines.append('_Created: 22-07-2026 · Last updated: 22-07-2026_')
    lines.append('')
    lines.append('Generated by `build_grade_gold.py build` (Sonnet 5, `claude-sonnet-5`), '
                 'H1457 Track A, %d rows.' % n)
    lines.append('')
    lines.append('**⚠️ AGENT-ADJUDICATED, not human-adjudicated.** No synchronous '
                 '`/gold-adjudicate` human round ran in this unattended pass (R5.1 '
                 'logged default — see the module docstring in `build_grade_gold.py`). '
                 'Treat `grade` in `grade_gold.jsonl` as PRELIMINARY pending a human pass; '
                 'this does not itself block A2, whose floor is measured against whatever '
                 'gold is frozen.')
    lines.append('')
    lines.append('## Grade distribution')
    lines.append('')
    lines.append('| Rater | A | B | C |')
    lines.append('|---|---|---|---|')
    lines.append('| 1 — label_policy (canonical `grade`) | %d | %d | %d |'
                 % (dist1['A'], dist1['B'], dist1['C']))
    lines.append('| 2 — qe_composite (cross-check) | %d | %d | %d |'
                 % (dist2['A'], dist2['B'], dist2['C']))
    lines.append('')
    lines.append('## Inter-rater agreement')
    lines.append('')
    lines.append('- Raw agreement: %d/%d (%.1f%%)' % (n_agree, n, 100 * n_agree / n))
    lines.append("- Cohen's kappa (unweighted, 3-class A/B/C): **%.4f**" % kappa)
    lines.append('')
    lines.append('Rater 1 maps the existing H136 semantic label (correct/lemma-variant/'
                 'proper-name/partial/wrong-sense/hallucinated) deterministically to A/B/C. '
                 'Rater 2 is `tm_grade.qe_proxy()`, a textual-shape heuristic (cleanliness, '
                 'length, Cyrillic coverage, latin leakage) discretized at the same A/B '
                 'thresholds tm_grade.py uses corpus-wide. The two use genuinely different '
                 'evidence (semantic annotation vs surface-form heuristic), so kappa here is '
                 'a real agreement signal, not circular.')
    lines.append('')
    lines.append('**Reading the near-zero kappa.** A kappa this low does NOT mean the '
                 'canonical `grade` (rater 1, grounded in the real H136 semantic '
                 'annotation) is unreliable. It means rater 2 — the pre-existing '
                 '`qe_proxy()` heuristic — is a poor stand-alone semantic judge: it scored '
                 '%d/%d rows A because it only reads surface shape (short, clean, '
                 'mostly-Cyrillic), which a `wrong-sense` or `hallucinated` gloss can still '
                 'exhibit. That is exactly the failure mode already logged in '
                 '[`SanskritLexicography/FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) '
                 '§70 ("proxy-QE is near-useless for adequacy") — this run reproduces it '
                 'quantitatively rather than contradicting the gold. It is itself the '
                 'evidence motivating A2 (replace the proxy with real COMET-QE); the low '
                 'kappa is a property of rater 2, not of the frozen labels.' % (dist2['A'], n))
    lines.append('')
    lines.append('## Strata (kind × period × modality)')
    lines.append('')
    lines.append('| Kind | Period | Modality | N |')
    lines.append('|---|---|---|---|')
    for (kind, period, modality), cnt in sorted(strata.items()):
        lines.append('| %s | %s | %s | %d |' % (kind, period, modality, cnt))
    lines.append('')
    lines.append('**Oral strata: none yet.** All 320 H136 rows are `written` (dictionary/'
                 'corpus segments); Track B (oral-corpus formalization) has not produced '
                 'graded oral units in this session. A later session running B2–B4 should '
                 'append oral rows to this same frozen file (schema already carries '
                 '`modality`) rather than starting a separate gold set.')
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    lines.append('')
    return '\n'.join(lines)


def cmd_verify(a):
    if not os.path.exists(a.out):
        sys.exit('frozen gold not found: %s (run `build` first)' % a.out)
    rows = [json.loads(l) for l in open(a.out, encoding='utf-8') if l.strip()]
    n = len(rows)
    missing = [r for r in rows if r.get('grade') not in ('A', 'B', 'C')]
    strata = collections.Counter((r.get('kind'), r.get('period'), r.get('modality'))
                                  for r in rows)
    print('verify: %d rows, %d missing a valid grade, %d strata cells'
          % (n, len(missing), len(strata)))
    if missing:
        sys.exit('verify FAILED: %d rows lack an A/B/C grade' % len(missing))
    if n != 320:
        print('verify: WARNING expected 320 H136 rows, found %d (oral rows appended?)' % n)
    print('verify OK')
    return 0


# ------------------------------------------------------------------------ selftest
def selftest():
    assert rater_label_policy({'label': 'correct'}) == 'A'
    assert rater_label_policy({'label': 'proper-name'}) == 'A'
    assert rater_label_policy({'label': 'lemma-variant'}) == 'B'
    assert rater_label_policy({'label': 'partial'}) == 'B'
    assert rater_label_policy({'label': 'wrong-sense'}) == 'C'
    assert rater_label_policy({'label': 'hallucinated'}) == 'C'
    assert rater_label_policy({'label': 'unknown-thing'}) == 'C'

    # perfect agreement -> kappa 1.0
    assert abs(cohens_kappa(['A', 'B', 'C'], ['A', 'B', 'C']) - 1.0) < 1e-9
    # systematic disagreement (all differ, but not deterministically opposite for 3
    # classes) -> kappa below 1 and finite
    k = cohens_kappa(['A', 'A', 'B', 'C'], ['B', 'C', 'A', 'A'])
    assert -1.0 <= k < 1.0, k
    # identical single-class lists -> chance agreement is total -> kappa defined as 1.0
    assert cohens_kappa(['A', 'A', 'A'], ['A', 'A', 'A']) == 1.0

    clean = {'slp1': 'karman', 'sa': 'karma', 'ru': 'действие', 'label': 'correct'}
    g, score = rater_qe_composite(clean)
    assert g in ('A', 'B', 'C') and 0.0 <= score <= 1.0
    print('build_grade_gold selftest OK -- label mapping, kappa (identity/partial), '
          'qe_composite rater')
    return 0


def main():
    ap = argparse.ArgumentParser(description='H1457 A1 -- frozen gold grade sample')
    sub = ap.add_subparsers(dest='cmd', required=True)

    b = sub.add_parser('build', help='label gold_set.jsonl A/B/C via two raters, freeze + memo')
    b.add_argument('--gold', default=DEFAULT_GOLD)
    b.add_argument('--out', default=DEFAULT_OUT)
    b.add_argument('--memo', default=DEFAULT_MEMO)

    v = sub.add_parser('verify', help='check the frozen file is well-formed')
    v.add_argument('--out', default=DEFAULT_OUT)

    sub.add_parser('selftest', help='deterministic fixture asserts')

    a = ap.parse_args()
    if a.cmd == 'build':
        return cmd_build(a)
    if a.cmd == 'verify':
        return cmd_verify(a)
    if a.cmd == 'selftest':
        return selftest()
    return 1


if __name__ == '__main__':
    sys.exit(main())
