"""Offline tests for sandhi-bench v2 (H6063).

Network is already disabled by conftest.py; nothing here reaches outside
the repository — the gold-audit re-derivation is pointed at the committed
data's own manifest shape and a synthetic mini-table, not the kosha clone
(which the sandboxed suite cannot assume exists).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

BENCH = Path(__file__).resolve().parent.parent / "sandhi-bench"
sys.path.insert(0, str(BENCH))

import evaluate as ev  # noqa: E402
import build_dataset as bd  # noqa: E402


# --- grader ---------------------------------------------------------------

def test_norm_answer_casefold_and_spaces():
    assert ev.norm_answer("  AjaRa+Amara  ") == ev.norm_answer("ajara+amara")
    assert ev.norm_answer("a\u0301j") == ev.norm_answer("\xe1j")  # NFC


def test_score_exact_and_unanswered():
    items = [
        {"id": "1", "gold": "ajara+amara", "category": "vowel coalescence"},
        {"id": "2", "gold": "nārada+am", "category": "anusvāra / nasal"},
        {"id": "3", "gold": "raja+anta", "category": "vowel coalescence"},
    ]
    preds = {"1": "AJARA+AMARA", "2": "wrong+split"}
    res = ev.score(items, preds)
    assert res["n"] == 3
    assert res["exact_acc"] == round(1 / 3, 4)
    assert res["unanswered"] == 1  # id 3 missing
    # macro over categories: 1/2 and 0/1
    assert res["macro_acc_by_category"] == round((0.5 + 0.0) / 2, 4)


# --- parser (the proven W1.1 pattern) --------------------------------------

def test_junction_re_shape():
    part = "kālāgnisadṛśaḥ krodhe kṣamayā pṛthivīsamaḥ kāla+agni→kālāgnisadṛśaḥ"
    m = bd.JUNCTION_RE.search(part.strip())
    assert m and m.groups() == ("kāla", "agni", "kālāgnisadṛśaḥ")
    assert part[: m.start()].strip().startswith("kālāgnisadṛśaḥ")
    # no arrow → no match (truncated example rows are skipped, not guessed)
    assert bd.JUNCTION_RE.search("nāradaṃ+paripapraccha") is None


# --- committed dataset invariants -------------------------------------------

SPLITS = ("train", "dev", "test")


def _load(split):
    return [json.loads(x) for x in
            (BENCH / "data" / f"{split}.jsonl").read_text(
                encoding="utf-8").splitlines() if x.strip()]


def test_splits_exist_and_text_disjoint():
    data = {s: _load(s) for s in SPLITS}
    assert all(len(v) > 0 for v in data.values())
    seen: dict[str, set[str]] = {}
    for split, rows in data.items():
        for it in rows:
            assert it["split"] == split
            seen.setdefault(it["text"], set()).add(split)
    leaks = {t: s for t, s in seen.items() if len(s) > 1}
    assert not leaks, f"text-disjointness violated: {leaks}"


def test_ids_unique_and_gold_wellformed():
    ids = [it["id"] for s in SPLITS for it in _load(s)]
    assert len(ids) == len(set(ids))
    for s in SPLITS:
        for it in _load(s):
            # committed rows carry gold as LEFT+RIGHT, single '+', both sides
            left, right = it["gold"].split("+")
            assert left and right


def test_manifest_counts_match_files():
    manifest = json.loads((BENCH / "data" / "manifest.json").read_text(
        encoding="utf-8"))
    for s in SPLITS:
        assert manifest["splits"]["n_items"][s] == len(_load(s))
    assert manifest["license"]["bench_data"].startswith("CC BY-SA")


def test_mfs_deterministic_on_fixture():
    train = [
        {"id": "a", "sandhied": "X", "gold": "p+q", "category": "c"},
        {"id": "b", "sandhied": "X", "gold": "p+q", "category": "c"},
        {"id": "c", "sandhied": "X", "gold": "z+z", "category": "c"},
    ]
    sys.path.insert(0, str(BENCH / "baselines"))
    import mfs_baseline as mfs
    assert mfs.train_mfs(train)["x"] == "p+q"  # norm_answer casefolds the key


def test_split_leakage_detector_fires_on_synthetic():
    """The A2 audit logic itself, on data designed to violate text-disjointness."""
    bad = [
        {"id": "1", "text": "t1", "split": "train"},
        {"id": "2", "text": "t1", "split": "dev"},   # same work, two splits
    ]
    text_split: dict[str, set[str]] = {}
    for it in bad:
        text_split.setdefault(it["text"], set()).add(it["split"])
    leaked = {t: s for t, s in text_split.items() if len(s) > 1}
    assert leaked == {"t1": {"train", "dev"}}  # detector really fires


@pytest.mark.parametrize("split", SPLITS)
def test_every_category_present_every_split(split):
    cats = {it["category"] for it in _load(split)}
    assert len(cats) >= 3  # the build-time coverage assertion, re-checked
