#!/usr/bin/env python
"""Build an optimized rerun harness from the latest audit_window requeue file.

  python src/pilot/requeue_from_audit.py sTA
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'output')
INP = os.path.join(HERE, 'input')
REQUEUE = os.path.join(OUT, 'requeue.keys.txt')

sys.path.insert(0, SRC)
from safe_filename import safe_name


def rootmap_path(root):
    for stem in (safe_name(root), root):
        p = os.path.join(INP, stem + '.rootmap.json')
        if os.path.exists(p):
            return p
    return None


def read_requeue():
    if not os.path.exists(REQUEUE):
        sys.exit('no %s — run audit_window.py --write-requeue first' % REQUEUE)
    keys = [ln.strip() for ln in open(REQUEUE, encoding='utf-8') if ln.strip()]
    if not keys:
        sys.exit('empty requeue file: %s' % REQUEUE)
    return keys


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else ''
    if not root:
        sys.exit('usage: python src/pilot/requeue_from_audit.py <root>')
    rp = rootmap_path(root)
    if not rp:
        sys.exit('no rootmap for %r under %s' % (root, INP))
    rm = json.load(open(rp, encoding='utf-8'))
    declared = {s['subkey'] for s in rm.get('sub_cards', [])}
    suffixes = {k.split('~~')[-1]: k for k in declared}
    keys = read_requeue()
    resolved, invalid = [], []
    for k in keys:
        full = k if k in declared else suffixes.get(k)
        if full and os.path.exists(os.path.join(INP, full + '.raw.txt')):
            resolved.append(full)
        else:
            invalid.append(k)
    if invalid:
        print('invalid/stale requeue keys:')
        for k in invalid:
            print('  ' + k)
        sys.exit(1)

    cmd = [sys.executable, os.path.join(HERE, 'gen_opt_harness.py'),
           root, '--keys=' + ','.join(resolved)]
    p = subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(HERE)),
                       text=True, encoding='utf-8', capture_output=True)
    if p.stdout.strip():
        print(p.stdout.rstrip())
    if p.stderr.strip():
        print(p.stderr.rstrip(), file=sys.stderr)
    if p.returncode:
        sys.exit(p.returncode)

    harness = os.path.join(HERE, 'run_pilot_wf.opt.js')
    print('requeue root      : %s' % root)
    print('requeue keys      : %d' % len(resolved))
    print('generated harness : %s' % harness)
    print('keys:')
    for k in resolved:
        print('  ' + k)


if __name__ == '__main__':
    main()
