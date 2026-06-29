# PWG→Russian Pipeline — Ultracode Retrospective (2026-06-29)

Prepared for Mārcis Gasūns. Source: a 7-dimension parallel audit (speed, tokens,
python, QA gates, printable-DH, orchestration, scholarly quality) over the repo
docs + ~115 pilot/core scripts, synthesised into one decision-ready report.
All file paths are under [`SanskritLexicography/RussianTranslation/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation).

Method: 8 Opus agents, ~1.05M tokens, 238 grounded tool calls. Keystone claim
(translations stranded from the exporter) independently verified after synthesis.

---

## 1. Executive summary

The pipeline **works and produces good Russian** — Slice C (1,110 cards, 75.9%
clean) and Slice D (879 cards, 70.5% clean) translated DE→RU with structured
per-sense fields (equivalence_type 100%, source_type 100%), low German residue
(4 leaks in 5,036 spans), and correct handling of the Latin-euphemism convention.
But the headline clean rates are **artificially depressed**: of Slice D's 259
requeues, **117 are pure rate-limit nulls** from launching 18 separate harnesses
concurrently — each independently fanning out to the per-run cap of ~8–14 agents,
a true peak of ~140–250 concurrent Sonnet agents against one Max session, not the
"18×" the operator reasoned about.

The four biggest levers, one per ask:

- **(speed)** Run roots through ONE throttled driver at the proven 2–3-wide
  concurrency instead of 18 parallel chats — this alone would have prevented all
  117 nulls.
- **(tokens)** Strip `citations_resolved`/`citations`/`strata` from the inlined
  portrait copy (~35% of the portrait, the larger half of inlined card content,
  the exact lever `AB_TEST_LEAN_TR.md` named and left untested).
- **(python)** Separate transient nulls from real defects in `audit_window.py`
  so the true quality rate (~85%) is visible and cheap re-runs route away from
  expensive rework.
- **(printable-DH)** Build the missing `promote_final_cards.py` convergence step.
  Today the entire translated output is **stranded**: `export_interop.py` builds
  the citable TEI/OntoLex edition from the RAW merged-input layer
  (`assembled_cards.jsonl`), never reading the `wf_output.sd/sc.*.json`
  translations. **Verified**: no exporter or edition-cut script references
  `wf_output`.

**Do first:** the single throttled-driver + concurrency cap — minor effort, no
credential, removes the dominant failure mode of the entire session.

---

## 2. What was done (verified)

- **Translation (Slice C+D).** 44 roots, ~1,989 cards via a batched+masked
  3-layer Sonnet harness (`gen_opt_harness2.py`). Per-sense schema validated by
  `validate_final_card_schema.py`. Differentia, where present, is Apresjan-grade.
- **Cost.** The one lever is agent count = batch size; ~30k/agent is a fixed
  framework constant. gam $16.14→$4.45 (−72%); per-card ~$0.027–0.051. A
  file-tool-read bug was found and fixed (yuj $4.96→$3.52). Lean-TR trimming was
  tested twice and correctly **rejected**.
- **QA gates.** Five free Python gates per window; provenance/stale-refusal
  works; `window_selftest.py` passes 13 tests; BOM hygiene correct. siD
  sense_dupes genuinely FAILs (correct detection). F-gate-nws-fp fixed.
- **FAIR/DH scaffold.** A complete editorial spec (`PRINT_ENTRY_SPEC.md`), a
  closed final-card schema, interop exporters (TEI Lex-0 / OntoLex / reverse
  index), immutable edition-cut + SHA256 manifest, and honestly-reported G1–G10
  gates (G5/G6/G7/G10 blocked at zero) all exist.
- **Scholarly fidelity.** Latin euphemisms preserved verbatim; the one safety
  failure (untranslated German euphemism in `sd.car`) was caught and requeued,
  not shipped. But the only LLM-judged evidence is the 38-card freq test; all
  ~1,989 bulk cards have `judge=null`.

---

## 3. Prioritized recommendations (impact ÷ effort)

"Owner" = AGENT (do now) or MG (needs decision first).

| # | Recommendation | Dimension | Effort | Expected gain | Owner / Blocks-on |
|---|---|---|---|---|---|
| 1 | **Single throttled driver: run roots sequentially or 2–3-wide** (proven Slice C width), not 18 parallel chats. | Speed / Orch | minor | Eliminates the ~80+ 429s and all 117 nulls; net cards/hour RISES | AGENT; **MG** picks standing cap |
| 2 | **Add `--out` flag to `gen_opt_harness2.py`** so each chat generates to its own file. | Orch | minor | Kills the wrong-root harness-launch hazard | AGENT |
| 3 | **Separate transient nulls from defects in `audit_window.py`** (`requeue.transient` vs `requeue.defect`); stop triple-counting nulls. | QA / Speed | medium | Restores true quality metric (~85% not 70.5%) | AGENT |
| 4 | **Portrait-slimming**: strip `citations_resolved`/`citations`/`strata`/`examples_sa` from the inlined portrait copy. | Token | minor | Lossless ~30–35% cut on the larger half of inlined content | AGENT; **MG** confirms translator never needs citation blurb |
| 5 | **Fix `requeue_from_audit.py:65`** to call `gen_opt_harness2.py` not legacy `gen_opt_harness.py`, OR delete it. | Python | minor | Stops the committed wrong-path | AGENT |
| 6 | **Repair `save_and_audit.py`**: raw-string docstring (kills `\.` warning), drop dead imports, fix lying "then audits it" docstring. | Python | minor | No warning; name no longer implies an audit that never runs | AGENT |
| 7 | **Bounded exponential backoff + jitter** in the retry loop; raise attempt cap for 429s only. | Speed | medium | Converts transient 429s into brief waits, not permanent nulls | AGENT; check agent() exposes catchable 429 |
| 8 | **Fix `foreign_gloss_translated` FPs** (90% FP): tighten `LATIN_BINOMIAL`, allow-list real euphemisms, add fixtures. | QA / Quality | minor | Removes ~74 FP requeues of correct cards | AGENT |
| 9 | **Backfill `stratum` deterministically** from each sense's citation (1,303 cited-but-blank), via the siglum→Renou crosswalk. No LLM spend. | Quality / DH | medium | stratum 19.5% → ~60–70% on cited senses | AGENT; **MG** confirms crosswalk authoritative |
| 10 | **Reorder `audit_state()`**: when requeue−nulls is empty, classify `transient_only` not `needs_requeue`. | QA / Orch | minor | Per-root triage at a glance | AGENT (after #3) |
| 11 | **Bump default `--budget` to ~15–18k** (fewer agents = lower peak concurrency + −23% cost). After #1/#7. | Token / Speed | minor | ~15–20% fewer framework payments | AGENT |
| 12 | **Update `AGENTS.md`** lines 39/50/171 to make opt2 canonical. | Python | minor | Runbook stops steering to the deprecated generator | AGENT |
| 13 | **Point `window_selftest.py:130` at the live opt2 harness.** | Python | medium | Tools-guard invariant covers the path Slice C/D runs | AGENT |
| 14 | **Fix legacy-harness path bug** in `root_window_status.py`, `requeue_from_audit.py`, `window_provenance.py` → opt2 (one shared constant). | Orch / Python | minor | Restores the "harness already current" resume optimization | AGENT |
| 15 | **Make `batch_of` exemption reproducible**: committed `rootmap_overrides.json` merged by `audit_sense_dupes.py`; stop relying on the gitignored hand-patched rootmap. | Python / QA | medium | Sense-dupe verdict reproducible from a clean clone | AGENT; **MG** picks track-rootmaps vs overrides-file |
| 16 | **Per-sense Renou register/diasystem label** stamped deterministically from per-headword register tags. | Quality / DH | medium | Populates the diasystem slot; no translation cost | AGENT; **MG** picks vocabulary |
| 17 | **Per-sense differentia gate** (3+-synonym string + empty differentia) → differentia-only enrichment pass (~270 senses). | Quality / QA | minor | Closes the 44%-undiscriminated-multi-synonym gap | AGENT |
| 18 | **Tighten `untranslated_german_residue`** to strip bare retained `<ab>` markers before the residue scan. | QA | medium | Restores "high-confidence = defective" meaning | AGENT |
| 19 | **Quarantine the 7 corpus-probe scripts** (`audit2–7.py`, `audit_fidelity.py`) into `src/pilot/archive/`. | Python | minor | Removes naming collision with the 4 real gates | AGENT; **MG** confirms one-off |
| 20 | **Retire prototype generators** `gen_batched_harness.py`, `gen_tlonly_harness.py`; extract shared scaffold into `window_common.py`. | Python | medium | One live generator, one shared core | AGENT; **MG** confirms A/B closed |
| 21 | **`run_state.jsonl` orchestrator** (`queue_run.py`): single committed per-root ledger replacing the 3 drifting scratchpad maps. | Orch | medium | Single source of truth; survives crash/handoff | AGENT; **MG** picks committed vs gitignored + launch-loop scope |
| 22 | **`promote_final_cards.py` convergence step** — THE keystone: ingest `wf_output.*.json`, validate, stamp provenance, write canonical translated store; repoint `export_interop.py` at it. | DH | heavy | The translations finally reach TEI/edition; unblocks G5 + provenance | AGENT; **MG** decides supersede-vs-union the old 217-row store |
| 23 | **Fix `CITATION.cff`**: license CC-BY-SA-4.0 (match DATA_LICENSE), author Mārcis Gasūns + ORCID, real repo URL + PID namespace. | DH | minor | Removes disqualifying FAIR/DOI metadata defects | AGENT; **MG** confirms byline/PID base |
| 24 | **Fix siD structural class at generation** (tag the 4 pwg00-03 head parts, or a declared part_overlap_group). | QA / Python | heavy | Converts a permanently-failing, un-requeue-fixable defect into a clean pass or a true content fail | **MG** scholarly call |
| 25 | **Opus judge over a stratified sample + complete G6 320-row gold**; publish precision + 95% Wilson CI. | Quality / DH | heavy | First real fidelity number on the actual output | **MG** supplies/delegates reviewers |
| 26 | **First renderer**: deterministic TEI-Lex0 → paged PDF over G5-approved cards only. | DH | heavy | The actual print-ready PDF | **MG** picks tech; after #22 + G5 > 0 |

---

## 4. Speed & token plan (concrete sequence)

The collapse was a **cross-run over-subscription artifact**, not a per-root limit
— single-root sTA ran 106 cards / 19 min / **0** transient failures
(`PILOT_COST.md:148-149`). Order:

1. **Stop launching N parallel chats (rec 1, do first).** One driver, sequential
   or 2–3-wide. Slice C succeeded at 2; Slice D collapsed at 18. A clean
   sequential sweep is **faster end-to-end** than a collapsed 18-way run + its
   recovery pass.
2. **`--out` flag (rec 2)** so the driver scopes each harness correctly.
3. **Split transient vs defect nulls (rec 3)** — exposes the true ~85% rate;
   `--transient-only` re-runs are cheap.
4. **Backoff + jitter (rec 7)** for residual 429s — waits, not permanent nulls.
   Conditional on `agent()` exposing a catchable rate-limit error.
5. **Portrait-slim (rec 4)** — the largest un-attacked cost slice. Verify on a
   **cold sequential** A/B (never parallel same-prompt).
6. **Bump `--budget` (rec 11)** — LAST; bigger batches at high concurrency would
   worsen 429s.
7. **One instrumented run-to-cap window** to fix the open Max weekly-quota divisor
   and record the empirical concurrency at which throttling first fires.

Net: cards/hour rises, $/root drops ~30% portrait + ~20% budget on top of ~$3/root,
and the binding constraint becomes the Max weekly quota — **more roots per Max week**.

---

## 5. Python consolidation plan (highest-severity first)

**Tier 1 — committed traps that silently corrupt behaviour:**

- **`save_and_audit.py` (rec 6):** `\.` SyntaxWarning, dead `os`/`subprocess`
  imports, docstring claims "then audits it" when `main` only saves. An operator
  may believe the gates ran.
- **`requeue_from_audit.py:65` (rec 5):** invokes the obsolete per-card
  `gen_opt_harness.py` — a different (non-masked, −89%-path-lost) regime.
- **gitignored rootmap `batch_of` patch (rec 15):** a green QA gate depends on an
  untracked hand-edit `_pilot_gen_merged.py` never emits — a fresh clone or regen
  silently flips jan's sense_dupes to FAIL.

**Tier 2 — false coverage & stale docs:** `window_selftest.py:130` tests the
legacy harness, never opt2 (rec 13); the legacy-path resume optimization is dead
code in 3 files (rec 14); `AGENTS.md` still prescribes the obsolete generator (rec 12).

**Tier 3 — clutter:** 7 corpus-probe `audit2–7.py` scripts collide with the 4 real
gates (rec 19); 4 generators with ~80% shared scaffold, only one live (rec 20).

---

## 6. Road to a printable, FAIR, TEI-grade edition (ordered gaps)

The spec, schema, exporters, edition-cut machinery, and honest gate tracking
**all exist**. The blockers are convergence, provenance, IDs, and review.

**Agent-doable now (confirm scope only):**

1. **Build `promote_final_cards.py` (rec 22) — THE keystone.** Today
   `export_interop.py:21` reads `assembled_cards.jsonl`, never the translations.
   **The entire PWG→Russian deliverable has zero path into the DOI-registered
   artifact.** Everything downstream blocks on this.
2. **Stamp per-card provenance** (model_id, prompt_sha, pwg_src_commit, corpus
   build id) — today run-level `meta` has only rootmap_sha256 + input_hashes and
   NO model_id.
3. **Normalize `record.h`** (free-text "dā (homonym 11…)") into
   `{h:int, sublemma, upasarga_chain}`; key cards on `(key1, h)`. `safe_id(key1)`
   currently collides homographs into one TEI ID.
4. **Backfill `stratum` (rec 9)** and **stamp Renou register (rec 16)** — the
   "era-correct Russian" headline feature, no LLM spend.
5. **Fix `CITATION.cff` (rec 23)** — license/author/PID defects disqualify a FAIR
   DOI deposit.
6. **Add per-sense corpus citation loci** from `corpus_lexicon.jsonl`
   (`corpus_provenance.py` already exists).

**Needs MG decision then agent-doable:** typed apparatus/Nachträge schema field
(7); G5 review on the NEW Slice C/D cards (8); first TEI→PDF renderer (9).

---

## 7. Open decisions for MG (deduped, grouped)

**A. Scope & priority** — (1) standing concurrency cap (3? 4? discretion?);
(2) canonical store: supersede vs union the old 217-row run_batch store;
(3) first citable `edition_v1` slice (flagship trio vs freq-core tranche);
(4) minimal Orch trio now vs full refactor; (5) `run_state.jsonl` committed vs gitignored.

**B. Scholarly judgment** — (6) siD 4-part overlap: faithful (whitelist) vs
over-production (hard-fail + re-translate); (7) stratum auto-fill authoritative?;
(8) diasystem vocabulary (Renou codes / Apresjan stylistic / both);
(9) demote the FP-heavy gates to hints?; (10) print-ready precision bar (>84.4%?);
(11) should the translator ever see `citations_resolved`?

**C. Rights & publication** — (12) CITATION.cff authorship + co-listing;
(13) persistent-ID namespace (GH-Pages / w3id PURL / Zenodo); (14) renderer tech
(LaTeX vs HTML+PagedJS).

**D. Resourcing & surface constraints** — (15) G5/G6/G7 review workforce
(0/320 gold is the only blocker to a real fidelity number); (16) agent() surface
facts (per-run vs account concurrency cap; catchable 429 + in-harness await;
programmatic launch?); (17) willing to spend one deliberate run-to-cap window to
measure the Max divisor + throttle-onset concurrency?
