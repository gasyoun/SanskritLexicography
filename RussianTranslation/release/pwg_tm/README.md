# PWG TM canonical v1 — four-format FAIR pack (H2685)

_Created: 14-08-2026 · Last updated: 14-08-2026 (Zenodo concept 10.5281/zenodo.21932900)_

Immutable interchange pack for the **2,392** publication-grade PWG German→Russian
translation-memory records (2,175 exact cards + 217 exact fragments). Canonical
JSONL is the source; TMX 1.4b, TEI Lex-0 and OntoLex-Lemon/vartrans/PROV-O are
derived. Rebuild with
[`src/pwg_tm_release.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_release.py).

## Formats

| File | Role | SHA-256 (see [SHA256SUMS](SHA256SUMS)) |
|---|---|---|
| `canonical.v1.jsonl` | lossless store | `b9ad8e9ff99d561de72029e9af40664e9cf7bfabe1575faf7858d88b757bbe82` |
| `pwg_tm.de-ru.tmx` | TMX 1.4b | `aecc76d0f4423067061da5b22da205179860333eb59df92b8a92dba076f3853a` |
| `pwg_tm.tei.lex0.xml` | TEI Lex-0 | `e4741f69ade8810e8cf76920896d416635c2b4fc523fdffc9510c5efbab653e7` |
| `pwg_tm.ontolex.ttl` | OntoLex + vartrans + PROV-O | `5a89ebf6c0e7eff680072200b52ce06428a156e5a23b247cf28e0e321179c398` |

The four binaries are gitignored (regenerable). GitHub Release
`pwg-tm-canonical-v1.0.0` carries the bytes. Tracked here:
[manifest.json](manifest.json), [coverage.json](coverage.json),
[loss_ledger.json](loss_ledger.json), [SHA256SUMS](SHA256SUMS),
[DATASHEET.md](DATASHEET.md), [CITATION.cff](CITATION.cff),
[LICENSE-DATA](LICENSE-DATA).

## Coverage denominators (do not collapse)

| Denominator | Value |
|---|---|
| Green publication records in this pack | **2,392 / 2,392** lossless |
| Indexed PWG headwords | 98,639 (94,074 unique k1) |
| Wave-1 frozen queue | 5,000 unique k1 (`f024ec4b0b2e58f7…`) |
| Wave-1 fragments accounted | 753,111 / 753,111 |
| Wave-1 promoted / quarantine | 655,332 / 97,779 |
| Wave-1 independent n=400 | fidelity 99.5% · equivalence 95.5% · serious error **2.5%** (floor fail) |

Wave-1 promoted fragments are **not** in the four-format green files. They stay
in the H2684 receipt as evidence, not as a published interchange.

## Rights (publish-safety GO)

- PWG German source: 19th-century public domain (Böhtlingk–Roth).
- Russian renderings: this project's own machine translation of that PD source.
- No confirmed prohibition, restricted designation, privacy exposure, or
  secrets. Rights uncertainty is recorded, not a stop.
- Data licence: CC BY 4.0. See [LICENSE-DATA](LICENSE-DATA).

DOI (verified 14-08-2026 against the live record, title and file sizes match):
**concept** [10.5281/zenodo.21932900](https://doi.org/10.5281/zenodo.21932900)
(cite this) · **version 1.0.0**
[10.5281/zenodo.21932901](https://doi.org/10.5281/zenodo.21932901).
This is a **dataset** DOI, not the repository software concept
[10.5281/zenodo.21306715](https://doi.org/10.5281/zenodo.21306715).
The four interchange files were not rewritten.

## Prove

```text
python src/pwg_tm_migrate_v1.py --verify
python src/build_tmx.py validate release/pwg_tm/pwg_tm.de-ru.tmx
python src/export_pwg_tm_tei.py --validate
python src/export_pwg_tm_ontolex.py --validate-shacl
python src/pwg_tm_export_loss.py --all-formats
```

14-08-2026 (Grok 4.6 `grok-4.6`): 2,392 TMX units; 953 TEI entries / 2,392
senses; SHACL pass; **0** unaccounted scholarly fields (153,088 checks).

_Dr. Mārcis Gasūns_
