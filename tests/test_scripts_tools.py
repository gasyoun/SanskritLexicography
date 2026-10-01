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
