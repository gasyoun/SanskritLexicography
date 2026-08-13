#!/usr/bin/env python
"""H2488 — generate the 40 E1 raw/portrait inputs into the worktree input dir."""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
WT_INPUT = os.path.normpath(os.path.join(HERE, '..', '..', 'src', 'pilot', 'input'))
MAN = os.path.join(HERE, 'sample_manifest.json')
GEN = os.path.join(
    r'C:\Users\user\Documents\GitHub\SanskritLexicography',
    'RussianTranslation', 'src', '_pilot_gen_merged.py')


def main():
    keys = json.load(open(MAN, encoding='utf-8'))['keys']
    os.makedirs(WT_INPUT, exist_ok=True)
    env = os.environ.copy()
    env['PWG_INPUT_DIR'] = WT_INPUT
    print('PWG_INPUT_DIR', WT_INPUT)
    print('keys', len(keys))
    cmd = [sys.executable, GEN] + keys
    r = subprocess.run(cmd, env=env, cwd=os.path.dirname(GEN), encoding='utf-8')
    print('gen_exit', r.returncode)
    return r.returncode


if __name__ == '__main__':
    sys.exit(main())
