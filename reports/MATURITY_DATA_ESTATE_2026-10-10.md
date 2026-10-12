# MATURITY_DATA_ESTATE — SanskritLexicography data estate (H6397)

_Created: 12-10-2026 (audit run 2026-10-12T06:21–06:40Z) · Last updated: 12-10-2026_

**Provenance:** H6397 · executor OxAlpha (opencode/z-ai/glm-5.3-flash) · worktree `SanskritLexicography-h6397-drain` off origin/master @ cdbc49aad · report-only: zero mutations (regen attempt artifacts discarded, never committed).
**Discipline:** /maturity-audit (C60) — the audit is an instrument, not a repair crew. Every metric below carries its **source command** and a **UTC timestamp**; no memory-derived numbers.

## Frame (locked before probing — threshold rules per score)

| # | Axis | What it measures | Score thresholds |
|---|---|---|---|
| 1 | Data-layer integrity | Gold-set key uniqueness, schema stability, BOM parity across export eras, upstream-provenance keys (H6384 rekey defect class) | 5 = unique keys + stable schema + provenance keys present; 4 = minor metadata drift only; 3 = one defect class present but bounded; ≤2 = duplicate keys or schema drift in gold sets |
| 2 | Pipeline reproducibility | Can the flagship export (`HeadwordLists/now-2026/`) be regenerated from source with ONE documented command | 5 = one command from clean clone, steady-state identical; 4 = one command with documented env override, no drift; 3 = works with override but count-drift/filename churn; 2 = silent failure mode present; ≤1 = cannot regenerate |
| 3 | Test & gate coverage on data transforms | Offline pin suite size + freshness, CI state on master, enforcement of the gate at merge | 5 = green + enforced + pins match documented claim; 3 = comprehensive pins but red on master; ≤2 = red on master AND merges continue unchecked |
| 4 | Docs truth for entry-format contracts | Verifiable current-state claims in CLAUDE.md / AGENTS.md (pin count, BOM states, filename grammar) | 5 = all sampled claims verify; 3 = minority stale; ≤1 = majority stale |
| 5 | Conveyor health | Merge latency, rework rate, merges-onto-red from git/CI history | 5 = median latency <24h AND rework <30% AND zero merges-on-red; 4 = one blemish; 3 = two blemishes; ≤2 = chronic rework or routine red merges |

<!-- METRICS-ANCHOR: verdict section appended below by H6397 execution pass -->
