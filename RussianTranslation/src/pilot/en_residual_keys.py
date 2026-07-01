#!/usr/bin/env python
"""Print the residual (no-English) selected_keys for a root's EN store.

  python src/pilot/en_residual_keys.py <root>

A key is "done" iff its card has >=1 record with >=1 sense carrying a non-empty
`english`. Prints comma-joined missing keys (LF, no trailing CR) to stdout so a
requeue can `--keys="$(python ... <root>)"`. Empty output => root at 100%.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


def missing(root):
    path = os.path.join(REPO, f"wf_output.en.{root}.json")
    if not os.path.exists(path):
        sys.exit(f"no store: {path}")
    d = json.load(open(path, encoding="utf-8"))
    have = set()
    for e in d["results"]:
        c = e.get("card")
        if c and c.get("records") and any(
            any(s.get("english") for s in r.get("senses", []))
            for r in c["records"]
        ):
            have.add(e["key"])
    return [k for k in d["meta"]["selected_keys"] if k not in have]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: en_residual_keys.py <root>")
    print(",".join(missing(sys.argv[1])), end="")
