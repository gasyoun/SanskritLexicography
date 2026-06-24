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
| PWG | [`PWG/prefaces/pwgpref_all.de.md`](https://github.com/sanskrit-lexicon/PWG/blob/master/prefaces/pwgpref_all.de.md) | `csl-orig/v02/pwg/pwg.txt` | homonyms `1.aMSa/2.aMSa`; gloss-rich `arTa`; deriv-nest `kf`/`gam` |
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
