"""Cross-tag the priority coverage additions (item B) with external attestation.

A coverage addition (DCS-attested, in no CDSL dict) is the SAFEST to add to a printed
list if an INDEPENDENT external wordlist also has it — that is corpus + a second
lexicographic source agreeing the word is real. This tags the priority band (≥3,
genuine nominal) of union/coverage_additions.tsv with whether each lemma is also in the
Catalan-Pujol and/or Huet/INRIA wordlists, and ranks by that corroboration.

Reuses huet_coverage for the Huet VH→SLP1 normaliser + the shared key; replicates the
small Catalan normaliser. Output: union/coverage_additions_crosstagged.tsv + summary.
"""
import sys, re, os, unicodedata
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su
import huet_coverage as huet              # has __main__ guard; gives norm_key, norm_huet
ADD = os.path.join(HERE, "union", "coverage_additions.tsv")
CAT = os.path.join(HERE, "Catalan-Pujol", "61267-Sanskrit-Catalan-Words-List.txt")
HUETFILE = huet.HUET
OUT = os.path.join(HERE, "union", "coverage_additions_crosstagged.tsv")

def norm_cat(w):
    w = re.sub(r'\([^)]*\)', '', w).strip().strip(' ,;').replace('√', '').replace('˚', '')
    w = re.sub(r'\d+$', '', w).strip()
    w = unicodedata.normalize('NFC', w).replace('-', '')
    try: slp = su.to_slp1(w)
    except Exception: return ''
    return huet.norm_key(slp) if slp else ''

def main():
    catalan = set()
    for l in open(CAT, encoding='utf-8-sig'):
        k = norm_cat(l.rstrip('\n'))
        if k: catalan.add(k)
    huetset = set()
    for l in open(HUETFILE, encoding='utf-8-sig'):
        k = huet.norm_huet(l.rstrip('\n'))
        if k: huetset.add(k)
    print(f"Catalan keys: {len(catalan)} | Huet keys: {len(huetset)}")

    # priority additions: genuine nominal, band >= 3
    pri = []
    for ln in open(ADD, encoding='utf-8'):
        b, kind, slp1, ia = ln.rstrip('\n').split('\t') if ln.count('\t') == 3 else (None,) * 4
        if b is None or b == 'dcs_band': continue
        if kind != 'nominal' or int(b) < 3: continue
        pri.append((int(b), slp1, ia))

    rows = []
    for band, slp1, ia in pri:
        inc = slp1 in catalan
        inh = slp1 in huetset
        n = inc + inh
        safety = "DCS+Cat+Huet" if n == 2 else ("DCS+Cat" if inc else ("DCS+Huet" if inh else "DCS-only"))
        rows.append((-n, -band, safety, band, slp1, ia, "Y" if inc else "", "Y" if inh else ""))
    rows.sort()
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("safety\tdcs_band\tslp1\tiast\tin_catalan\tin_huet\n")
        for _, _, safety, band, slp1, ia, c, h in rows:
            fh.write(f"{safety}\t{band}\t{slp1}\t{ia}\t{c}\t{h}\n")

    both = sum(1 for r in rows if r[2] == "DCS+Cat+Huet")
    cat = sum(1 for r in rows if r[2] == "DCS+Cat")
    hue = sum(1 for r in rows if r[2] == "DCS+Huet")
    only = sum(1 for r in rows if r[2] == "DCS-only")
    print(f"priority additions (band ≥3, nominal): {len(rows)}")
    print(f"  DCS + Catalan + Huet (safest): {both}")
    print(f"  DCS + Catalan only          : {cat}")
    print(f"  DCS + Huet only             : {hue}")
    print(f"  DCS only (no external)      : {only}")
    print(f"  → externally corroborated   : {both + cat + hue}  ({100*(both+cat+hue)/max(1,len(rows)):.0f}%)")
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
