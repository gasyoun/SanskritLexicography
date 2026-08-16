# IMPLEMENTATION — волна 1, пошаговая сборка

_Created: 16-08-2026 · Last updated: 16-08-2026_

Обложка и решения: [PLAN_SanskritLexicography_PWG_RU_PLACEMENT_AXIS_SPLIT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_PLACEMENT_AXIS_SPLIT.md)
· схема: [ARCHITECTURE](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_PWG_RU_PLACEMENT_AXIS.md)
· приёмка: [VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_SanskritLexicography_PWG_RU_PLACEMENT_AXIS.md)

Шаги строго по порядку: каждый опирается на предыдущий. Все пути — от
`C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation`.
Работать в изолированном worktree off `origin/master`.

## S0 — базовый замер (до любых правок)

Зафиксировать исходные числа, иначе нечем будет доказать эффект:

```
python src/build_reglue_evidence_sheet.py 2>&1 | grep "cards drawn"
```

Записать `checkable / no_target / too_thin` (ожидаемо 246 / 4 690 / 303) в отчёт прогона.
Ничего не коммитить.

## S1 — `normalize_sense_tag` в `edition_rel.py`

Новая чистая функция рядом с `classify_edition_rel`:

- срезает хвостовую пунктуацию (`)`, `.`, `,`) и пробелы;
- **ничего** больше не меняет;
- идемпотентна: `f(f(x)) == f(x)`.

Селфтест в том же файле (`selftest()` уже существует, дописать в него):
`'1)'→'1'`, `'1 '→'1'`, `'1'→'1'`, и **обязательные негативы** —
`'1-sub-einen Damm durchbrechen'`, `'1 (PW)'`, `'Nachtrag'`, `'caus-1'` не меняются.

## S2 — индекс смыслов PWG строится по нормализованному ключу

Там, где собирается набор существующих смыслов PWG (см. `build_pwg_gender_index` и
потребителей `insertion_point`), ключ строится через `normalize_sense_tag`.
**Симметрия обязательна:** и скелет, и `target_sense` проходят одну функцию.

## S3 — вычислить `placement` / `placement_reason`

В `classify_edition_rel`, **после** того как `target_sense` определён, и **до**
формирования `rel`:

1. `target_sense == "*new"` → `placement=False`, `reason="no_target_marker"`.
2. Иначе нормализовать и искать в индексе PWG:
   - нашлось → `placement=True`, `reason="found"`;
   - не нашлось и номер **выше** максимального числового смысла этой статьи/омонима →
     `reason="out_of_range"`;
   - не нашлось иначе → `reason="not_found"`.

Максимальный числовой смысл считать по **нормализованным** тегам, только по тем, что
целиком число.

> Для этого `classify_edition_rel` нужен доступ к индексу смыслов PWG, которого у неё
> сейчас нет (она получает только `pwg_gender_index`). Передать вторым индексом —
> **не** переиспользовать `pwg_gender_index`: он про род, и его состав может измениться
> независимо.

## S4 — `placement_hypothesis`

Заполнять **только** когда `placement=False`, `reason` ∈ {`not_found`}, и
нормализованный тег совпал бы при менее строгой нормализации. Метод — литерал
`"normalized_tag_match"`, `confidence: "low"`.
Во всех прочих случаях — `null`. Гипотеза никогда не пишется в `insertion_point`.

## S5 — сборщик сайдкара пробрасывает новые поля

В [`build_relationships.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_relationships.py)
(словарь `rel`, ~строки 66–75) добавить `placement`, `placement_reason`,
`placement_hypothesis`. Существующие ключи не трогать.

## S6 — обновить потребителей

Все четыре читают «нашлась ли цель», вычисляя это заново; заменить на чтение `placement`:

- `build_reglue.py` — `*new` ветка;
- `build_reglue_evidence_sheet.py` — построение checkable-пула;
- `build_reglue_sheet_v2.py` — чипы;
- `reglue_overlap.py` — отбор пар.

В карточке листа показывать `placement_reason` словами: «цель не указана» /
«номер выше диапазона PWG» / «смысл не найден».

## S7 — проверка перед регенерацией листов (стоп-условие)

Перед перегенерацией листов убедиться, что по ним **не поданы голоса**: отсутствуют
`review/*_decisions.json` для `h180-reglue-evidence-2026-08-15` и
`h180-reglue-spotcheck-v2-2026-08-15`. **Если голоса есть — остановиться и сообщить**;
решение 8 в этом случае уступает правилу H1404.

## S8 — регенерация

```
python src/build_relationships.py
python src/build_reglue.py
python src/build_reglue_sheet_v2.py
python src/build_reglue_evidence_sheet.py
```

Листы регенерируются (решение 8). Локи обновляются (`REVIEW_LOCK_FORCE=1` только если
шаг S7 прошёл).

## S9 — замер после и дельта

Повторить S0. В отчёт: было/стало по `checkable`, и распределение `placement_reason`
по всем 5 603 строкам. **Ожидание:** `no_target_marker` ≈ 4 618 (не должен вырасти),
`found` вырос за счёт `not_found`, `out_of_range` ≈ 381 (не должен измениться —
нормализация на него не влияет по построению).

## S10 — документы и закрытие

- `REGLUE_SPEC.md` — новый раздел про две оси и `placement`, с числами до/после.
- `FINDINGS` — дописать в §541 результат (не новый §).
- `CHANGELOG.md` — запись; затем `/cut-release`.
- Комментарий в [issue #1736](https://github.com/gasyoun/SanskritLexicography/issues/1736)
  с дельтой; **не закрывать** issue — в нём остаются волны 2–4.
- commit → PR → merge.

_Dr. Mārcis Gasūns_
