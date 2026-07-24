#!/usr/bin/env python
"""C-49 residual registry helpers — append / check / backfill (H1618).

The durable registry is `no_pwg_residuals.jsonl` (schema `pwg.no_pwg_residual.v1`).
`no_pwg_scale_plan.read_residuals` is the sole consumer for planner skip-lists.
This module:

  * appends blocked rows (idempotent on exact key+status)
  * records defect keys from an audit report as blocked residuals
  * checks that a documented key list is ledgered (test pin)
  * backfills the H255 w02–w05 documented residuals that only lived in RUN_LOG

  python src/pilot/no_pwg_residual_ledger.py selftest
  python src/pilot/no_pwg_residual_ledger.py check
  python src/pilot/no_pwg_residual_ledger.py append-from-audit <report.json> --window <tag>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from no_pwg_scale_plan import RESIDUALS, read_residuals  # noqa: E402
from window_common import append_jsonl_line  # noqa: E402

SCHEMA = 'pwg.no_pwg_residual.v1'

# C-49: documented-deterministic residuals from RUN_LOG (H255 no-PWG drain, 2026-07-10..15).
# Only keys that are retry-RESISTANT / not-to-blind-requeue. Source windows as logged.
DOCUMENTED_RESIDUALS = [
    # w02 (2026-07-14 session) fidelity-reject + STRANDED-ANCHOR + circular-gloss
    {'key': 'avy_ahata~~h0_zz_pw', 'source_window': 'no_pwg_w02',
     'reason': 'fidelity-reject span-drop; retry-resistant (RUN_LOG 2026-07-14)'},
    {'key': 'avyagra~~h0_zz_pw', 'source_window': 'no_pwg_w02',
     'reason': 'fidelity-reject span-drop; retry-resistant (RUN_LOG 2026-07-14)'},
    {'key': 'k_antap_az_a_ra~~h0_zz_pw', 'source_window': 'no_pwg_w02',
     'reason': 'STRANDED-ANCHOR mask-restoration defect (RUN_LOG 2026-07-14)'},
    {'key': 'kajjalik_a~~h0_zz_pw', 'source_window': 'no_pwg_w02',
     'reason': 'STRANDED-ANCHOR mask-restoration defect (RUN_LOG 2026-07-14)'},
    {'key': 'durg_a~~h0_zz_sch', 'source_window': 'no_pwg_w02',
     'reason': 'likely_circular_gloss; needs manual rework (RUN_LOG 2026-07-14)'},
    # w03 requeue residual (2026-07-11) — second-pass residual not requeued again
    {'key': 't_a~~h0_zz_nws00', 'source_window': 'no_pwg_w03',
     'reason': '2x kill-timeout; documented residual not requeued a third time'},
    {'key': 'gagana~~h0_zz_nws00', 'source_window': 'no_pwg_w03',
     'reason': 'STRANDED-ANCHOR/circular-gloss content defect'},
    {'key': 'mahat~~h0_zz_pw', 'source_window': 'no_pwg_w03',
     'reason': 'content defect (circular-gloss / STRANDED-ANCHOR class)'},
    {'key': 'sa_m_dy_a~~h0_zz_sch', 'source_window': 'no_pwg_w03',
     'reason': 'content defect (circular-gloss / STRANDED-ANCHOR class)'},
    # w04 second-null residual
    {'key': '_gawik_a~~h0_zz_nws00', 'source_window': 'no_pwg_w04',
     'reason': '2x kill-timeout; documented residual'},
    {'key': '_kowa~~h0_zz_pw', 'source_window': 'no_pwg_w04',
     'reason': 'selfheal-nothing-resolved after permitted requeue'},
    # w05 second-null residual
    {'key': '_u_das~~h0_zz_pw', 'source_window': 'no_pwg_w05',
     'reason': '2x kill-timeout; documented residual'},
    {'key': '_sibi~~h0_zz_pw', 'source_window': 'no_pwg_w05',
     'reason': '2x selfheal-nothing-resolved'},
    {'key': 'a_sud_da~~h0_zz_pw', 'source_window': 'no_pwg_w05',
     'reason': '2x selfheal-nothing-resolved'},
    {'key': 'aklizwa~~h0_zz_pw', 'source_window': 'no_pwg_w05',
     'reason': '2x selfheal-nothing-resolved'},
]


def utc_now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def make_row(key, reason, source_window, status='blocked', updated_at=None):
    return {
        'schema': SCHEMA,
        'key': key,
        'status': status,
        'reason': reason,
        'source_window': source_window,
        'updated_at': updated_at or utc_now(),
    }


def append_residual(path, key, reason, source_window, status='blocked',
                    updated_at=None, force=False):
    """Append one residual row if the latest status for `key` is not already `status`
    (unless force). Returns True when a row was written."""
    latest = read_residuals(path)
    cur = latest.get(key)
    if cur and cur.get('status') == status and not force:
        return False
    row = make_row(key, reason, source_window, status=status, updated_at=updated_at)
    os.makedirs(os.path.dirname(os.path.abspath(path)) or '.', exist_ok=True)
    append_jsonl_line(path, row)
    return True


def append_from_audit_report(report_path, source_window, path=RESIDUALS,
                             reason_prefix='audit defect'):
    """Record every requeue_defect key (and fidelity-resistant nulls if present) as blocked."""
    with open(report_path, encoding='utf-8') as f:
        report = json.load(f)
    keys = list(report.get('requeue_defect') or [])
    # Also accept EN-style hard_keys when requeue_defect is absent.
    if not keys:
        keys = list(report.get('hard_keys') or [])
    n = 0
    for key in keys:
        if append_residual(
                path, key,
                reason='%s (%s)' % (reason_prefix, source_window),
                source_window=source_window):
            n += 1
    return n, keys


def backfill_documented(path=RESIDUALS, documented=None):
    documented = documented if documented is not None else DOCUMENTED_RESIDUALS
    written = 0
    for row in documented:
        if append_residual(
                path, row['key'], row['reason'], row['source_window'],
                status='blocked', updated_at=row.get('updated_at') or '2026-07-15T00:00:00Z'):
            written += 1
    return written, len(documented)


def check_documented_are_ledgered(path=RESIDUALS, documented=None):
    """Return (ok, missing_keys). missing is empty when every documented key is blocked."""
    documented = documented if documented is not None else DOCUMENTED_RESIDUALS
    latest = read_residuals(path)
    missing = []
    for row in documented:
        key = row['key']
        cur = latest.get(key)
        if not cur or cur.get('status') != 'blocked':
            missing.append(key)
    return (not missing), missing


def selftest():
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, 'residuals.jsonl')
        assert append_residual(path, 'k1~~h0_zz_pw', 'r1', 'w02') is True
        assert append_residual(path, 'k1~~h0_zz_pw', 'r1-again', 'w02') is False
        assert append_residual(path, 'k1~~h0_zz_pw', 'r1-force', 'w02', force=True) is True
        latest = read_residuals(path)
        assert latest['k1~~h0_zz_pw']['reason'] == 'r1-force'
        # backfill + check against a tiny documented set
        doc = [{'key': 'a~~h0_zz_pw', 'reason': 'x', 'source_window': 'no_pwg_w02'},
               {'key': 'b~~h0_zz_pw', 'reason': 'y', 'source_window': 'no_pwg_w03'}]
        w, total = backfill_documented(path, doc)
        assert w == 2 and total == 2, (w, total)
        ok, missing = check_documented_are_ledgered(path, doc)
        assert ok and not missing, missing
        # simulate report append
        rep = os.path.join(td, 'audit_window.report.json')
        with open(rep, 'w', encoding='utf-8') as f:
            json.dump({'requeue_defect': ['c~~h0_zz_pw']}, f)
        n, keys = append_from_audit_report(rep, 'no_pwg_w04', path=path)
        assert n == 1 and keys == ['c~~h0_zz_pw']
        assert 'c~~h0_zz_pw' in read_residuals(path)
    print('no_pwg_residual_ledger selftest: PASS')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('cmd', choices=('selftest', 'check', 'backfill', 'append-from-audit'))
    ap.add_argument('report', nargs='?', help='audit report JSON for append-from-audit')
    ap.add_argument('--window', default='', help='source_window tag for append-from-audit')
    ap.add_argument('--path', default=RESIDUALS)
    args = ap.parse_args(argv)
    if args.cmd == 'selftest':
        return selftest()
    if args.cmd == 'backfill':
        w, total = backfill_documented(args.path)
        print('backfill: wrote %d of %d documented residual(s) to %s' % (w, total, args.path))
        return 0
    if args.cmd == 'check':
        ok, missing = check_documented_are_ledgered(args.path)
        if ok:
            print('check: all %d documented residuals are ledgered blocked' %
                  len(DOCUMENTED_RESIDUALS))
            return 0
        print('check FAIL: missing blocked residual(s): %s' % ', '.join(missing))
        return 1
    if args.cmd == 'append-from-audit':
        if not args.report or not args.window:
            ap.error('append-from-audit needs <report.json> and --window')
        n, keys = append_from_audit_report(args.report, args.window, path=args.path)
        print('append-from-audit: +%d blocked residual(s) from %d defect key(s)'
              % (n, len(keys)))
        return 0
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
