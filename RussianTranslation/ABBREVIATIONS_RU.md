# PWG `<ab>`/`<ls>` abbreviations — tooltips and RU-column purity

_Created: 10-07-2026 · Last updated: 09-09-2026_

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
| `DHĀTUP.` | 2760 | 2659 | 96.3% | 2760 | 1933 |

- **Full-form Pāṇini `P. a,p,s` (3-param):** 25061 / 25061 linked (**100.0%**) — the H1307 DoD target.
- **`Spr. (II) N` (2nd ed):** 8684 / 8684 linked (**100.0%**), 8395 full-text enriched (96.7% of linked).
- **`DHĀTUP. x,y` → Palsule (H1333 + H4339, unchanged by H4349):** 2657 / 2760 citations carry
  a gaṇa,serial coordinate (the rest are gaṇa-only `DHĀTUP.`, which has no root to key on);
  **1933 of those (72.8%)** resolve to a Palsule artha-index record — **1465 of the 1751 distinct
  coordinates PWG cites (83.7%)**, of which 1226 (70.0%) are Böhtlingk's own attribution and 239
  come from the Monier-Williams second witness added by H4339 (marked `[MW]` in the tooltip,
  `source` in the data). The remaining
  shortfall is honest and of two kinds: coordinates no dictionary
  attributes unambiguously (`skand`/`skund`, `cut`/`cyut`) and roots absent from Palsule's artha
  index (`edh`, `vīj`). **H4349 closed the last two untried PWG-family sources and found both
  empty** — PWG's 636 dotted-id articles cite one coordinate between them and PWG itself
  contests it; pw cites 40 and every one is either already present, refused as a same-author
  vote on a coordinate Böhtlingk himself left split, or refused as a coordinate pwg does not
  cite. Enrichment is **tooltip text only** — Palsule has no online
  edition — and the gaṇa-level Westergaard link is unchanged.

_Denominator: full source [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt) — the RU store
`src/pwg_ru_translated.jsonl` was absent on this machine, so per H1307 Prerequisite 1 the
count uses the whole PWG corpus (a superset of the RU-translated subset). Recompute against
the store when present: `python src/ls_coverage.py --md` (raw JSON → gitignored
`pwg_ru/eval/ls_coverage.json`). Generated 19-07-2026; DHĀTUP.→Palsule row re-run 08-09-2026 (H1333, H4339, then H4349)._

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

### `DHĀTUP.` → Palsule — WIRED 07-09-2026 (H1333)

MG's N15 asked that `DHĀTUP. x,y` citations cite the Palsule list. H1307 could only ship an
**acquisition spec**: no machine-readable Palsule-numbered dhātupāṭha and no
Böhtlingk/Westergaard→Palsule concordance existed anywhere in the org (hunt: SanskritGrammar
[`PALSULE_AUDIT.md`](https://github.com/gasyoun/SanskritGrammar/blob/main/GasunsDhatu_2014/revision-2026/PALSULE_AUDIT.md),
WhitneyRoots, [kosha datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json),
[FINDINGS §63](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).
**H1333 closes the arm** from the XLS MG supplied (Palsule's *artha* index, rights cleared by
MG 07-09-2026; raw file stays gitignored in `pwg_ru/eval/`, only the derived table ships).

**The join, and why it is not the one the spec feared.** The XLS carries **no** Böhtlingk
coordinate — 8,170 rows of `<artha> : ⎷<root> <pada>` with a Palsule page, keyed on the root.
But PWG *is* Böhtlingk: a `<ls>DHĀTUP. x,y</ls>` sits inside the article of the very root it
numbers, and that article's `<k1>` key is the dhātu in SLP1. So the coordinate→root half is
**read off Böhtlingk's own text**, not guessed — the ablaut-normalization risk the H328
negative result flagged (a naive it-stripped join matched 454/930 Whitney roots) never binds
it. Only root→Palsule is a join, across two transliterations of the same citation form.

**Two filters, both honest.** A coordinate is kept only when its citing articles agree on the
root. Where they disagree, a head-line citation outranks a body one (Böhtlingk states the
numbering on the root's own head line), and a nominal claimant — an article carrying `<lex>`,
which quotes the coordinate only as a gloss (`{#loqana#}¦ <lex>n.</lex> … als Erkl. von
{#bAD#} <ls>DHĀTUP. 2,4</ls>`) — is dropped in favour of the verbal one. What remains
ambiguous (Böhtlingk's own double spellings, `skand`/`skund`) is **dropped, never resolved by
citation count**.

**Coverage:** 1,226 / 1,751 distinct coordinates (70.0%), 1,441 / 2,760 citations (52.2%; 54.2% of the 2,657 that carry a coordinate at all) — both re-derivable from `python src/ls_coverage.py --md`, which is where the citation-level tally lives; the builder counts coordinates, not citation occurrences.
Without the two filters the same build links 1,144 (65.3%), so they are worth 4.7 points —
`_stats.match_rate_without_filters` in the committed table, not an assertion.

**Accuracy is a different number, and it is measured.** Böhtlingk frequently prints the
dhātupāṭha's own artha in SLP1 parentheses beside the citation — `{#sni/hyati (prItO)#}
<ls>DHĀTUP. 26,91</ls>`, `<ls>DHĀTUP. 22,30</ls> ({#gatinivfttO#})` — which is an
**independent witness**: it comes from PWG, our glosses come from the XLS. Over the 232
coordinates where he prints one, the artha he names is in our record **139 times exactly
(59.9%)** and 174 times allowing for citation-form variation (75.0% — a deliberately weak
test that accepts `ched` for *chede* and `mandāyāṃ gatau` for *mandāyāṁ gatau*). Both
numbers are re-derivable: `python src/build_dhatup_palsule.py` → `_stats.inline_artha_*`.

**A record is root-level, not coordinate-level.** Palsule's artha index is keyed on the
root, so it cannot separate the homonyms Böhtlingk numbers apart: `DHĀTUP. 26,91` is the
divādi `snih`, but its record carries the arthas of *every* `snih` in Palsule. Read a
tooltip as «what Palsule records for this root», never «what Palsule records at exactly
this coordinate». This is the main reason the strict agreement rate is 59.9% and not
higher — the right artha is nearly always present, alongside others that belong to a
homonym.

**No fabricated links.** Palsule's *Concordance* has no online edition, so the datum ships as
hover text carrying the printed page siglum (`DHĀTUP. 26,91 — Palsule √snih (P175, P186, …):
gatau, prītau, snehane, …`), never as an href. The existing gaṇa-level Westergaard scan link
(2,659/2,760 = 96.3%) is **untouched** — Palsule is an addition, not a replacement.

**Where it lives:** builder
[`src/build_dhatup_palsule.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dhatup_palsule.py)
→ committed table
[`src/data/dhatup_palsule.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/data/dhatup_palsule.json)
→ runtime
[`src/dhatup_palsule.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/dhatup_palsule.py),
wired into the shared `build_article_site._ls_tooltip` beside the `Spr. (II)` case (so the
H1301 review sheets inherit it) — no second resolver. Fixtures in
[`src/pilot/ls_enrichment_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/ls_enrichment_selftest.py).
Natural owner as a dataset/paper: article **A39**
([Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)).

### `DHĀTUP.` second coordinate witness — Monier-Williams — H4339, 07-09-2026

H1333 stopped at **1,226 / 1,751 coordinates (70.0%)** because Böhtlingk is his own only
witness: where he spells one root two ways (`skand`/`skund`), his text cannot say which he
numbered, and the coordinate was dropped rather than guessed. The
[reuse survey](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/REUSE_SURVEY_DHATUPATHA_COORDINATE_SOURCES_07-09-2026.md)
found the second witness already in the estate: **Monier-Williams cites the same Böhtlingk
coordinates**, with the gaṇa in Roman numerals (`Dhātup. xxiv, 68` = 24,68).

**Two channels, and the structured one wins.** MW carries the coordinate twice: in running
prose (`<ls>Dhātup. iii, 1</ls>`) and in its own editorial field
(`<info westergaard="ata,3.1,01.0033"/>`). They are not equally trustworthy, and the case that
settles it is coordinate **3,1**: MW's `pad` article cites `Dhātup. iii, 1` only to note that
`padati` is a variant reading for `badati` — reading the prose would hand 3,1 to `pad`, while
MW's own field at that very article names `ata` (= PWG's `at`, which is right). So the rule is
**field first**: where MW has numbered a coordinate itself, prose is not consulted at all — not
even as a fallback when the field names nobody usable. That is stricter than counting prose
citations and it also yields *more* usable coordinates (241 against 193), because removing
spurious claimants un-ambiguates coordinates that two prose citations had made look contested.

A field claimant counts only when the article's own headword occurs inside the Westergaard root
token the field names (`dIDI` in `dIDIN`, `cyut` in `ScyutiR`, and `pad` **not** in `ata`).
Westergaard's citation forms carry anubandhas at both ends, and stripping them by rule is
exactly the **H328** negative result (a naive it-stripped join matched 454/930) — so containment
is the test and the misses are accepted. One such conservative miss is `2,8` itself: MW's field
does number it (`skudi,2.8`, i.e. for `skund`), but `skudi` carries the nasal as an
anubandha-marked infix, so the headword is not contained in it and the coordinate stays dropped.

**Coverage: 1,226 → 1,465 of 1,751 (70.0% → 83.7%).** Two fill classes, never merged:

| `source` | rows | what it means |
|---|--:|---|
| `pwg` | 1226 | Böhtlingk's own attribution — H1333's rule, unchanged |
| `mw` | 140 | PWG named no single root; MW claims the coordinate for exactly one |
| `mw-respell` | 99 | PWG named a root Palsule does not gloss; MW spells it as Palsule does (`vark`/`vṛk`) |

`mw-respell` is the materially weaker class — it prefers one dictionary's citation form over the
other's — so it is stamped apart, keeps `pwg_root_slp1` on the record, and renders as `[MW sp.]`
against plain `[MW]`. A PWG row is unmarked. **MW never overrides a shipped PWG row**; a
`mw-respell` row displaces nothing, because PWG had no Palsule-glossable row there at all.

**Cross-validation — the confirmation H1333 never had.** Where both dictionaries resolve a
coordinate to a single root, they can be compared: **633 of 815 agree outright (77.7%)**, and
**696 (85.4%)** counting the regular guṇa alternation as the citation-form variation it is —
reported as a separate, deliberately weaker number, exactly like the loose artha rate, never
folded into the strict one. The 182 differences are **published in full** in the artifact's
`_mw_disagreements` (with `shipped_reading`, so what a reader sees is never in doubt) and
classified rather than resolved:

| shape | n | example | reading |
|---|--:|---|---|
| `guṇa ar~ṛ` | 63 | 6,16 `arj`/`ṛj` | one root, two citation conventions |
| `other` | 52 | 11,11 `tup`/`tump` | nasal infixes and genuinely different roots |
| `one letter` | 39 | 2,5 `nāth`/`nādh` | variant readings — the H328 class, the interesting ones |
| `stem~root` | 28 | 32,69 `pālay`/`pāl` | derived stem against root |

**Note the survey's numbers are superseded.** It reported 1,309 MW coordinates and 749/802
(93.4%) agreement; this build reads 1,461 (three citation splittings plus MW's dotted article
ids, which the PWG-shaped `<L>` pattern skips) and compares 815 pairs at 77.7%. The rate did not
fall because the data got worse — the sample got larger and the comparison stricter, and the
extra pairs are dominated by the `guṇa ar~ṛ` bucket. Both numbers are re-derivable; this one is
the artifact's.

**MW does not touch the artha axis.** Its glosses are English, so accuracy is still measured
against PWG's own parenthesized artha, and it is now measured **per source**: the H1333 figure
(139/232 = 59.9% strict, 75.0% loose) means exactly what it did, with the MW rows scored
separately (36/71 = 50.7% strict, 67.6% loose) beside it.

### The prose fallback shipped two wrong roots, and which SIDE of the citation a note sits on is the whole rule

**Two adjudication passes, 07-09-2026**, each an independent verifier re-deriving every number from the
merged artifact. Both confirmed the arithmetic; both found a wrong shipped row. Field-first protects a
coordinate only where MW's field *speaks* — where no `<info westergaard>` numbers one, the prose fallback
ran with none of the skepticism that motivated the rule, and the `pad`/3,1 pattern recurred there.

**Pass 1 found the defect.** Coordinate **20,21** shipped as `kṣal` on the strength of

> `<hom>1.</hom> <s>kzal</s> ¦ <ab>v.l.</ab> for √ <s>kzar</s>, <ls>Dhātup. xx, 21</ls>.`

which **assigns 20,21 to `kṣar`** and names `kṣal` as the reading it rejects. PWG's own claimants were
exactly `{kṣal, kṣar}`, both are in Palsule, so the wrong one of two reachable roots shipped. **32,43** is
the same shape (`tāṭayati` *v.l. for* `tāḍay˚` — the coordinate is `tāḍ`'s).

**Pass 2 found the first fix was too blunt**, and this is the part worth keeping. A line-scoped
`<ab>v.l.</ab>` guard destroyed two *correct* rows, because the note means opposite things on opposite
sides of the citation:

| article | text | what it means | verdict |
|---|---|---|---|
| `kzal` 20,21 | `<s>kzal</s> ¦ <ab>v.l.</ab> for √ <s>kzar</s>, <ls>…xx, 21</ls>` | note **before**, same clause — the headword IS the rejected reading | **refuse** |
| `juq` 28,37 | `<ls n="Dhātup. xxviii,">37</ls> (<ab>v.l.</ab> √ <s>jun</s>)` | note **after** — the coordinate is the headword's, `jun` is the variant | **keep** |
| `dAs` 27,32 | `(<ab>v.l.</ab> for <s>dAS</s>, <ls>Vop.</ls>; <ab>ib.</ab> <ls>…xxvii, 32</ls>)` | note before, but a `;` ends its clause — it governs the *Vop.* citation | **keep** |

**Pass 3 found the clause rule counted the wrong parenthesis.** A fourth article settles the last half:

| article | text | what it means | verdict |
|---|---|---|---|
| `paRq` 32,130 | `pile up (<ab>v.l.</ab> for <s>piRq</s>), <ls n="Dhātup.">xxxii, 130</ls>` | the `)` closes the parenthesis the note ITSELF sits in — it does not end the clause, which runs on to the citation | **refuse** |

Counting that `)` blindly shipped `paṇḍ` at 32,130 — a root **both** dictionaries disown. PWG's own `paRq`
article reads `v. l. für {#piRq#}`, and its `piRqay` article attributes 32,130 positively. So the rule is
clause-scoped **with parenthesis depth**: a note disqualifies a citation when nothing between them ends its
clause — a `;`, or a `)` closing a parenthesis opened *before* the note. `w.r.` (wrong reading) is read as
the same construction.

Refusals across the three passes went 162 → 22 → **57**, and the line-scoped version's collateral is
undone: 28,37 ships again and 27,32 is back in the cross-validation *as an agreement*.

**Net cost against the first build: three coordinates, each a root its own source disowns** — 1467 → 1465
(83.8% → 83.7%), with `mw` 143 → 140 and `mw-respell` 98 → 99 (removing spurious claimants un-ambiguates
as well as subtracts, so one coordinate gained a single claimant and shipped). No coordinate is
**re-attributed**: MW gives 20,21 to `kṣar` in words this parser does not read, and inventing that
attribution would be the fabrication the pipeline exists to refuse. Pinned by the added selftest
`test_dhatup_mw_variant_reading_is_never_harvested_as_a_claim`, which asserts every direction.

**Residual, declared rather than guessed.** A note in a *trailing parenthesis* is genuinely ambiguous in
MW's own usage — `juq`'s `(v.l. √ jun)` names the variant, while `SloR`'s 13,15 `(w.r. for pER)` reads the
other way. Those are kept, and 13,15 is field-spoken anyway. The known cost of that policy is **32,21**,
which ships MW's `śamb` where PWG attributes the coordinate to `samb` and calls the other form the variant:
MW's own note there is a bare trailing `(v.l.)` that names nobody, so refusing it would be a guess in the
opposite direction. Recorded here rather than resolved. One further misfire is harmless: 15,32's note
*names* the variant and is refused anyway, but that coordinate is field-spoken, so prose is never consulted.

Three things the first pass left undisclosed and these now publish:

1. **The fallback is measured, not assumed away.** 220 of the 239 MW fills are field-backed; **19** rest
   on running prose alone (`_stats.coords_filled_from_mw_prose_only`) — a genuinely weaker evidence class,
   counted apart and test-bounded to a quarter of the MW rows.
2. **The containment test is case-folded**, which SLP1 does not make innocuous (it conflates ā/a, ī/i,
   ṝ/ṛ, ś/s, ṇ/r). It is *permissive* — it can only admit claimants, never swap one — and the 9 fills that
   depend on it are ones where the strict claimant set is empty, so no attribution turns on it (verified
   independently). `pad` still fails against `ata` either way.
3. **`mw_coords_single_claimant_prose_first`** (1192 against field-first's 1062) makes the policy
   comparison re-derivable from the artifact. It is computed on the **unguarded** prose channel, because
   the policy being compared against is the one that shipped before the guard existed — measuring it on
   the guarded channel would publish a hybrid that never ran. Note these are different quantities:
   prose-first yields more single-claimant *coordinates* and fewer usable *fills* (193 against 241 as
   first measured), because its extra claimants mostly land on coordinates PWG had already resolved.

**Re-derive:** `python src/build_dhatup_palsule.py` (all `_stats` above), and
`python src/build_dhatup_palsule.py --mw "" --pw "" --no-pwg-dotted` rebuilds the PWG-only
H1333 table byte-for-byte (H4349 added the two later switches; both siblings currently fill
nothing, so `--mw ""` alone reproduces the same 1226 rows).

### `DHĀTUP.` third and fourth witnesses — PWG's dotted-id articles and pw — H4349, 08-09-2026

H4339 left two PWG-family sources untouched. Both are now read, and **both are empty**:
coverage stays at **1465 of 1751 (83.7%)**. That is the result, not a failure to reach one —
the value is in knowing *why* each is empty, and in the screens the second one forced.

> **This section was rewritten after an independent verifier refuted the first cut.** That
> version shipped two `pw` rows and reported 83.8%. Both rows were wrong and both are now
> refused; the sequence is documented below rather than quietly overwritten, because the two
> defects are the most reusable thing H4349 produced.

| `source` | rows | what it means |
|---|--:|---|
| `pwg` | 1226 | Böhtlingk's own attribution — H1333's rule, unchanged |
| `mw` | 140 | PWG named no single root; MW claims the coordinate for exactly one |
| `mw-respell` | 99 | PWG named a root Palsule does not gloss; MW spells it as Palsule does |
| `pw` | 0 | every candidate refused — see below |
| `pwg-dotted` | 0 | one coordinate cited, and PWG contests it |

Neither pass widens `_L` in place; each runs **beside** the H1333 pass, so `pwg_entries` and
every shipped baseline are untouched (verified as zero diffs, not as matching row counts).

#### The dotted-id class is one coordinate, not a hidden corpus

`_L`, the pattern H1333 measured PWG on, accepts an all-digit `<L>` id. **636 of PWG's 123,366
articles carry a dotted id** (`<L>26305.560<pc>`) and are invisible to it, which looked like a
large unread evidence class. It is not. Those 636 articles cite **exactly one `DHĀTUP.`
coordinate between them** — `15,89`, in `4. kar`.

That coordinate was already contested without them. `<L>18794` heads it `kfv`, and Böhtlingk's
own prose there says the root is `kṛv`, that it *has been placed under* `1. kar`, and that its
final `-v` "has not the slightest justification"; `<L>69734` claims it for `kar` again in the
Nachträge. Two readings, from the same lexicographer — precisely the shape H1333's
multi-claimant filter refuses to resolve. A dotted-id citation is **the same book**, so letting
it fill that coordinate would break the tie by adding a vote. It is refused by an explicit
same-book guard and pinned by a regression, so a corpus update that puts real coordinates into
that id space fails a test instead of passing silently.

#### pw cites 40 coordinates and contributes none

pw is the *Sanskrit-Wörterbuch in kürzerer Fassung* — Böhtlingk's own abridgement. That makes
it the strongest untapped source after pwg itself, and it is also exactly what disqualifies its
candidates: **same author is not a second witness.**

| what pw's 40 citations are | n |
|---|--:|
| head line of a noun being glossed — refused | 12 |
| body quotation, not an attribution — refused | 4 |
| a coordinate PWG's own multi-claimant filter refused — refused | 11 |
| a coordinate PWG never cites — refused | 3 |
| outside the attested coordinate space — refused | 2 |
| survives every screen — 7 the table already holds, 1 whose root Palsule does not gloss | 8 |
| **shipped** | **0** |

All six terms and their sum are asserted since H4386, in `ls_enrichment_selftest.py`
(`test_dhatup_pw_refusal_split_matches_the_published_table`) and again in
`dhatup_h4349_verify.py` against a count of pw's citations re-read from the corpus. Before that
only two of the six were pinned anywhere, so this table could drift from `_stats` in silence —
and an earlier version of it summed to 42 against its own header of 40. The sum is asserted as a
**partition**: every cited coordinate leaves the screen chain through exactly one bucket, so the
six above plus the two empty ones (`pw_refused_multiple_claimants`,
`pw_refused_variant_reading`) must add to `pw_coords_cited`. The last row's split (7 + 1) is
`pw_coords_overlapping_shipped` and `pw_candidates_without_palsule_row`; the earlier wording,
"the table already has the coordinate", was true of 7 of the 8, not 8.

**The `<lex>` test alone was not enough.** PWG discriminates a noun article by the *presence* of
a `<lex>` tag; pw abridges and often omits it. `{#DAnya#}¦ (von {#Dana#}) {%das Reichsein%}
<ls>DHĀTUP. 20,3</ls>` is a noun meaning "wealth" with no `<lex>` anywhere, and a negative test
admits it as a root — for a coordinate PWG gives to `jal`. Böhtlingk marks verbal articles
**positively**, with `√` on the head line (`*√{#cukk#}¦, {#cukkayati#}`), and that marker
separates all 37 head-line claimants cleanly. The pass therefore *requires* the marker.

#### The two defects an independent verifier found — the reusable part

Both were shipped by the first cut and both are the same underlying mistake: **treating a
same-author source as an independent one.**

1. **`32,56 → cukk` — a same-author vote breaking Böhtlingk's own tie.** PWG splits `32,56`
   between `{#cakk#}` (pwg:120515) and `√{#cikk#}` (pwg:126200, itself marked `<ab>v. l.</ab>`),
   so H1333's filter drops it; MW gives it to `cakk` too. PWG puts `cukk` at **`34,21`**
   (pwg:128203). The first cut passed the same-book screen to the `pwg-dotted` call and *not* to
   the `pw` call, so pw's `cukk` filled a coordinate two witnesses assign elsewhere. The screen
   now applies to both siblings — MW keeps its exemption, being a different author, which is
   the whole coverage argument of H4339.

2. **`33,67 → tras` — a coordinate PWG does not cite, counted against a denominator excluding
   it.** The ceiling screen bounds a serial against the highest attested in its gaṇa; `33,67`
   clears gaṇa 33's ceiling of 130 and PWG still never cites it. Böhtlingk **renumbered between
   editions**: pw's `2. *√{#tras#}¦, {#trAsayati#} ({#DAraRe, grahaRe, varaRe#})` at `33,67`
   (pw:193921) is pwg's `2. {#tras#}¦, {#trAsa/yati#} {%halten%} (<ab>v. l.</ab> {%ergreifen;
   zurückhalten%})` at `33,88` (pwg:155012) — one article, three matching glosses, two serials.
   Since `match_rate` divides by the set PWG cites, shipping it counted a row its own
   denominator excluded, and the advertised 83.8% was arithmetic on mismatched sets. A membership
   screen now runs beside the ceiling screen, and the standalone verifier asserts
   `set(table) ⊆ cited` directly — it could not see this before, because it derived the ceilings
   from `cited` and then tested only against the ceilings.

A third, latent defect was reported in the same pass and is now guarded — though the guard is **order-shadowed and refuses nothing as shipped**, which the first version of this section did not say. `pw_refused_variant_reading` is `0`, and a second independent verifier proved the guard inert by deleting it and getting a byte-identical artifact. The reason is screen order: pw has exactly one such citation, `31,32`, and PWG cites that coordinate for three claimants (`plI` pwg:254914, `lvI` pwg:420914, `vlI` pwg:470515), so the same-book screen refuses it first. Removing the same-book screen makes the variant-reading guard's COUNTER fire (`pw_refused_variant_reading` 0 → 1) — but not the artifact: an adversarial verifier rebuilt with the same-book screen off, and with both it and the variant guard off, and got the same 1466-row table either way (H4386, 08-09-2026). So the guard changes no shipped row even un-shadowed, and the earlier wording here, which said only that it "fires", read as more than that. It is kept as a **standing** guard, not a live one: the construction is real in pw and the next sibling pass need not be same-book conflicted. **pw uses the
variant-reading construction at a `DHĀTUP.` citation** — `*√{#plI#}¦, {#plinAti#} ({#gatO#}).
<ls>DHĀTUP. 31,32</ls>, <ab>v. l.</ab>` (pw:309560) — and the pass had no equivalent of H4339's
MW guard. In the Böhtlingk family the note follows the citation and marks the *article's own
headword* as the rejected reading, which is the mirror image of MW's leading `v.l. for √X`; it
is therefore a separate pattern, not a reuse. 364 PWG claimants carry it.

#### Adjudication — `DHĀTUP. 1,840` and `1,960` are refused

pw's Nachträge carry two citations no other witness echoes:

- `√{#can#}¦ II. {#ca/nati#} ({#hiMsArTa#}) <ls>DHĀTUP. 1,840</ls>` — a genuine `√`-marked
  verbal article, and Palsule glosses `can`. **It would have shipped.**
- `{#Kadana#}¦ II. <lex>n.</lex> {%das Festsein%} <ls>DHĀTUP. 1,960</ls>` — a noun, refused by
  the head-line test in any case.

**Verdict: neither is a point in this coordinate space.** Across the whole of pwg and mw, **gaṇa
1 is cited exactly three times and every time as `1,1`** — bhū, the first root of the
dhātupāṭha. The attested ceiling for gaṇa 1 is therefore 1, and a gaṇa whose serials stop at 1
does not have an 840th root: these are some other numbering of Westergaard that the supplement
reaches for twice. Admitting them would mint two coordinates no witness can confirm and would
collide with any genuine future `1,840`.

The ceiling is **derived from the corpus at build time** (`coordinate_ceilings`), never typed,
and derived from PWG's citations alone — the source being screened must not widen the space it
is screened against. Both refusals are published with the ceiling they failed in the artifact's
`_out_of_coordinate_space`. The ceiling screen deliberately runs *before* the membership screen,
which would also catch them: the ceiling says *why they are not coordinates*, while membership
reports the different finding of a coordinate renumbered between editions.

#### Cross-validation — reported as the weak thing it is

Only 8 coordinates have both a PWG attribution and a screened pw claimant: **1 agrees strictly
(12.5%)**, 3 counting citation-form variation (37.5% — `vṛkṣ`/`varkṣ` guṇa, `karṇ`/`karṇay`
stem). The other 5 (`darp`/`dramp`, `huḍ`/`bhruḍ`, `prath`/`parth`, `kaḍ`/`khaḍ`,
`grabh`/`gṛhay`) are genuine differences between Böhtlingk's two editions, published in
`_sibling_disagreements` and never resolved. **8 comparisons is far too few to read as a quality
verdict on either edition**, and it is said here so nobody quotes 12.5% as one. It is, however,
one more reason not to let pw break ties: the two editions disagree about roots often enough
that a pw claim is not obviously the better reading even where PWG is silent.

#### Declared residue

- **`15,89` stays dropped.** Böhtlingk states two readings himself; resolving it needs an
  editorial ruling, not more parsing.
- **`32,56` is "conflicted" only because a `v. l.` claimant counts as a full one.** PWG's `cikk`
  citation is explicitly a variant reading, and if H1333's own pass applied the guard added here,
  `32,56` would resolve cleanly to `cakk`. Applying it there would move the shipped H1333
  baseline, which H4349 is not permitted to do — so it is recorded as a candidate for a future
  handoff rather than smuggled in. **Adjudicated 08-09-2026 (H4386): measured, and declined.
  See below.**

#### `32,56` adjudicated — the cure is worse than the residue (H4386, 08-09-2026)

H4349 left `32,56` open because it was forbidden to move H1333's baseline. H4386 was permitted
to decide it, and did — by building the counterfactual rather than reasoning about it. **The
verdict is: do not apply H4349's variant-reading guard to H1333's own PWG pass.** The diagnosis
was right and the remedy is wrong, and the numbers say so.

Counterfactual A — the guard as written for the sibling passes, applied to PWG's own claimants
(drop any head-line claimant whose citation is followed by `<ab>v. l.</ab>`, then resolve as
H1333 does). 331 of PWG's head-line claimants carry that note, and **241 of 1751 coordinates
move**:

| what happens to the coordinate | n |
|---|--:|
| newly resolved — the tie was a `v. l.` against a plain claimant | 93 |
| **lost entirely — the sole claimant carried the note** | **130** |
| reattributed to a different root | 18 |

The 130 are decisive. In the sibling passes the guard only ever refuses a *fill*, so its worst
case is a coordinate left empty; run against PWG itself it **deletes attributions for which PWG
is the only witness** (`2,15 mud`, `3,12 khād`, `5,35 valg`, `7,40 vraj` …). A note that marks a
headword as a variant reading in a same-author *sibling* is not the same speech act as the same
note inside the article that Böhtlingk numbers — and 130 deletions is what the difference costs.

Counterfactual B — the narrow reading, `v. l.` as a tie-breaker among multi-claimant coordinates
only, never erasing a sole claimant: **0 lost, 93 gained, 18 still reattributed**, and `32,56`
does resolve to `cakk`. But **all 18 reattributions hand the coordinate to a claimant that is
not a verbal head line** — 8 to an article the builder's own `<lex>` head-line test flags as
nominal, and the other 10 to an article that never cites the coordinate on its head line at all
and merely quotes it in the body (`19,2 vyath → saṃcalana`, `23,40 vad → vyakta`,
`28,1 tud → vyathana`, `31,1 krī → vinimaya`, `32,119 mlakṣ → mlecchana`) — because dropping the
verbal claimant lets the artha-noun article win by default. That is the `pad`/3,1 defect class in
a new place, and it means the narrow variant is not a screen ordering away from correct:
"verbal beats nominal" would have to run *before* the tie-break, and then be re-verified.

> An earlier draft of this paragraph said "12 of the 18 hand the coordinate to a nominal
> claimant". An adversarial verifier could not reproduce 12 under any mechanical definition —
> it got 8 by the `<lex>` flag and 17 by "no `√` on the head line" — and it was right: 12 was a
> hand-count of names that read like artha-nouns, not a derived number. The 8 + 10 = 18 split
> above is mechanical and re-derivable. Publishing a number nobody can re-derive is the exact
> defect class this handoff exists to close, so the correction is recorded rather than
> overwritten.
>
> **The replacement gloss is wrong too, and for the same reason** (H4432's independent
> verifier, 09-09-2026). "All 18 hand the coordinate to a claimant that is not a verbal head
> line" is a statement about the *builder's flags*, not about the articles: **8 of the 18
> targets are verbal root articles, 6 of them carrying Böhtlingk's own `√`** — `lal` (9,76),
> `tuj` (32,30), `bal` (32,68), `tantray` (33,5), `las` (33,55), `svar` (35,11), plus `vell`
> (15,33) and `hvā` (23,39) unmarked. "No head-line citation" is not "nominal": Böhtlingk puts
> a causative or a later sense of the *same root* on a `<div n="p">` continuation line, e.g.
> `— <ab>caus.</ab> {#lAsa/yati#} … <ls>DHĀTUP. 33,55</ls>` under `las`, and the head/body
> discriminator sees exactly one physical line after `<L>`. The mechanical 8 + 10 split stands;
> what it *means* does not. Do not re-derive "18 nominal targets" from it.

The coverage arithmetic, published as required rather than folded into anything: counterfactual B
would take 1465/1751 (83.7%) to **1496/1751 (85.4%)** — 74 of the 93 gains have a Palsule row, 43
of those are coordinates the MW pass already fills, leaving **31 net new** — and would **change
17 attributions already shipped**. That is a re-baseline of H1333 and H4339 together, with 17 rows
whose provenance flips, not a residue fix.

**Decision: `32,56` stays dropped, the guard stays out of the PWG pass, and coverage stays
1465/1751.** (H4432 adjudicated that next handoff on 09-09-2026 and **confirmed the
decline** — see below: the arithmetic here reproduces exactly, and the detector it was
measured with does not survive clause-scoping.) The re-baseline is real work with a real
yield and it is somebody's next handoff,
with the ordering question (verbal-beats-nominal before the `v. l.` tie-break) as its first
task; it is not a screen-hardening pass's business to move a shipped baseline by 31 rows and flip
17 more on the way past. Re-derive both counterfactuals from the corpus by re-reading
`read_pwg_coords` with a fourth slot for `_BOEHTLINGK_VL` matches after the citation — the
measurement is 20 seconds of work and no part of it is stored, deliberately: a number nobody can
re-derive is a number nobody should trust.
- **The `√` marker is pw's convention**, not a law; a dictionary that marks roots differently
  needs its own test rather than this one reused.

#### The 17 flips adjudicated one by one — DECLINE CONFIRMED, and why (H4432, 09-09-2026)

H4386 declined the re-baseline on an aggregate: 18 reattributions, all of them to a claimant
that is not a verbal head line. H4432 was minted to test that aggregate against the articles
themselves — one quoted sentence per flipped row — and to answer the ordering question H4386
left open: does "verbal beats nominal" run *before* the `v. l.` tie-break, and is that ordering
justified from Böhtlingk's own prose rather than from the nicer number it produces?

**Every published figure reproduces.** `src/pilot/dhatup_h4432_rebaseline_probe.py` restates the
citation scan, the head-line weighting, the `<lex>` flag and H1333's resolution from this
document's prose, imports nothing from the builder, and asserts 25 figures — 1751 cited, 271
conflicted, 1480 resolved, 331 head-line claimants carrying the note, the blunt reading's
**93 / 130 / 18** (241 moved), the narrow reading's **0 / 93 / 18** with `32,56 → cakk`, the funnel
**74 → 43 → 31 → 1496/1751**, the **17** of 18 that are already shipped, and the 8 + 10 split.
All 25 hold. H4386's arithmetic is confirmed exactly, including the corrected 8 + 10.

**One of those 25 figures is arithmetic that the pipeline does not produce.** `1465 + 31 =
1496` counts the gains and assumes the 18 reattributions are free. They are not: 12 of the 18
targets have no Palsule row, so a reattributed coordinate either changes witness or **loses its
row outright**. Built end to end rather than added up, the narrow line-scoped guard gives
**1493/1751 (85.3%)** — 31 rows added, **3 deleted**, 21 rows changing root and 46 more changing
only their `source` token. The three deleted rows are `28,1 tud`, `31,1 krī` and `31,41 grath`,
all shipped `source=pwg` today, handed to `vyathana` / `vinimaya` / `saṃdarbha`, none of which
Palsule has and none of which MW refills. `28,1` is *tud*, the first root of the tudādi gaṇa.
**`1496/1751 = 85.4%` is refuted; the measured figure is 1493/1751 = 85.3%**, and "17 shipped
rows flip" undercounts — **21** shipped rows change root, because 13 of the 43 "the MW pass
already fills" are coordinates the PWG counterfactual wins first with a *different* root
(`26,23 jhṝ→su`, `33,63 lag→rak`, `17,43 riṣ→caṣ`, `28,84 cuṇ→chuṭ` and nine more). The funnel is
right; it was never built, and a funnel that is never built cannot see a deletion.

**And the measurement those figures describe is not a measurement of the note.** The
Böhtlingk-family variant-reading test is **line-scoped**: `_BOEHTLINGK_VL.search(line, mm.end())`
accepts a note anywhere later on the same physical line. A Cologne article is *one* physical
line, routinely carrying six or eight citations, so a note attached to an article's fourth
citation is read as disowning its first. MW's side of exactly this problem was corrected on
07-09-2026: `_vl_governs` there is clause-scoped with parenthesis depth, because `paṇḍ` at
`32,130` shipped a root both dictionaries disown when a `)` was counted blindly. The
Böhtlingk-side test is the same defect, uncorrected — and the note stands *after* its citation
here rather than before it, which is why it was never noticed as the same shape.

Mirroring that rule for a trailing note — the note governs only when nothing between it and the
citation ends the clause: no intervening `<ls` citation, no `.` or `;` at parenthesis depth 0
once markup and `{#…#}` / `{%…%}` braces are stripped, and the note not inside a parenthesis
opened after the citation — **cuts the head-line claimants carrying a governing note from 331 to
148**, and the narrow reading's 18 reattributions fall to 8. The 10 that vanish are precisely
the 10 adjudicated below as scope failures: the hand adjudication and the mechanical rule agree
row for row, which is the only reason either is worth quoting.

**The 183 that fall away are not all phantoms — about 166 are.** Roughly 17 of them are genuine
disowning notes of the shape `</ls>. <ab>v. l.</ab> für {#X#}`, which the rule above rejects
because it stops at the `.` that closes the citation. A variant admitting exactly that shape
leaves **165** governing claimants instead of 148 — and produces **the same eight
reattributions**, which is what makes the eight worth trusting. So the honest statement of the
detector's error rate is *at least half its firings*, not "183 of 331"; the 55% figure was the
first rule's number quoted as if it were the defect's.

##### The table

Every row's quotation is from `pwg.txt` verbatim; ✅ = the source says the coordinate belongs to
the proposed root, ❌ = it does not.

| coord | shipped | proposed | what PWG actually says | verdict |
|---|---|---|---|---|
| `9,76` | laḍ | lal | `{#laq#}¦, {#la/qati#} ({#vilAse#}) <ls>DHĀTUP. 9,76</ls>. {#laqayati#} ({#jihvonmaTane#}, <ab>v. l.</ab> …) <ls n="DHĀTUP.">19,53</ls>` — a full stop, a second finite form and an open parenthesis stand between: the note offers variants of **19,53's** artha | ❌ scope |
| `15,33` | vehl | vell | `{#vehl#}¦, {#vehlati#} ({#calane#}) <ls>DHĀTUP. 15,33</ls>, <ab>v. l.</ab>` — that is the *entire* article — against `{#vell#}¦, {#ve/llati#} ({#calane#}) <ls>DHĀTUP. 15,33</ls>`, same artha | ✅ |
| `17,13` | tvakṣ | tvacana | note governs (`<ls>DHĀTUP. 17,13</ls>, <ab>v. l.</ab> <ls>KAVIKALPATARU</ls>`), but the winner is `{#tvacana#}¦ (von {#tvacay#}) <lex>n.</lex> {%das Umlegen eines Felles%}` — a noun, and `tvakṣ`'s own head line cross-refers to it (`<ab>vgl.</ab> {#tvacana, tvacay#}`) | ❌ nominal |
| `17,80` | cah | parikalkana | `<ls>DHĀTUP. 17,80</ls>. <ls n="DHĀTUP.">32,82</ls> (<ab>v. l.</ab> für {#cap#})` — the note is **32,82's**, and it names `cap`; the winner is `{#parikalkana#}¦ <lex>n.</lex> {%das Betrügen%}` | ❌ scope + nominal |
| `19,2` | vyath | saṃcalana | `<ls>DHĀTUP. 19,2</ls> ({#BayasaMcalanayoH#} <ab>v. l.</ab> {#duHKacalanayoH, …#})` — the note is *inside* the artha parenthesis, offering variants of the meaning; the winner is `{#saMcalana#}¦ … <lex>n.</lex> {%das Zucken, Beben%}` | ❌ scope + nominal |
| `23,10` | skand | śoṣaṇa | the note is at the far end of the article and reads `<ls>VOP.</ls>_in_<ls>DHĀTUP. 2,8</ls> als <ab>v. l.</ab> von {#skund#}` — another coordinate, another root; the winner cites `23,10` in a body sense, `{%das Eintrocknen, Verdorren%}` | ❌ scope + nominal |
| `23,39` | spardhā | hvā | the note stands ~1.5 kB later, after `<ls>Spr. (II) 2391</ls>`. **But the shipped row is wrong for an unrelated reason** — see the residue note below | ❌ scope |
| `23,40` | vad | vyakta | `<ls>DHĀTUP. 23,40</ls> ({#vyaktAyAM vAci#}). <ls n="DHĀTUP.">34,34</ls> ({#saMdeSavacane#}, <ab>v. l.</ab> …)` — the note is **34,34's**; the winner merely quotes `{#vyaktA vAk#}` in a body sense | ❌ scope + nominal |
| `28,1` | tud | vyathana | the note is far down `tud`'s article, past `<ls>P. 6,1,173</ls>` and a `;`; the winner is `vyaTana`'s fourth body sense, `{%das Bereiten eines Schmerzes%}` | ❌ scope + nominal |
| `28,120` | prach | jñīpsā | the note is far down `praC`'s article; the winner is `{#jYIpsA#}¦ (vom <ab>desid.</ab> vom <ab>caus.</ab> von <hom>1.</hom> {#jYA#}) <lex>f.</lex> {%Erkundigung, das Fragen%}` — a noun of a *different* root | ❌ scope + nominal |
| `31,1` | krī | vinimaya | the note is far down `krI`'s article; the winner is `{#dravya˚#} <ls>DHĀTUP. 31,1</ls>` inside `vinimaya` `{%Tausch, Vertauschung%}` | ❌ scope + nominal |
| `31,41` | grath | saṃdarbha | `<ls>DHĀTUP. 31,41</ls>. {#granTa/yati#} … <ls n="DHĀTUP.">34,19</ls>. … <ls n="DHĀTUP. 34,">31</ls>, <ab>v. l.</ab>` — the note is **34,19/2,35's**; the winner is `{#saMdarBa#}¦ (von <hom>1.</hom> {#darB#} mit {#sam#}) <lex>m.</lex> {%das Winden%}` | ❌ scope + nominal |
| `32,30` | lañj | tuj | `<hom>2.</hom> √{#laYj#}¦, {#laYja/yati#} ({#hiMsAbalAdAnaniketanezu#}) <ls>DHĀTUP. 32,30</ls>, <ab>v. l.</ab> ({#BAzArTa#}, …)` against `{#tuYja/yati#} … = {#hiMsA, bala, AdAna#} oder {#dAna, niketana#} <ls>DHĀTUP. 32,30</ls>` — the same artha set, twice | ✅ with reservation |
| `32,68` | cal | bal | `<hom>3.</hom> √{#cal#}¦, {#cAla/yati#} {%ernähren%} <ls>DHĀTUP. 32,68</ls>, <ab>v. l.</ab> für {#bal#}.` — that is the entire article, and Böhtlingk **names the winner** | ✅ |
| `32,119` | mlakṣ | mlecchana | the note governs (`<ls>DHĀTUP. 32,119</ls>, <ab>v. l.</ab>` ends the article), but the winner is `{#mlecCana#}¦ (von {#mleC#}) <lex>n.</lex> {%das Wälschen%}` — if `mlakṣ` goes, the coordinate is `mleC`'s, not its artha noun's. **Drop, never flip** | ❌ nominal |
| `33,55` | laś | las | `{#laS#}¦, {#lASa/yati#} ({#Silpayoge#}) <ls>DHĀTUP. 33,55</ls>, <ab>v. l.</ab> für {#las#}.` — the whole article, naming the winner — against `<ab>caus.</ab> {#lAsa/yati#} ({#Silpayoge#}, …) <ls>DHĀTUP. 33,55</ls>`, same artha | ✅ |
| `35,11` | sur | svar | `√{#sur#}¦ … {#surayati (Akzepe)#} <ls>DHĀTUP. 35,11</ls>, <ab>v. l.</ab>` — the article's last token — against `<ab>caus.</ab> {#svarayati#} <ls>DHĀTUP. 35,11</ls> ({#Akzepe#})`, same artha | ✅ |

The 18th reattribution ships nothing and is recorded for completeness: **`33,5` kuṭumbay → tantray**
is ✅ — `!√{#kuwumbay#}¦ (von {#kuwumba#}), {#kuwumba/yate#} {%eine Familie unterhalten%}
<ls>DHĀTUP. 33,5</ls>, <ab>v. l.</ab>` against `tantray`'s `<ab>med.</ab> {%die Familie
unterhalten%} <ls>DHĀTUP. 33,5</ls>`, the same gloss word for word — but `kuṭumbay` has no
Palsule row, so no shipped row moves either way.

**Tally: 4 of the 17 justified outright, 1 with a reservation, 12 refused** — 10 because the note
belongs to a different citation, 2 because the note governs but hands the coordinate to an artha
noun. H4432's mandate says a re-baseline is applied only when a flip carries a source sentence
that says the coordinate belongs to the new root. Twelve do not.

##### The ordering question, answered

"Verbal beats nominal before the `v. l.` tie-break" **is** justified from Böhtlingk's own
practice: he marks a verbal article positively with `√` on its head line and writes a derived
noun as `(von X) <lex>n.</lex>`, so `tvacana` "(von `tvacay`)" and `mlecchana` "(von `mleC`)"
announce themselves as derivatives of a root that holds the coordinate. Ordering it first is
right, and it is measured: making the tie-break run last, on the claimants surviving H1333's own
nominal filter and only while they are still tied, gives **0 reattributions, 0 losses and 92
gains — 30 net new, 1495/1751**; with the clause-scoped note, 68 gains, **24 net new, 1489/1751**.

**But the ordering is not the load-bearing question, and applying it would be applying a
detector, not a rule.** It cannot rescue the narrow reading: it blocks 12 of the 17 flips only
because their challengers happen to be nouns, while leaving the other 5 rows attributed to roots
Böhtlingk explicitly disowns — `cal` at `32,68`, which his own article says is a variant reading
*for* `bal`, and `laś` at `33,55`, likewise *for* `las`. An ordering that keeps the two rows its
source names as wrong is not the fix; it is a different reading of the same broken signal.

**Decision: DECLINE CONFIRMED. The guard stays out of H1333's PWG pass, coverage stays
1465/1751 (83.7%), and `src/data/dhatup_palsule.json` is byte-identical.** Not because the
re-baseline is worthless — 7 shipped rows are demonstrably wrong, and 148 genuinely disowned
head-line claimants are real evidence — but because every number offered for it, 93 / 130 / 18
and 31 net new alike, was measured with a test that misfires on at least half of what it fires
on. The 7: five whose article disowns the shipped root *and* names a verbal replacement
(`15,33`, `32,30`, `32,68`, `33,55`, `35,11`, of which `32,30` is reserved rather than certain),
plus `17,13` and `32,119`, disowned with no usable replacement, where the correct outcome is to
drop the coordinate rather than flip it.

**The four reasons the decline rests on, stated so a future reader can check each one** — and
deliberately *not* "all 18 targets are nominal", which is false and would be re-derived as false
by the first person to look at the articles:

1. The detector is line-scoped in a corpus whose articles are one physical line, so it misfires
   on at least half its firings; clause-scoping cuts 331 governing claimants to 148 (165 under
   the variant that admits the `</ls>. <ab>v. l.</ab>` shape) and 18 reattributions to the same
   8 either way.
2. The offered baseline is not what the pipeline produces: built rather than added up, it is
   **1493/1751**, and it **deletes** `28,1 tud`, `31,1 krī`, `31,41 grath`.
3. The disturbance is larger than advertised — **21** shipped rows change root, not 17, plus 46
   changing witness only.
4. Twelve of the 17 adjudicated flips fail on the articles themselves: ten because the note
   belongs to a different citation, two because it hands the coordinate to a derived noun.

Applying the re-baseline now would move a shipped baseline on a signal this document has just
shown to misfire more often than not. The counterfactuals under the corrected test are published
beside the old baseline rather than folded into anything: narrow + clause-scoped =
**1490/1751** with 7 shipped rows flipping, ordered + clause-scoped = **1489/1751** with none.

##### What the successor handoff owes, and the residues this pass names

1. **Port `_vl_governs` to the Böhtlingk family** — a trailing-note mirror of MW's clause test,
   with its own adjudication of the 148 governing notes and of the 69 gains it produces. That is
   a correction to a screen, not a coverage project, and it must be measured before any
   re-baseline is argued again.
2. **The `<lex>` nominal head-line test has the same line-scope defect.** `_HEAD_LEX` searches
   the whole head line, so `vell` is flagged nominal for `15,33` because `<lex>n.</lex>` appears
   **1148 characters** later in the same physical line, in a later sense ("das Wälzen eines
   Pferdes") that has nothing to do with the citation — whereas `tvacana` and
   `mlecchana` carry `<lex>` *before* their citation, which is where a part-of-speech tag stands.
   Both head-line tests need the same scoping, and neither should be changed without the other.
   Measured: **73 of the 128** `<lex>` nominal flags carry no tag before the citation at all.
   Scoping this test alone moves the shipped table 1465 → **1463** and fixes `15,32 kvel→kṣvel`
   and `32,12 naḍ→naṭ` — a correction that has nothing to do with the re-baseline and is not
   made here.
3. **`23,39 → spardhā` is a live defect of a third class.** `{#sparDA#}¦ (wie eben) <lex>f.</lex>
   … als <ab>Bed.</ab> von {#hvA#} und {#A — hvA#} <ls>DHĀTUP. 23,39</ls>` is a noun article
   saying in as many words that the coordinate is a *meaning of* `hvā`, and `hvā`'s own article
   claims it with the matching artha: `<ls>DHĀTUP. 23,39</ls> ({#sparDAyAM Sabde ca#})`. It ships
   as `spardhā` because the nominal filter runs only among *multiple* head-line claimants, and
   `hvā` states its claim in the body. A sole nominal head claimant is never tested — that is
   its own residue, unrelated to the `v. l.` note, and it is not fixed here.
4. **`32,30` is the genuinely ambiguous row and is not rounded into the majority.** The note
   stands between the citation and a second, parenthesised artha, so it can be read as
   introducing that variant rather than as disowning `lañj`; the same trailing-parenthesis
   ambiguity MW's own guard declares and leaves alone. `tuj` matching the artha set word for
   word is why it is called justified, and the reservation is why it is not called certain.
5. **The head/body discriminator is a third instance of the same line-scope defect.** `at_head`
   is true for exactly the one physical line after `<L>`, so every later sense of a multi-sense
   root article counts as "body" — which is why `bal`, `las`, `svar` and `tuj` are recorded as
   having "no head-line citation" while being verbal claimants of their own coordinate inside
   their own root article. It is not fixed here, and it is why the 8 + 10 split must never be
   read as 18 nominal targets.
6. **PWG writes `DHĀTUP.` citations three ways and the builder reads two — so the denominator
   1751 is a property of a regex set, not of PWG.** `_DHATUP` and `_DHATUP_N` miss
   `<ls n="DHĀTUP.">4,13</ls>`, which occurs **320 times over 270 distinct coordinates**; MW's
   reader in the same file handles the exact analogue (`_MW_DHATUP_N_FULL`), so this is an
   asymmetry between the two readers and nothing anywhere records it as deliberate. Admitting
   the form end to end moves `coords_cited` **1751 → 1892 (+141)**, rows 1465 → 1576, changes 16
   attributions, and moves the published rate **83.7% → 83.3%** — a larger effect than the ±31
   this whole adjudication is about, in the opposite direction. Whether those 141 coordinates
   are real is *not* settled here: some may be the cross-edition renumbering H4349 already
   found. What is settled is that **83.7% may not be published again without ruling on the
   form**, and that ruling is a handoff of its own.
7. **`FEATURES_INDEX.md`'s L18 row still advertises the guard without its scope.** It calls the
   fourth screen a "Böhtlingk-family variant-reading guard" with no hint that the test is
   line-scoped, which is the one sentence a reader would need before reusing it. It is left
   untouched here on purpose: H4432's edit scope permits `FEATURES_INDEX.md` only if the
   baseline moves, and the baseline does not move. The successor of residue 1 amends that row
   in the same pass that fixes the scope.

**Re-derive:** `python src/pilot/dhatup_h4432_rebaseline_probe.py --xls <the gitignored Palsule
XLS>` — 25 asserted figures, the clause-scoped counts, and the per-row scope evidence quoted
above; `--dump-flips` prints both articles for every reattribution. It exits **2** when a corpus
is absent, never 0.

##### Who certified this, and what they refused to certify

The verdict is not the implementer's. An independent adversarial verifier (Opus 5,
`claude-opus-5`) re-derived every load-bearing number in a separate context from the raw corpora
and the Palsule XLS, wrote its own citation scanner and its own clause rule *before* reading the
builder's, and ran three end-to-end counterfactual builds against patched copies of the builder.
Its report is committed verbatim as
[reports/H4432_INDEPENDENT_VERIFIER_REPORT_09-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4432_INDEPENDENT_VERIFIER_REPORT_09-09-2026.md).

It **confirmed** the baseline (its scanner reproduced the 1226-coordinate PWG set with symmetric
difference 0), the blunt and narrow readings, the 17-of-18 membership, the 331 count, the
clause-scoped **148** and the identical eight surviving flips — which it reached independently —
all ten scope eliminations against the raw lines, the per-flip judgments, the `<lex>` defect, and
**DECLINE CONFIRMED** as the decision.

It **refuted** four things this document had said, and each refutation is folded in above rather
than footnoted: `1496/1751` (the build gives 1493 and deletes three rows), "17 shipped rows flip"
(21 change root), "all 18 targets are nominal" (8 are root articles, 6 with `√`), and "wrong 183
times in 331" (about 166; the rule that recovers the other 17 yields the same 8 flips). It also
found two defects nobody had claimed — the head/body discriminator's line scope, and the unread
third citation form — both recorded as residues 5 and 6.

Its own stated limits, kept rather than smoothed: it did not re-implement the MW reader
independently, so MW-derived rows inherit any defect that reader has; it read the Palsule XLS but
cannot check it against the printed book; it adjudicated against Böhtlingk's and Monier-Williams's
prose, not against a dhātupāṭha edition, so "32,68 belongs to `bal`" means Böhtlingk says so; and
it read 22 of the ~183 divergent firings in full, the rest being supported by gap statistics
rather than by individual reading. It also reported the adjudication absent from disk — it was
reading the main checkout, while this section lives on the H4432 branch.

#### Two hardenings that carry the screens forward (H4386, 08-09-2026)

**The screens are mandatory.** `_sibling_pass`'s `same_book_conflicted` and `pwg_cited` were
keyword arguments defaulting to `frozenset()`, and the membership test read
`if pwg_cited and coord not in …`, so a pass that simply forgot one was silently *unscreened* —
which is not a hypothetical: it is how the first cut shipped `32,56 → cukk`, passing the
same-book screen to the `pwg-dotted` call and not to the `pw` one. Both are now keyword-only with
no default (omitting one is a `TypeError` at the call site), the membership test is
unconditional, and an empty `pwg_cited` — the old default reached by hand — raises, because the
set being screened against is also the denominator `match_rate` divides by. `dhatup_h4349_verify.py`
asserts all of this off the builder's **syntax tree**, without importing it.

**What an independent verifier found, including where it refuted the first cut.** H4386's
verifier rebuilt the artifact four times with one screen disabled each, and the result is not
the clean four-for-four the handoff's acceptance line assumed:

| screen disabled | effect on the shipped table |
|---|---|
| same-book conflict | **1466 (+1)** — `32,56 → cukk` ships, `source=pw` |
| `pwg_cited` membership | **1466 (+1)** — `33,67 → tras` ships, `source=pw` |
| coordinate ceiling | **no change** — `1,840` / `1,960` move bucket, table identical |
| variant reading | **no change at all** — table identical, `_stats` diff empty |

Two of the four are load-bearing on the output; the ceiling screen is order-shadowed by the
membership screen and changes only which bucket two malformed citations are *reported* in (the
builder's own comment says so, and calls it a reporting decision); the variant guard refuses
nothing as shipped and moves no row even when un-shadowed. That is recorded rather than
smoothed over: a screen kept for a reason other than its current yield is fine, a screen
*claimed* to be load-bearing when it is not is the drift this handoff exists to stop.

**And the first cut of the mandatory-screen change was itself refuted.** Making the parameters
defaultless fixes the *signature*, and the shipped H4349 defect was never a missing argument —
it was a **call site** passing the permissive value. The verifier rebuilt against the hardened
code with `same_book_conflicted=frozenset()` at the call site and shipped `32,56 → cukk` again;
a `pwg_cited` that is merely truthy and always-contains (a list, a dict, a four-line
`__contains__` class) passed `if not pwg_cited` and screened nothing, shipping both bad rows.
Both are closed now: each screen must be a real `set`/`frozenset` **and** non-empty, the one
legitimate exemption is the named `NO_SAME_BOOK_CONFLICTS` sentinel so it is greppable at every
call site rather than indistinguishable from the mistake, and `dhatup_h4349_verify.py` now
checks the **call sites** as well as the signature — every call names both screens, none passes
an empty literal, and the validation covers both names rather than `pwg_cited` alone.

**The artifact is pinned to its builder.** Nothing used to prove `src/data/dhatup_palsule.json`
came from the committed `build_dhatup_palsule.py`: one harness reads the JSON, the other the JSON
plus the corpora, and neither rebuilds, so a stale or hand-edited artifact stayed green — H4349's
verifier had to rebuild by hand to establish the two agreed. `_stats.builder_sha256` now carries
the sha256 of the builder's own source, checked corpus-free in `ls_enrichment_selftest.py` and
again in the standalone verifier. **Change the builder without rebuilding and CI fails.** The pin
says "this artifact was written by this code", not "this is what the code would produce from
today's corpora" — that second question is what the corpus-backed checks are for. On landing,
the rebuilt artifact was byte-identical to the shipped one but for the new key: same 1465 rows,
same 1226/140/99 split, same disagreement and refusal lists.

**Re-derive:** `python src/build_dhatup_palsule.py` (all `_stats` above);
`python src/build_dhatup_palsule.py --mw "" --pw "" --no-pwg-dotted` rebuilds the PWG-only H1333
table byte-for-byte (1226 rows, verified as a zero diff);
`python src/pilot/dhatup_h4349_verify.py` re-derives every number above from the artifact and the
raw corpora without importing the builder.

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
