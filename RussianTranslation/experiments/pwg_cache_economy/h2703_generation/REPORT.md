# H2703 — exact-request Pro generation cold/warm

_Created: 14-08-2026 · Last updated: 14-08-2026_

**Generation-lane verdict: PASS.** Adoption is not decided here; that is [H2704 (Grok 4.6) — PWG cache economy residual C: PREP/TM proof, bounded L3, and adoption verdict](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2704-Grok_SanskritLexicography_pwg-cache-economy-prep-tm-adoption-verdict_14.08.26.md).

Rule: [VERDICT_RULE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2703_generation/VERDICT_RULE.md). Spend: [SPEND_AUTH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2703_generation/SPEND_AUTH.md). Summary: [run/summary.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/pwg_cache_economy/h2703_generation/run/summary.json).

## Frozen before token 1

| Clause | Sealed value | Measured | Hold |
|---|---|---|:---:|
| Pairs | 22 | 22 | yes |
| Parseable | ≥42/44 | 42/44 (95.5%) | yes |
| Served model | deepseek-v4-pro | see per-slot table | yes |
| Unique det_clean cards | context (H2676=21) | 20 | n/a |
| USD / unique clean | H2676 $0.01991 | 0.027798 | n/a |
| Canonical hashes | equal freeze | True | yes |
| Promotable | false | false | yes |

Sealed source commit: `f9b2a252451495f59b1a719fa173ae6121497db2`. Price card `pre-1608`. Slot 44 (`vicitra` warm) was dispatched after a `MemoryError` while re-hashing the canonical store before that last reserve; the runner was slimmed to rehash only the four canonical files and resume kept the sealed request identities. Two warm slots (`d_ikz_a`, `pf_tak`) returned no body (`served=None`, cost unevaluable) and count as the two unparseable terminals.

## Economy

| Arm | n | total USD | mean USD | median USD | mean cache-hit tokens |
|---|---:|---:|---:|---:|---:|
| cold | 22 | 0.300805 | 0.013672972727272727 | 0.013402 | 13585.454545454546 |
| warm | 20 | 0.255151 | 0.012757547499999999 | 0.01354368 | 13049.6 |

Paired delta (warm − cold): n=20 mean=-0.0008821370000000004 median=0.0003071100000000002 bootstrap 95% CI [-0.0024699745000000004, 0.0005983424999999994].

Total attributable USD **0.555956**. Cost per unique clean card **$0.02780**, above the H2676 one-shot baseline **$0.01991**, because this lane bought two generations per card. Retry amplification **1.0**. Mean cache-hit tokens were already high on the first slot of each pair (about 13.6k), so this run's `cold` label is pair position, not an empty provider prefix. The paired USD delta CI crosses zero. A cache hit is explanatory, not an accepted artifact.

## Per pair

| key / request | cold parse | warm parse | cold clean | warm clean | cold USD | warm USD | delta | blind |
|---|:---:|:---:|:---:|:---:|---:|---:|---:|---|
| `ya_tepsita` | True | True | True | True | 0.00890892 | 0.00958665 | 0.0006777299999999997 | disagree |
| `vi_svaha` | True | True | True | True | 0.00858003 | 0.00976584 | 0.001185809999999999 | equivalent_structure |
| `vi_sa` | True | True | True | False | 0.01334046 | 0.01474377 | 0.0014033099999999996 | disagree |
| `dr_ava_ra` | True | True | True | True | 0.01603337 | 0.01372526 | -0.002308110000000002 | disagree |
| `par_rin` | True | True | True | True | 0.01508713 | 0.0168193 | 0.0017321699999999982 | equivalent_structure |
| `sa_msargin` | True | True | True | True | 0.015142 | 0.01071805 | -0.004423949999999999 | equivalent_structure |
| `kakz_ivant` | True | True | True | True | 0.01170275 | 0.01366721 | 0.001964460000000001 | disagree |
| `a_ngaja` | True | True | True | True | 0.01346354 | 0.01731503 | 0.003851489999999999 | equivalent_structure |
| `vyatyaya` | True | True | True | True | 0.01263417 | 0.01315008 | 0.0005159099999999996 | equivalent_structure |
| `roza` | True | True | True | True | 0.00855297 | 0.00624573 | -0.0023072400000000003 | equivalent_structure |
| `pras_u` | True | True | True | True | 0.01198353 | 0.01362695 | 0.0016434200000000013 | disagree |
| `div_a` | True | True | True | True | 0.00917534 | 0.01076483 | 0.001589489999999999 | equivalent_structure |
| `vazawk_ara` | True | True | True | True | 0.00961112 | 0.00627206 | -0.0033390600000000005 | equivalent_structure |
| `anar_ta` | True | True | True | True | 0.01364325 | 0.01662909 | 0.0029858399999999983 | equivalent_structure |
| `sa_b_ajay` | True | True | True | True | 0.01038887 | 0.01048718 | 9.831000000000076e-05 | disagree |
| `vi_d` | True | True | True | True | 0.0172249 | 0.01346041 | -0.0037644900000000005 | disagree |
| `d_ikz_a` | True | False | False | False | 0.01469943 | None | None |  |
| `p_avana` | True | True | True | False | 0.02102964 | 0.01580094 | -0.005228699999999999 | disagree |
| `pf_tak` | True | False | True | False | 0.01331228 | None | None |  |
| `yatna` | True | True | True | True | 0.01709576 | 0.01580642 | -0.00128934 | disagree |
| `ras` | True | True | True | False | 0.01716513 | 0.01518414 | -0.00198099 | disagree |
| `vicitra` | True | True | False | False | 0.02203081 | 0.01138201 | -0.010648800000000002 | disagree |

Fail reasons: none.

## What this does not authorise

- Adoption of prefix cache as the default PWG generation route (H2704).
- TM / store write or auto-promote.
- Flipping `DEFAULT_MODEL` off Flash.
- Q4 / monster / unattended partition.

_Dr. Mārcis Gasūns_
