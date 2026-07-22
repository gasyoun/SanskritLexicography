# Print-bridge follow-ups — assessment (both are NOT quick fixes)

After the print bridge (PR #18) two follow-ups were flagged. On investigation, neither is a
small tweak; this records why, so they're scoped correctly rather than hacked.

## 1. Slice-C full-output recovery — coordination, do not re-run here

**State.** The per-root `wf_output.sc.*.json` files for the 16 requeued Slice-C roots are
requeue *subsets* (the full originals were overwritten when the requeue results were saved over
them). The bridge recovers jan/han from the shared `wf_output.sc.json`/`wf_output.json` and
flags the 11 thin roots; ~1,431 of ~1,989 cards are present.

**Why not now.** Recovery requires **re-running** those roots' full translation (the originals
are gone from local files, and the original Slice-C run was a different session whose transcripts
are not reachable here). That is a Max translation run, which **overlaps the autonomous account**
already doing Slice-C requeue work on `master` (it committed the `run_pilot_wf.sd_rq_*.js`
requeue harnesses). Launching a Slice-C re-run from this session would duplicate/race it.

**Disposition.** Coordination item — the autonomous account owns Slice-C requeue. When the full
roots are re-run, re-run `promote_final_cards.py` (idempotent, supersede) to complete the store.

## 2. Homograph `(key1,h)` keying — blocked on a missing discriminator

**Symptom.** In `--review-status ai_translated` preview, a promoted translation appears under
*every* `assembled_cards` entry that shares its `key1`, because [`export_interop.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_interop.py)
joins translations to structural cards by `key1` alone, and 11.7 % of `key1` (12,373) have >1
entry (homographs). The store rows are keyed on the headword `key1` (`meta.root`).

**Why it can't be fixed at the exporter now.** True per-homonym attribution needs a `(key1, h)`
join — but the **assembled side has no homonym discriminator**: a sampled 3-entry homograph
(`aNGas`) has `ord=None`, `hom=None`, `records[0].h=None` on every entry. There is nothing to
join the store's `h` against. The store side is ready (each row carries `h` and the homonym
ordinal is recoverable from `subcard`, e.g. `han~~h0_..` → `h0`); the blocker is that
`assembled_cards.jsonl` would first need a homonym key minted on its entries — the
"normalize `record.h` → `{h:int, sublemma, upasarga_chain}`" data-model task from the print
roadmap, not a bridge tweak.

**Why it is not urgent.** The multiplication is **inert in production**: it only shows in the
preview path. The default export gate is `{approved, human_reviewed}`, which is currently **0**
rows (no G5 review yet), so the citable edition emits no duplicated translations. The homograph
fix and G5 review are the same milestone — do the reconciliation layer when the renderer/edition
work starts, not before.

**Disposition.** Roadmap task (renderer/edition stage), tracked here; no code change now.

## Net

Both follow-ups are real but neither is a follow-up-sized change: one is a coordination boundary
(autonomous account owns Slice-C requeue), the other is blocked on a data-model layer that the
edition/renderer stage will build anyway and is inert until then.
