#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ls_links.py — render a pwg_ru ``<ls>`` citation as a link, or mark why it isn't (H2827).

This is a thin **rendering** layer over the resolver the repo already had.

Prior art, and why this module is not a second resolver
------------------------------------------------------
[`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
is a faithful Python port of Cologne's own ``csl-app`` Dart pattern engine and
already turns a PWG ``<ls>`` citation into a scan URL. It powers the public
article site via ``pilot/build_article_site.py::_ls_href``. Nothing was missing —
the re-glue renderer simply never called it, which is why every citation on
[the published re-glue sheet](https://gasyoun.github.io/vote/sheets/h180_reglue.html)
was dead text.

A second candidate was measured before this module was written: Cologne's
precomputed [csl-lslink](https://github.com/sanskrit-lexicon/csl-lslink)
``zip/pwg_lslinks.sqlite.zip`` (277,468 literal ``<ls>``-string → href rows).
Over all 41,115 ``<ls>`` occurrences in ``pwg_ru_translated.jsonl``
([`ls_coverage_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_coverage_probe.py),
15-08-2026):

| resolver | coverage |
|---|---|
| ``ls_resolver.py`` (algorithmic) | **83.6 %** |
| csl-lslink table (precomputed) | 79.3 % |
| union | 83.6 % |

The table wins **zero** citations the resolver misses, and on the 32,586 both
resolve they disagree on **zero** hrefs. So the resolver is a strict superset and
stays primary; the table is kept only as an optional cross-check oracle
(``LsLinks(verify=True)``) — that mutual agreement is the strongest evidence the
port is faithful that the repo has.

What is left after resolution is the answer to "why do citations still lack
links": of the 16.4 % unresolved, some are **bare abbreviations** with no locus
at all (``<ls>GORR.</ls>`` — nothing to point at, unlinkable by construction) and
the rest carry a real locus no pattern covers — the **mintable gap**, the only
bucket worth research. ``classify()`` separates them so a card can show the
difference instead of one undifferentiated dead-text mass.

The MBh e-text layer (H2845)
---------------------------
A scan link answers *where the verse is printed*; it does not answer *what the
verse says*, nor *which edition says it*. So a Mahābhārata citation now also
carries an **e-text** address in the Nīlakaṇṭha vulgate and a four-state
presence verdict against the BORI critical edition, joined out of csl-atlas
[`mbh_vulgate_critical_presence.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_vulgate_critical_presence.csv)
(83,971 verses; method + measured accuracy in
[`MBH_ETEXT_PRESENCE_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_ETEXT_PRESENCE_CENSUS.md)).
It lands *here*, in the shared renderer, so that every sheet built on ``linkify``
gains it at once rather than one sheet builder at a time.

``present/absent`` — the verse stands in the vulgate and not in the critical
edition — is the verdict worth reading: PWG then cites what BORI relegated to
its apparatus. It is rendered ``E†``. The fourth state, ``unchecked``, is
**never** rendered as ``absent``: csl-atlas is an optional sibling checkout, and
where it is missing this layer prints nothing at all instead of implying
absence. What the citation-level verdict is conditional on — the fitted index
lands on the exactly right verse about half the time — is measured in census §6;
read it before quoting a per-citation verdict as a claim about transmission.

Usage::

    from ls_links import LsLinks
    ll = LsLinks()
    ll.resolve('<ls>MBH. 12,8081.</ls>')
    # -> ('hit', 'https://sanskrit-lexicon-scans.github.io/mbhcalc?12.8081')
    ll.etext('https://sanskrit-lexicon-scans.github.io/mbhcalc?12.8081')
    # -> ('present/present', 'https://sanatana.in/…?id=P12_U03_A226_S006', '12.226.6')
    html, stats = ll.linkify(raw_store_body)

Distinct from [`citation_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py),
which fetches a **Russian translation** of the cited verse. They compose: a card
can carry both a scan link (here) and a RU rendering (citation_tm).
"""
import io
import os
import re
import csv
import sys
import html
import shutil
import sqlite3
import zipfile
import tempfile
import collections

os.environ.setdefault("LS_RESOLVER_QUIET", "1")   # bulk render: no per-miss stderr
import ls_resolver as lsr                          # noqa: E402  the canonical resolver

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))      # …/SanskritLexicography
ORG = os.path.dirname(REPO)                        # …/GitHub

#: Where csl-lslink is cloned (cross-check oracle only). Override with CSL_LSLINK_DIR.
LSLINK_DIR = os.environ.get("CSL_LSLINK_DIR", os.path.join(ORG, "csl-lslink"))
CACHE = os.path.join(tempfile.gettempdir(), "csl_lslink_cache")

#: Where csl-atlas is cloned — supplies the MBh e-text layer. Override with CSL_ATLAS_DIR.
ATLAS_DIR = os.environ.get("CSL_ATLAS_DIR", os.path.join(ORG, "csl-atlas"))
MBH_PRESENCE_CSV = os.path.join(
    ATLAS_DIR, "data", "forensic", "mbh_vulgate_critical_presence.csv")

LS_RE = re.compile(r"<ls\b[^>]*>.*?</ls>", re.S)
LS_PARTS = re.compile(r"^<ls\b([^>]*)>(.*)</ls>$", re.S)
N_ATTR = re.compile(r'n="([^"]*)"')
HAS_LOCUS = re.compile(r"\d")

#: resolution outcomes
HIT = "hit"                 #: a scan/text target exists
NO_LOCUS = "no_locus"       #: bare abbreviation — nothing to point at
MINTABLE = "mintable"       #: real locus, no target — the gap worth research

# ------------------------------------------------------------------ MBh e-text layer
#: the scan href ls_resolver already emits for a Mahābhārata citation
MBH_SCAN_HREF = re.compile(r"/mbhcalc\?(\d+)\.(-?\d+)\s*$")
MBH_ETEXT_BASE = "https://sanatana.in/mahabharata/listing/parva/"
#: sanatana.in reader slugs, parvan 1–18 — copied from csl-atlas
#: scripts/forensic/f8_mbh_presence.py, which built the ids this URL uses.
MBH_PARVA_SLUG = {
    1: "adiparva", 2: "sabhaparva", 3: "vanaparva", 4: "virataparva", 5: "udyogaparva",
    6: "bhishmaparva", 7: "dronaparva", 8: "karnaparva", 9: "shalyaparva", 10: "sauptikaparva",
    11: "striparva", 12: "shantiparva", 13: "anushasanaparva", 14: "ashwamedhikaparva",
    15: "ashramavasikaparva", 16: "mausalaparva", 17: "mahaprasthanikaparva",
    18: "swargarohanaparva",
}

#: the four states of the presence verdict. ``UNCHECKED`` is NOT ``absent`` — the
#: whole integrity requirement of H2845 is that the two are never conflated.
PRESENT_PRESENT = "present/present"    #: verified in both recensions
PRESENT_ABSENT = "present/absent"      #: vulgate-only — the finding worth having
ABSENT_PRESENT = "absent/present"      #: mis-fitted locus, or a different vulgate printing
UNCHECKED = "unchecked/unchecked"      #: not looked up — say nothing about presence

#: why a citation came back ``unchecked``, so a card never has to guess
NO_TABLE = "no-presence-table"         #: csl-atlas not cloned / file absent
NOT_MBH = "not-mbh"                    #: not a Mahābhārata citation at all
NO_ROW = "locus-not-in-concordance"    #: the fitted index has no verse at that number


def _ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


# --------------------------------------------------------------- optional oracle
def _extract_table(dict_code="pwg"):
    """Extract <dict>_lslinks.sqlite from the csl-lslink zip, cached."""
    zpath = os.path.join(LSLINK_DIR, "zip", "%s_lslinks.sqlite.zip" % dict_code)
    if not os.path.exists(zpath):
        raise FileNotFoundError(
            "csl-lslink zip not found: %s — clone sanskrit-lexicon/csl-lslink next "
            "to this repo, or set CSL_LSLINK_DIR. Only needed for verify=True."
            % zpath)
    target = os.path.join(CACHE, dict_code, "%s_lslinks.sqlite" % dict_code)
    if os.path.exists(target) and os.path.getmtime(target) >= os.path.getmtime(zpath):
        return target
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with zipfile.ZipFile(zpath) as zf:
        member = next(n for n in zf.namelist() if n.endswith(".sqlite"))
        with zf.open(member) as src, io.open(target, "wb") as dst:
            shutil.copyfileobj(src, dst)
    return target


class MbhEtext(object):
    """The Mahābhārata e-text address + presence verdict behind a scan link (H2845).

    A ``<ls>MBH. 12,8081</ls>`` already resolves to a Cologne **scan** page. This
    adds the second half MG asked for: the same verse in the Nīlakaṇṭha vulgate
    **e-text**, plus a verdict on whether it also stands in the BORI critical
    edition. Both come from csl-atlas
    [`mbh_vulgate_critical_presence.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_vulgate_critical_presence.csv)
    — 83,971 vulgate verses carrying `(parvan, adhyaya, shloka, upaparva,
    calibrated_N, vulgate, critical)`. Nothing is recomputed here; this is a
    lookup and a URL template, exactly as
    [`MBH_ETEXT_PRESENCE_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_ETEXT_PRESENCE_CENSUS.md) §2
    specifies.

    Two honesty properties, both load-bearing:

    * **The table is optional.** csl-atlas is a sibling checkout, not a
      dependency. When it is absent, every lookup returns ``UNCHECKED`` with
      reason ``NO_TABLE`` and the renderer prints no presence claim at all.
    * **``unchecked`` is never rendered as ``absent``.** A citation whose number
      the fitted index cannot place returns ``UNCHECKED``/``NO_ROW``, not
      "absent from the vulgate".

    The lookup key is ``(parvan, calibrated_N)`` read off the resolved scan href,
    so this layer never re-parses a citation — one parser, one truth. Note that
    83,971 verses carry only 80,376 distinct calibrated numbers (census §8.5);
    the first verse wins, matching how csl-atlas builds its own locus lookup.
    """

    def __init__(self, path=None):
        self.path = path or MBH_PRESENCE_CSV
        self._index = None
        self.loaded = False

    @property
    def index(self):
        if self._index is None:
            self._index = {}
            try:
                with io.open(self.path, encoding="utf-8", newline="") as f:
                    for row in csv.DictReader(f):
                        try:
                            key = (int(row["parvan"]), int(row["calibrated_N"]))
                        except (KeyError, TypeError, ValueError):
                            continue
                        if key in self._index:
                            continue          # repeated calibrated_N — keep the first
                        self._index[key] = (int(row["upaparva"]), int(row["adhyaya"]),
                                            int(row["shloka"]), row["vulgate"],
                                            row["critical"])
                self.loaded = True
            except (IOError, OSError):
                self.loaded = False           # sibling repo not cloned — stay silent
        return self._index

    @staticmethod
    def url(parvan, upaparva, adhyaya, shloka):
        """Deep link into the sanatana.in Nīlakaṇṭha reader, or ``None``.

        The ``id`` is the ``div.shloka`` id the csl-atlas harvest recorded, so the
        link is verifiable against our own data rather than guessed."""
        slug = MBH_PARVA_SLUG.get(parvan)
        if not slug:
            return None
        return ("%s%s?id=P%02d_U%02d_A%03d_S%03d"
                % (MBH_ETEXT_BASE, slug, parvan, upaparva, adhyaya, shloka))

    def for_scan_href(self, href):
        """``(verdict, etext_url_or_None, address_or_reason)`` for a resolved href.

        ``verdict`` is one of the four states; when it is ``UNCHECKED`` the third
        element names *why*, so a card can say "not looked up" instead of
        implying absence."""
        m = MBH_SCAN_HREF.search(href or "")
        if not m:
            return UNCHECKED, None, NOT_MBH
        idx = self.index
        if not self.loaded:
            return UNCHECKED, None, NO_TABLE
        hit = idx.get((int(m.group(1)), int(m.group(2))))
        if hit is None:
            return UNCHECKED, None, NO_ROW
        upaparva, adhyaya, shloka, vulgate, critical = hit
        parvan = int(m.group(1))
        verdict = "%s/%s" % (vulgate, critical)
        if verdict not in (PRESENT_PRESENT, PRESENT_ABSENT, ABSENT_PRESENT):
            # e.g. the 231 service records scored "absent/unchecked" — no claim to make
            return UNCHECKED, None, "%d.%d.%d" % (parvan, adhyaya, shloka)
        return (verdict, self.url(parvan, upaparva, adhyaya, shloka),
                "%d.%d.%d" % (parvan, adhyaya, shloka))


class LsLinks(object):
    """Resolve + render PWG ``<ls>`` citations.

    ``verify=True`` additionally loads the csl-lslink table and records every
    disagreement in ``self.disagreements`` — an audit mode, not the render path.

    ``etext=True`` (the default) adds the MBh e-text link + presence verdict
    beside the scan link when the csl-atlas sibling checkout is present; with it
    absent, rendering is byte-identical to before.
    """

    def __init__(self, dict_code="pwg", verify=False, etext=True):
        self.dict_code = dict_code
        self.verify = verify
        self._table = None
        self.disagreements = []
        self.mbh = MbhEtext() if etext else None

    @property
    def table(self):
        if self._table is None:
            con = sqlite3.connect(_extract_table(self.dict_code))
            self._table = {_ws(k): d for k, d in
                           con.execute("select key, data from keydoc_glob1")}
            con.close()
        return self._table

    # ------------------------------------------------------------------ resolve
    @staticmethod
    def parts(tag):
        """``(n_attribute_or_None, visible_text)`` for one raw ``<ls …>…</ls>``."""
        m = LS_PARTS.match(_ws(tag))
        if not m:
            return None, _ws(tag)
        na = N_ATTR.search(m.group(1) or "")
        return (na.group(1) if na else None), m.group(2).strip()

    @staticmethod
    def classify(visible):
        """Why an unresolved citation is unresolved — the two buckets differ."""
        return MINTABLE if HAS_LOCUS.search(visible or "") else NO_LOCUS

    def resolve(self, tag):
        """``(status, href_or_None)``. Never invents a target."""
        n_attr, visible = self.parts(tag)
        try:
            href = lsr.generate_href(self.dict_code, n_attr, visible) or None
        except Exception:
            href = None
        if self.verify:
            other = self.table.get(_ws(tag))
            if other is None:
                m = LS_PARTS.match(_ws(tag))
                if m:
                    trimmed = m.group(2).strip().rstrip(". ").strip()
                    other = self.table.get("<ls%s>%s</ls>" % (m.group(1), trimmed))
            if other and href and other.rstrip("/") != href.rstrip("/"):
                self.disagreements.append((tag, href, other))
            elif other and not href:
                self.disagreements.append((tag, None, other))
        if href:
            return HIT, href
        return self.classify(visible), None

    def etext(self, href):
        """``(verdict, url_or_None, address_or_reason)`` for an already-resolved href.

        Always answers — a non-MBh or unplaceable citation comes back
        ``UNCHECKED``, never ``absent``."""
        if self.mbh is None:
            return UNCHECKED, None, NO_TABLE
        return self.mbh.for_scan_href(href)

    # ------------------------------------------------------------------- render
    def linkify(self, raw_text, classes=None):
        """Rewrite every ``<ls>`` in a **raw** store body as a link or a marked gap.

        Takes the body exactly as the store keeps it — unescaped, with its PWG
        markup (``{#…#}``, ``<lex>``, ``<div n="p">``) intact. Everything that is
        not an ``<ls>`` element is HTML-escaped here, so the caller must NOT
        pre-escape: doing so hides the ``<ls>`` tags behind ``&lt;ls&gt;`` and
        silently drops the join to zero (the bug this docstring exists to
        prevent — it cost one full build during H2827).

        Returns ``(html, Counter)`` with HIT / NO_LOCUS / MINTABLE tallies, plus an
        ``etext:<verdict>`` tally for every MBh citation the resolver reached, so a
        sheet can report the four-state distribution it actually rendered.
        """
        cls = {HIT: "ls-hit", NO_LOCUS: "ls-nolocus", MINTABLE: "ls-mintable"}
        cls.update(classes or {})
        stats = collections.Counter()
        out, pos = [], 0
        raw_text = raw_text or ""
        for m in LS_RE.finditer(raw_text):
            out.append(html.escape(raw_text[pos:m.start()]))
            pos = m.end()
            tag = m.group(0)
            status, href = self.resolve(tag)
            stats[status] += 1
            n_attr, visible = self.parts(tag)
            # the n="…" continuation prefix is context the reader needs on screen
            shown = html.escape((n_attr or "") + visible)
            if status == HIT:
                out.append('<a class="%s" href="%s" target="_blank" rel="noopener" '
                           'title="Cologne scan / text">%s</a>'
                           % (cls[HIT], html.escape(href, quote=True), shown))
                out.append(self._etext_html(href, stats))
                continue
            mark = "∅" if status == NO_LOCUS else "⚑"
            title = ("bare abbreviation — no locus to point at"
                     if status == NO_LOCUS else
                     "locus present, no resolver pattern — mintable gap")
            out.append('<span class="%s" title="%s">%s<sup>%s</sup></span>'
                       % (cls[status], title, shown, mark))
        out.append(html.escape(raw_text[pos:]))
        return "".join(out), stats

    def _etext_html(self, href, stats):
        """The e-text sibling of a resolved scan link — markup, or "" when silent.

        Silence is deliberate in two cases: the citation is not a Mahābhārata one,
        and the csl-atlas table is not on this machine. Neither is evidence of
        anything, so neither prints a verdict. Only ``NO_ROW`` — a real MBh
        citation the fitted index could not place — surfaces, as a muted
        *unchecked* mark that explicitly does not say *absent*."""
        verdict, url, note = self.etext(href)
        if note in (NOT_MBH, NO_TABLE):
            return ""
        stats["etext:" + verdict] += 1
        if verdict == UNCHECKED:
            return ('<span class="ls-etext-unchecked" title="e-text presence unchecked '
                    '(%s) — this is NOT a claim of absence"><sup>?</sup></span>'
                    % html.escape(note, quote=True))
        if not url:
            return ""
        vulgate_only = verdict == PRESENT_ABSENT
        mark = "E†" if vulgate_only else "E"
        title = ("Nīlakaṇṭha vulgate e-text %s — %s" %
                 (note, "vulgate-only: the BORI critical edition relegates this verse "
                        "to its apparatus" if vulgate_only else
                        "present in the BORI critical edition too"
                        if verdict == PRESENT_PRESENT else
                        "in the critical edition but not at this vulgate address"))
        return ('<a class="ls-etext ls-v-%s" href="%s" target="_blank" rel="noopener" '
                'title="%s"><sup>%s</sup></a>'
                % (verdict.replace("/", "-"), html.escape(url, quote=True),
                   html.escape(title, quote=True), mark))


# --------------------------------------------------------------------- selftest
def selftest():
    """Fixture selftest — runs in CI (RussianTranslation gates job)."""
    ll = LsLinks()
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    # the reglue.md motivating citation
    st, href = ll.resolve("<ls>MBH. 12,8081.</ls>")
    check(st == HIT and href and href.endswith("12.8081"),
          "MBH. 12,8081. -> %s (%s)" % (href, st))

    # the period-less form must resolve identically
    check(ll.resolve("<ls>MBH. 12,8081</ls>") == (st, href),
          "period-less form resolves identically")

    # the n="" continuation shape, which carries its prefix in an attribute
    st3, href3 = ll.resolve('<ls n="ṚV.">5,15,4.</ls>')
    check(st3 == HIT and href3 and "rv05.015" in href3,
          'continuation n="ṚV." 5,15,4 -> %s' % href3)

    # a bare abbreviation is NOT a gap to mint — it has no locus
    check(ll.resolve("<ls>GORR.</ls>")[0] == NO_LOCUS,
          "bare abbreviation -> no_locus, not mintable")

    # an unknown source with a locus IS a mintable gap, and gets no href
    st5, href5 = ll.resolve("<ls>NOTADICT. 9,9,9</ls>")
    check(st5 == MINTABLE and href5 is None, "unknown source -> mintable, no href")

    # linkify escapes its own plain text and tallies both buckets
    out, stats = ll.linkify("идти <ls>MBH. 12,8081.</ls> и <ls>GORR.</ls> <b>")
    check("&lt;b&gt;" in out, "linkify escapes non-<ls> markup")
    check(stats[HIT] == 1 and stats[NO_LOCUS] == 1,
          "linkify tally: %d hit / %d no-locus / %d mintable"
          % (stats[HIT], stats[NO_LOCUS], stats[MINTABLE]))
    check('href="https://sanskrit-lexicon-scans.github.io/mbhcalc?12.8081"' in out,
          "linkify emits the resolved href")

    # ---------------------------------------------------------- MBh e-text layer
    # A three-row fixture stands in for csl-atlas so the four states are exercised
    # even where the sibling repo is not cloned (CI). Columns are the real ones.
    fx = os.path.join(tempfile.mkdtemp(prefix="ls_links_etext_"), "presence.csv")
    with io.open(fx, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["parvan", "adhyaya", "shloka", "upaparva", "continuous_C",
                    "calibrated_N", "vulgate", "critical"])
        w.writerow([12, 226, 6, 3, 8077, 8081, "present", "present"])
        w.writerow([12, 223, 24, 3, 7967, 7971, "present", "absent"])
        w.writerow([1, 1, 1, 1, 1, -45, "absent", "unchecked"])
    fll = LsLinks()
    fll.mbh = MbhEtext(fx)

    v, url, note = fll.etext("https://sanskrit-lexicon-scans.github.io/mbhcalc?12.8081")
    check(v == PRESENT_PRESENT and url ==
          "https://sanatana.in/mahabharata/listing/parva/shantiparva"
          "?id=P12_U03_A226_S006" and note == "12.226.6",
          "etext 12,8081 -> %s %s" % (v, url))

    v2, url2, _ = fll.etext("https://sanskrit-lexicon-scans.github.io/mbhcalc?12.7971")
    check(v2 == PRESENT_ABSENT and url2.endswith("id=P12_U03_A223_S024"),
          "vulgate-only verdict + its own e-text address (%s)" % v2)

    # the three ways an answer must come back UNCHECKED rather than "absent"
    check(fll.etext("https://sanskrit-lexicon-scans.github.io/mbhcalc?12.999999")
          == (UNCHECKED, None, NO_ROW), "unplaced locus -> unchecked, reason NO_ROW")
    check(fll.etext("https://www.sanskrit-lexicon.uni-koeln.de/scans/x")[2] == NOT_MBH,
          "non-MBh citation -> unchecked, reason NOT_MBH")
    check(MbhEtext(fx + ".missing").for_scan_href(
          "https://sanskrit-lexicon-scans.github.io/mbhcalc?12.8081")
          == (UNCHECKED, None, NO_TABLE), "no csl-atlas -> unchecked, reason NO_TABLE")
    # a service record scores absent/unchecked upstream: no claim, and no link
    check(fll.etext("https://sanskrit-lexicon-scans.github.io/mbhcalc?1.-45")[0] == UNCHECKED,
          "absent/unchecked upstream row -> unchecked, no link")

    eout, estats = fll.linkify("<ls>MBH. 12,8081.</ls> и <ls>GORR.</ls>")
    check("P12_U03_A226_S006" in eout and 'class="ls-etext ls-v-present-present"' in eout,
          "linkify renders the e-text link beside the scan link")
    check(estats["etext:" + PRESENT_PRESENT] == 1,
          "linkify tallies the four-state verdict it rendered")
    # a card must never grow an e-text claim where csl-atlas is absent
    plain, _ = LsLinks(etext=False).linkify("<ls>MBH. 12,8081.</ls>")
    check("sanatana.in" not in plain, "etext=False renders exactly as before")

    # when the real csl-atlas table IS on this machine, hold it to the same answer
    live = MbhEtext()
    live.index                                   # trigger the load
    if live.loaded:
        lv, lurl, _ = live.for_scan_href(
            "https://sanskrit-lexicon-scans.github.io/mbhcalc?12.8081")
        check(lurl == "https://sanatana.in/mahabharata/listing/parva/shantiparva"
                      "?id=P12_U03_A226_S006",
              "live csl-atlas table agrees on the specimen (%s)" % lv)
    else:
        print("  skip  live csl-atlas presence table not on this machine (%s)"
              % MBH_PRESENCE_CSV)

    print("ls_links selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(selftest())
