#!/usr/bin/env python
"""H2676 — rebuild gen_opt manifest + prep_slice payload for the frozen Q3 keys."""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.normpath(os.path.join(HERE, '..', '..'))
PILOT = os.path.join(RT, 'src', 'pilot')
SAMPLE = os.path.join(HERE, 'sample_keys.json')


def main():
    sample = json.load(open(SAMPLE, encoding='utf-8'))
    slp = list(sample['main_arm']['keys']) + list(sample['optional_max_subarm']['keys'])
    env = os.environ.copy()
    env['PWG_INPUT_DIR'] = os.path.join(PILOT, 'input')
    man_out = os.path.join(HERE, 'h2676.manifest.json')
    js_out = os.path.join(HERE, 'h2676.opt2.js')
    payload = os.path.join(HERE, 'slice_payload.json')
    cmd1 = [
        sys.executable, os.path.join(PILOT, 'gen_opt_harness2.py'),
        '_nominal', '--nominal', '--no-selfheal', '--no-tm',
        '--keys=' + ','.join(slp),
        '--manifest-out=' + man_out,
        '--out=' + js_out,
    ]
    print('gen_opt n=%d' % len(slp), flush=True)
    r1 = subprocess.run(cmd1, env=env, cwd=RT, encoding='utf-8')
    print('gen_opt_exit', r1.returncode, flush=True)
    if r1.returncode != 0:
        return r1.returncode
    cmd2 = [
        sys.executable, os.path.join(PILOT, 'h1209', 'prep_slice.py'),
        man_out, payload,
    ]
    print('prep_slice', flush=True)
    r2 = subprocess.run(cmd2, env=env, cwd=RT, encoding='utf-8')
    print('prep_slice_exit', r2.returncode, flush=True)
    if r2.returncode != 0:
        return r2.returncode
    sl = json.load(open(payload, encoding='utf-8'))
    man = json.load(open(man_out, encoding='utf-8'))
    keymap = (man.get('meta') or {}).get('nominal_keymap') or {}
    rev = {v: k for k, v in keymap.items()}
    main_payload = [rev[k] for k in sample['main_arm']['keys'] if k in rev]
    max_payload = [rev[k] for k in sample['optional_max_subarm']['keys'] if k in rev]
    map_path = os.path.join(HERE, 'payload_key_map.json')
    with open(map_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({
            'schema': 'pwg.h2676_payload_key_map.v1',
            'n_cards': len(sl.get('cards') or []),
            'main_payload_keys': main_payload,
            'max_payload_keys': max_payload,
            'nominal_keymap': keymap,
        }, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('payload_cards', len(sl.get('cards') or []))
    print('main_payload', len(main_payload), ','.join(main_payload))
    if len(main_payload) != 22:
        print('FAIL: expected 22 main payload keys, got', len(main_payload))
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
