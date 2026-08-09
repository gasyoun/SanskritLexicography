# `safe_excl` arm — trivial-phase A/B vs `safe` (closing GAPS §7)

_Created: 06-08-2026 · Last updated: 06-08-2026_

**Handoff:** [H2310](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2310-Fable_SanskritLexicography_safe-excl-arm-trivial-ab-run_06.08.26.md) (**Fable 5**) — run the `safe_excl` A/B arm, close [Uprava GAPS §7](https://github.com/gasyoun/Uprava/blob/main/GAPS.md).
**Rig:** [h2189_profile_ab.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2189_profile_ab.py), which gains the `safe_excl` arm in this same change (the [H2189 report §6](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2189/PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md) had recorded the flag as untested residual — the docstring listed the arm but the `ARMS` dict deliberately omitted it).
**Model:** paid calls Sonnet 5 (`claude-sonnet-5`) per the manifest; harness run + report by Fable 5 (`claude-fable-5`).
**Command:** `python src/pilot/h2189_profile_ab.py --run --phase trivial --repeats 2 --arms safe,safe_excl --out pwg_ru/h2189/raw_safe_excl` — both arms re-run fresh and sequential the same minute, so the comparison is same-day attributable rather than read against the 03-08 committed `safe` numbers. Raw envelopes: [raw_safe_excl/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2189/raw_safe_excl).

## Result — the flag buys nothing material on top of `--safe-mode`

| arm | call | create | read | in | out | wall ms | api ms | usd (1h-write repricing) |
|---|---|---|---|---|---|---|---|---|
| safe | #1 (cold) | 4 667 | 28 882 | 2 | 4 | 15 786 | 6 846 | 0.0367 |
| safe | #2 (warm) | 0 | 33 549 | 2 | 4 | 13 783 | 5 426 | 0.0101 |
| safe_excl | #1 (cold) | 4 383 | 28 882 | 2 | 4 | 11 402 | 7 651 | 0.0350 |
| safe_excl | #2 (warm) | 0 | 33 265 | 2 | 4 | 14 670 | 2 813 | 0.0100 |

- **Prefix delta: −284 tokens** (create 4 383 vs 4 667 cold; read 33 265 vs 33 549 warm) — the size of the dynamic sections (cwd/env/memory-path/git status) the flag relocates out of the system prompt. That is ~0.8 % of the ~33.5k warm prefix; ≈ $0.0009/call cold, ≈ $0.0001/call warm.
- **Identical everything else:** input 2 / output 4 both arms both calls; both arms' warm calls re-read the full prefix with 0 creation (the v2.1.223 cross-call amortisation of [FINDINGS §326](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) holds under the flag).
- Wall/api times overlap within ordinary variance at n=2; no latency claim is made.

**Verdict: measured-and-resolved, no prize.** The flag's own `--help` scopes it to cross-*user* cache reuse; on this single-user subscription lane it relocates ~284 tokens and changes nothing that prices or paces the lane. `execution.cli_safe_mode` (default ON since [PR #1150](https://github.com/gasyoun/SanskritLexicography/pull/1150), H2251) stays the shipped configuration; `--exclude-dynamic-system-prompt-sections` is NOT added to the production argv. [Uprava GAPS §7](https://github.com/gasyoun/Uprava/blob/main/GAPS.md) graduates to a FINDINGS row citing this report.

**Honest limits.** n=2 per arm, trivial phase only — enough to price a prefix-size lever (a deterministic token count), not to detect a latency effect. No card-phase run: with the prefix delta at 0.8 % there is no mechanism left for a card-level effect worth $2–3 of card calls, per the [FINDINGS §330](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) rule that magnitudes from small n are quotable only when the quantity is deterministic (a token count is; a wall-clock is not).

**Total spend this measurement: $0.092** (4 calls, 1h-write repricing).

_Dr. Mārcis Gasūns_
