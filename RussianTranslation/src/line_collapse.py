#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""line_collapse — which store newlines are typesetting and which are structure (H2844).

The problem, in one store body (``gā``, verbatim)::

    …{#yadA ca pfTivIM sarvAM yajamAno 'nuparyagAH#}\\n<ls>MBH. 12,8081.</ls>

That ``\\n`` is csl-orig's **physical line-wrap of the printed PWG column**. It
marks no structure at all — the citation simply did not fit on the same printed
line as the verse it sources. It is nevertheless carried into the store and
turned into a hard ``<br>`` by ``build_article_site._render`` (``t.replace('\\n',
'<br>')``), so every print view tears the citation off its own clause.

How common: measured over the 11,603-row store, ``ru`` fields carry **25,325**
newlines, of which **24,103 are immediately followed by ``<ls``** — 95.2 % of
all newlines, and 58.4 % of the store's 41,306 RU ``<ls>`` citations begin a
line this way. It is the majority case, not an edge case.

**Ruled (H2843 / H2844 P1): collapse it at render time; never touch the store.**
Same principle as the H2827 §8.3 gloss-chain split — a display transform with
the raw bytes one panel away. Every function here is pure: it takes a store
string and returns a new one, so the anatomy/raw panel keeps byte-identical
text (:func:`store_digest` is the mechanical proof of that, used by the sheet
builder's selftest).

What stays a line break
-----------------------
A newline is **structural** — and survives in expanded mode — when the text
after it opens a new unit of the entry rather than continuing a clause:

===================  ======  ==================================================
after the newline     ru n    why it is structure
===================  ======  ==================================================
``<div n="…">``       1,123   csl-orig's own sense division
``— 2)`` / ``2)``        26   a numbered sense
``— <ab>caus.</ab>``     52   a derivational / preverb block
``<hom>``                 5   a homonym boundary
===================  ======  ==================================================

Everything else continues the clause and collapses to a single space:
``<ls>`` (24,103), ``{#…#}`` (280), ``<ab>`` (255), ``{%…%}`` (38), bare text
including the ``[Page5-0288]`` column markers (568), ``<lex>``/``<lang>``/
``<is>`` (13).

Two modes, one data source (H2844 P3)
-------------------------------------
* ``expanded`` — the etext reading. Inherited wraps collapse; structural
  newlines stay, so each sense still starts on its own line.
* ``compact`` — the printed-dictionary column. Everything runs on; the sense
  markers (``1)``, ``— 2)``) remain visible as text and carry the boundary.

The collapse direction is safe by construction: replacing a newline with a
space can only ever **join** a citation to the clause before it. Nothing here
can tear one apart — the tearing is what the un-collapsed ``<br>`` already does.
"""
import hashlib
import re
import sys

__all__ = ["EXPANDED", "COMPACT", "collapse", "classify_sites", "store_digest"]

EXPANDED = "expanded"
COMPACT = "compact"

#: The text right after a newline opens a new unit of the entry. Anchored at the
#: start of the (left-stripped) tail, so nothing mid-clause can match.
#:
#: ``—\\s`` deliberately subsumes ``— 2)``: a dash-led run is a derivational or
#: preverb block either way. It is listed separately above only because the two
#: were counted separately in the census.
_STRUCTURAL = re.compile(
    r"""^(?:
          <div\b            # csl-orig's own sense division
        | <hom\b            # a homonym boundary
        | \d+[)〉]      # 2)  or  2>  — a numbered sense
        | —            # — a derivational / preverb block (incl. "— 2)")
    )""",
    re.X,
)

#: One newline with whatever horizontal whitespace hugs it. Consecutive blank
#: lines (which the ``[Page…]`` markers leave behind once stripped) are handled
#: one newline at a time, so each is classified on its own tail.
_NEWLINE = re.compile(r"[ \t]*\n[ \t]*")


def is_structural(tail):
    """True when the text following a newline opens a new unit of the entry.

    ``tail`` is the remainder of the body after the newline; only its first
    non-space characters are consulted.
    """
    return bool(_STRUCTURAL.match((tail or "").lstrip(" \t\n")))


def collapse(text, mode=EXPANDED):
    """Return ``(rendered_text, n_collapsed, n_kept)`` for one store body.

    ``rendered_text`` is a NEW string; ``text`` is never mutated (Python strings
    could not be anyway — the point is that no caller may pass the result back
    into the store). In ``EXPANDED`` mode structural newlines survive as ``\\n``
    and reach ``build_article_site._render`` as a ``<br>``; in ``COMPACT`` mode
    every newline becomes a space and the sense markers carry the boundary.
    """
    if not text:
        return text or "", 0, 0
    out, last, n_col, n_kept = [], 0, 0, 0
    seen = False                      # any non-space text emitted so far
    for m in _NEWLINE.finditer(text):
        head = text[last:m.start()]
        out.append(head)
        seen = seen or bool(head.strip())
        tail = text[m.end():]
        if mode != COMPACT and is_structural(tail):
            out.append("\n")
            n_kept += 1
        else:
            # A leading/trailing wrap has nothing to join; drop it rather than
            # opening the body with a stray space.
            out.append(" " if (seen and tail.strip()) else "")
            n_col += 1
        last = m.end()
    out.append(text[last:])
    joined = "".join(out)
    # A collapse can leave a double space where the store already had one.
    joined = re.sub(r"[ \t]{2,}", " ", joined)
    return joined, n_col, n_kept


def classify_sites(text):
    """Every newline in ``text`` as ``(offset, kind, before, after)``.

    ``kind`` is ``"structural"`` or ``"inherited"``; ``before``/``after`` are the
    40 characters either side, for an audit report that a human can read without
    opening the store.
    """
    sites = []
    for m in _NEWLINE.finditer(text or ""):
        tail = text[m.end():]
        kind = "structural" if is_structural(tail) else "inherited"
        sites.append((m.start(), kind,
                      text[max(0, m.start() - 40):m.start()], tail[:40]))
    return sites


def store_digest(*texts):
    """SHA-256 over the store strings exactly as they will reach the raw panel.

    The sheet builder takes this before rendering and again after, and refuses
    to publish if the two differ — the hash the acceptance asks for, instead of
    checking the raw panel by eye.
    """
    h = hashlib.sha256()
    for t in texts:
        h.update((t or "").encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def _selftest():
    sys.stdout.reconfigure(encoding="utf-8")
    ok = True

    def check(cond, label):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + label)
        ok = ok and bool(cond)

    ga = ("{#yadA ca pfTivIM sarvAM yajamAno 'nuparyagAH#}\n"
          "<ls>MBH. 12,8081.</ls>")
    out, n_col, n_kept = collapse(ga)
    check("#} <ls>MBH" in out, "the motivating case joins: %r" % out[-40:])
    check((n_col, n_kept) == (1, 0), "one inherited wrap collapsed, none kept")

    div = "{%достигать%}: {#ko vA#}\n<div n=\"1\"> 1) {%обретать%}"
    out2, n_col2, n_kept2 = collapse(div)
    check("\n<div" in out2 and (n_col2, n_kept2) == (0, 1),
          "a <div> sense division stays a line break in expanded mode")
    out3, n_col3, n_kept3 = collapse(div, COMPACT)
    check("\n" not in out3 and (n_col3, n_kept3) == (1, 0),
          "the same division runs on in compact mode")

    check(is_structural("— 2) {#sADayati#}"), "— 2) is a numbered sense")
    check(is_structural("2) {#saMBinna#}"), "2) is a numbered sense")
    check(is_structural("— <ab>desid.</ab> {#Asisizate#}"),
          "— <ab>caus.</ab> opens a derivational block")
    check(is_structural("<hom>2.</hom> {#˚gA#}"), "<hom> is a homonym boundary")
    check(not is_structural("<ls>P. 6,4,57.</ls>"), "<ls> continues the clause")
    check(not is_structural("{#aBIpsantI#}"), "a Sanskrit span continues the clause")
    check(not is_structural("[Page1-0651]"),
          "a column page marker is typesetting, not structure")

    page = "{#aBIpsatI#}\n<ls>MBH. 1,6469.</ls>\n[Page1-0651]\n{#aBIpsantI#}"
    outp, n_colp, n_keptp = collapse(page)
    check("\n" not in outp and n_colp == 3,
          "a page-marker line collapses on both sides: %r" % outp)

    check(collapse("одна строка")[0] == "одна строка", "a body with no newline is untouched")
    check(collapse("")[0] == "" and collapse(None)[0] == "", "empty/None is safe")

    lead = "\n<ls>P. 1,1</ls>"
    check(collapse(lead)[0] == "<ls>P. 1,1</ls>",
          "a leading wrap does not open the body with a space")

    # purity: the input string is still the input string, and the digest proves it
    src = ga
    before = store_digest(src)
    collapse(src, COMPACT)
    check(store_digest(src) == before, "collapse leaves the store string untouched")
    check(store_digest("a", "b") != store_digest("ab"),
          "the digest separates fields — 'a','b' is not 'ab'")

    kinds = [k for _, k, _, _ in classify_sites(page)]
    check(kinds == ["inherited", "inherited", "inherited"],
          "classify_sites labels every site: %r" % kinds)
    check([k for _, k, _, _ in classify_sites(div)] == ["structural"],
          "classify_sites finds the structural one")

    print("line_collapse selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_selftest())
