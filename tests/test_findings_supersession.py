"""findings_supersession.py — supersession DAG parser over FINDINGS.md (H7594).

Pins: the relation forms (SUPERSEDED/EXTENDED/REFUTED/CLOSED ... by §N|H####,
"extends §N", the builds-on citations), zone attribution (index row -> body
span -> header blurb), the in-place annotation forms (``**SUPERSEDED IN PART``,
``**Update``, "annotated in-place by"), chain orientation (stale -> current,
H-targets never join, fork + cycle guard), the stale-pointer flag classes
(ghost index rows, anchor drift beyond slugger dialect, dangling Sec targets),
``chain_panels`` and the ``write_json``/``main`` CLI contract. The real-repo
canary re-runs the module's own known-chain selftest against the committed
FINDINGS.md.

Offline: pure string fixtures plus the in-repo FINDINGS.md — no network, no
git, nothing written outside tmp_path.
"""
from __future__ import annotations

import json
import re

import pytest

from conftest import REPO, load_module

fs = load_module("tools/findings_supersession.py")

REAL = (REPO / "FINDINGS.md").read_text(encoding="utf-8")

# ------------------------------------------------------------------- fixtures
MD_RELATIONS = """\
### §20. Alpha
refuted by §21 the same day.
### §21. Beta
extended by H0001 later.
### §22. Gamma
SUPERSEDED IN PART by §23 after review.
### §23. Delta
closed by H0002 at the end.
"""

MD_TITLE_CASE = """\
### §19. Title case probe
Refuted by §21 title-case is not a relation keyword.
"""

MD_EXTENDS_CASE = """\
### §28. Case extends
EXTENDS §27 upper-case form
### §27. Base
body
"""

MD_LINK_FORM = """\
### §29. Link form
superseded in part by [§30](#30-target-name) with a markdown link.
### §30. Target name
body
"""

MD_ZONES = """\
_Created: 01-01-2026 · Last updated: 01-01-2026 (prior: §31 — superseded by §32 note.)
## Index
- 🟠 [§30. Indexed](#30-indexed) — superseded by §31
## Findings
### §30. Indexed
BODY superseded by §31 note.
### §31. Successor
clean body
### §32. Later
clean body
"""

MD_HEADER = """\
_Created: 01-01-2026 · Last updated: 01-01-2026 (§40 — retraction note, annotated in-place by H2468; prior: §39 closed by H1357 — earlier work.)
# FINDINGS
### §39. Earlier
body
### §40. Retracted
body with **SUPERSEDED (H2468, 01-01-2026):** detail
### §41. Fresh
body
"""

MD_INPLACE_FORMS = """\
### §25. Case probe
**superseded (H2222):** lowercase is not an in-place marker
### §26. Warn probe
**⚠️ SUPERSEDED (H3333):** warned form
### §27. Bare update
**Update 01-11-2026:** no handoff id
"""

MD_INPLACE_INDEX = """\
## Index
- 🟠 [§80. Annotated](#80-annotated) — **SUPERSEDED (H1111):**
## Findings
### §80. Annotated
stable body
"""

MD_AFTER_BREAK = """\
### §70. Last finding
stable body
## Appendix
superseded by §71 after the section break
"""

MD_FLAGS = """\
## Index
- 🟠 [§50. Real one](#50-real-one)
- 🟠 [§103. Renumber ghost](#103-ghost)
- 🟡 [§51. lemma_id drift check](#51-lemmaid-drift-check)
- 🟠 [§52. Renamed finding](#52-old-name)
## Findings
### §50. Real one
superseded by §777 nowhere.
### §51. lemma_id drift check
body
### §52. Renamed finding
body
"""

MD_CLEAN = """\
## Index
- 🟢 [§60. Whole](#60-whole)
## Findings
### §60. Whole
stable body
"""


def chain_of(sup, n):
    return next(c for c in sup["chains"] if n in c["chain"])


# --------------------------------------------------------------- pure helpers
def test_slugify_matches_findings_dashboard_dialect():
    assert fs.slugify("12. Third finding") == "12-third-finding"
    assert fs.slugify("Heritage×kosha form agrees 78.3%") == \
        "heritagekosha-form-agrees-783"
    assert fs.slugify("lemma_id drift check") == "lemma_id-drift-check"


def test_norm_anchor_is_slugger_dialect_insensitive():
    # dropped underscores and collapsed dash runs are the OTHER slugger's
    # dialect; only real title drift may flag (H7594 stale-pointer contract)
    assert fs._norm_anchor("#10_old--claim") == fs._norm_anchor("#10old-claim")
    assert fs._norm_anchor("#51-lemmaid-drift-check") == \
        fs._norm_anchor("#51-lemma_id-drift-check")
    assert fs._norm_anchor("#10-old-claim") != fs._norm_anchor("#10-new-claim")


def test_parse_findings_canonical_headings_only():
    md = """\
### §1. Alpha thing
### §2 Beta no dot
#### §3. Deep — not h3
### §4. Gamma!
"""
    f = fs.parse_findings(md)
    assert set(f) == {1, 4}
    assert f[1] == {"title": "Alpha thing", "anchor": "1-alpha-thing"}
    assert f[4] == {"title": "Gamma!", "anchor": "4-gamma"}


def test_parse_index_rows_four_dots_only():
    md = """\
- 🔴 [§1. Hot](#1-hot)
- 🟠 [§2. Warm](#2-warm)
- 🟡 [§3. Mild](#3-mild)
- 🟢 [§4. Cool](#4-cool)
- [§5. No dot](#5-no-dot)
- ❌ [§6. Bad dot](#6-bad)
"""
    rows = fs.parse_index_rows(md)
    assert [(r["n"], r["dot"]) for r in rows] == \
        [(1, "🔴"), (2, "🟠"), (3, "🟡"), (4, "🟢")]
    assert rows[0]["title"] == "Hot" and rows[0]["anchor"] == "1-hot"
    assert [r["n"] for r in fs.parse_index_rows(MD_FLAGS)] == [50, 103, 51, 52]


# ----------------------------------------------------------- relation parsing
def test_relation_forms_all_four_with_line_numbers():
    sup = fs.parse_supersession(MD_RELATIONS)
    edges = sup["edges"]
    assert {(e["from"], e["to"], e["relation"]) for e in edges} == {
        (20, "§21", "refuted_by"),
        (21, "H0001", "extended_by"),
        (22, "§23", "superseded_by"),
        (23, "H0002", "closed_by"),
    }
    assert [e["line"] for e in edges] == [2, 4, 6, 8]
    assert edges[0]["quote"] == "refuted by §21"
    assert sup["in_place"] == [] and sup["prose_superseded"] == []
    assert sup["findings_count"] == 4
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", sup["generated_at"])


def test_title_case_is_not_a_relation_keyword():
    # the keyword alternation is ALL-CAPS or lowercase only; "Refuted by §N"
    # must not invent an edge (real registry uses lower/caps forms)
    sup = fs.parse_supersession(MD_TITLE_CASE)
    assert sup["edges"] == [] and sup["chains"] == []


def test_extends_is_case_insensitive_and_orientation_is_active():
    sup = fs.parse_supersession(MD_EXTENDS_CASE)
    assert [(e["from"], e["to"], e["relation"]) for e in sup["edges"]] == \
        [(28, "§27", "extends")]
    c = chain_of(sup, 27)
    assert c["chain"] == [27, 28] and c["leaf"] == 28
    assert c["relations"] == ["extends"] and c["fork"] is False


def test_markdown_link_target_form():
    sup = fs.parse_supersession(MD_LINK_FORM)
    assert [(e["from"], e["to"], e["relation"]) for e in sup["edges"]] == \
        [(29, "§30", "superseded_by")]
    assert chain_of(sup, 29)["leaf"] == 30


# --------------------------------------------------------- zone attribution
def test_index_row_body_and_header_attribution():
    sup = fs.parse_supersession(MD_ZONES)
    # same relation text in three zones: index row -> §30, body -> §30,
    # header blurb -> the Sec named by "prior:" before it -> §31
    assert [(e["from"], e["line"]) for e in sup["edges"]] == \
        [(31, 1), (30, 3), (30, 6)]
    assert {e["relation"] for e in sup["edges"]} == {"superseded_by"}
    # duplicate edges collapse into one walk: 30 -> 31 -> 32
    assert len(sup["chains"]) == 1
    c = sup["chains"][0]
    assert c["chain"] == [30, 31, 32] and c["leaf"] == 32
    assert c["relations"] == ["superseded_by", "superseded_by"]
    assert c["fork"] is False


def test_header_subject_and_handoff_edges():
    sup = fs.parse_supersession(MD_HEADER)
    # the header blurb attributes "closed by H1357" to prior: §39, and the
    # "annotated in-place by" note to the §40 named before it
    assert sup["edges"] == [{"from": 39, "to": "H1357", "relation": "closed_by",
                             "line": 1, "quote": "closed by H1357"}]
    assert sup["in_place"] == [
        {"n": 40, "handoff": "H2468", "kind": "superseded_in_place",
         "line": 6, "quote": "**SUPERSEDED (H2468"},
        {"n": 40, "handoff": "H2468", "kind": "annotated_in_place",
         "line": 1, "quote": "annotated in-place by H2468"},
    ]
    # H-targets never join a chain
    assert sup["chains"] == []
    assert sup["flags"] == {"ghost_index_rows": [], "anchor_drift": [],
                            "dangling_edge_targets": []}


def test_inplace_annotation_forms():
    sup = fs.parse_supersession(MD_INPLACE_FORMS)
    kinds = {(a["n"], a["handoff"], a["kind"]) for a in sup["in_place"]}
    # lowercase **superseded is NOT a marker (regex is uppercase-only);
    # the ⚠️ variant and the bare Update note are
    assert kinds == {(26, "H3333", "superseded_in_place"),
                     (27, None, "update_note")}
    assert sup["edges"] == []


def test_inplace_marker_inside_an_index_row_is_ignored():
    sup = fs.parse_supersession(MD_INPLACE_INDEX)
    # in-place annotations only count inside the finding's own body
    assert sup["in_place"] == [] and sup["edges"] == []


def test_relation_after_h2_break_has_no_subject():
    sup = fs.parse_supersession(MD_AFTER_BREAK)
    # the "## Appendix" heading ends §70's body span; the relation past it
    # has no subject and must not invent an edge
    assert sup["edges"] == [] and sup["chains"] == []


def test_zero_findings_refused(tmp_path):
    bad = tmp_path / "bad.md"
    bad.write_text("no sections here\njust prose\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="REFUSED"):
        fs.parse_supersession(bad.read_text(encoding="utf-8"))
    with pytest.raises(SystemExit, match="REFUSED"):
        fs.main(["prog", "--md", str(bad)])


# ------------------------------------------------------------------- chains
def test_build_chains_orientation_passive_vs_active():
    passive = fs.build_chains({}, [{"from": 5, "to": "§6",
                                    "relation": "superseded_by"}])
    assert passive == [{"chain": [5, 6], "leaf": 6, "fork": False,
                        "relations": ["superseded_by"]}]
    active = fs.build_chains({}, [{"from": 6, "to": "§5",
                                   "relation": "builds_on"}])
    assert active == [{"chain": [5, 6], "leaf": 6, "fork": False,
                       "relations": ["builds_on"]}]


def test_build_chains_fork_flag_picks_sorted_first_successor():
    chains = fs.build_chains({}, [
        {"from": 5, "to": "§6", "relation": "superseded_by"},
        {"from": 5, "to": "§7", "relation": "closed_by"},
    ])
    assert len(chains) == 1
    c = chains[0]
    assert c["chain"] == [5, 6] and c["leaf"] == 6 and c["fork"] is True
    assert c["relations"] == ["superseded_by"]


def test_build_chains_cycle_guard_stops_with_fork():
    # a successor that loops back onto itself terminates the walk, fork=True
    chains = fs.build_chains({}, [
        {"from": 5, "to": "§6", "relation": "superseded_by"},
        {"from": 6, "to": "§6", "relation": "superseded_by"},
    ])
    assert len(chains) == 1
    c = chains[0]
    assert c["chain"] == [5, 6] and c["leaf"] == 6 and c["fork"] is True
    assert c["relations"] == ["superseded_by"]


def test_build_chains_ignores_handoff_targets():
    assert fs.build_chains({}, [{"from": 40, "to": "H7497",
                                 "relation": "superseded_by"}]) == []


# ------------------------------------------------------------------- flags
def test_check_flags_classes_and_dialect_tolerance():
    findings = {
        10: {"title": "A", "anchor": "10-a"},
        11: {"title": "B", "anchor": "11-b_id"},
        12: {"title": "C", "anchor": "12-c"},
    }
    rows = [
        {"n": 10, "dot": "🟢", "title": "A", "anchor": "10-a"},
        {"n": 103, "dot": "🟠", "title": "Ghost", "anchor": "103-ghost"},
        {"n": 11, "dot": "🟡", "title": "B", "anchor": "11-bid"},   # dialect-ok
        {"n": 12, "dot": "🟠", "title": "C", "anchor": "12-old-c"},  # real drift
    ]
    edges = [
        {"from": 10, "to": "§999", "relation": "superseded_by"},
        {"from": 10, "to": "H4321", "relation": "closed_by"},
    ]
    flags = fs.check_flags(findings, rows, edges)
    assert flags["ghost_index_rows"] == [{"n": 103, "title": "Ghost"}]
    assert flags["anchor_drift"] == [
        {"n": 12, "index_anchor": "12-old-c", "heading_anchor": "12-c"}]
    assert flags["dangling_edge_targets"] == ["§999"]  # H4321 excluded


def test_flags_full_pipeline_dangling_target_still_chains():
    sup = fs.parse_supersession(MD_FLAGS)
    flags = sup["flags"]
    assert flags["ghost_index_rows"] == [{"n": 103, "title": "Renumber ghost"}]
    assert flags["anchor_drift"] == [
        {"n": 52, "index_anchor": "52-old-name",
         "heading_anchor": "52-renamed-finding"}]
    assert flags["dangling_edge_targets"] == ["§777"]
    # a dangling target still joins the chain — the flag is the gate
    assert {tuple(c["chain"]) for c in sup["chains"]} == {(50, 777)}


# ------------------------------------------------------------------- panels
def test_chain_panels_payload():
    sup = fs.parse_supersession(MD_HEADER)
    findings = fs.parse_findings(MD_HEADER)
    panels = fs.chain_panels(sup, findings)
    assert panels["chains"] == []
    assert panels["lone_in_place"] == [
        {"n": 40, "handoff": "H2468", "kind": "superseded_in_place"},
        {"n": 40, "handoff": "H2468", "kind": "annotated_in_place"},
    ]
    assert panels["handoff_edges"] == [
        {"n": 39, "handoff": "H1357", "relation": "closed_by"}]
    assert panels["flags"] == sup["flags"]

    sup2 = fs.parse_supersession(MD_ZONES)
    panels2 = fs.chain_panels(sup2, fs.parse_findings(MD_ZONES))
    assert len(panels2["chains"]) == 1
    p = panels2["chains"][0]
    assert p["chain"] == [30, 31, 32] and p["leaf"] == 32
    assert p["leaf_title"] == "Later" and p["leaf_anchor"] == "32-later"
    assert p["in_place"] == [] and panels2["lone_in_place"] == []
    assert panels2["handoff_edges"] == []


# -------------------------------------------------------------------- CLI/io
def test_write_json_roundtrip_ensure_ascii_false(tmp_path, monkeypatch, capsys):
    out = tmp_path / "findings_supersession.json"
    monkeypatch.setattr(fs, "REPO", tmp_path)
    monkeypatch.setattr(fs, "OUT_PATH", out)
    sup = fs.parse_supersession(MD_FLAGS)
    fs.write_json(sup, fs.parse_findings(MD_FLAGS))
    assert out.exists()
    raw = out.read_text(encoding="utf-8")
    # ensure_ascii=False keeps the Sec sign literal (not \u00a7 escapes)
    assert '"§777"' in raw
    d = json.loads(raw)
    assert set(d) == {"generated_at", "findings_count", "edges", "in_place",
                      "prose_superseded", "chains", "flags", "panels"}
    assert d["panels"]["flags"]["dangling_edge_targets"] == ["§777"]
    assert "findings_supersession.json" in capsys.readouterr().out


def test_main_default_mode_writes_json(tmp_path, monkeypatch):
    clean = tmp_path / "clean.md"
    clean.write_text(MD_CLEAN, encoding="utf-8")
    out = tmp_path / "out" / "findings_supersession.json"
    monkeypatch.setattr(fs, "REPO", tmp_path)
    monkeypatch.setattr(fs, "OUT_PATH", out)
    assert fs.main(["prog", "--md", str(clean)]) == 0
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["findings_count"] == 1 and d["chains"] == []
    assert "panels" in d


def test_main_check_clean_exit_zero(tmp_path, capsys):
    clean = tmp_path / "clean.md"
    clean.write_text(MD_CLEAN, encoding="utf-8")
    assert fs.main(["prog", "--md", str(clean), "--check"]) == 0
    out = capsys.readouterr().out
    assert "CHECK PASS" in out and "zero stale pointers" in out


def test_main_check_flagged_exit_one(tmp_path, capsys):
    flagged = tmp_path / "flagged.md"
    flagged.write_text(MD_FLAGS, encoding="utf-8")
    assert fs.main(["prog", "--md", str(flagged), "--check"]) == 1
    out = capsys.readouterr().out
    assert "FLAG ghost index row: Sec-103" in out
    assert "FLAG anchor drift: Sec-52" in out
    assert "FLAG dangling edge target: §777" in out


def test_main_selftest_on_real_repo(capsys):
    assert fs.main(["prog", "--selftest"]) == 0
    assert "SELFTEST PASS" in capsys.readouterr().out


def test_selftest_fails_on_synthetic_data(capsys):
    # guards against a vacuous always-pass selftest: the known-chain checks
    # are pinned to the REAL FINDINGS.md, a synthetic registry must fail them
    sup = fs.parse_supersession(MD_RELATIONS)
    assert fs.selftest(sup) == 1
    assert "FAIL" in capsys.readouterr().out


# ------------------------------------------------------------- real-repo canary
def test_real_repo_known_chains_and_clean_flags():
    sup = fs.parse_supersession(REAL)
    findings = fs.parse_findings(REAL)
    assert sup["findings_count"] == len(findings) and len(findings) >= 300
    # the pre-renumbering finding lives at §451 (H1361); today's §103 is a
    # different, later finding — the struck thing was its stale index ROW
    assert 451 in findings
    # the four known chains (selftest textual anchors)
    assert chain_of(sup, 458)["chain"][-1] == 650
    assert chain_of(sup, 458)["relations"] == ["builds_on"]
    assert chain_of(sup, 447)["chain"][-1] == 453
    assert chain_of(sup, 447)["relations"] == ["builds_on"]
    assert chain_of(sup, 508)["chain"][-1] == 651
    assert chain_of(sup, 508)["relations"] == ["extends"]
    assert chain_of(sup, 18)["chain"][-1] == 579
    # in-place annotations on real data
    ip = {(a["n"], a["handoff"]) for a in sup["in_place"] if a["handoff"]}
    assert (40, "H7497") in ip and (465, "H1670") in ip
    # the stale-pointer gate is clean and the defensive prose list stays empty
    assert sup["flags"] == {"ghost_index_rows": [], "anchor_drift": [],
                            "dangling_edge_targets": []}
    assert sup["prose_superseded"] == []
    # quote/line invariants
    assert all(1 <= e["line"] and len(e["quote"]) <= 140
               for e in sup["edges"])
    # the module's own known-chain selftest passes on the committed registry
    assert fs.selftest(sup) == 0
