# RussianTranslation deep manual — the mw_ru and pwg_ru pipelines

_Created: 11-07-2026 · Last updated: 24-07-2026_

The subsystem deep manual for
[RussianTranslation/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation)
— first item of the deep-manual queue in
[PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md)
(handoff H606, authored by Fable 5 `claude-fable-5`; refreshed 24-07-2026 by
Grok 4.5). Audience: **maintainer / operator** — a fresh session that has to
run a production translation window, audit it, promote it, and close it out
without rediscovering a fixed bug. The orientation-layer sibling is
[MAINTAINER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md);
this document goes one level deeper into a single subsystem. Every count in
this manual is stamped with its as-of date; the live truth is always
[RussianTranslation/.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
and the command output of the scripts themselves.

## 0. Cold start (read this first — then stop digging)

**Today's production truth in five lines.**

1. Route = **headless CLI, manifest v2** (`execution_route: claude-cli-headless`). Max-Workflow is forensics only.
2. Generation model = **Sonnet 5 (`claude-sonnet-5`)**, pinned in the harness — not the interactive session model.
3. Store = gitignored `src/pwg_ru_translated.jsonl` (**11,603** sense rows as of 24-07-2026); never commit bulk RU.
4. Live queue = [`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md) — not this manual.
5. Trust order: **command output** > `.ai_state.md` > dated docs.

**Primary path = skills** (not a CLI scavenger hunt):

| Step | Skill | Stops when… |
|---|---|---|
| Live readiness | [`/pwg-live-gate`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md) | health under 30 s + canary 3/3 clean → GO; else **do not spend** |
| Paid window | [`/pwg-bounded-run`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-bounded-run.md) | one profile, `max-wide=1`, `--stop-before-promote` |
| Drain loop | [`/pwg-drain`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-drain.md) | next worklist head after gate + close |
| Close / promote | [`/pwg-window-close`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-window-close.md) | audit + provenance + exact key delta green |

**Five commands if skills are unavailable** (from `RussianTranslation/`):

```powershell
python src\pilot\root_window_status.py <root>
python src\pilot\perf_preflight.py <root>
python src\pilot\gen_opt_harness2.py <root>
# headless execute sealed manifest v2 → wf_output.json  (see RUN_FREQ_MAX)
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

**Stop conditions (do not invent a sixth path).**

- Live-gate NO-GO or stale GO → stop; never re-tune kill budgets on host noise.
- Promote without `execution_manifest_schema = pwg.headless_execution_manifest.v2` → hard refuse (correct).
- `--max-agents 1` on multi-key windows → only-b0 starvation (ledger `C2_M50_W1_MAX_AGENTS1_2026-07-24`).
- Symptom unknown → §11 cookbook, then [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md) — not a new theory.

**Where not to dig on first contact:** `PIPELINE_HISTORY.md` (narrative), `mw_ru` post-mortem (§3), archive handoffs, Workflow harness JS. Verbatim loop + worked headless example: [RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md).

## 1. What this subsystem is

Two LLM dictionary-translation pipelines sharing one engine design:

| Pipeline | Source → target | Status | Scale |
|---|---|---|---|
| `mw_ru` | Monier-Williams (English) → Russian | **finished** (May 2026); covered here as a post-mortem, §3 | 287,358 cards |
| `pwg_ru` | PWG / Böhtlingk-Roth (German) → Russian (primary) + English (secondary) | **live production on headless CLI (manifest v2, H1110)** — every paid window needs a **fresh** `/pwg-live-gate` GO (health + `dq_canary_puregloss`); host latency and session limits still gate spend | 106,082-headword universe; store **11,603** rows as of 24-07-2026 (H1080 hash-locked repair 17-07: 11,605→11,603); remaining unique ~**5,580** (H1339: 701 verb + 4,757 nominal-PWG + 122 no-PWG) |

The intellectual problem is not per-headword translation difficulty — a
38-unit judge test settled quality early (37/38 publishable). The whole
discipline of the subsystem is making an LLM run **reliable, cheap, and
mechanically verifiable at 100,000-headword scale** with **no Claude API
key** — generation goes through a profile-bound **headless CLI**
(`execution_route: claude-cli-headless`, H1110). The older Max-Workflow-from-
session path is **forensics only**. Everything below — masking, batching,
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
| Quantitative launch denominators (473 windows as of 24-07-2026 harvest) | [LAUNCH_STATS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md) (auto-generated — never hand-edit) |
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
API key**. Production generation runs through the **headless CLI** bound to a
named profile (`CLAUDE_CONFIG_DIR` + roster slot `c2`/`c4`/…), driven by
`coordinator.py` / `bounded_staged_run.py` / `headless_worker.py` under
`execution_route: claude-cli-headless` (H1110). The Max-Workflow lane
(`run_pilot_wf.opt2.js`) is retained for historical forensics only — a new
profile-bound v2 attempt must **not** re-enter Workflow as the production
route. Generation targets **Sonnet 5 (`claude-sonnet-5`)**, and since H818
(12-07-2026) the harness pins that id **explicitly on every `agent()` call,
both RU and EN** (SHARED in LANG_PARITY). The bulk QA judge policy is **Sonnet
judges, Opus 4.8 (`claude-opus-4-8`) adjudicates only rejects** (`ok=false ||
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
time, `wf_file`, `source_profile`, `layer`). **11,603** rows as of 24-07-2026
(post-H1080 repair). Promotions must pass `--gen-model-version
<exact-model-id>` and a bound
`execution_manifest_schema = pwg.headless_execution_manifest.v2`.

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

### 5.0 Skill-primary path (default)

| Phase | Skill | What it owns | Hard refuse / stop |
|---|---|---|---|
| Gate | [`/pwg-live-gate`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md) | ≥5 KB health + `dq_canary_puregloss` → mechanical GO/NO-GO | Stale GO; hand-asserted GO that contradicts `gate_reason` |
| Spend | [`/pwg-bounded-run`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-bounded-run.md) | one profile, `max-wide=1`, `--stop-before-promote`, no widen/retry in bootstrap | Missing fresh gate; unbound profile |
| Drain | [`/pwg-drain`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-drain.md) | pick worklist head → gate → bounded run → close | Gate NO-GO |
| Close | [`/pwg-window-close`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-window-close.md) | audit + provenance + key delta + backup + TM + ledger | Unbound manifest; truncated notice as sole evidence |
| Review packet | [`/pwg-review-packet`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-review-packet.md) | human G5/G6 sheet over promoted `ai_translated` cards | — |

CLI below is the **recovery / forensics appendix** and what the skills call. Prefer skills when available. Verbatim commands + **worked headless example** live in
[RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md).

The loop is fixed: **live-gate → preflight → prepare lease (manifest v2) →
headless execute → deterministic audit → requeue → (optional sample judge) →
promote (stop-before-promote until review) → TM rebuild → closeout.**
Do not skip or reorder.

**Step 0 — session preconditions.**
Check
[.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
WIP + the GTD `🔒 CLAIMED` tags for a concurrent session (H214 tree-intermix
incident). This repo is a shared tree: **isolated worktree + PR, never direct
edits, never `git add -A`.** Run scripts from the `RussianTranslation` repo
root. UTF-8 without BOM everywhere. Bind a **named profile**
(`CLAUDE_CONFIG_DIR` + roster slot) before any paid call — the orchestrator
fingerprints the config dir into the sealed manifest.

**Step 1 — live-gate (mandatory before every paid window).**
Run
[`/pwg-live-gate`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md):
one representative **≥5 KB** health call **and** a separate
`dq_canary_puregloss` synthetic control, both through the headless
manifest-v2 route. GO is **mechanical** from a named policy (`gate_reason`):
health PASS = latency under 30 s + zero connection errors; canary PASS = 3/3
senses + zero SAN-LOSS / TNMASK / unmapped / schema failures. A **stale** GO
(including a previous session's H1447 LIVE_GO) never authorizes a new paid
window. Trivial tiny probes are necessary-but-insufficient (H442). Every blind
launch into a degraded host has cost ~2M tokens for ~0–1 clean cards
(reproduced 3×, H437/H442). Log readings via
[src/pilot/probe_log.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/probe_log.py).

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

**Step 3 — generate harness + prepare lease (manifest v2).**

```powershell
python src\pilot\gen_opt_harness2.py <root>    # batched+masked; emits opt2 + inputs
python src\pilot\coordinator.py prepare LEASE_ID `
  --profile-slot c4 --config-dir C:\path\to\claude-c4 `
  --executor-lane serial-whole-card
```

[gen_opt_harness2.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
is the canonical generator (batched + masked; measured −72% cost on a full
mixed root, −90% on a clean small batch vs per-card). Defaults:
`--output-budget=90` (calibrated live 07-2026), selfheal + binary-split on,
presplit routing on (citation trigger AND the H155 sense-count trigger),
`--tm=auto`. `--no-tm` is the explicit opt-out — **mandatory on defect
requeues** (enforced in `requeue_from_audit.py` since 04-07-2026). The harness
inlines all inputs, sets `tools: []` on translate agents, embeds
rootmap/input SHA-256 provenance, and strips post-generation annotation
fields from the per-call schema (H428). The committed
[run_pilot_wf.js](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_pilot_wf.js)
is a template — never run it directly for production. Legacy
`gen_opt_harness.py` lives under
[src/pilot/archive/superseded_2026-07-06/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src/pilot/archive/superseded_2026-07-06).

Coordinator states: `claimed` / `prepared` / `requeue_prepared` reserve work
but consume **no** model runtime; `begin-run` is the only transition to
`running`; `record-output` moves through `auditing`. Ordinary/manual execution
is globally capped at **three** running leases; four only inside
`max_account_orchestrator.py staged-run` after a fresh matching probe receipt;
five is never allowed.

**Step 4 — headless execute (the only production route).**
Drive the sealed manifest through
[`/pwg-bounded-run`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-bounded-run.md)
/ `bounded_staged_run.py` + `headless_worker.py`: **one profile**,
`max-wide=1`, **`--stop-before-promote`**, no retry / requeue / replacement /
widening in bootstrap mode. Per-profile call concurrency is serialized by the
kernel-backed `ActiveCallClaim`. Agent and timeout budgets are enforced
inside `headless_worker.py` (not merely declared — H1110 / FINDINGS §93).
Save the full payload as `wf_output.json`; verify `meta.root` and that the
execution is bound to
`execution_manifest_schema = pwg.headless_execution_manifest.v2`.

Do **not** use `--max-agents 1` on multi-key / heal-capable windows — that flag
caps **total** translate+heal spawns and starves the window (ledger
`C2_M50_W1_MAX_AGENTS1_2026-07-24`: 0/3 nulls with only `b0` attempted). Leave
manifest budgets alone unless a canary explicitly needs a single-spawn probe.

Historical note: the `vid` worked example (102 agents / 6.6M tokens / ~19 min)
ran on the retired Workflow path; numbers illustrate scale, not the current
executor.

**Step 5 — audit (the canonical acceptance gate).**

```powershell
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

Runs the four free deterministic gates over the whole key set (§7), writes
`audit_window.report.{json,md}`, `window_status.{json,md}`,
`window_ledger.jsonl`, `requeue.keys.txt`, `judge_sample.keys.txt` under
`src\pilot\output`. Record token/time economics on the same command
(`--wall-clock-minutes`, `--max-*-tokens`, `--weekly-cap-fired`). Stale output
(meta/key/hash mismatch) is **refused** before gates and does not overwrite an
existing `requeue.keys.txt`; `--allow-stale` is forensic-only. One
`wf_output.json` per root — never combine roots. Manifest-v2 leases that once
failed to load as v1-only are fixed (H1339 B23).

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
can no longer regress a card. Supervisor requeues materialise real
`prepare-requeue` attempts + `::rqNN` jobs (H1339 A4).

**Step 7 — semantic judging (the only LLM QA spend).**
Only if mechanical gates pass and `judge_sample.keys.txt` is non-empty: that
queue = all Python-gate failures + a deterministic ~10% clean-card sample. It
is NOT the mechanical requeue list. Cheap pre-triage:
`python src\pilot\prompt_rule_audit.py --cards wf_output.json --review-limit 25`.

**Step 8 — promote + rebuild TM (after human/Opus review when stopped).**

```powershell
python src\promote_final_cards.py --gen-model-version claude-sonnet-5 --glob <explicit>
python src\pilot\translation_memory.py build --lang ru
python src\pilot\translation_memory.py build-frags --lang ru   # if a heal emitted frag_prov
```

⚠️ **Since H1080 Stage 3 (PR #511, 17-07-2026) promotion hard-refuses any
output not bound to a manifest-v2 execution** — `promote_final_cards.py`
raises `PromotionContractError` without
`execution_manifest_schema = pwg.headless_execution_manifest.v2` (profile slot,
config-dir fingerprint, model identifier all mandatory). The two H255
footguns are **mechanically guarded**: `--merge` with the implicit broad glob
is refused (explicit `--glob` mandatory), and `validate_promotion_entry()`
revalidates every candidate (final-card schema, exact `selected_keys`
membership, per-key input hashes, non-synthetic provenance, `{Tn}` residue).
Store writes are **fsynced atomic** (RU path; EN reuses the same helper since
H1421 P9). Still filter `requeue_defect` keys yourself. Under multi-account
operation only ONE account promotes per catch-up (single-promoter rule,
[src/promote_lock.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_lock.py)).
Promotion merges at **sub-card level**.

Prefer
[`/pwg-window-close`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-window-close.md)
for the full close packet (audit + provenance + exact key delta + store
backup + one-time TM rebuild + ledger row).

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

| Lane | State (24-07-2026) | Discipline |
|---|---|---|
| **Verb drain** (H151, standing) | ACTIVE when live-gate GO — 749 DCS-attested roots, **48 promoted / 701 remaining** as of 24-07-2026 (`verb_worklist.py`); most remaining still need rootmaps | one root at a time, headless loop §5 |
| **Nominal small** | production-proven (H201: 100/100 cards, 306 senses) | normal loop, grammar layer OFF in prompts |
| **Nominal medium50 / band-4** | **resume only after fresh live-gate** — H1447 plan parked (48 keys, 5 leases); c2 w1 forensics 24-07 proved `--max-agents 1` total-spawn starvation, not host death | serial-c4 / profile-bound headless; never copy canary `--max-agents 1` onto multi-key windows |
| **No-PWG supplement chain** | 122 remaining unique (H1339 population); single-fragment cards | small batches, 180 s ceiling budget; never dense-verb kill envelope |
| **Monster cards** (kAla-class) | defer lane | never bulk-run; `deferred_monsters.jsonl`, human-budgeted session only |
| **Sub-agent fan-outs** (synthesis etc.) | bare fan-outs BANNED (H234 fiasco) | always [src/synth_dispatch.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_dispatch.py): ≤3 concurrent (hard cap 4), liveness = output-file growth ONLY, confirmed-dead before redispatch, watcher-safe landing, >800-`<ls>` inputs auto-routed to the zero-LLM assembler |

**Concurrency (global, MG-locked).** Default **one headless window** at a
time; ordinary/manual leases ≤**3** running globally; four only inside
`max_account_orchestrator.py staged-run` after a fresh matching probe receipt;
five never. Each harness already fans out to many internal agent calls. Slice
D launched 18 roots at once → 80+ 429s → 117 transient nulls. In any session
with fresh transport / `rate_limit` errors, run a solo reference window clean
before trusting any width. Multi-account: one worktree per account, shard
roots first, single-promoter — see
[PIPELINE_CAPABILITY_AUDIT_2026-07-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md).

**medium50 — never relaunch blind.** Historical chain: H317 concurrency
blame (superseded) → H389 fat-schema refusal (FIXED H428) → H437 heal/kill
starvation → H442 guardrails (`PER_CARD_HEAL_BUDGET`, `KILL_TIMEOUT_NO_BISECT`,
[PR #301](https://github.com/gasyoun/SanskritLexicography/pull/301)) + split
budget pools ([PR #311](https://github.com/gasyoun/SanskritLexicography/pull/311)).
H1447 (22-07) derived mechanical LIVE_GO on c4 then stopped honestly at fleet
warm-up — **zero production calls**, plan survives as committed worklist.
24-07 c2 w1: operator `--max-agents 1` caused 0/3-only-b0; re-run without the
flag multi-spawned then hit session `rate_limit`. Resume precondition:
**fresh** §5 step-1 GO, then bounded w1 with **manifest budgets only**.

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
— **182** `test_*` functions in the module as of 24-07-2026; journal-verified
runs report **173/173** green after H1421 (and **157/157** at H1339 close —
the suite grows with each hardening wave). Pins every historical bug class
(stale-refusal preserving the requeue list, schema size ceiling, kill-gate
wiring, `sense_ord` threading, parity-ledger completeness, fsynced promote,
manifest-v2 auditability…). Run it plus `python -m py_compile <changed files>`
after any pipeline code change; the CI RussianTranslation-gates job runs the
fixture selftests too. Parity gate as of 24-07-2026:
`python src/pilot/lang_parity_check.py` → **74 entries, all verdicts complete,
no drift**.

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

State as of 24-07-2026: **74 entries, no drift** (ledger grew through H1339 /
H1421 factory hardening — re-read the file for the current SHARED /
INTENTIONAL-DIVERGENCE / GAP split). Divergences that must NOT be "fixed"
include: promotion stays two scripts (different store schemas); several
RU-only mechanisms with no EN counterpart (corpus_gate evidence markers,
evidence retrofit annotators, koch `см.` cross-reference resolution, fri
Latin-apparatus resolution); and EN-judge guards from H1152. H818 closed the
model-pin divergence as SHARED (both languages pin `claude-sonnet-5`). Root
cause of the founding failure: `audit_window_en.py` reimplements its gates
instead of sharing RU's — assume any RU gate fix needs an explicit EN parity
verdict.

## 9. Data assets and the rights boundary

| Asset | Where | Status |
|---|---|---|
| RU store `src/pwg_ru_translated.jsonl` (+ EN store) | gitignored, local-only | 11,603 rows as of 24-07-2026 (post-H1080 repair); per-sense provenance |
| 5 harvested Sa→Ru dicts (`koch/kow/kna/fri/smirnov.jsonl`) | gitignored | in-copyright sources; rebuild via `build_src.py` |
| `corpus_lexicon.jsonl` (1,091,528 pairs) + `mined` tier (10,132 pairs, 97%-precision-gated) + SPECIALIST glossaries (663 entries) | gitignored | mined tier quarantined — never merged into the clean lexicon |
| TM sidecars `translation_memory.*` | gitignored | rebuild after every promotion; regenerable |
| TMX 1.4b export + A/B/C grades (`build_tmx.py`, `tm_grade.py`) | gitignored `release/corpus_tm/` | **NO public release** — per-translator rights clearance (H215 Slice 5) is the blocker |
| Grammar layer (Whitney roots, Zaliznyak-style index, vidyut paradigms) | tracked (`datapackage.json`, CC-BY-SA-4.0) | structured data, deliberately NOT in translation prompts (A/B: no gain) |
| Article site (roots/senses grow with promotions) | published at [gasyoun.github.io/SanskritLexicography](https://gasyoun.github.io/SanskritLexicography/) | render-time presentation layer (§4); recount via site build, not this manual |
| Review sheets (`review/*.html`) | gitignored | embed unpublished RU — public repo, so never committed; registered in [REVIEW_SHEETS_INDEX](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md) |

The rule behind the column: **committed = reproducible code + small fixtures +
evidence samples; gitignored = bulk data, anything rights-encumbered, anything
regenerable.** Untracked files are also watcher-bait (H234 #4) — author agent
outputs outside the repo and land atomically.

## 10. Script census (generated — do not hand-edit the inventory)

**Full role-tagged inventory** is generated:

```powershell
python src\pilot\script_census.py          # → src/pilot/SCRIPT_CENSUS.md
python src\pilot\script_census.py --check  # drift gate
```

Snapshot as of 24-07-2026: **306** Python files under `src/` (+ root
`save_and_audit.py`), excluding archive / fixtures / nws bulk. See
[SCRIPT_CENSUS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/SCRIPT_CENSUS.md).

**Entry points only** (still hand-curated — the generator lists everything):

| Role | Entry points |
|---|---|
| Preflight / live-gate | **`freq_route.py`**, **`pilot/verb_worklist.py`**, **`pilot/root_window_status.py`**, **`pilot/perf_preflight.py`**, **`_pilot_gen_merged.py`**, **`pilot/probe_log.py`**, `pilot/h963_c4_gate0_probe.py` |
| Harness + headless | **`pilot/gen_opt_harness2.py`**, **`pilot/headless_worker.py`**, **`pilot/bounded_staged_run.py`**, **`pilot/coordinator.py`**, **`pilot/requeue_from_audit.py`** |
| Audit | **`pilot/audit_window.py`**, `pilot/audit_window_en.py`, `stage2_pregate.py` |
| Promote / store | **`promote_final_cards.py`**, `promote_en.py`, **`save_and_audit.py`** |
| TM | **`pilot/translation_memory.py`** |
| Selftest / parity | **`pilot/window_selftest.py`**, **`pilot/lang_parity_check.py`**, **`pilot/script_census.py`** |
| Fan-out | **`synth_dispatch.py`** only |

**Dead / superseded — do not run for production:**
`pilot/archive/superseded_2026-07-06/gen_opt_harness.py` + `_pilot_gen.py`;
`pilot/archive/legacy_max_2026-06-27/`; `pilot/run_real_test.py`;
`scale_route.py` (use `freq_route.py`).

**Destructive on re-run — think before typing:**

| Script | Destroys / overwrites |
|---|---|
| `promote_final_cards.py` | rewrites the canonical store (read-merge-replace); concurrent runs are last-writer-wins — single-promoter rule + `promote_lock.py` |
| `_pilot_gen_merged.py --root-split` | **deletes + regenerates a root's rootmap**, orphaning its already-translated sub-cards — not a safe post-hoc fix |
| `pilot/translation_memory.py build`/`build-frags` | rebuilds the TM sidecar from scratch (regenerable, but a mid-window rebuild changes TM-hit behavior) |
| `_purge_lexicon.py` | deletes rows from `corpus_lexicon.jsonl` |
| `promote_en.py` | overwrites `en` fields on store rows in place |
| any harness run | overwrites `wf_output.json` — capture per step 4 before the next run |

## 11. Symptom cookbook — check here before inventing a bug

| Symptom | First check | Fix / stop |
|---|---|---|
| Only `b0` ran; other keys null / missing | `--max-agents` total-spawn cap (`N < selected_keys`) | Omit flag; use manifest budgets. Worker refuses `N < selected_keys` (H1610/H1618). Ledger `C2_M50_W1_MAX_AGENTS1_2026-07-24` |
| Live-gate / health NO-GO (slow or errors) | Fresh ≥5 KB health latency; probe log | **Do not spend.** Do not re-tune kill budgets on host noise |
| Canary not 3/3 or SAN-LOSS / TNMASK | Canary is separate from health; read status-out | Fix route/schema first; never promote canary |
| `PromotionContractError` / unbound promote | Missing `execution_manifest_schema = pwg.headless_execution_manifest.v2` | Re-run headless with profile bind; Workflow payload cannot promote |
| `stale_artifact` audit refuse | `meta.root` / rootmap hash / selected keys mismatch | Preserve `requeue.keys.txt`; regenerate or re-run correct harness |
| All nulls, ~2M tokens, ~0 clean | Host degradation + fat window without GO | Live-gate first; solo reference window before any width |
| Requeue re-introduces rejected content | TM hit on defect fragment | `requeue_from_audit` (auto `--no-tm` except `--transient`) + fsha denylist |
| EN and RU disagree after a "fix" | LANG_PARITY entry missing or GAP | Classify SHARED / INTENTIONAL-DIVERGENCE / GAP; `lang_parity_check.py` |
| Promote wiped other roots | Root-level merge (historical) | Sub-card merge only; single-promoter + `promote_lock.py` |
| Session `rate_limit` mid-window | Account rolling window / weekly quota | Stop; wait for reset; do not widen |
| Coordinator stuck `preparing` / `auditing` | Dead subprocess still claimed | `recover-operation --confirm-dead` only after process is gone |
| `release-run` needed | Worker died mid-run | `release-run --confirm-dead --reason …` — never `record-output` on mere prepared lease |

## 12. Recurring failure shapes — narrative (after the cookbook)

Condensed from
[PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)
and
[LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)
(against a **473**-window / 62-root population as of **24-07-2026** harvest,
honest hard-fail rate **23.89%** — `needs_requeue` is the normal iterative
state, NOT a failure; ledger date span still ends mid-July and is mostly
Workflow-era rows — see [LAUNCH_STATS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md)):

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
6. **A manual save between executor and disk is a loss point** — H145 (Workflow
   era). On headless, still verify `meta.root` + manifest-v2 bind after
   writing `wf_output.json`; never promote an unbound payload.
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

## 13. Session-close checklist

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

## 14. Multi-account bulk protocol (3→4 accounts)

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

## 15. Interactive sessions vs generation fan-outs — two different limits

Folded from the root HUMAN_RU sheet §8 (18-07-2026, H1245); updated 24-07-2026
for the headless route — the distinction still matters when planning account
load:

- **Interactive Claude Code / Grok sessions**: there is no concurrency limit
  that surfaces as API errors — sessions share the account's rolling window
  and weekly quota; exhaustion reads as a clean "limit reached" /
  `rate_limit`, not a garbled error. 2–3 concurrent heavy sessions per
  account is comfortable; more just burns the window faster.
- **Generation fan-outs are what actually fall over**: measured
  `Connection closed mid-response`, kill-timeouts, and session `rate_limit`
  under high agent concurrency (Slice-D ≈18 concurrent root windows; c2
  medium50 w1 after multi-spawn) — hence the global ≤3-lease rule and
  headless `max-wide=1` on bounded paid runs. This is server-side
  load-shedding; the account of origin is irrelevant.
- **`--max-agents` is a total-spawn cap**, not "one batch at a time". Value
  `1` on a multi-key heal-capable window starves non-`b0` work
  (`C2_M50_W1_MAX_AGENTS1_2026-07-24`).

Safe per-account shape: **1 generation lane + 1–2 light sessions** (audit,
promotion, docs).

_Dr. Mārcis Gasūns_
