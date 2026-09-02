# PWG `<ab>`/`<ls>` abbreviations — tooltips and RU-column purity

_Created: 10-07-2026 · Last updated: 02-09-2026_

> Consolidated Russian style guide of record (all ratified rules, with provenance and the
> open 10-07 vs 19-07 abbreviation contradiction surfaced):
> [PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md) (H1859).
> Provenance of the three rulings behind this file, its limitations, and the ranked
> improvement backlog: [ABBREVIATIONS_RU.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.meta.md).

## Why this exists

MG flagged (10-07-2026, via the `mena` article on the public site) two problems
with the [PWG article site](https://gasyoun.github.io/SanskritLexicography/):

1. German `<ab>` grammar/usage abbreviations and `<ls>` literary-source sigla
   had no tooltip explaining what they stand for — unlike
   [sanskrit-lexicon.uni-koeln.de](https://sanskrit-lexicon.uni-koeln.de), whose
   convention this project is expected to match. He also asked for a
   corpus-wide dashboard of abbreviation usage, not just per-article.
2. The Russian (RU) column of the translated text still contained raw German
   inside `<ab>` tags — `s. u.` (German "siehe unter") is Russian `см.`, and
   must not be left untranslated in Russian prose. His own examples:
   `mena s. u. menā.` → RU should read `mena см. menā.`, and
   `Bein. Vṛṣaṇaśvaʼs` → RU should read `эпит. Вришанашва` (Cyrillic name, not
   IAST).

An audit of `RussianTranslation/src/pwg_ru_translated.jsonl` (11,275 rows,
2026-07-10) found this was not a small issue: **12,151 of 12,152 `<ab>`
occurrences in the RU field (99.99%) were still verbatim German/Latin**, across
265 distinct tokens.

## Case government (Rektion) — owned by government.html, not this dashboard (H1308)

MG's DA-vote row **N2** (19-07-2026, card `vas~~h0_zz_pw00|samava`) asked a
different question of the same `<ab>` markup: given a sense carrying
`(<ab>Instr.</ab>)`, *can I find every card with Instr. government in one click?*
That is **card retrieval**, not token frequency — so it lives on its own page, the
[government (Rektion) index](https://gasyoun.github.io/SanskritLexicography/government.html)
(case chips Instr./Loc./Gen./Acc./Dat./Abl. → every card governing that case, with
an honest floor-vs-ceiling coverage banner), NOT inside this abbreviations
dashboard. Ruling: **two pages, cross-linked** — `abbreviations.html` stays
token-frequency oriented, `government.html` is card-retrieval oriented; merging
would bury N2's one-click ask. Extractor: `government_census.extract_government()`,
now case-insensitive so the PW `zz_pw*` capitalized stratum (`(<ab>Instr.</ab>)`,
1,116 rows previously invisible) is captured alongside the PWG lowercase one. See
[H1308](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1308-Opus_RussianTranslation_pwg-ru-valency-government-index_19.07.26.md).

## Architecture decision: fix at RENDER TIME, not in the data store

The translated JSONL store (`pwg_ru_translated.jsonl`) keeps the `<ab>`/`<is>`
tags and their **raw German/IAST content untouched** — this already matches
how `<ls>` citations and `{#...#}` Sanskrit lexical forms are stored (source-
faithful, presentation decided by the site generator). So the fix lives
entirely in
[`RussianTranslation/src/pilot/build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py)'s
`_render()` function, which now takes a `lang` parameter (`'de'`/`'ru'`/`'en'`)
and treats `<ab>`/`<is>` differently per language column:

* **`<ls>` (literary-source sigla, e.g. `ṚV.`, `AV.`)** — unchanged text in
  every language, but now every resolvable siglum gets a `title=` tooltip with
  its full source name (from PWG's own 2,681-entry bibliography,
  [`pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py)).
* **`<ab>` (grammar/usage abbreviations)** — every language gets a `title=`
  tooltip with the authoritative German/English expansion (PWG's own 791-entry
  table,
  [`pwg_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab.py)).
  **Only the RU column's visible text changes**, per the bucket below.
* **`<is>` (proper names embedded in prose)** — DE/EN keep the IAST spelling;
  RU transliterates to Cyrillic
  ([`iast_to_cyrillic.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/iast_to_cyrillic.py)).

Because this is render-time, **it automatically covers every future
translated root with no prompt change and no reprocessing** — the fix is not a
one-time patch over the current ~11k-row store, it is permanent.

## Decision: grammatical-category abbreviations stay Latin

`<ab>` splits into two buckets, and which bucket a token is in is the whole
question MG asked to investigate ("нужно сделать расследование и понять, какие
[латинские] оправданы").

**Bucket B — grammatical categories (KEPT as international Latin, tooltip
only).** Case/mood/voice/tense/aspect/part-of-speech labels — `Acc.`, `Loc.`,
`caus.`, `pass.`, `aor.`, `sg.`, `masc.`, `partic.`, `subst.` … This is ~75% of
all `<ab>` volume (measured: 9,000 / 12,152). Decided via `AskUserQuestion`
10-07-2026: **keep as Latin**, matching both Cologne's own site and worldwide
Indological convention — a hover tooltip is the only change. No mapping table
needed; this is simply "no entry in `RU_MAP`" (the default/fallback path).

**Bucket A — editorial / cross-reference / deictic / domain-label
abbreviations (TRANSLATED to Russian).** These are plain German (or German-
flavoured Latin) function words with no comparable international-scholarly-
Latin status — `s.`/`s. u.` ("see"), `Vgl.` ("compare"), `Bed.` ("meaning"),
`Z.` ("line"), `dass.` ("the same"), and MG's own two examples `Bein.`
("epithet") and (implicitly, via `N. pr.`) "proper noun". The curated mapping
lives in
[`RussianTranslation/src/pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py)
(`RU_MAP`, 122 entries since H3959). ~~Anything NOT in `RU_MAP` falls back to the
original token~~ — that fallback was the defect MG's 02-09-2026 ruling outlawed;
see the next section.

## Ruling 02-09-2026: "none remain German" — the residue is closed (H3959)

MG voted the [registry-contradictions sheet](https://gasyoun.github.io/vote/sheets/uprava_registry_contradictions_02-09-26.html)
on 02-09-2026 (3 cards, all approved, 120 s):

> **«It's mixed. Some remain Latin, none remain German, most German become Russian
> and do not become Latin»**

That is the two-bucket policy above, approved, plus one constraint it had never
asserted and one direction correction:

1. **"Some remain Latin" = Bucket B, unchanged.** Grammatical categories keep the
   international Latin siglum. Not up for revision.
2. **"Most German become Russian" = Bucket A, unchanged in principle.**
3. **"and do not become Latin" — a direction correction.** The H2849 sweep's
   German→Latin direction (`Akk`→`Acc.`, `Lok`→`Loc.`) is right for Bucket B and
   **forbidden for Bucket A**: an editorial German abbreviation goes to Russian,
   never to Latin.
4. **"None remain German" — the new constraint, and the defect.** The 10-07
   design fell back to the raw token for anything not in `RU_MAP`, so a residue of
   Bucket-A tokens rendered as German inside Russian prose *by design*.

### The four-bucket census (H3959, 02-09-2026)

Method: every `<ab>…</ab>` span in the `ru` field of all 11,519 rows of
[`src/pwg_ru_translated.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src), whitespace-normalised, counted by
occurrence and by distinct token, then classified against the three explicit sets in
[`src/pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py).
Reproduce with `python pwg_ab_ru.py census` (exit 1 if any A-unmapped token survives).

Total: **12,194 occurrences / 272 distinct tokens.**

| Bucket | Occurrences | % | Distinct | % |
|---|---:|---:|---:|---:|
| B — stays international Latin | 6,465 | 53.0 % | 137 | 50.4 % |
| A-mapped — renders Russian from `RU_MAP` | 5,711 | 46.8 % | 121 | 44.5 % |
| residue — declared undecided | 18 | 0.1 % | 14 | 5.1 % |
| **A-unmapped — renders raw German** | **0** | **0.0 %** | **0** | **0.0 %** |

The three sets are now spelled out rather than inferred: `RU_MAP` (Bucket A),
`BUCKET_B` (138 grammatical sigla), `RESIDUE` (14 declared-undecided tokens). They
are disjoint, and anything outside all three is by definition A-unmapped — which is
what `census` fails on. Before H3959 that fourth bucket held 26 distinct tokens /
409 occurrences; the largest were `u.` (93, "unter"), `v. l.` (283, *varia lectio*)
and `ved.` (57, "vedisch").

All 122 `RU_MAP` values are Cyrillic — `census` asserts this, so no Bucket-A token
can be routed to Latin without failing the check.

### Judgment calls worth naming

- **`u.` → `под`.** PWG's own `pwgab` expands it as *unter*, not *und* — the
  preposition of the "see under ⟨headword⟩" formula, so a Russian preposition, not `см.`
- **`v. l.` → `разночт.`** *Varia lectio* is Latin, but it is **editorial**, not a
  grammatical category, so "some remain Latin" (= Bucket B) does not cover it.
  Russian textology has its own established siglum.
- **`ved.` → `вед.`, `metr.`, `euphem.`, `myst.`, `etymol.`, `Patron.`** — register,
  domain and usage labels, the same class as `buddh.`/`astr.`/`liturg.` and `Bein.`,
  which already translated.
- **`unregelm.`, `ungramm.`, `Ortsadv.`** are grammar *properties* spelled as German
  adjectives, not the Latin termini technici `Acc.`/`caus.` — Bucket A, not B.
- **`Präs.`, `instrans.`** stay Bucket B: `Präs.` is the tense category (orthography
  is not the criterion), `instrans.` is PWG's own typo for *intransitiv*.

### Declared residue — 14 tokens, 18 occurrences

Two admissible reasons only: no entry in PWG's own `pwgab` table, or a `pwgab`
entry that is itself ambiguous or garbled. A guessed Russian gloss for a garbled
token would put invented Russian into a dictionary; a declared undecided token
costs one row.

| Token | Occ. | Why undecided |
|---|---:|---|
| `e.` · `H.` · `o. W.` · `o.` | 2 each | no `pwgab` entry (`o.` is probably *oben*, but PWG never declares it) |
| `M.` · `Fr.` · `schl.` · `r. V.` · `d. r. V.` | 1 each | no `pwgab` entry |
| `3.` | 1 | no `pwgab` entry — numeric markup artifact |
| `geder.` | 1 | `pwgab` itself reads "gedeutet?" — garbled source |
| `d.` | 1 | `pwgab` reads "der / die / das" — ambiguous definite article |
| `pers.` | 1 | `pwgab` reads "Person / persisch" — grammatical vs domain, undecidable |
| `ind.` | 1 | `pwgab` reads "indisch / Indikativ" — domain vs grammatical, undecidable |

### Store-residue verdict (scoped by H3959, SWEPT by H3969 — releases H3947)

**65 store rows need a sweep, scoped as follows.** The `<ab>` policy is render-time
by design and no `<ab>` span needs a store write. But re-running the H2849 class of
check — German markers **outside** any `<ab>` tag, excluding `{#…#}` SLP1 spans and
all markup — finds **120 hits across 65 distinct rows** still in the `ru` field:
`Akk` ×110, `Lok` ×8, `Ausgabe` ×1, `Präs` ×1. By layer: `nws` 48 rows, `sch` 15,
`pwg` 2 — i.e. it is almost entirely the Grassmann/NWS-derived material H2849's
694-row pass did not reach, not PWG's own text. These are Bucket **B** markers, so
the sweep direction is German→Latin (`Akk`→`Acc.`, `Lok`→`Loc.`), the same direction
H2849 used and the one MG's ruling forbids only for Bucket A. Scoping and running
that sweep is **not** H3959.

#### The sweep as it actually ran (H3969, 02-09-2026)

Re-measured before writing anything, and the number had grown: **142 hits across 76
rows**, because the H3959 census above listed only `Akk`/`Lok`/`Ausgabe`/`Präs` while
`Instr` ×22 is the same German-only class with the same H2849 target. All of it was
swept in one pass by
[`src/h3969_german_latin_sweep.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h3969_german_latin_sweep.py)
(`census` · `--apply` · `--selftest`), `ru` field only, store resolved through
`store_path.canonical_store()`:

| Token found | Count | Shipped as |
|---|--:|---|
| `Akk` | 110 | `Acc.` |
| `Instr` | 22 | `Ins.` (H2849's naming choice, `pwg_ab.RENAME_ALIASES` keeps the tooltip) |
| `Lok` | 8 | `Loc.` |
| `Präs` | 1 | `Praes.` — the ASCII Latin twin; `Präs = Fut.` in `key1=yAvat` |

**141 substitutions over 75 rows** — `nws` 58 rows, `sch` 15, `pwg` 2. Store row count
unchanged (11,519 before and after); the German source column `de` untouched. Post-sweep
the check reports **1 hit / 1 row**, and the independent
[`src/ru_case_marker_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ru_case_marker_gate.py)
passes over all 11,519 rows.

**Declared residue — `Ausgabe` ×1** (`key1=nI`, layer `pwg`): *"…dieses Beispiels hat
aber die vollständige Ausgabe der `<ls>`SIDDH. K.…"* is a German **prose clause** left
untranslated in the `ru` field, not a grammatical marker. It has no Bucket B Latin
terminus technicus; routing it to `Ed.` would be an editorial decision, and translating
the clause is a translation job, not a marker sweep. Named here rather than guessed.

**Adjacent, deliberately not swept:** `Istr` (`key1=Cid`, layer `nws`, in
`(голову, Akk, ногой, Istr)`) is a source-side typo for `Instr`, outside every measured
token set. Correcting typos is a different pass; it is recorded here so the next scan
does not treat it as new.

## German case-abbreviation compliance sweep (H2849, 19-08-2026)

The Bucket B rule above was decided but had never been swept against
free-floating case markers that sit **outside** an `<ab>` tag — plain
parenthetical usage notes like `(Akk, Instr)` in the RU field, which the
render-time `<ab>` machinery above never sees because there is no tag to
intercept. 963 substitutions across 694 rows (**59** distinct `key1` entries) in
`src/pwg_ru_translated.jsonl`'s **`ru` field only** (the `de` field is the
German source column and is untouched, per the render-at-render-time
architecture above). The mint estimate (H2849's own pre-measurement) said 72
entries; 13 of those only "matched" via the `[Gen, unsp]` domain-tag false
positive below and are correctly excluded here — the 59 figure is the
post-exclusion, actually-swept count:

| Token found | Count | Canonical form shipped |
|---|--:|---|
| `Akk` | 110 | `Acc.` — unambiguously German, real substitution |
| `Lok` | 8 | `Loc.` — unambiguously German, real substitution |
| `Instr` | 261 | `Ins.` — Latin stem, renamed (see naming choice below) |
| `Abl` | 218 | `Abl.` — Latin stem, period added where missing |
| `Gen` | 173 | `Gen.` — Latin stem, period added where missing |
| `Dat` | 160 | `Dat.` — Latin stem, period added where missing |
| `Nom` | 33 | `Nom.` — Latin stem, period added where missing |

**Naming choice resolved: `Ins.`, not `Instr.`** MG's review instruction wrote
`Ins.`; this doc previously implied `Instr.` nowhere explicitly, but the
sweep's substitution table is a single named constant
(`GERMAN_TO_LATIN`/`LATIN_NORMALIZE` in the sweep script) so a reversal to
`Instr.` is a one-line flag change, not a re-derivation.

**False-positive guard found and excluded — `[Gen , unsp]` domain tags.** A
second, unrelated taxonomy also lives in this store: bracketed period/genre
tags borrowed from the MW-style convention — `[Ved, unsp]`, `[Buddh, Phil]`,
`[Jin]`, `[Reg]`, `[Tan]`, `[Epigr]`, and **`[Gen, unsp]`** where `Gen` means
*"General"* (a text-period label), not genitive case. 38 such `Gen` bracket
occurrences were detected and deliberately **not** substituted — matching
"General" against the genitive-case rule would have made the two senses of
`Gen.` indistinguishable in the data. Detection rule: a token is a domain tag
(and skipped) when it sits inside a bracket span containing **only** bare
Latin tag words joined by `,`/`:` — `\[(?:[A-Za-z]+\.?)(?:\s*[:,]\s*[A-Za-z]+\.?)*\]`
— never Cyrillic, parens, or `=`. One genuine case use nested inside a larger
bracket (`[только śámi (Lok) = Indekl]`) was excluded by this same guard as a
conservative trade-off — it fails the "bare tags only" test because of the
Cyrillic and `=`, so it was left as `Lok` rather than risk a false positive
elsewhere; a human can flag it for a follow-up pass if the single miss
matters.

**Renderer guard list.** `Akk`/`Instr`/`Lok` remain in
`build_reglue_sheet_v2.py`'s `ABBREV` split-guard tuple (harmless — they no
longer occur in swept RU text, but the German-source `de` field and any
future review-sheet input can still contain them); `Acc`/`Ins`/`Loc` were
**added** so a reglue sheet built from the now-Latin RU text does not split a
sentence right after one of these case markers' new stems. The same three
were added to `scan_sheet_latin_chrome.py`'s `ALLOWED_TOKENS`.

**A real regression, found and fixed: `<ab>` tooltips.** 261 of the `Instr`
occurrences sit inside `<ab>Instr.</ab>` tags, and `_ab_display()`
(`pilot/build_article_site.py`) resolves each tag's tooltip by looking the RU
column's own stored token up in
[`csl-pywork/v02/distinctfiles/pwg/pywork/pwgab/pwgab_input.txt`](https://github.com/sanskrit-lexicon/csl-pywork/blob/main/v02/distinctfiles/pwg/pywork/pwgab/pwgab_input.txt)
— the authoritative PWG print-abbreviation table, out of this repo's control.
That table's own key for the instrumental case is `Instr.` (not `Ins.`), so
renaming the stored token would have silently dropped the tooltip for every
one of those 261 occurrences (`pwg_ab.resolve()` returning `None`). Fixed with
a one-entry alias, `RENAME_ALIASES = {'Ins.': 'Instr.'}`, in
[`RussianTranslation/src/pwg_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab.py)'s
`resolve()` — verified: `python pwg_ab.py lookup "Ins."` now returns the same
`Instrumental / instrumental (case)` expansion as `lookup "Instr."`.

**Affected `key1` entries (59):** Ap, As, Ayuzkara, BerI, Bid, Buj, Cid, DA,
KecarI, SaSvat, Sam, aSakta, aSmarI, aSuci, ahar, asvatantra, banD, brU, car,
dA, dah, diS, dyAvApfTivI, gA, gAyatrI, gam, hA, han, hi, jIv, jYA, jan,
jananI, ji, mA, mad, mahat, man, muc, nI, naS, nirbIja, pA, pat, prota, rakz,
siD, su, vA, vac, vad, vah, vas, viS, vid, vraj, yA, yaj, yat.

## Two data-level collisions found and fixed

Some already-translated cards paraphrase the abbreviation by hand in the
surrounding RU prose **and** leave the tag — both `_ab_display()` and
`_is_display()` in `build_article_site.py` guard against these with
lookaround context checks (see their docstrings for the exact mechanism):

1. **Doubled "see"**: stored RU text `см. <ab>s. u.</ab> menā` — the
   translator had already written `см.` by hand; rendering our own `см.` for
   the tag too produced `см. см.`. Fixed by checking the text immediately
   before the tag and suppressing a redundant repeat.
2. **Doubled vowel in transliterated names**: `<is>Vṛṣaṇaśva</is>а` — an
   a-stem Sanskrit name transliterates to `Вришанашва` (already ending in
   `-а`), and the translator had glued a bare Russian case-vowel `а` directly
   after the tag (assuming the tag's content was a bare consonant stem) →
   `Вришанашваа`. Fixed by checking the character immediately after the tag
   and dropping our own trailing vowel when it would collide with a glued-on
   Russian ending.

## Known residual risk / open items (not solved here — future work)

* **`iast_to_cyrillic.py` is a first-pass transliterator**, not a validated
  scheme. Known weak spots are documented in its own docstring (semivowel
  y/v-glide coalescence not modeled, visarga handling is a heuristic,
  capitalization only on the first word of a multi-word name). It has been
  spot-checked on the `mena` article's two names (`Vṛṣaṇaśva` →
  `Вришанашва`, `Himavant` → `Химавант`) but **not** validated across the
  full corpus of `<is>` spans. A dedicated QA pass (sample + human review, or
  cross-check against any names Кочергина/Елизаренкова already transliterate)
  is recommended before treating this as authoritative — see the mint
  handoff.
* **`'med.'`/`'medic.'`** resolve in `pwgab` as "Medizin/medicine" (a
  subject-domain label) and are translated to `мед.` on that basis. If a
  genuine grammatical "medium voice" sense shares the bare token `med.`
  anywhere in the corpus (pwgab's table only stores one meaning per token
  string), that occurrence would be mistranslated. Not observed in a spot
  check but not exhaustively verified either.
- ~~**`RU_MAP` is a first pass covering the highest-frequency tokens (~95 of 266
  distinct)**~~ — **closed by H3959, 02-09-2026.** Every one of the 272 distinct
  tokens the corpus actually uses is now classified into exactly one of `RU_MAP`,
  `BUCKET_B` or `RESIDUE`, and `python pwg_ab_ru.py census` fails if any falls
  outside all three. It is still *not* an audit of the full `pwgab` table (791
  entries): a token that first appears as the corpus grows will surface as
  A-unmapped on the next census run, which is the intended way to catch it —
  append, don't rebuild.
* **Scope is `pwg_ru` only.** `mw_ru`'s `<gram>` tag has a *documented*
  "deliberately left untouched, do not fix" convention in the org
  [`CLAUDE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md)
  (a different, independent pipeline) — this change does **not** touch or
  override that. Whether `mw_ru` has the same German/Latin-leak problem is an
  open question, not investigated here.

## `<ls>` link enrichment (Pāṇini · Spr. · DHĀTUP.) — H1307

Three `<ls>` citation classes gain reader-facing enrichment on the pwg_ru
surfaces (article site now; review sheets via the shared `_render()`/`_ls_tooltip`
layer). Wired 19-07-2026 (Opus 4.8, `claude-opus-4-8`), born of MG's DA-sheet vote
(register rows N14 · N3(b) · N15 in
[H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md)).
All work extends the existing Cologne-port resolver
[`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
+ render layer — no second resolver.

### Coverage

| class | total | linked | linked % | tooltip | full-text enriched |
|---|--:|--:|--:|--:|--:|
| `P.` (Pāṇini) | 25351 | 25065 | 98.9% | 25349 | — (n/a) |
| `Spr.` (1st ed) | 13133 | 12953 | 98.6% | 13133 | — (n/a) |
| `Spr. (II)` (2nd ed) | 8684 | 8684 | 100.0% | 8684 | 8395 |
| `DHĀTUP.` | 2760 | 2659 | 96.3% | 2760 | — (n/a) |

- **Full-form Pāṇini `P. a,p,s` (3-param):** 25061 / 25061 linked (**100.0%**) — the H1307 DoD target.
- **`Spr. (II) N` (2nd ed):** 8684 / 8684 linked (**100.0%**), 8395 full-text enriched (96.7% of linked).

_Denominator: full source [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt) — the RU store
`src/pwg_ru_translated.jsonl` was absent on this machine, so per H1307 Prerequisite 1 the
count uses the whole PWG corpus (a superset of the RU-translated subset). Recompute against
the store when present: `python src/ls_coverage.py --md` (raw JSON → gitignored
`pwg_ru/eval/ls_coverage.json`). Generated 19-07-2026._

### Pāṇini `P.` → ashtadhyayi.com

The full form `P. adhyaya,pada,sutra` deep-links to
`https://ashtadhyayi.com/sutraani/{adhyaya}/{pada}/{sutra}` (unchanged; the N14
continuation form `n="P. 2,3,"` + visible `10.` resolves to `/sutraani/2/3/10` by
concatenation). **URL-form verification:** ashtadhyayi.com is a client-side SPA, so a
live HTTP 200 proves nothing (an invalid `/9/9/9` also returns 200 with the same shell).
The form was instead verified against the site's own authoritative backing data repo
[`ashtadhyayi-com/data`](https://github.com/ashtadhyayi-com/data) (`sutraani/data.txt`:
fields `a`=adhyaya, `p`=pada, `n`=number; 1.1.14 = निपात एकाजनाङ्), confirming the
adhyaya/pada/sutra decomposition. **Browse affordance** (MG's N14 "list of sūtras by
chapter and book"): a 2-param `P. a,p` links to the pāda list `/sutraani/{a}/{p}` and a
1-param `P. a` to the adhyāya list `/sutraani/{a}` — the site's own browse routes, no
local sūtra list built. Both patterns are **guarded** to Pāṇini's real ranges (pada 1–4,
adhyāya 1–8) so ambiguous or non-sūtra forms never mislink: `P. 1,23` (23 is no pada),
`P. 1,6` (pada 6), and the page-reference form `P. II, S. 3` (Böhtlingk vol. II, Seite 3
— **not** a sūtra) all correctly stay unlinked.

### `Spr.` / `Spr. (II)` → Indische Sprüche

Edition routing is unchanged and was **live-verified** this session: plain `Spr. N`
(1st ed) → [boesp1](https://sanskrit-lexicon-scans.github.io/boesp1/app1/?1415) and
`Spr. (II) N` (2nd ed) → [boesp2](https://sanskrit-lexicon-scans.github.io/boesp2/web1/boesp.html?6145),
both via a **bare `?N`** query. Verified against the viewers' own `main.js`: boesp2 accepts
both `?N` and `?verse=N`; boesp1 accepts **only** `?N` — so the resolver's bare-`N` form is
the single one that works uniformly, and switching to `verse=N` (as one README documents)
would silently break every 1st-ed link. No resolver change was needed. **Full-text
enrichment** (MG's N3(b)): every `Spr. (II) N` gains a hover tooltip carrying the saying's
IAST verse + German translation from the recognized full text
([`indische_sprueche.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/data/indische_sprueche.jsonl),
7,537 sayings numbered 1–7878 with 341 numbering gaps), while keeping the boesp2 href.
**Edition guard** ([PWG#87](https://github.com/sanskrit-lexicon/PWG/issues/87)): the 1st-ed
`Spr. N` (5,419 sayings) is a *different* edition and is never resolved against the 2nd-ed
JSONL — `spr_fulltext.second_ed_num()` matches only the `Spr. (II) <digit>` form. The 3.3%
of linked `Spr. (II)` refs left unenriched fall in the JSONL's numbering gaps (plus one
lone source-data typo, `Spr. (II) 15802`, beyond the edition's range — it links but cannot
enrich, never mis-enriches).

### `DHĀTUP.` → Palsule — SPEC'D-NOT-WIRED (acquisition spec)

MG's N15 asks that `DHĀTUP. x,y` citations cite the Palsule list. **Verdict: cannot be
wired from existing data — spec only.** A local hunt (SanskritGrammar
[`PALSULE_AUDIT.md`](https://github.com/gasyoun/SanskritGrammar/blob/main/GasunsDhatu_2014/revision-2026/PALSULE_AUDIT.md),
WhitneyRoots, [kosha datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json),
SanskritLexicography [FINDINGS §63](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md))
found **no** machine-readable Palsule-numbered dhātupāṭha and **no** Böhtlingk/Westergaard→Palsule
concordance anywhere in the org. The only machine-readable list is the vidyut dhātupāṭha
(2,259 dhātus, keyed by gaṇa.sūtra, SLP1) — a *different* numbering. PWG's `DHĀTUP. x,y` is
Böhtlingk's own gaṇa-arranged edition (x=gaṇa, y=serial-within-gaṇa); Palsule assigns its
own ~3,690-entry numbering. The current resolver already links `DHĀTUP. x,y` to the
Westergaard scan viewer at gaṇa level (2,659/2,760 = 96.3%); that stays. **Acquisition spec
to deliver Palsule references:** (a) digitize Palsule's numbered list from the print source
(G.B. Palsule, *The Sanskrit Dhātupāṭhas*); (b) build a verified Böhtlingk-`DHĀTUP.`↔vidyut
gaṇa.sūtra crosswalk; (c) normalize ablaut/citation-form (per FINDINGS §90 and the H328
negative result: a naive it-stripped join matched only 454/930 Whitney roots). Natural owner:
article **A39** ([Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)).
**No fabricated links.**

## Mechanical RU style rules (no-ё, terse metalanguage) — H1305

A separate, purely mechanical style stream lives in its own doc, not here:
[RU_STYLE_MECHANICAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md)
— no letter ё anywhere in RU output (whitelist: standalone «всё»/«Всё» only), «вместо»→«вм.»,
«в значении»→«в знач.» in editorial metalanguage, and `ed. Bomb.` → «Бомбейская ред.» in free
prose only (never inside `<ls>…</ls>`, which this doc's `<ls>` tooltip/link-enrichment layer
above still resolves against the verbatim Latin siglum). Distinct from the `<ab>`/`<is>`
render-time abbreviation-translation policy documented above: R1–R4 are STORE-LEVEL fixed
substitutions (swept once into `pwg_ru_translated.jsonl`, not a render-time transform), and
purely orthographic/terseness, not a translation-of-record decision.

## Files touched

* [`RussianTranslation/src/pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py) — new; the DE→RU editorial-abbreviation map + coverage CLI.
* [`RussianTranslation/src/iast_to_cyrillic.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/iast_to_cyrillic.py) — new; best-effort IAST→Cyrillic transliterator for `<is>` proper names.
* [`RussianTranslation/src/pilot/build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py) — `_render()` gained a `lang` parameter; `<ab>`/`<ls>` tooltips; `<is>` Cyrillicization; new `abbreviations.html`/`abbreviations.js` dashboard (`ab_frequency()` + `emit_abbreviations()`).
* `RussianTranslation/article_site/` — regenerated output (147 roots, 11,275 senses at time of writing).

H1307 `<ls>` link enrichment (19-07-2026):

* [`RussianTranslation/src/ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py) — guarded Pāṇini 2-param (`/sutraani/a/p`) and 1-param (`/sutraani/a`) chapter/book browse patterns.
* [`RussianTranslation/src/spr_fulltext.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/spr_fulltext.py) — new; Indische Sprüche 2nd-ed full-text lookup + `Spr. (II)` edition guard, for tooltips.
* [`RussianTranslation/src/pilot/build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py) — `_ls_tooltip()` (Spr. (II) full text over source title), wired into the html tooltip + md link title.
* [`RussianTranslation/src/ls_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_coverage.py) — new; per-class `<ls>` coverage counter (store, else pwg.txt).
* [`RussianTranslation/src/pilot/ls_enrichment_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/ls_enrichment_selftest.py) — new; fixture selftest, wired into the RussianTranslation CI gates.

H1305 mechanical RU style sweep (19-07-2026):

* [`RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md) — new; rules R1–R4, false-positive measurement, sweep counts.
* [`RussianTranslation/src/ru_style_sweep.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ru_style_sweep.py) — new; store sweep + shared violation detector (`--apply`/`--selftest`/`--wf`).
* [`RussianTranslation/src/pilot/audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) — new `ru_style` RU-only gate.
* [`RussianTranslation/src/pilot/run_pilot_wf.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_pilot_wf.js) — HARD RULE 9 (R1–R4) in the `CONV`/`TR` template.
* [`RussianTranslation/src/pilot/prompt_rule_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py) — `ru_style_*` rule pins.

_Dr. Mārcis Gasūns_
