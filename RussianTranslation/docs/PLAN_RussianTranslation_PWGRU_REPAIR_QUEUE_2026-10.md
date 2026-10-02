# PWG→RU pipeline — ranked repair queue (2026-10)

_Created: 02-10-2026 · Last updated: 02-10-2026_
_Status: staged plan (new file, untracked) — move into a worktree for the commit pass, per the guarded-main-tree rule._

Basis: full sweep of the open pwg_ru defect records in
[SanskritLexicography/FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md),
[GAPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) and
[PWG/docs/PIPELINE_MANUAL.md](https://github.com/gasyoun/PWG/blob/main/docs/PIPELINE_MANUAL.md)
landmines, cross-checked against the **current code** on 02-10-2026. Every "fixed"
record (§447, §453, §594, §600, §601, §604–§608, §610, §613, §615, §617, §619,
`nominals_worklist.py --out` per §592) was verified in-tree and is **excluded** here.

Ranking criteria, in order: (1) live data-corruption or publish risk today,
(2) unblocking value for the paid lane, (3) cost (session size, paid calls, whether a
design ruling is needed), (4) dependencies.

---

## Tier 0 — agent-executable now, zero paid calls, protects data

### 1. `src/citation_tm.py` — vālakhilya typed-miss refusal (§524, h2361 recipe step 1)

- **Defect:** `lookup('ṚV.', '8,60,1', lang='en')` returns `status=hit` with a fluent
  Griffith verse of the **wrong hymn** for RV 8.49–8.103 (678 stanzas, eleven
  vālakhilya hymns numbered inline in the key, appended in the source column).
  The h2361 refusal never landed.
- **Site:** `lookup(lang='en')`, after `resolved = _rigveda(locus)`, before
  `_fetch_en_rv(resolved)` — parse mandala/sūkta from the canonical
  `01_rigveda:8.60.1` shape; for mandala 8, sūkta ≥ 49 return
  `{**base, 'status': 'miss', 'reason': 'en-numbering-unverified'}`.
- **Cost:** ~10 lines + selftest pin (`lookup('ṚV.', '8,60,1', lang='en')` must never
  be `hit` until the asset is repaired). Half a session.
- **Note:** latent only — no live consumer consults `lang='en'` today
  (`corpus_gate._citation_reuse` uses the default `ru`). Ranked first by cost/benefit.

### 2. `src/promote_final_cards.py` — make `--merge` dry-run unless the write is explicit (§611.2)

- **Defect:** `--apply` gates only the ready-partial-report path; a plain `--merge`
  invocation **promotes for real**. H3663 surfaced it by accident (recoverable via
  `.premerge.*.bak`, but an unintended write).
- **Fix:** require an explicit write switch on the `--merge` lane (reuse `--apply`
  semantics or add `--confirm-write`); keep the automatic `.premerge.*.bak`; mind the
  H2089 `--allow-raw-default-merge` interplay. Update the H3654/H3663 recipes and
  RUN_LOG so downstream readers inherit the corrected contract.
- **Verification:** fixture-store selftest only (never the live store): no-write
  without the switch, write with it, refusal gates unchanged (order per §611.1 —
  read `requeue.defect.keys.txt`, the promotable verdict, never the "units clean" line).
- **Cost:** small code change + doc sweep.

---

## Tier 1 — preconditions before the next paid window

### 3. Cost plumbing: price from the envelope, keep the demotion honest (§597 + §602)

- **Defect:** the CLI envelope carries real `total_cost_usd` even on refused calls
  (PR #1837 capture), but `gateway_route.py` rule 3 demotes `cost_evaluable=False` on
  content failure, and `bounded_supervisor.py` stops at the **top of the drain loop**
  when `--cost-ceiling` is set and `_durable_cost_evaluable` is false — so a
  cost-bounded `no_pwg` window is **unrunnable** and human spend authorization cannot
  clear it.
- **Options:**
  - **(a)** record the envelope's `total_cost_usd` in a separate
    `observed_cost_usd_envelope` field that does **not** flip `cost_evaluable`, and
    change the supervisor's precondition to "envelope-cost capture available" —
    converts an unrunnable lane into a measured one. Cost: ~1 session + selftest.
  - **(b)** keep the lane unpriced; run `--allow-unbounded` under an explicit human
    ruling. Cost: zero code, but re-opens the H2851 guard-tunnelling shape.
- **Recommendation: (a).** The capture already exists; the demotion keeps its meaning
  (a *failed* call is never priced into the ledger), while the *window* becomes
  priceable from real envelopes. (b) only if (a) is ruled out on the ledger-contract
  grounds.
- **Human decision required** on (a) vs (b) before any code lands.

### 4. Canonical-resolution port: window-index glob + roster sqlite (§603)

- **Defect:** `no_pwg_scale_plan.py` globs the gitignored `output/` dir for the window
  index (a fresh worktree silently re-proposes a completed window) and
  `bounded_staged_run.py` resolves `max_orchestrator.sqlite` against **cwd**
  (dies, and silently creates an empty schema-only DB at the worktree root).
- **Fix:** port both to the `store_path.canonical_store()` pattern
  (env → main-worktree → local); until landed, pass `--start-index` / `--db`
  explicitly from any non-main checkout.
- **Adjacent hazard, human call:** `src/pilot/max_orchestrator.sqlite` is untracked
  **and** un-gitignored in the guarded main tree — the only record of validated
  profile slots; one `git clean -fd` kills the lane until rebuilt by hand.
  Options: (i) gitignore + committed rebuild/restore recipe; (ii) move the roster to
  a committed JSON and let the sqlite be a cache. **Recommendation: (ii)** — the
  roster is tiny, auditable in review, and a committed file cannot be cleaned away.
- **Cost:** ~1 session + the ruling.

### 5. Prove the schema-park half; add the free-RAM launch precondition (§596 residual + §599)

- **Defect:** the v1.144.114 salvage fix is proven (`out.json` written on abort), but
  the schema-park half (`structured_output_retry_exhausted` = park-and-continue) is
  **unproven** — `_sr_avaka`, the key that killed H3627, sits at index 19 and was
  never reached. Separately, `0xC0000142` host-RAM launch deaths are unguarded.
- **Fix:** (i) add a free-physical-RAM probe before the first paid call (threshold:
  name one and measure on c1 under load; signature `0xC0000142` + <100 ms + zero
  usage); (ii) run the `_sr_avaka` proof — needs items 3–4 landed first, one paid call.
- **Cost:** probe ~half a session unpaid; proof one paid call.

### 6. Durable evidence root: capture the INPUT sidecars (§612 fix)

- **Defect:** the evidence root preserves outputs only; `_pilot_gen_merged.py`
  (at `src/_pilot_gen_merged.py`) writes `<key>.raw.txt` / `.portrait.json` into the
  checkout-relative gitignored `src/pilot/input/`, so a window's cards become
  **permanently unpromotable** once its worktree dies.
- **Fix:** copy both sidecars for every `selected_key` into the evidence root at
  manifest-build time, resolved per the §604 rule (derive from the resolved root, no
  second independent resolution). Two small files per key.
- **Bonus:** bake §612's amendment into `audit_window.py`'s stale-input message —
  a regenerable `.raw.txt` that still matches proves the text is stable and isolates
  the drift to the moved field (the `layers: ["pw"] → ["nws","pw"]` case means the
  SOURCE grew a layer; the gate is protecting content, not just provenance).
- **Cost:** ~1 session.

---

## Tier 2 — quality / structural (design work, no urgency date)

### 7. Structural reuse fence (§590)

Replace the denylist's *coverage* role with a structural rule — require the reuse
target's source to be the whole publication fragment, or the source span to be a full
lexical unit; keep `SHORT_GLOSS_DENYLIST` as belt. Expect the Wave-2 quarantine rate
to rise slightly; that is correct behaviour, not a regression.

### 8. `restate`/`placement` reconciliation (§620)

4,187 rows still read the false `restate` value because every consumer takes the old
name alone. Derive the old field from `placement` at one site and RED-pin the
correspondence as a corpus STOP gate.

### 9. Griffith asset upstream repair (h2361 steps 2–3)

Re-extract from `rvlinks/RV_sa-hn-ru-de-en_1.html` fixing the English column drift,
re-check the **other** language columns of the same source with the deity-anchor
cross-column audit (~92 % aligned vs 19.8 % on 8.49–8.103), wire
`audit_griffith_en_alignment.py --selftest` into CI. Only blocking for EN promotion;
pairs naturally with item 1.

---

## Tier 3 — already-tracked programs and human decisions (do not re-plan)

- **Control-plane strangler** — issue [#1987](https://github.com/gasyoun/SanskritLexicography/issues/1987),
  H3714 Wave 1 landed PARTIAL (V12 second-reviewer sign-off and the V13 two-call
  canary owed; no legacy writer disabled until then). Plan doc exists.
- **3 store SAN-LOSS rows** (`mA` / `pat` / `asvatantra`) — parked for G5 per §601
  (the two `dA` medium rows were requeued `--no-tm`); the scanner defect is fixed,
  the *rows* wait on the human G5 ruling.
- **H3948 re-segmentation** — `@DECIDE` row already in GTD; 3,212 of 11,462 rows
  would change on the conservative join, 12 provably, 2,210 unresolved — a range,
  not a figure.
- **9 withdrawn rows need real translation** (§591 residual) — paid work, only after
  Tier 1 items 3–4 land.
- **289-row `Instr.→Ins.` drift** (GAPS §16) — adjudicate row by row into a committed
  ack file; surfaced by `audit_store_gates.py` `only_mirror`.
- **GAPS §19 / §621 provenance** — accept as permanently lost for 9 of 10 stamp
  classes; no repair possible, keep the honest gap row.

---

## Not in this queue

- **PWG repo digitization landmines** (`makeabbrv.sh` broken in both copies, 17
  divergent `updateByLine.py` copies, `make_js_index.py` generations) — different
  repo and pipeline; see PIPELINE_MANUAL landmine №1–3. Candidate for its own small
  sweep if the digitization lane revives.
- **§592 `nominals_worklist.py`** — the `--out` fix is **already in the current code**
  (verified 02-10-2026); FINDINGS §592 may take a one-line "applied" stamp at the next
  hub sweep.

---

## Sequencing summary

| # | Item | Tier | Cost | Paid? | Human ruling? |
|---|------|------|------|-------|---------------|
| 1 | citation_tm vālakhilya refusal | 0 | ~0.5 sess | no | no |
| 2 | promote --merge write gate | 0 | ~0.5 sess | no | no |
| 3 | cost plumbing (a/b) | 1 | ~1 sess | no | **yes** |
| 4 | canonical port + roster home | 1 | ~1 sess | no | **yes** (roster) |
| 5 | schema-park proof + RAM probe | 1 | ~0.5 + 1 call | yes | no |
| 6 | evidence-root input sidecars | 1 | ~1 sess | no | no |
| 7 | structural reuse fence | 2 | 1–2 sess | no | no |
| 8 | restate/placement derive | 2 | ~1 sess | no | no |
| 9 | Griffith asset repair | 2 | ~1 sess | no | no |

Items 1+2 fit one session with a shared worktree/PR. Items 3–4 gate every paid window
after them; item 5's proof call is the first thing that runs once they land.

_Dr. Mārcis Gasūns_
