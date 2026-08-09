#!/usr/bin/env python3
"""Repository-level EOL census — reads BLOBS from a ref, never the local index.

Why this exists (H2301, residual of H2266 / FINDINGS §299 · §305 · §313):
`git ls-files --eol` reports the *index of the checkout you run it in*. That is
how H2266's session read "0 violations" while `origin/main` was carrying a
fully-CRLF 906 KB `FINDINGS.md` — three separate passes closed this class on a
per-checkout measurement that structurally cannot see a remote-side violation.

So this checker asks git for the **blob bytes at a ref** (`git cat-file --batch`
over `<ref>:<path>`) and counts CR **bytes**. It never consults the working tree
or the index, and it is therefore valid run from any clone, any worktree, or CI.

Measurement note, learned expensively during H2266: count CR **bytes**
(`tr -cd '\\r' | wc -c`), never matching lines. `grep -c $'\\r'` gave a wrong
answer on these files and nearly produced a wrong finding.

Usage
-----
    python tools/eol_census.py                     # census origin/main
    python tools/eol_census.py --ref HEAD          # census another ref
    python tools/eol_census.py --history FINDINGS.md
                                                   # forensic: per-commit CR
                                                   # counts + author + subject,
                                                   # to NAME a bad writer

Exit codes: 0 clean · 1 violations found · 2 usage/environment error.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import threading
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def git_bytes(repo: Path, *args: str, stdin: bytes | None = None) -> bytes:
    """Run git and return raw stdout bytes (blob content must not be decoded).

    The org rule is `encoding='utf-8'` on output-capturing subprocess calls; this
    one is a DELIBERATE exception. Decoding here would destroy the very bytes the
    census measures — a CR byte must be counted in the blob, not in some decoded
    approximation of it. Decoding happens explicitly, per call site, in git_text.
    """
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): "
            f"{proc.stderr.decode('utf-8', 'replace').strip()}"
        )
    return proc.stdout


def git_text(repo: Path, *args: str, stdin: bytes | None = None) -> str:
    return git_bytes(repo, *args, stdin=stdin).decode("utf-8", "replace")


def ls_tree_paths(repo: Path, ref: str) -> list[str]:
    out = git_bytes(repo, "ls-tree", "-r", "-z", "--name-only", ref)
    return [p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p]


def eol_attrs(repo: Path, paths: list[str]) -> dict[str, tuple[str, str]]:
    """Map path -> (text, eol) as the working-tree .gitattributes assigns them.

    `check-attr` consults the working-tree .gitattributes, which is the same file
    the ref carries in every normal case; a divergence there is itself worth
    seeing, so it is not worked around here.
    """
    if not paths:
        return {}
    stdin = b"\0".join(p.encode("utf-8", "surrogateescape") for p in paths) + b"\0"
    out = git_bytes(repo, "check-attr", "--stdin", "-z", "text", "eol", stdin=stdin)
    fields = out.split(b"\0")
    attrs: dict[str, tuple[str, str]] = {}
    # -z output is a flat NUL stream of (path, attr, value) triples, one triple
    # per requested attribute per path.
    for i in range(0, len(fields) - 2, 3):
        raw_path, attr, value = fields[i], fields[i + 1], fields[i + 2]
        path = raw_path.decode("utf-8", "surrogateescape")
        text, eol = attrs.get(path, ("unspecified", "unspecified"))
        if attr == b"text":
            text = value.decode()
        elif attr == b"eol":
            eol = value.decode()
        attrs[path] = (text, eol)
    return attrs


def cr_counts_multi(repo: Path, specs: list[tuple[str, str]]) -> dict[tuple[str, str], int]:
    """CR bytes for each (ref, path) blob, STREAMED from one cat-file --batch.

    Streamed, not buffered. The first version captured the whole `--batch` output
    into one bytes object, which is fine for Uprava (~4 700 paths) and fatal at
    org scale: `kosha` has 51 269 tracked files, so the capture tried to hold the
    entire text content of the repository in memory at once and simply never
    returned. A checker that hangs on the largest repo in the fleet is one nobody
    can deploy, so this reads blob-by-blob and keeps at most one body live.

    Returns -1 for paths git would treat as binary — see is_binary.
    """
    if not specs:
        return {}

    proc = subprocess.Popen(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    counts: dict[tuple[str, str], int] = {}

    def feed() -> None:
        try:
            for ref, path in specs:
                proc.stdin.write(f"{ref}:{path}\n".encode("utf-8", "surrogateescape"))
            proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass  # reader side died; the read loop below reports the short stream

    # git blocks writing its output once the pipe buffer fills, so the request
    # stream has to be fed from another thread or the two sides deadlock — the
    # classic subprocess pipe deadlock, and it bites at exactly the repo sizes
    # that motivated the rewrite.
    writer = threading.Thread(target=feed, daemon=True)
    writer.start()

    out = proc.stdout
    for key in specs:
        header = out.readline()
        if not header:
            break
        parts = header.decode("utf-8", "replace").rstrip("\n").rsplit(" ", 2)
        if len(parts) != 3 or parts[1] != "blob":
            # "missing" / non-blob: git emits no body, so the stream stays aligned.
            continue
        size = int(parts[2])
        body = out.read(size)
        out.read(1)  # trailing newline after the body
        counts[key] = -1 if is_binary(body) else body.count(b"\r")

    writer.join(timeout=5)
    proc.stdout.close()
    proc.wait(timeout=30)
    return counts


def is_text_tracked(text: str) -> bool:
    """Should git store this path's blob with LF endings?

    Yes whenever the `text` attribute is set or auto-detected — `eol` is NOT the
    selector. `eol` decides what the WORKING TREE gets on checkout; the blob is
    LF either way. Selecting on `eol == "lf"` would silently exempt every
    `eol=crlf` path (`*.cmd`, `*.bat`) from a check that still applies to them.
    """
    return text in ("set", "auto")


def is_binary(body: bytes) -> bool:
    """git's own heuristic: a NUL byte within the first 8000 bytes (convert.c).

    This matters because `* text=auto eol=lf` ASSIGNS eol=lf to every path in the
    repo, including .docx and .pyc — but `text=auto` makes git skip conversion
    for content it detects as binary, so those CR bytes are correct and expected.
    Flagging them would bury the one real violation under ~500 false positives,
    which is how a census stops being read.
    """
    return b"\0" in body[:8000]


def cr_candidates(repo: Path, ref: str) -> list[str]:
    """Paths at `ref` whose blob contains ANY CR byte — found C-side by git grep.

    The performance load-bearing step. Byte-counting every text blob in Python is
    fine for a hub repo and unusable at fleet scale: `kosha` (51 269 files, 292 MB
    of history) never finished, while this returns its single candidate in ~5 s.
    git does the whole scan in C and hands back a shortlist; exact CR *byte* counts
    are then taken only on that shortlist, so the precision that matters is kept.

    `-I` applies git's own binary detection, the same rule the census uses for
    content exemption, so the prefilter cannot hide a text file. `-F` with a
    literal CR avoids depending on a PCRE-enabled git build.
    """
    proc = subprocess.run(
        ["git", "-C", str(repo), "grep", "-I", "-l", "-z", "-F", "\r", ref],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    # exit 1 == "no matches", which is the clean case, not an error
    if proc.returncode not in (0, 1):
        raise RuntimeError(
            f"git grep failed ({proc.returncode}): "
            f"{proc.stderr.decode('utf-8', 'replace').strip()}"
        )
    prefix = f"{ref}:".encode("utf-8", "surrogateescape")
    out = []
    for field in proc.stdout.split(b"\0"):
        if not field:
            continue
        if field.startswith(prefix):
            field = field[len(prefix):]
        out.append(field.decode("utf-8", "surrogateescape"))
    return out


def cmd_census(repo: Path, ref: str, quiet: bool) -> int:
    all_paths = ls_tree_paths(repo, ref)
    attrs = eol_attrs(repo, all_paths)
    text_paths = {p for p, (text, _eol) in attrs.items() if is_text_tracked(text)}

    # Prefilter C-side, then byte-count only the candidates.
    candidates = [p for p in cr_candidates(repo, ref) if p in text_paths]
    counts = cr_counts_multi(repo, [(ref, p) for p in candidates])

    bad: list[tuple[int, str]] = []
    skipped_binary = 0
    for (_ref, path), n in counts.items():
        if n == -1:
            skipped_binary += 1
        elif n:
            bad.append((n, path))
    bad.sort(reverse=True)

    print(f"eol census · ref={ref} · {len(text_paths)} text-attributed of {len(all_paths)} paths,"
          f" read as BLOBS (not the index) · {len(candidates)} CR candidate(s) byte-counted"
          + (f" · {skipped_binary} binary" if skipped_binary else ""))
    if not bad:
        print("OK — 0 CR bytes across every text-attributed path at this ref.")
        return 0

    print(f"VIOLATION — {len(bad)} path(s) carry CR bytes in the blob at {ref}:")
    for n, p in bad:
        text = attrs.get(p, ("?", "?"))[0]
        print(f"  {n:>9,} CR  {p}  (text: {text})")
    if not quiet:
        print()
        print("Fix (must land as a FAST-FORWARD, never a rebase — FINDINGS §305):")
        print("  git add --renormalize -- <path> && git commit -m 'fix(eol): renormalize to LF'")
    return 1


def cmd_changed(repo: Path, ref: str, since: str, quiet: bool) -> int:
    """Census only the paths `since..ref` touches — the push-gate mode.

    A full-repo census is ~34 s here, which is too slow to sit in front of every
    push; a push can only introduce a violation through a path it changes, so
    checking that set is the same guarantee at a fraction of the cost. The full
    scan stays available for CI and for catching blobs that arrived by some route
    that never ran this hook.
    """
    out = git_bytes(repo, "diff", "--name-only", "-z", f"{since}...{ref}")
    changed = [p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p]
    if not changed:
        print(f"eol census · {since}..{ref} · no paths changed")
        return 0

    attrs = eol_attrs(repo, changed)
    paths = [p for p, (text, _eol) in attrs.items() if is_text_tracked(text)]
    counts = cr_counts_multi(repo, [(ref, p) for p in paths])
    dirty_now = {p: n for (_r, p), n in counts.items() if n > 0}

    # RATCHET, not a snapshot. A path that was ALREADY CRLF at `since` is
    # pre-existing debris, not something this push introduced — blocking on it
    # would hand a maintainer a refusal for a defect they did not create, which
    # is the failure mode that got the stale-base guard demoted to WARN and that
    # gates `changelog-dupe-guard` on a content check. Measured 06-08-2026:
    # IndologyScholars carries 1 311 such paths, so without this the gate would
    # be undeployable in exactly the repo that needs it most. Only a path that is
    # clean-or-absent at `since` and CR-dirty at `ref` is this push's doing.
    before = cr_counts_multi(repo, [(since, p) for p in dirty_now])
    preexisting = {p for p in dirty_now if before.get((since, p), 0) > 0}
    bad = sorted(((n, p) for p, n in dirty_now.items() if p not in preexisting), reverse=True)

    print(f"eol census · {since}..{ref} · {len(changed)} changed path(s), "
          f"{len(paths)} text-attributed, read as BLOBS (not the index)"
          + (f" · {len(preexisting)} pre-existing CRLF path(s) ignored" if preexisting else ""))
    if not bad:
        print("OK — this push introduces no new CR bytes.")
        if preexisting:
            print(f"     ({len(preexisting)} touched path(s) were already CRLF before it — "
                  f"pre-existing, not blocked; renormalize separately.)")
        return 0

    print(f"VIOLATION — {len(bad)} path(s) would NEWLY land CR bytes in the blob:")
    for n, p in bad:
        print(f"  {n:>9,} CR  {p}  (text: {attrs.get(p, ('?', '?'))[0]})")
    if not quiet:
        print()
        print("A CRLF blob on an eol=lf path cannot be repaired by `git checkout` —")
        print("the defect is in the stored object, and every later checkout reports")
        print("the file as dirty forever (FINDINGS §299 · §305 · §313).")
        print("Fix before pushing:")
        print("  git add --renormalize -- <path> && git commit --amend --no-edit")
    return 1


def cmd_history(repo: Path, ref: str, path: str) -> int:
    """Per-commit CR counts for one path — the forensic half.

    A writer that stores CRLF blobs shows up as a run of non-zero rows; the
    author/subject columns are what actually name it.
    """
    revs = git_text(repo, "rev-list", "--reverse", ref, "--", path).split()
    if not revs:
        print(f"no commits touch {path} at {ref}", file=sys.stderr)
        return 2

    # One cat-file process for every (rev, path) blob and one git log for every
    # commit's metadata. The naive one-subprocess-per-commit shape took minutes
    # on a 424-commit path, which is long enough that nobody runs the forensic.
    counts = cr_counts_multi(repo, [(r, path) for r in revs])
    meta = {}
    log = git_text(
        repo, "log", "--no-walk=unsorted", "--format=%H%x09%h%x09%ad%x09%an%x09%s",
        "--date=format:%Y-%m-%d %H:%M", *revs, "--",
    )
    for line in log.splitlines():
        parts = line.split("\t", 4)
        if len(parts) == 5:
            meta[parts[0]] = parts[1:]

    print(f"eol history · {path} · {len(revs)} commits at {ref}")
    print(f"{'commit':<10} {'CR':>8}  {'date':<16} {'author':<22} subject")
    flagged = 0
    for rev in revs:
        n = counts.get((rev, path), 0)
        short, date, author, subject = meta.get(rev, [rev[:9], "", "", ""])
        if n:
            flagged += 1
        print(f"{short:<10} {n:>8,}  {date:<16} {author[:22]:<22} {subject[:60]}"
              f"{'  <-- CRLF' if n else ''}")

    print()
    print(f"{flagged} of {len(revs)} commits stored a CRLF blob for {path}.")
    return 1 if flagged else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".", help="repository path (default: cwd)")
    ap.add_argument("--ref", default="origin/main", help="ref to read blobs from (default: origin/main)")
    ap.add_argument("--history", metavar="PATH", help="forensic per-commit CR counts for ONE path")
    ap.add_argument("--changed-since", metavar="REF",
                    help="census only paths changed REF..--ref (the fast push-gate mode)")
    ap.add_argument("--quiet", action="store_true", help="suppress the remediation hint")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    try:
        if args.history:
            return cmd_history(repo, args.ref, args.history)
        if args.changed_since:
            return cmd_changed(repo, args.ref, args.changed_since, args.quiet)
        return cmd_census(repo, args.ref, args.quiet)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
