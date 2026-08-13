#!/usr/bin/env python3
"""How long does the fragment lane's LARGEST group actually need?

H2612's first sealed run stopped at ordinal 1: `vyavasTA#g1` (11 fragments, 27 379 prompt
bytes) did not return inside the rig's 1800 s default, so the run halted with one call
spent and no verdict. Raising the timeout blind would spend sixteen more calls on a guess.

This probe re-issues THAT prompt — replayed from the sealed plan and hash-verified before
dispatch, so it is the same bytes the run sent — with a longer ceiling, and reports the wall
time and usage. One call, deliberately OUTSIDE the sealed reservation ledger: a diagnostic
must never consume a reservation belonging to a run, the same rule B1's reproduction probe
followed.

    python timeout_probe.py [--timeout 5400] [--unit vyavasTA#g1] [--arm A] [--out probe.json]

Costs one paid call when run. Prints the plan/prompt hashes it verified first.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.dirname(os.path.dirname(HERE))
for path in (os.path.dirname(HERE), PILOT, os.path.dirname(PILOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

import prep_context_compare as pcc                            # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan-file', default=os.path.join(HERE, 'plan.json'))
    parser.add_argument('--unit', default='vyavasTA#g1')
    parser.add_argument('--arm', default='A', choices=('A', 'B'))
    parser.add_argument('--timeout', type=float, default=5400.0)
    parser.add_argument('--out', default=None)
    args = parser.parse_args()

    with open(args.plan_file, encoding='utf-8') as handle:
        plan = json.load(handle)
    plan['__plan_file__'] = os.path.abspath(args.plan_file)
    pcc.verify_plan_hash(plan)

    resolved = pcc.resolve_manifest(plan)
    with open(resolved, encoding='utf-8') as handle:
        manifest = json.load(handle)

    card = plan['cards'][args.unit]
    context_path = os.path.normpath(os.path.join(os.path.dirname(resolved),
                                                 card['context_path']))
    with open(context_path, encoding='utf-8') as handle:
        context = pcc.prep_pack.verify_compact_context(json.load(handle))

    prompt_a, prompt_b = pcc.arm_prompts(manifest, args.unit, context, card)
    prompt = prompt_a if args.arm == 'A' else prompt_b
    sealed = plan['prompts'][args.unit][args.arm]['sha256']
    if pcc.sha256_text(prompt) != sealed:
        raise SystemExit('prompt does not replay the sealed hash — refusing to dispatch')

    print('unit %s arm %s · %d fragments · %d prompt bytes'
          % (args.unit, args.arm, card['group_fragments'], len(prompt.encode('utf-8'))))
    print('plan  %s' % plan['plan_sha256'])
    print('prompt %s (verified against the sealed plan)' % sealed)
    print('dispatching with a %.0f s ceiling — ONE call, outside the sealed ledger' % args.timeout)

    argv = pcc.build_argv(plan, manifest)
    started = time.monotonic()
    result = pcc.cli_caller(argv, prompt, args.timeout)
    elapsed = time.monotonic() - started

    wrapper, parse_error = None, None
    try:
        wrapper = pcc.parse_cli_wrapper(result.get('stdout') or '')
    except ValueError as exc:
        parse_error = str(exc)[:400]

    telemetry = (pcc.telemetry_from_cli_wrapper(wrapper, max_agent_sdk_credit=True)
                 if wrapper is not None else pcc.unevaluable_telemetry())
    tokens = {name: int(telemetry.get(name) or 0) for name in
              ('input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_creation_tokens')}

    report = {
        'schema': 'pwg.h2612_timeout_probe.v1',
        'unit': args.unit, 'arm': args.arm,
        'fragments': card['group_fragments'],
        'prompt_sha256': sealed, 'prompt_bytes': len(prompt.encode('utf-8')),
        'timeout_s': args.timeout,
        'wall_s': round(elapsed, 1),
        'timed_out': bool(result.get('timed_out')),
        'returncode': result.get('returncode'),
        'parse_error': parse_error,
        'returned_model': ((wrapper or {}).get('model')
                           or next(iter((wrapper or {}).get('modelUsage') or {}), None)),
        'terminal': {name: (wrapper or {}).get(name) for name in pcc.TERMINAL_FIELDS},
        'tokens': tokens, 'tokens_total': sum(tokens.values()),
        'raw_head': str((wrapper or {}).get('result') or (result.get('stdout') or ''))[:600],
    }

    print('\nwall %.0f s · timed_out=%s · rc=%s · model=%s · tokens=%d'
          % (report['wall_s'], report['timed_out'], report['returncode'],
             report['returned_model'], report['tokens_total']))
    if report['terminal'].get('subtype'):
        print('subtype=%s terminal_reason=%s num_turns=%s'
              % (report['terminal']['subtype'], report['terminal'].get('terminal_reason'),
                 report['terminal'].get('num_turns')))

    if args.out:
        with open(args.out, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(report, handle, ensure_ascii=False, indent=1, sort_keys=True)
            handle.write('\n')
        print('wrote %s' % args.out)
    return 0 if not report['timed_out'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
