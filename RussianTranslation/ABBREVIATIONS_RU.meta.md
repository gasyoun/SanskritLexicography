# ABBREVIATIONS_RU.meta.md — metadoc for the PWG `<ab>`/`<ls>` abbreviation policy

_Created: 02-09-2026 · Last updated: 02-09-2026_

Companion to [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md).
Created during the H3959 propagation sweep, which found the governing doc had no metadoc
after eight weeks and three rulings.

## Purpose

Answers one question: **when a PWG abbreviation reaches the Russian column, what does the
reader see?** It is a *policy* doc with an executable twin — every rule it states is
enforced by [`src/pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py),
and where prose and code disagree, the code's `census` gate is the one that fails CI.
Scope is `pwg_ru` only; `mw_ru`'s "leave `<gram>` untouched" convention is a separate,
deliberately different pipeline.

## Provenance — three human rulings, not one

| Date | Ruling | What it settled |
|---|---|---|
| 10-07-2026 | MG, via `AskUserQuestion` | The two-bucket split: grammatical categories stay international Latin with a tooltip; editorial/cross-reference abbreviations translate to Russian. |
| 19-07-2026 | MG, h178 DA-vote notes N5/N8 | `Caus.` = «кауз.», `Aor.` "нельзя не переводить" — a *contradicting* position, delegated to a unified list that was never ratified. Logged as [CONTRADICTIONS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md). |
| 02-09-2026 | MG, [registry-contradictions sheet](https://gasyoun.github.io/vote/sheets/uprava_registry_contradictions_02-09-26.html) | «some remain Latin, none remain German, most German become Russian and do not become Latin» — kept 10-07, rejected the 19-07 reading, added *none remain German*. Applied by [H3959](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3959-Opus_SanskritLexicography_ab-german-residue-ru-map_02.09.26.md). |

The 26-08-2026 H3538 adjudication wave correctly refused to rule §4 from documents — both
sides were human policy — and it stayed open for a week only because nobody put it on a
sheet. That is the reusable lesson: *"no agent ruling is possible" is a well-formed ask, not
a dead end.*

## Ranked improvement backlog

1. **Graduate the three sets to a `D##` in [CROSS_REPO_DECISIONS.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md).** H1303's "unified ratified list" is now satisfied in code, but the decision registry has no tombstone. Bookkeeping, not blocking — and no `D##` has ever actually been minted, so this would be the first.
2. **Wire `census` into CI.** It is a gate with an exit code and no workflow step; today it only fails when someone runs it. One line in the `RussianTranslation gates` job would make "none remain German" a merge condition instead of a convention.
3. **Re-examine the 14-token residue against the printed scans.** `o.`, `H.`, `M.`, `Fr.`, `r. V.`, `o. W.` have no `pwgab` entry, but the printed volume may declare them where the machine-readable table does not. A scan check could shrink the residue honestly; guessing cannot.
4. **Decide `med.` case-sensitivity for real.** `med.` is mapped as "Medizin" (domain), but a genuine medium-voice usage would share the string. Flagged as residual risk since 10-07 and still unmeasured — a corpus probe, not a judgment call.
5. **Audit the remaining ~519 `pwgab` entries the corpus has not used yet.** The three sets cover the 272 tokens actually in the store, not the full 791-entry table. New corpus growth surfaces gaps as `A-unmapped` — which is the intended mechanism, but a pre-emptive pass would keep `census` from failing mid-release.

## Limitations — what this doc does NOT govern

- **The store.** The policy is render-time by design; `pwg_ru_translated.jsonl` keeps raw German tags. Free-floating German *outside* `<ab>` is a different problem with its own sweep (H2849, and the 65 rows H3959 measured as still owed).
- **The `de` field.** Source-faithful by design, never touched.
- **`<ls>` link enrichment.** Shares the file but is a separate workstream (H1307); the Pāṇini/Spr./DHĀTUP. sections stand on their own.
- **Bucket assignment for a token the corpus has never used.** Undecided until it appears.

## Related docs

- [`src/pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py) — the executable twin; `RU_MAP` · `BUCKET_B` · `RESIDUE` · `census`.
- [`pwg_ru/PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md) — rules 3.1–3.5 in Russian, with vote provenance. **Where the two disagree, the style guide of record wins on wording and this doc wins on mechanism** — the guide cites votes, this doc cites the code that enforces them.
- [CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) §4 — the registry row, now ✅ RULED.
- [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) **L16** — the capability row.
- [`CLAUDE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md) § Abbreviation invariant — the sync rule agents must follow.

## Revision history

| Date | Change | By |
|---|---|---|
| 02-09-2026 | Created during the H3959 propagation sweep; records all three rulings and the backlog above. | Opus 5 (`claude-opus-5`) |

_Dr. Mārcis Gasūns_
