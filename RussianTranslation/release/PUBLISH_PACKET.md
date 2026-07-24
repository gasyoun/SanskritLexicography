# Publish Packet — Publication-Grade Sa→Ru TM + Curated Terminology (D13)

_Created: 22-07-2026 (H1458 Track C5) · Sonnet 5 `claude-sonnet-5`_

**This packet is prepared for a HUMAN to execute via `/publish-safety-check`. The agent that
built it never publishes, mints a DOI, flips visibility, or pushes copyrighted text public —
that fence is load-bearing per the [H215](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md)/[H1458](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1458-Sonnet_RussianTranslation_pubgrade-tm-track-c-release-prep_22.07.26.md)
autonomy contract and is not overridable by this document.**

## 1. What is ready to publish now (no further clearance needed)

| Artifact | Path | Records | Rights |
|---|---|---:|---|
| PWG translation memory (public) | [`release/translation_memory/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release/translation_memory) | 2,392 | own translation of public-domain PWG — cleared |
| Corpus-TM public_full bundle | [`release/corpus_tm/public_full.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/corpus_tm/public_full.jsonl) / `.tmx` | 2,392 | same PWG source as above (re-derived TMX form) — cleared |
| Corpus-TM derived_only bundle | [`release/corpus_tm/derived_only.sample.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/corpus_tm/derived_only.sample.jsonl) (sample; full 1,093,391-row file regenerable, gitignored) | 1,093,391 | structure only — NO Russian surface text, verified by `--audit-rights` |
| Curated Sa→Ru terminology (D13) | [`release/sa_ru_terminology/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release/sa_ru_terminology) | 2,175 terms | own translation of public-domain PWG — cleared |
| Datasheet (Bender/Friedman + Gebru) | [`TRANSLATION_MEMORY_DATASHEET.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DATASHEET.md) | — | documentation |

**License for the above:** CC-BY-SA-4.0, per
[`DATA_LICENSE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DATA_LICENSE.md)
(own-work scope) — its enumerated file list should be extended to name
`release/translation_memory/`, `release/corpus_tm/public_full.*`, and
`release/sa_ru_terminology/` explicitly (currently implicit under "the pwg_ru edition");
a one-line addition, human sign-off recommended before the DOI mint.

## 2. What is NOT ready — per-source clearance checklist

The `corpus_tm` **full** `ru`-bearing pairs (`RussianTranslation/src/corpus_lexicon.jsonl`,
1.09M rows, local + gitignored) derive from the SamudraManthanam parallel corpus's 131 source
works. Per the canonical
[RIGHTS_TABLE.md](https://github.com/gasyoun/SamudraManthanam/blob/main/nkrya-parallel/export/RIGHTS_TABLE.md)
(H821, last tabulated 13-07-2026): **0 of 131 are cleared; all 131 are `needs_review`.**

Before any of the following can move from `needs_review` to `cleared` (and thus become
eligible for a future `public_full` inclusion), a human must, per source:

- [ ] Identify the physical edition + translator/publisher of record.
- [ ] Confirm whether the translation is public domain (translator deceased >70y in the
      relevant jurisdiction, or explicit PD release) — if so, mark `cleared` with the basis noted.
- [ ] If in-copyright: obtain written permission from the rights-holder (translator, estate, or
      publisher) for non-commercial scholarly redistribution of the aligned word-level pairs
      (NOT full-text reproduction — word/phrase-level alignment units only).
- [ ] Record the outcome in a `<slug>.meta.json` sidecar in
      `SamudraManthanam/web/corpus_builder/jsonl/` (H821 flagged that 143 of 148 previously-filled
      sidecars were never actually committed — restoring them is itself a queued `@DO`, separate
      from this packet).
- [ ] Re-run `RIGHTS_TABLE.md`'s generator so the ledger reflects the clearance.
- [ ] Re-run `build_release_bundles.py build` — a cleared work's rows will then carry
      `rights_status: cleared` and `--audit-rights` will permit their `ru` field into
      `public_full` on the next build.

**4 of 131 sources have a *documented* translator today** (still `needs_review`, not cleared):
`01_ramayana-balakanda` (П. А. Гринцер), `02_ramayana-ayodhyakanda` (П. А. Гринцер),
`03_mahabharata-aranyakaparva` (Я. В. Васильков, С. Л. Невелева), `03_ramayana-aranyakanda`
(П. А. Гринцер, attribution needs verification) — these are the natural starting point for
outreach, since the remaining 127 have no attribution on file at all yet.

## 3. DOI-mint steps (human, after §1 clearance sign-off)

1. Verify `python src\build_release_bundles.py --audit-rights` and
   `python src\terminology_build.py selftest` both pass on the commit being released.
2. Run `/publish-safety-check` over this packet + the target repo visibility.
3. Extend `DATA_LICENSE.md`'s enumerated scope to name the three release paths in §1 explicitly.
4. Mint the terminology dataset's DOI first (D13 — `release/sa_ru_terminology/manifest.ru.json`
   `doi_status: reserved` → update to the minted DOI once assigned); it has no outstanding
   clearance blocker.
5. Mint the TM's DOI (or fold it into A42's existing Zenodo DOI slot per the A42 fold-in,
   R3.2 — no separate TM paper) once A42's own "RU-translation IP documentation" gate is fully
   closed (§2 above; A42 currently only has the *mechanized* half done, not the human clearance).
6. Update [Uprava/ARTICLES.md A42 row](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)
   and this packet's §1 table with the minted DOI(s).

## 4. What this packet does NOT authorize

- Publishing `corpus_lexicon.jsonl` itself, in full or in part with `ru` populated, for any of
  the 131 `needs_review` sources.
- Enabling GitHub Pages, flipping repository visibility, or registering a DOI — all human actions.
- Treating "4 sources have a documented translator" as equivalent to "4 sources are cleared" —
  documentation is a prerequisite for outreach, not clearance itself.
