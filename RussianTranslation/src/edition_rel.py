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
  sch_correct     — SCH emends printed PWG text (`lies`, `Druckfehler`) (H2881, wave 3)
  sch_cancel      — SCH withdraws printed PWG text (`streiche`) (H2881, wave 3)
  derived_sense   — preverb/caus/desid grammar-derived (sch/pwkvn)
  a2a             — PWKVN addenda-to-addenda
  nws_at_sense    — NWS additive (German)
  foreign_fragment— NWS non-German fragment
  pwg_internal_correction — a row inside the PWG skeleton that amends another
                    PWG sense rather than being one (H2880, wave 2)
  unknown         — non-pwg layer not classified

Three of those name a PWG *sense* as the other end of the relation. Since H3752
(wave 5) each has an unplaced twin, used when no target was identified::

  restate_unplaced · nws_at_sense_unplaced · a2a_unplaced

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
    "sch_correct",
    "sch_cancel",
    "derived_sense",
    "a2a",
    "nws_at_sense",
    "foreign_fragment",
    "pwg_internal_correction",
    "unknown",
)

# --- wave 5 (H3752): the label must survive its own attachment result -------
# Issue #1736 measured the residue wave 1 left behind: 4,132 rows labelled
# `restate` ("PW пересказывает этот смысл PWG") while the same row's
# `target_sense` reads `*new` — the pipeline's own marker for "no such sense was
# identified". Wave 1 (H2879) added `placement` beside the label and deliberately
# left the label alone (REGLUE_SPEC §10: "duplicating one fact across two fields
# guarantees they drift apart"). That reasoning is sound about duplication and
# wrong about this field: a reader who takes `subtype` on its own — every sheet
# chip, every rollup row, the "86 % is PWG paraphrase" headline — still reads an
# assertion about a sense that was never found. The wave-5 ruling is therefore
# NOT "add a second field": it is that `subtype` becomes a FUNCTION of the
# placement result, computed once, at one site, immediately below the placement
# block. Two fields that are computed from the same variable in the same
# expression cannot drift; `placement_label_consistent()` pins that as an
# invariant and `placement_axis_check.py` gate W5a asserts it over the corpus.
#
# Only labels that name a PWG SENSE as the other end of the relation take the
# twin. The exclusions are deliberate, and each one is a different mechanism:
#   * `sch_star`, `derived_sense`, `foreign_fragment` — additive. They assert a
#     new sense, not a relation TO one; having no target is their normal state.
#   * `pw_correct` — grounded in the gender index, which is a separate lookup
#     that already succeeded. Its evidence does not come from `placement`.
#   * `pwg_internal_correction` — wave 2 (H2880 §11.3) ruled on exactly this
#     case: a bare `Nachtrag` is unplaced by design and the distribution of
#     placed-vs-unplaced corrections is one of that wave's results. Renaming it
#     here would overturn a decided question this handoff was not asked to reopen.
#   * `base`, `unknown` — no relation asserted at all.
#
# Caveat kept in the open: `a2a` is Nachträge-to-Nachträge, so its true other end
# may be another addendum rather than a PWG sense, while `placement` is measured
# only against the PWG skeleton. `a2a_unplaced` is honest under either reading —
# it says no target was identified, which is true — but it is not evidence that a
# PWG sense was sought and missed. Content alignment (issue #1736 variant D) is
# the only thing that would settle it, and it stays out of scope here.
SENSE_ASSERTING = frozenset({"restate", "nws_at_sense", "a2a"})

UNPLACED_SUFFIX = "_unplaced"

UNPLACED_SUBTYPES = tuple(sorted(s + UNPLACED_SUFFIX for s in SENSE_ASSERTING))

ALL_SUBTYPES = SUBTYPES + UNPLACED_SUBTYPES


def unplaced_name(subtype: str) -> str:
    """The unplaced twin of a sense-asserting label. Idempotent."""
    s = str(subtype or "")
    return s if s.endswith(UNPLACED_SUFFIX) else s + UNPLACED_SUFFIX


def base_subtype(subtype: str) -> str:
    """Strip the unplaced twin back to the label a consumer can group on.

    Every rollup, sheet legend and count that wants "how much of this corpus is
    PW restatement, placed or not" reads this; nothing has to learn a second
    vocabulary to keep working.
    """
    s = str(subtype or "")
    return s[: -len(UNPLACED_SUFFIX)] if s.endswith(UNPLACED_SUFFIX) else s


def is_unplaced_label(subtype: str) -> bool:
    return str(subtype or "").endswith(UNPLACED_SUFFIX)


def placement_label_consistent(subtype: str, placement: bool) -> bool:
    """The W5 invariant: the label and the placement flag say the same thing.

    True iff the label carries the unplaced suffix exactly when the row is a
    sense-asserting relation with no identified target. This is the anti-drift
    device wave 1 was right to want — asserted, not assumed.
    """
    base = base_subtype(subtype)
    if base not in SENSE_ASSERTING:
        return not is_unplaced_label(subtype)
    return is_unplaced_label(subtype) == (not placement)

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


# --- wave 3 (H2881): SCH rows that edit PWG rather than supplement it -------
# Until now the `sch` layer could only come out `sch_star` or `derived_sense`,
# both additive — so "SCH only supplements" was not a measurement, it was a
# property of this function. It is not true: SCH prints instructions to the
# reader of PWG ("read X", "delete Y") alongside its new senses.
#
# The cue lives in the DE BODY, not in the sense_tag — the one structural
# difference from wave 2, and the reason this needs its own predicate. The tag
# of a real correction is as likely to read `mit-nis` as `SCH-corrigendum`.
#
# MEASURED, not assumed (H2881 spike over all 210 SCH rows): the `pw_correct`
# signal the roadmap expected to reuse — a <lex> gender conflict against PWG —
# does not exist on this layer at all. ZERO of the 210 rows carry a <lex> token,
# so the gender path can never fire here and is deliberately not wired up. The
# one real gender correction in the layer (`ahiphena`, "lies n. statt m.")
# states it in prose and is caught by the `lies` rule below.
#
# Each rule is an IMPERATIVE ADDRESSED TO THE READER, never a descriptive word.
# That distinction is the whole criterion, and the negative controls in the
# selftest are the load-bearing half of it: bare `statt` ("metrisch statt na
# gan˚" — describing a metrical variant) and the abbreviation `St.` ("Ind. St."
# = Indische Studien) both look like corrections and are not. A cue set built
# by keyword rather than by speech-act would pull in 11 additive rows.
SCH_CORRECTION_MARKERS = (
    # "S. 152, Sp. 1, Z. 2 lies {%abhíhita%}" — read this instead of what is
    # printed. `\blies\b` and never a substring: it must not fire inside a word.
    ("lies", "correct", re.compile(r"\blies\b", re.I)),
    # "Vielleicht {%saṃpronmlāpya%} zu lesen"
    ("zu_lesen", "correct", re.compile(r"\bzu\s+lesen\b", re.I)),
    # "<ls>S II,267,18</ls> Druckfehler für {%vinirbhinna%}"
    ("druckfehler", "correct", re.compile(r"\bdruckfehler\b", re.I)),
    ("berichtige", "correct", re.compile(r"\bberichtig\w*", re.I)),
    ("verbessere", "correct",
     re.compile(r"\b(verbessere|corrigiere|korrigiere)\b", re.I)),
    # "— Mit {%abhyupa%} 3. streiche <ls>Med.</ls>" — withdraw it entirely.
    ("streiche", "cancel", re.compile(r"\bstreiche\b|\bzu\s+streichen\b", re.I)),
    ("tilge", "cancel", re.compile(r"\btilge\b|\bzu\s+tilgen\b", re.I)),
    ("faellt_weg", "cancel",
     re.compile(r"\bf(ä|ae)llt\s+weg\b|\bweggefallen\b", re.I)),
)

# A compressed SCH article is a run of preverb sections: "1. {%diś%}¦ … — Mit
# {%anvā%} … — Mit {%samā%} Z. 3 lies 231,16. — Mit {%ud%} …". Only the FIRST
# section is what the row as a whole is about.
SCH_SEGMENT_RE = re.compile(r"—\s*(?=Mit\b)", re.I)


def sch_correction_marker(de) -> tuple | None:
    """Name the printed instruction making an SCH row an edit, else None.

    Returns ``(rule_name, kind)`` with ``kind`` in ``{'correct', 'cancel'}`` —
    a name rather than a bool so the sidecar records *which* printed cue moved
    the row and a reviewer can disagree with that one rule (wave 2's contract).

    Scoped to the row's LEADING segment on purpose. 2 of the 210 rows are
    compressed multi-preverb articles whose fifth or sixth section happens to
    carry a correction clause ("— Mit {%samā%} Z. 3 lies 231,16") while the row
    as a whole introduces new senses. Calling such a row a correction would
    assert that SCH withdraws material it in fact adds — the same silent lie
    wave 1 exists to remove, so the conservative default keeps them additive.
    They are not dropped: ``classify_edition_rel`` flags them with
    ``contains_correction_clause`` so the residue stays measurable.
    """
    text = str(de or "")
    segs = [s for s in SCH_SEGMENT_RE.split(text) if s.strip()]
    lead = segs[0] if segs else text
    for name, kind, rx in SCH_CORRECTION_MARKERS:
        if rx.search(lead):
            return (name, kind)
    return None


def sch_has_correction_clause(de) -> bool:
    """True when a correction cue sits anywhere in the row, leading or not."""
    text = str(de or "")
    return any(rx.search(text) for _, _, rx in SCH_CORRECTION_MARKERS)


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
        # Wave 3 (H2881). A printed instruction outranks the tag: the two rows
        # that carry one — 'Mit abhi — corr', 'Mit abhyupa — 3 strikethrough' —
        # also match DERIV_RE on the bare word 'Mit', so testing the tag first
        # would file every SCH correction as `derived_sense` and the layer would
        # stay structurally additive exactly as before.
        sch_marker = sch_correction_marker(de)
        if sch_marker:
            name, kind = sch_marker
            if kind == "cancel":
                subtype = "sch_cancel"
                op = "delete"
            else:
                subtype = "sch_correct"
                op = "correct"
            # `direction` stays "additive": it is a property of the LAYER, not
            # of the pair (plan decision 1), and `pw_correct` sets the same
            # precedent by keeping "abridging". The corrective claim rides on
            # `subtype` + `op`, which is the axis split wave 1 established.
            extra["correction_marker"] = name
            evidence = "SCH edits PWG (%s: %s); sense_tag=%r" % (kind, name, st)
        else:
            subtype = "derived_sense" if DERIV_RE.search(st) else "sch_star"
            evidence = "SCH additive; sense_tag=%r" % st
            if sch_has_correction_clause(de):
                # A correction clause in a non-leading section. Additive by the
                # conservative default, but recorded so the residue is a
                # measured number rather than a silent omission.
                extra["contains_correction_clause"] = True
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
            # H3752: never print "at PWG sense *new" — `*new` is the marker for
            # "no sense was named", so spelling it into the prose reads as a
            # sense number to anyone skimming the evidence column.
            evidence = ("NWS additive at PWG sense %s; sense_tag=%r"
                        % (target_sense, st) if target_sense != "*new"
                        else "NWS additive, no PWG sense named; sense_tag=%r" % st)
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

    # --- label re-derivation (H3752, wave 5) ------------------------------
    # The single site where the label is made a function of the attachment
    # result. `direction` and `op` are NOT touched: "the PW layer abridges PWG"
    # and "this row restates rather than adds" are properties of the layer and
    # of the row, true whether or not a target was located — that half of
    # REGLUE_SPEC §10's two-axis split stands. What changes is only the claim
    # that named a specific PWG sense.
    if subtype in SENSE_ASSERTING and not placement:
        subtype = unplaced_name(subtype)
        evidence = "%s; no identified PWG target (%s)" % (
            evidence or "supplement", placement_reason)

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

    # PW restate (no gender conflict). H3752: the sense index is now supplied,
    # because without one there is no target and the honest label is the
    # unplaced twin — the case immediately below pins that.
    r = classify_edition_rel("pw", "1", "<lex>m.</lex> {%gehen%}", key1="gam",
                             subcard="gam~~h0_zz_pw01",
                             pwg_genders={"m."}, pwg_senses={"1"})
    check(r["subtype"] == "restate" and r["op"] == "restate", "restate: %r" % r)
    check(r["direction"] == "abridging", "pw direction: %r" % r)
    r = classify_edition_rel("pw", "1", "<lex>m.</lex> {%gehen%}", key1="gam",
                             subcard="gam~~h0_zz_pw01", pwg_genders={"m."})
    check(r["subtype"] == "restate_unplaced" and r["op"] == "restate",
          "no index at all -> the label must not claim a sense: %r" % r)

    # PW correct (gender change)
    r = classify_edition_rel("pw", "1", "<lex>f.</lex> {%x%}", key1="x",
                             subcard="x~~h0_zz_pw01", pwg_genders={"m."})
    check(r["subtype"] == "pw_correct" and r["op"] == "correct", "pw_correct: %r" % r)

    # SCH star vs derived
    r = classify_edition_rel("sch", "2", "{%neu%}", subcard="a~~h0_zz_sch")
    check(r["subtype"] == "sch_star", "sch_star: %r" % r)
    r = classify_edition_rel("sch", "anu_desid", "{%einstimmen%}", subcard="a~~h0_zz_sch")
    check(r["subtype"] == "derived_sense", "sch derived: %r" % r)

    # PWKVN a2a vs derived (H3752: index supplied so the target resolves)
    r = classify_edition_rel("pwkvn", "3", "{%x%}", subcard="a~~h0_zz_pwkvn",
                             pwg_senses={"3"})
    check(r["subtype"] == "a2a" and r["op"] == "relocate", "a2a: %r" % r)
    r = classify_edition_rel("pwkvn", "ava_caus", "{%x%}", subcard="a~~h0_zz_pwkvn")
    check(r["subtype"] == "derived_sense", "pwkvn derived: %r" % r)

    # NWS
    r = classify_edition_rel("nws", "2", "der und die mit sich",
                             subcard="a~~h0_zz_nws", pwg_senses={"2"})
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

    # H3752 supersedes the wave-1 expectation here. This same case used to
    # assert `subtype == "restate"` with `placement False` — that pairing IS
    # issue #1736: a paraphrase label over a sense that was never identified.
    r = classify_edition_rel("pw", "Nachtrag", "{%x%}", key1="x",
                             subcard="x~~h0_zz_pw01", pwg_senses=senses)
    check(r["subtype"] == "restate_unplaced" and r["placement"] is False,
          "an unplaced restate is labelled unplaced: %r" % r)
    check(base_subtype(r["subtype"]) == "restate",
          "…and still groups as a restate: %r" % r)

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

    # --- wave 3: SCH corrections and cancellations (H2881) -----------------
    # POSITIVES — the real printed instructions, quoted from the store.
    for de, want in (
        ("1. {%dhā%}¦  mit {%abhi%}, S. 152, Sp. 1, Z. 2 lies {%abhíhita%}.",
         ("lies", "correct")),
        ("Mit {%nis%} Z. 2 lies {%niṣpīta%}.", ("lies", "correct")),
        ("*{%ahiphena%}¦ , lies n. statt m.", ("lies", "correct")),
        ("Mit {%˚vini, vinibhinna%} <ls>S II,267,18</ls> Druckfehler für "
         "{%vinirbhinna%}.", ("druckfehler", "correct")),
        ("Vielleicht {%saṃpronmlāpya%} zu lesen.", ("zu_lesen", "correct")),
        ("— Mit {%abhyupa%} 3. streiche <ls>Med.</ls>", ("streiche", "cancel")),
        ("Der Zusatz ist zu tilgen.", ("tilge", "cancel")),
    ):
        got = sch_correction_marker(de)
        check(got == want, "sch marker %r -> %r, want %r" % (de[:40], got, want))

    # NEGATIVES — the whole criterion is "instruction to the reader", not
    # "keyword". Every string below is real additive SCH text that a keyword
    # rule would have swallowed; 11 of the 210 rows carry one of these tokens.
    for de in (
        # 'St.' is Indische Studien, not 'statt'
        "Mit {%vi, vyāpta%} 4. in allem enthalten, <ls>Ind. St. 9,137.</ls>",
        # bare 'statt' describing a metrical variant, not ordering a change
        "{%mā gantum arhasi%} metrisch statt {%na gan˚%},2,116,5.",
        "Statt dessen {%vipācayati%} 281,158.",
        # 'vgl.' points at literature; it edits nothing
        "Mit {%upapra%}, vgl. <ls>Pischel, Ved. Stud. I,72.</ls>",
        "{%yat%}¦ <ls>Kaus.</ls> vgl. Roth, <ls>ZDMG 41,676.</ls>",
        # ordinary new senses
        "Mit {%ava%} <ls>Kaus.</ls> jemand (Akk.) etwas (Akk.) erlangen lassen.",
        "Mit {%˚samud%}, to burst forth, <ls>Harṣac. 153,15; 167,9.</ls>",
        "", None,
    ):
        got = sch_correction_marker(de)
        check(got is None, "sch marker must not fire on %r, got %r" % (de, got))

    # THE trap: a compressed multi-preverb article whose LAST sections carry a
    # correction clause is still, as a row, additive. Classifying it as a
    # correction would assert SCH withdraws material it actually adds.
    mixed = ("1. {%diś%}¦ ˚hervorbringen, schaffen, <ls>Kir. I,18.</ls> "
             "— Mit {%anvā%} jemandem (Akk.) befehlen, <ls>Jātakam. 20</ls>. "
             "— Mit {%samā%} Z. 3 lies 231,16. "
             "— Mit {%ud%} auch abweisen, <ls>R. ed. Bomb. 3,46,35.</ls>")
    check(sch_correction_marker(mixed) is None,
          "a non-leading correction clause must not classify the row")
    check(sch_has_correction_clause(mixed) is True,
          "…but it must still be recorded as present")
    r = classify_edition_rel("sch", "˚hervorbringen", mixed,
                             subcard="diS~~h0_zz_sch")
    check(r["subtype"] in ("sch_star", "derived_sense"),
          "mixed row stays additive: %r" % r)
    check(r.get("contains_correction_clause") is True,
          "mixed row must carry the residue flag: %r" % r)

    # a leading correction DOES classify, even when it opens with '— Mit'
    r = classify_edition_rel("sch", "Mit abhyupa — 3 strikethrough",
                             "— Mit {%abhyupa%} 3. streiche <ls>Med.</ls>",
                             subcard="DA~~h0_zz_sch")
    check(r["subtype"] == "sch_cancel" and r["op"] == "delete",
          "sch_cancel: %r" % r)
    check(r["correction_marker"] == "streiche", "cancel marker: %r" % r)

    # DERIV_RE matches 'Mit' in both these tags. The correction cue must win,
    # or every SCH correction is filed as `derived_sense` and the layer stays
    # structurally additive — the exact defect wave 3 removes.
    for tag in ("Mit abhi — corr", "mit-nis", "Mit abhyupa — 3 strikethrough"):
        check(DERIV_RE.search(tag) is not None,
              "precondition: %r must look grammar-derived" % tag)
    r = classify_edition_rel("sch", "Mit abhi — corr",
                             "1. {%dhā%}¦ mit {%abhi%}, S. 152, Z. 2 lies "
                             "{%abhíhita%}.", subcard="DA~~h0_zz_sch")
    check(r["subtype"] == "sch_correct" and r["op"] == "correct",
          "correction outranks derived_sense: %r" % r)

    # op is deliberately correct/delete here, unlike wave 2's `amend`: these
    # rows really do withdraw the printed reading, so build_reglue's
    # "cancels PWG" strikethrough is the honest rendering.
    check(r["op"] in ("correct", "delete"), "sch edit must render as a cancel")

    # direction stays the LAYER's property (plan decision 1), as pw_correct does
    check(r["direction"] == "additive", "sch direction stays additive: %r" % r)

    # an ordinary additive SCH row grows no correction fields
    r = classify_edition_rel("sch", "2", "{%neu%}", subcard="a~~h0_zz_sch")
    check(r["subtype"] == "sch_star", "plain sch_star: %r" % r)
    check("correction_marker" not in r
          and "contains_correction_clause" not in r,
          "additive row must stay clean: %r" % r)

    # the cue is read from `de`, never from the tag: a tag that merely SAYS
    # corrigendum is not evidence, and a row is not spared because its tag is bland
    r = classify_edition_rel("sch", "SCH-corrigendum", "{%neu%} hinzuzufügen",
                             subcard="a~~h0_zz_sch")
    check(r["subtype"] == "sch_star", "tag alone must not convict: %r" % r)

    # other layers are untouched by the SCH rule, cue text notwithstanding
    for lay, want in (("pw", "restate"), ("pwkvn", "a2a")):
        r = classify_edition_rel(lay, "1", "Z. 2 lies {%x%}", key1="x",
                                 subcard="x~~h0_zz_%s" % lay,
                                 pwg_senses={"1"})
        check(r["subtype"] == want,
              "layer %s must ignore the sch cue: %r" % (lay, r))

    # --- wave 5: the label follows the attachment (H3752, issue #1736) ------
    # THE RED PIN. Every assertion in this block fails against the pre-H3752
    # classifier, which labelled all four rows `restate` / `nws_at_sense` /
    # `a2a` while their own `target_sense` read `*new`.
    w5 = {"1", "2", "3"}
    for lay, tag, de, want in (
        # mode A — no leading number on the supplement's own tag
        ("pw", "caus", "{%kurz%}", "restate_unplaced"),
        ("nws", "NWS-add", "der die und mit sich", "nws_at_sense_unplaced"),
        ("pwkvn", "Nachtrag", "{%x%}", "a2a_unplaced"),
        # mode B — a target number that leads nowhere
        ("pw", "9", "{%kurz%}", "restate_unplaced"),
    ):
        r = classify_edition_rel(lay, tag, de, key1="x",
                                 subcard="x~~h0_zz_%s" % lay, pwg_senses=w5)
        check(r["subtype"] == want,
              "unplaced %s must not keep the placed label: %r -> %r"
              % (lay, tag, r["subtype"]))
        check(r["placement"] is False, "…and stays unplaced: %r" % r)
        check(r["insertion_point"]["target_sense"] != "*new"
              or "no identified PWG target" in r["evidence"],
              "the evidence string must say the target is missing: %r" % r)

    # the placed twins keep the plain label — the fix must not empty the corpus
    for lay, tag, de, want in (
        ("pw", "2", "{%kurz%}", "restate"),
        ("nws", "2", "der die und mit sich", "nws_at_sense"),
        ("pwkvn", "3", "{%x%}", "a2a"),
    ):
        r = classify_edition_rel(lay, tag, de, key1="x",
                                 subcard="x~~h0_zz_%s" % lay, pwg_senses=w5)
        check(r["subtype"] == want and r["placement"] is True,
              "a placed %s keeps its label: %r" % (lay, r))

    # `direction` and `op` are LAYER/ROW properties and must survive untouched —
    # losing them is issue #1736 variant B, the over-correction this rejects.
    r = classify_edition_rel("pw", "caus", "{%kurz%}", key1="x",
                             subcard="x~~h0_zz_pw01", pwg_senses=w5)
    check(r["direction"] == "abridging" and r["op"] == "restate",
          "an unplaced restate is still an abridging restatement: %r" % r)

    # subtypes that assert no sense relation are NOT suffixed
    for lay, tag, de in (("sch", "neu", "{%neu%}"),
                         ("sch", "anu_desid", "{%x%}"),
                         ("nws", "NWS-1", "the of and in with is for from by as"),
                         ("pwg", "Nachtrag", "{%x%}")):
        r = classify_edition_rel(lay, tag, de, key1="x",
                                 subcard="x~~h0_zz_%s" % lay, pwg_senses=w5)
        check(not is_unplaced_label(r["subtype"]),
              "%s/%s asserts no sense relation and must keep its label: %r"
              % (lay, tag, r["subtype"]))

    # pw_correct is grounded in the gender index, not in `placement`
    r = classify_edition_rel("pw", "9", "<lex>f.</lex> {%x%}", key1="x",
                             subcard="x~~h0_zz_pw01", pwg_genders={"m."},
                             pwg_senses=w5)
    check(r["subtype"] == "pw_correct" and r["placement"] is False,
          "pw_correct is not suffixed by the placement result: %r" % r)

    # helpers
    check(unplaced_name("restate") == "restate_unplaced", "unplaced_name")
    check(unplaced_name("restate_unplaced") == "restate_unplaced",
          "unplaced_name is idempotent")
    check(base_subtype("restate_unplaced") == "restate", "base_subtype")
    check(base_subtype("restate") == "restate", "base_subtype is idempotent")
    check(base_subtype("sch_star") == "sch_star", "base_subtype leaves others")

    # the invariant the corpus gate (W5a) asserts
    check(placement_label_consistent("restate", True), "consistent: placed")
    check(placement_label_consistent("restate_unplaced", False),
          "consistent: unplaced")
    check(not placement_label_consistent("restate", False),
          "INCONSISTENT: the exact #1736 shape must be rejected")
    check(not placement_label_consistent("restate_unplaced", True),
          "INCONSISTENT: an unplaced label on a placed row")
    check(placement_label_consistent("sch_star", False),
          "an additive subtype is consistent either way")
    check(not placement_label_consistent("sch_star_unplaced", False),
          "a suffix on a non-asserting subtype is itself a defect")

    # every classifier output satisfies the invariant, by construction
    for lay, tag, de in (("pw", "1", "{%x%}"), ("pw", "caus", "{%x%}"),
                         ("pw", "9", "{%x%}"), ("nws", "1", "der die und"),
                         ("nws", "nws-x", "der die und"), ("pwkvn", "2", "{%x%}"),
                         ("pwkvn", "ava_caus", "{%x%}"), ("sch", "1", "{%x%}"),
                         ("pwg", "Nachtrag", "{%x%}"), ("zz", "1", "{%x%}")):
        r = classify_edition_rel(lay, tag, de, key1="x",
                                 subcard="x~~h0_zz_%s" % lay, pwg_senses=w5)
        check(placement_label_consistent(r["subtype"], r["placement"]),
              "classifier output violates the W5 invariant: %s/%s -> %r"
              % (lay, tag, r))

    # every emitted label is a declared one — no silently invented vocabulary
    check(set(UNPLACED_SUBTYPES) <= set(ALL_SUBTYPES), "unplaced names declared")
    check(all(base_subtype(s) in SUBTYPES for s in UNPLACED_SUBTYPES),
          "every unplaced twin strips back to a declared subtype")

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
        classify_edition_rel("sch", "1", "Z. 2 lies {%x%}")["subtype"],
        classify_edition_rel("sch", "1", "3. streiche <ls>Med.</ls>")["subtype"],
    }
    # H3752: grouped on the BASE name — these calls pass no sense index, so the
    # three sense-asserting labels come back as their unplaced twins. That is the
    # point of the fix, and `base_subtype` is exactly the seam that keeps every
    # existing consumer's grouping working without learning a second vocabulary.
    seen = {base_subtype(s) for s in seen}
    for need in ("base", "restate", "pw_correct", "sch_star", "derived_sense",
                 "a2a", "nws_at_sense", "foreign_fragment",
                 "pwg_internal_correction", "sch_correct", "sch_cancel"):
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
