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

### Register glossaries (one register each)

| Glossary | Register | Headwords | Note |
|---|---|--:|---|
| [`epigraphic_vocabulary.md`](epigraphic_vocabulary.md) | `epig` | 709 | **484 (68 %) are corpus-absent** — see below |
| [`bhasya_glossary.tsv`](bhasya_glossary.tsv) | `bhasya` | 14,498 | commentary language; 10,320 in ≥2 dicts (robust) |
| [`kavya_lexicon.tsv`](kavya_lexicon.tsv) | `kavya` | 26,973 | the poetic lexicon |
| [`bauddha_glossary.tsv`](bauddha_glossary.tsv) | `bauddha` | 25,740 | Buddhist Sanskrit vocabulary |
| [`jaina_vocabulary.md`](jaina_vocabulary.md) | `jaina` | 286 | Jaina Sanskrit (all via MW's Jaina sigla) |

### Cross-axis & state slices (the two axes composed)

| Glossary | Filter | Headwords | What it isolates |
|---|---|--:|---|
| [`vedic_in_commentary.tsv`](vedic_in_commentary.tsv) | `bhasya` ∩ state `I` | 6,895 | Vedic words the commentarial tradition kept alive |
| [`kavya_born_in_classical.tsv`](kavya_born_in_classical.tsv) | `kavya` ∖ state `I` | 20,758 | poetic vocabulary with **no** Vedic attestation — born in kāvya |
| [`vedic_only_archaisms.tsv`](vedic_only_archaisms.tsv) | state `I` only | 25,220 | words attested **only** in Vedic — pure archaisms |

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
# the register glossaries above
python renou_glossary.py epig    --format md  --out ../glossaries/epigraphic_vocabulary.md
python renou_glossary.py bhasya  --format tsv --out ../glossaries/bhasya_glossary.tsv
python renou_glossary.py kavya   --format tsv --out ../glossaries/kavya_lexicon.tsv
python renou_glossary.py bauddha --format tsv --out ../glossaries/bauddha_glossary.tsv
python renou_glossary.py jaina   --format md  --out ../glossaries/jaina_vocabulary.md

# cross-axis & state slices (the two axes composed)
python renou_glossary.py bhasya --state I --format tsv                      # Vedic-in-commentary
python renou_glossary.py kavya  --exclude-state I --format tsv              # born in kāvya (no Vedic)
python renou_glossary.py I --state-only --exclude-state II,III,IV,V --format tsv  # Vedic-only archaisms

# your own — e.g. cited (ls-only) kāvya words attested in ≥3 dictionaries:
python renou_glossary.py kavya --prov ls --min-dicts 3 --format md
```

Registers: see `renou_register.REGISTERS` (rgveda · atharva · yajus · brahmana ·
upanisad · sutra · vyakarana · **epig** · epic · purana · tantra · smrti · karika ·
**bhasya** · katha · natya · kavya · bauddha · jaina · hors_inde).
