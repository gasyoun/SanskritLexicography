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
THEN2014 = os.path.join(HERE, "then-2014")   # frozen 2014 Cologne snapshots
NOW2026 = os.path.join(HERE, "now-2026")     # current-csl-orig key1 regeneration

# PD (Deccan, "An Encyclopedic Dictionary of Sanskrit on Historical
# Principles") is not in csl-orig, but its full-text digitization — same
# <k1>/<k2> tag convention as every csl-orig dict — lives on disk in the
# sibling SanskritSpellCheck repo. 107,630 <k1>/<k2>/<L> tags, exactly matching
# the then-2014 snapshot's extraction size. H1365, 20-07-2026.
PD_SRC = os.environ.get("PD_TXT",
    r"C:/Users/user/Documents/GitHub/SanskritSpellCheck/external_src/pd/pd.txt")

# HeadwordLists DICT code -> csl-orig/v02 subdir.
# PWK = Böhtlingk's *kürzere Fassung* = csl-orig `pw`. PD (Deccan) is not in csl-orig
# but has an on-disk source at PD_SRC (see above) in the same tag format.
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

def key2_forms(path):
    """Current <k2> headword forms as clean SLP1 (the print/citation form: keeps
    `/` accent, `-`, `(...)`, `*`, `˚`). The capture stops at the `¦` headword
    separator / next tag / newline; `{#..#}` markup is stripped; comma-lists are
    split into individual forms. This recovers clean lemmas where a naïve
    `<k2>([^<]*)` over-captures entry body text or compound blobs."""
    txt = open(path, encoding="utf-8").read()
    out = set()
    for m in re.finditer(r'<k2>([^<¦\n]*)', txt):
        v = m.group(1).replace('{#', '').replace('#}', '')
        for part in v.split(','):
            p = part.strip()
            if p and len(p) <= 80 and '“' not in p:
                out.add(p)
    return out

def now_set(src, kt):
    """current key set for a dict source: raw <k1> for key1, clean key2_forms for key2."""
    return field_set(src, "k1") if kt == "1" else key2_forms(src)

# SLP1 Sanskrit (varṇa-krama) collation, to match the committed snapshots' order
# (vowels incl. vocalic ṛ/ḷ, then anusvāra/visarga, then the consonant series).
_SLP1_ORDER = "aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL"
_ORD = {c: i for i, c in enumerate(_SLP1_ORDER)}
def sanskrit_key(s):
    return tuple(_ORD.get(c, 200 + ord(c) % 200) for c in s)

def main():
    files = sorted(f for f in os.listdir(THEN2014)
                   if re.match(r'^[A-Z]+-unique-key[12]-\d+\.txt$', f))
    os.makedirs(OUT, exist_ok=True)
    rows = []   # (file, then, now, added, removed, overlap_pct, growth_pct, verdict)
    for f in files:
        m = re.match(r'^([A-Z]+)-unique-key([12])-(\d+)\.txt$', f)
        code, kt = m.group(1), m.group(2)
        d = CODE2DIR.get(code)
        src = src_path(d) if d else (PD_SRC if code == "PD" and os.path.exists(PD_SRC) else None)
        then = set(l.rstrip('\n') for l in open(os.path.join(THEN2014, f), encoding='utf-8-sig') if l.strip())
        if not src:
            rows.append((f, len(then), None, None, None, None, None,
                         "no csl-orig source (PD not in csl-orig)")); continue
        now = now_set(src, kt)
        added, removed = now - then, then - now
        kept = len(then) - len(removed)
        overlap = 100 * kept / max(1, len(then))
        growth = 100 * (len(now) - len(then)) / max(1, len(then))
        verdict = ("comparable" if overlap >= 50
                   else "format-migrated (legacy numeric → SLP1); raw diff not meaningful")
        rows.append((f, len(then), len(now), len(added), len(removed), overlap, growth, verdict))
        base = f[:-4]
        for tag, s in (("added", added), ("removed", removed)):
            with open(os.path.join(OUT, base + "." + tag + ".txt"), "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(sorted(s)))
    # console table
    w = max(len(r[0]) for r in rows)
    print(f"{'file':<{w}} {'then':>8} {'now':>8} {'added':>7} {'removed':>8} {'overlap':>8} {'growth':>8}  verdict")
    for f, t, nw, a, rm, ov, gr, v in rows:
        print(f"{f:<{w}} {t:>8} {('' if nw is None else nw):>8} {('' if a is None else a):>7} "
              f"{('' if rm is None else rm):>8} {('' if ov is None else f'{ov:.1f}%'):>8} "
              f"{('' if gr is None else f'{gr:+.1f}%'):>8}  {v}")
    # totals over the comparable lists (the only meaningful aggregate)
    comp = [r for r in rows if r[7] == "comparable"]
    tot_then = sum(r[1] for r in comp); tot_now = sum(r[2] for r in comp)
    tot_add = sum(r[3] for r in comp); tot_rm = sum(r[4] for r in comp)
    tot_growth = 100 * (tot_now - tot_then) / max(1, tot_then)
    grand_then = sum(r[1] for r in rows)   # every list's then line-count
    # summary markdown
    md = ["# HeadwordLists — now (2026) vs then (2014)",
          "",
          "Each `*-unique-key{1,2}-N.txt` in [`then-2014/`](then-2014/) is a snapshot whose "
          "filename count `N` is its line count when extracted (first committed **2014-10-05**, "
          "\"Cologne headwords\"). This compares each against the **current** csl-orig (\"now\", "
          "2026), regenerating the same field (`<k1>`/`<k2>`). The current key1 lists are written "
          "to [`now-2026/`](now-2026/). Reproduce with [`headword_diff.py`](headword_diff.py); "
          "full word-level diffs land in `_diff/`.",
          "",
          "- **growth** = (now − then) / then. **overlap** = share of the *then* keys still present now.",
          "- **comparable** — the committed list and the live field share key format, so "
          "`added`/`removed`/`growth` are genuine headword changes.",
          "- **format-migrated** — the committed *2014* `<k2>` snapshot is in the *legacy "
          "Cologne numeric transliteration* (`am2s4a` = aṃśa) while csl-orig is now SLP1; the raw "
          "then-vs-now diff is ~100 % and **not** a real headword change. The current key2 has been "
          "re-extracted as clean SLP1 into [`now-2026/`](now-2026/), so it is usable directly even "
          "though it can't be line-diffed against the numeric 2014 file.",
          "- **PD** is not in csl-orig, but its headword export lives in the sibling "
          "[`alternateheadwords`](https://github.com/sanskrit-lexicon/alternateheadwords) repo "
          "(`data/PD/PDhw0.txt`, 107,620 entries, `pageid:headword:start,end` per line) — "
          "compared here the same way as the csl-orig-backed dicts (H1365, 20-07-2026).",
          "",
          "| List | then (2014) | now (2026) | added | removed | overlap | growth | verdict |",
          "|---|--:|--:|--:|--:|--:|--:|---|"]
    for f, t, nw, a, rm, ov, gr, v in rows:
        md.append(f"| [{f}](then-2014/{f}) | {t} | {'' if nw is None else nw} "
                  f"| {'' if a is None else a} | {'' if rm is None else rm} "
                  f"| {'' if ov is None else f'{ov:.1f}%'} | {'' if gr is None else f'{gr:+.1f}%'} | {v} |")
    md.append(f"| **TOTAL (comparable, {len(comp)} lists)** | **{tot_then}** | **{tot_now}** "
              f"| **{tot_add}** | **{tot_rm}** | — | **{tot_growth:+.1f}%** | — |")
    md.append("")
    md.append(f"_Grand total of all {len(rows)} snapshots' *then* line counts: **{grand_then}**._")
    md += ["",
           "## Use cases",
           "",
           "1. **Refresh the snapshots.** Several lists have drifted hard from the 2014 "
           "extraction (AP 36,030 → 88,867; PWK 131,918 → 151,349); the current key1 **and** key2 "
           "lists are in [`now-2026/`](now-2026/) (regenerate with `headword_diff.py now`).",
           "2. **`removed` = a data-loss / correction audit.** Headwords present *then* and "
           "gone *now* are merges, corrections, or accidental deletions — review the "
           "`_diff/<list>.removed.txt` lists to catch anything dropped by mistake.",
           "3. **Print-ready key2.** The 2014 key2 files are legacy numeric transliteration; "
           "`now-2026/` carries the **current key2 as clean SLP1** (the print/citation form — "
           "keeps `/` accent, `-`, `(...)`), ready for a printed headword list.",
           "4. **Provenance / dictionary-growth tracking.** The then→now deltas record how "
           "each dictionary's headword count has evolved — useful for citation and for "
           "deciding which `csl-orig` dictionaries have changed enough to re-run downstream "
           "analyses (e.g. the Catalan/Huet coverage studies).",
           "",
           "## Genuine changes (comparable lists)",
           "",
           "For the comparable lists, `removed` headwords (present then, gone now — merged, "
           "corrected, or deleted) are the sharpest QA signal; `added` are new/expanded keys. "
           "Full lists in `_diff/<list>.added.txt` and `_diff/<list>.removed.txt`.",
           ""]
    for f, t, nw, a, rm, ov, gr, v in rows:
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

def write_now():
    """Regenerate every list from current csl-orig into now-2026/ (filename = now
    count), Sanskrit-collated. THEN files in then-2014/ are kept untouched for
    comparison. key1 = raw <k1> (machine key, accent-stripped); key2 = clean SLP1
    print form via key2_forms() (keeps `/` accent, `-`, `(...)`, `*`, `˚`)."""
    os.makedirs(NOW2026, exist_ok=True)
    files = sorted(f for f in os.listdir(THEN2014)
                   if re.match(r'^[A-Z]+-unique-key[12]-\d+\.txt$', f))
    written, skipped = [], []
    for f in files:
        m = re.match(r'^([A-Z]+)-unique-key([12])-\d+\.txt$', f)
        code, kt = m.group(1), m.group(2)
        d = CODE2DIR.get(code)
        src = src_path(d) if d else (PD_SRC if code == "PD" and os.path.exists(PD_SRC) else None)
        if not src:
            skipped.append(f"{code} key{kt} (no csl-orig source)"); continue
        keys = sorted(now_set(src, kt), key=sanskrit_key)
        out = os.path.join(NOW2026, f"{code}-unique-key{kt}-{len(keys)}.txt")
        # drop any stale now-2026/ file for this dict+keytype (count may have changed)
        for old in os.listdir(NOW2026):
            if re.match(rf'^{code}-unique-key{kt}-\d+\.txt$', old):
                os.remove(os.path.join(NOW2026, old))
        open(out, "w", encoding="utf-8", newline="\n").write("\n".join(keys) + "\n")
        written.append(os.path.basename(out))
    print(f"\nWrote {len(written)} now-2026/ snapshots:")
    for w in written:
        print("  now-2026/" + w)
    if skipped:
        print(f"\nSkipped {len(skipped)}:")
        for s in skipped:
            print("  " + s)

if __name__ == "__main__":
    import sys as _s
    if len(_s.argv) > 1 and _s.argv[1] == "now":
        write_now()
    else:
        main()
