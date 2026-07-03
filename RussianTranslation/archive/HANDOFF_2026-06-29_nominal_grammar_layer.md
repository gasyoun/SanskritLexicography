# Handoff — build the non-root NOMINAL grammar layer (Scope B/C prerequisite)

Date: 2026-06-29 · Audience: Claude Code (new chat) · Repo:
`SanskritLexicography/RussianTranslation` (subdir of `gasyoun/SanskritLexicography`, `master`).
Read `GRAMMAR_LAYER.md` (the design) and `.ai_state.md` first.

## Why

The pwg_ru pipeline currently has a 3rd grammar axis only for **verb roots** (`whitney_grammar.py`
→ Whitney class/PPP/§§/irregularities, injected by `gen_opt_harness2.py`). But PWG is **123,366
headwords**, of which ~100k are **nouns / adjectives / compounds / indeclinables** — they need the
**full Whitney grammar** (Declension, Derivation, Compounds), a distinct layer. This blocks the
full-dictionary scopes (the DCS-frequent 43,968 and the whole 123k). Build it so PWG translation
is enriched once, not redone.

## Hard rule: REUSE, don't hand-roll

A hand-rolled SLP1-suffix stem classifier was prototyped and **discarded** (reinvention). Build
on the real tools that already exist in the org:

1. **Morphology engine — `vidyut` (0.4.0, installed).** Use `vidyut-prakriya` **subanta** to
   decline a nominal stem by gender → the real paradigm + stem class. WhitneyRoots already drives
   vidyut for verbs: reuse `WhitneyRoots/scripts/vidyut_paradigms.py` + `scripts/sanskrit_util.py`.
   Do NOT re-bind vidyut or guess stems from endings.
2. **Whitney nominal/compound §§ — the deferred ingest.** The crosswalk ingested only the *verb*
   §§ (ch IX–XV). Extend `WhitneyRoots/scripts/wikisource/fetch_whitney.py` to the **nominal +
   compound chapters (I–VIII, XVI–XVIII)**, then hand-verify a **stem-class → § concordance**
   (the analog of the verb form→§ concordance).
3. **Compound (samāsa) segmentation — reuse Jim's MW analysis.** The MW already segments compounds:
   `<k2>` uses em-dash member boundaries (`aMSakaraRa`→`aMSa—karaRa`), **182,023 compound entries**,
   in `csl-orig/v02/mw/mw.txt` (read-only). Join a PWG compound headword → MW by `k1` (SLP1) →
   take the `<k2>` em-dash split = the vigraha skeleton for free. MW gives SEGMENTATION; type
   (tatpuruṣa/bahuvrīhi/dvandva) + right-headed rendering come from vidyut-per-member + the TR's
   existing samāsa rule (head = 2nd member).
4. **Exception detection already exists.** `WhitneyRoots/scripts/dcs/grammar_ref_builder.py` →
   `src/grammar_refs.json` (935 roots) classifies §-citations **generic/specific/exception** from
   Whitney's "except/irregular/anomalous" wording. Apply the same idiom to nominal §§; and fold
   its **root** exception citations into `whitney_grammar.json` to enrich the existing root layer.

## Build order

0. Confirm vidyut works for subanta (`WhitneyRoots/scripts/vidyut_paradigms.py` as reference).
1. **Headword morphology classifier**: PWG headword (`k1` SLP1) + gender/POS tag → stem class +
   vidyut paradigm. Inputs: PWG `<lex>`/gender tags + DCS morphology (CoNLL-U, VisualDCS).
2. **MW `<k2>` compound-segmentation join** (a small lookup like `whitney_grammar.json`).
3. **Whitney nominal §§ ingest** + stem-class→§ concordance (hand-verified).
4. **`nominal_grammar_for(slp1, gender, pos)`** → block parallel to `whitney_grammar.grammar_for`:
   `{stem_class, gender, declension §§, compound type+members, derivation, irregularities}`.
5. **Wire into the portrait/harness** for non-root headwords (analog of the root grammar
   injection in `gen_opt_harness2.py`), then a small A/B (cost + a blind quality judge) before
   adopting — same discipline as `AB_TEST_LEAN_TR.md` (sequential cost runs, non-inferiority).

## Guardrails

- **csl-orig read-only** (MW source). **WhitneyRoots has an external actor** — consume its
  published data (`crosswalk/`, `src/grammar_refs.json`), don't fork/push it. Commit your work to
  `SanskritLexicography` (`master`, `ai-wip:`, Co-Authored-By line). Materialize derived lookups
  locally (like `whitney_grammar.json`) so the pipeline has no run-time dependency on siblings.
- Scope = roots are DONE (Scope A handoff); this layer is for the noun/compound headwords that
  unlock Scopes B (43,968 DCS-frequent) and C (123,366 full PWG). Nouns are cheaper/card than
  dense root sub-cards, so the $ estimates ($2–2.7k for B, $6–7k for C) may come in lower.
- Update `GRAMMAR_LAYER.md`, `.ai_state.md`, and `../../Uprava/GTD_NEXT_ACTIONS.md` as you land phases.
