#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""build_h1306_style_sheet.py — H1306 style-rules ratification sheet (remake).

Phase 1 (21-07-2026, H1306) emitted a local-only sheet from an uncommitted
one-shot generator: unstamped, no H1404 lock, no font_scale, and
``mark_cyrillic`` wrapped every Russian word (464 yellow marks on 9 cards of
pure-Russian prose — unreadable). Zero votes cast, so supersession-by-remake
is legal (H1655 batch1v2 precedent).

This committed generator rebuilds the same 9 cards (A1–C3) from the research
memo content, on the current emitter + binding standard:

  * csl-pyutil ``render_review_sheet`` (font_scale default 1.5)
  * ``review_sheet_standard.standard_config`` (show_ids, note height, save_as)
  * ``review_binding.stamp`` + lock (H1404)

No blanket ``mark_cyrillic`` on prose — only intentional short RU tokens
where a proposed form is the decision subject (none on this sheet: the cards
are policy options, not RU gloss proposals).

Usage (from RussianTranslation/):
    python src/build_h1306_style_sheet.py

Deliberate re-cut after inputs move:
    set REVIEW_LOCK_FORCE=1
    python src/build_h1306_style_sheet.py
"""
from __future__ import annotations

import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from csl_pyutil.review_sheet import render_review_sheet, esc  # noqa: E402
import review_binding  # noqa: E402
from review_sheet_standard import standard_config  # noqa: E402

GENERATED = "2026-07-31"
SHEET_ID = "h1306_style"
MEMO_HREF = (
    "https://github.com/gasyoun/SanskritLexicography/blob/master/"
    "RussianTranslation/pwg_ru/STYLE_RESEARCH_DOUBLETS_VL_COMP.md"
)
SAVE_AS = "pwg_ru/eval/h1306_style.decisions.json"


def _q(html: str) -> str:
    """Question body — no mark_cyrillic (this sheet is all-RU policy prose)."""
    return html


def _card(cid, filt, title, badges, question, panels, note_ph=None):
    return {
        "id": cid,
        "filt": filt,
        "title": title,
        "title_href": MEMO_HREF,
        "badges": badges,
        "question": _q(question),
        "panels": panels,
        "note_placeholder": note_ph or "Комментарий / поправка к формулировке правила…",
    }


# Card bodies preserved from the 21-07 Phase-1 sheet / STYLE_RESEARCH memo §2–4.
# Wording is the ratified research product; only presentation is remade.

_LIT_DOUBLETS = (
    "<ul>"
    "<li>Апресян 1995, с. 218: точные синонимы = толкования совпадают полностью; "
    "квазисинонимы — лишь большая общая часть; словарь обязан их <b>различать</b> "
    "при фиксации.</li>"
    "<li>Берков 2004, с. 149–153: болезнь «синонимит» — нанизывание неразличённых "
    "синонимов размывает границы значения; но «не обкрадывай… будь расчетливо "
    "щедр» (заповедь 3); семантизатор при первом эквиваленте легален (с. 152).</li>"
    "<li>Щерба 1940 (этюд I, VI): переводные эквиваленты — лишь приблизительные "
    "подсказки; лечит семантизация, не количество.</li>"
    "</ul>"
)

_EX_DOUBLETS = (
    "<p><b>Примеры из реестра (публичные):</b></p>"
    "<ul>"
    "<li>N17 (reject): DE <code>{%hervorragen%}</code> → RU «выступать, возвышаться "
    "над окружающим»; KATHĀS. 26,9 у Серебрякова: волны «будто горы, сохранившие "
    "крылья» → арбитр поддерживает ОДНО «возвышаться» (уже внесено ремонтом H1302).</li>"
    "<li>N20: «почти везде вместо одного немецкого слова по два русских… Что об "
    "этом говорит Апресян?»</li>"
    "<li>Замер: 421 дублетная пара = 18,5% односложных DE-глосс; 411 карточек "
    "(3,5% стора).</li>"
    "</ul>"
)

_VL_PANEL = (
    "<p>Стор: 252 карточки с <code>v. l.</code>; 250 — внутри тега <code>ab</code> "
    "(хранится нетронутым по архитектуре ABBREVIATIONS_RU), 2 — голой прозой. "
    "Промпт-строка <code>v. l.</code> → «разночтение» фактически мертва (исполнена "
    "в 0 карточках из 252). Корпусный масштаб: 7 879 вхождений "
    "(pwg 4 976 + pw 2 732 + pwkvn 171).</p>"
    "<p><b>Прецедент:</b> Дворецкий, Латинско-русский словарь, «Условные "
    "сокращения. Латинские» (дословно): <code>v. l.— varia lectio — разночтение "
    "или орфографический вариант</code> — латиницей в статьях, глосса один раз "
    "в списке сокращений. Лихачёв 2001: русский термин — «разночтение» "
    "(глава об основных разрядах разночтений).</p>"
)

_COMP_PANEL = (
    "<p>N10 (MG): «в Comp. в препозиции — по-русски звучит громоздко… Подобная "
    "оговорка же встречается десятки тысяч раз?» Замер: реально ~2,1 тыс. "
    "корпусно (pw 2 071 + pwkvn 34; PWG выражает то же как «an der Spitze eines "
    "Comp.», 43); в сторе 102 карточки. Значение: слово стоит первым членом "
    "сложного слова.</p>"
    "<p>Русская традиция: Кочергина (оцифровка) — «первый элемент» сложного "
    "слова; грамматическая традиция — «первый член сложного слова».</p>"
)


def items():
    return [
        # ---- Q1 doublets ----
        _card(
            "h1306-A1",
            "doublets",
            "A1 — дублет только дискриминированный или как семантизатор (рекомендуется)",
            ["Q1 дублеты", "рекомендуется"],
            "<p><b>Последствие выбора:</b> <b>дефолт</b> — <b>ОДИН</b> основной "
            "эквивалент на односложную немецкую глоссу; второй член разрешён только "
            "(i) как семантизатор-уточнитель по Беркову или (ii) с зафиксированным "
            "различием в поле <code>differentia</code>; недискриминированный дублет "
            "становится дефектом гейта; при наличии опубликованного русского "
            "перевода цитаты аттестованный эквивалент решает (правило N17). Правка "
            "в промпты 1_perevod/3_pereperevod + гейт-правило; развертка по стору — "
            "по плану фазы 2 (порядка сотен карточек из 411 затронутых).</p>"
            "<p>Соответствует Апресяну (дискриминация квазисинонимов), Беркову "
            "(запрет синонимита при «расчетливой щедрости») и механизму арбитра.</p>",
            [("Примеры", _EX_DOUBLETS), ("Литература", _LIT_DOUBLETS)],
        ),
        _card(
            "h1306-A2",
            "doublets",
            "A2 — жёстко один эквивалент всегда",
            ["Q1 дублеты"],
            "<p><b>Последствие выбора:</b> все 421 дублетные пары сводятся к одному "
            "эквиваленту; поле <code>differentia</code> и семантизаторы "
            "игнорируются; гейт проще, но теряется легальная берковская "
            "семантизация — часть карточек обеднеет против печатного PWG.</p>"
            "<p><b>Против:</b> заповедь 3 Беркова («не обкрадывай пользователя»); "
            "Апресян требует различения, а не удаления квазисинонимов.</p>",
            [("Литература", _LIT_DOUBLETS)],
            "Комментарий…",
        ),
        _card(
            "h1306-A3",
            "doublets",
            "A3 — статус-кво: свободные дублеты",
            ["Q1 дублеты"],
            "<p><b>Последствие выбора:</b> ничего не меняется: 18,5% односложных "
            "глосс продолжают получать пары без указания различий; возражения "
            "N17/N18/N20 остаются неотвеченными; гейт не получает правила.</p>"
            "<p>Отвергается всеми тремя авторитетами (синонимит по Беркову; "
            "недискриминированные квазисинонимы по Апресяну; иллюзия точности "
            "по Щербе).</p>",
            [("Литература", _LIT_DOUBLETS)],
            "Комментарий…",
        ),
        # ---- Q2 v. l. ----
        _card(
            "h1306-B1",
            "vl",
            "B1 — v. l. остаётся латиницей, RU-тултип «разночтение» (рекомендуется)",
            ["Q2 v. l.", "рекомендуется"],
            "<p><b>Последствие выбора:</b> ноль правок стора; RU-рендер показывает "
            "тултип «разночтение» (Bucket B); промпт-строка сужается до 2 карточек "
            "голой прозы; токен <code>v. l.</code> передаётся в единый список H1303 "
            "— финальное токенное решение живёт там, без форка.</p>"
            "<p>Прецедент Дворецкого и кёльнская конвенция; полное соответствие "
            "render-time архитектуре.</p>",
            [("Данные и прецеденты", _VL_PANEL)],
            "Комментарий…",
        ),
        _card(
            "h1306-B2",
            "vl",
            "B2 — видимое RU «разночт.» через RU_MAP",
            ["Q2 v. l."],
            "<p><b>Последствие выбора:</b> <code>v. l.</code> переезжает в Bucket A "
            "(RU_MAP): видимый RU-текст «разночт.» на всех поверхностях; стор не "
            "трогается, но RU-поверхность расходится с Дворецким/Кёльном; вводится "
            "нестандартное сокращение (устойчивого «разночт.» в русской традиции "
            "нет).</p>"
            "<p>Русифицирует поверхность ценой разрыва со словарным прецедентом.</p>",
            [("Данные и прецеденты", _VL_PANEL)],
            "Комментарий…",
        ),
        _card(
            "h1306-B3",
            "vl",
            "B3 — полное «разночтение» в прозе (нынешняя промпт-строка)",
            ["Q2 v. l."],
            "<p><b>Последствие выбора:</b> исполнение нынешней промпт-строки "
            "повлечёт правку RU-поля 252 карточек стора (и далее ~7,9 тыс. "
            "корпусно) + самое длинное слово из вариантов; против render-time "
            "архитектуры ABBREVIATIONS_RU и против прецедента Дворецкого.</p>"
            "<p>Единственный аргумент за — максимальная читаемость без тултипов "
            "(печать/экспорт без hover).</p>",
            [("Данные и прецеденты", _VL_PANEL)],
            "Комментарий…",
        ),
        # ---- Q3 Comp. ----
        _card(
            "h1306-C1",
            "comp",
            "C1 — помета «в нач. сложн. слов» (рекомендуется)",
            ["Q3 Comp.", "рекомендуется"],
            "<p><b>Последствие выбора:</b> видимый RU-текст формулы становится "
            "«в нач. сложн. слов»; полная форма в тултипе: «в начале сложных слов "
            "(первым членом сложного слова)»; правка промптов + развертка на 102 "
            "карточки стора (план фазы 2); DE-поле и тег <code>ab</code> не "
            "трогаются.</p>"
            "<p>Терсеный стиль H1305 («вм.», «в знач.»), без латинского токена, "
            "читается без подготовки.</p>",
            [("Данные", _COMP_PANEL)],
            "Комментарий / своя формула…",
        ),
        _card(
            "h1306-C2",
            "comp",
            "C2 — «первым членом сложн. слова»",
            ["Q3 Comp."],
            "<p><b>Последствие выбора:</b> точная грамматическая формула в видимом "
            "тексте; длиннее C1 примерно вдвое на каждом из ~2,1 тыс. будущих "
            "вхождений; лучше годится тултипом к C1, чем строчной пометой.</p>"
            "<p>Выбор C2 означает: точность важнее краткости на высокочастотной "
            "помете.</p>",
            [("Данные", _COMP_PANEL)],
            "Комментарий…",
        ),
        _card(
            "h1306-C3",
            "comp",
            "C3 — голый токен Comp. с тултипом (аналог B1)",
            ["Q3 Comp."],
            "<p><b>Последствие выбора:</b> видимый RU-текст оставляет "
            "<code>&lt;ab&gt;Comp.&lt;/ab&gt;</code> с тултипом-объяснением; минимум "
            "правок, но жалоба N10 на нечитаемость «в Comp. в препозиции» не "
            "закрывается — читатель без латинской подготовки формулу не поймёт.</p>"
            "<p>Последовательно с B1, но именно здесь MG просил лёгкую РУССКУЮ "
            "конструкцию.</p>",
            [("Данные", _COMP_PANEL)],
            "Комментарий…",
        ),
    ]


def build(out_dir=None, force_lock=False):
    cards = items()
    assert len(cards) == 9, len(cards)
    cfg = {
        "sheet_id": SHEET_ID,
        "title": "H1306 — ратификация стилевых правил pwg_ru (дублеты · v. l. · Comp.-формула)",
        "subtitle": (
            "Remake 31-07-2026 (H1404 stamp+lock, font_scale, без blanket mark_cyrillic). "
            "9 карточек-вариантов по 3 вопросам (A/B/C). Approve ровно ОДНОГО варианта "
            "на вопрос достаточно; отвергать остальные не обязательно, но можно. "
            "Комментарий = поправка к формулировке. Основание: memo "
            "STYLE_RESEARCH_DOUBLETS_VL_COMP.md (реестр H178, строки N10/N13/N17/N18/N20). "
            "Эмиттер: csl-pyutil + review_binding."
        ),
        "footer": (
            "Approve = принять вариант как правило (промпты + план развертки фазы 2). "
            "Reject = вариант исключить. Defer = решить позже. "
            "Экспорт: pwg_ru/eval/h1306_style.decisions.json → H1306 Phase 2 / H1627."
        ),
        "approve_label": "Принять правило",
        "reject_label": "Отвергнуть",
        "filters": [
            ("doublets", "Q1 дублеты"),
            ("vl", "Q2 v. l."),
            ("comp", "Q3 Comp."),
        ],
        "generated": GENERATED,
    }
    cfg.update(standard_config(save_as=SAVE_AS))

    html_doc = render_review_sheet(cards, cfg)
    # Drop unused import warning: esc is available for future panel builders.
    _ = esc

    out_dir = out_dir or os.path.join(RT, "review")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "h1306_style_sheet.html")
    stamped, chash = review_binding.stamp(html_doc)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(stamped)

    if force_lock:
        os.environ["REVIEW_LOCK_FORCE"] = "1"
    lock_path = review_binding.lock_from_html(out, gate=None)

    print("H1306 style sheet: %d cards -> %s" % (len(cards), out))
    print("  %s" % chash)
    print("  lock -> %s" % lock_path)
    return out, chash, lock_path


if __name__ == "__main__":
    force = os.environ.get("REVIEW_LOCK_FORCE") == "1" or "--force" in sys.argv
    build(force_lock=force)
