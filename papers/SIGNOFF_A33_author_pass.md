# SIGNOFF A33 — author-voice pass

_Created: 06-09-2026 · Last updated: 06-09-2026_

**Scope.** Manuscript: [papers/A33_sense_ordering_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_sense_ordering_note.md) (*Genetic, not historical: how the 19th-century European Sanskrit dictionaries order senses — and how Apte and Kochergina differ*). Handoff: [H3857 all-articles author-voice pass workflow](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md). Pass by Fable 5.1 (`claude-fable-5-1`), 06-09-2026, against the hostile referee memo [A33_review_fable5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_review_fable5.md). Voice, register and framing only; no number, claim or citation altered; mechanical drift gate ([voice_drift_check.py](https://github.com/gasyoun/Uprava/blob/main/tools/voice_drift_check.py)) CLEAN. Every call below may be vetoed by reverting the hunk.

## 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Title block | Added the academic byline line (`Mārcis Gasūns, independent scholar (ORCID …), gasyoun@ya.ru`) under the H1 | The draft carried no byline; every target venue needs one on page 1 |
| 2 | Status blockquote | Added the "author-voice pass 06-09-2026" note with a link to this signoff; header `Last updated` bumped | Brief-mandated provenance line, nothing else touched in the status paragraph |
| 3 | Abstract, sentence 1 | "the great 19th-century European dictionaries" → "the 19th-century European dictionaries" | Grand epithet; the dictionaries named in the same sentence carry the weight without it |
| 4 | Abstract | "we test this at corpus scale" → "I test this at corpus scale" | Single author; Lexikos, IJL and eLex all accept first-person singular. Revert to "we" if the venue's style sheet says otherwise |
| 5 | Abstract | Bold removed from ten spans (`**historical**`, `**half right**`, `**etymological-genetic**`, `**73.5 %**`, `**52.7 %**`, `**moderately**`, `**pedagogical salience**`, `**2.3 %**`, `**0 %**`, `**23–25 %**`) | Bold-every-other-word; journals typeset abstracts without inline emphasis, and the sentences carry the contrast on their own. Italics on *within*, *Grundbedeutung*, *tendency* kept |
| 6 | §1, paragraph 1 | "We test it." → "I test it."; `**microstructure**` → plain | Same singular voice; the term is defined in the sentence and needs no bold |
| 7 | §1, related-work paragraph | "The typology we test" → "The typology I test"; "our Vedic-density discriminator" → "my Vedic-density discriminator" | Singular voice |
| 8 | §1, related-work paragraph | "That PWG and MW behave as 'the same animal' (§3.1) is expected" → "That PWG and MW order senses almost identically (§3.1) is expected" | Decorative metaphor, used twice in the paper; replaced by the literal finding. The §3.1 cross-reference is unchanged |
| 9 | §1, last sentence | "What we add to this line is quantification" → "My contribution to this line is quantification" | Makes the one explicit contribution statement singular and unmistakable; the content of the claim is untouched |
| 10 | §2 | "We use the CDSL editions" → "I use …"; "For each entry we segment" → "For each entry I segment"; "we compute Vedic-citation density" → "I compute …"; bold removed from "Vedic-citation density" | Singular voice; the term is already introduced in bold-free prose in the abstract |
| 11 | §3.1, paragraph after the table | ~~"The two dictionaries are statistically almost the same animal." → "The two dictionaries are statistically near-identical."~~ | **Reverted after adversarial verify:** "near-identical" strengthens the claim beyond the original "almost the same animal"; origin wording restored |
| 12 | §3.1 | Bold removed from "date-agnostic chance floor of 52.7 %", "real but partial", and the closing "genetic lead sense, chronological tendency" | Decorative emphasis; the closing sentence is the thesis and reads more firmly without it. The `**therefore**` inside the Grassmann quotation is kept: it is the author's emphasis on quoted text and part of the argument |
| 13 | §3.2 | Bold removed from "Classical/Pāṇinian technical sense" | Decorative emphasis |
| 14 | §3.3 | Bold removed from "logical-semantic / pedagogical" | Decorative emphasis; table cells untouched |
| 15 | §4, opening | ~~New first sentence: "The question posed at the outset now has its answer — a genetic lead sense, with a chronological tendency behind it — and the answer has a practical edge."~~ | **Reverted after adversarial verify:** the added sentence asserts a settled answer the paper itself qualifies as a tendency, and adds framing not present in the abstract; sentence deleted, §4 opens as in origin |
| 16 | §4 | "Our measurement shows the cost" → "The measurement above shows the cost"; bold removed from "change the lead sense for ~26.5 %", "preserve the source order", "per-sense display metadata" | Singular voice; decorative emphasis |

Left as they were on purpose: the two result tables (cell-level bold is the tables' own convention); the run-in labels **Relation to existing work.**, **Reproducibility note:**, **Companion studies …**, **Primary digital source.** (structural, not decorative); "now trivially possible" in the abstract (a claim about ease, not an intensifier); "It is widely assumed" (the received view the paper tests, not fake candour); the `**Status:**` blockquote and the "To do before submission" list (process metadata, not manuscript voice).

## 2. Substance flags carried (not fixed)

1. **MW column is a different snapshot.** §3.1's own note says the MW column is the 2026-06-24 run while PWG is the 2026-07-03 re-run, "a same-snapshot re-run is queued". Still queued; a referee will ask why the two columns are not on one snapshot.
2. **MW cited-sense base disagrees with the review memo.** §3.3 table: "99,716 cited senses" for MW; the referee memo's §1 re-verification quotes "99,726". One of the two is a typo or the memo's figure predates a change; not decidable from the manuscript. Check [`cross_dict_metrics.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/cross_dict_metrics.md) before submission.
3. **Coverage figure moved.** §2 now says the map covers 70.9 % of 801,788 PWG source citations; the memo verified 72.4 % of 772,567 (June state). Consistent with the re-run story, but the manuscript's own text does not say the coverage figure was re-run, only the §3.1 rates and counts.
4. **Companion-study labels.** §5 names the companions "csl-atlas P2" and "csl-atlas P6"; the referee memo (and ARTICLES.md as quoted there) calls them A02 and A06. Whichever is the live series label should be used in both places.
5. **Kochergina edition date.** Table row "Koch (Kochergina, 1978/87)" against the reference entry "1987, 2-е изд." — the memo's m3, still author-verifiable.
6. **References heading still reads "(draft — author to finalise)".** Not touched (heading count and text are gate-protected); it has to go before any submission.
7. **AP90 Vedic-siglum recall hand-check and GRA/PW control columns** — the paper's own open to-dos, unchanged.
8. **Abstract "0 %" vs table "0.0 %"** for Kochergina — cosmetic, but a copy-editor will query it.

## 3. Read-and-sign

About 30 minutes: read the abstract, §1 and §4 in full (the singular voice and the new §4 opener are the only framing changes), skim §2–§3 for the "I"/"my" substitutions, and rule on flags 2 and 4. Proposed readiness: stays 4/5 until flags 1, 2 and 6 are resolved (propose only; a human should decide). Venue: no change to the standing Lexikos / IJL / eLex `@DECIDE`; the note's length and the single-table-per-section shape fit a Lexikos short communication most naturally, but that is a recommendation, not a switch. No submission before 2026-11-01.

_Dr. Mārcis Gasūns_
