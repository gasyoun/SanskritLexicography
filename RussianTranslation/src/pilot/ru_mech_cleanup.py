#!/usr/bin/env python
r"""RU mechanical cleanup driver.

This does the local, deterministic part of the RU cleanup plan:

  python src/pilot/ru_mech_cleanup.py stale-refresh
  python src/pilot/ru_mech_cleanup.py priority-requeues
  python src/pilot/ru_mech_cleanup.py coverage-catchup
  python src/pilot/ru_mech_cleanup.py all

It intentionally does NOT claim to translate anything. It runs local status/audit
commands, writes per-root queue snapshots, and generates named Max Workflow
harnesses. Run those harnesses in Max, then merge results with save_and_audit.py
--merge and re-audit.
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)
OUT = os.path.join(HERE, "output")
QUEUE_DIR = os.path.join(OUT, "ru_cleanup_queues")
LOG = os.path.join(OUT, "ru_cleanup_driver_log.json")
MANIFEST = os.path.join(OUT, "ru_cleanup_manifest.json")

sys.path.insert(0, SRC)
from safe_filename import safe_name  # noqa: E402

STALE_SC_ROOTS = ["Ap", "As", "car", "gam", "jan", "ji", "jYA", "laB", "muc", "vah", "vas", "viS"]

# Plan priority order: quick wins, coverage blockers, then biggest defect buckets.
PRIORITY_REQUEUES = [
    ("sd", "ji"),
    ("sc", "hi"),
    ("sc", "naS"),
    ("sc", "pA"),
    ("sc", "rakz"),
    ("sc", "Sam"),
    ("sc", "vraj"),
    ("sd", "laB"),
    ("sc", "nI"),
    ("sc", "han"),
    ("sc", "yA"),
    ("sd", "dA"),
    ("sc", "pat"),
    ("sd", "mA"),
    ("sd", "car"),
    ("sd", "vas"),
]

COVERAGE_ROOTS = ["As", "Ap", "ji", "laB"]
LOW_DEFECT_ROOTS = {("sd", "ji"), ("sc", "hi"), ("sc", "naS"), ("sc", "pA"),
                    ("sc", "rakz"), ("sc", "Sam"), ("sc", "vraj"), ("sd", "laB")}


def run(cmd, ok=(0,)):
    p = subprocess.run(cmd, cwd=REPO, text=True, encoding="utf-8", capture_output=True)
    row = {
        "cmd": cmd,
        "returncode": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }
    if p.returncode not in ok:
        row["error"] = "unexpected return code"
    return row


def ensure_dirs():
    os.makedirs(QUEUE_DIR, exist_ok=True)


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read_keys(path):
    if not os.path.exists(path):
        return []
    return [ln.strip() for ln in open(path, encoding="utf-8") if ln.strip()]


def harness_out(tag, root, kind):
    return os.path.join(HERE, "run_pilot_wf.%s_%s_%s.js" % (tag, safe_name(root), kind))


def gen_harness(root, tag, kind, keys=None):
    out = harness_out(tag, root, kind)
    cmd = [sys.executable, os.path.join(HERE, "gen_opt_harness2.py"), root, "--out=" + out]
    if keys:
        cmd.insert(3, "--keys=" + ",".join(keys))
    res = run(cmd)
    res["harness"] = out
    res["key_count"] = len(keys or [])
    return res


def root_key_count(root):
    for stem in (safe_name(root), root):
        path = os.path.join(HERE, "input", stem + ".rootmap.json")
        if os.path.exists(path):
            try:
                return len((json.load(open(path, encoding="utf-8")).get("sub_cards") or []))
            except (OSError, json.JSONDecodeError):
                return None
    return None


def stale_refresh():
    rows = []
    for root in STALE_SC_ROOTS:
        status = run([sys.executable, os.path.join(HERE, "root_window_status.py"), root], ok=(0, 1))
        status_path = os.path.join(QUEUE_DIR, "sc.%s.status.txt" % safe_name(root))
        write_text(status_path, status["stdout"] + status["stderr"])
        row = {"root": root, "status_path": status_path, "status": status}
        if status["returncode"] != 0:
            row["state"] = "blocked"
            row["blocked_reason"] = "root_window_status failed; no refresh harness generated"
            rows.append(row)
            print("stale-refresh %-5s status_rc=%s BLOCKED; no harness generated" % (
                root, status["returncode"]))
            continue
        gen = gen_harness(root, "sc", "refresh")
        row.update({"state": "generated", "generate": gen})
        rows.append(row)
        print("stale-refresh %-5s status_rc=0 harness=%s" % (
            root, os.path.relpath(gen["harness"], REPO)))
    return rows


def audit_for_requeue(tag, root):
    wf = os.path.join(REPO, "wf_output.%s.%s.json" % (tag, root))
    res = run([sys.executable, os.path.join(HERE, "audit_window.py"), wf, "--root", root, "--write-requeue"],
              ok=(0, 1, 2))
    return res


def snapshot_queue(tag, root, kind, keys):
    path = os.path.join(QUEUE_DIR, "%s.%s.%s.keys.txt" % (tag, safe_name(root), kind))
    write_text(path, "".join(k + "\n" for k in keys))
    return path


def priority_requeues():
    rows = []
    for tag, root in PRIORITY_REQUEUES:
        audit = audit_for_requeue(tag, root)
        root_row = {"tag": tag, "root": root, "audit": audit, "queues": []}
        if audit["returncode"] == 2:
            print("requeue %-2s %-5s stale/refused; no requeue harness" % (tag, root))
            rows.append(root_row)
            continue
        for kind, filename in (
            ("transient", "requeue.transient.keys.txt"),
            ("defect", "requeue.defect.keys.txt"),
        ):
            keys = read_keys(os.path.join(OUT, filename))
            qpath = snapshot_queue(tag, root, kind, keys)
            qrow = {"kind": kind, "queue_path": qpath, "key_count": len(keys)}
            if keys:
                qrow["generate"] = gen_harness(root, tag, kind, keys)
                print("requeue %-2s %-5s %-9s keys=%-3d harness=%s" % (
                    tag, root, kind, len(keys),
                    os.path.relpath(qrow["generate"]["harness"], REPO)))
            else:
                print("requeue %-2s %-5s %-9s keys=0" % (tag, root, kind))
            root_row["queues"].append(qrow)
        rows.append(root_row)
    return rows


def coverage_catchup():
    rows = []
    for root in COVERAGE_ROOTS:
        res = run([sys.executable, os.path.join(HERE, "ru_coverage.py"), "--keys", safe_name(root)], ok=(0,))
        if res["returncode"] != 0:
            qpath = snapshot_queue("sc", root, "coverage", [])
            row = {"root": root, "coverage": res, "queue_path": qpath,
                   "key_count": 0, "state": "blocked",
                   "blocked_reason": "ru_coverage.py --keys failed; no coverage harness generated"}
            print("coverage %-5s status_rc=%s BLOCKED; no harness generated" % (
                root, res["returncode"]))
            rows.append(row)
            continue
        keys = [k for k in res["stdout"].strip().split(",") if k]
        qpath = snapshot_queue("sc", root, "coverage", keys)
        row = {"root": root, "coverage": res, "queue_path": qpath,
               "key_count": len(keys), "state": "generated" if keys else "clean"}
        if keys:
            row["generate"] = gen_harness(root, "sc", "coverage", keys)
            print("coverage %-5s keys=%-3d harness=%s" % (
                root, len(keys), os.path.relpath(row["generate"]["harness"], REPO)))
        else:
            print("coverage %-5s keys=0" % root)
        rows.append(row)
    return rows


def write_log(payload):
    payload["generated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    stale_rows = payload.get("stale_refresh") or []
    coverage_rows = payload.get("coverage_catchup") or []
    payload["summary"] = {
        "blocked_stale_roots": [r["root"] for r in stale_rows if r.get("state") == "blocked"],
        "blocked_coverage_roots": [r["root"] for r in coverage_rows if r.get("state") == "blocked"],
        "generated_harnesses": sum(
            1 for section in ("stale_refresh", "coverage_catchup")
            for r in (payload.get(section) or []) if r.get("generate")) + sum(
            1 for r in (payload.get("priority_requeues") or [])
            for q in (r.get("queues") or []) if q.get("generate")),
    }
    os.makedirs(OUT, exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("log: %s" % os.path.relpath(LOG, REPO))


def rel(path):
    return os.path.relpath(path, REPO)


def task_output_path(tag, root, kind):
    return os.path.join(OUT, "task_output.%s_%s_%s.json" % (tag, safe_name(root), kind))


def manifest_item(root, tag, kind, key_count, harness_path, keys_path=None, priority_group=""):
    task_path = task_output_path(tag, root, kind)
    wf_name = "wf_output.%s.%s.json" % (tag, root)
    save_flags = "--force" if kind == "refresh" else "--merge"
    return {
        "root": root,
        "safe_root": safe_name(root),
        "tag": tag,
        "kind": kind,
        "key_count": key_count,
        "keys_path": rel(keys_path) if keys_path else None,
        "harness_path": rel(harness_path),
        "expected_task_output": rel(task_path),
        "expected_wf_output": wf_name,
        "save_command": "python save_and_audit.py %s %s %s %s" %
                        (root, rel(task_path), tag, save_flags),
        "audit_command": "python src\\pilot\\audit_window.py %s --root %s --write-requeue" %
                         (wf_name, root),
        "promotion_command": "python src\\promote_final_cards.py --glob \"%s\" --merge" % wf_name,
        "priority_group": priority_group,
    }


def build_manifest(payload):
    items = []
    for row in payload.get("priority_requeues") or []:
        tag, root = row["tag"], row["root"]
        for q in row.get("queues") or []:
            gen = q.get("generate")
            if not gen:
                continue
            kind = q["kind"]
            group = "transient" if kind == "transient" else (
                "low_defect_quick_win" if (tag, root) in LOW_DEFECT_ROOTS else "large_defect")
            items.append(manifest_item(root, tag, kind, q["key_count"], gen["harness"],
                                       keys_path=q.get("queue_path"), priority_group=group))
    for row in payload.get("coverage_catchup") or []:
        gen = row.get("generate")
        if gen:
            items.append(manifest_item(row["root"], "sc", "coverage", row["key_count"],
                                       gen["harness"], keys_path=row.get("queue_path"),
                                       priority_group="coverage_blocker"))
    for row in payload.get("stale_refresh") or []:
        gen = row.get("generate")
        if gen:
            items.append(manifest_item(row["root"], "sc", "refresh",
                                       root_key_count(row["root"]), gen["harness"],
                                       keys_path=None, priority_group="stale_refresh"))
    order = {"transient": 0, "low_defect_quick_win": 1, "coverage_blocker": 2,
             "stale_refresh": 3, "large_defect": 4}
    items.sort(key=lambda r: (order.get(r["priority_group"], 99), r["key_count"] or 0,
                              r["tag"], r["safe_root"], r["kind"]))
    return {
        "generated_at": payload.get("generated_at"),
        "max_concurrency": 3,
        "items": items,
        "summary": {
            "item_count": len(items),
            "priority_order": ["transient", "low_defect_quick_win", "coverage_blocker",
                               "stale_refresh", "large_defect"],
        },
    }


def write_manifest(payload):
    manifest = build_manifest(payload)
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("manifest: %s" % rel(MANIFEST))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["stale-refresh", "priority-requeues", "coverage-catchup", "all"])
    args = ap.parse_args()
    ensure_dirs()
    payload = {"mode": args.mode}
    if args.mode in ("stale-refresh", "all"):
        payload["stale_refresh"] = stale_refresh()
    if args.mode in ("priority-requeues", "all"):
        payload["priority_requeues"] = priority_requeues()
    if args.mode in ("coverage-catchup", "all"):
        payload["coverage_catchup"] = coverage_catchup()
    write_log(payload)
    write_manifest(payload)


if __name__ == "__main__":
    main()
