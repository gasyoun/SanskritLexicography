"""HeadwordLists/works_catalogue — ACC/NCC parse and crosswalk contracts (H4353)."""
from __future__ import annotations

import io
import json
from contextlib import redirect_stderr

import pytest

from conftest import FIXTURES, load_defs, load_module


def test_parse_acc_records_from_fixture():
    pa = load_module("HeadwordLists/works_catalogue/parse_acc.py")
    err = io.StringIO()
    with redirect_stderr(err):
        recs = pa.parse_records(str(FIXTURES / "acc_mini.txt"))
    assert [r["acc_L"] for r in recs] == ["1", "2", "4"]
    assert "unparsed header" in err.getvalue() and "1 unparsed" in err.getvalue()
    r = recs[0]
    assert r["pc_scan"] == "1-1" and r["k1_slp1"] == "rAmAyaRa" and r["k2"] == "rAmAyaRa"
    assert r["lbody_ref"] == "1.1"
    assert r["body"].startswith("rāmāyaṇa by Vālmīki. Ed. Bombay 1888.")
    assert "[?]" in r["body"] and "[Page" not in r["body"] and "<b>" not in r["body"]
    assert r["match_key"] == "ramayana"
    assert r["sigla"] == ["Vālmīki. Ed. Bombay 1888", "Baroda 1960", "Aufrecht 1, 2", "Adyar. 45"]
    assert recs[1]["match_key"] == "yogasutra"
    assert recs[2]["match_key"] == "amsanadiphala"          # parenthetical stripped
    assert pa.normalize_headword_for_matching("a_b(c)") == "ab"


def test_parse_ncc_records_and_key_repair():
    pn = load_module("HeadwordLists/works_catalogue/parse_ncc.py")
    err = io.StringIO()
    with redirect_stderr(err):
        recs = pn.parse_records(str(FIXTURES / "ncc_mini.tsv"))
    assert [r["ncc_id"] for r in recs] == ["NCC-24-1", "NCC-22-7", "NCC-1-3", "NCC-1-4"]
    assert "1 malformed" in err.getvalue()
    r = recs[0]
    assert r["deva"] == "रामायण" and r["iast"] == "Rāmāyaṇa" and r["ncc_numid"] == "240001"
    assert r["match_key"] == "ramayana"                      # H1671: never 'namayana'
    assert r["mss_witnesses"] == ["MD. 4397", "TCD. 627"]
    assert "Bombay 1888" in r["sigla"]
    assert recs[1]["match_key"] == "yogasutra"                # never 'nogasutra'
    assert recs[2]["match_key"] == "amsanadiphala"
    assert recs[3]["match_key"] == "amsadiniinduphalani"
    assert pn.clean_body("<p>a\\nb</p>  c") == "a b c"
    # NFC: decomposed a + macron reaches to_slp1 as precomposed ā
    assert pn.match_key_for("Rāmāyaṇa") == "ramayana"


def test_crosswalk_folds_and_thresholds():
    # rapidfuzz (Tier D) is an optional dependency; the folds are pure → defs only
    bw = load_defs("HeadwordLists/works_catalogue/build_works_crosswalk.py")
    assert bw.nasal_and_geminate_fold("samkhya") == bw.nasal_and_geminate_fold("sankhya")
    assert bw.nasal_and_geminate_fold("tattva") == "tatva"
    assert bw.nasal_and_geminate_fold("aammnn") == "am"
    assert bw.tier_d_threshold(6) == 1 and bw.tier_d_threshold(14) == 2
    assert bw.tier_d_threshold(30) == 4 and bw.tier_d_threshold(0) == 1
    assert bw.TIER_C_MIN_KEY_LEN == 5


def test_crosswalk_load_jsonl_gz_roundtrip(tmp_path):
    bw = load_defs("HeadwordLists/works_catalogue/build_works_crosswalk.py")
    p = tmp_path / "x.jsonl"
    p.write_text('{"a": 1}\n\n{"a": 2}\n', encoding="utf-8")
    assert [r["a"] for r in bw.load_jsonl(str(p))] == [1, 2]


def test_adjudicate_strata_and_collapse():
    ad = load_module("HeadwordLists/works_catalogue/adjudicate_p2.py")
    assert ad.ncc_key_repaired("Rāmāyaṇa") == "ramayana"
    assert ad.stem_normalize("nirvacanan") == "nirvacana"
    assert ad.stem_normalize("man") == "man"                 # too short to strip
    assert ad.score_band("C", 0.99) == "c"
    assert ad.score_band("D", 0.95) == "hi" and ad.score_band("D", 0.9) == "mid"
    assert ad.score_band("D", 0.5) == "lo"
    assert ad.stratum_for("A", "exact_after_key_repair", 0.3) == "A-exact_after_key_repair"
    assert ad.stratum_for("D", "body_overlap", 0.96) == "D-body_overlap-hi"
    assert ad.MIN_STRATUM == 25
    counts = {"D-r-hi": 30, "D-r-lo": 3, "B-r-hi": 40, "C-q-c": 5, "D-q-lo": 4}
    tr = {"D-r-hi": "D-r", "D-r-lo": "D-r", "B-r-hi": "B-r", "C-q-c": "C-q", "D-q-lo": "D-q"}
    out = ad.collapse_map(counts, tr)
    assert out["D-r-hi"] == out["D-r-lo"] == "D-r"        # one small band pools the tier+rule
    assert out["B-r-hi"] == "B-r-hi"                       # all bands big: untouched
    assert out["C-q-c"] == out["D-q-lo"] == "q-residual"   # rule total < 25


def test_wilson_lower_bound_values():
    pg = load_module("HeadwordLists/works_catalogue/p2_precision_gate.py")
    assert pg.wilson_lower(0, 0) == 0.0
    assert pg.wilson_lower(6, 6) == pytest.approx(0.6097, abs=2e-3)
    assert pg.wilson_lower(95, 100) == pytest.approx(0.8872, abs=2e-3)
    assert 0.0 <= pg.wilson_lower(1, 100) < 0.06
    assert pg.wilson_lower(100, 100) > pg.wilson_lower(99, 100)


def test_apply_p2_decisions_readers_only(tmp_path):
    """Read-side helpers only: main() rewrites the crosswalk and is never run here."""
    ap = load_module("HeadwordLists/works_catalogue/apply_p2_decisions.py")
    dec = tmp_path / "d.json"
    dec.write_text(json.dumps({"items": [{"id": "1|x", "decision": "accept", "note": "ok"},
                                         {"id": "2|y", "decision": None}]}), encoding="utf-8")
    by_id, notes, payload = ap.load_decisions(str(dec))
    assert by_id == {"1|x": "accept", "2|y": None} and notes == {"1|x": "ok", "2|y": ""}
    row = {"acc_L": "1", "ncc_id": "N", "score": 0.5, "acc_match_key": "a", "ncc_match_key": "b"}
    assert ap.tsv_row(row, "A", "p2") == "1\tN\tA\t0.5\ta\tb\tp2"
    assert ap.TSV_COLS[-1] == "provenance"
    assert ap.spotcheck_size().endswith("-card") or ap.spotcheck_size() == "stratified"
