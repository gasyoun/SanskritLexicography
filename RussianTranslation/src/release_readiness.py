#!/usr/bin/env python
"""Write a release readiness report without cutting an edition."""
import csv
import json
import argparse
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_REPORT = os.path.join(ROOT, 'release', 'readiness_report.md')
GATES = os.path.join(ROOT, 'roadmap', 'quality_gates.jsonl')
REVIEW_CSV = os.environ.get('PWG_RU_REVIEW_CSV') or os.path.join(HERE, '_review_queue.csv')
STORE = os.environ.get('PWG_RU_STORE') or os.path.join(HERE, 'pwg_ru_translated.jsonl')
GOLD_CSV = os.path.join(ROOT, 'gold', '_human_gold_review.csv')
GOLD_LABELS = os.path.join(ROOT, 'gold', 'human_gold_labels.jsonl')
DOUBLE_REPORT = os.path.join(ROOT, 'gold', 'double_review_agreement.md')
G10 = 'G10_immutable_edition_cut'


def read_gates():
    rows = []
    with open(GATES, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def review_counts():
    out = {'rows': 0, 'decisions': 0, 'print_ready': 0}
    if os.path.exists(REVIEW_CSV):
        with open(REVIEW_CSV, encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                if not any((v or '').strip() for v in row.values()):
                    continue
                out['rows'] += 1
                if (row.get('decision') or '').strip():
                    out['decisions'] += 1
    if os.path.exists(STORE):
        with open(STORE, encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                if (row.get('review_status') in {'approved', 'human_reviewed'}
                        and row.get('ok') and row.get('placeholders_ok') and row.get('key_match')):
                    out['print_ready'] += 1
    return out


def gold_counts():
    out = {'rows': 0, 'complete': 0, 'labels_jsonl': 0}
    if os.path.exists(GOLD_CSV):
        with open(GOLD_CSV, encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                out['rows'] += 1
                if all((row.get(field) or '').strip()
                       for field in ('human_label', 'reviewer_id', 'confidence', 'needs_adjudication')):
                    out['complete'] += 1
    if os.path.exists(GOLD_LABELS):
        with open(GOLD_LABELS, encoding='utf-8') as f:
            out['labels_jsonl'] = sum(1 for line in f if line.strip())
    return out


def interop_ok(release_dir):
    r = subprocess.run([sys.executable, os.path.join(HERE, 'validate_interop.py'),
                        '--dir', release_dir],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


def local_gate_blockers(review, gold, double_exists):
    blockers = []
    if review['print_ready'] == 0:
        blockers.append('G5_translation_store_review_gate')
    if gold['complete'] < gold['rows'] or not gold['rows']:
        blockers.append('G6_human_gold_set')
    if not double_exists:
        blockers.append('G7_double_review_agreement')
    return blockers


def edition_blockers(blocking, review, gold, double_exists):
    return sorted((set(blocking) - {G10}) |
                  set(local_gate_blockers(review, gold, double_exists)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--release-dir', default=os.path.join(ROOT, 'release'))
    ap.add_argument('--out', default=DEFAULT_REPORT)
    ap.add_argument('--fail-on-blocked', action='store_true',
                    help='exit 1 when release blockers remain; default is report-only')
    args = ap.parse_args()
    gates = read_gates()
    blocking = [g['id'] for g in gates if g.get('blocks_print') and g.get('status') != 'passing']
    rc = review_counts()
    gc = gold_counts()
    iok, imsg = interop_ok(args.release_dir)
    double_exists = os.path.exists(DOUBLE_REPORT)
    eblockers = edition_blockers(blocking, rc, gc, double_exists)
    lines = [
        '# Release readiness report',
        '',
        '| item | status | detail |',
        '|---|---|---|',
        '| Roadmap blockers | %s | %s |' % ('blocked' if blocking else 'ready', ', '.join(blocking) or 'none'),
        '| G5 review decisions | %s | rows=%d decisions=%d print_ready=%d |'
        % ('blocked' if rc['print_ready'] == 0 else 'partial/ready', rc['rows'], rc['decisions'], rc['print_ready']),
        '| G6 human gold labels | %s | csv_rows=%d complete=%d labels_jsonl=%d |'
        % ('blocked' if gc['complete'] < gc['rows'] or not gc['rows'] else 'ready',
           gc['rows'], gc['complete'], gc['labels_jsonl']),
        '| G7 double-review report | %s | %s |'
        % ('present' if double_exists else 'blocked', DOUBLE_REPORT if double_exists else 'missing'),
        '| G9 interop artifacts | %s | %s |' % ('ready' if iok else 'blocked', imsg.replace('|', '\\|')[:180]),
        '| G10 edition cut | %s | blockers=%s |'
        % ('blocked' if eblockers else 'ready-to-cut', ', '.join(eblockers) or 'none'),
    ]
    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    open(args.out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('release readiness report -> %s' % args.out)
    print('blocking:', ', '.join(blocking) or 'none')
    if args.fail_on_blocked and eblockers:
        print('fail-on-blocked: blockers caused exit 1: %s' % ', '.join(eblockers))
        return 1
    if eblockers:
        print('report-only: blocked gates are informational for exit status; use --fail-on-blocked for CI/go-no-go')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
