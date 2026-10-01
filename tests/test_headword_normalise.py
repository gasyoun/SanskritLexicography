"""HeadwordLists/ — the parse → normalise → emit contract (H4353).

Every pin here is on a pure function of a HeadwordLists module, fed either
a literal or a fixture under ``tests/fixtures``. Nothing reads csl-orig,
DCS, SanskritSpellCheck or the Heritage mirror: those roots are pointed at
a non-existent directory by ``conftest.py`` before any module is imported.
"""
from __future__ import annotations

import io
import os
import shutil
import unicodedata
from contextlib import redirect_stderr

import pytest

from conftest import FIXTURES, load_defs, load_module

ACUTE = "́"


# --------------------------------------------------------------- huet_coverage
def test_velthuis_to_iast_table_order_longest_first():
    """`.rr` must be tried before `.r`, `aa` before `a`: the table is ordered."""
    hc = load_module("HeadwordLists/huet_coverage.py")
    assert hc.vh_to_iast("k.r.s.na") == "kṛṣṇa"
    assert hc.vh_to_iast("t.rr") == "tṝ"
    assert hc.vh_to_iast("zaastra") == "śāstra"
    assert hc.vh_to_iast("a~nga") == "añga"
    assert hc.vh_to_iast("safga") == "saṅga"
    assert hc.vh_to_iast("ka.m") == "kaṃ"


def test_norm_huet_self_check_vectors():
    """The module's own docstring vectors, and the empty/garbage contract."""
    hc = load_module("HeadwordLists/huet_coverage.py")
    for vh, slp in (("a.mza", "aMSa"), ("akalafka", "akalaNka"),
                    ("akaa.n.da", "akARqa"), ("akani.s.thataa", "akanizWatA"),
                    ("akaaraprazle.sa", "akArapraSleza")):
        assert hc.norm_huet(vh) == slp, vh
    assert hc.norm_huet("  ") == ""
    assert hc.norm_huet("a-b_c$") == hc.norm_huet("abc")
    assert hc.norm_key("a/gni˚") == "agni"


def test_huet_norm_key_is_accent_and_ascii_clean():
    hc = load_module("HeadwordLists/huet_coverage.py")
    assert hc.ascii_clean("dévī") == "devi"
    assert hc.norm_key("deva/tA") == "devatA"


# ------------------------------------------------------------ headword_diff
def test_key2_forms_splits_commas_and_strips_deva_markup():
    hd = load_module("HeadwordLists/headword_diff.py")
    src = FIXTURES / "csl_orig_mini" / "mw" / "mw.txt"
    assert hd.field_set(src, "k1") == {"a", "akza", "agni", "deva", "devatA"}
    assert hd.key2_forms(src) == {"a", "akza", "agni/", "deva/", "devI", "deva-tA"}
    assert hd.now_set(str(src), "1") == hd.field_set(src, "k1")
    assert hd.now_set(str(src), "2") == hd.key2_forms(src)


def test_key2_forms_stops_at_separator_and_length(tmp_path):
    hd = load_module("HeadwordLists/headword_diff.py")
    p = tmp_path / "x.txt"
    p.write_text(
        "<L>1<pc>1<k1>a<k2>a¦ body text that must not leak<h>1\n"
        "<L>2<pc>1<k1>b<k2>" + "b" * 81 + "\n"
        "<L>3<pc>1<k1>c<k2>“quoted”\n"
        "<L>4<pc>1<k1>d<k2>{#d#}, {#e#}\n", encoding="utf-8")
    assert hd.key2_forms(p) == {"a", "d", "e"}


def test_sanskrit_key_is_varna_krama_not_ascii():
    """a < A < i < ... < M < H < k ... < h < L; unknown chars sort after."""
    hd = load_module("HeadwordLists/headword_diff.py")
    order = sorted(["ka", "aM", "A", "a", "i", "h", "L", "f", "e", "H"], key=hd.sanskrit_key)
    assert order == ["a", "aM", "A", "i", "f", "e", "H", "ka", "h", "L"]
    assert sorted(["kz", "kK"], key=hd.sanskrit_key) == ["kK", "kz"]
    assert hd.sanskrit_key("a-") > hd.sanskrit_key("aL")  # punctuation after letters
    assert hd._SLP1_ORDER == "aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL"


# ------------------------------------------------------- Catalan-Pujol scripts
def test_match_rate_norm_cat():
    mr = load_defs("HeadwordLists/Catalan-Pujol/match_rate.py")
    assert mr.norm_cat("√kṛ") == ("kf", True)
    assert mr.norm_cat("deva-tā (f.)") == ("devatA", False)
    assert mr.norm_cat("deva-tā", joinhyphen=False) == ("deva-tA", False)
    assert mr.norm_cat("agní 2") == ("agni", False)
    assert mr.norm_cat("˚gata,") == ("gata", False)
    assert mr.norm_cat("") == ("", False)


def test_make_uncovered_lists_categorize():
    mu = load_defs("HeadwordLists/Catalan-Pujol/make_uncovered_lists.py")
    assert mu.categorize("√kṛ", "kf") == "root"
    assert mu.categorize("pra-√kṛ", "prakf") == "prefixed-root"
    assert mu.categorize("deva-tā", "devatA") == "compound(2)"
    assert mu.categorize("deva-rāja-putra", "devarAjaputra") == "long-compound(3+)"
    assert mu.categorize("deva", "deva") == "simple"
    assert mu.categorize("de•va", "deva") == "suspect-char"


def test_coverage_vs_dcs_classify_buckets():
    cv = load_defs("HeadwordLists/Catalan-Pujol/coverage_vs_dcs.py")
    assert cv.classify("pra-√kṛ")[0] == "verb"
    assert cv.classify("jigīṣā")[0] == "verb"
    assert cv.classify("svāhā")[0] == "bija"
    assert cv.classify("deva-tā")[0] == "deriv"
    assert cv.classify("deva-rāja")[0] == "compound"
    assert cv.classify("deva")[0] == "simple"


def test_accent_compare_pujol_entry_records_vowel_ordinals():
    ac = load_defs("HeadwordLists/Catalan-Pujol/accent_compare.py")
    assert ac.slp_vowel_ordinal("agn") == 1
    assert ac.slp_vowel_ordinal("devatA") == 3
    key, ords = ac.pujol_entry("agní")
    assert key == "agni" and ords == frozenset({2})
    key, ords = ac.pujol_entry("dévatā (f.) 2")
    assert key == "devatA" and ords == frozenset({1})
    assert ac.pujol_entry("√kṛ")[0] == "kf"
    assert ac.pujol_entry("   ") is None
    # Diacritics are letters, not accents: before the H4353 fix these keyed as
    # 'krsna' / 'atman' / 'siva' and never met their Cologne forms.
    assert ac.pujol_entry("kṛṣṇa") == ("kfzRa", frozenset())
    assert ac.pujol_entry("ātmán") == ("Atman", frozenset({2}))
    assert ac.pujol_entry("śiva") == ("Siva", frozenset())
    assert ac.pujol_entry("ā́ṃśa-") == ("AMSa", frozenset({1}))


def test_accent_review_pujol_accents_keeps_diacritics(monkeypatch, tmp_path):
    ar = load_module("HeadwordLists/accent_review.py")
    cat = tmp_path / "cat.txt"
    cat.write_text("kṛ́ṣṇa\nātmán\nagní\nagni\n", encoding="utf-8")
    monkeypatch.setattr(ar, "CAT", str(cat))
    out = ar.pujol_accents()
    assert out["kfzRa"] == {frozenset({1})}
    assert out["Atman"] == {frozenset({2})}
    assert out["agni"] == {frozenset({2}), frozenset()}


def test_coverage_by_dict_norm_cat_matches_match_rate():
    cb = load_defs("HeadwordLists/Catalan-Pujol/coverage_by_dict.py")
    mr = load_defs("HeadwordLists/Catalan-Pujol/match_rate.py")
    for hw in ("agní", "deva-tā", "√kṛ", "˚gata"):
        assert cb.norm_cat(hw) == mr.norm_cat(hw)[0]


# -------------------------------------------------------------- accent_review
def test_accented_iast_places_acute_on_named_vowels():
    ar = load_module("HeadwordLists/accent_review.py")
    assert ar.accented_iast("agni", frozenset({2})) == unicodedata.normalize("NFC", "agni" + "")[:3] + "í"
    assert ar.accented_iast("devatA", frozenset({1, 3})) == unicodedata.normalize("NFC", "dévatā́")
    assert ar.accented_iast("kf", frozenset()) == "kṛ"
    assert ar.has_acc([frozenset(), frozenset({1})]) is True
    assert ar.has_acc([frozenset(), frozenset()]) is False
    assert ar.best([frozenset({1}), frozenset({1, 2})]) == frozenset({1, 2})
    assert ar.best([]) == frozenset()


# --------------------------------------------------------- alternate_headwords
def test_variant_pairs_b_v_s_and_geminate():
    ah = load_module("HeadwordLists/alternate_headwords.py")
    ks = {"bala", "vala", "SavAsa", "zavAsa", "atta", "ata", "kAma"}
    assert ah.variant_pairs(ks) == {("bala", "vala"), ("SavAsa", "zavAsa"), ("ata", "atta")}
    assert ah.iast("kfzRa") == "kṛṣṇa"
    assert ah.now_key1("NOPE") is None


# ----------------------------------------------------------- assemble_typo_queue
def test_err_label_classifies_single_edit_confusions():
    at = load_module("HeadwordLists/assemble_typo_queue.py")
    assert at.err_label("kfzna", "kfzRa") == "dental→retroflex (n→ṇ)"
    assert at.err_label("bala", "vala") == "b↔v"
    assert at.err_label("deva", "devA") == "vowel length (a↔ā)"
    assert at.err_label("Siva", "ziva") == "sibilant (ś→ṣ)"
    assert at.err_label("kama", "kAma") == "vowel length (a↔ā)"
    assert at.err_label("kaMa", "kaka") == "M→k"        # unknown single edit: literal
    assert at.err_label("ka", "kaa") == "spelling"      # length differs
    assert at.err_label("abcd", "abxy") == "spelling"   # two edits


# ------------------------------------------------------------------ build_union
def test_gender_letters_and_dict_roster():
    bu = load_module("HeadwordLists/build_union.py")
    assert bu.gender_letters("m.") == frozenset("m")
    assert bu.gender_letters("mfn") == frozenset("mfn")
    assert bu.gender_letters("ind.") == frozenset()
    assert bu.gender_letters("f. pl.") == frozenset("f")
    assert bu.DICTS == ["AP", "BHS", "BUR", "CAE", "CCS", "GRA", "INM", "MD", "MW",
                        "PWG", "PWK", "SCH", "SKD", "VCP", "VEI"]
    assert bu.iast("kfzRa") == "kṛṣṇa"


# ----------------------------------------------------------- coverage_additions
def test_coverage_additions_norm_key():
    ca = load_module("HeadwordLists/coverage_additions.py")
    assert ca.norm_key("a/gni˚") == "agni"
    assert ca.ascii_clean("dévī") == "devi"
    assert ca.iast("devatA") == "devatā"


def test_crosstag_norm_cat_uses_huet_norm_key():
    ct = load_module("HeadwordLists/crosstag_additions.py")
    assert ct.norm_cat("agní") == "agni"
    assert ct.norm_cat("deva-tā (f.)") == "devatA"
    assert ct.norm_cat("√kṛ") == "kf"


# --------------------------------------------------------- heritage_freq_diff
def test_wx_to_slp1_swaps_dental_and_retroflex_rows():
    hf = load_module("HeadwordLists/heritage_freq_diff.py")
    assert hf.wx_to_slp1("waw") == "tat"
    assert hf.wx_to_slp1("Xarma") == "Darma"
    assert hf.wx_to_slp1("kAma") == "kAma"
    assert hf.wx_to_slp1("haswin") == "hastin"     # WX t = SLP1 w (retroflex), WX w = dental t
    assert hf.wx_to_slp1("a?b") == "a?b" and hf._UNMAPPED.get("?", 0) >= 1   # unmapped chars pass through, counted


def test_freq_tsv_loaders_skip_non_numeric_rows():
    hf = load_module("HeadwordLists/heritage_freq_diff.py")
    rows = hf.load_freq_tsv(FIXTURES / "freq_mini.tsv")
    assert rows == [("waw", 100), ("Xarma", 40), ("kAma", 40)]
    assert hf.transcode_series(rows) == [("tat", 100), ("Darma", 40), ("kAma", 40)]
    agg = hf.load_morph_freq_tsv(FIXTURES / "freq_mini.tsv")
    assert agg == [("waw", 100), ("Xarma", 40), ("kAma", 40)]
    assert hf.ranks_from_sorted(rows) == {"waw": 1, "Xarma": 2, "kAma": 3}


def test_spearman_local_ranks_and_ties():
    hf = load_module("HeadwordLists/heritage_freq_diff.py")
    assert hf._avg_ranks([10, 30, 20]) == [3.0, 1.0, 2.0]
    assert hf._avg_ranks([5, 5, 1]) == [1.5, 1.5, 3.0]
    assert hf.spearman([(1, 1), (2, 2), (3, 3)]) == pytest.approx(1.0)
    assert hf.spearman([(1, 3), (2, 2), (3, 1)]) == pytest.approx(-1.0)
    assert hf.spearman([(1, 1)]) is None
    rho = hf.spearman([(1, 2), (2, 1), (3, 4), (4, 3)])
    assert -1.0 <= rho <= 1.0


# ------------------------------------------------------- heritage_forms_oracle
def test_nasal_norm_canonicalises_final_and_preconsonantal_nasals():
    ho = load_module("HeadwordLists/heritage_forms_oracle.py")
    assert ho.nasal_norm("AvAsam") == "AvAsaM"
    assert ho.nasal_norm("oNkAra") == "oMkAra"
    assert ho.nasal_norm("BayaNkara") == "BayaMkara"
    assert ho.nasal_norm("kAmana") == "kAmana"      # nasal before vowel untouched
    assert ho.nasal_norm("") == ""
    assert ho.norm_set({"AvAsam", "AvAsaM"}) == {"AvAsaM"}
    assert ho.prefix_related({"garh"}, {"garhita"}) is True
    assert ho.prefix_related({"Ir"}, {"Iray"}) is False      # shorter than minlen
    assert ho.prefix_related({"deva"}, {"deva"}) is False    # identity is not relation


# --------------------------------------------------------- heritage_stem_extract
def test_heritage_stem_extract_strips_u_prefix_and_hash(monkeypatch):
    hs = load_module("HeadwordLists/heritage_stem_extract.py")
    monkeypatch.setattr(hs, "MIRROR_DICO", str(FIXTURES / "heritage_mirror" / "DICO"))
    keys, dropped_affix, nfiles = hs.extract()
    assert keys == {"kumbha", "deva", "devī"}
    assert dropped_affix == 1 and nfiles == 1


def test_heritage_stem_extract_refuses_empty_mirror(monkeypatch, tmp_path):
    hs = load_module("HeadwordLists/heritage_stem_extract.py")
    monkeypatch.setattr(hs, "MIRROR_DICO", str(tmp_path))
    with pytest.raises(SystemExit):
        hs.extract()


# --------------------------------------------------------- heritage_mw_crosswalk
def test_heritage_mw_crosswalk_dico_index_and_entry_clusters(monkeypatch):
    hm = load_module("HeadwordLists/heritage_mw_crosswalk.py")
    monkeypatch.setattr(hm, "MIRROR", str(FIXTURES / "heritage_mirror"))
    idx = hm.build_dico_index()
    assert idx == {"Ukumbha#1": "DICO/1.html#Ukumbha#1", "-tva": "DICO/1.html#-tva",
                   "deva": "DICO/1.html#deva", "devī": "DICO/1.html#devī"}
    text = (FIXTURES / "heritage_mirror" / "MW" / "mw_mini.html").read_text(encoding="utf-8")
    assert list(hm.entries_in_file(text)) == [("deva", True), ("devatA", False)]


# ---------------------------------------------------- heritage_dico_gloss_extract
def test_dico_gloss_entry_spans_and_strip_html():
    hg = load_module("HeadwordLists/heritage_dico_gloss_extract.py")
    text = (FIXTURES / "heritage_mirror" / "DICO" / "1.html").read_text(encoding="utf-8")
    spans = list(hg.entry_spans(text))
    keys = [k for k, _, _ in spans]
    assert keys == ["Ukumbha#1", "-tva", "deva", "devī"]
    glosses = {k: hg.strip_html(text[s:e]) for k, s, e in spans}
    assert glosses["Ukumbha#1"].startswith("कुम्भ kumbha [m.] pot; see ghaṭa")
    assert "deva" not in glosses["-tva"]                 # next entry does not leak
    assert glosses["devī"] == "देवी devī [f.] goddess."
    assert hg.strip_html("a&#160;<b>b</b>&amp;") == "a b &"
    assert hg.is_entry_boundary("<p>" + '<a class="navy"', 3) is True
    assert hg.is_entry_boundary("word " + '<a class="navy"', 5) is False


# ------------------------------------------------------ heritage_coverage_current
def test_greedy_coverage_order_and_stop():
    hc = load_module("HeadwordLists/heritage_coverage_current.py")
    keys = {"a", "b", "c", "d"}
    dsets = {"MW": {"a", "b"}, "PWG": {"a", "b", "c"}, "AP": {"z"}}
    covered, order = hc.coverage(keys, dsets)
    assert covered == {"a", "b", "c"}
    assert [o[0] for o in order] == ["PWG"]
    assert order[0][1:] == (3, 3, 75.0)


# ----------------------------------------------------------- screen_candidates
def test_screen_candidates_words_tokeniser():
    """Phrases between punctuation, lower-cased, >2 chars, stop-phrases dropped."""
    sc = load_module("HeadwordLists/screen_candidates.py")
    assert sc.words("The god of fire, or the fire-god. A deity; the") == \
        {"the god of fire", "or the fire", "god", "a deity"}
    assert sc.words("the, of, a") == set()
    assert sc.words("Kṛṣṇa") == {"kṛṣṇa"}


# ------------------------------------------------------------- cologne_k2 etc.
def test_cologne_k2_reads_a_csl_orig_layout(monkeypatch):
    """accent_compare.cologne_k2 walks ORIG/<dict>/<dict>.txt — on the fixture only."""
    ac = load_defs("HeadwordLists/Catalan-Pujol/accent_compare.py")
    monkeypatch.setattr(ac, "ORIG", str(FIXTURES / "csl_orig_mini"))
    out = ac.cologne_k2("mw")
    assert out["agni"] == {frozenset({2})}            # agni/ → udātta on vowel 2
    assert out["a"] == {frozenset()} and out["devatA"] == {frozenset()}
    assert "deva, devI" in out                         # raw <k2> comma-list is NOT split here
    assert ac.has_acc(out["agni"]) and not ac.has_acc(out["a"])


def test_external_roots_are_pointed_nowhere():
    for var in ("CSL_ORIG_V02", "PWG_INPUT_DIR", "DCS_LEMMA_SUMMARY", "SSC_DIR"):
        assert not os.path.exists(os.environ[var]), var
    hd = load_module("HeadwordLists/headword_diff.py")
    assert hd.src_path("mw") is None
    hc = load_module("HeadwordLists/huet_coverage.py")
    assert hc.load_k1("mw") == set()
