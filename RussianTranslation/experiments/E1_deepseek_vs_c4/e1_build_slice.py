#!/usr/bin/env python
"""H2488 — build gen_opt manifest + prep_slice payload for the frozen 40 keys."""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.normpath(os.path.join(HERE, '..', '..'))
PILOT = os.path.join(RT, 'src', 'pilot')
RUN = os.path.join(HERE, 'run')
WT_INPUT = os.path.join(PILOT, 'input')
CARD_IDS = os.path.join(PILOT, 'h1210', 'card_ids.txt')


def main():
    os.makedirs(RUN, exist_ok=True)
    ids = [ln.strip() for ln in open(CARD_IDS, encoding='utf-8') if ln.strip()][:40]
    keys = ','.join(ids)
    env = os.environ.copy()
    env['PWG_INPUT_DIR'] = WT_INPUT
    man_out = os.path.join(RUN, 'e1_40.manifest.json')
    js_out = os.path.join(RUN, 'e1_40.opt2.js')
    payload = os.path.join(RUN, 'e1_40.slice_payload.json')
    cmd1 = [
        sys.executable, os.path.join(PILOT, 'gen_opt_harness2.py'),
        '_nominal', '--nominal', '--no-selfheal', '--no-tm',
        '--keys=' + keys,
        '--manifest-out=' + man_out,
        '--out=' + js_out,
    ]
    print('gen_opt', ' '.join(cmd1[-4:]))
    r1 = subprocess.run(cmd1, env=env, cwd=RT, encoding='utf-8')
    print('gen_opt_exit', r1.returncode)
    if r1.returncode != 0:
        return r1.returncode
    cmd2 = [
        sys.executable, os.path.join(PILOT, 'h1209', 'prep_slice.py'),
        man_out, payload,
    ]
    print('prep_slice')
    r2 = subprocess.run(cmd2, env=env, cwd=RT, encoding='utf-8')
    print('prep_slice_exit', r2.returncode)
    if r2.returncode == 0 and os.path.exists(payload):
        sl = json.load(open(payload, encoding='utf-8'))
        print('payload_cards', len(sl.get('cards') or []))
    return r2.returncode


if __name__ == '__main__':
    sys.exit(main())
