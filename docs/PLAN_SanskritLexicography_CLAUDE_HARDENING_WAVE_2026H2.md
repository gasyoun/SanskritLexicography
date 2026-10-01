# PLAN — Claude Code hardening wave: fill the gaps, harden the code, revise the logic (pwg_ru), 2026H2

_Created: 30-08-2026 · Last updated: 30-08-2026_

**Goal.** Repair the already-KNOWN defect backlog of the pwg_ru pipeline in eight bounded, separately-minted Claude Code handoffs: turn master's own integrity gate green, make every gate's PASS carry evidence, land the five unstarted H1940/H1811 hardening items plus the sibling-path migration, measure provenance instead of asserting it, revise the two wrong-answer logic defects (homonym index, relation labels) with ledgered store rewrites, rejoin the fragmentizer's orphaned glosses, and fix the top measured performance hotspots. Discovery of UNKNOWN defects stays with the queued OxAlpha review (H3547) — the lanes are complementary. Authored by the `/ask` interview of 30-08-2026 (Fable 5 `claude-fable-5`): 16 forks, 16 separately ruled by MG in live chat, 0 defaults-locked.

## Layers

1. [Roadmap](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ROADMAP_SanskritLexicography_CLAUDE_HARDENING_WAVE_2026H2.md) — the eight wave units W0–W7, ordering, non-goals
2. [Architecture](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_CLAUDE_HARDENING_WAVE.md) — gate-evidence contract, H3591 store-mutation pattern, build-vs-reuse verdicts
3. [Implementation](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_SanskritLexicography_CLAUDE_HARDENING_WAVE.md) — file-level step order per unit
4. [Verification](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_SanskritLexicography_CLAUDE_HARDENING_WAVE.md) — acceptance per unit, RED-pin bar, risks & spikes

## Decisions taken

| # | Fork | Ruling | Rationale |
|---|---|---|---|
| 1 | Scope | pwg_ru pipeline first ([RussianTranslation/src](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src) + `src/pilot`); other subtrees only when a defect chain leads there | All open `[integrity]` issues, the H1940 remainder, and the worst health scores live there |
| 2 | vs H3547 OxAlpha review | Complementary — H3547 stays queued as the discovery lane; this wave repairs the KNOWN backlog | Known-vs-unknown split preserves the independent-reviewer design |
| 3 | Backlog sources | All four: `[integrity]` issues · H1940 remainder (H3, H4, H5, H7, H10) · logic revisions (#1801, #1736) · GAPS §18 + Repowise perf | Ruled in interview round 1 |
| 4 | Wave size | 6–8 handoffs → 8 units minted | Full source coverage without registry flooding |
| 5 | Gate contract (#1803) | Evidence-carrying PASS: measured evidence per gate, zero-work PASS becomes hard FAIL, one shared helper, all nine gates retrofitted | A PASS indistinguishable from "nothing checked" is the root defect |
| 6 | #1801 authority | Fix code + census; store rewrite WITH ledger (H3591 pattern) + mirror refresh in the same handoff, no human gate | Mapping is evidence-decidable; standing ledgered-mutation pattern |
| 7 | #1804 shape | Two handoffs: mechanical sibling_root migration separate from the provenance-measurement census | Different skills, different risk |
| 8 | GAPS §18 | Census + rejoin fix in `pwg_tm_fragmentize.py`; re-fragmenting existing rows out of scope | Repair at source; fragment identity untouched |
| 9 | Tiers | Mixed by risk: Opus 5 for logic revisions + gate retrofit (+ perf, judged by coordinator's untested 1.0/10 health — default, not separately ruled); Sonnet 5 for mechanical units | Effort matched to wrong-answer risk |
| 10 | Test bar | RED-on-pre-fix pin for every behavioral fix; store rewrites additionally proven via `audit_store_gates.py` before/after | Repo convention; green-only tests are the #1803 disease |
| 11 | Perf lane | Top-10 measured hotspots; static findings are the map, not the mission; before/after timing per fix | 939 static findings ≠ 939 real problems |
| 12 | Extra clusters | #1864 gate-RED repair IN, first in execution order; #1680 timeout forensics OUT | A RED master gate hollows "merge on green"; #1680 stays an issue |
| 13 | On ambiguity | Default-and-log: conservative reading, divergence logged in the PR body, keep going | The wave never stalls; wrong defaults reversible via ledger/PR |
| 14 | Extra stop conditions | Unledgered store delta → halt, don't commit. Census ≥2× off the issue's claim → halt the rewrite half, deliver census-only | Store is the crown jewel; a broken premise voids the rewrite authorization |
| 15 | Fence | Paid/live lanes · mw_ru + non-pwg_ru data · LANG_PARITY verdicts (re-affirm flow only). Prompts not additionally fenced; touching them must be logged | Ruled in interview round 4 |
| 16 | Execution | W0 first alone, then W1; W2–W7 parallel-safe, one worktree each, W7 last; no two units on the same module family concurrently | Gate meaning before gate consumers; collision avoidance |

## Autonomy contract

The executor of each handoff operates unattended under handoff-scoped autonomy (commit → PR → merge on green, no confirmation asks).

- **On ambiguity:** pick the plan's marked default or the conservative reading, log the divergence in the PR body (FINDINGS if reusable), continue. Never stall on a fork this plan already rules.
- **Stop conditions (halt and report):** any store diff without its ledger row; a census diverging ≥2× from the source issue's claimed population (deliver census-only); secrets/PII exposure; anything requiring a paid call.
- **Commit authority:** per-unit worktree off `origin/master`, PR, merge on green CI. No direct pushes to master; no force-push; rebase on master tip immediately before merge and re-run `lang_parity_check`.
- **The fence (never touch):** live generation / paid windows / router.cheap / Max profiles; mw_ru cards; frozen `HeadwordLists/then-2014/` exports; `literature/`; the ReverseDictionary dataset; LANG_PARITY verdicts outside the documented re-affirm flow; csl-orig.

## Open @DECIDE

None.

## Execution handoffs

Minted 30-08-2026 in one atomic batch (verified on `origin/main`, commit `d82508ce6`). Cost classes: 🟡2 medium ≈ 15 min–2 h agent runtime; 🔴3 hard ≈ 2 h+.

| Unit | Handoff | Tier · effort |
|---|---|---|
| W0 | [H3747 — epistemic gate RED repair](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3747-Sonnet_SanskritLexicography_epistemic-gate-red-repair_30.08.26.md) | Sonnet 5 · 🟡2 |
| W1 | [H3748 — gate-evidence contract](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3748-Opus_SanskritLexicography_gate-evidence-contract_30.08.26.md) | Opus 5 · 🔴3 |
| W2 | [H3749 — mechanical hardening batch](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3749-Sonnet_SanskritLexicography_pwg-mechanical-hardening-batch_30.08.26.md) | Sonnet 5 · 🔴3 |
| W3 | [H3750 — provenance census + backfill design](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3750-Opus_SanskritLexicography_pwg-provenance-census_30.08.26.md) | Opus 5 · 🟡2 |
| W4 | [H3751 — homonym index remap](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3751-Opus_SanskritLexicography_pwg-homonym-index-remap_30.08.26.md) | Opus 5 · 🔴3 |
| W5 | [H3752 — relation-label revision](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3752-Opus_SanskritLexicography_pwg-relation-label-revision_30.08.26.md) | Opus 5 · 🔴3 |
| W6 | [H3753 — fragmentizer rejoin](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3753-Sonnet_SanskritLexicography_pwg-fragmentizer-rejoin_30.08.26.md) | Sonnet 5 · 🟡2 |
| W7 | [H3754 — perf top-10 measured](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3754-Opus_SanskritLexicography_pwg-perf-top10-measured_30.08.26.md) | Opus 5 · 🟡2 |

_Dr. Mārcis Gasūns_

## Autonomy gate — 30-08-2026

| Check | Verdict |
|---|---|
| all mechanical checks | PASS |

Mechanical verdict: **PASS** (exit 0). Human halves — no-rebuild-what-exists, contract coverage of plausible ambiguities — attested by the authoring session, not parsed here.

_Dr. Mārcis Gasūns_
