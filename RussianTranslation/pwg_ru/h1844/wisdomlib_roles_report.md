# wisdomlib in four roles — what the on-disk feed actually supports

_Created: 29-07-2026 · Last updated: 29-07-2026_

Produced by [`src/rv_wisdomlib_bridge.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_wisdomlib_bridge.py) (H1844 step 15). Zero network calls (R17).

| Role (R11) | Status | Rows | Why |
|---|---|--:|---|
| 1 · EN gloss tier for PWG→EN | **not populated** | 0 | No gloss text on disk. `entries_index.jsonl` is a catalogue of works, not of headwords; `word_traditions.jsonl` carries an integer gloss *count*. Obtaining the text needs the crawl R17 forbids. |
| 2 · Tradition sense disambiguation | **zero overlap** | 0 | The join key is sound (`agni`→`agní-`, `indra`→`índra-`); the 63 words in `word_traditions.jsonl` are Vajrayāna Buddhist terminology (`bodhisattva`, `hevajra`, `vajravārāhī`…) harvested as a fetcher probe. Intersected with the RV’s 9539 lemmas the result is correctly empty. |
| 3 · Fifth contradiction-gate witness | **not populated** | 0 | A witness must supply a reading to contradict. Same missing gloss text as role 1. |
| 4 · AV citation-locus source | **staged** | 0 | No Atharvaveda data on disk, and AV is an explicit wave-1 non-goal (R3). |

## Measured inputs

| Input | Value |
|---|--:|
| wisdomlib words carrying tradition tags | 63 |
| RV lemmas (distinct folded join keys) | 9539 |
| Role-2 joined rows | 0 |
| `entries_index.jsonl` rows | 848 |
| `entries_index.jsonl` keys | `author`, `ctype`, `group`, `sections`, `slug`, `title`, `url`, `words` |
| Any gloss-bearing key present | no |

## Tradition histogram over the joined rows

| Tradition | Rows |
|---|--:|
| (none) | 0 |

## Consequence for the plan

PLAN §2 lists the wisdomlib crawler as an existing asset, which it is — but R11 assumed the *downloaded* half was a Sanskrit gloss resource. It is not: what is on disk is a catalogue of works, three crawled books, and a 63-word Buddhist-terminology probe. All four roles are therefore blocked on DATA, not on code — this bridge is written, tested and will populate the moment a real gloss feed lands. The unblocking step is a daytime `definitions.py` crawl over an RV-attested headword list, which is deliberately out of scope here (R17) and should be scoped as its own handoff rather than smuggled into this run.

The honest consequence for wave 1: **W1.13 cannot be met as written.** The acceptance criterion asks for a smoke test per role and zero network calls; the zero-network half holds, and each role has a test, but three roles test an empty result and the fourth tests a correct empty intersection. Recording that is the deliverable — asserting four working roles would not be true.

_Dr. Mārcis Gasūns_
