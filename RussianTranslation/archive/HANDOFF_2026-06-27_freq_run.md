# Handoff — launch the first REAL freq-queue window (pwg_ru on Max/Sonnet)

Cold-start brief for the next chat. Scope: **start the real PWG→Russian bulk run**
with the now-locked, token-optimized harness, run-to-cap, and instrument cost.
The proving ground (`tyaj`) is done; this is the first *production* window.

> Read first: [`TOKEN_OPTIMIZATION_2026-06-27.md`](TOKEN_OPTIMIZATION_2026-06-27.md)
> (why/how the run was re-architected + all findings) and [`CHANGELOG.md`](CHANGELOG.md)
> §2026-06-27. Cost model: [`PILOT_COST.md`](PILOT_COST.md) §6.

---

## State — everything upstream is GREEN and committed

- **Harness LOCKED** (commits `5b54e1c` · `ce7a1dd` · `e3dc6a6`). Translate-only,
  single-turn, inputs inlined; per-card LLM judge dropped for free Python gates.
- **Measured ~3.2× lower `cache_read`** (the real Max-quota driver), 0 transient
  failures (1 auto-retry/stage). A/B on tyaj: 19 cards, 640 k tok, 3.4 min.
- **Head lane correct:** giant heads sense-split at `<div n=>` by `<ls>` density
  (`HEAD_CIT_BUDGET=18`); both lanes inline-only (no over-production); causatives
  tagged `caus. N`.
- **4 deterministic gates, all free:** `audit_translation.py` (markup fidelity),
  `audit_coverage.py` (dropped/fabricated senses), `nws_split.py` (NWS owner map),
  `audit_sense_dupes.py` (cross-part duplicate senses — NEW).
- **The harness runs FROM-CHAT** via the Workflow tool (inlined inputs, no
  `node:fs`). The old "needs a human-driven Max session" caveat is obsolete.

## The one thing still UNMEASURED

The **absolute Max weekly-quota number** — we have a solid *relative* 3×, but
never ran until the cap fires. This window's job is to get that number, which
turns "weeks-not-days" from direction into `weeks = total ÷ measured_quota`.

## Run procedure (per giant root; repeat down the freq queue)

The freq queue top = `sTA, BU, gam, yuj, as, i, vid, han` — all **giant verbal
roots** (hundreds of sub-cards each). `gen_opt_harness.py` inlines **one root**'s
sub-cards per harness file, so run root-by-root.

```powershell
cd RussianTranslation\src

# 1. (Re)generate this root's split inputs if needed (idempotent; skips existing).
#    To force a re-split after a splitter change: delete src/pilot/input/<root>~~* first.
python _pilot_gen_merged.py --root-split sTA

# 2. Generate the optimized harness for this root (writes src/pilot/run_pilot_wf.opt.js).
python pilot\gen_opt_harness.py sTA
```

3. **Run it** via the in-chat **Workflow tool**:
   `Workflow({scriptPath: "…/RussianTranslation/src/pilot/run_pilot_wf.opt.js"})`.
   Save the result's `results` array as `wf_output.json`
   (`{"results": [...]}`, indented).

4. **Gate it (all 4, all free):**
```powershell
python src\audit_sense_dupes.py wf_output.json                 # cross-part dup senses
python src\pilot\run_real_test.py audit wf_output.json          # NWS owner map + render
python src\audit_translation.py src\pilot\output\scale_manifest.smoke.json   # markup fidelity
python src\audit_coverage.py  …                                 # dropped/fabricated senses
```
   (build `scale_manifest.smoke.json` = `[{"key1": <each result key>}]` of the
   cards that returned, as in the tyaj runs.) Any flagged card = re-queue, not accept.

5. **Glue:** `python src\root_glue_translated.py sTA` → `pilot\output\sTA.NESTED.md`.

6. **Instrument** (the point of the run): append to [`PILOT_COST.md`](PILOT_COST.md)
   §6 — per root: cards, `cache_read`/`cache_create`/output tokens (from the agent
   transcripts under `…/subagents/workflows/wf_*/agent-*.jsonl`), wall-clock,
   and whether/when the **Max weekly cap fired** + cumulative tokens at that point.

## Scope decision to make at the top of the chat

Each giant root ≈ a few hundred k → low-single-M tokens (tyaj's 14→19 sub-cards
was 640 k; sTA/BU/gam are larger). Options:
- **Conservative:** one giant root, gate + glue + cost it, then stop and read the
  number before continuing. (Recommended for the first real window.)
- **Run-to-cap:** keep running roots down the freq queue until the Max weekly cap
  fires — yields the full quota number in one push, but a big token commit.

## Gotchas / notes (so they're not re-discovered)

- `gen_opt_harness.py` is **per-root** (inlines that root's sub-cards). A
  multi-root window would need it extended to accept several roots — currently
  loop it per root. (Small TODO if a batched window is wanted.)
- ~10–20 % transient `Connection closed mid-response` / `ConnectionRefused` — the
  harness auto-retries once; a card that still returns null re-queues. An API
  outage can wreck a whole run (happened 2026-06-27) — just re-run.
- The `.opt.js` / `.run.js` harness files are **gitignored** (derived; regenerated
  per root). Don't commit them.
- Cologne policy reminders (already in the harness prompt, verify don't re-add):
  German abbrevs `Bed.`/`Schol.` verbatim; render every Nachträge patch; `<is>`
  italics → siglum not `{%…%}`; preserve PWG sense order (Renou = badge).
- **Run-start TODO:** wire `audit_sense_dupes.py` into the run loop next to the
  other gates (currently invoked manually).

## Track B (unchanged, secondary) — flagship sign-offs still open

`agni` + `akṣara` human sign-off gates remain (see the prior handoff
[`HANDOFF_2026-06-25_pwg_ru_max.md`](HANDOFF_2026-06-25_pwg_ru_max.md) Track B).
Not blocking the freq run.
