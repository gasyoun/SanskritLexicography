#!/usr/bin/env python
"""H2253 / #1000 — bisect the h1339_offline_bench signature across commits.

Creates a throwaway worktree per commit, runs ONE bench run (no warmups), and
records the printed signature (or the failure reason). Offline only: the bench
never issues a paid call.
"""
import os
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

#: The canonical checkout to cut throwaway worktrees from. Overridable so the rig is not
#: welded to one machine: $SL_REPO, else this file's own repo root.
REPO = os.environ.get('SL_REPO') or os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SIG_RE = re.compile(r'sig ([0-9a-f]{10})')


def git(args, cwd=REPO, check=True):
    return subprocess.run(['git'] + args, cwd=cwd, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', check=check)


def run_at(commit):
    wt = os.path.join(tempfile.gettempdir(), 'h2253bisect_%s' % commit[:9])
    subprocess.run(['git', 'worktree', 'remove', '--force', wt], cwd=REPO,
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
    r = git(['worktree', 'add', '--detach', wt, commit], check=False)
    if r.returncode:
        return commit, 'WORKTREE-FAIL', r.stderr.strip()[-200:]
    try:
        rt = os.path.join(wt, 'RussianTranslation')
        bench = os.path.join(rt, 'src', 'pilot', 'h1339_offline_bench.py')
        if not os.path.isfile(bench):
            return commit, 'NO-BENCH', bench
        p = subprocess.run([sys.executable, bench, '--warmups', '0', '--runs', '1'],
                           cwd=rt, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=1800)
        out = (p.stdout or '') + (p.stderr or '')
        m = SIG_RE.search(out)
        if m:
            fx = re.search(r'content hash ([0-9a-f]+)', out)
            return commit, m.group(1), 'fixture=%s' % (fx.group(1) if fx else '?')
        first = [l for l in out.splitlines() if l.strip()]
        return commit, 'FAIL', ' / '.join(first[-3:])[:220]
    finally:
        subprocess.run(['git', 'worktree', 'remove', '--force', wt], cwd=REPO,
                       capture_output=True, text=True, encoding='utf-8', errors='replace')


def main():
    commits = sys.argv[1:]
    print('%-12s %-14s %s' % ('commit', 'signature', 'note'))
    print('-' * 100)
    for c in commits:
        sha, sig, note = run_at(c)
        date = git(['log', '-1', '--format=%ad', '--date=short', c], check=False).stdout.strip()
        print('%-12s %-14s %s  %s' % (sha[:10], sig, date, note))
        sys.stdout.flush()


if __name__ == '__main__':
    main()
