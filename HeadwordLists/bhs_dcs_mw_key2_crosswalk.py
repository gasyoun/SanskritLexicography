#!/usr/bin/env python3
"""H4744 - BHS (Edgerton) x MW and x DCS Buddhist-texts key2 crosswalk.

Sibling census B8 (batch-1 xwalk wave, minted 14-09-2026). First crosswalk for
the BHS dictionary: BHS-unique-key2-18188 (SLP1) joined against
  (a) MW-unique-key2-198489 and PWG-unique-key2-110438 (exact/form_key tiers), and
  (b) DCS lemmas attested in Buddhist loci of the pinned dcs_full.sqlite
      (register-confounded texts; the period map (H1000, FINDINGS 87) excludes
      three of them as Buddhist-hybrid register).

DCS lemma text is IAST -> SLP1 via canonical sanskrit_util.to_slp1 (vendored by
import, never re-spelled locally).

Outputs (beside this file, HeadwordLists/):
  bhs_dcs_mw_key2_crosswalk.tsv        one row per BHS key2
  bhs_dcs_mw_key2_crosswalk_stats.json machine-readable stats + 30-entry sample

Read-only inputs: HeadwordLists/now-2026/*.txt (BOM state read as-is, none present),
VisualDCS/src/DCS-data-2026/dcs_full.sqlite (the REAL 921 MB DB, not the 0-byte decoy).
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, "/Users/mac/Documents/GitHub/sanskrit-util/py")
from sanskrit_util import to_slp1, slp1_form_key  # noqa: E402

MARKER = re.compile(r"[˚()\-]")
strip_markers = lambda s: MARKER.sub("", s)  # noqa: E731

DB = Path("/Users/mac/Documents/GitHub/VisualDCS/src/DCS-data-2026/dcs_full.sqlite")
NOW = REPO / "HeadwordLists" / "now-2026"
BHS_TSV = NOW / "BHS-unique-key2-18188.txt"
MW_TSV = NOW / "MW-unique-key2-198489.txt"
PWG_TSV = NOW / "PWG-unique-key2-110438.txt"

# Buddhist loci in DCS. PM-EXCLUDED = the three Buddhist texts the H1000 period
# map fences off as register-confounded (FINDINGS 87). BHS-HYBRID = further
# canonical Buddhist Hybrid Sanskrit texts present in DCS. BUDDHIST-CLASSICAL =
# Buddhist scholastic/classical works (Buddhist, but not the hybrid register).
LOCUS_CLASS = {
    "Divyāvadāna": "pm-excluded",
    "Aṣṭasāhasrikā": "pm-excluded",
    "Saddharmapuṇḍarīkasūtra": "pm-excluded",
    "Lalitavistara": "bhs-hybrid",
    "Avadānaśataka": "bhs-hybrid",
    "Saṅghabhedavastu": "bhs-hybrid",
    "Laṅkāvatārasūtra": "bhs-hybrid",
    "Abhidharmakośa": "buddhist-classical",
    "Abhidharmakośabhāṣya": "buddhist-classical",
    "Bodhicaryāvatāra": "buddhist-classical",
    "Buddhacarita": "buddhist-classical",
    "Mūlamadhyamakārikāḥ": "buddhist-classical",
    "Prasannapadā": "buddhist-classical",
    "Nyāyabindu": "buddhist-classical",
    "Saundarānanda": "buddhist-classical",
    "Śikṣāsamuccaya": "buddhist-classical",
    "Viṃśatikākārikā": "buddhist-classical",
    "Viṃśatikāvṛtti": "buddhist-classical",
    "Acintyastava": "buddhist-classical",
    "Āryāsaptaśatī": "buddhist-classical",
}

OUT_TSV = REPO / "HeadwordLists" / "bhs_dcs_mw_key2_crosswalk.tsv"
OUT_JSON = REPO / "HeadwordLists" / "bhs_dcs_mw_key2_crosswalk_stats.json"


def load_keys(path: Path) -> set[str]:
    data = path.read_bytes()
    assert not data.startswith(b"\xef\xbb\xbf"), f"unexpected BOM in {path}"
    keys = data.decode("utf-8").splitlines()
    keys = [k.strip() for k in keys if k.strip()]
    assert len(keys) == len(set(keys)), f"duplicate keys in {path}"
    return set(keys)


def main() -> None:
    bhs = sorted(load_keys(BHS_TSV))
    mw = load_keys(MW_TSV)
    pwg = load_keys(PWG_TSV)
    mw_fk = {slp1_form_key(k) for k in mw}
    pwg_fk = {slp1_form_key(k) for k in pwg}
    mw_s = {strip_markers(k) for k in mw if strip_markers(k)}
    pwg_s = {strip_markers(k) for k in pwg if strip_markers(k)}
    mw_sf = {slp1_form_key(k) for k in mw_s}
    pwg_sf = {slp1_form_key(k) for k in pwg_s}

    def lex_side(k: str, lex_exact: set, lex_fk: set, lex_s: set, lex_sf: set) -> str:
        """Tiered match verdict for one key against one lexicon's key sets."""
        if k in lex_exact:
            return "exact"
        if slp1_form_key(k) in lex_fk:
            return "form_key"
        s = strip_markers(k)
        if s and s in lex_s:
            return "marker_strip"
        if s and slp1_form_key(s) in lex_sf:
            return "marker_strip+form_key"
        return "unlinked"

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cur = con.cursor()
    names = dict(cur.execute("SELECT text_id, name FROM text").fetchall())
    tids = {n: t for t, n in names.items() if n in LOCUS_CLASS}
    missing = set(LOCUS_CLASS) - set(tids)
    assert not missing, f"locus absent from DCS: {missing}"

    # lemma_id -> (iast lemma, tokens, locus names)
    agg: dict[int, list] = defaultdict(lambda: [None, 0, set()])
    q = """
      SELECT t.lemma_id, c.text_id, COUNT(*)
      FROM token t
      JOIN sentence s ON s.id = t.sentence_id
      JOIN chapter c ON c.chapter_id = s.chapter_id
      WHERE c.text_id IN (%s) AND t.lemma_id != 0
      GROUP BY t.lemma_id, c.text_id""" % ",".join(str(tids[n]) for n in sorted(tids))
    for lemma_id, tid, n in cur.execute(q):
        a = agg[lemma_id]
        a[1] += n
        a[2].add(names[tid])

    lemmas = {lid: lem for lid, lem in cur.execute("SELECT lemma_id, lemma FROM lemma")}
    for lid, a in agg.items():
        a[0] = lemmas.get(lid)
    con.close()

    # DCS side keyed by SLP1: exact tier, form_key tier, marker-strip tiers
    dcs_by_slp1: dict[str, list] = defaultdict(list)
    dcs_fk: dict[str, list] = defaultdict(list)
    dcs_s: dict[str, list] = defaultdict(list)
    dcs_sf: dict[str, list] = defaultdict(list)
    for lid, (lem, n, loci) in agg.items():
        if lem is None:
            continue
        s = to_slp1(lem)
        dcs_by_slp1[s].append((lid, n, sorted(loci)))
        dcs_fk[slp1_form_key(s)].append((lid, n, sorted(loci)))
        st = strip_markers(s)
        if st:
            dcs_s[st].append((lid, n, sorted(loci)))
            dcs_sf[slp1_form_key(st)].append((lid, n, sorted(loci)))

    def dcs_tier(k: str) -> tuple[str, list]:
        fk = slp1_form_key(k)
        s = strip_markers(k)
        if k in dcs_by_slp1:
            return "exact", dcs_by_slp1[k]
        if fk in dcs_fk:
            return "form_key", dcs_fk[fk]
        if s and s in dcs_s:
            return "marker_strip", dcs_s[s]
        if s and slp1_form_key(s) in dcs_sf:
            return "marker_strip+form_key", dcs_sf[slp1_form_key(s)]
        return "unlinked", []

    rows = []
    tier_counts = defaultdict(lambda: defaultdict(int))
    stats: dict = dict(
        total=0, dcs_exact=0, hybrid_any=0, pm_excluded_any=0,
        multi_lemma=0, tokens_matched=0,
    )
    for k in bhs:
        mw_verdict = lex_side(k, mw, mw_fk, mw_s, mw_sf)
        pwg_verdict = lex_side(k, pwg, pwg_fk, pwg_s, pwg_sf)
        dtier, hits = dcs_tier(k)
        if hits:
            hits = sorted(hits, key=lambda h: -h[1])
            lid, n, loci = hits[0]
            if len(hits) > 1:
                stats["multi_lemma"] += 1
        else:
            lid, n, loci = "", 0, []
        core = [l for l in loci if LOCUS_CLASS[l] in ("pm-excluded", "bhs-hybrid")]
        if core:
            stats["hybrid_any"] += 1
        if any(LOCUS_CLASS[l] == "pm-excluded" for l in loci):
            stats["pm_excluded_any"] += 1
        stats["total"] += 1
        stats["dcs_exact"] += dtier == "exact"
        stats["tokens_matched"] += n
        tier_counts["mw"][mw_verdict] += 1
        tier_counts["pwg"][pwg_verdict] += 1
        tier_counts["dcs"][dtier] += 1
        rows.append([
            k, mw_verdict, pwg_verdict,
            lid, n, ";".join(loci), dtier, len(hits),
        ])

    # core-locus (hybrid register) presence, computed cleanly
    core_count = sum(
        1 for r in rows
        if any(LOCUS_CLASS[l] in ("pm-excluded", "bhs-hybrid") for l in r[5].split(";") if l)
    )
    stats["hybrid_any"] = core_count
    stats["classical_only"] = sum(1 for r in rows if r[5]) - core_count
    stats["tier_counts"] = {k: dict(v) for k, v in tier_counts.items()}

    with OUT_TSV.open("w", encoding="utf-8", newline="\n") as f:
        f.write("bhs_key2\tmw_tier\tpwg_tier\tdcs_lemma_id\tdcs_bhs_tokens\t"
                "dcs_bhs_loci\tdcs_tier\tdcs_lemma_hits\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")

    sample_idx = sorted({(i * 607) % len(rows) for i in range(30)})
    sample = [
        dict(row=rows[i][0], mw=rows[i][1], pwg=rows[i][2], dcs_lemma_id=rows[i][3],
             tokens=rows[i][4], loci=rows[i][5], dcs_tier=rows[i][6])
        for i in sample_idx
    ]
    stats["sample_30"] = sample
    stats["dcs_input"] = {
        "db": str(DB), "sha256_sidecar": (DB.parent / "dcs_full.sqlite.sha256").read_text().strip() if (DB.parent / "dcs_full.sqlite.sha256").exists() else None,
        "loci": LOCUS_CLASS,
        "tokens_in_loci": sum(a[1] for a in agg.values()),
        "distinct_lemmas_in_loci": len(agg),
    }
    stats["inputs"] = {
        "bhs": BHS_TSV.name, "mw": MW_TSV.name, "pwg": PWG_TSV.name,
        "slp1_transcoder": "sanskrit-util py to_slp1 (import, not vendored)",
    }
    OUT_JSON.write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")

    t = stats["total"]
    print(f"BHS {t} | MW {stats['tier_counts']['mw']} | PWG {stats['tier_counts']['pwg']}")
    print(f"DCS-Buddhist {stats['tier_counts']['dcs']} | hybrid-register rows "
          f"{stats['hybrid_any']} | tokens matched {stats['tokens_matched']}")
    print(f"wrote {OUT_TSV.name} and {OUT_JSON.name}")


if __name__ == "__main__":
    main()
