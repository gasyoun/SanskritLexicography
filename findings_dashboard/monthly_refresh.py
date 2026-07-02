#!/usr/bin/env python3
"""Monthly local refresh of the FINDINGS dashboard — Task Scheduler entrypoint.

Works in throwaway git worktrees so it never touches whatever branch the main
checkout happens to be on (this repo sees concurrent sessions switching
branches mid-day):

  1. worktree off origin/master → build_findings_data.py + probe_platforms.py
     → commit data files to master → push
  2. worktree off origin/gh-pages → copy dashboard files into findings/
     → commit → push

Scheduled task (already registered; re-create with):
  schtasks /Create /SC MONTHLY /D 3 /ST 09:30 /TN "SL findings dashboard refresh" ^
    /TR "cmd /c python C:\\Users\\user\\Documents\\GitHub\\SanskritLexicography\\findings_dashboard\\monthly_refresh.py >> C:\\Users\\user\\Documents\\GitHub\\SanskritLexicography\\findings_dashboard\\refresh.log 2>&1"
"""

import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

REPO = Path(__file__).resolve().parent.parent
PUBLISH = ['index.html', 'data.json', 'timeseries.json', 'platform_status.json']


def run(cmd, cwd):
    print('  $', ' '.join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def main():
    print(f"=== findings dashboard refresh {datetime.now().isoformat(timespec='seconds')} ===")
    run(['git', 'fetch', 'origin', 'master', 'gh-pages'], REPO)
    tmp = Path(tempfile.mkdtemp(prefix='findings-dash-'))
    wt_m, wt_p = tmp / 'master', tmp / 'pages'
    try:
        run(['git', 'worktree', 'add', '--detach', str(wt_m), 'origin/master'], REPO)
        run([sys.executable, str(wt_m / 'findings_dashboard' / 'build_findings_data.py')], wt_m)
        run([sys.executable, str(wt_m / 'findings_dashboard' / 'probe_platforms.py')], wt_m)
        run(['git', 'add', 'findings_dashboard'], wt_m)
        diff = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=wt_m)
        if diff.returncode != 0:
            run(['git', 'commit', '-m',
                 'chore(findings-dashboard): monthly data refresh [skip ci]'], wt_m)
            run(['git', 'push', 'origin', 'HEAD:master'], wt_m)
        else:
            print('  master: no data changes')

        run(['git', 'worktree', 'add', '--detach', str(wt_p), 'origin/gh-pages'], REPO)
        dest = wt_p / 'findings'
        dest.mkdir(exist_ok=True)
        for f in PUBLISH:
            src = wt_m / 'findings_dashboard' / f
            if src.exists():
                shutil.copy2(src, dest / f)
        run(['git', 'add', 'findings'], wt_p)
        diff = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=wt_p)
        if diff.returncode != 0:
            run(['git', 'commit', '-m',
                 'chore(findings-dashboard): publish monthly refresh'], wt_p)
            run(['git', 'push', 'origin', 'HEAD:gh-pages'], wt_p)
        else:
            print('  gh-pages: no changes')
    finally:
        for wt in (wt_m, wt_p):
            subprocess.run(['git', 'worktree', 'remove', '--force', str(wt)],
                           cwd=REPO, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)
    print('=== done ===')


if __name__ == '__main__':
    main()
