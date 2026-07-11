# Руководство по рабочему пространству SanskritLexicography — для человека

_Created: 10-07-2026 · Last updated: 11-07-2026_

Парное руководство для агентов (по-английски):
[MANUAL_LEXICON_WORKSPACE_AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/MANUAL_LEXICON_WORKSPACE_AGENTS.md).
Написано в рамках H479 (Fable 5 `claude-fable-5`), консолидировано в H604.
Это **тонкий индекс**: канонический набор руководств по аудиториям — четыре
манускрипта в [docs/manuals/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs/manuals)
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
  черновики статей (A33, A40, A42, A43, A51 и др.); сводный реестр —
  [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md).
- **Эпистемические реестры** — [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  и семь соседних (ASSUMPTIONS, CONTRADICTIONS, GAPS, DEAD_ENDS, RECIPES,
  STALENESS, GLOSSARY): что доказано, на что мы опираемся без доказательства,
  что заброшено.

## 3. pwg_ru — состояние на 10-07-2026

**Двигатель построен и прошел полный аудит (H188: вердикт GO, 0 блокеров).**
В хранилище `src/pwg_ru_translated.jsonl` (не в git) — **11 275 строк**
переведенных под-карточек при цели ~120 173 карточек всего словаря (~9 %).

**Массовый прогон еще не начат.** Что его держит:

1. **Номинальная линия (плотные band-4 карточки) остановлена** — каскад
   kill-gate/self-heal бюджета воспроизведен трижды (H317 → H437 → H442);
   все три запуска H442 инфраструктурно скомпрометированы, поэтому исправление
   ([PR #301](https://github.com/gasyoun/SanskritLexicography/pull/301)) «не
   проверено в поле, а не ошибочно». Владелец следующего шага —
   [H462](https://github.com/gasyoun/Uprava/blob/main/handoffs/H462-Fable_RussianTranslation_launch-telemetry-ledger-code-vs-docs-audit_10.07.26.md).
   **Не перезапускать medium50 вслепую.**
2. **Линия глагольных корней (H151) не затронута** — может капать и сейчас.
3. Человеческие ворота G5/G6/G7 (см. §5) держат публикацию, но не генерацию.

Хронология аварий и уроков — [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md);
статистика запусков — [LAUNCH_STATS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md).

## 4. Что изменилось за месяц (10-06 → 10-07-2026)

Месяц назад pwg_ru был пилотом с ручным запуском. С тех пор (~100 коммитов):

| Когда | Что легло |
|---|---|
| 23–24.06 | Архитектура root-split (гигантские корни → под-карточки, склейка без потерь), частотный порядок DCS, исследование порядка значений (порядок PWG сохраняем, Renou — бейдж), тест 38 единиц: 37/38 публикабельно |
| 26–29.06 | Производственное укрепление: провенанс-штампы, fail-fast на устаревших артефактах, журнал-ledger, локальный дашборд, детерминированные ворота аудита, [AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/AGENTS.md), [USE_CASES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/USE_CASES.md) |
| 04–06.07 | 30-дневный SLA-план полного PWG, аудит H188 → **GO**, починка пропускной способности no-PWG линии (36 %→100 %, H220), защита оркестрации (H234, `synth_dispatch.py`), индустриализация TM: экспорт TMX 1.4b, грейдер A/B/C, слой L0, устный регистр |
| 07–09.07 | Аудит возможностей H335 (конкурентность / провенанс свидетельств / управление падежами / жанр), **укрепление под 3 аккаунта H336** ([PR #254](https://github.com/gasyoun/SanskritLexicography/pull/254)), Stage-2 механический пре-гейт (99,72 % чисто), разблокировка классификатора схемы (H428), дорожная карта 30 исследовательских возможностей |
| 08–10.07 | Сага kill-gate: H317 (0/50) → H437 (2/37, каскад ×3) → H442 (3 запуска, все инфра-скомпрометированы, линия на паузе) → H462. Плюс журнал инцидентов и лог зондов API |

Итог месяца: производственный самопроверяющийся конвейер и ~11 тыс. строк —
и точное знание, что блокер сейчас **калибровка инфраструктуры, а не качество
перевода** (окна не выдают плохой русский — они не выдают ничего).

## 5. Что ждет именно человека

- **Голосование P2 ACC×NCC** — HTML-лист на 49 019 строк, потом
  `apply_p2_decisions.py` ([draft PR #264](https://github.com/gasyoun/SanskritLexicography/pull/264)).
- **Листы H178** — 4 HTML-листа оценочного bake-off (`review/h178_*_sheet.html`).
- **Листы H180** — типология κ, порог learner-словника, spot-check склейки.
- **Печатная готовность** — подать ~16 опечаток MW/PWG, решить по ~8/~7
  кандидатам, акцентная сверка ([PRINT_READINESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/PRINT_READINESS.md)).
- Сводно всё человеческое — в [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).

## 6. Гипотезы к проверке

Формальный список — 30 фальсифицируемых утверждений в
[RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md).
Операционно срочные (из разбора H442):

1. **Пер-карточный лимит self-heal работает** (PR #301) — нужен один чистый
   запуск, три предыдущих скомпрометированы инфраструктурой.
2. **Прогревочный зонд ≥5 КБ предсказывает здоровье окна** — тривиальный зонд
   3,3 с сказал GO, окно всё равно деградировало.
3. **Задержка kill-timeout не зависит от размера payload** (висли и 11-байтовые
   фрагменты на полу 45 с, и 8-КБ скелеты на потолке 180 с) — модель таймаута
   неверна.
4. **Разделение пула heal и пула перевода** снимает связывание `MAX_AGENTS` —
   сейчас heal тратит тот же счетчик, и бюджет окна срабатывает всегда
   (доказано трижды).
5. Исследовательское: прокси-QE не ловит неверный смысл (AUC 0,58) —
   семантический подъем дает консенсус + COMET; доля грейда A (5,3 %) должна
   измеримо вырасти с настоящим выравниванием.

## 7. Четыре аккаунта Claude Max — как гнать массовый PWG→RU

Протокол уже спроектирован (аудит H335 §W1) и укреплен кодом (H336:
claim-файлы промоушена, пер-оконные имена, гигиена append). Пошаговая
операционная версия (worktree на аккаунт, шардинг по корням, единственный
промоутер, глобальный потолок ≤3 линий) — **одна, в агентском руководстве §5**:
[MANUAL_LEXICON_WORKSPACE_AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/MANUAL_LEXICON_WORKSPACE_AGENTS.md)
— здесь не дублируется (H604: шаги в двух местах расходятся при первой же
правке). Человеку важно из нее одно: потолок ≤3 одновременных линий перевода —
**глобальный на всю организацию**, а не на аккаунт (обвал Slice-D — серверный,
~18 одновременных workflow).

**Неудобная правда:** 4 аккаунта умножают квоту, а не пропускную способность —
и квота сейчас не является узким местом. Пока H442/H462 не закрыты,
номинальная линия стоит при любом числе аккаунтов. Что 4 аккаунта дают уже
сегодня: (а) параллельные шарды глагольной линии H151; (б) выделенный аккаунт
под аудиты/промоушен/статьи; (в) после починки heal-бюджета — ротацию 24/7
по 5-часовым окнам, ровно как заложено в
[FULL_PWG_RU_30_DAY_SLA_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FULL_PWG_RU_30_DAY_SLA_PLAN.md).

## 8. Сколько Opus-сессий на один аккаунт Max

Два разных предела, их нельзя путать:

- **Интерактивные сессии Claude Code**: предела одновременности с ошибками
  API нет — сессии делят 5-часовое скользящее окно и недельный лимит
  аккаунта; отказ выглядит как чистое «лимит исчерпан», не как ошибка.
  Комфортно 2–3 одновременных Opus-сессии; больше — просто быстрее сгорает
  окно.
- **Workflow-развертки (вот что реально падает)**: по нашим же измерениям
  `Connection closed mid-response` и kill-таймауты появляются при высокой
  агентной конкурентности; обвал Slice-D — ~18 одновременных корневых
  workflow. Отсюда глобальное правило ≤3 линий. Это серверный сброс нагрузки,
  ему всё равно, с какого аккаунта пришла нагрузка.

Безопасная форма на аккаунт: **1 линия генерации + 1–2 легкие сессии**
(аудит, промоушен, документы).

_Dr. Mārcis Gasūns_
