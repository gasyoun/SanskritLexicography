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


def resolve_loci(dict_code, n_attr, visible):
    """``[(text, href), …]`` for a multi-address citation, or ``None``.

    ``None`` means "render this element exactly as before": either it holds one
    address (nothing to gain), or at least one address does not resolve and the
    all-or-nothing rule applies.
    """
    loci = split_ls_loci(n_attr, visible)
    if len(loci) < 2:
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

    # ---- all or nothing
    check(resolve_loci("pwg", None, "NOTADICT. 1,1. 2,2") is None,
          "an unresolvable work yields None, never a half-linked run")
    check(resolve_loci("pwg", None, "MBH. 12,8081.") is None,
          "a single address yields None (nothing to split)")

    print("ls_split selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest())
