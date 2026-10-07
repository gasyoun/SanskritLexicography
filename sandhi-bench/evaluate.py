#!/usr/bin/env python3
"""sandhi-bench v2 grader (H6063).

Scores a predictions file against a bench split. A prediction for item id
is a single string ``LEFT+RIGHT`` (one plus sign, no spaces). Grading is
exact-match over a deterministic normalization (NFC → casefold → whitespace
collapse), the same casefold decision the SSB W3.2 identifiability review
locked for IAST sandhi answers (case is not phonemic here).

Unanswered items (missing id, or empty/non-string prediction) count as
wrong and are reported in ``unanswered``.

Metrics: overall exact accuracy, macro accuracy over rule categories,
per-category accuracy, n.

Usage:
    python sandhi-bench/evaluate.py --pred results/mfs_predictions_test.jsonl \
        --split test [--out results/mfs_results_test.json]
"""
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def norm_answer(s: str) -> str:
    import re
    return re.sub(r"\s+", " ",
                  unicodedata.normalize("NFC", s).casefold()).strip()


def load_split(split: str) -> list[dict]:
    path = HERE / "data" / f"{split}.jsonl"
    rows = [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return rows


def load_predictions(path: Path) -> dict[str, str]:
    preds: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        preds[obj["id"]] = obj.get("pred", "") or ""
    return preds


def score(items: list[dict], preds: dict[str, str]) -> dict:
    per_cat = defaultdict(lambda: [0, 0])  # category -> [correct, total]
    correct = 0
    unanswered = 0
    for it in items:
        pred = preds.get(it["id"])
        ok = (isinstance(pred, str) and pred.strip() != ""
              and norm_answer(pred) == norm_answer(it["gold"]))
        per_cat[it["category"]][1] += 1
        if pred is None or (isinstance(pred, str) and pred.strip() == ""):
            unanswered += 1
        if ok:
            correct += 1
            per_cat[it["category"]][0] += 1
    n = len(items)
    return {
        "n": n,
        "exact_acc": round(correct / n, 4) if n else None,
        "macro_acc_by_category": round(
            sum(c / t for c, t in per_cat.values()) / len(per_cat), 4
        ) if per_cat else None,
        "unanswered": unanswered,
        "per_category": {k: {"acc": round(c / t, 4), "n": t}
                         for k, (c, t) in sorted(per_cat.items())},
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pred", required=True, type=Path,
                    help="predictions jsonl: {id, pred}")
    ap.add_argument("--split", required=True, choices=["train", "dev", "test"])
    ap.add_argument("--system", default=None,
                    help="system label recorded in the result json")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    items = load_split(args.split)
    preds = load_predictions(args.pred)
    res = score(items, preds)
    res["split"] = args.split
    res["system"] = args.system or args.pred.stem

    blob = json.dumps(res, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(blob + "\n", encoding="utf-8")
    print(blob)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
