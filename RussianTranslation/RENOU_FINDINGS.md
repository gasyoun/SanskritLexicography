# Renou register axis — findings register

Empirical findings from the two-axis tagging ([`RENOU.md`](RENOU.md)), beyond the
headline épigraphique result of [`papers/A34_renou_register_note.md`](../../papers/A34_renou_register_note.md).
Each is marked **[source]** (grounded in Renou's text) or **[data]** (measured over the
8 Renou-tagged dictionaries). The per-register metrics behind them:

| register | N | corpus-absent | 1-dict | mean states | ≥4 states |
|---|--:|--:|--:|--:|--:|
| rgveda | 15,370 | 0.0 % | 16.4 % | 2.19 | 23.4 % |
| atharva | 8,512 | 0.0 % | 14.9 % | 2.56 | 33.4 % |
| yajus | 11,015 | 0.0 % | 12.5 % | 2.51 | 31.4 % |
| brahmana | 16,562 | 0.0 % | 15.1 % | 2.49 | 30.1 % |
| upanisad | 4,831 | 0.0 % | 10.6 % | 3.44 | 56.7 % |
| sutra | 18,893 | 0.4 % | 11.8 % | 2.63 | 32.4 % |
| vyakarana | 22,429 | 0.0 % | 10.6 % | 2.40 | 26.6 % |
| epig | 709 | **63.0 %** | 26.2 % | 0.93 | 10.0 % |
| epic | 48,713 | 0.0 % | 21.7 % | 2.11 | 15.8 % |
| purana | 31,255 | 0.0 % | 13.1 % | 2.48 | 23.5 % |
| tantra | 5,416 | 0.0 % | 4.5 % | 3.64 | 57.3 % |
| smrti | 17,546 | 0.0 % | 18.5 % | 2.71 | 31.9 % |
| karika | 3,021 | 0.9 % | 4.1 % | 3.80 | **65.0 %** |
| bhasya | 14,498 | 0.8 % | 8.8 % | 2.86 | 36.1 % |
| katha | 24,393 | 0.0 % | 15.3 % | 2.42 | 24.9 % |
| natya | 12,611 | 0.4 % | 23.8 % | 2.55 | 29.8 % |
| kavya | 26,973 | 0.0 % | 19.8 % | 2.31 | 22.2 % |
| bauddha | 25,740 | 12.4 % | **44.5 %** | 2.01 | 22.8 % |
| jaina | 286 | 0.0 % | 13.6 % | 2.38 | 23.8 % |

> *corpus-absent* = headwords carrying the register but with **no** DCS state (off the
> literary timeline). *1-dict* = headwords only one of the 8 dictionaries records (a
> dictionary-specificity / coinage fingerprint). *mean states* / *≥4 states* = era-spread:
> how many Renou states the headword spans (high = era-neutral, low = period-bound).

---

## F1. bhāṣya is a cross-disciplinary *syntactic* register — **[source, confirmed]**

The hypothesis that bhāṣya is privileged as "śāstric Sanskrit" — a hard-syntax register
that cuts across topics — is **Renou's own thesis**. *Histoire*, p. 133 (chap. IV opening,
"Le commentaire (*bhāṣya*) de type ancien"):

> « L'aspect extérieur en a été **durci** par le long entraînement au genre « sūtra », par
> l'accentuation progressive du « **style nominal** » … [devenu] un instrument monotone
> mais puissant de raisonnement, d'interprétation, de dialectique, **approprié à servir
> d'expression doctrinale à tous les types de problèmes et de disciplines**. »

and p. 139 ("Caractère linguistique du bhāṣya"):

> « La prédominance du style nominal s'est affirmée … **plus vite et plus complètement que
> dans le style littéraire** ; le verbe personnel n'est plus qu'un outil accessoire … »

Renou's linguistic markers: rarefied finite verbs; agent-nouns in `-aka`, action-nouns in
`-ana`, abstract derivatives in `-tā / -tva`; long compounds. So bhāṣya is the one register
Renou defines by **syntax/style** rather than by text-genre, and explicitly as serving *all
disciplines*. This is a principled special status — not arbitrary elevation — and it
coexists with treating the 20 registers equally by default.

**[data] corroboration.** bhāṣya's 1-dict rate is **8.8 %** — among the *lowest* of all
literary registers (vs kāvya 19.8 %, nāṭya 23.8 %, epic 21.7 %). A register whose vocabulary
is **standardised across dictionaries**, not idiosyncratic — exactly what a cross-
disciplinary technical instrument should be. (*Next sources to check, per the plan:* Tubb &
Boose, *Scholastic Sanskrit*; Speijer's syntax; a finite-verb-density count on a real
bhāṣya sample vs a kāvya sample.)

## F2. bauddha (BHS) is a **second self-contained lexical world** — **[data]**

After épig, the next register with notable corpus-absence is **bauddha (12.4 %)**, and it
has by far the **highest 1-dict rate of all twenty: 44.5 %**. The cause is precise: of its
11,454 single-dictionary headwords, **10,511 (92 %) are recorded only by BHS** — Edgerton's
*Buddhist Hybrid Sanskrit Dictionary*. BHS is, lexically, its own world: ~10,500 headwords
no mainstream Sanskrit dictionary carries, and an eighth of the register attested in no DCS
text. This parallels the épig finding by a different mechanism — épig is vocabulary *outside
the corpus* (inscriptions), BHS is vocabulary *outside the standard dictionaries* (a hybrid
register one lexicographer catalogued) — and is a second case where a register recovers a
stratum the mainstream sources miss.

## F3. The doctrinal registers carry the **perennial** lexicon; narrative/poetic the **period-bound** — **[data]**

Era-spread (≥4-states %) splits the registers cleanly:

- **Most era-neutral:** kārikā **65.0 %**, tantra **57.3 %**, upaniṣad **56.7 %** — the
  philosophical/doctrinal registers. Their vocabulary (`ātman`, `brahman`, `tattva`, the
  abstract `-tā/-tva` terms) is the **perennial** lexicon, in active use across every period.
- **Most period-bound:** épig 10.0 %, epic 15.8 %, kāvya 22.2 %, bauddha 22.8 % — the
  narrative, poetic, and documentary registers, whose vocabulary is tied to their own era.

So the register axis predicts era-spread: a word's *discourse-type* tells you how
period-specific its vocabulary is. The cleanest case is upaniṣad (genuine philosophical
core); tantra/kārikā corroborate (small, doctrinal, dcs-only registers of abstract terms).

## F4. nāṭya and kāvya are the **coinage** registers — **[data]**

Among the literary registers, dictionary-specificity (1-dict %) ranks nāṭya **23.8 %**,
epic 21.7 %, kāvya 19.8 % at the top, and the śāstric registers — bhāṣya 8.8 %, vyākaraṇa
10.6 %, tantra 4.5 %, kārikā 4.1 % — at the bottom. The performative and poetic registers
**grow and individualise** the lexicon (ornament, synonymy, drama-specific vocabulary one
dictionary records and the next does not); the technical/doctrinal registers **standardise**
it. This is the same conservation-vs-invention axis seen in the cross-axis slices
([`RENOU_CROSSAXIS.md`](RENOU_CROSSAXIS.md) §1–2), now read off the register metrics directly.

---

## Reproducibility

Metrics computed over the canonical `{code}.renou.jsonl` (per-headword union across the 8
dictionaries; `renou_register.REGISTERS`). Renou quotations: *Histoire de la langue
sanskrite* (1956), pp. 133, 139 — scan in
[VisualDCS/docs](https://github.com/gasyoun/VisualDCS/tree/main/docs), print→PDF offset −7.
These findings feed the A34 data note and may seed a follow-on on register-predicted
era-spread.
