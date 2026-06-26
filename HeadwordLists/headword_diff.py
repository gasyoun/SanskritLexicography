"""Now-vs-then diff for the HeadwordLists/*-unique-key{1,2}-N.txt snapshots.

Each committed list is a snapshot: its filename count N == its line count, taken
when the list was generated "long ago". This regenerates the same key set from
the *current* csl-orig and reports what changed (added / removed headwords),
writing the full per-list diffs under HeadwordLists/_diff/.

Recipe (validated against the committed files): the list is the sorted-unique set
of the dictionary's <k1> (key1) or <k2> (key2) field values, verbatim — no
normalisation. A near-zero added+removed with the recipe confirms the match;
a large systematic delta means the generator used a different field/normalisation.
"""
import sys, re, os, collections
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
OUT = os.path.join(HERE, "_diff")

# HeadwordLists DICT code -> csl-orig/v02 subdir.
# PWK = Böhtlingk's *kürzere Fassung* = csl-orig `pw`. PD (Deccan) is not in csl-orig.
CODE2DIR = {"AP": "ap", "BHS": "bhs", "BUR": "bur", "CAE": "cae", "CCS": "ccs",
            "GRA": "gra", "INM": "inm", "MD": "md", "MW": "mw", "PD": None,
            "PWG": "pwg", "PWK": "pw", "SCH": "sch", "SKD": "skd", "VCP": "vcp",
            "VEI": "vei"}

def src_path(d):
    for cand in (os.path.join(ORIG, d, d + ".txt"),):
        if os.path.exists(cand):
            return cand
    return None

def field_set(path, tag):
    txt = open(path, encoding="utf-8").read()
    return set(m.group(1) for m in re.finditer(r'<%s>([^<]*)' % tag, txt))

def main():
    files = sorted(f for f in os.listdir(HERE)
                   if re.match(r'^[A-Z]+-unique-key[12]-\d+\.txt$', f))
    os.makedirs(OUT, exist_ok=True)
    rows = []   # (file, then, now, added, removed, overlap_pct, verdict)
    for f in files:
        m = re.match(r'^([A-Z]+)-unique-key([12])-(\d+)\.txt$', f)
        code, kt = m.group(1), m.group(2)
        d = CODE2DIR.get(code)
        src = src_path(d) if d else None
        then = set(l.rstrip('\n') for l in open(os.path.join(HERE, f), encoding='utf-8-sig') if l.strip())
        if not src:
            rows.append((f, len(then), None, None, None, None,
                         "no csl-orig source (PD not in csl-orig)")); continue
        now = field_set(src, "k1" if kt == "1" else "k2")
        added, removed = now - then, then - now
        kept = len(then) - len(removed)
        overlap = 100 * kept / max(1, len(then))
        verdict = ("comparable" if overlap >= 50
                   else "format-migrated (legacy numeric → SLP1); raw diff not meaningful")
        rows.append((f, len(then), len(now), len(added), len(removed), overlap, verdict))
        base = f[:-4]
        for tag, s in (("added", added), ("removed", removed)):
            with open(os.path.join(OUT, base + "." + tag + ".txt"), "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(sorted(s)))
    # console table
    w = max(len(r[0]) for r in rows)
    print(f"{'file':<{w}} {'then':>8} {'now':>8} {'added':>7} {'removed':>8} {'overlap':>8}  verdict")
    for f, t, nw, a, rm, ov, v in rows:
        print(f"{f:<{w}} {t:>8} {('' if nw is None else nw):>8} {('' if a is None else a):>7} "
              f"{('' if rm is None else rm):>8} {('' if ov is None else f'{ov:.1f}%'):>8}  {v}")
    # summary markdown
    md = ["# HeadwordLists — now vs then",
          "",
          "Each `*-unique-key{1,2}-N.txt` is a snapshot whose filename count `N` is its "
          "line count at generation time (\"then\"). This compares each against the **current** "
          "csl-orig (\"now\"), regenerating the same field (`<k1>`/`<k2>`). Reproduce with "
          "[`headword_diff.py`](headword_diff.py); full word-level diffs land in `_diff/`.",
          "",
          "- **comparable** — the committed list and the live field share key format, so "
          "`added`/`removed` are genuine headword changes.",
          "- **format-migrated** — the committed `<k2>` snapshot is in the *legacy Cologne "
          "numeric transliteration* (`am2s4a` = aṃśa) while csl-orig is now SLP1; the raw diff "
          "is ~100 % and **not** a real headword change. Re-transcoding is needed to compare.",
          "- **PD** has no csl-orig source locally.",
          "",
          "| List | then | now | added | removed | overlap | verdict |",
          "|---|--:|--:|--:|--:|--:|---|"]
    for f, t, nw, a, rm, ov, v in rows:
        md.append(f"| [{f}]({f}) | {t} | {'' if nw is None else nw} | {'' if a is None else a} "
                  f"| {'' if rm is None else rm} | {'' if ov is None else f'{ov:.1f}%'} | {v} |")
    md += ["",
           "## Genuine changes (comparable lists)",
           "",
           "For the comparable lists, `removed` headwords (present then, gone now — merged, "
           "corrected, or deleted) are the sharpest QA signal; `added` are new/expanded keys. "
           "Full lists in `_diff/<list>.added.txt` and `_diff/<list>.removed.txt`.",
           ""]
    for f, t, nw, a, rm, ov, v in rows:
        if v != "comparable":
            continue
        removed_words = sorted(set(l.rstrip('\n') for l in
                          open(os.path.join(OUT, f[:-4] + ".removed.txt"), encoding="utf-8") if l.strip()))
        md.append(f"### {f} — {t} → {nw}  (+{a} / −{rm})")
        if removed_words and rm <= 60:
            md.append("removed: " + ", ".join(f"`{x}`" for x in removed_words))
        elif removed_words:
            md.append(f"removed ({rm}): " + ", ".join(f"`{x}`" for x in removed_words[:40]) + " … (full list in `_diff/`)")
        md.append("")
    open(os.path.join(HERE, "NOW_VS_THEN.md"), "w", encoding="utf-8", newline="\n").write("\n".join(md))
    print(f"\nWrote NOW_VS_THEN.md; full per-list diffs in {OUT}/")

if __name__ == "__main__":
    main()
