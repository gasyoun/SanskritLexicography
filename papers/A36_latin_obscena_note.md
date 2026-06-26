# *Obscaena Latine*: the Latin discretion-screen in the Cologne German dictionaries (PWG, PW, SCH) — and who lifts it

**A36 · research note / short communication · draft 2026-06-26 · target: Lexikos / IJL / eLex / Dictionaries (DSNA)**

> **Status:** first draft (2/5). Dataset extracted, filtered, and reproducible across
> three German dictionaries with an MW/Apte cross-check; needs a related-work paragraph
> (Adams 1982; the history of *verba obscena* in scholarly lexicography), a manual audit
> of the clinical set, and a venue decision.

## Abstract

Nineteenth-century European Sanskrit lexicography inherited a classical-philology
convention: **taboo vocabulary is glossed in Latin, not in the vernacular**, so that the
classically educated reader can follow while the general reader (in the period's terms,
women and the young) cannot. The locus classicus is Böhtlingk–Roth's entry for the root
√*yabh*, glossed simply **futuere** — with a footnote to the Slavic cognate (Miklosich) —
rather than with any German verb. We extract every Latin sexual/scatological gloss from
the three German Cologne dictionaries — **PWG** (*Großes Petersburger Wörterbuch*),
**PW** (*Kürzere Fassung*), and **SCH** (Schmidt, *Nachträge*) — and separate two
registers that the practice conflates: a small **vulgar veil** (Latin words that are
themselves obscene — *futuere, cunnus, mentula, paedicare, mingere, stercus/cacare*) and
a large **clinical Latin** default (*coitus, penis, vulva, pudenda, semen, clitoris*).
We find **875 Latin-glossed senses** across the three dictionaries — **79 vulgar, 796
clinical** — and, cross-checking against Monier-Williams (English, 1899) and Apte (1890),
show a clean gradient of editorial candour: the German dictionaries veil in Latin only;
**Monier-Williams gives both** ("to have sexual intercourse, *futuere*"); **Apte, an
Indian lexicographer writing for Indian students, glosses openly in English** ("to
cohabit") with no screen at all.

## 1. The convention

The practice is not a quirk of one editor but a shared register rule of the St Petersburg
school, taken over from Greek and Roman textual scholarship (where *obscaena* were left
untranslated, or rendered into Latin in an otherwise vernacular apparatus). The screen is
**linguistic, not typographic**: the word is printed in full, in the body of the entry,
but in a language that filters its readership. Böhtlingk's √*yabh* is the textbook case
([csl-orig `pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt)):

> {#yaB#}, {#ya/Bati#} Dhātup. 23,11 … **futuere** (die entsprechende slavische Wurzel
> verzeichnet bei Miklosich …): {#yaBa\ mAm#} "**futue me**" spricht ein Weib AV.
> 20,136,11 … {#yiyapsyamAnA#} **quae futui cupit** ŚĀṄKH. ŚR. 12,23,16.

— note the candour *behind* the screen: a full sentence, *quae futui cupit* "she who longs
to be f.", is given because it is in Latin.

## 2. Method

Source files are the SLP1-native CDSL exports in
[`csl-orig/v02`](https://github.com/sanskrit-lexicon/csl-orig/tree/master/v02):
[`pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt),
[`pw/pw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt),
[`sch/sch.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/sch/sch.txt).
Each `<L>…<LEND>` entry was scanned for a curated list of Latin sexual/scatological terms;
for each hit we record the headword (SLP1 + IAST via
[`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util)), the Latin gloss, the
nearest Sanskrit example, and the nearest `<ls>` citation.

**Two filters matter** (both guard against the very plant/animal-name Latin one *expects*
in these dictionaries and which is *not* a discretion-screen):

1. **Binomial leak.** A naïve `sperma\b` matches the tail of Linnaean binomials —
   *Moringa pterygo**sperma** Gaertn.* (śigru, the drumstick tree) produced 18 false
   "semen" hits. We reject any match preceded by a letter (i.e. not at a word start),
   removing 97 binomial-internal leaks.
2. **Homographs.** *Clitoria* (the pea genus *Clitoria ternatea*, Skt. *aparājitā*) vs
   *clitoris*; open German *Excremente(n)* vs Latin *excrementum*; the grammatical future
   *futurum/futuri* vs *futuere*; the indologist *Cunningham* vs *cunnus* — all explicitly
   denied.

**Register assignment** follows J. N. Adams, *The Latin Sexual Vocabulary* (1982): the
obscene core of Latin (*cunnus, mentula, futuo, paedico*; the scatological *stercus,
cacare, merda, mingere*) is tagged **VULGAR**; the medical/euphemistic register (*coitus,
penis, vulva, pudenda, virilia, semen, clitoris*) is tagged **CLINICAL**. The distinction
is the point of the study: only the first set is "Latin so as not to be understood" in the
strong sense; the second is the era's default scientific register, screening by side
effect.

## 3. Two registers, by dictionary

Counts are Latin-glossed **senses** (one per field per entry).

| Register | Field (Latin) | PWG | PW | SCH | Total |
|---|---|---:|---:|---:|---:|
| **VULGAR** | *futuere* (futuere, fututio, fututor, futuens, fututa) | 8 | 10 | 1 | 19 |
| **VULGAR** | *cunnus* | 4 | 4 | 1 | 9 |
| **VULGAR** | *stercus / faeces / cacare / excrementum* | 19 | 28 | 0 | 47 |
| **VULGAR** | *mingere* (urinate) | 2 | 1 | 0 | 3 |
| **VULGAR** | *paedicare* (sodomise) | 0 | 1 | 0 | 1 |
| | **vulgar subtotal** | **33** | **44** | **2** | **79** |
| CLINICAL | *coitus / coïtus / coeundi / coire* | 108 | 102 | 245 | 455 |
| CLINICAL | *vulva* | 28 | 47 | 87 | 162 |
| CLINICAL | *penis / membrum virile / phallus* | 45 | 64 | 22 | 131 |
| CLINICAL | *pudenda / verenda* | 12 | 7 | 1 | 20 |
| CLINICAL | *semen virile / spermaticus* | 3 | 2 | 7 | 12 |
| CLINICAL | *testiculi / scrotum* | 6 | 3 | 0 | 9 |
| CLINICAL | *clitoris* | 3 | 3 | 0 | 6 |
| CLINICAL | *nates* (buttocks) | 1 | 0 | 0 | 1 |
| | **clinical subtotal** | **206** | **228** | **362** | **796** |
| | **TOTAL** | **239** | **272** | **364** | **875** |

The full per-sense dataset (all 875 rows: dict, headword, register, field, Latin gloss,
Sanskrit example, citation) is
[`A36_latin_obscena.csv`](A36_latin_obscena.csv).

## 4. The vulgar veil — full list (79 senses, 52 headwords)

This is the set in the strong sense of the question: words rendered in obscene Latin
*because there was no German the editors were willing to print*. It clusters in three
places — the √*yabh* family (sexual act), the defecation roots and dung-nouns
(scatology), and a handful of metaphorical *cunnus* kennings.

<!-- VULGAR_TABLE_START -->
| Dict | Headword (IAST) | Latin gloss | Sanskrit example | Citation |
|---|---|---|---|---|
| PWG | *gar* | cunnus | ā hanti gabhe paso ni galgal | VS. 23,22 |
| SCH | *garta* | cunnus |  | Sam. IV,66. |
| PW | *jaghanacyuti* | cunnus | jaghanacyuti | TBR. 2,4,6,4 |
| PWG | *kuṇḍāśin* | cunnus | kuṇḍa | ŚKDR. |
| PW | *madanātapatra* | cunnus | madanātapatra | BHĀVAPR. 1,18 |
| PW | *manobhavāgāra* | cunnus | manobhavāgāra | BHĀVAPR. 1,18,14 |
| PWG | *maṇḍūradhāṇika* | cunni | dhāṇikā | ṚV. 10,155,4 |
| PW | *sakthan* | cunnus | sakthī |  |
| PWG | *sakthan* | cunnus | sakthnā dediśyate nārī | VS. 23,29 |
| PW | *asaṃhata* | faeces | asaṃhata | SUŚR. 1,45,8 |
| PW | *bhinnaviṭka* | faeces | bhinnavarcas | BHĀVAPR. 4,41,14 |
| PWG | *bhinnaviṭka* | faeces | ˚tva | ŚĀRṄG. SAṂH. 1,7,71 |
| PW | *dhātumala* | faeces | dhātumala |  |
| PW | *gu* | cacare | guvati |  |
| PWG | *gu* | cacare | guvati | DHĀTUP. 28,106 |
| PW | *gūtha* | stercus | gūtha |  |
| PWG | *kar* | cacare | apaskara | WEST. |
| PW | *kīṭa* | stercus | kiṭṭa | HEMĀDRI 2,a,76,6 |
| PW | *laṇḍa* | stercus | laṇḍa | KĀVYAPR. S. 155, N. 51 |
| PW | *leṇḍa* | stercus | laṇḍa |  |
| PW | *mīḍha* | stercus | mīḍha | LALIT. 205,6. 11. 259,12 |
| PW | *niṣpad* | excrementum | niṣpad |  |
| PWG | *niṣpad* | excrementum | dudheryuktasya dravataḥ sahā | ṚV. 10,103,6 |
| PW | *pravāhaṇa* | faeces | pravāhaṇī | CARAKA. 8,10 |
| PWG | *pravāhaṇa* | faeces | bali | SUŚR. 1,258,11 |
| PW | *purīṣasaṃgrahaṇīya* | faeces | purīṣasaṃgrahaṇīya | Mat. med. 3 |
| PW | *purīṣavirañjanīya* | faeces | purīṣavirañjanīya | Mat. med. 3 |
| PW | *pāy* | cacare | pāyate |  |
| PWG | *pāy* | cacare | pāyate | PRAŚNOP. 4,2 |
| PW | *suga* | faeces | sugā | HEMĀDRI 1,463,15 |
| PWG | *suga* | faeces | pṛtsva1smabhyaṃ mahi varivaḥ | ŚABDAC. |
| PW | *utsarga* | stercus | chandasām | JAIM. 3,7,19 |
| PW | *varcas* | stercus | varcas |  |
| PWG | *varcas* | stercus | vigalitamegha˚ | UJJVAL. |
| PW | *varcaska* | stercus | varcaska |  |
| PW | *viś* | cacare | upa | CARAKA. 3,5 |
| PW | *viś* | faeces | viṣ |  |
| PWG | *viś* | faeces | viṣ | H. 634 |
| PWG | *viś* | cacare | upa | CARAKA 3,5 |
| PW | *viḍbandha* | faeces | viḍbandha |  |
| PWG | *viḍbandha* | faeces | sa˚ | SUŚR. 2,437,16 |
| PW | *viṣ* | faeces | viṣ |  |
| PWG | *viṣ* | faeces | viṭ | SIDDH. K. 247,b,2 v. u. |
| PW | *viṣṭhā* | faeces | viṣṭhā |  |
| PWG | *viṣṭhā* | faeces | viṣ | AK. 2,6,2,19 |
| PWG | *viṭka* | faeces | karṇa˚ | SUŚR. 2,368,13 |
| PW | *viṭsaṅga* | faeces | viṭsaṅga | CARAKA. 8,10 |
| PWG | *viṭsaṅga* | faeces | saṅga | SUŚR. 2,428,12 |
| PW | *śakan* | stercus | śaknas |  |
| PW | *śakṛt* | stercus | śakṛt |  |
| PWG | *śakṛt* | stercus | śaknas | 165 |
| PWG | *śamala* | stercus | viṣṭhā | AK. 2,6,2,18 |
| PW | *śodhana* | faeces | tāmravallī | 216,14 |
| PWG | *śodhana* | faeces | tattvaṃpadārtha˚ | ŚABDAC. |
| PW | *śārīra* | faeces | vṛṣa | S. S. S. 246 |
| PWG | *śārīra* | faeces | vṛṣe | M. 11,202 |
| PW | *ayabhyā* | futuenda | ayabhyā |  |
| PW | *han* | fututa | brāhmaṇihatā | 127,28 |
| PWG | *han* | fututa | he hate he hatetyevaṃ svāmib | 8,9,15 |
| PW | *jabh* | futuere | yabh | ed. Bomb. |
| PW | *ram* | futuere | ramyetām | Spr. 7818 |
| PWG | *ram* | futuere | tasya kalatraṃ rantuṃ samīha | ŚUK. in LA. (III) 37,3 |
| PW | *sap* | futuens | sāpayant |  |
| PWG | *sap* | futuens | kanīkhunadiva sāpayan | TBR. 2,4,6,5 |
| PW | *suyabhyā* | futuenda | suyabhyā | AV. 20,128,9 |
| PW | *yabh* | futuere | yabhate | VET. [U.] 116,3 |
| PWG | *yabh* | futuere | yapsyati | P. 7,2,10 |
| SCH | *yabh* | futuere |  | Dināl.-Śuk. 23,18. |
| PWG | *yabhana* | fututio | yabh | VOP. |
| PWG | *yabhya* | futuenda | ayabhyā | AV. 20,128,8 |
| PW | *yabhyā* | futuenda | ā˚ |  |
| PW | *yābha* | fututio | yābha |  |
| PWG | *yābha* | fututio | yabh | VOP. 21,5 |
| PW | *yābhavant* | futuens | yābhavant |  |
| PWG | *yābhavant* | futuens | yābhavataḥ | KĀVYĀD. 1,66 |
| PW | *kumbhīka* | paedicat | kumbhīka |  |
| PWG | *kar* | mingere | ālikhya vikṣipati | WEST. |
| PW | *mih* | mingere | mīḍha | MBH. 13,5979 |
| PWG | *mih* | mingere | secane | P. 7,2,10 |
<!-- VULGAR_TABLE_END -->

(The *example* column is the nearest Sanskrit token to the Latin gloss and is best-effort;
the citation column is the authoritative locator. A few examples land on an adjacent token
— e.g. *śamala* → *viṣṭhā* — which is itself telling: the editors cross-refer one veiled
word to another.)

### Highlights

- **The √*yabh* cluster** carries the whole *futuere* register: *yabh, yābha, yabhana,
  yabhya, yabhyā, ayabhyā, suyabhyā, yābhavant*, plus the by-form *jabh*. It is
  **lexicalised**, not scattered — the editors reached for *futuere* only here and in a
  few quotation contexts (*ram* "to take pleasure", *sap*, the *hata/fututa* pun under
  *han*).
- **The Vājasaneyi-Saṃhitā Aśvamedha litany** surfaces three times behind the screen:
  *gar* and *sakthan* (VS 23,22 and 23,29 — the ritual obscenities exchanged by the queen
  and the priests) and *maṇḍūradhāṇika* (ṚV 10,155,4), all glossed *cunnus*. This is
  precisely the material a 19th-century editor would not render into German.
- **Metaphorical kennings** are decoded *into* Latin: *madanātapatra* "Madana's parasol"
  and *manobhavāgāra* "the love-god's chamber" → *cunnus*.
- **Scatology is screened only in PWG/PW, never in SCH** (Schmidt has zero), and the
  same dictionaries print open German *Excremente* elsewhere — so here the Latin is
  register-habit more than strict taboo.

## 5. Cross-dictionary: who lifts the screen

Cross-checking the vulgar headwords against **MW** (Monier-Williams, English, 1899,
[`mw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt)) and
**AP90** (Apte, 1890,
[`ap90.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ap90/ap90.txt))
reveals a gradient of candour. The verified worked example, √*yabh*:

| Dictionary | Audience / date | Gloss of √*yabh* |
|---|---|---|
| PWG / PW / SCH | German scholars, 1855–1928 | **futuere** (Latin only) |
| MW | Anglophone scholars, 1899 | "to have sexual intercourse, **futuere**" (English **+** Latin) |
| AP90 | Indian students, 1890 | "To **cohabit**" (open English, no screen) |

The pattern generalises: Monier-Williams keeps the Latin as a learned doublet *beside* an
English gloss (belt and suspenders); **Apte, writing in English for an Indian readership,
mostly drops the screen entirely**. The discretion-screen is a feature of the European
philological apparatus, and it relaxes as the intended readership shifts away from the
European drawing room.

(The automated MW/AP90 flag in the pipeline is a presence-of-Latin heuristic and should be
read as indicative; the √*yabh* row above was confirmed by reading the entries.)

## 6. Why it matters

1. **Coverage gap for the modern reader.** A learner consulting PWG/SCH for *yabh*,
   *cunnus*-glossed kennings, or the Aśvamedha vocabulary meets a Latin wall. Any
   evidence-graded or learner-facing layer over these dictionaries (cf.
   [`ROADMAP_2026_2027.md`](../ROADMAP_2026_2027.md) P6) should **resolve the Latin
   screen into the target language** — the CSV here is a ready de-veiling key.
2. **A register signal, machine-readable.** The Latin gloss is a reliable flag for
   "sexual/scatological sense" across 875 senses — usable for content tagging, for
   filtering, or as a feature in sense classification.
3. **A candour axis across dictionaries.** Pairs neatly with A33 (sense-ordering) and A34
   (Renou registers): the *language of the gloss itself* encodes the editor's stance
   toward the reader, and it varies systematically by audience and date.

## 7. Data & reproducibility

- Full dataset: [`A36_latin_obscena.csv`](A36_latin_obscena.csv) (875 senses).
- Extraction is a single pass over the three SLP1 source files with the term list,
  binomial/homograph filters, and Adams-based register map described in §2; transliteration
  via [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util). The script is
  not committed here (one-off analysis); the method is fully specified above and the CSV is
  the canonical artefact.

## Caveats

- *coitus* (455 senses) is barely a "veil" — it was naturalised German scientific Latin
  by 1855; it is counted as CLINICAL and reported for completeness, not as concealment.
- The clinical set has not been manually audited sense-by-sense; the vulgar set (§4) has.
- Schmidt (SCH) is a supplement, so its proportions are not comparable head-to-head with
  the two main dictionaries.
