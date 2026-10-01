#!/usr/bin/env python3
"""Module 10b - DCS corpus attestation of verb classes + prefixed forms
(Sanskrit-in-Numbers, H4711 — census A5 wiring).

Module 10 (module10_verb_class_voice.py) reports the *lexical/grammatical*
view: Whitney's 938-root gana inventory and vidyut-generated pada paradigms.
Module 10b adds the *corpus* leg by CONSUMING two already-registered kosha
datasets (never re-deriving class inventories — census A5 contract):

  - dcs-verb-roots-by-class (463 rows): per-class attested root inventory,
    root,count per file 1.csv..10.csv (comma-CSV, IAST).
  - dcs-verb-class-prefix-frequency (8454 rows): per-class root counts
    INCLUDING prefixed verb forms (semicolon-CSV, root;count).

Both are consumed read-only from the sibling VisualDCS checkout, the same
resolution pattern as the SanskritGrammar H4178 consumer of the first dataset.

Honesty notes carried on the face of the output:
  - R2606-01 (Uprava DEAD_ENDS): both datasets are UNACCENTED counts, so they
    cannot separate present class I from VI (only accent does). No I/VI
    verdict is drawn here, ever.
  - roots 10.csv contains a single junk row ("0"): counted for manifest
    parity (463), excluded from every root-level statistic (state below).
  - "prefixed-only" entries = entries of the prefixed-forms dataset absent
    from the bare-roots inventory. Verified by sampling: the frq inventory is
    mostly roots (bhū, dā...) but ALSO lists prefixed stems as own entries
    (āgam, prāp, pracch...), and assigns classes more widely (dā appears in
    the class-1 frq file though grammatically class 3). Entries are consumed
    as-is — re-classifying them is out of scope by contract.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
GITHUB_ROOT = REPO.parent
VISUAL_DCS = GITHUB_ROOT / "VisualDCS"
ROOTS_DIR = (VISUAL_DCS / "derived-data" / "Glagolnye-formy" / "Klassy"
             / "Spiski-glagolnyh-kornej-po-klassam-2214" / "Imeyushchie-formy")
FRQ_DIR = (VISUAL_DCS / "derived-data" / "Glagolnye-formy" / "Klassy"
           / "Spisok-form-s-prefiksami-8444" / "Cl_Frq")

MANIFEST_ROWS_ROOTS = 463   # kosha datasets.json dcs-verb-roots-by-class.rows
MANIFEST_ROWS_FRQ = 8454    # kosha datasets.json dcs-verb-class-prefix-frequency.rows

CLASS_LABELS = {
    1: "1 (bhvādi)", 2: "2 (adādi)", 3: "3 (juhotyādi)", 4: "4 (divādi)",
    5: "5 (svādi)", 6: "6 (tudādi)", 7: "7 (rudhādi)", 8: "8 (tanādi)",
    9: "9 (kryādi)", 10: "10 (curādi)",
}
JUNK_ROOTS = {"0"}  # roots 10.csv single junk row (kept for parity only)


def sibling_commit() -> str | None:
    try:
        return subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", "derived-data/Glagolnye-formy/Klassy"],
            cwd=VISUAL_DCS, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return None


def load_roots() -> dict[int, list[tuple[str, int]]]:
    """dcs-verb-roots-by-class: comma-CSV root,count per class file."""
    per_class: dict[int, list[tuple[str, int]]] = {}
    for klass in range(1, 11):
        rows: list[tuple[str, int]] = []
        path = ROOTS_DIR / f"{klass}.csv"
        if path.is_file():
            with path.open(encoding="utf-8", newline="") as fh:
                for line in csv.reader(fh):
                    if not line or not line[0].strip():
                        continue
                    root = line[0].strip()
                    count = int(line[1]) if len(line) > 1 and line[1].strip().isdigit() else 0
                    rows.append((root, count))
        per_class[klass] = rows
    return per_class


def load_frq() -> dict[int, list[tuple[str, int]]]:
    """dcs-verb-class-prefix-frequency: semicolon-CSV root;count per class file."""
    per_class: dict[int, list[tuple[str, int]]] = {}
    for klass in range(1, 11):
        rows: list[tuple[str, int]] = []
        path = FRQ_DIR / f"{klass}.csv"
        if path.is_file():
            with path.open(encoding="utf-8", newline="") as fh:
                for raw in fh:
                    raw = raw.strip()
                    if not raw:
                        continue
                    parts = raw.split(";")
                    root = parts[0].strip()
                    count = int(parts[1]) if len(parts) > 1 and parts[1].strip().isdigit() else 0
                    rows.append((root, count))
        per_class[klass] = rows
    return per_class


def main() -> int:
    pin = sibling_commit()
    roots = load_roots()
    frq = load_frq()

    roots_total_rows = sum(len(v) for v in roots.values())
    frq_total_rows = sum(len(v) for v in frq.values())
    parity = {
        "dcs-verb-roots-by-class": {"counted": roots_total_rows, "manifest": MANIFEST_ROWS_ROOTS},
        "dcs-verb-class-prefix-frequency": {"counted": frq_total_rows, "manifest": MANIFEST_ROWS_FRQ},
    }
    drift = [k for k, v in parity.items() if v["counted"] != v["manifest"]]
    if drift:
        print(f"MANIFEST PARITY DRIFT: {drift} — counted {parity} — failing loud", file=sys.stderr)
        return 1

    # --- bare-roots inventory (junk row excluded from stats, kept in parity)
    roots_class_of: defaultdict[str, set[int]] = defaultdict(set)
    roots_count: Counter = Counter()
    for klass, rows in roots.items():
        for root, count in rows:
            if root in JUNK_ROOTS:
                continue
            roots_class_of[root].add(klass)
            roots_count[root] += count
    n_roots_distinct = len(roots_class_of)

    roots_per_class = []
    for klass in range(1, 11):
        stat = [(r, c) for r, c in roots[klass] if r not in JUNK_ROOTS]
        roots_per_class.append({
            "class": CLASS_LABELS[klass],
            "attested_roots": len(stat),
            "corpus_occurrences": sum(c for _, c in stat),
        })

    # --- prefixed-forms dataset
    frq_count: Counter = Counter()
    frq_class_of: defaultdict[str, set[int]] = defaultdict(set)
    for klass, rows in frq.items():
        for root, count in rows:
            frq_count[root] += count
            frq_class_of[root].add(klass)
    frq_per_class = []
    for klass in range(1, 11):
        stat = frq[klass]
        frq_per_class.append({
            "class": CLASS_LABELS[klass],
            "roots": len(stat),
            "occurrences_incl_prefixed": sum(c for _, c in stat),
        })

    # --- prefixed-only attestation: frq entries absent from the bare roots
    # inventory (prefixed stems like āgam/prāp listed as own entries; entries
    # consumed as-is, never re-classified — see module docstring)
    prefixed_only = sorted(set(frq_count) - set(roots_count), key=lambda r: -frq_count[r])

    # --- prefixed share for roots present in both (top by frq mass)
    prefixed_share = []
    for root in frq_count:
        bare = roots_count.get(root, 0)
        if bare and frq_count[root] > bare:
            prefixed_share.append({
                "root": root,
                "bare_occurrences": bare,
                "incl_prefixed_occurrences": frq_count[root],
                "prefixed_share_pct": round(100 * (frq_count[root] - bare) / frq_count[root], 1),
            })
    prefixed_share.sort(key=lambda d: -(d["incl_prefixed_occurrences"] - d["bare_occurrences"]))

    out = {
        "module": "10b",
        "title": "DCS corpus attestation of verb classes + prefixed forms "
                 "(kosha datasets dcs-verb-roots-by-class + dcs-verb-class-prefix-frequency)",
        "trust_block": {
            "source": "kosha-registered VisualDCS derived-data (10 per-class CSVs each): "
                      "dcs-verb-roots-by-class (463 rows) + dcs-verb-class-prefix-frequency "
                      "(8454 rows); consumed read-only from the sibling VisualDCS checkout, "
                      "census A5 wiring (H4711) — class inventories cited, never re-derived",
            "sibling_visualdcs_pin": pin,
            "manifest_parity": parity,
            "date": str(date.today()),
            "model": "OxAlpha (opencode/z-ai/glm-5.3-flash)",
        },
        "honesty_notes": [
            "R2606-01 (Uprava DEAD_ENDS): both datasets are UNACCENTED counts — they cannot "
            "separate present class I from VI (only accent does). No I/VI verdict is drawn here.",
            "roots 10.csv holds one junk row ('0'): counted for the 463-row manifest parity, "
            "excluded from every root-level statistic.",
            "Whitney leg (module 10) and this corpus leg use different denominators (938 lexical "
            "roots vs corpus-attested roots); the two views are reported side by side, never merged.",
            "The prefixed-forms dataset lists mostly roots but also prefixed stems as own entries "
            "(āgam, prāp...) and assigns classes more widely than the bare inventory; entries are "
            "consumed as-is (re-classification is out of scope by the census contract).",
        ],
        "corpus_leg": {
            "distinct_attested_roots": n_roots_distinct,
            "per_class_bare_roots": roots_per_class,
            "per_class_incl_prefixed": frq_per_class,
            "prefixed_only_entries_count": len(prefixed_only),
            "prefixed_only_top15": [
                {"root": r, "occurrences": frq_count[r]} for r in prefixed_only[:15]
            ],
            "prefixed_share_top15": prefixed_share[:15],
        },
        "lexical_leg_crossref": {
            "module10_source": "WhitneyRoots 938-root gana inventory + 454-root pada subset "
                               "(module10_verb_class_voice.json, H813)",
            "relationship": "module 10 = grammar's own classification; module 10b = what the "
                            "corpus actually attests per class and how much of it is prefixed",
        },
    }

    out_path = HERE / "module10b_dcs_verb_class_attestation.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"parity: roots {roots_total_rows}/{MANIFEST_ROWS_ROOTS}, "
          f"frq {frq_total_rows}/{MANIFEST_ROWS_FRQ} — OK")
    print(f"distinct attested roots (bare): {n_roots_distinct}; "
          f"prefixed-only: {len(prefixed_only)}")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
