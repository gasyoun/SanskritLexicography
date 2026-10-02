#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h5279_jev_design_probe.py — H5279: which Jev question design discriminates?

Companion to tools/h5279_jev_defgen_gloss_rerank.py (H5279). Before the full
defgen re-rank pass, four question designs were probed on 8 high-frequency
frozen-sample items (frequency bands where the A0 random-floor candidate is
clearly a derangement), reporting the A0-vs-systems floor gap per design:

  D1  score, all five candidates in ONE state (mirrors the H5277 rerank shape)
  D2  score, ONE candidate per state (adopted — mirrors the H730 judge)
  D3  noul, all five candidates in one state
  D4  choice, "which candidate best fits"

Measured 24-09-2026 (live, jev-1.13.0): D1 gap 0.011 · D2 gap +4.283 ·
D3 gap 0.001 · D4 one constant winner. The full pass runs D2; this file is the
evidence for that choice, not part of the production path.

Usage: python tools/h5279_jev_design_probe.py   (live, 4 designs x 8 items)
"""
import io, json, os, random, sys, time
sys.stdout.reconfigure(encoding="utf-8")
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(here, "tools"))
sys.path.insert(0, os.path.join(os.path.dirname(here), "Uprava", "tools"))
import jev_probe as jp
import h5279_jev_defgen_gloss_rerank as h

def shuffled_arms(slp1):
    order = list(h.ARMS)
    random.Random("%d|%s" % (h.SEED, slp1)).shuffle(order)
    return order


rows = h.load_frozen(); atts = h.load_attestations(); gen = h.load_gen(); judge = h.load_judge()
# 8 items: prefer high freq, where A0 is clearly a derangement
sample = [r for r in rows if r["freq_band"] == "high"][:8]
cfg = jp.resolve_config(type("N", (), {"env_file": str(jp.DEFAULT_ENV_FILE)})())

def call(state, questions):
    st, body = jp.call_jev({"state": state, "model": cfg[1], "questions": questions},
                           cfg[0], cfg[2], timeout_s=120)
    return st, body

def state_of(row, arms_in_state):
    sents = [s for s in atts.get(row["slp1"], []) if s.strip()][:5]
    L = ["Sanskrit headword: %s (SLP1: %s). Grammar: %s." % (row["iast"], row["slp1"], row.get("grammar","?")), "",
         "Corpus context — DCS attestation sentences showing the sense in use:"]
    for i, s in enumerate(sents, 1): L.append("  %d. %s" % (i, s))
    if arms_in_state:
        L.append(""); L.append("Candidate English glosses (unranked):")
        for i, a in enumerate(arms_in_state, 1): L.append("  %d. %s" % (i, gen[a].get(row["slp1"], "")))
    return "\n".join(L)

NOUL = {"true": "the gloss fits the sense in the corpus context",
        "false": "the gloss does not fit the sense in the corpus context"}
LEV = h.LEVELS

def d1(row):  # score, shared state (current)
    order = shuffled_arms(row["slp1"])
    return call(state_of(row, order), {("c%d" % i): jp._score("How faithful is Candidate %d to the sense used in the context?" % i, LEV) for i in range(1, 6)}) + (order,)

def d2(row):  # score, isolated candidate
    out = {}
    for a in h.ARMS:
        st, b = call(state_of(row, [a]), {"s": jp._score("How faithful is this gloss to the sense used in the context?", LEV)})
        out[a] = None if st != 200 else b["answers"]["s"]
    return out

def d3(row):  # noul, shared state
    order = shuffled_arms(row["slp1"])
    return call(state_of(row, order), {("c%d" % i): jp._noul("Does Candidate %d fit the sense in the corpus context?" % i, NOUL) for i in range(1, 6)}) + (order,)

def d4(row):  # choice: which candidate best fits
    order = shuffled_arms(row["slp1"])
    opts = {("c%d" % i): (gen[a].get(row["slp1"], "") or "")[:120] for i, a in enumerate(order, 1)}
    return call(state_of(row, order), {"best": jp._choice("Which candidate best fits the sense used in the corpus context?", opts)}) + (order,)

res = {"D1": [], "D2": [], "D3": [], "D4": []}
for row in sample:
    st, b, order = d1(row)
    if st == 200:
        res["D1"].append({order[int(k[1:])-1]: round(v.get("score", 0), 3) for k, v in b["answers"].items()})
    b = d2(row)
    res["D2"].append({a: (round(v["score"], 3) if v and "score" in v else None) for a, v in b.items()})
    st, b, order = d3(row)
    if st == 200:
        res["D3"].append({order[int(k[1:])-1]: round(v.get("noul", 0), 3) for k, v in b["answers"].items()})
    st, b, order = d4(row)
    if st == 200:
        ans = b["answers"]["best"]; ch = ans.get("choice")
        res["D4"].append({(order[int(ch[1:])-1] if ch and ch.startswith("c") else ch): 1.0})

for design, rowsx in res.items():
    if not rowsx: print(design, "NO DATA"); continue
    keys = h.ARMS
    mean = {a: sum(r.get(a, 0) or 0 for r in rowsx) / len(rowsx) for a in keys}
    sysm = sum(mean[a] for a in keys if a != "A0_random_floor") / 4
    print(design, "A0=%.3f systems=%.3f gap=%.3f" % (mean["A0_random_floor"], sysm, sysm - mean["A0_random_floor"]),
          {a: round(mean[a], 2) for a in keys})
    for r in rowsx: print("   ", {a: r.get(a) for a in keys})
