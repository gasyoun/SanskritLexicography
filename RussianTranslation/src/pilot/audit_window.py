#!/usr/bin/env python
"""audit_window.py — one deterministic audit command for a translated workflow window.

Runs the free Python gates against the SAME wf_output.json key set, writes one
machine-readable report plus a requeue list, and optionally glues a root article.

  python src/pilot/audit_window.py wf_output.json --root sTA --write-requeue
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import math
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
LEDGER = os.path.join(OUT, 'window_ledger.jsonl')
JUDGE_SAMPLE_FILE = os.path.join(OUT, 'judge_sample.keys.txt')

sys.path.insert(0, SRC)
import nws_split
from safe_filename import safe_name
from dashboard_events import append_event
from window_common import harness_meta

COLLECT = os.path.join(SRC, '_pilot_collect.py')
BATCH_FILE = os.path.join(OUT, '_realtest_batch.json')
PROTECTED = {'aMSa', 'anna', 'ap'}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    return json.load(open(path, encoding='utf-8'))


def run_py(args, env=None):
    t0 = time.perf_counter()
    p = subprocess.run([sys.executable] + args, cwd=SRC, capture_output=True,
                       text=True, encoding='utf-8', env=env)
    return {'argv': [sys.executable] + args, 'returncode': p.returncode,
            'stdout': p.stdout, 'stderr': p.stderr,
            'seconds': round(time.perf_counter() - t0, 3)}


def find_results_container(o):
    if isinstance(o, dict):
        if isinstance(o.get('results'), list):
            return o
        for v in o.values():
            r = find_results_container(v)
            if r is not None:
                return r
    if isinstance(o, list):
        for v in o:
            r = find_results_container(v)
            if r is not None:
                return r
    return None


def find_results(o):
    container = find_results_container(o)
    return container.get('results') if container else None


def workflow_payload(path):
    payload = load_json(path)
    container = find_results_container(payload) or {}
    results = container.get('results') or []
    if isinstance(container.get('meta'), dict):
        meta = container['meta']
    elif isinstance(payload, dict) and isinstance(payload.get('meta'), dict):
        meta = payload['meta']
    else:
        meta = {}
    keys, nulls = [], []
    for r in results:
        k = r.get('key')
        if not k:
            continue
        keys.append(k)
        if not r.get('card'):
            nulls.append(k)
    return payload, meta, results, keys, nulls


def workflow_keys(path):
    return workflow_payload(path)[3:5]


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


def merged_exists(key):
    return (exact_file_exists(OUT, safe_name(key) + '.merged.md')
            or exact_file_exists(OUT, key + '.merged.md'))


def rootmap_for(root):
    if not root:
        return None
    for stem in (safe_name(root), root):
        p = os.path.join(HERE, 'input', stem + '.rootmap.json')
        if os.path.exists(p):
            return p
    return None


def input_paths(key):
    return (os.path.join(HERE, 'input', key + '.raw.txt'),
            os.path.join(HERE, 'input', key + '.portrait.json'))


def current_root_provenance(root, selected_keys=None):
    rp = rootmap_for(root)
    if not rp:
        return {'ok': False, 'rootmap_path': None, 'error': 'no rootmap for %r' % root}
    rm = load_json(rp)
    root_keys = [s['subkey'] for s in rm.get('sub_cards', [])]
    keys = selected_keys or root_keys
    input_hashes = {}
    missing = []
    for k in keys:
        rawp, portraitp = input_paths(k)
        rec = {}
        if os.path.exists(rawp):
            rec['raw_sha256'] = sha256_file(rawp)
        else:
            missing.append(k + '.raw.txt')
        if os.path.exists(portraitp):
            rec['portrait_sha256'] = sha256_file(portraitp)
        else:
            missing.append(k + '.portrait.json')
        input_hashes[k] = rec
    return {
        'ok': True,
        'root': root,
        'safe_root': safe_name(root),
        'rootmap_path': rp,
        'rootmap_sha256': sha256_file(rp),
        'root_keys': root_keys,
        'selected_keys': keys,
        'input_hashes': input_hashes,
        'missing_inputs': missing,
    }


def stale_check(root, wf_meta, wf_keys):
    check = {'ok': True, 'stale': False, 'warnings': [], 'errors': [],
             'workflow_meta': wf_meta or {}, 'current': None}
    if not root:
        check['warnings'].append('no --root supplied; rootmap/input staleness was not checked')
        return check
    if not wf_meta:
        check['ok'] = False
        check['stale'] = True
        check['errors'].append('workflow meta missing from wf_output; fresh Max output is required')
        selected_keys = None
    else:
        selected_keys = wf_meta.get('selected_keys') or None
    current = current_root_provenance(root, selected_keys)
    check['current'] = current
    if not current.get('ok'):
        check['ok'] = False
        check['stale'] = True
        check['errors'].append(current.get('error') or 'root provenance unavailable')
        return check

    root_keys = current['root_keys']
    expected_keys = current['selected_keys']
    if selected_keys:
        invalid = sorted(set(selected_keys) - set(root_keys))
        if invalid:
            check['errors'].append('workflow selected keys not in current rootmap: %s' %
                                   ', '.join(invalid[:12]))
    if wf_keys != expected_keys:
        missing = sorted(set(expected_keys) - set(wf_keys))
        unexpected = sorted(set(wf_keys) - set(expected_keys))
        check['errors'].append('workflow keys do not match current selected rootmap keys '
                               '(workflow=%d expected=%d missing=%d unexpected=%d)' %
                               (len(wf_keys), len(expected_keys), len(missing), len(unexpected)))
        check['missing_keys'] = missing
        check['unexpected_keys'] = unexpected
    if current['missing_inputs']:
        check['errors'].append('current raw/portrait inputs missing: %s' %
                               ', '.join(current['missing_inputs'][:12]))

    if wf_meta:
        if wf_meta.get('root') and wf_meta.get('root') != root:
            check['errors'].append('workflow root %r != requested root %r' %
                                   (wf_meta.get('root'), root))
        if wf_meta.get('safe_root') and wf_meta.get('safe_root') != safe_name(root):
            check['errors'].append('workflow safe_root %r != current safe_root %r' %
                                   (wf_meta.get('safe_root'), safe_name(root)))
        if wf_meta.get('rootmap_sha256') != current['rootmap_sha256']:
            check['errors'].append('rootmap hash mismatch')
        wf_hashes = wf_meta.get('input_hashes') or {}
        for k in expected_keys:
            got = wf_hashes.get(k)
            cur = current['input_hashes'].get(k) or {}
            if not got:
                check['errors'].append('missing workflow input hash for %s' % k)
                continue
            if got.get('raw_sha256') != cur.get('raw_sha256'):
                check['errors'].append('raw hash mismatch for %s' % k)
            if got.get('portrait_sha256') != cur.get('portrait_sha256'):
                check['errors'].append('portrait hash mismatch for %s' % k)

    if check['errors']:
        check['ok'] = False
        check['stale'] = True
    return check


def glue_counts(summary):
    m = re.search(r':\s*(\d+)\s+sub-cards\s+\((\d+)\s+translated,\s+(\d+)\s+pending\)', summary or '')
    if not m:
        return None
    return {'subcards': int(m.group(1)), 'translated': int(m.group(2)), 'pending': int(m.group(3))}


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
    clean = [k for k in all_keys if k not in set(requeue) and k not in set(report.get('null_cards') or [])]
    clean = [k for k in clean if merged_exists(k)]
    sample_seed = seed or default_judge_sample_seed(report, rate, minimum)
    if report.get('state') == 'stale_artifact':
        clean = []
        clean_sample = []
    elif clean:
        target = int(math.ceil(len(clean) * rate))
        target = max(minimum, target)
        target = min(len(clean), target)
        ranked = sorted(clean, key=lambda k: hashlib.sha256((sample_seed + '\0' + k).encode('utf-8')).hexdigest())
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
    return {k: v for k, v in fields.items() if v not in (None, '')}


def harness_matches_current_root(report):
    root = report.get('root')
    stale = report.get('stale_check') or {}
    current = stale.get('current') or {}
    expected = current.get('selected_keys') or []
    meta = harness_meta(os.path.join(HERE, 'run_pilot_wf.opt.js'))
    if not root or not current.get('rootmap_sha256') or not expected:
        return False, meta
    if not meta.get('ok'):
        return False, meta
    ok = (
        meta.get('root') == root and
        meta.get('rootmap_sha256') == current.get('rootmap_sha256') and
        (meta.get('selected_keys') or []) == expected
    )
    if not ok:
        meta['scope_error'] = 'harness scope does not match current rootmap selection'
    return ok, meta


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
    if report.get('requeue'):
        return 'Run python src\\pilot\\requeue_from_audit.py %s, rerun Max Workflow, then rerun audit_window.py.' % root
    if pending:
        return 'Translate pending sub-cards for %s, then rerun audit_window.py.' % root
    if sample.get('sample_count'):
        return 'Send judge_sample.keys.txt to sampled semantic judging outside Python.'
    return 'Window is mechanically clean; advance to the next frequency root.'


def write_window_status(report):
    root = report.get('root')
    rootmap = rootmap_for(root)
    subkeys = []
    if rootmap:
        rm = load_json(rootmap)
        subkeys = [s['subkey'] for s in rm.get('sub_cards', [])]
    translated = sum(1 for k in (subkeys or report['keys']) if merged_exists(k))
    total = len(subkeys or report['keys'])
    glue = report.get('glue') or {}
    counts = glue_counts(glue.get('summary')) or {}
    pending = counts.get('pending', max(0, total - translated))
    if report.get('state'):
        state = report['state']
    elif report['crashed']:
        state = 'blocked'
    elif report['requeue']:
        state = 'needs_requeue'
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
        'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
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
        'judge_sample': judge_sample,
        'judge_sample_count': judge_sample.get('sample_count', 0),
        'judge_sample_seed': judge_sample.get('seed'),
        'clean_key_count': judge_sample.get('clean_key_count', 0),
        'next_action': next_action,
        'production_metrics': production_metrics,
        'crashed': report['crashed'],
        'gates': {name: {'returncode': g['returncode'],
                         'requeue_count': len(g.get('requeue') or []),
                         'seconds': g.get('seconds')}
                  for name, g in report['gates'].items()},
        'collect_seconds': (report.get('collect') or {}).get('seconds'),
        'glue': {'returncode': glue.get('returncode'),
                 'summary': glue.get('summary'),
                 'nested_exists': glue.get('nested_exists'),
                 'seconds': glue.get('seconds')},
    }
    jp = os.path.join(OUT, 'window_status.json')
    mp = os.path.join(OUT, 'window_status.md')
    json.dump(status, open(jp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
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
        lines += ['- ' + e for e in stale['errors'][:20]]
        if len(stale['errors']) > 20:
            lines.append('- ... %d more' % (len(stale['errors']) - 20))
        lines.append('')
    lines += [
        '## Gates',
        '',
        '| gate | exit | requeue | seconds |',
        '|---|---:|---:|---:|',
    ]
    for name, gate in status['gates'].items():
        lines.append('| %s | %s | %d | %s |' % (
            name, gate['returncode'], gate['requeue_count'],
            '' if gate['seconds'] is None else gate['seconds']))
    lines += ['', '## Requeue Keys', '']
    lines += report['requeue'] or ['(none)']
    lines += ['', '## Judge Sample Keys', '']
    lines += (judge_sample.get('keys') or ['(none)'])
    open(mp, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    append_ledger(status)
    return jp, mp


def audit_state(report):
    glue = report.get('glue') or {}
    root = report.get('root')
    rootmap = rootmap_for(root)
    subkeys = []
    if rootmap:
        rm = load_json(rootmap)
        subkeys = [s['subkey'] for s in rm.get('sub_cards', [])]
    total = len(subkeys or report.get('keys') or [])
    counts = glue_counts(glue.get('summary')) or {}
    translated = counts.get('translated')
    pending = counts.get('pending')
    if pending is None and total:
        translated = sum(1 for k in (subkeys or report.get('keys') or []) if merged_exists(k))
        pending = max(0, total - translated)
    if report.get('state'):
        return report['state']
    if report.get('crashed'):
        return 'blocked'
    if report.get('requeue'):
        return 'needs_requeue'
    if pending:
        return 'partial'
    return 'clean'


def emit_audit_event(event_type, level='info', root=None, state=None, summary='', data=None):
    append_event('audit_window', event_type, level=level, root=root,
                 state=state, summary=summary, data=data or {})


def append_ledger(status):
    os.makedirs(OUT, exist_ok=True)
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
        'judge_sample_count': status.get('judge_sample_count'),
        'judge_sample_seed': status.get('judge_sample_seed'),
        'clean_key_count': status.get('clean_key_count'),
        'next_action': status.get('next_action'),
        'production_metrics': status.get('production_metrics'),
        'crashed': status.get('crashed'),
        'rootmap_sha256': status.get('rootmap_sha256'),
    }
    with open(LEDGER, 'a', encoding='utf-8') as f:
        f.write(json.dumps(compact, ensure_ascii=False) + '\n')


def write_reports(report, write_requeue, write_requeue_file=True):
    os.makedirs(OUT, exist_ok=True)
    if 'judge_sample' not in report:
        report['judge_sample'] = build_judge_sample(
            report,
            report.get('judge_sample_rate', 0.10),
            report.get('judge_sample_min', 5),
            report.get('judge_sample_seed'))
    json_path = os.path.join(OUT, 'audit_window.report.json')
    md_path = os.path.join(OUT, 'audit_window.report.md')
    rq_path = os.path.join(OUT, 'requeue.keys.txt')
    js_path = JUDGE_SAMPLE_FILE
    requeue_written = bool(write_requeue and write_requeue_file)
    report['requeue_file_written'] = requeue_written
    report.setdefault('requeue_file_preserved', bool(write_requeue and not write_requeue_file))
    json.dump(report, open(json_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

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
    lines.append('| gate | exit | requeue |')
    lines.append('|---|---:|---:|')
    for name, gate in report['gates'].items():
        lines.append('| %s | %s | %d |' % (name, gate['returncode'], len(gate.get('requeue') or [])))
    stale = report.get('stale_check') or {}
    if stale.get('errors'):
        lines += ['', '## Stale Check', '']
        lines += ['- ' + e for e in stale['errors'][:30]]
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
    open(md_path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    open(js_path, 'w', encoding='utf-8').write('\n'.join(sample.get('keys') or []) + ('\n' if sample.get('keys') else ''))
    if requeue_written:
        open(rq_path, 'w', encoding='utf-8').write('\n'.join(report['requeue']) + ('\n' if report['requeue'] else ''))
    status_json, status_md = write_window_status(report)
    return json_path, md_path, rq_path if write_requeue and write_requeue_file else None, js_path, status_json, status_md


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
        for name, cmd, parser in commands:
            futures[ex.submit(run_py, cmd)] = (name, parser)
        for fut in concurrent.futures.as_completed(futures):
            name, parser = futures[fut]
            res = fut.result()
            if parser:
                res['requeue'] = parser(res['stdout'])
            gates[name] = res

    for name in ['nws', 'translation', 'coverage', 'sense_dupes']:
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
