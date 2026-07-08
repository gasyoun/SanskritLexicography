# Renou H6 — agreement follows the Zipf curve

_Created: 08-07-2026 · Last updated: 08-07-2026_

Step 3 of the [Renou hypothesis-testing programme](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_HYPOTHESES.md)
(spec authored by Fable 5, `claude-fable-5`). Tests H6: **`ls`–`dcs` exact
agreement falls with lemma corpus frequency; `dcs_adds` rises with it.**
Step 2 (MG's Step-0 pilot-sheet votes → `RENOU_VALIDATION.md`) is still
pending — H6 is explicitly ungated in the execution-order table, so it runs
ahead of it.

Computed by Sonnet 5 (`claude-sonnet-5`).

## Method

- **Corpus** — the 8 canonical dictionaries
  ([`renou_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_audit.py)'s
  `CANON` tuple: PWG, MW, PW, AP, AP90, BEN, SCH, BHS), every entry in
  `{code}.renou.jsonl` carrying **both** a non-empty `renou_ls` and
  `renou_dcs` span — 172,845 such entries.
- **Frequency** — `n_texts` per lemma from
  [`dcs_lemma_renou.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/dcs_lemma_renou.json)
  (joined on `iast`, the same join `renou_audit.py` already uses for its
  suspect ranking). Per the spec's instruction to prefer an existing canonical
  frequency table over re-deriving one from the raw 1,091,528-line
  `corpus_lexicon.jsonl`: `dcs_lemma_renou.json` **is** that table — it is
  itself built from the DCS corpus and is the frequency signal this exact
  pipeline already trusts. No entries were dropped for missing frequency
  (`n_texts` was present for all 172,845 rows).
- **Trichotomy** — `relation(ls, dcs)` reused verbatim from `renou_audit.py`:
  `exact` (same era span), `dcs_adds` (dcs widens beyond ls — the over-tag
  direction), `dcs_misses` (dcs narrower), `conflict` (overlap, neither
  contains the other).
- **Binning** — fixed-width 0.5-wide bins over `log10(n_texts)`.
- **Fit** — logistic regression, `P(exact) ~ sigmoid(a·log10(freq) + b)`,
  fit on the raw (unbinned) per-entry samples via scikit-learn
  `LogisticRegression`. The 50%-crossing frequency is `10^(-b/a)`.
- **Script** — [`src/renou_h6_zipf.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_h6_zipf.py).

## Result — **H6 confirmed, and the effect is steep**

| log10(freq) bin mid | n | exact | dcs_adds | dcs_misses | conflict |
|--:|--:|--:|--:|--:|--:|
| 0.25 (≈2 texts) | 68,841 | 66.7% | 9.3% | 6.1% | 17.9% |
| 0.75 (≈6 texts) | 32,071 | 30.4% | 51.7% | 5.3% | 12.6% |
| 1.25 (≈18 texts) | 35,422 | 11.8% | 76.8% | 2.9% | 8.4% |
| 1.75 (≈56 texts) | 26,878 | 2.2% | 90.6% | 0.9% | 6.3% |
| 2.21 (≈162 texts) | 9,633 | 0.2% | 97.8% | 0.0% | 1.9% |

Fitted curve: `P(exact) = sigmoid(-2.7315 · log10(freq) + 1.1969)`.
**P(exact) crosses 50% at log10(freq) ≈ 0.44 → freq ≈ 2.7 DCS texts.**

Figure: [`research/figures/renou/h6_zipf_agreement.svg`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/figures/renou/h6_zipf_agreement.svg)
(jittered per-entry scatter + per-bin exact-rate points + fitted logistic
curve; dashed guides at the 50% crossing).

Both halves of the hypothesis hold cleanly: `exact` collapses from 66.7% to
0.2% across the frequency range, and `dcs_adds` rises in lockstep from 9.3%
to 97.8% — monotonic in every bin, no reversal. `dcs_misses` and `conflict`
both shrink with frequency too (ls's tighter, less-corroborated span becomes
rarer as the lemma is better attested in DCS — consistent with dcs simply
having more textual evidence to widen the span with, not with ls becoming
"wrong").

**The crossing point is much lower than intuition suggests — 2.7 texts, not
tens or hundreds.** A lemma attested in even 3 DCS texts already has better
than a coin-flip's chance of `dcs_adds` beating an exact match with the
lexicographer's own citation span. This is steeper than the register-level
sparsity story in F1–F3 (`RENOU.md`, `RENOU_CROSSAXIS.md`) would predict on
its own — it says the disagreement is not a tail phenomenon confined to
hapax legomena, but kicks in almost immediately past the single-attestation
floor.

## Recommendation for `renou_portrait.py`

`renou_portrait.py`'s `LOW_INFO_MIN_STATES` heuristic currently flags
low-information entries by **state count** (how many of I–V a lemma spans),
not by corpus frequency. This result suggests a complementary,
**frequency-based** confidence flag would be more principled than a fixed
state-count cutoff: any entry whose lemma has `n_texts ≥ 3` in
`dcs_lemma_renou.json` should have its `dcs`-only states (states not
corroborated by `ls` or `bhs`) surfaced as **lower-confidence** rather than
treated on par with `ls`-anchored states, since past that point `dcs_adds`
already outnumbers `exact` agreement.

**This is a recommendation only — no behavior change to `renou_portrait.py`
in this pass**, per the spec. A human should decide whether to wire a
frequency-gated confidence badge into the portrait UI, and whether 3 texts
(the crossing point) or a more conservative threshold (e.g. the bin where
`dcs_adds` first exceeds 50%, also ≈6 texts) is the better operating point —
the crossing point is where the two curves are equal, not necessarily where
the tool should switch behavior.

## Limitations

- `n_texts` counts DCS *texts* the lemma appears in, not raw token
  frequency — a lemma appearing many times in one long text scores low
  relative to one appearing once each in many short texts. This is the same
  frequency definition `renou_audit.py`'s existing suspect ranking already
  uses, kept for consistency rather than switched to a token-count measure.
- The fit pools all 8 dictionaries into one curve; per-dictionary curves
  were not fit separately (out of scope for this pass — the spec asks for
  the aggregate relationship, not a per-dict breakdown; `renou_audit.py`
  already reports per-dict trichotomy shares without frequency binning).
- `conflict` and `dcs_misses` are not modeled by the logistic fit (binary
  target is `exact` vs. not-`exact`); their bin-level trends are reported
  above but not curve-fit.

_Dr. Mārcis Gasūns_
