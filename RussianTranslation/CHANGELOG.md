# pwg_ru — changelog

How the Russian edition of the Petersburg Dictionary (PWG, Böhtlingk–Roth)
evolved. Newest first. This is the *project* changelog (method + pipeline); the
data stores are gitignored and versioned by their build provenance.

See also: [METHODOLOGY_REVIEW.md](METHODOLOGY_REVIEW.md) (where we want to go),
[failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md) (what went wrong and
how it got better), [APRESJAN.md](APRESJAN.md) (the theory we build on).

## 2026-06-23

### Fixed
- `nws_split.py` OWNER citation now stops at `;` so the trailing-tag
  sub-entry variant (`gloss … <DIATAG> ; SOURCE:page`, e.g. `aYj`) keeps
  only the SOURCE as owner, not the diasystem tag.
- `nws_split.py check` locates card rows on word boundaries instead of raw
  substring, killing a false MISATTRIBUTION where the short Sanskrit
  locator `apāṃ` matched inside the compounds `apāṃpitta`/`apāṃnidhi`
  (the `ap` cross-reference `apāṃ napāt → s.v. napāt` has no card row).
- **Root cause of the `av` `+ upa` owner slide:** `compile_translatable`
  `mask_nws_gloss` now strips the leading owner *bleed*. A roman-numeral
  co-owner cite (`Rivelex (2) : XLV`) that `nws_split`'s digit-only OWNER
  can't tag rode onto the FRONT of the next gloss as `<tag> ; Source :
  page > …`, putting a competing source in the to-translate prose of
  glosses whose deterministic owner was already correct — which led the
  LLM assembly to attribute `+ upa` to Rivelex instead of Geldner. The
  strip fires only on real bleeds (5 `av` glosses) and leaves
  `nws_split.py` itself untouched (parsing the roman co-owner there
  destabilises lemma/gloss alignment).
- Hand-corrected the slid `av` `+ upa` block in the (gitignored) merged
  card to the reading-direction owners (Geldner → Graßmann → NṚV → NṚV →
  Rivelex); all other prefix blocks verified already-correct.

- `nws_split.py` OWNER trailing parenthetical now spans one level of
  nested parens and no longer requires the `s.v.` prefix, so cites like
  `BHSD : 154 (s.v. ekoti -(° tī -) bhūta)`,
  `Olivelle 2015 : 391 (s.v. ṣaḍvidha (- bala))` and bare headword
  variants `MW : 756 (bhā́s)` / `MW : 759 (bhujiṣyà)` resolve their owner
  instead of being dropped. Found by the b-section split-preview audit;
  `selftest` + all 10 a-section checks still CLEAN.
- `scale_route.py` accepts any single-letter section (e.g. `b`), not just
  `a`/`all`, emitting `scale_manifest.<letter>.json`.
- **`nws_split.nws_fragment` no longer swallows the appended owner map.**
  `_pilot_gen_merged.py` writes an authoritative `NWS — PRE-PARSED OWNER
  MAP` layer after the net-new NWS addendum, but `nws_fragment` captured
  `(.*)\Z` from the first `=== LAYER: NWS` marker to EOF, so on any
  owner-map input it re-parsed that map as source content — corrupting
  `split()`, the F12 gate (`check`) and `compile_translatable` (the
  d-section first showed 1,380 phantom empty-gloss + 33 phantom no-owner
  entries). It now captures only up to the next `=== LAYER:` marker and
  skips the `PRE-PARSED` header. Found while auditing the d-section (first
  section generated with the owner-map injection); `selftest` + all 10
  a-section checks still CLEAN, `compile_translatable('day')` → 7 clean
  units, 0 map artifacts.
- **`nws_owner_map` debleeds the injected owner map.** The roman co-owner
  bleed (e.g. `Hillebrandt 1885 : IV`) that `compile_translatable` already
  strips also contaminated the appended `PRE-PARSED OWNER MAP`: `split`'s
  `lemma_tag` scatters the bled segment into an entry's leading gloss, its
  tag (stray `; Name : page`) and a punctuation-only lemma (`{#,#}`). The
  owner stays correct, so this is cosmetic for what the translator reads.
  `nws_owner_map` now strips the leading-bleed from the gloss, removes a
  bled-in `Name : page` cite from the tag, and drops punct-only lemmas
  (mirrors `mask_nws_gloss`). The owner field is never touched; clean
  sections are no-ops. Found in the g-section (`gam`).

### Added
- `run_real_test.py audit` is now a true **NWS attribution gate**: a fresh
  (non-protected) card whose NWS owners disagree with the deterministic
  `nws_split` parse is rejected — its `<safe>.merged.md` is moved to
  `<safe>.merged.REJECTED.md` so the next `prep` re-queues it — and the
  command exits non-zero. Protected hand-authored cards are audited but
  never quarantined. Verified end-to-end (slid card → FAIL → quarantined →
  exit 1; clean card → PASS → exit 0). `selftest` + all 10 audited keys
  CLEAN.

### Audited
- **Full b-section deterministic split-preview** (all 4,613 b-keys → 971
  NWS-bearing, 2,655 entries): **0 roman-cite bleeds** — the `av`-class
  F12 owner slide does not occur anywhere in the b-section. After the
  trailer-paren fix above, only 11 entries are unowned: 4 benign
  empty-segments + 7 real losses confined to the two known-limitation
  sources below.
- **Full c-section deterministic split-preview** (all 2,366 c-keys → 719
  NWS-bearing, 1,828 entries): **0 roman-cite bleeds**. 17 unowned = 8
  benign empty-segments + 9 real losses, all in the known-limitation
  sources below (8 × Meister `(2.1)`, 1 × Böhtlingk `*NNN`).
- **Full d-section deterministic split-preview** (all 6,019 d-keys → 1,439
  NWS-bearing, 3,808 entries): **0 roman-cite bleeds**. First section
  generated with the owner-map injection, which surfaced the
  `nws_fragment` over-capture bug fixed above; after that fix only 4
  entries (0.10%) are real losses — one each Meister `(2.1)`, roman page,
  Böhtlingk `*NNN`, plus one page-less cross-reference
  (`duHzvapnya → s.v. duṣvápnya (Graßmann 1873 (1996))`, no `: page` to
  parse). The 14 remaining unowned are benign empty terminal segments.
- **Full e-section deterministic split-preview** (all 663 e-keys → 203
  NWS-bearing, 470 entries): **0 roman-cite bleeds**, cleanest section so
  far. 3 unowned = 2 benign empty + 1 page-less cross-reference
  (`eta → s.v. éta . Rivelex (2) (s.v. éta)`, no `: page` to parse); none
  of the Meister/roman/Böhtlingk classes appear. Cross-checked against the
  injected owner map: 470 map entries with exactly 3 `[NWS: ?]`, matching
  the split-preview one-for-one — confirming the `nws_fragment` fix and
  owner-map generation are consistent. The page-less cross-reference (no
  `Name : page` cite exists) is a recurring benign category, not a parser
  gap — it also appears once in d (`duHzvapnya`).
- **Full f-section deterministic split-preview** (all 339 f-keys [SLP1 `f`
  = ṛ] → 156 NWS-bearing, 502 entries): **0 roman-cite bleeds, 0 real
  losses** — the only unowned entry is a benign empty terminal segment, no
  Meister/roman/Böhtlingk/page-less cases. Owner-map cross-check: 502 map
  entries, exactly 1 `[NWS: ?]`, matching the split-preview one-for-one.
- **Full g-section deterministic split-preview** (all 3,354 g-keys → 974
  NWS-bearing, 2,866 entries): **2 roman-cite bleeds** (both `gam`,
  `Hillebrandt 1885 : IV`) — the first bleeds since the a-section; the
  owner stays correct (`Geldner 1907 : 52`), and the cosmetic owner-map
  contamination is fixed by the `nws_owner_map` debleed above. 9 unowned =
  8 benign empty + 1 Meister `(2.1)` (0.03% real loss). Owner-map
  cross-check: 2,866 entries, 9 `[NWS: ?]`, matching the split-preview.
- **Full h-section deterministic split-preview** (all 2,027 h-keys → 466
  NWS-bearing, 1,353 entries): **0 roman-cite bleeds**. 10 unowned = 8
  benign empty + 2 real (1 Meister `(2.1)`, 1 page-less cross-reference
  `hriRIy → s.v. hṛṇīy (TŚPC 3)`, no `: page`) = 0.15%. Owner-map
  cross-check: 1,353 entries, 10 `[NWS: ?]`, matching the split-preview,
  and **0 inputs with residual contamination** — confirming the
  `nws_owner_map` debleed produces clean maps on fresh generation.

### Known limitations
- **`Meister 1988 (2.1) : 397`** — a source name carrying a `.` *inside* a
  parenthetical volume number (`(2.1)`) is not recognized as an owner,
  because OWNER's name class excludes `.` on purpose (to stop names like
  `Hoernle 1893-1912 (II) 30.81` / `EI Vol. XV` from swallowing whole
  sentences — guarded by the `aMSa` selftest). Drops 4 b-section owners
  (`BadrapIWa`, `boDimaRqa`, `BadraraTa`, `BUmiKaRqa`).
- **`Walter 1893 : XXXII`** — a roman-numeral page is not matched, because
  OWNER's page is digit-only. Admitting roman pages globally is what
  destabilised the parser earlier (it turns co-owner segments into
  gloss-closers → lemma-stuffing) and was reverted, so it stays out.
  Drops 3 b-section owners (`brahmagranTi`, `brahmaranDra`, `brahmadvAra`).
- **`Böhtlingk 1887 : *163`** — an asterisk-prefixed page is not matched,
  because OWNER's page is digit-only. Extending it to `\*?\d+` was tried
  and reverted: like roman pages, admitting `*NNN` turns segments such as
  `Böhtlingk 1887 : *150 >` into gloss-closers and regressed `ap`/`av` to
  MISATTRIBUTION. Drops 1 c-section owner (`ci`).
- These are rare (b: 7 / 2,655 = 0.26%; c: 9 / 1,828 = 0.49%), terminal,
  and confined to a few works (Meister 1988, Walter 1893, Böhtlingk 1887);
  the safely-fixable nested/variant-paren gap is already fixed. Roman and
  asterisk pages share one cause — admitting them as page tokens
  destabilises segment/owner alignment — so both stay out by design.

## 2026-06-20

### Added
- `schemas/pwg_ru_final_card.schema.json` and
  `validate_final_card_schema.py` define the final translated-card + judge
  contract, including auditable Apresjan `differentia` evidence.
- `validate_assembled_export.py` checks deterministic assembled-card JSONL
  exports, with full count-match mode and bounded supervised-sample mode.
- `run_batch.py validate_review` and `run_batch.py apply_review` make the
  review store gate machine-checkable before any row can become print-ready.
- `gold_validate.py`, `gold_ingest.py`, and `gold_agreement.py` validate human
  gold labels, ingest release-bound JSONL, and compute Wilson precision plus
  double-review agreement metrics.
- `export_interop.py` and `validate_interop.py` generate and validate minimal
  TEI Lex-0, OntoLex, and Russian reverse-index artifacts.
- `make_edition_cut.py`, `validate_release.py`, `CITATION.cff`, and
  `DOI_PLAN.md` add the immutable edition-cut skeleton and manifest hash check.
- Nonhuman print-gate helper tooling now prepares reviewer work without filling
  human decisions: `run_batch.py review_report`, `gold_status.py`,
  `gold_packet.py`, `gold_double_review_queue.py`, and `release_readiness.py`.
- `gold/REVIEWER_HANDOFF.md` gives reviewers one place for allowed enum values,
  protected columns, validation commands, and the G5-G7 handoff flow.
- `gold_packet_verify.py`, `gold_double_review_verify.py`, and
  `preflight_remaining_gates.py` verify reviewer packets, second-review queues,
  and the compact "what's left?" status without inferring any human labels.
- `gold_ingest_double_review.py` bridges filled wide double-review queues into
  long-form reviewer JSONL that `gold_agreement.py` can score.
- Review-gate fixture coverage now exercises blank decisions, invalid approvals,
  explicit `apply_review`, and fail-closed interop export without touching the
  real local translation store.

### Changed
- `assemble.py build` now writes to temp files and installs outputs only after
  successful completion, protecting `assembled_cards.jsonl` from killed-run
  corruption.
- Failed atomic replacement now leaves the previous assembled export untouched
  and keeps the temp file for manual recovery instead of unlinking the old file.
- `assemble.py build` now precomputes corpus evidence once per build, uses
  `corpus_lexicon.jsonl` rows for export-time examples instead of per-card
  SQLite FTS, and supports grouped-card chunks via `--offset`, `--out`, and
  `--quarantine`.
- The top-level AI/release status now says the core release machinery is ready
  but print remains blocked by human review, human gold labels, double-review
  agreement, and a real immutable edition cut.
- `roadmap_check.py` now detects gate status drift between the aggregate
  scientific-hardening JSON and the JSONL gate ledger.
- Release manifest validation now rejects missing/null gate status maps and
  checks manifest gate statuses against the edition's copied gate ledger.
- The monorepo CI/local fixture checks now exercise final-card schemas,
  gold-label packets, double-review queues, interop fixture exports, and a
  fixture edition cut without requiring local gitignored production data.
- `run_batch.py` and `release_readiness.py` accept `PWG_RU_STORE`,
  `PWG_RU_REVIEW_Q`, `PWG_RU_REVIEW_CSV`, and `PWG_RU_REVIEW_REPORT` path
  overrides so review-gate tests can run against disposable fixture stores.
- Full interop export now validates: `release/tei_lex0.xml` and
  `release/ontolex.ttl` each cover 120,173 lexical entries, and
  `release/reverse_index.jsonl` has 209,319 Russian-to-Sanskrit rows.

## 2026-06-19

### Added
- Machine-readable scientific-hardening roadmap and print-blocking quality gates:
  `roadmap/scientific_hardening.json`, `roadmap/quality_gates.jsonl`, and
  `src/roadmap_check.py`.
- `src/pilot/run_real_test.py` audit preflight was exercised with a synthetic
  `ap` workflow output, proving the collect → protected-card preservation →
  `nws_split.py check` → report path before the June-22 Max run.
- `run_batch.py review_csv` exports `_review_queue.jsonl` to a spreadsheet-ready
  `_review_queue.csv` with blank human-review columns (`reviewer_id`, `decision`,
  `edit`, `notes`) while leaving review state unchanged.
- `gold/HUMAN_GOLD_PROTOCOL.md` defines the human gold-set labeling protocol,
  double-review/adjudication workflow, and acceptance criteria; `gold_review_csv.py`
  exports the existing 320-row balanced scaffold for reviewers.
- `schemas/pwg_ru_lexicographic_portrait.schema.json` and
  `validate_portrait_schema.py` define and check the v1 Apresjan portrait
  contract for live `microstructure.portrait()` output.

### Changed
- Modern Sanskrit-Russian sources with project approvals are now marked
  publishable with attribution/provenance, not evidence-only; see
  [RIGHTS_APPROVALS.md](RIGHTS_APPROVALS.md).
- Shared the case-collision-safe filename encoder across NWS scrape/split/audit,
  pilot generation, and merge lookup; forbidden Windows filename characters are
  escaped reversibly.
- `_pilot_collect.py` now writes audited `<safe>.merged.md` files directly using
  `safe_name()`; the real-test auditor no longer needs a brittle external
  `<key>.md` copy bridge and uses the same filename encoder as the rest of the
  pipeline.
- `run_real_test.py prep` was refreshed for the June-22 batch window
  (`OFFSET=0`, `LIMIT=10`): `as As Ap api amfta agni Atman anu arjuna arTa`,
  now correctly all fresh after exact-case output checks.
- `run_pilot_wf.js` now loads the canonical final-card schema instead of
  carrying a prompt-local schema copy.

### Fixed
- Corpus harvest no longer lemmatizes Sanskrit proper names such as `Агни` to
  unrelated Russian verbs such as `агнуть`.
- `scale_route.py` now routes by the protected microstructure sense parser.
- `assemble.py` quarantines lossy round-trip records instead of emitting them
  into the normal assembled card stream.
- `run_batch.py migrate_legacy` backfills old translation-store rows and marks
  unverifiable legacy cards `legacy_needs_review`.
- Protected hand-authored pilot cards (`aMSa`, `anna`, `ap`) are preserved during
  real-test collection/audit, while still being audited by `nws_split.py`.
- Legacy `.merged.md` compatibility checks now require exact filenames, avoiding
  Windows case-insensitive false positives such as `Ap` being treated as protected
  because `ap.merged.md` exists.
- Generated the missing writable a-section input for `arI|a` (`|` escaped as
  `~007c`); pilot inputs now cover 12,156/12,156 a-section manifest cards.
- Materialized the human review worklist with `run_batch.py review`: 217
  `legacy_needs_review` cards, severity-sorted, with no reviewer decisions
  advanced.

## 2026-06-16

### Added
- **Corpus harvest layer** ([HARVEST.md](HARVEST.md)): `build_ls_map.py` +
  `ls_source_map.json` (PWG `<ls>`→stratum, 45 sources = 72.4% of 772k
  citations, 29.8% corpus-harvestable) and `corpus_harvest.py` — SLP1 key →
  Russian renderings, lemma-grouped (pymorphy3), POS-filtered, stratified, with
  the `<ls>`-cited stratum first and a `--raw` escape for particle headwords.
- **Recurring deterministic integrity auditor** (`_audit.py`): flags
  placeholder leak / non-Cyrillic / `ru==sa` / `√`-keys / dups / stratum
  mismatch; run at each build milestone; exit-code verdict.
- **Live cost/ETA watcher** (`_watch.py`): progress bar, $ spent / needed, ETA,
  measured over a live window (not the append-only file's stale ctime).
- **Methodology review** ([METHODOLOGY_REVIEW.md](METHODOLOGY_REVIEW.md)):
  grounded 5-lens review (FAIR/DH, bilingual lexicography, corpus-NLP eval,
  standards/interop, editorial) → prioritized roadmap.
- **Priority-1 fixes**: per-card **provenance** (model ids, prompt hash,
  `pwg.txt` commit, run id, timestamp + persisted senses); **human-review state
  machine** + `run_batch.py review` editor worklist; **per-sense rights gate**
  (`corpus_gate.RIGHTS`/`publishable()`) + **CC BY-SA 4.0** data licence
  ([DATA_LICENSE.md](DATA_LICENSE.md)).
- **Coverage honesty check** (`corpus_harvest.py coverage`): per-stratum rows /
  groups-done flags EMPTY/thin strata.
- **Apresjan theoretical grounding** ([APRESJAN.md](APRESJAN.md)) and a
  **failure gallery** ([failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md)).

### Changed
- Corpus-lexicon build **batched** (~8 verse-units / DeepSeek call, 12 workers,
  biggest-first); quality verified equal to single-call, ~3–4× faster.
- `build_strata.count_groups()` now requires a Cyrillic translation, so sizes /
  ordering reflect genuinely-translated material (78,139 → 58,897 genuine groups).

### Fixed
- **Placeholder fabrication (build-stopping)**: untranslated `…` verses were fed
  to DeepSeek, which hallucinated 166k/204k rows (81%). Fixed with a Cyrillic
  guard; recovered to 26,277 genuine rows. See the gallery.
- Footnote-overwrites-translation; `√` leaking into keys; commentary
  cross-segment duplication; biggest-first cost mis-projection; frozen/dead-build
  liveness misreads. See [failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md).

## 2026-06-15

### Added
- **Source extraction** (`build_src.py`): 5 Sanskrit–Russian dictionaries
  (Кочергина, Кнауэр, Фриш, Смирнов, Коссович) pulled from SamudraManthanam →
  gitignored `src/*.jsonl` (~57,640 keyed entries).
- **Stage-4 corpus gate** (`corpus_gate.py`): SLP1 join over the 5 dicts + the
  parallel-corpus query; non-blocking 2-signal annotation (correctness vs
  independent dicts; reference-agreement vs KOW). Coverage measured honestly
  (correctness 16.4% / KOW 8.0% / corpus ~14–15%; dominant `no-check`).
- **Pipeline** (`pwg_mask.py` masker, `assemble.py` harvest, `run_batch.py`
  driver): mask German skeleton → harvest attested senses → translate (Sonnet
  4.6 on Max) → judge (Opus 4.8) → re-translate. Pilot: 6/6 then ~88–95%
  first-pass publishable.
- **Stratification** (`build_strata.py` + `corpus_strata.json`): 121 corpus
  texts by genre (Renou) + date (Dharmamitra Gibbs median + 95% CI) + period.

### Changed
- Strategy pivots: **harvest-first** (assemble Russian from existing material;
  harvested meanings become additional *attested senses*), then **corpus-first**
  (build the corpus word-alignment lexicon before bulk translation), then
  **quality-over-quantity** (it becomes a printed scholarly dictionary).

## 2026-06-14

### Added
- **pwg_ru kit scaffolded** (committed `384fedb`), mirroring the completed
  `mw_ru`: editor doc [pwg_ru.md](pwg_ru.md) + stage prompts
  ([pwg_ru_prompts/](pwg_ru_prompts/)) (translate → 2 QA judges → re-translate →
  corpus check). Headline format rule: PWG `{%…%}` wraps both German glosses
  (translate) and Latin (leave). Model unified to Opus 4.8.
