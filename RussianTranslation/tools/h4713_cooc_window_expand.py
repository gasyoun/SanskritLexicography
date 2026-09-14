#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4713_cooc_window_expand.py — stem co-occurrence expansion of pwg-sense-attestation-window.

Handoff H4713 (OxAlpha, 15-09-2026). Extends the C2 phase-1 per-sense attestation
window (RussianTranslation/src/pwg_sense_attestation_window.jsonl, H3168) with a
co-occurrence-based expansion derived from kosha dataset
``dcs-stem-cooccurrence-full`` (VisualDCS derived-data/Sochetaemost-sanskritskih-osnov/NEW/1-222342.csv).

Semantics (honesty contract preserved):
  * The C2P1 window (``earliest``/``latest``) stays UNTOUCHED: it is
    "per Böhtlingk–Roth's citations" — a fact about the dictionary, never about
    the language.
  * The expansion adds a SECOND evidence class — corpus co-occurrence. For a
    headword key1, its DCS co-occurring stems (pooled L+R, self excluded) that
    themselves carry a C2P1 window vote a weighted window:
    ``cooc_earliest`` = weighted 10th percentile of partner earliest values,
    ``cooc_latest``   = weighted 90th percentile of partner latest values
    (weights = raw co-occurrence counts).
  * ``expanded_earliest``/``expanded_latest`` = union of the BR window and the
    cooc window. ``expansion_delta_left``/``expansion_delta_right`` record how
    far the union pushed past the BR window (0 = no push).
  * Senses with NO BR window (unresolvable / citation-less) get the cooc window
    as an explicitly-labeled inferred-only window (``window_basis`` =
    "cooccurrence-only"); it is never presented as BR-cited.

Join: DCS stems (IAST) -> SLP1 via the canonical sanskrit_util.to_slp1;
PWG key1s are already SLP1. Partner key1s outside the window universe simply do
not contribute (counted, never guessed).

Verification: held-out sample of windowed senses (seeded) — the cooc window is
derived WITHOUT the sense's own BR window and checked for intersection /
containment against it. Pre-registered PASS rule: intersection rate >= 50%.

Usage (repo root):
  python RussianTranslation/tools/h4713_cooc_window_expand.py --selftest
  python RussianTranslation/tools/h4713_cooc_window_expand.py \
      --cooc <path to 1-222342.csv> [--limit-rows N]

Inputs are read-only; outputs land beside the C2P1 artifacts:
  RussianTranslation/src/pwg_sense_attestation_window_cooc_expanded.jsonl
  RussianTranslation/reports/H4713_cooc_window_expansion_validation.json
"""
import argparse
import json
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
REPO = os.path.dirname(RT)
sys.path.insert(0, os.path.join(os.path.dirname(REPO), "sanskrit-util", "py"))
from sanskrit_util import to_slp1  # noqa: E402

WINDOW_IN = os.path.join(RT, "src", "pwg_sense_attestation_window.jsonl")
WINDOW_OUT = os.path.join(RT, "src", "pwg_sense_attestation_window_cooc_expanded.jsonl")
REPORT_OUT = os.path.join(RT, "reports", "H4713_cooc_window_expansion_validation.json")

DEFAULT_COOC = os.path.join(
    os.path.dirname(REPO), "VisualDCS", "derived-data",
    "Sochetaemost-sanskritskih-osnov", "NEW", "1-222342.csv")

HELD_OUT_N = 300
HELD_OUT_SEED = 4713
PASS_INTERSECTION = 0.50


# ---------------------------------------------------------------- helpers
def norm_slp1(text):
    """Join key: IAST/SLP1 string -> normalized SLP1 (NFC, stripped, no digits)."""
    s = to_slp1(text.strip())
    return s.rstrip("0123456789")


def weighted_percentile(pairs, q):
    """pairs = [(value, weight)]; deterministic lower-interpolation percentile."""
    if not pairs:
        return None
    total = sum(w for _, w in pairs)
    if total <= 0:
        return None
    acc = 0.0
    for value, weight in sorted(pairs, key=lambda p: p[0]):
        acc += weight
        if acc >= q * total:
            return value
    return pairs[-1][0]


def load_windows(path):
    """-> (rows, key1 -> {earliest_min, latest_max, windowed_n, senses_n})."""
    rows = []
    by_key = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            rows.append(row)
            agg = by_key.setdefault(row["key1"], {
                "earliest_min": None, "latest_max": None, "windowed_n": 0, "senses_n": 0})
            agg["senses_n"] += 1
            if row.get("earliest") is not None:
                agg["windowed_n"] += 1
                e, l = row["earliest"], row["latest"]
                agg["earliest_min"] = e if agg["earliest_min"] is None else min(agg["earliest_min"], e)
                agg["latest_max"] = l if agg["latest_max"] is None else max(agg["latest_max"], l)
    return rows, by_key


def load_cooc(path, limit_rows=None):
    """Parse the Sochetaemost CSV.

    Row shape (tab-separated): stem_id, stem_iast, side(L|R), n_partners,
    then (partner_id, count) pairs. -> (id->stem, stem_slp1 -> {partner_id: count})
    """
    id_to_stem = {}
    cooc = defaultdict(lambda: defaultdict(int))
    n_rows = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4:
                continue
            sid = int(parts[0])
            id_to_stem[sid] = parts[1]
            n_pairs = int(parts[3])
            vals = parts[4:]
            stem_slp = norm_slp1(parts[1])
            for i in range(min(n_pairs, len(vals) // 2)):
                pid = int(vals[2 * i])
                cnt = int(vals[2 * i + 1])
                cooc[stem_slp][pid] += cnt  # pool L+R
            n_rows += 1
            if limit_rows and n_rows >= limit_rows:
                break
    return id_to_stem, dict(cooc)


def cooc_window_for(key1, cooc, id_to_stem, key_windows, self_slp):
    """Weighted partner window for one key1. Partners resolve via id_to_stem;
    only partners landing in the window universe contribute. Self excluded."""
    partners = cooc.get(self_slp, {})
    e_pairs, l_pairs = [], []
    used_n = used_w = 0
    for pid, cnt in partners.items():
        stem = id_to_stem.get(pid)
        if stem is None:
            continue
        pkey = norm_slp1(stem)
        if pkey == self_slp or pkey == key1:
            continue  # self-exclusion (both spellings)
        agg = key_windows.get(pkey)
        if agg is None or agg["earliest_min"] is None:
            continue
        e_pairs.append((agg["earliest_min"], cnt))
        l_pairs.append((agg["latest_max"], cnt))
        used_n += 1
        used_w += cnt
    if not e_pairs:
        return None
    return {
        "cooc_partner_n": used_n,
        "cooc_weight": used_w,
        "cooc_earliest": weighted_percentile(e_pairs, 0.10),
        "cooc_latest": weighted_percentile(l_pairs, 0.90),
    }


def expand_row(row, cw):
    """Attach cooc_* + expanded_* fields to one sense row (returns new dict)."""
    out = dict(row)
    if cw is None:
        out.update({"cooc_partner_n": 0, "cooc_weight": 0,
                    "cooc_earliest": None, "cooc_latest": None,
                    "expanded_earliest": row.get("earliest"),
                    "expanded_latest": row.get("latest"),
                    "expansion_delta_left": 0, "expansion_delta_right": 0,
                    "window_basis": "br-citations" if row.get("earliest") is not None
                    else "none"})
        return out
    out.update({"cooc_partner_n": cw["cooc_partner_n"],
                "cooc_weight": cw["cooc_weight"],
                "cooc_earliest": cw["cooc_earliest"],
                "cooc_latest": cw["cooc_latest"]})
    e, l = row.get("earliest"), row.get("latest")
    if e is None:
        out["expanded_earliest"] = cw["cooc_earliest"]
        out["expanded_latest"] = cw["cooc_latest"]
        out["expansion_delta_left"] = 0
        out["expansion_delta_right"] = 0
        out["window_basis"] = "cooccurrence-only"
    else:
        out["expanded_earliest"] = min(e, cw["cooc_earliest"])
        out["expanded_latest"] = max(l, cw["cooc_latest"])
        out["expansion_delta_left"] = e - out["expanded_earliest"]
        out["expansion_delta_right"] = out["expanded_latest"] - l
        out["window_basis"] = "br-citations+cooccurrence"
    return out


# ---------------------------------------------------------------- selftest
def selftest():
    # weighted_percentile
    assert weighted_percentile([(1, 1), (2, 1), (3, 1)], 0.5) == 2
    assert weighted_percentile([(10, 9), (1, 1)], 0.5) == 10
    assert weighted_percentile([(10, 1), (1, 9)], 0.5) == 1
    assert weighted_percentile([], 0.5) is None
    # self-exclusion + join via id map
    id_to_stem = {1: "agni", 2: "agní", 3: "vahnim", 4: "jvalā"}
    cooc = {"agni": {1: 5, 2: 3, 3: 2, 4: 1}}
    key_windows = {
        "agni": {"earliest_min": -900, "latest_max": 1830, "windowed_n": 2, "senses_n": 3},
        "vahnim": {"earliest_min": 400, "latest_max": 1200, "windowed_n": 1, "senses_n": 1},
        "jvalA": {"earliest_min": -900, "latest_max": 600, "windowed_n": 1, "senses_n": 1},
    }
    cw = cooc_window_for("agni", cooc, id_to_stem, key_windows, "agni")
    assert cw is not None and cw["cooc_partner_n"] == 2, cw  # agni+agní excluded
    row = {"key1": "agni", "sense_index": 0, "earliest": -400, "latest": 800}
    out = expand_row(row, cw)
    assert out["expanded_earliest"] <= -400 and out["expanded_latest"] >= 800
    assert out["window_basis"] == "br-citations+cooccurrence"
    # no-window row -> cooccurrence-only
    row2 = {"key1": "agni", "sense_index": 9, "earliest": None, "latest": None}
    out2 = expand_row(row2, cw)
    assert out2["window_basis"] == "cooccurrence-only" and out2["expanded_earliest"] is not None
    # no partners -> untouched BR
    out3 = expand_row(row, None)
    assert out3["expanded_earliest"] == -400 and out3["window_basis"] == "br-citations"
    print("selftest PASS (percentiles, self-exclusion, expansion, bases)")
    return 0


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cooc", default=DEFAULT_COOC)
    ap.add_argument("--limit-rows", type=int, default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    rows, key_windows = load_windows(WINDOW_IN)
    key1s = set(key_windows)
    id_to_stem, cooc = load_cooc(args.cooc, args.limit_rows)
    print(f"window rows {len(rows)} / key1s {len(key1s)}; "
          f"cooc stems {len(cooc)} / ids {len(id_to_stem)}")

    # per-key1 cooc windows (computed once, shared by all senses of the key1)
    key1_cw = {}
    for k1 in key1s:
        cw = cooc_window_for(k1, cooc, id_to_stem, key_windows, norm_slp1(k1))
        if cw is not None:
            key1_cw[k1] = cw

    # corpus horizon observed in the window universe (dating-table extremes
    # actually reached): used ONLY for the saturation flag, never for values.
    corpus_min = min(a["earliest_min"] for a in key_windows.values() if a["earliest_min"] is not None)
    corpus_max = max(a["latest_max"] for a in key_windows.values() if a["latest_max"] is not None)

    out_rows = []
    for r in rows:
        out = expand_row(r, key1_cw.get(r["key1"]))
        out["cooc_saturated"] = bool(
            out["cooc_partner_n"] > 0
            and out["cooc_earliest"] == corpus_min and out["cooc_latest"] == corpus_max)
        out_rows.append(out)
    os.makedirs(os.path.dirname(WINDOW_OUT), exist_ok=True)
    with open(WINDOW_OUT, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=False) + "\n")

    # ---- census
    n = len(out_rows)
    n_cooc = sum(1 for r in out_rows if r["cooc_partner_n"] > 0)
    n_br = sum(1 for r in out_rows if r.get("earliest") is not None)
    n_only = sum(1 for r in out_rows if r["window_basis"] == "cooccurrence-only")
    n_widened = sum(1 for r in out_rows
                    if r["window_basis"] == "br-citations+cooccurrence"
                    and (r["expansion_delta_left"] > 0 or r["expansion_delta_right"] > 0))
    n_untouched = sum(1 for r in out_rows
                      if r["window_basis"] == "br-citations+cooccurrence"
                      and r["expansion_delta_left"] == 0 and r["expansion_delta_right"] == 0)
    deltas = [r["expansion_delta_left"] + r["expansion_delta_right"] for r in out_rows
              if r["window_basis"] == "br-citations+cooccurrence"]
    med_delta = sorted(deltas)[len(deltas) // 2] if deltas else 0
    n_saturated = sum(1 for r in out_rows if r["cooc_saturated"])

    # ---- held-out verification: windowed senses, cooc window vs true window.
    # Reported split by saturation: for saturated rows the near-perfect
    # intersection is trivial (the union spans the corpus horizon) — the
    # informative number is the NON-saturated stratum.
    rng = random.Random(HELD_OUT_SEED)
    windowed = [r for r in out_rows if r.get("earliest") is not None and r["cooc_partner_n"] > 0]
    sample = rng.sample(windowed, min(HELD_OUT_N, len(windowed)))

    def stratum_stats(subset):
        inter = contain = 0
        for r in subset:
            ce, cl = r["cooc_earliest"], r["cooc_latest"]
            te, tl = r["earliest"], r["latest"]
            if ce <= tl and cl >= te:
                inter += 1
            if ce <= te and cl >= tl:
                contain += 1
        k = len(subset)
        return {"n": k,
                "intersection_rate": round(inter / k, 4) if k else None,
                "containment_rate": round(contain / k, 4) if k else None}

    sat_stats = stratum_stats([r for r in sample if r["cooc_saturated"]])
    nonsat_stats = stratum_stats([r for r in sample if not r["cooc_saturated"]])
    overall = stratum_stats(sample)
    verdict = "PASS" if (overall["intersection_rate"] or 0) >= PASS_INTERSECTION else "FAIL"

    report = {
        "handoff": "H4713",
        "created": "15-09-2026",
        "inputs": {
            "window": os.path.relpath(WINDOW_IN, REPO),
            "cooc": os.path.relpath(args.cooc, REPO) if os.path.exists(args.cooc) else args.cooc,
        },
        "output": os.path.relpath(WINDOW_OUT, REPO),
        "census": {
            "senses_total": n,
            "senses_with_cooc_evidence": n_cooc,
            "senses_br_windowed": n_br,
            "senses_cooccurrence_only": n_only,
            "senses_br_widened_by_cooc": n_widened,
            "senses_br_not_widened": n_untouched,
            "median_expansion_delta_years": med_delta,
            "senses_cooc_saturated_at_corpus_horizon": n_saturated,
        },
        "held_out_verification": {
            "seed": HELD_OUT_SEED,
            "pass_rule": f"intersection_rate >= {PASS_INTERSECTION}",
            "overall": overall,
            "by_saturation": {"saturated": sat_stats, "non_saturated": nonsat_stats},
            "verdict": verdict,
        },
    }
    os.makedirs(os.path.dirname(REPORT_OUT), exist_ok=True)
    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report["census"], indent=2))
    print(json.dumps(report["held_out_verification"], indent=2))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
