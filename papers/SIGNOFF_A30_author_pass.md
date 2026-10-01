# SIGNOFF A30 — author-voice pass (light)

_Created: 06-09-2026 · Last updated: 06-09-2026_

**Scope.** Manuscript: [papers/A30_skd_vcp_microstructure_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_skd_vcp_microstructure_note.md) ("When Zero Means Nothing: Recovering the Indigenous Microstructure of the *Śabdakalpadruma* and the *Vācaspatya*"). Handoff: [H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md). Pass by Fable 5.1 (`claude-fable-5-1`), 06-09-2026. **Light pass by MG ruling 29-07-2026:** byline block plus abstract-, introduction- and conclusion-level de-AI only; §§2–8, References and the to-do list were not touched. Voice, register and framing only; no number, claim or citation altered; mechanical drift gate ([tools/voice_drift_check.py](https://github.com/gasyoun/Uprava/blob/main/tools/voice_drift_check.py) against `origin/master`) CLEAN. Prior review consulted: [papers/A30_review_fable5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_review_fable5.md) (hostile referee pass, 21-07-2026), whose findings are carried in §2 below, not acted on.

## 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Byline (line after the status block) | `Mārcis Gasūns · ORCID … · gasyoun@ya.ru` → `Mārcis Gasūns, independent scholar ([ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)), gasyoun@ya.ru` | Standard academic byline form of the series; affiliation was absent. ORCID and e-mail unchanged. |
| 2 | Abstract, before the enumeration | "Three results. First, …" → "The paper reports three results. First, …" | Two-word fragment parcellation before a First/Second/Third run. The three-part enumeration itself is the paper's structure and stays. |
| 3 | §1, paragraph 3 | "…is instrumental — and the recovered microstructure turns out to be dense, disciplined, and internally consistent." → "…is instrumental; the recovered microstructure is dense, disciplined and internally consistent." | Em-dash as connective plus "turns out to be" softening a direct claim the data supports. All three predicates kept. |
| 4 | §1, paragraph 4 (lead-in to the doctrine quote) | "The methodological rule … is stated in the corpus's measurement doctrine and is worth quoting at the outset, since everything below is an application of it:" → "The corpus's measurement doctrine already states the rule the demonstration licenses; it belongs at the outset, since everything below applies it:" | "Is worth quoting" is the empty-opener family; the rewrite names the source as subject and drops "is an application of" for "applies". |
| 5 | §9, final two sentences | "…a zero is a question about the instrument. The instrument, not the dictionary, is what the zero measures." → "…a zero is a question about the instrument; what it measures is the instrument, not the dictionary." | The same statement was made twice as a closing aphorism; one sentence carries it. Claim unchanged. |

Header: `Last updated` bumped to 06-09-2026. No pass note was added to the status paragraph (it lists no prior passes; brief rule).

Kept deliberately: "This paper shows / this paper answers" (third person) rather than first-person singular — §5 still reads "we argue", and a light pass must not create an abstract-vs-body pronoun split; see flag 7. "The moral generalizes beyond Sanskrit" (abstract) and "The megastructural moral" (§5) are the author's own register and stay.

## 2. Substance flags carried (not fixed)

1. **Abstract and §9 still state the register causal reading as a finding** — "the difference tracks record type (short encyclopaedic entry vs. long discursive commentary), not dictionary identity" / "in proportions governed by genre register rather than by dictionary identity". The review memo's M4 shows the committed length statistics run the other way (SKD mean 531 / median 221 chars vs VCP 493 / 162; VCP has more records, 50,135 vs 42,531) and no committed artifact stratifies fusion by record length. Untouched: a claim, not voice.
2. **Abstract still reports 53.3 % / 77.6 % as findings**, though memo M1–M3 and M5 document three instrument artifacts (severed unfused citations, a 16-name recall ceiling, `ityarthaḥ`/`ityādi` false positives) and an object mismatch between SKD micro-units and VCP whole-record lumps. The paper-side re-scope to "instrument-relative" that the memo asks for has not landed anywhere in the draft.
3. **§7 "fewer, longer, argumentative entries"** for VCP contradicts the paper's own §1 and §6 tables (VCP 50,135 records > SKD 42,531). Body-level; out of the light scope, but a referee will find it on the same page.
4. **Edition date "1822"** (§2, §8 limitation 6, References "Deva, Rādhākānta (1822–1858)") — memo's edition-facts check corrects to "8 parts, Calcutta 1821/22–1857, supplement 1858"; the to-do row is still open and the text still reads 1822.
5. **§8 limitation 1 promises the fusion figures "may sharpen" after the ~100-unit adjudication**; memo M7 argues the sheet adjudicates citational-vs-grammatical, not fused-vs-separable, so the human pass would not validate the headline numbers. The model-labelled pass exists ([A30_SKD_ITI_ADJUDICATION_MODEL_PASS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_SKD_ITI_ADJUDICATION_MODEL_PASS.md)); the human gate is open.
6. **Threshold sensitivity (`FUSION_MIN_CONTENT_CHARS = 20`) still un-run** (limitation 2, to-do item 5, memo M6). The threshold defines the headline statistic; no alternative value is reported anywhere.
7. **Voice, body-level, for the full pass:** §5 "we argue" — single-author paper using the editorial plural; §1 and the abstract say "this paper". A future full pass should pick one register for the whole manuscript. Also §6.2's "80,164 … 1.88 per record" are *iti*-token counts, and the memo asks that the token-vs-citation distinction be kept explicit at every mention (memo minor 3).
8. **Status block does not record the 21-07-2026 hostile review** ([A30_review_fable5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_review_fable5.md)); a reader of the manuscript header cannot tell that a major-revision verdict exists. Not added here: the brief limits header notes to the pass-list case.
9. **Cross-artifact drift** (memo C7-a): A08's 80,164 / 15,619 are from the 44-file artifact; the regenerated 43-file coverage build reads 80,173 / 15,627. Immaterial, but one sentence pinning the source is owed when §6 is next revised.

## 3. Read-and-sign

About 30 minutes: read the abstract, §1 and §9 in the diff against `origin/master` (six hunks, all listed in §1 above), veto any call by reverting the hunk, then decide on flags 1–4, which a referee reaches first.

**Proposed readiness (propose only):** hold at **3/5**. Nothing in this pass touches the reason the review memo withheld 4/5 — the §6–§7 re-scope (flags 1–3) has not been written. Once that afternoon of edits lands, the memo's own 4/5 proposal applies; the voice pass does not move the gate either way.

**Venue recommendation (recommendation only, no submission before 2026-11-01):** the review memo's input stands — WSC 2027 for a first submission, since a methods-aware Sanskritist audience will read an instrument-relative §6 as a strength, while an IJL referee is likelier to bounce §6 as drafted. A human should decide; the open `@DECIDE` rows (venue, A35↔A04↔A30 lead paper) are unchanged.

_Dr. Mārcis Gasūns_
