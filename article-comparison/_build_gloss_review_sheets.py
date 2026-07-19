"""Generate the four gloss-review HTML voting sheets (H739).

Reads gloss_review_items.json (same directory) and renders one interactive
voting sheet per finalist word (agni, aksara, ananta, anya) via the shared
csl_pyutil.render_review_sheet emitter into the gitignored <repo-root>/review/
folder:

    review/sanskritlexicography-article-comparison_<word>_review.html

Votes export as sanskritlexicography-article-comparison_<word>_decisions.json
(drop into review/ — the Uprava review_decisions_watcher picks it up); accepted
rows are applied to article-comparison/<word>.pd-min.ru.md col. 3 via
/decisions-apply, then re-run RussianTranslation/src/_build_skeletons_ru.py
where the gloss feeds a generated view.

Usage:  python article-comparison/_build_gloss_review_sheets.py
Needs:  pip install "csl-pyutil @ https://github.com/sanskrit-lexicon/csl-pyutil/archive/refs/tags/v0.3.0.zip"
"""

import html
import json
import sys
from pathlib import Path

from csl_pyutil import mark_cyrillic, render_review_sheet

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent / "review"

sys.path.append(str(HERE.parent / "RussianTranslation" / "src"))
from review_sheet_standard import standard_config  # noqa: E402

# V4 — the published per-word article page (the exact file the accepted votes
# edit; publicly linked from article-comparison/README.md).
ARTICLE_URL = "https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/{}"

SEV_LABEL = {
    "H": "H — фактическая ошибка",
    "M": "M — норма/точность",
    "L": "L — полировка/добавка",
}
SECTION_LABEL = {"A": "замена", "B": "добавка"}


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def build_question(it: dict) -> str:
    current_label = "Сейчас" if it["section"] == "A" else "Сейчас (ячейка)"
    proposed_label = "Предлагается" if it["section"] == "A" else "Предлагаемая добавка"
    return (
        f'<div style="margin:2px 0"><b>EN (PD):</b> <i>{esc(it["en"])}</i></div>'
        f'<div style="margin:2px 0"><b>{current_label}:</b> {mark_cyrillic(esc(it["current_ru"]))}</div>'
        f'<div style="margin:2px 0"><b>{proposed_label}:</b> '
        f'<b>{mark_cyrillic(esc(it["proposed_ru"]))}</b></div>'
        f'<div style="margin-top:6px"><b>Почему:</b> {it["why"]}</div>'
    )


def build_footer(word: str, w: dict) -> str:
    fyi_rows = "".join(
        f'<tr><td style="padding:2px 8px;vertical-align:top">{esc(f["sense"])}</td>'
        f'<td style="padding:2px 8px;vertical-align:top"><i>{esc(f["en"])}</i></td>'
        f'<td style="padding:2px 8px;vertical-align:top">{esc(f["ru"])}</td></tr>'
        for f in w["fyi"]
    )
    decisions_name = f"sanskritlexicography-article-comparison_{word}_decisions.json"
    return (
        '<div style="text-align:left;max-width:920px;margin:18px auto;font-size:13px">'
        "<h3>FYI — дефекты источника/экстракции (правка RU не требуется)</h3>"
        '<table style="border-collapse:collapse"><tr>'
        "<th>Сенс</th><th>English (PD), как напечатано</th><th>RU (уже корректно)</th></tr>"
        f"{fyi_rows}</table>"
        f'<h3>Покрытие</h3><p>{esc(w["coverage"])}</p>'
        f"<h3>Куда идут голоса</h3><p>Файл {decisions_name} сохранить в "
        "SanskritLexicography/review/ — watcher заведет handoff применения; "
        f'/decisions-apply вносит принятые правки в article-comparison/{w["source_file"]} '
        "(колонка «Русский»), затем при необходимости перегенерация зависимых видов "
        "(RussianTranslation/src/_build_skeletons_ru.py).</p></div>"
    )


def main() -> None:
    data = json.loads((HERE / "gloss_review_items.json").read_text(encoding="utf-8"))
    OUT_DIR.mkdir(exist_ok=True)
    for word, w in data["words"].items():
        items = [
            {
                "id": it["id"],
                "filt": it["sev"],
                "title": f'{it["sense"]} · {it["en"][:80]}',
                "title_href": ARTICLE_URL.format(w["source_file"]),
                "badges": [it["sev"], SECTION_LABEL[it["section"]]],
                "question": build_question(it),
                "panels": [],
                "note_placeholder": "Своя формулировка / частичная правка вместо отклонения…",
            }
            for it in w["items"]
        ]
        sheet_id = f"sanskritlexicography-article-comparison_{word}"
        config = {
            **standard_config(
                save_as=f"SanskritLexicography\\review\\{sheet_id}_decisions.json"
            ),
            "sheet_id": sheet_id,
            "title": f'Глосс-ревью {w["headword_display"]} — правки ручных RU-глосс',
            "subtitle": (
                f'{w["headline"]} Источник: article-comparison/{w["source_file"]} '
                f'({w["glosses_total"]} глосс). Данные: gloss_review_items.json (H739).'
            ),
            "footer": build_footer(word, w),
            "approve_label": "Принять правку",
            "reject_label": "Оставить как есть",
            "filters": [(k, SEV_LABEL[k]) for k in ("H", "M", "L")
                        if any(it["sev"] == k for it in w["items"])],
            "generated": data["_meta"]["date"],
        }
        out = OUT_DIR / f"{sheet_id}_review.html"
        out.write_text(render_review_sheet(items, config), encoding="utf-8")
        print(f"{out.name}: {len(items)} items, {out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
