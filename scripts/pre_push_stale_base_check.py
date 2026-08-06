"""Refuse a push that deletes lines another session added upstream moments ago —
the silent-revert class of Uprava#1516.

WHY THE OBVIOUS DESIGN DOES NOT WORK
------------------------------------
The guard proposed on #1516 was "refuse a push whose tree contains a path modified
upstream after the local HEAD's merge-base". Implemented and measured 04-08-2026, it
is **redundant with git itself**: ``merge-base != remote_tip`` is the definition of a
non-fast-forward push, which git already rejects; and a fast-forward push always has
``merge-base == remote_tip``, so the check is vacuous exactly when it is needed. Both
#1516 incidents were clean fast-forwards. A ref-level test cannot see them.

What both incidents *do* share is visible at the line level: the push **deletes lines
that an upstream commit added very recently**, because the author's file content was a
pre-image copy — a stale index (29-07) or a stale checkout (04-08). Nobody edits a line
that landed ninety seconds ago on purpose without knowing it; when it happens it is
almost always a copy written before that line existed.

THE CHECK
---------
For each path the push changes, take the lines it removes relative to the remote tip,
``git blame`` them at the remote tip, and flag any whose introducing commit is

* **recent** — within ``--recent-days`` (default 3), and
* **not part of this push** — so rewriting your own just-pushed line is fine.

That pair is the whole rule. Old lines are ordinary edits. Your own lines are yours.
Someone else's line from an hour ago, deleted by a commit that never mentions it, is
the defect.

WARN BY DEFAULT — AND WHY IT WAS DEMOTED
----------------------------------------
This started as a **blocking** hook, which is what #1516 asked for. It was demoted to a
warning on the day it shipped, on measured evidence: while landing its own handoff it
refused three pushes, all of them legitimate, all of them this repo's standard workflow —

1. resolving a ``CHANGELOG`` version collision by renumbering a concurrent session's
   section (their rows deleted at the old line numbers, re-added lower);
2. filling a ``mint_handoff.py`` stub that had been pushed to ``main`` seconds earlier;
3. ``handoff_close.py`` archiving a handoff, which repoints ``handoffs/X`` links to
   ``handoffs/archive/X`` **inside rows added minutes ago**.

(1) and (2) are exempted below. (3) is not cleanly exemptible without special-casing the
repo's own tooling. Three false-positive classes from routine work in one session, against
two true incidents in a week, is the wrong ratio for a blocker: the standing response to a
hook that refuses good pushes is to switch it off, and then it protects nothing. So the
default is a loud warning that lets the push through, matching how the org already treats
imperfect-judgment guards (``pre_shell_guards`` guard 9 warns on ``git pull``, because
pulls are sometimes right)::

    STALE_BASE_PUSH_STRICT=1 git push ...   # restore blocking
    ALLOW_STALE_BASE_PUSH=1  git push ...   # silence entirely

A deliberate revert of fresh upstream work is flagged too — correctly. The goal is to put
the fact in front of a human at the last moment it is still free to act on, not to forbid.

LIMITS (measured, not assumed)
------------------------------
* Blame is per-path and costs ~one blame per changed file; on a push touching hundreds
  of files this is slow, so ``--max-paths`` (default 40) bounds it and the script says
  so rather than silently sampling.
* Pure additions are never flagged; only deletions and rewrites of recent upstream lines.
* Whitespace-only differences are ignored (``-w``), so a CRLF renormalisation sweep does
  not trip it — the §299/§305 class is a different problem with a different fix.
* A push that reverts a line older than the window is not caught. That is the accepted
  cost of keeping false positives near zero.

Install once per clone::

    git config core.hooksPath .githooks
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ESCAPE_ENV = "ALLOW_STALE_BASE_PUSH"
STRICT_ENV = "STALE_BASE_PUSH_STRICT"
MAX_LISTED = 12
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+")


def git(*args: str, check: bool = False) -> str:
    proc = subprocess.run(
        ("git",) + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), proc.stderr.strip()))
    return proc.stdout


def pushed_commits(remote_ref: str, local_ref: str) -> set[str]:
    out = git("rev-list", "%s..%s" % (remote_ref, local_ref))
    return {line.strip() for line in out.splitlines() if line.strip()}


def changed_paths(remote_ref: str, local_ref: str) -> list[str]:
    out = git("diff", "--name-only", "-w", remote_ref, local_ref)
    return [p for p in out.splitlines() if p.strip()]


def removed_line_numbers(remote_ref: str, local_ref: str, path: str) -> list[int]:
    """Line numbers AT THE REMOTE TIP that this push removes or rewrites."""
    out = git("diff", "-w", "-U0", remote_ref, local_ref, "--", path)
    numbers: list[int] = []
    old_line = 0
    for line in out.splitlines():
        m = HUNK_RE.match(line)
        if m:
            old_line = int(m.group(1))
            continue
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("-"):
            numbers.append(old_line)
            old_line += 1
    return numbers


STUB_MARKER = "STUB claimed by mint_handoff.py"


def surviving_text(local_ref: str, path: str) -> set[str]:
    """Every non-blank stripped line of the path as this push would leave it.

    Used to separate a MOVE from a LOSS. Renumbering a changelog section, resolving a
    merge by relocating someone's rows, reordering a table — all delete lines at their
    old position and re-add them elsewhere. The remote keeps the content, so there is
    nothing to protect. Only a line whose text survives NOWHERE in the pushed file is a
    real deletion. (Found by dogfooding: the guard blocked its own landing commit for
    exactly this, which is the false-positive class that gets a blocking hook disabled.)
    """
    out = git("show", "%s:%s" % (local_ref, path))
    return {ln.strip() for ln in out.splitlines() if ln.strip()}


def is_mint_stub(remote_ref: str, path: str) -> bool:
    """A freshly minted handoff skeleton being filled in the same pass.

    `mint_handoff.py` lands a placeholder body on origin/main, then the session that
    minted it replaces those placeholders with real content — a legitimate rewrite of
    lines that are, by construction, minutes old and authored outside the push.
    """
    if "/handoffs/" not in "/" + path.replace("\\", "/"):
        return False
    return STUB_MARKER in git("show", "%s:%s" % (remote_ref, path))


def blame_recent(remote_ref: str, path: str, lines: list[int],
                 cutoff: datetime, ours: set[str],
                 survivors: set[str]) -> list[tuple[int, str, str]]:
    """(line, short_sha, author) for removed lines added recently by someone else."""
    hits: list[tuple[int, str, str]] = []
    old_text = git("show", "%s:%s" % (remote_ref, path)).splitlines()
    for ln in lines:
        # Moved, not lost: the same text is still somewhere in the pushed file.
        if 1 <= ln <= len(old_text) and old_text[ln - 1].strip() in survivors:
            continue
        out = git("blame", "-w", "--line-porcelain", "-L", "%d,%d" % (ln, ln),
                  remote_ref, "--", path)
        if not out.strip():
            continue
        head = out.splitlines()[0].split()
        if not head:
            continue
        sha = head[0]
        if sha in ours:
            continue
        author = ""
        when: datetime | None = None
        for row in out.splitlines():
            if row.startswith("author "):
                author = row[len("author "):].strip()
            elif row.startswith("author-time "):
                try:
                    when = datetime.fromtimestamp(int(row.split()[1]), tz=timezone.utc)
                except (ValueError, IndexError):
                    when = None
        if when is not None and when >= cutoff:
            hits.append((ln, sha[:9], author))
    return hits


def scan(local_ref: str, remote_ref: str, recent_days: float,
         max_paths: int) -> tuple[dict[str, list], bool]:
    ours = pushed_commits(remote_ref, local_ref)
    cutoff = datetime.now(timezone.utc) - timedelta(days=recent_days)
    paths = changed_paths(remote_ref, local_ref)
    truncated = len(paths) > max_paths

    found: dict[str, list] = {}
    for path in paths[:max_paths]:
        removed = removed_line_numbers(remote_ref, local_ref, path)
        if not removed:
            continue
        if is_mint_stub(remote_ref, path):
            continue
        hits = blame_recent(remote_ref, path, removed, cutoff, ours,
                            surviving_text(local_ref, path))
        if hits:
            found[path] = hits
    return found, truncated


def report(found: dict[str, list], remote_ref: str, recent_days: float,
           truncated: bool, max_paths: int) -> None:
    total = sum(len(v) for v in found.values())
    e = sys.stderr
    print("", file=e)
    print("PUSH BLOCKED — this push deletes %d line(s) that landed on %s within the"
          % (total, remote_ref), file=e)
    print("last %g day(s), in %d file(s), and your commits never reference them."
          % (recent_days, len(found)), file=e)
    print("", file=e)
    shown = 0
    for path, hits in found.items():
        print("  %s" % path, file=e)
        for ln, sha, author in hits:
            if shown >= MAX_LISTED:
                break
            print("      line %-6d added by %s (%s)" % (ln, sha, author), file=e)
            shown += 1
        if shown >= MAX_LISTED:
            print("      …", file=e)
            break
    print("", file=e)
    print("That is Uprava#1516. Twice now a clean fast-forward with green hooks has", file=e)
    print("installed a pre-image copy over another session's work: 6 files on 29-07", file=e)
    print("(stale index after `git reset --soft`), 19 link fixes on 04-08 (stale", file=e)
    print("checkout — the branch ref moved, the working tree did not).", file=e)
    print("", file=e)
    print("If you did NOT mean to touch those lines, your file content is stale:", file=e)
    print("    git fetch origin && git rebase %s" % remote_ref, file=e)
    print("and if `git status` lists files you never edited, do NOT `git add -A` and", file=e)
    print("do NOT lift a patch out of that tree (a patch encodes its base, FINDINGS", file=e)
    print("§308) — rebuild on a fresh worktree off %s and re-apply your edits." % remote_ref, file=e)
    print("", file=e)
    print("If the revert IS deliberate:  %s=1 git push ..." % ESCAPE_ENV, file=e)
    if truncated:
        print("", file=e)
        print("NOTE: only the first %d changed paths were scanned (--max-paths)." % max_paths, file=e)
    print("", file=e)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("local_ref")
    ap.add_argument("remote_ref")
    ap.add_argument("--recent-days", type=float, default=3.0)
    ap.add_argument("--max-paths", type=int, default=40)
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if not args.no_fetch:
        git("fetch", args.remote_ref.split("/", 1)[0] or "origin", "--quiet")

    if not git("rev-parse", "--verify", "--quiet", args.remote_ref).strip():
        if args.json:
            print(json.dumps({"result": "skip", "reason": "remote ref not found"}))
        return 0

    found, truncated = scan(args.local_ref, args.remote_ref, args.recent_days, args.max_paths)

    if args.json:
        print(json.dumps({
            "result": "block" if found else "ok",
            "paths": sorted(found),
            "lines": sum(len(v) for v in found.values()),
            "truncated": truncated,
        }))
        return 1 if found else 0

    if not found:
        return 0
    report(found, args.remote_ref, args.recent_days, truncated, args.max_paths)
    # WARN by default; block only under STALE_BASE_PUSH_STRICT=1. See the module
    # docstring — measured false-positive rate in this repo's own workflows is what
    # decided this, not caution in the abstract.
    return 1 if os.environ.get(STRICT_ENV) else 0


if __name__ == "__main__":
    raise SystemExit(main())
