#!/usr/bin/env python3
"""Derive the root×devanagari join TSV from MG's 2013 PWG scan pair (H4536).

Inputs (RAW PAIR STAYS ON YADISK — derived-only, MG ruling 07-09-2026; fetch
read-only into scratch, never commit):

    rclone copy 'yadisk:Sanskrityatina/05_Sanskrit-Lexicon/1855-PWG/Boethlingk_PWGScan.csv' <scratch>/
    rclone copy 'yadisk:Sanskrityatina/05_Sanskrit-Lexicon/1855-PWG/Boethlingk_PWGScan_Devanagary.xlsx' <scratch>/

  Boethlingk_PWGScan.csv           ; CSV: URL;Word;Numerik;Paper;Lnumerik;About
                                   # 2013 header MISLABEL: the SLP1 headword
                                   # lives in the URL column, Word = sense no;
                                   # full SLP1+German pass, mixed encoding
  Boethlingk_PWGScan_Devanagary.xlsx  sheet 'Boethlingk_PWGScan_Devanagary'
                                   # col0 devanagari, col1 translit (IAST-ish),
                                   # col2 sense no, col3 numerik (= pwg.txt <pc>),
                                   # col4 '[L=N]' (Cologne <L> record id, noisy)

Join policy (precision-first — every joined row is page- AND word-confirmed):
  anchor='pc' : records whose pwg.txt <pc> == the row's Numerik AND whose
                k1/k2 == the row's translit (IAST -> SLP1 normalised); when the
                page holds several homs of the word, the row's sense number
                picks <h>.
  anchor='L'  : fallback — the row's [L=N] record's k1/k2 == translit. The
                [L=] refs are a noisy 2013 backfill (68.8% word-confirm vs
                93.8% for Numerik), used only when they self-confirm.
  everything else stays UNJOINED residue (counted, examples printed).

pwg.txt = csl-orig v02/pwg — the pwg_ru lane base layer (lemma/<key1> SLP1
spine). Header lines: <L>N<pc>V-PAGE<k1>..[<k2>..][<h>M]; k2 may carry a
trailing '/'; L ids may be dotted ('13188.1', unreachable from integer [L=N]).

Usage:
    python3 pwg_scan_devanagari_join.py --csv CSV --xlsx XLSX \
        --pwg-txt PWG_TXT --emit OUT.tsv          # (re)build the derived TSV
    ... --check OUT.tsv                           # parity gate, exit 1 on drift

stdout always carries the census stats (rows, keying, coverage vs pwg.txt).
Exit 0 ok; 2 usage; 1 --check mismatch.
"""
import argparse
import csv
import re
import sys
from collections import Counter

XLSX_SHEET = "Boethlingk_PWGScan_Devanagary"
LREF_RE = re.compile(r"\[L=(\d+)\]")
# k2 and h are OPTIONAL: only ~6.5k of 123k pwg.txt headers carry <h>.
PWHDR_RE = re.compile(
    r"^<L>(\d+(?:\.\d+)?)<pc>([^<]*)(?:<k1>([^<]*))?(?:<k2>([^<]*))?(?:<h>(\d+))?")
TSV_HEADER = ["L", "key1", "devanagari", "translit", "sense", "pc", "anchor"]

# IAST(-ish, as found in the xlsx translit column) -> SLP1, longest-first.
# SLP1: ś=S ṣ=z ṭ=w ḍ=q ṇ=R ñ=Y ṅ=N ā=A ī=I ū=U ṛ=f ṝ=F ḷ=x ṃ=M ḥ=H ai=E au=O,
# aspirates/digraphs: kh=K gh=G ch=C jh=J ṭh=W ḍh=Q th=T dh=D ph=P bh=B.
_IAST_MAP = {
    "kh": "K", "gh": "G", "ch": "C", "jh": "J", "ṭh": "W", "ḍh": "Q",
    "th": "T", "dh": "D", "ph": "P", "bh": "B",
    "ā": "A", "ī": "I", "ū": "U", "ṛ": "f", "ṝ": "F", "ḷ": "x", "ḹ": "X",
    "ñ": "Y", "ṅ": "N", "ṇ": "R", "ṭ": "w", "ḍ": "q", "ś": "S", "ṣ": "z",
    "ṃ": "M", "ḥ": "H", "ai": "E", "au": "O",
}


def iast_to_slp1(text):
    """'aṃśabhāj' -> 'aMSABAj' (case-insensitive compare happens downstream)."""
    if not text:
        return ""
    s = str(text).strip().lower()
    out, i = [], 0
    while i < len(s):
        pair = s[i:i + 2]
        if pair in _IAST_MAP:
            out.append(_IAST_MAP[pair])
            i += 2
        else:
            out.append(_IAST_MAP.get(s[i], s[i]))
            i += 1
    return "".join(out)


def _key_lower(k):
    return (k or "").rstrip("/").lower()


def parse_pwg_index(pwg_txt_path):
    """pwg.txt -> (by_L, by_pc); by_pc keeps header-file order for hom pick."""
    by_l, by_pc = {}, {}
    with open(pwg_txt_path, encoding="utf-8") as fh:
        for line in fh:
            m = PWHDR_RE.match(line)
            if not m:
                continue
            rec = (m.group(1), m.group(2), m.group(3) or "", m.group(4) or "",
                   m.group(5) or "")
            by_l[rec[0]] = rec
            by_pc.setdefault(rec[1], []).append(rec)
    return by_l, by_pc


def read_xlsx_rows(xlsx_path):
    """Yield (dev, translit, sense, numerik, Lref|int|None) per data row."""
    import openpyxl  # noqa: PLC0415  repo-standard dep (see build_dhatup_*.py)

    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb[XLSX_SHEET]
    for row in ws.iter_rows(values_only=True):
        dev = row[0]
        if dev is None or (isinstance(dev, str) and dev == "URL"):
            continue  # header row
        translit = row[1] if len(row) > 1 else None
        sense = row[2] if len(row) > 2 else None
        numerik = row[3] if len(row) > 3 else None
        paper = row[4] if len(row) > 4 else None
        m = LREF_RE.search(str(paper)) if paper is not None else None
        yield (str(dev).strip(), None if translit is None else str(translit).strip(),
               None if sense is None else str(sense).strip(),
               None if numerik is None else str(numerik).strip(),
               int(m.group(1)) if m else None)
    wb.close()


def read_csv_rows(csv_path):
    """Yield (word_slp1, sense, Lref|int|None) per data row.

    2013 HEADER MISLABEL (documented, not "fixed" in the raw file): the CSV
    header says URL;Word;... but the data carries the SLP1 headword in the
    URL column and the SENSE NUMBER in the Word column (mirroring the xlsx
    where col0/col1 are the devanagari/translit 'URL's and Word = sense).
    The body is mixed-encoding: decoding is byte-transparent latin-1 (never
    fails; non-ASCII garbles, but the join only consumes the ASCII columns).
    Parsed per-line with quote handling OFF — a stray German quote in some
    body would otherwise swallow the rest of the file into one field.
    """
    with open(csv_path, encoding="latin-1", newline="") as fh:
        for i, line in enumerate(fh):
            if i == 0:
                continue  # header
            parts = line.rstrip("\r\n").split(";")
            if len(parts) < 5 or not parts[0].strip():
                continue
            m = LREF_RE.search(parts[3])
            yield (parts[0].strip(), parts[1].strip(),
                   int(m.group(1)) if m else None)


def sense_sort_key(sense):
    try:
        return (0, int(sense))
    except (TypeError, ValueError):
        return (1, 0)


def _match_rec(rec, nt):
    return _key_lower(rec[2]) == nt or _key_lower(rec[3]) == nt


def build_join(csv_path, xlsx_path, pwg_txt_path):
    """Return (tsv_rows, stats). tsv_rows sorted by (L, sense)."""
    by_l, by_pc = parse_pwg_index(pwg_txt_path)
    x_rows = list(read_xlsx_rows(xlsx_path))
    c_rows = list(read_csv_rows(csv_path))

    tsv_rows, unjoined = [], []
    for dev, translit, sense, numerik, lref in x_rows:
        nt = iast_to_slp1(translit).lower()
        rec = None
        anchor = ""
        # Numerik can be a page RANGE ('1-0003 , 1-0004') — try each page.
        pages = [p.strip() for p in numerik.split(",")] if numerik else []
        if nt and pages:
            cands, seen = [], set()
            for pg in pages:
                for r in by_pc.get(pg, ()):
                    if _match_rec(r, nt) and r[0] not in seen:
                        seen.add(r[0])
                        cands.append(r)
            if len(cands) > 1 and sense:
                homed = [r for r in cands if r[4] == sense]
                cands = homed or cands
            if cands:
                rec, anchor = cands[0], "pc"
        if rec is None and nt and lref is not None:
            cand = by_l.get(str(lref))
            if cand is not None and _match_rec(cand, nt):
                rec, anchor = cand, "L"
        if rec is None:
            unjoined.append((dev, translit, sense, numerik, lref))
            continue
        tsv_rows.append((int(rec[0]) if rec[0].isdigit() else rec[0],
                         rec[2], dev, translit, sense or "", rec[1], anchor))
    tsv_rows.sort(key=lambda r: ((0, r[0], 0) if isinstance(r[0], int)
                                 else (1, 0, r[0]), sense_sort_key(r[4])))

    # CSV<->XLSX alignment probe (order-independent, L-multiset overlap).
    c_lrefs = Counter(r[2] for r in c_rows)
    x_lrefs = Counter(r[4] for r in x_rows)
    align_both = sum((c_lrefs & x_lrefs).values())

    joined_L = {r[0] for r in tsv_rows}
    joined_k1 = {r[1] for r in tsv_rows}
    all_k1 = {r[2] for r in by_l.values()}
    n_pc = sum(1 for r in tsv_rows if r[6] == "pc")
    stats = {
        "pwg_txt_entries": len(by_l),
        "pwg_txt_distinct_k1": len(all_k1),
        "csv_data_rows": len(c_rows),
        "csv_distinct_words": len({r[0] for r in c_rows}),
        "xlsx_data_rows": len(x_rows),
        "xlsx_rows_with_L": sum(1 for r in x_rows if r[4] is not None),
        "xlsx_distinct_L": len({r[4] for r in x_rows if r[4] is not None}),
        "joined_rows": len(tsv_rows),
        "joined_via_pc": n_pc,
        "joined_via_L": len(tsv_rows) - n_pc,
        "unjoined_rows": len(unjoined),
        "unjoined_examples": [u for u in unjoined[:5]],
        "joined_distinct_L": len(joined_L),
        "joined_distinct_key1": len(joined_k1),
        "coverage_pct_of_pwg_entries": round(100.0 * len(joined_L) / len(by_l), 2)
                                       if by_l else 0.0,
        "coverage_pct_of_pwg_headwords": round(100.0 * len(joined_k1) / len(all_k1), 2)
                                         if all_k1 else 0.0,
        "csv_xlsx_L_overlap_rows": align_both,
    }
    return tsv_rows, stats


def emit_tsv(rows, out_path):
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(TSV_HEADER) + "\n")
        for r in rows:
            fh.write("\t".join("" if c is None else str(c) for c in r) + "\n")


def tsv_bytes(rows):
    out = "\t".join(TSV_HEADER) + "\n"
    out += "".join("\t".join("" if c is None else str(c) for c in r) + "\n"
                   for r in rows)
    return out.encode("utf-8")


def print_stats(stats):
    for k, v in stats.items():
        if k == "unjoined_examples":
            continue
        print(f"{k}: {v}")
    for ex in stats.get("unjoined_examples", []):
        print(f"unjoined example: dev={ex[0]!r} translit={ex[1]!r} "
              f"sense={ex[2]!r} pc={ex[3]!r} L={ex[4]}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", required=True, help="Boethlingk_PWGScan.csv (scratch copy)")
    ap.add_argument("--xlsx", required=True,
                    help="Boethlingk_PWGScan_Devanagary.xlsx (scratch copy)")
    ap.add_argument("--pwg-txt", required=True,
                    help="csl-orig v02/pwg/pwg.txt (lane PWG base layer)")
    ap.add_argument("--emit", help="write the derived join TSV here")
    ap.add_argument("--check", help="verify this existing TSV matches a fresh derive")
    args = ap.parse_args(argv)

    rows, stats = build_join(args.csv, args.xlsx, args.pwg_txt)
    print_stats(stats)

    rc = 0
    if args.emit:
        emit_tsv(rows, args.emit)
        print(f"emit: wrote {len(rows)} rows -> {args.emit}")
    if args.check:
        with open(args.check, "rb") as fh:
            existing = fh.read()
        fresh = tsv_bytes(rows)
        if existing == fresh:
            print(f"check: PARITY OK ({args.check})")
        else:
            print(f"check: MISMATCH — {args.check} drifts from a fresh derive")
            rc = 1
    elif not args.emit:
        print("note: no --emit/--check given — census only")
    return rc


if __name__ == "__main__":
    sys.exit(main())
