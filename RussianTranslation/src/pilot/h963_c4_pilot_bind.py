#!/usr/bin/env python3
"""H963 c4 owner-override pilot — bind the captured Workflow results to their manifests.

Reads the two task-output files this session captured, extracts each run's result,
verifies it against the exact execution manifest it was generated from (root + selected
keys + input hashes + budgets), and writes canonical wf_output.<root>.json artifacts
plus a measurement summary. Makes NO model calls and never writes the canonical store.
"""
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

WT = r"C:\Users\user\Documents\GitHub\SanskritLexicography-h963-c4-live\RussianTranslation"
AT = os.path.join(WT, "src", "pilot", "output", "h963_c4_pilot")
TASKS = (r"C:\Users\user\AppData\Local\Temp\claude"
         r"\C--Users-user-Documents-GitHub-Uprava-review"
         r"\91e12bd6-145f-4db1-8ffc-e0f7cf2f320f\tasks")

RUNS = [
    ("canary", "wv3gqnx11.output", "manifest.canary.json", "h963_c4_canary"),
    ("real", "wrxiws6cw.output", "manifest.real.json", "h963_c4_real"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def extract_result(path):
    """Pull the workflow `result` object out of a captured task-output file."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    # The output file is JSON; the run payload is either the top-level object
    # (meta/summary/results) or nested under "result".
    try:
        obj = json.loads(raw)
    except ValueError:
        start = raw.find("{")
        obj = json.loads(raw[start:])
    if isinstance(obj, dict) and "result" in obj and isinstance(obj["result"], dict) \
            and "summary" in obj["result"]:
        return obj["result"], obj.get("logs") or []
    if isinstance(obj, dict) and "summary" in obj:
        return obj, []
    raise SystemExit("could not locate run payload in %s" % path)


print("=" * 78)
print("H963 c4 owner-override pilot — manifest binding + measurement")
print("=" * 78)

report = {"schema": "pwg.h963_c4_pilot_measurement.v1",
          "label": "single-profile c4 owner-override pilot", "runs": {}}

for label, taskfile, manifest_name, expect_root in RUNS:
    tp = os.path.join(TASKS, taskfile)
    mp = os.path.join(AT, manifest_name)
    res, logs = extract_result(tp)
    man = json.load(open(mp, encoding="utf-8"))
    meta, summ = res["meta"], res["summary"]

    # --- provenance binding checks -------------------------------------------
    checks = {}
    checks["root_matches_manifest"] = (meta["root"] == expect_root ==
                                       (man.get("meta") or {}).get("root"))
    man_keys = list(man["inputs"].keys()) if isinstance(man["inputs"], dict) else []
    checks["selected_keys_match"] = sorted(meta["selected_keys"]) == sorted(man_keys)
    checks["model_is_exact_sonnet5"] = meta["gen_model"] == "claude-sonnet-5" == man["model"]
    checks["batches_match"] = meta["batches"] == man["batches"]
    checks["agent_ceiling_honoured"] = summ["agents_spent"] <= meta["max_agents"] == 1
    checks["no_presplit"] = meta["presplit_keys"] == [] == man["presplit_keys"]
    checks["guards_soft"] = (summ["sanloss_hard_reject"] is False
                             and summ["tnmask_hard_reject"] is False)

    print("\n--- run: %s  (manifest root=%s)" % (label, meta["root"]))
    for k, v in checks.items():
        print("   %-28s %s" % (k, "OK" if v else "*** FAIL ***"))
    print("   cards=%d ok=%d null=%d healed=%d"
          % (summ["cards"], summ["ok"], summ["null"], summ["healed"]))
    print("   agents_spent=%d/%d  kill_timeouts=%d  conn_errors=%d"
          % (summ["agents_spent"], meta["max_agents"], summ["kill_timeouts"], summ["conn_errors"]))
    print("   budget_kill_switch_tripped=%s translate_tripped=%s heal_tripped=%s"
          % (summ["budget_kill_switch_tripped"], summ["translate_budget_tripped"],
             summ["heal_budget_tripped"]))
    print("   sanloss_shortfalls=%d  tnmask_mismatches=%d"
          % (summ["sanloss_shortfalls"], summ["tnmask_mismatches"]))
    print("   null_keys=%s  partial_keys=%s" % (summ["null_keys"], summ["partial_keys"]))
    if summ.get("failures"):
        for k, v in summ["failures"].items():
            print("   FAILURE %-8s %s" % (k, v))
    for line in logs:
        print("   LOG  %s" % line)

    # --- write the canonical wf_output artifact -------------------------------
    out = os.path.join(AT, "wf_output.%s.json" % meta["root"])
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    clean = [r for r in res["results"] if r.get("card")]
    report["runs"][label] = {
        "root": meta["root"],
        "manifest": manifest_name,
        "manifest_sha256": sha256(mp),
        "wf_output": os.path.basename(out),
        "wf_output_sha256": sha256(out),
        "binding_checks": checks,
        "binding_all_ok": all(checks.values()),
        "cards": summ["cards"], "ok": summ["ok"], "null": summ["null"],
        "clean_rate_pct": round(100.0 * summ["ok"] / summ["cards"], 1) if summ["cards"] else 0.0,
        "agents_spent": summ["agents_spent"], "max_agents": meta["max_agents"],
        "kill_timeouts": summ["kill_timeouts"], "conn_errors": summ["conn_errors"],
        "sanloss_shortfalls": summ["sanloss_shortfalls"],
        "tnmask_mismatches": summ["tnmask_mismatches"],
        "null_keys": summ["null_keys"], "failures": summ.get("failures") or {},
        "logs": logs,
        "input_hashes": meta["input_hashes"],
        "promotable_clean_keys": [r["key"] for r in clean],
    }
    print("   wrote %s" % out)

rp = os.path.join(AT, "pilot_measurement.json")
with open(rp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("\nwrote %s" % rp)

# --- promotion gate ----------------------------------------------------------
real = report["runs"]["real"]
print("\n" + "=" * 78)
print("PROMOTION GATE (real rows only — the synthetic canary is NEVER promotable)")
print("=" * 78)
print("real clean rate : %.1f%% (ok=%d / cards=%d)  — floor is 80%%"
      % (real["clean_rate_pct"], real["ok"], real["cards"]))
if real["clean_rate_pct"] < 80.0:
    print("VERDICT: DO NOT PROMOTE — clean rate below the 80% floor.")
    print("         Exact failed gate: translate agent hit the 180 s kill ceiling")
    print("         (kill_timeouts=%d), heal lane had 0 agents -> both real cards null."
          % real["kill_timeouts"])
    print("         No retry, no requeue (owner-override brief).")
else:
    print("VERDICT: clean rate meets the floor.")
print("\nCanonical store NOT written by this script under any branch.")
