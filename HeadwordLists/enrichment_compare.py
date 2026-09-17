#!/usr/bin/env python3
"""enrichment_compare.py — generic share-in-annexure vs share-in-main enrichment
for any (source-set, target-dictionary) pair, plus the general SxD coverage
matrix. Stdlib only, deterministic, csl-orig read-only.

Replaces the bespoke per-pair arithmetic that produced the published figures
in MW_NACHTRAG_UPTAKE_AND_PROVENANCE_DETAILS_15-09-2026.md (PW 7.79-7.91x,
BHS 2.09x) with one tool; the registry of measured pairs lives in
ENRICHMENT_METRICS_REGISTRY.md (same directory).

LOCKED COUNTING CONVENTIONS (registry §0; published 15-09-2026; the
conventions themselves were verified for the PUBLISHED figures by the
DeepSeek verifier round 2 of 14-09-2026 — see
MW_PWK_NACHTRAEGE_TRIAL_INDEPENDENT_RECHECK_14-09-2026.md; verification of
THIS tool's own run lives in ENRICHMENT_METRICS_REGISTRY.md §4.
Deviating from these forks the numbers):

  C1  headword sets are <k1>-only, verbatim field value, no normalization.
  C2  target annexure = set of k1 whose entry body contains the annexure tag
      (default '<info n="sup"/>', the MW99 Supplemental-Word annexure).
  C3  target main = k1_all MINUS annexure — a proper partition on duplicate
      k1s (a k1 that appears both tagged and untagged counts in the annexure
      only; the naive tag-absence set overlaps the annexure on duplicate k1s,
      DeepSeek verifier finding 14-09-2026).
  C4  enrichment(S, D) = (|S ∩ annexure| / |annexure|) / (|S ∩ main| / |main|);
      undefined (inf) when |S ∩ main| = 0, None when the target has no
      annexure split.
  C5  sup-layer source headword = k2 with ALL leading '*' stripped (lstrip,
      the prior-art convention) when k2 starts with '*', else k1 (the pw.txt
      Nachträge convention; deduped).

Usage:
  python enrichment_compare.py --target mw \
      --source pw:sup_7 --source pw:sup --source pwkvn --source bhs \
      [--orig DIR] [--annexure-tag TAG] [--source-file LABEL=PATH ...]
      [--matrix-dict CODE ...] [--tsv OUT] [--matrix-tsv OUT] [--json OUT]

  source spec: CODE        unique k1 set of dict CODE (e.g. bhs, pwkvn)
               CODE:sup_N  headwords of CODE's <info n="sup_N"/> entries
               CODE:sup    union of all sup_N layers of CODE
  --source-file adds an arbitrary one-headword-per-line set (SLP1, k1 domain).
  --matrix-dict adds dicts to the SxD coverage matrix (default: target + all
  source dicts); matrix cells are |S ∩ D_k1| and the share of S.

Exit 0 with every source measured; source-level failures are flagged in the
output (row status=ERROR:reason) and count against a 3-try stop-budget, never
a stall. --selftest runs synthetic-fixture checks (C2-C5) and exits.

Env: CSL_ORIG (default ../csl-orig sibling of this repo checkout, else
/Users/mac/Documents/GitHub/csl-orig/v02). Reads only; writes only the
--tsv/--matrix-tsv/--json paths given.
"""
import argparse
import io
import json
import os
import re
import sys

L_RE = re.compile(r"^<L>")
K1_RE = re.compile(r"<k1>([^<]+)")
K2_RE = re.compile(r"<k2>([^<]+)")
SUP_N_RE = re.compile(r'<info n="sup_(\d)"/>')
DEFAULT_ANNEX_TAG = '<info n="sup"/>'

for _stream in (sys.stdout, sys.stderr):
    _rc = getattr(_stream, "reconfigure", None)
    if _rc is not None:
        _rc(encoding="utf-8")


def dict_path(orig, code):
    return os.path.join(orig, code, code + ".txt")


def iter_entries(path):
    """Yield (k1, k2, body) for each <L>-anchored entry (verbatim fields)."""
    cur_k1 = None
    cur_k2 = None
    buf = []

    def flush():
        if cur_k1 is None:
            return
        yield cur_k1, cur_k2, "".join(buf)

    with io.open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if L_RE.match(line):
                for t in flush():
                    yield t
                g1 = K1_RE.search(line)
                cur_k1 = g1.group(1).strip() if g1 else ""
                m2 = K2_RE.search(line)
                cur_k2 = m2.group(1).strip() if m2 else ""
                buf = [line]
            elif cur_k1 is not None:
                buf.append(line)
    for t in flush():
        yield t


def sup_headword(k1, k2):
    """C5: pw Nachträge headword convention."""
    if k2 and k2.startswith("*"):
        return k2.lstrip("*")
    return k1


def load_target(orig, code, annex_tag):
    """k1_all, annexure per C1-C3. Returns (k1_all, annexure)."""
    k1_all = set()
    annexure = set()
    for k1, _k2, body in iter_entries(dict_path(orig, code)):
        if not k1:
            continue
        k1_all.add(k1)
        if annex_tag in body:
            annexure.add(k1)
    return k1_all, annexure


def load_source(orig, spec):
    """Source set per C1/C5. spec: CODE | CODE:sup_N | CODE:sup."""
    if ":" in spec:
        code, layer = spec.split(":", 1)
        prefix = '<info n="' + layer + '"/>'
        exact = SUP_N_RE  # for :sup union we re-derive N per entry
        if layer != "sup" and not re.fullmatch(r"sup_\d", layer):
            raise ValueError("layer spec must be sup_N or sup: " + spec)
        hw = set()
        for k1, k2, body in iter_entries(dict_path(orig, code)):
            if layer == "sup":
                if not exact.search(body):
                    continue
            elif prefix not in body:
                continue
            h = sup_headword(k1, k2)
            if h:
                hw.add(h)
        return code, hw
    hw = {k1 for k1, _k2, _body in iter_entries(dict_path(orig, spec)) if k1}
    return spec, hw


def load_source_file(path):
    hw = set()
    with io.open(path, encoding="utf-8-sig") as f:
        for line in f:
            h = line.strip()
            if h:
                hw.add(h)
    return hw


def enrich(s_set, annexure, k1_all):
    """C4. Returns (in_annex, annex_share, in_main, main_share, enrichment).

    Shares are always floats (0.0 when the denominator set is empty);
    enrichment is None only when the target has no annexure split.
    """
    main = k1_all - annexure  # C3 proper partition
    in_annex = len(s_set & annexure)
    in_main = len(s_set & main)
    annex_share = in_annex / len(annexure) if annexure else 0.0
    main_share = in_main / len(main) if main else 0.0
    if not annexure:
        enr = None
    elif in_annex and in_main:
        enr = annex_share / main_share
    elif in_annex:
        enr = float("inf")
    else:
        enr = 0.0
    return in_annex, annex_share, in_main, main_share, enr


def fmt_enr(e):
    if e is None:
        return "n/a"
    if e == float("inf"):
        return "inf"
    return "%.2fx" % e


def selftest():
    """Synthetic fixtures for C2-C5 math + proper partition."""
    # fixture: entries via a temp file tree
    import tempfile
    d = tempfile.mkdtemp(prefix="enr_selftest_")
    os.makedirs(os.path.join(d, "td"))
    ent = [
        "<L>1<k1>a<k2>x<info n=\"sup\"/>body1",      # a in annexure
        "<L>2<k1>b<body2",                            # b main
        "<L>3<k1>c<body3",                            # c main
        "<L>4<k1>d<info n=\"sup\"/>body4",            # d annexure
        "<L>5<k1>d<k2>y<info n=\"sup\"/>body5",       # duplicate d k1 -> annex
        "<L>6<k1>d<body6",                            # d duplicate untagged:
    ]                                                 #   still annex (C3)
    with io.open(os.path.join(d, "td", "td.txt"), "w", encoding="utf-8") as f:
        for e in ent:
            f.write(e + "\n")
            f.write("more body\n")
    k1_all, annex = load_target(d, "td", DEFAULT_ANNEX_TAG)
    assert k1_all == {"a", "b", "c", "d"}, k1_all
    assert annex == {"a", "d"}, annex  # duplicate-d stays annexure (C3)
    in_a, ashr, in_m, mshr, e = enrich({"a", "b"}, annex, k1_all)
    assert (in_a, in_m) == (1, 1)
    assert abs(ashr - 0.5) < 1e-9 and abs(mshr - 0.5) < 1e-9
    assert e is not None and abs(e - 1.0) < 1e-9, e
    in_a, ashr, in_m, mshr, e = enrich({"a"}, annex, k1_all)
    assert in_m == 0 and e == float("inf")
    _, _, _, _, e = enrich({"b"}, annex, k1_all)
    assert e == 0.0, e
    # C5 sup headword convention
    assert sup_headword("k1v", "*star") == "star"
    assert sup_headword("k1v", "plain") == "k1v"
    assert sup_headword("k1v", "") == "k1v"
    print("selftest PASS (C2-C5 fixtures, proper partition, sup convention)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    here_default = os.environ.get(
        "CSL_ORIG",
        os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "..", "csl-orig", "v02"))
    ap.add_argument("--orig", default=here_default)
    ap.add_argument("--target", help="target dict code (annexure holder)")
    ap.add_argument("--annexure-tag", default=DEFAULT_ANNEX_TAG)
    ap.add_argument("--source", action="append", default=[],
                    help="CODE | CODE:sup_N | CODE:sup (repeatable)")
    ap.add_argument("--source-file", action="append", default=[], metavar="LABEL=PATH")
    ap.add_argument("--matrix-dict", action="append", default=[],
                    help="extra dicts for the SxD coverage matrix (repeatable)")
    ap.add_argument("--tsv")
    ap.add_argument("--matrix-tsv")
    ap.add_argument("--json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.target:
        ap.error("--target is required (dict code holding the annexure)")

    orig = os.path.abspath(args.orig)
    if not os.path.isdir(orig):
        print("ERROR: --orig dir not found: %s" % orig, file=sys.stderr)
        return 2

    k1_all, annexure = load_target(orig, args.target, args.annexure_tag)
    main = k1_all - annexure  # C3
    print("target %s: k1_all=%d annexure=%d main=%d (tag %r)"
          % (args.target, len(k1_all), len(annexure), len(main),
             args.annexure_tag))

    # ---- source sets (skip+flag per stop-budget; never stall) ------------
    sources = []  # (label, set|None, error)
    for spec in args.source:
        label = spec
        got = None
        err = None
        for attempt in range(3):  # stop-budget: 3 tries per probe
            try:
                _, got = load_source(orig, spec)
                err = None
                break
            except Exception as ex:  # noqa: BLE001 — flagged, never fatal
                err = "%s (try %d)" % (ex, attempt + 1)
        sources.append((label, got, err))
    for spec in args.source_file:
        label, _, path = spec.partition("=")
        got = None
        err = None
        for attempt in range(3):
            try:
                got = load_source_file(path)
                err = None
                break
            except Exception as ex:  # noqa: BLE001
                err = "%s (try %d)" % (ex, attempt + 1)
        sources.append((label, got, err))

    # ---- matrix dicts ----------------------------------------------------
    auto = {args.target}
    for spec in args.source:
        auto.add(spec.split(":", 1)[0])
    matrix_dicts = []
    for c in list(dict.fromkeys(args.matrix_dict)) + sorted(auto):
        if c not in matrix_dicts:
            matrix_dicts.append(c)
    d_k1 = {}
    for c in matrix_dicts:
        try:
            d_k1[c] = {k1 for k1, _k2, _b in iter_entries(dict_path(orig, c)) if k1}
        except Exception as ex:  # noqa: BLE001 — flagged, never fatal
            print("WARN matrix dict %s failed: %s" % (c, ex), file=sys.stderr)

    # ---- enrichment table ------------------------------------------------
    rows = []
    print("\nsource_set\tn\tin_annex\tannex_share%\tin_main\tmain_share%\tenrichment")
    for label, s, err in sources:
        if s is None:
            row = {"source_set": label, "n": None, "status": "ERROR:" + (err or "?")}
            print("%s\tERROR %s" % (label, err))
            rows.append(row)
            continue
        in_a, ashr, in_m, mshr, e = enrich(s, annexure, k1_all)
        row = {
            "source_set": label, "n": len(s),
            "in_annexure": in_a,
            "annexure_share_pct": round(100 * ashr, 1),
            "in_main": in_m,
            "main_share_pct": round(100 * mshr, 1),
            "enrichment": None if e is None else e,
            "enrichment_fmt": fmt_enr(e), "status": "OK",
        }
        rows.append(row)
        print("%s\t%d\t%d\t%.1f\t%d\t%.1f\t%s" % (
            label, len(s), in_a, 100 * ashr, in_m, 100 * mshr,
            fmt_enr(e)))

    # ---- SxD coverage matrix --------------------------------------------
    print("\nSxD coverage matrix (share of S present in D k1):")
    hdr = ["source_set"] + ["n_in_" + c for c in matrix_dicts] \
        + ["share_" + c + "_pct" for c in matrix_dicts]
    print("\t".join(hdr))
    matrix_rows = []
    for label, s, err in sources:
        if s is None:
            continue
        counts = [len(s & d_k1.get(c, set())) for c in matrix_dicts]
        shares = [round(100 * n / len(s), 1) if s else 0.0 for n in counts]
        matrix_rows.append(dict(zip(hdr, [label] + counts + shares)))
        print("\t".join(map(str, [label] + counts + shares)))

    # ---- outputs ----------------------------------------------------------
    if args.tsv:
        with io.open(args.tsv, "w", encoding="utf-8", newline="") as f:
            cols = ["source_set", "n", "in_annexure", "annexure_share_pct",
                    "in_main", "main_share_pct", "enrichment", "status"]
            f.write("\t".join(cols) + "\n")
            for r in rows:
                f.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
        print("\nWROTE " + args.tsv)
    if args.matrix_tsv:
        with io.open(args.matrix_tsv, "w", encoding="utf-8", newline="") as f:
            f.write("\t".join(hdr) + "\n")
            for r in matrix_rows:
                f.write("\t".join(str(r[c]) for c in hdr) + "\n")
        print("WROTE " + args.matrix_tsv)
    if args.json:
        payload = {
            "tool": "enrichment_compare.py",
            "conventions": ["C1 k1-only", "C2 annexure = tag-bearing k1",
                             "C3 main = k1_all - annexure (proper partition)",
                             "C4 enrichment = annex_share/main_share",
                             "C5 sup hw = k2.lstrip('*') or k1"],
            "orig": orig, "target": args.target,
            "annexure_tag": args.annexure_tag,
            "target_counts": {"k1_all": len(k1_all), "annexure": len(annexure),
                              "main": len(main)},
            "matrix_dicts": matrix_dicts,
            "enrichment_rows": rows,
            "matrix_rows": matrix_rows,
        }
        with io.open(args.json, "w", encoding="utf-8", newline="") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
        print("WROTE " + args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
