# Руководство для студента — SanskritLexicography

_Created: 10-07-2026 · Last updated: 24-07-2026_

Для **студента санскрита** (в первую очередь русскоязычного, из круга
samskrte.ru / Общества ревнителей санскрита), который прошел базовую морфологию и
хочет понять, что в этом репозитории полезно лично ему. Технические подробности —
в [руководстве для сопровождающего](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md);
научная рамка — в [руководстве для исследователя](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RESEARCHER_MANUAL.md).

---

## 0. Честно: это мастерская, а не учебник

Здесь нет курса санскрита и нет готового онлайн-словаря. Это **рабочее
пространство** — черновики, наборы данных, исследовательские заметки. Часть
материалов уже готова к использованию прямо сейчас (открыть в браузере, читать),
часть — технические инструменты (нужна командная строка и Python), а часть — пока
**планы** (учебный веб-слой, публикация русских переводов). Ниже честно помечено,
что к какой категории относится.

За полноценным онлайн-словарем идите на
[сайт CDSL](https://www.sanskrit-lexicon.uni-koeln.de/), а за курсами — на
samskrte.ru.

## 1. Готово сейчас — открыть в браузере, ничего не устанавливая

### Санскритские частицы (главное для студента)

[Syntax-Lectures/](https://github.com/gasyoun/SanskritLexicography/tree/master/Syntax-Lectures)
— учебные материалы (на русском) по санскритским частицам и их синтаксису.
Аудитория прямо ваша: первокурсник-индолог после базовой морфологии.

- **Точка входа — конспект:**
  [sanskrit_particles_lectures.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Syntax-Lectures/sanskrit_particles_lectures.md).
  Две лекции по 60 минут: «Общая картина и позиционная классификация» и
  «Семантика и прагматика». Линия Whitney — Speyer — Gonda — Apte; позиционная
  классификация по А. А. Зализняку.
- **Интерактивный разбор** (скачайте и откройте в браузере):
  [sanskrit_particles_explorer.html](https://github.com/gasyoun/SanskritLexicography/blob/master/Syntax-Lectures/sanskrit_particles_explorer.html)
  — кликабельная позиционная карта над 16 частицами; по каждой — функция,
  примеры с глубокими ссылками на параллельный корпус (Гӣта/Ману), Whitney,
  Speyer, DCS, цитаты Gonda/König/Hock, библиография и вложенные статьи Apte
  (1957). Схема отдельно:
  [sanskrit_particles_schema.html](https://github.com/gasyoun/SanskritLexicography/blob/master/Syntax-Lectures/sanskrit_particles_schema.html).
- **Статьи Apte (1957) в русском переводе** — для семи частиц с отдельной
  статьей: api, eva, hi, iti, khalu, tu, vai (файлы
  `Apte_1957-*_RU.md` в той же папке). Остальные девять из шестнадцати покрыты
  только конспектом и схемой.

### Субхашиты — короткие стихи для чтения

[IndischeSprueche/](https://github.com/gasyoun/SanskritLexicography/tree/master/IndischeSprueche)
— 7 537 гномических двустиший Бетлингка: каждое дано в деванагари, IAST и с
немецким переводом. Отличный материал, чтобы читать целые (короткие,
самодостаточные) шлоки: грамматически простые, с готовым переводом. Русского
перевода в этом файле **нет** (только немецкий). Файл:
[data/indische_sprueche.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/data/indische_sprueche.jsonl)
(по одной записи на строку). Для точных ссылок «Spr. N» пользуйтесь живым сайтом
[boesp2](https://github.com/sanskrit-lexicon-scans/boesp2), а не этим файлом.

### Обратный словарь — по окончаниям слов

[ReverseDictionary/](https://github.com/gasyoun/SanskritLexicography/tree/master/ReverseDictionary)
— словарь, отсортированный по **последней** букве слова (для рифм, окончаний
стиха, суффиксов). Что реально доступно студенту прямо в браузере (обновлено
18-07-2026): в клоне **отслеживается** набор из ~38 `.mdx`-конвертаций ядра
материалов — предисловие составителя («Обратный словарь санскрита.mdx»),
«Bucknells Index to Endings.mdx» (парадигмы окончаний) и статистические
приложения в `Statistica/` — плюс `SCHEMA.md` и `DATA_STATEMENT.md`; обзор — в
[README](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/README.md).
⚠️ Сам большой список (266 820 слов) и сырые `.txt`-файлы старой выгрузки
(`249-types-of-pratyayas-MW.txt`, `nounend.txt`, `verbend-dev.txt`) в клон
**не входят**: список — намеренно локальный и закрыт по правам
(`RIGHTS_LEDGER.md`), а сырые файлы после инцидента 07-07-2026 живут только в
локальной резервной папке вне репозитория — из клона их не открыть.

Это «суффикс-ориентированный» взгляд на грамматику, которого не дает обычный
словарь по первой букве. Сам большой словарь пока **не издан** — это черновики к
будущей книге.

## 2. Для технического студента — нужен Python

Если вы дружите с командной строкой, в
[RussianTranslation/](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/README.md)
есть учебный грамматический аппарат (данные готовы; это не перевод, а грамматика):

```powershell
python src\nominal_grammar.py --table agni m.    # таблица склонения одного слова
python src\reverse_index.py --show "m·8n*"       # все слова с той же парадигмой
```

- **Learner-core** — подмножество из 22 772 заглавных слов (та ~21 % часть PWG,
  которую реально удерживают студенческие словари).
- **Зализняк-индекс** — компактная помета парадигмы `G·T S F` (например `m·8n*`),
  знакомая по русской лексикографии:
  [ZALIZNYAK_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md).
- **Обратный словарь по парадигме** — «покажи все слова, которые склоняются как
  это» (`reverse_index.py --show`).

## 3. Русские переводы великих словарей — статус

Две отдельные работы (подробности —
[RussianTranslation/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/README.md)):

- **mw_ru** — русский перевод всего словаря Monier-Williams (287 358 карточек,
  **готов**).
- **pwg_ru** — Петербургский словарь (Бетлингк–Рот) → русский, **в производстве**
  (headless CLI, store локальный; редакторский обзор —
  [pwg_ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md)).

⚠️ **Полный текст переводов пока не опубликован** и в голом клоне репозитория
его нет: bulk-store намеренно исключён из git (репозиторий публичный, а
неопубликованный русский текст — нет). Часть article-site (карточки по
переведённым корням) публикуется на
[gasyoun.github.io/SanskritLexicography](https://gasyoun.github.io/SanskritLexicography/);
полный учебный веб-слой на весь PWG — ещё не готов.

## 4. Куда идти дальше

- Полноценный онлайн-словарь: [сайт CDSL](https://www.sanskrit-lexicon.uni-koeln.de/).
- Курсы санскрита: samskrte.ru.
- Точные издания субхашит: [boesp1](https://github.com/sanskrit-lexicon-scans/boesp1) /
  [boesp2](https://github.com/sanskrit-lexicon-scans/boesp2).
- Общая карта репозитория: корневой
  [README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/README.md).

_Dr. Mārcis Gasūns_
