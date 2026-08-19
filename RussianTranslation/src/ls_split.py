#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ls_split.py — one ``<ls>`` element, several addresses (H3152, MG review 6a).

The defect
----------
PWG prints a run of addresses under one source abbreviation, and csl-orig wraps
the whole run in a single element::

    <ls>ṚV. 4,3,13. 10,18,4</ls>

[`ls_resolver.generate_href`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
is a *one address* function: it reads ``ṚV. 4,3,13.``, returns the href for
4.003.13, and the second address is silently swallowed. On the card the reader
sees two verse numbers and can click one — which reads as "there is no second
place", the exact complaint in review point 6a.

The fix is a **render-time** split. The source is not touched (PLAN fence 2);
each address is resolved on its own and the change is additionally written out
as a csl-corrections change-file so the markup improves upstream too.

How the split works
-------------------
Splitting on "period, space, digit" *alone* is wrong, and wrong in a way that
would quietly destroy good citations: ``AIT. BR. 6,33.`` and ``BHĀG. P. 2,6,35.``
and ``MED. t. 3`` all contain that boundary inside their **source abbreviation**,
so a naive rule tears the work name off its address.

So the visible text is cut in two first: the leading run of non-digits is the
source prefix (``ṚV. ``, ``AIT. BR. ``, ``MED. t. ``), and only what follows —
the address region — is split. Every resulting address is re-joined to the same
prefix, which makes the first address reconstruct the original string byte for
byte. That invariant is what the selftest pins: **splitting can never change how
the first address resolves.**

All or nothing (ARCHITECTURE §4)
--------------------------------
:func:`resolve_loci` returns ``None`` unless *every* address resolves. A partial
split is worse than none: three addresses of which two are links reads as
"the third place does not exist", which is the same false statement the defect
already makes, just moved. When any address fails the caller renders the element
exactly as it does today.

Run: ``python src/ls_split.py --selftest``
"""
import sys, os, re

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("LS_RESOLVER_QUIET", "1")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ls_resolver as lsr                                      # noqa: E402

#: The address-region boundary: a period, whitespace, then a digit. Applied only
#: *after* the source prefix has been cut off, which is what keeps it away from
#: the periods inside ``AIT. BR.`` / ``BHĀG. P.`` / ``MED. t.``.
_ADDR_BOUNDARY = re.compile(r"(?<=\.)\s+(?=\d)")

#: The source prefix is the leading run of characters before the first digit.
#: ``Spr. (II) 1234.`` keeps its edition marker; ``<ls n="ṚV.">4,3,13.</ls>``
#: has an empty prefix because its work name lives in the ``n=`` attribute.
_PREFIX = re.compile(r"^\D*")

#: Nested markup inside the citation body — ``<is n="Vārttika">Vārtt.</is>`` and
#: friends. Its presence means the run is NOT a plain list of addresses under one
#: siglum, so prefix inheritance does not hold. See :func:`splittable`.
_NESTED = re.compile(r"<[^>]+>")

#: A sibling address is *purely* a locus: digits and commas, an optional trailing
#: period, nothing else. Anything richer — ``11087 (p. 572)``, ``83, N. 6``,
#: ``100,a.`` — is one address carrying a page reference, a note marker or a
#: column letter, not two addresses.
_PURE_ADDRESS = re.compile(r"^\d+(?:\s*,\s*\d+)*\.?$")

#: An address's shape: how many numeric components it has.
_COMPONENTS = re.compile(r"\d+")


def split_ls_loci(n_attr, visible):
    """Split one ``<ls>`` body into the address strings it actually holds.

    Returns a list of *visible-equivalent* strings: each carries the shared
    source prefix, so every element can be handed to ``generate_href`` with the
    element's own unchanged ``n=`` attribute. A single-address citation comes
    back as a one-element list holding the original text, so callers never need
    to special-case the common shape.

    ``n_attr`` is accepted (and ignored) so the signature matches every other
    citation helper in this repo and a caller cannot pass the two the wrong way
    round without a type error being obvious.
    """
    vis = (visible or "").strip()
    if not vis:
        return []
    prefix = _PREFIX.match(vis).group(0)
    rest = vis[len(prefix):]
    if not rest:
        return [vis]
    parts = [p.strip() for p in _ADDR_BOUNDARY.split(rest)]
    return [prefix + p for p in parts if p]


def splittable(visible, loci):
    """Is this really a run of sibling addresses under one siglum? Three refusals.

    **Resolving is not enough**, and this is the trap the whole function exists
    for: the resolver will happily place an address the split *invented*, so a run
    can be cut into links that all work and all point somewhere — a worse failure
    than not splitting, because it looks correct. Every refusal below was found on
    a real ``pwg.txt`` line while generating the upstream change file.

    **Nested markup.** ``<ls>P. 4,3,66, <is n="Vārttika">Vārtt.</is> 2. 3</ls>`` is
    Pāṇini 4.3.66, Vārttikas 2 *and* 3. Splitting yields ``<ls n="P.">3</ls>``,
    which resolves — to sūtra 3, an entirely different place.

    **Impure address.** ``<ls n="MBH. 3,">11087 (p. 572)</ls>`` is one citation
    with a page reference; ``<ls n="HARIV.">83, N. 6</ls>`` is one with a note
    marker; ``Verz. d. Oxf. H. 100,a. 101,b`` uses column letters. A sibling
    address is digits and commas and nothing else.

    **Shape mismatch.** In a genuine run every address has the same number of
    numeric components — ``ṚV. 4,3,13. 10,18,4`` is 3 and 3. A different shape is
    usually a continuation of an *inner* coordinate, and inheriting the outer
    siglum misplaces it.
    """
    if _NESTED.search(visible or ""):
        return False
    prefix = _PREFIX.match(loci[0]).group(0)
    addresses = [text[len(prefix):] if text.startswith(prefix) else text
                 for text in loci]
    if not all(_PURE_ADDRESS.match(a.strip()) for a in addresses):
        return False
    shapes = {len(_COMPONENTS.findall(a)) for a in addresses}
    return len(shapes) == 1


def resolve_loci(dict_code, n_attr, visible):
    """``[(text, href), …]`` for a multi-address citation, or ``None``.

    ``None`` means "render this element exactly as before": it holds one address,
    or it is not a plain address run (:func:`splittable`), or at least one address
    does not resolve and the all-or-nothing rule applies.
    """
    loci = split_ls_loci(n_attr, visible)
    if len(loci) < 2 or not splittable(visible, loci):
        return None
    out = []
    for text in loci:
        try:
            href = lsr.generate_href(dict_code, n_attr, text)
        except Exception:
            href = None
        if not href:
            return None
        out.append((text, href))
    return out


def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    # ---- the case from MG review point 6a, verbatim
    loci = split_ls_loci(None, "ṚV. 4,3,13. 10,18,4")
    check(loci == ["ṚV. 4,3,13.", "ṚV. 10,18,4"],
          "review-6a citation splits into two addresses: %r" % (loci,))

    r = resolve_loci("pwg", None, "ṚV. 4,3,13. 10,18,4")
    check(r is not None and len(r) == 2, "both addresses resolve")
    check(r and "rv04.003" in r[0][1] and r[0][1].endswith("13"),
          "first address still points at ṚV 4.3.13 (%s)" % (r[0][1] if r else None))
    check(r and "rv10.018" in r[1][1] and r[1][1].endswith("04"),
          "second address points at ṚV 10.18.4, not back at the first (%s)"
          % (r[1][1] if r else None))

    # ---- the invariant that makes the split safe: address 1 is byte-identical
    for vis in ("ṚV. 4,3,13. 10,18,4", "AV. 11,4,26. 4,10,7.", "MBH. 12,8081."):
        first = split_ls_loci(None, vis)[0]
        check(vis.startswith(first),
              "first address reconstructs the original prefix of %r" % vis)
        check(lsr.generate_href("pwg", None, first)
              == lsr.generate_href("pwg", None, vis),
              "splitting does not change how %r resolves" % vis)

    # ---- source abbreviations that CONTAIN the split boundary must survive
    for vis in ("AIT. BR. 6,33.", "BHĀG. P. 2,6,35.", "MED. t. 3",
                "ŚAT. BR. 14,5,4,4.", "VERZ. D. OXF. H. 100,a."):
        check(len(split_ls_loci(None, vis)) == 1,
              "multi-word source abbreviation is not torn apart: %r -> %r"
              % (vis, split_ls_loci(None, vis)))

    # ---- a work name carried in n=, address alone in the body
    check(split_ls_loci("ṚV.", "5,15,4.") == ["5,15,4."],
          'n="ṚV." continuation stays one address')
    r2 = resolve_loci("pwg", "ṚV.", "4,3,13. 10,18,4")
    check(r2 is not None and "rv10.018" in r2[1][1],
          "a multi-address body under an n= prefix splits too")

    # ---- no locus at all
    check(split_ls_loci(None, "GORR.") == ["GORR."],
          "a bare abbreviation is one (unresolvable) item, not zero")
    check(resolve_loci("pwg", None, "GORR.") is None, "bare abbreviation -> None")

    # ---- the two refusals that stop a WRONG split (both from real pwg.txt lines)
    nested = 'P. 4,3,66, <is n="Vārttika">Vārtt.</is> 2. 3'
    check(resolve_loci("pwg", None, nested) is None,
          "a body with nested markup is never split — that trailing 3 is "
          "Vārttika 3, and <ls n=\"P.\">3</ls> would resolve to sūtra 3")
    check(resolve_loci("pwg", None, "Spr. 100. 2,3,4") is None,
          "addresses of different shape are not siblings under one siglum")
    for impure, why in (
            ("11087 (p. 572)", "a page reference is not a second address"),
            ("83, N. 6", "a note marker is not a second address"),
            ("Verz. d. Oxf. H. 100,a. 101,b", "column letters are not a plain locus")):
        check(resolve_loci("pwg", "MBH. 3," if impure[0].isdigit() else None,
                           impure) is None, "%s (%r)" % (why, impure))
    check(splittable("ṚV. 4,3,13. 10,18,4",
                     split_ls_loci(None, "ṚV. 4,3,13. 10,18,4")),
          "…while a genuine same-shape run still splits")

    # ---- all or nothing
    check(resolve_loci("pwg", None, "NOTADICT. 1,1. 2,2") is None,
          "an unresolvable work yields None, never a half-linked run")
    check(resolve_loci("pwg", None, "MBH. 12,8081.") is None,
          "a single address yields None (nothing to split)")

    print("ls_split selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest())
