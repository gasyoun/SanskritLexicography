#!/usr/bin/env python3
"""Per-year census of Cologne csl-orig entry-level corrections (H7223/H7228).

Reads the git history of a local csl-orig clone (READ-ONLY) and emits, per
correction event, the change-file record that was touched:

    dc_year  dict  L-id  headword  add|mod  csl-corrections-issue  commit_sha  commit_date

The axis year is the DC date from the commit subject ("DC 28 July 2026"),
falling back to the commit date when the subject carries none.

Attribution (v2, H7228) is by **record boundary**, not by hunk context:
the tool walks the diffs oldest-first and keeps, for every changed file, the
post-image line array together with the record index of every line — the span
of each ``<L>{id}`` record, closed by its ``<LEND>``.  Every line added by
``git diff --unified=0`` is mapped by its new line number into that span:
a ``+`` line that *is* an ``<L>`` header is an ``add``; any other added
content line inside the span is a ``mod``.  Added non-blank lines outside any
record (file preamble / section ``<H>`` lines) are counted as the residual
class, never silently dropped.  The post-image is maintained incrementally
from the diffs and pinned to the blob SHA git reports for it; a mismatch
(merge/reorder/rename) triggers a ``git cat-file`` resync of that one file.

Deterministic by construction: the output depends only on the clone's git
history and the requested revision, rows are sorted, and ``--check`` verifies
a byte-identical re-run plus the four independent invariants from the H7223
report (which compared the parser against the previous ``-U6`` implementation
and the source history, not against this parser).
"""
import argparse
import collections
import gzip
import re
import subprocess
import sys
from array import array
from pathlib import Path

CORE_DICTS = ("mw", "mw72", "ap90", "pw", "pwg", "bhs")
DEFAULT_CLONE = Path.home() / "Documents" / "GitHub" / "csl-orig"
ZERO_SHA = "0" * 40

def _is_zero(sha):
    return sha is not None and set(sha) == {"0"}

# Invariants pinned from the H7223 report (v1, -U6 parser, same csl-orig pin).
EXPECTED_DISTINCT = 1_508_914
EXPECTED_2019_ADD = 1_263_842
EXPECTED_YEAR_COMMITS = {
    "2019": 32, "2020": 248, "2021": 326, "2022": 141,
    "2023": 151, "2024": 200, "2025": 245, "2026": 580,
}
RESIDUAL_TARGET_PCT = 1.0

L_RE = re.compile(r"^<L>([^<\s]+)")
K1_RE = re.compile(r"<k1>([^<]*)")
ISSUE_RE = re.compile(r"issues/(\d+)")
DC_RE = re.compile(r"DC \d+ \w+ (\d{4})")
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
FILE_RE = re.compile(r"^diff --git a/(v02/([a-z0-9_]+)/.+?) b/")
RENAME_RE = re.compile(r"^rename to (v02/[a-z0-9_]+/.+)$")
INDEX_RE = re.compile(r"^index ([0-9a-f]+)\.\.([0-9a-f]+)")
SEP = "\x01"
KIND_NORMAL, KIND_HEADER, KIND_LEND = 0, 1, 2


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


def run_git_log(clone: Path, rev: str):
    """Oldest-first commit stream with context-free diffs.

    ``--full-index`` gives full new-blob hashes in the ``index`` line, which
    pins the post-image this parser reconstructs; ``--reverse --topo-order``
    lets the record arrays be carried forward from the root commit.
    """
    cmd = [
        "git", "-C", str(clone), "log", "--no-color", "--date=short",
        "--reverse", "--topo-order", "--full-index", "-p", "-U0",
        "--pretty=format:%x01%H%x01%ad%x01%s", rev, "--", "v02",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True,
                            errors="replace", bufsize=1 << 20)
    for line in proc.stdout:
        yield line.rstrip("\n")
    proc.stdout.close()
    if proc.wait() != 0:
        raise SystemExit(f"git log failed in {clone} at {rev}")


def _alloc_head(heads, intern, l_id, hw):
    """One head entry per distinct (l_id, hw); rebuilds reuse entries.

    An EMPTY headword is never interned (per-occurrence, like v1) so a late
    ``<k1>`` patch cannot retarget an entry shared across dicts.
    """
    if hw:
        rid = intern.get((l_id, hw))
        if rid is None:
            rid = len(heads)
            heads.append((l_id, hw))
            intern[(l_id, hw)] = rid
        return rid
    rid = len(heads)
    heads.append((l_id, hw))
    return rid


def _patch_head(heads, intern, rid, hw):
    l_id = heads[rid][0]
    heads[rid] = (l_id, hw)
    intern[(l_id, hw)] = rid


def blob_lines(clone: Path, sha: str):
    """Return a blob's lines as ``str`` (used only for resync)."""
    out = subprocess.run(
        ["git", "-C", str(clone), "cat-file", "blob", sha],
        stdout=subprocess.PIPE, check=True,
    ).stdout
    return out.decode("utf-8", "replace").split("\n")


def build_state_from_blob(clone: Path, sha: str, heads, intern):
    """Full record map of one post-image blob: (ids, kinds).

    ``heads`` is the global header table; a header line seen in a blob
    allocates (or reuses) an entry here so later ``mod`` rows can carry its
    headword.
    """
    ids = array("i")
    kinds = bytearray()
    cur = -1
    for body in blob_lines(clone, sha):
        body = body.rstrip("\r")
        if L_RE.match(body):
            kinds.append(KIND_HEADER)
            rid = _alloc_head(heads, intern, L_RE.match(body).group(1), _k1_of(body))
            ids.append(rid)
            cur = rid
        elif body.startswith("<LEND>"):
            kinds.append(KIND_LEND)
            ids.append(cur)
            cur = -1
        else:
            kinds.append(KIND_NORMAL)
            ids.append(cur)
    return ids, kinds


class State:
    __slots__ = ("blob", "ids", "kinds")

    def __init__(self, blob="", ids=None, kinds=None):
        self.blob = blob
        self.ids = ids if ids is not None else array("i")
        self.kinds = kinds if kinds is not None else bytearray()


def rebuild_from_blob(clone: Path, sha: str, heads, intern):
    """Resync a file state from one blob; header ids are interned per (L, hw)."""
    ids, kinds = build_state_from_blob(clone, sha, heads, intern)
    return State(sha, ids, kinds)


def census(clone: Path, rev: str):
    """Stream one oldest-first -U0 pass; return (rows, heads, stats)."""
    rows = []
    heads = []                 # rid -> (L-id, headword) or None
    intern = {}                # (L-id, headword) -> rid
    stats = collections.Counter()
    state = {}                 # path -> State
    seen = set()               # (dict, L) within the current commit
    cur = None                 # (sha, dc_year, issue, date)
    dict_of = {}               # path -> dict
    cur_path = None
    cur_dict = None
    cur_old = cur_new = None
    hunk = None                # (a, b, c, d)
    buf = []                   # added bodies of the open hunk
    in_hunk = False
    file_delta = 0              # net line delta of hunks applied so far in this file diff
    file_verified = False       # state checked against cur_old for this file diff?
    residual_class = collections.Counter()

    def flush_hunk():
        nonlocal buf, hunk, in_hunk, file_delta, file_verified
        if hunk is None or cur_path is None:
            buf = []
            return
        a, b, _c, _d = hunk
        # Verify the carried state against the pre-image blob ONCE per file
        # diff (the `index` line is per-file, not per-hunk).  Later hunks of
        # the same diff apply incrementally, with `a` re-based by the delta
        # of the hunks before them: git hunk positions are pre-image lines.
        if not file_verified:
            st = state.get(cur_path)
            if _is_zero(cur_old):
                st = State()      # new file (A) or re-add: empty pre-image
                state[cur_path] = st
            elif st is None or st.blob != cur_old:
                # first sight of this path or merge/reorder/rename drift:
                # rebuild the post-image record map from the real old blob.
                st = rebuild_from_blob(clone, cur_old, heads, intern)
                stats["blob_resync"] += 1
                state[cur_path] = st
            file_verified = True
            file_delta = 0
        else:
            st = state[cur_path]
        ids, kinds = st.ids, st.kinds
        index = (a - 1 if b > 0 else a) + file_delta
        del ids[index:index + b]
        del kinds[index:index + b]
        if index > 0:
            cur_rid = -1 if kinds[index - 1] == KIND_LEND else ids[index - 1]
        else:
            cur_rid = -1
        ins_ids = array("i")
        ins_kinds = bytearray()
        for body in buf:
            body = body.rstrip("\r")
            k = KIND_NORMAL
            rid = cur_rid
            if L_RE.match(body):
                k = KIND_HEADER
                rid = _alloc_head(heads, intern, L_RE.match(body).group(1), _k1_of(body))
                cur_rid = rid
            elif body.startswith("<LEND>"):
                k = KIND_LEND
                rid = cur_rid
                cur_rid = -1
            ins_ids.append(rid)
            ins_kinds.append(k)
        ids[index:index] = ins_ids
        kinds[index:index] = ins_kinds
        file_delta += len(ins_ids) - b
        # Record-boundary repair of the unchanged tail: a structural insert or
        # delete can change which record the following lines belong to.
        tail = index + len(ins_ids)
        if len(ins_ids) == 0:
            tail = index
        if tail > 0:
            if kinds[tail - 1] == KIND_LEND:
                run = -1
            else:
                run = ids[tail - 1]
        else:
            run = -1
        j = tail
        n = len(ids)
        while j < n and kinds[j] != KIND_HEADER:
            if kinds[j] == KIND_LEND:
                run = -1
            else:
                ids[j] = run
            j += 1
        # Emit rows for this commit's added lines.
        for off, body in enumerate(buf):
            body = body.rstrip("\r")
            k = ins_kinds[off]
            rid = ins_ids[off]
            if k == KIND_HEADER:
                stats["added_content_lines"] += 1
                l_id, hw = heads[rid]
                key = (cur_dict, l_id)
                if key not in seen:
                    seen.add(key)
                    rows.append((cur[1], cur_dict, l_id, hw, "add", cur[2], cur[0], cur[3]))
                    stats["entries_add"] += 1
            elif k == KIND_LEND:
                continue
            elif body.strip():
                stats["added_content_lines"] += 1
                if rid >= 0:
                    l_id, hw = heads[rid]
                    key = (cur_dict, l_id)
                    if key not in seen:
                        seen.add(key)
                        rows.append((cur[1], cur_dict, l_id, hw, "mod", cur[2], cur[0], cur[3]))
                        stats["entries_mod"] += 1
                    if not hw:
                        km = K1_RE.search(body)
                        if km:
                            _patch_head(heads, intern, rid, km.group(1))
                else:
                    stats["residual_lines"] += 1
                    cls = "markup-outside-record" if body.lstrip().startswith("<") else "text-outside-record"
                    residual_class[cls] += 1
                    stats[f"residual:{cur_dict}/{Path(cur_path).name}"] += 1
        st.blob = cur_new or cur_old or ""
        buf = []
        hunk = None
        in_hunk = False

    for line in run_git_log(clone, rev):
        if line.startswith(SEP):
            flush_hunk()
            parts = line.split(SEP)
            sha = parts[1]
            date = parts[2] if len(parts) > 2 else ""
            subject = parts[3] if len(parts) > 3 else ""
            issue_m = ISSUE_RE.search(subject)
            cur = (sha, dc_year_of(subject, date[:4]), issue_m.group(1) if issue_m else "", date)
            seen = set()
            cur_path = None
            cur_dict = None
            cur_old = cur_new = None
            file_delta = 0
            file_verified = False
            stats["commits"] += 1
            continue
        if line.startswith("diff --git "):
            flush_hunk()
            m = FILE_RE.match(line)
            if m:
                cur_path = m.group(1)
                cur_dict = m.group(2)
                dict_of[cur_path] = cur_dict
            else:
                cur_path = None
                cur_dict = None
            cur_old = cur_new = None
            file_delta = 0
            file_verified = False
            continue
        if line.startswith("rename to "):
            m = RENAME_RE.match(line)
            if m and cur_dict:
                cur_path = m.group(1)
                dict_of[cur_path] = cur_dict
            continue
        m = INDEX_RE.match(line)
        if m:
            cur_old, cur_new = m.group(1), m.group(2)
            continue
        if line.startswith("@@"):
            flush_hunk()
            m = HUNK_RE.match(line)
            if m and cur_path is not None:
                a = int(m.group(1))
                b = int(m.group(2)) if m.group(2) is not None else 1
                c = int(m.group(3))
                d = int(m.group(4)) if m.group(4) is not None else 1
                hunk = (a, b, c, d)
                in_hunk = True
            continue
        if not in_hunk or hunk is None or cur is None or cur_path is None:
            continue
        if line.startswith("+"):
            buf.append(line[1:])
        # '-' lines need no buffering: the hunk header carries the old span.
    flush_hunk()
    stats["residual_classes"] = len(residual_class)
    top_files = sorted(
        ((k[len("residual:"):], v) for k, v in stats.items() if k.startswith("residual:")),
        key=lambda kv: -kv[1],
    )
    return rows, heads, stats, residual_class, top_files


def _k1_of(body: str) -> str:
    m = K1_RE.search(body)
    return m.group(1) if m else ""


def rollup(rows):
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


def invariants(rows):
    """The four H7223 canaries, independent of this parser's internals."""
    distinct = {(d, l) for _y, d, l, *_ in rows}
    add2019 = sum(1 for y, _d, _l, _hw, k, *_ in rows if y == "2019" and k == "add")
    commits = collections.defaultdict(set)
    for y, _d, _l, _hw, _k, _iss, sha, _dt in rows:
        commits[y].add(sha)
    year_commits = {y: len(s) for y, s in commits.items()}
    lines = []
    ok = True
    d_ok = len(distinct) == EXPECTED_DISTINCT
    lines.append(f"[1] distinct (dict,L) = {len(distinct)} (H7223: {EXPECTED_DISTINCT}) "
                 f"{'PASS' if d_ok else 'DELTA %+d' % (len(distinct) - EXPECTED_DISTINCT)}")
    a_ok = abs(add2019 - EXPECTED_2019_ADD) <= max(1, EXPECTED_2019_ADD // 1000)
    lines.append(f"[2] 2019 additions = {add2019} (H7223: {EXPECTED_2019_ADD}) "
                 f"{'PASS' if a_ok else 'FAIL'}")
    c_ok = year_commits == EXPECTED_YEAR_COMMITS
    lines.append(f"[3] per-year commits = " + "/".join(str(year_commits.get(y, 0)) for y in sorted(EXPECTED_YEAR_COMMITS))
                 + " (H7223: " + "/".join(str(v) for _y, v in sorted(EXPECTED_YEAR_COMMITS.items())) + ") "
                 + ("PASS" if c_ok else "DELTA " + str({y: year_commits.get(y, 0) - v for y, v in EXPECTED_YEAR_COMMITS.items() if year_commits.get(y, 0) != v})))
    spot = Path(__file__).resolve().parents[1] / "reports" / "H7228_record_boundary_spotcheck.tsv"
    s_ok = spot.exists()
    lines.append(f"[4] 10-row hand spot-check file {spot.name}: {'present' if s_ok else 'MISSING'} "
                 f"{'PASS' if s_ok else 'FAIL'}")
    ok = d_ok and a_ok and c_ok and s_ok
    return "\n".join(lines), ok


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--clone", type=Path, default=DEFAULT_CLONE, help="path to local csl-orig clone (read-only)")
    ap.add_argument("--rev", default="HEAD", help="csl-orig revision to census (default: HEAD; the H7223/H7228 pin is 55e8addb)")
    ap.add_argument("--out", type=Path, default=None, help="TSV(.gz) output path (default: reports/cologne_entry_census.tsv.gz beside the repo root)")
    ap.add_argument("--check", action="store_true", help="re-run and verify byte-identical output plus the four invariants")
    ap.add_argument("--selftest", action="store_true", help="parse synthetic diffs and pin the record-boundary rules")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        print("selftest PASS")
        return

    rows, heads, stats, residual_class, top_files = census(args.clone, args.rev)
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[7], r[6]))
    out = args.out
    if out is None:
        out = Path(__file__).resolve().parents[1] / "reports" / "cologne_entry_census.tsv.gz"
    content = "dc_year\tdict\tL\theadword\tkind\tissue\tcommit\tcommit_date\n" + "".join(
        "\t".join(r) + "\n" for r in rows
    )
    print(rollup(rows))
    print(matrix(rows, sorted({r[0] for r in rows})))
    unattr = stats.get("residual_lines", 0)
    total_lines = stats.get("added_content_lines", 0)
    pct = 100.0 * unattr / max(total_lines, 1)
    print(f"== attribution residual: {unattr} added content lines outside any record "
          f"({pct:.3f}% of {total_lines} added content lines) — counted, not dropped ==")
    print(f"== residual classes: {dict(residual_class)} ==")
    if top_files:
        print("== residual concentration (top 10 files): "
              + ", ".join(f"{f}={n}" for f, n in top_files[:10]) + " ==")
    print(f"== state resyncs (blob SHA mismatch): {stats.get('blob_resync', 0)} ==")
    inv, ok = invariants(rows)
    print("== H7223 invariants ==")
    print(inv)
    if args.check:
        old = read_out(out)
        if old != content:
            sys.exit(f"CHECK FAIL: {out} differs from a fresh re-run "
                     f"({len(old.splitlines())} vs {len(content.splitlines())} lines)")
        print(f"check PASS: {out} byte-identical on re-run ({len(rows)} rows)")
        if not ok or pct > RESIDUAL_TARGET_PCT:
            sys.exit("INVARIANT FAIL")
        return
    write_out(out, content)
    print(f"wrote {out} ({len(rows)} rows)")


def selftest():
    """Synthetic history: long record (>6 lines), mid-record insert, preamble add.

    The second commit's hunk has NO <L> within the old -U6 context because the
    record is long — the exact failure mode of the v1 parser; record-boundary
    attribution must still land it on L99.
    """
    long_body = [f" <s>word</s> ¦ gloss line {i}" for i in range(12)]
    fixture = [
        f"{SEP}SHAROOT{SEP}2019-01-01{SEP}initial import",
        "diff --git a/v02/mw/mw.txt b/v02/mw/mw.txt",
        "new file mode 100644",
        "index 0000000..aaa111",
        "--- /dev/null",
        "+++ b/v02/mw/mw.txt",
        "@@ -0,0 +1,18 @@",
        "+<L>99<pc>1,1<k1>oldword<k2>a<e>1",
        *["+" + x for x in long_body],
        "+<LEND>",
        "+<L>100<pc>1,1<k1>newword<k2>b<e>1",
        "+<s>newword</s> ¦ brand new entry",
        "+<LEND>",
        "+<H>{#z#}",
        f"{SEP}SHA2{SEP}2026-03-01{SEP}DC 28 February 2026. See https://github.com/sanskrit-lexicon/csl-corrections/issues/300",
        "diff --git a/v02/mw/mw.txt b/v02/mw/mw.txt",
        "index aaa111..bbb222 100644",
        "--- a/v02/mw/mw.txt",
        "+++ b/v02/mw/mw.txt",
        "@@ -10,1 +10,2 @@",
        " <s>word</s> ¦ gloss line 7",
        "+<s>word</s> ¦ corrected deep gloss",
        f"{SEP}SHA3{SEP}2026-03-02{SEP}DC 1 March 2026. See https://github.com/sanskrit-lexicon/csl-corrections/issues/301",
        "diff --git a/v02/mw/mw.txt b/v02/mw/mw.txt",
        "index bbb222..ccc333 100644",
        "--- a/v02/mw/mw.txt",
        "+++ b/v02/mw/mw.txt",
        "@@ -2,0 +3,1 @@",
        "+<s>word</s> ¦ spear",
        f"{SEP}SHA4{SEP}2026-03-03{SEP}DC 2 March 2026",
        "diff --git a/v02/mw/mw.txt b/v02/mw/mw.txt",
        "index ccc333..ddd444 100644",
        "--- a/v02/mw/mw.txt",
        "+++ b/v02/mw/mw.txt",
        "@@ -0,0 +1,1 @@",
        "+<H>{#new section#}",
        # two hunks in ONE file diff: hunk 2's `a` is a PRE-IMAGE position, so
        # it must be re-based by hunk 1's +2 delta, and its boundary owner
        # must be the record hunk 1 CREATED (tail repair), not the one the
        # pre-image would suggest.
        f"{SEP}SHA5{SEP}2026-03-04{SEP}DC 3 March 2026",
        "diff --git a/v02/mw/mw.txt b/v02/mw/mw.txt",
        "index ddd444..eee555 100644",
        "--- a/v02/mw/mw.txt",
        "+++ b/v02/mw/mw.txt",
        "@@ -5,0 +6,2 @@",
        "+<LEND>",
        "+<L>98<pc>1,1<k1>tailword<k2>t<e>1",
        "@@ -10,1 +12,1 @@",
        "- <s>word</s> ¦ gloss line 7",
        "+ <s>word</s> ¦ gloss line 7 corrected",
        # single hunk on the TRUE post-image of SHA5: lands inside the
        # record SHA5 split off (L98), proving the state survived the
        # two-hunk diff byte-exactly (not pre-image + last hunk).
        f"{SEP}SHA6{SEP}2026-03-05{SEP}DC 4 March 2026",
        "diff --git a/v02/mw/mw.txt b/v02/mw/mw.txt",
        "index eee555..fff666 100644",
        "--- a/v02/mw/mw.txt",
        "+++ b/v02/mw/mw.txt",
        "@@ -8,1 +8,1 @@",
        "- <s>word</s> ¦ gloss line 3",
        "+ <s>word</s> ¦ gloss line 3 corrected",
    ]

    orig = run_git_log

    def fake(_clone, _rev):
        return iter(fixture)

    globals()["run_git_log"] = fake
    try:
        rows, heads, stats, residual, _top = census(Path("."), "HEAD")
    finally:
        globals()["run_git_log"] = orig
    by_key = {(r[6], r[2]): r for r in rows}
    assert by_key[("SHAROOT", "99")][4] == "add"
    assert by_key[("SHAROOT", "100")][4] == "add"
    # deep-in-record correction: v1's -U6 context cannot see <L>99; v2 must.
    assert by_key[("SHA2", "99")][4] == "mod", by_key.get(("SHA2", "99"))
    assert by_key[("SHA3", "99")][4] == "mod"
    # added <H> preamble/section line has no record -> residual, not a row
    assert stats["residual_lines"] == 2, stats["residual_lines"]  # root <H> + late preamble <H>
    assert stats["entries_add"] == 3 and stats["entries_mod"] == 3, stats
    assert by_key[("SHA2", "99")][5] == "300" and by_key[("SHA3", "99")][5] == "301"
    # dedupe: SHA3's <s> line is the second added line of L99 in that commit
    assert sum(1 for r in rows if r[6] == "SHA3") == 1
    # SHA5: the split record's header is an add; hunk 2's mod of the SAME
    # record in the SAME commit is deduped; no mis-attributed L99 row may
    # appear (pre-image offset or per-hunk rebuild would produce one).
    assert by_key[("SHA5", "98")][4] == "add", by_key.get(("SHA5", "98"))
    assert by_key[("SHA5", "98")][3] == "tailword", by_key[("SHA5", "98")]
    assert ("SHA5", "99") not in by_key and ("SHA5", "100") not in by_key
    # SHA6 lands on the TRUE post-image of the two-hunk diff, inside the
    # record SHA5 created: mod(L98), not mod(L99).
    assert by_key[("SHA6", "98")][4] == "mod", by_key.get(("SHA6", "98"))
    assert ("SHA6", "99") not in by_key
    # one verification per file diff: no blob resync anywhere in this history
    assert stats["blob_resync"] == 0, stats["blob_resync"]


if __name__ == "__main__":
    main()
