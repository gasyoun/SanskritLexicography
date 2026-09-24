_Created: 24-09-2026 · Last updated: 25-09-2026_

# H5263 — NKRYa evidence block in the c1 PWG-RU prompts: build done, A/B NOT RUN

**Verdict: BUILD SHIPPED, A/B BLOCKED. 0 of the 5 pre-authorized paid c1 calls spent — the
budget is untouched and still authorized.** The keep/drop recommendation the handoff asks for
cannot be earned from 0 calls, so this report names what the block does, what it costs in
prompt bytes, and the two gates that stand between here and the A/B.

**Try 2 (25-09-2026) re-measured both gates: gate 1 is GONE, a third gate was found, and the
handoff's named stop («stop after 2 tries») is now reached with the budget still at 0/5.**
See [§ Try 2](#try-2--25-09-2026-gate-1-cleared-gate-3-found-named-stop-reached) at the end.

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

## What unblocks the A/B

1. **MG generates the non-expiring NKRYa key** at [ruscorpora.ru for-devs](https://ruscorpora.ru/accounts/profile/for-devs)
   and it is stored on this box (`python -c "import keyring,getpass; keyring.set_password('ruscorpora-api','token',getpass.getpass())"` — it never enters chat or git).
   *If done:* the evidence block can be built for any card, and the A/B becomes a ~1 h run.
   *If not:* H5263's A/B half stays parked; the build half above is already live and inert.
2. **A fresh `/pwg-live-gate` GO on c1**, then the msg_ id route check, then the 5 calls.

## Try 2 — 25-09-2026: gate 1 cleared, gate 3 found, named stop reached

Same handoff, second executor pass (Opus 5 `claude-opus-5[1m]`, **0 paid c1 calls, 0 live NKRYa
calls**). The handoff's stop condition is «stop after 2 tries»; this is try 2, so the A/B half
closes here and goes back to a human with the three gates measured rather than assumed.

### Gate 1 (the NKRYa token) is GONE — for the A/B's two cards

Between try 1 and try 2 the evidence was fetched **on the Mac**, where the token lives, and
committed: [`pwg_ru/h5263/evidence_han.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5263/evidence_han.json) and
[`pwg_ru/h5263/evidence_yat.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5263/evidence_yat.json) (14 live NKRYa calls there, plus the new
`pwg_ru/nkrya_cache` entries), with [`tools/h5263_ab_evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h5263_ab_evidence.py) `inject` replaying them
offline. **The Windows box no longer needs a NKRYa token to run this A/B** — the cards were
chosen precisely so it would not (`han~~h0_57_sam_0` = the C07 clouds collocation, MG's own
«тучи сгущаются»; `yat~~h0_01_sec_1` = the C02 non-word `союзить`), and both carry an MG-voted
gold rendering from the H5069 chat vote, which is what the scoring compares against.

### Gate 3 (new, and the one that actually stops the run): the two cards have no prepared inputs

This was never named before, so try 1's plan («a ~1 h run once the key exists») was wrong.
The paid call needs a validated execution manifest, and a manifest needs the card's ingested
inputs. Measured this pass, on this box:

1. `python src/pilot/gen_opt_harness2.py han --keys=han~~h0_57_sam_0 …` → `FAIL: no rootmap
   for 'han'`. Same for `yat`.
2. `src/pilot/input/` (the gitignored ingest output, read in the **main checkout**) holds 1077
   files and **exactly one** `*.rootmap.json` — neither `han.rootmap.json` nor `yat.rootmap.json`,
   and no `han~~*` / `yat~~*` `raw.txt` / `portrait.json` pair anywhere in the repo.
3. So building the two arms' manifests means running the ingest/prepare path over the PWG dump
   through the `coordinator.py` lease flow — the same "unfamiliar lease/promote machinery under a
   live paid clock" H3791 refused to improvise on 02-09-2026, and the reason this pass did not
   improvise it either inside a 45-minute unit on a money-class handoff.
4. The card content itself is **not** missing — [`pwg_ru/h5069/sample30.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5069/sample30.jsonl) carries
   `han~~h0_57_sam_0` with `source_string` (German) and `target_string` (the store rendering), and
   [`src/pilot/h1210/h2591/execution_manifest.h2591.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/h2591/execution_manifest.h2591.json) is a real production prompt
   donor (1226 B preamble + 12 423 B translation rules). What is missing is the **masking** half:
   a production skeleton is `{Tn}`-masked with `placeholder_maps` / `fragment_placeholder_maps`
   built by the prepare path, and a hand-assembled substitute would change the very prompt shape
   the A/B is supposed to measure.

### Gate 2 (the live gate) is still shut, and was NOT probed

`src/pilot/generation_api_probe_log.jsonl`: the newest gate verdict is **GO 2026-08-28T14:20:51Z**
(`production_v3`) — nothing for 24-09 or 25-09. The gate probe is itself a paid call and is
rationed (≥6 h spacing, ≤2 attempts/UTC day), so with gate 3 standing it was deliberately **not**
spent: a GO that cannot be exploited inside the unit would burn part of a non-renewable,
pre-authorized 5-call budget on nothing. **Budget after try 2: 0/5.**

### Keep / drop — still no recommendation, and that is the honest answer

Nothing in try 2 measures the benefit side, so the try-1 position stands unchanged: cost
**+1533 bytes of volatile per-card prompt** at C07 density (never cached, paid on every call),
benefit unmeasured. What try 2 adds is that the *cheap* part of the A/B (evidence) is done and
committed, and the *expensive* part is an ingest run, not an API key.

### What a human must decide (the A/B half of H5263 goes back on the desk)

1. **Authorize the ingest prepare for the two cards** (`han`, `yat`) — one lease through
   `coordinator.py prepare`, 0 paid calls, ~30–60 min of agent time — and the A/B becomes
   `/pwg-live-gate` + 4 calls (2 cards × with/without evidence), inside the 5-call cap.
   *If done:* the keep/drop verdict arrives with per-card diffs against MG's own gold renderings.
   *If not:* the build half stays live and inert (every manifest without an `nkrya` input is
   byte-identical), and the 5 calls stay authorized indefinitely.
2. **Or re-scope the A/B onto a card that already has prepared inputs**, accepting that no MG
   gold rendering exists for it — cheaper, and measurably weaker evidence.

_Гасунс_
