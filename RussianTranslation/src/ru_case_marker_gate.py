#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ru_case_marker_gate.py — no German case abbreviations in Russian bodies (H3152 B1).

MG review point 2: *«идти дорогой (Akk, Instr) — не показывай мне немецкие
аббревиатуры в русском тексте»*.

State of the world, measured 19-08-2026 over all 11,603 store rows
------------------------------------------------------------------
The store is **already clean**: ``Akk``, ``Instr`` and ``Lok`` occur zero times
outside ``<ab>``, ``<ls>`` and Sanskrit spans. H2849 replaced them with the Latin
forms MG chose (``Acc.``, ``Ins.``, ``Loc.``) on 19-08-2026. What MG was looking
at is a **stale build**: ``pwg_ru/reglue/gA.md`` was generated before that
cleanup, so the card still showed the German forms while the store no longer did.
Point 2 therefore closes by rebuilding, not by cleaning again — and by this gate,
so that a future regeneration from an older store cannot quietly put them back.

What is and is not a case marker
--------------------------------
Only ``Akk``/``Instr``/``Lok`` (and their longer spellings) are **German-only**.
``Gen``, ``Dat``, ``Abl``, ``Nom``, ``Voc`` are spelled the same in Latin and are
the correct forms under decision 12 — flagging them would fail the store for
doing exactly what it was told to do. They are listed here as ``SHARED`` so the
distinction is written down rather than rediscovered.

The one known false positive, from H2849 and deliberately preserved: ``[Gen, unsp]``
is a **domain/register** marker in the MW-derived NWS material, not a case. It is
inside the shared set, so it cannot fire in the first place; the note stays because
a future widening of the pattern would resurrect the bug.

Run::

    python src/ru_case_marker_gate.py            # gate the whole store, exit 1 on a hit
    python src/ru_case_marker_gate.py --selftest
"""
import sys, os, io, json, re, argparse, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from store_path import canonical_store                          # noqa: E402

#: German-only case abbreviations — these fail the gate.
GERMAN_ONLY = ("Akk", "Akkus", "Instr", "Instrum", "Lok")

#: Spelled identically in Latin, and correct there (decision 12). Never flagged.
#: ``Gen`` in particular also occurs as the domain marker ``[Gen, unsp]``.
SHARED = ("Gen", "Dat", "Abl", "Nom", "Voc")

#: Regions that are not Russian prose and are excluded before matching:
#: the source's own abbreviation element, citations, and Sanskrit spans.
_SKIP = re.compile(r"<ab>.*?</ab>|<ls\b[^>]*>.*?</ls>|\{[#%].*?[#%]\}", re.S)

_HIT = re.compile(r"(?<![\wÀ-ɏ])(%s)(?![\wÀ-ɏ])" % "|".join(GERMAN_ONLY))


def scan_body(text):
    """``[(marker, context)]`` for every German-only case marker in Russian prose."""
    if not text:
        return []
    prose = _SKIP.sub(" ", text)
    return [(m.group(1), prose[max(0, m.start() - 40):m.end() + 20].replace("\n", " "))
            for m in _HIT.finditer(prose)]


def gate(store_path=None, field="ru"):
    """``(hits, rows_scanned)`` over the whole store. ``hits`` empty means pass."""
    hits, rows = [], 0
    with io.open(store_path or canonical_store(HERE), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            rows += 1
            for marker, ctx in scan_body(d.get(field)):
                hits.append((d.get("subcard"), d.get("layer"), marker, ctx))
    return hits, rows


def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    # ---- MG's own line, in its pre-H2849 form: must fail the gate
    bad = "идти дорогой (Akk, Instr)."
    found = [m for m, _ in scan_body(bad)]
    check(found == ["Akk", "Instr"], "MG's line fails the gate: %r" % found)
    check(scan_body("приходить к чему-л. (Lok или нар. места)"),
          "Lok fails the gate too")

    # ---- and its post-H2849 form: must pass
    check(scan_body("идти дорогой (Acc., Ins.).") == [],
          "the Latin forms MG chose pass cleanly")

    # ---- the shared spellings are correct Latin and must NOT fire
    for word in SHARED:
        check(scan_body("приходить кому-л. (%s.)" % word) == [],
              "%s. is Latin as well as German — never flagged" % word)
    check(scan_body("разбивать на куски. [Gen, unsp] ; MW : 1330") == [],
          "the [Gen, unsp] domain marker is not a case marker (H2849)")

    # ---- regions that are not Russian prose
    check(scan_body("<ab>Akk.</ab> дорогой") == [],
          "the source's own <ab> element is not Russian prose")
    check(scan_body("{#Akk#} дорогой") == [], "a Sanskrit span is skipped")
    check(scan_body('<ls n="Akk. 1,2">Akk. 1,2</ls>') == [],
          "a citation is skipped")

    # ---- no substring false positives
    check(scan_body("Akkusativ") == [], "a longer word is not a bare marker")
    check(scan_body("Instrumental") == [], "Instrumental is not Instr")

    # ---- the live store, which is the actual acceptance
    try:
        hits, rows = gate()
    except (IOError, OSError) as exc:
        print("  skip  store not on this machine (%s)" % exc)
        hits, rows = [], 0
    if rows:
        check(not hits,
              "the live store carries no German case marker (%d rows, %d hits)"
              % (rows, len(hits)))
        for h in hits[:5]:
            print("        %s [%s] %s — %s" % h)

    print("ru_case_marker_gate selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--field", default="ru")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    hits, rows = gate(field=a.field)
    print("scanned %d rows, field %r" % (rows, a.field))
    if not hits:
        print("PASS — no German case abbreviation in Russian prose")
        return 0
    by_marker = collections.Counter(h[2] for h in hits)
    print("FAIL — %d hits: %s" % (len(hits), dict(by_marker)))
    for sub, layer, marker, ctx in hits[:40]:
        print("  %-28s [%-5s] %-6s … %s" % (sub, layer, marker, ctx))
    return 1


if __name__ == "__main__":
    sys.exit(main())
