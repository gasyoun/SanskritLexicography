#!/usr/bin/env python
"""Build scratch harness arms for pwg_ru performance calibration.

This helper only generates harness files plus a manifest/report template. It does
not run Workflow, audit outputs, promote cards, or touch the RU store.
"""
import argparse
import datetime
import itertools
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding="utf-8")

import width_policy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, 'output')

CACHE_WARNING = (
    'Run live calibration arms sequentially with cache cooldown; never run same-prompt '
    'arms in parallel. AB_TEST_LEAN_TR.md showed the 5-minute prompt cache makes the '
    'second parallel/same-prompt run artificially cheap.'
)


def split_csv(text):
    return [x.strip() for x in str(text).split(',') if x.strip()]


def parse_ints(text):
    return [int(x) for x in split_csv(text)]


def apply_arm_set(args):
    if args.arm_set == 'conservative':
        args.output_budgets = args.output_budgets or [90, 110]
        args.selfheal_budgets = args.selfheal_budgets or [12]
        args.tm_modes = args.tm_modes or ['auto', 'off']
    elif args.arm_set == 'wide':
        args.output_budgets = args.output_budgets or [90, 110, 120]
        args.selfheal_budgets = args.selfheal_budgets or [8, 12, 16]
        args.tm_modes = args.tm_modes or ['auto', 'off']
    else:
        args.output_budgets = args.output_budgets or [60, 90]
        args.selfheal_budgets = args.selfheal_budgets or [12]
        args.tm_modes = args.tm_modes or ['auto', 'off']
    return args


def arm_name(output_budget, selfheal_budget, tm_mode, max_wide=None):
    name = 'ob%s_sh%s_tm%s' % (output_budget, selfheal_budget, tm_mode)
    return name if max_wide is None else '%s_w%d' % (name, max_wide)


def width_bracket(args):
    """H1403 A7 / H4529: the width arm, unlocked only by measured-healthy telemetry.

    Width above the A5-pinned 3 is a *measurement*, never a policy move: the
    Slice-D / H317 / H255 cascades were all unconditional width raises. So the
    bracket is empty unless the caller hands over per-window telemetry whose tail
    `width_policy.healthy_for_calibration` accepts, and it is clamped to
    `width_policy.CALIBRATION_CEILING` (8). Arms still run sequentially with the
    cache cooldown the rest of this module already demands.

    Returns ``[None]`` (one arm, width untouched) when the width axis is off.
    """
    if not getattr(args, 'width_arm', False):
        return [None]
    rows = []
    if args.healthy_telemetry:
        with open(args.healthy_telemetry, encoding='utf-8') as fh:
            raw = json.load(fh)
        rows = raw.get('windows', []) if isinstance(raw, dict) else list(raw or [])
    healthy = width_policy.healthy_for_calibration(rows)
    requested = args.widths or width_policy.calibration_bracket(healthy=True)
    if not healthy:
        raise SystemExit(
            'calibrate --width-arm refused: the width bracket %s needs measured-healthy '
            'telemetry (--healthy-telemetry <windows.json>: %d consecutive load-representative '
            'windows with zero kill-timeouts/conn-errors). A degraded day cannot buy a width '
            'raise — that is the H255/H317 cascade.'
            % (requested, width_policy.HEALTHY_WINDOWS_TO_WIDEN))
    bracket = [w for w in requested if 1 <= w <= width_policy.CALIBRATION_CEILING]
    if not bracket:
        raise SystemExit('calibrate --width-arm: no width in 1..%d requested'
                         % width_policy.CALIBRATION_CEILING)
    return bracket


def build_command(args, out_js, output_budget, selfheal_budget, tm_mode, max_wide=None):
    cmd = [
        sys.executable,
        os.path.join(HERE, 'gen_opt_harness2.py'),
        args.root,
        '--keys=%s' % ','.join(args.keys),
        '--out=%s' % out_js,
        '--output-budget=%s' % output_budget,
        '--selfheal-budget=%s' % selfheal_budget,
        '--lang=%s' % args.lang,
    ]
    if args.nominal:
        cmd.append('--nominal')
    if args.no_grammar:
        cmd.append('--no-grammar')
    if tm_mode == 'off':
        cmd.append('--no-tm')
    elif tm_mode == 'on':
        cmd.append('--tm=%s' % args.tm_path if args.tm_path else '--tm')
    elif tm_mode == 'auto':
        cmd.append('--tm=auto')
    else:
        raise ValueError('unknown tm mode %r' % tm_mode)
    if max_wide is not None:
        cmd.append('--max-wide=%d' % max_wide)   # H1403 A7 width arm (width_policy bracket)
    return cmd


def write_readme(path, manifest):
    lines = [
        '# pwg_ru Performance Calibration Scratch',
        '',
        CACHE_WARNING,
        '',
        'These files are generated harness arms only. Run each arm manually in Workflow,',
        'one at a time, record transcript/cost/audit outputs below, then compare.',
        '',
        '## Fixed Inputs',
        '',
        '- root: `%s`' % manifest['root'],
        '- lang: `%s`' % manifest['lang'],
        '- keys: `%s`' % ','.join(manifest['keys']),
        '- generated_at: `%s`' % manifest['generated_at'],
        '',
        '## Arms',
        '',
    ]
    for arm in manifest['arms']:
        lines.extend([
            '### %s' % arm['name'],
            '',
            '- output_budget: `%s`' % arm['output_budget'],
            '- selfheal_budget: `%s`' % arm['selfheal_budget'],
            '- tm_mode: `%s`' % arm['tm_mode'],
            '- harness: `%s`' % arm['harness'],
            '- generator_status: `%s`' % arm['status'],
            '- command: `%s`' % ' '.join(arm['command']),
            '- workflow_output: TODO',
            '- audit_report: TODO',
            '- cost_summary: TODO',
            '- null_keys: TODO',
            '',
        ])
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines).rstrip() + '\n')


def main(argv=None):
    ap = argparse.ArgumentParser(description='Generate scratch harness arms for calibration.')
    ap.add_argument('root')
    ap.add_argument('--keys', required=True, type=split_csv,
                    help='Comma-separated fixed key set; required so arms are comparable.')
    ap.add_argument('--arm-set', default='custom', choices=('custom', 'conservative', 'wide'),
                    help='Named calibration grid; explicit budget/TM flags override each axis.')
    ap.add_argument('--output-budgets', default=None, type=parse_ints)
    ap.add_argument('--selfheal-budgets', default=None, type=parse_ints)
    ap.add_argument('--tm-modes', default=None, type=split_csv,
                    help='Comma-separated: auto,on,off.')
    ap.add_argument('--tm-path', default=None)
    ap.add_argument('--lang', default='ru', choices=('ru', 'en'))
    ap.add_argument('--nominal', action='store_true')
    ap.add_argument('--no-grammar', action='store_true')
    ap.add_argument('--out-dir', default=None)
    ap.add_argument('--width-arm', action='store_true',
                    help='H1403 A7: add the dispatch-width axis (--max-wide per arm). Requires '
                         '--healthy-telemetry; refused on anything but measured-healthy windows.')
    ap.add_argument('--widths', default=None, type=parse_ints,
                    help='Width bracket for --width-arm (default 4..%d, the width_policy '
                         'calibration ceiling).' % width_policy.CALIBRATION_CEILING)
    ap.add_argument('--healthy-telemetry', default=None,
                    help='Per-window telemetry JSON (list or {"windows": [...]}, oldest first) '
                         'whose tail must be measured-healthy for the width arm to unlock.')
    ap.add_argument('--emit-only', action='store_true',
                    help='Write manifest/report commands without invoking gen_opt_harness2.py.')
    args = ap.parse_args(argv)
    args = apply_arm_set(args)
    widths = width_bracket(args)

    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.abspath(args.out_dir or os.path.join(OUT, 'perf_calibration',
                                                          '%s_%s' % (args.root, stamp)))
    os.makedirs(out_dir, exist_ok=True)

    manifest = {
        'schema': 'pwg.performance_calibration.v1',
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec='seconds').replace('+00:00', 'Z'),
        'root': args.root,
        'lang': args.lang,
        'keys': args.keys,
        'arm_set': args.arm_set,
        'cache_warning': CACHE_WARNING,
        'arms': [],
    }
    # H4529: the width axis is a 4th arm dimension, defaulting to [None] (untouched width)
    # so every pre-H4529 invocation emits exactly the arms it emitted before.
    for output_budget, selfheal_budget, tm_mode, max_wide in itertools.product(
            args.output_budgets, args.selfheal_budgets, args.tm_modes, widths):
        name = arm_name(output_budget, selfheal_budget, tm_mode, max_wide)
        out_js = os.path.join(out_dir, '%s.js' % name)
        cmd = build_command(args, out_js, output_budget, selfheal_budget, tm_mode, max_wide)
        status, stdout, stderr = 'emit-only', '', ''
        if not args.emit_only:
            proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True,
                                  encoding='utf-8')
            status, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
            if proc.returncode != 0:
                print(proc.stdout)
                print(proc.stderr, file=sys.stderr)
                raise SystemExit(proc.returncode)
        manifest['arms'].append({
            'name': name,
            'output_budget': output_budget,
            'selfheal_budget': selfheal_budget,
            'tm_mode': tm_mode,
            'max_wide': max_wide,
            'harness': out_js,
            'command': cmd,
            'status': status,
            'stdout_tail': stdout[-2000:],
            'stderr_tail': stderr[-2000:],
        })

    manifest_path = os.path.join(out_dir, 'manifest.json')
    readme_path = os.path.join(out_dir, 'REPORT_TEMPLATE.md')
    with open(manifest_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write('\n')
    write_readme(readme_path, manifest)
    print('wrote', manifest_path)
    print('wrote', readme_path)
    print(CACHE_WARNING)


if __name__ == '__main__':
    main()
