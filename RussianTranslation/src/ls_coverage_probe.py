#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ls_coverage_probe.py — which <ls> resolver covers the pwg_ru store better? (H2827)

Two candidates already exist in the org and neither had ever been measured
against the translated store:

* [`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
  — the in-repo Python port of Cologne's own csl-app Dart pattern engine
  (algorithmic: parse the locus, build the scan URL).
* [csl-lslink](https://github.com/sanskrit-lexicon/csl-lslink) ``zip/pwg_lslinks.sqlite.zip``
  — Cologne's precomputed table, 277k literal ``<ls>`` string → href rows,
  generated from pwg.xml itself.

Run: python src/ls_coverage_probe.py   (set PWG_RU_DATA_ROOT for the store)
"""
import sys, os, io, json, re, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("LS_RESOLVER_QUIET", "1")

import ls_resolver as lsr
from ls_links import LsLinks, HIT, LS_RE, LS_PARTS, _ws

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("PWG_RU_DATA_ROOT", os.path.dirname(HERE))
STORE = os.path.join(DATA, "src", "pwg_ru_translated.jsonl")
N_ATTR = re.compile(r'n="([^"]*)"')


def resolver_href(tag):
    m = LS_PARTS.match(_ws(tag))
    if not m:
        return None
    attrs, visible = m.group(1), m.group(2).strip()
    na = N_ATTR.search(attrs)
    try:
        return lsr.generate_href("pwg", na.group(1) if na else None, visible) or None
    except Exception:
        return None


def main():
    ll = LsLinks()
    tot = 0
    both = only_res = only_tab = neither = 0
    disagree = collections.Counter()
    ex_only_tab, ex_only_res, ex_disagree = [], [], []

    for line in io.open(STORE, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        for tag in LS_RE.findall(d.get("de") or ""):
            tot += 1
            r = resolver_href(tag)
            st, t = ll.resolve(tag)
            t = t if st == HIT else None
            if r and t:
                both += 1
                if r.rstrip("/") != t.rstrip("/"):
                    disagree[(r.split("?")[0], t.split("?")[0])] += 1
                    if len(ex_disagree) < 8:
                        ex_disagree.append((tag, r, t))
            elif r:
                only_res += 1
                if len(ex_only_res) < 8:
                    ex_only_res.append((tag, r))
            elif t:
                only_tab += 1
                if len(ex_only_tab) < 8:
                    ex_only_tab.append((tag, t))
            else:
                neither += 1

    pc = lambda n: "%6d  %5.1f%%" % (n, 100.0 * n / max(tot, 1))
    print("<ls> occurrences in store : %d\n" % tot)
    print("  both resolve            : %s" % pc(both))
    print("  ls_resolver only        : %s" % pc(only_res))
    print("  csl-lslink table only   : %s" % pc(only_tab))
    print("  neither                 : %s" % pc(neither))
    print("\n  ls_resolver total       : %s" % pc(both + only_res))
    print("  csl-lslink total        : %s" % pc(both + only_tab))
    print("  union                   : %s" % pc(both + only_res + only_tab))
    print("\n  disagreeing hrefs (both resolved, different target): %d"
          % sum(disagree.values()))
    for (a, b), n in disagree.most_common(10):
        print("    %5d  resolver=%s   table=%s" % (n, a, b))
    for label, ex in (("table-only", ex_only_tab), ("resolver-only", ex_only_res)):
        print("\n  %s examples:" % label)
        for t in ex:
            print("    %s -> %s" % (t[0][:60], t[1][:80]))
    if ex_disagree:
        print("\n  disagreement examples:")
        for tag, r, t in ex_disagree:
            print("    %s\n      resolver=%s\n      table   =%s" % (tag[:60], r, t))
    return 0


if __name__ == "__main__":
    sys.exit(main())
