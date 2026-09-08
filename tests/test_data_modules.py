"""data/ — classifier, census, witness and semdom contracts on fixtures (H4353)."""
from __future__ import annotations

import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from conftest import FIXTURES, REPO, load_defs, load_module

MW_MINI = FIXTURES / "csl_orig_mini" / "mw" / "mw.txt"


# ------------------------------------------------------------ semdom_ak_metrics
def test_coarse_and_kappa():
    sm = load_module("data/semdom_ak_metrics.py")
    assert sm.coarse("8.4.1") == "8.4" and sm.coarse("1.1") == "1.1"
    assert sm.coarse("NONE") == "NONE" and sm.coarse("7") == "7"
    po, k = sm.kappa([("a", "a"), ("b", "b"), ("a", "a"), ("b", "b")])
    assert po == 1.0 and k == 1.0
    po, k = sm.kappa([("a", "a"), ("a", "b"), ("b", "a"), ("b", "b")])
    assert po == 0.5 and k == pytest.approx(0.0)
    po, k = sm.kappa([("a", "b"), ("b", "a")])
    assert po == 0.0 and k == pytest.approx(-1.0)


# ------------------------------------------------- definition_typology_classifier
def test_strip_markup_and_records():
    dt = load_module("data/definition_typology_classifier.py")
    assert dt.strip_markup("{#deva#}¦ m. <s>deva</s> a god <ls>RV.</ls> <info lex=\"m\"/> {%x%}") \
        == "deva m. deva a god RV. x"
    recs = list(dt.extract_records(MW_MINI))
    assert [r[0] for r in recs] == ["1", "2", "3", "4", "5"]
    assert recs[2][1] == "agni" and "fire" in recs[2][2]
    assert dt.body_after_pipe("{#a#}¦ the def") == " the def"
    assert dt.body_after_pipe("no pipe") == "no pipe"
    assert dt.content_tokens("kṛṣṇa, the black one; देव") == ["kṛṣṇa", "the", "black", "one", "देव"]
    # A period counts only when NOT preceded by a letter (abbreviation guard):
    # "1899." and "(x)." count, "god." does not — the existing contract, pinned as is.
    assert dt.sentence_period_count("born 1899. died 1950. m. a god.") == 2
    assert dt.sentence_period_count("(x). y") == 1


def test_classify_priority_and_classes():
    dt = load_module("data/definition_typology_classifier.py")
    assert dt.CLASSES == ("synonym", "equivalent", "encyclopedic", "residual")
    for plain in ("", "m. N. of a man", "cf. deva", "= deva"):
        cls, reason = dt.classify(plain)
        assert cls in dt.CLASSES and isinstance(reason, str) and reason
    assert dt.classify("")[0] == "residual"
    assert dt.classify("m. a god, deity, divine being")[0] in ("synonym", "equivalent")


def test_classify_reproduces_committed_sample():
    """The committed 500-row sample carries `predicted`; re-classifying its excerpt
    must agree on every UNTRUNCATED excerpt and on ≥ 450/500 overall (excerpts are cut
    at 240 chars, so a few long bodies legitimately flip). Floors measured 08-09-2026."""
    import csv
    dt = load_module("data/definition_typology_classifier.py")
    with open(REPO / "data/definition_typology_sample.tsv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    assert len(rows) == 500
    assert set(r["predicted"] for r in rows) <= set(dt.CLASSES)
    agree = sum(dt.classify(r["plain_excerpt"])[0] == r["predicted"] for r in rows)
    assert agree >= 450, agree
    short = [r for r in rows if len(r["plain_excerpt"]) < 240]
    mismatch = [(r["dict"], r["l_id"]) for r in short
                if dt.classify(r["plain_excerpt"])[0] != r["predicted"]]
    assert len(short) > 100 and not mismatch, mismatch[:5]
    with open(REPO / "data/definition_typology_gold.tsv", encoding="utf-8") as fh:
        gold = list(csv.DictReader(fh, delimiter="\t"))
    assert len(gold) == 79 and all(g["gold"] in dt.CLASSES for g in gold)
    assert sum(g["predicted"] == g["gold"] for g in gold) >= 63          # 79.7 % gold agreement


def test_verify_sample_reports_and_warns(tmp_path, capsys):
    dt = load_module("data/definition_typology_classifier.py")
    hdr = "dict\tl_id\tk1\tpredicted\treason\tplain_excerpt\tgold\tnotes\n"
    ok = tmp_path / "ok.tsv"
    ok.write_text(hdr + "MW\t1\ta\tsynonym\tr\tb\tsynonym\t\nMW\t2\ta\tsynonym\tr\tb\tequivalent\t\n"
                  "MW\t3\ta\tsynonym\tr\tb\t\t\n", encoding="utf-8")
    dt.verify_sample(ok)
    out = capsys.readouterr().out
    assert "gold-filled rows: 2 (unfilled: 1)" in out and "accuracy: 1/2 = 50.0%" in out
    bad = tmp_path / "bad.tsv"
    bad.write_text(hdr + "MW\t1\ta\tsynonym\tr\tb\tbogus\t\n", encoding="utf-8")
    dt.verify_sample(bad)
    captured = capsys.readouterr()
    assert "WARN unknown gold label: 'bogus'" in captured.err
    assert "No gold labels found" in captured.out


# ------------------------------------------------------------- markup_tag_census
def test_census_file_counts_tags_and_entries():
    mt = load_module("data/markup_tag_census.py")
    entries, tags = mt.census_file(MW_MINI)
    assert entries == 5
    assert tags["<L>"] == 5 and tags["<ls>"] == 7 and tags["<k1>"] == 5   # 6 in bodies + 1 header
    assert tags["<info>"] == 1 and tags["<s1>"] == 1
    assert tags[mt.BRACE_LABEL["#"]] == 5 and tags[mt.BRACE_LABEL["%"]] == 1


def test_census_main_writes_tsv_and_refuses_missing_root(tmp_path):
    out = tmp_path / "census.tsv"
    r = subprocess.run([sys.executable, str(REPO / "data/markup_tag_census.py"),
                        "--csl-orig", str(FIXTURES / "csl_orig_mini"), "--out", str(out)],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "dict\tentries\ttag\tcount\tper_1000_entries"
    assert "mw\t5\t<ls>\t7\t1400.0" in lines[1:], lines
    r = subprocess.run([sys.executable, str(REPO / "data/markup_tag_census.py"),
                        "--csl-orig", str(tmp_path / "nope"), "--out", str(out)],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode != 0 and "not found" in r.stderr


# ------------------------------------------------------------ mw_ls_textattest
def test_mw_ls_textattest_l_only_headwords(tmp_path):
    """Run a COPY of the script so its beside-the-script output lands in tmp."""
    script = tmp_path / "mw_ls_textattest.py"
    shutil.copy(REPO / "data/mw_ls_textattest.py", script)
    r = subprocess.run([sys.executable, str(script), "--mw", str(MW_MINI)],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    out = tmp_path / "mw_non_textattested_slp1.txt"
    assert out.exists()
    got = set(out.read_text(encoding="utf-8").split())
    assert got == {"a", "deva"}                       # only <ls>L.</ls> → not text-attested
    r = subprocess.run([sys.executable, str(script), "--mw", str(tmp_path / "missing.txt")],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode != 0 and "not found" in r.stderr


# ---------------------------------------------------------- headword_overlap_matrix
def test_headword_overlap_matrix_on_mini_union(tmp_path):
    script = tmp_path / "headword_overlap_matrix.py"
    shutil.copy(REPO / "data/headword_overlap_matrix.py", script)
    r = subprocess.run([sys.executable, str(script), "--union", str(FIXTURES / "union_mini.tsv")],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    matrix = (tmp_path / "headword_overlap_matrix.tsv").read_text(encoding="utf-8").splitlines()
    uniq = (tmp_path / "headword_unique_counts.tsv").read_text(encoding="utf-8").splitlines()
    assert matrix[0] == "dict_a\tdict_b\tshared\tunion\tjaccard"
    rows = {tuple(l.split("\t")[:2]): l.split("\t") for l in matrix[1:]}
    assert rows[("MW", "PWG")][2:] == ["3", "4", "0.7500"]
    assert uniq[0] == "dict\theadwords\tunique_to_dict\tunique_share"
    urows = {l.split("\t")[0]: l.split("\t") for l in uniq[1:]}
    assert urows["MW"] == ["MW", "4", "1", "0.2500"] and urows["SKD"] == ["SKD", "1", "1", "1.0000"]
    assert "union rows: 5" in r.stdout


# ------------------------------------------------------ witness_independence_reaudit
def test_witness_policies_and_distribution():
    wi = load_module("data/witness_independence_reaudit.py")
    pol = wi.build_policies()
    assert [p[0] for p in pol] == ["P0", "P1", "P2", "P3", "P4"]
    p0 = pol[0][3]
    assert all(p0[d] == d for d in wi.ALL_DICTS)
    assert pol[1][3]["CAE"] == pol[1][3]["CCS"] == wi.CAP
    assert pol[3][3]["MW"] == wi.PETB and pol[3][3]["AP"] == "AP"      # Apte stays separate
    assert pol[4][3]["MD"] == wi.PETB
    rows = list(wi.load_union(FIXTURES / "union_mini.tsv"))
    assert rows[0] == ("A", ["AP", "MW", "PWG", "PWK"], 4)
    dist = wi.distribution(rows, p0)
    assert dist == Counter({4: 1, 5: 1, 2: 1, 1: 2})
    assert dist == Counter(n for _, _, n in rows)                    # P0 == file's n_dicts
    dist3 = wi.distribution(rows, pol[3][3])
    assert dist3[1] == 3                                             # MW+PWG(+PWK) → one witness
    masked = wi.distribution(rows, p0, mw_mask={"onlymw"})
    assert masked[0] == 1                                            # ghost falls to n=0
    cum, total = wi.cumulative_ge(dist)
    assert total == 5 and cum[1] == 5 and cum[4] == 2 and cum[5] == 1
    assert wi.MW_L_ONLY == 59697


# --------------------------------------------------------------- semdom_ak_bridge
def test_semdom_bridge_parsers_without_nltk():
    """nltk's wordnet is imported at module top; the parsers are pure — load defs only."""
    sb = load_defs("data/semdom_ak_bridge.py")
    amar = sb.parse_amar(FIXTURES / "amar_mini.txt")
    assert amar == [(sb.VARGA_IDS[0], 1, ["svar", "svarga", "nAka"]),
                    (sb.VARGA_IDS[0], 2, ["deva", "sura"]),
                    (sb.VARGA_IDS[1], 3, ["vyoman"])]
    mw = sb.parse_mw(MW_MINI)
    assert set(mw) == {"a", "akza", "agni", "deva", "devatA"}
    assert "<ls>" not in mw["agni"] and "fire" in mw["agni"]
    bridge = sb.load_bridge(FIXTURES / "wn_bridge_mini.tsv")
    assert bridge == {"01234567-n": {"1.1"}, "07654321-n": {"8.4"}}    # eng rows only
    assert sb.gloss_words("The God of Fire, an axle") == ["god", "fire", "axle"] or \
        set(sb.gloss_words("The God of Fire, an axle")) <= {"god", "fire", "axle"}


# ------------------------------------------------------ semdom_varga_crosswalk
def test_varga_crosswalk_loaders_offline(tmp_path):
    sv = load_module("data/semdom_varga_crosswalk.py")
    order, counts = sv.load_vargas(FIXTURES / "amar_mini.txt")
    assert order == ["svargavarga", "vyomavarga"]
    assert counts == {"svargavarga": 2, "vyomavarga": 1}
    sd = tmp_path / "semdom.json"
    sd.write_text('{"items": [{"key": "1.1", "label": "Universe"}]}', encoding="utf-8")
    assert sv.load_semdom(str(sd)) == {"1.1": {"key": "1.1", "label": "Universe"}}
    assert sv.EXCLUDED == {"AK-3.1", "AK-3.2", "AK-3.3", "AK-3.4"}


def test_varga_crosswalk_cache_miss_cannot_reach_network(monkeypatch, tmp_path):
    from conftest import NetworkDisabled
    sv = load_module("data/semdom_varga_crosswalk.py")
    monkeypatch.setattr(sv, "SEMDOM_CACHE", tmp_path / "absent.json")
    with pytest.raises(NetworkDisabled):
        sv.load_semdom(None)


def test_annex_subtree_codes():
    sa = load_module("data/semdom_ak_annex_table.py")
    domains = {"1": 0, "1.1": 0, "1.1.2": 0, "1.10": 0, "2": 0}
    assert sa.subtree_codes(domains, "1.1") == ["1.1", "1.1.2"]
    assert sa.subtree_codes(domains, "1") == ["1", "1.1", "1.1.2", "1.10"]
    assert sa.subtree_codes(domains, "3") == []


# ------------------------------------------------------------ viz/build_viz_pages
def test_build_viz_pages_refuses_missing_or_empty_feed(monkeypatch, tmp_path):
    bv = load_module("data/viz/build_viz_pages.py")
    monkeypatch.setattr(bv, "TSV", tmp_path / "absent.tsv")
    with pytest.raises(SystemExit) as e:
        bv.load_tsv()
    assert "STOP: missing feed" in str(e.value)
    monkeypatch.setattr(bv, "TSV", FIXTURES / "markup_tag_census_header_only.tsv")
    with pytest.raises(SystemExit) as e:
        bv.load_tsv()
    assert "STOP: empty TSV" in str(e.value)
    monkeypatch.setattr(bv, "TSV", FIXTURES / "markup_tag_census_mini.tsv")
    rows = bv.load_tsv()
    assert rows == [{"dict": "MW", "entries": 5, "tag": "<ls>", "count": 7, "per_1000_entries": 1400.0}]
    monkeypatch.setattr(bv, "JSON_PATH", tmp_path / "absent.json")
    with pytest.raises(SystemExit):
        bv.load_json()
