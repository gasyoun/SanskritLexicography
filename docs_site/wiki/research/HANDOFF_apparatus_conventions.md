# Handoff research — apparatus conventions across the core dictionaries (2026-06-24)

**Question.** Extending [`HANDOFF_microstructure_conventions.md`](HANDOFF_microstructure_conventions.md)
(the four "structural" conventions: homonym / gloss-type / citation / run-on), this study
maps the four **apparatus** conventions that the merged `pwg_ru` card must also respect:

1. **Grammatical apparatus & government** — gender/POS, verb class (gaṇa)/conjugation,
   accent, and the **government pattern** (*rekcija* — the case + preposition frame). The
   substrate for Apresjan's *integral description* + government-pattern goal; the card
   schema reserves a `government` field.
2. **Labels / diasystem** — register/style, chronology/genre (Vedic→classical), and
   domain/subject (botany, medicine, Nyāya…). Feeds the Renou I–V tag + the
   culture-connotation ("naive picture of the world") layer.
3. **Etymology presentation** — comparative-IE vs native *prakṛti+pratyaya* vs derivation
   reference vs none; and its typographic form.
4. **Cross-reference & sense-relations** — see-also (`s.u.`/`vgl.`/`cf.`/`см.`), synonymy
   (mostly implicit, via kośa), antonymy/conversives. The raw material for the Apresjan
   relations layer + a Russian→Sanskrit reverse index.

## Sources (all local)
Same six dictionaries as handoff C — prefaces in each sibling repo's `prefaces/` (AP90 =
`csl-orig/v02/ap90/ap90_front.txt`), entry files `csl-orig/v02/<dict>/<dict>.txt` —
**plus a 7th column: Kochergina** (Кочергина, *Sanskrit→Russian Dictionary*), the truest
**target-language precedent**, extracted into `RussianTranslation/src/koch.jsonl`
(gitignored; built from SamudraManthanam via `src/build_src.py`). Its Russian gloss
preserves the source microstructure inline (Roman-numeral homonyms `aja I/II`, Arabic
senses, gender `n., m.`, full verb paradigm, government `(Acc.)`, labels `грам./миф./бот.`,
`см.` cross-refs). The **Renou I–V** chronology axis is **already computed** into
`src/*_renou.jsonl`.

**Method.** Per dimension: (1) read each preface for its stated rule and quote it; (2)
confirm + **quantify** against the entry files (real grep/awk counts, probes
`aMSa/aja/arTa/Darma/kf/gam`); (3) add Kochergina; (4) state **keep / adapt / drop** vs
the `pwg_ru` schema. Executed as four parallel read-only research agents, synthesized here.

---

## RESULTS (executed 2026-06-24)

### Dimension 1 — Grammatical apparatus & government (rekcija/valency)

| Dict | Gender/POS | Verb class | Accent (in `<k2>`) | Government (rekcija) |
|---|---|---|---|---|
| **PWG** | `<lex>`/`<ab>` (`m.`/`n.`/`adj.`) | **No class given** — 3sg pres. only (`ga/mati`…`ga/cCati`) | 20,870 / 123,366 k2 (**17%**) | lowercase `<ab>acc.</ab>` 2542, loc. 1239, gen. 1094, instr. 960, abl. 559, dat. 464 (**~5860**) |
| **PW** | inline German abbrev.; `*` = grammarian-only | No class; 3sg pres. (Böhtlingk system) | 21,543 / 170,556 (**13%**) | **richest**: `<ab>Acc.</ab>` 4893, Loc. 2809, Instr. 2253, Gen. 2037, Abl. 1438, Dat. 990 (**~14,420**) |
| **MW** | `mfn.`/`m.`/`n.` after crude stem | tenses + participles given | 47,598 / 286,560 (**17%**) | "with `<ab>gen.</ab>`" etc.; acc. 2521, loc. 2001, gen. 1614, instr. 1602, abl. 1021 |
| **GRA** | inline (Pāṇinian case order) | full finite-form paradigm, no class | 10,699 / 12,785 (**84%** — Vedic-only) | lists actual declined forms, **not** frame labels (0 case-`<ab>`) |
| **AP90** | **headword visarga = m., anusvāra = n.** (Dir. §9) | **`{c1c}` conjugation figure + `P./A./U.`** (Dir. §11) | **0** (accent never marked) | sparse: acc. 238, loc. 181, gen. 150, instr. 106 |
| **SCH** | none (`<lex>` = 0; inline German) | inline only (supplement) | 1124 / 29,125 (**4%**, skewed) | 0 case-`<ab>` (transcribed pw idiom) |
| **Koch** | `n., m.` inline; homonyms split | **full paradigm in parens** `(P. pr. gacchati — fut. …pf. …)` | `/`-accent inside `/slp1/` | **inline Russian prose** (the model): `(Acc.)`/`Abl.`/`Gen.` + "ради/для", "по причине", "в сочет. с Acc." |

**Evidence.**
- PWG — no class, derive from 3sg: *"Bei den Verbalwurzeln findet man keine Klasse angegeben, da diese sich aus der beigefügten 3. Person sg. praes. … von selbst ergiebt"* — [pwgpref_all.de.md L189](https://github.com/sanskrit-lexicon/PWG/blob/main/prefaces/pwgpref_all.de.md).
- PW — accent + construction + genus only where attested, grammarian-only flagged `*`: *"Accentuirt sind nur diejenigen Wörter, die in accentuirten Texten vorkommen … Ein Wort, eine Bedeutung, eine Construction oder ein Genus, die bis jetzt nur von Grammatikern … aufgeführt werden, sind mit \* bezeichnet"* — [pwpref_all.de.md L60](https://github.com/sanskrit-lexicon/PWK/blob/master/prefaces/pwpref_all.de.md).
- AP90 — gender by headword ending + conjugation figure: *"the visarga … indicating masculine gender, and the anusvāra neuter"* (§9); *"the Arabic figure before P., A. and U. denotes the conjugation … Parasmaipada … Ātmanepada … Ubhayapada"* (§11) — [ap90_front.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ap90/ap90_front.txt). Real entry: `{#gam#}¦ {c1c} <ab>P.</ab> ({#gacCati, jagAma, agamat#}…)`.
- Kochergina — government inline (the model): `अर्थ … 1) цель- Acc. अर्थम्, Dat. अर्थाय, Loc. अर्थे ради, для 2) причина … Abl. अर्थद् по причине, из-за`; `गम् (P. pr. gacchati — fut. …) … 6) достигать чего-л. (Acc.) … 11) в сочет. с Acc.`

**Keep / adapt / drop.**
- **KEEP, and follow Kochergina as the model for the `government` field.** Koch already prints rekcija inline in Russian — exactly the Apresjan government frame the schema reserves. Map PWG's case-`<ab>` tokens → a structured `government` value rendered in the Koch idiom (`Acc.` + Russian preposition gloss).
- **ADAPT PWG's "no class" into the `<gram>`/`<lex>` integral link.** PWG gives only the 3sg present; derive and store the gaṇa explicitly (Koch supplies the full paradigm), so the integral-grammar layer is complete though the German source omits it.
- **KEEP accent** — PWG's `/` marks (17% of headwords) transfer directly into the Russian headword, as Koch does inside `/gam/`.
- **DROP reliance on SCH for grammar** (`<lex>` = 0, accent 4%, no case tags) — treat its grammar as inline German prose, not a structured source.

### Dimension 2 — Labels / diasystem

| Dict | Register / style | Chronology / genre | Domain / subject |
|---|---|---|---|
| **PWG** | **None** (19th-c. practice). Diasystem only via `<ab>` (`N. pr.` 17,791, `Bein.` 2625, `patron.` 2094) | **Implicit** via `<ls>` siglum; Vedic 20,719 vs classical 100,791 (≈1:5) | **Implicit** in prose/`<ls>`: `Pflanze` 2981, `Astr*` 1477, `medic*` 237, `Gramm*` 415 — no domain tag |
| **PW** | **None** | **Implicit**; Vedic 1902 vs classical 9901 (≈1:5) | **Implicit**: `Pflanze` 1654, `Astr*` 773, `medic*` 179 |
| **MW** | **None** stylistic; encyclopedic articles scattered throughout | **Implicit, Vedic-heavy** — Vedic 38,234 vs classical 15,973 (**the only dict Vedic > classical**) | `plant` 3158, `Astr*` 816, `medic*` 670; plants flagged by capital-letter convention |
| **GRA** | **None** | **Genre constant = RV** (Vedic 508 vs classical 1) — fixed by design, no marking | **None** (pure RV glossary) |
| **AP90** | **None** stylistic | **Classical-leaning** — Vedic 37 vs classical 5536 (≈1:150) | **Explicit in-line + bracket**: technical terms in Nyāya/Alaṃkāra/Vedānta/Grammar/Dramaturgy; **2011** `[…]` mythology spans (Dir. §13); `plant` 1125 |
| **SCH** | **None** | **Implicit**, classical-leaning (Vedic 327 vs classical 940) | **Implicit**, sparse (`Pflanze` 101) |
| **Koch** | **Yes — thin register set**: `поэт.` 6, `воен.` 6, `юр.` 8, `разг.` 1 (the one source with style tags) | not per-entry labelled | **Explicit abbreviated domain labels** (the model): `nom. pr.` 920, `adv.` 949, `грам.` 229, `филос.` 75, `астр.` 28, `миф.` 20, `бот.` 20, `мед.` 4 |

**Evidence.**
- PWG states the *ideal* (mark genre; Vedic attestation = a "patent of nobility") but leaves it implicit: *"Wohl aber wäre eine allgemeine Angabe der Schriftgattungen, in welchen ein Wort in einer angegebenen Bedeutung gebraucht wird, am Platz … Kommt ein Wort oder eine Wortbedeutung schon im Veda vor, so müsste dieses … vermerkt werden, da Niemand ein derartiges Adelsdiplom mit gleichgiltigem Auge betrachten darf"* — [pwgpref_all.de.md L1174/1191](https://github.com/sanskrit-lexicon/PWG/blob/main/prefaces/pwgpref_all.de.md).
- MW — encyclopedic stance: *"the articles on mythology, literature, religion, and philosophy, scattered everywhere throughout its pages"* — [mwpref_all.en.md L390](https://github.com/sanskrit-lexicon/MWS/blob/master/prefaces/mwpref_all.en.md).
- AP90 §13 — *"Mythological allusions are explained in small type in the body of the work between rectangular brackets []."* — [ap90_front.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ap90/ap90_front.txt) (confirmed: 2011 `[…]` spans).

**Renou — already solved.** The Renou I–V chronology axis is **precomputed and stored**:
`pwg_ru_translated.renou.jsonl` carries `renou` (e.g. `["II"]`), `renou_oldest`,
`renou_oldest_source`; the richer `mw_renou.jsonl`/`ap90_renou.jsonl` add `renou_ls`,
`renou_dcs`, `renou_enriched`, `renou_provenance` — i.e. each Renou layer is derived from
**both** the citation siglum (`ls`) **and** the DCS corpus (`dcs`), with provenance. The
"implicit genre via `<ls>`" that all six dicts encode is thus already resolved into
explicit period labels per sense. The **domain** axis is *not* in these objects — it still
needs `<ab>`/bracket mining + Koch's `грам./бот./миф.` tags.

**Keep / adapt / drop.**
- **KEEP — the Renou I–V tag is solved.** Surface `renou_oldest` as the printed period stamp; the dual-witness (`ls`+`dcs`) design backfills confidence. The Vedic:classical siglum mix (PWG 1:5, MW Vedic>classical, AP90 1:150, GRA RV-only) confirms the axis is real and dict-discriminating.
- **ADAPT — domain labels: follow Koch, not the German source dicts.** PWG/PW/MW/SCH carry domain *implicitly* (no tag). Koch provides the target-language abbreviated set (`грам.` 229, `nom. pr.` 920, `миф.` 20, `бот.` 20, `мед.` 4, `астр.` 28, `филос.` 75); map PWG's `<ab>N. pr.`/`patron.`/`Bein.` and AP90's bracketed Nyāya/Alaṃkāra explanations onto it.
- **ADAPT — AP90's `[ ]` small-type mythology (2011 spans) + MW's encyclopedic articles** are the raw feed for Apresjan's culture-connotation layer — extract as connotation, not as headword gloss.
- **DROP — register/style for the 19th-c. dicts** (confirmed absent in all six). Only Koch carries a thin set; treat register as an optional Koch-sourced annotation, not a structural column.

### Dimension 3 — Etymology presentation

| Dict | Given? | Tradition | Typographic form | Density (real count) |
|---|---|---|---|---|
| **PWG** | Yes, routinely | Native-derivation `(von X)` + sparing IE comparison | round parens `(von {#…#})` | **20,729** `(von ` |
| **PW** | Rarely as a formal field | derivation-only reference | round parens | **812** `(von ` |
| **MW** | Yes, very routinely | comparative-IE: `fr. √` + bracketed cognates | `(probably fr. √ …)`; comparisons in `[ ]` | **7308** `<ab>fr.</ab>` · 14,290 `√` |
| **GRA** | Yes ("could not be missing") | comparative-philological via sigla | `Cu./Fi./Ku./BR.` inline | **350** `Cu.` · 95 `Ku.` · 71 `Fi.` · 301 `BR.` |
| **AP90** | Yes, for every important word | **native Pāṇinian *prakṛti + pratyaya*** (kṛt/taddhita) | **square brackets** `[{#aMS ac#}]` | **6826** `[{#…` |
| **SCH** | Essentially no (supplement) | none / rare `(von …)` | round parens (rare) | **68** `(von ` |
| **Koch** | No (almost never IE) | **root cross-reference only** (`см. कर्`) | plain `см. ` prose | **7519** `см. ` |

**Evidence.**
- PWG — etymology recovers worn meanings: *"…da darf man zurückgreifen in den Schatz des Veda … Deshalb wird auch die Etymologie insbesondere durch die Erschliessung der alten Sprache gefördert"*; and the **big-vs-handy warning**: *"In einem grossen Wörterbuche bringt eine gewagte Etymologie … geringen Schaden … ein Handwörterbuch ist in den Händen von Anfängern, denen nur ganz Sicheres geboten werden darf"* — [pwgpref_all.de.md](https://github.com/sanskrit-lexicon/PWG/blob/main/prefaces/pwgpref_all.de.md). Probe: `{#aMSala#}¦ (von {#aMSa#} {%Schulter%}) adj. {%stark, kräftig%}`.
- MW — etymology in parens covers the whole family: *"their etymology—given in a parenthesis—applies to the whole family of cognate words … In this way all repetition of etymologies is avoided"* — [mwpref_all.en.md L355](https://github.com/sanskrit-lexicon/MWS/blob/master/prefaces/mwpref_all.en.md). Probe: `a/MSa ¦ m. (probably fr. √ 1. aS …)`.
- GRA — short, by siglum: *"The etymology could not be missing … However, I kept the etymology as short as possible by referencing Curtius (Cu.), Fick (Fi.), Kuhn (Ku.), Böhtlingk und Roth (BR.)"* — [grapref_all.en.md L72](https://github.com/sanskrit-lexicon/GRA/blob/master/prefaces/grapref_all.en.md).
- AP90 — native grammarians: *"I have followed the system of native grammarians who resolve every word into its 'prakṛti' and 'pratyaya' … Philological comparisons have been given only where useful"* — [ap90_front.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ap90/ap90_front.txt). Probe: `{#aMSaH#}¦ [{#aMS ac#}] …`.

**Keep / adapt / drop.**
- **KEEP the PWG `(von X)` derivation field, translated** (densest field, 20,729×; a *safe, native derivation reference*, not speculative): `(von {#aMSa#} {%Schulter%})` → `(от {#aMSa#} «плечо»)`, per the project's translate-the-German-wrapper rule.
- **DROP / do not amplify comparative-IE speculation.** PWG's own preface assigns risky etymology to the BIG dictionary; a learner-facing Russian edition should not import GRA/MW-style IE-cognate apparatus — keep only what PWG itself prints.
- **ADAPT (optional): an AP90-style native `[prakṛti+pratyaya]` gloss in `[ ]`** — most student-useful, least speculative, typographically distinct from PWG's `( )`. Treat as an enhancement (PWG lacks the Pāṇinian suffix tags, so it would need derivation).
- **Koch sets the floor, not the model** (≈0 etymology, only `см. <root>`): `pwg_ru` should *exceed* Koch by retaining PWG's `(von)` derivations.

### Dimension 4 — Cross-reference & sense-relations

| Dict | See-also / compare (real count) | Synonymy | Antonymy / conversive |
|---|---|---|---|
| **PWG** | `Vgl.` 18,299 · `vgl.` 11,348 · `s. u.` 3410 (≈33k) | implicit via kośa cites (`AK.`, H., Trik.) | `Gegens.` 1241 — inline, not structured |
| **PW** | `Vgl.` 2470 · `dass.` 1913 (=same-as) · `s. u.` 1234 · `vgl.` 867 | `dass.` = near-equivalence pointer; else kośa-implicit | `Gegens.` 37 |
| **MW** | `cf.` 11,383 · `q.v.` 3506 | implicit via kośa cites | `opp.` 446 — inline |
| **GRA** | `s.` (siehe) 1630 · `<hom>` root-refs 1193 · `Vgl.` 239 | root-family grouping (structural), not synonymy | none |
| **AP90** | `See ` 1730 · `q. v.` 930 | **semi-explicit** (§5: synonyms piled under one numbered sense) | `opp.` 321 — inline |
| **SCH** | ~0 (Nachträge — no internal cross-ref apparatus) | none structural | none |
| **Koch** | `см.` 7522 · **of which 2636 carry a sense number** (`см. <lemma> N)`) | `см.` collapses synonym/variant lemmas onto a head | `противоп.` 24 |

**Evidence.**
- AP90 §5 (the one explicit synonymy rule): *"…several synonyms are given under the same meaning, from which the reader will have to make his choice. Where the shades of meaning are sufficiently broad, they are numbered as separate senses."* — [ap90_front.txt L216](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ap90/ap90_front.txt).
- PWG `S. u.` (probe `aMSaka`): `{#aMSaka#}¦ <lex>f.</lex> {#aMSikA#} … <ab>S. u.</ab> 1. {#aMSa#}` — [pwg.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt).
- PW `dass.` (probe `aMSaprakalpanA`): `{#aMSaprakalpanA#}¦ <lex>f.</lex> <ab>dass.</ab> <ls>M. 8,211</ls>` — [pw.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt).
- Kochergina sense-granular cross-ref (the model): `कृ /kṛ/ см. कर् I`; `см. लालक 2)` — `RussianTranslation/src/koch.jsonl` (gitignored/local; 2636 of 7522 `см.` carry a sense number).

**Keep / adapt / drop.**
- **KEEP & promote PWG's `Vgl.`/`vgl.`/`S. u.` (~33k pointers) to a structured SKOS layer.** Translate the token (`Vgl.`→«ср.», `S. u.`→«см.») but capture the target lemma as a typed `skos:related`/`seeAlso` edge — the densest relation signal in the source.
- **ADAPT Kochergina's `см. <lemma> N)` as the cross-ref target model** — the only precedent with **sense granularity** (2636/7522). Resolve each cross-ref to `lemma#sense`, feeding the Russian→Sanskrit reverse index + near-synonym discrimination.
- **ADAPT kośa citations (`AK.`/H./Trik.) into `skos:closeMatch` synonym clusters** — synonymy is implicit in every print dict; mine lemmas co-cited under one Amarakośa locus as a candidate near-synonym set (the cheapest synonymy layer the sources never marked).
- **DROP antonymy as a first-class layer** — `Gegens.`/`opp.`/`противоп.` are real but sparse and inline; capture opportunistically, don't build a conversive schema.

---

## Cross-dimension harmonization note

One through-line ties all four apparatus dimensions together: **Kochergina is the
Russian-target *model*, PWG remains the structural *spine*, and the precomputed Renou
layer already supplies chronology.**

- **Where the source dicts under-specify for a Russian reader, Kochergina is the
  template.** It is the only one of the seven that prints **government inline** (`(Acc.)` +
  Russian preposition), **abbreviated domain labels** (`грам./миф./бот.`), **register**
  tags (thin), and **sense-numbered cross-refs** (`см. lemma N)`) — i.e. exactly the four
  fields the source dictionaries leave implicit. `pwg_ru` should adopt Koch's *rendering
  conventions* for `government`, diasystem labels, and typed cross-refs.
- **But PWG stays the structural spine and Koch never overrides its content.** PWG supplies
  the senses, the citations, the `(von)` etymology, and the homonym split; Koch supplies
  only the *Russian apparatus idiom* and, where PWG omits grammar (verb class), a
  fill-in. This mirrors handoff C's verdict ("the spine wins") and the
  [`DICTIONARY_CHAIN.md`](RussianTranslation/DICTIONARY_CHAIN.md) layering.
- **Two axes are already done in code.** Chronology/genre = the precomputed **Renou I–V**
  layer (`renou_oldest` + `ls`/`dcs` provenance). Sense order = handoff B's verdict (keep
  PWG's own `<div n>` order). Neither needs new policy.
- **Net new policy needed for only two things:** (1) the **`government` field** — derive
  from PWG case-`<ab>` tokens, render in Koch's idiom; (2) the **domain-label set** —
  adopt Koch's Russian abbreviations and map PWG `<ab>`/AP90 brackets onto them. The other
  apparatus decisions are *keep PWG* (etymology, cross-ref density, accent) or *drop*
  (register back-fill, IE-etymology amplification, antonymy schema).

## Cross-links
- Structural conventions → [`HANDOFF_microstructure_conventions.md`](HANDOFF_microstructure_conventions.md).
- Sense order → [`HANDOFF_sense_ordering.md`](HANDOFF_sense_ordering.md).
- Root nesting/splitting → [`ROOT_ENTRY_ARCHITECTURE.md`](ROOT_ENTRY_ARCHITECTURE.md).
- What `pwg_ru` already implements → [`../DICTIONARY_CHAIN.md`](../DICTIONARY_CHAIN.md), [`../APRESJAN.md`](../APRESJAN.md).
