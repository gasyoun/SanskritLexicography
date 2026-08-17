# Волна 4 — какие смыслы MW и AP отсутствуют у PWG-семейства (H2882)

_Created: 17-08-2026 · Last updated: 17-08-2026_

**Задача:** [H2882](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2882-Fable_SanskritLexicography_mw-ap-sense-coverage-w4_16.08.26.md)
· волна 4 из [issue #1736](https://github.com/gasyoun/SanskritLexicography/issues/1736)
· дорожная карта: [ROADMAP_SanskritLexicography_PWG_RU_EDITION_RELATIONS_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ROADMAP_SanskritLexicography_PWG_RU_EDITION_RELATIONS_2026.md).
Исполнитель: Fable 5 (`claude-fable-5`), 16–17-08-2026.

## Ответ одной строкой

**Наивный механический счёт «смыслов MW/AP, отсутствующих у PWG-семейства» —
232 (MW) + 300 (AP90) кандидатов — завышен примерно в шесть раз: ручная
адъюдикация случайной выборки из 30 кандидатов показала, что лишь ~17 %
(5/30) — правдоподобно настоящие лакуны, а 83 % — это «не привязано», а не
«отсутствует».** Экстраполяция: настоящих смысловых добавок MW и AP вместе — порядка
**40–90 на весь 261-леммный срез**, с широким доверительным интервалом (n=30).
Это сходится с выводом csl-atlas A09-H3 («потомки копируют или сжимают, а не
до-добавляют») и с [FINDINGS §97](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
(MW составлен *из* PW/PWG): даже у формально независимого Апте бо́льшая часть
«нового» — тот же смысл с другим цитатным аппаратом.

## Метод (заявлен до прогона)

Метод — «якорение на санскрите» из csl-atlas
[PAPER_SENSE_ALIGNMENT.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PAPER_SENSE_ALIGNMENT.md)
(A09), переиспользован концептуально: смысл отпечатывается **санскритским
материалом внутри него** (SLP1-токены цитируемых форм + `<ls>`-сигла с локусами,
римские цифры MW переведены в арабские), выравнивание — по пересечению
отпечатков. Перевод и глоссы **не используются** — overlap-метрика глосс
измерена и отвергнута ранее ([FINDINGS §541](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).

- **Вселенная:** 261 истинная лемма стора pwg_ru (11 603 смысловые строки слоёв
  pwg / pw / sch / pwkvn / nws) — единственный срез, где волны 1–3
  ([H2879](https://github.com/gasyoun/SanskritLexicography/pull/1751) /
  [H2880](https://github.com/gasyoun/SanskritLexicography/pull/1756) /
  [H2881](https://github.com/gasyoun/SanskritLexicography/pull/1758)) установили,
  что у семейства **действительно** есть.
- **Единица смысла MW** — одна запись `<L>` из
  [csl-orig/v02/mw/mw.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw.txt)
  (собственная сегментация Кёльна, никакого самодельного сплиттера);
  **единица AP90** — сегмент `{@N@}` из
  [csl-orig/v02/ap90/ap90.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/ap90/ap90.txt).
- **Трёхчастный вердикт** (асимметрия цены ошибки — ровно та, что чинили волны
  1–3: ложное «отсутствует» дорого, ложное «совпало» дёшево):
  - `matched` — ≥ 2 общих якорных пункта с каким-то смыслом семейства;
  - `unalignable` — у смысла MW/AP < 2 собственных якорей → метод не имел
    честного шанса найти пару, **отсутствие не утверждается**;
  - `family_thin` — ни один смысл семейства по этой лемме не несёт ≥ 2 якорей →
    промах ничего не говорит о словаре;
  - `absent_candidate` — якорей достаточно с обеих сторон, пересечение нулевое.

Скрипт: [RussianTranslation/src/mw_ap_sense_coverage.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mw_ap_sense_coverage.py)
(selftest 11/11). Датасет:
[RussianTranslation/pwg_ru/mw_ap_sense_coverage.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/mw_ap_sense_coverage.jsonl)
+ [mw_ap_sense_coverage_summary.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/mw_ap_sense_coverage_summary.json).

## Механические счётчики

| | MW | AP90 |
|---|---|---|
| единиц смысла по 261 лемме | 1 482 | 1 285 |
| `matched` | 127 | 203 |
| `unalignable` (не привязываемо — тонкий отпечаток) | 1 023 | 708 |
| `family_thin` (семейный срез не даёт якорей) | 100 | 74 |
| `absent_candidate` | 232 | 300 |
| лемм вообще нет в словаре | 8 | 119 |

Точность `matched` по выборке 8/8 (сильные якоря: формы спряжения, точные
локусы вроде ṚV 1,174,8 у *bhid*). 119 лемм, отсутствующих у Апте целиком, —
ожидаемый размер словаря (практический словарь против тезауруса) плюс
ведийская лексика среза.

## Адъюдикация absent_candidate — «нет» vs «не привязано»

Случайная выборка 30 кандидатов (15 MW + 15 AP90, seed=4), ручное сличение с
полными смысловыми строками семейства:

| Класс | MW | AP90 | Доля |
|---|---|---|---|
| **Тот же смысл, непересекающийся цитатный аппарат** (aśuci «unrein», bālacandrikā — та же женщина из Daśakumāracarita, но DAŚAK ≠ Daś для сигл; jātīphala; laBh caus.; kalaśī) | 4 | 7 | 37 % |
| **Омоним/окно среза** — у семейства в сторе лежит другой омоним или одна заглушка-отсылка (MW 2. bhuj «geniessen» против среза с 1. bhuj «biegen»; ghoṣa-отсылка; kakṣyā только из SCH-Nachtrag; оба hā у Апте) | 4 | 3 | 23 % |
| **Артефакт ключа леммы** — деградация key1/subcard стора смешала леммы (vaśā́ ↔ vasa; bhara/bhāra/bāṇa под `bara`; uttá ↔ uttha; satkara ↔ satkāra) — см. FINDINGS §560 | 4 | 3 | 23 % |
| **Правдоподобно настоящая лакуна** | 3 | 2 | **17 %** |

Пять выживших кандидатов настоящих добавок: MW *cakrikā* «отряд, толпа»
(Rājataraṅgiṇī), MW *āragvadha* «его плод» (Suśr.), MW 3. *nī* mfn. «ведущий»
как лексикализованное ifc.; AP90 *anvita* «связанный синтаксически» (Sāhityadarpaṇa
— шастрический пласт Апте), AP90 *anaḍuh* «знак Тельца» (астрология — поздний
пласт Апте). Профиль добавок неслучаен: у MW — кашмирская хроника и
лексикализация композитов, у Апте — аланкара-шастра и джьётиша, то есть
**жанровые пласты, которых у Петербургского словаря не было по замыслу**.

## Ограничения (честные)

1. **`absent_candidate` — верхняя граница, не утверждение.** Метод сертифицирует
   присутствие (точность matched высокая), но не отсутствие: у одинаковых смыслов
   бывают непересекающиеся цитаты (37 % выборки).
2. **Сигла-кроссволк неполон** — DAŚAK/Daś., MED/Med. сведены только
   diacritic-strip'ом + один алиас (Mn→M); часть совпадений не засчитана.
   Направление ошибки консервативно задокументировано (завышает «отсутствует»).
3. **Срез, не словарь.** «Отсутствует у семейства» здесь значит «отсутствует в
   11 603 строках стора по 261 лемме» — окна среза местами держат только
   заглушку-отсылку (kalaśa, ghoṣa) или один омоним.
4. **Ключи лемм стора деградированы** (161 строка; группы `vasa` ×5, `bara` ×3
   слиты) — часть сравнений шла к неверной лемме; вычищено декодом subcard, но
   у меньшинства строк и subcard недостоверен по долготе/придыханию
   (FINDINGS §560). Это данные для `[integrity]`-issue, не для тихой починки.

## Воспроизведение

```
python RussianTranslation/src/mw_ap_sense_coverage.py --selftest
python RussianTranslation/src/mw_ap_sense_coverage.py --store <путь к pwg_ru_translated.jsonl>
```

Стор канонический, в git не хранится; скрипт его **только читает**.

_Dr. Mārcis Gasūns_
