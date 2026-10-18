"""scripts/check_prose_number_drift.py — the prose-number gate (H5421, hardened H5509).

Pins BOTH separator regimes: the canonical comma forms the gate was born with
(H5421) and the space/NBSP/narrow-NBSP/thin-space forms RU-locale prose
carries — the exact shape that let «323 425» live in the published H5509
explainer from 26-09 to 05-10-2026 while the gate stayed green. Negative
controls keep the gate honest: the display value in any separator (RU prose
may legally re-separate the CORRECT figure) and interior digit groups of
larger numbers must never hit.
"""
from __future__ import annotations

from conftest import load_module

CLAIM = {
    "id": "union-headword-count",
    "display": "323,422",
    "stale_values": ["323,425", "323,426", "323,417"],
    "allow_paths": ["CHANGELOG.md", "changelog_queue/*", "changelog_queue/**"],
}

ARTICLE = "SANSKRIT_WORD_COUNT_FIVE_DENOMINATORS_26-09-2026.md"


def _regex():
    mod = load_module("scripts/check_prose_number_drift.py")
    return mod.build_regex(CLAIM)


def test_stale_comma_form_hits():
    assert _regex().search("union даёт 323,425 статей")


def test_stale_plain_space_form_hits():  # the H5509 miss, verbatim shape
    assert _regex().search("| **323 425** (из них 17 386 статей")


def test_stale_nbsp_and_narrow_and_thin_forms_hit():
    rx = _regex()
    assert rx.search("323\u00a0425 ;")
    assert rx.search("323\u202f425.")
    assert rx.search("323\u2009417?")


def test_other_stale_values_space_forms_hit():
    rx = _regex()
    assert rx.search("было 323 426 потом")
    assert rx.search("старое 323,417 значение")


def test_display_comma_is_matched_for_main_skip_but_not_new():
    # display stays literal in the alternation; main() skips old == display
    rx = _regex()
    assert rx.search("верно: 323,422 статей")


def test_display_reseparated_ru_prose_never_hits():
    rx = _regex()
    assert rx.search("верно и по-русски: 323 422 статей") is None
    assert rx.search("323\u00a0422.") is None


def test_interior_groups_of_larger_numbers_never_hit():
    rx = _regex()
    assert rx.search("миллионы: 1 323 425 и 323 425 000 — группы") is None
    assert rx.search("1,323,425 rows") is None


def test_fix_mode_rewrites_separator_variants_to_display():
    fixed = _regex().sub(CLAIM["display"], "**323 425** и 323,426 и 323\u202f417")
    assert fixed == "**323,422** и 323,422 и 323,422"


def test_gate_is_green_on_the_live_explainer():
    mod = load_module("scripts/check_prose_number_drift.py")
    assert mod.main(["--check", ARTICLE]) == 0
