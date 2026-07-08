# Renou register axis — findings register

_Created: 26-06-2026 · Last updated: 03-07-2026_

Empirical findings from the two-axis tagging ([`RENOU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md)), beyond the
headline épigraphique result of [`papers/A34_renou_register_note.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A34_renou_register_note.md).
Each is marked **[source]** (grounded in Renou's text) or **[data]** (measured over the
8 Renou-tagged dictionaries). The per-register metrics behind them:

> ⚠️ **Staleness (03-07-2026):** this table is a hand-copy from an earlier DCS-index
> generation and needs regeneration from `renou_audit.py` (indices via
> `renou_pipeline.py --all`). Known defect: the **epig corpus-absent cell reads 63.0 %,
> but the committed glossary gives 484/709 = 68.3 %** — verified in
> [`papers/A34_corpus_absent_verification.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A34_corpus_absent_verification.md);
> the paper (A34) carries the correct 68.3 %. Until the regen, trust the glossaries over
> this table wherever they disagree, and re-check bauddha's 12.4 % in the same pass.

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

**[data] corroboration — two independent measures.**
(a) *Lexical:* bhāṣya's 1-dict rate is **8.8 %** — among the *lowest* of all literary
registers (vs kāvya 19.8 %, nāṭya 23.8 %, epic 21.7 %): a vocabulary **standardised across
dictionaries**, exactly what a cross-disciplinary technical instrument should be.
(b) *Syntactic (corpus):* the finite-verb-density count (now done — see F5 /
[`RENOU_NOMINAL_STYLE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_NOMINAL_STYLE.md)) puts bhāṣya at **6.25 %** finite verbs,
**below kāvya (7.48 %)** — confirming Renou's exact p. 139 claim that the nominal style
asserts itself in bhāṣya "plus complètement que dans le style littéraire." (*External
sources still to read + cite:* Tubb & Boose, *Scholastic Sanskrit*; Speijer's syntax.)

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
([`RENOU_CROSSAXIS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_CROSSAXIS.md) §1–2), now read off the register metrics directly.

## F5. The finite verb recedes across the states — Renou's nominalisation, measured — **[source + data]**

Renou's central diachronic thesis — the **personal/finite verb is progressively replaced by
a nominal style** — is verifiable on running text (not headwords). Measured over the DCS
corpus (finite verb = `VERB` + `Mood/Person`, no `VerbForm`), **finite-verb density more than
halves** across the states: **I 14.40 % → III 8.33 % → IV 6.66 %**, while participles rise
(3.9 → 6.2 %) and noun+adj rise (44 → 59 %) — the exact trade-off Renou names. By register
the nominal floor is the **philosophical-sūtra / grammar / scholastic / kośa** texts
(Nyāyasūtra 0.18 %, Aṣṭādhyāyī 0.57 %, Abhidharmakośa 2.02 %, Amarakośa 2.52 %), the verbal
ceiling the **Vedic Saṃhitā/Brāhmaṇa** (Taittirīyasaṃhitā 18.5 %) — a 50–100× span. Full
study, tables, and caveats (the "sūtra" register is verbal because it is the *Vedic ritual*
sūtra, not the darśana-sūtra): [`RENOU_NOMINAL_STYLE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_NOMINAL_STYLE.md);
tool [`src/nominal_style.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nominal_style.py). This is the strongest single result of
the project: a named 1956 thesis confirmed at corpus scale, with the predicted mechanism
(participle/nominal rise) visible in the same numbers.

## F6. Every 19th/20th-century dictionary under-cites the epic relative to actual usage — **[data]**

H4 (dictionary citation bias): the corpus baseline puts **epic at 61.0%** of all attested
usage — by far the largest register, ~4× rgveda (14.4%), ~16× kāvya (3.9%). Compared
against each dictionary's own `<ls>`-citation register profile (entry-level shares, log2
bias = log2(citation_share / usage_share), 1,000-rep bootstrap CI), **the epic is
under-cited in all 8 dictionaries without exception** — PWG log2 = −1.65, MW −2.24, PW
−4.21, AP −2.54, AP90 −2.34, BEN −0.97, SCH −6.62, BHS −6.86 (all CIs exclude zero).
Rgveda is under-cited in 7/7 dictionaries where the comparison is reachable. Kāvya runs
the other way in 5/8 dictionaries (PWG +1.37, MW +0.26, AP +1.11, AP90 +1.90, BEN +2.13 —
over-cited relative to usage) and under-cited in the 3 sparsest citation profiles (PW,
SCH, BHS). This is a direct, deterministic measurement of Renou's philological-taste
hypothesis: the great narrative bulk of the tradition is comparatively invisible to
19th-century lexicographic citation practice, while classical kāvya is disproportionately
foregrounded in the citation-dense dictionaries. Full tables, method, and limitations
(units differ — entry-level citation vs attestation-level usage; instance-level citation
counts not recoverable from the current tagger index — the acceptance criterion's
cross-unit sign check is partial pending that data):
[RENOU_H4_CITATION_BIAS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_H4_CITATION_BIAS.md);
tool [src/renou_h4_citation_bias.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_h4_citation_bias.py);
figures [research/figures/renou/h4_citation_vs_usage_{dict}.svg](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/research/figures/renou).
Computed by Sonnet 5 (`claude-sonnet-5`).

## F7. `ls`–`dcs` agreement collapses almost as soon as a lemma is attested at all — **[data]**

H6 (Zipf agreement): among 172,845 entries across the 8 canonical dictionaries carrying
both an `<ls>` citation span and a `dcs` corpus span, exact agreement falls from **66.7%**
at the sparsest attested frequencies (~2 DCS texts) to **0.2%** at the densest (~162
texts), while `dcs_adds` (dcs widening the era span beyond `<ls>`) rises in lockstep from
9.3% to 97.8% — monotonic across every bin, no reversal. A fitted logistic curve
(`P(exact) = sigmoid(-2.7315·log10(freq) + 1.1969)`) crosses 50% at **freq ≈ 2.7 DCS
texts** — far earlier than intuition suggests: `dcs_adds` already has better than even
odds of beating an exact `<ls>` match by the time a lemma clears the single-attestation
floor. This gives `renou_low_info`'s current state-count heuristic a principled
frequency-based alternative (recommendation only, no code change this pass — see the doc
for the operating-point tradeoff). Full method, table, and limitations:
[RENOU_H6_ZIPF.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_H6_ZIPF.md);
tool [src/renou_h6_zipf.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_h6_zipf.py);
figure [research/figures/renou/h6_zipf_agreement.svg](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/figures/renou/h6_zipf_agreement.svg).
Computed by Sonnet 5 (`claude-sonnet-5`).

---

## Reproducibility

Metrics computed over the canonical `{code}.renou.jsonl` (per-headword union across the 8
dictionaries; `renou_register.REGISTERS`). Renou quotations: *Histoire de la langue
sanskrite* (1956), pp. 133, 139 — scan in
[VisualDCS/docs](https://github.com/gasyoun/VisualDCS/tree/main/docs), print→PDF offset −7.
These findings feed the A34 data note and may seed a follow-on on register-predicted
era-spread.

_Dr. Mārcis Gasūns_
