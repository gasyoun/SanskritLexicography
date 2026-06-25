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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--release-dir', default=os.path.join(ROOT, 'release'))
    ap.add_argument('--out', default=DEFAULT_REPORT)
    args = ap.parse_args()
    gates = read_gates()
    blocking = [g['id'] for g in gates if g.get('blocks_print') and g.get('status') != 'passing']
    rc = review_counts()
    gc = gold_counts()
    iok, imsg = interop_ok(args.release_dir)
    double_exists = os.path.exists(DOUBLE_REPORT)
    lines = [
        '# Release readiness report',
        '',
        '| item | status | detail |',
        '|---|---|---|',
        '| Roadmap blockers | %s | %s |' % ('blocked' if blocking else 'ready', ', '.join(blocking) or 'none'),
        '| G5 review decisions | %s | rows=%d decisions=%d print_ready=%d |'
        % ('blocked' if rc['print_ready'] == 0 else 'partial/ready', rc['rows'], rc['decisions'], rc['print_ready']),
        '| G6 human gold labels | %s | csv_rows=%d complete=%d labels_jsonl=%d |'
        % ('blocked' if gc['complete'] < 320 else 'ready', gc['rows'], gc['complete'], gc['labels_jsonl']),
        '| G7 double-review report | %s | %s |'
        % ('present' if double_exists else 'blocked', DOUBLE_REPORT if double_exists else 'missing'),
        '| G9 interop artifacts | %s | %s |' % ('ready' if iok else 'blocked', imsg.replace('|', '\\|')[:180]),
        '| G10 edition cut | %s | waits for G5-G7 before edition_vN |'
        % ('blocked' if any(g in blocking for g in ('G5_translation_store_review_gate',
                                                    'G6_human_gold_set',
                                                    'G7_double_review_agreement')) else 'ready-to-cut'),
    ]
    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    open(args.out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('release readiness report -> %s' % args.out)
    print('blocking:', ', '.join(blocking) or 'none')


if __name__ == '__main__':
    main()
