#!/usr/bin/env python3
"""H5263 — 0-call proof that the NKRYa evidence block reaches the c1 prompt.

Builds a production-shaped one-card execution manifest, injects the C07 corpus facts
from the COMMITTED `pwg_ru/nkrya_cache` (offline, no token, no paid call), and writes the
prompt diff report the handoff asks for as step 1.

  python tools/h5263_prompt_evidence_probe.py --out reports/H5263_prompt_evidence_diff.json
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "src")
for path in (SRC, os.path.join(SRC, "pilot")):
    if path not in sys.path:
        sys.path.insert(0, path)

import nkrya_client as nk  # noqa: E402
import nkrya_evidence_card as card  # noqa: E402
import nkrya_prompt_evidence as npe  # noqa: E402

CACHE = os.path.join(os.path.dirname(HERE), "pwg_ru", "nkrya_cache")
HEADS = "туча:S,облако:S"
# The C07 card's five candidates — «последовательный» is deliberately absent, exactly as
# in the card: it was never queried, so it is not in the committed cache either.
CANDIDATES = ("связный:A,сплочённый:A,сплошной:A,"
              "сгущающийся=сгущаться:V,сомкнутый=сомкнуть:V")
KEY = "meGa"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def manifest():
    """The production prompt shape (headless_worker.build_prompt), one card."""
    return {
        "schema": "pwg.headless_execution_manifest.v1",
        "meta": {"root": "h5263-probe", "lang": "ru", "selected_keys": [KEY]},
        "field": "russian", "model": "claude-sonnet-5",
        "prompt": {"preamble": "PREAMBLE\n", "translation": "TRANSLATION RULES\n",
                   "grammar": "WINDOW GRAMMAR\n", "grammars": {}, "nws_rule": ""},
        "inputs": {KEY: {"skeleton": "{T1} Wolke", "portrait": "{}",
                         "ls": 0, "sk": 0, "nws": 0}},
        "suggestions": {},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    cli = nk.NkryaClient(cache_dir=CACHE, offline=True)
    evidence = npe.build_evidence(cli, card.parse_items(HEADS),
                                  card.parse_items(CANDIDATES))
    before = manifest()
    after = npe.inject(manifest(), KEY, evidence)
    report = npe.prompt_diff(before, after, [KEY])
    report["paid_calls"] = 0
    report["nkrya_live_calls"] = 0
    report["cache_entries_used"] = evidence["cache_keys"]
    report["block"] = npe.render_block(evidence)
    report["heads"] = HEADS
    report["candidates"] = CANDIDATES

    out = a.out if os.path.isabs(a.out) else os.path.join(os.path.dirname(HERE), a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(report["block"])
    print("\n%d cache entries, 0 live NKRYa calls, 0 paid c1 calls" % len(evidence["cache_keys"]))
    print("prompt bytes %d -> %d (delta %+d) -> %s"
          % (report["bytes_before"], report["bytes_after"], report["delta_bytes"], out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
