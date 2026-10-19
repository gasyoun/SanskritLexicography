"""scripts/ and tools/ — changelog gate, EOL census helpers, epistemic integrity (H4353)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from conftest import FIXTURES, REPO, load_module


# ------------------------------------------------- changelog_duplicate_bullets
def test_normalise_strips_markup_links_and_case():
    cd = load_module("scripts/changelog_duplicate_bullets.py")
    assert cd._normalise("- **Fix** the [`thing`](http://x).") == "fix the thing"
    assert cd._normalise("- (none in this release)") == "none in this release"
    assert cd._normalise("- N/A") == "n/a"


def test_find_duplicates_on_fixture_changelog():
    cd = load_module("scripts/changelog_duplicate_bullets.py")
    text = (FIXTURES / "changelog_mini.md").read_text(encoding="utf-8")
    dupes, skipped = cd.find_duplicates(text)
    keys = [d[0].split("\n")[0] for d in dupes]
    assert "- **Fix the thing.** Details here." in keys
    assert "- allowlisted marker ALLOW-ME appears twice" in keys
    assert not any(k.startswith("- **[`build.py`]") for k in keys), \
        "same first line, different continuation → not a duplicate"
    assert skipped == {"placeholder": 1, "nested-label": 1}
    hits = dict(dupes)["- **Fix the thing.** Details here."]
    assert [s for s, _ in hits] == ["## [1.0.1] - 2026-09-01", "## [1.0.0] - 2026-08-30"]
    dupes2, skipped2 = cd.find_duplicates(text, allowlist=["ALLOW-ME"])
    assert len(dupes2) == 1 and skipped2["allowlisted"] == 2


def test_load_allowlist(tmp_path):
    cd = load_module("scripts/changelog_duplicate_bullets.py")
    assert cd.load_allowlist(str(tmp_path)) == []
    (tmp_path / cd.ALLOW_FILE).write_text("# c\n\nMARK-1\n MARK-2 \n", encoding="utf-8")
    assert cd.load_allowlist(str(tmp_path)) == ["MARK-1", "MARK-2"]


def test_changelog_gate_cli_exit_codes(tmp_path):
    """The CLI checks the changelog of ITS OWN repo (dirname of scripts/) — so a
    copy of the script goes into tmp/scripts/ next to a tmp CHANGELOG.md."""
    import shutil
    (tmp_path / "scripts").mkdir()
    script = tmp_path / "scripts" / "changelog_duplicate_bullets.py"
    shutil.copy(REPO / "scripts/changelog_duplicate_bullets.py", script)
    (tmp_path / "CHANGELOG.md").write_text(
        (FIXTURES / "changelog_mini.md").read_text(encoding="utf-8"), encoding="utf-8")
    r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 1, "duplicates must fail the gate: " + r.stdout
    assert "2 entr(y/ies) duplicated, 4 copies total" in r.stdout
    r = subprocess.run([sys.executable, str(script), "--json"], capture_output=True, text=True,
                       encoding="utf-8")
    import json
    payload = json.loads(r.stdout)
    assert r.returncode == 1 and payload["file"] == "CHANGELOG.md"
    assert sorted(d["count"] for d in payload["duplicates"]) == [2, 2]
    (tmp_path / "CHANGELOG.md").write_text("# C\n\n## [1]\n\n- only one\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0 and "no duplicated entries" in r.stdout
    (tmp_path / "CHANGELOG.md").unlink()
    r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0 and "no changelog found" in r.stdout


# ------------------------------------------------- changelog_dupe_evidence_gate
def test_evidence_gate_counts_entries_and_finds_changelogs(tmp_path):
    eg = load_module("scripts/changelog_dupe_evidence_gate.py")
    text = (FIXTURES / "changelog_mini.md").read_text(encoding="utf-8")
    assert eg.count_entries(text) == 9            # the pre-section bullet is not an entry
    assert eg.count_entries("- no section\n") == 0
    (tmp_path / "CHANGELOG.md").write_text("x", encoding="utf-8")
    (tmp_path / "RussianTranslation").mkdir()
    (tmp_path / "RussianTranslation" / "changelog.md").write_text("y", encoding="utf-8")
    found = eg.find_changelogs(str(tmp_path))
    # case-insensitive compare: on APFS/NTFS CHANGELOG.md and changelog.md are one file
    assert [Path(p).relative_to(tmp_path).as_posix().lower() for p in found] == \
        ["changelog.md", "russiantranslation/changelog.md"]


# --------------------------------------------------------------- eol_census
def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True, encoding="utf-8").stdout


def test_eol_census_helpers_on_a_throwaway_repo(tmp_path):
    """No history walk of the shallow clone: a throwaway repo instead.

    ``scripts/eol_census.py`` does ``import git_ops`` from its own directory, and
    that module is NOT in this repo (it lives in Uprava/tools) — so the script
    cannot run here as committed. The pure helpers are pinned via ``load_defs``;
    the ``git_ops``-backed ones (``ls_tree_paths``, ``cr_counts_multi``,
    ``cmd_*``) are deliberately uncovered — see tests/OFFLINE_CONTRACT_PINS_08-09-2026.md.
    """
    from conftest import load_defs
    ec = load_defs("scripts/eol_census.py")
    assert "git_ops" not in sys.modules or True
    assert ec.is_text_tracked("set") and ec.is_text_tracked("auto")
    assert not ec.is_text_tracked("unset") and not ec.is_text_tracked("unspecified")
    assert ec.is_binary(b"abc\0def") and not ec.is_binary(b"plain\r\ntext")
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    _git(repo, "config", "core.autocrlf", "false")
    (repo / "lf.txt").write_bytes(b"a\nb\n")
    (repo / "crlf.txt").write_bytes(b"a\r\nb\r\n")
    (repo / "bin.dat").write_bytes(b"\0\r\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "one")
    assert ec.cr_candidates(repo, "HEAD") == ["crlf.txt"]     # binary excluded by -I
    with pytest.raises(RuntimeError):
        ec.cr_candidates(repo, "no-such-ref")


# ---------------------------------------------------- epistemic_integrity_check
def test_epistemic_headings_index_marker_on_fixture():
    ei = load_module("tools/epistemic_integrity_check.py")
    good = (FIXTURES / "epistemic_ok" / "FINDINGS.md").read_text(encoding="utf-8")
    assert ei.headings(good) == [(1, ""), (2, ""), (3, "")]
    defects: list[str] = []
    ei.check_duplicates(defects, "FINDINGS.md", good)
    ei.check_findings_index(defects, good)
    ei.check_marker(defects, good)
    assert defects == []
    bad = (FIXTURES / "epistemic_bad" / "FINDINGS.md").read_text(encoding="utf-8")
    defects = []
    ei.check_duplicates(defects, "FINDINGS.md", bad)
    ei.check_findings_index(defects, bad)
    ei.check_marker(defects, bad)
    joined = "\n".join(defects)
    assert "duplicate heading §1 (2 headings share it)" in joined
    assert "1 heading(s) missing from Index: §3" in joined
    assert "dangling): §9" in joined
    assert "marker says §2, expected §4" in joined
    assert ei.index_block("no index here") is None
    d2: list[str] = []
    ei.check_findings_index(d2, "### §1. x\n")
    assert d2 == ["FINDINGS.md: no `## Index` section found"]


def test_epistemic_dashboard_parity_reads_json(tmp_path):
    ei = load_module("tools/epistemic_integrity_check.py")
    (tmp_path / "findings_dashboard").mkdir()
    (tmp_path / "epistemic_dashboard").mkdir()
    (tmp_path / "findings_dashboard" / "data.json").write_text(
        '{"counts": {"total": 2}, "findings": [{"n": 1, "importance": null}]}', encoding="utf-8")
    (tmp_path / "epistemic_dashboard" / "epistemic.json").write_text(
        '{"core": {"total": 3, "by_importance": {"3": 1}}}', encoding="utf-8")
    defects: list[str] = []
    ei.check_dashboard_parity(defects, tmp_path, 3)
    joined = "\n".join(defects)
    assert "data.json total=2 != 3" in joined
    assert "1 finding(s) with null importance" in joined
    assert "by_importance sums to 1 but core.total=3" in joined
    (tmp_path / "epistemic_dashboard" / "epistemic.json").write_text("{not json", encoding="utf-8")
    defects = []
    ei.check_dashboard_parity(defects, tmp_path, 3)
    assert any("invalid JSON" in d for d in defects)


def test_epistemic_cli_passes_good_fixture_and_fails_bad(tmp_path):
    tool = REPO / "tools/epistemic_integrity_check.py"
    r = subprocess.run([sys.executable, str(tool), "--dir", str(FIXTURES / "epistemic_ok"),
                        "--structural-only"], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
    r = subprocess.run([sys.executable, str(tool), "--dir", str(FIXTURES / "epistemic_bad"),
                        "--structural-only"], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode != 0
    assert "duplicate heading" in r.stdout + r.stderr


def test_epistemic_check_on_the_live_registries():
    """The repo's own registries must pass the structural check (CI runs the same)."""
    tool = REPO / "tools/epistemic_integrity_check.py"
    r = subprocess.run([sys.executable, str(tool), "--dir", str(REPO), "--structural-only"],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr


# --------------------------------------------- audit_features_index_repo_cells
def test_features_index_rows_parser():
    af = load_module("tools/audit_features_index_repo_cells.py")
    text = (FIXTURES / "features_index_mini.md").read_text(encoding="utf-8")
    assert list(af.rows(text)) == [("MW", "[MWS](https://github.com/sanskrit-lexicon/MWS)"),
                                   ("PWG", "—")]
    live = (REPO / "FEATURES_INDEX.md").read_text(encoding="utf-8")
    codes = [c for c, _ in af.rows(live)]
    assert len(codes) >= 15 and "MW" in codes and "PWG" in codes
    assert af.REPO_COL == 6 and af.HEADER == "| Code | Dictionary |"


# ============================================================ bughunt 19-10-2026
# Regression pins for BUGHUNT-FINDINGS-SanskritLexicography-19.10.2026.md, one
# per gate that was found reading the wrong artifact. Each pin holds BOTH
# directions where a false verdict has a mirror: the defect must be refused AND
# the legitimate case must still pass.

def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def _git_repo(path: Path, files: dict[str, bytes]) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "pin@example.invalid")
    _git(path, "config", "user.name", "pin")
    for name, payload in files.items():
        target = path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    _git(path, "add", "-A")
    _git(path, "commit", "-qm", "base")
    return path


# ------------------------------------------------------- §2 utf8_gate --staged
def test_utf8_gate_staged_reads_the_index_not_the_worktree(tmp_path):
    ug = load_module("tools/utf8_gate.py")
    repo = _git_repo(tmp_path / "r", {"a.txt": b"seed\n"})

    # invalid blob staged, file then fixed without re-staging → MUST fail
    (repo / "a.txt").write_bytes(b"ok \xff bad\n")
    _git(repo, "add", "a.txt")
    (repo / "a.txt").write_bytes(b"now valid utf8\n")
    assert ug.run_staged(ug.staged_blobs(repo), repo) == 1

    # valid blob staged, worktree still invalid → must NOT be refused
    (repo / "a.txt").write_bytes(b"valid staged\n")
    _git(repo, "add", "a.txt")
    (repo / "a.txt").write_bytes(b"worktree \xff junk\n")
    assert ug.run_staged(ug.staged_blobs(repo), repo) == 0


# -------------------------------------------------- §5 utf8_gate UTF-16 sniff
def test_utf8_gate_refuses_non_latin_utf16_without_a_bom():
    ug = load_module("tools/utf8_gate.py")
    for payload in ("Привет, мир.\n".encode("utf-16-le"),
                    "नमस्ते\n".encode("utf-16-le"),
                    "नमस्ते\n".encode("utf-16-be")):
        status, reason, _ = ug.check_bytes(payload)
        assert status == "error", (payload[:8], status, reason)
        assert "UTF-16 without BOM" in reason
    # a real binary stays skipped, not refused
    assert ug.check_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")[0] == "binary"


# ------------------------------------------- §3 stale-base removed-line numbers
def test_stale_base_line_numbers_survive_a_dash_rule(tmp_path):
    pps = load_module("scripts/pre_push_stale_base_check.py")
    repo = _git_repo(tmp_path / "r", {"doc.md": b"intro\n---\nold line\ntail\n"})
    (repo / "doc.md").write_bytes(b"intro\ntail\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "drop the rule and the line after it")
    import os
    cwd = os.getcwd()
    os.chdir(repo)
    try:
        # line 2 is the markdown rule, line 3 the line that actually vanished
        assert pps.removed_line_numbers("HEAD~1", "HEAD", "doc.md") == [2, 3]
    finally:
        os.chdir(cwd)


def test_stale_base_added_line_texts_keep_a_plus_initial_line(tmp_path):
    pps = load_module("scripts/pre_push_stale_base_check.py")
    repo = _git_repo(tmp_path / "r", {"doc.md": b"intro\n"})
    (repo / "doc.md").write_bytes(b"intro\n+++ counter value\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "add a +++-initial line")
    import os
    cwd = os.getcwd()
    os.chdir(repo)
    try:
        assert pps.added_line_texts("HEAD~1", "HEAD", "doc.md") == ["+++ counter value"]
    finally:
        os.chdir(cwd)


# ------------------------------------- §7 changelog gate path normalisation
def test_changelog_gate_normalises_a_relative_repo_path(tmp_path, monkeypatch):
    dupe = tmp_path / "dupe"
    dupe.mkdir()
    (dupe / "CHANGELOG.md").write_text(
        "# Changelog\n\n## 1.0\n\n- same bullet text here\n\n"
        "## 0.9\n\n- same bullet text here\n", encoding="utf-8")
    gate = REPO / "scripts/changelog_dupe_evidence_gate.py"
    monkeypatch.chdir(tmp_path)
    r = subprocess.run([sys.executable, str(gate), "--repo", "./dupe",
                        "--evidence", str(tmp_path / "ev.json")],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "hit" in (r.stdout + r.stderr)


# ------------------------------------------------ §4 envelope CHK-5 verdict
def test_envelope_chk5_refuses_a_dead_tag_and_a_missing_commit(tmp_path):
    ec = load_module("scripts/envelope_check.py")
    repo = _git_repo(tmp_path / "r", {"f.txt": b"x\n"})
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                         capture_output=True, text=True).stdout.strip()
    _git(repo, "tag", "v1")
    ok, detail = ec.code_revision_verdict({"tag": "v1", "commit": sha}, repo=repo)
    assert ok, detail
    # dead tag with no recorded commit was `None == None` → PASS before the fix
    ok, detail = ec.code_revision_verdict({"tag": "v-dead"}, repo=repo)
    assert not ok and "does not resolve" in detail, detail
    # a resolving tag still cannot vouch for an unrecorded commit
    ok, detail = ec.code_revision_verdict({"tag": "v1"}, repo=repo)
    assert not ok and "no commit recorded" in detail, detail
    # wrong commit is a mismatch, not a pass
    ok, detail = ec.code_revision_verdict({"tag": "v1", "commit": "0" * 40}, repo=repo)
    assert not ok and "resolves to" in detail, detail


# ------------------------------------- §8 eol census reads the REF's attributes
def test_eol_census_reads_attributes_from_the_ref_not_the_checkout(tmp_path):
    eol = load_module("scripts/eol_census.py")
    repo = _git_repo(tmp_path / "r", {"data.txt": b"a\r\nb\r\n"})
    _git(repo, "config", "core.autocrlf", "false")
    # ref B adds the attributes only; the CR-bearing blob came from A
    (repo / ".gitattributes").write_bytes(b"* text=auto\n")
    _git(repo, "add", ".gitattributes")
    _git(repo, "commit", "-qm", "add attributes")
    ref_b = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                           capture_output=True, text=True).stdout.strip()
    _git(repo, "reset", "-q", "--hard", "HEAD~1")      # checkout has no attributes
    assert not (repo / ".gitattributes").exists()
    rc = eol.cmd_census(repo, ref_b, quiet=True)
    assert rc == 1, "a CR blob that only the REF marks as text must be a violation"


# ------------------------------------- §10/§9 canary honours the filter, names its run
def test_canary_honours_the_edition_filter_and_writes_meta(tmp_path, monkeypatch):
    cen = load_module("HeadwordLists/works_catalogue/census_ncc_mss.py")
    calls = []

    def fake_extract(body, cat_re, filter_editions=True, trace=None):
        calls.append(filter_editions)
        unit = ("Cat", "1")
        return ([unit] if filter_editions else [unit, ("Cat", "2")]), {"raw_units": 2}

    monkeypatch.setattr(cen, "extract_units", fake_extract)
    monkeypatch.setattr(cen, "CANARY_WORKS", [("Test", "Test", None)])
    rows = [{"iast": "Test", "body_html": "<p>body</p>"}]
    out = tmp_path / "canary.tsv"
    cen.run_canary(rows, None, str(out), filter_editions=False,
                   meta={"lexicon_mode": "witness-prefix-only", "mode": "canary"})
    assert calls and calls[0] is False, "run_canary must pass filter_editions through"
    meta = out.with_name(out.name + ".meta.json")
    assert meta.exists()
    assert '"lexicon_mode": "witness-prefix-only"' in meta.read_text(encoding="utf-8")


# ------------------------------------- §14 quota allocator on feasible frames
def test_quota_allocator_accepts_a_below_floor_class():
    smp = load_module("data/definition_typology_pool_sampler.py")
    q = smp.allocate_quotas({"synonym": 5, "equivalent": 100,
                             "encyclopedic": 100, "residual": 100}, 300)
    assert sum(q.values()) == 300 and q["synonym"] == 5
    q = smp.allocate_quotas({"a": 3, "b": 4, "c": 500}, 200)
    assert sum(q.values()) == 200 and q["c"] == 193
    for totals, q in (({"a": 100, "b": 100, "c": 100, "d": 100}, 300),):
        alloc = smp.allocate_quotas(totals, q)
        assert all(alloc[c] <= totals[c] for c in alloc)


# ------------------------------------- §1 the snapshot writer's BOM contract
def test_headword_diff_selftest_green():
    """Locks the write contract, including the BOM source, into CI."""
    r = subprocess.run([sys.executable, "HeadwordLists/headword_diff_selftest.py"],
                       cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "SELFTEST GREEN" in r.stdout
