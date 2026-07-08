#!/usr/bin/env python
"""Deterministic census of case-government markers (Rektion) in the raw PWG source.

H335 W3(a): answers "snih requires Locativus — сколько таких помет в PWG?"
Counts explicit government markers in the German sense text of csl-orig
``pwg.txt`` (the RAW source, never masked skeletons):

  * parenthesized case groups:      ``(<ab>loc.</ab>)``,
                                    ``(<ab>loc.</ab> und <ab>gen.</ab>)``,
                                    ``(<ab>acc.</ab> oder <ab>loc.</ab>)``
  * mit-phrases (prose government): ``mit <ab>acc.</ab>``, ``mit dem <ab>gen.</ab>``

Core government cases: acc / loc / instr / gen / dat / abl. Parenthesized
``nom.``/``voc.`` are tallied separately (usually citation-form notes, not
government). Text inside ``<ls>...</ls>`` citation spans is excluded before
matching. Groups containing prose besides case abbreviations (rare) are NOT
matched — the census is a deterministic floor, not a ceiling.

Usage:
  python government_census.py [--source PATH] [--tsv OUT.tsv] [--top N]
  python government_census.py selftest

Read-only over the source; writes only the optional TSV. No LLM, no network.
"""

import argparse
import io
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SOURCE = os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "csl-orig", "v02", "pwg", "pwg.txt")
)

GOV_CASES = ("acc", "loc", "instr", "gen", "dat", "abl")
NONGOV_CASES = ("nom", "voc")
ALL_CASES = GOV_CASES + NONGOV_CASES

_AB = r"<ab>(?:%s)\.</ab>" % "|".join(ALL_CASES)
PAREN_RE = re.compile(
    r"\(\s*(" + _AB + r"(?:\s*(?:,|und|oder)\s*" + _AB + r")*)\s*\)"
)
CASE_RE = re.compile(r"<ab>(%s)\.</ab>" % "|".join(ALL_CASES))
CONNECTOR_RE = re.compile(r"\b(und|oder)\b")
MIT_RE = re.compile(r"\bmit (?:dem |der )?(" + _AB + r")")
LS_RE = re.compile(r"<ls\b[^>]*>.*?</ls>", re.S)
LEX_RE = re.compile(r"<lex>([^<]+)</lex>")
SENSE_SPLIT_RE = re.compile(r"\d+〉")


def classify_pos(head_line, body_text):
    """Coarse POS for the census: verb root vs head-line <lex> class vs unknown.

    PWG root entries are marked by a leading root sign OR (more often) a
    Dhatupatha citation on the head line ({#sTA#}, {#ti/zWati#} <ls>DHATUP...).
    <lex> is trusted only on the HEAD line — a <lex> deep in the body belongs
    to a derived form, not the headword (sTA would classify as adj otherwise).
    """
    if "√" in head_line or "DHĀTUP" in head_line:
        return "verb"
    m = LEX_RE.search(head_line)
    if not m:
        return "unknown"
    lex = m.group(1).strip().rstrip(".").lower()
    if lex.startswith("adj"):
        return "adj"
    if lex.startswith(("m", "f", "n")):
        return "nominal"
    if lex.startswith(("adv", "indecl", "interj", "praep")):
        return "indecl"
    return "other(%s)" % lex


def sense_units(entry_lines):
    """Yield (unit_label, text) — one unit per <div> block segment / head line,
    further split at numbered sense markers ``N〉``. Deterministic proxy for
    'sense' on the raw line-structured source."""
    for i, line in enumerate(entry_lines):
        label = "head" if i == 0 else "div%d" % i
        parts = SENSE_SPLIT_RE.split(line)
        if len(parts) == 1:
            yield label, line
        else:
            for j, part in enumerate(parts):
                yield "%s.s%d" % (label, j), part


def scan_entry(header, entry_lines):
    """Return list of hit dicts for one <L> entry."""
    hits = []
    head_line = entry_lines[0] if entry_lines else ""
    pos = classify_pos(head_line, "\n".join(entry_lines))
    for unit, text in sense_units(entry_lines):
        text_nols = LS_RE.sub("", text)
        for m in PAREN_RE.finditer(text_nols):
            cases = CASE_RE.findall(m.group(1))
            connectors = sorted(set(CONNECTOR_RE.findall(m.group(1))))
            kind = "paren-single" if len(cases) == 1 else "paren-variation"
            if all(c in NONGOV_CASES for c in cases):
                kind = "paren-nongov"
            hits.append({
                "L": header.get("L", ""), "k1": header.get("k1", ""),
                "h": header.get("h", ""), "pos": pos, "unit": unit,
                "kind": kind, "cases": "+".join(cases),
                "connector": "/".join(connectors),
                "snippet": m.group(0),
            })
        for m in MIT_RE.finditer(text_nols):
            cases = CASE_RE.findall(m.group(1))
            hits.append({
                "L": header.get("L", ""), "k1": header.get("k1", ""),
                "h": header.get("h", ""), "pos": pos, "unit": unit,
                "kind": "mit-phrase", "cases": "+".join(cases),
                "connector": "", "snippet": m.group(0),
            })
    return hits


HEADER_RE = re.compile(r"<L>(\d+).*?<k1>([^<]*)(?:<k2>[^<]*)?(?:<h>(\d+))?")


def iter_entries(fh):
    """Yield (header_dict, entry_lines) per <L>..<LEND> block."""
    header, lines = None, []
    for raw in fh:
        line = raw.rstrip("\n")
        if line.startswith("<L>"):
            m = HEADER_RE.match(line)
            header = {"L": m.group(1) if m else "", "k1": m.group(2) if m else "",
                      "h": m.group(3) or "" if m else ""}
            lines = []
        elif line.startswith("<LEND>"):
            if header is not None:
                yield header, lines
            header, lines = None, []
        elif header is not None and line:
            lines.append(line)


def run_census(source, tsv=None, top=10):
    n_entries = 0
    n_units = 0
    entries_with = set()
    units_with = set()
    kind_counter = Counter()
    case_counter = defaultdict(Counter)   # kind -> cases-combo -> n
    pos_entry = defaultdict(set)          # pos -> set of L with >=1 gov hit
    pos_entries_all = Counter()           # pos -> total entries
    per_entry_hits = Counter()
    all_hits = []
    with open(source, encoding="utf-8") as fh:
        for header, entry_lines in iter_entries(fh):
            n_entries += 1
            units = list(sense_units(entry_lines))
            n_units += len(units)
            hits = scan_entry(header, entry_lines)
            head_line = entry_lines[0] if entry_lines else ""
            pos_entries_all[classify_pos(head_line, "\n".join(entry_lines))] += 1
            for hval in hits:
                kind_counter[hval["kind"]] += 1
                case_counter[hval["kind"]][hval["cases"]] += 1
                if hval["kind"] != "paren-nongov":
                    entries_with.add(hval["L"])
                    units_with.add((hval["L"], hval["unit"]))
                    pos_entry[hval["pos"]].add(hval["L"])
                    per_entry_hits[(hval["L"], hval["k1"])] += 1
            all_hits.extend(hits)
    if tsv:
        cols = ["L", "k1", "h", "pos", "unit", "kind", "cases", "connector", "snippet"]
        with open(tsv, "w", encoding="utf-8", newline="") as out:
            out.write("\t".join(cols) + "\n")
            for hval in all_hits:
                out.write("\t".join(str(hval[c]) for c in cols) + "\n")
    return {
        "n_entries": n_entries, "n_units": n_units,
        "entries_with": len(entries_with), "units_with": len(units_with),
        "kinds": dict(kind_counter),
        "cases": {k: dict(v) for k, v in case_counter.items()},
        "pos_gov_entries": {k: len(v) for k, v in pos_entry.items()},
        "pos_entries_all": dict(pos_entries_all),
        "top_entries": per_entry_hits.most_common(top),
        "n_hits": len(all_hits),
    }


def print_report(r):
    gov_total = sum(n for k, n in r["kinds"].items() if k != "paren-nongov")
    print("# PWG case-government census (deterministic, raw source)")
    print()
    print("| metric | value |")
    print("|---|---|")
    print("| PWG entries scanned | %d |" % r["n_entries"])
    print("| sense units scanned | %d |" % r["n_units"])
    print("| government markers (total occurrences) | %d |" % gov_total)
    for kind in ("paren-single", "paren-variation", "mit-phrase", "paren-nongov"):
        print("| … %s | %d |" % (kind, r["kinds"].get(kind, 0)))
    print("| entries with >=1 government marker | %d |" % r["entries_with"])
    print("| sense units with >=1 government marker | %d |" % r["units_with"])
    print()
    for kind in ("paren-single", "paren-variation", "mit-phrase"):
        combos = r["cases"].get(kind, {})
        if not combos:
            continue
        print("## %s — by case(s)" % kind)
        print()
        print("| case(s) | n |")
        print("|---|---|")
        for combo, n in sorted(combos.items(), key=lambda x: -x[1]):
            print("| %s | %d |" % (combo, n))
        print()
    print("## POS of marker-bearing entries")
    print()
    print("| pos | entries w/ marker | entries total |")
    print("|---|---|---|")
    for pos, n in sorted(r["pos_gov_entries"].items(), key=lambda x: -x[1]):
        print("| %s | %d | %d |" % (pos, n, r["pos_entries_all"].get(pos, 0)))
    print()
    print("## Top entries by marker count")
    print()
    print("| L / k1 | markers |")
    print("|---|---|")
    for (lnum, k1), n in r["top_entries"]:
        print("| %s %s | %d |" % (lnum, k1, n))


FIXTURE = """<L>1<pc>1-1<k1>snih<k2>snih<h>1
<hom>1.</hom> √{#snih#}¦, {#sne/hati#} <ls>DHĀTUP. 26,91</ls>.
<div n="1"> 1〉 {%geschmeidig werden%}: {#x#} <ls>CARAKA 1,13</ls>.
<div n="1">— 2〉 {%sich heften auf%} (<ab>loc.</ab>): {#y#} <ls>KATHĀS. 11,11</ls>. {%Zuneigung empfinden zu%} (<ab>loc.</ab> und <ab>gen.</ab>): {#z#} <ls>ŚĀK. 102,6</ls>.
<div n="p">— {#sam#} {%zusammen kommen%} mit dem <ab>instr.</ab>: {#w#} <ls>MBH. 1,1</ls>.
<LEND>

<L>2<pc>1-2<k1>deva<k2>deva/
{#deva/#}¦ <lex>m.</lex> {%Gott%} (<ab>pl.</ab>) <ls>ṚV. 1,1,1</ls>. (<ab>voc.</ab>) auch so.
<LEND>

<L>3<pc>1-3<k1>sTA<k2>sTA<h>1
<hom>1.</hom> {#sTA#}¦, {#ti/zWati#} <ls>DHĀTUP. 22,30</ls>.
<div n="1"> 1〉 {%stehen bleiben bei%} (<ab>loc.</ab>): {#q#} <ls>MBH. 2,2</ls>. <lex>adj.</lex> {#sTita#}.
<LEND>
"""


def selftest():
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                     encoding="utf-8") as tf:
        tf.write(FIXTURE)
        path = tf.name
    try:
        r = run_census(path)
        assert r["n_entries"] == 3, r
        assert r["kinds"].get("paren-single") == 2, r          # snih (loc.) + sTA (loc.)
        assert r["kinds"].get("paren-variation") == 1, r       # (loc. und gen.)
        assert r["kinds"].get("mit-phrase") == 1, r            # mit dem instr.
        assert r["kinds"].get("paren-nongov") == 1, r          # (voc.); (pl.) never matches
        assert r["cases"]["paren-variation"] == {"loc+gen": 1}, r
        assert r["entries_with"] == 2, r                       # snih + sTA; deva's voc is nongov
        # sTA: no root sign, DHĀTUP head line, body <lex>adj.</lex> must NOT win
        assert r["pos_gov_entries"] == {"verb": 2}, r
        assert r["units_with"] == 3, r  # snih div2.s1 (both parens) + snih div3 (mit) + sTA div1.s1
        print("government_census selftest: OK")
    finally:
        os.unlink(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="census",
                    choices=["census", "selftest"])
    ap.add_argument("--source", default=DEFAULT_SOURCE)
    ap.add_argument("--tsv", default=None,
                    help="write per-hit rows to this TSV (gitignored path)")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()
    if args.cmd == "selftest":
        selftest()
        return
    if not os.path.exists(args.source):
        sys.exit("source not found: %s" % args.source)
    print_report(run_census(args.source, tsv=args.tsv, top=args.top))


if __name__ == "__main__":
    main()
