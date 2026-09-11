#!/usr/bin/env python3
"""Independent verifier for H4536 (pwg_scan_devanagari_join.tsv).

Written from scratch by the DeepSeek verifier session; imports nothing from the
executor's builder. Re-derives the join from the raw xlsx + pwg.txt per the
documented policy and diffs against the committed TSV.

Usage:
    python3 verify_h4536.py --csv RAW.csv --xlsx RAW.xlsx --pwg-txt pwg.txt \
        --tsv committed.tsv
"""
import argparse
import re
import sys
from collections import Counter

XLSX_SHEET = "Boethlingk_PWGScan_Devanagary"
LREF_RE = re.compile(r"\[L=(\d+)\]")
PWG_RE = re.compile(
    r"^<L>(?P<L>[^<]+)<pc>(?P<pc>[^<]*)"
    r"(?:<k1>(?P<k1>[^<]*))?(?:<k2>(?P<k2>[^<]*))?(?:<h>(?P<h>\d+))?"
)
TSV_HEADER = ["L", "key1", "devanagari", "translit", "sense", "pc", "anchor"]

# IAST(-ish) -> SLP1. Verifier's own table, same mapping as documented.
MAP2 = {"kh": "K", "gh": "G", "ch": "C", "jh": "J", "ṭh": "W", "ḍh": "Q",
        "th": "T", "dh": "D", "ph": "P", "bh": "B", "ai": "E", "au": "O"}
MAP1 = {"ā": "A", "ī": "I", "ū": "U", "ṛ": "f", "ṝ": "F", "ḷ": "x", "ḹ": "X",
        "ñ": "Y", "ṅ": "N", "ṇ": "R", "ṭ": "w", "ḍ": "q", "ś": "S", "ṣ": "z",
        "ṃ": "M", "ḥ": "H"}


def to_slp1(text):
    if not text:
        return ""
    s = str(text).strip().lower()
    out, i = [], 0
    while i < len(s):
        if s[i:i + 2] in MAP2:
            out.append(MAP2[s[i:i + 2]])
            i += 2
        else:
            out.append(MAP1.get(s[i], s[i]))
            i += 1
    return "".join(out)


def kl(k):
    return (k or "").rstrip("/").lower()


def parse_pwg(path):
    by_l, by_pc = {}, {}
    n_hdr = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = PWG_RE.match(line)
            if not m:
                continue
            n_hdr += 1
            rec = (m.group("L"), m.group("pc"), m.group("k1") or "",
                   m.group("k2") or "", m.group("h") or "")
            by_l[rec[0]] = rec
            by_pc.setdefault(rec[1], []).append(rec)
    return by_l, by_pc, n_hdr


def read_xlsx(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[XLSX_SHEET]
    rows = []
    for row in ws.iter_rows(values_only=True):
        dev = row[0]
        if dev is None or (isinstance(dev, str) and dev == "URL"):
            continue
        translit = row[1] if len(row) > 1 else None
        sense = row[2] if len(row) > 2 else None
        numerik = row[3] if len(row) > 3 else None
        paper = row[4] if len(row) > 4 else None
        m = LREF_RE.search(str(paper)) if paper is not None else None
        rows.append((str(dev).strip(),
                     None if translit is None else str(translit).strip(),
                     None if sense is None else str(sense).strip(),
                     None if numerik is None else str(numerik).strip(),
                     int(m.group(1)) if m else None))
    wb.close()
    return rows


def match(rec, nt):
    return kl(rec[2]) == nt or kl(rec[3]) == nt


def derive(x_rows, by_l, by_pc):
    joined, unjoined = [], []
    for dev, translit, sense, numerik, lref in x_rows:
        nt = to_slp1(translit).lower()
        rec, anchor = None, ""
        pages = [p.strip() for p in numerik.split(",")] if numerik else []
        if nt and pages:
            cands, seen = [], set()
            for pg in pages:
                for r in by_pc.get(pg, ()):
                    if match(r, nt) and r[0] not in seen:
                        seen.add(r[0])
                        cands.append(r)
            if len(cands) > 1 and sense:
                homed = [r for r in cands if r[4] == sense]
                cands = homed or cands
            if cands:
                rec, anchor = cands[0], "pc"
        if rec is None and nt and lref is not None:
            cand = by_l.get(str(lref))
            if cand is not None and match(cand, nt):
                rec, anchor = cand, "L"
        if rec is None:
            unjoined.append((dev, translit, sense, numerik, lref))
            continue
        joined.append((int(rec[0]) if rec[0].isdigit() else rec[0], rec[2],
                       dev, translit, sense or "", rec[1], anchor))
    return joined, unjoined


def sense_key(s):
    try:
        return (0, int(s))
    except (TypeError, ValueError):
        return (1, 0)


def row_sort_key(r):
    lk = (0, r[0], 0) if isinstance(r[0], int) else (1, 0, r[0])
    return (lk, sense_key(r[4]))


def line_of(r):
    return "\t".join("" if c is None else str(c) for c in r)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--pwg-txt", required=True)
    ap.add_argument("--tsv", required=True)
    args = ap.parse_args(argv)

    by_l, by_pc, n_hdr = parse_pwg(args.pwg_txt)
    x_rows = read_xlsx(args.xlsx)
    joined, unjoined = derive(x_rows, by_l, by_pc)

    print("=== CHECK 1: xlsx recount / join counts ===")
    print(f"xlsx_data_rows           = {len(x_rows)}   (claimed 109375)")
    print(f"derived_joined_rows      = {len(joined)}   (claimed 109279)")
    print(f"derived_unjoined_rows    = {len(unjoined)}   (claimed 96)")
    pct = round(100.0 * len(joined) / len(x_rows), 2) if x_rows else 0.0
    print(f"joined_pct               = {pct}%  (claimed 99.91%)")
    print("unjoined examples (truncated):")
    for u in unjoined[:5]:
        print("   ", tuple((x[:60] + "…" if isinstance(x, str) and len(x) > 60 else x) for x in u))

    print("\n=== CHECK 3: pwg.txt + coverage ===")
    all_k1 = {r[2] for r in by_l.values()}
    print(f"pwg_header_lines         = {n_hdr}")
    print(f"pwg_distinct_L (by_l)    = {len(by_l)}   (claimed 123366)")
    print(f"pwg_distinct_k1          = {len(all_k1)}   (claimed 106082)")
    jL = {r[0] for r in joined}
    jK = {r[1] for r in joined}
    print(f"tsv_distinct_L           = {len(jL)}   (claimed 107742)")
    print(f"tsv_distinct_key1        = {len(jK)}   (claimed 92619)")
    print(f"coverage_key1            = {round(100.0*len(jK)/len(all_k1),2)}%  (claimed 87.31%)")
    print(f"coverage_L               = {round(100.0*len(jL)/len(by_l),2)}%  (claimed 87.34%)")

    print("\n=== CHECK 2: row-for-row diff vs committed TSV ===")
    committed = []
    with open(args.tsv, encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            committed.append(tuple(line.rstrip("\n").split("\t")))
    print(f"tsv_header               = {head}")
    print(f"committed_data_rows      = {len(committed)}")
    # compare as ordered lists
    my_lines = [line_of(r) for r in sorted(joined, key=row_sort_key)]
    my_tuples = [tuple(line_of(r).split("\t")) for r in sorted(joined, key=row_sort_key)]
    diff_ordered = sum(1 for a, b in zip(my_lines, [line_of(c) for c in committed]) if a != b)
    diff_ordered += abs(len(my_lines) - len(committed))
    print(f"ordered_line_diffs       = {diff_ordered}   (expected 0)")
    # multiset compare
    ca, cb = Counter(my_tuples), Counter(committed)
    only_mine = ca - cb
    only_comm = cb - ca
    print(f"multiset_only_derived    = {sum(only_mine.values())}")
    print(f"multiset_only_committed  = {sum(only_comm.values())}")
    for t, n in list(only_mine.items())[:5]:
        print("   only-derived:", n, t)
    for t, n in list(only_comm.items())[:5]:
        print("   only-committed:", n, t)

    print("\n=== CHECK 4: spot rows ===")
    for dev, sense in [("अंशक", "1"), ("अंशक", "2"), ("अंशक", "3")]:
        hits = [r for r in committed if r[2] == dev and r[4] == sense]
        print(f"{dev} sense {sense}: {hits}")
    hits = [r for r in committed if r[2] == "अंशभाज्"]
    print(f"अंशभाज्: {hits}")

    print("\n=== CHECK 5: integrity (full) ===")
    pwg_tuples = {(r[0], r[1], r[2]) for r in by_l.values()}
    # also include k2-based key1? TSV key1 comes from rec[2] (k1) only
    bad_l_pc_k1 = 0
    bad_anchor = 0
    for r in committed:
        L, key1, pc, anchor = r[0], r[1], r[5], r[6]
        if (L, pc, key1) not in pwg_tuples:
            bad_l_pc_k1 += 1
            if bad_l_pc_k1 <= 5:
                print("   BAD (L,pc,key1):", r)
        if anchor != "pc":
            bad_anchor += 1
    print(f"rows_failing_(L,pc,key1) = {bad_l_pc_k1}")
    print(f"rows_anchor_not_pc       = {bad_anchor}   (expected 0)")


if __name__ == "__main__":
    sys.exit(main())
