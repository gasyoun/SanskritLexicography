# Handoff research — microstructure conventions across the core dictionaries (2026-06-23)

**Question.** For each core dictionary, *how* are the four microstructure conventions
realized — so `pwg_ru` can decide which to follow (or harmonize) for its printed Russian
edition:

1. **Homonym handling** — how are spelling-identical but distinct headwords separated?
   (numbered `1. X / 2. X`, superscripts `X¹`, etymological grouping, …) and on what
   basis (etymology, part of speech, derivation)?
2. **Equivalent vs explanatory gloss** — does the dict give terse target-language
   *equivalents* (`часть`), discursive *explanatory* glosses (толкование), or a mix —
   and is there a typographic signal distinguishing them?
3. **Citation / illustration policy** — every sense cited? text-citations vs
   kośa/grammarian authorities vs example sentences? citation density and format?
4. **Run-on / derivative treatment** — are derivatives (nominal stems, compounds,
   secondary forms) given as **separate headwords**, **run-on** in a paragraph under the
   base, or **niched** (indented sub-lemmas)?

These four set the per-source rules our merged card must respect and the conventions the
Russian edition adopts.

## Sources (all local)
| Dict | Preface (OCR) | Entry file | Probe set |
|---|---|---|---|
| PWG | [`PWG/prefaces/pwgpref_all.de.md`](https://github.com/sanskrit-lexicon/PWG/blob/main/prefaces/pwgpref_all.de.md) | `csl-orig/v02/pwg/pwg.txt` | homonyms `1.aMSa/2.aMSa`; gloss-rich `arTa`; deriv-nest `kf`/`gam` |
| PW | [`PWK/prefaces/pwpref_all.de.md`](https://github.com/sanskrit-lexicon/PWK/blob/master/prefaces/pwpref_all.de.md) | `csl-orig/v02/pw/pw.txt` | same |
| MW | [`MWS/prefaces/mwpref_all.en.md`](https://github.com/sanskrit-lexicon/MWS/blob/master/prefaces/mwpref_all.en.md) | `csl-orig/v02/mw/mw.txt` | same |
| GRA | [`GRA/prefaces/grapref_all.en.md`](https://github.com/sanskrit-lexicon/GRA/blob/master/prefaces/grapref_all.en.md) | `csl-orig/v02/gra/gra.txt` | RV-only; check citation = every occurrence |
| AP90 | *(print front-matter)* | `csl-orig/v02/ap90/ap90.txt` | `artha`; check example-sentence style |
| SCH | [`SCH/prefaces/schpref_all.de.md`](https://github.com/sanskrit-lexicon/SCH/blob/master/prefaces/schpref_all.de.md) | `csl-orig/v02/sch/sch.txt` | `°`/`*` markers (already decoded — see DICTIONARY_CHAIN.md) |

**Method.** Per dict: (1) read the preface for its stated rules on each of the four;
quote. (2) Confirm against the probe entries pulled from the entry file. (3) Fill a
4-column matrix.

**Output:** a matrix `dict × {homonym / gloss-type / citation / run-on}`, each cell a
short classification + an evidence quote, and a closing "harmonization note" — where the
four sources conflict and what `pwg_ru` should standardize on (e.g. keep PWG's numbered
homonyms + its two-source attested/lexicographic distinction, already in our schema).

**Preliminary priors (verify):**
- **Homonyms:** PWG/PW number `1./2.` by derivation; MW uses superscripts; GRA by root.
- **Gloss type:** PWG = German equivalent **+** explanatory, dense; MW = English
  equivalents, very dense, abbreviation-heavy; AP = equivalents **plus example
  sentences** (its pedagogical hallmark); GRA = precise philological gloss per RV sense.
- **Citation:** PWG/PW cite exhaustively (text + kośa, the two-source principle); GRA
  cites **every** RV occurrence; MW cites abbreviated sources, not every occurrence; AP
  cites less, leans on illustrative sentences.
- **Run-on:** MW heavily **run-on** for derivatives; PWG/PW more **separate headwords**;
  AP mixes. (This dovetails with the root-architecture handoff.)

## Cross-links
- Root nesting/splitting → [`ROOT_ENTRY_ARCHITECTURE.md`](ROOT_ENTRY_ARCHITECTURE.md).
- Sense order → [`HANDOFF_sense_ordering.md`](HANDOFF_sense_ordering.md).
- What `pwg_ru` already implements (homonym `h`-keying, equivalence_type, two-source
  attested/lexicographic, Apresjan discrimination, Renou I–V) →
  [`../DICTIONARY_CHAIN.md`](../DICTIONARY_CHAIN.md), [`../APRESJAN.md`](../APRESJAN.md),
  the final-card schema. The research output should say, per convention, **keep / adapt /
  drop** against what we already do.

---

## RESULTS (executed 2026-06-24)

Method as briefed: each dictionary's **preface rule** (quoted) was confirmed against the
**probe entries** pulled live from `csl-orig/v02/<dict>/<dict>.txt` (homonyms
`aMSa`/`aja`, gloss-rich `arTa`/`aMSa`, derivative-nest compounds of `aMSa`, plus the
SCH `°`/`*` markers). Evidence quotes are from the OCRed prefaces and the entry files.

### The matrix

| Dict | 1 · Homonym handling | 2 · Gloss type (equivalent vs explanatory) | 3 · Citation / illustration | 4 · Run-on / derivative |
|---|---|---|---|---|
| **PWG** | **Numbered `1./2.`**, split on POS **+ etymology**. `<h>1` `a/MSa` "Theil" vs `<h>2` `aMSa` "Schulter" (note: *"durch das goth. amsa sich als die ältere Form erweist"*). | **Mixed: German equivalent + толкование, dense.** `{%Theil%}` then `{%der 16te Theil (des Mondes) heisst kalā%}`. Equivalents in `{%…%}`, discursive matter inline. | **Exhaustive, two-source.** Every sense cited; kośa/grammarian authority **+** text passage with quoted Sanskrit: sense 1 → `AK. 2,9,90`, `H. 1434`; `ṚV. 3,45,4` … *"Die genausten Belege sind bei einem ausführlichen Wörterbuch unerlässlich."* | **Separate headwords.** `aMSaka`, `aMSakaraRa`, `aMSay`, `aMSala`, `aMSasavarRa` each own `<L>`, strict alphabetical, etymology in parens `(1. aMSa + karaRa)`. |
| **PW** | **Numbered `<hom>1./2.`**, same etymological basis (`aja/` √aj "Treiben/Ziegenbock" vs `aja/` "ungeboren"). **Collapses** to no number when only one survives (`aMSa` = single, "Schulter" exiled to `aMsa`). | **Terse equivalents, sense-numbered `1〉 2〉`.** `1〉 Theil`, `2〉 Antheil, Erbtheil`. Explanatory matter trimmed vs PWG. `*` flags grammarian/lexicographer-only attestation (`6〉 *Tag GAL.`). | **Deliberately reduced — points back to PWG.** *"durch Weglassung aller dort gegebenen Citate und Stellen stets daran mahnen, dass das grössere Wörterbuch die Hauptquelle bleiben müsse."* Many senses uncited; one `Chr.` ref where kept. | **Separate headwords**, as PWG. *"Die mangelnden Belege für neu aufgenommene Composita findet man im grösseren Werke unter dem ersten oder unter dem zweiten Worte."* |
| **MW** | **Prefixed figures `1. 2. 3.`** before the transliterated form: *"words … different in meaning, but appear identical in form, are distinguished … by the figures 1, 2, 3, &c."* (`1. a-śita / 2. aśita`). Stored as `<hom>N.</hom>`. | **Terse English equivalents, very dense, synonym-rich.** `a share, portion, part, party`. `,` = amplification, `;` = distinct sense; remarks in `( )`, comparisons in `[ ]`. | **Abbreviated sigla, NOT every sense.** Only some senses carry `<ls>` (`stake … RV. v,86,5; TāṇḍyaBr.`); `L.` = "lexicographers" (= PW's `*`). No quoted example sentences. | **Heavily run-on / niched under leading word.** Compounds shown with dash `aMSa—karaRa`, `aMSa—BAgin` grouped under `aMSa` (`<e>3`); verbs-with-prepositions in own alphabetical order (Greek/Latin method), derivatives in the "subordinate line" under the root. |
| **GRA** | **By root, etymological.** Headword glossed *"das als Antheil erlangte (s. `<hom>1.</hom> aś)"* — homonyms resolved by reference to the numbered root. | **Precise philological gloss per RV sense, numbered `1〉…`, with толкование.** `aṃśú`: a paragraph deriving 1〉 Somapflanze → 2〉 Somasaft → 3〉 Eigenname before the numbered list. | **Every RV occurrence, by inflected form.** Forms `-as / -am / -āya …` each list **all** song-numbers per sense (`-am 1〉 {210,5}. 2〉 {279,4}. 3〉 {102,4}`). The exhaustive-concordance hallmark. | **Inflected-form paradigm run-on** under the stem; derivatives are separate stems. (Roots posited only if attested: *"avoided positing stems … that do not occur."*) |
| **AP90** | **Repeated as separate words** for clear homonyms (*"though identical in form, differ entirely in meaning … generally repeated as separate words; e.g. hā, hi"*); **Roman figures I/II** for conjugation-homonym **verbs** (`as, gup, hā`). `aMSa` "shoulder" folded as sense 5, *"more generally written aMsa"*. | **Equivalents PLUS illustrative example sentences — the pedagogical hallmark.** *"added quotations and references to the peculiar and noteworthy senses … apt illustrations."* `A share, part … sakfdaMSo nipatati Ms. 9.47`. Senses by **importance/frequency**, not history. | **Illustrative quotations, not exhaustive.** Most noteworthy senses get a verse-cite (`Bg. 15.7`, `R. 8.16`, `Līlā.`); later letters thinner (*"substituting references for quotations"* after p. 364). | **Mixed.** Compounds run-on in a `--Comp.` paragraph under the base (`--aMSaH`, `--avatāraH`, `--BAj`); but Kṛt/Taddhita derivatives **separate** (*"All words formed by Kṛt or Taddhita affixes are given separately"*), roots-with-prepositions separate. |
| **SCH** | **No own homonym system — keyed to PW sense numbers.** `aṃśu ¦ 1. … 4. Faden` patches PW's senses 1/4. No `<h>` tags in the file. | **Terse German equivalents** (`Schärpe`, `Lampe`, `Faden`), addendum-style. `°` = word/sense/gender wholly absent from pw; `*` = not yet attested in pw — both lifted into `type=˚`/`type=*`. | **Dense per-addendum, by Band/Seite/Zeile.** `Śat. Br. 4,1,1,2`; `Spr. 2931`; `v.u.` = von unten. ⚠ Böhtlingk-Nachträge cites taken over **unverified** (1889-vintage). | **Separate headwords**, each own `<L>`, keyed to the PW lemma it supplements; compounds separate. |

### Reading the matrix — the two axes that actually divide the sources

1. **Citation philosophy splits the family in two.** PWG and GRA are **exhaustive**
   (PWG: kośa-authority **+** text passage per sense; GRA: every RV occurrence by form).
   PW, MW, AP90, SCH are **selective** — but for *different* reasons: PW drops cites *by
   design* and re-points to PWG; MW abbreviates to fit one volume; AP90 keeps only
   *illustrative* quotations; SCH cites densely but only its *addenda*. So "is every
   sense cited?" = **yes** for PWG/GRA, **no** for the rest.

2. **Run-on vs separate-headword splits the same family differently.** PWG/PW/SCH = each
   compound and derivative is a **full alphabetical headword**. MW = compounds and
   derivatives are **niched under the leading word / root** (the dash `aMSa—…`,
   `<e>3`). AP90 = **hybrid** (compounds run-on under `--Comp.`, Kṛt/Taddhita derivatives
   separate). GRA = inflected **forms** run-on, derivative **stems** separate. The
   priors held on every count.

3. **Homonym basis is uniform; only the typography differs.** All six that split do so
   on **etymology / derivation / POS**, never on a frequency or arbitrary axis — PWG/PW
   prefix `1./2.` (digitized `<h>`/`<hom>`), MW prefixes figures `1. 2. 3.`, GRA keys to
   the numbered root, AP90 repeats the word (Roman I/II for verbs), SCH inherits PW's
   numbering. The decision *whether* to split is the only variable: AP90 folds freely,
   PW collapses when one member emigrates to a variant spelling.

### Harmonization note — keep / adapt / drop vs what `pwg_ru` already implements

`pwg_ru`'s schema (homonym `h`-keying, `equivalence_type`, two-source
attested/lexicographic, Apresjan discrimination, Renou I–V) was checked against each
convention. See [`../DICTIONARY_CHAIN.md`](../DICTIONARY_CHAIN.md),
[`../APRESJAN.md`](../APRESJAN.md).

- **Homonyms → KEEP, unchanged.** Our `h`-keying *is* the PWG/PW `<h>`/`<hom>` numbered,
  etymology-based split — the dominant convention (4 of 6 dicts number; GRA/SCH key to a
  number). **Adapt only at the merge seam:** when PW collapses a PWG homonym (the
  `aMSa`-1/2 → single-`aMSa` + `aMsa` case), `pwg_ru` should keep **PWG's** finer split
  as the spine and record PW's collapse as a provenance note, not silently inherit PW's
  single entry. Standardize the print on `1. / 2.` prefixed figures (PWG idiom), which is
  also MW's, so cross-dictionary refs line up.

- **Gloss type → KEEP the `equivalence_type` field; ADAPT the default toward толкование.**
  The dicts span a continuum: AP90/MW lean **equivalent**, PWG/GRA lean **equivalent +
  толкование**, and Apresjan's *требования к толкованиям* (our stated backbone) demand a
  proper Russian *толкование* where no equivalent is isomorphic. So `pwg_ru` should
  **standardize on PWG's mixed model** — terse Russian equivalent first, толкование where
  anisomorphic — and use `equivalence_type` to tag which a sense is. **Drop** MW's
  pure-synonym-pile habit (Apresjan near-synonym discrimination replaces it).

- **Citation → KEEP the two-source attested/lexicographic distinction; it is literally
  the sources' own device.** PWG's koša-authority + text-passage pairing and PW/MW/SCH's
  `*`/`L.`/`°` "grammarian-or-lexicographer-only" flag **are** our
  `attested` vs `lexicographic` split — adopt the markers as the provenance vocabulary
  (`*`→lexicographic, `°`→net-new-in-layer). **Adapt density to the layer:** carry PWG's
  full citations (the spine), render PW/SCH cites as *supplements keyed to PWG*, and treat
  GRA's exhaustive RV concordance as **collapsible evidence** (count + first-cite, expand
  on demand) rather than printing every song-number. **Drop** any goal of re-verifying
  SCH's inherited Böhtlingk cites — flag them `unverified-1889` instead.

- **Run-on / derivative → ADAPT: split for translation, glue for display (already the
  decided two-mode model).** The sources disagree head-on (PWG/PW separate vs MW niched
  vs AP90 hybrid), so there is **no convention to inherit** — `pwg_ru` must choose, and
  the root-architecture decision already did: **SPLIT** derivatives/compounds into their
  own translatable cards (PWG/PW idiom, the majority), then **GLUE** them back into a
  MW-style nested display on demand. **Keep** PWG's parenthetical etymology
  (`(1. aMSa + karaRa)`) as the glue key. This is the one convention where the answer is
  *standardize deliberately*, not *keep/drop*, because the four sources genuinely conflict
  → see [`ROOT_ENTRY_ARCHITECTURE.md`](ROOT_ENTRY_ARCHITECTURE.md).

**Where the sources conflict, the spine wins.** On every axis the resolution is: take
**PWG** as the structural default (numbered etymological homonyms, equivalent+толкование
gloss, exhaustive two-source citation, separate-headword derivation), layer PW/SCH/NWS as
keyed supplements, borrow MW's nesting only as a *display* mode, and borrow AP90's
illustrative quotation as an *optional pedagogical* enrichment — never as the citation
backbone. This keeps `pwg_ru` aligned with its own already-built schema: only the **gloss
default** (toward толкование) and the **citation density per layer** need new policy; the
rest is already implemented.
