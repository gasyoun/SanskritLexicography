#!/usr/bin/env python
r"""cohort_clean_rates.py — W1-A per-cohort clean-rate report + D-1 debt worklist (H1149).

Ruling R3 (PWG_RU_UNFREEZE plan) asks for a per-cohort clean-rate measurement BEFORE any
further pwg_ru lane is drained: either a cohort genuinely clears the 80% bar (and scale
unfreezes honestly), or the bar is proven unreachable with the evidence that exists. This
script is a pure, stdlib-only, READ-ONLY join over the canonical store + already-committed
evidence documents. It invents no cohort definitions and recomputes no audited number:

  * the `no_pwg` / `root_upasarga` / `nominal` split is a lookup against
    `verb_worklist.verb_universe()` (the same `verbs01/pwg_preverb1.txt` root universe
    `verb_worklist.py` already reads) and the store's own `layer` field
    (ARCHITECTURE_SanskritLexicography_PWG_RU_UNFREEZE.md §2.1) — never a regex guess;
  * `no_pwg`'s clean rate is CONSUMED verbatim from the H911 quality/economy census
    (`pwg_ru/h911/h911_quality_economy_census.json`), never recomputed;
  * `root_upasarga` / `nominal` clean-rate evidence is READ from `src/pilot/RUN_LOG.md`'s
    already-committed prose entries (frozen, dated, cited by section) — see the two
    `_EVIDENCE` constants below for exactly what was read and why each carries a caveat.

CRITICAL FRAMING (do not violate): an all-cohorts-BELOW_BAR / INSUFFICIENT_EVIDENCE result
is a PASS of this deliverable's goal. Do not widen the sample, re-run, or retry to reach a
higher number — report what the frozen evidence says and stop.

Usage:
    python src/pilot/cohort_clean_rates.py --out pwg_ru/h1112/cohort_clean_rates.json

Writes: `pwg_ru/h1112/cohort_clean_rates.json`, plus the companion D-1 worklist via
`--worklist-out` (see `write_h_reconstructed_worklist`).
"""
import argparse
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
RT = os.path.dirname(SRC)

if SRC not in sys.path:
    sys.path.insert(0, SRC)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from store_path import canonical_store  # noqa: E402
import verb_worklist as vw              # noqa: E402

DEFAULT_STORE = canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl'))
H911_CENSUS = os.path.join(RT, 'pwg_ru', 'h911', 'h911_quality_economy_census.json')
NO_PWG_LAYERS = {'pw', 'sch', 'nws', 'pwkvn'}
BAR = 0.80

# ---------------------------------------------------------------------------------
# Frozen prose evidence for the two PWG-native cohorts. NOT recomputed — read once
# from the committed RUN_LOG.md and hardcoded here with an explicit artifact
# citation + the caveat that governs the verdict. A future session with FRESH
# audited evidence replaces these constants; it must not silently average them in.
# ---------------------------------------------------------------------------------

# root_upasarga: the only per-window AUDITED clean-vs-reject split for a PWG-rooted
# VERB window anywhere in RUN_LOG.md is the "Stage A+B summary" table (2026-06-29):
# sTA 96/123, BU 45/59, as 81/98, i 179/204 -> 401/484 = 82.9%.
# LOAD-BEARING CAVEAT (verified 17-07-2026 against the live canonical store): none of
# {sTA, BU, as, i} exist as a promoted key1 under ANY layer in the CURRENT store
# (11,603 rows) — checked both as literal key1 and via `safe_filename` decoding of
# every pwg-layer subcard prefix. The store's current 48 root_upasarga heads (the
# intersection of pwg-layer key1s with `verb_worklist.verb_universe()`: Ap, As, Bid,
# Buj, Cid, DA, Sam, Sru, banD, brU, car, dA, dah, diS, gA, gam, hA, han, hi, iz, jIv,
# jYA, jan, ji, laB, mA, mad, man, muc, nI, naS, pA, paS, pat, rakz, siD, su, vA, vac,
# vad, vah, vas, viS, vid, vraj, yA, yaj, yat) were promoted by LATER, separate
# sessions using a different generator (`gen_opt_harness2.py`, not the Stage A+B
# `gen_opt_harness.py`) — every one of those later RUN_LOG entries (`dah`, `gam`,
# `vid`, ...) reports a raw PROMOTED count, never an audited clean-vs-reject split.
# The one number that exists therefore cannot be bound to the population it would
# need to describe. Reported as INSUFFICIENT_EVIDENCE, not averaged in or assumed.
ROOT_UPASARGA_EVIDENCE = {
    'artifact': 'RussianTranslation/src/pilot/RUN_LOG.md#Stage-AB-summary-2026-06-29',
    'sample_clean': 401,
    'sample_n': 484,
    'sample_rate': round(401 / 484, 4),
    'sample_roots': ['sTA', 'BU', 'as', 'i'],
    'caveat': (
        "Stage A+B's 4 roots (sTA, BU, as, i) are ABSENT from the current canonical "
        "store (verified 17-07-2026: zero rows under those key1 values, any layer) -- "
        "the 401/484 sample cannot be bound to the store's CURRENT 48-root "
        "root_upasarga population. No other RUN_LOG.md entry provides an audited "
        "clean-vs-reject split (as opposed to a raw promoted-count) for a root "
        "actually present in the store today (dah, gam, vid, ...)."
    ),
}

# nominal: the only nominal-cohort PRODUCTION run in RUN_LOG.md is
# `nominal_w1_100small` (2026-07-06): 100/100 cards PROMOTED (0 null after 2 requeue
# passes). But that entry's OWN text states the audit tool is untrustworthy for
# nominal windows: "a nominal keys-based window has no rootmap ... audit_window.py
# ... needs --allow-stale. In that forensic mode the glue gates CRASH and
# missing_required_sense_field misfires, reporting a bogus 86 'defect'". "Promoted"
# therefore measures GENERATION success, not AUDITED quality — no clean-vs-reject
# split was ever produced. `pril10_w1` (2026-07-05) aborted on cost, not quality,
# and produced no rate either.
NOMINAL_EVIDENCE = {
    'artifact': 'RussianTranslation/src/pilot/RUN_LOG.md#nominal-window-nominal_w1_100small-2026-07-06',
    'sample_promoted': 100,
    'sample_n': 100,
    'caveat': (
        "100/100 PROMOTED is a generation-success count, not an audit-clean count -- "
        "the same RUN_LOG entry documents that audit_window.py's glue gates CRASH "
        "and missing_required_sense_field misfires on nominal (--allow-stale) "
        "windows, so no reliable clean-vs-reject split was ever produced for this "
        "cohort. `pril10_w1` (2026-07-05) aborted on cost, not quality -- no rate "
        "either."
    ),
}


def read_store(path=DEFAULT_STORE):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def partition(rows, verb_roots):
    """Partition store rows into no_pwg / root_upasarga / nominal / unassigned.

    Binds to existing machinery only (ARCHITECTURE §2.1):
      - no_pwg          <- layer in {pw, sch, nws, pwkvn}
      - root_upasarga   <- layer == pwg AND key1 resolves into verb_worklist's
                            verbs01/pwg_preverb1.txt root universe
      - nominal         <- layer == pwg AND key1 does NOT resolve into that universe
      - unassigned      <- anything else (reported, never dropped)

    Each row is also tagged with whether it carries provenance.h_reconstructed==true
    (the D-1 exclusion, §2.1(a)) so the caller can report cohort rows both
    inclusive and exclusive of that debt.
    """
    buckets = collections.defaultdict(list)
    for row in rows:
        layer = row.get('layer')
        if layer in NO_PWG_LAYERS:
            cohort = 'no_pwg'
        elif layer == 'pwg':
            cohort = 'root_upasarga' if row.get('key1') in verb_roots else 'nominal'
        else:
            cohort = 'unassigned'
        buckets[cohort].append(row)
    return buckets


def is_h_reconstructed(row):
    return bool((row.get('provenance') or {}).get('h_reconstructed'))


def count_h_reconstructed(store_path):
    """Count `provenance.h_reconstructed == true` rows in a store file (any path)."""
    n = 0
    with open(store_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if is_h_reconstructed(json.loads(line)):
                n += 1
    return n


def assert_h_reconstructed_regression(store_path, expected=468, manifest_path=None):
    """D-1 regression guard (H1149 step 9, window_selftest.py's live consumer).

    The `h_reconstructed` count must stay exactly `expected` unless an authorized
    re-translation manifest documents a decrease. A silent DROP in this count is the
    exact failure mode this guards against: PR #510's underlying `h is None` count
    fell 468 -> 0 and became invisible to the only query that could find it (Uprava
    FINDINGS §95). This must FAIL LOUD on any unexplained change, not pass quietly.

    Returns the measured count on success; raises AssertionError otherwise.
    """
    actual = count_h_reconstructed(store_path)
    if actual == expected:
        return actual
    if manifest_path and os.path.exists(manifest_path):
        with open(manifest_path, encoding='utf-8') as f:
            manifest = json.load(f)
        if (manifest.get('schema') == 'pwg_ru.h_reconstructed_retranslation_manifest.v1'
                and manifest.get('new_count') == actual and actual < expected):
            return actual  # an authorized live run documented exactly this decrease
    raise AssertionError(
        'h_reconstructed count regression: expected %d, found %d in %s -- a silent '
        'change to this count must be documented by an authorized re-translation '
        'manifest (schema pwg_ru.h_reconstructed_retranslation_manifest.v1 with a '
        'matching new_count), not silently accepted (Uprava FINDINGS §95: this exact '
        'class of drop went 468->0 and became unfindable by the query that could see '
        'it, once already).' % (expected, actual, store_path))


def cohort_counts(rows):
    hrecon = [r for r in rows if is_h_reconstructed(r)]
    return {
        'rows_total_layer': len(rows),
        'h_reconstructed_excluded': len(hrecon),
        'rows': len(rows) - len(hrecon),
    }


def load_no_pwg_evidence(census_path=H911_CENSUS):
    with open(census_path, encoding='utf-8') as f:
        census = json.load(f)
    fam = census['families']['H255_no_pwg_workflow']
    rate_str = fam['population_audit_clean_rate']
    # Parse the median/range the census itself states -- CONSUME, do not recompute.
    import re
    m = re.search(r'(\d+)%-(\d+)%.*?median ~(\d+)%', rate_str)
    if not m:
        raise SystemExit('FAIL: could not parse H911 population_audit_clean_rate: %r' % rate_str)
    lo, hi, median = (int(m.group(i)) / 100.0 for i in (1, 2, 3))
    return {
        'clean_rate': median,
        'range': [lo, hi],
        'raw_statement': rate_str,
        'evidence': 'RussianTranslation/pwg_ru/h911/h911_quality_economy_census.json'
                    '#families.H255_no_pwg_workflow.population_audit_clean_rate',
        'not_recoverable_note': census.get('not_recoverable_note'),
    }


def verdict_for(clean_rate, n, bar=BAR):
    if clean_rate is None:
        return 'INSUFFICIENT_EVIDENCE'
    # A tiny n cannot separate ~62% from 80% -- treat n < 30 as insufficient
    # regardless of the point estimate (same spirit as the census's own median-CI caveat).
    if n is not None and n < 30:
        return 'INSUFFICIENT_EVIDENCE'
    return 'CLEARS_BAR' if clean_rate >= bar else 'BELOW_BAR'


def build_report(store_path=DEFAULT_STORE, census_path=H911_CENSUS):
    rows = read_store(store_path)
    verb_roots = vw.verb_universe()
    buckets = partition(rows, verb_roots)

    no_pwg_counts = cohort_counts(buckets.get('no_pwg', []))
    root_counts = cohort_counts(buckets.get('root_upasarga', []))
    nominal_counts = cohort_counts(buckets.get('nominal', []))
    unassigned_rows = buckets.get('unassigned', [])

    no_pwg_evidence = load_no_pwg_evidence(census_path)
    no_pwg_verdict = verdict_for(no_pwg_evidence['clean_rate'], no_pwg_counts['rows'])

    root_verdict = verdict_for(None, None)  # forced INSUFFICIENT_EVIDENCE, see constant docstring
    nominal_verdict = verdict_for(None, None)

    total_hrecon = (no_pwg_counts['h_reconstructed_excluded']
                    + root_counts['h_reconstructed_excluded']
                    + nominal_counts['h_reconstructed_excluded'])
    rows_sum = no_pwg_counts['rows'] + root_counts['rows'] + nominal_counts['rows']

    report = {
        'schema': 'pwg_ru.cohort_clean_rates.v1',
        'measured': '2026-07-17',
        # a logical repo-relative label, NOT a filesystem os.path.relpath -- the store
        # resolves to the MAIN checkout via canonical_store() and this report may run
        # from an isolated worktree, where a filesystem-relative path would be
        # worktree-specific and misleading once committed.
        'store_path': 'RussianTranslation/src/pwg_ru_translated.jsonl',
        'store_rows': len(rows),
        'excluded': {
            'h_reconstructed': total_hrecon,
            'unassigned': len(unassigned_rows),
        },
        'unassigned_keys': sorted({r.get('key1') for r in unassigned_rows}),
        'bar': BAR,
        'cohorts': {
            'no_pwg': {
                'rows': no_pwg_counts['rows'],
                'rows_including_h_reconstructed': no_pwg_counts['rows_total_layer'],
                'h_reconstructed_excluded': no_pwg_counts['h_reconstructed_excluded'],
                'clean_rate': no_pwg_evidence['clean_rate'],
                'range': no_pwg_evidence['range'],
                'n_windows': 10,
                'verdict': no_pwg_verdict,
                'evidence': no_pwg_evidence['evidence'],
                'evidence_statement': no_pwg_evidence['raw_statement'],
            },
            'root_upasarga': {
                'rows': root_counts['rows'],
                'rows_including_h_reconstructed': root_counts['rows_total_layer'],
                'h_reconstructed_excluded': root_counts['h_reconstructed_excluded'],
                'clean_rate': None,
                'verdict': root_verdict,
                'evidence': ROOT_UPASARGA_EVIDENCE['artifact'],
                'evidence_sample': '%d/%d = %.1f%% (%s)' % (
                    ROOT_UPASARGA_EVIDENCE['sample_clean'], ROOT_UPASARGA_EVIDENCE['sample_n'],
                    100 * ROOT_UPASARGA_EVIDENCE['sample_rate'],
                    ', '.join(ROOT_UPASARGA_EVIDENCE['sample_roots'])),
                'evidence_caveat': ROOT_UPASARGA_EVIDENCE['caveat'],
            },
            'nominal': {
                'rows': nominal_counts['rows'],
                'rows_including_h_reconstructed': nominal_counts['rows_total_layer'],
                'h_reconstructed_excluded': nominal_counts['h_reconstructed_excluded'],
                'clean_rate': None,
                'verdict': nominal_verdict,
                'evidence': NOMINAL_EVIDENCE['artifact'],
                'evidence_sample': '%d/%d promoted (not an audit-clean count)' % (
                    NOMINAL_EVIDENCE['sample_promoted'], NOMINAL_EVIDENCE['sample_n']),
                'evidence_caveat': NOMINAL_EVIDENCE['caveat'],
            },
        },
        'rows_plus_excluded_equals_store_rows': rows_sum + total_hrecon == len(rows),
        'economy': 'NOT_MEASURABLE',
        'economy_note': no_pwg_evidence['not_recoverable_note'],
        'drain_recommendation': (
            'No cohort names a drainable lane at the 80%% bar. no_pwg is MEASURED '
            'BELOW_BAR (~%d%% median, range %d%%-%d%%, evidence: H911 census). '
            'root_upasarga and nominal both lack an audited clean-vs-reject split '
            'verifiably bound to their CURRENT store population (see each cohort\'s '
            '`evidence_caveat`) -- reported INSUFFICIENT_EVIDENCE, not assumed. This '
            'report names no cohort as ready to drain; whether/how to lower the bar '
            'or gather fresh audited evidence for root_upasarga/nominal is a human '
            '`@DECIDE`.' % (round(100 * no_pwg_evidence['clean_rate']),
                            round(100 * no_pwg_evidence['range'][0]),
                            round(100 * no_pwg_evidence['range'][1]))
        ),
    }
    return report, buckets


def write_report_json(report, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
        f.write('\n')


BLOB_BASE = 'https://github.com/gasyoun/SanskritLexicography/blob/master/'


def blob_url(evidence_path):
    """Turn a repo-relative `evidence` citation into a full clickable GitHub blob URL
    (org convention: committed Markdown never carries a bare relative link)."""
    path, _, anchor = evidence_path.partition('#')
    url = BLOB_BASE + path
    return (url + '#' + anchor) if anchor else url


def write_report_md(report, out_path):
    lines = []
    lines.append('# H1112 — per-cohort clean-rate report (W1-A)')
    lines.append('')
    lines.append('_Created: 17-07-2026 · Last updated: 17-07-2026_')
    lines.append('')
    lines.append('_Auto-generated by `src/pilot/cohort_clean_rates.py` (H1149). Do not hand-edit '
                 '-- regenerate from the store + frozen evidence instead._')
    lines.append('')
    lines.append('**Ruling R3 (narrow-and-measure before draining):** this report gates every '
                 'pwg_ru drain in the repo, including H255\'s no-PWG lane. '
                 '**All-cohorts-BELOW_BAR/INSUFFICIENT_EVIDENCE is a PASS** of this deliverable '
                 '-- the measurement is commissioned to be capable of killing the 80% bar with '
                 'data, not to reach a good number.')
    lines.append('')
    lines.append('Store: `%s` — **%d rows** (measured %s).' %
                 (report['store_path'], report['store_rows'], report['measured']))
    lines.append('')
    lines.append('| cohort | rows (excl. h_reconstructed) | h_reconstructed excluded | '
                 'clean rate | verdict | evidence |')
    lines.append('|---|---:|---:|---|---|---|')
    for name in ('no_pwg', 'root_upasarga', 'nominal'):
        c = report['cohorts'][name]
        rate = ('%.1f%%' % (100 * c['clean_rate'])) if c.get('clean_rate') is not None else '—'
        lines.append('| `%s` | %d | %d | %s | **%s** | [`%s`](%s) |' % (
            name, c['rows'], c['h_reconstructed_excluded'], rate, c['verdict'],
            c['evidence'], blob_url(c['evidence'])))
    lines.append('')
    lines.append('**Bar:** %.0f%%.' % (100 * report['bar']))
    lines.append('')
    lines.append('**Exclusions:** `h_reconstructed` rows excluded from rates: **%d** '
                 '(counted separately, never dropped). `unassigned`: **%d**. '
                 '`rows + 468 == store_rows`: **%s**.' % (
                     report['excluded']['h_reconstructed'], report['excluded']['unassigned'],
                     report['rows_plus_excluded_equals_store_rows']))
    lines.append('')
    lines.append('## no_pwg')
    lines.append('')
    c = report['cohorts']['no_pwg']
    lines.append('- Clean rate **%.1f%%** (range %.0f%%–%.0f%%), consumed verbatim from the '
                 'H911 census: *"%s"*' % (100 * c['clean_rate'], 100 * c['range'][0],
                                          100 * c['range'][1], c['evidence_statement']))
    lines.append('- Verdict: **%s** (< 80%% bar).' % c['verdict'])
    lines.append('')
    lines.append('## root_upasarga')
    lines.append('')
    c = report['cohorts']['root_upasarga']
    lines.append('- Only candidate evidence: %s' % c['evidence_sample'])
    lines.append('- Caveat: %s' % c['evidence_caveat'])
    lines.append('- Verdict: **%s**.' % c['verdict'])
    lines.append('')
    lines.append('## nominal')
    lines.append('')
    c = report['cohorts']['nominal']
    lines.append('- Only candidate evidence: %s' % c['evidence_sample'])
    lines.append('- Caveat: %s' % c['evidence_caveat'])
    lines.append('- Verdict: **%s**.' % c['verdict'])
    lines.append('')
    lines.append('## Economy')
    lines.append('')
    lines.append('`NOT_MEASURABLE` — %s (quality only, never implies a cost verdict).' %
                 report['economy_note'])
    lines.append('')
    lines.append('## Drain recommendation')
    lines.append('')
    lines.append('> %s' % report['drain_recommendation'])
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def write_h_reconstructed_worklist(rows, out_path):
    """D-1: the standing re-translation worklist for the 468 h_reconstructed rows.

    Each line is one JSON object for one store row whose `provenance.h_reconstructed`
    is true. `h` is the DERIVED head (not lexicographic evidence -- see
    `mark_reconstructed_headwords.py`); grouping by `h` gives the 14 heads the 468
    rows collapse onto. This is the standing re-translation worklist (D-1);
    discharge requires an authorized live run, not this read-only report.
    """
    targets = [r for r in rows if is_h_reconstructed(r)]
    heads = collections.Counter(r.get('h') for r in targets)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        for r in targets:
            f.write(json.dumps({
                'schema': 'pwg_ru.h_reconstructed_worklist.v1',
                'worklist_note': ('standing re-translation worklist (D-1); discharge requires '
                                  'an authorized live run, not this read-only report'),
                'key': r.get('subcard'),
                'key1': r.get('key1'),
                'layer': r.get('layer'),
                'h': r.get('h'),
                'collapses_onto_head': r.get('h'),
                'head_group_size': heads[r.get('h')],
                'iast_reconstructed': bool((r.get('provenance') or {}).get('iast_reconstructed')),
                'grammar_defaulted_empty': bool((r.get('provenance') or {}).get('grammar_defaulted_empty')),
            }, ensure_ascii=False) + '\n')
    return len(targets), len(heads)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--store', default=DEFAULT_STORE, help='path to pwg_ru_translated.jsonl')
    ap.add_argument('--census', default=H911_CENSUS, help='path to h911 quality/economy census')
    ap.add_argument('--out', default=os.path.join(RT, 'pwg_ru', 'h1112', 'cohort_clean_rates.json'),
                    help='cohort_clean_rates.json output path')
    ap.add_argument('--md-out',
                    default=os.path.join(RT, 'pwg_ru', 'h1112',
                                         'H1112_COHORT_CLEAN_RATES_2026-07-17.md'),
                    help='dated markdown report output path')
    ap.add_argument('--worklist-out',
                    default=os.path.join(RT, 'pwg_ru', 'h1112', 'h_reconstructed_worklist.jsonl'),
                    help='D-1 worklist output path')
    args = ap.parse_args()

    report, buckets = build_report(args.store, args.census)
    write_report_json(report, args.out)
    write_report_md(report, args.md_out)
    all_rows = [r for rs in buckets.values() for r in rs]
    n_worklist, n_heads = write_h_reconstructed_worklist(all_rows, args.worklist_out)

    print('store_rows=%d  no_pwg=%d(%s)  root_upasarga=%d(%s)  nominal=%d(%s)  '
          'h_reconstructed=%d  unassigned=%d' % (
              report['store_rows'],
              report['cohorts']['no_pwg']['rows'], report['cohorts']['no_pwg']['verdict'],
              report['cohorts']['root_upasarga']['rows'], report['cohorts']['root_upasarga']['verdict'],
              report['cohorts']['nominal']['rows'], report['cohorts']['nominal']['verdict'],
              report['excluded']['h_reconstructed'], report['excluded']['unassigned']))
    print('rows + h_reconstructed == store_rows: %s' % report['rows_plus_excluded_equals_store_rows'])
    print('wrote %s' % args.out)
    print('wrote %s' % args.md_out)
    print('wrote %s (%d lines, %d distinct heads)' % (args.worklist_out, n_worklist, n_heads))
    if n_worklist != 468:
        raise SystemExit('FAIL: expected 468 h_reconstructed rows, found %d' % n_worklist)
    if n_heads != 14:
        raise SystemExit('FAIL: expected 14 distinct collapsed heads, found %d' % n_heads)
    if report['excluded']['unassigned'] != 0:
        raise SystemExit('FAIL: %d row(s) unassigned -- partition is incomplete' %
                         report['excluded']['unassigned'])


if __name__ == '__main__':
    main()
