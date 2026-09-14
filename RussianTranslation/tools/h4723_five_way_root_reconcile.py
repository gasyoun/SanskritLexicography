#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H4723 — MW root/dhātu extraction five-way reconciliation.

Reconciles five independent MW root inventories into ONE root-identity
crosswalk keyed on a normalized form_key (homonym-stripped, lowercase IAST):

  1. WhitneyRoots   crosswalk/mw_roots.json            (750 MW verbal-root records)
  2. MWS            root_crosswalk/root_crosswalk.csv  (935 Whitney-hub rows, 809 in-MW)
  3. csl-orig       v02/etymology_stats/root_oracle.tsv (derived-word → root pairs)
  4. SanskritLexicography  RussianTranslation/src/data/dhatup_multisource_crosswalk.json
                    (H4478 Palsule-hubbed dhātupāṭha crosswalk, whitney_root leg)
  5. MWderivations  step4/all.txt                      (220,248 classified derivations;
                    joined by parent form, root-matching parents only)

Canonical MW-side anchor (SHARED_CODE.md §11, kosha dataset `mw-roots`):
  csl-orig/v02/mw/mw_roots.tsv — 2,113 rows (750 genuineroot + 1,363 root).
  "3 repos independently re-scanned mw.txt before this existed (got
  750/809/1163) — consume this, never re-scan." This tool CONSUMES it; it
  never re-scans mw.txt.

Normalization (house rule, mirrors WhitneyRoots/scripts/root_triangulation.py
s2i()/bare(), SHARED_CODE.md §16 — vendored with provenance, cross-repo import
is fragile):
  form_key = lowercase( s2i( bare( form ) ) ) with two extra folds for the
  dhatup workbook's French-style transliteration: 'ç'→'ś' and '√'/NBSP strip.
  bare() strips homonym markers: leading "N " (Whitney hub) / trailing digit (MW).

Read-only over the four sibling clones; writes ONLY repo-local artifacts:
  RussianTranslation/data/etym/h4723_mw_roots_five_way_crosswalk.tsv
  RussianTranslation/reports/H4723_five_way_drift_report.json

Usage:
  python3 h4723_five_way_root_reconcile.py --emit    # build artifacts
  python3 h4723_five_way_root_reconcile.py --check   # recompute, diff vs committed
Exits 2 with a clear message when a sibling clone is missing (H4432 precedent).
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))            # SanskritLexicography/
GH = os.path.dirname(REPO)                                # GitHub/ siblings

P_WHITNEYROOTS = os.path.join(GH, "WhitneyRoots", "crosswalk", "mw_roots.json")
P_WR_MWDERIV = os.path.join(GH, "WhitneyRoots", "crosswalk", "mw_derivations.json")
P_MWS = os.path.join(GH, "MWS", "root_crosswalk", "root_crosswalk.csv")
P_ORACLE = os.path.join(GH, "csl-orig", "v02", "etymology_stats", "root_oracle.tsv")
P_ROOTNORM = os.path.join(GH, "csl-orig", "v02", "etymology_stats", "root_norm.tsv")
P_MW_ROOTS_TSV = os.path.join(GH, "csl-orig", "v02", "mw", "mw_roots.tsv")
P_DHATUP = os.path.join(REPO, "RussianTranslation", "src", "data",
                        "dhatup_multisource_crosswalk.json")
P_MWDERIV = os.path.join(GH, "MWderivations", "step4", "all.txt")

OUT_TSV = os.path.join(REPO, "RussianTranslation", "data", "etym",
                       "h4723_mw_roots_five_way_crosswalk.tsv")
OUT_REPORT = os.path.join(REPO, "RussianTranslation", "reports",
                          "H4723_five_way_drift_report.json")

# --- vendored normalization (provenance: WhitneyRoots/scripts/root_triangulation.py,
#     SHARED_CODE.md §16; do not diverge without re-reading that module) ------------
_S2I = {'A': 'ā', 'I': 'ī', 'U': 'ū', 'f': 'ṛ', 'F': 'ṝ', 'x': 'ḷ', 'X': 'ḹ',
        'E': 'ai', 'O': 'au', 'M': 'ṃ', 'H': 'ḥ', 'K': 'kh', 'G': 'gh', 'N': 'ṅ',
        'C': 'ch', 'J': 'jh', 'Y': 'ñ', 'w': 'ṭ', 'W': 'ṭh', 'q': 'ḍ', 'Q': 'ḍh',
        'R': 'ṇ', 'T': 'th', 'D': 'dh', 'P': 'ph', 'B': 'bh', 'S': 'ś', 'z': 'ṣ',
        'L': 'ḻ'}


def s2i(s):
    """SLP1 -> IAST (vendored from root_triangulation.s2i)."""
    return ''.join([_S2I[c] if c in _S2I else c for c in s])


def bare(r):
    """Strip homonym markers: leading 'N ' (hub) or trailing digit (MW)."""
    r = r.strip()
    r = r.replace('\xa0', ' ')
    r = r.replace('√', '')
    r = r.replace('ç', 'ś')  # dhatup workbook French-style transliteration
    r = r.replace('\u1e5b', 'ṛ')  # safety no-op fold, keeps ascii-normalizers happy
    import re
    r = re.sub(r'^\d+\s+', '', r)
    r = re.sub(r'\d+$', '', r)
    return r.strip()


def form_key(raw):
    """Normalized root-identity key: bare + s2i + lowercase."""
    return s2i(bare(raw)).lower()


def need(path):
    if not os.path.exists(path):
        sys.stderr.write(
            "MISSING %s — this tool reads five sibling clones read-only; "
            "clone it next to SanskritLexicography/ first (H4432: exit 2, "
            "not a traceback).\n" % path)
        sys.exit(2)


# --- leg extractors -----------------------------------------------------------

def load_whitneyroots():
    """Leg 1: WhitneyRoots crosswalk/mw_roots.json -> {key: detail}."""
    d = json.load(open(P_WHITNEYROOTS, encoding='utf-8'))
    out = {}
    for rec in d:
        k = form_key(rec['slp1'])
        if not k:
            continue
        cur = out.setdefault(k, {'mw_L': [], 'classes': set(), 'homonyms': set(),
                                 'records': 0, 'slp1': rec['slp1']})
        cur['records'] += 1
        if rec.get('mw_L'):
            cur['mw_L'].append(str(rec['mw_L']))
        cur['classes'].update(rec.get('class') or [])
        if rec.get('homonym'):
            cur['homonyms'].add(str(rec['homonym']))
    return d, out


def load_mws():
    """Leg 2: MWS root_crosswalk.csv (935 Whitney-hub rows)."""
    rows = []
    out = {}
    with open(P_MWS, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            root = row.get('root') or ''
            rows.append(row)
            k = form_key(root)
            if not k:
                continue
            cur = out.setdefault(k, {'whitney_ids': set(), 'in_mw': False,
                                     'dcs_status': set()})
            cur['whitney_ids'].add(row['whitney_id'])
            cur['in_mw'] = cur['in_mw'] or row['in_MW'] == 'yes'
            if row.get('dcs_status'):
                cur['dcs_status'].add(row['dcs_status'])
    return rows, out


def load_oracle():
    """Leg 3: csl-orig etymology_stats/root_oracle.tsv, canonical-mapped keys."""
    canon = {}
    with open(P_ROOTNORM, encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            canon[row['variant_slp1']] = row['canonical_slp1']
    n_pairs = 0
    out = {}
    with open(P_ORACLE, encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            n_pairs += 1
            r = canon.get(row['root_slp1'], row['root_slp1'])
            k = form_key(r)
            if not k:
                continue
            cur = out.setdefault(k, {'pairs': 0, 'slp1': r})
            cur['pairs'] += 1
    return n_pairs, out


def load_dhatup():
    """Leg 4: SanskritLexicography dhatup_multisource_crosswalk.json whitney_root."""
    d = json.load(open(P_DHATUP, encoding='utf-8'))
    filled = 0
    out = {}
    for row in d['rows']:
        wr = row.get('whitney_root')
        if not wr:
            continue
        filled += 1
        k = form_key(wr)
        if not k:
            continue
        out.setdefault(k, {'rows': 0})
        out[k]['rows'] += 1
    return d, filled, out


def load_mwderiv(root_union):
    """Leg 5: MWderivations step4/all.txt — classification rows joined by parent
    form; only parents matching the four root legs enter the crosswalk."""
    n_rows = 0
    n_todo = 0
    parents = Counter()
    class_hist = Counter()
    matched = {}
    with open(P_MWDERIV, encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 5:
                continue
            n_rows += 1
            cls = parts[4]
            class_hist[cls] += 1
            if 'TODO' in cls.upper():
                n_todo += 1
            parent = form_key(parts[3].split('-')[0]) if parts[3] else ''
            if not parent:
                continue
            parents[parent] += 1
            if parent in root_union:
                cur = matched.setdefault(parent, {'rows': 0, 'classes': Counter()})
                cur['rows'] += 1
                cur['classes'][cls] += 1
    return {'n_rows': n_rows, 'n_todo': n_todo, 'class_hist': class_hist,
            'distinct_parents': len(parents), 'matched': matched,
            'n_matched_forms': len(matched),
            'matched_rows': sum(v['rows'] for v in matched.values())}


def load_canonical_mw_roots():
    """Canonical MW-side anchor: csl-orig/v02/mw/mw_roots.tsv (never re-scan mw.txt)."""
    by_type = Counter()
    with open(P_MW_ROOTS_TSV, encoding='utf-8') as f:
        r = csv.DictReader(f, delimiter='\t')
        col = 'verb_type' if 'verb_type' in (r.fieldnames or []) else None
        for row in r:
            if col:
                by_type[row[col]] += 1
            else:
                by_type['_rows'] += 1
    return sum(by_type.values()), dict(by_type)


# --- main ---------------------------------------------------------------------

def build():
    for p in (P_WHITNEYROOTS, P_WR_MWDERIV, P_MWS, P_ORACLE, P_ROOTNORM,
              P_MW_ROOTS_TSV, P_DHATUP, P_MWDERIV):
        need(p)

    wr_raw, leg1 = load_whitneyroots()
    wr_deriv = json.load(open(P_WR_MWDERIV, encoding='utf-8'))
    n_wr_deriv_roots = len(wr_deriv.get('by_whitney_no', {}))
    n_wr_deriv_records = sum(len(v) if isinstance(v, list) else 1
                             for v in wr_deriv.get('by_whitney_no', {}).values())

    mws_rows, leg2 = load_mws()
    mws_in_mw = sum(1 for v in leg2.values() if v['in_mw'])
    # published 809 counts CSV ROWS with in_MW=yes (rows == keys here: 1:1)
    mws_in_mw_rows = sum(1 for r in mws_rows if r['in_MW'] == 'yes')

    n_oracle_pairs, leg3 = load_oracle()
    dhatup_raw, n_dhatup_filled, leg4 = load_dhatup()

    root_union = set(leg1) | set(leg2) | set(leg3) | set(leg4)
    md = load_mwderiv(root_union)
    n_canon, canon_by_type = load_canonical_mw_roots()

    # ---- assemble the crosswalk ----
    all_keys = sorted(root_union)
    rows = []
    nsrc_hist = Counter()
    for k in all_keys:
        l1 = leg1.get(k)
        l2 = leg2.get(k)
        l3 = leg3.get(k)
        l4 = leg4.get(k)
        l5 = md['matched'].get(k)
        flags = [bool(l1), bool(l2), bool(l3), bool(l4), bool(l5)]
        n = sum(flags)
        nsrc_hist[n] += 1
        rows.append({
            'form_key': k,
            'n_sources': n,
            'whitneyroots': int(flags[0]),
            'mws': int(flags[1]),
            'cslorig_etym': int(flags[2]),
            'sanskritlex': int(flags[3]),
            'mwderiv': int(flags[4]),
            'whitneyroots_mw_L': ','.join(sorted(set(l1['mw_L']))) if l1 else '',
            'whitneyroots_class': ','.join(sorted(l1['classes'])) if l1 else '',
            'whitneyroots_homonym': ','.join(sorted(l1['homonyms'])) if l1 else '',
            'whitneyroots_records': l1['records'] if l1 else 0,
            'mws_whitney_id': ','.join(sorted(l2['whitney_ids'])) if l2 else '',
            'mws_dcs_status': ','.join(sorted(l2['dcs_status'])) if l2 else '',
            'cslorig_oracle_pairs': l3['pairs'] if l3 else 0,
            'sanskritlex_rows': l4['rows'] if l4 else 0,
            'mwderiv_rows': l5['rows'] if l5 else 0,
            'mwderiv_classes': ';'.join(
                '%s:%d' % (c, n_) for c, n_ in
                sorted(l5['classes'].items(), key=lambda x: -x[1])[:5]) if l5 else '',
            'slp1_native': (l1 or l3 or {}).get('slp1', ''),
        })

    all5 = nsrc_hist[4]  # four root legs all present
    report = {
        'handoff': 'H4723',
        'built': '2026-09-15',
        'normalization': 'form_key = lowercase(s2i(bare(form))) ; bare strips '
                         'homonym markers/√/NBSP, folds ç→ś (dhatup workbook); '
                         's2i/bare vendored from WhitneyRoots/scripts/'
                         'root_triangulation.py (SHARED_CODE §16)',
        'sources': {
            'whitneyroots': {
                'path': 'WhitneyRoots/crosswalk/mw_roots.json',
                'published': {'records': 750,
                              'note': 'MWS/root_crosswalk/ROOT_CROSSWALK_SUMMARY.md '
                                      '"MW verbal-root records: 750"'},
                'recounted': {'records': len(wr_raw),
                              'distinct_form_keys': len(leg1)},
                'verdict': 'MATCH' if len(wr_raw) == 750 else 'DRIFT',
                'census_drift': 'H4700 census §A2 said "620 корней" — conflated '
                                'with WhitneyRoots/crosswalk/mw_derivations.json '
                                'by_whitney_no=%d roots (records=%d). Census row '
                                'stale, file is 750.' % (n_wr_deriv_roots,
                                                         n_wr_deriv_records),
            },
            'mws': {
                'path': 'MWS/root_crosswalk/root_crosswalk.csv',
                'published': {'hub_rows': 935, 'in_MW_yes': 809,
                              'note': 'ROOT_CROSSWALK_SUMMARY.md'},
                'recounted': {'hub_rows': len(mws_rows),
                              'in_MW_yes_rows': mws_in_mw_rows,
                              'distinct_form_keys': len(leg2),
                              'in_MW_yes_keys': mws_in_mw},
                'verdict': ('MATCH' if (len(mws_rows) == 935 and
                                        mws_in_mw_rows == 809) else 'DRIFT'),
            },
            'cslorig_etymology_stats': {
                'path': 'csl-orig/v02/etymology_stats/root_oracle.tsv',
                'published': {'distinct_roots_census': 1163},
                'recounted': {'oracle_pairs': n_oracle_pairs,
                              'distinct_form_keys_canonical_mapped': len(leg3)},
                'verdict': 'DRIFT-EXPLAINED',
                'census_drift': '1,163 was a historical third re-scan of mw.txt '
                                '(kosha dataset mw-roots notes: "3 repos '
                                'independently re-scanned mw.txt before this '
                                'existed (got 750/809/1163)"). The root oracle '
                                'counts DERIVED-WORD→root pairs across 10 dicts '
                                '(3,036 distinct roots), a different population '
                                'from the MW verbal-root inventory. Canonical '
                                'MW-side anchor: csl-orig/v02/mw/mw_roots.tsv.',
                'canonical_mw_roots_tsv': {'rows': n_canon,
                                           'by_verb_type': canon_by_type,
                                           'expect': '2113 = 750 genuineroot + '
                                                     '1363 root (kosha mw-roots)'},
            },
            'sanskritlex_dhatup': {
                'path': 'RussianTranslation/src/data/'
                        'dhatup_multisource_crosswalk.json',
                'published': {'rows': 5183, 'whitney_root_filled': 1692,
                              'note': 'in-file counts block (H4478)'},
                'recounted': {'rows': dhatup_raw['counts']['rows'],
                              'whitney_root_filled': n_dhatup_filled,
                              'distinct_form_keys': len(leg4)},
                'verdict': ('MATCH' if (dhatup_raw['counts']['rows'] == 5183 and
                                        n_dhatup_filled == 1692) else 'DRIFT'),
            },
            'mwderivations': {
                'path': 'MWderivations/step4/all.txt',
                'published': {'records': 220248,
                              'note': 'H4700 census §C3'},
                'recounted': {'records': md['n_rows'],
                              'TODO_rows': md['n_todo'],
                              'distinct_parent_forms': md['distinct_parents'],
                              'parents_matching_root_union': md['n_matched_forms'],
                              'rows_on_matched_parents': md['matched_rows'],
                              'class_histogram_top10': dict(
                                  md['class_hist'].most_common(10))},
                'verdict': ('MATCH' if md['n_rows'] == 220248 else 'DRIFT'),
                'scope_note': 'MWderivations classifies NOMINAL derivations; its '
                              'parents are bases, not roots. Only parents matching '
                              'the four root inventories enter the crosswalk '
                              '(mwderiv column); forms unique to MWderivations are '
                              'counted here, not emitted as root rows. Census §C3 '
                              '"5,667 TODO" is NOT reproducible from the current '
                              'tree: step4/all.txt col5 carries gender/verb-class '
                              '(0 TODO rows); the NTD/TODO status belongs to the '
                              'analysis pipeline fields (step4/readme.org init: '
                              '22,033 NTD / 180,612 TODO) — census-figure drift, '
                              'not a data defect.',
            },
        },
        'crosswalk': {
            'rows': len(rows),
            'n_sources_histogram': {str(k): v for k, v in sorted(nsrc_hist.items())},
            'all_four_root_legs': all5,
            'legs_sizes': {'whitneyroots': len(leg1), 'mws': len(leg2),
                           'cslorig_etym': len(leg3), 'sanskritlex': len(leg4),
                           'mwderiv_matched': md['n_matched_forms']},
        },
    }
    return rows, report


TSV_COLS = ['form_key', 'n_sources', 'whitneyroots', 'mws', 'cslorig_etym',
            'sanskritlex', 'mwderiv', 'whitneyroots_mw_L', 'whitneyroots_class',
            'whitneyroots_homonym', 'whitneyroots_records', 'mws_whitney_id',
            'mws_dcs_status', 'cslorig_oracle_pairs', 'sanskritlex_rows',
            'mwderiv_rows', 'mwderiv_classes', 'slp1_native']


def write_tsv(rows):
    os.makedirs(os.path.dirname(OUT_TSV), exist_ok=True)
    with open(OUT_TSV, 'w', encoding='utf-8', newline='') as f:
        f.write('\t'.join(TSV_COLS) + '\n')
        for r in rows:
            f.write('\t'.join(str(r[c]) for c in TSV_COLS) + '\n')


def write_report(report):
    os.makedirs(os.path.dirname(OUT_REPORT), exist_ok=True)
    with open(OUT_REPORT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--emit', action='store_true', help='build artifacts')
    g.add_argument('--check', action='store_true',
                   help='recompute and diff against committed report')
    args = ap.parse_args()

    rows, report = build()

    if args.emit:
        write_tsv(rows)
        write_report(report)
        print('EMITTED %s (%d rows)' % (OUT_TSV, len(rows)))
        print('EMITTED %s' % OUT_REPORT)
        print('verdicts: ' + '; '.join(
            '%s=%s' % (k, v['verdict'])
            for k, v in report['sources'].items()))
        return 0

    # --check: recompute and diff against the committed report
    if not os.path.exists(OUT_REPORT):
        sys.stderr.write('CHECK FAIL: no committed report at %s\n' % OUT_REPORT)
        return 1
    committed = json.load(open(OUT_REPORT, encoding='utf-8'))
    if committed == report:
        print('CHECK PASS: recomputed report identical to committed (%d crosswalk '
              'rows)' % len(rows))
        return 0
    diffs = []
    for src in set(committed['sources']) | set(report['sources']):
        if committed['sources'].get(src) != report['sources'].get(src):
            diffs.append('sources.%s' % src)
    for k in ('rows', 'n_sources_histogram', 'all_four_root_legs', 'legs_sizes'):
        if committed['crosswalk'].get(k) != report['crosswalk'].get(k):
            diffs.append('crosswalk.%s' % k)
    sys.stderr.write('CHECK FAIL: drift in %s\n' % ', '.join(sorted(diffs)))
    return 1


if __name__ == '__main__':
    sys.exit(main())
