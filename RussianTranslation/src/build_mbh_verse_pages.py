#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_mbh_verse_pages.py — IAST verse pages for Mahābhārata citations (H3152 A2).

MG review point 1, second half: *sanatana.in «is rather slow and devanagari only.
Can … our datasets … link to our local, IAST version of the text?»*

This builds that local IAST text as static pages, one per **adhyāya**, with an
anchor per verse — so `MBH. 12,8081.` can link to `mbh/12.226.html#v6` instead of
a slow Devanāgarī reader.

Where the text is, and why it took looking twice
------------------------------------------------
The Nīlakaṇṭha vulgate is **not in any working tree**. It is 58.8 MB of
rights-gated third-party text, so CommentaryStrategies keeps it on a local-only
git branch — ``mahabharata-nilakantha-local-only-do-not-push`` — and consumers
read it with ``git show <branch>:<path>``. That is the org's standing convention
for this class of asset; csl-atlas's own
[`f8_mbh_witnesses.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_witnesses.py)
reads it exactly this way.

An earlier pass of this handoff checked the working-tree path, found nothing and
concluded the text was gone. It was not: *checking the file system is not
checking the repository*. The census in
[`NILAKANTHA_VULGATE_CENSUS.md`](https://github.com/gasyoun/CommentaryStrategies/blob/main/mahabharata-nilakantha/NILAKANTHA_VULGATE_CENSUS.md)
was accurate all along — 83,971 verses, all 18 parvans, `mula_iast` already
transliterated.

The two witnesses are NOT treated alike
---------------------------------------
**Nīlakaṇṭha vulgate** — third-party rights are *unclear*, which under the org's
standing policy
([`STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md`](https://github.com/gasyoun/Uprava/blob/main/docs/STANDING_POLICY_RIGHTS_UNCERTAINTY_IS_NOT_A_STOP_2026.md))
is **not** a stop, including for publication. This is what the pages render.

**BORI critical** — © BORI 1999; John D. Smith's stated terms are *"please do not
provide copies of the text to others"*
([`BORI_CRITICAL_SOURCE.md`](https://github.com/gasyoun/CommentaryStrategies/blob/main/mahabharata-nilakantha/BORI_CRITICAL_SOURCE.md)).
That is a **confirmed prohibition**, which the same policy does treat as a stop.
Its 18 files are on the same branch and this generator never opens them: a page
carries the critical *address*, which is a citation, and never the critical
*reading*, which would be a copy. :func:`page_html` has no parameter that could
carry one.

The ṭīkā (Nīlakaṇṭha's commentary, present in the source as ``tika_iast``) is
also not rendered: the ask was the verse, and the commentary would triple the
published bytes for text nobody linked to.

Run::

    python src/build_mbh_verse_pages.py --check          # input availability
    python src/build_mbh_verse_pages.py --out DIR        # build
    python src/build_mbh_verse_pages.py --selftest
"""
import sys, os, io, json, html, argparse, subprocess, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

REPO = os.path.dirname(os.path.dirname(HERE))
ORG = os.path.dirname(REPO)

#: The sibling that owns the text, and the local-only branch it lives on.
SIBLING = os.environ.get("COMMENTARY_STRATEGIES_DIR",
                         os.path.join(ORG, "CommentaryStrategies"))
BRANCH = os.environ.get("MBH_VULGATE_BRANCH",
                        "mahabharata-nilakantha-local-only-do-not-push")
VULGATE_BLOB = "mahabharata-nilakantha/nilakantha_vulgate_full.jsonl"
BORI_BLOB_DIR = "mahabharata-nilakantha/bori-critical"

RIGHTS_VULGATE = "uncertain — may be published (org standing policy)"
RIGHTS_BORI = "PROHIBITED — © BORI 1999, 'do not provide copies to others'"

#: parvan number -> the slug the source uses, for a human label
PARVA_LABEL = {
    1: "Ādiparvan", 2: "Sabhāparvan", 3: "Āraṇyakaparvan", 4: "Virāṭaparvan",
    5: "Udyogaparvan", 6: "Bhīṣmaparvan", 7: "Droṇaparvan", 8: "Karṇaparvan",
    9: "Śalyaparvan", 10: "Sauptikaparvan", 11: "Strīparvan",
    12: "Śāntiparvan", 13: "Anuśāsanaparvan", 14: "Āśvamedhikaparvan",
    15: "Āśramavāsikaparvan", 16: "Mausalaparvan", 17: "Mahāprasthānikaparvan",
    18: "Svargārohaṇaparvan",
}


def _git(args, binary=False):
    return subprocess.run(["git", "-C", SIBLING] + args, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          **({} if binary else dict(encoding="utf-8",
                                                    errors="replace")))


def branch_exists():
    p = _git(["rev-parse", "--verify", "--quiet", BRANCH])
    return p.returncode == 0


def blob_size(path):
    """Size in bytes of a blob on the branch, or ``None``."""
    p = _git(["ls-tree", "-l", BRANCH, "--", path])
    if p.returncode or not p.stdout.strip():
        return None
    try:
        return int(p.stdout.split()[3])
    except (IndexError, ValueError):
        return None


def iter_verses():
    """Stream ``(parvan, adhyaya, shloka, id, iast)`` from the local-only branch.

    Streamed rather than loaded: 58.8 MB of JSON lines, and the caller only ever
    needs one adhyāya's worth at a time.
    """
    p = subprocess.Popen(["git", "-C", SIBLING, "show",
                          "%s:%s" % (BRANCH, VULGATE_BLOB)],
                         stdout=subprocess.PIPE)
    for raw in io.TextIOWrapper(p.stdout, encoding="utf-8"):
        raw = raw.strip()
        if not raw:
            continue
        d = json.loads(raw)
        iast = (d.get("mula_iast") or "").strip()
        if not iast:
            continue
        yield (d.get("parva_no"), d.get("adhyaya"), d.get("shloka"),
               d.get("id"), iast)
    p.stdout.close()
    p.wait()


def inputs_status():
    """``[(name, locator, present, rights)]`` — what a build needs, and its rights."""
    ok = branch_exists()
    vsize = blob_size(VULGATE_BLOB) if ok else None
    bori = blob_size(BORI_BLOB_DIR + "/MBh12.txt") if ok else None
    return [
        ("Nīlakaṇṭha vulgate (text)",
         "%s:%s" % (BRANCH, VULGATE_BLOB), vsize is not None, RIGHTS_VULGATE),
        ("BORI critical (text)",
         "%s:%s/MBh*.txt" % (BRANCH, BORI_BLOB_DIR), bori is not None, RIGHTS_BORI),
    ]


def can_build():
    if not branch_exists():
        return False, ("the local-only branch %r is not in %s — the vulgate text "
                       "lives there, not in any working tree" % (BRANCH, SIBLING))
    if blob_size(VULGATE_BLOB) is None:
        return False, "%s carries no %s" % (BRANCH, VULGATE_BLOB)
    return True, "vulgate text present on %s (%.1f MB)" % (
        BRANCH, blob_size(VULGATE_BLOB) / 1048576.0)


_CSS = """body{font-family:Georgia,serif;max-width:46em;margin:2em auto;padding:0 1em;
line-height:1.6;color:#222}h1{font-size:1.4em}.v{margin:.9em 0;padding-left:3.2em;
text-indent:-3.2em}.n{color:#999;font-size:.85em;display:inline-block;width:2.6em}
.sa{font-style:italic}.src{color:#666;font-size:.85em;margin-top:2em;border-top:1px
solid #ddd;padding-top:.8em}a{color:#06c}"""


def page_html(parvan, adhyaya, verses):
    """One adhyāya page: every verse in IAST, anchored by its śloka number.

    ``verses`` is ``[(shloka, iast)]``. There is deliberately no parameter for a
    critical-edition reading — see the module docstring.
    """
    label = PARVA_LABEL.get(parvan, "parvan %s" % parvan)
    out = ["<!doctype html><meta charset=utf-8>",
           "<title>MBh %s.%s — %s</title>" % (parvan, adhyaya, label),
           "<style>%s</style>" % _CSS,
           "<h1>Mahābhārata %s.%s <small>(%s)</small></h1>"
           % (parvan, adhyaya, html.escape(label))]
    for shloka, iast in verses:
        out.append('<p class=v id="v%s"><span class=n>%s</span>'
                   '<span class=sa>%s</span></p>'
                   % (html.escape(str(shloka)), html.escape(str(shloka)),
                      html.escape(iast).replace("\n", "<br>")))
    out.append('<p class=src>Нилакантхинская вульгата, IAST. Текст сверх этой '
               'редакции — критическое издание BORI — здесь не приводится: '
               'e-text под запретом на распространение, доступен только адрес. '
               'Комментарий Нилакантхи (ṭīkā) есть в источнике и не публикуется '
               'здесь.</p>')
    return "\n".join(out)


def verse_href(parvan, adhyaya, shloka, base="mbh"):
    """The address :mod:`mbh_locus` should point a vulgate coordinate at."""
    return "%s/%s.%s.html#v%s" % (base, parvan, adhyaya, shloka)


def build(out_dir, limit_parvan=None):
    ok, why = can_build()
    if not ok:
        print("REFUSED: %s" % why)
        return 2
    os.makedirs(out_dir, exist_ok=True)
    groups = collections.OrderedDict()
    n_verses = 0
    for parvan, adhyaya, shloka, _vid, iast in iter_verses():
        if limit_parvan and parvan != limit_parvan:
            continue
        groups.setdefault((parvan, adhyaya), []).append((shloka, iast))
        n_verses += 1
    for (parvan, adhyaya), verses in groups.items():
        path = os.path.join(out_dir, "%s.%s.html" % (parvan, adhyaya))
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(page_html(parvan, adhyaya, verses))
    print("wrote %d adhyāya pages (%d verses) -> %s"
          % (len(groups), n_verses, out_dir))
    return 0


def report():
    print("Mahābhārata verse pages (H3152 A2) — input availability\n")
    print("%-28s %-9s %s" % ("input", "present", "rights"))
    print("-" * 78)
    for name, locator, present, rights in inputs_status():
        print("%-28s %-9s %s" % (name, "yes" if present else "NO", rights))
        print("%-28s %s" % ("", locator))
    ok, why = can_build()
    print("\nbuildable: %s — %s" % ("yes" if ok else "NO", why))
    return 0 if ok else 1


def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    p = page_html(12, 226, [(6, "santāpādbhraśyate cāyur"), (7, "tato rājā")])
    check("Mahābhārata 12.226" in p, "the page names its coordinate")
    check('id="v6"' in p and 'id="v7"' in p, "every verse is anchored by its number")
    check("santāpād" in p, "the vulgate reading is rendered")
    check("Śāntiparvan" in p, "the parvan is named in words")
    check("под запретом" in p,
          "the page says the critical reading is withheld, rather than omitting it")

    # the rights rule, mechanically: no parameter can carry a BORI reading in
    import inspect
    params = list(inspect.signature(page_html).parameters)
    check(params == ["parvan", "adhyaya", "verses"],
          "page_html cannot be handed a critical reading: %r" % params)

    check(verse_href(12, 226, 6) == "mbh/12.226.html#v6",
          "the href a coordinate points at: %s" % verse_href(12, 226, 6))

    ok_build, why = can_build()
    check(isinstance(ok_build, bool), "can_build reports a reason: %s" % why)
    if ok_build:
        # the live branch must actually yield the specimen MG named
        want = None
        for parvan, adhyaya, shloka, _vid, iast in iter_verses():
            if (parvan, adhyaya, shloka) == (12, 223, 24):
                want = iast
                break
        check(want and "yajamāno" in want,
              "the branch yields the verse whose pratīka PWG prints at MBH. 12,8081: %r"
              % ((want or "")[:60],))
    else:
        print("  note  branch not available here: %s" % why)

    print("build_mbh_verse_pages selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", help="output directory")
    ap.add_argument("--parvan", type=int, help="build only this parvan")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check or not a.out:
        return report()
    return build(a.out, a.parvan)


if __name__ == "__main__":
    sys.exit(main())
