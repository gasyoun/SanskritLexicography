#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ls_gap_mine.py — mine the ⚑ mintable <ls> citation gaps (H2835).

[FINDINGS §536](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
left one bucket explicitly unmined: **16.4 %** of the pwg_ru store's 41,115
`<ls>` occurrences resolve to no href, and about 17 % of all occurrences carry a
**real locus** the resolver has no pattern for. "Go add patterns" is not a plan
until that mass is split by *why* it fails, because the two failure classes cost
wildly different amounts:

* **FORMAT** — the resolver demonstrably handles this source (other citations of
  it resolve), but *this* locus shape does not match its regex: a Roman numeral
  where the pattern wants digits, a `fgg.`/`ff.` range tail, an `(I)`/`(II)`
  volume marker, a bare continuation number. A scan target **already exists**;
  only the parse is missing. Cheap, mechanical, and verifiable against the
  citations of the same source that already work.
* **SOURCE** — the resolver never resolves this source at all. No amount of regex
  work helps: somebody has to find (or digitise) a target first. Real research,
  correctly out of scope for a rendering pass.

A third class falls out of the data and is worth naming because it is *not* work:

* **STRUCTURAL** — the "locus" is a bare volume/page marker or a continuation
  fragment (`(I)`, `II,`, `4,10,7.` after an `n=` prefix that itself did not
  resolve). These carry digits, so the ⚑/∅ split in `ls_links.py` counts them as
  mintable, but there is no independent work to point at.

Outputs (all under `reports/`):
  * `ls_gap_by_source.tsv`   — one row per source key: occurrences, class,
                               resolved/unresolved split, the pwgbib expansion,
                               and a worked example of each.
  * `ls_gap_examples.jsonl`  — up to N raw citations per source for eyeballing.
  * `LS_CITATION_GAP_REPORT.md` — the ranked, human-readable finding.

Run: python src/ls_gap_mine.py            (set PWG_RU_DATA_ROOT for the store)
     python src/ls_gap_mine.py --selftest
"""
import sys, os, io, json, re, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("LS_RESOLVER_QUIET", "1")

import ls_resolver as lsr
import pwg_sources as pwgsrc
from ls_links import LsLinks, HIT, NO_LOCUS, MINTABLE, LS_RE, LS_PARTS, _ws

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("PWG_RU_DATA_ROOT", os.path.dirname(HERE))
STORE = os.path.join(DATA, "src", "pwg_ru_translated.jsonl")
REPORTS = os.path.join(DATA, "reports")

#: failure classes
FORMAT = "format"        #: source resolves elsewhere; this locus shape does not
SOURCE = "source"        #: source never resolves — needs a target to exist
STRUCTURAL = "structural"  #: volume/continuation fragment — not independent work

#: locus shapes that explain a FORMAT miss, tested in order (first match wins)
SHAPE_TESTS = [
    ("roman", re.compile(r"(?<![A-Za-zĀĪŪṚṢŚṬḌṄÑṆṂḤ])[IVXLC]+[,.]")),
    ("range_fgg", re.compile(r"\b(fgg?|ff)\.")),
    ("vol_marker", re.compile(r"\((?:[IVXLC]+|[0-9]+)\)")),
    ("ed_variant", re.compile(r"\bed\.\s*(Bomb|Calc|Ser|Schl)")),
    ("ibid", re.compile(r"\bebend", re.I)),
    ("multi_locus", re.compile(r"[0-9]\s*[.,]\s*[0-9]+\s*[.,]\s*[0-9]+\s*[.,]\s*[0-9]")),
    ("trailing_prose", re.compile(r"[0-9][^0-9]{4,}$")),
]

#: a "locus" that is only a bare fragment — no work of its own
BARE_FRAGMENT = re.compile(r"^[\s0-9IVXLC(),.;-]*$")


def source_key(visible, n_attr):
    """The bibliographic key a citation belongs to.

    Prefers the `n=` continuation prefix, which is exactly what PWG supplies so a
    bare-number ref keeps its work; falls back to the resolver's own
    `extract_first_key` so this groups the way the resolver dispatches.
    """
    base = (n_attr or visible or "").strip()
    k = lsr.extract_first_key(base)
    if not k:
        k = pwgsrc.source_key(base)
    return (k or "?").strip().rstrip(".,").strip() or "?"


def locus_shape(visible):
    for name, rx in SHAPE_TESTS:
        if rx.search(visible or ""):
            return name
    return "plain"


def scan(store_path):
    """One pass over the store. Returns (per_source, totals)."""
    ll = LsLinks()
    per = collections.defaultdict(lambda: {
        "hit": 0, "mintable": 0, "no_locus": 0,
        "shapes": collections.Counter(),
        "ex_hit": None, "ex_miss": [],
    })
    totals = collections.Counter()

    for line in io.open(store_path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        for tag in LS_RE.findall(d.get("de") or ""):
            n_attr, visible = ll.parts(tag)
            status, href = ll.resolve(tag)
            key = source_key(visible, n_attr)
            rec = per[key]
            totals[status] += 1
            if status == HIT:
                rec["hit"] += 1
                if rec["ex_hit"] is None:
                    rec["ex_hit"] = (_ws(tag), href)
            elif status == MINTABLE:
                rec["mintable"] += 1
                rec["shapes"][locus_shape(visible)] += 1
                if len(rec["ex_miss"]) < 6:
                    rec["ex_miss"].append(_ws(tag))
            else:
                rec["no_locus"] += 1
    return per, totals


def classify(key, rec):
    """FORMAT / SOURCE / STRUCTURAL for one source key."""
    if rec["hit"] > 0:
        return FORMAT
    # no citation of this source ever resolves. Is the key itself a fragment?
    if BARE_FRAGMENT.match(key) or key in ("?", ""):
        return STRUCTURAL
    return SOURCE


def build_rows(per):
    rows = []
    for key, rec in per.items():
        if rec["mintable"] == 0:
            continue
        cls = classify(key, rec)
        shapes = rec["shapes"].most_common(3)
        rows.append({
            "source_key": key,
            "class": cls,
            "mintable": rec["mintable"],
            "resolved_same_source": rec["hit"],
            "no_locus_same_source": rec["no_locus"],
            "top_shapes": ";".join("%s=%d" % s for s in shapes),
            "expansion": (pwgsrc.resolve(key) or "")[:90],
            "example_miss": rec["ex_miss"][0] if rec["ex_miss"] else "",
            "example_hit": (rec["ex_hit"][0] if rec["ex_hit"] else ""),
            "example_hit_href": (rec["ex_hit"][1] if rec["ex_hit"] else ""),
            "_all_miss": rec["ex_miss"],
        })
    rows.sort(key=lambda r: (-r["mintable"], r["source_key"]))
    return rows


def write_outputs(rows, totals):
    os.makedirs(REPORTS, exist_ok=True)
    cols = ["source_key", "class", "mintable", "resolved_same_source",
            "no_locus_same_source", "top_shapes", "expansion",
            "example_miss", "example_hit", "example_hit_href"]
    tsv = os.path.join(REPORTS, "ls_gap_by_source.tsv")
    with io.open(tsv, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]).replace("\t", " ") for c in cols) + "\n")

    jl = os.path.join(REPORTS, "ls_gap_examples.jsonl")
    with io.open(jl, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps({"source_key": r["source_key"], "class": r["class"],
                                 "mintable": r["mintable"],
                                 "examples": r["_all_miss"]},
                                ensure_ascii=False) + "\n")
    return tsv, jl


def summarize(rows, totals):
    by_class = collections.Counter()
    src_by_class = collections.Counter()
    for r in rows:
        by_class[r["class"]] += r["mintable"]
        src_by_class[r["class"]] += 1
    return by_class, src_by_class


def main():
    if not os.path.exists(STORE):
        print("store not found: %s — set PWG_RU_DATA_ROOT" % STORE)
        return 1
    print("scanning %s ..." % STORE)
    per, totals = scan(STORE)
    rows = build_rows(per)
    tsv, jl = write_outputs(rows, totals)
    by_class, src_by_class = summarize(rows, totals)

    tot = sum(totals.values())
    print("\n<ls> occurrences        : %d" % tot)
    print("  resolved              : %6d  %5.1f%%" % (totals[HIT], 100.0*totals[HIT]/tot))
    print("  bare abbreviation (∅) : %6d  %5.1f%%" % (totals[NO_LOCUS], 100.0*totals[NO_LOCUS]/tot))
    print("  mintable (⚑)          : %6d  %5.1f%%" % (totals[MINTABLE], 100.0*totals[MINTABLE]/tot))
    print("\n⚑ split by why it fails:")
    for cls in (FORMAT, SOURCE, STRUCTURAL):
        n = by_class[cls]
        print("  %-11s %6d occurrences  %5.1f%% of ⚑   across %3d source keys"
              % (cls, n, 100.0*n/max(totals[MINTABLE], 1), src_by_class[cls]))
    print("\ntop 25 gaps:")
    print("  %-22s %-11s %7s %8s  %s" % ("source", "class", "⚑", "resolved", "top shape"))
    for r in rows[:25]:
        print("  %-22s %-11s %7d %8d  %s"
              % (r["source_key"][:22], r["class"], r["mintable"],
                 r["resolved_same_source"], r["top_shapes"][:34]))
    print("\nwrote %s\n      %s" % (tsv, jl))
    return 0


# --------------------------------------------------------------------- selftest
def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    # source_key groups the way the resolver dispatches, and honours n=
    check(source_key("12,8081.", "MBH.") == "MBH",
          "n= prefix supplies the source for a bare-number ref")
    check(source_key("MBH. 12,8081.", None) == "MBH", "plain form yields the same key")
    check(source_key("R. ed. Bomb. 1,2,3", None) == "R. ed. Bomb",
          "a complex multi-word prefix is kept whole, not cut at the first dot")

    # locus shapes
    check(locus_shape("HIT. I,139.") == "roman", "roman numeral locus detected")
    check(locus_shape("ŚAT. BR. 12,5,2,9. fgg.") == "range_fgg", "fgg. range detected")
    check(locus_shape("Spr. (II) 4021") == "vol_marker", "volume marker detected")
    check(locus_shape("MBH. 12,8081") == "plain", "an ordinary locus is plain")

    # classification: a source with ANY resolved citation is a FORMAT gap
    fmt = {"hit": 40, "mintable": 3, "no_locus": 0, "shapes": collections.Counter()}
    check(classify("HIT", fmt) == FORMAT, "source that resolves elsewhere -> format gap")
    src = {"hit": 0, "mintable": 30, "no_locus": 2, "shapes": collections.Counter()}
    check(classify("DAŚAK", src) == SOURCE, "source that never resolves -> source gap")
    check(classify("(I)", src) == STRUCTURAL, "a bare fragment key -> structural, not work")
    check(classify("II,", src) == STRUCTURAL, "a bare continuation key -> structural")

    print("ls_gap_mine selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
