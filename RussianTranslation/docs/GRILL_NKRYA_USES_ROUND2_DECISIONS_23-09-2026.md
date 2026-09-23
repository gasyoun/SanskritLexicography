_Created: 23-09-2026 · Last updated: 23-09-2026_

# NKRYa key: uses beyond PWG — grill round 2 decisions (23-09-2026)

Follow-up to [GRILL_NKRYA_SKILL_DECISIONS_22-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/GRILL_NKRYA_SKILL_DECISIONS_22-09-2026.md). The NKRYa (ruscorpora.ru) API key is now in the Mac keychain (service `ruscorpora-api`, stored 23-09-2026 07:39Z). MG asked what else the key can do: PWG translation, RuWritingStyles, the parallel corpus, the Rāmāyaṇa translation, CommentaryStrategies, and "study my whole GitHub". Session: Claude Code, Opus 5.5 (`claude-opus-5-5`).

## Live findings (probed 23-09-2026)

1. **Key works:** `probe` → `auth: true`; the 19th-century filter (`created` 1800–1899) is accepted (308 hits). `pair сгущаться туча` returns real lines (Аврора 2024, Дарьял 2022, Поиск 2020).
2. **ё bug — fixed this pass.** Word portraits (freq, sketch) returned null for lemmas written with ё (`сплочённый` → null, `сплоченный` → 0.94 ipm). Concordance handled ё correctly. Fix: `yo_fold()` in [nkrya_client.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nkrya_client.py) for portrait lemmas and `rank_in` matching; regression asserts in the selftest; live re-check `сплочённый` → 0.94 ipm.
3. **Rate limit:** HTTP 429 "Too many requests" after ~10 calls in a minute. The client's 1 s politeness sleep is too fast for batch runs → throttle + 429 back-off is part of H5282.
4. **Band direction:** NKRYa frequency band **1 = rarest (under 1 ipm) … 6 = most frequent** (сплоченный 1, туча 3, черный 4). Two stubs minted today had it inverted; corrected in [Uprava PR #3567](https://github.com/gasyoun/Uprava/pull/3567).
5. **MSI:** the Windows Credential Manager cannot be written or read over SSH (error 1312, "logon session does not exist"). The key must be typed once at the MSI keyboard (command in the "Human step" section below).
6. **Parallel corpus:** NKRYa has a Hindi parallel corpus (9 texts, 9,490 sentences, 122,486 words); `san` returns HTTP 500 — no Sanskrit. Details: SamudraManthanam [DECISIONS_NKRYA_PARALLEL_SUBMISSION_23-09-2026.md](https://github.com/gasyoun/SamudraManthanam/blob/main/docs/DECISIONS_NKRYA_PARALLEL_SUBMISSION_23-09-2026.md).

## MG rulings (verbatim, 23-09-2026)

Round-2 questions were asked in chat (13 questions on NKRYa uses + 9 on the parallel corpus). MG's reply, verbatim:

> 1 сейчас делай для соннета, 2 да, напиши также письмо за меня об увеличенных лимитах 3 витрина, H5263 first, остальное по рекомендации
> All 4 corpus-grounded passports at once
> store on both
> /ru-copy-pass and /litredaktor + sokratil
> Beginner Anki decks and textbooks. - grillme and mint now
> With the key, one API call can check whether any of our texts are already live in the NKRYa parallel corpora. - none are, we want to submit ours to them
> individual Kratchkovsky/Bartold/Turaev/Golenishchev style passports - ok, but Zalizniak is our main one needed now
>
> А в переводе Рамаяны? А в CommentaryStrategies? где еще применить? изучи весь мой гитхаб

How each maps:

| # | Question | Ruling |
|---|---|---|
| U1 | Unpark H5261 now | now, for Sonnet (park expires 24-09; ё fix already landed here) |
| U2 | Rate limit for H5262 | recommendation: slow + cache + resume; measure the real limit and word count first. **No multiple keys** (account-ban risk; asked separately, answered in chat) |
| U3 | H5263 before H5262 | **H5263 first** |
| U4 | Verb government in the evidence card | recommendation: yes, second pass after frequency |
| U5 | Modern vs 19th-century disagreement | recommendation: modern wins; 19th-century result is a note on the vote card |
| U6 | RWS anachronism evidence | recommendation: advisory → H5283 |
| U7 | RWS passport keyness | **all 4 at once; Zaliznyak first ("our main one, needed now")** → H5283 |
| U8 | Where the shared client lives | recommendation: csl-pyutil → H5282 |
| U9 | RWS CI | recommendation: offline cache; rebaseline folded into the owed paid-run item → H5283 |
| U10 | Key on MSI | **store on both** (human step below) |
| U11 | Copy skills | **yes: /ru-copy-pass, /litredaktor + /sokratil** → H5284 |
| U12 | Beginner Anki decks + textbooks | **grill + mint now** → H5285; grill below |
| U13 | Check our texts already in NKRYa | **none are; we want to submit** — no check needed |
| P1–P9 | Parallel corpus | in the SamudraManthanam decisions doc → H5281 + letter drafts |

## Minted (23-09-2026)

Filename token is Opus because the mint lane guard (H3470) lets a Claude Code session mint only under its own family; per acceptance rule 12 that records provenance, and **Sonnet 5 executes** (MG: «делай для соннета»).

1. [H5281](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5281-Opus_SamudraManthanam_nkrya-parallel-showcase-metadata_23.09.26.md) (🔴3 hard, class data): NKRYa parallel-corpus showcase package — real NKRYa metadata fields, rights-table fix, sphere + spot-check sheet.
2. [H5282](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5282-Opus_csl-pyutil_nkrya-client-shared-module_23.09.26.md) (🟡2 medium): shared NKRYa client in csl-pyutil with a 429-safe throttle.
3. [H5283](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5283-Opus_RuWritingStyles_nkrya-keyness-zaliznyak-first_23.09.26.md) (🔴3 hard): NKRYa keyness for style passports (Zaliznyak first, then the 4 scholars) + advisory anachronism evidence.
4. [H5284](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5284-Opus_claude-config_nkrya-step-ru-copy-litredaktor-sokratil_23.09.26.md) (🟡2 medium): NKRYa check step in /ru-copy-pass, /litredaktor, /sokratil.
5. [H5285](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5285-Opus_Systema-Sanscriticum_nkrya-beginner-gloss-lint_23.09.26.md) (🔴3 hard): NKRYa gloss lint for Russian beginner SRS decks and textbook answer keys.

## Whole-GitHub survey (23-09-2026, three read-only Explore passes)

No repo calls NKRYa yet. Candidates by value:

| Repo | What produces Russian | NKRYa use | Priority |
|---|---|---|---|
| pwg-ru-data | 11,519 PWG→RU cards; `tools/advisory_qa_gate.py` (191 term_gap, 122 polarity flags) | `nkrya_register` flag family in the QA gate; government check before `promote_final_cards.py` | high — overlaps H5262 |
| SanskritRussian | 105k root + 351k lemma glosses; `ROOT_GLOSS_REGISTER_POLICY.md` (only 5.8% of top-1 verb glosses are infinitives) | pick the lexicalized aspect partner by ipm; government check; replace the suffix-regex register classifier | high |
| CommentaryStrategies | 17,863+ notes; 611 LLM lexical notes for Sundara 68 sargas; `scripts/lexical_judge_prep.py`; `false-friends-lexicon.md` | NKRYa evidence into the lexical judge; sketch profiles of competing equivalents (долг/закон/дхарма) for the article; government audit | high |
| RussianRamayana | Leonov's books 5–7; footnote "difficult words" engine (`docs/ROADMAP_LEONOV_TRANSLATOR_ENV_RAMAYANA_5_7_2026.md` §3.3) | fifth signal: ipm band of competing classic renderings; 19th-century slice for epithet collocations (books 6–7) | medium |
| SamudraManthanam sanskritisms | ~10,664 candidate lemmas (9,459 names + 1,205 terms) | split general-Russian loanwords from corpus-only names by ipm; date first attestation by decade → the missing paper on Sanskritisms in Russian | high |
| Uprava style guide | `docs/SANSKRITISM_GUARD_RUNBOOK_RU_2026-09-19.md`, `docs/SAMSKRTE_SAMSKRTAM_EDITORIAL_STYLE_GUIDE_2026.md` | settle spelling variants (Рамаяна vs Рамайана) by corpus counts | medium |
| kosha | `data/ru_gloss/ru_gloss_layer.tsv` 2,958 rows | flag rare glosses for pedagogy | medium |
| BookIndex, IndologyScholars, SanskritSpellCheck, prefaces_* | lecture KWIC; 1,374 RU article pages; pre-1918 spelling strand; LLM preface translations | keyness; 19th-century term spread; spelling-drift baseline; calque flag | low |

Nothing to do: SanskritCorpora, Parallel-Sanskrit-Corpora (empty), Nalopakhyanam, somadeva (dormant), AfanasiyNikitin, HindiLexicography, GreekInSanskrit, ArabicInSanskrit.

## Open: Anki/textbooks grill (H5285) and the survey candidates

Asked in chat 23-09-2026; answers get appended here. Unanswered questions take the recommendation.

1. **Which files first.** `roots_frequency_ru.tsv` (570 roots, inflected glosses like «сделал») and `lemmas_for_srs.tsv` (1,286, case forms like «сближении»). **Recommendation:** these two.
2. **Mechanical lemma normalization without a vote?** Turning «сделал» into «делать» changes no meaning. **Recommendation:** automatic and reversible; votes only for synonym swaps.
3. **Teacher Memrise decks** (Кочергина ~2,160, Бюлер ~1,220 rows, teachers' wording). **Recommendation:** flag only; the teacher's wording stays, and a modern hint is added only after a vote.
4. **What counts as too rare for a beginner.** **Recommendation:** band 1 (under 1 ipm) or 19th-century-only; band 2 is a soft note.
5. **buhler-sanskrit-book dictionary** (658 rows, Лихушина 2008). **Recommendation:** later wave.
6. **Answer keys: verb government on the Кочергина методичка first.** **Recommendation:** yes.
7. **Survey candidates to mint:** CommentaryStrategies, SanskritRussian, RussianRamayana, Sanskritisms dating paper; pwg-ru-data folded into H5262. **Recommendation:** mint the first three plus the Sanskritisms paper once H5282 (shared client) lands; fold pwg-ru-data into H5262.

## Human step — the key on MSI

Windows Credential Manager refuses SSH sessions (error 1312), so at the MSI keyboard (or over Remote Desktop), in PowerShell:

```bash
python -c "import keyring,getpass; keyring.set_password('ruscorpora-api','token',getpass.getpass('NKRYa key: '))"
```

Paste the key when prompted (it is not echoed). The key is the same one as on the Mac, from [ruscorpora.ru/accounts/profile/for-devs](https://ruscorpora.ru/accounts/profile/for-devs).

_Гасунс_
