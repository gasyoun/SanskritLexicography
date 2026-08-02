# H1909 — NWS bare-citation vs. provenance-note fragment discriminator — report

_Created: 02-08-2026 · Last updated: 02-08-2026_

Handoff: [H1909](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1909-Sonnet_SanskritLexicography_nws-bare-citation-provenance-discriminator_29.07.26.md)
· Model: Sonnet 5 (`claude-sonnet-5`) · Tooling:
[nws_ls_markup.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nws_ls_markup.py) ·
Tests: [tests/test_nws_ls_markup.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_nws_ls_markup.py).

## What this was

[H1809](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1809-Sonnet_SanskritLexicography_nws-bare-citation-ls-markup_28.07.26.md)
fixed the specific defect MG reported (`ṚV(Sā) I 165, 11` not clickable). Its own census, run
over ALL `g5_card_render._BARE_CIT`-shaped spans in NWS rows (not just the Roman-numeral
convention it fixed), found **929 matches** store-wide — far more than the handful of genuine
unlinked citations. H1809 deliberately declined to mark any of them, logging the count and
stopping rather than guessing at scale (see its own
[report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1809_NWS_LS_MARKUP_REPORT_2026-07-29.md)
§"Explicitly out of scope"). This handoff is that follow-on: build the recognizer.

## Discriminator design — three provenance-fragment signals, one validation gate

`classify_general_bare_citation()` in
[nws_ls_markup.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nws_ls_markup.py)
excludes a match as a provenance-note fragment (never marked) on any of:

1. **Bracket position** — lives inside a literal `[NWS: ...]` tag. Strongest single signal,
   as the handoff's own prerequisite guessed: 125 matches, only 1 borderline case (see §3).
2. **Bare-year-shaped locus** — a single 4-digit number, no internal separator, in the range
   1400–2029 (`'Lévi 1925'`, `'Dalal 1934'`). Provenance notes are sometimes rendered as
   parenthetical or bare-comma prose OUTSIDE the literal bracket too, so this signal alone
   catches 290 more author+year fragments the bracket check misses.
3. **`_SPURIOUS_SHORT_SIG`** — one measured false-positive siglum, `'H'` (3 matches; see §3).

Everything surviving all three is a **citation candidate**, then validated exactly like
H1809's own gate: siglum must resolve in `pwg_sources`' PWG bibliography, and the normalised
locus must produce a real href via `ls_resolver.generate_href`. Only spans passing **both**
classification and validation are wrapped in `<ls n="...">`; the locus normaliser
(`_normalize_general_loc`) generalises H1809's Roman-mandala conversion to the comma-attached
NWS spelling (`'I,85,12'`, not just the space-separated `'I 165, 11'` the Roman-specific pass
already handled) — this recovered 49 citations that a first draft using only the space-form
converter left as false residue.

## Measured false-positive rate — 0/195 in the marked set, not estimated

Every one of the 195 spans this pass actually marks was hand-inspected (full listing in the
census output, not a sample): all 195 are `ṚV`/`AV` (Ṛgveda/Atharvaveda) citations with a
genuine multi-part locus. **0/195 = 0% measured false-positive rate**, against the handoff's
<5% stop condition.

### §3 — how two candidate false positives were found and ruled out

The design process itself surfaced two near-misses, both worth recording since they shaped
the final rules:

- **`'H. 12'`** (siglum `H`) resolves in PWG's own bibliography (Hemacandra's
  *Abhidhānacintāmaṇi*) and even generates a valid href for a bare 1–2 digit locus. But
  every one of the 4 store-wide occurrences of this exact span (1 inside a `[NWS: ...]`
  bracket, 3 outside) is actually `"2. H. 12. Jh."` = German *"2nd half, 12th century"* — a
  date descriptor, not a citation. A first-draft fix excluded ALL 1-character sigla, which
  also silently dropped 4 genuine `'R I.44.6'`-shaped citations (see below) — replaced with
  a `_SPURIOUS_SHORT_SIG = {'H'}` set naming only the one siglum with concrete evidence.
- **`'R I.44.6'`, `'R VII.21.42'`, `'R II.12.110'`, `'R III.61.3'`** (siglum `R`, Rāmāyaṇa)
  are genuine citations that the blanket short-siglum rule above wrongly excluded in the
  first draft. `'R'` legitimately resolves in PWG's bibliography, and `ls_resolver` even
  generates an href for SOME locus spellings — but Arabic vs. Roman book numbers there route
  to **different critical editions** (`ramayanaschl`/Schlegel vs. `ramayanagorr`/Gorresio;
  measured directly against `ls_resolver.generate_href`). Auto-converting the store's
  period-separated Roman form (`'I.44.6'`) to Arabic to make it resolve would silently pick
  an edition MG never specified. This module does not guess: these 4 spans fall through to
  `residue_no_href` (siglum resolves, locus shape doesn't) — visible in the residue list,
  not silently dropped, and not marked with a possibly-wrong link.

## Store-wide results (NWS-layer rows: 506 of 11,603)

| Category | Count |
|---|---|
| Total `_BARE_CIT`-shaped spans in NWS rows | 929 |
| — already claimed by H1809's Roman-specific pass or a pre-existing `<ls>` span (unchanged by this pass) | 8 |
| — inside `[NWS: ...]` bracket (provenance fragment) | 125 |
| — bare-year-shaped locus outside bracket (provenance fragment) | 290 |
| — `'H.'` century-descriptor collision (provenance fragment) | 3 |
| — citation-shaped, siglum not in PWG's bibliography (honest residue) | 276 |
| — citation-shaped, siglum resolves but locus shape has no `ls_resolver` pattern (honest residue, includes the 4 Rāmāyaṇa spans above) | 32 |
| **Resolved + marked with `<ls n="...">`** | **195** |

## Store mutation

Applied via `python nws_ls_markup.py apply` against the canonical store
(`RussianTranslation/src/pwg_ru_translated.jsonl`, resolved through `store_path.py`, same
loss-safety convention as H1809). Backup:
`pwg_ru_translated.jsonl.h1809nws.<timestamp>.<pid>.<host>.bak` (H2146/H2153 locked writer,
gitignored). **110 of 11,603 rows changed** (195 `<ls>` wraps landed across 110 rows — several
rows carry more than one citation). Verified against the pre-apply backup: every row's fields
other than `ru` are byte-identical; stripping every newly-added `<ls n="...">...</ls>` wrapper
from each changed row's `ru` reproduces the backup's `ru` exactly (zero drift beyond the
wrapper itself). Verified idempotent: a second `apply` run reports 0 rows changed, 0 new
`resolved + marked`.

## Verification

- `python -m pytest tests/` (full RussianTranslation suite): 103/104 pass. The 1 failure
  (`test_apply_round_trip_on_a_scratch_store::test_apply_round_trip_on_a_scratch_store`
  backup-filename assertion) reproduces byte-for-byte identically on the unmodified
  pre-H1909 code — pre-existing, unrelated to this change, not touched.
- `python -m pytest tests/test_nws_ls_markup.py`: 20/21 pass (same pre-existing failure); 8
  new tests added, one per discriminator branch plus one end-to-end `apply()` fixture
  exercising all of them in a single row.
- `python -m py_compile RussianTranslation/src/nws_ls_markup.py`: clean.
- Byte-diff verification script (backup vs. post-apply store): 110 rows changed, 195 net
  `<ls>` tags added, 0 other-field changes, 0 mismatches beyond the `<ls>` wrapper.

_Dr. Mārcis Gasūns_
