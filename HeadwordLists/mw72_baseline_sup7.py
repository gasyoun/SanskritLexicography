"""MW72 baseline for the Nachträge-vs-MW comparison (csl-corrections#119 follow-up).

MG's point (14-09-2026): MW72 (55,390 entries) predates the completion of the
great PW (1855-75) and the whole kürzere Fassung (1879-89), so MW72 never saw
the later PW volumes / supplements. Comparing the Nachträge headwords against
MW72 AND MW99 separates two classes the single MW99 diff conflates:

  * never-seen  — absent from MW72 AND MW99: the Nachträge offered them and no
                  MW edition ever took them (the kāritra class proper),
  * seen-skipped — absent from MW99 but PRESENT in MW72: MW dropped an entry it
                  itself once had (a different correction class),
  * uptake      — of the pool NEW since MW72 (absent from MW72), how much did
                  MW99 add (main vs annexure)?

Also: per-layer MW72 coverage of sup_1..sup_7 — later PW volumes were printed
later, so MW72's coverage should fall off with the layer index.

Read-only over csl-orig/v02; deterministic; stdlib only.
"""
import sys, os, io, re
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "mw72_baseline_sup7.tsv")

L = re.compile(r"^<L>"); K1 = re.compile(r"<k1>([^<]+)"); K2 = re.compile(r"<k2>([^<]+)")
SUP = re.compile(r'<info n="sup_(\d)"/>'); MWSUP = '<info n="sup"/>'

def keys(path, want_annex=False):
    """Unique verbatim k1∪k2; optionally the k1 set of annexure-tagged entries."""
    k1s, k2s, annex, cur, buf = set(), set(), set(), None, []
    def flush():
        if cur is None: return
        g = K1.search(cur); k1 = g.group(1).strip() if g else None
        is_sup = any(MWSUP in b for b in buf)
        if k1:
            k1s.add(k1)
            if want_annex and is_sup: annex.add(k1)
        g = K2.search(cur)
        if g:
            k2s.add(g.group(1).strip())
            if want_annex and is_sup: annex.add(g.group(1).strip())
    for line in io.open(path, encoding='utf-8'):
        if L.match(line):
            flush(); cur = line; buf = [line]
        else:
            buf.append(line)
    flush()
    return (k1s | k2s, annex) if want_annex else (k1s | k2s, None)

mw99, annex99 = keys(os.path.join(ORIG, "mw", "mw.txt"), want_annex=True)
mw72, _ = keys(os.path.join(ORIG, "mw72", "mw72.txt"))
print(f"MW99 keys={len(mw99)} (annexure k1∪k2={len(annex99)}); MW72 keys={len(mw72)}")

# sup_7 headwords (raw k1, or starred k2 as the trial does)
sup_layers = {}
sup7 = []
cur = None; buf = []
def flush_pw():
    if cur is None: return
    m = None
    for b in buf:
        mm = SUP.search(b)
        if mm: m = mm; break
    if not m: return
    layer = int(m.group(1))
    g1 = K1.search(cur); g2 = K2.search(cur)
    k1 = g1.group(1).strip() if g1 else ""
    k2 = g2.group(1).strip() if g2 else ""
    sup_layers[layer] = sup_layers.get(layer, 0) + 1
    if layer == 7:
        hw = k2.lstrip("*") if k2.startswith("*") else k1
        if hw: sup7.append(hw)
for line in io.open(os.path.join(ORIG, "pw", "pw.txt"), encoding='utf-8'):
    if L.match(line):
        flush_pw(); cur = line; buf = [line]
    else:
        buf.append(line)
flush_pw()
sup7u = sorted(set(sup7))
print("sup layers: " + ", ".join(f"sup_{k}={v}" for k, v in sorted(sup_layers.items())))
print(f"sup_7 unique headwords: {len(sup7u)}")

s72, s99 = set(sup7u), set(sup7u)
never = [h for h in sup7u if h not in mw72 and h not in mw99]
dropped = [h for h in sup7u if h in mw72 and h not in mw99]
kept = [h for h in sup7u if h in mw72 and h in mw99]
new99 = [h for h in sup7u if h not in mw72 and h in mw99]
new_annex = [h for h in new99 if h in annex99]
new_main = [h for h in new99 if h in mw99 and h not in annex99]
print(f"2x2 over sup_7 unique: never-seen(absent MW72 & MW99)={len(never)}, "
      f"dropped(MW72 yes, MW99 no)={len(dropped)}, kept(both)={len(kept)}, "
      f"added-since-MW72(new in MW99)={len(new99)}")
print(f"of the {len(new99)} added since MW72: annexure={len(new_annex)}, main={len(new_main)}")
print(f"MW72 kAritra: {'kAritra' in mw72}; MW99 kAritra: {'kAritra' in mw99}")

# per-layer MW72 coverage (later volumes printed later -> falling coverage)
rows_cov = []
cur = None; buf = []; layer_hw = {}
for line in io.open(os.path.join(ORIG, "pw", "pw.txt"), encoding='utf-8'):
    if L.match(line):
        flush_pw(); cur = line; buf = [line]
    else:
        buf.append(line)
flush_pw()
# rebuild per-layer headword sets in one more pass
layer_hw = {}
cur = None; buf = []
def flush_pw2():
    if cur is None: return
    m = None
    for b in buf:
        mm = SUP.search(b)
        if mm: m = mm; break
    if not m: return
    layer = int(m.group(1))
    g1 = K1.search(cur); g2 = K2.search(cur)
    k1 = g1.group(1).strip() if g1 else ""
    k2 = g2.group(1).strip() if g2 else ""
    hw = k2.lstrip("*") if k2.startswith("*") else k1
    if hw: layer_hw.setdefault(layer, set()).add(hw)
for line in io.open(os.path.join(ORIG, "pw", "pw.txt"), encoding='utf-8'):
    if L.match(line):
        flush_pw2(); cur = line; buf = [line]
    else:
        buf.append(line)
flush_pw2()
for layer in sorted(layer_hw):
    hw = layer_hw[layer]
    rows_cov.append((layer, len(hw), sum(1 for h in hw if h in mw72), sum(1 for h in hw if h in mw99)))
print("layer | headwords | in MW72 | in MW99")
for layer, n, c72, c99 in rows_cov:
    print(f"sup_{layer} | {n} | {c72} ({100*c72/n:.0f}%) | {c99} ({100*c99/n:.0f}%)")

with io.open(OUT, "w", encoding='utf-8', newline='') as f:
    f.write("sup7_headword\tin_mw72\tin_mw99\tmw99_annexure\tclass\n")
    for h in sup7u:
        a, b = h in mw72, h in mw99
        cls = ("kept" if a and b else "dropped" if a else "never-seen" if not b else "added-since-mw72")
        f.write(f"{h}\t{'Y' if a else 'N'}\t{'Y' if b else 'N'}\t{'Y' if h in annex99 else 'N'}\t{cls}\n")
print(f"WROTE {OUT}")