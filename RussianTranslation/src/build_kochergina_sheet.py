#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_kochergina_sheet.py — generator for the Kochergina okas/okya/guda/sphic sheet.

Replaces the previously HAND-AUTHORED, generator-less artifact
``RussianTranslation/review/sanskritlexicography-kochergina-okas-guda-sphic_4rows_review.html``
(H779 Nagari-list 2013 re-verification, generated 12-07-2026 by Sonnet 5,
``claude-sonnet-5``). The 4 items below are a faithful transcription of that
file's inline ``const ITEMS`` array; the sheet_id and item ids are unchanged so
existing localStorage votes stay addressable.

Emits via the shared ``csl_pyutil.render_review_sheet`` (v0.3.0) on the
19-07-2026 review-sheet standard (V1-V8, see
``RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md`` section 2):
visible id chips (V3), taller note box (V6), Cyrillic highlight on the
gloss/proposed panels (V7), and the save-as banner (V8). No ``title_href`` —
the source data carries no entry URLs. No rating widget — this is an
approve/reject correction sheet, not a DA sheet, so the export keeps the
original ``{id, decision, note}`` schema.

MIGRATION: the old hand-authored page stored votes under localStorage key
``"reviewsheet:" + SHEET_ID`` (no hyphen); the emitter uses
``"review-sheet:" + SHEET_ID``. A migration snippet is spliced onto the
returned HTML (the h178_eval_bakeoff.py splice-on-returned-string pattern) —
but BEFORE the core ``<script>``, not before ``</body>``, because the core
IIFE reads the store at load time. When the new key is empty and the old key
exists, it copies old -> new; the old page's record schema
(``state[id] = {decision: "approve"|"reject"|"defer"|null, note: str}``)
maps 1:1 onto the emitter's, so the copy is field-faithful.

Regen (canonical invocation, from the repo root):

  python RussianTranslation/src/build_kochergina_sheet.py

Output: ``RussianTranslation/review/<sheet_id>_review.html`` (gitignored).
"""
import io
import json
import os
import sys

from csl_pyutil import esc, mark_cyrillic, render_review_sheet

from review_sheet_standard import standard_config

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REVIEW = os.path.join(ROOT, "review")

SHEET_ID = "sanskritlexicography-kochergina-okas-guda-sphic_4rows"
GENERATED = "19-07-2026"

FLAG_LABELS = {"change": "нужна правка", "noaction": "без изменений"}

# Faithful transcription of the inline `const ITEMS` array in the hand-authored
# sanskritlexicography-kochergina-okas-guda-sphic_4rows_review.html (12-07-2026).
ITEMS = [
    {
        "id": "okas",
        "title": "ओकस् okas (n.) — сомнительный смысл 3 «родина»",
        "flag": "change",
        "asis": "1) удовольствие 2) жилище-приют, убежище 3) родина",
        "proposed": "Снять/пометить смысл 3 «родина» как незасвидетельствованный. "
                    "Оставить: 1) удовольствие (первично, только RV) 2) жилище/приют/убежище "
                    "(вторично, Böhtlingk от √uc).",
        "evidence": [
            "MW s.v. okas — «house, dwelling, place of abiding, abode, home, refuge, asylum "
            "{RV. AV. MBh. BhP.}» — смысла «родина/отчизна» нет ни в одной цитате.",
            "Apte s.v. okas — «house, residence; asylum, refuge; resting place; pleasure, "
            "gratification» — тоже без «родины».",
            "Ни один локус RV не даёт смысла «родина/отчизна»; предположительно смысл взят из "
            "последнего (самого широкого) значения у Grassmann и там переусложнён.",
        ],
    },
    {
        "id": "okya",
        "title": "ओक्य okya (mfn./n.) — логически невозможный дериват «связанный с родиной»",
        "flag": "change",
        "asis": "1. 1) родной 2) связанный с родиной  2. n. см. ओकस् 3)",
        "proposed": "Заменить на «домашний, благоприятный для дома/обитателей»; снять «связанный "
                    "с родиной» (дериват не может нести смысл, которого нет у базы) и «родной» "
                    "(не подтверждается).",
        "evidence": [
            "MW s.v. okya — «fit for or belonging to a home {RV 9.86.45}».",
            "Apte s.v. okya — «(1) Favourable to the house, i.e. to its inmates (2) Good for a "
            "house, kind to a household».",
            "Все 8 вхождений в RV перепроверены напрямую в акцентуированном корпусе VedaWeb "
            "(Scarlata/Widmer/Lubotsky, "
            "VisualDCS/non-derived/vedaweb/accented_text_scarlata_widmer_lubotsky.json): "
            "1.91.13 svá okyè · 1.132.5 índra okyàṃ didhiṣanta dhītáyaḥ · 3.42.8 túbhyéd indra "
            "svá okyè · 8.25.17 ánu pū́rvāṇy okyā̀ · 8.49.3 ánv okyàṃ sáraḥ · 8.72.14 svám okyàṃ "
            "· 9.86.45 rāyá okyàḥ · 10.44.9 astv okyàṃ — везде «приютное/благоприятное место», "
            "нигде «родина».",
        ],
    },
    {
        "id": "guda",
        "title": "गुद guda / गुदा gudā — заявленный «гендерный дефект» ОПРОВЕРГНУТ",
        "flag": "noaction",
        "asis": "У Кочергиной УЖЕ ЕСТЬ два отдельных гнезда: guda m.pl. «1) кишечник 2) анат. "
                "задний проход» и gudā f.pl. «кишки» (проверено напрямую в Кочергина.no_tags, "
                "корпус SamudraManthanam).",
        "proposed": "БЕЗ ИЗМЕНЕНИЙ. Тезис ветки 2013 г. («у Кочергиной только m.pl., а в RV — "
                    "f.pl., это дефект») не подтверждается текущим текстом словаря — раздельное "
                    "f.-гнездо уже есть. Опционально — информационное примечание: масс. guda у "
                    "MW цитируется только из VS/TS/ShBr/Kauś (яджурведийская проза), НЕ из RV; "
                    "RV 10.163.3 даёт только женский род gudā.",
        "evidence": [
            "Кочергина.no_tags, строка 8155: «गुद /guda/ m. pl. 1) кишечник 2) анат. задний "
            "проход».",
            "Кочергина.no_tags, строка 8156 (сразу следом): «गुदा /gudā/ f. pl. кишки».",
            "MW s.v. guda — «m. an intestine, entrail, rectum, anus {VS. TS. ShBr. Kauś.} "
            "(ifc. f. ā)».",
            "RV 10.163.3 перепроверено напрямую в акцентуированном корпусе VedaWeb: «āntrébhyas "
            "te gúdābhyo vaniṣṭhór hŕ̥dayād ádhi» — gúdābhyaḥ = dat./abl.pl. жен. рода gudā, "
            "что соответствует уже имеющемуся отдельному f.-гнезду у Кочергиной.",
            "Порядок смыслов (кишечник → задний проход) внутри guda m. уже вторичен для «ануса» "
            "— претензия ветки 2013 г. по порядку смыслов тоже не актуальна.",
        ],
    },
    {
        "id": "sphic",
        "title": "स्फिच् sphic / स्फिगी sphigī / स्फिज् sphij — отсутствует заглавное слово + "
                 "перепутана ссылка",
        "flag": "change",
        "asis": "sphigī f. «бедро»; sphij f. «см. sphigī»; заглавного слова sphic НЕТ вообще.",
        "proposed": "(a) добавить недостающее заглавное слово sphic/sphik f. «ягодица, бедро "
                    "(мн. ягодицы)» как первичную форму; (b) исправить глоссу sphigī с «бедро» "
                    "на «ягодица, бедро» (текущая глосса — смысловая ошибка); (c) развернуть "
                    "направление перекрёстной ссылки: sphij и sphigī → sphic (как у MW), а не "
                    "наоборот.",
        "evidence": [
            "MW s.v. sphic — «sphic or sphij f. (nom. sphik) a buttock, hip "
            "{ShāṅkhGṛ. Mn. MBh &c.}».",
            "MW s.v. sphigī — «f. = sphic, a buttock {RV.}» — собственная ссылка MW идёт "
            "sphigī → sphic, ровно наоборот направлению у Кочергиной (sphij → sphigī).",
            "Apte s.v. sphic — «f. Buttocks, hips».",
            "KEWA III:542-543 трактует sphik/sphij/sphic как варианты одного этимона.",
            "RV-аттестация перепроверена напрямую в акцентуированном корпусе VedaWeb: 3.32.11 "
            "«…yád anyáyā sphigyā̀ kṣā́m ávasthāḥ» и 8.4.8 «savyā́m ánu sphigyàṃ vāvase vŕ̥ṣā» "
            "— обе формы sphigī; голого sphic/sphij в RV нет (согласуется с MW, где эти формы "
            "цитируются из более поздних текстов: ShāṅkhGṛ./Manu/MBh).",
        ],
    },
]

# Migration: old hand-authored key "reviewsheet:<id>" -> emitter key
# "review-sheet:<id>". Runs BEFORE the emitter's core script (which reads
# STORE_KEY into `state` at load), so it is spliced ahead of the document's
# single <script>, not onto </body>. Copies only when the new key is empty and
# the old one exists; the old record shape {decision, note} maps 1:1.
MIGRATION_JS = """<script>
(function () {
  var SHEET_ID = %(sheet_id_json)s;
  var NEW_KEY = 'review-sheet:' + SHEET_ID;  /* csl_pyutil emitter key */
  var OLD_KEY = 'reviewsheet:' + SHEET_ID;   /* hand-authored 12-07-2026 page key */
  try {
    var newRaw = localStorage.getItem(NEW_KEY);
    var oldRaw = localStorage.getItem(OLD_KEY);
    if (oldRaw && (!newRaw || newRaw === '{}')) {
      var old = JSON.parse(oldRaw) || {};
      var migrated = {};
      %(ids_json)s.forEach(function (id) {
        var rec = old[id];
        if (!rec) return;
        var out = {};
        if (rec.decision === 'approve' || rec.decision === 'reject' || rec.decision === 'defer') {
          out.decision = rec.decision;
        }
        if (typeof rec.note === 'string' && rec.note) { out.note = rec.note; }
        if (out.decision || out.note) { migrated[id] = out; }
      });
      if (Object.keys(migrated).length) {
        localStorage.setItem(NEW_KEY, JSON.stringify(migrated));
      }
    }
  } catch (e) { /* never block the sheet on migration */ }
})();
</script>
"""


def build_items():
    out = []
    for it in ITEMS:
        panels = [
            ("Как сейчас (Кочергина)", mark_cyrillic(esc(it["asis"]))),
            ("Предлагается", mark_cyrillic(esc(it["proposed"]))),
            ("Аттестация / источники",
             "<ul>%s</ul>" % "".join("<li>%s</li>" % esc(e) for e in it["evidence"])),
        ]
        out.append({
            "id": it["id"],
            "filt": it["flag"],
            "title": it["title"],
            "badges": [FLAG_LABELS[it["flag"]]],
            "question": "",
            "panels": panels,
            # no title_href: the source data carries no entry URLs (V4 n/a)
        })
    return out


def main():
    config = {
        "sheet_id": SHEET_ID,
        "title": "Кочергина (learnsanskrit.ru): okas · okya · guda · sphic — 4 кандидата на правку",
        "generated": GENERATED,
        "subtitle": "H779 · Nagari-list 2013 re-verification · перегенерировано по стандарту "
                    "19-07-2026 из ручного листа 12-07-2026 (Sonnet 5, claude-sonnet-5)",
        "footer": "Кочергина re-verification (H779) — approve = принять вердикт карточки "
                  "(правка или «без изменений»), reject = отклонить его.",
        "approve_label": "Approve",
        "reject_label": "Reject",
        "filters": [("change", "нужна правка"), ("noaction", "без изменений")],
    }
    config.update(standard_config(
        save_as="RussianTranslation\\review\\" + SHEET_ID + "_decisions.json"))

    html_out = render_review_sheet(build_items(), config, extras=True)

    # Splice the localStorage migration ahead of the document's single core
    # <script> (h178_eval_bakeoff.py pattern, but pre-script: the core IIFE
    # reads the store at load, so an after-</body> splice would run too late).
    assert html_out.count("<script>") == 1, "emitter layout changed — re-check migration splice"
    html_out = html_out.replace("<script>", MIGRATION_JS % {
        "sheet_id_json": json.dumps(SHEET_ID),
        "ids_json": json.dumps([it["id"] for it in ITEMS]),
    } + "<script>", 1)

    os.makedirs(REVIEW, exist_ok=True)
    out = os.path.join(REVIEW, SHEET_ID + "_review.html")
    io.open(out, "w", encoding="utf-8").write(html_out)
    print("sheet:", out, "(%d items)" % len(ITEMS))


if __name__ == "__main__":
    main()
