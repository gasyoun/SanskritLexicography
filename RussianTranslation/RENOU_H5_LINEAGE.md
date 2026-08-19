# Renou H5 — MW inherits the Petersburg citation structure

_Created: 19-08-2026 · Last updated: 19-08-2026_

Step 5 of the [Renou hypothesis-testing programme](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_HYPOTHESES.md)
(spec authored by Fable 5, `claude-fable-5`). Tests H5: **MW's citation
profile is largely inherited from PWG/PW** (known philologically, never
measured). Step 2 (MG's Step-0 pilot-sheet votes → `RENOU_VALIDATION.md`) and
step 4 (H1 survival curves, explicitly gated "after Step 0 votes land") are
both still pending — the v2 remake sheet ([PR #565](https://github.com/gasyoun/SanskritLexicography/pull/565),
[H1311](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1311-Fable_RussianTranslation_renou-pilot-evidence-remake_19.07.26.md))
still shows no completed vote (only a stale 3/70-decided `decisions.json` for
the superseded v1 sheet, `sheet_id=renou-pilot-2026-07-02`, sits in
`review/`; GTD still lists the re-vote as an open `@DO` for MG). H5 is
ungated in the execution-order table, so it runs ahead of both.

Computed by Sonnet 5 (`claude-sonnet-5`).

## Method

- **Corpus** — headwords shared between MW and PWG (`{code}.renou.jsonl`,
  joined on `key1`; homographs collapsed by unioning `renou_ls` across all
  lines sharing a `key1`, matching the
  [union headword list](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md)'s
  own collapse convention). Baseline: the same comparison against AP (Apte)
  — an **independent lineage**, since MW's headword apparatus is
  Petersburg-derived while Apte is not
  ([FINDINGS §83/§97](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).
- **Signal** — `renou_ls`, the set of era-states (I–V) attested via an
  explicit `<ls>` citation marker in the dictionary's own text (as opposed to
  `renou_dcs`, the independently-derived corpus-attestation signal used by
  H6). This is the layer that would carry a copied citation apparatus.
- **Metrics**, computed only over headwords where **MW's own `renou_ls` is
  non-empty** (MW actually carries a citation there — an empty MW set is
  trivially a subset of anything and would inflate containment without
  testing inheritance):
  - **exact-match rate** — `set(MW.ls) == set(OTHER.ls)`
  - **mean Jaccard** — `|MW.ls ∩ OTHER.ls| / |MW.ls ∪ OTHER.ls|`
  - **containment** — `P(MW.ls ⊆ OTHER.ls)` — the inheritance signature: if
    MW's citation states are a subset of PWG's far more often than of AP's,
    MW's apparatus is derived from PWG's, not independently compiled.
- **Uncertainty** — 2,000-resample bootstrap 95% CIs on each metric;
  one-sided permutation test (5,000 shuffles, unpaired — the MW∩PWG and
  MW∩AP headword sets differ) on the containment gap.
- **Script** — [`src/renou_h5_lineage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_h5_lineage.py).

## Result — **H5 confirmed, decisively**

| baseline | n (MW ls non-empty) | exact-match | mean Jaccard | containment |
|---|--:|---|---|---|
| **PWG** (hypothesized lineage) | 71,229 | 0.671 [0.667, 0.674] | 0.767 [0.765, 0.770] | **0.782** [0.780, 0.785] |
| **AP** (independent baseline) | 29,563 | 0.129 [0.125, 0.133] | 0.210 [0.207, 0.214] | **0.140** [0.136, 0.144] |

Containment gap (MW–PWG minus MW–AP) = **0.6422**, one-sided permutation
p = **0.0002** (0/5,000 shuffles reached the observed gap).

Figure: [`research/figures/renou/h5_lineage.svg`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/figures/renou/h5_lineage.svg)
(containment bar chart, MW–PWG vs MW–AP, 95% bootstrap CIs).

Every metric moves the same direction, sharply: MW's `<ls>` citation states
are contained in PWG's **5.6×** more often than in AP's (78.2% vs 14.0%),
exact-match agrees **5.2×** more often (67.1% vs 12.9%), and mean Jaccard
overlap is **3.7×** higher (0.767 vs 0.210). This is not a subtle effect —
where MW cites a period, PWG independently attests that same period (or a
superset of it) in roughly 4 cases out of 5; against an unrelated
dictionary, that falls to about 1 in 7, close to what shared genuine
philological overlap (not lineage) would produce on its own. The scale (n =
71,229 MW headwords with citations, shared with PWG) also rules out the
result being a small-sample artifact — CIs on all three MW–PWG metrics are
under half a percentage point wide.

This gives a first **quantitative** measurement of a fact previously known
only philologically (per the H5 hypothesis statement itself) — MW's citation
apparatus is not an independent compilation but substantially reuses PWG's
(and, transitively, PW's) attested-period judgments for shared headwords.

## Limitations

- **Siglum-level join not attempted.** The spec names siglum-level
  containment ("shared *citations*, not just shared eras") as a stronger,
  optional extension if per-entry resolved sigla are recoverable. `renou_ls`
  only carries era-states (I–V), not resolved individual citations — that
  join was out of scope for this pass and would need a different source
  field (or a fresh sigla-resolution step) than what `{code}.renou.jsonl`
  currently exposes.
- **Containment is directional and MW-conditioned by construction** (only
  rows where MW's own `renou_ls` is non-empty are scored) — this measures
  "when MW cites a period, does PWG corroborate it," not the reverse
  direction (PWG citing something MW doesn't). The reverse containment
  (`PWG.ls ⊆ MW.ls`) was not computed; it answers a different question
  (PWG's own completeness relative to MW) not asked by H5.
- **AP as sole baseline.** The method section names AP as *the* baseline
  ("an independent lineage"); AP90 (Apte 1890) is also available in the same
  `{code}.renou.jsonl` format and was not run as a second baseline — left
  for a future pass if a human wants a robustness check across baselines
  rather than a decision this step needed to make.
- **Homograph collapse.** Unioning `renou_ls` across all lines sharing a
  `key1` (rather than attempting sense-level alignment between MW's and
  PWG's homograph numbering, which do not correspond 1:1) means the
  comparison is at the headword level, consistent with how the union
  headword list itself collapses homographs — but it cannot distinguish
  "MW's sense 2 copies PWG's sense 1" from genuine independent agreement at
  the same headword.

_Dr. Mārcis Gasūns_
