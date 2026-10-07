#!/usr/bin/env python3
"""Build the public sandhi-bench v2 dataset (H6063, ruling B4 — public release).

Harvests junction-level items from the kosha per-text sandhi tables
(`kosha/data/sandhi/<text>_sandhi.tsv`), each induced from DCS `Unsandhied=`
gold by the house sandhi programme (kosha SANDHI_PROGRAMME.md). The item
shape and the example-column parser reuse the proven W1.1 F1-pilot generator
(`Uprava/tools/ssb_gen_f1_sandhi_pilot.py`): examples are ` · `-separated
`<context> <left>+<right>→<surface>` fragments.

Splits are TEXT-DISJOINT (a work appears in exactly one split) so that
surface-form memorisation cannot leak across splits; the assignment is a
seeded shuffle with a coverage assertion (each split must contain all rule
categories present in the corpus). The seed is searched deterministically
from SEED_BASE upward until coverage holds, so rebuilds are reproducible.

Outputs (derived-only, publishable under CC BY-SA 4.0 — see README):
    sandhi-bench/data/train.jsonl
    sandhi-bench/data/dev.jsonl
    sandhi-bench/data/test.jsonl
    sandhi-bench/data/manifest.json

Usage:
    python sandhi-bench/build_dataset.py            # rebuild all four files
    python sandhi-bench/build_dataset.py --dry-run  # report counts only
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

SCHEMA_VERSION = "2.0.0"
SEED_BASE = 20261004
N_DEV_TEXTS = 4
N_TEST_TEXTS = 5
MIN_CONTEXT_WORDS = 4   # pilot filter: context must carry real sentential context
MIN_SURFACE_CHARS = 4   # pilot filter: avoid degenerate 2-char surfaces
JUNCTION_RE = re.compile(r"(\S+)\+(\S+)→(\S+)$")

# kosha resolution: env override → estate sibling of the main checkout.
# (Worktrees live outside GitHub/, so relative paths from the worktree do
# not reach the kosha clone; resolve the estate root via the .git pointer.)


def find_kosha() -> Path:
    env = os.environ.get("SANDHI_BENCH_KOSHA")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    # main repo root: follow the worktree .git file to the parent checkout
    probe = REPO
    for _ in range(3):
        gitfile = probe / ".git"
        if gitfile.is_file():
            gitdir = Path(gitfile.read_text(encoding="utf-8")
                          .split("gitdir:", 1)[1].strip())
            main_repo = gitdir.parent.parent  # <main>/.git/worktrees/<name>
            cand = main_repo.parent / "kosha"
            if cand.is_dir():
                return cand
            probe = main_repo.parent
            continue
        cand = probe.parent / "kosha"
        if cand.is_dir():
            return cand
        probe = probe.parent
    raise SystemExit(
        "kosha clone not found: set SANDHI_BENCH_KOSHA=<path to kosha clone>")


def git_ref(repo: Path) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s).casefold()).strip()


def harvest(kosha: Path) -> list[dict]:
    items, seen = [], set()
    for path in sorted((kosha / "data" / "sandhi").glob("*_sandhi.tsv")):
        text_id = path.name.removesuffix("_sandhi.tsv")
        with path.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                rule = row.get("rule", "")
                category = row.get("category", "") or "unclassified"
                for part in row.get("examples", "").split(" · "):
                    m = JUNCTION_RE.search(part.strip())
                    if not m:
                        continue
                    left, right, surf = m.groups()
                    ctx = part[: m.start()].strip()
                    if len(ctx.split()) < MIN_CONTEXT_WORDS:
                        continue
                    if len(surf) < MIN_SURFACE_CHARS:
                        continue
                    if not left or not right:
                        continue
                    if left == "_" or right == "_":
                        continue  # DCS '_' = empty stem: not a two-word
                                   # junction; excluded from the bench premise
                    key = (text_id, surf, left, right)
                    if key in seen:
                        continue
                    seen.add(key)
                    items.append({
                        "text": text_id,
                        "rule": rule,
                        "category": category,
                        "sent": ctx,
                        "sandhied": surf,
                        "left": left,
                        "right": right,
                        "gold": f"{left}+{right}",
                    })
    # stable order → stable ids across rebuilds on the same source
    items.sort(key=lambda x: (x["text"], x["rule"], x["sandhied"],
                              x["left"], x["right"]))
    for i, it in enumerate(items, 1):
        it["id"] = f"sb-{i:06d}"
    return items


def assign_splits(items: list[dict]) -> tuple[dict[str, list[dict]], int]:
    texts = sorted({it["text"] for it in items})
    cats = {it["category"] for it in items}
    per_text = Counter(it["text"] for it in items)

    def cats_of(sel: set[str]) -> set[str]:
        return {it["category"] for it in items if it["text"] in sel}

    seed = SEED_BASE
    while True:
        rng = random.Random(seed)
        pool = list(texts)
        rng.shuffle(pool)
        test_set = set(pool[:N_TEST_TEXTS])
        dev_set = set(pool[N_TEST_TEXTS:N_TEST_TEXTS + N_DEV_TEXTS])
        # coverage: every split carries every corpus rule category, and every
        # split is non-trivial (≥40 items)
        ok = (cats_of(test_set) == cats and cats_of(dev_set) == cats
              and sum(per_text[t] for t in test_set) >= 40
              and sum(per_text[t] for t in dev_set) >= 40)
        if ok:
            break
        seed += 1
        if seed > SEED_BASE + 10000:
            raise SystemExit("no seed found satisfying split coverage")

    splits = {"train": [], "dev": [], "test": []}
    for it in items:
        splits["test" if it["text"] in test_set
               else "dev" if it["text"] in dev_set
               else "train"].append(it)
    return splits, seed


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    kosha = find_kosha()
    ref = git_ref(kosha)
    items = harvest(kosha)
    splits, seed = assign_splits(items)

    n_by_split = {k: len(v) for k, v in splits.items()}
    texts_by_split = {
        k: sorted({it["text"] for it in v}) for k, v in splits.items()}
    cat_counts = Counter(it["category"] for it in items)
    print(f"kosha @ {ref[:12]} · harvested {len(items)} junction items")
    for k in ("train", "dev", "test"):
        print(f"  {k:5s}: {n_by_split[k]:5d} items · "
              f"{len(texts_by_split[k])} texts")
    print(f"  seed used: {seed}")
    if args.dry_run:
        return 0

    out = HERE / "data"
    out.mkdir(exist_ok=True)
    for name, rows in splits.items():
        with (out / f"{name}.jsonl").open("w", encoding="utf-8") as fh:
            for it in rows:
                fh.write(json.dumps(
                    {"id": it["id"], "text": it["text"], "split": name,
                     "category": it["category"], "rule": it["rule"],
                     "sent": it["sent"], "sandhied": it["sandhied"],
                     "gold": it["gold"]}, ensure_ascii=False) + "\n")

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "bench": "sandhi-bench-v2",
        "created": "2026-10-06",
        "handoff": "H6063 (ruling B4 — public release)",
        "task": ("given the sandhied surface token in its sentence context, "
                 "recover the original two-word junction LEFT+RIGHT"),
        "answer_format": "single string LEFT+RIGHT, one '+' , no spaces",
        "splits": {"scheme": "text-disjoint (a work appears in one split only)",
                   "seed": seed, "seed_base": SEED_BASE,
                   "n_texts": {"train": len(texts_by_split["train"]),
                               "dev": len(texts_by_split["dev"]),
                               "test": len(texts_by_split["test"])},
                   "n_items": n_by_split},
        "categories": dict(sorted(cat_counts.items())),
        "source": {
            "repo": "gasyoun/kosha",
            "git": ref,
            "path": "data/sandhi/*_sandhi.tsv",
            "lineage": ("DCS CoNLL-U gold Unsandhied= fields, induced by the "
                        "kosha junction-rule inducer (method A, 96.3% "
                        "Gita-gold coverage)"),
            "harvest_parser": "Uprava/tools/ssb_gen_f1_sandhi_pilot.py "
                              "JUNCTION_RE (proven W1.1 pattern)",
        },
        "license": {
            "bench_data": "CC BY-SA 4.0 (inherits DCS source share-alike)",
            "code": "MIT (repository LICENSE)",
            "redistribution": "derived measurements only; the raw DCS dump "
                              "is not redistributed",
        },
        "excluded": {
            "vedic": "no Vedic sandhi in this bench (ruling B5: separate "
                     "split/bench if ever added)",
            "scharf": "ScharfSandhi dataset not yet in the estate (ruling "
                      "B10 says include when available)",
        },
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"wrote {out}/train.jsonl dev.jsonl test.jsonl manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
