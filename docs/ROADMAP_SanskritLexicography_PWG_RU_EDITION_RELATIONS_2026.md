# ROADMAP — отношения между редакциями в pwg_ru, 2026

_Created: 16-08-2026 · Last updated: 17-08-2026_

Обложка и решения: [PLAN_SanskritLexicography_PWG_RU_PLACEMENT_AXIS_SPLIT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_PLACEMENT_AXIS_SPLIT.md).

Общая рамка: сейчас в сторе описано отношение **PWG → PW / SCH / PWKVN / NWS**, и даже
оно описано неверно (метка не сверяется с привязкой). Полная картина отношений шире —
правки внутри самого PWG, правки (а не только дополнения) из SCH, и словари, вышедшие
из PWG иначе: MW и AP. Волны 2–4 закрывают это по одной оси за раз.

## Волна 1 — развести метку и привязку (готова к исполнению)

**Что:** ввести `placement` / `placement_reason` / `placement_hypothesis`;
консервативно нормализовать теги смыслов PWG; перегенерировать производные.

**Разблокирует:** любое дальнейшее суждение об отношениях. Пока метка утверждает
отношение к несуществующему смыслу, ни одна волна ниже не может опереться на сайдкар.

**Готово, когда:** ни одна строка с `placement=false` не несёт подтипа, утверждающего
отношение к смыслу; доля проверяемых пар измерена до и после; window suite 211/211.

## Волна 2 — правки внутри самого PWG

**Что:** тип отношения `pwg_internal_correction`. В сторе уже лежат теги смыслов
`Nachtrag` (76), `addendum` (46), `1 (PW)` (45), `PW` (48) — они сидят в скелете как
обычные смыслы, хотя по природе это правки **к** смыслу того же PWG.

**Зависит от:** волны 1 — это тот же дефект осей, и чинить его надо тем же механизмом
(`placement` + причина), а не вторым, параллельным.

**Открытый вопрос для исполнителя:** привязка Nachtrag к правимому смыслу не всегда
явная в тексте; там, где не явная, — `placement=false`, гипотеза по правилу, не догадка.

## Волна 3 — правки и отмены из SCH ✅ ЗАКРЫТА (H2881, 16-08-2026)

**Результат:** из 210 строк SCH правят PWG **7 (3,3 %)** — 6 `sch_correct`,
1 `sch_cancel`; 203 остаются дополнением. Утверждение «SCH только дополняет»
теперь измерено, а не встроено в классификатор.

**Прогноз этой дорожной карты не подтвердился и заменён измерением.** Ниже
ожидалось, что признаком будет тот же конфликт рода, что у `pw_correct`. Ни
одна из 210 строк SCH **не несёт `<lex>`** вообще, так что этот путь на слое
физически не срабатывает. Рабочий признак — печатное **указание читателю**
(`lies`, `Druckfehler`, `zu lesen`; для отмены `streiche`), а не ключевое слово:
11 строк несут похожий на правку токен (`statt` в описательном смысле, `St.` =
Indische Studien, `vgl.`) и правками не являются — они закреплены негативными
тестами. Единственная правка рода в слое (`ahiphena`, «lies n. statt m.»)
выражена прозой и ловится правилом `lies`.

Подробно: [REGLUE_SPEC §12](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md)
· [FINDINGS §552](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
· гейты W3a–W3e в [placement_axis_check.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/placement_axis_check.py).

**Что было запланировано:**

**Что:** подтипы `sch_correct` / `sch_cancel`.

**Почему это дыра:** сейчас SCH **структурно не может** быть ничем, кроме дополнения —
`classify_edition_rel` выдаёт для слоя `sch` только `sch_star` и `derived_sense`, обе
аддитивные. То есть утверждение «SCH только дополняет» не измерено, оно **встроено в
классификатор**. 210 строк SCH в сторе.

**Зависит от:** волны 1. Нужен критерий отличия правки от дополнения — вероятно, тот же
класс признаков, что у `pw_correct` (конфликт рода), плюс печатные пометы SCH.

## Волна 4 — MW и AP: чего нет в PWG и его потомках ✅ ЗАКРЫТА (H2882, 17-08-2026)

**Результат:** механический счёт «отсутствует у семейства» — 232 (MW) + 300
(AP90) кандидатов по 261 лемме среза — **завышен ~в шесть раз**: ручная
адъюдикация 30 случайных кандидатов оставила ~17 % правдоподобно настоящих
лакун; 83 % — «не привязано» (непересекающийся цитатный аппарат 37 %,
омоним/заглушка окна 23 %, деградированный ключ леммы 23 % —
[FINDINGS §560](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).
Настоящих добавок MW+AP на срез — порядка 40–90, и они жанровые (у MW —
Rājataraṅgiṇī, лексикализация ifc.; у Апте — аланкара-шастра, джьётиша).
Подробно: [FINDINGS §559](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
· отчёт [RussianTranslation/pwg_ru/MW_AP_SENSE_COVERAGE_W4.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/MW_AP_SENSE_COVERAGE_W4.md)
· скрипт [mw_ap_sense_coverage.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mw_ap_sense_coverage.py)
· датасет [mw_ap_sense_coverage.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/mw_ap_sense_coverage.jsonl).
Требование «/prior-art перед стартом» выполнено: метод — переиспользование
csl-atlas [A09](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PAPER_SENSE_ALIGNMENT.md)
«якорения на санскрите»; сегментация MW — собственные `<L>`-записи Кёльна,
AP90 — печатные номера `{@N@}`; ничего не строилось заново.

**Что было запланировано:**

**Что:** сопоставление смыслов MW и AP с PWG-семейством; ответ на вопрос «какие значения
есть у них и отсутствуют у PWG и всех словарей, вышедших из него».

**Состояние активов (проверено 16-08-2026):** локально есть репозитории
[MWS](https://github.com/sanskrit-lexicon/MWS) и [AP90](https://github.com/sanskrit-lexicon/AP90),
есть [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) с типологией богатства
словарей и манифест датасетов
[kosha/data/manifest/datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json).
Store `mw_ru` локально отсутствует (в git не хранится).

**Зависит от:** волн 1–3 — и это принципиально. Сравнивать охват смыслов с MW/AP можно
только когда известно, что у PWG-семейства **действительно** есть: пока 90 % отношений
внутри семейства не установлены, «отсутствует у PWG» неотличимо от «не привязано».

**Перед стартом обязателен `/prior-art`:** это межсловарная работа, и csl-atlas/kosha
могли уже часть её сделать.

## Не-цели

- Content-alignment (gloss-to-sense) — отложенный gold pass. Волна 1 намеренно
  **ортогональна** ему: даже идеальная привязка не чинит метку, которая её не читает.
- Метрика пересечения глосс как признак — измерена и отвергнута
  ([FINDINGS §541](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).
- Изменение канонического store. Все волны правят только производные.

_Dr. Mārcis Gasūns_
