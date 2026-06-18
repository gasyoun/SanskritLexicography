# aṃśa — corrected NWS sub-source parse (ground truth)

NWS "Kleines Zitat" format: `TAG > gloss … SOURCE:page >`.
The **diasystem tag precedes** the gloss; the **source citation CLOSES** the gloss (comes after it).
Proof: `áṃśa Gen, unsp > … a share of booty … MW:1 >` (English booty-gloss is Monier-Williams', cite after);
`… Antheil. Erbtheil. Partei … Graßmann 1873:1 >` (German gloss = Grassmann's, cite after).

The 2026-06-17 re-pass parsed it as `SOURCE > TAG > gloss`, shifting every owner by one and dropping
Grassmann's real gloss. Correct entry→owner mapping, in source order:

| # | TAG | gloss (head words) | TRUE owner (cite) |
|---|---|---|---|
| 1 | Gen, unsp | a share of booty; earnest money; a lot; denominator of a fraction; degree of lat/long | **MW : 1** |
| 2 | Ved, unsp | Antheil. Erbtheil. Partei. der viele Antheile besitzt oder zu vergeben hat. N e. der Aditisöhne | **Graßmann 1873 (1996) : 1** |
| 3 | Ved, unsp | Zugebrachtes, Anteil. ṚV III 45,4. Personifizierung (rāyó áṃśaḥ) … ṚV V 86,5 | **NṚV 1 : 3** |
| 4 | Ved, unsp | burden/load; sacks; good luck/lot/stake; Soma-juice; offering; relative/ally; milk; food; angle/ring; part + time-measure 11 19/31 min; property; base/descendant; reality; Sun-deity ṚV 2.1.4; ṛṣi ṚV 1.112.1; metrical sub-condition ṚVPrā 17.5 | **Vishva Bandhu 1972 : 1** |
| 5 | Ved, unsp | Anteil; share. Vermögen, Beute ṚV 7,32,12. Truppe, Partei ṚV 1,112,1. Aditisohn ṚV 2,1,4; Krick 1982 | **Rivelex (1) : 1** |
| 6 | aṃśa Gen, unsp | N de division. Renou 1997, S. 511 | **Renou 1997 : 940** |
| 7 | Ved, unsp | +āharate/+prāsyate "to draw lots" PVB XXI.1.2; +apaharate "tire au sort" Caland 1928 | **Renou 1934 : 173** |
| 8 | Ved, unsp | [aṃśena] partly (not wholly)… MaiSaṃ 3.8.4 | **Vishva Bandhu 1972 : 8** (s.v. aṃśena) |
| 9 | Śā, Astr, 10. Jhd. | a degree, the 360th part of a revolution. MSiddh 1.5 | **Sarma 1966 : 165** |
| 10 | Śā, Soc | zugewiesener Teil/Aufgabe, der Feind, den ein best. Held zu töten hat. (Meyer 1926 S.294) | **Meyer 1926 : 940** |
| 11 | Śā, Soc | share of an inheritance KA 3.5.13 [s. vibhāga]; share of return/profits KA 2.1.22 | **Olivelle 2015 : 1** |
| 12 | Śā, Math | part, numerator of a fraction; denominator marked with aṃśa; substitute for bhāga (degree) | **Keller 2006 : 198** |
| 13 | Śā, Med | (for aṃsa) shoulder; part, quantity; Adj mfn in comp. consisting of a part of | **Hoernle 1908 : 241** |
| 14 | Tan, unsp | part (idée de participation/affinité); avatāras = aṃśas of Puruṣa/Viṣṇu/Rudra. JayāSaṃ 4.11 | **TAK 1 : 73** |
| 15 | Buddh, unsp | (part, and so) "time"; maitra aṃśa "portion of affection" = love. Divyāv 60.24 | **BHSD : 1** |
| 16 | Epigr, unsp | a small territorial unit. EI Vol. XV S.297 | **Sircar 1966 : 18** |
| 17 | aṃśaka, Tan, unsp | = aṃśa (derived lemma) | **TAK 1 : 73** (s.v. aṃśa) |

Disambiguator = each scholar's specialty: Keller = Indian mathematics; Hoernle = Bower Ms (medical);
Olivelle = Kauṭilya Arthaśāstra (KA cites); TAK = Tāntrikābhidhānakośa; BHSD = Buddhist Hybrid Sanskrit;
Sircar = epigraphy (EI). Every one confirms the cite-closes-gloss reading.

→ Failure to log: **F12 — NWS "Kleines Zitat" off-by-one** (cite-after-gloss mis-read as cite-before-gloss),
plus the QA judge sharing the same blind spot and false-clearing it. Add a guard to 6_merged_translate.md.
