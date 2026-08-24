# Wave-3 regeneration reconciliation vs the H3299 regen

_Created: 24-08-2026 · Session: H3434 execution (OxAlpha, opencode/x-preview-f-free)_

## Counts

| metric | h3299 regen (24-08) | regen h3434 (24-08) | delta |
|---|---|---|---|
| queue_keys | 5000 | 5000 | 0 |
| extracted_fragments | 197 925 | 197 925 | 0 |
| promoted | 162 120 | 162 043 | −77 |
| quarantine | 35 805 | 35 882 | +77 |
| silent_drops | 0 | 0 | 0 |
| fill.deterministic | 158 819 | 158 819 | 0 |
| fill.drafted | 0 | 0 | 0 ($0, ledger calls=0) |
| fill.sense_merge | 428 | 370 | −58 |
| fill.source_reuse | 3 145 | 3 081 | −64 |
| fill.unfilled | 35 533 | 35 655 | +122 |
| prompt_sha256 | 55ae9562… | 55ae9562… | same |

Accounting closes exactly: sense_merge −58 and source_reuse −64 = **−122** rows that can no
longer take a wave-1-carried fill for a now-denylisted source; unfilled +122. Of those,
77 had been promoted under the old policy (now quarantine), 45 were already quarantined
rows whose origin changed to unfilled.

## Attribution

1. **source_reuse −64 / sense_merge −58 = the denylist extension itself.** The 31 new
   `SHORT_GLOSS_DENYLIST` tokens (census-evidenced, [denylist_census.json](denylist_census.json))
   remove those sources from `build_source_lexicon`, from the `exact_reuse` index
   (`reuse_index_from_publication` — the previously unguarded path), and therefore from
   `gloss_map` feeding `sense_merge`.
2. **deterministic unchanged (158 819)** — placeholder/copy/formula paths untouched; the
   H3299 `{%Jmd%}`/`{%Etwas%}` fills still fire (denylisted sources skip only reuse paths
   and then land on the deterministic placeholder render).
3. **`<ab>v. a.</ab>` content delta:** 502 promoted rows changed `<ab>т. е.</ab>` →
   `<ab>особенно</ab>` inside otherwise-stable targets (promoted→promoted, invisible in
   the count columns). Rows still rendering «т. е.» for v. a.: **0**.
4. **Zero model calls:** cost_ledger calls=0, tokens=0, cost_usd=0.0; drafted=0.

## Where the data lives

The full promoted/quarantine dumps stay out of git (regenerable, `$0`) in the session
out-dir. This directory carries the tracked evidence: sample + meta (seed 3434), blind
packet, adjudication, quality report, census, verdict. The dumps are deterministically
regenerable from the tracked queue+manifest with the repaired policy.
