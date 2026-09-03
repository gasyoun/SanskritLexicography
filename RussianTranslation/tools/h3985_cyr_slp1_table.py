#!/usr/bin/env python3
"""H3985 / SL GAPS §6 — build + validate the Cyrillic proper-noun → SLP1 table.

Every key is derived from IAST **already present in the seed line**, transcoded
to SLP1 by `indic_transliteration.sanscript` (a lossless script transcode of a
witness), then validated against a Sanskrit onomasticon before any consumer
reads the table. No key is ever produced from Russian character rules: practical
Russian transcription collapses dental and retroflex (т = त and ट), so a
rule-based converter manufactures wrong keys for exactly the retroflex-bearing
epic names (FINDINGS §60, §495) — the refuted approach this gap fences off.

Stages
  B  extract (Cyrillic headword, IAST) pairs from the IAST-bearing seeds
  C  IAST → SLP1 transcode of the witness
  D  validate each key against the onomasticon (csl-orig INM + PUI <k1>)
  E  coverage against the fully-Cyrillic name indices
"""
from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from indic_transliteration import sanscript  # noqa: E402

HERE = Path(__file__).resolve().parent
SL = HERE.parents[1]
GITHUB = SL.parent
INVENTORY = HERE / "h3985_seed_inventory.json"
REPORTS = SL / "RussianTranslation" / "reports"
DATA = SL / "RussianTranslation" / "data"
TABLE = DATA / "cyrillic_proper_noun_slp1.tsv"
VALIDATION = REPORTS / "H3985_cyr_slp1_validation.json"

CSL = GITHUB / "csl-orig" / "v02"
ONOMASTICON = {"inm": CSL / "inm" / "inm.txt", "pui": CSL / "pui" / "pui.txt"}
LEXICON = {"mw": CSL / "mw" / "mw.txt"}

IAST_DIACRITIC = "ĀāĪīŪūṚṛṜṝḶḷḸḹṂṃḤḥÑñṄṅṬṭḌḍṆṇŚśṢṣ"
CYR_RE = re.compile(r"[А-Яа-яЁё]")
# A Cyrillic head-word run immediately followed by a parenthesised Latin gloss.
PAIR_RE = re.compile(
    r"(?<![А-Яа-яЁё\-])"
    r"([А-ЯЁ][А-Яа-яЁё]+(?:[ \-][А-Яа-яЁё]+){0,3})"
    r"[ \t]*\(\s*([^)]{2,80}?)\s*[)—,;]"
)
# What may appear inside the IAST witness before the gloss dash.
IAST_TOKEN = re.compile(r"^[A-Za-z" + IAST_DIACRITIC + r"][A-Za-z" + IAST_DIACRITIC + r"\-]*"
                        r"(?: [A-Za-z" + IAST_DIACRITIC + r"][A-Za-z" + IAST_DIACRITIC + r"\-]*){0,2}$")

# Russian function/verb words: a run containing one is running prose
# ("Сравните этот термин"), not an index headword.
RU_STOPWORD = {
    "и", "а", "но", "или", "не", "но", "же", "ли", "бы", "как", "что", "это",
    "этот", "эта", "эти", "того", "тот", "та", "те", "в", "во", "на", "с", "со",
    "из", "от", "до", "по", "за", "для", "при", "об", "о", "у", "к", "ко",
    "его", "ее", "её", "их", "он", "она", "они", "мы", "вы", "я", "ты",
    "см", "также", "здесь", "там", "термин", "слово", "имя", "название",
    "сравните", "сравни", "смотри", "часть", "глава", "книга", "стих",
}


def clean_witness(raw: str) -> str:
    """Take the IAST head of a parenthesised gloss, up to the first separator."""
    s = raw.split("—")[0].split(" - ")[0].split(",")[0].split(";")[0]
    s = s.replace("«", " ").replace("»", " ")
    return unicodedata.normalize("NFC", s).strip()


def load_headwords(paths: dict[str, Path]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    k1 = re.compile(r"<k1>([^<]+)")
    for name, p in paths.items():
        hw: set[str] = set()
        if p.exists():
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                m = k1.search(line)
                if m:
                    hw.add(m.group(1).strip())
        out[name] = hw
    return out


def extract_pairs(seeds: list[dict]) -> tuple[list[dict], list[dict]]:
    """Stage B — headword-anchored (Cyrillic, IAST) pairs; plus rejects."""
    kept: list[dict] = []
    rejected: list[dict] = []
    for seed in seeds:
        path = Path(seed["path"])
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            rejected.append({"seed": seed["rel"], "reason": f"unreadable: {e}"})
            continue
        for lineno, line in enumerate(text.splitlines()[:5000], 1):
            if not CYR_RE.search(line):
                continue
            for m in PAIR_RE.finditer(line):
                cyr, raw = m.group(1).strip(), m.group(2)
                witness = clean_witness(raw)
                rec = {"cyrillic": cyr, "witness": witness,
                       "seed": seed["rel"], "line": lineno}
                if not witness:
                    continue
                if any(w.lower().strip("-") in RU_STOPWORD for w in cyr.split()):
                    rec["reason"] = "Cyrillic run is running prose, not an index headword"
                    rejected.append(rec)
                    continue
                if CYR_RE.search(witness):
                    bad = sorted({c for c in witness if CYR_RE.match(c)})
                    rec["reason"] = "mixed-script witness (Cyrillic inside the IAST parens)"
                    rec["detail"] = "".join(bad)
                    rejected.append(rec)
                    continue
                if not witness[0].isupper():
                    rec["reason"] = "witness not capitalised — common noun, not a proper noun"
                    rejected.append(rec)
                    continue
                if witness.replace(" ", "").replace("-", "").isupper():
                    # Sigla and Roman numerals in the same parens shape as a
                    # gloss: "(EVP IX)", "(IV)" — bibliography, not a name.
                    rec["reason"] = "witness is an all-caps siglum or numeral, not a name"
                    rec["detail"] = witness[:40]
                    rejected.append(rec)
                    continue
                if not IAST_TOKEN.match(witness):
                    rec["reason"] = "witness outside the IAST alphabet"
                    rec["detail"] = witness[:40]
                    rejected.append(rec)
                    continue
                kept.append(rec)
    return kept, rejected


HEAD_RE = re.compile(r"\s*([А-ЯЁ][А-Яа-яЁё]+(?:[ \-][А-Яа-яЁё]+){0,3})[\t ]*[—\-(]")
TAG_RE = re.compile(r"<[^>]+>")


def index_headwords(path: Path) -> set[str]:
    """Stage E — Cyrillic index headwords, per storage format.

    The three named indices live in three shapes: Kadambari as plain TSV-ish
    text, Potapova and Erman-Temkin as corpus-builder JSONL (one dictionary
    entry per line, headword in `text`). A line regex alone sees only the first.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return set()
    if path.suffix.lower() == ".jsonl":
        lines = []
        for raw in text.splitlines()[:20000]:
            try:
                obj = json.loads(raw)
            except Exception:
                continue
            if isinstance(obj, dict) and isinstance(obj.get("text"), str):
                lines.append(obj["text"])
    elif path.suffix.lower() in {".html", ".htm"}:
        lines = TAG_RE.sub("\n", text).splitlines()[:20000]
    else:
        lines = text.splitlines()[:20000]
    heads = set()
    for line in lines:
        m = HEAD_RE.match(line)
        if m:
            heads.add(m.group(1).strip())
    return heads


def to_slp1(witness: str) -> str:
    """Stage C — lossless transcode of the witness. Never a Cyrillic rule."""
    return sanscript.transliterate(witness, sanscript.IAST, sanscript.SLP1)


def main() -> None:
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    seeds = inv["seeds_with_iast"]
    pure_cyr = inv["seeds_pure_cyrillic"]

    kept, rejected = extract_pairs(seeds)
    ono = load_headwords(ONOMASTICON)
    lex = load_headwords(LEXICON)

    # Stage C+D — key, then validate; merge duplicate (cyr, key) pairs.
    rows: dict[tuple[str, str], dict] = {}
    for rec in kept:
        key = to_slp1(rec["witness"])
        if not key:
            continue
        ident = (rec["cyrillic"], key)
        row = rows.setdefault(ident, {
            "cyrillic": rec["cyrillic"], "slp1": key, "iast": rec["witness"],
            "seeds": set(), "witness_count": 0,
        })
        row["seeds"].add(rec["seed"])
        row["witness_count"] += 1

    for row in rows.values():
        k = row["slp1"]
        hits = [n for n, hw in ono.items() if k in hw]
        row["onomasticon"] = ",".join(hits)
        if hits:
            row["validation"] = "onomasticon"
        elif any(k in hw for hw in lex.values()):
            row["validation"] = "lexicon"
        else:
            row["validation"] = "iast-witness-only"

    ordered = sorted(rows.values(), key=lambda r: (r["slp1"], r["cyrillic"]))

    # Ambiguity: one Cyrillic spelling standing for several distinct SLP1 keys.
    by_cyr: dict[str, set[str]] = defaultdict(set)
    for r in ordered:
        by_cyr[r["cyrillic"]].add(r["slp1"])
    ambiguous = {c: sorted(k) for c, k in by_cyr.items() if len(k) > 1}

    DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    with TABLE.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["cyrillic", "slp1", "iast_witness", "validation",
                    "onomasticon", "witness_count", "seeds"])
        for r in ordered:
            w.writerow([r["cyrillic"], r["slp1"], r["iast"], r["validation"],
                        r["onomasticon"], r["witness_count"],
                        "|".join(sorted(r["seeds"]))])

    # Stage E — coverage against the fully-Cyrillic indices.
    cyr_keys = {r["cyrillic"] for r in ordered}
    coverage = []
    for seed in pure_cyr:
        heads = index_headwords(Path(seed["path"]))
        if not heads:
            continue
        hit = sorted(heads & cyr_keys)
        coverage.append({
            "index": seed["rel"], "headwords_detected": len(heads),
            "covered_by_table": len(hit),
            "coverage_pct": round(100.0 * len(hit) / len(heads), 1),
            "covered_sample": hit[:25],
        })
    coverage.sort(key=lambda c: -c["headwords_detected"])

    tiers = defaultdict(int)
    for r in ordered:
        tiers[r["validation"]] += 1

    reject_reasons: dict[str, int] = defaultdict(int)
    for r in rejected:
        reject_reasons[r.get("reason", "?")] += 1
    reject_reasons = dict(sorted(reject_reasons.items(), key=lambda x: -x[1]))

    report = {
        "handoff": "H3985",
        "gap": "SanskritLexicography/GAPS.md §6",
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "model": "Opus 5 (claude-opus-5)",
        "method": ("keys transcoded from IAST present in the seed line "
                   "(indic_transliteration IAST→SLP1); zero keys derived from "
                   "Russian character rules"),
        "seeds_iast_bearing": len(seeds),
        "seeds_pure_cyrillic_unkeyed": len(pure_cyr),
        "pairs_extracted": len(kept),
        "pairs_rejected": len(rejected),
        "table_rows": len(ordered),
        "distinct_cyrillic": len(by_cyr),
        "distinct_slp1": len({r["slp1"] for r in ordered}),
        "rule_derived_keys": 0,
        "validation_tiers": dict(tiers),
        "onomasticon_sources": {n: len(hw) for n, hw in ono.items()},
        "lexicon_sources": {n: len(hw) for n, hw in lex.items()},
        "ambiguous_cyrillic": ambiguous,
        "reject_reasons": reject_reasons,
        "rejected_sample": rejected[:40],
        "coverage_cyrillic_indices": coverage,
        "unkeyed_pure_cyrillic_seeds": [s["rel"] for s in pure_cyr],
        "table": str(TABLE.relative_to(SL)),
    }
    VALIDATION.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("seeds_iast_bearing", "seeds_pure_cyrillic_unkeyed",
                       "table_rows", "distinct_slp1", "rule_derived_keys",
                       "validation_tiers", "reject_reasons")},
                     ensure_ascii=False, indent=2))
    print("table:", TABLE)
    print("validation:", VALIDATION)


if __name__ == "__main__":
    main()
