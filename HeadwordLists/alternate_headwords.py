"""Generate the item-F (alternate & feminine headword) candidate lists for the editor.

For a dictionary (default MW), from its current key1 set in now-2026/, emit to
f_candidates/:
  <D>_fem_masc.tsv    feminine stem <-> its masculine base, both headworded (-ā↔-a, -inī↔-in, -ī↔-in)
  <D>_orphan_fem.tsv  feminine stems (-ā/-ī/-inī) with NO masculine base headworded
  <D>_variants.tsv    candidate variant-spelling pairs both headworded (b~v, ś~ṣ, geminate~single)
  <D>_multi_k2.tsv    entries whose <k2> is a comma-list = alternate forms of ONE entry (from csl-orig)
and a summary block to stdout. Each row carries SLP1 + IAST. These are *candidates*
— some pairs are coincidental homographs; the editor rules per item F of
PRINT_READINESS.md. The policy (headword separately / fold mf(ā/ī) / merge+xref) is human.

Usage:  python alternate_headwords.py [DICT]      (DICT default MW)
"""
import sys, re, os
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su
ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
OUT = os.path.join(HERE, "f_candidates")
CODE2DIR = {"PWK": "pw"}
CONS = set("kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh")   # SLP1 consonants (for geminate detection)

def iast(slp):
    try: return su.from_slp1(slp)
    except Exception: return slp

def now_key1(code):
    import glob
    g = glob.glob(os.path.join(HERE, "now-2026", f"{code}-unique-key1-*.txt"))
    if not g: return None
    return set(l.strip() for l in open(g[0], encoding="utf-8") if l.strip())

def variant_pairs(ks):
    """unordered (a,b) headword pairs differing by a classic orthographic variant."""
    pairs = set()
    for k in ks:
        cands = set()
        if 'b' in k: cands.add(k.replace('b', 'v'))      # b~v
        if 'v' in k: cands.add(k.replace('v', 'b'))
        if 'S' in k: cands.add(k.replace('S', 'z'))      # ś~ṣ
        if 'z' in k: cands.add(k.replace('z', 'S'))
        for c in CONS:                                    # geminate ~ single (CC->C)
            if c * 2 in k: cands.add(k.replace(c * 2, c))
        for c2 in cands:
            if c2 != k and c2 in ks:
                pairs.add(tuple(sorted((k, c2))))
    return pairs

def multi_k2_groups(code):
    d = CODE2DIR.get(code, code.lower())
    p = os.path.join(ORIG, d, d + ".txt")
    groups = []
    if not os.path.exists(p): return groups
    for m in re.finditer(r'<k2>([^<¦\n]*)', open(p, encoding="utf-8").read()):
        v = m.group(1).replace('{#', '').replace('#}', '')
        forms = [x.strip() for x in v.split(',') if x.strip() and '“' not in x and len(x) <= 80]
        if len(forms) > 1:
            groups.append(forms)
    return groups

def tsv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")

def main(code):
    ks = now_key1(code)
    if ks is None:
        print(f"no now-2026 key1 for {code}"); return
    os.makedirs(OUT, exist_ok=True)
    fem_masc, orphan = [], []
    for k in ks:
        base = None
        if k.endswith('inI') and k[:-1] in ks: base = k[:-1]            # -inī -> -in
        elif k.endswith('I') and k[:-1] + 'in' in ks: base = k[:-1] + 'in'  # -ī -> -in
        elif k.endswith('A') and k[:-1] + 'a' in ks: base = k[:-1] + 'a'    # -ā -> -a
        if base:
            fem_masc.append((k, iast(k), base, iast(base)))
        elif k[-1] in 'AI' or k.endswith('inI'):
            orphan.append((k, iast(k)))
    vp = sorted(variant_pairs(ks))
    groups = multi_k2_groups(code)
    tsv(os.path.join(OUT, f"{code}_fem_masc.tsv"),
        ["fem_slp1", "fem_iast", "masc_slp1", "masc_iast"], sorted(fem_masc))
    tsv(os.path.join(OUT, f"{code}_orphan_fem.tsv"),
        ["slp1", "iast"], sorted(orphan))
    tsv(os.path.join(OUT, f"{code}_variants.tsv"),
        ["a_slp1", "a_iast", "b_slp1", "b_iast"],
        [(a, iast(a), b, iast(b)) for a, b in vp])
    tsv(os.path.join(OUT, f"{code}_multi_k2.tsv"),
        ["forms_slp1", "forms_iast"],
        [(" , ".join(g), " , ".join(iast(x) for x in g)) for g in groups])
    print(f"=== {code} (key1 {len(ks)}) — item-F candidates -> f_candidates/ ===")
    print(f"  fem<->masc pairs      : {len(fem_masc)}  ({code}_fem_masc.tsv)")
    print(f"  orphan feminines      : {len(orphan)}  ({code}_orphan_fem.tsv)")
    print(f"  variant-spelling pairs: {len(vp)}  ({code}_variants.tsv)")
    print(f"  multi-<k2> alt groups : {len(groups)}  ({code}_multi_k2.tsv)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "MW")
