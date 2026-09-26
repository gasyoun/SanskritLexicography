#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h5279_jev_defgen_gloss_rerank.py — H5279: Jev re-rank of defgen candidate glosses.

Mission (Uprava/handoffs/H5279-OxAlpha_SanskritLexicography_jev-defgen-gloss-rerank_23.09.26.md):
on the frozen 500-headword kosha defgen sample, re-rank/judge the five frozen
arms' candidate glosses with TypeSafe «System One» Jev — ``state`` = headword +
corpus context (DCS attestation sentences) + ONE candidate gloss, one ``score``
question per candidate ("how faithful to the corpus sense is this gloss?").
Candidates are then ranked by that score: the ranking step under test.
Compare against the EXISTING LLM-judge baseline (``deepseek-chat`` adequacy 0-5
vs the MW gold gloss, ``kosha/data/eval/defgen/judge_<arm>.jsonl``) on accuracy
(per-item rank agreement + floor separation) and cost.

Design note (measured, not assumed). The first candidate design put ALL five
glosses in one state and asked five ``score`` questions in one call (mirroring
the H5277 shape). On an 8-item/arm=all probe it collapsed: every arm scored
~3.70, floor gap 0.011. The isolated-candidate design (state carries one gloss,
like the H730 baseline judge) separates the random floor by **+4.28** on the
same probe. The in-state ``noul`` and ``choice`` variants also failed (gap 0.001
and one constant winner). This file implements the design that measures; the
probe that chose it is committed as ``tools/h5279_jev_design_probe.py``.

This is a MEASUREMENT pass. No defgen lane is rewired: the gold gloss stays out
of the Jev state (Jev judges against the DCS corpus context, the baseline judge
against the MW gold — a different, harder signal); the verdict is only "does Jev
reproduce the baseline ranking step, and at what cost".

Reused, not rebuilt:
  * Uprava ``tools/jev_probe.py`` — the measured Jev client contract (dict-keyed
    questions, score criteria = list of 2-10 level strings, $0.042/1M input).
  * kosha ``data/eval/defgen/`` — frozen_sample.tsv, attestations.jsonl,
    gen_<arm>.jsonl, judge_<arm>.jsonl, scores_per_item.tsv (read-only).
  * the sibling H5277 bench (Uprava ``tools/bench_recall_jev_rerank.py``) — the
    concurrent-calls + resumable-JSONL + dated-report shape.

Modes:
  --selftest   offline controls (no network): loaders, gold-leak fence,
               determinism, metrics, request-shape validation
  --smoke N    live, first N sample items (5 calls each, resumable)
  --run        live, full frozen sample (resumable JSONL)
  --analyze    read the scores + baseline -> per-item JSON + aggregate JSON + MD

Requires TYPESAFE_API_KEY in ~/.secrets/typesafe.env. Python >= 3.9.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import io
import json
import math
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GH = os.path.dirname(REPO)
KOSHA = os.path.join(GH, "kosha")
KDATA = os.path.join(KOSHA, "data", "eval", "defgen")
UPRAVA_TOOLS = os.path.join(GH, "Uprava", "tools")
if UPRAVA_TOOLS not in sys.path:
    sys.path.insert(0, UPRAVA_TOOLS)
try:
    import jev_probe as jp  # noqa: E402  (H5275 measured client contract)
except ImportError as exc:  # pragma: no cover
    raise SystemExit("BLOCKER: Uprava tools/jev_probe.py not importable: %s" % exc)

FROZEN = os.path.join(KDATA, "frozen_sample.tsv")
ATT = os.path.join(KDATA, "attestations.jsonl")
PER_ITEM_CHRF = os.path.join(KDATA, "scores_per_item.tsv")
OUT = os.path.join(REPO, "data", "defgen_jev_rerank")
RAW = os.path.join(OUT, "jev_scores_raw.jsonl")
PER_ITEM = os.path.join(OUT, "jev_per_item.json")
AGG = os.path.join(OUT, "jev_rerank_aggregate.json")
REPORT_MD = os.path.join(REPO, "data", "DEFGEN_JEV_RERANK_REPORT_%s.md")
REPORT_DATE = "2026-09-24"

ARMS = ["A0_random_floor", "A1_chat_ctx", "A2_chat_noctx", "A3_reasoner_ctx",
        "F1_fable_ctx"]
SYSTEM_ARMS = [a for a in ARMS if a != "A0_random_floor"]
SEED = 5279
MAX_ATT = 5
POOL_DEPTH = 10          # concurrent live calls (H5277 used 10)
TIMEOUT_S = 180.0
CAND_QUESTION = ("How faithful is this candidate gloss to the sense of the "
                 "Sanskrit headword as used in the corpus context above?")
LEVELS = [
    "0 not faithful: unrelated to the headword's meaning",
    "1 related domain but wrong meaning",
    "2 weak: mostly wrong sense",
    "3 core sense right, senses missing or extra",
    "4 good: covers the sense in context, minor gap",
    "5 fully faithful to the sense in the corpus context",
]

_lock = threading.Lock()


# ----------------------------------------------------------------- loaders
def _read_tsv(path):
    rows = []
    with io.open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(header):
                parts += [""] * (len(header) - len(parts))
            rows.append(dict(zip(header, parts)))
    return rows


def load_frozen():
    return _read_tsv(FROZEN)


def load_attestations():
    out = {}
    with io.open(ATT, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            out[r["slp1"]] = [s.get("text", "") for s in r.get("sentences", [])]
    return out


def load_gen():
    out = {}
    for arm in ARMS:
        path = os.path.join(KDATA, "gen_%s.jsonl" % arm)
        d = {}
        with io.open(path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                d[r["slp1"]] = (r.get("gloss") or "").strip()
        out[arm] = d
    return out


def load_judge():
    out = {}
    for arm in ARMS:
        path = os.path.join(KDATA, "judge_%s.jsonl" % arm)
        d = {}
        with io.open(path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                d[r["slp1"]] = r.get("adequacy")
        out[arm] = d
    return out


def load_chrf():
    out = collections.defaultdict(dict)
    for r in _read_tsv(PER_ITEM_CHRF):
        out[r["slp1"]][r["arm"]] = float(r["chrf"])
    return out


# ------------------------------------------------------------- state / prompts
def build_state(row, atts, candidate_gloss):
    sents = [s for s in atts.get(row["slp1"], []) if s.strip()][:MAX_ATT]
    lines = [
        "Sanskrit headword: %s (SLP1: %s). Grammar: %s." % (
            row["iast"], row["slp1"], row.get("grammar", "?")),
        "",
        "Corpus context — Digital Corpus of Sanskrit attestation sentences "
        "showing the sense in use:",
    ]
    for i, s in enumerate(sents, 1):
        lines.append("  %d. %s" % (i, s))
    lines.append("")
    lines.append("Candidate English gloss for this headword: %s"
                 % (candidate_gloss or "(empty)"))
    return "\n".join(lines)


def build_request(row, atts, candidate_gloss, model):
    return {"state": build_state(row, atts, candidate_gloss),
            "model": model,
            "questions": {"faith": jp._score(CAND_QUESTION, LEVELS)}}


def parse_answer(ans, n_levels=len(LEVELS)):
    """(score, level, confidence, legend_key). score = raw continuous value."""
    score = ans.get("score")
    if not isinstance(score, (int, float)):
        return None, None, None, None
    legend = ans.get("legend")
    lk = None
    if isinstance(legend, dict) and len(legend) == 1:
        k = next(iter(legend))
        if str(k).isdigit() and 1 <= int(k) <= n_levels:
            lk = int(k)
    level = (lk - 1) if lk else max(0, min(n_levels - 1, int(round(score))))
    return float(score), level, ans.get("confidence"), lk


# ------------------------------------------------------------------- scoring
def score_task(row, arm, atts, gen, cfg, timeout_s=TIMEOUT_S):
    req = build_request(row, atts, gen[arm].get(row["slp1"], ""), cfg[1])
    ok, why = jp.validate_request(req)
    base = {"slp1": row["slp1"], "arm": arm}
    if not ok:
        base.update({"status": "REQ_INVALID", "error": why})
        return base
    t = time.monotonic()
    status, body = jp.call_jev(req, cfg[0], cfg[2], timeout_s=timeout_s)
    ms = (time.monotonic() - t) * 1000
    cls = jp.classify_result(status, body)
    base.update({"status": cls, "http": status, "ms": round(ms),
                 "state_chars": len(req["state"])})
    if cls != "OK":
        base["error"] = json.dumps(body, ensure_ascii=False)[:400]
        return base
    ans = (body.get("answers") or {}).get("faith")
    if not isinstance(ans, dict):
        base.update({"status": "ANSWER_MISSING",
                     "error": json.dumps(body, ensure_ascii=False)[:300]})
        return base
    score, level, conf, lk = parse_answer(ans)
    if score is None:
        base.update({"status": "ANSWER_UNPARSED",
                     "error": json.dumps(ans, ensure_ascii=False)[:300]})
        return base
    usage = body.get("usage") or {}
    base.update({"score": score, "level": level, "conf": conf, "legend_key": lk,
                 "usage": usage, "cost_usd": jp.cost_usd(usage)})
    return base


def load_raw():
    """{(slp1, arm): rec} for OK rows; full row list for diagnostics."""
    done, rows = {}, []
    if os.path.exists(RAW):
        with io.open(RAW, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                rows.append(r)
                if r.get("status") == "OK":
                    done[(r["slp1"], r["arm"])] = r
    return done, rows


def run_live(rows, atts, gen, cfg, workers, limit=0, smoke=0):
    os.makedirs(OUT, exist_ok=True)
    done, _ = load_raw()
    todo_rows = rows[:limit] if limit else rows
    if smoke:
        todo_rows = todo_rows[:smoke]
    todo = [(r, a) for r in todo_rows for a in ARMS
            if (r["slp1"], a) not in done]
    print("jev rerank: %d candidate scores done, %d to run (%d items x %d arms), "
          "%d workers" % (len(done), len(todo), len(todo_rows), len(ARMS), workers))
    if not todo:
        return 0
    fh = io.open(RAW, "a", encoding="utf-8", newline="\n")

    def work(task):
        row, arm = task
        rec = score_task(row, arm, atts, gen, cfg)
        with _lock:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
        return rec

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(work, todo))
    fh.close()
    classes = collections.Counter(r.get("status") for r in results)
    in_tok = sum((r.get("usage") or {}).get("input_tokens", 0) or 0
                 for r in results)
    ms = [r["ms"] for r in results if isinstance(r.get("ms"), (int, float))]
    print("done: %s | input_tokens %d | $%.5f | mean call %.0f ms" % (
        dict(classes), in_tok, in_tok / 1e6 * jp.PRICE_PER_1M_INPUT_USD,
        (sum(ms) / len(ms)) if ms else 0))
    return 0 if classes.get("OK", 0) > 0 else 1


# -------------------------------------------------------------------- metrics
def kendall_tau_b(x, y):
    n = len(x)
    conc = disc = tx = ty = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx, dy = x[i] - x[j], y[i] - y[j]
            if dx == 0 and dy == 0:
                tx += 1
                ty += 1
            elif dx == 0:
                tx += 1
            elif dy == 0:
                ty += 1
            elif dx * dy > 0:
                conc += 1
            else:
                disc += 1
    den = math.sqrt((conc + disc + tx) * (conc + disc + ty))
    return (conc - disc) / den if den else float("nan")


def _ranks(xs):
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


def spearman(a, b):
    ra, rb = _ranks(a), _ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return num / (da * db) if da and db else float("nan")


def argmax_det(vals):
    """argmax over ARMS with deterministic first-in-ARMS-order tiebreak."""
    best = None
    for arm in ARMS:
        v = vals.get(arm)
        if v is None:
            continue
        if best is None or v > vals[best]:
            best = arm
    return best


def load_scores():
    """{slp1: {arm: rec}} for OK rows."""
    done, _ = load_raw()
    by_item = collections.defaultdict(dict)
    for (slp1, arm), rec in done.items():
        by_item[slp1][arm] = rec
    return by_item


def analyze(rows, gen, judge, chrf):
    by_item = load_scores()
    items = []
    for row in rows:
        k = row["slp1"]
        recs = by_item.get(k, {})
        if len(recs) != len(ARMS):
            continue
        jv = {a: recs[a]["score"] for a in ARMS}
        bv = {a: judge[a][k] for a in ARMS
              if isinstance(judge[a].get(k), (int, float))}
        cv = {a: chrf[k].get(a) for a in ARMS if a in chrf.get(k, {})}
        item = {
            "slp1": k, "iast": row["iast"],
            "freq_band": row.get("freq_band"), "poly_band": row.get("poly_band"),
            "jev": {a: round(jv[a], 3) for a in ARMS},
            "jev_level": {a: recs[a]["level"] for a in ARMS},
            "judge": bv,
            "chrf": {a: round(cv[a], 2) for a in cv},
            "top1_jev": argmax_det(jv),
        }
        j_vec = [jv[a] for a in ARMS]
        if len(bv) == len(ARMS):
            b_vec = [bv[a] for a in ARMS]
            tau = kendall_tau_b(j_vec, b_vec)
            item["tau_jev_judge"] = None if math.isnan(tau) else round(tau, 4)
            item["top1_judge"] = argmax_det(bv)
            item["top1_agree"] = int(item["top1_jev"] == item["top1_judge"])
        if len(cv) == len(ARMS):
            c_vec = [cv[a] for a in ARMS]
            tau = kendall_tau_b(j_vec, c_vec)
            item["tau_jev_chrf"] = None if math.isnan(tau) else round(tau, 4)
            item["top1_chrf"] = argmax_det(cv)
            item["top1_agree_chrf"] = int(item["top1_jev"] == item["top1_chrf"])
        items.append(item)

    agg = collections.defaultdict(dict)
    for arm in ARMS:
        js = [it["jev"][arm] for it in items]
        bs = [it["judge"][arm] for it in items
              if isinstance(it["judge"].get(arm), (int, float))]
        cs = [it["chrf"][arm] for it in items if arm in it["chrf"]]
        agg["jev_mean"][arm] = round(sum(js) / len(js), 4) if js else None
        agg["jev_n"][arm] = len(js)
        agg["judge_mean"][arm] = round(sum(bs) / len(bs), 4) if bs else None
        agg["chrf_mean"][arm] = round(sum(cs) / len(cs), 2) if cs else None
        pair = [(it["jev"][arm], it["judge"][arm]) for it in items
                if isinstance(it["judge"].get(arm), (int, float))]
        agg["spearman_jev_judge"][arm] = (
            round(spearman([p[0] for p in pair], [p[1] for p in pair]), 4)
            if len(pair) > 2 else None)
        pairc = [(it["jev"][arm], it["chrf"][arm]) for it in items
                 if arm in it["chrf"]]
        agg["spearman_jev_chrf"][arm] = (
            round(spearman([p[0] for p in pairc], [p[1] for p in pairc]), 4)
            if len(pairc) > 2 else None)

    def _finite(xs):
        return [v for v in xs if v is not None and not math.isnan(v)]

    taus_j = _finite([it["tau_jev_judge"] for it in items if "tau_jev_judge" in it])
    taus_c = _finite([it["tau_jev_chrf"] for it in items if "tau_jev_chrf" in it])
    agree = [it["top1_agree"] for it in items if "top1_agree" in it]
    agree_c = [it["top1_agree_chrf"] for it in items if "top1_agree_chrf" in it]
    n_const_judge = sum(
        1 for it in items
        if "tau_jev_judge" in it and it["tau_jev_judge"] is None)

    _done, all_rows = load_raw()
    ok = [r for r in all_rows if r.get("status") == "OK"]
    in_tok = sum((r.get("usage") or {}).get("input_tokens", 0) or 0 for r in ok)
    out_tok = sum((r.get("usage") or {}).get("output_tokens", 0) or 0 for r in ok)
    ms = [r["ms"] for r in ok if isinstance(r.get("ms"), (int, float))]

    # baseline judge cost: reconstruct the exact H730 judge prompt for the same
    # 2500 (arm, item) pairs and price it at the historical deepseek-chat rate
    # (H1210 arm-B note: 0.27 in / 1.10 out per 1M, 11-07-2026).
    base_chars = 2500 * 500  # JUDGE_SYS per call
    for row in rows:
        k = row["slp1"]
        for arm in ARMS:
            base_chars += (len(gen[arm].get(k, "")) + len(row["gold_gloss"])
                           + len(k) + 120)
    base_in_tok = base_chars / 4.0

    result = {
        "meta": {
            "handoff": "H5279",
            "date": REPORT_DATE,
            "model": "jev-1.13.0 (TypeSafe System One)",
            "endpoint": "https://api.typesafe.ai/v1/systemone",
            "sample": "kosha frozen defgen sample (seed 730, n=%d)" % len(rows),
            "scored_items": len(items),
            "candidate_arms": ARMS,
            "candidate_calls": len(ok),
            "state": "headword + grammar + <=%d DCS attestation sentences + ONE "
                     "candidate gloss (gold gloss NOT in state)" % MAX_ATT,
            "question": "score per candidate: how faithful to the corpus sense "
                        "(6-level 0-5 list), one call per candidate (isolated)",
            "baseline": "deepseek-chat adequacy 0-5 vs MW gold gloss "
                        "(kosha judge_<arm>.jsonl, H730)",
            "design_probe": "8 high-freq items: all-candidates-in-one-state "
                            "score -> floor gap 0.011; isolated-candidate score "
                            "-> floor gap +4.283 (tools/h5279_jev_design_probe.py)",
            "seed": SEED,
        },
        "jev_mean": agg["jev_mean"],
        "judge_mean": agg["judge_mean"],
        "chrf_mean": agg["chrf_mean"],
        "spearman_jev_judge": agg["spearman_jev_judge"],
        "spearman_jev_chrf": agg["spearman_jev_chrf"],
        "rank_agreement": {
            "tau_jev_judge_mean": round(sum(taus_j) / len(taus_j), 4) if taus_j else None,
            "tau_jev_chrf_mean": round(sum(taus_c) / len(taus_c), 4) if taus_c else None,
            "top1_agree_judge": ("%d/%d" % (sum(agree), len(agree))) if agree else None,
            "top1_agree_chrf": ("%d/%d" % (sum(agree_c), len(agree_c))) if agree_c else None,
            "items_with_constant_judge_row": n_const_judge,
            "note": "Kendall τ-b is undefined (NaN) on an item whose baseline "
                    "judge row is constant (all five arms the same adequacy); "
                    "such items are excluded from the τ means and counted "
                    "above — they also bound the per-item top-1 agreement.",
        },
        "arm_ranking": {
            "jev": sorted(ARMS, key=lambda a: -(agg["jev_mean"].get(a) or -1)),
            "judge": sorted(ARMS, key=lambda a: -(agg["judge_mean"].get(a) or -1)),
            "chrf": sorted(ARMS, key=lambda a: -(agg["chrf_mean"].get(a) or -1)),
        },
        "floor_separation": {
            "jev": {
                "A0": agg["jev_mean"].get("A0_random_floor"),
                "systems_mean": round(sum(agg["jev_mean"][a] for a in SYSTEM_ARMS)
                                      / len(SYSTEM_ARMS), 4),
                "gap": round(sum(agg["jev_mean"][a] for a in SYSTEM_ARMS)
                             / len(SYSTEM_ARMS) - agg["jev_mean"]["A0_random_floor"], 4),
            },
            "judge": {
                "A0": agg["judge_mean"].get("A0_random_floor"),
                "systems_mean": round(sum(agg["judge_mean"][a] for a in SYSTEM_ARMS)
                                      / len(SYSTEM_ARMS), 4),
                "gap": round(sum(agg["judge_mean"][a] for a in SYSTEM_ARMS)
                             / len(SYSTEM_ARMS) - agg["judge_mean"]["A0_random_floor"], 4),
            },
        },
        "cost": {
            "jev": {"calls": len(ok), "input_tokens": in_tok,
                    "output_tokens": out_tok,
                    "usd": round(in_tok / 1e6 * jp.PRICE_PER_1M_INPUT_USD, 5)},
            "baseline_judge_reconstructed": {
                "calls": 2500, "est_input_tokens": int(base_in_tok),
                "usd": round(base_in_tok / 1e6 * 0.27, 4),
                "rate": "deepseek-chat 0.27/1M in (H1210 arm-B historical note)",
                "note": "the historical run's usage was not recorded; the prompt "
                        "is reconstructed from the committed judge template and "
                        "priced at the H1210-documented rate"},
            "latency_ms": {"call_mean": round(sum(ms) / len(ms)) if ms else None,
                           "call_p50": round(sorted(ms)[len(ms) // 2]) if ms else None},
        },
    }
    bcost = result["cost"]["baseline_judge_reconstructed"]["usd"]
    result["verdict"] = {
        "arm_ranking_identical": (result["arm_ranking"]["jev"]
                                  == result["arm_ranking"]["judge"]),
        "floor_separated": result["floor_separation"]["jev"]["gap"] > 1.0,
        "cheaper_than_baseline": result["cost"]["jev"]["usd"] < bcost,
    }
    result["verdict"]["go"] = all(result["verdict"][k] for k in
                                  ("arm_ranking_identical", "floor_separated",
                                   "cheaper_than_baseline"))
    os.makedirs(OUT, exist_ok=True)
    with io.open(AGG, "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with io.open(PER_ITEM, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"items": items}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return result


def render_md(res, rows):
    r = res
    L = []
    L.append("# H5279 — Jev gloss re-rank on the frozen defgen sample")
    L.append("")
    L.append("_Created: %s · Last updated: %s_" % (r["meta"]["date"], r["meta"]["date"]))
    L.append("")
    L.append("**Handoff:** H5279 (OxAlpha) · **Executor:** OxAlpha "
             "(opencode/z-ai/glm-5.3-flash) · **Model:** %s" % r["meta"]["model"])
    L.append("")
    L.append("## What was measured")
    L.append("")
    L.append("- **Sample:** %s — scored **%d/%d** headwords "
             "(**%d** candidate calls)." % (
                 r["meta"]["sample"], r["meta"]["scored_items"], len(rows),
                 r["meta"]["candidate_calls"]))
    L.append("- **Jev state:** %s." % r["meta"]["state"])
    L.append("- **Jev question:** %s." % r["meta"]["question"])
    L.append("- **Baseline:** %s." % r["meta"]["baseline"])
    L.append("- **Measurement-only:** no lane is rewired. The Jev arm judges "
             "against the DCS corpus context, the baseline judge against the MW "
             "gold gloss — the comparison asks *does Jev reproduce the ranking "
             "step, and at what cost*, never which is more correct.")
    L.append("")
    L.append("### Design probe (why this shape)")
    L.append("")
    L.append("- %s." % r["meta"]["design_probe"])
    L.append("- The all-candidates-in-one-state shape (mirroring the H5277 "
             "rerank) collapses on this task: with a shared state the model "
             "hedges every candidate near 3.7 regardless of arm, so the random "
             "floor is not separated. The isolated-candidate shape used here is "
             "the one that measures.")
    L.append("")
    L.append("## Arm scores (mean per candidate, 0–5)")
    L.append("")
    L.append("| Arm | Jev 0–5 | baseline judge 0–5 | chrF-MW |")
    L.append("|---|---|---|---|")
    for a in ARMS:
        L.append("| %s | %s | %s | %s |" % (
            a, r["jev_mean"].get(a), r["judge_mean"].get(a),
            r["chrf_mean"].get(a)))
    L.append("")
    a0j = r["floor_separation"]["jev"]
    a0b = r["floor_separation"]["judge"]
    L.append("- **Floor separation** — Jev: A0 %s vs systems %s (**gap %s**); "
             "baseline judge: A0 %s vs systems %s (gap %s)."
             % (a0j["A0"], a0j["systems_mean"], a0j["gap"],
                a0b["A0"], a0b["systems_mean"], a0b["gap"]))
    L.append("")
    L.append("## Rank agreement")
    L.append("")
    ra = r["rank_agreement"]
    L.append("- Mean per-item Kendall τ-b Jev vs baseline judge: **%s** "
             "(vs chrF: %s)" % (ra["tau_jev_judge_mean"], ra["tau_jev_chrf_mean"]))
    L.append("- Per-item top-1 agreement: **%s** vs baseline judge, **%s** vs "
             "chrF (%d/500 items carry a constant baseline-judge row, where no "
             "ranking is defined — that caps the judge agreement)."
             % (ra["top1_agree_judge"], ra["top1_agree_chrf"],
                ra["items_with_constant_judge_row"]))
    L.append("- Per-arm Spearman ρ (Jev score vs baseline adequacy): %s"
             % ", ".join("%s %s" % (a, r["spearman_jev_judge"].get(a))
                         for a in ARMS))
    L.append("- Arm ranking (best→worst) — Jev: %s; judge: %s; chrF: %s"
             % (" > ".join(r["arm_ranking"]["jev"]),
                " > ".join(r["arm_ranking"]["judge"]),
                " > ".join(r["arm_ranking"]["chrf"])))
    L.append("")
    L.append("## Cost + latency")
    L.append("")
    jc = r["cost"]["jev"]
    bc = r["cost"]["baseline_judge_reconstructed"]
    L.append("| arm | calls | input tokens | cost |")
    L.append("|---|---|---|---|")
    L.append("| Jev (measured) | %d | %s | $%s |"
             % (jc["calls"], f"{jc['input_tokens']:,}", jc["usd"]))
    L.append("| baseline judge (reconstructed, priced at %s) | %d | ~%s | ~$%s |"
             % (bc["rate"], bc["calls"], f"{bc['est_input_tokens']:,}", bc["usd"]))
    L.append("")
    L.append("- Jev per-call latency: mean %s ms, p50 %s ms."
             % (r["cost"]["latency_ms"]["call_mean"],
                r["cost"]["latency_ms"]["call_p50"]))
    L.append("- Per 500-headword pass: Jev $%s vs baseline ~$%s "
             "(%sx)." % (jc["usd"], bc["usd"],
                         round(bc["usd"] / jc["usd"], 1) if jc["usd"] else "n/a"))
    L.append("")
    L.append("## Verdict")
    L.append("")
    v = r["verdict"]
    L.append("| check | value |")
    L.append("|---|---|")
    L.append("| arm ranking identical to baseline | %s |" % v["arm_ranking_identical"])
    L.append("| A0 floor separated (gap > 1.0) | %s |" % v["floor_separated"])
    L.append("| cheaper than the baseline judge | %s |" % v["cheaper_than_baseline"])
    L.append("| **GO** (all three) | **%s** |" % v["go"])
    L.append("")
    if v["go"]:
        L.append("**GO** — Jev reproduces the baseline judge's arm ranking on the "
                 "frozen sample, separates the random floor, and costs less per "
                 "pass. Replacing the defgen ranking step with Jev is a "
                 "legitimate *future* unit; this report rewires nothing.")
    else:
        L.append("**Measurement-only / NO-GO** — not all three checks are green, "
                 "so the defgen ranking step stays with the LLM judge. The "
                 "per-check rows above name which condition failed.")
    L.append("")
    L.append("## Checks")
    L.append("")
    L.append("```")
    L.append("python tools/h5279_jev_defgen_gloss_rerank.py --selftest   # offline")
    L.append("python tools/h5279_jev_defgen_gloss_rerank.py --run        # live, resumable")
    L.append("python tools/h5279_jev_defgen_gloss_rerank.py --analyze    # report")
    L.append("```")
    L.append("")
    L.append("Artifacts: `data/defgen_jev_rerank/jev_per_item.json` (per-item "
             "scores), `jev_rerank_aggregate.json` (aggregate), this report, "
             "`tools/h5279_jev_design_probe.py` (the design probe).")
    L.append("")
    L.append("_Гасунс_")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ selftest
def selftest():
    rows = load_frozen()
    atts = load_attestations()
    gen = load_gen()
    judge = load_judge()
    assert len(rows) == 500, len(rows)
    assert set(gen) == set(ARMS)
    for arm in ARMS:
        assert len(gen[arm]) >= 500, arm
        assert len(judge[arm]) >= 500, arm
    row = rows[0]
    for arm in ARMS:
        state = build_state(row, atts, gen[arm].get(row["slp1"], ""))
        assert row["gold_gloss"][:25] not in state, "GOLD LEAK in the Jev state"
        assert row["iast"] in state and row["slp1"] in state
        assert gen[arm][row["slp1"]] in state or not gen[arm].get(row["slp1"])
        assert "Candidate English gloss for this headword" in state
    req = build_request(row, atts, gen["A1_chat_ctx"][row["slp1"]], "jev-1.13.0")
    ok, why = jp.validate_request(req)
    assert ok, why
    assert set(req["questions"]) == {"faith"}
    q = req["questions"]["faith"]
    assert q["type"] == "score" and isinstance(q["criteria"], list)
    assert 2 <= len(q["criteria"]) <= 10
    assert kendall_tau_b([1, 2, 3], [1, 2, 3]) == 1.0
    assert kendall_tau_b([1, 2, 3], [3, 2, 1]) == -1.0
    assert abs(spearman([1, 2, 3, 4], [1, 2, 3, 4]) - 1.0) < 1e-9
    s, lv, cf, lk = parse_answer(
        {"type": "score", "score": 4.2, "legend": {"5": "fully"}, "confidence": 0.8})
    assert s == 4.2 and lv == 4 and lk == 5
    assert argmax_det({"A0_random_floor": 1, "A1_chat_ctx": 1}) == "A0_random_floor"
    assert argmax_det({"A0_random_floor": 1, "A1_chat_ctx": 2}) == "A1_chat_ctx"
    print("selftest: H5279 jev-defgen-rerank offline controls PASS "
          "(500 items, gold-leak fence, determinism, metrics, request shape)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--smoke", type=int, default=0, help="live: first N items")
    ap.add_argument("--run", action="store_true", help="live: full sample")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=POOL_DEPTH)
    ap.add_argument("--env-file", default=str(jp.DEFAULT_ENV_FILE))
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    rows = load_frozen()
    if args.analyze:
        atts = load_attestations()
        gen = load_gen()
        res = analyze(rows, gen, load_judge(), load_chrf())
        with io.open(REPORT_MD % REPORT_DATE, "w", encoding="utf-8", newline="\n") as f:
            f.write(render_md(res, rows))
        print("verdict=%s | ranking identical=%s | tau_judge=%s | top1 %s | "
              "floor gap %s | $%s" % (
                  res["verdict"]["go"], res["verdict"]["arm_ranking_identical"],
                  res["rank_agreement"]["tau_jev_judge_mean"],
                  res["rank_agreement"]["top1_agree_judge"],
                  res["floor_separation"]["jev"]["gap"],
                  res["cost"]["jev"]["usd"]))
        return 0

    ns = argparse.Namespace(env_file=args.env_file)
    cfg = jp.resolve_config(ns)
    if not cfg[0]:
        print("BLOCKER: TYPESAFE_API_KEY missing", file=sys.stderr)
        return 2
    atts = load_attestations()
    gen = load_gen()
    if args.smoke:
        return run_live(rows, atts, gen, cfg, args.workers, smoke=args.smoke)
    if args.run or args.limit:
        return run_live(rows, atts, gen, cfg, args.workers, limit=args.limit)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
