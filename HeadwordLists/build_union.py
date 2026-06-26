"""Cross-dict UNION headword index, feminines folded under the masculine (mf(ā/ī)).

Scope decision (2026-06-26): a single merged headword list across the dictionaries,
with feminine stems folded under their masculine base. This builds it from the 2026
key1 sets in now-2026/ (the 8 dicts with a key1: AP GRA MW PWG PWK SKD VCP VEI),
records per-headword provenance (which dicts attest it), aggregates gender from each
dict's <lex> tags, and folds GENDER-CONFIRMED feminines onto their masculine base.

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

def main():
    key1files = sorted(glob.glob(os.path.join(HERE, "now-2026", "*-unique-key1-*.txt")))
    codes = [os.path.basename(f).split('-')[0] for f in key1files]
    union = collections.defaultdict(set)              # k1 -> {dict codes}
    for f, code in zip(key1files, codes):
        for l in open(f, encoding='utf-8'):
            k = l.strip()
            if k: union[k].add(code)
    print(f"union over {len(codes)} dicts {codes}: {len(union)} headwords")

    # gender per k1, aggregated across the same dicts' csl-orig <lex>.
    # Entries are multi-line records delimited by <L>; <k1> is on the header and
    # <lex> in the body, so parse per-record (not per-line).
    gender = collections.defaultdict(set)             # k1 -> set of letters
    for code in set(codes):
        d = CODE2DIR.get(code, code.lower())
        p = os.path.join(ORIG, d, d + ".txt")
        if not os.path.exists(p): continue
        txt = open(p, encoding='utf-8').read()
        for rec in txt.split('<L>'):
            mk = re.search(r'<k1>([^<]+)', rec)
            if not mk: continue
            k = mk.group(1).strip()
            if k not in union: continue
            for ml in re.finditer(r'<lex>([^<]*)</lex>', rec):
                gender[k] |= gender_letters(ml.group(1))
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
    with open(os.path.join(OUT, "fold_candidates.tsv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("fem_slp1\tfem_iast\tmasc_slp1\tmasc_iast\tending\tnote\n")
        for F, M, e in sorted(candidates):
            fh.write(f"{F}\t{iast(F)}\t{M}\t{iast(M)}\t{e}\tconfirm same lexeme (e.g. āśā≠āśa)\n")

    byn = collections.Counter(len(v) for v in union.values())
    md = ["# Cross-dict UNION headword index (2026)", "",
          f"A single merged headword list across **{len(codes)} dictionaries** "
          f"({', '.join(sorted(set(codes)))}), built from their 2026 key1 sets in "
          f"[`now-2026/`](now-2026/). Feminines are folded under the masculine (`mf(ā/ī)`) "
          f"by confirmed `<lex>` gender. Generated by [`build_union.py`](build_union.py).", "",
          f"- **Union headwords:** {len(union)}  → **{len(rows)}** after auto-folding "
          f"{len(folded)} gender-confirmed `-inī` feminines onto their `-in` base.",
          f"- **Fold candidates for editor review:** {len(candidates)} `-ā`/`-ī` feminines "
          f"(gender-confirmed but stem-sharing — may be independent lexemes).",
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
           "**confirm by hand** (gender + shape match, but may be a distinct lexeme — `āśā` "
           "\"hope\" is *not* the feminine of `āśa` \"corner\").", "",
           "**Caveats.** The fold is deliberately split: only the unambiguous **`-inī`→`-in`** "
           "(gender-confirmed) is applied automatically; `-ā`/`-ī` are left as **candidates** "
           "because a feminine `-ā` noun often shares a stem with an unrelated masculine `-a` "
           "noun. Feminines without a `<lex>` (dicts lacking gender tags) or without an attested "
           "base stay as their own headword. Homograph numbering (`<h>`) is collapsed — the "
           "union key is the bare lemma. Covers the 8 key1 dicts; the key2-only dicts "
           "(BHS/BUR/CAE/CCS/INM/MD/SCH) can be merged next via accent-stripped key2."]
    open(os.path.join(OUT, "UNION.md"), "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
    print(f"wrote union/ ({len(rows)} headwords, {len(folded)} folded)")

if __name__ == "__main__":
    main()
