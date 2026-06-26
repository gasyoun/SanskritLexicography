# HeadwordLists — now vs then

Each `*-unique-key{1,2}-N.txt` is a snapshot whose filename count `N` is its line count at generation time ("then"). This compares each against the **current** csl-orig ("now"), regenerating the same field (`<k1>`/`<k2>`). Reproduce with [`headword_diff.py`](headword_diff.py); full word-level diffs land in `_diff/`.

- **comparable** — the committed list and the live field share key format, so `added`/`removed` are genuine headword changes.
- **format-migrated** — the committed `<k2>` snapshot is in the *legacy Cologne numeric transliteration* (`am2s4a` = aṃśa) while csl-orig is now SLP1; the raw diff is ~100 % and **not** a real headword change. Re-transcoding is needed to compare.
- **PD** has no csl-orig source locally.

| List | then | now | added | removed | overlap | verdict |
|---|--:|--:|--:|--:|--:|---|
| [AP-unique-key1-36030.txt](AP-unique-key1-36030.txt) | 36030 | 88701 | 53572 | 901 | 97.5% | comparable |
| [AP-unique-key2-36704.txt](AP-unique-key2-36704.txt) | 36126 | 88805 | 53606 | 927 | 97.4% | comparable |
| [BHS-unique-key2-17784.txt](BHS-unique-key2-17784.txt) | 17784 | 17810 | 17793 | 17767 | 0.1% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [BUR-unique-key2-19238.txt](BUR-unique-key2-19238.txt) | 19238 | 19598 | 19598 | 19238 | 0.0% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [CAE-unique-key2-39256.txt](CAE-unique-key2-39256.txt) | 39256 | 39296 | 35152 | 35112 | 10.6% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [CCS-unique-key2-29317.txt](CCS-unique-key2-29317.txt) | 29317 | 29474 | 28317 | 28160 | 3.9% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [GRA-unique-key1-10315.txt](GRA-unique-key1-10315.txt) | 10315 | 11108 | 975 | 182 | 98.2% | comparable |
| [GRA-unique-key2-10526.txt](GRA-unique-key2-10526.txt) | 10526 | 12481 | 12422 | 10467 | 0.6% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [INM-unique-key2-9466.txt](INM-unique-key2-9466.txt) | 9466 | 9919 | 8346 | 7893 | 16.6% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [MD-unique-key2-20748.txt](MD-unique-key2-20748.txt) | 20108 | 20243 | 19822 | 19687 | 2.1% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [MW-unique-key1-193978.txt](MW-unique-key1-193978.txt) | 193978 | 194084 | 753 | 647 | 99.7% | comparable |
| [MW-unique-key2-198220.txt](MW-unique-key2-198220.txt) | 198220 | 198489 | 110369 | 110100 | 44.5% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [MW-unique-key2-198231.txt](MW-unique-key2-198231.txt) | 198231 | 198489 | 110389 | 110131 | 44.4% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [PD-unique-key1-104936.txt](PD-unique-key1-104936.txt) | 104935 |  |  |  |  | no csl-orig source (PD not in csl-orig) |
| [PD-unique-key2-104941.txt](PD-unique-key2-104941.txt) | 104941 |  |  |  |  | no csl-orig source (PD not in csl-orig) |
| [PWG-unique-key1-106085.txt](PWG-unique-key1-106085.txt) | 106085 | 106083 | 148 | 150 | 99.9% | comparable |
| [PWG-unique-key2-110402.txt](PWG-unique-key2-110402.txt) | 110402 | 119109 | 115744 | 107037 | 3.0% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [PWK-unique-key1-131918.txt](PWK-unique-key1-131918.txt) | 131918 | 151349 | 19617 | 186 | 99.9% | comparable |
| [PWK-unique-key2-133741.txt](PWK-unique-key2-133741.txt) | 133741 | 167351 | 162388 | 128778 | 3.7% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [SCH-unique-key2-28495.txt](SCH-unique-key2-28495.txt) | 28495 | 29118 | 29118 | 28495 | 0.0% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [SKD-unique-key1-40551.txt](SKD-unique-key1-40551.txt) | 40551 | 40815 | 807 | 543 | 98.7% | comparable |
| [SKD-unique-key2-40595.txt](SKD-unique-key2-40595.txt) | 40595 | 42529 | 42529 | 40595 | 0.0% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [VCP-unique-key1-47107.txt](VCP-unique-key1-47107.txt) | 47107 | 48629 | 2515 | 993 | 97.9% | comparable |
| [VCP-unique-key2-47145.txt](VCP-unique-key2-47145.txt) | 47145 | 50135 | 50135 | 47145 | 0.0% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [VEI-unique-key1-3703.txt](VEI-unique-key1-3703.txt) | 3703 | 3704 | 18 | 17 | 99.5% | comparable |
| [VEI-unique-key2-3770.txt](VEI-unique-key2-3770.txt) | 3770 | 3722 | 3722 | 3770 | 0.0% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |

## Genuine changes (comparable lists)

For the comparable lists, `removed` headwords (present then, gone now — merged, corrected, or deleted) are the sharpest QA signal; `added` are new/expanded keys. Full lists in `_diff/<list>.added.txt` and `_diff/<list>.removed.txt`.

### AP-unique-key1-36030.txt — 36030 → 88701  (+53572 / −901)
removed (901): `ABAsu`, `ABogya`, `AJA`, `AJAnam`, `AJApaka`, `AJApanam`, `AJAtf`, `AJAyin`, `ANgAra`, `ASArikaH`, `ASImat`, `ASco`, `ASrukarRa`, `ASuman`, `AcCA`, `AcCodanama`, `Adda`, `AddaS`, `Addata`, `AddazwiH`, `Agamizwa`, `AgnIDpya`, `AgrahAyaRa`, `Agu`, `AjAnepya`, `AjiJAsenya`, `Ajura`, `AkA`, `AkAmakaH`, `AkAnta`, `AkAntiH`, `AkApya`, `AkI`, `AkIq`, `AkIqanam`, `AkIqin`, `Akam`, `AkamaH`, `Akand`, `AkandaH` … (full list in `_diff/`)

### AP-unique-key2-36704.txt — 36126 → 88805  (+53606 / −927)
removed (927): `ABAsu`, `ABogya`, `AJA`, `AJAnam`, `AJApaka`, `AJApanam`, `AJAtf`, `AJAyin`, `ANgAra`, `ASArikaH,`, `ASImat`, `ASco`, `ASrukarRa`, `ASuman`, `AcCA`, `AcCodanama`, `Adda`, `AddaS`, `Addata`, `AddazwiH`, `Agamizwa`, `AgnIDpya`, `AgrahAyaRa`, `Agu`, `AjAnepya`, `AjiJAsenya`, `Ajura`, `AkA`, `AkAmakaH`, `AkAnta`, `AkAntiH`, `AkApya`, `AkI`, `AkIq`, `AkIqanam`, `AkIqin`, `Akalpam`, `Akam`, `AkamaH,`, `Akand` … (full list in `_diff/`)

### GRA-unique-key1-10315.txt — 10315 → 11108  (+975 / −182)
removed (182): `ABias`, `ABis`, `AByAm`, `AByas`, `Are`, `AsAm`, `Asaam`, `Asu`, `AvfRaj`, `AyAjyu`, `BUriSfYga`, `BUrvakza`, `Bidat`, `BurisTAtra`, `DAmasaS`, `Dehi`, `Durv`, `Dya`, `Gus`, `SavisTa`, `Svapada`, `aBiBAnu`, `aBiSris`, `aBiSu`, `aBijnu`, `aBipra`, `aDakza`, `aDat`, `aQi`, `aSvesita`, `abdA`, `acfTita`, `aciSu`, `adabDanIti`, `aditI`, `ahamyu`, `ahiSusmasatvan`, `ajnAtayakzma`, `ajosa`, `akzIyamAna` … (full list in `_diff/`)

### MW-unique-key1-193978.txt — 193978 → 194084  (+753 / −647)
removed (647): `ASiraduG`, `AdipurAna`, `AmardakatirTanATa`, `AmiSraBUta`, `AmiSraBUtatva`, `AruRyopanIzad`, `Asanizu`, `AtreyA`, `AyAsadayin`, `BAravoDf`, `BOmasAnti`, `BUrI`, `BadraBadra`, `Batila`, `BavacCada`, `BerItAdaRa`, `BikzopaBegin`, `BinrArTa`, `BrAtfSvasura`, `BramaragIwawIkA`, `Buktotohizwa`, `Cagalapayas`, `CemuRA`, `CinnAbra`, `DArayitF`, `DAtakiKaRqa`, `DAtakizaRqa`, `DAtreyikAyI`, `DAtutaraMginI`, `DAvIyas`, `DanAyas`, `DananAsa`, `DarmasAstrin`, `DarminI`, `EndraniGanwu`, `GanadundBisvana`, `GrARacakzuS`, `GritAhuta`, `IdfSIdfktA`, `Ihatas` … (full list in `_diff/`)

### PWG-unique-key1-106085.txt — 106085 → 106083  (+148 / −150)
removed (150): `AKowSIrzaka`, `Abaradvasava`, `Acyadoha`, `AgNga`, `AjYApti`, `AjunAvaka`, `Anupak`, `AposUrti`, `AtIzadIya`, `BAdvAjI`, `BArikaM`, `BaganarAyaM`, `Baraqka`, `Batrya`, `BramarAmvAkzetra`, `Brazwraja`, `DUlikadamba`, `Danda`, `Dandeva`, `DmANK`, `EndravaruRa`, `GaRtodara`, `GanDakAlikA`, `GoYculikA`, `Japaketana`, `OkzRoniyAna`, `OtkaRQya`, `SAPakzi`, `Slizwakzepa`, `SudDAyu`, `SvaNge`, `UM~`, `aDihastyaM`, `aDyArUWa`, `aNolaka`, `aRvya`, `amarakaRwka`, `aniHzavya`, `antafAvedI`, `aparAHRaka` … (full list in `_diff/`)

### PWK-unique-key1-131918.txt — 131918 → 151349  (+19617 / −186)
removed (186): `Adityozwi`, `AgAmikaM`, `Amayintu`, `ArdrODAgni`, `AsyaMDaMya`, `AzwakIya`, `Bepura`, `BizaNnAtar`, `BlaS`, `CandasyaM`, `DarmameGaTyAna`, `Dfzwadmumna`, `GrAM~`, `Irkzya`, `Irmatas`, `KAditaMr`, `OpaSadf`, `SApAmvu`, `SavasOSInara`, `SilpojIvin`, `SirOpanizad`, `SitivAraM`, `SukamahimnaH`, `UM~`, `UrvazwIva`, `aByaNgaM`, `aDOpAsana`, `aSrutavarRa`, `aSvaprayatana`, `aYjanakoMSI`, `adadyaYc`, `adyAraBya`, `agnijvalitatevrana`, `ajyOzWineya`, `alaktaM`, `anugrahakat`, `anuzwupkArmIRa`, `apaScAdaTvan`, `appEdIkzita`, `arDANI` … (full list in `_diff/`)

### SKD-unique-key1-40551.txt — 40551 → 40815  (+807 / −543)
removed (543): `ASubrIhiH`, `AmkanditakaM`, `AnupUrbbI`, `ArawWajaH`, `AyurdruvyaM`, `BARqalaH`, `BAraziH`, `BImArjjunasahadevAstadanu`, `BUpitaH`, `BUtAra`, `BadrAdanI`, `BadrapaRIM`, `BakzyAlAyuH`, `BfYa`, `BogamUmiH`, `BramaracCalI`, `DUlIkadaKakaH`, `DvajItTAnaM`, `ESvayyakarmmA`, `GaMwwagA`, `Garvva`, `GawAlAyuH`, `GftabaraH`, `GrARatapaRaH`, `IkzyaM`, `Imme`, `IzyAluH`, `KadarikA`, `KaravallalikA`, `KemaRiH`, `PaParIkaH`, `Pakva`, `PalAWyA`, `PalaguvfntAkaH`, `PullAvallI`, `SAkunikah`, `SElamanDaM`, `SIrRANgriH`, `SIzaMGAtI`, `SUlagulmanASitvam` … (full list in `_diff/`)

### VCP-unique-key1-47107.txt — 47107 → 48629  (+2515 / −993)
removed (993): `ABAyya`, `ADamApana`, `ADaryya`, `ADidevika`, `AQApadi`, `AQhatama`, `ATarvaRRa`, `AcCIdana`, `AcCIwita`, `AgAragoGikA`, `AhIpuruzikA`, `Akroqa`, `AkzEtrajYya`, `AnandaBarava`, `AnandamayakIza`, `AndIlana`, `AnupUrbbI`, `ApImaya`, `Apavastra`, `Apayi`, `AtBahatyA`, `AtamasAkzin`, `Atiyigva`, `AtmanDin`, `Attagavva`, `AvarttaketuH`, `BAkzAwana`, `BArakara`, `BAs`, `BAvayat`, `BOjOya`, `BUpatra`, `BaYjaruM`, `Badaturaga`, `BadraTava`, `BadrasImA`, `BagIla`, `BatfsTAna`, `BavAdfkzaS`, `BavaketuH` … (full list in `_diff/`)

### VEI-unique-key1-3703.txt — 3703 → 3704  (+18 / −17)
removed: `SaNkuinTe`, `Salmall`, `SunaHpuCa`, `SunolAngUla`, `SvetaketuaruReya`, `aSvatTva`, `amAvAsyaSARdilyAyana`, `azAQOttarapArASarya`, `kArSkeyIputra`, `kanzya`, `kosa`, `kusurubindaOddalaki`, `nIeya`, `piakza`, `saMvartaAngirasa`, `skanDhyA`, `vAfzRivfdDa`
