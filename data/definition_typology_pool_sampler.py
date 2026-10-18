#!/usr/bin/env python3
"""H5330 — stratified 300 x 7 definition-typology sample (double-keyed pool frame).

Draws the reproducible review-pool sample for definition-typology round 2:
300 entries from each of seven dictionaries (2,100 rows total), stratified by
the H1483 classifier's predicted rubric class (WS2.4: synonym / equivalent /
encyclopedic / residual). NO annotation happens here — this only produces the
sampling frame the double-keyed sheets are rendered from.

Classifier logic is REUSED, never re-derived: this script imports the H1483
module `definition_typology_classifier.py` (same directory) and runs its
extract/strip/classify pipeline verbatim over csl-orig.

Strata
------
Dictionary (n=300 each, the seven dict set) x predicted class (4). Within each
dictionary the 300 slots are allocated across the four classes proportional to
that dictionary's predicted class distribution, with a minimum quota of 10 per
class (when the class has >= 10 entries in that dictionary), largest-remainder
rounding so the total is exactly 300.

The seven dictionaries
----------------------
No canonical "7 dicts" list exists in the estate, so it is fixed HERE, from the
WS2.4 all-dict distribution (definition_typology_per_dict.tsv), to span all
four rubric classes with the estate's core comparative set:

  mw   286,525  anchor bilingual, equivalent-dominant (89.6%)
  pw   170,556  Petersburg large; heaviest residual share (14.1%)
  pwg  123,366  Petersburg graded; 30.0% encyclopedic (P4 subject)
  ap90  34,882  Apte student encyclopedic (46.6%)
  vcp   50,135  Vacaspatyam, encyclopedic (45.2%)
  skd   42,531  indigenous kosa, encyclopedic (56.0%)
  ben   17,310  synonym-heavy house style (30.3% — the class's best mass)

Reproducibility: single RNG `random.Random(seed)` (default 5330), dicts
processed in fixed sorted order, sample rows sorted (dict, class, l_id).
Same csl-orig input + same seed => byte-identical manifest.

Usage:
    python data/definition_typology_pool_sampler.py \
        [--csl-orig ../csl-orig/v02] [--seed 5330] [--out-dir data]
    python data/definition_typology_pool_sampler.py --selftest

Outputs (in --out-dir):
    definition_typology_pool_300x7_manifest.tsv   2100 rows, NO definition text
    definition_typology_pool_300x7_strata.tsv     dict x class allocation table
    definition_typology_pool_300x7_meta.json      seed, counts, input fingerprint

H5330, 24-09-2026, OxAlpha (opencode/z-ai/glm-5.3-flash).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent

# The seven dictionaries (see module docstring for the selection rationale).
SEVEN_DICTS = ("ap90", "ben", "mw", "pw", "pwg", "skd", "vcp")

ENTRIES_PER_DICT = 300
MIN_QUOTA_PER_CLASS = 10
DEFAULT_SEED = 5330


def _load_classifier():
    """Import the H1483 classifier module from this directory."""
    mod_path = HERE / "definition_typology_classifier.py"
    if not mod_path.is_file():
        sys.exit(f"classifier module not found: {mod_path}")
    spec = importlib.util.spec_from_file_location("dt_classifier", mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scan_dict_frames(mod, root: Path, code: str):
    """Run the classifier verbatim over one dictionary; return per-class
    (l_id, k1) frames plus the total record count. Order is file order, which
    is deterministic for a given csl-orig checkout."""
    path = root / code / f"{code}.txt"
    if not path.is_file():
        sys.exit(f"missing dictionary file: {path}")
    frames: dict[str, list[tuple[str, str]]] = {c: [] for c in mod.CLASSES}
    n = 0
    for lid, k1, body in mod.extract_records(path):
        n += 1
        plain = mod.strip_markup(mod.body_after_pipe(body))
        label, _reason = mod.classify(plain)
        frames[label].append((lid, k1))
    return frames, n


def allocate_quotas(class_totals: dict[str, int], total: int,
                    min_quota: int = MIN_QUOTA_PER_CLASS) -> dict[str, int]:
    """Proportional allocation with min quota + largest-remainder rounding.

    Sums to exactly `total` (or to `sum(class_totals.values())` when the
    dictionary is smaller than `total`). Raises ValueError if it cannot.
    """
    n_avail = sum(class_totals.values())
    if n_avail < total:
        raise ValueError(
            f"dictionary has {n_avail} entries < required {total}"
        )
    classes = sorted(class_totals)
    # Path 1 — class smaller than the floor: take everything it has.
    fixed = {c: t for c, t in class_totals.items() if 0 < t < min_quota}
    # Path 2 — floored classes: every remaining class starts at min_quota.
    # (Empty classes — class_total == 0 — get 0 and never donate.)
    floored = {c: min_quota for c, t in class_totals.items()
               if t >= min_quota}
    zeroed = {c: 0 for c, t in class_totals.items() if t == 0}
    remaining = total - sum(fixed.values()) - sum(floored.values())
    if remaining < 0:
        raise ValueError("cannot meet quota: floors exceed dictionary size")
    # Distribute `remaining` proportionally to class size over the floored
    # classes (largest remainder, deterministic tie-break by class name).
    denom = sum(class_totals[c] for c in floored)
    if denom == 0:
        if remaining != 0:
            raise ValueError("no class available to absorb the remainder")
        raw, base = {}, {c: 0 for c in floored}
    else:
        raw = {c: remaining * class_totals[c] / denom for c in floored}
        base = {c: int(v) for c, v in raw.items()}
        left = remaining - sum(base.values())
        order = sorted(floored, key=lambda c: (-(raw[c] - base[c]), c))
        for c in order[:left]:
            base[c] += 1
    quotas = {**fixed, **zeroed, **{c: floored[c] + base[c] for c in floored}}
    # Cap at class size, pushing overflow to the largest under-cap class.
    for c in sorted(quotas, key=lambda c: -quotas[c]):
        if class_totals[c] < quotas[c]:
            over = quotas[c] - class_totals[c]
            quotas[c] = class_totals[c]
            donors = [d for d in quotas
                      if d != c and quotas[d] < class_totals[d]]
            if not donors:
                raise ValueError("no donor class for capped quota overflow")
            donors.sort(key=lambda d: (-(class_totals[d] - quotas[d]), d))
            quotas[donors[0]] += over
    for c, q in quotas.items():
        if q > class_totals[c]:
            raise ValueError(f"quota {q} exceeds class size {class_totals[c]}")
        if 0 < class_totals[c] and q < min_quota:
            raise ValueError(f"floor violated for {c}: {q} < {min_quota}")
    if sum(quotas.values()) != total:
        raise ValueError(
            f"allocation sums to {sum(quotas.values())}, expected {total}"
        )
    return quotas


def draw_sample(root: Path, seed: int, dicts=SEVEN_DICTS,
                per_dict: int = ENTRIES_PER_DICT):
    """Full sample draw. Returns (rows, strata_rows, meta)."""
    mod = _load_classifier()
    rng = random.Random(seed)
    rows: list[dict] = []
    strata_rows: list[dict] = []
    fingerprints = []
    for code in dicts:  # fixed sorted order
        frames, n = scan_dict_frames(mod, root, code)
        class_totals = {c: len(frames[c]) for c in mod.CLASSES}
        quotas = allocate_quotas(class_totals, per_dict)
        picked: list[tuple[str, str, str]] = []  # (class, l_id, k1)
        for c in sorted(quotas):  # deterministic class order
            bucket = sorted(frames[c])  # stable by (l_id, k1)
            chosen = rng.sample(bucket, quotas[c])
            picked.extend((c, lid, k1) for lid, k1 in chosen)
        picked.sort(key=lambda r: (mod.CLASSES.index(r[0]), r[1]))
        for seq, (c, lid, k1) in enumerate(picked, 1):
            rows.append({
                "dict": code, "l_id": lid, "k1": k1,
                "predicted": c, "sample_seq": seq,
            })
        for c in mod.CLASSES:
            strata_rows.append({
                "dict": code, "class": c, "class_total": class_totals[c],
                "allocated": quotas.get(c, 0),
            })
        # input fingerprint (same scheme as the H1483 run meta)
        p = root / code / f"{code}.txt"
        st = p.stat()
        h = hashlib.sha1()
        h.update(str(st.st_size).encode())
        with open(p, "rb") as fh:
            head = fh.read(65536)
            h.update(head)
            if st.st_size > 65536:
                fh.seek(max(0, st.st_size - 65536))
                h.update(fh.read(65536))
        fingerprints.append(f"{code}:{st.st_size}:{h.hexdigest()[:12]}")
    meta = {
        "handoff": "H5330",
        "seed": seed,
        "dicts": list(dicts),
        "entries_per_dict": per_dict,
        "total_rows": len(rows),
        "min_quota_per_class": MIN_QUOTA_PER_CLASS,
        "allocator": "proportional-to-predicted-class, min 10/class, "
                     "largest-remainder, overflow to largest under-cap class",
        "classifier_module": "data/definition_typology_classifier.py (H1483), reused verbatim",
        "input_sha1_12": ";".join(fingerprints),
    }
    return rows, strata_rows, meta


def write_outputs(out_dir: Path, rows, strata_rows, meta) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    man = out_dir / "definition_typology_pool_300x7_manifest.tsv"
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("dict\tl_id\tk1\tpredicted\tsample_seq\n")
        for r in rows:
            fh.write(f"{r['dict']}\t{r['l_id']}\t{r['k1']}\t"
                     f"{r['predicted']}\t{r['sample_seq']}\n")
    st = out_dir / "definition_typology_pool_300x7_strata.tsv"
    with open(st, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("dict\tclass\tclass_total\tallocated\n")
        for r in strata_rows:
            fh.write(f"{r['dict']}\t{r['class']}\t{r['class_total']}\t"
                     f"{r['allocated']}\n")
    mj = out_dir / "definition_typology_pool_300x7_meta.json"
    with open(mj, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"wrote {man} ({len(rows)} rows)")
    print(f"wrote {st}")
    print(f"wrote {mj}")


# ---------------------------------------------------------------- selftest

def _write_synth_dict(root: Path, code: str, n_syn: int, n_eq: int,
                      n_enc: int, n_res: int) -> None:
    """Write a tiny synthetic csl-orig-style dictionary whose bodies
    deterministically hit each classifier class.

    NOTE: the H1483 apparatus strip eats bare Latin words (sigla-shaped, re.I),
    so the fixtures use Devanagari synonym chains and numbered-sense prose,
    which the classifier demonstrably classes synonym/encyclopedic.
    """
    d = root / code
    d.mkdir(parents=True)
    records = (
        [f"<L>{code}s{i:05d}<k1>syn{i}\n<p>जलम्, अम्बु, पाथः</p>"
         for i in range(n_syn)]
        + [f"<L>{code}e{i:05d}<k1>eq{i}\n<p>N. of a river</p>"
           for i in range(n_eq)]
        + [f"<L>{code}c{i:05d}<k1>enc{i}\n"
           f"<p>1〉 long descriptive sense one follows here always. "
           f"2〉 second numbered sense continues in prose beyond limits</p>"
           for i in range(n_enc)]
        + [f"<L>{code}r{i:05d}<k1>res{i}\n<p>q.v.</p>"
           for i in range(n_res)]
    )
    text = "\n".join(records) + "\n"
    (d / f"{code}.txt").write_text(text, encoding="utf-8")


def selftest() -> int:
    """Positive + negative controls on a synthetic corpus (offline)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for i, code in enumerate(sorted(SEVEN_DICTS)):
            # 'res' = 10..16 entries: proportional share is BELOW the floor,
            # so the min-quota lift genuinely fires for ap90 (10 entries).
            _write_synth_dict(root, code, 110, 100, 110, 10 + i)
        rows, strata, meta = draw_sample(root, seed=7, per_dict=300)
        # positive: exact counts, determinism, no leakage
        assert meta["total_rows"] == 300 * len(SEVEN_DICTS), meta["total_rows"]
        rows2, strata2, meta2 = draw_sample(root, seed=7, per_dict=300)
        assert [tuple(sorted(r.items())) for r in rows] == \
               [tuple(sorted(r.items())) for r in rows2], "seed not deterministic"
        by_dict: dict[str, int] = {}
        for r in rows:
            by_dict[r["dict"]] = by_dict.get(r["dict"], 0) + 1
            assert r["dict"] in SEVEN_DICTS
        assert all(v == 300 for v in by_dict.values()), by_dict
        for code in SEVEN_DICTS:
            alloc = {s["class"]: s["allocated"] for s in strata
                     if s["dict"] == code}
            assert sum(alloc.values()) == 300
            for cls, v in alloc.items():
                assert 0 < v or cls in (), (code, cls, v)
                if v > 0:
                    assert v >= MIN_QUOTA_PER_CLASS, (code, cls, v)
            totals = {s["class"]: s["class_total"] for s in strata
                      if s["dict"] == code}
            for cls, v in alloc.items():
                assert v <= totals[cls], (code, cls, v, totals[cls])
        # the floor genuinely bound: the smallest class got lifted, not
        # proportionally shrunk (ap90 residual: 10 entries -> exactly 10)
        ap90 = {s["class"]: (s["class_total"], s["allocated"]) for s in strata
                if s["dict"] == "ap90"}
        assert ap90["residual"] == (10, MIN_QUOTA_PER_CLASS), ap90
        # negative: allocator must refuse an undersized dictionary
        try:
            allocate_quotas({"synonym": 5, "equivalent": 5,
                             "encyclopedic": 5, "residual": 5}, 300)
        except ValueError:
            pass
        else:
            print("FAIL: allocator accepted an undersized dictionary",
                  file=sys.stderr)
            return 1
        # positive: a non-round total must still allocate EXACTLY that total
        q = allocate_quotas({"synonym": 100, "equivalent": 100,
                             "encyclopedic": 100, "residual": 100}, 301)
        assert sum(q.values()) == 301, q
    print("selftest PASS: determinism, exact 300/dict, min-quota floors, "
          "allocator refusals")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csl-orig",
                    default=str(HERE.parent.parent / "csl-orig" / "v02"))
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--out-dir", default=str(HERE))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    root = Path(args.csl_orig)
    if not root.is_dir():
        sys.exit(f"csl-orig/v02 not found at {root}")
    rows, strata_rows, meta = draw_sample(root, args.seed)
    write_outputs(Path(args.out_dir), rows, strata_rows, meta)
    print(f"seed={args.seed} dicts={','.join(meta['dicts'])} "
          f"total={meta['total_rows']}")


if __name__ == "__main__":
    main()
