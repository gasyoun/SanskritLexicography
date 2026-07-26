#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""review_residue_gate.py — reader-visible German-residue gate for review sheets.

Mandated by the g5-live-queue-batch1 abort vote (MG, 25-07-2026, sheet
``g5-live-queue-batch1-2026-07-25``): «Я не должен искать немецкие слова в
русском переводе. Ты должен. Перед тем как мне показывать.» A card must not
reach a human G5 sheet while its RENDERED Russian text still shows German.

Three mechanical detector layers, each covering a blind spot of the others:

1. **prose** — ``german_residue_scan.scan_text`` (H1302), keeping class ``'b'``
   hits only (class ``'c'`` are vetted false positives — preserved Latin/French
   glosses and author names; class ``'a'`` was fixed store-wide by H1302 and no
   longer occurs).
2. **ab** — an ``<ab>`` token that will render as German: classified
   «немецкое»/«контекстное»/«OCR» by the H1303 unified inventory
   (``pwg_ru/ABBREV_UNIFIED_LIST_PROPOSAL_2026-07.md``, column «Класс») and NOT
   yet render-translated by ``pwg_ab_ru.RU_MAP`` (unmapped tokens fall back to
   the raw German token at render time). Tokens absent from BOTH the inventory
   and ``RU_MAP`` are flagged too (``ab-unknown``) — unclassified means
   unscreened, and the gate errs toward not showing them. «Латинское»-classed
   tokens (Acc., ved., p., …) pass: per the 10-07-2026 decision they stay as
   international Latin sigla pending the H1303 ratification vote.
3. **ls-tail** — German sequence tokens (``fg.``/``fgg.``) inside ``<ls>``
   citation spans, which both layers above deliberately mask (named explicitly
   in the abort vote: «Может ли русский перевод содержать aus, zu, und, fg.?»).

**Machine-flag layer (P1 ruling, 26-07-2026).** MG ruled on the voting-queue
triage `@DECIDE` (screening audit
`Uprava/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md` §5/§7): cards carrying
a machine-findable store flag are AUTO-REJECTED from human sheets — a human is
never asked to vote a card an agent can already see is defective. Pending its
triage/repair (H1651), ``machine_flags(ru, de)`` detects:

* **D1** — Cyrillic inside ``{#…#}`` (the SLP1/Sanskrit wrapper) — never valid;
* **D3** — gloss-wrapper drift: the DE side has ``{%…%}`` gloss slots, the RU
  side has none and renders glosses as «…» guillemets instead;
* **D4** — gloss-slot count mismatch between DE and RU (flag-only class: many
  are legitimate, but per the ruling a flagged card waits for triage rather
  than spending a human vote).

D5 (gloss byte-identical to the German) is deliberately NOT flagged — the audit
measured it as mostly false positives (legitimate Latin/IAST).

The gate only decides what a human is SHOWN — it never rewrites store text
(that stays with H1302's fixer, the H1303 ratification, and H1651's repair
sweep).

  python src/review_residue_gate.py --stats [--queue PATH] [--store PATH]
  python src/review_residue_gate.py --selftest
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
PILOT = os.path.join(HERE, "pilot")
for p in (HERE, PILOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import german_residue_scan  # noqa: E402  (H1302 prose-residue detector)
from pwg_ab_ru import RU_MAP  # noqa: E402  (render-time <ab> -> RU display)

H1303_INVENTORY = os.path.join(RT, "pwg_ru", "ABBREV_UNIFIED_LIST_PROPOSAL_2026-07.md")
# | `tok` | freq | expansion | класс | ... — the H1303 unified 269-token table.
_H1303_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|\s*[^|]*\|\s*([^|]*)\|", re.M)
GERMAN_AB_CLASSES = frozenset({"немецкое", "контекстное", "OCR"})

_AB = re.compile(r"<ab\b[^>]*>(.*?)</ab>", re.S)
_LS = re.compile(r"<ls\b[^>]*>(.*?)</ls>", re.S)
# German sequence tokens legitimate layers mask away inside citations.
_LS_GERMAN = re.compile(r"\bfgg?\.")

_CONTEXT = 40


def _load_ab_classes(path=H1303_INVENTORY):
    if not os.path.exists(path):
        raise FileNotFoundError(
            "H1303 inventory missing: %s — the <ab> layer of the residue gate "
            "cannot classify tokens without it" % path)
    txt = io.open(path, encoding="utf-8").read()
    classes = {m.group(1): m.group(3).strip() for m in _H1303_ROW.finditer(txt)}
    if len(classes) < 200:  # the committed inventory has 269 tokens
        raise ValueError("H1303 inventory parse degraded: only %d tokens found "
                         "in %s" % (len(classes), path))
    return classes


_AB_CLASSES = None


def ab_classes():
    global _AB_CLASSES
    if _AB_CLASSES is None:
        _AB_CLASSES = _load_ab_classes()
    return _AB_CLASSES


def visible_german(ru_text):
    """Every way `ru_text` would still show German to a Russian reader after
    render-time <ab> translation. Returns [(layer, token, context), ...]."""
    if not ru_text:
        return []
    hits = []
    # 1. prose residue (H1302 detector; 'b' = needs retranslation)
    for token, ctx, cls in german_residue_scan.scan_text(ru_text):
        if cls == "b":
            hits.append(("prose", token, ctx))
    # 2. <ab> tokens that render as German
    classes = ab_classes()
    for m in _AB.finditer(ru_text):
        tok = re.sub(r"\s+", " ", m.group(1)).strip()
        if tok in RU_MAP:
            continue                      # renders as Russian
        ctx = ru_text[max(0, m.start() - _CONTEXT):m.end() + _CONTEXT].replace("\n", " ")
        cls = classes.get(tok)
        if cls is None:
            hits.append(("ab-unknown", tok, ctx))
        elif cls in GERMAN_AB_CLASSES:
            hits.append(("ab", tok, ctx))
    # 3. German sequence tokens inside <ls> citation spans
    for m in _LS.finditer(ru_text):
        for g in _LS_GERMAN.finditer(m.group(1)):
            s = m.start(1) + g.start()
            ctx = ru_text[max(0, s - _CONTEXT):s + len(g.group(0)) + _CONTEXT].replace("\n", " ")
            hits.append(("ls-tail", g.group(0), ctx))
    return hits


def is_clean(ru_text):
    return not visible_german(ru_text)


# --------------------------------------------------------------------------- machine flags
_SA_WRAP = re.compile(r"\{#(.*?)#\}", re.S)
_GLOSS_WRAP = re.compile(r"\{%.*?%\}", re.S)
_CYRILLIC = re.compile(r"[А-Яа-яЁё]")
_GUILLEMET = re.compile(r"«[^»]+»")


def machine_flags(ru_text, de_text):
    """Machine-findable store defects (P1 ruling 26-07-2026: auto-reject from
    sheets, route to triage/repair instead of a human vote).
    Returns [(flag, detail), ...] — 'D1' / 'D3' / 'D4'."""
    ru = ru_text or ""
    de = de_text or ""
    flags = []
    for m in _SA_WRAP.finditer(ru):
        if _CYRILLIC.search(m.group(1)):
            flags.append(("D1", "Cyrillic inside {#…#}: %s" %
                          m.group(0)[:60].replace("\n", " ")))
            break
    de_n = len(_GLOSS_WRAP.findall(de))
    ru_n = len(_GLOSS_WRAP.findall(ru))
    if de_n and not ru_n and _GUILLEMET.search(ru):
        flags.append(("D3", "DE has %d {%%…%%} slots, RU has none and uses «…»" % de_n))
    elif de_n != ru_n:
        flags.append(("D4", "gloss-slot count mismatch: DE %d vs RU %d" % (de_n, ru_n)))
    return flags


# --------------------------------------------------------------------------- stats
def _iter_jsonl(path):
    for line in io.open(path, encoding="utf-8"):
        if line.strip():
            yield json.loads(line)


def stats(queue_path, store_path):
    """Gate the live queue the way build_g5_review_sheet does: RU text taken
    from the store row when it resolves (fresh, post-H1302), else the queue's
    frozen copy."""
    store = {}
    for rec in _iter_jsonl(store_path):
        store[(rec.get("subcard"), str(rec.get("sense_tag")))] = rec
    total = flagged = 0
    by_layer = {}
    flagged_ids = []
    for r in _iter_jsonl(queue_path):
        total += 1
        rid = r.get("review_id") or ""
        rec = {}
        if ":subcard:" in rid and "#" in rid:
            sub, tag = rid.split(":subcard:", 1)[1].rsplit("#", 1)
            rec = store.get((sub, tag), {})
        ru = rec.get("ru") or r.get("ru") or ""
        hits = visible_german(ru)
        mflags = machine_flags(ru, rec.get("de") or "")
        if hits or mflags:
            flagged += 1
            flagged_ids.append(rid)
            for layer, _, _ in hits:
                by_layer[layer] = by_layer.get(layer, 0) + 1
            for flag, _ in mflags:
                by_layer[flag] = by_layer.get(flag, 0) + 1
    return {"total": total, "flagged": flagged, "clean": total - flagged,
            "hits_by_layer": by_layer, "flagged_ids": flagged_ids}


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = True

    def check(cond, label):
        nonlocal ok
        print(("  ok " if cond else "  FAIL ") + label)
        ok = ok and cond

    # inventory parses fully and the abort-vote tokens classify as expected
    classes = ab_classes()
    check(len(classes) >= 269, "H1303 inventory parsed (%d tokens)" % len(classes))
    check(classes.get("s. u.") == "немецкое" and classes.get("ved.") == "латинское",
          "inventory classes: 's. u.' German, 'ved.' Latin")

    # the two 25-07 reject cards' patterns:
    # _adika: <ab>s. u.</ab> is RU_MAP-mapped -> renders «см.» -> clean
    check(is_clean("{#Adika#}¦ <ab>s. u.</ab> {#Adi#}."),
          "_adika pattern clean (s. u. renders as см.)")
    # _bid: fg. inside an <ls> tail is reader-visible German -> flagged
    hits = visible_german('<ab>Sch.</ab> к <ls n="P.">7,2,61. fg.</ls>')
    check(any(l == "ls-tail" and t == "fg." for l, t, _ in hits),
          "_bid pattern flagged (fg. inside <ls>)")

    # unmapped German <ab> token flagged; Latin grammatical token passes
    check(not is_clean("{%также%} <ab>u. dgl.</ab> {#x#}")
          if classes.get("u. dgl.") in GERMAN_AB_CLASSES or "u. dgl." not in classes
          else True, "unmapped German/unknown <ab> flagged")
    check(is_clean("2. <ab>p.</ab> {#aBinas#} и {#aBinad#}"),
          "Latin grammatical <ab> passes (p.)")

    # prose German (H1302 class b) flagged; protected spans stay protected
    check(not is_clean("{%думать о%}; mit dem <ab>acc.</ab>: {#aBi#}"),
          "prose German flagged (mit dem)")
    check(is_clean("{%родственник%} «nahe stehend» {#Api#}"),
          "«…» verbatim German quote not flagged")

    # machine flags (P1 ruling 26-07-2026)
    d1 = machine_flags("6) {#полагать, думать#}: {#mfto 'yamiti#}",
                       "6) {%glauben%}: {#mfto 'yamiti#}")
    check(any(f == "D1" for f, _ in d1), "D1: Cyrillic inside {#…#} flagged")
    d3 = machine_flags("1) «пахтать»: {#manTAmi#}", "1) {%quirlen%}: {#manTAmi#}")
    check(any(f == "D3" for f, _ in d3), "D3: gloss drift to «…» flagged")
    d4 = machine_flags("2) {%жечь%}", "2) {%brennen%} {%verbrennen%}")
    check(any(f == "D4" for f, _ in d4), "D4: gloss-slot count mismatch flagged")
    check(machine_flags("3) {%гнать%}: {#ajati#}", "3) {%treiben%}: {#ajati#}") == [],
          "matched slots + clean wrapper pass machine flags")

    print("review_residue_gate selftest " + ("OK" if ok else "FAILED"))
    return 0 if ok else 1


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--queue", default=os.path.join(HERE, "_review_queue.jsonl"))
    ap.add_argument("--store", default=os.environ.get(
        "PWG_RU_STORE", os.path.join(HERE, "pwg_ru_translated.jsonl")))
    ap.add_argument("--json", help="write flagged review_ids + layers here (JSON)")
    a = ap.parse_args()
    if a.selftest:
        raise SystemExit(selftest())
    if a.stats:
        s = stats(a.queue, a.store)
        print("queue rows      : %d" % s["total"])
        print("flagged (German): %d  (%.1f%%)" % (s["flagged"],
              100.0 * s["flagged"] / max(s["total"], 1)))
        print("clean           : %d" % s["clean"])
        print("hits by layer   : %s" % json.dumps(s["hits_by_layer"], ensure_ascii=False))
        if a.json:
            with io.open(a.json, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(s, fh, ensure_ascii=False, indent=2)
            print("wrote", a.json)
        return
    print(__doc__)


if __name__ == "__main__":
    main()
