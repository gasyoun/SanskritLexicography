#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_wsd_c1_pilot_48_sheet.py -- MG pass-1 vehicle for the C1 WSD pilot.

Emits the 48-card Russian review sheet over the frozen pilot slice
(wsd_frame_c1_pilot_48.tsv, cut by pilot_wsd_frame.py from the 200-row
wsd_frame_c1_200.tsv), per
docs/WSD_GOLD_SET_ANNOTATION_PROTOCOL_2026.md section 5.

Why this exists at all: H3172 shipped the frame and the protocol but no
annotation vehicle, so pass 1 was left pointing at a .tsv. A TSV is an agent
format -- /review-sheet Phase 0-pre bans adjudicating inside one, and MG ruled
the same on 28-08-2026 ("This format is for agents, not humans"). The BLI half
of the same programme already had its sheet (build_bli_gold_b1_500_sheet.py,
H2551); this is the missing twin, deliberately built to the same shape so the
two pass-1 surfaces behave identically.

Inverted screening case (protocol section 5 / review-sheet Phase 0-bis): the
human label IS the deliverable, so all 48 cards are class (d) -- no
deterministic/lookup/agent resolver applies. The frame's own deterministic
screen already ran upstream at sampling time (sample_wsd_frame.py excluded 206
lemmas whose menus are degenerate, protocol section 3); that is recorded here
as the (a) count rather than re-run.

Label semantics (protocol section 5), mapped onto the emitter's three verbs:

  Approve  -- one listed sense fits; its NUMBER goes in the note field.
  Reject   -- carries a reason label, and the two reasons are NOT the same
              outcome: ``none`` is the protocol's NONE (no listed sense fits
              this token) and is a REPORTED FINDING measuring how much real
              corpus usage the PWG numbered inventory fails to cover -- not an
              annotator error; ``proper_name`` / ``corrupt`` / ``wrong_lemma``
              are the protocol's SKIP, which drops the row from the
              denominator entirely. Keeping them as distinct reject labels is
              what lets the NONE-rate be computed separately downstream.
  Defer    -- undecided, revisit.

V9 EvidenceManifest: declares what each card joined (the frozen pilot slice)
and what was deliberately withheld -- above all mfs_baseline.py's own
most-frequent-sense prediction for these same lemmas. Protocol section 5 is
explicit that neither annotator may see the WSD system's or the MFS baseline's
predictions: showing the machine's answer next to the question it is being
measured against turns the gold set into a rubber stamp.

Regen (canonical invocation, from the repo root):

  python RussianTranslation/src/eval/build_wsd_c1_pilot_48_sheet.py

Output: ``RussianTranslation/review/<sheet_id>.html`` (gitignored).
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from csl_pyutil import RU_UI_STRINGS, esc, mark_cyrillic  # noqa: E402
from csl_pyutil.evidence import find_slp1  # noqa: E402

from _sanskrit_util_vendored import source_line_to_iast  # noqa: E402
from packset_output import emit_sheet  # noqa: E402
from review_evidence_preflight import EvidenceManifest  # noqa: E402
from review_sheet_standard import pwg_entry_href, slp1_iast, standard_config  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.dirname(os.path.dirname(HERE))
REVIEW = os.path.join(RT_ROOT, "review")
FRAME_TSV = os.path.join(HERE, "wsd_frame_c1_pilot_48.tsv")

SHEET_ID = "sanskritlexicography-wsd_gold_c1_pilot_48_review"
GENERATED = "28-08-2026"

# Polysemy bands as the frame cuts them (protocol section 4). I10+ is the band
# the pilot exists to stress: 12-16 options a row is where the reading cost and
# the expected disagreement both concentrate.
BAND_LABEL = {
    "I2-5": "I2-5 (2-5 значений)",
    "I6-9": "I6-9 (6-9 значений)",
    "I10+": "I10+ (10 и более значений)",
}


def parse_frame(path):
    rows = []
    with io.open(path, encoding="utf-8") as f:
        header = None
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            cols = line.split("\t")
            if header is None:
                header = cols
                continue
            rows.append(dict(zip(header, cols)))
    return rows


def split_menu(menu):
    """The frame's sense_menu -> [(tag, gloss_html), ...], one per option.

    Options are separated by U+2016 and each opens with its PWG sense tag in
    square brackets: ``[1] ... ‖ [2] ...``. The tag is what pass 1 writes in
    the note field, so it is rendered as the visible option number.
    """
    out = []
    for chunk in (menu or "").split("‖"):
        chunk = chunk.strip()
        if not chunk:
            continue
        m = re.match(r"^\[([^\]]+)\]\s*(.*)$", chunk, re.S)
        tag, body = (m.group(1), m.group(2)) if m else ("?", chunk)
        out.append((tag.strip(), body.strip()))
    return out


def close_truncated_markup(body):
    """-> (body, was_truncated). Repair a PWG markup span the frame cut open.

    The frame caps the ``sense_menu`` field, and the cut lands mid-``{#...#}``
    on 32 of the pilot's 352 options (9%, measured). ``source_line_to_iast()``
    only converts *balanced* spans, so an unterminated tail would reach the
    reviewer as raw ``{#ra`` -- SLP1 in human-facing text, which is both the
    V9 preflight's blocking finding and simply unreadable. Closing the span
    lets the same canonical converter romanise it; the caller then marks the
    option as truncated so nobody mistakes a cut gloss for a complete one.

    The cut can land anywhere inside the two-character closer, so the repair
    has to look at what actually survived: ``...da^DiDve#`` kept its ``#`` and
    lost only the ``}``, and blindly appending a whole ``#}`` there yields
    ``##}``, which the converter's ``\\{[#@]([^#@]*)[#@]\\}`` still refuses to
    match -- the leak this function exists to stop, wearing a second hat.
    """
    out, cut = body.rstrip(), False
    for op, cl in (("{#", "#}"), ("{@", "@}")):
        if out.count(op) > out.count(cl):
            # closer half-eaten (delimiter char kept, brace lost) vs fully eaten
            out += "}" if out.endswith(cl[0]) else cl
            cut = True
    if out.endswith("{"):          # even the delimiter char was cut away
        out, cut = out[:-1].rstrip(), True
    return out, cut


def render_menu(menu):
    """The sense menu as a numbered, readable list.

    ``{#...#}`` is PWG's SLP1-in-markup; source_line_to_iast() is this repo's
    canonical converter for it (SHARED_CODE: do not re-derive a transcoder).
    Russian glosses get mark_cyrillic() per V7; the IAST around them must not.
    """
    parts = []
    for tag, body in split_menu(menu):
        body, cut = close_truncated_markup(body)
        html = mark_cyrillic(esc(source_line_to_iast(body, "pwg")))
        if cut:
            html += (' <span style="opacity:.7" title="Статья PWG в этом месте '
                     'обрезана рамкой выборки">&hellip; ⟨обрезано⟩</span>')
        parts.append(
            '<li style="margin-bottom:.42em"><b style="color:var(--accent)">[%s]</b> %s</li>'
            % (esc(tag), html)
        )
    return ('<ol style="margin:.3em 0 .1em 1.2em;line-height:1.55">%s</ol>'
            % "".join(parts))


def render_sentence(sentence, form):
    """The DCS sentence with the token under judgment made findable.

    Without the highlight a reviewer re-scans a 12-word Sanskrit line for the
    target on every card; the form column already says which token it is.

    4 of the 48 pilot rows (measured, 8%) carry a ``form`` that does NOT occur
    verbatim in ``sentence`` -- external sandhi has fused it into a neighbour
    (``jahyāt`` + ``jīvitāt`` -> ``jahyājjīvitād``; ``hi`` + ``iha`` ->
    ``hīha``), or the lemma assignment is itself wrong. Rendering those with a
    silently-missing highlight would hand the reviewer a card whose question
    ("this token, in this sentence") cannot be located, so the card says so
    instead and names the reject path. Finding these is part of what an
    instrument check is for.
    """
    s = esc(sentence or "")
    f = esc(form or "")
    box = ('<div style="font-size:1.12em;line-height:1.65;padding:.5em .7em;'
           'border-left:3px solid var(--accent)">%s</div>')
    if f and f in s:
        return box % s.replace(
            f,
            '<mark style="background:var(--accent);color:#000;padding:0 .18em;'
            'border-radius:3px;font-weight:700">%s</mark>' % f,
            1)
    return (box % s) + (
        '<p style="margin:.5em 0 0;opacity:.85"><b>Слово в разборе:</b> '
        '<code>%s</code> &mdash; в предложении оно <b>не встречается в этой '
        'форме</b>: внешнее сандхи слило его с соседним словом, либо лемма '
        'определена неверно. Найдите его сами по смыслу; если это невозможно '
        '&mdash; &laquo;Не подходит / непригодно&raquo; с причиной '
        '<code>wrong_lemma</code> (или <code>corrupt</code>).</p>' % f)


def band_stats(rows):
    """U7 -- every band chip carries its own n and its share of THIS sheet.

    Denominator stated explicitly (Phase 0-ter rule 2): the 48 pilot rows, not
    the 200-row frame and not the store.
    """
    total = len(rows)
    counts = {}
    for r in rows:
        counts[r["band"]] = counts.get(r["band"], 0) + 1
    # ``share`` is a fraction of this sheet's population, not a percent string
    # -- the emitter formats it (U7). Denominator = the 48 pilot rows.
    return {b: (n, float(n) / total) for b, n in counts.items()}


HOWTO = (
    "<p><b>Задача.</b> Выберите <b>одно</b> значение из списка PWG, которое "
    "подходит для выделенного слова <i>в этом предложении</i>, и впишите его "
    "номер в поле записи (например <code>2</code>), затем нажмите "
    "&laquo;Значение выбрано&raquo;.</p>"
    "<p><b>Если ни одно значение не подходит</b> &mdash; нажмите "
    "&laquo;Не подходит / непригодно&raquo; и выберите причину "
    "<code>none</code>. Это <b>не ошибка разметки, а результат</b>: доля "
    "<code>NONE</code> измеряет, насколько нумерованные значения PWG вообще "
    "покрывают реальное употребление в корпусе, и это самостоятельный вывод "
    "пункта C1.</p>"
    "<p><b>Если строку нельзя размечать</b> (собственное имя, испорченное "
    "предложение, лемма определена неверно) &mdash; та же кнопка, но причина "
    "<code>proper_name</code> / <code>corrupt</code> / <code>wrong_lemma</code>. "
    "Такая строка выбывает из знаменателя целиком, в отличие от "
    "<code>none</code>.</p>"
    "<p><b>Не уверены</b> &mdash; &laquo;Отложить&raquo;.</p>"
)


def build_items(rows, stats):
    out = []
    for r in rows:
        key1 = r["lemma_key1"]
        band = r["band"]
        n, share = stats[band]
        options = split_menu(r["sense_menu"])
        out.append({
            "id": r["row_id"],
            "filt": band,
            "title": "%s — %s" % (r["lemma_iast"], r["form"]),
            "title_href": pwg_entry_href(key1),
            "badges": [
                r["upos"],
                r["citation"],
                "%d вариантов в меню" % len(options),
            ],
            "typology": [{"label": BAND_LABEL.get(band, band), "n": n, "share": share}],
            "question": render_sentence(r["sentence"], r["form"]),
            "panels": [
                ("Значения PWG — выберите одно", render_menu(r["sense_menu"])),
                ("Как размечать", HOWTO),
            ],
            "note_placeholder": "номер значения, например 2",
        })
    return out


def declared_slp1_tokens(rows):
    """SLP1-looking tokens the sheet legitimately shows (V9 leak check).

    Declared from the data rather than silenced globally (same discipline as
    build_bli_gold_b1_500_sheet.py). Four honest sources: the frame's own IAST
    lemma and token forms, the romanised DCS sentence, and -- the two that
    actually trip the D2 heuristic here -- the text-source sigla in the
    citation badge (MBh, MPur, DKCar, GokPurS, HBhVil ...) and the Latin
    abbreviations travelling inside the verbatim-quoted PWG menu (DHATUP.,
    Nachtr. and friends). A siglum is a citation label, not leaked SLP1; it
    must stay verbatim for the citation to remain checkable.
    """
    ids = {r["lemma_iast"] for r in rows} | {r["form"] for r in rows}
    chunks = []
    for r in rows:
        chunks.append(r["citation"])
        chunks.append(r["sentence"])
        # Per option, and through the same truncation repair the cards use --
        # otherwise the allow-set is computed over text the sheet never shows.
        for _tag, body in split_menu(r["sense_menu"]):
            body, _cut = close_truncated_markup(body)
            chunks.append(source_line_to_iast(body, "pwg"))
    blob = "\n".join(chunks)
    return ids | set(find_slp1(blob, allow=ids))


def build_manifest(sheet_id, items, frame_path):
    """What this sheet joined per card, and what it deliberately did not."""
    man = EvidenceManifest(sheet_id, [it["id"] for it in items])
    rel = os.path.relpath(frame_path, RT_ROOT).replace("\\", "/")

    man.declare_joined(rel, ["row_id", "occ_id", "citation", "lemma_key1",
                             "lemma_iast", "band", "n_senses", "form", "upos",
                             "sentence", "sense_menu"])
    for it in items:
        man.add_card(it["id"], ["lemma_iast", "form", "upos", "citation",
                                "band", "sentence", "sense_menu"])

    man.declare_omitted(
        "mfs_baseline.py's most-frequent-sense prediction for these same "
        "lemmas (the card-5 emitter shipped in H775, whose accuracy number is "
        "exactly what this gold set is being built to measure)",
        "protocol section 5 -- neither annotator may see the WSD system's or "
        "the MFS baseline's predictions; annotating with the system's output "
        "visible converts the gold set into a rubber stamp, and the baseline "
        "would anchor pass 1 toward the very sense it is being scored on")
    man.declare_omitted(
        "the frozen model annotator-2 pass over the same rows (protocol "
        "section 5, shared annotator-2 freeze record)",
        "order constraint -- pass 2 must not run, and must not be visible, "
        "before pass 1 is frozen; showing it would collapse the human-model "
        "agreement statistic the whole two-pass design exists to produce")
    man.declare_omitted(
        "the remaining 152 rows of wsd_frame_c1_200.tsv",
        "deliberate scope -- the pilot is an instrument check (one row per "
        "lemma, every menu inspected exactly once) whose job is to decide "
        "whether the other 152 rows are worth annotating at all; row_id and "
        "occ_id are preserved so these labels merge straight into the full "
        "gold if they are")
    return man


def main(pack_size=0, hub_name=None, out_dir=None, locks_dir=None):
    rows = parse_frame(FRAME_TSV)
    assert len(rows) == 48, "pilot row count changed: %d (expected 48)" % len(rows)

    stats = band_stats(rows)
    filters = [(b, BAND_LABEL[b]) for b in ("I2-5", "I6-9", "I10+") if b in stats]

    config = {
        "sheet_id": SHEET_ID,
        "title": "WSD gold C1: пилот pass-1 (MG) — 48 карточек",
        "generated": GENERATED,
        "subtitle": (
            "H3172 · строгое подмножество wsd_frame_c1_200.tsv "
            "(row_id и occ_id сохранены, метки вливаются в полный gold) "
            "· 48 строк = по одной на лемму, каждое меню значений "
            "просматривается ровно один раз · 23% читательской нагрузки "
            "полной рамки "
            "· проценты на плашках диапазонов считаются от 48 строк этого "
            "пилота, не от 200-строчной рамки и не от словника"
        ),
        "footer": (
            "Approve = «Значение выбрано»: одно из значений PWG подходит, "
            "его номер вписан в поле записи — строка попадает в gold с этой "
            "меткой и в знаменатель P@1. "
            "Reject = «Не подходит / непригодно» с причиной: "
            "none — ни одно значение не подходит (это РЕЗУЛЬТАТ, доля NONE "
            "измеряет покрытие нумерованных значений PWG, строка остаётся в "
            "знаменателе); proper_name / corrupt / wrong_lemma — строка "
            "выбывает из знаменателя. "
            "Defer = отложить. "
            "Пилот решает, стоит ли размечать остальные 152 строки рамки."
        ),
        "approve_label": "Значение выбрано",
        "reject_label": "Не подходит / непригодно",
        "reject_labels": [
            ("none", "ни одно значение не подходит (NONE — это результат)"),
            ("proper_name", "собственное имя"),
            ("corrupt", "предложение испорчено"),
            ("wrong_lemma", "лемма определена неверно"),
        ],
        "filters": filters,
        "identity_gate": {"patterns": [r"\bH\d{3,4}\b"], "labels": {}},
        "ui_strings": dict(RU_UI_STRINGS, save_banner=(
            '&#128229; Ваш экспорт скачивается как <code>%s_decisions.json</code> '
            '&rarr; сохраните его в <code>RussianTranslation\\review\\%s_decisions.json</code> '
            '(значение <code>sheet_id</code> внутри файла — <code>%s</code> — так следующая '
            'сессия узнаёт, к какому листу относятся эти решения).'
            % (SHEET_ID, SHEET_ID, SHEET_ID))),
    }
    config.update(standard_config(
        save_as=r"RussianTranslation\review\%s_decisions.json" % SHEET_ID))

    screening = {
        # (a) ran upstream at sampling time, not re-run here: sample_wsd_frame.py
        # excluded 206 of the 254 candidate lemmas whose menus are degenerate
        # (fewer than 2 numeric pwg senses, or no 2 distinguishable glosses) --
        # protocol section 3. Those never became cards.
        "deterministic": 206,
        "lookup": 0,
        "agent": 0,
        "human": len(rows),
        "evidence_path": "docs/WSD_GOLD_SET_ANNOTATION_PROTOCOL_2026.md#3-degenerate-menus-are-excluded-not-pooled",
        "rules": [
            "degenerate-menu-exclusion (protocol section 3, applied in sample_wsd_frame.py)",
            "human label is the deliverable (protocol section 5) -- no resolver applies to the 48",
        ],
    }

    items = build_items(rows, stats)
    config["preflight"] = {"allow_slp1_tokens": tuple(sorted(declared_slp1_tokens(rows)))}
    os.makedirs(REVIEW, exist_ok=True)
    out = os.path.join(out_dir or REVIEW, SHEET_ID + ".html")
    paths, lock, n_packs = emit_sheet(
        items, config, out,
        screening=screening,
        manifest=build_manifest(SHEET_ID, items, FRAME_TSV),
        generated=GENERATED, locks_dir=locks_dir, gate="WSD-C1",
        pack_size=pack_size, hub_name=hub_name)
    if n_packs:
        print("sheet: %s (%d items -> %d packs of <=%d)"
              % (out, len(items), n_packs, pack_size))
    else:
        print("sheet:", out, "(%d items)" % len(items))
    print("  lock ->", lock)


def selftest():
    rows = parse_frame(FRAME_TSV)
    assert len(rows) == 48, "expected 48 pilot rows, got %d" % len(rows)
    ids = set(r["row_id"] for r in rows)
    assert len(ids) == 48, "duplicate row_id in pilot"
    lemmas = set(r["lemma_key1"] for r in rows)
    assert len(lemmas) == 48, "pilot is one row per lemma: got %d lemmas" % len(lemmas)
    stats = band_stats(rows)
    items = build_items(rows, stats)
    for it in items:
        assert it["id"] and it["title_href"], it
        assert "<li" in it["panels"][0][1], "empty sense menu on %s" % it["id"]
        # Either the token is highlighted, or the card explicitly says it
        # could not be located -- never a silently unmarked sentence.
        assert ("<mark" in it["question"]
                or "не встречается в этой форме" in it["question"]), \
            "target form neither highlighted nor flagged on %s" % it["id"]
    unlocatable = sum(1 for r in rows if r["form"] not in r["sentence"])
    assert unlocatable == 4, (
        "sandhi-fused/unlocatable target count changed: %d (was 4/48 when the "
        "sheet was designed) -- re-read render_sentence()'s docstring"
        % unlocatable)
    # No raw PWG markup may survive into human-facing card text.
    for it in items:
        menu_html = it["panels"][0][1]
        for bad in ("{#", "#}", "{@", "@}"):
            assert bad not in menu_html, \
                "raw markup %r leaked into %s's menu" % (bad, it["id"])
    n_opts = sum(len(split_menu(r["sense_menu"])) for r in rows)
    n_cut = sum(1 for r in rows for _t, b in split_menu(r["sense_menu"])
                if close_truncated_markup(b)[1])
    assert n_cut == 33, (
        "frame-truncated option count changed: %d (was 33/352 when the sheet "
        "was designed -- 32 with a half-eaten closer, 1 with the delimiter "
        "cut away entirely)" % n_cut)
    print("selftest: OK (%d rows, %d lemmas, %d menu options, bands %s)"
          % (len(rows), len(lemmas), n_opts, sorted(stats)))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
    else:
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument("--pack-size", type=int, default=0)
        ap.add_argument("--hub-name", default=None)
        ap.add_argument("--out-dir", default=None)
        ap.add_argument("--locks-dir", default=None)
        a = ap.parse_args()
        main(pack_size=a.pack_size, hub_name=a.hub_name,
             out_dir=a.out_dir, locks_dir=a.locks_dir)
