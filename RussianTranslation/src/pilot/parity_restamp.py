#!/usr/bin/env python
"""parity_restamp.py -- shared mechanics for the h*_parity_restamp.py receipts (H4408).

The five one-shot restamp scripts (h3500/i2109/h2254/h2504/h3144) each grew
their own copy of the same three mechanics: parse the ```json lang_parity_ledger
block, ask the checker which entries drifted, and refresh each drifted entry via
`lang_parity_check.py --update-hash <id>` — one full interpreter start PER entry.
This module is the one shared implementation:

  * load_ledger()/write_ledger()  -- the LANG_PARITY.md json block, once.
  * drifted_ids()                 -- ONE checker run; parses BOTH output shapes
                                    (the `- <id>: ... changed since last parity
                                    verification` lines h2254/h2504 matched and
                                    the backticked `--update-hash <id>` remedy
                                    i2109/h3144 matched), unioned.
  * update_hashes(ids)            -- N ids, ONE invocation: imports the checker
                                    and calls update_hash() in-process (the
                                    scripts used to spawn a subprocess per id).
  * finish(ids)                   -- update_hashes + one final verify run;
                                    returns the checker's exit code.

The per-handoff scripts stay in-tree as thin callers: their docstrings and NOTE
receipts are the review evidence and must not be merged away.

H4408 follow-up (16-09-2026): the h4527_/h4527b_/h4528_/h4861_parity_restamp.py
receipts had each grown their own ~25-line copy of a second mechanic --
stamp-the-drifted-entries + add-a-new-entry-if-missing + refresh-hashes-and-
report, using `lang_parity_check` directly rather than this module (h4528's own
docstring names the class: "same class as h2254_/h2504_/h4438_parity_restamp.py").
`ensure_entry()`, `stamp_drifted()` and `restamp_receipt()` below are that
mechanic, extracted once; h4438_parity_restamp.py's hand-rolled ledger block
parsing and per-id subprocess loop were also folded onto load_ledger()/
write_ledger()/update_hashes()/run_checker() above. h4529_parity_restamp.py
stayed separate: it is a dry-run reporter with an `--apply` flag and a distinct
CRLF-normalized hash comparison (via `lang_parity_check.file_sha256`), not the
same mutate-then-restamp shape.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]          # .../RussianTranslation
LEDGER = ROOT / "LANG_PARITY.md"
CHECK = ROOT / "src" / "pilot" / "lang_parity_check.py"
BLOCK_OPEN = "```json lang_parity_ledger"


def load_ledger():
    """-> (full_text, block_start, block_end, entries) for LANG_PARITY.md."""
    text = LEDGER.read_text(encoding="utf-8")
    start = text.index(BLOCK_OPEN) + len(BLOCK_OPEN)
    end = text.index("\n```", start)
    return text, start, end, json.loads(text[start:end])


def write_ledger(text, start, end, entries):
    """Rewrite the json block in place, preserving everything around it."""
    body = json.dumps(entries, ensure_ascii=False, indent=2)
    LEDGER.write_text(text[:start] + "\n" + body + text[end:],
                      encoding="utf-8", newline="\n")


def drifted_ids():
    """Ask the checker (ONE run) which entries drifted; both output shapes."""
    proc = subprocess.run([sys.executable, str(CHECK)], cwd=str(ROOT),
                          capture_output=True, text=True, encoding="utf-8")
    out = (proc.stdout or "") + (proc.stderr or "")
    ids = set()
    for line in out.splitlines():
        line = line.strip()
        # shape 1 (h2254/h2504): `- <id>: <file> changed since last parity verification`
        if (line.startswith('- ') and ':' in line
                and 'changed since last parity verification' in line):
            ids.add(line[2:].split(':', 1)[0].strip())
    # shape 2 (i2109/h3144): the remedy inside backticks — strip the trailing
    # backtick rather than swallowing it into the id.
    ids |= {m.group(1) for m in re.finditer(r"--update-hash ([A-Za-z0-9_]+)", out)}
    ids.discard('coverage')                          # coverage prefix is not an id
    return sorted(ids)


def update_hashes(ids):
    """Refresh verified_sha256 for N entries in THIS interpreter — one process,
    no per-id spawn. Falls back to the subprocess CLI if the import fails."""
    if not ids:
        return
    try:
        sys.path.insert(0, str(CHECK.parent))
        import lang_parity_check as lpc
    except ImportError:
        for entry_id in ids:
            subprocess.run([sys.executable, str(CHECK), "--update-hash", entry_id],
                           cwd=str(ROOT), check=True, capture_output=True,
                           text=True, encoding="utf-8")
        return
    for entry_id in ids:
        lpc.update_hash(entry_id)                    # loads + rewrites per call


def run_checker():
    return subprocess.run([sys.executable, str(CHECK)], cwd=str(ROOT),
                          capture_output=True, text=True, encoding="utf-8")


def finish(ids):
    """The shared tail: re-attest N ids, then verify the ledger is clean.
    Returns the checker's exit code (0 = clean)."""
    print("re-attesting %d entr(y|ies) whose tracked files moved" % len(ids))
    update_hashes(ids)
    remaining = drifted_ids()
    if remaining:
        print("STILL DRIFTED: %s" % ", ".join(remaining))
        return 1
    print("lang parity ledger clean")
    return 0


def ensure_entry(entries, new_entry):
    """Append `new_entry` (a dict with at least an 'id' key) if no entry with that
    id exists yet. Returns True iff it was added."""
    if any(e.get("id") == new_entry["id"] for e in entries):
        return False
    entries.append(dict(new_entry))
    return True


def stamp_drifted(entries, ids, stamp):
    """Append `stamp` to the `note` field of every entry in `entries` whose id is
    in `ids`, unless `stamp` is already present in that note. Returns True iff any
    note was changed."""
    ids = set(ids)
    changed = False
    for e in entries:
        if e.get("id") in ids:
            note = e.get("note") or ""
            if stamp not in note:
                e["note"] = (note.rstrip() + " " + stamp).strip()
                changed = True
    return changed


def restamp_receipt(stamp, new_entry, extra_stamps=()):
    """The h4527_/h4527b_/h4528_/h4861_parity_restamp.py receipt tail: stamp
    `stamp` onto the note of every ledger entry the checker reports as drifted
    (checked in-process via lang_parity_check, the path these four receipts
    always used -- distinct from drifted_ids()'s subprocess-plus-regex parse
    above), ensure `new_entry` exists, optionally stamp (ids, text) pairs onto
    other entries regardless of drift (h4527b's supersession sentence onto the
    entry its pass retired), refresh hashes for every touched id through
    lang_parity_check's own writer, and print the receipts' shared summary line.
    Returns the checker's exit code (0 = clean)."""
    sys.path.insert(0, str(CHECK.parent))
    import lang_parity_check as lpc
    entries, text, span = lpc.load_ledger()
    drifted = sorted({v.split(":", 1)[0] for v in lpc.check(entries)})
    changed = stamp_drifted(entries, drifted, stamp)
    for ids, extra in extra_stamps:
        changed = stamp_drifted(entries, ids, extra) or changed
    changed = ensure_entry(entries, new_entry) or changed
    if changed:
        block = json.dumps(entries, indent=2, ensure_ascii=False)
        with open(lpc.LEDGER_MD, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text[:span[0]] + block + "\n" + text[span[1]:])
    for entry_id in drifted + [new_entry["id"]]:
        lpc.update_hash(entry_id)
    left = lpc.check(lpc.load_ledger()[0])
    print("re-derived %d drifted entr%s; %d violation(s) left"
          % (len(drifted), "y" if len(drifted) == 1 else "ies", len(left)))
    return 1 if left else 0
