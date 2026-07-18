# RussianTranslation deep manual — the mw_ru and pwg_ru pipelines

_Created: 11-07-2026 · Last updated: 11-07-2026_

The subsystem deep manual for
[RussianTranslation/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation)
— first item of the deep-manual queue in
[PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md)
(handoff H606, authored by Fable 5 `claude-fable-5`). Audience: **maintainer /
operator** — a fresh session that has to run a production translation window,
audit it, promote it, and close it out without rediscovering a fixed bug.
The orientation-layer sibling is
[MAINTAINER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md);
this document goes one level deeper into a single subsystem. Every count in
this manual is stamped with its as-of date; the live truth is always
[RussianTranslation/.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
and the command output of the scripts themselves.

## 1. What this subsystem is

Two LLM dictionary-translation pipelines sharing one engine design:

| Pipeline | Source → target | Status | Scale |
|---|---|---|---|
| `mw_ru` | Monier-Williams (English) → Russian | **finished** (May 2026); covered here as a post-mortem, §3 | 287,358 cards |
| `pwg_ru` | PWG / Böhtlingk-Roth (German) → Russian (primary) + English (secondary) | **production, environment-gated** (since 13-07 every live generation lane is NO-GO by environment — H1110 c4 probe 98.6 s vs the 30 s ceiling; the H1209 controller-worker Workflow lane measured GO 18-07) | 106,082-headword universe; store **11,603** rows as of 18-07-2026 (the 17-07 H1080 hash-locked repair restored 668 placeholder rows + 468 null owners and quarantined two `banD` rows, 11,605→11,603 — the store HAS needed one repair) |

The intellectual problem is not per-headword translation difficulty — a
38-unit judge test settled quality early (37/38 publishable). The whole
discipline of the subsystem is making an LLM run **reliable, cheap, and
mechanically verifiable at 100,000-headword scale** through the Claude
Workflow tool, with no Claude API key. Everything below — masking, batching,
deterministic gates, translation memory, kill gates, incident ledgers — exists
to serve that.

Hard boundary to keep in mind everywhere: **the repo is public, the
translations are not published.** The RU/EN stores, the harvested dictionary
data, and the TM sidecars are all gitignored, local-only assets (§9). Never
commit them, never paste bulk store content into public artifacts.

## 2. Document map — which file owns what

The subsystem carries ~106 top-level Markdown docs (~244 across the whole
tree); these are the load-bearing ones. Read
in this order on first contact.

| You need… | Read |
|---|---|
| The narrative "how did we get here" (phases 0–15, recurring failure shapes) | [PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) |
| The exact production loop, verbatim commands, worked example | [src/pilot/RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) |
| Intent → command quick map (18 use cases) | [USE_CASES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/USE_CASES.md) |
| Repo-local agent rules (audit/acceptance, markup policy, encoding) | [AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/AGENTS.md) |
| What is queued / in flight / paused right now | [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md) (subordinate to the repo-root journal) |
| The per-launch incident register + failure typology | [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md) |
| Quantitative launch denominators (458 windows as of 18-07-2026) | [LAUNCH_STATS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md) (auto-generated — never hand-edit) |
| RU/EN fix-parity policy + ledger | [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) |
| Output-complexity taxonomy + kill-gate design | [FAILURE_MODES_AND_KILL_GATE_2026-07-04.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FAILURE_MODES_AND_KILL_GATE_2026-07-04.md) |
| The finished mw_ru run, editor-facing | [mw_ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md) |
| Engine design history (staleness-bannered) | [PIPELINE_ARCHITECTURE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_ARCHITECTURE.md) |
| `<ab>`/`<ls>` tooltip + RU-abbreviation-purity policy | [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md) |
| Judge-model policy (Sonnet bulk, Opus on rejects) | [research/JUDGE_POLICY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/JUDGE_POLICY.md) |
| The five harvested Sa→Ru dictionaries (Russian) | [src/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/README.md) |

Trust order when they disagree: **command output** (`root_window_status.py`,
`window_status.json`) > `.ai_state.md` > the dated docs. Several docs carry
explicit staleness banners — respect them.

## 3. mw_ru — the finished pipeline (post-mortem chapter)

Full account: [mw_ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md).
What a maintainer needs to retain:

**Numbers.** 287,358 MW cards translated in ~11 days (14–25 May 2026),
append-only chunked runs, latest-version-per-card wins at assembly. Final
translator shares: Sonnet 4.6 67.4% (main pass), Opus 4.7 28.1% (re-translation
of rejects), Yandex ~2.8% (short-card fill + light fixes), mechanical regex
~1.1%. Two independent QA judges issued verdicts only (no text): Opus 4.7
~227,000 verdicts, YandexGPT 5.1 ~222,000 (~77% of the dictionary). Gemini 2.5
Pro was tried as a judge and **rejected** (90% BAD-rate vs Opus's 62% — false
positives). Severity ≥ 3 routed a card to re-translation; ~111k cards were
rewritten.

**Stages and prompts.** translate → two independent QA judges → mechanical
regex fixes (~20k cards, no LLM) → re-translate rejects in rounds → Yandex
fill. One prompt file per LLM stage in
[mw_ru_prompts/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/mw_ru_prompts):
[1_perevod.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru_prompts/1_perevod.txt)
(translation, with a 91-pair glossary),
[2_qa_sudya_opus.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru_prompts/2_qa_sudya_opus.txt) /
[2_qa_sudya_yandexgpt.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru_prompts/2_qa_sudya_yandexgpt.txt)
(the two judges, one rubric),
[3_pereperevod_opus.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru_prompts/3_pereperevod_opus.txt)
(re-translation, 145-pair glossary), and
[qa_judge_v4.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru_prompts/qa_judge_v4.md)
(a **proposed, never-applied** v4 judge design, ready for a future run).

**The format invariant (do not "fix" this).** Cards were masked to `{Tn}`
placeholders; the model translated only open English prose. Sanskrit (`<s>`),
grammar abbreviations, and source references (`<ls>`) are deliberately
untouched, and `<ab>` abbreviations are deliberately NOT expanded (the site
renders tooltips). Punctuation is semantic and count-preserving (`;` = sense
boundary, `,` = synonym boundary).

**Where the data is.** NOT in this repo. The finished cards, pipeline code,
and glossaries live in a separate `mw_ru` working repo; this repo holds only
the editor doc + prompt kit. Consequence measured in
[PIPELINE_ARCHITECTURE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_ARCHITECTURE.md)
§6: the planned "mw_ru terminological seed" harvest input for pwg_ru is
**blocked on locating that repo**, and pwg_ru production runs without it.

**What pwg_ru inherited:** the masking/placeholder contract as the load-bearing
invariant; two-independent-judge severity gating (≥3 → rewrite); mechanical
regex for systemic 130+-repeat errors instead of LLM spend; append-only runs
with latest-wins assembly; heuristic pre-filtering before judge spend
(matured into pwg_ru's deterministic-gates-first policy, §7).

## 4. pwg_ru — what actually gets translated

**The source is NOT `pwg.txt` alone.** The translated unit is the **5-layer
all-in-one card** built by
[src/_pilot_gen_merged.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py):
PWG main + Nachträge + PW + SCH + PWKVN + NWS (owner-mapped), live since
17-06-2026 and never reverted. `csl-orig/v02/pwg/pwg.txt` is read-only and is
only the PWG-layer input. Sub-card IDs carry the layer routing: `_zz_pw`,
`_zz_sch`, `_zz_pwkvn`, `_zz_nws00` suffixes. A headword with **no** PWG record
but a PW/SCH/PWKVN/NWS record renders as standalone supplement-chain sub-cards
(`<key>~~h0_zz_<layer>`, the "no-PWG lane") — no fabricated PWG portrait.

**Masking.** [src/pwg_mask.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py)
splits the dictionary into `<L>…<LEND>` records and masks everything
untranslatable to `{Tn}` placeholders — verified 123,365/123,366 records
round-trip losslessly (the 1 known-lossy record is why per-card round-trip
assertion is mandatory before translation). The `{%…%}` German-vs-Latin
classifier keeps German glosses translatable and Latin verbatim.

**Harvest layers** (the "richer than a plain translation" design):
five extracted Sa→Ru dictionaries keyed by SLP1 —
koch 29,177 · kow 13,488 · kna 3,271 · fri 8,151 · smirnov 3,547 entries
(≈57,634 total; regenerated by
[src/build_src.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_src.py),
data gitignored — Kochergina/Frisch/Smirnov are in copyright); the 1,091,528-pair
corpus word-alignment lexicon `src/corpus_lexicon.jsonl` (DeepSeek-built from
the SamudraManthanam verse-aligned corpus, gitignored); joined by
[src/corpus_gate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py)
as a **non-blocking two-signal annotator** (correctness vs independent dicts;
reference agreement vs the human KOW translation, which corroborates but never
decides).

**Models and access paths — the standing constraint.** There is **no Claude
API key**. Claude stages run through the **Claude Workflow tool** in a session
that has it (tool availability is per-session, not per-tier — check the
toolset at session start). Generation targets **Sonnet 5 (`claude-sonnet-5`)**, and since H818
(12-07-2026) the generated harness pins `model: 'claude-sonnet-5'`
**explicitly on every `agent()` call, both RU and EN** — the former
RU-alias-vs-EN-pin divergence is closed as SHARED in LANG_PARITY (the bare
`sonnet` alias once resolved to 4.6 on a real run, which is why the pin is
explicit). The bulk QA judge policy is **Sonnet judges,
Opus 4.8 (`claude-opus-4-8`) adjudicates only rejects** (`ok=false ||
severity>=3`, Opus verdict final) — decided on a 474-card A/B with κ=1.0, see
[research/JUDGE_POLICY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/JUDGE_POLICY.md);
and since the 2026-06-27 token optimization the per-card LLM judge is dropped
from the bulk path entirely — four free Python gates own bulk QA (§7).
DeepSeek (`deepseek-chat`, via OpenRouter, a real API key) owns high-volume
Python-API work: the corpus-lexicon build and running-text TM mining.
YandexGPT is a designed second judge, not in production.

**The store.** `src/pwg_ru_translated.jsonl` (RU spine; a parallel EN store) —
local-only, gitignored, one row per sense, with full provenance per row
(model alias + exact `model_version`, root/rootmap/input hashes, generation
time, `wf_file`, `source_profile`, `layer`). 11,317 rows as of 10-07-2026.
Promotions must pass `--gen-model-version <exact-model-id>`.

**Translation policy invariants** (from
[AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/AGENTS.md)):
preserve PWG printed sense order; preserve `{#...#}`, `<ls>…</ls>`, sigla, and
German abbreviations like `Bed.`/`Schol.` verbatim; render **every** Nachträge
patch (dropping one is a coverage failure); `<is>…</is>` is siglum text, not a
gloss wrapper; NWS owner attribution exact, one row per source; Renou labels
are badges, never a reason to reorder senses. Presentation-layer decisions
(tooltips, RU-column abbreviation purity, `<is>` Cyrillicization) happen at
**render time** in
[src/pilot/build_article_site.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py),
never in the store — see
[ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md)
(grammatical-category abbreviations stay international Latin with a tooltip;
editorial/cross-reference ones translate to Russian — both ruled 10-07-2026).

## 5. The production window, step by step

The loop is fixed: **probe → preflight → generate harness → Workflow run →
capture → deterministic audit → requeue → promote → TM rebuild → closeout.**
Do not skip or reorder. Verbatim commands + a worked example (`vid`, real
numbers: 102 agents, 6.6M tokens, ~19 min) live in
[RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md);
this section is the annotated checklist with every trap at its step.

**Step 0 — session preconditions.**
The session must HAVE the Workflow tool (check the toolset, don't pick a
"tier"). Check
[.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
WIP + the GTD `🔒 CLAIMED` tags for a concurrent session (H214 tree-intermix
incident). This repo is a shared tree: **isolated worktree + PR, never direct
edits, never `git add -A`.** Run scripts from the `RussianTranslation` repo
root. UTF-8 without BOM everywhere.

**Step 1 — warm-up probe (mandatory since 10-07-2026).**
Fire a load-representative warm-up `agent()` probe (**≥5 KB skeleton-sized
payload** — a trivial probe passed GO while the window still degraded, H442
launch 3) and log the reading with
[src/pilot/probe_log.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/probe_log.py)
(gate: **0 connection errors AND sub-30 s**). NO-GO → do not launch; log the
abort row. Every blind launch into a degraded environment has cost ~2M tokens
for ~0–1 clean cards (reproduced 3×, H437/H442).

**Step 2 — preflight (free, before any token spend).**

```powershell
python src\pilot\verb_worklist.py --top 20
python src\pilot\root_window_status.py <root>
python src\pilot\perf_preflight.py <root> [...more roots]
python src\pilot\prompt_rule_audit.py --fail-on-missing
```

`root_window_status.py` prints one `next action` / `next command` — trust it
over stale prose. `perf_preflight.py` reports TM hits, presplit routing, and
`agent_expected_after_tm` (the estimator was fixed 04-07-2026 after pricing a
102-agent `vid` run at 13 agents — presplit giants now count their fragment
groups). A `defer-calibrate` root gets its own session. An over-ceiling
(kAla-class) monster window is parked in `deferred_monsters.jsonl` by the
`coordinator.py` cost gate and refused — `prepare --allow-over-cost` only in a
dedicated human-budgeted session (MG ruling 07-07-2026).

**Step 3 — generate the harness.**

```powershell
python src\pilot\gen_opt_harness2.py <root>    # → src\pilot\run_pilot_wf.opt2.js
```

[gen_opt_harness2.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
is the canonical generator (batched + masked; measured −72% cost on a full
mixed root, −90% on a clean small batch vs per-card). Defaults:
`--output-budget=90` (calibrated live 07-2026), selfheal + binary-split on,
presplit routing on (citation trigger AND the H155 sense-count trigger),
`--tm=auto`. `--no-tm` is the explicit opt-out — **mandatory on defect
requeues** (enforced in `requeue_from_audit.py` since 04-07-2026). The harness
inlines all inputs, sets `tools: []` on translate agents (any file `Read` in a
run means an obsolete harness), embeds rootmap/input SHA-256 provenance, and
strips post-generation annotation fields from the per-call schema
(`_strip_post_generation_fields()`, H428 — the reachable schema went
10,940 → 1,698 chars after the Workflow safety classifier refused the fat one
at 0 tokens, 67/67 calls). The committed
[run_pilot_wf.js](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_pilot_wf.js)
is a template — never run it directly. The legacy `gen_opt_harness.py` is
archived under
[src/pilot/archive/superseded_2026-07-06/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src/pilot/archive/superseded_2026-07-06).

**Step 4 — run in the Workflow tool and capture the result.**
Drive the Workflow **from the orchestrating Claude Code session** — never a
manual Max-surface save. The H145 `vid` run was lost exactly at the manual
hand-off: the Workflow completed but the save never reached disk and the stale
file silently held the previous root. After writing `wf_output.json`, verify
`meta.root` equals the root you ran and `meta.generated_at` is newer than the
harness generation time. Read the workflow task's `.result` from its output
file (the completion notification text truncates).

**Step 5 — audit (the canonical acceptance gate).**

```powershell
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

Runs the four free deterministic gates over the whole key set (§7), writes
`audit_window.report.{json,md}`, `window_status.{json,md}`,
`window_ledger.jsonl`, `requeue.keys.txt`, `judge_sample.keys.txt` under
`src\pilot\output`. Record token/time economics on the same command
(`--wall-clock-minutes`, `--max-*-tokens`, `--weekly-cap-fired`) — metric
coverage is the standing instrumentation gap (wall-clock on 12/458 windows as
of 10-07-2026). Stale output (meta/key/hash mismatch) is **refused** before
gates and does not overwrite an existing `requeue.keys.txt`; `--allow-stale`
is forensic-only. One `wf_output.json` per root — never combine roots.

**Step 6 — requeue.**

```powershell
python src\pilot\requeue_from_audit.py <root> --transient   # null cards only
python src\pilot\requeue_from_audit.py <root>               # all requeue keys (auto --no-tm)
```

The requeue list is split: `requeue.transient.keys.txt` (nulls =
rate-limit/dropout — cheap re-run, low concurrency) vs
`requeue.defect.keys.txt` (a gate flagged content — rework, TM disabled, and
the flagged fragment SHAs are denylisted so the fragment TM can never re-serve
them, H304). Repeat run→audit until the requeue is empty or clearly
diminishing. `save_and_audit.py --merge` is better-attempt-wins — a requeue
can no longer regress a card.

**Step 7 — semantic judging (the only LLM QA spend).**
Only if mechanical gates pass and `judge_sample.keys.txt` is non-empty: that
queue = all Python-gate failures + a deterministic ~10% clean-card sample. It
is NOT the mechanical requeue list. Cheap pre-triage:
`python src\pilot\prompt_rule_audit.py --cards wf_output.json --review-limit 25`.

**Step 8 — promote + rebuild TM.**

```powershell
python src\promote_final_cards.py --gen-model-version claude-sonnet-5 --glob <explicit>
python src\pilot\translation_memory.py build --lang ru
python src\pilot\translation_memory.py build-frags --lang ru   # if a heal emitted frag_prov
```

⚠️ **Since H1080 Stage 3 (PR #511, 17-07-2026) promotion hard-refuses any
workflow output not bound to a manifest-v2 execution** — `promote_final_cards.py`
raises `PromotionContractError` on anything without
`execution_manifest_schema = pwg.headless_execution_manifest.v2` (profile slot,
config-dir fingerprint, model identifier all mandatory), and RUN_FREQ_MAX now
routes new attempts through `coordinator.py prepare ... --profile-slot c4` on
the CLI/headless path, NOT the legacy Workflow route (a bound generated
template aborts before its first agent call on the old route). The Workflow-run
framing in steps 4-7 above describes the historical lane; follow RUN_FREQ_MAX's
current manifest-v2 procedure for any new attempt.

The two H255 footguns are now **mechanically guarded** (same hardening wave):
`--merge` with the implicit broad glob is refused outright — an explicit
`--glob` is mandatory — and `validate_promotion_entry()` revalidates every
candidate (final-card schema, exact `selected_keys` membership, per-key input
hashes, non-synthetic provenance, `{Tn}` residue) independent of
audit/coordinator state. Still filter `requeue_defect` keys yourself — the
audit's defect split remains the operator's responsibility. Under multi-account operation only
ONE account promotes per catch-up (single-promoter rule,
[src/promote_lock.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_lock.py)).
Promotion merges at **sub-card level** — the root-level merge that would have
wiped other roots' rows was caught and killed in Phase 4.

**Step 9 — closeout (before the handoff is closed).**
Any launch with a failure, null wave, stall, kill, stale-refusal, retry pass,
or cost drift gets a classified entry in
[LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md);
verify with `python src\pilot\check_launch_ledger.py --handoff H###`. Classify
every RU/EN-touching fix in the LANG_PARITY ledger (§8). Update
`.ai_state.md` + `src\pilot\RUN_LOG.md`. Micro-commit (`ai-wip:`), next root.

## 6. Lanes, concurrency, and what is paused

**Calibration is lane-specific — never copy one lane's kill budget, cost, or
concurrency envelope to another** (H220 is the standing counter-example: the
dense-verb-batch kill gate false-killed valid no-PWG singletons). The lanes:

| Lane | State (11-07-2026) | Discipline |
|---|---|---|
| **Verb drain** (H151, standing) | ACTIVE — 749 DCS-attested roots, 46 promoted / 703 remaining as of 04-07-2026; queue via `verb_worklist.py` | one root at a time, RUN_FREQ_MAX loop verbatim |
| **Nominal small** | production-proven (H201: 100/100 cards, 306 senses) | normal loop, grammar layer OFF in prompts |
| **Nominal medium50 / band-4** | **PAUSED — do not launch** (H317→H389→H437→H442 saga) | see below |
| **No-PWG supplement chain** (232 lemmas) | unblocked but PAUSED ON INFRA (H255: 57% transient on a degraded host, 27 keys not requeued) | single-fragment cards, small batches, 180 s ceiling budget |
| **Monster cards** (kAla-class) | defer lane | never bulk-run; `deferred_monsters.jsonl`, human-budgeted session only |
| **Sub-agent fan-outs** (synthesis etc.) | bare fan-outs BANNED (H234 fiasco) | always [src/synth_dispatch.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_dispatch.py): ≤3 concurrent (hard cap 4), liveness = output-file growth ONLY, confirmed-dead before redispatch, watcher-safe landing, >800-`<ls>` inputs auto-routed to the zero-LLM assembler |

**Concurrency (global, MG-locked).** Default ONE Workflow window at a time;
**≤3-wide is an upper bound, not a target, and it is global across all
accounts**. Each harness already fans out to ~8–14 agents internally. Slice D
launched 18 roots at once → 80+ 429s → 117 transient nulls; H317 showed even
3-wide collapses on an unstable session. In any session with fresh transport
errors, run a solo reference window clean before trusting any width. Running
3 accounts: one worktree per account, shard roots via `verb_worklist.py`
first, single-promoter — the protocol lives in
[PIPELINE_CAPABILITY_AUDIT_2026-07-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md).

**The medium50 pause — never relaunch blind.** The band-4 nominal-singleton
lane is paused with the H442 3-launch cap **exhausted and zero measurable
clean-rate** (all three launches infra-confounded). The failure chain, by
elimination: H317 blamed concurrency (superseded) → H389 found the real
deterministic blocker (Workflow safety classifier refusing the fat schema;
FIXED by H428's schema slim) → H437 isolated heal/kill-budget starvation
(0 connection errors, 2/37 clean, ~2M tokens per window for ~1 clean card) → H442 landed two
guardrails (`PER_CARD_HEAL_BUDGET`, `KILL_TIMEOUT_NO_BISECT`,
[PR #301](https://github.com/gasyoun/SanskritLexicography/pull/301)) that are
**untested in the field, not wrong** — every validation window since has been
infra-confounded. One of the two structural findings is FIXED on master: the split
translate/heal budget pools landed 10-07-2026 (`src/pilot/agent_budget.py`,
PR #311 — the heal ceiling now equals the sum of per-card heal ceilings, so
the window pool cannot fire before the per-card guards; LANG_PARITY
`split_agent_budget_pools_20260710`, SHARED). Still true: the trivial probe
gate is necessary-but-insufficient (hence the
≥5 KB load-representative probe, step 1). Preconditions to resume: a healthy
≥5 KB GO probe, then the `h317_w1b` canary — and do NOT re-tune heal budgets
on infra-confounded evidence.

## 7. Gates, kill mechanics, and selftests

**The four free deterministic gates** (0 tokens, 100% of cards), all inside
[audit_window.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py):
NWS owner-map (misattribution quarantined as `*.merged.REJECTED.md`), markup
fidelity (`<ls>`/`{#…#}` counts vs source — a mismatching card is nulled, never
emitted garbled), sense coverage (every source sense present, Nachträge
included), sense duplicates (cross-part, via `audit_sense_dupes.py` logic).
Plus [src/stage2_pregate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/stage2_pregate.py)
(H405): the mechanical pre-gate measured 99.72% CLEAN / 0.10% hard-FAIL over
the 11,261-row store, wired into the window audit as `stage2_mechanical`;
mechanical criteria are stripped from the judge prompts — judges judge
semantics only.

**The wall-clock kill gate** (in every generated harness): each schema-bearing
`agent()` call races a `setTimeout` budget scaled to its masked-skeleton byte
size (the measured best predictor; `KILL_FACTOR=2`, tunable `--kill-factor`,
`--no-kill`). A killed call falls to binary-split / selfheal fragments — cards
are recovered, never dropped. Runtime constraints shaped it: `Date.now()` is
banned in Workflow scripts and `AbortController` doesn't exist, so a killed
call keeps running in the background — the harness just stops blocking on it.
Budgets have diverged by lane since the first calibration: no-fallback singles
get the 180 s ceiling (H220), the heal lane shows a 45 s floor / 180 s ceiling
in practice (H442), and `KILL_TIMEOUT_NO_BISECT` now stops the
kill-timeout × bisection waste spiral. Separately, each window carries a
`MAX_AGENTS` budget kill-switch (factor 3 × batches + headroom 10) that trips
`budget_kill_switch_tripped=true` and requeues the remainder. When a new stall
class appears, promote it from "caught by the kill gate" to its own structural
presplit trigger — the discipline that produced the H155 sense-count trigger.

**Selftests.**
[window_selftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py)
— **142 tests, all passing as verified 18-07-2026 (H1110 Phase 2)** — pins
every historical bug class (stale-refusal preserving the requeue list, schema
size ceiling, kill-gate wiring, `sense_ord` threading, parity-ledger
completeness, telemetry counters…). Run it plus
`python -m py_compile <changed files>` after any pipeline code change; the CI
RussianTranslation-gates job runs the fixture selftests too. Also verified
this session: `python src/pilot/lang_parity_check.py` → "41 entries, all
verdicts complete, no drift"; `python src/pilot/check_launch_ledger.py --since
2026-07-05` → "14 entries complete".

## 8. Cross-language parity — the RU/EN contract

The pipeline is lang-parameterized (RU primary, EN secondary). **Before
closing any session that fixed or added behavior on one language path,
classify the change in
[LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)**
as SHARED (lang-agnostic code, applies everywhere), INTENTIONAL-DIVERGENCE
(one-line why REQUIRED), or GAP (tracking reference REQUIRED — an untracked
GAP fails the gate). The ledger is a machine-readable JSON block; the gate
(`lang_parity_check.py`, wired into `window_selftest.py`) also fails on
sha-drift of any tracked file — re-affirm with `--update-hash <entry-id>`
after verifying your edit didn't change the described behavior.

State as of 18-07-2026: **53 entries — 45 SHARED, 7 INTENTIONAL-DIVERGENCE,
1 GAP** (`defect_fragment_denylist_h304`: the EN auditor doesn't emit the
defect-fragment denylist yet). The seven divergences that must NOT be "fixed":
promotion stays two scripts (different store schemas); four RU-only mechanisms
with no EN counterpart (corpus_gate evidence markers, evidence retrofit
annotators, koch `см.` cross-reference resolution, fri Latin-apparatus
resolution); and two H1152 EN-judge guards (`en_polyseme_judge_guard_h1152`,
`en_de_residue_soft_class_h1152`). The former model-pin divergence left the
list — H818 closed it as SHARED (both languages pin `claude-sonnet-5`). Root cause of the founding failure: `audit_window_en.py`
reimplements its gates instead of sharing RU's — assume any RU gate fix needs
an explicit EN parity verdict.

## 9. Data assets and the rights boundary

| Asset | Where | Status |
|---|---|---|
| RU store `src/pwg_ru_translated.jsonl` (+ EN store) | gitignored, local-only | 11,603 rows as of 18-07-2026 (post-H1080 repair); per-sense provenance |
| 5 harvested Sa→Ru dicts (`koch/kow/kna/fri/smirnov.jsonl`) | gitignored | in-copyright sources; rebuild via `build_src.py` |
| `corpus_lexicon.jsonl` (1,091,528 pairs) + `mined` tier (10,132 pairs, 97%-precision-gated) + SPECIALIST glossaries (663 entries) | gitignored | mined tier quarantined — never merged into the clean lexicon |
| TM sidecars `translation_memory.*` | gitignored | rebuild after every promotion; regenerable |
| TMX 1.4b export + A/B/C grades (`build_tmx.py`, `tm_grade.py`) | gitignored `release/corpus_tm/` | **NO public release** — per-translator rights clearance (H215 Slice 5) is the blocker |
| Grammar layer (Whitney roots, Zaliznyak-style index, vidyut paradigms) | tracked (`datapackage.json`, CC-BY-SA-4.0) | structured data, deliberately NOT in translation prompts (A/B: no gain) |
| Article site (147 roots, 11,275 senses as of 10-07-2026) | published at [gasyoun.github.io/SanskritLexicography](https://gasyoun.github.io/SanskritLexicography/) | render-time presentation layer (§4) |
| Review sheets (`review/*.html`) | gitignored | embed unpublished RU — public repo, so never committed; registered in [REVIEW_SHEETS_INDEX](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md) |

The rule behind the column: **committed = reproducible code + small fixtures +
evidence samples; gitignored = bulk data, anything rights-encumbered, anything
regenerable.** Untracked files are also watcher-bait (H234 #4) — author agent
outputs outside the repo and land atomically.

## 10. Script census (as of 11-07-2026)

**252 Python files** as of 18-07-2026: 170 at `src/` top level, 81 under `src/pilot/` (+ root `save_and_audit.py`)
(including `archive/`, `dashboard/`, `eval/`), plus the repo-root
[save_and_audit.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/save_and_audit.py).
All tracked; the data they read/write is gitignored (§9). Three tracked `.js`
(the harness template, its archived predecessor, the dashboard) — every
harness an operator actually runs is generated and gitignored. Functional
map, condensed (entry points in bold):

| Role | Scripts |
|---|---|
| Preflight | **`freq_route.py`**, **`pilot/verb_worklist.py`**, `pilot/nominals_worklist.py`, **`pilot/root_window_status.py`**, **`pilot/perf_preflight.py`**, `pilot/prompt_rule_audit.py`, **`_pilot_gen_merged.py`** (5-layer source builder) |
| Harness generation | **`pilot/gen_opt_harness2.py`** (canonical), `pilot/autosplit_requeue.py`, **`pilot/requeue_from_audit.py`**, `pilot/gen_fidelity_judge*.py` (sampled-judge workflows) |
| Audit gates | **`pilot/audit_window.py`** (canonical RU), `pilot/audit_window_en.py`, `stage2_pregate.py`, `audit_coverage.py`, `audit_sense_dupes.py`, `audit_root_split.py`, `nws_split.py` (owner map), `pilot/ru_coverage.py`, `validate_*.py` |
| Promote / store | **`promote_final_cards.py`**, `promote_en.py`, `promote_lock.py`, **root `save_and_audit.py`** (save + audit + merge in one step) |
| Translation memory | **`pilot/translation_memory.py`**, `tm_grade.py`, `tm_align.py`, `build_tmx.py`, `build_l0.py`, `ingest_oral.py`/`build_oral_l0.py` |
| Instrumentation | `pilot/check_launch_ledger.py`, `pilot/harvest_launch_stats.py`, `pilot/probe_log.py`, `pilot/classify_run.py`, `pilot/parse_workflow_cost.py`, `pilot/coordinator.py`, **`pilot/dashboard_server.py`** (live UI, port 8765), `pilot/lang_parity_check.py`, `pipeline_version.py`, `pilot/layer_versions.py`, `pilot/watch_upstream.py` |
| Selftests | **`pilot/window_selftest.py`**, `roadmap_check.py`, `review_changelog_guard.py`, `lod_acceptance.py` |
| Release / edition | `preflight_remaining_gates.py`, `release_readiness.py`, `make_edition_cut.py`, `build_reglue.py` (the edition backbone — synthesize-first lost the bake-off), `build_article_site.py`, `export_interop.py`, `export_lod.py` |
| Gold / human review | the `gold_*.py` family (14 scripts), `fidelity_sample*.py`, `build_h180_review_sheets.py` |
| Source / corpus builders | `build_src.py`, `build_corpus_lexicon.py`, `mine_running_text.py`, `build_glossaries.py`, `corpus_gate.py`, `pwg_mask.py`, `dict_merge.py`, `build_dcs_*.py`, `build_learner_scores.py`, `build_relationships.py` |
| Renou / grammar layers | `renou*.py` (12), `annotate_*.py`, `whitney_grammar.py`, `nominal_grammar.py`, `reverse_index.py`, `government_census.py` |
| Fan-out guard | **`synth_dispatch.py`** (the only sanctioned multi-agent dispatcher) |
| One-offs / `_`-prefixed | ~20–25 dated bake-off, ad-hoc-build, and watcher scripts — check the docstring before reuse |

**Dead / superseded — do not run for production:**
`pilot/archive/superseded_2026-07-06/gen_opt_harness.py` + `_pilot_gen.py`
(0 importers, H188-confirmed); `pilot/archive/legacy_max_2026-06-27/` (manual
a-section path, audit history only); `pilot/run_real_test.py` (live in tree
but self-marked superseded); `scale_route.py` (superseded by `freq_route.py`).

**Destructive on re-run — think before typing:**

| Script | Destroys / overwrites |
|---|---|
| `promote_final_cards.py` | rewrites the canonical store (read-merge-replace); concurrent runs are last-writer-wins — single-promoter rule + `promote_lock.py` |
| `_pilot_gen_merged.py --root-split` | **deletes + regenerates a root's rootmap**, orphaning its already-translated sub-cards — not a safe post-hoc fix |
| `pilot/translation_memory.py build`/`build-frags` | rebuilds the TM sidecar from scratch (regenerable, but a mid-window rebuild changes TM-hit behavior) |
| `_purge_lexicon.py` | deletes rows from `corpus_lexicon.jsonl` |
| `promote_en.py` | overwrites `en` fields on store rows in place |
| any harness run | overwrites `wf_output.json` — capture per step 4 before the next run |

## 11. Recurring failure shapes — read before declaring a new bug

Condensed from
[PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)
and the 17-entry ledger in
[LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)
(against a 458-window / 62-root population as of 18-07-2026, honest hard-fail
rate 24.67% — `needs_requeue` is the normal iterative state, NOT a failure;
see [LAUNCH_STATS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md)):

1. **Wide concurrency collapses the run** — 429 waves, transient nulls.
   Process fix (≤3-wide global), not code.
2. **Transcript size says nothing about agent liveness** — transcripts buffer;
   only output-file growth counts. Ten healthy agents were once killed on the
   0-byte inference.
3. **An unconfirmed-dead agent is a zombie** — it finishes later and
   overwrites the good result. Confirm death; one writer per file; seal
   landed outputs.
4. **Untracked files are watcher-bait** — the repo watcher deletes them
   mid-write. Stage outside the repo, land atomically, re-verify the sha.
5. **TM re-serves rejected content** — TM addresses on input hash, not
   pass/fail history. `--no-tm` on every defect requeue + the H304 fragment
   denylist.
6. **A manual save between Workflow and disk is a loss point** — H145. Drive
   the Workflow from the session; verify `meta.root` after saving.
7. **Gate false positives cluster around markup/language misclassification** —
   every gate-bug hunt found a heuristic built for one input class firing on a
   structurally similar other one. Suspect this before suspecting the
   translation.
8. **Unchecked cost estimates are optimistic about fan-out** — presplit
   giants priced as one call (13 estimated vs 102 real agents on `vid`).
9. **A complexity metric tuned for one driver is blind to the next** —
   citation count waved through the 35-sense/11-`<ls>` `tyaj~~h0_zz_pw`
   addenda card. Output complexity is a SUM (citations, senses, gloss volume,
   masked tokens, nesting, batch sums); drivers #3–#5 still have only the
   kill-gate backstop, no structural trigger.
10. **A fix on one language path doesn't reach the other** — §8.
11. **Kill-gate calibration is lane-specific** — §6.
12. **A repeated `unknown` failure shape is not an accepted residual** — it
    becomes a bug-hunt handoff (that rule produced H442).

## 12. Session-close checklist

1. Deterministic gates green, requeue state understood — never claim a window
   accepted otherwise.
2. Non-clean launch → classified [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)
   entry + `check_launch_ledger.py --handoff H###` green.
3. RU/EN-touching change → LANG_PARITY verdict + `lang_parity_check.py` green
   (§8).
4. `window_selftest.py` + `py_compile` green on any code change.
5. Store promoted → TM rebuilt (`build --lang ru`, `build-frags` if heal
   provenance exists).
6. [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
   (subsystem AND repo root, in lockstep) + `src/pilot/RUN_LOG.md` updated;
   micro-commit `ai-wip:`; deliverables via worktree + PR.
7. Tables/findings worth keeping → the right hub (FINDINGS / RESULTS_LOG /
   PROJECT_INTERLINKS), not chat.

## 13. Multi-account bulk protocol (3→4 accounts)

Canonical home of the protocol the root AGENTS sheet §5 used to restate
(folded here 18-07-2026, H1245; designed in
[PIPELINE_CAPABILITY_AUDIT_2026-07-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md)
§W1, hardened by H336 / [PR #254](https://github.com/gasyoun/SanskritLexicography/pull/254):
promotion claim files, per-window namespacing, append hygiene):

1. **One worktree/clone per account** — state paths are repo-relative, so
   per-clone runs are disk-isolated for free.
2. **Shard by root via the worklist before starting** — disjoint slices;
   root-sharding guarantees disjoint rootmaps, inputs, TM card keys, requeue
   sets. Fragment-TM cross-duplication is benign iff sidecars are rebuilt by
   the single promoter.
3. **Single-promoter rule** — one owner runs `promote_final_cards.py --merge`
   + TM rebuilds per convergence cycle
   ([src/promote_lock.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_lock.py));
   non-promoter accounts stop at "audited clean, `wf_output.<window>.json`
   saved + RUN_LOG pointer".
4. **Global ≤3 translation lanes** regardless of account count: 4 accounts ×
   1 root each, max 3 in flight (the Slice-D collapse at ~18 concurrent
   workflows was a server-side cliff — it does not care which account sent
   the load).
5. **Cloud/web sessions (claude.ai/code) return outputs via git**, since
   locks never span machines: commit `wf_output.<window>.json` +
   `audit_window.report.json` onto the session branch under
   `RussianTranslation/incoming/<account>/<window>/` (a tracked landing
   directory — create on first use), PR it, and the promoter promotes from
   `incoming/` then deletes the landed files in the same PR. The store itself
   is gitignored and NEVER travels through git — only `wf_output` payloads do.
   ⚠️ Any promotion from `incoming/` still passes the manifest-v2 binding
   gate (§5 step 8) — unbound payloads are refused.

## 14. Interactive sessions vs workflow fan-outs — two different limits

Folded from the root HUMAN_RU sheet §8 (18-07-2026, H1245) — the distinction
matters when planning account load:

- **Interactive Claude Code sessions**: there is no concurrency limit that
  surfaces as API errors — sessions share the account's 5-hour rolling window
  and weekly quota; exhaustion reads as a clean "limit reached", not an error.
  2–3 concurrent Opus-tier sessions per account is comfortable; more just
  burns the window faster.
- **Workflow fan-outs are what actually fall over**: measured
  `Connection closed mid-response` and kill-timeouts appear under high agent
  concurrency (the Slice-D collapse ≈18 concurrent root workflows) — hence
  the global ≤3-lane rule above. This is server-side load-shedding; the
  account of origin is irrelevant.

Safe per-account shape: **1 generation lane + 1–2 light sessions** (audit,
promotion, docs).

_Dr. Mārcis Gasūns_
