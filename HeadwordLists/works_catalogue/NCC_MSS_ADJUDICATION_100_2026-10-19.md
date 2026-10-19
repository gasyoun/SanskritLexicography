# NCC MSS 100-unit adjudication — precision gate (H7080, residual of H7073)

_Created: 19-10-2026 · DeepSeek v4.1 Flash (`deepseek-flash`) · launch box: Mac · workbook **present**_

## Verdict first

**HOLD** for the full 152,526-entry census.

| gate | value | threshold | pass |
|---|---|---:|---|
| point precision | **87 / 99 = 87.9 %** | ≥ 95 % | **NO** |
| Wilson 95 % lower bound | **80.0 %** | ≥ 90 % | **NO** |
| `AMBIGUOUS` count | **1** | ≤ 10 | yes |
| canary names both numbers | Mahābhārata 2,355 · Rāmāyaṇa 814 | both named | yes (but both DIFF — see below) |

Two of the four locked conditions fail, and they are the two that matter: the parser's
precision is **7.1 points short of the target**, and the interval's floor is 10 points short.
A GO is not available at any reading of the rule.

The GO rule itself was locked on 18-10-2026 in
[`NCC_MSS_PRECISION_100_2026-10-18.md`](NCC_MSS_PRECISION_100_2026-10-18.md) before any
verdict row existed, and is reproduced here unchanged. It was not edited after results.

## Why this handoff exists

[H7073](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7073-DeepSeek_SanskritLexicography_ncc-mss-100-unit-adjudication_18.10.26.md)
shipped, in PR [#2433](https://github.com/gasyoun/SanskritLexicography/pull/2433), the
edition/journal filter, the seeded volume-stratified sampler and a HOLD report — but **not**
its named deliverable `ncc_mss_adjudication_100.tsv`, because the VisualDCS counting
workbook was reported absent on that launch box. Its own fallback sanctioned exactly that
split ("commit the filter + a reproduced pilot-table delta and hand off the adjudication").

The workbook is present on this box:

```
~/Documents/GitHub/VisualDCS/non-derived/NCC/Works-Share-NCC/NCC-mss-counting-1 031 077.xlsx
    sheet "NCC_mss_counting- 1 032 077": 140,848 data rows
    columns: id, eid, vol, pg, col, IAST, Type, mss, Cats, Details
    `id` == `ncc_numid` in ncc.jsonl
```

so the blocked half is executable here. Nothing in that workbook is used as an answer: the
`mss` count is never quoted, `1,032,077` is never quoted as a census, and `--full` was not run.

## Sample design (locked, unchanged)

- Source: the same 500-entry pilot as H6995 (`pilot_sample`, systematic over `(volume, ncc_id)`), **post-filter** units only.
- Population: **1,290** distinct post-filter units.
- Stratification: all 39 volumes, proportional allocation with a floor of 2 per volume, capped by supply; the draw reaches **39 volumes** (volume 23 supplies one unit, every other volume at least two).
- Seed: **20261018** — byte-identical re-draw:
  `python census_ncc_mss.py --ncc ncc.jsonl --adjudication-sample 100 --seed 20261018`
- `verdict` / `reason` were left empty by the sampler; the 100 verdicts below are the hand read.

## Method actually used

1. **Draw** with the committed sampler, seed 20261018 (no hand picking, no re-draw after results).
2. **Read each unit at the mention that produced it.** The sampler's `source_span` is keyed on
   the *first* mention of a catalogue in the body; where a body mentions a catalogue twice that
   span can point at the wrong occurrence. Each unit was therefore re-located to the mention
   whose segment actually yielded its accession before a verdict was assigned. This changed the
   evidence for several units — e.g. `Oppert 8690` looks misattributed against the first-mention
   span, but the producing segment is a continuous `Oppert II. 360. 6031. 6851. 8690. 10361.`
   run, so it is SUPPORTED.
3. **`Details` as a second opinion only.** It corroborates 60 of the 87 SUPPORTED units. It is
   **body-derived, not independent**: for entry `numid=117979` its `D.` set is
   `{148 164 68 73 1908 12 15-6 1898 1899 1911}`, which mixes accession numbers with years and a
   page range; and the `|20|51|12|81|` page-marker artifacts in the bodies show up as "accessions"
   in `Details` (e.g. `Baroda: 5 {6933 20 51 12 81}`). Where `Details` and the body disagree, the
   body decides.
4. **Verdict vocabulary** (locked): `SUPPORTED` · `FALSE_POSITIVE` · `AMBIGUOUS`, each with a
   `reason`. Precision = `SUPPORTED ÷ (SUPPORTED + FALSE_POSITIVE)`, `AMBIGUOUS` excluded and
   reported separately.
5. **Wilson 95 % interval** on that denominator (z = 1.959964).

## Result

| verdict | count |
|---|---:|
| SUPPORTED | **87** |
| FALSE_POSITIVE | **12** |
| AMBIGUOUS | **1** |
| **total** | **100** |

`precision = 87 / 99 = 0.8788` → **87.9 %**, Wilson 95 % CI **[80.00 %, 92.93 %]**.

Reproduce from the committed TSV alone:

```bash
awk -F'\t' 'NR>1 && $5=="SUPPORTED"{s++} NR>1 && $5=="FALSE_POSITIVE"{f++} NR>1 && $5=="AMBIGUOUS"{a++}
            END{printf "S=%d F=%d A=%d  precision=%.4f\n",s,f,a,s/(s+f)}' ncc_mss_adjudication_100.tsv
```

## The 12 false positives, by class

| class | n | units |
|---|---:|---|
| volume / part marker | 5 | `Vol 190`, `Vol 303`, `Vol 448`, `Vol 510`, `Pt 1129` |
| scholar / editor name | 2 | `Dutt 3`, `Fausboll 164` |
| subject marker | 1 | `Bud 35` |
| bibliographic page in a secondary source | 1 | `Sn 919` |
| year range expanded into accessions | 1 | `Ben 1900` |
| **`MD` folded into the preceding segment** | 2 | `Adyar 6571`, `Jain 8771` |

| # | vol | siglum | acc | evidence |
|---:|---:|---|---:|---|
| 10 | 3 | Dutt | 3 | `English transl. by J. C. Dutt. 3 Vol.` — translator's name + volume count |
| 11 | 3 | Fausboll | 164 | `Fausboll 148 … Fausboll 164` — editor's name; the workbook's `D.` set here is body-derived |
| 28 | 10 | Bud | 35 | `Bud.` is a subject marker (Buddhist) throughout the corpus; 35 belongs to `Hod. Bud.` |
| 31 | 11 | Adyar | 6571 | body reads `Adyar II. p. 211a . MD. 6571-74` — 6571 is **MD's** accession |
| 45 | 18 | Ben | 1900 | `Skt. Col.. Ben. 1897-1901. p. 173` — acquisition years, not serials |
| 54 | 22 | Sn | 919 | `See M. Krishnamachariar, HCSL., Sn. 919` — page in a published history |
| 67 | 28 | Jain | 8771 | `Jain. MD. 8771. 8772` — subject marker + 8771 is **MD's** accession |
| 74 | 31 | Vol | 190 | `Ser. 10. Vol. XIX. 163-93` — volume marker; 190 is a page-range member |
| 75 | 31 | Vol | 303 | volume marker |
| 76 | 31 | Vol | 448 | volume marker |
| 77 | 31 | Vol | 510 | volume marker; 510 closes the page range `429-510` |
| 82 | 33 | Pt | 1129 | `Pt.` is a part marker; `p. 993 . 1129` is a page run |

The filter added in H7073 removed the journal/series/year/page-prefix classes (528 units in the
pilot). It does **not** catch volume/part markers spelled `Vol.`/`Pt.`, scholar names used as
catalogue sigla, subject markers (`Bud.`, `Jain.`), secondary-source pages, or year ranges that
get expanded. Those six classes are what the remaining 12 % is made of.

## Ambiguous (1)

`Sup 1024` (vol 36): `TD. XX. Sup. 1024 . 1024 .` — `Sup.` is a supplement qualifier of `TD`,
not a catalogue name, and 1024 appears twice. Whether it is a supplement accession or a page is
not readable from the span. Excluded from the precision denominator, as the locked rule requires.

## The parser defect this adjudication exposed

**`MD` is silently dropped from the catalogue lexicon, because `ROMAN_RE` reads it as a roman
numeral 1,500.**

`catalogue_regex()` filters out every lexicon key matching `ROMAN_RE` — correct for `II`, `XIV`,
`LXXVIII` (66 of the 67 dropped sigla are genuine volume markers) — but `MD` is spelled entirely
in roman-numeral letters and is a **real NCC catalogue**. Consequences:

1. `MD.` never terminates a segment, so MD's accession numbers are harvested under whatever
   catalogue preceded them. That is the direct cause of 2 of the 12 false positives
   (`Adyar 6571`, `Jain 8771`).
2. It inflates the witness count of the preceding catalogue and under-counts MD everywhere.

Minimal reproduction (no network, committed data):

```bash
cd HeadwordLists/works_catalogue
python - <<'PY'
import sys; sys.path.insert(0, '.')
import census_ncc_mss as M
rows = M.load_rows('ncc.jsonl')
lex = M.build_lexicon(rows, None)
print('MD in lexicon :', 'MD' in lex)              # True
print('MD dropped    :', bool(M.ROMAN_RE.match(M.norm_cat('MD'))))   # True  <-- defect
re_ = M.catalogue_regex(lex)
print('matches       :', [m.group(0) for m in re_.finditer('Adyar II. p. 211a . MD. 6571-74.')])
# -> ['Adyar']   MD is absent, so 6571 is folded into Adyar
PY
```

Blast radius, measured on the pilot:

| probe | value |
|---|---:|
| dropped lexicon sigla that match `ROMAN_RE` | 67 |
| of those, genuine workbook catalogues | **1** (`MD`) |
| pilot-500 entries whose body mentions `MD.` | 27 |
| harvested pilot units whose own segment swallows an `MD.` reference | **14 / 730 = 1.9 %** |
| sampled units misattributed because of it | **2 / 100** |

Corroborating evidence that `MD` is a real catalogue and not a volume marker: its numbers behave
exactly like other catalogues (`MD. 6571-74`, `MD. 8771`, `MD. 4695`), it appears as
`MD.: n { … }` in the workbook's own `Details` vocabulary, and no volume in NCC runs to 1,500.

**Not fixed in this pass on purpose.** Changing the lexicon now would change the sampled
population after the first verdict row was read — the failure mode the locked design forbids.
The fix is one line (an explicit known-catalogue exception for `MD`, or requiring a roman marker
to be followed by a volume-ish context) and belongs to a fresh draw with a fresh seed.

## Label truncation (10 SUPPORTED units, not false positives)

Ten units record a truncated compound catalogue name whose accession is genuine and
workbook-corroborated. They count as SUPPORTED — the manuscript exists and the number is its
accession — but the *catalogue label* is wrong, which matters for any downstream join:

`Adyar 830` / `Adyar 996` (→ `Adyar D.`), `Inst 468` (→ `French Inst.`), `Inst 5722`
(→ `B. J. Inst.`), `SS 1720` (→ `Udaipur SS.`), `Otani 760` / `Otani 5182` (→ `Suzuki, Otani`),
`Mysore 704` (→ `Mysore D.`), `Uni 61` (→ `Calcutta Uni.`), `Uni 4578` (→ `Trav. Uni.`).

The cause is that the lexicon's longest-first alternation matches only as far as the shipped
witness string was truncated, not the full compound name.

## Canary after the filter (own data)

Re-run with the workbook present, so the lexicon carries the workbook's catalogue keys:

| work | body units (post-filter) | VisualDCS `mss` | delta | status |
|---|---:|---:|---:|---|
| Mahābhārata | 2,355 | 21 | +2,334 | DIFF |
| Rāmāyaṇa | 814 | 2,762 | −1,948 | DIFF |
| Skandapurāṇa | 0 | 17 | — | **INCONCLUSIVE (absent from bodies)** |

The canary condition in the locked rule — "still names both numbers for Mahābhārata / Rāmāyaṇa"
— is satisfied literally: both numbers exist (2,355 and 814). But they disagree with VisualDCS in
opposite directions, exactly as the H7073 report recorded (1,798 / 668 on the narrower
no-workbook lexicon). Restoring `MD` shrinks the over-harvest (Mahābhārata 2,519 → 2,355,
Rāmāyaṇa 1,006 → 814 against the committed no-workbook canary), which is the right direction and
not enough.

This is a **semantic** mismatch, not a counting bug alone: the body parser counts strict
`(catalogue, accession)` units across every catalogue an entry mentions, while VisualDCS's `mss`
column counts that work's manuscripts in one aggregation. A GO on precision alone would still
ship a canary whose two computable epics disagree by thousands.

## Acceptance state

| required | state |
|---|---|
| `ncc_mss_adjudication_100.tsv` — 100 hand verdicts, seed 20261018 | **done** (101 lines, 87/12/1) |
| `NCC_MSS_ADJUDICATION_100_2026-10-19.md` — precision, Wilson 95 % CI, GO/HOLD | **done** (this file) |
| precision arithmetic reproducible from the TSV | **done** (awk above) |
| false-positive classes counted with examples | **done** (6 classes, 12 units) |
| parser defect quantified with reproduction | **done** (`MD` / `ROMAN_RE`, 1.9 % blast radius) |
| own-data canary after the filter | **done** (2,355 / 814 / INCONCLUSIVE) |
| explicit GO/HOLD | **HOLD** — precision 87.9 % < 95 %, Wilson floor 80.0 % < 90 % |

## Delivery (five fields)

- **Changed:** new `ncc_mss_adjudication_100.tsv` (100 hand verdicts with reason and span) and
  this report. No parser, no sampler, no filter and no committed pilot/canary artifact is touched.
- **Unchanged:** `census_ncc_mss.py`, `ncc.jsonl`, `ncc_mss_census_pilot_500*.tsv`,
  `ncc_mss_canary_20.tsv`, `ncc_mss_filter_delta_2026-10-18.json`,
  `NCC_MSS_PRECISION_100_2026-10-18.md` and its locked GO rule. No workbook `mss` count is quoted
  and `1,032,077` appears nowhere except as a path component.
- **Checks:** `wc -l ncc_mss_adjudication_100.tsv` → 101; verdict counts 87 + 12 + 1 = 100; the
  awk precision line reproduces 0.8788; the seed-20261018 re-draw is byte-identical; the `MD`
  reproduction above prints `True`/`True`/`['Adyar']`.
- **Risks:** the population is the no-workbook 1,290-unit pilot, so the estimate is of *this*
  parser on *this* pilot, not of the final pipeline; the `MD` defect depresses precision by ~2
  points; `AMBIGUOUS` was used once and could hide further undecidables at scale; `Details`
  corroboration is body-derived and cannot break ties on its own.
- **Inspect:** `ncc_mss_adjudication_100.tsv` rows for `#10`, `#31`, `#45`, `#67`, `#74`, `#92`
  first, then the `MD`/`ROMAN_RE` reproduction block in this report.

_Dr. Mārcis Gasūns_
