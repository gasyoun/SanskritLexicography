# HeadwordLists — now (2026) vs then (2014)

Each `*-unique-key{1,2}-N.txt` in [`then-2014/`](then-2014/) is a snapshot whose filename count `N` is its line count when extracted (first committed **2014-10-05**, "Cologne headwords"). This compares each against the **current** csl-orig ("now", 2026), regenerating the same field (`<k1>`/`<k2>`). The current key1 lists are written to [`now-2026/`](now-2026/). Reproduce with [`headword_diff.py`](headword_diff.py); full word-level diffs land in `_diff/`.

- **growth** = (now − then) / then. **overlap** = share of the *then* keys still present now.
- **comparable** — the committed list and the live field share key format, so `added`/`removed`/`growth` are genuine headword changes.
- **format-migrated** — the committed *2014* `<k2>` snapshot is in the *legacy Cologne numeric transliteration* (`am2s4a` = aṃśa) while csl-orig is now SLP1; the raw then-vs-now diff is ~100 % and **not** a real headword change. The current key2 has been re-extracted as clean SLP1 into [`now-2026/`](now-2026/), so it is usable directly even though it can't be line-diffed against the numeric 2014 file.
- **PD** is not in csl-orig, but its headword export lives in the sibling [`alternateheadwords`](https://github.com/sanskrit-lexicon/alternateheadwords) repo (`data/PD/PDhw0.txt`, 107,620 entries, `pageid:headword:start,end` per line) — compared here the same way as the csl-orig-backed dicts (H1365, 20-07-2026).

| List | then (2014) | now (2026) | added | removed | overlap | growth | verdict |
|---|--:|--:|--:|--:|--:|--:|---|
| [AP-unique-key1-36030.txt](then-2014/AP-unique-key1-36030.txt) | 36030 | 88869 | 53742 | 903 | 97.5% | +146.7% | comparable |
| [AP-unique-key2-36704.txt](then-2014/AP-unique-key2-36704.txt) | 36126 | 88829 | 56024 | 3321 | 90.8% | +145.9% | comparable |
| [BHS-unique-key2-17784.txt](then-2014/BHS-unique-key2-17784.txt) | 17784 | 18188 | 16457 | 16053 | 9.7% | +2.3% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [BUR-unique-key2-19238.txt](then-2014/BUR-unique-key2-19238.txt) | 19238 | 19251 | 297 | 284 | 98.5% | +0.1% | comparable |
| [CAE-unique-key2-39256.txt](then-2014/CAE-unique-key2-39256.txt) | 39256 | 39280 | 3000 | 2976 | 92.4% | +0.1% | comparable |
| [CCS-unique-key2-29317.txt](then-2014/CCS-unique-key2-29317.txt) | 29317 | 29233 | 3328 | 3412 | 88.4% | -0.3% | comparable |
| [GRA-unique-key1-10315.txt](then-2014/GRA-unique-key1-10315.txt) | 10315 | 11108 | 975 | 182 | 98.2% | +7.7% | comparable |
| [GRA-unique-key2-10526.txt](then-2014/GRA-unique-key2-10526.txt) | 10526 | 11453 | 10815 | 9888 | 6.1% | +8.8% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [INM-unique-key2-9466.txt](then-2014/INM-unique-key2-9466.txt) | 9466 | 9454 | 89 | 101 | 98.9% | -0.1% | comparable |
| [MD-unique-key2-20748.txt](then-2014/MD-unique-key2-20748.txt) | 20108 | 20107 | 44 | 45 | 99.8% | -0.0% | comparable |
| [MW-unique-key1-193978.txt](then-2014/MW-unique-key1-193978.txt) | 193978 | 194084 | 754 | 648 | 99.7% | +0.1% | comparable |
| [MW-unique-key2-198220.txt](then-2014/MW-unique-key2-198220.txt) | 198220 | 198489 | 110368 | 110099 | 44.5% | +0.1% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [MW-unique-key2-198231.txt](then-2014/MW-unique-key2-198231.txt) | 198231 | 198489 | 110388 | 110130 | 44.4% | +0.1% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [PD-unique-key1-104936.txt](then-2014/PD-unique-key1-104936.txt) | 104935 | 104938 | 118 | 115 | 99.9% | +0.0% | comparable |
| [PD-unique-key2-104941.txt](then-2014/PD-unique-key2-104941.txt) | 104941 | 104940 | 87 | 88 | 99.9% | -0.0% | comparable |
| [PWG-unique-key1-106085.txt](then-2014/PWG-unique-key1-106085.txt) | 106085 | 106082 | 149 | 152 | 99.9% | -0.0% | comparable |
| [PWG-unique-key2-110402.txt](then-2014/PWG-unique-key2-110402.txt) | 110402 | 110438 | 380 | 344 | 99.7% | +0.0% | comparable |
| [PWK-unique-key1-131918.txt](then-2014/PWK-unique-key1-131918.txt) | 131918 | 151349 | 19617 | 186 | 99.9% | +14.7% | comparable |
| [PWK-unique-key2-133741.txt](then-2014/PWK-unique-key2-133741.txt) | 133741 | 155688 | 23265 | 1318 | 99.0% | +16.4% | comparable |
| [SCH-unique-key2-28495.txt](then-2014/SCH-unique-key2-28495.txt) | 28495 | 28519 | 22979 | 22955 | 19.4% | +0.1% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| [SKD-unique-key1-40551.txt](then-2014/SKD-unique-key1-40551.txt) | 40551 | 40817 | 807 | 541 | 98.7% | +0.7% | comparable |
| [SKD-unique-key2-40595.txt](then-2014/SKD-unique-key2-40595.txt) | 40595 | 40817 | 2281 | 2059 | 94.9% | +0.5% | comparable |
| [VCP-unique-key1-47107.txt](then-2014/VCP-unique-key1-47107.txt) | 47107 | 48636 | 2514 | 985 | 97.9% | +3.2% | comparable |
| [VCP-unique-key2-47145.txt](then-2014/VCP-unique-key2-47145.txt) | 47145 | 48638 | 4360 | 2867 | 93.9% | +3.2% | comparable |
| [VEI-unique-key1-3703.txt](then-2014/VEI-unique-key1-3703.txt) | 3703 | 3704 | 18 | 17 | 99.5% | +0.0% | comparable |
| [VEI-unique-key2-3770.txt](then-2014/VEI-unique-key2-3770.txt) | 3770 | 3704 | 3703 | 3769 | 0.0% | -1.8% | format-migrated (legacy numeric → SLP1); raw diff not meaningful |
| **TOTAL (comparable, 20 lists)** | **1264957** | **1416262** | **171849** | **20544** | — | **+12.0%** | — |

_Grand total of all 26 snapshots' *then* line counts: **1721983**._

## Use cases

1. **Refresh the snapshots.** Several lists have drifted hard from the 2014 extraction (AP 36,030 → 88,867; PWK 131,918 → 151,349); the current key1 **and** key2 lists are in [`now-2026/`](now-2026/) (regenerate with `headword_diff.py now`).
2. **`removed` = a data-loss / correction audit.** Headwords present *then* and gone *now* are merges, corrections, or accidental deletions — review the `_diff/<list>.removed.txt` lists to catch anything dropped by mistake.
3. **Print-ready key2.** The 2014 key2 files are legacy numeric transliteration; `now-2026/` carries the **current key2 as clean SLP1** (the print/citation form — keeps `/` accent, `-`, `(...)`), ready for a printed headword list.
4. **Provenance / dictionary-growth tracking.** The then→now deltas record how each dictionary's headword count has evolved — useful for citation and for deciding which `csl-orig` dictionaries have changed enough to re-run downstream analyses (e.g. the Catalan/Huet coverage studies).

## Genuine changes (comparable lists)

For the comparable lists, `removed` headwords (present then, gone now — merged, corrected, or deleted) are the sharpest QA signal; `added` are new/expanded keys. Full lists in `_diff/<list>.added.txt` and `_diff/<list>.removed.txt`.

### AP-unique-key1-36030.txt — 36030 → 88869  (+53742 / −903)
removed (903): `ABAsu`, `ABogya`, `AJA`, `AJAnam`, `AJApaka`, `AJApanam`, `AJAtf`, `AJAyin`, `ANgAra`, `ASArikaH`, `ASImat`, `ASco`, `ASrukarRa`, `ASuman`, `AcCA`, `AcCodanama`, `Adda`, `AddaS`, `Addata`, `AddazwiH`, `Agamizwa`, `AgnIDpya`, `AgrahAyaRa`, `Agu`, `AjAnepya`, `AjiJAsenya`, `Ajura`, `AkA`, `AkAmakaH`, `AkAnta`, `AkAntiH`, `AkApya`, `AkI`, `AkIq`, `AkIqanam`, `AkIqin`, `Akam`, `AkamaH`, `Akand`, `AkandaH` … (full list in `_diff/`)

### AP-unique-key2-36704.txt — 36126 → 88829  (+56024 / −3321)
removed (3321): `A,`, `ABAsu`, `ABicaraRika,`, `ABirUpakam,`, `ABogya`, `ADitvam,`, `AGarzaH,`, `AGozaRam,`, `AJA`, `AJAnam`, `AJApaka`, `AJApanam`, `AJAtf`, `AJAyin`, `AKAtaH,`, `AKaH,`, `ANgAra`, `ANgUzaH,`, `AQakaH,`, `AQakika,`, `AQyaMBavizRu,`, `ASArikaH,`, `ASImat`, `ASaMsitf,`, `AScaryatA,`, `ASco`, `ASita,`, `ASramaH,`, `ASrukarRa`, `ASuman`, `ASutvam,`, `AYjalikyam,`, `AbanDaH,`, `AcAryatA,`, `AcCA`, `AcCedaH,`, `AcCodanama`, `AcaraRIya,`, `AdArin,`, `AdIpita,` … (full list in `_diff/`)

### BUR-unique-key2-19238.txt — 19238 → 19251  (+297 / −284)
removed (284): `*Bro`, `*Cz`, `*Garba`, `*Ix`, `*KuqM`, `*Kuqa`, `*Kurda`, `*Pall`, `*SaMl`, `*SraW`, `*bukv`, `*druk`, `*gO`, `*iNKa`, `*jark`, `*kalla`, `*kfN`, `*klfp`, `*krTa`, `*kraRW`, `*kuTa`, `*mUrCa`, `*murva`, `*nATa`, `*nahn`, `*naya`, `*nikza`, `*pala`, `*palla`, `*parRa`, `*picca`, `*sew`, `*vyaW`, `*yaNg`, `Akuta`, `ArDirzam`, `AsodAmi`, `AtyantikaM`, `Cfda`, `Crdi` … (full list in `_diff/`)

### CAE-unique-key2-39256.txt — 39256 → 39280  (+3000 / −2976)
removed (2976): `(Siti°pA/d)`, `(ala°jI)`, `(citra°SAlikA*)`, `(fti°zA/h)`, `(karke°taraka*)`, `(lajjApayi°tfka)`, `(na/+u)`, `(nf°zA/h)`, `(nirvARayi°tfka)`, `(nirvApayi°tfka*)`, `(niz°zA/h)`, `(sumf°QIka/)`, `(vajra°vA/h)`, `(vala°Bi)`, `(za/w°pAd)`, `(°pAd)`, `(°vA/h)`, `(°vallaki)`, `(°zA/c)`, `(°zA/h)`, `*BadraSI`, `*SIsaMjYa`, `*SIvezwa`, `*kiMqkirAta`, `*pattrANgu°lI`, `*sitApAnga`, `*°janman`, `*°ka`, `*°koSotTa`, `*°pawa*`, `1tva/`, `A &amp; I`, `A/Suta`, `A/Suti`, `A/jasvant`, `A/strfta`, `A/viTya`, `ABaraRasvAna`, `ABi°zecanika`, `ADi°dEvika` … (full list in `_diff/`)

### CCS-unique-key2-29317.txt — 29317 → 29233  (+3328 / −3412)
removed (3412): `(*BavAdfkza),`, `(kzipra/jYazu`, `(mfktika)`, `(sUnftAvan),`, `(sUvan),`, `*CandrasaMjYa`, `*draDIyaMs`, `*dvyahavfkta`, `*gamIn`, `*kzudraGARiwakA`, `*lUra`, `*mandaseDas`, `*paktrANga`, `*paktrANguli`, `*pratiserA`, `*takziRAhi`, `*tryahavfkta`, `*ulleca`, `A/YjunaganDi`, `ABimusvya`, `ADAwa/`, `ADyagni`, `ASiHkriya`, `ASrayaRa,`, `ASvana,`, `ATarvaRa/,`, `AYChu,`, `AcArya\`, `AcAryf`, `AcAryfaAcAryatA`, `AcAryfvant`, `AcisvyAsu`, `Agant/r`, `Agneya/,`, `AhAra,`, `AhvAnay,`, `AkalkANkzA`, `AkarRay,`, `AkarzaRa,`, `Akulay,` … (full list in `_diff/`)

### GRA-unique-key1-10315.txt — 10315 → 11108  (+975 / −182)
removed (182): `ABias`, `ABis`, `AByAm`, `AByas`, `Are`, `AsAm`, `Asaam`, `Asu`, `AvfRaj`, `AyAjyu`, `BUriSfYga`, `BUrvakza`, `Bidat`, `BurisTAtra`, `DAmasaS`, `Dehi`, `Durv`, `Dya`, `Gus`, `SavisTa`, `Svapada`, `aBiBAnu`, `aBiSris`, `aBiSu`, `aBijnu`, `aBipra`, `aDakza`, `aDat`, `aQi`, `aSvesita`, `abdA`, `acfTita`, `aciSu`, `adabDanIti`, `aditI`, `ahamyu`, `ahiSusmasatvan`, `ajnAtayakzma`, `ajosa`, `akzIyamAna` … (full list in `_diff/`)

### INM-unique-key2-9466.txt — 9466 → 9454  (+89 / −101)
removed (101): `AtiTi`, `BUrBuva`, `BuvaH`, `DArzWadyumna`, `DAtu`, `DarmAranya`, `Darmagupta`, `Darmavid`, `KaSira`, `Otanka`, `aDiraTi`, `aGaRwin`, `aSrama`, `aSramavAsa`, `aSvayuja`, `aTida`, `acAryamuKya`, `adityapaTa`, `adityaparvata`, `adityapratima`, `ahas`, `ahibraDna`, `ajagaraparvan`, `akfti`, `apagA`, `apagAsuta`, `apageya`, `apava`, `apta`, `araRyaka`, `araRyakaparvan`, `ardracarman`, `aruRi`, `aruja`, `arzwizeRa`, `asurAyaRi`, `atapana`, `avikzita`, `bAhudaNtaka`, `bahuvadyAH` … (full list in `_diff/`)

### MD-unique-key2-20748.txt — 20108 → 20107  (+44 / −45)
removed: `BAtvakzAs`, `Buraja`, `KA°`, `UM~`, `[Gu`, `[Kal`, `[Kaq`, `[Kar`, `[cap`, `[gaB`, `[jaMh`, `[kru`, `[kuB`, `[kuS`, `[kuq`, `[mU`, `[mUr`, `[maYj`, `[miS`, `[muj`, `[paYc`, `[paj`, `[piYj`, `[ruD`, `[ruh`, `[sTU`, `[stu`, `[vaja`, `[yah`, `aDarozWa,°rOzWa`, `akfcCriMn`, `atyuccrita`, `a°`, `dus°`, `duz°`, `dvi°`, `ko°`, `mOjAvata`, `niHka°`, `niHpa°`, `prOga`, `purOzRih`, `sutIkzaRa`, `uhya`, `uttarozWa,°rOzWa`

### MW-unique-key1-193978.txt — 193978 → 194084  (+754 / −648)
removed (648): `ASiraduG`, `AdipurAna`, `AmardakatirTanATa`, `AmiSraBUta`, `AmiSraBUtatva`, `AruRyopanIzad`, `Asanizu`, `AtreyA`, `AyAsadayin`, `BAravoDf`, `BOmasAnti`, `BUrI`, `BadraBadra`, `Batila`, `BavacCada`, `BerItAdaRa`, `BikzopaBegin`, `BinrArTa`, `BrAtfSvasura`, `BramaragIwawIkA`, `Buktotohizwa`, `Cagalapayas`, `CemuRA`, `CinnAbra`, `DArayitF`, `DAtakiKaRqa`, `DAtakizaRqa`, `DAtreyikAyI`, `DAtutaraMginI`, `DAvIyas`, `DanAyas`, `DananAsa`, `DarmasAstrin`, `DarminI`, `EndraniGanwu`, `GanadundBisvana`, `GrARacakzuS`, `GritAhuta`, `IdfSIdfktA`, `Ihatas` … (full list in `_diff/`)

### PD-unique-key1-104936.txt — 104935 → 104938  (+118 / −115)
removed (115): `aDOcCizwa`, `aDOpAsana`, `aDOpariguRita`, `aDOparyantam`, `aDaHSAKAcaturTAM~Sa`, `aDarmAM~Sa`, `aDarmAM~SodBava`, `aDikArasaMbavDin`, `aDikftvAA`, `aDizTAnajYAnavizayatA`, `aDomuKapuzpI`, `aDyAtmakXpti`, `aGorAcrana`, `aKiladfgdrazwwa`, `aMSkartftva`, `aMhaha`, `aNBAvapakza`, `aNGrayanta`, `aNGrikARQa`, `aNgIkftasantAnIcCeda`, `aNgaRadIrDikA`, `aNgajAnurAga`, `aNgamAwravizayatva`, `aNganibanDa`, `aNgatvADyAropa`, `aNgimAdtrAnuzWAna`, `aNgrakzayaMkara`, `aNguzWadErDya`, `aNkoWopuzpaka`, `aNkuritAjYjana`, `aNpavAda`, `aRqayoHstavDa`, `aRuvrtaparAyaRa`, `accahAyAnNa`, `acidBdeda`, `acikIrzatAsmikA`, `acintyAdButasrazwr`, `acintysSaktitA`, `acirasOraBasaRgatas`, `acirtratva` … (full list in `_diff/`)

### PD-unique-key2-104941.txt — 104941 → 104940  (+87 / −88)
removed (88): `aDOcCizwa`, `aDOpAsana`, `aDOpariguRita`, `aDOparyantam`, `aDaHSAKAcaturTAM~Sa`, `aDarmAM~Sa`, `aDarmAM~SodBava`, `aDikArasaMbavDin`, `aDikftvAA`, `aDizTAnajYAnavizayatA`, `aDyAtmakXpti`, `aGorAcrana`, `aKiladfgdrazwwa`, `aNBAvapakza`, `aNGrayanta`, `aNGrikARQa`, `aNgIkftasantAnIcCeda`, `aNgaRadIrDikA`, `aNgamAwravizayatva`, `aNgimAdtrAnuzWAna`, `aNgrakzayaMkara`, `aNguzWadErDya`, `aNkoWopuzpaka`, `aNkuritAjYjana`, `aNpavAda`, `aRqayoHstavDa`, `aRuvrtaparAyaRa`, `accahAyAnNa`, `acidBdeda`, `acikIrzatAsmikA`, `acintyAdButasrazwr`, `acintysSaktitA`, `acirasOraBasaRgatas`, `acirtratva`, `adfzwanASnASya`, `advEtabrahmadrSin`, `agnidibyaprayoga`, `ajagaravfttzAnta`, `akzatakrRI`, `akzavilasaQvfdDi` … (full list in `_diff/`)

### PWG-unique-key1-106085.txt — 106085 → 106082  (+149 / −152)
removed (152): `AKowSIrzaka`, `Abaradvasava`, `Acyadoha`, `AgNga`, `AjYApti`, `AjunAvaka`, `Anupak`, `AposUrti`, `AtIzadIya`, `BAdvAjI`, `BArikaM`, `BaganarAyaM`, `Baraqka`, `Batrya`, `BramarAmvAkzetra`, `Brazwraja`, `DUlikadamba`, `Danda`, `Dandeva`, `DmANK`, `EndravaruRa`, `GaRtodara`, `GanDakAlikA`, `GoYculikA`, `Japaketana`, `OkzRoniyAna`, `OtkaRQya`, `SAPakzi`, `SUrya`, `Slizwakzepa`, `SudDAyu`, `SvaNge`, `UM~`, `aDihastyaM`, `aDyArUWa`, `aNolaka`, `aRvya`, `amarakaRwka`, `aniHzavya`, `antafAvedI` … (full list in `_diff/`)

### PWG-unique-key2-110402.txt — 110402 → 110438  (+380 / −344)
removed (344): `A/junAvaka`, `AKowSIrzaka`, `AM/Sa`, `Abaradvasava`, `Acyadoha`, `AgNga`, `AjYApti`, `Anupa/k`, `AposUrti`, `AtIzadIya`, `AvidvaM/s`, `BAdvAjI`, `BArikaM`, `BUtAM/Sa`, `BaM/sas`, `BaganarAyaM`, `BakzivaM/s`, `Baraqka`, `Batrya`, `Bra/zwraja`, `BramarAmvAkzetra`, `DUlikadamba`, `Danda`, `Dandeva`, `DmANK`, `EndravaruRa`, `GaRtodara`, `GanDakAlikA`, `GoYculikA`, `Japaketana`, `OkzRoniyAna`, `OtkaRQya`, `SAM/Sapaka`, `SAPakzi`, `SU/rya`, `SaM/star`, `SaM/tanu`, `SityaM/sa`, `Slizwakzepa`, `SuSruvaM/s` … (full list in `_diff/`)

### PWK-unique-key1-131918.txt — 131918 → 151349  (+19617 / −186)
removed (186): `Adityozwi`, `AgAmikaM`, `Amayintu`, `ArdrODAgni`, `AsyaMDaMya`, `AzwakIya`, `Bepura`, `BizaNnAtar`, `BlaS`, `CandasyaM`, `DarmameGaTyAna`, `Dfzwadmumna`, `GrAM~`, `Irkzya`, `Irmatas`, `KAditaMr`, `OpaSadf`, `SApAmvu`, `SavasOSInara`, `SilpojIvin`, `SirOpanizad`, `SitivAraM`, `SukamahimnaH`, `UM~`, `UrvazwIva`, `aByaNgaM`, `aDOpAsana`, `aSrutavarRa`, `aSvaprayatana`, `aYjanakoMSI`, `adadyaYc`, `adyAraBya`, `agnijvalitatevrana`, `ajyOzWineya`, `alaktaM`, `anugrahakat`, `anuzwupkArmIRa`, `apaScAdaTvan`, `appEdIkzita`, `arDANI` … (full list in `_diff/`)

### PWK-unique-key2-133741.txt — 133741 → 155688  (+23265 / −1318)
removed (1318): `*AsyaMDaMya`, `*AzwakIya`, `*BizaNnAtar`, `*BlaS`, `*Irkzya`, `*aSvaprayatana`, `*aYjanakoMSI`, `*adadyaYc`, `*amAtAputra°`, `*anta[H]snehaPalA`, `*arGISi`, `*asTiSOTilya`, `*daDiTAKya`, `*dvyaNgula_utkarzam`, `*gardayitru`, `*gavyadaQa`, `*hananIya`, `*hayaSAla`, `*iwkara`, `*jaMpatI`, `*kAzWaDatrIPala`, `*kurarANGra`, `*lakac`, `*mahASutklA`, `*makat°`, `*mana_Apa`, `*mantUya`, `*nIv/`, `*niHzAmat`, `*pawwiloDna`, `*raTArBfka`, `*sarvasasya°`, `*suradIrDikA`, `*suralAsika`, `*tAqI`, `*tElaspanda`, `*tvaNnala`, `*tvaNnanya`, `*tvaNnaya`, `*vakraKaNga` … (full list in `_diff/`)

### SKD-unique-key1-40551.txt — 40551 → 40817  (+807 / −541)
removed (541): `ASubrIhiH`, `AmkanditakaM`, `AnupUrbbI`, `ArawWajaH`, `AyurdruvyaM`, `BARqalaH`, `BAraziH`, `BImArjjunasahadevAstadanu`, `BUpitaH`, `BUtAra`, `BadrAdanI`, `BadrapaRIM`, `BakzyAlAyuH`, `BfYa`, `BogamUmiH`, `BramaracCalI`, `DUlIkadaKakaH`, `DvajItTAnaM`, `ESvayyakarmmA`, `GaMwwagA`, `Garvva`, `GawAlAyuH`, `GftabaraH`, `GrARatapaRaH`, `IkzyaM`, `Imme`, `IzyAluH`, `KadarikA`, `KaravallalikA`, `KemaRiH`, `PaParIkaH`, `Pakva`, `PalAWyA`, `PalaguvfntAkaH`, `PullAvallI`, `SAkunikah`, `SElamanDaM`, `SIrRANgriH`, `SIzaMGAtI`, `SUlagulmanASitvam` … (full list in `_diff/`)

### SKD-unique-key2-40595.txt — 40595 → 40817  (+2281 / −2059)
removed (2059): `(Banja`, `AKuBuk [j] puM`, `AQ2akI`, `AQ2akInaH`, `AQ2akaH`, `AQ2akaM`, `AQ2akikaH`, `ASAQ2A`, `ASAQ2aH`, `ASitA [f] tri`, `ASubrIhiH`, `AhAryyaH puM`, `AkASajananI [n] puM`, `AkASarakzI [n] puM`, `AkrIq2aH`, `Akzoq2aH`, `AlIQ2aM`, `AlIQ2akaM`, `AmkanditakaM`, `Amreq2itaM`, `AnupUrbbI`, `ApIq2aH`, `ApaH [s] klI`, `Aq2UH`, `Aq2ambaraH`, `Aq2iH`, `ArUQ2aH`, `ArawWajaH`, `ArttavaH tri`, `AtmajanmA [n] puM`, `AyattiH: strI`, `AyurdruvyaM`, `AzAQ2A`, `AzAQ2ABUH`, `AzAQ2I`, `AzAQ2aBavaH`, `AzAQ2aH`, `AzAQ2akaH`, `BARqalaH`, `BArayaH puM` … (full list in `_diff/`)

### VCP-unique-key1-47107.txt — 47107 → 48636  (+2514 / −985)
removed (985): `ABAyya`, `ADamApana`, `ADaryya`, `ADidevika`, `AQApadi`, `AQhatama`, `ATarvaRRa`, `AcCIdana`, `AcCIwita`, `AgAragoGikA`, `AhIpuruzikA`, `Akroqa`, `AkzEtrajYya`, `AnandaBarava`, `AnandamayakIza`, `AndIlana`, `AnupUrbbI`, `ApImaya`, `Apavastra`, `Apayi`, `AtBahatyA`, `AtamasAkzin`, `Atiyigva`, `AtmanDin`, `Attagavva`, `AvarttaketuH`, `BAkzAwana`, `BArakara`, `BAs`, `BAvayat`, `BOjOya`, `BUpatra`, `BaYjaruM`, `Badaturaga`, `BadraTava`, `BadrasImA`, `BagIla`, `BatfsTAna`, `BavAdfkzaS`, `BavaketuH` … (full list in `_diff/`)

### VCP-unique-key2-47145.txt — 47145 → 48638  (+4360 / −2867)
removed (2867): `A(a)kOSala`, `A(a)kzEtrajYya`, `A(a)nESvaryya`, `A(a)nEpuRa`, `A(a)rdDakaMsika`, `ABAyya`, `ABIrapalli(llI)`, `ADamApana`, `ADaryya`, `ADidevika`, `ANguri(li)ka`, `AQ*hatama`, `AQApadi`, `ASA(qa)Q*a`, `ASAQ*A(qA)`, `ASco(Scyo)tana`, `ATarvaRRa`, `AcCIdana`, `AcCIwita`, `Adi(pu)pUruza`, `AgAragoGikA`, `Aga(gA)min`, `Agatya(mya)`, `AgrahAya(Ra)Rika`, `AhIpuruzikA`, `Ajanma(na)`, `AkarzA(zA)di`, `Akroq*a`, `AlAbu(bU)`, `AmAti(tI)sAra`, `AnandaBarava`, `AnandamayakIza`, `AndIlana`, `Antari(rI)kza`, `AnupUrbbI`, `ApImaya`, `Apavastra`, `Apayi`, `ArUQ*a`, `ArUQ*i` … (full list in `_diff/`)

### VEI-unique-key1-3703.txt — 3703 → 3704  (+18 / −17)
removed: `SaNkuinTe`, `Salmall`, `SunaHpuCa`, `SunolAngUla`, `SvetaketuaruReya`, `aSvatTva`, `amAvAsyaSARdilyAyana`, `azAQOttarapArASarya`, `kArSkeyIputra`, `kanzya`, `kosa`, `kusurubindaOddalaki`, `nIeya`, `piakza`, `saMvartaAngirasa`, `skanDhyA`, `vAfzRivfdDa`
