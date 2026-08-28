# H2996 — pwg_ru wrong-entry ingest: 159 rows quarantined, 61 lemmas queued for re-ingest

_Created: 28-08-2026 · Last updated: 28-08-2026_

Applies the whole of [key1_repair_proposals.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/key1_repair_proposals.jsonl)
(56 proposals, 161 store rows) to the canonical `pwg_ru` store, per handoff
H2996 and the MG ruling of 17-08-2026 that withdrew
[key1_repair_vote_2026-08-17.html](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/key1_repair_vote_2026-08-17.html)
from voting: every verdict here is decided by the card's own printed head, so
there was nothing for a human to rule on. Closes the apply half of
[issue #1767](https://github.com/gasyoun/SanskritLexicography/issues/1767);
the defect itself is [FINDINGS §562](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

## What was wrong

The ingest went after an intended lemma — preserved in the subcard prefix
(`aDvan`, `vAsA`, `BAra`, `Apta`, `aSru`…) — but fetched the **flattened
look-alike** entry (`advan`, `vasa`, `bara`, `apta`, `asru`…) and stored that
article's content under the intended lemma's subcard. Where one flattened key
covered several intended lemmas, the same wrong card was stored verbatim once
per lemma. The real PWG articles of those lemmas were therefore never in the
store at all.

## What was applied

| class | action | cards | store rows | re-ingest lemmas |
|---|---|---:|---:|---:|
| `wrong_entry` | quarantine | 44 | 102 | 44 |
| `wrong_entry_xref` | quarantine | 8 | 29 | 8 |
| `wrong_entry_dup` | quarantine | 3 | 28 | 9 |
| `junk_key1` | key fix in place | 1 | 2 | 0 |
| **total** | | **56** | **161** | **61** |

**Deferred: none.** All 56 cards cleared the printed-source gate. Handoff step 4
(defer a genuine ambiguity rather than batch it into a vote) was therefore never
exercised — the gate exists in code and is selftested, but no card needed it.

The three proven duplications, unchanged from §562:

| id | fetched key1 | rows | intended lemmas whose real article was missing |
|---|---|---:|---|
| `k1r-009` | `bara` | 4 | `BAra`, `Bara` |
| `k1r-048` | `vasa` | 20 | `vAsA`, `vAsa`, `vaSA`, `vaSa`, `vasA` |
| `k1r-049` | `vasin` | 4 | `vAsin`, `vaSin` |

### Why `junk_key1` was repaired in place and not re-ingested

The handoff asked for `junk_key1` (`durg_a~~h0_zz_sch`) to go through the same
quarantine/re-ingest mechanism. It did not, and the evidence is why:

1. The card's printed head is `durgā`, i.e. **the intended lemma** — the content
   is correct and only `key1` is malformed (it carries the whole subcard stem).
   Quarantining it would have destroyed a sound translation.
2. The card is `sch` layer (Schmidt *Nachträge*). A sweep of all 123 366 PWG
   records found records for 61 of the 62 intended lemmas — `durgA` is the one
   with **no PWG record to re-ingest from**, so a re-ingest unit for it could
   never be discharged.

The proposal's own `action` field already prescribed the in-place fix
(`mechanical: set key1 to the decoded subcard lemma`), and that is what ran:
`key1` is now `durgA` on both rows; the `subcard` stem is untouched.

## Store before / after

| | rows | sha256 |
|---|---:|---|
| before | 11 621 | `fc7af23ace17325a3dbfd563539ed9831970fff1d7a0357b37e70bb1d5e6a1a7` |
| after | 11 462 | `19fcf5258e5ea384baa6aa0883e5495edd83d1ec0cb9f0cbf70bfd912b69bb9c` |

Delta **−159** rows, expected: quarantine removes rows from the store, it does
not delete them. Backup taken automatically by the rewrite:
`pwg_ru_translated.jsonl.h2996_key1_repair.20260828T113217.856069Z.p23024.0f74cecb873f.bak`.

No row was lost: the 159 quarantined rows are retained verbatim, each with a
`_quarantine` block naming the proposal, the fetched key, the intended lemma and
the printed-head evidence.

## Gates

| gate | before | after |
|---|---|---|
| `window_selftest.py` | 213/213 pass | 213/213 pass |
| `placement_axis_check.py` | OK (6374 sidecar rows, 661 placed) | OK, A3/A5 stop-conditions clear |
| store row count | 11 621 | 11 462 (−159, expected) |
| human-touched rows removed | — | **0** (all 161 were `ai_translated`, `reviewer: None`) |

**LANG_PARITY: RU-only by construction.** There is no EN translated store — the
EN lane audits window artifacts, not a persistent store — so this repair has no
EN twin to port. The two derived RU siblings next to the store
(`pwg_ru_translated.enriched.jsonl`, `pwg_ru_translated.renou.jsonl`, 217 rows
each) were checked and carry **0** of the 159 quarantined rows, so no derivative
re-publishes a quarantined card.

## Artifacts

- Apply pass: [src/apply_key1_repair.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/apply_key1_repair.py) — dry-run by default, `--selftest` 8/8
- Quarantined rows: [reports/pwg_ru_wrong_entry_quarantine.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/pwg_ru_wrong_entry_quarantine.jsonl) (159)
- Apply ledger: [reports/H2996_key1_repair_apply_ledger.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H2996_key1_repair_apply_ledger.jsonl) (56 events, one per proposal)
- Re-ingest worklist: [pwg_ru/H2996_WRONG_ENTRY_REINGEST_WORKLIST_2026-08-28.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H2996_WRONG_ENTRY_REINGEST_WORKLIST_2026-08-28.jsonl) (61 lemmas)
- Re-ingest roots: [pwg_ru/H2996_WRONG_ENTRY_REINGEST_ROOTS_2026-08-28.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H2996_WRONG_ENTRY_REINGEST_ROOTS_2026-08-28.txt) (one lemma per line)

## What is NOT done here, deliberately

The 61 lemmas are **queued, not translated**. Re-ingest runs through the
standard pipeline and a paid window needs a live-gate GO — this pass writes no
translation and calls no model. Until those windows run, the store simply has
159 fewer wrong rows; it does not yet have the 61 right articles.

Each worklist unit carries the exact SLP1 key and an explicit consumer contract:
match the PWG `<k1>` field **exactly, never case-folded** — the flattened lookup
is the defect itself. Verified against the source: `pwg_mask.py card aDvan`
resolves the `aDvan` article and `card advan` the `advan` one, so a consumer
keyed on the exact lemma re-ingests correctly today. The historical flattening
site upstream of that lookup was **not** located in this pass and is not claimed
fixed — the worklist defuses it by construction rather than by repair.

## Consequence for wave 4 (§559)

For these ~60 lemmas the MW/AP sense-coverage comparison ran against the
look-alike's content, so those verdicts are invalid in both directions. They
stay invalid until the re-ingest windows land; re-running the wave-4 comparison
before then would only re-measure the hole.

_Dr. Mārcis Gasūns_
