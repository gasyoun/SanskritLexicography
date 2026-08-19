# IMPLEMENTATION — reglue2, волны 1–3 по шагам

_Created: 19-08-2026 · Last updated: 19-08-2026_

Слой «реализация» плана
[PLAN_RussianTranslation_REGLUE2_CITATIONS_TYPOLOGY_2026-08](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_RussianTranslation_REGLUE2_CITATIONS_TYPOLOGY_2026-08.md).
Шаги идут в порядке зависимостей; каждый называет файлы, которые трогает, и то, чем
доказывается его завершение. Границы компонентов — в
[ARCHITECTURE](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_RussianTranslation_REGLUE2_CITATION_LAYER.md).

## Шаг 0 — рабочее дерево и замер «до»

Репозиторий охраняемый: правки только в собственном рабочем дереве сессии.

```
git -C SanskritLexicography fetch origin
git -C SanskritLexicography worktree add -b <ветка> ../SanskritLexicography-<slug>-<pid> origin/master
```

Затем **замер до правки**, он же база для условия стопа 2: сколько цитат в хранилище
резолвится сегодня, отдельно по `MBH.`, `ṚV.`, `AV.`, отдельно по слоям PWG и NWS.
Инструмент существует —
[`ls_coverage_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_coverage_probe.py);
цифру записать в отчёт до первой правки. Без этого числа условие «охват упал» непроверяемо.

Переменная окружения `PWG_RU_DATA_ROOT` должна указывать на локальное хранилище: оно
gitignored и в клоне отсутствует.

## Шаг 1 — `src/mbh_locus.py` (поставка A1)

Новый модуль. Собирает координаты Махабхараты в один контракт `MbhLocus` (схема — в
архитектуре §2).

Трогает: **новый** `RussianTranslation/src/mbh_locus.py`.
Читает: `MbhEtext` из [`ls_links.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_links.py),
`generate_href` из [`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py),
csl-atlas [`mbh_vulgate_critical_presence.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_vulgate_critical_presence.csv)
(колонка `bori_locus` — то, что до сих пор никуда не выводилось).

Обязательные ветки селфтеста:

- `MBH. 12,8081` → вульгата `12.226.6`, `bori_locus` непустой, `presence == present`;
- запись со статусом «только в вульгате» → `bori is None`, `presence == vulgate_only`;
- csl-atlas отсутствует → `presence == unchecked`, и это **не** `absent`.

`sys.stdout.reconfigure(encoding='utf-8')` в начале — правило Windows.

## Шаг 2 — страницы стихов IAST (поставка A2)

Трогает: **новый** `RussianTranslation/src/build_mbh_verse_pages.py`, выход в каталог
публикации сайта статей.

Читает (только чтение, забор п. 4): `CommentaryStrategies/data/edition_comparison_mbh/<parva>/concordance.json`
для всех 18 парв — там выравненные по каноникализованному IAST чтения Вульгаты и BORI.

Одна страница на стих, имя файла — вульгатная координата. На странице: оба чтения в
IAST рядом, подпись, какое из какого издания, и обратная ссылка на кельнский скан.
Страницы без чтения BORI печатают «в критическом издании отсутствует», а не пустоту.

Проверка шага: страница `12.226.6` содержит `yadā ca pṛthivīṃ sarvāṃ yajamāno 'nuparyagāḥ`.

## Шаг 3 — рендер тройки координат (поставка A3, закрывает п. 1)

Трогает: `_ls_html` в
[`build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py) —
одна правка, три поверхности.

Немой значок `E` / `E†`, введённый в H2845, **заменяется** на видимые координаты:

```
MBH. 12,8081. = Вульг. 12.226.6 = крит. 12,220.6
```

Каждая часть — своя ссылка: калькуттская на кельнский скан, вульгатная на страницу
шага 2, критическая на BORI-чтение той же страницы. При `vulgate_only` — `крит. —` с
подсказкой. При `unchecked` третьей координаты нет вовсе.

Осторожно с одной деталью, уже стоившей времени в H2845: адрес e-текста несёт `?id=…`,
а `=` внутри намеренно некавыченного значения атрибута этого рендерера — ошибка разбора
HTML5. Атрибут кавычится через отдельный сентинел; не сломать это заново.

## Шаг 4 — разбиение многоместного `<ls>` (поставка A4, закрывает п. 6а)

Трогает: `_ls_html` (тот же файл) и — если разбор нужен и вне рендера —
[`ls_links.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_links.py).

Алгоритм и правило «всё или ничего» — архитектура §4. Контрольный случай ровно из
замечания MG: `<ls>ṚV. 4,3,13. 10,18,4</ls>` даёт **две** ссылки, вторая ведёт на
`ṚV. 10,18,4`, а не на первую.

Тот же разбор пишет строки для очереди правок (шаг 9).

## Шаг 5 — обёртка Ригведы и Атхарваведы в слое NWS (поставка A5, закрывает п. 5)

Трогает: **новый** `RussianTranslation/src/nws_citation_wrap.py`; вызывается из рендера.

Узкий белый список форм (`ṚV`, `RV`, `AV`, `AV(P)` и их варианты записи), а не общий
поиск «похоже на цитату»: ложная обёртка портит текст, пропущенная лишь не даёт ссылку.
Контрольные случаи из `gA.md`: `AV(P) 9.10,10` и `ṚV 10,108,9` в теле NWS.

Каждая обёртка даёт строку change-файла для очереди (шаг 9). **Ни одного коммита в
`csl-orig`** — условие стопа 3.

## Шаг 6 — указатель русских изданий Махабхараты (поставка A6)

Трогает: **новый** `RussianTranslation/data/mbh_russian_editions.tsv` + строка в
[Uprava/PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md).

Колонки: парва, номер, том русского издания, переводчик, год, издательство, есть ли
скан, примечание. Все 18 строк заполнены; там, где перевода нет, стоит «нет издания», а
не пустая ячейка. Подключается к `mbh_locus.bori` — русский перевод ищется по
критическому адресу.

Здесь вероятнее всего сработает контракт неясности: библиографические детали части
парв спорны. Брать умолчание, отмечать строкой в журнале решений, не останавливаться.

## Шаг 7 — волна 2, презентационный слой

Строго после того, как волна 1 зелёная.

**7a. Пересборка из зачищенного хранилища (B1, п. 2).** H2849 уже свёл немецкие падежи
к латинским, но мутация хранилища не коммитилась — она локальная. Прогнать
`build_reglue.py` заново и добавить гейт в
[`scan_sheet_latin_chrome.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/scan_sheet_latin_chrome.py):
свободно стоящие `Akk`, `Instr`, `Lok` в русском теле — падение. Осторожно с известным
ложным срабатыванием: доменная помета `[Gen, unsp]` — не падежная, она исключена в
H2849, не сломать исключение. Русская подсказка при наведении (решение 12) идёт через
уже существующий механизм тултипов `pwg_ab.resolve`; не забыть, что таблица PWG
ключуется `Instr.`, а не `Ins.` — за это отвечает `RENAME_ALIASES`.

**7b. Дифф-классификатор (B2).** Новый `RussianTranslation/src/reglue_delta.py`:
четыре дельты (источник, форма, управление, оттенок), сравнение **немецкого** с
немецким, старшинство знаков `＋ → ʰ § ≈`. Гейт различительной способности: ни один знак
не берёт больше 70 % пилота, иначе — условие стопа 4, доложить отрицательный результат.

**7c. Пять знаков и легенда (B3, п. 4).** Трогает `build_reglue.py` и генераторы листов.
Четырёхкратный чип `≈ переформулировкаrestatePW · переформулирует` заменяется на знак в
строке плюс легенду один раз вверху карточки; латинский код и полный список дельт — в
подсказке.

**7d. Ярлык привязки (B4, п. 5a).** Везде, где печаталось `значение PWG N`, теперь
`привязано к смыслу PWG N`; при `target_sense='*new'` — `новый смысл, в PWG
соответствия нет`. Это 90.2 % добавок, формулировка обязана быть честной.

**7e. Немецкая склейка (B5, п. 3).** `build_reglue.py` получает язык, выдаёт
`reglue/<key1>.de.md`. Гейт паритета: множества точек вставки русской и немецкой
склеек совпадают.

**7f. Флаг спорной глоссы (B6, п. 6б).** Только пометка. Признак: содержательные слова
русской глоссы, не поддержанные ни немецким телом, ни процитированным местом. «следовать
за» при `ṚV. 4,3,13` обязано попасть в отчёт. **Текст не править** — забор п. 3.

## Шаг 8 — прогон и приёмка

Все селфтесты затронутых модулей, пересборка `gā`, выборочная сверка 50 цитат. Подробно —
[VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_RussianTranslation_REGLUE2.md).
Повторный замер охвата и сравнение с базой шага 0.

## Шаг 9 — публикация и уход правок наверх (волна 3)

1. Change-файлы шагов 4 и 5 — в очередь
   [/cologne-correction-queue](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-correction-queue.md).
   Не открывать PR в `csl-orig`.
2. Опубликовать страницы стихов и пересобранный
   [сайт статей](https://gasyoun.github.io/SanskritLexicography/).
3. Пересобрать и опубликовать
   [h180_reglue_v3](https://gasyoun.github.io/vote/sheets/h180_reglue_v3.html); строка в
   [Uprava/REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md).
4. Issue в кельнском репозитории: необёрнутые цитаты Ригведы и Атхарваведы, затем
   `link-splitting`. Тип, степень и веха по
   [/cologne-issue-runbook](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-issue-runbook.md);
   номера вех узнавать через API, **не хардкодить**.
5. Записи в хабы: новый или изменённый помощник → [SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md);
   указатель изданий → [Uprava/PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md);
   непредвиденная ловушка → [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).
6. Строка в [CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md),
   затем [/cut-release](https://github.com/gasyoun/claude-config/blob/main/commands/cut-release.md).
7. Убрать рабочее дерево тем же проходом; при блокировке файла на Windows повторить
   один раз, затем `git worktree prune`.

## Правила среды, нарушение которых стоило времени раньше

- `sys.stdout/stderr.reconfigure(encoding='utf-8')` в каждом печатающем скрипте;
  `encoding='utf-8'` в `subprocess.run`, читающем вывод. BOM запрещён.
- Многошаговый скрипт — файлом `.py`, не через `python -c`.
- Инструменты Uprava разрешают пути от расположения скрипта, а не от текущего каталога:
  запускать копию `tools/` своего рабочего дерева.
- Ни `git pull`, ни `--autostash` в клонах с несколькими сессиями; только `git fetch`
  плюс свежее рабочее дерево.

_Dr. Mārcis Gasūns_
