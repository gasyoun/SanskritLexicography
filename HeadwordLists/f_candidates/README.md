# f_candidates/ — item-F alternate & feminine headword worklists

Machine-generated *candidate* lists for [PRINT_READINESS.md](../PRINT_READINESS.md) item
**F**, summarised in [ALTERNATE_HEADWORDS.md](../ALTERNATE_HEADWORDS.md). Produced by
[`../alternate_headwords.py`](../alternate_headwords.py) from the 2026 key1 sets in
[`../now-2026/`](../now-2026/). Per dictionary `<D>` (currently MW, SKD):

| file | columns | what it is |
|---|---|---|
| `<D>_fem_masc.tsv` | fem_slp1, fem_iast, masc_slp1, masc_iast | a feminine stem **and** its masculine base both headworded (`-ā↔-a`, `-inī↔-in`, `-ī↔-in`) |
| `<D>_orphan_fem.tsv` | slp1, iast | `-ā/-ī/-inī` stems with **no** masculine base headworded (mostly inherent feminines) |
| `<D>_variants.tsv` | a_slp1, a_iast, b_slp1, b_iast | both forms headworded, differing by `b~v`, `ś~ṣ`, or geminate~single |
| `<D>_multi_k2.tsv` | forms_slp1, forms_iast | one entry listing several alternate forms (negligible — MW/SKD = 0) |

**These are candidates to filter, not decisions to apply.** The pairing is
morphological-shape based, so it includes semantic non-pairs (e.g. `ā`↔`a`) and
coincidental homographs the editor must drop. The fold/keep/merge policy is human.
Regenerate for any dict: `python alternate_headwords.py <DICT>`.
