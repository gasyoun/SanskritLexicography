# pwg_ru — merged-layer translate prompt (LOCKED v1, 2026-06-17)

The translation stage for the **full supplement chain** (PWG + PW + SCH + PWKVN +
NWS), producing ONE consolidated Russian entry per headword. Supersedes the PWG-only
[`5_corpus_translate.md`](5_corpus_translate.md) for merged cards. Hardened from the
2026-06-17/18 a-section pilot (`aṃśa`, `anna`) — see the seven guards below, each tied to
a real judge finding.

## Conventions (unchanged)
- REGISTER: scholarly-philological Russian, faithful to the source's density.
- Translate to Russian ONLY the natural-language gloss prose — which is German (PWG/PW/
  SCH/PWKVN and many NWS sub-sources) but ALSO English and French in the NWS layer
  (see Guard 7). Translate each gloss FROM ITS OWN language, never relayed through German.
- KEEP VERBATIM: Sanskrit (IAST/Devanāgarī in `{#…#}`/`{%…%}`); literary sigla
  (ṚV., MBH., AK., MW, R., TS., …); German grammar abbrevs (m./f./n./Pl./Du./v.l.).
- TWO-SOURCE PRINCIPLE: text-cited sense = `attested`; kośa/grammarian-only =
  `lexicographic`.

## Task
Build the sense tree from the **PWG MAIN** entry; render every numbered/lettered
sense to Russian. Then FOLD IN the other layers (PW revision, SCH/PWKVN supplements,
NWS cumulative addendum), each net-new fact attributed in brackets `[PW]`/`[Schmidt]`/
`[PWKVN]`/`[NWS]`. Use `portrait.json` `corpus_synonyms` as the primary word-choice
evidence; discriminate near-synonyms à la Apresjan.

## The seven HARD guards (each from a pilot judge finding)

1. **No editorial-intent fabrication.** Attribute *facts* to layers, but NEVER narrate
   *why* a layer changed something. Forbidden: "[PW] omits X as unreliable", "dropped
   because…". PW/SCH simply do or don't carry a thing — state the presence/absence,
   not a motive. *(anna: invented "[PW] omits Sonne as unreliable".)*

2. **Don't label "[new]" without checking the earlier layer.** Only mark a sense as a
   layer's net-new addition if it is genuinely ABSENT from the earlier layers. A sense
   that already exists in PW (e.g. its sense 2c) is not a "[PW new]" — it is just PW's
   structure. Never re-list the same sense twice. *(anna: framed PW's own 2c "Wolke"
   as a brand-new addition and duplicated it.)*

3. **Keep every NWS sub-source's gloss with its OWN label.** NWS aggregates many
   sub-dictionaries (Grassmann, NṚV, MW, Olivelle, Keller, TAK, Hoernle, Sircar…).
   Do NOT swap or merge which sub-source owns which gloss. *(aṃśa: paired Keller 2006:198
   — the "shoulder" entry — with Olivelle's "numerator" sense.)*

4. **Render EVERY NWS sub-sense — do not condense the condensed.** NWS is already a
   "Kleines Zitat"; dropping its sub-senses loses net-new coverage. Render all of them.
   *(aṃśa: dropped real NWS senses — Rivelex/Renou "tire au sort", Vishva Bandhu
   "degree = 360th part", the Meyer "inheritance share" block.)*

5. **State cross-layer gender/structure deltas plainly, in one place.** When PW changes
   gender or restructures (e.g. PWG `m.`+`n.` → PW `n.` only → NWS re-adds an `m.`
   proper-name sense), say exactly that as a single clear note — don't scatter
   contradictory `m.`/`n.` fragments across senses. *(anna: m./n. layering muddled.)*

6. **NWS "Kleines Zitat" reads cite-AFTER-gloss.** The NWS string packs many sub-sources
   as `TAG > gloss … SOURCE:page >` — the diasystem tag comes BEFORE each gloss and the
   citation CLOSES it (comes AFTER). Pair every gloss with the source that *follows* it,
   never the one before; otherwise every label slides forward one entry. Sanity-check by
   author specialty (Keller = Indian mathematics; Hoernle = medical Bower Ms; Olivelle =
   Arthaśāstra/KA cites; TAK = Tāntrikābhidhānakośa; BHSD = Buddhist Hybrid Sanskrit;
   Sircar = epigraphy/EI). The unambiguous head entries prove the direction: `… a share
   of booty … MW:1 >` (English gloss is MW's, cite after). *(aṃśa: parsed as
   `SOURCE > TAG > gloss`, mis-attributing ~15 sub-sources and dropping Grassmann; the QA
   judge inherited the same misparse and false-cleared it — F12.)*

7. **The chain is MULTILINGUAL — translate each gloss from its own language.** NWS
   sub-sources are written in German (Geldner, Graßmann, Vishva Bandhu, Meyer, Windisch…),
   English (MW, Olivelle, Keller, Hoernle, BHSD, Sircar…) AND French (Renou, Padoux,
   Caland, Rivelex…). Do NOT assume "German" for the whole card and do NOT relay a French
   or English gloss through German. The per-unit source language is precomputed in the
   compiled manifest [`pilot/translate/<safe>.json`](../src/compile_translatable.py)
   (`lang`: `de`/`fr`/`en`; `en?` = undecided, read the gloss and judge; `sa` = a bare
   Sanskrit headword — KEEP verbatim, never translate). Render directly: French `N de
   division` → «название деления», `idée de participation` → «идея причастности», `tire au
   sort` → «тянуть жребий»; English `numerator of a fraction` → «числитель дроби», `a
   share of booty` → «доля добычи». A gloss given in two/three languages (NWS `riz cuit;
   cooked rice; gekochter Reis`) is ONE sense — render it once, not thrice. Sigla / IAST /
   grammar stay verbatim regardless of source language. *(a-section compile: 2,432 cards
   carry English NWS prose and 490 carry French — a German-only assumption mistranslates
   ~4,900 units.)*

Plus the original four (still in force): NO content fabrication · COMPLETE coverage ·
SIGLA UNTOUCHED (no German/English leaks into the Russian) · ALL records incl.
Nachträge. And: **discrimination must be built only from `portrait.json`
`corpus_synonyms.candidates`** — do not add register-synonyms absent from that evidence
*(anna: added "прокормление", not a candidate; missed corpus-attested рис/зерно/блюдо)*.

**QA-judge note (F12).** When a source format has an ambiguous reading-direction, a second
judge can share the translator's blind spot and rubber-stamp a systematic error. Arm the
judge with the parse rule explicitly and have it disambiguate by an independent signal
(here, each sub-source author's field).

**Owner-map feed (F12 eliminated by construction, 2026-06-23).** `_pilot_gen_merged.py` now appends an AUTHORITATIVE "PRE-PARSED OWNER MAP" (deterministic `nws_split` triples) to each card's NWS layer; the translator emits one row per entry with the owner VERBATIM and never re-derives owners. Validated: `ās` went MISATTRIBUTION (3 owner-swaps) → **CLEAN** (0 mismatches). Workflow HARD RULE 5 updated to consume the map.

## Sense-order policy & stratum badge (added 2026-06-24 — grounds: study A33)

Additive policy, not a change to the seven guards. Settled by the quantified sense-ordering
audit ([`research/HANDOFF_sense_ordering.md`](../research/HANDOFF_sense_ordering.md),
[`sense_order_metrics.md`](../research/sense_order_metrics.md)):

- **ORDER — render senses in PWG MAIN's PRINTED order** (the `<div>` numbering), verbatim.
  **NEVER re-sort senses** by frequency, by attestation date, or by anything else. The
  frequency-first pivot reorders the *translation queue* (which headwords are done first),
  **not** the senses inside a card. Why it matters: PWG's order is *etymological-genetic*,
  not historical — its sense 1 is the oldest-attested only **73.5 %** of the time (Kendall
  τ = 0.375), so a date/frequency re-sort would change the lead sense for **~1 entry in 4**
  and fight the source. Faithfulness to PWG's editorial order wins; chronology and frequency
  are *lenses laid over* that order, never replacements for it.
- **STRATUM BADGE (the «страт» column) = display metadata, never a reordering key.** Fill it
  from the sense's OWN cited sources: floor = Renou state of the *oldest* citation, ceiling =
  the *youngest* (e.g. ṚV + Manu → "Vedic–Classical"). Renou states: **I** ведийский · **II**
  паниниевский · **III** эпический · **IV** классический · **V** буддийско-джайнский. A sense
  with only kośa/grammarian citations (`lexicographic`) → «–».
- **Optional hardening (mirrors the F12 owner-map).** The per-sense stratum can be
  *precomputed deterministically* from `ls_source_map.json` (every `<ls>` siglum already
  carries a Renou state + date) and fed to the translator, instead of being inferred by the
  model — eliminating stratum-guess error the same way the pre-parsed NWS owner map
  eliminated F12. Tracked as a follow-up, not yet wired.

## Microstructure & apparatus rules (added 2026-06-24 — grounds: studies A33 + microstructure C + apparatus)

Additive policy folding in the three convention studies
([`research/HANDOFF_microstructure_conventions.md`](../research/HANDOFF_microstructure_conventions.md),
[`research/HANDOFF_apparatus_conventions.md`](../research/HANDOFF_apparatus_conventions.md),
[`research/HANDOFF_sense_ordering.md`](../research/HANDOFF_sense_ordering.md)). Verdict on every
axis: **PWG is the structural spine; Kochergina is the Russian-rendering model; never let a
later layer or Koch override PWG content.** Each rule below is keep / adapt / drop.

**Structural conventions (study C).**
1. **Homonyms — KEEP PWG's numbered split** (the `h` field). Carry PWG's `<h>1/2` as the record's
   `h`, split on PWG's etymology/POS basis. When PW *collapses* a PWG homonym (e.g. `aMSa` 1/2 →
   single + `aMsa`), keep PWG's finer split and note PW's collapse — do not inherit PW's single entry.
2. **Gloss — default to PWG's mixed equivalent + толкование.** Lead with a terse Russian equivalent,
   add a толкование where the equivalent is anisomorphic (Apresjan *требования к толкованиям*). Tag
   each sense `equivalence_type` = `equivalent` | `explanatory`. DROP MW's pile-of-synonyms habit —
   discriminate near-synonyms from `corpus_synonyms` instead (existing guard).
3. **Citation — KEEP the two-source `source_type`** (`attested` vs `lexicographic`, already in force).
   Density follows the layer: PWG full citations are the spine; PW/SCH cites are *supplements keyed to
   PWG*; treat GRA's exhaustive per-occurrence lists as collapsible (count + first cite). Flag SCH's
   inherited Böhtlingk cites as 1889-vintage, never re-verify them.
4. **Run-on — SPLIT for translation, GLUE for display.** Derivatives/compounds are their own
   translatable cards (PWG/PW idiom); reassemble into a MW-style nest only at display. Keep PWG's
   parenthetical etymology as the glue key. See [`ROOT_ENTRY_ARCHITECTURE.md`](../research/ROOT_ENTRY_ARCHITECTURE.md).

**Apparatus conventions (apparatus study).**
5. **Government / rekcija — NEW `government` sense field, rendered in the Kochergina idiom.** Where a
   sense governs a case/preposition, fill `government` like Koch: `+ Acc. (ради, для)`, `с Instr.`,
   `Abl. (по причине)`. Derive from PWG/PW case-`<ab>` tokens (PW alone carries ~14,420). Empty when
   nothing is governed. This is the integral grammar↔entry link (Apresjan pillar 1).
6. **Labels / diasystem — NEW `labels` sense field, Koch's Russian abbreviation set.** Map PWG `<ab>`
   (`N. pr.`→`nom. pr.`, `patron.`, `Bein.`) and AP90 bracketed domain markers onto Koch's vocabulary
   (`грам./миф./бот./мед./астр./филос./юр.`). Chronology does NOT go here — that is the `stratum`/`renou`
   fields (rule from study A33). DROP register/style back-fill from the 19th-c. dicts (effectively
   absent: PWG 0.2 %, PW 0, MW 3 tokens) — only Koch carries a thin register set, treat as optional.
7. **Etymology — KEEP PWG's `(von X)` derivation, translated** into the `notes`/inline gloss
   (`(von {#aMSa#} {%Schulter%})` → `(от {#aMSa#} «плечо»)`). DROP comparative-IE amplification — PWG's
   own preface assigns risky etymology to the big dictionary, not a learner-facing one. An AP90-style
   `[prakṛti+pratyaya]` bracket is an optional future enhancement, not required.
8. **Cross-references — KEEP & translate the pointer token** (`Vgl.`→«ср.», `S. u.`→«см.»). Capturing
   them as a typed, sense-numbered relations layer (Koch's `см. <lemma> N)` model; kośa co-citations →
   near-synonym sets) is a **follow-up SKOS layer**, not part of this prompt. DROP a dedicated antonymy
   schema (too sparse: `Gegens.`/`opp.`/`противоп.` are rare and inline).

**Schema.** Rules 5–6 add two OPTIONAL fields to
[`schemas/pwg_ru_final_card.schema.json`](../schemas/pwg_ru_final_card.schema.json) — `sense.government`
(string) and `sense.labels` (array of Koch label strings) — validated when present by
[`validate_final_card_schema.py`](../src/validate_final_card_schema.py); existing cards stay valid.

## Pilot result (baseline)
- `anna` — re-pass severity **3 → 2** (publishable after light edits): guards 1–2 fixed the
  editorial-intent/[new] meta-claims; discrimination re-grounded in corpus candidates; m./n.
  delta stated once. King Ānāka (1349 A.D., SJS 2:43) + the MW:45-vs-1313 derivative split
  verified faithful. Residual nits: stray German connectives (`u. s. w.`, `oder`) in the
  Russian column.
- `aṃśa` — first re-pass *regressed* (hidden severity ~4): the NWS layer had a systematic
  cite-after-gloss off-by-one (F12) that the QA judge inherited and false-cleared. Rebuilt
  from an explicit pre-parsed owner map; all 17 NWS sub-sources now correctly attributed,
  Grassmann's gloss restored, the `[aṃśena] partly` duplicate collapsed. Now severity ~1–2.

→ With guards 1–7 the recurring defects are addressed; re-run before scaling to the
full a-section. Source-language routing for the whole a-section is precompiled by
[`compile_translatable.py`](../src/compile_translatable.py) (`all` mode → one manifest per
headword, each unit tagged de/fr/en/sa/en?); audit NWS attribution with
[`nws_split.py check`](../src/nws_split.py) as a deterministic, judge-independent F12 gate.
