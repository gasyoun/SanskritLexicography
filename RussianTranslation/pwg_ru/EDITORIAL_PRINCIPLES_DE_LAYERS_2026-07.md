# Editorial principles — German-side layers (H1624 G1–G6 + form layer)

_Created: 25-07-2026 · Last updated: 25-07-2026_

## Purpose

[H1624](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1624-Opus_SanskritLexicography_pwg-german-layers-backlog-ordered_25.07.26.md)
shipped six field families that thicken the DE edition graph without ever
rewriting the German string. Each family sits somewhere on a spectrum from
**pure machine derivation** (a regex/parser over `<ab>`/`<ls>`/`<lex>` markup
that always fires the same way) to **fields that wait on a human vote**
(H1306 style research) to **derivation with an explicit undecided flag**
(compound-split conflicts). This datasheet is the single place that states,
per field, which of those three buckets it is in and how confident the
extraction is — so a consumer never has to re-derive the provenance from the
code. It does **not** invent new editorial policy; every "voted" row below
points at the handoff that owns the vote, and every "derived" row points at
the extractor that produces it deterministically.

Cross-referenced from [pwg_ru.md §8.0](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md)
and [RUSSIANTRANSLATION_DEEP_MANUAL.md §2b–§2c](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md).


## Design fence (non-negotiable)

| Do | Do not |
|---|---|
| Attach structure/indexes derived from DE markup | Rewrite 19th-c. German orthography |
| Label supplement layers / owners / span types | Inject Russian into `de` / raw DE |
| Store derived fields on portrait / sense schema | Put `corpus_gate` / `review_status` into DE body |
| Keep grammar off the translate prompt (A/B already rejected) | Re-open grammar-in-prompt without a new measured A/B |
| Classify shared schema/path changes in [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) | Fix EN-only or RU-only without a ledger row |

One-line rule: **German layers thicken the edition graph; they do not smuggle RU, review scores, or quality labels into the DE string.**

## How to read this table

- **derived** — deterministic extraction from the DE (or DE+supplement) markup; re-running the extractor on the same input always yields the same output; no human adjudication step.
- **voted** — depends on a ratified `*.decisions.json` export from a review sheet; the field does not exist (or stays at its pre-vote default) until that file lands.
- **derived + undecided flag** — deterministic extraction that also detects when two source layers disagree, and marks the disagreement rather than resolving it.
- **confidence** — for `derived` fields, whether the extractor is a documented *floor* (undercounts, never overcounts) or a *ceiling* (best-effort, may include noise), plus any measured coverage number from the owning report. For `voted` fields, the blocker that keeps confidence at zero today.

## G1 — `gloss_lang` (per `{%…%}` span)

| Field | Source | Derived / voted | Confidence |
|---|---|---|---|
| `gloss_lang` (`de`\|`la`\|`en`\|`ambig`) | Rule cascade over `{%…%}` span text + surrounding context in [`pwg_mask.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py) `classify_pct_detail` | derived | Floor by design — `ambig` is a deliberate escape hatch (`RULE_HOMOGRAPH_AMBIG`, translate-if-unsure) rather than a forced de/la/en guess; selftest vectors pin every rule (`window_selftest` + `test_pwg_mask_gloss_lang_g1`) |
| `rule_id` | Same cascade — one of `latin_cue`, `latin_phrase`, `botany_binomial`, `wilson_en`, `engl_cue`, `english_content`, `homograph_ambig`, `default_de` | derived | Each `rule_id` is a named, individually-tested cue (see table below); `default_de` is the fallback, not a rule match |
| `translate` (bool) | Derived from `gloss_lang`/`rule_id` — `False` for `la`/`en`, `True` for `de`/`ambig` | derived | Gate consumer: residue/mask selftests assert LA/EN spans stay untranslated |

Rule cue reference (do not rename `rule_id` values lightly — they are a stable API per `pwg_mask.py` header comment):

| `rule_id` | Cue |
|---|---|
| `latin_cue` | `das lat.` / `<ab>lat.</ab>` / `griech.` |
| `latin_phrase` | `De accentu…` / `In usum Delphini` |
| `botany_binomial` | `Trapa bispinosa` / `Galedupa arborea` style binomials |
| `wilson_en` | `Wils./WILSON` + English content |
| `engl_cue` | `engl.` / `englisch` near the span |
| `english_content` | Clear English prose, no DE markers |
| `homograph_ambig` | Short ambiguous tokens (`in` / `an` / `et` …) |
| `default_de` | No cue matched — fallback |

## G2 — `government` (Rektion) on every DE sense

| Field | Source | Derived / voted | Confidence |
|---|---|---|---|
| `government[].cases` | `<ab>Instr.</ab>` / `(Instr.)` etc. in DE, via [`government_census.extract_government`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/government_census.py) | derived | **Floor, not ceiling** (module docstring, explicit): parenthesized non-government cases and unmatched free-text mentions are excluded rather than guessed |
| `government[].variation` (bool), `.connector` (`und`/`oder`/``) | Same extractor — multi-case groups (`paren-variation`) | derived | Same floor guarantee |
| `government[].kind`, `.span` | Same extractor — `paren-single` / `paren-variation` / `mit-phrase` | derived | Deterministic, re-runnable (`--check` flags stored-vs-re-extracted drift) |
| store stamping | `annotate_government.py` (retrofit/drift-repair) **or** `promote_final_cards.rows_for` (new promotions stamp at write time, H1624 G2) | derived | Two producers, same extractor — no dual-source drift by construction |

Honest floor-vs-ceiling banner stays on [government.html](https://gasyoun.github.io/SanskritLexicography/government.html) per H1624 design fence.


## Form layer (H1624 sibling of G2) — `form_labels` + `form_notes`

H1624 also shipped a DE-side morphosyntax layer that is **not** Rektion. Handed
as PRs [#717](https://github.com/gasyoun/SanskritLexicography/pull/717) /
[#718](https://github.com/gasyoun/SanskritLexicography/pull/718); inventory required
by [H1634](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1634-Sonnet_SanskritLexicography_pwg-de-editorial-principles-doc_25.07.26.md).

| Field | Source | Derived / voted | Confidence |
|---|---|---|---|
| `form_labels` (number / gender / voice / case_form) | DE `<ab>sg./du./pl.</ab>`, `<lex>m.</lex>` / unambiguous `masc./fem./neutr.`, `act./med./pass.`, `nom./voc.` via [`form_labels.extract_form_labels`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/form_labels.py) | derived | Floor: bare `<ab>n.</ab>` is **not** gender (too often "note"); never invents labels |
| `form_notes` (dedicated nom./voc.) | Same DE markers; first-class field separate from multi-axis `form_labels` and from `government` | derived | High on narrow axis; shape `{case: nom|voc, kind, span}` via `extract_form_notes` |

Stamped at promote + portrait; backfill via `annotate_form_labels.py`. LANG_PARITY: `form_labels_number_gender_voice_h1624`, `form_notes_nom_voc_dedicated_h1624`.

## G3 — `citation_edges` (normalized `<ls>` graph)

| Field | Source | Derived / voted | Confidence |
|---|---|---|---|
| `raw_ls`, `siglum` | Visible text inside `<ls>…</ls>`, source-key extraction in [`citation_edges.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_edges.py) | derived | Deterministic parse; raw `<ls>` is never stripped from DE |
| `work_id`, `renou`, `bib_ok` | `ls_source_map` lookup (matched) | derived | Ceiling bounded by `ls_source_map` completeness — unmatched sigla fall through to `bib`/`orphan`, not silently dropped |
| `page` | Locator (digit-bearing token + remainder) after siglum | derived | Best-effort string parse; absent when no digit run found (`null`, not guessed) |
| `resolver_status` | One of `map` (siglum matched `ls_source_map`, has renou/genre) / `bib` / `orphan` / `empty` | derived | Coverage report gives measured % resolvable vs orphan (see [CITATION_COVERAGE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CITATION_COVERAGE.md)) — this is the honest confidence number, not a claim of full resolution |

## G4 — `edition_rel` (edition-relationship flags on DE subcards)

| Field | Source | Derived / voted | Confidence |
|---|---|---|---|
| `edition_rel` (`restate`\|`pw_correct`\|`sch_star`\|`derived_sense`\|`a2a`\|`nws_at_sense`) | Deterministic join from [`relationships_rollup.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/relationships_rollup.tsv) via [`edition_rel.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/edition_rel.py) `classify_edition_rel` | derived | Machine classification only; `pw_correct` requires a matched PWG gender index or defaults to `restate` (documented fallback, not a guess) |
| Human-facing *typology display names* | H180 typology sheets | voted (display layer only) | Optional — attaching the machine class does **not** wait on the vote; only the label wording does (H1624 design decision, not this doc's invention) |

## G5 — H1306 DE tags (doublets / `v. l.` / *im Comp.*) — ⏸ blocked

| Field | Source | Derived / voted | Confidence |
|---|---|---|---|
| `doublet`, `varia_lectio`, `compound_position` | Would tag DE spans per voted options once `pwg_ru/eval/h1306_style.decisions.json` exists | **voted — not yet ratified** | Confidence: **zero today**. [H1306](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md) Phase 1 (style research memo) shipped; the ratification sheet ([h1306_style_sheet.html](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/h1306_style_sheet.html)) is present but unexported. Do not invent prompt rules or a provisional tag set ahead of the vote — H1624 explicit non-goal. |

## G6 — compound/derivation DE portrait

| Field | Source | Derived / voted | Confidence |
|---|---|---|---|
| `derivation` block (compound split / derivation path) | Portrait `derivation` sidecar, [`enrich_portrait_derivation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/enrich_portrait_derivation.py) | derived | Machine-safe fields only |
| `conflict` (bool), `conflict_kind` | `compound_status == 'differs'` (PWG split ≠ index `compound_members`) | **derived + undecided flag** | Measured: **4,226 / 39,539 rows (10.69%)** flagged `differs` (H1624 G6 conflict-rate report) — never auto-adjudicated |
| `needs_human` (bool) | `compound_status` in `{differs, index-only}` | **derived + undecided flag** | Same measured rate; this is the field that routes the ~4.2k disagreements to a future `/review-sheet` sample (N11), not a silent resolution |


## G7 — DHĀTUP. → Palsule wiring — blocked

| Field | Source | Derived / voted | Confidence |
|---|---|---|---|
| DHĀTUP. tooltip / Palsule concordance link | Would wire from Palsule XLS once present | **undecided (data-gated)** | Confidence: **zero today**. XLS absent; delegated to [H1333](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1333-Opus_RussianTranslation_pwg-ru-dhatup-palsule-wire-from-xls_19.07.26.md). Do not invent a machine list. |

## Field-family summary

| Family | Bucket | Notes |
|---|---|---|
| G1 `gloss_lang`/`rule_id` | derived | Rule-cascade, floor by design (`ambig` escape hatch) |
| G2 `government` | derived | Explicit floor, not ceiling |
| G3 `citation_edges` | derived | Ceiling bounded by `ls_source_map`; honest coverage % |
| G4 `edition_rel` | derived (+ voted display names, optional) | Machine class ships without waiting on typology vote |
| G5 H1306 DE tags | **voted, unratified** | Zero confidence until `h1306_style.decisions.json` |
| form_labels / form_notes | derived | Not Rektion; nom/voc dedicated field |
| G6 `derivation`/`conflict`/`needs_human` | derived + undecided flag | 10.69% measured disagreement, routed to human review, not resolved |
| G7 Palsule | **data-gated** | XLS absent; H1333 |

## Explicit non-goals of this datasheet

- Does not adjudicate G5 (H1306) or the G6 `differs` compound disagreements — it documents that they are undecided, per [H1624 explicit non-goals](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1624-Opus_SanskritLexicography_pwg-german-layers-backlog-ordered_25.07.26.md#explicit-non-goals).
- Does not re-derive coverage numbers beyond what the owning reports already measured (H1624 acceptance matrix, `conflict_rate_report`, [CITATION_COVERAGE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CITATION_COVERAGE.md)).
- Does not cover G7 (DHĀTUP. → Palsule) — still XLS-gated, delegated to [H1333](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1333-Opus_RussianTranslation_pwg-ru-dhatup-palsule-wire-from-xls_19.07.26.md).

## Related

- [H1624](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1624-Opus_SanskritLexicography_pwg-german-layers-backlog-ordered_25.07.26.md) — parent programme, acceptance matrix, PR links (#715, #716, #720, #721, #722)
- [pwg_ru.md §8.0–§8.1](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md) — layer registry this datasheet expands on
- [RUSSIANTRANSLATION_DEEP_MANUAL.md §2b–§2c](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md) — operator-facing English twin
- [H1306](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md) — owns the G5 vote
- [H1282 archive](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1282-Opus_SanskritLexicography_pwg-ru-derivation-portrait-enrichment_19.07.26.md) — G6 residue origin

## Provenance (dual-run salvage)

- First land: [PR #737](https://github.com/gasyoun/SanskritLexicography/pull/737) (Claude Code session, 25-07-2026) — G1–G6 core tables.
- Gap fill: [PR #738](https://github.com/gasyoun/SanskritLexicography/pull/738) (Grok 4.5) — design fence, **form_labels/form_notes** (H1634 Do list), G7 blocked table, metadoc, LANG_PARITY pointers.

_Dr. Mārcis Gasūns_
