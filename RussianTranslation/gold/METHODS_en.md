# EN gold sample — METHODS

Ground truth: **faithful to the PWG German** sense (FU1 decision 6). Monier-Williams is a
cross-check only and is **withheld from the reviewer sheet** to avoid anchoring.

- Population: tri-lingual store rows carrying `en` (60 sampled).
- Strata: DCS freq band x source_type x stratum, fixed seed, proportional with a per-cell floor.
- Reviewer sheet shows headword + German (de) + English (en) only; label vocabulary: `correct`, `lemma-variant`, `proper-name`, `partial`, `wrong-sense`, `hallucinated`.
- GOOD = {correct, lemma-variant, proper-name}; ERR = {wrong-sense, hallucinated}.
- Two annotators -> `gold_agreement.py` reports precision (Wilson 95%% CI) + Cohen kappa.
  The working sample aliases `period`=freq-band and `kind`=source_type so that scorer is
  reused unchanged.

## Sample composition (freq_band x source_type)

| freq_band | source_type | n |
|---|---|---:|
| band0 | attested | 8 |
| band1 | attested | 4 |
| band2 | attested | 5 |
| band3 | attested | 2 |
| band4 | attested | 8 |
| band4 | lexicographic | 1 |
| band5 | attested | 28 |
| band5 | lexicographic | 3 |
| band5 | mixed | 1 |
