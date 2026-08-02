"""H2158 -- is the CLI lane alive at all, or is every call hanging?

Phase 1's CLI arm returned 3/3 timeouts at exactly HARD_TIMEOUT_MS with no envelope.
That shape has two very different causes and they demand opposite responses:

  * account-level refusal -- FINDINGS 270: a rate-limited CLI HANGS instead of
    returning 429, so an exhausted account is indistinguishable from a slow call
    until something cheap succeeds or fails alongside it. Nothing about the pwg_ru
    prompt is at fault and no amount of re-running helps.
  * prompt/route-level -- the ~25 KB translation prompt specifically cannot finish,
    while trivial calls sail through.

ONE trivial call discriminates them: `--max-turns 1`, a 5-token prompt, bare cwd,
the same profile config dir the paid lane uses. If THIS hangs, the lane is down and
the H2158 measurement is blocked on the account, not on anything in this handoff.

Deliberately not the same thing as `/pwg-live-gate`: that gate judges readiness for a
paid WINDOW on a representative >=5 KB call. This asks the strictly smaller question
"does any call at all come back", which is what tells you whether running the gate is
even worth its spend.

    python src/pilot/h2158_liveness_probe.py [--timeout 90]

Model: authored by Opus 5 (`claude-opus-5`) for handoff H2158.
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from headless_worker import bare_cli_cwd, claude_argv_prefix         # noqa: E402

CONFIG_DIR = r'D:\ClaudeTools\profiles\claude4\.claude'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument('--timeout', type=float, default=90.0)
    ap.add_argument('--model', default='claude-sonnet-5')
    ap.add_argument('--max-turns', dest='max_turns', default=None,
                    help="pass --max-turns N. Omitted by default: `--max-turns 1` makes the "
                         "envelope come back is_error=True even on a call that answered, "
                         "which is indistinguishable from a real failure at a glance.")
    ap.add_argument('--out', default=os.path.join(
        os.path.dirname(os.path.dirname(here)), 'pwg_ru', 'h2158', 'raw'))
    ap.add_argument('--tag', default='liveness')
    args = ap.parse_args()

    argv = claude_argv_prefix('claude') + [
        '-p', 'Reply with exactly: ok', '--model', args.model,
        '--output-format', 'json']
    if args.max_turns:
        argv += ['--max-turns', str(args.max_turns)]
    env = dict(os.environ, CLAUDE_CONFIG_DIR=CONFIG_DIR)
    print('config dir : %s' % CONFIG_DIR)
    print('cwd        : %s' % bare_cli_cwd())
    print('timeout    : %.0f s' % args.timeout)
    started = time.monotonic()
    try:
        proc = subprocess.run(argv, capture_output=True, encoding='utf-8',
                              timeout=args.timeout, cwd=bare_cli_cwd(), env=env)
    except subprocess.TimeoutExpired as exc:
        wall = time.monotonic() - started
        out = (exc.stdout or b'')
        err = (exc.stderr or b'')
        if isinstance(out, bytes):
            out = out.decode('utf-8', 'replace')
        if isinstance(err, bytes):
            err = err.decode('utf-8', 'replace')
        print('\nVERDICT: HUNG after %.0f s on a FIVE-TOKEN prompt.' % wall)
        print('The lane is down at the ACCOUNT/CLI level, not at the pwg_ru prompt.')
        print('drained stdout tail: %r' % out[-400:])
        print('drained stderr tail: %r' % err[-400:])
        return 1
    wall = time.monotonic() - started
    print('\nreturncode : %d' % proc.returncode)
    print('wall       : %.1f s' % wall)
    try:
        wrapper = json.loads(proc.stdout)
    except Exception as exc:
        print('VERDICT: returned in %.1f s but the envelope is unreadable (%s)' % (wall, exc))
        print('stdout tail: %r' % (proc.stdout or '')[-400:])
        print('stderr tail: %r' % (proc.stderr or '')[-400:])
        return 1
    # Persist BEFORE interpreting. The reason the pre-H2095 gate series is undecomposable
    # is that its envelopes were gitignored; a probe that prints and discards repeats it.
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, '%s.envelope.json' % args.tag)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump({'argv_tail': argv[-8:], 'wall_s': round(wall, 1),
                   'returncode': proc.returncode, 'raw': wrapper}, fh,
                  ensure_ascii=False, indent=2)

    usage = wrapper.get('usage') or {}
    creation = usage.get('cache_creation') or {}
    print('is_error   : %s' % wrapper.get('is_error'))
    print('result     : %r' % str(wrapper.get('result'))[:300])
    print('subtype    : %r' % wrapper.get('subtype'))
    print('usage      : create=%s read=%s in=%s out=%s'
          % (usage.get('cache_creation_input_tokens'), usage.get('cache_read_input_tokens'),
             usage.get('input_tokens'), usage.get('output_tokens')))
    print('ttl split  : 1h=%s 5m=%s' % (creation.get('ephemeral_1h_input_tokens'),
                                        creation.get('ephemeral_5m_input_tokens')))
    print('cost_usd   : %s' % wrapper.get('total_cost_usd'))
    print('envelope   : %s' % path)
    if wrapper.get('is_error'):
        print('\nVERDICT: the call RETURNED (so the lane is not hung) but reports '
              'is_error=True. It still BILLED -- read the subtype above before calling '
              'this a success or a failure.')
        return 1
    print('\nVERDICT: the CLI lane ANSWERS cleanly. A trivial call completes, so the 300 s '
          'timeouts on the pwg_ru prompt are prompt/route-specific, not account-level. '
          'Note what the trivial call still cost: that figure is the per-call floor no '
          'pwg_ru card can go below on this route.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
