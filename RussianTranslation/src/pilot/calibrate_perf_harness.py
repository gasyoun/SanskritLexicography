#!/usr/bin/env python
"""Build scratch harness arms for pwg_ru performance calibration.

This helper only generates harness files plus a manifest/report template. It does
not run Workflow, audit outputs, promote cards, or touch the RU store.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

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


def arm_name(output_budget, selfheal_budget, tm_mode):
    return 'ob%s_sh%s_tm%s' % (output_budget, selfheal_budget, tm_mode)


def build_command(args, out_js, output_budget, selfheal_budget, tm_mode):
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
    ap.add_argument('--emit-only', action='store_true',
                    help='Write manifest/report commands without invoking gen_opt_harness2.py.')
    args = ap.parse_args(argv)
    args = apply_arm_set(args)

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
    for output_budget in args.output_budgets:
        for selfheal_budget in args.selfheal_budgets:
            for tm_mode in args.tm_modes:
                name = arm_name(output_budget, selfheal_budget, tm_mode)
                out_js = os.path.join(out_dir, '%s.js' % name)
                cmd = build_command(args, out_js, output_budget, selfheal_budget, tm_mode)
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
