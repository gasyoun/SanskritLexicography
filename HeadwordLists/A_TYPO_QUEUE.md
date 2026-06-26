# Item A — MW + PWG typo queue (ready to file)

The **16** body-confirmed FILE-FIRST typos for the print spine (MW + PWG), consolidated from [SanskritSpellCheck](https://github.com/gasyoun/SanskritSpellCheck) (`corrections_draft/<DICT>/<DICT>_file_first_sf.txt`). Each was classified TYPO from the dictionary's **own entry text** and source-confirmed; the consonant-class flags (retroflex / sibilant / aspirate / b↔v) are the high-precision ones.

**To file:** verify each on the scan, then in the SanskritSpellCheck repo flip the trailing `n`→`y` in the `*_file_first_sf.txt` and run `python chg_nchg_sep.py <DICT>_file_first_sf.txt chg.txt nchg.txt` → file to [csl-corrections](https://github.com/sanskrit-lexicon/csl-corrections). Do **not** bulk-apply — these are individually confirmed.

| dict | wrong (SLP1) | wrong (IAST) | → right (SLP1) | right (IAST) | error type | evidence |
|---|---|---|---|---|---|---|
| MW | `kattfna` | kattṛna | `kattfRa` | kattṛṇa | dental→retroflex (n→ṇ) | `[dcs=3 ndicts=1 body=realword x2]` MW: kat—tfna  n. a fragrant grass, Suśr. \|\| Pistia Stratiotes, L. |
| MW | `Bawwaraka` | bhaṭṭaraka | `BawwAraka` | bhaṭṭāraka | vowel length (a↔ā) | `[dcs=3 ndicts=1 body=realword]` MW: Bawwaraka  mf(ikA)n. venerable, L. |
| MW | `akzAMsa` | akṣāṃsa | `akzAMSa` | akṣāṃśa | sibilant (s→ś) | `[dcs=0 ndicts=2 body=realword]` MW: akzAMsa  m. a degree of latitude. |
| MW | `prativoDavya` | prativodhavya | `prativoQavya` | prativoḍhavya | aspirate retroflex (dh→ḍh) | `[dcs=0 ndicts=1 body=realword]` MW: prati-˚voDavya  mfn. to be carried home, R. |
| PWG | `avakaSa` | avakaśa | `avakASa` | avakāśa | vowel length (a↔ā) | `[dcs=4 ndicts=1 body=realword]` PWG: {#avakaSa#} {%das Herableuchten%}: {#nakzatrARAmavakASena puRqarIkaM jAyate#} PAÑCAV. BR. 18,9,6. — 2) {#(anayoH stanayoH) avakASo na paryAptastava bAhulat |
| PWG | `tarAvalI` | tarāvalī | `tArAvalI` | tārāvalī | vowel length (a↔ā) | `[dcs=2 ndicts=1 body=realword]` PWG: {#tarAvalI#}  1) {%eine Menge von Sternen%} KATHĀS. 73,340. — 2) {%eine best. rhetorische Figur%}: {#tArARAM saMKyayA padyEryuktA tArAvalI matA#} PRATĀPAR. |
| PWG | `dIvAkIrtya` | dīvākīrtya | `divAkIrtya` | divākīrtya | vowel length (i↔ī) | `[dcs=2 ndicts=1 body=realword]` PWG: {#dIvAkI/rtya#} ({#divA + kI˚#})  1) adj. {%was bei Tage herzusagen, auszusprechen ist%}; n. Bez. {%bestimmter Recitationen%} oder {%Gesänge%}: {#divAkIrty |
| PWG | `yajYamus` | yajñamus | `yajYamuz` | yajñamuṣ | sibilant (s→ṣ) | `[dcs=2 ndicts=1 body=realword]` PWG: {#yajYamu/s#} ({#yajYa#} + 2. {#muz#}) adj. {%das Opfer raubend%}; m. {%ein dem Opfer nachstellender Dämon%} TS. 3,5,4,1. KĀṬH. 32,6. MBH. 3,14165. fg. VAR |
| PWG | `tfzitottara` | tṛṣitottara | `tfzitottarA` | tṛṣitottarā | vowel length (a↔ā) | `[dcs=0 ndicts=1 body=realword]` PWG: {#tfzitottara#} ({#tfzita#} n. + {#uttara#} 4, {%e%}) f. N. einer Pflanze ({#aSanaparRI#}) ŚABDAC. im ŚKDR. |
| PWG | `paRavanDa` | paṇavandha | `paRabanDa` | paṇabandha | b↔v | `[dcs=0 ndicts=1 body=realword]` PWG: {#paRavanDa#} ({#paRa + ba˚#}) m. {%das Abschliessen eines Vertrags%} RAGH. 8,21. 10,87. Schol. zu P. 3,4,8. 6,2,154. |
| PWG | `BAvavanDana` | bhāvavandhana | `BAvabanDana` | bhāvabandhana | b↔v | `[dcs=0 ndicts=1 body=realword]` PWG: {#BAvavanDana#} ({#BAva + ba˚#}) adj. {%die Herzen verbindend%}: {#preman#} RAGH. 3,24. |
| PWG | `Dabalapakza` | dhabalapakṣa | `Davalapakza` | dhavalapakṣa | b↔v | `[dcs=0 ndicts=1 body=realword]` PWG: {#Dabalapakza#} ({#Da˚ + pakza#}) m. {%Gans%} RĀJAN. im ŚKDR. — Nach ŚKDR. und WILS. auch {%die lichte Hälfte eines Mondmonats, die Zeit des zunehmenden Mo |
| PWG | `duzwu` | duṣṭu | `duzWu` | duṣṭhu | aspiration (ṭ→ṭh) | `[dcs=1 ndicts=2 body=realword]` PWG: {#duzwu/#} (2. {#duz + sTu#} von {#sTA#}) UṆĀDIS. 1,26. gaṇa {#udgAtrAdi#} zu P. 5,1,129. adj. {%sich schlecht betragend%} UJJVAL. adv. einen {%Tadel%} bez |
| PWG | `arTavanDa` | arthavandha | `arTabanDa` | arthabandha | b↔v | `[dcs=0 ndicts=1 body=realword]` PWG: {#arTavanDa#}, {#lalitArTabanDaM pattre niveSitamudAharaRaM priyAyAH#} VIKR. 32. |
| PWG | `pfzwavanDu` | pṛṣṭavandhu | `pfzwabanDu` | pṛṣṭabandhu | b↔v | `[dcs=0 ndicts=1 body=realword]` PWG: {#pfzwavanDu#} vielleicht {%der seine Sippe aufgesucht hat, Gast seiner Verwandtschaft%}; vgl. {#banDupfcC#} . |
| PWG | `biBedayisu` | bibhedayisu | `biBedayizu` | bibhedayiṣu | sibilant (s→ṣ) | `[dcs=0 ndicts=1 body=realword]` PWG: {#biBedayisu#} (vom desid. des caus. von {#Bid)#} adj. {%zu entzweien beabsichtigend%} MBH. 5,5822. |

_MW: 4 · PWG: 12 · total 16. Source-of-truth + filing workflow live in SanskritSpellCheck; this is the print-readiness (item A) consolidated view._
