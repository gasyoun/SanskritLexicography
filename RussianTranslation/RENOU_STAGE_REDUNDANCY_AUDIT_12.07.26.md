# RENOU stage-redundancy audit — verification + deletion PROPOSAL

_Created: 12-07-2026 · Last updated: 12-07-2026_

**Handoff:** [H692](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H692-Fable_RussianTranslation_assembled-cards-dedup-verify_11.07.26.md).
**Model:** Sonnet 5 (`claude-sonnet-5`), continuing an in-flight Fable 5
(`claude-fable-5`) session that had written but not yet run
[`src/renou_stage_redundancy_check.py`](src/renou_stage_redundancy_check.py)
in this same worktree. That script was run against the live data (all files
gitignored, local-only, single-copy under `RussianTranslation/src/` in the
main checkout) and its findings were cross-checked with an independent,
homonym-aware (`key1`+`hom`) positional verifier for the two series named in
the handoff (`assembled_cards`, `mw`) before any verdict below was written.
**ZERO files were deleted, moved, or renamed by this session** — this is a
proposal only, per the H692 stop condition.

## Series A — `assembled_cards` chain: CLEAN, safe-to-delete candidate

Chain: `assembled_cards.jsonl` → `.renou.jsonl` → `.renou.bhs.jsonl` →
`.renou.bhs.wl.jsonl` (120,173 rows each, identical `key1` order throughout).

Each stage strictly **adds** fields (`renou_dcs*`/`renou_enriched`/
`renou_provenance` at stage 2, `renou_bhs` at stage 3, `renou_wl` at stage 4)
and never mutates a substantive field already present. The only fields that
change value between adjacent stages are the two tracking fields
`renou_provenance` and `renou_enriched` — and every change there is a
**monotonic** addition (e.g. `{"V": ["dcs"]}` → `{"V": ["dcs", "bhs"]}`,
`renou_enriched: []` → `["V"]`), verified with zero exceptions across all
120,173 rows for every adjacent pair. No substantive field (`renou_dcs`,
`renou_dcs_oldest`, `renou_dcs_texts`, `renou_bhs`, `renou_wl`, `iast`,
`key1`, `key2`, `records`, `attested_senses`, `quarantined_records`, `reuse`,
`rights`) ever regresses between stages.

**Verdict: `assembled_cards.jsonl`, `.renou.jsonl`, `.renou.bhs.jsonl` are
fully content-contained in `.renou.bhs.wl.jsonl`** (mod. the intermediate
provenance/enriched *snapshot*, which is reconstructable from the final
file's provenance lists by dropping the `bhs`/`wl` source tags — see
`enrich_renou_bhs.py`/`enrich_renou_wisdomlib.py` for the tag semantics).

- **PROPOSE DELETE**: `assembled_cards.jsonl` (183 MB), `assembled_cards.renou.jsonl`
  (198 MB), `assembled_cards.renou.bhs.jsonl` (199 MB) — **~607 MB recoverable**.
- **KEEP**: `assembled_cards.renou.bhs.wl.jsonl` (201 MB) as the sole canonical
  file for this series.
- Out of scope (small, not part of this progressive chain — test/dev
  fixtures written by `assemble.py`/`validate_assembled_export.py`, not
  reused downstream the same way): `.chunk`, `.chunk.quarantine`, `.perf`,
  `.perf.quarantine`, `.quarantine`, `.smoke`, `.smoke.quarantine`, `.test`,
  `.test.quarantine` (all ≤14 MB, mostly KB-scale). Not audited here — no
  redundancy claim either way.

## Series B — per-dict `{code}_renou*` chain vs canonical `{code}.renou.jsonl`: NOT redundant, DO NOT DELETE

The `.`-vs-`_` naming split flagged by the census is a real, **org-wide,
systematic** pattern across 7 of 8 dictionary codes (`ap`, `ap90`, `ben`,
`bhs`, `mw`, `pw`, `sch`; `pwg` has only the canonical dot-file, no
underscore chain):

- `{code}_renou.jsonl` [→ `{code}_renou.bhs.jsonl` → `{code}_renou.bhs.wl.jsonl`]
  — the **old staged pipeline**, built 23/24‑06‑2026 by
  [`tag_mw_from_source.py`](src/tag_mw_from_source.py) /
  [`tag_dict_from_source.py`](src/tag_dict_from_source.py) →
  [`enrich_renou_bhs.py`](src/enrich_renou_bhs.py) →
  [`enrich_renou_wisdomlib.py`](src/enrich_renou_wisdomlib.py).
- `{code}.renou.jsonl` — the **canonical consolidated file**
  (`renou_bhs`+`renou_wl`+`renou_register`+`renou_register_provenance` all
  present in one file), built ~25‑06‑2026, roughly one day later and ~53 min
  after `dcs_lemma_renou.json` (the DCS attestation index) was itself
  regenerated (`2026-06-25 13:17`).

**Internally, the old underscore chain is clean** (same monotonic-addition
pattern as Series A, verified for `ap` and `mw` with zero substantive-field
regressions across every row of every adjacent pair).

**But the old chain's final stage is NOT a strict subset of the canonical
dot-file — real content diverges**, confirmed two ways:

1. Homonym-aware (`key1`+`hom`) positional check, exact (not sampled), on
   `mw`: of 286,560 rows, **13,836 (4.8%) differ in `renou_dcs`** and
   **9,737 (3.4%) differ in `renou_dcs_oldest`** — always by the canonical
   file having *fewer* register (I–V) attestations than the old chain (e.g.
   `aMSuhasta`: old `["IV"]` → canonical `[]`; `aka`: old `["I","II","IV"]`
   → canonical `["I","II"]`). Zero `key1` order mismatches; `mw.renou.jsonl`
   itself lacks a `hom` field the underscore chain carries, so alignment
   required matching by row position, not naive `key1` dict lookup (a naive
   `key1`-keyed comparison over-reports divergence because ~26% of `mw`
   `key1` values are shared across multiple homonyms).
2. [`src/renou_stage_redundancy_check.py`](src/renou_stage_redundancy_check.py)'s
   independent 1-in-25 `key1`-sampled check corroborates the same order of
   magnitude and additionally surfaces **`renou_ls` divergence** (citation-derived
   states, not just DCS-derived), which the exact `mw` check above did not
   probe: `mw` sample disagreement `renou_ls` 2,596/11,396 (22.8%), `renou_dcs`
   545/11,396 (4.8% — matches the exact count above), `renou_enriched`
   1,171/11,396 (10.3%). The same qualitative pattern (`renou_ls`/`renou_dcs`/
   `renou_enriched` disagreement, `renou_provenance`/order clean) recurs for
   `ap`, `ap90`, `ben`, `bhs`, `pw`, `sch` — this is **not an `mw`-specific
   anomaly**, it is systematic across the whole dictionary set.

**Working hypothesis (not confirmed — needs a human call):** the canonical
dot-files were regenerated a day after the old chain against a refreshed
`dcs_lemma_renou.json` (and possibly a refreshed `ls_source_map_mw.json` for
the `renou_ls` divergence), so the divergence may be a **correction**
(old chain over-attested; canonical is right) rather than a **regression**
(canonical is right for `renou_ls`/`renou_dcs` reduction but something else
broke). Recent unrelated pipeline work in the same window fixed a
"scale-plan OUT-path bug" (commit `f655bba`), which raises the prior that
index/attestation regeneration bugs were actively being hunted around this
date — but that commit is in a different subsystem (H255 no-PWG lane) and
is not confirmed to be the same code path.

**Verdict: KEEP BOTH old chain and canonical dot-file for every code until
the divergence is adjudicated.** This is explicitly **not** a
"row-counts-match → safe to delete" case — the row counts matching masked a
real, systematic ~3–23% (field-dependent) content difference. Deleting the
old chain now would be irreversible if the canonical regeneration turns out
to have regressed rather than corrected.

- **DO NOT DELETE**: `ap_renou.jsonl`, `ap_renou.bhs.jsonl`,
  `ap_renou.bhs.wl.jsonl`, `ap90_renou.jsonl`, `ben_renou.jsonl`,
  `bhs_renou.jsonl`, `mw_renou.jsonl`, `mw_renou.bhs.jsonl`,
  `mw_renou.bhs.wl.jsonl`, `pw_renou.jsonl`, `sch_renou.jsonl`
  (~379 MB total) — pending the `@DECIDE` below.
- Naming-drift catalog (dot = canonical/newer, underscore = old
  staged/older) — same table as above; no rename proposed here since the
  two are not (yet proven) interchangeable.

## Full run output

Raw per-code numbers (rows, distinct `key1`, containment stats, sampled
agreement) are in the script's own run — reproduce with:

```
python src/renou_stage_redundancy_check.py --out RENOU_STAGE_REDUNDANCY_RUN_12.07.26.md
```

(run from `RussianTranslation/src/` in the checkout that actually holds the
gitignored data files — this repo's worktrees do not carry them).

## GTD follow-up

- `@DO` (human executes, no urgency): delete `assembled_cards.jsonl`,
  `assembled_cards.renou.jsonl`, `assembled_cards.renou.bhs.jsonl`
  (~607 MB) — proven safe above.
- `@DECIDE` (human decides, blocks the ~379 MB underscore-chain deletion):
  is the 25‑06 canonical `{code}.renou.jsonl` regeneration a correction
  (old chain over-attested — safe to delete old chain once confirmed) or a
  regression (canonical under-attests — investigate `enrich_renou_dcs.py`/
  `tag_mw_from_source.py`/`ls_source_map_mw.json`/`dcs_lemma_renou.json`
  provenance around 25‑06‑2026 before trusting the canonical files for
  anything downstream)? Mirrored to
  [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).

## ADJUDICATION (12-07-2026, Opus 4.8 `claude-opus-4-8`) — CORRECTION, not regression

The `@DECIDE` above is resolved: the 25‑06 canonical `{code}.renou.jsonl`
regeneration is a **correction**. The old underscore chain over‑attested; the
canonical files are the trustworthy artifact.

> **Authoritative verdict:** this question was adjudicated org‑wide by **H771**
> (Opus 4.8, [SanskritLexicography PR #394](https://github.com/gasyoun/SanskritLexicography/pull/394))
> in a dedicated companion doc,
> [`RENOU_DCS_INDEX_REGRESSION_INVESTIGATION_12.07.26.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_DCS_INDEX_REGRESSION_INVESTIGATION_12.07.26.md)
> — CORRECTION for all 7 codes, **28,662/646,926 rows (4.4%)** divergent, every
> one a pure removal of a low‑confidence DCS state (thin `n=1` tail or Epic/`III`
> date‑fallback), **0 anomalies**; `renou_ls` **positionally byte‑identical**
> across all codes. Read that doc first — it is the primary record; the section
> below is an independent corroboration of the DCS axis from the audit doc where
> the `@DECIDE` was posed. Evidence, strongest first:

1. **DCS axis — proved exactly against the still‑present lossless index.**
   `renou.py` documents `DCS_MIN_SUPPORT = 2`: a register/state is kept only if
   attested in ≥2 DCS texts **or** backed by an authoritative source; the
   thin single‑text tail is pruned. The index `dcs_lemma_renou.json` is
   **lossless** — it stores the raw `state_support`/`register_support` counts,
   and the threshold is applied at consumption time (`filter_dcs_states`),
   fully tunable/reversible. Re‑running the projection over the live canonical
   `mw.renou.jsonl`: for **all 26,290** rows whose `key1` resolves in the index,
   the file's `renou_dcs` equals `filter_dcs_states(index_entry)` **exactly —
   0 mismatches**. The audit's own example `aka` is decisive: index
   `state_support = {I:3, II:1, IV:1}`; under min‑support≥2, `IV` (n=1, no
   authoritative backing) is pruned → canonical `["I","II"]`; the old chain's
   `["I","II","IV"]` carried the n=1 noise. The reduction is the documented
   confidence policy, not data loss — and nothing is unrecoverable, since a
   re‑run at `--dcs-min-support 1` reproduces the old behaviour from the same
   index.

2. **`<ls>` axis — no real divergence (H771).** The audit's sampled ~22.8% `mw`
   `renou_ls` figure was a **homonym‑misalignment artifact of `key1`‑keyed
   sampling**, not a data change: H771's positional (row‑order) check found
   `renou_ls` **byte‑identical** across all 7 codes. (My own earlier
   build‑timeline hypothesis for this axis is therefore moot — there was nothing
   to explain. The Phase 2/3 `<ls>`‑route commits refined the code but did not
   change the emitted `renou_ls` values between the two builds.)

3. **`renou_enriched` divergence is derivative** — it is the per‑row union across
   the corrected `renou_ls`/`renou_dcs` axes, so it necessarily moves whenever
   its inputs are corrected. No independent signal.

4. **The whole window was audit‑driven.**
   [`44e3637f`](https://github.com/gasyoun/SanskritLexicography/commit/44e3637f)
   (24‑06) records an *independent data‑integrity audit* fixing `renou_dcs_oldest`
   with **"entry counts unchanged"** — the corrections tightened per‑row state
   lists without dropping rows, exactly the pattern seen here.

**Consequences.** (a) Trust the canonical `{code}.renou.jsonl` files downstream
(the H4 citation‑bias, H6 Zipf, register portrait/audit work). (b) The old
underscore chain's deletion (H771, ~362 MB) was **safe** — it held pre‑audit,
over‑attested data reproducible from the lossless index at `min_support=1`.
(c) No fix or regeneration follow‑up is owed — there is no regression anywhere.

Reproduce claim 1 (aggregates only, no data rows) from `RussianTranslation/src/`:

```python
import json, renou
idx = json.load(open('dcs_lemma_renou.json', encoding='utf-8'))
m = x = 0
for line in open('mw.renou.jsonl', encoding='utf-8'):
    o = json.loads(line); e = idx.get(o.get('key1'))
    if e is None: continue
    if sorted(renou.filter_dcs_states(e)) == sorted(o.get('renou_dcs') or []): m += 1
    else: x += 1
print(m, x)   # -> 26290 0
```

_Dr. Mārcis Gasūns_
