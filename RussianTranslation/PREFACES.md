# PWG prefaces — dates, what they give us, how they help pwg_ru

Böhtlingk & Roth's *Sanskrit-Wörterbuch* (the "Großes Petersburger Wörterbuch",
PWG) appeared in **7 volumes over 1855–1875**. The front matter is digitized and
translated in the PWG repo:
[prefaces/](https://github.com/sanskrit-lexicon/PWG/tree/master/prefaces) —
German original (`*.md`), English (`*.en.md`), **Russian (`*.ru.md`)**, plus the
combined [pwgpref_all.de.md](https://github.com/sanskrit-lexicon/PWG/blob/master/prefaces/pwgpref_all.de.md)
/ `.en.md` / `.ru.md`. This note documents the dates and what the prefaces give
the pwg_ru project.

## The seven volumes and their dates

The forewords are **dual-dated** (Julian / Gregorian — Russia used the Julian
calendar) and **dual-located**: Böhtlingk worked in St. Petersburg (later Jena),
Roth in Tübingen. They "live at a distance from one another too great to permit
even occasional meetings" (vol. 1).

| Vol | Range | Title-page | Foreword signed | Place |
|---|---|---|---|---|
| **1** | vowels (*Die Vocale*: a … au) | **1855** | 1855 (footnote dated 17 May 1855) | St. Petersburg |
| **2** | क — ट (ka–ṭa) | **1858** | **14/26 October 1858** | Tübingen |
| **3** | (ṭha … ) | **1861** | **1/13 July 1861** | St. Petersburg / Tübingen |
| **4** | | **1865** | 1865 | — |
| **5** | | **1868** | 1868 | — |
| **6** | | **1871** | *(title page only — no foreword)* | — |
| **7** | ( … h, final) | **1875** | **4 August 1875** | **Jena** and Tübingen |

**Why the dates matter — the dictionary changed over 25 years** (this is the key
point: an entry's character depends on *when*, i.e. *which letter/volume*, it was
written):

- **Source coverage grew through the alphabet.** The abbreviation notes are
  explicit: *MBh* "from p. 521 the first three books, from p. 601 also the last
  five, and from ऋ onward also the 13th book have been exploited"; *Bhāg. P.*
  "from ऋ onward the 9 Skandha." So a word in **a-** (vol. 1) was checked against
  *less* MBh/Purāṇa than a later word — early entries cite a narrower corpus.
- **Vedic depth thinned after vol. 4.** Vol. 1 (1855) is a Vedic manifesto with
  exhaustive Saṃhitā treatment. By **vol. 5 (1868)** they *deliberately held back*
  Vedic articles and corrections, yielding precedence to Aufrecht's Vedic
  dictionary and Müller's Ṛgveda then being announced ("easier than we did sixteen
  years ago"). So **later-alphabet Vedic senses are less exhaustive** than early
  ones.
- **Pacing.** By vol. 4 (1865), "⅗ of our work… about 12½ years"; finished vol. 7
  after "nearly twenty-five years."

→ *Implication for pwg_ru: stamp each entry with its volume/letter, so a reader
(and our QA) knows an `a-` Vedic sense rests on fuller treatment than a late-letter
one.*

## What the prefaces give us

### 1. The authoritative source bibliography (with editions + citation rules)
Pages 07–11 (+ per-volume additions) are the **Verzeichniss der Abkürzungen** —
the same table now in `pwgbib.txt` that drives our `<ls>` resolver, but the
prefaces add what the bare table lacks:
- the **exact edition** behind each siglum (AV = Roth & Whitney, Berlin 1855;
  Śat. Br. = Weber 1849; M = Manu ed. Loiseleur; …) — so a citation is dated and
  locatable;
- the **citation structure** per source (Ait. Br. by Pañcikā + chapter; Hit. by
  book/page/line; *Med.* arranged by final consonant; a single number = śloka,
  double = page+line);
- the **`*` = rarely-cited** convention.

### 2. The editorial method (vol. 1 foreword — a manifesto)
- **Two irreducible sources:** (a) the Indian word-collections (kośas, grammarians)
  — used *critically*, "poor and slight… countless errors and distortions," kept
  only because even an error "points toward the truth"; (b) **their own collations
  from actual literature — the only firm ground.** *This is exactly our
  form-citation (kośa/grammar) vs text-source distinction — confirmed as
  Böhtlingk-Roth's own principle.*
- **The Stellen-method:** meaning "won from the texts themselves by holding
  together all passages related in wording or content." PWG glosses are
  usage-grounded, not glossator-derived.
- **Anti-commentator for the hymns:** Sāyaṇa et al. are good for the Brāhmaṇa
  (theology) but *unfit* for the ancient hymns (they read classical Sanskrit + their
  own theology into the Veda); PWG seeks "the meaning which the poets themselves
  placed in their hymns." → *A PWG Vedic sense is 19th-c. European philology, at
  times since superseded — flag, don't canonize.*
- **Against vague concepts:** commentators glossed countless Vedic words with
  "force, sacrifice, food, wisdom," verbs with "to go, to move"; PWG insists on the
  "definite value and concrete content" of each. *This is the same drive toward
  discriminated, concrete senses as our Apresjan synonym-discrimination step.*

### 3. The concrete conventions (vol. 1, p. VII)
Directly relevant to our parser and translation:
- **Verbal roots carry no class number** — it "follows of itself from the appended
  3rd person sg. present, especially with the accent." (So absence of a class is
  intentional, not missing data.)
- Root-final ऋ ॠ ऌ and diphthongs are banished from final position; **final ऋ in
  nominal stems is written अर्** (affects headword/key forms).
- **Accent:** a simple non-Indian notation for the dictionary's own forms; the
  manuscript marking is kept in Vedic *examples*.
- Denominatives are listed under the denominative suffix, not as roots.
- **Division of labour:** Roth = the Veda + Vedic auxiliary books + Suśruta's
  Āyurveda + botanical names; Böhtlingk = all the rest + the arrangement of the
  whole. (So a botanical or Vedic entry is Roth's hand; the bulk is Böhtlingk's.)

## How this helps pwg_ru

1. **Front matter (done in part):** the prefaces are already translated to Russian
   (`PWG/prefaces/*.ru.md`) — the pwg_ru edition gets a faithful Russian Vorrede,
   plus a short editor's note explaining our corpus-attested method.
2. **Conventions → code/translation rules:** the root-no-class rule, the अर्/accent
   conventions, and the two-source critical principle feed the microstructure parser
   and the translation prompt (e.g. don't "fix" a missing root class; treat a
   kośa-only sense as Indian-lexicographic, not attested usage).
3. **Volume/date metadata layer:** stamp each entry with its volume + letter so the
   uneven Vedic depth and growing source coverage are visible (an `a-` entry ≠ a
   late-letter entry in evidentiary weight).
4. **Citation grounding:** the edition + citation-structure notes let us resolve and,
   where useful, *modernize* a `<ls>` reference (e.g. know that MBh = the Calcutta
   edition, cited by parvan/śloka).
5. **Theory alignment:** PWG's own war on vague concept-glosses and its passage-
   collation method are the 1855 ancestor of our stratified, corpus-attested,
   Apresjan-discriminated senses — the pwg_ru edition is continuous with Böhtlingk-
   Roth's program, not a departure from it.

---
*Source: [PWG/prefaces/](https://github.com/sanskrit-lexicon/PWG/tree/master/prefaces)
(German + English + Russian). Dates from the title pages and foreword signatures;
volume letter-ranges and the remaining precise dates are on the per-volume title
pages (`pwgpref12/17/20/22/25/26`).*
