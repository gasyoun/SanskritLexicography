"""Pre-resolve the §7 accent-position disagreements (Pujol vs Cologne) for adjudication.

For every lemma where Pujol's udātta sits on a different vowel than Cologne's (no
accent-variant matches — the ~3% from accent_compare.py), render BOTH sides as accented
IAST (acute on the marked vowel) so the editor can pick the right one at a glance. Where
the conflict is with the Rigveda (GRA), the Cologne/GRA reading is normally canonical.

Output: Catalan-Pujol/accent_disagreements.tsv (lemma, Pujol form, GRA form, MW form,
recommendation).
"""
import sys, re, os, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su
ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
CAT = os.path.join(HERE, "Catalan-Pujol", "61267-Sanskrit-Catalan-Words-List.txt")
OUT = os.path.join(HERE, "Catalan-Pujol", "accent_disagreements.tsv")
SLP_VOWELS = "aAiIuUfFxXeEoO"
ACUTE, GRAVE = '́', '̀'

def ascii_clean(k):
    k = unicodedata.normalize('NFD', k)
    return ''.join(c for c in k if ord(c) < 128 and not unicodedata.combining(c))

def accented_iast(bare, ords):
    """bare SLP1 -> IAST with an acute on each vowel ordinal in `ords` (1-based)."""
    out, vc = [], 0
    for c in bare:
        ic = su.from_slp1(c) if c in SLP_VOWELS or c.isalpha() else c
        if c in SLP_VOWELS:
            vc += 1
            out.append(ic + (ACUTE if vc in ords else ''))
        else:
            out.append(ic)
    return unicodedata.normalize('NFC', ''.join(out))

def pujol_accents():
    """bare key -> set of accent-ordinal frozensets (accented variants)."""
    out = collections.defaultdict(set)
    for line in open(CAT, encoding='utf-8-sig'):
        hw = line.rstrip('\n')
        w = re.sub(r'\([^)]*\)', '', hw).strip().strip(' ,;').replace('√', '').replace('˚', '')
        w = re.sub(r'\d+$', '', w).strip()
        w = unicodedata.normalize('NFC', w).replace('-', '')
        nfd = unicodedata.normalize('NFD', w)
        base, acc = [], []
        for ch in nfd:
            if unicodedata.combining(ch):
                if ch in (ACUTE, GRAVE) and base: acc.append(len(base) - 1)
                continue
            base.append(ch)
        try:
            key = ascii_clean(su.strip_slp1_accents(su.to_slp1(''.join(base))))
        except Exception:
            continue
        if not key: continue
        ords = set()
        for i in acc:
            try: ords.add(sum(1 for c in su.to_slp1(''.join(base[:i + 1])) if c in SLP_VOWELS))
            except Exception: pass
        out[key].add(frozenset(ords))
    return out

def cologne_accents(dictcode):
    out = collections.defaultdict(set)
    p = os.path.join(ORIG, dictcode, dictcode + ".txt")
    if not os.path.exists(p): return out
    for line in open(p, encoding='utf-8'):
        m = re.search(r'<k2>([^<]+)', line)
        if not m: continue
        k2 = m.group(1).strip()
        ords, vc = set(), 0
        for ch in k2:
            if ch in SLP_VOWELS: vc += 1
            elif ch == '/': ords.add(vc)
        bare = ascii_clean(su.strip_slp1_accents(k2).replace('-', '').replace('°', '').replace('+', ''))
        if bare: out[bare].add(frozenset(ords))
    return out

def has_acc(v): return any(s for s in v)
def best(v):    return max((s for s in v if s), key=len, default=frozenset())

def main():
    puj = pujol_accents()
    gra, mw = cologne_accents("gra"), cologne_accents("mw")
    rows = []
    for key in sorted(puj):
        if not has_acc(puj[key]): continue
        for col, name in ((gra, "GRA"), (mw, "MW")):
            if key in col and has_acc(col[key]) and not (puj[key] & col[key]):
                po, co = best(puj[key]), best(col[key])
                rows.append((name, key, su.from_slp1(key),
                             accented_iast(key, po), sorted(po),
                             accented_iast(key, co), sorted(co)))
    # de-dup: one row per (key) preferring GRA (RV, canonical)
    seen, final = set(), []
    for r in sorted(rows, key=lambda r: (r[1], r[0] != "GRA")):
        if r[1] in seen: continue
        seen.add(r[1]); final.append(r)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("vs\tlemma_slp1\tlemma_iast\tpujol_accented\tpujol_vowel\tcologne_accented\tcologne_vowel\trecommend\n")
        for name, key, ia, pf, po, cf, co in final:
            rec = "Cologne (RV)" if name == "GRA" else "Cologne (MW)"
            fh.write(f"{name}\t{key}\t{ia}\t{pf}\t{'/'.join(map(str, po))}\t{cf}\t{'/'.join(map(str, co))}\t{rec}\n")
    print(f"accent disagreements (Pujol vs Cologne): {len(final)} lemmas")
    print(f"  vs GRA: {sum(1 for r in final if r[0]=='GRA')} | vs MW only: {sum(1 for r in final if r[0]=='MW')}")
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
