#!/usr/bin/env python3
"""H4527: the record-gated admission rule for a LIVE cohort width > 1.

H1437 Phase 3 hard-disabled live cohort execution against `COHORT_LIVE_GATE`: a width > 1
`--execute` was refused unconditionally because the three prerequisites (attempt/result/run
binding, promotion-receipt reconciliation, campaign reservation ledger) had never been proven
on a LIVE serial window and no reviewer had signed the barrier off. Phase 4 then measured
widths 1/2/3 byte-identical OFFLINE (clean/requeue decisions, accepted order, store bytes) --
the offline half of the argument is finished; the LIVE half is what is still missing.

This module is the deliberate, fail-closed flip H4527 asks for. It does NOT decide that the
gate is passed; it defines the ONE artifact that can say so, and refuses everything until that
artifact exists and validates:

    RussianTranslation/pwg_ru/h4527/COHORT_LIVE_ACCEPTANCE.json   (schema below)

Design rules (each one is a pin in `cohort_live_admission_selftest`):

1. **Fail closed everywhere.** Missing file, unreadable file, bad JSON, wrong schema, a
   missing/blank field, a non-PASS reviewer verdict, a record admitting fewer profiles than
   the requested width -> REFUSE. There is no "assume yes" branch and no environment variable
   override: the point is that a session cannot admit itself.
2. **Width 3+ is refused even by a perfect record.** `MAX_ADMITTED_WIDTH = 2` is a hard cap in
   code, not data. Slice-D's 18-wide and H317's 3-wide cascades (LAUNCH_FUCKUPS.md) are the
   standing counter-examples; width 3 gets its own rung, its own evidence and its own
   deliberate edit here.
3. **Both halves are required.** A live serial-acceptance window AND a reviewer sign-off.
   Either alone admits nothing -- that is exactly the pair the Phase 3 refusal message names.
4. **The record is evidence-bearing, not a flag.** Each half must carry at least one evidence
   pointer (run-id, packet path, blob link); a record that says `signed: true` with nothing to
   open is rejected as unfalsifiable.
5. **The acceptance window must have run through the cohort path** (`via_cohort_path`). Once
   rung 4 wired the live dispatch (`cohort_live_dispatch`), a width-1 window can be run either
   on the serial supervisor or on the cohort dispatch; only the latter is evidence about the
   code a width-2 wave will use. `bounded_staged_run --execute --cohort-path` at width 1 is
   the run that earns this field.

Read-only and side-effect-free: importing or calling this never writes, probes or spends.
"""
import json
import os
import sys

SCHEMA = 'pwg.cohort_live_acceptance.v1'

# The hard code-side cap. Data can only ever admit LESS than this, never more.
MAX_ADMITTED_WIDTH = 2

# Where the one acceptance record lives, relative to the repo's RussianTranslation root.
RECORD_RELPATH = os.path.join('pwg_ru', 'h4527', 'COHORT_LIVE_ACCEPTANCE.json')

_HERE = os.path.dirname(os.path.abspath(__file__))
# .../RussianTranslation/src/pilot -> .../RussianTranslation
_RT_ROOT = os.path.dirname(os.path.dirname(_HERE))


def record_path(rt_root=None):
    """Absolute path of the acceptance record (no existence check)."""
    return os.path.join(os.path.abspath(rt_root or _RT_ROOT), RECORD_RELPATH)


def _nonblank(value):
    return isinstance(value, str) and value.strip() != ''


def _evidence_list(block):
    items = block.get('evidence')
    if isinstance(items, str):
        items = [items]
    if not isinstance(items, list):
        return []
    return [x for x in items if _nonblank(x)]


def validate_record(record):
    """(ok, reason) for a loaded acceptance record. Pure; never touches the filesystem."""
    if not isinstance(record, dict):
        return False, 'acceptance record is not a JSON object'
    if record.get('schema') != SCHEMA:
        return False, ('acceptance record schema is %r, expected %r'
                       % (record.get('schema'), SCHEMA))

    serial = record.get('serial_acceptance')
    if not isinstance(serial, dict):
        return False, 'acceptance record has no `serial_acceptance` block'
    for field in ('run_id', 'window_id', 'profile', 'completed_utc'):
        if not _nonblank(serial.get(field)):
            return False, 'serial_acceptance.%s is missing or blank' % field
    if serial.get('byte_identical_to_serial') is not True:
        return False, ('serial_acceptance.byte_identical_to_serial is not true -- the live '
                       'window did not reproduce the serial route decisions/store bytes')
    if serial.get('via_cohort_path') is not True:
        # H4527 rung 4. A width-1 window on the SERIAL supervisor proves the route; it proves
        # nothing about the cohort dispatch a width-2 wave actually runs on. The acceptance
        # window must therefore have gone through the cohort path itself
        # (`bounded_staged_run --execute --cohort-path`, width 1) -- that is the only reading
        # of work item 1's "one bounded headless window THROUGH THE COHORT PATH at width 1"
        # under which the record licenses anything it has evidence for.
        return False, ('serial_acceptance.via_cohort_path is not true -- the acceptance '
                       'window did not run through the cohort dispatch, so it is evidence '
                       'about the serial supervisor, not about the wiring width 2 would use')
    if not _evidence_list(serial):
        return False, ('serial_acceptance.evidence is empty -- an acceptance claim with '
                       'nothing to open is not evidence')

    review = record.get('reviewer_sign_off')
    if not isinstance(review, dict):
        return False, 'acceptance record has no `reviewer_sign_off` block'
    for field in ('reviewer', 'session', 'dated'):
        if not _nonblank(review.get(field)):
            return False, 'reviewer_sign_off.%s is missing or blank' % field
    if str(review.get('verdict') or '').strip().upper() != 'PASS':
        return False, 'reviewer_sign_off.verdict is %r, not PASS' % (review.get('verdict'),)
    if not _evidence_list(review):
        return False, 'reviewer_sign_off.evidence is empty -- an unfalsifiable sign-off'

    width = record.get('max_admitted_width')
    if not isinstance(width, int) or isinstance(width, bool):
        return False, 'max_admitted_width is not an integer: %r' % (width,)
    if width < 1:
        return False, 'max_admitted_width must be >= 1: %r' % (width,)
    if width > MAX_ADMITTED_WIDTH:
        # A record asking for more than the code cap is a defect IN THE RECORD, and the whole
        # record is rejected rather than silently clamped: somebody meant something by it.
        return False, ('max_admitted_width %d exceeds the code cap %d -- width %d has its own '
                       'rung (evidence + a deliberate edit of MAX_ADMITTED_WIDTH); it is '
                       'never granted by data' % (width, MAX_ADMITTED_WIDTH, width))

    profiles = record.get('admitted_profiles')
    if not isinstance(profiles, list) or not profiles or not all(_nonblank(p) for p in profiles):
        return False, 'admitted_profiles must be a non-empty list of profile names'
    if len(set(profiles)) != len(profiles):
        return False, 'admitted_profiles contains duplicates: %r' % (profiles,)
    if len(profiles) < width:
        return False, ('admitted_profiles lists %d profile(s) but max_admitted_width is %d -- '
                       'a wave cannot be wider than its admitted fleet'
                       % (len(profiles), width))
    return True, 'acceptance record valid'


def load_record(path=None, rt_root=None):
    """(record_or_None, reason). Any read/parse failure is a refusal reason, never a raise."""
    path = path or record_path(rt_root)
    if not os.path.exists(path):
        return None, 'no acceptance record at %s' % path
    try:
        with open(path, encoding='utf-8') as handle:
            return json.load(handle), 'loaded %s' % path
    except (OSError, ValueError) as exc:
        return None, 'acceptance record at %s is unreadable: %s' % (path, exc)


def admit(width, path=None, rt_root=None):
    """(admitted, reason, record) for a requested LIVE cohort width.

    width <= 1 is the serial production route and is always admitted (it is what runs today).
    """
    try:
        width = int(width or 1)
    except (TypeError, ValueError):
        return False, 'cohort width %r is not an integer' % (width,), None
    if width <= 1:
        return True, 'serial route (width 1) -- no acceptance record required', None
    if width > MAX_ADMITTED_WIDTH:
        return False, ('cohort width %d exceeds the admitted maximum %d; width %d has its own '
                       'acceptance rung and is refused regardless of any record '
                       '(LAUNCH_FUCKUPS.md: Slice-D 18-wide, H317 3-wide)'
                       % (width, MAX_ADMITTED_WIDTH, width)), None
    record, reason = load_record(path=path, rt_root=rt_root)
    if record is None:
        return False, reason, None
    ok, why = validate_record(record)
    if not ok:
        return False, why, record
    if width > int(record['max_admitted_width']):
        return False, ('acceptance record admits width %d; %d was requested'
                       % (record['max_admitted_width'], width)), record
    return True, ('admitted by %s: serial window %s on %s, %s sign-off %s'
                  % (os.path.basename(path or record_path(rt_root)),
                     record['serial_acceptance']['run_id'],
                     record['serial_acceptance']['profile'],
                     record['reviewer_sign_off']['reviewer'],
                     record['reviewer_sign_off']['dated'])), record


def main(argv=None):
    """`python cohort_live_admission.py [--width N] [--record PATH]` -- print the verdict."""
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    argv = list(sys.argv[1:] if argv is None else argv)
    width, path = 2, None
    while argv:
        flag = argv.pop(0)
        if flag == '--width':
            width = int(argv.pop(0))
        elif flag == '--record':
            path = argv.pop(0)
        else:
            raise SystemExit('usage: cohort_live_admission.py [--width N] [--record PATH]')
    ok, reason, _ = admit(width, path=path)
    print(json.dumps({'schema': SCHEMA, 'requested_width': width,
                      'record_path': path or record_path(),
                      'admitted': ok, 'reason': reason}, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
