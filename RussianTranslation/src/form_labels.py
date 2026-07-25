#!/usr/bin/env python
"""Deterministic DE-side form / morphosyntax labels (H1624 form-layer).

Sibling of ``government_census.extract_government`` (Rektion). That extractor
deliberately ignores number, gender, nom/voc, and voice — those are form notes,
not case government. This module extracts them as structured markup from the
same German sense text, never inventing labels and never reading RU.

Axes (curated floor, not every <ab>):

  * **number**   — ``sg.`` / ``du.`` / ``pl.`` in ``<ab>`` (paren or bare)
  * **gender**   — from ``<lex>m.</lex>`` / ``f.`` / ``n.`` / ``m.n.`` … and from
                   unambiguous ``<ab>masc.</ab>`` / ``fem.`` / ``neutr.``
                   (bare ``<ab>n.</ab>`` is NOT treated as gender: too often "note")
  * **case_form** — ``nom.`` / ``voc.`` (citation-form notes; NONGOV for Rektion)
  * **voice**    — ``act.`` / ``med.`` / ``pass.``

Usage:
  python src/form_labels.py --selftest
  python src/form_labels.py extract "…DE text…"
"""
from __future__ import annotations

import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Strip citations first — same discipline as government_census.
LS_RE = re.compile(r"<ls\b[^>]*>.*?</ls>", re.S)

# --- number -----------------------------------------------------------------
NUMBER_TOKENS = {
    "sg": "sg", "sg.": "sg",
    "du": "du", "du.": "du",
    "pl": "pl", "pl.": "pl",
}

# --- gender from <lex> (primary) -------------------------------------------
# Token is the full <lex> content, lowercased, trailing dots kept for matching.
LEX_GENDER = {
    "m.": "m",
    "f.": "f",
    "n.": "n",
    "m.n.": "m.n",
    "m.f.": "m.f",
    "f.n.": "f.n",
    "m.f.n.": "m.f.n",
    "masc.": "m",
    "fem.": "f",
    "femin.": "f",
    "neutr.": "n",
}
LEX_RE = re.compile(r"<lex>([^<]+)</lex>", re.I)

# --- gender from unambiguous <ab> only -------------------------------------
GENDER_AB = {
    "masc": "m", "masc.": "m",
    "fem": "f", "fem.": "f",
    "neutr": "n", "neutr.": "n",
}

# --- case form (nom/voc — not Rektion) -------------------------------------
CASE_FORM = {
    "nom": "nom", "nom.": "nom",
    "voc": "voc", "voc.": "voc",
}

# --- voice -----------------------------------------------------------------
VOICE = {
    "act": "act", "act.": "act",
    "med": "med", "med.": "med",
    "pass": "pass", "pass.": "pass",
}

AB_INNER_RE = re.compile(r"<ab\b[^>]*>([^<]+)</ab>", re.I)
# Parenthesized ab group (may hold several joined by und/oder/,)
PAREN_AB_RE = re.compile(
    r"\(\s*((?:<ab\b[^>]*>[^<]+</ab>(?:\s*(?:,|und|oder)\s*)?)+)\s*\)",
    re.I,
)


def _norm_tok(raw: str) -> str:
    return (raw or "").strip().lower()


def _axis_for_ab_token(tok: str):
    """Return (axis, value) or None for one <ab> inner token."""
    t = _norm_tok(tok)
    if not t:
        return None
    # ensure trailing-dot key variants work
    keys = (t, t if t.endswith(".") else t + ".")
    for k in keys:
        if k in NUMBER_TOKENS or t.rstrip(".") in ("sg", "du", "pl"):
            return "number", NUMBER_TOKENS.get(k) or NUMBER_TOKENS.get(t.rstrip(".") + ".") or t.rstrip(".")
        if k in CASE_FORM or t.rstrip(".") in ("nom", "voc"):
            return "case_form", CASE_FORM.get(k) or t.rstrip(".")
        if k in VOICE or t.rstrip(".") in ("act", "med", "pass"):
            return "voice", VOICE.get(k) or t.rstrip(".")
        if k in GENDER_AB or t.rstrip(".") in ("masc", "fem", "neutr"):
            return "gender", GENDER_AB.get(k) or GENDER_AB.get(t.rstrip(".") + ".")
    return None


def extract_form_labels(text: str | None) -> list[dict]:
    """Extract structured form/morph labels from one sense's German text.

    Returns a list of hit dicts (possibly empty)::
      {axis, value, kind, span}

    ``kind`` is ``paren_ab`` | ``bare_ab`` | ``lex``.
    Order follows source appearance (lex first in document order mixed with abs).
    """
    text_nols = LS_RE.sub("", text or "")
    hits: list[dict] = []
    covered_spans: set[tuple[int, int]] = set()

    # 1) <lex> gender (primary gender source in PWG)
    for m in LEX_RE.finditer(text_nols):
        raw = m.group(1).strip()
        key = raw.lower() if raw.endswith(".") else raw.lower() + "."
        # also try exact
        val = LEX_GENDER.get(raw.lower()) or LEX_GENDER.get(key)
        if val is None:
            # multi-part already covered by keys; skip adj./adv./indecl.
            continue
        hits.append({
            "axis": "gender",
            "value": val,
            "kind": "lex",
            "span": m.group(0),
        })
        covered_spans.add((m.start(), m.end()))

    # 2) parenthesized <ab> groups — number / case_form / voice / unambiguous gender
    for m in PAREN_AB_RE.finditer(text_nols):
        inners = AB_INNER_RE.findall(m.group(1))
        for raw in inners:
            av = _axis_for_ab_token(raw)
            if not av:
                continue
            axis, value = av
            hits.append({
                "axis": axis,
                "value": value,
                "kind": "paren_ab",
                "span": m.group(0) if len(inners) == 1 else ("<ab>%s</ab>" % raw.strip()),
            })
        covered_spans.add((m.start(), m.end()))

    # 3) bare (non-paren) <ab> for number / voice / case_form / unambiguous gender
    #    skip tokens already inside a paren group we handled
    for m in AB_INNER_RE.finditer(text_nols):
        # skip if this match sits inside a covered paren span
        if any(s <= m.start() and m.end() <= e for s, e in covered_spans):
            continue
        av = _axis_for_ab_token(m.group(1))
        if not av:
            continue
        axis, value = av
        # rebuild full <ab>…</ab> span from surrounding text if possible
        # m is on the inner group of AB_INNER_RE which only captures content —
        # find the full tag by expanding left/right is fragile; use group via
        # a wider match on the original for span fidelity.
        full = m.group(0)
        # AB_INNER_RE already is the full <ab>…</ab> because of the pattern
        hits.append({
            "axis": axis,
            "value": value,
            "kind": "bare_ab",
            "span": full if full.startswith("<") else ("<ab>%s</ab>" % m.group(1).strip()),
        })

    return hits


def form_labels_summary(hits: list[dict] | None) -> dict:
    """Roll-up helper: {numbers, genders, case_forms, voices} sorted unique lists."""
    hits = hits or []
    out = {"numbers": [], "genders": [], "case_forms": [], "voices": []}
    key = {
        "number": "numbers",
        "gender": "genders",
        "case_form": "case_forms",
        "voice": "voices",
    }
    for h in hits:
        bucket = key.get(h.get("axis") or "")
        if not bucket:
            continue
        v = h.get("value")
        if v and v not in out[bucket]:
            out[bucket].append(v)
    for k in out:
        out[k] = sorted(out[k])
    return out


def selftest() -> None:
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    # number paren
    h = extract_form_labels("{%Gott%} (<ab>pl.</ab>) <ls>ṚV. 1,1,1</ls>.")
    check(any(x["axis"] == "number" and x["value"] == "pl" for x in h), "pl: %r" % h)

    # gender from lex
    h = extract_form_labels("<lex>m.</lex> {%Gott%}")
    check(any(x["axis"] == "gender" and x["value"] == "m" and x["kind"] == "lex" for x in h),
          "lex m: %r" % h)
    h = extract_form_labels("<lex>f.</lex> {%Göttin%}")
    check(any(x["value"] == "f" for x in h), "lex f: %r" % h)
    h = extract_form_labels("<lex>n.</lex> {%Wasser%}")
    check(any(x["value"] == "n" for x in h), "lex n: %r" % h)
    h = extract_form_labels("<lex>m.n.</lex> {%x%}")
    check(any(x["value"] == "m.n" for x in h), "lex m.n: %r" % h)
    # adj. is not gender
    h = extract_form_labels("<lex>adj.</lex> {%gross%}")
    check(not any(x["axis"] == "gender" for x in h), "adj not gender: %r" % h)

    # case form nom/voc (NOT government)
    h = extract_form_labels("{%Gott%} (<ab>voc.</ab>) auch so.")
    check(any(x["axis"] == "case_form" and x["value"] == "voc" for x in h), "voc: %r" % h)
    h = extract_form_labels("(<ab>Nom.</ab>)")
    check(any(x["value"] == "nom" for x in h), "Nom cap: %r" % h)

    # voice
    h = extract_form_labels("(<ab>med.</ab>) {%sich freuen%}")
    check(any(x["axis"] == "voice" and x["value"] == "med" for x in h), "med: %r" % h)
    h = extract_form_labels("<ab>pass.</ab> {#x#}")
    check(any(x["value"] == "pass" for x in h), "pass bare: %r" % h)

    # number bare (not only paren)
    h = extract_form_labels("<ab>sg.</ab> {%der Eine%}")
    check(any(x["value"] == "sg" for x in h), "sg bare: %r" % h)
    h = extract_form_labels("<ab>Du.</ab>")
    check(any(x["value"] == "du" for x in h), "Du cap: %r" % h)

    # Rektion cases must NOT appear here
    h = extract_form_labels("{%sich heften%} (<ab>loc.</ab>)")
    check(not any(x["value"] == "loc" for x in h), "loc not form: %r" % h)
    h = extract_form_labels("(<ab>Instr.</ab>)")
    check(h == [] or not any(x["axis"] == "case_form" and x["value"] == "instr" for x in h),
          "instr not form: %r" % h)

    # bare <ab>n.</ab> is NOT gender (ambiguous note vs neuter)
    h = extract_form_labels("<ab>n.</ab> {%etwas%}")
    check(not any(x["axis"] == "gender" for x in h), "bare n. not gender: %r" % h)

    # combined card
    de = ("<lex>m.</lex> {%Gott%} (<ab>pl.</ab>) <ls>ṚV. 1,1</ls>. "
          "(<ab>voc.</ab>) auch so. <ab>med.</ab>")
    h = extract_form_labels(de)
    summ = form_labels_summary(h)
    check(summ["genders"] == ["m"], "summ gender: %r" % summ)
    check(summ["numbers"] == ["pl"], "summ number: %r" % summ)
    check(summ["case_forms"] == ["voc"], "summ case: %r" % summ)
    check(summ["voices"] == ["med"], "summ voice: %r" % summ)

    # ls stripped — fake pl. inside ls must not fire
    h = extract_form_labels("<ls>pl. 1,1</ls> plain")
    check(not any(x["axis"] == "number" for x in h), "ls strip: %r" % h)

    if fails:
        for f in fails:
            print("FAIL:", f, file=sys.stderr)
        sys.exit(1)
    print("form_labels --selftest: OK (%d checks)" % 16)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    if sys.argv[1] in ("--selftest", "selftest"):
        selftest()
        return
    if sys.argv[1] == "extract" and len(sys.argv) > 2:
        import json
        print(json.dumps(extract_form_labels(sys.argv[2]), ensure_ascii=False, indent=2))
        return
    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    main()
