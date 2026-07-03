# A34 — verification of the épigraphique corpus-absent headline

_Created: 03-07-2026 · Last updated: 03-07-2026_

Data-verification pass over the headline claim of
[`papers/A34_renou_register_note.md`](A34_renou_register_note.md) (§3.2): *"of 709
headwords tagged épigraphique, 484 (68 %) have no attestation in the literary corpus at
all."* This note records that the figure **reproduces exactly** from the committed
tagged indices, states the precise definition that yields it, and flags one stale
companion figure to reconcile.

## Verdict: 484 / 68 % confirmed

Computed over the eight Renou-tagged dictionaries (PWG, MW, PW, AP, AP90, BEN, SCH, BHS),
deduplicating épigraphique headwords by IAST key:

| quantity | value |
|---|--:|
| distinct épigraphique headwords | **709** (matches the glossary exactly) |
| corpus-absent — no `renou_dcs` **and** no `renou_enriched` state | **484 (68.3 %)** — **the paper's figure** |
| corpus-absent — no `renou_dcs` state only (stricter) | 518 (73.1 %) |

So the headline is **exact** under the paper's definition: a headword counts as
corpus-attested if it carries *either* a direct DCS-corpus state (`renou_dcs`) *or* an
enriched DCS-derived state (`renou_enriched`); the 484 that carry neither are the
inscription-only vocabulary (donative/administrative terms, monastery names, the dynastic
onomasticon). The stricter "no `renou_dcs`" reading gives 518 (73.1 %); the paper's 68 %
is the conservative one.

## One companion figure is stale — reconcile before submission

[`RENOU_FINDINGS.md`](../RussianTranslation/RENOU_FINDINGS.md)'s per-register table (last
updated 02-07-2026) reports the épigraphique corpus-absent rate as **63.0 %** (≈ 447),
which **does not reproduce** from the current committed indices — no natural definition of
"corpus-absent" recomputes 447 (the candidates are 484 and 518, above). It is a stale
hand-copy from an earlier DCS-index generation. The whole per-register table there should
be regenerated from `renou_audit.py` against the current indices so it agrees with the
paper's 68.3 %.

## Reproducibility dependency (fresh clone)

The per-lemma tagged indices `src/{code}.renou.jsonl` and the DCS state map
`src/dcs_lemma_renou.json` are **gitignored** (DCS-2026-snapshot-dependent), so a clean
checkout cannot recompute the 484 until they are regenerated with
`python renou_pipeline.py --all`. This is the paper's declared §5 posture (the indices are
"gitignored and regenerated"); the committed **glossaries** remain the walkable artifact
for the 709 headwords themselves. The DCS corpus itself is external (VisualDCS boundary).

_Dr. Mārcis Gasūns_
