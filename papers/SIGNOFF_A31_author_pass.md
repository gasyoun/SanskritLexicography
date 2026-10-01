# SIGNOFF A31 — author-voice pass

_Created: 06-09-2026 · Last updated: 06-09-2026_

## Scope

Manuscript: [A31_fifty_thousand_corrections_error_origin_typology.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A31_fifty_thousand_corrections_error_origin_typology.md) (Lexikos draft, A31/P5). Pass under handoff [H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md), executed 06-09-2026 by Fable 5.1 (`claude-fable-5-1`). Voice, register and framing only; no number, claim or citation altered; mechanical drift gate ([voice_drift_check.py](https://github.com/gasyoun/Uprava/blob/main/tools/voice_drift_check.py) against `origin/master`) CLEAN on numbers, URLs, DOIs, citations, IAST, Devanagari, heading count and table rows. The one line the gate had to be told to skip is the added byline (its ORCID URL and the author's own name are the only "new" tokens).

## 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Header | Byline block added below the dated header (`Mārcis Gasūns, independent scholar (ORCID …), gasyoun@ya.ru`); `Last updated` bumped to 06-09-2026 | Paper carried no author line; Lexikos needs one |
| 2 | Abstract, §1–§5, §8 (18 places) | `we` / `our` → `I` / `my` throughout | Single-author paper; Lexikos accepts first-person singular; the editorial "we" read as a committee |
| 3 | Abstract | Bold removed from `error-origin typology`, `evidence complementarity`, `single-collator campaign fingerprints`; the em-dash class list became a parenthesis | Journals strip markup from abstracts; bold-for-emphasis is a de-AI item |
| 4 | Abstract, first sentence | `quietly asserts` → `asserts` | `quietly` / `silently` occurred three times; kept the one in §6.1 that carries meaning |
| 5 | §1 para 1 | `fixes the text — but the error belonged` → `fixes the text, but the error belonged` | Em-dash used as a plain conjunction |
| 6 | §1 para 3 | `The answer turns out to hinge` → `The answer hinges` | `turns out` twice in one paragraph; the second (`turns out to be the single most valuable`) kept |
| 7 | §1 para 4 | `Our contributions: (i)…` → `The contribution of this paper is the origin axis itself, delivered in four parts: (i)…` | One explicit singular contribution statement; the four items untouched |
| 8 | §2, form era | `Crucially, the reporting user` → `The reporting user` | Filler intensifier |
| 9 | §5 | `editorial events wearing an error costume` → `editorial events recorded as error repairs` | Decorative metaphor |
| 10 | §5, last sentence | Two em-dash clauses split into a colon and a new sentence | Em-dash-as-copula run |
| 11 | §6.1 | Bold removed from `98.9 %` and `23.1 %`; two em-dashes → comma | Emphasis by bold in body text; the numbers carry themselves |
| 12 | §6.3 heading | `…is a collation campaign, not a background hum` → `…is a collation campaign` | "not X, it's Y" pattern plus a decorative metaphor; heading count unchanged |
| 13 | §6.3 | `signatures of **systematic … campaigns** — one careful proofreader … — not population estimates` → bold dropped, the aside in parentheses | Same em-dash/bold pattern |
| 14 | §8, first paragraph | `nor, it must be said plainly, for any axis` → `nor for any axis` | Fake-candour opener |
| 15 | §8, editorial paragraph | `— our sample suggests a few per cent —` → `(my sample suggests a few per cent)` | Em-dash aside → parenthesis |
| 16 | §9 | `a humble web form` → `a plain web form` | Epithet |
| 17 | Provenance blockquote | One line appended naming this pass and this signoff | Required pass ledger note; nowhere else |

Left alone on purpose: the remaining meaningful em-dashes (the abstract's `git history — positionally richer …`, §2 `— the CDSL interface links …`), `The split could hardly be sharper.` (§6.1, a real transition), `Read naïvely, Table 4 says …`, and every `not because X, but because Y` contrast that carries an argument (§6.3, §7.3, §9). British `digitisation` in prose against the code-style class label `digitization` is deliberate in the source and was not touched.

## 2. Substance flags carried (not fixed)

1. **§5 "All five classified errors"** — Table 2 has 1 + 2 + 3 = 6 classified errors (90 − 84 = 6). The prose says five and then lists three kinds. Either the count or the table needs reconciling against [a31_origin_validation_metrics.csv](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31/a31_origin_validation_metrics.csv).
2. **Abstract "0.5 %–46.9 %"** vs Table 4 minimum 0.6 % (WIL). The abstract range presumably comes from the full by-dictionary table (dictionaries below the ≥ 30 cut-off); say so or align the two.
3. **§6.3 "in every dictionary with a high print-source share, a single corrector contributed 94–100 %"** — PUI (13.4 % share) has a top-corrector share of 70.7 %, and the same paragraph counts PUI inside the "13–47 %" collation band. The 94–100 % statement holds only for the top five rows; the threshold for "high" should be named.
4. **Contributor counts**: §2 says 206 distinct submitters against 5 appliers (A15 figure); §3 says 208 named correctors after alias resolution (OBS-T figure). The two definitions differ; a one-clause reconciliation would forestall a referee query.
5. **§4.2 "an earlier text classifier … silently misclassified at least 7.1 %"** — no citation or link; a referee will ask where the 7.1 % comes from.
6. **§3 and §8, no-κ statements** are dated 17-07-2026; if the second annotator on [gold_sample.csv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/gold_sample.csv) has since landed, both paragraphs and Table 2's framing go stale together.
7. **§5 annotator of record is the drafting model** (Fable 5, `claude-fable-5`) — kept verbatim; a human should decide whether Lexikos will accept a model as sole annotator or whether the human pass must precede submission.
8. **References** are marked draft; Bryant et al. 2017, Gebru et al. 2021 and Wiegand 1998– lack page/volume detail, and the Afrikaans *opsomming* the venue requires is still owed.
9. **Title "Fifty Thousand"** against the corrected count 52,498 (and the stale 50,953 the paper itself retires in §3) — fine as a round title, but a human should confirm it is not read as the retired figure.

## 3. Read-and-sign

About 30 minutes: read the abstract, §1 last paragraph, §5 second paragraph and §6.3 in full; skim the rest for any `I` that reads wrong. Proposed readiness: 4/5 (propose only) — the voice is clean, but flags 1 and 3 are arithmetic mismatches a referee would catch, and flag 7 is a policy question. Venue: Lexikos remains the right fit (metalexicographic, practice-facing); no change recommended. Submission is frozen until 2026-11-01 regardless.

_Dr. Mārcis Gasūns_
