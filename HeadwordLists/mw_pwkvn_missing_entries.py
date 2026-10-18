"""MW ↔ pwkvn (Böhtlingk Nachträge) headword join: entries MW skipped — pilot.

csl-corrections issue #119, Q37 thread (Andhrabharati comment 01-05-2026)
postulates that MW (1899) skipped intended entries — e.g. *kāritra*, which the
letzte Nachträge of pwk7 (p. 331-d, the Mahāvyutpatti supplement) has and MW
lacks. This pilot quantifies the postulate in BOTH directions against the
Cologne digitizations (csl-orig/v02, read-only):

  A. evidence that MW's Supplemental-Word annexure (<info n="sup"/>) draws on
     the Nachträge: |pwkvn ∩ MWsup| vs |pwkvn ∩ MWmain| (enrichment ratio);
  B. skipped-entry candidates: pwkvn <k1> absent from MW <k1>∪<k2> (verbatim
     tier + a marker-stripped tier), each with its pwkvn page-column, whether
     the Mahāvyutpatti supplement register (MAHĀVY refs) is cited, and whether
     the great PW (pw) / kürzere Fassung (pwg) also attests it.

Recipe = HeadwordLists/headword_diff.py: verbatim <k1>/<k2> field values,
sorted unique; no transliteration change. Deterministic; no writes to csl-orig.

Output: mw_pwkvn_missing_entries.tsv (side B) + mw_pwkvn_sup_overlap.tsv
(side A) + stdout summary. Named check: 'kAritra' must surface in B and be
absent from MW — the pilot's own validity gate; the script refuses to emit
artifacts if the gate fails.
"""
import sys, os, re, io, collections
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
OUT_TSV_B = os.path.join(HERE, "mw_pwkvn_missing_entries.tsv")
OUT_TSV_A = os.path.join(HERE, "mw_pwkvn_sup_overlap.tsv")

K1_RE = re.compile(r"<k1>([^<]+)")
K2_RE = re.compile(r"<k2>([^<]+)")
PC_RE = re.compile(r"<pc>([^<]+)")
L_RE = re.compile(r"^<L>(\d+)")

def entries(path):
    """Yield (Lnum, k1, k2, pc, body) for each <L>-anchored entry."""
    Lnum = k1 = k2 = pc = None
    body = []
    with io.open(path, encoding='utf-8') as f:
        for line in f:
            m = L_RE.match(line)
            if m:
                if Lnum is not None:
                    yield Lnum, k1, k2, pc, "".join(body)
                Lnum = m.group(1)
                k1 = ((K1_RE.search(line).group(1).strip() if K1_RE.search(line) else ""))
                m2 = K2_RE.search(line)
                k2 = (m2.group(1).strip() if m2 else "")
                mpc = PC_RE.search(line)
                pc = (mpc.group(1).strip() if mpc else "")
                body = [line]
            elif Lnum is not None:
                body.append(line)
                if line.startswith("<LEND>"):
                    yield Lnum, k1, k2, pc, "".join(body)
                    Lnum = None; body = []
    if Lnum is not None:
        yield Lnum, k1, k2, pc, "".join(body)

def norm(key):
    """Marker-stripped join tier: drop * ˚ ~ and hom-numeric suffix dots."""
    return key.strip().strip("*˚~").strip()

# --- MW -----------------------------------------------------------------
mw_k1, mw_k2, mw_sup, mw_main = set(), set(), set(), set()
mw_by_k1 = {}
for Lnum, k1, k2, pc, body in entries(os.path.join(ORIG, "mw", "mw.txt")):
    if not k1:
        continue
    mw_k1.add(k1)
    if k2:
        mw_k2.add(k2)
    if '<info n="sup"/>' in body:
        mw_sup.add(k1)
    mw_by_k1[k1] = (Lnum, pc)
mw_main = mw_k1 - mw_sup   # proper partition (verifier finding 14-09-2026: the
                           # tag-absence set overlapped mw_sup on duplicate k1s)
mw_all = mw_k1 | mw_k2
mw_all_norm = {norm(x) for x in mw_all if x}
print(f"MW: entries with k1={len(mw_k1)}, k1∪k2 unique={len(mw_all)}, "
      f"sup(annexure)={len(mw_sup)}, main={len(mw_main)}")

# --- pwkvn (Nachträge digitization) -------------------------------------
pwkvn_rows = list(entries(os.path.join(ORIG, "pwkvn", "pwkvn.txt")))
pwkvn_k1s = [k1 for _, k1, _, _, _ in pwkvn_rows if k1]
pwkvn_set = set(pwkvn_k1s)
print(f"pwkvn: entries={len(pwkvn_rows)}, unique k1={len(pwkvn_set)}")

# --- great PW + kürzere Fassung k1 sets ---------------------------------
pw_set = {k1 for _, k1, _, _, _ in entries(os.path.join(ORIG, "pw", "pw.txt")) if k1}
pwg_set = {k1 for _, k1, _, _, _ in entries(os.path.join(ORIG, "pwg", "pwg.txt")) if k1}
print(f"pw: unique k1={len(pw_set)}; pwg: unique k1={len(pwg_set)}")

# --- gate: the pilot's named check --------------------------------------
GATE_OK = ('kAritra' in pwkvn_set) and ('kAritra' not in mw_all) and ('kAritra' not in mw_all_norm)
if not GATE_OK:
    sys.exit("GATE FAIL: kAritra expected in pwkvn and absent from MW — "
             "pilot premise does not hold on current csl-orig; no artifacts written.")
print("GATE OK: kAritra in pwkvn, absent from MW (verbatim + normalized).")

# --- side A: annexure-overlap evidence ----------------------------------
pwkvn_pc_by_k1 = {}
for _, k1, _, pc, _ in pwkvn_rows:
    if k1 and k1 not in pwkvn_pc_by_k1:
        pwkvn_pc_by_k1[k1] = pc
inter_all = pwkvn_set & mw_all
inter_sup = pwkvn_set & mw_sup
inter_main = pwkvn_set & mw_main
enr = (len(inter_sup) / len(mw_sup)) / (len(inter_main) / len(mw_main)) if inter_main else float('inf')
print(f"Side A: pwkvn∩MW={len(inter_all)}  (∩MWsup={len(inter_sup)}, ∩MWmain-only={len(inter_main)})  "
      f"enrichment of MWsup vs MWmain = {enr:.2f}x")
with io.open(OUT_TSV_A, "w", encoding='utf-8', newline='') as f:
    f.write("pwkvn_k1\tpc\tmw_L\tmw_pc\tin_mw_sup\n")
    for k1 in sorted(inter_all):
        Lnum, mpc = mw_by_k1[k1]
        f.write(f"{k1}\t{pwkvn_pc_by_k1.get(k1,'')}\t{Lnum}\t{mpc}\t"
                f"{'sup' if k1 in mw_sup else 'main'}\n")

# --- side B: skipped-entry candidates ------------------------------------
rows = []
for Lnum, k1, k2, pc, body in pwkvn_rows:
    if not k1 or k1 in mw_all:
        continue
    if norm(k1) in mw_all_norm:
        tier = "normalized-only"   # matches MW only after *˚~ stripping
    else:
        tier = "absent"
    rows.append((k1, Lnum, pc, tier,
                 "Y" if "MAHĀVY" in body else "N",
                 "Y" if k1 in pw_set else "N",
                 "Y" if k1 in pwg_set else "N",
                 re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", body.split("\n", 1)[1] if "\n" in body else body)).strip()[:120]))
n_abs = sum(1 for r in rows if r[3] == "absent")
n_norm = sum(1 for r in rows if r[3] == "normalized-only")
n_mah = sum(1 for r in rows if r[4] == "Y")
uniq = {r[0] for r in rows}
n_pw = sum(1 for r in rows if r[5] == "Y")
n_pwg = sum(1 for r in rows if r[6] == "Y")
mah_uniq = {r[0] for r in rows if r[4] == "Y"}
print(f"Side B: pwkvn−MW = {len(rows)} rows over {len(uniq)} unique headwords "
      f"(absent={n_abs}, normalized-only={n_norm}); MAHĀVY-citing rows={n_mah} "
      f"({len(mah_uniq)} unique); in great-PW={n_pw}, in pwg={n_pwg}")

with io.open(OUT_TSV_B, "w", encoding='utf-8', newline='') as f:
    f.write("pwkvn_k1\tpwkvn_L\tpc\ttier\tmahavy\tin_pw\tin_pwg\tgloss_snippet\n")
    for r in sorted(rows, key=lambda r: r[0]):
        f.write("\t".join(r) + "\n")

print(f"WROTE {OUT_TSV_A}\nWROTE {OUT_TSV_B}")