"""H2158 Phase 1 -- measure the pwg_ru translation call on BOTH routes, same cards.

The question this answers is narrow and was set by H2158: what does one real pwg_ru
translation call actually cost and how long does it take when issued through the
**Messages API with an explicit cached prefix**, versus the **CLI-headless** route
production uses today? It does not port anything and it does not flip a route.

Why a cached prefix is the whole point
--------------------------------------
v1.127.0 measured that two identical back-to-back `claude -p` calls each RE-CREATE
their cache (49 153 -> 49 165 create, read pinned at 28 882): a one-shot subprocess
cannot amortise its own system prompt, so every call pays a cache WRITE where it
should pay a cache READ. On the 1-hour TTL the CLI actually uses, that is $6.00/Mtok
against $0.30/Mtok -- a 20x spread on the identical bytes. The Messages API puts the
breakpoint under our control, so the arm here marks the stable head of the prompt
with `cache_control` and leaves only the card block volatile.

Byte-identity, not a paraphrase
-------------------------------
Both arms send the SAME prompt bytes, taken from the production surface:

    headless_worker.build_prompt(manifest, [key])

The API arm merely SPLITS that string at the boundary build_prompt itself uses --
everything before the first card block is the cacheable prefix, the card block is the
tail -- and `assert prefix + tail == build_prompt(...)` enforces it. If that assert
ever fires the measurement is void, not merely inaccurate: the two arms would be
pricing different prompts. This is the H2011 trap ("a manifest that validates, runs,
bills, and tests a prompt production never uses") written as an executable check.

Known non-equivalences, stated rather than buried
-------------------------------------------------
* Structured output: the CLI passes `--json-schema`; the API arm forces the same
  schema through `tool_choice={"type":"tool"}` with the schema as the tool's
  input_schema. Same schema object, different enforcement mechanism.
* The CLI envelope's `total_cost_usd` is Anthropic's own figure for a subscription
  call; the API arm has no such field, so BOTH arms are additionally re-priced from
  `parse_workflow_cost.PRICE` so the comparison is like-for-like.
* PRICE['cache_write'] is the 5-minute rate (1.25x base). The CLI's writes land in
  `ephemeral_1h_input_tokens`, which bills at 2x base -- see CACHE_WRITE_1H below.
* This harness bypasses the production reservation ledger and profile claim. It is a
  measurement rig, not an execution path; it must never be wired into a bulk run.

Raw envelopes are written to --out (default pwg_ru/h2158/raw/) and are COMMITTED, not
gitignored: the .gitignore wf_output* rules are why the pre-H2095 gate series is
undecomposable, and this handoff refuses to repeat that.

Offline by default. Paid calls happen only with --run.

    python src/pilot/h2158_route_ab.py --check          # auth + prompt split only
    python src/pilot/h2158_route_ab.py --run --keys 2 --repeats 2

Model: authored by Opus 5 (`claude-opus-5`) for handoff H2158.
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
    bare_cli_cwd, build_prompt, card_block, claude_argv_prefix, parse_cli_wrapper)
from parse_workflow_cost import PRICE                                # noqa: E402

# The profile-bound config dir the paid CLI lane runs under (cache_prefix_stability_probe
# pins the same one). Without it the child inherits whatever profile the session has.
CONFIG_DIR = r'D:\ClaudeTools\profiles\claude4\.claude'

# PRICE['cache_write'] = 3.75 is the FIVE-MINUTE cache-write rate (1.25x the $3.00 base).
# Every write v1.127.0 observed went to `ephemeral_1h_input_tokens`, and the 1-hour TTL
# bills at 2x base = $6.00/Mtok. Pricing 1h writes at the 5m rate understates the CLI
# lane's true cost by 1.6x, which is the wrong direction for a GO/NO-GO. Rates are still
# single-sourced from PRICE -- only the multiplier differs.
CACHE_WRITE_1H = PRICE['input'] * 2.0
CACHE_WRITE_5M = PRICE['cache_write']


def price(tokens, per_mtok):
    return (tokens or 0) * per_mtok / 1e6


def repriced(usage, write_rate):
    """One cost figure for either arm, from the same rate table."""
    return (price(usage.get('input_tokens'), PRICE['input'])
            + price(usage.get('output_tokens'), PRICE['output'])
            + price(usage.get('cache_creation_input_tokens'), write_rate)
            + price(usage.get('cache_read_input_tokens'), PRICE['cache_read']))


def split_prompt(manifest, key):
    """Return (stable_prefix, volatile_tail) whose concatenation IS build_prompt's output.

    build_prompt is `preamble + grammar + translation + [nws] + ''.join(card blocks)`.
    Splitting before the first card block is therefore the only breakpoint that keeps
    byte-identity with the production prompt while isolating the per-card remainder.
    """
    prompt = manifest['prompt']
    nws = prompt.get('nws_rule', '') if manifest['inputs'][key].get('nws') else ''
    prefix = (prompt['preamble'] + prompt.get('grammar', '') + prompt['translation']
              + ('\n\n' + nws + '\n' if nws else ''))
    tail = card_block(manifest, key)
    whole = build_prompt(manifest, [key])
    if prefix + tail != whole:
        raise AssertionError(
            'prompt split is not byte-identical to build_prompt for key %r -- the two '
            'arms would price different prompts; refusing to measure' % key)
    return prefix, tail


def call_cli(manifest, key, timeout):
    """The production route, argv-for-argv as HeadlessEngine.call builds it."""
    prompt = build_prompt(manifest, [key])
    argv = claude_argv_prefix('claude') + [
        '-p', '--output-format', 'json', '--json-schema',
        json.dumps(manifest['output_schema'], ensure_ascii=False, separators=(',', ':')),
        '--model', manifest['model'], '--permission-mode', 'plan']
    env = dict(os.environ, CLAUDE_CONFIG_DIR=CONFIG_DIR)
    started = time.monotonic()
    try:
        proc = subprocess.run(argv, input=prompt, text=True, encoding='utf-8',
                              capture_output=True, timeout=timeout,
                              cwd=bare_cli_cwd(), env=env)
    except subprocess.TimeoutExpired:
        return {'arm': 'cli', 'key': key, 'wall_ms': int(timeout * 1000),
                'failure_class': 'timeout', 'usage': {}}, None
    wall_ms = int((time.monotonic() - started) * 1000)
    try:
        wrapper = parse_cli_wrapper(proc.stdout)
    except ValueError as exc:
        # A paid call that produced no readable envelope is cost-UNEVALUABLE, never $0 --
        # the same fail-closed rule call_reservation applies in production.
        return {'arm': 'cli', 'key': key, 'wall_ms': wall_ms, 'returncode': proc.returncode,
                'failure_class': 'malformed_envelope', 'detail': str(exc)[:400],
                'stderr_tail': (proc.stderr or '')[-400:], 'usage': {}}, None
    usage = wrapper.get('usage') or {}
    creation = usage.get('cache_creation') or {}
    return {
        'arm': 'cli', 'key': key, 'wall_ms': wall_ms, 'returncode': proc.returncode,
        'api_ms': wrapper.get('duration_api_ms'),
        'failure_class': None if not wrapper.get('is_error') else 'cli_error',
        'usage': {k: usage.get(k) for k in (
            'input_tokens', 'output_tokens',
            'cache_creation_input_tokens', 'cache_read_input_tokens')},
        'ttl_1h_tokens': creation.get('ephemeral_1h_input_tokens'),
        'ttl_5m_tokens': creation.get('ephemeral_5m_input_tokens'),
        'envelope_cost_usd': wrapper.get('total_cost_usd'),
    }, wrapper


def call_api(client, manifest, key, prefix, tail, max_tokens):
    """The candidate route: same bytes, explicit 1h cache breakpoint after the prefix."""
    import anthropic
    schema = manifest['output_schema']
    started = time.monotonic()
    try:
        msg = client.messages.create(
            model=manifest['model'],
            max_tokens=max_tokens,
            system=[{'type': 'text', 'text': prefix,
                     'cache_control': {'type': 'ephemeral', 'ttl': '1h'}}],
            messages=[{'role': 'user', 'content': tail}],
            tools=[{'name': 'emit_cards',
                    'description': 'Return the translated cards in the required schema.',
                    'input_schema': schema}],
            tool_choice={'type': 'tool', 'name': 'emit_cards'},
        )
    except anthropic.APIStatusError as exc:
        # The point of the failure-class column: HTTP gives a status code where the CLI
        # gives a hang (FINDINGS 270) or a destroyed rate-limit signal (FINDINGS 273).
        wall_ms = int((time.monotonic() - started) * 1000)
        return {'arm': 'api', 'key': key, 'wall_ms': wall_ms,
                'failure_class': 'http_%d' % exc.status_code,
                'error_type': getattr(exc, 'type', None),
                'retry_after': exc.response.headers.get('retry-after'),
                'detail': str(exc)[:400], 'usage': {}}, None
    except anthropic.APIConnectionError as exc:
        wall_ms = int((time.monotonic() - started) * 1000)
        return {'arm': 'api', 'key': key, 'wall_ms': wall_ms,
                'failure_class': 'connection', 'detail': str(exc)[:400], 'usage': {}}, None
    wall_ms = int((time.monotonic() - started) * 1000)
    usage = msg.usage.model_dump()
    cards_ok = any(b.type == 'tool_use' and isinstance(b.input, dict)
                   and isinstance(b.input.get('cards'), list) for b in msg.content)
    return {
        'arm': 'api', 'key': key, 'wall_ms': wall_ms, 'api_ms': None,
        'failure_class': None if cards_ok else 'no_cards',
        'stop_reason': msg.stop_reason,
        'usage': {k: usage.get(k) for k in (
            'input_tokens', 'output_tokens',
            'cache_creation_input_tokens', 'cache_read_input_tokens')},
        # The API arm's breakpoint is declared ttl=1h, so its writes are 1h writes too.
        'ttl_1h_tokens': usage.get('cache_creation_input_tokens'),
        'ttl_5m_tokens': None,
        'envelope_cost_usd': None,
    }, msg.model_dump()


def api_client():
    """Return (client, note). Presence-only auth report -- never echo the credential."""
    import anthropic
    for var in ('ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN'):
        if os.environ.get(var):
            return anthropic.Anthropic(), '%s present in environment' % var
    return None, ('no ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN in environment and the '
                  '`ant` CLI is absent, so no OAuth profile can be resolved either')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument('--manifest', default=os.path.join(here, 'h1209_slice3.manifest.json'))
    ap.add_argument('--out', default=os.path.join(
        os.path.dirname(os.path.dirname(here)), 'pwg_ru', 'h2158', 'raw'))
    ap.add_argument('--keys', type=int, default=2, help='how many real cards (small N)')
    ap.add_argument('--repeats', type=int, default=2,
                    help='calls per card per arm; >=2 is what exposes cache reuse')
    ap.add_argument('--max-tokens', type=int, default=16000)
    ap.add_argument('--timeout', type=float, default=300.0)
    ap.add_argument('--check', action='store_true',
                    help='offline: verify auth + the byte-identical prompt split, spend nothing')
    ap.add_argument('--run', action='store_true', help='issue the paid calls')
    ap.add_argument('--arms', default='api,cli',
                    help='which arms to run. Running ONE arm is a half-measurement and can '
                         'never yield a GO/NO-GO on its own -- it is for landing the lane '
                         'that is unblocked while the other waits on a prerequisite.')
    args = ap.parse_args()

    with open(args.manifest, encoding='utf-8') as fh:
        manifest = json.load(fh)
    keys = list((manifest.get('meta') or {}).get('selected_keys') or [])[:args.keys]
    client, auth_note = api_client()

    print('manifest      : %s' % args.manifest)
    print('model         : %s' % manifest['model'])
    print('cards         : %s' % ', '.join(keys))
    print('auth          : %s' % auth_note)
    print('bare cli cwd  : %s' % bare_cli_cwd())
    for key in keys:
        prefix, tail = split_prompt(manifest, key)          # raises if not byte-identical
        print('split %-10s: prefix %6d chars (cacheable) + tail %6d chars (volatile) '
              '= %6d, byte-identical to build_prompt OK'
              % (key, len(prefix), len(tail), len(prefix) + len(tail)))
    arms = [a.strip() for a in args.arms.split(',') if a.strip()]
    unknown = [a for a in arms if a not in ('api', 'cli')]
    if unknown:
        print('unknown arm(s): %s' % ', '.join(unknown), file=sys.stderr)
        return 2
    print('arms          : %s' % ', '.join(arms))
    if not args.run:
        print('\n--check only; no calls issued. Re-run with --run to spend.')
        return 0
    if 'api' in arms and client is None:
        print('\nREFUSING to run the api arm: no credential, so the A/B would be one-armed '
              'and the GO/NO-GO unanswerable. Re-run with --arms cli to land the CLI '
              'baseline alone, and record the result as INCONCLUSIVE.', file=sys.stderr)
        return 2
    if len(arms) < 2:
        print('\nNOTE: single-arm run (%s). This is a BASELINE, not an A/B -- it cannot '
              'support a GO/NO-GO by itself.' % arms[0])

    os.makedirs(args.out, exist_ok=True)
    rows = []
    for key in keys:
        prefix, tail = split_prompt(manifest, key)
        for arm in arms:
            for n in range(1, args.repeats + 1):
                if arm == 'api':
                    row, raw = call_api(client, manifest, key, prefix, tail, args.max_tokens)
                else:
                    row, raw = call_cli(manifest, key, args.timeout)
                row['n'] = n
                row['cost_usd_1h_write'] = round(repriced(row['usage'], CACHE_WRITE_1H), 6)
                row['cost_usd_5m_write'] = round(repriced(row['usage'], CACHE_WRITE_5M), 6)
                rows.append(row)
                stem = '%s_%s_%d' % (arm, key, n)
                with open(os.path.join(args.out, stem + '.envelope.json'), 'w',
                          encoding='utf-8') as fh:
                    json.dump({'row': row, 'raw': raw}, fh, ensure_ascii=False, indent=2)
                print('%-3s %-10s #%d  %7d ms  create=%-7s read=%-7s out=%-6s $%.4f  %s'
                      % (arm, key, n, row['wall_ms'],
                         row['usage'].get('cache_creation_input_tokens'),
                         row['usage'].get('cache_read_input_tokens'),
                         row['usage'].get('output_tokens'),
                         row['cost_usd_1h_write'], row['failure_class'] or 'ok'))

    with open(os.path.join(args.out, 'rows.json'), 'w', encoding='utf-8') as fh:
        json.dump({'manifest': os.path.basename(args.manifest), 'model': manifest['model'],
                   'keys': keys, 'repeats': args.repeats,
                   'rates': {'input': PRICE['input'], 'output': PRICE['output'],
                             'cache_write_1h': CACHE_WRITE_1H,
                             'cache_write_5m': CACHE_WRITE_5M,
                             'cache_read': PRICE['cache_read']},
                   'rows': rows}, fh, ensure_ascii=False, indent=2)
    print('\nraw envelopes + rows.json written to %s (committed, not gitignored)' % args.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
