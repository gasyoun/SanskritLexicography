# -*- coding: utf-8 -*-
"""H3098 — the packset binding chain, end to end.

A packset is one instrument spread over a parent index and N pack pages. This
exercises the whole path the audit trail depends on:

    render packset -> stamp every part -> write ONE packset lock
        -> a pack-NN.json export validates against ITS pack
        -> an export from another pack does not
        -> a re-cut collides instead of silently rebinding

The last one is the point of the exercise. `write_lock`'s own docstring: an
overwritten lock "makes votes already cast against the committed generation
unapplicable, with no signal until validate_decisions.py rejects the export
AFTER the human has spent them" (H1703). A packset must inherit that, not
quietly lose it by being four files instead of one.

    python src/test_packset_binding.py
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import review_binding as rb  # noqa: E402

from csl_pyutil import render_review_sheet_packset  # noqa: E402

FAILS = []


def check(cond, label):
    print("  %s %s" % ("ok  " if cond else "FAIL", label))
    if not cond:
        FAILS.append(label)


def _items(n):
    return [{"id": "P%03d" % i, "filt": "a", "title": "card %d" % i,
             "question": "Is card %d right?" % i, "panels": []}
            for i in range(1, n + 1)]


def _config(sheet_id):
    return {"sheet_id": sheet_id, "title": "packset binding test",
            "subtitle": "H3098", "footer": "f.", "approve_label": "Approve",
            "reject_label": "Reject", "filters": [("a", "A")],
            "generated": "2026-08-18", "pack_size": 10}


def _screening(n):
    return {"deterministic": 0, "lookup": 0, "agent": 0, "human": n,
            "evidence_path": "src/test_packset_binding.py", "rules": ["synthetic"]}


def _export(sheet_id, pack_html, ids, decision="approve"):
    """The payload a pack page would download."""
    return {
        "sheet_id": sheet_id,
        "generated": "2026-08-18T00:00:00.000Z",
        "decided": len(ids),
        "content_hash": rb._stamped_hash(pack_html),
        "items": [{"id": i, "decision": decision, "note": ""} for i in ids],
    }


def main():
    tmp = tempfile.mkdtemp(prefix="h3098-")
    locks = os.path.join(tmp, "locks")
    sheet_id = "h3098-packset-selftest"
    try:
        out = render_review_sheet_packset(_items(22), _config(sheet_id),
                                          screening=_screening(22))
        check(out["parent"] is not None and len(out["packs"]) == 3,
              "22 items render as parent + 3 packs")

        parent = out["parent"]          # an index: hashed, never stamped
        packs = [rb.stamp(p)[0] for p in out["packs"]]

        path = rb.write_packset_lock(sheet_id, parent, packs, "2026-08-18",
                                     locks_dir=locks, gate="TEST")
        lock = json.load(io.open(path, encoding="utf-8"))

        check(lock["packset"]["n_packs"] == 3, "lock records 3 packs")
        check([p["n_items"] for p in lock["packset"]["packs"]] == [10, 10, 2],
              "lock records the 10/10/2 split")
        check(lock["n_items"] == 22 and len(lock["ids"]) == 22,
              "lock still names the whole instrument (22 ids)")
        check(lock["content_hash"] == lock["packset"]["packset_hash"],
              "top-level content_hash is the PACKSET hash")
        check(lock["packset"]["parent_hash"] == rb.content_hash(parent),
              "the parent index is hashed, not stamped")
        check(len({p["content_hash"] for p in lock["packset"]["packs"]}) == 3,
              "each pack binds its own distinct hash")

        # a pack export validates against ITS pack
        p2 = lock["packset"]["packs"][1]
        exp = _export(sheet_id, packs[1], p2["ids"])
        f = os.path.join(tmp, "pack-02.json")
        io.open(f, "w", encoding="utf-8").write(json.dumps(exp, ensure_ascii=False))
        r = subprocess.run([sys.executable, "src/validate_decisions.py", f,
                            "--locks-dir", locks],
                           capture_output=True, text=True, encoding="utf-8")
        check(r.returncode == 0, "pack-02 export VALIDATES against its own pack")
        check("pack-02" in (r.stdout + r.stderr), "validator names the pack it matched")

        # the same ids under a DIFFERENT pack's hash must not pass
        bad = dict(exp, content_hash=rb._stamped_hash(packs[2]))
        fb = os.path.join(tmp, "bad.json")
        io.open(fb, "w", encoding="utf-8").write(json.dumps(bad, ensure_ascii=False))
        r2 = subprocess.run([sys.executable, "src/validate_decisions.py", fb,
                            "--locks-dir", locks],
                            capture_output=True, text=True, encoding="utf-8")
        check(r2.returncode != 0, "pack-02 ids under pack-03's hash is REFUSED")

        # a foreign hash is refused and says the sheet is a packset
        alien = dict(exp, content_hash="sha256:" + "0" * 64)
        fa = os.path.join(tmp, "alien.json")
        io.open(fa, "w", encoding="utf-8").write(json.dumps(alien, ensure_ascii=False))
        r3 = subprocess.run([sys.executable, "src/validate_decisions.py", fa,
                            "--locks-dir", locks],
                            capture_output=True, text=True, encoding="utf-8")
        check(r3.returncode != 0, "an unknown content_hash is REFUSED")
        check("packset" in (r3.stdout + r3.stderr),
              "the refusal explains that this sheet is a packset")

        # idempotent re-lock of the same packset is allowed
        rb.write_packset_lock(sheet_id, parent, packs, "2026-08-18", locks_dir=locks)
        check(True, "re-locking the identical packset is allowed")

        # a CHANGED packset collides instead of silently rebinding (H1703)
        out2 = render_review_sheet_packset(_items(22), _config(sheet_id),
                                           screening=_screening(22),
                                           hub_name="different")
        packs2 = [rb.stamp(p)[0] for p in out2["packs"]]
        parent2 = out2["parent"]
        changed = rb.packset_hash([rb._stamped_hash(p) for p in packs2]) \
            != lock["packset"]["packset_hash"]
        if changed:
            try:
                rb.write_packset_lock(sheet_id, parent2, packs2, "2026-08-18",
                                      locks_dir=locks)
                check(False, "a re-cut packset COLLIDES")
            except rb.LockCollision:
                check(True, "a re-cut packset COLLIDES")
        else:
            # hub_name only moves the parent, so force a real pack change instead
            out3 = render_review_sheet_packset(_items(23), _config(sheet_id),
                                               screening=_screening(23))
            packs3 = [rb.stamp(p)[0] for p in out3["packs"]]
            parent3 = out3["parent"]
            try:
                rb.write_packset_lock(sheet_id, parent3, packs3, "2026-08-18",
                                      locks_dir=locks)
                check(False, "a re-cut packset COLLIDES")
            except rb.LockCollision:
                check(True, "a re-cut packset COLLIDES")

        # converting a SINGLE-FILE locked sheet into a packset must collide
        single_id = "h3098-was-single"
        from csl_pyutil import render_review_sheet
        solo = render_review_sheet(_items(22), _config(single_id),
                                   screening=_screening(22))
        solo, solo_hash = rb.stamp(solo)
        rb.write_lock(single_id, solo_hash, ["P%03d" % i for i in range(1, 23)],
                      "2026-08-18", locks_dir=locks)
        out_s = render_review_sheet_packset(_items(22), _config(single_id),
                                            screening=_screening(22))
        packs_s = [rb.stamp(p)[0] for p in out_s["packs"]]
        try:
            rb.write_packset_lock(single_id, out_s["parent"], packs_s, "2026-08-18",
                                  locks_dir=locks)
            check(False, "single-file -> packset conversion COLLIDES")
        except rb.LockCollision as e:
            check("SINGLE-FILE" in str(e), "single-file -> packset conversion COLLIDES")
        rb.write_packset_lock(single_id, out_s["parent"], packs_s, "2026-08-18",
                              locks_dir=locks, force=True)
        check(True, "…and force=True performs the deliberate conversion")

        # a pack that declares a different sheet_id is refused
        try:
            other = render_review_sheet_packset(_items(22), _config("someone-else"),
                                                screening=_screening(22))
            rb.write_packset_lock(sheet_id, parent,
                                  [rb.stamp(p)[0] for p in other["packs"]],
                                  "2026-08-18", locks_dir=locks, force=True)
            check(False, "a pack with a foreign sheet_id is refused")
        except ValueError as e:
            check("sheet_id" in str(e), "a pack with a foreign sheet_id is refused")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILS:
        print("packset binding selftest FAILED: %s" % ", ".join(FAILS))
        return 1
    print("packset binding selftest OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
