# PLAN — pwg_ru: развести ось «метка» и ось «привязка»

_Created: 16-08-2026 · Last updated: 16-08-2026_

Обложка плана: цель, все принятые решения, контракт автономного исполнения и ссылки
на четыре слоя. Исполняющий агент читает **этот** файл первым.

**Источник:** [issue #1736](https://github.com/gasyoun/SanskritLexicography/issues/1736)
· [FINDINGS §541](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
· [REGLUE_SPEC §9](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md)

## Цель

Поле `subtype` в сайдкаре склейки смешивает два разных утверждения — свойство слоя
(«PW сокращает PWG», верно всегда) и утверждение о паре («эта добавка пересказывает
**вот этот** смысл PWG», требует найденной цели). Из-за этого **4 132 из 5 054** строк
`restate` утверждают отношение к смыслу, которого нет: в той же строке стоит
`target_sense='*new'`.

Волна 1 разводит эти оси и чистит формат тегов смыслов. Это **исправление
корректности**, а не расширение охвата: доля реально привязанных добавок вырастет
только за счёт снятия форматного шума, никакой новой семантики не вводится.

## Принятые решения (интервью 16-08-2026)

| # | Развилка | Решение | Обоснование |
|---|---|---|---|
| 1 | Как чинить оси | **Вариант C** — развести две оси | `direction` уже несёт свойство слоя; утверждение о паре требует цели |
| 2 | Форма поля | **Отдельное булево** `placement`, не суффикс подтипа | Суффикс дублирует информацию в двух полях — они разойдутся |
| 3 | Режим B (висячая цель) | **Разделить**: сначала нормализовать теги, остаток → `placement=false` с причиной | 941 висячая цель — это ДВА явления: 560 внутри диапазона PWG (форматный шум) и 381 выше максимума PWG (у поздней редакции реально больше смыслов) |
| 4 | Падать ли на режиме B | **Нет.** `out_of_range` — не ошибка сборки | «У PW больше смыслов, чем у PWG» — реальное явление и прямое свидетельство для статьи о перенумерации |
| 5 | Догадка о привязке | **Отдельное поле-гипотеза**, никогда не `placement=true` | Догадка не поднимается до факта молча; голосуется отдельно |
| 6 | Агрессивность нормализации | **Консервативно**: только пунктуация и пробелы | Ложное `placement=true` тихо врёт; честное `placement=false` просто не знает |
| 7 | Набор полей | `placement` + `placement_reason` + `placement_hypothesis` | `reason` различает режимы A и B — ради чего всё и затевалось |
| 8 | Перегенерация | **Всё, включая листы голосования** | Ruling MG вопреки рекомендации — см. «Принятый риск» ниже |
| 9 | Объём волны 1 | Только метка + нормализация | Остальное — отдельные волны со своими handoff |
| 10 | Правки внутри PWG | **Волна 2**, свой тип отношения | Тот же дефект осей на другом слое; чинить после того, как механизм устоялся |
| 11 | При неоднозначности | Консервативный дефолт + журнал | См. контракт ниже |

**Принятый риск по решению 8.** Регенерация опубликованных листов меняет их
`content_hash`, и ранее выгруженные `decisions.json` перестают проходить строгую
валидацию. Риск сейчас низкий: по `h180-reglue-evidence-2026-08-15` голосов ещё не
подано, лист опубликован 16-08-2026. Агент обязан **проверить это перед регенерацией**
(см. шаг S7 в имплементации) и, если голоса уже есть, остановиться и сообщить — это
единственное место, где решение 8 уступает правилу H1404.

## Контракт автономного исполнения

- **При неоднозначности классификации** — всегда выбирать `placement=false`
  (не утверждать отношение), записать случай в отчёт прогона и продолжать.
  Никогда не «догадываться в сторону» `placement=true`.
- **Останавливаться** только если: (а) падает `window_selftest.py`;
  (б) меняется число строк store (`rows=11715`) — значит тронуты канонические данные;
  (в) `placement=true` появляется там, где раньше было `target_sense='*new'` —
  это признак слишком агрессивной нормализации, то есть ровно того дефекта, который чиним;
  (г) по опубликованному листу уже поданы голоса (см. риск выше).
- **Полномочия:** commit → PR → merge в рамках handoff волны 1, без вопросов.
- **Забор (не трогать):** `pwg_ru_translated.jsonl` (канонический store — только чтение),
  `csl-orig` и любые апстримы Кёльна, `mw_ru*`, каталог `src/pilot/output/`,
  локи уже проголосованных листов.

## Слои плана

| Слой | Документ |
|---|---|
| Дорожная карта, волны 1–4 | [ROADMAP_SanskritLexicography_PWG_RU_EDITION_RELATIONS_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ROADMAP_SanskritLexicography_PWG_RU_EDITION_RELATIONS_2026.md) |
| Схема, границы, контракты | [ARCHITECTURE_SanskritLexicography_PWG_RU_PLACEMENT_AXIS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_PWG_RU_PLACEMENT_AXIS.md) |
| Пошаговая сборка волны 1 | [IMPLEMENTATION_SanskritLexicography_PWG_RU_PLACEMENT_AXIS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_SanskritLexicography_PWG_RU_PLACEMENT_AXIS.md) |
| Критерии приёмки, риски | [VERIFICATION_SanskritLexicography_PWG_RU_PLACEMENT_AXIS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_SanskritLexicography_PWG_RU_PLACEMENT_AXIS.md) |

## Что уже проверено (prior art)

- `edition_rel.py` / `build_relationships.py` — существуют, правим их, не пишем заново.
- Нормализация тегов смыслов — **нигде в репо не реализована**; ближайшее, `safe_filename.py`,
  решает другую задачу (имена файлов). Пишем новую функцию в `edition_rel.py`.
- Измерение проверяемости пар уже есть:
  [`build_reglue_evidence_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_evidence_sheet.py)
  печатает `checkable / no_target / too_thin` — переиспользуем как замер до/после.
- Overlap-метрика уже измерена и **отвергнута** как признак ([FINDINGS §541](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md));
  в волне 1 её не трогаем и на карточки не выводим.

_Dr. Mārcis Gasūns_
