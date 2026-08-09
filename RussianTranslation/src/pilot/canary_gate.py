#!/usr/bin/env python
"""H2159 (H2025 G4 / F-B2+F-B3) — the canary half of the live gate, as CODE.

Before this module the /pwg-live-gate canary verdict ("3/3 senses + zero
SAN-LOSS/TNMASK") existed only as skill PROSE: an operator/model read the
canary wf_output and typed GO or NO-GO, nothing recorded the verdict, and
``bounded_staged_run.py --execute`` had no way to know whether a gate had run,
passed, or run two days ago (the health half was already mechanical —
``probe_log.derive_fails`` + the probe receipts — this closes the other half).

Two commands:

``judge <wf_output.json> [--expect-senses 3] [--receipt PATH]``
    Derive the verdict mechanically and write an atomic GO/NO-GO receipt:
    - the envelope must parse and every result key must be SYNTHETIC
      (``execution_contract.SYNTHETIC_KEY_RE`` — judging a REAL window as a
      canary is itself a NO-GO);
    - every card must be non-null with exactly ``--expect-senses`` senses
      carrying non-empty ``russian`` (the canary-level SAN-LOSS check: a
      dropped sense shows up as a shortfall);
    - zero unresolved ``{Tn}`` placeholders anywhere in the card
      (``promote_final_cards.TN_RE`` — the same single-sourced regex the
      promote C-01 guard uses, so the two can never drift);
    - zero literal ``SAN-LOSS`` / ``UNMAPPED`` markers in the card text.

``check <receipt> [--max-age-seconds N] [--only-profile SLOT]``
    Validate a receipt the way ``--execute`` does: verdict GO, age within
    bound, profile matches. Exit 0 on pass, 2 on refusal.

``bounded_staged_run.py --execute`` calls ``enforce()`` — a paid run now
REFUSES to start without a fresh canary GO receipt (``--skip-canary-gate`` is
the explicit, command-review-visible escape hatch).
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

from promote_final_cards import SYNTHETIC_KEY_RE, TN_RE  # noqa: E402  C-01 single source
import marker_scan  # noqa: E402  H2253 — one marker/{Tn} scope definition, two gates
from execution_contract import PRODUCTION_HARD_TIMEOUT_MS  # noqa: E402  H2254 one ceiling

RECEIPT_SCHEMA = 'pwg.canary_gate_receipt.v1'
# H2254: the fields a bounded live proof must be able to answer FROM ITS OWN ARTIFACT.
#
# The v1 receipt recorded the verdict and its reasons and nothing about the run that produced
# it -- so "how many calls did this actually cost, what did it cost in dollars, was the kill
# switch on, which commit was it" were answerable only by correlating four separate files by
# hand, and only while the operator still remembered which four. That is exactly the shape of
# evidence the live-gate contract calls disposable. The keys below are ADDITIVE: `verdict`,
# `reasons`, `facts`, `profile_slot` and `cli_safe_mode` keep their v1 meaning and position,
# so `enforce()` and every receipt already on disk stay valid and the schema token does not
# move. Missing evidence is recorded as None, never as a zero -- a zero cost and an unknown
# cost are the distinction 05-08 turned on (`observed_cost_usd: 0` meaning "not evaluable"
# versus 06-08's genuine $0 refusal), and collapsing them is how a floor gets read as a total.
EVIDENCE_KEYS = ('commit', 'manifest_sha256', 'manifest_path', 'status_path',
                 'call_reservation_path', 'run_id', 'calls_spent', 'max_calls',
                 'observed_cost_usd', 'cost_evaluable', 'unevaluable_calls',
                 'api_latency_ms', 'wall_latency_ms', 'kill_switch',
                 'cli_safe_mode_effective', 'timeout_ceil_ms', 'hard_timeout_ms')
DEFAULT_EXPECT_SENSES = 3
DEFAULT_MAX_AGE_SECONDS = 6 * 3600   # same freshness posture as the probe receipts
LITERAL_MARKERS = ('SAN-LOSS', 'UNMAPPED')


def _load_wf(path):
    with open(path, encoding='utf-8') as fh:
        wrapper = json.load(fh)
    result = wrapper.get('result')
    if isinstance(result, str):
        result = json.loads(result)
    return result if result is not None else wrapper


def judge_payload(res, expect_senses=DEFAULT_EXPECT_SENSES):
    """Pure verdict derivation -> (verdict, reasons, facts). No I/O."""
    reasons = []
    results = res.get('results') or []
    if not results:
        return 'NO-GO', ['no results in the canary output'], {}
    keys, sense_counts, tn_hits, marker_hits = [], [], [], []
    for row in results:
        key = row.get('key') or '<missing-key>'
        keys.append(key)
        if not SYNTHETIC_KEY_RE.search(key):
            reasons.append('%s: NOT a synthetic-control key — refusing to judge a real '
                           'window as a canary' % key)
            continue
        card = row.get('card')
        if not card:
            reasons.append('%s: null card' % key)
            continue
        # H2253 (#1073): both scopes now come from ``marker_scan`` — the sibling
        # ci_gate_runner carried the identical whole-card scan and kept failing this
        # very fixture after H2174 fixed it here. One definition, two consumers.
        # H2174: the literal-marker scan reads TRANSLATED CONTENT only, never the
        # card's free-text ``notes``. The curated canary fixture's portrait ``note``
        # (pwg_ru/h994/canary/…portrait.json) contains the literal string "SAN-LOSS"
        # and is fed to the model VERBATIM as prompt input, so every real canary run
        # paraphrases it back into ``notes`` — observed identically in H1447 (22-07)
        # and H2011 (02-08). Scanning the whole card therefore made this gate
        # UNPASSABLE for the one fixture it exists to judge (the H2160
        # "inert by construction" class, inverted: always-fail instead of
        # always-pass). It stayed invisible because the selftest's clean_card
        # carries no ``notes`` key at all. Sense loss is still caught — by the
        # sense-count check above, which is the fixture's actual detector.
        senses = sum(1 for rec in card.get('records') or []
                     for sense in rec.get('senses') or []
                     if (sense.get('russian') or '').strip())
        sense_counts.append((key, senses))
        if senses != expect_senses:
            reasons.append('%s: %d/%d senses with Russian content (canary SAN-LOSS '
                           'shortfall)' % (key, senses, expect_senses))
        hits = marker_scan.tn_hits(card)
        if hits:
            tn_hits.append((key, hits[:5]))
            reasons.append('%s: unresolved TNMASK placeholder(s): %s'
                           % (key, ', '.join(hits[:5])))
        for marker in marker_scan.marker_hits(card):
            marker_hits.append((key, marker))
            reasons.append('%s: literal %s marker in card' % (key, marker))
    facts = {'keys': keys, 'sense_counts': sense_counts,
             'tn_hits': tn_hits, 'marker_hits': marker_hits}
    return ('GO' if not reasons else 'NO-GO'), reasons, facts


def _atomic_write_json(path, payload):
    directory = os.path.dirname(os.path.abspath(path)) or '.'
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.%s.' % os.path.basename(path),
                               suffix='.tmp', dir=directory)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def _abs_or_none(path):
    return os.path.abspath(path) if path else None


def _read_json(path):
    """Best effort: absent or unreadable evidence is None, never a fabricated zero."""
    if not path:
        return None
    try:
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _repo_commit():
    """The commit the paid call ran from. `None` if git cannot answer -- the handoff's
    'seal the released commit' is a claim about a real revision, so a guess is worse
    than an absence."""
    try:
        out = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=HERE, capture_output=True,
                             text=True, encoding='utf-8', timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None if out.returncode == 0 else None


def _latencies(reservation, run_id):
    """Wall and route latency of the MEASURED calls, from the durable reservation ledger.

    Returns the maximum over finalized reservations rather than a sum or a mean: the gate's
    question is "did any call breach the ceiling", and a mean hides exactly the bimodality
    (a 15 s warm-up beside a 300 s measured leg) that every c4 NO-GO day so far has shown.
    """
    if not isinstance(reservation, dict):
        return None, None
    run = ((reservation.get('runs') or {}).get(str(run_id))
           if run_id else None)
    if run is None:
        runs = list((reservation.get('runs') or {}).values())
        run = runs[0] if len(runs) == 1 else None
    if not isinstance(run, dict):
        return None, None
    wall, api = [], []
    for item in run.get('reservations') or []:
        telemetry = item.get('telemetry') or {}
        for source, sink in (('duration_ms', wall), ('duration_api_ms', api)):
            value = telemetry.get(source)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                sink.append(value)
    return (max(wall) if wall else None), (max(api) if api else None)


def collect_evidence(res, args):
    """Derive the H2254 evidence block. Every value is READ, never asserted."""
    meta = res.get('meta') or {}
    summary = res.get('summary') or {}
    manifest = _read_json(args.manifest)
    status = _read_json(args.status)
    reservation = _read_json(args.call_reservation)
    budgets = (manifest or {}).get('budgets') or {}
    run = None
    if isinstance(reservation, dict):
        runs = reservation.get('runs') or {}
        run = runs.get(str(args.run_id)) if args.run_id else (
            list(runs.values())[0] if len(runs) == 1 else None)
    usage = (run or {}).get('usage') or {}
    wall_ms, api_ms = _latencies(reservation, args.run_id)
    # The kill switch is not a single serialized flag: `budgets.kill_switch` is an INPUT to
    # `derive_agent_budget`, and what actually bounds a run is whether the derived per-lane
    # ceilings came out as numbers or as None (H2173 §2 row 10 -- "kill_switch=false => every
    # ceiling None => unbounded"). Record the observable consequence next to the declaration,
    # so a receipt claiming a bounded run can be checked rather than believed.
    kill_switch = {
        'declared': budgets.get('kill_switch'),
        'max_agents': budgets.get('max_agents'),
        'max_translate_agents': budgets.get('max_translate_agents'),
        'max_heal_agents': budgets.get('max_heal_agents'),
        'bounded': all(budgets.get(name) is not None
                       for name in ('max_translate_agents', 'max_heal_agents')) or None,
        'budget_stops': summary.get('budget_stops'),
    } if manifest is not None else None
    return {
        'commit': _repo_commit(),
        'manifest_sha256': (sha256_file(args.manifest) if args.manifest
                            and os.path.exists(args.manifest) else None),
        'manifest_path': _abs_or_none(args.manifest),
        'status_path': _abs_or_none(args.status),
        'call_reservation_path': _abs_or_none(args.call_reservation),
        'run_id': args.run_id,
        'calls_spent': (run or {}).get('calls_spent'),
        'max_calls': (run or {}).get('max_calls'),
        'observed_cost_usd': usage.get('observed_cost_usd'),
        'cost_evaluable': usage.get('cost_evaluable'),
        'unevaluable_calls': usage.get('unevaluable_calls'),
        'api_latency_ms': api_ms,
        'wall_latency_ms': wall_ms,
        'kill_switch': kill_switch,
        # What the spawn ACTUALLY did (H2251), read off the worker's own status file rather
        # than re-derived -- the manifest records the REQUEST and the two differ on a CLI that
        # cannot parse `--safe-mode`.
        'cli_safe_mode_effective': (status or {}).get('cli_safe_mode_effective'),
        'timeout_ceil_ms': budgets.get('timeout_ceil_ms'),
        'hard_timeout_ms': PRODUCTION_HARD_TIMEOUT_MS,
        'gen_model': meta.get('gen_model'),
    }


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def cmd_judge(args):
    res = _load_wf(args.wf_output)
    verdict, reasons, facts = judge_payload(res, expect_senses=args.expect_senses)
    meta = res.get('meta') or {}
    execution = meta.get('execution') or {}
    receipt = {
        'schema': RECEIPT_SCHEMA,
        'verdict': verdict,
        'judged_at_epoch': time.time(),
        'wf_output': os.path.abspath(args.wf_output),
        'wf_sha256': hashlib.sha256(open(args.wf_output, 'rb').read()).hexdigest(),
        'expect_senses': args.expect_senses,
        'profile_slot': execution.get('profile_slot'),
        # H2251: which SPAWN SHAPE this receipt is evidence about. A canary judged on one
        # spawn shape says nothing about a lane running the other, and until this field
        # existed a receipt could not distinguish the two -- which is what made "a GO
        # receipt produced on the safe-mode arm, not inherited from a baseline run"
        # unverifiable from the artifact itself. `None` means the manifest pinned nothing
        # and the lane default applied at judging time; it is NOT the same as `False`.
        'cli_safe_mode': execution.get('cli_safe_mode'),
        'reasons': reasons,
        'facts': facts,
    }
    # H2254: additive evidence block. Written unconditionally so a receipt's SHAPE never
    # depends on which optional flags the operator remembered -- an absent key and a null key
    # look identical to a reader, and only one of them proves the evidence was looked for.
    receipt['evidence'] = collect_evidence(res, args)
    if args.receipt:
        _atomic_write_json(args.receipt, receipt)
    print('CANARY %s%s' % (verdict, ' -> %s' % args.receipt if args.receipt else ''))
    for reason in reasons:
        print('  - %s' % reason)
    return 0 if verdict == 'GO' else 2


def load_receipt(path):
    with open(path, encoding='utf-8') as fh:
        receipt = json.load(fh)
    if receipt.get('schema') != RECEIPT_SCHEMA:
        raise ValueError('not a %s receipt: %s' % (RECEIPT_SCHEMA, path))
    return receipt


def enforce(receipt_path, max_age_seconds=DEFAULT_MAX_AGE_SECONDS, only_profile=None):
    """The --execute gate. Raises SystemExit with the refusal reason; returns the
    receipt on pass. Fail-closed: an unreadable receipt is a refusal, never a pass."""
    try:
        receipt = load_receipt(receipt_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit('canary gate: cannot read a GO receipt at %s (%s) — run '
                         '/pwg-live-gate step 2 then `canary_gate.py judge` (H2159)'
                         % (receipt_path, exc))
    if receipt.get('verdict') != 'GO':
        raise SystemExit('canary gate: receipt verdict is %r, not GO: %s'
                         % (receipt.get('verdict'), '; '.join(receipt.get('reasons') or [])))
    age = time.time() - float(receipt.get('judged_at_epoch') or 0)
    if age < 0 or age > max_age_seconds:
        raise SystemExit('canary gate: GO receipt is %.0f s old (max %d) — a paid window '
                         'needs a FRESH gate; re-run the canary (H2159)'
                         % (age, max_age_seconds))
    receipt_profile = receipt.get('profile_slot')
    if only_profile and receipt_profile and receipt_profile != only_profile:
        raise SystemExit('canary gate: receipt is for profile %r, this run is '
                         '--only-profile %r — gate the SAME profile you spend on'
                         % (receipt_profile, only_profile))
    return receipt


def cmd_check(args):
    try:
        enforce(args.receipt, max_age_seconds=args.max_age_seconds,
                only_profile=args.only_profile)
    except SystemExit as exc:
        print(str(exc))
        return 2
    print('canary gate: GO receipt valid')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    j = sub.add_parser('judge', help='derive GO/NO-GO from a canary wf_output')
    j.add_argument('wf_output')
    j.add_argument('--expect-senses', type=int, default=DEFAULT_EXPECT_SENSES)
    j.add_argument('--receipt', help='write the atomic receipt JSON here')
    # H2254: the durable inputs the evidence block reads. All optional -- `judge` still works
    # on a bare wf_output, it just records `null` for what it was not shown, which is the
    # honest answer and is distinguishable from a measured zero.
    j.add_argument('--manifest', help='sealed manifest the canary ran (hashed into the receipt)')
    j.add_argument('--status', help='worker --status-out file (effective spawn shape)')
    j.add_argument('--call-reservation', help='durable call-reservation ledger (calls + cost)')
    j.add_argument('--run-id', help='reservation run id, when the ledger holds several')
    c = sub.add_parser('check', help='validate a receipt the way --execute does')
    c.add_argument('receipt')
    c.add_argument('--max-age-seconds', type=int, default=DEFAULT_MAX_AGE_SECONDS)
    c.add_argument('--only-profile')
    args = ap.parse_args(argv)
    return {'judge': cmd_judge, 'check': cmd_check}[args.cmd](args)


if __name__ == '__main__':
    sys.exit(main())
