"""Dashboard generators — malformed or empty input is a LOUD refusal (H4353).

Three generators: ``epistemic_dashboard/build_epistemic_dashboard.py``,
``findings_dashboard/build_findings_data.py`` and the progress dashboard
builders. Each test asserts the concrete refusal (exit code + message) or the
concrete content written — never merely "no exception was raised".
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

import pytest

from conftest import FIXTURES, REPO, load_module

EPI = REPO / "epistemic_dashboard/build_epistemic_dashboard.py"


def _run_epi(root: Path, out: Path):
    return subprocess.run([sys.executable, str(EPI), "--dir", str(root), "--side", "sanskrit",
                           "--repo-url", "https://example.invalid/r", "--out", str(out)],
                          capture_output=True, text=True, encoding="utf-8")


# ------------------------------------------------------ build_epistemic_dashboard
def test_epistemic_dashboard_counts_from_fixture(tmp_path):
    out = tmp_path / "epistemic.json"
    r = _run_epi(FIXTURES / "epistemic_ok", out)
    assert r.returncode == 0, r.stderr
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["core"]["total"] == 3
    assert d["core"]["by_importance"] == {"3": 1, "2": 1, "1": 1}   # Index dot, then body dot
    layers = {l["key"]: l for l in d["layers"]}
    assert set(layers) == {"GAPS", "STALENESS"}
    assert layers["GAPS"]["total"] == 2
    assert layers["GAPS"]["by_origin"] == {"auto": 1, "human": 1}
    assert layers["GAPS"]["by_importance"] == {"3": 1, "2": 1, "1": 0}
    assert layers["GAPS"]["interlinks"] == 1 and layers["GAPS"]["categories"] == 1
    assert layers["GAPS"]["entries"][0]["url"].endswith("/GAPS.md#1-a-gap")
    assert d["staleness"] == {"total": 3, "red": 1, "yellow": 0, "green": 1, "unknown": 1}
    assert d["totals"]["findings"] == 3 and d["totals"]["layers"] == 2


def test_epistemic_dashboard_refuses_empty_dir(tmp_path):
    out = tmp_path / "epistemic.json"
    r = _run_epi(tmp_path / "empty", out)
    assert r.returncode != 0
    assert "REFUSED" in r.stderr and "no epistemic registry" in r.stderr
    assert not out.exists(), "a refused build must not leave an empty page behind"


def test_epistemic_dashboard_refuses_findings_without_headings(tmp_path):
    root = tmp_path / "r"
    root.mkdir()
    (root / "FINDINGS.md").write_text("# Findings\n\nprose only, no §-headings\n", encoding="utf-8")
    out = tmp_path / "epistemic.json"
    r = _run_epi(root, out)
    assert r.returncode != 0 and "REFUSED" in r.stderr and "0 findings" in r.stderr
    assert not out.exists()


def test_epistemic_parsers_pure():
    be = load_module("epistemic_dashboard/build_epistemic_dashboard.py")
    assert be.gh_slug("§1. A gap (x)") == "1-a-gap-x"
    total, flags = be.parse_staleness((FIXTURES / "epistemic_ok" / "STALENESS.md").read_text(encoding="utf-8"))
    assert (total, flags) == (3, {"red": 1, "yellow": 0, "green": 1, "unknown": 1})
    assert be.parse_findings_core("nothing") == (0, {"3": 0, "2": 0, "1": 0})
    n, imp = be.parse_findings_core((FIXTURES / "epistemic_ok" / "FINDINGS.md").read_text(encoding="utf-8"))
    assert n == 3 and imp == {"3": 1, "2": 1, "1": 1}
    entries = be.parse_entry_layer("### T\n🔴 ⚙️ x\n", "u")
    assert entries == [{"title": "T", "importance": 3, "origin": "auto", "url": "u#t"}]


# ----------------------------------------------------------- build_findings_data
def _findings_module(monkeypatch, root: Path):
    bf = load_module("findings_dashboard/build_findings_data.py")
    here = root / "findings_dashboard"
    here.mkdir(exist_ok=True)
    monkeypatch.setattr(bf, "HERE", here)
    monkeypatch.setattr(bf, "REPO", root)
    monkeypatch.setattr(bf, "SIBLINGS", root / "siblings")
    return bf, here


def test_findings_data_parse_and_main_on_fixture(monkeypatch, tmp_path):
    bf, here = _findings_module(monkeypatch, tmp_path)
    (tmp_path / "FINDINGS.md").write_text(
        (FIXTURES / "epistemic_ok" / "FINDINGS.md").read_text(encoding="utf-8"), encoding="utf-8")
    findings = bf.parse_findings((tmp_path / "FINDINGS.md").read_text(encoding="utf-8"))
    assert [(f["n"], f["importance"], f["evidence_date"]) for f in findings] == \
        [(1, 3, "2026-01-15"), (2, 1, "2026-09-01"), (3, 2, "2026-06")]
    assert findings[0]["section"] == "A. Section one"
    assert findings[0]["url"].endswith("#1-first-finding")
    assert findings[0]["age_days"] > 200 and findings[1]["age_days"] >= 0
    assert bf.slugify("§3. Third finding, dot only in body") == "3-third-finding-dot-only-in-body"
    bf.main()                                   # network is disabled: collectors miss, main survives
    data = json.loads((here / "data.json").read_text(encoding="utf-8"))
    assert data["counts"] == {"total": 3, "by_importance": {"3": 1, "1": 1, "2": 1}, "stale": 1}
    ts = json.loads((here / "timeseries.json").read_text(encoding="utf-8"))
    assert len(ts["snapshots"]) == 1 and ts["snapshots"][0]["registry"]["total"] == 3
    assert ts["snapshots"][0]["metrics"]["dcs_cdsl_linkage_pct"] is None   # offline → null, not fabricated


def test_findings_data_refuses_missing_and_empty_registry(monkeypatch, tmp_path):
    bf, here = _findings_module(monkeypatch, tmp_path)
    with pytest.raises(FileNotFoundError):
        bf.main()
    (tmp_path / "FINDINGS.md").write_text("# Findings\n\n## Index\n\nno headings\n", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        bf.main()
    assert "REFUSED" in str(e.value) and "0 findings" in str(e.value)
    assert not (here / "data.json").exists()


def test_findings_read_source_local_first_then_offline_null(monkeypatch, tmp_path):
    bf, _ = _findings_module(monkeypatch, tmp_path)
    (tmp_path / "siblings" / "x").mkdir(parents=True)
    (tmp_path / "siblings" / "x" / "readme.md").write_text("(42.5%) linked to wf0", encoding="utf-8")
    assert bf.rx(r"\(([\d.]+)%\) linked to wf0", bf.read_source("x/readme.md", "https://example.invalid")) == 42.5
    assert bf.read_source("x/absent.md", "https://example.invalid/absent") is None
    assert bf.rx("x", None) is None


# ------------------------------------------------------------ progress dashboard
def test_backfill_ledger_helpers():
    bl = load_module("progress_dashboard/backfill_ledger_metrics.py")
    rows = bl._load_rows(FIXTURES / "ledger_mini.jsonl")
    assert [r["window_id"] for r in rows] == ["w1", "w2", "w3"]      # blank + bad JSON skipped
    assert bl._load_rows(FIXTURES / "absent.jsonl") == []
    cov = bl.coverage(rows)
    assert cov == {"windows": 3, "wall_clock_present": 1, "wall_clock_coverage_pct": 33.3,
                   "gen_model_present": 2, "gen_model_coverage_pct": 66.7}
    assert bl.coverage([]) == {"windows": 0, "wall_clock_present": 0, "wall_clock_coverage_pct": None,
                               "gen_model_present": 0, "gen_model_coverage_pct": None}
    ts = bl._parse_ts("2026-09-08T05:30:00Z")
    assert ts.isoformat() == "2026-09-08T05:30:00+00:00"
    assert bl._parse_ts("garbage") is None and bl._parse_ts(None) is None
    assert bl._parse_ts("2026-09-08T05:30:00").tzinfo is not None


def test_live_refresh_pure_helpers(tmp_path):
    lr = load_module("progress_dashboard/live_refresh.py")
    assert lr.resolve_data_root(str(tmp_path)) == tmp_path.resolve()
    on, age = lr.is_translation_on(tmp_path, 60)
    assert (on, age) == (False, None)                                # no store → off, honestly
    src = tmp_path / "RussianTranslation" / "src"
    src.mkdir(parents=True)
    (src / "pwg_ru_translated.jsonl").write_text("{}\n", encoding="utf-8")
    on, age = lr.is_translation_on(tmp_path, 60)
    assert on is True and 0 <= age <= 60
    fp1 = lr.payload_fingerprint(tmp_path)
    (tmp_path / lr.PUBLISH[0]).write_text("x", encoding="utf-8")
    assert lr.payload_fingerprint(tmp_path) != fp1 and len(fp1) == 16


def test_build_progress_data_null_contract_for_missing_artifacts(monkeypatch, tmp_path):
    """A missing local artifact is reported as None, never as a fabricated number."""
    bp = load_module("progress_dashboard/build_progress_data.py")
    monkeypatch.setattr(bp, "RT", tmp_path / "RussianTranslation")
    assert bp._load_json("src/pilot/output/absent.json") is None
    p = tmp_path / "RussianTranslation" / "x.json"
    p.parent.mkdir(parents=True)
    p.write_text("﻿{\"a\": 1}", encoding="utf-8")
    assert bp._load_json("x.json") == {"a": 1}                        # BOM-tolerant
    p.write_text("{not json", encoding="utf-8")
    assert bp._load_json("x.json") is None


SELFTESTS = sorted(p.name for p in (REPO / "progress_dashboard").glob("*_selftest.py"))


@pytest.mark.parametrize("name", SELFTESTS)
def test_progress_dashboard_selftest(name):
    r = subprocess.run([sys.executable, str(REPO / "progress_dashboard" / name)],
                       capture_output=True, text=True, encoding="utf-8", cwd=str(REPO))
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert "PASS" in r.stdout or "OK" in r.stdout or "pass" in r.stdout.lower(), r.stdout[-500:]


def test_selftest_roster_is_the_seven_known():
    assert SELFTESTS == ["health_ribbon_selftest.py", "kitchen_collision_selftest.py",
                         "kitchen_instrumentation_selftest.py", "kitchen_multi_lane_selftest.py",
                         "kitchen_nominal_selftest.py", "kitchen_progress_slice_selftest.py",
                         "kitchen_promote_selftest.py"]
