# Cross-axis slices — where Renou's state and register axes compose

The two Renou axes — diachronic **state** (I–V) and **register** (the 20 subsections,
[`RENOU_REGISTERS.md`](RENOU_REGISTERS.md)) — are orthogonal, so their **intersections and
differences** name strata neither axis can name alone. This note works through the most
revealing of them: for each, what it is, how it breaks down, real headwords (glosses abridged from the **Monier-Williams** entry), and what it
tells us. Companion to the data note [`papers/A34_renou_register_note.md`](../../papers/A34_renou_register_note.md).

**Counting convention.** Each slice's **headline count is the reproducible figure** printed
by the `renou_glossary.py` command shown — distinct headwords (by IAST) where the condition
holds *within a sense* (the same entry carries the register and meets the state condition),
aggregated across the 8 dictionaries (PWG · MW · PW · AP · AP90 · BEN · SCH · BHS). The
**anatomy** figures below (co-registers, dict-spread) are computed at the **headword level**
across all of a word's senses and are *indicative* — they may sum to a slightly different
total than the headline, since a word can carry one register in one sense and another in a
second. Run the command to reproduce the exact set. The glossary extractor gained
`--and-register` / `--not-register` for the register intersections used here.

**Dict-spread** (how many of the 8 dictionaries attest a headword) is the slice's robustness
fingerprint: a slice dominated by 1-dict headwords is specialised/obscure; one spread across
6–8 dicts is core shared vocabulary.

---

## 1. Vedic-in-commentary — `bhāṣya ∩ I` — 6,895 headwords

> *The vocabulary the commentarial tradition kept teaching.* Words first attested in the
> Veda (state I) that resurface in the commentary register.

`renou_glossary.py bhasya --state I`

**Anatomy.** Heavy co-occurrence with `purāṇa` (5,529), `epic` (5,473), `sūtra` (5,362),
`smṛti`, `kāvya` — i.e. these are the **long-lived core**: words present in every later
stratum, not Vedic curiosities. Dict-spread is broad (only 296 are single-dict (of ~7,016 headword-level);
2,323 reach ≥6 dictionaries). This is the opposite of an obscure slice — it is the
load-bearing lexicon.

| headword | gloss | spans |
|---|---|---|
| `mārga` | seeking, tracing (fr. *mṛga* "game"); path, way; (later) method | I → IV |
| `sārathi` | a charioteer, driver of a car | I → III |
| `siṃha` | "the powerful one", a lion (RV.) | I → IV |
| `lāṅgala` | a plough (RV.) | I → IV |
| `hutāśana` | "oblation-eater", fire | I → IV |
| `sapatnī` | co-wife, rival | I → IV |

**Reading.** The bhāṣya register is, lexically, a **Vedic reservoir**: the commentators
keep a Vedic word in active use centuries after its source text, because their whole task is
to gloss older texts. A word like `lāṅgala` or `hutāśana` would look "Vedic" on the state
axis alone, but the register axis shows it never went out of *use* — it went out of
*composition* and survived in *exegesis*. The two axes together separate "old" from "obsolete."

## 2. Born-in-kāvya — `kāvya ∖ I` — 20,758 headwords

> *The coinage engine.* Poetic-register words with **no** Vedic attestation — vocabulary that
> first surfaces in classical poetry.

`renou_glossary.py kavya --exclude-state I`

**Anatomy.** Co-occurs with `epic` (8,244) and `katha` (5,681) but the tell is the
**dict-spread**: roughly a quarter (5,073) are single-dict, far more than slice 1 — a long tail
of specialised, ornamental, often *hapax-feeling* coinages that one dictionary records and
the next does not. These are abstract nouns, bahuvrīhi epithets, and rare ornamental synonyms.

| headword | gloss | note |
|---|---|---|
| `vāñchā` | wish, desire, longing for | classical; the Veda used `kāma` |
| `sthairya` | firmness, solidity, steadfastness | abstract `-ya` derivative |
| `udbhūti` | coming forth, appearance, origin | |
| `sūcita` | pointed out, indicated, hinted | the *dhvani* poetics vocabulary |
| `rogahṛt` | disease-curing | classical compound (medical/poetic) |

**Reading.** Where slice 1 is conservation, this is **invention**. Classical poetry is the
register that *grows* the lexicon — abstract nominalisations for poetic theory (`sūcita`,
`dhvani`-adjacent), and an explosion of synonym-ornament. The ~25 % single-dict rate
quantifies the well-known impressionistic claim that kāvya vocabulary is vast, dictionary-
specific, and only partly shared.

## 3. Epic-in-commentary — `epic ∩ bhāṣya` — 8,118 headwords

> *The most-glossed stratum.* The single largest register∩register intersection in the
> lattice: epic vocabulary that the commentaries take up.

`renou_glossary.py epic --and-register bhasya`

**Anatomy.** Co-registers `purāṇa` (7,210), `kathā`, `kāvya`, `smṛti` — the whole
epic-and-after continuum. Dict-spread is broad (only 301 single-dict; 2,729 in ≥6 dicts):
this is mainstream narrative-and-didactic vocabulary, the words a commentator on the
Mahābhārata or a Dharmaśāstra actually needs to explain.

| headword | gloss |
|---|---|
| `guṇa` | a thread, strand; quality; merit; (gram.) vowel grade |
| `lakṣaṇa` | mark, sign, characteristic; (śāstra) definition |
| `viveka` | discrimination, distinction |
| `daiva` | divine, of the gods; (n.) fate, destiny |

**Reading.** That epic∩bhāṣya is the largest commentary intersection (larger than
vyākaraṇa∩bhāṣya, §4) reflects what the commentarial industry mostly *was*: exegesis of the
epic-Purāṇic-Dharmaśāstric corpus. Words like `guṇa` and `lakṣaṇa` sit at the hinge — ordinary
in the epic, technical in the śāstra the commentary serves.

## 4. The grammatical meta-language — `vyākaraṇa ∩ bhāṣya` — 6,931 headwords

> *Language about language about language.* Words belonging to **both** the grammarians'
> normative register and the commentary register — the vocabulary of the
> Mahābhāṣya/Kāśikā-vṛtti, a commentary that is itself grammatical.

`renou_glossary.py vyakarana --and-register bhasya`

**Anatomy.** Co-occurs with the general literary registers (`epic` 4,062, `purāṇa` 3,975)
because the grammarians' *examples* are ordinary words; the slice is the union of technical
terms and their illustrative vocabulary. 502 single-dict.

| headword | gloss |
|---|---|
| `dvaṃdva` | pair; **(gram.) copulative compound** |
| `guṇa` | **(gram.) the a/e/o vowel grade**; quality |
| `kartṛka` | (ifc.) having (such) an agent |

**Reading.** This slice isolates Sanskrit's most reflexive layer: `dvaṃdva` is the perfect
specimen — a word that *names a grammatical category* and is *defined in a grammatical
commentary*. The intersection makes the indigenous metalinguistic vocabulary queryable as a
set, which the citation-register papers (A08/A18) approach from the MW side.

## 5. Buddhist poetry — `bauddha ∩ kāvya` — 5,999 headwords

> *Cross-tradition vocabulary.* Words in **both** the Buddhist register and the poetic
> register — the lexicon of Buddhist kāvya (Aśvaghoṣa's *Buddhacarita*, *Saundarananda*).

`renou_glossary.py bauddha --and-register kavya`

**Anatomy.** Strong co-occurrence with `epic`/`purāṇa`/`kathā` — Buddhist poetry draws on
the shared classical poetic lexicon, not a separate vocabulary. Dict-spread broad (235
single-dict; 2,411 in ≥6). `bhāṣya` co-occurs 4,232 (Buddhist scholastic commentary).

| headword | gloss |
|---|---|
| `sugata` | going well; (m.) **the Buddha** ("well-gone") |
| `megha` | "sprinkler", a cloud (RV.) |
| `candra` | shining, bright; (m.) the moon |
| `vihaṃgama` | moving in the sky, flying; (m.) a bird |
| `gadgada` | stammering, stuttering (with emotion) |

**Reading.** The slice quantifies that Buddhist Sanskrit poetry is **lexically classical** —
`sugata` is the rare register-marked term (an epithet that is Buddhist *and* poetic), but
`megha`, `candra`, `gadgada` show the Buddhist poet writing in the common kāvya idiom. Where
the state axis would flatten an Aśvaghoṣa word to "V," the register pair shows it living in
two registers at once.

## 6. The inscription-only onomasticon — `épig ∖ corpus` — 484 headwords

> *Outside the literary timeline entirely.* The épigraphique headwords with **no** Renou
> state at all — attested only in inscriptions, never in the literary corpus (the A34
> headline, here anatomised).

`renou_glossary.py epig --exclude-state I,II,III,IV,V`

**Anatomy.** **No co-registers** — by construction, `épig` is their only register and they
carry no state. The dict-spread is the surprise: only 174 are single-dict; **172
appear in three dictionaries** and 94 in two — the inscriptional onomasticon is *shared*
lexicographic knowledge (MW, AP, and PW all harvest the same epigraphic corpora), not a
one-dictionary quirk.

| headword | gloss | type |
|---|---|---|
| `vākāṭaka` | N. of a family of princes (the Vākāṭaka dynasty) | dynasty |
| `cālikya` | = Cālukya (Inscr., dated 489 A.D.) | dynasty |
| `kṛṣṇarāya` | N. of various kings | ruler |
| `humāuṃ` | Humāyūn (emperor) | ruler (Indo-Persian) |
| `durgāvatī` | N. of a princess | ruler |

**Reading.** This is the slice that only the register axis can produce: a word attested
solely in an undated inscription has **no definable Renou state** (no literary text dates
it) yet a perfectly definite register. It is overwhelmingly an **onomasticon** — dynasties,
kings, queens, places — including the Indo-Persian layer (`humāuṃ`, `premasāhi`) that the
literary corpus never records. For an epigraphist this slice is a ready vocabulary; for the
theory it is the proof that register ≠ period, because here register exists *in the absence*
of period.

---

## Synthesis — what the composed axes show

| Slice | One-line finding |
|---|---|
| `bhāṣya ∩ I` | the commentary register is a **Vedic reservoir** — old ≠ obsolete |
| `kāvya ∖ I` | classical poetry is the **coinage engine** (~a quarter dictionary-specific) |
| `epic ∩ bhāṣya` | the **largest** commentary intersection — exegesis was mostly of the epic-Purāṇic corpus |
| `vyākaraṇa ∩ bhāṣya` | the indigenous **metalinguistic** vocabulary, as a queryable set |
| `bauddha ∩ kāvya` | Buddhist poetry is **lexically classical** — two registers at once |
| `épig ∖ corpus` | an **onomasticon outside the timeline** — register with no period |

The recurring lesson is that the **state axis alone conflates distinctions the register axis
recovers**: "Vedic" splits into *obsolete* (slice 0, pure archaism) vs *conserved-in-commentary*
(slice 1); "Classical" splits into *inherited* vs *coined-in-kāvya* (slice 2); and a whole
stratum (slice 6) has register but no period. Evidence-graded lexicography needs both
coordinates because meaning, currency, and discourse-type are three different facts about a
word.

## Reproducibility

All slices above are regenerable with [`src/renou_glossary.py`](src/renou_glossary.py) using
the printed commands (`--state` / `--exclude-state` / `--and-register` / `--not-register`).
Anatomy (co-registers, dict-spread) is computed over the canonical `{code}.renou.jsonl`. See
[`RENOU.md`](RENOU.md) for the tagging system and [`RENOU_REGISTERS.md`](RENOU_REGISTERS.md)
for the register catalog.
