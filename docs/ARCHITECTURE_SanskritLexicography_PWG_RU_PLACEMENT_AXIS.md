# ARCHITECTURE — ось привязки в сайдкаре pwg_ru

_Created: 16-08-2026 · Last updated: 16-08-2026_

Обложка и решения: [PLAN_SanskritLexicography_PWG_RU_PLACEMENT_AXIS_SPLIT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_PLACEMENT_AXIS_SPLIT.md).

## Что сейчас

[`edition_rel.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/edition_rel.py)
`classify_edition_rel` вычисляет две вещи независимо:

- **строка 146** — `target_sense = si if si else "*new"`, где `si` — ведущее число тега
  смысла **самой добавки** (нумерация PW, не указатель на PWG);
- **строки 187–189** — `subtype = "restate"` в ветке слоя `pw`, `target_sense` не читается.

Ничто между ними их не сверяет, поэтому `restate` уживается с `target_sense='*new'`.

## Разделение осей

`subtype` сегодня несёт два утверждения. Разводим их так:

| утверждение | где живёт после волны 1 | когда верно |
|---|---|---|
| «слой PW сокращает PWG» | `direction: "abridging"` (**уже есть**, не трогаем) | всегда, привязка не нужна |
| «эта добавка относится к **вот этому** смыслу» | `placement: bool` (**новое**) | только когда цель найдена в скелете PWG |
| «характер отношения» | `subtype` (как есть) | читается **только вместе с** `placement` |

`subtype` намеренно **не переименовывается** у непривязанных: дублирование одного факта
в двух полях гарантированно разойдётся (решение 7).

## Контракт полей

Внутри `relationship` в `pwg_ru_relationships.jsonl`:

```json
{
  "subtype": "restate",
  "op": "restate",
  "direction": "abridging",
  "placement": false,
  "placement_reason": "no_target_marker",
  "placement_hypothesis": null,
  "insertion_point": {"key1": "Ap", "homonym": "h0", "target_sense": "*new", "anchor": "sense"}
}
```

**`placement`** — `true` тогда и только тогда, когда `(key1, homonym, target_sense)` после
нормализации находится среди смыслов слоя `pwg`. Никаких других источников истины.

**`placement_reason`** — ровно одно из:

| значение | смысл | ожидаемый объём |
|---|---|---|
| `found` | цель найдена | ~549 + то, что добавит нормализация |
| `no_target_marker` | `target_sense == "*new"`: у тега добавки нет ведущего числа, цели нет по построению | ~4 618 |
| `out_of_range` | номер цели **выше** максимального числового смысла PWG у этой статьи/омонима | ~381 |
| `not_found` | номер внутри диапазона, но такого смысла нет | остаток от 560 после нормализации |

Различение `no_target_marker` / `out_of_range` / `not_found` — то, ради чего вводится
`reason`: это три разных явления, и только последнее похоже на дефект данных.

**`placement_hypothesis`** — `null` либо
`{"target": "<sense>", "method": "<named>", "confidence": "<low|medium>"}`.
Заполняется **только** именованным детерминированным методом. В волне 1 такой метод один:
`normalized_tag_match`. Гипотеза **никогда** не влияет на `placement` и никогда не
подставляется в `insertion_point`.

## Нормализация тегов смыслов

Новая функция `normalize_sense_tag(tag)` в `edition_rel.py`. Консервативно (решение 6):

- срезать хвостовую пунктуацию и пробелы: `'1)'` → `'1'`, `'1 '` → `'1'`;
- ничего больше не трогать.

**Не сливаются** (и это существо решения):

| тег | почему остаётся отдельным |
|---|---|
| `1-sub-einen Damm durchbrechen` | подсмысл — не смысл 1 |
| `1 (PW)` | смысл с чужим провенансом |
| `Nachtrag`, `addendum` | правка **к** смыслу, отдельный тип (волна 2) |
| `caus-1`, `anu-1` | смысл в другой грамматической ветке |

Нормализация применяется **симметрично** — и к тегам скелета PWG при построении индекса,
и к `target_sense` при поиске. Асимметрия дала бы новый класс промахов.

## Границы

- **Канонический store — только чтение.** `pwg_ru_translated.jsonl` не трогается ничем
  в этой волне. Число строк (`rows=11715`) — стоп-условие.
- **`direction`, `op`, `evidence`, `confidence` не меняют семантику.** Меняется только то,
  что добавляется рядом.
- **Потребители сайдкара** — [`build_reglue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue.py),
  [`build_reglue_evidence_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_evidence_sheet.py),
  [`build_reglue_sheet_v2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_sheet_v2.py),
  [`reglue_overlap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reglue_overlap.py).
  Все читают `insertion_point.target_sense`; после волны 1 они должны читать `placement`,
  а не заново вычислять «нашлась ли цель».
- **Обратная совместимость:** новые поля добавляются, старые остаются. Потребитель, не
  знающий про `placement`, продолжает работать как раньше — но именно поэтому все
  перечисленные потребители обновляются в этой же волне, иначе расхождение сохранится.

## Сборка vs переиспользование

| кусок | вердикт |
|---|---|
| классификатор отношений | **переиспользовать** `edition_rel.py`, править на месте |
| сборщик сайдкара | **переиспользовать** `build_relationships.py` |
| нормализация тегов | **писать новое** — в репо нет ничего подобного (`safe_filename.py` решает другую задачу) |
| замер проверяемости до/после | **переиспользовать** счётчик из `build_reglue_evidence_sheet.py` |
| метрика пересечения глосс | **не трогать** — измерена и отвергнута как признак |

_Dr. Mārcis Gasūns_
