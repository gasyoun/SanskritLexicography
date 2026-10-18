#!/usr/bin/env python3
"""LLM baseline for sandhi-bench v2 (H6063).

Runs a local ollama-served OpenAI-ish model over a seeded subsample of a
bench split with a fixed few-shot prompt (5 category-stratified examples
from TRAIN only — no dev/test leakage into the prompt), temperature 0.

The row this produces is a *local reproducibility reference* for the
leaderboard: it shows what an ordinary instruct LLM scores zero-shot-ish
on this bench, on hardware anyone can rent. It is NOT the frontier-LLM
entry — submissions of stronger systems follow the README protocol.

Requires the ollama server (localhost:11434) and is explicitly opt-in
(`--run`); nothing network-touching runs by default anywhere in this bench.

Usage:
    python sandhi-bench/baselines/llm_baseline.py --run \
        --model qwen2.5:7b-instruct --split test --sample 100 --seed 20261006
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
sys.path.insert(0, str(BENCH))

import evaluate as ev  # noqa: E402

OLLAMA = "http://localhost:11434/api/generate"
N_SHOT = 5
# answer shape: LEFT+RIGHT, no spaces in either half (\p{L} unsupported in re)
ANSWER_RE = re.compile(r"([^\s+]+)\+([^\s+]+)")

PROMPT_TMPL = (
    "You split Sanskrit sandhi. Given a sandhied continuous surface token "
    "in its sentence context, recover the original two-word junction that "
    "produced it.\n\nExamples:\n{shots}\n\nNow the task. Context: \"{sent}\"\n"
    "Surface token: {surf}\nAnswer with ONLY the split in the form LEFT+RIGHT "
    "(one plus sign, no spaces, no explanation)."
)


def few_shot(train: list[dict], seed: int) -> list[dict]:
    rng = random.Random(seed)
    by_cat: dict[str, list[dict]] = {}
    for it in train:
        by_cat.setdefault(it["category"], []).append(it)
    cats = sorted(by_cat)
    picks = []
    for i in range(N_SHOT):
        cat = cats[i % len(cats)]
        picks.append(rng.choice(by_cat[cat]))
    return picks


def call_ollama(model: str, prompt: str) -> str:
    payload = json.dumps({
        "model": model, "prompt": prompt, "stream": False,
        "options": {"temperature": 0, "num_predict": 60},
    }).encode()
    req = urllib.request.Request(
        OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode()).get("response", "")


def extract_answer(text: str) -> str:
    m = ANSWER_RE.search(text)
    return f"{m.group(1)}+{m.group(2)}" if m else ""


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", action="store_true",
                    help="actually call the model (opt-in)")
    ap.add_argument("--model", default="qwen2.5:7b-instruct")
    ap.add_argument("--split", default="test", choices=["dev", "test"])
    ap.add_argument("--sample", type=int, default=100)
    ap.add_argument("--seed", type=int, default=20261006)
    args = ap.parse_args(argv)
    if not args.run:
        print("refusing to run without --run (network-touching, opt-in)")
        return 2

    train = ev.load_split("train")
    items = ev.load_split(args.split)
    rng = random.Random(args.seed)
    sample = sorted(items, key=lambda x: x["id"])
    rng.shuffle(sample)
    sample = sample[: args.sample]

    shots = few_shot(train, args.seed)
    shot_block = "\n".join(
        f'Context: "{s["sent"]}"\nSurface token: {s["sandhied"]}\n'
        f'Answer: {s["gold"]}' for s in shots)

    preds, raws = {}, {}
    t0 = time.monotonic()
    for i, it in enumerate(sample, 1):
        prompt = PROMPT_TMPL.format(
            shots=shot_block, sent=it["sent"], surf=it["sandhied"])
        try:
            out = call_ollama(args.model, prompt)
        except Exception as e:  # transient server issue: record, keep going
            raws[it["id"]] = f"ERROR: {e}"
            preds[it["id"]] = ""
            continue
        raws[it["id"]] = out.strip().replace("\n", " ")[:120]
        preds[it["id"]] = extract_answer(out)
        if i % 20 == 0:
            print(f"  {i}/{len(sample)} · {time.monotonic()-t0:.0f}s",
                  file=sys.stderr)

    res = ev.score(sample, preds)
    res.update({
        "split": args.split,
        "system": f"LLM local · {args.model} (5-shot, temp 0)",
        "protocol": {"model": args.model, "n_shot": N_SHOT,
                     "temperature": 0, "sample": len(sample),
                     "sample_seed": args.seed,
                     "few_shot_source": "train split only"},
        "wall_seconds": round(time.monotonic() - t0, 1),
    })

    tag = args.model.replace(":", "_").replace("/", "_")
    res_dir = BENCH / "results"
    res_dir.mkdir(exist_ok=True)
    (res_dir / f"llm_{tag}_predictions_{args.split}.jsonl").write_text(
        "".join(json.dumps({"id": k, "pred": preds[k], "raw": raws[k]},
                           ensure_ascii=False) + "\n"
                for k in sorted(preds)), encoding="utf-8")
    out = res_dir / f"llm_{tag}_results_{args.split}.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
