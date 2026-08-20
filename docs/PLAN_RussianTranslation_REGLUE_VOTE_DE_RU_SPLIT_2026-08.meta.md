# Метадок — PLAN DE|RU split голосовального листа

_Created: 20-08-2026 · Last updated: 20-08-2026_

Спутник
[PLAN_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT_2026-08](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT_2026-08.md).

## Зачем существует

План отвечает на замечание MG к
[h180_reglue_v5](https://gasyoun.github.io/vote/sheets/h180_reglue_v5.html)
(store сразу виден, нет немецкого оригинала рядом, 980px) и рассчитан на
исполнителя без человека на 5–8 часов. 22 решения записаны; развилок нет.

## Кто читает

- **Исполнитель H3199** — стартует от PLAN, шаги в
  [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT.md).
- **Следующая сессия по листам PWG** — таблица prior-art: не строить второй
  anatomy и не ставить glued `.de.md` слева.

## Что нельзя менять молча

- Таблица 22 решений — только новым интервью с датой.
- Забор и пять стопов.
- Строка «левый столбец = `pwg_de`, не `.de.md`».

## Что устаревает первым

| Кусок | Когда | Признак |
|---|---|---|
| Пин csl-pyutil git-URL | Cologne вольёт 0.22.0 | requirements всё ещё указывает на ветку PR |
| «v5 без голосов» | кто-то проголосует v5 до v6 | localStorage на старом `sheet_id` |
| Порог 900px / 220px | браузерный проход подвинет константы | CSS не совпадёт с IMPLEMENTATION |

## Соседи

- [PLAN reglue2](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_RussianTranslation_REGLUE2_CITATIONS_TYPOLOGY_2026-08.md) — цитаты и типология, эта волна их не трогает.
- [g5_card_render.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/g5_card_render.py) — три панели, которые split сжимает.
- [csl-pyutil review_sheet.py](https://github.com/sanskrit-lexicon/csl-pyutil/blob/main/csl_pyutil/review_sheet.py) — 980px и V17 `#voteBar`.
- [REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md) — строка v5, которую v6 сменит как votable.

## Intended use

Консультация на время сборки v6 и G5 recut. После зелёного хаба читают lock и
индекс листов, не этот план.

## Maintenance and sunset

После мержа H3199 и публикации v6: статус PLAN → executed. Волна 2 (флаг на
другие длинные листы) — только после голоса на v6, отдельный хэндоф. Не
расширять этот файл «заодно» новыми листами.

## Deprecation status

Active. Sunset: когда v6 проголосован или снят, и флаг либо в дефолте csl-pyutil,
либо сознательно не пошёл дальше двух билдеров.

_Dr. Mārcis Gasūns_
