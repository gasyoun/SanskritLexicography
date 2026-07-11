# The Latin discretion-screen in nineteenth-century Sanskrit lexicography: a history, and a metalanguage-relative method for measuring it

**Mārcis Gasūns** · independent researcher · gasyoun@ya.ru · ORCID [0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)

**A36 · research note / short communication · draft 2026-07-02 · target: *Beiträge zur Geschichte der Sprachwissenschaft* (Nodus Publikationen, Münster; ISSN 0939-2815; eds. G. Haßler & A. Rüter) — English-language submission**

> **Status:** ready to send (5/5). History-first per the venue: the recovery of the
> *obscaena Latine* across **eleven Cologne dictionaries** (1832–1959; 5 German, 5 English,
> 1 Latin-medium) leads; the metalanguage-relative test (§3b) is the method serving it, with
> three internal controls — screen-vs-doublet (§5b), the 401-entry blunt-German
> counter-inventory (§5b), and Bopp's all-Latin *Glossarium* as positive control (§5b) —
> plus a diachronic shape (§3c) and a comparative-philology sub-study (§5a). Vulgar set
> hand-vetted; clinical set audited for binomial false positives; method confirmed
> corpus-wide across all **43 CDSL dictionaries** (§3d), incl. the Cappeller bilingual and
> Monier-Williams two-edition controls. Referee-style pre-submission review by Fable 5
> (`claude-fable-5`), 02-07-2026, all findings applied — incl. the Liddell–Scott
> comparandum in §0 and the Bopp/MW72 source corrections
> ([`A36_review_fable5.md`](A36_review_fable5.md)). Byline final (M. Gasūns, ORCID
> 0000-0003-4513-884X). Remaining (post-acceptance, not blocking): normalisation to the
> Nodus stylesheet once obtained from the editors; optional German version of the article.

## Abstract

A recurrent device of nineteenth-century philology is the *discretion-screen*: a taboo word
is rendered not in the vernacular but in Latin, so that the learned reader can follow and
the lay reader cannot. In Sanskrit lexicography the classic case is Böhtlingk–Roth's
Petersburg *Wörterbuch*, which glosses the root √*yabh* simply **futuere**, with no German
verb at all. The device is familiar at the margins of classical scholarship — the Loeb
Classical Library's Latin renderings of obscene Greek, Liddell–Scott's *inire, coire* for
βινέω — but it has never been documented for Sanskrit lexicography, nor measured for any
tradition. We measure it. Across **eleven machine-readable Cologne dictionaries** (1832–1959;
five German — **PWG** *Großes Petersburger Wörterbuch*, **PW** *Kürzere Fassung*, **SCH**
Schmidt's *Nachträge*, **PWK** Böhtlingk's abridgment, **GRA** Grassmann; five English —
**MW** Monier-Williams 1899, **AP90** Apte 1890, **AP** Apte revised, **WIL** Wilson,
**CAE** Cappeller; one Latin-medium — **BOP** Bopp's *Glossarium*) we find **2,104
Latin-glossed senses**, concentrated in the German Petersburg core (**875 in PWG/PW/SCH**:
79 vulgar, 796 clinical), and document a **gradient of editorial candour by audience**: the
German dictionaries veil in Latin only; **Monier-Williams gives both** ("to have sexual
intercourse, *futuere*"); **both Apte editions (1890; Gode–Karve 1957–59), written for an
Indian readership, drop the obscene screen entirely** — zero *futuere/cunnus/stercus*, open
English ("to cohabit", "excrement", "dung") for the taboo core. The screen also has a shape
in time — a high-Victorian window, c. 1855–1899: absent in Wilson (1832), the rule in the
Petersburg dictionaries, **tightening within Monier-Williams's own two editions** (*futuere*
zero times in 1872, four in 1899), fading by Schmidt (1928), gone from Gode–Karve (1957–59);
Cappeller, who wrote both a German and an English dictionary, screens in both. A
comparative-philology sub-study shows the screen near-total even for the editors themselves:
of the entire obscene vocabulary across five German dictionaries, **exactly one entry** (PWG
√*yabh*) carries an etymological footnote — one of only **seven** comparative-grammar
references our scan finds in all 593,596 lines of PWG.

Measuring this computationally is confounded by a subtlety: **the screen-language is often
also the source of the target language's ordinary technical vocabulary.** A naïve
string-match for Latin in a Sanskrit–English dictionary flags *semen, penis, coitus* — words
that are simply English — and so cannot tell a euphemistic screen from native scientific
register. We propose a **metalanguage-relative test**: split the Latin material into a
*veil-marker core* (Adams' 1982 basic obscenities *futuere, cunnus, mentula, paedicare*,
plus the blunt scatological terms) and a *clinical* tier (*coitus, penis, vulva, semen*),
and treat a Latin gloss as a screen only when it is *marked* in that dictionary's
metalanguage — for a German dictionary, either tier standing in for an available Germanic
word; for an English dictionary, only the obscene core. We validate the test on the eleven
dictionaries with three internal controls — a screen-vs-doublet check, a blunt-vernacular
counter-inventory, and Bopp's all-Latin *Glossarium* as a positive control — then confirm it
**corpus-wide across all 43 CDSL dictionaries** (five metalanguages). It isolates the
genuine screen where raw matching cannot.

## 0. Related work

**The obscene/euphemistic distinction in Latin.** The register split this method depends on is
J. N. Adams's *The Latin Sexual Vocabulary* (Duckworth, 1982), which established that Latin
had a small set of *basic obscenities* (*cunnus, mentula, futuo, pēdīcō*) alongside a rich
stock of euphemisms and clinical/medical terms ([archive.org](https://archive.org/details/latinsexualvocab0000adam)).
We use that distinction not, as Adams did, to study Latin, but as a **diagnostic** applied to
the *metalanguage* of dictionaries of another language.

**The discretion-screen as an editorial device.** Rendering taboo passages into a learned
language rather than the vernacular is a known practice of classical philology — most visibly
the Loeb Classical Library, which for decades printed the "dirty bits" of Greek authors in
*Latin* on the facing English page (and ribald Romans in Italian), a policy its editor
G. P. Goold dismantled after 1973 as "shabby scholarship"
([Loeb history](https://www.loebclassics.com/page/history); [Harvard Magazine, "Some Classical Profanity"](https://www.harvardmagazine.com/2001/01/some-classical-profanity-html)).
The Sanskrit *obscaena Latine* studied here is the same device, moved from text-editing into
the dictionary entry.

**The same screen inside a dictionary — Greek lexicography.** The device does occur inside a
dictionary entry in the era's most famous lexicon: Liddell–Scott glosses obscene Greek in
Latin — βινέω "*inire, coire*, of illicit intercourse", χέζω "ease oneself, do one's need" —
a coyness removed only by the *Cambridge Greek Lexicon* (Diggle et al. 2021), whose editors'
"no blushes spared" policy made international headlines
([Irish Times, 27 May 2021](https://www.irishtimes.com/culture/books/first-english-dictionary-of-ancient-greek-since-victorian-era-spares-no-blushes-1.4576743)).
That case, however, lives in anecdote and press coverage; it has not been treated as an
object of historiography, and it has never been counted. To our knowledge the discretion-
screen has never been documented for Sanskrit lexicography at all, and never *measured* —
corpus-wide, against controls — for any tradition; that is what this note does.

**Decency in vernacular lexicography — and a contrast.** Anglophone lexicography of the same
period handled obscenity mostly by **omission**: the *OED* under Murray excluded *cunt* and
*fuck*, not restored until the 1972 Supplement, and no English dictionary printed *fuck* until
the Penguin (1965), after the 1960 *Lady Chatterley* trial — under the shadow of Victorian
obscenity law ([Murray Scriptorium, "Defining obscenity"](https://www.murrayscriptorium.org/commentaries/com-defining-obscenity.shtml);
[OUPblog](https://blog.oup.com/2016/08/victorian-profanities-english/)). The Petersburg
strategy is the **opposite** trade-off: *include* the word — scholarship demands completeness —
but *screen* it in Latin. The two solutions (omit vs. encrypt) are the genre's two answers to
the same pressure, and the Latin screen is the one that let a dictionary be both complete and
"decent".

**Computational treatment.** NLP work on euphemism is recent and aimed at running text and
content-moderation (the FigLang 2022 Euphemism Detection shared task and successors,
[ACL](https://aclanthology.org/2022.flp-1.27.pdf)); the nearest classical-philology effort is
Clérice's *Detecting Sexual Content … in First Millennium Latin Texts* (LREC-COLING 2024,
[arXiv:2309.14974](https://arxiv.org/abs/2309.14974)), which classifies sexual content *within*
Latin. Our problem is the inverse and, we believe, novel: not detecting obscenity in a text,
but detecting the **act of screening** in a dictionary — where the screen-language doubles as
the target language's technical register, so the naïve signal is confounded (§3b). No prior
work, computational or historiographic, measures the discretion-screen across a dictionary
corpus or addresses that metalanguage-relativity confound; that gap is this note's
contribution.

## 1. The convention

The practice is not a quirk of one editor but a shared register rule of the St Petersburg
school, taken over from Greek and Roman textual scholarship (where *obscaena* were left
untranslated, or rendered into Latin in an otherwise vernacular apparatus). The screen is
**linguistic, not typographic**: the word is printed in full, in the body of the entry,
but in a language that filters its readership. Böhtlingk's √*yabh* is the textbook case
([csl-orig `pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt)):

> *yabh*, *yábhati* Dhātup. 23,11 … **futuere** (die entsprechende slavische Wurzel
> verzeichnet bei Miklosich …): *yabha mām* "**futue me**" spricht ein Weib AV.
> 20,136,11 … *yiyapsyamānā* **quae futui cupit** ŚĀṄKH. ŚR. 12,23,16.
>
> *(quoted from the machine-readable CDSL text, transliterated; SLP1 markup resolved to IAST)*

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

**Register assignment** starts from J. N. Adams, *The Latin Sexual Vocabulary* (1982):
Adams' *basic obscenities* (*cunnus, mentula, futuo, paedico*) are tagged **VULGAR**,
together with the blunt scatological/urinary set (*stercus, cacare, merda, mingere*). The
latter are not all obscene *within* Latin — *stercus* is ordinary in Roman agricultural
prose, and *mingere* was the acceptable term (Adams treats *merda* as the true obscenity) —
but the criterion here is not their Roman register: it is that **no nineteenth-century
vernacular author prints them except as a screen**, which is what the tag must track. The
medical/euphemistic register (*coitus, penis, vulva, pudenda, virilia, semen, clitoris*) is
tagged **CLINICAL**. The distinction is the point of the study: only the first set is
"Latin so as not to be understood" in the strong sense; the second is the era's default
scientific register, screening by side effect.

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

The full per-sense dataset (all 2,104 rows across eleven dictionaries: dict, metalanguage,
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
| AP90 | en | 0* | 199 | 199 | Apte 1890 — no *obscene* Latin; open English for the taboo core |
| AP | en | 12* | 279 | 291 | Apte (Gode–Karve 1957–59) — the 12 are *faeces* (see below) |
| WIL | en | 5* | 218 | 223 | Wilson 1832 — the 5 are *faeces*, not obscene Latin |
| CAE | en | 6 | 49 | 55 | Cappeller — incl. *futuere* ×2 (English, *not* Latin-medium) |
| BOP | la | 24 | 30 | 54 | Bopp's *Glossarium* — all-Latin; "vulgar" here is not a veil |
| **Total** | | **150** | **1,954** | **2,104** | |

> **\*Register is metalanguage-relative — read the English vulgar column with care.** The
> VULGAR/CLINICAL split is calibrated for a *vernacular* dictionary (the veil-marker set of
> §2: Adams' basic obscenities plus the blunt scatological terms). But a Latinate medical
> word that screens in German
> (*coitus, penis, faeces*) is *naturalised* in English scientific prose — *faeces* is even
> the ordinary British spelling. So the English "vulgar" counts above are inflated by
> naturalised *faeces*. The honest veil-test for an English dictionary is the **truly
> obscene Latin core** no English author would write except to screen — *futuere, cunnus,
> mentula, stercus, paedicare, mingere* — which isolates a sharp result:

| English dict | obscene-Latin core | screens? |
|---|---|---|
| **MW** (1899) | *futuere* ×4, *mingere* ×1 | **yes** |
| **CAE** (Cappeller 1891) | *futuere* ×2 | **yes** (mildly) |
| **AP90** (Apte 1890) | — none — | no |
| **AP** (Gode–Karve 1957–59) | — none — | no |
| **WIL** (Wilson 1832) | — none — | no |

Five results fall out of the wider sweep:

- **The abridgment drops the veil with the bulk.** PWK (Böhtlingk's one-volume *kürzere
  Fassung*) has **zero** vulgar veils and ten clinical senses — the obscene vocabulary is
  among the first material cut when the dictionary is condensed for a wider readership.
- **The Rig-Veda dictionary has almost none — because the corpus does.** GRA has **no
  √*yabh* entry at all**: the root is unattested in the Ṛgveda. The obscene Vedic material
  (the Aśvamedha dialogue, AV 20's *khila* hymns) sits in the *Yajur-* and *Atharvaveda*,
  outside Grassmann's scope. The screen tracks the source corpus, not just the editor.
- **The veil is an English option too, but only for some.** Among the English dictionaries
  only **Monier-Williams** and **Cappeller** reach for the genuine obscene Latin
  (*futuere*); **both Apte editions and Wilson never do**, glossing √*yabh* "to cohabit" and
  scatology as "excrement / dung / ordure" in plain English. So the screen does not split
  cleanly German-vs-English — it splits by editor and intended reader.
- **No Gode–Karve "re-Latinising".** A natural hypothesis — that the 1957–59 revision
  (P. K. Gode & C. G. Karve) re-introduced the European Latin screen — is **false** for the
  obscene core: the revised *AP* carries the same **zero** *futuere/cunnus/stercus* as the
  1890 *AP90*, and glosses √*yabh* identically ("to cohabit"). The only edition-to-edition
  drift is orthographic and clinical — *AP90*'s English "feces/fæces" becomes the classical
  spelling *faeces*, and clinical Latinate terms tick up modestly (*coitus* 23→38, *penis*
  33→38) — not a return of the veil.
- **The all-Latin dictionary is the limiting case.** In Bopp's *Glossarium* (BOP) the whole
  gloss is Latin, so Latin there is the ordinary metalanguage, not a discretion device —
  and indeed Bopp never uses the obscene core for the sex act (he has no √*yabh* entry and
  glosses the field with *coitus / coire*, §3b); the register distinction that organises
  this study collapses. BOP is therefore not a counter-example but a **positive control** —
  see §5b.

## 3b. The methodological payoff: register is metalanguage-relative

The Adams tag (§2) is a property of *Latin*: it asks whether a word was obscene in Rome.
But whether a Latin word *functions as a veil* in a dictionary depends on the dictionary's
**metalanguage** — and the cross-dictionary counts make the two tiers behave in opposite
directions:

| Field (Latin) | tier | German | English | Latin (BOP) |
|---|---|---:|---:|---:|
| *futuere* | **obscene** | 19 | 6 | 0 |
| *cunnus* | **obscene** | 9 | 0 | 0 |
| *paedicare* | **obscene** | 1 | 0 | 0 |
| *mingere* | **obscene** | 3 | 1 | 4 |
| *stercus / faeces* | scato. | 47 | 39 | 12 |
| *coitus* | clinical | 461 | 355 | 14 |
| *vulva* | clinical | 165 | 123 | 3 |
| *penis* | clinical | 135 | **241** | 3 |
| *pudenda* | clinical | 20 | **133** | 0 |
| *semen* | clinical | 12 | **142** | 5 |
| *testiculi* | clinical | 9 | **100** | 3 |
| *clitoris* | clinical | 6 | **21** | 0 |

Two opposite signatures:

- **The obscene core is a German speciality.** *futuere/cunnus/paedicare* run 29 in German,
  6 in English (and those six are confined to MW and Cappeller, §3a), and **0** in Bopp —
  Bopp never reaches for *futuere* at all: his *Glossarium* has no √*yabh* entry, and where
  the sex act does occur he glosses it with clinical Latin (*maithuna* → *coitus*; under
  √*gam*, "adire virum, feminam, i.e. *coire, concumbere*"). These are words used *only* to
  screen; their distribution is the distribution of the screen.
- **The clinical tier inverts — English uses it *more*.** *penis* (241 vs 135), *pudenda*
  (133 vs 20), *semen* (142 vs 12), *testiculi* (100 vs 9), *clitoris* (21 vs 6): for every
  one of these the English dictionaries out-use the German. The reason is not prudery but
  vocabulary — **English scientific prose is natively Latinate**: *semen, penis, testicle,
  pudenda* are simply the ordinary English words, requiring no insertion, whereas German has
  Germanic equivalents (*Same, Glied, Hoden, Scham*) and so a Latin form there is a *marked*
  choice. A high "clinical-Latin" count in English therefore measures the **English lexicon**,
  not concealment; the identical count in German measures a **decision**.

Hence the veil-test cannot be the same string-match in both metalanguages. In German, both
tiers screen (the clinical Latin stands in for an available Germanic word — confirmed in
§5b, where it stands *alone*, not beside German, 94–98 % of the time). In English, only the
**obscene core** (*futuere, cunnus, mentula, stercus, paedicare, mingere*) — words no
anglophone author writes except to avoid the vernacular — is a veil; the naturalised
clinical Latinate is not. Applying *that* test (and only that test) to the English shelf
isolates the result of §3a: Monier-Williams and Cappeller screen, the Aptes and Wilson do
not. Counting raw Latin strings would have buried this under 800-odd naturalised English
*semen*/*penis* tokens.

## 3c. The screen in time — a high-Victorian phenomenon

Ordering the dictionaries by publication date (taken from each CDSL header) and asking only
the metalanguage-correct question — *does it screen the obscene core?* — gives a clear
diachronic shape (counts are the raw corpus-sweep tallies of §3d):

| Dict | Date | Lang | obscene-core | Screens? |
|---|---|---|---:|---|
| WIL Wilson | 1832 | en | 0 | **no** — open English |
| BOP Bopp | (1830–)1847 | la | (13) | n/a — all-Latin metalanguage |
| PWG | 1855–75 | de | 20 | **yes** — the rule |
| BEN Benfey | 1866 | en | 4 | **yes** — *mingere, stercus* |
| MW72 Monier-W. 1st ed | 1872 | en | (1) | **no** — the lone hit is etymological, not a gloss (see below) |
| GRA Grassmann | 1873–75 | de | 0 | — (√*yabh* absent from the Ṛgveda) |
| PW | 1879–89 | de | 30 | **yes** |
| PWK | 1879–89 | de | 0 | no — abridged out with the bulk |
| AP90 Apte 1st ed | 1890 | en | 1 | no — one *cacare*; else open English |
| CAE Cappeller (Engl.) | 1891 | en | 4 | **yes** — *futuere* ×2 |
| CCS Cappeller (Germ.) | 1887 | de | 7 | **yes** — √*yabh* → *futuere* |
| MW Monier-W. 2nd ed | 1899 | en | 6 | **yes** — *futuere* ×4 beside English |
| LAN | 1906 | en | 2 | *mingere* |
| SCH | 1928 | de | 2 | minimal — one *futuere*, one *cunnus* |
| AP Apte (Gode–Karve) | 1957–59 | en | 0 | **no** — open English |

The obscene screen is concentrated in **c. 1855–1899**, absent before (Wilson 1832) and
fading after (Schmidt 1928 keeps only clinical Latin; Gode–Karve Apte 1957–59 has none). The
most telling datum is **within one author**: Monier-Williams's *first* edition (1872)
screens **no headword at all** — it glosses √*yabh* in plain English, "to know carnally,
have sexual intercourse with, lie with", and its single obscene-core string (*cunnus*) sits
inside a comparative etymology, glossing the Lithuanian cognate *pís-ti* in Latin (an exact
miniature of the §5a finding: the comparative reach itself hides behind Latin). His *second*
edition (1899) uses *futuere* **four** times — the screen *tightened* across the
high-Victorian quarter-century, in the same lexicographer's hands. The device is thus not
"Victorian English" or "German philology" as such but a **shared high-Victorian moment** —
the label is anglocentric shorthand for a print-decency regime that was European (the
Petersburg volumes are a Russian-imperial German product) — the half-century when a learned
readership and a strict print-decency norm co-existed.

## 3d. Corpus-wide validation — all 43 Cologne dictionaries

To check that the eleven-dictionary case study is representative and that the method does not
mis-fire elsewhere, we ran the metalanguage detector and the strict obscene-core count over
**every CDSL dictionary above 50 kB — 43 in five metalanguages** (44 source files; the two
editions of Monier-Williams, MW72 and MW, are separate files but counted as one dictionary;
full table: [`A36_corpus_screen.csv`](A36_corpus_screen.csv)). Each gloss-text sample was language-typed by
function-word frequency, then the obscene core (*futuere/cunnus/mentula/stercus/cacare/
paedicare/mingere*) was counted with the binomial + denylist filters of §2.

| Metalanguage | dicts | screeners (obscene-core > 0) |
|---|---|---|
| German | 6 | **PW 30, PWG 20, CCS 7, SCH 2** (PWK 0, GRA 0) |
| English | 29 (30 files, both MW editions) | **MW 6, BEN 4, CAE 4, LAN 2**, MW72 1, AP90 1 (24 others 0) |
| French | 2 | BUR 1 (one *cacare*), STC 0 |
| Latin | 1 | BOP 13 — metalanguage, not a screen |
| Sanskrit-medium | 5 | VCP 1, KRM 1 (one *cacare* each); SKD, ABCH, ARMH 0 |

The sweep confirms and sharpens the case study:

- **The screen is a German speciality with a thin English band.** Substantive screening
  occurs only in the German Petersburg/Cappeller dicts (PW, PWG, CCS, SCH) and four English
  ones (MW, Benfey, Cappeller-English, Lanman). The remaining ~24 English dictionaries — and
  every later one — score zero. Across 43 dictionaries the obscene veil is **not** a general
  feature of Sanskrit lexicography; it is a local, dated practice.
- **A within-author, cross-metalanguage control: Cappeller.** Carl Cappeller wrote *both* a
  Sanskrit–German dictionary (**CCS**, 1887) and a Sanskrit–English one (**CAE**, 1891), and
  he screens in **both** — *yabh* → *futuere* in the German, *futuere* ×2 in the English.
  Holding the author constant, the screen survives the change of metalanguage: it is a
  property of the scholarly register, not of German alone.
- **French takes a third path.** Neither Latin obscenity nor vulgar French: Stchoupak–Nitti
  (STC, 1932) glosses √*yabh* "**faire le coït**" — a clinical *French* phrase. Romance
  vernaculars, already close to the Latinate clinical register, euphemise *in the vernacular*
  rather than switching languages.
- **Sanskrit-medium dictionaries do not screen at all.** The Śabdakalpadruma, Vācaspatya
  &c. score zero obscene Latin (the lone *cacare* tokens are incidental): a dictionary whose
  metalanguage *is* the learned language has no lay outsider to screen against — the veil
  presupposes a vernacular/elite split that a Sanskrit-to-Sanskrit kośa lacks.

(The corpus-wide obscene-core counts are raw per-field tallies for triage; the curated
eleven-dictionary figures in §3–§5 are the hand-vetted numbers.)

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
| CAE | Anglophone scholars, 1891 | (uses *futuere* elsewhere; mild screen) |
| AP90 | Indian students, 1890 | "To **cohabit**" (open English, no screen) |
| AP | Indian students, 1957–59 | "To **cohabit**, have sexual intercourse with" (open English) |

The pattern is **not** a simple German-veils / English-open split. The screen is an option in
both metalanguages, taken up by editor and intended reader: the German Petersburg school
uses it as a rule, **Monier-Williams** keeps the Latin as a learned doublet beside English,
and **Cappeller** reaches for *futuere* twice — while **both Apte editions and Wilson never
screen the obscene core**, glossing √*yabh* "to cohabit" in plain English. The veil is a
feature of the *European philological drawing room*; it is absent precisely from the
dictionaries made for Indian students, and (see §3a) it does **not** return in the
Gode–Karve revision.

(The automated MW/AP90 flag in the extraction is a presence-of-Latin heuristic and is read
through the obscene-core test of §3a; the √*yabh* rows above were confirmed by reading the
entries.)

## 5a. The one footnote behind the curtain — comparative philology and the obscene root

Böhtlingk's √*yabh* does something the rest of the obscene vocabulary never does: it points
the reader *outward*, to the cognate. After *futuere* it adds "(die entsprechende slavische
Wurzel verzeichnet bei **Miklosich**, *Vgl. Gr.* III, S. VIII und *Wurzeln des Altslov.*
S. 15)" — a nod to the Slavic root (Common Slavic *jebati*, Russ. *ebát′*), itself an
obscenity, so that the comparative point too is made behind the Latin screen.

This turns out to be **unique**. Scanning every vulgar-veil entry across all five German
dictionaries for comparative-philology apparatus (the sigla *Miklosich, Curtius, Fick,
Pott, Kuhn, Benfey*; *Vgl. Gr.*; cognate-language tags *slav., lat., gr., got., lit.,
ahd.*), **exactly one entry matches: PWG √*yabh***. PW's √*yabh* is terse — "*futuere*
BHĀG. P." — with no footnote; *mih, gu, viś, śakṛt, gūtha* and the rest carry none. And the
rarity is structural, not incidental: across the entire 593,596-line PWG, the same scan
finds only **seven** comparative-grammar references at all (the Petersburg *Wörterbuch*
programmatically excluded Indo-European etymology, and whatever a wider siglum list might
add, the order of magnitude — a handful in half a million lines — stands). That √*yabh* is
one of those seven is the point — the single place
where Böhtlingk reached past the Sanskrit into comparative grammar is an obscene root, and
the reach is itself encrypted in Latin and a Latin-script Slavic siglum.

## 5b. Positive control — what the screen actually suppressed (Bopp's *Glossarium*)

Because Bopp's *Glossarium Sanscritum* (BOP, 1830–47) is written *entirely* in Latin, it
gives the obscene Sanskrit vocabulary **unscreened** — Latin there is the ordinary
metalanguage, not a discretion device. BOP therefore works as a positive control: it shows
the full obscene semantic field in plain terms, against which the German screen's
**selectivity** becomes visible.

Two fields are decisive. BOP glosses Sanskrit "prostitute" words with *meretrix*
(*bandhakī, gaṇikā, paṇyastrī, puṃścalī, veśyā*) and "violate / rape" words with
*stuprum / stuprare* (*dhṛṣ, duṣ, mṛś*). **In the German dictionaries these two fields are
glossed in German, never in Latin** — *gaṇikā* → *Hure / Buhlerin*, *duṣ* → *schänden* —
and indeed the entire German corpus has **zero** *meretrix* and **zero** *stuprum*. The
screen was *not* applied here. Why? Because German already had printable words for
"whore" and "to violate"; it had no printable word for the sexual act, the genitalia, or
excrement. **The Latin screen maps precisely onto the gaps in the decent German lexicon** —
it covers *futuere / cunnus / stercus* (where German offered only *ficken / Fotze /
Scheiße*) and stops exactly where German offered a usable euphemism. Bopp, lacking any
vernacular to fall back on, Latinises the whole field and so throws that selectivity into
relief.

| Sanskrit field | Bopp (no screen) | German dicts (PWG/PW) |
|---|---|---|
| sexual act (*maithuna*, √*gam*; BOP lacks √*yabh*) | *coitus; coire, concumbere* | *futuere* for √*yabh* (Latin — no decent German) |
| genitalia (*bhaga, meḍhra*) | *vulva, penis* | *vulva, penis* (Latin) |
| excrement (*viṣ, śakṛt*) | *stercus, excrementum* | *stercus, faeces* (Latin) |
| **prostitute** (*gaṇikā, veśyā*) | *meretrix* | **German** (*Hure, Buhlerin*) — never Latin |
| **rape / violate** (*duṣ, dhṛṣ*) | *stuprum, stuprare* | **German** (*schänden*) — never Latin |

The screen, in other words, is not a blanket policy on "indecent meanings"; it is a precise
patch over the words the editors' own language could not print.

### Screen, not doublet

One might object that the German *coitus* is merely a learned synonym printed *beside* a
German gloss — a doublet ("Beischlaf, coitus"), not a screen. The entries refute this. For
each clinical Latin term we counted PWG+PW entries where it stands **alone** versus where a
German near-synonym co-occurs:

| Latin term | German near-synonym sought | stands **alone** | doublet | screen rate |
|---|---|---:|---:|---:|
| *coitus* | Beischlaf / Begattung / Umarmung | 194 | 4 | 98 % |
| *penis* | Glied / Ruthe / männliches Glied | 89 | 3 | 97 % |
| *vulva* | Scham / Scheide / Schoß | 71 | 4 | 95 % |
| *futuere* | beschlafen / begatten | 30 | 2 | 94 % |
| *stercus / faeces* | Kot / Excremente / Mist | 37 | 10 | 79 % |

For the sexual field the Latin word almost never appears next to a German one — it *replaces*
it. The few doublets are telling exceptions: the *penis* doublets are the Vedic words
*kapṛth* and *śephas*, where the philological commentary forced the German out; the *futuere*
doublets are both *ram* "to take pleasure", glossed in German with the Latin only for the
crude sense.

### A taboo gradient, not a switch

Combining the doublet rates with the BOP control reveals that the screen has **three
intensities**, tracking how taboo the concept was in 19th-century bourgeois German and
whether a printable German word existed:

1. **Sexual act + genitalia — near-absolute screen (94–98 % Latin-alone).** German had no
   printable word (*ficken, Fotze, Schwanz*), so *futuere / coitus / penis / vulva* stand
   alone almost without exception.
2. **Excretion — partial screen (79 %).** Here German *did* have semi-printable words, and
   the dictionaries use them: PWG glosses √*had* with the blunt German *scheissen*, √*mih*
   with the doublet *mingere* / *seichen*, and *avaskara, gūtha, uccāra* with German *die
   Excremente*. Latin *stercus/faeces* is chosen for some roots, German *Kot/scheissen* for
   others — register habit, not an absolute rule (so SCH, the politest, simply omits the
   field).
3. **Prostitution + sexual violence — no screen at all.** German had fully respectable words,
   so *meretrix* and *stuprum* never appear: *gaṇikā, paṇyastrī, puṃścalī* → *Hure*; √*duṣ* →
   *verderben, schänden*. Bopp must write *meretrix / stuprare* because Latin is all he has;
   the German editors, who had *Hure* and *schänden*, never reach for Latin here.

The Latin screen is thus **inversely proportional to the printability of the German word and
proportional to the taboo-load of the concept** — densest on sex, partial on the body's
waste, absent on the morally-but-not-verbally charged (the whore, the rape). Bopp's
all-Latin glossary, by flattening every field to Latin, is exactly the baseline that makes
this German gradient legible.

### Blunt German is printed — for everything but sex

The decisive counter-evidence: the German dictionaries are *not* squeamish in general. A
sweep for blunt or plain German taboo words finds **401 entries** where the editors print
exactly the vernacular they supposedly avoid — and the distribution is the proof:

| Taboo field | blunt/plain German printed | entries (5 German dicts) |
|---|---|---:|
| prostitution | *Hure, Hurenwirthin, Hurenkind, Buhlerin, Dirne* | 158 |
| excrement (noun) | *Koth, Unrat, Mist, Dreck* | 106 |
| urination | *Harn, harnen, seichen, pissen* | 68 |
| sexual violence | *schänden, geschändet, entehren, Unzucht, vergewaltigen* | 44 |
| flatulence | *Furz, furzen* | 15 |
| defecation (verb) | ***scheissen, beschissen*** | 10 |
| **sex act / genitalia** | *ficken, vögeln, Fotze, Möse, Schwanz, Pimmel* … | **0** |

The editors who would not write a German word for "to copulate" or "vulva" cheerfully printed
**√*had* → *scheissen*** "to shit" (Dhātup. 23,8), **√*mih* → *seichen*** "to piss",
**√*snu*/√*sru* → *beschissen***, *Furz* "fart", and **158** instances of *Hure* "whore".
The blunt-German count for the **sex act and the genitalia is exactly zero** — the apparent
hits (*vögeln* = "(of) birds", *Schwanz* = animal "tail") are homographs, not the sexual
words. So the screen is not a decency policy in general; it is a precise, near-surgical
suppression of the **sexual** vernacular specifically, with the body's other functions left
in plain (often crude) German. (Full inventory: [`A36_blunt_german.csv`](A36_blunt_german.csv).)

## 6. Why it matters

1. **For the historiography of the discipline.** The study recovers and dates a practice that
   the literature on 19th-century comparative philology and lexicography has not described as
   such: a systematic *linguistic* discretion-screen, distinct from the Anglophone strategy of
   omission (Mugglestone 2005), by which the St Petersburg school and its heirs kept their
   dictionaries simultaneously *complete* and *decent*. It locates the practice precisely —
   strongest in Böhtlingk–Roth, fading by Schmidt (1928), tightening within Monier-Williams's
   own two editions — and ties it to the same impulse that produced Loeb's Latin-screened
   Greek a generation later. For the history of Indology it also returns to view a stratum of
   the lexica (the Aśvamedha and *kāvya* obscene vocabulary) that the screen made invisible to
   non-classicists for over a century.
2. **A reusable method (the formal contribution).** The metalanguage-relative test (§3b) generalises
   beyond Sanskrit and beyond Latin: any historical dictionary whose discretion-screen is
   written in a *prestige* language that also feeds the target language's technical register
   (Latin/Greek into the European vernaculars; Classical Chinese; Sanskrit into the modern
   Indian languages) faces the same confound, and the same fix — score the screen against the
   *marked-ness* of the gloss in that dictionary's own metalanguage, not against a raw word
   list. The three controls here (screen-vs-doublet, blunt-vernacular counter-inventory,
   all-screen-language positive control) are a portable validation kit.
3. **Coverage gap for the modern reader.** A learner consulting PWG/SCH for *yabh*,
   *cunnus*-glossed kennings, or the Aśvamedha vocabulary meets a Latin wall. Any
   evidence-graded or learner-facing layer over these dictionaries (cf.
   [`ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md) P6) should **resolve the Latin
   screen into the target language** — the CSV here is a ready de-veiling key.
4. **A register signal, machine-readable.** The Latin gloss is a reliable flag for
   "sexual/scatological sense" across 2,104 senses in eleven dictionaries — usable for
   content tagging, for filtering, or as a feature in sense classification.
5. **A candour axis across dictionaries.** Pairs neatly with A33 (sense-ordering) and A34
   (Renou registers): the *language of the gloss itself* encodes the editor's stance
   toward the reader, and it varies systematically by audience and date.

## 7. Data & reproducibility

- Full dataset: [`A36_latin_obscena.csv`](A36_latin_obscena.csv) (2,104 Latin-glossed senses,
  eleven dictionaries, with a `lang` column for metalanguage). The `register` column is the
  raw, metalanguage-neutral Adams tag; for English dictionaries it should be read through the
  caveat below (naturalised *faeces/coitus/penis* are not veils there).
- Counter-inventory: [`A36_blunt_german.csv`](A36_blunt_german.csv) (401 entries where the
  German dictionaries print blunt/plain German for a taboo concept), supporting §5b.
- Corpus-wide sweep: [`A36_corpus_screen.csv`](A36_corpus_screen.csv) (44 rows — the 43
  CDSL dictionaries with MW's two editions as separate rows — with metalanguage, year, raw
  obscene-core and clinical counts), supporting §3d.
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
- **Register is metalanguage-relative** (§3a). The VULGAR/CLINICAL tag is calibrated for a
  *vernacular* dictionary; in English prose the Latinate *coitus/penis/faeces* are
  naturalised, so the English "vulgar" counts are read through the obscene-core test
  (*futuere/cunnus/stercus*), not the raw tag. In Bopp (Latin-medium) the distinction does
  not apply at all (§5b).

## References

### Secondary literature

- Adams, James Noel. 1982. *The Latin Sexual Vocabulary*. London: Duckworth.
- Clérice, Thibault. 2024. Detecting Sexual Content at the Sentence Level in First Millennium
  Latin Texts. In *Proceedings of LREC-COLING 2024*. Torino. (arXiv:2309.14974.)
- Diggle, James, et al. (eds.). 2021. *The Cambridge Greek Lexicon*. 2 vols. Cambridge:
  Cambridge University Press.
- Lee, Patrick, Anna Feldman & Jing Peng. 2022. A Report on the Euphemisms Detection Shared
  Task. In *Proceedings of the 3rd Workshop on Figurative Language Processing (FLP)*, 184–190.
  Abu Dhabi / EMNLP. (ACL Anthology 2022.flp-1.27.)
- Mugglestone, Lynda. 2005. *Lost for Words: The Hidden History of the Oxford English
  Dictionary*. New Haven & London: Yale University Press.

### Primary sources — the dictionaries (with CDSL sigla)

- **PWG** Böhtlingk, Otto & Rudolph Roth. 1855–1875. *Sanskrit-Wörterbuch* (Großes
  Petersburger Wörterbuch). 7 vols. St. Petersburg: Kaiserliche Akademie der Wissenschaften.
- **PW / PWK** Böhtlingk, Otto. 1879–1889. *Sanskrit-Wörterbuch in kürzerer Fassung*.
  St. Petersburg: Kaiserliche Akademie der Wissenschaften.
- **SCH** Schmidt, Richard. 1928. *Nachträge zum Sanskrit-Wörterbuch in kürzerer Fassung von
  Otto Böhtlingk*. Leipzig: Harrassowitz.
- **GRA** Grassmann, Hermann. 1873–1875. *Wörterbuch zum Rig-Veda*. Leipzig: Brockhaus.
- **BOP** Bopp, Franz. 1847. *Glossarium Sanscritum*. 2nd ed. Berlin: Dümmler.
- **MW72 / MW** Monier-Williams, Monier. 1872 (1st ed.), 1899 (2nd ed., rev.). *A
  Sanskrit-English Dictionary*. Oxford: Clarendon Press.
- **AP90** Apte, Vaman Shivram. 1890. *The Practical Sanskrit-English Dictionary*. Poona:
  Shiralkar. **AP** Rev. & enl. ed. P. K. Gode & C. G. Karve. 1957–1959. Poona: Prasad
  Prakashan.
- **WIL** Wilson, Horace Hayman. 1832. *A Dictionary in Sanscrit and English*. 2nd ed.
  Calcutta: Education Press.
- **CCS** Cappeller, Carl. 1887. *Sanskrit-Wörterbuch*. Strassburg: Trübner. **CAE** id. 1891.
  *A Sanskrit-English Dictionary*. London: Luzac.
- **BEN** Benfey, Theodor. 1866. *A Sanskrit-English Dictionary*. London: Longmans, Green.
- **LAN** Lanman, Charles Rockwell. 1884. *A Sanskrit Reader: Text and Vocabulary and Notes*.
  Boston: Ginn. (The CDSL edition of the vocabulary is dated 1906.)
- **STC** Stchoupak, Nadine, Luigia Nitti & Louis Renou. 1932. *Dictionnaire sanscrit-
  français*. Paris: Geuthner. **BUR** Burnouf, Émile. 1866. *Dictionnaire classique
  sanscrit-français*. Paris/Nancy.
- All consulted in the machine-readable editions of the **Cologne Digital Sanskrit
  Dictionaries (CDSL)**, Universität zu Köln,
  [`www.sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/) /
  [`github.com/sanskrit-lexicon/csl-orig`](https://github.com/sanskrit-lexicon/csl-orig).

*(Citation style to be normalised to the Nodus / BGS house style on submission.)*
