# PWG → RU translation logic review (02-10-2026)

_Created: 02-10-2026 · Last updated: 02-10-2026_

End-to-end logic review of the PWG→Russian pipeline: **mask → anchor → restore →
gates → promote** (`src/` core), the **coordinator / lane / kernel** orchestration
(`src/pilot/`, `src/pwg_pipeline/`), and the **budget/telemetry** layer. Method:
three parallel scoped reviews (core path; orchestration; gates & promotion),
then every reported finding re-verified in source at line level in this session —
`CONFIRMED` below means the code was read and the mechanism traced; nothing is
reported on agent assertion alone. Prior audits (2026-07-02 → 2026-08-13) were
read first; their open items are listed separately and **not** re-reported as new.

Reviewers: 3× scoped passes + aggregation and line verification, all
GLM-5.3 (`account:zai-individual-coding-plan`, ZCode). Elapsed ≈ 50 min
(review + verification + landing).

## Verdict

The **core translation path is sound and heavily audited**: `pwg_mask` →
`{Tn}` skeletons → prompt → anchor repair (`german_anchor`/`target_anchor`) →
stage-2 mechanical gates → fail-closed promotion (manifest-v2 binding, hashes,
denylist, journal, exactly-once) is contract-tested (`window_selftest.py`,
10k lines) and its known weak spots are already ledgered. **New findings
concentrate in three places**: the older NWS-side masking helper
([compile_translatable.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/compile_translatable.py)),
the **weekly budget accumulation** in the scheduler (money-guard integrity, not
translation output), and small liveness/annotation drifts. No 🔴 found; two 🟠.

## New findings (verified this pass)

| # | Sev | Location | Defect | Status |
|---|-----|----------|--------|--------|
| L1 | 🟠 | [compile_translatable.py:126-127](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/compile_translatable.py) | Owner-cite strip `re.sub(escape(owner)+r'.*$', '', g)` truncates at the **first** occurrence of the owner surname anywhere in the gloss, not the trailing cite — a scholar named mid-gloss destroys everything after it. Also no `re.S`/`re.M`: on a multi-line gloss `.*$` cannot reach end-of-string, so the owner cite is **not stripped at all**. Either way text is silently lost from (or leaked into) the translation input. NWS gloss layer only. | CONFIRMED (traced) |
| L2 | 🟠 | [nonstop_scheduler.py:228-237](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nonstop_scheduler.py) | Tick cost = sum of `observed_cost_usd` from `checkpoint.calls.json`; `except (OSError, ValueError): pass` → a missing/corrupt ledger (e.g. after a crash) yields `cost=0.0` for a **paid** window. The row-level `cost_evaluable` flag ([usage_accounting.py:194-200](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/usage_accounting.py), `observed_cost_usd: 0 if cash is None`) exists precisely for this, and the weekly accumulator ignores it → weekly USD ceiling silently under-counts. Run-level `--cost-ceiling` is stop-closed on unevaluable (AGENTS.md, 25-07) — the **weekly** layer is not. | CONFIRMED |
| L3 | 🟡 | [coordinator.py:335-344](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py) | `lease_expired` returns False for anything not `claimed` — a lease stuck `running` by a crashed machine never expires and permanently holds one of the 3 runtime slots until a human `release-run --confirm-dead`. Deliberate (auto-expiring a live run double-writes), but there is no running-TTL/heartbeat; ops-runbook mitigation only. | CONFIRMED (design tradeoff) |
| L4 | 🟡 | [kernel.py:95-118, 190](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/kernel.py) | Timeout abandons the daemon thread (documented: ledger sees `timeout` terminal) — the abandoned call can still complete and **bill at the provider**, invisible to `observed_cost_usd`. And `estimated_input_tokens: int = 1000` default projects pre-spend ceilings from a 1k-token guess while real windows are ≥5 KB. | CONFIRMED (docstring acknowledges) |
| L5 | 🟡 | [pwg_mask.py:338-339 vs 293-294](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py) | Production `mask()` classifies `{%…%}` with 100/80-char context; sidecar `gloss_lang_spans()` uses symmetric `context_window=100`. Same span can classify differently per path → sidecar annotations can disagree with what was actually masked/translated. | CONFIRMED |
| L6 | 🟡 | [promote_final_cards.py:1416-1437](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) | Defect-key guard fails **open** when no list is discoverable (`skipped_no_list`, documented tradeoff), and `--force` clears a real intersection with one line of stdout. Given the H255 footgun history this is the softest link in an otherwise fail-closed promoter. | CONFIRMED (documented tradeoff) |
| L7 | 🟡 | [compile_translatable.py:99-101, 131-132](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/compile_translatable.py) | Hygiene: `INLINE_SA` lacks `re.S` (multi-line `<is>`/`{#…#}` spans unmasked — `pwg_mask.PAIRED_RE` has it); `LS` regex defined, never used; `for m in GRAM.findall(...): pass` dead loop; `pwg_mask --selftest` prints hardcoded `20` ([pwg_mask.py:573](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py)) regardless of checks run. | CONFIRMED |
| L8 | 🟡 | [synth_dispatch.py:186](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_dispatch.py) | `time.sleep(recheck_s)` inside `land_watcher_safe` blocks the dispatcher loop (called from `_maybe_land`) — kill-guard polling stalls for every running worker during each landing retry. | CONFIRMED |
| L9 | 🟡 | [cloud_window.py:115-120](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cloud_window.py) | `wf_output.<window>.json` written with plain `open('w')`, not the tmp+`os.replace` pattern used elsewhere — partial-write hazard on the artifact promotion consumes. | CONFIRMED |
| L10 | 🟢 | low batch | [slp1_norm.py:32-43](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/slp1_norm.py) space-stripping can collide distinct join keys (only 4 asserts pin it); [iast_to_cyrillic.py:50-86](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/iast_to_cyrillic.py) has no Sanskrit-ness guard (pure-ASCII Latin would pseudo-cyrillize if ever fed non-IAST); [store_write.py:127-132](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_write.py) `except BaseException` reduces refresh failure to one stderr line (documented best-effort). | CONFIRMED |

## Prior art — still open, do not re-report

From [ARCHITECTURE_AUDIT_2026-07-02](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ARCHITECTURE_AUDIT_2026-07-02.md), [PIPELINE_HARDENING_AUDIT_2026-07-25](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HARDENING_AUDIT_2026-07-25.md), [PIPELINE_AUDIT_PWG_RU_H2025_01-08-2026](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_AUDIT_PWG_RU_H2025_01-08-2026.md), [PWG_RU_DRAIN_BOTTLENECK_CENSUS_POST_AUTHORIZATION_13-08-2026](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_RU_DRAIN_BOTTLENECK_CENSUS_POST_AUTHORIZATION_13-08-2026.md), [CODE_REVIEW_2026-07-04](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CODE_REVIEW_2026-07-04.md):

- `prompt_rule_audit.has_text_signal()` false-positive churn (Mode 6, open since 06-29).
- Hardening-audit P0 posture: Windows kill-tree not kernel-backed; promotion as one transaction (journal landed H1339; `promotion_receipt.py` not to be wired unchanged).
- `stage2_pregate.py` hardcoded store path (H2025 S2-8) and `promote_lock` swallowed restore/release (H2025 S3-17) — both still visible in code.
- `--min-cards` skips count-integrity; `degenerate_passthrough` German-as-RU; `supersedes` string-iteration (latent) — CODE_REVIEW backlog.
- HARD_TIMEOUT 300 s < one real card (511 s); metered transport absent; G5–G10 block print only (D2 machine-preview default — decided, not a defect).
- H2025: ceilings default None → evaluability gate passes unset; scheduler swallow → double paid window (same family as L2, run-level).

## Test-coverage gaps (zero tests anywhere)

`compile_translatable.py` (`units`, `mask_nws_gloss`, `detect` — where L1/L7
live), `synth_score.py` (all), `root_glue_translated.glue`, `slp1_norm`
(module asserts only), `iast_to_cyrillic` (`transliterate`, `name_for_ru_prose`).

## Ranked recommendations

1. **L1**: anchor the owner strip to the string tail + `re.S`, pin with tests, and run a one-off corpus scan of existing NWS prose/keep outputs for early-truncation scars (silent loss feeding the LLM).
2. **L2**: a tick whose ledger is missing/unparsable, or any row with `cost_evaluable: False`, must mark the tick unevaluable and stop-closed (skip, alarm), never contribute 0.0 — mirrors the run-level rule the repo already mandates.
3. **L3**: running-lease TTL+heartbeat, or at minimum a RUNBOOK line (slot leak → `release-run --confirm-dead`).
4. **L5**: one shared classifier-window constant + a parity selftest entry.
5. **L4**: derive `estimated_input_tokens` from the manifest payload; log provider-billed-after-timeout as a known ledger undercount.
6. **L7–L9**: delete dead code, fix the hardcoded selftest count, atomic write in `cloud_window`, non-blocking watcher poll.
7. Close the five zero-coverage modules above (highest value: `mask_nws_gloss`).

_Гасунс_
