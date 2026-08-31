# Content-aware re-glue spec

_Created: 06-07-2026 · Last updated: 31-08-2026_

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
| ∅ | an `≈крит.` address (`<span class=lsc>`) | **no** — deliberate: `mbh_locus.bori_href` is `None` by design (the BORI e-text is © BORI 1999, not redistributable), so no target will ever exist. H3501: the old digit-test flagged all 508 of them ⚑ on every card, overstating the mintable gap by exactly that count |

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

## 9. The vote had no evidence on it — and 90 % of it was unaskable (H2859, 16-08-2026)

§8 made the sheet legible. Asked for **more data in the voting**, the check found
the problem was not thin presentation but an unanswerable question.

### 9.1 The ≈ chip claims a relation to a sense that is not there

`restate` is assigned by **layer default** — `layer=pw` and no gender conflict —
*independently of whether an insertion target was found*. Measured over the
sidecar: **5,054 of 5,603 supplements (90.2 %) carry
`target_sense='*new'`**, the pipeline's own marker for "no PWG sense to attach
to", **and are still labelled `restate` ("PW abridging restatement")**. The chip
asserts a relationship to PWG while the insertion point simultaneously says there
is nothing to relate to. Asking a human "does this restatement sit at the right
PWG sense?" when the sidecar already says there is no such sense is not a
question, and no amount of extra display fixes it.

This is the same divergence §5a measured from the other side (PW renumbers, so
naive leading-integer attachment misfires) — but §5a read it as *placement falls
back to `*new`, nothing lost*. The label did not fall back with it.

### 9.2 What is actually checkable: 4.4 %

| bucket | supplements | share |
|---|---:|---:|
| no PWG target (`*new`) | 4,690 | 83.7 % |
| target exists, German too thin to compare | 303 | 5.4 % |
| **genuinely checkable** | **246** | **4.4 %** |

`nws/foreign_fragment` (62) and `pw/pw_correct` (1) have **zero** checkable pairs —
every one lands in `*new`. So the single `pw_correct`, the one cancellation the
whole corpus contains, cannot be verified against a PWG sense at all.

### 9.3 An evidence axis that was tried and rejected

Gloss-word overlap (Jaccard over German content words) was the obvious candidate
for making ≈-vs-＋ checkable. It does **not** discriminate — median 0.000 for both
classes — and the cause is the data, not the metric: a PWG sense body has a
**median of 3 content words** (39 chars) and 16 % have none, so two short German
synonym lists share no surface forms even when one restates the other. Kept in
[`reglue_overlap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reglue_overlap.py)
so the negative result stays reproducible, and deliberately **not** shown on a
card as a signal — a number that looks like evidence and isn't is worse than none.

Citation overlap survives as objective evidence and is displayed.

> A self-inflicted trap worth keeping: the first cut of that measurement stripped
> `{%…%}` along with `{#…#}`. `{#…#}` is Sanskrit; **`{%…%}` is the German meaning
> gloss** — the very text being compared. Deleting it drove 95 % of pairs to a
> spurious 0.000 that *looked* like a finding. Caught only by reading actual pairs
> instead of trusting the aggregate.

### 9.4 What the vote now is

[`build_reglue_evidence_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_evidence_sheet.py)
→ **one supplement per card**, 47 cards drawn only from the 246 checkable pairs,
stratified across every `(layer, subtype)` that has any. Each card carries the
**German original of both sides** (anatomy-coloured) — because the relation holds
between the sources, not between their translations — the Russian beneath it, and
the machine's full claim: subtype, op, direction, anchor, sidecar evidence string,
confidence, shared `<ls>` citations, and gloss-word counts. Reject reveals a
required reason (`wrong_place` / `wrong_label` / `both` / `not_a_supplement`).

The 90.2 % is reported in the footer as a finding, not put to a vote.

## 10. Two axes, not one: `placement` (H2879, 16-08-2026)

§9 diagnosed the defect; this is the fix. `subtype` was carrying two unrelated
claims at once — a property of the **layer** ("PW abridges PWG", true whether or
not anything was located) and a claim about the **pair** ("this supplement
restates *that* sense", true only when a target was actually found). They are now
separate fields, and `subtype` must be read together with `placement`.

| claim | field | true when |
|---|---|---|
| the PW layer abridges PWG | `direction: "abridging"` (pre-existing) | always; needs no target |
| this supplement relates to **that** sense | `placement: bool` (**new**) | only when the target is found in the PWG skeleton |
| what kind of relation it is | `subtype` (unchanged) | read **only together with** `placement` |

`subtype` is deliberately **not** renamed on unplaced rows: duplicating one fact
across two fields guarantees they drift apart.

> **Superseded 31-08-2026 by §13 (H3752).** The ruling above held for two weeks
> and was half right. Duplication really is the hazard — but the reader of a chip,
> a rollup row or a published percentage takes `subtype` **on its own** and never
> sees the boolean beside it, so 4,187 rows went on asserting a relation to a
> sense that was never identified. §13 does not add a third field: it makes
> `subtype` a **function** of `placement`, computed in one expression at one site,
> with the invariant asserted over the whole corpus by gate W5a. The row below is
> kept as written, and read together with §13.

### 10.1 `placement_reason` — three phenomena the old `*new` bucket merged

`placement=false` is not one thing. Measured over all 6,009 sidecar rows:

| `placement_reason` | rows | share | what it means |
|---|---:|---:|---|
| `found` | 595 | 9.9 % | target located in the PWG skeleton |
| `no_target_marker` | 4,901 | 81.6 % | the supplement's own tag has no leading number — no target exists *by construction*, not a lookup that failed |
| `out_of_range` | 383 | 6.4 % | the target number is above PWG's highest sense here — the later edition genuinely has more senses; **evidence about renumbering, not a data defect** |
| `not_found` | 130 | 2.2 % | inside the range, but no such sense — the only bucket that looks like a defect |

Separating `out_of_range` from `not_found` is the substantive gain: 383 rows that
read as broken links are in fact the renumbering phenomenon this project is
documenting, and only 130 rows are genuinely unexplained.

### 10.2 Tag normalisation — deliberately conservative

`normalize_sense_tag` strips trailing whitespace, `.`, `,` and an **unmatched**
trailing `)`, and nothing else, applied **symmetrically** to the PWG skeleton and
to the target. It does not merge `1-sub-…` (a sub-sense), `1 (PW)` (foreign
provenance), `Nachtrag` (an edit *to* a sense) or `caus-1` (another grammatical
branch) — each is pinned by a negative selftest. A false merge would produce a
silent `placement=true` on the wrong sense, which is worse than the defect being
repaired.

### 10.3 Measured effect — and what it is not

On an identical store and sidecar, switching the old raw-equality rule for the
`placement` flag:

| | old rule | new rule | delta |
|---|---:|---:|---:|
| checkable | 250 | **257** | +7 |
| no PWG target | 5,426 | 5,414 | −12 |
| too thin | 333 | 338 | +5 |

12 rows became placed; 7 of them have enough German to be compared. **This is a
correctness fix, not a coverage win** — the honest attribution is +7 checkable
pairs. The larger apparent jump from the previously published 246/4,690/303 is
mostly unrelated: that baseline was measured against a sidecar built 06-07-2026
while the store had moved on to 02-08-2026, so this pass also refreshed a stale
sidecar (5,603 → 6,009 rows). Wave 1's own effect is the +7.

`out_of_range` moved 381 → 383. VERIFICATION A4 expected it not to move at all;
the two extra rows are `vA h0` targets 8 and 9, in an article whose skeleton is
written `3)`–`7)` with no bare integer at all. Before normalisation that article
had no computable maximum, so both rows fell to `not_found`; they are genuinely
out of range and are now filed as such. The reclassification follows from S3's own
instruction to compute the maximum over normalised tags — A4's premise was
slightly wrong, not the implementation.

`placement_hypothesis` is implemented, guarded and selftested, but fires on **0**
real rows: no `not_found` row matched even under the looser key. The field earns
its place as the designed home for future named methods, not as a current result.

### 10.4 Acceptance is re-runnable

[`placement_axis_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/placement_axis_check.py)
proves A1–A5 and A9 against the artifacts on disk, including the two stop
conditions — that no row which had no target became placed (A3), and that the
canonical store is byte-identical (A5). Run it after any change to the classifier.

## 11. Corrections that live inside PWG itself (H2880, 16-08-2026)

Wave 1 split the axes for the *supplement* layers. The same defect sat one layer
down, in the skeleton: **365 rows carried on the `pwg` layer are not senses of
PWG at all.** They are the authors' own later supplements (`Nachtrag`,
`Nachtr.`, `addendum`, `addenda`, `corrigendum`) or material the later PW
edition contributed at a PWG sense (`1 (PW)`, `PW`, `PW-1`). Until now every one
of them was rendered as an ordinary skeleton sense — `**Nachtrag)** …` — so a
card asserted the existence of a PWG sense called "Nachtrag".

They are now classified `pwg_internal_correction` and attached through wave 1's
placement mechanism rather than a second, parallel one.

### 11.1 The marker is named, and the name is kept

A row leaves the skeleton only when a **named** printed cue matches
(`pwg_correction_marker`), and the matched name is recorded on the sidecar row as
`correction_marker`. A reviewer can therefore disagree with one specific rule
instead of with an opaque verdict. A tag matching nothing stays `base`: pulling a
row out of the skeleton wrongly *loses a real PWG sense* from the card, which is
the more expensive error in this direction.

The `PW`-family regex is anchored whole-string (`^\s*PW(?:[-_ ]?\d+)?\s*$`) so it
can never fire on `PWG` or `PWKVN` — a selftest pins exactly that, because the
failure mode is emptying the skeleton of its real senses.

### 11.2 The trap: a trailing digit is usually not a target

`Nachtrag-1`, `addendum-2`, `PW-1` and `Nachtrag §75-1` all carry a digit, and in
none of them is it a PWG sense number — it is the ordinal of the addendum, or a
section reference. Reading it as a target would silently attach the row to sense
1. The existing `lead_int` already declines these (no *leading* digit), so wave 2
adds no new extraction rule at all; it pins the behaviour with negative
selftests instead. Targets come only from a leading integer — `4 (Nachtrag)`,
`6_addendum`, `1 (PW)` — exactly as in wave 1.

### 11.3 Distribution — the answer to "how many actually attach"

| marker | rows | found | no_target_marker | out_of_range | not_found |
|---|---:|---:|---:|---:|---:|
| `nachtrag` | 184 | 6 | 178 | 0 | 0 |
| `addendum` | 88 | 18 | 66 | 3 | 1 |
| `pw_provenance` | 86 | 41 | 40 | 1 | 4 |
| `corrigendum` | 7 | 1 | 6 | 0 | 0 |
| **total** | **365** | **66** | **290** | **4** | **5** |

**66 of 365 (18.1 %) attach to a named PWG sense; 290 (79.5 %) carry no target
marker at all** — the open question in the handoff, answered by measurement
rather than guessed at. The asymmetry is the result: a `Nachtrag` almost never
names the sense it amends (6 of 184), while a `1 (PW)` almost always does (41 of
86), because the PW provenance tag *is* a sense number. Per the wave-1 contract
the unnamed 290 are `placement=false` with a reason, never a guess.

### 11.4 `op` is `amend`, deliberately not `correct`

`build_reglue` renders `op in ("correct", "delete")` with a
`~~(cancels PWG)~~` strikethrough. A Nachtrag *amends* the sense it points at; it
does not withdraw it. Reusing `op="correct"` would have struck through hundreds
of senses as cancelled. `direction` is likewise a new value `internal` — the
material is neither a later layer's addition (`additive`) nor the skeleton
(`base`). `placement_axis_check` W2d fails the build if a correction ever
acquires a cancelling `op`.

PW provenance is recorded on the existing `source_layers` (`["pwg", "pw"]`), not
as a second subtype — duplicating one fact across two fields is what wave 1's
decision 7 forbids.

### 11.5 A correction is not a target

`build_pwg_sense_index` now excludes correction rows, so a Nachtrag can never be
offered as the *target* of another Nachtrag — the wave-2 analogue of the defect
wave 1 removed. This is asserted, not assumed: W2b and W2c fail the build if a
correction is placed onto a correction, or if a correction tag survives in the
skeleton index. It is a **no-op for wave 1's numbers**, and that too is measured
rather than argued — see 11.6.

### 11.6 Wave 1 is provably untouched

Re-running wave 1's own code over this same store reproduces its published
figures exactly (6,009 sidecar rows · found 595 · no_target_marker 4,901 ·
out_of_range 383 · not_found 130). Against that baseline, wave 2 changes **zero**
non-`pwg` rows — not one row lost, gained, or altered in any field. The sidecar
grows 6,009 → 6,374 (+365, all corrections) and the reason counts move by exactly
the corrections' own distribution.

The canonical store is untouched and proved so: `rows=11603`,
`sha256 811bbc21…`, identical to wave 1's. Window suite 211/211.

> The stop-condition figure in the PLAN cover reads `rows=11715`; the real store
> has **11,603** rows, which is what wave 1 shipped against. The plan's number
> was stale on arrival — verify against the store, not the prose.

### 11.7 What wave 2 deliberately does NOT do

- **Not put on a vote.** The `h180-reglue-evidence` sheet asks "does this
  supplement from a later layer sit at the right PWG sense?", which is not the
  question to ask of a Nachtrag inside PWG. Corrections are excluded from that
  sheet's census, so its content and its 47 sampled cards are **byte-identical**
  to wave 1's. They get their own gate when wave 2 goes to review.
- **Not fed to the gloss-overlap metric**, which was measured and rejected
  (FINDINGS §541). `reglue_overlap` keeps skipping `pwg` rows, now by documented
  intent rather than by accident.
- **Not touching the canonical store**, per the roadmap's non-goals.

## 12. SCH corrects PWG too — 3.3 % of the time (H2881, 16-08-2026)

### 12.1 The hole

`classify_edition_rel` returned, for the `sch` layer, only `sch_star` or
`derived_sense` — both additive. So "SCH only supplements PWG" was **built into
the classifier**, not measured from the edition: no row of data could ever have
contradicted it. Wave 3 adds `sch_correct` and `sch_cancel` so the claim becomes
falsifiable, then measures it.

### 12.2 The criterion — a printed imperative, not a keyword

The cue lives in the **DE body**, not in the `sense_tag`. That is the one
structural difference from wave 2, and the reason `sch_correction_marker(de)` is
a separate predicate from `pwg_correction_marker(tag)`: a real SCH correction is
as likely to be tagged `mit-nis` as `SCH-corrigendum`.

| kind | rules | example from the store |
|---|---|---|
| `sch_correct` (`op=correct`) | `lies` · `zu lesen` · `Druckfehler` · `berichtige` · `verbessere` | `S. 152, Sp. 1, Z. 2 lies {%abhíhita%}` |
| `sch_cancel` (`op=delete`) | `streiche` · `tilge` · `fällt weg` | `— Mit {%abhyupa%} 3. streiche <ls>Med.</ls>` |

Every rule is an **instruction addressed to the reader**. That is the whole
criterion, and the negative controls are its load-bearing half: 11 of the 210
rows carry a look-alike token that is descriptive, not directive — bare `statt`
(`metrisch statt {%na gan˚%}`), the abbreviation `St.` (*Indische Studien*), and
`vgl.` These are pinned as negatives in `edition_rel --selftest` and as gate W3c.

**The gender path is deliberately absent.** The roadmap predicted wave 3 would
reuse `pw_correct`'s `<lex>` gender conflict. Measured: **zero of the 210 SCH
rows carry a `<lex>` token**, so that signal cannot fire on this layer. The one
real gender correction (`ahiphena`, "lies n. statt m.") states it in prose and is
caught by `lies`.

### 12.3 Scope — the cue governs the leading segment only

A compressed SCH article is a run of preverb sections. Where a correction clause
sits in a non-leading section (`— Mit {%samā%} Z. 3 lies 231,16` inside a row
that otherwise introduces four new senses), the row stays **additive** by the
conservative default: calling it a correction would assert SCH withdraws material
it in fact adds. Those rows carry `contains_correction_clause` so the residue is
a reported number (gate W3e: 2 rows), never a silent omission.

### 12.4 Result

210 SCH rows → 6 `sch_correct` · 1 `sch_cancel` · 203 additive (148 `sch_star`,
55 `derived_sense`). Unlike wave 2's `amend`, `op` is `correct`/`delete` here,
because these rows genuinely withdraw the printed reading — build_reglue's
"cancels PWG" strikethrough is the honest rendering. An **unplaced** correction
shows no strikethrough: it never identified a sense to strike, which is wave 1's
contract working, not a rendering gap. `direction` stays `additive`, the layer's
property, exactly as `pw_correct` keeps `abridging` (PLAN decision 1).

### 12.5 What wave 3 changes downstream

The evidence sheet drops one card, 47 → 46: `jñā · SCH → смысл 3` is now a
correction, and "does this supplement sit at the right PWG sense?" is not the
question to ask of one — the same exclusion wave 2 applied to Nachträge. Re-cut
under PLAN decision 8 after checking the vote gate (no `decisions.json` exists
for the sheet). Waves 1–2 are unchanged and proved so; the canonical store is
untouched.

## 13. The label follows the attachment (H3752, 31-08-2026)

Wave 1 (§10) split the axes and stopped one step short: it put the truth in a new
field and left the **old field still saying the false thing**. Measured on the
live store: **4,187 rows** labelled `restate` — "PW пересказывает *этот* смысл
PWG" — whose own `target_sense` reads `*new`. Every surface that reads `subtype`
alone (sheet chips, `relationships_rollup.tsv`, the "86 % is PWG paraphrase"
headline) therefore still reported a relation to a sense nobody located.

### 13.1 The fix is one field, not two

`subtype` becomes a **function of the placement result** — rewritten from
`placement` in the same expression that produced it, inside `classify_edition_rel`.
Three labels name a PWG *sense* as the other end of the relation and gain an
unplaced twin:

| label | placed | unplaced | twin |
|---|---:|---:|---|
| `restate` | 562 | **4,637** | `restate_unplaced` |
| `nws_at_sense` | 6 | **317** | `nws_at_sense_unplaced` |
| `a2a` | 10 | **112** | `a2a_unplaced` |

This is issue [#1736](https://github.com/gasyoun/SanskritLexicography/issues/1736)
**variant C**, with the issue's naming question answered *suffix*: wave 1 already
shipped the boolean, so the label was the missing half, not a second flag.

### 13.2 What is deliberately left alone

`direction` and `op` survive on every relabelled row — "the PW layer abridges
PWG" and "this row restates rather than adds" need no target. Dropping them is
variant B, which would erase the ＋/≈/✕ distinction from ~90 % of supplements;
gate W5c proves it did not happen. Three subtypes take no suffix, each for its
own reason: the additive ones (`sch_star`, `derived_sense`, `foreign_fragment`)
assert a new sense rather than a relation to one; `pw_correct` rests on the
gender index, a lookup that already succeeded; and `pwg_internal_correction` was
ruled on by wave 2 (§11.3), where unplaced-by-design is a published result.

### 13.3 Drift is prevented mechanically, not promised

§10's objection is answered by construction: one computation site,
`placement_label_consistent()` stating the invariant in both directions, and gate
**W5a** in `placement_axis_check.py` applying it to every row as a STOP. It was
**RED at 5,066 rows** against the pre-fix sidecar and is 0 after. Consumers learn
no second vocabulary — `base_subtype()` resolves a twin back to the key their
tables already use, so `TYPOLOGY` and `CLASS_OF` keep one row per relation kind.
A twin falling through to a lookup default would have painted these very rows as
green ＋ additions; a selftest pins that it cannot.

### 13.4 Scope, and what did not move

The canonical store is **untouched** — its `edition_rel` field exists on 86 rows,
all `base` or `pwg_internal_correction`, none sense-asserting, so 0 rows change
(gate A5 with the sha pinned). The mirror carries `ru`, which this does not
touch: `audit_store_gates.py` is byte-identical before and after. The label lives
in the derived sidecar, and the 5,066 moves are ledgered anyway, in
`pwg-ru-data/tm/h3752_relabel_ledger.jsonl`, joined on `row_key` (132 pairs
repeat here; a bare-pair join would ledger the wrong sibling — FINDINGS §551).

**The checkable population does not grow**: 637 placed rows before and after, so
the evidence sheet's cards are unchanged and it is not re-cut. Mode B — 521 rows
whose target number leads nowhere — is variant **D**, content alignment, and
stays out of scope; it remains split into `out_of_range` (387, the renumbering
phenomenon) and `not_found` (134). Full write-up:
[reports/H3752_RELATION_LABEL_REVISION_31-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3752_RELATION_LABEL_REVISION_31-08-2026.md).

_Dr. Mārcis Gasūns_
