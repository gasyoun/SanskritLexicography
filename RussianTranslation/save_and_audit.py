#!/usr/bin/env python
r"""Save a Workflow task-output JSON to wf_output.<tag>.<root>.json, then audit it.

  python save_and_audit.py <root> <task_output_file> [tag] [--no-audit]

tag defaults to 'sc' (Slice C); pass 'sd' etc. for other slices — the tag used to
be hard-coded to 'sc', which silently misfiled every non-sc slice. With audit on
(the default) it shells to src/pilot/audit_window.py and prints the gate summary,
so the script name is honest; pass --no-audit to save only (the bulk-save case).
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    positional = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(positional) < 2:
        sys.exit("usage: python save_and_audit.py <root> <task_output_file> [tag] [--no-audit]")
    root, task_file = positional[0], positional[1]
    tag = positional[2] if len(positional) > 2 else "sc"

    with open(task_file, encoding="utf-8") as f:
        wrapper = json.load(f)
    result = wrapper.get("result")
    if isinstance(result, str):
        result = json.loads(result)
    if result is None:                      # direct (non-wrapped) workflow result
        result = wrapper

    out_path = os.path.join(HERE, f"wf_output.{tag}.{root}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    cards = result.get("results", [])
    null_count = sum(1 for r in cards if not r.get("card"))
    print(f"Saved {out_path}: {len(cards)} cards, {null_count} null")

    if "--no-audit" in flags:
        return
    audit = os.path.join(HERE, "src", "pilot", "audit_window.py")
    if not os.path.exists(audit):
        print("(audit_window.py not found — saved only)")
        return
    p = subprocess.run([sys.executable, audit, out_path, "--root", root],
                       text=True, encoding="utf-8")
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
