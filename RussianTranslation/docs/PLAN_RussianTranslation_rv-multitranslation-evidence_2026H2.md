# PLAN — Rig-Veda multi-translation evidence layer for PWG→RU/EN

_Created: 29-07-2026 · Last updated: 29-07-2026_

Cover/index document for the **Rig-Veda multi-translation evidence layer**: a lemma-keyed
join of the Ṛgveda against four translations (Grassmann 1876–77 · Geldner 1951–57 ·
Elizarenkova 1989–99 · Griffith 1896), a typed divergence taxonomy over them, an advisory
word-level alignment layer, and the wiring that makes all of it visible to the PWG→Russian
and PWG→English translation pipeline.

Authored by `/ask` (Opus 5, `claude-opus-5[1m]`) on 29-07-2026 after a 4-round interview.
Execution handoffs: [H1843](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1843-Sonnet_RussianTranslation_rv-multitranslation-spine-w1a_29.07.26.md)
(wave 1a) and [H1844](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1844-Opus_RussianTranslation_rv-multitranslation-typing-w1b_29.07.26.md)
(wave 1b).

**Layer docs:**
[ROADMAP](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_rv-multitranslation-evidence_2026H2.md) ·
[ARCHITECTURE](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_rv-multitranslation-evidence.md) ·
[IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_rv-multitranslation-evidence.md) ·
[VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_rv-multitranslation-evidence.md)

---

## 1. Goal in one paragraph

The Ṛgveda is the one Sanskrit text where the same 10,552 stanzas exist in four independent,
century-spanning scholarly translations into three target languages. That makes it the natural
**calibration and evidence corpus** for a machine translation pipeline whose output is a
Russian (and later English) rendering of a German dictionary. This plan turns that latent
resource into a committed, queryable layer: for any Ṛgvedic lemma, what did each translator
make of it, where did they disagree, and where did one of them decline to translate at all.
The layer then feeds the pipeline in three places — as evidence shown to the judge, as a
contradiction gate that queues suspect cards for review, and as a new translation-memory tier
supplying candidate glosses for **every** target language, not Russian alone.

## 2. What already exists — do NOT rebuild

Recorded from the `/prior-art` audit run on 29-07-2026. Every item below is committed and live.

| Asset | Where | What it already gives us |
|---|---|---|
| VedaWeb 2.0 bulk export (H096, CC BY 4.0) | [`VisualDCS/non-derived/vedaweb/`](https://github.com/gasyoun/VisualDCS/tree/main/non-derived/vedaweb) | Casaretto accented word-split + morphology, lemmatization + CDSD cross-refs, Scarlata–Widmer accented text, Lubotsky padapāṭha, metrical data 2024 — all 10,552 stanzas, position-aligned on `location` |
| GRA ↔ VedaWeb crosswalk (H097) | [`gra_vedaweb_crosswalk.tsv`](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/vedaweb/gra_vedaweb_crosswalk.tsv) | VedaWeb's `id_gra` **equals** the Grassmann `<L>` number — the join is local, no fuzzy matching. 9,945/12,785 GRA entries (77.8 %) RV-attested |
| PWG ↔ VedaWeb gloss crosswalk (H362) | [`pwg_vedaweb_gloss_crosswalk.tsv`](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/vedaweb/pwg_vedaweb_gloss_crosswalk.tsv) | 10,182 PWG entries RV-attested, each row already carrying `geldner_text` **and** `grassmann_text` side by side. The Grassmann-vs-Geldner comparison MG asked for has its raw material here |
| Three translation layers | `geldner_de_1951_1957.json`, `grassmann_de_1876_1877.json`, `elizarenkova_ru_1989_1999.json` in the same directory | Stanza-keyed, CC BY 4.0, 10,552 stanzas each |
| Five-layer aligned Ṛgveda | [`rvlinks/RV_sa-hn-ru-de-en_1.html`](https://github.com/sanskrit-lexicon/rvlinks/blob/main/RV_sa-hn-ru-de-en_1.html) (12.4 MB) = the page published at [gasyoun.github.io](https://gasyoun.github.io) | Devanāgarī + IAST + Elizarenkova + Geldner + **Griffith** — the only place the English layer exists in aligned form. 1,029 per-hymn pages in [`rvhymns/`](https://github.com/sanskrit-lexicon/rvlinks/tree/main/rvhymns) |
| Calibrated alignment gate | [`src/ALIGN_GATE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ALIGN_GATE.md) + [`src/tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py) | Per-pair LaBSE confidence, gate calibrated at `agreement >= 0.20` (H1457 A3) |
| LaBSE/Vecalign sentence aligner | [`src/LABSE_ALIGN.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/LABSE_ALIGN.md) + [`src/tm_saru_align_labse.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_saru_align_labse.py) | Monotone DP alignment, precision@sample 0.966 (H1457 A5) |
| TM contract + source priors | [`schemas/translation_memory.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/translation_memory.schema.json), [`src/tm_source_weights.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_source_weights.json) | `trust_level` / `reuse_policy` enums, `lang: [ru, en]`, and `by_work_contains` **already carrying `rigveda: 0.72` and `atharvaveda: 0.72`** |
| wisdomlib crawler | [`SamudraManthanam/web/corpus_builder/wisdomlib/`](https://github.com/gasyoun/SamudraManthanam/tree/main/web/corpus_builder/wisdomlib) | `entries_index.jsonl`, `word_traditions.jsonl`, `definitions.py`; bulk-public rights ruling of 28-07-2026 |
| Renou-footnote carrier | Elizarenkova's commentary inside SamudraManthanam (`Index/.../NN_rigveda.no_tags`) | **2,213** mentions of Renou across the 10 maṇḍalas, **368** of them carrying a directly quoted French fragment |
| Atharvaveda text base | [`avlinks`](https://github.com/sanskrit-lexicon/avlinks) | 731 hymns / 5,933 verses, published; no translation layer yet |

**Build-vs-reuse verdict:** nothing in wave 1 is a from-scratch build. Layer A is a join over
existing committed feeds; layer B is a re-parameterization of an aligner that already ships
with a calibrated gate; the TM tier is two enum values and a weights row, not a new subsystem.
The only genuinely new extraction is Griffith (out of our own HTML) and the Renou index.

## 3. Decisions taken — the 17 interview rulings

Every row below was ruled by a human on 29-07-2026 and is **binding on the execution agent**.
No row may be re-litigated mid-run.

| # | Fork | Ruling | Note |
|---|---|---|---|
| R1 | Primary deliverable | **Both, strictly sequential** — wave 1 = working evidence layer for the pipeline; wave 2 = the same layer packaged as a citable dataset + paper | Wave 2 does not start until wave 1 is accepted |
| R2 | Owning repo | **`SanskritLexicography/RussianTranslation`** | Not VisualDCS; the feed stays where it is and is read sibling-path |
| R3 | Wave-1 scope | **Ṛgveda only, all 10,552 stanzas.** Atharvaveda begins only once RV work is fully complete | Explicit non-goal for wave 1 |
| R4 | English layer | **Griffith now** (public domain, extracted from our own HTML); **Jamison–Brereton later as the "gold" reference** | J–B is in copyright (OUP) — sample-scale reference use only, never bulk |
| R5 | Granularity | **Deterministic spine A + word-level layer B on top.** B is advisory and never written into reviewed data | Answers "how is this particular word translated" without letting alignment error into the store |
| R6 | Divergence model | **Typed taxonomy** — agreement / lexical variant / semantic shift / omitted by one / added by one | Gives the pipeline a signal and the wave-2 paper a statistic |
| R7 | Pipeline entry point | **All three at once**: witness shown to the judge, contradiction gate, **and** a new TM tier supplying candidate glosses — **and not for Russian only** | Explicitly serves the EN path and any future third language |
| R8 | Rights posture | **Ignore rights as a blocker.** Internal use unrestricted, including the grey-rights Samudra commentary and the Renou quotations | Human ruling, recorded verbatim; consequence in §5 |
| R9 | Renou in wave 1 | **Locus index + the 368 extracted French quotations.** Full *Études védiques et pāṇinéennes* not before 2027 | Renou d. 1966 — EVP in copyright in France until 2037 |
| R10 | Publish boundary | **Everything in the open repo, no split** between rights-clean and grey material | Human ruling; consequence in §5 |
| R11 | wisdomlib roles | **All four** — EN gloss TM tier for PWG→EN · tradition-based sense disambiguation · contradiction-gate witness · citation-locus source for the AV wave | Uses only already-downloaded data in wave 1 |
| R12 | Storage format | **JSONL keyed by lemma + flat TSV mirror**, plus a JSON Schema in `schemas/` | Matches the existing crosswalk feeds; no SQLite, no RDF-first |
| R13 | Typing scale | **Pilot ~2,000 stanzas → gate → full 10,552 run** | Same shape as the existing pwg_ru pilot discipline |
| R14 | Layer-B acceptance | **300-token gold sample, precision ≥ 85 % per language** (ru/de/en scored separately) | Below the bar, B ships flagged `low_confidence` and is excluded from gates; spine A is unaffected |
| R15 | Pilot gate | **≥ 80 % agreement with a human on 100 stanzas**, collected through `/review-sheet` HTML voting | Markdown checkbox sheets are banned org-wide |
| R16 | Ambiguity policy | **Take the marked default, log it, keep going.** Never halt on an unplanned fork | Logged to `DECISIONS_LOG` inside the run |
| R17 | The fence | Read-only: reviewed `pwg_ru` data · the VisualDCS vedaweb feed · csl-orig and all dictionary sources. **No wisdomlib network crawl during the run** | See §4 |

## 4. The autonomy contract

Recorded verbatim for the execution agent. This is the section that makes a 5–8 hour
unattended run safe.

**On an unplanned ambiguity (R16).** Every fork this plan anticipates carries a marked
default in [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_rv-multitranslation-evidence.md).
For a fork this plan did **not** anticipate: choose the more conservative option (the one that
writes less, asserts less, and leaves the existing pipeline unchanged), append a dated line to
`docs/DECISIONS_LOG_rv_multitranslation.md` recording the fork, the choice and the reason,
and continue. Do not stop. Do not ask.

**Stop conditions — the only four.** Halt and report, rather than improvising, when:

1. A required input feed is absent or unreadable (any file listed in §2 that is expected but
   missing) — the run cannot proceed on invented data.
2. A write outside the fence is about to happen (see below).
3. The layer-B gold sample scores below 85 % on **all three** languages — that is not a
   parameter to tune blind; ship spine A alone, mark B `low_confidence`, and report.
4. Cumulative token spend crosses the run's cost gate — the repo's existing cost-gate
   machinery governs, not a new one.

Everything else — a stanza that fails to parse, a lemma with no translation coverage, an
unexpected divergence class — is logged and skipped, never escalated.

**Commit authority.** Both handoffs are handoff-scoped work under the standing org rule:
commit → PR → merge in the same pass, no confirmation prompt. Work happens in a
session-unique worktree off `origin/master`, never in the guarded main checkout.

**The fence (R17) — read-only, no exceptions.**

- Reviewed `pwg_ru` data: `headword_index.tsv`, reviewed cards, the store. The new layer
  writes only into its own files.
- [`VisualDCS/non-derived/vedaweb/`](https://github.com/gasyoun/VisualDCS/tree/main/non-derived/vedaweb) —
  a non-derived bulk export whose re-pull consumes a **single-use** `pickupKey`. Read it; never
  rewrite it; never hit the VedaWeb API.
- `csl-orig`, `GRA`, `PWG` and every other dictionary source repo — no commits, ever
  (standing org rule, restated here so the agent does not have to go looking for it).
- wisdomlib: use only the already-downloaded `entries_index.jsonl` / `word_traditions.jsonl`.
  A fresh network crawl is a separate, daytime task.

## 5. Known consequences of R8 + R10 — stated, not re-litigated

The human ruling is that rights do not gate this work and that everything lands in the open
repo without a rights-based split. Recorded and followed. Three factual consequences the
execution agent should be aware of, so nobody is surprised later:

1. **Most of the material needs no exemption at all.** Geldner, Grassmann and Elizarenkova as
   carried by the VedaWeb feed are **CC BY 4.0**; Griffith 1896 is public domain; wisdomlib has
   a bulk-public ruling of 28-07-2026. The ruling only actually bites on two things: the
   Samudra copy of Elizarenkova's *commentary* (grey-rights, and the sole carrier of the Renou
   footnotes) and, later, Jamison–Brereton.
2. **Keep the Renou artifact quotation-shaped.** The design commits a locus index plus the 368
   short French fragments Elizarenkova herself quotes — that is quotation with attribution, a
   materially different act from redistributing the commentary. Copying whole-stanza commentary
   text into the repo is **not** part of this plan and should not be added on the agent's own
   initiative; if a step seems to require it, that is an unplanned fork → take the conservative
   default (index the locus, do not copy the body) and log it.
3. **Wave 2 will meet a gate.** A citable, DOI-bearing dataset release runs through
   `/publish-safety-check`, which will flag any grey-rights payload. Because of R10 there is no
   pre-separated clean subset, so wave 2 must budget a subsetting step. This is a scheduling
   fact recorded in the roadmap's wave-2 entry, not an objection to R10.

## 6. Wave-1 deliverables at a glance

Full detail in the layer docs; this is the index.

| ID | Deliverable | Handoff | Acceptance |
|---|---|---|---|
| W1.1 | `griffith_en_1896.json` — English layer extracted from our own HTML, stanza-keyed like the other three | H1843 | 10,552 stanzas, 0 unmatched loci |
| W1.2 | `rv_stanza_translations.jsonl` + `rv_lemma_occurrences.jsonl` + schema — lemma → stanzas → 4 translations | H1843 | Every RV lemma present; join is `location`-exact, no fuzzy |
| W1.3 | `rv_renou_citation_index.jsonl` — 2,213 loci, 368 with quoted French | H1843 | Counts reproduce; every row carries maṇḍala/hymn/stanza |
| W1.4 | Typed divergence taxonomy, pilot 2,000 → gate → full 10,552 | H1844 | ≥ 80 % human agreement on 100 stanzas (R15) |
| W1.5 | Word-level layer B with per-pair confidence | H1844 | ≥ 85 % precision per language on 300-token gold (R14) |
| W1.6 | Pipeline wiring — judge witness, contradiction gate, TM tier (ru **and** en) | H1844 | Existing test suite green; `lang_parity_check.py` passes |
| W1.7 | wisdomlib in all four roles | H1844 | Each role has a smoke test; no network access during the run |

## 7. Non-goals for wave 1

- Atharvaveda (R3) — begins only after RV is complete.
- Full Renou EVP (R9) — not before 2027.
- Jamison–Brereton at bulk scale (R4) — sample-scale reference only.
- A citable dataset release with a DOI (R1) — that is wave 2.
- Any change to reviewed `pwg_ru` card data (R17).
- Re-pulling anything from the VedaWeb API (R17).

_Dr. Mārcis Gasūns_
