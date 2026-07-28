# PWG→RU finish brief — what to do, in what order, with exact files

_Created: 28-07-2026 · Last updated: 28-07-2026_

**Handoff:** [H1778](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1778-Grok_SanskritLexicography_pwg-ru-finish-action-brief_28.07.26.md) · Model: Grok 4.5 (`grok-4.5`)

---

## DO THIS FIRST (≤20 min)

Open and vote **one** sheet — the shortest unlock:

1. Open [g6_mqm_starter_sheet.html](file:///C:/Users/user/Documents/GitHub/SanskritLexicography/RussianTranslation/review/g6_mqm_starter_sheet.html)
2. Vote all **20** cards (~15–20 min)
3. Type your name in Reviewer
4. **Save to folder…** →  
   `C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\review\g6-mqm-gold-starter-2026-07-25_decisions.json`
5. Stop. Tell an agent: *“apply G6 decisions”*

That is the entire first session. Everything else waits.

**Why this first:** G6 is the gold instrument. Gold cut [H1665](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1665-Fable_SanskritLexicography_pwg-store-gold-cut-execute-r1-r5_26.07.26.md) cannot run without it. Manual: [REVIEW_GOLD_VOTING_DEEP_MANUAL.md §8](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/REVIEW_GOLD_VOTING_DEEP_MANUAL.md).

---

## STATE (one screen)

| Fact | Number | Meaning |
|---|---:|---|
| Store rows now | **11 603** | Pilot, not the whole dictionary |
| Human-approved | **3** | Almost nothing is gold |
| Still `ai_translated` | **11 598** | Machine-preview label is correct |
| Unique `key1` clusters | **254** | Root/lemma families only |
| Full PWG entries | **~123 366** | Finish line for “whole book” |
| Quality claim | **machine-preview** | Ruled 17-07-2026 — not print-grade |
| Paid bulk drain | **blocked** | Needs fresh live-gate GO (health / rate_limit) |

**Wins already banked (do not re-do):**

- Pipeline, TM, stripped-config economy (~−66% call cost)
- Controller–worker canary code shipped
- Voting-queue triage ruled (A2 / Б / В2) — you do **not** vote 49k or 90 re-asks
- Abbrev sheet collapsed 273 → **33** cards (H1682)
- Compound agent adjudicated all ~4.2k rows; you only verify arms

---

## PICK A FINISH LINE (one choice)

| Finish line | What “done” means | Human time left | Money (API) | Do you need this? |
|---|---|---|---|---|
| **A — Machine-preview book** | Most PWG rows as `ai_translated`, labelled AI | ~0 per card; operator restarts only | **tens of $k** at scale | Default / ruled path |
| **B — Policy + sample gold** | Style, abbrev, G6, G5 sample, compound arms voted | **~8–15 h** browser voting | Low (agent apply) | Needed for better future bulk + print path start |
| **C — Print every sense** | Human approve each row | **hundreds–thousands of hours** | High | **Not chosen** (D2) |

Ruled quality bar: [DECISIONS_PWG_RU_QUALITY_BAR.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DECISIONS_PWG_RU_QUALITY_BAR.md)  
D1: per-cohort bars · D2: **machine-preview, not production-grade**.

---

## HUMAN VOTES — DO NOW (≤5 items)

Do these in order. Save each `decisions.json` to the path shown. One sheet per sitting is fine.

| # | Sheet (open) | Cards | Time | Save as | Unlocks |
|---:|---|---:|---:|---|---|
| 1 | [g6_mqm_starter](file:///C:/Users/user/Documents/GitHub/SanskritLexicography/RussianTranslation/review/g6_mqm_starter_sheet.html) | 20 | **15–20 min** | `review\g6-mqm-gold-starter-2026-07-25_decisions.json` | Gold cut H1665 |
| 2 | [h1306_style](file:///C:/Users/user/Documents/GitHub/SanskritLexicography/RussianTranslation/review/h1306_style_sheet.html) | 9 | **10–20 min** | `pwg_ru\eval\h1306_style.decisions.json` | Prompt rules phase 2 of H1306 |
| 3 | Abbrev: prefer **h1682** 33 cards if present; else [h1303_abbrev](file:///C:/Users/user/Documents/GitHub/SanskritLexicography/RussianTranslation/review/h1303_abbrev_sheet.html) | 33 | **45–90 min** | `pwg_ru\eval\h1303_abbrev.decisions.json` or h1682 twin | `RU_MAP` + ABBREVIATIONS_RU |
| 4 | [compound arm1 stratified200](file:///C:/Users/user/Documents/GitHub/SanskritLexicography/RussianTranslation/review/sanskritlexicography-pwg-compound-differs_stratified200_review.html) | 200 | **60–90 min** | `review\sanskritlexicography-pwg-compound-differs_stratified200_decisions.json` | ~3.1k compound rows (one stratum) |
| 5 | [compound arm2 rulestrat](file:///C:/Users/user/Documents/GitHub/SanskritLexicography/RussianTranslation/review/sanskritlexicography-pwg-compound-differs_rulestrat_arm2_review.html) | 232 | **70–100 min** | `review\sanskritlexicography-pwg-compound-differs_rulestrat_arm2_decisions.json` | Remaining compound strata |

### How to vote (every sheet)

1. Open the `file:///` link above in a browser (Chrome/Edge).
2. For each card: Approve / Reject / Defer (labels are on the sheet header).
3. Fill **Reviewer**.
4. **Save to folder…** into the path above (exact filename).
5. Do **not** edit the store by hand.
6. Next session for agent:

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\<H###>.md and execute it.
```

Or short: *“apply decisions from `<path-to-decisions.json>`”*.

### Vote meanings (copy next to your screen)

| Sheet | Approve | Reject |
|---|---|---|
| G6 MQM | LLM gold label is right | First word of note = correct label from the 6-label set |
| Style h1306 | Exactly **one** option per question (A1/B1/C1 recommended) | Other option |
| Abbrev | RU form for that rule/token | Leave Latin / different form |
| Compound arms | PWG split is right | Index split is right |

**Style recommendations (if you trust the memo):** A1 · B1 · C1 — [STYLE_RESEARCH_DOUBLETS_VL_COMP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/STYLE_RESEARCH_DOUBLETS_VL_COMP.md)

---

## HUMAN VOTES — LATER (not today)

| Sheet | Cards | Time | When | Path |
|---|---:|---:|---|---|
| [g5_batch1v3](file:///C:/Users/user/Documents/GitHub/SanskritLexicography/RussianTranslation/review/g5_batch1v3_sheet.html) | 150 | **2–4 h** | **After G6** | Save `review\g5-live-queue-batch1v3-2026-07-26_decisions.json` |
| h180 typology + learner + reglue | ≤148 | **2–4 h** | After rescreen residue (agent H1650) | `pwg_ru\eval\h180_*.decisions.json` |
| Renou pilot v2 | 70 | **1–2 h** | Separate programme | `review\` export |

**Do not open these (retired / agent path):**

| Sheet | Why skip |
|---|---|
| `h178_mqm` / `likert` / `pairwise` | **Retired** — same 30 cards as voted `h178_da` |
| `g5_batch1` (old) | **Aborted** — use **v3** only |
| `h1303` 273-card framing | Superseded by **33-card** rule collapse; do not re-vote 273 |
| ACC×NCC 49k sheet | Agent already adjudicated; human only the **698** spot-check if you care about that lane (not bulk PWG translate) |

Triage source: [VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md)

---

## AGENT WORK YOU CAN START WITHOUT VOTING

### 1) Apply a vote you just finished (~5–15 min agent)

```
cd C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation
python src/apply_decisions.py <path-to-decisions.json>
```

(If that entrypoint differs, agent uses `/decisions-apply`.)

### 2) Live-gate before any paid drain (~2 min)

```
# From RussianTranslation, after profiles exist:
# Skill: /pwg-live-gate c4
# Must PASS fresh health ≥5 KB — stale GO from last week does NOT authorize spend
```

**If NO-GO:** stop. Do not open medium50. Fix is auth/rate_limit/host, not more code.

### 3) Economy route for paid calls (when GO)

- Use **stripped** `CLAUDE_CONFIG_DIR` (auth only) — [H1517 report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1517/H1517_STRIPPED_CONFIG_ECONOMY_SAMPLE_2026-07-22.md)
- Budget: **~$0.14–0.25 per card** (retry doubles cost)
- Always `--stop-before-promote` on first window of a session
- Never promote on a health-fail run

### 4) Starter lines for open agent handoffs

G6/G5 done → gold cut:

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H1665-Fable_SanskritLexicography_pwg-store-gold-cut-execute-r1-r5_26.07.26.md and execute it.
```

Style vote saved → H1306 phase 2:

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md and execute it.
```

Abbrev vote saved → H1303 session 2:

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H1303-Fable_RussianTranslation_pwg-ru-abbrev-unified-list-ratification_19.07.26.md and execute it.
```

Paid fidelity validation (code already merged):

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H858-Opus_SanskritLexicography_pwg_ru_sense_fidelity_anchor_repair_13.07.26.md and execute it.
```

Bake-off compute after da + agent arms:

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H274-Fable_DO_RussianTranslation_pwg_ru_bakeoff_compute_07.07.26.md and execute it.
```

Controller residual (medium50 after live GO):

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H1209-Opus_SanskritLexicography_pwg-ru-controller-worker-canary_17.07.26.md and execute it.
```

---

## COST — ACTABLE NUMBERS

### Money (API / Max)

| Scenario | Formula | Rough total |
|---|---|---|
| One medium50 window | ~50 cards × $0.15–0.30 | **$8–15** |
| Next 1 000 cards | 1000 × $0.20 | **~$200** |
| Full PWG sense-scale (order 10⁵ cards) | 1e5 × $0.15–0.30 | **$15k–$30k** |
| Full PWG if retries/malformed high | ×1.5–2 | **$25k–$60k** |

TM hits = free re-emit (no agent call). Pilot TM already reuses identical sources.

**Not free:** human calendar around serial control plane (generation only ~12–22% of wall time — [H1403](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1403-Fable_RussianTranslation_pwg-ru-speed-orchestration-audit_20.07.26.md)).

### Human time (Finish line B only)

| Block | Minutes |
|---|---:|
| G6 | 15–20 |
| Style | 10–20 |
| Abbrev 33 | 45–90 |
| Compound 200 | 60–90 |
| Compound 232 | 70–100 |
| G5 150 (after G6) | 120–240 |
| **Subtotal core** | **~5–9 h** |
| + h180 + Renou optional | +3–6 h |

Split: **one sheet per sitting**. Never batch 432 compound cards in one night if that burns you out — arm1 and arm2 are independent.

### What you should **not** spend human time on

1. Re-judging rows a dataset already decided (compound agent strata already ruled; you only verify arms).
2. Voting store defects D1/D3/D4 — auto-reject into repair (H1651).
3. Full-store G5 on 11 598 rows — sample only (G5 batch), not census.
4. Re-running retired h178 arms.

---

## HANDOFFS — WHAT IS OPEN VS DONE

### Still open / partial (pwg_ru-critical)

| ID | Status | Your action |
|---|---|---|
| [H1665](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1665-Fable_SanskritLexicography_pwg-store-gold-cut-execute-r1-r5_26.07.26.md) | Queued · gated on G6 (+ G5 path) | Vote G6 first |
| [H1306](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md) | Phase 1 ✅ · phase 2 waits vote | Vote 9 cards |
| [H1303](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1303-Fable_RussianTranslation_pwg-ru-abbrev-unified-list-ratification_19.07.26.md) | Session 1 ✅ · session 2 waits vote | Vote 33 cards |
| [H180](https://github.com/gasyoun/Uprava/blob/main/handoffs/H180-Opus_RussianTranslation_pwg_ru_addenda_typology_glue_learner_05.07.26.md) | Builders ✅ · sheets unvoted | Later |
| [H1209](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1209-Opus_SanskritLexicography_pwg-ru-controller-worker-canary_17.07.26.md) | Partial | Live GO + medium50 |
| [H858](https://github.com/gasyoun/Uprava/blob/main/handoffs/H858-Opus_SanskritLexicography_pwg_ru_sense_fidelity_anchor_repair_13.07.26.md) | Code ✅ · paid validation ⏸ | After live GO |
| [H274](https://github.com/gasyoun/Uprava/blob/main/handoffs/H274-Fable_DO_RussianTranslation_pwg_ru_bakeoff_compute_07.07.26.md) | Queued | After da path released (A2 done) |
| [H255](https://github.com/gasyoun/Uprava/blob/main/handoffs/H255-Sonnet_RussianTranslation_pwg_ru_no_pwg_lane_scale_06.07.26.md) | **FROZEN** | Do not unfreeze without explicit order |
| [H151](https://github.com/gasyoun/Uprava/blob/main/handoffs/H151-Sonnet_RussianTranslation_pwg_ru_verb_batch_drain_04.07.26.md) | **Legacy / skip** | Do not pick |
| [H215](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md) | Agent slices mostly done | FAIR clearance = human `@DO` residual |

### Done examples (do not re-open)

H1517 economy · H1403 speed audit · H1313 sheet standard · H1681 compound agent adjudicate · H1682 abbrev collapse · H1655 G5 German gate · H1657 ACC×NCC agent · many DE-layer handoffs (H1628–H1635 family) — see registry archive.

---

## VOTING RULE (one standard)

**One sheet UX standard** (csl-pyutil V1–V8). **Not** one human judgment per store row.

| Class | Who decides | Human load |
|---|---|---|
| **A** agent-ruleable | Dataset / code | 0 |
| **HY** hybrid | Agent all rows + human stratified arm | Sample only |
| **H** human-only | You | Full sheet |

Rule text: GTD 26-07-2026 «A2 · Б · В2» + screening audit §9-bis / §11.

**Check before any new sheet is built:** “Can a dataset or LLM decide this with cited evidence?” If yes → HY or A, never dump 10k cards on you.

---

## BLOCKERS (if stuck)

| Symptom | Cause | Fix |
|---|---|---|
| Live drain dies / rate_limit | Profile health / session limit | Fresh `/pwg-live-gate`; wait; do not burn money |
| G5 shows German | Old sheet | Use **g5_batch1v3 only** |
| validate_decisions rejects export | Unstamped sheet | Compound arms were re-bound H1703 — use current HTML |
| Want full print quality | Wrong finish line | Stay on **A/B**; C is multi-year human labour |
| Foreign-route GTD row | Optional multi-account diagnostic | Not required for c4 single-profile path |

---

## CHECKLIST — PRINT OR PIN

```
[ ] Vote G6 (20)           → ~20 min
[ ] Vote style (9)         → ~15 min
[ ] Vote abbrev (33)       → ~60 min
[ ] Vote compound arm1     → ~75 min
[ ] Vote compound arm2     → ~85 min
[ ] Agent applies each decisions.json same day if possible
[ ] Only then: G5 v3 (150)
[ ] Only with live GO: paid medium50
[ ] Never: vote retired h178 arms / 49k ACC sheet / full 11k G5
```

---

## SOURCES (open when you need proof)

| Need | Link |
|---|---|
| This programme journal | [RussianTranslation/.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md) |
| Quality rulings | [DECISIONS_PWG_RU_QUALITY_BAR.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DECISIONS_PWG_RU_QUALITY_BAR.md) |
| Sheet index | [REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md) |
| Vote screening | [VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md) |
| Human Do Today rows | [GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) |
| Gold voting manual | [REVIEW_GOLD_VOTING_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/REVIEW_GOLD_VOTING_DEEP_MANUAL.md) |
| Economy sample | [H1517](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1517/H1517_STRIPPED_CONFIG_ECONOMY_SAMPLE_2026-07-22.md) |

---

## NEXT AFTER YOU FINISH THIS DOC

Open the G6 sheet and vote card 1:

[file:///C:/Users/user/Documents/GitHub/SanskritLexicography/RussianTranslation/review/g6_mqm_starter_sheet.html](file:///C:/Users/user/Documents/GitHub/SanskritLexicography/RussianTranslation/review/g6_mqm_starter_sheet.html)

_Dr. Mārcis Gasūns_
