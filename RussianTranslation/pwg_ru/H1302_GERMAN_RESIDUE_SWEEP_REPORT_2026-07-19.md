# H1302 — German-prose-residue store sweep + 3 rejected-card repair (report)

_Created: 19-07-2026 · Last updated: 19-07-2026_

Handoff: [H1302](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1302-Opus_RussianTranslation_pwg-ru-german-residue-sweep-reject-repair_19.07.26.md)
· Model: Opus 4.8 (`claude-opus-4-8`) · Register:
[H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md)
(rows N16, N17, N19; §6 item 1).

## What this was

Store-wide sweep for **German prose function words / phrases surviving untranslated in the
`ru` field OUTSIDE protected markup** — e.g. citation *zu* in "Schol. zu ŚĀK. 14." (→ «к»),
*mit Ergänzung von* (→ «с восполнением»), the preverb-header *Mit {#prefix#}* (→ «С»), and the
grammatical/connective residue (*und*, *oder*, *mit dem <ab>acc.</ab>*, *so v. a.*). Distinct
from `<ab>`-tagged abbreviations (H1303 scope) and from the Russian glosses inside `{%…%}`
(translated content, protected). Plus repair + in-place re-promotion of the 3 cards the DA
sheet rejected.

## Method

1. **Detector** —
   [src/pilot/german_residue_scan.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/german_residue_scan.py):
   masks protected spans (`{%…%}`/`{#…#}`/«…»/`<ab|ls|is|lex>`/`<div…>`/`[Page…]`/`[NWS:…]`),
   flags German residue via a curated lexicon (seeded from `prompt_rule_audit.GERMAN_GLOSS_WORDS`
   + the survivors it missed) plus umlaut/ß orthography, guards proper-name false positives
   (Graßmann/Böhtlingk) with `foreign_literal_guards`, and classes each hit **a** (deterministic
   closed-set), **b** (needs retranslation), or **c** (whitelisted false positive).
2. **Deterministic fix** —
   [fix_german_connectives.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/fix_german_connectives.py)
   `--store` mode applies the class-a subs to the canonical store's `ru` field in place
   (backup `pwg_ru_translated.jsonl.h1302.bak`). Context patterns imported from the detector so
   the two can never drift.
3. **Requeue** — class-b hits parked to a worklist (no generation channel this session); the
   next window feeds the roots to `requeue_from_audit.py <root> --defect` (`--no-tm` implied).
4. **3-card repair** —
   [repair_h178_da_cards.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/repair_h178_da_cards.py),
   in place, `review_status` kept at `ai_translated` (the promoted-store value = the re-promotion
   the register's contract requires), with a `provenance.repairs` note per card.

## Counts by class (store: 11,603 rows)

| class | disposition | hits | rows |
|---|---|---:|---:|
| **a** | fixed deterministically in store | 690 | 486 |
| **b** | parked to requeue worklist (retranslate) | 465 | 273 |
| **c** | whitelisted false positive (proper-name authors) | 30 | — |
| — | **total flagged** | **1,185** | **684** |

After the deterministic pass + 3-card repair, a rescan shows **0 class-a** and **0 unclassified**
hits remaining; the 495 residual hits are the 465 class-b (parked) + 30 class-c (whitelisted).

Top class-b tokens (for the requeue window): `mit`=132 (mostly "mit dem <ab>case.</ab>"),
`so`=62 ("so v. a."), `zu`=45 (non-citation "zu lesen"/"zu ziehen"), `der/die/des/den/dem`=73,
`nach`=13, `im`=12, `von`=10, `wohl`=10, `als`=8, `aus`=7, `für`=6.

## Per-iteration precision (stop after ≤3; reached clean at 3)

| iter | change | hits | detector precision (residue sample) |
|---|---|---:|---|
| 1 | initial scan | 1,212 | not sampled — FPs present (Graßmann/Böhtlingk via ß/umlaut; `mit Ergänzung von` triple-counted) |
| 2 | mask `[NWS:…]`, whitelist proper names, dedup overlapping spans | 1,185 | **50 / 50 = 1.00** (hand-classified; all 50 genuine German residue) |
| 3 | classification refinement (citation `zu` after `</is>`, `Mit {#prefix#}` header) | 1,185 | 1.00 (unchanged; only a↔b reclassification) |

Precision requirement (≥0.90) met at 1.00. All 50 sampled residue hits were genuine untranslated
German; the only false positives in the raw run were the two proper-name authors, now class-c.

## 3-card repair outcomes

| register | key | fix | outcome |
|---|---|---|---|
| N16 | `nI\|n_i~~h0_13_apa\|5)` | prose *zu* "Schol. zu ŚĀK. 14." → «Schol. к ŚĀK. 14.» | repaired in place |
| N19 | `DA\|_d_a~~h0_81_a_bisam\|8` | *mit Ergänzung von* → «с восполнением» | repaired in place |
| N17 | `gam\|gam~~h0_42_prod\|1` | DE 1 word `{%hervorragen%}` rendered as a RU doublet → single attested «возвышаться» | repaired in place |

All three keep `review_status = ai_translated` and carry a `provenance.repairs` note
(`handoff: H1302`, date `2026-07-19`, reason `h178_da reject`).

### Deferred → H1304 (citation check, do NOT silently drop)

The N17 arbiter — **KATHĀS. 26,9** (Kathāsaritsāgara / Ocean of Stories, verse
`yadṛcchāprodgatodagrasapakṣagiri`) — is **absent from every local TM**: the 1.09M-pair
`corpus_lexicon.jsonl` is not on disk (only `src/fixtures/corpus_lexicon.fixture.jsonl`), and
[pwg_ru/aligned_works.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/aligned_works.txt)
lists no Kathāsaritsāgara. Per the handoff fallback the single equivalent «возвышаться» was used;
the citation-translation check against a published RU rendering is **deferred to
[H1304](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1304-Fable_RussianTranslation_pwg-ru-covered-texts-citation-tm-registry_19.07.26.md)**
(Ocean-of-Stories ingest). If H1304 surfaces a published rendering that differs, re-verify this cell.

## Prevention (SHARED across RU + EN)

- **Shared token source** — `GERMAN_PROSE_RESIDUE` / `GERMAN_PROSE_RESIDUE_EN` added to
  [foreign_literal_guards.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/foreign_literal_guards.py)
  (the module already named as the single cross-gate source of truth). The RU gate
  (`prompt_rule_audit.GERMAN_RESIDUE` / `GERMAN_GLOSS_WORDS`) unions the full set; the EN gate
  (`audit_window_en.DE_WORDS`) unions only the German-only subset — `so`/`als`/`aus`/`am`/`in`/
  `ein`/`wie` are deliberately excluded from the EN list so they never false-positive on ordinary
  English (they are impossible in Russian, so the RU gate keeps them).
- **LANG_PARITY** — new **SHARED** ledger entry `german_prose_residue_h1302`
  ([LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)),
  hashes snapshotted; `test_lang_parity_ledger_complete` green. (32 sibling entries tracking the
  three touched files were re-snapshotted — Case C, unrelated additive edits.)
- **Prompt rule** — a "no German prose in citation scaffolding" rule added to the RU translate
  prompt of record
  ([pwg_ru_prompts/1_perevod.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru_prompts/1_perevod.txt),
  rule 10) and the active harness
  ([src/pilot/run_pilot_wf.js](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_pilot_wf.js),
  HARD rule 8); `prompt` component bumped **1.0.0 → 1.1.0** in
  [pipeline_versions.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pipeline_versions.json)
  and re-frozen. (The pre-existing `glossary`/`script` drift is upstream, untouched by this work.)
- **Fixture** — `test_h1302_german_prose_residue_scan` in
  [window_selftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py)
  pins that prose `zu`/`mit Ergänzung von` outside protected spans is flagged, a protected
  `{%…%}`/«…» German span is NOT, "mit dem <ab>acc.</ab>" is class-b, proper names are class-c,
  and the `--store` fixer repairs the two rejected-card patterns. Full suite: **148/148 green.**

## Guardrails honoured

Worktree off `origin/master` (never the shared main checkout); store read/written only via
`canonical_store`; scope fenced OUT of `<ab>` content (H1303); `--no-tm` recorded on the requeue
worklist; no «ё» introduced (H1305 defect class avoided); committed evidence = counts + short
snippets only (no bulk RU rows); the repo is PUBLIC and `pwg_ru/eval/*` stays gitignored.

_Dr. Mārcis Gasūns_
