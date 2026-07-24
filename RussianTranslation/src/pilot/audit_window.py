#!/usr/bin/env python
"""audit_window.py — one deterministic audit command for a translated workflow window.

Runs the free Python gates against the SAME wf_output.json key set, writes one
machine-readable report plus a requeue list, and optionally glues a root article.

  python src/pilot/audit_window.py wf_output.json --root sTA --write-requeue
"""
import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))          # .../src/pilot
SRC = os.path.dirname(HERE)                                # .../src
OUT = os.path.join(HERE, 'output')
# H1386 P3f: PWG_INPUT_DIR points a hermetic harness at a sandbox input dir.
INPUT_DIR = os.environ.get('PWG_INPUT_DIR') or os.path.join(HERE, 'input')  # .../src/pilot/input (portrait sidecars)

sys.path.insert(0, SRC)
import nws_split
import validate_final_card_schema
from safe_filename import safe_name
from dashboard_events import append_event, emit_stage_boundary
from prompt_rule_audit import (
    DEFAULT_HARNESS,
    DEFAULT_TEMPLATE,
    audit_cards as audit_semantic_cards,
    build_report as build_prompt_rule_report,
)
from sense_count import scan_sense_shortfall             # H920 SAN-LOSS sense-count guard
from workflow_payload import workflow_payload
from window_provenance import stale_check
from window_reports import (
    audit_state,
    build_judge_sample,
    build_production_metrics,
    write_reports,
)

def _under_tempdir(path):
    """True if `path` lives under the OS temp dir — i.e. a self-test/fixture wf_output rather
    than a real repo run. Used to auto-guard the live singleton status files (FL8): a fixture
    audit must never overwrite window_status.json / audit_window.report.json. commonpath raises
    ValueError across Windows drives (temp on a different drive than the wf) -> treat as real."""
    try:
        tmp = os.path.realpath(tempfile.gettempdir())
        return os.path.commonpath([tmp, os.path.realpath(path)]) == tmp
    except (ValueError, OSError):
        return False


COLLECT = os.path.join(SRC, '_pilot_collect.py')
BATCH_FILE = os.path.join(OUT, '_realtest_batch.json')
PROTECTED = {'aMSa', 'anna', 'ap'}


def run_final_schema_gate(results):
    """Audit every non-null card against the final record contract in-process."""
    invalid = {}
    checked = 0
    for row in results or []:
        if not isinstance(row, dict) or not row.get('card'):
            continue
        key = row.get('key') or (row['card'].get('key1') if isinstance(row['card'], dict) else '?')
        checked += 1
        try:
            validate_final_card_schema.validate_card(row['card'])
        except ValueError as exc:
            invalid[key] = str(exc)
    lines = ['final-card schema: %d checked, %d invalid' % (checked, len(invalid))]
    lines.extend('  %s: %s' % item for item in sorted(invalid.items()))
    return {
        'argv': ['in-process', 'validate_final_card_schema.validate_card'],
        'returncode': 1 if invalid else 0,
        'stdout': '\n'.join(lines) + '\n',
        'stderr': '',
        'seconds': 0.0,
        'requeue': sorted(invalid),
        'schema_violations': invalid,
    }


def run_py(args, env=None):
    t0 = time.perf_counter()
    argv = [sys.executable] + args
    # P6 (H1422): subprocess.run had no try/except -- a TimeoutExpired/OSError re-raised
    # straight through the caller (collect_cards / root_glue_translated.py) and crashed
    # the whole audit with no report or requeue. The rest of main() already handles a
    # non-{0,1} returncode gracefully (gates/'collect'/'glue' each append to `crashed` and
    # the audit still reports+requeues) -- so on either exception this returns the SAME
    # shape a normal run does, with a distinguishing returncode: 124 (the conventional
    # "timed out" exit code) or -1 for any other OSError (missing interpreter, etc.).
    try:
        p = subprocess.run(argv, cwd=SRC, capture_output=True,
                           text=True, encoding='utf-8', env=env, timeout=1800)
        return {'argv': argv, 'returncode': p.returncode,
                'stdout': p.stdout, 'stderr': p.stderr,
                'seconds': round(time.perf_counter() - t0, 3)}
    except subprocess.TimeoutExpired as e:
        return {'argv': argv, 'returncode': 124, 'stdout': e.stdout or '',
                'stderr': (e.stderr or '') + '\nrun_py: TimeoutExpired after %ss' % e.timeout,
                'seconds': round(time.perf_counter() - t0, 3)}
    except OSError as e:
        return {'argv': argv, 'returncode': -1, 'stdout': '',
                'stderr': 'run_py: OSError: %s' % e,
                'seconds': round(time.perf_counter() - t0, 3)}


def run_py_inproc(args):
    """H1339 Phase 3 (route-neutral speed): run a child gate script IN-PROCESS via runpy
    instead of a fresh interpreter -- the child's imports resolve from this process's
    sys.modules cache, eliminating one interpreter+site+import startup per gate per window
    (5 gates x every audited window). The EXECUTED CODE is byte-identical (runpy runs the
    same script file top-level as __main__), stdout is captured verbatim so the strict
    FLAGGED_JSON parsers see exactly what the subprocess form printed, and SystemExit
    carries the same returncode semantics. Any crash returns rc=3 with the traceback in
    stderr -- feeding the SAME unparseable-verdict fail-loud path as a crashed subprocess
    (H169 defect 2). Callers must not run two of these concurrently (sys.argv/stdout are
    process-global) -- the gate loop runs them sequentially."""
    import contextlib
    import io as _io
    import runpy
    import traceback

    class _CapturedIO(_io.StringIO):
        def reconfigure(self, **_kw):
            # every org script opens with sys.stdout.reconfigure(encoding='utf-8');
            # a captured buffer is already text -- the call is a harmless no-op here.
            return None

    script, argv = args[0], args[1:]
    t0 = time.perf_counter()
    out, err = _CapturedIO(), _CapturedIO()
    old_argv, old_cwd = sys.argv, os.getcwd()
    rc = 0
    try:
        sys.argv = [script] + list(argv)
        os.chdir(SRC)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                runpy.run_path(script, run_name='__main__')
            except SystemExit as exc:
                code = exc.code
                if isinstance(code, int):
                    rc = code
                elif code is None:
                    rc = 0
                else:
                    # H1386 P3e: mirror CPython -- sys.exit('<message>') prints the
                    # message to stderr and exits 1. Pre-fix the diagnosis vanished
                    # (a crashed entry with EMPTY stderr).
                    err.write(str(code) + '\n')
                    rc = 1
            except KeyboardInterrupt:
                # H1386 P3d: an operator abort must ABORT the audit, not be recorded as a
                # crashed gate that pollutes the failure gallery with a phantom crash.
                raise
            except BaseException:
                err.write(traceback.format_exc())
                rc = 3
    finally:
        sys.argv = old_argv
        os.chdir(old_cwd)
    return {'argv': ['in-process'] + list(args), 'returncode': rc,
            'stdout': out.getvalue(), 'stderr': err.getvalue(),
            'seconds': round(time.perf_counter() - t0, 3)}


def parse_flagged_json(stdout):
    """Strict parse of a child auditor's machine-readable verdict line
    (`FLAGGED_JSON: [...]`, emitted by audit_translation.py / audit_coverage.py /
    audit_sense_dupes.py). Returns None — never `[]` — when the line is missing or
    malformed, so the caller can tell "genuinely clean" apart from "unparseable
    output" instead of silently treating a wording drift as a clean pass (H169
    defect 2: the old prose-scraping parser returned [] on any drift and dropped
    flagged cards from the requeue without a trace)."""
    m = re.search(r'^FLAGGED_JSON:\s*(.+)$', stdout, re.M)
    if not m:
        return None
    try:
        parsed = json.loads(m.group(1))
    except (ValueError, TypeError):
        return None
    if not isinstance(parsed, list):
        return None
    return sorted(str(x).strip() for x in parsed if str(x).strip())


parse_translation = parse_flagged_json
parse_coverage = parse_flagged_json
parse_dupes = parse_flagged_json


def exact_file_exists(directory, name):
    try:
        return name in set(os.listdir(directory))
    except OSError:
        return False


def load_protected():
    protected = set(PROTECTED)
    if os.path.exists(BATCH_FILE):
        try:
            batch = json.load(open(BATCH_FILE, encoding='utf-8'))
            protected.update(batch.get('protected') or [])
        except Exception:
            pass
    return protected


def quarantine(key):
    for nm in (safe_name(key) + '.merged.md', key + '.merged.md'):
        if exact_file_exists(OUT, nm):
            src = os.path.join(OUT, nm)
            dst = os.path.join(OUT, nm[:-len('.merged.md')] + '.merged.REJECTED.md')
            if os.path.exists(dst):
                os.remove(dst)
            os.replace(src, dst)
            return True
    return False


def collect_cards(wf, protected):
    env = os.environ.copy()
    env['PILOT_COLLECT_PROTECTED'] = ','.join(sorted(protected))
    return run_py([COLLECT, wf], env=env)


def run_nws_gate(keys, protected):
    t0 = time.perf_counter()
    lines = ['=== 2. NWS attribution audit (nws_split) ===']
    clean = misattr = no_nws = missing_raw = missing_card = other = 0
    bad_cards, bad_misattribution = [], []
    for k in keys:
        if k in protected:
            lines.append('  %-12s protected — keeping hand-authored card' % k)
        res = nws_split.check_result(k)
        lines.extend(res['lines'])
        verdict = res['verdict']
        if verdict == 'CLEAN':
            clean += 1
        elif verdict == 'NO-NWS':
            no_nws += 1
        elif verdict == 'NO-RAW':
            missing_raw += 1
            bad_cards.append(k)
        elif verdict == 'NO-CARD':
            missing_card += 1
            bad_cards.append(k)
        elif verdict == 'MISATTRIBUTION':
            misattr += 1
            bad_cards.append(k)
            bad_misattribution.append(k)
        else:
            other += 1

    lines += ['', '=== REPORT ===']
    lines.append('  cards audited      : %d' % len(keys))
    lines.append('  NWS audit CLEAN    : %d' % clean)
    lines.append('  F12 misattribution : %d %s' % (
        misattr, ('→ ' + ' '.join(bad_misattribution)) if bad_misattribution else ''))
    lines.append('  no NWS fragment    : %d' % no_nws)
    lines.append('  missing raw input  : %d' % missing_raw)
    lines.append('  missing card output: %d' % missing_card)
    lines.append('  other verdicts     : %d' % other)
    lines.append('  judge pass rate    : see "publishable" line in collect section above')

    gate_fail = [k for k in bad_cards if k not in protected]
    if gate_fail:
        lines.append('')
        lines.append('  GATE: FAIL — %d card(s) require rejection (F12 slide): %s'
                     % (len(gate_fail), ' '.join(gate_fail)))
    else:
        lines.append('')
        lines.append('  GATE: PASS — no F12 misattribution in fresh cards')

    return {'argv': ['in-process', 'nws_split.check_result'], 'returncode': 1 if gate_fail else 0,
            'stdout': '\n'.join(lines) + '\n', 'stderr': '', 'requeue': sorted(gate_fail),
            'misattribution': sorted(k for k in bad_misattribution if k not in protected),
            'rejected': [], 'seconds': round(time.perf_counter() - t0, 3)}


def run_prompt_semantic_audit(wf, protected, review_limit=25):
    t0 = time.perf_counter()
    paths = [os.path.abspath(DEFAULT_TEMPLATE)]
    harness = os.path.abspath(DEFAULT_HARNESS)
    if os.path.exists(harness):
        paths.append(harness)
    prompt_rules = build_prompt_rule_report(paths)
    card_risks = audit_semantic_cards(wf, review_limit=review_limit)
    requeue = sorted(
        key for key in (card_risks.get('requeue_keys') or [])
        if key not in set(protected))
    missing_rule_count = prompt_rules.get('missing_rule_count', 0)
    lines = [
        'Prompt/manual rules: %s (%d missing required rule%s)' % (
            'FAIL' if missing_rule_count else 'PASS',
            missing_rule_count,
            '' if missing_rule_count == 1 else 's'),
        'Live manual coverage: %s' % ', '.join(
            prompt_rules.get('live_manual_coverage') or []),
        'Methodology/design only: %s' % ', '.join(
            prompt_rules.get('methodology_only_manuals') or []),
        'Semantic risks: %d risk(s) across %d key(s); high-confidence=%d key(s)' % (
            card_risks.get('risk_count', 0),
            card_risks.get('risky_key_count', 0),
            len(card_risks.get('high_confidence_keys') or [])),
        'High-confidence requeue candidates: %s' % (
            ', '.join(requeue) if requeue else '(none)'),
    ]
    queue = (card_risks.get('review_queue') or {}).get('items') or []
    if queue:
        lines.append('Review queue:')
        for item in queue[:10]:
            lines.append('  %-34s score=%d high_confidence=%d risks=%s' % (
                item['key'], item['risk_score'],
                item.get('high_confidence_count', 0),
                ', '.join(item.get('top_risks') or [])))
    for target in prompt_rules.get('targets') or []:
        for rule in target.get('missing') or []:
            lines.append('  missing %s in %s: %s' % (
                rule['id'], os.path.relpath(target['path'], SRC),
                ', '.join(rule.get('missing_phrases') or [])))
    return {
        'argv': ['in-process', 'prompt_rule_audit'],
        'returncode': 2 if missing_rule_count else (1 if requeue else 0),
        'stdout': '\n'.join(lines) + '\n',
        'stderr': '',
        'requeue': requeue,
        'prompt_rules': prompt_rules,
        'card_risks': card_risks,
        'seconds': round(time.perf_counter() - t0, 3),
    }


def run_sense_shortfall_gate(results, input_dir, protected):
    """H920 deterministic SAN-LOSS guard: flag any translated card whose OUTPUT sense count
    falls short of its input portrait's declared source_senses.

    Closes the no_pwg / supplement whole-card gap the H911 gate surfaced: the harness
    accept() gate is only an <ls>/{# token-count match, so a dropped citation-free sense
    (e.g. darv_i~~h0_zz_pw: 3 source senses -> output 2, sense 1 "Löffel" dropped, ls 0==0 &
    sk 3==3) passes clean and is never flagged partial/missing_senses. This gate compares the
    portrait's deterministic source-sense count (stamped by _pilot_gen_merged.gen_no_pwg_card)
    to the output card's sense count and requeues the shortfall as a content defect BEFORE
    promotion. In-process, no model/network. A card whose portrait predates the H920 stamp
    (source_senses absent) is silently skipped — never a false positive."""
    t0 = time.perf_counter()
    short = [s for s in scan_sense_shortfall(results, input_dir) if s['key'] not in protected]
    lines = ['=== 7. SAN-LOSS sense-count guard (portrait source_senses vs output) ===']
    if short:
        for s in short:
            lines.append('  %-30s SAN-LOSS: output %d < source %d (dropped %d sense(s))'
                         % (s['key'], s['actual'], s['expected'], s['dropped']))
        lines.append('')
        lines.append('  GATE: FAIL — %d card(s) dropped a whole source sense: %s'
                     % (len(short), ' '.join(s['key'] for s in short)))
    else:
        lines.append('  GATE: PASS — no output card falls short of its source sense count')
    return {'argv': ['in-process', 'sense_count.scan_sense_shortfall'],
            'returncode': 1 if short else 0,
            'stdout': '\n'.join(lines) + '\n', 'stderr': '',
            'requeue': sorted(s['key'] for s in short),
            'sense_shortfall': short,
            'seconds': round(time.perf_counter() - t0, 3)}


def emit_audit_event(event_type, level='info', root=None, state=None, summary='', data=None):
    append_event('audit_window', event_type, level=level, root=root,
                 state=state, summary=summary, data=data or {})
    # Auto-capture genuine failures (error-level) into the failure gallery for the
    # dashboard's typology/trends. Best-effort + de-duped per (mode, root, day) so
    # it never floods the curated post-mortems or breaks an audit.
    if level == 'error':
        try:
            from failure_capture import append_failure
            append_failure(mode=state or event_type or 'audit-failure',
                           symptom=summary or event_type, severity='high',
                           root=root, data={'event_type': event_type})
        except Exception:
            pass


def classify_harness_requeues(null_cards, partial_cards, gate_requeue, failure_reasons):
    """Split incomplete harness output from independently gate-flagged defects."""
    null_set = set(null_cards or [])
    partial_set = set(partial_cards or [])
    gate_set = set(gate_requeue or [])
    fidelity_nulls = {
        k for k, e in (failure_reasons or {}).items()
        if e.startswith('fidelity-reject') or e.startswith('stitched-fidelity')
    }
    defect = (gate_set - null_set) | fidelity_nulls
    transient = (null_set | partial_set) - defect
    return transient, defect, fidelity_nulls


def collect_harness_quality(results):
    """Extract explicit partial-card and null-failure metadata from harness rows."""
    partial_cards, failure_reasons = {}, {}
    for row in results or []:
        key = row.get('key')
        if not key:
            continue
        card = row.get('card')
        if card and (card.get('partial') or row.get('partial')):
            partial_cards[key] = {
                name: (card.get(name) if card.get(name) is not None else row.get(name))
                for name in ('missing_fragments', 'missing_groups', 'total_groups',
                             'missing_senses', 'total_senses')
                if card.get(name) is not None or row.get(name) is not None
            }
        if not card and row.get('error'):
            failure_reasons[key] = row['error']
    return partial_cards, failure_reasons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('wf_output')
    ap.add_argument('--root')
    ap.add_argument('--execution-manifest',
                    help='prepared pwg.headless_execution_manifest.v1 contract for this output')
    ap.add_argument('--write-requeue', action='store_true')
    ap.add_argument('--allow-stale', action='store_true',
                    help='forensic mode: continue even if workflow/rootmap/input provenance is stale')
    ap.add_argument('--ephemeral', action='store_true',
                    help='fixture/self-test mode: write status+report to a throwaway scratch dir, '
                         'never touching the live singleton window_status.json / '
                         'audit_window.report.json (auto-enabled for a wf_output under the OS temp dir)')
    ap.add_argument('--out-dir',
                    help='write report/status/requeue artifacts to this directory instead of src/pilot/output')
    ap.add_argument('--window-tag', nargs='?', const='', default=None,
                    help='H336/H-2: route window_status/report/requeue/judge-sample artifacts to '
                         'src/pilot/output/<tag>/ instead of the flat singletons, so 3 accounts '
                         'auditing 3 different windows in ONE clone cannot clobber each other\'s '
                         'status or requeue a sibling window\'s keys. Bare --window-tag (no value) '
                         'defaults the tag to --root. Omit entirely for the untagged legacy '
                         'behavior (writes src/pilot/output/ singletons, unchanged).')
    ap.add_argument('--judge-sample-rate', type=float, default=0.10,
                    help='deterministic clean-key semantic judge sample rate (default: 0.10)')
    ap.add_argument('--judge-sample-min', type=int, default=5,
                    help='minimum clean keys to sample when clean keys exist (default: 5)')
    ap.add_argument('--judge-sample-seed',
                    help='override deterministic semantic sample seed')
    ap.add_argument('--wall-clock-minutes', type=float,
                    help='Max workflow wall-clock minutes for this run/window')
    ap.add_argument('--max-input-tokens', type=int,
                    help='Max-reported input tokens')
    ap.add_argument('--max-output-tokens', type=int,
                    help='Max-reported output tokens')
    ap.add_argument('--max-cache-read-tokens', type=int,
                    help='Max-reported cache_read tokens')
    ap.add_argument('--max-cache-create-tokens', type=int,
                    help='Max-reported cache_create tokens')
    ap.add_argument('--max-total-tokens', type=int,
                    help='Max-reported total tokens, if available')
    ap.add_argument('--weekly-cap-fired', action='store_true',
                    help='record that the Max weekly cap fired during/after this window')
    ap.add_argument('--weekly-cap-cumulative-tokens', type=int,
                    help='cumulative token count observed when the weekly cap fired')
    ap.add_argument('--metrics-note',
                    help='short free-text note for the production metrics ledger')
    args = ap.parse_args()

    wf = os.path.abspath(args.wf_output)
    if not os.path.exists(wf):
        sys.exit('no workflow output %r' % args.wf_output)
    # FL8 fixture guard: a self-test / temp-file audit writes its status+report to a scratch
    # dir so it can never clobber the live singletons; a real repo run writes OUT as before.
    ephemeral = args.ephemeral or _under_tempdir(wf)
    # Precedence: explicit --out-dir wins outright; else --window-tag namespaces under
    # OUT/<tag> (tag defaults to --root when the flag is bare); else the ephemeral
    # scratch-dir guard; else None (write the flat OUT singletons, untagged legacy path).
    window_tag = (args.window_tag or args.root or 'default') if args.window_tag is not None else None
    report_out_dir = os.path.abspath(args.out_dir) if args.out_dir else (
        os.path.join(OUT, safe_name(window_tag)) if window_tag else (
        tempfile.mkdtemp(prefix='pwg_audit_ephemeral_') if ephemeral else None))

    _payload, wf_meta, results, keys, null_cards = workflow_payload(wf)
    emit_stage_boundary(
        'audit_start', window_tag=window_tag, root=args.root,
        data={'workflow': wf, 'workflow_keys': len(keys)})
    emit_audit_event(
        'audit_start', root=args.root, state='started',
        summary='audit started for %s (%d workflow keys)' % (os.path.basename(wf), len(keys)),
        data={'workflow': wf, 'workflow_keys': len(keys),
              'null_cards': len(null_cards),
              'has_meta': bool(wf_meta),
              'allow_stale': args.allow_stale})
    execution_manifest = None
    if args.execution_manifest:
        try:
            with open(args.execution_manifest, encoding='utf-8') as f:
                execution_manifest = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            execution_manifest = {'_load_error': str(e)}
    stale = stale_check(args.root, wf_meta, keys, execution_manifest=execution_manifest)
    if stale.get('stale') and not args.allow_stale:
        print('\n=== stale artifact check ===')
        for err in stale.get('errors') or []:
            print('  ' + err)
        print('  refusing collect/gates/glue; refresh wf_output.json or rerun with --allow-stale for inspection')
        report = {'workflow': wf, 'root': args.root, 'state': 'stale_artifact',
                  'workflow_meta': wf_meta, 'stale_check': stale,
                  'keys': keys, 'null_cards': null_cards,
                  'collect': None, 'gates': {}, 'glue': None,
                  'requeue': [], 'crashed': ['stale_artifact'],
                  'requeue_file_written': False,
                  'requeue_file_preserved': bool(args.write_requeue),
                  'requeue_note': 'stale artifact refused before gates; existing requeue.keys.txt preserved; no trustworthy mechanical requeue generated',
                  'judge_sample_rate': args.judge_sample_rate,
                  'judge_sample_min': args.judge_sample_min,
                  'judge_sample_seed': args.judge_sample_seed,
                  'production_metrics': build_production_metrics(
                      args, wf_path=wf, workflow_meta=wf_meta)}
        json_path, md_path, rq_path, js_path, status_json, status_md = write_reports(
            report, args.write_requeue, write_requeue_file=False, out_dir=report_out_dir)
        emit_audit_event(
            'stale_refusal', level='error', root=args.root, state='stale_artifact',
            summary='stale artifact refused before collect/gates/glue (%d issue%s)' %
            (len(stale.get('errors') or []), '' if len(stale.get('errors') or []) == 1 else 's'),
            data={'workflow': wf, 'errors': stale.get('errors') or [],
                  'warnings': stale.get('warnings') or [],
                  'workflow_keys': len(keys),
                  'expected_keys': len(((stale.get('current') or {}).get('selected_keys') or [])),
                  'missing_keys': stale.get('missing_keys') or [],
                  'unexpected_keys': stale.get('unexpected_keys') or []})
        emit_stage_boundary(
            'audit_end', window_tag=window_tag, root=args.root,
            data={'workflow': wf, 'state': 'stale_artifact', 'cards': len(keys)})
        emit_audit_event(
            'audit_end', level='error', root=args.root, state='stale_artifact',
            summary='audit ended: stale_artifact; cards=%d requeue=0' % len(keys),
            data={'workflow': wf, 'cards': len(keys), 'state': 'stale_artifact',
                  'requeue_count': 0, 'crashed': ['stale_artifact'],
                  'status_json': status_json})
        print('report json  : %s' % os.path.relpath(json_path, SRC))
        print('report md    : %s' % os.path.relpath(md_path, SRC))
        print('status json  : %s' % os.path.relpath(status_json, SRC))
        print('status md    : %s' % os.path.relpath(status_md, SRC))
        print('judge sample : %s' % os.path.relpath(js_path, SRC))
        if args.write_requeue:
            print('requeue file : preserved (stale artifact)')
        elif rq_path:
            print('requeue file : %s' % os.path.relpath(rq_path, SRC))
        sys.exit(2)
    if stale.get('stale') and args.allow_stale:
        print('\n=== stale artifact check (allowed) ===')
        for err in stale.get('errors') or []:
            print('  ' + err)
    protected = load_protected()
    gates = {'final_schema': run_final_schema_gate(results)}

    print('\n=== collect ===')
    collect = collect_cards(wf, protected)
    print(collect['stdout'].rstrip())
    if collect['stderr'].strip():
        print(collect['stderr'].rstrip(), file=sys.stderr)

    commands = [
        ('translation', [os.path.join(SRC, 'audit_translation.py'), '--wf', wf], parse_translation),
        ('stage2_mechanical', [os.path.join(SRC, 'stage2_pregate.py'), '--wf', wf], parse_flagged_json),
        ('coverage', [os.path.join(SRC, 'audit_coverage.py'), wf], parse_coverage),
        ('sense_dupes', [os.path.join(SRC, 'audit_sense_dupes.py'), wf], parse_dupes),
        # H1305: RU-only mechanical style gate (no-ё, terse editorial metalanguage «вм.»/
        # «в знач.», in-<ls> `ed. Bomb.` left verbatim) -- reads the SAME .merged.md rendered
        # output as translation/stage2_mechanical above. RU-only by construction (LANG_PARITY
        # ru_style_mechanical_yo_terseness); never wired into audit_window_en.py.
        ('ru_style', [os.path.join(SRC, 'ru_style_sweep.py'), '--wf', wf], parse_flagged_json),
    ]
    futures = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futures[ex.submit(run_nws_gate, keys, protected)] = ('nws', None)
        futures[ex.submit(run_prompt_semantic_audit, wf, protected)] = ('prompt_semantic', None)
        futures[ex.submit(run_sense_shortfall_gate, results, INPUT_DIR, protected)] = ('sense_loss', None)
        for fut in concurrent.futures.as_completed(futures):
            name, parser = futures[fut]
            res = fut.result()
            gates[name] = res
    # H1339 Phase 3: the five child-script gates run IN-PROCESS (runpy), sequentially --
    # sys.argv/stdout are process-global, so they must not overlap; the thread pool above
    # only existed to hide per-gate interpreter startup, which run_py_inproc eliminates.
    # Same scripts, same stdout, same strict parsers, same fail-loud path.
    for name, cmd, parser in commands:
        res = run_py_inproc(cmd)
        if parser:
            parsed = parser(res['stdout'])
            if parsed is None:
                # Unparseable child verdict (missing/malformed FLAGGED_JSON line): never
                # silently treat this as "no flags". Fail loud and requeue every card in
                # the window so a wording drift in the child auditor cannot silently drop
                # flagged cards (H169 defect 2).
                res['requeue'] = sorted(keys)
                res['unparseable_verdict'] = True
            else:
                res['requeue'] = parsed
        gates[name] = res

    for name in ['final_schema', 'nws', 'translation', 'stage2_mechanical', 'coverage',
                 'sense_dupes', 'prompt_semantic', 'sense_loss', 'ru_style']:
        res = gates[name]
        print('\n=== %s ===' % name)
        print(res['stdout'].rstrip())
        if res['stderr'].strip():
            print(res['stderr'].rstrip(), file=sys.stderr)
        emit_audit_event(
            'gate_summary',
            level='warn' if res['returncode'] or res.get('requeue') else 'info',
            root=args.root,
            state='gate_failed' if res['returncode'] not in (0, 1) else
            ('needs_requeue' if res.get('requeue') else 'clean'),
            summary='%s exit=%s requeue=%d' %
            (name, res['returncode'], len(res.get('requeue') or [])),
            data={'gate': name, 'returncode': res['returncode'],
                  'requeue': res.get('requeue') or [], 'seconds': res.get('seconds')})

    if gates['nws'].get('misattribution'):
        rejected = [k for k in gates['nws']['misattribution'] if quarantine(k)]
        gates['nws']['rejected'] = rejected
        if rejected:
            gates['nws']['stdout'] += '  quarantined        : %s\n' % ' '.join(rejected)

    glue = None
    # Root-article glue reassembles a PWG root's sub-cards from its rootmap. A NOMINAL window
    # (keys-based, meta.nominal / no rootmap on disk — e.g. the H214 no-PWG supplement lane) has
    # no rootmap, so root_glue_translated crashes there (H201/H214 caveat). Skip glue cleanly in
    # that case: the content gates above still vet the cards; there is simply no root to glue.
    rootmap_path = os.path.join(OUT, safe_name(args.root) + '.rootmap.json') if args.root else None
    nominal_window = bool((wf_meta or {}).get('nominal')) or (
        bool(args.root) and not os.path.exists(rootmap_path))
    if args.root and nominal_window:
        print('\n=== glue %s: skipped (nominal / no-rootmap window) ===' % args.root)
    elif args.root:
        print('\n=== glue %s ===' % args.root)
        res = run_py([os.path.join(SRC, 'root_glue_translated.py'), args.root])
        print(res['stdout'].rstrip())
        if res['stderr'].strip():
            print(res['stderr'].rstrip(), file=sys.stderr)
        nested = os.path.join(OUT, safe_name(args.root) + '.NESTED.md')
        glue = {'returncode': res['returncode'], 'stdout': res['stdout'], 'stderr': res['stderr'],
                'summary': (res['stdout'].strip().splitlines()[-1] if res['stdout'].strip() else ''),
                'nested_exists': os.path.exists(nested)}
        emit_audit_event(
            'glue_result',
            level='warn' if glue['returncode'] or not glue['nested_exists'] else 'info',
            root=args.root,
            state='blocked' if glue['returncode'] or not glue['nested_exists'] else 'ok',
            summary=glue['summary'] or 'glue finished',
            data={'returncode': glue['returncode'],
                  'nested_exists': glue['nested_exists'],
                  'seconds': res.get('seconds')})

    requeue = set(null_cards)
    gate_requeue = set()
    crashed = []
    for name, gate in gates.items():
        gate_requeue.update(gate.get('requeue') or [])
        if gate['returncode'] not in (0, 1):
            crashed.append(name)
        if gate.get('unparseable_verdict'):
            crashed.append(name + '-unparseable-verdict')
    requeue.update(gate_requeue)
    if glue and glue['returncode'] != 0:
        crashed.append('glue')
    if glue and not glue.get('nested_exists'):
        crashed.append('glue-missing-nested')

    if collect['returncode'] not in (0, 1):
        crashed.append('collect')

    # Harness-side quality markers (post-#63/#64 wf files): per-row failure reasons on null
    # cards, and partial:true cards (usable but incomplete — selfheal/autosplit partial
    # credit). Older wf files carry neither; everything below degrades to empty.
    partial_cards, failure_reasons = collect_harness_quality(results)

    # Partial output remains promotable as useful intermediate data, but it is never a clean
    # window result. Requeue it for targeted top-up even when percentage gates miss a small
    # omission.
    partial_set = set(partial_cards)
    requeue.update(partial_set)

    report = {'workflow': wf, 'root': args.root, 'keys': keys, 'null_cards': null_cards,
              'workflow_meta': wf_meta, 'stale_check': stale,
              'collect': collect,
              'gates': gates, 'glue': glue, 'requeue': sorted(requeue), 'crashed': crashed,
              'partial_cards': partial_cards, 'failure_reasons': failure_reasons}
    # Split the requeue: transient = card came back null (rate-limit/dropout -> cheap re-run
    # at low concurrency); defect = a gate flagged real content on a card that DID translate
    # (needs rework). A null key fails coverage etc. only because it is absent, so it is
    # transient, never a defect. PROCESS_AUDIT_2026-06-29.md rec 3/10.
    # Refinement: a null whose recorded reason is a fidelity REJECT is retry-RESISTANT by
    # construction (the model answered; the deterministic guard refused it — observed live
    # as the Sam/Buj/naS 'stubborn null' loop) -> classify as defect, not transient, so the
    # cheap-re-run lane stops burning quota on it.
    transient, defect, fidelity_nulls = classify_harness_requeues(
        null_cards, partial_set, gate_requeue, failure_reasons)
    report['requeue_transient'] = sorted(transient)
    report['requeue_defect'] = sorted(defect)
    # H304 gate-outcome memory: the fragment TM is harvested from raw wf_output BEFORE any
    # gate runs, so a defect card's fragments would otherwise stay silently reusable
    # (frag_address keys on the input SHA, not on whether the output passed). Surface every
    # defect card's frag_prov fsha here; requeue_from_audit appends them to the TM denylist
    # alongside the card addresses. Conservative by design — the gates flag CARDS, so all of
    # a flagged card's fragments are blocked (a re-translation is cheap; a re-served defect
    # is the gam requeue trap at fragment granularity).
    defect_set = set(report['requeue_defect'])
    report['requeue_defect_fshas'] = sorted(
        {fp['fsha'] for r in results or [] if r and r.get('key') in defect_set
         for fp in ((r.get('card') or {}).get('frag_prov') or []) if fp.get('fsha')})
    report['prompt_rules'] = gates.get('prompt_semantic', {}).get('prompt_rules')
    report['semantic_risks'] = gates.get('prompt_semantic', {}).get('card_risks')
    report['sense_shortfall'] = gates.get('sense_loss', {}).get('sense_shortfall') or []
    report['judge_sample_rate'] = args.judge_sample_rate
    report['judge_sample_min'] = args.judge_sample_min
    report['judge_sample_seed'] = args.judge_sample_seed
    report['judge_sample'] = build_judge_sample(
        report, args.judge_sample_rate, args.judge_sample_min, args.judge_sample_seed)
    report['production_metrics'] = build_production_metrics(
        args, wf_path=wf, workflow_meta=wf_meta)
    json_path, md_path, rq_path, js_path, status_json, status_md = write_reports(
        report, args.write_requeue, out_dir=report_out_dir)
    state = audit_state(report)
    emit_audit_event(
        'requeue_summary',
        level='warn' if report['requeue'] else 'info',
        root=args.root, state=state,
        summary='requeue count %d' % len(report['requeue']),
        data={'requeue_count': len(report['requeue']),
              'requeue': report['requeue'],
              'partial_cards': sorted(partial_cards),
              'failure_reasons': failure_reasons,
              'judge_sample_count': report['judge_sample']['sample_count'],
              'judge_sample_seed': report['judge_sample']['seed'],
              'clean_key_count': report['judge_sample']['clean_key_count'],
              'production_metrics': report.get('production_metrics') or {}})
    if crashed:
        emit_audit_event(
            'crash_state', level='error', root=args.root, state='blocked',
            summary='crashed gates: %s' % ', '.join(crashed),
            data={'crashed': crashed})
    emit_stage_boundary(
        'audit_end', window_tag=window_tag, root=args.root,
        data={'workflow': wf, 'state': state, 'cards': len(keys),
              'requeue_count': len(report['requeue']),
              'wall_clock_source': (report.get('production_metrics') or {}).get(
                  'wall_clock_source')})
    emit_audit_event(
        'audit_end',
        level='error' if crashed else ('warn' if report['requeue'] else 'info'),
        root=args.root, state=state,
        summary='audit ended: %s; cards=%d requeue=%d' %
        (state, len(keys), len(report['requeue'])),
        data={'workflow': wf, 'cards': len(keys), 'state': state,
              'requeue_count': len(report['requeue']),
              'crashed': crashed, 'status_json': status_json})

    print('\n=== AUDIT WINDOW SUMMARY ===')
    print('cards        : %d' % len(keys))
    print('requeue      : %d%s' % (len(report['requeue']),
          '' if not report['requeue'] else ' (' + ', '.join(report['requeue'][:12]) + (', ...' if len(report['requeue']) > 12 else '') + ')'))
    print('  transient  : %d (null cards — cheap re-run at low concurrency)' % len(report.get('requeue_transient') or []))
    print('  defect     : %d (real content failures — needs rework%s)' % (
        len(report.get('requeue_defect') or []),
        (', incl. %d retry-resistant fidelity-reject null(s)' % len(fidelity_nulls)) if fidelity_nulls else ''))
    if partial_cards:
        print('partial cards: %d (usable but incomplete — missing pieces recorded in report): %s'
              % (len(partial_cards), ', '.join(sorted(partial_cards)[:8])
                 + (', ...' if len(partial_cards) > 8 else '')))
    if failure_reasons:
        from collections import Counter
        top = Counter(e.split(':')[0] for e in failure_reasons.values()).most_common()
        print('null reasons : %s' % ', '.join('%s x%d' % (r, n) for r, n in top))
    print('clean keys   : %d' % report['judge_sample']['clean_key_count'])
    print('judge sample : %d (seed %s)' % (report['judge_sample']['sample_count'], report['judge_sample']['seed']))
    print('report json  : %s' % os.path.relpath(json_path, SRC))
    print('report md    : %s' % os.path.relpath(md_path, SRC))
    print('status json  : %s' % os.path.relpath(status_json, SRC))
    print('status md    : %s' % os.path.relpath(status_md, SRC))
    print('judge sample : %s' % os.path.relpath(js_path, SRC))
    if rq_path:
        print('requeue file : %s' % os.path.relpath(rq_path, SRC))
    if crashed:
        print('crashed gates: %s' % ', '.join(crashed))
    sys.exit(1 if report['requeue'] or crashed else 0)


if __name__ == '__main__':
    main()


