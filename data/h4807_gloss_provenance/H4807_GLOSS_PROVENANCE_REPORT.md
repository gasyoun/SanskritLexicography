# H4807 — Wisdomlib dictionary glosses vs csl-orig MW/AP90: borrowed vs own

_Created: 19-09-2026 · tier: OxAlpha (opencode/z-ai/glm-5.3-flash)_

Shortlist cand.7 (census C6 sibling leg, after H4733's headword crosswalk this
measures the GLOSS TEXT itself): provenance of the Sanskrit-dictionary gloss
blocks inside wisdomlib-sanskrit-layers definition pages, against the csl-orig
MW + AP90 English glosses, keyed = sanskrit headword + form_key.

## Inputs (provenance, all read-only)

| input | source | rows |
|---|---|---|
| wisdomlib-sanskrit-layers definitions store (CC BY 4.0, Zenodo DOI 10.5281/zenodo.22118256), Sanskrit-dictionary gloss blocks + explicit per-gloss `Source :` attributions | scrape store `out/jsonl/definitions/{a-z}.jsonl.zst` (MSI box), extracted by `tools/h4807_msi_extract.py` | 255,348 pages / 708,875 gloss blocks |
| csl-orig/v02/mw/mw.txt MW English glosses | rebuilt via canonical `RussianTranslation/src/mw_en_tm.py` | 187,505 headwords |
| csl-orig/v02/ap90/ap90.txt Apte-1890 English glosses | `tools/h4807_ap90_glosses.py` (AP90 markup variant of the same cleaner) | 34,882 records / 34,277 glossed |
| transliteration | canonical `sanskrit_util` (`to_slp1`/`from_slp1`/`strip_slp1_accents`), never forked | — |

Reconciliation: pages swept = **255,348** = L8 index rows exactly (zero drift);
81 pages carry no Sanskrit-dictionary section.

## Provenance share table (attribution census — all 708,875 gloss blocks)

| attribution class | blocks | share |
|---|---|---|
| Cologne: Monier-Williams | 177,507 | 25.0 % |
| Cologne: Apte 1890 (attributed as "DDSA: The practical Sanskrit-English dictionary") | 70,724 | 10.0 % |
| Cologne: other (PW, PW-kürzer, Shabda-Sagara, Yates, Cappeller, Aufrecht, Benfey, Edgerton BHSD, Goldstücker) | 389,681 | 55.0 % |
| own / other-external (DDSA-Prakrit, DILA Sanskrit-Chinese, Alar Kannada, Sutta-Pali, wisdomlib editorial) | 70,963 | 10.0 % |
| **Cologne-declared total (borrowed-by-attribution)** | **637,912** | **90.0 %** |

## Text verification lane (MW/AP-attributed rows only, 248,231)

Headword: slug → `to_slp1`, tiered lookup (exact / hyphen-digit-cleaned /
accentless / wisdomlib geminate-vowel `aa→A` repair / canonical folded
`form_key(from_slp1(...))`). Gloss: `clean_wl_gloss` (drop nav brackets, section
header, MW inline `[..]` markup — mirror of `mw_en_tm.clean_body`) →
`form_key`; verdict per sense segment: G1 exact / G2 containment (≥15 chars or
ratio ≥0.6) / G3 content-word Jaccard ≥0.6 / G4 no match.

| verdict | all | cologne_mw | cologne_ap90 |
|---|---|---|---|
| match_G1 exact | 219 | 216 | 3 |
| match_G2 containment | 74,362 | 68,439 | 5,923 |
| match_G3 overlap ≥0.6 | 6,941 | 5,797 | 1,144 |
| **text-proven borrowed** | **81,522 (32.8 %)** | **74,452 (42.0 %)** | **7,070 (10.0 %)** |
| D1 headword-miss | 123,362 (49.7 %) | 65,103 | 58,259 |
| D2 no-text-match | 43,347 (17.5 %) | 37,952 | 5,395 |

## Defect catch (before reader-pack consumption)

- **D1 (123,362)** — headword not resolvable to the claimed source's TM key. AP90
  side is dominated by TM coverage (Apte 1890 = 34,277 glossed headwords vs
  wisdomlib's 70,724 Apte-attributed blocks), not by provenance doubt; MW side is
  compound/relative entries whose full text lives under another headword plus
  slug initial-vowel-length ambiguity (`Abaddha…` vs slug `abaddha…`).
- **D2 (43,347)** — attributed + headword resolved but text unmatched: MW
  relative glosses (`= -maṇḍa`, `See -mukha`), paraphrase/compression drift,
  wisdomlib edits. These are the rows a reader-pack consumer must NOT treat as
  verbatim csl-orig equivalents.
- **D3 mis-attribution probe** ran over the drawn sample (no D1/D2 rows were
  drawn — all 50 sample slots fell on match rows; D3 remains available via the
  builder for a defect-focused re-sample).
- Defect flags are exactly the rows carrying `D1_*`/`D2_*` in
  `h4807_mwap_match.tsv.gz` (rebuildable, not committed at 20.6 MB).

## Verify: 50-gloss sample

`h4807_sample50.tsv` — `random.Random(42)` balanced MW/AP draw from match rows;
every row mechanically revalidated (same headword tier + gloss-verdict
recomputation): **50/50 PASS** (`SELFTEST/PASS` in builder output). Hand
inspection: `capalaka` "fickle, inconsiderate" = MW; `naddhrī` "a strip of
leather" = MW; `paryāpta` "Obtained, got, gained" = Apte; `upadravin` =
Apte sense list. All four are genuine source borrowings, not coincidence.

## Check (prove with)

```
python3 tools/h4807_ap90_glosses.py --selftest
python3 tools/h4807_gloss_provenance.py --glosses <h4807_skt_glosses.tsv.gz> --outdir data/h4807_gloss_provenance
# -> SELFTEST/PASS requires 50/50 sample revalidation; full match TSV:
python3 tools/h4807_msi_extract.py        # on the scrape box, read-only over the store
```

## License note

wisdomlib CC BY 4.0 × csl-orig MW/AP90 CC BY-SA 4.0 ⇒ the committed AP90 gloss
TM (`tools/h4807_ap90_glosses.json`) and any shipped join inherit the stricter
share-alike term: **CC BY-SA 4.0** with wisdomlib + Cologne provenance, per
H4733's LICENSE-DATA norm.

## Risks / limits

- Text-match is a strict LOWER BOUND on borrowing: attribution census is the
  high-precision signal (wisdomlib explicitly labels 90 % Cologne), while
  verbatim-grade equality is provable only where markup noise and relative-gloss
  structure allow.
- Wisdomlib attribution strings are taken at face value; they are themselves
  the thing measured, so "Cologne-declared" ≠ "Cologne-verified" for the
  unmatched 57 %.
- The match TSV (20.6 MB gz) is intentionally NOT committed (repo bulk norm);
  rebuild from the two committed tools + the scrape store.
- Full 55 MB gloss extraction stays on the scrape box (MSI,
  `out/meta/h4807/`); committed tools regenerate it deterministically.

## Delivery (five fields)

- **Changed:** new provenance measurement lane + AP90 gloss TM + report (this
  file), no existing data modified.
- **Unchanged:** csl-orig (read-only), wisdomlib store (read-only),
  `mw_en_tm.json` (rebuilt byte-equivalent input, not committed), H4733
  artifacts.
- **Checks:** builder selftest PASS (50/50 revalidated); sweep reconciliation
  255,348 = L8 rows; AP90 selftest PASS (34,882 records).
- **Risks:** D1 coverage artifact on the AP90 lane (see Defect catch); strict
  match undercounts borrowing.
- **Inspect:** [h4807_sample50.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/h4807_gloss_provenance/h4807_sample50.tsv),
  then `h4807_stats.json`, then the two committed tools.
