# «Санскрит в цифрах» — Wave 1: five NEW module datasets

_Created: 13-07-2026 · Last updated: 13-07-2026_

> Executes Wave 1 of [ROADMAP_SANSKRIT_IN_NUMBERS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/ROADMAP_SANSKRIT_IN_NUMBERS_2026_2027.md)
> under handoff [H813](https://github.com/gasyoun/Uprava/blob/main/handoffs/H813-Sonnet_SanskritLexicography_sanskrit_in_numbers_wave1_new_modules_12.07.26.md).
> Five modules, each with a reproducible generator script and a committed dataset. This is
> the portrait's own scholarly novelty (§5 anti-salami: modules 2/7 are cited elsewhere, see
> [MODULES_OWNED.md](MODULES_OWNED.md)).

## Module 5 — akṣara / phoneme frequency

**Source · n · date:** Petersburg family (PWG+PWK+SCH) headwords, `HeadwordLists/now-2026/`
key1/key2 SLP1, n=285,950 headwords · DCS-2026 corpus tokens, n=5,688,416 · 13-07-2026 ·
Sonnet 5 (`claude-sonnet-5`). Generator: [module5_akshara_phoneme_freq.py](module5_akshara_phoneme_freq.py).

Reports BOTH layers because sandhi makes them diverge — the module's core finding, with no
German counterpart:

| Layer | Family top-5 | DCS-corpus top-5 |
|---|---|---|
| **Phonemic** (SLP1 char = 1 phoneme) | a (24.2%), r (6.7%), A (6.4%), i (5.2%), t (4.9%) | a (21.2%), A (7.2%), t (7.0%), r (5.3%), i (5.0%) |
| **Graphemic** (Devanagari akṣara) | न (3.8%), र (3.6%), क (3.6%), अ (2.9%), म (2.7%) | म (5.5%), त (4.4%), अ (3.6%), न (3.0%), व (2.6%) |

Totals: family = 2,572,557 phonemes / 1,187,061 akṣaras; DCS corpus = 32,067,704 phonemes /
15,084,217 akṣaras. The phonemic and graphemic rankings genuinely diverge (e.g. `a` dominates
phonemically but no single akṣara dominates as heavily graphemically) — a direct, quantified
demonstration of sandhi's effect on the written vs. spoken/phonemic layer that Duden's German
letter-chart has no equivalent for. Full histograms (top-40 each): [module5_akshara_phoneme_freq.json](module5_akshara_phoneme_freq.json).

## Module 6 — longest compounds (samāsa)

**Source · n · date:** DCS-2026 corpus, `token.form` surface forms, n=381,413 distinct forms
(91,726 meeting the ≥5-occurrence honesty floor) · 13-07-2026 · Sonnet 5 (`claude-sonnet-5`).
Generator: [module6_longest_compounds.py](module6_longest_compounds.py).

| | Form | Occurrences | Char length | Akṣara length |
|---|---|---|---|---|
| **Record (≥5-occurrence floor)** | *sāgaravaradharabuddhivikrīḍitābhijñasya* | 5 | 39 | 16 |
| No-floor "record" (hapax) | *vyādhavākyopadeśakathanapūrvakadānādiphalavarṇanaṃ* | 1 | 50 | — |

The floor matters exactly the way Duden's own methodology intends: without it, a one-off
colophon-title string sets an unrepresentative 50-character "record"; with the same
≥5-occurrence discipline Duden applies to German's 79-character *Bandwurmwort*, Sanskrit's
honest record is 39 characters / 16 akṣaras. Full top-50 + length distribution:
[module6_longest_compounds.json](module6_longest_compounds.json).

**Method note:** "compound" here = longest attested single orthographic word (Duden's own
unit for the *Bandwurmwort* record), not a formally verified samāsa parse — see Module 9 for
why full samāsa segmentation is a separate, harder problem.

## Module 8 — gender distribution

**Source · n · date:** [zaliznyak-grammar-index](https://github.com/gasyoun/kosha/releases/tag/data-v0.1.0)
(A56, kosha), `lex` column, n=98,639 PWG headwords · 13-07-2026 · Sonnet 5 (`claude-sonnet-5`).
Generator: [module8_gender_distribution.py](module8_gender_distribution.py). Reuses an
already-released committed asset (not re-derived from raw PWG markup) — see anti-salami note
in [MODULES_OWNED.md](MODULES_OWNED.md).

| Gender | n | % (of 64,488 gendered nouns) |
|---|---|---|
| Masculine | 35,184 | 54.56% |
| Neuter | 15,112 | 23.43% |
| Feminine | 14,192 | 22.01% |

**Multi-gender headwords** (the Sanskrit *der/die/das Joghurt* analog): **482** headwords
(0.74% of gendered nouns) attested with more than one gender — m./n. 459, m./f./n. (tri-gender)
12, m./f. 7, f./n. 4. Non-gendered categories (adj./adv./indecl./interj., 33,662 headwords)
are excluded from the percentage base, since Sanskrit adjectives take the gender of the noun
they modify rather than carrying a fixed dictionary gender — the structural reason Sanskrit's
multi-gender set is dominated by substantivized adjectives, not ordinary nouns, unlike German.
Full breakdown: [module8_gender_distribution.json](module8_gender_distribution.json).

## Module 9 — samāsa types (best-effort, flagged)

**Source · n · date:** DCS-2026 corpus, `token.deprel` UD-style compound relations, n=5,688,416
tokens total (2,214 carrying an explicit compound-member relation) · 13-07-2026 · Sonnet 5
(`claude-sonnet-5`). Generator: [module9_samasa_types.py](module9_samasa_types.py).

| deprel | n | Type |
|---|---|---|
| `compound:coord` | 2,044 | **dvandva (coordinate)** — reliably tagged, not heuristic |
| `compound` | 119 | tatpuruṣa / karmadhāraya / bahuvrīhi, **undifferentiated** |
| `compound:name` | 51 | proper-name compound |

**Explicitly flagged best-effort, per the roadmap.** DCS's own UD-style tagging gives a
reliable, corpus-native **dvandva** count (`compound:coord`) — this is not a guess. But the
much larger tatpuruṣa/bahuvrīhi distinction is **not** auto-classified: the UD `compound`
relation used by DCS does not carry that distinction, and inventing percentages for it via
unverified heuristics would risk fabricating data. A random 15-item sample per bucket is
included in the dataset for a future dedicated segmentation pass (vidyut `cheda` + hand
adjudication) to type — that full typing pass is a follow-up, not delivered here. **Scale
caveat:** only 0.039% of all DCS tokens carry an explicit compound-member deprel at all — most
Sanskrit compounds in this corpus remain single, undecomposed orthographic words (see Module
6), so this module describes the tagged minority, not the full compound population. Full
detail: [module9_samasa_types.json](module9_samasa_types.json).

## Module 10 — verb classes (gaṇa) + voice

**Source · n · date:** [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots)
`Whitney_roots_class-PP.txt` (Whitney 1885 digitized classification), n=857 roots, for gaṇa;
`src/paradigms.json` (vidyut-prakriya 0.4.0 generated paradigms), n=419 roots corroborated,
for voice · 13-07-2026 · Sonnet 5 (`claude-sonnet-5`). Generator:
[module10_verb_class_voice.py](module10_verb_class_voice.py).

**Gaṇa (primary class, 689 classified roots; 168 unclassified/no attested class):**

| Gaṇa | I | II | IV | VI | III/V/VII/VIII/IX (each) |
|---|---|---|---|---|---|
| % | 71.99% | 7.11% | 8.85% | 6.53% | 1.89% / 1.31% / 0.73% / 0.29% / 0.73% |

Class I dominates at **72%** — the direct Sanskrit analog of Duden's "weak verbs 76.7%",
structurally similar in magnitude though for a different reason (thematic-vowel regularity
vs. German's weak/strong conjugation split). 244 roots (35.4% of classified roots) belong to
more than one gaṇa (see `gana_membership_pct` in the dataset for the full multi-class
picture).

**Voice (pada), 419 vidyut-corroborated roots (NOT extrapolated to all 857):**

| Pada | n | % |
|---|---|---|
| Parasmaipada | 256 | 61.10% |
| Ātmanepada | 86 | 20.53% |
| Ubhayapada | 77 | 18.38% |

A cleaner structural analog of German's *haben/sein* auxiliary split than German's own
(irregular, historically accreted) list — Sanskrit's P/A/U split is a live grammatical
category assigned to every verb root, not a lexical residue. **Cross-reference, cited not
re-measured:** WhitneyRoots' own corpus-vs-Whitney gaṇa agreement measurement (857
DCS-attested roots, 85.5% agreement) lives in that repo's `corpus_verdict_summary.txt`.
Full detail: [module10_verb_class_voice.json](module10_verb_class_voice.json).

---

## Reproducibility

Every script reads only already-committed sibling-repo data (VisualDCS, WhitneyRoots, kosha
release, this repo's HeadwordLists) — no manual/uncommitted inputs. Re-run any module with
`python module<N>_<name>.py` from this directory; each writes its own `.json` and prints its
headline numbers to stdout.

_Dr. Mārcis Gasūns_
