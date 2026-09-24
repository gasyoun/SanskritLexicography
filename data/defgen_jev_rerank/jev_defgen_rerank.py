#!/usr/bin/env python3
"""jev_defgen_rerank.py — H5279: TypeSafe Jev (jev-1.13.0) as defgen gloss judge/re-ranker.

Measurement-only bench runner (no product change): on the FROZEN 500-headword
defgen sample (kosha data/eval/defgen, seed 730, FEATURES_INDEX F48), Jev
scores the 5 frozen arm candidates per headword. Results are compared with the
existing blinded DeepSeek-chat judge baseline (judge_*.jsonl, 11-07-2026 run)
on judge-quality agreement + cost. Verdict REPLACE only if Jev beats the
baseline at lower cost (AND survives the evidence-map bar: two-box
reproduction — JEV_NO_VALUE_EVIDENCE_MAP_24-09-2026); MEASURE-ONLY otherwise.

Call architecture (live-calibrated 24-09-2026, this file's --probe history):
  - ONE call PER CANDIDATE with a SINGLE `noul` question — the estate's only
    discrimination-proven form (H5277 GO, H5276 PASS). Batch forms (5-10
    questions per request against a shared state) measured content-insensitive
    on this API: gold-copy and deranged candidates both scored ~4.45/6 (score
    primitive) and exactly 0.36 noul. Proven single-question per-candidate
    form is therefore the primary arm; the `score` primitive gets a small
    single-question check (--score-check) for the record.
  - Budget fence <=550 external calls for the whole handoff: 4 calibration
    probes + 500 subset (100 headwords x 5 arms) + 25 canary + 15
    score-check = 544.

Client contract reused verbatim from Uprava tools/jev_probe.py (H5275,
e63a872d17) — POST {state, model, questions:DICT}; `noul` carries REQUIRED
criteria {true,false}; 64k budget; $0.042/1M input, output free. Key:
TYPESAFE_API_KEY from ~/.secrets/typesafe.env — never echoed.

Usage:
  jev_defgen_rerank.py --build-subset       seeded stratified 100-headword
                                            subset off the frozen 500 (writes
                                            subset_100.tsv + subset_100.meta.json)
  jev_defgen_rerank.py --probe              1 live calibration call (synthetic)
  jev_defgen_rerank.py --run [--limit N]    subset run, resumable (jev_scores.jsonl)
  jev_defgen_rerank.py --canary             re-score 5 seeded items x 5 arms
  jev_defgen_rerank.py --score-check        3 seeded items x 5 arms, score primitive
  jev_defgen_rerank.py --analyze            metrics + baseline comparison
  jev_defgen_rerank.py --dry-run            build 3 requests, validate, no network

kosha data/eval/defgen is consumed READ-ONLY. Stdlib only; Python >= 3.9.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
DEFAULT_KOSHA = Path.home() / "Documents" / "GitHub" / "kosha" / "data" / "eval" / "defgen"
DEFAULT_UPRAVA_TOOLS = Path.home() / "Documents" / "GitHub" / "Uprava" / "tools"

ARMS = ["A0_random_floor", "A1_chat_ctx", "A2_chat_noctx", "A3_reasoner_ctx",
        "F1_fable_ctx"]
SEED = 730                 # frozen-sample seed; every derived draw keys off it
SUBSET_N = 100
CANARY_ITEMS = 5
SCORECHECK_ITEMS = 3
WORKERS = 8                # <=8 in flight (fence); API allows 1200 req/min
SCORES_OUT = HERE / "jev_scores.jsonl"       # primary noul arm, subset run
CANARY_OUT = HERE / "jev_canary.jsonl"       # stability re-run
SCORECHECK_OUT = HERE / "jev_score_check.jsonl"  # score-primitive control
SUBSET_TSV = HERE / "subset_100.tsv"
SUBSET_META = HERE / "subset_100.meta.json"
SUMMARY_OUT = HERE / "jev_summary.json"

# Adequacy levels mirror the baseline judge rubric verbatim (kosha
# defgen_score.py JUDGE_SYS). Used only by --score-check (the score primitive
# measured content-insensitive in batch form; single-question form is checked
# on a small control set for the record).
LEVELS = [
    "0 unrelated or empty: wrong meaning or nothing usable",
    "1 related domain but wrong meaning",
    "2 partially right: fragments of the sense, major errors or omissions",
    "3 core sense right, some senses missing or extra",
    "4 good coverage, only minor gaps",
    "5 covers the gold senses accurately",
]

NOUL_CRITERIA = {
    "true": "the candidate gloss conveys the gold meaning",
    "false": "the candidate gloss misses or contradicts the gold meaning",
}


# ---------------------------------------------------------------- jev client

def import_jev_probe():
    tools = Path(os.environ.get("UPRAVA_TOOLS", "") or DEFAULT_UPRAVA_TOOLS)
    p = tools / "jev_probe.py"
    if not p.exists():
        raise SystemExit(f"jev_probe.py not found at {p} (set UPRAVA_TOOLS)")
    spec = importlib.util.spec_from_file_location("jev_probe", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- data load

def load_sample(kosha: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with (kosha / "frozen_sample.tsv").open(encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            rows.append(dict(zip(header, line.rstrip("\n").split("\t"))))
    return rows


def load_attestations(kosha: Path) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    with (kosha / "attestations.jsonl").open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            out[r["slp1"]] = [s.get("sentence", "") for s in r.get("sentences", [])]
    return out


def load_gen(kosha: Path, arm: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    with (kosha / f"gen_{arm}.jsonl").open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            out[r["slp1"]] = r.get("gloss") or ""
    return out


def load_judge_baseline(kosha: Path) -> Dict[str, Dict[str, Optional[float]]]:
    """{slp1: {arm: adequacy}} — the frozen DeepSeek-chat judge scores."""
    out: Dict[str, Dict[str, Optional[float]]] = {}
    for arm in ARMS:
        with (kosha / f"judge_{arm}.jsonl").open(encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                out.setdefault(r["slp1"], {})[arm] = r.get("adequacy")
    return out


def load_chrf(kosha: Path) -> Dict[Tuple[str, str], float]:
    """{(slp1, arm): chrf} from the frozen per-item deterministic metrics."""
    out: Dict[Tuple[str, str], float] = {}
    with (kosha / "scores_per_item.tsv").open(encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        idx = {k: header.index(k) for k in ("slp1", "arm", "chrf")}
        for line in f:
            vals = line.rstrip("\n").split("\t")
            out[(vals[idx["slp1"]], vals[idx["arm"]])] = float(vals[idx["chrf"]])
    return out


# ---------------------------------------------------------------- subset

def build_subset(kosha: Path) -> List[Dict[str, str]]:
    """Seeded stratified SUBSET_N headwords off the frozen 500, proportional
    per freq x poly cell (largest-remainder), seed 730 family."""
    rows = load_sample(kosha)
    cells: Dict[Tuple[str, str], List[Dict[str, str]]] = {}
    for r in rows:
        cells.setdefault((r["freq_band"], r["poly_band"]), []).append(r)
    quota: Dict[Tuple[str, str], int] = {}
    raw: Dict[Tuple[str, str], float] = {}
    for cell, items in cells.items():
        raw[cell] = SUBSET_N * len(items) / len(rows)
        quota[cell] = int(raw[cell])
    remainder = SUBSET_N - sum(quota.values())
    for cell in sorted(raw, key=lambda c: raw[c] - quota[c], reverse=True)[:remainder]:
        quota[cell] += 1
    picked: List[Dict[str, str]] = []
    for cell in sorted(cells):
        rng = random.Random(f"h5279-subset:{SEED}:{'/'.join(cell)}")
        picked.extend(rng.sample(cells[cell], quota[cell]))
    picked.sort(key=lambda r: r["slp1"])
    with SUBSET_TSV.open("w", encoding="utf-8") as f:
        f.write("\t".join(["slp1", "iast", "grammar", "freq_band", "poly_band"])
                + "\n")
        for r in picked:
            f.write("\t".join([r["slp1"], r.get("iast", ""), r.get("grammar", ""),
                               r["freq_band"], r["poly_band"]]) + "\n")
    meta = {
        "subset_n": len(picked), "seed_family": f"h5279-subset:{SEED}",
        "from": "kosha data/eval/defgen frozen_sample.tsv (500, seed 730)",
        "quota_per_cell": {"/".join(c): quota[c] for c in sorted(quota)},
        "available_per_cell": {"/".join(c): len(v) for c, v in sorted(cells.items())},
        "generated": time.strftime("%Y-%m-%d"),
    }
    with SUBSET_META.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"subset: {len(picked)} headwords -> {SUBSET_TSV.name}")
    print(json.dumps(meta["quota_per_cell"], ensure_ascii=False))
    return picked


def load_subset(kosha: Path) -> List[Dict[str, str]]:
    if not SUBSET_TSV.exists():
        return build_subset(kosha)
    keep: Dict[str, Dict[str, str]] = {r["slp1"]: r for r in load_sample(kosha)}
    rows: List[Dict[str, str]] = []
    with SUBSET_TSV.open(encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            r = dict(zip(header, line.rstrip("\n").split("\t")))
            full = keep.get(r["slp1"], {})
            r["gold_gloss"] = full.get("gold_gloss", "")
            rows.append(r)
    return rows


# ---------------------------------------------------------------- requests

def cand_state(row: Dict[str, str], atts: List[str], cand: str) -> str:
    lines = [
        f"Headword (SLP1): {row['slp1']}",
        f"Headword (IAST): {row.get('iast', '')}",
        f"Grammar: {row.get('grammar', '')}",
        f"GOLD reference gloss (Monier-Williams 1899): {row['gold_gloss']}",
        "Corpus attestations (Digital Corpus of Sanskrit):",
    ]
    for i, s in enumerate(atts[:5], 1):
        lines.append(f"{i}. {s}")
    lines.append(f"Candidate gloss to judge: {cand}")
    return "\n".join(lines)


NOUL_QUESTION = (
    "Does the candidate gloss convey the same meaning as the GOLD reference "
    "gloss for this headword (sense coverage included, wording and "
    "formatting irrelevant; the gold text may contain OCR/markup debris)?")

SCORE_QUESTION = (
    "How faithful is the candidate gloss to the corpus sense of the headword "
    "as fixed by the GOLD reference gloss? Judge MEANING coverage only, "
    "never formatting.")


def build_cand_request(row: Dict[str, str], atts: List[str], cand: str,
                       model: str, primitive: str = "noul") -> Dict[str, Any]:
    """H5277-proven form: one call, one candidate in state, ONE question."""
    state = cand_state(row, atts, cand)
    if primitive == "noul":
        q: Dict[str, Any] = {"type": "noul", "question": NOUL_QUESTION,
                             "criteria": NOUL_CRITERIA}
    else:
        q = {"type": "score", "question": SCORE_QUESTION, "criteria": LEVELS}
    return {"state": state, "model": model, "questions": {"faithful": q}}


def build_probe_request(model: str) -> Dict[str, Any]:
    """Synthetic calibration: exact gold copy (noul -> 1.0) vs unrelated
    deranged gloss (noul -> 0.0) in the H5277 single-question form."""
    gold = ("to come near or towards; to arrive, approach; to reach, attain, "
            "enter; to get or fall into any state or condition")
    deranged = "relating to the handle of a plough; m. a kind of carriage pole"
    row = {"slp1": "AyA", "iast": "āyā", "grammar": "2.Ā.", "gold_gloss": gold}
    atts = ["so 'yam āyāti", "ratham āyāta"]
    req = build_cand_request(row, atts, gold, model, "noul")
    # two questions would leave the proven single-question form; do gold-copy
    # only, deranged via a second --probe invocation alternates via env
    which = os.environ.get("H5279_PROBE_CAND", "gold")
    cand = deranged if which == "deranged" else gold
    return build_cand_request(row, atts, cand, model, "noul")


# ---------------------------------------------------------------- run loop

def call_one(jev, req: Dict[str, Any], api_key: str, endpoint: str,
             retries: int = 3) -> Dict[str, Any]:
    ok, why = jev.validate_request(req)
    if not ok:
        return {"status": -1, "verdict": "CLIENT_INVALID", "body": {"error": why}}
    last: Dict[str, Any] = {}
    for attempt in range(retries):
        status, body = jev.call_jev(req, api_key, endpoint)
        verdict = jev.classify_result(status, body)
        last = {"status": status, "verdict": verdict, "body": body}
        if verdict == "OK":
            return last
        if verdict in ("TRANSPORT_ERROR", "HTTP_429", "HTTP_500", "HTTP_502",
                       "HTTP_503"):
            time.sleep(2.0 * (attempt + 1))
            continue
        return last  # shape/auth errors: no retry
    return last


def run_pairs(jev, pairs: List[Tuple[Dict[str, str], str]], atts, gens, model,
              api_key, endpoint, out_path: Path, primitive: str = "noul",
              label: str = "run") -> int:
    """pairs = [(row, arm)]; one resumable call per (slp1, arm)."""
    done: set = set()
    if out_path.exists():
        with out_path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    done.add((r["slp1"], r["arm"]))
                except (json.JSONDecodeError, KeyError):
                    continue
    todo = [(r, a) for r, a in pairs if (r["slp1"], a) not in done]
    print(f"{label} [{primitive}]: {len(done)} done, {len(todo)} to run -> "
          f"{out_path.name}")
    if not todo:
        return 0
    lock = threading.Lock()
    fout = out_path.open("a", encoding="utf-8")

    def work(pair):
        row, arm = pair
        cand = gens[arm].get(row["slp1"], "")
        req = build_cand_request(row, atts.get(row["slp1"], []), cand, model,
                                 primitive)
        res = call_one(jev, req, api_key, endpoint)
        rec = {"slp1": row["slp1"], "arm": arm, "model": model,
               "primitive": primitive,
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
        if res["verdict"] == "OK":
            body = res["body"]
            rec["status"] = res["status"]
            rec["answer"] = body.get("answers", {}).get("faithful", {})
            rec["usage"] = body.get("usage", {})
        else:
            rec["status"] = res["status"]
            rec["verdict"] = res["verdict"]
            rec["error"] = json.dumps(res.get("body", {}),
                                      ensure_ascii=False)[:500]
        with lock:
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fout.flush()
        return res["verdict"]

    verdicts = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for v in ex.map(work, todo):
            verdicts.append(v)
            if v != "OK":
                print(f"  FAIL: {v}", file=sys.stderr)
    n_ok = sum(v == "OK" for v in verdicts)
    fout.close()
    print(f"{label} [{primitive}]: {n_ok}/{len(todo)} OK")
    return len(todo) - n_ok


# ---------------------------------------------------------------- stats helpers

def rank_avg(xs: List[float]) -> List[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        r = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    return ranks


def spearman(a: List[float], b: List[float]) -> float:
    if len(a) != len(b) or len(a) < 2:
        return float("nan")
    ra, rb = rank_avg(a), rank_avg(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return num / (da * db) if da and db else float("nan")


def load_jev_scores(path: Path, primitive: Optional[str] = None
                    ) -> Dict[Tuple[str, str], Dict[str, Any]]:
    out: Dict[Tuple[str, str], Dict[str, Any]] = {}
    if not path.exists():
        return out
    with path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("verdict") is None and r.get("answer"):
                if primitive and r.get("primitive") != primitive:
                    continue
                out[(r["slp1"], r["arm"])] = r
    return out


def noul_value(rec: Dict[str, Any]) -> Optional[float]:
    n = rec.get("answer", {}).get("noul")
    return float(n) if isinstance(n, (int, float)) else None


def score_value(rec: Dict[str, Any]) -> Optional[float]:
    """Raw live score is 1-based continuous over the criteria list (probe:
    everything lands ~4.4/6 regardless of content); normalized = raw-1
    clamped, kept only for the score-check control record."""
    try:
        raw = float(rec.get("answer", {}).get("score"))
    except (TypeError, ValueError):
        return None
    return max(0.0, min(5.0, raw - 1.0))


# ---------------------------------------------------------------- analysis

def analyze(kosha: Path) -> Dict[str, Any]:
    subset = load_subset(kosha)
    subset_ids = {r["slp1"] for r in subset}
    baseline_all = load_judge_baseline(kosha)
    chrf = load_chrf(kosha)
    jev_scores = load_jev_scores(SCORES_OUT, "noul")

    def mean(xs):
        return sum(xs) / len(xs) if xs else float("nan")

    per_arm: Dict[str, Dict[str, List[float]]] = {
        arm: {"prim": [], "base": [], "chrf": []} for arm in ARMS}
    item_rhos: List[float] = []
    top1_hits = 0
    top1_n = 0
    top1_tie_hits = 0
    n_singleton = 0
    n_singleton_hit = 0
    for row in subset:
        slp1 = row["slp1"]
        bl = baseline_all.get(slp1, {})
        jv: Dict[str, float] = {}
        for arm in ARMS:
            rec = jev_scores.get((slp1, arm))
            if rec is None:
                continue
            v = noul_value(rec)
            if v is None:
                continue
            jv[arm] = v * 5.0  # noul 0-1 -> 0-5 adequacy scale
        for arm in ARMS:
            if arm in jv:
                per_arm[arm]["prim"].append(jv[arm])
            b = bl.get(arm)
            if isinstance(b, (int, float)):
                per_arm[arm]["base"].append(float(b))
            c = chrf.get((slp1, arm))
            if c is not None and arm in jv:
                per_arm[arm]["chrf"].append(c)
        keys = [a for a in ARMS if a in jv
                and isinstance(bl.get(a), (int, float))]
        if len(keys) >= 2:
            rho = spearman([jv[a] for a in keys], [float(bl[a]) for a in keys])
            if not math.isnan(rho):
                item_rhos.append(rho)
            jmax = max(keys, key=lambda a: jv[a])
            bvals = {a: float(bl[a]) for a in keys}
            bmax_set = {a for a in keys if bvals[a] == max(bvals.values())}
            top1_n += 1
            top1_tie_hits += jmax in bmax_set
            if len(bmax_set) == 1:
                n_singleton += 1
                n_singleton_hit += jmax in bmax_set

    arm_summary = {}
    for arm in ARMS:
        prim, chrf_l = per_arm[arm]["prim"], per_arm[arm]["chrf"]
        arm_summary[arm] = {
            "n": len(prim),
            "jev_mean_x5": round(mean(prim), 3),
            "baseline_mean": round(mean(per_arm[arm]["base"]), 3),
            "jev_spearman_vs_chrf": round(spearman(prim, chrf_l), 3)
            if len(chrf_l) == len(prim) and chrf_l else None,
            "baseline_spearman_vs_chrf_full500": None,  # from scores_summary
        }
    jev_rank = sorted(ARMS, key=lambda a: -mean(per_arm[a]["prim"]))
    base_rank = sorted(ARMS, key=lambda a: -mean(per_arm[a]["base"]))

    # frozen full-500 baseline judge~chrF for reference
    ss_path = kosha / "scores_summary.json"
    if ss_path.exists():
        with ss_path.open(encoding="utf-8") as f:
            base_full = json.load(f).get("judge", {})
        for arm in ARMS:
            arm_summary[arm]["baseline_spearman_vs_chrf_full500"] = base_full \
                .get(arm, {}).get("spearman_vs_chrf")

    usage_in_total = sum(int(r.get("usage", {}).get("input_tokens", 0) or 0)
                         for r in jev_scores.values())
    n_calls = len(jev_scores)
    cost_in = usage_in_total / 1_000_000 * 0.042

    summary: Dict[str, Any] = {
        "n_items": len({s for s, _ in jev_scores}),
        "n_calls": n_calls,
        "per_arm": arm_summary,
        "jev_arm_ranking": jev_rank,
        "baseline_arm_ranking": base_rank,
        "arm_ranking_match": jev_rank == base_rank,
        "per_item_spearman_vs_baseline": {
            "mean": round(mean(item_rhos), 4), "n": len(item_rhos)},
        "top1_agreement": {
            "tie_aware_rate": round(top1_tie_hits / top1_n, 4) if top1_n else None,
            "tie_aware_hits": top1_tie_hits, "n": top1_n,
            "strict_rate_where_baseline_singleton": round(
                n_singleton_hit / n_singleton, 4) if n_singleton else None,
            "n_baseline_singleton": n_singleton,
            "n_baseline_singleton_hit": n_singleton_hit,
            "note": "baseline adequacies are integers with frequent ties at 5; "
                    "tie_aware counts Jev's argmax inside the baseline max-set; "
                    "strict is conditioned on items where baseline has a "
                    "unique winner"},
        "floor_separation": {
            "jev": round(mean(per_arm["A1_chat_ctx"]["prim"])
                         - mean(per_arm["A0_random_floor"]["prim"]), 3),
            "baseline": round(mean(per_arm["A1_chat_ctx"]["base"])
                              - mean(per_arm["A0_random_floor"]["base"]), 3)},
        "cost": {
            "jev_input_tokens_total": usage_in_total,
            "jev_usd_total": round(cost_in, 6),
            "jev_usd_per_call": round(cost_in / n_calls, 6) if n_calls else None,
            "jev_usd_per_1000_candidates": round(
                cost_in / n_calls * 1000, 4) if n_calls else None,
            "note": "output free; $0.042/1M input (H5275 live-probed price); "
                    "1 call per (headword, arm) candidate — same billable "
                    "shape as the baseline judge",
        },
        "model": "jev-1.13.0",
        "primitive": "noul (single question per call, H5277 form)",
        "generated": time.strftime("%Y-%m-%d"),
    }

    # canary stability if present
    canary = load_jev_scores(CANARY_OUT, "noul")
    if canary:
        diffs, exact = [], 0
        for key, rec in canary.items():
            main = jev_scores.get(key)
            if not main:
                continue
            a, b = noul_value(main), noul_value(rec)
            if a is None or b is None:
                continue
            diffs.append(abs(a - b))
            exact += a == b
        summary["canary"] = {
            "n_calls": len(canary),
            "mean_abs_diff": round(mean(diffs), 4) if diffs else None,
            "exact_rate": round(exact / len(diffs), 4) if diffs else None,
        }

    # score-primitive control if present
    scheck = load_jev_scores(SCORECHECK_OUT, "score")
    if scheck:
        per_arm_s: Dict[str, List[float]] = {a: [] for a in ARMS}
        for (slp1, arm), rec in scheck.items():
            v = score_value(rec)
            if v is not None:
                per_arm_s[arm].append(v)
        summary["score_check_control"] = {
            arm: round(mean(v), 3) for arm, v in per_arm_s.items() if v}

    with SUMMARY_OUT.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"-> {SUMMARY_OUT.name}")
    return summary


# ---------------------------------------------------------------- main

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kosha", default=str(DEFAULT_KOSHA),
                    help="kosha data/eval/defgen dir (read-only)")
    ap.add_argument("--build-subset", action="store_true",
                    help=f"seeded stratified {SUBSET_N}-headword subset")
    ap.add_argument("--probe", action="store_true",
                    help="1 live calibration call (H5279_PROBE_CAND=gold|deranged)")
    ap.add_argument("--run", action="store_true",
                    help=f"subset run: {SUBSET_N} items x 5 arms, noul")
    ap.add_argument("--canary", action="store_true",
                    help=f"re-score {CANARY_ITEMS} seeded items x 5 arms")
    ap.add_argument("--score-check", action="store_true",
                    help=f"{SCORECHECK_ITEMS} seeded items x 5 arms, score primitive")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--limit", type=int, default=0,
                    help="limit run to first N subset items (smoke)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    kosha = Path(args.kosha)
    jev = import_jev_probe()

    if not any((args.build_subset, args.probe, args.run, args.canary,
                args.score_check, args.analyze, args.dry_run)):
        ap.error("nothing to do: pass --build-subset/--probe/--run/--canary/"
                 "--score-check/--analyze/--dry-run")

    rows = load_sample(kosha)
    atts = load_attestations(kosha)
    gens = {arm: load_gen(kosha, arm) for arm in ARMS}
    subset = load_subset(kosha)

    if args.dry_run:
        all_ok = True
        for row in subset[:2]:
            for primitive in ("noul", "score"):
                req = build_cand_request(
                    row, atts.get(row["slp1"], []),
                    gens["A1_chat_ctx"].get(row["slp1"], ""), jev.DEFAULT_MODEL,
                    primitive)
                ok, why = jev.validate_request(req)
                blob = json.dumps(req, ensure_ascii=False)
                print(f"{row['slp1']}/{primitive}: valid={ok} "
                      f"chars={len(blob)} {why}")
                all_ok = all_ok and ok
        return 0 if all_ok else 1

    api_key, model, endpoint = jev.resolve_config(argparse.Namespace(
        env_file=str(jev.DEFAULT_ENV_FILE)))
    if not api_key:
        print("FAIL: no TYPESAFE_API_KEY", file=sys.stderr)
        return 3

    if args.probe:
        req = build_probe_request(model)
        ok, why = jev.validate_request(req)
        print(f"probe request valid={ok} {why}")
        if not ok:
            return 1
        res = call_one(jev, req, api_key, endpoint)
        print(f"probe: status={res['status']} verdict={res['verdict']}")
        if res["verdict"] == "OK":
            for qid, ans in res["body"]["answers"].items():
                print(f"  {qid}: {jev.format_answer(ans)}")
            print(f"  usage: {res['body'].get('usage')} "
                  f"cost ${jev.cost_usd(res['body'].get('usage')):.6f}")
            return 0
        print(json.dumps(res.get("body", {}), ensure_ascii=False)[:1000])
        return 1

    if args.run:
        pairs = [(r, arm) for r in subset for arm in ARMS]
        if args.limit:
            pairs = [(r, a) for r in subset[:args.limit] for a in ARMS]
        n_fail = run_pairs(jev, pairs, atts, gens, model, api_key, endpoint,
                           SCORES_OUT, "noul", label="run")
        return 0 if n_fail == 0 else 1

    if args.canary:
        rng = random.Random(f"h5279-canary:{SEED}")
        picked = rng.sample([r["slp1"] for r in subset], CANARY_ITEMS)
        if CANARY_OUT.exists():
            CANARY_OUT.unlink()  # canary always re-runs fresh
        pairs = [(r, arm) for r in subset if r["slp1"] in picked for arm in ARMS]
        n_fail = run_pairs(jev, pairs, atts, gens, model, api_key, endpoint,
                           CANARY_OUT, "noul", label="canary")
        return 0 if n_fail == 0 else 1

    if args.score_check:
        rng = random.Random(f"h5279-scorecheck:{SEED}")
        picked = rng.sample([r["slp1"] for r in subset], SCORECHECK_ITEMS)
        if SCORECHECK_OUT.exists():
            SCORECHECK_OUT.unlink()
        pairs = [(r, arm) for r in subset if r["slp1"] in picked for arm in ARMS]
        n_fail = run_pairs(jev, pairs, atts, gens, model, api_key, endpoint,
                           SCORECHECK_OUT, "score", label="score-check")
        return 0 if n_fail == 0 else 1

    if args.analyze:
        analyze(kosha)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
