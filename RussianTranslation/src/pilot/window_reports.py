#!/usr/bin/env python
"""Report, queue, and status writers for PWG frequency-window audits."""
import datetime
import hashlib
import json
import math
import os
import re

from window_common import HERE, OUT, load_json, rootmap_for, exact_file_exists
from window_provenance import harness_matches_current_root

import sys
SRC = os.path.dirname(HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)
from safe_filename import safe_name

LEDGER = os.path.join(OUT, 'window_ledger.jsonl')
JUDGE_SAMPLE_FILE = os.path.join(OUT, 'judge_sample.keys.txt')


def merged_exists(key, out_dir=OUT):
    return (exact_file_exists(out_dir, safe_name(key) + '.merged.md')
            or exact_file_exists(out_dir, key + '.merged.md'))


def glue_counts(summary):
    match = re.search(r':\s*(\d+)\s+sub-cards\s+\((\d+)\s+translated,\s+(\d+)\s+pending\)', summary or '')
    if not match:
        return None
    return {'subcards': int(match.group(1)), 'translated': int(match.group(2)),
            'pending': int(match.group(3))}


def default_judge_sample_seed(report, rate, minimum):
    meta = report.get('workflow_meta') or {}
    stale = report.get('stale_check') or {}
    current = stale.get('current') or {}
    parts = [
        'pwg_ru_judge_sample_v1',
        report.get('root') or '',
        meta.get('rootmap_sha256') or current.get('rootmap_sha256') or '',
        ','.join(report.get('keys') or []),
        'rate=%.6f' % rate,
        'min=%d' % minimum,
    ]
    return hashlib.sha256('\n'.join(parts).encode('utf-8')).hexdigest()[:16]


def build_judge_sample(report, rate, minimum, seed=None):
    rate = max(0.0, min(1.0, float(rate)))
    minimum = max(0, int(minimum))
    requeue = sorted(set(report.get('requeue') or []))
    all_keys = list(report.get('keys') or [])
    clean = [key for key in all_keys
             if key not in set(requeue)
             and key not in set(report.get('null_cards') or [])]
    clean = [key for key in clean if merged_exists(key)]
    sample_seed = seed or default_judge_sample_seed(report, rate, minimum)
    if report.get('state') == 'stale_artifact':
        clean = []
        clean_sample = []
    elif clean:
        target = int(math.ceil(len(clean) * rate))
        target = max(minimum, target)
        target = min(len(clean), target)
        ranked = sorted(clean, key=lambda key: hashlib.sha256(
            (sample_seed + '\0' + key).encode('utf-8')).hexdigest())
        clean_sample = sorted(ranked[:target])
    else:
        clean_sample = []
    keys = sorted(set(requeue) | set(clean_sample))
    return {
        'rate': rate,
        'minimum': minimum,
        'seed': sample_seed,
        'clean_key_count': len(clean),
        'clean_sample_count': len(clean_sample),
        'python_gate_failure_count': len(requeue),
        'sample_count': len(keys),
        'clean_sample_keys': clean_sample,
        'python_gate_failure_keys': requeue,
        'keys': keys,
    }


def build_production_metrics(args):
    fields = {
        'wall_clock_minutes': args.wall_clock_minutes,
        'max_input_tokens': args.max_input_tokens,
        'max_output_tokens': args.max_output_tokens,
        'max_cache_read_tokens': args.max_cache_read_tokens,
        'max_cache_create_tokens': args.max_cache_create_tokens,
        'max_total_tokens': args.max_total_tokens,
        'weekly_cap_fired': args.weekly_cap_fired,
        'weekly_cap_cumulative_tokens': args.weekly_cap_cumulative_tokens,
        'notes': args.metrics_note,
    }
    return {key: value for key, value in fields.items() if value not in (None, '')}


def next_action_for(state, report, pending):
    root = report.get('root') or '<root>'
    sample = report.get('judge_sample') or {}
    if state == 'stale_artifact':
        matches, _meta = harness_matches_current_root(report)
        if matches:
            return 'Run the generated optimized harness in Max Workflow and save fresh wf_output.json.'
        return 'Regenerate optimized harness for %s and rerun Max Workflow.' % root
    if report.get('crashed'):
        return 'Inspect crashed gates: %s.' % ', '.join(report['crashed'])
    if state == 'transient_only':
        return ('All requeue keys are transient nulls (rate-limit dropouts), no content defect. '
                'Re-run ONLY requeue.transient.keys.txt at low concurrency (<=3-wide), then rerun audit_window.py.')
    if report.get('requeue'):
        return 'Run python src\\pilot\\requeue_from_audit.py %s, rerun Max Workflow, then rerun audit_window.py.' % root
    if pending:
        return 'Translate pending sub-cards for %s, then rerun audit_window.py.' % root
    if sample.get('sample_count'):
        return 'Send judge_sample.keys.txt to sampled semantic judging outside Python.'
    return 'Window is mechanically clean; advance to the next frequency root.'


def append_ledger(status, out_dir=None):
    out_dir = out_dir or OUT
    os.makedirs(out_dir, exist_ok=True)
    compact = {
        'recorded_at': status.get('recorded_at'),
        'root': status.get('root'),
        'workflow': status.get('workflow'),
        'state': status.get('state'),
        'workflow_keys': status.get('workflow_keys'),
        'root_subcards': status.get('root_subcards'),
        'translated': status.get('translated'),
        'pending': status.get('pending'),
        'requeue_count': status.get('requeue_count'),
        'requeue_transient_count': status.get('requeue_transient_count'),
        'requeue_defect_count': status.get('requeue_defect_count'),
        'judge_sample_count': status.get('judge_sample_count'),
        'judge_sample_seed': status.get('judge_sample_seed'),
        'clean_key_count': status.get('clean_key_count'),
        'next_action': status.get('next_action'),
        'production_metrics': status.get('production_metrics'),
        'crashed': status.get('crashed'),
        'rootmap_sha256': status.get('rootmap_sha256'),
    }
    with open(os.path.join(out_dir, os.path.basename(LEDGER)), 'a', encoding='utf-8') as f:
        f.write(json.dumps(compact, ensure_ascii=False) + '\n')


def write_window_status(report, out_dir=None):
    out_dir = out_dir or OUT
    root = report.get('root')
    rootmap = rootmap_for(root) if root else None
    subkeys = []
    if rootmap:
        rootmap_json = load_json(rootmap)
        subkeys = [row['subkey'] for row in rootmap_json.get('sub_cards', [])]
    translated = sum(1 for key in (subkeys or report['keys']) if merged_exists(key))
    total = len(subkeys or report['keys'])
    glue = report.get('glue') or {}
    counts = glue_counts(glue.get('summary')) or {}
    pending = counts.get('pending', max(0, total - translated))
    if report.get('state'):
        state = report['state']
    elif report['crashed']:
        state = 'blocked'
    elif report['requeue']:
        # All-transient (only null cards, no gate defect) is a cheap re-run, not rework.
        # Guard on key presence so pre-split reports stay 'needs_requeue'.
        state = ('transient_only' if 'requeue_defect' in report and not report['requeue_defect']
                 else 'needs_requeue')
    elif pending:
        state = 'partial'
    else:
        state = 'clean'
    stale = report.get('stale_check') or {}
    current = stale.get('current') or {}
    judge_sample = report.get('judge_sample') or {}
    production_metrics = report.get('production_metrics') or {}
    next_action = next_action_for(state, report, pending)
    status = {
        'root': root,
        'workflow': report['workflow'],
        'state': state,
        'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec='seconds').replace('+00:00', 'Z'),
        'workflow_meta': report.get('workflow_meta') or {},
        'stale_check': stale,
        'rootmap_sha256': current.get('rootmap_sha256'),
        'selected_key_count': len((report.get('workflow_meta') or {}).get('selected_keys') or report['keys']),
        'workflow_keys': len(report['keys']),
        'root_subcards': total,
        'translated': counts.get('translated', translated),
        'pending': pending,
        'requeue_count': len(report['requeue']),
        'requeue_keys': report['requeue'],
        'requeue_transient_count': len(report.get('requeue_transient') or []),
        'requeue_defect_count': len(report.get('requeue_defect') or []),
        'judge_sample': judge_sample,
        'judge_sample_count': judge_sample.get('sample_count', 0),
        'judge_sample_seed': judge_sample.get('seed'),
        'clean_key_count': judge_sample.get('clean_key_count', 0),
        'next_action': next_action,
        'production_metrics': production_metrics,
        'crashed': report['crashed'],
        'prompt_rules': report.get('prompt_rules'),
        'semantic_risks': {
            'risk_count': (report.get('semantic_risks') or {}).get('risk_count', 0),
            'risky_key_count': (report.get('semantic_risks') or {}).get('risky_key_count', 0),
            'high_confidence_count': (report.get('semantic_risks') or {}).get('high_confidence_count', 0),
            'high_confidence_keys': (report.get('semantic_risks') or {}).get('high_confidence_keys', []),
            'review_queue': (report.get('semantic_risks') or {}).get('review_queue', {}),
        },
        'gates': {name: {'returncode': gate['returncode'],
                         'requeue_count': len(gate.get('requeue') or []),
                         'seconds': gate.get('seconds')}
                  for name, gate in report['gates'].items()},
        'collect_seconds': (report.get('collect') or {}).get('seconds'),
        'glue': {'returncode': glue.get('returncode'),
                 'summary': glue.get('summary'),
                 'nested_exists': glue.get('nested_exists'),
                 'seconds': glue.get('seconds')},
    }
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, 'window_status.json')
    md_path = os.path.join(out_dir, 'window_status.md')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=1)
    lines = [
        '# Window Status',
        '',
        '| field | value |',
        '|---|---:|',
        '| root | %s |' % (root or ''),
        '| state | %s |' % state,
        '| workflow keys | %d |' % len(report['keys']),
        '| root subcards | %d |' % total,
        '| translated | %d |' % status['translated'],
        '| pending | %d |' % pending,
        '| requeue | %d |' % len(report['requeue']),
        '| clean keys | %d |' % judge_sample.get('clean_key_count', 0),
        '| judge sample | %d |' % judge_sample.get('sample_count', 0),
        '| judge sample seed | %s |' % (judge_sample.get('seed') or ''),
        '| next action | %s |' % next_action,
        '| rootmap sha256 | %s |' % ((current.get('rootmap_sha256') or '')[:16]),
        '',
    ]
    if production_metrics:
        lines += ['## Production Metrics', '']
        lines += ['| metric | value |', '|---|---:|']
        for key in sorted(production_metrics):
            lines.append('| %s | %s |' % (key, production_metrics[key]))
        lines.append('')
    if stale.get('errors'):
        lines += ['## Stale Check', '']
        lines += ['- ' + err for err in stale['errors'][:20]]
        if len(stale['errors']) > 20:
            lines.append('- ... %d more' % (len(stale['errors']) - 20))
        lines.append('')
    prompt_rules = report.get('prompt_rules') or {}
    if prompt_rules:
        lines += ['## Manual Rule Coverage', '']
        lines.append('- live harness rules: %s' % ', '.join(
            prompt_rules.get('live_manual_coverage') or []))
        lines.append('- methodology/design only: %s' % ', '.join(
            prompt_rules.get('methodology_only_manuals') or []))
        lines.append('- missing required rules: %d' %
                     prompt_rules.get('missing_rule_count', 0))
        lines.append('')
    semantic = report.get('semantic_risks') or {}
    if semantic:
        lines += ['## Semantic Risk Queue', '']
        lines += ['| metric | value |', '|---|---:|']
        lines.append('| risky keys | %d |' % semantic.get('risky_key_count', 0))
        lines.append('| risks | %d |' % semantic.get('risk_count', 0))
        lines.append('| high-confidence risks | %d |' %
                     semantic.get('high_confidence_count', 0))
        lines.append('| high-confidence keys | %d |' %
                     len(semantic.get('high_confidence_keys') or []))
        lines.append('')
    lines += ['', '## Gates', '', '| gate | exit | requeue | seconds |',
              '|---|---:|---:|---:|']
    for name, gate in status['gates'].items():
        lines.append('| %s | %s | %d | %s |' % (
            name, gate['returncode'], gate['requeue_count'],
            '' if gate['seconds'] is None else gate['seconds']))
    lines += ['', '## Requeue Keys', '']
    lines += report['requeue'] or ['(none)']
    lines += ['', '## Judge Sample Keys', '']
    lines += (judge_sample.get('keys') or ['(none)'])
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    append_ledger(status, out_dir)
    return json_path, md_path


def audit_state(report):
    glue = report.get('glue') or {}
    root = report.get('root')
    rootmap = rootmap_for(root) if root else None
    subkeys = []
    if rootmap:
        rootmap_json = load_json(rootmap)
        subkeys = [row['subkey'] for row in rootmap_json.get('sub_cards', [])]
    total = len(subkeys or report.get('keys') or [])
    counts = glue_counts(glue.get('summary')) or {}
    pending = counts.get('pending')
    if pending is None and total:
        translated = sum(1 for key in (subkeys or report.get('keys') or []) if merged_exists(key))
        pending = max(0, total - translated)
    if report.get('state'):
        return report['state']
    if report.get('crashed'):
        return 'blocked'
    if report.get('requeue'):
        if 'requeue_defect' in report and not report['requeue_defect']:
            return 'transient_only'
        return 'needs_requeue'
    if pending:
        return 'partial'
    return 'clean'


def write_reports(report, write_requeue, write_requeue_file=True, out_dir=None):
    # out_dir defaults to the live OUT dir. An ephemeral/fixture audit (see audit_window.py
    # --ephemeral) passes a throwaway scratch dir so a self-test or temp-file run can NEVER
    # clobber the live singleton window_status.json / audit_window.report.json — the "current
    # status" once reported a temp-file fixture precisely because these names were fixed (FL8).
    out_dir = out_dir or OUT
    os.makedirs(out_dir, exist_ok=True)
    if 'judge_sample' not in report:
        report['judge_sample'] = build_judge_sample(
            report,
            report.get('judge_sample_rate', 0.10),
            report.get('judge_sample_min', 5),
            report.get('judge_sample_seed'))
    json_path = os.path.join(out_dir, 'audit_window.report.json')
    md_path = os.path.join(out_dir, 'audit_window.report.md')
    requeue_path = os.path.join(out_dir, 'requeue.keys.txt')
    judge_sample_path = os.path.join(out_dir, os.path.basename(JUDGE_SAMPLE_FILE))
    requeue_written = bool(write_requeue and write_requeue_file)
    report['requeue_file_written'] = requeue_written
    report.setdefault('requeue_file_preserved', bool(write_requeue and not write_requeue_file))
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

    lines = ['# Audit Window Report', '', 'State: `%s`' % (report.get('state') or 'audited'), '']
    sample = report.get('judge_sample') or {}
    metrics = report.get('production_metrics') or {}
    lines += [
        '| metric | value |',
        '|---|---:|',
        '| workflow keys | %d |' % len(report.get('keys') or []),
        '| clean keys | %d |' % sample.get('clean_key_count', 0),
        '| requeue keys | %d |' % len(report.get('requeue') or []),
        '| judge sample keys | %d |' % sample.get('sample_count', 0),
        '| judge sample seed | %s |' % (sample.get('seed') or ''),
        '',
    ]
    if metrics:
        lines += ['## Production Metrics', '']
        lines += ['| metric | value |', '|---|---:|']
        for key in sorted(metrics):
            lines.append('| %s | %s |' % (key, metrics[key]))
        lines.append('')
    prompt_rules = report.get('prompt_rules') or {}
    if prompt_rules:
        lines += ['## Manual Rule Coverage', '']
        lines.append('Live harness rules: %s.' % ', '.join(
            prompt_rules.get('live_manual_coverage') or []))
        lines.append('Methodology/design only: %s.' % ', '.join(
            prompt_rules.get('methodology_only_manuals') or []))
        lines.append('')
        lines += ['| target | missing required rules |',
                  '|---|---:|']
        for target in prompt_rules.get('targets') or []:
            status = 'missing-file' if not target.get('exists') else len(target.get('missing') or [])
            lines.append('| `%s` | %s |' % (
                os.path.relpath(target['path'], os.path.dirname(HERE)), status))
        lines.append('')
    semantic = report.get('semantic_risks') or {}
    if semantic:
        lines += ['## Semantic Risk Queue', '']
        lines += ['| metric | value |', '|---|---:|']
        lines.append('| risky keys | %d |' % semantic.get('risky_key_count', 0))
        lines.append('| risks | %d |' % semantic.get('risk_count', 0))
        lines.append('| high-confidence risks | %d |' %
                     semantic.get('high_confidence_count', 0))
        lines.append('| high-confidence keys | %d |' %
                     len(semantic.get('high_confidence_keys') or []))
        lines.append('')
        queue = (semantic.get('review_queue') or {}).get('items') or []
        lines += ['| rank | key | score | high-confidence | top risks |',
                  '|---:|---|---:|---:|---|']
        for rank, item in enumerate(queue[:20], 1):
            lines.append('| %d | `%s` | %d | %d | %s |' % (
                rank, item['key'], item['risk_score'],
                item.get('high_confidence_count', 0),
                ', '.join('`%s`' % risk for risk in item.get('top_risks') or [])))
        lines.append('')
    lines.append('| gate | exit | requeue |')
    lines.append('|---|---:|---:|')
    for name, gate in report['gates'].items():
        lines.append('| %s | %s | %d |' % (
            name, gate['returncode'], len(gate.get('requeue') or [])))
    stale = report.get('stale_check') or {}
    if stale.get('errors'):
        lines += ['', '## Stale Check', '']
        lines += ['- ' + err for err in stale['errors'][:30]]
        if len(stale['errors']) > 30:
            lines.append('- ... %d more' % (len(stale['errors']) - 30))
    lines += ['', '## Requeue Keys', '']
    if report.get('state') == 'stale_artifact':
        lines.append('(not generated: stale artifact refused before gates; existing requeue.keys.txt was preserved)')
    else:
        lines += report['requeue'] or ['(none)']
    lines += ['', '## Judge Sample Keys', '']
    lines += sample.get('keys') or ['(none)']
    if report.get('glue'):
        lines += ['', '## Glue', '', report['glue']['summary']]
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    with open(judge_sample_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sample.get('keys') or []) + ('\n' if sample.get('keys') else ''))
    if requeue_written:
        with open(requeue_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report['requeue']) + ('\n' if report['requeue'] else ''))
        # Split files so a cheap transient re-run never triggers expensive defect rework.
        # requeue.defect.fshas.txt (H304): the defect cards' frag_prov content addresses —
        # requeue_from_audit appends these to the TM denylist so the fragment sidecar can
        # never re-serve a gate-flagged fragment.
        for fname, keys_ in (('requeue.transient.keys.txt', report.get('requeue_transient')),
                             ('requeue.defect.keys.txt', report.get('requeue_defect')),
                             ('requeue.defect.fshas.txt', report.get('requeue_defect_fshas'))):
            if keys_ is None:
                continue
            with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f:
                f.write('\n'.join(keys_) + ('\n' if keys_ else ''))
    status_json, status_md = write_window_status(report, out_dir)
    return (json_path, md_path,
            requeue_path if write_requeue and write_requeue_file else None,
            judge_sample_path, status_json, status_md)
