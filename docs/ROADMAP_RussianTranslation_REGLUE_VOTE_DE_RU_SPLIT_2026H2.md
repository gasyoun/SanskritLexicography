# ROADMAP — DE|RU split на голосовальных листах PWG→RU

_Created: 20-08-2026 · Last updated: 20-08-2026_

Индекс плана:
[PLAN_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT_2026-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT_2026-08.md).

## Волна 1 — сейчас (H3199, один проход 5–8 ч)

Разблокирует голосование склейки человеком на читаемой поверхности.

| ID | Поставка | Что разблокирует |
|---|---|---|
| W1.A | Флаг `split_layout` в csl-pyutil 0.22.x: wide main, две колонки, details для store, кнопки текущей карточки в `#voteBar` | Сборку обоих листов без копипаста CSS |
| W1.B | [`build_reglue_sheet_v2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_sheet_v2.py) → `h180_reglue_v6`, новый `sheet_id` | Голосование склейки |
| W1.C | [`build_g5_review_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_g5_review_sheet.py) пересрезка `--pin-ids` | Тот же G5 с новым хромом, без потери localStorage |
| W1.D | Хаб: [h180_reglue_v6.html](https://gasyoun.github.io/vote/sheets/h180_reglue_v6.html); G5 — тот же URL/файл, что в индексе, если он на хабе, иначе локальный recut | Человек голосует не с `file://` для склейки |
| W1.E | Строка в [REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md) + `@DO` голосовать v6 | Очередь человека |

Волна 1 строго последовательна внутри: A до B и C (B и C параллельны после A), D после зелёных селфтестов и браузерного прохода, E в том же проходе.

## Волна 2 — после первого голоса на v6 (не эта сессия)

Вынести флаг на другие длинные словарные листы **только если** v6 подтвердил, что
человек читает. Не дефолт для skill-mine и коротких очередей.

Не-цели волны 2 (уже отвергнуты в интервью): снимать 980px у всех листов;
ставить чипы вставки на G5; править `reglue_delta`.

## Не-цели (волна 1 тоже)

- Пересборка типологии / знаков H3152.
- Правка `pwg_ru_translated.jsonl` и csl-orig.
- Замена v5 URL (v5 остаётся для сравнения).
- Новая немецкая склейка `.de.md` как левый столбец.
- Третья колонка голоса.
- Модальное окно store.
- Жёсткая синхронизация скролла двух колонок.

## Решения — см. таблицу из 22 строк в PLAN

Здесь нет `@DECIDE`. Все развилки закрыты 20-08-2026.

_Dr. Mārcis Gasūns_
