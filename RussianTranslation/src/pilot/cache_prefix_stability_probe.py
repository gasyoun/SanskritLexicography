"""Decide WHY every headless call re-creates ~50k tokens of cache (PR #986's open hypothesis).

#986 left two candidates: (a) the cache prefix is not stable across `claude -p`
invocations, or (b) the TTL lapses between 2-3 minute calls. H2152's ping already
narrows it: the write went to `ephemeral_1h_input_tokens`, and a 1-hour TTL cannot
expire between calls minutes apart. This probe confirms by firing identical calls
back-to-back and watching cache_creation vs cache_read.

Two arms, because the fix is in the second one:
  repo  -- cwd = the SanskritLexicography worktree (CLAUDE.md + git context injected)
  bare  -- cwd = an empty temp dir (no CLAUDE.md, no git repo, no project context)

If `bare` creates materially less than `repo`, the varying prefix is project context
injection and the mitigation is to run the paid lane from a fixed minimal cwd.

Read-only apart from the paid calls themselves. Prints a table; writes nothing.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding='utf-8')

CONFIG_DIR = r'D:\ClaudeTools\profiles\claude4\.claude'
PROMPT = 'Reply with exactly: ok'
REPO_CWD = r'C:\Users\user\Documents\GitHub\SanskritLexicography'
N = 2

# The Windows npm launcher is a .cmd shim that subprocess cannot exec directly (the
# H818 defect). headless_worker.claude_argv_prefix already resolves it to
# [node, <cli>.cjs] -- reuse it rather than re-deriving the resolution.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from headless_worker import claude_argv_prefix  # noqa: E402

ARGV = claude_argv_prefix('claude') + [
    '-p', PROMPT, '--model', 'claude-sonnet-5',
    '--output-format', 'json', '--max-turns', '1']


def one_call(cwd):
    env = dict(os.environ, CLAUDE_CONFIG_DIR=CONFIG_DIR)
    start = time.monotonic()
    try:
        proc = subprocess.run(ARGV, cwd=cwd, env=env, capture_output=True,
                              encoding='utf-8', timeout=200)
    except subprocess.TimeoutExpired:
        return {'error': 'timeout at 200s', 'wall_ms': 200000}
    wall = int((time.monotonic() - start) * 1000)
    try:
        w = json.loads(proc.stdout)
    except Exception as exc:
        return {'error': 'unparseable envelope: %s' % exc, 'wall_ms': wall}
    u = w.get('usage', {}) or {}
    cc = u.get('cache_creation', {}) or {}
    return {
        'wall_ms': wall,
        'api_ms': w.get('duration_api_ms'),
        'create': u.get('cache_creation_input_tokens'),
        'read': u.get('cache_read_input_tokens'),
        'out': u.get('output_tokens'),
        'ttl_1h': cc.get('ephemeral_1h_input_tokens'),
        'ttl_5m': cc.get('ephemeral_5m_input_tokens'),
        'usd': w.get('total_cost_usd'),
    }


def main():
    bare = tempfile.mkdtemp(prefix='c4probe-')
    rows = []
    for arm, cwd in (('repo', REPO_CWD), ('bare', bare)):
        for i in range(1, N + 1):
            r = one_call(cwd)
            r['arm'], r['n'] = arm, i
            rows.append(r)
            print('%-5s #%d  %s' % (arm, i, json.dumps(r, ensure_ascii=False)))

    print('\n%-5s %-3s %9s %9s %9s %9s %8s' %
          ('arm', '#', 'wall_ms', 'api_ms', 'create', 'read', 'usd'))
    for r in rows:
        if 'error' in r:
            print('%-5s %-3d %9d  %s' % (r['arm'], r['n'], r['wall_ms'], r['error']))
            continue
        print('%-5s %-3d %9d %9s %9s %9s %8.4f' %
              (r['arm'], r['n'], r['wall_ms'], r['api_ms'], r['create'],
               r['read'], r['usd'] or 0.0))

    good = [r for r in rows if 'error' not in r and r['create'] is not None]
    if len(good) >= 2:
        total = sum(r['usd'] or 0 for r in good)
        print('\ntotal spend on this probe: $%.4f over %d calls' % (total, len(good)))


if __name__ == '__main__':
    main()
