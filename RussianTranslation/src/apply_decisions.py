#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_decisions — validator-gated ingest of a review sheet's decisions.json (H1404).

The repo-side realization of the `/decisions-apply` wiring: the FIRST thing
this script does is run ``validate_decisions.validate()`` and hard-stop on any
rejection — a decisions.json that cannot be bound to a known sheet lock never
touches a queue, a CSV, or a gold label. Only then does it route by gate (from
the sheet's committed lock, overridable with ``--gate``):

* **G5** (bulk edition decisions) — merge the votes into the pwg_ru review CSV
  (``src/_review_queue.csv``; approve→``approved``, reject→``reject``,
  defer→``needs_review``; every decided row needs a reviewer), then run the
  existing gate check ``python src/run_batch.py validate_review <csv>``.
  Print-ready promotion stays run_batch's job — this script never bypasses its
  key_match/placeholders_ok integrity rules.
* **G6** (gold labels) — convert the votes into the 11-column human-gold CSV
  (metadata joined from ``gold/gold_set.jsonl``; approve = confirm the shown
  LLM label, reject = the correct label written as the FIRST token of the note
  — same convention as the H180 typology sheet — defer = needs_adjudication),
  then run ``python src/gold_ingest.py <csv> <out.jsonl>`` (explicit out path:
  the 320-item hard gate belongs to the full set, not a starter packet).

Unmatched ids, unparseable reject labels, or a missing reviewer abort BEFORE
anything is written — partial application is worse than no application.

CLI:
  python src/apply_decisions.py <decisions.json> [--gate G5|G6] [--locks-dir DIR]
      [--allow-legacy] [--reviewer NAME] [--dry-run]
      [--review-csv PATH]              (G5; default src/_review_queue.csv)
      [--gold-set PATH] [--out-dir D]  (G6; defaults gold/gold_set.jsonl, gold/)
  python src/apply_decisions.py --selftest
Exit 0 = applied (downstream check ran green); 1 = rejected/aborted; 2 = usage/parked.
"""
import csv
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import validate_decisions
from validate_decisions import Reject

DEFAULT_REVIEW_CSV = os.path.join(HERE, "_review_queue.csv")
DEFAULT_GOLD_SET = os.path.join(RT, "gold", "gold_set.jsonl")
DEFAULT_G6_OUT_DIR = os.path.join(RT, "gold")

G5_DECISION_MAP = {"approve": "approved", "reject": "reject", "defer": "needs_review"}
G6_LABELS = {"correct", "lemma-variant", "proper-name", "partial", "wrong-sense",
             "hallucinated"}


def _decided_items(doc):
    return [it for it in doc["items"] if it.get("decision")]


def _reviewer(doc, cli_reviewer):
    return (doc.get("reviewer") or cli_reviewer or "").strip()


# --------------------------------------------------------------------------- G5
def apply_g5(doc, review_csv, reviewer, dry_run=False):
    decided = _decided_items(doc)
    if not decided:
        print("G5: nothing decided in the export — nothing to apply")
        return 0
    if not reviewer:
        print("ABORT G5: no reviewer — the export carries no strict-review 'reviewer' "
              "field; pass --reviewer (run_batch requires reviewer_id per decision)")
        return 1
    if not os.path.exists(review_csv):
        print("ABORT G5: review CSV %s missing — run: python src/run_batch.py review_csv"
              % review_csv)
        return 1
    with io.open(review_csv, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames
        rows = list(reader)
    by_rid = {}
    for row in rows:
        rid = (row.get("review_id") or "").strip()
        if rid:
            by_rid.setdefault(rid, []).append(row)
    votes = {it["id"]: it for it in decided}
    unmatched = sorted(set(votes) - set(by_rid))
    if unmatched:
        print("ABORT G5: %d decided id(s) not present in %s — nothing applied. "
              "e.g. %s" % (len(unmatched), review_csv, ", ".join(unmatched[:5])))
        return 1
    applied = 0
    for rid, it in votes.items():
        for row in by_rid[rid]:
            row["decision"] = G5_DECISION_MAP[it["decision"]]
            row["reviewer_id"] = reviewer
            note = (it.get("note") or "").strip()
            if note:
                existing = (row.get("notes") or "").strip()
                row["notes"] = (existing + " | " if existing else "") + note
            applied += 1
    if dry_run:
        print("DRY-RUN G5: would apply %d decision(s) from sheet '%s' to %s and run "
              "run_batch validate_review" % (applied, doc["sheet_id"], review_csv))
        return 0
    with io.open(review_csv, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print("G5: applied %d decision(s) from sheet '%s' to %s"
          % (applied, doc["sheet_id"], review_csv))
    proc = subprocess.run([sys.executable, os.path.join(HERE, "run_batch.py"),
                           "validate_review", review_csv], encoding="utf-8")
    return proc.returncode


# --------------------------------------------------------------------------- G6
def g6_rows(doc, gold_meta, reviewer):
    """Convert bound votes to gold_validate's 11-column rows. Raises Reject on
    any unconvertible vote so the caller aborts before writing."""
    rows, problems = [], []
    for it in _decided_items(doc):
        meta = gold_meta.get(it["id"])
        if meta is None:
            problems.append("%s: not in gold_set" % it["id"])
            continue
        llm_label = meta.get("label", "")
        note = (it.get("note") or "").strip()
        decision = it["decision"]
        needs_adj = "false"
        if decision == "approve":
            human_label = llm_label
        elif decision == "reject":
            reject_label = (it.get("reject_label") or "").strip().lower()
            if reject_label:
                # H1802: the emitter's required single-select control — preferred
                # over the note-prefix convention whenever the export carries it.
                if reject_label not in G6_LABELS:
                    problems.append("%s: reject_label %r is not one of %s"
                                    % (it["id"], reject_label, "|".join(sorted(G6_LABELS))))
                    continue
                human_label = reject_label
            else:
                # Legacy fallback for sheets exported before H1802.
                first = note.split()[0].strip(".,;:—-").lower() if note else ""
                if first not in G6_LABELS:
                    problems.append("%s: reject note must START with the correct label "
                                    "(one of %s); got %r"
                                    % (it["id"], "|".join(sorted(G6_LABELS)), note[:40]))
                    continue
                human_label = first
        else:  # defer
            human_label = llm_label
            needs_adj = "true"
        rating = it.get("rating")
        confidence = ("high" if rating is not None and rating >= 4 else
                      "low" if rating is not None and rating <= 2 else "medium")
        rows.append({
            "id": it["id"], "slp1": meta.get("slp1", ""), "sa": meta.get("sa", ""),
            "ru": meta.get("ru", ""), "kind": meta.get("kind", ""),
            "period": meta.get("period", ""), "work": meta.get("work", ""),
            "llm_label": llm_label, "human_label": human_label,
            "reviewer_id": reviewer, "confidence": confidence,
            "needs_adjudication": needs_adj, "human_note": note,
        })
    if problems:
        raise Reject("G6 conversion: %d problem(s) — nothing applied.\n  "
                     % len(problems) + "\n  ".join(problems[:10]))
    return rows


def apply_g6(doc, gold_set, out_dir, reviewer, dry_run=False):
    decided = _decided_items(doc)
    if not decided:
        print("G6: nothing decided in the export — nothing to apply")
        return 0
    if not reviewer:
        print("ABORT G6: no reviewer — pass --reviewer or use a strict-review sheet")
        return 1
    if not os.path.exists(gold_set):
        print("ABORT G6: gold set %s missing" % gold_set)
        return 1
    gold_meta = {}
    for line in io.open(gold_set, encoding="utf-8"):
        if line.strip():
            rec = json.loads(line)
            gold_meta[str(rec.get("id"))] = rec
    try:
        rows = g6_rows(doc, gold_meta, reviewer)
    except Reject as e:
        print("ABORT %s" % e)
        return 1
    sheet_slug = doc["sheet_id"].replace("/", "_")
    out_csv = os.path.join(out_dir, "decisions_%s.csv" % sheet_slug)
    out_jsonl = os.path.join(out_dir, "decisions_%s.labels.jsonl" % sheet_slug)
    if dry_run:
        print("DRY-RUN G6: would write %d label row(s) -> %s and run gold_ingest -> %s"
              % (len(rows), out_csv, out_jsonl))
        return 0
    fields = ["id", "slp1", "sa", "ru", "kind", "period", "work", "llm_label",
              "human_label", "reviewer_id", "confidence", "needs_adjudication",
              "human_note"]
    with io.open(out_csv, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print("G6: wrote %d label row(s) from sheet '%s' -> %s"
          % (len(rows), doc["sheet_id"], out_csv))
    proc = subprocess.run([sys.executable, os.path.join(HERE, "gold_ingest.py"),
                           out_csv, out_jsonl], encoding="utf-8")
    return proc.returncode


# --------------------------------------------------------------------------- main
def main(argv):
    if "--selftest" in argv:
        return _selftest()
    opts = {"--gate": None, "--locks-dir": None, "--reviewer": None,
            "--review-csv": DEFAULT_REVIEW_CSV, "--gold-set": DEFAULT_GOLD_SET,
            "--out-dir": DEFAULT_G6_OUT_DIR}
    flags = {"--allow-legacy": False, "--dry-run": False}
    paths = []
    i = 0
    while i < len(argv):
        if argv[i] in opts:
            opts[argv[i]] = argv[i + 1]; i += 2
        elif argv[i] in flags:
            flags[argv[i]] = True; i += 1
        else:
            paths.append(argv[i]); i += 1
    if len(paths) != 1:
        print(__doc__)
        return 2

    # Gate 1 — the validator, always, before anything is applied.
    try:
        doc = validate_decisions.validate(paths[0], locks_dir=opts["--locks-dir"],
                                          allow_legacy=flags["--allow-legacy"])
    except Reject as e:
        print("REJECTED %s\n  %s\n  (nothing applied)" % (paths[0], e))
        return 1

    gate = opts["--gate"]
    if gate is None:
        locks_dir = opts["--locks-dir"] or validate_decisions.DEFAULT_LOCKS_DIR
        with io.open(os.path.join(locks_dir, doc["sheet_id"] + ".lock.json"),
                     encoding="utf-8") as fh:
            lock = json.load(fh)
        gate = lock.get("gate")
    if gate not in ("G5", "G6"):
        print("PARKED: sheet '%s' carries no G5/G6 gate in its lock (gate=%r) — "
              "pass --gate explicitly, or route this pilot/retired sheet by hand"
              % (doc["sheet_id"], gate))
        return 2

    reviewer = _reviewer(doc, opts["--reviewer"])
    if gate == "G5":
        return apply_g5(doc, opts["--review-csv"], reviewer, dry_run=flags["--dry-run"])
    return apply_g6(doc, opts["--gold-set"], opts["--out-dir"], reviewer,
                    dry_run=flags["--dry-run"])


# --------------------------------------------------------------------------- selftest
def _selftest():
    import tempfile
    from review_binding import _MINI, stamp, write_lock, extract_ids, extract_sheet_id

    ok = True

    def check(cond, label):
        nonlocal ok
        print(("  ok " if cond else "  FAIL ") + label)
        ok = ok and cond

    with tempfile.TemporaryDirectory() as td:
        _, chash = stamp(_MINI)
        sheet_id = extract_sheet_id(_MINI)
        ids = extract_ids(_MINI)  # ["a|1", "b|2"]

        def dump(name, docd):
            p = os.path.join(td, name)
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(docd, fh, ensure_ascii=False, indent=2)
            return p

        good = {"sheet_id": sheet_id, "generated": "2026-07-25", "decided": 2,
                "content_hash": chash, "reviewer": "selftest",
                "items": [{"id": ids[0], "decision": "approve", "note": ""},
                          {"id": ids[1], "decision": "reject",
                           "note": "wrong-sense — глосса не о том"}]}

        # 1. the validator gate: a corrupt file is refused BEFORE any apply.
        write_lock(sheet_id, chash, ids, "2026-07-25", locks_dir=td, gate="G6",
                   force=True)   # fixture: one sheet_id, several generations
        bad = dict(good, content_hash="sha256:" + "e" * 64)
        marker = os.path.join(td, "decisions_%s.csv" % sheet_id)
        rc = main([dump("bad.json", bad), "--locks-dir", td,
                   "--gold-set", os.path.join(td, "gs.jsonl"), "--out-dir", td])
        check(rc == 1 and not os.path.exists(marker),
              "bad file refused by the validator before any decision is applied")

        # 2. G6 route: convert + gold_ingest end-to-end.
        with io.open(os.path.join(td, "gs.jsonl"), "w", encoding="utf-8",
                     newline="\n") as fh:
            for gid in ids:
                fh.write(json.dumps({"id": gid, "slp1": "gam", "sa": "s", "ru": "р",
                                     "kind": "translation", "period": "Classical",
                                     "work": "w", "label": "correct"},
                                    ensure_ascii=False) + "\n")
        rc = main([dump("good.json", good), "--locks-dir", td,
                   "--gold-set", os.path.join(td, "gs.jsonl"), "--out-dir", td])
        labels_path = os.path.join(td, "decisions_%s.labels.jsonl" % sheet_id)
        check(rc == 0 and os.path.exists(labels_path), "G6 route runs through gold_ingest")
        if os.path.exists(labels_path):
            labels = [json.loads(l) for l in io.open(labels_path, encoding="utf-8")]
            check(sorted(r["human_label"] for r in labels) == ["correct", "wrong-sense"],
                  "approve confirms LLM label; reject note's first token becomes the label")

        # 2b. H1802: csl-pyutil's reject_labels picker field is preferred over
        # the note-prefix convention (note carries free-text rationale only).
        field_good = dict(good, items=[
            {"id": ids[0], "decision": "approve", "note": ""},
            {"id": ids[1], "decision": "reject", "note": "плохая глосса, не связана",
             "reject_label": "hallucinated"}])
        rc = main([dump("field_good.json", field_good), "--locks-dir", td,
                   "--gold-set", os.path.join(td, "gs.jsonl"), "--out-dir", td])
        check(rc == 0, "G6 route accepts a reject_label field (rc=%s)" % rc)
        if rc == 0 and os.path.exists(labels_path):
            labels = [json.loads(l) for l in io.open(labels_path, encoding="utf-8")]
            check(sorted(r["human_label"] for r in labels) == ["correct", "hallucinated"],
                  "reject_label field wins over a note that doesn't start with the label")

        # 3. G6 abort on an unparseable reject note — nothing written.
        badnote = dict(good, items=[{"id": ids[0], "decision": "reject", "note": "nope"},
                                    {"id": ids[1], "decision": "approve", "note": ""}])
        rc = main([dump("badnote.json", badnote), "--locks-dir", td,
                   "--gold-set", os.path.join(td, "gs.jsonl"), "--out-dir",
                   os.path.join(td, "sub")])
        check(rc == 1 and not os.path.exists(os.path.join(td, "sub")),
              "unparseable reject label aborts before writing")

        # 4. G5 route: merge + run_batch validate_review (fixture store via env).
        # run_batch derives store review_ids as 'ord:<ord>', so the G5 fixture
        # sheet uses ord-shaped card ids (a real G5 sheet does the same).
        mini_g5 = _MINI.replace('["a|1","b|2"]', '["ord:1","ord:2"]')
        _, chash = stamp(mini_g5)
        ids = extract_ids(mini_g5)
        good = {"sheet_id": sheet_id, "generated": "2026-07-25", "decided": 2,
                "content_hash": chash, "reviewer": "selftest",
                "items": [{"id": ids[0], "decision": "approve", "note": ""},
                          {"id": ids[1], "decision": "reject", "note": "не то"}]}
        write_lock(sheet_id, chash, ids, "2026-07-25", locks_dir=td, gate="G5",
                   force=True)   # fixture: one sheet_id, several generations
        g5csv = os.path.join(td, "rq.csv")
        fields = ["review_id", "severity", "ord", "key1", "key2", "review_status",
                  "key_match", "placeholders_ok", "reason", "attested", "ru",
                  "reviewer_id", "decision", "edit", "notes"]
        with io.open(g5csv, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for n, gid in enumerate(ids, 1):
                w.writerow({"review_id": gid, "severity": "1", "ord": str(n),
                            "key1": "gam", "key2": "gam", "review_status": "ai_translated",
                            "key_match": "true", "placeholders_ok": "true",
                            "reason": "", "attested": "true", "ru": "р",
                            "reviewer_id": "", "decision": "", "edit": "", "notes": ""})
        store = os.path.join(td, "store.jsonl")
        with io.open(store, "w", encoding="utf-8", newline="\n") as fh:
            for n in (1, 2):
                fh.write(json.dumps({"ord": n, "subcard": "gam~~h0",
                                     "sense_tag": str(n)}) + "\n")
        # the run_batch subprocess reads the store path from the environment
        os.environ["PWG_RU_STORE"] = store
        try:
            rc = main([dump("good.json", good), "--locks-dir", td,
                       "--review-csv", g5csv])
        finally:
            os.environ.pop("PWG_RU_STORE", None)
        with io.open(g5csv, encoding="utf-8-sig", newline="") as fh:
            merged = {r["review_id"]: r for r in csv.DictReader(fh)}
        check(merged[ids[0]]["decision"] == "approved"
              and merged[ids[1]]["decision"] == "reject"
              and merged[ids[0]]["reviewer_id"] == "selftest",
              "G5 merge writes decisions + reviewer into the review CSV")
        g5_ok = rc == 0
        check(g5_ok, "G5 route ends with run_batch validate_review green (rc=%s)" % rc)

        # 5. G5 positional-id drift: 'row:NNNNNN:' review_ids embed the store
        # LINE POSITION at queue-mint time; when the store grows before the
        # decisions are applied, the position goes stale (g5-live-queue-batch1,
        # 26-07-2026: 2/5 votes hit 'not found in store'). run_batch must fall
        # back to the stable 'subcard:<sub>#<tag>' tail.
        drift_id = "row:000001:subcard:gam~~h0#1"
        mini_drift = _MINI.replace('["a|1","b|2"]', json.dumps([drift_id]))
        _, chash = stamp(mini_drift)
        good = {"sheet_id": sheet_id, "generated": "2026-07-25", "decided": 1,
                "content_hash": chash, "reviewer": "selftest",
                "items": [{"id": drift_id, "decision": "approve", "note": ""}]}
        write_lock(sheet_id, chash, [drift_id], "2026-07-25", locks_dir=td,
                   gate="G5", force=True)   # fixture: deliberate re-cut
        with io.open(g5csv, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerow({"review_id": drift_id, "severity": "1", "ord": "",
                        "key1": "gam", "key2": "gam", "review_status": "ai_translated",
                        "key_match": "true", "placeholders_ok": "true",
                        "reason": "", "attested": "true", "ru": "р",
                        "reviewer_id": "", "decision": "", "edit": "", "notes": ""})
        with io.open(store, "w", encoding="utf-8", newline="\n") as fh:
            # a row prepended since queue mint shifts gam~~h0#1 to position 2
            fh.write(json.dumps({"subcard": "newer~~h0", "sense_tag": "1"}) + "\n")
            fh.write(json.dumps({"subcard": "gam~~h0", "sense_tag": "1"}) + "\n")
        os.environ["PWG_RU_STORE"] = store
        try:
            rc = main([dump("drift.json", good), "--locks-dir", td,
                       "--review-csv", g5csv])
        finally:
            os.environ.pop("PWG_RU_STORE", None)
        check(rc == 0, "stale positional review_id resolves via its subcard#tag "
                       "tail (rc=%s)" % rc)

    print("apply_decisions selftest " + ("OK" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main(sys.argv[1:]))
