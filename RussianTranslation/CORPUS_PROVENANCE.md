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
  way. Requires the SamudraManthanam sibling repo.

## So, to answer "why is this Russian here?"

1. Check the sense's `source_type` / the portrait `evidence_scope`.
2. If corpus-grounded: `python src/corpus_provenance.py <form>` → the text:passage(s).
   For the published verse + translator, use `_build_corpus_ru.py` (needs `corpus.db`).
3. If `root-fallback` / `lexicographic`: it's translated from the **German gloss**; the
   corpus shows nothing for that surface form (the bare root's candidates were a hint only).

**Open improvement:** carry the top loci (`work:passage`) into the portrait's
`corpus_synonyms` so each card can cite its corpus source inline — then step 2 becomes
unnecessary. Tracked as a follow-up.
