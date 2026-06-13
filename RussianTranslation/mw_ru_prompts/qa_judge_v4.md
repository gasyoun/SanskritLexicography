# QA-судья V4 (tag_dropped + pre-filter + Yandex-slim)

Готовый к внедрению апдейт QA-судьи. Включает изменения из
[improvements.md](improvements.md), пункт 3.

**Целевое внедрение:**
- `data/scripts/qa_pilot.py` — основной QA_SYSTEM_PROMPT + калибровка
- `data/scripts/qa_yandex.py` — урезанный вариант для Yandex
- Новая утилита `data/scripts/qa_prefilter.py` — отсев тривиально-OK
  карточек до отправки в QA

**Применение:** перед следующим QA-прогоном (Stage B на apte_ru,
повторная валидация mw_ru, или verification post-retranslate).

**Изменения относительно v3:**

| | v3 (текущий) | v4 |
|---|---|---|
| Категория `tag_dropped` | прячется в `anchors` | **отдельная** (для метрик retranslate-output) |
| Stage-D-style пример | нет | **`{T3} {T4}` без связки = OK** |
| Yandex-промпт | полный (8K chars) | **slim (~3K chars)**, только anglicism + grammar + structure |
| Pre-filter тривиальных | нет | **отдельный шаг до QA** |

**Ожидаемый эффект на полном mw_ru QA (если бы делали с нуля):**
- Pre-filter отсечёт ~25% карточек (тривиально-OK) → экономия ~$700
- Yandex-slim снизит per-call cost на 63% → если Yandex full → ~$1 000
- Новая `tag_dropped` метрика → видно реальные регрессии retranslate

---

## 1. Новая категория `tag_dropped`

### Что это

Случай когда opaque-тег `<ab>X.</ab>` был **дропнут** в RU и заменён
русским текстом. Например EN: `<ab>N.</ab> of <ab>wk.</ab>`,
RU: `название произведения` — оба тега исчезли.

Сейчас это попадает в `anchors`, но смешивается с другими anchor-ошибками
(потеря `<s1>`, `<ls>`). Для аналитики retranslate-output важно
выделить отдельно.

### Куда добавить

В QA_SYSTEM_PROMPT, **новая категория 4** (сдвинуть hallucination → 5,
truncation → 6, anglicism → 7, grammar → 8):

```
4. **tag_dropped** — отдельный класс ошибок: opaque-тег <ab>X.</ab>
   (включая <ab>N.</ab>, <ab>wk.</ab>, <ab>partic.</ab> и т.п.) был
   дропнут в RU и заменён русским текстом. Например EN содержит
   `<ab>N.</ab> of <ab>wk.</ab>`, а в RU `название произведения`
   (теги исчезли). Это нарушение архитектурного контракта о
   неприкосновенности opaque-тегов. Использовать отдельно от `anchors`
   (там — потеря <s1>/<ls>/<bot>).
```

### Калибровочный пример

Один новый BAD-пример **с реальными тегами в body** (судья видит
демаскированный текст, не skeleton):

```python
{"category": "tag_dropped",
 "body_en": '<body><s>ra/sa—suDA<srs />kara</s> <lex>m.</lex> <ab>N.</ab> of <ab>wk.</ab><info lex="m" /></body>',
 "body_ru": '<body><s>ra/sa—suDA<srs />kara</s> <lex>m.</lex> название произведения<info lex="m" /></body>',
 "verdict": "BAD", "severity": 4, "issues": ["tag_dropped"],
 "comment": "Теги <ab>N.</ab> и <ab>wk.</ab> дропнуты в RU. "
            "Должно быть «<ab>N.</ab> <ab>wk.</ab>» (теги сохранены)."}
```

---

## 2. Stage-D-style OK пример

### Зачем

После retranslate v2 типичный вывод — `<ab>N.</ab> <ab>wk.</ab>` без
связки «of». Это **архитектурно правильно** (теги сохранены),
но судья может ошибочно счесть это `truncation` (пропущено связующее
слово). Добавить явный пример.

### Куда добавить

В `QA_CALIBRATION_EXAMPLES` — **с реальными тегами в body** (судья видит
демаскированный после reinsert_translation текст, не skeleton):

```python
{"category": "OK_post_retranslate",
 "body_en": '<body><s>X</s> <lex>m.</lex> <ab>N.</ab> of <ab>wk.</ab><info lex="m" /></body>',
 "body_ru": '<body><s>X</s> <lex>m.</lex> <ab>N.</ab> <ab>wk.</ab><info lex="m" /></body>',
 "verdict": "OK", "severity": 1, "issues": [],
 "comment": "Связка «of» опущена (русский родительный падеж не требует "
            "предлога), все теги <ab>/<s>/<lex> сохранены. Не truncation."}
```

### Контекст в QA_SYSTEM_PROMPT

В блок «Что НЕ считать BAD» добавить пункт:

```
- **Без связки «of» между сохранёнными тегами** (например `<ab>N.</ab>
  <ab>wk.</ab>` где английский был `<ab>N.</ab> of <ab>wk.</ab>`). Это
  результат архитектурно-корректного retranslate: связки «of/from/with»
  опущены, теги сохранены, русский родительный падеж не требует
  предлога. **OK, не truncation.**
```

---

## 3. Yandex-slim промпт

### Проблема

Yandex не поддерживает prompt cache. Полный промпт (8K chars) платится
**целиком на каждый запрос**. На 287K карточек full mw_ru:
- 287K × 2700 input × $0.0089/1K = **~$6 870**

Yandex слабее на anchors/structure, сильнее на anglicism/grammar/русскую
естественность. Имеет смысл специализировать.

### Slim промпт

Урезанная версия, фокус только на сильных сторонах Yandex:

```
Ты — корректор переводов санскритского словаря Monier-Williams на русский.
Тебе дают английский оригинал (body_en) и русский перевод (body_ru).
Оцени КАЧЕСТВО РУССКОГО ТЕКСТА по 3 критериям:

1. **anglicism** — калька с английского ("ходить вперёд" вместо
   "продвигаться"; "из X" как буквальный перевод "of X").
2. **grammar** — ошибки падежей, рода, согласования, орфографии.
3. **structure** — пунктуация (`;` разделяет значения, `,` — синонимы);
   нарушение количества `;`.

НЕ оценивай: семантику (semantic), потерю опорных тегов (anchors),
галлюцинации, truncation. Эти категории отдаются другим судьям.

НЕ считай ошибкой:
- сохранённые английские аббревиатуры в <ab>X.</ab> тегах
- skeleton-style output `{T1} {T2}` без связки

Возвращай ТОЛЬКО JSON одной строкой:
{"verdict": "OK"|"BAD", "issues": [<anglicism|grammar|structure>],
 "severity": 0-5, "comment": "одна фраза"}
```

**Размер:** ~600 chars вместо 8000 (−92%).

### Цена (на 287K карточек full mw_ru)

Yandex Pro: sync ₽0.80/1K tokens, async ₽0.40/1K (см. [docs/yandex_api.md](../yandex_api.md)).
Output на QA — ~30 tok per call (короткий verdict JSON).

| | Full prompt (2700 tok) | Slim prompt (200 tok) |
|---|---|---|
| Total input on 287K | 774M tok | 57M tok |
| **Sync** input cost (₽0.80/1K) | ₽619K ≈ **$7 030** | ₽46K ≈ **$520** |
| **Async** input cost (₽0.40/1K) | ₽310K ≈ **$3 520** | ₽23K ≈ **$260** |
| + output (8.6M tok) sync/async | $77 / $39 | $77 / $39 |
| **Total sync** | **~$7 100** | **~$600** |
| **Total async** | **~$3 560** | **~$300** |

**Экономия от full → slim:** ~92% независимо от sync/async режима.

С pre-filter (−25% карточек):
- Slim async + pre-filter: **~$225** на 287K (полное покрытие mw_ru
  через Yandex)

### Когда использовать

- **Полный mw_ru через Yandex** (если решим делать) — берём slim+async (~$225-300)
- **Pilot/проверка** — берём full sync (там цена не критична, нужно
  полное покрытие категорий)

---

## 4. Pre-filter тривиально-OK

### Идея

Многие карточки **очевидно OK** без LLM:
- Body length ≤ 30 символов («шов, <ls>L.</ls>»)
- В EN body нет: `of`, `from`, `with`, `mentioned in`, многозначных слов
- Только простой `<s>X</s> <lex>m.</lex> word, <ls>Src.</ls>` паттерн

Их можно вообще не отправлять в QA. Снизит нагрузку на ~25%.

### Эвристика — по длине открытого английского текста после strip тегов

Стрипаем opaque-теги перед оценкой. Реальная тривиальная карточка —
`<body>a seam, <ls>L.</ls><info lex="inh" /></body>` — там открытого
английского ≤15 символов после удаления тегов.

```python
import re

STRIP_TAGS_RE = re.compile(r'<(s|s1|ab|ls|lex|info|hom|pb|srs|bot)[^>]*?(/>|>.*?</\1>)',
                           re.DOTALL)

def open_text_length(body: str) -> int:
    """Длина открытого английского текста после удаления opaque-тегов."""
    return len(STRIP_TAGS_RE.sub('', body).strip())

def is_trivially_ok(en_body: str, ru_body: str) -> bool:
    """Карточка тривиально-OK если:
       - открытый английский текст ≤15 символов (типа «a seam,», «frightened,»);
       - после strip тегов EN и RU имеют похожую длину (нет truncation).
    """
    en_open = open_text_length(en_body)
    if en_open > 15:
        return False
    ru_open = open_text_length(ru_body)
    # Sanity-check: RU не сильно отличается от EN после strip
    # (поверхностная проверка против hallucination/severe truncation)
    if abs(en_open - ru_open) > 10:
        return False
    return True
```

**Что НЕ делать:**

- ❌ `levenshtein_ratio(en, ru) > 0.85` — cyrillic vs latin даёт почти
  максимальную edit distance даже при эквивалентном переводе. Эта
  эвристика **никогда не сработает буквально** или ловит совсем другой
  класс (RU = копия EN — это severe BAD, а не trivially-OK).

- ❌ `not re.search(r'\b(of|from|with)\b', en)` — `of` встречается в
  большинстве MW-статей. Pre-filter будет ловить почти ничего.

- ❌ Эвристики на ключевые слова в EN — слишком хрупко, MW использует
  тысячи разных конструкций.

### Опционально: дополнительный flag для подозрительных

Если хочется поймать «RU = копия EN» (severe BAD класс) — это
**отдельный flag-for-review**, не pre-filter skip:

```python
def is_ru_copy_of_en(en_body: str, ru_body: str) -> bool:
    """RU полностью идентичен EN (Sonnet вернул вход вместо перевода)."""
    return en_body.strip() == ru_body.strip()
```

Такие карточки **не** skip-аем — отправляем в QA с пометкой
`prefilter_flag=ru_eq_en`, чтобы судья оценил отдельно.

### Скрипт

Новый `data/scripts/qa_prefilter.py`:

```bash
docker compose exec web python data/scripts/qa_prefilter.py \
    --input <full_lnum_list.json> \
    --output-pass <trivial_ok.json> \
    --output-fail <needs_qa.json>
```

Дальше `qa_pilot.py` и `qa_targeted.py` принимают только `needs_qa.json`.

### Эффект

| | Текущий | С pre-filter |
|---|---|---|
| Карточек в QA на full mw_ru | 287K | ~210K (−25%) |
| Стоимость Opus QA | ~$3 360 | ~$2 520 (**−$840**) |
| Стоимость Yandex slim | ~$510 | ~$380 (**−$130**) |

### Риск

Pre-filter может пропустить тонкий semantic-баг. Mitigation:
- На пилоте проверить 1000 «trivially-OK» через полный Opus → ожидаем
  <1% BAD (если больше — ослабить эвристики).
- Periodic resampling — 5% от pre-filter-pass всё равно гнать через QA
  как контроль.

---

## Итоговая экономия (full mw_ru QA сценарий)

| Стратегия | Цена | Покрытие |
|---|---|---|
| v3 Opus QA full 287K (текущий) | ~$3 360 | 100% полно |
| v4 Opus QA + pre-filter (−25%) | ~$2 520 | 100% (тривиальные = auto-OK) |
| v4 Yandex-slim async + pre-filter | **~$225** | 100% (anglicism/grammar/structure) |
| v4 Гибрид: Yandex-slim async для anglicism + Opus QA на ~30K «подозрительных» (sev≥3 от Yandex + не-тривиальные) | **~$800** | optimal coverage + cost |

**Гибрид v4** — самый расчётливый вариант: Yandex-slim делает первый
проход (находит anglicism/grammar дёшево), Opus делает целевой проход
по найденным sev≥3 + 5% контрольному сэмплу.

**Кардинальная экономия от v3 → v4 гибрид: ~76%** ($3 360 → $800), без
потери качества (Opus всё равно проверяет semantic/anchors).

---

## История

| Дата | Версия | Что |
|---|---|---|
| 2026-05-17 | v1 | Базовый QA-судья |
| 2026-05-18 | v2 | + правило про `<ab>` теги |
| 2026-05-18 | v3 | Перебалансировка калибровки, sev=3 semantic, BAD_with_ab_kept |
| 2026-05-18 | v4 (draft) | `tag_dropped` категория, Stage-D-style OK, Yandex-slim, pre-filter |
