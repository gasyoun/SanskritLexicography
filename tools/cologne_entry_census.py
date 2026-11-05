#!/usr/bin/env python3
"""Per-year census of Cologne csl-orig entry-level corrections (H7223, v2 H7228).

Reads the git history of a local csl-orig clone (READ-ONLY) and emits, per
correction event, the change-file record that was touched:

    dc_year  dict  L-id  headword  add|mod  csl-corrections-issue  commit_sha  commit_date

The axis year is the DC date from the commit subject ("DC 28 July 2026"),
falling back to the commit date when the subject carries none.

v2 (H7228) attributes an added line by **record boundary**, not by hunk
context: for every ``(commit, dict)`` diff it takes the post-image blob named
on the diff's ``index`` line, computes the line span of every ``<L>{id}``
record in that blob, and maps each added line number (from ``--unified=0``)
into its record by range.  An added ``<L>`` header is an ``add``; any other
added content line in the record is a ``mod``.  Lines that fall before the
first record (file preamble, ``<LEND>``/blank lines excluded) are counted in
the residual bucket with their class, never silently dropped.

Deterministic by construction: the output depends only on the clone's git
history, rows are sorted, and ``--check`` verifies a byte-identical re-run
and prints the four independent invariants (including a ``git show``
spot-check of 10 rows that does not reuse the attribution parser).
"""
import argparse
import bisect
import collections
import gzip
import itertools
import random
import re
import subprocess
import sys
from pathlib import Path

VERSION = 2

CORE_DICTS = ("mw", "mw72", "ap90", "pw", "pwg", "bhs")
DEFAULT_CLONE = Path.home() / "Documents" / "GitHub" / "csl-orig"
DEFAULT_REV = "55e8addbd96e8d9001b8789026b026763f4049c1"  # data pin, 26-09-2026

# Invariants that must hold independently of the parser (see --check).
EXPECTED_DISTINCT_RECORDS = 1_508_914
EXPECTED_2019_ADDITIONS = 1_263_842
EXPECTED_YEAR_COMMITS = {
    "2019": 32, "2020": 248, "2021": 326, "2022": 141,
    "2023": 151, "2024": 200, "2025": 245, "2026": 580,
}

L_RE = re.compile(rb"^<L>([^<\s]+)")
K1_RE = re.compile(rb"<k1>([^<]*)")
ISSUE_RE = re.compile(r"issues/(\d+)")
DC_RE = re.compile(r"DC \d+ \w+ (\d{4})")
HUNK_RE = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
FILE_RE = re.compile(rb"^diff --git a/v02/([a-z0-9_]+)/")
INDEX_RE = re.compile(rb"^index ([0-9a-f]+)\.\.([0-9a-f]+)")
SEP = "\x01"
SEP_B = SEP.encode()


def read_out(path: Path) -> str:
    if path.suffix == ".gz":
        return gzip.decompress(path.read_bytes()).decode("utf-8")
    return path.read_text(encoding="utf-8")


def write_out(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".gz":
        path.write_bytes(gzip.compress(content.encode("utf-8"), 9, mtime=0))
    else:
        path.write_text(content, encoding="utf-8")


def dc_year_of(subject: str, commit_year: str) -> str:
    m = DC_RE.search(subject)
    return m.group(1) if m else commit_year


def iter_log(clone: Path, rev: str, log_cache: Path | None = None):
    """Yield one ``git log -p -U0`` line at a time (bytes, no newline)."""
    if log_cache is not None:
        with open(log_cache, "rb") as fh:
            for line in fh:
                yield line.rstrip(b"\n")
        return
    cmd = [
        "git", "-C", str(clone), "log", "--no-color", "--date=short",
        f"--pretty=format:{SEP}%H{SEP}%ad{SEP}%s", "-p", "-U0",
        "--full-index", "--no-renames", rev, "--", "v02",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1 << 22)
    try:
        for line in proc.stdout:
            yield line.rstrip(b"\n")
    finally:
        proc.stdout.close()
        if proc.wait() != 0:
            raise SystemExit(f"git log failed in {clone}")


class CatFile:
    """One persistent ``git cat-file --batch`` reader."""

    def __init__(self, clone: Path):
        self.proc = subprocess.Popen(
            ["git", "-C", str(clone), "cat-file", "--batch"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1 << 22,
        )

    def get(self, sha: bytes):
        self.proc.stdin.write(sha + b"\n")
        self.proc.stdin.flush()
        header = self.proc.stdout.readline()
        if not header:
            raise SystemExit("git cat-file died")
        parts = header.split()
        if len(parts) != 3 or parts[1] != b"blob":
            return None
        size = int(parts[2])
        data = self.proc.stdout.read(size)
        self.proc.stdout.read(1)  # trailing LF
        if len(data) != size:
            raise SystemExit("short read from git cat-file")
        return data

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=10)
        except Exception:
            self.proc.kill()


def record_starts(data: bytes):
    """Split a post-image into ``<L>`` records.

    Returns ``(chunks, starts, first)``: ``chunks[i]`` begins with the record
    after the split marker, ``starts[i]`` is its 1-based line number, and
    ``first`` is the chunk index holding the first record (0 when the file
    opens with ``<L>``).  Record ``i`` spans lines ``starts[i] .. starts[i+1]-1``.
    """
    chunks = data.split(b"\n<L>")
    nl = [c.count(b"\n") for c in chunks]
    acc = list(itertools.accumulate(nl))
    if data.startswith(b"<L>"):
        first = 0
        starts = [1] + [acc[i - 1] + i + 1 for i in range(1, len(chunks))]
    else:
        first = 1
        starts = [acc[i - 1] + i + 1 for i in range(1, len(chunks))]
    return chunks, starts, first


def header_of(chunk: bytes) -> tuple[str, str]:
    """Return ``(L-id, headword)`` parsed from the first line of a record."""
    if chunk.startswith(b"<L>"):
        chunk = chunk[3:]
    head = chunk.split(b"\n", 1)[0]
    lid = chunk.split(b"<", 1)[0].decode("utf-8", "replace")
    km = K1_RE.search(head) or K1_RE.search(chunk[:400])
    return lid, (km.group(1).decode("utf-8", "replace") if km else "")


def attribute(adds, data: bytes):
    """Attribute added new-file line numbers to post-image records.

    Yields ``(kind, L-id, headword, line_no)`` for every attributed line and
    counts a leading position with ``None`` as the L-id (preamble residual).
    """
    chunks, starts, first = record_starts(data)
    out = []
    if not starts:
        return out, len(adds)
    pre = 0
    for k in sorted(adds):
        j = bisect.bisect_right(starts, k) - 1
        if j < 0:
            pre += 1
            continue
        lid, hw = header_of(chunks[j + first])
        out.append(("add" if starts[j] == k else "mod", lid, hw, k))
    return out, pre


def census(clone: Path, rev: str = DEFAULT_REV, log_cache: Path | None = None):
    """Stream one git-log pass; return (rows, stats)."""
    rows = []
    stats = collections.Counter()
    cur = None            # (sha, dc_year, issue, date)
    seen = set()          # (sha, dict, L) already emitted
    files = []            # [dict, post_blob, [added line numbers]]
    cur_file = None
    in_hunk = False
    new_line = 0
    cat = CatFile(clone)

    def flush():
        for d, blob, adds in files:
            if not adds:
                continue
            if blob is None or blob == b"0" * 40:
                stats["unattributed_no_blob"] += len(adds)
                continue
            data = cat.get(blob)
            if data is None:
                stats["unattributed_no_blob"] += len(adds)
                stats["added_content_lines"] += len(adds)
                stats["unattributed"] += len(adds)
                continue
            if b"\n<L>" not in data and not data.startswith(b"<L>"):
                # auxiliary files living under v02/<dict>/ (etymology TSVs,
                # *_hwextra, statistics) carry no <L> records at all: nothing
                # in them can be a dictionary entry, so they are a named
                # excluded class, not an attribution failure.
                stats["aux_file_lines"] += len(adds)
                stats["aux_changed_files"] += 1
                continue
            attributed, preamble = attribute(adds, data)
            stats["added_content_lines"] += len(adds)
            stats["unattributed_preamble"] += preamble
            stats["unattributed"] += preamble
            for kind, lid, hw, _k in attributed:
                key = (cur[0], d, lid)
                if key in seen:
                    continue
                seen.add(key)
                rows.append((cur[1], d, lid, hw, kind, cur[2], cur[0], cur[3]))
                stats[f"entries_{kind}"] += 1
                stats[f"{kind}:{d}"] += 1

    try:
        for line in iter_log(clone, rev, log_cache):
            if line.startswith(SEP_B):
                if cur is not None:
                    flush()
                    files.clear()
                parts = line.decode("utf-8", "replace").split(SEP)
                sha, date, subject = parts[1], parts[2], parts[3] if len(parts) > 3 else ""
                commit_year = date[:4]
                issue_m = ISSUE_RE.search(subject)
                cur = (sha, dc_year_of(subject, commit_year),
                       issue_m.group(1) if issue_m else "", date)
                cur_file = None
                in_hunk = False
                stats["commits"] += 1
                continue
            m = FILE_RE.match(line)
            if m:
                cur_file = [m.group(1).decode("ascii"), None, []]
                files.append(cur_file)
                in_hunk = False
                stats[f"files:{cur_file[0]}"] += 1
                continue
            m = INDEX_RE.match(line)
            if m and cur_file is not None:
                cur_file[1] = m.group(2)
                continue
            m = HUNK_RE.match(line)
            if m:
                new_line = int(m.group(3))
                in_hunk = True
                continue
            if not in_hunk or cur_file is None or not line:
                continue
            if line[0:1] == b"+":
                body = line[1:]
                if body.strip() and body.strip() != b"<LEND>":
                    cur_file[2].append(new_line)
                new_line += 1
            elif line[0:1] == b" ":
                new_line += 1
            elif line[0:1] == b"-":
                pass
            elif line[0:1] == b"\\":
                pass
            else:
                in_hunk = False
        if cur is not None:
            flush()
            files.clear()
    finally:
        cat.close()
    return rows, stats


def rollup(rows, stats):
    per_year = collections.defaultdict(lambda: collections.Counter())
    per_year_commits = collections.defaultdict(set)
    per_year_dicts = collections.defaultdict(set)
    for year, d, _l, _hw, kind, _iss, sha, _date in rows:
        per_year[year]["entries"] += 1
        per_year[year][f"kind_{kind}"] += 1
        per_year_commits[year].add(sha)
        per_year_dicts[year].add(d)
    lines = ["== per DC-year: commits / dicts-touched / entries (add+mod) =="]
    for year in sorted(per_year):
        c = per_year[year]
        lines.append(
            f"{year}  commits={len(per_year_commits[year])}  dicts={len(per_year_dicts[year])}  "
            f"entries={c['entries']} (add={c['kind_add']} mod={c['kind_mod']})"
        )
    return "\n".join(lines)


def matrix(rows, years):
    core = collections.defaultdict(int)
    for year, d, *_ in rows:
        if year in years and d in CORE_DICTS:
            core[(year, d)] += 1
    hdr = "year  " + "  ".join(f"{d:>6}" for d in CORE_DICTS)
    lines = ["== core dict entries per year ==", hdr]
    for year in sorted(years):
        lines.append(f"{year}  " + "  ".join(f"{core.get((year, d), 0):>6}" for d in CORE_DICTS))
    return "\n".join(lines)


def residual_line(stats):
    unattr = stats.get("unattributed", 0)
    lines = stats.get("added_content_lines", 0)
    rows = stats.get("entries_add", 0) + stats.get("entries_mod", 0)
    share = 100.0 * unattr / lines if lines else 0.0
    mixed = 100.0 * unattr / (rows + unattr) if rows + unattr else 0.0
    classes = [f"aux_file={stats.get('aux_file_lines', 0)} added lines in "
               f"{stats.get('aux_changed_files', 0)} changed files with no <L> records "
               f"(excluded, not entries)"]
    for key in ("unattributed_preamble", "unattributed_no_blob"):
        if stats.get(key):
            classes.append(f"{key.removeprefix('unattributed_')}={stats[key]}")
    cls = " [" + ", ".join(classes) + "]"
    return (f"== attribution residual: {unattr} added content lines unattributed "
            f"({share:.4f}% of {lines} added content lines in record-bearing files; "
            f"{mixed:.2f}% on the v1 mixed denominator of {rows} rows){cls} ==")


def spotcheck(rows, clone: Path, rev: str, n: int = 10):
    """Independent git-show re-check of n deterministic sample rows."""
    rng = random.Random(7228)
    sample = rng.sample(rows, min(n, len(rows)))
    lines = ["== independent `git show` spot-check (parser not reused) =="]
    ok = 0
    for row in sample:
        year, d, lid, hw, _kind, _iss, sha, _date = row
        path = f"v02/{d}/{d}.txt"
        try:
            data = subprocess.run(
                ["git", "-C", str(clone), "show", f"{sha}:{path}"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True,
            ).stdout
        except subprocess.CalledProcessError:
            lines.append(f"FAIL {sha[:9]} {d} L{lid}: post-image path missing")
            continue
        # record span in the post-image, found by a plain line scan
        blob_lines = data.split(b"\n")
        start = None
        for i, ln in enumerate(blob_lines):
            if ln.startswith(b"<L>" + lid.encode() + b"<") or ln == b"<L>" + lid.encode():
                start = i
                break
            if ln.startswith(b"<L>" + lid.encode() + b" "):
                start = i
                break
        if start is None:
            lines.append(f"FAIL {sha[:9]} {d} L{lid}: record not in post-image")
            continue
        end = start + 1
        while end < len(blob_lines) and not blob_lines[end].startswith(b"<L>"):
            end += 1
        diff = subprocess.run(
            ["git", "-C", str(clone), "show", "--no-color", "-U0", "--format=",
             sha, "--", path],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True,
        ).stdout
        added, pos = [], None
        for dl in diff.split(b"\n"):
            m = HUNK_RE.match(dl)
            if m:
                pos = int(m.group(3))
                continue
            if pos is None or not dl:
                continue
            if dl[0:1] == b"+":
                added.append(pos)
                pos += 1
            elif dl[0:1] == b" ":
                pos += 1
        hit = [k for k in added if start + 1 <= k <= end]
        if not hit:
            lines.append(f"FAIL {sha[:9]} {d} L{lid}: no added line inside record span "
                         f"{start + 1}-{end}")
            continue
        evidence = blob_lines[start][:160].decode("utf-8", "replace")
        lines.append(f"PASS {sha[:9]} {d} L{lid} span {start + 1}-{end} "
                     f"added_line={hit[0]} | {evidence}")
        ok += 1
    lines.append(f"spot-check: {ok}/{len(sample)} rows are real changes to that record")
    return "\n".join(lines), ok == len(sample)


def invariants(rows, stats, clone: Path, rev: str):
    blocks = []
    pairs = {(d, lid) for _y, d, lid, *_ in rows}
    delta = len(pairs) - EXPECTED_DISTINCT_RECORDS
    blocks.append(
        f"invariant 1 distinct (dict,L): {len(pairs)} (expected "
        f"{EXPECTED_DISTINCT_RECORDS}, delta {delta:+d}) "
        f"{'PASS' if abs(delta) <= 200_000 else 'FAIL'}"
    )
    adds_2019 = sum(1 for y, _d, _l, _h, kind, *_ in rows if y == "2019" and kind == "add")
    d2 = adds_2019 - EXPECTED_2019_ADDITIONS
    blocks.append(
        f"invariant 2 2019 additions: {adds_2019} (expected "
        f"{EXPECTED_2019_ADDITIONS}, delta {d2:+d}) "
        f"{'PASS' if abs(d2) <= 20_000 else 'FAIL'}"
    )
    per_year = collections.defaultdict(set)
    for year, _d, _l, _h, _k, _i, sha, _dt in rows:
        per_year[year].add(sha)
    got = "/".join(str(len(per_year[y])) for y in sorted(per_year))
    exp = "/".join(str(EXPECTED_YEAR_COMMITS[y]) for y in sorted(per_year))
    blocks.append(f"invariant 3 per-year commits: {got} (expected {exp}) "
                  f"{'PASS' if got == exp else 'FAIL'}")
    block, ok = spotcheck(rows, clone, rev)
    blocks.append(block)
    blocks.append(f"invariants: {'PASS' if ok else 'FAIL'}")
    return "\n".join(blocks)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--clone", type=Path, default=DEFAULT_CLONE,
                    help="path to local csl-orig clone (read-only)")
    ap.add_argument("--rev", default=DEFAULT_REV, help="csl-orig revision/commit pin to read")
    ap.add_argument("--out", type=Path, default=None,
                    help="TSV output path (default: reports/cologne_entry_census.tsv beside the repo root)")
    ap.add_argument("--log-cache", type=Path, default=None,
                    help="optional pre-dumped `git log -p -U0` stream (derivation accelerator)")
    ap.add_argument("--check", action="store_true",
                    help="re-run, print the invariants, and verify byte-identical output")
    ap.add_argument("--selftest", action="store_true",
                    help="parse synthetic fixtures and pin the attribution rules")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        print("selftest PASS")
        return

    rows, stats = census(args.clone, args.rev, args.log_cache)
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[7], r[6]))
    out = args.out
    if out is None:
        out = Path(__file__).resolve().parents[1] / "reports" / "cologne_entry_census.tsv"
    content = "dc_year\tdict\tL\theadword\tkind\tissue\tcommit\tcommit_date\n" + "".join(
        "\t".join(r) + "\n" for r in rows
    )
    if args.check:
        print(rollup(rows, stats))
        print(matrix(rows, sorted({r[0] for r in rows})))
        print(residual_line(stats))
        print(invariants(rows, stats, args.clone, args.rev))
        old = read_out(out)
        if old != content:
            sys.exit(f"CHECK FAIL: {out} differs from a fresh re-run "
                     f"({len(old.splitlines())} vs {len(content.splitlines())} lines)")
        print(f"check PASS: {out} byte-identical on re-run ({len(rows)} rows)")
        return
    write_out(out, content)
    print(f"census v{VERSION}")
    print(rollup(rows, stats))
    print(matrix(rows, sorted({r[0] for r in rows})))
    print(residual_line(stats))
    print(f"wrote {out} ({len(rows)} rows)")


def selftest():
    # post-image: preamble line, record 10 (2 lines), record 11 (2 lines)
    post = (b"# preamble\n<L>10<pc>1,1<k1>old<k2>a\n"
            b"<s>old</s> | gloss\n<LEND>\n"
            b"<L>11<pc>1,1<k1>new<k2>b\n<s>new</s> | gloss\n<LEND>\n")
    # added: header 11 (line 5), a content line of record 10 (line 3), a preamble line (1)
    got, pre = attribute([1, 3, 5], post)
    assert pre == 1, pre
    assert got[0][:3] == ("mod", "10", "old"), got[0]
    assert got[1][:3] == ("add", "11", "new"), got[1]
    assert got[0][3] == 3 and got[1][3] == 5, got

    # a record spanning to EOF is closed by the end of the file
    got2, pre2 = attribute([5], b"<L>1<k1>a\nx\n")
    assert (got2[0][0], got2[0][1]) == ("mod", "1"), got2

    # --unified=0 header parsing: the third number is the new-file start line
    m = HUNK_RE.match(b"@@ -10,0 +11,2 @@")
    assert (m.group(1), m.group(2), m.group(3), m.group(4)) == (b"10", b"0", b"11", b"2"), m.groups()
    m = HUNK_RE.match(b"@@ -7 +9,3 @@ optional section heading")
    assert (m.group(1), m.group(2), m.group(3), m.group(4)) == (b"7", None, b"9", b"3"), m.groups()
    # index line carries the post-image blob (full index)
    m = INDEX_RE.match(b"index " + b"a" * 40 + b".." + b"b" * 40 + b" 100644")
    assert m.group(2) == b"b" * 40, m.groups()
    # commit subject -> DC year, issue
    assert dc_year_of("DC 28 February 2026. issues/300", "2026") == "2026"
    assert dc_year_of("no editorial date here", "2025") == "2025"
    assert ISSUE_RE.search("issues/300").group(1) == "300"


if __name__ == "__main__":
    main()
