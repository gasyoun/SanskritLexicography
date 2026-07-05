# Content-aware re-glue spec

_Created: 06-07-2026 · Last updated: 06-07-2026_

**Deliverable 3 of
[H180](https://github.com/gasyoun/Uprava/blob/main/handoffs/H180-Opus_RussianTranslation_pwg_ru_addenda_typology_glue_learner_05.07.26.md)**
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

## 6. Guardrails

- Never blocks the H179 run; consumes its output.
- **No re-translation** — assert byte-identity of every `ru` against the store in CI.
- The layered store remains canonical; `reglue/` is derived and regenerable.
- LLM smoothing is optional, marked, and content-neutral.

See [`SYNTHESIS_PILOT_10.md`](SYNTHESIS_PILOT_10.md) for the bake-off that tests whether
*synthesize-German-first* ever beats this after-translation remix.

_Dr. Mārcis Gasūns_
