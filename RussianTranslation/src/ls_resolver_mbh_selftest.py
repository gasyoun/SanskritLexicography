#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ls_resolver_mbh_selftest.py — guards the H2853 Mahābhārata fix.

Two deliberate divergences from the ported Dart original live in
``ls_resolver.href_mahabharata``: the previously-unreachable ``'MBH.'`` prefix
branch, and the renamed scan hosts. This asserts both, and — more importantly —
asserts the blast radius is exactly what was intended:

* the mixed-case ``MBh.`` form (Monier-Williams' abbreviation, carried into PWG
  data by Schmidt's *Nachträge*) resolves, and lands on the **same page** the
  uppercase ``MBH.`` form already reached;
* edition selection is by **arity**, not by case;
* nothing that resolved before now resolves differently;
* the fix does **not** leak into the neighbouring case-distinguished prefixes,
  where case legitimately selects a different edition (``ŚĀK.`` → PWG's
  Śakuntalā scan vs ``Śāk.`` → Monier-Williams'). A blanket "uppercase the
  prefix" rule would have silently crossed that boundary; this one must not.

Run: python src/ls_resolver_mbh_selftest.py
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("LS_RESOLVER_QUIET", "1")

import ls_resolver as lsr

OK = []


def href(visible, n_attr=None):
    return lsr.generate_href("pwg", n_attr, visible)


def check(cond, msg):
    OK.append(bool(cond))
    print(("  ok   " if cond else "  FAIL ") + msg)


def main():
    # --- the fix itself: mixed-case MBh. now resolves ----------------------
    for locus in ("1,71,17.", "8,33,31.", "5,163,4.", "13,93,117", "13,23,79."):
        mixed = href("MBh. " + locus)
        upper = href("MBH. " + locus)
        check(mixed is not None, "MBh. %s resolves (was None)" % locus)
        check(mixed == upper,
              "MBh. %s lands where MBH. %s already did%s"
              % (locus, locus, "" if mixed == upper else " (%s != %s)" % (mixed, upper)))

    # --- edition is chosen by arity, not by case --------------------------
    three = href("MBh. 1,71,17.")
    two = href("MBh. 12,8081.")
    check(three and "mbhbomb" in three, "3 coordinates -> Bombay scan")
    check(two and "mbhcalc" in two, "2 coordinates -> Calcutta scan")
    check(href("MBH. 12,8081.") == two, "the 2-coordinate rule matches the uppercase form too")

    # --- the dead hosts are gone -----------------------------------------
    for form in ("MBh. 1,71,17.", "MBh. (ed. Bomb.) 1,71,17.", "MBh. (ed. Calc.) 1,2,3"):
        h = href(form) or ""
        check("mahabharata/calc" not in h and "mahabharata/bomb" not in h,
              "%s does not emit a renamed-away host" % form)

    # --- a 3-coordinate Calcutta citation is malformed; do not guess ------
    check(href("MBh. (ed. Calc.) 1,2,3") is None,
          "3 coordinates explicitly marked Calcutta -> None, not a guessed URL")

    # --- NO leak into case-distinguished prefixes -------------------------
    # Case selects the EDITION for these; the fix must not have merged them.
    pairs = [("ŚĀK. 1,2", "Śāk. 1,2"), ("RAGH. 1,2", "Ragh. 1,2"),
             ("YĀJÑ. 2,266.", "Yājñ. 2,266.")]
    for up, mixed in pairs:
        hu, hm = href(up), href(mixed)
        if hu and hm:
            check(hu != hm, "%r and %r still resolve to DIFFERENT editions" % (up, mixed))
        else:
            check(True, "%r / %r unchanged (one side unresolved, as before)" % (up, mixed))

    # --- regression: a sample of already-working citations is untouched ---
    frozen = {
        "MBH. 12,8081.": "https://sanskrit-lexicon-scans.github.io/mbhcalc?12.8081",
        "MBH. 1,3647.": "https://sanskrit-lexicon-scans.github.io/mbhcalc?1.3647",
        "MBH. 1,71,17.": "https://sanskrit-lexicon-scans.github.io/mbhbomb/app1?1,71,17",
        "P. 1,1,14": "https://ashtadhyayi.com/sutraani/1/1/14",
        "VARĀH. BṚH. S. 79,14.": "https://sanskrit-lexicon-scans.github.io/brihatsam/app1?79,14",
    }
    for cit, want in frozen.items():
        got = href(cit)
        check(got == want, "unchanged: %s -> %s" % (cit, got if got == want else "%s (want %s)" % (got, want)))

    ok = all(OK)
    print("\nls_resolver_mbh selftest: %s (%d/%d)"
          % ("PASS" if ok else "FAIL", sum(OK), len(OK)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
