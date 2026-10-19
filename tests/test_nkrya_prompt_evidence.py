"""Offline pin for the H5263 NKRYa c1 prompt-evidence block.

Runs the module's own selftest as a subprocess, which is where the contract lives:
byte-identical prompt bytes for a card WITHOUT an ``nkrya`` input, and the rendered
block appended verbatim for a card with one. Offline by construction — it reads the
committed ``RussianTranslation/pwg_ru/nkrya_cache`` and makes no network call and no
paid call.

CI runs the same selftest directly in the RussianTranslation gates job; this pin puts
it inside the offline contract suite too, so ``python tests/run_offline_suite.py``
covers it (H5263).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "RussianTranslation" / "src" / "nkrya_prompt_evidence.py"


def test_prompt_evidence_selftest():
    pytest.importorskip("csl_pyutil", reason="csl-pyutil pin provides the NKRYa client")
    proc = subprocess.run([sys.executable, str(SCRIPT), "--selftest"],
                          capture_output=True, text=True, encoding="utf-8",
                          cwd=str(SCRIPT.parent.parent))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "selftest OK" in proc.stdout, proc.stdout
