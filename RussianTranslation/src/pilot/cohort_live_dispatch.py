#!/usr/bin/env python3
"""H4527 rung 4 — the LIVE wiring between `bounded_staged_run --execute` and `cohort_engine`.

`cohort_live_admission` (rung 1) decides *whether* a live cohort width > 1 may run. This
module is the other half the Phase 3 refusal named: *how* a live wave is actually dispatched
so that an admitted width is a real wave and not a serial window wearing a width label.

Three gaps stood between the proven engine and the live route, and this module closes each
with one small, separately pinned piece:

1. **Per-profile window binding.** `CohortEngine` enforces one in-flight job per profile, an
   invariant that is meaningless unless each window names its profile. Plan-scoped windows
   never carried one (`bounded_staged_run.scope_windows` builds them from lease ids), so the
   engine would have treated every window as not-in-fleet and quietly dispatched nothing.
   `assign_profiles` binds them deterministically, in plan order, round-robin over the
   *probed-healthy* fleet.
2. **A fleet precondition.** A width the live fleet cannot fill is a lie, not a wave:
   `fleet_guard` refuses width N unless N distinct admitted profiles are actually there. On
   the roster as it stands (one validated slot, `c1`) this is what refuses width 2 — before
   any call is spent, and with the real reason rather than a mysterious half-empty wave.
3. **One promote + one TM per wave.** The serial route promotes inside `run_window`, once per
   lease. A wave must promote once, for the whole accepted set, through the same coordinator
   entry point — `promote-ready --lease-id` is repeatable and lands the bundle in ONE store
   transaction (`promote_final_cards.batch_promote`), so the wave promoter is exactly that
   one call. Windows dispatched through here therefore carry `wave_promote` and the per-lease
   promote in `run_window` stands down.

**Deliberately NOT in here:** any second dispatch engine (banned by the H1437 Grok review),
any change to call shape (one card per call, H4054), and any ceiling the cohort path cannot
honour. `CohortEngine` bounds a run by `max_calls` alone; `BoundedSupervisor`'s cost / clean /
window / empty-streak ceilings have no cohort equivalent, so `unsupported_ceilings` names them
and the caller REFUSES rather than running a bounded-looking window with the bound removed.

Pure control plane: every live effect (the window runner, the audit, the promote subprocess)
is injected. Importing or calling anything here spends nothing by itself.
"""
import os
import sys

SCHEMA = 'pwg.cohort_live_dispatch.v1'

# Ceilings BoundedSupervisor enforces that CohortEngine has no equivalent for. Silently
# dropping one of these would turn a bounded run into an unbounded one wearing the flag.
SUPERVISOR_ONLY_CEILINGS = ('cost_ceiling', 'max_clean', 'max_windows', 'empty_streak')


def assign_profiles(windows, profiles):
    """Bind every window to a profile, round-robin in plan order. Returns NEW dicts.

    Deterministic on purpose: the same plan and the same admitted fleet must produce the same
    binding on a resume, or a resumed wave would re-bind leases to different profiles and the
    engine's per-profile exclusion would be meaningless across lives. A window that already
    carries a profile keeps it (an explicit binding always wins over the round robin).
    """
    fleet = [p for p in (profiles or []) if isinstance(p, str) and p.strip()]
    if not fleet:
        raise ValueError('assign_profiles needs at least one profile to bind windows to')
    out, cursor = [], 0
    for window in (windows or []):
        w = dict(window)
        if not w.get('profile'):
            w['profile'] = fleet[cursor % len(fleet)]
            cursor += 1
        out.append(w)
    return out


def fleet_guard(width, healthy_profiles):
    """(ok, reason) — may a wave of `width` run on this admitted fleet?

    Refuses rather than shrinking the width: a caller that asked for 2 and silently got 1 has
    been told a wave ran when a serial window did, which is the exact confusion rung 2 exists
    to prevent.
    """
    try:
        width = int(width or 1)
    except (TypeError, ValueError):
        return False, 'cohort width %r is not an integer' % (width,)
    fleet = sorted({p for p in (healthy_profiles or []) if isinstance(p, str) and p.strip()})
    if width < 1:
        return False, 'cohort width must be >= 1: %r' % (width,)
    if not fleet:
        return False, ('no probed-healthy profile in the admitted fleet — a live cohort wave '
                       'needs at least one')
    if len(fleet) < width:
        return False, ('cohort width %d needs %d distinct probed-healthy profiles; the '
                       'admitted fleet has %d (%s). Widen the fleet (a human roster act) or '
                       'run width %d.' % (width, width, len(fleet), ', '.join(fleet), len(fleet)))
    return True, 'fleet admits width %d: %s' % (width, ', '.join(fleet))


def unsupported_ceilings(ceilings):
    """Names of supervisor-only ceilings that are SET and would be dropped on the cohort path."""
    ceilings = ceilings or {}
    return [name for name in SUPERVISOR_ONLY_CEILINGS
            if ceilings.get(name) not in (None, 0, False)]


def make_wave_promoter(promote_leases, gen_model_version):
    """Return promote_wave(clean_members) -> receipt: ONE promote for the whole accepted wave.

    `promote_leases(lease_ids, gen_model_version)` is the injected coordinator call (one
    `promote-ready` invocation carrying every lease id; the coordinator promotes the bundle in
    a single store transaction). The receipt is what `CohortEngine` persists as the wave's
    promotion record and hands to `rebuild_tm`, so it must be JSON-serialisable and must name
    the leases actually promoted — a receipt that cannot be opened is not evidence.
    """
    def promote_wave(clean_members):
        lease_ids = [m['id'] for m in (clean_members or [])]
        result = promote_leases(lease_ids, gen_model_version) or {}
        receipt = {
            'schema': SCHEMA,
            'members': lease_ids,
            'lease_ids': lease_ids,
            'gen_model_version': gen_model_version,
            'promoted': True,
        }
        for key in ('returncode', 'stdout_tail', 'promoted_at'):
            if key in result:
                receipt[key] = result[key]
        return receipt
    return promote_wave


def run_cohort_live(windows, width, run_window, checkpoint_path, audit=None,
                    promote_wave=None, rebuild_tm=None, admitted=None, parked=None,
                    max_calls=None, coord_dir=None, resume=False):
    """Dispatch LIVE bounded windows through the landed `CohortEngine` and return its summary.

    The caller owns every gate that must precede this (admission record, canary receipt, fleet
    probe, ceiling check); this function owns only the invariant the engine itself cannot
    check: every window carries a profile binding. A profile-less window is refused loudly —
    `CohortEngine` reads a `None` profile as not-in-fleet and would settle the wave having
    quietly dispatched nothing, which on a paid lane reads as "the window ran and found no
    work".
    """
    import cohort_engine as ce
    windows = [dict(w) for w in (windows or [])]
    missing = [w.get('id') or ('#%d' % i) for i, w in enumerate(windows) if not w.get('profile')]
    if missing:
        raise SystemExit('cohort_live_dispatch: every live cohort window needs a profile '
                         'binding (assign_profiles); missing on: %s' % ', '.join(missing))
    ok, why = fleet_guard(width, admitted or {w['profile'] for w in windows})
    if not ok:
        raise SystemExit('cohort_live_dispatch: %s' % why)
    engine = ce.CohortEngine(
        windows, run_window, checkpoint_path, audit=audit, promote_wave=promote_wave,
        rebuild_tm=rebuild_tm, width=width, admitted=admitted, parked=parked,
        max_calls=max_calls, coord_dir=coord_dir, resume=resume)
    return engine.run()


def main(argv=None):
    """`python cohort_live_dispatch.py --width N --fleet c1,c2` — print the fleet verdict."""
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    import json
    argv = list(sys.argv[1:] if argv is None else argv)
    width, fleet = 2, []
    while argv:
        flag = argv.pop(0)
        if flag == '--width':
            width = int(argv.pop(0))
        elif flag == '--fleet':
            fleet = [p.strip() for p in argv.pop(0).split(',') if p.strip()]
        else:
            raise SystemExit('usage: cohort_live_dispatch.py --width N --fleet c1,c2')
    ok, why = fleet_guard(width, fleet)
    print(json.dumps({'schema': SCHEMA, 'requested_width': width, 'fleet': fleet,
                      'ok': ok, 'reason': why}, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
