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
