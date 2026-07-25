# Словарь `pwg_ru` — русский перевод Большого Петербургского словаря

_Created: 09-07-2026 · Last updated: 25-07-2026_

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

#### `gloss_lang` rule table (H1624 G1 — durable metadata, not a DE rewrite)

Stage-0 classifier in
[pwg_mask.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py)
(`classify_pct_detail` / `gloss_lang_spans`). Emits sidecar list
`{span, gloss_lang, rule_id, start, end, translate}` for every `{%…%}`.
**Does not** rewrite 19th-c. German orthography or inject RU into DE.

| `gloss_lang` | `rule_id` | Cue / surface | Mask? |
|---|---|---|---|
| `la` | `latin_cue` | preceding `lat.` / `latein` / `griech.` / `gr.` (incl. inside `<ab>`) | yes `{Tn}` |
| `la` | `latin_phrase` | `De accentu…` / genuine Latin openers (C8: `In der Regel` stays DE) | yes |
| `la` | `botany_binomial` | title-case Genus + lowercase epithet (`Trapa bispinosa`); German noun phrases rejected | yes |
| `en` | `wilson_en` | `WILS.` / `Wilson` near span **and** English content | yes |
| `en` | `engl_cue` | `engl.` / `englisch` near span **and** English content | yes |
| `en` | `english_content` | clear English markers, no German | yes |
| `ambig` | `homograph_ambig` | short `in`/`an`/`et`… tokens | no (inline, flagged) |
| `de` | `default_de` | everything else (incl. Wilson + German content like `{%Honig%}`) | no (translate) |

CLI: `python src/pwg_mask.py gloss-langs <key1>` · `python src/pwg_mask.py --selftest`.
Residue gate (`prompt_rule_audit.looks_foreign_literal`) shares the same classifier
so Latin/Wilson preserved literals are not requeued as untranslated German.

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

## 8. Что слои разметки **могут** и **ещё не могут** ответить

Карта возможностей — не runbook. Операторский deep manual описывает *как*
гнать окно; этот раздел — *какой вопрос* уже опирается на слои, *где* смотреть
ответ, и *где честная дыра*. Покрытие store (25-07-2026): **11 603** sense-row;
поля layer / provenance / 
eview_status — на всех; vidence_summary —
~10.8k; полный vidence[] — ~2.2k; differentia — ~4.7k.

Все ссылки в таблицах **кликабельны** (blob URL для committed docs; relative path
для local-only store/sheets — открываются из клона в редакторе).

### 8.0. Какие слои добавляются **к немецкому оригиналу** (в процессе перевода)

Важно: «слой» ≠ всегда «новый русский текст». Часть слоёв — это **сборка и
обогащение немецкой (и supplement) исходки** до/вокруг LLM; часть — **поверх**
перевода.

`
csl-orig pwg.txt  ──►  5-layer merge  ──►  portrait + raw  ──►  mask {Tn}
        │                    │                    │                 │
        │                    ├─ PW/SCH/PWKVN/NWS  ├─ NWS owners     ├─ model sees DE only
        │                    │   labeled in raw   ├─ microstructure │
        │                    │                    └─ corpus portrait│
        └─ markup already in German: {#}, <ls>, <ab>, <div>, {%…%}
                                                                  │
                              RU/EN + evidence + review ◄─────────┘
                              (после LLM; evidence читает RU, не пишет DE)
`

| Когда | Что добавляется **к немецкой стороне** | Код / doc |
|-------|----------------------------------------|-----------|
| **Уже в PWG print/XML** | Разметка оригинала: {#…#}, <ls>, <ab>, <is>, <lex>, <div>, {%…%}, Nachträge в PWG | [csl-orig pwg](https://github.com/sanskrit-lexicon/csl-orig/tree/master/v02/pwg); [§4](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md) |
| **Pre-LLM: merge** | В **одну** карточку склеиваются немецкие слои **PWG main + Nachträge + PW + SCH + PWKVN + NWS** (каждый labeled в raw) | [_pilot_gen_merged.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py); [PWG_LAYER_COMBINATIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md) |
| **Pre-LLM: portrait** | JSON-портрет микроструктуры + corpus evidence **по немецкому headword** (не перевод) | output: [example portrait](src/pilot/input/nakzatra.portrait.json) · [example raw](src/pilot/input/nakzatra.raw.txt) |
| **Pre-LLM: NWS owners** | Детерминированный owner-map **дописывается** к raw/portrait (кто автор NWS-фрагмента) | [
ws_split.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nws_split.py); [NWS_SOURCE_DEFECTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NWS_SOURCE_DEFECTS.md) |
| **Pre-LLM: mask** | Немецкий текст **трансформируется** в skeleton + {Tn} (Sa/cite/gram прячутся) — это не новый смысл, а форма подачи модели; LA/EN `{%…%}` → `{Tn}` | [pwg_mask.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py) |
| **Pre-LLM: sense tags / splits** | Канонические sense tags, citation batches, root/head splits — нарезка **немецкого** body | same merge + harness; [FAILURE_MODES…](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FAILURE_MODES_AND_KILL_GATE_2026-07-04.md) |
| **Derived from DE markup (не правка DE string)** | **Renou I–V** из <ls>; **government** (Rektion) + **form_labels** (number/gender/nom\|voc/voice) from DE (H1624); ab frequency; **`gloss_lang` per `{%…%}`** (de\|la\|en, H1624 G1) | [RENOU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md); [H1308](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1308-Opus_RussianTranslation_pwg-ru-valency-government-index_19.07.26.md); [form_labels.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/form_labels.py); [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md); [§4 gloss_lang table](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md) |
| **Grammar layer** | Whitney / Zaliznyak **рядом**, в prompt **не** вставляется (A/B reject) | [NOMINAL_GRAMMAR_AB.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NOMINAL_GRAMMAR_AB.md) |
| **Post-LLM (не на DE)** | Поля 
u / n, vidence* (по RU), 
eview_status, provenance, render tooltips | [§7](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md); [corpus_gate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py); [uild_article_site.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py) |

**Итог одной фразой:** к немецкому оригиналу в pipeline **добавляются** (1) тексты
других немецких supplement-слоёв, (2) structural labels/owners/portrait, (3)
mask-форма для модели, (4) производные индексы из уже существующей DE-разметки.
**Не** добавляются в сам немецкий gloss: русский перевод, corpus_gate verdicts,
review_status — они живут **рядом** в store/site.

### 8.1. Слои (краткий реестр)

| Слой | Что это | Поверхность / детали |
|------|---------|----------------------|
| **L0 маска** | {#}, <ls>, <ab>, <is>, <lex>, {%…%} (+ **gloss_lang** de\|la\|en), <div> | [§4 format](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md); [pwg_mask.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py); H1624 G1 |
| **L1 5-dict stack** | PWG + Nachträge + PW + SCH + PWKVN + NWS | [_pilot_gen_merged.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py); [PWG_LAYER_COMBINATIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md) |
| **L2 NWS owners** | детерминированный owner-map | [NWS_SOURCE_DEFECTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NWS_SOURCE_DEFECTS.md); [nws_split.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nws_split.py) |
| **L3 Renou I–V** | состояние языка по <ls> (+ DCS enrich) | [RENOU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md); [annotate_renou.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_renou.py); [enrich_renou_dcs.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/enrich_renou_dcs.py) |
| **L4 government** | Rektion из (<ab>Instr.</ab>) и т.п. — **на каждом sense** (store + portrait); promote stamps from DE; floor vs ceiling | [government.html](https://gasyoun.github.io/SanskritLexicography/government.html); [H1308](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1308-Opus_RussianTranslation_pwg-ru-valency-government-index_19.07.26.md); H1624 G2; [annotate_government.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_government.py); [enrich_portrait_government.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/enrich_portrait_government.py) |
| **L4b form_labels** | Number / gender / nom\|voc / voice from DE (`sg.`/`pl.`/`<lex>m.</lex>`/…); **not** Rektion | [form_labels.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/form_labels.py); H1624 form-layer; [annotate_form_labels.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_form_labels.py) |
| **L5 abbreviations** | tooltips + частоты <ab> | [abbreviations.html](https://gasyoun.github.io/SanskritLexicography/abbreviations.html); [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md) |
| **L6 evidence / corpus_gate** | pass/divergence vs Koch…; agreement vs KOW | [§7 corpus](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md); [corpus_gate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py); [H335 archive](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H335-Fable_RussianTranslation_pipeline-capability-audit_08.07.26.md) |
| **L7 grammar / Zaliznyak** | class, reverse paradigm | [ZALIZNYAK_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md); [NOMINAL_GRAMMAR_AB.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NOMINAL_GRAMMAR_AB.md) |
| **L8 relationships** | тип supplement sense | [relationships_rollup.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/relationships_rollup.tsv); [REGLUE_SPEC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md) |
| **L9 provenance** | model, hashes, pipeline | [store (local)](src/pwg_ru_translated.jsonl); [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md); [H1110](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1110-Opus_SanskritLexicography_pwg-ru-post-h1080-audit-fix-skills-c4-restart_17.07.26.md) |
| **L10 presentation** | tooltips, RU purity, Cyrillic <is> | [build_article_site.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py) |

### 8.2. Вопросы, на которые **уже** можно ответить (полностью или с оговоркой)

| # | Вопрос | Слои | Оговорка | Детали (все ссылки кликабельны) |
|---|--------|------|----------|----------------------------------|
| Q1 | Какой RU/DE/(EN) текст **этого** sense? | L0, store | Только promoted subset | [article site](https://gasyoun.github.io/SanskritLexicography/); [store local](src/pwg_ru_translated.jsonl); [§4 format](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md) |
| Q2 | Это PWG-base, PW, SCH, NWS…? | L1 | no-PWG lane real | [PWG_LAYER_COMBINATIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md); [_pilot_gen_merged.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py) |
| Q3 | Сохранён ли порядок values PWG? | L0 policy | Gate ≠ gold | [audit_window.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py); [AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/AGENTS.md) |
| Q4 | Что маскировалось (Sa / cite / gram)? | L0 | 1 known-lossy record | [pwg_mask.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py); [§4](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md) |
| Q5 | Кто owner у NWS-фрагмента? | L2 | misattr → REJECTED | [NWS_SOURCE_DEFECTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NWS_SOURCE_DEFECTS.md); [NWS_AUDIT_REPORT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NWS_AUDIT_REPORT.md) |
| Q6 | Renou I–V у sense/леммы? | L3 | badge; not reorder | [RENOU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md); [annotate_renou.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_renou.py); [enrich_renou_dcs.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/enrich_renou_dcs.py) |
| Q7 | Карточки с Instr./Loc./… government? | L4 | floor vs ceiling | [government.html](https://gasyoun.github.io/SanskritLexicography/government.html); [H1308](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1308-Opus_RussianTranslation_pwg-ru-valency-government-index_19.07.26.md); [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md) |
| Q8 | Что значит <ab>X</ab> и как часто? | L5 | H1303 not voted | [abbreviations.html](https://gasyoun.github.io/SanskritLexicography/abbreviations.html); [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md); [ABBREV_UNIFIED_LIST…](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ABBREV_UNIFIED_LIST_PROPOSAL_2026-07.md) |
| Q9 | RU vs независимый S→R (Koch…)? | L6 | non-blocking; sparse vidence[] | [§7 corpus](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md); [corpus_gate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py); [DECISIONS_PIPELINE_CAPABILITY_H335.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DECISIONS_PIPELINE_CAPABILITY_H335.md) |
| Q10 | Близость RU к **KOW**? | L6 s2 | similarity ≠ truth | same Q9 links; KOW role in [§7](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md) |
| Q11 | Склонение / «как *agni*»? | L7 | not sense meaning | [ZALIZNYAK_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md); [NOMINAL_GRAMMAR_AB.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NOMINAL_GRAMMAR_AB.md) |
| Q12 | Supplement = new / restate / correction? | L8 | rollup only | [relationships_rollup.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/relationships_rollup.tsv); [REGLUE_SPEC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md); [H180](https://github.com/gasyoun/Uprava/blob/main/handoffs/H180-Opus_RussianTranslation_pwg_ru_addenda_typology_glue_learner_05.07.26.md) |
| Q13 | Model/version/hash row? | L9 | pin H818+ | [store local](src/pwg_ru_translated.jsonl); [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md); [H1110](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1110-Opus_SanskritLexicography_pwg-ru-post-h1080-audit-fix-skills-c4-restart_17.07.26.md) |
| Q14 | 
eview_status / human gold? | review | mostly i_translated | [HUMAN_GOLD_PROTOCOL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md); [GRADE_GOLD_MEMO.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/GRADE_GOLD_MEMO.md); [h178_da sheet](review/h178_da_sheet.html); [h180_typology sheet](review/h180_typology_sheet.html) |
| Q15 | German residue / broken markup? | L0 gates | detector ≠ full semantic | [audit_window.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py); [H1302 residue report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1302_GERMAN_RESIDUE_SWEEP_REPORT_2026-07-19.md); [FAILURE_MODES…](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FAILURE_MODES_AND_KILL_GATE_2026-07-04.md) |

### 8.3. Вопросы, на которые **ещё нельзя** (или только после human gate / данных)

| # | Вопрос | Почему *yet* | Разблокирует | Детали (все ссылки кликабельны) |
|---|--------|--------------|--------------|--------------------------------|
| N1 | Единый канон RU для каждого b | sheet not voted; 
= class | Session 2 after decisions.json | [H1303](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1303-Fable_RussianTranslation_pwg-ru-abbrev-unified-list-ratification_19.07.26.md); [ABBREV_UNIFIED_LIST…](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ABBREV_UNIFIED_LIST_PROPOSAL_2026-07.md); [h1303 sheet](review/h1303_abbrev_sheet.html) → target [h1303_abbrev.decisions.json](pwg_ru/eval/h1303_abbrev.decisions.json) |
| N2 | Doublets / . l. / *im Comp.* в промпте+store | Phase 2 waits vote | decisions.json | [H1306](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md); [STYLE_RESEARCH…](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/STYLE_RESEARCH_DOUBLETS_VL_COMP.md); [h1306 sheet](review/h1306_style_sheet.html) → [h1306_style.decisions.json](pwg_ru/eval/h1306_style.decisions.json) |
| N3 | Печатная G5–G10 edition | no human gold cut | G5–G6 votes | [HUMAN_GOLD_PROTOCOL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md); [readiness_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/readiness_report.md); [h180_typology](review/h180_typology_sheet.html); [h180_learner](review/h180_learner_sheet.html); [h180_reglue](review/h180_reglue_sheet.html) |
| N4 | Полный PWG→RU словарь | ~5.5k remaining + host | drain + LIVE_GO | [H1339 status](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1339/H1339_TIER_B_STATUS_2026-07-19.md); [RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md); [RESULTS_LOG](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md) |
| N5 | Sense-level corpus frequency / WSD | no full sense inventory join | Wave-2 senses | [H335 archive](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H335-Fable_RussianTranslation_pipeline-capability-audit_08.07.26.md); [sense-corpus-join skill](https://github.com/gasyoun/claude-config/blob/main/commands/sense-corpus-join.md) |
| N6 | «Sense #1 = most common»? | order ≠ Zipf | frequency layer | [RENOU_H6_ZIPF.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_H6_ZIPF.md) |
| N7 | DHĀTUP. → Palsule links | no machine list | MG XLS | [H1333](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1333-Opus_RussianTranslation_pwg-ru-dhatup-palsule-wire-from-xls_19.07.26.md) |
| N8 | mw_ru term seed on shared headwords | seed repo missing | locate mw_ru cards | [PIPELINE_ARCHITECTURE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_ARCHITECTURE.md); [mw_ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md) |
| N9 | Public TM / bulk RU download | rights grey | clearance | [H1458](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1458-Sonnet_RussianTranslation_pubgrade-tm-track-c-release-prep_22.07.26.md); [TRANSLATION_MEMORY_DATASHEET.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DATASHEET.md); [PUBLISH_PACKET.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/PUBLISH_PACKET.md) |
| N10 | EN full twin of RU | EN secondary | EN drain + parity | [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md); [H033 EN followups](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/archive/H033-Opus_RussianTranslation_pwg_en_followups_30.06.26.md) |
| N11 | All compound-split adjudications | ~4.2k diffs | review-sheet sample | [H1282 archive](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1282-Opus_SanskritLexicography_pwg-ru-derivation-portrait-enrichment_19.07.26.md); [GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) |
| N12 | Oral / register A–C everywhere | oral + style gates | sample + H1306 | [H290](https://github.com/gasyoun/Uprava/blob/main/handoffs/H290-Opus_RussianTranslation_oral_text_pdf_tm_ingest_07.07.26.md); [H1306](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md); [h1306 sheet](review/h1306_style_sheet.html) |
| N13 | «AI лучше human/KOW» | no adjudicated gold edition | G6 + judges | [HUMAN_GOLD_PROTOCOL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md); [JUDGE_POLICY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/JUDGE_POLICY.md) |
| N14 | Diachronic PW/PWG/SCH timeline UI | layers co-present only | edition-diff product | [PWG_LAYER_COMBINATIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md); [edition_deltas.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/edition_deltas.tsv) |
| N15 | Scan-page for every <ls> | partial resolver | link-target scale | [CITATION_COVERAGE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CITATION_COVERAGE.md); [cologne-link-target skill](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-link-target.md) |
| N16 | Learner-core filter on full site | scores exist; not product filter | wire scores | [REGLUE_SPEC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md); [H180](https://github.com/gasyoun/Uprava/blob/main/handoffs/H180-Opus_RussianTranslation_pwg_ru_addenda_typology_glue_learner_05.07.26.md); [h180_learner sheet](review/h180_learner_sheet.html) |
| N17 | Paid CLI drain **now** | 403 / HEALTH_NOGO | re-auth + gate | [RESULTS_LOG](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md); [GENERATION_API_PROBE_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/GENERATION_API_PROBE_LOG.md); [H1447 gate packet](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1447/H1447_C4_LIVE_GATE_2026-07-22.md) |
| N18 | «93% glyph quarantine = bad RU» | detector inflated | sample ~200 | [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md); [GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md); [quarantine file local](src/pwg_ru_translated.jsonl.h1080_quarantine.jsonl) |

### 8.4. Как читать статус

- **Q*** = можно спрашивать *сейчас* (иногда только на promoted subset / site).
- **N*** = не выдавать за готовый ответ; в manual/chat честно «ещё нет».
- Human sheets **не** «почти done» без *.decisions.json (см. linked review HTML).
- Presentation (L10) **не** чинить правкой store «для красоты».
- §8.0 отвечает: *что именно навешивается на немецкий оригинал* vs *что появляется только после LLM*.

English twin:
[docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md) §2b–§2c.

## 9. Куда идти дальше

| Нужно | Документ |
|-------|----------|
| Операторский loop, verbatim | [src/pilot/RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) |
| Глубина lanes/gates/kill | [RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md) |
| «Как мы сюда пришли» | [PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) |
| 18 intent→command maps | [USE_CASES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/USE_CASES.md) |
| Очередь / WIP | [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md) |
| MW-редакторский twin | [mw_ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md) |
| Сокращения / Rektion | [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md) |

_Dr. Mārcis Gasūns_
