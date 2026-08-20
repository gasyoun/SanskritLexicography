# ARCHITECTURE — split_layout для review sheet

_Created: 20-08-2026 · Last updated: 20-08-2026_

Индекс:
[PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT_2026-08.md).

## 1. Границы

```
csl-pyutil render_review_sheet
    config["split_layout"] = True     # opt-in; default False = 980px как сейчас
    item["left"] / item["right"]      # HTML колонок
    item["store_markup"]              # emitter wraps in details
         │
         ├─ build_reglue_sheet_v2.py  # W1.B: PWG skeleton + chips | glued RU
         └─ build_g5_review_sheet.py  # W1.C: de_panel | print_panel
```

Шаблон не знает про склейку и PWG. Билдер не дублирует CSS ширины. Anatomy
остаётся [`csl_pyutil.anatomy`](https://github.com/sanskrit-lexicon/csl-pyutil/blob/main/csl_pyutil/anatomy.py)
(H1646/H1808) — не второй подсветчик.

## 2. Флаг `split_layout`

Когда `False` (дефолт): байт-поведение нынешних листов, `main` 980px.

Когда `True`:

- `main` и `footer.hint` без max-width (padding 12px 16px).
- Карточка: сетка две колонки `1fr 1fr`, зазор 16px; колонки `min-height: 0`,
  каждая `overflow: auto` и `max-height: calc(100vh - 220px)` — независимый скролл.
- `@media (max-width: 900px)`: одна колонка, DE затем RU.
- `.controls` и `textarea.note` в карточке скрыты (`display:none`); JS копирует
  их в существующий `#voteBar` (V17) для карточки, чей верх пересекает середину
  вьюпорта (`IntersectionObserver`, порог 0.4). Смена карточки при скролле меняет
  полосу. Экспорт и localStorage остаются привязаны к `id` карточки, не к клону в
  полосе: клон — зеркало, клик пишет в оригинал (скрытый в карточке, не
  удалять из DOM).
- `item["store_markup"]`: одна строка-ссылка («разметка store — цитировать в
  заметке»), внутри закрытый details. Открытый details не стоп.

Имя флага одно. Четыре куска хрома не разводятся отдельными булями — решение 13.

## 3. Данные левой колонки склейки

Источник: `reglue/<key1>.json`, поля `pwg_de` на каждом смысле PWG и `de` на
каждом supplement. Не csl-orig, не `.de.md`.

На смысле: немецкий `pwg_de` (через тот же `print_panel` / line_collapse, что RU),
затем чипы привязанных supplements. Чип: знак типологии (уже посчитанный
`reglue_delta`, не пересчитывать), слой (`PW`/`NWS`/`SCH`), `data-pair="HOM:SENSE"`.
Полный `de` дополнения — атрибут тултипа (не `title=`): CSS hover на десктопе,
тап закрепляет `.pinned` на узком, второй тап или клик вне снимает.

Новые смыслы без цели PWG (`new_senses`) — блок внизу левой колонки «некуда
вставить», те же чипы. Иначе «куда» для неразмещённых дополнений пропадает.

`data-pair` на русском блоке «привязано к смыслу PWG N» тот же ключ. Клик на
любой стороне добавляет класс подсветки паре и `scrollIntoView` в другой колонке
**этой карточки**, не синхронизируя скролл целиком.

## 4. Правая колонка склейки

Существующий `render_card` expanded + compact. Переключатель «компактно» уже
CSS `:has(#modecompact)` — распространить на `.col-de` так же, как на
`.render-compact` / `.render-expanded`. Слева компакт = `line_collapse` на
`pwg_de`, чипы на месте (решение 16).

## 5. G5

Три панели H1808 сжимаются в split: left = `de_panel(sense.german)`, right =
`print_panel(ru)`, `store_markup` = `store_panel`. Чипов нет. `--pin-ids` как в
нынешнем билдере: дрейф текста — стоп, не новая партия.

## 6. Build-vs-reuse

| Кусок | Вердикт |
|---|---|
| Ширина / липкий футтер / anatomy / G5 DE-панель / `pwg_de` / V17 `#voteBar` | reuse |
| Флаг `split_layout`, сетка, details-обёртка, observer кнопок, чип+тултип, `data-pair` | build |
| Второй резолвер, второй anatomy, немецкий из csl-orig, glued `.de.md` слева | не строить |

## 7. Совместимость

`extras=False` (donor fixture) флага не видит. Листы без `left`/`right` при
`split_layout=True` — `ValueError` на сборке, не молчаливый 980px.

Версия пакета: текущий тег csl-pyutil `0.21.0` → `0.22.0` (minor: новый opt-in
флаг). SanskritLexicography до мержа Cologne ставит git-URL ветки PR.

_Dr. Mārcis Gasūns_
