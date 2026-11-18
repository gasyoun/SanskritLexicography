"""Pure, offline pattern primitives for the Sanskrit e-text scanner (H8429).

This module has NO network imports and NO third-party imports at module load.
It ports the *design* of the CLLG-Scanner workflow (import -> mask -> OCR ->
resumable per-page cache -> structured TEI) to scanned Sanskrit pages; the
implementation is original and shares no code with that Apache-2.0 project.

_Created: 18-11-2026 · Last updated: 18-11-2026_
_Dr. Mārcis Gasūns_
"""
from __future__ import annotations

import re
import shutil
import unicodedata
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

SCHEMA = "offline-sanskrit-scanner/1"
TEI_NS = "http://www.tei-c.org/ns/1.0"
DEV_RE = re.compile(r"[\u0900-\u097f]")
LB_RE = re.compile(r'^<lb n="(\d+)"(?:\s+break="no")?/>\s?(.*)$')
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


class PatternError(ValueError):
    """Raised on malformed project state or out-of-range input."""


def nfc(text: str) -> str:
    """TEI export normalises to Unicode NFC (CLLG pattern, section 7)."""
    return unicodedata.normalize("NFC", text)


def dev_count(text: str) -> int:
    """Devanagari codepoint count — the own-data canary on a real print."""
    return len(DEV_RE.findall(text))


def parse_selection(spec: str | None, total: int) -> list[int]:
    """Expand ``1-3,5`` to ``[1, 2, 3, 5]``; None/empty -> all pages, 1-based."""
    if total < 0:
        raise PatternError("total must be >= 0")
    if not spec:
        return list(range(1, total + 1))
    out: list[int] = []
    for chunk in str(spec).split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, _, b = chunk.partition("-")
            try:
                lo, hi = int(a), int(b)
            except ValueError as exc:
                raise PatternError(f"bad page range: {chunk!r}") from exc
            if lo < 1 or hi < lo:
                raise PatternError(f"bad page range: {chunk!r}")
            out.extend(range(lo, hi + 1))
        else:
            try:
                n = int(chunk)
            except ValueError as exc:
                raise PatternError(f"bad page number: {chunk!r}") from exc
            if n < 1:
                raise PatternError(f"bad page number: {chunk!r}")
            out.append(n)
    out = sorted(set(out))
    bad = [n for n in out if n > total]
    if bad:
        raise PatternError(f"page(s) beyond source: {bad} (source has {total})")
    return out


def page_path(project: Path | str, n: int) -> Path:
    return Path(project) / "pages" / f"page_{n:04d}.png"


def masked_path(project: Path | str, n: int) -> Path:
    return Path(project) / "pages" / f"page_{n:04d}_masked.png"


def orig_path(project: Path | str, n: int) -> Path:
    return Path(project) / "pages" / f"page_{n:04d}.orig.md"


def cache_path(project: Path | str, n: int) -> Path:
    return Path(project) / "pages" / f"page_{n:04d}.md"


def new_project(source_kind: str, source_ref: str, *, dpi: int = 300,
                script: str = "devanagari", lang: str = "san",
                psm: int = 6, backend: str = "tesseract") -> dict:
    return {
        "schema": SCHEMA,
        "source": {"kind": source_kind, "ref": str(source_ref), "dpi": int(dpi)},
        "script": script,
        "engine": {"backend": backend, "lang": lang, "psm": int(psm),
                   "remote_opt_in": False},
        "pages": [],
        "hierarchy": [],
        "page_divs": {},
        "bibliography": {"title": "", "author": "", "source": ""},
    }


def save_project(project: Path | str, data: dict) -> Path:
    import json
    root = Path(project)
    root.mkdir(parents=True, exist_ok=True)
    (root / "pages").mkdir(exist_ok=True)
    path = root / "project.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path


def load_project(project: Path | str) -> dict:
    import json
    data = json.loads((Path(project) / "project.json").read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise PatternError(f"unsupported project schema: {data.get('schema')!r}")
    return data


def render_pdf(pdf: Path | str, project: Path | str, *, pages: str | None = None,
               dpi: int = 300) -> list[int]:
    """Render selected PDF pages to local PNGs with PyMuPDF (never poppler)."""
    import pymupdf  # lazy: keep import cheap for --help/--selftest
    doc = pymupdf.open(str(pdf))
    try:
        sel = parse_selection(pages, doc.page_count)
        Path(project, "pages").mkdir(parents=True, exist_ok=True)
        for n in sel:
            pix = doc[n - 1].get_pixmap(dpi=dpi, alpha=False)
            pix.save(str(page_path(project, n)))
        return sel
    finally:
        doc.close()


def import_images(srcdir: Path | str, project: Path | str,
                  *, pages: str | None = None) -> list[int]:
    files = sorted(p for p in Path(srcdir).iterdir()
                   if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)
    sel = parse_selection(pages, len(files))
    Path(project, "pages").mkdir(parents=True, exist_ok=True)
    for n in sel:
        src = files[n - 1]
        dest = page_path(project, n)
        if src.suffix.lower() in {".png", ".tif", ".tiff"}:
            shutil.copyfile(src, dest)
        else:
            # Normalise JPEG -> real PNG: a JPEG with a .png name makes
            # Leptonica/tesseract refuse the page (H8429 smoke catch).
            from PIL import Image
            with Image.open(src) as im:
                im.convert("RGB").save(dest, format="PNG")
    return sel


def parse_alto_lines(xml_text: str) -> list[dict]:
    """Extract text lines + geometry from ALTO XML (eScriptorium export style)."""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_text)
    lines: list[dict] = []
    for node in root.iter():
        if not node.tag.rsplit("}", 1)[-1] == "TextLine":
            continue
        words = [(e.get("CONTENT") or "").strip() for e in node
                 if e.tag.rsplit("}", 1)[-1] == "String"]
        text = " ".join(w for w in words if w).strip()
        if not text:
            continue
        def num(attr: str, default: int = 0) -> int:
            try:
                return int(float(node.get(attr, default)))
            except (TypeError, ValueError):
                return default
        lines.append({"left": num("HPOS"), "top": num("VPOS"),
                      "width": num("WIDTH"), "height": num("HEIGHT"), "text": text})
    lines.sort(key=lambda d: (d["top"], d["left"]))
    return lines


def apply_mask(image: Path | str, masks: list, out: Path | str) -> Path:
    """Whitelist mask rectangles -> white rectangles; return the masked image."""
    from PIL import Image, ImageDraw
    im = Image.open(str(image)).convert("RGB")
    w, h = im.size
    draw = ImageDraw.Draw(im)
    for box in masks:
        if not isinstance(box, (list, tuple)) or len(box) != 4:
            raise PatternError(f"mask must be [x, y, w, h], got {box!r}")
        x, y, bw, bh = (int(v) for v in box)
        if min(bw, bh) <= 0:
            raise PatternError(f"mask must have positive size, got {box!r}")
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(w, x + bw), min(h, y + bh)
        if x1 > x0 and y1 > y0:
            draw.rectangle((x0, y0, x1 - 1, y1 - 1), fill="white")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(str(out))
    return out


def lines_from_tsv(tsv: str) -> list[tuple[int, str]]:
    """Group tesseract TSV words into reading-ordered lines with 1-based anchors."""
    import csv
    import io
    groups: dict[tuple[str, str, str], list[tuple[int, int, str]]] = {}
    reader = csv.DictReader(io.StringIO(tsv), delimiter="\t")
    for row in reader:
        text = (row.get("text") or "").strip()
        if not text or text == "-":
            continue
        key = (row.get("block_num", "0"), row.get("par_num", "0"),
               row.get("line_num", "0"))
        try:
            left, top = int(row.get("left", 0)), int(row.get("top", 0))
        except (TypeError, ValueError):
            left, top = 0, 0
        groups.setdefault(key, []).append((top, left, text))
    ordered = sorted(groups.items(), key=lambda kv: min((t, l) for t, l, _ in kv[1]))
    out: list[tuple[int, str]] = []
    for _key, words in ordered:
        words.sort(key=lambda w: (w[0], w[1]))
        out.append((len(out) + 1, " ".join(w[2] for w in words)))
    return out


def write_page_cache(project: Path | str, n: int,
                     lines: list[tuple[int, str]]) -> Path:
    """Write the reviewed cache; preserve the untouched first pass (`.orig.md`)."""
    body = "".join(f'<lb n="{i:04d}"/> {nfc(text)}\n' for i, text in lines)
    orig = orig_path(project, n)
    if not orig.exists():
        orig.write_text(body, encoding="utf-8")
    cache = cache_path(project, n)
    cache.write_text(body, encoding="utf-8")
    return cache


def read_page_cache(path: Path | str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        m = LB_RE.match(raw.strip())
        if m:
            out.append((int(m.group(1)), nfc(m.group(2))))
    return out


def combine(project: Path | str) -> Path:
    data = load_project(project)
    parts = []
    for page in data["pages"]:
        n = page["n"]
        cache = cache_path(project, n)
        parts.append(f"<!-- ===== page {n} ===== -->\n")
        parts.append(cache.read_text(encoding="utf-8") if cache.exists() else "")
    out = Path(project) / "ocr_output.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


def _div_ops(page_divs: dict, n: int, open_levels: list[tuple[str, str]]) -> tuple[list, list]:
    """Return (levels to close — reversed, levels to open) for this page."""
    want = [(str(lv), str(num)) for lv, num in page_divs.get(str(n), [])]
    common = 0
    for a, b in zip(open_levels, want):
        if a != b:
            break
        common += 1
    return open_levels[common:], want[common:]


def tei_export(project: Path | str) -> str:
    """Deterministic TEI P5: pb + lb anchors, citeStructure, NFC, hierarchy divs."""
    data = load_project(project)
    bib = data.get("bibliography", {})
    title = nfc(str(bib.get("title") or data["source"]["ref"]))
    author = nfc(str(bib.get("author") or ""))
    source = nfc(str(bib.get("source") or ""))
    backend = data["engine"]["backend"]

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<TEI xmlns="{TEI_NS}">', "  <teiHeader>", "    <fileDesc>",
           "      <titleStmt>", f"        <title>{escape(title)}</title>"]
    if author:
        out.append(f"        <author>{escape(author)}</author>")
    out += ["      </titleStmt>",
            "      <publicationStmt>",
            "        <p>Local-only transcription: no page image left this machine.</p>",
            "      </publicationStmt>", "      <sourceDesc>",
            f"        <bibl>{escape(source or title)}</bibl>",
            "      </sourceDesc>", "    </fileDesc>", "    <encodingDesc>",
            '      <refsDecl n="PB">',
            '        <citeStructure unit="pb" match="//pb[@n]">',
            '          <citeStructure unit="lb" match="lb[@n]"/>',
            "        </citeStructure>", "      </refsDecl>",
            f'      <appInfo><application version="{SCHEMA}">'
            f'<label>offline_sanskrit_scanner · {escape(backend)}</label>'
            "</application></appInfo>",
            "    </encodingDesc>", "  </teiHeader>", "  <text>", "    <body>"]

    page_divs = data.get("page_divs") or {}
    open_levels: list[tuple[str, str]] = []
    for page in data["pages"]:
        n = int(page["n"])
        close, opendlivs = _div_ops(page_divs, n, open_levels)
        for lv, _num in reversed(close):
            tag = lv.split(":", 1)[0]
            out.append(f'      </div><!-- {escape(tag)} -->')
        for lv, num in opendlivs:
            name, _, kind = lv.partition(":")
            out.append(f'      <div type={quoteattr(name)} n={quoteattr(num)}'
                       f' subtype={quoteattr(kind or "section")}>')
        open_levels = [lv for lv in open_levels if lv not in close] + opendlivs
        out.append(f'      <pb n="{n}"/>')
        cache = cache_path(project, n)
        lines = read_page_cache(cache) if cache.exists() else []
        if lines:
            out.append("      <p>")
            for idx, (i, text) in enumerate(lines):
                nxt = lines[idx + 1][1] if idx + 1 < len(lines) else ""
                brk = ' break="no"' if text.rstrip().endswith("-") and nxt else ""
                out.append(f'        <lb n="{i:04d}"{brk}/>{escape(text)}')
            out.append("      </p>")
    for lv, _num in reversed(open_levels):
        out.append(f'      </div><!-- {escape(lv.split(":", 1)[0])} -->')
    out += ["    </body>", "  </text>", "</TEI>", ""]
    return "\n".join(out)


def tei_check(project: Path | str, path: Path | str) -> bool:
    """Byte-parity gate: the committed TEI must equal a fresh local export."""
    expected = tei_export(project)
    actual = Path(path).read_text(encoding="utf-8")
    if actual != expected:
        raise PatternError("TEI drift: regenerate with `export --out <path>`")
    return True


def xml_wellformed(tei: str) -> bool:
    import xml.etree.ElementTree as ET
    ET.fromstring(tei)
    return True
