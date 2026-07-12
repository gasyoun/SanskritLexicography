# SIL semantic domains (semdom.org) ↔ Amarakosha varga crosswalk — scoping memo

_Created: 11-07-2026 · Last updated: 11-07-2026_

Scoping deliverable of
[H725](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H725-Fable_SanskritLexicography_semdom-kosha-crosswalk-scoping_11.07.26.md),
executing the MG ruling of 11-07-2026 recorded in
[SIL_MDF_ECOSYSTEM_CORRELATION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/SIL_MDF_ECOSYSTEM_CORRELATION.md)
§3 item 5 and §5 item 4. Researched and written by Fable 5 (`claude-fable-5`); web and
local prior-art sweeps run as two parallel subagents of the same session.

## Verdict: GO

A crosswalk between SIL's ~1,800 semantic domains and the Amarakosha varga structure is
**feasible with assets already in hand, novel in the literature, and licence-clean as an
ID-pair table**. Recommended build shape: a two-level crosswalk (varga→domain structural
map + a gold-standard synset-level pilot), bridged automatically through the existing
semdom↔WordNet mapping, human-verified. Build handoff:
[H742](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H742-Fable_SanskritLexicography_semdom-kosha-crosswalk-build_11.07.26.md)
(minted this pass); paper registered via `/articles-update`.

## 1. Novelty — confirmed

- **No semdom ↔ Sanskrit, semdom ↔ Amarakosha, or semdom ↔ any classical/historical
  thesaurus (Roget, Buck, Chinese leishu) mapping exists.** Targeted searches of the ACL
  Anthology, SIL publications, and the open web surfaced nothing. The claim in
  [SIL_MDF_ECOSYSTEM_CORRELATION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/SIL_MDF_ECOSYSTEM_CORRELATION.md)
  ("no Sanskrit exists in the SIL/MUDIDI semantic-domain world") stands after checking.
- **Nearest prior art, semdom side:** da Costa, Kratochvíl, Saad, Bond et al.,
  [Linking SIL Semantic Domains to Wordnet (GWC 2023)](https://aclanthology.org/2023.gwc-1.38/)
  with its released mapping
  [lmorgadodacosta/sil-semantic-domains-wordnet-mapping](https://github.com/lmorgadodacosta/sil-semantic-domains-wordnet-mapping)
  (CC BY-SA 4.0; ~75% of semdom classes matched to a Princeton WordNet/OMW synset), and the
  earlier [GWC 2014 linking paper](https://aclanthology.org/W14-0106.pdf). This is not
  competition — it is the **bridge** (see §3).
- **Nearest prior art, kosha side:** Nair & Kulkarni,
  [The Knowledge Structure in Amarakośa (2010)](https://sanskrit.uohyd.ac.in/scl/amarakosha/amarakosha_knowledge_structure.pdf)
  (UoHyd — synonymy/hypernymy/meronymy relations as a database, the upstream of our AMAR
  data); Bharati, Kulkarni & Nair,
  [Use of Amarakosha and Hindi WordNet in Building a Network of Sanskrit Words](https://www.semanticscholar.org/paper/Use-of-Amarakosa-and-Hindi-WordNet-in-Building-a-of-Bharati-Kulkarni/e9d31e03ffac1a6d42fc5026b83c0148453a014c);
  and IIT Bombay's Sanskrit WordNet (CFILT). All link Amarakosha to *WordNet-style*
  ontologies; none touch SIL's field-lexicography taxonomy.
- **Structural precedent inside SemDom itself:** each domain record already carries
  crosswalk hooks to two external taxonomies — `OcmCodes` (HRAF Outline of Cultural
  Materials) and `LouwNidaCodes` (Louw–Nida Greek NT domains). A varga code is a third
  such hook, methodologically identical — a strong "this is how SIL itself does it"
  argument for the paper.

## 2. Data-asset inventory

| Asset | Where | Structure | Size | Licence | Verified |
|---|---|---|---|---|---|
| SemDom canonical XML | [sillsdev/liblcm SemDom.xml](https://github.com/sillsdev/liblcm/blob/master/src/SIL.LCModel/Templates/SemDom.xml) | GUID + hierarchical code (1, 1.1, …) + name + description + elicitation questions + OcmCodes/LouwNidaCodes | **1,792 domains** (counted), 2.7 MB, English-only | data CC BY-SA 4.0 per [semdom.org](https://semdom.org); repo LGPL 2.1+ | fetched, element-counted |
| SemDom pre-parsed JSON | [sillsdev/LfMerge data/semantic-domains](https://github.com/sillsdev/LfMerge/tree/master/data/semantic-domains) (`semdom.json` + `parseme.py`) | same 1,792 domains as JSON | ~330 KB | repo MIT, data CC BY-SA 4.0 | fetched |
| SemDom localizations | [sillsdev/FwLocalizations](https://github.com/sillsdev/FwLocalizations) | `LocalizedLists-⟨lang⟩.xml`, 20 languages incl. **ru** and **hi** (completeness varies; ru has many empty slots) | — | LGPL 2.1+ | listing + ru header fetched |
| Amarakosha, CDSL org copy | [sanskrit-lexicon/AMAR amar.txt](https://github.com/sanskrit-lexicon/AMAR/blob/master/amar.txt) | `;v{}` varga markers, per-entry kāṇḍa+varga attribution, `eid` synonym sets with SLP1 lemmas + gender codes | **24 vargas, 5,590 synsets** (counted locally), 15,814 lines | GPL v3 (in-file), from UoHyd SCL (Sivaja Nair PhD database) | local file inspected |
| UoHyd SCL Amarakosha net | [sanskrit.uohyd.ac.in/scl/amarakosha](https://sanskrit.uohyd.ac.in/scl/amarakosha/index.html) | per-word synonyms/hypernyms/knowledge-net (richest relational layer) | — | GPL v2+ | fetched; consume via API per [REUSE_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/REUSE_INDEX.md), don't clone |
| semdom↔WordNet bridge | [lmorgadodacosta/sil-semantic-domains-wordnet-mapping](https://github.com/lmorgadodacosta/sil-semantic-domains-wordnet-mapping) | semdom code ↔ PWN offset/OMW | ~75% of domains matched | CC BY-SA 4.0 | fetched |
| Verse-keyed Amarakosha JSON (fallback) | [ashtadhyayi-com/data kosha/amara.json](https://github.com/ashtadhyayi-com/data/blob/master/kosha/amara.json) | one record per verse keyed `kanda.varga.verse`, Devanagari | — | **no licence file** — avoid as primary | fetched |
| Wider kosha corpus (extension) | [sanskrit-kosha/kosha](https://github.com/sanskrit-kosha/kosha) (Dhaval Patel) | dozens of koshas incl. AK commentaries, shared [annotation format](https://github.com/sanskrit-kosha/kosha/blob/master/docs/annotation_thoughts.md) | — | per-file | listing fetched |

What we do **not** have, checked this pass: no Amarakosha varga data in the
[kosha data-hub manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json)
(its `varga-series-diachrony` row is consonant-class phonetics, unrelated); the
csl-standards
[parse-skd-kosa.mjs](https://github.com/sanskrit-lexicon/csl-standards/blob/main/scripts/parse-skd-kosa.mjs)
pilot is 6 curated **Sabdakalpadruma** records (TEI-Lex0 format demo, not varga data).
The H137 caveat that AMAR "scores ~0 on prose-dictionary fingerprints by construction"
is a non-issue here — the crosswalk consumes exactly the verse-thesaurus structure that
made it an outlier there.

## 3. Method draft

**Unit of alignment — two levels:**

- **Level A (structural, the core deliverable):** varga → semdom domain(s), many-to-many,
  over the **~20 thematic vargas** (svarga, vyoma, dik, kāla, dhī, śabdādi, nāṭya,
  pātālabhogi, naraka, vāri, bhūmi, pura, śaila, vanauṣadhi, siṃhādi, manuṣya, brahma,
  kṣatriya, vaiśya, śūdra). The final 4 vargas (viśeṣyanighna = adjectives, saṅkīrṇa =
  miscellany, nānārtha = homonyms, avyaya = indeclinables) are **grammatical/structural,
  not semantic** — they are excluded from the domain crosswalk and that exclusion is
  itself a reportable finding (Amarakosha mixes semantic and grammatical organizing
  principles; SIL's taxonomy is purely semantic). Target granularity: semdom level 2–3
  (level 1 is only 9 headings — too coarse; level 4+ too fine for a 24-bucket source).
- **Level B (synset-level pilot, the evidence layer):** a stratified gold sample of AK
  `eid` synsets assigned to semdom **leaf** domains. Candidate assignments generated
  automatically: AK synset → English gloss (via MW, which cites AK 14,473 times per
  [ch05 of the book](https://github.com/gasyoun/Digital_Sanskrit_Lexicography-BOOK/blob/main/ch05_mw_block_economy.md),
  and/or the UoHyd knowledge net) → WordNet synset → the GWC-2023 semdom↔WordNet
  bridge → semdom code. Humans verify, never author from scratch.

**Gold sample size:** 200 synsets (~3.6% of 5,590), stratified ≥5 per thematic varga,
dual-annotated (two independent model annotators with distinct prompts, or model + MG
spot-check via `/review-sheet`), adjudicated; report Cohen's κ. 200 is enough for a
coverage estimate with ~±6% CI and matches the gold-sample sizes used in our csl-atlas
parse-rules evaluations.

**Measurable claims for the paper:**

1. **Coverage:** % of 1,792 semdom leaf domains with ≥1 AK synset; % of AK synsets
   assignable to any domain. Hypothesis: AK covers the human/ritual/natural-world
   subtrees densely and the modern-artifact subtrees not at all — the *shape* of the gap
   is a 6th-century-vs-modern taxonomy comparison no one has quantified.
2. **Structure agreement:** do vargas map to *contiguous* semdom subtrees (tree-alignment
   / adjusted Rand over the induced partitions), i.e. how far is a 1,500-year-old
   domain organization from a modern field-lexicography one?
3. **Bridge quality:** precision of the automatic WordNet-bridged candidates vs the
   human gold — reusable as a method result for other classical thesauri (Roget, leishu).

**What CDSL gains:** an `\sd` semantic-domain layer it currently lacks — emitted into the
MDF/LIFT exports of
[H721](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H721-Sonnet_csl-standards_mdf-spec-refine-lift-export_11.07.26.md)
(MDF §6.4 / App. C field), and a semantic-domain browse axis over MW/PWG via their AK
citations. Also instantly localizable UI labels: FwLocalizations ships domain names in
Russian and Hindi.

**Licensing route:** publish the crosswalk as an **ID-pair table** (semdom GUID/code ↔
varga ID ↔ AK synset `eid`), no copied prose from either side → CC BY-SA 4.0 (share-alike
required by the semdom side), citing AMAR (GPL v3) and UoHyd (GPL v2+) as sources.
Bundling UoHyd synonym *content* would pull the data release under GPL — keep content out
of the published table; register the table in the kosha data-hub manifest, public tier.

## 4. Effort estimate

- **Level A structural map:** S — one session (24 vargas × reading semdom level 2–3; the
  mapping is judgment, the tooling is trivial).
- **Level B pilot (bridge script + 200-synset gold + metrics):** M — 1–2 sessions; the
  bridge needs AK→English glosses, which MW's `AK.` citations and the UoHyd net both
  provide.
- **Paper draft to readiness 3:** M — one session on top of A+B. Venue shapes: GWC (the
  semdom↔WordNet lineage), ACL workshops (LT4HALA / LChange), or a DH venue; the SIL/MDF
  angle also fits *Dictionaria*/lexicography venues. Venue choice via `/venue-scout` at
  readiness 3.

Total to a submittable short paper: **~4 sessions**.

## 5. Risks / open points

- **Depth mismatch:** 24 vargas vs 1,792 domains means Level A alone is thin for a paper;
  the synset-level pilot (Level B) is what makes it publishable. Mitigated by the
  WordNet bridge doing the heavy candidate generation.
- **AMAR data quality:** the in-file licence says GPL v3 while the repo label says
  GPL-2.0 — for an ID-pair table this is moot, but any content redistribution needs the
  discrepancy resolved first (a human should decide only if content bundling ever becomes
  desirable; the recommended route avoids it).
- **English-only canonical SemDom:** glossing/judging runs through English domain names —
  fine for the method, but the ru localization being incomplete means no free Russian
  labels for every domain yet.
- **nānārtha varga** (homonyms) is excluded from Level A but is independently interesting
  (polysemy inventory); parked, not lost — noted in the build handoff.

## 6. Decision trail

- GO verdict per §1–§3: assets exist, novelty confirmed, licence route clean.
- Build handoff
  [H742](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H742-Fable_SanskritLexicography_semdom-kosha-crosswalk-build_11.07.26.md)
  minted this pass (Level A + Level B pilot + kosha-manifest registration).
- Paper registered in [ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)
  via `/articles-update` (readiness 1→2 once H736 lands data).
- Feeds [H721](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H721-Sonnet_csl-standards_mdf-spec-refine-lift-export_11.07.26.md)'s
  `\sd` field on delivery.

## 7. Results (H742 build, 11-07-2026, Fable 5 `claude-fable-5`)

The build landed same-day; full tables, method detail, and file inventory in
[data/SEMDOM_AK_CROSSWALK_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SEMDOM_AK_CROSSWALK_2026.md).
Headline numbers against §3's three measurable claims:

| Claim (§3) | Result |
|---|---|
| Coverage: AK synsets assignable | 5,391 / 5,590 (96.4%) got ≥1 candidate; **0 NONE votes** in the 200-synset gold — no SIL coverage hole for the sampled material |
| Coverage: semdom domains reached | 1,196 / 1,792 (66.7%) receive ≥1 candidate (noisy upper bound); 142 distinct domains in the gold |
| Structure agreement | 134 / 200 (67.0%) of gold leaf domains fall inside their varga's Level A subtree set |
| Bridge quality | top-1 17.5% exact / 27.5% level-2; gold-in-top-6 45.0% exact / 58.5% level-2 — a candidate generator, not a classifier |

Gold: 200 synsets, stratified ≥5 per thematic varga, dual-annotated blind
(Annotator A: Fable 5 `claude-fable-5`, Annotator B: Opus 4.8
`claude-opus-4-8`), exact κ **0.677**, level-2 κ **0.806**, 64 disagreements
adjudicated (60→A, 4→B, audit trail committed). §5's depth-mismatch risk
resolved in favour of publishability: the synset-level pilot produced usable
per-eid gold plus an honest negative result on the automatic bridge.

_Dr. Mārcis Gasūns_
