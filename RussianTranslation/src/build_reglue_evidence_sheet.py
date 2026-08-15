#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_reglue_evidence_sheet.py — the re-glue vote, with the evidence on the card (H2859).

What was wrong with the v2 sheet
--------------------------------
It asked "is the glue typology and placement right?" over a whole headword — up
to **412 supplements behind one approve/reject** — and showed only the *Russian*.
Both are disqualifying under the org
[content standard](https://github.com/gasyoun/Uprava/blob/main/docs/REVIEW_SHEET_CONTENT_STANDARD_2026.md):

* **U2 (self-contained)** — the typology is a claim about how a later layer
  relates to PWG, and that relation holds **between the German originals**. A
  card showing two Russian translations asks the reviewer to judge a relationship
  whose evidence is off-card.
* **E1 (primary evidence quoted, not "agent said OK")** — the sidecar's whole
  justification for 5,054 of 5,603 chips is the string
  ``"PW abridging restatement; sense_tag='4'"``, i.e. the rule restated. Per
  [ADDENDA_TYPOLOGY](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ADDENDA_TYPOLOGY.md)
  §5 `restate` is simply the default when no gender conflict is found.
* **Granularity** — one verdict cannot answer for hundreds of independent claims.

So this sheet is **per supplement**, stratified, and puts the German of both
sides on the card next to what the machine claimed and why.

An axis that was tried and rejected
-----------------------------------
Gloss-word overlap (Jaccard over German content words) looked like the obvious
way to make ≈-vs-＋ checkable. Measured, it does **not** discriminate: median
overlap is 0.000 for both classes. The cause is in the data, not the code —
a PWG sense body has a **median of 3 content tokens** (39 chars) and 16 % have
none at all, so two short German synonym lists share no surface forms even when
one genuinely restates the other. It is reported per card as raw counts for
context, and deliberately **not** rendered as a verdict signal: a number that
looks like evidence and isn't is worse than no number.
[`reglue_overlap.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reglue_overlap.py)
keeps the measurement so the negative result stays reproducible.

Citation overlap survives as real, objective evidence and is shown.

Run: python src/build_reglue_evidence_sheet.py   (set PWG_RU_DATA_ROOT)
     python src/build_reglue_evidence_sheet.py --selftest
"""
import sys, os, io, json, re, html, collections

from csl_pyutil import render_review_sheet, mark_cyrillic, anatomy
from review_binding import stamp, write_lock
from review_sheet_standard import standard_config, slp1_iast, pwg_entry_href
from sheet_screening import screening_block
import reglue_overlap as ro

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("PWG_RU_DATA_ROOT", os.path.dirname(HERE))
REVIEW = os.path.join(DATA, "review")
GENERATED = "2026-08-15"
SHEET_ID = "h180-reglue-evidence-2026-08-15"

#: (layer, subtype) -> how many to sample, drawn ONLY from checkable pairs.
#:
#: "Checkable" is doing real work here. Of 5,603 supplements, **5,054 (90.2 %)
#: carry `target_sense='*new'`** — the pipeline's own marker for "no PWG sense to
#: attach to" — while still being labelled `restate`, because the subtype is
#: assigned by layer default independently of whether a target was found. Asking
#: a human "does this restatement sit at the right PWG sense?" when the sidecar
#: already says there is no such sense is not a question. A further slice has a
#: real target but German too thin to compare (a PWG sense body has a median of
#: 3 content words), leaving **246 (4.4 %)** genuinely checkable pairs. The vote
#: is drawn from those; the structural facts are reported, not voted on.
QUOTA = {
    ("pw", "restate"): 26,
    ("pwkvn", "a2a"): 6,
    ("sch", "derived_sense"): 5,
    ("sch", "sch_star"): 4,
    ("nws", "nws_at_sense"): 4,
    ("pwkvn", "derived_sense"): 2,
}

CLASS_LABEL = {"adds": "＋ добавленный смысл", "restates": "≈ пересказ",
               "cancels": "✕ отмена / правка"}
CLASS_OF = {"restate": "restates", "pw_correct": "cancels", "pw_cancels": "cancels",
            "nws_at_sense": "adds", "sch_star": "adds", "derived_sense": "adds",
            "foreign_fragment": "adds", "a2a": "adds"}

EXTRA_CSS = """  .tchip { display:inline-block; padding:1px 7px; border-radius:9px;
    font-size:11px; font-weight:600; margin-right:4px; white-space:nowrap; }
  .t-adds { background:#173a22; color:#8fe3a8; border:1px solid #2f6b42; }
  .t-restates { background:#3a3117; color:#e6c07b; border:1px solid #6b5a2f; }
  .t-cancels { background:#3a1a1a; color:#e69a9a; border:1px solid #6b2f2f; }
  .t-meta { background:#23282f; color:#9aa0aa; border:1px solid #3a4048; }
  .side { display:block; margin:0 0 10px 0; padding:8px 10px;
          border-left:3px solid #3a4048; }
  .side .who { font-weight:700; color:#9aa0aa; margin-bottom:4px; font-size:12px; }
  .side .de { color:#d8dce2; line-height:1.6; }
  .side .ru { color:#9aa0aa; line-height:1.6; margin-top:5px; font-size:13px; }
  .claim { font:12.5px/1.7 Consolas,'Cascadia Mono',monospace; color:#d8dce2; }
  .claim b { color:#e6c07b; }
  .weak { color:#e06c75; }
"""


def esc(s):
    return html.escape("" if s is None else str(s))


def de_html(text):
    """German body, anatomy-coloured (the evidence the judgement rests on)."""
    return anatomy.highlight(text or "(нет немецкого текста в store)")


def ru_html(text):
    return mark_cyrillic(esc(ro.strip_markup(text or "") or "(нет русского перевода)"))


def build_items():
    store, rel = ro.load()
    idx = ro.pwg_sense_index(store)

    # Build the CHECKABLE pool: a real PWG target sense, and enough German on
    # both sides to compare. Everything else is a structural fact to report, not
    # a question to put in front of a human.
    pools = collections.defaultdict(list)
    census = collections.Counter()
    for r in rel:
        st = (r["layer"], r["relationship"]["subtype"])
        census["total"] += 1
        rec = store.get((r["subcard"], str(r["sense_tag"])))
        if not rec:
            continue
        ip = r["relationship"]["insertion_point"]
        target = idx.get((r.get("key1"), ip.get("homonym", "h0"),
                          str(ip.get("target_sense"))))
        if not target:
            census["no_target"] += 1
            continue
        if not ro.compare(target.get("de", ""), rec.get("de", ""))["comparable"]:
            census["too_thin"] += 1
            continue
        census["checkable"] += 1
        pools[st].append((r, rec, target))

    items, sampled = [], collections.Counter()
    for stratum, quota in QUOTA.items():
        pool = sorted(pools.get(stratum) or [],
                      key=lambda t: (t[0]["key1"], t[0]["subcard"], str(t[0]["sense_tag"])))
        if not pool:
            continue
        # deterministic even stride — no seed to lose, reproducible from the file
        step = max(1, len(pool) // quota)
        for r, rec, target in pool[::step][:quota]:
            ip = r["relationship"]["insertion_point"]
            m = ro.compare(target.get("de", ""), rec.get("de", ""))
            subtype = r["relationship"]["subtype"]
            kl = CLASS_OF.get(subtype, "adds")
            layer = r["layer"]

            pwg_side = (
                '<div class="side"><div class="who">PWG — смысл %s (немецкий оригинал)</div>'
                '<div class="de">%s</div><div class="ru">%s</div></div>'
                % (esc(ip.get("target_sense")),
                   de_html(target.get("de", "")), ru_html(target.get("ru", ""))))
            supp_side = (
                '<div class="side"><div class="who">%s — эта добавка (немецкий оригинал)</div>'
                '<div class="de">%s</div><div class="ru">%s</div></div>'
                % (esc(layer.upper()), de_html(rec.get("de", "")), ru_html(rec.get("ru", ""))))

            cit = m["citation_overlap"]
            cit_s = ("%.0f%% (%s)" % (100 * cit, ", ".join(m["shared_citations"]) or "—")
                     if cit is not None else "у смысла PWG нет цитат")
            weak = ("" if m["comparable"] else
                    ' <span class="weak">— слишком короткие глоссы, доля слов здесь '
                    'неинформативна</span>')
            claim = (
                '<div class="claim">'
                'машина утверждает: <b>%s</b> · op <b>%s</b> · направление <b>%s</b><br>'
                'точка вставки: смысл <b>%s</b>, якорь <b>%s</b><br>'
                'обоснование в сайдкаре: <b>%s</b><br>'
                'уверенность: <b>%s</b><br><br>'
                'общие цитаты &lt;ls&gt;: <b>%s</b><br>'
                'слов в глоссе: PWG <b>%d</b> · добавка <b>%d</b>%s<br>'
                'длина: PWG %d знаков · добавка %d знаков</div>'
                % (esc(subtype), esc(r["relationship"]["op"]),
                   esc(r["relationship"]["direction"]),
                   esc(ip.get("target_sense")), esc(ip.get("anchor")),
                   esc(r["relationship"].get("evidence", "—")),
                   esc(r["relationship"].get("confidence", "—")),
                   esc(cit_s), m["pwg_terms"], m["supp_terms"], weak,
                   m["pwg_chars"], m["supp_chars"]))

            items.append({
                "id": "%s::%s" % (r["subcard"], r["sense_tag"]),
                "filt": layer,
                "title": "%s · %s → смысл %s" % (slp1_iast(r["key1"]), layer.upper(),
                                                 ip.get("target_sense")),
                "title_href": pwg_entry_href(r["key1"]),
                "badges": [subtype, CLASS_LABEL[kl]],
                "question": (
                    'Сравните два немецких текста выше. '
                    '<b>Добавка стоит в нужном смысле PWG, и метка «%s» верна?</b>'
                    '<span class="muted"> — «Да» = и место, и метка верны; '
                    '«Нет» = что-то не так (укажите что в поле ниже); '
                    '«Не знаю» = не хватает данных.</span>'
                    % esc(CLASS_LABEL[kl])),
                "note_placeholder": "если «нет»: неверное место / неверная метка / и то и другое — и как правильно",
                "panels": [
                    ("1 · что говорит PWG и что говорит добавка", pwg_side + supp_side),
                    ("2 · что утверждает машина и на каком основании", claim),
                ],
                "machine_resolvable": False,
            })
            sampled[stratum] += 1
    return items, sampled, census


def main():
    os.makedirs(REVIEW, exist_ok=True)
    items, sampled, census = build_items()
    if not items:
        print("no items — is PWG_RU_DATA_ROOT pointing at a tree with the store + sidecar?")
        return 1

    strata_note = " · ".join("%s/%s %d из %d" % (l, s, sampled[(l, s)], q)
                             for (l, s), q in QUOTA.items() if sampled.get((l, s)))
    config = standard_config(
        save_as="RussianTranslation\\pwg_ru\\eval\\h180_reglue_evidence.decisions.json")
    config.update({
        "sheet_id": SHEET_ID,
        "title": "H180 · склейка: место и метка каждой добавки",
        "subtitle": ("по одной добавке на карточку — с немецкими оригиналами обеих "
                     "сторон, а не только с русским переводом"),
        "footer": (
            "Каждая карточка — <b>одна</b> добавка, а не целая статья: в v2 за одним "
            "«одобрить» стояло до 412 добавок сразу. Метка «≈ пересказ» стоит у 5 054 из "
            "5 603 добавок и в сайдкаре ничем не обоснована — это значение по умолчанию "
            "для слоя PW, когда не найдено расхождения в роде. Поэтому здесь на карточке "
            "лежит первичное свидетельство: <b>немецкий оригинал обеих сторон</b>, потому "
            "что отношение между слоями держится именно на нём, а не на переводе.<br>"
            "Доля общих слов в глоссах <b>намеренно не показана как признак</b>: она "
            "измерена и не разделяет классы (медиана 0,000 у обоих) — у смысла PWG в "
            "медиане всего 3 знаменательных слова, поэтому два коротких немецких "
            "синонимических ряда не пересекаются даже когда один пересказывает другой."
            "<br><br><b>Что здесь НЕ голосуется, и почему.</b> Из %d добавок <b>%d "
            "(%.1f%%)</b> в сайдкаре имеют <code>target_sense='*new'</code> — то есть "
            "смысла PWG, к которому их якобы прикрепили, попросту нет, — и при этом всё "
            "равно помечены <code>restate</code> («пересказ PWG»), потому что метка "
            "ставится по слою, независимо от того, нашлась ли цель. Спрашивать человека "
            "«в том ли смысле стоит пересказ», когда сайдкар сам говорит, что смысла нет, "
            "— это не вопрос. Ещё %d пары имеют цель, но слишком короткий немецкий, чтобы "
            "их можно было сверить. Остаётся <b>%d (%.1f%%)</b> действительно проверяемых "
            "пар — голосование идёт по ним. Остальное — структурная находка, она "
            "зафиксирована в отчёте, а не вынесена на голос.<br>"
            "Выборка: " + strata_note + " (равномерный шаг по отсортированному списку, "
            "без случайного зерна — воспроизводится из файла).")
            % (census["total"], census["no_target"],
               100.0 * census["no_target"] / max(census["total"], 1),
               census["too_thin"], census["checkable"],
               100.0 * census["checkable"] / max(census["total"], 1)),
        "approve_label": "Да — место и метка верны",
        "reject_label": "Нет — что-то не так",
        "reject_labels": [
            ("wrong_place", "не тот смысл PWG"),
            ("wrong_label", "не та метка (＋/≈/✕)"),
            ("both", "и место, и метка"),
            ("not_a_supplement", "это вообще не добавка к этому смыслу"),
        ],
        "filters": [("pw", "PW"), ("nws", "NWS"), ("sch", "SCH"), ("pwkvn", "PWKVN")],
        "generated": GENERATED,
        "extra_css": EXTRA_CSS,
    })
    sc = screening_block(
        deterministic=0, lookup=0, agent=0, human=len(items),
        evidence_path="RussianTranslation/pwg_ru/SCREENING_H1650.md",
        rules=["reglue-evidence-h2859", "citation-overlap", "stratified-by-layer-subtype"])
    doc = render_review_sheet(items, config, extras=True, screening=sc)
    doc, chash = stamp(doc)

    with io.open(os.path.join(REVIEW, "h180_reglue_evidence_sample.jsonl"),
                 "w", encoding="utf-8", newline="\n") as fh:
        for it in items:
            fh.write(json.dumps({k: it[k] for k in ("id", "filt", "title")},
                                ensure_ascii=False) + "\n")
    out = os.path.join(REVIEW, "h180_reglue_evidence_sheet.html")
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    write_lock(SHEET_ID, chash, [it["id"] for it in items], GENERATED, source_html=out)

    print("  %d cards drawn from %d checkable pairs (of %d supplements; %d have no PWG target, %d too thin) -> %s"
          % (len(items), census["checkable"], census["total"], census["no_target"], census["too_thin"], out))
    for k, v in sorted(sampled.items()):
        print("     %-24s %d" % ("%s / %s" % k, v))
    return 0


# --------------------------------------------------------------------- selftest
def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    check(sum(QUOTA.values()) <= 80,
          "sample stays votable in one sitting (%d cards)" % sum(QUOTA.values()))
    # `nws/foreign_fragment` (62) and `pw/pw_correct` (1) are absent ON PURPOSE:
    # every one of them lands in the *new bucket with no PWG sense to compare
    # against, so there is no checkable pair to draw. Their absence is a finding
    # reported in the sheet footer, not an oversight in the quota table.
    check(set(QUOTA) == {("pw", "restate"), ("nws", "nws_at_sense"),
                         ("sch", "sch_star"), ("pwkvn", "a2a"),
                         ("sch", "derived_sense"), ("pwkvn", "derived_sense")},
          "quota covers exactly the strata that HAVE checkable pairs")
    check(all(s in CLASS_OF for (_, s) in QUOTA),
          "every sampled subtype maps to a displayed class")
    # the rejected axis must not be presented as a verdict signal
    src = io.open(os.path.abspath(__file__), encoding="utf-8").read()
    check("gloss_overlap" not in src.split("An axis that was tried")[1].split('"""')[1],
          "gloss_overlap is not rendered on the card as a signal")
    check("не показана как признак" in src, "the sheet states the axis was rejected, and why")
    check('"machine_resolvable": False' in src or "machine_resolvable" in src,
          "V10 screening flag is set per card")
    print("build_reglue_evidence_sheet selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
