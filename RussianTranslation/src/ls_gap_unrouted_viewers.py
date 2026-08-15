#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ls_gap_unrouted_viewers.py — hosted scans the resolver never routes to (H2835).

`ls_gap_repair.py` measures which ⚑ gaps a *pattern* rule can rescue (answer: 60
of 5,257). Everything else was provisionally called "needs digitisation" — but
that conflates two very different statements:

  * the **resolver** has no pattern for the work  (a code gap — cheap)
  * **Cologne** hosts no scan of the work         (a digitisation gap — not cheap)

Only the second is genuinely out of reach. This module separates them by taking
the live inventory of scan viewers from the
[sanskrit-lexicon-scans](https://github.com/sanskrit-lexicon-scans) org and
subtracting the viewer apps the resolver's own pattern list can reach. What
remains is **hosted-but-unrouted**: a scan that exists, that no `<ls>` in any
dictionary can currently link to.

The inventory is passed in (or cached) rather than fetched here, so the module
stays offline and CI-safe:

    gh api users/sanskrit-lexicon-scans/repos --paginate --jq '.[].name' \\
        > reports/cologne_scan_repos.txt
    python src/ls_gap_unrouted_viewers.py

Matching viewer→source is deliberately conservative: a scan repo counts as
covering a gap only when its name matches the source's transliterated key or its
pwgbib expansion, and every proposed match is printed for a human to confirm.
A wrong match here would mint a link to the wrong book.
"""
import sys, os, io, re, csv, json, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("LS_RESOLVER_QUIET", "1")

import ls_resolver as lsr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("PWG_RU_DATA_ROOT", os.path.dirname(HERE))
REPORTS = os.path.join(DATA, "reports")
INVENTORY = os.path.join(REPORTS, "cologne_scan_repos.txt")
GAPS = os.path.join(REPORTS, "ls_gap_unrepairable_by_source.tsv")

#: repos that are dictionaries or infrastructure, not citable text viewers
NON_TEXT = {
    "documentation", "linktarget_howto", "Oxf_Cat_Aufrecht",
    # CDSL dictionaries (their own <ls> targets are dictionary entries, not loci)
    "ap90", "ben", "ben-v0", "bhs", "bop", "bor", "bur", "cae", "ccs", "fri",
    "gra", "gra-v0", "gst", "ieg", "inm", "krm", "lan", "lrv", "mci", "md",
    "mw", "mw-v0", "mw72", "mwe", "pe", "pgn", "pui", "pw", "pwg", "sch",
    "shs", "skd", "skd-v0", "snp", "stc", "vcp", "vei", "wil", "yat", "acc",
    "armh", "armh2", "acph", "acsj", "ae",
}

#: source key -> scan repo, proposed by hand from the pwgbib expansion.
#: Each entry is a CLAIM a human must confirm before any pattern is written.
PROPOSED = {
    "KĀTY": "katyasr", "TBR": "taittiriyabr", "TS": "taittiriyas",
    "YĀJÑ": "yajnavalkya", "MĀRK": "markandeyapurana", "KATHĀS": "kss",
    "RĀJA": "rajatar", "SĀH": "sahityadarpana", "KUMĀRAS": "kumaras",
    "MEGH": "meghasrnga", "BHAṬṬ": "bhattikavya", "RAGH": "raghuvamsa",
    "PAÑCAT": "pantankose", "VIKR": "vikramor", "MĀLAV": "malavikagni",
    "M": "manu", "HARIV": "hariv", "BHAG": "bhagavadgita",
}


def norm(s):
    return re.sub(r"[\s.'’]+", "", (s or "")).upper()


def routed_apps():
    """Viewer app slugs the resolver's pattern list can actually reach."""
    apps = set()
    for p in getattr(lsr, "PWG_PATTERNS", []):
        t = getattr(p, "url_template", "") or ""
        m = re.search(r"sanskrit-lexicon(?:-scans)?\.github\.io/([A-Za-z0-9_-]+)", t)
        if m:
            apps.add(m.group(1))
    # the special href_* generators hardcode their host outside the template
    for name in dir(lsr):
        if not name.startswith("href_"):
            continue
        try:
            src = __import__("inspect").getsource(getattr(lsr, name))
        except Exception:
            continue
        for m in re.finditer(r"sanskrit-lexicon(?:-scans)?\.github\.io/([A-Za-z0-9_-]+)", src):
            apps.add(m.group(1))
    return apps


def main():
    if not os.path.exists(INVENTORY):
        print("inventory missing: %s\n  gh api users/sanskrit-lexicon-scans/repos "
              "--paginate --jq '.[].name' > %s" % (INVENTORY, INVENTORY))
        return 1
    hosted = {l.strip() for l in io.open(INVENTORY, encoding="utf-8") if l.strip()}
    text_viewers = {h for h in hosted if h not in NON_TEXT}
    routed = routed_apps()
    unrouted = sorted(text_viewers - routed)

    print("scan repos hosted            : %d" % len(hosted))
    print("  of them citable text scans : %d" % len(text_viewers))
    print("  routed to by the resolver  : %d" % len(text_viewers & routed))
    print("  HOSTED BUT UNROUTED        : %d" % len(unrouted))
    print("    %s" % ", ".join(unrouted))

    gaps = {}
    if os.path.exists(GAPS):
        for r in csv.DictReader(io.open(GAPS, encoding="utf-8"), delimiter="\t"):
            gaps[norm(r["source"])] = int(r["occurrences"])

    print("\nproposed source -> hosted viewer matches (EVERY ROW NEEDS A HUMAN OK):")
    print("  %-14s %-18s %8s  %s" % ("source", "viewer", "⚑ occ", "status"))
    total = 0
    for src, repo in sorted(PROPOSED.items(), key=lambda kv: -gaps.get(norm(kv[0]), 0)):
        n = gaps.get(norm(src), 0)
        if repo not in hosted:
            status = "viewer NOT hosted — claim is wrong"
        elif repo in routed:
            status = "already routed (gap is elsewhere)"
        else:
            status = "UNROUTED — a pattern here would pay"
            total += n
        print("  %-14s %-18s %8d  %s" % (src, repo, n, status))
    print("\n⚑ occurrences reachable via an unrouted hosted viewer: %d" % total)
    print("(upper bound: each still needs its locus scheme checked against the scan)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
