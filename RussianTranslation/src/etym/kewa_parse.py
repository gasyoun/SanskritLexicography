"""Parser for the OCRed KEWA heading index (H3169, ceiling C4).

Source: SamudraManthanam/Index/lib/x86_64-win64/Data/KEWA.txt — one line per
printed heading block of Mayrhofer, *Kurzgefasstes etymologisches Woerterbuch
des Altindischen* (KEWA, 1953-1980), carrying:

    <seq> <volume>: <page(s)> <devanagari headings> <iast headings> /<slashed forms>/ <br><img ...>

The slashed forms are the OCR project's own machine keys: first the N IAST
forms (accents stripped), then, when they differ, the N SLP1 forms.  This
module never trusts them - it re-derives SLP1 from the IAST with the canonical
transcoder (sanskrit-util) and reports the disagreements as a census class.

No KEWA article text is read or emitted; the index carries headings only.
"""
from __future__ import annotations

import html
import re
import sys
import unicodedata

from kewa_accent import strip_vowel_accents
from dataclasses import dataclass, field

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DEVA = re.compile(r"[ऀ-ॿ]")
# The page field is deliberately permissive: three of them were rewritten as
# Russian dates by a spreadsheet round-trip (see repair_page in kewa_normalize).
LINE = re.compile(r"^(?P<seq>\d+)\s+(?P<vol>[IVX]+):\s+(?P<page>\S+)\s+(?P<rest>.*)$")
IMG = re.compile(r"<br>\s*<img\s+src=\"(?P<src>[^\"]+)\"\s*>\s*$")
SLASHED = re.compile(r"(?:/[^/]*/\s*)+$")

# Volume -> roman numeral sanity set (KEWA is I-III plus the register).
VOLUMES = {"I", "II", "III", "IV"}


@dataclass
class KewaRow:
    seq: int
    vol: str
    page: str
    deva: list[str]
    iast_accented: list[str]
    iast_plain: list[str]
    file_forms: list[str]
    img: str
    noise: list[str] = field(default_factory=list)


def strip_accents(s: str) -> str:
    """Drop KEWA's udatta marks over vowels, keeping s-acute intact.

    Delegates to [`kewa_accent.strip_vowel_accents`](kewa_accent.py) - see there
    for why a blanket "remove every U+0301" is wrong for IAST.
    """
    return strip_vowel_accents(s)


def split_headings(chunk: str) -> list[str]:
    parts = [p.strip() for p in chunk.split(",")]
    return [p for p in parts if p]


def parse_line(line: str) -> KewaRow | None:
    """Return a KewaRow, or None for a line that is not an index row."""
    line = line.rstrip("\n").rstrip()
    if not line or line.startswith("<!--"):
        return None
    m = LINE.match(line)
    if not m:
        return KewaRow(-1, "", "", [], [], [], [], "", ["unparsed-line-shape"])

    seq = int(m.group("seq"))
    vol = m.group("vol")
    page = m.group("page")
    rest = m.group("rest")
    noise: list[str] = []
    if vol not in VOLUMES:
        noise.append("unknown-volume")

    img = ""
    mi = IMG.search(rest)
    if mi:
        img = mi.group("src")
        rest = rest[: mi.start()].rstrip()
    else:
        noise.append("missing-image-ref")

    file_forms: list[str] = []
    ms = SLASHED.search(rest)
    if ms:
        blob = rest[ms.start():].strip()
        file_forms = [f for f in (x.strip() for x in blob.split("/")) if f]
        rest = rest[: ms.start()].rstrip()
    else:
        noise.append("no-machine-key")

    rest = html.unescape(rest).strip()

    # Devanagari prefix, then the IAST rendering of the same headings.
    first_latin = None
    for i, ch in enumerate(rest):
        if ch.isalpha() and not DEVA.match(ch):
            first_latin = i
            break
    if first_latin is None:
        deva_chunk, iast_chunk = rest, ""
        noise.append("no-iast-heading")
    elif first_latin == 0:
        deva_chunk, iast_chunk = "", rest
        noise.append("no-devanagari-heading")
    else:
        deva_chunk, iast_chunk = rest[:first_latin], rest[first_latin:]

    deva = split_headings(deva_chunk)
    iast_accented = split_headings(iast_chunk)
    iast_plain = [strip_accents(x) for x in iast_accented]

    if deva and iast_accented and len(deva) != len(iast_accented):
        noise.append("deva-iast-count-mismatch")
    if not iast_accented:
        noise.append("no-iast-heading")

    return KewaRow(seq, vol, page, deva, iast_accented, iast_plain, file_forms, img, noise)


def iter_rows(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            row = parse_line(line)
            if row is not None:
                yield row
