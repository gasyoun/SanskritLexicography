# COLOGNE_YEARLY_ENTRY_CENSUS_2026-10-22.meta.md — metadoc for the H7223 census report

_Created: 22-10-2026 · Last updated: 22-10-2026_

This is a **metadoc** — a document *about* a document. Its subject is
[COLOGNE_YEARLY_ENTRY_CENSUS_2026-10-22.md](COLOGNE_YEARLY_ENTRY_CENSUS_2026-10-22.md).
It does not repeat the report's numbers; it records everything around it.

## Subject

- **Document:** [COLOGNE_YEARLY_ENTRY_CENSUS_2026-10-22.md](COLOGNE_YEARLY_ENTRY_CENSUS_2026-10-22.md)
- **Purpose:** per-year census of entry-level edits in Cologne `csl-orig` (all dictionaries, core ones
  detailed), plus a live freshness check of the two derived sites `michaelmeyer.fr` and
  `sanskritdictionary.com`.
- **Audience:** sessions touching csl-orig corrections, derived-site consumers, census/maturity audits
  that need a correction-volume baseline, and anyone re-measuring the derived sites.
- **Format / contract:** method + per-year and per-dictionary tables + issue attribution + derived-site
  verdicts + limits + reproduction commands. Every table is generated from the committed
  `reports/cologne_entry_census.tsv.gz`, not hand-tallied.

## Provenance

- **Created:** 22-10-2026 (handoff H7223, GLM 5.3 Flash `account:zai-individual-coding-plan/GLM-5.3-Flash`, ZCode).
- **Data pin:** `csl-orig` HEAD `55e8addbd96e8d9001b8789026b026763f4049c1` (26-09-2026), read-only.
- **Generator:** `tools/cologne_entry_census.py` (stdlib only; `--selftest`, `--check`, gzip output).
- **Sampler:** `tools/cologne_derived_sample.py` (stdlib only; `--sd-results` merge path for the CF half).
- **Canary:** `--check` re-ran the full pass twice; the shipped `reports/cologne_entry_census.tsv.gz`
  matched byte-for-byte (4,439,695 rows).

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Recover the 5.88% unattributed added lines | `-U6` context misses the `<L>` header on long records; a record-boundary parser (or `-U20`) would attribute them, raising coverage and shrinking the residual line | open |
| 2 | Complete the sanskritdictionary.com half | CF managed challenge blocks every non-interactive path tried (9 attempts, receipts in `reports/cologne_derived_receipts/probe.json`); needs one browser-session fetch merged via `--sd-results` | open — blocked site-side |
| 3 | Extend the derived-site check from additions to gloss corrections | Present method is robust but tests new headwords only; a gloss-diff measure would catch sites that add entries but serve stale definitions | open (method design) |
| 4 | Add a small committed aggregate (`year × dict × kind`) | The full TSV is 27.6 MB gzipped; a KB-sized aggregate would let downstream docs cite numbers without the blob | open |
| 5 | Wire `--check` into a scheduled canary | Determinism is proven only when someone runs it; a monthly clone-pinned run would catch silent regressions of the parser | open (needs a runner with the clone) |

## Known limitations / caveats

- The report's **correctness note** is load-bearing: the first dataset was deterministic but wrong (the
  literal `SHA` format marker was parsed as the commit hash, collapsing per-commit dedupe). The re-derive
  changed the row count from 1.51M to 4.44M with the same 1,508,914 distinct records. Cite the 4.44M
  figure, never the earlier one.
- The plain TSV (364.5 MB) is deliberately **not** committed — it exceeds GitHub's per-file cap. The gzip
  is the artifact; regenerate the plain file with the committed tool.
- `dc_year` is the DC editorial date from the commit subject, not `%ad`; both are in the TSV
  (`dc_year`, `commit_date`) and they disagree by design.
- The derived-site verdict for michaelmeyer.fr is a **freshness** result, not a staleness one; the SD
  verdict is `BLOCKED-CF`, not "stale".
