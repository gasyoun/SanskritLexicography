# H1809 — NWS-layer bare-citation `<ls>` markup + domain-slot half-translation — report

_Created: 29-07-2026 · Last updated: 29-07-2026_

Handoff: [H1809](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1809-Sonnet_SanskritLexicography_nws-bare-citation-ls-markup_28.07.26.md)
· Model: Sonnet 5 (`claude-sonnet-5`) · Tooling:
[nws_ls_markup.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nws_ls_markup.py) ·
Tests: [tests/test_nws_ls_markup.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_nws_ls_markup.py).

## What this was

MG (28-07-2026, voting `g5_batch1v3_sheet.html`): «ṚV(Sā) I 165, 11 is not clickable? Why?
All such entries are long ago clickable even at Cologne». [H1808](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1808-Opus_csl-pyutil_review-sheet-legibility-anatomy-citations_28.07.26.md)
fixed the sheet's render path; this handoff fixes the underlying data gap it could not
reach — the NWS (`Nachträge`) layer cites sources in its own convention (Roman-numeral
maṇḍala, optional `(Sā)` recension marker, no period after the siglum), which
`ls_resolver` (a faithful port of Cologne's own `ls_service.dart`, PWG-only) cannot
resolve without normalisation.

## Store-wide census (NWS-layer rows: `layer == 'nws'` OR inline `[NWS: ...]` marker, 506 of 11,603 rows)

The batch1v3 sample (150 cards) found 3 such spans; store-wide it is smaller, not
larger — **6 spans across 4 cards**, not the ~230 a naive linear extrapolation from the
sample would suggest. The sample happened to be denser than the store average.

| Card | Original span | Result |
|---|---|---|
| `Adika` | `ṚV(Sā) I 165, 11` | **resolved** → `n="ṚV. 1,165,11"` → resolves to Ṛgveda 1.165.11 (rvlinks/rvhymns) |
| `yaj` | `ṚV IV 42, 8` | **resolved** → `n="ṚV. 4,42,8"` → resolves to Ṛgveda 4.42.8 |
| `Cid` | `ChU VI 7, 1` | residue — `ChU` (Chāndogya Upaniṣad) is not in PWG's own 2,681-entry bibliography |
| `gA` | `ChU VI 4, 1` | residue — same |
| `dah` | `ChU VI 16, 3` | residue — same |
| `yaj` | `Harisv XIII 5, 4, 5` | residue — `Harisv` not in the bibliography either |

Residue is left as bare text (unlinked, as H1808's render-time `_bare_citation_html`
already marks it with a tooltip) — not guessed at. A future pass could add `ChU`/`Harisv`
scan links if/when a Cologne scan target exists for them; that is a *new resolver
pattern*, out of this handoff's scope (normalising an existing convention, not adding new
citable works).

## The recension-marker question — resolved by construction, not by a ruling

H1809's own prerequisite asked whether `(Sā)` is worth preserving and flagged it as a
human decision. The implementation sidesteps the fork instead of forcing it: the
normalised locus goes **only** into the `<ls n="...">` attribute; the visible span stays
byte-identical, `(Sā)` included. `generate_href` concatenates `n_attr + visible` and every
PWG pattern is `^`-anchored, so the unmatched original tail after a valid `n_attr` match is
harmless — confirmed end-to-end: rendering the store span

```
<ls n="ṚV. 1,165,11">ṚV(Sā) I 165, 11</ls>
```

produces a real link (href resolving to `rv01.165.html#rv01.165.11`, title starting
"ṚGVEDA. ..."), with the visible text still reading `ṚV(Sā) I 165, 11` — link and
bibliography tooltip both resolve correctly. Nothing is discarded, so the question of
whether discarding it would be acceptable never needed an answer.

## Domain-slot half-translation (H1809's "second, unrelated defect")

`g5_card_render.py`'s own vocabulary census (H1847) measured 13 `без уточн(.)`, 2
`Мед(.)`, 1 `Линг(.)`, 1 `Лингв(.)` across the store's `[diasystem, domain]` bracket tags
— a machine-readable tag half-translated into Russian in a handful of rows while the rest
(153 `unsp`, 28 `Med`, 11 `Ling`) stayed canonical Latin. All **17 occurrences migrated**
to their Latin form (`unsp`/`Med`/`Ling`) in place, slot 1 (diasystem) and everything
outside the bracket left untouched. `g5_card_render.DOMAIN_RU` already glossed both
spellings, so no rendering regresses.

## Store mutation

Applied via `python nws_ls_markup.py apply` against the canonical store
(`RussianTranslation/src/pwg_ru_translated.jsonl`, resolved through `store_path.py` so a
worktree run still lands on the persistent store, not a worktree-local copy that would be
discarded — see the H255 loss-safety note in that module). Backup:
`pwg_ru_translated.jsonl.h1809.bak` (gitignored, same convention as prior `.h####.bak`
files). **19 of 11,603 rows changed** (2 citation wraps + 17 domain migrations); every
other field on every row, and the `ru` field on every untouched row, verified
byte-identical against the pre-apply backup. Verified idempotent: a second `apply` run
reports 0 rows changed.

## Explicitly out of scope — logged, not silently dropped

A broader census of ALL `_BARE_CIT`-shaped spans (the general Arabic-form bare-citation
matcher `g5_card_render._BARE_CIT` already uses at render time) across the 506 NWS-layer
rows found **927 matches**, of which only a fraction are genuine unmarked PWG citations —
most are author-name+publication-year fragments living inside `[NWS: Author Year : page]`
provenance notes (e.g. `Hoernle`, `Geldner`, `Graßmann` followed by a 4-digit year, which
`_BARE_CIT`'s permissive "capital-letter siglum + numeral locus" shape matches just as
readily as a real citation). Wrapping those in `<ls>` at scale on a shared, gitignored
production store risks fabricated or misleading links; H1809's scope (a *specific*
convention-mismatch defect with a concrete, human-supplied example) does not license
guessing at that scale. A future handoff scoped specifically to "distinguish a genuine bare
citation from an NWS provenance-note fragment" would need its own recognizer, not a reuse
of `_BARE_CIT`.

## Verification

- `python g5_card_render.py` (selftest): PASS, unchanged.
- `python -m pytest tests/test_nws_ls_markup.py tests/test_ls_resolver_rvps_arity.py`: 23/23 pass.
- End-to-end render check (`build_article_site._render`) on the `Adika` row: produces a
  real citation link with a correct bibliography tooltip.

_Dr. Mārcis Gasūns_
