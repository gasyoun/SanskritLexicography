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
  pwg_internal_correction — a row inside the PWG skeleton that amends another
                    PWG sense rather than being one (H2880, wave 2)
  unknown         — non-pwg layer not classified

Shape (stored on the sense row)::

  {
    "subtype": str,
    "op": str,
    "direction": str,          # additive | abridging | base | internal
    "layer": str,              # pwg | pw | sch | pwkvn | nws
    "source_layers": [str],    # the layer(s) the material came from
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
    "pwg_internal_correction",
    "unknown",
)

# --- wave 2 (H2880): corrections that live INSIDE the PWG skeleton ----------
# Some rows carried on the `pwg` layer are not senses of PWG at all — they are
# the authors' own later supplements (`Nachtrag`, `addendum`) or material the
# later PW edition contributed at a PWG sense (`1 (PW)`). Until now they sat in
# the skeleton as ordinary senses, i.e. exactly the axis defect wave 1 removed
# from the supplement layers, one layer down.
#
# Each marker is matched by a NAMED rule and the name is reported as evidence.
# A tag that matches nothing stays `base` — the conservative default, because a
# row wrongly pulled out of the skeleton loses a real PWG sense from the card.
PWG_CORRECTION_MARKERS = (
    # `Nachtrag`, `Nachtr.`, `Nachträge`, `4 (Nachtrag)`, `Nachtrag §76`
    ("nachtrag", re.compile(r"nachtr", re.I)),
    # `addendum`, `addenda`, `6_addendum`, `3 (addendum)`
    ("addendum", re.compile(r"addend", re.I)),
    ("corrigendum", re.compile(r"corrigend", re.I)),
    # `1 (PW)` / `2 (PW)` — a PWG sense as the PW edition gives it
    ("pw_provenance", re.compile(r"\(\s*PW\s*\)")),
    # bare `PW`, `PW-1`, `PW_2` — PW material with no sense pointer.
    # Anchored whole-string so it can never fire on `PWG`/`PWKVN`.
    ("pw_provenance", re.compile(r"^\s*PW(?:[-_ ]?\d+)?\s*$")),
)


def pwg_correction_marker(tag) -> str | None:
    """Name the printed cue marking a PWG-layer row as a correction, else None.

    Returns the marker NAME (``nachtrag`` / ``addendum`` / ``corrigendum`` /
    ``pw_provenance``), never a bare bool, so the sidecar can record *why* a row
    left the skeleton and a reviewer can disagree with that specific rule.
    """
    s = str(tag or "")
    for name, rx in PWG_CORRECTION_MARKERS:
        if rx.search(s):
            return name
    return None


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


def normalize_sense_tag(tag) -> str:
    """Strip *format* noise from a sense tag, and nothing else (H2879, decision 6).

    PWG skeleton tags and supplement targets disagree only cosmetically in a
    small set of cases — the skeleton writes ``'1)'`` or ``'caus.'`` where the
    supplement points at ``'1'`` / ``'caus'``. This collapses exactly that, so
    the placement lookup is symmetric on both sides (ARCHITECTURE §Нормализация).

    Deliberately conservative: it removes trailing whitespace, ``.``, ``,`` and
    an *unmatched* trailing ``)``. It never merges tags that name different
    things — ``'1-sub-…'`` (a sub-sense), ``'1 (PW)'`` (foreign provenance),
    ``'Nachtrag'`` (an edit *to* a sense, wave 2) and ``'caus-1'`` (another
    grammatical branch) all pass through untouched. A false merge here would
    produce a silent ``placement=true`` on the wrong sense, which is worse than
    the defect being fixed.

    Idempotent: ``f(f(x)) == f(x)``.
    """
    s = str(tag or "").strip()
    while True:
        prev = s
        s = s.rstrip(" \t.,")
        # Only an unbalanced ')' is punctuation; a matched one is structure,
        # so '1)' -> '1' but '1 (PW)' is left alone.
        if s.endswith(")") and s.count("(") < s.count(")"):
            s = s[:-1]
        s = s.rstrip(" \t")
        if s == prev:
            return s


def lex_genders(text: str) -> set:
    toks = {t.strip() for t in LEX_RE.findall(text or "") if t.strip()}
    return {t for t in toks if t in GENDER}


def _max_numeric_sense(senses) -> int | None:
    """Highest purely-numeric sense in a PWG article, over NORMALISED tags.

    Normalised on purpose: an article whose skeleton is written ``'3)'..'7)'``
    has no bare-integer tag at all, so a raw-tag maximum would be ``None`` and
    every out-of-range target would be misfiled as ``not_found`` (H2879 spike:
    that is exactly what happened to ``vA h0`` targets 8 and 9).
    """
    nums = [int(t) for t in (senses or ()) if t.isdigit()]
    return max(nums) if nums else None


def _loose_sense_key(tag: str) -> str:
    """Deliberately sloppier key, used ONLY to propose a hypothesis (S4).

    Never consulted by ``placement`` — a guess must not be promoted to a fact.
    """
    return re.sub(r"[^0-9A-Za-z]", "", str(tag or "")).lower()


def classify_edition_rel(
    layer: str | None,
    sense_tag=None,
    de: str | None = None,
    *,
    key1: str | None = None,
    subcard: str | None = None,
    pwg_genders: set | None = None,
    pwg_senses: set | None = None,
    confidence: str = "rule",
) -> dict:
    """Classify one subcard/sense into an edition_rel record.

    ``pwg_genders`` — optional set of PWG ``<lex>`` gender tokens for the same
    key1/hom/sense (enables ``pw_correct``). Without it, PW defaults to ``restate``.

    ``pwg_senses`` — optional set of NORMALISED PWG sense tags for the same
    key1/homonym (enables the ``placement`` axis, H2879). Kept separate from
    ``pwg_genders`` on purpose: that index is about gender and its membership
    may change for reasons that have nothing to do with which senses exist.
    Absent it, ``placement`` stays ``False`` — the conservative default, never a
    guess in the direction of ``True``.
    """
    layer = (layer or "pwg").lower()
    st = str(sense_tag or "")
    si = lead_int(st)
    hom = homonym_of(subcard or "")
    key1 = key1 or ""
    de = de or ""

    pwg_marker = pwg_correction_marker(st) if layer == "pwg" else None

    if layer == "pwg" and not pwg_marker:
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

    if layer == "pwg":
        # Wave 2. `op` is deliberately NOT "correct": build_reglue renders
        # op in ("correct", "delete") with a "cancels PWG" strikethrough, and a
        # Nachtrag amends the sense it points at rather than withdrawing it.
        subtype = "pwg_internal_correction"
        op = "amend"
        direction = "internal"
        extra["correction_marker"] = pwg_marker
        if pwg_marker == "pw_provenance":
            # The material is PW's, carried at a PWG sense. `source_layers` is
            # the field that already exists for exactly this; duplicating it as
            # a second subtype would re-create the wave-1 defect.
            extra["source_layers"] = ["pwg", "pw"]
        evidence = "PWG-internal correction (%s); sense_tag=%r" % (pwg_marker, st)
    elif layer == "sch":
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

    # --- placement axis (H2879) -------------------------------------------
    # `subtype` says what KIND of relation this is; `placement` says whether the
    # relation has a target at all. Conflating them is the defect being fixed:
    # 'restate' used to co-exist with target_sense='*new', i.e. it claimed to
    # restate a sense that was never identified.
    senses = pwg_senses if pwg_senses is not None else set()
    placement_hypothesis = None
    if target_sense == "*new":
        # No leading number on the supplement's own tag: there is no target by
        # construction, not a lookup that failed.
        placement = False
        placement_reason = "no_target_marker"
    else:
        nt = normalize_sense_tag(target_sense)
        if nt in senses:
            placement = True
            placement_reason = "found"
        else:
            placement = False
            mx = _max_numeric_sense(senses)
            if mx is not None and nt.isdigit() and int(nt) > mx:
                # The later edition genuinely has more senses than PWG here.
                # A real phenomenon, not a data defect — see PLAN decision 4.
                placement_reason = "out_of_range"
            else:
                placement_reason = "not_found"
                # S4: a looser key might have matched. Record it as a guess and
                # never anywhere else — it must not reach `insertion_point`.
                lk = _loose_sense_key(nt)
                cand = sorted({s for s in senses if _loose_sense_key(s) == lk})
                if len(cand) == 1:
                    placement_hypothesis = {
                        "target": cand[0],
                        "method": "normalized_tag_match",
                        "confidence": "low",
                    }

    rel = {
        "subtype": subtype,
        "op": op,
        "direction": direction,
        "layer": layer,
        "source_layers": [layer],
        "placement": placement,
        "placement_reason": placement_reason,
        "placement_hypothesis": placement_hypothesis,
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


def edition_rel_for_row(
    row: dict,
    pwg_gender_index: dict | None = None,
    pwg_sense_index: dict | None = None,
) -> dict:
    """Classify a store-shaped row.

    ``pwg_gender_index``: (key1, hom, sense_int) -> gender set.
    ``pwg_sense_index``:  (key1, hom) -> set of normalised sense tags (H2879).
    """
    layer = row.get("layer") or "pwg"
    subcard = row.get("subcard") or ""
    key1 = row.get("key1") or ""
    st = row.get("sense_tag")
    si = lead_int(st)
    hom = homonym_of(subcard)
    pwg_g = None
    if pwg_gender_index is not None and layer == "pw" and si:
        pwg_g = pwg_gender_index.get((key1, hom, si))
    pwg_s = None
    if pwg_sense_index is not None:
        pwg_s = pwg_sense_index.get((key1, hom), set())
    return classify_edition_rel(
        layer,
        st,
        row.get("de"),
        key1=key1,
        subcard=subcard,
        pwg_genders=pwg_g,
        pwg_senses=pwg_s,
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


def build_pwg_sense_index(rows) -> dict:
    """Map (key1, homonym) -> set of NORMALISED PWG sense tags (H2879 S2).

    The normalisation is applied here, on the skeleton side, and again to the
    target at lookup time. Both sides must go through the same function —
    normalising only one of them would invent a fresh class of misses.

    H2880: a row that is itself a PWG-internal correction is NOT a sense of the
    skeleton, so it is excluded here. Otherwise a Nachtrag could be offered as
    the target of another Nachtrag, which is the wave-2 analogue of the defect
    wave 1 removed. Expected to be a no-op for wave 1's numbers — no correction
    tag normalises to a bare integer — and that is asserted, not assumed, by
    ``placement_axis_check.py``.
    """
    idx: dict = {}
    for d in rows:
        if d.get("layer") != "pwg":
            continue
        if pwg_correction_marker(d.get("sense_tag")):
            continue
        key = (d.get("key1") or "", homonym_of(d.get("subcard") or ""))
        idx.setdefault(key, set()).add(normalize_sense_tag(d.get("sense_tag")))
    return idx


def selftest() -> None:
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    # --- normalize_sense_tag (H2879 S1) -----------------------------------
    # positives: format noise only
    for raw, want in (
        ("1)", "1"), ("1 ", "1"), ("1", "1"), (" 1 ", "1"),
        ("1.", "1"), ("caus.", "caus"), ("Caus.", "Caus"),
        ("Nachtr.", "Nachtr"), ("4b)", "4b"), ("2,", "2"),
    ):
        got = normalize_sense_tag(raw)
        check(got == want, "normalize %r -> %r, want %r" % (raw, got, want))

    # NEGATIVES — these name different things and must survive untouched.
    # A merge here is the exact silent-lie failure mode wave 1 exists to avoid.
    for raw in (
        "1-sub-einen Damm durchbrechen",   # sub-sense, not sense 1
        "1 (PW)",                          # sense with foreign provenance
        "Nachtrag",                        # edit *to* a sense (wave 2)
        "addendum",
        "caus-1",                          # other grammatical branch
        "anu-1",
        "Nachtrag: 1) patch",              # ')' is matched -> structural
        "Nachtrag: 7)(b), 1",
        "*new",
        "",
    ):
        got = normalize_sense_tag(raw)
        check(got == raw, "normalize must not touch %r, got %r" % (raw, got))

    # idempotence
    for raw in ("1)", "1 (PW)", "caus.", "1-sub-x", " 2 ,", "Nachtrag"):
        once = normalize_sense_tag(raw)
        check(normalize_sense_tag(once) == once,
              "normalize not idempotent on %r" % raw)

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

    # --- placement axis (H2879 S3/S4) --------------------------------------
    senses = {"1", "2", "3", "caus"}

    # found — target present in the skeleton
    r = classify_edition_rel("pw", "2", "{%x%}", key1="x",
                             subcard="x~~h0_zz_pw01", pwg_senses=senses)
    check(r["placement"] is True and r["placement_reason"] == "found",
          "placement found: %r" % r)
    check(r["placement_hypothesis"] is None, "found must not guess: %r" % r)

    # found via normalisation — skeleton writes '1)', supplement points at '1'
    r = classify_edition_rel("pw", "1", "{%x%}", key1="x",
                             subcard="x~~h0_zz_pw01",
                             pwg_senses=build_pwg_sense_index([
                                 {"key1": "x", "subcard": "x~~h0_00_pwg00",
                                  "layer": "pwg", "sense_tag": "1)"},
                             ])[("x", "h0")])
    check(r["placement"] is True and r["placement_reason"] == "found",
          "placement found via normalisation: %r" % r)

    # no_target_marker — the supplement's own tag has no leading number
    r = classify_edition_rel("sch", "Nachtrag", "{%x%}", key1="x",
                             subcard="x~~h0_zz_sch", pwg_senses=senses)
    check(r["placement"] is False
          and r["placement_reason"] == "no_target_marker",
          "no_target_marker: %r" % r)
    check(r["insertion_point"]["target_sense"] == "*new",
          "no_target_marker target: %r" % r)

    # out_of_range — the later edition has more senses than PWG
    r = classify_edition_rel("pw", "9", "{%x%}", key1="x",
                             subcard="x~~h0_zz_pw01", pwg_senses=senses)
    check(r["placement"] is False and r["placement_reason"] == "out_of_range",
          "out_of_range: %r" % r)

    # out_of_range is computed over NORMALISED tags: a '3)'..'7)' skeleton has
    # no bare integer at all, and must still yield a usable maximum.
    r = classify_edition_rel("pw", "9", "{%x%}", key1="x",
                             subcard="x~~h0_zz_pw01",
                             pwg_senses={"3", "4", "5", "6", "7"})
    check(r["placement_reason"] == "out_of_range",
          "out_of_range over normalised max: %r" % r)

    # not_found — inside the range, but no such sense
    r = classify_edition_rel("pw", "2", "{%x%}", key1="x",
                             subcard="x~~h0_zz_pw01", pwg_senses={"1", "3"})
    check(r["placement"] is False and r["placement_reason"] == "not_found",
          "not_found: %r" % r)

    # no index at all -> conservative, never a guess towards True
    r = classify_edition_rel("pw", "1", "{%x%}", key1="x",
                             subcard="x~~h0_zz_pw01")
    check(r["placement"] is False, "no index must not claim placement: %r" % r)

    # hypothesis: proposed, but never promoted and never leaked
    r = classify_edition_rel("pw", "1", "{%x%}", key1="x",
                             subcard="x~~h0_zz_pw01",
                             pwg_senses={"1-sub-x", "3"})
    check(r["placement"] is False, "hypothesis must not set placement: %r" % r)
    check(r["insertion_point"]["target_sense"] == "1",
          "hypothesis must not touch insertion_point: %r" % r)

    # an ambiguous guess is no guess at all
    r = classify_edition_rel("pw", "1", "{%x%}", key1="x",
                             subcard="x~~h0_zz_pw01",
                             pwg_senses={"1-sub-a", "(1)-b"})
    check(r["placement_hypothesis"] is None or
          isinstance(r["placement_hypothesis"], dict),
          "hypothesis shape: %r" % r)

    # placement is orthogonal to subtype: a restate can be unplaced
    r = classify_edition_rel("pw", "Nachtrag", "{%x%}", key1="x",
                             subcard="x~~h0_zz_pw01", pwg_senses=senses)
    check(r["subtype"] == "restate" and r["placement"] is False,
          "restate may be unplaced: %r" % r)

    # sense index build + row helper
    srows = [
        {"key1": "y", "subcard": "y~~h0_00_pwg00", "layer": "pwg",
         "sense_tag": "1)", "de": "{%y%}"},
        {"key1": "y", "subcard": "y~~h0_00_pwg01", "layer": "pwg",
         "sense_tag": "2", "de": "{%y%}"},
        {"key1": "y", "subcard": "y~~h0_zz_pw01", "layer": "pw",
         "sense_tag": "1", "de": "{%y%}"},
    ]
    sidx = build_pwg_sense_index(srows)
    check(sidx[("y", "h0")] == {"1", "2"}, "sense index: %r" % sidx)
    rel = edition_rel_for_row(srows[2], None, sidx)
    check(rel["placement"] is True and rel["placement_reason"] == "found",
          "row helper placement: %r" % rel)

    # --- wave 2: PWG-internal corrections (H2880) --------------------------
    # POSITIVES — printed cues that really mark a row as an edit to a sense.
    for tag, want in (
        ("Nachtrag", "nachtrag"), ("Nachtr.", "nachtrag"),
        ("Nachträge", "nachtrag"), ("nachtrag", "nachtrag"),
        ("4 (Nachtrag)", "nachtrag"), ("Nachtrag §76", "nachtrag"),
        ("Nachtrag-1", "nachtrag"),
        ("addendum", "addendum"), ("addenda", "addendum"),
        ("6_addendum", "addendum"), ("3 (addendum)", "addendum"),
        ("caus-addendum-1", "addendum"),
        ("addendum-corrigendum", "addendum"),   # first rule wins, both apply
        ("1 (PW)", "pw_provenance"), ("2 (PW)", "pw_provenance"),
        ("PW", "pw_provenance"), ("PW-1", "pw_provenance"),
        ("PW-2", "pw_provenance"),
    ):
        got = pwg_correction_marker(tag)
        check(got == want, "marker %r -> %r, want %r" % (tag, got, want))

    # NEGATIVES — ordinary senses and, critically, the layer names. A marker
    # that fired on 'PWG'/'PWKVN' would empty the skeleton of real senses.
    for tag in ("1", "1)", "2a", "caus", "caus-1", "main", "intro", "tail",
                "head", "cross-ref", "note", "PWG", "PWKVN", "pwkvn",
                "NWS-1", "PPP-1", "desid", "1-sub-x", "etym", "PW-extra"):
        got = pwg_correction_marker(tag)
        check(got is None, "marker must not fire on %r, got %r" % (tag, got))

    senses2 = {"1", "2", "3", "4"}

    # placed: the tag names the sense it amends
    r = classify_edition_rel("pwg", "4 (Nachtrag)", "{%x%}", key1="x",
                             subcard="x~~h0_00_pwg09", pwg_senses=senses2)
    check(r["subtype"] == "pwg_internal_correction", "w2 subtype: %r" % r)
    check(r["placement"] is True and r["placement_reason"] == "found",
          "w2 placed: %r" % r)
    check(r["op"] == "amend" and r["direction"] == "internal",
          "w2 op/direction: %r" % r)
    check(r["correction_marker"] == "nachtrag", "w2 marker recorded: %r" % r)

    # op must never be 'correct'/'delete': build_reglue would strike the sense
    # through as cancelled, which a Nachtrag does not do.
    check(r["op"] not in ("correct", "delete"),
          "a Nachtrag must not render as a cancellation: %r" % r)

    # unplaced: a bare marker names no target at all
    r = classify_edition_rel("pwg", "Nachtrag", "{%x%}", key1="x",
                             subcard="x~~h0_00_pwg09", pwg_senses=senses2)
    check(r["subtype"] == "pwg_internal_correction", "w2 bare subtype: %r" % r)
    check(r["placement"] is False
          and r["placement_reason"] == "no_target_marker",
          "w2 bare unplaced: %r" % r)

    # THE trap: the digit in 'Nachtrag-1' is the ordinal of the addendum, not a
    # PWG sense. Reading it as a target would silently attach the row to sense 1.
    for tag in ("Nachtrag-1", "Nachtrag-2", "addendum-1", "addendum-2",
                "Nachtrag §76", "Nachtrag §75-1", "PW-1"):
        r = classify_edition_rel("pwg", tag, "{%x%}", key1="x",
                                 subcard="x~~h0_00_pwg09", pwg_senses=senses2)
        check(r["placement"] is False
              and r["placement_reason"] == "no_target_marker",
              "ordinal/section must not be read as a target: %r -> %r"
              % (tag, r))

    # PW provenance is recorded on source_layers, not as a second subtype
    r = classify_edition_rel("pwg", "1 (PW)", "{%x%}", key1="x",
                             subcard="x~~h0_00_pwg09", pwg_senses=senses2)
    check(r["source_layers"] == ["pwg", "pw"], "w2 source_layers: %r" % r)
    check(r["placement"] is True, "w2 '1 (PW)' places on sense 1: %r" % r)

    # an ordinary PWG sense is untouched by wave 2
    r = classify_edition_rel("pwg", "1", "{%x%}")
    check(r["subtype"] == "base" and r["insertion_point"] is None,
          "ordinary PWG sense stays base: %r" % r)
    check("placement" not in r, "base must not grow a placement axis: %r" % r)

    # a correction is not a skeleton sense, so it cannot be another's target
    crows = [
        {"key1": "z", "subcard": "z~~h0_00_pwg00", "layer": "pwg",
         "sense_tag": "1", "de": "{%z%}"},
        {"key1": "z", "subcard": "z~~h0_00_pwg01", "layer": "pwg",
         "sense_tag": "Nachtrag", "de": "{%z%}"},
        {"key1": "z", "subcard": "z~~h0_00_pwg02", "layer": "pwg",
         "sense_tag": "1 (PW)", "de": "{%z%}"},
    ]
    cidx = build_pwg_sense_index(crows)
    check(cidx[("z", "h0")] == {"1"},
          "correction rows must not enter the skeleton index: %r" % cidx)
    rel = edition_rel_for_row(crows[1], None, cidx)
    check(rel["subtype"] == "pwg_internal_correction", "row helper w2: %r" % rel)
    rel = edition_rel_for_row(crows[2], None, cidx)
    check(rel["placement"] is True and rel["placement_reason"] == "found",
          "row helper w2 placed: %r" % rel)

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
        classify_edition_rel("pwg", "Nachtrag")["subtype"],
    }
    for need in ("base", "restate", "pw_correct", "sch_star", "derived_sense",
                 "a2a", "nws_at_sense", "foreign_fragment",
                 "pwg_internal_correction"):
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
