# H2703 — exact-request generation cold/warm

_Created: 14-08-2026 · Last updated: 14-08-2026_

Sealed DeepSeek V4 Pro experiment on the frozen H2676 22-card Q3 cohort. One compiled request per card; each request is sent twice, contiguously (cold then warm). Maximum 44 reserved base calls.

- Rule: [VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2703_generation/VERDICT_RULE.md)
- Spend: [SPEND_AUTH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2703_generation/SPEND_AUTH.md)
- Runner: [cache_generation_pairs.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_generation_pairs.py)
- Report: [cache_economy_report.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cache_economy_report.py)

`cold` / `warm` are pair positions in this sealed run, not a claim that the provider prefix cache was empty. A prior H2676 Pro call can leave prefix tokens resident; that shows up as cache-hit tokens on the first slot and is recorded, not hidden.

Adoption is not decided here. [H2704 (Grok 4.6) — PWG cache economy residual C: PREP/TM proof, bounded L3, and adoption verdict](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2704-Grok_SanskritLexicography_pwg-cache-economy-prep-tm-adoption-verdict_14.08.26.md) owns that.

_Dr. Mārcis Gasūns_
