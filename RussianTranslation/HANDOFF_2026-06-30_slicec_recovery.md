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
> - **DONE — ALL 15 roots re-run this session (Max, ≤3-wide).** First wave: `pat`(73),
>   `gA`(65), `vad`(47). Remaining 12: `Sam`(38), `Buj`(39), `vraj`(34), `Bid`(35), `pA`(34),
>   `Cid`(32), `yat`(28), `naS`(26), `yaj`(25), `rakz`(23), `hi`(20), `mad`(21). All saved as
>   full per-root files. **Final bridge: 1920 non-null cards / 8015 sense rows / 46 headwords;
>   no root left on the thin-warning list.** Slice-C recovery COMPLETE.
> - **Quality pass DONE — all 15 roots requeued (transient nulls + defect rework).** Each
>   root's requeue keys re-translated via `requeue_from_audit`-style harnesses
>   (`run_pilot_wf.sc_rq_<root>.js`, ≤3-wide) and `--merge`d back (new non-null replaces the
>   defect card; nulls keep prior). Final bridge: **1934 non-null cards / 8592 sense rows /
>   46 headwords.** Residual: ~3 stubborn null head-cards (Sam/Buj/naS) the fidelity guard
>   keeps rejecting — bridge skips them, acceptable. (CRLF gotcha: `requeue.keys.txt` is
>   CRLF; strip `\r` before comma-joining into `--keys`, or only the last key matches.)
> - **NEW — DCS frequency, THREE dimensions** (per MG, 2026-06-30), all on `dcs_freq` per row:
>   1. **General band** — `build_dcs_freq.py`: `{band 1-5, count, hapax, attested, core80}`,
>      per preverb-compound w/ root fallback (96.5% matched). core80 = 2,551 lemmas (2.8% of
>      types) covering 80% of the 5.69M-token corpus. Gap: vowel-sandhi compounds
>      (pra+āp→prāp) fall back to root count; sandhi-aware join = follow-up.
>   2. **POS frequency** — `build_dcs_freq_dims.py`: `dcs_freq.pos` = full upos distribution
>      (counts + shares + dominant + recalibrated 1-5 band per POS).
>   3. **Genre frequency** — `dcs_freq.genre` (16 fine genres, recalibrated band per genre)
>      + `dcs_freq.era` (5-era Renou rollup). Counts are **TOKEN frequency** per register:
>      each text is resolved to its Renou register(s) via `build_dcs_renou`'s genre+name
>      logic, then tokens are counted per register (token→sentence→chapter→text join).
>      76% of corpus tokens land in a register; the rest (medical / rasaśāstra / nighaṇṭu /
>      classical śāstra prose) genuinely has no Renou register and contributes to none.
>   Bands are RECALIBRATED per dimension (quintile edges within each genre/POS), vs the
>   general band's fixed log10 edges. Both builders carry `--selftest`; tables gitignored.
> - **Both earlier caveats tightened (2026-06-30):** (a) genre is now token-frequency, not
>   document-frequency (above); (b) `sandhi_key` (build_dcs_freq.py) applies vowel sandhi at
>   the preverb–root junction so `pra+āp`→`prāp`, `vi+āp`→`vyāp`, `anu+ā`→`anvā` match their
>   exact compound lemma (match kind `compound_sandhi`) instead of falling back to the root
>   count — e.g. prāp now 6022 (its own), was the root āp's 2328.

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
