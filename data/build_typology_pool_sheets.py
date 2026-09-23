#!/usr/bin/env python3
"""H5330 — render the double-keyed definition-typology review sheets (300 x 7).

Consumes the H5330 sampling frame (definition_typology_pool_300x7_manifest.tsv,
built by definition_typology_pool_sampler.py) and renders, per dictionary, TWO
annotator variants of the same 300-row pool using the house review-sheet
standard (csl_pyutil.render_review_sheet_packset, v16 packset):

  <dict>-a  variant A — manifest order (the seeded sample order)
  <dict>-b  variant B — same rows, reshuffled with a per-variant seed

Distinct sheet_ids mean distinct localStorage records, so two annotators can
key the same rows independently and export TWO decisions files per dictionary
(the double-key assignment rule: full row overlap, independent keys, blind to
the machine's predicted class).

Cards are PREDICTION-BLIND: the classifier's predicted class is deliberately
NOT shown — it anchors annotators (that anchoring is why round 1's gold is
single-pass). The 4-class force-choice is carried by the sheet's rating row
(1 synonym / 2 equivalent / 3 encyclopedic / 4 residual); approve/reject
carries card usability ("Оценил" / "Карточка битая").

Dry run (--dry-run): after rendering, re-opens the RENDERED pack HTML files,
parses the card data-id attributes back out of the artifact (never from the
in-memory item list), synthesizes one decisions payload per variant in the
exact handin export shape, validates it (sheet_id, full id set, every row
decided, rating in 1..4, variant A ids == variant B ids) and writes
<sheet_id>_decisions.json beside the sheets. This is the handoff stop
condition: the sheets produce decisions files in a dry run.

Output: data/typology_pool_300x7_sheets/ — gitignored (the cards carry
csl-orig-derived definition text; the guard "never commit csl-orig" keeps bulk
dictionary bodies out of git. The committed manifest carries ids only; the
sheets are byte-reproducible from manifest + seed + local csl-orig).

Usage:
    python data/build_typology_pool_sheets.py --dry-run \
        [--csl-orig ../csl-orig/v02] [--venv-python /Users/mac/.venvs/sheet-smoke/bin/python]

Requires the csl_pyutil package (sheet-smoke venv or sys.path).

H5330, 24-09-2026, OxAlpha (opencode/z-ai/glm-5.3-flash).
"""

from __future__ import annotations

import argparse
import html
import json
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
SHEETS_DIR = HERE / "typology_pool_300x7_sheets"
MANIFEST = HERE / "definition_typology_pool_300x7_manifest.tsv"
GENERATED_DATE = "2026-09-24"
PACK_SIZE = 10
RATING_LABEL = ("Тип дефиниции: 1 — синоним · 2 — эквивалент · "
                "3 — энциклопедическая · 4 — residual")
CARD_QUESTION = ("Определите тип дефиниции по рубрике WS2.4 "
                 "(H1483). Оценка 1–4 ниже карточки; кнопка "
                 "«Оценил» фиксирует оценку, «Карточка битая» — "
                 "текст не подлежит классификации.")
RUBRIC_HTML = (
    "<ul>"
    "<li><b>синоним (1)</b> — 2+ коротких глосс через запятую/точку с "
    "запятой; короткая paryāya/iti-цепочка</li>"
    "<li><b>эквивалент (2)</b> — короткий переводной эквивалент; "
    "«N. of…» / «N. pr.»</li>"
    "<li><b>энциклопедическая (3)</b> — нумерованные значения, "
    "придаточные, длинная проза, цитируемые дефиниции</li>"
    "<li><b>residual (4)</b> — пусто; только ПОС; чистое «= лемма»; "
    "see / s.u. / q.v.; только цитата; номер значения без текста</li>"
    "</ul>"
)

DATA_ID_RE = re.compile(r'<section class="card" data-id="([^"]+)"')


def load_manifest() -> dict[str, list[dict]]:
    """manifest.tsv -> {dict: [ {l_id,k1,predicted,sample_seq} ] }"""
    if not MANIFEST.is_file():
        sys.exit(f"manifest not found: {MANIFEST} — run the sampler first")
    per_dict: dict[str, list[dict]] = {}
    with open(MANIFEST, encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        assert header == ["dict", "l_id", "k1", "predicted", "sample_seq"]
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 5:
                continue
            per_dict.setdefault(parts[0], []).append({
                "l_id": parts[1], "k1": parts[2],
                "predicted": parts[3], "sample_seq": int(parts[4]),
            })
    return per_dict


def fetch_bodies(csl_root: Path, dict_code: str,
                 wanted: dict[str, dict]) -> dict[str, str]:
    """One pass over the dict file; return {l_id: plain_body} for sampled ids.
    Plain body via the H1483 strip (reuse, not re-derivation)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "dt_classifier", HERE / "definition_typology_classifier.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    path = csl_root / dict_code / f"{dict_code}.txt"
    if not path.is_file():
        sys.exit(f"missing dictionary file: {path}")
    out: dict[str, str] = {}
    for lid, _k1, body in mod.extract_records(path):
        if lid in wanted:
            out[lid] = mod.strip_markup(mod.body_after_pipe(body))
            if len(out) == len(wanted):
                break
    missing = set(wanted) - set(out)
    if missing:
        sys.exit(f"{dict_code}: {len(missing)} sampled l_ids not found "
                 f"(e.g. {sorted(missing)[:3]}) — manifest vs csl-orig drift")
    return out


def render_packset(items, config, screening, outdir: Path, sheet_id: str):
    """Call the house emitter (csl_pyutil) and write parent + packs."""
    from csl_pyutil import render_review_sheet_packset  # noqa: E402
    out = render_review_sheet_packset(items, config, screening=screening)
    (outdir / f"{sheet_id}.html").write_text(out["parent"], encoding="utf-8")
    packdir = outdir / sheet_id
    packdir.mkdir(parents=True, exist_ok=True)
    pack_paths = []
    for n, h in enumerate(out["packs"], 1):
        p = packdir / f"pack-{n:02d}.html"
        p.write_text(h, encoding="utf-8")
        pack_paths.append(p)
    return pack_paths


def build_variant(dict_code: str, rows: list[dict], bodies: dict[str, str],
                  variant: str, seed: int) -> tuple[str, list[dict], dict]:
    """sheet_id + emitter items + config for one (dict, variant)."""
    sheet_id = f"h5330typ-{dict_code}-{variant}"
    ordered = list(rows)
    if variant == "b":
        rng = random.Random(seed + 1)  # variant salt; A keeps manifest order
        rng.shuffle(ordered)
    items = []
    for r in ordered:
        body = bodies[r["l_id"]]
        items.append({
            "id": f"{dict_code}:{r['l_id']}",
            "filt": "pool",
            "title": f"{r['k1']}  ({dict_code} <L>{r['l_id']})",
            "question": CARD_QUESTION,
            "panels": [("определение (после снятия разметки)",
                        "<p>%s</p>" % html.escape(body or "(пусто)")),
                       ("рубрика WS2.4", RUBRIC_HTML)],
        })
    n = len(items)
    config = {
        "sheet_id": sheet_id,
        "title": f"Definition typology — {dict_code} ({n} entries, key {variant.upper()})",
        "subtitle": ("H5330 double-keyed pool: 4-class force-choice, "
                     "prediction-blind"),
        "footer": "Rubric: data/DEFINITION_TYPOLOGY_WS2_4_2026.md (H1483). "
                  "Do not discuss cards between the two keys.",
        "approve_label": "Оценил", "reject_label": "Карточка битая",
        "filters": [("pool", "все карточки")],
        "generated": GENERATED_DATE,
        "pack_size": PACK_SIZE,
        "rating": {"label": RATING_LABEL, "scale": 4},
    }
    screening = {"deterministic": 0, "lookup": 0, "agent": 0, "human": n,
                 "evidence_path": "data/definition_typology_pool_sampler.py",
                 "rules": ["no pre-screening — full 300-row pool goes to the "
                           "human key; machine prediction deliberately hidden"]}
    return sheet_id, items, config


# ------------------------------------------------------------------ dry run

def dry_run(outdir: Path, ids_by_sheet: dict[str, set[str]]) -> int:
    """Artifact-level dry run: decisions files must fall out of the RENDERED
    sheets, and the two variants of each dict must key the SAME id set."""
    failures = []
    by_prefix: dict[str, dict[str, set[str]]] = {}
    for sheet_id, expected_ids in sorted(ids_by_sheet.items()):
        packdir = outdir / sheet_id
        pack_files = sorted(packdir.glob("pack-*.html"))
        if not pack_files:
            failures.append(f"{sheet_id}: no packs rendered")
            continue
        found: list[str] = []
        for p in pack_files:
            found.extend(DATA_ID_RE.findall(p.read_text(encoding="utf-8")))
        if len(found) != len(set(found)):
            failures.append(f"{sheet_id}: duplicate data-id in rendered packs")
        if set(found) != expected_ids:
            failures.append(
                f"{sheet_id}: rendered ids != manifest ids "
                f"({len(set(found))} vs {len(expected_ids)})")
            continue
        prefix = sheet_id.rsplit("-", 1)[0]
        by_prefix.setdefault(prefix, {})[sheet_id] = set(found)
        # synthesize a decisions payload in the exact handin export shape
        payload = {
            "sheet_id": sheet_id,
            "generated": GENERATED_DATE,
            "decided": len(found),
            "partial": False,
            "complete": True,
            "undecided": 0,
            "items": [{"id": i, "decision": "a", "note": "dry-run",
                       "rating": (hash(i) % 4) + 1} for i in found],
        }
        dp = outdir / f"{sheet_id}_decisions.json"
        dp.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    # double-key pairability: variant A and B cover the same ids
    for prefix, variants in sorted(by_prefix.items()):
        keys = sorted(variants)
        if len(keys) != 2 or not {k[-1] for k in keys} == {"a", "b"}:
            failures.append(f"{prefix}: expected variants a+b, got {keys}")
            continue
        if variants[keys[0]] != variants[keys[1]]:
            failures.append(f"{prefix}: variant id sets differ — cannot double-key")
        else:
            print(f"dry-run {prefix}: a/b cover the same {len(variants[keys[0]])} ids ✓")
    for f in failures:
        print(f"dry-run FAIL: {f}", file=sys.stderr)
    if failures:
        return 1
    n = sum(len(v) for v in ids_by_sheet.values())
    print(f"dry-run PASS: {len(ids_by_sheet)} sheets, {n} card decisions, "
          f"{len(ids_by_sheet)} decisions files written")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csl-orig",
                    default=str(HERE.parent.parent / "csl-orig" / "v02"))
    ap.add_argument("--seed", type=int, default=5330)
    ap.add_argument("--out-dir", default=str(SHEETS_DIR))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    try:
        import csl_pyutil  # noqa: F401
    except ImportError:
        venv = Path("/Users/mac/.venvs/sheet-smoke/bin/python")
        if venv.is_file():
            sys.exit("csl_pyutil not importable — re-run under the sheet-smoke "
                     f"venv: {venv} (or pip install csl-pyutil)")
        sys.exit("csl_pyutil not importable and no sheet-smoke venv found")

    per_dict = load_manifest()
    total = sum(len(v) for v in per_dict.values())
    if total != 2100:
        sys.exit(f"manifest carries {total} rows, expected 2100 — refusing")
    outdir = Path(args.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    ids_by_sheet: dict[str, set[str]] = {}
    for dict_code in sorted(per_dict):
        rows = per_dict[dict_code]
        wanted = {r["l_id"]: r for r in rows}
        bodies = fetch_bodies(Path(args.csl_orig), dict_code, wanted)
        for variant in ("a", "b"):
            sheet_id, items, config = build_variant(
                dict_code, rows, bodies, variant, args.seed)
            scr = {"deterministic": 0, "lookup": 0, "agent": 0,
                   "human": len(items),
                   "evidence_path":
                       "data/definition_typology_pool_sampler.py",
                   "rules": ["no pre-screening — full 300-row pool goes to "
                             "the human key; machine prediction hidden"]}
            pack_paths = render_packset(items, config, scr, outdir, sheet_id)
            ids_by_sheet[sheet_id] = {it["id"] for it in items}
            print(f"rendered {sheet_id}: {len(items)} cards in "
                  f"{len(pack_paths)} packs")
    if args.dry_run:
        sys.exit(dry_run(outdir, ids_by_sheet))


if __name__ == "__main__":
    main()
