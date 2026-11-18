# Offline-first Sanskrit e-text scanner — H8429

_Created: 18-11-2026 · Last updated: 18-11-2026_
_Dr. Mārcis Gasūns_

A CLI that turns a scanned printed Sanskrit page or book into **structured TEI
XML with page/line anchors**, with a **local-only default**: no page image
leaves the machine unless an operator explicitly opts in to a separate remote
lane. This is adoption move 3 of the CLLG strategy scorecard
([H8426](https://github.com/gasyoun/Uprava/blob/main/handoffs/H8426-OxAlpha_csl-observatory_cllg-sanskrit-peer-comparison_18.11.26.md)).

## What was studied, and what was not copied

The design of [CLLG-Scanner](https://github.com/cllg-project/cllg-scanner)
(Apache-2.0) was studied from its public README: the seven-step workflow
(import → document → mask → OCR → structure → review → TEI export), the
resumable per-page cache (`page_NNNN.md` + untouched `.orig.md`), line-anchored
transcription (`<lb n="…"/>`), and TEI P5 export with `<pb>`, `citeStructure`
and Unicode NFC.

**No CLLG code was copied.** This is an original, stdlib-plus-estate-assets
Python implementation. The Apache-2.0 project is credited as the pattern
source; the pattern itself is an idea, not protected expression. This file and
the tool are released under the repository's MIT license.

## Pattern → implementation map

| CLLG-Scanner step | Here |
|---|---|
| Import PDF/DjVu/image folder/ALTO | `import --kind pdf\|images\|alto`; PyMuPDF 300-dpi render (never poppler — Cyrillic-blanking trap), image folder, ALTO `TextLine` geometry |
| Document / zone choices | `project.json` (`script`, `engine.lang`, `engine.psm`) |
| Mask regions before recognition | `mask: [[x, y, w, h], …]` per page → whiten via Pillow → `page_NNNN_masked.png` |
| Local OCR, cached per page | `ocr`; tesseract subprocess (`san`/`eng`/`san+eng`), TSV word→line grouping, `<lb n>` anchors; `page_NNNN.md` + `.orig.md`; skip cached unless `--force`; `ocr_output.md` rebuilt |
| Structure / reference hierarchy | `page_divs` mapping page → nested `(level, number)` → TEI `<div>`; `citeStructure` in header |
| Review | the per-page `.md` is the editable transcription; re-run `ocr --force` rewrites only the current pass, never `.orig.md` |
| TEI export, offline, NFC | `export`; deterministic string build, `<pb n>`, `<lb n>` with `break="no"` at hyphenated line ends, `citeStructure`, NFC, `--check` byte parity |

## Local-only contract

- `import`, `ocr` with the default tesseract backend, `export` and `smoke` run
  inside `offline_guard()`: a socket connect attempt raises and aborts the run.
- The estate's VLM asset (`Uprava/tools/ocr_vlm`, DashScope) is **network**; it
  is not the default and is not used by the smoke. Invoking it requires
  `--backend vlm --remote --accept-network DATA_LEAVES_THIS_MACHINE`, prints a
  loud notice, and delegates to the estate tool (which reads its own key from
  env). Without the consent flag the call is refused.
- Known limit: tesseract `rus+eng` garbles mixed Cyrillic+IAST scans
  (Latin→Cyrillic lookalikes). This tool's local lane is for Devanagari / IAST
  pages; for mixed Cyrillic+IAST use the estate VLM asset in a consented lane.

## Usage

```sh
T=tools/offline_sanskrit_scanner/scanner.py

# a) import a printed book (selected pages) and OCR locally
python $T import --kind pdf --source book.pdf --project /path/proj --pages 1-5 --lang san
python $T ocr --project /path/proj                 # resumable; local only
python $T export --project /path/proj --out /path/proj/scan.tei.xml

# b) import a folder of page images
python $T import --kind images --source scans/ --project /path/proj

# c) import an ALTO export with its page image
python $T import --kind alto --source page.xml --alto-image page.png --project /path/proj

# deterministic committed artifact check
python $T export --project /path/proj --out scan.tei.xml --check

# offline controls + real-print smoke
python $T selftest
python $T smoke            # Monier-Williams printed p. 277, local tesseract
```

The smoke work dir is **repo-local by default** (some hosts fence `/tmp` from
tesseract's file reads). `--work DIR` overrides; `--receipt FILE` writes the
measured canary receipt.

## Acceptance evidence (18-11-2026)

- `selftest`: **18/18** offline positive/negative controls PASS.
- `smoke`: real printed Monier-Williams p. 277 (`EntryAnatomy/assets/mw_kala_p277.jpg`),
  local tesseract `san`, **87** line anchors, **2,806** Devanagari chars, NFC,
  well-formed, byte-parity, **0** network calls — see
  [SMOKE_RECEIPT_18-11-2026.json](SMOKE_RECEIPT_18-11-2026.json).
- Own-data canary: the Devanagari count and the fixture SHA-256 are pinned in
  the committed receipt; a drifted fixture or engine fails the smoke.
- `pytest tests/test_offline_sanskrit_scanner.py` is registered in the H4353
  offline suite (`tests/run_offline_suite.py` auto-discovers `tests/`).

## Files

- `pattern.py` — pure primitives (selection, import, mask, TSV→lines, TEI, NFC).
- `engines.py` — local tesseract backend + explicit opt-in remote delegation.
- `scanner.py` — CLI, offline guard, selftest, real-print smoke.
