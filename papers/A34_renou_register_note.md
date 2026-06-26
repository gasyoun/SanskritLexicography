# Register, not just period: Renou's subsections as an orthogonal axis for evidence-graded Sanskrit lexicography — and the inscriptional vocabulary that corpus methods miss

**A34 · research note / short communication · draft 2026-06-26 · target: Lexikos / IJL / eLex**

> **Status:** full first draft (3/5). Tagging built, audited, and reproducible across
> eight dictionaries; needs a related-work paragraph, one external validation pass on
> the épigraphique sample, and a venue decision before submission.

## Abstract

Louis Renou's *Histoire de la langue sanskrite* (1956) is routinely reduced, in digital
work, to **five language-states** (I Vedic · II Pāṇinian · III Epic · IV Classical ·
V Buddhist/Jaina) — the book's five chapters. But Renou's chapters are themselves divided
into **subsections that are registers, not periods**: the *bhāṣya* (commentary language)
opens the Classical chapter and is given *its own grammar* ("Caractères linguistiques du
bhāṣya", p. 139); *le sanskrit épigraphique* is filed inside the Pāṇinian-norm chapter
(p. 94) as a witness to *real attested usage* against the grammarians' ideal. A flat I–V
tag cannot express either. We operationalise **both** axes — a diachronic **state** axis
(I–V) and an orthogonal, multi-label **register** axis (a 20-code lattice of Renou's
subsections) — and apply them to **770,292 entries across eight machine-readable Cologne
dictionaries**, each tag carrying its evidential provenance (lexicographer's citation /
corpus attestation / register membership). The headline result is a structural one: of
**709 headwords tagged épigraphique, 484 (68 %) have no attestation in the literary
corpus at all** — they exist only in inscriptions (`akṣayanīvī` "perpetual endowment",
monastery names, the dynastic onomasticon). The register axis recovers a stratum that
both the corpus and the period axis structurally miss. We release the tagger and eight
register glossaries.

## 1. The problem

Diachronic tagging of Sanskrit lexicon entries has converged on Renou's five states,
treated as a period scale. This is useful but lossy in a specific way: **register
cross-cuts period**. A commentary (*bhāṣya*) can gloss a Vedic, epic, or classical base
text; its language — terse, formulaic, meta-textual — is a register of its own that does
not reduce to "Classical". Inscriptional Sanskrit is, for Renou, not a period at all but
a documentary *witness*, deliberately placed beside the discussion of the spoken norm.
Reading the actual *table des matières* (transcribed in
[VisualDCS/docs/Renou_1956_structure.md](https://github.com/gasyoun/VisualDCS/blob/main/docs/Renou_1956_structure.md))
makes the gap concrete: the Classical chapter alone holds four distinct registers
(*bhāṣya*, *kathā* narrative, the *théâtre* dialogue, *kāvya* poetry), and the
Pāṇinian-norm chapter hosts the épigraphique witness. None of these is a fifth, sixth, or
seventh *state*; they are an orthogonal dimension.

## 2. Method

We tag every dictionary sense on **two independent axes**, each multi-label (a word can
carry several values) and each value carrying a provenance set:

- **State (I–V)** — Renou's five chapters. Three deterministic signals plus a tertiary
  one: the entry's own `<ls>` **citation** resolved through a curated siglum→state map;
  **DCS-corpus** attestation (the lemma's occurrence across the Digital Corpus of
  Sanskrit, each text typed to a state by genre/name/date); **Edgerton's BHS** set
  membership for V; and a partial **wisdomlib** tradition tag.
- **Register** — a 20-code lattice of Renou's subsections, built from the *same* two
  primary signals plus dedicated detectors: a genre/name→register map over the corpus
  texts (commentary caught by name-stems `*bhāṣya/ṭīkā/vṛtti/vārttika`, since the corpus
  has no commentary *genre*); the `<ls>` siglum's source genre/name (the only route to
  **jaina** and a second signal for *bhāṣya*); and a **dedicated épigraphique detector**
  — an inscription marker (PWG German `Inschr.`, MW/Apte `Inscr.`) inside any citation,
  the sole route to a register the corpus contains none of.

Both axes share one noise-control policy. The corpus index is **lossless** — it stores,
per lemma, the per-state and per-register evidence depth `{n_texts, confidence}` — and a
**min-support filter** is applied at tagging time: a corpus state is kept only if
attested in ≥2 texts *or* in one authoritatively-typed text, which prunes the thin
date-fallback tail (9.9 % of corpus state-assignments; **0 %** of states II and V, which
come only from typed sources). The two axes are kept in **disjoint vocabularies and
separate fields**; an independent data-integrity audit confirmed entry-count invariance,
provenance coherence across 1.43 M register assignments, and zero leakage between axes.

The substrate is the Cologne Digital Sanskrit Lexicon (`csl-orig`) — PWG, MW, PW, AP,
AP90, BEN, SCH, BHS — and the DCS 2026 corpus snapshot.

## 3. Results

### 3.1 Coverage

The register axis is populated across all eight dictionaries (19–100 % of entries carry
≥1 register; BHS is 100 %, every entry being Buddhist). The commentary register is large
and robust — *bhāṣya* tags **14,498 distinct headwords** (10,320 attested in ≥2
dictionaries); the poetic and Buddhist lexica reach 26,973 (*kāvya*) and 25,740
(*bauddha*). Nineteen of the twenty lattice registers are populated; only *hors-de-l'Inde*
(Sanskrit abroad) is empty, having no source in either signal.

### 3.2 The headline: épigraphique is largely corpus-invisible

| Register | Distinct headwords | Corpus-absent (no DCS attestation) |
|---|--:|--:|
| **épigraphique** | **709** | **484 (68 %)** |
| jaina | 286 | 0 |
| bhāṣya | 14,498 | (corpus-rich) |

Sixty-eight per cent of the épigraphique vocabulary has **no literary-corpus attestation
whatsoever**. These are the words a corpus-only diachronic method never sees: donative and
administrative terms (`akṣayanīvī` "perpetual, non-confiscable endowment"), monastery names
(`abhayagirivihāra`), and above all the dynastic onomasticon engraved in stone
(`ajayavarman`, `akkādevī`, `akabara` = Akbar). The contrast with *jaina* (0 % corpus-absent
— Jaina-tagged words are literary words MW happens to cite from Jaina sources) sharpens the
point: épigraphique is the one register whose vocabulary lies **outside the literary
timeline**, and it is recoverable only because the lexicographers preserved the
inscription citation. This is the clearest demonstration that the register axis carries
signal the state axis, by construction, cannot: a word attested only in an undated
inscription has *no* well-defined Renou state, yet a perfectly definite register.

### 3.3 Composing the two axes

Because state and register are orthogonal, their intersection and difference define
editorially meaningful strata that neither axis alone can name:

| Slice | Definition | Headwords | What it is |
|---|---|--:|---|
| Vedic-in-commentary | register `bhāṣya` ∩ state I | 6,895 | Vedic vocabulary the commentarial tradition kept alive |
| born-in-kāvya | register `kāvya` ∖ state I | 20,758 | poetic words with no Vedic attestation (`abdhi` "ocean" vs Vedic *samudra*) |
| pure archaisms | state I only | 25,220 | words dropped after the Saṃhitās |

The full coordinate per sense is `(state, register, provenance)` — e.g. *akṣobhya* =
`III·V` / `purāṇa·tantra·bauddha` / all-signals — an evidence-graded position, not a
single label. Six such slices are worked through in detail — with quantitative anatomy
and glossed examples — in
[`RENOU_CROSSAXIS.md`](../RussianTranslation/RENOU_CROSSAXIS.md): the bhāṣya register as a
**Vedic reservoir**, kāvya as a **coinage engine** (≈¼ of its words dictionary-specific),
the *dvaṃdva*-type **grammatical meta-language** (vyākaraṇa∩bhāṣya), **Buddhist poetry**
(bauddha∩kāvya, *sugata* etc.), and the inscription-only **onomasticon** (épig∖corpus:
*vākāṭaka*, *humāuṃ* = Humāyūn) — register in the *absence* of period.

### 3.4 What does *not* need correcting

The min-support filter that prunes the state axis is, on the register axis, a **no-op by
construction**: a register only ever derives from a *typed* source (a corpus genre, a
curated siglum, an inscription marker), so no register rests on the low-confidence
date-fallback texts that produce state-axis noise. Register quality therefore rides on the
genre/name confidence floor, not on a frequency gate — a result of the audit, not an
assumption.

## 4. Consequence

For an evidence-graded digital dictionary, the register is a second per-sense badge,
independent of the period badge, and the two compose into a queryable coordinate rather
than a flat label. Two concrete payoffs: (1) **reusable register lexica** — we ship eight
glossaries (épigraphique, *bhāṣya*, *kāvya*, *bauddha*, *jaina*, plus the three cross-axis
slices of §3.3), each a deduplicated, provenance-tagged headword list; the épigraphique
list is, in effect, a ready feed of inscriptional Sanskrit vocabulary for epigraphists.
(2) **honest negative coverage** — the 68 % corpus-absent figure is itself a finding about
the limits of corpus-driven lexicography, and the tagging makes that gap measurable
instead of invisible.

## 5. Reproducibility

Tagger and resolvers:
[`src/renou.py`](../RussianTranslation/src/renou.py),
[`src/renou_register.py`](../RussianTranslation/src/renou_register.py),
[`src/build_dcs_renou.py`](../RussianTranslation/src/build_dcs_renou.py),
[`src/tag_dict_from_source.py`](../RussianTranslation/src/tag_dict_from_source.py).
Audit and display: [`src/renou_audit.py`](../RussianTranslation/src/renou_audit.py),
[`src/renou_portrait.py`](../RussianTranslation/src/renou_portrait.py). Glossary extractor
and the eight shipped glossaries:
[`src/renou_glossary.py`](../RussianTranslation/src/renou_glossary.py),
[`glossaries/`](../RussianTranslation/glossaries/README.md). System overview:
[`RENOU.md`](../RussianTranslation/RENOU.md); register design:
[`RENOU_SUBSECTIONS_PLAN.md`](../RussianTranslation/RENOU_SUBSECTIONS_PLAN.md); the
source-book structure: [Renou 1956 TOC](https://github.com/gasyoun/VisualDCS/blob/main/docs/Renou_1956_structure.md).
Derived indices (`{code}.renou.jsonl`) are gitignored and regenerated by
`renou_pipeline.py --all`.

## To do before submission

- Related work: position against the citation-register literature (this project's own
  A08/A18 on the two MW citation registers), Renou reception, and digital-philology
  register tagging; cite Vogel's *Indian Lexicography* and Edgerton (BHS) directly.
- External validation: hand-check a sample of the 709 épigraphique headwords against a
  published inscription corpus (EI / CII) to estimate the inscription-marker detector's
  precision and recall — the one number a referee will ask for.
- Broaden the inscription detector beyond the `Insch?r` marker (it is deliberately
  conservative); report the recall ceiling honestly.
- Decide venue (Lexikos vs IJL vs eLex) and trim to length; fold the method figure from
  RENOU.md.
