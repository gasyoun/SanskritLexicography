"""Pre-screen the LOW-confidence -ā/-ī fold candidates with their MW glosses, so the
editor can reject the false folds at a glance.

For each low-confidence row of union/fold_candidates.tsv (masc base is m-only, so the
-ā/-ī is probably a *distinct* feminine noun, not a fold), pull the short MW gloss of
both the feminine and the masculine. Unrelated glosses (āśā "hope" vs āśa "reaching")
= reject the fold; near-identical glosses = a real fold the gender heuristic under-rated.

Output: union/low_candidates_screened.tsv  (fem / masc with glosses + a crude hint).
"""
import sys, re, os
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su
ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
CAND = os.path.join(HERE, "union", "fold_candidates.tsv")
OUT = os.path.join(HERE, "union", "low_candidates_screened.tsv")
STOP = set("a the of or and to in with as an for".split())

def iast(s):
    try: return su.from_slp1(s)
    except Exception: return s

def mw_glosses():
    """k1 -> short English gloss (first sense, citations stripped)."""
    txt = open(os.path.join(ORIG, "mw", "mw.txt"), encoding="utf-8").read()
    g = {}
    for rec in txt.split('<L>'):
        mk = re.search(r'<k1>([^<]+)', rec)
        if not mk: continue
        k = mk.group(1).strip()
        if k in g: continue                       # keep first record only
        i = rec.find('</lex>')
        seg = rec[i + 6:] if i >= 0 else rec
        j = seg.find('<ls>')                      # meaning ends where citations begin
        if j >= 0: seg = seg[:j]
        seg = re.sub(r'<[^>]+>', '', seg)         # drop tags (incl. <s> sanskrit)
        seg = re.sub(r'^\s*\([^)]*\)\s*,?\s*', '', seg)   # drop leading (√ …) etymology
        seg = seg.replace('¦', '').replace('&c.', '')
        seg = re.sub(r'\s+', ' ', seg).strip(' ,;()')
        g[k] = seg[:90]
    return g

def words(s):
    return set(w for w in re.findall(r"[a-zāīūṛṝḷ ṅñṭḍṇśṣ]+", s.lower()) for w in [w.strip()] if len(w) > 2 and w not in STOP)

def main():
    g = mw_glosses()
    rows = []
    for ln in open(CAND, encoding="utf-8"):
        p = ln.rstrip("\n").split("\t")
        if p[0] != "low": continue                # screen the low-confidence ones
        _, nshared, F, Fi, M, Mi, end, mg = p
        gf, gm = g.get(F, "(not in MW)"), g.get(M, "(not in MW)")
        # crude relatedness hint: shared content words between the two glosses
        shared = words(gf) & words(gm) if "(not in MW)" not in (gf, gm) else set()
        hint = "MAYBE-related" if shared else "likely-distinct"
        rows.append((hint, nshared, F, Fi, gf, M, Mi, gm, end))
    rows.sort(key=lambda r: (r[0] != "MAYBE-related", -int(r[1])))   # related ones first
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("hint\tn_shared_dicts\tfem_slp1\tfem_iast\tfem_gloss_MW\tmasc_slp1\tmasc_iast\tmasc_gloss_MW\tending\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    nmaybe = sum(1 for r in rows if r[0] == "MAYBE-related")
    print(f"screened {len(rows)} low candidates -> {OUT}")
    print(f"  {nmaybe} share a gloss word (MAYBE a real fold), {len(rows) - nmaybe} likely-distinct (reject)")

if __name__ == "__main__":
    main()
