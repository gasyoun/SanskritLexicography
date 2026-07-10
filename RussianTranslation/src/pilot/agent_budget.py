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
    print('agent_budget selftest OK')


if __name__ == '__main__':
    selftest()
