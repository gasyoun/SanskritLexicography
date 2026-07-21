#!/usr/bin/env python
"""Print the residual (not-fully-English) selected_keys for a root's EN store.

  python src/pilot/en_residual_keys.py <root>

A key is "done" iff EVERY translation slot in its card carries a non-empty
`english` — coverage-complete, not merely ">=1 English sense". The old ">=1"
rule counted a 1/40-sense card as done and hid 39 untranslated senses (FL4).
The coverage-complete rule now lives in the shared, --lang-parameterized kernel
`card_coverage.card_done(card, field)` (H1425 W1), so a fix to it reaches any
language that calls it; this CLI is the field='english' consumer. Prints
comma-joined missing keys (LF, no trailing CR) to stdout so a requeue can
`--keys="$(python ... <root>)"`. Empty output => root at 100%.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from card_coverage import card_done  # noqa: E402  (shared FL4 slot-coverage kernel)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


def missing(root):
    path = os.path.join(REPO, f"wf_output.en.{root}.json")
    if not os.path.exists(path):
        sys.exit(f"no store: {path}")
    d = json.load(open(path, encoding="utf-8"))
    have = {e["key"] for e in d["results"] if card_done(e.get("card"), "english")}
    return [k for k in d["meta"]["selected_keys"] if k not in have]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: en_residual_keys.py <root>")
    print(",".join(missing(sys.argv[1])), end="")
