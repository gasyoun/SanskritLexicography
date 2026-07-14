# Where the Russian meanings come from — provenance & traceability

When you read a Russian gloss in a generated card, it has **one of two origins**.
Knowing which — and, for corpus ones, *which text* — is what lets you judge a change
instead of guessing.

## The two sources of a Russian rendering

1. **Corpus-attested** — the Russian is a word that actually appears as the published
   translation of this Sanskrit form in a parallel Sanskrit↔Russian corpus. These are
   the translator's *primary* evidence (the portrait's `corpus_synonyms`/`candidates`).
   **Every such word is traceable to an exact text and verse.**
2. **German-governed (B&R gloss)** — for forms the corpus does not attest (most split
   prefixed verbs: the portrait marks them `evidence_scope = root-fallback`), the Russian
   is translated from Böhtlingk-Roth's German gloss, with the corpus candidates demoted to
   a weak hint. These have **no corpus passage** — by design.

A card's per-sense `source_type` (`attested` vs `lexicographic`) and the portrait's
`evidence_scope` tell you which case you're in. Example from the `gam` run: `nyā+gam` →
«нисходить к» is **German-governed** (`evidence_scope=root-fallback`; «нисходить» has zero
corpus attestations), whereas a Vedic `gam` form like `gamemahi` is **corpus-attested**.

## The ground truth: `corpus_lexicon.jsonl`

The candidates are mined from [`src/corpus_lexicon.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_lexicon.jsonl)
— 1,091,528 word-aligned Sa→Ru pairs (derived from the
[SamudraManthanam](https://github.com/gasyoun/SamudraManthanam) parallel corpus). **Each
pair carries full provenance:**

```json
{"work":"01_atharvaveda","passage":"1.4","slp1":"gamemahi","sa":"gamemahi",
 "ru":"соединимся","genre":"Veda — Saṃhitā","period":"Vedic (Brāhmaṇa–Upaniṣad)","date":-940}
```

`work` + `passage` = the exact text and verse; `period`/`date` = the stratum. **The
portrait drops `work`/`passage`** (it keeps only the bare Russian word, grouped by
stratum), which is why a card alone doesn't show its source — the link has to be recovered
from the lexicon.

## Two tools to recover it

- [`src/corpus_provenance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_provenance.py)
  — no dependencies beyond the lexicon; works for **any** form, root, or reverse Russian
  lookup. Each rendering → count, period span, and the `text:passage`(s) attesting it.
  ```
  python src/corpus_provenance.py gamemahi          # gamemahi → соединимся (AV 1.4), повстречаться (RV 81.2)…
  python src/corpus_provenance.py --root gam         # every SLP1 form containing 'gam'
  python src/corpus_provenance.py --ru нисходить      # reverse — here: "no corpus attestations" (= German-derived)
  ```
- [`src/_build_corpus_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_build_corpus_ru.py)
  — richer, **DB-backed**: joins the lexicon loci to `SamudraManthanam/web/corpus.db` to
  print the actual **verse pair + the published Russian translation it's quoted from**
  (Елизаренкова РВ/АВ, academic Mahābhārata, …). Currently wired for 4 flagship headwords
  (agni, anya, akṣara, ananta); generalize its `WORDS` map to document any headword that
  way. Requires the SamudraManthanam sibling repo. **This corpus's Elizarenkova text is
  grey-rights** (not cleared for redistribution, per `SamudraManthanam/README.md`) — it
  stays internal to that application, never surfaced in a public artifact.

## RV citation witness (VedaWeb, CC BY 4.0 — distinct from the corpus above)

[`src/vedaweb_ru_witness.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/vedaweb_ru_witness.py)
([H361](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H361-Sonnet_SanskritLexicography_vedaweb_elizarenkova_ru_witness_08.07.26.md))
looks up Elizarenkova's published Russian rendering by **RV location**
(`mandala.hymn.stanza`), reading the committed
[`VisualDCS/non-derived/vedaweb/elizarenkova_ru_1989_1999.json`](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/vedaweb/elizarenkova_ru_1989_1999.json)
feed (10,552 stanzas, sibling repo). This is a **different source and a different rights
posture** from the `_build_corpus_ru.py` DB above: VedaWeb (Universität zu Köln) holds an
explicit written CC BY 4.0 grant for this specific hosted resource (confirmed 08-07-2026,
see the feed's own README), so it is committed openly — the SamudraManthanam copy is not,
and the two must never be conflated when citing "Elizarenkova via this org."

```
python src/vedaweb_ru_witness.py 1.1.1          # one stanza
python src/vedaweb_ru_witness.py --hymn 1.1     # every stanza in a hymn
python src/vedaweb_ru_witness.py --citation     # full bibliographic citation
```

**Advisory/citation-context only** — this is a lookup tool, not a data pipeline. It is
meant to be run by hand (or from an ad-hoc script) when a PWG/MW headword's RV citation
would benefit from the published Russian rendering as scholarly context. Nothing it
returns is ever written into `headword_index.tsv` or any other reviewed store data —
per the org's I/VI accent-collapse lesson, external corpus/translation data stays
read-only and advisory everywhere.

## So, to answer "why is this Russian here?"

1. Check the sense's `source_type` / the portrait `evidence_scope`.
2. If corpus-grounded: `python src/corpus_provenance.py <form>` → the text:passage(s).
   For the published verse + translator, use `_build_corpus_ru.py` (needs `corpus.db`).
3. If `root-fallback` / `lexicographic`: it's translated from the **German gloss**; the
   corpus shows nothing for that surface form (the bare root's candidates were a hint only).

**Open improvement:** carry the top loci (`work:passage`) into the portrait's
`corpus_synonyms` so each card can cite its corpus source inline — then step 2 becomes
unnecessary. Tracked as a follow-up.

## Renou register layer (attestation-level)

The corpus stores no Renou register tag, but its `genre` resolves onto the canonical
20-register lattice (`renou_register.REGISTERS`). [`src/renou_corpus_map.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_corpus_map.py)
bridges them — it **reuses** `renou_register._genre_register` and adds only a work-slug
override (RV vs AV Saṃhitā, Buddhist kāvya) and a supplement for corpus-only genres
(Upaniṣad, commentary, darśana, tantra, kāma). Every attestation thus gets an
*attestation-level* register (distinct from the *headword-level* `*.renou.jsonl`).

- Per-meaning register: `python src/corpus_provenance.py <form> --renou` tags each rendering
  with its register(s) and prints a register profile for the query. E.g. `gamemahi` →
  «соединимся» [`atharva`] (AV 1.4), «повстречаться» [`rgveda`] (RV 81.2).
- Corpus-wide register count stats: `python src/renou_corpus_map.py`. Over all 1,091,528
  aligned pairs: **epic 61.0 %, rgveda 14.4 %, atharva 5.6 %, kavya 3.9 %, smrti 3.6 %,
  upanisad 3.5 %, karika 2.6 %, katha 2.0 %, tantra 1.2 %, bhasya 1.2 %, bauddha 1.1 %**
  (full coverage — no unmapped genres).

This makes "which register does this Russian meaning belong to?" answerable per sense,
grounded in real parallel-corpus usage rather than the dictionary's `<ls>` sigla — a layer
to build register-distribution / register×period analyses on.
