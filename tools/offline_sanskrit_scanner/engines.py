"""OCR backends for the offline Sanskrit scanner (H8429).

DEFAULT = tesseract, a local subprocess; no Python socket is ever opened.
The optional ``vlm`` backend is a *delegation* to the estate's existing
``Uprava/tools/ocr_vlm`` asset and is refused unless the operator explicitly
accepts that page images leave the machine. It is never used by ``smoke``.

_Created: 18-11-2026 · Last updated: 18-11-2026_
_Dr. Mārcis Gasūns_
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


class EngineError(RuntimeError):
    """OCR backend failed or is unavailable."""


class NetworkOptInRequired(RuntimeError):
    """A remote OCR path was requested without the explicit consent flag."""


CONSENT = "DATA_LEAVES_THIS_MACHINE"
NOTICE = ("REMOTE OCR: page image(s) will be transmitted to a third-party VLM "
          "via the estate OCR asset. This is NOT the default and is never used "
          "by the smoke test.")


def tesseract_available() -> bool:
    return shutil.which("tesseract") is not None


def ocr_tesseract(image: Path | str, *, lang: str = "san", psm: int = 6,
                  timeout: int = 300) -> str:
    """Return tesseract TSV on stdout — entirely local, no network."""
    if not tesseract_available():
        raise EngineError("tesseract not found on PATH (brew install tesseract tesseract-lang)")
    cmd = ["tesseract", str(image), "stdout", "-l", lang, "--psm", str(psm), "tsv"]
    # Tesseract TSV can carry non-UTF-8 bytes in OCR fields; decode tolerantly
    # instead of failing the whole page on one bad byte (H8429 smoke catch).
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         timeout=timeout)
    if res.returncode != 0:
        err = res.stderr.decode("utf-8", "replace").strip()
        raise EngineError(f"tesseract exit {res.returncode}: {err[:400]}")
    return res.stdout.decode("utf-8", "replace")


def estate_vlm_tool() -> Path:
    root = os.environ.get("UPRAVA_HOME") or str(Path.home() / "Documents/GitHub/Uprava")
    tool = Path(root) / "tools" / "ocr_vlm" / "vlm_ocr.py"
    if not tool.is_file():
        raise EngineError(f"estate VLM asset not found: {tool}")
    return tool


def ocr_vlm(image: Path | str, *, accept_network: bool = False,
            consent: str = "", timeout: int = 600,
            key_env: str = "DASHSCOPE_API_KEY") -> str:
    """Opt-in remote path, delegated to the estate asset. See NOTICE."""
    if not accept_network or consent != CONSENT:
        raise NetworkOptInRequired(
            "remote OCR requires --remote --accept-network DATA_LEAVES_THIS_MACHINE")
    tool = estate_vlm_tool()
    if not os.environ.get(key_env):
        raise EngineError(f"{key_env} is not set; the estate tool reads it from env")
    print(NOTICE, file=sys.stderr)
    res = subprocess.run([sys.executable, str(tool), str(image)],
                         capture_output=True, text=True, timeout=timeout)
    if res.returncode != 0:
        raise EngineError(f"estate VLM exit {res.returncode}: {res.stderr.strip()[:400]}")
    return res.stdout
