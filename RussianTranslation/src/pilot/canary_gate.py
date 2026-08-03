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

RECEIPT_SCHEMA = 'pwg.canary_gate_receipt.v1'
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
        blob = json.dumps(card, ensure_ascii=False)
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
        content_blob = json.dumps(card.get('records') or [], ensure_ascii=False)
        senses = sum(1 for rec in card.get('records') or []
                     for sense in rec.get('senses') or []
                     if (sense.get('russian') or '').strip())
        sense_counts.append((key, senses))
        if senses != expect_senses:
            reasons.append('%s: %d/%d senses with Russian content (canary SAN-LOSS '
                           'shortfall)' % (key, senses, expect_senses))
        hits = TN_RE.findall(blob)
        if hits:
            tn_hits.append((key, hits[:5]))
            reasons.append('%s: unresolved TNMASK placeholder(s): %s'
                           % (key, ', '.join(hits[:5])))
        for marker in LITERAL_MARKERS:
            if marker in content_blob:
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
        'reasons': reasons,
        'facts': facts,
    }
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
    c = sub.add_parser('check', help='validate a receipt the way --execute does')
    c.add_argument('receipt')
    c.add_argument('--max-age-seconds', type=int, default=DEFAULT_MAX_AGE_SECONDS)
    c.add_argument('--only-profile')
    args = ap.parse_args(argv)
    return {'judge': cmd_judge, 'check': cmd_check}[args.cmd](args)


if __name__ == '__main__':
    sys.exit(main())
