# PLAN — двухколоночный DE|RU вид голосовального листа склейки

_Created: 20-08-2026 · Last updated: 20-08-2026_

Ответ на замечание MG к опубликованному
[h180_reglue_v5](https://gasyoun.github.io/vote/sheets/h180_reglue_v5.html):
панель «разметка store» не должна быть видна сразу; рядом нужен чистый немецкий
оригинал PWG с местами вставки; русская склейка и немецкий столбец вместе на всю
ширину экрана; кнопки голоса не занимают эту ширину.

Слои: [ROADMAP](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ROADMAP_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT_2026H2.md)
· [ARCHITECTURE](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT.md)
· [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT.md)
· [VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT.md)
· [metadoc](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT_2026-08.meta.md)

Исполнение волны 1:
[H3199 (Sonnet 5) — Wave 1: DE|RU split vote layout for h180_reglue v6 and G5 pin-ids recut](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3199-Sonnet_SanskritLexicography_reglue-vote-de-ru-split_20.08.26.md).

## Цель одним абзацем

Человек на карточке склейки сразу видит две колонки на всю ширину окна: слева
исходный немецкий PWG с чипами вставки (полный немецкий текст дополнения — тултип),
справа русскую склеенную карточку. Разметка store спрятана за одной ссылкой,
раскрывающей HTML-элемент details на той же карточке. Кнопки голоса текущей
карточки живут в липкой полосе внизу экрана. Тот же хром (ширина, DE|RU, store в
details, липкий голос) переносится на G5 партию 1v3 без смены `sheet_id`. Новых
данных и новой типологии нет: только презентация.

## Что показал аудит (не переспрашивать)

| Факт | Где | Следствие |
|---|---|---|
| `main { max-width:980px }` | [csl-pyutil `review_sheet.py`](https://github.com/sanskrit-lexicon/csl-pyutil/blob/main/csl_pyutil/review_sheet.py) | «окно голосования не на всю ширину» — умолчание шаблона, не баг билдера |
| Панель 2 = `anatomy.highlight(raw)` сразу в теле карточки | [`build_reglue_sheet_v2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_sheet_v2.py) | огромная статья store видна не-агенту без клика |
| `pwg_de` и `supplements[].de` уже в JSON склейки | [`build_reglue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue.py) | левый столбец строится из пилота, не из csl-orig |
| `gā.de.md` — склеенная немецкая статья | тот же билдер, H3152 решение 14 | **не** то, что просили: нужен исходный PWG, не зеркало склейки |
| G5 уже имеет `de_panel` / `store_panel` / `print_panel` | [`g5_card_render.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/g5_card_render.py), H1808 | хром переносится; чипы вставки на G5 не ставить |
| Липкая полоса V17 уже есть | csl-pyutil `_V17_CSS` / `#voteBar` | туда переезжают кнопки **текущей** карточки; не строить вторую полосу |
| G5 `g5-live-queue-batch1v3-2026-07-26` в очереди «доголосовать» | [REVIEW_SHEETS_INDEX](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md) | только `--pin-ids`, тот же `sheet_id` |
| На v5 голосов в индексе нет | та же строка | новый `sheet_id` v6 безопасен |
| Классификатор типологии уже отвечает «в чём отличие» | [`reglue_delta.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reglue_delta.py) | **не** трогать в этой волне |

Prior-art verdict: **PARTIAL**. Ширина, анатомия, немецкий DE-файл, липкий футтер и
G5-панели существуют. Дыра: двухколоночный контракт, скрытие store, исходный PWG с
чипами, перенос кнопок текущей карточки в V17, opt-in флаг, чтобы остальные листы
хаба остались 980px.

## Решения интервью 20-08-2026 (22 штуки)

Исполнитель принимает их как данность и не переоткрывает.

| № | Вопрос | Решение | Почему |
|---|---|---|---|
| 1 | Вид по умолчанию | DE слева, RU справа, на всю ширину; store не в теле | Человек читает оригинал и склейку; агентная разметка — по ссылке |
| 2 | Левый столбец | Исходный PWG + метки вставки, не `gā.de.md` | «изначальный PWG» и «куда вставить» |
| 3 | Store | Ссылка раскрывает details на той же карточке | Цитата в заметку без новой вкладки |
| 4 | Голос | Липкая полоса снизу, не сверху и не третья колонка | Кнопки не крадут ширину DE\|RU |
| 5 | Объём | Этот лист **и** G5 (общий хром) | G5 уже имеет немецкую панель |
| 6 | Идентичность листа склейки | Новый `sheet_id` v6; v5 остаётся на хабе | Сравнить виды; голосов на v5 нет |
| 7 | «Что куда» | Чип у значения + **полный** немецкий текст дополнения в тултипе | Не раздувать левый столбец полной врезкой |
| 8 | Длинный `gā` | Независимый скролл колонок + клик подсвечивает пару | Жёсткий sync ломается, когда справа больше дополнений |
| 9 | G5 вставки | Не ставить чипы; только хром | G5 — годность одного смысла, не склейка |
| 10 | Компактно | Оба столбца переключаются вместе | Печатная колонка vs etext на DE и RU |
| 11 | Узкий экран | Стек: сначала DE, потом RU; липкий голос остаётся | Порог 900px |
| 12 | Что липнет | Кнопки **текущей** карточки в `#voteBar`; в карточке кнопок нет | Иначе две зоны и рассинхрон заметки |
| 13 | Куда код | Флаг в csl-pyutil; оба билдера его включают | Один контракт; остальные листы не расширяются |
| 14 | G5 identity | Пересрезка `--pin-ids`, тот же `sheet_id` | localStorage голосов живёт |
| 15 | Тултип на телефоне | Hover на десктопе; тап закрепляет; второй тап / клик вне закрывает | Native `title` обрежет длинный NWS |
| 16 | Компакт слева | Тот же `line_collapse`, чипы остаются | Не голый PWG и не склейка |
| 17 | Доказательство без взгляда MG | Селфтест HTML + один браузерный проход по `gā` и одной карточке G5 | Публикация не ждёт человека |
| 18 | csl-pyutil не влит | PR + ставить пакет с той ветки в SanskritLexicography | Хаб не ждёт Cologne |
| 19 | Новая развилка | Наименее разрушительное умолчание + строка в отчёт | Человека нет 5–8 ч |
| 20 | Стоп | Красный селфтест после двух чинок · дрейф G5 pin-ids · слева протёк русский · anatomy видна без открытого details · байты store изменились | Остальное — записать и ехать |
| 21 | Забор | Store jsonl · csl-orig · `reglue_delta` / ADDENDA_TYPOLOGY · состав/текст карточек G5 · другие листы хаба · правка немецкого | Только презентация |
| 22 | Публикация | Merge gasyoun (SL + Uprava); PR csl-pyutil; v6 и перерезанный G5 на хаб в том же проходе | Голосовать v6 — `@DO` после волны, не стоп |

## Контракт автономности

**При неясности.** Берёт наименее разрушительное умолчание, продолжает, в тот же
проход пишет строку в «Решения, принятые без человека» отчёта волны: что было
неясно, что выбрано, что стало бы иначе. Не останавливается, не спрашивает.

**Стоп — пять условий.** Останавливается и докладывает, а не ищет обход:

1. Селфтест красный после **двух** честных попыток починки. Ослаблять тест запрещено.
2. `--pin-ids` на G5 показывает дрейф состава или текста карточек.
3. В левой колонке склейки появляется русский текст тела (не ярлыки чипов).
4. `anatomy.highlight` виден в DOM карточки вне закрытого details (открытый details
   по клику — норма).
5. SHA-256 тел store / сырой панели склейки изменился относительно гейта
   `digest_guard` в [`build_reglue_sheet_v2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_sheet_v2.py).

**Коммиты.** Handoff-scoped: commit → PR → merge в
[gasyoun/SanskritLexicography](https://github.com/gasyoun/SanskritLexicography)
и прямая запись хабов в [gasyoun/Uprava](https://github.com/gasyoun/Uprava).
В [sanskrit-lexicon/csl-pyutil](https://github.com/sanskrit-lexicon/csl-pyutil) —
PR, без автослияния; сборка листов идёт с ветки PR (решение 18).

**Забор.** Пункт 21 таблицы. Плюс: не снимать 980px у листов без флага; не
переименовывать v5 URL; не пересобирать `h180_reglue_v3` / v2.

## Шлюз автономности

Каждая поставка волны 1 имеет архитектуру, упорядоченные шаги, критерий приёмки и
именованный риск. Блокирующих развилок нет. Prior-art записан. Контракт покрывает
невлитый csl-pyutil, дрейф G5 и утечку store. **PASS.**

_Dr. Mārcis Gasūns_
