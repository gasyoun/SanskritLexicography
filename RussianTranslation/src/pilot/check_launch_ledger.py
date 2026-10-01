#!/usr/bin/env python
"""Mechanical check for LAUNCH_FUCKUPS.md.

  python src/pilot/check_launch_ledger.py
  python src/pilot/check_launch_ledger.py --handoff H220
  python src/pilot/check_launch_ledger.py --since 2026-07-05

The ledger is a human Markdown file with one fenced JSON block. This checker
does not infer root cause; it only enforces that every recorded launch failure
has enough structured information to be useful at handoff closeout time.
"""
import argparse
import datetime as _dt
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gate_evidence as ge                                          # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
LEDGER_MD = os.path.join(REPO_ROOT, 'LAUNCH_FUCKUPS.md')
RUN_LOG_MD = os.path.join(HERE, 'RUN_LOG.md')
FENCE_RE = re.compile(r'```json launch_failure_ledger\r?\n(.*?)```', re.DOTALL)
RUNLOG_HEADING_RE = re.compile(r'^(#{2,4})\s+(\d{4}-\d{2}-\d{2})\s+[—-]\s+(.*)$')
HANDOFF_RE = re.compile(r'\bH\d{3}\b')

VALID_CLASSES = {
    'concurrency/api',
    'structured-output-limit',
    'complexity-estimate-drift',
    'kill-gate-calibration',
    'gate-bug',
    'artifact/provenance',
    'tm/cache',
    'filesystem/watcher',
    'key/schema-mismatch',
    'operator/process',
    'external-api',
    'unknown',
}

VALID_RESIDUAL = {
    'fixed',
    'structurally-guarded',
    'accepted-as-proven-residual',
    'bug-hunt-handoff',
    'open-paused',
}

REQUIRED_TEXT = (
    'id',
    'date',
    'title',
    'lane',
    'model',
    'orchestrator',
    'symptoms',
    'classification',
    'root_cause',
    'guardrail',
    'residual_status',
    'residual_risk',
)


def parse_date(s):
    try:
        return _dt.date.fromisoformat(s)
    except ValueError:
        raise SystemExit('invalid date %r, expected YYYY-MM-DD' % s)


def load_ledger(path=LEDGER_MD):
    text = open(path, encoding='utf-8').read()
    m = FENCE_RE.search(text)
    if not m:
        raise SystemExit('no ```json launch_failure_ledger fenced block found in %s' % path)
    try:
        entries = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise SystemExit('invalid JSON launch ledger: %s' % e)
    if not isinstance(entries, list):
        raise SystemExit('launch ledger JSON must be a list')
    return entries


def _has_value(v):
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (int, float)):
        return True
    return bool(v)


def check_entries(entries):
    violations = []
    seen_ids = set()
    unknown_shapes = {}
    for i, e in enumerate(entries):
        label = e.get('id') or '<entry %d>' % (i + 1)
        if not isinstance(e, dict):
            violations.append('%s: entry must be an object' % label)
            continue
        if label in seen_ids:
            violations.append('%s: duplicate id' % label)
        seen_ids.add(label)
        for key in REQUIRED_TEXT:
            if not _has_value(e.get(key)):
                violations.append('%s: missing non-empty %s' % (label, key))
        if e.get('classification') and e.get('classification') not in VALID_CLASSES:
            violations.append('%s: classification %r is not valid' % (label, e.get('classification')))
        if e.get('residual_status') and e.get('residual_status') not in VALID_RESIDUAL:
            violations.append('%s: residual_status %r is not valid' % (label, e.get('residual_status')))
        try:
            parse_date(e.get('date', ''))
        except SystemExit as exc:
            violations.append('%s: %s' % (label, exc))
        for bucket in ('expected', 'actual'):
            value = e.get(bucket)
            if not isinstance(value, dict):
                violations.append('%s: %s must be an object with agents/tokens' % (label, bucket))
                continue
            for field in ('agents', 'tokens'):
                if not _has_value(value.get(field)):
                    violations.append('%s: %s.%s is required' % (label, bucket, field))
        if not isinstance(e.get('passes'), int) or e.get('passes') < 1:
            violations.append('%s: passes must be an integer >= 1' % label)
        if e.get('classification') == 'unknown':
            shape = (e.get('lane', '').strip(), e.get('symptoms', '').strip().lower())
            unknown_shapes.setdefault(shape, []).append(label)
    for shape, labels in unknown_shapes.items():
        if len(labels) > 1:
            violations.append(
                'unknown recurrence requires bug-hunt handoff: %s share %r' %
                (', '.join(labels), shape[1][:80]))
    return violations


def launch_headings_since(since, run_log=RUN_LOG_MD):
    if not os.path.exists(run_log):
        return []
    headings = []
    with open(run_log, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = RUNLOG_HEADING_RE.match(line.rstrip('\n'))
            if not m:
                continue
            day = parse_date(m.group(2))
            title = m.group(3)
            if day < since:
                continue
            lowered = title.lower()
            if 'no max/workflow' in lowered or 'no workflow' in lowered:
                continue
            if not any(token in lowered for token in ('run', 'aborted', 'workflow', 'max', 'api', 'promoted')):
                continue
            handoffs = HANDOFF_RE.findall(title)
            if handoffs:
                headings.append((day.isoformat(), title, sorted(set(handoffs))))
    return headings


def check_requested(entries, handoff=None, since=None):
    violations = []
    if handoff:
        matches = [e for e in entries if e.get('handoff') == handoff]
        if not matches:
            violations.append('%s: no launch-failure ledger entry' % handoff)
    if since:
        present = {e.get('handoff') for e in entries if e.get('handoff')}
        for day, title, handoffs in launch_headings_since(since):
            for h in handoffs:
                if h not in present:
                    violations.append(
                        '%s: RUN_LOG launch heading on %s lacks ledger entry: %s' %
                        (h, day, title))
    return violations


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--handoff', help='require at least one entry for this H### handoff')
    p.add_argument('--since', help='scan RUN_LOG launch headings since YYYY-MM-DD')
    p.add_argument('--ledger', default=LEDGER_MD, help=argparse.SUPPRESS)
    p.add_argument('--evidence', default=None, help=argparse.SUPPRESS)
    args = p.parse_args(argv)
    if not args.evidence:
        args.evidence = ge.default_sidecar('launch_ledger')

    entries = load_ledger(args.ledger)
    # W1 (H3748, #1803): the verdict is built THROUGH a GateEvidence record, so a green
    # line names what it checked. The predicate logic below is unchanged -- what is new
    # is that "0 entries, 0 violations" can no longer read as a clean audit.
    ev = ge.GateEvidence('launch_ledger', 'LAUNCH_FUCKUPS.md completeness (C8-4)')
    ev.add_input('ledger', path=args.ledger, units=len(entries))
    violations = check_entries(entries)
    # Each entry is evaluated against the required-field / vocabulary / shape suite.
    ev.add_predicate('entry_completeness', evaluations=len(entries), hits=len(violations))
    if args.handoff or args.since:
        since = parse_date(args.since) if args.since else None
        requested = check_requested(entries, args.handoff, since)
        headings = launch_headings_since(since) if since else []
        if since:
            ev.add_input('run_log', path=RUN_LOG_MD, units=len(headings))
        ev.add_predicate('handoff_cross_check',
                         evaluations=len(headings) + (1 if args.handoff else 0),
                         hits=len(requested))
        if since and not headings:
            ev.declare_expected_empty(
                'no_runlog_launch_headings',
                'no launch-shaped RUN_LOG heading since %s to cross-check' % since)
        violations.extend(requested)
    if not entries:
        ev.declare_expected_empty(
            'no_launch_failures_recorded',
            'the ledger records incidents; an empty one is a clean history, not a dead gate')
    ev.set_verdict('fail' if violations else 'pass')
    try:
        ev.assert_nonvacuous()
    except ge.VacuousGateError as exc:
        print('LAUNCH FAILURE LEDGER: %s' % exc)
        ev.set_verdict('fail')
        ev.emit(args.evidence)
        return 1
    ev.emit(args.evidence)
    if violations:
        print('LAUNCH FAILURE LEDGER: %d violation(s)' % len(violations))
        for v in violations:
            print('  - ' + v)
        return 1
    print('LAUNCH FAILURE LEDGER: %d entries complete (%s)' % (len(entries), ev.summary()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
