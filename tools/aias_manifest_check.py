# VENDORED COPY of Uprava/tools/aias_manifest_check.py (H7119, 24-10-2026).
# Canonical: https://github.com/gasyoun/Uprava/blob/main/tools/aias_manifest_check.py
# Re-vendor when schema_version moves; the gate runs --selftest so a broken copy
# cannot pass silently. Drift is reported by Uprava's update sweep, not enforced here.
#!/usr/bin/env python3
"""aias_manifest_check.py — the data layer's AI declaration (`aias.yaml`), H7119.

Why this exists
---------------
``metadoc_ai_field.py`` (19-10-2026) made an AIAS statement a required field of
a *metadoc* — the document about a document. The artifacts that actually get
cited and reused are datasets: kosha manifests, corpus exports, derived tables.
A dataset that nobody can attribute has no reader contract; Palomar asks for a
``formalization.yaml`` beside every indexed project for exactly this reason, and
the Xena Project's "How to Formalize All of Mathematics" (16-10-2026) puts it
bluntly: an AI-built artifact whose provenance is undeclared is worse than no
artifact at all.

So the declaration travels with the DATA, not only with the prose. One flat file
at the repo root::

    schema_version: 1
    level: 3                                  # 1-5, or: not declared
    produced_by: "code (ingest + validation scripts); table rows"
    decided_by: "MG ruled the schema and the acceptance; agent chose internals"
    review: docs/AIAS_REVIEW_2026-10-24.md    # or: none
    generated_at: 2026-10-24
    scope: "data/manifest/datasets.json + derived tables built from it"

Field-compatible with the metadoc block by construction: the same AIAS v2 scale
(Perkins/Furze/Roe/MacVaugh) — 1 No AI · 2 AI Planning · 3 AI Collaboration ·
4 Full AI · 5 AI Exploration — and the same explicit escape hatch, ``not
declared``, for a dataset whose provenance was never recorded. ``not declared``
is valid and never fails ``--strict``: an honest gap stays visible and countable
instead of being papered over with a guessed level. That guess — a file that
overstates human review — is the failure mode this tool exists to catch.

Rules
-----
* ``level`` MUST be an integer 1-5 or the literal ``not declared``.
  Out of range (0, 6, 99) and unparsable values are FAILs, not warnings.
* ``review`` MUST be ``none`` or a path that RESOLVES relative to the
  ``aias.yaml`` that names it. A dangling pointer is a FAIL: a review claim
  nobody can open is worse than an admitted ``none``.
* ``produced_by`` and ``decided_by`` MUST be non-empty and MUST NOT be an
  unfilled ``<...>`` placeholder — a stub is red by design.
* ``generated_at`` MUST be an ISO date (YYYY-MM-DD).
* ``schema_version`` MUST equal the supported version (1).

Usage
-----
    python tools/aias_manifest_check.py                      # discover under cwd
    python tools/aias_manifest_check.py aias.yaml             # explicit files
    python tools/aias_manifest_check.py --require-root .      # release gate
    python tools/aias_manifest_check.py --repos-dir ..        # per-repo coverage
    python tools/aias_manifest_check.py --strict --require-root .
    python tools/aias_manifest_check.py --json
    python tools/aias_manifest_check.py --selftest

Exit: 0 clean (or report-only) · 1 findings · 2 usage.
``--require-root`` is the shape a release path wants: it turns "no aias.yaml at
this root" from "nothing to check" into a named refusal, so a release cannot
sail through on an empty scan.

Standalone by rule (imports nothing from tools/, no PyYAML): a minimal clone can
run this with nothing but CPython 3.9+. The flat-YAML reader below accepts only
the shape the schema uses and REFUSES anything nested, with a named error —
silently ignoring a key is how a manifest becomes decorative.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SCHEMA_VERSION = 1
FILENAME = "aias.yaml"

REQUIRED = ("schema_version", "level", "produced_by", "decided_by", "review", "generated_at")
OPTIONAL = ("scope", "level_name", "generated_by", "notes")

LEVEL_NAMES = {
    1: "No AI",
    2: "AI Planning",
    3: "AI Collaboration",
    4: "Full AI",
    5: "AI Exploration",
}
UNDECLARED_RE = re.compile(r"^(?:not declared|undeclared|не заявлено)$", re.I)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PLACEHOLDER_RE = re.compile(r"^\s*<.*>\s*$")

# Keys whose value may legitimately be the bare word "none".
NONE_OK = ("review",)


# --- flat YAML ---------------------------------------------------------

class YamlError(ValueError):
    """A manifest the reader refuses to guess at."""


def _strip_comment(line):
    """Drop a trailing ``# comment`` that is not inside quotes."""
    out = []
    quote = None
    for i, ch in enumerate(line):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            continue
        if ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _unquote(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_flat_yaml(text):
    """Parse the flat ``key: value`` mapping this schema uses.

    Raises YamlError on anything the schema does not allow — a nested mapping,
    a list item, a tab indent, a duplicate key. Returning a partial dict would
    let a malformed manifest validate on the keys that survived.
    """
    data = {}
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = _strip_comment(raw)
        if not line.strip():
            continue
        if line.startswith((" ", "\t")):
            raise YamlError("line %d: indented content is not supported (flat key: value only): %r"
                            % (lineno, raw.strip()[:60]))
        if line.lstrip().startswith("- "):
            raise YamlError("line %d: list items are not supported (use one quoted string): %r"
                            % (lineno, raw.strip()[:60]))
        if ":" not in line:
            raise YamlError("line %d: expected 'key: value', got %r" % (lineno, raw.strip()[:60]))
        key, _, value = line.partition(":")
        key = key.strip()
        if not key:
            raise YamlError("line %d: empty key" % lineno)
        if key in data:
            raise YamlError("line %d: duplicate key %r" % (lineno, key))
        data[key] = _unquote(value.strip())
    return data


# --- one manifest ------------------------------------------------------

def check_manifest(path):
    """Validate one aias.yaml. Returns a result dict (never raises on findings)."""
    path = Path(path)
    res = {"path": str(path), "status": "ok", "level": None, "findings": [], "data": {}}

    def fail(code, detail):
        res["findings"].append({"code": code, "detail": detail})

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {"path": str(path), "status": "missing", "level": None,
                "findings": [{"code": "missing_file", "detail": "cannot read %s: %s" % (path, exc)}],
                "data": {}}

    try:
        data = parse_flat_yaml(text)
    except YamlError as exc:
        return {"path": str(path), "status": "invalid", "level": None,
                "findings": [{"code": "malformed_yaml", "detail": str(exc)}], "data": {}}

    res["data"] = data

    unknown = [k for k in data if k not in REQUIRED and k not in OPTIONAL]
    if unknown:
        fail("unknown_key", "unknown key(s): %s (allowed: %s)"
             % (", ".join(sorted(unknown)), ", ".join(REQUIRED + OPTIONAL)))

    for key in REQUIRED:
        if key not in data:
            fail("missing_key", "required key %r is absent" % key)

    if "schema_version" in data:
        if data["schema_version"] != str(SCHEMA_VERSION):
            fail("schema_version", "schema_version must be %d, got %r"
                 % (SCHEMA_VERSION, data["schema_version"]))

    # level: 1-5 integer, or the explicit undeclared escape
    level = None
    if "level" in data:
        raw = data["level"].strip()
        if UNDECLARED_RE.match(raw):
            res["status"] = "undeclared"
        elif re.match(r"^-?\d+$", raw):
            n = int(raw)
            if 1 <= n <= 5:
                level = n
                res["level"] = n
            else:
                fail("level_range", "level out of range: %d (AIAS v2 is 1-5, or 'not declared')" % n)
        else:
            fail("level_value", "level must be 1-5 or 'not declared', got %r" % raw[:60])

    if "level_name" in data and level is not None:
        declared = data["level_name"].strip()
        canonical = LEVEL_NAMES[level]
        if declared and declared.lower() != canonical.lower():
            fail("level_name", "level_name %r contradicts level %d (%r)" % (declared, level, canonical))

    # prose fields: present, non-empty, not a placeholder
    for key in ("produced_by", "decided_by"):
        if key in data:
            value = data[key].strip()
            if not value:
                fail("empty_field", "%s is empty — say what the AI did and what the human ruled" % key)
            elif PLACEHOLDER_RE.match(value):
                fail("placeholder", "%s is an unfilled placeholder: %r" % (key, value[:60]))
            elif value.upper() == "UNKNOWN":
                fail("placeholder", "%s is 'unknown' — an unknown provenance is declared as level: not declared" % key)

    # review: `none`, or a path that resolves from this file
    if "review" in data:
        review = data["review"].strip()
        if not review:
            fail("empty_field", "review is empty — use 'none' when no review evidence exists")
        elif review.lower() == "none":
            pass
        elif PLACEHOLDER_RE.match(review):
            fail("placeholder", "review is an unfilled placeholder: %r" % review[:60])
        else:
            target = (path.parent / review).resolve()
            if not target.exists():
                fail("dangling_review", "review path does not resolve: %r (from %s) — a pointer nobody can "
                                        "open is a FAIL; declare 'none' if there is no evidence" % (review, path))
            elif target.is_dir():
                fail("dangling_review", "review path is a directory, not an evidence file: %r" % review)

    if "generated_at" in data and not DATE_RE.match(data["generated_at"].strip()):
        fail("bad_date", "generated_at must be an ISO date YYYY-MM-DD, got %r"
             % data["generated_at"].strip()[:40])

    if res["status"] == "undeclared" and not res["findings"]:
        res["status"] = "undeclared"
    elif res["findings"]:
        res["status"] = "invalid"
    return res


# --- discovery / report ------------------------------------------------

PRUNE = {".git", "node_modules", "venv", ".venv", "__pycache__", ".mypy_cache", "dist"}


def discover(root):
    """Every aias.yaml under root, skipping the usual dependency noise."""
    root = Path(root)
    found = []
    for path in sorted(root.rglob(FILENAME)):
        if any(part in PRUNE for part in path.parts):
            continue
        found.append(path)
    return found


def repo_root_of(path):
    """The nearest ancestor holding a .git entry (a worktree's .git is a file)."""
    for parent in [path.parent] + list(path.parent.parents):
        if (parent / ".git").exists():
            return parent
    return path.parent


def coverage(results):
    """Group results by repository and summarise declared / undeclared / missing."""
    groups = {}
    for r in results:
        root = repo_root_of(Path(r["path"]))
        groups.setdefault(str(root), []).append(r)
    out = []
    for root, rows in sorted(groups.items()):
        declared = sum(1 for r in rows if r["status"] == "ok")
        undeclared = sum(1 for r in rows if r["status"] == "undeclared")
        bad = sum(1 for r in rows if r["status"] in ("invalid", "missing"))
        if declared and not undeclared and not bad:
            state = "DECLARED"
        elif bad:
            state = "FAIL"
        elif undeclared:
            state = "NOT DECLARED"
        else:
            state = "DECLARED"
        out.append({"repo": root, "manifests": len(rows), "declared": declared,
                    "not_declared": undeclared, "failing": bad, "state": state})
    return out


def scan_repos_dir(parent):
    """One row per immediate child directory: MISSING when it carries no manifest.

    This is the coverage view: a data repo with no aias.yaml is the artifact
    Palomar would refuse to index, so it is reported, not silently skipped.
    """
    rows = []
    for child in sorted(p for p in Path(parent).iterdir() if p.is_dir()):
        if child.name.startswith(".") or child.name in PRUNE:
            continue
        results = [check_manifest(m) for m in discover(child)]
        if not results:
            rows.append({"repo": str(child), "manifests": 0, "declared": 0,
                         "not_declared": 0, "failing": 0, "state": "MISSING"})
            continue
        rows.extend(coverage(results))
    return rows


def print_report(results, cov, quiet=False):
    if not quiet:
        for r in results:
            mark = {"ok": "OK      ", "undeclared": "LEGACY  ", "missing": "FAIL    ", "invalid": "FAIL    "}[r["status"]]
            if r["status"] == "ok":
                detail = "level %d — %s" % (r["level"], LEVEL_NAMES[r["level"]])
            elif r["status"] == "undeclared":
                detail = "explicitly not declared — honest gap, never a pass in coverage"
            else:
                detail = r["findings"][0]["detail"] if r["findings"] else r["status"]
            print("%s %-60s %s" % (mark, r["path"], detail))
            for f in r["findings"][1:]:
                print("         %-60s %s [%s]" % ("", f["detail"], f["code"]))
    if cov:
        print()
        print("coverage per repo:")
        for c in cov:
            print("  %-8s %-50s manifests=%d declared=%d not_declared=%d failing=%d"
                  % (c["state"], c["repo"], c["manifests"], c["declared"], c["not_declared"], c["failing"]))
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print()
    print("summary: %d manifest(s) · %d declared · %d not declared · %d failing"
          % (len(results), counts.get("ok", 0), counts.get("undeclared", 0),
             counts.get("missing", 0) + counts.get("invalid", 0)))


# --- selftest ----------------------------------------------------------

def selftest():
    import tempfile

    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    good = (
        "schema_version: 1\n"
        "level: 3\n"
        "produced_by: \"code (ingest scripts); table rows\"\n"
        "decided_by: \"MG ruled the schema; agent chose internals\"\n"
        "review: none\n"
        "generated_at: 2026-10-24\n"
    )

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "evidence.md").write_text("review notes\n", encoding="utf-8")

        cases = {
            "good.yaml": good,
            "undeclared.yaml": good.replace("level: 3", "level: not declared"),
            "range.yaml": good.replace("level: 3", "level: 9"),
            "dangling.yaml": good.replace("review: none", "review: docs/missing.md"),
            "resolved.yaml": good.replace("review: none", "review: evidence.md"),
            "placeholder.yaml": good.replace('"MG ruled the schema; agent chose internals"', "<what the human ruled>"),
            "empty.yaml": good.replace('"MG ruled the schema; agent chose internals"', '""'),
            "nested.yaml": good + "extra:\n  inner: 1\n",
            "list.yaml": good + "tags:\n- a\n- b\n",
            "dup.yaml": good + "level: 4\n",
            "unknown.yaml": good + "confidence: high\n",
            "baddate.yaml": good.replace("2026-10-24", "24-10-2026"),
            "noschema.yaml": good.replace("schema_version: 1\n", ""),
            "conflict.yaml": good.replace("level: 3\n", "level: 3\nlevel_name: Full AI\n"),
            "zero.yaml": good.replace("level: 3", "level: 0"),
        }
        for name, body in cases.items():
            (root / name).write_text(body, encoding="utf-8")

        def res(name):
            return check_manifest(root / name)

        check(res("good.yaml")["status"] == "ok" and res("good.yaml")["level"] == 3,
              "a well-formed manifest must be ok at level 3")
        check(res("undeclared.yaml")["status"] == "undeclared", "'not declared' must be valid and counted separately")
        check(res("range.yaml")["status"] == "invalid", "level 9 must fail")
        check(any(f["code"] == "level_range" for f in res("range.yaml")["findings"]),
              "level 9 must name level_range")
        check(res("zero.yaml")["status"] == "invalid", "level 0 must fail")
        check(res("dangling.yaml")["status"] == "invalid", "a dangling review path must fail")
        check(any(f["code"] == "dangling_review" for f in res("dangling.yaml")["findings"]),
              "a dangling review must name dangling_review")
        check(res("resolved.yaml")["status"] == "ok", "a review path that resolves must pass")
        check(res("placeholder.yaml")["status"] == "invalid", "an unfilled placeholder must fail")
        check(res("empty.yaml")["status"] == "invalid", "an empty decided_by must fail")
        check(res("nested.yaml")["status"] == "invalid", "nested yaml must be refused, not ignored")
        check(res("list.yaml")["status"] == "invalid", "list yaml must be refused")
        check(res("dup.yaml")["status"] == "invalid", "a duplicate key must be refused")
        check(any(f["code"] == "unknown_key" for f in res("unknown.yaml")["findings"]),
              "an unknown key must be named")
        check(res("baddate.yaml")["status"] == "invalid", "a non-ISO generated_at must fail")
        check(res("noschema.yaml")["status"] == "invalid", "a missing schema_version must fail")
        check(res("conflict.yaml")["status"] == "invalid", "level_name contradicting level must fail")

        # discovery, coverage and the release-gate shape
        empty = root / "emptyrepo"
        empty.mkdir()
        (empty / "README.md").write_text("no manifest here\n", encoding="utf-8")
        declared_repo = root / "declaredrepo"
        (declared_repo / "nested").mkdir(parents=True)
        (declared_repo / FILENAME).write_text(good, encoding="utf-8")
        (declared_repo / "nested" / FILENAME).write_text(
            good.replace("level: 3", "level: not declared"), encoding="utf-8")
        found = discover(declared_repo)
        check(len(found) == 2, "discover must find every aias.yaml under a root (got %d)" % len(found))
        check(discover(empty) == [], "discover must return nothing for a repo without a manifest")

        missing = check_manifest(empty / FILENAME)
        check(missing["status"] == "missing", "a missing file must be reported as missing, never as ok")

        cov = coverage([check_manifest(declared_repo / FILENAME)])
        check([c["state"] for c in cov] == ["DECLARED"],
              "a repo with one declared manifest must report DECLARED: %r" % (cov,))
        cov_und = coverage([check_manifest(declared_repo / "nested" / FILENAME)])
        check([c["state"] for c in cov_und] == ["NOT DECLARED"],
              "coverage must count an undeclared manifest separately: %r" % (cov_und,))
        cov_missing = coverage([check_manifest(empty / FILENAME)])
        check([c["state"] for c in cov_missing] == ["FAIL"],
              "coverage must be FAIL when a manifest is missing: %r" % (cov_missing,))

        rows = scan_repos_dir(root)
        check(any(r["state"] == "MISSING" for r in rows),
              "scan_repos_dir must report a data repo with no manifest as MISSING")
        check(any(r["state"] == "DECLARED" for r in rows),
              "scan_repos_dir must report a declared repo as DECLARED: %r" % (rows,))

    if failures:
        print("SELFTEST FAILED:")
        for f in failures:
            print("  - %s" % f)
        return 1
    print("SELFTEST OK (%d checks)" % 20)
    return 0


# --- CLI ---------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", help="aias.yaml files to check (default: discover under --root)")
    ap.add_argument("--root", default=".", help="tree to discover manifests in (default: cwd)")
    ap.add_argument("--require-root", action="append", default=[], metavar="DIR",
                    help="release gate: DIR must carry a valid aias.yaml at its root, "
                         "or the run exits 1 with a named refusal")
    ap.add_argument("--repos-dir", help="report one coverage row per immediate child repo")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on any failing manifest (also with --require-root)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    targets = [Path(p) for p in args.paths]
    refusals = []

    for root in args.require_root:
        root = Path(root)
        manifest = root / FILENAME
        if not manifest.is_file():
            refusals.append("REFUSED: no %s at %s — the release path will not cut a dataset "
                            "whose AI provenance is undeclared (H7119)" % (FILENAME, root.resolve()))
        else:
            targets.append(manifest)

    if not args.paths and not args.require_root:
        targets = discover(args.root)

    results = [check_manifest(t) for t in targets]
    cov = scan_repos_dir(args.repos_dir) if args.repos_dir else coverage(results)

    if args.json:
        print(json.dumps({"results": results, "coverage": cov, "refusals": refusals},
                         ensure_ascii=False, indent=2))
    else:
        print_report(results, cov, quiet=args.quiet)
        for line in refusals:
            print(line)

    if not results and not refusals:
        print("nothing to check (no %s under %s)" % (FILENAME, Path(args.root).resolve()))
        return 0

    failing = [r for r in results if r["status"] in ("missing", "invalid")]
    if refusals:
        return 1
    if args.strict and failing:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
