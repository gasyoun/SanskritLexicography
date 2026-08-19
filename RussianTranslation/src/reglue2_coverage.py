#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""reglue2_coverage.py — the before/after citation-coverage meter for H3152.

Why this exists and why it is not
[`ls_coverage_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_coverage_probe.py)
------------------------------------------------------------------------------
``ls_coverage_probe`` answers a *different* question — **which of two resolvers**
(the ported ``ls_resolver`` vs Cologne's precomputed csl-lslink table) covers the
store better. It reports one global number over the ``de`` field only.

The H3152 stop condition needs something the probe cannot give: coverage **broken
down by cited work** (``MBH.`` / ``ṚV.`` / ``AV.``) and **by store layer**
(``pwg`` / ``nws``), taken once before the change and once after, over the whole
store rather than the 15-root pilot (PLAN decision 3). A single global percentage
would hide exactly the regression the stop condition exists to catch: NWS
Ṛgveda coverage can collapse while the PWG-layer majority holds the average up.

It additionally counts the two gaps H3152 closes, so "after" can be compared with
"before" on the same axes:

``extra_loci``
    Loci that are *inside* an ``<ls>`` element but after the first one —
    ``<ls>ṚV. 4,3,13. 10,18,4</ls>`` is one element holding two addresses, and
    only the first was ever resolvable. Every extra locus is a citation the
    reader can see and cannot click (MG review point 6a).

``bare``
    Ṛgveda/Atharvaveda addresses standing in the running text with **no**
    ``<ls>`` wrapper at all, because csl-orig has none — ``AV(P) 9.10,10`` in the
    NWS layer (MG review point 5). Counted with the same narrow whitelist the
    wrapper uses, so the two numbers are commensurable.

Every number is a count of *occurrences*, not of rows: one body may carry twenty
citations and each is a separate chance to link or fail to link.

Run::

    python src/reglue2_coverage.py                 # human table
    python src/reglue2_coverage.py --json out.json # machine baseline
    python src/reglue2_coverage.py --selftest
"""
import sys, os, io, json, re, argparse, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("LS_RESOLVER_QUIET", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from ls_links import LsLinks, HIT, LS_RE                       # noqa: E402
from ls_split import split_ls_loci, resolve_loci               # noqa: E402
from nws_citation_wrap import find_bare_citations, wrap_bare_citations  # noqa: E402
from store_path import canonical_store                         # noqa: E402

#: Which cited work an ``<ls>`` belongs to, for the per-work breakdown. Order
#: matters: ``AV(P)``/``AVP`` must be tried before a bare ``AV``.
WORK_PATTERNS = [
    ("MBH.", re.compile(r"^\s*MBH\b", re.I)),
    ("ṚV.", re.compile(r"^\s*(ṚV|RV)\b", re.I)),
    ("AV.", re.compile(r"^\s*AV\b", re.I)),
]


def work_of(n_attr, visible):
    """The work bucket for one citation, or ``other``.

    The ``n=`` attribute wins when present: it carries the *normalized* prefix a
    continuation citation inherits (``<ls n="ṚV.">5,15,4.</ls>`` is a Ṛgveda
    citation even though its visible text names no work)."""
    for probe in (n_attr, visible):
        if not probe:
            continue
        for name, rx in WORK_PATTERNS:
            if rx.match(probe):
                return name
    return "other"


def measure_body(ll, text, bucket):
    """Tally one store body into ``bucket`` (a Counter keyed ``work:metric``).

    Both sides of the stop condition are counted in the same pass over the same
    text, which is the only way "before" and "after" can be compared without
    arguing about whether the two runs saw the same store:

    ``total`` / ``hit``
        addresses present, and addresses the **old** one-address-per-element path
        turned into a link.
    ``linked_after``
        addresses the **new** path links: every address of a fully-resolvable
        multi-address element, plus the bare addresses the NWS wrapper accepts.

    ``linked_after`` can never be below ``hit``: the split is all-or-nothing and
    falls back to the old single resolution, and the wrapper only adds elements.
    That is not an assumption — :func:`selftest` pins it, and the whole-store run
    reports both columns so a regression would be visible rather than argued.
    """
    text = text or ""
    # A5 first: an address the wrapper accepts becomes a real element, so it is
    # counted the same way every other citation is rather than as a special case.
    wrapped_text, n_wrapped = wrap_bare_citations(text)
    for _start, _end, _raw, work, _canon in find_bare_citations(text):
        bucket[work + ":bare"] += 1
    for tag in LS_RE.findall(wrapped_text):
        n_attr, visible = ll.parts(tag)
        work = work_of(n_attr, visible)
        loci = split_ls_loci(n_attr, visible)
        resolved = resolve_loci("pwg", n_attr, visible)
        status, _href = ll.resolve(tag)
        # The denominator is ADDRESSES, not elements. Counting elements would let
        # "after" exceed 100 %, since one element can hold several addresses — and
        # would understate the gap, which is the whole thing being measured.
        bucket[work + ":total"] += len(loci)
        bucket[work + ":elements"] += 1
        is_new = n_wrapped and tag not in text
        if not is_new:
            if status == HIT:
                bucket[work + ":hit"] += 1
            if len(loci) > 1:
                bucket[work + ":extra_loci"] += len(loci) - 1
        if resolved:
            bucket[work + ":linked_after"] += len(resolved)
        elif status == HIT:
            bucket[work + ":linked_after"] += 1


def measure(store_path=None, limit=None):
    """Return ``{layer: {work: {metric: count}}}`` over the whole store."""
    ll = LsLinks()
    per_layer = collections.defaultdict(collections.Counter)
    rows = 0
    with io.open(store_path or canonical_store(HERE), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            rows += 1
            if limit and rows > limit:
                break
            layer = d.get("layer") or "?"
            measure_body(ll, d.get("ru"), per_layer[layer])
    out = {}
    for layer, counter in per_layer.items():
        works = collections.defaultdict(dict)
        for key, n in counter.items():
            work, metric = key.rsplit(":", 1)
            works[work][metric] = n
        out[layer] = dict(works)
    return {"rows": rows, "layers": out}


def render(result):
    """The human table. Coverage is hits / total for that (layer, work) cell."""
    lines = ["store rows: %d" % result["rows"], ""]
    lines.append("%-6s %-6s %8s %8s %8s %8s %8s %9s %6s"
                 % ("layer", "work", "addrs", "before", "after", "cov_b",
                    "cov_a", "extra_loci", "bare"))
    lines.append("-" * 82)
    tb = ta = tt = 0
    for layer in sorted(result["layers"]):
        works = result["layers"][layer]
        for work in ("MBH.", "ṚV.", "AV.", "other"):
            w = works.get(work)
            if not w:
                continue
            tot = w.get("total", 0)
            hit, aft = w.get("hit", 0), w.get("linked_after", 0)
            tt += tot; tb += hit; ta += aft
            lines.append("%-6s %-6s %8d %8d %8d %7.1f%% %7.1f%% %9d %6d"
                         % (layer, work, tot, hit, aft,
                            100.0 * hit / max(tot, 1), 100.0 * aft / max(tot, 1),
                            w.get("extra_loci", 0), w.get("bare", 0)))
    lines.append("-" * 82)
    lines.append("%-13s %8d %8d %8d %7.1f%% %7.1f%%"
                 % ("TOTAL", tt, tb, ta,
                    100.0 * tb / max(tt, 1), 100.0 * ta / max(tt, 1)))
    lines.append("")
    lines.append("before = links the one-address-per-element path produced")
    lines.append("after  = links the split + NWS-wrap path produces "
                 "(never fewer — stop condition 2)")
    return "\n".join(lines)


def selftest():
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    check(work_of(None, "MBH. 12,8081.") == "MBH.", "visible text names the work")
    check(work_of("ṚV.", "5,15,4.") == "ṚV.",
          'n="ṚV." continuation is bucketed as Ṛgveda, not "other"')
    check(work_of(None, "AV(P) 9.10,10") == "AV.", "AV(P) buckets as Atharvaveda")
    check(work_of(None, "GORR.") == "other", "unlisted work -> other")

    ll = LsLinks()
    b = collections.Counter()
    measure_body(ll, "идти <ls>MBH. 12,8081.</ls> и <ls>ṚV. 4,3,13. 10,18,4</ls>", b)
    check(b["MBH.:total"] == 1 and b["MBH.:hit"] == 1, "MBh citation counted and linked")
    check(b["ṚV.:extra_loci"] == 1,
          "the second locus of a two-address <ls> is counted as an extra locus (%d)"
          % b["ṚV.:extra_loci"])
    check(b["ṚV.:hit"] == 1 and b["ṚV.:linked_after"] == 2,
          "the same element yields 1 link before and 2 after (%d -> %d)"
          % (b["ṚV.:hit"], b["ṚV.:linked_after"]))

    # the stop-condition invariant, stated as a test rather than as a hope
    b4 = collections.Counter()
    measure_body(ll, "<ls>NOTADICT. 1,1. 2,2</ls> <ls>GORR.</ls> "
                     "<ls>AIT. BR. 6,33.</ls>", b4)
    check(b4["other:linked_after"] >= b4["other:hit"],
          "an unresolvable run never lowers the after count (%d >= %d)"
          % (b4["other:linked_after"], b4["other:hit"]))

    b2 = collections.Counter()
    measure_body(ll, "идти. AV 5,28,9", b2)
    check(b2["AV.:bare"] == 1, "an unwrapped Atharvaveda address is counted as bare")

    # The bare count must agree with what the wrapper will actually wrap,
    # otherwise "before" and "after" are measuring different populations. The
    # Paippalāda recension is refused there (a different text), so it must not
    # be promised here either.
    b3 = collections.Counter()
    measure_body(ll, "идти. AV(P) 9.10,10", b3)
    check(b3["AV.:bare"] == 0,
          "AV(P) is not counted as a linkable gap — the wrapper refuses it too")

    print("reglue2_coverage selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", help="write the raw counts here")
    ap.add_argument("--store", help="store path (default: canonical_store)")
    ap.add_argument("--limit", type=int, help="stop after N rows (smoke runs)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    result = measure(a.store, a.limit)
    print(render(result))
    if a.json:
        with io.open(a.json, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=1)
        print("\nwrote %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
