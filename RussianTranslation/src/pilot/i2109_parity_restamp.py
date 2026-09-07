#!/usr/bin/env python3
"""#2109 parity re-stamp: flip `gloss_wrapper_worked_example_localisation` GAP -> SHARED, then
refresh the verified_sha256 values that moved because the fix touched two widely-referenced
files.

Same class as `h3144_parity_restamp.py` / `h3500_parity_restamp.py` — meta-tooling kept as the
receipt for a documented review. It never translates, audits, gates, promotes, or touches the
store; it edits LANG_PARITY.md and shells out to lang_parity_check.py.

WHY the mass re-stamp is honest here. The fix keeps `MASK_PREAMBLE` as the RU rendering
(byte-identical to before, which is what the language-neutral readiness probe prepends) and
adds `mask_preamble(field)` — the same `.replace('`russian`', field)` parameterization both
call sites already used, plus a `GLOSS_WRAPPER_EXAMPLE[field]` substitution so each lane's
worked example is written in the language that lane must produce. No gate, schema, call-site
semantics or lang-branch behaviour changes; the selftest diff is test-only pins. So every
existing verdict that merely references `gen_opt_harness2.py` or `window_selftest.py` still
holds unchanged — what moved is the file hash, not the parity semantics.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]          # .../RussianTranslation
LEDGER = ROOT / "LANG_PARITY.md"
CHECK = ROOT / "src" / "pilot" / "lang_parity_check.py"
BLOCK_OPEN = "```json lang_parity_ledger"

ENTRY_ID = "gloss_wrapper_worked_example_localisation"
MECHANISM = (
    "The worked example inside the GLOSS WRAPPERS block is language-keyed next to `field` "
    "(GLOSS_WRAPPER_EXAMPLE[field], rendered by gen_opt_harness2.mask_preamble), so each lane "
    "is shown a demonstration in the language it must produce"
)
NOTE = (
    "#2109 (07-09-2026, Opus 5 `claude-opus-5`): closed as SHARED. The RULE was already shared "
    "(`gloss_wrapper_prompt_preservation_h4270`); its demonstration was not — "
    "`MASK_PREAMBLE.replace('`russian`', '`%s`' % field)` swapped the field NAME only, so an "
    "`--lang en` window read «becomes RU `а) {%некий%} …`» as the model example for the "
    "English output it was about to produce. The block now carries a `{{GLOSS_WRAPPER_EXAMPLE}}` "
    "slot filled from `GLOSS_WRAPPER_EXAMPLE[field]` by the new `mask_preamble(field)` helper, "
    "which both call sites (v2 execution manifest + generated JS harness) use in place of the "
    "raw `.replace()`. RU keeps the H4270 example verbatim and `MASK_PREAMBLE` stays "
    "byte-identical to its pre-fix text (so the lang-neutral readiness probe, which prepends "
    "it, is untouched); EN gets the same DE source sense demonstrated as `a) {%a certain%} "
    "<is>Arhant</is> <ls>H. 25</ls>.` with the same {Tn}-verbatim clause. No gate, schema or "
    "lang-branch behaviour changed. `test_gloss_wrapper_prompt_preservation_h4270` grew an "
    "EN-lane section pinning both renderings and forbidding either lane from carrying the "
    "other's example."
)
TRACKING = "https://github.com/gasyoun/SanskritLexicography/issues/2109"


def load_block(text):
    start = text.index(BLOCK_OPEN) + len(BLOCK_OPEN)
    end = text.index("\n```", start)
    return start, end, json.loads(text[start:end])


def flip_entry():
    text = LEDGER.read_text(encoding="utf-8")
    start, end, entries = load_block(text)
    hit = [e for e in entries if e.get("id") == ENTRY_ID]
    if not hit:
        raise SystemExit("no ledger entry with id %r" % ENTRY_ID)
    e = hit[0]
    if e.get("verdict") == "SHARED":
        print("ledger entry %s already SHARED" % ENTRY_ID)
        return False
    e["mechanism"] = MECHANISM
    e["verdict"] = "SHARED"
    e["note"] = NOTE
    e["tracking"] = TRACKING
    body = json.dumps(entries, ensure_ascii=False, indent=2)
    LEDGER.write_text(text[:start] + "\n" + body + text[end:], encoding="utf-8", newline="\n")
    print("flipped ledger entry %s GAP -> SHARED" % ENTRY_ID)
    return True


def drifted_ids():
    proc = subprocess.run([sys.executable, str(CHECK)], cwd=str(ROOT),
                          capture_output=True, text=True, encoding="utf-8")
    out = (proc.stdout or "") + (proc.stderr or "")
    # The guard prints the remedy inside backticks (`… --update-hash <id>`), so strip the
    # trailing backtick rather than swallowing it into the id.
    return sorted({m.group(1) for m in re.finditer(r"--update-hash ([A-Za-z0-9_]+)", out)})


def main():
    flip_entry()
    ids = drifted_ids()
    print("re-attesting %d entr(y|ies) whose tracked files moved" % len(ids))
    for entry_id in ids:
        subprocess.run([sys.executable, str(CHECK), "--update-hash", entry_id],
                       cwd=str(ROOT), check=True, capture_output=True, text=True,
                       encoding="utf-8")
    remaining = drifted_ids()
    if remaining:
        print("STILL DRIFTED: %s" % ", ".join(remaining))
        return 1
    print("lang parity ledger clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
