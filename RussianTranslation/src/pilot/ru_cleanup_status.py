#!/usr/bin/env python
r"""Read-only RU cleanup operator dashboard.

Usage:
  python src/pilot/ru_cleanup_status.py
  python src/pilot/ru_cleanup_status.py --json
"""
import argparse
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)
OUT = os.path.join(HERE, "output")
MANIFEST = os.path.join(OUT, "ru_cleanup_manifest.json")
WINDOW_STATUS = os.path.join(OUT, "window_status.json")


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def rel(path):
    return os.path.relpath(path, REPO)


def abs_repo(path):
    return path if os.path.isabs(path) else os.path.join(REPO, path)


def matching_window_status(wf_name):
    status = load_json(WINDOW_STATUS, default={}) or {}
    wf = status.get("workflow") or status.get("workflow_path") or ""
    if os.path.basename(wf) != os.path.basename(wf_name):
        return None
    return status


def row_state(item):
    harness = abs_repo(item["harness_path"])
    task = abs_repo(item["expected_task_output"])
    wf = abs_repo(item["expected_wf_output"])
    if not os.path.exists(harness):
        return "blocked", "missing harness"
    harness_mtime = os.path.getmtime(harness)
    task_fresh = os.path.exists(task) and os.path.getmtime(task) >= harness_mtime
    wf_fresh = os.path.exists(wf) and os.path.getmtime(wf) >= harness_mtime
    if not wf_fresh:
        if task_fresh:
            return "needs_save", "task output exists"
        return "needs_max", "run current manifest harness in Max"
    status = matching_window_status(item["expected_wf_output"])
    if not status:
        return "needs_audit", "workflow output exists"
    state = status.get("state") or ""
    requeue_count = status.get("requeue_count") or 0
    if state in ("stale_artifact", "blocked") or status.get("crashed"):
        return "blocked", state or "audit blocked"
    if requeue_count or state in ("needs_requeue", "transient_only"):
        return "needs_requeue", "%s requeue" % requeue_count
    if state == "clean":
        return "clean", "audit clean"
    return "needs_audit", state or "audit state unclear"


def coverage_summary():
    cmd = [sys.executable, os.path.join(HERE, "ru_coverage.py"), "--min", "90"]
    p = subprocess.run(cmd, cwd=REPO, text=True, encoding="utf-8", capture_output=True)
    lows = []
    for line in p.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 5 and parts[-1] == "LOW":
            lows.append(parts[0])
    return {
        "returncode": p.returncode,
        "below_min_roots": lows,
        "command": "python src\\pilot\\ru_coverage.py --min 90",
    }


def build_status(manifest_path=MANIFEST):
    manifest = load_json(manifest_path)
    if not manifest:
        raise SystemExit("no manifest found: %s" % rel(manifest_path))
    rows = []
    for item in manifest.get("items") or []:
        state, note = row_state(item)
        out = dict(item)
        out["state"] = state
        out["note"] = note
        rows.append(out)
    counts = {}
    for row in rows:
        counts[row["state"]] = counts.get(row["state"], 0) + 1
    return {
        "manifest": rel(manifest_path),
        "max_concurrency": manifest.get("max_concurrency"),
        "counts": counts,
        "coverage": coverage_summary(),
        "items": rows,
    }


def print_table(payload):
    print("RU cleanup status  (max concurrency <= %s)" % (payload.get("max_concurrency") or 3))
    counts = payload.get("counts") or {}
    print("counts: " + ", ".join("%s=%s" % (k, counts[k]) for k in sorted(counts)))
    cov = payload.get("coverage") or {}
    if cov.get("returncode"):
        print("coverage: below 90%% -> %s" % ", ".join(cov.get("below_min_roots") or []))
    else:
        print("coverage: >=90%% for tracked roots")
    print("")
    print("%-14s %-5s %-9s %-8s %5s %-14s %s" %
          ("state", "tag", "kind", "root", "keys", "priority", "next"))
    print("%-14s %-5s %-9s %-8s %5s %-14s %s" %
          ("-" * 14, "-" * 5, "-" * 9, "-" * 8, "-" * 5, "-" * 14, "-" * 24))
    for row in payload.get("items") or []:
        if row["state"] == "needs_max":
            nxt = row["harness_path"]
        elif row["state"] == "needs_save":
            nxt = row["save_command"]
        elif row["state"] == "needs_audit":
            nxt = row["audit_command"]
        elif row["state"] == "needs_requeue":
            nxt = row["audit_command"]
        elif row["state"] == "clean":
            nxt = row["promotion_command"]
        else:
            nxt = row["note"]
        print("%-14s %-5s %-9s %-8s %5s %-14s %s" %
              (row["state"], row["tag"], row["kind"], row["root"],
               row.get("key_count") if row.get("key_count") is not None else "",
               row["priority_group"], nxt))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=MANIFEST)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    payload = build_status(args.manifest)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
    else:
        print_table(payload)


if __name__ == "__main__":
    main()
