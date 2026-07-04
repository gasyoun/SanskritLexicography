#!/usr/bin/env python
"""Require a changelog touch after major RussianTranslation review/audit edits."""
import argparse
import fnmatch
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

CHANGELOG = "RussianTranslation/CHANGELOG.md"
BYPASS_MARKER = "Changelog: not applicable"
REVIEW_PATTERNS = (
    "RussianTranslation/*REVIEW*.md",
    "RussianTranslation/*AUDIT*.md",
    "RussianTranslation/CODE_REVIEW_*.md",
    "RussianTranslation/ARCHITECTURE_AUDIT_*.md",
    "RussianTranslation/roadmap/*review*.json",
)


def run_git(args):
    p = subprocess.run(["git"] + args, text=True, encoding="utf-8",
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise SystemExit(p.stderr.strip() or "git command failed: %s" % " ".join(args))
    return p.stdout


def norm(path):
    return path.replace("\\", "/").strip()


def changed_files(args):
    if args.files:
        return [norm(p) for p in args.files if norm(p)]
    if args.staged:
        out = run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMR"])
        return [norm(p) for p in out.splitlines() if p.strip()]
    if args.base and args.head:
        spec = "%s...%s" % (args.base, args.head)
        p = subprocess.run(["git", "diff", "--name-only", "--diff-filter=ACMR", spec],
                           text=True, encoding="utf-8", stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        if p.returncode:
            out = run_git(["diff", "--name-only", "--diff-filter=ACMR",
                           "%s..%s" % (args.base, args.head)])
            return [norm(x) for x in out.splitlines() if x.strip()]
        return [norm(x) for x in p.stdout.splitlines() if x.strip()]
    out = run_git(["diff", "--name-only", "--diff-filter=ACMR", "HEAD"])
    return [norm(p) for p in out.splitlines() if p.strip()]


def is_review_file(path):
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in REVIEW_PATTERNS)


def has_bypass_marker(path):
    if not os.path.exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as f:
            return any(BYPASS_MARKER in line for line in f)
    except OSError:
        return False


def check(paths):
    changed = set(paths)
    review_files = sorted(p for p in changed if is_review_file(p))
    if not review_files:
        return 0
    if CHANGELOG in changed:
        return 0
    unwaived = [p for p in review_files if not has_bypass_marker(p)]
    if not unwaived:
        return 0
    print("Major review/audit files changed without %s:" % CHANGELOG, file=sys.stderr)
    for path in unwaived:
        print("  - %s" % path, file=sys.stderr)
    print("\nAdd a changelog entry, or add an auditable '%s' marker to the review file."
          % BYPASS_MARKER, file=sys.stderr)
    return 1


def selftest():
    import contextlib
    import io
    import tempfile

    with contextlib.redirect_stderr(io.StringIO()):
        assert check(["RussianTranslation/CODE_REVIEW_2026-07-04.md"]) == 1
    assert check(["RussianTranslation/CODE_REVIEW_2026-07-04.md", CHANGELOG]) == 0
    assert check(["RussianTranslation/README.md"]) == 0
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "REVIEW.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("Changelog: not applicable\n")
        old_patterns = REVIEW_PATTERNS
        try:
            globals()["REVIEW_PATTERNS"] = (path.replace("\\", "/"),)
            assert check([path.replace("\\", "/")]) == 0
        finally:
            globals()["REVIEW_PATTERNS"] = old_patterns
    print("review_changelog_guard selftest OK")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base")
    ap.add_argument("--head")
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("files", nargs="*")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    return check(changed_files(args))


if __name__ == "__main__":
    sys.exit(main())
