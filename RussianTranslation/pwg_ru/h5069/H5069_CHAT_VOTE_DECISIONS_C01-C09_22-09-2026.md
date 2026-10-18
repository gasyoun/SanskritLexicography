_Created: 22-09-2026 · Last updated: 22-09-2026_

# H5069 — chat vote on corrections C01–C09 (22-09-2026)

MG voted in chat on 22-09-2026 on the nine corrections staged by the H5069 source-support audit. The Codex Astra review is recorded in [H5069_ASTRA_REVIEW_ADJUDICATION_22-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5069/H5069_ASTRA_REVIEW_ADJUDICATION_22-09-2026.md). The vote was taken with the interactive question tool; the answers are copied verbatim below. The outcome is recorded in the `vote_22_09_2026` column of [corrections_proposed.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5069/corrections_proposed.tsv). **The store is not written.** `applied` stays `no` until the editorial apply step runs.

| id | MG's answer (verbatim) | Outcome | Final proposal |
|---|---|---|---|
| C01 | Approve (Recommended) | approved | оттеснять первую жену (acc.) второй женой (instr.) |
| C02 | Approve (Recommended) | approved | связывать союзом, объединять |
| C03 | «следовать, таща за собой» | approved, amended | следовать, таща за собой |
| C04 | Approve (Recommended) | approved | {%брать в жёны%} |
| C05 | best. comes from bestimmte. We have a rule that no German abbreviations get to Russian translation. Have you lost context? опред. от определенный | approved, amended | определ. построения войск |
| C06 | Approve (Recommended) | approved | сгущаться, становиться твёрдым —, плотным |
| C07 | используй стабильно данные НКРЯ. Если речь про тучи, то тучи сгущаются, тучи не могут быть последовательными | **deferred** | pending an NKRYa-grounded replacement |
| C08 | Approve (Recommended) | approved | {%привязанный к%} |
| C09 | «произносить, читать наизусть» | approved, amended | {%произносить, читать наизусть%} |

## Notes

1. **C05: German abbreviation removed.** The staged proposal kept `<ab>best.</ab>`, which violates the standing rule that no German abbreviation reaches the Russian text. The repository's voted mapping ([src/pwg_ab_ru.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py) `RU_MAP`, `'best.': 'определ.'`, voted in H1303/H1682) gives «определ.». MG wrote «опред.». This record uses the voted map form «определ.» for consistency with the rest of the store. **Open question:** if «опред.» should replace «определ.» everywhere, that is a change to RU_MAP, not to this row.
2. **C07: deferred.** Russian collocation choices must be grounded in data from the Russian National Corpus (NKRYa), not in intuition. The replacement for «последовательный» (of clouds) waits for the NKRYa tool handoff born from this vote.
3. The eight approved rows go to the store only through the existing editorial apply path. This vote does not write to the store.

_Гасунс_
