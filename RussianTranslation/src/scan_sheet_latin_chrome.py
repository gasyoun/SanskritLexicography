#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan_sheet_latin_chrome.py — H2847: catch English reviewer-facing chrome
left in a rendered /review-sheet HTML file.

Scope, deliberately narrow: this only scans known CHROME regions (header
title/subtitle, footer, buttons, badges, typology/filter chip labels,
question text, note placeholder, per-card section headers) — never the card
DATA payload (dictionary translations, citations, {#...#} IAST spans, raw
store markup), which legitimately stays Latin/German/IAST. It also never
touches `sheet_id`, `save_as` paths, model slugs, or the fixed dictionary
codes in ALLOWED_TOKENS (PWG, PW, NWS, SCH, MW, RU, EN, FR, LA, IAST, plus
the grammar abbreviations ABBREVIATIONS_RU.md keeps international).

This is a chrome-region heuristic, not a full DOM/semantic parse — it can
miss a template region this list hasn't been taught about yet. Treat a clean
run as "no *known* chrome region regressed", not an absolute proof.

Run: python src/scan_sheet_latin_chrome.py <sheet.html> [<sheet2.html> ...]
"""
import sys, re, html

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Dictionary codes, language tags, and grammar abbreviations that stay
# international per RussianTranslation/ABBREVIATIONS_RU.md + the org's
# dictionary-code convention (../CLAUDE.md), plus a small set of established
# cross-language technical jargon (API/storage names, domain shorthand) that
# already appears inside this repo's own Russian prose. Case-sensitive.
ALLOWED_TOKENS = {
    "PWG", "PW", "NWS", "SCH", "MW", "DA", "RU", "EN", "FR", "LA", "IAST",
    "H180", "H2835", "H2844", "H2846", "MBH", "Cologne", "SHA",
    "Akk", "Dat", "Gen", "Instr", "Lok", "Abl", "Nom", "Voc", "Adj", "Adv",
    # H2849: RU-field case markers now ship as Acc./Ins./Loc.
    "Acc", "Ins", "Loc",
    "Comp", "sc", "Druckfehler", "lies", "streiche", "tilge", "Nachtrag",
    "Nachträge", "localStorage", "etext", "csl-orig", "store",
    "Nachträge-to-Nachträge",
    # export-format identifiers (H2847 scope: "export JSON keys... stays ASCII")
    "decisions", "json", "decision", "null",
}

# Latin-1 letters (À-ÖØ-öø-ÿ) so a diacritic word like "Nachträge" is one
# token, not split at the ä into "Nachtr"/"ge". A hyphen/apostrophe only
# joins two letter runs (never trails before a digit/space), so "SHA-256"
# matches just "SHA", not "SHA-".
LATIN_WORD = re.compile(
    r"[A-Za-zÀ-ÖØ-öø-ÿ]{2,}(?:['’-][A-Za-zÀ-ÖØ-öø-ÿ]+)*")
#: technical identifiers/hashes/paths/JSON keys always render inside <code>
#: in this template family — never reviewer prose, so never scanned.
_CODE_SPAN = re.compile(r"<code>.*?</code>", re.S)
#: literal escaped XML tag names quoted in legend prose, e.g. "&lt;ab&gt;" —
#: markup vocabulary, not reviewer prose.
_ESCAPED_TAG = re.compile(r"&lt;[a-zA-Z][^&]*?&gt;")

# Known chrome regions, anchored on stable template markup emitted by
# csl_pyutil.review_sheet + this repo's own card renderer. Each entry is
# (label, compiled pattern with a `body` group).
CHROME_REGIONS = [
    ("title/subtitle", re.compile(r"<h1[^>]*>(?P<body>.*?)</h1>", re.S)),
    ("footer", re.compile(r"<footer[^>]*>(?P<body>.*?)</footer>", re.S)),
    ("legend", re.compile(r'<div class="legend"[^>]*>(?P<body>.*?)</div>', re.S)),
    ("savebanner", re.compile(r'<div class="savebanner">(?P<body>.*?)</div>', re.S)),
    ("badge", re.compile(r'<span class="badge">(?P<body>.*?)</span>', re.S)),
    ("tchip", re.compile(r'<span class="tchip[^"]*"[^>]*>(?P<body>.*?)</span>', re.S)),
    ("tchip-title", re.compile(r'<span class="tchip[^"]*" title="(?P<body>[^"]*)"', re.S)),
    ("question", re.compile(r'<div class="q">(?P<body>.*?)</div>', re.S)),
    ("note-placeholder", re.compile(r'placeholder="(?P<body>[^"]*)"')),
    ("button", re.compile(r"<button[^>]*>(?P<body>.*?)</button>", re.S)),
    ("filt-label", re.compile(r'<option value="[^"]*">(?P<body>.*?)</option>', re.S)),
    ("h4-header", re.compile(r"<h4>(?P<body>.*?)</h4>", re.S)),
    # NOTE: `.hd` ("значение PWG %s") is deliberately NOT scanned — its %s is
    # the dictionary's own sense identifier, which can itself be a Latin
    # grammatical label (e.g. "PPP 1)"), not template chrome. Confirmed
    # 18-08-2026: scanning it flags real dictionary content as false
    # positives. The Russian prefix was verified by direct inspection instead.
]

_TAG = re.compile(r"<[^>]+>")
_SANSKRIT_SPAN = re.compile(r"\{[#%].*?[#%]\}", re.S)


def scan_text(label, text):
    """Yield (label, word) for each disallowed Latin-script run in text."""
    text = _SANSKRIT_SPAN.sub(" ", text)  # never flag {#IAST#} / {%RU%} spans
    text = _CODE_SPAN.sub(" ", text)      # never flag <code> identifiers/paths/hashes
    text = _ESCAPED_TAG.sub(" ", text)    # never flag escaped &lt;tag&gt; names
    text = _TAG.sub(" ", text)
    text = html.unescape(text)
    for m in LATIN_WORD.finditer(text):
        word = m.group(0)
        if word in ALLOWED_TOKENS:
            continue
        yield label, word


def scan_file(path):
    doc = open(path, encoding="utf-8").read()
    hits = []
    for label, pattern in CHROME_REGIONS:
        for m in pattern.finditer(doc):
            hits.extend(scan_text(label, m.group("body")))
    return hits


def main(argv):
    if not argv:
        print("usage: scan_sheet_latin_chrome.py <sheet.html> [...]")
        return 2
    total = 0
    for path in argv:
        hits = scan_file(path)
        total += len(hits)
        if hits:
            print("%s: %d disallowed Latin run(s) in chrome" % (path, len(hits)))
            for label, word in hits[:40]:
                print("  [%s] %r" % (label, word))
        else:
            print("%s: 0 (clean)" % path)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
