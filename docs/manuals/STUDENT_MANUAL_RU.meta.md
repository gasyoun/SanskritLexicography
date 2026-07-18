# STUDENT_MANUAL_RU.md — metadoc

_Created: 18-07-2026 · Last updated: 18-07-2026_

Companion record for [docs/manuals/STUDENT_MANUAL_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/STUDENT_MANUAL_RU.md) (Russian).

## Purpose & audience

Что студент санскрита может использовать уже сегодня: лекции по синтаксису, парадигмы, обратный словарь, mw_ru — без внутренней кухни. Аудитория — студент, не оператор.

## Provenance

Authored 10-07-2026 (H479/H535). Refreshed 18-07-2026 under [H1245](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1245-Fable_multi_big-manuals-estate-refresh-umbrella_18.07.26.md): the ReverseDictionary section rewritten to the post-incident reality (tracked `.mdx` set is the browser-usable layer; the legacy `.txt` files live only in a local backup outside the repo; the 266k list stays rights-gated).

## Verification

```
LAST_VERIFIED: 18-07-2026
VERIFIED_BY: Fable 5 (claude-fable-5), H1245
COMMANDS_SPOT_RUN: 2
```

Executed 18-07-2026: both §2 commands verbatim — `python src/nominal_grammar.py --table agni m.` (correct agni i-stem declension table) and `python src/reverse_index.py --show "m·8n*"` (138 headwords) — plus the fact-check agent's path/count sweep (7 Apte particle files, 7,537 JSONL records, learner-core 22,772).

## Improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | Point the ReverseDictionary section at concrete `.mdx` starting files once the set stabilises | open |

## Known limitations

- Русский текст без ё (правило репозитория).

## Intended use / known misuse

**Для:** самостоятельного студента. **Не для:** оценки состояния конвейеров или прав на данные — это другие руководства.

## Maintenance & sunset plan

Refreshed by [/workspace-manual](https://github.com/gasyoun/claude-config/blob/main/commands/workspace-manual.md) passes; H1246 consumes the Verification block.

## Deprecation status

`active`

## Revision history

| Date | Change | By |
|---|---|---|
| 10-07-2026 | Subject manual authored (H479/H535); ё dropped per H543 11-07-2026 | Fable 5 (`claude-fable-5`) |
| 18-07-2026 | Metadoc created (H1245 estate refresh); ReverseDictionary section rewritten to post-incident reality | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
