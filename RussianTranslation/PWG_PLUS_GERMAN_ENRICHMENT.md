## PWG++ — gluing the derivable research layers onto the German original (H772)

_Created: 12-07-2026 · Last updated: 12-07-2026_

**The question this answers.** Which research layers are *cheap and derivable* in
parallel with the Russian translation, and can they be attached not only to the
Russian but to the **original German** PWG source — glued together on one spine?

**The answer, now built.** Every derivable layer keys on the **SLP1 lemma
(`key1`)**, not on the Russian. The Russian translation is just *one* consumer
hanging off that spine; the German source is another. So the same layer set
enriches the German original as cheaply as it enriches the Russian, and the two
become **sibling `ontolex:LexicalEntry` nodes on one shared `lemma/<key1>` node** —
literally glued. This is emitted by a new `de-lexicon` mode of
[`src/export_lod.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_lod.py)
as a **separate** graph
([`release/fixture/pwg_de_lexicon.ttl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/fixture/pwg_de_lexicon.ttl)
for the fixture) that federates on the same lemma IRI as the RU lexical graph and
the DCS-frequency graph — the same LiLa-style lemma-bank pattern the RU export
already used, extended to a second language.

### The cheap derivable layers (parallel to, and independent of, translation)

None of these calls the translate/judge workflow; each is deterministic or a
one-time flat-rate join, and each keys on the headword — so each attaches to the
German entry, the Russian entry, or (via the shared lemma) both.

| Layer group | Source / script | Keys on | Now on the German entry? |
|---|---|---|---|
| Source structure — homonym + numbered/lettered sense tree, per-sense German gloss, `<lex>` POS | [`src/microstructure.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/microstructure.py) + [`src/pwg_mask.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py) `restore` | the German PWG markup | **Yes** — the German sense body |
| `<ls>` literary-source citations (98.9% of 571,632 loci resolved) | [`src/build_citation_index.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_citation_index.py), [`src/pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py) | German source | **Yes** — `dct:references` → `pwglex:Citation` |
| Renou register / dated stratum axis | [`src/annotate_renou.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_renou.py), `pwg_sense_stratum.jsonl` | lemma + sense_no | **Yes** — `pwglex:renouStratum` + the **shared** `pwglex:attestation` node |
| Diasystem / grammar-usage `<ab>` labels | [`src/pwg_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab.py) | German source | **Yes** — `pwglex:diasystem` |
| DCS corpus frequency + bands (5.69M tokens) | [`src/build_dcs_freq.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dcs_freq.py) | lemma | **Yes** — via the shared lemma (`dcs_freq.ttl` join) |
| Whitney root + nominal grammar, Zaliznyak index | [`src/whitney_grammar.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/whitney_grammar.py), [`src/nominal_grammar.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nominal_grammar.py) | lemma | Next graph (slots on the same lemma, like DCS freq) |
| Learner CEFR band, Hindi/Latin/kośa sense signals, etymology | [`src/build_learner_scores.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_learner_scores.py), [`src/build_indic.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_indic.py), [`src/build_meulenbeld.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_meulenbeld.py) | lemma | Next graphs (same pattern) |

### What the German entry carries (built)

A first-class German `ontolex:LexicalEntry` per PWG homograph card
(`entry/<key1>[-N]/de`), sourced from the **full ~120k** `assembled_cards.jsonl`
(the German source), **not** the ~11.5k translated subset — so the German
dictionary is decoupled from how far the Russian translation has reached. Per
sense (`ontolex:LexicalSense`, graded `gr:pwg-source`, public domain, citable):

- `skos:definition …@de` + `pwglex:germanEquivalent …@de` — B&R's own gloss(es);
- `pwglex:senseNumber` / `pwglex:senseSub`, `pwglex:equivalenceType`,
  `pwglex:grammar` (POS from `<lex>`);
- `pwglex:diasystem`, `pwglex:renouStratum`;
- `dct:references` → each `<ls>` as a first-class `pwglex:Citation`;
- `pwglex:attestation` → the **same** dated `pwglex:StratumAttestation` node the
  Russian sense uses (shared enrichment, not a copy).

The German entry's `ontolex:canonicalForm` is the shared `lemma/<key1>` node, so
the DCS-frequency graph enriches it with **zero** extra work.

### Reuse, not reinvention

The German sense split is **not** re-implemented: `de_card_senses()` restores the
masked source via `pwg_mask.restore` (the lossless placeholder round-trip) and
reuses `microstructure.split_senses` / `sense_node` — the same deterministic parse
the Apresjan portrait uses. The lemma-bank spine, IRI minting, citation
extraction and stratum loader are reused from the existing RU emitter.

### Run it

```
# German enrichment graph (separate .ttl, joins on the shared lemma IRI)
python src/export_lod.py de-lexicon --out-dir release
# fixture regen (byte-stable) + acceptance gate (RU + DE + DCS-freq federated)
python src/export_lod.py de-lexicon --keys rakz,a,aMSa,aMSaka \
  --generated-at 2026-07-08 --out-dir release/fixture
python src/lod_acceptance.py
```

The acceptance gate
([`src/lod_acceptance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/lod_acceptance.py))
gained block **C**: the three-way federated join (German sense × its `<ls>`
citation × the DCS frequency of the shared lemma) returns rows; every German
entry is language-tagged and lemma-anchored; RU and DE entries provably sit on the
same lemma; German sense count matches source; and the German graph regenerates
byte-identical. The RU + DCS graphs remain byte-identical (existing B1 unchanged).

### Verified (fixture, Opus 4.8 `claude-opus-4-8`, 12-07-2026)

| Check | Result |
|---|---|
| German entries / senses (4 fixture headwords, homographs split) | 12 entries / 34 senses |
| Three-way join (DE entry × citation × DCS freq on shared lemma) | 25 rows, 4/4 headwords |
| Lemmas carrying RU + DE sibling entries | 4/4 |
| German sense count vs source | 34 = 34 |
| Robustness (first 2000 source cards) | 1999 entries / 3146 senses, valid Turtle (109,887 triples) |

### Backlog

- Emit the grammar layer (`whitney_grammar` / `nominal_grammar`) as its own graph
  on the lemma spine (identical pattern to `dcs_freq.ttl`).
- Publish the full German graph as a standalone **PWG++** artifact (rights are
  clean — B&R is public domain); the RU graph's publication-domain `@DECIDE`
  (base IRI) is shared, see
  [`LOD_GRAPH.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LOD_GRAPH.md).
- `owl:sameAs` the shared lemma to a real Sanskrit LiLa lemma bank when one exists.

_Dr. Mārcis Gasūns_
