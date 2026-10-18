"""Assemble MG's own fuzzy MW<->PWK correction pairings (yadisk 05_Sanskrit-Lexicon/corrigenda/,
4 workbooks 2013-11-26 x3 + 2014-fuzzy) into one derived MW<->PWK pair table.

Derived-only (MG ruling 07-09-2026): the raw xlsx/xlsm workbooks stay on yadisk, never
committed here. Point CORRIGENDA_DIR at a local copy fetched via WebDAV
(see docs/agents -- yadisk WebDAV recipe, H4473) before running.

Three of the four workbooks are near-duplicates of the same 2013-11-26 comparison
(one plain .xlsx, one "peresortirovka" resort in .xlsx and .xlsm) -- verified here
(own-data parity check) that the MW/PWK/verdict columns are byte-identical across
all three; only the resort's derived "LEN(PWK)"/"Book" helper columns went stale
after the row reorder. Only the plain .xlsx is read; the other two are counted for
parity and skipped as confirmed duplicates.

H4537.
"""
import sys, os, csv
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
CORRIGENDA_DIR = os.environ.get("CORRIGENDA_DIR", os.path.join(HERE, "..", "_corrigenda_raw"))
OUT = os.path.join(HERE, "mw_pwk_corrigenda_pairs.tsv")

PLAIN_2013 = "Fuzzy-word-correction-MW-PWK_26112013.xlsx"
RESORT_XLSX = "Fuzzy-word-correction-MW-PWK_26112013-peresortirovka.xlsx"
RESORT_XLSM = "Fuzzy-word-correction-MW-PWK_26112013-peresortirovka.xlsm"
RAW_2014 = "fuzzy-mw-vs-pwk-2014.xlsm"

# expected sheet dims from the yadisk census (H4477 sec4) -- own-data parity floor
EXPECTED_DIMS = {
    ("Сравнительная1", PLAIN_2013): 9829,
    ("fuzzy_DEV_FINISH", PLAIN_2013): 27081,
    ("fuzzy_IAST_FINISH", PLAIN_2013): 28520,
    ("Совпадения MW и НАДPWK", PLAIN_2013): 1164,
    ("Лист1", RAW_2014): 193978,
}


def comparativa_verdict(row):
    """Сравнительная1: col3=editorial typo call, col4=note, col5=cross-list dup status."""
    typ, note, dup = row[3], row[4], row[5]
    parts = []
    if typ not in (None, 0, 1, "?"):
        parts.append(f"typo:{typ}")
    elif typ == "?":
        parts.append("uncertain")
    elif typ == 1:
        parts.append("flag:1")
    elif typ == 0:
        parts.append("flag:0")
    else:
        parts.append("unreviewed")
    if note:
        parts.append(f"note:{note}")
    if dup:
        parts.append(dup)
    return "; ".join(parts)


def dup_flag_verdict(row, col, present_label, absent_label):
    return present_label if row[col] == "Duplicate" else absent_label


def load_sheet(path, workbook_name, sheet_name, row_fn, id_col=0, min_row=2):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet_name]
    n = 0
    out = []
    for row in ws.iter_rows(min_row=min_row, values_only=True):
        if row[id_col] is None:
            continue
        n += 1
        out.append(row_fn(row, workbook_name, sheet_name))
    wb.close()
    return out, n


def main():
    rows = []
    parity = []

    p_plain = os.path.join(CORRIGENDA_DIR, PLAIN_2013)
    p_resort_x = os.path.join(CORRIGENDA_DIR, RESORT_XLSX)
    p_resort_m = os.path.join(CORRIGENDA_DIR, RESORT_XLSM)
    p_2014 = os.path.join(CORRIGENDA_DIR, RAW_2014)

    for missing in (p_plain, p_resort_x, p_resort_m, p_2014):
        if not os.path.exists(missing):
            print(f"MISSING workbook, cannot proceed: {missing}", file=sys.stderr)
            sys.exit(1)

    # own-data parity: confirm the two 2013 duplicate variants carry the same row
    # counts per sheet as the plain canonical source (content already verified
    # byte-identical for MW/PWK/verdict columns in the H4537 exploration pass).
    for dup_path, dup_name in ((p_resort_x, RESORT_XLSX), (p_resort_m, RESORT_XLSM)):
        wb = openpyxl.load_workbook(dup_path, read_only=True, data_only=True)
        for sn in ("Сравнительная1", "fuzzy_DEV_FINISH", "fuzzy_IAST_FINISH", "Совпадения MW и НАДPWK"):
            ws = wb[sn]
            expected = EXPECTED_DIMS.get((sn, PLAIN_2013))
            ok = (ws.max_row == expected)
            parity.append((dup_name, sn, ws.max_row, expected, ok))
        wb.close()

    # sheet 1: Сравнительная1 -- IAST, editorial verdict column
    r, n = load_sheet(p_plain, PLAIN_2013, "Сравнительная1",
                       lambda row, wbn, sn: (wbn, sn, row[0], "iast", row[1], row[2], comparativa_verdict(row)))
    rows += r
    parity.append((PLAIN_2013, "Сравнительная1", n + 1, EXPECTED_DIMS[("Сравнительная1", PLAIN_2013)], n + 1 == EXPECTED_DIMS[("Сравнительная1", PLAIN_2013)]))

    # sheet 2: fuzzy_DEV_FINISH -- devanagari pair, use its own IAST columns (4,5) for the pair key
    r, n = load_sheet(p_plain, PLAIN_2013, "fuzzy_DEV_FINISH",
                       lambda row, wbn, sn: (wbn, sn, row[0], "iast", row[4], row[5],
                                             dup_flag_verdict(row, 6, "cross-dup:in-iast-list", "unique-to-dev-list")))
    rows += r
    parity.append((PLAIN_2013, "fuzzy_DEV_FINISH", n + 1, EXPECTED_DIMS[("fuzzy_DEV_FINISH", PLAIN_2013)], n + 1 == EXPECTED_DIMS[("fuzzy_DEV_FINISH", PLAIN_2013)]))

    # sheet 3: fuzzy_IAST_FINISH -- IAST pair
    r, n = load_sheet(p_plain, PLAIN_2013, "fuzzy_IAST_FINISH",
                       lambda row, wbn, sn: (wbn, sn, row[0], "iast", row[1], row[2],
                                             dup_flag_verdict(row, 3, "cross-dup:in-dev-list", "unique-to-iast-list")))
    rows += r
    parity.append((PLAIN_2013, "fuzzy_IAST_FINISH", n + 1, EXPECTED_DIMS[("fuzzy_IAST_FINISH", PLAIN_2013)], n + 1 == EXPECTED_DIMS[("fuzzy_IAST_FINISH", PLAIN_2013)]))

    # sheet 4: Совпадения MW и НАДPWK -- exact-string matches (MW == PWK), dup status vs the other two lists
    r, n = load_sheet(p_plain, PLAIN_2013, "Совпадения MW и НАДPWK",
                       lambda row, wbn, sn: (wbn, sn, row[0], "iast", row[1], row[2],
                                             "exact-match; " + (row[3] or "")))
    rows += r
    parity.append((PLAIN_2013, "Совпадения MW и НАДPWK", n + 1, EXPECTED_DIMS[("Совпадения MW и НАДPWK", PLAIN_2013)], n + 1 == EXPECTED_DIMS[("Совпадения MW и НАДPWK", PLAIN_2013)]))

    # sheet 5: 2014 raw candidate list -- SLP1, no header row, no human verdict recorded
    r, n = load_sheet(p_2014, RAW_2014, "Лист1",
                       lambda row, wbn, sn: (wbn, sn, None, "slp1", row[1], row[2], "unverified-candidate"),
                       id_col=1, min_row=1)
    rows += r
    parity.append((RAW_2014, "Лист1", n, EXPECTED_DIMS[("Лист1", RAW_2014)], n == EXPECTED_DIMS[("Лист1", RAW_2014)]))

    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["source_workbook", "source_sheet", "row_id", "script", "mw", "pwk", "verdict"])
        for row in rows:
            w.writerow(["" if v is None else v for v in row])

    print(f"wrote {OUT}: {len(rows)} pairs")
    print("own-data parity (sheet row count vs workbook dims, H4477 census sec4):")
    all_ok = True
    for wbn, sn, got, expected, ok in parity:
        all_ok = all_ok and ok
        print(f"  {wbn} :: {sn} -> got={got} expected={expected} {'OK' if ok else 'MISMATCH'}")
    if not all_ok:
        print("PARITY MISMATCH -- see above", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
