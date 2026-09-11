#!/usr/bin/env python3
"""Telemetry-driven dispatch-width policy for the generated PWG-RU/EN harness.

Single owner of ``MAX_WIDE`` / ``STAGGER_MS`` and of the rule that moves them.

Before this module the two numbers were free-standing constants in
``gen_opt_harness2.py`` and the per-window telemetry the harness already
returns (``kill_timeouts``, ``conn_errors``, ``null_keys``, non-null yield) was
read by *no policy at all* (H1403 audit ledger #4).  Width was therefore static:
a degraded transport kept being hit at the same width until a human noticed, and
a healthy transport never earned its width back.

Two measured facts are baked in and must not be re-litigated by a caller:

* **A5 / H1283** — <=3-wide lifted non-null yield 10 % -> 78 % on a degraded
  transport.  ``DEFAULT_MAX_WIDE = 3`` is a *yield protector*, not a naive cap,
  and is also the automatic ceiling: :func:`decide_width` narrows freely but
  never widens past ``ceiling`` (default 3).  Going above 3 is a deliberate,
  separately budgeted *calibration* act (:func:`calibration_bracket`), never an
  adaptive one — the Slice-D / H317 / H255 cascades were all unconditional
  width raises.
* **H255 w07** — a single isolated schema probe completing in ~54 s said nothing
  about the same window at ~10-wide (32/36 kill-timeouts).  A warm-up is only
  evidence for the width it was actually run at, which is why
  :func:`probe_plan` asks for width-representative concurrency and
  :func:`probe_gate_verdict` refuses an isolated probe as a GO for a wide
  window.

Everything here is pure: no I/O, no clock, no network.  The generator imports
the defaults, the runtime telemetry is fed back in as plain dicts, and the whole
policy is exercised offline by :func:`selftest`.
"""

import math
import sys
from dataclasses import asdict, dataclass, field

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# --- pinned defaults (the harness imports these; it no longer owns them) -----
DEFAULT_MAX_WIDE = 3        # A5/H1283 measured yield protector, also the adaptive ceiling
DEFAULT_STAGGER_MS = 2000   # H255/H811 thundering-herd guard between the first MAX_WIDE starts
MIN_MAX_WIDE = 1            # narrowing floor: serial, never 0 (0 means "unbounded", see below)
CALIBRATION_CEILING = 8     # H1403 A7 width arm brackets 4..8 — offline/scratch keys only

# --- what counts as degraded / healthy --------------------------------------
DEGRADED_YIELD = 0.75       # below this non-null share the window is degraded evidence
HEALTHY_YIELD = 0.95        # at/above this (with zero kill-timeouts and zero conn errors) healthy
HEALTHY_WINDOWS_TO_WIDEN = 2   # consecutive measured-healthy windows required before +1 width
MIN_HEALTHY_KEYS = 3        # a 1-2 key window is not load-representative evidence of health
STAGGER_DEGRADED_FACTOR = 2     # degraded => spread the first starts further apart
MAX_STAGGER_MS = 8000       # beyond this the stagger dominates the window's wall-clock


@dataclass(frozen=True)
class WindowTelemetry:
    """One window's post-run signals, as the generated harness already returns them."""

    keys_total: int = 0
    null_keys: int = 0
    kill_timeouts: int = 0
    conn_errors: int = 0
    max_wide: int = 0           # the width this window actually ran at (0 = unbounded)
    label: str = ''

    @classmethod
    def from_window(cls, row):
        """Build from a harness result dict (``null_keys`` may be a list of keys)."""
        row = dict(row or {})
        meta = dict(row.get('meta') or {})
        nulls = row.get('null_keys', meta.get('null_keys'))
        if isinstance(nulls, (list, tuple, set)):
            null_keys = len(nulls)
        else:
            null_keys = int(nulls or 0)
        keys_total = row.get('keys_total', meta.get('keys_total'))
        if keys_total is None:
            selected = row.get('selected_keys', meta.get('selected_keys')) or []
            keys_total = len(selected) if selected else null_keys
        return cls(
            keys_total=int(keys_total or 0),
            null_keys=null_keys,
            kill_timeouts=int(row.get('kill_timeouts', meta.get('kill_timeouts')) or 0),
            conn_errors=int(row.get('conn_errors', meta.get('conn_errors')) or 0),
            max_wide=int(row.get('max_wide', meta.get('max_wide')) or 0),
            label=str(row.get('label', meta.get('window')) or ''),
        )

    @property
    def nonnull_yield(self):
        if self.keys_total <= 0:
            return 0.0
        return max(0.0, (self.keys_total - self.null_keys)) / float(self.keys_total)

    def classify(self, current_width=DEFAULT_MAX_WIDE):
        """``'degraded'`` | ``'healthy'`` | ``'inconclusive'``.

        Health is only claimed for a window that was *load-representative*: it
        ran at least as wide as the width we are being asked to keep or exceed,
        and carried enough keys to mean anything (H255 w07 — the isolated
        54 s probe that "proved" a width it never ran at).
        """
        if self.keys_total <= 0:
            return 'inconclusive'
        if self.kill_timeouts > 0 or self.conn_errors > 0:
            return 'degraded'
        if self.nonnull_yield < DEGRADED_YIELD:
            return 'degraded'
        representative = (self.max_wide == 0 or self.max_wide >= max(1, current_width))
        if (self.nonnull_yield >= HEALTHY_YIELD
                and self.keys_total >= MIN_HEALTHY_KEYS
                and representative):
            return 'healthy'
        return 'inconclusive'


@dataclass(frozen=True)
class WidthDecision:
    max_wide: int
    stagger_ms: int
    action: str          # bootstrap | narrow | hold | widen
    reason: str
    healthy_streak: int = 0
    evidence: tuple = field(default_factory=tuple)

    def meta(self):
        d = asdict(self)
        d['evidence'] = list(self.evidence)
        return d


def stagger_for(max_wide, base_stagger_ms=DEFAULT_STAGGER_MS, degraded=False):
    """Stagger that keeps the first ``max_wide`` starts apart without dominating."""
    if max_wide <= 1:
        return 0 if not degraded else base_stagger_ms
    ms = base_stagger_ms * (STAGGER_DEGRADED_FACTOR if degraded else 1)
    return int(min(MAX_STAGGER_MS, ms))


def decide_width(history,
                 *,
                 current_max_wide=DEFAULT_MAX_WIDE,
                 base_stagger_ms=DEFAULT_STAGGER_MS,
                 ceiling=DEFAULT_MAX_WIDE,
                 floor=MIN_MAX_WIDE):
    """Return the width/stagger to run the NEXT window at.

    ``history`` is oldest-first; only the tail matters.  Rules, in order:

    1. No telemetry at all -> ``bootstrap``: keep the pinned default.
    2. Most recent window degraded -> ``narrow``: halve toward ``floor`` and
       widen the stagger.  One degraded window is enough; the H255 w07 cost of
       staying wide on a degraded transport is a whole window of nulls.
    3. ``HEALTHY_WINDOWS_TO_WIDEN`` consecutive *measured-healthy,
       load-representative* windows -> ``widen`` by exactly one, never past
       ``ceiling`` (default = the A5-pinned 3).
    4. Anything else -> ``hold``.

    ``current_max_wide == 0`` (explicitly unbounded) is honoured as a human
    decision on the way down only: a degraded window still narrows it to the
    ceiling, but the policy never re-enters unbounded dispatch by itself.
    """
    if ceiling < floor:
        raise ValueError('ceiling must be >= floor')
    rows = [t if isinstance(t, WindowTelemetry) else WindowTelemetry.from_window(t)
            for t in (history or [])]
    effective_current = ceiling if current_max_wide == 0 else int(current_max_wide)
    if not rows:
        return WidthDecision(
            max_wide=current_max_wide if current_max_wide else ceiling,
            stagger_ms=base_stagger_ms,
            action='bootstrap',
            reason='no window telemetry yet; keeping the A5/H1283 pinned default',
        )

    last = rows[-1]
    if last.classify(effective_current) == 'degraded':
        narrowed = max(floor, int(math.floor(effective_current / 2.0)) or floor)
        return WidthDecision(
            max_wide=narrowed,
            stagger_ms=stagger_for(narrowed, base_stagger_ms, degraded=True),
            action='narrow',
            reason=('degraded transport: kill_timeouts=%d conn_errors=%d non-null %.0f%% '
                    '-> %d-wide' % (last.kill_timeouts, last.conn_errors,
                                    100 * last.nonnull_yield, narrowed)),
            evidence=(last.label or 'last-window',),
        )

    streak, labels = 0, []
    for t in reversed(rows):
        if t.classify(effective_current) == 'healthy':
            streak += 1
            labels.append(t.label or 'window-%d' % streak)
        else:
            break

    if streak >= HEALTHY_WINDOWS_TO_WIDEN and effective_current < ceiling:
        widened = min(ceiling, effective_current + 1)
        return WidthDecision(
            max_wide=widened,
            stagger_ms=stagger_for(widened, base_stagger_ms),
            action='widen',
            reason=('%d consecutive measured-healthy load-representative windows '
                    '-> %d-wide (ceiling %d)' % (streak, widened, ceiling)),
            healthy_streak=streak,
            evidence=tuple(reversed(labels)),
        )

    return WidthDecision(
        max_wide=effective_current,
        stagger_ms=stagger_for(effective_current, base_stagger_ms),
        action='hold',
        reason=('healthy streak %d < %d required, or already at ceiling %d'
                % (streak, HEALTHY_WINDOWS_TO_WIDEN, ceiling)),
        healthy_streak=streak,
        evidence=tuple(reversed(labels)),
    )


# --- load-representative warm-up gate (H255 w07) -----------------------------

def probe_plan(max_wide, *, min_probes=2):
    """How the pre-window warm-up must be fired to be evidence for ``max_wide``.

    A single isolated call measures the *isolated* latency of one card, which
    H255 w07 showed is not the latency the same card sees inside the window.
    """
    width = CALIBRATION_CEILING if max_wide == 0 else max(1, int(max_wide))
    concurrency = width if width > 1 else 1
    return {
        'max_wide': max_wide,
        'concurrency': concurrency,
        'min_probes': max(min_probes if width > 1 else 1, concurrency),
        'rationale': ('H255 w07: an isolated probe is evidence only for 1-wide; fire %d '
                      'concurrent schema probes to represent a %s window'
                      % (concurrency, '%d-wide' % width if max_wide else 'unbounded')),
    }


def probe_gate_verdict(receipt, max_wide):
    """``('GO'|'NO-GO', reason)`` for a warm-up receipt against the planned width.

    ``receipt`` carries ``concurrency`` (how many probes were actually in
    flight together) and optionally ``ok`` / ``schema_valid``.
    """
    plan = probe_plan(max_wide)
    r = dict(receipt or {})
    got = int(r.get('concurrency', r.get('probes_concurrent', 1)) or 1)
    if r.get('ok') is False or r.get('schema_valid') is False:
        return 'NO-GO', 'warm-up probe failed its schema/ok check'
    if got < plan['concurrency']:
        return 'NO-GO', ('warm-up ran %d-concurrent probes but the window is planned at %s '
                         '— an isolated probe is not evidence for a wide window (H255 w07)'
                         % (got, '%d-wide' % max_wide if max_wide else 'unbounded'))
    return 'GO', 'warm-up was load-representative (%d concurrent probes)' % got


# --- calibration bracket (H1403 A7 width arm) --------------------------------

def calibration_bracket(*, healthy=False, low=4, high=CALIBRATION_CEILING):
    """Width values for the calibration arm, or [] when the transport is not healthy.

    The arm is a *measurement*, not a policy move: it only ever runs on scratch
    keys, sequentially, with a cache cooldown between arms, and only when the
    caller can show measured-healthy telemetry.  On anything else it returns an
    empty bracket, so a degraded day cannot buy a width raise.
    """
    if not healthy:
        return []
    low = max(MIN_MAX_WIDE, int(low))
    high = min(CALIBRATION_CEILING, int(high))
    return [w for w in range(low, high + 1) if w >= low] if high >= low else []


def healthy_for_calibration(history, *, current_max_wide=DEFAULT_MAX_WIDE):
    """True only when the tail of ``history`` is an unbroken measured-healthy run."""
    rows = [t if isinstance(t, WindowTelemetry) else WindowTelemetry.from_window(t)
            for t in (history or [])]
    if len(rows) < HEALTHY_WINDOWS_TO_WIDEN:
        return False
    tail = rows[-HEALTHY_WINDOWS_TO_WIDEN:]
    return all(t.classify(current_max_wide) == 'healthy' for t in tail)


def policy_meta(decision, max_wide=None):
    """The manifest block: what the policy decided and what warm-up it now demands."""
    width = decision.max_wide if decision is not None else max_wide
    return {
        'module': 'width_policy',
        'default_max_wide': DEFAULT_MAX_WIDE,
        'default_stagger_ms': DEFAULT_STAGGER_MS,
        'adaptive_ceiling': DEFAULT_MAX_WIDE,
        'calibration_ceiling': CALIBRATION_CEILING,
        'decision': decision.meta() if decision is not None else None,
        'probe_plan': probe_plan(width if width is not None else DEFAULT_MAX_WIDE),
    }


def _degraded_h255_w07():
    """The H255 w07 degraded-transport fixture: 36 keys, 32 kill-timeouts at ~10-wide."""
    return WindowTelemetry(keys_total=36, null_keys=31, kill_timeouts=32, conn_errors=0,
                           max_wide=0, label='H255_w07')


def _healthy_window(label, keys=12, wide=3):
    return WindowTelemetry(keys_total=keys, null_keys=0, kill_timeouts=0, conn_errors=0,
                           max_wide=wide, label=label)


def selftest():
    # 1. No telemetry: the pinned A5 default stands.
    boot = decide_width([])
    assert boot.action == 'bootstrap' and boot.max_wide == DEFAULT_MAX_WIDE, boot

    # 2. H255 w07 degraded fixture narrows immediately and widens the stagger.
    deg = decide_width([_degraded_h255_w07()], current_max_wide=3)
    assert deg.action == 'narrow' and deg.max_wide == 1, deg
    assert deg.stagger_ms >= DEFAULT_STAGGER_MS, deg

    # 3. One conn error alone is degraded evidence even at a perfect yield.
    flaky = WindowTelemetry(keys_total=12, null_keys=0, conn_errors=1, max_wide=3, label='flaky')
    assert flaky.classify(3) == 'degraded'
    assert decide_width([flaky], current_max_wide=3).action == 'narrow'

    # 4. Width NEVER rises without measured-healthy consecutive windows.
    one_good = decide_width([_healthy_window('w1', wide=2)], current_max_wide=2)
    assert one_good.action == 'hold' and one_good.max_wide == 2, one_good
    two_good = decide_width([_healthy_window('w1', wide=2), _healthy_window('w2', wide=2)],
                            current_max_wide=2)
    assert two_good.action == 'widen' and two_good.max_wide == 3, two_good

    # 5. The adaptive ceiling is the A5 default — healthy telemetry cannot cascade past it.
    many = [_healthy_window('w%d' % i, wide=3) for i in range(6)]
    capped = decide_width(many, current_max_wide=3)
    assert capped.max_wide == DEFAULT_MAX_WIDE and capped.action == 'hold', capped

    # 6. A thin or non-representative window is not evidence of health.
    thin = WindowTelemetry(keys_total=2, null_keys=0, max_wide=3, label='thin')
    assert thin.classify(3) == 'inconclusive'
    narrow_run = WindowTelemetry(keys_total=12, null_keys=0, max_wide=1, label='ran-1-wide')
    assert narrow_run.classify(3) == 'inconclusive', 'a 1-wide window cannot vouch for 3-wide'
    assert decide_width([narrow_run, narrow_run], current_max_wide=3).action == 'hold'

    # 7. Unbounded dispatch is never re-entered by the policy, but does narrow.
    unb = decide_width([_degraded_h255_w07()], current_max_wide=0)
    assert unb.max_wide == 1, unb
    held = decide_width([_healthy_window('a'), _healthy_window('b')], current_max_wide=0)
    assert held.max_wide != 0 and held.max_wide <= DEFAULT_MAX_WIDE, held

    # 8. Harness-shaped dict parsing (null_keys as a list of keys).
    row = {'keys_total': 4, 'null_keys': ['k1', 'k2'], 'kill_timeouts': 0,
           'conn_errors': 0, 'max_wide': 3}
    t = WindowTelemetry.from_window(row)
    assert t.null_keys == 2 and abs(t.nonnull_yield - 0.5) < 1e-9
    assert t.classify(3) == 'degraded'

    # 9. Load-representative warm-up gate (H255 w07: the isolated 54 s GO).
    assert probe_plan(3)['concurrency'] == 3
    assert probe_gate_verdict({'concurrency': 1}, 3)[0] == 'NO-GO'
    assert probe_gate_verdict({'concurrency': 3}, 3)[0] == 'GO'
    assert probe_gate_verdict({'concurrency': 1}, 1)[0] == 'GO'
    assert probe_gate_verdict({'concurrency': 8, 'ok': False}, 3)[0] == 'NO-GO'

    # 10. The calibration bracket exists only on healthy evidence and stops at 8.
    assert calibration_bracket(healthy=False) == []
    assert calibration_bracket(healthy=True) == [4, 5, 6, 7, 8]
    assert calibration_bracket(healthy=True, high=99) == [4, 5, 6, 7, 8]
    assert not healthy_for_calibration([_degraded_h255_w07(), _healthy_window('a')])
    assert healthy_for_calibration([_healthy_window('a'), _healthy_window('b')])

    # 11. The manifest block is JSON-shaped and carries the probe demand.
    meta = policy_meta(two_good)
    assert meta['decision']['action'] == 'widen'
    assert meta['probe_plan']['concurrency'] == 3
    assert meta['adaptive_ceiling'] == DEFAULT_MAX_WIDE

    print('width_policy selftest OK')


if __name__ == '__main__':
    selftest()
