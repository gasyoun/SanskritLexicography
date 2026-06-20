#!/usr/bin/env python
"""Compact non-mutating preflight for the remaining print gates."""
import argparse
import csv
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))


def run(label, cmd, ok_codes=(0,)):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180)
    status = 'ok' if r.returncode in ok_codes else 'fail'
    detail = (r.stdout.strip() or r.stderr.strip()).splitlines()
    return label, status, detail[-1] if detail else ''


def review_state():
    path = os.path.join(HERE, '_review_queue.csv')
    rows = decisions = 0
    if os.path.exists(path):
        with open(path, encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                if not any((v or '').strip() for v in row.values()):
                    continue
                rows += 1
                decisions += 1 if (row.get('decision') or '').strip() else 0
    return 'blocked', 'review decisions %d/%d' % (decisions, rows)


def gold_state():
    path = os.path.join(ROOT, 'gold', '_human_gold_review.csv')
    rows = complete = 0
    if os.path.exists(path):
        with open(path, encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                rows += 1
                complete += 1 if all((row.get(field) or '').strip()
                                      for field in ('human_label', 'reviewer_id',
                                                    'confidence', 'needs_adjudication')) else 0
    return 'blocked', 'gold complete %d/%d' % (complete, rows)


def roadmap_blockers():
    path = os.path.join(ROOT, 'roadmap', 'quality_gates.jsonl')
    blockers = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                if row.get('blocks_print') and row.get('status') != 'passing':
                    blockers.append(row['id'])
    return blockers


def skipped(label, detail):
    return label, 'blocked', detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--release-dir', default=os.path.join(ROOT, 'release'))
    ap.add_argument('--readiness-out', default=os.path.join(ROOT, 'release', 'readiness_report.md'))
    ap.add_argument('--skip-local-human-artifacts', action='store_true',
                    help='fixture mode: skip local review/gold CSV validators')
    args = ap.parse_args()
    checks = [run('roadmap_check', [sys.executable, os.path.join(HERE, 'roadmap_check.py')])]
    if args.skip_local_human_artifacts:
        checks.append(skipped('validate_review', 'skipped fixture mode; human review CSV is local'))
        checks.append(skipped('gold_status', 'skipped fixture mode; human gold CSV is local'))
    else:
        checks.append(run('validate_review', [sys.executable, os.path.join(HERE, 'run_batch.py'),
                                              'validate_review']))
        checks.append(run('gold_status', [sys.executable, os.path.join(HERE, 'gold_status.py'),
                                          os.path.join(ROOT, 'gold', '_human_gold_review.csv')]))
    checks.extend([
        run('validate_interop', [sys.executable, os.path.join(HERE, 'validate_interop.py'),
                                 '--dir', args.release_dir]),
        run('release_readiness', [sys.executable, os.path.join(HERE, 'release_readiness.py'),
                                  '--release-dir', args.release_dir, '--out', args.readiness_out]),
    ])
    checks.append(('G5 review',) + review_state())
    checks.append(('G6 gold',) + gold_state())
    blockers = roadmap_blockers()
    checks.append(('roadmap blockers', 'blocked' if blockers else 'ok', ', '.join(blockers) or 'none'))
    print('| check | status | detail |')
    print('|---|---|---|')
    failed = False
    for label, status, detail in checks:
        print('| %s | %s | %s |' % (label, status, str(detail).replace('|', '\\|')[:180]))
        failed = failed or status == 'fail'
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
