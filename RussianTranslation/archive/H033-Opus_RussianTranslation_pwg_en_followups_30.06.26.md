# Handoff — PWG→English follow-ups (after the 16-root pilot)

**For:** a fresh agent session (or the autonomous account). **Context:** the PWG→English
track is wired and pilot-proven on the 16 Slice-C roots (2026-06-30). This doc is the
resume point for the three remaining follow-ups. Everything below lives in
`SanskritLexicography/RussianTranslation/`, branch `recover/slicec-top3-pat-ga-vad`
([PR #25](https://github.com/gasyoun/SanskritLexicography/pull/25)).

> **Status (2026-06-30):** ✅ **FU2 SHIPPED** —
> [`src/pilot/audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/src/pilot/audit_window_en.py)
> (report-only; 0 hard flags over all 16 pilot roots), wired into `save_and_audit.py` (tag `en`).
> ✅ **FU3 SHIPPED** —
> [`src/promote_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/src/promote_en.py)
> (German-text fuzzy join; 2417 store rows now carry `en`, `dcs_freq` re-annotated).
> ⏳ **FU1 PLANNED, not yet run** — all six design decisions MG-locked 2026-06-30; full spec +
> 30-root worklist (1,260 subcards, ~$42 Sonnet) in
> [`FU1_PLAN.md`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/FU1_PLAN.md).
> Summary: EN-only on the already-RU'd roots + merge (bilingual single-pass reserved for future
> roots); Sonnet generate + Opus judge; scope = match RU coverage; validation = audit + judge +
> human gold sample (ground truth = faithful to the PWG German); full per-sense provenance. Build
> the Opus EN judge + provenance-aware merge + gold sampler (no quota) before the Max run.

## ⚠️ Read first — environment + coordination

- **Check your branch before committing:** `git rev-parse --abbrev-ref HEAD` must be
  `recover/slicec-top3-pat-ga-vad`, NOT `master`. A handoff-revert once silently left the
  checkout on `master` and pwg commits landed there; recovered by FF-moving the branch +
  `reset --hard origin/master`. The translated outputs (`wf_output*.json`, the stores, the
  `*.json` freq tables) are **gitignored, regenerable artifacts** — commit only code/docs.
- **csl-orig is READ-ONLY** (`mw.txt`, `pwg.txt`): extract from it, never modify/stage it.
- A second (autonomous) account also works pwg on this branch/master — announce, don't
  double-run a root, prefer PR-only.
- **≤3-wide Workflow concurrency** for Max harness runs (Slice-D's 18× fan-out caused a
  117-null collapse; single/low-width = 0 nulls). Run roots sequentially or ≤3 at a time.
- **Workflow scriptPath limit = 512 KB.** Big roots (DA = 145 cards) exceed it — split into
  two harnesses via `--keys=<half>` (see DA_a/DA_b below).

## How the EN pipeline works (already built — verify, don't rebuild)

- **Harness:** `python src/pilot/gen_opt_harness2.py <root> --lang en --out=src/pilot/run_pilot_wf.en_<root>.js`
  - Uses `src/pilot/tr_en.txt` (self-contained scholarly-literal EN prompt), per-sense field
    `english` (schema + JS restore auto-swapped), injects an MW REFERENCE block once per root.
  - **The RU path (`--lang ru`, default) is byte-for-byte unchanged** — regression-checked.
    EN harness passes `node --check`.
  - `--mw-tm=PATH` overrides the MW feed (default `src/mw_en_tm.json`).
- **MW translation-memory:** `python src/mw_en_tm.py` → `src/mw_en_tm.json` (187,506 SLP1-keyed
  English glosses from read-only `../../csl-orig/v02/mw/mw.txt`; `<k1>` is already SLP1).
  MW is partly descended from PW/PWG → strong TM. Hybrid: MW candidates injected, the LLM
  adjudicates against the German + corpus, follows PWG's sense order.
- **Headword crosswalk EXISTS — don't rebuild:** `HeadwordLists/union/union_headwords.tsv`
  (SLP1-keyed, `dicts` column) gives **94,753 PWG∩MW** headwords.
- **Run loop:** generate harness → run via in-chat Workflow tool (≤3-wide) → save:
  `python save_and_audit.py <root> <task-output-file> en --no-audit` → `wf_output.en.<root>.json`.
  (`--no-audit` because the deterministic `audit_window.py` is RU-tuned — see follow-up 2.)
- **Pilot state:** all 16 Slice-C roots done — `wf_output.en.{pat,gA,vad,Sam,Buj,vraj,Bid,pA,
  Cid,yat,naS,yaj,rakz,hi,mad,DA}.json` (685 sub-cards, 663 non-null; ~22 nulls = stubborn
  head cards). German-residue 3/2906 senses (0%).
- **Tri-lingual view:** `python src/pilot/trilingual_sample.py <root>` (or `--all --out FILE`)
  joins `wf_output.sc.<root>` (de+ru) + `wf_output.en.<root>` (de+en) by sub-card key+sense.
  Sample committed: `PWG_EN_PILOT_2026-06-30.md`.

## Follow-up 1 — full DCS-frequency-ordered EN run (beyond the 16 pilot roots)

Scale EN to the rest of the frequency queue, same as the RU bulk run.
- The freq manifest is `src/pilot/output/scale_manifest.freq.json` (DCS-freq order; built by
  `python src/freq_route.py N`). The 16 done roots are the Slice-C set; the next roots follow
  the manifest. Confirm a root is structurally ready first:
  `python src/pilot/root_window_status.py <root>` (rootmaps + masked inputs under
  `src/pilot/input/` must exist; if missing, `python src/_pilot_gen_merged.py --manifest freq
  --root-split --limit N`).
- Per root: `gen_opt_harness2.py <root> --lang en --out=...en_<root>.js` → Workflow (≤3-wide)
  → `save_and_audit.py <root> <out> en --no-audit`. Split any harness >512 KB by `--keys`.
- **Real Max-quota spend** — coordinate scope with MG first (how many roots / which slice).
- DA pattern for oversized roots (reuse): split keys in half from the rootmap, two harnesses,
  save the first then `save_and_audit.py DA <out2> en --merge --no-audit` to combine.

## Follow-up 2 — EN-specific audit gate

`src/pilot/audit_window.py` (the deterministic gate: NWS owner-map, markup fidelity, sense
coverage, sense-duplicate) and `prompt_rule_audit.py` have **Russian-specific** semantic
checks (e.g. `untranslated_german_residue`, Russian register), so the pilot used `--no-audit`.
What IS already enforced for EN: the harness's in-JS fidelity guard (nulls any card whose
restored `<ls>`/`{#..#}` counts don't match source — language-agnostic) + a German-residue
spot check (3/2906 = 0%).
- **Task:** add a `--lang en` path to the audit (or a sibling `audit_window_en.py`) that keeps
  the language-agnostic gates (markup fidelity, coverage, sense-dup, NWS owner-map) and swaps
  the RU semantic checks for EN ones (German/Russian residue in the `english` field, circular
  gloss, sigla-kept, MW-divergence flag as a soft QA signal — MW is the gold cross-check MG
  chose). Keep it report-only by default.
- The `english` field is where RU's `russian` was; `german` (source) is unchanged. Reuse the
  RU gate code; only the per-sense target field name and the residue language flip.

## Follow-up 3 — merge EN into a single tri-lingual store

Today RU lives in `src/pwg_ru_translated.jsonl` (per-sense `ru`, via
`src/promote_final_cards.py`) and EN lives in the per-root `wf_output.en.<root>.json`. Goal: one
store carrying `de` + `ru` + `en` per sense (+ the `dcs_freq` block already added by
`annotate_dcs_freq.py`).
- **Approach:** extend `promote_final_cards.py` (or a sibling `promote_en.py`) to also read the
  `wf_output.en.*.json` and attach each sense's `english` onto the matching RU store row. Join
  key = (sub-card key `subkey`, sense index/tag) — the store row already carries `subcard`; the
  EN card's senses align positionally with the RU card's (same masked skeleton, same order).
  Watch the ~22 EN nulls and the few RU nulls — leave the missing-language field absent, don't
  fabricate.
- Keep `review_status='ai_translated'` (G5 gate). The freq annotation step is language-agnostic
  and already runs after the bridge — re-run `annotate_dcs_freq.py` after the merge.
- Then `trilingual_sample.py` can read the single store instead of two file sets (optional
  cleanup).

## Pointers

- EN harness: [`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/src/pilot/gen_opt_harness2.py) (`--lang en`) ·
  prompt [`src/pilot/tr_en.txt`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/src/pilot/tr_en.txt)
- MW TM: [`src/mw_en_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/src/mw_en_tm.py) → `src/mw_en_tm.json` (gitignored)
- save/merge: [`save_and_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/save_and_audit.py) (`en` tag, `--no-audit`, `--merge`)
- RU bridge to extend: [`src/promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/src/promote_final_cards.py)
- freq annotation: [`src/annotate_dcs_freq.py`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/src/annotate_dcs_freq.py) (+ `build_dcs_freq.py`,
  `build_dcs_freq_dims.py`)
- tri-lingual: [`src/pilot/trilingual_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/src/pilot/trilingual_sample.py) ·
  sample [`PWG_EN_PILOT_2026-06-30.md`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/PWG_EN_PILOT_2026-06-30.md)
- loop/concurrency doctrine: [`src/pilot/RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/src/pilot/RUN_FREQ_MAX.md)
- prior Slice-C recovery handoff: [`HANDOFF_2026-06-30_slicec_recovery.md`](https://github.com/gasyoun/SanskritLexicography/blob/recover/slicec-top3-pat-ga-vad/RussianTranslation/HANDOFF_2026-06-30_slicec_recovery.md)
