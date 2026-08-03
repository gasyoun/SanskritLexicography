#!/usr/bin/env python
"""H2189 Phase 3 -- sequential A/B of the headless PROFILE surface, both arms bare cwd.

The question
------------
H2158 shipped `bare_cli_cwd()`, which strips the **project** context from every paid
spawn. What it cannot strip is the **profile** bound as `CLAUDE_CONFIG_DIR`: its
CLAUDE.md, its ~200 commands and ~57 skills, and its `SessionStart`/`UserPromptSubmit`
hooks all reach the model before the card does. H2158 measured the cost side of that and
hit the correctness side of it too -- a model that refused its own task instruction,
citing an operator rule it could only have received through the profile.

So: how much create/read/wall does the profile surface actually cost per call, and does
removing it stop the profile from overriding the task text?

Arms (all bare cwd, all sequential, one variable each)
------------------------------------------------------
    paid          the profile production runs under today -- the BASELINE
    minimal       a sibling profile with no CLAUDE.md, no skills/commands/agents,
                  no hooks, same credentials  (built by h2189_min_profile.py)
    safe          the paid profile + `--safe-mode`, which the CLI documents as
                  disabling CLAUDE.md, skills, plugins, hooks, MCP, custom commands
                  and agents -- while auth, model selection, built-in tools and
                  permissions keep working
    safe_excl     `safe` + `--exclude-dynamic-system-prompt-sections`, which moves the
                  per-machine sections (cwd, env, memory paths, git status) out of the
                  system prompt and into the first user message

`safe` matters because it reaches the same surface as `minimal` WITHOUT a second on-disk
credential copy and WITHOUT a second `ActiveCallClaim` fingerprint. If it measures level
with `minimal`, the cheaper and safer wiring is a flag, not a directory.

`--bare` is deliberately NOT an arm. It strips the same context, but its own help states
that Anthropic auth becomes strictly `ANTHROPIC_API_KEY`/apiKeyHelper and that OAuth is
never read -- i.e. it silently moves this lane from the subscription identity to metered
billing. That is the subscription-vs-metered question PROMPT_CACHING_PWG_RU 4 reserves
for a human, not a side effect to smuggle in behind a cache optimisation.

Two phases, because they answer different halves
-------------------------------------------------
    trivial  `--max-turns 1` on a five-token prompt. Translates nothing, so every token
             it bills IS the scaffolding -- the cleanest possible read of the profile
             surface, and comparable with the v1.127.0 / cache_prefix_stability_probe
             numbers that used the same shape.
    card     the real production prompt, `headless_worker.build_prompt(manifest, [key])`,
             with the manifest's own `--json-schema` and `--permission-mode plan`, argv
             for argv as `HeadlessEngine.call` builds it. This is the arm that can show
             an instruction override, because a trivial prompt gives a profile rule
             nothing to override.

Sequential with a cooldown, never parallel: two same-prompt calls in flight at once
contaminate each other's cache accounting, which is the exact confound H2158 called out.

This is a measurement rig. It bypasses the production call-reservation ledger and the
profile claim, and must never be wired into a bulk run.

Raw envelopes are COMMITTED under --out (default pwg_ru/h2189/raw/), not gitignored:
the pre-H2095 gate series is undecomposable precisely because its envelopes were dropped.

    python src/pilot/h2189_profile_ab.py --check
    python src/pilot/h2189_profile_ab.py --run --phase trivial --repeats 2
    python src/pilot/h2189_profile_ab.py --run --phase card --keys 1 --arms paid,safe

Model: authored by Opus 5 (`claude-opus-5[1m]`) for handoff H2189.
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from headless_worker import (                                        # noqa: E402
    bare_cli_cwd, build_prompt, claude_argv_prefix, parse_cli_wrapper)
from h2189_min_profile import (                                      # noqa: E402
    MIN_CONFIG_DIR, PAID_CONFIG_DIR, clean_cwd, cwd_ancestry_scan)
from parse_workflow_cost import PRICE, cache_write_rate              # noqa: E402

CACHE_WRITE_1H = cache_write_rate('1h')

TRIVIAL_PROMPT = 'Reply with exactly: ok'

# A spawn directory whose ANCESTRY carries no memory files. Measured offline before this
# harness was ever run: `bare_cli_cwd()` lands in %TEMP%, i.e. under the Windows user
# profile, and an ancestor walk from there still finds C:\Users\user\.claude\CLAUDE.md
# (31 625 B) plus .claude\rules (1 154 B) -- ~33 KB of operator memory that the H2158
# bare-cwd fix does NOT remove, because its ancestor check looks for a bare `CLAUDE.md`
# and a `.git`, not for `.claude\CLAUDE.md`. A different DRIVE is the cheapest ancestry
# with none of that on it.
CLEAN_CWD_PATH = r'D:\ClaudeTools\pwg_ru_clean_cwd'

# One variable per arm, relative to `paid`. Keep it that way: an arm that changes two
# things at once cannot attribute its own delta. `safe_clean` is the deliberate exception
# -- it is the STACK of `safe` and `clean_cwd`, and is only interpretable next to both.
ARMS = {
    'paid':       {'config_dir': PAID_CONFIG_DIR, 'extra': [],
                   'cwd': 'bare', 'home': None},
    'minimal':    {'config_dir': MIN_CONFIG_DIR,  'extra': [],
                   'cwd': 'bare', 'home': os.path.dirname(MIN_CONFIG_DIR)},
    'safe':       {'config_dir': PAID_CONFIG_DIR, 'extra': ['--safe-mode'],
                   'cwd': 'bare', 'home': None},
    'clean_cwd':  {'config_dir': PAID_CONFIG_DIR, 'extra': [],
                   'cwd': 'clean', 'home': None},
    'safe_clean': {'config_dir': PAID_CONFIG_DIR, 'extra': ['--safe-mode'],
                   'cwd': 'clean', 'home': None},
}
ARM_ORDER = ('paid', 'minimal', 'safe', 'clean_cwd', 'safe_clean')

# `--exclude-dynamic-system-prompt-sections` (move cwd/env/memory-path/git sections out of
# the system prompt into the first user message) is a real adjunct lever but is NOT an arm
# here: its own help scopes it to cross-USER cache reuse, and adding a sixth arm to a
# small-N sequential run buys less than it costs. Recorded as untested residual, not as
# measured-and-rejected.


def arm_cwd(name):
    """The spawn directory for an arm. Fails LOUD: an arm whose clean cwd could not be
    proven ancestry-free must not silently fall back to the leaking one and be reported
    as if it had measured the clean case."""
    if ARMS[name]['cwd'] == 'bare':
        return bare_cli_cwd()
    path = clean_cwd(CLEAN_CWD_PATH)
    if path is None:
        raise SystemExit(
            'arm %s needs an ancestry-clean cwd; %s still inherits: %s'
            % (name, CLEAN_CWD_PATH,
               ', '.join(h['path'] for h in cwd_ancestry_scan(CLEAN_CWD_PATH))))
    return path


def arm_env(name):
    """The child environment for an arm.

    The `minimal` arm overrides HOME/USERPROFILE as well as CLAUDE_CONFIG_DIR, because on
    this box the profile is bound by USERPROFILE (`~/.claude`), not by CLAUDE_CONFIG_DIR
    alone -- this very session runs under claude4 with CLAUDE_CONFIG_DIR unset. Setting
    only the documented variable would leave the child resolving skills/commands/agents
    out of the profile the arm is supposed to have left behind.
    """
    arm = ARMS[name]
    env = dict(os.environ, CLAUDE_CONFIG_DIR=arm['config_dir'])
    if arm['home']:
        env['USERPROFILE'] = arm['home']
        env['HOME'] = arm['home']
    return env


def price(tokens, per_mtok):
    return (tokens or 0) * per_mtok / 1e6


def repriced(usage):
    """One cost figure per call from the shared rate table, cache writes at the 1h rate.

    The envelope's own `total_cost_usd` is Anthropic's figure for a subscription call and
    is reported alongside, but the comparison between arms uses this: `PRICE['cache_write']`
    is the 5-minute rate and every write these calls make lands in the 1h bucket (H2190).
    """
    return (price(usage.get('input_tokens'), PRICE['input'])
            + price(usage.get('output_tokens'), PRICE['output'])
            + price(usage.get('cache_creation_input_tokens'), CACHE_WRITE_1H)
            + price(usage.get('cache_read_input_tokens'), PRICE['cache_read']))


def build_argv(arm_name, phase, manifest, key):
    """Return the argv for one call. The `card` phase mirrors HeadlessEngine.call exactly."""
    arm = ARMS[arm_name]
    if phase == 'trivial':
        argv = claude_argv_prefix('claude') + [
            '-p', TRIVIAL_PROMPT, '--model', manifest['model'],
            '--output-format', 'json', '--max-turns', '1']
    else:
        argv = claude_argv_prefix('claude') + [
            '-p', '--output-format', 'json', '--json-schema',
            json.dumps(manifest['output_schema'], ensure_ascii=False, separators=(',', ':')),
            '--model', manifest['model'], '--permission-mode', 'plan']
    return argv + arm['extra']


def one_call(arm_name, phase, manifest, key, timeout):
    """Issue one paid call and return a row. Never raises on a failed call -- a paid
    failure is a measurement, and pricing it at $0 is the fail-open this lane forbids."""
    argv = build_argv(arm_name, phase, manifest, key)
    stdin = None if phase == 'trivial' else build_prompt(manifest, [key])
    env = arm_env(arm_name)
    cwd = arm_cwd(arm_name)
    started = time.monotonic()
    try:
        proc = subprocess.run(argv, input=stdin, text=True, encoding='utf-8',
                              capture_output=True, timeout=timeout,
                              cwd=cwd, env=env)
    except subprocess.TimeoutExpired:
        return {'arm': arm_name, 'phase': phase, 'key': key,
                'wall_ms': int(timeout * 1000), 'failure_class': 'timeout',
                'usage': {}}, None
    wall_ms = int((time.monotonic() - started) * 1000)
    try:
        wrapper = parse_cli_wrapper(proc.stdout)
    except ValueError as exc:
        return {'arm': arm_name, 'phase': phase, 'key': key, 'wall_ms': wall_ms,
                'returncode': proc.returncode, 'failure_class': 'malformed_envelope',
                'detail': str(exc)[:400], 'stderr_tail': (proc.stderr or '')[-400:],
                'usage': {}}, None
    usage = wrapper.get('usage') or {}
    creation = usage.get('cache_creation') or {}
    row = {
        'arm': arm_name, 'phase': phase, 'key': key, 'wall_ms': wall_ms,
        'returncode': proc.returncode, 'api_ms': wrapper.get('duration_api_ms'),
        'num_turns': wrapper.get('num_turns'),
        'failure_class': None if not wrapper.get('is_error') else 'cli_error',
        'usage': {k: usage.get(k) for k in (
            'input_tokens', 'output_tokens',
            'cache_creation_input_tokens', 'cache_read_input_tokens')},
        'ttl_1h_tokens': creation.get('ephemeral_1h_input_tokens'),
        'ttl_5m_tokens': creation.get('ephemeral_5m_input_tokens'),
        'envelope_cost_usd': wrapper.get('total_cost_usd'),
    }
    if phase == 'card':
        row.update(instruction_compliance(wrapper))
    return row, wrapper


def instruction_compliance(wrapper):
    """Did the call DO the task, or answer about something else?

    The H2158 failure was not a crash: the call succeeded, billed, and returned prose
    declining the work on the authority of a profile rule. So compliance here is
    structural -- did a schema-shaped `cards` payload come back -- plus a keyword probe
    for the operator vocabulary that can only have arrived through the profile.
    """
    result = wrapper.get('result')
    text = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
    payload = None
    if isinstance(result, str):
        try:
            payload = json.loads(result)
        except ValueError:
            payload = None
    elif isinstance(result, dict):
        payload = result
    cards = payload.get('cards') if isinstance(payload, dict) else None
    # Vocabulary that exists only in the operator's GTD/handoff ruleset, never in a
    # pwg_ru translation prompt. A hit means profile text reached the model's answer.
    markers = ('handoff', 'H###', 'GTD', 'NEXT ISSUE', 'Next Steps', 'starter line',
               'мint', 'ambient context')
    leaked = sorted({m for m in markers if m.lower() in (text or '').lower()})
    return {
        'cards_returned': len(cards) if isinstance(cards, list) else 0,
        'schema_compliant': isinstance(cards, list) and len(cards) > 0,
        'profile_vocab_leaked': leaked,
        'result_head': (text or '')[:300],
    }


def summarise(rows):
    """Per-arm medians. Reported per phase because the two phases are not comparable."""
    out = {}
    for arm in ARM_ORDER:
        for phase in ('trivial', 'card'):
            sel = [r for r in rows if r['arm'] == arm and r['phase'] == phase
                   and not r.get('failure_class')]
            if not sel:
                continue
            def med(fn):
                vals = sorted(v for v in (fn(r) for r in sel) if v is not None)
                return vals[len(vals) // 2] if vals else None
            out['%s/%s' % (arm, phase)] = {
                'n': len(sel),
                'create': med(lambda r: r['usage'].get('cache_creation_input_tokens')),
                'read': med(lambda r: r['usage'].get('cache_read_input_tokens')),
                'input': med(lambda r: r['usage'].get('input_tokens')),
                'output': med(lambda r: r['usage'].get('output_tokens')),
                'ttl_1h': med(lambda r: r['ttl_1h_tokens']),
                'wall_ms': med(lambda r: r['wall_ms']),
                'api_ms': med(lambda r: r['api_ms']),
                'cost_usd_1h_write': round(
                    sum(r['cost_usd_1h_write'] for r in sel) / len(sel), 6),
                'envelope_cost_usd': round(
                    sum(r['envelope_cost_usd'] or 0.0 for r in sel) / len(sel), 6),
            }
    return out


def print_table(rows):
    print('\n%-10s %-7s %-10s %3s %8s %8s %8s %8s %9s %9s %9s'
          % ('arm', 'phase', 'key', '#', 'create', 'read', 'in', 'out',
             'wall_ms', 'api_ms', 'usd_1h'))
    for r in rows:
        if r.get('failure_class'):
            print('%-10s %-7s %-10s %3s  FAILED: %s'
                  % (r['arm'], r['phase'], (r['key'] or '-')[:10], r.get('n', '-'),
                     r['failure_class']))
            continue
        u = r['usage']
        print('%-10s %-7s %-10s %3s %8s %8s %8s %8s %9d %9s %9.4f'
              % (r['arm'], r['phase'], (r['key'] or '-')[:10], r.get('n', '-'),
                 u.get('cache_creation_input_tokens'), u.get('cache_read_input_tokens'),
                 u.get('input_tokens'), u.get('output_tokens'),
                 r['wall_ms'], r.get('api_ms'), r['cost_usd_1h_write']))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument('--manifest', default=os.path.join(here, 'h1209_slice3.manifest.json'))
    ap.add_argument('--out', default=os.path.join(
        os.path.dirname(os.path.dirname(here)), 'pwg_ru', 'h2189', 'raw'))
    ap.add_argument('--arms', default=','.join(ARM_ORDER))
    ap.add_argument('--phase', default='trivial', choices=('trivial', 'card'))
    ap.add_argument('--keys', type=int, default=1, help='real cards (card phase only)')
    ap.add_argument('--repeats', type=int, default=2,
                    help='calls per arm; >=2 is what exposes cross-call cache reuse')
    ap.add_argument('--cooldown', type=float, default=3.0,
                    help='seconds between calls; arms are sequential, never parallel')
    ap.add_argument('--timeout', type=float, default=300.0)
    ap.add_argument('--check', action='store_true',
                    help='offline: verify profiles, argv and prompt; spend nothing')
    ap.add_argument('--run', action='store_true', help='issue the paid calls')
    args = ap.parse_args()

    with open(args.manifest, encoding='utf-8') as fh:
        manifest = json.load(fh)
    keys = list((manifest.get('meta') or {}).get('selected_keys') or [])
    keys = keys[:args.keys] if args.phase == 'card' else [None]
    arms = [a.strip() for a in args.arms.split(',') if a.strip()]
    unknown = [a for a in arms if a not in ARMS]
    if unknown:
        print('unknown arm(s): %s (known: %s)' % (', '.join(unknown), ', '.join(ARM_ORDER)),
              file=sys.stderr)
        return 2

    print('manifest      : %s' % args.manifest)
    print('model         : %s' % manifest['model'])
    print('phase         : %s' % args.phase)
    print('cards         : %s' % (', '.join(k for k in keys if k) or '(trivial prompt)'))
    bare = bare_cli_cwd()
    leak = cwd_ancestry_scan(bare) if bare else []
    print('bare cli cwd  : %s' % bare)
    print('  ancestry    : %d bytes injectable from %d ancestor file(s)%s'
          % (sum(h['bytes'] for h in leak), len(leak),
             '' if not leak else '  <- the residual tax bare_cli_cwd does not remove'))
    for hit in leak:
        print('    %-5s %7d B  %s' % (hit['kind'], hit['bytes'], hit['path']))
    for name in arms:
        arm = ARMS[name]
        ok = os.path.isdir(arm['config_dir'])
        creds = os.path.exists(os.path.join(arm['config_dir'], '.credentials.json'))
        cwd = arm_cwd(name)
        print('arm %-11s: %s%s\n              cwd=%s (%s)  extra=%s  creds=%s'
              % (name, arm['config_dir'], '' if ok else '  (MISSING)',
                 cwd, arm['cwd'], ' '.join(arm['extra']) or '(none)',
                 'yes' if creds else 'NO'))
        if not ok:
            print('              build it first: python src/pilot/h2189_min_profile.py --build',
                  file=sys.stderr)
            return 2
        if not creds:
            print('              a profile without .credentials.json cannot authenticate; '
                  'the arm would fail, not measure.', file=sys.stderr)
            return 2
    if args.phase == 'card':
        for key in keys:
            prompt = build_prompt(manifest, [key])
            print('prompt %-10s: %d chars from build_prompt (production surface)'
                  % (key, len(prompt)))
    print('argv (arm %s): %s' % (arms[0],
                                 ' '.join(build_argv(arms[0], args.phase, manifest,
                                                     keys[0])[-6:])))

    if len(arms) < 2:
        print('\nNOTE: single-arm run (%s). That is a BASELINE, not an A/B, and cannot '
              'support a GO/NO-GO on its own.' % arms[0])
    if not args.run:
        print('\n--check only; no calls issued. Re-run with --run to spend.')
        return 0

    os.makedirs(args.out, exist_ok=True)
    rows = []
    for key in keys:
        for name in arms:
            for n in range(1, args.repeats + 1):
                row, raw = one_call(name, args.phase, manifest, key, args.timeout)
                row['n'] = n
                row['cost_usd_1h_write'] = round(repriced(row['usage']), 6)
                rows.append(row)
                print('%-10s %-7s %-10s #%d  %s'
                      % (name, args.phase, key or '-', n,
                         row.get('failure_class') or 'ok'))
                if raw is not None:
                    stem = 'h2189_%s_%s_%s_%d.json' % (args.phase, name, key or 'trivial', n)
                    with open(os.path.join(args.out, stem), 'w', encoding='utf-8') as fh:
                        json.dump(raw, fh, ensure_ascii=False, indent=2)
                time.sleep(args.cooldown)

    print_table(rows)
    summary = summarise(rows)
    print('\n== per-arm medians (%s phase) ==' % args.phase)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.phase == 'card':
        print('\n== instruction compliance ==')
        for r in rows:
            if r.get('failure_class'):
                continue
            print('%-10s %-10s cards=%d schema_ok=%s leaked=%s'
                  % (r['arm'], r['key'], r.get('cards_returned', 0),
                     r.get('schema_compliant'), r.get('profile_vocab_leaked') or 'none'))

    rollup = os.path.join(args.out, 'h2189_%s_rows.json' % args.phase)
    with open(rollup, 'w', encoding='utf-8') as fh:
        json.dump({'rows': rows, 'summary': summary,
                   'manifest': os.path.basename(args.manifest),
                   'model': manifest['model'],
                   'cache_write_1h_rate': CACHE_WRITE_1H}, fh, ensure_ascii=False, indent=2)
    print('\nrows + summary: %s' % rollup)
    return 0


if __name__ == '__main__':
    sys.exit(main())
