# Maturity audit — SanskritLexicography data estate (H6397)

_Created: 11-10-2026 (probe window 2026-10-11T14:49–14:57Z) · Auditor: OxAlpha (opencode/z-ai/glm-5.3-flash) · Handoff: [H6397](https://github.com/gasyoun/Uprava/blob/main/handoffs/H6397-OxAlpha_SanskritLexicography_maturity-data-estate_10.10.26.md)_

**Scope:** report-only maturity audit of THIS repo's data estate per the /maturity-audit discipline. The audit repairs nothing: every mutation a probe incidentally produced was `git restore`d before commit; defects found are recorded and minted as follow-up handoffs, never fixed in place here.

**Method (machine metrics only):** every number below carries the exact source command that produced it and a UTC timestamp. No memory-derived numbers. Probes ran in worktree `SanskritLexicography-h6397-drain` at `cdbc49aad` = `origin/master` tip (`git rev-parse HEAD` = `cdbc49aadabeb6e16d037ef23f66feceb46e0c06`, 2026-10-11T14:47Z).

## The five axes and their scoring rules (locked before scoring)

| # | Axis | 5 = | 3 = | 1 = |
|---|------|-----|-----|-----|
| A1 | **Data-layer integrity** (gold sets, keys, schema/BOM drift — the H6384 rekey defect class) | every gold key unique under a *declared* contract; zero parse defects; zero drift between committed artifacts and fresh regen | one undeclared key-uniqueness class or one committed-vs-regen drift row | silent corruption found in a promoted artifact |
| A2 | **Pipeline reproducibility** (can documented exports regen from source with one command) | every documented regen is one command, offline-safe, from a fresh clone, read-only by default | documented regens run but need local-only assets or silently mutate tracked data | no documented regen runs |
| A3 | **Test and gate coverage on data transforms** | offline suite green AND main CI green AND ≥50% of transform modules test-referenced | suite green or CI green, but not both; coverage thin | no automated gate on data transforms |
| A4 | **Docs truth for entry-format contracts** | 100% of sampled documented claims reproduce with the cited source command | ≥1 material claim fails to reproduce | documented claims systematically false |
| A4→A5 | **Conveyor health** (merge latency + rework rate from git history) | median merge < 1 day, rework (review-returned) < 10%, gates green at merge time | fast/reviewed conveyor but gates red at merge time | chronic rework or blocked conveyor |

Headline = mean of the five axis scores. Top-3 levers chosen by (defect severity × how many axes they unblock).

## Scores

_Filled in the second commit of this PR (same file, below the frame) — frame locked first per H6397 acceptance._
