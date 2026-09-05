_Created: 24-08-2026 · Last updated: 05-09-2026_

# Wave-2 regeneration reconciliation vs the lost wave-2 receipt

_Created: 24-08-2026 · Session: H3299 execution (opencode/x-preview-f-free, MG-approved tier override)_

## Counts

| metric | wave2_b receipt (H2727, 14-08) | regen h3299 (24-08) | delta |
|---|---|---|---|
| queue_keys | 5000 | 5000 | 0 |
| extracted_fragments | 197 916 | 197 925 | +9 |
| promoted | 162 107 | 162 120 | +13 |
| quarantine | 35 809 | 35 805 | −4 |
| silent_drops | 0 | 0 | 0 |
| fill.deterministic | 158 807 | 158 819 | +12 |
| fill.drafted | 0 | 0 | 0 |
| fill.sense_merge | 420 | 428 | +8 |
| fill.source_reuse | 3 138 | 3 145 | +7 |
| fill.unfilled | 35 551 | 35 533 | −18 |
| ledger cost_usd | 0.0 | 0.0 | $0 |
| prompt_sha256 | 55ae9562… | 55ae9562… | same |

Bucket deltas sum to +9 = extracted delta; accounted delta +17 splits promoted/quarantine consistently (both runs reconcile internally).

## Attribution

1. **+12 deterministic = the H3299 placeholder fix itself.** Exactly 12 rows carry `generation.origin == 'placeholder'` ([placeholder_fills.jsonl](placeholder_fills.jsonl)): 10× «кто-л.» (`{%Jmd%}`), 1× «кого-л.» (`{%Jmdn%}`/`{%Jmds%}`), 1× «что-л.» (`{%Etwas%}`). These previously stayed unfilled/quarantined.
2. **All other movement is tracked-pipeline drift, not input drift.** Proven unchanged inputs: TM publication last modified in git 06-08 (`5869f25ee`, single commit touching the file) and upstream `csl-orig/v02/pwg/pwg.txt` last modified 27-06 (`88229223`) — both predate the 14-08 wave and are byte-identical today. The only pipeline-code change since the wave is `d8ca453ab` (H2876, PR #1754, 16-08): `pwg_tm_fragmentize.py` dropped its private token tables for the shared sanskrit-util inventories (+ H2684 repair extras), which reclassifies some spans between formula/gloss/sense classes → the residual +9/+8/+7/−18 movements.
3. **Zero poisoned rows regenerated:** no fragment with a pure `{%Jmd%}`/`{%Etwas%}`/`{%Jmdm%}`/`{%Jmdn%}`/`{%Jmds%}` source carries a verb-phrase target anywhere in the new pool (scan: 0 hits).

## Where the data lives

The full promoted/quarantine dumps stay out of git (the loss class that ate `wave2_b/`); this directory carries the tracked evidence: sample, blind packet, adjudication, quality report, this reconciliation, and the enumerated placeholder fills. The dumps are deterministically regenerable (`drafted=0`, zero model calls) from the tracked queue+manifest.

_Dr. Mārcis Gasūns_
