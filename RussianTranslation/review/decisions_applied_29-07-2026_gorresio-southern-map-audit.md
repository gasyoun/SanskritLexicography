# Gorresio↔Southern verse map — audit sheet decisions applied (H1656 round 1)

_Created: 29-07-2026 · Last updated: 29-07-2026_

Audit record per the [`/decisions-apply`](https://github.com/gasyoun/claude-config/blob/main/commands/decisions-apply.md)
runbook for sheet `sanskritlexicography-gorresio-southern-map_audit-26-07-26` (32 cards,
`"complete": true`).

**This record is a backfill, not a second application.** The votes were applied on
26-07-2026 in
[PR #793](https://github.com/gasyoun/SanskritLexicography/pull/793) (merged
2026-07-26T12:29:25Z) / commit
[`6f7336b6`](https://github.com/gasyoun/SanskritLexicography/commit/6f7336b63d10330c2b4d5fc09fe5111a4ba4f2f3);
what was missing was the audit trail every other voted sheet in this directory carries
(compare
[decisions_applied_2026-07-26_g5-batch1.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions_applied_2026-07-26_g5-batch1.md)
and
[decisions_applied_2026-07-28_g6-mqm-gold-starter.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions_applied_2026-07-28_g6-mqm-gold-starter.md)).
Re-verified and written 29-07-2026 by Opus 5 (`claude-opus-5[1m]`); **nothing in the data
was changed by this pass.**

The vote export and the sheet HTML stay **uncommitted** — `.git/info/exclude` covers
`RussianTranslation/review/*_decisions.json` and `RussianTranslation/review/*_review.html`
as personal voting artifacts. Reviewer field of the export, verbatim: «Fable 5
(claude-fable-5) — агентское голосование по прямому поручению MG (26-07-2026, «vote the
audit sheet now»); НЕ клики MG» — i.e. an **agent vote on MG's direct delegation**, not
MG's own clicks. That distinction matters if this map is ever cited as human-gated.

## Verdict counts

| verdict | n | route taken |
|---|---:|---|
| approve | 28 | no action — row keeps its `matched`/`fuzzy` class, citation reuse stays ON |
| reject | 4 | `class` column set to `audit-rejected` + the pair pinned in the rebuild denylist |
| defer | 0 | — |
| unvoted | 0 | sheet carries `"complete": true`; 32 of 32 decided |

Approvals were **not** rewritten — that is the correct route, not an omission: an approve
means "leave the mapping as the builder derived it", and touching the row would only add
churn to a 19,852-row generated file.

## Pipeline

Applied through the domain's own mechanism, in three coupled layers, so a rebuild cannot
silently undo the vote:

1. **Data** —
   [ramayana_gorresio_southern_verse_map.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_gorresio_southern_verse_map.tsv):
   the rejected row's `class` becomes `audit-rejected`. The `s_kanda`/`s_sarga`/`s_verse`
   and `score` columns are deliberately **kept**, so the vetoed pair stays legible as an
   evidence trail rather than being blanked.
2. **Consumer** — `_gorr_map()` in
   [citation_tm.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py)
   keys citation reuse only off rows whose class is `matched` or `fuzzy` **and** whose
   `s_sarga` is non-empty. `audit-rejected` therefore falls out by construction — no
   special case in the loader, and the locus degrades to an honest
   `no-southern-counterpart` miss instead of an invented offset.
3. **Rebuild denylist** — `AUDIT_REJECTED_PAIRS` in
   [build_ramayana_concordance.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ramayana_concordance.py),
   re-applied by `build-gorresio`. It is keyed by the **full six-number pair**, not by the
   Gorresio locus alone: if a future rebuild maps that Gorresio verse to a *different*
   Southern verse, the old veto does not carry over and the new pair goes back to a human
   sheet. Pinned by the CI gate `python src/build_ramayana_concordance.py selftest`.

## The four rejected rows

All four are one systematic sub-class — OCR dropped a `॥N॥` verse marker, two half-verses
merged into one chunk, and the aligner paired the merged chunk with the Southern verse
matching its **tail**. Notes are the reviewer's, verbatim.

| id | Gorresio | Southern | score at vote | score today | reviewer note |
|---|---|---|---:|---:|---|
| G1.12.28 | 1,12,28 | 1,13,33 | 0.262 | 0.262 | сдвиг на полстиха: OCR потерял ॥N॥, два полустишия склеились; хвост чанка = S 13.33, но сам стих G 12.28 другой |
| G1.48.11 | 1,48,11 | 1,47,8 | 0.277 | 0.277 | сдвиг на полстиха (та же причина): начало чанка = S 47.8cd, продолжение уже следующий стих |
| G1.62.8 | 1,62,8 | 1,60,7 | 0.391 | 0.391 | сдвиг на полстиха: G-чанк начинается с S 60.7d и уходит в следующий стих |
| G2.4.7 | 2,4,7 | 2,5,7 | 0.286 | **0.741** | сегментация склеила 2 стиха (внутри чанка виден ॥5॥); S 5.7 — соседний стих сцены, не тот же |

## Verification run, 29-07-2026

Run in a worktree off `origin/master` at `c340bc0a`, on the committed TSVs only (no local
stores, no network).

**1. Repo selftest** — `python src/build_ramayana_concordance.py selftest`, exit 0,
28 checks all green (`selftest: all green`). The three this sheet owns:

```
  ok  - verse-map classes are typed
  ok  - 4 audit-rejected rows from the 26-07-2026 sheet stay switched off
  ok  - gold anchor G 1,22,1 -> S 19,1 matched (scan-verified 26-07-2026)
```

**2. Vote-to-data reconciliation** — all 32 ids parsed as `G{g_kanda}.{g_sarga}.{g_verse}`
(confirmed against the sheet HTML's `data-id` attributes) and matched against the TSV:

```
items in decisions.json : 32
ids match HTML exactly  : True   (HTML ids: 32)
verdict counts          : {'approve': 28, 'reject': 4}
TSV data rows           : 19852
TSV audit-rejected rows : 4  -> ['G1.12.28', 'G1.48.11', 'G1.62.8', 'G2.4.7']
VERIFY: all 32 votes match the committed TSV state.
```

28/28 approvals still have reuse ON; 4/4 rejects have reuse OFF; and **no row outside this
sheet carries `audit-rejected`**, so the class was not over-applied.

**3. Live-consumer probe** — `citation_tm.lookup('R. GORR.', …)`, status / canonical_id /
class:

```
--- REJECTED (must NOT resolve to a mapped Southern locus) ---
  R. GORR. 1,12,28   -> miss / no-southern-counterpart / -  inert
  R. GORR. 1,48,11   -> miss / no-southern-counterpart / -  inert
  R. GORR. 1,62,8    -> miss / no-southern-counterpart / -  inert
  R. GORR. 2,4,7     -> miss / no-southern-counterpart / -  inert
--- APPROVED CONTROLS (must still resolve) ---
  R. GORR. 1,22,1    -> hit / 01_ramayana-balakanda:19.1 / matched  ok
  R. GORR. 1,1,1     -> hit / 01_ramayana-balakanda:1.1 / matched  ok
  R. GORR. 2,3,35    -> hit / 02_ramayana-ayodhyakanda:4.35 / matched  ok
  R. GORR. 3,6,13    -> hit / 03_ramayana-aranyakanda:1.13 / matched  ok
```

**4. Historical check** — `git show 6f7336b6:…/ramayana_gorresio_southern_verse_map.tsv`
confirms the four rows were already `audit-rejected` at the 26-07-2026 commit, with the
scores the sheet showed (0.262 / 0.277 / 0.391 / 0.286).

## Nothing unapplied

All 32 items were determinate and all 32 are reflected in the data. No item was deferred,
none was left unvoted, none required a ruling the sheet did not supply.

## Open observations — flagged, deliberately not acted on

- **G2.4.7's score moved 0.286 → 0.741 under the H1689 rebuild**
  (commit [`bfa8f44c`](https://github.com/gasyoun/SanskritLexicography/commit/bfa8f44c),
  which replaced the vol-2/4/uk e-text). Same pair, so the full-pair denylist correctly
  held the veto — that is the mechanism working as designed. But the reviewer rejected a
  card showing 0.286; the evidence under that judgement has materially changed, and 0.741
  would now classify `matched`. This is a **re-vote candidate for audit round 2**, not
  something to flip here: reversing a recorded reject without a new vote is exactly the
  invented ruling the runbook forbids. The other three rows are byte-identical across the
  rebuild.
- **This sheet has no lock file.** Every other sheet in
  [review/locks/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/review/locks)
  has a `*.lock.json` binding its export to a sha256; this one does not, so the export
  could not be validated against a lock the way the G5 batch was. The reconciliation above
  (32/32 ids present in both the sheet HTML and the export, verdicts consistent with the
  committed data) is the substitute evidence.
- **Filename date format.** This record uses `DD-MM-YYYY` per the `/decisions-apply`
  instruction; its two siblings in this directory use ISO `YYYY-MM-DD`. Worth settling one
  way before a third convention appears.

## Provenance of this record

Two sessions took this sheet on 29-07-2026. An earlier Opus 5 (`claude-opus-5[1m]`) run
(worktree `SanskritLexicography-votes-98204`) completed the verification and drafted this
record but died before committing, leaving it uncommitted in an orphaned worktree. The
present run (worktree `SanskritLexicography-votes-100895`, same tier and version)
re-derived every number above from scratch — selftest, reconciliation, consumer probe and
the `6f7336b6` historical check all re-run — found the draft's claims correct, and landed
it. No data was written by either run; the dead worktree and its branch were removed.

Handoff:
[H1656](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1656-Opus_SanskritLexicography_gorresio-southern-critical-concordances_26.07.26.md).
Detection heuristic for the remaining half-verse-shift residue (over-long Gorresio chunks,
or chunks with an interior `॥N॥`) stays queued in the H1689 refinement pass.

_Dr. Mārcis Gasūns_
