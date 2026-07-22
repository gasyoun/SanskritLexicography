# Changelog

All notable changes to SanskritLexicography are documented here.

Entries use dated, versioned releases. Keep upcoming work under [Unreleased],
then **cut a new version every time the changelog is updated** (promote
[Unreleased] to the next `x.y.z` with today's date and start a fresh
[Unreleased]).

Historical note on the version sequence: 1.0.0–1.1.3 were cut mid-June 2026, the
lane then dropped to 0.0.1–0.0.42 snapshot tags (18-06 … 02-07) before resuming
at 1.1.4 on 03-07 — the dip is baked into the published tags and is intentional,
not an error.

## [Unreleased]

## [1.54.0] — 22-07-2026

### Fixed

- pwg_ru post-H1339 review landing set
  ([H1386](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1386-Fable_RussianTranslation_pwg-ru-post-h1339-resume-fixes-prepare-speed_20.07.26.md),
  Fable 5 `claude-fable-5`), every fix test-first with a pinned failing regression. Confirmed
  P1s: C1 — bounded `--resume` passed the staged-plan-scope **dict** to `cmd_recover`, so
  crash recovery matched ZERO jobs and a crashed window checkpointed COMPLETED with zero
  output (now the lease-id set; `_scope_sql` rejects dict/str; a None-output window fails
  loudly); C2 — a requeue item whose origin lease had already recorded/promoted wedged every
  `--resume` in `materialize_requeue` (post-audit states with a completed `::rq` job now
  resume to the existing attempt job); C3 — the B12 fragment unblock re-served gate-flagged
  senses: `build_frags` now treats a currently-denied fsha as not-cached, the harvest glob is
  recursive (`artifacts/**`) so requeue outputs two dirs deep are harvested at all, and
  `best_reusable` breaks same-second ties toward the newer row. Also: D2 identity-checked
  atomic-rename promote-lock reclaim (TOCTOU), D3 per-lease `store_delta` from the batch
  report (was bundle-wide stamped N times), D4 `PWG_COORDINATOR_DIR` injected into all three
  bounded coordinator subprocesses (the A7 class), D5 `--batch-manifest` refuses
  `--dry-run`/`--force`/`--init-store` instead of silently mutating the store, and the P3
  sweep (P3b canonical `mw_en_tm` resolution, P3c `reset-failed` origin-lease matching +
  full failed-job ids in fail-closed messages, P3d/P3e `run_py_inproc` KeyboardInterrupt +
  string-exit semantics, P3g batch null-subcard gate, P3h stale_check v2
  execution/provenance cross-check, P3j `probe_log` falsy-zero clean recovery).

### Added

- pwg_ru medium50 start-today enabler (H1386 D1): h1209 payload v3 hoists the shared ~12 KB
  preamble/translation boilerplate into ONE `prompt_common` (was duplicated into every
  card), `inject_payload.py` hard-refuses an emitted script over `WORKFLOW_SCRIPT_CAP`
  (512 KB) with the split remedy, `prep_slice.py --keys`/`--chunk N` auto-splits a big
  manifest into cap-sized sub-payloads, and `canonical_audit.py` merges several chunk
  slice_results into one audit.
- pwg_ru prepare-stage batching (H1386 OPT): `coordinator prepare-batch` prepares N claimed
  leases in ONE coordinator process with the perf_preflight/gen_opt_harness2 children run
  in-process (the H1339 runpy-gates pattern applied to the prepare stage H1339's closeout
  named as the remaining dominant spawn cost), A/B-benched against the per-lease shape with
  semantic-store-equality proven by the bench's deterministic signature.
- pwg_ru hermetic offline bench (H1386 P3f): `h1339_offline_bench.py` now sandboxes its
  fixture inputs (`PWG_INPUT_DIR`, honored by all 14 previously hand-copied input-dir
  sites) and its events ledger (`PWG_EVENTS_PATH`), with a `finally:` teardown — a bench
  run leaves the checkout byte-identical (previously it froze 12 fixture bodies into the
  live `src/pilot/input/` and appended to the live `dashboard_events.jsonl`).
## [1.53.0] — 22-07-2026

### Added

- [`LINK_CHECK_BASELINE_2026H2.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/LINK_CHECK_BASELINE_2026H2.md)
  ([H741](https://github.com/gasyoun/Uprava/blob/main/handoffs/H741-Fable_SanskritLexicography_repo-wide-dead-link-sweep_11.07.26.md),
  Fable 5 `claude-fable-5`): the stated baseline the weekly link-check job is judged against —
  full-repo measurement 16,861 unique dead links (15,919 in `literature/md/` ebook conversions,
  942 in real project surface) drained to **73 accepted survivors in 21 files** (goal <100);
  survivor classes, ignore-list rationale, and path-exclusion rulings documented per row.

### Changed

- Weekly [link-check workflow](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/link-check.yml)
  rebuilt (H741): explicit find-based `markdown-link-check@3.14.2` invocation excluding
  `literature/md/**` (third-party book texts, H734 territory) and `docs_site/wiki/**`
  (build_site `--sync` copies); [`mlc_config.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/mlc_config.json)
  gains ignore patterns for the 11 private `gasyoun/*` repos (unauthenticated-404-by-design),
  `mailto:`, DOI resolvers, bot-blocking publishers, and flaky project-adjacent academic hosts;
  `aliveStatusCodes` gains 202.

### Fixed

- 62 CI-visible dead links across 31 files
  ([PR #666](https://github.com/gasyoun/SanskritLexicography/pull/666), H741 bucket A):
  archive-move relative links → full blob URLs; gitignored-by-design targets delinked;
  PR #540-deleted gloss-reviews → pinned pre-deletion SHAs; wrong-owner GitHub URLs
  (csl-atlas / csl-observatory / csl-standards / sanskrit-util / MWS → `sanskrit-lexicon`;
  SanskritSpellCheck / kosha / WhitneyRoots → `gasyoun`); Wikipedia/TMX/archive.org 404s
  repointed to verified targets; two broken in-file anchors.

## [1.52.0] — 21-07-2026

### Added

- **Restored the nine Russian/Soviet full-text conversions removed by [PR #481](https://github.com/gasyoun/SanskritLexicography/pull/481).** Owner ruling on the [Uprava weekly @DECIDE sheet 20-07-2026](https://github.com/gasyoun/Uprava/blob/main/review/weekly/archive/uprava-weekly-decide_20-07-2026_review.html): «bring back, I take the risk» — the copyright risk is explicitly accepted, consistent with the same-day rulings that kept Kumar 1976 + Meenakshi 1983 and left the ~30-work Western academic-press cluster on tip. Files recovered from `68a88c94^` and verified byte-identical to their pre-removal state: four under `literature/md/Вспомогательное/` (Zaliznyak & Paducheva 1975, Jakobson 1987, Mitrenina 2008 + 2010) and five under `literature/md/Общий синтаксис/` (Kibrik et al. 2020, Entsiklopedicheskiy slovar 1984, Testelets, Lomov, Sintaksis-2009). The nine `*_DIGEST.md` files added at removal time are **kept** — they now sit beside their full texts rather than standing in for them. `.gitignore` unchanged (PR #481 touched only a comment there; `!literature/md` still stands); both READMEs corrected — `Вспомогательное/` 15 → 19 files, `Общий синтаксис/` 6 → 11, total referenced 67 → 76.

## [1.51.0] — 21-07-2026

### Added

- pwg_ru abbreviation ↔ ЛЭС-1990 comparison layer: standalone [`pwg_ru/ABBREV_LES1990_SRAVNENIE_2026-07.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ABBREV_LES1990_SRAVNENIE_2026-07.md)
  plus a summary врезка in [`pwg_ru/ABBREV_UNIFIED_LIST_PROPOSAL_2026-07.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ABBREV_UNIFIED_LIST_PROPOSAL_2026-07.md)
  (Opus 4.8 `claude-opus-4-8`, `/ask`): benchmarks the 269-token unified list against the
  «Список основных сокращений» of the Linguistic Encyclopedic Dictionary (ЛЭС, ed. В. Н. Ярцева,
  1990). 24 tokens match ЛЭС verbatim (см./ср./напр./изд./ред. + the case Latinisms
  акк./ген./абл./лок.); the Sanskrit verbal apparatus (аорист/каузатив/медий) lies outside ЛЭС
  jurisdiction (там эталон — классическая индоевропеистика); jurisdictional divergences (spacing
  «т. е.», ед.→ед. ч., стр.→с., дат.→дат. п., герунд.→абс.) parked as a non-binding
  harmonization-candidate list — voted H1303 tables untouched.
- A30 hostile referee pass ([H1382](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1382-Fable_SanskritLexicography_a30-hostile-referee-pass-skd-vcp_20.07.26.md),
  Fable 5 `claude-fable-5`): [`papers/A30_review_fable5.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_review_fable5.md)
  — verdict **major revision, 4/5 gate not cleared as drafted**; C1–C4/C6 CONFIRMED (the
  53.3 %/77.6 % *iti*-fusion contrast rests on a classifier with three artifact classes
  visible in its own committed sample — severed sandhi citations, a 16-name recall ceiling,
  formula false-positives — and §7's "fewer, longer" VCP claim is contradicted by the
  corpus's committed length stats), C5 downgraded to CLEAN, C7 re-derived CLEAN; every §1–§5
  figure verified exact against csl-atlas `origin/main`. Includes the edition-facts check
  (SKD "from 1822" → corrected 1821/22–1858; VCP 1873–1884 confirmed).
- SKD *iti* adjudication sample, model pass ([`papers/A30_SKD_ITI_ADJUDICATION_MODEL_PASS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_SKD_ITI_ADJUDICATION_MODEL_PASS.md)):
  102 rows labelled citational 81 / grammatical 6 / unclear 15 — explicitly **not** the human
  gold (that gate stays open); sheet-readiness defects reported (severed-before-name rows,
  missing post-stratification weights).

## [1.50.0] — 21-07-2026

### Added

- pwg_ru style-research memo [`pwg_ru/STYLE_RESEARCH_DOUBLETS_VL_COMP.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/STYLE_RESEARCH_DOUBLETS_VL_COMP.md)
  ([H1306](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md)
  phase 1, Fable 5 `claude-fable-5`): doublet-gloss policy grounded in Апресян 1995 (с. 95, 218,
  verified verbatim) + Берков 2004 «синонимит» (с. 149–153) + Щерба 1940; `v. l.` ruling with the
  Дворецкий abbreviation-list precedent (verbatim) vs the dead prompt rule (0/252 store cards obey
  it); the *im Comp., vorangehend* formula measured at ~2.1k corpus-wide (not "tens of thousands");
  KATHĀS. 26,9 attested-citation arbiter worked example via SamudraManthanam (Серебряков). 9-card
  ratification sheet `review/h1306_style_sheet.html` (`sheet_id h1306_style`, csl-pyutil 0.3.1,
  local-only + gitignored) awaits MG's vote → `pwg_ru/eval/h1306_style.decisions.json`.

- FINDINGS §459 (csl-atlas H1423, [PR #290](https://github.com/sanskrit-lexicon/csl-atlas/pull/290)):
  PWG's entry-size decay is a **smooth funding/energy fade** across its whole 20-year run
  (−14 %/decade; vols 2–7 still −15 %/decade after dropping the over-detailed vol-1) — settling the
  §458 cause question — measured by mapping all 123,366 PWG entries to a real publication year via
  the `<pc>`→volume→year field. Plus the reusable gotcha that cross-dictionary markup-density
  measures the *digitisation apparatus*, not lexicographic depth (SKD/VCP carry ~0 Cologne markup).

## [1.48.0] — 21-07-2026

### Fixed
- **H1397 — reattached FINDINGS §456's orphaned body + regenerated stale dashboards.** The 20-07-2026 §102→§456 collision fix ([PR #618](https://github.com/gasyoun/SanskritLexicography/pull/618), issue #624) moved only §456's header + tombstone note, leaving the actual finding body (H1328's uttarapada dict-vs-corpus Jaccard analysis) orphaned as headerless text between §457 and §458 — invisible to `epistemic_integrity_check.py`'s heading scan but genuine duplicate/dead content. Moved the body back under its own §456 header (pure relocation, no content change); regenerated `findings_dashboard/data.json`/`timeseries.json` and `epistemic_dashboard/epistemic.json` (stale 115/116 headings before this fix). `epistemic_integrity_check.py --dir .` now reports full `OK`. ([SanskritLexicography PR #642](https://github.com/gasyoun/SanskritLexicography/pull/642), Sonnet 5 `claude-sonnet-5`)

## [1.47.0] — 21-07-2026

### Fixed — PWG→RU/EN pipeline bug-hunt: all 9 confirmed findings (C1–C9)

- An Opus 4.8 (`claude-opus-4-8`) adversarial code review of the pwg_ru translation pipeline (9
  finder groups + per-finding verification) surfaced 9 confirmed bugs, all now fixed and merged
  ([issue #632](https://github.com/gasyoun/SanskritLexicography/issues/632); component-level detail
  in [`RussianTranslation/CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md)):
  - **C1** (subsumes C5) — the `<ls>`/`{#..#}` markup-fidelity guard only checked the German
    source-echo on every lane except the JS batch `accept()`; ported the target-language-field
    check to the heal/presplit, headless `normalize_batch` (production route), and autosplit stitch
    lanes, so a translation faithful in German but missing a Sanskrit/citation span in the
    Russian/English column can no longer be promoted silently ([PR #638](https://github.com/gasyoun/SanskritLexicography/pull/638)).
  - **C2** — the EN `DUP` gate keyed on `prose()` (which strips `{#..#}`), false-flagging distinct
    proper-name senses (310 real cases); now keys on the raw english. **C6** — the EN promote lane
    gained the RU lane's unrestored-`{Tn}` refusal ([PR #634](https://github.com/gasyoun/SanskritLexicography/pull/634)).
  - **C3** — EN card-TM was written under the store column `en` instead of the card field
    `english`, so 100 % of EN card-TM hits were silently refused. **C4** — a rate-limited job never
    got its attempt back, permanently stranding it and busy-looping `staged-run` ([PR #636](https://github.com/gasyoun/SanskritLexicography/pull/636)/[#637](https://github.com/gasyoun/SanskritLexicography/pull/637)).
  - **C7** — `build-frags` built the fragment TM from the default tree, ignoring
    `PWG_COORDINATOR_DIR`. **C8** — German glosses opening `In…`/`Ab…` were masked as Latin and
    dropped (1 of 192,763 spans). **C9** — the EN store backup could clobber a same-second recovery
    copy; now µs+pid+uuid + O_EXCL ([PR #640](https://github.com/gasyoun/SanskritLexicography/pull/640)).

### Added

- FINDINGS §458 (H1416, [csl-atlas PR #282](https://github.com/sanskrit-lexicon/csl-atlas/pull/282)):
  the per-letter law — a Sanskrit dictionary's big letters (`a`, `u`, `p`, `s`, `v`) are big
  because they head **preverb families**, so `a`'s 83.1 % compound share is not unique; plus the
  reusable methodological gotcha that testing "entries shrink over serial publication" needs an
  outlier-robust per-letter rank estimator (encyclopedic SKD/VCP have single 300k-char articles
  that give a parametric regression a spurious +733 % slope). Funding-decay hypothesis **refuted
  for SKD/VCP**, real in PWG/PWK/GRA.

- **H803 CLOSED: LaukikaNyaya reaches its ≥400-record target, 404 records (Sonnet 5 `claude-sonnet-5`, picked up via `/next-task`).** Implements the `prev_is_prose()` pipeline-wide fix [`LaukikaNyaya/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/README.md)'s 20-07-2026 pass had explicitly deferred (verification cost). Root cause: the heuristic rejected any index-crossref candidate whose preceding line was heavy Devanagari, conflating "sits mid-citation" with "immediately follows a different entry's own closing verse." Fix: only reject when that preceding line does NOT itself close with a verse-final daṇḍa/double-daṇḍa. Re-running the fixed pipeline recovers 27 more headword boundaries (base lane 302 → 329) with **zero records lost** (verified by diffing the full boundary set before/after). Because Sanskrit verse padas commonly end in a daṇḍa even mid-citation, every one of the 18 brand-new candidates beyond the known-12 was independently checked by a 2-stage adversarial review (1 initial classifier + 2 skeptic/refuters per GENUINE verdict, 50 agent calls, Sonnet 5 `claude-sonnet-5` ultracode workflow) against the raw OCR context, the book's own back-matter index, and the committed dataset: 15 confirmed genuine (previously swallowed verbatim into the preceding entry's runaway explanation field), 3 rejected as duplicates of content already present under a different OCR lane/spelling. Combined with the 3 of the original hand-verified 12 the fix still can't auto-recover (kept as a documented manual addition), the corrected 329-record base lane reconciles against the unchanged 301-record clean-scan lane to **404 records**, crossing the ≥400 Definition-of-Done target for the first time. New [`LaukikaNyaya/tools/apply_h803_followup2_prevprose_fix.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/tools/apply_h803_followup2_prevprose_fix.py) documents the exclusions/additions. Registered as [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) F45 — closes the last open deliverable of the 2004 AIOC-Varanasi manifesto («Сентенции и афористические цитаты»).

## [1.46.0] — 20-07-2026

### Added

- **PWG→RU speed & orchestration audit — bottleneck ledger + adversarially verified action map (H1403, Fable 5 `claude-fable-5`, 22-agent ultracode workflow).** [`RussianTranslation/PWG_RU_SPEED_ORCHESTRATION_BOTTLENECK_AUDIT_2026-07-20.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_RU_SPEED_ORCHESTRATION_BOTTLENECK_AUDIT_2026-07-20.md): 5 subsystem miners → synthesis → two adversarial lenses per recommendation. Headline: **0/8 synthesized recommendations survived unmodified (6 weakened, 2 refuted)** — dominant reason "already shipped or already minted", i.e. the speed frontier is executing queued work (H1209 medium50, H390 rule 4(a) instrumentation, three operator-loop residues), not new mechanisms. Ledger top-3: transport availability (6 days at 0 promoted cards with the validated controller-worker lane parked), operator serial loop (generation only ~12–22 % of chain calendar), and the blended clean-rate metric hiding content-clean ~83 % vs transport yield. Also registers the H1225 SANLOSS counter-fix escalation as [`DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §12 — the audit's own synthesis re-proposed that disproven fix, proving the registry gap's cost live — and lands the missing §11 (H1349 W3 vidyut-cheda NO-GO), which `.ai_state.md` referenced but never wrote.

## [1.45.0] — 20-07-2026

### Fixed
- **§102 duplicate-heading collision resolved — the new integrity gate's first live catch (Opus 4.8 `claude-opus-4-8`).** [PR #618](https://github.com/gasyoun/SanskritLexicography/pull/618) (H1328, MW uttarapada × DCS Kompozity divergence) appended a **second** `### §102`, colliding with the incumbent DCS `text_sandhied` §102 and turning the epistemic-integrity gate red on `master` — caught the moment the [v1.44.0 gate](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/epistemic-integrity.yml) went live ([issue #624](https://github.com/gasyoun/SanskritLexicography/issues/624)). Per the [citation-identity ruling](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md) rule 4 the later claim moves: the H1328 finding renumbered **§102 → §456** (tombstone + Index entry 🟠), marker → §457. Regenerated `verifiability.json` (114 findings: A 95 · B 12 · C 4 · D 3), STALENESS (114 rows), and both dashboards; integrity gate green.

## [1.44.0] — 20-07-2026

### Added
- **H1362 follow-up: epistemic-integrity gate now runs on every PR + push to master (Opus 4.8 `claude-opus-4-8`).** New [`.github/workflows/epistemic-integrity.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/epistemic-integrity.yml) runs `tools/epistemic_integrity_check.py --structural-only` on any PR touching the registries/dashboards **and** on every push to `master`, opening a tracking issue if `master` ever goes red. Before this the check ran only from the monthly `findings-dashboard` workflow + the local pre-commit hook — which is exactly why the concurrent H1350×H1361 §448–451 collision could merge through two isolated-green PRs and sit red on `master` until noticed. Closes the residual follow-up from the [citation-identity ruling](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md) §6.

## [1.43.0] — 20-07-2026

### Added
- **H803 LaukikaNyaya: newly-discovered back-matter index cross-referenced, 377 → 389 records (Sonnet 5 `claude-sonnet-5`).** The `handfulofpopular03jacoiala` clean-scan source turns out to carry its own "ALPHABETICAL LIST OF NYAYAS EXPLAINED IN PARTS I, II & III" at leaves 169-176 — [`LaukikaNyaya/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LaukikaNyaya/README.md)'s prior "no back-matter index in this source" claim only checked the literal last ~6 pages and missed it (same index already used by `build_laukika_nyaya.py`'s own cross-reference pass, reprinted a second time in this scan). Cross-referencing it against the 377 committed headwords via the project's own rigorous skeleton+gloss-corroboration matcher surfaced **12 genuinely new, individually-verified records** — see [`tools/append_h803_followup_records.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LaukikaNyaya/tools/append_h803_followup_records.py) for the full methodology and root-cause analysis (a `prev_is_prose()` false-negative class in the existing extraction pipeline). FEATURES_INDEX registration still withheld — 389/400 = 97.25%, closest yet.

### Added
- **H1362 FINDINGS verifiability axis — every finding classed by re-derivability (Opus 4.8 `claude-opus-4-8`).** New [`epistemic_dashboard/FINDINGS_VERIFIABILITY_RULING_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/FINDINGS_VERIFIABILITY_RULING_2026.md) + machine-readable [`epistemic_dashboard/verifiability.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/verifiability.json) classify all **113** findings into **A** auto-reproducible (94) · **B** re-probeable (12) · **C** historically fixed (4) · **D** not reproducible as stated (3, §69/§85/§450) — each adjudicated from its `> **Source:**` blockquote, and for every class-A finding the cited script was `git ls-tree`-verified to exist (all 94 resolved). The [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) schema now carries the class-D citation rule (a D finding must be cited with its non-reproducibility named); the three D rows are marked in place. Three new [RECIPES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) rows (§7 →§67, §8 →§71, §9 →§89) reproduce high-value class-A findings that had none. [`derive_staleness.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/derive_staleness.py) gains `--verifiability`: STALENESS's **Re-check recipe** column is now filled from the class (zero `RECIPES §TBD` in the class-A set) and the snapshot counts the true **113**-finding denominator (was a frozen 77). The [epistemic dashboard](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/index.html) renders a `verifiability` block beside the staleness board.

### Fixed
- **H1362 resolved the H1350×H1361 §448–451 collision that left CI red (Opus 4.8 `claude-opus-4-8`).** [H1350](https://github.com/gasyoun/SanskritLexicography/pull/612) (13:58) and [H1361](https://github.com/gasyoun/SanskritLexicography/pull/615) (14:38) concurrently assigned **different** findings to §448–451, and `origin/master` shipped with duplicate headings — the epistemic-integrity gate failing on `master`. Per the citation-identity ruling's rule-4 citation exception (the merged ruling doc itself names the H1361 movers at §448–451, the strongest anchor), the H1361 movers keep §448–451 and the **H1350 PWG block moved to §452–455** with in-place tombstones; the next-free marker advanced `§452 → §456`; the ruling doc gained a §6 documenting it. Integrity check now green (113 distinct headings, Index parity, dashboards in sync).

### Added
- **H1361 epistemic-registry integrity gate + citation-identity ruling (Opus 4.8 `claude-opus-4-8`).** New [`tools/epistemic_integrity_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/tools/epistemic_integrity_check.py) enforces the §-number contract over FINDINGS + the seven sibling registries — duplicate-number, heading↔Index parity, dangling-index, next-free-marker, and dashboard↔file count/importance parity — import-free, exits non-zero with a per-defect report; wired into [`findings-dashboard.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/findings-dashboard.yml) (structural gate before the builders, full parity check after) and `.pre-commit-config.yaml`. The ruling is [`epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/REGISTRY_CITATION_IDENTITY_RULING.md) (append-only · one claim per number · later claim moves with a tombstone · the Index is the classification of record).
- **H1389 union corroboration: text-attestation regrade + post-fold table (Opus 4.8 `claude-opus-4-8`), follow-up to H1363.** (1) **Regrade:** new [`data/mw_ls_textattest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/mw_ls_textattest.py) parses MW's `<ls>L.</ls>` from csl-orig `mw.txt`, reproducing [FINDINGS §97 v2](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) exactly (59,697/194,084 = 30.8% of MW headwords carry no text citation); the committed mask [`mw_non_textattested_slp1.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/mw_non_textattested_slp1.txt) drives new `-TA` policies in [`witness_independence_reaudit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/witness_independence_reaudit.py) that count MW as a witness only when it *cites a text*. **Measured result** (supersedes the H1363 ~18,368 estimate): P3 corroborated share 34.7% → **33.8%** (larger drop at P2, 53.1% → 46.2%, where MW is still separate); **17,386 union headwords are MW-listed ghosts** — MW's only dictionary, only listed, **zero text witnesses**. (2) **Post-fold table:** regenerated UNION.md's pre-fold "in N dicts" table on the live post-fold 323,425 file (in ≥2 180,804, singletons 142,621), closing the 237-headword drift. Updates the H1363 report, `witness_tiers.json`, and FINDINGS §103 with measured figures.

### Fixed
- **H1361: FINDINGS/DEAD_ENDS §-number collisions ruled + dashboards corrected.** [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) carried four duplicate numbers (§80, §86, §87, §103) and [DEAD_ENDS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) three §8 headings; the later/non-cited claim in each moved (FINDINGS → **§448–§451**, DEAD_ENDS → **§9/§10**) with in-place tombstones, the winner keeping the number (published-first / cited). Fixed the `currently §448 → §452` next-free marker, and **backfilled 26 Index entries** (22 headings §76+ absent from the Index, plus the four renumbered). Both dashboard parsers ([`build_findings_data.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/build_findings_data.py), [`build_epistemic_dashboard.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/epistemic_dashboard/build_epistemic_dashboard.py)) now read importance from the Index dot (34 findings carried it only there), so the 27/23 `null`-importance findings are classified and the count is the true distinct-heading total: **95 → 109**, `by_importance` {🔴18, 🟠74, 🟡17} now sums to 109. Regenerated `findings_dashboard/data.json` + `epistemic_dashboard/epistemic.json`. CONTRADICTIONS §6×2 was already resolved by [H1364](https://github.com/gasyoun/SanskritLexicography/pull/604) — extended, not re-touched.

## [1.40.0] — 20-07-2026

### Added
- **H1363 dictionary witness-independence map + re-audit of the 15-dict union corroboration (Opus 4.8 `claude-opus-4-8`).** The published union "in N dicts" distribution ([`HeadwordLists/union/UNION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md)) is read as corroboration, but the 15 dictionaries are not 15 independent witnesses. New [`data/WITNESS_INDEPENDENCE_REAUDIT_UNION15_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/WITNESS_INDEPENDENCE_REAUDIT_UNION15_2026.md) operationalizes the standing ruling of [FINDINGS §83/§97](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) ("PWG, PW and MW collapse to roughly one European witness"; MW compiled *from* Böhtlingk-Roth) — building the derivation graph and recomputing the corroboration distribution under a 5-rung independence ladder (P0 published 15 → P1 CAE≡CCS → P2 Petersburg lineage → **P3 = §83/§97 ruling, MW folded, 11 clusters** → P4 strict +MD, 10) via [`data/witness_independence_reaudit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/witness_independence_reaudit.py) (+ two derived TSVs). Apte is kept independent per §83 (its named independent control). **Finding:** corroborated share (≥2 witnesses) falls from **55.9%** (published) to **53.1%** (documented Petersburg collapse) to **34.7%** under the established §83/§97 ruling — 68,651 headwords that look multiply-attested rest on a single European lineage; the ≥5-witness "well-attested" tier more than halves. P0 identity map reproduces the live file's `n_dicts` column exactly (regression anchor). Also surfaced: UNION.md's published table is **pre-fold** (sums to 323,662 vs the live post-fold 323,425) — noted in-place. Extends FAIR dataset E40.

### Fixed
- **H1364: CONTRADICTIONS.md duplicate `§6` key repaired + Ch. 14 Zenodo DOI ruled.** Two unrelated rows both used `§6` (Concordance-Q3 plan-set vs the Ch. 14 correction-dataset DOI); §3–§8 renumbered strictly ascending. Live Zenodo check resolves the dispute the collision had buried: `10.5281/zenodo.15834721` is a **false DOI** (resolves to an unrelated topology preprint) — BOOK_PLAN was right, `data/FAIR_RELEASE_1.md` was wrong, and csl-observatory's own `CITATION.cff` carried the same false DOI. All three corrected; see [FINDINGS §103](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

## [1.42.0] — 20-07-2026

### Added
- **H1350 PWG data-layers wave (Sonnet 5 `claude-sonnet-5`) — card anatomy, the first formal PWG grammar, full-corpus validation, and four extended extraction layers.** [`docs/PWG_CARD_ANATOMY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PWG_CARD_ANATOMY.md) crosswalks the three existing anatomy descriptions. [`RussianTranslation/schemas/pwg_markup.rnc`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_markup.rnc) is the first RelaxNG grammar `csl-orig` has ever had (39 element tags, including 21 not in csl-atlas's own census); [`validate_pwg_markup.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/validate_pwg_markup.py) and [`validate_pwg_portrait.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/validate_pwg_portrait.py) validate all 123,366 records (122,730+123,366 pass, 0 unclassified). [`audit_sense_glyph.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_sense_glyph.py) full-measured the `〉` sense-glyph fix at corpus scale (93.78% of RU-store rows touch an affected headword) with a read-only, byte-identical-verified store join and a side-file quarantine. [`extend_ls_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/extend_ls_coverage.py) confirmed citation resolution already at 98%+ (not the previously-cited 72.4%) and added a deterministic ibid rule. [`resolve_xrefs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/resolve_xrefs.py) resolved 2,845 new PWG `<ab>s.</ab>` cross-reference edges (shipped as [csl-atlas#274](https://github.com/sanskrit-lexicon/csl-atlas/pull/274)). [`extend_ontolex_xrefs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/extend_ontolex_xrefs.py) layers those edges onto the OntoLex graph as an additive sidecar. Four new FINDINGS entries (§452–455, renumbered from §448–451 per H1362 to resolve the H1350×H1361 concurrent collision). Full plan: [PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md); three follow-on `@DECIDE`s filed in Uprava GTD.

## [1.39.0] — 20-07-2026

### Fixed
- **H1339 Tier-B factory hardening — 20 of 21 still-reproducing H1283 Tier-B defects fixed test-first, including both P0s (adjudication + orchestration Fable 5 `claude-fable-5`; 44 finder/verifier agents on Fable 5 `claude-fable-5`).** Highlights: TM-served whole cards are schema-complete at build AND refused fail-closed at serve (B03, P0 — one TM hit used to poison the whole window at the save gate); heal-stitched cards carry schema-required `iast`/`notes` on both twins (B02); `record.grammar` joined `PROMOTED_COMMON` so the promote-time `{Tn}` residue backstop and `backfill_tn_residue` cover the full store write-set (B21 — the H1283 verifier conflict, resolved); the canonical-store `--merge` is better-attempt-wins (B08); TM sidecars and the RU coverage gate resolve worktree-safely via canonical resolvers (B04/B09 — a fresh-worktree run used to get 0 TM hits and an empty-store coverage verdict); `save_and_audit` refreshes the requeue singletons (B10); `stage2_pregate`/`audit_translation` resolve merged output with the dual `safe_name` lookup (B19); a crashed audit's blast-radius requeue list is refused, and the TM denylist gained an unblock lifecycle cleared by gate-passing promotions (B11/B12); the `translated_source_siglum` trigger fires only on citation-shaped Russian (B13); `perf_preflight` prices per lane — healthy 60K-tok vs pril10 monster 184K-tok calibration (B14); all-null probe-log outcome rows are refused with note-kv recovery (B15); the dispatch roster filters parked/unvalidated accounts before slicing (B16); h1209 lane: null-worker retries, sticky controller rejections, agent deadlines, null-card-tolerant canonical audit (B05/B06/B07); heal/presplit fragment prompts carry per-card grammar + portrait evidence on both lanes (B01). B17 (6h probe-receipt expiry, direct `cmd_staged_run` lane only) deferred with a recorded rationale. `window_selftest` 150 → 157; 9 new `LANG_PARITY` entries; every fix carries a failing-first regression. Matrix + evidence: [`RussianTranslation/pwg_ru/h1339/H1339_TIER_B_STATUS_2026-07-19.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1339/H1339_TIER_B_STATUS_2026-07-19.md).
- **H1339 B23 (P0, found by the new offline benchmark's first end-to-end run): manifest-v2 leases were unauditable.** `window_provenance.stale_check` and `coordinator.read_execution_manifest` accepted only manifest v1 while production profile-bound `prepare` emits v2 — every v2 lease audited `stale_artifact`, so the headless factory chain could never have passed its own audit on a live run (unnoticed because the c4 ladder NO-GO'd before any live `record-output` and all audit fixtures were v1). Both loaders now accept v1+v2; the benchmark exercises the v2 chain end-to-end on every run.

### Added
- **H1339 real unattended requeue materialisation (the H1283 A4 completion).** A bounded-loop requeue work-item now materialises a REAL coordinator requeue attempt (`prepare-requeue`, transient lane before defect) plus a runnable `<lease>::rqNN-<kind>` orchestrator job via the new `import-requeue` command — idempotent at every crash seam, loud when unmaterialisable, with `coordinator_lease_id()` mapping at every coordinator command site; new audited `reset-failed` command is the ONLY exit from the terminal failed-job state (scoped, mandatory reason, events-ledger row). Selftest-pinned end to end.
- **H1339 frozen offline benchmark** — [`src/pilot/h1339_offline_bench.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1339_offline_bench.py) + committed hermetic fixture (12 real PWG keys, 5 leases: clean/requeue/TM-hit/presplit/multi-lease) driving the REAL prepare→audit→promote chain in a per-run sandbox with zero model calls and a deterministic semantic output signature.
- **H1339 hash-pinned population rederivation** — [`src/pilot/h1339_population_rederive.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1339_population_rederive.py): the refuted "~10,199 remaining" premise is replaced by **5,580 unique remaining headwords** (701 verb roots + 4,757 nominal PWG-rooted + 122 no-PWG supplement-chain; the three nominal cores are nested — 6,772-lemma double-count avoided), content hash pinned.

### Changed
- **H1339 measured offline speed — total −23.0% (measured PARTIAL vs the ≥25% target), semantic store equality proven.** Batched multi-lease promotion (`promote_final_cards --batch-manifest` + `coordinator.promote_ready` bundling: one claim → one store read → one better-attempt merge → one backup → one atomic replacement, all-or-nothing, per-lease attribution) cut the store-write stage **−49.8%**; the five audit child gates run in-process via `runpy` (identical script code, captured stdout, same strict parsers/fail-loud path) cutting the gate stack 3.05 s → 0.25 s (audit stage −19.8%). Same-session frozen-fixture medians: 12.08 s → 9.30 s. No concurrency cap or safety gate touched; the remaining dominant stage (per-lease `perf_preflight`/`gen` subprocess spawns) is recorded for the successor.

## [1.38.0] — 19-07-2026

### Added
- **H803 clean-scan lane — LaukikaNyaya 302 → 377 records, real per-entry page citations for the first time (Sonnet 5 `claude-sonnet-5`).** Independently found and OCR'd a different, cleaner archive.org source — three University of California Libraries scans (`handfulofpopular01/02/03jacoiala`, one per Jacob "handful") — after re-confirming the primary `YKTn_...` item's image backend was still down; this alternate source's own OCR text layer is Devanagari-blind, but its IIIF backend worked (a different datanode), so all 378 page images were fetched and OCR'd locally with Tesseract's Sanskrit-aware `san+eng` model. Reconciled against the corrected 302-record file: 223 matched (193 body-upgraded, all gaining a real page citation), 78 genuinely new, 79 kept as-is, minus 3 pre-existing visarga-differing near-duplicate pairs in the 302-set exposed and resolved along the way → **377 records (94.25% of the ≥400 target, the closest yet)**. Also completed the real image-based 20-record-class spot-check the handoff's Definition of Done always asked for (blocked in every earlier pass by the outage), finding and disclosing 2 real OCR errors and fixing 2 real recall gaps (an invisible zero-width non-joiner silently broke the headword-line regex) live. FEATURES_INDEX registration correctly still withheld — target not yet met. See [`LaukikaNyaya/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/README.md) "Clean-scan lane methodology" for the full writeup, including a caught-and-fixed false-positive in the reconciliation matcher itself.

## [1.37.0] — 19-07-2026

### Fixed
- **H803 dedup + false-positive correction — LaukikaNyaya 390 → 302 records, `/dual-run-salvage`'s reconciliation had two verified defects (Sonnet 5 `claude-sonnet-5`).** The dual-run reconciliation directly below (240+300→390) turned out to contain 57 same-`_ocr_line` duplicate pairs (114 records for 57 physical occurrences, 0 content differences once whitespace is normalized — a dedup-by-`nyaya_slp1` miss caused by two lanes formatting headword whitespace differently) plus 31 further false-positive lines matching the same length-based false-positive signature already established for the unbounded `index-crossref-prefix` strategy. Every one of the 88 removed records is individually accounted for (57 duplicate, 31 false positive) — none dropped without a specific, checkable reason; 0 lines are unique to the corrected 302 that weren't already in the 390's set, i.e. this only ever removes, never misses relative coverage. The dataset is now produced by a single `python build_laukika_nyaya.py` invocation with no manual merge step. See [`LaukikaNyaya/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/README.md) "19-07-2026 dedup + false-positive correction" for the full audit.

## [1.36.0] — 19-07-2026

### Added
- **H803 dual-run reconciliation — LaukikaNyaya 240 + 300 records merged to 390 (`/dual-run-salvage`, Sonnet 5 `claude-sonnet-5`).** Two independent extraction passes ([PR #577](https://github.com/gasyoun/SanskritLexicography/pull/577), merged; [PR #576](https://github.com/gasyoun/SanskritLexicography/pull/576), open/conflicted) diverged from the same 151-record baseline unaware of each other. Reconciled as a union deduplicated on `nyaya_slp1` (150 records in common, 0 gloss-identity conflicts, 90+150 net-new) — the merged file is a manual reconciliation, not directly reproducible by a single [`tools/build_laukika_nyaya.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/tools/build_laukika_nyaya.py) run. See [`LaukikaNyaya/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/README.md) for the full accounting.

## [1.35.0] — 19-07-2026

### Added
- **FINDINGS §97 v3 update — PWG lexicon-only audit joins Amara, Rājanighaṇṭu/Trikāṇḍaśeṣa/Nighaṇṭu confirmed unsourceable (H1326, Sonnet 5 `claude-sonnet-5`).** Appends the [SanskritGrammar PR #459](https://github.com/gasyoun/SanskritGrammar/pull/459) result to [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) §97: joining Amarakośa (GNU GPL v3.0, `sanskrit-kosha/kosha`) as an 8th koṣa moved pwg-unique 2,298→2,294 and koṣa-corroborated 10,724→10,812, but left the hardest 788-word "absent from every dictionary" core unchanged. Records the negative result that Rājanighaṇṭu/Trikāṇḍaśeṣa/generic Nighaṇṭu have **no bulk lemma-tagged headword set anywhere checked** (a 126-dictionary scan of `sanskrit-kosha/kosha`, the `cltk/sanskrit_text_dcs` DCS mirror, web search) — only raw unsegmented sandhi-joined verse — and the reusable rule that a "digitise dictionary X" backlog item needs a headword-tagged-vs-raw-OCR check before estimating effort.

## [1.34.0] — 19-07-2026

### Added
- **[FINDINGS §98](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) — PD's inline sigla contain a near-homograph pair that similarity-clustering silently fuses** (19-07-2026, Opus 4.8 `claude-opus-4-8`, harvested while scoping [H1336](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1336-Opus_csl-atlas_pd-abbrev-vs-dcs-corpus-coverage_19.07.26.md)). The Poona Dictionary has **no `<ls>` citation layer** — it contributes zero edges to [`ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv) — so any consumer must regex-harvest sigla from running prose and then normalise variants (measured: 107,630 entries, **99.2 % carry a citation**, 5,231 distinct tokens over 416,767 occurrences, against a plausible ~800–1,500 real works). The obvious normalisation tool fuses the dictionary's two highest-value sources:
  - **`MahāBhā.` (9,339) is the Mahābhārata; `MahāBh.` (1,940) is Patañjali's Mahābhāṣya.** One character apart, not variants. **Verified against actual citation contexts rather than inferred from abbreviation convention** — `MahāBhā.` carries parvan.adhyāya.śloka locators (`vii. 22. 33`) and cross-refs to `BrahmP.`/`ŚabdKaDru.`; `MahāBh.` carries Kielhorn vol.page.line plus an **`({%on%} …)` tail naming the commented rule** (`({%on%} P. viii. 4. 68)`). 1,317 vs 72 distinct locator shapes.
  - **The `({%on%} …)` tail is the robust mechanical discriminator**, not the siglum spelling — a Mahābhāṣya citation names the sūtra it comments on, a Mahābhārata citation never does.
  - Fusing them inflates one node to 11,279 citations and destroys the epic-vs-grammatical distinction that any corpus-coverage or citation-weighting measurement depends on. A blanket "never merge" rule is equally wrong: `Kāśi.`/`KāśiVṛ.` and `PadmP.`/`PadmaP.` in the same frequency head are genuine merges.
  - Also records the other harvest noise classes (structural tokens, language labels, and **secondary scholarship** — `EI.` 3,281, `POK.`, `TURN.`) and the standing caveat that PD is published only `a-` to ~`apaca-`, so any harvested siglum list is PD's canon *as exercised under one letter*, not its full declared canon.

## [1.33.0] — 19-07-2026

### Added
- **One-click case-government (Rektion) index + PW capitalized-marker gap closed (19-07-2026, Opus 4.8 `claude-opus-4-8`, [H1308](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1308-Opus_RussianTranslation_pwg-ru-valency-government-index_19.07.26.md))**:
  answers DA-vote row N2 (card `vas~~h0_zz_pw00|samava`) — a searchable government surface plus
  the fix for the PW `zz_pw*` supplement stratum, which writes case markers CAPITALIZED
  (`(<ab>Instr.</ab>)`) that the lowercase-only extractor missed entirely (0 of 1,123 store
  rows, incl. the N2 card). Made the marker regexes in
  [`government_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/government_census.py)
  case-insensitive (new `_cases()` lowercase-normaliser; one change serves both
  `extract_government()` over the store and `run_census()` over raw `pwg.txt`). Store
  government rows **508 → 1,756** (614 → 2,129 markers); raw `pwg.txt` ceiling **3,853 → 3,905**
  (the +52 are sentence-initial "Mit dem `<ab>…</ab>`" prose government previously missed).
  New `government.html`/`government.js` via `emit_government()` in
  [`build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py):
  case chips → every governing card (Instr. one-click returns 218 cards incl. vas/samava),
  `index.html#g=<safe>` deep-links to the full entry, honest floor-vs-ceiling coverage banner;
  cross-linked with the abbreviations dashboard. `census_stats.json` re-frozen; government
  sidecar regenerated (local-only). SHARED in LANG_PARITY; census + site-builder selftests
  wired into CI.

### Changed
- **LaukikaNyaya phrase-tier recall broadened — 151 → 240 records (19-07-2026, Sonnet 5 `claude-sonnet-5`, [H803](https://github.com/gasyoun/Uprava/blob/main/handoffs/H803-Sonnet_SanskritLexicography_laukika-nyaya-jacob-ingest_12.07.26.md) continuation)**:
  the non-`न्याय` phrase-tier headword gate in [`build_laukika_nyaya.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/tools/build_laukika_nyaya.py)
  was broadened from a literal `"The maxim of"` opener match (4/199 candidates recovered) to
  `looks_like_gloss_sentence()`, verified against all 113 surviving candidates and their 8
  specific identified false positives — named-tier count unchanged (147) confirming the change
  is scoped. `_page_numbers.json` sidecar fetched and found genuinely unusable (11/360 leaves
  page-numbered, none in the body); image-level scan cross-check still blocked by an archive.org
  image-server outage (logged in [Uprava/SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)).
  Still short of the ≥400 stop condition (240/400, 60%) — root cause is a source-availability
  ceiling, not extraction effort; see [`LaukikaNyaya/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/LaukikaNyaya/README.md)
  "19-07-2026 follow-up pass" for full detail. FEATURES_INDEX.md registration remains deferred.

## [1.32.0] — 19-07-2026

### Added
- **Mechanical RU style sweep — no-ё, terse editorial metalanguage (19-07-2026, Sonnet 5 `claude-sonnet-5`, [H1305](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1305-Sonnet_RussianTranslation_pwg-ru-style-mechanical-yo-terseness-sweep_19.07.26.md))**:
  MG's DA-vote (N7/N12 + the terseness half of N4) ratified four deterministic RU style
  rules, applied store-wide and wired for future generation. R1: no letter ё anywhere in
  RU output (whitelist: standalone «всё»/«Всё» only; «всё-таки» defaults to е like every
  other ё-word). R2/R3: «вместо»→«вм.» and «в значении»→«в знач.» in editorial
  metalanguage — measured 0/60 and 0/24 false positives on the canonical store (well under
  the 2% restriction threshold), so both apply unrestricted. R4: `ed. Bomb.` → «Бомбейская
  ред.» in free prose ONLY — 282/283 occurrences sit inside `<ls>…</ls>` citation spans that
  [`pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py)
  keys against PWG's bibliography, so rewriting them would break source resolution; only
  the store's 1 genuine free-prose occurrence was swept. Applied to the canonical store
  (11,603 rows, unchanged): 2,029 substitutions across 1,485 rows, 0 residual violations
  after apply. New
  [`ru_style_sweep.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ru_style_sweep.py)
  (store sweep + shared violation detector, `--apply`/`--selftest`/`--wf`); new `ru_style`
  gate in
  [`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py);
  prompt HARD RULE 9 in
  [`run_pilot_wf.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_pilot_wf.js)
  (auto-inherited by every future generated harness), pinned in
  [`prompt_rule_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py).
  RU-only by construction — `LANG_PARITY.md` `ru_style_mechanical_yo_terseness`
  INTENTIONAL-DIVERGENCE. Full rule table + measurement:
  [`RU_STYLE_MECHANICAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md).

## [1.30.0] — 19-07-2026

### Added
- **`<ls>` link enrichment — Pāṇini deep/browse links + Spr. (II) full-text tooltips (19-07-2026, Opus 4.8 `claude-opus-4-8`, [H1307](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1307-Opus_RussianTranslation_pwg-ru-ls-link-enrichment-panini-spr-dhatup_19.07.26.md))**:
  MG's DA-vote (N14/N3(b)/N15) enrichment for three `<ls>` citation classes in the pwg_ru render
  layer. Pāṇini `P. a,p,s` deep links to [ashtadhyayi.com](https://ashtadhyayi.com) were already
  100% (25,061/25,061); guarded 2-param/1-param patterns add the pāda/adhyāya browse routes
  (`/sutraani/a/p`, `/sutraani/a`) — pada 1–4, adhyāya 1–8 guarded so page-refs like `P. II, S. 3`
  never mislink. Every `Spr. (II) N` (8,684, 100% linked) gains an IAST+German hover tooltip from
  [`indische_sprueche.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/data/indische_sprueche.jsonl)
  (7,537 sayings) behind a 1st-edition guard (plain `Spr. N` never resolves against the 2nd-ed corpus).
  URL forms verified against the ashtadhyayi.com backing data repo (the site is a client-side SPA) and
  the boesp1/boesp2 viewer JS (bare `?N` is the only form working for both editions). `DHĀTUP.` → Palsule
  exited as a committed acquisition spec (no machine-readable Palsule list exists org-wide; the Westergaard
  gaṇa-level link stays). New [`spr_fulltext.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/spr_fulltext.py),
  [`ls_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_coverage.py),
  fixture selftest in CI; coverage table + spec in
  [`ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md).

## [1.29.0] — 19-07-2026

### Changed
- **Renou Step-0 pilot sheet remade (v2) — per-state named evidence (19-07-2026, Fable 5 `claude-fable-5`, [H1311](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1311-Fable_RussianTranslation_renou-pilot-evidence-remake_19.07.26.md))**:
  MG voted 3/70 v1 cards (all reject, [review/decisions.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions.md))
  — all three rejections traced to one defect: the evidence panel showed lemma-global
  facts (oldest text overall, bare counts) under a question about one specific state.
  New [`renou_pilot_evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_pilot_evidence.py)
  collects the full per-text DCS attestation list per sampled lemma (name, date, state,
  confidence, registers; text→state resolution imported from `build_dcs_renou` verbatim)
  and joins the SanskritGrammar [pwg_register_genre](https://github.com/gasyoun/SanskritGrammar/blob/main/data/pwg_register_genre/README.md)
  layer by SLP1 k1; the rebuilt sheet names the contested-state texts, lists the full
  attestation surface, states a per-state judgment criterion (état II: Aṣṭādhyāyī
  quotation suffices — per the S0-002 ruling; Manusmṛti is état III, never Vedic — per
  S0-001), and renders the three v1 notes as prior-vote context. Sheet_id →
  `renou-pilot-v2-2026-07-19`; v1 3-vote export committed as the methodology record.
  Response doc incl. the ACC/NCC source-markup design answer:
  [`RENOU_PILOT_EVIDENCE_REMAKE_19.07.26.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_PILOT_EVIDENCE_REMAKE_19.07.26.md).
- **One review-sheet standard: every pending SanskritLexicography sheet remade on csl-pyutil v0.3.0 (19-07-2026, Fable 5 `claude-fable-5`, [H1313](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1313-Fable_SanskritLexicography_review-standard-v030-orgwide-remake_19.07.26.md), executing [H1301](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1301-Opus_RussianTranslation_pwg-ru-review-sheet-ux-standard-regen_19.07.26.md) per MG's direct order)**:
  the V1–V8 rulings from the h178_da vote ([register §2](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md))
  shipped as [csl-pyutil v0.3.0](https://github.com/sanskrit-lexicon/csl-pyutil/releases/tag/v0.3.0)
  (rating 1–5 below the card with approve-coupling + `rating` export field, visible id
  chips, clickable IAST headword links, taller notes, `mark_cyrillic()` RU highlighting,
  sheet_id+save-path banner) and consumed here: new shared helper
  [`RussianTranslation/src/review_sheet_standard.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_sheet_standard.py)
  (root→PWG-column kosha deep links, SLP1→IAST); ports of
  [`h178_eval_bakeoff.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h178_eval_bakeoff.py)
  (DA slider → emitter 1–5 rating; RUBRIC_JS export carries `rating`),
  [`build_h180_review_sheets.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_h180_review_sheets.py)
  (hand-rolled donor → emitter consumer, fixing its bare `decisions.json` download name),
  [`build_renou_pilot_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_renou_pilot_sheet.py),
  NEW [`build_kochergina_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_kochergina_sheet.py)
  (the hand-authored 4-row sheet gains a generator AND its missing decisions export, with a
  localStorage vote-migration shim), and
  [`article-comparison/_build_gloss_review_sheets.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/_build_gloss_review_sheets.py);
  13 pending sheets regenerated. The h178 sheets render the frozen 30-gloss sample, so
  bake-off comparability with the voted DA arm is preserved — the remaining three h178
  votes are now UNBLOCKED. csl-atlas (JS stack) and SanskritGrammar (hand-authored
  skeleton) ports queued as
  [H1314](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1314-Opus_csl-atlas_review-sheets-standard-port_19.07.26.md)/[H1315](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1315-Opus_SanskritGrammar_review-sheets-standard-port_19.07.26.md);
  two SanskritGrammar sheets found already fully voted on disk (precative 7/7,
  w2-core-11 12/12, index rows were stale) → apply handoff
  [H1316](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1316-Opus_SanskritGrammar_apply-voted-precative-w2core-visas_19.07.26.md).

## [1.28.0] — 19-07-2026

### Added
- **H178 DA-sheet vote processed → 8-handoff work-stream fan-out H1301–H1308 (19-07-2026, Fable 5 `claude-fable-5`, [H1300](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1300-Fable_RussianTranslation_h178-da-vote-processing_19.07.26.md))**:
  MG's first bake-off vote (`h178_da`, 30 promoted pwg_ru glosses: 27 approve / 3 reject,
  partial 15/30 DA numeric channel) filed to the
  [H274](https://github.com/gasyoun/Uprava/blob/main/handoffs/H274-Fable_DO_RussianTranslation_pwg_ru_bakeoff_compute_07.07.26.md)
  contract path (local-only `pwg_ru/eval/h178_da.decisions.json`; evidence copies under
  `D:\ClaudeTools\evidence\`); all 8 sheet-system rulings (DA 1–5 buttons below card,
  visible card IDs, IAST headword links, Publishable→DA≥4, RU-token highlighting,
  sheet↔decisions binding standard) + 20 content issues (German residue in RU fields,
  abbreviation policy, citation-translation reuse incl. Elizarenkova/KATHĀS./Leonov,
  no-ё + terseness style, doublet policy per Apresyan, Pāṇini/Spr./DHĀTUP. link
  enrichment, valency index) extracted into
  [`RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md)
  and fanned out into nine atomically-minted handoffs (H1300–H1308) with execution
  gates (sheet regeneration only after the German-residue + mechanical-style sweeps
  land). The 10-07 stay-Latin abbreviation ruling vs the 19-07 translate-them vote
  notes logged as [CONTRADICTIONS §7](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
  (resolution path: H1303 ratification sheet).

## [1.27.0] — 19-07-2026

### Added
- **A67 negative-results methods paper drafted + full failure adjudication (18/19-07-2026, Fable 5 `claude-fable-5`, [H1268](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1268-Fable_SanskritLexicography_negative-results-dead-ends-methods-paper_18.07.26.md))**: the programme's first negative-results paper, [papers/A67_negative_results_computational_sanskrit_lexicography.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A67_negative_results_computational_sanskrit_lexicography.md) — 46 recorded failure candidates harvested from both DEAD_ENDS registries, both CONTRADICTIONS registries, FINDINGS, and the ⚫ RETIRED work-registry rows, each adjudicated INTRINSIC / INCIDENTAL / UNDERPOWERED / REVERSED / OUT-OF-SCOPE with per-row rationale in the committed audit trail [papers/A67_negative_results_adjudication_table.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A67_negative_results_adjudication_table.md). Verdict distribution 21+1 enter / 12+5 excluded / 7 out-of-scope — fewer than half of recorded failures survive as scientific negative results, itself the paper's first result. Four-class taxonomy (missing-signal · lossy-key · wrong-witness · statistical-artifact), the §8b MBH reversal as the falsifiability case study, venue shortlist (Insights from Negative Results in NLP · LRE · DSH). Fact-check pass ran before commit: a read-only verification agent checked every number/attribution against its cited source; its 10 findings (one invented detail, one wrong availability statement, a missed candidate, the I12 arithmetic wrinkle in DEAD_ENDS §8's 37.7%, and attribution fixes) are applied and disclosed in both files. Registered as **A67** (readiness 2/5) in [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) the same pass.

## [1.26.0] — 18-07-2026

### Added
- **M01 monograph complete in draft — Ch. 3 + Ch. 11 written, 14 of 14 chapters in book form (18-07-2026, Fable 5 `claude-fable-5`, [H1240](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1240-Fable_SanskritLexicography_m01-ch03-a40-ch11-a50-data-chapter-prose_18.07.26.md))**: the last two chapters land as [ch03_headword_inventory.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch03_headword_inventory.md) (← A40: the 2014-vs-2026 census +14.3 %, the 15-dictionary union's overlap structure, and the corpus-grounding bridge — attestation VEI 69.8 % … SKD 14.1 % on the DCS-2021 denominator, read as coverage geometry under ch02 §6.2; the reverse DCS↔CDSL crosswalk stated at its true 13-text-pilot scope with wf0-floor semantics) and [ch11_citation_frequency_graph.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch11_citation_frequency_graph.md) (← A50: the 828,505-citation / 912-text frequency graph written to ch02 §6.3's effect-sizes-first contract; the text→tradition map stated as **inferred, 0/119 human-reviewed**, in text and tables; the ch10-vs-graph-builder `<ls>` extraction conventions reconciled — bare vs attribute-bearing tags). Both turned out to be journal→book **conversions** (A40 full prose per H675, A50 per H677 — the "data-only, first-drafting" premise was stale). Same pass: the Part II/IV bridge ⚠️ boxes resolved against the merged chapters; an **attestation/absence semantics inversion fixed** in ch02 §6.2/§6.4 and BRILL_PROPOSAL (the 69.8 %…14.1 % range is attestation, not absence, per A40 §4.4); book CHANGELOG, BOOK_PLAN §11 done-entry + still-to-do renumber, and BOOK_PLAN.meta backlog #1/#2 ticked.

## [1.25.0] — 18-07-2026

### Added
- **M01 monograph glue drafted — Introduction + 5 part-bridges + Conclusion (18-07-2026, Fable 5 `claude-fable-5`, [H1241](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1241-Fable_SanskritLexicography_m01-introduction-part-bridges-conclusion-glue_18.07.26.md))**: the connective tissue that turns the 12 committed chapters into a monograph rather than an anthology — 7 new files in [Digital_Sanskrit_Lexicography-BOOK/chapters/](https://github.com/gasyoun/SanskritLexicography/tree/master/Digital_Sanskrit_Lexicography-BOOK/chapters). The [Introduction](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch00_introduction_two_civilizations.md) is seeded from **A61's serial-infrastructural-conversion argument** per MG's 18-07 ruling (chronicle/testimony/quotations stay in the WSC paper; no A61 permission gate touched; the book does not cite A61 — the ruled ordering has A61 citing the book). The [Part III bridge](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/bridge_part3_microstructure_civilizations.md) carries the crosswalk §4.1 comparative upgrade (Baalbaki order/witness/copying, Ferri per-essay, Dickey). Part II/IV bridges flag their H1240-pending Ch. 3/11 sections at plan altitude with boxed ⚠️ revision obligations. The [Conclusion](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/conclusion_evidence_graph.md) argues the evidence graph as a general model with explicit transfer conditions and an honest FAIR/κ self-audit. All 12 vetoable framing calls parked for the author in [SIGNOFF_M01_glue_framing_calls.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/SIGNOFF_M01_glue_framing_calls.md) (MG `@DO`); book CHANGELOG, BOOK_PLAN §11, BOOK_PLAN.meta backlog #5 and `.ai_state.md` ticked in the same pass.

## [1.24.1] — 18-07-2026

### Added
- **H1110 closeout residue — Phase 6 record propagated, Phase 2 doc gaps closed (18-07-2026, Opus 4.8 `claude-opus-4-8`)**: an independent 6-phase fulfilment verification of [H1110](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1110-Opus_SanskritLexicography_pwg-ru-post-h1080-audit-fix-skills-c4-restart_17.07.26.md) (10 agents, adversarial refutation per COMPLETE verdict) found Phases 1–6 delivered but three documentation obligations from Phase 2 item 11 and Phase 7 never landed. Closed here: **[FINDINGS §93](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)** (declared-validated-never-enforced; the execution-route parity discipline that surfaced it, plus the 8-fixed/38-open/2-refuted shape of the C-01…C-59 re-execution), a standing **execution-route section in [PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)** recording that the headless CLI (manifest v2) replaced the retired Workflow-from-session route and that degradation is now measured per run rather than asserted from a date, and the **Phase 6 `HEALTH_NOGO_BY_ENVIRONMENT` entry** in the pwg_ru changelog. Verification also **refuted three further reported gaps as stale-clone artefacts** — the github-spine `SKILLS_INDEX.md` rows, the Uprava G46 wiring, and H1110 Phase 3's Codex half ([codex-config PR #2](https://github.com/gasyoun/codex-config/pull/2)) were each already delivered on their default branches, and only appeared missing when read from a local clone lagging behind (the H1245 false-FAIL class; the canonical SanskritLexicography clone sat on a *deleted* branch 78 commits behind `origin/master`, which is also what made `goals_check.py` report G46's on-disk pilot scripts as stale). A redundant Codex re-port authored against the stale clone was discarded rather than pushed. **Standing lesson: `git fetch` before believing an absence — a verification agent reading a working tree measures the clone, not the repo.** No paid call was made; the c4 ladder remains host-blocked.

## [1.24.0] — 18-07-2026

### Added
- **H1209 controller-worker canary — rig built and VALIDATED on the 3-card promote-DRY slice (18-07-2026, orchestration Fable 5 `claude-fable-5` resuming an Opus 4.8 `claude-opus-4-8[1m]` session; workers Sonnet 5 `claude-sonnet-5`, controller agents Opus 4.8 `claude-opus-4-8`, [PR #553](https://github.com/gasyoun/SanskritLexicography/pull/553))**: first measured probe of the «инжиниринг контроля» concept ([H1209](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1209-Opus_SanskritLexicography_pwg-ru-controller-worker-canary_17.07.26.md)) — Workflow rig under [`RussianTranslation/src/pilot/h1209/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1209/canonical_audit.py) reusing the production prompt invariants verbatim (manifest-driven), with FREE deterministic retry gates and Opus review only for surviving cards. The v1 slice exposed a **`gate-bug`**: a non-canonical EQUALITY sense gate (naive `senses` glyph count) made workers displace source `{Tn}` spans into unrestorable `card.notes` — workflow self-report 3/3 vs **canonical audit 1/3** (incident `H1209_SLICE_V1_2026-07-18` in [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)). v2 gates are direction-aligned with `accept()` (HARD `{Tn}`-multiset fidelity german+russian, shortfall-only vs `source_senses`); v2 rerun `wf_e858f3cf-6af`: **canonical 3/3 PASS, self-report == canonical** (8 agents, 544,056 tok). `canonical_audit.py` (card_fields C-01 restore + `accept()` battery + schema) is the authoritative promote-DRY verdict, independently adversarially reviewed 7/7 faithful. `window_selftest` 142/142, `lang_parity_check` 0 drift (GAP `h1209_controller_worker_rig`), `check_launch_ledger` clean. Promote-DRY only; medium50 RU + mini-EN deferred. Full narrative: [RUN_LOG.md 2026-07-18](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md).

## [1.23.0] — 18-07-2026

### Changed
- **H1245 big-manuals estate refresh (18-07-2026, Fable 5 `claude-fable-5`)** — all 10 manual
  files refreshed against the 221-commit drift window, one adversarial `fact-check-against-source`
  agent per manual, **every confirmed finding fixed** (39 across the seven manuals: manifest-v2
  promotion refusal + mechanized H255 guards + H818 model-pin closure + 53-entry parity in the
  RussianTranslation deep manual; docs-site CI job, A30/A31/A58, 12/14 chapters, closed
  corpus-methods `@DECIDE`, the flagged Zenodo-DOI conflict → [CONTRADICTIONS §6](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
  in the publication manual; per-list key2 verdicts + era-split `wc -l` rule + RIGHTS_LEDGER
  gate in data-reuse; release-stance + CI + FINDINGS-§N-breach warning in maintainer; book/venue/
  registries in researcher; MW-key2 measurement + same-day corpus_gate fix in headwordlists;
  post-incident ReverseDictionary reality in the student manual). Root sheets **re-thinned**:
  AGENTS §4 → live-pointer rule, §5 + HUMAN_RU §8 folded into the deep manual as §13–§14;
  phantom A51 and stale "draft PR #264" framing corrected. **9 per-manual `.meta.md` metadocs
  created**, each with a `LAST_VERIFIED` block (spot-run counts recorded); set-level
  [README.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/README.meta.md)
  narrowed; router gains the H1029 onboarding row.

### Added
- [CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
  §6: the `10.5281/zenodo.15834721` mint-status conflict (BOOK_PLAN vs FAIR_RELEASE_1) —
  unresolved, needs one online Zenodo check.

## [1.22.0] — 18-07-2026

### Added
- **H968 — 11 metadocs backfilled for hook-flagged genre-named docs (18-07-2026, Sonnet 5 `claude-sonnet-5`)**: sibling `<name>.meta.md` companions authored for every currently-missing metadoc in scope — [FEATURES_INDEX.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.meta.md), [FINDINGS.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.meta.md), [HERITAGE_INRIA_ROADMAP.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.meta.md), [ROADMAP_ACC_NCC.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ACC_NCC.meta.md), [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.meta.md), [ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.meta.md), [ROADMAP_VEDAWEB_REUSE.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_VEDAWEB_REUSE.meta.md), and three RussianTranslation roadmaps ([RESEARCH_CAPABILITY_ROADMAP_2026-07-09.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.meta.md), [REVIEW_AND_ROADMAP.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_AND_ROADMAP.meta.md), [research/ROADMAP_ACL_LESSONS_2026.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_ACL_LESSONS_2026.meta.md), [research/ROADMAP_CEILING_2026.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.meta.md)). Each carries purpose/audience/format, a ranked improvement backlog with real owners (`H###` or `parked — <reason>`), known limitations read from the actual subject text, deprecation status, and related-doc links; two cross-doc overlaps were surfaced (BLI-evaluation work duplicated across `RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md` and `research/ROADMAP_ACL_LESSONS_2026.md`) as backlog items rather than silently resolved.

## [1.21.0] — 18-07-2026

### Changed
- **H1110 Phase 6 — c4 bounded live-acceptance attempted, deferred at `HEALTH_NOGO_BY_ENVIRONMENT` (18-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, [PR #534](https://github.com/gasyoun/SanskritLexicography/pull/534) · [#538](https://github.com/gasyoun/SanskritLexicography/pull/538) · [#545](https://github.com/gasyoun/SanskritLexicography/pull/545))**: the c4 profile was mechanically proven — a validated roster slot in `max_accounts.sqlite` bound to `config_dir_fingerprint e96ee464…`, `validate_profile` clean — and every offline gate is green (`window_selftest` **142/142**, headless/execution/bounded selftests PASS, `lang_parity_check` 0 drift). But the Anthropic host is degraded: a confirmation health probe read **98,625 ms (~98.6 s, 3.3× the 30 s ceiling)**, a success/pure-latency NO-GO unchanged from H963's 16-07 104,870 ms. The bounded paid ladder is therefore **deferred** — **1 confirmation c4 call, canary + batch unspent, no production translation** — with the terminal record + exact resume in [`pwg_ru/h1110/H1110_PHASE6_C4_LADDER_HEALTH_NOGO_BY_ENVIRONMENT_2026-07-18.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1110/H1110_PHASE6_C4_LADDER_HEALTH_NOGO_BY_ENVIRONMENT_2026-07-18.md). (The H1110 Phase 1–5 code — headless CLI/manifest-v2 production route, R6 null-owner exec-gate, R9 kernel-backed active-call lock, R10 durable `AWAITING_REVIEW` checkpoint — shipped in v1.18.0–v1.20.0; this entry records the live-acceptance outcome.)

### Added
- **H1150 W1-B — offline false-flag rate for `SANLOSS_*`/`TNMASK_*` guards (measure, don't arm) (18-07-2026, [PR #544](https://github.com/gasyoun/SanskritLexicography/pull/544))**: measures the offline false-flag rate for the sense-count / TNMASK hard-reject guards with a per-guard arming recommendation. Both `SANLOSS_HARD_REJECT` and `TNMASK_HARD_REJECT` remain `= false` (byte-unchanged in `gen_opt_harness2.py`); arming stays a human `@DECIDE`.

## [1.20.0] — 18-07-2026

### Added
- **docs_site research wiki: publish-safety GO verdict recorded, deploy decision surfaced (18-07-2026, Fable 5 `claude-fable-5`, [H740](https://github.com/gasyoun/Uprava/blob/main/handoffs/H740-Fable_SanskritLexicography_docs-site-research-deploy_11.07.26.md))**: `/publish-safety-check` run over the 10 published research docs — **GO, no blocker** (all content already public on `master`; PD 19th-c. sources + citation-scale Kochergina probes; no personal data, secrets, or gitignored bulk in the `_site` bundle), with one anonymity-period caveat surfaced for the ruling; verdict recorded in [PUBLICATION_PIPELINE_DEEP_MANUAL.md § 5.3](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PUBLICATION_PIPELINE_DEEP_MANUAL.md) ([PR #541](https://github.com/gasyoun/SanskritLexicography/pull/541)). The previously invisible deploy-or-don't decision + the 10-vs-16 scope fork now sit as `@DECIDE` rows in [Uprava GTD](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md); the site stays undeployed pending the ruling. Also: 7 stale wiki copies re-synced (`--sync` — closes the audit's README "Living monitors" / sense_order_metrics staleness), 4/4 site tests green; documented that `merge_BU.md` never had a `research/` source (wiki-only doc, `--sync` skips it).

## [1.19.0] — 18-07-2026

### Added

- **article-comparison gloss-review goes interactive (H739).** The four finalist words'
  hand-authored RU sense-gloss reviews are now one committed dataset,
  [article-comparison/gloss_review_items.json](https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/gloss_review_items.json)
  (32 votable edits: agni 11 · akṣara 6 · ananta 9 · anya 6, each with severity + rationale
  + per-word FYI defect lists), rendered by
  [article-comparison/_build_gloss_review_sheets.py](https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/_build_gloss_review_sheets.py)
  into four interactive HTML voting sheets (shared csl-pyutil emitter, gitignored
  `review/`). The missing ananta/anya editorial passes were authored in the same pass —
  Fable 5 (`claude-fable-5`); headline findings: ananta m. 17B «окончательно добавленный
  аугмент» mistranslates the positional *finally added* (PD's own note: Pāṇini's
  kit-āgama, P. 1.1.46), and anya 5Biii «противосложение» is a music-theory false friend
  for *countersubject*.

### Removed

- **Markdown ✓/✗ gloss-review sheets retired (H739):** `article-comparison/agni.gloss-review.md`
  and `aksara.gloss-review.md` deleted — checkbox sheets are banned for gating artifacts;
  their proposals live on (rationales translated to Russian) in `gloss_review_items.json`
  and the generated HTML sheets.

## [1.18.1] — 18-07-2026

### Fixed
- **RussianTranslation/src script hygiene — path anchoring, encoding, orphan triage, full CI compile gate (18-07-2026, Fable 5 `claude-fable-5`, [H738](https://github.com/gasyoun/Uprava/blob/main/handoffs/H738-Fable_RussianTranslation_src-script-hygiene-refactor_11.07.26.md))**: the 8 gitignored/untracked audit scripts (`audit2/3/4/5/7`, `audit_fidelity`, `inspect_ru`, `inspect_verse`) re-anchored the SamudraManthanam corpus path on `__file__` instead of `os.getcwd()` and got the `sys.stdout.reconfigure(encoding='utf-8')` preamble (edited in place in the shared checkout — outside the PR by nature); the org-mandated UTF-8 preamble added to tracked [promote_lock.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_lock.py), [roadmap_check.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/roadmap_check.py), [slp1_norm.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/slp1_norm.py); the only two absolute-path literals among ~170 top-level src scripts removed — [build_src.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_src.py) and [build_glossaries.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_glossaries.py) now derive `DEFAULT_SM` from `__file__` (argv override kept).

### Changed
- **CI "Compile gate scripts" step covers ALL tracked top-level `RussianTranslation/src` scripts** via `git ls-files ':(glob)RussianTranslation/src/*.py'` (was a hand-picked list of 23; `pilot/` keeps its explicit list) — [ci.yml](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml).
- **Orphan triage (H738 audit list of 14)**: `_nws_watch.py` deleted as provably dead (zero references org-wide, watcher of a long-finished NWS scrape); 5 orphans parked with written reasons and 2 hub-cited scripts (`a43_family_stats.py`, `build_pwg_freq_order.py`) documented in a new [src README section](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/README.md); `safe_filename.py` (27 importers) registered in the org [SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md). Untracked scratch deletion (`audit6.py`) left to a human — unrecoverable.

## [1.18.0] — 18-07-2026

### Fixed
- **Findings/epistemic/progress dashboard refresh chain repaired end-to-end (18-07-2026, Fable 5 `claude-fable-5`, [H737](https://github.com/gasyoun/Uprava/blob/main/handoffs/H737-Fable_SanskritLexicography_findings-dashboard-refresh-repair_11.07.26.md))**: the three CONFIRMED breaks from the H733 audit are closed. **(a)** `dcs_cdsl_linkage_pct` — dead (null) in every snapshot since day one despite H733's regex fix — now records **81.4** in a fresh 18-07 snapshot, with the 11-07 snapshot kept as `source: "backfill"` recomputed from csl-apidev git history and the provenance documented in [`findings_dashboard/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/README.md) ([PR #532](https://github.com/gasyoun/SanskritLexicography/pull/532)). **(b)** the `SL findings dashboard refresh` scheduled task — which had NEVER completed a run (0xC000013A, Interactive-only, Temp log purged) — re-registered with `StartWhenAvailable`, explicit working directory, 2h cap and a durable gitignored log at `findings_dashboard/refresh.log`, then **proved one clean run** (Last Result 0, 7/12 platform probes ok, master + gh-pages pushed); the stored-credentials upgrade for logged-off runs is a GTD `@DO` ([PR #533](https://github.com/gasyoun/SanskritLexicography/pull/533)). **(c)** published gh-pages all re-serve fresh data — [`/findings/`](https://gasyoun.github.io/SanskritLexicography/findings/) + [`/episteme/`](https://gasyoun.github.io/SanskritLexicography/episteme/) `generated_at` 18-07 (DEAD_ENDS 11 = registry, post-H616 keys), [`/progress/`](https://gasyoun.github.io/SanskritLexicography/progress/) now a real 2-point series (senses 11,275→11,603, roots 147→254; [PR #535](https://github.com/gasyoun/SanskritLexicography/pull/535)). Refresh-cadence (monthly→weekly) and progress-nudge proposals filed as GTD `@DECIDE`, not applied.

## [1.17.0] — 18-07-2026

### Fixed
- **Canonical reverse-dictionary dataset recovered — the H733 "data loss" was a stranded fast-forward backup (18-07-2026, Fable 5 `claude-fable-5`, H736)**: `266820-reverse-Gasuns.txt` (4,135,335 bytes, 266,820 data lines, SHA-256 `925e696f…e150b9970`) plus every `.doc`/`.pdf` milestone (250,026 / 255,882) and reference corpus was found intact in `C:\Users\user\Documents\GitHub\ReverseDictionary.untracked-backup.20260707T093250\` — a Codex fast-forward on 07-07-2026 09:32 had moved the whole untracked dump there when `origin/master` began tracking `ReverseDictionary/`, and no repo doc recorded it, so the 11-07 audit ([H733](https://github.com/gasyoun/Uprava/blob/main/handoffs/H733-Fable_SanskritLexicography_full-repo-audit-fix-pass_11.07.26.md)) and the 17-07 rights ledger both reported the dataset unlocatable. Canonical `.txt` restored to the working tree (still gitignored by design), full dump mirrored to `D:\ReverseDictionary.untracked-backup.20260707T093250\` (470/470 files, hash-verified), dead blob links in [`ReverseDictionary/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/README.md) repointed to a new "Data location, integrity & backups" section, [`DATA_REUSE_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/DATA_REUSE_MANUAL.md) "not in a clone" claim corrected, and the recovery recorded in [`ReverseDictionary/CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/CHANGELOG.md). Off-machine backup (Yandex WebDAV) and the distribution-tier ruling remain open — see [H736](https://github.com/gasyoun/Uprava/blob/main/handoffs/H736-Fable_SanskritLexicography_reverse-dictionary-dataset-recovery_11.07.26.md).

### Added
- **FEATURES_INDEX Section VI (Q1–Q30) — methods & algorithms inventory (17-07-2026, Opus 4.8 `claude-opus-4-8`, H1202)**: catalogues the named computational methods behind the assets for the first time — 30 method-family rows (transliteration/keys · Sa↔Sa alignment & collation · bitext/translation-memory · morphology/roots/sandhi · classifiers/register/phonostatistics · search/OCR/ingestion), each graded **N/S/A/X** (novel · standard-in-house · adapted · external-consumed) with its verified home file, in [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) (+ regenerated [`features_index.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/features_index.html)). Introduces the `Q` ID prefix; flags the known-defective Renou register classifier (Q21, unanchored regex). Compiled from a 5-agent read-only sweep across ~85 repos; the exhaustive ~70-method backing inventory is in [H1202](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1202-Opus_SanskritLexicography_features-index-methods-algorithms-section-q_17.07.26.md). Answers the standing "do we track algorithms as an asset?" gap — previously visible only obliquely via SHARED_CODE (code), datasets.json (outputs), and RECIPES (reproduction).
- **H963 offline launch-readiness report recovered from an abandoned worktree (17-07-2026, Opus 4.8 `claude-opus-4-8`)**: [`RussianTranslation/pwg_ru/h963/H963_OFFLINE_LAUNCH_READINESS_REPORT_2026-07-16.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_OFFLINE_LAUNCH_READINESS_REPORT_2026-07-16.md) — a read-only planning snapshot (cheapest safe first tranche, plus full-drain cost in calls and agents) found uncommitted in the `SanskritLexicography-h963-resume` worktree during an org-wide worktree sweep; the only at-risk artifact across 154 repos swept. Committed under its own brief's exception ("keep runtime reports uncommitted **unless repository policy explicitly tracks them**" — the six sibling `H963_C4_*.md` reports in the same directory are tracked and nothing there is gitignored), and its self-declared "UNCOMMITTED" status header rewritten to state this rather than ship a false claim. Makes no generation call, promotes nothing, writes to no store, and does **not** lift the launch NO-GO gate (`c5`/`c6` logged out; `c4` latency ~30–53 s against the ≤ 30 s ceiling — both owner-gated). Delivered via [PR #518](https://github.com/gasyoun/SanskritLexicography/pull/518).

## [1.14.1] — 17-07-2026

### Added
- **FINDINGS §91 — DCS `feat_formation` isolates the aorist from the perfect within `feat_tense='Past'` (17-07-2026, Sonnet 5 `claude-sonnet-5`)**:
  harvested from [H1134](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1134-Opus_SanskritGrammar_whitney-aorist-per-text-tagger_17.07.26.md)
  ([SanskritGrammar PR #357](https://github.com/gasyoun/SanskritGrammar/pull/357)) via the
  registry-audit reference-harvest reflex, so the technique survives handoff archival. DCS has no
  aorist tense code — `feat_tense='Past'` conflates aorist and perfect — but `feat_formation IN
  {root, them, s, is, red, sa, sis}` cleanly isolates the seven aorist classes (12,054 finite
  tokens / 1.2% of verbal forms), correcting the earlier form-set method's 2,452 / 0.31% undercount
  (it missed the two largest classes). See [FINDINGS.md §91](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

## [1.14.0] — 17-07-2026

### Added
- **M01 Ch. 2 §6 *The corpus as a bounded witness* — the monograph's canonical corpus-epistemics section (17-07-2026, Fable 5 `claude-fable-5`, H1078)**:
  executes MG's 13-07-2026 ruling (b) on the corpus-methods fork
  ([LITERATURE_CROSSWALK.md §4.2](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md)).
  ~7 pp. of book-only new writing in
  [ch02_measurement_framework.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/chapters/ch02_measurement_framework.md):
  the DCS 2026 disclosure (5,688,416 content tokens · 270 texts · 95,457 disambiguated
  lemmas · 41.9 % hapax share, per the committed
  [VisualDCS census](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Leksicheskie-issledovaniya/Gapaksy-DCS-2026/README.md)),
  the absence-inference rule (bounded DCS-coverage statements, never "non-existent" —
  McEnery & Brezina), the five-clause statistical-practice contract (effect sizes, not bare
  p-values at corpus N — Kilgarriff 2005), and the Ch. 3/5/11/13 binding map; ch02's old
  §6–§9 renumbered §7–§10, 9 references added. Proposal ToC (Ch. 2 bullet), BOOK_PLAN §11,
  crosswalk §4.2 (15→14-chapter consumer numbering made explicit), BOOK_PLAN.meta backlog
  #3 and the book CHANGELOG all ticked in the same pass.

## [1.13.0] — 17-07-2026

### Added
- **A31/P5 Lexikos draft — error-origin typology over the OBS-T correction corpus (17-07-2026,
  Fable 5 `claude-fable-5`, H1074)**: full draft
  [papers/A31_fifty_thousand_corrections_error_origin_typology.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A31_fifty_thousand_corrections_error_origin_typology.md)
  adds a third, origin axis (print-source / digitization / conversion-markup / undetermined,
  never guessed) on top of OBS-T's location x edit-type design. Census computed by
  [papers/a31_origin_census.py](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31_origin_census.py)
  over the released 52,498-event snapshot: 58.4% classified, per-class precision 0.90-0.97
  (micro 0.933) on a 120-row hand-checked stratified sample (single-annotator, kappa pending
  the org's standing second-annotator recruit). Headline findings: form-era workflow preserved
  origin testimony for 98.9% of its events vs 23.1% for the git era; digitization-era slips
  outnumber inherited print errors >10:1; high per-dictionary print-error shares (BEN 46.9%,
  PD 37.2%, BUR 32.6%) are single-collator campaign fingerprints (top corrector 94-100%).
- **FINDINGS §87 — the roadmap's "OBS-T κ=0.42" was a phantom figure**: no measured agreement
  exists for any OBS-T axis (gold second-annotator column blank, κ=0.0 over 4 incidental
  pairs); both roadmap cells corrected, rule logged (re-derive statistics from committed
  metrics files, never cite planning-doc cells into papers).

## [1.12.0] — 17-07-2026

### Added
- **A30 full paper draft — "When Zero Means Nothing: Recovering the Indigenous Microstructure
  of the *Śabdakalpadruma* and the *Vācaspatya*" (17-07-2026, Fable 5 `claude-fable-5`, H1073)**:
  [`papers/A30_skd_vcp_microstructure_note.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_skd_vcp_microstructure_note.md)
  — roadmap P4 taken from outline (2/5) to full IJL/WSC-2027 draft (3/5 proposed). Claims the
  record-level indigenous microstructure (entry template, front-matter megastructure key, the
  *iti*-unit, SKD-vs-VCP register contrast); every figure read from committed csl-atlas
  artifacts, no new computation; scope coordinated against A04 (root grammar) / A35 (affixes)
  / A02 (sense inheritance) / A08 (citation registers).
- **FINDINGS §86 — samāsa-type frequency does not exist in any org corpus; the canonical
  examples are corpus-ghosts (16-07-2026, Opus 4.8 `claude-opus-4-8`)**: measured while
  scoping a frequency layer for the [samāsa-cakra wheel](https://gasyoun.github.io/SamasaChakram/).
  Two walls, both measured: DCS has 841 052 compound members but no type label (EM4, per H989),
  and VisualDCS's `категории композитов.ods` means *stem count* by "категория", not samāsa class;
  the fallback of showing each leaf's example frequency dies at **8/58 attested** (max 147,
  min 0). Records why an example-frequency layer is worse than none — it is a type-frequency
  claim in disguise that inverts the truth on the most-taught subtypes.
- **`ONBOARDING_NEW_CONTRIBUTOR_RU.md` — gentle Russian on-ramp for a non-technical Sanskrit contributor (16-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, H1029)**:
  fills the gap between the git-assuming English `CONTRIBUTING.md` and the deep-project
  `MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md` — a 5-rung ladder (talk-to-Claude → GitHub issues →
  browser PRs → Claude Code → independent contributor) with a beginner-safe first task
  (OCR/scan-quality error reporting, no deep lexical judgment required). Pointer added from
  `CONTRIBUTING.md`.
  - **Follow-up (16-07-2026):** added "Вариант Б" for a **zero-Sanskrit** beginner —
    proofreading the English/Latin side of entries (Apte/MW) against the scan, plus a
    simplest fallback (flag illegible scans / dead cross-reference links). Makes the first
    task reachable without reliable Devanagari.
  - **First-task redesign (16-07-2026):** replaced the open-ended "open 5–10 entries and
    hunt for OCR errors" (unbounded, low-yield, unclear done) with a **bounded verification
    task against the live `HeadwordLists/A_TYPO_QUEUE.md` worklist** — verify the 4
    MW-flagged suspect headwords vs the scan (confirm → files a correction; refute → clears
    a false positive), directly feeding print-readiness gate A. Both variant B and the
    fallback rebounded to a page/column unit rather than "read the whole dictionary".

## [1.9.19] - 2026-07-15

### Fixed
- **D-P follow-through — `latency_payload_sweep.py` `actual_prompt_bytes` + latency runbook hardened for the v1.9.17 probe (15-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, Ultracode)**:
  the D-P fix (v1.9.17) changed `_probe_call`'s prompt but left `latency_payload_sweep.py` with a stale
  mirror constant (`PREFIX_LEN + padding_bytes`) that **miscounted `actual_prompt_bytes`** (the field the
  `latency_sweep_analyze.py` payload-size axis reads) — reporting 6554 when the real prompt is 6828 B.
  Now derived from the SAME `_probe_prompt` (single source of truth, cannot drift):
  `actual_prompt_bytes = len(_probe_prompt(padding_bytes))`. Also updated
  `PWG_RU_LATENCY_POLICY_INVESTIGATION_2026-07-13.md` (the H909 owner runbook): Method step 2 now
  **requires a probe ≥ v1.9.17** on both hosts (a pre-fix `'x'`-padding probe is artificially-fast on
  compliance and refusal-bimodal under `--permission-mode plan`, confounding route latency), records the
  first honest home reading (**c4 ~30–53 s**, over the 30 s ceiling), and caveats the prior home-route
  sweep/variance results (the 8.9 s→59.2 s spread is partly that probe artifact) as needing a re-baseline.
  No behaviour change to the probe itself; diagnostic-tooling + runbook correctness only.

## [1.9.18] - 2026-07-15

### Added
- **D-Q (H994) — reliable silent-SAN-LOSS canary for the rung-3 measurement (15-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, Ultracode)**:
  the rung-3 false-flag measurement needs a card that *passes* `accept()`'s `<ls>`/`{#` fidelity gate while
  *dropping* a numbered source sense (the silent SAN-LOSS the H920/H960 sense-count soft-guard catches).
  `darvI`/`gaRanA` are unreliable — `darvI` carries `{#darvI#}` in sense 3, so dropping it `fidelity-reject`s
  instead of silently losing a sense. Curated a **deterministic** canary
  `RussianTranslation/pwg_ru/h994/canary/dq_canary_puregloss~~h0_zz_pw` (three pure-gloss senses, **zero
  `<ls>`, zero `{#`**): dropping *any* sense keeps the fidelity gate at `0==0` while `source_senses` stays 3,
  so SAN-LOSS is the only catch. Extended `accept_sensecount_test.js` to prove it against the **real**
  `accept()` (faithful clean; drop 1st/middle/last each → kept + fidelity-clean + `SANLOSS dropped=1`; drop
  two → `dropped=2`; contrast: the `darvI` `{#`-sense drop `fidelity-reject`s) — green via
  `test_h960_accept_sanloss_soft_gate`; offline harness build-check stamps `source_senses:3 / ls:0 / sk:0`.
  Curation doc: `RussianTranslation/pwg_ru/h994/H994_DQ_SANLOSS_CANARY_CURATION_2026-07-15.md`. Both H994
  probe/canary defects (D-P, D-Q) now closed; the live rung-3 gates only on the latency rung + a usable
  profile. No live generation, no store mutation.

## [1.9.17] - 2026-07-15

### Fixed
- **D-P (H994) — PWG-RU acceptance-probe prompt fragility (15-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, Ultracode)**:
  `max_account_orchestrator._probe_call`'s degenerate readiness prompt (`"Return JSON {ok:true}. Preserve
  this padding as inert input." + N×'x'`) tripped Sonnet-5's `--permission-mode plan` refusal (prose citing
  the "end your turn via AskUserQuestion" rule, `structured_output=None`), producing a **false
  `content`/`timeout`/`malformed` NO-GO on a genuinely responding profile**. Replaced with a new
  `_probe_prompt()` helper: one unambiguous "reply with exactly `{"ok": true}` and nothing else" instruction
  + ≥5 KB of inert, domain-shaped filler, under the **same `--permission-mode plan` the real generation path
  (`headless_worker.call`) uses**. Added a `D-P readiness prompt` selftest (captures the real argv + stdin;
  asserts the completable task, ≥5 KB payload, plan mode retained, degenerate `x`-padding gone). Live-verified
  on c4: both probe phases now return `success` (no refusal, 1 483 B output).
  **Correction it surfaced:** the old `'x'`-padding BPE-compresses to few tokens, giving *artificially fast*
  latency (~8 s) — the H994 v1.9.16 "c4 sub-30 s, first sub-ceiling reading" was that artifact. Under the
  fixed load-representative payload c4 measures **~30–53 s (latency NO-GO)**, consistent with H818/H895's
  ~40 s NO-GOs; the latency rung remains a genuine blocker (H818/H909 foreign-route), independent of the
  c5/c6 logins. No store mutation.

## [1.9.16] - 2026-07-15

### Added
- **H994 (pre-named H963) — PWG-RU two-profile live-ladder measurement, owner Option B (15-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, Ultracode; measurement-only, no promotion — store unchanged at 11,605)**:
  ran the owner-gated live ladder's rungs 1–2 on profiles c1/c4 (no canary generation, no store/TM
  mutation). **Rung 1 auth:** c1/c4 ✅ Max, **c5/c6 ❌ `loggedIn:false`** → four-profile acceptance stays
  **NO-GO** (owner must `claude auth login` c5/c6). **Rung 2 latency:** c1 `rate_limit` (parked); **c4
  genuinely healthy at ~8–12 s — the first sub-30 s pwg-ru probe reading ever** (H818/H895 were ~40 s
  NO-GO ×2). **Two defects surfaced:** **D-P** — the D-K acceptance probe's degenerate padding prompt
  (`"Return JSON {ok:true}" + N×'x'` under `--permission-mode plan`) trips Sonnet-5's plan-mode refusal,
  producing a *false* `content`/`timeout` NO-GO on a healthy fast profile; **D-Q** — `darvI`/`gaRanA` are
  poor SAN-LOSS soft-guard canaries (`darvI` is a deterministic fidelity-reject), so a canary that *passes*
  fidelity while dropping a sense must be curated before rung 3. Rung 3 canary **not reached**. Report:
  [pwg_ru/h994/H994_TWO_PROFILE_LIVE_MEASUREMENT_GATE_2026-07-15.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h994/H994_TWO_PROFILE_LIVE_MEASUREMENT_GATE_2026-07-15.md).
  No code shipped (measurement + docs only); H255 stays frozen until the four-profile ladder passes.

## [1.9.15] - 2026-07-15

### Fixed
- **H870 correction — FINDINGS §80 retracted-and-rewritten; MW facsimile auto-pull re-enabled (15-07-2026, Fable 5 `claude-fable-5`)**:
  an `api=1` probe via an independent egress disproved v1.9.14's diagnosis — the
  `MWScan/2020` `servepdf.php` endpoint correctly serves **1899** pages
  (`page=277` → `MWScanpdf/mw0277-kArSNi.pdf`), with or without `dict=`. The wrong
  1872 pages that prompted the diagnosis came from the portal's separate first-edition
  browser (`pg_NNNN.pdf` files) — a manual-navigation hazard, not an endpoint bug.
  [`EntryAnatomy/build_entry_anatomy.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/build_entry_anatomy.py)
  MW auto-pull re-enabled (URLs now carry `dict=` like the endpoint's own nav links);
  [FINDINGS §80](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  rewritten as the navigation-level cross-edition trap with an explicit retraction.
  Verified downstream: kosha's `app/scan_resolver.py` links are correct as-is — no
  change needed there.

## [1.9.14] - 2026-07-15

### Added
- **H870 follow-up — mw-kAla specimen gets its 1899 print inset; MW scan auto-pull disabled over a cross-edition trap (15-07-2026, Fable 5 `claude-fable-5`)**:
  [`mw-kAla-specimen`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/mw-kAla-specimen.html)
  rebuilt with the genuine 1899 p. 277 facsimile (owner-supplied scan, committed as
  [`assets/mw_kala_p277.jpg`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/assets/mw_kala_p277.jpg);
  running heads *kārshṇi/kālikā-purāṇa* verified). The v1.9.12 scan-server auto-pull for
  MW turned out to point at the **1872 first-edition** scan whose page numbers silently
  collide with 1899 `<pc>` loci — `--markup` MW builds now require `--facsimile`, and the
  trap is documented as [FINDINGS §80](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

## [1.9.13] - 2026-07-15

### Added
- **H960 — four-profile PWG→Russian production-readiness (15-07-2026, Opus 4.8 `claude-opus-4-8[1m]`, offline)**:
  verified H920 (every offline gate green) and closed the six load-bearing gaps blocking four-profile
  nonstop scale, each a **SOFT / report-only** guard pinned by a selftest and wired into CI (arming any
  hard reject stays owner-gated — a silent pass → visible requeue changes throughput, measured on live
  traffic first). (1) [`accept()` sense-count](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
  (H920's deferred deepest fix): stamps the hardened `source_senses`, records a `SANLOSS_SHORTFALLS`
  shortfall (`SANLOSS_HARD_REJECT` owner-gated); [`sense_count.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/sense_count.py)'s
  counter hardened to skip cross-reference ordinals (~4.78%-of-cards over-count). (2) grammar `{Tn}`
  multiset check on the main `accept()` path (`TNMASK_MISMATCHES`), catching a dropped `<lex>` span the
  `<ls>/{#` count misses. (3) [`dropped_sanskrit_span`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py)
  — content-multiset German `{#..#}` source-vs-target diff, LOW/report-only, head-label FP class excluded.
  (4) new [`economy_ledger.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/economy_ledger.py)
  derives `agents_per_clean` + a bounded `$/clean` band from the frozen probe log. (5) four-profile
  [`staged-run`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py):
  guard relaxed to ≥1 account, `probe_fleet()` STOP-on-any-NO-GO, `only_accounts` dispatch filter. (6) new
  [`bounded_supervisor.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_supervisor.py)
  injectable-seam nonstop loop with crash-resume. An adversarial correctness-review pass fixed 2 bugs +
  a CodeQL ReDoS. Residual NO-GO = the owner-gated live ladder (auth→latency→canary→arm→10→20→multi-profile).
  [PR #475](https://github.com/gasyoun/SanskritLexicography/pull/475); gate report:
  [pwg_ru/h960/H960_FOUR_PROFILE_PRODUCTION_READINESS_GATE_2026-07-15.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h960/H960_FOUR_PROFILE_PRODUCTION_READINESS_GATE_2026-07-15.md).

## [1.9.12] - 2026-07-15

### Added
- **H870 — /entry-specimen visual engine (15-07-2026, Fable 5 `claude-fable-5`)**:
  [`EntryAnatomy/build_entry_anatomy.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/build_entry_anatomy.py)
  extended with the two /entry-specimen modes on top of the H780 callout/leader/`@page`
  engine: `--markup <dict> <headword>` re-typesets ANY `<k1>` headword from csl-orig
  (MW `<e>`-level paragraph grouping, PWG one-paragraph-per-record; auto-proposed
  callout first pass marked "proposed — verify", or a `--callouts` JSON/TSV spec;
  facsimile inset auto-pulled from the Cologne scan server with soft 429 fallback),
  and `--image <path>` annotating a supplied picture or rasterized PDF page with
  region-anchored (`{x,y,w,h}` fractions) callouts. One HTML source serves both
  outputs: print-faithful single-sheet PDF (headless Chrome) and theme-aware
  interactive web (hover/click callout↔target sync, leader reflow on resize,
  light/dark via `prefers-color-scheme` + toggle). New committed exemplars:
  [`mw-kAla-specimen`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/mw-kAla-specimen.html)
  (39 records, 2 print paragraphs) and
  [`duden-faser-image-specimen`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/duden-faser-image-specimen.html)
  (the Duden *Faser* plate annotated in image mode, 13 regions located via the
  PDF text layer).

## [1.9.11] - 2026-07-14

### Fixed
- **H937 — H178 RUBRIC_JS note-clobber fix (14-07-2026, Sonnet 5 `claude-sonnet-5`)**: h178's
  `RUBRIC_JS` widget script wrote rubric values (MQM severities, Likert, DA, pairwise) into
  `localStorage` directly, bypassing the shared `csl_pyutil` core template's closure-private
  `state` object — core's `vote()`/`save()` (any approve/reject/defer click, on ANY card)
  unconditionally overwrote the entire stored record with stale in-memory `state`, wiping the
  note field; a second, more severe variant clobbered a *different* card's already-written
  note on any vote elsewhere on the sheet. Fixed entirely within `RUBRIC_JS` (core template
  untouched): `rubricNote()` derives the note purely from a card's current DOM widget values,
  `healAll()` re-merges every touched card's note into fresh `localStorage` on every vote
  click, and the Download button is clone-and-replaced to export fresh from `localStorage`
  instead of core's stale `state`. Browser-verified via Blob interception across same-card,
  cross-card, textarea-edit-last, and rubric-less `pairwise` scenarios.
- **H937 follow-up — download-filename regression (14-07-2026, Sonnet 5 `claude-sonnet-5`)**:
  H937's rubric-note-clobber fix cloned+replaced h178's Download button to strip the shared
  `csl_pyutil` core template's stale-state listener, but the new listener's `a.download`
  reverted to the literal `'decisions.json'` — reintroducing the exact generic-filename
  collision [csl-pyutil#1](https://github.com/sanskrit-lexicon/csl-pyutil/issues/1)/H933 had
  just fixed in the shared emitter (the two fixes shipped independently within the same hour
  and didn't compose). Now `SHEET_ID + '_decisions.json'`, matching convention. Browser-verified
  (synthetic 2-card sheet): vote-after-rubric-edit no longer clobbers a different card's note,
  and the exported filename is correctly `<sheet_id>_decisions.json`.

## [1.9.10] - 2026-07-14

### Added
- **Methodology lineage — Apresyan's systematic lexicography ↔ ACL computational lexicography**
  (H942): new Part II subsection in
  [`ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md)
  with an Apresyan-concept → ACL-resource crosswalk and a 9-item verified ACL Anthology reading
  list (WordNet, FrameNet, PropBank, VerbNet, Kilgarriff, WSD eval, lexical functions, definition
  modelling, LLM definitions). Gives the "system, not a list" thesis its genealogy and seeds the
  monograph's evidence-graded-method framing chapter.

## [1.9.9] - 2026-07-14

### Fixed
- **PWG→Russian no-PWG promotion safety** — planner manifests now emit an explicit
  single-window workflow glob and exact generation model id; merge promotions refuse the
  implicit repo-root glob that repeatedly ingested unrelated stale workflow artifacts.

## [1.9.8] - 2026-07-14

### Added
- **pwg_ru latency-policy investigation — payload-size sweep executed (H898)** —
  31 diagnostic `claude-sonnet-5` plain-probes (new
  `RussianTranslation/src/pilot/latency_payload_sweep.py` + `latency_sweep_analyze.py`,
  reusing `max_account_orchestrator._probe_call`; raw JSONL committed as durable
  evidence) settle the ~40 s measured-probe breach that NO-GO'd H818 acceptance
  twice: it is **not** payload-size-driven (a 93 B call hit 52.8 s; all-data R²=0.02)
  and **not** a flat ~40 s floor (range 8.9–59.2 s) — a modest input-size throughput
  floor (~+1 ms/byte) superimposed on a dominant, size-independent, time-clustered
  route jitter (CV 0.53) that spikes even tiny payloads over the ceiling (11/31
  breaches in-window). Results + verdict in
  `RussianTranslation/PWG_RU_LATENCY_POLICY_INVESTIGATION_2026-07-13.md`. Policy
  unchanged (30 000 ms ceiling kept; fix is the H818 foreign-route, not smaller
  payloads); step 3 (foreign-route comparison) stays human-gated.
- **FAIR Release #1 metadata (H817 WS1.4)** — `CITATION.cff`, `DATA_LICENSE.md`,
  and `data/FAIR_RELEASE_1.md` prepared for a curated Zenodo dataset deposit of
  the markup-tag census (E39) and headword-overlap matrix (E40), cross-linked
  to the csl-atlas citation graph (E38). Deliberately a file-level deposit,
  not a whole-repo GitHub→Zenodo integration — this repo mixes in
  third-party-rights-uncertain scan PDFs a full archive would sweep in. The
  Zenodo upload itself is parked `@DO` (account/token gate).

### Changed
- **H817 WS1.2** — `FEATURES_INDEX.md` registers E43–E46 (code-duplication census +
  LOC/language mix, already done pre-roadmap via H688 but unregistered; POS-per-text,
  sense/polysemy per dict, paradigm-cell coverage, both new via H817); flips 5 rows in
  `ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md` Part 0 from ○/◐ to ✅/◐ and bumps its
  `Last updated`.

## [1.9.7] - 2026-07-13

### Added
- **H813 — «Санскрит в цифрах» Wave 0 + Wave 1 (Sanskrit-in-Numbers, the Duden
  *Sprache in Zahlen* analog).** New `papers/sanskrit_in_numbers/`: Wave 0 assembles
  the already-owned modules (vocab size → A40/A55, POS → A56, lemma/token +
  a new Zipf coverage curve → VisualDCS) into `MODULES_OWNED.md`; Wave 1 ships
  the five NEW modules with reproducible generator scripts + committed JSON
  datasets — akṣara/phoneme frequency (Module 5), longest compounds with a
  ≥5-occurrence honesty floor (Module 6), gender distribution (Module 8),
  samāsa types best-effort via DCS's UD-style `compound:coord` tag (Module 9,
  explicitly flagged — no fabricated tatpuruṣa/bahuvrīhi split), and verb
  classes + parasmaipada/ātmanepada/ubhayapada voice from WhitneyRoots (Module
  10). See `WAVE1_SUMMARY.md` for headline numbers + trust blocks.

## [1.9.6] - 2026-07-13

### Fixed
- **H852 — the four H818 Windows headless-invocation defects, fixed and verified
  live.** `claude_argv_prefix()` resolves a Windows `.cmd`/`.ps1` launcher to
  `[node, cli-wrapper.cjs]` (bypassing cmd.exe, which corrupted the `--json-schema`
  arg); `--claude-bin` is threaded through `staged-run → run_once → run_claimed`;
  rate-limit detection (`is_rate_limited`) trusts the worker classification / raw
  stderr instead of matching the `manifest_sha256` hash; `staged-run` halts cleanly
  when all accounts are parked instead of busy-looping. Re-run on Windows: presplit
  canary GO, 1-headword generation `done`/`success`, no false park, no livelock —
  the invocation baseline is now functional (residual non-GO was a content-hard card,
  not invocation). Adds D-A/D-C unit tests. Report:
  [`RussianTranslation/H818_WINDOWS_LIVE_ACCEPTANCE_2026-07-13.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/H818_WINDOWS_LIVE_ACCEPTANCE_2026-07-13.md).

## [1.9.5] - 2026-07-13

### Added
- **H818 Windows live acceptance — NO-GO on four Windows/robustness defects
  (auth now resolved).** First live Windows run to get past the prior `401`:
  `init` (auth + minimal `claude -p --model claude-sonnet-5`) and the ≥5 KB
  `live_probe` passed, all offline gates green, canonical store present (11,562
  rows), 149 net-additive unpromoted headwords. Headless generation is
  non-functional on Windows — presplit canary and the first promoting window
  failed before any promotion; store unchanged, real Max account healthy.
  Defects: `claude.cmd` batch-shim cmd.exe corruption of the `--json-schema`
  argv; `run_claimed` not forwarding `--claude-bin`; `RATE_LIMIT` regex matching
  the `manifest_sha256` hash; `staged-run` parked-account livelock. Report:
  [`RussianTranslation/H818_WINDOWS_LIVE_ACCEPTANCE_2026-07-13.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/H818_WINDOWS_LIVE_ACCEPTANCE_2026-07-13.md);
  fixes tracked in
  [H852](https://github.com/gasyoun/Uprava/blob/main/handoffs/H852-Opus_SanskritLexicography_h818-windows-headless-invocation-fix_13.07.26.md).
  H841/H842/H843 remain gated on a Windows-baseline GO.

## [1.9.4] - 2026-07-12

### Changed
- **Renou stage-redundancy audit (H692) `@DECIDE` — closed in the audit doc with
  a pointer to the authoritative H771 verdict: the 25-06 canonical
  `{code}.renou.jsonl` regeneration is a CORRECTION, not a regression.** The
  primary org-wide adjudication is H771's
  [`RENOU_DCS_INDEX_REGRESSION_INVESTIGATION_12.07.26.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_DCS_INDEX_REGRESSION_INVESTIGATION_12.07.26.md)
  ([PR #394](https://github.com/gasyoun/SanskritLexicography/pull/394): 28,662/646,926
  rows = 4.4% divergent, all pure low-confidence DCS-noise removal, 0 anomalies;
  `renou_ls` positionally byte-identical). The audit doc's § ADJUDICATION adds an
  independent DCS-axis corroboration (all 26,290 index-resolvable `mw` rows:
  canonical `renou_dcs` == the `DCS_MIN_SUPPORT=2` projection of the lossless
  `dcs_lemma_renou.json`, 0 mismatches). Canonical files trustworthy downstream;
  the old underscore chain's deletion (H771) was safe.

## [1.9.3] - 2026-07-12

### Added — interactive "Каталог каталогов" over FEATURES_INDEX.md
- [`features_index.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/features_index.html) —
  a self-contained, filterable single-file HTML view of the capability inventory
  (free-text search + category tabs Данные/Словари/Интерфейсы/Инструменты/Changelog
  + status/size-tier/language filters), theme-aware, zero-dependency.
- [`build_features_index_html.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/build_features_index_html.py) —
  the generator that parses [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md)
  into that artifact, so the two never drift (edit the Markdown, re-run).
- Closes the interactive-view item long marked "planned / not built yet" in
  FEATURES_INDEX.md — and the «Каталог каталогов» deliverable of the 2004
  AIOC-Varanasi programme manifesto.

## [1.9.2] - 2026-07-12

### Added — Kochergina okas/okya/guda/sphic attestation-verify review sheet (H779)
- New [`RussianTranslation/review/sanskritlexicography-kochergina-okas-guda-sphic_4rows_review.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/sanskritlexicography-kochergina-okas-guda-sphic_4rows_review.html):
  re-verification of the 2013 Nagari-list forum thread's 4 dictionary-correction
  candidates (okas, okya, guda, sphic/sphigī/sphij) against RV attestation
  (VedaWeb accented corpus) and MW/Apte/KEWA — okas/okya senses confirmed
  unattested and flagged for change; guda's claimed gender defect **refuted**
  (Kochergina already carries a correctly separated `gudā` f. entry); sphic
  confirmed missing as a headword plus a newly found gloss error on `sphigī`.
  Interactive approve/reject/defer sheet, registered in
  [Uprava/REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md).

## [1.9.1] - 2026-07-12

### Added — Böhtlingk item-#1 shared-omission finding + Stache-Weiske notes (H796)
- [FINDINGS §83](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md):
  MW and the Petersburg dictionaries are **not** independent witnesses on inventory/apparatus
  (do not count their agreement as corroboration) — but no shared *error* has ever been found.
  Grounded in the new csl-atlas shared-omission test (A10 §3.5 / F9,
  [csl-atlas PR #263](https://github.com/sanskrit-lexicon/csl-atlas/pull/263)): on 6,941 real
  indigenous-attested words, MW's omissions track PWG's ≈8× more than the independent Apte's, yet
  MW independently supplies 54.6% of PWG's gaps.
- Reading notes on the source paper:
  [`papers/Stache-Weiske_Bö-MW.notes.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/Stache-Weiske_Bö-MW.notes.md)
  — the itemised 1881–83 charge (omission/error/sense-order) mapped to each A10 test, with the
  remaining open clause (sense-order) and the 35-Stellen gold-set flagged as actionable.

## [1.9.0] - 2026-07-12

### Added — Duden-style entry-anatomy specimen pages for PWG, MW and the CDSL record (H780)
- New [`EntryAnatomy/`](https://github.com/gasyoun/SanskritLexicography/tree/master/EntryAnatomy):
  three annotated "how to read an entry" pages after the Duden
  *Universalwörterbuch* specimen-spread model
  ([`papers/duden_deutsches_universalworterbuch-page.pdf`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/duden_deutsches_universalworterbuch-page.pdf)) —
  [`pwg-entry-anatomy.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/pwg-entry-anatomy.html)
  (24 callouts, *heman* homograph cluster + √*cumb*),
  [`mw-entry-anatomy.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/mw-entry-anatomy.html)
  (21 callouts, same lemma family for cross-tradition comparison), and
  [`cdsl-record-anatomy.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/cdsl-record-anatomy.html)
  (the digital record layer: key1/key2, SLP1 accents, `<e>` levels, `<info>`).
  Each self-contained (facsimile insets from the Cologne scan server embedded)
  with a single-sheet print PDF; generator
  [`EntryAnatomy/build_entry_anatomy.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/build_entry_anatomy.py)
  re-typesets records straight from csl-orig v02. MW `<e>`-semantics finding
  logged as FINDINGS §82. Fable 5 (`claude-fable-5`).

## [1.8.1] - 2026-07-12

### Added — A58 paper skeleton + grammatical-annex counted table (H767/H774)
- A58 paper skeleton over the H742 crosswalk tables:
  [`papers/A58_semdom_amarakosha_crosswalk_paper.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A58_semdom_amarakosha_crosswalk_paper.md)
  — claim, 12-row claim→artifact data inventory, outline, verified comparanda.
- Grammatical-annex parallel counted:
  [`data/semdom_ak_annex_table.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_annex_table.py)
  derives AK kāṇḍa 3 (2,592/5,590 synsets, 46.4%) vs semdom top-level 9
  (168/1,792 domains, 9.4%), converging to 10.7% vs 9.4% with nānārtha's
  polysemy register set aside; table embedded in
  [`data/SEMDOM_AK_CROSSWALK_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SEMDOM_AK_CROSSWALK_2026.md),
  finding logged as FINDINGS §77.

### Fixed
- FINDINGS duplicate-§76 key: the DCS `m_wordsem` finding renumbered to §78
  (renumber note in place; STALENESS link updated); §76 stays the
  MW→WordNet→semdom bridge finding cited from FEATURES_INDEX C19.
- `data/semdom.json` / `wn-links` fetch caches actually gitignored (the
  docstrings already claimed they were).

## [1.8.0] - 2026-07-11

### Added — semdom ↔ Amarakosha crosswalk, Level A + Level B gold pilot (H742)
- First crosswalk between SIL's 1,792 semantic domains and a classical
  thesaurus: [`data/SEMDOM_AK_CROSSWALK_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SEMDOM_AK_CROSSWALK_2026.md)
  (README of record) + ID-pair tables — Level A varga map
  ([`data/semdom_varga_crosswalk.csv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_varga_crosswalk.csv),
  20 thematic vargas, hand-authored with evidence), Level B machine candidates
  for all 5,590 synsets
  ([`data/semdom_ak_candidates.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_candidates.tsv))
  and a 200-synset adjudicated gold sample
  ([`data/semdom_ak_gold.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_gold.tsv),
  dual-annotated blind Fable 5 `claude-fable-5` × Opus 4.8 `claude-opus-4-8`,
  exact κ 0.677 / level-2 κ 0.806). Key numbers: 96.4% synsets get ≥1
  candidate, 0 NONE gold votes, structure agreement 67.0%, bridge top-1
  precision 17.5% (candidate generator, not classifier). Results also in
  [`papers/SEMDOM_KOSHA_CROSSWALK_SCOPING.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/SEMDOM_KOSHA_CROSSWALK_SCOPING.md)
  §7. Feeds the H721 MDF/LIFT `\sd` layer; paper A58. Per
  [Uprava H742](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H742-Fable_SanskritLexicography_semdom-kosha-crosswalk-build_11.07.26.md).

## [1.7.0] - 2026-07-11

### Added
- CodeQL SAST workflow for the repo's Python/JS tooling
  ([PR #329](https://github.com/gasyoun/SanskritLexicography/pull/329)).
- H607 HeadwordLists analytics deep manual —
  [`docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md)
  ([PR #339](https://github.com/gasyoun/SanskritLexicography/pull/339)).
- SIL MDF ecosystem correlation map (Coward–Grimes 2000 vs the CDSL workbench;
  MG rulings 11-07-2026; H721–H727 program) —
  [`papers/SIL_MDF_ECOSYSTEM_CORRELATION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/SIL_MDF_ECOSYSTEM_CORRELATION.md)
  ([PR #342](https://github.com/gasyoun/SanskritLexicography/pull/342)).
- DEAD_ENDS §8b: full MBH locus census blocked — no free vulgate e-text (H610)
  ([PR #343](https://github.com/gasyoun/SanskritLexicography/pull/343)).
- Markup-tag frequency census over all 44 Cologne v02 dictionaries (H683)
  ([PR #345](https://github.com/gasyoun/SanskritLexicography/pull/345)).
- [`DICTIONARY_REVIEWS_BIBLIOGRAPHY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DICTIONARY_REVIEWS_BIBLIOGRAPHY.md)
  — published reviews of the Sanskrit dictionaries (H731)
  ([PR #346](https://github.com/gasyoun/SanskritLexicography/pull/346)).
- Headword pairwise-overlap matrix over the 15-dict union (H684)
  ([PR #347](https://github.com/gasyoun/SanskritLexicography/pull/347)).
- E41/E42/F43 registered — correction-events trio, Kompozity `names.csv`,
  `allngramtxt` n-gram oracle (H694)
  ([PR #350](https://github.com/gasyoun/SanskritLexicography/pull/350)).
- Coward & Grimes 2000 (MDF lexicography guide) digested into the literature
  notes (H723)
  ([PR #351](https://github.com/gasyoun/SanskritLexicography/pull/351)).

### Changed
- papers: A40 headword-inventory prose completed over locked data, readiness
  3/5 → 4/5 (H675)
  ([PR #348](https://github.com/gasyoun/SanskritLexicography/pull/348)).
- pwg_ru H255 no_pwg_w03 drain: requeue of no_pwg_w02's 27 transient keys,
  11/27 promoted
  ([PR #344](https://github.com/gasyoun/SanskritLexicography/pull/344)).
- pwg_ru H255: fresh 6-headword no_pwg_w03 window + rq1 requeue, 9 clean
  promoted ([PR #352](https://github.com/gasyoun/SanskritLexicography/pull/352));
  pre-launch warm-up probe logged (21.05 s, GO)
  ([PR #353](https://github.com/gasyoun/SanskritLexicography/pull/353)).

### Fixed
- H255: [`RussianTranslation/src/pilot/no_pwg_scale_plan.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_scale_plan.py)
  STORE path — dedup was silently reading the wrong store
  ([PR #349](https://github.com/gasyoun/SanskritLexicography/pull/349)).
- Full-repo audit fix pass (H733): dead-link/doc-hygiene/CI/code fixes,
  `ROADMAP_2026_2027.md` → `ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`
  rename, `WSC2025_Reviews_7.pdf` rename — see
  [Uprava H733](https://github.com/gasyoun/Uprava/blob/main/handoffs/H733-Fable_SanskritLexicography_full-repo-audit-fix-pass_11.07.26.md).

## [1.6.0] - 2026-07-11

### Added — publication-pipeline deep manual (H608)
- New [`docs/manuals/PUBLICATION_PIPELINE_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PUBLICATION_PIPELINE_DEEP_MANUAL.md):
  subsystem deep manual for the publication layer —
  [`papers/`](https://github.com/gasyoun/SanskritLexicography/tree/master/papers)
  lifecycle (stable A-IDs, readiness scale, the scaffold→referee→author-pass
  skill chain), the M01 Brill/De Gruyter book build (article→chapter recipe,
  rights-table trigger rule, FAIR/DOI critical path as of 11-07-2026), and
  [`docs_site/`](https://github.com/gasyoun/SanskritLexicography/tree/master/docs_site)
  build/test/deploy state (built + tested, **not yet deployed** — no
  `research/` on `gh-pages`). Router row added, PROFILE deep-manual queue row
  flipped, metadoc revision logged. Third item of the H604 queue; per
  [Uprava H608](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H608-Fable_SanskritLexicography_papers-book-publication-deep-manual_11.07.26.md).

## [1.5.2] - 2026-07-11

### Added — RussianTranslation deep manual (H606)
- New [`docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md):
  first subsystem deep manual per the
  [PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md)
  queue — mw_ru covered as a finished-pipeline post-mortem, pwg_ru as the live
  operator procedure (production window step-by-step with traps inline, lanes +
  medium50 pause state, kill-gate mechanics, RU/EN parity contract, 216-script
  census with destructive-on-rerun table, data-assets/rights boundary).
  Fact-checked against sources; router row, PROFILE queue flip, and metadoc
  revision row in the same change. Fable 5 (`claude-fable-5`), 11-07-2026.

## [1.5.1] - 2026-07-11

### Fixed — FINDINGS.md duplicate section keys (H616)
- Repaired the seven accidentally duplicated `§N` citation keys found by the
  H604 fact-check: the later twin of each pair renumbered to a fresh key with a
  one-line tombstone under the renamed heading — §60→§70 (pwg_ru TM composite
  grade), §62→§71 (PWG case-government census), §63→§72 (VedaWeb `id_gra` =
  GRA `<L>`), §64→§73 (VedaWeb license fields), §65→§74 (ls-graph degeneracy
  for MW), §69→§75 (Devībhāgavata not on GRETIL). The second "§56" was a
  verbatim double-append of §68 (spellchecker landscape, PRs #305/#307) and was
  removed with a tombstone under §68. Header max-number marker corrected
  (§65→§75); stale citations of the renamed twins repointed in
  [`STALENESS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/STALENESS.md),
  [`ROADMAP_VEDAWEB_REUSE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_VEDAWEB_REUSE.md),
  [`RussianTranslation/PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md),
  [`RussianTranslation/USE_CASES.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/USE_CASES.md)
  and `RussianTranslation/.ai_state.md`; duplication caveats dropped from
  [`docs/manuals/MAINTAINER_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md) §3
  and [`docs/manuals/RESEARCHER_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RESEARCHER_MANUAL.md) §5;
  metadoc backlog item 4 closed.

## [1.5.0] - 2026-07-11

### Added — audience manuals
- New [`docs/manuals/`](https://github.com/gasyoun/SanskritLexicography/tree/master/docs/manuals):
  four deep, standalone manuals for distinct audiences — maintainer, researcher,
  student (Russian), and data-reuser — plus a
  [router README](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/README.md).
  Linked from the root README documentation map. Language follows audience
  (student = Russian; the rest English). Built under
  [Uprava H535](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H535-Opus_SanskritLexicography_audience-manuals-quartet_10.07.26.md).

### Changed — CLAUDE.md reflects the repo is now hybrid (data + code)
- Corrected the stale "no source code (no `.py`…)" and "Python/JS lint jobs …
  never fire because no such files exist" claims in
  [`CLAUDE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md):
  the repo now carries substantial Python (263 tracked `.py`, a root
  `requirements.txt`) and CI's Python lint + RussianTranslation gates do fire.
  Follow-up flagged under H535 (already noted in the maintainer manual).

### Added — other highlights since v1.4.0 (synthesized from git log; the tagged pwg_ru releases v1.2.0–v1.4.0 themselves are backfilled as sections below)
- Public PWG→RU translation **progress dashboard**
  ([PR #315](https://github.com/gasyoun/SanskritLexicography/pull/315)).
- pwg_ru article site: `<ab>`/`<ls>` tooltips + RU-column abbreviation purity per
  [`RussianTranslation/ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md)
  ([PR #308](https://github.com/gasyoun/SanskritLexicography/pull/308)); multi-second
  freeze on large articles fixed ([PR #320](https://github.com/gasyoun/SanskritLexicography/pull/320)).
- M01 literature crosswalk + 37-manual library metadoc, H505
  ([PR #319](https://github.com/gasyoun/SanskritLexicography/pull/319)).
- FINDINGS §66–§69 (QL SLP1 truncation, PWG article-size confound, spellchecker
  landscape, DBhP absence from GRETIL) and DEAD_ENDS/GAPS/ASSUMPTIONS episteme
  entries for the Sundara apparatus and F4-DCS edition-mismatch dead ends.
- Editorial rule applied repo-wide: drop `ё` (keep the всё/все distinction), H543
  ([PR #324](https://github.com/gasyoun/SanskritLexicography/pull/324)).

## [1.4.0] - 2026-07-06

pwg_ru pipeline release (tagged "pwg_ru 1.4.0"); section backfilled 11-07-2026
from the [GitHub release](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.4.0).
Full detail in
[`RussianTranslation/CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md).

### Added — no-PWG supplement-chain lane (H214)
- PWG-missing headwords with a PW/SCH/PWKVN/NWS record now render as standalone
  supplement-chain sub-cards (`<key>~~h0_zz_<layer>`), no fabricated PWG base
  portrait. Per-card `source_profile` (`no_pwg_supplement_chain` /
  `pwg_with_supplements` / `pwg_only` / `pwg_supplement_subcard`) on every
  promoted row; the 232 PWG-miss lemmas become a `no_pwg_runnable` lane. First
  live run validated end-to-end, 5 verified-clean sub-cards promoted; residual
  low single-card throughput tracked in H220.

### Added — upstream-change watcher (H182)
- [`RussianTranslation/src/pilot/watch_upstream.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/watch_upstream.py):
  monthly Cologne + NWS drift detection → stale-worklist; flag-only, on a
  scheduled workflow.

### Fixed
- `{{Lbody=NNNN}}` alternate-headword-pointer leak (`dict_merge.resolve_lbody()`)
  and the nominal audit crash (`audit_window.py` now skips glue for no-rootmap
  windows). PRs
  [#174](https://github.com/gasyoun/SanskritLexicography/pull/174),
  [#178](https://github.com/gasyoun/SanskritLexicography/pull/178),
  [#183](https://github.com/gasyoun/SanskritLexicography/pull/183),
  [#185](https://github.com/gasyoun/SanskritLexicography/pull/185).

## [1.3.0] - 2026-07-05

Section backfilled 11-07-2026 from the
[GitHub release](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.3.0).

### Changed — nominal-window guardrails (H191 verified, optimized, staged)
- H189 `pril10_w1` post-mortem verified deterministically: the aborted
  top-size nominal run reproduces to 42,316,604 tokens / ~$79.83, confirming
  fragment-level `agent()` fan-out plus repeated cache writes caused the
  blow-up.
- Generated harness size reduced for cached/retry windows: non-agent cards
  omitted from `INPUTS`/`PH`; TM-resolved and degenerate pass-through cards
  stay self-contained in `TM_RESOLVED` / `DEGENERATE_RESOLVED`.
- Monster handling hardened in two places: citation-dense single-line senses
  split only at complete `<ls>...</ls>` spans, and `perf_preflight.py` emits
  `cost_partition.run_now` / `cost_partition.defer_monster` grouped totals, so
  mixed windows run their cheap cards while `kAla`-class cards route to a
  human-budgeted lane.
- First safe nominal follow-up staged:
  [`RussianTranslation/src/pilot/NOMINAL_W1_100SMALL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/NOMINAL_W1_100SMALL.md)
  — 100 small Приложение 5 heads, 95 live inputs, 5 degenerate pass-through
  cards, 0 deferred monsters, 3 expected agents, ~745k tokens / ~$1.41
  estimated; the downstream Sonnet/Max run delegated to Uprava H201.

## [1.2.0] - 2026-07-04

Section backfilled 11-07-2026 from the
[GitHub release](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.2.0).

### Added — production ramp planning (runnable work, not wishful work)
- Live PWG→RU ramp planner `ramp_plan.py` (since retired) for the
  100 → 1,000 → 10,000 card progression, pricing each runnable root with the
  same preflight machinery used before Max spend; 10,000-card mode marked as a
  root-by-root drain (default concurrency 1, hard ceiling 3).
- H151 verb-root worklist made runnable-aware
  ([`RussianTranslation/src/pilot/verb_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/verb_worklist.py)):
  702 DCS-attested verb roots remained, 13 runnable, 689 blocked on rootmap
  generation/recovery. First controlled ramp target locked to runnable roots
  `tyaj`, `dah`, `kzip` (106 cards/sub-cards, 45 expected agents).

### Changed — QA gates fail loud, then requeue
- RU audit gate hardened: child auditors must emit strict `FLAGGED_JSON`;
  missing/malformed verdict lines crash loud and requeue the whole window.
- Real EN duplicate-sense hard gate added and gate-bug fixes ported across the
  EN path (language parity); Latin/Greek cue-masking leak fixed
  (`<ab>lat.</ab>` behind a placeholder is expanded for classification);
  collection/store writes made safer (robust JSON-string parsing, one parsed
  batch pass, coalesced appends).

### Added — schema-validated translation-memory publication assets
- Publication + terminology export commands for the TM lane: RU publication
  feed checksum-locked and schema-validated under `release/translation_memory/`
  (2,392 publication records pass validation); the `sa_ru_terminology` DOI lane
  intentionally empty until curated term suggestions exist; fuzzy TM matches
  advisory-only until validated.

### Added — review discipline + pipeline versioning
- Blocking
  [`RussianTranslation/src/review_changelog_guard.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_changelog_guard.py)
  hook: major review/audit edits must update the changelog in the same diff (or
  carry an auditable `Changelog: not applicable` marker); wired into pre-commit
  and CI.
- [`RussianTranslation/src/pipeline_version.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pipeline_version.py)
  + manifest `src/pipeline_versions.json`: a semver per output-affecting
  component family (prompt / glossary / script), orthogonal to the model
  version, stamped into every stored row's `provenance.pipeline` by both store
  producers — answers "which stored translations predate this tooling fix and
  need a batch re-run?". Forgotten-bump guard (content-SHA freeze + `check`
  warning), stale-row reporting, explicit-only backfill for legacy rows; store
  at introduction: 10,794 rows bucketed unversioned-legacy (not falsely marked
  stale), baseline frozen at v1.0.0.

## [1.1.5] - 2026-07-03

### Added — Indische Sprüche dataset
- New [`IndischeSprueche/`](https://github.com/gasyoun/SanskritLexicography/tree/master/IndischeSprueche)
  data asset: the full Böhtlingk *Indische Sprüche* collection (2nd ed. 1870–1873),
  7,537 sayings exported from `VisualDCS` archive.sqlite's `subhashita` table (D4)
  via the new `VisualDCS/src/DCS-data-2026/export_subhashita_jsonl.py`, as
  [`IndischeSprueche/data/indische_sprueche.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/data/indische_sprueche.jsonl).
  PWG cites this collection 6,666 times and PWK 138 times as `Spr. N` — see
  [`IndischeSprueche/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/README.md)
  for provenance and the scoped PWG/PWK citation-crosswalk follow-on
  ([Uprava H143](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H143_pwg_pwk_indische_sprueche_crosswalk.md)).

## [1.1.4] - 2026-07-03

## [0.0.42] - 2026-07-02

### Changed — A36 ready to send (Fable S9 pre-submission pass)
- [`papers/A36_latin_obscena_note.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_latin_obscena_note.md)
  reaches **5/5 ready-to-send** for *Beiträge zur Geschichte der Sprachwissenschaft*: referee-style
  review [`papers/A36_review_fable5.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_review_fable5.md)
  (7 major + 7 minor findings, all applied same pass — history-first retitle, Liddell–Scott /
  Cambridge-Greek-Lexicon comparandum in §0, Bopp-has-no-√yabh + MW72-etymological-*cunnus*
  source corrections against csl-orig, Adams register set re-defined, §3c table repaired; every
  table figure re-verified against the three CSVs). Cover letters (EN/DE) synced.
  ([PR #74](https://github.com/gasyoun/SanskritLexicography/pull/74)) — Fable 5 (`claude-fable-5`).

### Added — FINDINGS §44
- Raw Latin-string tallies over gloss text include etymological false positives (MW72's lone
  *cunnus* glosses a Lithuanian cognate); Bopp lacks √*yabh* entirely — reuse caveats for
  [`papers/A36_corpus_screen.csv`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_corpus_screen.csv).
  ([PR #76](https://github.com/gasyoun/SanskritLexicography/pull/76))

## [0.0.41] - 2026-07-02

### Fixed — dashboard: single-snapshot charts no longer render as a floating dot
- With only one monthly snapshot, each tracked-metric chart drew a lone centered dot in an
  empty box (looked broken). Single-snapshot metrics now render as a stat card (big value +
  "trend line appears with the next monthly refresh"); real multi-point series gain min/max
  axis labels, first/last month labels, gridlines, and an emphasized last point. Both states
  browser-verified (the multi-point branch against a synthetic two-snapshot series).

## [0.0.40] - 2026-07-02

### Added — FINDINGS dashboard (recurring visualization of the registry)
- New [`findings_dashboard/`](https://github.com/gasyoun/SanskritLexicography/tree/master/findings_dashboard):
  a single-file dashboard (vanilla JS + inline SVG, no build step) live at
  <https://gasyoun.github.io/SanskritLexicography/findings/> — importance × section matrix,
  staleness flags (> 180 days, 🔴-first), monthly time series for the re-measurable findings
  (§12 DCS→CDSL linkage, §13 glossary coverage, §21 citation coverage, §25 queue decay,
  registry size), and the §41 platform-liveness board (12 platforms).
- **Refresh = monthly, mixed:** GitHub Actions cron
  ([`findings-dashboard.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/findings-dashboard.yml),
  3rd of month) for registry meta + metric collection; a local Task-Scheduler run
  ([`monthly_refresh.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/findings_dashboard/monthly_refresh.py))
  for the platform probes, which need residential egress (GHA IPs are blocked by several
  hosts). Collectors verified against live values (81.4 / 86.6 / 83.2 / 0.82 %).
- Scope: public SL registry only — the private Uprava infra registry is deliberately excluded.
- Built by Fable 5 (`claude-fable-5`); page render browser-verified before publish.

## [0.0.39] - 2026-07-02

### Added — FINDINGS.md: importance labels on every finding
- Every finding (§1–§43) now carries a 3-level colour dot at the start of its claim line and
  index entry — 🔴 3 important · 🟠 2 medium · 🟡 1 not that important — mirroring the issue
  taxonomy's severity palette (minor/medium/hard). Legend + assign-on-append rule added to the
  schema. Same treatment in
  [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) (§1–§9).
  Plain emoji — no HTML; heading anchors untouched (dots live outside the headings).

## [0.0.38] - 2026-07-02

### Changed — FINDINGS.md: HTML Source styling reverted to plain blockquotes
- The v0.0.37 `<div align="right">` + `<sub>` Source styling was **rejected on review**
  ("looks ugly, never repeat") and removed same day. Every **Source** paragraph in
  [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  (and [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)) is now
  a plain blockquote `> **Source:** …` — left indent + GitHub's muted rendering, zero HTML.
  The no-HTML-in-md rule is restored as absolute (global rule, md-hygiene skill, and memory
  updated with the tested-and-rejected verdict). § numbering from 0.0.37 stays.

## [0.0.37] - 2026-07-02

### Changed — FINDINGS.md: § signs + right-aligned small Source lines
- Every finding number now carries the paragraph sign (`### §16. …`, mirrored in the index;
  anchors unchanged — GitHub strips `§` from slugs). Every **Source** paragraph is right-aligned
  small type via `<div align="right">` + `<sub>` — the one **sanctioned HTML** in the FINDINGS
  registries (grey text is impossible on GitHub around clickable links; right+small is the
  agreed stand-in). Same treatment in
  [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) (§1–§8).
  The global no-HTML-in-md rule, the md-hygiene skill, and memory carry the matching carve-out.

## [0.0.36] - 2026-07-02

### Changed — FINDINGS.md: numbered findings + Source as own paragraph
- Every finding in [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  now carries a paragraph number in its heading (1–40, **append-only** — a new finding takes
  the next free number, existing numbers never shift, mirrored in the index anchors), and each
  **Source** line is its own paragraph so it renders on a separate line. Same treatment applied
  to the [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) infra
  registry (8 findings).

## [0.0.35] - 2026-07-02

### Changed — FINDINGS.md restructured into an indexed, anchored registry
- [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md):
  every finding is now a `###` heading with a stable anchor, plus a MEMORY-style one-line
  index at the top (40 findings) — recall without reading bodies. Dated header + byline
  added; the intro's `PILOT_LESSONS`/`SHARED_CODE` links upgraded to full blob URLs.
- Re-sectioned: the four Sanskrit-data findings mis-filed under "Tooling & infra" moved to a
  new **Etymology & derivation** section / "Dictionary structure & markup"; the CodeQL-has-no-PHP
  finding moved to [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)
  (infra registry), leaving a pointer.

### Added — 15 new verified findings from a six-repo sweep
- Sweep of WhitneyRoots, VisualDCS, SanskritSpellCheck, csl-atlas, csl-apidev, csl-observatory,
  csl-corrections + this repo (6 parallel Fable 5 `claude-fable-5` Explore agents, then a
  dedicated Fable 5 fact-check agent re-verified every number against its source file — 12
  agent-reported inaccuracies corrected before commit). Highlights: DCS `OccId`/`sent_id` non-unique (134,047
  tokens / 449 sentences dropped pre-fix); UD `Tense=Past` conflates aorist/perfect; homonym
  token-split ceiling (5/38 gaṇa-splittable); Sa→Ru glossary 86.6 % token coverage; PWG∩MW
  union = 94,753; MW inherited PWG's apparatus skeleton (0.81 citation-order concordance);
  gloss-language ortho-drift ∝ reform type (RU 358/1k ≫ DE 10.3 ≫ FR/EN ≤ 0.5 ≫ LA 0);
  body-text headword mining dead end (38.6 % precision — negative result rescued from a
  deleted review artifact).
## [0.0.34] - 2026-07-02

### Changed — kosha planning-corpus triage (audit, 4 locked meta-decisions, scaffold removed)
- `KOSHA_FOLDER_SETUP.md` rewritten as an honest status doc (was "Setup Complete" over empty
  directories); `KOSHA_DECISIONS_NEEDED.md` blanks filled with real decisions (M1–M4;
  cadence/etymology left OPEN).
- Triage banners + inline fixes: real `<pc>` formats (MW page/column single-volume; PWG
  volume-page hyphen; AP90 page-column-letter), real Heritage/Cologne endpoints, current
  headword counts, VedaWeb/Lexonomy URLs, `union_headwords` marked already-built.
- `KOSHA_DEPLOYMENT.md` added: salvage of `kosha/DEPLOYMENT.md` + README API contract with
  4 config defects fixed (`Type=notify`, missing `proxy_pass`, `WorkingDirectory`,
  force-push advice).
- The `kosha/` scaffold in this repo deleted until code is real (M2: dedicated `kosha` repo;
  M4: own Pages). (Fable 5 `claude-fable-5`.)

## [0.0.33] - 2026-06-29

### Added — grammar-layer FAIR package + VedaWeb accent-axis probe (follow-up to 0.0.32)
- **Declension display** shipped (`nominal_grammar.py --table`, `reverse_index.py --show`) — vidyut
  paradigm table per headword / per paradigm token. Per-word grammar dataset materialized into
  `headword_index.tsv` (98,639 rows; kept out of translation — portraits untouched).
- **FAIR data package** `RussianTranslation/src/datapackage.json` (Frictionless, CC-BY-SA-4.0) over
  the five grammar resources with field schemas, sources, and deterministic-rebuild provenance;
  archivable on its own DOI track.
- **VedaWeb accent-axis probe CONFIRMED**: VedaWeb 2.0 API live (`vedaweb.uni-koeln.de/api`); the
  Casaretto et al. (2025) annotation layer returns udātta-marked, position-aligned per-word forms
  (RV 6.59.3: `…agnī́; ávasā; …devā́`) with co-located lemma+morphology and a bulk export — the
  accent a–f axis is de-risked (only the Whitney-rule encoding + join remain). Turnkey API path +
  resource IDs recorded in `ZALIZNYAK_INDEX.md` and `FINDINGS.md`.

## [0.0.32] - 2026-06-29

### Added — pwg_ru structured grammar layer (nominal grammar, Zaliznyak index, reverse dictionary)
- **Nominal grammar layer**: `RussianTranslation/src/nominal_grammar.py` (stem class, Whitney §§,
  vidyut subanta paradigm with the `nyap` fix for feminine ā/ī/ū stems) + `src/mw_compounds.py`
  (106,603 MW `<k2>` compound segmentations). Whitney exception §§ folded into the root layer
  (`whitney_grammar.json`, 289 records). Docs: `GRAMMAR_LAYER.md` (hub).
- **A/B test → grammar-in-translation REJECTED** (`NOMINAL_GRAMMAR_AB.md` +
  `NOMINAL_GRAMMAR_AB_DETAIL.md`): blind Opus judge over 8 stratified headwords, arm A (grammar
  OFF) 5 / tie 2 / arm B (ON) 1; both arms 0 nulls, 100% markup fidelity. Nominal windows run
  grammar **OFF**; the layer is kept as structured data only (portraits left untouched).
- **Zaliznyak inflection index** (`ZALIZNYAK_INDEX.md`): compact per-word token `G·T S F`
  (e.g. `m·8n*`); **reverse dictionary** over all 123,366 PWG entries → 98,639 indexed → 335
  paradigm tokens; per-word FAIR dataset `headword_index.tsv` + `reverse_paradigm_index.json` +
  `paradigm_stats.tsv`; **declension display** via vidyut (`--show` / `--table`).
- **Accent a–f axis** spec'd + unblocked: Whitney's per-case accent §§ already ingested + PWG
  `key2` accents + **VedaWeb** (CC BY 4.0) as the validation set; logged in `FINDINGS.md`.

## [0.0.31] - 2026-06-26

### Fixed — stale-doc cleanup across the pwg_ru planning/runbook set
- Aligned the `RussianTranslation/` docs with the current pipeline after the judge-escalation +
  harvest-port changes: corrected present-tense "Opus judges every card" claims to the
  Sonnet-bulk + Opus-on-reject policy (STRATEGY.md, FREQ_TEST_RUNBOOK.md, HANDOFF); marked the
  four prompt nits and the `--root-split` hook as done; noted the dropped `pwg_preverb1.txt`
  sandhi-join follow-up; added superseded-pointers to the pre-Max-harness plans
  (IMPLEMENTATION_PLAN.md, PIPELINE_ARCHITECTURE.md) and a "now-implemented" note to PILOT_COST §7.
  Correct historical statements (the Opus-run validation passes) were left intact;
  `research/JUDGE_POLICY.md` is the single source of truth for the judge policy.

## [0.0.30] - 2026-06-26

### Changed — pwg_ru judge escalation: Sonnet bulk, Opus only on hard cases
- Implemented the decided judge policy (`RussianTranslation/research/JUDGE_POLICY.md`) in the Max
  harness (`RussianTranslation/src/pilot/run_pilot_wf.js`): **Sonnet judges every card; Opus
  re-judges ONLY the rejects** (`ok=false || severity>=3`), Opus verdict final. Publishable cards
  (sev 1–2) spend no Opus tokens — the weekly-quota headroom that makes the bulk run feasible on one
  Max seat. Justified by the κ=1.0 / 474-card A/B (`JUDGE_AB.md`). Pipeline now 3-stage
  (Translate · Judge · Adjudicate); `node --check` clean. Runbook + policy docs marked implemented.

## [0.0.29] - 2026-06-26

### Changed — pwg_ru bulk-run preflight: harvest ported into the production harness
- **Launch-readiness audit** of the PWG→Russian bulk run (translator = Sonnet, judge =
  Opus 4.8). Verdict: GREEN to start the first instrumented window. Confirmed all four
  "pre-run prompt nits" already encoded in the Max harness and all gate scripts wired.
- **Literature-harvest refinements ported into the live harness**
  (`RussianTranslation/src/pilot/run_pilot_wf.js`, which inlines its own prompt and does not
  read `pwg_ru_prompts/*.txt`): samāsa right-headedness, the *yad…tad* correlative map,
  śāstric formula equivalents, synonym-string cardinality, comma/semicolon sense-grouping,
  manner/position forcing, plus a soft judge check. `node --check` clean.
- **Runbook + docs updated:** `RUN_FREQ_MAX.md` window loop (SECTION warning + fidelity-gate
  step); [`MANUALS_FIVE_DEEP_DIVE.md`](RussianTranslation/MANUALS_FIVE_DEEP_DIVE.md) closing
  section rewritten as a per-finding pipeline-status table (live / ported / deferred);
  `pwg_ru.md` gains a theoretical-basis pointer to the literature docs.

## [0.0.28] - 2026-06-26

### Added — literature shelf mined for the Sanskrit→Russian dictionary
- **Per-manual audit + theory deep-dive for pwg_ru.** Three new docs under
  `RussianTranslation/`: [`LITERATURE_FOR_PWG_RU.md`](RussianTranslation/LITERATURE_FOR_PWG_RU.md)
  (three-pass full-text harvest of the whole `literature/md/` shelf, distilled by pipeline
  insertion point), [`MANUALS_FOR_PWG_RU.md`](RussianTranslation/MANUALS_FOR_PWG_RU.md) (all
  **37** `Lexicography-Manuals/` walked one at a time — 19 drive theory, 2 marginal, 15 serve
  other repos, 1 OCR-blocked), and
  [`MANUALS_FIVE_DEEP_DIVE.md`](RussianTranslation/MANUALS_FIVE_DEEP_DIVE.md) (detailed,
  text-grounded theory of the five load-bearing manuals — Apresjan, Riemer, Hartmann & James,
  Gonda–Vogel, Klosa — for making a Sanskrit–Russian dictionary).
- **Harvest folded into the live pipeline:** the pwg_ru translator and QA-judge prompts plus a
  new hand-curated glossary `RussianTranslation/glossaries/de_ru_translation_aids.md` (samāsa
  types, case-absolute constructions, śāstric formulas, the *yad…tad* correlative map, the
  19th-c. German orthography decoder).
- **Literature index refreshed.** [`literature/md/INDEX.md`](literature/md/INDEX.md) gains the
  **⚠ blocked** convention (5 files un-mineable until re-OCR'd / re-extracted), RuTrans tags on
  Renou/Apresjan/Tubb, and ✓-fixed notes on the two re-sliced NLP-proceedings bundles
  (Adapting-NLP, Performance-POS). README documentation-map updated to point at the new docs.

## [0.0.27] - 2026-06-26

### Fixed — doc consolidation
- **Broken relative links repaired.** `union/UNION.md` (generated) linked its scripts and
  sibling TSVs with HeadwordLists-relative paths although the file lives in `union/`; fixed
  in `build_union.py`'s md generation (`../build_union.py`, `../screen_candidates.py`,
  same-dir TSVs) and the Catalan §7 `accent_review.py` link → `../accent_review.py`. All **143
  internal links across the 19 HeadwordLists md files now resolve** (0 broken).
- **`.ai_state.md`** gains a "Current status (2026-06-26)" header: HeadwordLists print-readiness
  agent-prep complete (A–F), pwg_ru Track A ongoing.
## [0.0.26] - 2026-06-26

### Added — accent disagreements rendered for adjudication (item C)
- [`accent_review.py`](HeadwordLists/accent_review.py) → [`Catalan-Pujol/accent_disagreements.tsv`](HeadwordLists/Catalan-Pujol/accent_disagreements.tsv):
  the **63** Pujol-vs-Cologne accent-position disagreements (32 vs GRA, 31 vs MW), each
  rendered as **accented IAST on both sides** (`bhagá` vs `bhága`) with the vowel ordinal and
  a `recommend` column (Cologne RV/MW canonical). The print list (the union) already uses the
  Cologne `<k2>` accents, so item C resolves to: **use Cologne accents; the 63 are a QA list
  for the Catalan editors**, not a change to the print list. §7 + PRINT_READINESS C updated.
- **All PRINT_READINESS agent-prep is now complete** (A–F): the remaining work is human
  verification/decisions, and the two headline findings stand — CDSL coverage of attested
  vocabulary is essentially complete (B), and the MW/PWG spine is gated only by 16 typos (A).
## [0.0.25] - 2026-06-26

### Changed — typo queue extended to all 122; coverage additions cross-tagged
- **A — all 122 typos.** [`assemble_typo_queue.py`](HeadwordLists/assemble_typo_queue.py) now
  auto-discovers every dict's FILE-FIRST queue → [`A_TYPO_QUEUE.md`](HeadwordLists/A_TYPO_QUEUE.md)
  is the full **122 across 11 dicts** (spine MW 4 + PWG 12 first, then SHS 37, YAT 27, ACC 22,
  MCI 10, SKD 3, WIL 3, PW 2, GST 1, VCP 1), each with IAST + error type + entry-body evidence.
- **B — cross-tagged.** [`crosstag_additions.py`](HeadwordLists/crosstag_additions.py) tags the 416
  priority additions with Catalan/Huet external attestation
  ([`union/coverage_additions_crosstagged.tsv`](HeadwordLists/union/coverage_additions_crosstagged.tsv)).
  **Only 25/416 (6 %) are externally corroborated, and ~8 are genuine real words** (`karkandhū`
  jujube, `maṇikā` jar, `cittamātra`, `nistaraṅga`…); the rest are verb roots / Pāṇinian affixes
  (`ghañ`, `ktvā`) Catalan/Huet also headword. **Conclusion: CDSL coverage of attested vocabulary
  is essentially complete — the print list needs ~nothing added.**
## [0.0.24] - 2026-06-26

### Added — MW+PWG typo queue assembled (item A)
- [`assemble_typo_queue.py`](HeadwordLists/assemble_typo_queue.py) consolidates the print
  spine's body-confirmed FILE-FIRST typos from
  [SanskritSpellCheck](https://github.com/gasyoun/SanskritSpellCheck) into
  [`A_TYPO_QUEUE.md`](HeadwordLists/A_TYPO_QUEUE.md): **16 (MW 4 + PWG 12)**, each with SLP1 +
  IAST, an **error-type** label (n→ṇ, vowel-length, sibilant, b↔v, aspirate) and the
  dictionary's **own entry-body evidence**. PWG's are mostly **b↔v** (Fraktur-OCR). Verify on
  scan → flip `n`→`y` → file to csl-corrections (workflow stays in SanskritSpellCheck). The
  spine's "don't print known typos" pass is now a 16-row checklist.
## [0.0.23] - 2026-06-26

### Added — coverage additions ranked by DCS band (item B)
- [`coverage_additions.py`](HeadwordLists/coverage_additions.py) → DCS-corpus lemmas absent
  from all 15 CDSL dicts (the union, with folded feminines added back to the baseline),
  ranked by frequency band: [`COVERAGE_ADDITIONS.md`](HeadwordLists/COVERAGE_ADDITIONS.md) +
  [`union/coverage_additions.tsv`](HeadwordLists/union/coverage_additions.tsv).
- **21,759 absent**, but the high-frequency end is **lemmatisation artifacts** (causative `-ay`
  stems, prefixed/desiderative roots, bīja, indeclinables — flagged by a `kind` column), not
  real gaps. Genuine **nominal** additions concentrate low-band; the **actionable priority =
  409 band-3 nominal** (e.g. `bhasmasūta`, `bhṛgutīrtha`, `āntarika`). Confirms the Catalan §5
  pattern: real coverage gaps are rare words. PRINT_READINESS B marked ranked.
## [0.0.22] - 2026-06-26

### Added — gloss pre-screen of the low-confidence fold candidates
- [`screen_candidates.py`](HeadwordLists/screen_candidates.py) pulls the short **MW gloss** for
  both forms of each of the 426 low-confidence `-ā/-ī` fold candidates →
  [`union/low_candidates_screened.tsv`](HeadwordLists/union/low_candidates_screened.tsv). Result:
  **419 likely-distinct** (reject at a glance — `ārā` "awl" vs `āra` "brass"; `īṣā` "carriage-pole"
  vs `īṣa` "the month Āśvina") and **7 MAYBE-related** to eyeball (`tālikā`/`tālika` same gloss;
  `adharmā`/`adharma`). Cuts the editor's low-set review from 426 to ~7; the gloss is the first MW
  sense (text after `</lex>`, before the first `<ls>` citation, etymology stripped).
## [0.0.21] - 2026-06-26

### Changed — union now covers all 15 dicts + fold candidates ranked
- **Fuller union.** `build_union.py` now reads `<k1>` directly from current csl-orig for
  **all 15 dicts** with a source (adds the 7 key2-only dicts BHS/BUR/CAE/CCS/INM/MD/SCH to
  the original 8) → **323,425** headwords (was 295,298), 180,989 in ≥2 dicts.
- **Fold candidates ranked for review.** The `-ā`/`-ī` candidates in
  [`union/fold_candidates.tsv`](HeadwordLists/union/fold_candidates.tsv) now carry a
  `confidence` (+ `n_shared_dicts`, `masc_gender`): **3,569 high** (the masculine base is
  itself `mfn`, so the `-ā/-ī` genuinely is its feminine — `parā←para`) vs **426 low** (masc
  `m`-only → likely a distinct lexeme like `āśā`≠`āśa`). Review high first. 237 `-inī`
  auto-folded. Gender is MW/AP-driven (BUR has no `<lex>`).
## [0.0.20] - 2026-06-26

### Added — cross-dict UNION headword index (scope E) with feminine fold (F)
- **Scope decided = union**, feminines folded under the masculine. [`build_union.py`](HeadwordLists/build_union.py)
  merges the 8 key1 dicts (AP GRA MW PWG PWK SKD VCP VEI) from `now-2026/` into a single
  **295,298-headword** index with per-headword **provenance** (which dicts attest it) and
  **gender** aggregated from each dict's `<lex>` (parsed per multi-line `<L>` record).
  → [`union/UNION.md`](HeadwordLists/union/UNION.md), `union/union_headwords.tsv`
  (`slp1, iast, n_dicts, dicts, gender, fem_fold`).
- **Feminine fold, gender-driven and split for safety:** only the unambiguous **`-inī`→`-in`**
  (238, gender-confirmed) is auto-folded — the masculine base gets an `mf(ī)` marker; the
  **3,993 `-ā`/`-ī`** cases go to [`union/fold_candidates.tsv`](HeadwordLists/union/fold_candidates.tsv)
  for editor review, because a feminine `-ā` noun often shares a stem with an unrelated
  masculine `-a` (e.g. `āśā` "hope" ≠ feminine of `āśa` "corner"). Auto-fold audit in
  `union/folded_feminines.tsv`. Covers the 8 key1 dicts; key2-only dicts mergeable next.
## [0.0.19] - 2026-06-26

### Added — item-F candidate lists (`alternate_headwords.py` + `f_candidates/`)
- Generated the editor worklists for PRINT_READINESS item **F**:
  [`alternate_headwords.py`](HeadwordLists/alternate_headwords.py) emits, from the 2026
  key1 sets, feminine↔masculine pairs, orphan feminines, variant-spelling pairs
  (b~v / ś~ṣ / geminate), and multi-`<k2>` alternate groups (SLP1 + IAST) into
  [`f_candidates/`](HeadwordLists/f_candidates/), summarised in
  [`ALTERNATE_HEADWORDS.md`](HeadwordLists/ALTERNATE_HEADWORDS.md). **MW: 5,036
  feminine↔masculine pairs, 22,298 orphan feminines, 1,217 variant pairs, 0 multi-`<k2>`**
  (alternate comma-lists negligible). SKD generated as a union-case sample. These are
  candidates to filter (morphological-shape pairing includes semantic non-pairs); the
  fold/keep/merge policy stays human.
## [0.0.18] - 2026-06-26

### Changed — PRINT_READINESS: add alternate/feminine headword gate (F)
- New checklist item **F — alternate & feminine headword policy** in
  [`PRINT_READINESS.md`](HeadwordLists/PRINT_READINESS.md). MW (2026) is **~14 % ā/ī-stems**
  (18,186 `-ā` + 9,148 `-ī`) and CDSL headwords feminines *inconsistently* — only 24 % of
  `-ā` feminines have a separate masculine base, 30 % of `-inī` have the `-in`. Pujol/INRIA
  list feminines separately; the corpus attests feminines CDSL omits. Plus variant/alternate
  spellings (b~v ≈ 397 MW pairs) and same-lemma multi-`<k2>` forms (comma-lists in SKD/VCP,
  which the now-2026 key2 split into separate lines). Policy (headword separately / fold with
  `mf(ā/ī)` / merge-and-cross-ref) is human; the candidate pair-lists are agent-doable. The
  MW/PWG print spine is largely unaffected (MW key2 = one clean form per entry).
## [0.0.17] - 2026-06-26

### Added — key2 re-extracted as SLP1 + a print-readiness checklist
- **key2 now regenerated as clean SLP1** into [`now-2026/`](HeadwordLists/now-2026/) for
  every dict (was key1-only). The 2014 key2 files are legacy numeric transliteration; the
  current `<k2>` is SLP1 but a naïve `<k2>([^<]*)` over-captured entry-body text / `{#..#}`
  compound blobs (a 64 MB dump). Fixed in `headword_diff.py` (`key2_forms`): stop the
  capture at the `¦` separator, strip `{#..#}`, split comma-lists → clean **print/citation
  form** keeping `/` accent, `-`/`—`, `(...)`, `*`, `˚` (e.g. `aMSa—karaRa`; SKD recovered
  40,817 vs the 64 MB blob). 23 now-2026 files (key1+key2; PD has no source).
- **[`HeadwordLists/PRINT_READINESS.md`](HeadwordLists/PRINT_READINESS.md)** — consolidates
  the A–E checks for publishing a printed headword list, with per-dictionary verdicts.
  **MW/PWG are the print-ready spine** (stable, +0.1 %/−0.0 % since 2014); the gates are
  human/editorial — **A** clear SanskritSpellCheck's 122 fileable typos (the "don't print
  known typos" pass, highest value), **B** coverage additions, **C** accents, **E** scope —
  while **D** (key2 as SLP1) is now closed.

## [0.0.16] - 2026-06-26

### Changed — foldered the snapshots (`then-2014/` + `now-2026/`) + % and TOTAL columns
- **Dated the snapshots.** The committed headword lists were verified (git) to have been
  extracted **2014-10-05** ("Cologne headwords"), so all 31 root `*.txt` now live in
  [`HeadwordLists/then-2014/`](HeadwordLists/then-2014/), and the current regeneration in
  [`HeadwordLists/now-2026/`](HeadwordLists/now-2026/) (was `now/`). Paths updated across
  the README, the Huet doc, and `huet_coverage.py`.
- **`NOW_VS_THEN.md` gains a `growth %` column and a TOTAL row.** Net change per list
  (e.g. **AP +146.6 %**, PWK +14.7 %, MW +0.1 %) and the aggregate over the 9 comparable
  lists: **605,813 → 733,617 (+21.1 %)**; grand total of all 26 snapshots' then-counts =
  1,721,983.

## [0.0.15] - 2026-06-26

### Added — `HeadwordLists/now/` current regeneration of the key1 snapshots
- Regenerated the **key1** lists from the **current** csl-orig into
  [`HeadwordLists/now/`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026)
  (renamed `now-2026/` in 0.0.16; filename = now-count), Sanskrit-collated;
  the parent THEN files are kept frozen so the two can be compared directly.
  `headword_diff.py now` produces them.
- **key1 only, deliberately** — it's the genuinely comparable set (THEN and NOW both
  SLP1 `<k1>`). key2 is skipped: the THEN `<k2>` is legacy numeric transliteration
  (format migration, not a headword diff), and several dicts' raw `<k2>` is `{#..#}`
  compound blobs, not lemmas (a naïve dump was 64 MB of markup). 8 written
  (AP, GRA, MW, PWG, PWK, SKD, VCP, VEI); PD has no csl-orig source.
- Notable now-counts: **AP 88,867** (was 36,030), **PWK 151,349** (was 131,918),
  **MW 194,084**, PWG 106,082, VCP 48,636. `now/README.md` documents scope + the
  Sanskrit-collation (compare by set, not line-diff) caveat; refreshed `NOW_VS_THEN.md`
  to match (csl-orig had drifted a little since the previous run).

## [0.0.14] - 2026-06-26

### Added — `HeadwordLists/` drift tooling, Huet/INRIA control, accent check, use cases
- **Now-vs-then diff of the `*-unique-key{1,2}-N.txt` snapshots.** `headword_diff.py`
  regenerates each list from current csl-orig; `NOW_VS_THEN.md` is the summary. The
  **key1** (SLP1) lists are comparable and have drifted: **AP 36,030 → 88,701**,
  **PWK 131,918 → 151,349** (large real growth), **MW 193,978 → 194,084** (+753/−647),
  PWG/GRA/SKD/VCP/VEI small. The **key2** snapshots are in the *legacy Cologne numeric
  transliteration* (`am2s4a` = aṃśa) vs current SLP1 — a format migration, flagged not
  reported. PD is not in csl-orig. (`removed`-word lists embedded for QA; scratch
  `_diff/` dumps gitignored.)
- **Huet / INRIA Heritage wordlist** — a non-Cologne control alongside Catalan-Pujol.
  `huet_coverage.py` decodes Huet's VH/Velthuis (`z`=ś, `f`=ṅ, `.s`=ṣ, `aa/ii/uu`) to
  IAST→SLP1 and runs the same coverage. 21,055 keys, **MW 83.5 % / all CDSL 86.2 %,
  DCS-attested 60.0 %**. Headline ([`Huet-INRIA-Wordlist-vs-Cologne.md`]): both are MW
  subsets, but the reader's lexicon is far more corpus-attested than Pujol's full
  dictionary spine (60 % vs 46 %) — less dictionary "dark matter".
- **Catalan-Pujol additions.** The full 177-lemma corpus-attested-no-CDSL list
  (`DCS-attested-no-CDSL.md`, §5, triaged); the **accent comparison** (§7,
  `accent_compare.py`): Pujol marks udātta with a combining acute, Cologne with `/`
  after the vowel, but **~97 %** agree on position (GRA 96.9 %, MW 97.1 %).
- **Use-case sections** added to all three studies: Catalan-Pujol §8 (CDSL gloss layer,
  corpus-confirmed candidate headwords, editor QA list, morphology overlay, learner's
  layer), Huet §5 (corpus-weighted core vocab, VH↔SLP1 bridge, benchmark), and
  `NOW_VS_THEN.md` (snapshot refresh, removed-word audit, re-transcoding triage).

## [0.0.13] - 2026-06-26

### Added — `HeadwordLists/Catalan-Pujol/` dataset + full coverage analysis
- **The dataset.** An external Sanskrit headword spine and its CDSL/corpus coverage
  analysis: the **61,266-lemma list** of the *Diccionari Sànscrit–Català* (Òscar Pujol,
  Enciclopèdia Catalana, 2005 — the first Sanskrit→Catalan dictionary), mirrored from
  `sanskrit-lexicon/CORRECTIONS`. In accented IAST with `√`-roots, Vedic udātta, and
  Pujol's compound-segmenting hyphens; UTF-8 **with BOM**.
- **Dictionary axis** — the list is essentially a Monier-Williams subset: **MW alone
  covers 88.5 %**, all 15 compared CDSL dicts together 91.0 %; the ~4,680 lemmas no CDSL
  dictionary covers are bucketed (simple / compound / root / prefixed-root / suspect-char)
  under `Catalan-uncovered/`. Two transcoding traps documented (display-added line
  numbers; `ś`=s+U+0301 accent collision; match rate 78 %→89 % after the fix).
- **Corpus axis (vs DCS)** — only **46.4 %** of the list is attested in the DCS-2021
  corpus though 91 % sits in a dictionary; **44.9 % is dictionary-listed but
  corpus-unattested** ("lexicographic dark matter"). The 0.3 % (177) corpus-attested with
  no CDSL entry is **triaged**: ~55 lemmatisation/morphology convention (41 prefixed/
  denominative verb roots, 9 productive `-tā/-tva/-tara/-tama/-vat`, 5 bīja), 29
  unheadworded compounds, ~93 simple/feminine — within which a genuine residue of
  corpus-attested **rare lexemes absent from all 43 CDSL dictionaries** (plant/animal
  names: `alasāndra-` cowpea, `kustumburī-` coriander, `kaṅkolī-`, `udumbarī-`, …) are
  real candidate additions.
- **Pujol's 11 headword conventions documented** (§6): `√`-roots, preverb+root
  segmentation with `√` on the final root, sandhi-resolution parens, Vedic udātta,
  compound hyphens, stem/feminine/productive-suffix forms, homograph numbering, bīja
  syllables, BOM + precomposed-`ś` encoding, and export artifacts.
- **Scripts** (repo-portable, IAST→SLP1 via `sanskrit-util`): `coverage_by_dict.py`,
  `match_rate.py`, `make_uncovered_lists.py`, and `coverage_vs_dcs.py` (dictionary ×
  corpus cross-tab against `VisualDCS/dcs_lemma_summary.json`). Full write-up in
  `HeadwordLists/Catalan-Pujol/Sanskrit-Catalan-Wordlist-vs-Cologne.md`; indexed in
  `HeadwordLists/README.md`.

> Provenance note: the dataset files were first committed in `56564a0` (initially via an
> accidental `git add -A`), then adopted and refactored repo-portable by a parallel
> session (`75b917d`); kept by decision. This entry consolidates all Pujol work.

## [0.0.12] - 2026-06-26

### Changed
- **`article-comparison/*.table.md` — rows ordered chronologically by edition year**
  (oldest → newest), so the side-by-side reads as the lexicographic tradition
  developing: WIL 1832 → YAT 1846 → BOP 1847 → PWG (Bd. I) 1855 → … → AP 1957 →
  PE 1975 → PD 1976. The `#` column renumbers to the new order. Sorting is in
  `_build_tables.py` (stable on the prior order for same-year ties, e.g. BUR/BEN 1866,
  GRA/VCP 1873, pw/PWK 1879).

## [0.0.11] - 2026-06-25

### Changed
- **`article-comparison/*.table.md` — full, untruncated entries.** The side-by-side
  tables previously capped each cell at ~800 chars with a trailing ` …`, so longer
  entries (e.g. STC, PWG, AP90, VCP, PE) showed only a fragment. Every cell now
  carries the **complete** condensed entry (citations in `[ ]` stripped, SLP1→IAST,
  paragraphs joined with ▸); PD remains its full sense skeleton (its verbatim entry is
  20–234 KB and stays in the verbatim/IAST files). 40 truncated cells expanded.

### Added
- **`RussianTranslation/src/_build_tables.py`** — the table builder, now committed (it
  never was). Regenerates all four tables from the full `*.iast.md` sections (+ the
  `*.pd-min.md` skeleton for the PD row), reproducing the original condensation but
  without the length cap, and with **nested-citation-safe** bracket stripping (fixes a
  stray `]` the old run left on `[m., [RāmatUp.]]`-style nested refs, e.g. akṣara/MW).

## [0.0.10] - 2026-06-25

### Added
- **`article-comparison/agni.gloss-review.md` — agent draft review of agni's 130
  hand-authored RU sense-glosses.** An Opus-4.8 editorial pass against the English PD
  sense + Sanskrit term + Russian Indological norm (Kochergina / Elizarenkova),
  produced as a **sign-off worklist** (the glosses themselves are untouched — they
  remain the draft they were flagged as). Findings: 1 factual category error (the
  *agnicayana* altar↔rite mix-up at senses 4i/4vi), 3 transliteration/precision fixes
  (ахаванья→ахавания; hotṛ "возливатель"→"призыватель"; udātta), 3 optional polish,
  4 optional add-glosses, and 6 English-source OCR typos already corrected in the RU.
  This is the agent-doable half of the Track B gloss review; final scholarly sign-off
  is the human step.

## [0.0.9] - 2026-06-25

### Changed
- **`article-comparison/*.table.md` — multi-volume Petersburg dictionaries now name
  the volume, not just the span.** A 7-volume dictionary's true year is the year of
  the *volume* containing the headword's letter. All four study words are a-stems, so
  the PWG / pw / PWK labels now read **Bd./Th. I** with the volume-1 year (PWG
  `Bd. I, 1855`; pw/PWK `Th. I, 1879`) instead of a bare year that read as the whole
  1855–1875 / 1879–1889 run. Header note explains the volume convention.

## [0.0.8] - 2026-06-25

### Changed
- **`article-comparison/*.table.md` — every quote now carries its dictionary's
  edition year.** Previously only a few EN dictionaries showed a year (MW 1899,
  AP90 1890, WIL 1832, MW72 1872); the Dictionary column now labels all 20 sources
  with their CDSL edition year — e.g. PWG 1855, pw/PWK 1879, GRA 1873, VCP 1873,
  SKD 1886, SHS 1900, BUR 1866, CAE 1891, BEN 1866, YAT 1846, BOP 1847, STC 1932,
  AP 1957, PE 1975, PD 1976. Years are taken from the authoritative
  [CDSL front page](https://www.sanskrit-lexicon.uni-koeln.de/) catalog (via
  `csl-guides/src/data/dictionaries.json`), the same source as the existing labels;
  a provenance note was added to each table header.

## [0.0.7] - 2026-06-25

### Changed
- **`article-comparison/` — Max-LLM residual per-sense pass (Track B tail).** Each
  attested Russian rendering the deterministic matcher left in the
  `### Не привязано к значению` bucket of every `*.persense-ru.md` was adjudicated
  by an Opus-4.8 pass against the full bilingual PD sense skeleton and routed to a
  specific sense — or kept as honest "other" (function-word / context / off-headword
  name). Per-sense coverage rises to **97–100 %** (`agni` 100 %, `akṣara` 99 %,
  `anya`/`ananta` 97 %). Implemented as a reproducible `LLM_ASSIGN` override map in
  `RussianTranslation/src/_build_persense_ru.py` (surface form → sense ordinal,
  mirroring `SYN`/`ROUTE`); LLM-assigned renderings carry a **°** marker and the
  coverage line reports the deterministic-vs-LLM split.

## [0.0.6] - 2026-06-25

> Backfilled to match tag `v0.0.6` (cut by a parallel actor against the project
> narrative `RussianTranslation/CHANGELOG.md`); this section records the same scope
> in the semver changelog.

### Added
- **Renou *register* axis** — an orthogonal multi-label `renou_register` field
  (20-code lattice: épigraphique, bhāṣya, jaina, …) parallel to the I–V Renou
  *state*, per `RussianTranslation/RENOU_SUBSECTIONS_PLAN.md`. Two provenance-tagged
  detector routes (DCS corpus `build_dcs_renou.py` + `<ls>` citation
  `renou_register.py`) plus a dedicated `épig` detector; wired end-to-end through
  `renou_audit.py` (register mode) and `renou_portrait.py`. The state axis is
  unchanged.

### Changed
- **Judge-model A/B settled — Sonnet bulk judge + Opus repass/audit.** Across
  ~650 judged cards a Sonnet QA judge is statistically indistinguishable from Opus
  (κ = 1.0 on real cards; both 99 % recall / 0 % FP on a 250-item ground-truth
  defect battery). Policy: Sonnet judges the bulk, Opus re-judges every reject + a
  ~5 % audited sample. New `src/judge_disagreements.py` / `src/judge_ab_score.py`.
  The synthetic semantic-defect test was dropped (a word-pair gloss is undecidable
  out of context). See `RussianTranslation/research/JUDGE_AB.md` / `JUDGE_POLICY.md`.

## [0.0.5] - 2026-06-25

### Added
- **`article-comparison/` — one headword across every CDSL dictionary.** A study
  comparing four "a-" headwords — `agni`, `anya` (non-samāsa) and `akṣara`,
  `ananta` (a-samāsa / nañ-privative) — each chosen as most-frequent in DCS 2026
  **and** present in the unfinished Deccan **PD** dictionary (PD's "a" stops at
  ~`apaca-`, the real constraint). Six views per word: `.table.md` (side-by-side
  all dicts, SLP1→IAST), `.pd-min.md` (PD `{@..@}` sense skeleton),
  `.pd-min.ru.md` (bilingual EN/RU), `.corpus-ru.md` (attested Russian from the
  DeepSeek word-alignment lexicon + published SamudraManthanam verse pairs),
  `.persense-ru.md` (each rendering hung under its PD sense, 88–99 % coverage),
  `.verbatim.md`/`.iast.md` (full). Builders in `RussianTranslation/src/`
  (`_build_corpus_ru.py`, `_build_skeletons_ru.py`, `_build_agni_ru.py`,
  `_build_persense_ru.py`). Audited; 2 per-sense assignment bugs fixed. Headline:
  the per-sense attested-RU split (`agni`→Агни/огонь, `akṣara`→слог/Непреходящее,
  `ananta`→бесконечный/Ананта).
- `RussianTranslation/src/run_batch.py review_csv` exports the existing
  `_review_queue.jsonl` human worklist to `_review_queue.csv` for spreadsheet
  review. The CSV keeps the severity-sorted machine evidence and adds blank
  `reviewer_id` / `decision` / `edit` / `notes` columns without advancing any
  review state.
- `RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md` and
  `RussianTranslation/src/gold_review_csv.py` define and export the human
  precision-review scaffold: 320 balanced `period × kind` rows, LLM labels kept
  separate from blank human-label/adjudication columns.
- `RussianTranslation/schemas/pwg_ru_lexicographic_portrait.schema.json` and
  `RussianTranslation/src/validate_portrait_schema.py` define a v1 Apresjan
  portrait contract and validate live `microstructure.portrait()` output.

## [0.0.4] - 2026-06-23

_(Backfilled 2026-06-25 — this release was tagged and published on GitHub but
not previously recorded here.)_

### Fixed
- **NWS attribution: the `av` `+ upa` owner slide root-caused & gated.**
  `compile_translatable.mask_nws_gloss` strips the leading owner *bleed* — a
  roman-numeral co-owner cite (`Rivelex (2) : XLV`) that `nws_split`'s digit-only
  OWNER can't tag was riding onto the next gloss's prose and misleading the LLM
  assembly. `nws_split` OWNER now stops at `;`; `check` uses word-boundary locator
  matching (kills the `apāṃ`-in-`apāṃpitta` false MISATTRIBUTION).

### Added
- **NWS attribution gate** (`run_real_test.py audit`): a fresh non-protected card
  whose NWS owners disagree with the deterministic `nws_split` parse is rejected
  (→ `<safe>.merged.REJECTED.md`, re-queued; run exits non-zero); protected
  hand-authored cards are audited but never quarantined.

## [0.0.3] - 2026-06-19

### Added
- `RussianTranslation/src/pilot/run_real_test.py` — driver for the real-conditions
  pilot test (run locally on the Max subscription, two phases, one command each):
  `prep [N] [OFFSET]` selects a coverage-first a-section batch, marks fresh vs
  protected (hand-authored `aMSa`/`anna`/`ap`) cards, and sets the workflow's
  `OFFSET`/`LIMIT`; `audit <wf_output.json>` renders via `_pilot_collect.py`,
  runs `nws_split.py check` per card, and reports judge pass rate +
  NWS-attribution (F12) clean count + misattributions.
- The audit phase was pre-flighted with a synthetic `ap` workflow output:
  collect → protected-card preservation → `nws_split.py check` → report. Result:
  publishable 1/1, NWS audit CLEAN 1, F12 misattribution 0.
- Materialized the human-review worklist with `run_batch.py review`: 217
  `legacy_needs_review` cards, severity-sorted, with no reviewer decisions
  advanced.

### Changed
- `RussianTranslation/src/pilot/run_pilot_wf.js` — the translate→judge workflow is
  now **manifest-driven** instead of a hardcoded 15-key list: it reads
  `scale_route.py`'s coverage-first `scale_manifest.<section>.json` and runs a
  `[OFFSET, OFFSET+LIMIT)` slice (editable consts), so the full a-section's 12,155
  inputs can be translated in successive batches. Falls back to the original 15-key
  pilot list if the manifest can't be read. Verified: a 30-card batch resolves
  30/30 inputs on disk via the shared `safeName()` stem.
- `run_pilot_wf.js` translator prompt — new **HARD RULE 5 (NWS layer format)**:
  render the NWS "Kleines Zitat" fragment as ONE entry per source, tagged `[NWS:]`,
  keeping each OWNER citation (`Author year : page`) verbatim as the last citation,
  never merging/compressing owners, never sliding the owner onto the next gloss
  (failure F12 reading-direction trap), sub-lemmas as first-class rows. Encodes the
  format the deterministic `nws_split.py` auditor requires — found while validating
  the loop manually on card `ap` (2026-06-19): the translation was sound but the
  first draft failed the audit purely on output format; the rule makes future cards
  audit-ready (re-checked: `nws_split.py check ap` → CLEAN, 0 misattributions).
- `_pilot_collect.py` now writes audited `<safe>.merged.md` files directly using
  the shared `safe_name()` encoder; `run_real_test.py` no longer uses the brittle
  external `<key>.md` → `<key>.merged.md` copy bridge.
- `run_real_test.py prep` was refreshed for the June-22 batch window
  (`OFFSET=0`, `LIMIT=10`): `as As Ap api amfta agni Atman anu arjuna arTa`,
  now correctly all fresh after exact-case output checks.

### Fixed
- Legacy `.merged.md` compatibility checks now require exact filenames, avoiding
  Windows case-insensitive false positives such as `Ap` being treated as protected
  because `ap.merged.md` exists.
- Generated the missing writable a-section input for `arI|a` (`|` escaped as
  `~007c`); pilot inputs now cover 12,156/12,156 a-section manifest cards.

## [0.0.2] - 2026-06-19

### Fixed
- **Case-collision in pilot input filenames (F10) — silently dropped 1,237 of
  12,156 a-section cards.** SLP1 headword keys are case-sensitive (`api`/`Api`/`ApI`,
  `as`/`As`/`aS`) but Windows filenames are not, so `_pilot_gen_merged.py` writing
  `<key>.raw.txt` made case-variants overwrite each other — including high-value
  heads (`api`, `arTa`, `As`, `aNga`), whose translation inputs held the wrong
  variant's content. Applied the NWS scraper's proven `safe_name()` (uppercase →
  `_`+lower, injective) across every reader/writer of these files
  (`_pilot_gen_merged.py`, the superseded `_pilot_gen.py`, `nws_split.py`, and the
  JS workflow `run_pilot_wf.js` with a matching `safeName()`); Python/JS encodings
  verified identical. The full a-section regenerated CLEAN (12,155 distinct files =
  12,155 by-key lookups, no collisions; 1 unwritable, `arI|a`, which contains a `|`).
  Also added per-card error-resilience so a single unwritable key no longer aborts
  an 11k-card run.

### Added
- `_pilot_gen_merged.py` now supports a manifest-driven scaled mode
  (`--manifest <section> --limit N`) driven by `scale_route.py`'s coverage-first
  order, used to generate the **full a-section** merged+NWS inputs (12,155 cards;
  PW 90 % / SCH 13 % / PWKVN 10 % / NWS-extra 35 %). `nws_split.py` (deterministic
  NWS "Kleines Zitat" splitter, F12 audit tool) is now tracked.

## [0.0.1] - 2026-06-18

### Added
- **NWS layer fully scraped, drift-validated, and folded into the merge spine.**
  `RussianTranslation/src/nws_scrape.py section all` captured all **167,990**
  headwords of the *Nachtragswörterbuch des Sanskrit* (Halle); `_nws_audit.py all`
  = CLEAN (0 missing / 0 case-collisions / 0 dups / 0 refusals), net-new
  `has_nws_extra` = 34,101 (20 %). `_nws_drift.py all` confirms the a-section's "LOW
  staleness" finding across the whole dictionary (Schmidt 96.7 % identical, mean
  Jaccard 0.987; pw 80.9 % overlap, only 0.1 % NWS-only). `dict_merge.merged()` now
  appends NWS as a 5th "external" layer — net-new only, per-key on demand, kept out
  of `LAYERS` since it adds no new headwords. (NWS scraped data stays gitignored and
  provisional pending a formal Halle data request.)
- **Merged+NWS pilot scaled from 6 hardcoded keys to a manifest-driven run.**
  `_pilot_gen_merged.py --manifest <section> --limit N` consumes `scale_route.py`'s
  coverage-first manifest to generate full layered inputs (PWG+PW+SCH+PWKVN+NWS) at
  volume, resumable. On the top-300 dense a-section heads, NWS-extra coverage reaches
  95 % (vs 20 % dict-wide). `RussianTranslation/DICTIONARY_CHAIN.md` updated with the
  all-sections scrape/drift/fold status.

### Fixed
- `_pilot_gen_merged.py` resumable skip now verifies a pre-existing `<key>.raw.txt`
  is actually in merged (`=== LAYER:`) format. The superseded PWG-only `_pilot_gen.py`
  writes the same filenames in `=== RECORD` format; trusting mere file existence
  silently skipped ~17 of the top-300 cards (e.g. `api`, `Atman`), leaving them
  un-merged. Now those stale files are regenerated.

## [1.1.3] - 2026-06-15

### Fixed
- `RussianTranslation/src/corpus_gate.py` — `tune` now draws a reproducible
  random sample (same fixed seed as `coverage`) instead of the first N keys, so
  mid-size runs are representative. A random 4000-sample matches the full-PWG
  agreement shape (head-term Jaccard ≥0.5 ≈3.6% vs the full 3.7%); `n ≥ total`
  still reports the full run (106,085 headwords, 2,585 ≥2-dict pairs). Completes
  the random-sampling fix begun for `coverage` in 1.1.2.

## [1.1.2] - 2026-06-15

### Fixed
- `RussianTranslation/src/corpus_gate.py` — `coverage` now draws a **random**
  sample (fixed seed, reproducible) instead of the first N keys. PWG headwords are
  SLP1-sorted and the `a-` section is over-covered (especially KOW), so first-N
  coverage badly overstated true numbers (3000-sample KOW was 39.8% vs the full
  8.0%). The corpus signal also gets its own random sub-sample. A random
  3000-sample now matches the full run (independent correctness 16.6% vs 16.4%,
  KOW 7.0% vs 8.0%, corpus ~15%). Full-PWG coverage of 106,085 headwords:
  independent correctness ≈16%, KOW reference ≈8%, corpus ≈15%.

## [1.1.1] - 2026-06-15

### Fixed
- `RussianTranslation/src/corpus_gate.py` — the stage-4 corpus query returned 0
  aligned verses for common headwords (agni, rāma, kṛṣṇa, deva). `corpus_lines`
  (FTS) also holds dictionary rows (no `#sa`/`#ru` suffix); the query did
  `MATCH ? LIMIT 400` with no `#sa` filter in SQL, so for high-frequency words the
  first 400 matches were all dictionary rows and the Python `#sa` filter discarded
  every one. Pushed the `#sa` filter into SQL so `LIMIT` captures Sanskrit verse
  lines. Found while validating the gate end-to-end (lookup/card/coverage/tune all
  run; 5 dictionaries = 57,640 entries; coverage on a 3000-key sample: independent
  correctness 20.4%, KOW reference 39.8%, corpus 20.7%).

## [1.1.0] - 2026-06-14

### Added
- `RussianTranslation/pwg_ru.md` + `RussianTranslation/pwg_ru_prompts/` — scaffold
  for the **planned** Russian translation of the German Petersburg dictionary
  (PWG, Böhtlingk–Roth), mirroring the `mw_ru` kit. Editor-facing doc
  (`pwg_ru.md`: a card-format guide for a German source — the `{%…%}`
  German-gloss vs. Latin rule, the placeholder scheme, the `mw_ru`-seed
  mechanism) plus five stage prompts: `1_perevod.txt` (German→Russian translate
  with a 179+80-pair DE→RU glossary), the two QA judges
  (`2_qa_sudya_opus.txt`, `2_qa_sudya_yandexgpt.txt`),
  `3_pereperevod_opus.txt` (re-translate rejects), and a new
  `4_korpus_proverka.txt` — a non-blocking, two-signal Sanskrit→Russian corpus
  gate (independent-correctness + KOW reference-agreement). The translation
  pipeline itself is framed as planned/not-yet-run.
- `RussianTranslation/src/` — the stage-4 corpus-gate layer (code only; the
  `*.jsonl` dictionary data is gitignored, regenerated by `build_src.py`):
  `build_src.py` extracts five SLP1-keyed Sanskrit→Russian dictionaries from the
  sibling SamudraManthanam corpus (Kochergina 29,177; Kossovich/KOW 13,488;
  Knauer 3,271; Frisch/FRI 8,156; Smirnov 3,548 — ≈57,640 entries); `corpus_gate.py`
  joins a PWG headword to those dictionaries (+ optional SamudraManthanam parallel
  corpus) and emits the `4_korpus_proverka.txt` input, with coverage/tune modes.
- `RussianTranslation/SAMUDRA_INTEGRATION.md` — roadmap for how the sibling
  SamudraManthanam parallel-corpus tool feeds the Russian-translation projects
  (`pwg_ru`, `mw_ru`) and the WhitneyRoots crosswalk; separates built from
  planned, with verified extraction counts only.

### Notes
- The PWG corpus-check gate (stage 4) is designed as a **non-blocking annotator**
  emitting two separate signals per card: (1) *correctness* against independently
  compiled Sanskrit→Russian dictionaries (Kochergina, FRI, KNA), and
  (2) *reference-agreement* against KOW — itself a partial human PWG→Russian
  translation (Wilson-derived), so used only as a secondary, non-decisive
  reference, never to decide correctness. SKD/VCP are Sanskrit→Sanskrit and serve
  as Sanskrit-side sense corroboration only, never as a Russian authority. The
  five correctness/reference dictionaries are now extracted into
  `RussianTranslation/src/` from SamudraManthanam (≈57,640 SLP1-keyed entries);
  coverage is measured at ingest, not a blocker.

## [1.0.2] - 2026-06-14

### Added
- `HeadwordLists/README.md` — index of the headword exports: SLP1/Velthuis
  encoding, the `{DICT}-unique-{key1|key2}-{N}` naming (with the `wc -l` = N−1
  trailing-newline caveat), variant patterns (`fehlerhaft` = full XML records,
  `accents-IAST`, count-prefix, the HK aggregate, the 41 MB `sanhw1.xlsx`),
  key1/key2 semantics, the two-MW-key2 version note, the BOM-inconsistency
  caveat, and a 16-code dictionary table cross-checked against the CDSL site
  (resolves PD = Encyclopedic Dictionary on Historical Principles, CCS =
  Cappeller Sanskrit→German).
- `REFERENCES.md` — provenance (source, date, producer, size) for the root
  reference assets (`CDSL-2025.pdf`, the two DCS HTML exports,
  `helpmorphids.html`, `gasuns_cologne-zograf_2019.pdf`, and the previously
  unlisted `WSC 2025 Reviews 7.pdf`, since renamed `WSC2025_Reviews_7.pdf`),
  read from each file's own metadata with
  inferred descriptions flagged; linked from the README Contents table.
- `README.md` — new "Documentation map" section grouping every doc by purpose
  (Orientation; Contributors & agents; Material by area) with a one-line hook
  and link each, so a newcomer can find the right entry point.

### Changed
- `CONTRIBUTING.md` — expanded from the 3-step stub: formalised the data-change
  provenance expectation (source + transformation + counts/checksums) that
  previously lived only in README prose, plus filename-count and BOM conventions,
  a Documentation-changes section, and a Hygiene section.

## [1.0.1] - 2026-06-14

### Added
- `CLAUDE.md` — repository-level guidance for Claude Code. Documents what is
  specific to this data/research workspace (no source code): `HeadwordLists/`
  naming and key1/key2 semantics, the inconsistent UTF-8 BOM state across
  exports, the `mw_ru` translation format invariant, and the lint-only
  CI/pre-commit expectations. Ecosystem/workflow/taxonomy conventions are
  deferred to the org-level `../CLAUDE.md`.
- `Syntax-Lectures/sanskrit_particles_explorer.html` — a self-contained,
  Russian-language interactive explorer that digests the particle lectures for
  students: a clickable positional map (Zaliznyak / Wackernagel) over 16
  particles, with per-particle function, examples (deep-linked to the Gītā/Manu
  parallel corpus, Whitney, Speyer, Archive.org and DCS), Gonda/König/Hock
  citations, the full bibliography, and the folded-in Apte (1957) dictionary
  entries for the seven particles that have them. Built from
  `sanskrit_particles_lectures.md`, `sanskrit_particles_schema.html`, and the
  `Apte_1957-*_RU.md` series.
- `Syntax-Lectures/README.md` — Russian index of the particle materials: a
  start-here pointer to the lectures conspect, a table of the three primary
  files (lectures, the Zaliznyak positional schema, the interactive explorer),
  and a mapping of the seven `Apte_1957-*_RU.md` particle entries (those of the
  16 explorer particles that have an Apte article).
- `RussianTranslation/mw_ru.md` — new section 7 "Внешние документы", an
  appendix tabling the six files referenced from the mw_ru docs that live in
  the separate working repo (`kosha_ai_translation.md`, `improvements.md`,
  `yandex_api.md`, the two glossary JSONs, the QA scripts): what each is and
  where it is cited.

### Fixed
- mw_ru docs: demoted four dead links pointing at external working-repo files
  to plain text (`improvements.md` and `docs/yandex_api.md` in `qa_judge_v4.md`;
  two glossary JSONs in `mw_ru.md`), so all relative links in
  `RussianTranslation/` now resolve. Added `qa_judge_v4.md` to the prompts
  `README.md` index, marked as a proposed v4 update to the stage-2 judge.

## [1.0.0] - 2026-06-13

### Added
- Added this changelog so repository-level changes have a stable home.
- Recorded the current repository purpose: Research and data workspace for Sanskrit digital lexicography, with a focus on Cologne Digital Sanskrit Lexicon headword lists, cross-dictionary comparison, and teaching materials for Sanskrit lexical and syntactic study.

### Recent Git History
- 2026-06-12 Add 12-month research roadmap: csl-atlas DH review, paper pipeline P1-P6, book plan
- 2026-05-29 ai-wip: add .pre-commit-config.yaml (yaml-only)
- 2026-05-29 ai-wip: add .github/dependabot.yml for GitHub Actions auto-updates
- 2026-05-29 ai-wip: add CODE_OF_CONDUCT.md (Contributor Covenant 2.1)
- 2026-05-29 ai-wip: add CI workflow (generic-text)
