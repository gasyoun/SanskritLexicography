# A35 — referee-style review (pre-submission, hostile)

_Created: 03-07-2026 · Last updated: 03-07-2026_

Hostile pre-submission review of
[csl-orig/v02/etymology_stats/PAPER_DRAFT.md](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/PAPER_DRAFT.md)
("Cross-dictionary consistency of Pāṇinian derivation in the Cologne lexica", → IJL /
Lexicographica) by Fable 5 (`claude-fable-5`), 03-07-2026, Fable trial window session S6.
**csl-orig is read-only for agents, so — unlike the A36 pass — nothing was applied**; every
finding below is a documented, evidence-backed fix for a later maintainer pass. All numbers
were re-verified against the committed CSVs
([cross_dict_agreement.csv](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/cross_dict_agreement.csv),
[cross_dict_root_agreement.csv](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/cross_dict_root_agreement.csv),
[root_capture.csv](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/root_capture.csv)),
the ten `*_etymology.tsv` extractions, the agreement code in
[stats_etymology.py](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/stats_etymology.py)
(§6a/6b), and — for the Wilson diagnosis — fresh computations over the TSVs (documented
inline).

**Overall verdict: the Sanskrit-side finding (F1) is real and publishable, and the strict-tier
robustness check is exemplary practice. But the paper is NOT submittable as drafted: its most
quotable claim — the Wilson outlier as "confirmed idiosyncratic, pre-critical etymologies" —
is substantially a measurement artifact that the paper's own released data exposes, and any
referee who pulls the CSVs (the paper invites them to) will also find a Sanskrit-side pair at
20 % that Table 1 silently omits, plus an unreported Wilson root-agreement of 8–20 % against
every dictionary including MW. Verdict: major revision. The fixes are mechanical and the paper
comes out stronger — the honest version ("half of Wilson's divergence is our extractor, the
rest is Wilson") is more interesting than the current one.**

---

## Major findings

### M1. The Wilson outlier (F2) is substantially a measurement artifact; the CI argument doesn't cover it

The paper argues Wilson's divergence is "statistically clear, not sampling noise" from
non-overlapping Wilson intervals. True — but confidence intervals answer *sampling* error, not
*measurement* error, and the measurement is where the problem is:

- Every Sanskrit-side dictionary's `affix` field draws on a **closed Pāṇinian vocabulary**
  (SKD 35 distinct values, VCP 36, AP90/SHS/KRM 23; union = 39). **WIL's affix field has
  3,375 distinct values**, and **only 50.1 % of WIL's 19,641 affix instances are valid
  Pāṇinian affix names at all** (measured against the union vocabulary). The long tail is
  raw-token captures (`somavat`, `viDAna`, `tena`, …) that can never match anything —
  mechanically depressing every WIL pair.
- Recomputing the paper's own agreement statistic restricted to shared head-words where WIL's
  affix is at least in the canonical vocabulary (same set-intersection rule, same TSVs):

  | pair | paper (all) | WIL-affix ∈ Pāṇinian vocab only |
  |---|---|---|
  | WIL↔SKD | 22.9 % (16/70) | **66.7 %** (16/24) |
  | WIL↔VCP | 61.2 % (921/1504) | **80.2 %** (921/1149) |
  | WIL↔SHS | 60.0 % (114/190) | **78.1 %** (114/146) |
  | WIL↔AP90 | 54.2 % (45/83) | **71.4 %** (45/63) |
  | WIL↔AP | 52.4 % (43/82) | **71.7 %** (43/60) |

  Roughly **half to two-thirds of the headline Wilson gap evaporates** once junk captures are
  removed from the denominator. A genuine residual gap remains (≈67–80 % vs ≈90–100 %
  Sanskrit-side), so F2 survives — weakened — but the current wording ("confirming Wilson's
  idiosyncratic, pre-critical etymologies") attributes to Wilson what is partly the WIL
  extractor.
- The within-Wilson spread already signals this: WIL↔SKD 22.9 % vs WIL↔VCP 61.2 % is a 3×
  range. A coherent "distinct stratum" doesn't agree three times better with one indigenous
  kośa than another.

**Fix:** report both numbers (raw + vocabulary-filtered); manually audit a sample (~50) of
WIL↔SKD disagreements and classify extractor-error vs genuine divergence; reword F2 and the
abstract to claim only what survives. Consider adding the vocabulary-validity rate per
dictionary as a data-quality column — it is a finding in its own right.

### M2. Table 1 omits its own counter-example: VCP↔KRM at 20.0 %

[cross_dict_agreement.csv](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/cross_dict_agreement.csv)
contains **VCP↔KRM 20.0 % [7.0–45.2] (n=15)** — a *Sanskrit-side* pair whose point estimate
is **below Wilson's headline 22.9 %**. Table 1 omits it (along with WIL↔KRM 22.2 %, SKD↔AP
91.8 %, SKD↔SHS 100 % n=5, Apte↔SHS 96.3 %, AP↔SHS 100 %) with no stated inclusion rule,
while the caption asserts "the Sanskrit-side block (top) is uniformly high" and F1 claims
"90–100 %". A referee opening the released CSV finds the contradiction in seconds.

KRM plausibly *deserves* a carve-out — it is organised as kṛdanta paradigms by root, and its
affix distribution is structurally different (top affix `ka` 95×, vs `lyuṭ`/`ghañ` everywhere
else), so its comparisons are partly apples-to-oranges. But the carve-out must be argued in
print, with the row shown.

**Fix:** state an explicit inclusion rule (e.g. n ≥ 25), apply it uniformly, print the KRM
rows with the structural explanation, and qualify F1 ("90–100 % among the prose kośas;
the root-organised KRM is a structural exception discussed in §…").

### M3. The measured object is affix-name intersection — not "derivation"

Title and abstract claim consistency of *derivation* (root + affix + kāraka). What §6a
actually measures ([stats_etymology.py:199-215](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/stats_etymology.py))
is: per shared `headword_slp1`, whether the two dictionaries' **affix-name sets intersect**.

- **Kāraka agreement is never measured**, although SKD/VCP/AP90/AP/SHS all carry a per-row
  kāraka — the one dimension the title's "Pāṇinian derivation" most implies.
- **Within-tradition root agreement is never reported**, and it is markedly lower than affix
  agreement: SKD↔VCP **81.0 %**, SKD↔Apte 76.2 %, SKD↔AP **68.9 %**, VCP↔SHS 85.1 %
  (inclusive tier). Readers of F1 (90–100 %) will assume derivational agreement; the roots
  say 69–85 %.
- Set-intersection is inflationary for multi-affix head-words (any overlap counts). The
  multi-affix share is small (VCP 196/2,964 head-words ≈ 6.6 %, others less), so this is a
  sensitivity note, not a flaw — but say it, and/or report an exact-match variant.

**Fix:** either narrow the claim to *affix* consistency throughout, or add the kāraka-agreement
table and the within-tradition root table with discussion. State the intersection rule's
direction of bias and the multi-affix share.

### M4. Wilson's root agreement (8–20 % against everyone, including MW) is unreported — and diagnosable

The released
[cross_dict_root_agreement.csv](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/cross_dict_root_agreement.csv)
shows WIL agreeing on the root with: SKD 8.9 %, VCP 7.9 % (n=1912), **MW 8.4 % (n=1074)**,
PWG 11.6 % (**n=4257**), PW 13.3 %. The paper never mentions Wilson root rows. Agreement of
8 % with MW — the dictionary that historically *built on* Wilson — is not editorial
divergence; it is form mismatch. Concrete verified case: for *aṃśa*, WIL's extracted root is
`aMSa` (Wilson prints the root in thematic form: "{#aMSa#} to divide, {#ac#} affix") while
SKD's is `aMS` — the exact class of variant (`sada`→`sad`) the paper's root-normalization
pass §"Root-form normalization" exists to fold, evidently not reaching the WIL rows.

**Fix:** extend the (variant → citation-form) fold to WIL extractions and re-run; whatever
remains, either report the WIL root rows or exclude WIL from root tables with a stated
reason. At n=4,257 (WIL↔PWG is the largest shared-headword pair in the whole study), silence
is not an option.

### M5. "~67,000 derivations" is an undefined instance count

Current TSV rows total **68,510**, of which **WIL alone is 39,650 (58 %)** — and WIL's rows
split into `root+affix` 18,957, **`compound` 17,686**, `prefix+word` 1,406, `multi-derivation`
1,214, `single-stem` 212, `cross-ref` 158, `unparsed` 17. Compound analyses and cross-refs are
not root+affix derivations; under a strict definition the corpus is ~50k, not 67k, and the
"outlier" dictionary contributes the majority of instances either way. Related figure drift:
"the residual 117" for VCP vs `empty=96` in the current
[root_capture.csv](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/etymology_stats/root_capture.csv);
"SHS reaches 95 %" vs current 96.1 %.

**Fix:** define "derivation instance", give per-type counts per dictionary (one small table),
and regenerate every in-text figure from the current run (the draft's own Limits section
already warns about this — apply it to the draft itself).

### M6. DeepSeek grades its own homework

Roots are back-filled by a DeepSeek *llm-pass*, and tier precision is established by a
"DeepSeek-judged" audit — the same model family generating and grading. The dhātu-list
validation genuinely constrains the llm-pass, but the quoted precision figures for
*oracle-join* (≈83 %) and *nearest-root* (≈66–75 %) rest entirely on the same judge, and the
draft itself notes judge false-negatives. The Limits section proposes a second-annotator
audit; for submission that must be done, not proposed — a 50-row human-adjudicated sample per
inferred tier is an afternoon and converts two soft numbers into hard ones.

---

## Minor findings

1. **Figure drift:** F3 says "65 %" (CSV: 64.2 %), "PWG↔PW 93 %" (CSV: 93.9 %); abstract's
   "~two-thirds" is fine. Use the CSV values.
2. **Naming:** "Apte" (= AP90) vs "AP" is ambiguous outside the project — Method table says
   AP90, findings and CSVs say "Apte". Use the CDSL codes with one expansion at first mention.
3. **CAE/MD `E.` caveat is missing.** WIL's derivation marker is `<ab>E.</ab>`; MD (201×) and
   CAE (584×) carry the *same tag* meaning **Epic register**, not etymology (verified in
   `md.txt`/`cae.txt`: "`<ab>E.</ab> + <cl>Ⅰ.</cl>`…"). The pipeline correctly excludes them,
   but the paper never says why the two obvious "E."-bearing candidates are absent — one
   sentence forestalls both the referee question and a naive replicator's error.
4. **n<25 pairs in prose:** SKD↔SHS 100 % [56.6–100] rests on n=5. The dashboard's own
   caveat ("a tidy 100 % over n=5 is weak evidence") belongs in the paper.
5. **Table 1 caption** says "sorted by shared count"; the rows aren't (178, 206, 97, …). Fix
   order or caption.
6. **Reproducibility overclaim:** "all figures reproducible … via `python stats_etymology.py`"
   — the README's actual build is two extraction passes plus an optional DeepSeek step
   requiring an API key. Say "regenerable except the committed LLM tiers".
7. **Denominator framing:** all agreement is conditional on *both* extractors succeeding on a
   shared head-word — coverage gaps never enter. The dashboard states this ("Can't tell
   you…"); the paper should too, in Method, one sentence.

## What is solid (keep and foreground)

- The strict-tier robustness check (MW↔PWG and PWG↔PW identical with/without `nearest-root`)
  is exactly the right move and survives verification.
- Wilson-interval reporting throughout; provenance-tagged tiers; the oracle's dhātu-list +
  ≥⅔-majority guards; the root-norm fold's canonical-collision guard (`kṝ` ≠ `kṛ`) — all
  verified in code and defensible.
- F4/F4b (kāraka×pratyaya structure; KRM's kartari inversion) are internally consistent and
  uncontested by this review.

## Disposition

| # | Where the fix lands | Effort |
|---|---|---|
| M1 | WIL extractor / `stats_etymology.py` (vocab-validity column) + PAPER_DRAFT F2, abstract | medium |
| M2 | PAPER_DRAFT Table 1 + F1 wording | minor |
| M3 | `stats_etymology.py` (kāraka + within-tradition root tables) + title/claims | medium |
| M4 | root-norm fold applied to WIL + re-run; PAPER_DRAFT | medium |
| M5 | PAPER_DRAFT abstract/Method (instance definition, per-type table, figure refresh) | minor |
| M6 | human 50-row audit per inferred tier (MG or second annotator) | medium, human |
| m1–m7 | PAPER_DRAFT text | minor |

All csl-orig edits go through the read-only discipline: prepared in a maintainer session,
never by an agent chat. Readiness stays **4/5**; after M1–M6 the paper is a genuinely
stronger 5/5 — the artifact-vs-divergence decomposition of Wilson is a better headline than
the current one.

_Dr. Mārcis Gasūns_
