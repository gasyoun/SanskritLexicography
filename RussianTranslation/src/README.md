# `src/` — словари для корпусной сверки (этап 4 `pwg_ru`)

Здесь лежат **нормализованные, ключенные по SLP1 санскритско-русские словари**,
по которым этап 4 ([../pwg_ru_prompts/4_korpus_proverka.txt](../pwg_ru_prompts/4_korpus_proverka.txt))
сверяет русский перевод PWG. Шлюз — неблокирующий аннотатор с двумя сигналами;
см. [../pwg_ru.md](../pwg_ru.md), раздел 7. План интеграции корпуса —
[../SAMUDRA_INTEGRATION.md](../SAMUDRA_INTEGRATION.md).

## Что здесь

Данные **извлекаются из SamudraManthanam** (`samskrtam.ru`, параллельный
санскритско-русский корпус) скриптом [build_src.py](build_src.py) — там эти
словари уже оцифрованы и ключены по SLP1.

| Файл | Словарь | Роль в шлюзе | Записей |
|------|---------|-------------|---------|
| `koch.jsonl` | Кочергина, Санскритско-русский словарь (1987) | независимый — **корректность** (главный якорь) | 29 177 |
| `kow.jsonl` | Коссович, Санскрито-русский словарь (1854); частичный человеческий PWG→рус., посеян из WIL | **эталон** (сигнал 2) + вторичное подтверждение | 13 488 |
| `kna.jsonl` | Кнауэр, Учебник санскритского языка (1908), словарь | независимый — **корректность** | 3 271 |
| `fri.jsonl` | Фриш, Санскритская хрестоматия II, словарь (1956) | независимый — **корректность** | 8 151 |
| `smirnov.jsonl` | Смирнов, Симфонический словарь (1955–1989) | независимый — **корректность** | 3 547 |

Итого ≈ 57 634 ключенные статьи. SKD/VCP сюда **не** кладутся
(санскритско-санскритские, ноль кириллицы).

## Формат

Одна статья на строку: `{"source","slp1","iast","gloss"}`. Ключ соединения с
заглавным словом PWG — `slp1` (нормализуемый длиносохраняющей `form_key()`).
Для koch/kow/kna ключ берется из исходного поля `slp1`; для fri/smirnov —
транслитерируется из IAST (см. [build_src.py](build_src.py)).

**Гигиена ключей.** Несколько исходных записей SamudraManthanam несут ключ, не
являющийся санскритским словом: затекший в поле `slp1` номер/скобка со скана
Кочергиной (`(nu`, `11`, `5)`), кириллично-латинская мешанина в строках Фриша
(`ргаdA`, `араnI`, …), многоформенное поле Фриша с неотображенной заглавной `Ī`
(`Īdfkza/…`) и русская отсылка «см.» у Смирнова (`РЕЧЬ … см. ↑`). Все они
ловятся по не-ASCII-букве в начале нормализованного ключа (санскритское слово
так не начинается). [build_src.py](build_src.py) пытается восстановить ключ из
первой **чисто деванагарской** формы записи, иначе строку отбрасывает: 4
восстановлено (3 koch + 1 fri), 6 отброшено (5 fri + 1 smirnov).

## Специализированные глоссарии имен — `build_glossaries.py`

Помимо пяти общих словарей выше, [build_glossaries.py](build_glossaries.py) читает
**сырые** файлы `Data/*.txt` SamudraManthanam (индексы имен при печатных изданиях
Рамаяны — они НЕ проходили через `corpus_builder/jsonl`, в отличие от источников
`build_src.py`). Это текстово-специфичные словари ИМЕН, не общая лексика — держатся
отдельно от `INDEP` (`SPECIALIST` в `corpus_gate.py`), никогда не попадают в
`heuristic()`/coverage/tune, только в поле карточки `specialist_glosses`
(корроборация, evidence-only, права не подтверждены).

| Файл | Источник | Записей |
|------|---------|---------|
| `grin12.jsonl` | Гринцер, словарь к «Рамаяне» I-II (2006) | 457 |
| `grin3.jsonl` | Гринцер, словарь к «Рамаяне» III (2006) | 206 |

**Ключ.** Оба файла дают IAST прямо в скобках после заглавного слова
(`Агастья\t(Agastya) — …`), детерминированно переводимый в SLP1 через
`iast_to_slp1` (реюз из `build_src.py`, с предварительным `.lower()` — имена
пишутся с большой буквы, а регистр в SLP1-ключах PWG значим только для
долготы/ретрофлексии, не для имени собственного).

**Остальные 4 из исходного списка MG (05-07-2026) НЕ вынесены сюда — сознательно:**
- `Словарь Потаповой.txt`, `Эрман-Темкин.txt`, `Словарь Гринцера из Бада
  Кадамбари.txt` — заглавные слова **только кириллицей**, IAST нет вообще (0
  строк с латиницей у первых двух; у Бада-Кадамбари латиница есть в 68/464
  строк, но это латинские биномены растений/животных в глоссе, а не IAST
  заглавного слова). Детерминированной кирилло-санскритской транслитерации без
  потери информации (дентальные/ретрофлексные согласны сливаются в практической
  русской транскрипции) не существует и в репозитории ее нет — строить
  эвристическую сейчас означало бы рисковать тихо неверными ключами в сигнале,
  который используется как **источник корректности** для остального пайплайна.
  Флаг для будущей сессии, если появится время построить и провалидировать
  такой транслитератор.
- `Топоров.txt` — это НЕ словарь глосс, а именной указатель к печатным статьям
  (`Агнихотра\t22` = имя + номер страницы). Не источник Sa→Ru соответствий вообще.

## Хинди-сигнал значения (indic-dict) — `build_indic.py`

Помимо пяти санскритско-русских словарей, шлюз использует МЯГКИЙ
**третьеязычный сигнал ЗНАЧЕНИЯ** на хинди — для снятия многозначности (какое
значение головное), НЕ для корректности русского перевода. Источник —
словари [indic-dict/stardict-sanskrit](https://github.com/indic-dict/stardict-sanskrit),
свободное использование с атрибуцией (мейнтейнер, e-mail 2026-06-24; см.
[../INDIC_DICT_EVALUATION.md](../INDIC_DICT_EVALUATION.md)).

[build_indic.py](build_indic.py) парсит StarDict-экспорты `.babylon` (заглавное
слово — деванагари, глосса — хинди) в SLP1-ключенный JSONL:

| Файл | Словарь | Записей | Покрытие PWG |
|------|---------|---------|--------------|
| `apte_hi.jsonl` | Apte → हिन्दी | 111 235 | 31.7 % |
| `vedic_rituals_hi.jsonl` | ведийская обрядовая лексика → हिन्दी | 6 166 | 2.3 % |

Строка: `{source, slp1, stem, dev, pos, gloss, attribution}`. apte-hi дает леммы
в **именительном падеже** (अग्निः→`agniH`, फलम्→`…am`), а PWG ключит по основе —
поэтому добавлено поле `stem` (снятие nom-sg висарги / среднего `-am`), и индекс
шлюза несет оба ключа. Эти словари в `heuristic()` НЕ подаются (хинди ≠ русский);
они только наполняют `hindi_sense` карточки и могут попасть в `corroborated_by`
как `"Hindi"` (правило 8 в
[../pwg_ru_prompts/4_korpus_proverka.txt](../pwg_ru_prompts/4_korpus_proverka.txt)).

Исходные `.babylon` лежат (gitignored) в `../research/external/`; выходные
`*.jsonl` тоже gitignored.

## Санскритские синонимы из кош (indic-dict) — `build_kosha.py`

Санскритско-санскритские СИНОНИМИЧЕСКИЕ коши indic-dict (НЕ из Cologne) питают
санскритскую корроборацию значения (поле `skd_vcp_synonyms`, правило 5) — какой
референт у головного слова, через его санскритские синонимы. НИКОГДА не русская
глосса, не корректность. [build_kosha.py](build_kosha.py) → `kosha_syn.jsonl`,
строка `{source, slp1, dev, syn_dev, syn_slp1}`. **88 839 строк ≈ 7.8 %
заглавных слов PWG** — только ИСТИННО синонимические коши (жанр nAmamAlA):
Amarakosha `amara-onto` (явное поле `समानार्थक:`), nAmamAlikA, дополнения
Abhidhanachintamani (parishiShTa/shilonCha). **Исключены аудитом 2026-06-24** (не
синонимы): anekArtha- (омонимы/многозначность: svarga↦गो/अक्षि/जल), bhUtasankhyA
(числовые код-слова), upasargArthachandrikA (корень↔приставочный), jhaLkI-nyAya
(вариант с висаргой), vaiShNava-/shaiva-kosha (ярлыки HTML-таблиц); а также
`amara-sudhA` = паниниева деривация (prakriyA, для парадигм, не сюда),
`laxaNa-sangraha` = ньяя-определения, `ekAkSharanAmamAlA` = только стих,
`e-bhAratI-sampat` ≈3 строки.
Коши уже в csl-orig (skd/vcp/abch/armh) сюда НЕ берутся.

## Латинские биномены растений (Meulenbeld=SNP) — `build_meulenbeld.py`

[build_meulenbeld.py](build_meulenbeld.py) парсит уже извлеченный глоссарий
названий растений Meulenbeld (= Cologne-словарь **SNP**) → `meulenbeld_plants.jsonl`,
строка `{slp1, stem, dev, binomials, sa_equivalents, gloss}`. **453 заглавных
слова, 235 с латинским биноменом** (`ajamodA`→*Apium graveolens*,
`agaru`→*Commiphora roxburghii*). Поле карточки `latin_binomials` — детерминированно
закрывает «латинский биномен оставлен непереведенным» (`Hedysarum gangeticum`).

## Корпусный лексикон пословного выравнивания (DeepSeek) — `build_corpus_lexicon.py`

Главный **множитель повторного использования**: пословное (word-by-word)
санскритско-русское выравнивание всего параллельного корпуса. Для каждой
выровненной по стиху пары Sa↔Ru из SamudraManthanam DeepSeek сопоставляет
каждому санскритскому знаменательному слову его русское соответствие **в этом
переводе**. Пакетно (~8 стиховых единиц на вызов, 12 потоков), append-only,
возобновляемо.

| Файл | Что | Записей |
|------|-----|---------|
| `corpus_lexicon.jsonl` | пословный лексикон Sa→Ru, ключ SLP1 | **1 091 528** |

Строка: `{group, work, passage, slp1, sa, ru, kind(translation|commentary),
genre, period, date}`. Соединение с заглавным словом — по `slp1`; дает
**эмпирическое распределение засвидетельствованных русских соответствий** на
слово (напр. `agni`→Агни ×1111 / огонь ×~600; `akṣara`→слог / Непреходящее;
`ananta`→бесконечный / Ананта). Постишевые **опубликованные** русские переводы
(Елизаренкова РВ/АВ, акад. Махабхарата, русские Гиты) — в
`SamudraManthanam/web/corpus.db` по `canonical_id` (`#sa`/`#ru`).

> ⚠️ **Где искать.** Ключ DeepSeek задается через окружение
> (`ai_service.py`/`.env`), а `corpus_lexicon.jsonl` в `.gitignore` — поэтому
> `grep -ri deepseek` по репозиториям **ничего не находит**. Ищите по артефакту
> (`build_corpus_lexicon.py` / `corpus_lexicon.jsonl`), не по строке «deepseek».
> Сборка — DeepSeek, июнь 2026; история и ловушка галлюцинаций (плейсхолдер `…`)
> — в [../CHANGELOG.md](../CHANGELOG.md).

**Потребитель (2026-06-24):** корпусная русская опора в
[../../article-comparison/](../../article-comparison/) (`*.corpus-ru.md` для
agni/anya/akṣara/ananta).

## Регенерация

```sh
python build_src.py [путь-к-SamudraManthanam]      # 5 санскр.-рус. словарей
python build_glossaries.py [путь-к-SamudraManthanam] # 2 специализированных глоссария имен
python build_indic.py [путь-к-.babylon-каталогу]   # хинди-сигнал значения
python build_kosha.py [путь-к-.babylon-каталогу]   # санскритские синонимы из кош
python build_meulenbeld.py [путь-к-.babylon-каталогу] # латинские биномены растений
python build_corpus_lexicon.py build <textfile> [N]  # пословный лексикон (нужен DEEPSEEK_API_KEY в .env)
python build_corpus_lexicon.py status                # записей + различных ключей
```

`build_corpus_lexicon.py` рассчитан на плохой интернет/API: вызовы идут с
настраиваемыми повторами (`DEEPSEEK_RETRIES`, `DEEPSEEK_CONNECT_TIMEOUT`,
`DEEPSEEK_READ_TIMEOUT`, `DEEPSEEK_BACKOFF_BASE`), готовые группы пропускаются,
а полностью сорванные API-батчи пишутся в `corpus_lexicon.failures.jsonl`.
Их можно добрать позже той же командой с `--retry-failed`; основной JSONL при
этом остается append-only и не переписывается.

`build_src.py` по умолчанию читает `web/corpus_builder/jsonl/` соседнего
репозитория SamudraManthanam; `build_indic.py` — `../research/external/`.

## Реноовская разметка: язык-состояние (I–V) + регистр

Отдельная подсистема в этом же `src/` — диахроническая разметка каждого
словарного значения по **пяти состояниям санскрита Луи Рену** (I ведийское ·
II паниниевское · III эпическое · IV классическое · V буддийско-джайнское) и по
ортогональной оси **регистра** (подразделы Рену: épigraphique, bhāṣya, kāvya …).
Полное описание — [../RENOU.md](../RENOU.md); план оси регистра —
[../RENOU_SUBSECTIONS_PLAN.md](../RENOU_SUBSECTIONS_PLAN.md); структура книги-
источника — [VisualDCS/docs/Renou_1956_structure.md](https://github.com/gasyoun/VisualDCS/blob/main/docs/Renou_1956_structure.md).

| Файл | Роль |
|------|------|
| [renou.py](renou.py) | резолвер состояний + политика min-support (`filter_dcs_states/_registers`) |
| [renou_sigla.py](renou_sigla.py) | сигла Apte/Benfey/BHS → состояние + `SIGLUM_REGISTER` |
| [renou_register.py](renou_register.py) | ось регистра: канон `REGISTERS` + `<ls>`-маршруты (вкл. dedicated `epig`) |
| [build_dcs_renou.py](build_dcs_renou.py) | скан корпуса DCS → лемма-индекс (`state_support` + `register_support`) |
| [tag_dict_from_source.py](tag_dict_from_source.py), [tag_mw_from_source.py](tag_mw_from_source.py) | теггер: оба поля `renou_*` и `renou_register*` |
| [renou_pipeline.py](renou_pipeline.py) | драйвер (`--all` → `{code}.renou.jsonl`) |
| [renou_portrait.py](renou_portrait.py) | редакторский ярлык: состояние + регистр + флаги малоинформативности |
| [renou_audit.py](renou_audit.py) | межсигнальный аудит (состояние + режим регистра) |
| [renou_glossary.py](renou_glossary.py) | глоссарии по регистру/состоянию → [../glossaries/](../glossaries/README.md) |

Выходы (`dcs_lemma_renou.json`, `{code}.renou.jsonl`) — **в `.gitignore`**,
регенерируются. Глоссарии (épig 709 · bhāṣya 14 498 · jaina 286) **закоммичены**
как готовые артефакты в [../glossaries/](../glossaries/README.md).

## Git и авторские права

`*.jsonl` здесь — **в `.gitignore`**, данные не коммитятся: современные словари
(Кочергина, Фриш, Смирнов) под авторским правом; Коссович (1854) и Кнауэр (1908)
— public domain. В репозитории — только [build_src.py](build_src.py) и этот файл
(воспроизводимый контракт), а сами данные собираются локально / на сервере.

## Служебные скрипты: общий помощник, хаб-цитируемые, архив

**Общий помощник:** [safe_filename.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/safe_filename.py)
— де-факто разделяемый модуль (импортируется 27 скриптами: 14 верхнего уровня + 13 в
`pilot/`); зарегистрирован в орг-карте
[SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md). Тот же
паттерн «помощник без регистрации» повторяют
[_ls_extract.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_ls_extract.py),
[gold_sample.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_sample.py) и
[build_dcs_freq.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dcs_freq.py).

**Цитируются в хабах Uprava** (держать, в репо-доках больше нигде не упомянуты):
[a43_family_stats.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/a43_family_stats.py)
(статья A43 в [ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)) и
[build_pwg_freq_order.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_pwg_freq_order.py)
(PROJECT_INTERLINKS / реестр handoff'ов).

**Архив — осиротевшие скрипты, оставлены с причиной** (аудит H738, 18-07-2026; ни один
не менялся после графта клона 09-07-2026):

- [_build_agni_ru.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_build_agni_ru.py) — рукописные RU-глоссы agni (Track B): несёт данные, не только код;
- [_build_skeletons_ru.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_build_skeletons_ru.py) — на него ссылаются живые доки `article-comparison/*.gloss-review.md`;
- [_nws_defect_scan.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_nws_defect_scan.py) — переиспользуемый QA-сканер дефектов NWS-корпуса;
- [_purge_lexicon.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_purge_lexicon.py) — одноразовое восстановление, упомянут в [RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md);
- [gold_aggregate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_aggregate.py) — агрегатор gold-точности (семейство `gold_*` стоит в CI-гейте).

Удалён как доказуемо мёртвый:
[_nws_watch.py](https://github.com/gasyoun/SanskritLexicography/blob/5aaee0672e6465eca8a3debb082ce9cf15a20840/RussianTranslation/src/_nws_watch.py)
— вотчер давно завершённого NWS-скрейпа, ноль ссылок во всём репозитории (ссылка — на
последний коммит перед удалением).
