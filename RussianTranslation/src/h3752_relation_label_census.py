#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""h3752_relation_label_census.py — W5 census: does the relation LABEL survive
its own attachment result? (H3752, issue #1736)

Read-only. Writes nothing but an optional dated report; never touches the store,
the sidecar or the mirror. This is step 1 of the W4/W5 store-mutation pattern
(ARCHITECTURE §2): the census gates the rewrite half, and under PLAN ruling 14 a
population diverging >=2x from the issue's claim HALTS the rewrite and the unit
delivers census-only.

What it measures, against the CURRENT classifier and the CURRENT store:

  * modes A/B/C of issue #1736 -- `*new` by construction / dangling target /
    target really found -- per subtype, and for `restate` specifically;
  * how many rows carry a SENSE-ASSERTING subtype while `placement` is false,
    i.e. the population the label re-derivation would relabel;
  * the same count on the canonical store's own `edition_rel` field, which is
    the half that needs a ledgered rewrite rather than a regeneration.

Run:
  python src/h3752_relation_label_census.py                 # print
  python src/h3752_relation_label_census.py --report <path> # + write markdown
  python src/h3752_relation_label_census.py --selftest
"""
import argparse
import collections
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from store_path import canonical_store, main_worktree_root      # noqa: E402
from edition_rel import (                                       # noqa: E402
    SENSE_ASSERTING, build_pwg_gender_index, build_pwg_sense_index,
    edition_rel_for_row, pwg_correction_marker, unplaced_name,
)

STORE = canonical_store(os.path.join(HERE, "pwg_ru_translated.jsonl"))
_MAIN = main_worktree_root(HERE)
SIDECAR = (os.path.join(_MAIN, "RussianTranslation", "src",
                        "pwg_ru_relationships.jsonl") if _MAIN
           else os.path.join(HERE, "pwg_ru_relationships.jsonl"))

# The claims of issue #1736, measured 16-08-2026 over a 5,603-row sidecar. PLAN
# ruling 14 compares the live census against these and halts the rewrite half on
# a >=2x divergence.
ISSUE_CLAIM = {
    "sidecar_rows": 5603,
    "restate_rows": 5054,
    "restate_new": 4132,       # the headline population
    "restate_dangling": 404,
    "restate_found": 518,
}


def load_jsonl(path):
    rows = []
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def qualifying(recs):
    """The store rows that get a sidecar row (build_relationships.classify_store)."""
    for d in recs:
        if d.get("layer") == "pwg" and not pwg_correction_marker(d.get("sense_tag")):
            continue
        yield d


def mode_of(rel):
    """Issue #1736's three modes, over the placement axis wave 1 already built."""
    reason = rel.get("placement_reason")
    if reason == "found":
        return "C_found"
    if reason == "no_target_marker":
        return "A_new"
    return "B_dangling"          # not_found | out_of_range


def census(recs):
    """Classify the whole store and count. Returns a plain dict of counters."""
    gender = build_pwg_gender_index(recs)
    senses = build_pwg_sense_index(recs)

    by_mode = collections.Counter()
    by_subtype = collections.Counter()
    by_subtype_mode = collections.Counter()
    by_reason = collections.Counter()
    # the population the re-derivation relabels: sense-asserting subtype, no target
    relabel = collections.Counter()
    rows = 0

    for d in qualifying(recs):
        rel = edition_rel_for_row(d, gender, senses)
        st = rel["subtype"]
        # census the BASE name, so the count is stable whether it runs before or
        # after the re-derivation lands (the report must be reproducible on both).
        base = st[: -len("_unplaced")] if st.endswith("_unplaced") else st
        m = mode_of(rel)
        rows += 1
        by_mode[m] += 1
        by_subtype[base] += 1
        by_subtype_mode[(base, m)] += 1
        by_reason[rel["placement_reason"]] += 1
        if base in SENSE_ASSERTING and not rel["placement"]:
            relabel[base] += 1

    return {
        "rows": rows,
        "by_mode": by_mode,
        "by_subtype": by_subtype,
        "by_subtype_mode": by_subtype_mode,
        "by_reason": by_reason,
        "relabel": relabel,
    }


def store_edition_rel_census(recs):
    """The `edition_rel` field carried ON store rows -- the ledgered-rewrite half.

    The sidecar is fully derived and is regenerated, not ledgered. Any row whose
    stored `edition_rel.subtype` would change is a real store mutation and needs
    a ledger row under the H3591 pattern.
    """
    gender = build_pwg_gender_index(recs)
    senses = build_pwg_sense_index(recs)
    carried = 0
    changed = []
    for d in recs:
        er = d.get("edition_rel")
        if not isinstance(er, dict):
            continue
        carried += 1
        old = er.get("subtype")
        new = edition_rel_for_row(d, gender, senses)["subtype"]
        if old != new:
            changed.append({
                "key1": d.get("key1"), "subcard": d.get("subcard"),
                "sense_tag": str(d.get("sense_tag")), "layer": d.get("layer"),
                "subtype_before": old, "subtype_after": new,
            })
    return carried, changed


def divergence(measured, claimed):
    """Ratio used by PLAN ruling 14. A claim of 0 can never diverge by a factor."""
    if not claimed:
        return 0.0
    return max(measured, claimed) / float(min(measured, claimed) or 1)


def render(c, sidecar_rows, carried, changed):
    L = []
    w = L.append
    w("store rows classified (sidecar population) : %d" % c["rows"])
    w("sidecar rows on disk                       : %s" % (
        sidecar_rows if sidecar_rows is not None else "(absent)"))
    w("")
    w("mode (issue #1736):")
    for k, label in (("A_new", "A  *new by construction"),
                     ("B_dangling", "B  dangling target"),
                     ("C_found", "C  target found")):
        n = c["by_mode"][k]
        w("  %-26s %6d  %5.1f%%" % (label, n, 100.0 * n / max(c["rows"], 1)))
    w("")
    w("placement_reason:")
    for k in ("found", "no_target_marker", "out_of_range", "not_found"):
        w("  %-18s %6d" % (k, c["by_reason"][k]))
    w("")
    w("subtype x mode:")
    w("  %-26s %7s %7s %7s %7s" % ("subtype", "total", "A_new", "B_dang", "C_found"))
    for st, tot in sorted(c["by_subtype"].items(), key=lambda kv: -kv[1]):
        w("  %-26s %7d %7d %7d %7d%s" % (
            st, tot,
            c["by_subtype_mode"][(st, "A_new")],
            c["by_subtype_mode"][(st, "B_dangling")],
            c["by_subtype_mode"][(st, "C_found")],
            "  <- sense-asserting" if st in SENSE_ASSERTING else ""))
    w("")
    w("relabelled by the re-derivation (sense-asserting subtype, no target):")
    tot = 0
    for st, n in sorted(c["relabel"].items(), key=lambda kv: -kv[1]):
        w("  %-26s %6d  ->  %s" % (st, n, unplaced_name(st)))
        tot += n
    w("  %-26s %6d" % ("TOTAL", tot))
    w("")
    w("ruling-14 divergence vs issue #1736 (16-08-2026):")
    live_restate_new = c["by_subtype_mode"][("restate", "A_new")]
    for name, measured, claimed in (
        ("restate rows", c["by_subtype"]["restate"], ISSUE_CLAIM["restate_rows"]),
        ("restate *new", live_restate_new, ISSUE_CLAIM["restate_new"]),
        ("restate dangling", c["by_subtype_mode"][("restate", "B_dangling")],
         ISSUE_CLAIM["restate_dangling"]),
        ("restate found", c["by_subtype_mode"][("restate", "C_found")],
         ISSUE_CLAIM["restate_found"]),
    ):
        d = divergence(measured, claimed)
        w("  %-18s live %6d  issue %6d  x%.2f%s" % (
            name, measured, claimed, d, "   HALT (>=2x)" if d >= 2.0 else ""))
    w("")
    w("canonical store `edition_rel` field (the ledgered half):")
    w("  rows carrying edition_rel : %d" % carried)
    w("  rows whose subtype changes: %d" % len(changed))
    return "\n".join(L)


def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    recs = [
        # PWG skeleton: senses 1 and 2 exist
        {"key1": "x", "subcard": "x~~h0_00_pwg00", "layer": "pwg",
         "sense_tag": "1", "de": "{%x%}"},
        {"key1": "x", "subcard": "x~~h0_00_pwg01", "layer": "pwg",
         "sense_tag": "2", "de": "{%x%}"},
        # PW pointing at sense 1 -> found (mode C), stays `restate`
        {"key1": "x", "subcard": "x~~h0_zz_pw01", "layer": "pw",
         "sense_tag": "1", "de": "{%kurz%}"},
        # PW with no leading number -> mode A, relabelled
        {"key1": "x", "subcard": "x~~h0_zz_pw02", "layer": "pw",
         "sense_tag": "caus", "de": "{%kurz%}"},
        # PW pointing at a sense that is not there but inside range -> mode B
        {"key1": "x", "subcard": "x~~h0_zz_pw03", "layer": "pw",
         "sense_tag": "9", "de": "{%kurz%}"},
        # SCH additive, no target -> NOT sense-asserting, untouched
        {"key1": "x", "subcard": "x~~h0_zz_sch01", "layer": "sch",
         "sense_tag": "neu", "de": "{%neu%}"},
    ]
    c = census(recs)
    check(c["rows"] == 4, "only non-pwg rows enter the census (%d)" % c["rows"])
    check(c["by_mode"]["A_new"] == 2, "mode A counted: %d" % c["by_mode"]["A_new"])
    check(c["by_mode"]["B_dangling"] == 1,
          "mode B counted: %d" % c["by_mode"]["B_dangling"])
    check(c["by_mode"]["C_found"] == 1,
          "mode C counted: %d" % c["by_mode"]["C_found"])
    check(c["relabel"]["restate"] == 2,
          "both unplaced restates relabel: %r" % dict(c["relabel"]))
    check("sch_star" not in c["relabel"],
          "an additive subtype is never relabelled: %r" % dict(c["relabel"]))
    # the census keys on the BASE name, so it reads the same before and after
    check(c["by_subtype"]["restate"] == 3,
          "subtype census uses the base name: %r" % dict(c["by_subtype"]))
    check(abs(divergence(4132, 4132) - 1.0) < 1e-9, "divergence of equals is 1")
    check(divergence(8264, 4132) == 2.0, "a doubled population diverges 2x")
    check(divergence(2066, 4132) == 2.0, "a halved population diverges 2x too")

    carried, changed = store_edition_rel_census([
        dict(recs[3], edition_rel={"subtype": "restate"}),
    ] + recs[:3])
    check(carried == 1, "only rows carrying edition_rel are counted: %d" % carried)
    check(len(changed) == 1 and changed[0]["subtype_after"] == "restate_unplaced",
          "a stored stale label is reported for the ledger: %r" % changed)

    print("h3752_relation_label_census selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default=None,
                    help="also write the census as markdown to this path")
    ap.add_argument("--store", default=STORE)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    recs = load_jsonl(a.store)
    sidecar_rows = None
    if os.path.exists(SIDECAR):
        with io.open(SIDECAR, encoding="utf-8") as fh:
            sidecar_rows = sum(1 for line in fh if line.strip())

    c = census(recs)
    carried, changed = store_edition_rel_census(recs)
    text = render(c, sidecar_rows, carried, changed)
    print(text)
    print("\nstore: %s (%d rows)" % (a.store, len(recs)))

    if a.report:
        with io.open(a.report, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("```\n" + text + "\n```\n")
        print("wrote %s" % a.report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
