"""H742 Level B evaluation: inter-annotator kappa, then bridge metrics vs gold.

Modes:
  python data/semdom_ak_metrics.py kappa
      Compare semdom_ak_annotator_A.tsv vs _B.tsv: exact + coarse (level-2
      prefix) Cohen's kappa, and write semdom_ak_disagreements.tsv for
      adjudication.
  python data/semdom_ak_metrics.py metrics
      Requires the adjudicated semdom_ak_gold.tsv (eid, code). Reports bridge
      top-1 precision / top-6 recall vs gold, coverage both directions, and
      varga<->semdom-subtree structure agreement against the Level A
      crosswalk (semdom_varga_crosswalk.csv).
"""

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent


def read_tsv(name):
    rows = {}
    with open(HERE / name, encoding="utf-8-sig") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for r in rdr:
            rows[int(r["eid"])] = r
    return rows


def coarse(code):
    """Level-2 prefix: '8.4.1' -> '8.4'; '1.1' -> '1.1'; NONE stays NONE."""
    if code == "NONE":
        return code
    parts = code.split(".")
    return ".".join(parts[:2])


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[c] / n * cb[c] / n for c in set(ca) | set(cb))
    return po, (po - pe) / (1 - pe)


def mode_kappa():
    A, B = read_tsv("semdom_ak_annotator_A.tsv"), read_tsv("semdom_ak_annotator_B.tsv")
    assert set(A) == set(B) and len(A) == 200, (len(A), len(B))
    eids = sorted(A)
    exact = [(A[e]["code"], B[e]["code"]) for e in eids]
    co = [(coarse(a), coarse(b)) for a, b in exact]
    po_e, k_e = kappa(exact)
    po_c, k_c = kappa(co)
    print(f"n=200  exact: agreement {po_e:.1%}, kappa {k_e:.3f}")
    print(f"       coarse(level-2): agreement {po_c:.1%}, kappa {k_c:.3f}")
    with open(HERE / "semdom_ak_disagreements.tsv", "w", encoding="utf-8", newline="") as f:
        f.write("eid\tcode_A\tnote_A\tcode_B\tnote_B\n")
        n = 0
        for e in eids:
            if A[e]["code"] != B[e]["code"]:
                f.write(f"{e}\t{A[e]['code']}\t{A[e].get('note','')}\t"
                        f"{B[e]['code']}\t{B[e].get('note','')}\n")
                n += 1
    print(f"disagreements written: {n} -> semdom_ak_disagreements.tsv")


def mode_metrics():
    gold = read_tsv("semdom_ak_gold.tsv")
    cand = {}
    with open(HERE / "semdom_ak_candidates.tsv", encoding="utf-8") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for r in rdr:
            codes = [c.split(":")[0] for c in r["candidates"].split(";") if c]
            cand[int(r["eid"])] = (r["varga"], codes)

    judged = {e: g["code"] for e, g in gold.items() if g["code"] != "NONE"}
    none_n = len(gold) - len(judged)
    top1 = sum(cand[e][1][:1] == [c] for e, c in judged.items())
    top6 = sum(c in cand[e][1] for e, c in judged.items())
    top1c = sum(bool(cand[e][1]) and coarse(cand[e][1][0]) == coarse(c)
                for e, c in judged.items())
    top6c = sum(any(coarse(x) == coarse(c) for x in cand[e][1])
                for e, c in judged.items())
    print(f"gold n={len(gold)}, NONE={none_n}, judged={len(judged)}")
    print(f"bridge top-1 exact:  {top1}/{len(judged)} = {top1/len(judged):.1%}")
    print(f"bridge top-6 exact:  {top6}/{len(judged)} = {top6/len(judged):.1%}")
    print(f"bridge top-1 coarse: {top1c}/{len(judged)} = {top1c/len(judged):.1%}")
    print(f"bridge top-6 coarse: {top6c}/{len(judged)} = {top6c/len(judged):.1%}")

    # Coverage both directions (over ALL 5,590 synsets).
    with open(HERE / "semdom.json", encoding="utf-8") as f:
        all_codes = {it["key"] for it in json.load(f)["items"]}
    hit = set()
    n_any = 0
    for _, codes in cand.values():
        n_any += bool(codes)
        hit.update(codes)
    print(f"AK->semdom: {n_any}/{len(cand)} synsets with >=1 candidate "
          f"({n_any/len(cand):.1%})")
    print(f"semdom<-AK: {len(hit)}/{len(all_codes)} domains receive >=1 AK "
          f"candidate ({len(hit)/len(all_codes):.1%})")
    gold_domains = set(judged.values())
    print(f"semdom<-AK (gold only): {len(gold_domains)} distinct domains in "
          f"the 200-synset gold")

    # Structure agreement: gold code's level-1/2 ancestor vs Level A row set.
    levelA = defaultdict(set)
    with open(HERE / "semdom_varga_crosswalk.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            levelA[r["ak_varga_id"]].add(r["semdom_code"])
    agree = 0
    for e, c in judged.items():
        varga = cand[e][0]
        anc = {".".join(c.split(".")[:i]) for i in range(1, c.count(".") + 2)}
        agree += bool(anc & levelA[varga] or any(
            a.startswith(c + ".") or c.startswith(a + ".") or a == c
            for a in levelA[varga]))
    print(f"structure agreement (gold domain within the varga's Level A "
          f"subtree set): {agree}/{len(judged)} = {agree/len(judged):.1%}")


if __name__ == "__main__":
    {"kappa": mode_kappa, "metrics": mode_metrics}[sys.argv[1]]()
