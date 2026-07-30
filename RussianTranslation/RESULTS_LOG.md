# RussianTranslation — results log

_Created: 09-07-2026 · Last updated: 30-07-2026_

Append-only, reverse-chronological. Each entry: date, context, model tier, table.

## 30-07-2026 — H1910: Jamison–Brereton 2014 as the fifth column, Renou EVP as a witness

Opus 5 1M (`claude-opus-5[1m]`),
[H1910](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1910-Opus_RussianTranslation_rv-jamison-brereton-renou-fifth-witness_29.07.26.md).
J–B extracted by [`src/rv_jamison_brereton_extract.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_jamison_brereton_extract.py)
from the archive.org OCR of all three print volumes (an INPUT, never committed); Renou joined
from the committed H1843 citation index by
[`src/rv_renou_evp_witness.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_renou_evp_witness.py).

### J–B coverage — the acceptance bar was Griffith's, not Geldner's

J–B translate the complete RV, so anything short of 10,552 with 0 unmatched means the parser
is wrong rather than the book incomplete (handoff requirement 4).

| Gate | Result |
|---|---:|
| Canonical loci covered | **10,552 / 10,552** |
| Unmatched loci | **0** |
| Duplicate loci | 0 |
| Loci outside the canonical set | 0 |
| Hymns short of their canonical stanza count | 0 |
| Hymn headings anchored from the OCR | 1,020 / 1,028 |
| Hymns resolved positionally (heading destroyed by OCR) | 8 |
| Commentary leaks (J–B introductions/notes inside a stanza) | **0** |
| Stanzas ending in page/running-head furniture | **0** |

### Text-quality controls, against the Griffith layer as an independent control

Griffith was extracted by a different script from a different source, so its rates are a
usable baseline rather than a self-comparison. Every defect below is one a locus count cannot
see — each held at 10,552/10,552 while it was present, which is the point.

| Measure | J–B 2014 | Griffith 1896 (control) |
|---|---:|---:|
| Stanzas | 10,552 | 10,552 |
| Characters of text | 1,937,825 | 1,618,483 |
| Median stanza length | 188 | — |
| Longest stanza | 454 | — |
| No terminal punctuation | 264 (2.50%) | 197 (1.87%) |

| Defect found during the run | Extent | Longest stanza |
|---|---:|---:|
| Next hymn's whole heading block swallowed (OCR-destroyed heading) | 8 hymns | 5,751 |
| `Mandala N` section introduction swallowed at a mandala boundary | 9 stanzas | 4,387 |
| Hymn-group introduction swallowed (no heading, no metre line) | 11 detected | 2,434 |
| Page number + running head embedded mid-text | 1,031 open-ended (9.77%) | — |
| Mangled running head glued to the last word (`V111.78`, `VI.43^4`) | 16 stanzas | — |
| **After the fixes** | **0** | **454** |

### Renou EVP as a locus-keyed witness — not a sixth column

EVP is a selective commentary, so a `translations` column would be mostly
`absent_from_source` and would corrupt `omitted_by_one`, whose meaning rests on absence being
meaningful.

| Measure | Value |
|---|---:|
| Renou mentions in the committed H1843 index | 2,213 |
| `locus_unresolved` (front matter / hymn-group intro) | 31 |
| Resolved onto a locus | 2,182 |
| — of those, carrying a quoted French fragment | 458 |
| **Distinct loci carrying a Renou witness** | **1,908** |
| Loci with at least one quoted fragment | 431 |
| Of the 100 sampled gate-sheet items, those at a Renou locus | 14 |

Per mandala (loci with a witness): 1:457 · 2:116 · 3:160 · 4:116 · 5:156 · 6:110 · 7:169 ·
8:122 · 9:223 · 10:279.

The 458 quoted figure sits one below H1843's measured 459 because one quoted mention is
`locus_unresolved` and so carries no locus. Neither reconciles to the H1843 spec's published
368 — H1843 logged that discrepancy rather than tuning to match, and this pass does not
re-open it.

### Scope impact of the fifth translator

| Quantity | Before (4 translators) | After (5) |
|---|---:|---:|
| Translator pairs (n choose 2) | 6 | **10** |
| Pairs decided deterministically by Geldner's gap | 3 of 6 | **4 of 10** |
| Flat TSV mirror rows | 659,032 | **823,790** |
| Flat TSV mirror size | 173.6 MB | **216.6 MB** (gitignored; 500-row sample committed) |
| Labels for a full typing run | 63,312 | **105,520** |
| Cost at the measured pilot rate ($1.06/12,000 labels) | ≈ $5.6 | **≈ $9.3** |

### One measured philological fact worth keeping

At **RV 10.106.5–8** — the four stanzas Geldner omits — J–B print *transliterated Vedic*,
not English: they decline to translate rather than skip. Those loci are therefore `present`
in the spine but are not an English rendering, and the divergence typer must not read them as
one. Pinned by `test_jb_untranslated_loci_are_present_not_absent`.

## 29-07-2026 — H1847: NWS tag vocabulary — in-card legend + faceted browse

Opus 5 1M (`claude-opus-5[1m]`),
[H1847](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1847-Opus_SanskritLexicography_nws-tag-vocabulary-facets_29.07.26.md).
Tag reach measured over the whole RU store (`src/pwg_ru_translated.jsonl` — local-only,
gitignored) with [`g5_card_render.card_tags`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/g5_card_render.py);
corpus figures from the committed census aggregate.

| Scope | Denominator | Carrying an NWS tag | Rate |
|---|---:|---:|---:|
| RU translation store | 11,603 rows | 255 | 2.20% |
| G5 batch1v3 sheet (150-card live slice) | 150 cards | 4 | 2.7% |
| NWS corpus (census denominator, for contrast) | 34,101 cards | 48,214 tagged senses | — |

Vocabulary actually present in our slice — the facet bar is built from this, the chip's
percentage from the corpus census:

| Slot | Distinct in store | Top values (store counts) |
|---|---:|---|
| diasystem | 10 | `Ved` 115 · `Śā` 67 · `Gen` 33 · `Buddh` 16 · `Reg` 8 |
| domain | 12 | `unsp` 170 · `Med` 34 · `Soc` 15 · `без уточн` 13 · `Ling` 12 |
| position | 2 | `ifc` 3 · `Bhvr` 1 |

Worktree sibling-path degradation — same command, same inputs, only the checkout differing
(FINDINGS §503; the left column is what would have reached the reviewer):

| Layer in the re-issued 150-card sheet | Built in a worktree | With `CSL_SIBLING_ROOT` set |
|---|---:|---:|
| `<ab>` spans with German/Russian expansion | 0 | 253 |
| unlinked-citation marks (needs `pwgbib`) | 1 | 8 |
| Cologne `<ls>` links (needs neither table) | 988 | 988 |
| NWS tag tooltips | 47 | 47 |
| facet chips / in-card tag panels | 8 / 4 | 8 / 4 |

Non-goals / caveats: the two store-side tag defects (17 half-translated tags, 1 malformed
bracket) are **reported, not repaired** — repair is store-side. Nine further `src/` modules still
carry the worktree-fragile sibling-root guess. The pinned re-issue proved 150/150 card digests
byte-identical, so votes already cast still bind. Findings: §503, §504.

## 29-07-2026 (later) — H1210 coverage fill (H1846): the A/B at 100 vs 100, and the metric flips the winner

Arm A's 13 unattempted cards run from the frozen payloads (Opus 5 1M `claude-opus-5[1m]`
session; workers Sonnet 5 `claude-sonnet-5`, controller resolved to `claude-opus-5[1m]` for
these 13 vs `claude-opus-4-8` for the original 87). Both arms now at **100/100 attempted**.
Report updated in place:
[H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md).

**The fill overturned the earlier conclusion — via the metric, not the new cards.**
`canonical_audit.py` scores `cards_out`, which holds the last attempt that *returned*, while
`final_status` records how the card *ended*; a card whose controller rejected attempt 1 and
whose attempt 2 died mid-stream ends `worker-null-death` yet still carries attempt 1's text
into the audit. So "audit-clean" includes cards the pipeline refused to ship — 21 in arm A,
8 in arm B.

| entry-length quartile | A audit-clean | B audit-clean | A shippable | B shippable |
|---|---:|---:|---:|---:|
| Q1 (28–176 B) | 22/22 (100%) | 21/22 (95%) | 22/22 (100%) | 21/22 (95%) |
| Q2 (180–526 B) | 23/23 (100%) | 21/23 (91%) | 23/23 (100%) | 21/23 (91%) |
| Q3 (670–4349 B) | 19/22 (86%) | 19/22 (86%) | 15/22 (68%) | 15/22 (68%) |
| Q4 (4553–11974 B) | 20/23 (87%) | 8/23 (35%) | **3/23 (13%)** | **4/23 (17%)** |
| no_pwg | 9/10 (90%) | 9/10 (90%) | 9/10 (90%) | 9/10 (90%) |
| **TOTAL** | **93/100** | **78/100** | **72/100** | **70/100** |

`shippable` = audit promote-DRY **and** the rig ended the card `clean-no-review` /
`clean-controller-approved`. On that metric the arms **tie (72 vs 70)** and Q4 **reverses**
(13% vs 17%): neither pipeline ships long entries unattended. The S2 defect-culprit stratum
shows it sharpest — arm A 13 audit-clean → **4** shippable (9 refused), arm B 3 → **2**.

**The earlier "length-routed hybrid" recommendation is withdrawn** — it rested on arm A's
93% vs 35% on Q4, which does not survive the pipeline metric. Two caveats bound the tie:
the 13 filled cards ran on a later controller tier, and **8 of them lost attempts to API
transport failures** (`stalled mid-stream` / `connection closed`), so arm A's Q4 13% is a
floor. Largest available lever is now the retry/transport layer (a null attempt consumes one
of three), not the generator.

## 29-07-2026 — H1210: DeepSeek vs Claude-native on 100 stratified PWG cards

Runs 28-07-2026, report 29-07-2026. Controller in **both** arms Opus 4.8
(`claude-opus-4-8`); arm-A workers Sonnet 5 (`claude-sonnet-5`); arm-B generator
`deepseek-chat`. Report, coverage audit and blind sheet: Opus 5 1M (`claude-opus-5[1m]`).
Full method, limitations and what the numbers do *not* support:
[pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1210/H1210_AB_DEEPSEEK_VS_CLAUDE_100CARD_2026-07-29.md).
Both arms promote-DRY; nothing entered the store.

**Read the coverage row before the clean rates.** Arm A completed 87 of 100 cards — three
size-bounded chunks never ran — and because chunks pack by BYTES the gap is a contiguous
band, not a random 13: 9 of the 13 fall in Q4, and **all ten S4 verb-root cards are missing**.
The two headline percentages are therefore *not* a head-to-head; the quartile table is.

| metric | arm A — Claude-native | arm B — DeepSeek + same controller |
|---|---|---|
| cards attempted | 87/100 (S4 verb roots: 0/10) | 100/100 |
| audit-clean % (canonical promote-DRY) | 95.4% (83/87) — not comparable, see above | 78.0% (78/100) |
| **Q1 28–176 B / Q2 180–526 B** | **100% (22/22) / 100% (22/22)** | **95% (21/22) / 91% (21/23)** |
| **Q3 670–4349 B / Q4 4553–11974 B** | **89% (17/19) / 93% (13/14)** | **86% (19/22) / 35% (8/23)** |
| defect-culprit stratum S2 | 11/12 | 3/15 |
| NULL-CARD / worker-null-death | 0 / 5 | 9 / 13 |
| calls per clean card (controller share) | 2.96 (38.2%) | 2.55 (25.1%) |
| escalated to review-sheet | 12 (13.8%) | 15 (15.0%) |
| generation USD → per clean card | n/a (subscription lane); 16.54 M subagent tokens | **$0.7255 → $0.0093** |
| wall clock | 9,625 s (median 114 s/card) | 1,255 s |

The two arms are a wash below ~4.5 kB and diverge sharply above it — a single averaged
percentage over a length-stratified sample is a weighted artifact of the selection rule, not
a quality delta. Arm B's $ figure is **generation only** (its controller runs on the same
subscription lane, uncosted), and the 7.7× wall-clock difference is lane latency (Workflow
agent harness vs a direct HTTP loop), not model latency.

Generator-independent findings from the same run: the rig's self-report **understates**
audited cleanliness in both arms (70 vs 83; 72 vs 78 — H1209 v1 saw it overstate, so the
canonical audit is the verdict either way), and the complexity trigger false-flags 77.8%
(A) / 63.2% (B) of the cards it escalates. Blind 40-item human vote (20/arm, unlabelled) is
generated and pending a reviewer; verdicts are the top quality layer and can still move the
conclusion.

## 26-07-2026 - H1681 follow-up: the compound-`differs` blind arm re-cut, deduped and BOUND

Executor: Opus 5 1M (`claude-opus-5[1m]`). MG ruled **re-cut** on the H1681 `@DECIDE`
(re-cut vs retro-lock). Generator
[`src/pilot/compound_differs_review_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/compound_differs_review_sample.py)
repaired on both counts and the sheet re-drawn from the same `seed=1628`.

| | before | after |
|---|---|---|
| frame sampled from | 4,226 rows (103 sharing a card id) | **4,123**, one per `(k1, hom)` card id |
| sample | 200 rows / **199** distinct ids | 200 rows / **200** distinct ids |
| binding | none — `validate_decisions.py` would reject the export | `sha256:31c106bb13cd2bad…`, lock committed, gate `G6-compound` |

**The duplicate card was the visible end of a queue-wide mismatch:** `headword_index.tsv`
carries one row per part-of-speech reading (`agraRI` as `adj.` and as `m.`; 2,383 of its
keys are multi-row), while a card id is only `(k1, hom)`. So the `differs` queue's 4,226
rows are **4,123 distinct cards**. The adjudication is unaffected — all 103 duplicate rows
agree with their twin on both members and verdict (0 disagreements), since a compound's
analysis does not depend on the entry's `lex`.

Arm coverage after the re-cut (200 cards): `same_split_pwg_lemma_form` 138 → max Wilson-95
lb 0.973, still the only stratum that can clear the 0.90 gate; `pwg_lexeme_vs_mw_suffixed_tail`
17 · `mw_cut_leaves_nonword` 11 · rest unchanged. **Promotion ceiling stays 3,018/4,226
(71.4 %)** — the second, rule-stratified arm remains [H1703](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1703-Opus_SanskritLexicography_compound-differs-second-arm-and-sheet-binding_26.07.26.md)
and is still sequenced behind [SanskritGrammar#527](https://github.com/gasyoun/SanskritGrammar/issues/527)
+ [#801](https://github.com/gasyoun/SanskritLexicography/issues/801).

The HTML stays gitignored; `generated` is pinned to `26-07-2026` so a regeneration
reproduces the exact bytes the lock binds. `csl_pyutil` is **0.4.0** here, not the 0.3.1
the H1404 manual records — the stamp anchors still matched.

## 26-07-2026 - H1681: all 4,226 PWG-vs-MW compound `differs` rows adjudicated by rule

Executor: Opus 5 1M (`claude-opus-5[1m]`), Claude Code. В2 arm of the H1664 triage. Full
method + limitations:
[research/PWG_COMPOUND_DIFFERS_AGENT_ADJUDICATION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_COMPOUND_DIFFERS_AGENT_ADJUDICATION.md);
verdicts:
[research/pwg_compound_differs_adjudication.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_compound_differs_adjudication.tsv).
**No store field changed; the 200-card blind arm was not touched.**

The queue is not "one dictionary is wrong": PWG's parenthesis states the compound's
members **as lexemes**, MW's `<k2>` is a **surface segmentation** — MW's members
concatenate back to the headword in 4,215/4,226 rows (99.7 %), PWG's in 81 (1.9 %).

| Verdict | rows | share | = sheet vote |
|---|---:|---:|---|
| `pwg_members-right` | 3,724 | 88.1 % | approve |
| `index_members-right` | 180 | 4.3 % | reject |
| `unresolved` | 322 | 7.6 % | defer |

20 rules, first-match-wins; the five largest: `same_split_pwg_lemma_form` 3,018 ·
`pwg_lexeme_vs_mw_suffixed_tail` 323 · `mw_cut_leaves_nonword` 277 ·
`cut_moved_both_readings_lexical` 253 (unresolved — both readings lexical) ·
`pwg_layer_no_headword_paren` 82.

**Four upstream defects found and worked around in memory (nothing rewritten):**

| Defect | In queue | Whole dataset |
|---|---:|---|
| `pwg_compound_split.py` takes the first `+`-chain with no bracket awareness — inner sub-analysis or a *different word's* parenthesis | 162 | 344/16,738 wrong chain (2.06 %) + 368 unverifiable (2.20 %) |
| `mw_compounds._clean_member` strips `;` and the space, fusing MW `<k2>` variants into one bogus member | 10 | 41/106,603 MW compound records (0.04 %) |
| transcription typos in PWG's own member strings (`sda` for *sūda*, `hasaM` for *haṃsa*) | 12 | csl-orig batch candidates, not swept further |
| the H1628 sheet has no lock/content-hash and a duplicate card (200 rows, 199 ids) | — | `validate_decisions.py` would reject the vote export |

**Promotion plan (gate: per-stratum Wilson-95 % lb ≥ 0.90, provenance `agent`, never
`human_reviewed`):** only `same_split_pwg_lemma_form` (3,018 rows, 140 arm cards, max lb
0.973) can clear the gate — **the 200 votes close 3,018 of 4,226 rows (71.4 %), not all
of them.** A stratum needs ≥ 35 arm cards at 100 % agreement to reach 0.90, and the H1628
sample was stratified by length × DCS frequency before these rule strata existed. The
remaining 1,208 rows need a second, rule-stratified arm of ~280 cards.

## 26-07-2026 - H1682: h1303_abbrev rule-collapse — 273 → 33 cards

Executor: Sonnet 5 (`claude-sonnet-5`),
[H1682](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1682-Sonnet_SanskritLexicography_h1303-abbrev-rule-collapse_26.07.26.md).
Full method + per-section table:
[H1682_ABBREV_RULE_COLLAPSE_REPORT_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1682_ABBREV_RULE_COLLAPSE_REPORT_2026-07-26.md);
100% classification: [H1682_ABBREV_RULE_COLLAPSE_CLASSIFICATION_2026-07-26.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1682_ABBREV_RULE_COLLAPSE_CLASSIFICATION_2026-07-26.tsv).

| | count |
|---|--:|
| ab-tokens classified (100%) | 269 |
| rule-bulk (folds into a section policy) | 252 |
| residue (classifier-flagged ambiguous) | 17 |
| Rule cards | 12 |
| Residue + ls-border + meta cards | 17 + 3 + 1 |
| **New sheet total** (`h1682_abbrev_rules`) | **33** |
| Old sheet (`h1303_abbrev`, superseded-unvoted) | 273 |

No token reclassified — every rule/residue label is re-grouped from
`build_h1303_abbrev_sheet.py`'s existing `O` overlay (H1303 Session 1,
21-07-2026) via its own 12 `# --- ...` section headers, parsed straight from
source (no hand-retyped token lists). Found + fixed in passing: the H1682
mandate's own "CONTRADICTIONS §7" (and `.ai_state.md`'s) is stale — renumbered
to §4 by H1364 (20-07-2026).

## 26-07-2026 - H1664: voting-queue triage — a verdict for every pending sheet, human bill recounted

Executor: Fable 5 (`claude-fable-5`),
[H1664](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1664-Fable_SanskritLexicography_voting-queue-agent-adjudication-triage_26.07.26.md).
Full verdict table (all 42 pending sheets org-wide, each with its enabling dataset):
[VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md §11](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md).

| Bucket | Sheets | Judgments now | Owed after routing |
|---|---|---|---|
| AGENT-RULEABLE | 1 (+2 zombie rows) | 17 | 0 |
| HYBRID (В2: agent adjudicates, human votes a blind stratified arm) | 20 | 2,282 | ~666 |
| HUMAN-ONLY | 21 | 663 | 663 |
| **Pending queue total** | **42** | **2,962** | **~1,329 (−55 %)** |
| acc_ncc lane (rerouted 26-07, executed; post-H1671 key repair the C/D set is 10,614) | 1 | 49,019 | 698 |

SL-specific outcomes: compound-`differs` goes В2 —
[H1681](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1681-Opus_SanskritLexicography_pwg-compound-differs-b2-full-queue-adjudication_26.07.26.md)
adjudicates all ~4,226 and the H1628 200-card sheet becomes the blind verification arm (same
200 votes then close the whole queue); h1303_abbrev collapses to rule-level cards
([H1682](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1682-Sonnet_SanskritLexicography_h1303-abbrev-rule-collapse_26.07.26.md),
273 → ~30); the 32 article-comparison edits get source-checked pre-vote
([H1683](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1683-Sonnet_SanskritLexicography_article-comparison-source-check_26.07.26.md));
h180 stays routed via H1650. HUMAN-ONLY (kept, with the why): G6 gold starter (the label is
the instrument), G5 batch1v3 (already the В2 human arm), h1306 style, Renou pilot 70,
Kochergina 4. The acc_ncc blind spot-check (698 rows post-H1671 re-draw; the pre-repair 686 sample was voided unvoted) is now registered in
[REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md)
the H1671 sequencing gate resolved itself the same day — the key repair merged ([PR #785](https://github.com/gasyoun/SanskritLexicography/pull/785)) and the fresh sample is safe to vote. HY "after" numbers
are planning estimates — exact arm sizes derive per stratum at execution
([PR #783](https://github.com/gasyoun/SanskritLexicography/pull/783) pattern).

## 26-07-2026 - H1628: stratified 200-item review sheet, PWG-vs-index compound `differs` (H1624 G6 residual)

Executor: Sonnet 5 (`claude-sonnet-5`). Sampled from the ~4226-row `differs` queue the
[H1624 G6](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1624-Opus_SanskritLexicography_pwg-german-layers-backlog-ordered_25.07.26.md)
`enrich_portrait_derivation.py --conflict-rate` flags (39539 rows scanned, 4226/39539 =
10.69% conflict, 10577/39539 = 26.75% needs_human — unchanged from G6's freeze). Sampling
script:
[`src/pilot/compound_differs_review_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/compound_differs_review_sample.py)
(`--selftest` wired; `--report` dry-runs the strata; `--write` emits the frame + sheet).

**Sample frame — two-stage stratified, seed=1628 (deterministic, reproducible):**

1. `vs_index_class` (how PWG's split disagrees with the pre-existing
   `headword_index.tsv` `compound_members`, not itself stratifiable since the whole
   queue is `compound_status=differs`): `member_count_diff` (76/4226, 1.8%) gets a flat
   **guaranteed quota of 20** — proportional allocation would round it to ~1-2 items and
   bury a structurally distinct failure mode; `same_count_diff_split` (4150/4226) fills
   the remaining 180 proportionally across length x frequency cells (largest-remainder
   rounding to land exactly on 180).
2. `length_bucket` (`len(k1)`): short ≤8 / medium 9-10 / long ≥11 (quartile-derived cuts
   on the full differs frame).
3. `freq_bucket` (DCS attestation count via
   [`src/pwg_freq_order.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_freq_order.tsv)):
   `no_dcs_freq` (no match, 58.1% of the frame) / low 1-2 / mid 3-9 / high ≥10.

| stratum | full differs frame (n=4226) | sample (n=200) |
|---|---:|---:|
| vs_index_class: member_count_diff | 76 (1.8%) | 20 (10.0%, oversampled by design) |
| vs_index_class: same_count_diff_split | 4150 (98.2%) | 180 (90.0%) |
| length: short(≤8) | 1904 (45.1%) | 83 (41.5%) |
| length: medium(9-10) | 1622 (38.4%) | 78 (39.0%) |
| length: long(≥11) | 700 (16.6%) | 39 (19.5%) |
| freq: no_dcs_freq | 2456 (58.1%) | 123 (61.5%) |
| freq: low(1-2) | 660 (15.6%) | 28 (14.0%) |
| freq: mid(3-9) | 503 (11.9%) | 22 (11.0%) |
| freq: high(≥10) | 607 (14.4%) | 27 (13.5%) |

Sample frame (metadata only — k1/hom/both splits/strata/panini/gaṇa, no `ru`/`de` store
text) committed at
[`review/sanskritlexicography-pwg-compound-differs_stratified200_frame.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/sanskritlexicography-pwg-compound-differs_stratified200_frame.tsv).
The interactive sheet itself
(`review/sanskritlexicography-pwg-compound-differs_stratified200_review.html`) stays
**gitignored**, per the `/review-sheet` contract — personal voting artifact, not a repo
deliverable.

**Vote → store contract (so `derivation.human_reviewed` never gets a bulk overwrite):**
`decisions.json` export carries one decision per `(k1, hom)` id — `approve` = PWG's split
is correct (a future apply step sets that entry's `derivation.compound.human_reviewed =
true` with `members` taken from `pwg_members`); `reject` = the index's split is correct
(same overlay, `members` taken from `index_members`, PWG layer flagged
`needs_correction`); `defer` = no vote, stays `needs_human`. The overlay write touches
**only the ~200 sampled `(k1, hom)` keys** — `enrich_portrait_derivation.enrich_portrait_obj`
already refuses to touch any entry whose `derivation.human_reviewed` is truthy, so applying
this batch cannot silently re-stamp the other ~4026 unsampled `differs` rows.

**Explicit non-goal:** the remaining ~4026 `differs` rows (4226 − 200) stay `needs_human`;
this sheet closes zero rows on its own until MG votes and `/decisions-apply` runs.

## 26-07-2026 - P1 ruling applied: machine-flag layer over the live queue, batch1v3 (H1655)

Executor: Fable 5 (`claude-fable-5`). MG ruled the voting-queue triage `@DECIDE` «auto-reject»
(screening-audit §7: machine-flagged cards never reach a human sheet). `machine_flags` (D1/D3/D4)
added to
[`review_residue_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_residue_gate.py);
batch1v2 superseded UNVOTED by `g5-live-queue-batch1v3-2026-07-26`.

| Metric | n |
|---|---:|
| queue rows | 11,163 |
| excluded: reader-visible German | 636 |
| excluded: machine flags D1/D3/D4 | 3,236 |
| ... D4 slot-count mismatch / D3 gloss-drift «…» / D1 Cyrillic in `{#…#}` | 3,067 / 370 / 20 |
| already decided | 5 |
| eligible for sheets | 7,286 (65.3%) |
| batch1v3 cards (0 leaks, both layers) | 150 |

D5 (gloss byte-identical to DE) deliberately not flagged — audit-measured ~false-positive.
Store-side repair of flagged rows: H1651 (queued, Sonnet).

## 26-07-2026 - H1631: edition-diff reading surface (N14 pilot) — subtype counts on the 7 REGLUE_SPEC pilot roots

Executor: Sonnet 5 (`claude-sonnet-5`). Fixture-driven static page +
[`src/pilot/build_edition_diff_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_edition_diff_site.py)
(`--selftest` wired into CI). Renders the PWG sense skeleton with PW/SCH/PWKVN/NWS
supplements attached at their `edition_rel` insertion point, each badged with its
subtype — the H1624 G4 classifier is the only typology used, no new classes invented.
Table below is a local `--out` run against the (gitignored, uncommitted) live store's
5-layer pilot keys from [`REGLUE_SPEC.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md) Sec.5 — counts only, no store text
published (N9).

| subtype | count (7 pilot roots, 1077 rows) |
|---|---|
| base | 433 |
| restate | 475 |
| pw_correct | 0 |
| sch_star | 11 |
| derived_sense | 3 |
| a2a | 13 |
| nws_at_sense | 111 |
| foreign_fragment | 31 |

Pilot roots: `gA`, `Cid`, `Sam`, `jIv`, `rakz`, `vraj`, `yat` (the 5-layer set). No
`pw_correct` (gender-conflict) instance among these 7 — consistent with REGLUE_SPEC's own
finding that PW mostly *restates* rather than corrects at this sample. N14 partial close:
demo covers PWG/PW/SCH/PWKVN/NWS badges for the pilot set; scaling to the full store,
per-sense visual grouping polish, and any editorial adjudication of `differs` cases are
explicitly out of scope (non-goals).

## 26-07-2026 - H1629 DE edition-graph export (OntoLex + TEI Lex-0) + three integrity findings

Executor: Opus 5 (`claude-opus-5[1m]`). New generator
[`src/export_de_edition.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_de_edition.py);
profile doc
[`DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md).

**Golden-fixture export** (22 DE-only rows → `release/fixture/de_edition/`, `--generated-at 2026-07-26`):

| entries | senses exported | quarantined | sanitized tags | government | form_notes | citation_edges | gloss_spans | edition_rel |
|---|---|---|---|---|---|---|---|---|
| 7 | 20 | 2 | 1 | 15 | 2 | 42 | 3 | 17 |

Edition-layer coverage in the fixture: `pwg` 3 · `pw` 6 · `sch` 3 · `pwkvn` 5 · `nws` 3.
Artifacts: `pwg_de_edition.ttl` 42 KB · `pwg_de_edition.tei.xml` 23 KB · manifest 1.4 KB.

**Finding 1 — Russian tokens inside the German `de` field.** 11 of 11,603 store rows
(0.09%). Verified against csl-orig: `huti` reads `{%Opfer%} in {#sarva˚#} **und**
{#havirhuti#}` upstream but `… **и** …` in the store (and the store row also dropped the
`(von 1. {#hu#})` etymology parenthesis).

| symptom | example row |
|---|---|
| `и` for `und` | `huti`: `{%Opfer%} in {#sarva˚#} и {#havirhuti#}` |
| `для` for `für` | `parihara`: `<ab>v. l.</ab> для {#parihAra#}` |
| `в` for `in` | `nI` desid-3: `<ls>VĀRĀHA-P.</ls> в <ls>Verz. d. Oxf. H. 59,a,3.</ls>` |
| `С` for `Mit` | `viS` 175: `<div n="p">— С {#anUpa#}` |
| `корригенда` | `DA` pw: `Mit <div n="p"> — корригенда` |
| **total rows with Cyrillic in `de`** | **11 / 11,603 (0.09%)** |

**Finding 2 — Russian prose in DE-side structural fields.** `sense_tag`: 110/11,603 rows
(0.95%), e.g. `c) с dat. лица и instr. предмета`. The `h` field likewise carries Russian
disambiguation prose (`PW 3 (с sam, о супружеском намерении)`). The export quarantines
`de`-contaminated rows, reduces a contaminated `sense_tag` to its ASCII skeleton, and drops
`h` from the allowlist entirely.

**Finding 3 — G1 `gloss_lang` classifier false positives.** Census over every `{%…%}` span
in the store's German text:

| lang | rule_id | spans | German-looking | FP rate |
|---|---|---|---|---|
| en | `english_content` | 153 | 117 | **76.5%** |
| la | `botany_binomial` | 68 | 5 | 7.4% |
| ambig | `homograph_ambig` | 8 | 0 | 0.0% |
| **total non-DE** | | **229** | **122** | **53.3%** |

Base: 15,901 spans scanned; 229 (1.44%) classified non-DE. Examples of misfires — all
unmistakably German: `bis an's Ziel bringen`, `an sich nehmen, empfangen, erlangen,
erhalten` (→ `en`); `Gelegenheit gefunden habend`, `Willens sein` (→ `la` botany binomial).
Because `pwg_mask.classify_pct_detail` marks `la`/`en` spans `translate: False`, these
German glosses are also masked out of the translate path upstream. "German-looking" is a
heuristic proxy (umlaut / German function word / `-en` verb ending), so the rate is ±;
the direction is not in doubt. **Not fixed here** — changing the classifier changes masking
behaviour pipeline-wide and needs its own measured A/B.
## 26-07-2026 - G5 batch1 decisions applied + reader-visible German gate over the live queue (H1655)

Executor: Fable 5 (`claude-fable-5`). Reviewer MG aborted batch 1 at 5/150 votes («Переделай
все» — German must be screened BEFORE a human sees a card). Votes applied through
`apply_decisions --gate G5` → `run_batch apply_review`; new
[`review_residue_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_residue_gate.py)
swept the queue; batch1v2 rebuilt gate-clean. Full audit:
[decisions_applied_2026-07-26_g5-batch1.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions_applied_2026-07-26_g5-batch1.md).

| Metric | n |
|---|---:|
| batch1 votes: approve / reject / unvoted (abort) | 3 / 2 / 145 |
| live queue rows swept | 11,163 |
| flagged: reader-visible German | 637 (5.7%) |
| ... hits by layer: prose (H1302 class b) / ls-tail `fg.` / German `ab` | 457 / 371 / 145 |
| clean rows eligible for sheets | 10,526 |
| batch1v2 cards (all verified German-free) | 150 |
| positional-id drift: votes initially unresolvable against grown store | 2/5 (fixed: suffix fallback + CI pin) |

## 26-07-2026 — H1630 top-N `citation_edges` sigla → Cologne scan/HTML link coverage

Executor: Sonnet 5 (`claude-sonnet-5`), isolated worktree. Script: `src/citation_edges.py`
(`topn` subcommand, new; `scan_href` field, new — H1624 G3 parent). Store: the live
11,603-row `pwg_ru_translated.jsonl` (gitignored, main-worktree canonical copy).

**What's new.** `extract_citation_edges()` gained an additive `scan_href` field —
`ls_resolver.generate_href('pwg', n_attr, raw_ls)` when it actually resolves a Cologne
scan/HTML target, else `null`. This is a *different* axis from the existing
`resolver_status` (map/bib/orphan): `resolver_status` only asks "is this siglum a known
work", not "does a clickable Cologne target exist for this exact locator" — e.g. `AK. 1`
is `map` (Amarakośa is a known work) but `scan_href` is `null` (the resolver pattern for
Amarakośa needs 3–4 coordinate parts, not one).

**Top-25 sigla by raw citation frequency → `scan_href` coverage:**

| siglum | citations | `scan_href` resolved | coverage | sample target |
|---|---:|---:|---:|---|
| MBH | 5,753 | 5,737 | 99.7% | [mbhcalc?1.1090](https://sanskrit-lexicon-scans.github.io/mbhcalc?1.1090) |
| ṚV | 3,705 | 3,697 | 99.8% | [rv01.100.html#rv01.100.05](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv01.100.html#rv01.100.05) |
| R | 3,126 | 3,123 | 99.9% | [ramayanaschl/?1,4,18](https://sanskrit-lexicon-scans.github.io/ramayanaschl/?1,4,18) |
| BHĀG. P | 2,167 | 2,152 | 99.3% | [bhagp_bom/app1/?10,19,13](https://sanskrit-lexicon-scans.github.io/bhagp_bom/app1/?10,19,13) |
| ŚAT. BR | 1,781 | 1,770 | 99.4% | [shatapathabr/app1?10,1,2,1](https://sanskrit-lexicon-scans.github.io/shatapathabr/app1?10,1,2,1) |
| M | 1,636 | 1,635 | 99.9% | [manu/index.html?2,109](https://sanskrit-lexicon-scans.github.io/manu/index.html?2,109) |
| KATHĀS | 1,472 | 1,472 | 100.0% | [kss/index.html?17,32](https://sanskrit-lexicon-scans.github.io/kss/index.html?17,32) |
| AV | 1,207 | 1,199 | 99.3% | [av09.005.html#av09.005.12](https://sanskrit-lexicon.github.io/avlinks/avhymns/av09.005.html#av09.005.12) |
| P (Pāṇini) | 1,049 | 1,034 | 98.6% | [sutraani/6/4/57](https://ashtadhyayi.com/sutraani/6/4/57) |
| Spr | 1,039 | 1,038 | 99.9% | [boesp1/app1/?1402](https://sanskrit-lexicon-scans.github.io/boesp1/app1/?1402) |
| HARIV | 905 | 902 | 99.7% | [hariv?3964](https://sanskrit-lexicon-scans.github.io/hariv?3964) |
| R. GORR | 671 | 671 | 100.0% | [ramayanagorr/?2,5,27](https://sanskrit-lexicon-scans.github.io/ramayanagorr/?2,5,27) |
| RAGH | 668 | 668 | 100.0% | [raghuvamsa/app1?12,52](https://sanskrit-lexicon-scans.github.io/raghuvamsa/app1?12,52) |
| PAÑCAT | 607 | 606 | 99.8% | [pantankose/app2?71,24](https://sanskrit-lexicon-scans.github.io/pantankose/app2?71,24) |
| VARĀH. BṚH. S | 576 | 555 | 96.4% | [brihatsam/app1?79,14](https://sanskrit-lexicon-scans.github.io/brihatsam/app1?79,14) |
| RĀJA-TAR | 575 | 575 | 100.0% | [rajatar/app1?5,424](https://sanskrit-lexicon-scans.github.io/rajatar/app1?5,424) |
| ŚĀK | 525 | 522 | 99.4% | [shakuntala/app1?62](https://sanskrit-lexicon-scans.github.io/shakuntala/app1?62) |
| BHAṬṬ | 460 | 431 | 93.7% | [bhattikavya/app1?2,28](https://sanskrit-lexicon-scans.github.io/bhattikavya/app1?2,28) |
| Spr. (II) | 450 | 450 | 100.0% | [boesp2/web1/boesp.html?7515](https://sanskrit-lexicon-scans.github.io/boesp2/web1/boesp.html?7515) |
| VOP | 428 | 404 | 94.4% | [mugdhabodha/app1?26,215](https://sanskrit-lexicon-scans.github.io/mugdhabodha/app1?26,215) |
| AIT. BR | 409 | 407 | 99.5% | [aitbr/app1?2,16](https://sanskrit-lexicon-scans.github.io/aitbr/app1?2,16) |
| TS | 394 | 390 | 99.0% | [taittiriyas/app1?6,6,11,5](https://sanskrit-lexicon-scans.github.io/taittiriyas/app1?6,6,11,5) |
| MĀRK. P | 367 | 367 | 100.0% | [markandeyapurana/app1?101,8](https://sanskrit-lexicon-scans.github.io/markandeyapurana/app1?101,8) |
| KĀTY. ŚR | 328 | 328 | 100.0% | [katyasr/app1?22,6,16](https://sanskrit-lexicon-scans.github.io/katyasr/app1?22,6,16) |
| HIT | 308 | 307 | 99.7% | [hitopadesha/app2?20,15](https://sanskrit-lexicon-scans.github.io/hitopadesha/app2?20,15) |

**Residual (top-25 sigla with ZERO `scan_href` hits): none.** Every one of the 25
highest-frequency works (33,251 of 41,115 total citations, 80.9%) already resolves to a
Cologne scan/HTML target for the overwhelming majority of its individual locators
(93.7%–100%); the small per-siglum shortfalls (BHAṬṬ 93.7%, VOP 94.4%, VARĀH. BṚH. S 96.4%)
are individual malformed/unusual coordinates, not missing targets — the pattern-driven
resolver already covers this frequency band essentially completely.

**Where the real gaps are (beyond top-25): genuinely-uncovered high-frequency works.**
`resolver_status == "orphan"` (siglum unknown to `ls_source_map`/`pwgbib` at all — a
different, stricter failure than a `scan_href` miss) ranked by occurrences with a numeric
locator (excludes non-coordinate labels like "ed. Bomb."/"ed. Calc." — edition/cross-ref
notes with no locus, never linkable per the existing `build_citation_index.py` convention):

| rank | siglum | citations | work |
|---:|---|---:|---|
| 1 | JĀTAKAM / Jātakam | 95 | Jātaka tales |
| 2 | MAHĀVY / Mahāvy | 32 | Mahāvyutpatti |
| 3 | VAJRACCH / Vajracch | 24 | Vajracchedikā |
| 4 | CAMPAKA | 20 | (Buddhist Skt. text) |
| 5 | Journ. of the Am | 19 | Journal of the American Oriental Society |
| 6 | S | 18 | (ambiguous single-letter siglum) |
| 7 | KĀRAṆḌ | 18 | Kāraṇḍavyūha |
| 8 | Divyāvad | 16 | Divyāvadāna |
| 9 | HARṢAC / Harṣac | 14 | Harṣacarita |
| 10 | Kir | 8 | Kirātārjunīya |
| 11 | Maitr. S | 8 | Maitrāyaṇī Saṃhitā |
| 12 | Kauṭ | 8 | Kauṭilīya (Arthaśāstra) |

These are almost entirely Buddhist-Sanskrit / less-common works with **no scan repository
in `sanskrit-lexicon-scans`** — matches the pre-existing note in `build_citation_index.py`
("coverage is target-limited, not resolver-limited"). Hard gaps (no Cologne target exists
to link to at all) — route through [`/cologne-link-target`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-link-target.md)
if/when digitization work is prioritized; not attempted here (N15 out of scope, per H1630).

Reproduce: `python src/citation_edges.py topn --n 25` (JSON; the store resolves via
`store_path.canonical_store`, so this also works unmodified from a linked worktree).
Selftest for `scan_href` + `topn_scan_coverage`: `python src/citation_edges.py --selftest`.

## 26-07-2026 - H858 c1 live gate: HEALTH_NOGO (rate_limit) - profile sweep now 3/3 NO-GO

Executor: Opus 5 (`claude-opus-5[1m]`). Third profile gated for the same owed H858 window.

| Profile | UTC | Calls | Latency | Blocker |
|---|---|---|---|---|
| c4 | 25-07 16:02Z, 18:18Z | warm-up `rate_limit`, measured never ran | 17.9 s / 19.9 s - fine | quota |
| c5 | 25-07 18:56Z | warm-up + measured both `success` | 59.7 s / 53.0 s - ~2x ceiling | route latency |
| c1 | 26-07 02:37Z | warm-up `rate_limit`, measured never ran | 6.4 s - fine | quota |

c1: warm-up 6 424 ms `rate_limit`, measured never ran, wall clock 6.4 s. Same class as c4,
fastest rejection of the three.

**Two things this sweep establishes.** (1) The blockers are orthogonal - two profiles have
latency headroom but no quota, one has quota but no speed - so profile-swapping does not
unblock the window, it only changes which NO-GO you get. (2) **The wait is not "until
tomorrow":** c1 was probed at 02:37Z on a FRESH UTC day and still returned `rate_limit`, so
the binding cap does not reset at the date boundary. A future session must re-probe and read
the answer rather than assume a date change cleared anything.

No canary, no window, nothing promoted. Per-account evidence:
`src/pilot/output/h963_<account>_gate0_probe_events.jsonl`.

## 25-07-2026 — medium50 “all without --max-agents”: LIVE STOP (auth 403) + offline prep

Executor: Grok 4.5 · intent: fresh live-gate then **all five** medium50 windows
(`h1447-m50-w1…w5`, 48 keys) headless with **no** production `--max-agents`.

### Live gate (paid) — mechanical NO-GO

| profile | config_dir | health | detail |
|---|---|---|---|
| **c4** | `D:\ClaudeTools\profiles\claude4\.claude` | **NO-GO** | `h963_c4_gate0_probe`: warmup **auth**; events also show rate_limit/auth; measured history 168s ceiling breach |
| **c2** | `D:\ClaudeTools\profiles\claude2\.claude` | **NO-GO** | warmup **auth** 7358 ms |
| c1 / c4 / c5 / default | same stack | **403** | direct `claude -p` → `Failed to authenticate. API Error: 403 Request not allowed` for default, sonnet, opus, `claude-sonnet-5` |

**Stop reason:** `HEALTH_NOGO` / org-wide CLI **403** — no canary, no production calls, no store write.
Probe log rows: `gate0-c4-fresh-2026-07-25`, `gate0-c2-fresh-2026-07-25`.

**Human unblock:** re-auth / fix Max org permission so `claude -p` succeeds on a roster profile, then re-run live-gate.

### Offline prep completed (ready when GO returns)

| artifact | n |
|---|---:|
| merged 5-layer inputs (`_pilot_gen_merged`) | 48 keys |
| bare-key input aliases for `gen_opt_harness2.input_paths` | 48 |
| execution_manifest.v2 + harness per window | **5** (`w1` 3 keys agent_exp=3; `w2` 12→20; `w3` 11→14; `w4` 11→12; `w5` 11→12) |
| manifest `max_translate_agents` (no CLI max-agents) | 19 / 34 / 31 / 34 / 40 |

Resume recipe (gitignored output tree):
`src/pilot/output/MEDIUM50_NO_MAX_AGENTS_RESUME_2026-07-25.md` — headless lines
**omit** `--max-agents` on multi-key windows; canary alone may use `--max-agents 1`.

## 25-07-2026 - H858 c5 live gate: HEALTH_NOGO (latency ~2x ceiling) - orthogonal to c4

Executor: Opus 5 (`claude-opus-5[1m]`). First gate ever run on c5, after two c4 attempts the
same day returned HEALTH_NOGO on `rate_limit`. Packet:
[`pwg_ru/h858/H858_C5_LIVE_GATE_HEALTH_NOGO_2026-07-25.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h858/H858_C5_LIVE_GATE_HEALTH_NOGO_2026-07-25.md).

| Reading | Elapsed | Classification | Verdict input |
|---|---|---|---|
| warm-up | 59 651 ms | `success` | >= 30 000 ms ceiling -> FAIL |
| measured | 52 960 ms | `success` | >= 30 000 ms ceiling -> FAIL |

Both calls SUCCEEDED with real output and zero connection errors - this is not quota, not
auth. Wall clock 112.6 s for the pair.

### The finding: c4 and c5 fail for ORTHOGONAL reasons

| Profile | Calls | Latency | Blocker |
|---|---|---|---|
| c4 (16:02Z, 18:18Z) | warm-up `rate_limit`, measured never ran | 17.9 s / 19.9 s - fine | quota / account state |
| c5 (18:56Z) | warm-up + measured both `success` | 59.7 s / 53.0 s - ~2x ceiling | route latency |

Neither is a code defect and they share no cause: c4 has headroom but no quota, c5 has
quota but no speed. **Swapping profiles does not unblock the window** - it trades one
NO-GO for a different one. c5's numbers sit in the degradation band tracked since mid-July
(H963 104 870 ms; H1110 98 625 ms) and match H898's size-independent route-jitter finding:
the identical 6 828 B prompt read 16 621 ms on c4 at the 22-07 LIVE_GO.

Operational note: c5 is the profile this session runs on - a paid window there competes
with interactive sessions for the same quota, independent of today's latency verdict.

## 25-07-2026 - H858 c4 live gate: HEALTH_NOGO (rate_limit), no window opened

Executor: Opus 5 (`claude-opus-5[1m]`). `/pwg-live-gate c4`, one attempt, no reroll.
Packet: [`pwg_ru/h858/H858_C4_LIVE_GATE_HEALTH_NOGO_2026-07-25.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h858/H858_C4_LIVE_GATE_HEALTH_NOGO_2026-07-25.md).

| Reading | Elapsed | Classification | Verdict input |
|---|---|---|---|
| warm-up | 17 878 ms | `rate_limit` | fail-closed -> STOP |
| measured | - | never ran | - |

`gate_reason = HEALTH_NOGO` -> `verdict = NO-GO`. **Not a latency block** (17.9 s is well
inside the 30 000 ms ceiling) - c4 is rate-limited. No canary, no bounded window, nothing
promoted; one paid warm-up call was spent. The H858 Part B validation window stays owed.

c4 has produced no clean pair since 23-07: `rate_limit` x2 on 24-07, `auth` x2 earlier on
25-07, `rate_limit` today.

### Attempt 2 (18:18Z, through the fixed probe v1.63.0)

| Reading | Elapsed | Classification | Verdict input |
|---|---|---|---|
| warm-up | 19 903 ms | `rate_limit` | fail-closed -> STOP |
| measured | - | never ran | - |

Same `HEALTH_NOGO`. c4's rate-limit window has not reset: three `rate_limit` readings now
span 24-07 -> 25-07 18:18Z with two `auth` between, and latency is fine in every one
(9.9-19.9 s, all far inside the 30 000 ms ceiling). Quota/account state, not code or route -
further probing today is spend without information.

First live proof of the #729 fix: RAW READINGS printed ONE row (this run's, under a
per-invocation run id) and the NO-GO reasons name this run's own absent measured reading.
The old constant `RUN_ID` would have re-read all 10 historical rows and cited the 23-07
168 352 ms again.

### Probe defect found by this run (integrity)

| Defect | Impact | Tracking |
|---|---|---|
| `h963_c4_gate0_probe.py` hardcodes `RUN_ID`, then filters the append-only log by it and keeps the last row per purpose - so every run re-reads the whole history and can pair today's warm-up with a **stale** `measured` | today it only mis-stated a NO-GO reason (cited a 23-07 reading of 168 352 ms for a call never made). The inverse is the hazard: a stale passing `measured` + a passing warm-up prints `GATE-0 VERDICT: PASS`, which Step 3 turns into `LIVE_GO` and authorizes paid spend off a two-day-old number | [#729](https://github.com/gasyoun/SanskritLexicography/issues/729) |

## 25-07-2026 - H858 Part B: german-anchor repair — offline verification (NO paid run)

Executor: Opus 5 (`claude-opus-5`). Isolated worktree off `origin/master` @ `f96361ca`.
**Scope honesty: these are OFFLINE gates only.** The handoff's own validation — a bounded
no_pwg window showing the `{#…#}`-drop null class eliminated — is a PAID run and was NOT
performed: it needs a fresh live-gate GO, and the last c2/c4 readings were NOGO/rate-limited.
The live answer will come from `summary.german_anchor_repairs` on the first window that runs.

### Gates run

| Gate | Lane | Result |
|---|---|---|
| `german_anchor.selftest()` | Python (authored source) | 8/8 OK |
| `german_anchor_test.js` vs a REAL generated harness | JS (interpolated twin) | 21/21 PASS |
| `headless_worker_selftest.py` (incl. the new H858 test) | Python production route | PASS |
| `window_selftest.py` | both | **185/185**, 0 failed |
| `promote_final_cards.py --selftest` | store provenance | PASS |
| `lang_parity_check.py` | ledger | 82 entries, no drift, coverage complete |

### Behaviour pinned (both lanes, identical fixtures)

| Case | Before | After |
|---|---|---|
| headword `{#…#}` dropped from the echo (`{# 0/1`) | card NULLED, requeue reproduces it | repaired at sense head, stamped, promoted |
| mid-card span dropped (`1/2`, `1/3`) | card NULLED | re-injected at its nearest surviving neighbour |
| span dropped in a multi-sense card | card NULLED | lands in the correct sense (nearest-neighbour, not always-after) |
| echo faithful | accepted | accepted, **byte-identical, unstamped** |
| echo duplicates / fabricates / reorders a span | rejected | rejected, reason recorded (`german-anchor duplicate-token`, …) |
| german repaired but TARGET field dropped the span | `translation-fidelity-reject` | `translation-fidelity-reject` (unchanged — no laundering) |

### Integrity defect found in passing (pre-existing, unrelated to H858)

| File | Defect | Fix |
|---|---|---|
| `src/pilot/window_selftest.py` (coordinator-requeue test) | ran a real `--defect` requeue without `--no-residual`, appending a junk `{"key": "a"}` row to the tracked `no_pwg_residuals.jsonl` on EVERY suite run — the registry that decides which keys are BLOCKED from requeue | `--no-residual` added; polluting row reverted; the test's own assertions unaffected |

## 25-07-2026 - H1624 DH follow-up batch minted (H1626–H1635)

Executor: Grok 4.5. Mint-only (no execution). Parent: H1624 German layers closed G1–G6.

| ID | Priority | Topic | Status |
|---|---|---|---|
| H1626 | P0 | H1303 abbrev apply | ⏸ vote |
| H1627 | P0 | H1306 style / G5 | ⏸ vote |
| H1628 | P1 | compound differs sheet | QUEUED |
| H1629 | P2 | OntoLex/TEI DE graph | QUEUED |
| H1630 | P3 | citation top-N scans | QUEUED |
| H1631 | P4 | edition-diff UI | QUEUED |
| H1632 | P5 | sense–DCS pilot | QUEUED |
| H1633 | P7 | gold cut + methods | QUEUED |
| H1634 | docs | editorial principles | QUEUED |
| H1635 | FAIR | Zenodo public sidecars | QUEUED (rights) |

G7: existing H1333 (XLS-gated). Spec: Uprava/handoffs/_batch_h1624_dh_followups.tsv.

## 25-07-2026 - H1624 G6: compound conflict flags + G5/G7 blockers

Executor: Grok 4.5.

### G6 conflict rate (pwg_derivation_layer.tsv)

| metric | n | pct |
|---|---:|---:|
| rows | 39539 | 100 |
| conflict (differs) | 4226 | 10.69 |
| needs_human (differs+index-only) | 10577 | 26.75 |
| agrees | 6180 | — |
| pwg-new-fill | 6386 | — |

Never auto-adjudicates differs — future /review-sheet sample.

### G5 blocked
Awaiting pwg_ru/eval/h1306_style.decisions.json (sheet exists; vote not exported).

### G7 blocked
Palsule XLS not present; delegate H1333 when XLS lands.

## 25-07-2026 - H1624 G4: edition_rel on DE subcards

Executor: Grok 4.5.
Structured edition relationship flags on each sense (no DE rewrite).

| subtype | typical layer |
|---|---|
| base | pwg |
| restate | pw |
| pw_correct | pw (gender conflict) |
| sch_star / derived_sense | sch |
| a2a / derived_sense | pwkvn |
| nws_at_sense / foreign_fragment | nws |

Selftest: python src/edition_rel.py --selftest; promote stamp.

## 25-07-2026 - H1624 G3: citation_edges normalized DE <ls> graph

Executor: Grok 4.5 - offline.
Additive per-sense edges; raw <ls> not stripped.

| resolver_status | meaning |
|---|---|
| map | hit in ls_source_map (renou I-V) |
| bib | pwgbib expansion only |
| orphan | neither |
| empty | unparseable |

Selftest: python src/citation_edges.py --selftest; promote stamp; annotate --selftest.
Coverage CLI: python src/citation_edges.py report

## 25-07-2026 - H1624 form_notes: dedicated Nom/Voc field

Executor: Grok 4.5.
orm_notes = first-class field for nominative/vocative citation-form markers only.

| field | covers |
|---|---|
| government | acc loc instr gen dat abl |
| form_labels | number, gender, case_form, voice |
| form_notes | nom, voc only ({case, kind, span}) |

Selftest: form_labels --selftest; promote stamps form_notes.

## 25-07-2026 - H1624 form_labels: number / gender / nom-voc / voice on DE senses

Executor: Grok 4.5 - offline.
Sibling of government (Rektion). Acc/Loc/Instr/Gen/Dat/Abl stay in government;
form notes go to form_labels.

| axis | values | sources |
|---|---|---|
| number | sg, du, pl | ab sg./du./pl. (paren or bare) |
| gender | m, f, n, m.n, ... | lex primary; masc./fem./neutr. ab |
| case_form | nom, voc | parenthetical form notes (not Rektion) |
| voice | act, med, pass | ab med./act./pass. |

Not gender: bare ab n. (ambiguous with note). Not form_labels: Rektion cases.

Selftest: python src/form_labels.py --selftest; promote + microstructure stamp.
LANG_PARITY SHARED form_labels_number_gender_voice_h1624.

## 25-07-2026 - H1624 G2: government on every DE sense (promote + portrait)

Executor: Grok 4.5 · offline · no paid window.
Closes the gap where structured Rektion only appeared after a separate
nnotate_government backfill. Schema shape unchanged (array of hit dicts, D4/H338).

| path | producer | notes |
|---|---|---|
| store row on promote | promote_final_cards.rows_for + xtract_government(de) | always stamped (empty list if none) |
| store retrofit | nnotate_government.py | existing rows / drift repair |
| portrait sense at gen | microstructure.sense_node | from full DE segment |
| portrait backfill | nrich_portrait_government.py | older local portraits |
| retrieval surface | government.html via uild_article_site | still re-extracts from de_raw; floor banner |

Selftests: government_census selftest, nnotate_government --selftest,
promote_final_cards --selftest (PW (Instr.)), nrich_portrait_government --selftest,
uild_article_site --selftest. LANG_PARITY SHARED government_on_promote_and_portrait_h1624_g2.

## 25-07-2026 - H1624 G1: per-span gloss_lang on {%...%} (DE|LA|EN)

Executor: Grok 4.5 (session override; handoff pinned Opus 4.8) · offline · no paid window.
Artifact: [src/pwg_mask.py](src/pwg_mask.py) classify_pct_detail / gloss_lang_spans; residue shares classifier via [prompt_rule_audit.py](src/pilot/prompt_rule_audit.py); LANG_PARITY SHARED gloss_lang_spans_h1624_g1.

| vector | expect | rule_id | mask |
|---|---|---|---|
| {%das Nichthandeln%} | de | default_de | inline |
| das lat. {%ignis%} / <ab>lat.</ab> {%ignis%} | la | latin_cue | {Tn} |
| {%De accentu comp.%} | la | latin_phrase | {Tn} |
| {%Trapa bispinosa%} | la | botany_binomial | {Tn} |
| WILS. ... durch {%leaving, abandoning%} | en | wilson_en | {Tn} |
| {%terrestrial latitude%}, WILS. | en | wilson_en | {Tn} |
| WILS. ... {%Honig%} | de | default_de | inline |
| {%Name eines Baumes%} | de | default_de | inline (not binomial) |

Selftest: python src/pwg_mask.py --selftest · window_selftest.test_pwg_mask_gloss_lang_g1 · lang_parity_check green.

## 24-07-2026 — c2 medium50 w1 forensics: only-b0 / all-nulls = `--max-agents 1` starvation

Executor: Grok 4.5 (session) · gen model: Sonnet 5 (`claude-sonnet-5`) · profile: **c2 Pro**
(not Max) · keys: `nakzatra` / `sarvatra` / `sakft` · artifacts under
`src/pilot/output/c2_m50_w1*` (gitignored). Ledger:
[`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) id `C2_M50_W1_MAX_AGENTS1_2026-07-24`.

| run | config | `--max-agents` | ok/null | attempts seen | translate/heal spent | budget_stops | cost USD | terminal |
|---|---|---:|---|---|---|---:|---:|---|
| full w1 | c2 full profile | **1** | 0/3 | **b0 only** (success 161.8s) | 1 / 0 | **24** | 0.599 | all errors `selfheal-nothing-resolved` |
| stripped w1 | c2-stripped (H1517) | **1** | 0/3 | **b0 only** (timeout 180.3s) | 1 / 0 | **23** | 0.000 | same error stamp |
| fix w1 | c2 full profile | **omit** (manifest 19/41) | aborted | b0 timeout + **many** `heal:nakzatra#g*` + b1 | multi-spawn | n/a (HardFailure) | partial (~0.50+ on last call) | **`rate_limit`** session limit; resets 15:30 Europe/Moscow |

**Root cause (operator/process, not Pro-host):** `--max-agents N` caps **total** model
spawns (translate+heal) for the whole run. `N=1` spends the budget on the first batch;
remaining work refuses as `budget_exceeded` without spawning; `self_heal` overwrites notes
with `selfheal-nothing-resolved`. Smoking gun triad: `budget_stops ≫ 0` +
`translate_agents_spent=1` + single `b0` in `headless_attempts`.

**Guardrail:** do not copy `--max-agents 1` from single-key canaries onto multi-key windows.
**Separate residual:** c2 Pro session limit blocked the fix-run before a clean 3/3; re-run
after reset without the flag.

## 20-07-2026 — Sa→Ru gloss layer, wave 4: read-only TM lookup wired (H1349 W4 — H1349 COMPLETE)

Downstream wave: [`src/saru_gloss_tm.py`](src/saru_gloss_tm.py) `GlossTM` exposes the lemma +
root gloss layers as a **read-only** lookup for the pwg_ru/mw_ru card path — given a Sanskrit
lemma/root (SLP1) it returns ranked candidate Russian renderings. Additive consumer only; it
does not touch `pilot/translation_memory.py`, the store, or anything the safety-plan PRs
#547/#550 touch (the wave-4 risk fence). Smoke test on the published `SanskritRussian` data:

| query | layer | top candidates |
|---|---|---|
| `gam` (prefer root) | root | пришел (196) · отправился (177) · ушел (141) · пришли (100) |
| `karman` | lemma | действия (240) · деяния (186) · действие … |

Fixture-backed regression test (`tests/test_saru_gloss_tm.py`, 6 cases) wired into CI;
PROJECT_INTERLINKS glossary downstream row flipped planned→wired. **This closes H1349** —
waves 1 (defect fixes) + 2 (measured 85% precision) shipped; wave 3 (coverage) a measured
NO-GO (DEAD_ENDS §11); wave 4 (this) wires the read-only consumer.

## 20-07-2026 — Sa→Ru gloss layer, wave-3 coverage spike: vidyut-cheda NO-GO (H1349 W3)

Tried recovering the 78,842 unresolved forms via `vidyut.cheda` compound segmentation
(D7 reuse). **Measured NO-GO.** A strict gate (≥2 tokens + every member glossable,
[`src/build_compound_split.py`](src/build_compound_split.py)) recovers 28,673 forms (36.4% of
unresolved / 55,008 tokens) — but a 2-judge panel (Opus 4.8 `claude-opus-4-8` + Sonnet 5
`claude-sonnet-5`) on 40 gated recoveries scored segmentation **28% both-correct / 72%
either-wrong**, gloss **18% both-correct / 60% either-wrong / 40% acceptable**. Against the
wave-2 baseline (85.3% gloss) that is a catastrophic regression — ~half the recoveries are
outright wrong. Root cause: vidyut-cheda is a *running-text* segmenter; on isolated OOV forms
it shatters inflected/dual/plural words into stem + spurious glossable particle (`sahadevaśca`
→ `sahadeva`+`ca`, head "и"). **Decision: not wired in** — the 85% layer stays unregressed;
the 78,842 stay an honest coverage gap. Recommended path (backlog): the DharmaMitra **neural**
segmenter over the aligned *verse text*, which kosha's `compare_sandhi_methods.py` already
benchmarked as near-perfect and far above vidyut-cheda. Full write-up:
[`gold/saru_gloss_wave3_cheda_coverage.md`](gold/saru_gloss_wave3_cheda_coverage.md).

## 20-07-2026 — Sa→Ru gloss layer, measured precision (H1349 wave 2)

First **accuracy** measurement of the gloss layer (every prior number was coverage).
**Model-vs-model LLM panel, NOT human gold** (org gold-provenance rule): 3 judges
(Opus 4.8 `claude-opus-4-8`, Sonnet 5 `claude-sonnet-5`, Haiku 4.5 `claude-haiku-4-5`)
independently labelled a **tier × frequency stratified** sample of 110 resolutions on two
axes (lemmatization, gloss — D6); 9 split/correct-vs-wrong disagreements adversarially
adjudicated by a 4th model (Fable 5 `claude-fable-5`). Sampler + aggregator
[`src/saru_gloss_sample.py`](src/saru_gloss_sample.py) / [`src/saru_gloss_aggregate.py`](src/saru_gloss_aggregate.py);
full report [`gold/saru_gloss_precision_report.md`](gold/saru_gloss_precision_report.md).
Wilson 95% CI; "unsure" excluded from the denominator.

| axis | precision | 95% CI | note |
|---|--:|--:|---|
| lemmatization (overall) | **86.1%** | 78.3–91.4 | correct 93 · wrong 15 · unsure 2 |
| gloss (overall) | **85.3%** | 77.5–90.8 | ≈ the 84.4% upstream pair-precision ceiling; good+partial 97.2% |

| tier | lemma prec | gloss prec |
|---|--:|--:|
| dcs (n=40) | 94.9% | 87.5% |
| **vidyut (n=40)** | **71.8%** | 79.5% |
| marker (n=30) | 93.3% | 90.0% |

The **vidyut** tier is the lemmatization weak spot. Panel + verify converged on three
systematic, actionable defect classes (wave-3 targets): (1) ṛ/ṝ root-vowel length collapsed
to short (`kiranto`→√kṛ not √kṝ); (2) derived nominals lemmatized to a bare verbal root
(`janitṛ`→jan, `liṅgin`→liṅg); (3) compound tokens lemmatized to their final member only
(`anartha-trivarga`→trivarga). A human spot-check of the frozen sample is queued as a GTD @DO.

## 20-07-2026 — Sa→Ru gloss layer, wave-1 defect fixes (H1349 W1.1–W1.3)

Three pipeline-defect fixes in the Sa→Ru gloss layer, measured before/after over
one regenerated two-pass bootstrap (DCS `dcs_full.sqlite` 5.69M tokens + vidyut
kosha 0.4.0 + `surface_glossary.jsonl`). Fixes + measurement Opus 4.8
(`claude-opus-4-8`);
[`src/measure_wave1_delta.py`](src/measure_wave1_delta.py) replays the OLD and NEW
rule over identical inputs so each row isolates the code change alone. Regressions
pinned by [`tests/test_saru_gloss_pipeline.py`](tests/test_saru_gloss_pipeline.py)
(7 passing).

| Defect | Before | After | Note |
|---|--:|--:|---|
| W1.1 distinct root keys in lemma→root map | 3,570 | 3,147 | 434 self-mapped pseudo-root rows split out to `dcs_lemma2root_unresolved.tsv` (net −423 distinct keys); `root_glossary` layer now 1,853 roots |
| W1.2 homograph alternate rows | 9,521 | 11,289 | +1,768 rows; the old code inspected only `cands[1]`, so a genuine 3rd+ homograph was dropped — now the full trail over 9,733 forms |
| W1.3 vidyut ambiguity rows recorded | 0 | 5,952 | `stats['ambiguous']` was a bare counter (4,133 forms); now a `vidyut_ambiguity.tsv` competitor trail mirroring the DCS schema |

Two-pass bootstrap outcome (regen, fixed pipeline): 40,370 lemmas / 1,853 roots;
surface-form resolution 43.6 % (DCS) → 58.7 % (+vidyut +marker). The published
`SanskritRussian` data (still showing 2,021 roots) is **not** regenerated here —
D8 fences republish behind a human GO; a wave-2-gated republish will drop the root
count to ~1,853. Accuracy of these glosses is still unmeasured (coverage ≠
accuracy — wave 2 publishes a per-tier precision figure).

## 12-07-2026 — E2 sense-genre vs DCS attestation (H833 / H350 backlog #3)

Does per-sense citation-genre predict DCS corpus attestation better than the
lemma's aggregate genre? Analysis Opus 4.8 (`claude-opus-4-8`);
[`research/analyze_sense_genre_attestation.py`](research/analyze_sense_genre_attestation.py),
full write-up [`research/SENSE_GENRE_ATTESTATION_FINDINGS.md`](research/SENSE_GENRE_ATTESTATION_FINDINGS.md).
n = 1316 headword lemmas (grouped by normalised IAST, **not** `key1`=root),
49.8% DCS-attested. 5-fold stratified CV AUC (out-of-fold):

| Model | Features | AUC |
|---|---|---:|
| 0 | size only (n_senses, citation mass) | 0.700 |
| A | 0 + lemma union coarse-genre | 0.716 |
| B | 0 + sense-resolution genre | 0.710 |
| A+B | 0 + both | 0.714 |

ΔAUC(B−A) = **−0.006**, 95% bootstrap CI [−0.020, +0.009] → **thesis not
supported**: sense-resolution adds no separable signal over the lemma aggregate
at this scale. Attestation is driven by citation *volume* (genre adds ~+0.016);
per-genre, a *pure* sense in kāvya/purāṇa/kośa/śāstra raises attestation odds
(OR 2.2–3.5, CI>1) but Vedic-only senses do not (OR 1.06) — antiquarian signal.

## 09-07-2026 — pwg_ru medium50 relaunch (H437, post-classifier-unblock)

Windows `h317_w1b`/`w2a`/`w2b` relaunched solo (1-wide) after
[H428](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H428-Sonnet_RussianTranslation_opt2-schema-slim-classifier-unblock_09.07.26.md)
slimmed the opt2 schema. Orchestrator Opus 4.8 (`claude-opus-4-8`); generation
Sonnet 5 (`claude-sonnet-5`, harness-pinned). Full account +
n=50 tally: [`MEASUREMENT_2026-07-08_H317.md`](MEASUREMENT_2026-07-08_H317.md)
(H437 section). Finding: classifier unblocked (agents ran, 0 connection errors),
but every window tripped its `MAX_AGENTS` budget-kill-switch via the self-heal
cascade — the kill-gate miscalibration for dense band-4 nominal singletons is now
the isolated blocker.

| window | cards | agents (spent/max) | net clean (promoted) | defect | transient-null | subagent tokens |
|---|---:|---:|---:|---:|---:|---:|
| h317_w1b | 12 | 61/61 | 1 (`yuvan`) | 2 | 9 | 2,898,353 |
| h317_w2a | 13 | 49/49 | 1 (`ṛtvij`) | 2 | 10 | 1,628,556 |
| h317_w2b | 12 | 52/52 | 0 | 2 | 10 | 2,153,758 |
| **total** | **37** | **162** | **2** | **6** | **29** | **6,680,667** |

medium50 net over the whole H317→H389→H437 arc: **2 / 50 promoted (4%)**;
kill-gate recalibration routed to a bug-hunt handoff (see
[`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) `H437_MEDIUM50_KILLGATE_CASCADE_2026-07-09`).

## 09-07-2026 — pwg_ru card stats rollup (annotate_stats.py)

Script v1.0.0 · Sonnet 5 (claude-sonnet-5)

| metric | value |
|---|---|
| lemmas | 145 |
| records (homonym groups) | 563 |
| senses | 11261 |
| government markers | 0 |
| lemmas with case variation | 0 |
| evidence: provides | 1734 |
| evidence: supports | 1935 |

## 12-07-2026 — pwg_ru card stats rollup (annotate_stats.py)

Script v1.1.0 · Opus 4.8 (claude-opus-4-8)

| metric | value |
|---|---|
| lemmas | 205 |
| records (homonym groups) | 635 |
| senses | 11505 |
| government markers | 508 |
| lemmas with case variation | 2 |
| grammar-joined lemmas (single homonym) | 32 |
| … whitney irregularities counted | 46 |
| grammar ambiguous-homonym (alignment owed) | 17 |
| dcs-matched lemmas | 170 |
| <ls> citations (total) | 41031 |
| evidence: provides | 1699 |
| evidence: supports | 1893 |

Numbers are over the current 205-lemma pwg_ru_translated store (the gitignored working
copy); the fields (`government`, `stats`, `sense_stats`, `record_stats`) are materialised
locally by re-running the annotator chain — the store itself is not committed. Contrast the
09-07 v1.0.0 row above (0 government markers, no grammar counts) with this v1.1.0 row: H777
joined the grammar block (`n_irregularities` no longer stuck at 0) and added the layer /
markup / QA / frequency families.

## 12-07-2026 — PWG case-government census, frozen (H778, government_census.py freeze)

Script v1.1.0 · Opus 4.8 (`claude-opus-4-8`). Corpus-level marker census over the **whole
raw** [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt)
(sha `430c910f8b0c9229`), frozen to the committed [`src/census_stats.json`](src/census_stats.json)
sidecar so the scan is not re-run on every question. This is the corpus answer to "сколько
таких помет в PWG"; the per-205-lemma store rollup above is the pwg_ru subset.

| metric | value |
|---|---|
| PWG entries scanned | 123366 |
| sense units scanned | 288991 |
| government markers (total) | 3853 |
| … paren-single / variation / mit-phrase | 2309 / 40 / 1504 |
| entries with ≥1 marker | 1476 |
| sense units with ≥1 marker | 3222 |

## 29-07-2026 — RV multi-translation evidence layer, wave 1b (H1844)

Context: [H1844](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1844-Opus_RussianTranslation_rv-multitranslation-typing-w1b_29.07.26.md) — divergence taxonomy, advisory word-level layer B, and the pwg_ru/en pipeline wiring, over the wave-1a spine. Orchestration and adjudication: **Opus 5 (`claude-opus-5[1m]`)**. Divergence typing generator: **`deepseek-chat`** (DeepSeek V3, OpenAI-compatible endpoint). Alignment models: **`bert-base-multilingual-cased`** (committed default) and **`sentence-transformers/LaBSE`**, both via the committed `tm_align.embed_aligner_factory`.

### Divergence-class distribution — pilot, 2,000 stanzas × 6 translator pairs

12,000 labels, of which 11,997 model-decided and 3 deterministic. Cost **$1.0582** (849,276 cache-miss + 1,033,344 cache-hit input, 687,741 output tokens).

| Class | Pilot n=12,000 | Spike n=300 |
|---|--:|--:|
| `agreement` | 37.2 % (4,462) | 37.7 % |
| `semantic_shift` | 54.4 % (6,533) | 62.0 % |
| `lexical_variant` | 6.0 % (719) | 0.3 % |
| `omitted_by_one` | 2.4 % (286) | 0.0 % |
| `added_by_one` | **0.0 % (0)** | 0.0 % |
| coarse: agreement / divergence / omission | 37.2 % / 60.4 % / 2.4 % | 37.7 % / 62.3 % / 0.0 % |

The spike/pilot column split is itself the result: a 300-observation spike read `lexical_variant` as dead (1 label) when its rate at scale is 6.0 %. `added_by_one` is inert at both scales — 0 of 12,000 — which is implausible against Griffith's freely supplied material and is flagged as a prompt/taxonomy defect, not a fact about the corpus.

### Spike S2 — inter-model agreement on the divergence taxonomy (H1901, 29-07-2026)

Three arms, same seeded 50-stanza sample (seed 1844), 300 (stanza × pair) labels each. Arms: **`deepseek-chat`** (DeepSeek, direct), **`openai/gpt-4o-mini`** and **`google/gemini-2.5-flash`** (both via OpenRouter). Orchestration Opus 5 (`claude-opus-5[1m]`). Cost for the two new arms: **$0.054**.

| Pair | n | five-class κ | coarse κ | `lexical_variant` vs `semantic_shift` κ |
|---|--:|--:|--:|--:|
| deepseek ↔ gpt-4o-mini | 300 | 0.222 | 0.235 | **0.089** |
| deepseek ↔ gemini-2.5-flash | 267 | 0.357 | 0.350 | **−0.012** |
| gpt-4o-mini ↔ gemini-2.5-flash | 267 | 0.227 | 0.216 | **0.256** |

Per-arm class usage on the shared sample:

| Class | deepseek | gpt-4o-mini | gemini-2.5-flash |
|---|--:|--:|--:|
| `agreement` | 37.7 % | 20.3 % | 27.3 % |
| `lexical_variant` | 0.3 % | 11.0 % | 6.7 % |
| `semantic_shift` | 62.0 % | 68.7 % | 65.9 % |
| `omitted_by_one` | 0.0 % | 0.0 % | 0.0 % |
| `added_by_one` | **0.0 %** | **0.0 %** | **0.0 %** |

**Verdict: the fine distinction is not separable** (mean κ ≈ 0.11, one arm-pair below chance) — K3 fires. Collapsing to coarse raises κ only to 0.216–0.350, "fair" but not reliable, so the coarse taxonomy is *more* reproducible without being demonstrated *reliable*; the step-8 human gate is the instrument for that and is now more load-bearing, not less.

**Methodological caution, recorded because it nearly shipped as a positive result:** raw agreement on the `lexical_variant`/`semantic_shift` subset reads 89.0 % / 95.1 % / 85.7 % — near-consensus by appearance, worthless in fact. All three models default to `semantic_shift`, so they agree by sharing a prior; κ removes that expected agreement and leaves ~nothing. Under extreme base-rate skew, percent-agreement measures the skew. `added_by_one` never fires in any arm (0/300, 0/300, 0/267), which indicts the instrument rather than the corpus.

### Layer-B word-level precision — 300-token gold, 69 adjudicated

Bar: ≥ 85 % per target language (R14). Annotator Opus 5 (`claude-opus-5[1m]`); sample frequency-stratified, seed 1844.

| Target | n | Correct | Precision | Verdict |
|---|--:|--:|--:|---|
| de | 24 | 7 | 29.2 % | **FAIL** |
| ru | 26 | 5 | 19.2 % | **FAIL** |
| en | 19 | 2 | 10.5 % | **FAIL** |

All three below the bar ⇒ **stop condition 3**: spine A ships alone, layer B ships flagged `low_confidence` and excluded from the contradiction gate, the 0.20 gate is not re-tuned, and the ~8.8 h full-scale run is **not** executed.

### Layer-B alignment run — 150 stanzas per model arm

| Metric | `bert-base-multilingual-cased` | `sentence-transformers/LaBSE` |
|---|--:|--:|
| Candidate token→span alignments | 9,400 | 9,400 |
| Dropped by the 0.20 ALIGN_GATE | **0** | **0** |
| Mutual-argmax confirmed | 30.2 % | 28.6 % |
| Modal confidence bucket | [0.5,0.6) — 6,016 | [0.5,0.6) — 6,462 |
| Throughput | 3.03 s/stanza | 2.83 s/stanza |

A gate that rejects 0 of 9,400 is not a gate: the H1457 A3 threshold (calibrated on 30 mined rows with one negative) carries no discriminative power on Vedic. Swapping the alignment model reproduces the signature rather than fixing it, so the failure is a property of subword-embedding alignment on transliterated Vedic, not of one checkpoint (risk K1/K2 landing as predicted). Full-scale extrapolation: 10,552 stanzas ≈ **8.8 h**, not the 52 h a cold-start probe suggested.

### wisdomlib, four roles (R11) — coverage

| Role | Status | Rows |
|---|---|--:|
| 1 · EN gloss tier | not populated — no gloss text on disk | 0 |
| 2 · tradition disambiguation | zero overlap — Buddhist probe set vs RV lemmas | 0 |
| 3 · fifth gate witness | not populated — same missing gloss text | 0 |
| 4 · AV citation locus | staged — no AV data, wave-1 non-goal (R3) | 0 |

`word_traditions.jsonl` holds 63 Vajrayāna Buddhist terms against the RV's 9,539 lemmas; the join key was verified sound in both directions (`agni`→`agní-`, `indra`→`índra-`), so the empty intersection is correct. **W1.13 cannot be met as written** — recorded rather than asserted away.

## 30-07-2026 — NWS tag half-translation store repair, before/after (H1903)

Continuation of [H1809](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1809-Sonnet_SanskritLexicography_nws-bare-citation-ls-markup_28.07.26.md)'s
domain-only migration (17 rows, `_BRACKET_TAG_DOMAIN` anchored on a Latin diasystem in slot 1) —
its own `nws_ls_markup.py census` reports 0 domain-slot half-translations both before and after
this pass, confirming no overlap/double-processing. This pass covers what that regex's Latin-only
anchor structurally could not reach: a Cyrillic diasystem, the unbracketed `DIA , DOM >` header
form, source-fidelity date/place residue, and one gloss-bracket false-positive.

| Defect class | Rows touched | Fix |
|---|--:|---|
| Cyrillic diasystem and/or domain slot (bracketed) | 16 | Latin restored from the same row's `de` field (never mistranslated), position-aligned, occurrence-count verified |
| `>`-separator dropped when the tag was translated (`ajA` card) | 3 | restored `Ved , unsp >` verbatim from `de` |
| Manuscript date+place ran into the domain slot (source-fidelity — confirmed against the raw `pilot/nws/br_ahm_i.json` scraped card) | 14 (ru+de, 10 distinct rows) | split to 2-slot `[DIA, DOM]` + `(DATE, PLACE)` restored to the body, both fields |
| `[mahat, n. (…)]` gloss-note bracket read as a spurious tag by the shape-only detector | 1 | `[…]` → `(…)` so the shape no longer collides |

**Verify:** a vocabulary-anchored direct-text scan and `validate_final_card_schema.nws_tag_defects()`
(new write-time guard, wired into `validate_sense()`) both report **0** Cyrillic-valued and **0**
comma/digit-bearing NWS tag slots store-wide (11,603 rows, JSONL integrity re-checked — same row
count before/after). `python nws_ls_markup.py census`, `nws_tag_census.py --selftest`,
`g5_card_render.py`, `build_g5_review_sheet.py --selftest`, `validate_final_card_schema.py
--selftest` all pass. The compensating Cyrillic aliases in `g5_card_render.DOMAIN_RU` (`без
уточн.`, `Мед.`, `Линг`, `Лингв`) are retired — see [FINDINGS §504](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md#504-the-nws-tag-layer-reaches-only-22--of-the-ru-store--a-facet-bar-over-it-is-right-but-it-is-not-the-sheets-main-axis).

Model: Sonnet 5 (`claude-sonnet-5`).

