# IMPLEMENTATION — волна 1, по шагам

_Created: 20-08-2026 · Last updated: 20-08-2026_

Индекс:
[PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT_2026-08.md).
Границы: [ARCHITECTURE](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT.md).
Приёмка: [VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT.md).

Исполнитель: [H3199 (Sonnet 5) — Wave 1: DE|RU split vote layout for h180_reglue v6 and G5 pin-ids recut](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3199-Sonnet_SanskritLexicography_reglue-vote-de-ru-split_20.08.26.md).

## Шаг 0 — деревья

Охраняемые репозитории: правки только в session-unique worktree.

```
git -C SanskritLexicography fetch origin
git -C SanskritLexicography worktree add -b h3199-reglue-vote-split ../SanskritLexicography-h3199-PID origin/master
git -C csl-pyutil fetch origin
# csl-pyutil не в списке 16 guarded; ветка от origin/main всё равно
```

`PWG_RU_DATA_ROOT` на локальное хранилище (gitignored). Без него шаг 4 не соберёт карточки.

## Шаг 1 — csl-pyutil флаг (W1.A)

Трогает: [csl_pyutil/review_sheet.py](https://github.com/sanskrit-lexicon/csl-pyutil/blob/main/csl_pyutil/review_sheet.py)
(CSS + JS + ветка в `render_review_sheet`), новый тест
`tests/test_split_layout.py`, `pyproject.toml` version `0.21.0` → `0.22.0`,
CHANGELOG пакета.

Поведение — архитектура §2. Обязательные ветки теста:

- без флага фикстура не содержит `card-split` и сохраняет `max-width:980px`;
- с флагом и `left`/`right` — две колонки, нет `max-width:980px` у `main`;
- `store_markup` есть, строка anatomy встречается только внутри details;
- без `left` при флаге — исключение;
- JS-фикстура: `#voteBar` получает кнопки, скрытый `.controls` карточки остаётся в DOM.

PR в [sanskrit-lexicon/csl-pyutil](https://github.com/sanskrit-lexicon/csl-pyutil). Не ждать мержа (решение 18).

## Шаг 2 — зависимость SanskritLexicography

Трогает: `RussianTranslation/requirements` / где сейчас пин csl-pyutil (найти
одной grep по `csl-pyutil`, не плодить второй пин). Пока PR открыт: git URL
ветки. Когда Cologne вольёт тег `0.22.0` в том же проходе — переключить на тег.
Если не вольёт: оставить git URL, записать в отчёт.

## Шаг 3 — левая колонка склейки

Трогает: [`build_reglue_sheet_v2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_sheet_v2.py)
(функция рядом с `render_card`, не новый репозиторий).

Для каждого смысла: `print_panel(collapse(pwg_de, mode))` + чипы supplements.
`data-pair` = `"{hom}:{sense}"`. Тултип = полный `de` (экранированный HTML).
`--selftest` расширить: левая колонка `gA` не содержит кириллицы в телах
значений (чипы могут нести русские ярлыки слоёв — исключить их из проверки
через класс `.chip`); каждый привязанный supplement даёт ровно один чип;
`new_senses` видны в блоке «некуда вставить».

Не вызывать `reglue_delta` заново, если знак уже лежит в JSON карточки / чипе
правой колонки — reuse `rd.deltas` только если правая колонка уже так делает
в том же проходе сборки.

## Шаг 4 — сборка v6

В `build()`: `panels` больше не держат store. Вместо:

- `left` / `right` (right = нынешние expanded+compact divs);
- `store_markup` = `anatomy.highlight(raw)`;
- `config["split_layout"] = True`;
- `sheet_id` = `h180-reglue-spotcheck-v6-2026-08-20` (дата сборки; если проход
  сорвался на следующий календарный день — дата файла, не «вчера»);
- выход `review/h180_reglue_v6_sheet.html` + новый lock + sample jsonl;
- заголовок листа: v6, не «(v3)» из текущего конфига (это ложь v5).

`digest_guard` остаётся. Смена lock/sheet_id — новая генерация, не `--pin-ids`.

Зависимость: шаги 1–3.

## Шаг 5 — G5 pin-ids recut

Трогает: [`build_g5_review_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_g5_review_sheet.py).
`split_layout True`; left `de_panel`, right `print_panel`, store в
`store_markup`. `sheet_id` не менять. Сборка только с `--pin-ids`. Дрейф —
стоп 2, не «отрезать новую партию».

Зависимость: шаг 1. Параллелен шагу 4.

## Шаг 6 — селфтесты + браузер

Команды — [VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT.md).
Браузер: карточка `gā` на v6 и одна карточка G5. Клики: пара подсветки, чип
тултипа, details store, липкая полоса при скролле на вторую карточку, узкий
вьюпорт (900px). Без голоса человека.

## Шаг 7 — публикация и хабы

- Скопировать `h180_reglue_v6_sheet.html` на хаб как
  [h180_reglue_v6.html](https://gasyoun.github.io/vote/sheets/h180_reglue_v6.html)
  тем же рецептом, что v5 (клон `gasyoun.github.io`, каталог `vote/sheets/`).
  v5 **не** удалять.
- G5: если индекс даёт хаб-URL — перезаписать тот файл; если только `file://` —
  recut локальный gitignored, индекс обновить «переиздан, sheet_id тот же».
- [REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md):
  новая строка v6 (🟢, 15 карточек, hub URL); v5 → ⚫ SUPERSEDED как v3 в своё время,
  «голос — v6».
- GTD `@DO`: проголосовать
  [h180_reglue_v6](https://gasyoun.github.io/vote/sheets/h180_reglue_v6.html)
  (15 карточек). Полный URL, не «лист на хабе».
- CHANGELOG SanskritLexicography `[Unreleased]` + `/cut-release` в том же проходе.

## Забор на каждом шаге

Не открывать `pwg_ru_translated.jsonl` на запись. Не трогать
[`reglue_delta.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reglue_delta.py).
Не коммитить csl-orig. Не менять id/текст карточек G5.

_Dr. Mārcis Gasūns_
