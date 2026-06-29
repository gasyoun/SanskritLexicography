#!/usr/bin/env python
"""audit_window.py — one deterministic audit command for a translated workflow window.

Runs the free Python gates against the SAME wf_output.json key set, writes one
machine-readable report plus a requeue list, and optionally glues a root article.

  python src/pilot/audit_window.py wf_output.json --root sTA --write-requeue
"""
import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))          # .../src/pilot
SRC = os.path.dirname(HERE)                                # .../src
OUT = os.path.join(HERE, 'output')

sys.path.insert(0, SRC)
import nws_split
from safe_filename import safe_name
from dashboard_events import append_event
from prompt_rule_audit import (
    DEFAULT_HARNESS,
    DEFAULT_TEMPLATE,
    audit_cards as audit_semantic_cards,
    build_report as build_prompt_rule_report,
)
from workflow_payload import workflow_payload
from window_provenance import stale_check
from window_reports import (
    audit_state,
    build_judge_sample,
    build_production_metrics,
    write_reports,
)

COLLECT = os.path.join(SRC, '_pilot_collect.py')
BATCH_FILE = os.path.join(OUT, '_realtest_batch.json')
PROTECTED = {'aMSa', 'anna', 'ap'}


def run_py(args, env=None):
    t0 = time.perf_counter()
    p = subprocess.run([sys.executable] + args, cwd=SRC, capture_output=True,
                       text=True, encoding='utf-8', env=env)
    return {'argv': [sys.executable] + args, 'returncode': p.returncode,
            'stdout': p.stdout, 'stderr': p.stderr,
            'seconds': round(time.perf_counter() - t0, 3)}


def parse_flagged(stdout):
    m = re.search(r'\|\s*flagged:\s*(.+)$', stdout, re.M)
    if not m:
        return []
    return [x.strip() for x in m.group(1).split(',') if x.strip()]


def parse_translation(stdout):
    return parse_flagged(stdout)


def parse_coverage(stdout):
    return parse_flagged(stdout)


def parse_dupes(stdout):
    keys = set()
    for line in stdout.splitlines():
        m = re.search(r'rendered by:\s*(.+)$', line)
        if m:
            keys.update(k.strip() for k in m.group(1).split(',') if k.strip())
    return sorted(keys)


def parse_nws(stdout):
    keys = set()
    m = re.search(r'GATE: FAIL[^\n]*\n\s*rejected:\s*(.+)', stdout)
    if m:
        keys.update(k.strip() for k in m.group(1).split() if k.strip())
    for line in stdout.splitlines():
        if 'MISATTRIBUTION' in line:
            keys.add(line.split()[0])
    return sorted(keys)


def exact_file_exists(directory, name):
    try:
        return name in set(os.listdir(directory))
    except OSError:
        return False


def load_protected():
    protected = set(PROTECTED)
    if os.path.exists(BATCH_FILE):
        try:
            batch = json.load(open(BATCH_FILE, encoding='utf-8'))
            protected.update(batch.get('protected') or [])
        except Exception:
            pass
    return protected


def quarantine(key):
    for nm in (safe_name(key) + '.merged.md', key + '.merged.md'):
        if exact_file_exists(OUT, nm):
            src = os.path.join(OUT, nm)
            dst = os.path.join(OUT, nm[:-len('.merged.md')] + '.merged.REJECTED.md')
            if os.path.exists(dst):
                os.remove(dst)
            os.replace(src, dst)
            return True
    return False


def collect_cards(wf, protected):
    env = os.environ.copy()
    env['PILOT_COLLECT_PROTECTED'] = ','.join(sorted(protected))
    return run_py([COLLECT, wf], env=env)


def run_nws_gate(keys, protected):
    t0 = time.perf_counter()
    lines = ['=== 2. NWS attribution audit (nws_split) ===']
    clean = misattr = no_nws = missing_raw = missing_card = other = 0
    bad_cards, bad_misattribution = [], []
    for k in keys:
        if k in protected:
            lines.append('  %-12s protected — keeping hand-authored card' % k)
        res = nws_split.check_result(k)
        lines.extend(res['lines'])
        verdict = res['verdict']
        if verdict == 'CLEAN':
            clean += 1
        elif verdict == 'NO-NWS':
            no_nws += 1
        elif verdict == 'NO-RAW':
            missing_raw += 1
            bad_cards.append(k)
        elif verdict == 'NO-CARD':
            missing_card += 1
            bad_cards.append(k)
        elif verdict == 'MISATTRIBUTION':
            misattr += 1
            bad_cards.append(k)
            bad_misattribution.append(k)
        else:
            other += 1

    lines += ['', '=== REPORT ===']
    lines.append('  cards audited      : %d' % len(keys))
    lines.append('  NWS audit CLEAN    : %d' % clean)
    lines.append('  F12 misattribution : %d %s' % (
        misattr, ('→ ' + ' '.join(bad_misattribution)) if bad_misattribution else ''))
    lines.append('  no NWS fragment    : %d' % no_nws)
    lines.append('  missing raw input  : %d' % missing_raw)
    lines.append('  missing card output: %d' % missing_card)
    lines.append('  other verdicts     : %d' % other)
    lines.append('  judge pass rate    : see "publishable" line in collect section above')

    gate_fail = [k for k in bad_cards if k not in protected]
    if gate_fail:
        lines.append('')
        lines.append('  GATE: FAIL — %d card(s) require rejection (F12 slide): %s'
                     % (len(gate_fail), ' '.join(gate_fail)))
    else:
        lines.append('')
        lines.append('  GATE: PASS — no F12 misattribution in fresh cards')

    return {'argv': ['in-process', 'nws_split.check_result'], 'returncode': 1 if gate_fail else 0,
            'stdout': '\n'.join(lines) + '\n', 'stderr': '', 'requeue': sorted(gate_fail),
            'misattribution': sorted(k for k in bad_misattribution if k not in protected),
            'rejected': [], 'seconds': round(time.perf_counter() - t0, 3)}


def run_prompt_semantic_audit(wf, protected, review_limit=25):
    t0 = time.perf_counter()
    paths = [os.path.abspath(DEFAULT_TEMPLATE)]
    harness = os.path.abspath(DEFAULT_HARNESS)
    if os.path.exists(harness):
        paths.append(harness)
    prompt_rules = build_prompt_rule_report(paths)
    card_risks = audit_semantic_cards(wf, review_limit=review_limit)
    requeue = sorted(
        key for key in (card_risks.get('requeue_keys') or [])
        if key not in set(protected))
    missing_rule_count = prompt_rules.get('missing_rule_count', 0)
    lines = [
        'Prompt/manual rules: %s (%d missing required rule%s)' % (
            'FAIL' if missing_rule_count else 'PASS',
            missing_rule_count,
            '' if missing_rule_count == 1 else 's'),
        'Live manual coverage: %s' % ', '.join(
            prompt_rules.get('live_manual_coverage') or []),
        'Methodology/design only: %s' % ', '.join(
            prompt_rules.get('methodology_only_manuals') or []),
        'Semantic risks: %d risk(s) across %d key(s); high-confidence=%d key(s)' % (
            card_risks.get('risk_count', 0),
            card_risks.get('risky_key_count', 0),
            len(card_risks.get('high_confidence_keys') or [])),
        'High-confidence requeue candidates: %s' % (
            ', '.join(requeue) if requeue else '(none)'),
    ]
    queue = (card_risks.get('review_queue') or {}).get('items') or []
    if queue:
        lines.append('Review queue:')
        for item in queue[:10]:
            lines.append('  %-34s score=%d high_confidence=%d risks=%s' % (
                item['key'], item['risk_score'],
                item.get('high_confidence_count', 0),
                ', '.join(item.get('top_risks') or [])))
    for target in prompt_rules.get('targets') or []:
        for rule in target.get('missing') or []:
            lines.append('  missing %s in %s: %s' % (
                rule['id'], os.path.relpath(target['path'], SRC),
                ', '.join(rule.get('missing_phrases') or [])))
    return {
        'argv': ['in-process', 'prompt_rule_audit'],
        'returncode': 2 if missing_rule_count else (1 if requeue else 0),
        'stdout': '\n'.join(lines) + '\n',
        'stderr': '',
        'requeue': requeue,
        'prompt_rules': prompt_rules,
        'card_risks': card_risks,
        'seconds': round(time.perf_counter() - t0, 3),
    }


def emit_audit_event(event_type, level='info', root=None, state=None, summary='', data=None):
    append_event('audit_window', event_type, level=level, root=root,
                 state=state, summary=summary, data=data or {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('wf_output')
    ap.add_argument('--root')
    ap.add_argument('--write-requeue', action='store_true')
    ap.add_argument('--allow-stale', action='store_true',
                    help='forensic mode: continue even if workflow/rootmap/input provenance is stale')
    ap.add_argument('--judge-sample-rate', type=float, default=0.10,
                    help='deterministic clean-key semantic judge sample rate (default: 0.10)')
    ap.add_argument('--judge-sample-min', type=int, default=5,
                    help='minimum clean keys to sample when clean keys exist (default: 5)')
    ap.add_argument('--judge-sample-seed',
                    help='override deterministic semantic sample seed')
    ap.add_argument('--wall-clock-minutes', type=float,
                    help='Max workflow wall-clock minutes for this run/window')
    ap.add_argument('--max-input-tokens', type=int,
                    help='Max-reported input tokens')
    ap.add_argument('--max-output-tokens', type=int,
                    help='Max-reported output tokens')
    ap.add_argument('--max-cache-read-tokens', type=int,
                    help='Max-reported cache_read tokens')
    ap.add_argument('--max-cache-create-tokens', type=int,
                    help='Max-reported cache_create tokens')
    ap.add_argument('--max-total-tokens', type=int,
                    help='Max-reported total tokens, if available')
    ap.add_argument('--weekly-cap-fired', action='store_true',
                    help='record that the Max weekly cap fired during/after this window')
    ap.add_argument('--weekly-cap-cumulative-tokens', type=int,
                    help='cumulative token count observed when the weekly cap fired')
    ap.add_argument('--metrics-note',
                    help='short free-text note for the production metrics ledger')
    args = ap.parse_args()

    wf = os.path.abspath(args.wf_output)
    if not os.path.exists(wf):
        sys.exit('no workflow output %r' % args.wf_output)

    _payload, wf_meta, _results, keys, null_cards = workflow_payload(wf)
    emit_audit_event(
        'audit_start', root=args.root, state='started',
        summary='audit started for %s (%d workflow keys)' % (os.path.basename(wf), len(keys)),
        data={'workflow': wf, 'workflow_keys': len(keys),
              'null_cards': len(null_cards),
              'has_meta': bool(wf_meta),
              'allow_stale': args.allow_stale})
    stale = stale_check(args.root, wf_meta, keys)
    if stale.get('stale') and not args.allow_stale:
        print('\n=== stale artifact check ===')
        for err in stale.get('errors') or []:
            print('  ' + err)
        print('  refusing collect/gates/glue; refresh wf_output.json or rerun with --allow-stale for inspection')
        report = {'workflow': wf, 'root': args.root, 'state': 'stale_artifact',
                  'workflow_meta': wf_meta, 'stale_check': stale,
                  'keys': keys, 'null_cards': null_cards,
                  'collect': None, 'gates': {}, 'glue': None,
                  'requeue': [], 'crashed': ['stale_artifact'],
                  'requeue_file_written': False,
                  'requeue_file_preserved': bool(args.write_requeue),
                  'requeue_note': 'stale artifact refused before gates; existing requeue.keys.txt preserved; no trustworthy mechanical requeue generated',
                  'judge_sample_rate': args.judge_sample_rate,
                  'judge_sample_min': args.judge_sample_min,
                  'judge_sample_seed': args.judge_sample_seed,
                  'production_metrics': build_production_metrics(args)}
        json_path, md_path, rq_path, js_path, status_json, status_md = write_reports(
            report, args.write_requeue, write_requeue_file=False)
        emit_audit_event(
            'stale_refusal', level='error', root=args.root, state='stale_artifact',
            summary='stale artifact refused before collect/gates/glue (%d issue%s)' %
            (len(stale.get('errors') or []), '' if len(stale.get('errors') or []) == 1 else 's'),
            data={'workflow': wf, 'errors': stale.get('errors') or [],
                  'warnings': stale.get('warnings') or [],
                  'workflow_keys': len(keys),
                  'expected_keys': len(((stale.get('current') or {}).get('selected_keys') or [])),
                  'missing_keys': stale.get('missing_keys') or [],
                  'unexpected_keys': stale.get('unexpected_keys') or []})
        emit_audit_event(
            'audit_end', level='error', root=args.root, state='stale_artifact',
            summary='audit ended: stale_artifact; cards=%d requeue=0' % len(keys),
            data={'workflow': wf, 'cards': len(keys), 'state': 'stale_artifact',
                  'requeue_count': 0, 'crashed': ['stale_artifact'],
                  'status_json': status_json})
        print('report json  : %s' % os.path.relpath(json_path, SRC))
        print('report md    : %s' % os.path.relpath(md_path, SRC))
        print('status json  : %s' % os.path.relpath(status_json, SRC))
        print('status md    : %s' % os.path.relpath(status_md, SRC))
        print('judge sample : %s' % os.path.relpath(js_path, SRC))
        if args.write_requeue:
            print('requeue file : preserved (stale artifact)')
        elif rq_path:
            print('requeue file : %s' % os.path.relpath(rq_path, SRC))
        sys.exit(2)
    if stale.get('stale') and args.allow_stale:
        print('\n=== stale artifact check (allowed) ===')
        for err in stale.get('errors') or []:
            print('  ' + err)
    protected = load_protected()
    gates = {}

    print('\n=== collect ===')
    collect = collect_cards(wf, protected)
    print(collect['stdout'].rstrip())
    if collect['stderr'].strip():
        print(collect['stderr'].rstrip(), file=sys.stderr)

    commands = [
        ('translation', [os.path.join(SRC, 'audit_translation.py'), '--wf', wf], parse_translation),
        ('coverage', [os.path.join(SRC, 'audit_coverage.py'), wf], parse_coverage),
        ('sense_dupes', [os.path.join(SRC, 'audit_sense_dupes.py'), wf], parse_dupes),
    ]
    futures = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futures[ex.submit(run_nws_gate, keys, protected)] = ('nws', None)
        futures[ex.submit(run_prompt_semantic_audit, wf, protected)] = ('prompt_semantic', None)
        for name, cmd, parser in commands:
            futures[ex.submit(run_py, cmd)] = (name, parser)
        for fut in concurrent.futures.as_completed(futures):
            name, parser = futures[fut]
            res = fut.result()
            if parser:
                res['requeue'] = parser(res['stdout'])
            gates[name] = res

    for name in ['nws', 'translation', 'coverage', 'sense_dupes', 'prompt_semantic']:
        res = gates[name]
        print('\n=== %s ===' % name)
        print(res['stdout'].rstrip())
        if res['stderr'].strip():
            print(res['stderr'].rstrip(), file=sys.stderr)
        emit_audit_event(
            'gate_summary',
            level='warn' if res['returncode'] or res.get('requeue') else 'info',
            root=args.root,
            state='gate_failed' if res['returncode'] not in (0, 1) else
            ('needs_requeue' if res.get('requeue') else 'clean'),
            summary='%s exit=%s requeue=%d' %
            (name, res['returncode'], len(res.get('requeue') or [])),
            data={'gate': name, 'returncode': res['returncode'],
                  'requeue': res.get('requeue') or [], 'seconds': res.get('seconds')})

    if gates['nws'].get('misattribution'):
        rejected = [k for k in gates['nws']['misattribution'] if quarantine(k)]
        gates['nws']['rejected'] = rejected
        if rejected:
            gates['nws']['stdout'] += '  quarantined        : %s\n' % ' '.join(rejected)

    glue = None
    if args.root:
        print('\n=== glue %s ===' % args.root)
        res = run_py([os.path.join(SRC, 'root_glue_translated.py'), args.root])
        print(res['stdout'].rstrip())
        if res['stderr'].strip():
            print(res['stderr'].rstrip(), file=sys.stderr)
        nested = os.path.join(OUT, safe_name(args.root) + '.NESTED.md')
        glue = {'returncode': res['returncode'], 'stdout': res['stdout'], 'stderr': res['stderr'],
                'summary': (res['stdout'].strip().splitlines()[-1] if res['stdout'].strip() else ''),
                'nested_exists': os.path.exists(nested)}
        emit_audit_event(
            'glue_result',
            level='warn' if glue['returncode'] or not glue['nested_exists'] else 'info',
            root=args.root,
            state='blocked' if glue['returncode'] or not glue['nested_exists'] else 'ok',
            summary=glue['summary'] or 'glue finished',
            data={'returncode': glue['returncode'],
                  'nested_exists': glue['nested_exists'],
                  'seconds': res.get('seconds')})

    requeue = set(null_cards)
    crashed = []
    for name, gate in gates.items():
        requeue.update(gate.get('requeue') or [])
        if gate['returncode'] not in (0, 1):
            crashed.append(name)
    if glue and glue['returncode'] != 0:
        crashed.append('glue')
    if glue and not glue.get('nested_exists'):
        crashed.append('glue-missing-nested')

    if collect['returncode'] not in (0, 1):
        crashed.append('collect')

    report = {'workflow': wf, 'root': args.root, 'keys': keys, 'null_cards': null_cards,
              'workflow_meta': wf_meta, 'stale_check': stale,
              'collect': collect,
              'gates': gates, 'glue': glue, 'requeue': sorted(requeue), 'crashed': crashed}
    report['prompt_rules'] = gates.get('prompt_semantic', {}).get('prompt_rules')
    report['semantic_risks'] = gates.get('prompt_semantic', {}).get('card_risks')
    report['judge_sample_rate'] = args.judge_sample_rate
    report['judge_sample_min'] = args.judge_sample_min
    report['judge_sample_seed'] = args.judge_sample_seed
    report['judge_sample'] = build_judge_sample(
        report, args.judge_sample_rate, args.judge_sample_min, args.judge_sample_seed)
    report['production_metrics'] = build_production_metrics(args)
    json_path, md_path, rq_path, js_path, status_json, status_md = write_reports(report, args.write_requeue)
    state = audit_state(report)
    emit_audit_event(
        'requeue_summary',
        level='warn' if report['requeue'] else 'info',
        root=args.root, state=state,
        summary='requeue count %d' % len(report['requeue']),
        data={'requeue_count': len(report['requeue']),
              'requeue': report['requeue'],
              'judge_sample_count': report['judge_sample']['sample_count'],
              'judge_sample_seed': report['judge_sample']['seed'],
              'clean_key_count': report['judge_sample']['clean_key_count'],
              'production_metrics': report.get('production_metrics') or {}})
    if crashed:
        emit_audit_event(
            'crash_state', level='error', root=args.root, state='blocked',
            summary='crashed gates: %s' % ', '.join(crashed),
            data={'crashed': crashed})
    emit_audit_event(
        'audit_end',
        level='error' if crashed else ('warn' if report['requeue'] else 'info'),
        root=args.root, state=state,
        summary='audit ended: %s; cards=%d requeue=%d' %
        (state, len(keys), len(report['requeue'])),
        data={'workflow': wf, 'cards': len(keys), 'state': state,
              'requeue_count': len(report['requeue']),
              'crashed': crashed, 'status_json': status_json})

    print('\n=== AUDIT WINDOW SUMMARY ===')
    print('cards        : %d' % len(keys))
    print('requeue      : %d%s' % (len(report['requeue']),
          '' if not report['requeue'] else ' (' + ', '.join(report['requeue'][:12]) + (', ...' if len(report['requeue']) > 12 else '') + ')'))
    print('clean keys   : %d' % report['judge_sample']['clean_key_count'])
    print('judge sample : %d (seed %s)' % (report['judge_sample']['sample_count'], report['judge_sample']['seed']))
    print('report json  : %s' % os.path.relpath(json_path, SRC))
    print('report md    : %s' % os.path.relpath(md_path, SRC))
    print('status json  : %s' % os.path.relpath(status_json, SRC))
    print('status md    : %s' % os.path.relpath(status_md, SRC))
    print('judge sample : %s' % os.path.relpath(js_path, SRC))
    if rq_path:
        print('requeue file : %s' % os.path.relpath(rq_path, SRC))
    if crashed:
        print('crashed gates: %s' % ', '.join(crashed))
    sys.exit(1 if report['requeue'] or crashed else 0)


if __name__ == '__main__':
    main()


