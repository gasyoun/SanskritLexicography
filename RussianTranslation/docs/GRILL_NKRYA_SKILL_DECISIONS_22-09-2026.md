_Created: 22-09-2026 · Last updated: 23-09-2026_

# NKRYa skill: grill decisions (22-09-2026)

This grill was born from the H5069 chat vote, where MG wrote on C07: «используй стабильно данные НКРЯ. Если речь про тучи, то тучи сгущаются, тучи не могут быть последовательными». The goal is that Russian word and collocation choices in PWG-RU rest on data from the Russian National Corpus (НКРЯ, ruscorpora.ru), not on intuition. The questions were asked through the interactive question tool; the answers below are verbatim rulings. Vote record: [H5069_CHAT_VOTE_DECISIONS_C01-C09_22-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5069/H5069_CHAT_VOTE_DECISIONS_C01-C09_22-09-2026.md).

## Homework (before the questions)

1. **Official API:** [ruscorpora/public-api](https://github.com/ruscorpora/public-api), last pushed 25-11-2025.
   - Bearer token from the NKRYa personal account ([for-devs](https://ruscorpora.ru/accounts/profile/for-devs)).
   - `word-portrait` gives `PORTRAIT_SKETCH` (collocations, dice metric) and `PORTRAIT_FREQUENCY` (ipm plus a 1–6 category); there is also concordance search.
   - The [openapi.json](https://ruscorpora.ru/api/v1/openapi.json) answered 200 on 22-09-2026.
2. **No token on the Mac:** the keychain has no `ruscorpora` item, and no repo `.env` has one.
3. **In the estate, NKRYa is only an export target:** [SamudraManthanam nkrya-parallel](https://github.com/gasyoun/SamudraManthanam/tree/main/nkrya-parallel) and [ROADMAP_NKRYA_PARALLEL_RUSCORPORA_2026_2027.md](https://github.com/gasyoun/SamudraManthanam/blob/main/docs/ROADMAP_NKRYA_PARALLEL_RUSCORPORA_2026_2027.md). No query tool exists anywhere.
4. **User clients:** [kunansy/rnc](https://github.com/kunansy/rnc) is an HTML scraper (last pushed 2023); [kmike/ruscorpora-tools](https://github.com/kmike/ruscorpora-tools) covers only the free subset.

## Rulings

| # | Question | MG's answer |
|---|---|---|
| 1 | Token: how obtained and stored | **Unlimited key, both boxes** (non-expiring key; Mac keychain + MSI credential store; never in git) |
| 2 | Default subcorpus | **MAIN modern + 19c check** (recommended) |
| 3 | What the evidence does | **Evidence card, human votes** (recommended); advisory, no auto-apply |
| 4 | Scope of the first handoff | **all 3**: client + skill + C07 pilot; store batch audit; c1 prompt evidence |
| 5 | Paid c1 calls for the A/B test | **Pre-authorize 5 calls** (one 5-card volume; more needs a new yes) |
| 6 | Batch audit unit | **Every content word ipm** |
| 7 | Where flagged cards go | **Review sheets ≤10 cards** (recommended) |
| 8 | Handoff shape | **3 handoffs, batch mint** (recommended) |

## Minted

1. [H5261](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5261-Opus_SanskritLexicography_nkrya-client-skill-c07-pilot_22.09.26.md) (Opus 5 filename token; Sonnet 5 suffices, 🟡2 medium): the NKRYa corpus client, the `/nkrya` skill, and the C07 clouds pilot on real data.
2. [H5262](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5262-Opus_SanskritLexicography_nkrya-store-ipm-batch-audit_22.09.26.md) (Opus 5, 🔴3 hard): an NKRYa ipm batch audit of every PWG-RU store content word, with flags going to vote sheets of ≤10 cards. Depends on H5261.
3. [H5263](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5263-Opus_SanskritLexicography_nkrya-c1-prompt-evidence-ab_22.09.26.md) (Opus 5, 🟡2 medium): an NKRYa evidence block in the c1 prompts, A/B tested on one 5-card volume (≤5 paid calls). Depends on H5261.

The filename token is Opus because the mint lane guard (H3470) lets a Claude Code session mint only under its own family. Per acceptance rule 12 this records provenance; it does not reserve the executor.

## Human step (blocks H5261's live queries)

MG generates a non-expiring API key in the NKRYa account (ruling 1). The H5261 executor stores it; it is never pasted into chat or git.

Follow-up: round 2 (other uses of the key, 23-09-2026) — [GRILL_NKRYA_USES_ROUND2_DECISIONS_23-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/GRILL_NKRYA_USES_ROUND2_DECISIONS_23-09-2026.md).

_Гасунс_
