#!/usr/bin/env python
r"""Lane halt rule + revert (H2175 step 7, ruling R4.1).

Evaluates one day's ``spotcheck_<date>.json`` (spot_check_daily.py) for one lane:

    >= 2 sev-3 defects in the day  OR  ANY SAN-LOSS reaching the store
        -> FREEZE the lane and REVERT its unreviewed auto-promoted windows.
    1 sev-3 -> no freeze (the calibrated threshold; a single defect is queue food).

Freeze = a durable ``lane_freeze_<lane>.json`` (schema ``pwg.lane_freeze.v1``) in
--freeze-dir; nonstop_scheduler.py refuses a frozen lane at tick time (other lanes
keep ticking — the freeze is per-lane by construction). Unfreezing is a HUMAN act:
delete the file after the weekly review rules on the defects.

Revert = for every ``pwg.auto_promotion.v1`` record of that day (the lane's
unreviewed windows), remove the affected subcards' store rows and quarantine them
to a JSONL next to the freeze record, with the promoter's own primitives (fsynced
backup + atomic row write). Two hard fences, both non-negotiable:
  * a row ``promote_final_cards.human_touched()`` protects is NEVER removed —
    reverting machine output must not delete a human ruling (H2146 / FINDINGS §513);
  * default is DRY-RUN; ``--execute`` performs the store write.
The reverted keys land in a ``*.requeue.keys.txt`` worklist (the autosplit_requeue
evidence convention) so the next healthy window re-earns them honestly.
"""
import argparse
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

from store_path import canonical_store            # noqa: E402
import promote_final_cards as pfc                 # noqa: E402
from promote_lock import PromoteClaim              # noqa: E402
import spot_check_daily as scd                    # noqa: E402

SCHEMA = 'pwg.lane_freeze.v1'
SEV3_FREEZE_THRESHOLD = 2      # R4.1: >=2 sev-3/day freezes; 1 does not


def freeze_path(freeze_dir, lane):
    return os.path.join(freeze_dir, 'lane_freeze_%s.json' % lane)


def frozen(freeze_dir, lane):
    """Scheduler-facing check: is this lane frozen? (the file IS the state)"""
    return os.path.exists(freeze_path(freeze_dir, lane))


def evaluate(report):
    """Pure R4.1 verdict over a spotcheck report -> (freeze: bool, reasons: [str])."""
    reasons = []
    if (report.get('sev3_count') or 0) >= SEV3_FREEZE_THRESHOLD:
        reasons.append('%d sev-3 defects in the day (threshold %d)'
                       % (report['sev3_count'], SEV3_FREEZE_THRESHOLD))
    if report.get('san_loss_in_store'):
        reasons.append('SAN-LOSS reached the store (unconditional freeze)')
    return bool(reasons), reasons


def revert_windows(records, store, quarantine_path, execute=False):
    """Remove the day's auto-promoted subcards from the store (unprotected rows only).

    Returns (removed_rows, protected_subcards, affected_keys). With execute=False
    nothing is written — the same lists are computed for the dry-run report."""
    keys = set(scd.promoted_keys(records))
    if not keys or not os.path.exists(store):
        return [], [], sorted(keys)

    def read_and_partition():
        with open(store, encoding='utf-8') as f:
            rows = [json.loads(line) for line in f if line.strip()]
        return _partition(rows, keys)

    if not execute:
        # Dry run is a pure read: no claim is taken, and none is needed. Holding the
        # promote claim just to compute a report would block live promotes for nothing.
        removed, _kept, protected = read_and_partition()
        return removed, sorted(protected), sorted(keys)

    # H3748 (#1800 C5-3): an EXECUTING revert is a whole-store rewrite, and it took no
    # claim at all — it read, filtered, and called pfc._atomic_write_rows with nothing
    # serializing it against a concurrent promote. That is precisely the
    # read-existing-store / merge / os.replace window promote_lock.py exists to guard,
    # so it now takes the same claim, across the READ as well as the write. ClaimBusy
    # propagates deliberately: a revert that cannot serialize must fail loudly rather
    # than race the promote it is reverting.
    with PromoteClaim(store):
        removed, kept, protected = read_and_partition()
        if removed:
            backup = pfc._backup_path(store, 'lane_guard_revert')
            pfc._fsynced_backup(store, backup)
            with open(quarantine_path, 'w', encoding='utf-8', newline='\n') as f:
                for row in removed:
                    f.write(json.dumps(row, ensure_ascii=False) + '\n')
            pfc._atomic_write_rows(store, kept)
    return removed, sorted(protected), sorted(keys)


def _partition(rows, keys):
    """(removed, kept, protected_subcards) — the selection logic, unchanged and pure."""

    def affected(row):
        sub = row.get('subcard') or ''
        return sub in keys or sub.split('~~', 1)[0] in keys

    removed, kept, protected = [], [], set()
    for row in rows:
        if affected(row):
            if pfc.human_touched(row):
                protected.add(row.get('subcard'))
                kept.append(row)          # a human ruling outlives the machine revert
            else:
                removed.append(row)
        else:
            kept.append(row)
    return removed, kept, protected


def run(args):
    report = json.load(open(args.spotcheck, encoding='utf-8'))
    date = report.get('date')
    freeze, reasons = evaluate(report)
    if not freeze:
        print('lane %s: no freeze (sev3=%s, san_loss_in_store=%s) — R4.1 threshold not met'
              % (args.lane, report.get('sev3_count'), report.get('san_loss_in_store')))
        return 0
    os.makedirs(args.freeze_dir, exist_ok=True)
    records = scd.day_promotion_records(args.records_dir, date) if args.records_dir else []
    quarantine = os.path.join(args.freeze_dir,
                              'lane_revert_%s_%s.quarantine.jsonl' % (args.lane, date))
    store = args.store or canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl'))
    removed, protected, keys = revert_windows(records, store, quarantine,
                                              execute=args.execute)
    requeue = os.path.join(args.freeze_dir,
                           'lane_revert_%s_%s.requeue.keys.txt' % (args.lane, date))
    if args.execute:
        with open(requeue, 'w', encoding='utf-8', newline='\n') as f:
            for k in keys:
                f.write(k + '\n')
    record = {
        'schema': SCHEMA, 'lane': args.lane, 'date': date,
        'frozen_at': int(time.time()), 'reasons': reasons,
        'spotcheck': os.path.abspath(args.spotcheck),
        'windows_reverted': [r.get('lease_id') for r in records],
        'rows_removed': len(removed), 'protected_subcards': protected,
        'requeue_worklist': os.path.abspath(requeue),
        'quarantine': os.path.abspath(quarantine),
        'executed': bool(args.execute),
        'unfreeze': 'HUMAN act: delete this file after the weekly review rules on it',
    }
    fp = freeze_path(args.freeze_dir, args.lane)
    tmp = fp + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(record, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, fp)
    mode = 'EXECUTED' if args.execute else 'DRY-RUN (pass --execute to revert)'
    print('lane %s FROZEN [%s]: %s; %d rows reverted, %d protected subcards kept -> %s'
          % (args.lane, mode, '; '.join(reasons), len(removed), len(protected), fp))
    return 2


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lane', help='lane name (pc | prod | routine | ...)')
    ap.add_argument('--spotcheck', help='spotcheck_<date>.json from spot_check_daily.py')
    ap.add_argument('--freeze-dir', help='where lane_freeze/quarantine/requeue land '
                                         '(gatelogs dir of the data root)')
    ap.add_argument('--records-dir', help='dir holding the day\'s *.PROMOTED.json records')
    ap.add_argument('--store', default=None)
    ap.add_argument('--execute', action='store_true',
                    help='perform the store revert (default: dry-run report only)')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.lane and args.spotcheck and args.freeze_dir):
        ap.error('--lane, --spotcheck and --freeze-dir are required (unless --selftest)')
    return run(args)


def selftest():
    import tempfile

    def mk_report(td, sev3, san):
        p = os.path.join(td, 'spotcheck_t.json')
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'schema': scd.SCHEMA, 'date': scd.utc_date(time.time()),
                       'sev3_count': sev3, 'san_loss_in_store': san, 'defects': []}, f)
        return p

    with tempfile.TemporaryDirectory() as td:
        # (1) pure verdicts: 2 sev-3 freeze; 1 no-freeze; SAN-LOSS unconditional
        assert evaluate({'sev3_count': 2, 'san_loss_in_store': False})[0]
        assert not evaluate({'sev3_count': 1, 'san_loss_in_store': False})[0]
        assert evaluate({'sev3_count': 0, 'san_loss_in_store': True})[0]

        # (2) end-to-end: synthetic store + promotion records; 2 sev-3 -> freeze,
        # revert removes machine rows, keeps the human-touched row, writes worklists
        now = int(time.time())
        scd._mk_promotion(td, 'wA', ['r~~a', 'r~~b'], now)
        store = os.path.join(td, 'store.jsonl')
        rows = [
            {'subcard': 'r~~a', 'ru': 'x', 'review_status': 'ai_translated',
             'reviewer': None},
            {'subcard': 'r~~b', 'ru': 'y', 'review_status': 'approved',
             'reviewer': 'MG'},                      # human-touched -> protected
            {'subcard': 'other~~z', 'ru': 'z', 'review_status': 'ai_translated'},
        ]
        with open(store, 'w', encoding='utf-8', newline='\n') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        fdir = os.path.join(td, 'freeze')
        ns = argparse.Namespace(lane='pc', spotcheck=mk_report(td, 2, False),
                                freeze_dir=fdir, records_dir=td, store=store,
                                execute=True)
        assert run(ns) == 2
        assert frozen(fdir, 'pc') and not frozen(fdir, 'prod')   # per-lane freeze
        left = [json.loads(l) for l in open(store, encoding='utf-8')]
        subs = {r['subcard'] for r in left}
        assert subs == {'r~~b', 'other~~z'}, subs   # machine row gone, human + unrelated stay
        frz = json.load(open(freeze_path(fdir, 'pc'), encoding='utf-8'))
        assert frz['rows_removed'] == 1 and frz['protected_subcards'] == ['r~~b']
        q = [json.loads(l) for l in open(frz['quarantine'], encoding='utf-8')]
        assert len(q) == 1 and q[0]['subcard'] == 'r~~a'         # evidence retained
        wl = open(frz['requeue_worklist'], encoding='utf-8').read().split()
        assert set(wl) == {'r~~a', 'r~~b'}, wl
        backups = [f for f in os.listdir(td)
                   if f.startswith('store.jsonl.premerge.') and f.endswith('.bak')]
        assert backups, 'store backup missing before revert write'

        # (3) 1 sev-3 -> no freeze file for a fresh lane
        ns2 = argparse.Namespace(lane='prod', spotcheck=mk_report(td, 1, False),
                                 freeze_dir=fdir, records_dir=td, store=store,
                                 execute=True)
        assert run(ns2) == 0 and not frozen(fdir, 'prod')

        # (4) dry-run: freeze verdict recorded, store untouched
        store2 = os.path.join(td, 'store2.jsonl')
        with open(store2, 'w', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps({'subcard': 'r~~a', 'ru': 'x',
                                'review_status': 'ai_translated'}) + '\n')
        ns3 = argparse.Namespace(lane='routine', spotcheck=mk_report(td, 0, True),
                                 freeze_dir=fdir, records_dir=td, store=store2,
                                 execute=False)
        assert run(ns3) == 2 and frozen(fdir, 'routine')
        assert len(open(store2, encoding='utf-8').readlines()) == 1, 'dry-run wrote store'
    print('lane_guard selftest: PASS (R4.1 thresholds, freeze+revert with human-row '
          'protection + quarantine + requeue worklist + backup, per-lane isolation, '
          'dry-run safety)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
