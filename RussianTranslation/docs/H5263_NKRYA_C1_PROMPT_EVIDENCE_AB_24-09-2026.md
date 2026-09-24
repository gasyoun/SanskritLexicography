_Created: 24-09-2026 · Last updated: 24-09-2026_

# H5263 — NKRYa evidence block in the c1 PWG-RU prompts: build done, A/B NOT RUN

**Verdict: BUILD SHIPPED, A/B BLOCKED. 0 of the 5 pre-authorized paid c1 calls spent — the
budget is untouched and still authorized.** The keep/drop recommendation the handoff asks for
cannot be earned from 0 calls, so this report names what the block does, what it costs in
prompt bytes, and the two gates that stand between here and the A/B.

## What shipped

1. [`src/nkrya_prompt_evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nkrya_prompt_evidence.py) — the compact advisory block. It reads its facts through
   `nkrya_evidence_card.gather()`, the same query path and the same disk cache as the H5261
   evidence card, so there is exactly one NKRYa client in this repo, not two.
2. [`src/pilot/headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) `card_block()` appends `nkrya_block(inp)` — which returns
   the empty string, and does not even import the NKRYa module, when a card carries no
   `nkrya` input. A manifest without the key therefore produces **byte-identical** prompt
   bytes; `headless_worker_selftest.py` (PASS, unchanged) is the witness on the existing pins.
3. [`tools/h5263_prompt_evidence_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h5263_prompt_evidence_probe.py) — the 0-call proof, output in
   [`reports/H5263_prompt_evidence_diff.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H5263_prompt_evidence_diff.json).
4. [`tests/test_nkrya_prompt_evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/tests/test_nkrya_prompt_evidence.py) puts the selftest inside the offline contract-pin
   suite, so `python tests/run_offline_suite.py` (the `offline-contract-pins` CI job) covers
   it — offline, committed cache, no token, 0 paid calls. It is **not** wired into the
   `russian-translation-gates` selftest list next to the two H5261 lines: this session's
   credentials cannot push `.github/workflows/ci.yml` (`refusing to allow an OAuth App to …
   without workflow scope`). A human with workflow scope can add the one line
   `python src/nkrya_prompt_evidence.py --selftest` there; the pin above already makes it
   redundant rather than missing.

## Step 1 — the 0-call prompt diff (the handoff's own precondition)

Ran on the C07 clouds data, offline against the committed `pwg_ru/nkrya_cache` (29 entries,
**0 live NKRYa calls, 0 paid c1 calls**). One card, production prompt shape:

```
prompt bytes 163 -> 1696 (delta +1533)
```

The block as it reaches the model:

```
--- advisory NKRYa corpus evidence (FACTS ONLY; НКРЯ, основной корпус; do not treat as a choice) ---
reading rule: the API returns only the top 10 collocates per relation, so "not in top 10" never means "unattested"; pair = candidate lemma within 3 words of the head lemma, either order; 19c = texts created 1800-1899.
head туча:S 42.40 ipm (cat 3)
head облако:S 65.75 ipm (cat 3)
  связный + туча | 2.71 ipm (cat 2) | sketch: not in top 10 | pair MAIN n/a, 19c n/a
  сплочённый + туча | 0.94 ipm (cat 1) | sketch: not in top 10 | pair MAIN n/a, 19c n/a
  сплочённый + облако | 0.94 ipm (cat 1) | sketch: not in top 10 | pair MAIN 1, 19c n/a
  сплошной + туча | 35.21 ipm (cat 3) | sketch: not in top 10 | pair MAIN 95, 19c 16
  сгущающийся (lemma сгущаться) + туча | 4.90 ipm (cat 2) | sketch: nsubj_S_V #1 dice 8.94 | pair MAIN 226, 19c 12
  сомкнутый (lemma сомкнуть) + туча | 5.17 ipm (cat 2) | sketch: not in top 10 | pair MAIN 1, 19c n/a
```

(abridged — the full 14-line block is in the JSON report).

Every number here reproduces the corresponding cell of
[`pwg_ru/h5069/C07_NKRYA_EVIDENCE_CARD.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5069/C07_NKRYA_EVIDENCE_CARD.md) — the block is a re-rendering of that card's
data, not a second measurement of the corpus. It is also exactly the fact MG asked for on C07
(«тучи сгущаются, тучи не могут быть последовательными»): `сгущаться` is the **#1 nsubj
collocate of туча** with 226 MAIN pairs, while `связный` and `сплочённый` have no pair reading
at all. Two deliberate choices in the wording:

- **`n/a`, never `0`.** A missing count is the API returning no number; printing `0` would turn
  "no reading" into the false claim "never co-occurs".
- **The reading rule ships inside the block.** Top-10 truncation is the one way this evidence
  can be misread into a prohibition, so the correction travels with the data.

## Step 2 — route check: config-level only, msg_ id NOT obtained

The H4527 standing check wants the `msg_` id off a live transcript, which costs a paid call.
What was probed at 0 cost: `D:\ClaudeTools\profiles\claude1\.claude\settings.json` carries **no**
`ANTHROPIC_BASE_URL` and no third-party auth override, consistent with the H4527 restore
recorded in `.ai_state.md` («`c1` is back on Anthropic», 22-09-2026). That is config evidence,
**not** the transcript proof — the msg_ id check must still run as the first paid call of the
A/B, before the five translation calls.

## Step 3 — the A/B: NOT RUN. Two gates, both real

1. **No NKRYa API token on this box.** `python src/nkrya_client.py probe` returns the
   "no token found" path; the Windows credential store has no `ruscorpora-api` entry and no
   `RUSCORPORA_API_TOKEN` is set. This is the human step the 22-09 grill already recorded as
   outstanding ([GRILL_NKRYA_SKILL_DECISIONS_22-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/GRILL_NKRYA_SKILL_DECISIONS_22-09-2026.md) § Human step). The committed cache
   covers **only** the C07 clouds vocabulary, so an arbitrary 5-card volume cannot be given an
   evidence block at all without the key. This gate blocks the A/B *independently of the money
   side* — the paid calls would run against empty evidence blocks and measure nothing.
2. **The paid lane needs a fresh live-gate GO.** A 5-card volume is legal only after
   `/pwg-live-gate` (health probe + `dq_canary_puregloss` control) passes; the gate itself is
   ~$0.55/probe and rationed (≥6 h spacing, ≤2 attempts/UTC day). No GO exists for 24-09-2026.

Neither gate is something an agent may self-authorize, and spending the 5 calls without gate 1
would burn a pre-authorized, non-renewable budget on a null measurement.

## Keep / drop — what the A/B must decide, and the prior

**No recommendation is earned yet.** What the eventual A/B has to weigh:

- **Cost side, now measured:** +1533 bytes of *volatile* prompt per card at C07 density
  (two heads, five candidates). That lands in the per-card block — the volatile suffix, right
  of the cache breakpoint — so it is paid on **every** card, every call, with no prefix reuse.
  At 5 cards that is ~7.7 KB of uncached input per window.
- **Benefit side, unmeasured:** whether the block actually moves collocation and rare-word
  choices, scored with the handoff-B flags.
- **The honest prior:** the block is advisory by construction (grill ruling 3) and the
  evidence's own shape rewards caution — three of five C07 candidates have no pair reading, so
  the block's most common content is an absence the model must not over-read. A measured A/B is
  the only thing that can tell "useful grounding" from "expensive noise"; this report does not
  guess.

## Delivery (five fields)

- **Changed:** the NKRYa prompt-evidence module, the one-line `card_block` hook, the 0-call
  probe tool, its JSON report, one CI selftest line, this report.
- **Unchanged:** every prompt byte for cards without an `nkrya` input; the store; the paid
  budget (0/5 spent); the NKRYa cache (read-only, 0 live calls).
- **Checks:** `python src/nkrya_prompt_evidence.py --selftest` PASS (11 checks, offline);
  `python src/pilot/headless_worker_selftest.py` PASS; `python src/nkrya_client.py --selftest`
  PASS; `python src/nkrya_evidence_card.py --selftest` PASS.
- **Risks:** the block sits in the volatile suffix and defeats no cache, but it is paid per
  card — at high candidate counts it could dominate a card's input. The `n/a` rendering is a
  mitigation of the top-10 misreading risk, not a proof it does not happen; only the A/B
  settles that.
- **Inspect:** [`reports/H5263_prompt_evidence_diff.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H5263_prompt_evidence_diff.json) first — it carries the diff, the
  byte deltas, the 29 cache keys used, and `paid_calls: 0`.

## Second pass, 24-09-2026 15:05–15:40Z — Opus 5.5 (`claude-opus-5-5`), Mac + MSI over SSH

The first pass's gate 1 was a **box** gate, not a missing key: the Mac's keychain holds
`ruscorpora-api` (`nkrya_client.py probe` → `auth: true`). So this pass split the work
across boxes: NKRYa on the Mac, the paid half on MSI.

1. **Evidence pre-fetched and committed**. [`tools/h5263_ab_evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/h5263-drain/RussianTranslation/tools/h5263_ab_evidence.py) `fetch` made 14 live NKRYa calls
   and wrote [`pwg_ru/h5263/evidence_han.json`](https://github.com/gasyoun/SanskritLexicography/blob/h5263-drain/RussianTranslation/pwg_ru/h5263/evidence_han.json) and [`evidence_yat.json`](https://github.com/gasyoun/SanskritLexicography/blob/h5263-drain/RussianTranslation/pwg_ru/h5263/evidence_yat.json), plus the new cache
   entries. MSI injects them offline (`inject`), with 0 NKRYa calls.
   - **The A/B cards carry an MG-voted gold rendering** (the [H5069 chat vote](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5069/H5069_CHAT_VOTE_DECISIONS_C01-C09_22-09-2026.md)):
     - `han~~h0_57_sam` is C07, the clouds collocation.
     - `yat~~h0_01_sec_1` is C02: the store has «союзить»; the gold is «связывать союзом, объединять».
   - The yat block already shows the signal the A/B is meant to test:
     - `союзить + союз | ipm n/a | … | pair MAIN n/a`: the store's word has **no reading at all** in the main corpus.
     - `связывать + союз` has 40 main-corpus pairs and 15 in the 19th-century subcorpus.
   - **Disclosed leak:** the gold verb is among the yat candidates, as the audit proposal would have put it there in production too.
2. **Route check: PASS, at 0 extra cost.** A live c1 transcript on MSI (a drain session, 15:04Z)
   carries `"model":"claude-opus-5"` and a native Anthropic `msg_011C…` id, and c1's
   `.credentials.json` was refreshed at 14:48Z. That clears the 06:20Z 403 recorded earlier the same day.
3. **Inputs and manifests built on MSI, 0 calls.**
   - `_pilot_gen_merged.py --root-split han yat` wrote into a scratch `PWG_INPUT_DIR`. The splitter now keeps
     the clouds sense in one sub-card, `han~~h0_57_sam`; the store record is the older `…_sam_0` split.
   - `gen_opt_harness2.py … --no-tm --profile-slot=c1` and `perf_preflight.py` ran per root:
     - yat: one card, one batch, so 1 call per arm.
     - han: presplit (136 `<ls>` > the floor of 40), so **3 fragment calls per arm**.
4. **Finding: the prompt hook missed every presplit card, now fixed.**
   - A presplit card is prompted through `headless_worker.fragment_prompt_blocks()`, which never called `card_block()`.
     So the NKRYa block would have silently vanished from `han~~h0_57_sam`, the very clouds card that motivated the handoff.
   - `fragment_prompt_blocks` now appends `nkrya_block(inp)`. It is still `''` for cards without evidence, so every existing
     fragment prompt stays byte-identical.
   - The selftest gained the fragment check (12 checks, PASS), and `headless_worker_selftest.py` still PASSes.
5. **`/pwg-live-gate` on c1: health PASS, canary NO-GO.**
   - Health: `h963_c4_gate0_probe.py --account c1`, warm-up 6 356 ms, measured 5 237 ms, against a ceiling of 240 000 ms: **PASS**.
     The probe warned that MSI had 777 MB of physical memory free.
   - Canary: `dq_canary_puregloss` through `headless_worker` → `classification: refusal`
     (`StructuredRefusal`). The model declined the structured output because «plan mode is still
     active in this session». `canary_gate.py judge` → **CANARY NO-GO** (`null card`).
     This is the FINDINGS §498 shape from 19-08: the worker always passes `--permission-mode plan`
     (`headless_worker.py` `_spawn` argv), and the profile is not at fault (`defaultMode: auto`).
     Receipt: `C:\Users\user\.pwg_h5263\canary\canary_receipt.json` on MSI.
   - A failed gate stops the run: no retry inside a sitting. **The A/B's own calls were not spent.**

**Spend:** 3 c1 calls, all gate legs (health warm-up + measured, 1 canary at $0.2427).
**0 of the 5 pre-authorized A/B calls were used.** NKRYa: 14 live calls.

**Keep / drop: still not earned.** Nothing new on the benefit side. On the cost side, the yat block is
+775 bytes per card, well under C07's +1533.

## What unblocks the A/B

1. **The next legal c1 gate attempt is at or after ~21:20Z on 24-09** (the ration: ≥ 6 h after the 15:20Z
   probe, ≤ 2 attempts per UTC day). Otherwise it is any time from 25-09.
   - The recipe is ready on MSI: inputs under `C:\Users\user\.pwg_h5263\`, and the canary script in
     [`tools/h5263_msi_canary.ps1`](https://github.com/gasyoun/SanskritLexicography/blob/h5263-drain/RussianTranslation/tools/h5263_msi_canary.ps1).
   - On a GO, the run is:
     1. yat arm A (as built) and arm B (`h5263_ab_evidence.py inject`): 2 calls.
     2. If calls remain, han arm A and arm B: 6 calls. That is above the 5-call cap, so it needs a new MG yes.
2. **If the plan-mode refusal repeats**, it is a lane defect, not an H5263 one. It needs a decision on the
   `--permission-mode plan` argv. H3157's safe-mode arm (`SAFE_MODE_FLAG`) is the documented
   mitigation, and turning it on is an operator choice, not something an agent may set itself.

_Гасунс_
