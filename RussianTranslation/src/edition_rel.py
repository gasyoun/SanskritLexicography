#!/usr/bin/env python
"""Edition-relationship flags for DE subcards (H1624 G4 / H180 typology).

Deterministic join of the ADDENDA_TYPOLOGY / relationships_rollup machine classes
onto each store/portrait sense as structured ``edition_rel`` — without rewriting
DE text and without wiping the store.

Subtypes (rollup classes; display names from H180 sheets are optional later)::

  base            — PWG skeleton layer
  restate         — PW abridging restatement
  pw_correct      — PW gender/form correction vs PWG
  sch_star        — SCH additive * sense
  derived_sense   — preverb/caus/desid grammar-derived (sch/pwkvn)
  a2a             — PWKVN addenda-to-addenda
  nws_at_sense    — NWS additive (German)
  foreign_fragment— NWS non-German fragment
  unknown         — non-pwg layer not classified

Shape (stored on the sense row)::

  {
    "subtype": str,
    "op": str,
    "direction": str,          # additive | abridging | base
    "layer": str,              # pwg | pw | sch | pwkvn | nws
    "source_layers": [str],    # same as layer for now; list for multi-source future
    "insertion_point": {...} | null,
    "confidence": "rule",
    "evidence": str
  }

Usage:
  python src/edition_rel.py --selftest
  python src/edition_rel.py classify --layer pw --sense-tag 1 --de "..."
"""
from __future__ import annotations

import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# grammar-derivation markers in a sense_tag → derived sub-sense (caus/desid/preverb)
DERIV_RE = re.compile(
    r"caus|desid|\bmit\b|\bdes\.\b|\banu\b|_(pat|caus|desid)|\bpra\b", re.I
)

GENDER = {"m.", "n.", "f.", "mn.", "nm.", "mf.", "fn.", "mfn."}
LEX_RE = re.compile(r"<lex>(.*?)</lex>")

DE_MARK = re.compile(
    r"\b(der|die|das|und|ist|mit|ein|eine|nicht|von|zu|auf|sich|dem|den)\b", re.I
)
EN_MARK = re.compile(r"\b(the|to|of|and|in|with|is|for|from|by|as)\b")
FR_MARK = re.compile(r"\b(le|la|les|du|des|une|avec|dans|pour|est|qui)\b")
LA_MARK = re.compile(r"\b(et|cum|ad|vel|non|est|quod|sunt|atque|sive)\b")
TAG_RE = re.compile(r"<[^>]+>")
BRACE_RE = re.compile(r"\{%.*?%\}")

# Machine classes listed in relationships_rollup.tsv / ADDENDA_TYPOLOGY §3
SUBTYPES = (
    "base",
    "restate",
    "pw_correct",
    "sch_star",
    "derived_sense",
    "a2a",
    "nws_at_sense",
    "foreign_fragment",
    "unknown",
)


def strip_markup(s: str) -> str:
    s = BRACE_RE.sub(" ", s or "")
    s = TAG_RE.sub(" ", s)
    return s


def guess_lang(de_text: str) -> str:
    """Return 'de' | 'en' | 'fr' | 'la' for an NWS source fragment (heuristic)."""
    t = strip_markup(de_text)
    scores = {
        "de": len(DE_MARK.findall(t)),
        "en": len(EN_MARK.findall(t)),
        "fr": len(FR_MARK.findall(t)),
        "la": len(LA_MARK.findall(t)),
    }
    best = max(scores, key=scores.get)
    if best != "de" and scores[best] >= 2 and scores[best] > scores["de"]:
        return best
    return "de"


def lead_int(sense_tag) -> str | None:
    m = re.match(r"\s*(\d+)", str(sense_tag or ""))
    return m.group(1) if m else None


def homonym_of(subcard: str) -> str:
    m = re.search(r"~~(h\d+)", subcard or "")
    return m.group(1) if m else "h0"


def lex_genders(text: str) -> set:
    toks = {t.strip() for t in LEX_RE.findall(text or "") if t.strip()}
    return {t for t in toks if t in GENDER}


def classify_edition_rel(
    layer: str | None,
    sense_tag=None,
    de: str | None = None,
    *,
    key1: str | None = None,
    subcard: str | None = None,
    pwg_genders: set | None = None,
    confidence: str = "rule",
) -> dict:
    """Classify one subcard/sense into an edition_rel record.

    ``pwg_genders`` — optional set of PWG ``<lex>`` gender tokens for the same
    key1/hom/sense (enables ``pw_correct``). Without it, PW defaults to ``restate``.
    """
    layer = (layer or "pwg").lower()
    st = str(sense_tag or "")
    si = lead_int(st)
    hom = homonym_of(subcard or "")
    key1 = key1 or ""
    de = de or ""

    if layer == "pwg":
        return {
            "subtype": "base",
            "op": "base",
            "direction": "base",
            "layer": "pwg",
            "source_layers": ["pwg"],
            "insertion_point": None,
            "confidence": confidence,
            "evidence": "PWG skeleton layer",
        }

    target_sense = si if si else "*new"
    anchor = "sense"
    op = "add"
    direction = "additive"
    subtype = "unknown"
    evidence = ""
    extra: dict = {}

    if layer == "sch":
        subtype = "derived_sense" if DERIV_RE.search(st) else "sch_star"
        evidence = "SCH additive; sense_tag=%r" % st
    elif layer == "pwkvn":
        if DERIV_RE.search(st):
            subtype = "derived_sense"
            evidence = "PWKVN grammar-derived; sense_tag=%r" % st
        else:
            subtype = "a2a"
            op = "relocate"
            evidence = "PWKVN Nachtraege-to-Nachtraege (a2a); sense_tag=%r" % st
    elif layer == "nws":
        lang = guess_lang(de)
        if lang != "de":
            subtype = "foreign_fragment"
            extra["source_lang"] = lang
            extra["needs_ru_from_%s" % lang] = True
            evidence = "NWS fragment in %s (heuristic); sense_tag=%r" % (lang.upper(), st)
        else:
            subtype = "nws_at_sense"
            evidence = "NWS additive at PWG sense %s; sense_tag=%r" % (target_sense, st)
        if re.match(r"\s*nws", st, re.I):
            target_sense = "*new"
    elif layer == "pw":
        direction = "abridging"
        pw_g = lex_genders(de)
        if pwg_genders and pw_g and pwg_genders.isdisjoint(pw_g):
            subtype = "pw_correct"
            op = "correct"
            anchor = "grammar"
            evidence = "gender change PWG %s -> PW %s at sense %s" % (
                sorted(pwg_genders), sorted(pw_g), si)
        else:
            subtype = "restate"
            op = "restate"
            evidence = "PW abridging restatement; sense_tag=%r" % st
    else:
        subtype = "unknown"
        evidence = "unclassified layer=%r" % layer

    rel = {
        "subtype": subtype,
        "op": op,
        "direction": direction,
        "layer": layer,
        "source_layers": [layer],
        "insertion_point": {
            "key1": key1,
            "homonym": hom,
            "target_sense": target_sense,
            "anchor": anchor,
        },
        "confidence": confidence,
        "evidence": evidence,
    }
    rel.update(extra)
    return rel


def edition_rel_for_row(row: dict, pwg_gender_index: dict | None = None) -> dict:
    """Classify a store-shaped row. Optional index: (key1, hom, sense_int) -> gender set."""
    layer = row.get("layer") or "pwg"
    subcard = row.get("subcard") or ""
    key1 = row.get("key1") or ""
    st = row.get("sense_tag")
    si = lead_int(st)
    pwg_g = None
    if pwg_gender_index is not None and layer == "pw" and si:
        pwg_g = pwg_gender_index.get((key1, homonym_of(subcard), si))
    return classify_edition_rel(
        layer,
        st,
        row.get("de"),
        key1=key1,
        subcard=subcard,
        pwg_genders=pwg_g,
    )


def build_pwg_gender_index(rows) -> dict:
    """Map (key1, homonym, sense_int) -> set of PWG gender tokens."""
    idx: dict = {}
    for d in rows:
        if d.get("layer") != "pwg":
            continue
        si = lead_int(d.get("sense_tag"))
        if not si:
            continue
        key = (d.get("key1") or "", homonym_of(d.get("subcard") or ""), si)
        g = lex_genders(d.get("de") or "")
        if g:
            idx.setdefault(key, set()).update(g)
    return idx


def selftest() -> None:
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    # base PWG
    r = classify_edition_rel("pwg", "1", "{%gehen%}")
    check(r["subtype"] == "base" and r["layer"] == "pwg", "base: %r" % r)
    check(r["source_layers"] == ["pwg"], "source_layers: %r" % r)

    # PW restate (no gender conflict)
    r = classify_edition_rel("pw", "1", "<lex>m.</lex> {%gehen%}", key1="gam",
                             subcard="gam~~h0_zz_pw01",
                             pwg_genders={"m."})
    check(r["subtype"] == "restate" and r["op"] == "restate", "restate: %r" % r)
    check(r["direction"] == "abridging", "pw direction: %r" % r)

    # PW correct (gender change)
    r = classify_edition_rel("pw", "1", "<lex>f.</lex> {%x%}", key1="x",
                             subcard="x~~h0_zz_pw01", pwg_genders={"m."})
    check(r["subtype"] == "pw_correct" and r["op"] == "correct", "pw_correct: %r" % r)

    # SCH star vs derived
    r = classify_edition_rel("sch", "2", "{%neu%}", subcard="a~~h0_zz_sch")
    check(r["subtype"] == "sch_star", "sch_star: %r" % r)
    r = classify_edition_rel("sch", "anu_desid", "{%einstimmen%}", subcard="a~~h0_zz_sch")
    check(r["subtype"] == "derived_sense", "sch derived: %r" % r)

    # PWKVN a2a vs derived
    r = classify_edition_rel("pwkvn", "3", "{%x%}", subcard="a~~h0_zz_pwkvn")
    check(r["subtype"] == "a2a" and r["op"] == "relocate", "a2a: %r" % r)
    r = classify_edition_rel("pwkvn", "ava_caus", "{%x%}", subcard="a~~h0_zz_pwkvn")
    check(r["subtype"] == "derived_sense", "pwkvn derived: %r" % r)

    # NWS
    r = classify_edition_rel("nws", "2", "der und die mit sich", subcard="a~~h0_zz_nws")
    check(r["subtype"] == "nws_at_sense", "nws_at_sense: %r" % r)
    check(r["insertion_point"]["target_sense"] == "2", "nws target: %r" % r)
    r = classify_edition_rel(
        "nws", "NWS-1",
        "the of and in with is for from by as divide",
        subcard="cid~~h0_zz_nws00")
    check(r["subtype"] == "foreign_fragment", "foreign_fragment: %r" % r)
    check(r.get("source_lang") == "en", "source_lang: %r" % r)

    # DE not rewritten (caller responsibility; we only return metadata)
    de = "{%Feuer%} (<ab>loc.</ab>)"
    classify_edition_rel("pw", "1", de)
    check(de == "{%Feuer%} (<ab>loc.</ab>)", "de immutable")

    # row helper + gender index
    rows = [
        {"key1": "x", "subcard": "x~~h0_00_pwg00", "layer": "pwg",
         "sense_tag": "1", "de": "<lex>m.</lex> {%x%}"},
        {"key1": "x", "subcard": "x~~h0_zz_pw01", "layer": "pw",
         "sense_tag": "1", "de": "<lex>f.</lex> {%x%}"},
    ]
    idx = build_pwg_gender_index(rows)
    rel = edition_rel_for_row(rows[1], idx)
    check(rel["subtype"] == "pw_correct", "index pw_correct: %r" % rel)
    rel0 = edition_rel_for_row(rows[0], idx)
    check(rel0["subtype"] == "base", "index base: %r" % rel0)

    # all rollup subtypes reachable
    seen = {
        classify_edition_rel("pwg", "1")["subtype"],
        classify_edition_rel("pw", "1", "<lex>m.</lex>")["subtype"],
        classify_edition_rel("pw", "1", "<lex>f.</lex>", pwg_genders={"m."})["subtype"],
        classify_edition_rel("sch", "1")["subtype"],
        classify_edition_rel("sch", "pra_caus")["subtype"],
        classify_edition_rel("pwkvn", "1")["subtype"],
        classify_edition_rel("pwkvn", "ava_caus")["subtype"],
        classify_edition_rel("nws", "1", "der die und")["subtype"],
        classify_edition_rel(
            "nws", "1", "the of and in with is for from by as")["subtype"],
    }
    for need in ("base", "restate", "pw_correct", "sch_star", "derived_sense",
                 "a2a", "nws_at_sense", "foreign_fragment"):
        check(need in seen, "missing subtype %s in %r" % (need, seen))

    if fails:
        for f in fails:
            print("FAIL:", f, file=sys.stderr)
        sys.exit(1)
    print("edition_rel --selftest: OK")


def main() -> None:
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    if argv[0] in ("--selftest", "selftest"):
        selftest()
        return
    if argv[0] == "classify":
        import argparse
        import json
        ap = argparse.ArgumentParser()
        ap.add_argument("--layer", required=True)
        ap.add_argument("--sense-tag", default="")
        ap.add_argument("--de", default="")
        ap.add_argument("--key1", default="")
        ap.add_argument("--subcard", default="")
        args = ap.parse_args(argv[1:])
        print(json.dumps(
            classify_edition_rel(
                args.layer, args.sense_tag, args.de,
                key1=args.key1, subcard=args.subcard),
            ensure_ascii=False, indent=2))
        return
    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    main()
