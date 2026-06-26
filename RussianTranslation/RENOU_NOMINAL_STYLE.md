# Nominal vs verbal style — Renou's thesis, measured on the corpus

Renou's *Histoire de la langue sanskrite* (1956) makes the **rise of the nominal style at
the expense of the finite verb** its central diachronic claim. That claim is about *running
text*, so — unlike the register tags, which sit on headwords — it can be **verified directly**
on the POS-annotated DCS corpus. This note states what Renou says, defines the measure, and
reports the result. Tool: [`src/nominal_style.py`](src/nominal_style.py).

## 1. What Renou says

The nominal style is a through-line of the book, sharpest in the commentary section
(chap. IV, "Caractère linguistique du bhāṣya", pp. 133, 139):

> p. 133 — « L'aspect extérieur en a été **durci** par le long entraînement au genre « sūtra »,
> par l'accentuation progressive du « **style nominal** » … [devenu] un instrument monotone
> mais puissant de raisonnement … Les exercices linguistiques « abstraits » se sont intensifiés :
> noms d'agent en *-aka*, noms d'action en *-ana*, dérivés abstraits en *-tā / -tva*, composés
> longs, **raréfaction des formes personnelles du verbe**. »

> p. 139 — « La prédominance du style nominal s'est affirmée … **plus vite et plus complètement
> que dans le style littéraire** ; le verbe personnel n'est plus qu'un outil accessoire … »

Three testable predictions follow: **(P1)** finite ("personal") verbs grow *rarer* over time
(Vedic → Classical); **(P2)** the rarefaction is *most extreme* in the śāstra / sūtra /
bhāṣya register, exceeding even the literary (kāvya) style; **(P3)** the verbal idea is
carried instead by **participles** and action-nouns — so as finite verbs fall, participles
and nominals rise.

## 2. What we can measure

The DCS 2026 CoNLL-U gives UPOS + morphology per token. DCS marks a **finite verb** as
`UPOS=VERB` with a `Mood=` / `Person=` feature and *no* `VerbForm`; participles carry
`VerbForm=Part`, absolutives/infinitives `VerbForm=Conv|Inf`. So:

- **finite-verb density** = finite verbs / all tokens — the direct measure of P1/P2;
- **participle density** and **noun+adj density** — the nominalisation mechanism (P3).

Each DCS text is typed to a Renou **state** and **register** by the same map the tagger uses
(`build_dcs_renou.build_text_states`). Figures are corpus-weighted (token totals).

## 3. Result — P1: finite verbs fall across the states

| State | texts | **finite-verb %** | participle % | noun+adj % | tokens |
|---|--:|--:|--:|--:|--:|
| **I** Vedic | 67 | **14.40** | 3.93 | 44.2 | 1.29 M |
| II Pāṇinian | 2 | 1.79 | 1.70 | 74.0 | 18 k* |
| **III** Epic | 44 | 8.33 | 6.88 | 53.1 | 2.51 M |
| **IV** Classical | 144 | **6.66** | 6.20 | 58.8 | 1.63 M |
| V Buddhist | 12 | 8.41 | 6.99 | 50.7 | 0.24 M |

Finite-verb density **more than halves** from Vedic (14.4 %) to Classical (6.7 %); over the
same span participles rise 3.9 → 6.2 % and noun+adj 44 → 59 %. **P1 and P3 confirmed**: the
finite verb recedes and the participle/nominal advances, exactly the trade-off Renou
describes. (*State II = only the two grammar texts in DCS — a real but tiny sample; see §5.*)

## 4. Result — P2: bhāṣya out-nominalises the literary style

Finite-verb density by register, most-nominal first:

| Register | finite-verb % | | Register | finite-verb % |
|---|--:|---|---|--:|
| vyākaraṇa* | 1.79 | | smṛti | 8.12 |
| nāṭya | 5.23 | | bauddha | 8.41 |
| **bhāṣya** | **6.25** | | epic | 8.78 |
| kārikā | 7.37 | | **sūtra** | **12.55** |
| tantra | 7.44 | | upaniṣad | 13.21 |
| **kāvya** | **7.48** | | rgveda | 13.90 |
| purāṇa | 7.54 | | brāhmaṇa | 14.99 |
| kathā | 8.05 | | yajus | 16.70 |

**bhāṣya (6.25 %) sits below kāvya (7.48 %)** — the commentary register is *more* nominal
than the literary style, the precise wording of Renou p. 139. The per-text extremes make it
vivid (finite-verb %, ≥500 tokens):

- **most nominal:** Nyāyasūtra 0.18 · Yogasūtra 0.26 · Aṣṭādhyāyī 0.57 · Vaiśeṣikasūtra 1.50 ·
  Tarkasaṃgraha 1.57 · Abhidharmakośa 2.02 · Amarakośa 2.52 + the nighaṇṭu lexicons (~1–2 %)
  — i.e. exactly the **philosophical-sūtra, grammar, scholastic and kośa** texts;
- **most verbal:** Taittirīyasaṃhitā 18.48 · Taittirīyabrāhmaṇa 18.47 · Vājasaneyisaṃhitā 16.61
  · the Śrautasūtras and Brāhmaṇas (16–18 %) — the **Vedic Saṃhitā/Brāhmaṇa** prose.

A ~50–100× gap between the scholastic floor (Nyāyasūtra 0.18 %) and the Vedic ceiling
(Taittirīyasaṃhitā 18.5 %). **P2 confirmed**, and the texts that anchor the nominal floor are
precisely the ones Renou names.

## 5. Caveats (so a referee can't)

- **State II / vyākaraṇa = 2 texts** (Aṣṭādhyāyī + one) — the lowest finite-verb point is
  real (grammar *is* maximally nominal) but the *aggregate* rests on a tiny sample; do not
  read it as a stage average.
- **The "sūtra" *register* is verbal (12.55 %) — not a contradiction.** That register is
  dominated by the **Vedic ritual** śrauta/gṛhya-sūtras (state I, 16 %+), whereas the
  **classical philosophical** sūtras (Nyāya-, Yoga-, Vaiśeṣika-sūtra) are the nominal floor
  but type to III/IV and to other registers. The measure thus *separates two things both
  called "sūtra"* — the verbal Vedic ritual sūtra from the nominal darśana-sūtra — which is
  itself a result.
- **Corpus-weighted:** large texts dominate a stratum (Epic III ≈ MBh+Rām). A per-text-mean
  variant is one flag away (`agg_by` already keeps `n_texts`).
- **DCS tagging** (Hellwig) is the ground truth; finite = `VERB`+`Mood/Person`, no `VerbForm`.

## 6. Use cases

- **Diachronic dating signal.** Finite-verb density is a cheap, language-internal estimate of
  a text's "nominal-ness," hence a soft register/date probe for an *unattributed* passage —
  complementary to lexical dating.
- **Register classification.** The finite-verb / participle / noun ratios are features for
  classifying a text's register (śāstra vs narrative vs Vedic) without metadata.
- **Translation calibration (`pwg_ru`).** A bhāṣya-register card should be rendered in terse,
  nominal Russian; a Vedic or epic card tolerates finite verbs — the measure says *how
  nominal* the target register actually is, quantitatively.
- **Teaching.** A concrete, quantified illustration of "Sanskrit nominalises over time" for a
  syntax course — the Nyāyasūtra-vs-Taittirīyasaṃhitā contrast (0.18 % vs 18.5 %).
- **Reader UX.** Pair the Renou register badge with a "nominal-style" indicator on long
  passages, derived from the same corpus.

## 7. Status of the other "after" sources

The finite-verb count (this note) is the empirical leg of the verification and is **done**.
The two book sources flagged earlier are **external and not held locally** (no clean web
fetch from this environment), so they remain to-cite, not yet read:

- **Tubb & Boose, *Scholastic Sanskrit* (2007)** — the standard handbook of commentarial
  (bhāṣya) syntax; its catalogue of nominal constructions (the *iti*-clause, the abstract in
  *-tva*, the *bahuvrīhi* gloss) is the qualitative counterpart to §4. *To read + cite.*
- **Speijer, *Sanskrit Syntax* (1886)** — §§ on the predominance of the participle and the
  passive over the finite verb; the classical baseline against which to read P1. *To read + cite.*

When their texts are available, the move is to map their named constructions onto the
morphological counts here (e.g. Speijer's "participle for finite verb" ↔ the participle-rise
of §3).

## Reproduce

```sh
cd RussianTranslation/src
python nominal_style.py          # state + register finite-verb tables (corpus scan ~2-3 min)
python nominal_style.py --texts  # per-text finite-verb %, lowest first
```
See [`RENOU_FINDINGS.md`](RENOU_FINDINGS.md) (F1, F5) and the data note
[`papers/A34_renou_register_note.md`](../../papers/A34_renou_register_note.md).
