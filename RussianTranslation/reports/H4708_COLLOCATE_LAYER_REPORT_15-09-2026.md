# H4708 — Collocate layer report: `dcs-sintagmatic-appendix7` → pwg_ru

_Created: 15-09-2026 · Last updated: 15-09-2026_

Mission (Uprava handoffs/H4708): consume kosha dataset `dcs-sintagmatic-appendix7`
to enrich pwg_ru word-portrait pages with per-lemma collocate context —
enrichment layer + dated report; never overwrite reviewed overlay data.

## What shipped

| Artifact | What it is |
|---|---|
| [src/pwg_collocate_layer.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_collocate_layer.py) | Deterministic builder: DCS_Sintagmatic.csv (IAST) → vendored sanskrit-util `to_slp1` → `headword_index.tsv` k1 join. `--selftest` (10/10 PASS, positive+negative+BOM-guard), `--spot-check N` (seeded re-derivation from raw CSV). |
| [src/pwg_collocate_layer.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_collocate_layer.tsv) | Committed sidecar (grammar-FAIR), 40,839 data rows, 3.5 MB: `k1 · hom · lemma_iast · total_occ · cooccur · collocates` (top-12 `iast:freq` pairs, pipe-delimited, source ranking preserved verbatim). |

Join coverage: **37,183 of 94,074 unique k1 (39.5 %)** gain a collocate profile,
emitted onto every homonym row (40,839 (k1, hom) rows) — same k1-level policy as
[pwg_derivation_layer.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_derivation_layer.py)'s
aggregated Pāṇini field: DCS aggregates the corpus lemma and cannot distinguish
PWG homonyms, so the profile is inherently homonym-ambiguous.

## Verification

- **Selftest:** `python src/pwg_collocate_layer.py --selftest` → **10/10 PASS**
  (join hit, homonym fan-out, top-N ordering + freq preservation, count
  preservation, two negative controls, skipped-line accounting, BOM guard).
- **10-portrait spot check:** `python src/pwg_collocate_layer.py --spot-check 10`
  (seed 4708) → **10/10 PASS** — each sampled row re-derived independently from
  the raw CSV; totals, co-occurrence counts and top collocates match
  (vyomayāna, marya, avimūḍha, śūkapattra, raṅgakṣetra, māṁsonnati, sadyaskāra,
  haryakṣa, śatatejas, anavacchinna).

## What did NOT change (the "never overwrite" guarantee)

- No `portrait.json`, no reviewed overlay, no store row was written. The layer
  is a sidecar only; `--apply` onto local portraits is the maintainer's step
  and is deliberately not implemented in this script (H1282 precedent).
- The source CSV is read-only; its known token corruption (e.g. `vikﾱp`,
  U+FFB1 mojibake in the pre-2026 dump) is carried through **verbatim** —
  cleaning is an editorial call, never a silent rewrite of a derived layer.

## Delivery (five fields)

- **Changed:** new builder + committed collocate sidecar; kosha
  `dcs-sintagmatic-appendix7` consumer registered; VisualDCS→SanskritLexicography
  edge row (Uprava PROJECT_INTERLINKS + interlinks_edges.tsv).
- **Unchanged:** headword_index, microstructure/portrait parser, pwg_ru store,
  all overlay/promoted data.
- **Checks:** `--selftest` 10/10 PASS · `--spot-check 10` 10/10 PASS ·
  coverage 37,183/94,074 k1 · 0 skipped CSV lines (79,985 usable of 82,799 registered).
- **Risks:** (1) DCS lemma aggregation is homonym-blind — collocates mix PWG
  homonym senses; consumers must treat the profile as k1-level context.
  (2) Source token corruption propagated verbatim by design. (3) The DCS corpus
  span ≠ PWG's textual scope — a headword's corpus collocates may reflect
  registers PWG never cites. (4) **Duplicate source lemma rows collapse
  last-wins** (`profiles[lemma] = …`): the file's ~82.8k lines hold 79,985
  distinct lemmas (FINDINGS §489), so repeated rows overwrite, deterministic but
  lossy. (5) `to_slp1` merges ṃ/ṁ → `M`, so variant-spelling lemmas collide onto
  one k1 and the first hit wins. (4)+(5) disclosed by the paired-family verifier
  (DeepSeek, 15-09-2026, verdict: pass).
- **Inspect:** `python src/pwg_collocate_layer.py --selftest && python src/pwg_collocate_layer.py --spot-check 10`

_Гасунс_
