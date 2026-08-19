#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ls_split_changefile.py — send the multi-address <ls> fix upstream (H3152 A4/step 9).

Splitting a citation run at render time fixes *our* surfaces. The markup itself
is still one element holding several addresses in Cologne's own source, so every
other consumer of ``pwg.txt`` keeps the defect. This emits the change-file that
carries the fix upstream, in the ``line old`` / ``line new`` format
[csl-corrections](https://github.com/sanskrit-lexicon/csl-corrections) uses.

**Nothing here writes to csl-orig.** Agents never commit or push there; corrections
are parked in the local queue and promoted by one consolidated PR at most monthly
([/cologne-correction-queue](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-correction-queue.md)
→ [/cologne-batch-pr](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-batch-pr.md)).
This is stop condition 3 of the plan, and it is why the output is a file rather
than a pull request.

The rewrite
-----------
``<ls>ṚV. 4,3,13. 10,18,4</ls>`` becomes
``<ls>ṚV. 4,3,13.</ls> <ls n="ṚV.">10,18,4</ls>`` — the continuation form Cologne
**already uses** elsewhere in the same file (``<ls n="ṚV.">5,15,4.</ls>``), so this
proposes no new convention, only a consistent application of the existing one.
That is what makes it a ``link-splitting`` correction rather than a redesign.

Only fully-resolvable runs are proposed. A run where one address does not resolve
is left alone: the whole point of the all-or-nothing rule is that a partial split
asserts "there is no further place", which is the defect wearing different clothes.

Reads only the NWS-free PWG source. The Halle Nachtragswörterbuch layer is **not**
in csl-orig — it is scraped from
[nws.uzi.uni-halle.de](https://nws.uzi.uni-halle.de) — so the unwrapped Ṛgveda and
Atharvaveda addresses of review point 5 produce **no** csl-orig change-file, only
our own render-time wrapper. The plan assumed otherwise; see the report.

Which dictionary — measured, not assumed
----------------------------------------
The plan expected this correction in ``pwg``. It is not there. Run over both
Petersburg dictionaries on 19-08-2026:

========  ==============  ====================================================
dict      splittable runs  what the rest of the multi-address elements are
========  ==============  ====================================================
``pwg``   **0**            page references (``11087 (p. 572)``), note markers
                           (``83, N. 6``), Oxford column letters (``100,a.``)
                           — 2,838 lines that must NOT be split. PWG's genuine
                           runs already use the ``n=`` continuation form.
``pw``    **141**          real address runs: ``ṚV. 1,146,4. 5,69,1``,
                           ``HARIV. 3248. 3317``, ``BHAṬṬ. 11,11. 2,31``
========  ==============  ====================================================

Aiming this at ``pwg`` on the plan's say-so would have queued 2,838 lines of
damage, every one of which resolves to a real but wrong page. That is why
:func:`ls_split.splittable` refuses on impure addresses rather than trusting the
resolver's willingness to place them.

Run::

    python src/ls_split_changefile.py --count
    python src/ls_split_changefile.py --dict pwg --count
    python src/ls_split_changefile.py --out <queue-dir> [--limit N]
"""
import sys, os, io, re, argparse, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("LS_RESOLVER_QUIET", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ls_split import split_ls_loci, resolve_loci                # noqa: E402

ORG = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSL_ORIG = os.environ.get("CSL_ORIG_DIR", os.path.join(ORG, "csl-orig"))

#: Where the population actually is. Measured 19-08-2026 across both Petersburg
#: dictionaries: **pwg** yields 0 splittable runs — its genuine multi-address
#: citations already use the ``n=`` continuation form, and every remaining
#: multi-address element is a page reference, a note marker or an Oxford column
#: letter that must NOT be split. **pw** yields 141 lines. So the correction
#: belongs to `pw`, and a change file aimed at `pwg` would have been 2,838 lines
#: of damage.
DEFAULT_DICT = "pw"


def source_path(dict_code):
    return os.path.join(CSL_ORIG, "v02", dict_code, "%s.txt" % dict_code)

_LS = re.compile(r"<ls\b([^>]*)>(.*?)</ls>", re.S)
_N_ATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')
_L_NUM = re.compile(r"^<L>(\d+)")


def rewrite_line(line):
    """``(new_line, [(old_element, new_elements)])`` — or ``(None, [])`` if untouched."""
    changes = []

    def one(m):
        attrs, visible = m.group(1), m.group(2)
        n_attr = _N_ATTR.search(attrs or "")
        n_attr = n_attr.group(1) if n_attr else None
        loci = split_ls_loci(n_attr, visible)
        if len(loci) < 2 or not resolve_loci("pwg", n_attr, visible):
            return m.group(0)
        # Address 1 keeps the element's attributes untouched and only loses the
        # trailing addresses from its text, so a reviewer can see at a glance that
        # the first link cannot have moved — the change is additive.
        head = "<ls%s>%s</ls>" % (attrs, loci[0])
        # the shared source prefix, for the continuation elements' n= attribute
        pfx = re.match(r"^\D*", loci[0]).group(0).strip()
        tail = ['<ls n="%s">%s</ls>'
                % (n_attr or pfx, text[len(re.match(r"^\D*", text).group(0)):])
                for text in loci[1:]]
        new = " ".join([head] + tail)
        changes.append((m.group(0), new))
        return new

    out = _LS.sub(one, line)
    return (out, changes) if changes else (None, [])


def scan(path, limit=None):
    """``[(lineno, L, old_line, new_line, changes)]`` over the whole dictionary."""
    hits = []
    lnum = 0
    cur_L = None
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            lnum += 1
            m = _L_NUM.match(line)
            if m:
                cur_L = m.group(1)
            if "<ls" not in line:
                continue
            new, changes = rewrite_line(line.rstrip("\n"))
            if new:
                hits.append((lnum, cur_L, line.rstrip("\n"), new, changes))
                if limit and len(hits) >= limit:
                    break
    return hits


def write_changefile(hits, out_dir, dict_code=DEFAULT_DICT, handoff="H3152"):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "change_%s_h3152_link_splitting.txt" % dict_code)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("; %s / link-splitting: one <ls> holding several addresses is "
                 "split into one element per address,\n" % handoff)
        fh.write("; using the continuation form %s.txt already uses elsewhere "
                 '(<ls n="Chr. 240,">28</ls>). Only runs where EVERY address\n'
                 % dict_code)
        fh.write("; resolves are proposed — a partial split would assert that the "
                 "remaining places do not exist.\n")
        fh.write("; Generated by RussianTranslation/src/ls_split_changefile.py; "
                 "%d lines affected.\n" % len(hits))
        for lnum, cur_L, old, new, _ch in hits:
            fh.write("; L=%s\n" % cur_L)
            fh.write("%d old %s\n" % (lnum, old))
            fh.write("%d new %s\n" % (lnum, new))
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dict", default=DEFAULT_DICT,
                    help="csl-orig dictionary code (default: %s)" % DEFAULT_DICT)
    ap.add_argument("--out", help="queue directory to write the change file into")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--sample", type=int, default=6)
    a = ap.parse_args(argv)

    path = source_path(a.dict)
    if not os.path.exists(path):
        print("csl-orig not on this machine: %s" % path)
        return 2
    print("dictionary          : %s (%s)" % (a.dict, path))
    hits = scan(path, limit=a.limit)
    n_elem = sum(len(h[4]) for h in hits)
    n_addr = sum(len(c[1].split("<ls")) - 2 for h in hits for c in h[4])
    print("lines affected      : %d" % len(hits))
    print("<ls> elements split : %d" % n_elem)
    print("addresses gained    : %d" % n_addr)
    works = collections.Counter()
    for h in hits:
        for old, _new in h[4]:
            body = _LS.match(old)
            works[re.match(r"^\D*", (body.group(2) if body else "")).group(0).strip()
                  or "(n= prefix)"] += 1
    print("\nby source prefix (top 12):")
    for k, v in works.most_common(12):
        print("  %-22s %5d" % (k, v))
    print("\nsample:")
    for lnum, cur_L, old, new, ch in hits[:a.sample]:
        print("  line %d (L=%s)" % (lnum, cur_L))
        for o, n in ch[:1]:
            print("    old  %s" % o[:110])
            print("    new  %s" % n[:130])
    if a.out:
        p = write_changefile(hits, a.out, a.dict)
        print("\nwrote %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
