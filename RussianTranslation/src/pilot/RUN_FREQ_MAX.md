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

## Current operating truth

- The optimized **translate-only** Max harness is live and is generated per root by
  [`gen_opt_harness.py`](gen_opt_harness.py). It inlines raw/portrait inputs, disables
  translate-agent tools, and returns provenance metadata used by the audit stale guard.
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
- Canonical next roots: finish the `sTA` re-batch cleanup, then run
  `BU`, `gam`, `yuj`, `as`, `i`, `vid`, `han`.

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
- Frequency top 8: `sTA`, `BU`, `gam`, `yuj`, `as`, `i`, `vid`, `han`.
- Top 3 with `--root-split`: already generated locally (`0 to generate`), so the
  machine has the required rootmaps/sub-cards for `sTA`, `BU`, and `gam`.
- `verify_root_glue.py`: **ALL GATES PASS**; lossless round-trip, 0 secondary
  conjugation blocks still merged, 60 rootmaps with unique keyed subkeys.

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
  assembled main+Nachträge by `_pilot_gen_merged.py`;
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
```

This command prints the structural state plus one `next action` and one
`next command`; if it disagrees with stale notes elsewhere, trust the command
output and `src\pilot\output\window_status.json`.

Generate the **optimized** harness for the root:

```powershell
python src\pilot\gen_opt_harness.py sTA
```

After this succeeds, a stale `window_status.json` from the previous audit is no longer the next
operator step. `root_window_status.py` should now tell you to run the generated harness in Max,
then audit the fresh `wf_output.json`.

Run the generated `src\pilot\run_pilot_wf.opt.js` in the Claude/Max Workflow surface and save
the JSON result as `wf_output.json`. This optimized harness is self-contained: it inlines raw
and portrait inputs, strips `node:fs`, disables translate-agent tools with `tools: []`, and
returns top-level workflow provenance (`meta`: root, mode, selected keys, rootmap SHA-256,
and raw/portrait SHA-256 values). It is the supported route for the in-chat Workflow tool.
Do not run the committed `run_pilot_wf.js` directly for production windows; it is the template
used by `gen_opt_harness.py`.

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
`judge_sample.keys.txt` is the semantic review spend queue: all Python-gate failures plus a
deterministic 10 % sample of clean translated keys. It is NOT the mechanical requeue list.

## Flaky API / Internet Policy

- There is no Claude API client in this repo for production PWG translation. Claude work runs
  through the Max Workflow surface, so the local scripts must make interruptions resumable
  instead of trying to hide network loss.
- The generated optimized harness retries each card once. A still-null card is recorded by
  `audit_window.py` and lands in `requeue.keys.txt`; rerun only those cards with
  `requeue_from_audit.py`.
- The stale-provenance check is mandatory after any interrupted run. It prevents old
  `wf_output.json` files from being audited against newly regenerated rootmaps or inputs.
- DeepSeek corpus-lexicon API calls are append-only/resumable in `build_corpus_lexicon.py`.
  Use `DEEPSEEK_RETRIES`, `DEEPSEEK_CONNECT_TIMEOUT`, `DEEPSEEK_READ_TIMEOUT`, and
  `DEEPSEEK_BACKOFF_BASE` to tune retry behavior; failed API batches are logged locally and
  can be retried later with `--retry-failed`.

If `requeue.keys.txt` is non-empty, generate the rerun harness directly from it:

```powershell
python src\pilot\requeue_from_audit.py sTA
```

Run the regenerated `run_pilot_wf.opt.js`, save its JSON as the next `wf_output.json`, and rerun
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

## Done criterion

The frequency queue milestone is done when:

- every manifest entry in the target frequency window has a merged card or a
  glued nested article;
- zero `*.merged.REJECTED.md` files remain for that window;
- rootmap-backed giant roots have matching `*.NESTED.md` outputs;
- the cost/quota table has enough windows to estimate the run duration.
