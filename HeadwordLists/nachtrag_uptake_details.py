"""Uptake-evolution + corroboration details for the Nachtraege-vs-MW study (MG batch 15-09-2026).

From csl-orig/v02 (read-only) and the adjudication TSV on master:
  1. publication-year-annotated source table (the timeline argument),
  2. MW72 (1872) -> MW99 (1899) per-layer uptake + the dropped-between-editions list,
  3. DCS-band-ranked top-10 samples for every big list,
  4. BHS/Edgerton (1953) vs MW99: overlap + annexure-vs-main enrichment (the
     same metric shape as the ~7.8x PW finding) + BHS corroboration of candidates,
  5. sup_7 homonym/sense-extension census (explicit <hom> tags; headwords already
     present in the PW main body = extensions, not new headwords),
  6. machine-usable proposal list from the corroborated adds.

Outputs: mw72_uptake_evolution.tsv, nachtrag_dcs_samples.tsv,
MW-NACHTRAG-PROPOSALS-15-09-2026.tsv
"""
import sys, os, io, re, json, collections
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
DCS_JSON = os.environ.get("DCS_LEMMA_JSON", r"C:/Users/user/Documents/GitHub/VisualDCS/dcs_lemma_summary.json")
HERE = os.path.dirname(os.path.abspath(__file__))
ADJ = os.path.join(HERE, "MW-NACHTRAG-ADJUDICATION-14-09-2026.tsv")

L = re.compile(r"^<L>"); K1 = re.compile(r"<k1>([^<]+)"); K2 = re.compile(r"<k2>([^<]+)")
SUP = re.compile(r'<info n="sup_(\d)"/>'); MWSUP = '<info n="sup"/>'
HOM = re.compile(r"<hom>(\d+)\.</hom>")

def entries(path):
    cur = None; buf = []
    def flush():
        if cur is None: return
        g = K1.search(cur); k1 = g.group(1).strip() if g else ""
        g = K2.search(cur); k2 = g.group(1).strip() if g else ""
        yield k1, k2, "".join(buf)
    for line in io.open(path, encoding='utf-8'):
        if L.match(line):
            for t in flush(): yield t
            cur = line; buf = [line]
        else:
            buf.append(line)
    for t in flush(): yield t

mw99 = set(); annex99 = set()
for k1, k2, body in entries(os.path.join(ORIG, "mw", "mw.txt")):
    if k1:
        mw99.add(k1)
        if MWSUP in body: annex99.add(k1)
    if k2: mw99.add(k2)
main99 = mw99 - annex99
mw72 = set()
for k1, k2, body in entries(os.path.join(ORIG, "mw72", "mw72.txt")):
    if k1: mw72.add(k1)
    if k2: mw72.add(k2)
bhs = set()
for k1, k2, body in entries(os.path.join(ORIG, "bhs", "bhs.txt")):
    if k1: bhs.add(k1)
    if k2: bhs.add(k2)

layer_hw = collections.defaultdict(list); layer_hom = collections.Counter()
pw_main_k1 = set(); sup7 = []; sup_layers = collections.Counter()
for k1, k2, body in entries(os.path.join(ORIG, "pw", "pw.txt")):
    m = SUP.search(body)
    if not m:
        if k1: pw_main_k1.add(k1)
        continue
    layer = int(m.group(1)); sup_layers[layer] += 1
    hw = k2.lstrip("*") if k2.startswith("*") else k1
    if not hw: continue
    layer_hw[layer].append(hw)
    if HOM.search(body): layer_hom[layer] += 1
    if layer == 7: sup7.append(hw)
sup7u = sorted(set(sup7))

# DCS bands (1..5; see bandingRule in the json)
dcs = json.load(io.open(DCS_JSON, encoding='utf-8'))
lemmas = dcs.get("lemmas", {})
print(f"DCS: lemmaCount={dcs.get('lemmaCount')} bandingRule={dcs.get('bandingRule')!r} release={dcs.get('corpusRelease')}")
def band(h): return (lemmas.get(h) or {}).get("freqBand", 0)

def top10(pool, title, out_rows):
    ranked = sorted(set(pool), key=lambda h: (-band(h), h))[:10]
    print(f"\n## top-10 by DCS band — {title} (of {len(set(pool))})")
    for i, h in enumerate(ranked):
        print(f"{i+1}. {h} (DCS band {band(h)})")
        out_rows.append((title, i + 1, h, band(h), len(set(pool))))
    return ranked

samples = []
# --- 1 timeline
print("\n## sources with publication years (timeline argument)")
for row in [
    ("PW Böhtlingk-Roth, great Petersburg dictionary", "1855-1875", "vol 7 (1872-75) carries the Nachträge; sup_1..sup_7 tags in Cologne pw.txt"),
    ("Nachträge und Verbesserungen (standalone digitization)", "—", "Cologne pwkvn.txt, 24,976 entries"),
    ("kürzere Fassung (MG's 'PWK')", "1879-1889", "Cologne code pw per headers (see CONTRADICTIONS §18)"),
    ("Monier-Williams MW72", "1872", "51,162 unique k1∪k2; no annexure"),
    ("Monier-Williams MW99", "1899", "344,684 unique k1∪k2; 6,067-entry annexure (<info n=\"sup\"/>)"),
    ("Edgerton, BHS Dictionary", "1953", "17,839 entries; Cologne bhs.txt"),
    ("Mahāvyutpatti (cited by the Nachträge)", "ed. 1849", "MAHĀVY 245/844 = kāritra"),
]:
    print(f"- {row[0]} — {row[1]} — {row[2]}")

# --- 2 MW72 -> MW99 evolution
print("\n## MW72 -> MW99 uptake per layer (new-in-MW99 split annexure/main)")
evo = []
for layer in sorted(layer_hw):
    hw = sorted(set(layer_hw[layer]))
    in72 = sum(1 for h in hw if h in mw72)
    in99 = sum(1 for h in hw if h in mw99)
    new = [h for h in hw if h not in mw72 and h in mw99]
    na = sum(1 for h in new if h in annex99); nm = len(new) - na
    skip = [h for h in hw if h not in mw72 and h not in mw99]
    evo.append((layer, len(hw), in72, in99, len(new), na, nm, len(skip)))
    print(f"sup_{layer} | n={len(hw)} | MW72 {in72} ({100*in72/len(hw):.0f}%) | MW99 {in99} ({100*in99/len(hw):.0f}%) | new {len(new)} = {na} annexure + {nm} main | skipped-both {len(skip)}")
with io.open(os.path.join(HERE, "mw72_uptake_evolution.tsv"), "w", encoding='utf-8', newline='') as f:
    f.write("layer\tn_unique\tin_mw72\tin_mw99\tnew_in_mw99\tnew_via_annexure\tnew_via_main\tskipped_by_both\n")
    for r in evo: f.write("\t".join(map(str, r)) + "\n")

dropped = sorted({h for h in sup7 if h in mw72 and h not in mw99})
print(f"\n## dropped between MW72 and MW99 ({len(dropped)}): " + ", ".join(dropped))

# --- 3 samples from the adjudication
rows = []
with io.open(ADJ, encoding='utf-8') as f:
    hdr = f.readline().rstrip("\n").split("\t")
    for line in f: rows.append(line.rstrip("\n").split("\t"))
ix = {c: hdr.index(c) for c in ("hw_slp1", "verdict", "corr_n", "mahavy", "corr_dicts")}
confirmed = [r[ix["hw_slp1"]] for r in rows if r[ix["verdict"]] == "confirmed-missing"]
corr2 = [r[ix["hw_slp1"]] for r in rows if r[ix["verdict"]] == "confirmed-missing" and int(r[ix["corr_n"]]) >= 2]
mah = [r[ix["hw_slp1"]] for r in rows if r[ix["verdict"]] == "confirmed-missing" and r[ix["mahavy"]] not in ("", "0")]
never = [h for h in sup7u if h not in mw72 and h not in mw99]
print(f"\n## adjudication: {len(rows)} rows; confirmed-missing {len(confirmed)}; of them >=2 dicts {len(corr2)}; citing MAHĀVY {len(mah)}")
top10(confirmed, "confirmed-missing from MW (1,751)", samples)
top10(corr2, "confirmed-missing corroborated >=2 dicts", samples)
top10(mah, "confirmed-missing citing MAHĀVY", samples)
top10(never, "never-seen (absent MW72 & MW99)", samples)

# --- 4 BHS / Edgerton
b_annex = bhs & annex99; b_main = bhs & main99
enr = (len(b_annex) / len(annex99)) / (len(b_main) / len(main99)) if b_main else float("inf")
print(f"\n## BHS (Edgerton 1953) vs MW99 (1899)")
print(f"BHS unique keys={len(bhs)}; also in MW99={len(bhs & mw99)} ({100*len(bhs & mw99)/len(bhs):.0f}% of BHS)")
print(f"BHS in MW99 annexure={len(b_annex)}/{len(annex99)} ({100*len(b_annex)/len(annex99):.1f}%); in MW99 main={len(b_main)}/{len(main99)} ({100*len(b_main)/len(main99):.1f}%)")
print(f"BHS enrichment of the MW annexure = {enr:.2f}x  (compare: PW/Nachträge 7.84x)")
bcorr = [h for h in confirmed if h in bhs]
print(f"confirmed-missing also attested in BHS/Edgerton: {len(bcorr)}")
top10(bcorr, "confirmed-missing also in BHS/Edgerton", samples)

# --- 5 homonym extensions
dup = [h for h in sup7 if h in pw_main_k1]; new = [h for h in sup7 if h not in pw_main_k1]
print(f"\n## sup_7 homonym/sense extensions")
print("explicit <hom>N.</hom> tags per layer: " + ", ".join(f"sup_{k}={v}" for k, v in sorted(layer_hom.items())))
print(f"sup_7 entries={len(sup7)}; unique={len(sup7u)}; headword already in PW main body (extension)={len(dup)} ({100*len(dup)/len(sup7):.0f}%); new headword={len(new)}")
top10(dup, "sup_7 extension headwords (already in PW main body)", samples)

with io.open(os.path.join(HERE, "nachtrag_dcs_samples.tsv"), "w", encoding='utf-8', newline='') as f:
    f.write("pool\trandom_rank\thw_slp1\tdcs_band\tpool_size\n")
    for s in samples: f.write("\t".join(map(str, s)) + "\n")

# --- 6 machine-usable proposal list
PROP = os.path.join(HERE, "MW-NACHTRAG-PROPOSALS-15-09-2026.tsv")
with io.open(PROP, "w", encoding='utf-8', newline='') as f:
    f.write("hw_slp1\tiast\tpw_L\tpw_pc\tcorr_n\tcorr_dicts\tmahavy_refs\tdcs_band\tproposed_action\tevidence\tgloss\n")
    n = 0
    for r in rows:
        if r[ix["verdict"]] != "confirmed-missing": continue
        if int(r[ix["corr_n"]]) < 2: continue
        c = {k: hdr.index(k) for k in ("pwk_L", "pwk_pc", "iast", "mahavy_refs", "evidence")}
        hw = r[ix["hw_slp1"]]
        f.write("\t".join([
            hw, r[c["iast"]], r[c["pwk_L"]], r[c["pwk_pc"]], r[ix["corr_n"]], r[ix["corr_dicts"]],
            r[c["mahavy_refs"]], str(band(hw)), "add-entry", r[c["evidence"]], "",
        ]) + "\n")
        n += 1
print(f"\nWROTE {PROP} ({n} proposal rows: confirmed-missing + corroborated >=2 dicts)")
print("WROTE mw72_uptake_evolution.tsv, nachtrag_dcs_samples.tsv")