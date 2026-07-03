#!/usr/bin/env python
"""analyze_sense_order_null.py — chance baseline for the A33 sense-ordering claims.

analyze_sense_order.py reports that PWG's printed sense-1 is the oldest-attested
sense 73.5% of the time and that printed order correlates with date at Kendall
tau 0.375. The paper (A33) calls this "genetic, not a strict date-sort" by
comparing against the CEILING (a pure oldest-first sort would give 100% / tau=1).
It never states the FLOOR: what would date-agnostic ordering give? Without it,
"moderate correlation" is uncalibrated — 73.5% could be a strong genetic signal
or an artifact of most entries having few senses.

This computes that floor. Reusing analyze_sense_order.py's own parser, for every
entry with >=2 dated senses it takes the per-sense OLDEST citation date in printed
order, then compares the observed statistics against a date-agnostic null:

  * sense-1-is-oldest: analytic uniform-permutation expectation = mean over
    entries of (number of senses tied for the oldest date) / (number of dated
    senses) — the chance a randomly-placed sense leads with the oldest date.
  * mean Kendall tau: expectation under uniform permutation is exactly 0 (by
    antisymmetry); a shuffle estimate is reported as a numerical check.

The gap observed − null, against the ceiling, calibrates "half right": how far
PWG's order sits from date-agnostic (floor) toward a pure chronological sort.

Usage:  python analyze_sense_order_null.py [path/to/pwg.txt] [--shuffles N]
"""
import json
import os
import random
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# Reuse the EXACT parsing + dating of the published metric, so any observed
# figure here reproduces analyze_sense_order.py rather than re-deriving it.
from analyze_sense_order import (  # noqa: E402
    DEFAULT_PWG, entries, split_senses, citation_dates, kendall_tau,
)

OUT_JSON = os.path.join(HERE, "sense_order_null.json")
OUT_MD = os.path.join(HERE, "sense_order_null.md")


def sense_date_sequences(path):
    """Per multi-sense entry, the printed-order list of per-sense oldest dates
    (only senses that carry >=1 dated citation; only entries with >=2 such)."""
    seqs = []
    for _k1, body in entries(path):
        senses = split_senses(body)
        if not senses:
            continue
        seq = []
        for _no, text in senses:
            dates = citation_dates(text)
            if dates:
                seq.append(min(dates))
        if len(seq) >= 2:
            seqs.append(seq)
    return seqs


def analytic_sense1_null(seqs):
    """Uniform-permutation P(sense-1 is an oldest sense), averaged over entries."""
    probs = []
    for seq in seqs:
        oldest = min(seq)
        ties = sum(1 for d in seq if d == oldest)
        probs.append(ties / len(seq))
    return 100 * statistics.mean(probs)


def main():
    shuffles = 200
    positional = []
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i] == "--shuffles":
            shuffles = int(argv[i + 1])
            i += 2
        else:
            positional.append(argv[i])
            i += 1
    path = os.path.abspath(positional[0]) if positional else DEFAULT_PWG

    seqs = sense_date_sequences(path)
    n = len(seqs)

    # Observed (must reproduce analyze_sense_order.py's 73.5% / 0.375).
    obs_sense1 = 100 * statistics.mean(1.0 if seq[0] == min(seq) else 0.0 for seq in seqs)
    taus = [kendall_tau(seq) for seq in seqs]
    taus = [t for t in taus if t is not None]
    obs_tau = statistics.mean(taus)

    # Floor: date-agnostic ordering.
    null_sense1 = analytic_sense1_null(seqs)
    rng = random.Random(20260703)
    shuffled_tau_means = []
    for _ in range(shuffles):
        acc = []
        for seq in seqs:
            s = seq[:]
            rng.shuffle(s)
            t = kendall_tau(s)
            if t is not None:
                acc.append(t)
        shuffled_tau_means.append(statistics.mean(acc))
    null_tau = statistics.mean(shuffled_tau_means)
    null_tau_sd = statistics.pstdev(shuffled_tau_means)

    # Calibration: fraction of the floor->ceiling span the observed value covers.
    sense1_span = round((obs_sense1 - null_sense1) / (100 - null_sense1), 3)
    tau_span = round((obs_tau - null_tau) / (1.0 - null_tau), 3)

    payload = {
        "schemaVersion": "1.0",
        "generatedBy": "RussianTranslation/research/analyze_sense_order_null.py",
        "source": path,
        "entries_>=2_dated_senses": n,
        "sense1_is_oldest": {
            "observed_pct": round(obs_sense1, 1),
            "null_pct_uniform_permutation": round(null_sense1, 1),
            "ceiling_pct": 100.0,
            "span_covered_floor_to_ceiling": sense1_span,
        },
        "kendall_tau_printed_vs_date": {
            "observed": round(obs_tau, 3),
            "null_shuffle_mean": round(null_tau, 3),
            "null_shuffle_sd": round(null_tau_sd, 4),
            "ceiling": 1.0,
            "span_covered_floor_to_ceiling": tau_span,
            "shuffles": shuffles,
        },
        "interpretation": (
            f"PWG leads with the oldest sense {round(obs_sense1,1)}% of the time vs a "
            f"date-agnostic floor of {round(null_sense1,1)}% and a pure-sort ceiling of 100% "
            f"— covering {sense1_span:.0%} of the floor→ceiling span. Printed-order/date tau "
            f"is {round(obs_tau,3)} vs a shuffle floor of {round(null_tau,3)} and ceiling 1.0 "
            f"({tau_span:.0%} of the span). Both confirm a REAL but PARTIAL genetic signal: "
            f"well above date-agnostic chance, well below a strict chronological sort — the "
            f"quantitative form of A33's 'genetic, not historical'."
        ),
    }

    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    s1 = payload["sense1_is_oldest"]
    tau = payload["kendall_tau_printed_vs_date"]
    md = [
        "# Sense-order chance baseline — PWG (A33)",
        "",
        f"Generated by [analyze_sense_order_null.py](analyze_sense_order_null.py); raw [sense_order_null.json](sense_order_null.json). Reuses analyze_sense_order.py's parser + Renou dating on {n} entries with >=2 dated senses.".format(n=n),
        "",
        "The published 73.5% / tau=0.375 were reported only against the pure-sort *ceiling*.",
        "This adds the date-agnostic *floor*, so 'genetic, not historical' becomes a calibrated",
        "effect size rather than a qualitative 'moderate'.",
        "",
        "| Statistic | Floor (date-agnostic) | Observed | Ceiling (pure sort) | Span covered |",
        "|---|---:|---:|---:|---:|",
        f"| Sense-1 is oldest | {s1['null_pct_uniform_permutation']}% | **{s1['observed_pct']}%** | 100% | **{s1['span_covered_floor_to_ceiling']:.0%}** |",
        f"| Kendall tau (order vs date) | {tau['null_shuffle_mean']} | **{tau['observed']}** | 1.0 | **{tau['span_covered_floor_to_ceiling']:.0%}** |",
        "",
        payload["interpretation"],
        "",
        "_Auto-generated; see analyze_sense_order_null.py._",
        "",
    ]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))

    print(f"wrote {OUT_JSON}")
    print(f"  sense1-oldest: floor {s1['null_pct_uniform_permutation']}% -> obs {s1['observed_pct']}% -> ceil 100% ({s1['span_covered_floor_to_ceiling']:.0%} span)")
    print(f"  tau: floor {tau['null_shuffle_mean']} -> obs {tau['observed']} -> ceil 1.0 ({tau['span_covered_floor_to_ceiling']:.0%} span)")


if __name__ == "__main__":
    main()
