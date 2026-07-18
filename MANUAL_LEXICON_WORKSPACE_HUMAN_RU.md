# Руководство по рабочему пространству SanskritLexicography — для человека

_Created: 10-07-2026 · Last updated: 18-07-2026_

Парное руководство для агентов (по-английски):
[MANUAL_LEXICON_WORKSPACE_AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/MANUAL_LEXICON_WORKSPACE_AGENTS.md).
Написано в рамках H479 (Fable 5 `claude-fable-5`), консолидировано в H604.
Это **тонкий индекс**: канонический набор руководств — семь манускриптов в
[docs/manuals/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs/manuals)
(четыре аудиторных + три глубоких по подсистемам)
(маршрутизатор: [docs/manuals/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/README.md));
при расхождении канонический документ прав, этот лист чинится в тот же заход.

## 1. Что это за репозиторий

Это **рабочее пространство данных и исследований**, а не программный продукт.
Здесь живут: экспортированные списки заглавных слов 15+ словарей Кельнской
коллекции, русский перевод Монье-Вильямса (mw_ru, 287 358 карточек, завершен),
действующий конвейер перевода Большого Петербургского словаря (pwg_ru,
PWG→русский), исследовательские заметки и черновики статей. Исходные тексты
словарей лежат не здесь, а в `csl-orig`; сюда попадают производные данные.

Три главные точки входа:

| Вопрос | Документ |
|---|---|
| Что происходит прямо сейчас | [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/.ai_state.md) + [RussianTranslation/.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md) |
| Как мы сюда пришли (pwg_ru) | [PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) |
| Измеренные факты и ловушки | [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) |

## 2. Карта репозитория

- **[HeadwordLists/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists)** —
  аналитическое ядро: уникальные списки key1/key2 по словарям, кросс-словарные
  объединения (союз 323 тыс. заглавных слов), кроссволки MW↔Heritage,
  ACC×NCC, форм-оракул. Статус печатной готовности:
  [PRINT_READINESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/PRINT_READINESS.md).
- **[RussianTranslation/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation)** —
  два независимых конвейера: **mw_ru** (Монье-Вильямс → русский, завершен,
  документация [mw_ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md))
  и **pwg_ru** (PWG → русский, основной действующий проект — см. §3).
- **[papers/](https://github.com/gasyoun/SanskritLexicography/tree/master/papers)** —
  черновики статей (A30, A31, A33–A43, A58 и др.); сводный реестр —
  [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md).
- **Эпистемические реестры** — [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  и семь соседних (ASSUMPTIONS, CONTRADICTIONS, GAPS, DEAD_ENDS, RECIPES,
  STALENESS, GLOSSARY): что доказано, на что мы опираемся без доказательства,
  что заброшено.

## 3. pwg_ru — где смотреть состояние (и срез на 18-07-2026)

Живое состояние — всегда в
[RussianTranslation/.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
(этот лист его не дублирует: снимок 10-07 устарел за неделю). Срез на
18-07-2026, только заголовки:

- **Двигатель GO (H188) — по-прежнему в силе.** В хранилище **11 603** строки
  (репарация H1080 от 17-07: восстановлены 668 строк-заглушек и 468 владельцев,
  две строки в карантине; 11 605 → 11 603).
- **Блокер сместился с калибровки на среду:** цепочка H442/H462 закрыта
  последующими циклами; сейчас c4-headless канал — `HEALTH_NOGO_BY_ENVIRONMENT`
  (зонд 18-07: 98,6 с при потолке 30 с, внешний блокер), а прямой
  Workflow-канал (контроллер-воркер, H1209) в тот же день измерен **GO**
  (15,74 с) — деградация транспорт-специфична.
- Глагольная линия (H151) не затронута; medium50 вслепую не перезапускать
  (правило §3 агентского листа).

## 4. Что изменилось — где читать

Хронология «как мы сюда пришли» целиком живет в
[PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)
— этот лист больше не держит помесячную таблицу (снимок 10-06→10-07
переехал туда же в качестве истории; правка 18-07-2026, H1245). Свежая неделя
одной строкой: 17-07 — репарация хранилища H1080 и manifest-v2-привязка
промоушена (PR #510/#511); 18-07 — H1110 фазы 1–6 закрыты с вердиктом
`HEALTH_NOGO_BY_ENVIRONMENT` по c4, зонд контроллер-воркер канала H1209 — GO,
восстановлен канонический 266k-файл обратного словаря (H736).

## 5. Что ждет именно человека

- **Голосование P2 ACC×NCC** — HTML-лист на 49 019 строк (локальный,
  вне git), потом `apply_p2_decisions.py`. Внимание:
  [PR #264](https://github.com/gasyoun/SanskritLexicography/pull/264) слит еще
  09-07-2026 — воротами остается именно голос, а не PR.
- **Листы H178** — 4 HTML-листа оценочного bake-off (`review/h178_*_sheet.html`).
- **Листы H180** — типология κ, порог learner-словника, spot-check склейки.
- **Печатная готовность** — подать ~16 опечаток MW/PWG, решить по ~8/~7
  кандидатам, акцентная сверка ([PRINT_READINESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/PRINT_READINESS.md)).
- Сводно всё человеческое — в [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).

## 6. Гипотезы к проверке — где список

Формальный список — 30 фальсифицируемых утверждений в
[RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md);
оперативные вопросы эпохи H442 (лимит self-heal, зонд ≥5 КБ, модель таймаута,
разделение пулов) частично закрыты делом: пулы heal/перевода разделены на
master еще 10-07 (PR #311), а вопрос здоровья канала переформулирован
транспорт-специфично итогами H1110/H1209 (см. §3). Детали и цифры — в
[LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)
и roadmap-документе, не здесь (правка 18-07-2026, H1245).

## 7. Четыре аккаунта Claude Max — как гнать массовый PWG→RU

Протокол уже спроектирован (аудит H335 §W1) и укреплен кодом (H336:
claim-файлы промоушена, пер-оконные имена, гигиена append). Пошаговая
операционная версия (worktree на аккаунт, шардинг по корням, единственный
промоутер, глобальный потолок ≤3 линий) — **одна, в глубоком руководстве
конвейера, §13**:
[RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)
— здесь не дублируется (H604: шаги в двух местах расходятся при первой же
правке; переезд из агентского листа — 18-07-2026, H1245). Человеку важно из нее одно: потолок ≤3 одновременных линий перевода —
**глобальный на всю организацию**, а не на аккаунт (обвал Slice-D — серверный,
~18 одновременных workflow).

**Неудобная правда:** 4 аккаунта умножают квоту, а не пропускную способность —
и квота сейчас не является узким местом. Пока H442/H462 не закрыты,
номинальная линия стоит при любом числе аккаунтов. Что 4 аккаунта дают уже
сегодня: (а) параллельные шарды глагольной линии H151; (б) выделенный аккаунт
под аудиты/промоушен/статьи; (в) после починки heal-бюджета — ротацию 24/7
по 5-часовым окнам, ровно как заложено в
[FULL_PWG_RU_30_DAY_SLA_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FULL_PWG_RU_30_DAY_SLA_PLAN.md).

## 8. Сколько сессий на аккаунт — где ответ

> Перенесено в [RUSSIANTRANSLATION_DEEP_MANUAL.md §14](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)
> (18-07-2026, H1245) — здесь остается указатель, чтобы старые ссылки жили.
> Короткая форма: интерактивные сессии упираются в квоту окна (не в ошибки);
> падают workflow-развертки — отсюда глобальный потолок ≤3 линий. Безопасная
> форма на аккаунт: 1 линия генерации + 1–2 легкие сессии.

_Dr. Mārcis Gasūns_
