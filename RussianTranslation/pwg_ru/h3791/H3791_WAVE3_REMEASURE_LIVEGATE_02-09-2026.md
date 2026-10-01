# H3791 — Wave 3 requeue: fresh measurement + live-gate GO, requeue step not executed

_Created: 02-09-2026 · Last updated: 02-09-2026_

**Model:** Sonnet 5 (`claude-sonnet-5`)

## Ruling chain (re-derived, not re-guessed)

1. MG **RULED 29-07-2026** (weekly `@DECIDE` sheet): sample first — re-translate a bounded
   ~200-row slice of the `〉`-quarantine, measure how many are genuinely bad, then decide.
   Full paid re-translation of the whole quarantine is **not authorised** until that sample
   reports.
2. The 200-row sample ran **01-08-2026** (`src/pilot/sample_glyph_quarantine.py`, seed
   `20260801`, purely mechanical — **no re-translate**): 200/200 rows are `segmentation_flag`
   (sense-count changed under the corrected `〉` splitter), not a measured RU-quality label.
   Report: [H_GLYPH_QUARANTINE_SAMPLE_REPORT_20260801.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H_GLYPH_QUARANTINE_SAMPLE_REPORT_20260801.md).
   **Explicit conclusion:** "Mass re-translate is not authorised by this sample alone. Next
   step if RU quality is in doubt: a human/paid read of a smaller nested sample of the
   `segmentation_flag` class (e.g. 30 cards), not a full paid re-run of 10k rows."
3. **That 30-card human/paid read has not happened.** No report, no worklist, no coordinator
   lease for it exists anywhere in the repo as of this session.

## What this session did (H3791 takeover, claim released+reclaimed 02-09-2026)

1. **Re-measured the contaminated set mechanically, fresh, read-only** (`src/audit_sense_glyph.py`,
   no `--limit`): **10,902 of 11,519 RU-store rows (94.64%, 95% CI 94.22–95.04%)** are flagged —
   up slightly from the 20-07-2026 baseline (10,881/11,603) because the RU-store population
   itself moved between those dates (H2996's unrelated 28-08 key1-repair quarantined 159 rows
   and shrank the store 11,621→11,462; today's rescan reads 11,519, i.e. some of those returned
   via other work since). Store sha256 confirmed **unchanged** before/after the audit pass.
   Regenerated `reports/pwg_sense_glyph_audit.json` and `reports/pwg_ru_glyph_quarantine.jsonl`
   (10,902 rows) committed this pass.
2. **Ran a fresh `/pwg-live-gate` on c1** (the sole live lane since c4's 19-08 retirement):
   - Step 1 health: **PASS** — measured wall 23,446 ms (< 80,000 ceiling), API 11,955 ms
     (< 45,000 ceiling), zero connection errors, `production_v3` policy.
   - Step 2 canary (`dq_canary_puregloss~~h0_zz_pw`, ONE paid call, rc 0, 67.5 s): **GO** —
     3/3 senses, zero SAN-LOSS/TNMASK/unmapped/schema failures.
   - Verdict: **LIVE_GO**. Receipt: `D:\ClaudeTools\profiles\claude1\.pwg_ru_evidence\c1\h3791\canary_receipt.json`
     (valid ≤6h from `judged_at_epoch` per the skill's `DEFAULT_MAX_AGE_SECONDS`).
3. **Did NOT run the 30-card requeue-and-audit step.** Reason: no existing tool fits it.
   `src/pilot/requeue_from_audit.py` and `coordinator.py prepare-requeue` are both built
   around the transient/defect-retry lease flow (a job already claimed and dispatched once),
   not an ad hoc "translate these N pre-selected quarantine keys, write the result to a
   report only, never promote" quality read. `bounded_staged_run.py` needs a coordinator
   lease/plan as its unit of work — there is no first-class notion of a bounded, non-promoting
   sample translate in this pipeline as it stands. Building one from scratch against the
   lease/promote machinery, live, under a fresh 6h receipt clock and with host RAM thin
   (898 MB free at session start, recovered to ~2.1–2.3 GB during the gate — well above the
   documented 1.7 GB crash floor but still shared with several other concurrent sessions on
   this box), was judged too risky to improvise rather than hand off.

## Host RAM note (Danger Facts precedent)

Free physical RAM measured **898 MB** at claim-takeover time (multiple concurrent `claude`/
`OpenCode` sessions on this box — H3775/H3776/H3780/H3844/H3845/H3883 etc. all held live
claims at the time). This is *below* the documented crash floor
(`danger_paid_window_dies_on_host_ram` — a window died at ~1.7 GB free). No paid call was
attempted until RAM recovered to **2.1–2.3 GB free**, confirmed again immediately before the
live-gate probe and canary (both events logged `host_avail_phys_mb` 1859–2104). Neither call
crashed. Still tight — a next session spending here should re-check free RAM before its own
first paid call, not trust this reading.

## What is owed next (human or a future session)

1. **Build (or get pointed to) a "translate N pre-selected keys, report only, never promote"
   entrypoint** for exactly this quarantine-sample use case — either a small new script
   scoped tightly to read-report-only, or a ruling that an existing lane (nominal window?
   defect-repair with `--no-residual`?) is actually the right vehicle and how to bound it to
   30 keys without touching unrelated queue state.
2. Once that exists: draw the 30-card nested sample from the **fresh** 10,902-row quarantine
   (stratified the same way as the 01-08 200-row sample, or a sub-sample of that exact 200 for
   continuity), translate under `--max-calls` bound, and get a human/paid RU-quality read —
   **never write to the RU store** until that read reports (same as the 200-row precedent).
3. The `/pwg-live-gate` GO from this session is usable by whoever runs step 2, **only within
   6h of `judged_at_epoch` (2026-09-02T09:53:37Z)** — after that, a fresh gate is required.

_Dr. Mārcis Gasūns_
