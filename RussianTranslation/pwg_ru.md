# Словарь `pwg_ru` — русский перевод Большого Петербургского словаря

_Created: 09-07-2026 · Last updated: 24-07-2026_

> Документ для **редактора**. Описывает, **как устроен** AI-перевод Большого
> Петербургского словаря (`pwg_ru`, Бетлингк–Рот): кто переводит и кто судит
> сегодня, по каким проходам собирается издание, и — главное — **как устроен
> формат** карточки, которую вы правите, чтобы заранее понимать логику
> разметки и не «чинить» то, что задумано намеренно.
>
> **Статус (24-07-2026): производство живо.** Это уже **не план будущего
> запуска**, а редакторский срез живого конвейера. RU-склад
> `src/pwg_ru_translated.jsonl` — **11 603** строки (sense-level, локальный,
> gitignored; после hash-locked repair H1080). Вселенная — **106 082**
> заглавных слова; остаток по H1339: **~5 580** уникальных (701 verb + 4 757
> nominal-PWG + 122 no-PWG). Пилот качества (38 единиц) — 37/38 publishable.
> Операторский runbook:
> [src/pilot/RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md);
> глубина для сопровождающего:
> [docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md);
> журнал очереди:
> [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md).
>
> **Теоретическая основа.** Правила перевода и рубрика судьи опираются на
> профильную лексикографическую литературу:
> [LITERATURE_FOR_PWG_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LITERATURE_FOR_PWG_RU.md)
> (по точкам подключения),
> [MANUALS_FOR_PWG_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/MANUALS_FOR_PWG_RU.md)
> (аудит 37 руководств) и
> [MANUALS_FIVE_DEEP_DIVE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/MANUALS_FIVE_DEEP_DIVE.md)
> (пять ключевых: Апресян, Riemer, Hartmann & James, Gonda–Vogel, Klosa).
> Готовые таблицы —
> [glossaries/de_ru_translation_aids.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/glossaries/de_ru_translation_aids.md).

---

## 1. Что такое `pwg_ru` в двух словах

`pwg_ru` — **живой** русский (и вторичный английский) перевод классического
санскритско-немецкого **Большого Петербургского словаря** (*Petersburger
Wörterbuch*, PWG; Бетлингк и Рот, 1855–1875). Немецкий оригинал (`pwg`) —
public domain; русская версия — производная от него. Склад и TM **не
публикуются** (репозиторий публичный; bulk RU gitignored).

Источник — **плотный научный немецкий язык XIX в.** с орфографией той эпохи
(`thun`, `That`, `Theil`, `negirende`), длинными придаточными и обилием
латинских вкраплений. Это главное отличие от завершённого `mw_ru`, где
переводили английскую «обвязку».

**Переводится не весь видимый текст статьи целиком**, а только немецкая проза
и немецкие глоссы. Санскрит, грамматические сокращения, ссылки на источники и
латинские вставки **остаются нетронутыми** (раздел 4 — ключевой для
понимания формата).

**Источник карточки — не один `pwg.txt`.** Единица перевода — **5-слойная
all-in-one карточка**
([src/_pilot_gen_merged.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py)):
PWG main + Nachträge + PW + SCH + PWKVN + NWS (owner-mapped), live с 17-06-2026.
Суффиксы sub-card: `_zz_pw`, `_zz_sch`, `_zz_pwkvn`, `_zz_nws00`. Леммы без
PWG-слоя, но с supplement — lane **no-PWG** (`<key>~~h0_zz_<layer>`).

---

## 2. Кто переводит и кто судит (актуальное состояние)

Два разных слоя: **кто переводит** (пишет русский текст) и **кто судит**
(оценивает, текст не пишет). Плюс **корпусная сверка** — неблокирующий
аннотатор (раздел 7).

**Слой 1 — переводчики** (то, что ляжет в словарь):

| Модель | Роль |
|--------|------|
| **Claude Sonnet 5 (`claude-sonnet-5`)** | **Основной переводчик** — pin на каждом `agent()` call (H818, SHARED RU/EN) |
| **Claude Opus 4.8 (`claude-opus-4-8`)** | переписывает/адъюдикирует reject'ы (`ok=false` \|\| `severity>=3`) |
| Механические regex / stage2 pre-gate | системные ошибки без LLM (H405: ~99.7% CLEAN на store) |
| Yandex | **спроектирован**, не в bulk-production |

**Слой 2 — QA** (bulk ≠ per-card LLM judge):

| Механизм | Роль |
|----------|------|
| **Четыре free Python-гейта** (`audit_window.py`) | 100% карточек, 0 tokens: NWS owner-map · markup fidelity · sense coverage · sense duplicates |
| **Sonnet judge + Opus на rejects** | только Python-flagged + ~10% clean sample (`judge_sample.keys.txt`) |
| YandexGPT 5.1 | **спроектирован** как второй судья; bulk path его не ждёт |

**Слой 3 — корпусная сверка** (live, non-blocking):
[src/corpus_gate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py)
выдаёт **два сигнала** и **никогда не задерживает** карточку.

| Сигнал | Что меряет | Источники | Вывод |
|--------|------------|-----------|-------|
| **(1) Корректность** | согласуется ли RU-термин с **независимым** S→R словарём | **Кочергина** (якорь), **FRI**, **KNA**, **Смирнов** | `pass / divergence / no-check / key-mismatch` |
| **(2) Согласие с эталоном** | близость к **человеческому** PWG→RU | **KOW** (Коссович ← WIL) — эталон сходства, **не** sole arbiter корректности | `high / partial / none / no-ref` |

**Схема в одной фразе:** Sonnet 5 переводит окно (headless CLI, manifest v2) →
четыре free-гейта принимают bulk → requeue/TM → promote → corpus_gate
аннотирует; LLM-судья — только sample + rejects. **Нет Claude API key** —
generation идёт через profile-bound headless CLI (`CLAUDE_CONFIG_DIR`), не
через Python Anthropic SDK.

**Затравка из `mw_ru`.** Для общих заглавных слов готовая `mw_ru`-карточка —
**терминологический ориентир**, не источник: переводится немецкий PWG.
Harvest-seed заблокирован, пока отдельный `mw_ru` working repo не найден;
production идёт без него.

---

## 3. Проходы (как собирается издание сейчас)

Сборка **append-only / better-attempt-wins**: новые версии не стирают старые
вслепую; promote merge'ит на sub-card level; requeue не может регрессировать
карточку (`save_and_audit.py --merge`, H304).

| Этап | Что делается | Модель / инструмент | Промпт / код |
|------|--------------|---------------------|--------------|
| **0. Пилот / bar** | 38-unit judge test; 37/38 publishable; quality settled early | multi-model | [PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) |
| **1. Основной перевод** | frequency / worklist windows: 5-layer cards, mask → batch → headless Sonnet 5 | **Sonnet 5** via headless manifest v2 | harness TR + [1_perevod.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru_prompts/1_perevod.txt) |
| **2. Deterministic audit** | NWS · markup · coverage · dupes + stage2 pre-gate | pure Python | [audit_window.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) |
| **2b. Requeue** | transient nulls (cheap) vs defect (TM off + fragment denylist) | Sonnet 5 re-run | [requeue_from_audit.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/requeue_from_audit.py) |
| **3. Sampled LLM QA** | только `judge_sample.keys.txt` | Sonnet; Opus on rejects | [2_qa_sudya_*.txt](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru_prompts) |
| **4. Механика** | системные 130+-repeat ошибки | regex / stage2 | [stage2_pregate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/stage2_pregate.py) |
| **5. Promote + TM** | store write (fsynced atomic) + TM rebuild; **только** bound manifest-v2 | scripts | [promote_final_cards.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) |
| **6. Корпусная сверка** | два сигнала, non-blocking | [corpus_gate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py) | — |
| **7. Human review** | G5/G6 sheets; print gates G7/G10 | HTML review sheets | [pwg-review-packet](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-review-packet.md) |

**Execution route (H1110, с 18-07-2026):** production =
`headless_worker.py` + coordinator + `execution_route: claude-cli-headless`
(manifest v2). Max-Workflow (`run_pilot_wf.opt2.js` в Workflow tool) —
**только forensics**, не production. Перед платным окном:
[`/pwg-live-gate`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md)
(≥5 KB health + `dq_canary_puregloss`); spend:
[`/pwg-bounded-run`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-bounded-run.md)
(один profile, max-wide=1, `--stop-before-promote`).

После каждого promote словарь «слойный»: base Sonnet + requeue heals +
механические правки + corpus annotations; human gold — отдельный gate.

---

## 4. Как устроена карточка — что переводится, а что НЕТ

Это самый важный раздел для редактора. Карточка PWG — **размеченный фрагмент**
со специальными тегами. Перед нейросетью текст **маскируется**: всё
непрозрачное прячется за `{T1}, {T2}, …`; модель видит только немецкий текст
между ними. После перевода маркеры вставляются обратно. Схема плейсхолдеров
та же, что в `mw_ru`, плюс PWG-специфика `{%…%}`.

Маскировщик:
[src/pwg_mask.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py)
— verified **123 365 / 123 366** records round-trip losslessly (один known-lossy
record → per-card round-trip assertion обязателен).

### Что НЕ трогается (остается как в оригинале)

| Маркер | Что это | Пример |
|--------|---------|--------|
| `{#…#}` | санскрит в SLP1 | `{#aMSumAlA#}`, `{#a + kARqa#}` |
| `<ls>…</ls>` | ссылка на источник | `<ls>ṚV. 3,45,4</ls>` |
| `<ab>…</ab>` | научное сокращение (нем./лат.) | `<ab>Sch.</ab>`, `<ab>vgl.</ab>` |
| `<is>…</is>` | санскрит IAST / онимы | `<is>Viṣṇu</is>` — **siglum text**, не RU-gloss wrapper |
| `<lex>…</lex>` | часть речи / род | `<lex>m.</lex>` |
| `<lang n="…">…</lang>` | иноязычный когнат | `<lang n="greek">ἀ, ἀν</lang>` |
| `<L>…`, `<LEND>` | границы записи | `<L>29<pc>1-0005…` |
| `<div n="1\|2\|v\|p\|u">` | нумерация значений / деления | `<div n="v">— <ab>Vgl.</ab> …` |
| `<H>…</H>`, `[PageN-PPPP]`, `¦`, `˚` | служебное / элизия | |

### Метка Рену (I–V) по `<ls>`

Текст `<ls>` не переводится, но **читается**: детерминированно выводится
языковое состояние по Рену (*Histoire de la langue sanskrite*): **I** ведийское ·
**II** паниниевское · **III** эпическое · **IV** классическое · **V**
буддийско-джайнское. Карта — [src/ls_source_map.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json);
проставляет [src/annotate_renou.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_renou.py).
Метки — **badges/context only**; **не** повод переставлять senses.

**Обогащение DCS:** второй слой attestation
([src/enrich_renou_dcs.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/enrich_renou_dcs.py))
добавляет `renou_dcs` / `renou_enriched` / `renou_provenance` на уровне
леммы, не затирая per-sense `<ls>`-метку.

### Что переводится

- **немецкая связная проза** между тегами;
- **немецкие глоссы** `{%…%}` (правило ниже);
- содержимое **`<F>…</F>`** (мелкошрифтные примечания Бетлингка: разметка
  маскируется, немецкий переводится).

### Главное правило PWG: `{%…%}` — немецкое переводим, латинское НЕТ

Скобки `{% %}` **на выходе всегда сохраняются**; решается только судьба
содержимого:

- **немецкая `{%…%}`** → раскрыть, перевести, **снова обернуть** в `{% %}`.
  `{%das Nichthandeln%}` → `{%недеяние%}`.
- **латинская `{%…%}`** → один `{Tn}`, **дословно**.
  (`{%in%}`, `{%Trapa bispinosa%}`, …).
- **английская** ремарка Уилсона (`Wils. übersetzt … durch {%leaving…%}`) →
  как латынь, **не** на русский.

### Пунктуация несет смысл

- `;` — **разные значения**;
- `,` — **синонимы внутри одного значения** (`{%Gabe, Geschenk%}` → `{%дар, подарок%}`).

Количество и позиции сохраняются. Нумерация (`1)`, `a)`) и тире `—`/`--` едут
с разметкой.

### Presentation layer (render-time, не store)

[src/pilot/build_article_site.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py)
+ [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md):
грамматические `<ab>` остаются international Latin + tooltip; editorial /
cross-ref — RU (ruled 10-07-2026). **Не** «чините» store, меняя то, что
должно жить только на render.

---

## 5. Промпты

[pwg_ru_prompts/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru_prompts)
— зеркало `mw_ru_prompts/`, переписанное под немецкий источник. **Live harness**
inline'ит production TR (lean-TR A/B отвергнут); эти файлы — editor/history
kit + sampled judge.

| Файл | Этап | Статус |
|------|------|--------|
| [1_perevod.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru_prompts/1_perevod.txt) | основной перевод + глоссарии | live seed for TR |
| [2_qa_sudya_opus.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru_prompts/2_qa_sudya_opus.txt) | sampled QA (Opus path) | ready |
| [2_qa_sudya_yandexgpt.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru_prompts/2_qa_sudya_yandexgpt.txt) | second judge (designed) | ready, not bulk |
| [3_pereperevod_opus.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru_prompts/3_pereperevod_opus.txt) | rewrite rejects | ready |
| [4_korpus_proverka.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru_prompts/4_korpus_proverka.txt) | corpus-gate schema | implemented in `corpus_gate.py` |

**PWG-специфика рубрики судьи** (сверх `mw_ru`):

1. категория «латинская `{%…%}`, ошибочно переведенная» / зеркало;
2. раскрытие нем. сокращений по русской традиции vs calque;
3. калибровка на реальных PWG-карточках буквы `a`.

Severity ≥ 3 → rewrite / Opus adjudicate.

---

## 6. Известные слабые места (на что смотреть при вычитке)

1. **`{%…%}` нем. vs лат.** — главный PWG-риск; флаг `das lat.`, botany binominal, Wilson EN.
2. **Плотный придаточный XIX в.** — `<div n="v">`, `<F>…</F>`.
3. **Сокращения.** UI-tooltip: внутри `<ab>` **не** разворачивать в store-текст.
4. **Орфография оригинала** (`thun`, `That`, `negirende`) — глоссарий ключует обе формы.
5. **SLP1 с акцентами** в `{#…#}` — целиком маскируется.
6. **Длинные глагольные статьи** — multi-sense, causative/desiderative chains, `<div n="p">`.
7. **German residue** в promoted store — отдельный sweep (H1302+); requeue, не silent edit.
8. **Presentation vs store** — RU-column purity / tooltips на render; store держит source-faithful markup.

---

## 7. Корпусная сверка (live)

### 7.1. Два сигнала

Ступень **неблокирующая**: размечает карточку, сомнительное → редактору,
из словаря **не отзывает**.

1. **Корректность** — `pass` / `divergence` / `no-check` / `key-mismatch`
   только по **независимым** S→R (Кочергина ∪ FRI ∪ KNA ∪ Смирнов).
2. **Согласие с эталоном** — `high` / `partial` / `none` / `no-ref` vs **KOW**.

**Почему два сигнала.** KOW — частичный human PWG→RU из WIL; идеальный эталон
сходства, но **не** sole arbiter корректности. SKD/VCP — санскрит↔санскрит,
**ноль** кириллицы → корректность **не** решают (конфиг, гонящий RU-check на
них, должен hard-fail).

**Пять извлечённых словарей**
([src/build_src.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_src.py),
~57 634 записей, gitignored):

| Файл | Источник | n | Роль |
|------|----------|---|------|
| `koch.jsonl` | Кочергина 1987 | 29 177 | главный якорь корректности |
| `fri.jsonl` | Frisch 1956 | 8 151 | независимый |
| `kna.jsonl` | Knauer 1908 | 3 271 | независимый, PD |
| `smirnov.jsonl` | Смирнов 1955–89 | 3 547 | независимый |
| `kow.jsonl` | Коссович 1854 | 13 488 | эталон согласия; вторичное подтверждение |

Плюс **corpus_lexicon.jsonl** (~1.09M verse-aligned pairs, DeepSeek/OpenRouter)
и мягкий слой SamudraManthanam parallel corpus (verse-level, не word-level) —
корроборант + цитаты, не `pass` arbiter.

Ключи — SLP1 `form_key()` (length-preserving, **не** NFD+strip).

### 7.2. Где живут артефакты

В отличие от раннего плана («отдельный working repo, как mw_ru»), **pipeline,
скрипты, prompts, article site, research — в этом дереве**
`RussianTranslation/`. Gitignored: store, TM, harvested dicts, bulk review
HTML, regenerable ledgers.

| Артефакт | Где | Статус |
|----------|-----|--------|
| RU/EN store | `src/pwg_ru_translated.jsonl` (+ EN) | local-only; **11 603** RU rows (24-07-2026) |
| 5-layer inputs | `_pilot_gen_merged.py` output | regenerable |
| TM sidecars | `translation_memory.*` | rebuild after every promote |
| PWG source layer | `csl-orig/v02/pwg/pwg.txt` | read-only input |
| Operator loop | [RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) | headless v2 |
| Parity | [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) | SHARED / INTENTIONAL-DIVERGENCE / GAP |
| Live queue | [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md) | subordinate to repo-root journal |

### 7.3. Открытые / human-gated (не «до запуска»)

Дизайн сверки и supply словарей **закрыты**. Остаётся human gate:

1. **Print gates G5–G10** — human gold / double review / edition cut
   (`preflight_remaining_gates.py` report-only by default).
2. **H1303 / H1306** — ratification sheets (abbrev unified list; style doublets /
   `v. l.` / *im Comp.*) ждут vote → `*.decisions.json`.
3. **TM public release** — rights clearance на grey parallel-corpus works
   (H1458 bundles ready; publish fenced).
4. **Palsule XLS** — H1333 blocked until the spreadsheet lands.
5. **mw_ru seed** — locate the finished-cards repo for terminology seed.

---

## 8. Куда идти дальше

| Нужно | Документ |
|-------|----------|
| Операторский loop, verbatim | [src/pilot/RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) |
| Глубина lanes/gates/kill | [RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md) |
| «Как мы сюда пришли» | [PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) |
| 18 intent→command maps | [USE_CASES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/USE_CASES.md) |
| Очередь / WIP | [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md) |
| MW-редакторский twin | [mw_ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md) |

_Dr. Mārcis Gasūns_
