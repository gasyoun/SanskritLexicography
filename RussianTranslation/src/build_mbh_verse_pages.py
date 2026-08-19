#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_mbh_verse_pages.py — IAST verse pages for Mahābhārata citations (H3152 A2).

MG review point 1, second half: *sanatana.in «is rather slow and devanagari only.
Can … our datasets … link to our local, IAST version of the text?»*

This is the generator for that. **It does not run today**, and the reason is an
input, not a design: neither Mahābhārata e-text is on this machine, and one of the
two may not be republished at all. Both facts are checked at run time and reported
as a refusal with the path that is missing — never as an empty build.

The two witnesses, and what may be done with each
-------------------------------------------------
**Nīlakaṇṭha vulgate** — the text ``12.226.6`` addresses. Harvested from
[sanatana.in](https://sanatana.in/mahabharata/) into
``CommentaryStrategies/mahabharata-nilakantha/nilakantha_vulgate_full.jsonl``
(58.9 MB), **gitignored**; census in
[`NILAKANTHA_VULGATE_CENSUS.md`](https://github.com/gasyoun/CommentaryStrategies/blob/main/mahabharata-nilakantha/NILAKANTHA_VULGATE_CENSUS.md).
Third-party rights are *unclear*, which under the org's standing policy
([`STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md`](https://github.com/gasyoun/Uprava/blob/main/docs/STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md))
is **not** a stop, including for publication. So this side may be rendered.

**BORI critical** — the text ``12,219.6a`` addresses. © BORI 1999; John D. Smith's
stated terms are *"please do not provide copies of the text to others"*
([`BORI_CRITICAL_SOURCE.md`](https://github.com/gasyoun/CommentaryStrategies/blob/main/mahabharata-nilakantha/BORI_CRITICAL_SOURCE.md)).
That is a **confirmed prohibition**, which the same standing policy does treat as
a stop. So the critical *reading* is never written to a published page; only its
*address* is, which is a citation and not a copy. A reader who wants the text goes
to the printed volume — which is what the Russian-editions index
(``data/mbh_russian_editions.tsv``) is for.

Consequence for the card
------------------------
Until the vulgate jsonl is staged, the vulgate coordinate produced by
[`mbh_locus`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mbh_locus.py)
keeps pointing at sanatana.in — slow and Devanāgarī, exactly as MG complained, but
real and reachable. The coordinate itself becomes visible either way, which is the
half of review point 1 that this handoff does close.

Run::

    python src/build_mbh_verse_pages.py --check      # report input availability
    python src/build_mbh_verse_pages.py --out DIR    # build (needs the vulgate text)
    python src/build_mbh_verse_pages.py --selftest
"""
import sys, os, io, json, html, argparse

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

REPO = os.path.dirname(os.path.dirname(HERE))
ORG = os.path.dirname(REPO)

#: The harvested Nīlakaṇṭha vulgate. Gitignored in its own repo; override with
#: ``MBH_VULGATE_JSONL`` if it has been staged somewhere else.
VULGATE_JSONL = os.environ.get(
    "MBH_VULGATE_JSONL",
    os.path.join(ORG, "CommentaryStrategies", "mahabharata-nilakantha",
                 "nilakantha_vulgate_full.jsonl"))

#: The BORI critical e-text directory. Present only to be *reported* — nothing
#: read from here is ever written to a published page.
BORI_DIR = os.environ.get(
    "MBH_BORI_DIR",
    os.path.join(ORG, "CommentaryStrategies", "mahabharata-nilakantha",
                 "bori-critical"))

RIGHTS_VULGATE = "uncertain — may be published (org standing policy)"
RIGHTS_BORI = "PROHIBITED — © BORI 1999, 'do not provide copies to others'"


def inputs_status():
    """``[(name, path, present, rights)]`` — what a build would need, and its rights."""
    return [
        ("Nīlakaṇṭha vulgate (text)", VULGATE_JSONL,
         os.path.exists(VULGATE_JSONL), RIGHTS_VULGATE),
        ("BORI critical (text)", BORI_DIR, os.path.isdir(BORI_DIR), RIGHTS_BORI),
    ]


def can_build():
    """``(bool, reason)`` — only the vulgate side is required, and only it is publishable."""
    if not os.path.exists(VULGATE_JSONL):
        return False, ("the Nīlakaṇṭha vulgate e-text is not on this machine: %s "
                       "(gitignored in CommentaryStrategies; re-harvest with its "
                       "nilakantha_parser.py scrape)" % VULGATE_JSONL)
    return True, "vulgate text present"


def page_html(address, text_iast, bori_address=None):
    """One verse page. Vulgate reading in IAST; the critical side as an ADDRESS only.

    The asymmetry is the rights rule made mechanical: a reading is a copy, an
    address is a citation. Nothing in this function can emit BORI text, because
    it is never passed any.
    """
    crit = ("<p class=crit>Критическое издание (BORI): <b>%s</b> — "
            "адрес приведён без текста: e-text под запретом на распространение.</p>"
            % html.escape(bori_address)) if bori_address else \
           "<p class=crit>Соответствия в критическом издании нет.</p>"
    return (
        "<h1>Mahābhārata %s</h1>\n"
        "<p class=ed>Nīlakaṇṭha vulgate, IAST</p>\n"
        "<p class=verse lang=sa>%s</p>\n%s\n"
        % (html.escape(address), html.escape(text_iast), crit))


def build(out_dir, limit=None):
    ok, why = can_build()
    if not ok:
        print("REFUSED: %s" % why)
        return 2
    os.makedirs(out_dir, exist_ok=True)
    n = 0
    with io.open(VULGATE_JSONL, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            address = "%s.%s.%s" % (d.get("parvan"), d.get("adhyaya"), d.get("shloka"))
            text = d.get("text_iast") or d.get("iast") or ""
            if not text:
                continue
            with io.open(os.path.join(out_dir, address + ".html"), "w",
                         encoding="utf-8") as out:
                out.write(page_html(address, text))
            n += 1
            if limit and n >= limit:
                break
    print("wrote %d verse pages -> %s" % (n, out_dir))
    return 0


def report():
    print("Mahābhārata verse pages (H3152 A2) — input availability\n")
    print("%-28s %-9s %s" % ("input", "present", "rights"))
    print("-" * 78)
    for name, path, present, rights in inputs_status():
        print("%-28s %-9s %s" % (name, "yes" if present else "NO", rights))
        print("%-28s %s" % ("", path))
    ok, why = can_build()
    print("\nbuildable: %s — %s" % ("yes" if ok else "NO", why))
    return 0 if ok else 1


def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    p = page_html("12.226.6", "santāpādbhraśyate cāyur", "12,219.6a")
    check("12.226.6" in p and "santāpād" in p, "the vulgate reading is rendered")
    check("12,219.6a" in p, "the critical ADDRESS is rendered")
    check("под запретом" in p,
          "the page says WHY the critical reading is absent, rather than omitting it")

    p2 = page_html("12.223.24", "yadā ca pṛthivīṃ", None)
    check("Соответствия в критическом издании нет" in p2,
          "a vulgate-only verse says so in words")

    # the rights rule, mechanically: the function has no parameter that could
    # carry BORI text into a page
    import inspect
    params = list(inspect.signature(page_html).parameters)
    check(params == ["address", "text_iast", "bori_address"],
          "page_html takes a critical ADDRESS and no critical text: %r" % params)

    ok_build, why = can_build()
    check(isinstance(ok_build, bool) and isinstance(why, str),
          "can_build reports a reason either way: %s / %s" % (ok_build, why))
    if not ok_build:
        print("  note  A2 is input-blocked on this machine, as expected: %s" % why)

    print("build_mbh_verse_pages selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", help="output directory")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--check", action="store_true", help="report input availability")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check or not a.out:
        return report()
    return build(a.out, a.limit)


if __name__ == "__main__":
    sys.exit(main())
