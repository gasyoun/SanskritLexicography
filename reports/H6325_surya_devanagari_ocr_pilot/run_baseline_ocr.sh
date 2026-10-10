#!/usr/bin/env bash
# H6325 baseline OCR runner — the sanscritica-ocr-reachable engines on this box:
#   B1 macOS Vision (tools/ocr_plate.swift lane — the engine actually used on the plates corpus, G26 QC dry-run 04-10-2026)
#   B2 Tesseract 5.5 (Engine B of the sanscritica-ocr skill; langs rus+eng+san)
# Usage: run_baseline_ocr.sh <plates_dir> <out_dir>
set -euo pipefail
PLATES_DIR="${1:?plates dir}"
OUT_DIR="${2:?out dir}"
mkdir -p "$OUT_DIR/vision_macos" "$OUT_DIR/tesseract"

# --- B1: macOS Vision via the Uprava ocr_plate.swift lane ---
SWIFT_TOOL="${OCR_PLATE_SWIFT:-/Users/mac/Documents/GitHub/Uprava/tools/ocr_plate.swift}"
: > "$OUT_DIR/vision_macos/raw.tsv"
while IFS= read -r f; do
  id="$(basename "$f" .png)"
  printf '%s\n' "$f" | swift "$SWIFT_TOOL" | tail -1 >> "$OUT_DIR/vision_macos/raw.tsv"
  echo "vision: $id done"
done < "$PLATES_DIR/plates.txt"
# split raw.tsv (path \t OK|ERR \t lines joined by " | ") -> per-plate txt
while IFS=$'\t' read -r path status text; do
  id="$(basename "$path" .png)"
  printf '%s\n' "$(printf '%s' "$text" | sed 's/ | /\n/g')" > "$OUT_DIR/vision_macos/$id.txt"
done < "$OUT_DIR/vision_macos/raw.tsv"

# --- B2: tesseract rus+eng+san (psm 3 = auto page segmentation) ---
LANGS="${TESS_LANGS:-rus+eng+san}"
while IFS= read -r f; do
  id="$(basename "$f" .png)"
  tesseract "$f" "$OUT_DIR/tesseract/$id" -l "$LANGS" --psm 3 2>/dev/null || \
    tesseract "$f" "$OUT_DIR/tesseract/$id" -l rus+eng --psm 3 2>/dev/null
  echo "tesseract: $id done"
done < "$PLATES_DIR/plates.txt"
echo "baselines complete"
