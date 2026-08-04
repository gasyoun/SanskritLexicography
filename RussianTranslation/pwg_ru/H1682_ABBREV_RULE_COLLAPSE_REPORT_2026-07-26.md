# H1682 — h1303_abbrev rule-collapse: report

_Created: 26-07-2026 · Last updated: 26-07-2026_

## What this is

[H1664](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1664-Fable_SanskritLexicography_voting-queue-agent-adjudication-triage_26.07.26.md)
([`VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md` §11](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md))
ruled the `h1303_abbrev` review sheet (273 cards, never voted) HYBRID: "a
~6-rule policy asked 273 times" — a card-**design** defect, not a screening
problem, since [`build_h1303_abbrev_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_h1303_abbrev_sheet.py)'s
`O` overlay already carries a full per-token classification (bucket
grammatical/editorial/citation, class German/Latin/contextual/OCR, proposed
RU, precedent notes) — it just renders one card per token instead of one
card per *policy*.

This handoff re-groups that same classification (no token reclassified) into
a rule-level sheet: 12 rule cards (one per the `O` overlay's own `# --- ...`
section header, authored by Fable 5 `claude-fable-5` in H1303 Session 1,
21-07-2026) + individually-flagged ambiguous residue + the 3 `ls`-border
cards + the meta-card, both carried over verbatim.

## Method

1. [`h1682_abbrev_collapse.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h1682_abbrev_collapse.py)
   parses `build_h1303_abbrev_sheet.py`'s source directly (its `O` dict +
   its 12 `# --- ...` section-header comments) so no token is re-typed by
   hand — avoiding exactly the manual-transcription error a 269-token
   re-bucketing invites. Every token is classified **residue** iff its `ru`
   proposal is `None`, or its `note` matches a collision/caution/OCR/
   no-fixed-value/context-dependent signal (`_AMBIG_RE`); otherwise it folds
   into its section's **bulk** rule (any settled explanatory footnote is
   preserved in the tsv but does not make the token residue).
2. [`build_h1682_abbrev_classification_tsv.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_h1682_abbrev_classification_tsv.py)
   emits [`H1682_ABBREV_RULE_COLLAPSE_CLASSIFICATION_2026-07-26.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1682_ABBREV_RULE_COLLAPSE_CLASSIFICATION_2026-07-26.tsv) —
   **100% of the 269 store-attested `ab`-tokens**, each with its rule
   section, bulk/residue status, bucket, class, proposed RU, one-line cited
   precedent, and its original note. Asserted `== 269` at generation time.
3. [`build_h1682_abbrev_rules_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_h1682_abbrev_rules_sheet.py)
   emits the replacement sheet, H1404-stamped (`content_hash` + a committed
   metadata-only lock at `review/locks/h1682_abbrev_rules.lock.json`).

## Result — 273 → 33 cards (~8.3×)

| | count |
|---|--:|
| ab-tokens classified (100%) | 269 |
| — rule-bulk (folds into its section's policy) | 252 |
| — residue (classifier-flagged ambiguous, individual card) | 17 |
| Rule cards (12 sections) | 12 |
| Residue cards | 17 |
| `ls`-border cards (carried over verbatim) | 3 |
| Meta-card (carried over verbatim) | 1 |
| **Total human-facing cards** | **33** |
| Old sheet (`h1303_abbrev`) | 273 |

The [audit's](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md)
"~30" was an explicit planning estimate; the real, published number is **33**
— a ~8.3× reduction in cards, and the residue set (17) is smaller than the
audit's own routing table implied because several notes on the O overlay are
settled explanatory footnotes (a citation, a worked example) rather than
genuine ambiguity, and fold into their section's bulk rule with the footnote
preserved in the tsv.

### The 12 rule cards (source-order, from `build_h1303_abbrev_sheet.py`'s own section comments)

| Section | Bulk | Residue | Precedent |
|---|--:|--:|---|
| cross-reference / deictic | 17 | 0 | RU_MAP + MG 10-07 AskUserQuestion (Bucket A) + DA-vote N3(a)/N4 |
| meaning / designation / usage labels | 48 | 3 | RU_MAP + N3(a)/N4; MG's own Bein./N. pr. examples |
| domain labels | 12 | 0 | ABBREVIATIONS_RU.md domain-label rule + RU_MAP |
| contextual `n=`-governed (mechanism only) | 0 | 10 | Render-time mechanism note — no context-independent fixed RU is possible per token |
| grammatical: cases | 20 | 0 | DA-vote N3/N5/N8 (19-07-2026) |
| grammatical: number/gender/person | 9 | 2 | DA-vote N3/N5/N8 |
| grammatical: voice/secondary stems | 15 | 1 | DA-vote N3/N5/N8; N8 pins Caus.→кауз. |
| grammatical: tense/mood | 28 | 0 | DA-vote N5: "Aor. cannot stay untranslated" |
| grammatical: non-finite/POS/syntax | 34 | 0 | DA-vote N3/N5/N8 |
| grammatical: valency/diathesis-adjacent | 13 | 0 | DA-vote N3/N5/N8 |
| grammatical: word formation/morphology/degree | 26 | 0 | DA-vote N3/N5/N8 |
| source/citation mechanics | 30 | 1 | DA-vote N4/N9; Sch./Schol./Comm. as native-Russian scholarly forms |

### The 17 residue tokens (classifier-flagged, individually voted)

`ebend.`, `W.`, `geder.`, `e.`, `H.`, `o. W.`, `o.`, `schl.`, `d.`, `M.`,
`r. V.`, `d. r. V.`, `Fr.`, `neutr.`, `3.`, `Med.`, `v. l.` — each carries its
own O-overlay note verbatim in both the tsv and the sheet card (collision
risk, OCR noise, or a per-occurrence `n=`-attribute dependency that a static
token→RU table cannot resolve).

## Non-goals honored

- The underlying policy is **not** re-ruled here — every proposed RU comes
  verbatim from `build_h1303_abbrev_sheet.py`'s `O` overlay (H1303 Session 1).
- `RU_MAP` (`pwg_ab_ru.py`) is untouched — this handoff only builds the
  voting surface; application happens after a human votes.
- No fenced file (`review/voted.md`, `review/decisions.md`) touched.
- The old `h1303_abbrev` sheet/lock/index row is kept, marked
  superseded-unvoted (never deleted, never re-asked) — legal because it was
  never voted (batch1v2 supersession-by-remake precedent, H1655).

## Next step (human)

Vote `review/h1682_abbrev_rules_sheet.html`, export
`pwg_ru/eval/h1682_abbrev_rules.decisions.json`; a follow-up session applies
approved rule cards to `RU_MAP`/`pwg_ab_ru.py` in bulk and approved residue
tokens individually, then resolves
[CONTRADICTIONS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
→ `D##` (renumbered from §7 by H1364, 20-07-2026 — the H1682 handoff's own
"§7" and `.ai_state.md`'s are stale mentions of the pre-renumbering key,
corrected here).

_Dr. Mārcis Gasūns_
