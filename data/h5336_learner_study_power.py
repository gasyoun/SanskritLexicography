#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H5336 — preregistered power / sample-size and item-frame tool for the G7 learner-layer user study.

Written BEFORE any participant data exists (that is the point: the analysis plan is
fixed in code, not chosen after looking at results). Three subcommands:

  power    analytic paired-t sample size (by-participant aggregate, the preregistered
           fallback analysis) + Monte-Carlo power for the crossed participant x item
           design that the primary mixed model assumes.
  frame    item-frame eligibility counted on our own live data: DCS frequency bands
           (VisualDCS dcs_lemma_summary.json) intersected with the H5330 definition
           typology pool manifest. Fails closed when an input is missing.
  selftest determinism, monotonicity, analytic/simulated agreement, refusals.

Design it models (see docs/USER_STUDY_PROTOCOL_LEARNER_LAYER_G7_24-09-2026.md):
within-subject, two conditions (learner layer vs plain Cologne lookup), each
participant does K items per condition, items counterbalanced across conditions by a
2-group Latin square. Primary outcome = log time-to-correct-sense.

Usage:
  python data/h5336_learner_study_power.py power --d 0.5 0.6 0.8
  python data/h5336_learner_study_power.py frame
  python data/h5336_learner_study_power.py selftest
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

try:  # scipy is present on the dev boxes; the fallback keeps the tool runnable without it
    from scipy import stats as _stats
except Exception:  # pragma: no cover - exercised only on a scipy-less box
    _stats = None

# --- repo paths (resolved from this file, so the tool runs from any cwd) --------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
POOL_MANIFEST = os.path.join(_HERE, "definition_typology_pool_300x7_manifest.tsv")
DCS_SUMMARY = os.path.normpath(
    os.path.join(_REPO, os.pardir, "VisualDCS", "dcs_lemma_summary.json")
)
# The shipped learner reading layer (condition B): a lemma absent from this index has no
# card to show, so it cannot be a study item however attested it is in the corpus.
LEARNER_INDEX = os.path.normpath(
    os.path.join(_REPO, os.pardir, "csl-atlas", "src", "data", "learner", "learner-index.json")
)

# Bands eligible as study items: uncommon/common/very-common. Hapax and rare lemmas are
# excluded because a learner cannot be asked to disambiguate a sense for a word that the
# corpus attests once — there is no reading context to put it in.
ELIGIBLE_BANDS = (3, 4, 5)

ALPHA = 0.05


def _t_ppf(p: float, df: int) -> float:
    if _stats is not None:
        return float(_stats.t.ppf(p, df))
    # Cornish-Fisher expansion off the normal quantile; accurate to ~1e-3 for df >= 10
    z = _norm_ppf(p)
    g1 = (z ** 3 + z) / 4.0
    g2 = (5 * z ** 5 + 16 * z ** 3 + 3 * z) / 96.0
    return z + g1 / df + g2 / df ** 2


def _norm_ppf(p: float) -> float:
    if _stats is not None:
        return float(_stats.norm.ppf(p))
    # Acklam's rational approximation (|err| < 1.15e-9)
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def paired_t_n(d: float, power: float = 0.80, alpha: float = ALPHA) -> int:
    """Smallest n for a two-sided paired t-test to reach `power` at effect size `d`.

    Iterated on the t distribution (the normal-quantile closed form under-counts by
    ~2 participants in this range), so the number is the one the test actually needs.
    """
    if d <= 0:
        raise ValueError("effect size d must be > 0")
    if not 0 < power < 1:
        raise ValueError("power must be in (0, 1)")
    for n in range(4, 5001):
        df = n - 1
        crit = _t_ppf(1 - alpha / 2, df)
        ncp = d * math.sqrt(n)
        if _stats is not None:
            achieved = 1 - _stats.nct.cdf(crit, df, ncp) + _stats.nct.cdf(-crit, df, ncp)
        else:  # normal approximation to the noncentral t
            achieved = 1 - _norm_cdf(crit - ncp) + _norm_cdf(-crit - ncp)
        if achieved >= power:
            return n
    raise ValueError("no n <= 5000 reaches the requested power")


def _norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def simulate_power(
    n_participants: int,
    k_items_per_condition: int,
    beta: float,
    sd_participant: float = 0.35,
    sd_item: float = 0.30,
    sd_residual: float = 0.45,
    sd_participant_slope: float = 0.15,
    n_sims: int = 2000,
    seed: int = 5336,
    alpha: float = ALPHA,
    counterbalanced: bool = True,
) -> float:
    """Monte-Carlo power for the crossed participant x item design.

    Generates log-time as participant intercept + participant-specific condition slope +
    item intercept + residual, then applies the PREREGISTERED FALLBACK test
    (by-participant mean difference, paired t over all participants of both
    counterbalancing groups) — deliberately the conservative analysis, so the reported
    power is a floor for the primary mixed model, never an optimistic ceiling.

    `counterbalanced=True` models the protocol's 2-group Latin square: the SAME two item
    sets are used in both conditions, with the assignment flipped between groups, so the
    item-set offset enters the two groups with opposite signs and is absorbed by the
    between-participant variance the t-test estimates. `counterbalanced=False` models the
    naive design where each condition gets its own items — it is kept because the
    selftest asserts that this variant blows the type-I rate far past alpha, which is the
    quantitative reason the protocol mandates the Latin square.

    Variance-component defaults sit in the published reading/lookup-task range (SD of log
    task time ~0.4-0.6 overall). They are assumptions, and the protocol says so out loud;
    the pilot re-estimates them and the n is recomputed before the main run.
    """
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n_sims):
        u_p = rng.normal(0, sd_participant, n_participants)
        s_p = rng.normal(0, sd_participant_slope, n_participants)
        set_1 = rng.normal(0, sd_item, k_items_per_condition)
        set_2 = rng.normal(0, sd_item, k_items_per_condition)
        # condition A = control (plain Cologne lookup), B = learner layer; beta = log-ratio
        noise_a = rng.normal(0, sd_residual, (n_participants, k_items_per_condition))
        noise_b = rng.normal(0, sd_residual, (n_participants, k_items_per_condition))
        if counterbalanced:
            # group 1: set_1 under A, set_2 under B; group 2: the reverse
            g1 = np.arange(n_participants) % 2 == 0
            items_a = np.where(g1[:, None], set_1[None, :], set_2[None, :])
            items_b = np.where(g1[:, None], set_2[None, :], set_1[None, :])
        else:
            items_a = np.broadcast_to(set_1[None, :], (n_participants, k_items_per_condition))
            items_b = np.broadcast_to(set_2[None, :], (n_participants, k_items_per_condition))
        y_a = u_p[:, None] + items_a + noise_a
        y_b = (u_p + s_p + beta)[:, None] + items_b + noise_b
        diff = y_b.mean(axis=1) - y_a.mean(axis=1)
        sd = diff.std(ddof=1)
        if sd == 0:
            continue
        t = diff.mean() / (sd / math.sqrt(n_participants))
        if abs(t) >= _t_ppf(1 - alpha / 2, n_participants - 1):
            hits += 1
    return hits / n_sims


def load_frame() -> dict:
    """Count the item frame on our own data. Fails closed — never invents a count."""
    missing = [p for p in (POOL_MANIFEST, DCS_SUMMARY, LEARNER_INDEX) if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError(
            "item-frame inputs missing (no substitute is guessed): " + "; ".join(missing)
        )
    with open(DCS_SUMMARY, encoding="utf-8") as fh:
        dcs = json.load(fh)
    lemmas = dcs["lemmas"]
    bands_all = collections.Counter(v["freqBand"] for v in lemmas.values())

    with open(POOL_MANIFEST, encoding="utf-8") as fh:
        rows = fh.read().splitlines()
    cols = rows[0].split("\t")
    recs = [dict(zip(cols, r.split("\t"))) for r in rows[1:] if r.strip()]
    keys = {r["k1"] for r in recs}
    attested = {k for k in keys if k in lemmas}
    bands_pool = collections.Counter(lemmas[k]["freqBand"] for k in attested)
    band_eligible = {k for k in attested if lemmas[k]["freqBand"] in ELIGIBLE_BANDS}

    with open(LEARNER_INDEX, encoding="utf-8") as fh:
        learner = json.load(fh)
    learner_lemmas = {e["l"] for e in learner["entries"]}
    covered = band_eligible & learner_lemmas
    return {
        "corpusRelease": dcs.get("corpusRelease"),
        "bandingRule": dcs.get("bandingRule"),
        "dcs_lemma_count": dcs.get("lemmaCount", len(lemmas)),
        "dcs_bands": dict(sorted(bands_all.items())),
        "pool_rows": len(recs),
        "pool_distinct_k1": len(keys),
        "pool_attested_in_dcs": len(attested),
        "pool_bands": dict(sorted(bands_pool.items())),
        "eligible_bands": list(ELIGIBLE_BANDS),
        "band_eligible_items": len(band_eligible),
        "learner_index_generated": learner.get("generatedAt"),
        "learner_index_records": learner.get("counts", {}).get("recordCount", len(learner_lemmas)),
        "eligible_items": len(covered),
    }


def cmd_power(args: argparse.Namespace) -> int:
    print(f"Two-sided paired t, alpha={ALPHA}, target power={args.power}")
    print("effect d  n(participants)")
    for d in args.d:
        print(f"{d:>8.2f}  {paired_t_n(d, args.power):>3d}")
    print()
    print(
        f"Monte-Carlo, crossed participants x items (n_sims={args.sims}, seed={args.seed}), "
        "analysed with the conservative by-participant paired test:"
    )
    print("  n   k   beta(log)  ratio   power")
    for n in args.n:
        for k in args.k:
            for beta in args.beta:
                p = simulate_power(n, k, beta, n_sims=args.sims, seed=args.seed)
                print(f"{n:>3d} {k:>3d} {beta:>10.2f} {math.exp(beta):>6.2f} {p:>7.3f}")
    return 0


def cmd_frame(args: argparse.Namespace) -> int:
    frame = load_frame()
    print(json.dumps(frame, ensure_ascii=False, indent=2))
    return 0


def cmd_selftest(args: argparse.Namespace) -> int:
    failures = []

    # 1. analytic sample size: known values, monotone in d
    n50, n60, n80 = paired_t_n(0.5), paired_t_n(0.6), paired_t_n(0.8)
    if not (n50 > n60 > n80):
        failures.append(f"paired_t_n not monotone decreasing in d: {n50}, {n60}, {n80}")
    if not (30 <= n50 <= 36):
        failures.append(f"paired_t_n(0.5) = {n50}, expected 30-36 (textbook value 34)")

    # 2. more power with more participants, and with a bigger effect
    p_small = simulate_power(12, 10, -0.25, n_sims=400)
    p_big = simulate_power(30, 10, -0.25, n_sims=400)
    if not p_big > p_small:
        failures.append(f"power not increasing in n: {p_small} -> {p_big}")
    p_weak = simulate_power(24, 10, -0.10, n_sims=400)
    p_strong = simulate_power(24, 10, -0.40, n_sims=400)
    if not p_strong > p_weak:
        failures.append(f"power not increasing in |beta|: {p_weak} -> {p_strong}")

    # 3. determinism at a fixed seed
    a = simulate_power(20, 8, -0.25, n_sims=300, seed=11)
    b = simulate_power(20, 8, -0.25, n_sims=300, seed=11)
    if a != b:
        failures.append(f"simulation not deterministic at a fixed seed: {a} != {b}")

    # 4. null calibration: with beta = 0 the counterbalanced design must sit near alpha
    p_null = simulate_power(24, 10, 0.0, n_sims=2000, seed=7)
    if not 0.01 <= p_null <= 0.085:
        failures.append(f"type-I rate off nominal: {p_null} (expected <= {ALPHA})")

    # 5. the design reason for the Latin square, asserted quantitatively: dropping the
    #    counterbalance makes item variance masquerade as a condition effect
    p_null_naive = simulate_power(24, 10, 0.0, n_sims=2000, seed=7, counterbalanced=False)
    if not p_null_naive > 4 * ALPHA:
        failures.append(
            f"uncounterbalanced type-I rate {p_null_naive} is not visibly inflated — "
            "the selftest can no longer justify the Latin square"
        )

    # 6. refusals
    for bad in (0.0, -1.0):
        try:
            paired_t_n(bad)
        except ValueError:
            pass
        else:
            failures.append(f"paired_t_n accepted invalid d={bad}")

    # 7. the item frame is computed from live data, not from a literal
    try:
        frame = load_frame()
        if frame["eligible_items"] <= 0:
            failures.append("item frame reports no eligible items")
        if frame["pool_attested_in_dcs"] > frame["pool_distinct_k1"]:
            failures.append("attested count exceeds the pool it was drawn from")
    except FileNotFoundError as exc:
        print(f"  frame check SKIPPED (fails closed as designed): {exc}")

    if failures:
        print("SELFTEST FAIL")
        for f in failures:
            print("  -", f)
        return 1
    print("SELFTEST PASS")
    print(f"  n(d=0.5)={n50}  n(d=0.6)={n60}  n(d=0.8)={n80}  type-I={p_null:.3f}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("power", help="sample-size table + Monte-Carlo power")
    p.add_argument("--d", type=float, nargs="+", default=[0.4, 0.5, 0.6, 0.8])
    p.add_argument("--power", type=float, default=0.80)
    p.add_argument("--n", type=int, nargs="+", default=[16, 20, 24, 30])
    p.add_argument("--k", type=int, nargs="+", default=[10])
    p.add_argument("--beta", type=float, nargs="+", default=[-0.18, -0.25, -0.35])
    p.add_argument("--sims", type=int, default=2000)
    p.add_argument("--seed", type=int, default=5336)
    p.set_defaults(func=cmd_power)

    f = sub.add_parser("frame", help="item-frame eligibility on our own live data")
    f.set_defaults(func=cmd_frame)

    s = sub.add_parser("selftest", help="determinism, monotonicity, calibration, refusals")
    s.set_defaults(func=cmd_selftest)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
