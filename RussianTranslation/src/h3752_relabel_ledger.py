#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""h3752_relabel_ledger.py — the ledger for the W5 relation-label revision.

Step 2 of the W4/W5 store-mutation pattern (ARCHITECTURE §2): every changed row
gets a ledger row carrying its old value, its new value, the rule that moved it
and the run's timestamp, and the ledger lands in the same PR as the rewrite.

Scope note, measured rather than assumed (see the H3752 report): the relation
label lives in the DERIVED sidecar `src/pwg_ru_relationships.jsonl`, not in the
canonical store. `pwg_ru_translated.jsonl` carries an `edition_rel` field on 86
rows, all of them `pwg`-layer `base` (76) or `pwg_internal_correction` (10) —
neither is sense-asserting, so **zero canonical-store rows change** and the
store stays byte-identical (proved by `placement_axis_check.py` A5). The ledger
is therefore over the sidecar. That does not make it optional: the sidecar is
what every sheet, rollup and published percentage reads, and a 5,000-row label
change with no before/after record is precisely the unledgered mutation PLAN
ruling 14 halts on.

Rows are joined on H3300 `row_key`, never on the bare `(subcard, sense_tag)`
pair — 132 pairs repeat in this sidecar (595 rows under them) and a bare-pair
join would silently ledger the wrong sibling (FINDINGS §551).

  python src/h3752_relabel_ledger.py --before <old.jsonl> --after <new.jsonl> \
      --out <ledger.jsonl> [--summary-only]
  python src/h3752_relabel_ledger.py --selftest
"""
import argparse
import collections
import hashlib
import io
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from edition_rel import base_subtype, is_unplaced_label   # noqa: E402

HANDOFF = "H3752"
RULE = ("label re-derived from the sense-attachment result: a sense-asserting "
        "subtype with no identified PWG target takes its `_unplaced` twin "
        "(issue #1736, REGLUE_SPEC §13)")


def load(path):
    rows = []
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def sha256_of(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def key_of(row):
    """H3300 row identity, with the legacy pair only as a last resort."""
    return row.get("row_key") or "%s::%s#0" % (row.get("subcard"),
                                               row.get("sense_tag"))


def diff(before, after):
    """Per-row label delta. Returns (entries, summary counters)."""
    b_by = {key_of(r): r for r in before}
    a_by = {key_of(r): r for r in after}

    entries = []
    moves = collections.Counter()
    summary = collections.Counter()

    for k, a in a_by.items():
        b = b_by.get(k)
        a_rel = a.get("relationship") or {}
        new = a_rel.get("subtype")
        if b is None:
            summary["added_rows"] += 1
            continue
        old = (b.get("relationship") or {}).get("subtype")
        if old == new:
            continue
        entries.append({
            "row_key": k,
            "key1": a.get("key1"),
            "subcard": a.get("subcard"),
            "sense_tag": a.get("sense_tag"),
            "layer": a.get("layer"),
            "subtype_before": old,
            "subtype_after": new,
            # the evidence the new label rests on, so a reviewer can disagree
            # with THIS row rather than with the rule in the abstract
            "placement": a_rel.get("placement"),
            "placement_reason": a_rel.get("placement_reason"),
            "target_sense": (a_rel.get("insertion_point") or {}).get("target_sense"),
        })
        moves["%s -> %s" % (old, new)] += 1
    summary["removed_rows"] = len(set(b_by) - set(a_by))
    summary["changed_rows"] = len(entries)
    summary["before_rows"] = len(before)
    summary["after_rows"] = len(after)
    return entries, moves, summary


def classify(entries):
    """Split the delta into the change this handoff authorises and anything else.

    An entry is IN SCOPE only if it is exactly a placed label becoming its own
    unplaced twin. Anything else — a different subtype family, a twin turning
    back into a plain label — is a different mutation and is reported
    separately rather than folded into the headline count.
    """
    in_scope, other = [], []
    for e in entries:
        before, after = e["subtype_before"], e["subtype_after"]
        if (is_unplaced_label(after) and not is_unplaced_label(before)
                and base_subtype(after) == before and e["placement"] is False):
            in_scope.append(e)
        else:
            other.append(e)
    return in_scope, other


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--out", default=None, help="ledger JSONL to write")
    ap.add_argument("--summary-only", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    before, after = load(a.before), load(a.after)
    entries, moves, summary = diff(before, after)
    in_scope, other = classify(entries)

    print("sidecar rows : %d -> %d (added %d, removed %d)"
          % (summary["before_rows"], summary["after_rows"],
             summary["added_rows"], summary["removed_rows"]))
    print("label changes: %d" % summary["changed_rows"])
    for m, n in moves.most_common():
        print("  %-46s %d" % (m, n))
    print("in scope (placed label -> its unplaced twin): %d" % len(in_scope))
    print("OUT OF SCOPE (any other label move)         : %d" % len(other))
    if other:
        for e in other[:10]:
            print("  ! %s  %s -> %s" % (e["row_key"], e["subtype_before"],
                                        e["subtype_after"]))

    if a.summary_only or not a.out:
        return 1 if other else 0

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    header = {
        "handoff": HANDOFF,
        "ts": stamp,
        "issue": "https://github.com/gasyoun/SanskritLexicography/issues/1736",
        "rule": RULE,
        "artifact": "RussianTranslation/src/pwg_ru_relationships.jsonl (derived)",
        "canonical_store_rows_changed": 0,
        "before_rows": summary["before_rows"],
        "after_rows": summary["after_rows"],
        "changed_rows": summary["changed_rows"],
        "in_scope_rows": len(in_scope),
        "out_of_scope_rows": len(other),
        "moves": dict(moves),
        "before_sha256": sha256_of(a.before),
        "after_sha256": sha256_of(a.after),
    }
    with io.open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(header, ensure_ascii=False) + "\n")
        for e in entries:
            fh.write(json.dumps(dict(e, handoff=HANDOFF, ts=stamp),
                                ensure_ascii=False) + "\n")
    print("wrote %s (%d entries + 1 header)" % (a.out, len(entries)))
    return 1 if other else 0


def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    def row(rk, subtype, placement, target="*new"):
        return {"row_key": rk, "key1": "x", "subcard": rk.split("::")[0],
                "sense_tag": "1", "layer": "pw",
                "relationship": {"subtype": subtype, "placement": placement,
                                 "placement_reason":
                                     "found" if placement else "no_target_marker",
                                 "insertion_point": {"target_sense": target}}}

    before = [row("a::1#0", "restate", False),
              row("a::1#1", "restate", True, "1"),
              row("b::1#0", "nws_at_sense", False),
              row("c::1#0", "sch_star", False)]
    after = [row("a::1#0", "restate_unplaced", False),
             row("a::1#1", "restate", True, "1"),
             row("b::1#0", "nws_at_sense_unplaced", False),
             row("c::1#0", "sch_star", False)]

    entries, moves, summary = diff(before, after)
    check(summary["changed_rows"] == 2, "only the two relabelled rows: %d"
          % summary["changed_rows"])
    in_scope, other = classify(entries)
    check(len(in_scope) == 2 and not other,
          "both moves are in scope: %d / %d" % (len(in_scope), len(other)))

    # THE join trap: `a::1#0` and `a::1#1` are the same (subcard, sense_tag).
    # A bare-pair join would ledger the placed sibling as if it had changed.
    changed_keys = {e["row_key"] for e in entries}
    check("a::1#1" not in changed_keys,
          "the placed duplicate sibling is NOT ledgered: %r" % changed_keys)

    # a move that is not "placed label -> its own twin" must be flagged, loudly
    entries2, _m, _s = diff([row("d::1#0", "restate", False)],
                            [row("d::1#0", "sch_star", False)])
    _in, other2 = classify(entries2)
    check(len(other2) == 1, "a cross-family move is out of scope: %r" % other2)
    # …and so is a twin reverting to a plain label on an unplaced row
    entries3, _m, _s = diff([row("e::1#0", "restate_unplaced", False)],
                            [row("e::1#0", "restate", False)])
    _in, other3 = classify(entries3)
    check(len(other3) == 1, "a reverting twin is out of scope: %r" % other3)
    # …and a twin claimed on a PLACED row, which W5a would also reject
    entries4, _m, _s = diff([row("f::1#0", "restate", True, "1")],
                            [row("f::1#0", "restate_unplaced", True, "1")])
    _in, other4 = classify(entries4)
    check(len(other4) == 1, "a twin on a placed row is out of scope: %r" % other4)

    print("h3752_relabel_ledger selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
