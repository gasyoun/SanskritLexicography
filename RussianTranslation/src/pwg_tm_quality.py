#!/usr/bin/env python
"""H2684 independent 400-fragment quality apparatus.

Grok 4.6 drafts. This module freezes a stratified sample and scores only a
genuinely independent adjudication file. Self-scores are retained as a
labelled diagnostic and NEVER counted as the independent gate.

  python src/pwg_tm_quality.py verify --sample 400
  python src/pwg_tm_quality.py freeze --in DIR --out FILE --sample 400
  python src/pwg_tm_quality.py packet --sample-file FILE --out FILE
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_canonical as C  # noqa: E402

SAMPLE_N = 400
FLOORS = {
    'fidelity': 0.98,
    'equivalence': 0.95,
    'serious_error': 0.01,
}
FORBIDDEN_INDEPENDENT_JUDGES = frozenset({
    'grok-4.6', 'grok-4.6-draft', 'grok-4.6-live', 'self', 'self_score',
    'self-score',
})

# ---- H3299 step 4: pinned per-defect-class severity rubric -------------------
# The judge labels every adjudicated row with exactly ONE defect_class; the
# serious_error verdict is DERIVED from this table and is never re-judged per
# fragment class or stratum bucket. H2684 convicted the same {%Jmd%}
# corruption as serious in one cell and non-serious in another — under this
# rubric that inconsistency is a machine-checkable violation
# (check_severity_consistency), not a judgment call.
# Historical adjudication files written before H3299 carry no defect_class;
# they stay byte-untouched evidence and are NOT re-verified under this rule.
SEVERITY_RUBRIC = {
    'none': False,                             # faithful + equivalent
    'placeholder_rendered_as_content': True,   # {%Jmd%} -> invented verb phrase
    'wrong_lexical_meaning': True,
    'sense_absent_or_inverted': True,
    'sanskrit_dropped_or_altered': True,
    'unfaithful_to_source': True,
    'german_residue': False,                   # minor: DE word left in RU
    'markup_drift': False,                     # minor: preserved-span drift
    'register_or_style': False,                # minor: meaning holds, style off
    'target_typo': False,                      # minor: typo in RU only
}
RUBRIC_UNKNOWN = object()


def rubric_serious(defect_class):
    """Pinned severity for a defect class; RUBRIC_UNKNOWN if unlisted."""
    if defect_class not in SEVERITY_RUBRIC:
        return RUBRIC_UNKNOWN
    return SEVERITY_RUBRIC[defect_class]


def _as_bool_sev(sev):
    return sev in (True, 1, 'yes', 'serious')


def check_severity_consistency(rows):
    """Same defect class ⇒ same severity, everywhere, regardless of bucket."""
    violations = []
    for i, row in enumerate(rows):
        adj = row.get('adjudication') or row
        sev = adj.get('serious_error')
        if sev is None:
            continue
        dc = adj.get('defect_class')
        expected = rubric_serious(dc)
        if expected is RUBRIC_UNKNOWN:
            violations.append(
                'row %d: unknown defect_class %r' % (i, dc))
        elif bool(_as_bool_sev(sev)) != bool(expected):
            violations.append(
                'row %d: defect_class %r is pinned serious=%s but '
                'serious_error=%r' % (i, dc, expected, sev))
    return violations
BLIND_DROP = (
    'generation', 'gate_receipt', 'gate_status', 'confidence_tier',
    'trust_level', 'reuse_policy', 'promotion_status', 'quarantine_reasons',
    'self_score', 'model_self_assessment', 'draft_note',
)
FREQ_BANDS = (
    ('zero_or_missing', lambda n: n is None or n <= 0),
    ('low', lambda n: n is not None and 0 < n < 50),
    ('mid', lambda n: n is not None and 50 <= n < 500),
    ('high', lambda n: n is not None and 500 <= n < 5000),
    ('very_high', lambda n: n is not None and n >= 5000),
)


def wilson(k, n, z=1.96):
    if n <= 0:
        return 0.0, 0.0, 0.0
    p = k / n
    z2 = z * z
    den = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / den
    half = (z / den) * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return p, max(0.0, centre - half), min(1.0, centre + half)


def freq_band(count_all):
    for name, pred in FREQ_BANDS:
        if pred(count_all):
            return name
    return 'zero_or_missing'


def complexity_stratum(row):
    loc = row.get('source_locator') or {}
    ctx = row.get('context') or {}
    if row.get('complex') or ctx.get('complex'):
        return 'complex'
    src = row.get('source_string') or ''
    if len(src) >= 240 or src.count('<ls') >= 3:
        return 'complex'
    if loc.get('homonym'):
        return 'complex'
    return 'simple'


def load_pool(paths):
    rows = []
    for path in paths:
        if not path or not os.path.exists(path):
            continue
        for row in C.read_jsonl(path):
            if row.get('record_kind') == 'fragment' or row.get('fragment_id'):
                rows.append(row)
    return rows


def stratum_key(row, queue_by_k1):
    loc = row.get('source_locator') or {}
    k1 = loc.get('lemma_slp1') or loc.get('key1') or ''
    q = queue_by_k1.get(k1) or {}
    accepted = row.get('promotion_status') == 'promoted' or row.get('gate_status') == 'pass'
    return (
        row.get('fragment_class') or 'unknown',
        freq_band(q.get('count_all')),
        complexity_stratum(row),
        row.get('confidence_tier') or 'unknown',
        'accepted' if accepted else 'rejected',
    )


def freeze_sample(rows, queue_rows, n=SAMPLE_N, seed=2684):
    queue_by_k1 = {r['k1']: r for r in queue_rows}
    buckets = defaultdict(list)
    for row in rows:
        buckets[stratum_key(row, queue_by_k1)].append(row)
    rng = random.Random(seed)
    for key in buckets:
        buckets[key].sort(key=lambda r: r.get('fragment_id') or '')
        rng.shuffle(buckets[key])
    # guarantee every non-empty class / band / accept-reject cell is represented
    picked = []
    seen = set()

    def take(row):
        fid = row.get('fragment_id')
        if not fid or fid in seen:
            return False
        seen.add(fid)
        picked.append(row)
        return True

    # first pass: one from each bucket
    for key in sorted(buckets):
        if buckets[key]:
            take(buckets[key][0])
    # second: round-robin until n
    order = sorted(buckets)
    idx = {k: 1 for k in order}
    while len(picked) < n:
        progressed = False
        for key in order:
            rows_k = buckets[key]
            i = idx[key]
            if i < len(rows_k) and take(rows_k[i]):
                idx[key] = i + 1
                progressed = True
            if len(picked) >= n:
                break
        if not progressed:
            break
    meta = {
        'schema': 'pwg.tm.quality.sample.v1',
        'n_requested': n,
        'n_drawn': len(picked),
        'seed': seed,
        'pool': len(rows),
        'buckets': {str(k): len(v) for k, v in sorted(buckets.items())},
        'by_class': dict(Counter(r.get('fragment_class') for r in picked)),
        'by_accept': dict(Counter(
            'accepted' if (r.get('promotion_status') == 'promoted'
                           or r.get('gate_status') == 'pass') else 'rejected'
            for r in picked)),
        'complete_n': len(picked) >= n,
    }
    return picked, meta


def blind_packet(rows):
    out = []
    for row in rows:
        item = {k: v for k, v in row.items() if k not in BLIND_DROP}
        item['adjudication'] = {
            'fidelity': None,
            'equivalence': None,
            'serious_error': None,
            'defect_class': None,
            'notes': '',
            'judge_id': None,
            'judge_model': None,
        }
        out.append(item)
    return out


def load_adjudication(path):
    rows = C.read_jsonl(path)
    return rows


def independence_errors(rows):
    errors = []
    if not rows:
        errors.append('adjudication file empty')
        return errors
    for i, row in enumerate(rows):
        adj = row.get('adjudication') or row
        judge = str(adj.get('judge_model') or adj.get('judge_id') or '').strip()
        if not judge:
            errors.append('row %d missing judge identity' % i)
            continue
        low = judge.lower()
        if low in FORBIDDEN_INDEPENDENT_JUDGES or low.startswith('grok-4.6'):
            errors.append(
                'row %d judge %r is not independent (Grok may not adjudicate itself)'
                % (i, judge))
    return errors


def score_adjudication(rows):
    n = len(rows)
    fid = eq = serious = 0
    labelled = 0
    per_class = defaultdict(lambda: {'n': 0, 'fid': 0, 'eq': 0, 'serious': 0})
    for row in rows:
        adj = row.get('adjudication') or row
        klass = row.get('fragment_class') or 'unknown'
        per_class[klass]['n'] += 1
        fidelity = adj.get('fidelity')
        equiv = adj.get('equivalence')
        sev = adj.get('serious_error')
        if fidelity is None and equiv is None and sev is None:
            continue
        labelled += 1
        if fidelity in (True, 1, 'pass', 'yes'):
            fid += 1
            per_class[klass]['fid'] += 1
        if equiv in (True, 1, 'correct', 'pass', 'yes'):
            eq += 1
            per_class[klass]['eq'] += 1
        if sev in (True, 1, 'yes', 'serious'):
            serious += 1
            per_class[klass]['serious'] += 1
    denom = labelled or n
    fp, flo, fhi = wilson(fid, denom)
    ep, elo, ehi = wilson(eq, denom)
    sp, slo, shi = wilson(serious, denom)
    return {
        'n': n,
        'labelled': labelled,
        'fidelity': {'k': fid, 'p': fp, 'lo': flo, 'hi': fhi},
        'equivalence': {'k': eq, 'p': ep, 'lo': elo, 'hi': ehi},
        'serious_error': {'k': serious, 'p': sp, 'lo': slo, 'hi': shi},
        'per_class': {k: dict(v) for k, v in per_class.items()},
    }


def floors_hold(scores):
    reasons = []
    if scores['labelled'] < SAMPLE_N:
        reasons.append('labelled %d < %d' % (scores['labelled'], SAMPLE_N))
    if scores['fidelity']['p'] < FLOORS['fidelity']:
        reasons.append('fidelity %.4f < %.2f' % (
            scores['fidelity']['p'], FLOORS['fidelity']))
    if scores['equivalence']['p'] < FLOORS['equivalence']:
        reasons.append('equivalence %.4f < %.2f' % (
            scores['equivalence']['p'], FLOORS['equivalence']))
    if scores['serious_error']['p'] > FLOORS['serious_error']:
        reasons.append('serious_error %.4f > %.2f' % (
            scores['serious_error']['p'], FLOORS['serious_error']))
    return not reasons, reasons


def verify(sample_n=SAMPLE_N, adjudication=None, sample_meta=None):
    report = {
        'schema': 'pwg.tm.quality.report.v1',
        'sample_n_required': sample_n,
        'floors': FLOORS,
        'independent': False,
        'independent_gate': 'not_run',
        'self_score_present': False,
        'ok': False,
        'reasons': [],
    }
    if sample_meta:
        report['sample'] = sample_meta
        if not sample_meta.get('complete_n'):
            report['reasons'].append(
                'frozen sample has %s rows; %d required'
                % (sample_meta.get('n_drawn'), sample_n))
    if not adjudication:
        report['reasons'].append(
            'no independent adjudication file; Grok self-scores are not a substitute')
        report['independent_gate'] = 'not_run'
        return report
    errs = independence_errors(adjudication)
    if errs:
        report['reasons'].extend(errs)
        report['independent_gate'] = 'refused_not_independent'
        return report
    scores = score_adjudication(adjudication)
    report['scores'] = scores
    report['independent'] = True
    report['rubric'] = 'pinned'
    rubric_violations = check_severity_consistency(adjudication)
    if rubric_violations:
        report['rubric_violations'] = rubric_violations
        report['reasons'].append(
            'severity rubric violated on %d row(s)' % len(rubric_violations))
    ok, reasons = floors_hold(scores)
    report['reasons'].extend(reasons)
    report['ok'] = ok and not report['reasons']
    report['independent_gate'] = 'pass' if report['ok'] else 'fail'
    return report


def iter_jsonl_offsets(path):
    with open(path, encoding='utf-8') as f:
        while True:
            pos = f.tell()
            line = f.readline()
            if line == '':
                break
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            yield pos, row


def read_offsets(path, offsets):
    rows = []
    with open(path, encoding='utf-8') as f:
        for pos in offsets:
            f.seek(pos)
            line = f.readline()
            if line.strip():
                rows.append(json.loads(line))
    return rows


def freeze_stream(paths, queue_rows, n=SAMPLE_N, seed=2684):
    """Stratum sample without loading the whole pool into RAM."""
    queue_by_k1 = {r['k1']: r for r in queue_rows}
    loc_buckets = defaultdict(list)
    pool = 0
    for path in paths:
        if not path or not os.path.exists(path):
            continue
        for pos, row in iter_jsonl_offsets(path):
            if not (row.get('record_kind') == 'fragment' or row.get('fragment_id')):
                continue
            loc_buckets[stratum_key(row, queue_by_k1)].append((path, pos))
            pool += 1
    rng = random.Random(seed)
    for key in loc_buckets:
        loc_buckets[key].sort()
        rng.shuffle(loc_buckets[key])
    picked_locs = []
    seen = set()

    def take(loc):
        token = '%s:%s' % loc
        if token in seen:
            return False
        seen.add(token)
        picked_locs.append(loc)
        return True

    for key in sorted(loc_buckets):
        if loc_buckets[key]:
            take(loc_buckets[key][0])
    order = sorted(loc_buckets)
    idx = {k: 1 for k in order}
    while len(picked_locs) < n:
        progressed = False
        for key in order:
            rows_k = loc_buckets[key]
            i = idx[key]
            if i < len(rows_k) and take(rows_k[i]):
                idx[key] = i + 1
                progressed = True
            if len(picked_locs) >= n:
                break
        if not progressed:
            break
    by_path = defaultdict(list)
    for path, pos in picked_locs:
        by_path[path].append(pos)
    picked = []
    for path, positions in by_path.items():
        picked.extend(read_offsets(path, positions))
    picked.sort(key=lambda r: r.get('fragment_id') or '')
    meta = {
        'schema': 'pwg.tm.quality.sample.v1',
        'n_requested': n,
        'n_drawn': len(picked),
        'seed': seed,
        'pool': pool,
        'buckets': {str(k): len(v) for k, v in sorted(loc_buckets.items())},
        'by_class': dict(Counter(r.get('fragment_class') for r in picked)),
        'by_accept': dict(Counter(
            'accepted' if (r.get('promotion_status') == 'promoted'
                           or r.get('gate_status') == 'pass') else 'rejected'
            for r in picked)),
        'complete_n': len(picked) >= n,
        'streamed': True,
    }
    return picked, meta


def cmd_freeze(args):
    paths = args.inputs or [
        os.path.join(args.in_dir, 'promoted.jsonl'),
        os.path.join(args.in_dir, 'quarantine.jsonl'),
    ]
    queue = C.read_jsonl(args.queue) if args.queue and os.path.exists(args.queue) else []
    if getattr(args, 'stream', False):
        picked, meta = freeze_stream(paths, queue, n=args.sample, seed=args.seed)
    else:
        pool = load_pool(paths)
        picked, meta = freeze_sample(pool, queue, n=args.sample, seed=args.seed)
    C.write_jsonl(args.out, picked)
    meta_path = args.out + '.meta.json'
    C.write_json(meta_path, meta)
    print(json.dumps(meta, ensure_ascii=False))
    return 0 if meta['n_drawn'] else 1


def cmd_packet(args):
    rows = C.read_jsonl(args.sample_file)
    packet = blind_packet(rows)
    C.write_jsonl(args.out, packet)
    print('blind packet %d -> %s (self-assessment stripped)' % (len(packet), args.out))
    return 0


def cmd_verify(args):
    meta = None
    if args.sample_meta and os.path.exists(args.sample_meta):
        meta = json.load(open(args.sample_meta, encoding='utf-8'))
    adj = load_adjudication(args.adjudication) if args.adjudication else None
    if adj is not None and args.allow_self_score:
        print('pwg_tm_quality: --allow-self-score is diagnostic only; '
              'independent_gate stays refused', file=sys.stderr)
    report = verify(sample_n=args.sample, adjudication=adj, sample_meta=meta)
    if args.out:
        C.write_json(args.out, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # verify exits 0 when the apparatus is honest, even if the gate is not_run.
    # A fake independent pass exits 1. A real fail exits 1.
    if report['independent_gate'] == 'refused_not_independent':
        return 1
    if report['independent_gate'] == 'fail':
        return 1
    return 0


def _selftest():
    src_rows = []
    classes = list(C.FRAGMENT_CLASSES)
    for i in range(60):
        src_rows.append({
            'fragment_id': 'f%d' % i,
            'fragment_class': classes[i % 6],
            'record_kind': 'fragment',
            'source_string': 'src %d' % i,
            'target_string': 'tgt %d' % i,
            'source_locator': {'key1': 'k%d' % (i % 5), 'lemma_slp1': 'k%d' % (i % 5)},
            'promotion_status': 'promoted' if i % 4 else 'quarantine',
            'gate_status': 'pass' if i % 4 else 'fail',
            'confidence_tier': 'machine_gated' if i % 4 else 'uncertain',
            'generation': {'model_id': 'grok-4.6', 'self_score': 0.99},
        })
    queue = [{'k1': 'k%d' % i, 'count_all': 10 * i, 'stratum': 'attested_high'}
             for i in range(5)]
    picked, meta = freeze_sample(src_rows, queue, n=20, seed=1)
    assert len(picked) == 20, meta
    assert len(meta['by_class']) >= 6 or set(meta['by_class']) <= set(classes)
    packet = blind_packet(picked)
    assert 'generation' not in packet[0]
    assert packet[0]['adjudication']['fidelity'] is None
    # self judge refused
    fake = []
    for row in packet:
        adj = dict(row)
        adj['adjudication'] = {
            'fidelity': 'pass', 'equivalence': 'correct', 'serious_error': False,
            'judge_id': 'grok-4.6', 'judge_model': 'grok-4.6',
        }
        fake.append(adj)
    report = verify(sample_n=20, adjudication=fake, sample_meta=meta)
    assert report['independent_gate'] == 'refused_not_independent', report
    # independent judge, too few labelled
    good = []
    for row in packet:
        adj = dict(row)
        adj['adjudication'] = {
            'fidelity': 'pass', 'equivalence': 'correct', 'serious_error': False,
            'judge_id': 'human:packet', 'judge_model': 'human',
        }
        good.append(adj)
    report2 = verify(sample_n=400, adjudication=good, sample_meta={'complete_n': False,
                                                                   'n_drawn': 20})
    assert report2['independent_gate'] == 'fail', report2
    assert not report2['ok']
    empty = verify(sample_n=400, adjudication=None)
    assert empty['independent_gate'] == 'not_run'
    p, lo, hi = wilson(392, 400)
    assert 0.95 < p < 1.0 and lo < p < hi
    # H3299 rubric pins: same defect class => same severity everywhere
    assert rubric_serious('placeholder_rendered_as_content') is True
    assert rubric_serious('german_residue') is False
    assert rubric_serious('no_such_class') is RUBRIC_UNKNOWN
    consistent = [
        {'fragment_class': 'definition_gloss',
         'adjudication': {'serious_error': True,
                          'defect_class': 'placeholder_rendered_as_content'}},
        {'fragment_class': 'sense',
         'adjudication': {'serious_error': True,
                          'defect_class': 'placeholder_rendered_as_content'}},
        {'fragment_class': 'sense',
         'adjudication': {'serious_error': False, 'defect_class': 'none'}},
    ]
    assert check_severity_consistency(consistent) == []
    # the H2684 inconsistency shape: same class in a second bucket judged
    # non-serious must be a violation, not a judgment call
    flipped = consistent[:1] + [{
        'fragment_class': 'recurring_formula',
        'adjudication': {'serious_error': False,
                         'defect_class': 'placeholder_rendered_as_content'},
    }]
    v = check_severity_consistency(flipped)
    assert len(v) == 1 and 'pinned serious=True' in v[0], v
    unknown = [{'adjudication': {'serious_error': True,
                                 'defect_class': 'mystery'}}]
    assert len(check_severity_consistency(unknown)) == 1
    print('pwg_tm_quality: PASS')
    return 0


def build_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    sub = ap.add_subparsers(dest='cmd')
    p_fr = sub.add_parser('freeze')
    p_fr.add_argument('--in-dir', dest='in_dir', required=True)
    p_fr.add_argument('--inputs', nargs='*')
    p_fr.add_argument('--queue', default=os.path.join(
        C.DEFAULT_OUT_DIR, 'priority_5000.jsonl'))
    p_fr.add_argument('--out', required=True)
    p_fr.add_argument('--sample', type=int, default=SAMPLE_N)
    p_fr.add_argument('--seed', type=int, default=2684)
    p_fr.add_argument('--stream', action='store_true')
    p_pk = sub.add_parser('packet')
    p_pk.add_argument('--sample-file', required=True)
    p_pk.add_argument('--out', required=True)
    p_v = sub.add_parser('verify')
    p_v.add_argument('--sample', type=int, default=SAMPLE_N)
    p_v.add_argument('--adjudication', default=None)
    p_v.add_argument('--sample-meta', default=None)
    p_v.add_argument('--out', default=None)
    p_v.add_argument('--allow-self-score', action='store_true')
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.cmd == 'freeze':
        return cmd_freeze(args)
    if args.cmd == 'packet':
        return cmd_packet(args)
    if args.cmd == 'verify':
        return cmd_verify(args)
    return _selftest()


if __name__ == '__main__':
    sys.exit(main())
