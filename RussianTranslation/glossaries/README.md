# Renou register glossaries

Register-specific vocabulary lists extracted from the Renou-tagged dictionaries by
[`../src/renou_glossary.py`](../src/renou_glossary.py). Each glossary is the set of
headwords tagged with one Renou **register** (a subsection of the *Histoire de la langue
sanskrite* — see [`RENOU.md`](../RENOU.md) and
[VisualDCS/docs/Renou_1956_structure.md](https://github.com/gasyoun/VisualDCS/blob/main/docs/Renou_1956_structure.md)),
aggregated by IAST headword across all 8 dictionaries (PWG, MW, PW, AP, AP90, BEN, SCH,
BHS). Each row gives the **states** the word spans, the register **provenance**
(`ls` = a lexicographer cited a source of that register · `dcs` = corpus attestation),
the **dictionaries** that attest it, and the **sense** count.

These are **derived snapshots** — regenerate with `renou_glossary.py`, don't hand-edit.

| Glossary | Register | Headwords | Note |
|---|---|--:|---|
| [`epigraphic_vocabulary.md`](epigraphic_vocabulary.md) | `epig` | 709 | **484 (68 %) are corpus-absent** — see below |
| [`bhasya_glossary.tsv`](bhasya_glossary.tsv) | `bhasya` | 14,498 | commentary language; 10,320 in ≥2 dicts (robust) |
| [`jaina_vocabulary.md`](jaina_vocabulary.md) | `jaina` | 286 | Jaina Sanskrit (all via MW's Jaina sigla) |

## Why the épigraphic list matters

**68 % of the épigraphic vocabulary (484 of 709 words) has *no* DCS-corpus attestation
at all** — these headwords live only in inscriptions, so a corpus-only method never sees
them. The list surfaces exactly that: donative/administrative terms (`akṣayanīvī`
"perpetual endowment"), monastery names (`abhayagirivihāra`), and the dynastic
onomasticon of the inscriptions (`ajayavarman`, `akkādevī`, `akabara` = Akbar). This is
the clearest demonstration that the register axis adds signal the state axis cannot:
épig is the one register whose words are largely *outside* the literary timeline.

## Regenerate / make your own

```sh
cd ../src
python renou_glossary.py epig   --format md  --out ../glossaries/epigraphic_vocabulary.md
python renou_glossary.py bhasya --format tsv --out ../glossaries/bhasya_glossary.tsv
python renou_glossary.py jaina  --format md  --out ../glossaries/jaina_vocabulary.md

# any register, with filters — e.g. kāvya poetic words attested in ≥3 dictionaries:
python renou_glossary.py kavya --min-dicts 3 --format md
# cross-axis — Vedic (I) words the commentaries kept alive:
python renou_glossary.py bhasya --state I --format md
# a state glossary instead of a register one:
python renou_glossary.py I --state-only --format tsv
```

Registers: see `renou_register.REGISTERS` (rgveda · atharva · yajus · brahmana ·
upanisad · sutra · vyakarana · **epig** · epic · purana · tantra · smrti · karika ·
**bhasya** · katha · natya · kavya · bauddha · jaina · hors_inde).
