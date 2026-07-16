# When Zero Means Nothing: Recovering the Indigenous Microstructure of the *Śabdakalpadruma* and the *Vācaspatya*

_Created: 17-07-2026 · Last updated: 17-07-2026_

**A30 · full paper draft · draft 17-07-2026 · target: International Journal of Lexicography (primary) / World Sanskrit Conference 2027 (alternate)**

> **Status:** first full draft from the P4 outline ([roadmap Part III](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md)), readiness 3/5 proposed. Every number herein is read from committed csl-atlas artifacts (2026-06 measurement snapshot, 43-dictionary corpus; re-verified in the 2026-07-03 referee pass of the companion root-grammar paper). No figure in this draft is newly computed.
> **Scope coordination:** this paper claims the *record-level* indigenous microstructure — the entry template, the megastructure key, the *iti*-unit, the register contrast. The verbal-root grammatical layer (*gaṇa*/*pada*/transitivity via *anubandha*) is claimed by the companion A04; derivational affixes by A35; sense inheritance by A02; the two citation registers by A08. See the coordinated-siblings block in the References.

Mārcis Gasūns · ORCID [0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X) · gasyoun@ya.ru

## Abstract

The two largest indigenous Sanskrit–Sanskrit dictionaries in the Cologne Digital Sanskrit Dictionaries corpus — the *Śabdakalpadruma* (**42,531** digitized records) and the *Vācaspatya* (**50,135** records) — score zero on every microstructural detector built for the European dictionaries of the same corpus: **0** `<ab>` abbreviation tags, **0** `<div>` apparatus blocks, **0** `<ls>` source citations, **0** `<s>` lemma markup, against explicit-markup counts running to the hundreds of thousands in Monier-Williams and the Petersburg dictionary. Read naively, the two kośas are the emptiest objects in the corpus. This paper shows that the zero is a fact about the instruments, not the dictionaries, and recovers the microstructure the detectors cannot see. Three results. First, the *entry template*: the *Śabdakalpadruma* record is a disciplined fixed-slot structure — headword, indicatory-letter slot, locative-case meaning (continuing the *nānārtha* convention of the classical kośa), authority citations closed by *iti*, and verse quotation — encoded entirely by position and convention, without one tag. Second, the *megastructure key*: the dictionary's own front matter (Durgādāsa's *anubandha* table, reproduced by the compilers) decodes the microstructure — the tradition even prints its own zero-meaning rule, instructing that roots without an indicatory letter receive "a dot or a zero" (*bindu-yuktam athavā śūnyam*). Third, the *sense/citation unit*: the microstructural quantum of the kośa is the *iti*-closed group, in which enumeration and attestation fuse — **53.3 %** of authority-marked units in the *Śabdakalpadruma* and **77.6 %** in the *Vācaspatya* are authority-terminal, and the difference tracks record type (short encyclopaedic entry vs. long discursive commentary), not dictionary identity. By tagged-citation density the *Śabdakalpadruma* ties for last place in the 44-file corpus; by *iti*-density it ranks second. The moral generalizes beyond Sanskrit: in any multi-convention corpus, a cross-dictionary zero must be reported as "does not use this markup," never as "lacks this feature" — otherwise the statistic systematically erases exactly the tradition it claims to measure.

**Keywords:** Sanskrit lexicography; kośa; Śabdakalpadruma; Vācaspatya; microstructure; indigenous lexicographic traditions; measurement bias; digital lexicography

## 1. The problem: two dictionaries that measure as empty

The Cologne Digital Sanskrit Dictionaries (CDSL) corpus digitizes both of the lexicographic civilizations that described Sanskrit: the European dictionaries of 1832–1957 (Wilson, the Petersburg dictionaries, Monier-Williams, Apte and their descendants) and the indigenous tradition, represented at scale by two nineteenth-century Calcutta compilations — Rādhākānta Deva's *Śabdakalpadruma* (SKD) and Tārānātha Tarkavācaspati's *Vācaspatya* (VCP). Both are Sanskrit-in-Sanskrit encyclopaedic dictionaries, and together they contribute 92,666 records to the corpus.

The corpus's microstructural instruments were built, reasonably, around the explicit markup of the European files: `<ab>` for grammatical abbreviations, `<div>` for apparatus blocks, `<ls>` for literary-source citations, `<s>` for Sanskrit lemmata. Against those instruments the two kośas return the most extreme profile in the corpus ([`MICROSTRUCTURE_ZERO_MEANING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ZERO_MEANING.md)):

| Dictionary | Records | `<ab>` | `<div>` | `<s>` | `<ls>` |
|---|---:|---:|---:|---:|---:|
| SKD | 42,531 | 0 | 0 | 0 | 0 |
| VCP | 50,135 | 0 | 0 | 0 | 0 |
| MW (1899) | 286,560 | 182,097 | 15,312 | 350,610 | dense |
| PWG (1855–75) | 123,366 | 185,563 | 113,613 | 0 | dense |

*Source: tag inventory in [`MICROSTRUCTURE_ZERO_MEANING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ZERO_MEANING.md); register shares in [`data/dictionary-coverage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary-coverage.json).*

A naive corpus-wide statistic — average senses per entry, citation density, grammar-marking share — therefore reports the two largest indigenous dictionaries as the *emptiest* objects in the corpus. The question this paper answers is whether that emptiness is real (the kośas genuinely lack microstructure) or instrumental (the microstructure is present but encoded by conventions no European-keyed detector reads). The answer, demonstrated on three independent layers, is instrumental — and the recovered microstructure turns out to be dense, disciplined, and internally consistent.

The methodological rule the demonstration licenses is stated in the corpus's measurement doctrine and is worth quoting at the outset, since everything below is an application of it:

> "Marker-based counts are comparable **only within the set of dictionaries that share the same markup convention** […] A cross-dictionary **0 is never a statement about content.** Report it as 'does not use this markup,' never as 'lacks this feature.'" ([`MICROSTRUCTURE_ZERO_MEANING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ZERO_MEANING.md))

## 2. Background: the kośa tradition and its non-European microstructure

The indigenous Sanskrit dictionary is not an underdeveloped European dictionary; it is a different genre with its own access structures and its own entry grammar. Vogel's survey of the tradition (1979) established the fundamentals. Classical kośas divide into synonymic (*ekārtha*) works — subject-grouped, versified catalogues of words sharing a meaning, headed by the *Amarakośa* — and homonymic (*anekārtha*, *nānārtha*) works listing words of several meanings. Because the books were composed for memorization rather than consultation, "nowhere does a European type of organization occur": ordering runs by verse economy, syllable count, final consonant, or gender rather than by initial letter. Within the entry, the tradition developed compact positional devices in place of labels: synonyms cited in the nominative; homonym senses listed in the *locative* case, the headword repeated only when gender changes; gender itself signalled by grammatical form (the *ekaśeṣa* device — dual for a two-meaning word, plural for three or more); new articles set off by particles (*atha*, *tu*) rather than typography.

The nineteenth-century Calcutta compilations inherit this entry grammar while changing the macrostructure: the SKD and VCP are alphabetized reference works of pan-Indic scope, compiled by paṇḍits — Rādhākānta Deva's team (SKD, published in parts from 1822) and Tārānātha Tarkavācaspati (VCP, 1873–1884) — who fused the classical kośas, the grammatical tradition (Pāṇini's *Dhātupāṭha* and its Bengali recension, Vopadeva's *Kavikalpadruma* with Durgādāsa's commentary), the śāstric literatures, and verse attestation into consolidated prose entries. The result is a dictionary whose microstructure is carried by three indigenous mechanisms, each invisible to tag-based detection:

1. **Position and case**, continuing the classical conventions above (meanings in the locative; slots in fixed order).
2. **Indicatory letters** (*anubandha*): a metalinguistic code inherited from Pāṇinian grammar, in which appended consonants and vowels on a cited root encode its grammatical behaviour.
3. **The *iti* construction**: Sanskrit's native quotation-closer, which ends an enumeration or a quotation and names its authority (*ity Amaraḥ*, *iti Medinī*, *iti kavikalpadrumaḥ*), fusing content and attestation into one unit.

Comparative lexicography offers a close analogue. The Arabic tradition described by Baalbaki (2014) likewise splits into onomasiological (*mubawwab*) and form-based (*muǧannas*) macrostructures, organizes the form-based works by consonantal root and morphological pattern rather than surface alphabet, and grounds entries in a graded witness apparatus (*šawāhid*) of Qurʾānic, poetic and proverbial attestation. A detector keyed to European citation markup would erase the Arabic tradition's evidence structure exactly as `<ls>`-counting erases the kośa's. The zero-meaning problem is not a Sanskrit curiosity; it is the general condition of measuring any pre-modern non-European lexicography with instruments derived from one convention family.

Within lexicographic theory, the recovery below can be read in Apresjan's (2000) terms. The SKD entry, it will emerge, is a *lexicographic type* in the strict sense — a class of entries described on one fixed grid — and the individual record is a compressed *portrait* whose slots are filled by convention rather than by labels. The type/portrait apparatus, developed for explicit modern dictionaries, transfers surprisingly well to a tradition that never wrote its grid down as a schema — but did, as §5 shows, print its code table.

## 3. Data and method

**Corpus.** CDSL source files (`csl-orig/v02`), 2026-06 measurement snapshot (43 dictionary files; the corpus grew to 44 in 2026-07, and rank statements below say "of 44" where the companion study already recomputed them). SKD and VCP are romanized (SLP1) Sanskrit prose; display forms below are IAST.

**Instruments.** Three kinds, all committed in the [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) repository:

- *European-keyed detectors* (the M1–M3 scripts), which count `<ab>`/`<div>`/`<ls>`-family markup — used here only to establish the zero inventory of §1.
- *Convention-keyed parsers*: the indigenous-root extractor [`scripts/lexico/m4_indigenous.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m4_indigenous.py) (whose grammatical results are the companion paper A04's and are only cited here), and the *iti*-unit segmenter behind [`data/lexico/r2_kosa_fusion.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion.json) (built by [`scripts/build-r2-kosa-fusion.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-kosa-fusion.mjs)), which segments each record on closing-authority constructions and classifies the resulting units.
- *Register profiling*: per-dictionary structural-register shares (grammar-marking share, tagged-citation share, inline-*iti* share) in [`data/dictionary-coverage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary-coverage.json), with the family-separation review in [`docs/H6_STRUCTURAL_REGISTER_REVIEW.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H6_STRUCTURAL_REGISTER_REVIEW.md).

**Primary sources for the key.** The *anubandha* table used to read SKD's indicatory-letter slot is Durgādāsa Vidyāvāgīśa's *Dhātudīpikā* (on Vopadeva's *Kavikalpadruma*), as reproduced in the SKD's own front matter; the digitized table and its verification against Palsule's edition are committed in [`docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md).

**Method of this paper.** No new computation. The paper assembles, from the committed artifacts, the three-layer demonstration that the kośa microstructure is recoverable — and states the measurement doctrine that the recovery licenses. Where a committed figure is owned by a companion study (root grammar, sense inheritance, citation registers), it is cited, not re-derived.

## 4. The entry template: what an SKD record is

The SKD record is a fixed-slot prose structure. The worked example from the measurement doctrine — the root *īr* — shows every slot ([`MICROSTRUCTURE_ZERO_MEANING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ZERO_MEANING.md); SLP1 as committed, IAST reading beneath):

```
Ira¦, ki gatO . preraRe . iti kavikalpadrumaH . (vA, curAM-paraM-sakaM-sew .) nudi . ki Irayati Irati .
```

Read positionally: **headword** (*īra*, closed by the daṇḍa-like `¦` separator) — **indicatory-letter slot** (*ki*) — **meaning in the locative** (*gatau* 'in the sense of motion') — **causative sense** (*preraṇe* 'in causing') — **authority citation closed by *iti*** (*iti kavikalpadrumaḥ*) — **parenthesized grammatical résumé** (class *curādi*, *parasmaipada*, transitive, *seṭ*) — **inflected forms** (*īrayati*, *īrati*). Seven information categories that a European dictionary would distribute across seven kinds of explicit markup, and, as the doctrine notes, "not one `<ab>` tag."

Three properties of the template deserve emphasis.

**It is classical, not improvised.** The locative-case meaning slot continues the *nānārtha* convention Vogel documents for the classical homonymic kośa; the *iti*-closed authority slot continues the kośa-and-commentary citation practice; even the parenthesized résumé is a compressed *Dhātupāṭha* formula. The SKD did not invent an entry grammar; it consolidated the tradition's existing one into reference-work prose.

**It is uniform at scale.** The template is not anecdotal. The convention-keyed parser recognizes the root-entry variant of the template in **2,544** SKD records and **2,230** VCP records ([`data/lexico/indigenous_by_dict.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/indigenous_by_dict.json)); the *iti*-segmenter recovers **122,691** units across SKD's 42,531 records (2.88 per record) and **65,675** across VCP's 50,135 (1.31 per record) ([`data/lexico/r2_kosa_fusion.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion.json)). A corpus that detectors report as structureless yields, to a parser that reads the convention, roughly 188,000 microstructural units.

**It is machine-decodable because it is disciplined.** In Apresjan's vocabulary: the SKD verbal entry is a lexicographic type — one grid, positionally encoded — and each record is a portrait filled against that grid. Uniformity is what makes recovery possible; the recovery's success (the agreement figures cited in §5) is in turn evidence of the discipline.

The VCP realizes the same tradition in a different genre register. Where the typical SKD entry is a short encyclopaedic notice, the typical VCP entry is a discursive commentary: extended śāstric argument threading source sigla (a trailing-`0` convention: *hemaca0*, *vahnipu0*) through prose, with *iti*-closures marking quotation boundaries inside the argument. The companion sense-inheritance study's exemplar is *dharma*: the SKD closes a synonym run (*puṇyam, śreyaḥ, sukṛtam, vṛṣaḥ*…) with *ity Amaraḥ* — one fused unit — while the VCP develops a Mīmāṃsā discussion of the same headword across many units. Section 6 quantifies this contrast; the point here is that both are realizations of one entry grammar, differing in the proportions of the slots, not in the slots themselves.

## 5. The megastructure key: front matter decodes microstructure

The second recovery layer is methodological and, we argue, generalizable: **the kośa's own front matter is the codebook for its microstructure.**

The indicatory-letter slot of the SKD root template (§4) is opaque to any modern reader without a key — the letters are *anubandhas*, the Pāṇinian tradition's metalinguistic code, in Vopadeva's Bengal-school variant rather than the pan-Indian *Dhātupāṭha* inventory. The key exists, and the SKD prints it: the compilers reproduce Durgādāsa's *anubandha-phala* table — 46 indicatory letters with their grammatical effects — in the dictionary's front matter. The digitization of that table ([`docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md), verified against Palsule's edition of the *Kavikalpadruma*, which tallies 43 code letters — a difference in variant-counting, not substance) is what turned the slot from noise into data: applying the key raised the machine-resolvable grammatical coverage of SKD root entries from 1,117 to **1,737** records for verb class and from 1,167 to **1,498** for voice — gains of 55 % and 28 % over surface markers alone. (These decoded features, their cross-dictionary agreement — verb class compatible across five independent lexica in **85.5 %** of multiply-classified roots — and their linguistic analysis are the companion paper A04's results; this paper claims the method: where the key came from and what kind of object it is.)

The tradition even states the zero-meaning rule about itself. The front-matter table's preamble instructs (quoted in the committed key document):

> प्रत्येक-धातोरनुबन्धञ्च निर्णीतवान्। येषां धातूनामनुबन्धो नास्ति तत्स्थानं बिन्दुयुक्तमथवा शून्यमास्ते।
> "…and the anubandha of each root has been determined. For roots that have no anubandha, that slot carries a dot — or a zero (śūnya)."

A zero in the SKD's own microstructure is thus an *explicit, printed convention*: the marked absence of a marker, meaningful only against the codebook. The paper's title generalizes the compilers' own doctrine: a zero read without the convention that produced it means nothing.

The megastructural moral: in the European tradition, front and back matter are usage guides, ancillary to the entries; Wiegand's textbook distinction between the *megastructure* and the microstructure it frames treats the former as orientation. In the kośa, the relation is stronger — the front matter is *load-bearing*: without it, a systematic slot present in ~1,925 of 2,544 root records (76 %) is undecodable. For digitization practice this inverts a habit: CDSL, like most retro-digitization projects, digitized entries first and prefaces never or last; the SKD case shows the preface can be the highest-value page in the book. A systematic megastructure study of the corpus's remaining narrative dictionaries (the roadmap's Q1-2027 item) is the natural sequel.

## 6. The sense/citation unit: the *iti*-group

The third layer is the microstructural quantum itself. European microstructure separates the *sense* (a numbered definition) from the *apparatus* (the citations supporting it); the corpus's data model, and most of digital lexicography's (TEI Lex-0's `sense` vs `cit`), presupposes that separation. The kośa's native unit fuses them: an enumeration or definition runs to its authority and closes — *…ity Amaraḥ* — so that the content and its attestation form one construction, the ***iti*-group**.

The committed segmentation quantifies the fusion ([`data/lexico/r2_kosa_fusion.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion.json)):

| | SKD | VCP |
|---|---:|---:|
| Records | 42,531 | 50,135 |
| *iti*-units recovered | 122,691 | 65,675 |
| Records with ≥1 authority-marked unit | 18,418 (**43.3 %**) | 38,459 (**76.7 %**) |
| Authority-marked units | 24,087 | 42,980 |
| — of which authority-terminal (fused) | 12,831 (**53.3 %**) | 33,352 (**77.6 %**) |
| — of which separable | 11,256 (46.7 %) | 9,628 (22.4 %) |

*Source: [`r2_kosa_fusion.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion.json), regenerated by [`build-r2-kosa-fusion.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-kosa-fusion.mjs); fusion ("authority-terminal") = ≥20 non-whitespace characters of definitional content precede the earliest authority match within the unit — a definition running to its closing citation; otherwise separable.*

Two readings of the table matter for lexicographic theory.

**Fusion is register-dependent, not dictionary-essential.** The companion sense-inheritance study (A02), which shipped this dataset, tested whether fusion is a *dictionary-level* trait ("SKD fuses, VCP separates," as its dictionary-scale exemplars first suggested) and found the corpus-scale answer to be no: the fusion rate tracks **record type** — short encyclopaedic entries fuse (the enumeration ends at its authority); long discursive commentary separates (quotations sit inside continuing argument). The VCP, three-quarters of whose records carry authority-marked units, is *more* fused among those units than the SKD, because its authority citations more often close their discursive unit. The European question "is the citation part of the sense?" has no convention-independent answer here — which is precisely what a data model must record.

**The invisible register is dense.** The same corpus whose tagged-citation count for SKD/VCP is zero carries, by the companion citation-register study (A08), on the order of **80,164** *iti*-citations in the SKD (1.88 per record) and **15,619** in the VCP — an upper-bound register indicator, since *iti* also serves grammatical quotation. The rank inversion is the sharpest single statement of the zero-meaning problem: by `<ls>` density the SKD ties for last among 44 source files; by *iti*-density it ranks **second of 44**, behind only the *Kṛdantarūpamālā* and ahead of every European dictionary including the Petersburg lexicon. One statistic, two conventions, opposite rankings of the same book.

A proposed typology of the *iti*-units (definition-unit, authority-quotation, authority-siglum, commentarial-discussion, morphology unit, headword stub; [`docs/R2_INDIGENOUS_ITI_AUTHORITY_LABELS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_INDIGENOUS_ITI_AUTHORITY_LABELS.md)) exists in machine-proposed form; it is deliberately not used for any quantitative claim above because it has not passed scholar review (§8).

## 7. One tradition, two registers: SKD vs VCP

The recovered structure permits, for the first time in this corpus, a *within-tradition* microstructural comparison — the kind of comparison the zero inventory made impossible. On the corpus's structural-register profile ([`data/dictionary-coverage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary-coverage.json)):

| Share of records | SKD | VCP | MW | PWG |
|---|---:|---:|---:|---:|
| Grammar-marking | 2.49 % | 6.98 % | 73.27 % | 80.11 % |
| Tagged citation (`<ls>`) | 0 | 0 | 79.13 % | 94.30 % |
| Inline *iti* citation | **88.78 %** | **10.08 %** | 0.06 % | 0.67 % |

*Source: `blockPct` fields in [`dictionary-coverage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary-coverage.json); family review in [`H6_STRUCTURAL_REGISTER_REVIEW.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H6_STRUCTURAL_REGISTER_REVIEW.md).*

On this profile the two kośas and the *Kṛdantarūpamālā* separate cleanly from every European family as an **indigenous-prose register** — prose and *iti* where the Europeans have tags and sigla — with the explicit review caveat that VCP's low *detected* inline-*iti* share is itself partly a recovery artifact (its `…0` siglum convention is yet another citation encoding that plain *iti*-counting underreads). The within-pair contrast is genre, quantified:

- **SKD, the encyclopaedic register:** *iti* on 88.78 % of records, 2.88 units per record, 43.3 % of records authority-marked — short entries, densely and explicitly sourced, the classical kośa's citation habit industrialized.
- **VCP, the commentarial register:** *iti* on 10.08 % of records as a share, yet 76.7 % of records carrying authority-marked units and the higher fusion rate of the two kośas measured — fewer, longer, argumentative entries in which authority is woven through śāstric discussion rather than appended to enumerations.

The same entry grammar, deployed at two points of the classical text-type spectrum: the kośa proper and the *bhāṣya*. That the two largest indigenous dictionaries occupy *different* registers is itself a finding with practical force: "the indigenous tradition" is not one convention to add support for, but a register space — any data model, TEI customization, or corpus statistic that accommodates the SKD pattern must still be checked against the VCP pattern, and vice versa.

## 8. Limitations

1. **The *iti*-unit is an upper-bound proxy.** *iti* also closes grammatical and reported speech; the citation counts of §6 are register indicators, not adjudicated citation totals. A stratified ~100-unit SKD sample for citational-vs-grammatical adjudication is drawn but not yet human-reviewed ([`REVIEW_SKD_ITI_ADJUDICATION.html`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REVIEW_SKD_ITI_ADJUDICATION.html)); the 53.3 %/77.6 % fusion figures may sharpen once it is.
2. **The fusion threshold is documented, not calibrated.** "Authority-terminal" means at least 20 non-whitespace characters of definitional content precede the earliest authority match inside the unit (a definition ending in its citation); units below the threshold are classed separable. The threshold is a committed constant, and sensitivity to it has not been reported.
3. **The unit typology is machine-proposed.** The label vocabulary of [`R2_INDIGENOUS_ITI_AUTHORITY_LABELS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/R2_INDIGENOUS_ITI_AUTHORITY_LABELS.md) awaits scholar review and is used here only qualitatively.
4. **The register-separation chart is prototype-supported.** The H6 family review recommends source-reading any individual edge cited as an example; this paper cites only the family-level separation and the committed per-dictionary shares.
5. **VCP recovery is incomplete by construction.** The `…0` siglum convention means VCP citation density is underread by *iti*-counting alone; all VCP-vs-SKD register contrasts above are stated with that direction of error acknowledged (it strengthens, not weakens, the "zero means nothing" thesis).
6. **Edition and publication facts** (SKD publication run from 1822; VCP 1873–1884; the compilers' team structure) are stated from the standard references and flagged for verification against title pages before submission.
7. **Snapshot.** Counts are the 2026-06 snapshot (43 files); rank statements marked "of 44" follow the companion study's 2026-07 recomputation.

## 9. Conclusion

Measured with the corpus's European-keyed instruments, the *Śabdakalpadruma* and the *Vācaspatya* are the emptiest dictionaries in the CDSL corpus. Read with their own conventions, they are among its richest: a fixed-slot entry template continuous with the classical kośa; a printed front-matter codebook that decodes a systematic indicatory-letter slot — and states, in Sanskrit, its own theory of the meaningful zero; and a native microstructural unit, the *iti*-group, that fuses sense and citation in proportions governed by genre register rather than by dictionary identity. None of this required new philology to see; it required only refusing to read an instrument's zero as the object's emptiness.

The doctrine is portable. Every digitized multi-tradition corpus — Arabic *muǧannas* lexica with their *šawāhid*, Chinese *leishu*, Tibetan *brda-sprod* glossaries — will contain files that score zero on detectors built for another convention family. The kośa case supplies both the cautionary statistic (a dictionary that is simultaneously last and second in citation density, depending on the instrument) and the constructive method: treat the tradition's own apparatus — its front matter, its closure particles, its case conventions — as the schema, and build the parser to the schema. In a multi-convention corpus, a zero is a question about the instrument. The instrument, not the dictionary, is what the zero measures.

## References

Apresjan, Ju. D. (2000). *Systematic Lexicography*. Translated by K. Windle. Oxford: Oxford University Press.

Baalbaki, R. (2014). *The Arabic Lexicographical Tradition: From the 2nd/8th to the 12th/18th Century*. Handbook of Oriental Studies I/107. Leiden: Brill.

Böhtlingk, O. and Roth, R. (1855–1875). *Sanskrit-Wörterbuch*. 7 vols. St. Petersburg: Kaiserliche Akademie der Wissenschaften. [PWG]

Deva, Rādhākānta (1822–1858). *Śabdakalpadruma*. Calcutta. [SKD]

Monier-Williams, M. (1899). *A Sanskrit-English Dictionary*. Oxford: Clarendon Press. [MW]

Palsule, G. B. (1961). *The Sanskrit Dhātupāṭhas: A Critical Study*. Poona: University of Poona.

Stenzler, A. F. (1847). *De lexicographiae Sanscritae principiis*. Breslau. (Cited after Vogel 1979.)

Tarkavācaspati, Tārānātha (1873–1884). *Vācaspatya*. Calcutta. [VCP]

Tasovac, T. and Romary, L. (2018). *TEI Lex-0: A baseline encoding for lexicographic data*. DARIAH Working Group on Lexical Resources. https://dariah-eric.github.io/lexicalresources/pages/TEILex0/TEILex0.html

Vogel, C. (1979). *Indian Lexicography*. A History of Indian Literature V.4. Wiesbaden: Otto Harrassowitz.

Wiegand, H. E. (1989). Aspekte der Makrostruktur im allgemeinen einsprachigen Wörterbuch. In F. J. Hausmann et al. (eds), *Wörterbücher / Dictionaries / Dictionnaires*, Vol. 1. Berlin: de Gruyter.

Zachariae, Th. (1897). *Die indischen Wörterbücher (Kośa)*. Grundriss der indo-arischen Philologie I.3b. Strassburg: Trübner. (Cited after Vogel 1979.)

Zgusta, L. (1971). *Manual of Lexicography*. Prague: Academia / The Hague: Mouton.

Cologne Digital Sanskrit Dictionaries (CDSL). Cologne Sanskrit Lexicon project, U. of Cologne; source files https://github.com/sanskrit-lexicon/csl-orig (v02 snapshot used here).

**Companion papers (this series).**

Gasūns, M. (in preparation). Grammar without tags: the verbal-root microstructure of the indigenous Sanskrit kośa. [A04 — the *anubandha*/root-grammar layer: gaṇa/pada/transitivity decode and five-lexicon agreement.]

Gasūns, M. (in preparation). Condensation, not inflation: sense inheritance in the Sanskrit dictionary family. [A02 — sense units and the kośa-fusion dataset's inheritance analysis.]

Gasūns, M. (in preparation). Two citation registers: European source apparatus and indigenous *iti* quotation. [A08 — the corpus-wide citation-register census, including the SKD/VCP *iti* totals cited in §6.]

Gasūns, M. (in preparation). Cross-dictionary consistency of Pāṇinian derivation in ten Sanskrit dictionaries. [A35 — derivational affixes.]

**Coordinated sibling studies (shared SKD/VCP apparatus — one lead paper to be designated before submission).** This paper claims the record-level microstructure: the entry template (§4), the megastructure key as method (§5), the *iti*-unit and register contrast (§§6–7). The *anubandha*/root-grammar layer is A04's; derivational affixes are A35's; sense-inheritance consequences of the *iti*-unit are A02's; the corpus-wide citation-register census is A08's.

## To do before submission

- [ ] Verify SKD/VCP edition facts (publication years, volume structure, compiler teams) against title pages / Vogel §Śabdakalpadruma pages (limitation 6).
- [ ] Human adjudication of the ~100-unit SKD *iti* sample (shared gate with A02/A08); update §6 if the fusion figures move.
- [ ] Decide venue by deadline calendar: IJL vs WSC 2027 (roadmap Part IV Q1-2027 item) — and the A35↔A04↔A30 lead-paper designation (open `@DECIDE`).
- [ ] Wiegand megastructure reference: replace the survey-volume citation with the precise essay if §5's megastructure claim is kept in the submitted version.
- [ ] Optional: fusion-threshold sensitivity run (limitation 2) — one committed table, cheap insurance against a referee.

_Dr. Mārcis Gasūns_
