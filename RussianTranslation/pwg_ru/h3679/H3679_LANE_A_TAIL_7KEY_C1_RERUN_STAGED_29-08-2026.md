# H3679 — Lane A tail: the 7 held keys, STAGED for the next c1 window

_Created: 29-08-2026 · Last updated: 29-08-2026_

Handoff: [H3679](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3679-OxAlpha_SanskritLexicography_lane-a-7keys-paid-rerun_29.08.26.md)
(Uprava). Source context: [H3663 Lane A](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3663/H3663_LANE_A_16KEY_C1_WINDOW_29-08-2026.md)
§3/§4/§9/§10 and FINDINGS §597/§602/§611/§612/§614.

**Status: STAGED, ZERO PAID CALLS.** The free half of the mission is done and verified
offline; the paid half is blocked by two named preconditions (§2, §3) and must fire from the
box that holds the c1 roster (§4). A fire session needs ONLY this document — every command
below was executed once from a clean worktree and is known-good syntax.

## 1. The keys

| safe name | SLP1 | senses | class |
|---|---|---:|---|
| `jar_ayu` | `jarAyu` | 6 | defect |
| `r_ama_wa` | `rAmaWa` | 4 | defect |
| `_s_ulin` | `SUlin` | 8 | defect |
| `ut_ta` | `utTa` (uttha) | 5 | defect |
| `y_atu` | `yAtu` | 5 | defect |
| `v_as_a` | `vAsA` | 1 | defect |
| `ut_t_apana` | `utTApana` (utthāpana) | 11 | transient (plain re-run) |

Requeue list (safe names, one per line): [requeue.7keys.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h3679/requeue.7keys.txt).
Safe-name → SLP1 decode is `safe_name`'s uppercase→`_lower` rule; the two non-obvious ones
are `_s_ulin` = śūlin (`SUlin`) and the `ut_ta` pair = uttha/utthāpana (`T` = tha, NOT ṭ —
`uTta`/`uTtApana` are absent from PWG and the generator refuses them).

Inputs were regenerated offline, 7/7, zero calls:

```
PWG_INPUT_DIR=<checkout>/RussianTranslation/src/pilot/input \
  python src/_pilot_gen_merged.py jarAyu rAmaWa SUlin utTa yAtu vAsA utTApana
```

The generator is idempotent/resumable (skips existing `.raw.txt`). The 14 files
(`.raw.txt` + `.portrait.json` per key) are ALSO copied to the durable data root
`pwg-ru-data/raws/` — the §603/§612 lesson (worktree-local inputs die with the worktree and
make audited cards permanently unpromotable) applied to the fire session in advance.
**The fire session must run `audit_window.py` against inputs byte-identical to the ones the
manifest was built from — prefer copying from `pwg-ru-data/raws/`, and re-run the one-line
generation above if the checkout has none.**

## 2. Ration — the reason this did not run on 29-08

The c1 ration (H3658/H3663: **≤2 attempts per UTC day, ≥6 h spacing**) is **exhausted for
29-08 UTC**:

1. H3659's `no_pwg_w09` window — 8 priced calls, close PRs #1943/#1944/#1949 merged
   05:56–07:29Z.
2. H3663's 16-key Lane A window (killed attempt + 5 chunks) — close PRs #1965/#1966 merged
   09:47Z, repair pass #1972 at 11:30Z.

The earliest legal fire is therefore **30-08 00:00:00Z or later**; the ≥6 h spacing from the
last 29-08 call is then satisfied automatically. The gate itself (GATE-0 + canary) was
deliberately NOT fired early: the canary is a paid call, and a same-day probe would itself
violate the ration; a receipt also expires in ~6 h, so nothing fired today survives to be
useful tomorrow. MG's «run those two windows» pre-ruling (29-08) authorised unbounded for the
two windows that have ALREADY run; `--allow-unbounded` is moot on this lane anyway —
`headless_worker.py` has no cost gate (H3663 correction).

## 3. Store lineage — reconcile BEFORE promoting anything here

The only store copy on the 29-08 Mac estate is `pwg-ru-data/tm/pwg_ru_translated.jsonl`:
**11 462 rows**, sha `19fcf5258e5e…`, last refreshed by **H3627** (28-08 13:17Z, ledger row +
commit `5346cba`; `pwg-ru-data` local == origin, nothing newer pushed).

H3663's close claims **11 515 → 11 519** (mirror → `3022239c63ac`) and H3654 promoted before
that — **neither write reached any durable surface on this box** (no newer tm commit on
origin, no other copy on disk, mirror ledger's last row is H3627). H3659's durable evidence
root `D:\ClaudeTools\profiles\claude1\.pwg_ru_evidence\c1\h3659` proves 29-08's windows ran
on the **Windows box**, so the 11 519 store most likely exists THERE (Windows-local
`src/tm/`, worktree-local writes — the §603 class again).

**Gate on the fire session: before `promote_final_cards.py --merge`, establish the store
base.** Either (a) the Windows store is confirmed 11 519 + mirror `3022239c63ac` → sync it
into `pwg-ru-data/tm` first, or (b) it is unrecoverable → the 9 H3663/H3654-promoted cards
rejoin the requeue queue honestly and this lane promotes onto the 11 462 base. The 7 keys of
this lane are unaffected either way — they were never promoted and are absent from both
generations. Do NOT merge onto an unverified base and assume the lane doc's numbers.

## 4. Where the fire can physically happen

Verified absent on the 29-08 Mac estate: `max_orchestrator.sqlite` (the validated-profile
roster — gitignored, main-tree-only), any profile `--config-dir`, any `PWG_EVIDENCE_DIR`
durable root, `ClaudeTools` profiles. All of these live on the Windows box
(`D:\ClaudeTools\profiles\claude1\…`). A `claude` CLI exists on the Mac, but no roster row
can bind `--only-profile c1` without the roster DB (H3659 hit that refusal by name). Fire
from the Windows box, or first re-validate the roster wherever you fire.

## 5. Chunks — build verified end-to-end (free)

`ut_t_apana` (the H3663 transient that needed retry + 2 heal rounds) is isolated alone, the
`_sr_avaka` containment pattern; each chunk writes its own output, and the turn is kept
alive by polling (§604: background windows die at turn end).

| chunk | keys | max-calls |
|---|---|---:|
| h3679a | `jar_ayu` `r_ama_wa` | 12 |
| h3679b | `_s_ulin` `ut_ta` | 12 |
| h3679c | `y_atu` `v_as_a` | 12 |
| h3679d | `ut_t_apana` | 8 |

Build (cwd = `RussianTranslation/`; requeue_from_audit stamps the TM denylist and validates
the keys, then gen_opt_harness2 re-stamps BOTH artifacts in byte mode; **flags are
equals-form only** — `--out <path>` as two tokens is silently ignored and writes the default
`run_pilot_wf.opt2.js` instead):

```
python src/pilot/requeue_from_audit.py h3627-reingest \
    --requeue-file=pwg_ru/h3679/chunk.h3679a.keys.txt --nominal \
    --out=src/pilot/output/h3679/run_pilot_wf.h3679a.js \
    --manifest-out=src/pilot/output/h3679/manifest.h3679a.json

python src/pilot/gen_opt_harness2.py h3627-reingest --keys=jar_ayu,r_ama_wa \
    --nominal --no-tm --budget=1 \
    --out=src/pilot/output/h3679/run_pilot_wf.h3679a.js \
    --manifest-out=src/pilot/output/h3679/manifest.h3679a.json
```

Measured on the staging pass: every chunk lands `N cards in N batches (sizes [1,…])` —
`--budget=1` byte mode confirmed. Bare `requeue_from_audit` (no `--transient/--defect`)
routes `which='all'` → `--no-tm` + TM-denylist stamping, which is the safe superset here: the
transient had nothing cached, and the 6 defects' cached H3663 content must NOT be re-served
(the docstring's re-serve trap). No deterministic repair rule is involved (PR #789 refusal
stands; §614 measured these wrappers as never-emitted, not drifted).

**v1/v2 trap (H3677):** without the five binding flags the manifest stamps
`pwg.headless_execution_manifest.v1` and production refuses it. On the fire box, rebuild
with the profile binding so the schema is **v2**:

```
    --profile-slot=c1 --config-dir=<c1 config dir> \
    --execution-route=claude-cli-headless \
    --executor-lane=serial-whole-card \
    --validation-method=audit_window+final_schema
```

The staged v1 manifests on the Mac are syntax-validation artifacts only — seal and run the
v2 rebuild.

## 6. Fire recipe (ordered, per H3663's measured path)

1. `git fetch origin && git worktree add` off a fresh `origin/master`; restore inputs (§1).
2. `PWG_EVIDENCE_DIR` to the durable root **outside every checkout**; roster DB via `--db`
   explicitly (H3659 refusal: `--only-profile` is not a roster slot).
3. GATE-0 health probe (`h963_c4_gate0_probe.py --account c1`, default is the RETIRED c4) →
   **PASS** required.
4. Canary `dq_canary_puregloss`, one paid call, judged by `canary_gate.py judge` → **GO**
   required; receipt lands in the durable root (a worktree-local receipt is not a ration
   record — H3663 §8).
5. Per chunk (§5 order, `ut_t_apana` LAST):

```
python src/pilot/headless_worker.py <manifest.h3679X.json> \
    --output src/pilot/output/h3679/out.h3679X.json \
    --status-out src/pilot/output/h3679/status.h3679X.json \
    --only-profile c1 --timeout 300 --max-calls <chunk ceiling> \
    --preflight <scope-matched preflight> --manifest-sha256 <sha256 of the v2 manifest> \
    --call-reservation src/pilot/output/h3679/call_reservation.h3679.jsonl \
    --run-id h3679-<chunk>
```

   OMIT `--max-agents` (total-spawn ceiling; `--max-agents 1` is canary-only). Poll; never
   pipe stdout through `tail`; watch `run['reservations']`, never `run['calls']`.
6. `audit_window.py <out> --window-tag=h3679X` per chunk — the promotable verdict is each
   dir's `requeue.defect.keys.txt`, NOT the `PASS: n/n units clean` line (§611).
7. Promotion input = passing keys only; union block list from ALL chunk audit dirs; do NOT
   pass `--override-reviewed`; **`--merge` writes the store — it is not a dry run** (§612):

```
python src/promote_final_cards.py --merge \
    --glob 'src/pilot/output/h3679/promote/out.*.json' \
    --defect-keys src/pilot/output/h3679/requeue.blocked.keys.txt \
    --gen-model-version <generation model> --promotion-id h3679-lane-a-tail
```

8. `refresh_tm_mirror.py --handoff h3679` → then `audit_store_gates.py` and
   `placement_axis_check.py` must exit 0 (after §3's reconciliation).
9. Honest residue: whatever `requeue.defect.keys.txt` holds after this window stays requeued
   — never forced past the guard. Then GTD row update, changelog + `/cut-release` pwg_ru,
   `/handoff-close H3679` with the actual tier+version that ran.

## 7. Cost honesty

Preflight estimate ~$0.06/card (~$0.42 for 7). This route reports
`billing_mode: unknown_gateway` — **cost is NOT evaluable; never report $0** (§597).

## 8. Acceptance (locked)

- **Done looks like:** all 7 keys re-translated on c1 in ≤4 chunks; each chunk audited; keys
  whose audit dirs hold no defect promoted with gates green; the rest requeued honestly; lane
  doc + store base reconciled.
- **Prove with:** per-chunk `out.*.json` + status + audit dirs (durable root), promotion id
  `h3679-lane-a-tail`, `refresh_tm_mirror` G1–G3 PASS, `audit_store_gates` +
  `placement_axis_check` exit 0, gate receipts (health PASS + canary GO) in the durable
  probe log with the fire date.
- **On our data:** store base reconciled per §3 before the write; the 7 keys absent from the
  store before and present-after only for audit-clean ones.
- **Fail =:** any NO-GO at health or canary (record the named stop, spend nothing); a
  `budget_exceeded` chunk ceiling (split the residue, requeue honestly); promotion attempted
  on an unreconciled store base (STOP — that is the §3 gate, not a speed bump).

_Dr. Mārcis Gasūns_
