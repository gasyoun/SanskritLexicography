# Literature Index — repo relevance map

Each file tagged with the repos/projects it directly serves.
Repo codes: **MWS** · **AP90** · **GRA** · **PWG**/**PW** · **PWK** · **DCS**
(VisualDCS/corpus pipeline) · **csl-atlas** · **csl-websanlexicon** · **csl-orig** ·
**WhitneyRoots** · **RuTrans** (RussianTranslation mw\_ru + pwg\_ru) ·
**SaLex** (this repo — research papers P1–P6, roadmap) · **IndSch** (IndologyScholars)

**⚠ blocked** = the `.md` text can't currently be mined: either an un-OCR'd image PDF /
OCR-noise body (*needs OCR*), or a multi-paper bundle where the cited paper isn't isolated
(*re-extract*). Such a file can't yet serve its tagged repo until fixed. 5 files affected.

---

## Root level

| File | Author · Year | Repos | Primary use |
|---|---|---|---|
| [Apte-Composition1885.md](Apte-Composition1885.md) | V.S. Apte · 1885 | **AP90**, MWS, csl-atlas | Compound formation rules; cross-reference for AP90 `<comp>` markup and csl-atlas compound headword splitting |
| [Leitan_Sintaksis 20.2_11.09.2022.md](Leitan_Sintaksis%2020.2_11.09.2022.md) | Leitan · 2022 | **RuTrans**, SaLex | Modern Russian syntax reference for mw\_ru/pwg\_ru translation quality checks |
| [Speyer-Syntax1886.md](Speyer-Syntax1886.md) | J.S. Speyer · 1886 | **MWS**, **GRA**, SaLex | Sanskrit syntax citation source; `<ls>` link target ("Spe." abbreviation in MW/GRA entries); foundational for syntax annotation papers |
| [Tubb-ScholasticSans-2007.md](Tubb-ScholasticSans-2007.md) | Gary Tubb · 2007 | **MWS**, **RuTrans**, SaLex | Scholastic Sanskrit register decisions; markup choices for scholastic/kāvya vocabulary in MWS; cited in Renou nominal-style note. **RuTrans:** śāstric/bhāṣya register metalanguage — the five services of a commentary + glossing formulae (`iti`, `ity arthaḥ`, `iti yāvat`, `-ādi`, vigraha) for the pwg\_ru commentary layer; calibrates the Renou `bhāṣya` register tag and the translate/QA masking that preserves quoted commentarial Sanskrit untranslated |

---

## Lexicography-Manuals/

| File | Author · Year | Repos | Primary use |
|---|---|---|---|
| [#x98;The#x9C; Routledge handbook of semantics.md](Lexicography-Manuals/%23x98%3BThe%23x9C%3B%20Routledge%20handbook%20of%20semantics.md) | Nick Riemer · 2015 | **SaLex**, MWS | Semantic field theory for lexicography papers (P1/P2); MWS semantic domain markup |
| [A history of Indian literature_ Vol_ 5.md](Lexicography-Manuals/A%20history%20of%20Indian%20literature_%20Vol_%205.md) | Gonda & Vogel | **SaLex**, PWG, MWS | Indian lexicographical tradition background; historical framing for P5 paper |
| [Adapting_Standard_NLP_Tools_and_Resource.md](Lexicography-Manuals/Adapting_Standard_NLP_Tools_and_Resource.md) | Reiter, Hellwig et al. · 2010 | **DCS**, SaLex | NLP adaptation for Sanskrit ritual texts (LaTeCH 2010 workshop); information extraction and semantic annotation methods directly relevant to DCS text processing. **✓ fixed:** md sliced to the cited Reiter/Hellwig paper only (pp. 39–46), out of the full proceedings bundle |
| [Ancient Greek Scholarship.md](Lexicography-Manuals/Ancient%20Greek%20Scholarship.md) | Eleanor Dickey | **SaLex**, AP90, MWS | Comparative ancient lexicography method; parallel to Sanskrit scholastic tradition; P5 paper (comparative lexicography) |
| [Corpus Linguistics and Second Language Acquisition.md](Lexicography-Manuals/Corpus%20Linguistics%20and%20Second%20Language%20Acquisition.md) | Xiaofei Lu | **DCS**, RuTrans | Learner corpus methodology; second-language use of DCS data |
| [Corpus Linguistics and Statistics with R.md](Lexicography-Manuals/Corpus%20Linguistics%20and%20Statistics%20with%20R.md) | Guillaume Desagulier | **csl-observatory**, DCS | Statistical corpus methods (freq distributions, collocations) for observatory metrics and DCS analysis |
| [Corpus Linguistics for Education.md](Lexicography-Manuals/Corpus%20Linguistics%20for%20Education.md) | Pérez-Paredes | **DCS**, SaLex | Corpus pedagogy; framing DCS as teaching resource |
| [Corpus Linguistics for Vocabulary.md](Lexicography-Manuals/Corpus%20Linguistics%20for%20Vocabulary.md) | Paweł Szudarski | **DCS**, RuTrans | Vocabulary profiling methods; word frequency approaches for corpus\_lexicon |
| [Dictionary of lexicography.md](Lexicography-Manuals/Dictionary%20of%20lexicography.md) | Hartmann & James · 2002 | **SaLex**, MWS, AP90 | Standard terminology reference for all lexicography papers (P1–P6); definition of key terms |
| [Doing Linguistics with a Corpus.md](Lexicography-Manuals/Doing%20Linguistics%20with%20a%20Corpus.md) | Egbert, Larsson, Biber | **DCS**, csl-atlas | Corpus methodology; annotation methodology for DCS syntax evaluation |
| [Evaluating_Syntactic_Annotation_of_Ancie.md](Lexicography-Manuals/Evaluating_Syntactic_Annotation_of_Ancie.md) | Biagetti, Hellwig et al. · 2021 | **DCS**, csl-atlas | Inter-annotator agreement evaluation for the Vedic Treebank (UD scheme); direct benchmark methodology for DCS annotation quality and csl-atlas annotation standards |
| [Handbook of Corpus Linguistics.md](Lexicography-Manuals/Handbook%20of%20Corpus%20Linguistics.md) | John Ryan · 2019 | **DCS**, csl-observatory | General corpus reference; methods for observatory cross-repo statistics |
| [Hints to the Study of Sanskrit Compounds.md](Lexicography-Manuals/Hints%20to%20the%20Study%20of%20Sanskrit%20Compounds.md) | Rātānjanakar · 1896 | **AP90**, **MWS**, csl-atlas | Sanskrit compound analysis; headword splitting rules for csl-atlas; AP90 compound entry corrections. **⚠ blocked — needs re-OCR:** md body is Devanagari OCR noise, no clean extractable prose |
| [How to Use Corpora in Language Teaching.md](Lexicography-Manuals/How%20to%20Use%20Corpora%20in%20Language%20Teaching.md) | Sinclair | **DCS**, RuTrans | Corpus pedagogy; using DCS data for Sanskrit instruction |
| [internet lexicography.md](Lexicography-Manuals/internet%20lexicography.md) | Klosa-Kückelhaus · 2024 | **csl-websanlexicon**, MWS | Online dictionary design; UX and access patterns for the CDSL web interface |
| [Lexicography _ An Introduction.md](Lexicography-Manuals/Lexicography%20_%20An%20Introduction.md) | Howard Jackson · 2002 | **SaLex**, MWS, AP90 | Core lexicography primer; theoretical grounding for P1–P3 papers |
| [Lowe Participles in Rigvedic Sanskrit.md](Lexicography-Manuals/Lowe%20Participles%20in%20Rigvedic%20Sanskrit.md) | John Lowe | **GRA**, **WhitneyRoots**, csl-atlas | Rigvedic participial morphology; direct use for GRA participle markup and Whitney root class assignment |
| [Patterns_of_Exchange.md](Lexicography-Manuals/Patterns_of_Exchange.md) | Oliver Hellwig · 2010 | **DCS**, SaLex | Quantitative model for transcultural exchange in travel reports using digital text annotation (Hellwig = DCS creator); methodological bridge between corpus annotation and cultural analytics |
| [Performance_of_a_Lexical_and_POS_Tagger.md](Lexicography-Manuals/Performance_of_a_Lexical_and_POS_Tagger.md) | Jha et al. (eds.) · 2010 | **DCS**, csl-atlas | Proceedings of 4th International Sanskrit Computational Linguistics Symposium (JNU); covers morphological parsing, lexical resources, Pāṇinian formalisation, machine translation — broader than the filename suggests. **✓ fixed:** md sliced to the cited Hellwig "Performance of a Lexical and POS Tagger for Sanskrit" (pp. 162–172), out of the full ISCLS-4 volume |
| [Primary Education in Sanskrit.md](Lexicography-Manuals/Primary%20Education%20in%20Sanskrit.md) | Edwin Gerow | **SaLex**, AP90 | Sanskrit pedagogy; AP90 as pedagogical dictionary; learner's layer roadmap (Q4 2026) |
| [Programming for Corpus Linguistics with Python.md](Lexicography-Manuals/Programming%20for%20Corpus%20Linguistics%20with%20Python.md) | Daniel Keller · 2024 | **DCS**, csl-observatory, RuTrans | Python corpus pipeline patterns; methods for DCS statistical pipeline and pwg\_ru corpus gate |
| [StrategiesDoing Corpus Linguistics.md](Lexicography-Manuals/StrategiesDoing%20Corpus%20Linguistics.md) | — · 2024 | **DCS**, SaLex | Corpus study design; methodology reference for DCS-based papers |
| [Systematic Lexicography.md](Lexicography-Manuals/Systematic%20Lexicography.md) | Apresjan · 2008 | **RuTrans**, **SaLex**, **MWS** | Structured/systematic lexicography theory; primary theoretical grounding for P1 (evidence-graded entries); MWS entry structure; Russian sense-structure / lexical-function model behind [RussianTranslation/APRESJAN.md](../../RussianTranslation/APRESJAN.md) (pwg_ru register & sense-splitting decisions) |
| [The Arabic Lexicographical Tradition.md](Lexicography-Manuals/The%20Arabic%20Lexicographical%20Tradition.md) | Ramzi Baalbaki · 2014 | **SaLex** | Comparative ancient lexicography (Arabic vs Sanskrit traditions); P5 paper |
| [The Bloomsbury Companion to Lexicography.md](Lexicography-Manuals/The%20Bloomsbury%20Companion%20to%20Lexicography.md) | Howard Jackson · 2013 | **SaLex**, MWS | Survey reference covering all major lexicography subfields; P1–P6 background |
| [The encoding of ad hoc categories in Sanskrit.md](Lexicography-Manuals/The%20encoding%20of%20ad%20hoc%20categories%20in%20Sanskrit.md) | Inglese & Geupel · 2018 | **csl-atlas**, **MWS**, DCS | Semantic category encoding in Sanskrit grammar; direct relevance to csl-atlas markup decisions and MWS `<gram>` tagging |
| [The fundamental principles of corpus linguistics.md](Lexicography-Manuals/The%20fundamental%20principles%20of%20corpus%20linguistics.md) | McEnery & Brezina · 2022 | **DCS**, csl-observatory | Core corpus principles; methodology grounding for all DCS-based analysis |
| [The Gentle Art of Lexicography.md](Lexicography-Manuals/The%20Gentle%20Art%20of%20Lexicography.md) | Eric Partridge · 1963 | **SaLex** | Classic essay on lexicography craft; background reading for P1 framing |
| [The latin of roman lexicography.md](Lexicography-Manuals/The%20latin%20of%20roman%20lexicography.md) | Rolando Ferri | **SaLex** | Comparative ancient lexicography (Latin); P5 parallel |
| [The routledge handbook of applied linguistics.md](Lexicography-Manuals/The%20routledge%20handbook%20of%20applied%20linguistics.md) | Li Wei et al. · Vol 1 | **SaLex**, DCS | Applied linguistics survey; language documentation framing |
| [The Routledge Handbook of Applied Linguistics; Second.md](Lexicography-Manuals/The%20Routledge%20Handbook%20of%20Applied%20Linguistics%3B%20Second.md) | Li Wei et al. · 2024 | **SaLex**, DCS | Updated applied linguistics reference |
| [The Routledge Handbook of Corpus Linguistics.md](Lexicography-Manuals/The%20Routledge%20Handbook%20of%20Corpus%20Linguistics.md) | O'Keeffe & McCarthy · 2010 | **DCS**, csl-observatory | Standard corpus handbook; methodology backbone for DCS pipeline papers |
| [THE ROUTLEDGE HANDBOOK OF HISTORICAL LINGUISTICS.md](Lexicography-Manuals/THE%20ROUTLEDGE%20HANDBOOK%20OF%20HISTORICAL%20LINGUISTICS.md) | Bowern & Evans · 2014 | **GRA**, **SaLex** | Historical linguistics methods; Vedic/historical Sanskrit dimension of GRA and P4 paper |
| [The Routledge Handbook of Linguistics.md](Lexicography-Manuals/The%20Routledge%20Handbook%20of%20Linguistics.md) | Keith Allan · 2016 | **SaLex** | General linguistics reference; theoretical framing |
| [The Routledge Handbook of Second Language Acquisition.md](Lexicography-Manuals/The%20Routledge%20Handbook%20of%20Second%20Language%20Acquisition.md) | Wong & Barcroft · 2024 | **RuTrans**, DCS | SLA theory; use of corpus data in language acquisition |
| [The Routledge Handbook of Syntax.md](Lexicography-Manuals/The%20Routledge%20Handbook%20of%20Syntax.md) | Carnie, Siddiqi, Sato · 2014 | **SaLex**, DCS | Syntax theory survey; annotation framework for DCS UD and syntax papers |
| [The Routledge Handbook of Teaching English to Young Learners.md](Lexicography-Manuals/The%20Routledge%20Handbook%20of%20Teaching%20English%20to%20Young%20Learners.md) | Garton & Copland | *(background only)* | General applied linguistics; low direct relevance |

---

## Вспомогательное/ (Supporting materials)

| File | Author · Year | Repos | Primary use |
|---|---|---|---|
| [55.md](Вспомогательное/55.md) | O.V. Mitrenina · 2008 | RuTrans, SaLex | "Syntax of Correlative Constructions in Russian: A Generative Approach" (FDSL/LSA 2008); Russian correlatives from a generative perspective — companion to [mitrenina_fdsl.md](Вспомогательное/mitrenina_fdsl.md) |
| [Загадки_5.md](Вспомогательное/Загадки_5.md) | — | SaLex | Russian linguistic riddles / wordplay material; teaching material |
| [Якобсон Грамматический параллелизм 1987.md](Вспомогательное/Якобсон%20Грамматический%20параллелизм%201987.md) | Jakobson · 1987 | **SaLex** | Grammatical parallelism theory; poetic structure analysis for Sanskrit verse studies |
| [Apte-CompKey1923.md](Вспомогательное/Apte-CompKey1923.md) | V.S. Apte · 1923 | **AP90**, csl-orig | Apte compound key reference (1923 edition); direct use for AP90 correction cross-checking and csl-orig edits |
| [Correlatives Cross-Linguistically.md](Вспомогательное/Correlatives%20Cross-Linguistically.md) | — | **SaLex**, DCS | Correlative clause typology; syntax annotation reference for Sanskrit correlative constructions in DCS |
| [Gillon&Shaer-wildtrees.md](Вспомогательное/Gillon%26Shaer-wildtrees.md) | Gillon & Shaer | **SaLex** | Formal syntax (wild-tree structures); theoretical background for Sanskrit phrase-structure papers |
| [Gillon95-wordformation.md](Вспомогательное/Gillon95-wordformation.md) | Gillon · 1995 | **csl-atlas**, MWS | Sanskrit word formation analysis; headword segmentation and compound markup in csl-atlas |
| [Gillon96-wordorder.md](Вспомогательное/Gillon96-wordorder.md) | Gillon · 1996 | **SaLex**, DCS | Sanskrit word order; corpus word-order statistics from DCS |
| [Historical Syntax and Linguistic Theory.md](Вспомогательное/Historical%20Syntax%20and%20Linguistic%20Theory.md) | — | **SaLex**, GRA | Historical syntax methods; Vedic syntax dimension of GRA entries |
| [Kumar_Sanskrit_Syntax_1976.md](Вспомогательное/Kumar_Sanskrit_Syntax_1976.md) | Kumar · 1976 | **SaLex**, MWS | Sanskrit syntax reference; annotation decisions for MWS usage examples |
| [LSA08.md](Вспомогательное/LSA08.md) | Alice Davison · 2008 | **SaLex**, GRA | "Weak and Strong Correlatives" (LSA Jan 2008); Sanskrit/Hindi correlative clause typology vs European languages — direct reference for Sanskrit correlative syntax annotation and GRA entry interpretation |
| [Meenakshi-Syntax1983.md](Вспомогательное/Meenakshi-Syntax1983.md) | Meenakshi · 1983 | **SaLex**, MWS | Sanskrit syntax study; complements Speyer/Delbrück for MWS example annotation. **⚠ blocked — needs OCR:** md has no body (~222 chars, title block only) |
| [mitrenina_fdsl.md](Вспомогательное/mitrenina_fdsl.md) | Mitrenina (FDSL) | **RuTrans** | Russian formal syntax (FDSL conference); Russian grammatical terminology for mw\_ru/pwg\_ru translation |
| [Ruppel_Cambridge-Introduction-Sanskrit_2017_Correlative-Clauses.md](Вспомогательное/Ruppel_Cambridge-Introduction-Sanskrit_2017_Correlative-Clauses.md) | Ruppel · 2017 | **SaLex**, MWS | Ch. 23 of *Cambridge Introduction to Sanskrit* — relative and correlative clauses with classical examples; pedagogical grammar reference for MWS usage example annotation |
| [ZaliznjakPaducheva_Tipologija_otnositelnogo_predlozhenija 1975.md](Вспомогательное/ZaliznjakPaducheva_Tipologija_otnositelnogo_predlozhenija%201975.md) | Zaliznyak & Paducheva · 1975 | **SaLex**, RuTrans | Relative clause typology (Russian theoretical tradition); cross-linguistic syntax framework |

---

## На иностранных/ (Foreign language)

| File | Author · Year | Repos | Primary use |
|---|---|---|---|
| [Delbruck Altindische_Syntax 1888.md](На%20иностранных/Delbruck%20Altindische_Syntax%201888.md) | Berthold Delbrück · 1888 | **GRA**, **MWS**, **PWG** | *Altindische Syntax* — foundational Vedic syntax reference; `<ls>` link target for "Delb." citations in GRA/MW/PWG entries; essential for link-target work (DTB milestone) |
| [Renou-Histoire-de-La-Language-Sanskrite.md](На%20иностранных/Renou-Histoire-de-La-Language-Sanskrite.md) | Louis Renou | **RuTrans**, **SaLex**, MWS | Renou's Sanskrit language history; cited in multiple SaLex papers; Renou nominal-style study source; genre/register taxonomy behind the [RussianTranslation/RENOU*.md](../../RussianTranslation/RENOU.md) cluster and the pwg_ru corpus genre strata (`corpus_strata.json`) |
| [Speyer-Syntax1895.md](На%20иностранных/Speyer-Syntax1895.md) | J.S. Speyer · 1895 | **MWS**, **GRA** | *Vedische und Sanskrit-Syntax* (1895 German ed.); `<ls>` target for Speyer citations in MW/GRA; complements the 1886 English edition. **⚠ blocked — needs OCR:** md is an un-OCR'd image PDF (~215 chars, no body) |

---

## Общий синтаксис/ (General syntax)

| File | Author · Year | Repos | Primary use |
|---|---|---|---|
| [Ломов А.М. русский синтаксис в алфавитном порядке.md](Общий%20синтаксис/Ломов%20А.М.%20русский%20синтаксис%20в%20алфавитном%20порядке.md) | Lomov | **RuTrans** | Russian syntax reference dictionary (A–Z); terminology reference for mw\_ru/pwg\_ru translation |
| [Синтаксис современного русского языка словарь-справочник 2009.md](Общий%20синтаксис/Синтаксис%20современного%20русского%20языка%20словарь-справочник%202009.md) | — · 2009 | **RuTrans** | Modern Russian syntax handbook; target-language grammatical terminology for translation quality |
| [AEK_et_al_corrected_2020.md](Общий%20синтаксис/AEK_et_al_corrected_2020.md) | Kibrik et al. (23 authors) · 2020 | **SaLex**, RuTrans | *Введение в науку о языке* — comprehensive Russian university linguistics textbook (phonetics through computational linguistics); general methodology reference, not Sanskrit-specific |
| [Entsiklopedicheskiy_slovar_yunogo_filologa_Yazykoznanie 1984.md](Общий%20синтаксис/Entsiklopedicheskiy_slovar_yunogo_filologa_Yazykoznanie%201984.md) | — · 1984 | **SaLex**, RuTrans | Soviet linguistics encyclopedia for young philologists; terminological reference |
| [peshkovskii_am_russkii_sintaksis_v_nauchnom_osveshchenii.md](Общий%20синтаксис/peshkovskii_am_russkii_sintaksis_v_nauchnom_osveshchenii.md) | Peshkovsky | **RuTrans** | Classic Russian syntax (Peshkovsky) — foundational grammatical categories; used when translating Sanskrit syntactic constructions into Russian in mw\_ru |
| [testelets_iag_vvedenie_v_obshchii_sintaksis.md](Общий%20синтаксис/testelets_iag_vvedenie_v_obshchii_sintaksis.md) | Testelets | **RuTrans**, SaLex | Modern Russian general syntax textbook; Russian grammatical terminology; also typological framing for SaLex syntax papers |

---

## Reverse index — by repo

### MWS
Tubb-ScholasticSans-2007 · Speyer-Syntax1886 · Apte-Composition1885 · Dictionary of lexicography · Systematic Lexicography · Bloomsbury Companion · Lexicography: An Introduction · Hints to Sanskrit Compounds · internet lexicography · Encoding of ad hoc categories · Gillon95-wordformation · Kumar-Syntax1976 · Meenakshi-Syntax1983 · Speyer-Syntax1895 · Delbruck-Altindische-Syntax · Renou-Histoire

### AP90
Apte-Composition1885 · Apte-CompKey1923 · Hints to Sanskrit Compounds · Dictionary of lexicography · Lexicography: An Introduction · Primary Education in Sanskrit · Ancient Greek Scholarship

### GRA
Speyer-Syntax1886 · Speyer-Syntax1895 · Delbruck-Altindische-Syntax · Lowe-Participles · Historical Syntax · Routledge Handbook of Historical Linguistics · Davison-LSA08 (Sanskrit correlatives)

### PWG / PW
Delbruck-Altindische-Syntax · History of Indian Literature Vol 5

### DCS (VisualDCS / corpus pipeline)
Adapting Standard NLP Tools · Evaluating Syntactic Annotation · Performance of Lexical and POS Tagger (4th ISCLS) · Patterns of Exchange (Hellwig) · Corpus Linguistics + Statistics with R · Doing Linguistics with a Corpus · Handbook of Corpus Linguistics · Corpus Linguistics for Vocabulary · Corpus Linguistics for Education · Programming for Corpus Linguistics · StrategiesDoing Corpus Linguistics · Fundamental Principles · Routledge Handbook of Corpus Linguistics · Routledge Handbook of Syntax · Encoding of ad hoc categories · Gillon96-wordorder · Correlatives Cross-Linguistically

### csl-atlas
Adapting Standard NLP Tools · Apte-Composition1885 · Hints to Sanskrit Compounds · Gillon95-wordformation · Evaluating Syntactic Annotation · Doing Linguistics with a Corpus · Encoding of ad hoc categories · Lowe-Participles

### csl-websanlexicon
internet lexicography

### WhitneyRoots
Lowe-Participles

### RussianTranslation (mw\_ru / pwg\_ru)
Leitan-Sintaksis · Corpus Linguistics for Vocabulary · Corpus Linguistics + SLA · How to Use Corpora · Programming for Corpus Linguistics · Routledge Handbook of SLA · Peshkovsky · Lomov · Sintaksis-2009 · mitrenina-fdsl · Mitrenina-55 (Russian correlatives) · Zaliznyak-Paducheva · Testelets · Entsiklopedicheskiy-slovar · Kibrik-AEK-2020 · Systematic Lexicography (Apresjan) · Renou-Histoire · Tubb-ScholasticSans-2007 (bhāṣya register metalanguage)

### SanskritLexicography (papers P1–P6, roadmap)
Systematic Lexicography · Dictionary of lexicography · Bloomsbury Companion · Lexicography: An Introduction · Gentle Art of Lexicography · Arabic Lexicographical Tradition · Ancient Greek Scholarship · Latin of Roman Lexicography · History of Indian Literature · Routledge Handbook of Semantics · Routledge Handbook of Linguistics · Routledge Handbook of Historical Linguistics · Routledge Handbook of Syntax · Primary Education in Sanskrit · Jakobson-Parallelism · Gillon96-wordorder · Gillon-wildtrees · Historical Syntax · Kumar-Syntax · Meenakshi-Syntax · Ruppel-Correlatives (ch.23) · Correlatives-Cross-Linguistically · Davison-LSA08 · Zaliznyak-Paducheva · Renou-Histoire · Hellwig-Patterns-of-Exchange · Kibrik-AEK-2020 · Testelets · Adapting-NLP-Tools

---

*65 files · generated 2026-06-26*
