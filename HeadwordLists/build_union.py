"""Cross-dict UNION headword index, feminines folded under the masculine (mf(ā/ī)).

Scope decision (2026-06-26): a single merged headword list across the dictionaries,
with feminine stems folded under their masculine base. Built from the current csl-orig
<k1> of all 15 dicts that have one (PD has none), records per-headword provenance
(which dicts attest it), aggregates gender from each dict's <lex> tags, and folds
GENDER-CONFIRMED feminines onto their masculine base.

Fold rule (conservative, gender-driven — not word-shape guessing):
  fold feminine F under masculine M iff
    * F is feminine-only  (aggregated <lex> has f and not m), AND
    * M = morphological base of F is in the union and masculine-capable (<lex> has m), via
        -inī → -in   (unambiguous feminine of an -in stem)
        -ā   → -a    (productive feminine of an a-stem)
        -ī   → -in   (candidate)
  The masculine row gets an `mf(ā/ī)` marker; the feminine row is removed from the main
  list and recorded in folded_feminines.tsv. Feminines whose base isn't attested, or
  whose gender isn't confirmed, stay as their own headword (not force-folded).

Outputs to union/: union_headwords.tsv (the list), folded_feminines.tsv (audit), UNION.md.
"""
import sys, re, os, glob, collections
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su
ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
OUT = os.path.join(HERE, "union")
CODE2DIR = {"PWK": "pw"}

def iast(s):
    try: return su.from_slp1(s)
    except Exception: return s

def gender_letters(lexstr):
    """<lex> string -> subset of {m,f,n} (ind./other -> empty)."""
    s = lexstr.lower()
    if 'ind' in s: return frozenset()
    return frozenset(c for c in s if c in 'mfn')

# All HeadwordLists dicts that have a csl-orig source (PD has none). key1 is read
# straight from csl-orig <k1>, so the union covers every dict — not just the 8 with a
# 2014 key1 snapshot. Provenance uses the HeadwordLists code (PWK, not pw).
DICTS = ["AP", "BHS", "BUR", "CAE", "CCS", "GRA", "INM", "MD", "MW",
         "PWG", "PWK", "SCH", "SKD", "VCP", "VEI"]

def main():
    union = collections.defaultdict(set)              # k1 -> {dict codes}
    gender = collections.defaultdict(set)             # k1 -> set of letters {m,f,n}
    # Entries are multi-line records delimited by <L>; <k1> is on the header and
    # <lex> in the body, so parse per-record (not per-line).
    for code in DICTS:
        d = CODE2DIR.get(code, code.lower())
        p = os.path.join(ORIG, d, d + ".txt")
        if not os.path.exists(p):
            print(f"  skip {code}: no csl-orig source"); continue
        for rec in open(p, encoding='utf-8').read().split('<L>'):
            mk = re.search(r'<k1>([^<]+)', rec)
            if not mk: continue
            k = mk.group(1).strip()
            if not k: continue
            union[k].add(code)
            for ml in re.finditer(r'<lex>([^<]*)</lex>', rec):
                gender[k] |= gender_letters(ml.group(1))
    codes = DICTS
    print(f"union over {len(DICTS)} dicts: {len(union)} headwords")
    fem_only = lambda k: ('f' in gender.get(k, ())) and ('m' not in gender.get(k, ()))
    masc_cap = lambda k: 'm' in gender.get(k, ())

    # Fold gender-confirmed feminines. Only the morphologically-unambiguous -inī→-in
    # is auto-folded (an -inī is reliably the feminine of an -in: vyāpinī←vyāpin).
    # The -ā→-a / -ī→-in cases share a stem with possibly-unrelated lexemes (āśā "hope"
    # vs āśa "corner"), so they go to a candidates file for the editor to confirm — NOT
    # auto-folded.
    folded = {}                                # fem -> (masc, ending)  [auto: -inī only]
    fem_mark = collections.defaultdict(set)    # masc -> {endings}
    candidates = []                            # (fem, masc, ending) for editor review
    for F in list(union):
        if not fem_only(F): continue
        if F.endswith('inI') and F[:-1] in union and masc_cap(F[:-1]):
            folded[F] = (F[:-1], 'ī'); fem_mark[F[:-1]].add('ī'); continue
        if F.endswith('A') and (F[:-1] + 'a') in union and masc_cap(F[:-1] + 'a'):
            candidates.append((F, F[:-1] + 'a', 'ā'))
        elif F.endswith('I') and (F[:-1] + 'in') in union and masc_cap(F[:-1] + 'in'):
            candidates.append((F, F[:-1] + 'in', 'ī'))
    print(f"auto-folded (-inī→-in, gender-confirmed): {len(folded)}; "
          f"fold candidates for review (-ā/-ī): {len(candidates)}")

    os.makedirs(OUT, exist_ok=True)
    # main list: every union headword except the folded feminines; masc carries mf marker
    rows = []
    for k in sorted(union, key=lambda x: (len(x), x)):
        if k in folded: continue
        g = ''.join(sorted(gender.get(k, ()))) or '-'
        mf = 'mf(%s)' % '/'.join(sorted(fem_mark[k])) if k in fem_mark else ''
        rows.append((k, iast(k), str(len(union[k])), ' '.join(sorted(union[k])), g, mf))
    with open(os.path.join(OUT, "union_headwords.tsv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("slp1\tiast\tn_dicts\tdicts\tgender\tfem_fold\n")
        for r in rows: fh.write("\t".join(r) + "\n")
    with open(os.path.join(OUT, "folded_feminines.tsv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("fem_slp1\tfem_iast\tmasc_slp1\tmasc_iast\tending\n")
        for F, (M, e) in sorted(folded.items()):
            fh.write(f"{F}\t{iast(F)}\t{M}\t{iast(M)}\t{e}\n")
    # Rank the -ā/-ī fold candidates so the editor reviews the likely-true ones first:
    #   confidence HIGH  = the masculine base is itself mfn (gender has 'f') → it is an
    #                      adjective/n. whose feminine is exactly this -ā/-ī (fold likely right).
    #   confidence LOW   = masc is m-only → the -ā is probably a distinct feminine noun
    #                      sharing the stem (āśā "hope" vs āśa "corner") → likely NOT a fold.
    # secondary key: number of dicts attesting BOTH forms (more shared = more likely related).
    ranked = []
    for F, M, e in candidates:
        conf = "high" if 'f' in gender.get(M, ()) else "low"
        nshared = len(union[F] & union[M])
        ranked.append((0 if conf == "high" else 1, -nshared, F, conf, nshared, M, e))
    ranked.sort()
    nhigh = sum(1 for r in ranked if r[3] == "high")
    with open(os.path.join(OUT, "fold_candidates.tsv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("confidence\tn_shared_dicts\tfem_slp1\tfem_iast\tmasc_slp1\tmasc_iast\tending\tmasc_gender\n")
        for _, _, F, conf, nshared, M, e in ranked:
            fh.write(f"{conf}\t{nshared}\t{F}\t{iast(F)}\t{M}\t{iast(M)}\t{e}\t{''.join(sorted(gender.get(M, ()))) or '-'}\n")
    print(f"fold candidates ranked: {nhigh} high-confidence (masc is mfn), {len(ranked) - nhigh} low")

    byn = collections.Counter(len(v) for v in union.values())
    md = ["# Cross-dict UNION headword index (2026)", "",
          f"A single merged headword list across **{len(codes)} dictionaries** "
          f"({', '.join(sorted(set(codes)))}), built from their current csl-orig `<k1>`. "
          f"Feminines are folded under the masculine (`mf(ā/ī)`) "
          f"by confirmed `<lex>` gender. Generated by [`build_union.py`](build_union.py).", "",
          f"- **Union headwords:** {len(union)}  → **{len(rows)}** after auto-folding "
          f"{len(folded)} gender-confirmed `-inī` feminines onto their `-in` base.",
          f"- **Fold candidates for editor review:** {len(candidates)} `-ā`/`-ī` feminines, "
          f"**ranked** — {nhigh} high-confidence (masculine is `mfn`, so the feminine is its) "
          f"vs {len(candidates) - nhigh} low (masc `m`-only — likely a distinct lexeme).",
          f"- **Provenance:** in ≥2 dicts {sum(1 for v in union.values() if len(v) >= 2)}, "
          f"singletons {sum(1 for v in union.values() if len(v) == 1)}.", "",
          "| in N dicts | headwords |", "|--:|--:|"]
    for n in sorted(byn): md.append(f"| {n} | {byn[n]} |")
    md += ["", "## Files", "",
           "- [`union/union_headwords.tsv`](union/union_headwords.tsv) — the merged list "
           "(`slp1, iast, n_dicts, dicts, gender, fem_fold`); folded feminines removed, their "
           "masculine carries the `mf(ā/ī)` marker.",
           "- [`union/folded_feminines.tsv`](union/folded_feminines.tsv) — audit of every "
           "auto-fold (`-inī`→`-in`).",
           "- [`union/fold_candidates.tsv`](union/fold_candidates.tsv) — `-ā`/`-ī` feminines to "
           "**confirm by hand**, ranked `confidence` high→low with `n_shared_dicts` and "
           "`masc_gender`. **High** = masc is `mfn` (the feminine is genuinely its); **low** = "
           "masc `m`-only, likely a distinct lexeme (`āśā` \"hope\" ≠ feminine of `āśa` "
           "\"corner\"). Review high first.",
           "- [`union/low_candidates_screened.tsv`](union/low_candidates_screened.tsv) — the "
           "**426 low** candidates pre-screened with their MW glosses (via "
           "[`screen_candidates.py`](screen_candidates.py)): **419 likely-distinct** (reject — "
           "`ārā` awl vs `āra` brass) and **7 MAYBE-related** to eyeball (`tālikā`/`tālika` "
           "same gloss). Cuts the low-set review from 426 to ~7.", "",
           "**Caveats.** The fold is deliberately split: only the unambiguous **`-inī`→`-in`** "
           "(gender-confirmed) is applied automatically; `-ā`/`-ī` are left as **candidates** "
           "because a feminine `-ā` noun often shares a stem with an unrelated masculine `-a` "
           "noun. Feminines without a `<lex>` (dicts lacking gender tags) or without an attested "
           "base stay as their own headword. Homograph numbering (`<h>`) is collapsed — the "
           "union key is the bare lemma. Covers all 15 dicts with a csl-orig `<k1>` (PD has "
           "none); gender is richest in MW/AP and sparse elsewhere (BUR has no `<lex>`), so "
           "folds are MW/AP-driven."]
    open(os.path.join(OUT, "UNION.md"), "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
    print(f"wrote union/ ({len(rows)} headwords, {len(folded)} folded)")

if __name__ == "__main__":
    main()
