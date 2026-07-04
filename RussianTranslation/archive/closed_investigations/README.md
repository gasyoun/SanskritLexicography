# Closed investigations

Archived 04-07-2026 during a documentation pass. These are self-contained,
dated, one-off investigation notes from 2026-06-30/07-01 — each answers a
specific question that came up mid-pipeline-build and was resolved. None of
them were linked from any other doc at archive time (verified by a
repo-wide reference scan); their conclusions are already folded into the
living docs (`RUN_FREQ_MAX.md`, `.ai_state.md`) so nothing is lost by moving
them out of the top level. Kept for audit history, not deleted.

| File | Question it answers |
|---|---|
| [BRIDGE_FOLLOWUPS_2026-06-30.md](BRIDGE_FOLLOWUPS_2026-06-30.md) | Are the 2 print-bridge follow-ups (after PR #18) quick fixes? — no, neither is. |
| [HOMOGRAPH_KEYING_FIX_2026-06-30.md](HOMOGRAPH_KEYING_FIX_2026-06-30.md) | Is the bridge-preview homograph multiplication bug fixed? — yes, verified. |
| [PWG_EN_PILOT_2026-06-30.md](PWG_EN_PILOT_2026-06-30.md) | What does a DE→RU+EN tri-lingual aligned sample look like? (Bid pilot rows) |
| [PWG_TRANSLATION_ECONOMICS.md](PWG_TRANSLATION_ECONOMICS.md) | What's the measured cost/timeline for a full PWG→EN run on Sonnet 5? |
| [SIDH_DUPE_INVESTIGATION.md](SIDH_DUPE_INVESTIGATION.md) | Did `siD` fail sense_dupes because of over-production? — no, faithful to source. |
| [TOKEN_LEVER_FINDING_2026-06-30.md](TOKEN_LEVER_FINDING_2026-06-30.md) | Is "portrait-slim" a real token-cost lever? — no; batch budget is the real lever. |

For the full chronological narrative these fit into, see
[`../../PIPELINE_HISTORY.md`](../../PIPELINE_HISTORY.md). For current
production process, see [`../../src/pilot/RUN_FREQ_MAX.md`](../../src/pilot/RUN_FREQ_MAX.md).
