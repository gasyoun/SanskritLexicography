#!/usr/bin/env python3
"""Pure agent-budget planning for the generated PWG Workflow runtime.

The production harness has two materially different call lanes:

* ``translate`` — whole-card batches and their binary-split retries;
* ``heal`` — fragment recovery, including cards routed directly to presplit.

Before this module existed both lanes spent one ``MAX_AGENTS`` counter.  On an
all-heal window the shared ceiling necessarily fired before the sum of the
per-card heal ceilings, making the per-card guard unreachable.  Keeping the
plan pure makes that invariant executable without launching the external
Workflow runtime.
"""

import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class AgentBudgetPlan:
    """Derived call ceilings for one generated Workflow window."""

    translate_expected: int
    heal_groups: int
    heal_cards: int
    max_translate_agents: int | None
    max_heal_agents: int | None
    max_agents: int | None
    strategy: str

    def meta(self):
        return asdict(self)


def _scaled(expected, factor, headroom):
    if expected <= 0:
        return 0
    return int(math.ceil(expected * factor)) + headroom


def _per_card_heal_cap(groups, factor, headroom):
    if groups <= 0:
        return 0
    return int(math.ceil(groups * factor)) + headroom


def _allocate_total(total, translate_default, heal_default):
    """Allocate an explicit legacy ``--max-agents`` ceiling across both pools.

    The override remains a hard *combined* ceiling.  Defaults are used only as
    weights; translate gets the odd/last slot because primary work must be able
    to reach recovery rather than being pre-empted by recovery already in
    flight.  A ceiling below the number of active pools necessarily leaves one
    pool disabled, which is honest and deterministic.
    """
    if total < 0:
        raise ValueError('max_agents_override must be >= 0')
    if not translate_default:
        return 0, total
    if not heal_default:
        return total, 0
    if total == 0:
        return 0, 0
    if total == 1:
        return 1, 0
    combined = translate_default + heal_default
    translate = max(1, int(round(total * translate_default / combined)))
    translate = min(total - 1, translate)
    return translate, total - translate


def derive_agent_budget(
        batch_count,
        heal_groups_by_key,
        *,
        enabled=True,
        translate_factor=3.0,
        translate_headroom=10,
        per_card_heal_budget=True,
        per_card_heal_factor=1.5,
        per_card_heal_headroom=3,
        max_agents_override=None):
    """Return independent translate/heal ceilings for one window.

    With per-card heal budgeting enabled, the window heal ceiling is exactly
    the sum of every card's ceiling.  Therefore the window pool cannot fire
    before a card-level ceiling merely because several cards recover at once.
    With per-card budgeting disabled, a conservative scaled group count keeps
    a finite global recovery backstop.
    """
    if batch_count < 0:
        raise ValueError('batch_count must be >= 0')
    raw_groups = {str(k): int(v) for k, v in dict(heal_groups_by_key or {}).items()}
    if any(v < 0 for v in raw_groups.values()):
        raise ValueError('heal group counts must be >= 0')
    groups = {k: v for k, v in raw_groups.items() if v > 0}
    if not enabled:
        return AgentBudgetPlan(
            translate_expected=batch_count,
            heal_groups=sum(groups.values()),
            heal_cards=len(groups),
            max_translate_agents=None,
            max_heal_agents=None,
            max_agents=None,
            strategy='disabled',
        )

    translate_default = _scaled(batch_count, translate_factor, translate_headroom)
    if per_card_heal_budget:
        heal_default = sum(
            _per_card_heal_cap(n, per_card_heal_factor, per_card_heal_headroom)
            for n in groups.values())
    else:
        heal_default = _scaled(sum(groups.values()), translate_factor, translate_headroom)

    if max_agents_override is None:
        max_translate, max_heal = translate_default, heal_default
        strategy = 'split-pools-per-card-heal'
    else:
        max_translate, max_heal = _allocate_total(
            int(max_agents_override), translate_default, heal_default)
        strategy = 'split-pools-total-override'

    return AgentBudgetPlan(
        translate_expected=batch_count,
        heal_groups=sum(groups.values()),
        heal_cards=len(groups),
        max_translate_agents=max_translate,
        max_heal_agents=max_heal,
        max_agents=max_translate + max_heal,
        strategy=strategy,
    )


def refuse_starvation_override(key_count, max_agents_override, *, force=False, where='generation'):
    """H1610/H1618/H4529: refuse a ``--max-agents N`` that is really a width wish.

    ``--max-agents`` is a TOTAL spawn ceiling across both pools, not a concurrency
    width. On a multi-key window an override below the key count cannot finish the
    window at all: the first keys spend the ceiling, the rest come back null and
    stamped ``selfheal-nothing-resolved`` with ``budget_stops >> 0`` — the ledger
    entry ``C2_M50_W1_MAX_AGENTS1_2026-07-24``, where ``--max-agents 1`` on a
    50-card window produced only-b0 work and nothing else.

    ``headless_worker.refuse_starvation_max_agents`` enforces the same invariant at
    the paid boundary; this one fires one step earlier, at manifest generation, so
    the footgun is caught before a harness is even written. Concurrency is
    ``--max-wide`` (``width_policy``), which is a different knob entirely.

    Returns a warning string when ``force`` lets a genuinely intended override
    through (the caller prints it loudly), else ``None``.
    """
    if max_agents_override is None:
        return None
    n = int(key_count or 0)
    override = int(max_agents_override)
    if n <= 1 or override >= n:
        return None
    msg = ('--max-agents=%d on a %d-key window is a TOTAL spawn ceiling, not a width: '
           '%d key(s) cannot be reached at all and come back null with budget_stops>0 '
           '(ledger C2_M50_W1_MAX_AGENTS1_2026-07-24). Use --max-wide=N for concurrency, '
           'or omit --max-agents and let the derived translate/heal pools apply.'
           % (override, n, n - override))
    if force:
        return ('WARNING (%s, --force-max-agents): %s' % (where, msg))
    raise ValueError('%s refused: %s Pass --force-max-agents if this is a deliberate '
                     'single-spawn canary.' % (where, msg))


def selftest():
    plan = derive_agent_budget(8, {'a': 2, 'b': 5})
    assert plan.max_translate_agents == 34
    assert plan.max_heal_agents == 6 + 11
    assert plan.max_agents == 51
    assert plan.max_heal_agents == sum(
        _per_card_heal_cap(n, 1.5, 3) for n in (2, 5))

    overridden = derive_agent_budget(8, {'a': 2, 'b': 5}, max_agents_override=20)
    assert overridden.max_agents == 20
    assert overridden.max_translate_agents > 0
    assert overridden.max_heal_agents > 0

    disabled = derive_agent_budget(8, {'a': 2}, enabled=False)
    assert disabled.max_agents is None
    assert disabled.strategy == 'disabled'

    test_h437_all_heal_window_reaches_every_per_card_cap()
    test_c2_m50_w1_max_agents1_starvation_refused()
    print('agent_budget selftest OK')


def test_h437_all_heal_window_reaches_every_per_card_cap():
    """H437 shape: EVERY card heals, and every card still gets its own full ceiling.

    Before the pool split the window spent ONE counter, so on the measured
    H437 w1b window (12 dense band-4 cards, 61/61 agents, 1 clean card,
    ~2 M tokens) three or four cards exhausted the shared ceiling between them
    and the remaining ~9 were nulled ``budget-kill-switch`` UN-ATTEMPTED — the
    per-card cap H442 added could never bind, because the window cap fired
    first. The invariant this pins is structural, not a tuning: the heal pool
    is exactly the SUM of the per-card ceilings, so the sum cannot be smaller
    than any subset of them, whatever the translate lane is doing.
    """
    groups = {'k%02d' % i: 12 for i in range(12)}          # 12 cards, 12 heal groups each
    plan = derive_agent_budget(12, groups)

    per_card = _per_card_heal_cap(12, 1.5, 3)              # ceil(12*1.5)+3 = 21
    assert per_card == 21, per_card
    assert plan.heal_cards == 12 and plan.heal_groups == 144

    # 1. The window heal ceiling is the exact sum of the card ceilings.
    assert plan.max_heal_agents == 12 * per_card == 252, plan.max_heal_agents

    # 2. Therefore the LAST card to heal still has its whole ceiling available
    #    after the other eleven have each spent theirs in full — the pre-split
    #    shared counter (61 agents for the same window) made this impossible.
    spent_by_others = 11 * per_card
    assert plan.max_heal_agents - spent_by_others == per_card

    # 3. And recovery cannot be starved by translation: the pools are disjoint,
    #    so a translate runaway spends its own ceiling, not the heal one.
    assert plan.max_translate_agents == _scaled(12, 3.0, 10) == 46
    assert plan.max_agents == plan.max_translate_agents + plan.max_heal_agents
    assert plan.strategy == 'split-pools-per-card-heal'

    # 4. Disabling the per-card budget is the only way back to the H437 shape:
    #    the flat backstop is a single window-wide pool with no card-level
    #    ceiling under it, so ONE dense card may legally spend all 442 calls
    #    and null the other eleven. Bigger number, worse guarantee.
    flat = derive_agent_budget(12, groups, per_card_heal_budget=False)
    assert flat.max_heal_agents == _scaled(144, 3.0, 10) == 442, flat.max_heal_agents
    assert flat.max_heal_agents > per_card * 12, 'the flat pool cannot bound any single card'


def test_c2_m50_w1_max_agents1_starvation_refused():
    """Ledger C2_M50_W1_MAX_AGENTS1_2026-07-24: --max-agents 1 on a 50-key window."""
    try:
        refuse_starvation_override(50, 1)
    except ValueError as exc:
        assert 'C2_M50_W1_MAX_AGENTS1_2026-07-24' in str(exc)
        assert '--max-wide' in str(exc), 'the refusal must name the width knob it was confused with'
    else:
        raise AssertionError('--max-agents=1 on a 50-key window must be refused')

    forced = refuse_starvation_override(50, 1, force=True)
    assert forced and forced.startswith('WARNING'), forced

    # A true single-spawn canary (1 key) and any override at/above the key count pass.
    assert refuse_starvation_override(1, 1) is None
    assert refuse_starvation_override(4, 4) is None
    assert refuse_starvation_override(4, None) is None

    # The override remains a COMBINED ceiling once allowed: it never inflates.
    plan = derive_agent_budget(4, {'a': 2, 'b': 2}, max_agents_override=6)
    assert plan.max_agents == 6
    assert plan.max_translate_agents + plan.max_heal_agents == 6


if __name__ == '__main__':
    selftest()
