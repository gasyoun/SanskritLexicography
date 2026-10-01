#!/usr/bin/env python3
"""H3144 parity re-stamp: add the plan-mode TASK SHAPE ledger entry, then refresh the
verified_sha256 values that moved because this fix touched two widely-referenced files.

Same class as `h2254_parity_restamp.py` / `h2504_parity_restamp.py` — meta-tooling kept as
the receipt for a documented review. It never translates, audits, gates, promotes, or
touches the store; it edits LANG_PARITY.md and shells out to lang_parity_check.py.

WHY the mass re-stamp is honest here. The H3144 fix (MG ruling, option B) adds a
language-neutral TASK SHAPE block to `gen_opt_harness2.MASK_PREAMBLE` and one selftest that
pins it. `MASK_PREAMBLE` feeds BOTH lanes through the same
`.replace('`russian`', '`%s`' % field)` call, and the added text names no target field, no
language, and no lang-branching behaviour. So every existing SHARED verdict that merely
references `gen_opt_harness2.py` or `window_selftest.py` still holds unchanged — what moved
is the file hash, not the parity semantics.
"""
import hashlib
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_restamp as pr  # noqa: E402

ROOT = pr.ROOT                                     # .../RussianTranslation

ENTRY_ID = "plan_mode_task_shape_preamble_h3144"
TRACKED = [
    "src/pilot/gen_opt_harness2.py",
    "src/pilot/window_selftest.py",
]
NOTE = (
    "H3144 (19-08-2026, Opus 5 `claude-opus-5`): the production spawn passes "
    "`--permission-mode plan` together with `--json-schema`. On 19-08-2026 the c1 canary "
    "returned a null card reported as `malformed_output: … Expecting value: line 1 column 1 "
    "(char 0)`; the CLI session transcript shows the model DECLINED to emit structured output "
    "on plan-mode grounds (\"the tools that workflow expects me to end with (AskUserQuestion, "
    "ExitPlanMode) aren't even available to me in this session\"), refused again against the "
    "CLI's own `[structured-output-enforce]` retry, and the harness then fell back to the prose "
    "in `result`. The call billed in full. MG ruled option B — keep plan mode, reframe the "
    "prompt — the same fix H994 applied to the health probe on 15-07-2026. The new TASK SHAPE "
    "block opens `MASK_PREAMBLE`, which both lanes consume via the same "
    "`.replace('`russian`', field)` call; it names no target field, no language and no "
    "lang-branching behaviour, so it reaches RU and EN identically by construction. "
    "`test_mask_preamble_carries_task_shape` pins the block's presence and forbids "
    "reintroducing the bare tool-demand shape the model refused twice. Uprava FINDINGS §498."
)
TRACKING = ("https://github.com/gasyoun/Uprava/blob/main/handoffs/"
            "H3144-Opus_SanskritLexicography_h858-residual-c1-window-after-canary-nogo_19.08.26.md")


def sha256_of(rel_path):
    return hashlib.sha256((ROOT / rel_path).read_bytes()).hexdigest()


def add_entry():
    text, start, end, entries = pr.load_ledger()
    if any(e.get("id") == ENTRY_ID for e in entries):
        print("ledger entry %s already present" % ENTRY_ID)
        return False
    entries.append({
        "id": ENTRY_ID,
        "mechanism": (
            "Plan-mode-compatible TASK SHAPE block at the head of "
            "gen_opt_harness2.MASK_PREAMBLE, so a headless `claude -p --json-schema "
            "--permission-mode plan` call does not refuse to emit structured output; pinned by "
            "window_selftest.test_mask_preamble_carries_task_shape"
        ),
        "files": list(TRACKED),
        "languages": ["ru", "en"],
        "verdict": "SHARED",
        "note": NOTE,
        "tracking": TRACKING,
        "verified_sha256": {rel: sha256_of(rel) for rel in TRACKED},
    })
    pr.write_ledger(text, start, end, entries)
    print("added ledger entry %s" % ENTRY_ID)
    return True


def main():
    add_entry()
    sys.exit(pr.finish(pr.drifted_ids()))


if __name__ == "__main__":
    raise SystemExit(main())
