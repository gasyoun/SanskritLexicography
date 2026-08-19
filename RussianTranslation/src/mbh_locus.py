#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mbh_locus.py — every coordinate a Mahābhārata citation has, in one object (H3152).

MG review point 1: ``MBH. 12,8081.E`` shows a mute ``E``; show the vulgate address
``12.226.6`` instead, link *from* it, and say whether the critical edition carries
the verse — so the Russian translation of the quoted line can be found.

Three coordinates, three different kinds of fact
-----------------------------------------------
=================  ===========================  =====================================
coordinate         where it comes from          how much it is worth
=================  ===========================  =====================================
Calcutta           **printed in PWG**            certain — this is the datum
``12,8081``
vulgate            csl-atlas **fitted index**    exactly right 49.4 % of the time
``12.226.6``       (``calibrated_N``)
critical           csl-atlas ``bori_locus``,     certain *given* the vulgate address,
``12,219.6a``      joined on the vulgate address so it inherits the 49.4 %
=================  ===========================  =====================================

Only the first is knowledge. The other two are the output of a fitted index, and
this module refuses to let a caller forget that: :attr:`MbhLocus.fitted` is always
true for the vulgate/critical pair and :data:`FITTED_EXACT_RATE` carries the
measured number, so the renderer can mark the coordinate as approximate rather
than printing it as the verse's address.

Why that matters is not theoretical. MG's own specimen is a **miss**: csl-atlas
[`f8_specimen_mbh_12_8081.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f8_specimen_mbh_12_8081.json)
records that the pratīka PWG prints for ``MBH. 12,8081`` —
``yadā ca pṛthivīṃ sarvāṃ yajamāno 'nuparyagāḥ`` — actually stands at vulgate
**12.223.24**, and that the fitted address 12.226.6 holds a different verse
(``contains_pratika: false``). The printed number and the fitted one differ by 110
ślokas. Rendering ``= Вульг. 12.226.6`` as a bare equals sign would state a
falsehood about that citation; rendering ``≈ Вульг. 12.226.6`` states what we
actually know. This is the same discipline as H2845's ``unchecked`` ≠ ``absent``,
one step further out.

Where the numbers come from
---------------------------
[`mbh_vulgate_critical_presence.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_vulgate_critical_presence.csv)
(83,971 vulgate verses) — method and accuracy in
[`MBH_ETEXT_PRESENCE_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_ETEXT_PRESENCE_CENSUS.md).
``FITTED_EXACT_RATE`` is ``fitted_index_agreement_within_k_slokas["0"]`` from
[`f8_quote_lane_report.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/f8_quote_lane_report.json),
measured over the 6,912 PWG citations whose printed pratīka could be retrieved.

The ``bori_locus`` column is what this module adds to what
[`ls_links.MbhEtext`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_links.py)
already read: the column has been in csl-atlas since H2845 and had **never been
surfaced to a reader**.

csl-atlas is optional (PLAN, ARCHITECTURE §2)
---------------------------------------------
It is a sibling checkout, not a dependency. Absent, every lookup answers
``UNCHECKED`` and the renderer prints nothing about the critical edition.
``unchecked`` is never rendered as ``absent``: saying "this verse is not in the
critical edition" when we merely did not look is inventing a fact about the
manuscript tradition.

Run: ``python src/mbh_locus.py --selftest``
"""
import sys, os, io, csv, re, argparse

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("LS_RESOLVER_QUIET", "1")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ls_resolver as lsr                                            # noqa: E402
from ls_links import (MBH_PRESENCE_CSV, MBH_SCAN_HREF, MbhEtext,     # noqa: E402
                      PRESENT_PRESENT, PRESENT_ABSENT, ABSENT_PRESENT)

#: presence states, in the words a card uses. Deliberately NOT the four
#: ``vulgate/critical`` strings of ls_links: a reader is being told one thing —
#: does the critical edition carry this verse — not a two-axis verdict.
PRESENT = "present"              #: in the vulgate and in the critical edition
VULGATE_ONLY = "vulgate_only"    #: PWG cites what BORI relegated to its apparatus
ABSENT = "absent"                #: at this vulgate address the vulgate has nothing
UNCHECKED = "unchecked"          #: not looked up — say nothing at all

#: why an answer is ``unchecked``, so a card never has to guess
NO_TABLE = "no-presence-table"       #: csl-atlas not cloned
NO_ROW = "locus-not-in-concordance"  #: the fitted index has no verse at that number
NO_CLAIM = "upstream-unadjudicated"  #: the 231 ``absent/unchecked`` service records

_VERDICT_TO_PRESENCE = {
    PRESENT_PRESENT: PRESENT,
    PRESENT_ABSENT: VULGATE_ONLY,
    ABSENT_PRESENT: ABSENT,
}

#: Measured exact-hit rate of the fitted index — csl-atlas f8_quote_lane_report,
#: ``fitted_index_agreement_within_k_slokas["0"]`` over 6,912 retrievable PWG
#: citations. Within ±2 ślokas it is 0.680; within ±50, 0.856.
FITTED_EXACT_RATE = 0.494
FITTED_WITHIN_2_RATE = 0.680

#: ``MBH. P,N`` as PWG prints it, off the visible text of an ``<ls>``
_CITED = re.compile(r"^\s*MBH\.?\s*(\d{1,2})\s*,\s*(\d{1,5})", re.I)

#: Where our own IAST verse pages are published, relative to the article site.
#: Override with ``MBH_IAST_BASE`` when the site is served from elsewhere.
IAST_BASE = os.environ.get("MBH_IAST_BASE", "mbh")


class MbhLocus(object):
    """The coordinates of one Mahābhārata citation. Immutable, cheap, printable."""

    __slots__ = ("parvan", "calcutta_n", "vulgate", "bori", "scan_href",
                 "vulgate_href", "presence", "reason")

    def __init__(self, parvan, calcutta_n, vulgate=None, bori=None,
                 scan_href=None, vulgate_href=None, presence=UNCHECKED,
                 reason=None):
        self.parvan = parvan
        self.calcutta_n = calcutta_n
        self.vulgate = vulgate
        self.bori = bori
        self.scan_href = scan_href
        self.vulgate_href = vulgate_href
        self.presence = presence
        self.reason = reason

    @property
    def calcutta(self):
        """The citation exactly as PWG prints it — the one certain coordinate."""
        return "%d,%d" % (self.parvan, self.calcutta_n)

    @property
    def fitted(self):
        """True whenever a vulgate coordinate is being offered at all.

        There is no lane in this module that produces a *verified* vulgate
        address: placing a citation by its printed pratīka needs a text search,
        which is csl-atlas's quote lane, not a lookup. This property exists so a
        renderer asks the object rather than assuming.
        """
        return self.vulgate is not None

    @property
    def iast_href(self):
        """Our own IAST page for the vulgate coordinate, or ``None``.

        This is the half of MG review point 1 that a coordinate alone does not
        close: *«sanatana.in is rather slow and devanagari only … link to our
        local, IAST version»*. Built by
        [`build_mbh_verse_pages.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_mbh_verse_pages.py)
        from the Nīlakaṇṭha vulgate — one static page per adhyāya, anchored per
        verse. ``vulgate_href`` (sanatana.in) stays available beside it as the
        source of record.
        """
        if not self.vulgate:
            return None
        return "%s/%s.html#v%s" % (IAST_BASE, self.vulgate.rsplit(".", 1)[0],
                                   self.vulgate.rsplit(".", 1)[1])

    @property
    def bori_href(self):
        """``None``, always — and that is a statement, not an omission.

        The BORI critical e-text (Tokunaga/Smith) is © BORI 1999 and its stated
        terms are *"please do not provide copies of the text to others"*
        ([`BORI_CRITICAL_SOURCE.md`](https://github.com/gasyoun/CommentaryStrategies/blob/main/mahabharata-nilakantha/BORI_CRITICAL_SOURCE.md)),
        so there is no public reading surface of ours to point at, and inventing a
        third-party deep link we have not verified would be worse than none. The
        critical address is therefore rendered as text: its job is to let a reader
        find the printed volume and the Russian translation keyed to it —
        see ``data/mbh_russian_editions.tsv``.
        """
        return None

    def __repr__(self):
        return ("MbhLocus(%s -> vulgate=%s bori=%s presence=%s%s)"
                % (self.calcutta, self.vulgate, self.bori, self.presence,
                   " reason=%s" % self.reason if self.reason else ""))


class MbhLocusIndex(object):
    """``(parvan, calibrated_N)`` → the csl-atlas row, loaded once, lazily.

    Reuses [`ls_links.MbhEtext`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_links.py)
    for the vulgate address and the sanatana.in URL — one parser, one truth — and
    reads the CSV a second time only for the column ``MbhEtext`` does not keep,
    ``bori_locus``.
    """

    def __init__(self, path=None):
        self.path = path or MBH_PRESENCE_CSV
        self.etext = MbhEtext(self.path)
        self._bori = None

    @property
    def bori_index(self):
        if self._bori is None:
            self._bori = {}
            try:
                with io.open(self.path, encoding="utf-8", newline="") as f:
                    for row in csv.DictReader(f):
                        try:
                            key = (int(row["parvan"]), int(row["calibrated_N"]))
                        except (KeyError, TypeError, ValueError):
                            continue
                        if key in self._bori:
                            continue        # repeated calibrated_N — keep the first
                        self._bori[key] = row.get("bori_locus") or None
            except (IOError, OSError):
                self._bori = {}
        return self._bori

    @property
    def loaded(self):
        self.etext.index                     # trigger the load
        return self.etext.loaded

    def resolve(self, parvan, calcutta_n):
        """``MbhLocus`` for one PWG Mahābhārata citation. Never returns ``None``.

        A missing table, an unplaceable number and an unadjudicated upstream row
        all come back as ``UNCHECKED`` carrying a distinct ``reason``, because a
        card that must stay silent still deserves to know *why* it is silent.
        """
        try:
            scan = lsr.generate_href("pwg", None, "MBH. %d,%d" % (parvan, calcutta_n))
        except Exception:
            scan = None
        loc = MbhLocus(parvan, calcutta_n, scan_href=scan)
        if not self.loaded:
            loc.reason = NO_TABLE
            return loc
        verdict, url, note = self.etext.for_scan_href(
            scan or "https://sanskrit-lexicon-scans.github.io/mbhcalc?%d.%d"
            % (parvan, calcutta_n))
        presence = _VERDICT_TO_PRESENCE.get(verdict)
        if presence is None:
            # ls_links already distinguishes "no row" from "upstream made no claim"
            loc.reason = NO_ROW if note == "locus-not-in-concordance" else NO_CLAIM
            return loc
        loc.presence = presence
        loc.vulgate = note
        loc.vulgate_href = url
        loc.bori = self.bori_index.get((parvan, calcutta_n))
        return loc

    def resolve_citation(self, visible, n_attr=None):
        """``MbhLocus`` for the visible text of an ``<ls>``, or ``None``.

        ``None`` means "not a Mahābhārata citation in ``P,N`` form" — a Bombay- or
        adhyāya-addressed MBh citation is out of scope for the fitted index and
        must not be silently coerced into it.
        """
        m = _CITED.match((n_attr or "") + (visible or "")) or _CITED.match(visible or "")
        if not m:
            return None
        return self.resolve(int(m.group(1)), int(m.group(2)))


_DEFAULT = None


def resolve(parvan, calcutta_n):
    """Module-level convenience over one shared, lazily-loaded index."""
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = MbhLocusIndex()
    return _DEFAULT.resolve(parvan, calcutta_n)


def resolve_citation(visible, n_attr=None):
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = MbhLocusIndex()
    return _DEFAULT.resolve_citation(visible, n_attr)


# --------------------------------------------------------------------- selftest
def _fixture(tmpdir):
    """A four-row stand-in for csl-atlas, so all four states run in CI."""
    path = os.path.join(tmpdir, "presence.csv")
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["parvan", "adhyaya", "shloka", "upaparva", "continuous_C",
                    "calibrated_N", "vulgate", "critical", "bori_locus"])
        # the specimen: in both recensions, and the row that carries bori_locus
        w.writerow([12, 226, 6, 3, 8077, 8081, "present", "present", "12,219.6a"])
        # vulgate-only: PWG cites what BORI put in its apparatus
        w.writerow([12, 223, 24, 3, 7967, 7971, "present", "absent", ""])
        # an upstream service record — no claim to make either way
        w.writerow([1, 1, 1, 1, 1, -45, "absent", "unchecked", "01,1.1A"])
    return path


def selftest():
    import tempfile
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    idx = MbhLocusIndex(_fixture(tempfile.mkdtemp(prefix="mbh_locus_")))

    # ---- A1 acceptance row 1: the specimen resolves to all three coordinates
    loc = idx.resolve(12, 8081)
    check(loc.calcutta == "12,8081", "the printed Calcutta number is preserved verbatim")
    check(loc.vulgate == "12.226.6",
          "MBH. 12,8081 -> vulgate 12.226.6 (%s)" % loc.vulgate)
    check(loc.bori == "12,219.6a",
          "bori_locus is surfaced at last: %s" % loc.bori)
    check(loc.presence == PRESENT, "presence = present (%s)" % loc.presence)
    check(loc.scan_href and loc.scan_href.endswith("12.8081"),
          "the Cologne scan link is still there: %s" % loc.scan_href)
    check(loc.vulgate_href == "https://sanatana.in/mahabharata/listing/parva/"
                              "shantiparva?id=P12_U03_A226_S006",
          "the vulgate address deep-links into the source reader: %s" % loc.vulgate_href)
    check(loc.iast_href == "mbh/12.226.html#v6",
          "…and into OUR fast IAST page, which is what MG asked for: %s"
          % loc.iast_href)
    check(idx.resolve(12, 999999).iast_href is None,
          "no coordinate, no IAST page — the link is never invented")

    # ---- the honesty property this module exists for
    check(loc.fitted is True,
          "a vulgate coordinate always declares itself fitted, never verified")
    check(loc.bori_href is None,
          "no critical-edition link is invented — the e-text is not redistributable")
    check(0.4 < FITTED_EXACT_RATE < 0.6,
          "the measured exact-hit rate travels with the module (%.3f)"
          % FITTED_EXACT_RATE)

    # ---- A1 acceptance row 2: vulgate-only has no critical address
    v = idx.resolve(12, 7971)
    check(v.presence == VULGATE_ONLY, "vulgate-only verdict (%s)" % v.presence)
    check(v.bori is None,
          "a vulgate-only verse carries no critical address (%r)" % v.bori)
    check(v.vulgate == "12.223.24", "…but still has its own vulgate address")

    # ---- A1 acceptance row 3: no csl-atlas -> unchecked, and NEVER absent
    gone = MbhLocusIndex(idx.path + ".missing")
    g = gone.resolve(12, 8081)
    check(g.presence == UNCHECKED and g.reason == NO_TABLE,
          "csl-atlas absent -> unchecked/%s" % g.reason)
    check(g.presence != ABSENT,
          "an unchecked citation is NEVER reported as absent from the critical edition")
    check(g.vulgate is None and g.fitted is False,
          "with no table there is no coordinate to offer, fitted or otherwise")
    check(g.scan_href, "the Cologne scan link survives without csl-atlas")

    # ---- an address the fitted index cannot place
    nr = idx.resolve(12, 999999)
    check(nr.presence == UNCHECKED and nr.reason == NO_ROW,
          "unplaceable number -> unchecked/%s, not absent" % nr.reason)

    # ---- an upstream row that adjudicated nothing
    nc = idx.resolve(1, -45)
    check(nc.presence == UNCHECKED and nc.reason == NO_CLAIM,
          "upstream absent/unchecked -> unchecked/%s" % nc.reason)

    # ---- parsing a citation as the renderer will hand it over
    c = idx.resolve_citation("MBH. 12,8081.")
    check(c and c.vulgate == "12.226.6", "resolve_citation on the visible text")
    check(idx.resolve_citation("MBH. 12,8081") is not None,
          "the period-less form parses identically")
    check(idx.resolve_citation("ṚV. 4,3,13.") is None,
          "a non-Mahābhārata citation is not coerced into the index")
    check(idx.resolve_citation("MBH. ed. Bomb. 3,4,5") is None,
          "a Bombay-edition citation is out of scope, not silently mis-fitted")

    # ---- the live table, when this machine has it, must agree
    live = MbhLocusIndex()
    if live.loaded:
        lv = live.resolve(12, 8081)
        check(lv.vulgate == "12.226.6" and lv.bori == "12,219.6a",
              "live csl-atlas agrees on the specimen (%s / %s)" % (lv.vulgate, lv.bori))
    else:
        print("  skip  live csl-atlas presence table not on this machine (%s)"
              % MBH_PRESENCE_CSV)

    print("mbh_locus selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("citation", nargs="?", help='e.g. "MBH. 12,8081."')
    a = ap.parse_args(argv)
    if a.citation:
        print(resolve_citation(a.citation))
        return 0
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
