#!/usr/bin/env python
r"""Daily spot-check of auto-promoted cards (H2175 step 6, halt rule R4.1 input).

Samples a deterministic 10% (--fraction) of the cards a day's auto-promotions landed
in the store, re-runs the deterministic per-card gates on the STORE rows (what
actually landed, not what the window claimed), optionally runs one judge pass per
sampled card, and writes ``spotcheck_<date>.json`` to the telemetry dir. The
companion ``lane_guard.py`` evaluates the R4.1 halt rule over this report:
>=2 sev-3 defects in a day, or ANY SAN-LOSS reaching the store, freezes the lane.

Population source: the ``pwg.auto_promotion.v1`` records (``*.PROMOTED.json``,
written by bounded_staged_run.auto_promote_window) found under --records-dir whose
``promoted_at`` falls on --date (UTC). Their AWAITING_REVIEW checkpoints carry the
exact selected keys, so the sample frame is the day's promoted subcards.

Severity vocabulary (deterministic checks):
  sev-3  SAN-LOSS / UNMAPPED literal in a content field; unrestored {Tn} mask
         placeholder; empty russian on a promoted row  — store-corrupting classes.
  sev-2  sense-count shortfall vs the card's recorded source senses; missing
         h/grammar on a row.
  sev-1  layer field outside the known vocabulary.

The judge pass is a HOOK: --judge-cmd is a shell template invoked once per sampled
card with ``{payload}`` replaced by a JSON payload path; it must print a JSON object
``{"severity": 0..3, "notes": "..."}``. Absent --judge-cmd the report records
``judge: skipped`` — the deterministic half still runs (the lanes wire a real judge
per experiment E2). A failing/unparseable judge is recorded as ``judge_error`` and
counts as INCONCLUSIVE, never as PASS (missing evidence is not evidence).
"""
import argparse
import glob
import json
import math
import os
import random
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

from store_path import canonical_store  # noqa: E402

SCHEMA = 'pwg.spotcheck_daily.v1'

# single-sourced content policies (promote_final_cards owns TN_RE; canary_gate owns
# the SAN-LOSS literal class) — import, never restate (H2158 lesson).
import promote_final_cards as pfc  # noqa: E402

SAN_LOSS_RE = re.compile(r'SAN-LOSS|UNMAPPED')
CONTENT_FIELDS = pfc.CONTENT_MASS_FIELDS
KNOWN_LAYERS = ('pwg', 'pw', 'sch', 'pwkvn', 'nws')


def utc_date(ts):
    return time.strftime('%Y-%m-%d', time.gmtime(ts))


def day_promotion_records(records_dir, date):
    """All pwg.auto_promotion.v1 records under records_dir promoted on `date` (UTC)."""
    out = []
    pattern = os.path.join(records_dir, '**', '*.PROMOTED.json')
    for path in sorted(glob.glob(pattern, recursive=True)):
        try:
            rec = json.load(open(path, encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if rec.get('schema') != 'pwg.auto_promotion.v1':
            continue
        if utc_date(rec.get('promoted_at') or 0) == date:
            rec['_path'] = path
            out.append(rec)
    return out


def promoted_keys(records):
    """The day's promoted subcard keys: union of each record's checkpoint selected_keys."""
    keys = set()
    for rec in records:
        cp = rec.get('awaiting_review_checkpoint')
        try:
            payload = json.load(open(cp, encoding='utf-8'))['payload']
            keys.update(payload['bound']['selected_keys'] or [])
        except (OSError, ValueError, KeyError, TypeError):
            # checkpoint gone/unreadable -> fall back to the lease id so the window is
            # still represented in the sample frame rather than silently invisible
            if rec.get('lease_id'):
                keys.add(rec['lease_id'])
    return sorted(keys)


def sample_keys(keys, fraction, date):
    """Deterministic sample: seeded by the date so a re-run reproduces the same draw."""
    if not keys:
        return []
    n = max(1, math.ceil(len(keys) * fraction))
    rng = random.Random('spotcheck:' + date)
    return sorted(rng.sample(keys, min(n, len(keys))))


def store_rows_for(store, keys):
    """subcard/root -> its store rows. One pass; keys match subcard exactly or by root
    prefix (a lease id fallback covers all of its subcards)."""
    wanted = set(keys)
    rows_by_key = {k: [] for k in keys}
    if not os.path.exists(store):
        return rows_by_key
    with open(store, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            sub = row.get('subcard') or ''
            if sub in wanted:
                rows_by_key[sub].append(row)
                continue
            root = sub.split('~~', 1)[0]
            if root in wanted:
                rows_by_key[root].append(row)
    return rows_by_key


def check_card(key, rows):
    """Deterministic per-card gate suite over STORE rows. Returns a defect list."""
    defects = []
    if not rows:
        defects.append({'key': key, 'severity': 3, 'check': 'presence',
                        'detail': 'no store rows found for a promoted key'})
        return defects
    total_senses = None
    for row in rows:
        prov = row.get('provenance') or {}
        if prov.get('total_senses'):
            total_senses = prov['total_senses']
        for field in CONTENT_FIELDS:
            value = row.get(field)
            if not isinstance(value, str):
                continue
            if pfc.TN_RE.search(value):
                defects.append({'key': key, 'severity': 3, 'check': 'tn_residue',
                                'detail': 'unrestored {Tn} in %s' % field})
            if field in ('ru', 'en') and SAN_LOSS_RE.search(value):
                defects.append({'key': key, 'severity': 3, 'check': 'san_loss',
                                'detail': 'SAN-LOSS/UNMAPPED literal in %s' % field})
        if not (row.get('ru') or row.get('en')):
            defects.append({'key': key, 'severity': 3, 'check': 'empty_translation',
                            'detail': 'promoted row with no ru/en content'})
        if not row.get('h') or not row.get('grammar'):
            defects.append({'key': key, 'severity': 2, 'check': 'row_fields',
                            'detail': 'missing h/grammar on a promoted row'})
        if row.get('layer') not in KNOWN_LAYERS:
            defects.append({'key': key, 'severity': 1, 'check': 'layer_vocab',
                            'detail': 'layer %r outside %s' % (row.get('layer'),
                                                               '/'.join(KNOWN_LAYERS))})
    if total_senses and len(rows) < 0.8 * total_senses:
        defects.append({'key': key, 'severity': 2, 'check': 'sense_shortfall',
                        'detail': 'rows %d < 80%% of recorded source senses %d'
                                  % (len(rows), total_senses)})
    return defects


def store_san_loss_scan(store):
    """ANY SAN-LOSS/UNMAPPED literal anywhere in the store's ru/en fields (R4.1's
    unconditional freeze trigger) — full scan, not sample-bounded."""
    hits = []
    if not os.path.exists(store):
        return hits
    with open(store, encoding='utf-8') as f:
        for line in f:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            for field in ('ru', 'en'):
                value = row.get(field)
                if isinstance(value, str) and SAN_LOSS_RE.search(value):
                    hits.append({'subcard': row.get('subcard'), 'field': field})
    return hits


def judge_card(judge_cmd, key, rows, workdir):
    """One judge pass for one sampled card via the --judge-cmd template. Returns a
    judge dict; failures are judge_error (INCONCLUSIVE), never silently clean."""
    payload_path = os.path.join(workdir, 'judge_payload_%d.json' % abs(hash(key)))
    with open(payload_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'key': key, 'rows': rows}, f, ensure_ascii=False, indent=1)
    cmd = judge_cmd.replace('{payload}', payload_path)
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              encoding='utf-8', timeout=600)
        verdict = json.loads(proc.stdout.strip().splitlines()[-1])
        sev = int(verdict.get('severity'))
        assert 0 <= sev <= 3
        return {'key': key, 'severity': sev, 'notes': verdict.get('notes'),
                'status': 'judged'}
    except Exception as exc:  # noqa: BLE001 — any judge failure is inconclusive
        return {'key': key, 'status': 'judge_error', 'detail': str(exc)[:500]}


def build_report(date, fraction, records_dir, store, judge_cmd=None, workdir=None):
    records = day_promotion_records(records_dir, date)
    population = promoted_keys(records)
    sampled = sample_keys(population, fraction, date)
    rows_by_key = store_rows_for(store, sampled)
    defects = []
    for key in sampled:
        defects.extend(check_card(key, rows_by_key.get(key) or []))
    san_hits = store_san_loss_scan(store)
    judge_results = []
    if judge_cmd:
        for key in sampled:
            judge_results.append(judge_card(judge_cmd, key, rows_by_key.get(key) or [],
                                            workdir or os.getcwd()))
            sev = judge_results[-1].get('severity')
            if judge_results[-1]['status'] == 'judged' and sev == 3:
                defects.append({'key': key, 'severity': 3, 'check': 'judge',
                                'detail': judge_results[-1].get('notes') or 'judge sev-3'})
    sev3 = [d for d in defects if d['severity'] == 3]
    return {
        'schema': SCHEMA,
        'date': date,
        'generated_at': int(time.time()),
        'fraction': fraction,
        'promotion_records': [r['_path'] for r in records],
        'population': len(population),
        'sampled': sampled,
        'defects': defects,
        'sev3_count': len(sev3),
        'san_loss_in_store': bool(san_hits),
        'san_loss_hits': san_hits[:100],
        'judge': ({'cmd_template': judge_cmd, 'results': judge_results} if judge_cmd
                  else 'skipped'),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--date', default=utc_date(time.time()), help='UTC date, default today')
    ap.add_argument('--fraction', type=float, default=0.10)
    ap.add_argument('--records-dir',
                    help='dir walked recursively for *.PROMOTED.json auto-promotion '
                         'records (the bounded-run manifests/checkpoint dir)')
    ap.add_argument('--store', default=None,
                    help='store path (default: canonical resolution incl. $PWG_RU_STORE)')
    ap.add_argument('--out-dir',
                    help='telemetry dir the spotcheck_<date>.json report lands in')
    ap.add_argument('--judge-cmd', default=None,
                    help='shell template run once per sampled card; {payload} is replaced '
                         'by a JSON payload path; must print {"severity":0..3,...}')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.records_dir and args.out_dir):
        ap.error('--records-dir and --out-dir are required (unless --selftest)')
    store = args.store or canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl'))
    os.makedirs(args.out_dir, exist_ok=True)
    report = build_report(args.date, args.fraction, args.records_dir, store,
                          judge_cmd=args.judge_cmd, workdir=args.out_dir)
    out = os.path.join(args.out_dir, 'spotcheck_%s.json' % args.date)
    tmp = out + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, out)
    print('spot-check %s: population=%d sampled=%d sev3=%d san_loss_in_store=%s -> %s'
          % (args.date, report['population'], len(report['sampled']),
             report['sev3_count'], report['san_loss_in_store'], out))
    # exit 1 when the R4.1 inputs are non-clean so a scheduler can gate cheaply;
    # lane_guard.py remains the authority on freezing.
    return 1 if (report['sev3_count'] or report['san_loss_in_store']) else 0


def _mk_promotion(td, name, keys, promoted_at):
    cp = os.path.join(td, name + '.AWAITING_REVIEW.w.json')
    payload = {'schema': 'pwg.awaiting_review.v1', 'bound': {'selected_keys': keys}}
    with open(cp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'payload': payload, 'payload_sha256': 'x'}, f)
    rec = {'schema': 'pwg.auto_promotion.v1', 'promoted_at': promoted_at,
           'lease_id': name, 'awaiting_review_checkpoint': cp}
    with open(cp + '.PROMOTED.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(rec, f)
    return cp


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        now = int(time.time())
        today = utc_date(now)
        # population: two windows promoted today, one yesterday (excluded)
        _mk_promotion(td, 'w1', ['rootA~~a', 'rootA~~b'], now)
        _mk_promotion(td, 'w2', ['rootB~~c'], now)
        _mk_promotion(td, 'w0', ['old~~z'], now - 86400 * 2)
        store = os.path.join(td, 'store.jsonl')
        rows = [
            {'subcard': 'rootA~~a', 'ru': 'чистый', 'h': 'a', 'grammar': 'm', 'layer': 'pwg',
             'provenance': {'total_senses': 1}},
            {'subcard': 'rootA~~b', 'ru': 'плохой {T3}', 'h': 'b', 'grammar': 'm',
             'layer': 'pwg'},                                  # sev-3 tn_residue
            {'subcard': 'rootB~~c', 'ru': 'x SAN-LOSS y', 'h': 'c', 'grammar': 'f',
             'layer': 'zzz'},                                  # sev-3 san_loss + sev-1 layer
        ]
        with open(store, 'w', encoding='utf-8', newline='\n') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        # fraction 1.0 -> whole population sampled deterministically
        rep = build_report(today, 1.0, td, store)
        assert rep['population'] == 3 and set(rep['sampled']) == \
            {'rootA~~a', 'rootA~~b', 'rootB~~c'}, rep['sampled']
        checks = {(d['key'], d['check']) for d in rep['defects']}
        assert ('rootA~~b', 'tn_residue') in checks, checks
        assert ('rootB~~c', 'san_loss') in checks, checks
        assert ('rootB~~c', 'layer_vocab') in checks, checks
        assert not any(d['key'] == 'rootA~~a' and d['severity'] == 3
                       for d in rep['defects']), 'clean card flagged'
        assert rep['sev3_count'] >= 2 and rep['san_loss_in_store'] is True
        assert rep['judge'] == 'skipped'
        # determinism: same date -> same sample
        rep2 = build_report(today, 1.0, td, store)
        assert rep2['sampled'] == rep['sampled']
        # judge hook: a sev-3 judge verdict lands as a defect; a broken judge is
        # judge_error (inconclusive), not silently clean
        judge_ok = '%s -c "import json;print(json.dumps({\'severity\':3,\'notes\':\'reg\'}))"' \
            % json.dumps(sys.executable)
        rep3 = build_report(today, 1.0, td, store, judge_cmd=judge_ok, workdir=td)
        assert any(d['check'] == 'judge' for d in rep3['defects'])
        rep4 = build_report(today, 1.0, td, store,
                            judge_cmd=json.dumps(sys.executable) + ' -c "print(41+"',
                            workdir=td)
        assert all(j['status'] == 'judge_error' for j in rep4['judge']['results'])
        # a promoted key with NO store rows is a sev-3 presence defect
        _mk_promotion(td, 'w3', ['ghost~~g'], now)
        rep5 = build_report(today, 1.0, td, store)
        assert ('ghost~~g', 'presence') in {(d['key'], d['check']) for d in rep5['defects']}
    print('spot_check_daily selftest: PASS (day scoping, deterministic sample, gate '
          'suite severities, store SAN-LOSS scan, judge hook + inconclusive-on-error, '
          'ghost-key presence)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
