# Handoff roadmap — pwg_ru on Max + lock the comparison flagship (2026-06-25)

A cold-start brief for the next chat. Scope set with the user 2026-06-25.
Primary = **scale PWG→Russian on the Max harness**. Secondary = **lock the
article-comparison flagship 1+1 pair and finish its Russian to 100 %**. The
SamudraManthanam `#sa` corpus fix is **maintainer-owned — not on this roadmap**.

---

## Track A (PRIMARY) — PWG→Russian bulk run on Max

**Decision (locked 2026-06-24):** the production vehicle is the **Max
subscription**. DeepSeek / judge-sampling are kept for **A/B testing only**, not
the real run. (See `Uprava/GTD_NEXT_ACTIONS.md` → SanskritLexicography.)

**Where it stands:**
- Frequency-first order built: `src/freq_route.py` → `scale_manifest.freq.json`
  (gitignored; **43,968 / 106,083 = 41 % DCS-attested**; band-5 = 641, band-4 =
  3,170 → ~3.8 k core). Top of the queue = giant verbal roots (sthā/bhū/gam).
- Giant-root failure SOLVED: `_pilot_gen_merged.py --root-split` (composes with
  `--manifest freq`) explodes a giant root into single-pass sub-cards +
  `<safe>.rootmap.json`; `src/root_glue_translated.py` re-collects them into one
  NESTED article. Head-card sense-splitter handles the 820-line heads. Audited
  all-green (lossless, all-homonyms-split, glue-complete).
- a-section inputs **owner-map-ready** (`_pilot_gen_merged.py --manifest a` →
  4,264 regenerated with the authoritative NWS owner map; `run_pilot_wf.js`
  owner-map-aware via HARD RULE 5 + Guard 7).
- **38-unit freq test RUN + audited** (2026-06-24): 38 Sonnet agents, 10.5 min,
  1.61 M tok → glued `man` 30/30 (publishable; Apresjan register-judgment
  validated). Fidelity gate `src/audit_translation.py` = **38/38 clean**.

**Resume steps (do in order):**
1. ✅ **Opus 4.8 judge pass is done** (recorded 2026-06-26): severity
   **{1:24, 2:13, 3:1} → 37/38 publishable**; the lone sev-3 is the idam
   NWS-owner-row swap class that the deterministic owner gate is meant to catch.
2. **Run the freq queue on Max with `--root-split`**, window by window, per
   [`src/pilot/RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md): refresh/verify the
   freq manifest, generate root-split inputs for the next slice, run
   `run_pilot_wf.js` on the interactive Max harness (`node:fs` required), then
   audit `wf_output.json` so rejects auto-re-queue. Top of queue = sthā/bhū/gam.
3. **Instrument the run** (the decisive cost experiment, `PILOT_COST.md` §6):
   record tokens + wall-clock per window, keep going until the **Max weekly cap**
   fires, note the cumulative-token number → yields per-card cost + harness
   throughput + the weekly quota together = the clean "2-months-feasible? yes/no".

**Known follow-ups (lower priority):** extend the head-splitter to large
non-giant nouns (kāla/ka ~520 lines); Apte roles b/c/d in `apte_parse.py`.
(The sandhi-join prefix-portrait `pwg_preverb1.txt` fix was **dropped as futile** —
only 3/15 prefixed forms corpus-attested; the root-fallback hint is final.)

**Policy reminders for the translator:** preserve PWG sense order (Renou = badge,
never re-sort); `{%…%}` wraps BOTH German glosses (translate) AND Latin (leave);
keep `{#..#}`/`<ls>` sigla verbatim; NWS owners verbatim, one row per source.

---

## Track B (SECONDARY) — lock the comparison flagship + finish its Russian

The `article-comparison/` study (agni, anya, akṣara, ananta) is complete and
released (**v0.0.5**). Two tasks remain, per the user (2026-06-25):

1. **Flagship 1 + 1 pair — LOCKED (2026-06-25): `agni` (non-samāsa) + `akṣara`
   (a-samāsa).** Both sort early (maximal cross-dict coverage), both
   high-frequency, and both carry the cleanest comparison *finding* — the
   theonym↔common-noun split (Агни/огонь) and the syllable↔Brahman split
   (слог/Непреходящее). **`anya` and `ananta` become supporting examples**, not
   the flagship.
2. **Finish the chosen pair's Russian to 100 %** (user said "close the tail"):
   - Run a **Max-LLM per-sense assignment** over the residual renderings (the
     `### Не привязано к значению` bucket in each `*.persense-ru.md`, currently
     1–12 % of occurrences) — assign each to its PD sense or "other". Deterministic
     coverage is 88–99 %; this closes the synonym/paraphrase tail.
   - **Review the hand-authored RU glosses** for the flagship pair (agni's 130
     senses are hand-authored; akṣara/ananta/anya came from
     `_build_skeletons_ru.py`) — publication-quality pass.
   - Builders to re-run: `RussianTranslation/src/_build_persense_ru.py` (extend
     with the LLM-assigned residual), `_build_corpus_ru.py`, `_build_skeletons_ru.py`.

---

## OUT OF SCOPE (maintainer-owned, do NOT put on the agent roadmap)

**SamudraManthanam `#sa` Cyrillic cleanup.** Source jsonl already cleaned +
committed (branch `feature/chronology-index`); tools shipped
(`web/ingest/clean_sa_cyrillic.py`, `scan_homoglyphs.py`,
`fix_corpus_db_sa.py`); list = `web/ingest/HOMOGLYPH_WORDS.tsv`; documented in
[SamudraManthanam #16](https://github.com/gasyoun/SamudraManthanam/issues/16).
The **human maintainer** runs `fix_corpus_db_sa.py --db <server>/corpus.db
--apply` on the live server and merges the branch. The agent should not execute
the server fix.

---

## Key files & commands

| Purpose | Path / command |
|---|---|
| Max window loop | [`src/pilot/RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md) |
| Older a-section loop | archived: [`src/pilot/archive/legacy_max_2026-06-27/RUN_ASECTION_MAX.md`](src/pilot/archive/legacy_max_2026-06-27/RUN_ASECTION_MAX.md) |
| 38-unit freq test runbook | [`src/pilot/FREQ_TEST_RUNBOOK.md`](src/pilot/FREQ_TEST_RUNBOOK.md) |
| Workflow harness (has fs; Max only) | [`src/pilot/run_pilot_wf.js`](src/pilot/run_pilot_wf.js) |
| Freq order + giant-root split | `src/freq_route.py`, `_pilot_gen_merged.py --manifest freq --root-split` |
| Fidelity gate | `src/audit_translation.py` |
| Cost/quota analysis | [`PILOT_COST.md`](PILOT_COST.md) §6 |
| Comparison study | [`../article-comparison/README.md`](../article-comparison/README.md) |
| Per-sense RU + residual tail | `../article-comparison/*.persense-ru.md`, `src/_build_persense_ru.py` |

## Decisions (locked 2026-06-25)
- **Track B flagship pair:** **agni + akṣara** (anya/ananta = supporting examples).
- **Track A judge model:** **Opus 4.8** for the 38-output severity *validation* pass.
  (Bulk policy since 2026-06-26: Sonnet judges every card, Opus re-judges rejects only —
  [`research/JUDGE_POLICY.md`](research/JUDGE_POLICY.md).)

No open decisions — both tracks are cleared to execute.
