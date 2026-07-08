# SkillOpt B-arm held-out benchmark (H388)

_Created: 08-07-2026 · Last updated: 08-07-2026_

The frozen "exam" the SkillOpt PWG→RU pilot grades every skill-document edit
against. Design + rationale:
[`Uprava/docs/SKILLOPT_PIPELINE_MEMO.md`](https://github.com/gasyoun/Uprava/blob/main/docs/SKILLOPT_PIPELINE_MEMO.md)
§5; loop:
[`Uprava/tools/skillopt/`](https://github.com/gasyoun/Uprava/tree/main/tools/skillopt);
handoff:
[`H388`](https://github.com/gasyoun/Uprava/blob/main/handoffs/H388-Opus_Uprava_skillopt_skill_optimizer_pwg_pilot_08.07.26.md).

## Files

- [`build_heldout.py`](build_heldout.py) — reproducible builder. Embeds a **dated
  snapshot** of the runnable-root universe (a frozen exam must not drift with the
  live queue) and emits the fixture deterministically.
- [`heldout_v1.json`](heldout_v1.json) — the frozen fixture (schema
  `pwg.skillopt.heldout.v1`).

## The split (16 active roots, 2:1:7)

| Split | N | Sizes | Roots | Role (SkillOpt §3.1) |
|---|---|---|---|---|
| train | 3 | 1L·1M·1S | i, as, SaMs | supplies rollout experience |
| selection | 2 | 1M·1S | tap, muh | **GATES every edit** — a candidate skill is kept only if it beats the current one here |
| test | 11 | 2L·3M·6S | yuj, BU, kzip, ram, Baj, aS, nu, sev, tyaj, hu, pU | **report-only** — looked at once, at the end |

`sTA` (241 expected agents, defer-calibrate) is held aside as a **cost-deferred
control**, not scored — one monster must not dominate B-arm cost.

## Score `r` per root

The deterministic gate `r ∈ [0,1]` = `audit_window.py --json` clean fraction
(optionally composited with `ru_coverage.py`). **No LLM judge** — this is the
pilot's advantage: a reproducible, un-gameable signal.

## Honest constraints (surfaced, not padded)

1. **N is 16, not 25.** Only 17 roots were runnable (had rootmaps) on 08-07-2026;
   684 remain rootmap-less. A larger exam is possible only after **generating more
   rootmaps first** — a prerequisite task, tracked separately, not conjured here.
2. **Unit = root (coarse).** Card-level scoring (denser, per-card `r`) is a later
   refinement once the loop proves out at root granularity.
3. **Stratified, documented sampling** by size band (small <30 KB · medium
   30–80 KB · large >80 KB) so no split is size-skewed. No silent truncation.
4. **Cost.** Scoring a root means a real Sonnet-5 generation of its cards. The
   3 train + 2 sel roots (~5) are the per-epoch cost; the 11 test roots are
   generated once for the final report. Run under `perf_preflight.py
   --refuse-over-cost`.

## Regenerate

```bash
python build_heldout.py     # deterministic; overwrites heldout_v1.json
```

_Dr. Mārcis Gasūns_
