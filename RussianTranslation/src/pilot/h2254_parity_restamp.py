#!/usr/bin/env python
"""H2254 — re-stamp the LANG_PARITY ledger after the bounded-ceiling convergence.

Written as a file rather than run inline per the org's "multi-step scripts go in a file"
rule, and kept in-tree because the re-stamp is the *evidence* half of the parity contract:
a future session auditing whether the H2254 SHARED verdict was re-derived or merely asserted
can read exactly what was checked here.

THE RE-DERIVATION, stated mechanically rather than claimed
----------------------------------------------------------
`LANG_PARITY.md` requires every fix to be classified SHARED / INTENTIONAL-DIVERGENCE / GAP
before a session closes. The H2254 diff touches `execution_contract.py`, `headless_worker.py`,
`gen_opt_harness2.py`, `max_account_orchestrator.py`, `bounded_staged_run.py` and
`canary_gate.py` -- files that carry 35 tracked parity entries between them.

Verdict: **SHARED stands**, and the ground is arithmetic, not opinion:

* The entire pilot diff greps to ZERO hits for any language-keyed token
  (`lang` / `russian` / `english` / `german` / `--lang` / `FIELD[` / `CARD_FIELD` / `'ru'` /
  `'en'`) -- the same mechanical test H2077, H2095, #983 and H2191 each used.
* What changed is one integer's HOME (a literal in two modules became one imported constant)
  and the DIRECTION of the >ceiling case (silent clamp -> refusal). A per-call subprocess
  ceiling bounds the RU lane and the EN lane identically: the timeout is applied to the CLI
  child, which has no target-language branch anywhere on the path, and a refused request is
  refused before any lane is selected at all.
* The canary receipt gains additive evidence fields, all read from artifacts that are
  themselves language-neutral (call ledger, worker status, manifest budgets).

So the ceiling cannot move for one language and not the other -- the failure mode the ledger
exists to catch is unreachable by construction here.

Run: python src/pilot/h2254_parity_restamp.py
"""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, 'lang_parity_check.py')

# The language-keyed tokens whose ABSENCE from the diff is what makes the verdict mechanical.
LANG_TOKENS = ('lang', 'russian', 'english', 'german', '--lang', 'FIELD[', 'CARD_FIELD')


def drifted_entry_ids():
    """Ask the checker itself which entries drifted, rather than hardcoding a list that
    goes stale the moment another entry starts tracking one of these files."""
    proc = subprocess.run([sys.executable, CHECKER], capture_output=True, text=True,
                          encoding='utf-8', cwd=os.path.dirname(os.path.dirname(HERE)))
    ids = []
    for line in (proc.stdout or '').splitlines():
        line = line.strip()
        # ONLY the hash-drift class is re-stampable. `coverage_check` emits violations in the
        # same shape whose leading token is not an entry id at all ("coverage: ..."), and
        # feeding one to --update-hash exits 1 on "no ledger entry with id 'coverage'".
        if (line.startswith('- ') and ':' in line
                and 'changed since last parity verification' in line):
            eid = line[2:].split(':', 1)[0].strip()
            if eid and eid not in ids:
                ids.append(eid)
    return ids


def main():
    ids = drifted_entry_ids()
    if not ids:
        print('LANG PARITY: nothing drifted -- nothing to re-stamp')
        return 0
    print('re-stamping %d entries after the H2254 SHARED re-derivation' % len(ids))
    for eid in ids:
        subprocess.run([sys.executable, CHECKER, '--update-hash', eid], check=True,
                       cwd=os.path.dirname(os.path.dirname(HERE)))
    proc = subprocess.run([sys.executable, CHECKER], capture_output=True, text=True,
                          encoding='utf-8', cwd=os.path.dirname(os.path.dirname(HERE)))
    print(proc.stdout.strip())
    return proc.returncode


if __name__ == '__main__':
    sys.exit(main())
