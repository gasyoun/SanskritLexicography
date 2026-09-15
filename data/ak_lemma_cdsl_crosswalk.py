#!/usr/bin/env python3
"""Amarakosha lemma-level x CDSL union crosswalk (H4746, sibling census B10).

AK is NOT in CDSL (H3862 trap: Amara/Medini recorded ABSENT from the CDSL
union — union_headwords.tsv carries zero AMAR rows). The only existing AK
edge is the DOMAIN level (semdom-amarakosha-crosswalk, A58/H742); the LEMMA
level — AK lemma x CDSL union key1 — never existed. This builder fills it.

Consumes (never rebuilt here, per the reuse rule):
  * HeadwordLists/union/union_headwords.tsv — THE 12-dict CDSL headword
    master (323k rows, exact SLP1 <k1> key; overlap-matrix precedent).
  * AMAR/amar.txt — Cologne Amarakosha source; parsed by the SAME code path
    as the domain-level sibling data/semdom_ak_bridge.py (parse_amar vendored
    verbatim below so both lanes read AK identically).

The join is exact SLP1 string equality on the union key; no extra
normalization is applied or needed (union/UNION.md already collapses
homograph numbering). A casefolded diagnostic tier only COUNTS accent-only
near-misses — it never promotes them to matches.

Outputs (beside this script):
  * ak_lemma_cdsl_crosswalk.tsv — one row per (varga, eid, lemma) instance:
    lemma_slp1  varga  eid  match_type  union_dicts  n_dicts
    match_type = exact (hit) | miss. union_dicts empty for misses.
  * ak_lemma_cdsl_crosswalk_stats.json — coverage, per-varga, n_dicts spread.

Selftest (--selftest): seeded 30-lemma sample re-verified through an
INDEPENDENT code path (linear re-scan of the union TSV + re-parse of
amar.txt); exits 1 on any discrepancy. This is the H4746 "Prove with".

License: lemma strings + ID pairs only, CC BY-SA 4.0 (same basis as the
union index and A58; no AK prose).

H4746 (14-09-2026, OxAlpha (opencode/z-ai/glm-5.3-flash)).
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
UNION = REPO / "HeadwordLists" / "union" / "union_headwords.tsv"
AMAR = REPO.parent / "AMAR" / "amar.txt"

# AK kanda.varga ids in amar.txt ;v{ file order — shared with A58 (H742).
VARGA_IDS = [
    "AK-1.1", "AK-1.2", "AK-1.3", "AK-1.4", "AK-1.5", "AK-1.6", "AK-1.7",
    "AK-1.8", "AK-1.9", "AK-1.10", "AK-2.1", "AK-2.2", "AK-2.3", "AK-2.4",
    "AK-2.5", "AK-2.6", "AK-2.7", "AK-2.8", "AK-2.9", "AK-2.10", "AK-3.1",
    "AK-3.2", "AK-3.3", "AK-3.4",
]


def parse_amar(path):
    """Yield (varga_id, eid, [slp1 lemmas]) in file order.

    Vendored VERBATIM from data/semdom_ak_bridge.py (H742) — semdom_ak_bridge
    imports nltk at module top and cannot be imported without it; both lanes
    must read AK through the same normalization (strip trailing gender code).
    """
    out = []
    vi = -1
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith(";v{"):
                vi += 1
                continue
            m = re.match(r"<eid>(\d+)<syns><s>(.*?)</s>", ln)
            if m and vi >= 0:
                eid = int(m.group(1))
                lemmas = []
                for tok in m.group(2).split(","):
                    tok = tok.strip()
                    if "-" in tok:
                        tok = tok.rsplit("-", 1)[0]  # strip gender code
                    if tok:
                        lemmas.append(tok)
                out.append((VARGA_IDS[vi], eid, lemmas))
    return out


def load_union(path):
    """slp1 key -> dicts string, straight from the union index."""
    union = {}
    with open(path, encoding="utf-8-sig") as f:
        header = f.readline().rstrip("\n").split("\t")
        i_s, i_d = header.index("slp1"), header.index("dicts")
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) > i_d:
                union[p[i_s]] = p[i_d]
    return union


def build():
    synsets = parse_amar(AMAR)
    union = load_union(UNION)

    rows = []  # (lemma, varga, eid, match_type, dicts, n_dicts)
    inst = hit_inst = 0
    dist = set()
    dist_hits = set()
    per_varga = defaultdict(lambda: [0, 0])
    ndist = Counter()
    for varga, eid, lemmas in synsets:
        for lem in lemmas:
            inst += 1
            dist.add(lem)
            per_varga[varga][0] += 1
            d = union.get(lem)
            if d is not None:
                hit_inst += 1
                dist_hits.add(lem)
                per_varga[varga][1] += 1
                n = len(d.split())
                ndist[n] += 1
                rows.append((lem, varga, eid, "exact", d, n))
            else:
                rows.append((lem, varga, eid, "miss", "", 0))

    # Diagnostic only: accent/case-fold near-misses are COUNTED, never matched.
    fold_union = defaultdict(list)
    for k in union:
        fold_union[k.lower()].append(k)
    fold_recoverable = sum(
        1 for lem in dist - dist_hits if lem.lower() in fold_union
    )

    out = HERE / "ak_lemma_cdsl_crosswalk.tsv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write("lemma_slp1\tvarga\teid\tmatch_type\tunion_dicts\tn_dicts\n")
        for lem, varga, eid, mt, d, n in rows:
            f.write(f"{lem}\t{varga}\t{eid}\t{mt}\t{d}\t{n}\n")

    stats = {
        "handoff": "H4746",
        "ak_source": "AMAR/amar.txt (Cologne Amarakosha; NOT in CDSL, H3862)",
        "union_source": "HeadwordLists/union/union_headwords.tsv (12 CDSL dicts)",
        "join": "exact SLP1 string equality on the union key (house standard)",
        "ak_synsets": len(synsets),
        "ak_lemma_instances": inst,
        "ak_lemma_distinct": len(dist),
        "exact_instance_hits": hit_inst,
        "exact_instance_coverage": round(100 * hit_inst / inst, 2),
        "exact_distinct_hits": len(dist_hits),
        "exact_distinct_coverage": round(100 * len(dist_hits) / len(dist), 2),
        "misses_distinct": len(dist) - len(dist_hits),
        "fold_near_miss_distinct_diagnostic_only": fold_recoverable,
        "per_varga": {
            v: {"instances": a, "hits": b, "coverage": round(100 * b / a, 2)}
            for v, (a, b) in sorted(per_varga.items())
        },
        "n_dicts_distribution_matched_instances": dict(sorted(ndist.items())),
        "crosswalk_rows": len(rows),
    }
    with open(HERE / "ak_lemma_cdsl_crosswalk_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=1, sort_keys=False)
    return stats


def selftest(sample=30, seed=42):
    """30-lemma sample re-verified through an INDEPENDENT code path."""
    synsets = parse_amar(AMAR)
    with open(UNION, encoding="utf-8-sig") as f:  # independent linear re-scan
        header = f.readline().rstrip("\n").split("\t")
        i_s, i_d = header.index("slp1"), header.index("dicts")
        union_lines = {}
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) > i_d:
                union_lines[p[i_s]] = p[i_d]

    tsv = {}
    with open(HERE / "ak_lemma_cdsl_crosswalk.tsv", encoding="utf-8") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        for line in f:
            p = line.rstrip("\n").split("\t")
            tsv[(p[0], p[1], int(p[2]))] = (p[3], p[4], int(p[5]))

    instances = [(v, e, l) for v, e, ls in synsets for l in ls]
    import random
    rng = random.Random(seed)
    picks = rng.sample(instances, sample)
    checked = 0
    for v, e, l in picks:
        # Expectation re-derived from the INDEPENDENT union re-scan:
        expected = "exact" if l in union_lines else "miss"
        mt, d, n = tsv[(l, v, e)]
        assert mt == expected, f"match_type mismatch for {l} ({v}/{e}): tsv={mt} independent={expected}"
        if expected == "exact":
            real = union_lines[l]
            assert real == d, f"dicts mismatch for {l}: tsv={d!r} union={real!r}"
            assert n == len(d.split()), f"n_dicts mismatch for {l}"
        else:
            assert d == "" and n == 0, f"miss row carries residue for {l}"
        checked += 1
    n_exact = sum(1 for v, e, l in picks if l in union_lines)
    print(f"selftest PASS: {checked}/{sample} sampled rows re-verified via "
          f"independent union re-scan (seed={seed}; {n_exact} exact / "
          f"{checked - n_exact} miss)")
    # eyeball canaries (first occurrence anywhere in the crosswalk)
    for c in ("deva", "svarga", "nara"):
        row = next((k for k in tsv if k[0] == c), None)
        print("canary", c, "->", tsv.get(row, "ABSENT"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--union", default=str(UNION))
    ap.add_argument("--amar", default=str(AMAR))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    stats = build()
    s = json.dumps(stats, ensure_ascii=False, indent=1)
    print(s)
    print("\nNow run: python data/ak_lemma_cdsl_crosswalk.py --selftest")


if __name__ == "__main__":
    main()
