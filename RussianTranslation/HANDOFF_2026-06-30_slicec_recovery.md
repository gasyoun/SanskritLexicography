# Handoff — recover the full Slice-C translated output

> **UPDATE 2026-06-30 (recovery session, branch `recover/slicec-top3-pat-ga-vad`):**
> Two material corrections to the plan below, plus progress:
> - **DA needs NO re-run.** The full dhā output survives on disk in
>   [`wf_output_da_a.json`](wf_output_da_a.json) + [`wf_output_da_b.json`](wf_output_da_b.json)
>   (72+73=145 cards; the bridge globs `wf_output*.json` and promoted **138/145**). The
>   table's "DA 0/145 — biggest loss" is stale. Only ~7 DA cards are marginal.
> - **True remaining deficit ≈ 514 cards / 15 roots** (not 630/16), because DA drops out.
> - **`jan`/`han` salvaged** to stable names `wf_output.sc.jan_full.json` / `wf_output.sc.han.json`.
> - **The §Guardrail fix is already implemented** in [`save_and_audit.py`](save_and_audit.py)
>   (overwrite-refusal + `--merge`). Do not re-add it.
> - **DONE this session (Max re-run, ≤3-wide): `pat` (73), `gA` (65), `vad` (47).** Saved as
>   full per-root files; bridge coverage 1431→1603 non-null cards / 7218 sense rows; pat/gA/vad
>   off the thin-warning list. Residual requeues left for an optional quality pass:
>   transient nulls pat 5 / gA 2; defect (semantic-risk, G5 territory) pat 14 / gA 6 / vad 8.
> - **STILL TO DO (12 roots, ~390 cards):** Sam(36), vraj(34), Buj(33), Bid(32), pA(32),
>   Cid(27), yat(25), naS(25), yaj(25), rakz(23), hi(19), mad(17) — same loop as below.

**For:** a fresh agent session (or the autonomous account). **Goal:** restore the ~630
Slice-C cards missing from local files so the print bridge ([`src/promote_final_cards.py`](src/promote_final_cards.py))
promotes the **full** Slice C, not a partial set. This is a **Max re-run** task (the originals
are unrecoverable otherwise — see below) and must be **coordinated** (a second account also
works pwg_ru on `master`).

## Why the gap exists

During the Slice-C null-requeue pass, the small requeue results were saved **over** the full
per-root `wf_output.sc.<root>.json` files (`save_and_audit.py` overwrites). So the per-root files
for the 16 requeued roots now hold only the **requeue subset**, not the full original. Separately,
**`wf_output.sc.DA.json` was never written at all** — DA's full output (145 cards) lived only in
the shared `wf_output.sc.json`, which was later overwritten by other roots. The original Slice-C
run was a different session whose transcripts are not reachable here, so **re-running is the only
local recovery path**. The rootmaps + masked inputs under `src/pilot/input/` still exist, so a
re-run reproduces equivalent output.

## What is still salvageable WITHOUT a re-run (do this first, it's volatile)

The two shared files still hold one root each — preserve them before anything overwrites them:

```powershell
cd RussianTranslation
# jan (33/38) currently survives in the shared wf_output.sc.json; han (78) in wf_output.json
copy wf_output.sc.json  wf_output.sc.jan.json    # rescue jan
copy wf_output.json     wf_output.sc.han.json    # rescue han (Stage C, also promotable)
```

(The bridge already globs `wf_output*.json` and recovers these, but copying to stable per-root
names protects them from the next shared-file overwrite.)

## Roots needing a full re-run (16 — have / full sub-cards)

| root | have | full | missing | note |
|---|---:|---:|---:|---|
| **DA** | 0 | 145 | 145 | never saved per-root (biggest loss; dhā) |
| gA | 5 | 65 | 60 | |
| pat | 1 | 73 | 72 | |
| vad | 2 | 47 | 45 | |
| Sam | 5 | 38 | 33 | |
| Bid | 3 | 35 | 32 | |
| Buj | 7 | 39 | 32 | |
| vraj | 2 | 34 | 32 | |
| pA | 3 | 34 | 31 | |
| Cid | 5 | 32 | 27 | |
| naS | 1 | 26 | 25 | |
| yat | 4 | 28 | 24 | |
| yaj | 1 | 25 | 24 | |
| rakz | 1 | 23 | 22 | |
| hi | 1 | 20 | 19 | |
| mad | 5 | 21 | 16 | |

≈ **630 cards** total. (The other 10 Slice-C roots — DA-excepted yA, nI, man, banD, su, iz, paS,
brU, jIv — have full per-root files; leave them.)

## Recovery procedure (per root)

Follow the canonical loop ([`src/pilot/RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md)), **≤3-wide
concurrency** (Slice D's 18× fan-out caused the 117-null collapse; single/low-width = 0 nulls):

```powershell
cd RussianTranslation
# 1. generate the FULL harness for the root (no --keys — the whole root), per-root output file
python src/pilot/gen_opt_harness2.py DA --out=src/pilot/run_pilot_wf.sc_rec_DA.js
# 2. run run_pilot_wf.sc_rec_DA.js via the in-chat Workflow tool (≤3 roots at once)
# 3. save + audit (tag 'sc'):
python save_and_audit.py DA <task-output-file> sc
# 4. repeat for the 16 roots, then re-run the bridge (idempotent, supersede):
python src/promote_final_cards.py
```

The bridge's coverage report will show the thin-root warning shrink as roots are recovered;
done when no Slice-C root is flagged thin.

## Guardrail — prevent this from recurring (recommended small fix)

The root cause is that a requeue save overwrote a fuller file. Add a guard to
`save_and_audit.py`: **refuse to overwrite an existing `wf_output.<tag>.<root>.json` with a file
that has FEWER non-null cards, unless `--force`** (and for requeue, MERGE the new non-null cards
into the existing file instead of replacing). This stops the requeue-overwrite class entirely.

## Coordination

- A second (autonomous) account works pwg_ru on `master`; its committed harnesses are
  `run_pilot_wf.sd_rq_*.js` = **Slice-D** requeue — so Slice-C recovery is *distinct*, not a
  direct overlap. Still: announce on the branch/PR, do not double-run a root, and do this on a
  branch (the store `pwg_ru_translated.jsonl` is a gitignored, regenerable artifact).
- This is a real Max-quota spend (~630 cards across 16 roots). If quota is tight, prioritise the
  high-card roots (DA 145, pat 72, gA 60) first.

## Pointers

- bridge + coverage report: [`src/promote_final_cards.py`](src/promote_final_cards.py)
- loop + concurrency doctrine: [`src/pilot/RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md)
- harness gen: [`src/pilot/gen_opt_harness2.py`](src/pilot/gen_opt_harness2.py) (default budget 12000 if PR #20 merged, else 9000)
- save: [`save_and_audit.py`](save_and_audit.py) (note the overwrite hazard above)
- context: [`BRIDGE_FOLLOWUPS_2026-06-30.md`](BRIDGE_FOLLOWUPS_2026-06-30.md), PR #18 (bridge)
