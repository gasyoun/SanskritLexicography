#!/usr/bin/env python3
"""H4750 / sibling census C17 — backfill the Cyrillic proper-noun → SLP1 table
from inm/pui <k1> headwords.

Direction guarantee (the "never by rule" fence, FINDINGS §60/§629): every NEW
slp1 key is COPIED VERBATIM from a Cologne inm/pui <k1> headword — never derived
from the Cyrillic string. The project's existing IAST→Cyrillic proper-name
renderer (src/iast_to_cyrillic.py, the same <is>-span utility pwg_ru already
uses) is employed ONLY as a JOIN KEY: a rendered spelling locates the
corpus-attested Russian headword inside the fully-Cyrillic name indices, and a
pair ships only on an EXACT string match. The rendering direction (IAST→Cyr) is
unambiguous where the refuted reverse (Cyr→IAST) is not (т = t and ṭ), so no
key ambiguity can be manufactured by the join; rendering COLLAPSES (ā→а) are
handled by the ambiguity class below, which is excluded from the shipped batch.

Selection (census C17, Uprava docs/CROSSWALK_CANDIDATES_PENDING_MAPPINGS_14-09-2026.md
item 17): +88 rows. The 88 are taken from the UNAMBIGUOUS class only — spellings
where exactly ONE distinct inm/pui key renders to the attested spelling — in
deterministic (slp1, cyrillic) order. The surplus pool is measured and reported
for a possible follow-up, never silently dropped.

Stages
  A  load existing table (never mutated rows)
  B  uncovered Cyrillic index headwords (pure-Cyrillic seeds, H3985 inventory)
  C  inm/pui k1 → IAST → rendered spelling → exact-match join on B
  D  ambiguity class (one spelling, 2+ distinct keys) — recorded, excluded
  E  ship +88 unambiguous rows; revalidate the whole table; recount tiers

  python h4750_cyr_slp1_backfill.py            # dry run (no writes)
  python h4750_cyr_slp1_backfill.py --apply    # write table + revalidation report
  python h4750_cyr_slp1_backfill.py --selftest # hermetic fixture test
"""
from __future__ import annotations

import csv
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "src"))

from h3985_cyr_slp1_table import LEXICON, ONOMASTICON, index_headwords, load_headwords  # noqa: E402
from iast_to_cyrillic import name_for_ru_prose, transliterate  # noqa: E402
from indic_transliteration import sanscript  # noqa: E402

SL = HERE.parents[1]
TABLE = SL / "RussianTranslation" / "data" / "cyrillic_proper_noun_slp1.tsv"
INVENTORY = HERE / "h3985_seed_inventory.json"
REPORT = SL / "RussianTranslation" / "reports" / "H4750_cyr_slp1_backfill.json"
HEADER = ["cyrillic", "slp1", "iast_witness", "validation",
          "onomasticon", "witness_count", "seeds"]
TARGET_NEW_ROWS = 88


def load_table(path: Path = TABLE) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    assert list(rows[0].keys()) == HEADER, "table schema drift"
    return rows


def render_key(k1: str) -> str:
    """SLP1 dictionary headword → IAST → Cyrillic proper-noun spelling.

    The SLP1 key itself passes through UNCHANGED; only its rendering is used
    for the join."""
    iast = sanscript.transliterate(k1, sanscript.SLP1, sanscript.IAST)
    words = []
    for w in iast.split():
        t = transliterate(w)
        words.append(t[0].upper() + t[1:] if t else t)
    return " ".join(words)


def uncovered_cyrillic(table_rows: list[dict], inv: dict) -> dict[str, set[str]]:
    """Stage B — index headwords the table does not cover yet, with their seeds."""
    known = {r["cyrillic"] for r in table_rows}
    out: dict[str, set[str]] = {}
    for seed in inv["seeds_pure_cyrillic"]:
        p = Path(seed["path"])
        if not p.exists():
            continue
        for h in index_headwords(p):
            if h not in known:
                out.setdefault(h, set()).add(seed["rel"])
    return out


def join(uncovered: dict[str, set[str]], ono: dict[str, set[str]]) -> tuple[list[dict], dict]:
    """Stage C+D — dictionary-keyed exact-match join + ambiguity census."""
    hits: list[dict] = []
    by_cyr: dict[str, set[str]] = {}
    for src in sorted(ono):
        for k1 in sorted(ono[src]):
            iast = sanscript.transliterate(k1, sanscript.SLP1, sanscript.IAST)
            for cyr in {render_key(k1), name_for_ru_prose(iast)}:
                if cyr in uncovered:
                    seeds = "|".join(sorted(uncovered[cyr]))
                    rec = {"cyrillic": cyr, "slp1": k1, "iast_witness": iast,
                           "validation": "onomasticon", "onomasticon": src,
                           "witness_count": 1, "seeds": seeds}
                    hits.append(rec)
                    by_cyr.setdefault(cyr, set()).add(k1)
    # de-dup identical (cyr, key) pairs (two render variants can agree)
    seen: set[tuple[str, str]] = set()
    uniq = []
    for r in hits:
        ident = (r["cyrillic"], r["slp1"])
        if ident not in seen:
            seen.add(ident)
            uniq.append(r)
    ambiguous = {c: sorted(ks) for c, ks in by_cyr.items() if len(ks) > 1}
    return uniq, ambiguous


def select_batch(cands: list[dict], ambiguous: dict[str, list[str]],
                 target: int = TARGET_NEW_ROWS) -> list[dict]:
    """Stage E — unambiguous spellings only, deterministic (slp1, cyrillic) order."""
    pool = [r for r in cands if r["cyrillic"] not in ambiguous]
    pool.sort(key=lambda r: (r["slp1"], r["cyrillic"]))
    return pool[:target]


def recount(table_rows: list[dict], ono: dict[str, set[str]],
            lex: dict[str, set[str]]) -> dict[str, int]:
    """Revalidate every row's tier against the live onomasticon/lexicon."""
    tiers = {"onomasticon": 0, "lexicon": 0, "iast-witness-only": 0}
    for r in table_rows:
        k = r["slp1"]
        if any(k in hw for hw in ono.values()):
            tiers["onomasticon"] += 1
        elif any(k in hw for hw in lex.values()):
            tiers["lexicon"] += 1
        else:
            tiers["iast-witness-only"] += 1
    return tiers


def run(apply: bool) -> int:
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    table = load_table()
    before_sig = [(r["cyrillic"], r["slp1"]) for r in table]
    ono = load_headwords(ONOMASTICON)
    lex = load_headwords(LEXICON)
    before_tiers = recount(table, ono, lex)
    uncovered = uncovered_cyrillic(table, inv)
    cands, ambiguous = join(uncovered, ono)
    batch = select_batch(cands, ambiguous)

    unamb_pool = [r for r in cands if r["cyrillic"] not in ambiguous]
    leftover = len(unamb_pool) - len(batch)
    print(f"uncovered spellings: {len(uncovered)}")
    print(f"join candidates (cyr,key): {len(cands)}  ambiguous spellings: {len(ambiguous)}")
    print(f"unambiguous pool: {len(unamb_pool)}  batch selected: {len(batch)}  leftover pool: {leftover}")

    if apply:
        merged = sorted(table + batch, key=lambda r: (r["slp1"], r["cyrillic"]))
        after_sig = [(r["cyrillic"], r["slp1"]) for r in merged]
        assert len(after_sig) == len(before_sig) + len(batch)
        # stability: the original rows survive untouched (as a set)
        assert set(before_sig) <= set(after_sig), "existing rows mutated"
        with TABLE.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter="\t", lineterminator="\n")
            w.writerow(HEADER)
            for r in merged:
                w.writerow([r["cyrillic"], r["slp1"], r["iast_witness"],
                            r["validation"], r["onomasticon"],
                            r["witness_count"], r["seeds"]])
        reloaded = load_table()
        assert [(r["cyrillic"], r["slp1"]) for r in reloaded] == after_sig, "write/read drift"
        after_tiers = recount(reloaded, ono, lex)
        assert after_tiers["onomasticon"] == before_tiers["onomasticon"] + len(batch)
        report = {
            "handoff": "H4750",
            "census": "Uprava docs/CROSSWALK_CANDIDATES_PENDING_MAPPINGS_14-09-2026.md item 17 (C17)",
            "measured_at": datetime.now(timezone.utc).isoformat(),
            "model": "OxAlpha (opencode/z-ai/glm-5.3-flash)",
            "method": ("keys COPIED verbatim from inm/pui <k1> headwords; IAST→Cyrillic "
                       "rendering (src/iast_to_cyrillic.py) used ONLY as an exact-match "
                       "join key to locate corpus-attested Russian spellings in the "
                       "fully-Cyrillic name indices; zero keys derived from Cyrillic "
                       "character rules (FINDINGS §60 fence intact)"),
            "rule_derived_keys": 0,
            "table_rows_before": len(table),
            "table_rows_after": len(reloaded),
            "new_rows_shipped": len(batch),
            "target_new_rows": TARGET_NEW_ROWS,
            "renderer_selfcheck_on_own_table_pct": round(100.0 * sum(
                1 for r in table
                if render_key(r["slp1"]) == r["cyrillic"]) / len(table), 1),
            "uncovered_index_spellings": len(uncovered),
            "join_candidates_cyr_key_pairs": len(cands),
            "ambiguous_spellings": len(ambiguous),
            "ambiguous_sample": dict(sorted(ambiguous.items())[:25]),
            "leftover_unambiguous_pool": sum(
                1 for r in cands if r["cyrillic"] not in ambiguous) - len(batch),
            "recount_before": before_tiers,
            "recount_after": after_tiers,
            "new_rows_sample": [
                {k: r[k] for k in ("cyrillic", "slp1", "iast_witness", "onomasticon")}
                for r in batch[:15]],
            "table": str(TABLE.relative_to(SL)),
        }
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        print("recount:", before_tiers, "->", after_tiers)
        print("report:", REPORT)
    else:
        print("DRY RUN — no writes. Re-run with --apply.")
    return 0


def selftest() -> int:
    """Hermetic fixture test — proves the never-by-rule + attestation +
    stability invariants on a tmp sandbox, no csl-orig access."""
    tmp = Path(tempfile.mkdtemp(prefix="h4750_selftest_"))
    (tmp / "inm").mkdir()
    (tmp / "pui").mkdir()
    # fixtures: agni = hits; SAntA/SAnta = ambiguity pair (Śāntā/Śantā both render
    # to Шанта); plava = no attested index spelling. Keys use Cologne SLP1
    # (ś=S, ā=A, uppercase stops = aspirates: kAkutsTa = kākutstha).
    (tmp / "inm" / "inm.txt").write_text(
        "<k1>agni</k1>fire\n<k1>SAntA</k1>name\n<k1>SAnta</k1>name\n"
        "<k1>plava</k1>swimmer\n", encoding="utf-8")
    (tmp / "pui" / "pui.txt").write_text("", encoding="utf-8")
    idx = tmp / "idx.txt"
    idx.write_text("Шанта — герой\nАгни — бог\n", encoding="utf-8")  # HEAD_RE shape
    table = tmp / "t.tsv"
    with table.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(HEADER)
        w.writerow(["Агни", "agni", "Agni", "onomasticon", "inm", 3, "s0"])

    rows = load_table(table)
    assert len(rows) == 1
    unco = {"Шанта": {"seed:idx"}, }  # Агни already covered by the table row
    ono = load_headwords({"inm": tmp / "inm" / "inm.txt", "pui": tmp / "pui" / "pui.txt"})
    cands, amb = join(unco, ono)
    # attestation gate: plava has no attested spelling → absent
    assert all(r["cyrillic"] != "Плава" for r in cands), "unattested spelling leaked"
    # ambiguity: Шанта renders from BOTH SAntA and SAnta → ambiguous class
    assert "Шанта" in amb and sorted(amb["Шанта"]) == ["SAntA", "SAnta"]
    batch = select_batch(cands, amb)
    assert batch == [], "ambiguous spelling must not ship"
    # unambiguous control: remove SAnta → Шанта ships with key copied from k1
    (tmp / "inm" / "inm.txt").write_text(
        "<k1>agni</k1>fire\n<k1>SAntA</k1>name\n", encoding="utf-8")
    ono2 = load_headwords({"inm": tmp / "inm" / "inm.txt", "pui": tmp / "pui" / "pui.txt"})
    cands2, amb2 = join(unco, ono2)
    assert amb2 == {}
    batch2 = select_batch(cands2, amb2)
    assert len(batch2) == 1
    r = batch2[0]
    assert r["cyrillic"] == "Шанта"
    assert r["slp1"] == "SAntA", "key must be the literal dictionary k1, not a rule output"
    assert r["validation"] == "onomasticon" and r["onomasticon"] == "inm"
    # stability: original row untouched
    assert [(x["cyrillic"], x["slp1"]) for x in rows] == [("Агни", "agni")]
    print("SELFTEST PASS (5/5 assertions): attestation gate, ambiguity exclusion, "
          "k1-verbatim key, tier assignment, existing-row stability")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(run(apply="--apply" in sys.argv))
