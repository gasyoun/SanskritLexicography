# Metadoc — PROMPT_CACHING_PWG_RU.md

_Created: 03-08-2026 · Last updated: 03-08-2026_

## Purpose

The **single playbook of record** for what a paid PWG→RU call costs and which
levers move that cost. It exists so that no session re-derives cache economics
from envelopes: measurements land in handoffs and FINDINGS, and this file is the
one place that *ranks* the levers, names the code that implements each, and says
which questions are settled versus still open.

Audience: an operator or executor about to spend tokens on the lane, and any
session picking up a cache/cost handoff. It is a **decision surface**, not a
tutorial — every claim in §1 is a measurement someone paid for.

## Provenance

- Consolidated 02-08-2026 by Grok 4.5 (`grok-4.5`) from measurements already
  committed across [H2152](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2152-Opus_RussianTranslation_c4-quota-call-shape-audit_02.08.26.md),
  H2158 and their reports — a consolidation, not a new experiment.
- Extended 02-08-2026 by [H2190](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2190-Opus_SanskritLexicography_pwg-cache-write-1h-pricing_02.08.26.md)
  (dual-rate 1 h cache-write pricing, standing truth #6).
- Extended 03-08-2026 by [H2189](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2189-Opus_SanskritLexicography_pwg-headless-minimal-profile_02.08.26.md)
  (Opus 5 1M, `claude-opus-5[1m]`): §3 rank 1 resolved — `--safe-mode` GO,
  a dedicated minimal `CLAUDE_CONFIG_DIR` rejected at −8.7 % against the flag's
  −88 % — plus the standing-truth-#1 contradiction flag.
- Org-level residue from the same runs lives in
  [Uprava FINDINGS](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) §284/§297,
  [CONTRADICTIONS §7](https://github.com/gasyoun/Uprava/blob/main/CONTRADICTIONS.md)
  and [GAPS §7–§8](https://github.com/gasyoun/Uprava/blob/main/GAPS.md).

## Ranked improvement backlog

1. **Resolve standing truth #1** — it currently carries a self-contradiction
   (H2189 measured amortisation in all five arms; v1.127.0 measured none). It is
   the premise under the entire rank-2 Messages-API case, so it should not stay
   flagged for long. Re-measurement: [H2250](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2250-Opus_SanskritLexicography_pwg-cli-cache-amortisation-remeasure_03.08.26.md).
2. **Close the `cli_safe_mode` default question** — the flag ships default OFF
   solely because one `tag`-vocabulary divergence is unattributed at n=1
   ([H2251](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2251-Opus_SanskritLexicography_pwg-safe-mode-canary-flip-default_03.08.26.md)).
   Until it flips, the lane pays ~2.5× per card by default.
3. **Add a "what is NOT a lever" section.** Rejected levers (lean TR, batching,
   the minimal profile dir) are recorded in different places at different depths;
   a reader currently learns them by reading three handoffs.
4. **State each truth's measured CLI version inline.** #1 was measured on
   v1.127.0 and contradicted two versions later — a truth about someone else's
   binary has a version, and without it a stale reading looks permanent.
5. **Price the last unmeasured flag** (`--exclude-dynamic-system-prompt-sections`,
   [GAPS §7](https://github.com/gasyoun/Uprava/blob/main/GAPS.md)) so §3 stops
   listing a lever nobody has costed.

## Limitations

- **Every number is a snapshot against a third-party binary.** The CLI is not
  ours; a version bump can invalidate a truth without touching this repo, which
  is exactly what §1 truth #1 is currently living through.
- Costs are list-rate reconstructions; a paid call that times out yields **no**
  evaluable cost and must never be read as `$0` (the fail-closed rule the lane's
  `call_reservation` already applies).
- It ranks levers for the **paid CLI lane only** — the offline/no-PWG lane and
  the Messages-API route have different economics and are out of scope.
- Not an operator runbook: window mechanics live in
  [`/pwg-drain`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-drain.md)
  and [`/pwg-live-gate`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md).

## Related docs

- Subject: [`PROMPT_CACHING_PWG_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PROMPT_CACHING_PWG_RU.md)
- [`pwg_ru/h2189/PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2189/PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md)
- [`src/pilot/headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) — where `bare_cli_cwd()` and `cli_safe_mode` live
- [`src/pilot/RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md)
- [Uprava DANGER_FACTS](https://github.com/gasyoun/Uprava/blob/main/DANGER_FACTS.md) § SanskritLexicography — the duplicate-`CLAUDE_CONFIG_DIR` concurrency trap this playbook's rejected lever would have created

## Revision history

| Date | Change |
|---|---|
| 03-08-2026 | Initial metadoc, written during the H2189 propagation sweep (Opus 5 1M, `claude-opus-5[1m]`). Subject state: six standing truths, rank 1 resolved, truth #1 flagged as contradicted. |

_Dr. Mārcis Gasūns_
