# *Obscaena Latine*: the Latin discretion-screen in the Cologne German dictionaries (PWG, PW, SCH) — and who lifts it

**A36 · research note / short communication · draft 2026-06-26 · target (history-of-lexicography): Dictionaries (DSNA) / Historiographia Linguistica / Beiträge zur Geschichte der Sprachwissenschaft**

> **Status:** draft (2/5). Dataset extracted, filtered, and reproducible across **eleven
> Cologne dictionaries** (5 German, 5 English, 1 Latin-medium); vulgar set hand-vetted,
> clinical set audited for binomial false positives, comparative-apparatus sub-study done.
> Needs a related-work paragraph (Adams 1982; the history of *verba obscena* in scholarly
> lexicography, the Anglo-Indian decency debates) and a final venue decision.

## Abstract

Nineteenth-century European Sanskrit lexicography inherited a classical-philology
convention: **taboo vocabulary is glossed in Latin, not in the vernacular**, so that the
classically educated reader can follow while the general reader (in the period's terms,
women and the young) cannot. The locus classicus is Böhtlingk–Roth's entry for the root
√*yabh*, glossed simply **futuere** — with a footnote to the Slavic cognate (Miklosich) —
rather than with any German verb. We extract every Latin sexual/scatological gloss from
**eleven machine-readable Cologne dictionaries** — five German (**PWG** *Großes
Petersburger Wörterbuch*, **PW** *Kürzere Fassung*, **SCH** Schmidt's *Nachträge*, **PWK**
Böhtlingk's abridgment, **GRA** Grassmann's *Wörterbuch zum Rig-Veda*), five English (**MW**
Monier-Williams 1899, **AP90** Apte 1890, **AP** Apte revised, **WIL** Wilson 1832, **CAE**
Cappeller), and one Latin-medium (**BOP** Bopp's *Glossarium*, where the whole gloss is
Latin and the distinction collapses). We separate two registers that the practice conflates:
a small **vulgar veil** (Latin words that are themselves obscene — *futuere, cunnus,
mentula, paedicare, mingere, stercus/cacare*) and a large **clinical Latin** default
(*coitus, penis, vulva, pudenda, semen, clitoris*). We find **2 104 Latin-glossed senses**
in all, concentrated in the German Petersburg core (**875 in PWG/PW/SCH**: 79 vulgar, 796
clinical), and document a **gradient of editorial candour by audience**: the German
dictionaries veil in Latin only; **Monier-Williams gives both** ("to have sexual
intercourse, *futuere*"); **Apte 1890, an Indian lexicographer writing for Indian students,
drops the screen entirely** — zero Latin veils, open English ("to cohabit", "excrement",
"dung") throughout. A comparative-philology sub-study shows the screen is near-total even
for the editors themselves: of the entire obscene vocabulary across five German
dictionaries, **exactly one entry** (PWG √*yabh*) carries an etymological footnote — and
it is one of only **seven** comparative-grammar references in all 593 596 lines of PWG.

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
[`csl-orig/v02`](https://github.com/sanskrit-lexicon/csl-orig/tree/master/v02) — eleven
dictionaries grouped by metalanguage: **German** `pwg`, `pw`, `sch`, `pwkvn` (PWK), `gra`;
**English** `mw`, `ap90`, `ap`, `wil`, `cae`; **Latin-medium** `bop`.
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

The full per-sense dataset (all 2 104 rows across eleven dictionaries: dict, metalanguage,
headword, register, field, Latin gloss, Sanskrit example, citation) is
[`A36_latin_obscena.csv`](A36_latin_obscena.csv); the table above is the German Petersburg
core, where the convention is densest and the vulgar set was hand-vetted.

## 3a. The full corpus — eleven dictionaries

Latin-glossed senses per dictionary (one per field per entry):

| Dict | Lang | Vulgar | Clinical | Total | Note |
|---|---|---:|---:|---:|---|
| PWG | de | 33 | 206 | 239 | *Großes PW* — the locus of the convention |
| PW | de | 44 | 228 | 272 | *Kürzere Fassung* — keeps the spicy material |
| SCH | de | 2 | 362 | 364 | Schmidt's *Nachträge*; heavy *coitus/vulva*, almost no vulgar veil |
| PWK | de | **0** | 10 | 10 | Böhtlingk's abridgment — the screen is *dropped with the bulk* |
| GRA | de | **0** | 3 | 3 | Grassmann (Rig-Veda only) — the obscene corpus is elsewhere |
| MW | en | 24 | 370 | 394 | keeps Latin as a learned doublet beside English |
| AP90 | en | **0** | 199 | 199 | Apte 1890 — **no Latin veil at all**; open English |
| AP | en | 12 | 279 | 291 | Apte revised — reintroduces some Latin (esp. *stercus/faeces*) |
| WIL | en | 5 | 218 | 223 | Wilson 1832 |
| CAE | en | 6 | 49 | 55 | Cappeller (English, *not* Latin-medium) |
| BOP | la | 24 | 30 | 54 | Bopp's *Glossarium* — all-Latin; "vulgar" here is not a veil |
| **Total** | | **150** | **1 954** | **2 104** | |

Four results fall out of the wider sweep:

- **The abridgment drops the veil with the bulk.** PWK (Böhtlingk's one-volume *kürzere
  Fassung*) has **zero** vulgar veils and ten clinical senses — the obscene vocabulary is
  among the first material cut when the dictionary is condensed for a wider readership.
- **The Rig-Veda dictionary has almost none — because the corpus does.** GRA has **no
  √*yabh* entry at all**: the root is unattested in the Ṛgveda. The obscene Vedic material
  (the Aśvamedha dialogue, AV 20's *khila* hymns) sits in the *Yajur-* and *Atharvaveda*,
  outside Grassmann's scope. The screen tracks the source corpus, not just the editor.
- **Apte 1890 is the candour benchmark.** AP90 carries **zero** Latin veils; where the
  Germans write *stercus* and *futuere* it writes "excrement", "dung", "to cohabit" in plain
  English (98 lines use open English *excrement/dung*). Writing in English for an Indian
  student readership, Apte simply does not screen. The *revised* Apte (AP) reintroduces a
  little Latin (12 vulgar senses, mostly *stercus/faeces*), a small step back toward the
  European register.
- **The all-Latin dictionary is the limiting case.** In Bopp's *Glossarium* (BOP) the whole
  gloss is Latin, so *futuere*/*cunnus* are not a discretion-screen but the ordinary
  metalanguage; the register distinction that organises this study collapses, and BOP is
  reported only for completeness.

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

## 5a. The one footnote behind the curtain — comparative philology and the obscene root

Böhtlingk's √*yabh* does something the rest of the obscene vocabulary never does: it points
the reader *outward*, to the cognate. After *futuere* it adds "(die entsprechende slavische
Wurzel verzeichnet bei **Miklosich**, *Vgl. Gr.* III, S. VIII und *Wurzeln des Altslov.*
S. 15)" — a nod to the Slavic root (OCS *jębati* / Russ. *jebátʹ*), itself an obscenity, so
that the comparative point too is made behind the Latin screen.

This turns out to be **unique**. Scanning every vulgar-veil entry across all five German
dictionaries for comparative-philology apparatus (the sigla *Miklosich, Curtius, Fick,
Pott, Kuhn, Benfey*; *Vgl. Gr.*; cognate-language tags *slav., lat., gr., got., lit.,
ahd.*), **exactly one entry matches: PWG √*yabh***. PW's √*yabh* is terse — "*futuere*
BHĀG. P." — with no footnote; *mih, gu, viś, śakṛt, gūtha* and the rest carry none. And the
rarity is structural, not incidental: the entire 593 596-line PWG contains only **seven**
comparative-grammar references at all (the Petersburg *Wörterbuch* programmatically excluded
Indo-European etymology). That √*yabh* is one of those seven is the point — the single place
where Böhtlingk reached past the Sanskrit into comparative grammar is an obscene root, and
the reach is itself encrypted in Latin and a Latin-script Slavic siglum.

## 6. Why it matters

1. **Coverage gap for the modern reader.** A learner consulting PWG/SCH for *yabh*,
   *cunnus*-glossed kennings, or the Aśvamedha vocabulary meets a Latin wall. Any
   evidence-graded or learner-facing layer over these dictionaries (cf.
   [`ROADMAP_2026_2027.md`](../ROADMAP_2026_2027.md) P6) should **resolve the Latin
   screen into the target language** — the CSV here is a ready de-veiling key.
2. **A register signal, machine-readable.** The Latin gloss is a reliable flag for
   "sexual/scatological sense" across 2 104 senses in eleven dictionaries — usable for
   content tagging, for filtering, or as a feature in sense classification.
3. **A candour axis across dictionaries.** Pairs neatly with A33 (sense-ordering) and A34
   (Renou registers): the *language of the gloss itself* encodes the editor's stance
   toward the reader, and it varies systematically by audience and date.

## 7. Data & reproducibility

- Full dataset: [`A36_latin_obscena.csv`](A36_latin_obscena.csv) (2 104 senses, eleven
  dictionaries, with a `lang` column for metalanguage).
- Extraction is a single pass over the eleven SLP1 source files with the term list,
  binomial/homograph filters, and Adams-based register map described in §2; transliteration
  via [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util). The scripts are
  not committed here (one-off analysis); the method is fully specified above and the CSV is
  the canonical artefact.

## Caveats

- *coitus* (455 senses in the German core) is barely a "veil" — it was naturalised German
  scientific Latin by 1855; it is counted as CLINICAL and reported for completeness, not as
  concealment.
- **Clinical-set audit.** The clinical fields were audited for the plant/animal-binomial
  Latin one *expects* in these dictionaries (and which is *not* a discretion-screen): the
  *clitoris* field was cleared of the genus *Clitoria* (the pea, Skt. *aparājitā*), *vulva*
  checked for *Chenopodium vulvaria* (none present), *semen* for binomial *-sperma* tails
  (97 removed, e.g. *Moringa pterygosperma*), and *pudenda* for the German homograph
  *verendet* "perished". The reported clinical counts are post-audit. The vulgar set (§4)
  was additionally vetted entry-by-entry.
- Schmidt (SCH), PWK and GRA are a supplement, an abridgment and a single-corpus glossary
  respectively, so their proportions are not comparable head-to-head with PWG/PW.
