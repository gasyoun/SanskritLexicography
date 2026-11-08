#!/usr/bin/env python3
# A-class script gate — H7596 (GLM-5.3-Flash, 01-11-2026).
#
# Finding-as-test over epistemic_dashboard/verifiability.json: every class-A row
# that declares a primary_script must have its recipe still runnable. In-tree
# scripts must exist; a script that declares a selftest (an argparse
# add_argument("--selftest", ...) literal) must exit 0. A script whose committed
# home is another repo is cross-checked against the committed EXTERNAL_SCRIPTS map
# below; CI checks out one repo, so external rows are skipped (home named), not red.
#
# Red = the recipe behind a class-A claim no longer runs:
#   1. script_exists=true, script absent, row not in EXTERNAL_SCRIPTS
#   2. script present, declares --selftest, selftest exits nonzero or times out
#   3. script_exists=false but the script IS present (stale gone-claim)
#
# Exit: 0 green · 1 red · 2 usage. CI: .github/workflows/a-class-script-check.yml
#
# EXTERNAL_SCRIPTS provenance: RECIPES.md §2/§4/§7/§9 + estate probe 01-11-2026
# (SanskritGrammar, VisualDCS, csl-apidev, csl-atlas, csl-orig, mw-dev,
# SamudraManthanam, Uprava); register_census.py lives upstream in
# sanskrit-lexicon/MWS and is not cloned locally.

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_VERIFIABILITY = "epistemic_dashboard/verifiability.json"
DEFAULT_TIMEOUT = 120

# Cross-repo homes (owner/repo path/under/repo) for A-class primary_script rows
# whose script is not in this tree. An absent row NOT listed here is red.
EXTERNAL_SCRIPTS = {
    "delta_annotation_layers.py": "gasyoun/VisualDCS derived-data/Corpus-Delta-2021-2026",
    "build_xref.py": "sanskrit-lexicon/csl-apidev simple-search/dcs_xref",  # RECIPES §2
    "f5_entry_comparison.py": "gasyoun/csl-atlas scripts/forensic",
    "build_root_normalization.py": "gasyoun/csl-orig v02/etymology_stats",
    "hw.py": "gasyoun/mw-dev pywork",
    "stats_etymology.py": "gasyoun/csl-orig v02/etymology_stats",
    "varga_shares.py": "gasyoun/SanskritGrammar GasunsDhatu_2014/revision-2026",  # §4
    "titov_control_entry_size.py": "gasyoun/Uprava research",  # RECIPES §7
    "delta_supplement.py": "gasyoun/VisualDCS derived-data/Corpus-Delta-2021-2026",
    "nkrya_annotate.py": "gasyoun/SamudraManthanam web/corpus_builder",
    "f9_shared_omission.py": "gasyoun/csl-atlas scripts/forensic",
    "period_style_gradient.py": "gasyoun/SanskritGrammar ZalizniakOcherk_1978",
    "whitney_aorist_tagger.py": "gasyoun/SanskritGrammar WhitneyGrammar_1889",
    "test_converter.py": "gasyoun/SamudraManthanam web/tests",
    "buhler_provenance.py": "gasyoun/SanskritGrammar scripts",
    "build_samasa_ladder.py": "gasyoun/SanskritGrammar sangram/data/samasa_ladder",
    "aggregate_dcs_gov.py": "gasyoun/SanskritGrammar BuhlerLeitfaden_1923/government_class_index",
    "build_uttarapada_dict_vs_corpus.py": "gasyoun/VisualDCS derived-data/Kompozity",
    "register_census.py": "sanskrit-lexicon/MWS papers/p3_citation_registers/register_census",
}


def declared_selftest(path: str) -> bool:
    """True iff the file's argparse declares a --selftest flag (not a docstring)."""
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    except (OSError, SyntaxError):
        return False
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"
                and any(isinstance(a, ast.Constant) and a.value == "--selftest"
                        for a in node.args)):
            return True
    return False


def locate(name: str, root: str) -> list:
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        if name in filenames:
            hits.append(os.path.join(dirpath, name))
    return sorted(hits)


def run_selftest(path: str, timeout: int):
    """Run <path> --selftest from its own directory; returns (ok, detail)."""
    try:
        r = subprocess.run([sys.executable, path, "--selftest"],
                           cwd=os.path.dirname(os.path.abspath(path)) or ".",
                           capture_output=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"selftest TIMEOUT after {timeout}s"
    tail = (r.stdout or "").strip().splitlines() + (r.stderr or "").strip().splitlines()
    return (r.returncode == 0), (tail[-1][:120] if tail else "(no output)")


def check(findings, root, external, timeout=DEFAULT_TIMEOUT, log=print):
    """Returns (exit_code, summary). Red classes 1-3 per module docstring."""
    reds = []
    n_in = n_ext = n_self = n_rows = 0
    for key in sorted(findings, key=int):
        row = findings[key]
        if str(row.get("class", "")).upper() != "A" or not row.get("primary_script"):
            continue
        n_rows += 1
        name = row["primary_script"]
        hits = locate(name, root)
        if not hits:
            if name in external:
                n_ext += 1
                log(f"  skip  {key:>4}  {name}  -> external: {external[name]}")
                continue
            reds.append(f"[{key}] script_exists=true but {name!r} is absent from the "
                        f"tree and has no committed external home — recipe no longer runs")
            continue
        n_in += 1
        if row.get("script_exists") is False:
            reds.append(f"[{key}] script_exists=false but {name!r} IS present "
                        f"({os.path.relpath(hits[0], root)}) — stale gone-claim")
            continue
        for h in hits:
            if not declared_selftest(h):
                log(f"  ok    {key:>4}  {name}  ({os.path.relpath(h, root)})")
                continue
            n_self += 1
            ok, detail = run_selftest(h, timeout)
            log(f"  st    {key:>4}  {name}  ({os.path.relpath(h, root)}) -> "
                f"{'PASS' if ok else 'FAIL ' + detail}")
            if not ok:
                reds.append(f"[{key}] {name!r} ({os.path.relpath(h, root)}) declares a "
                            f"--selftest that exits nonzero: {detail}")
    for r in reds:
        log(f"  RED   {r}")
    summary = {"rows_checked": n_rows, "in_tree": n_in,
               "external_skipped": n_ext, "selftests_run": n_self, "reds": len(reds)}
    return (1 if reds else 0), summary


def selftest():
    """Five fixtures over a synthetic tree; prints N checks, exits 1 on mismatch."""
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "epistemic_dashboard"), exist_ok=True)
        okscript = ("import argparse, sys\n"
                    "ap = argparse.ArgumentParser()\n"
                    "ap.add_argument('--selftest', action='store_true')\n"
                    "a = ap.parse_args()\n"
                    "if a.selftest:\n    print('fixture ok')\n    sys.exit(0)\n")
        badscript = ("import argparse, sys\n"
                     "ap = argparse.ArgumentParser()\n"
                     "ap.add_argument('--selftest', action='store_true')\n"
                     "a = ap.parse_args()\n"
                     "if a.selftest:\n    print('fixture fails')\n    sys.exit(3)\n")
        open(os.path.join(td, "okscript.py"), "w").write(okscript)
        open(os.path.join(td, "badscript.py"), "w").write(badscript)
        json.dump({"findings": {}},
                  open(os.path.join(td, "epistemic_dashboard/verifiability.json"), "w"))
        ext = {"ghost.py": "fixture/external-home"}
        A = "A"
        rows_ok = {"1": {"class": A, "primary_script": "okscript.py", "script_exists": True}}
        rows_missing = {"1": {"class": A, "primary_script": "ghost.py", "script_exists": True}}
        rows_fail = {"1": {"class": A, "primary_script": "badscript.py", "script_exists": True}}
        rows_false = {"1": {"class": A, "primary_script": "okscript.py", "script_exists": False}}
        checks = []
        c, s = check(rows_ok, td, ext, log=lambda *_: None)
        checks.append(("existing-pass", c == 0 and s["selftests_run"] == 1))
        c, s = check(rows_missing, td, {}, log=lambda *_: None)
        checks.append(("missing-script(red)", c == 1))
        c, s = check(rows_missing, td, ext, log=lambda *_: None)
        checks.append(("external-skip(green)", c == 0 and s["external_skipped"] == 1))
        c, s = check(rows_fail, td, ext, log=lambda *_: None)
        checks.append(("failing-selftest(red)", c == 1 and s["selftests_run"] == 1))
        c, s = check(rows_false, td, ext, log=print if False else (lambda *_: None))
        checks.append(("false-present(red)", c == 1))
        fails = [n for n, passed in checks if not passed]
        for n, passed in checks:
            print(f"  fixture {n}: {'ok' if passed else 'MISMATCH'}")
        if fails:
            print(f"selftest: {len(checks) - len(fails)}/{len(checks)} checks passed — FAIL: {fails}")
            return 1
        print(f"selftest: {len(checks)} checks")
        return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=".", help="repo root (default: cwd)")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    root = os.path.abspath(args.dir)
    vp = os.path.join(root, DEFAULT_VERIFIABILITY)
    if not os.path.isfile(vp):
        print(f"a_class_script_check: no {DEFAULT_VERIFIABILITY} under {root}",
              file=sys.stderr)
        return 2
    with open(vp, encoding="utf-8") as f:
        findings = json.load(f)["findings"]
    code, summary = check(findings, root, EXTERNAL_SCRIPTS, args.timeout)
    print(f"a_class_script_check: {'GREEN' if code == 0 else 'RED'} — "
          f"{summary['rows_checked']} A-class primary_script rows: "
          f"{summary['in_tree']} in-tree, {summary['external_skipped']} external-skip, "
          f"{summary['selftests_run']} declared selftests run, {summary['reds']} red")
    return code


if __name__ == "__main__":
    sys.exit(main())
