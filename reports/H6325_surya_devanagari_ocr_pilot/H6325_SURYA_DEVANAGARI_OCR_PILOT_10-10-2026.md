# H6325 — Surya Devanagari OCR pilot vs sanscritica-ocr on specimen plates

_Created: 10-10-2026 · Last updated: 10-10-2026_

Executed by OxAlpha (opencode/z-ai/glm-5.3-flash) · 10-10-2026. Handoff: [H6325](https://github.com/gasyoun/Uprava/blob/main/handoffs/H6325-OxAlpha_SanskritLexicography_surya-devanagari-ocr-pilot_09.10.26.md).

## Verdict: NEGATIVE (do not adopt)

On the corpus's actual Devanagari content, **no engine extracts usable text — including surya**. Devanagari set-recall is ≤ 0.12 everywhere (the corpus's Devanagari is scattered decorative aksharas integrated into artwork, not a typeset text zone). Surya's full-plate CER edge over the incumbent macOS Vision lane is real but small (−10 % mean, 4/6 plates) and not on the axis the pilot targeted. Details below.

## Prior-art note (read before running, per estate rule)

| Source | Takeaway |
|---|---|
| [datalab-to/surya](https://github.com/datalab-to/surya) (official) | Surya 2 = single 650M-param VLM for OCR/layout/tables; `pip install surya-ocr`; on CPU/Apple-Silicon requires `llama.cpp` (`brew install llama.cpp`); Hindi pass-rate 82.2 %, Russian 88.8 % on their internal 91-language benchmark; v0.20+ is a breaking rework (one `surya_ocr INPUT_PATH` CLI, no language flags) |
| [Aditya-PS-05/devanagari-ocr-benchmark](https://github.com/Aditya-PS-05/devanagari-ocr-benchmark) | 10 OCR systems on Hindi/Devanagari: clean rendered text is indistinguishable (chrF++ 91–98) but real printed scans collapse most systems (spread 76 points); English-OCR rankings do not transfer to Devanagari — synthetic benchmarks overstate Indic quality |
| [arXiv 2507.18264](https://arxiv.org/html/2507.18264v2) (Zero-shot OCR of low-resourced languages) | Surya excels on Sinhala (WER 2.61 %) yet is weak on Tamil — Indic performance is per-script, not per-engine; do not extrapolate Devanagari numbers from other Indic scripts |
| [Surya OCR 2 on an 800+ page Hindi/Sanskrit book](https://www.mrashutoshnigam.in/knowledge-hub/surya-ocr-2-hindi-sanskrit-book/) | User report: surya handles contiguous typeset Devanagari document bodies well (structure, formulas, tables) but needs review on damaged scans and unusual glyph combinations — i.e. document-page regime, not decorative-art plates |

## Corpus and protocol

- **Plates:** 6 masters from the plates-intake-qc corpus (G26-C intake + later batches), local masters in `~/Downloads`, staged untracked as `plates/` (gitignored; hashes via provenance in the intake report [G26_PLATES_QC_DRYRUN_04-10-2026](https://github.com/gasyoun/Uprava/blob/main/docs/G26_PLATES_QC_DRYRUN_04-10-2026.md)): `g01`, `g02` (1920×1080), `gst01` (1080×1920), `gzero`, `tradst` (1080×1920), `rudra` (1080×1350).
- **Reference:** agent vision transcription of each plate ([reference_transcriptions.json](reference_transcriptions.json)) — ordered text zones in reading order (CER basis) + best-effort set of visible Devanagari glyphs incl. tree-canopy letters (DevRecall basis, flagged approximate). Caveat stated: reference made by the benchmarking agent's vision, single read; RU strings cross-checked against `creative_plates_status.tsv` and the G26 dry-run.
- **Engines on the SAME 6 plates:**
  - `surya` — surya-ocr 0.22.x (Surya 2 GGUF via llama-server, Metal, `-ngl 99`), default full-page OCR ([run_surya_ocr.py](run_surya_ocr.py))
  - `vision_macos` — macOS Vision `.accurate`, ru-RU/en-US via Uprava [tools/ocr_plate.swift](https://github.com/gasyoun/Uprava/blob/main/tools/ocr_plate.swift) — the engine actually used on this corpus (G26 QC dry-run)
  - `tesseract` — tesseract 5.5.3, `rus+eng+san`, psm 3 (sanscritica-ocr Engine B)
- **Metrics** ([compute_cer.py](compute_cer.py)): `CER = levenshtein(ref, out)/len(ref)` on NFC-normalized, whitespace-collapsed text; `DevRecall = |ref_dev_set ∩ out_dev| / |ref_dev_set|` (order-insensitive, tree letters included).

## Per-plate CER table (lower is better; win = lowest CER)

| Plate | CER surya | CER tesseract | CER vision_macos | DevRecall surya | DevRecall tesseract | DevRecall vision | Verdict |
|---|---|---|---|---|---|---|---|
| g01 | **0.274** | 0.575 | 0.301 | **0.118** | 0.059 | 0.0 | surya |
| g02 | **0.272** | 0.578 | 0.320 | **0.118** | 0.059 | 0.0 | surya |
| gst01 | 0.350 | 0.550 | **0.258** | 0.083 | 0.0 | 0.0 | vision_macos |
| gzero | 0.328 | 0.672 | **0.254** | 0.0 | 0.0 | 0.0 | vision_macos |
| tradst | **0.320** | 0.740 | 0.640 | 0.0 | 0.0 | 0.0 | surya |
| rudra | **0.695** | 0.854 | 0.720 | 0.0 | 0.0 | 0.0 | surya |
| **mean** | **0.373** | 0.662 | 0.416 | 0.053 | 0.020 | 0.0 | surya 4 : vision 2 |

## Why NEGATIVE

1. **The pilot's axis is Devanagari, and surya does not win it.** DevRecall ≤ 0.12 on every plate for every engine; surya's 2/17-glyph hits on g01/g02 (a stray `क`) are noise-level. The corpus's Devanagari is scattered single aksharas embedded in painted foliage — an art-segmentation problem, not a recognition problem. Prior art agrees this regime is where OCR collapses (devanagari-ocr-benchmark: real-image robustness, not clean text, separates systems).
2. **The full-plate CER edge is small and not decision-relevant.** −10 % mean CER vs the incumbent macOS Vision lane (4/6 plates) on Cyrillic-dominant marketing plates whose QC decisions (forbidden-word filter, date/pair consistency, registry match) are word-level human checks, not character-level transcription.
3. **Cost asymmetry.** Adopting surya adds a 650M VLM runtime (llama-server, GGUF download, ~10× the macOS Vision lane's resource footprint) for a marginal gain on the wrong axis. The handoff says adopt only on a win; there is no Devanagari win to adopt.
4. **A re-pilot makes sense only when the corpus changes**: if plates gain contiguous typeset Devanagari text zones (book-page regime — surya's documented strength), re-run this benchmark on that subset. Parked as a GTD residual.

## Runtime measurement (within CPU/time budget — measured, not assumed)

- Box: Apple M3, 8 cores, 16 GB RAM, macOS (arm64). No GPU rental (per handoff).
- surya-ocr 0.22.x install (uv, torch 2.x macOS wheel): ~14 min (network-bound downloads, one transient retry).
- Model fetch (surya-2.gguf + mmproj from HF) + llama-server spawn: < 2 min; first plate batch (6 plates, Metal `-ngl 99`): **~75 s total**.
- macOS Vision lane: ~5 s/plate. Tesseract: < 1 s/plate.
- So surya DOES run within budget on Apple Silicon — the NEGATIVE verdict is a quality verdict, not a resource failure.

## Baseline-side limitation (honesty note)

sanscritica-ocr Engine A (Claude vision band-crop OCR) and the DashScope qwen3-vl-plus lane were NOT runnable from this worker (no Claude vision API budget on this executor; no DASHSCOPE key configured on this box). The baseline side is therefore the two mechanical engines above — `vision_macos` being the exact lane that produced the corpus's existing OCR outputs in the G26 QC dry-run. A Claude-vision Engine A comparison on the same plates remains possible follow-up, but Engine A is a per-page authoring workflow, not a plates-QC pipeline.

## Re-run commands

```sh
cd reports/H6325_surya_devanagari_ocr_pilot
# one-time: brew install llama.cpp tesseract tesseract-lang; uv venv ~/.venvs/surya-pilot --python 3.12
#           uv pip install --python ~/.venvs/surya-pilot/bin/python surya-ocr
bash run_baseline_ocr.sh plates outputs                                     # vision + tesseract
~/.venvs/surya-pilot/bin/python run_surya_ocr.py plates outputs             # surya
~/.venvs/surya-pilot/bin/python compute_cer.py reference_transcriptions.json outputs
```

_Гасунс_
