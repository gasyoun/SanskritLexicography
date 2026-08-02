# PWG translation — duplication map & unjustified-code optimization inventory

_Created: 02-08-2026 · Last updated: 02-08-2026 (H2229 OPT-8 kitchen banner; H2226 OPT-4 closed)_

**Purpose.** One place to hunt **optimization**: where the PWG→RU/EN pipeline
_duplicates logic or code without a good reason_. Companion to the product-
content story (edition restates, style doublets) so a future session does not
confuse **lexicographic overlap** with **engineering waste**.

**Prior art (do not rebuild):**

| Doc | Owns |
|-----|------|
| [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) | SHARED / INTENTIONAL-DIVERGENCE / **GAP** ledger for every RU↔EN fix |
| [ARCHITECTURE_AUDIT_2026-07-02.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ARCHITECTURE_AUDIT_2026-07-02.md) §7 | Inline selfheal vs `autosplit_requeue` — consolidation **deferred on purpose** |
| [DICTIONARY_CHAIN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DICTIONARY_CHAIN.md) | PWG↔PW↔SCH↔NWS layer semantics |
| [STYLE_RESEARCH_DOUBLETS_VL_COMP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/STYLE_RESEARCH_DOUBLETS_VL_COMP.md) | Gloss doublets (1 DE → ≥2 RU) — **style policy**, not code |
| [REUSE_MAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md) | Sa→Ru authority assets for `corpus_gate` |
| Uprava FINDINGS §31 | TM re-serves audit-failed content unless requeue `--no-tm` |

**How to use this file.** Walk §2 (intentional — leave alone) then §3–§5
(ranked optimization targets). Each **OPT-** row is a candidate refactor or
parity port. Prefer closing a **LANG_PARITY GAP** over inventing a third twin.

**Model provenance:** Grok 4.5 (`grok-4.5`), inventory session 02-08-2026
([H2222](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2222-Grok_SanskritLexicography_pwg-dup-optimization-inventory_02.08.26.md)).

---

## 1. Taxonomy — four kinds of “duplication”

| Kind | Question | Optimization? |
|------|----------|---------------|
| **A. Lexicographic / edition** | Same lemma restated across PWG/PW/SCH/NWS | **No** — product is layered completeness; tag via `provenance.relationship` |
| **B. Target-language product** | Same German sense → RU **and** EN | **No** for two store fields; **Yes** if gate/promote logic is copy-pasted instead of `--lang` / `CARD_FIELD` |
| **C. Pipeline process** | Same input translated twice (TM hit, double-run root, dual session) | **Yes** for cost/ops; mostly guardrails, not merge of modules |
| **D. Code / control-flow twin** | Two files implement the same plan/merge/fidelity rule with drift risk | **Yes** — primary optimization surface of this inventory |

Rule of thumb: if [LANG_PARITY](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) already marks it **SHARED**, the code path is already parameterized — do not “dedupe” by forking. If **GAP**, the missing twin **is** the waste (fix once, port once). If **INTENTIONAL-DIVERGENCE**, document why and stop.

---

## 2. Intentional duplication (do **not** optimize away)

### 2.1 Edition-chain content (~5k restates)

Non-`pwg` sub-cards classified by
[`build_relationships.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_relationships.py)
(roll-up `pwg_ru/relationships_rollup.tsv`): order of magnitude **~5 054 `restate`**
(PW abridging PWG), plus smaller `nws_at_sense` / `a2a` / `sch_star` / etc.
This is historical dictionary design, not a bug. Optimization would be **display**
(collapse restates in UI) or **spend** (skip re-translating pure restates when
RU already exists from PWG) — never delete the layer from the store.

**Spend-side idea (product, not code-dupe):** when `relationship.subtype == restate`
and a same-homonym PWG RU already exists, prefer TM/suggest-only or human
“accept abridge” over a full Sonnet window. Track as a separate handoff if pursued.

### 2.2 Gloss style doublets (~18.5% of one-word DE pairs)

Measured in
[STYLE_RESEARCH_DOUBLETS_VL_COMP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/STYLE_RESEARCH_DOUBLETS_VL_COMP.md):
one German gloss word → two+ Russian equivalents. Awaiting style vote (H1306
sheet). **Not** a `SENSE-DUPE` failure.

### 2.3 Free gates that _detect_ sense-id duplication

[`audit_sense_dupes.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_sense_dupes.py)
+ hard `DUP` on EN: catch cross-part over-production of the same sense number.
Keep — this is anti-duplication logic, not waste.

### 2.4 Stage-0 mask / kill / TM address (already SHARED)

Masking, wall-clock kill, frag-count selfheal trigger, `sha256(lang+input)` TM
address, target-field fidelity — live in lang-agnostic code. See SHARED rows in
LANG_PARITY. **Do not split RU/EN copies “for clarity.”**

### 2.5 `resolveGroup` / `healGroup` near-clones

[ARCHITECTURE_AUDIT §7](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ARCHITECTURE_AUDIT_2026-07-02.md):
unifying them parametrically was **prototyped and rejected** — shared abstraction
harder to read than the duplication. Leave unless a third consumer appears.

---

## 3. Unjustified or high-cost engineering duplication (optimize here)

Ranked by **leverage × risk** for a refactor session. Line counts measured
02-08-2026 on `origin/master` (~4118e6a6).

### OPT-1 — EN promote lacks RU merge discipline (LANG_PARITY **SHARED** — closed H2224)

| | |
|--|--|
| **Files** | [`promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) (~2080 lines) vs [`promote_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_en.py) (attach-overlay + B08/B20/H1553 twins) |
| **Waste** | ~~EN attach overwrote `en` without better-attempt-wins / model-id / defect refuse.~~ **Closed H2224** (Grok 4.5 `grok-4.5`, 02-08-2026): better-attempt-wins on `en`/`en_provenance`, `model_tier` + execution.model_identifier refuse, defect-key refuse + `--ready-partial-report`. Ledger: `h1339_en_promote_parity_gap` + `h1553_wall_clock_defect_ready_partial` → SHARED. |
| **Optimize** | ~~Port merge ranking + refuse-defect + model-id.~~ Done without folding the full RU bridge into EN (helpers single-sourced from `promote_final_cards`). |
| **Prove** | LANG_PARITY SHARED; `promote_en --selftest` (B08/B20/H1553 pins); fixture dry-run defect refuse. |
| **Risk** | First real `promote_en` production run remains the consumer — guards now present. |

### OPT-2 — RU audit orchestrator vs EN all-in-one auditor (structural twin)

| | |
|--|--|
| **Files** | [`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) (~844 lines, **orchestrates** child auditors) vs [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py) (~527 lines, **reimplements** gates in one file) |
| **Waste** | LANG_PARITY header states the original problem: EN reimplements gates from scratch → C1–C9 class of EN-only holes. Shared pieces already extracted (`foreign_literal_guards.py`, `stage2_pregate`, `window_reports.build_production_metrics`, `CARD_FIELD`). Residual: LS/SAN/AB/DUP/MISSING-* loops still forked. |
| **Optimize** | Extract **lang-agnostic sense markup gates** (`ls_loss`, `san_loss`, `ab_loss`, identical-target `DUP`) into one module parameterized by target field name (`russian`/`english`); leave language-specific soft flags (NO-RUSSIAN / DE-RESIDUE / MW-DIVERGE) in thin wrappers. |
| **Prove** | `window_selftest` green; LANG_PARITY hash re-stamp; byte-stable reports on a frozen `wf_output` fixture. |
| **Risk** | High if done as a big-bang rewrite; low if one gate family per PR. |

### OPT-3 — Inline selfheal vs standalone autosplit (deferred consolidation)

| | |
|--|--|
| **Files** | [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) inline selfheal **and** [`autosplit_requeue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/autosplit_requeue.py) |
| **Waste** | Same fragment-planning + partial-credit philosophy twice; divergent markers (`missing_fragments` / `missing_groups` vs `missing_senses`); opposite grouping (heal-group vs `--budget=1`). Failure **semantics** aligned 02-07-2026; implementations not merged. |
| **Optimize** | Single `plan()` consumer API: both call one stitch/partial module. Only worth it if a **third** consumer appears (ARCHITECTURE_AUDIT §7 explicit revisit criterion) **or** a measured bug from marker drift reappears. |
| **Prove** | golden fragment fixtures: same input → identical stitched card + missing-ids from both entry points. |
| **Risk** | High (translation control flow). Default: **defer**. |

### OPT-4 — H1209 / H1210 Workflow templates hardcode RU (LANG_PARITY **SHARED** — closed H2226)

| | |
|--|--|
| **Files** | `src/pilot/h1209/wf_template.js`, `h1210/wf_template_ab.js`, `h1210/control_template.js` (+ already field-parameterized Python: `canonical_audit.py`, `det_gate.py`, …) |
| **Waste** | ~~JS hardcodes `russian` target + RU controller prompt.~~ **Closed H2226** (Grok 4.5 `grok-4.5`, 02-08-2026): `TARGET_FIELD` + `CONTROLLER_PROMPT` from payload (`prep_slice` / `arm_b_control`); EN inject build without a second scaffold tree. |
| **Optimize** | ~~Parameterize the two prompts / target field in JS once.~~ Done; live paid EN campaign remains optional follow-up. |
| **Prove** | `js_field_param_selftest` RU/EN inject; `det_gate selftest` EN field path; RU 3-card canary fixture + `canonical_audit` green. LANG_PARITY `h1209_controller_worker_rig` + `h1210_ab_arm_scaffold` → SHARED. |
| **Risk** | Residual: first live EN Workflow run still the consumer. |

### OPT-5 — Judge / gold-sample twins (small, low urgency)

| Twin | Lines (approx.) | Note |
|------|-----------------|------|
| `gen_fidelity_judge.py` / `gen_fidelity_judge_en.py` | ~107 / ~128 | Rubrics differ by language — INTENTIONAL for homograph rules (H1070 EN). Share only packaging (CLI, JSON emit). |
| `gold_sample.py` / `gold_sample_en.py` | ~70 / ~150 | Stratification logic likely shareable; EN-specific MW-hidden rules stay. |

**Optimize** only if a third language lane appears or a shared CLI bug is fixed twice.

### OPT-6 — Citation index coverage double-count (CODE_REVIEW debt) — ✅ DONE H2225

[`CODE_REVIEW_2026-07-04.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CODE_REVIEW_2026-07-04.md):
`build_citation_index.py` vs `occurrence_stats()` disagreed on coverage semantics →
`CITATION_SOURCES.md` / `UNCOVERED_SOURCES.md` could diverge.

| | |
|--|--|
| **Optimize** | One pure function `coverage_key(ls)` used by both. |
| **Risk** | Low. |
| **Prove** | Fixed fixture set: both emitters print identical coverage rows. |
| **Shipped** | 02-08-2026 · Grok 4.5 (`grok-4.5`) · H2225 — `coverage_key` + `coverage_bucket` + `coverage_rows_from_pairs` in [`build_citation_index.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_citation_index.py); `build()` and `occurrence_stats()` both call the kernel; `python src/build_citation_index.py --selftest` green. **Totals shift:** CITATION_SOURCES `unresolved` no longer includes non-coordinate labels (same rule UNCOVERED already used). |

### OPT-7 — TM serve of failed content (process, not file twin)

Uprava FINDINGS **§31**: requeue harness with TM on re-serves the **exact**
audit-failed card (`agent_expected_after_tm: 0` real work).

| | |
|--|--|
| **Optimize** | Already mitigated by `--no-tm` on defect requeue. Residual hardening: TM invalidation keyed on **last audit outcome** (or fragment denylist always applied before TM hit), so a default requeue cannot silently no-op. |
| **Risk** | Medium (false-invalidates good TM if audit is wrong). |
| **Prove** | gam-class fixture: requeue without flags still refuses failed hash. |

### OPT-8 — Multi-execution of the same root (ops)

Concurrent sessions / Max accounts double-run a root; dual handoff mint of the
same work (historical H963/H994 shape).

| | |
|--|--|
| **Optimize** | Already: store-hit preflight, coordinator occupied-keys, worktree claim, `--max-wide=1` bounded run. Residual: surface **store-hit / lease collision** louder in progress kitchen / ledger so a human does not start a second paid window. |
| **Risk** | Low (observability only). |
| **Status (H2229)** | **Shipped observability:** collision aborts emit `dashboard_events` (`lease_collision` / `store_hit` / `occupied_keys_unreadable`); kitchen `collision_guard` + red banner + operator one-liner. Selftest `progress_dashboard/kitchen_collision_selftest.py`. Not a new concurrency protocol. |

---

## 4. Content-side optimization (not code twins, still “duplication cost”)

These burn **tokens/time** because the same German meaning is paid twice, even
when code is clean.

| ID | Pattern | Candidate save |
|----|---------|----------------|
| **C-1** | PW **restate** of already-promoted PWG sense | Suggest-only / short-path translate; or skip if abridge-only and RU PWG exists |
| **C-2** | Style doublets force longer RU output | After H1306 policy: one primary + optional `differentia`, fewer tokens |
| **C-3** | `mw_ru` terminology seed + full PWG DE→RU | Keep as orient only (current doctrine); do not harvest-seed bulk |
| **C-4** | Corpus_gate multi-dict lookup (koch/kna/fri/smirnov/kow) per card | Already free Python; only optimize if profile shows hot loop |
| **C-5** | EN + RU full generation of same window | EN is second product; share **mask/skeleton/presplit** (already SHARED), never share translated text |

---

## 5. Hunt method (repeatable)

When looking for new OPT rows:

1. **List twins by filename:** `*_en.py`, `*_en.js`, `tr_en.txt` vs `1_perevod.txt`,
   `audit_window*` pair, `promote*` pair, `gen_fidelity_judge*` pair.
2. **Diff structure, not bytes:** shared helpers already in
   `card_fields.py`, `foreign_literal_guards.py`, `stage2_pregate.py`,
   `store_path.py`, `window_reports.py` — prefer extending those over a new twin.
3. **Check LANG_PARITY first:** GAP → port; SHARED → stop; INTENTIONAL → document.
4. **Check ARCHITECTURE_AUDIT §7** before touching selfheal/autosplit.
5. **Measure:** if the “dupe” is only in **edition restates** or **style doublets**,
   it belongs in §2 / §4, not a refactor PR.
6. **One family per PR** — markup gate extract, promote parity, JS field param —
   never “dedupe the pipeline” as a single change.

Quick local probes (read-only):

```text
# twin surface
rg -n "audit_window_en|promote_en|gen_fidelity_judge_en|CARD_FIELD|TARGET_FIELD" RussianTranslation/src

# open GAPs
rg -n '"verdict": "GAP"' RussianTranslation/LANG_PARITY.md

# relationship restates (content, not code)
# see pwg_ru/relationships_rollup.tsv
```

---

## 6. Recommended drain order (for a human or a follow-on handoff)

| Priority | Item | Why first |
|----------|------|-----------|
| **P0** | ~~OPT-1 EN promote parity~~ **done H2224** | Guards landed; first real EN promote still the consumer |
| **P1** | ~~OPT-6 citation coverage single source~~ **done H2225** | Pure function shipped |
| **P1** | ~~OPT-4 H1209/H1210 JS field parameterize~~ **done H2226** | Scaffold field-param; first live EN Workflow still the consumer |
| **P2** | OPT-2 extract lang-agnostic markup gates | High leverage, needs staged PRs |
| **P3** | OPT-7 TM invalidation on defect | Cost insurance on requeues |
| **P3** | C-1 restate short-path | Product spend; needs policy + measurement |
| **Defer** | OPT-3 selfheal↔autosplit merge | Explicitly deferred until third consumer or drift bug |
| **Defer** | OPT-5 judge/gold twins | Low line-count, intentional rubric split |

---

## 7. What this inventory is **not**

- Not a plan to collapse PWG and PW into one store layer.
- Not a ban on RU and EN products.
- Not a rewrite of headless_worker / coordinator.
- Not a substitute for LANG_PARITY’s mechanical hash gate — any code change that
  touches listed `files:` must re-stamp via
  `python src/pilot/lang_parity_check.py --update-hash <id>`.

---

## 8. Changelog of this inventory

| Date | Change |
|------|--------|
| 02-08-2026 | First cut: taxonomy A–D, intentional §2, OPT-1–8, content C-1–5, drain order. Grok 4.5 (`grok-4.5`). H2222. |

_Dr. Mārcis Gasūns_
