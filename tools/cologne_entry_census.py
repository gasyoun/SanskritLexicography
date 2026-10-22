#!/usr/bin/env python3
"""Per-year census of Cologne csl-orig entry-level corrections (H7223).

Reads the git history of a local csl-orig clone (READ-ONLY) and emits, per
correction event, the change-file record that was touched:

    dc_year  dict  L-id  headword  add|mod  csl-corrections-issue  commit_sha  commit_date

The axis year is the DC date from the commit subject ("DC 28 July 2026"),
falling back to the commit date when the subject carries none. Record
attribution walks each diff hunk (-U6 context) and attributes added content
lines to the nearest preceding ``<L>`` record header; a hunk whose context
reaches no ``<L>`` line lands in the ``?`` residual bucket and is counted,
never silently dropped.

Deterministic by construction: the output depends only on the clone's git
history, rows are sorted, and ``--check`` verifies a byte-identical re-run.
"""
import argparse
import collections
import gzip
import re
import subprocess
import sys
from pathlib import Path

CORE_DICTS = ("mw", "mw72", "ap90", "pw", "pwg", "bhs")
DEFAULT_CLONE = Path.home() / "Documents" / "GitHub" / "csl-orig"

L_RE = re.compile(r"^<L>([^<\s]+)")
K1_RE = re.compile(r"<k1>([^<]*)")
ISSUE_RE = re.compile(r"issues/(\d+)")
DC_RE = re.compile(r"DC \d+ \w+ (\d{4})")
HUNK_RE = re.compile(r"^@@")
FILE_RE = re.compile(r"^diff --git a/v02/([a-z0-9_]+)/")
SEP = "\x01"


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


def run_git_log(clone: Path):
    cmd = [
        "git", "-C", str(clone), "log", "--no-color", "--date=short",
        f"--pretty=format:{SEP}%H{SEP}%ad{SEP}%s", "-p", "-U6", "--", "v02",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True,
                            errors="replace", bufsize=1 << 20)
    for line in proc.stdout:
        yield line.rstrip("\n")
    proc.stdout.close()
    if proc.wait() != 0:
        raise SystemExit(f"git log failed in {clone}")


def census(clone: Path):
    """Stream one git log -p pass; return (rows, stats)."""
    rows = []
    stats = collections.Counter()
    cur = None            # (sha, dc_year, issue)
    cur_dict = None
    last_l = None         # [L-id, headword]
    seen = set()          # (sha, dict, L) already emitted
    in_hunk = False

    for line in run_git_log(clone):
        if line.startswith(SEP):
            parts = line.split(SEP)
            # '', sha, date, subject
            sha, date, subject = parts[1], parts[2], parts[3] if len(parts) > 3 else ""
            commit_year = date[:4]
            issue_m = ISSUE_RE.search(subject)
            cur = (sha, dc_year_of(subject, commit_year), issue_m.group(1) if issue_m else "", date)
            cur_dict = None
            last_l = None
            in_hunk = False
            stats["commits"] += 1
            continue
        m = FILE_RE.match(line)
        if m:
            cur_dict = m.group(1)
            last_l = None
            in_hunk = False
            stats[f"files:{cur_dict}"] += 1
            continue
        if line.startswith(("index ", "+++ ", "--- ")):
            continue
        if HUNK_RE.match(line):
            in_hunk = True
            continue
        if not in_hunk or cur is None or cur_dict is None or not line:
            continue
        polarity, body = line[0], line[1:]
        lm = L_RE.match(body)
        if lm and polarity in (" ", "+"):
            new_l = [lm.group(1), ""]
            km = K1_RE.search(body)
            if km:
                new_l[1] = km.group(1)
            if polarity == "+":
                # a record header added by this commit: new record
                key = (cur[0], cur_dict, new_l[0])
                if key not in seen:
                    seen.add(key)
                    rows.append((cur[1], cur_dict, new_l[0], new_l[1], "add", cur[2], cur[0], cur[3]))
                    stats["entries_add"] += 1
                    stats[f"add:{cur_dict}"] += 1
            last_l = new_l
            continue
        km = K1_RE.search(body)
        if km and last_l is not None and not last_l[1]:
            last_l[1] = km.group(1)
        if polarity == "+" and body.strip() and body.strip() != "<LEND>":
            if last_l is not None:
                key = (cur[0], cur_dict, last_l[0])
                if key not in seen:
                    seen.add(key)
                    rows.append((cur[1], cur_dict, last_l[0], last_l[1], "mod", cur[2], cur[0], cur[3]))
                    stats["entries_mod"] += 1
                    stats[f"mod:{cur_dict}"] += 1
            else:
                stats["entries_unattributed"] += 1
    return rows, stats


def rollup(rows, stats):
    per_year = collections.defaultdict(lambda: collections.Counter())
    per_year_commits = collections.defaultdict(set)
    for year, d, _l, _hw, kind, _iss, sha, _date in rows:
        per_year[year]["entries"] += 1
        per_year[year][f"kind_{kind}"] += 1
        per_year_commits[year].add(sha)
    lines = ["== per DC-year: commits / dicts-touched / entries (add+mod) =="]
    for year in sorted(per_year):
        dicts = len({d for y, d, *_ in rows if y == year})
        c = per_year[year]
        lines.append(
            f"{year}  commits={len(per_year_commits[year])}  dicts={dicts}  "
            f"entries={c['entries']} (add={c['kind_add']} mod={c['kind_mod']})"
        )
    return "\n".join(lines)


def matrix(rows, years):
    core = collections.defaultdict(int)
    for year, d, *_ in rows:
        if year in years and d in CORE_DICTS:
            core[(year, d)] += 1
    hdr = "year  " + "  ".join(f"{d:>6}" for d in CORE_DICTS)
    lines = ["== core dict entries per year ==" , hdr]
    for year in sorted(years):
        lines.append(f"{year}  " + "  ".join(f"{core.get((year, d), 0):>6}" for d in CORE_DICTS))
    return "\n".join(lines)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--clone", type=Path, default=DEFAULT_CLONE, help="path to local csl-orig clone (read-only)")
    ap.add_argument("--out", type=Path, default=None, help="TSV output path (default: reports/cologne_entry_census.tsv beside the repo root)")
    ap.add_argument("--check", action="store_true", help="re-run and verify byte-identical output vs the existing file")
    ap.add_argument("--selftest", action="store_true", help="parse a synthetic diff fixture and pin the attribution rules")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        print("selftest PASS")
        return

    rows, stats = census(args.clone)
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
        unattr = stats.get("entries_unattributed", 0)
        total = stats.get("entries_add", 0) + stats.get("entries_mod", 0)
        print(f"== attribution residual: {unattr} added lines without a <L> in context "
              f"({100.0 * unattr / max(total + unattr, 1):.2f}% of {total + unattr}) ==")
        old = read_out(out)
        if old != content:
            sys.exit(f"CHECK FAIL: {out} differs from a fresh re-run ({len(old.splitlines())} vs {len(content.splitlines())} lines)")
        print(f"check PASS: {out} byte-identical on re-run ({len(rows)} rows)")
        return
    write_out(out, content)
    print(rollup(rows, stats))
    years = sorted({r[0] for r in rows})
    print(matrix(rows, years))
    unattr = stats.get("entries_unattributed", 0)
    total = stats.get("entries_add", 0) + stats.get("entries_mod", 0)
    print(f"== attribution residual: {unattr} added lines without a <L> in context "
          f"({100.0 * unattr / max(total + unattr, 1):.2f}% of {total + unattr}) — counted, not dropped ==")
    print(f"wrote {out} ({len(rows)} rows)")


def selftest():
    fixture = [
        f"{SEP}SHA1{SEP}2026-03-01{SEP}DC 28 February 2026. See https://github.com/sanskrit-lexicon/csl-corrections/issues/300",
        "diff --git a/v02/mw/mw.txt b/v02/mw/mw.txt",
        "--- a/v02/mw/mw.txt",
        "+++ b/v02/mw/mw.txt",
        "@@ -10,7 +10,8 @@",
        " <L>99<pc>1,1<k1>oldword<k2>a<e>1",
        " <s>oldword</s> ¦ old gloss text here",
        "+<s>oldword</s> ¦ corrected gloss with newword marker",
        " <LEND>",
        "+<L>100<pc>1,1<k1>newword<k2>b<e>1",
        "+<s>newword</s> ¦ brand new entry",
        "+<LEND>",
    ]

    seen_lines = iter(fixture)
    orig = run_git_log

    def fake(_clone):
        return seen_lines

    globals()["run_git_log"] = fake
    try:
        rows, stats = census(Path("."))
    finally:
        globals()["run_git_log"] = orig
    assert rows[0][:5] == ("2026", "mw", "99", "oldword", "mod"), rows[0]
    assert rows[1][:5] == ("2026", "mw", "100", "newword", "add"), rows[1]
    assert rows[0][5] == "300"
    assert stats["entries_mod"] == 1 and stats["entries_add"] == 1


if __name__ == "__main__":
    main()
