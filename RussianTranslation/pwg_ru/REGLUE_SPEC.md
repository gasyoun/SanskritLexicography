# Content-aware re-glue spec

_Created: 06-07-2026 · Last updated: 15-08-2026_

**Deliverable 3 of
[H180](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H180-Opus_RussianTranslation_pwg_ru_addenda_typology_glue_learner_05.07.26.md)**
(canonical after-translation track). The five layers are today glued **mechanically**
(fixed order PWG → PW → SCH → PWKVN → NWS, no sense-aware placement). This spec designs
a **content-aware remix** that interleaves the *already-translated* sub-cards so each
supplement sits at its relevant PWG sense — proving the re-glue is **free** (zero
re-translation).

## 1. Canonical design ruling (MG 05-07-2026)

- The **layered, provenance-preserving store stays canonical.** Synthesis is a *derived
  presentation*, built after translation, never replacing the per-sub-card store.
- Sub-cards stay individually translated + auditable (free re-glue preserved).
- The remix step **never calls the translate workflow** — it consumes
  [`src/pwg_ru_translated.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ru_translated.jsonl)
  only. This is the proof that re-glue is free.

## 2. Inputs (all already on disk)

Per sub-card, keyed by `key1` + `subcard`:
- `layer` (H179 Step 1): `pwg` | `pw` | `sch` | `pwkvn` | `nws`.
- `sense_tag`: PWG sense number (`6`) or supplement tag (`NWS-1`, `anu_desid`, `ava_caus`).
- `provenance.relationship.insertion_point` (from
  [`ADDENDA_TYPOLOGY.md`](ADDENDA_TYPOLOGY.md) §2/§4): `{homonym, target_sense, anchor}`.
- `ru` (translated body) + `de` (source) + the markup (`{%…%}`, `<ls>`, `<lex>`).

## 3. Algorithm (deterministic + light LLM assist)

For each `key1`:

1. **Skeleton.** Take all `layer=pwg` sub-cards, ordered by homonym then `sense_tag`
   numeric — this is the frame. Everything else hangs off it (MG: "PWG remains the
   skeleton").
2. **Attach.** For each non-`pwg` sub-card, read `insertion_point.target_sense`:
   - a PWG sense number → splice **inside** that sense block as a marked supplement
     (`— [SCH] …`, `— [NWS] …`), carrying its layer badge + source citations.
   - `*new` → append as a new, badged sense at the end of the homonym, flagged *addition*.
   - `*whole` → attach at entry head (applies to the whole headword).
3. **Cancellations.** A `pw_cancel` / `pw_correct` instance (op=`delete`/`correct`)
   renders the PWG value **struck / annotated** in place (`PWG n. → PW m.`), never
   silently dropped — provenance is visible.
4. **Foreign fragments.** `foreign_fragment` sub-cards (NWS in FR/LA/**EN**) render the
   Russian translation as the body with the original-language source shown beneath
   (badge `‹fr›`/`‹la›`/`‹en›`).
5. **Deterministic first, LLM only for prose smoothing.** Steps 1–4 are pure data
   placement. An **optional** LLM pass only *smooths connective prose* between spliced
   blocks (never invents content, never re-translates) and is marked
   `reglue_smoothed: llm` so it is auditable and skippable.

Output per entry = a **print-oriented card**: PWG skeleton with SCH/NWS/PW/PWKVN
additions inline at their sense, cancellations struck/annotated, foreign-origin bits
shown with their RU translation.

## 4. Output artifact

`pwg_ru/reglue/<key1>.json` (+ a rendered `.md`/`.html` for eyeballing), schema:

```json
{"key1":"gA","homonyms":[
  {"h":"h0","senses":[
    {"sense":"1","pwg_ru":"…","supplements":[
      {"layer":"sch","subtype":"sch_star","ru":"…","source":"…","confidence":"llm"}]},
    {"sense":"*new","added_by":"nws","ru":"…","source":"Sūryas iv,26","lang":"en"}
  ]}]}
```

No field here requires a new translation — every `ru` is copied from the sub-card store.

## 5. Pilot (15 rich multi-layer headwords, zero re-translation)

Chosen from the translated set (measured 06-07-2026; the corpus is verb-root-first per
H179/H201, so the pilot is roots):

- **5 layers** (pwg+pw+sch+pwkvn+nws): `gA` (319 sub-cards), `Cid` (154 — includes the
  NWS English foreign-fragment case), `Sam` (172), `jIv` (78), `rakz` (67), `vraj`
  (128), `yat`.
- **4 layers**: `DA` (803 — the stress test), `Ap` (152), `Bid` (205), `Buj` (104),
  `banD` (137), `Sru` (80).
- **3 layers** (handoff-named family): `viS` (537, pwg+pw+pwkvn), `siD` (187).

`DA` (803 sub-cards) is the load/coherence stress case; `Cid` exercises the
foreign-fragment path; `gA` exercises all five layers at once.

**Success criteria:** (a) byte-identical `ru` bodies vs the sub-card store (proves zero
re-translation); (b) every supplement lands at a real PWG sense or a flagged `*new`;
(c) no cancellation silently dropped; (d) human spot-check of the 15 rendered cards on
an interactive HTML sheet.

Builder to write: `src/build_reglue.py` (consumes `pwg_ru_translated.jsonl` +
relationship sidecar; emits `pwg_ru/reglue/`). Depends on
[`ADDENDA_TYPOLOGY.md`](ADDENDA_TYPOLOGY.md)'s `build_relationships.py` having populated
`insertion_point`.

## 5a. Pilot run results (06-07-2026, Arm A — zero re-translation proven)

[`src/build_reglue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue.py)
built all **15/15** pilot headwords →
[`pwg_ru/reglue/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/reglue)
(`<key1>.json` + rendered `.md` + [`PILOT_SUMMARY.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/reglue/PILOT_SUMMARY.tsv)).

**Success criteria met:**
- **(a) byte-identity** — every emitted `ru` (skeleton *and* supplement) is asserted
  present verbatim in the store; all 15 pass `byte_ok=True`. **Re-glue is free.**
- **(b) nothing lost** — every supplement lands at a real PWG sense (`placed`) or is
  flagged `*new`; none dropped.
- **(c) cancellations visible** — the 1 `DA` `pw_correct` renders annotated, not dropped.
- **(d) human spot-check** — deferred to an interactive HTML voting sheet (not checkboxes).

**Key finding — descendant sense-numbering diverges from PWG, so most supplements fall
to `*new` rather than `placed`** (e.g. `Sam` 0 placed / 130 new; `DA` 36 / 412). Two
causes, both measured:
1. **PW renumbers.** A PW sense `5` is *PW's own* numbering, **not** a pointer to PWG
   sense 5 — so naive leading-integer attachment misfires. True alignment needs *content*
   matching (gloss-to-sense), which is exactly the deferred gold pass, not a first-pass
   heuristic.
2. **The store is verb-root-first** — PWG senses live on *per-preverb* sub-cards each with
   their own `1,2,3…`, so a flat "sense N" key is ambiguous until more of PWG is
   translated.

The mechanism is proven and lossless; higher placement is a *content-alignment* task for
the gold pass, not a re-glue-engine fix. This divergence is itself evidence for the
Deliverable-5 paper ("how the tradition renumbered itself when it abridged").

## 6. Guardrails

- Never blocks the H179 run; consumes its output.
- **No re-translation** — assert byte-identity of every `ru` against the store in CI.
- The layered store remains canonical; `reglue/` is derived and regenerable.
- LLM smoothing is optional, marked, and content-neutral.

See [`SYNTHESIS_PILOT_10.md`](SYNTHESIS_PILOT_10.md) for the bake-off that tests whether
*synthesize-German-first* ever beats this after-translation remix.

## 7. N14 pilot — edition-diff reading surface (H1631, 26-07-2026, PARTIAL CLOSE)

A lighter-weight sibling of the full re-glue engine: a **read-only diff/badge view**
(not a print-oriented merged card) over the same `edition_rel` classification
(H1624 G4), for browsing rather than final presentation.
[`src/pilot/build_edition_diff_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_edition_diff_site.py)
renders the PWG skeleton with PW/SCH/PWKVN/NWS supplements attached at their
`insertion_point.target_sense`, each badged with its subtype — no DE rewrite, no
re-translation, no new typology. Pilot coverage: the same 7 five-layer roots as
Section 5 (`gA`, `Cid`, `Sam`, `jIv`, `rakz`, `vraj`, `yat`); counts in
[RESULTS_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md)
26-07-2026. **Not yet done:** scaling past the 7-root pilot, per-sense visual
polish, and this view does not replace the Section 4/5 print-oriented re-glue
output — the two are complementary (diff/browse vs. merged/print).

## 8. The presentation layer — what a reviewer must SEE (H2827, 15-08-2026)

Sections 1–5 fix what the re-glue *is*; this section fixes what it *shows*. Three
defects of the v1 spot-check sheet, each with its ruling:

### 8.1 Citations are links, not prose

Every `<ls>` in a rendered card goes through
[`ls_links.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_links.py),
a rendering layer over the repo's existing
[`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py).
**83.6 %** of the store's 41,115 citations resolve to a Cologne scan/text target.
Never write a second resolver: Cologne's own precomputed csl-lslink table reaches
only 79.3 % and wins zero citations the resolver misses — full measurement in
[FINDINGS §536](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

The unresolved remainder is rendered as **two distinct marks**, because it is two
distinct things:

| mark | meaning | is it work? |
|---|---|---|
| ⚑ | a real locus no pattern covers | **yes** — the mintable gap |
| ∅ | a bare abbreviation (`GORR.`, `ed. Bomb.`) with no locus | **no** — nothing to point at, ever |

Collapsing them into one "unresolved" count overstates the backlog by about a
fifth. Per-card totals sit in a coverage strip above the card.

### 8.2 The glue typology is a first-class visual, keyed to ONE question

[`ADDENDA_TYPOLOGY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ADDENDA_TYPOLOGY.md)
already defines three axes and eight subtypes. For *reading a card* only one
question matters — **did this supplement add meaning, or not?** — so the eight
subtypes collapse to three colour-coded classes:

| class | subtypes | what the reader concludes |
|---|---|---|
| **＋ added meaning** (green) | `nws_at_sense` · `sch_star` · `derived_sense` · `foreign_fragment` · `a2a` | a later layer knows something PWG did not |
| **≈ restatement** (amber) | `restate` | PW says the same thing more briefly — **no new meaning** |
| **✕ cancels / corrects** (red) | `pw_correct` · `pw_cancels` | PWG's value is overridden; never silently dropped |

This is not decoration — it is the finding. Across the 15 pilot cards: **1,534
restatements vs 250 additions vs 1 correction**. Roughly **86 %** of everything
glued onto PWG is PW abridging what PWG already said. A reviewer who cannot see
that at a glance will read a card as far richer than it is.

**Ordering ruling (answers "are the glued-in entries ABOVE all old?"):** no. PWG
remains the skeleton (§1) and supplements are rendered *beneath* the PWG sense
they attach to, in layer order. A supplement is visually subordinate to the sense
it supplements; only a `*new` sense — one with no PWG sense to attach to — is
promoted to its own block at the end of the homonym. Position encodes attachment,
the chip encodes relationship; neither encodes precedence.

### 8.3 Gloss chains are split for reading, never in the store

NWS and SCH separate sense clusters with a **full stop** carried over verbatim
from the German (`gehen, kommen, wandern. weggehen.` → `идти, приходить,
странствовать. уходить.`). That is faithful to the source and unnatural in
Russian. The ruling: **split at render time, never in the store.** The card shows
numbered clusters; the raw store string stays one panel away, unchanged and
byte-identical (§6 guardrail intact).

The splitter is deliberately timid — it refuses to split inside a `{#…#}` Sanskrit
span, inside an unclosed bracket, after a known abbreviation (`нар.`, `т. е.`),
after a Russian clitic (`кому-л.`), or anywhere in a citation-bearing body, and it
falls back to plain rendering unless it finds ≥2 clusters. A missed split is
invisible; a wrong split silently rewrites a definition.

**Sheet:** [h180_reglue_v2.html](https://gasyoun.github.io/vote/sheets/h180_reglue_v2.html)
(generator
[`build_reglue_sheet_v2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_sheet_v2.py)).
v1 stays published for comparison but is not the vote.

_Dr. Mārcis Gasūns_
