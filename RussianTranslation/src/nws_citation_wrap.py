#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nws_citation_wrap.py — Ṛgveda/Atharvaveda addresses that carry no ``<ls>`` (H3152).

MG review point 5: *«вся Ригведа и Атхарваведа должна быть железно
пролинкована»*. The resolver is not the gap —
[`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
links a well-formed ``<ls>ṚV. 10,108,9</ls>`` correctly and has for a year. The
gap is that in the NWS layer the address often stands in the running text with
**no element around it at all**, because the Cologne source has none::

    идти. AV(P) 9.10,10
    ṚV x, 68, 1

Nothing to resolve means nothing to link. This module finds those addresses so
the renderer can wrap them, and so a change-file can carry the same wrap back to
csl-orig through the correction queue (never a direct commit — PLAN fence 2).

Why a narrow whitelist and not "looks like a citation"
------------------------------------------------------
The two failure modes are not symmetric. A **missed** address costs one link. A
**false** wrap puts a link on text that is not a citation — it corrupts the
article and, worse, sends the reader to a verse that has nothing to do with what
they were reading. So recognition is a short list of shapes measured in the
store, every candidate is resolved before it is accepted, and anything that does
not produce a real href is left alone.

What is deliberately NOT wrapped
--------------------------------
``AV(P)``
    The Paippalāda recension. It is a **different text** from the Śaunaka
    Atharvaveda that ``avlinks`` publishes, so ``AV(P) 9.10,10`` and
    ``AV. 9,10,10`` are not the same verse. Linking one to the other would
    manufacture a false identity between two recensions — the sort of claim the
    ``unchecked``-is-not-``absent`` rule of H2845 exists to forbid. Three
    occurrences in the store; they stay plain text and are reported.

bare ``ṚV`` / ``AV`` with no address
    ``ṚV, AV, ŚB, Mbh.`` names works, not places. There is nothing to point at —
    the same ``no_locus`` bucket
    [`ls_links.classify`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_links.py)
    already separates for wrapped citations.

incomplete Roman addresses
    ``AV v, 1`` is book and hymn with no verse. The link target needs all three.

Run: ``python src/nws_citation_wrap.py --selftest``
"""
import sys, os, re, html

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("LS_RESOLVER_QUIET", "1")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ls_resolver as lsr                                      # noqa: E402

#: Regions of a store body that are never scanned: an existing citation element
#: (already linked, and re-wrapping would nest elements) and a Sanskrit span
#: (whose transliteration can contain look-alike digit runs).
_MASKED = re.compile(r"<ls\b[^>]*>.*?</ls>|\{[#%].*?[#%]\}|<[^>]+>", re.S)

#: Ṛgveda and Atharvaveda in the spellings the store actually uses. The trailing
#: period is optional because the NWS layer usually drops it.
_WORK = r"(?P<work>ṚV|RV|ṚgV|AV)\.?"

#: Arabic address, three comma-separated groups: mandala/book, hymn, verse.
_ARABIC = re.compile(
    r"(?<![\wĀ-ɏ(])" + _WORK + r"\s+(?P<addr>\d{1,2},\s?\d{1,3},\s?\d{1,3})"
    r"(?![\d,])")

#: The Roman-numeral form the MW-derived NWS material uses: ``ṚV x, 68, 1``.
#: Followed by ``&`` or ``;`` it introduces a *run* of addresses, which this
#: module does not attempt — one address at a time or nothing.
_ROMAN = re.compile(
    r"(?<![\wĀ-ɏ(])" + _WORK +
    r"\s+(?P<roman>[ivxlIVXL]{1,6}),\s?(?P<hymn>\d{1,3}),\s?(?P<verse>\d{1,3})"
    r"(?!\s*[&;,]\s*\d)(?![\d,])")

#: canonical work prefix for the ``n=`` attribute, keyed by what was written
_CANON = {"ṚV": "ṚV.", "RV": "ṚV.", "ṚgV": "ṚV.", "AV": "AV."}

_ROMAN_VALUE = {"i": 1, "v": 5, "x": 10, "l": 50}

#: How many books each work has. The resolver does **not** range-check: asked for
#: ``ṚV. 99,999,999`` it dutifully formats ``rv99.999.html#rv99.999.999``, a URL
#: that is well-formed and points at nothing. For a citation the source already
#: wrapped that is harmless (the address came from PWG and is presumed real); for
#: an address *this module invents an element around* it is not, so the bound is
#: checked here before anything is claimed.
_MAX_BOOK = {"ṚV.": 10, "AV.": 20}


def roman_to_int(s):
    """Subtractive Roman numeral → int, or ``None``. Range is small by design:
    Ṛgveda has 10 maṇḍalas and the Atharvaveda 20 books, so anything outside
    1–20 is a misread, not a citation."""
    s = (s or "").lower()
    if not s or any(c not in _ROMAN_VALUE for c in s):
        return None
    total, prev = 0, 0
    for c in reversed(s):
        v = _ROMAN_VALUE[c]
        total += -v if v < prev else v
        prev = max(prev, v)
    return total if 1 <= total <= 20 else None


def _accept(work, addr):
    """``(canonical_citation, href)`` if this address really resolves, else None.

    Resolution is the acceptance test, not a check applied afterwards: a shape
    the resolver cannot place is not a citation this module is willing to claim.
    """
    prefix = _CANON[work]
    try:
        book = int(addr.split(",")[0])
    except (ValueError, IndexError):
        return None
    if not 1 <= book <= _MAX_BOOK[prefix]:
        return None
    canon = "%s %s" % (prefix, addr)
    try:
        href = lsr.generate_href("pwg", None, canon)
    except Exception:
        href = None
    return (canon, href) if href else None


def find_bare_citations(text):
    """Every unwrapped Ṛgveda/Atharvaveda address in ``text``.

    Yields ``(start, end, raw, work_bucket, canonical)`` in document order, where
    ``work_bucket`` is ``ṚV.``/``AV.`` (matching
    [`reglue2_coverage`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reglue2_coverage.py))
    and ``canonical`` is the citation string to put in the ``n=`` attribute.
    """
    text = text or ""
    # blank out everything already marked up, preserving offsets
    scan = _MASKED.sub(lambda m: " " * len(m.group(0)), text)
    found = []
    for rx in (_ARABIC, _ROMAN):
        for m in rx.finditer(scan):
            work = m.group("work")
            if rx is _ARABIC:
                addr = re.sub(r",\s*", ",", m.group("addr"))
            else:
                book = roman_to_int(m.group("roman"))
                if book is None:
                    continue
                addr = "%d,%s,%s" % (book, m.group("hymn"), m.group("verse"))
            hit = _accept(work, addr)
            if not hit:
                continue
            found.append((m.start(), m.end(), text[m.start():m.end()],
                          _CANON[work], hit[0]))
    found.sort()
    # two patterns can never legitimately claim the same span; keep the first
    out, last_end = [], -1
    for item in found:
        if item[0] >= last_end:
            out.append(item)
            last_end = item[1]
    return out


def wrap_bare_citations(text):
    """``text`` with every recognised bare address wrapped in an ``<ls>`` element.

    The element mirrors the shape the store already uses for NWS citations that
    *were* wrapped upstream — ``<ls n="ṚV. 10,108,9">ṚV 10,108,9</ls>`` — so the
    downstream renderer needs no new code path and the visible text the reader
    sees is unchanged, character for character.
    """
    hits = find_bare_citations(text)
    if not hits:
        return text, 0
    out, pos = [], 0
    for start, end, raw, _work, canon in hits:
        out.append(text[pos:start])
        out.append('<ls n="%s">%s</ls>' % (html.escape(canon, quote=True), raw))
        pos = end
    out.append(text[pos:])
    return "".join(out), len(hits)


def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    # ---- the control cases from the gā card (VERIFICATION §1, A5)
    hits = find_bare_citations("идти, входить в; уходить. ṚV 10,108,9")
    check(len(hits) == 1 and hits[0][4] == "ṚV. 10,108,9",
          "bare ṚV 10,108,9 is recognised as ṚV. 10,108,9 (%r)" % (hits,))
    wrapped, n = wrap_bare_citations("идти, входить в; уходить. ṚV 10,108,9")
    check(n == 1 and '<ls n="ṚV. 10,108,9">ṚV 10,108,9</ls>' in wrapped,
          "wrap reproduces the store's own NWS element shape: %s" % wrapped)
    check(lsr.generate_href("pwg", "ṚV. 10,108,9", "ṚV 10,108,9"),
          "the emitted element resolves through the normal render path")

    # ---- the Roman-numeral MW form
    r = find_bare_citations("скрываться, бояться (?). ṚV x, 68, 1")
    check(len(r) == 1 and r[0][4] == "ṚV. 10,68,1",
          "Roman maṇḍala x is converted to 10 (%r)" % (r,))
    check(roman_to_int("iii") == 3 and roman_to_int("xiv") == 14,
          "subtractive Roman numerals")
    check(roman_to_int("xxx") is None and roman_to_int("") is None,
          "out-of-range and empty Roman numerals are refused")

    # ---- Paippalāda: a different recension, deliberately NOT linked
    check(find_bare_citations("идти. AV(P) 9.10,10") == [],
          "AV(P) — the Paippalāda recension — is never wrapped as Śaunaka AV")

    # ---- nothing to point at
    check(find_bare_citations("благой, добрый. ṚV, AV, B(MW), ŚS(MW).") == [],
          "a list of work names with no address is not a citation")
    check(find_bare_citations("вред. AV v, 1 . скрываться") == [],
          "an incomplete Roman address (book, hymn, no verse) is refused")
    check(find_bare_citations("ṚV x, 14, 16 & 130, 4") == [],
          "a run of addresses joined by & is left alone, not half-linked")

    # ---- never touch what is already marked up
    already = 'уходить. <ls n="ṚV. 10,108,9">ṚV 10,108,9</ls>'
    check(find_bare_citations(already) == [],
          "an address already inside <ls> is not re-wrapped")
    check(wrap_bare_citations(already)[0] == already,
          "a body with no bare address comes back byte-identical")
    check(find_bare_citations("{#ṚV 10,108,9#}") == [],
          "a Sanskrit span is masked before scanning")

    # ---- an address outside the work is not claimed, even though the resolver
    # will happily format a URL for it
    check(lsr.generate_href("pwg", None, "ṚV. 99,999,999"),
          "the resolver itself does NOT range-check maṇḍala numbers")
    check(find_bare_citations("ṚV 99,999,999") == [],
          "maṇḍala 99 does not exist — refused despite a well-formed URL")
    check(find_bare_citations("AV 25,1,1") == [],
          "Atharvaveda book 25 does not exist — refused")
    check(len(find_bare_citations("AV 20,1,1")) == 1,
          "AV book 20 (the last real one) is still accepted")

    print("nws_citation_wrap selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest())
