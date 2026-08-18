#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""build_h2805_q3_deploy_sheet.py — H2805 Q3 graphic-notation DEPLOYMENT sheet.

MG's 15-08-2026 vote on `h1306_style` rejected all three word-based options
(C1/C2/C3) for the «im Comp., vorangehend» formula and ruled a fourth form the
sheet never offered: a GRAPHIC ring mark in Kochergina's manner (ring+hyphen =
initial member, hyphen+ring = final member). Those five rejected cards are NOT
re-asked here (decisions_applied_15-08-2026_h1306-style.md §4). This sheet asks
only the open deployment questions of guide §6.3:

  D — application layer (render vs card-base rewrite)
  G — codepoint of the ring (˚ U+02DA / ° U+00B0 / ॰ U+0970)
  T — tooltip behaviour

Evidence: pwg_ru/H2805_Q3_COMP_GRAPHIC_FONT_RENDER_PROOF_2026-08-15.md
(font cmap census over 324 installed families + Pillow raster proof).
§5.4 sheet-authoring rules honoured: 5-10 real examples per rule, explicit
denominators, no «стор» in human-facing prose, citations not repeated 1:1.

Usage (from RussianTranslation/):
    python src/build_h2805_q3_deploy_sheet.py
Deliberate re-cut after inputs move:
    set REVIEW_LOCK_FORCE=1 && python src/build_h2805_q3_deploy_sheet.py
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
from sheet_screening import screening_block  # noqa: E402
from csl_pyutil import RU_UI_STRINGS, anatomy  # noqa: E402

GENERATED = "2026-08-15"
SHEET_ID = "h2805_q3_deploy"
PROOF_HREF = (
    "https://github.com/gasyoun/SanskritLexicography/blob/master/"
    "RussianTranslation/pwg_ru/H2805_Q3_COMP_GRAPHIC_FONT_RENDER_PROOF_2026-08-15.md"
)
SAVE_AS = "pwg_ru/eval/h2805_q3_deploy.decisions.json"

# 8 real cards of the 102 (out of 11 603 rows of the card base) whose DE carries
# `im <ab>Comp.</ab> vorangehend`; RU today keeps the Latin token in 102/102.
_EX_ROWS = [
    ("Bid 12 (bhid)",
     "отличный, — от (<ab>Abl.</ab> или в <ab>Comp.</ab> предшествующем)",
     "отличный, — от (<ab>Abl.</ab> или {R}-)"),
    ("Bid 13 (bhid)",
     "смешанный, соединенный с (<ab>Instr.</ab> или в <ab>Comp.</ab> предшествующем)",
     "смешанный, соединенный с (<ab>Instr.</ab> или {R}-)"),
    ("Cid ava 2 (chid)",
     "ограниченный —, замкнутый (предшествующим в <ab>Comp.</ab>)",
     "ограниченный —, замкнутый ({R}-)"),
    ("DA 2b (dhā)",
     "покрытый, — чем-либо (в <ab>Comp.</ab> предшествующем)",
     "покрытый, — чем-либо ({R}-)"),
    ("DA 2c (dhā)",
     "скрытый, — в (<ab>Loc.</ab> или в <ab>Comp.</ab> предшествующем)",
     "скрытый, — в (<ab>Loc.</ab> или {R}-)"),
    ("DA 3 (dhā, {#˚hita#})",
     "разлученный, разделенный, — посредством (в <ab>Comp.</ab> предшествующем)",
     "разлученный, разделенный, — посредством ({R}-)"),
    ("DA samā 7 (dhā)",
     "соединенный —, связанный —, снабженный (<ab>Instr.</ab> или в <ab>Comp.</ab> предшествующем)",
     "соединенный —, связанный —, снабженный (<ab>Instr.</ab> или {R}-)"),
    ("DA 2b′ (dhā)",
     "снабженный, наделенный (в <ab>Comp.</ab> предшествующем)",
     "снабженный, наделенный ({R}-)"),
]


def _examples_panel(ring, legend=False):
    rows = []
    plain = ring.replace("<b>", "").replace("</b>", "")
    for key, before, after in _EX_ROWS:
        rows.append(
            "<tr><td><code>%s</code></td><td>%s</td><td>%s</td></tr>"
            % (key,
               anatomy.highlight(before),
               anatomy.highlight(after.replace("{R}", plain)))
        )
    return ((anatomy.legend_html() if legend else "") +
        "<p>8 из 102 реальных карточек (знаменатель: 102 карточки базы карточек "
        "из 11 603 строк несут формулу <code>im &lt;ab&gt;Comp.&lt;/ab&gt; "
        "vorangehend</code>; RU сегодня держит латинский токен в 102/102; "
        "«в препозиции» — 2/102). Корпусный знаменатель будущей развёртки: "
        "~2,1 тыс. вхождений формулы малого PW в разметке <code>ab</code> "
        "(pw 2 071 + pwkvn 34).</p>"
        "<table><tr><th>Карточка</th><th>Сейчас</th><th>После</th></tr>"
        + "".join(rows) + "</table>"
    )


_FONT_PANEL = (
    "<p>Перепись cmap 324 установленных семейств + растровая проба файлов "
    "шрифтов (Pillow), 15-08-2026 — <a href='%s'>полный отчёт</a>:</p>"
    "<table>"
    "<tr><th>Знак</th><th>Шрифтов</th><th>Стек веб-карточки</th><th>Растровая проба</th></tr>"
    "<tr><td>˚ U+02DA</td><td>271/324</td><td>Segoe UI ✅ Roboto ✅</td>"
    "<td>однородная строка во всех потребителях</td></tr>"
    "<tr><td>° U+00B0</td><td>315/324</td><td>Segoe UI ✅ Roboto ✅</td>"
    "<td>однородная строка во всех потребителях</td></tr>"
    "<tr><td>॰ U+0970</td><td>21/324</td><td>Segoe UI ❌ (тофу) — спасает только "
    "per-glyph fallback браузера (Nirmala UI, в которой нет кириллицы)</td>"
    "<td>тофу в Segoe UI, Times New Roman, Consolas; SIL-шрифты MDF-потребителей "
    "деванагари не покрывают</td></tr>"
    "</table>"
    "<p>Живая проба на ЭТОМ экране (то, что вы видите прямо сейчас): "
    "<b>॰-</b> · <b>-॰</b> | <b>˚-</b> · <b>-˚</b> | <b>°-</b> · <b>-°</b> — "
    "если первый кружок отличается по посадке/весу от двух других или показан "
    "прямоугольником, это и есть эффект fallback.</p>" % PROOF_HREF
)


def _card(cid, filt, title, badges, question, panels, note_ph=None):
    return {
        "id": cid,
        "filt": filt,
        "title": title,
        "title_href": PROOF_HREF,
        "badges": badges,
        "question": question,
        "panels": panels,
        "note_placeholder": note_ph or "Комментарий / поправка…",
    }


def items():
    return [
        # ---- D: layer ----
        _card(
            "h2805-D1", "layer",
            "D1 — развёртка на РЕНДЕРЕ: база карточек не трогается (рекомендуется)",
            ["Слой", "рекомендуется"],
            "<p><b>Принять</b> = видимый RU-текст формулы заменяется кружком на "
            "рендере (<code>build_article_site.py</code>, по образцу RU_MAP): "
            "паттерн «в <code>&lt;ab&gt;Comp.&lt;/ab&gt;</code> предшествующем» → "
            "«кружок-дефис» с тултипом; DE-поле, тег <code>ab</code> и все "
            "<code>{%…%}</code>-якоря остаются байт-в-байт нетронутыми; покрываются "
            "сразу все 102 карточки базы и ~2,1 тыс. будущих корпусных вхождений "
            "без репроцессинга. <b>Отвергнуть</b> = слой рендера исключён, остаётся "
            "правка базы карточек (D2).</p>"
            "<p>Соответствует архитектуре §3.1 свода (решение MG 10-07-2026: перевод "
            "помет живёт на рендере) и прецеденту B1 по <code>v. l.</code>.</p>",
            [("Примеры (глиф-плейсхолдер ˚)",
              _examples_panel("<b>˚</b>", legend=True))],
        ),
        _card(
            "h2805-D2", "layer",
            "D2 — правка БАЗЫ КАРТОЧЕК: кружок вписывается в RU-текст",
            ["Слой"],
            "<p><b>Принять</b> = RU-поле 102 карточек переписывается (реочередь с "
            "гейтом и отчётом), кружок оказывается в самой базе; экспорты (MDF) и "
            "любые будущие потребители видят его без логики рендера. "
            "<b>Отвергнуть</b> = база карточек не трогается.</p>"
            "<p>Цена: против архитектуры §3.1; правка текста рядом с "
            "<code>{%…%}</code>-якорями требует пословного гейта (класс риска, "
            "закрытый в H1651/H1702 только для необёрнутых глосс); каждое будущее "
            "корпусное вхождение требует той же правки снова — правило живёт в "
            "данных, а не в коде.</p>",
            [("Примеры (глиф-плейсхолдер ˚)", _examples_panel("<b>˚</b>"))],
        ),
        # ---- G: glyph ----
        _card(
            "h2805-G1", "glyph",
            "G1 — кружок ˚ (U+02DA), знак самой базы карточек (рекомендуется)",
            ["Глиф", "рекомендуется"],
            "<p><b>Принять</b> = помета набирается знаком <b>˚</b> (U+02DA RING "
            "ABOVE): <b>˚-</b> = в начале сложных слов, <b>-˚</b> = в конце. Это "
            "ТОТ ЖЕ кружок, которым PWG-оцифровка уже помечает усечённый член в "
            "санскритских сегментах этих же карточек (<code>{#˚hita#}</code>, "
            "<code>{#˚DIyatAm#}</code>): один знак = одно значение «член сложного "
            "слова опущен здесь» в санскритском И русском тексте. "
            "<b>Отвергнуть</b> = знак ˚ исключён.</p>",
            [("Шрифтовые факты", _FONT_PANEL),
             ("Примеры с ˚", _examples_panel("<b>˚</b>"))],
        ),
        _card(
            "h2805-G2", "glyph",
            "G2 — кружок ° (U+00B0, знак градуса)",
            ["Глиф"],
            "<p><b>Принять</b> = помета набирается знаком <b>°</b> (U+00B0): "
            "<b>°-</b> / <b>-°</b>. Максимальное покрытие (315/324 шрифтов), "
            "визуально в мелком кегле неотличим от ˚; именно так кружок набирают "
            "оцифровки MW. <b>Отвергнуть</b> = знак ° исключён.</p>"
            "<p>Минус: у знака есть собственное значение «градус»; поиск по "
            "тексту будет цеплять температуры/углы в цитатах (в базе карточек "
            "таких почти нет — риск малый, но ненулевой).</p>",
            [("Примеры с °", _examples_panel("<b>°</b>"))],
        ),
        _card(
            "h2805-G3", "glyph",
            "G3 — деванагарский знак сокращения ॰ (U+0970)",
            ["Глиф"],
            "<p><b>Принять</b> = помета набирается родным деванагарским знаком "
            "<b>॰</b> (U+0970): <b>॰-</b> / <b>-॰</b> — семантически «правильный» "
            "знак сокращения деванагари, сидит у базовой линии. "
            "<b>Отвергнуть</b> = знак ॰ исключён.</p>"
            "<p>Измеренная цена: ни один шрифт стека веб-карточки его не несёт "
            "(21/324 шрифтов машины); в браузере строка всегда двухшрифтовая "
            "(кириллица из Segoe UI, кружок из Nirmala UI), в одношрифтовых "
            "потребителях (MDF-просмотрщики на SIL-шрифтах, одношрифтовый PDF) — "
            "тофу. Подробности — в шрифтовой панели G1.</p>",
            [("Примеры с ॰", _examples_panel("<b>॰</b>"))],
        ),
        # ---- T: tooltip ----
        _card(
            "h2805-T1", "tooltip",
            "T1 — тултип с полной формулой (рекомендуется)",
            ["Тултип", "рекомендуется"],
            "<p><b>Принять</b> = кружок-помета получает тултип: для начальной "
            "позиции «в начале сложных слов (первым членом сложного слова)», для "
            "конечной «в конце сложных слов (последним членом сложного слова)» — "
            "тем же механизмом <code>title=</code>, которым уже снабжены "
            "<code>ab</code>-пометы и <code>ls</code>-сиглы. <b>Отвергнуть</b> = "
            "тултипа нет (T2).</p>"
            "<p>Печать/PDF тултипов не показывают — расшифровка дублируется в "
            "списке условных обозначений фронт-материала (как у Кочергиной и в "
            "списке сокращений Дворецкого — расшифровка один раз, не в статьях).</p>",
            [("Примеры", _examples_panel("<b>˚</b>"))],
        ),
        _card(
            "h2805-T2", "tooltip",
            "T2 — голый кружок без тултипа",
            ["Тултип"],
            "<p><b>Принять</b> = помета остаётся без тултипа; расшифровка — "
            "только в списке условных обозначений. Чище типографически, но "
            "читатель веб-карточки, не заглянувший во фронт-материал, значения "
            "не узнает. <b>Отвергнуть</b> = тултип обязателен (T1).</p>",
            [("Примеры", _examples_panel("<b>˚</b>"))],
        ),
    ]


def build(out_dir=None, force_lock=False):
    cards = items()
    assert len(cards) == 7, len(cards)
    cfg = {
        "sheet_id": SHEET_ID,
        "title": "H2805 — развёртка графической пометы позиции в сложном слове (˚- / -˚)",
        "subtitle": (
            "Голос MG 15-08-2026 уже постановил ФОРМУ (кружок по Кочергиной, а не "
            "слова) — форма здесь не переголосуется, и отвергнутые C1/C2/C3 не "
            "переспрашиваются. Три вопроса развёртки: Слой (D) · Глиф (G) · Тултип "
            "(T). Approve ровно ОДНОГО варианта в каждой группе достаточно. "
            "Основание: font/render-отчёт H2805 + guide §6.3."
        ),
        "footer": (
            "«Принять» = принять вариант развёртки. «Отвергнуть» = исключить. "
            "«Отложить» = решить позже. Экспорт: "
            "<code>pwg_ru/eval/h2805_q3_deploy.decisions.json</code> → "
            "применяющий проход закрывает §6.3 свода."
        ),
        "approve_label": "Принять",
        "reject_label": "Отвергнуть",
        "filters": [
            ("layer", "D слой"),
            ("glyph", "G глиф"),
            ("tooltip", "T тултип"),
        ],
        "generated": GENERATED,
        # H3103: U6 Russian-only chrome. RU_UI_STRINGS covers everything
        # except save_banner (its default bakes in this sheet's own
        # sheet_id/save_as, so a fixed preset string would drop them).
        "ui_strings": dict(RU_UI_STRINGS, save_banner=(
            '&#128229; Ваш экспорт скачивается как <code>%s_decisions.json</code> '
            '&rarr; сохраните его в <code>%s</code> (значение <code>sheet_id</code> '
            'внутри файла — <code>%s</code> — так следующая сессия узнаёт, к какому '
            'листу относятся эти решения).'
            % (esc(SHEET_ID), esc(SAVE_AS), esc(SHEET_ID)))),
    }
    cfg.update(standard_config(save_as=SAVE_AS))

    sc = screening_block(
        deterministic=0,
        lookup=0,
        agent=0,
        human=len(cards),
        evidence_path=(
            "RussianTranslation/pwg_ru/"
            "H2805_Q3_COMP_GRAPHIC_FONT_RENDER_PROOF_2026-08-15.md"
        ),
        rules=["font_cmap_census_324_families", "pillow_raster_proof",
               "store_formula_census_102_of_11603"],
    )
    html_doc = render_review_sheet(cards, cfg, extras=True, screening=sc)
    _ = esc

    out_dir = out_dir or os.path.join(RT, "review")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "h2805_q3_deploy_sheet.html")
    stamped, chash = review_binding.stamp(html_doc)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(stamped)

    if force_lock:
        os.environ["REVIEW_LOCK_FORCE"] = "1"
    lock_path = review_binding.lock_from_html(out, gate=None)

    print("H2805 Q3 deploy sheet: %d cards -> %s" % (len(cards), out))
    print("  %s" % chash)
    print("  lock -> %s" % lock_path)
    return out, chash, lock_path


if __name__ == "__main__":
    force = os.environ.get("REVIEW_LOCK_FORCE") == "1" or "--force" in sys.argv
    build(force_lock=force)
