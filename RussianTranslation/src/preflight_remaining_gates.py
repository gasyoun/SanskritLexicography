#!/usr/bin/env python
"""Compact non-mutating preflight for the remaining print gates."""
import argparse
import csv
import datetime
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
PILOT = os.path.join(HERE, 'pilot')
sys.path.insert(0, PILOT)
from dashboard_events import append_event

REVIEW_CSV = os.environ.get('PWG_RU_REVIEW_CSV') or os.path.join(HERE, '_review_queue.csv')
STORE = os.environ.get('PWG_RU_STORE') or os.path.join(HERE, 'pwg_ru_translated.jsonl')
GOLD_CSV = os.path.join(ROOT, 'gold', '_human_gold_review.csv')
GOLD_LABELS = os.path.join(ROOT, 'gold', 'human_gold_labels.jsonl')
DOUBLE_REVIEW_CSV = os.path.join(ROOT, 'gold', '_double_review_queue.csv')
DOUBLE_REVIEW_LABELS = os.path.join(ROOT, 'gold', 'double_review_labels.jsonl')
DOUBLE_REVIEW_REPORT = os.path.join(ROOT, 'gold', 'double_review_agreement.md')
G10 = 'G10_immutable_edition_cut'


def run(label, cmd, ok_codes=(0,)):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180)
    status = 'ok' if r.returncode in ok_codes else 'fail'
    detail = (r.stdout.strip() or r.stderr.strip()).splitlines()
    return label, status, detail[-1] if detail else ''


def review_state():
    s = review_summary()
    return 'blocked' if s['print_ready_rows'] == 0 else 'partial', (
        'review decisions %d/%d, print-ready %d' %
        (s['decisions'], s['rows'], s['print_ready_rows']))


def review_summary():
    out = {'gate': 'G5_translation_store_review_gate', 'rows': 0, 'decisions': 0,
           'decision_counts': {}, 'print_ready_candidates': 0, 'print_ready_rows': 0,
           'review_csv': REVIEW_CSV, 'store': STORE}
    if os.path.exists(REVIEW_CSV):
        with open(REVIEW_CSV, encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                if not any((v or '').strip() for v in row.values()):
                    continue
                out['rows'] += 1
                decision = (row.get('decision') or '').strip()
                if decision:
                    out['decisions'] += 1
                    out['decision_counts'][decision] = out['decision_counts'].get(decision, 0) + 1
                    if decision in {'approved', 'human_reviewed'}:
                        out['print_ready_candidates'] += 1
    if os.path.exists(STORE):
        with open(STORE, encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                if (row.get('review_status') in {'approved', 'human_reviewed'}
                        and row.get('ok') and row.get('placeholders_ok') and row.get('key_match')):
                    out['print_ready_rows'] += 1
    return out


def gold_state():
    s = gold_summary()
    return 'blocked' if s['complete'] < s['rows'] or not s['rows'] else 'ready', (
        'gold complete %d/%d' % (s['complete'], s['rows']))


def gold_summary():
    out = {'gate': 'G6_human_gold_set', 'rows': 0, 'complete': 0,
           'missing_fields': {}, 'labels_jsonl_rows': 0,
           'gold_csv': GOLD_CSV, 'labels_jsonl': GOLD_LABELS}
    if os.path.exists(GOLD_CSV):
        with open(GOLD_CSV, encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                out['rows'] += 1
                missing = [field for field in ('human_label', 'reviewer_id',
                                                'confidence', 'needs_adjudication')
                           if not (row.get(field) or '').strip()]
                if missing:
                    for field in missing:
                        out['missing_fields'][field] = out['missing_fields'].get(field, 0) + 1
                else:
                    out['complete'] += 1
    if os.path.exists(GOLD_LABELS):
        with open(GOLD_LABELS, encoding='utf-8') as f:
            out['labels_jsonl_rows'] = sum(1 for line in f if line.strip())
    return out


def double_review_summary():
    out = {'gate': 'G7_double_review_agreement', 'queue_rows': 0, 'complete': 0,
           'labels_jsonl_rows': 0, 'agreement_report_exists': os.path.exists(DOUBLE_REVIEW_REPORT),
           'queue_csv': DOUBLE_REVIEW_CSV, 'labels_jsonl': DOUBLE_REVIEW_LABELS,
           'agreement_report': DOUBLE_REVIEW_REPORT}
    if os.path.exists(DOUBLE_REVIEW_CSV):
        with open(DOUBLE_REVIEW_CSV, encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                out['queue_rows'] += 1
                if all((row.get(field) or '').strip()
                       for field in ('second_reviewer_id', 'second_human_label',
                                     'second_confidence', 'second_needs_adjudication')):
                    out['complete'] += 1
    if os.path.exists(DOUBLE_REVIEW_LABELS):
        with open(DOUBLE_REVIEW_LABELS, encoding='utf-8') as f:
            out['labels_jsonl_rows'] = sum(1 for line in f if line.strip())
    return out


def local_gate_blockers(review, gold, double):
    blockers = []
    if review['print_ready_rows'] == 0:
        blockers.append('G5_translation_store_review_gate')
    if gold['complete'] < gold['rows'] or not gold['rows']:
        blockers.append('G6_human_gold_set')
    if not double['agreement_report_exists']:
        blockers.append('G7_double_review_agreement')
    return blockers


def edition_summary(blockers, release_dir, gate_blockers=None):
    editions = []
    if os.path.isdir(release_dir):
        editions = sorted(name for name in os.listdir(release_dir) if name.startswith('edition_'))
    upstream_blockers = sorted((set(blockers) - {G10}) | set(gate_blockers or []))
    return {'gate': G10,
            'release_dir': release_dir,
            'edition_dirs': editions,
            'latest_edition': editions[-1] if editions else None,
            'agreement_report_exists': os.path.exists(DOUBLE_REVIEW_REPORT),
            'blocked_by': upstream_blockers,
            'ready_to_cut': not upstream_blockers}


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


def write_dashboard(path_json, path_md, checks, dashboard):
    for path in (path_json, path_md):
        parent = os.path.dirname(os.path.abspath(path))
        if parent:
            os.makedirs(parent, exist_ok=True)
    json.dump(dashboard, open(path_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    review = dashboard['gates']['G5_translation_store_review_gate']
    gold = dashboard['gates']['G6_human_gold_set']
    double = dashboard['gates']['G7_double_review_agreement']
    edition = dashboard['gates']['G10_immutable_edition_cut']
    lines = [
        '# Gate Status Snapshot',
        '',
        '| gate | status | detail |',
        '|---|---|---|',
        '| G5 translation review | %s | decisions %d/%d; print-ready rows %d |'
        % ('blocked' if review['print_ready_rows'] == 0 else 'partial',
           review['decisions'], review['rows'], review['print_ready_rows']),
        '| G6 human gold | %s | complete %d/%d; labels jsonl %d |'
        % ('blocked' if gold['complete'] < gold['rows'] or not gold['rows'] else 'ready',
           gold['complete'], gold['rows'], gold['labels_jsonl_rows']),
        '| G7 double review | %s | complete %d/%d; agreement report %s |'
        % ('blocked' if not double['agreement_report_exists'] else 'report-present',
           double['complete'], double['queue_rows'],
           'yes' if double['agreement_report_exists'] else 'no'),
        '| G10 edition cut | %s | latest edition %s; blockers %s |'
        % ('ready-to-cut' if edition['ready_to_cut'] else 'blocked',
           edition['latest_edition'] or 'none',
           ', '.join(edition['blocked_by']) or 'none'),
        '',
        '## Preflight Commands',
        '',
        '| check | status | detail |',
        '|---|---|---|',
    ]
    for label, status, detail in checks:
        lines.append('| %s | %s | %s |' %
                     (label, status, str(detail).replace('|', '\\|')[:180]))
    open(path_md, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--release-dir', default=os.path.join(ROOT, 'release'))
    ap.add_argument('--readiness-out', default=os.path.join(ROOT, 'release', 'readiness_report.md'))
    ap.add_argument('--json-out', default=os.path.join(ROOT, 'release', 'gate_status_snapshot.json'))
    ap.add_argument('--md-out', default=os.path.join(ROOT, 'release', 'gate_status_snapshot.md'))
    ap.add_argument('--skip-local-human-artifacts', action='store_true',
                    help='fixture mode: skip local review/gold CSV validators')
    ap.add_argument('--fail-on-blocked', action='store_true',
                    help='exit 1 when print gates are blocked; default is report-only')
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
    review = review_summary()
    gold = gold_summary()
    double = double_review_summary()
    gate_blockers = local_gate_blockers(review, gold, double)
    dashboard = {
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'release_dir': args.release_dir,
        'roadmap_blockers': blockers,
        'gates': {
            'G5_translation_store_review_gate': review,
            'G6_human_gold_set': gold,
            'G7_double_review_agreement': double,
            G10: edition_summary(blockers, args.release_dir, gate_blockers),
        },
    }
    write_dashboard(args.json_out, args.md_out, checks, dashboard)
    edition = dashboard['gates'][G10]
    blocked = sorted(set(edition['blocked_by']) | ({G10} if not edition['ready_to_cut'] else set()))
    append_event(
        'preflight_remaining_gates', 'print_gate_snapshot',
        level='warn' if blocked else 'info',
        root=None,
        state='blocked' if blocked else 'ready',
        summary='print gates %s; blockers=%d' %
        ('blocked' if blocked else 'ready', len(blocked)),
        data={'json_out': args.json_out, 'md_out': args.md_out,
              'roadmap_blockers': blockers, 'blocked': blocked,
              'gates': dashboard['gates']})
    print('| check | status | detail |')
    print('|---|---|---|')
    failed = False
    for label, status, detail in checks:
        print('| %s | %s | %s |' % (label, status, str(detail).replace('|', '\\|')[:180]))
        failed = failed or status == 'fail'
    print('dashboard json -> %s' % args.json_out)
    print('dashboard md   -> %s' % args.md_out)
    if args.fail_on_blocked and blocked:
        print('fail-on-blocked: blockers caused exit 1: %s' % ', '.join(blocked))
        return 1
    if blocked:
        print('report-only: blocked gates are informational for exit status; use --fail-on-blocked for CI/go-no-go')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
