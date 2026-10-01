#!/usr/bin/env python3
"""bench_defgen_jev_gloss_judge.py — H5279 Jev gloss judge/re-rank on the defgen sample.

Mission (H5279, Uprava registry): on the frozen 500-headword defgen sample
(kosha data/eval/defgen, F48), Jev judges candidate glosses — state = headword
+ context (gold gloss + DCS attestations) + candidate list — scoring "how
faithful to the corpus sense is this gloss" 0–5, blinded to arm exactly like
the baseline judge (deepseek-chat, kosha DEFGEN_MW_GLOSS_EVAL_PROTOCOL §track-a).
Compare vs the existing LLM-judge baseline on accuracy + cost. Replace the
ranking step only if Jev matches-or-beats the baseline at lower cost;
measurement-only otherwise. Dated report.

Baseline gates mirrored (protocol §track-a): (1) per-arm Spearman ρ of judge
score vs chrF, (2) separation of the A0_random_floor arm, (3) arm-mean ranking
agreement Jev vs baseline. Verdict: GO-for-rerank only if pairwise agreement
ρ >= 0.70 AND floor separation AND arm-rank ρ >= 0.80 AND cost < baseline;
durable KEEP-BASELINE otherwise (same verdict shape as H5274/H5280 NO-GO).

Data (read-only, all frozen 09/2026):
  frozen_sample.tsv   slp1 iast grammar ... n_attest gold_gloss   (500 rows)
  attestations.jsonl  {slp1, dcs_lemma_id, sentences:[{sent_id,text,work}]}
  gen_<ARM>.jsonl     {slp1, arm, gloss, model, raw}              (5 arms)
  judge_<ARM>.jsonl   {slp1, arm, adequacy}   baseline judge 0–5  (5 arms)
  scores_per_item.tsv slp1 freq_band poly_band arm bleu chrf token_f1 empty

Fences: defgen data is public-domain MW glosses + DCS citations — no 152-FZ
surface is touched; zero prod writes; read-only over sibling clones.

Usage:
  bench_defgen_jev_gloss_judge.py --selftest   (offline: metrics + assembly)
  bench_defgen_jev_gloss_judge.py --smoke      (1 headword, live, print raw)
  bench_defgen_jev_gloss_judge.py              (full 500 -> reports/)
Key: TYPESAFE_API_KEY from ~/.secrets/typesafe.env (jev_probe.resolve_config).
Client: Uprava tools/jev_probe.py (H5275) via --uprava-tools, default the
sibling clone ../Uprava/tools. Python >= 3.9.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

ARMS = ["A0_random_floor", "A1_chat_ctx", "A2_chat_noctx",
        "A3_reasoner_ctx", "F1_fable_ctx"]
LABELS = ["A", "B", "C", "D", "E"]  # blinded: labels carry no arm names
LEVELS = ["0", "1", "2", "3", "4", "5"]
JUDGE_QUESTION = ("How faithful is candidate {label} to the corpus sense of "
                  "the headword, judged against the gold gloss and the "
                  "attestations? Score adequacy {range} (0 = unrelated/wrong "
                  "sense, 5 = fully faithful), judging meaning and ignoring "
                  "gold-side markup debris.")
MAX_ATTEST = 5
MAX_ATTEST_CHARS = 220
WORKERS_DEFAULT = 6
RETRY_CLASSES = ("TRANSPORT_ERROR", "HTTP_429", "HTTP_500", "HTTP_502",
                 "HTTP_503", "HTTP_504")
RETRIES = 3
# Baseline deepseek-chat judge cost estimate input price ($/1M tokens):
# Sept-2026 list-price ASSUMPTION for the estimate column only, flagged in the
# report — Jev side is always measured from live usage, never assumed.
DEEPSEEK_IN_PER_1M_USD = 0.28
EST_BASELINE_STATE_TOKENS = 1200

REPORT_TAG = "2026-09-24"
# verdict thresholds (locked in the docstring before the run)
AGREE_RHO_MIN = 0.70
ARMRANK_RHO_MIN = 0.80


# --- data loading ----------------------------------------------------------

def load_frozen(defgen: Path) -> dict:
    """slp1 -> frozen_sample row dict."""
    rows = {}
    lines = (defgen / "frozen_sample.tsv").read_text(encoding="utf-8").splitlines()
    hdr = lines[0].split("\t")
    for ln in lines[1:]:
        if not ln.strip():
            continue
        cells = ln.split("\t")
        row = dict(zip(hdr, cells))
        rows[row["slp1"]] = row
    return rows


def load_attestations(defgen: Path) -> dict:
    """slp1 -> list of 'text — work' strings (<= MAX_ATTEST, truncated)."""
    out = {}
    for ln in (defgen / "attestations.jsonl").read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        row = json.loads(ln)
        sents = []
        for s in row.get("sentences", [])[:MAX_ATTEST]:
            txt = (s.get("text") or "")[:MAX_ATTEST_CHARS]
            w = s.get("work") or ""
            sents.append(f"{txt} — {w}" if w else txt)
        out[row["slp1"]] = sents
    return out


def load_arm_jsonl(defgen: Path, prefix: str) -> dict:
    """(arm, slp1) -> row dict for gen_/judge_ jsonl files."""
    out = {}
    for arm in ARMS:
        p = defgen / f"{prefix}_{arm}.jsonl"
        for ln in p.read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            row = json.loads(ln)
            out[(arm, row["slp1"])] = row
    return out


def load_chrf(defgen: Path) -> dict:
    """(arm, slp1) -> float chrF from scores_per_item.tsv."""
    out = {}
    lines = (defgen / "scores_per_item.tsv").read_text(encoding="utf-8").splitlines()
    hdr = lines[0].split("\t")
    for ln in lines[1:]:
        if not ln.strip():
            continue
        row = dict(zip(hdr, ln.split("\t")))
        try:
            out[(row["arm"], row["slp1"])] = float(row["chrf"])
        except (KeyError, ValueError):
            continue
    return out


# --- blinded state + questions ----------------------------------------------

def build_state(hw: dict, attests: list, candidates: dict) -> str:
    """Blinded state: headword + gold gloss + attestations + candidates A–E.
    No arm names anywhere (same blinding contract as the baseline judge)."""
    parts = [f"Headword: {hw['iast']} ({hw['slp1']}), grammar {hw['grammar']}.",
             f"Gold gloss: {hw['gold_gloss']}"]
    if attests:
        parts.append("Corpus attestations:")
        parts.extend(f"{i}. {s}" for i, s in enumerate(attests, 1))
    parts.append("Candidate glosses:")
    parts.extend(f"{label}) {candidates[label]}" for label in LABELS)
    return "\n".join(parts)


def build_questions(candidates: dict) -> dict:
    qs = {}
    for label in LABELS:
        qs[f"cand_{label}"] = jp._score(
            JUDGE_QUESTION.format(label=label, range="0–5"), LEVELS)
    return qs


def build_request(hw: dict, attests: list, candidates: dict, model: str) -> dict:
    return {"state": build_state(hw, attests, candidates),
            "model": model,
            "questions": build_questions(candidates)}


def parse_answers(body: dict) -> dict:
    """qid label -> (score float, ok bool, confidence or None)."""
    out = {}
    answers = body.get("answers") or {}
    for label in LABELS:
        ans = answers.get(f"cand_{label}")
        if not isinstance(ans, dict):
            out[label] = (None, False, None)
            continue
        score = ans.get("score")
        try:
            score = float(score)
        except (TypeError, ValueError):
            out[label] = (None, False, ans.get("confidence"))
            continue
        out[label] = (score, True, ans.get("confidence"))
    return out


# --- metrics (pure stdlib) ---------------------------------------------------

def _ranks(xs: list) -> list:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(xs: list, ys: list) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    syy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sxy / (sxx * syy) if sxx > 0 and syy > 0 else float("nan")


def spearman(xs: list, ys: list) -> float:
    """Rank correlation with average-rank tie handling."""
    return _pearson(_ranks(xs), _ranks(ys))


def arm_metrics(per_arm: dict, arm: str, chrf: dict) -> dict:
    """mean adequacy + judge~chrF rho for one arm (any judge)."""
    pairs = [(v, chrf[(arm, s)]) for s, v in per_arm.get(arm, {}).items()
             if (arm, s) in chrf]
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    return {"n": len(xs),
            "mean_adequacy": round(sum(xs) / len(xs), 3) if xs else None,
            "spearman_vs_chrf": round(spearman(xs, ys), 3) if len(xs) > 2 else None}


# --- live arm -----------------------------------------------------------------

def run_live(items: list, cfg: tuple, workers: int, limit: int) -> tuple:
    """items: [(slp1, hw, attests, candidates)]. Returns (results, cost, calls).
    results: slp1 -> {label: (score, ok, confidence)}."""
    api_key, model, endpoint = cfg
    results: dict = {}
    cost = [0.0, 0]  # usd, calls
    done = [0]

    def one(it):
        slp1, hw, attests, candidates = it
        req = build_request(hw, attests, candidates, model)
        last_cls = "NO_CALL"
        body = {}
        for attempt in range(1, RETRIES + 1):
            status, body = jp.call_jev(req, api_key, endpoint, timeout_s=90.0)
            last_cls = jp.classify_result(status, body)
            if last_cls == "OK":
                u = body.get("usage") or {}
                c = jp.cost_usd(u)
                if c is not None:
                    cost[0] += c
                cost[1] += 1
                break
            if last_cls not in RETRY_CLASSES:
                break
            time.sleep(2.0 * attempt)
        parsed = parse_answers(body) if last_cls == "OK" else {
            label: (None, False, None) for label in LABELS}
        results[slp1] = {"answers": parsed, "classify": last_cls}
        done[0] += 1
        if done[0] % 50 == 0:
            print(f"  ... {done[0]}/{len(items)} scored, ${cost[0]:.4f}",
                  flush=True)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(one, items[:limit or None]))
    return results, cost[0], cost[1]


# --- analysis ------------------------------------------------------------------

def analyse(results: dict, items: list, baseline: dict, chrf: dict,
            cost_usd: float, calls: int) -> dict:
    """Full metric block + verdict. items mirror run_live's input."""
    jev_flat = {}   # (arm, slp1) -> score   via label->arm map built per item
    base_flat = {}  # (arm, slp1) -> baseline adequacy
    label_arm = {}  # slp1 -> {label: arm}
    ok_calls = sum(1 for r in results.values() if r["classify"] == "OK")
    for slp1, hw, _att, candidates in items:
        r = results.get(slp1)
        if not r or r["classify"] != "OK":
            continue
        label_arm[slp1] = {label: arm for label, arm in zip(LABELS, ARMS)}
        for label, arm in label_arm[slp1].items():
            score, ok, _conf = r["answers"][label]
            if ok:
                jev_flat[(arm, slp1)] = score
    for (arm, slp1), row in baseline.items():
        base_flat[(arm, slp1)] = float(row["adequacy"])

    pairs = [(jev_flat[k], base_flat[k]) for k in jev_flat if k in base_flat]
    agree_rho = spearman([p[0] for p in pairs], [p[1] for p in pairs])
    agree_pearson = _pearson([p[0] for p in pairs], [p[1] for p in pairs])

    jev_by_arm, base_by_arm = {}, {}
    for (arm, _slp1), v in jev_flat.items():
        jev_by_arm.setdefault(arm, []).append(v)
    for (arm, _slp1), v in base_flat.items():
        base_by_arm.setdefault(arm, []).append(v)
    arms_block = {}
    for arm in ARMS:
        jv = jev_by_arm.get(arm, [])
        bv = base_by_arm.get(arm, [])
        jm = arm_metrics({arm: {s: v for (a, s), v in jev_flat.items()
                                if a == arm}}, arm, chrf) if jv else {}
        bm = arm_metrics({arm: {s: v for (a, s), v in base_flat.items()
                                if a == arm}}, arm, chrf) if bv else {}
        arms_block[arm] = {
            "jev": {"n": jm.get("n"), "mean": jm.get("mean_adequacy"),
                    "rho_chrf": jm.get("spearman_vs_chrf")},
            "baseline": {"n": bm.get("n"), "mean": bm.get("mean_adequacy"),
                         "rho_chrf": bm.get("spearman_vs_chrf")}}

    def arm_means(by_arm):
        return [sum(v) / len(v) for arm in ARMS if (v := by_arm.get(arm))]
    armrank_rho = (spearman(arm_means(jev_by_arm), arm_means(base_by_arm))
                   if len(jev_by_arm) == len(base_by_arm) == len(ARMS)
                   else float("nan"))
    ctx = [a for a in ARMS if a != "A0_random_floor"]
    jev_ctx_mean = (sum(v for a in ctx for v in jev_by_arm.get(a, []))
                    / max(1, sum(len(jev_by_arm.get(a, [])) for a in ctx)))
    jev_floor_mean = sum(jev_by_arm.get("A0_random_floor", [])) \
        / max(1, len(jev_by_arm.get("A0_random_floor", [1])))
    base_ctx_mean = (sum(v for a in ctx for v in base_by_arm.get(a, []))
                     / max(1, sum(len(base_by_arm.get(a, [])) for a in ctx)))
    base_floor_mean = sum(base_by_arm.get("A0_random_floor", [])) \
        / max(1, len(base_by_arm.get("A0_random_floor", [1])))

    n_pairs = len(pairs)
    per_judgment_usd = cost_usd / max(1, len(jev_flat))
    est_base_per_judgment = (EST_BASELINE_STATE_TOKENS / 1e6
                             * DEEPSEEK_IN_PER_1M_USD)
    go = (n_pairs >= 500 and agree_rho == agree_rho
          and agree_rho >= AGREE_RHO_MIN and armrank_rho == armrank_rho
          and armrank_rho >= ARMRANK_RHO_MIN
          and (jev_ctx_mean - jev_floor_mean) >= 1.0
          and per_judgment_usd < est_base_per_judgment)
    return {
        "verdict": "GO_FOR_RERANK" if go else "KEEP_BASELINE",
        "verdict_rule": (f"pairwise rho>={AGREE_RHO_MIN} on n>=500 AND "
                         f"arm-rank rho>={ARMRANK_RHO_MIN} AND floor gap>=1.0 "
                         "AND cost<baseline-est"),
        "pairs": n_pairs,
        "jev_calls_ok": ok_calls,
        "agreement": {"spearman": round(agree_rho, 3),
                      "pearson": round(agree_pearson, 3)},
        "arm_rank_spearman": round(armrank_rho, 3),
        "floor_separation": {"jev_ctx_minus_floor": round(jev_ctx_mean
                                                          - jev_floor_mean, 3),
                             "baseline_ctx_minus_floor": round(base_ctx_mean
                                                               - base_floor_mean, 3)},
        "arms": arms_block,
        "cost": {"jev_total_usd": round(cost_usd, 4),
                 "jev_calls": calls,
                 "jev_per_judgment_usd": round(per_judgment_usd, 7),
                 "baseline_est_per_judgment_usd": round(est_base_per_judgment, 7),
                 "baseline_est_note": ("deepseek-chat list-price assumption "
                                       f"${DEEPSEEK_IN_PER_1M_USD}/1M in x "
                                       f"~{EST_BASELINE_STATE_TOKENS} tok — "
                                       "estimate only, Jev side measured")},
    }


# --- report ---------------------------------------------------------------------

def write_reports(out: dict, results: dict, items: list) -> tuple:
    reports = REPO / "reports"
    reports.mkdir(exist_ok=True)
    jp_ = reports / f"DEFGEN_JEV_GLOSS_JUDGE_{REPORT_TAG}.json"
    mp = reports / f"DEFGEN_JEV_GLOSS_JUDGE_{REPORT_TAG}.md"
    dump = {"handoff": "H5279", "date": REPORT_TAG,
            "model": "jev-1.13.0 (TypeSafe System One)",
            "summary": out,
            "per_item": {slp1: {"answers": {k: list(v) for k, v in
                                            r["answers"].items()},
                                "classify": r["classify"]}
                         for slp1, r in results.items()}}
    jp_.write_text(json.dumps(dump, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    a = out
    lines = [
        f"# Jev gloss judge on the defgen sample — {a['verdict']} (H5279)",
        "",
        f"_Generated: {REPORT_TAG} · model `jev-1.13.0` (TypeSafe System One) · "
        f"blinded 5-candidate scoring, 500 frozen headwords · H5279_",
        "",
        f"**Verdict: {a['verdict']}** — rule: {a['verdict_rule']}.",
        "",
        "| Metric | Jev | Baseline (deepseek-chat) |",
        "|---|---|---|",
        (f"| Pairwise agreement vs baseline | ρ={a['agreement']['spearman']} "
         f"(Pearson {a['agreement']['pearson']}), n={a['pairs']} | — |"),
        (f"| Arm-rank agreement | ρ={a['arm_rank_spearman']} | — |"),
        (f"| Floor separation (ctx−A0) | {a['floor_separation']['jev_ctx_minus_floor']} "
         f"| {a['floor_separation']['baseline_ctx_minus_floor']} |"),
        (f"| Cost per judgment | ${a['cost']['jev_per_judgment_usd']} (measured) "
         f"| ~${a['cost']['baseline_est_per_judgment_usd']} (est) |"),
        "",
        "| Arm | Jev mean | Jev ρ~chrF | Base mean | Base ρ~chrF |",
        "|---|---|---|---|---|",
    ]
    for arm in ARMS:
        b = a["arms"][arm]
        lines.append(
            f"| {arm} | {b['jev']['mean']} | {b['jev']['rho_chrf']} "
            f"| {b['baseline']['mean']} | {b['baseline']['rho_chrf']} |")
    lines += [
        "",
        f"Calls: {a['jev_calls_ok']} OK / {a['cost']['jev_calls']} billed, "
        f"${a['cost']['jev_total_usd']} total. Full per-item dump: "
        f"[{jp_.name}]({jp_.name}). External anchor: TypeSafe's own skill-"
        "suggestion cookbook reports 7.3% wrong picks on a 182-skill ranking "
        "roster — same order of task.",
        "",
        "_Гасунс_",
    ]
    mp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return jp_, mp


# --- selftest -------------------------------------------------------------------

def selftest() -> int:
    global jp
    ut = REPO.parent / "Uprava" / "tools"
    if not (ut / "jev_probe.py").exists():
        sys.exit(f"jev_probe.py not found at {ut} (selftest needs it)")
    sys.path.insert(0, str(ut))
    import jev_probe as _jp  # noqa: PLC0415
    jp = _jp
    assert abs(spearman([1, 2, 3, 4], [10, 20, 30, 40]) - 1.0) < 1e-9
    assert abs(spearman([1, 2, 3, 4], [40, 30, 20, 10]) + 1.0) < 1e-9
    r = spearman([1, 2, 2, 4], [3, 1, 2, 4])  # ties survive
    assert -1.0 <= r <= 1.0
    hw = {"slp1": "prada", "iast": "prada", "grammar": "m.",
          "gold_gloss": "giving, granting"}
    atts = ["sentence one — Work", "sentence two — Work2"]
    cands = {label: f"gloss {label}" for label in LABELS}
    state = build_state(hw, atts, cands)
    for label in LABELS:  # blinding: no arm names in the state
        for arm in ARMS:
            assert arm not in state, f"arm leak: {arm}"
    assert "A) gloss A" in state and "Gold gloss:" in state
    req = build_request(hw, atts, cands, "jev-1.13.0")
    ok, msg = jp.validate_request(req)
    assert ok, msg
    assert all(q["type"] == "score" and isinstance(q["criteria"], list)
               for q in req["questions"].values())
    fake = {"answers": {f"cand_{label}": {"type": "score", "score": float(i),
                                          "confidence": 0.9}
                        for i, label in enumerate(LABELS)}}
    parsed = parse_answers(fake)
    assert parsed["C"] == (2.0, True, 0.9)
    m = arm_metrics({"A1_chat_ctx": {"x": 5.0, "y": 3.0}}, "A1_chat_ctx",
                    {("A1_chat_ctx", "x"): 20.0, ("A1_chat_ctx", "y"): 10.0})
    assert m["n"] == 2 and m["mean_adequacy"] == 4.0
    print("selftest PASS")
    return 0


# --- main -------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--defgen-dir", default=str(REPO.parent / "kosha"
                                                / "data" / "eval" / "defgen"))
    ap.add_argument("--uprava-tools", default=str(REPO.parent / "Uprava"
                                                  / "tools"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=WORKERS_DEFAULT)
    ap.add_argument("--env-file", default=str(Path.home() / ".secrets"
                                              / "typesafe.env"))
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    ut = Path(args.uprava_tools)
    if not (ut / "jev_probe.py").exists():
        sys.exit(f"jev_probe.py not found at {ut} — pass --uprava-tools "
                 "(H5275 client, sibling Uprava clone)")
    sys.path.insert(0, str(ut))
    global jp
    import jev_probe as jp  # noqa: PLC0415

    defgen = Path(args.defgen_dir)
    if not (defgen / "frozen_sample.tsv").exists():
        sys.exit(f"defgen data not found at {defgen} — pass --defgen-dir "
                 "(kosha clone, F48 frozen sample)")

    frozen = load_frozen(defgen)
    att = load_attestations(defgen)
    gens = load_arm_jsonl(defgen, "gen")
    baseline = load_arm_jsonl(defgen, "judge")
    chrf = load_chrf(defgen)

    items = []
    for slp1, hw in frozen.items():
        candidates = {}
        for label, arm in zip(LABELS, ARMS):
            g = gens.get((arm, slp1))
            if not g or not (g.get("gloss") or "").strip():
                candidates = {}
                break
            candidates[label] = g["gloss"]
        if candidates:
            items.append((slp1, hw, att.get(slp1, []), candidates))
    print(f"frozen={len(frozen)} benchable={len(items)} "
          f"baseline_rows={len(baseline)}")

    cfg = jp.resolve_config(args)
    if not cfg[0]:
        sys.exit("TYPESAFE_API_KEY missing (~/.secrets/typesafe.env)")
    if args.smoke:
        args.limit = 1
    results, cost, calls = run_live(items, cfg, args.workers, args.limit)
    if args.smoke:
        slp1, _hw, _a, _c = items[0]
        print(json.dumps({slp1: results.get(slp1)}, ensure_ascii=False,
                         indent=1))
        print(f"smoke OK: {calls} call(s), ${cost:.5f}")
        return 0
    out = analyse(results, items, baseline, chrf, cost, calls)
    jp_, mp = write_reports(out, results, items)
    print("verdict:", out["verdict"])
    print("agreement:", out["agreement"], "arm_rank_rho:",
          out["arm_rank_spearman"])
    print("floor:", out["floor_separation"])
    print("cost:", out["cost"])
    print(f"reports: {jp_} {mp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())




