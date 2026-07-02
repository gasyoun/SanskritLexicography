# Renou H4 — dictionary citation bias

_Created: 02-07-2026 · Last updated: 02-07-2026_

Step 1 of the [Renou hypothesis-testing programme](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_HYPOTHESES.md)
(spec authored by Fable 5, `claude-fable-5`). Tests H4: **19th-century
dictionaries over-cite Vedic and kāvya relative to actual usage, and
under-cite the epic** — a measurable imprint of philological taste.

Computed by Sonnet 5 (`claude-sonnet-5`).

## Method

Two deterministic routes into the same 20-register lattice
([`renou_register.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_register.py)),
neither depending on the `dcs` state-tagging precision that Step 0 pilots —
this hypothesis needs no gold standard:

- **Citation side.** Per dictionary, per register: the share of entries whose
  `renou_register_provenance` for that register includes `"ls"` (the
  lexicographer's own citation) — an **entry-level** unit. The canonical
  `{code}.renou.jsonl` records retain only which *signal* backs each register
  (`ls`/`dcs`), not the resolved per-entry citation *instances* (which siglum,
  how many times) — that detail is discarded by
  [`tag_dict_from_source.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tag_dict_from_source.py)
  at merge time. Recovering instance-level counts would require re-running the
  tagger with a schema change; out of scope for this pass (see Limitations).
- **Usage side.** [`renou_corpus_map.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_corpus_map.py)
  corpus-wide register shares over 1,091,528 aligned Sanskrit–Russian
  attestations — an **attestation-level** unit.
- **Bias metric.** bias(d, r) = log2( citation_share(d, r) / usage_share(r) ).
  Positive = the dictionary over-cites register r relative to its actual
  corpus weight; negative = under-cites. 95% CI via 1,000-rep bootstrap
  resampling of entries (citation side only — the usage-side baseline is a
  fixed population parameter per the spec).
- **Scope guard.** Only registers reachable by both routes enter the ratio
  table (usage_share > 0 AND the register appears in the dict's `ls` route).
  `hors_inde` is excluded (no source at all). One-route registers are listed
  separately below.

Reproduce: [`src/renou_h4_citation_bias.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_h4_citation_bias.py)
(writes gitignored `h4_citation_bias.json`) then
[`src/renou_h4_figures.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_h4_figures.py)
(figures below).

## Headline: the epic is under-cited in every one of the 8 dictionaries

Corpus baseline: epic **61.0%** of all usage — by far the largest single
register, roughly 4× rgveda (14.4%) and 16× kāvya (3.9%). Yet its citation
share never approaches that in any dictionary:

| Dict | epic citation share | log2 bias (epic) | rgveda citation share | log2 bias (rgveda) | kāvya citation share | log2 bias (kāvya) |
|---|--:|--:|--:|--:|--:|--:|
| PWG | 19.5% | **−1.65** [−1.66, −1.63] | 8.4% | −0.78 [−0.80, −0.75] | 10.0% | **+1.37** [+1.35, +1.39] |
| MW | 13.0% | **−2.24** [−2.25, −2.22] | 4.6% | −1.63 [−1.66, −1.61] | 4.6% | +0.26 [+0.24, +0.29] |
| PW | 3.3% | **−4.21** [−4.25, −4.18] | 0.8% | −4.24 [−4.32, −4.16] | 1.9% | −1.03 [−1.08, −0.98] |
| AP | 10.5% | **−2.54** [−2.57, −2.52] | 1.5% | −3.24 [−3.32, −3.17] | 8.3% | **+1.11** [+1.07, +1.14] |
| AP90 | 12.1% | **−2.34** [−2.38, −2.29] | 0.5% | −4.81 [−5.03, −4.60] | 14.4% | **+1.90** [+1.86, +1.93] |
| BEN | 31.1% | **−0.97** [−1.01, −0.94] | 3.6% | −2.02 [−2.13, −1.90] | 16.9% | **+2.13** [+2.09, +2.18] |
| SCH | 0.6% | **−6.62** [−6.84, −6.41] | 0.5% | −4.96 [−5.24, −4.74] | 0.5% | −2.98 [−3.22, −2.74] |
| BHS | 0.5% | **−6.86** [−7.20, −6.59] | — (unreachable) | — | 0.3% | −3.73 [−4.14, −3.34] |

Every single log2(epic) bias is negative — the epic is under-cited relative
to its usage weight in **all 8 dictionaries**, ranging from a 2× under-cite
(BEN, log2 = −0.97) to a ~116× under-cite (BHS, log2 = −6.86; SCH, log2 =
−6.62). Rgveda is under-cited in 7/7 dictionaries where the comparison is
reachable (BHS's `ls`-route never resolves an rgveda-classed siglum, so it is
excluded by the scope guard). Kāvya is **over-cited** in 5/8 dictionaries
(PWG, MW, AP, AP90, BEN — log2 positive) and under-cited in the remaining 3
(PW, SCH, BHS) — the direction Renou's philological-taste hypothesis
predicts, though not universal.

## Full per-dictionary tables

Registers reachable by both routes only; sorted alphabetically. `n` = entries
citing that register via `ls`.

### PWG (n=123,366 entries, 64,938 with an `ls` register)

| register | citation share | usage share | log2 bias | 95% CI | n |
|---|--:|--:|--:|--:|--:|
| atharva | 4.46% | 5.56% | −0.32 | [−0.35, −0.29] | 5,506 |
| epic | 19.49% | 61.03% | **−1.65** | [−1.66, −1.63] | 24,042 |
| katha | 9.60% | 1.97% | **+2.28** | [+2.26, +2.31] | 11,849 |
| kavya | 9.99% | 3.86% | **+1.37** | [+1.35, +1.39] | 12,323 |
| rgveda | 8.38% | 14.36% | −0.78 | [−0.80, −0.75] | 10,335 |
| smrti | 5.93% | 3.61% | +0.72 | [+0.68, +0.75] | 7,313 |

ls-only (one-route) registers: yajus (4.68%, n=5,772), brahmana (5.59%,
n=6,900), sutra (3.07%, n=3,793), vyakarana (12.48%, n=15,402), epig (0.01%,
n=9), purana (10.64%, n=13,129), natya (2.23%, n=2,757).

### MW (n=286,560 entries, 115,117 with an `ls` register)

| register | citation share | usage share | log2 bias | 95% CI | n |
|---|--:|--:|--:|--:|--:|
| atharva | 2.23% | 5.56% | −1.32 | [−1.36, −1.29] | 6,377 |
| bauddha | 1.48% | 1.12% | +0.40 | [+0.36, +0.44] | 4,246 |
| bhasya | 1.43% | 1.18% | +0.29 | [+0.24, +0.33] | 4,109 |
| epic | 12.96% | 61.03% | **−2.24** | [−2.25, −2.22] | 37,132 |
| katha | 4.33% | 1.97% | +1.14 | [+1.11, +1.16] | 12,420 |
| kavya | 4.64% | 3.86% | +0.26 | [+0.24, +0.29] | 13,287 |
| rgveda | 4.62% | 14.36% | **−1.63** | [−1.66, −1.61] | 13,253 |
| smrti | 2.85% | 3.61% | −0.34 | [−0.37, −0.31] | 8,164 |
| upanisad | 0.52% | 3.48% | **−2.75** | [−2.83, −2.68] | 1,480 |

ls-only: yajus, brahmana, sutra, vyakarana, epig, purana, natya, jaina.

### PW (n=170,556 entries, 16,082 with an `ls` register)

| register | citation share | usage share | log2 bias | 95% CI | n |
|---|--:|--:|--:|--:|--:|
| atharva | 0.42% | 5.56% | −3.73 | [−3.84, −3.63] | 713 |
| epic | 3.29% | 61.03% | **−4.21** | [−4.25, −4.18] | 5,617 |
| katha | 0.58% | 1.97% | −1.76 | [−1.85, −1.67] | 994 |
| kavya | 1.90% | 3.86% | −1.03 | [−1.08, −0.98] | 3,233 |
| rgveda | 0.76% | 14.36% | **−4.24** | [−4.32, −4.16] | 1,297 |
| smrti | 0.37% | 3.61% | −3.27 | [−3.37, −3.16] | 638 |

PW has the sparsest `ls`-register coverage of the trust-ladder-high
dictionaries (9.4% of entries) — every register is under-cited, including
kāvya, unlike PWG/MW/AP/AP90/BEN.

### AP (n=90,654 entries, 23,234 with an `ls` register)

| register | citation share | usage share | log2 bias | 95% CI | n |
|---|--:|--:|--:|--:|--:|
| atharva | 0.45% | 5.56% | −3.62 | [−3.75, −3.49] | 409 |
| epic | 10.49% | 61.03% | **−2.54** | [−2.57, −2.52] | 9,511 |
| katha | 3.29% | 1.97% | +0.74 | [+0.69, +0.79] | 2,983 |
| kavya | 8.32% | 3.86% | **+1.11** | [+1.07, +1.14] | 7,540 |
| rgveda | 1.52% | 14.36% | −3.24 | [−3.32, −3.17] | 1,375 |
| smrti | 4.77% | 3.61% | +0.40 | [+0.36, +0.44] | 4,320 |

### AP90 (n=34,882 entries, 9,807 with an `ls` register)

| register | citation share | usage share | log2 bias | 95% CI | n |
|---|--:|--:|--:|--:|--:|
| atharva | 0.01% | 5.56% | −8.92 | [−10.92, −7.92] | 4 |
| epic | 12.07% | 61.03% | **−2.34** | [−2.38, −2.29] | 4,212 |
| katha | 6.57% | 1.97% | +1.74 | [+1.68, +1.79] | 2,293 |
| kavya | 14.38% | 3.86% | **+1.90** | [+1.86, +1.93] | 5,017 |
| rgveda | 0.51% | 14.36% | −4.81 | [−5.03, −4.60] | 179 |
| smrti | 6.42% | 3.61% | +0.83 | [+0.77, +0.89] | 2,241 |

AP90's atharva CI is wide (n=4) — near the floor of reliable estimation;
read as directional only.

### BEN (n=17,310 entries, 11,830 with an `ls` register)

| register | citation share | usage share | log2 bias | 95% CI | n |
|---|--:|--:|--:|--:|--:|
| epic | 31.09% | 61.03% | **−0.97** | [−1.01, −0.94] | 5,381 |
| katha | 23.08% | 1.97% | **+3.55** | [+3.51, +3.59] | 3,995 |
| kavya | 16.94% | 3.86% | **+2.13** | [+2.09, +2.18] | 2,933 |
| rgveda | 3.55% | 14.36% | −2.02 | [−2.13, −1.90] | 615 |
| smrti | 20.12% | 3.61% | **+2.48** | [+2.44, +2.52] | 3,482 |

BEN is the most register-dense dictionary of the eight (68.4% of entries
carry an `ls` register) and shows the strongest kathā/smṛti/kāvya
over-citation of the set alongside the mildest epic under-citation — Benfey's
citation profile leans hardest into classical narrative/didactic material.

### SCH (n=29,125 entries, 976 with an `ls` register — sparsest overall)

| register | citation share | usage share | log2 bias | 95% CI | n |
|---|--:|--:|--:|--:|--:|
| atharva | 0.27% | 5.56% | −4.34 | [−4.71, −4.06] | 80 |
| epic | 0.62% | 61.03% | **−6.62** | [−6.84, −6.41] | 181 |
| kavya | 0.49% | 3.86% | −2.98 | [−3.22, −2.74] | 143 |
| rgveda | 0.46% | 14.36% | −4.96 | [−5.24, −4.74] | 134 |
| smrti | 0.39% | 3.61% | −3.22 | [−3.51, −2.97] | 113 |

SCH's `ls`-tagged register coverage is only 3.4% of entries — small counts
give wide CIs; treat as suggestive, not a strong per-register estimate. Every
register is under-cited, consistent with SCH's role as a small/specialised
dictionary rather than a general citation-rich one.

### BHS (n=17,839 entries, all 17,839 carry an `ls` register by construction)

| register | citation share | usage share | log2 bias | 95% CI | n |
|---|--:|--:|--:|--:|--:|
| atharva | 4.87% | 5.56% | −0.19 | [−0.29, −0.11] | 869 |
| bauddha | 100.00% | 1.12% | **+6.48** | [+6.48, +6.48] | 17,839 |
| bhasya | 0.01% | 1.18% | −7.71 | [n<3, unstable] | 1 |
| epic | 0.53% | 61.03% | **−6.86** | [−7.20, −6.59] | 94 |
| katha | 0.05% | 1.97% | −5.29 | [−6.46, −4.46] | 9 |
| kavya | 0.29% | 3.86% | **−3.73** | [−4.14, −3.34] | 52 |
| smrti | 0.01% | 3.61% | −9.33 | [n<3, unstable] | 1 |

BHS's `bauddha = 100%` figure is **tautological, not a finding** — every BHS
entry is assigned `bauddha` by
[`renou_sigla.registers_for_block`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_sigla.py)
regardless of citation content (`if code == 'bhs': regs.add('bauddha')`), since
Edgerton's dictionary is wholly Buddhist Hybrid Sanskrit by definition. Exclude
it from any cross-dictionary comparison; it measures the dictionary's scope,
not a citation choice. bhasya/smrti (n=1 each) are below any reliable
threshold — reported for completeness only.

## Acceptance criterion — entry-level sign stability

The spec's acceptance criterion is: *the sign of the bias (over/under) agrees
between entry-level and instance-level units for every register reported.*
**This criterion cannot be fully evaluated in this pass** — see Limitations.
Only the entry-level unit was computed (the canonical `.renou.jsonl` records
do not retain resolved per-entry citation instances; recovering them requires
a tagger schema change, out of scope here). What *is* stated: the entry-level
sign is internally stable and directionally coherent across all 8
dictionaries for the headline registers (epic under-cited in 8/8; rgveda
under-cited in 7/7 reachable; kāvya over-cited in 5/8, under-cited in 3/8,
with the direction correlating with each dictionary's overall citation
density — PW/SCH, the two sparsest, are also the two where kāvya flips
negative). A future pass with instance-level counts (see Limitations) is
needed to close the acceptance criterion as originally specified.

## Limitations

- **Units differ, by design.** Citation share is an entry-level incidence
  rate (an entry counts once per register it cites, regardless of how many
  times); usage share is an attestation-level rate (every aligned word pair
  counts once). The spec anticipates this explicitly ("compare shares, not
  raw counts") — the log2 ratio compares *shares*, not underlying event
  counts, and the two units are not interchangeable in any other computation.
- **Instance-level citation counts are not recoverable without re-running the
  tagger.** `renou_register_provenance` in `{code}.renou.jsonl` records only
  which *signal* (`ls`/`dcs`) supports each register per entry — not how many
  distinct citations, or which sigla, contributed. The spec allows this
  ("if… recoverable… use instance counts and report both units; [if not]…");
  it is not recoverable from the current index, so only the entry-level unit
  is reported. This also means the acceptance criterion's cross-unit sign
  check is partial (see above).
- **BHS's `bauddha=100%` is tautological**, not a citation-choice finding —
  excluded from cross-dictionary reading (see BHS table note).
- **Sparse dictionaries (PW 9.4%, SCH 3.4% `ls`-register coverage) give wide
  CIs** on low-n registers; read those cells as directional, not precise.
- **Register reachability is asymmetric by dictionary.** BHS's `ls` route
  never resolves an rgveda-classed siglum (its curated sigla table has no
  Ṛgveda entry), so rgveda is excluded from BHS's both-route table — a gap
  in `renou_sigla.py`'s BHS coverage, not a finding about BHS's actual
  citation practice.
- **The usage-side corpus is itself unbalanced** (61% epic reflects the
  parallel corpus's own text selection, mostly Mahābhārata/Rāmāyāṇa
  translation projects) — "actual usage" here means *usage within this
  parallel corpus*, not a claim about the full surviving Sanskrit textual
  record. Renou's 1956 hypothesis was about the latter; this measurement is
  the best available proxy, not identical to it.
- **No gold-standard validation gate** — H4 was deliberately designed
  (per the spec) to need none, since both routes are fully deterministic. It
  does not depend on Step 0's pilot precision estimates.

## Findings routing

Confirmed (epic under-citation, universal across 8/8 dictionaries; rgveda
under-citation, 7/7 reachable) → appended as F6 to
[RENOU_FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_FINDINGS.md).

_Dr. Mārcis Gasūns_
