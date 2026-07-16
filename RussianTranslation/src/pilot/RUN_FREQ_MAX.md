# Runbook — frequency queue on the Max workflow harness

Goal: scale the PWG→Russian production run in DCS-frequency order, with giant
roots split into single-pass units and re-glued after translation. This is the
post-judge path: the 38-unit freq test is complete, 37/38 were publishable, and
the lone sev-3 belongs to the NWS owner-row slip class that the deterministic
audit gate catches.

**QA policy — BALANCED, token-optimized (2026-06-27, [`../../TOKEN_OPTIMIZATION_2026-06-27.md`](../../TOKEN_OPTIMIZATION_2026-06-27.md)):**
the bulk pass is **translate (Sonnet, single-turn inlined) + four FREE Python gates on 100 %
of cards**; the LLM judge is no longer per-card. The measured driver is `cache_read ≈ context ×
turns`, so the run is reshaped to "Python at max, LLM at minimum" — the A/B cut cache_read 3.2×
and eliminated the transient dropouts.

- **Free gates (0 tokens, every card):** the canonical command is
  [`audit_window.py`](audit_window.py). It renders workflow output once, runs NWS owner-map,
  markup fidelity, sense coverage, and sense-duplicate gates against the same key set, writes
  a report/status ledger, and emits the exact re-queue list.
- **Live dashboard:** start it locally with
  `python src/pilot/dashboard_server.py --port 8765` from the `RussianTranslation`
  repo root, then open `http://127.0.0.1:8765/`. It refreshes every 5 seconds and
  shows Max-run status, next action, requeue/sample queues, token/time metrics,
  recent audit events, file freshness, and the G5/G6/G7/G10 print-gate snapshot
  without inventing any human review labels.
- **LLM judge (the only QA spend):** runs ONLY on Python-gate-flagged cards + a deterministic
  ~10 % mistranslation sample written by `audit_window.py` to `judge_sample.keys.txt`.
  **Sonnet judges; Opus adjudicates ONLY its rejects** (`ok=false ||
  severity>=3`), Opus verdict final — see [`../../research/JUDGE_POLICY.md`](../../research/JUDGE_POLICY.md).
  Publishable cards spend no Opus tokens.

## Cross-language parity — read before closing out any RU/EN fix or feature

This pipeline runs RU and EN (and any future language) through the same
lang-parameterized tooling. A fix landing on only one language path and never
reaching the other is a recurring failure mode (3 gate-bug fixes shipped
2026-07-03 stayed RU-only for a day before an audit caught it). Before calling
any fix/feature session done, classify it in
[`../../LANG_PARITY.md`](../../LANG_PARITY.md) as SHARED / INTENTIONAL-DIVERGENCE
(with a one-line why) / GAP (with a tracked follow-up) — see that file's policy
section. `python src/pilot/lang_parity_check.py` enforces ledger completeness +
tracked-file drift and is wired into `window_selftest.py`
(`test_lang_parity_ledger_complete`).

## Current operating truth

- **Session + generation model (H178 A-4a, 06-07-2026):** run in a session that **HAS the
  Workflow tool** — the session model picker does NOT control generation. Generation is
  **always Sonnet 5 (`claude-sonnet-5`)**: the generated harness hardcodes `model:'sonnet'`
  on every `agent()` call. Workflow-tool availability is a per-session tooling fact, not a
  tier rule (Opus 4.8 and Fable 5 sessions had it; one Sonnet chat did not) — check the
  toolset at session start instead of selecting a "generation tier".
- **The translated source is the 5-layer all-in-one** built by
  [`_pilot_gen_merged.py`](../_pilot_gen_merged.py) — PWG main+Nachträge + PW + SCH + PWKVN +
  NWS (owner-mapped) — live since commit `1dad0dd` (17-06-2026), never reverted.
  `csl-orig/v02/pwg/pwg.txt` is read-only and is only the **PWG layer input**, not "the
  source"; the `_zz_pw` / `_zz_sch` / `_zz_pwkvn` / `_zz_nws00` card-ID suffixes are the live
  per-layer routing (H178 A-4b).
- The optimized **translate-only** Max harness is live and is generated per root by
  [`gen_opt_harness2.py`](gen_opt_harness2.py). It masks and batches raw/portrait inputs,
  disables translate-agent tools, auto-uses translation-memory sidecars when present,
  presplits over-budget dense cards into the selfheal lane, and returns provenance metadata
  used by the audit stale guard.
- Article-site/root dashboard lazy loading is already shipped; do not spend performance time
  re-implementing that path.
- Lean TR / prompt trimming was tested and rejected; keep the full production TR unless a new
  measured sequential calibration proves otherwise.
- Superseded a-section/manual harness notes are archived under
  [`archive/legacy_max_2026-06-27/`](archive/legacy_max_2026-06-27/). Do not use those
  files for current production windows.
- The corpus word-alignment lexicon exists; bulk throughput is no longer blocked on that asset.
- Deterministic gates are canonical for bulk acceptance: NWS owner-map, markup fidelity,
  sense coverage, and sense-duplicate checks all run through [`audit_window.py`](audit_window.py).
- Print readiness is a separate downstream gate: G5 review, G6 human gold, G7 double review,
  and G10 edition cut remain blocked until human review/gold work is done.
  `preflight_remaining_gates.py` and `release_readiness.py` are report-only by default; add
  `--fail-on-blocked` when using them as CI/go-no-go gates.
- **Scope ruling (MG, 04-07-2026): drain ALL remaining DCS-attested verb roots**, root-by-root.
  The worklist is enumerated reproducibly by [`verb_worklist.py`](verb_worklist.py) (verbs01
  universe ∩ freq manifest − promoted store): 749 attested verb roots, 46 promoted,
  **703 remaining** (~5.3 MB source) as of 04-07-2026. Operator `--top` output is filtered
  to roots with existing rootmaps; the JSON keeps the full backlog plus
  `blocked_missing_rootmap`. Drain discipline lives in the standing handoff
  [`H151`](https://github.com/gasyoun/Uprava/blob/main/handoffs/H151-Sonnet_RussianTranslation_pwg_ru_verb_batch_drain_04.07.26.md).
- The per-root loop below is unchanged — "all roots next batch" scales the QUEUE, not the
  width. Roots still run **one at a time (≤3-wide max)**; the Slice-D 18×-parallel collapse
  (117 transient nulls) is the standing counter-example.
- **H304 hardening (07-07-2026) — four operator-memory rules are now code paths:**
  (1) **cap-and-defer** — `coordinator.py claim/prepare` act on the `perf_preflight` cost
  gate: an over-ceiling (kAla-class) window is parked in
  [`deferred_monsters.jsonl`](deferred_monsters.jsonl) and refused (`prepare
  --allow-over-cost` only inside a dedicated human-budgeted monster session — MG ruling
  07-07-2026); (2) **gate-outcome memory** — the RU audit writes
  `output/requeue.defect.fshas.txt` and `requeue_from_audit.py` denylists those fragment
  addresses, so `--tm=auto` can never re-serve a gate-flagged fragment (EN emitter is a
  tracked GAP: `defect_fragment_denylist_h304` in [`LANG_PARITY.md`](../../LANG_PARITY.md));
  (3) **better-attempt-wins** — `save_and_audit.py --merge` keeps the better prior attempt
  per card (complete > partial, fewer `missing_fragments` > more), so a requeue can no
  longer regress a card; (4) **presplit topup is sound** — `autosplit_requeue.frag_groups()`
  reconstructs the fragment partition with the budgets of the run that minted the `gN:fM`
  ids (pass the wf `meta` + key), instead of always the heal budget.

The earlier "Opus-judged-every-card" framing was the validation phase; "Sonnet-bulk/Opus-on-reject"
was the 2026-06-26 escalation policy; the per-card LLM judge itself is now dropped from the bulk path.
The older human-driven Max-session wording is obsolete here: the in-chat Workflow route is the
supported production path for optimized harnesses.

## Current preflight

Last local preflight: **2026-06-26**.

```powershell
cd RussianTranslation\src
python freq_route.py 8
python _pilot_gen_merged.py --manifest freq --root-split --limit 3
python verify_root_glue.py
```

Observed state:

- `scale_manifest.freq.json`: **43,968 / 106,082** PWG headwords are DCS-attested
  (**41%**).
- Frequency top lists are advisory unless they come from current
  `verb_worklist.py --top` runnable output; roots missing rootmaps are reported separately in
  `blocked_missing_rootmap`.
- Top 3 with `--root-split`: already generated locally (`0 to generate`), so the
  machine has the required rootmaps/sub-cards for `sTA`, `BU`, and `gam`.
- `verify_root_glue.py`: **ALL GATES PASS**; lossless round-trip, 0 secondary
  conjugation blocks still merged, 60 rootmaps with unique keyed subkeys.
- 2026-06-29 root status refresh: `sTA` is structurally ready but stale-output
  blocked; `BU` (59 sub-cards), `as` (98), and `i` (204) are clean-ready after
  harness generation; `gam`, `yuj`, `vid`, and `han` have stale generated
  raw/portrait inputs and must be pruned/rechecked before harness generation.

The preflight writes only gitignored pilot artifacts except when code/docs are
changed intentionally.

## Prompt/gate nits — DONE, encoded in the harness (verify, don't re-apply)

These four were folded into the inlined prompt of
[`run_pilot_wf.js`](run_pilot_wf.js) and the audit loop; this is now a
**verification checklist**, not a to-do:

- ✅ keep German abbreviations such as `Bed.`/`Schol.` verbatim, never expand —
  `CONV` line + **HARD RULE 3**;
- ✅ render **every** PWG Nachträge patch — **HARD RULE 4** ("ALL RECORDS,
  INCLUDING NACHTRÄGE … dropping any single patch fails coverage"); inputs are
  assembled by `_pilot_gen_merged.py` as the **5-layer all-in-one** (PWG main+Nachträge
  + PW + SCH + PWKVN + NWS), not main+Nachträge alone;
- ✅ treat `<is>...</is>` source italics as siglum text, never `{%...%}` gloss —
  `CONV` line + **HARD RULE 3**;
- ✅ `nws_split.py` owner-map gate — **HARD RULE 5** (authoritative pre-parsed
  owner map) + the deterministic auditor wired into `run_real_test.py audit`
  (quarantines misattribution → `*.merged.REJECTED.md`).

Also encoded (2026-06-26 literature-harvest port): Sanskrit-microstructure
rendering guidance (samāsa right-headedness, the *yad…tad* correlative map,
śāstric formulas, synonym-string cardinality, comma/semicolon sense-grouping,
manner/position forcing) as soft-judged guidance (judge check 7). Source tables:
[`../../glossaries/de_ru_translation_aids.md`](../../glossaries/de_ru_translation_aids.md).

## Window loop

The loop is fixed: **preflight → generate optimized harness → Max Workflow → deterministic
audit → requeue or sampled semantic judging**. Do not skip or reorder these steps.

For enough data to estimate speed and quality, use the live runnable queue plus
`perf_preflight.py`:

1. Generate the current runnable queue with `python src\pilot\verb_worklist.py --top 20`.
2. Run `perf_preflight.py` over the next runnable roots and follow its recommended order.
3. Give any `defer-calibrate` root a dedicated calibration/session. Current calibration
   warning: `sTA` live preflight on 04-07-2026 reports 123 cards, 19 batches, 241 expected
   agents, `defer-calibrate`; do not use the older ~30-agent estimate.

```powershell
cd RussianTranslation\src

# Refresh the frequency manifest if VisualDCS data changed.
python freq_route.py 20

# Ensure the next manifest slice has root-split inputs.
python _pilot_gen_merged.py --manifest freq --root-split --limit 50
```

Preflight the root before spending Claude/Max tokens:

```powershell
python src\pilot\root_window_status.py sTA
python src\pilot\perf_preflight.py sTA
python src\pilot\verb_worklist.py --top 20
python src\pilot\perf_preflight.py sTA BU yuj as i tap dah ram
```

The first command prints the structural state plus one `next action` and one
`next command`; if it disagrees with stale notes elsewhere, trust the command
output and `src\pilot\output\window_status.json`. The second command is read-only
performance accounting: it reports card/fragment TM hits, degenerate pass-through,
presplit routing, batch count, and `agent_expected_after_tm` before Max spend. Use
`--json` when saving a machine-readable preflight report. With more than one root it
prints a compact comparison table plus a recommended order: zero-agent roots are skipped,
low-agent roots run first, and high-agent roots are deferred until cache refresh or
calibration. If presplit keys exist while `translation_memory.frag.<lang>.jsonl` is empty,
the preflight warns to run
`python src\pilot\translation_memory.py build-frags --lang ru` after a heal Workflow emits
`frag_prov`; if no matching `wf_output*.json` contains `frag_prov`, the warning says so.

Generate the harness for the root. **Default: the batched + masked v2 harness**
([`gen_opt_harness2.py`](gen_opt_harness2.py)) — masks each card (pwg_mask), packs
several per agent call, and restores `{Tn}` to source markup in-JS so the result is a
canonical `wf_output.json` (audit consumes it unchanged, no extra step). Measured
**−72 % cost on a full mixed root** (gam: original per-card **\$16.14 → \$4.45**; a clean
small batch is −90 %). Current defaults: `--output-budget=90`, selfheal on,
binary-split on, presplit routing on, and `--tm=auto` (uses
`translation_memory.<lang>.json` + `translation_memory.frag.<lang>.jsonl` when present;
`--no-tm` is the explicit opt-out). Refresh TM after every promotion/heal harvest:
`python src\pilot\translation_memory.py build --lang ru` and, when fragment provenance was
created, `python src\pilot\translation_memory.py build-frags --lang ru`. See
[`../../TLONLY_PROTOTYPE.md`](../../TLONLY_PROTOTYPE.md).

```powershell
python src\pilot\gen_opt_harness2.py sTA            # default (batched+masked, TM auto, output-budget 90)
# -> writes src\pilot\run_pilot_wf.opt2.js  (run THIS in Max, save result as wf_output.json)
# --output-budget=N tunes citation-weighted output packing (default 90).
# --budget=N without --output-budget keeps legacy byte-mode packing.
# --no-tm disables automatic card/fragment translation-memory reuse.
# A batch retries only its still-unresolved cards; a card whose restored <ls>/{#..#}
# counts don't match source is nulled -> requeue (never emitted garbled).
```

Remaining useful speed work is measured, not guessed: increase TM/fragment-TM coverage,
let conservative degenerate cross-reference stubs pass through without an LLM call, and use
[`calibrate_perf_harness.py`](calibrate_perf_harness.py) for scratch-only wider calibration
across fixed key sets (`--arm-set conservative` or `--arm-set wide`). Run live calibration
arms sequentially with cache cooldown; never run same-prompt arms in parallel.
Do not widen degenerate pass-through for editorial correction prose (`lies:`, `zu streichen`,
etc.); those rows stay in the normal LLM lane unless a future fixture proves exact
deterministic reconstruction is safe.

Legacy per-card harness (still supported; no masking/batching):

```powershell
python src\pilot\gen_opt_harness.py sTA             # -> run_pilot_wf.opt.js
```

Confirm the committed prompt template and generated harness still carry the
manual-derived semantic rules before Max spend:

```powershell
python src\pilot\prompt_rule_audit.py --fail-on-missing
```

After this succeeds, a stale `window_status.json` from the previous audit is no longer the next
operator step. `root_window_status.py` should now tell you to run the generated harness in Max,
then audit the fresh `wf_output.json`.

Run the generated harness (default `src\pilot\run_pilot_wf.opt2.js`, or the legacy
`run_pilot_wf.opt.js`) in the Claude/Max Workflow surface and save the JSON result as
`wf_output.json`.
**Immediately after saving, verify the file actually landed before closing the Workflow
tab:** `meta.root` in the freshly-saved `wf_output.json` must equal the root you just ran and
`meta.generated_at` must be newer than the harness generation time. The H145 `vid` run
(03-07-2026) was lost exactly here — the Workflow completed but the save never reached disk,
and the stale file silently still held the previous root. A Claude Code session driving the
Workflow tool writes the file itself and does not have this manual hand-off gap; prefer that
route for production windows. Both are self-contained: they inline inputs, disable translate-agent tools
with `tools: []`, and return top-level workflow provenance (`meta`: root, mode, selected keys,
rootmap SHA-256, per-input SHA-256). The v2 harness additionally batches, masks, and restores
`{Tn}` in-JS — its output is already canonical, so the audit step is unchanged. It is the
supported route for the in-chat Workflow tool.
Do not run the committed `run_pilot_wf.js` directly for production windows; it is the template
used by `gen_opt_harness.py`.

Before the mechanical window audit, run the cheap translated-card semantic triage:

```powershell
python src\pilot\prompt_rule_audit.py --cards wf_output.json --review-limit 25
```

This writes the same ignored `prompt_rule_audit.{json,md}` report family with a
separate `card_risks` section and ranked `review_queue`. It is advisory by default;
start human/LLM semantic review from the `review_queue`, while mechanical reruns
still come only from `audit_window.py`. Add `--fail-on-risk` or `--fail-on-high-risk`
only for fixture/CI smoke checks, not for routine operator flow.

Lanes:

- **sparse** card (≤30 `<ls>`): single-turn, inputs inlined, **no tools** — the cheap path for
  the ~43 k normal sub-cards.
- **dense** card (>30 `<ls>`, e.g. a lone over-budget head sense): multi-turn, reads its own
  files, no-abridge directive. Heads are pre-split into citation-light parts by `sense_chunks()`
  (`_pilot_gen_merged.py`, budget `HEAD_CIT_BUDGET=18`), so this lane is a rare fallback.
- 1 automatic retry per stage; `judge:null` (the free Python gates own bulk QA).
- The optimized translate agents explicitly run with `tools: []`; any `Read`
  use in a Max run means an outdated harness file is being used.

Audit the window with the single deterministic command:

```powershell
python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue
```

If Max shows token/time numbers, record them on the same audit command so the ledger captures
the production economics:

```powershell
python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue `
  --wall-clock-minutes 19 `
  --max-cache-read-tokens 6288668 `
  --max-cache-create-tokens 3697049 `
  --max-output-tokens 358884 `
  --max-total-tokens 10300000
```

If the weekly Max cap fires, add `--weekly-cap-fired --weekly-cap-cumulative-tokens N`.

For Stage B and later roots, change only `--root` and the generated harness root
name. Do not combine multiple roots into one `wf_output.json`; audit economics
and requeue keys must remain root-scoped.

The audit first compares workflow provenance against the current rootmap and raw/portrait
inputs. Stale output (missing `meta`, key mismatch, rootmap hash mismatch, or input hash
mismatch) stops before collect/gates/glue and records state `stale_artifact`. Check
`root_window_status.py`: if the optimized harness already matches the current rootmap, rerun
that harness in Max and save a fresh `wf_output.json`; regenerate only when the status command
says the harness is missing, invalid, or scoped to the wrong keys. Use `--allow-stale` only for
forensic inspection.
If stale output is refused, `--write-requeue` does **not** overwrite the existing
`requeue.keys.txt`; stale artifacts cannot produce a trustworthy mechanical requeue list.

The audit writes `audit_window.report.json`, `audit_window.report.md`, `window_status.json`,
`window_status.md`, `window_ledger.jsonl`, `requeue.keys.txt`, and
`judge_sample.keys.txt` under `src\pilot\output`.
Any NWS owner mismatch is quarantined as `*.merged.REJECTED.md`; markup-fidelity, coverage,
sense-duplicate, missing-card, or stale-input failures are re-queues, not accepts.
`prompt_rule_audit.py` is the no-token semantic wiring and translated-card triage check: before
Max it catches missing manual-derived prompt rules; after Max it flags cheap semantic-risk
patterns such as German residue, collapsed synonym strings, circular glosses, missing metadata,
markup/sigla leakage, formula drift, sense-compression signals, and suspicious source-type
evidence. Its ranked `review_queue` is the fastest human-first reading order; it does not
rewrite prompts, requeue cards, or replace human judgment.
`judge_sample.keys.txt` is the semantic review spend queue: all Python-gate failures plus a
deterministic 10 % sample of clean translated keys. It is NOT the mechanical requeue list.

## Concurrency — run a throttled driver, not N parallel chats

**Default to one Workflow window at a time; treat 3-wide as an upper bound, not a target.**
Each generated harness internally fans out to ~8–14 agents, so N concurrent root-harnesses
peak at N×~12 Sonnet agents on a single Max session. Slice D launched 18 at once →
~140–250 peak agents → ~80+ `Server is temporarily limiting requests` 429s → 117 transient
null cards. H317 then showed that even **3 concurrent medium windows** can collapse if the
session/provider is already unstable (0/38 clean, and the solo retry still saw repeated
`Connection closed mid-response`). In any session with fresh transport errors, first run a
single solo reference window and see it return mostly clean before trusting any concurrent
width. A clean sequential sweep is faster end-to-end than a collapsed wide run plus recovery.

**Running 3 accounts at once (3 clones, not 3 chats in one clone)?** Read the
[3-account operating protocol](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md#recommended-3-account-operating-protocol-no-code-changes-needed)
(H335 W1) first: one worktree per account (never a shared clone), shard roots via
`verb_worklist.py` before starting, only ONE account runs `promote_final_cards.py --merge`
per catch-up (single-promoter rule), and the ≤3-wide rule above is **global across all
accounts**, not per-account — 3 accounts × 3-wide each is the 429 danger band all over again.
H336 hardened the direct-path collision matrix that protocol documents (promotion claim file,
`--window-tag` output namespacing, JSONL append hygiene) — see
[promote_lock.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_lock.py)
and `audit_window.py --window-tag` / `requeue_from_audit.py --window-tag` — but the operating
protocol (sharding + single-promoter) is still the primary defense; the hardening is a backstop,
not a substitute for it.

## Flaky API / Internet Policy

- There is no Claude API client in this repo for production PWG translation. Claude work runs
  through the Max Workflow surface, so the local scripts must make interruptions resumable
  instead of trying to hide network loss.
- The generated optimized harness retries each card once. A still-null card is recorded by
  `audit_window.py`. The requeue list is **split** so a cheap re-run never triggers expensive
  rework: `requeue.transient.keys.txt` (null cards = rate-limit/dropout) vs
  `requeue.defect.keys.txt` (a gate flagged real content). A window whose only requeue is
  transient nulls reports state `transient_only` — re-run just those at low concurrency.
- The stale-provenance check is mandatory after any interrupted run. It prevents old
  `wf_output.json` files from being audited against newly regenerated rootmaps or inputs.
  Coordinator/headless runs additionally pass `--execution-manifest`: root, nominal mode,
  input hashes, and result keys must match that prepared contract, with every selected key
  present exactly once. A stale, duplicated, foreign, or unbound result is never promotable.
- A coordinator retry is a new execution attempt on the same lease. The lease seals the
  initial execution-manifest path and SHA-256 as its immutable key universe; every pending
  transient/defect key is bound to the path and SHA-256 of the audit report that classified
  it. `prepare-requeue` reads only this validated `pending_requeue` backlog, never a mutable
  split-key file. Changed reports, foreign/duplicate keys, overlapping classifications, or
  ambiguous legacy provenance fail closed.
- `prepare-requeue` accepts only `promoted_partial`, `needs_requeue`, or `transient_only`;
  promote a `ready_partial` clean subset first. Selecting one lane snapshots the other under
  `current_attempt.remaining_pending`, so a transient retry cannot discard pending defects
  (or vice versa). Clean rows with remaining work become `ready_partial`, promotion becomes
  `promoted_partial`, and the lease reaches `promoted` only after the backlog is empty.
- Each retry is preserved under `artifacts/<lease>/requeue/rqNN-{transient|defect}/` with its
  exact key file, conservatively collected defect-fragment hashes, harness, and execution
  manifest. Allocation advances past the highest state/history attempt and any existing
  `rqNN-*` directory. Unreferenced directories from hard interruptions are recorded as
  orphans and left untouched; only a newly created directory from a caught preparation
  failure is removed. Never copy retry output over prior artifacts or adopt/delete an orphan.
- Standalone `requeue_from_audit.py` remains compatible with the commands below. For a manually
  managed provenance-bound retry, add `--manifest-out <path>` and pass that exact manifest to
  `audit_window.py --execution-manifest <path>` when recording the result.
- `no_pwg_scale_plan.py` reads the tracked `no_pwg_residuals.jsonl` decision ledger and
  skips keys whose latest status is `blocked`. Append a later `retry` or `resolved` row to
  reopen one key, or use `--include-residuals` for a deliberate one-run override. Do not
  delete the history or repeatedly spend Max quota on a documented deterministic failure.
  A fully blocked chunk is listed in `omitted_windows` and does not consume
  `--limit-windows`; preparation advances to the next eligible deterministic index. Plan
  manifests retain plan-wide `selected_headwords` and separately report
  `prepared_headwords`. Staged acceptance uses only windows carrying prepared `headless`
  metadata, so future plan rows cannot inflate its window or headword denominators.
- DeepSeek corpus-lexicon API calls are append-only/resumable in `build_corpus_lexicon.py`.
  Use `DEEPSEEK_RETRIES`, `DEEPSEEK_CONNECT_TIMEOUT`, `DEEPSEEK_READ_TIMEOUT`, and
  `DEEPSEEK_BACKOFF_BASE` to tune retry behavior; failed API batches are logged locally and
  can be retried later with `--retry-failed`.

If `requeue.keys.txt` is non-empty, generate the rerun harness directly from it (pass
`--transient` for the cheap null-only re-run, `--defect` for the rework-only set):

```powershell
python src\pilot\requeue_from_audit.py sTA --transient   # null cards only (state transient_only)
python src\pilot\requeue_from_audit.py sTA               # all requeue keys
```

Run the regenerated `run_pilot_wf.opt2.js`, save its JSON as the next `wf_output.json`, and rerun
`audit_window.py`.

If `requeue.keys.txt` is empty and `judge_sample.keys.txt` is non-empty, send only those keys to
the sampled semantic judge outside Python. Do not block mechanical acceptance on unrelated
documentation cleanup or print-readiness gates.

## Instrumentation

For each Max window, record:

- `OFFSET`, `LIMIT`, fresh units, rejected units, and successful merged cards;
- wall-clock minutes;
- Max-reported input/output/cache tokens if available;
- whether the weekly cap fired, and cumulative tokens at that moment.

`audit_window.py` records the operational state, next action, sample counts, and any token/time
measurements in `window_status.json` and `window_ledger.jsonl`. Append milestone summaries to
`PILOT_COST.md` §6 when a root or run-to-cap tranche is complete. The point is to answer the
feasibility question: one Max seat over roughly two months vs a paid API bulk run.

## Post-launch closeout

Every Workflow/API launch with a failure, null wave, stall, kill, stale-artifact refusal,
retry pass, cost drift, or suspicious residual must be registered in
[`../../LAUNCH_FUCKUPS.md`](../../LAUNCH_FUCKUPS.md) before the handoff is closed. The
entry must include expected vs actual agents/tokens, pass count, failure class, root cause,
guardrail/fix, and residual risk. This is the exhaustive incident register; the narrative
history in [`../../PIPELINE_HISTORY.md`](../../PIPELINE_HISTORY.md) only gets curated
phase-level lessons.

Closeout checklist:

```powershell
# Update the live state and launch evidence.
# - .ai_state.md: handoff result and next physical action
# - src\pilot\RUN_LOG.md: launch metrics and pass/fail narrative
# - LAUNCH_FUCKUPS.md: classified failure record for any non-clean launch

python src\pilot\check_launch_ledger.py --handoff H220
python src\pilot\check_launch_ledger.py --since 2026-07-05
```

Calibration is lane-specific. Keep separate evidence for `verb batch`, `nominal small`,
`nominal monster`, `no-PWG single`, `synth fan-out`, and `external API mining`; do not copy
one lane's kill-budget, cost, or concurrency envelope into another without a measured
launch/replay. H220 is the standing counter-example: the dense-root kill gate was correct
for verb batches but false-killed valid no-fallback no-PWG singleton cards.

## Worked example — one real root, start to finish (vid, 04-07-2026)

A concrete run, with real numbers, so the loop above isn't just abstract steps.
`vid` (55 sub-cards, 5 giant heads at 141-193 `<ls>` citations each):

1. **Preflight:** `python src\pilot\perf_preflight.py vid as BU yuj` → recommended
   order `vid, as, BU, yuj` (agent estimates as of the fixed estimator: 63/21/…).
2. **Generate:** `python src\pilot\gen_opt_harness2.py vid` → 55 cards in 8 batches,
   5 cards routed to presplit (each too dense for one call).

   A new CLI/headless production attempt must mint manifest v2 and bind the actual logical slot
   and config directory at preparation time, for example:

   ```powershell
   python src\pilot\coordinator.py prepare LEASE_ID `
     --profile-slot c4 --config-dir C:\path\to\claude-c4 `
     --executor-lane serial-whole-card
   ```

   `c4` is a roster slot, not evidence of billing identity. Later execution must repeat
   `--only-profile c4`; the orchestrator checks the slot and directory fingerprint against the
   sealed manifest. Old v1 manifests are historical-audit inputs only and cannot be promoted.
3. **Run:** the historical `vid` run drove `run_pilot_wf.opt2.js` via Workflow. Do not use that
   route for a new profile-bound v2 attempt: Workflow cannot prove `CLAUDE_CONFIG_DIR` or join the
   host-wide active-call claim, so a bound generated template now aborts before its first agent
   call. Run the execution manifest through the CLI/headless route instead: use the bounded
   command's default dry-run first, then explicitly add `--execute --only-profile c4`. Every
   admitted production entry point holds the global config-fingerprint claim, so a second c4
   launch fails closed instead of spending concurrently.
   Real result: **102 agents, 6,626,992 tokens, ~19 min wall-clock.**
4. **Capture:** read the workflow task's `.result` from its output file (holds the
   full `{meta, summary, results}` payload uncapped) and write it to `wf_output.json`
   directly — do not rely on the completion notification text, which truncates.
5. **Reorder before auditing:** the harness emits `results` in TM-lane /
   degenerate-lane / batch-completion order, which essentially never matches the
   rootmap's declared `meta.selected_keys` order even though every key is present.
   `window_provenance.stale_check` now compares as sets (fixed 04-07-2026), so this
   step is no longer mandatory, but reordering to `meta.selected_keys` order first
   is still good hygiene (keeps `wf_output.json` in a canonical, diffable shape).
6. **Audit:** `python src\pilot\audit_window.py wf_output.json --root vid --write-requeue`
   → 34/55 clean, 21 requeue (10 transient null, 11 defect), 8 partial-but-usable.
7. **Requeue:** `python src\pilot\requeue_from_audit.py vid` (now automatically
   appends `--no-tm` on anything but `--transient` — fixed 04-07-2026) → a 21-key
   harness, ~7 agents expected. Run it the same way as step 3, then repeat steps
   4-6 until requeue is empty or clearly diminishing (compare to the `gam` history:
   two rounds recovered most residuals, a stubborn few needed a manual resolution).
8. **Promote + rebuild TM:** `promote_final_cards.py --gen-model-version claude-sonnet-5`,
   then `translation_memory.py build --lang ru` (+ `build-frags` if any heal emitted
   `frag_prov`). Promotion requires the canonical store to exist: a missing or misresolved path is
   a hard refusal so backup/shrink/merge guards cannot be bypassed. `--init-store` is reserved for
   an explicit first-ever initialization and itself refuses an existing store. Never use it to
   recover a missing production path. Every candidate is revalidated for final-card schema,
   exact manifest-key membership, real (non-synthetic) provenance, and unresolved `{Tn}` tokens
   immediately before the atomic store replacement.
9. **Close out the launch ledger:** if the run had nulls, retries, kills, stale-artifact
   refusals, or cost drift, update `LAUNCH_FUCKUPS.md` and run
   `python src\pilot\check_launch_ledger.py --handoff H151` (or the active handoff ID).
10. **Micro-commit**, move to the next queued root.

What this run taught (folded into the process above, not left as trivia): the
preflight's agent-count estimate was badly wrong for presplit-heavy roots (now
fixed); 100% of the null cards traced to 2 batches that failed outright, and
specifically to the undersized cards inside them that have no fragment fallback
of their own (an open follow-up, not yet fixed — see `PIPELINE_HISTORY.md`).

## Done criterion

The frequency queue milestone is done when:

- every manifest entry in the target frequency window has a merged card or a
  glued nested article;
- zero `*.merged.REJECTED.md` files remain for that window;
- rootmap-backed giant roots have matching `*.NESTED.md` outputs;
- the cost/quota table has enough windows to estimate the run duration;
- every non-clean Workflow/API launch in the window has a complete
  `LAUNCH_FUCKUPS.md` entry and passes `check_launch_ledger.py`.
