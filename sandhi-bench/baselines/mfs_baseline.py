#!/usr/bin/env python3
"""MFS (most-frequent-split) baseline for sandhi-bench v2 (H6063).

Learns, from the TRAIN split only, the most frequent gold split per
normalized surface token. On dev/test, predicts that split; for surfaces
unseen in train, predicts the identity (unsplit surface), which is always
wrong for a two-word junction. Ties break alphabetically for determinism.

This is the honest weak floor any sandhi splitter must beat.

Usage:
    python sandhi-bench/baselines/mfs_baseline.py --split test \
        [--out-prefix results/mfs]
Writes:
    results/mfs_predictions_<split>.jsonl  and  results/mfs_results_<split>.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
sys.path.insert(0, str(BENCH))

import evaluate as ev  # noqa: E402  (local module)


def train_mfs(train_items: list[dict]) -> dict[str, str]:
    counts: dict[str, Counter] = {}
    for it in train_items:
        counts.setdefault(ev.norm_answer(it["sandhied"]),
                          Counter())[ev.norm_answer(it["gold"])] += 1
    return {surf: sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            for surf, c in counts.items()}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--split", required=True, choices=["dev", "test"])
    ap.add_argument("--out-prefix", default="results/mfs")
    args = ap.parse_args(argv)

    train = ev.load_split("train")
    items = ev.load_split(args.split)
    mfs = train_mfs(train)

    preds = {}
    n_unseen = 0
    for it in items:
        key = ev.norm_answer(it["sandhied"])
        if key in mfs:
            preds[it["id"]] = mfs[key]
        else:
            preds[it["id"]] = it["sandhied"]  # identity: no split
            n_unseen += 1

    res_dir = BENCH / "results"
    res_dir.mkdir(exist_ok=True)
    pred_path = res_dir / f"{Path(args.out_prefix).name}_predictions_{args.split}.jsonl"
    with pred_path.open("w", encoding="utf-8") as fh:
        for pid, p in preds.items():
            fh.write(json.dumps({"id": pid, "pred": p}, ensure_ascii=False) + "\n")

    res = ev.score(items, preds)
    res.update({"split": args.split, "system": "MFS (surface, train-only)",
                "surface_oov_rate": round(n_unseen / len(items), 4)})
    out_path = res_dir / f"{Path(args.out_prefix).name}_results_{args.split}.json"
    out_path.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
