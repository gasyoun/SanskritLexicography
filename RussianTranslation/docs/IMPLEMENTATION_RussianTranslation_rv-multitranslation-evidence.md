# IMPLEMENTATION — Rig-Veda multi-translation evidence layer, wave 1

_Created: 29-07-2026 · Last updated: 29-07-2026_

File-level, step-ordered build sequence for wave 1 of
[PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md).
Data model and contracts: [ARCHITECTURE](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_rv-multitranslation-evidence.md).
Acceptance: [VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_rv-multitranslation-evidence.md).

Every step names the files it touches and what it depends on. **Each step also names its
marked default** — the choice the agent takes without asking if the step turns out ambiguous
(ruling R16).

---

## Preconditions — check before step 1, halt if unmet

1. The sibling feed resolves and these five files are readable under
   `VisualDCS/non-derived/vedaweb/`: `lemmatization.json`,
   `geldner_de_1951_1957.json`, `grassmann_de_1876_1877.json`,
   `elizarenkova_ru_1989_1999.json`, `accented_text_scarlata_widmer_lubotsky.json`.
2. `rvlinks/RV_sa-hn-ru-de-en_1.html` resolves as a sibling repo checkout.
3. The SamudraManthanam Ṛgveda commentary files resolve
   (`Index/lib/x86_64-win64/add/To_add/NN_rigveda.no_tags`, 10 files).
4. `SamudraManthanam/web/corpus_builder/wisdomlib/entries_index.jsonl` and
   `word_traditions.jsonl` are present **on disk** — no network access is permitted (R17).

A missing input is stop condition 1. Do not synthesise, do not fetch.

## Windows and encoding rules — apply to every script written below

Org-level, mechanically linted: `sys.stdout.reconfigure(encoding='utf-8')` and
`sys.stderr.reconfigure(encoding='utf-8')` at the top of every printing script; `encoding='utf-8'`
on every output-capturing `subprocess.run`; never write a UTF-8 BOM. Multi-step work goes in a
`.py` file, not an inline shell one-liner. Repo CI additionally enforces: no trailing
whitespace, newline at EOF, Markdown lint and link-check clean.

---

# Wave 1a — deterministic spine (handoff H1843)

## Step 1 — `src/rv_griffith_extract.py`

**Touches:** new `src/rv_griffith_extract.py`; writes `pwg_ru/griffith_en_1896.json`.
**Depends on:** nothing.

Parse `rvlinks/RV_sa-hn-ru-de-en_1.html`. The file is a flat sequence of blocks; the locus is
carried by `p.stamp` in the form `rv01.001.01`, and the English text by the following `p.en`.
Convert `rv01.001.01` → `1.1.1` (strip the `rv` prefix, drop leading zeros in each of the three
fields). Emit the same envelope the VedaWeb translation files use: a top-level object with
`meta` (author `Ralph T. H. Griffith`, year `1896`, language `en`, plus a `provenance` string
naming this extraction and its source commit) and a `contents` list of
`{createdAt, archived, text, location}`.

- **Marked default — `<BR>` handling:** the English blocks contain literal line breaks. Replace
  them with `\n`, do not collapse to a space; Elizarenkova's records already use `\n` the same way.
- **Marked default — locus not in the VedaWeb set:** record it in the run log and skip the
  record. Do not invent a mapping.
- **Marked default — duplicate locus:** keep the first, log the collision.

## Step 2 — `src/rv_spine_build.py` (part 1: stanza table)

**Touches:** new `src/rv_spine_build.py`; writes `pwg_ru/rv_stanza_translations.jsonl`.
**Depends on:** step 1.

Load the four translation files, key each by `location`, and emit one record per stanza in the
canonical 10,552-stanza set (taken from `lemmatization.json`, which is the authority for what
stanzas exist). For each translator write `status` + `text` per ARCHITECTURE §3.1:
`present` when the locus is in that translator's `contents` with non-blank text,
`absent_from_source` when the locus is missing from that file entirely, `empty` when present
but blank. Also split `location` into integer `mandala` / `hymn` / `stanza`.

- **Marked default — a translator's file has a locus not in the canonical set:** log and ignore;
  the lemmatization export defines the stanza universe.
- **Hard invariant:** exactly four stanzas must come out `absent_from_source` for Geldner
  (`10.106.5`–`10.106.8`) and zero for Grassmann and Elizarenkova. If the numbers differ, the
  parse is wrong — that is a bug to fix, not a finding to record.

## Step 3 — `src/rv_spine_build.py` (part 2: lemma occurrences)

**Touches:** same script; writes `pwg_ru/rv_lemma_occurrences.jsonl`.
**Depends on:** step 2.

For each of the 10,552 records in `lemmatization.json`, parse `transformContext` — it is a
**JSON string**, not a nested object, so `json.loads` it — yielding a list of tokens each with
`form`, `lemma`, `lemma_ewaia`, `id_gra`, `id_mw`, `id_pwg`. Group by `lemma`; emit one record
per lemma with its `occurrence_count` and the full `occurrences` list
(`location`, `form`, `token_index`, `wordlevel: null`).

This step **is** deliverable W1.5 — the dictionary anchors are already on the tokens, so no
separate crosswalk join is needed. Carry `id_gra` / `id_pwg` / `id_mw` up to the lemma record as
the union over its tokens.

- **Marked default — a token's `lemma` is empty:** key it under the `form` and set
  `lemma_missing: true`. Do not drop the token; the total must reconcile to 164,758.
- **Marked default — conflicting `id_pwg` across tokens of one lemma:** keep the union, sorted,
  and do not attempt to pick a winner.

## Step 4 — `src/rv_spine_build.py` (part 3: flat mirror) + schema

**Touches:** same script; writes `pwg_ru/rv_translation_spine.tsv`,
`schemas/rv_translation_spine.schema.json`.
**Depends on:** steps 2 and 3.

Emit the denormalised TSV (columns in ARCHITECTURE §3.3) and a JSON Schema covering both JSONL
files. Follow the existing house style in `schemas/translation_memory.schema.json`:
`$schema` draft 2020-12, a `$id`, `$defs` for the shared enums (`status`, `translator`,
`divergence_class`).

- **Marked default — the TSV exceeds 200 MB:** do not commit it; emit it under a gitignored
  path, commit the generator plus a 500-row sample as
  `pwg_ru/rv_translation_spine.sample.tsv`, and note it in the run log. The two JSONL files are
  the contract, the TSV is a convenience view.

## Step 5 — `src/rv_renou_citations.py`

**Touches:** new `src/rv_renou_citations.py`; writes `pwg_ru/rv_renou_citation_index.jsonl`.
**Depends on:** nothing (can run in parallel with steps 1–4).

Scan the ten `NN_rigveda.no_tags` commentary files for mentions of `Рену`. For each: resolve the
enclosing stanza locus from the commentary's own numbering, capture a bounded Russian context
window, and detect whether a Latin-script quotation in guillemets follows within ~25 characters —
if so, extract it as `quote_fr` and set `mention_kind: "quoted_fr"`, otherwise
`mention_kind: "paraphrase_ru"` with `quote_fr: null`.

**Do not use the `renou_` prefix for anything here** — that token already means the 1956
language-states axis in this repo (ARCHITECTURE §3.4). Everything is `rv_renou_*`.

- **Hard invariant:** 2,213 total mentions, 368 with a Latin-script quotation. Per-maṇḍala
  totals for cross-checking: I 459 · II 117 · III 161 · IV 118 · V 158 · VI 110 · VII 171 ·
  VIII 123 · IX 226 · X 287.
- **Marked default — the locus cannot be resolved:** emit the row with `location: null` and a
  `locus_unresolved: true` flag rather than dropping it, so the count still reconciles.
- **Marked default — context window length:** 300 characters centred on the mention, clipped to
  sentence boundaries where they exist. Per PLAN §5 this stays a bounded window; do not widen it
  to the surrounding paragraph.

## Step 6 — tests and wave-1a close-out

**Touches:** new `tests/test_rv_spine.py`; updates `CHANGELOG.md`, `.ai_state.md`.
**Depends on:** steps 1–5.

Tests asserting every hard invariant above (see VERIFICATION §2). Then the standard close-out:
an `[Unreleased]` changelog bullet, `.ai_state.md` updated, commit → PR → merge.

---

# Wave 1b — typing, alignment, wiring (handoff H1844)

## Step 7 — `src/rv_divergence_type.py`, pilot

**Touches:** new `src/rv_divergence_type.py`; writes `pwg_ru/rv_divergence_pilot.jsonl`.
**Depends on:** wave 1a merged.

Type ~2,000 stanzas over the five classes of ARCHITECTURE §3.5, **per translator pair** (six
pairs over four translators). Compute the `absent_from_source` sub-case deterministically before
any model call — it is already in the stanza table and must not cost a token.

- **Marked default — sampling frame:** stratified by maṇḍala proportionally to stanza count,
  seeded deterministically so the pilot is reproducible.
- **Marked default — a pair where one side is `absent_from_source`:** label
  `omitted_by_one` deterministically and skip the model call.

## Step 8 — the human gate

**Touches:** writes `review/rv_divergence_gate_<date>.html` and, after voting,
`review/rv_divergence_gate_<date>.decisions.json`.
**Depends on:** step 7.

Sample 100 stanzas out of the pilot into a `/review-sheet` HTML voting sheet — **an HTML sheet,
never a Markdown checkbox list**, which is banned org-wide. Human votes the class per item.
Agreement ≥ 80 % releases step 9 (R15).

**This is the one step that requires a human and therefore cannot complete inside an unattended
run.** The agent produces the sheet, records that it is awaiting a vote, mirrors a `@DO` row
into [`Uprava/GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md),
and proceeds to step 10 — which does not depend on it. It does **not** stop the run, and it does
**not** self-approve the gate.

## Step 9 — full typing run

**Touches:** writes `pwg_ru/rv_divergence.jsonl`; enriches `rv_stanza_translations.jsonl`'s
`divergence` field.
**Depends on:** step 8 passing.

All 10,552 stanzas, six translator pairs. Runs under the repo's existing cost gate.

- **Marked default — the gate has not been voted when the agent reaches this step:** do not run.
  Leave it queued, log it, finish everything else. A full run without the gate is exactly the
  waste ruling R13 exists to prevent.

## Step 10 — `src/rv_wordlevel_align.py`

**Touches:** new `src/rv_wordlevel_align.py`; writes `pwg_ru/rv_wordlevel.jsonl`, enriches
`rv_lemma_occurrences.jsonl`'s `wordlevel` field.
**Depends on:** wave 1a merged. Independent of steps 7–9 — run it in parallel.

**Reuse, do not rewrite.** [`src/tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py)
already provides per-pair LaBSE confidence through the in-env `nn_api.embed` path, calibrated at
`agreement >= 0.20` ([ALIGN_GATE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ALIGN_GATE.md));
[`src/tm_saru_align_labse.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_saru_align_labse.py)
provides the monotone Vecalign DP ([LABSE_ALIGN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/LABSE_ALIGN.md)).
This step parameterises those for the token → span case; it introduces no new aligner.

Every emitted span carries `confidence` and a `low_confidence` boolean. Nothing here is ever
written into reviewed `pwg_ru` data (R5, R17).

- **Marked default — the 0.20 threshold was calibrated on mined running text, not on Vedic:**
  keep 0.20 for the first pass and record the observed distribution in the run log; do not
  silently re-tune. Re-calibration is a separate, evidence-backed step.
- **Marked default — a stanza where the translation has no plausible span:** emit no row rather
  than a low-confidence guess. Absence is a cleaner signal than noise.

## Step 11 — the 300-token gold sample

**Touches:** writes `gold/rv_wordlevel_gold.jsonl`, `gold/rv_wordlevel_precision_report.md`.
**Depends on:** step 10.

Draw 300 tokens stratified by corpus frequency, score precision separately for ru / de / en
(R14). Follow the existing protocol in [`gold/HUMAN_GOLD_PROTOCOL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md).

- **Marked default — precision below 85 % on one or two languages:** ship those languages
  flagged `low_confidence` and exclude them from the contradiction gate; the others proceed.
- **Below 85 % on all three:** stop condition 3 — ship spine A alone and report.

## Step 12 — pipeline bridge: judge witness

**Touches:** the judge prompt-assembly path; `REUSE_MAP.md`.
**Depends on:** steps 9 and 10 (uses whatever is available; degrades to spine-only).

For a headword with an `id_pwg` present in the spine, attach a compact witness block: up to N
example loci with all four renderings. Advisory context, not an instruction to copy.

- **Marked default — N:** 3 loci, chosen by descending corpus frequency of the lemma.

## Step 13 — pipeline bridge: contradiction gate

**Touches:** the audit/gate path alongside the existing gates; `REVIEW_QUEUE_TRIAGE.md`.
**Depends on:** step 12.

If a produced Russian (or English) gloss contradicts **all four** translators at every attested
locus, queue the card for human review. Queue — never reject, never rewrite.

- **Marked default — "contradicts" is not mechanically decidable:** require the gate to fire
  only on the unanimous case, and log near-misses at a lower severity without queueing them.
  A noisy gate gets switched off; a quiet one gets trusted.

## Step 14 — pipeline bridge: the TM tier

**Touches:** `schemas/translation_memory.schema.json`, `src/tm_source_weights.json`,
`LANG_PARITY.md`, the TM build path.
**Depends on:** step 9.

Add `trust_level: "corpus_translation_witness"` with `reuse_policy: "suggest_only"`, and
per-translator weight rows. `lang` is already an enum over `[ru, en]` and the weights file is
keyed by work rather than language, so R7's "not for Russian only" is satisfied by
configuration.

**Mandatory:** classify this change in [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
as SHARED / INTENTIONAL-DIVERGENCE / GAP before calling the step done —
`lang_parity_check.py` fails the suite otherwise, and an unclassified entry is a process defect.

- **Marked default — classification:** SHARED. The tier is language-parameterised by
  construction; if the implementation turns out to force a RU-only path, that is
  INTENTIONAL-DIVERGENCE only with a written why, otherwise it is a GAP with a tracked follow-up.

## Step 15 — wisdomlib, four roles

**Touches:** new `src/rv_wisdomlib_bridge.py`; `REUSE_MAP.md`.
**Depends on:** nothing beyond the on-disk wisdomlib data.

1. **EN gloss tier for PWG→EN** — English term definitions keyed to SLP1, entering the TM as
   `suggest_only` at the same tier as step 14.
2. **Tradition-based sense disambiguation** — `word_traditions.jsonl` narrows which PWG sense is
   live in a given context.
3. **Fifth witness in the contradiction gate** — covers the whole lexicon, not just RV-attested
   headwords, so it is the one witness available outside the Ṛgveda.
4. **AV citation-locus source** — staged for wave 3 as a committed index; no AV work now (R3).

- **Hard constraint:** read only the already-downloaded files. **No network crawl** (R17).
- **Marked default — a wisdomlib entry has no resolvable SLP1 key:** skip it and count it; do
  not transliterate speculatively.

## Step 16 — close-out

**Touches:** `CHANGELOG.md`, `.ai_state.md`, `REUSE_MAP.md`, `RESULTS_LOG.md`.

Run the full existing test suite plus the new tests; `lang_parity_check.py` must pass. Persist
every results table produced (coverage, divergence-class distribution, per-language precision)
to `RESULTS_LOG.md` with date, context and model tier + exact version — a table that exists only
in a chat reply is an unfinished step. Then `[Unreleased]` changelog bullet → `/cut-release` →
commit → PR → merge, and `/artifact-propagate` for the hub sweep.

---

## Parallelism map

Steps 1 and 5 are independent and can run concurrently. Steps 7–9 (typing) and steps 10–11
(alignment) are independent of one another after wave 1a merges. Step 15 is independent of
everything. Step 8 is the only human-blocked step and it blocks step 9 alone — nothing else in
wave 1b waits on it.

_Dr. Mārcis Gasūns_
