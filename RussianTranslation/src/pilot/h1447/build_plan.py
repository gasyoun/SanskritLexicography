#!/usr/bin/env python
"""H1447: assemble the prepared medium50 serial-c4 plan JSON from the 5 prepared leases."""
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

WINDOWS = ['h1447-m50-w1', 'h1447-m50-w2', 'h1447-m50-w3', 'h1447-m50-w4', 'h1447-m50-w5']
BASE = os.path.join('src', 'pilot', 'output', 'coordinator', 'artifacts')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''):
            h.update(ch)
    return h.hexdigest()


def rel(p):
    return os.path.relpath(p).replace(os.sep, '/')


def main():
    state = json.load(open(os.path.join('src', 'pilot', 'output', 'coordinator', 'state.json'),
                           encoding='utf-8'))
    leases = {l['id']: l for l in state['leases']}
    windows = []
    for w in WINDOWS:
        adir = os.path.join(BASE, w)
        harness = os.path.join(adir, 'run_pilot_wf.%s.js' % w)
        manifest = os.path.join(adir, 'execution_manifest.%s.json' % w)
        preflight = os.path.join(adir, 'preflight.json')
        man = json.load(open(manifest, encoding='utf-8'))
        pf = json.load(open(preflight, encoding='utf-8'))
        lease = leases[w]
        if lease['state'] != 'prepared':
            raise SystemExit('%s not prepared: %s' % (w, lease['state']))
        windows.append({
            'root': w,
            'mode': 'medium50',
            'headwords': lease['details']['keys'],
            'subcards': man['meta']['selected_keys'],
            'harness': rel(harness),
            'workflow_output': None,
            'preflight': rel(preflight),
            'headless': {
                'execution_manifest': rel(manifest),
                'manifest_sha256': sha(manifest),
                'harness_sha256': sha(harness),
                'presplit_keys': man['meta'].get('presplit_keys') or [],
                'projected_calls': pf.get('agent_expected_after_tm'),
            },
        })
    w1_man = json.load(open(os.path.join(BASE, 'h1447-m50-w1',
                                         'execution_manifest.h1447-m50-w1.json'),
                            encoding='utf-8'))
    plan = {
        'schema': 'pwg.no_pwg_scale_plan.v1',
        'plan_kind': 'h1447_medium50_serial_c4',
        'worklist': 'src/pilot/H317_medium50_worklist.08.07.26.json',
        'worklist_schema': 'pwg.h317_medium50_selection.v1',
        'excluded_already_promoted': ['yuvan', 'ftvij'],
        'baseline_commit': 'e603e47c29cd880075b35e155e44b5ce8f46a445',
        'baseline_describe': 'v1.55.0-4-ge603e47c',
        'profile_slot': 'c4',
        'config_dir_fingerprint': w1_man['execution']['config_dir_fingerprint'],
        'prepared_windows': len(windows),
        'selected_headwords': sum(len(w['headwords']) for w in windows),
        'selected_subcards': sum(len(w['subcards']) for w in windows),
        'projected_calls': sum(w['headless']['projected_calls'] for w in windows),
        'windows': windows,
    }
    out = os.path.join('src', 'pilot', 'output', 'h1447_medium50_plan.v1.json')
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print('wrote', out)
    print('windows: %d | headwords: %d | subcards: %d | projected calls: %d'
          % (len(windows), plan['selected_headwords'], plan['selected_subcards'],
             plan['projected_calls']))
    print('starter w1 projected_calls:', windows[0]['headless']['projected_calls'])


if __name__ == '__main__':
    main()
