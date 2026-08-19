#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mbh_russian_editions.py — which Russian edition carries a cited MBh verse (H3152 A6).

MG review point 1, third question: having the critical address, *«So we can find
the Russian translation of the quote itself?»*. The address alone does not answer
it — you also need to know which printed volume covers that parvan, who
translated it and whether a Russian translation exists at all. That index did not
exist anywhere in the organisation, in any form; this is the one genuinely new
asset of H3152.

Reads ``data/mbh_russian_editions.tsv``, 18 rows, one per parvan.

Two parvans have no complete Russian translation and say so **in words** rather
than with an empty cell — Śānti (12) and Anuśāsana (13). Śānti is the larger
gap in practice: PWG cites it heavily (5,647 Mahābhārata citations in the store,
a large share from parvan 12) and only Mokṣadharma and Nārāyaṇīya have ever been
put into Russian, by Smirnov, outside the academic series.

Confidence is a column, not a footnote
--------------------------------------
Bibliographic detail for a translation series published across 55 years is
exactly where an unattended agent would quietly invent a year. So every row
carries its own ``confidence``:

``org-verified``
    corroborated by committed metadata in this organisation — the row can be
    quoted as it stands.
``series-standard``
    the standard volume of the academic series; right in substance, but the
    imprint line has not been checked against the physical book.
``needs-check``
    a human must verify before this row is cited in a paper.

Nothing here is silently promoted. A row that is not ``org-verified`` is a
research lead, not a citation.

Run::

    python src/mbh_russian_editions.py              # print the table
    python src/mbh_russian_editions.py 12           # what covers parvan 12?
    python src/mbh_russian_editions.py --selftest
"""
import sys, os, io, csv, argparse

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(os.path.dirname(HERE), "data", "mbh_russian_editions.tsv")

#: the confidence vocabulary, most trustworthy first
ORG_VERIFIED = "org-verified"
SERIES_STANDARD = "series-standard"
NEEDS_CHECK = "needs-check"
CONFIDENCE = (ORG_VERIFIED, SERIES_STANDARD, NEEDS_CHECK)

#: how a row without a published translation is written, so the absence is a
#: statement and never an empty cell
NO_EDITION = "нет издания"

_rows = None


def load(path=None):
    """``{parvan:int -> row dict}``. Comment lines (leading ``#``) are the header
    prose and are skipped; the first non-comment line is the column header."""
    global _rows
    if _rows is not None and path is None:
        return _rows
    out = {}
    with io.open(path or TSV, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    for row in csv.DictReader(lines, delimiter="\t"):
        try:
            out[int(row["parvan"])] = row
        except (KeyError, TypeError, ValueError):
            continue
    if path is None:
        _rows = out
    return out


def for_parvan(parvan):
    """The edition row for one parvan, or ``None`` outside 1–18."""
    return load().get(int(parvan))


def describe(parvan):
    """One human line: which Russian volume covers this parvan, or that none does."""
    r = for_parvan(parvan)
    if not r:
        return None
    if r["volume_ru"] == NO_EDITION:
        return "%s (%s): полного русского перевода нет — %s" % (
            r["name_ru"], r["name_iast"], r["note"])
    return "%s (%s): %s, пер. %s, %s, %s [%s]" % (
        r["name_ru"], r["name_iast"], r["volume_ru"], r["translator"],
        r["year"], r["publisher"], r["confidence"])


def render():
    rows = load()
    out = ["%-3s %-22s %-18s %-32s %-6s %-16s" %
           ("#", "парва", "том", "переводчик", "год", "достоверность"),
           "-" * 100]
    for p in sorted(rows):
        r = rows[p]
        out.append("%-3d %-22s %-18s %-32s %-6s %-16s"
                   % (p, r["name_ru"], r["volume_ru"], r["translator"],
                      r["year"], r["confidence"]))
    return "\n".join(out)


def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    rows = load()
    check(len(rows) == 18, "all 18 parvans have a row (%d)" % len(rows))
    check(sorted(rows) == list(range(1, 19)),
          "the parvans are 1..18 with no gap and no duplicate")

    # A6 acceptance: not one empty cell anywhere
    empty = [(p, c) for p in sorted(rows) for c, v in rows[p].items()
             if v is None or not str(v).strip()]
    check(not empty, "no empty cell in any row (%r)" % empty[:4])

    # absence is written in words, never left blank
    for p in (12, 13):
        r = rows[p]
        check(r["volume_ru"] == NO_EDITION and "нет" in r["translator"],
              "parvan %d records the absence of a translation in words: %r"
              % (p, r["translator"]))
    check(describe(12).startswith("Шантипарва"), "describe() for a gap parvan")
    check("полного русского перевода нет" in describe(13),
          "describe() says so plainly for Anuśāsana")

    # every confidence value is from the vocabulary — no ad-hoc third state
    bad = sorted({r["confidence"] for r in rows.values()} - set(CONFIDENCE))
    check(not bad, "confidence values are all from the vocabulary (%r)" % bad)

    # the org-verified rows must name the file that verifies them
    for p, r in rows.items():
        if r["confidence"] == ORG_VERIFIED:
            check("/" in r["source"] and r["source"].endswith(("json", "txt")),
                  "parvan %d cites the file that verifies it: %s" % (p, r["source"]))

    # the multi-parvan volumes agree with one another
    check(rows[10]["volume_ru"] == rows[11]["volume_ru"],
          "books 10 and 11 share one volume")
    check(len({rows[p]["volume_ru"] for p in (15, 16, 17, 18)}) == 1,
          "books 15–18 share one volume")
    check(len({rows[p]["year"] for p in (15, 16, 17, 18)}) == 1,
          "…and one year")

    check(for_parvan(19) is None and for_parvan(0) is None,
          "a parvan outside 1–18 has no row rather than a wrong one")

    print("mbh_russian_editions selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("parvan", nargs="?", type=int)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.parvan:
        d = describe(a.parvan)
        if not d:
            print("no such parvan: %s (1–18)" % a.parvan)
            return 1
        print(d)
        return 0
    print(render())
    return 0


if __name__ == "__main__":
    sys.exit(main())
