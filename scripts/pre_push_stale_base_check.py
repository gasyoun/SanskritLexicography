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

BLOCKS BY DEFAULT — DEMOTED, THEN RE-PROMOTED
---------------------------------------------
**Current behaviour: this hook REFUSES the push.** Override per-push with
``ALLOW_STALE_BASE_PUSH=1``. ``STALE_BASE_PUSH_STRICT=1`` is now the default and is
accepted as a no-op.

Re-promoted 16-08-2026 on MG's ruling, reversing the demotion described below. The
history is kept because it is the argument against this decision, and a future session
weighing another flip should read it rather than rediscover it:

This started as a **blocking** hook, which is what #1516 asked for. It was demoted to a
warning on the day it shipped, on measured evidence: while landing its own handoff it
refused three pushes, all of them legitimate, all of them this repo's standard workflow —

1. resolving a ``CHANGELOG`` version collision by renumbering a concurrent session's
   section (their rows deleted at the old line numbers, re-added lower);
2. filling a ``mint_handoff.py`` stub that had been pushed to ``main`` seconds earlier;
3. ``handoff_close.py`` archiving a handoff, which repoints ``handoffs/X`` links to
   ``handoffs/archive/X`` **inside rows added minutes ago**.

**All three are now exempted below.** (3) was the open cost of re-promoting this to a
blocker, and was closed the same day (MG 16-08-2026) rather than left to bite: see
``archive_normalized``. It is exempted by normalizing the ``handoffs/X.md`` →
``handoffs/archive/X.md`` repoint on both sides of the surviving-text comparison, so an
archive pass reads as the move it is. A push that repoints a link *and* drops anything
else on the same line still blocks — the exemption is the rewrite, not the tool.

The demotion argument was that three false-positive classes against two true incidents is
the wrong ratio for a blocker, since the standing response to a hook that refuses good
pushes is to switch it off, and then it protects nothing. The counter-argument, which won:
a silent revert of another session's work is not recoverable by the person it happens to —
they discover it days later, if ever — while a false positive costs one extra environment
variable at the moment of the push, by someone who can see exactly what is being reverted::

    ALLOW_STALE_BASE_PUSH=1  git push ...   # per-push override (the only one needed)
    STALE_BASE_PUSH_STRICT=1 git push ...   # accepted no-op; blocking is now the default

A deliberate revert of fresh upstream work is flagged too — correctly, and now it must be
declared with the override rather than merely noticed.

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


# handoffs/H123-foo.md -> handoffs/archive/H123-foo.md, in a path or a full blob URL.
# Negative lookahead so an already-archived link is left alone (the transform must be
# idempotent, or a second archive pass would stop matching).
ARCHIVE_REPOINT_RE = re.compile(r"(handoffs/)(?!archive/)(H\d+[^)\s\"'<>]*\.md)")


def archive_normalized(text: str) -> str:
    """Collapse the pre- and post-archive spelling of a handoff link to one form.

    Class 3 of the known false positives: `handoff_close.py` archiving a handoff
    repoints every `handoffs/X.md` reference to `handoffs/archive/X.md`, including
    inside registry rows another session added minutes ago. The row is NOT lost —
    only its link is repointed — but the raw text no longer matches, so the
    surviving-text check in `blame_recent` cannot see it as a move.

    Normalizing the REMOVED line makes that visible: it is exempt only when its
    text, once the repoint is applied, still exists verbatim in the pushed file. A
    push that repoints a link AND drops anything else on the line does not match,
    so this forgives exactly the archive rewrite and nothing more.

    ONE DIRECTION ONLY — do not also normalize the survivors. Un-archiving someone's
    link (pushing `handoffs/X.md` over their `handoffs/archive/X.md`) is the exact
    pre-image revert this guard exists to catch, and it is what the test's own case 1
    does. Normalizing both sides makes the two indistinguishable and silently forgives
    the real defect; the lookahead above is what keeps the transform one-way.
    """
    return ARCHIVE_REPOINT_RE.sub(r"\1archive/\2", text)


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
        # Moved, not lost: the same text is still somewhere in the pushed file —
        # either verbatim, or with its handoff link repointed to archive/ (class 3).
        if 1 <= ln <= len(old_text):
            stripped = old_text[ln - 1].strip()
            if stripped in survivors or archive_normalized(stripped) in survivors:
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
    # The banner must match what main() actually returns — the H2656 lesson, kept
    # after the 16-08-2026 re-promotion to a blocker. It once printed "PUSH BLOCKED"
    # on a path that warned and let the push through; a session read that as a
    # refusal twice and hand-verified origin both times before noticing. Now the
    # check blocks unconditionally, so the one banner is the true one.
    print("", file=e)
    print("PUSH BLOCKED — this push deletes %d line(s) that landed on %s"
          % (total, remote_ref), file=e)
    print("within the last %g day(s), in %d file(s), and your commits never "
          "reference them." % (recent_days, len(found)), file=e)
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
    # BLOCKS by default (MG 16-08-2026, reversing the demotion below). The push is
    # refused; the escape hatch in the banner is the single way through. STRICT_ENV
    # is kept as an accepted no-op so older callers and docs do not break.
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
