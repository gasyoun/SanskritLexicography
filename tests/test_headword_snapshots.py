"""Regenerated lists: non-shrink floors, stable sort order, encoding round-trip (H4353).

Every floor below is the list's committed record count on 08-09-2026, written
as a literal. A regeneration that shrinks a list fails here; growth is fine —
bump the literal in the same PR that grows the list.

Round-trip fixtures are real headwords read from the committed ``now-2026``
lists (SLP1) and rendered to IAST and Devanagari through the sanctioned route
``slp1_to_devanagari(to_slp1(iast))``. ``iast_to_devanagari`` is booby-trapped
for the duration of this module: any test that routes through it fails.
"""
from __future__ import annotations

import re

import pytest

from conftest import REPO, load_module, read_lines

# --------------------------------------------------------------------- floors
# path → committed record count (data lines, header included where the file
# has one). Filename N for now-2026 lists == line count by contract.
NOW_2026 = {
    "AP-unique-key1-88867.txt": 88867,
    "AP-unique-key2-88828.txt": 88828,
    "BHS-unique-key2-18188.txt": 18188,
    "BUR-unique-key2-19251.txt": 19251,
    "CAE-unique-key2-39280.txt": 39280,
    "CCS-unique-key2-29233.txt": 29233,
    "GRA-unique-key1-11108.txt": 11108,
    "GRA-unique-key2-11453.txt": 11453,
    "INM-unique-key2-9454.txt": 9454,
    "MD-unique-key2-20107.txt": 20107,
    "MW-unique-key1-194084.txt": 194084,
    "MW-unique-key2-198489.txt": 198489,
    "PD-unique-key1-104959.txt": 104959,
    "PD-unique-key2-104968.txt": 104968,
    "PWG-unique-key1-106082.txt": 106082,
    "PWG-unique-key2-110438.txt": 110438,
    "PWK-unique-key1-151349.txt": 151349,
    "PWK-unique-key2-155688.txt": 155688,
    "SCH-unique-key2-28519.txt": 28519,
    "SKD-unique-key1-40817.txt": 40817,
    "SKD-unique-key2-40817.txt": 40817,
    "VCP-unique-key1-48636.txt": 48636,
    "VCP-unique-key2-48638.txt": 48638,
    "VEI-unique-key1-3704.txt": 3704,
    "VEI-unique-key2-3704.txt": 3704,
}

# Frozen 2014 snapshots: never regenerated, so the pin is EXACT, not a floor.
THEN_2014_EXACT = {
    "21562-huet-velthius.txt": 21562,
    "AP-unique-key1-36030.txt": 36030,
    "AP-unique-key2-36704.txt": 36704,
    "BHS-unique-key2-17784.txt": 17784,
    "BUR-unique-key2-19238.txt": 19238,
    "CAE-unique-key2-39256.txt": 39256,
    "CCS-unique-key2-29317.txt": 29317,
    "GRA-unique-key1-10315.txt": 10315,
    "GRA-unique-key2-10526.txt": 10526,
    "INM-unique-key2-9466.txt": 9466,
    "MD-unique-key2-20748.txt": 20748,
    "MW-unique-key1-193978.txt": 193978,
    "MW-unique-key2-198220.txt": 198220,
    "MW-unique-key2-198231.txt": 198231,
    "PD-unique-key1-104936.txt": 104936,
    "PD-unique-key2-104941.txt": 104941,
    "PWG-fehlerhaft-1661.txt": 1661,
    "PWG-unique-key1-106085.txt": 106085,
    "PWG-unique-key2-110402.txt": 110402,
    "PWK-fehlerhaft-2227.txt": 2227,
    "PWK-unique-key1-131918.txt": 131918,
    "PWK-unique-key2-133741.txt": 133741,
    "SCH-accents-IAST-20247.txt": 20247,
    "SCH-unique-key2-28495.txt": 28495,
    "SKD-unique-key1-40551.txt": 40551,
    "SKD-unique-key2-40595.txt": 40595,
    "VCP-unique-key1-47107.txt": 47107,
    "VCP-unique-key2-47145.txt": 47145,
    "VEI-unique-key1-3703.txt": 3703,
    "VEI-unique-key2-3770.txt": 3770,
    "mw-apte-mcdonell-hk.txt": 202567,
}

# Other regenerated outputs (line count incl. header where present).
OTHER_FLOORS = {
    "HeadwordLists/union/union_headwords.tsv": 323423,
    "HeadwordLists/union/folded_feminines.tsv": 238,
    "HeadwordLists/union/fold_candidates.tsv": 3996,
    "HeadwordLists/union/coverage_additions.tsv": 21760,
    "HeadwordLists/union/coverage_additions_crosstagged.tsv": 417,
    "HeadwordLists/union/low_candidates_screened.tsv": 427,
    "HeadwordLists/f_candidates/MW_fem_masc.tsv": 5037,
    "HeadwordLists/f_candidates/MW_multi_k2.tsv": 1,
    "HeadwordLists/f_candidates/MW_orphan_fem.tsv": 22299,
    "HeadwordLists/f_candidates/MW_variants.tsv": 1218,
    "HeadwordLists/f_candidates/SKD_fem_masc.tsv": 259,
    "HeadwordLists/f_candidates/SKD_multi_k2.tsv": 1,
    "HeadwordLists/f_candidates/SKD_orphan_fem.tsv": 9541,
    "HeadwordLists/f_candidates/SKD_variants.tsv": 556,
    "HeadwordLists/heritage_current_candidates_no_cdsl.txt": 187,
    "HeadwordLists/heritage_current_stems.txt": 38343,
    "HeadwordLists/heritage_dico_gloss.tsv": 24550,
    "HeadwordLists/heritage_forms_oracle_disagreements.tsv": 20497,
    "HeadwordLists/heritage_frequency_diff.tsv": 86556,
    "HeadwordLists/heritage_only_forms.tsv": 992195,
    "HeadwordLists/mw_heritage_crosswalk.tsv": 185804,
    "HeadwordLists/Catalan-Pujol/61267-Sanskrit-Catalan-Words-List.txt": 61267,
    "HeadwordLists/Catalan-Pujol/Catalan-uncovered-by-CDSL.txt": 4696,
    "HeadwordLists/Catalan-Pujol/accent_disagreements.tsv": 64,
    "HeadwordLists/works_catalogue/acc.jsonl": 49833,
    "HeadwordLists/works_catalogue/ncc.jsonl": 152526,
    "HeadwordLists/works_catalogue/works_crosswalk.tsv": 249803,
    "HeadwordLists/works_catalogue/works_crosswalk_agent_proposed.tsv": 10615,
    "HeadwordLists/works_catalogue/works_crosswalk_rejected.tsv": 1,
    "data/definition_typology_per_dict.tsv": 45,
    "data/definition_typology_sample.tsv": 501,
    "data/definition_typology_gold.tsv": 80,
    "data/headword_overlap_matrix.tsv": 106,
    "data/headword_unique_counts.tsv": 16,
    "data/markup_tag_census.tsv": 672,
    "data/mw_non_textattested_slp1.txt": 59697,
    "data/semdom_ak_candidates.tsv": 5591,
    "data/semdom_ak_gold.tsv": 201,
    "data/semdom_varga_crosswalk.csv": 109,
    "data/witness_independence_clusters.tsv": 76,
    "data/witness_independence_reaudit.tsv": 115,
}

GZ_FLOORS = {
    "HeadwordLists/heritage_forms_oracle.tsv.gz": 94265,
    "HeadwordLists/works_catalogue/crosswalk_candidates.jsonl.gz": 260416,
    "HeadwordLists/works_catalogue/p2_agent_verdicts.jsonl.gz": 10614,
}

NAME_RE = re.compile(r"^([A-Z]+)-unique-key([12])-(\d+)\.txt$")


@pytest.mark.parametrize("name,floor", sorted(NOW_2026.items()))
def test_now_2026_list_non_shrink_sorted_unique(name, floor):
    hd = load_module("HeadwordLists/headword_diff.py")
    rel = f"HeadwordLists/now-2026/{name}"
    raw = (REPO / rel).read_bytes()
    lines = read_lines(rel)
    m = NAME_RE.match(name)
    assert m, "snapshot filename shape {DICT}-unique-key{1|2}-{N}.txt"
    assert len(lines) == int(m.group(3)), "filename N must equal the line count"
    assert len(lines) >= floor, f"{name} shrank below its committed floor {floor}"
    assert not raw.startswith(b"\xef\xbb\xbf"), "no BOM"
    assert b"\r" not in raw and raw.endswith(b"\n"), "LF-only with trailing newline"
    assert all(line.strip() for line in lines), "no blank lines"
    assert len(set(lines)) == len(lines), "unique"
    assert lines == sorted(lines, key=hd.sanskrit_key), "SLP1 varṇa-krama order"
    if m.group(2) == "1":
        assert not any("/" in line for line in lines), "key1 is accent-stripped"


@pytest.mark.parametrize("name,count", sorted(THEN_2014_EXACT.items()))
def test_then_2014_snapshot_is_frozen(name, count):
    assert len(read_lines(f"HeadwordLists/then-2014/{name}")) == count


@pytest.mark.parametrize("rel,floor", sorted(OTHER_FLOORS.items()))
def test_regenerated_output_non_shrink(rel, floor):
    n = len(read_lines(rel))
    assert n >= floor, f"{rel} has {n} lines, committed floor {floor}"


@pytest.mark.parametrize("rel,floor", sorted(GZ_FLOORS.items()))
def test_regenerated_gz_output_non_shrink(rel, floor):
    import gzip
    with gzip.open(REPO / rel, "rb") as fh:
        n = sum(1 for _ in fh)
    assert n >= floor, f"{rel} has {n} lines, committed floor {floor}"


# ---------------------------------------------------------------- key shapes
def test_now_2026_roster_matches_readme_dicts():
    hd = load_module("HeadwordLists/headword_diff.py")
    names = sorted(p.name for p in (REPO / "HeadwordLists/now-2026").glob("*.txt"))
    assert names == sorted(NOW_2026), "a new snapshot needs its floor literal here"
    key1 = {NAME_RE.match(n).group(1) for n in names if "-key1-" in n}
    key2 = {NAME_RE.match(n).group(1) for n in names if "-key2-" in n}
    assert key1 <= key2 | {"PD"} and "MW" in key1 and "MW" in key2
    assert hd  # module importable with all roots pointed nowhere


def test_union_headwords_columns_and_roster():
    bu = load_module("HeadwordLists/build_union.py")
    lines = read_lines("HeadwordLists/union/union_headwords.tsv")
    assert lines[0].split("\t") == ["slp1", "iast", "n_dicts", "dicts", "gender", "fem_fold"]
    roster = set(bu.DICTS)
    for line in lines[1:5000]:
        cells = line.split("\t")
        dicts = cells[3].split()
        assert int(cells[2]) == len(dicts), line
        assert set(dicts) <= roster, line
        assert dicts == sorted(dicts), line


def test_works_catalogue_match_keys_are_lowercase_simplified(su):
    import json
    pn = load_module("HeadwordLists/works_catalogue/parse_ncc.py")
    for line in read_lines("HeadwordLists/works_catalogue/ncc.jsonl")[:2000]:
        row = json.loads(line)
        assert row["match_key"] == pn.match_key_for(row["iast"]), row["iast"]
        assert row["match_key"] == row["match_key"].lower()
    for line in read_lines("HeadwordLists/works_catalogue/acc.jsonl")[:2000]:
        row = json.loads(line)
        assert row["match_key"] == su.slp1_simplify(row["k1_slp1"].replace("_", "")), row


# ---------------------------------------------------------------- round trip
SLP1_LETTERS = set("aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL")


@pytest.fixture(autouse=True)
def _forbid_iast_to_devanagari(monkeypatch, su):
    def boom(*_a, **_k):
        raise AssertionError("iast_to_devanagari is the known-broken route (ka → कअ); "
                             "use slp1_to_devanagari(to_slp1(s))")
    monkeypatch.setattr(su, "iast_to_devanagari", boom)


def _sample(rel, step):
    lines = read_lines(rel)
    return lines[::step]


@pytest.mark.parametrize("name", ["MW-unique-key1-194084.txt", "PWG-unique-key1-106082.txt",
                                  "SKD-unique-key1-40817.txt", "GRA-unique-key1-11108.txt"])
def test_key1_round_trip_slp1_iast_devanagari(su, name):
    """SLP1 → IAST → SLP1 and SLP1 → Devanagari → SLP1 are identities on real key1.

    Two documented exceptions, pinned as such rather than hidden:
    * IAST hiatus: SLP1 ``a`` + ``u``/``i`` renders as ``au``/``ai``, which
      IAST cannot distinguish from the diphthong (``aDaupAsana`` ↔ ``aDOpAsana``).
    * Devanagari drops the candrabindu ``~`` and avagraha ``'`` on the way back.
    """
    words = _sample(f"HeadwordLists/now-2026/{name}", 53)
    assert len(words) > 50
    checked = 0
    for w in words:
        if not set(w) <= SLP1_LETTERS:
            continue
        iast = su.from_slp1(w)
        deva = su.slp1_to_devanagari(su.to_slp1(iast))
        assert deva == su.slp1_to_devanagari(w)
        assert su.deva_to_slp1(deva) == w, (w, deva)
        if "ai" in w or "au" in w:
            continue  # IAST hiatus ambiguity, see docstring
        assert su.to_slp1(iast) == w, (w, iast)
        checked += 1
    assert checked > 40


def test_documented_round_trip_exceptions_are_still_exceptions(su):
    assert su.to_slp1(su.from_slp1("aDaupAsana")) == "aDOpAsana"
    assert su.deva_to_slp1(su.slp1_to_devanagari("nF~HpraRetra")) == "nFMHpraRetra"
    assert su.deva_to_slp1(su.slp1_to_devanagari("aDo'kza")) == "aDokza"


def test_real_headwords_in_three_scripts(su):
    """Literal triples drawn from MW key1 / key2 (08-09-2026)."""
    for slp1, iast, deva in (
        ("agni", "agni", "अग्नि"),
        ("kfzRa", "kṛṣṇa", "कृष्ण"),
        ("aMSu", "aṃśu", "अंशु"),
        ("hveya", "hveya", "ह्वेय"),
        ("afRin", "aṛṇin", "अऋणिन्"),
    ):
        assert su.from_slp1(slp1) == iast
        assert su.to_slp1(iast) == slp1
        assert su.slp1_to_devanagari(su.to_slp1(iast)) == deva
        assert su.deva_to_slp1(deva) == slp1
    assert su.strip_slp1_accents("aMSuma/t") == "aMSumat"
    assert su.slp1_to_devanagari(su.to_slp1(su.from_slp1("aMSumat"))) == "अंशुमत्"


def test_key2_accent_strip_lands_in_key1(su):
    """GRA key2 keeps the `/` udātta; stripping it yields a form present in key1."""
    key1 = set(read_lines("HeadwordLists/now-2026/GRA-unique-key1-11108.txt"))
    key2 = read_lines("HeadwordLists/now-2026/GRA-unique-key2-11453.txt")
    accented = [k for k in key2 if "/" in k and "-" not in k][::40]
    assert len(accented) > 100
    hits = sum(su.strip_slp1_accents(k) in key1 for k in accented)
    assert hits / len(accented) > 0.95, f"{hits}/{len(accented)}"
