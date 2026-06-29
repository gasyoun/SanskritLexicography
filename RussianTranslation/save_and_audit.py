#!/usr/bin/env python
"""save_and_audit.py ROOT TASK_OUTPUT_FILE
   Saves workflow result to wf_output.sc.ROOT.json, then audits it.
   Usage: python save_and_audit.py yA C:\...\tasks\TASKID.output
"""
import json, sys, subprocess, os
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

root = sys.argv[1]
task_file = sys.argv[2]

with open(task_file, encoding="utf-8") as f:
    wrapper = json.load(f)
result = wrapper.get("result")
if isinstance(result, str):
    result = json.loads(result)

out_path = f"wf_output.sc.{root}.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False)

cards = result.get("results", [])
null_count = sum(1 for r in cards if not r.get("card"))
print(f"Saved {out_path}: {len(cards)} cards, {null_count} null")
