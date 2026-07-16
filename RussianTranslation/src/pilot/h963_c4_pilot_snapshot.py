#!/usr/bin/env python3
"""H963 c4 owner-override pilot — runtime-data inventory + snapshot into the isolated worktree.

Makes NO model calls and MUTATES NOTHING in the shared checkout: it only READS the
shared runtime files and COPIES them into an attempt-specific directory inside this
isolated worktree.

Why this is load-bearing (not belt-and-braces): `store_path.canonical_store()` resolves
a LINKED worktree's store to the MAIN checkout's real store by design (the H255 w06 /
H805 loss fix). Verified empirically from this worktree: unpinned it resolves to
`...\\SanskritLexicography\\RussianTranslation\\src\\pwg_ru_translated.jsonl`. So every
generation/audit step in this pilot MUST run with `PWG_RU_STORE` pinned to the scratch
copy this script creates; only the final, base-hash-verified promotion may target the
real store.
"""
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SHARED = r"C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation"
WT = r"C:\Users\user\Documents\GitHub\SanskritLexicography-h963-c4-live\RussianTranslation"
ATTEMPT = os.path.join(WT, "src", "pilot", "output", "h963_c4_pilot")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def stat_row(label, path, count_rows=False):
    if not os.path.exists(path):
        return {"label": label, "path": path, "present": False}
    st = os.stat(path)
    rec = {
        "label": label,
        "path": path,
        "present": True,
        "bytes": st.st_size,
        "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sha256": sha256(path),
    }
    if count_rows:
        rec["rows"] = rows(path)
    return rec


SOURCES = [
    ("canonical_store", os.path.join(SHARED, "src", "pwg_ru_translated.jsonl"), True),
    ("card_tm_ru", os.path.join(SHARED, "src", "pilot", "translation_memory.ru.json"), False),
    ("frag_tm_ru", os.path.join(SHARED, "src", "pilot", "translation_memory.frag.ru.jsonl"), True),
    ("suggest_tm_ru", os.path.join(SHARED, "src", "pilot", "translation_memory.suggest.ru.json"), False),
    ("residuals", os.path.join(SHARED, "src", "pilot", "no_pwg_residuals.jsonl"), True),
    ("rootmap_overrides", os.path.join(SHARED, "src", "pilot", "rootmap_overrides.json"), False),
    ("tm_source_weights", os.path.join(SHARED, "src", "tm_source_weights.json"), False),
]

os.makedirs(ATTEMPT, exist_ok=True)

print("=" * 78)
print("H963 c4 owner-override pilot — runtime-data inventory (READ-ONLY on shared)")
print("=" * 78)
print("stamped (UTC): %s" % datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
print("attempt dir  : %s" % ATTEMPT)
print()

inventory = []
for label, path, cr in SOURCES:
    rec = stat_row(label, path, cr)
    inventory.append(rec)
    if rec["present"]:
        extra = " rows=%d" % rec["rows"] if "rows" in rec else ""
        print("%-18s %10d B%s  mtime=%s" % (label, rec["bytes"], extra, rec["mtime_utc"]))
        print("%-18s sha256=%s" % ("", rec["sha256"]))
    else:
        print("%-18s ABSENT (%s)" % (label, path))
    print()

store_rec = inventory[0]
if not store_rec.get("present"):
    print("ABORT: canonical store absent — cannot establish an optimistic-concurrency base.")
    raise SystemExit(2)

# --- the optimistic-concurrency base -----------------------------------------
BASE_HASH = store_rec["sha256"]
BASE_ROWS = store_rec["rows"]
print("-" * 78)
print("OPTIMISTIC-CONCURRENCY BASE")
print("  store rows   : %d" % BASE_ROWS)
print("  store sha256 : %s" % BASE_HASH)
print("-" * 78)

# --- copy runtime inputs into the isolated worktree ---------------------------
copies = {}
scratch_store = os.path.join(ATTEMPT, "store_scratch.jsonl")
shutil.copy2(store_rec["path"], scratch_store)
copies["store_scratch"] = stat_row("store_scratch", scratch_store, True)
print("\ncopied store -> scratch promotion target")
print("  %s" % scratch_store)
print("  rows=%d sha256=%s" % (copies["store_scratch"]["rows"], copies["store_scratch"]["sha256"]))
if copies["store_scratch"]["sha256"] != BASE_HASH:
    print("ABORT: scratch copy hash != base hash (torn copy)")
    raise SystemExit(2)
print("  scratch copy is byte-identical to base OK")

# TM + residuals into the worktree's own tree so --tm=auto finds them locally.
for label, dest_rel in (
        ("card_tm_ru", os.path.join("src", "pilot", "translation_memory.ru.json")),
        ("frag_tm_ru", os.path.join("src", "pilot", "translation_memory.frag.ru.jsonl")),
        ("suggest_tm_ru", os.path.join("src", "pilot", "translation_memory.suggest.ru.json")),
        ("residuals", os.path.join("src", "pilot", "no_pwg_residuals.jsonl")),
        ("rootmap_overrides", os.path.join("src", "pilot", "rootmap_overrides.json")),
        ("tm_source_weights", os.path.join("src", "tm_source_weights.json")),
):
    src = next(r for r in inventory if r["label"] == label)
    if not src.get("present"):
        print("  skip %-16s (absent upstream)" % label)
        continue
    dest = os.path.join(WT, dest_rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(src["path"], dest)
    ok = sha256(dest) == src["sha256"]
    print("  copied %-16s -> %s  [%s]" % (label, dest_rel, "hash OK" if ok else "HASH MISMATCH"))
    if not ok:
        raise SystemExit(2)

manifest = {
    "schema": "pwg.h963_c4_pilot_runtime_snapshot.v1",
    "stamped_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "handoff": "H963",
    "label": "single-profile c4 owner-override pilot",
    "shared_checkout": SHARED,
    "worktree": WT,
    "attempt_dir": ATTEMPT,
    "optimistic_concurrency_base": {"store_rows": BASE_ROWS, "store_sha256": BASE_HASH},
    "sources": inventory,
    "scratch_store": copies["store_scratch"],
}
mpath = os.path.join(ATTEMPT, "runtime_snapshot_manifest.json")
with open(mpath, "w", encoding="utf-8", newline="\n") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)
print("\nwrote runtime snapshot manifest: %s" % mpath)
print("\nSNAPSHOT OK — no shared file was modified; zero model calls made.")
