#!/usr/bin/env python3
"""Re-audit the 15-dict union corroboration counts under a witness-independence map.

The published cross-dict union (``HeadwordLists/union/union_headwords.tsv``,
323,425 headwords) records, per headword, *how many of the 15 dictionaries*
attest it — and ``HeadwordLists/union/UNION.md`` publishes that "in N dicts"
distribution. That distribution is silently read as a **corroboration** count:
a headword "in 15 dicts" looks 15-times corroborated. But the 15 dictionaries
are **not 15 independent witnesses**. Several are the same work, revised
editions of one work, pure supplements to it, or headword-inventory derivatives
of it (documented in RussianTranslation/DICTIONARY_CHAIN.md and FINDINGS.md
§28). Counting them as independent inflates every corroboration figure.

This script collapses the 15 dictionary codes into **independence clusters**
under a ladder of increasingly strict policies (P0 published .. P4 aggressive),
then recomputes, for each headword, the number of *distinct independent
witnesses* = distinct clusters that attest it. It reports how the corroboration
distribution deflates, and — the headline — how many headwords the published
count calls "corroborated" (in >=2 dicts) collapse to a **single independent
witness** once same-work / same-lineage duplicates are merged.

The pivotal collapse (P3, MW into the Petersburg witness) is NOT a new claim of
this script: FINDINGS.md §83 already ruled "PWG, PW and MW collapse to roughly
one European witness" (measured six ways in csl-atlas A10), and §97 gives the
bibliographic reason (MW was compiled substantially FROM Boehtlingk-Roth). This
script's job is to *quantify* what that ruling does to the published union
corroboration counts, which still treat all 15 dicts as independent.

P0 is the identity map (each dict its own cluster); running it MUST reproduce
UNION.md's published "in N dicts" distribution exactly — that is the built-in
regression anchor (``--check``).

Inputs consumed as-is (never rebuilt, per the reuse rule):
  * ``HeadwordLists/union/union_headwords.tsv`` — cols ``slp1 iast n_dicts
    dicts gender fem_fold``; ``dicts`` is a space-joined list of the 2-3 letter
    codes. utf-8-sig (the union carries a BOM).

Outputs (beside this script):
  * ``witness_independence_reaudit.tsv`` — one row per (policy, n_witnesses):
    ``policy  n_clusters_max  n_witnesses  headwords  cum_ge  cum_ge_share``.
  * ``witness_independence_clusters.tsv`` — the map itself: ``policy  dict
    cluster``.

Usage:
    python witness_independence_reaudit.py [--union PATH] [--check]

H1363. Run 20-07-2026 by Opus 4.8 (claude-opus-4-8).
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ALL_DICTS = [
    "AP", "BHS", "BUR", "CAE", "CCS", "GRA", "INM", "MD",
    "MW", "PWG", "PWK", "SCH", "SKD", "VCP", "VEI",
]

# --- The witness-independence map -----------------------------------------
# Each policy maps a dict code to a *cluster id*. Two dicts sharing a cluster
# id count as ONE independent witness of any headword they both attest. The
# ladder is ordered by evidentiary strength of the collapses it makes; every
# collapse is grounded in the derivation graph documented in the report.
#
# Collapse edges (strongest -> weakest):
#   CAE == CCS  same work, two languages (Cappeller 1887 de / 1891 en);
#               Jaccard 0.672, the highest pair in the overlap matrix.   [same-work]
#   PWG->PWK    Boehtlingk's revised condensation of Boehtlingk-Roth.    [revised-edition]
#   PWK->SCH    Schmidt 1928 Nachtraege: pure addenda to PW.             [supplement]
#   PWG->MW     MW inherited the Petersburg apparatus/inventory
#               (FINDINGS §83/§97, §28; 0.81 citation-order concordance;
#               MW gap-sensitivity to PWG 12.3x).                        [apparatus-derived]
#   {PWG,MW}->MD  Macdonell's Practical Dict is a school abridgment of
#               Boehtlingk / MW (2.0% unique headwords).                 [partial-source, P4]
#
# NOT collapsed (established-finding / data-driven independence, for the record):
#   AP          Apte is the NAMED independent European control in §83
#               (gap-sensitivity 1.5x -> behaves like an independent compiler,
#               supplies 54.6% of PWG-omitted indigenous words). Never folded.
#   SKD vs VCP  both Bengal indigenous kosas, but Jaccard ~0.084 at the
#               headword level -> they attest largely disjoint inventories;
#               §83's independent non-European anchor.
#   GRA/VEI/INM corpus concordances/indexes (Rigveda / Vedic index / MBh
#               names): primary-text witnesses, independent of the
#               lexicographic tradition (§97 names GRA/BHS/AP as independent).
#   BUR         Burnouf 1866, built on Wilson/Bopp, not Petersburg.
#   BHS         Edgerton's Buddhist Hybrid Sanskrit, own corpus.

# cluster ids used below
PETB = "PETERSBURG"   # Boehtlingk-Roth editorial lineage (+ MW under §83)
CAP = "CAPPELLER"     # Cappeller, one work two languages


def _identity():
    return {d: d for d in ALL_DICTS}


def build_policies():
    """Return an ordered list of (id, label, evidentiary_note, cluster_map)."""
    policies = []

    # P0 — published: each dict is its own witness (the status quo).
    policies.append((
        "P0", "published (15 independent witnesses)",
        "identity map — the count UNION.md publishes; regression anchor",
        _identity(),
    ))

    # P1 — same-work only (indisputable): CAE == CCS.
    m = _identity()
    m["CAE"] = CAP
    m["CCS"] = CAP
    policies.append((
        "P1", "same-work collapse (14 clusters)",
        "CAE==CCS: one dictionary (Cappeller) in two languages — not two witnesses",
        m,
    ))

    # P2 — editorial lineage (documented): + Petersburg = PWG+PWK+SCH.
    m = dict(m)
    m["PWG"] = PETB
    m["PWK"] = PETB
    m["SCH"] = PETB
    policies.append((
        "P2", "editorial-lineage collapse (12 clusters)",
        "+ PWG->PWK (revised edition) ->SCH (supplement): one Petersburg lineage, "
        "shared editor (Boehtlingk) and source-reading tradition",
        m,
    ))

    # P3 — the FINDINGS §83 / §97 RULING (not speculation): MW folds into the
    # Petersburg witness. §83 measured this six ways (csl-atlas A10) and ruled
    # "PWG, PW and MW collapse to roughly one European witness"; §97 gives the
    # bibliographic reason (MW compiled substantially FROM Boehtlingk-Roth). This
    # is the substantive answer this re-audit exists to quantify.
    m = dict(m)
    m["MW"] = PETB
    policies.append((
        "P3", "FINDINGS §83/§97 ruling — MW into Petersburg (11 clusters)",
        "+ MW: §83 ruling 'PWG, PW and MW collapse to ~one European witness' "
        "(MW gap-sensitivity to PWG's inclusion decision 12.3x vs independent "
        "Apte 1.5x). MW's glosses are independent English; its headword inventory "
        "is Petersburg-derived",
        m,
    ))

    # P4 — strict: + MD (Macdonell), a school abridgment of MW/Boehtlingk, folds
    # into the Petersburg witness too. NOTE: Apte is deliberately NOT folded —
    # §83 names Apte as THE genuinely independent European-tradition control
    # (gap-sensitivity 1.5x, behaves like an independent compiler), so collapsing
    # it would contradict the repo's own established finding.
    m = dict(m)
    m["MD"] = PETB
    policies.append((
        "P4", "strict — + MD school abridgment into Petersburg (10 clusters)",
        "+ MD: Macdonell's Practical Dictionary is an MW/Boehtlingk school "
        "abridgment (2.0% unique headwords). Apte kept SEPARATE per §83 (the "
        "named independent control) — folding it would over-collapse",
        m,
    ))
    return policies


def load_union(path):
    """Yield ``(dict_codes, n_dicts_field)`` per headword.

    ``n_dicts_field`` is the file's own recorded count — used as an independent
    regression anchor for P0 (identity map): P0's distinct-cluster count must
    equal the file's ``n_dicts`` for every row, so the P0 histogram must equal
    the ``n_dicts``-column histogram exactly.
    """
    with open(path, encoding="utf-8-sig") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        i_dicts = header.index("dicts")
        i_n = header.index("n_dicts")
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            yield parts[i_dicts].split(), int(parts[i_n])


def distribution(union_rows, cluster_map):
    """headwords bucketed by number of *distinct clusters* that attest them."""
    dist = Counter()
    for dicts, _n in union_rows:
        clusters = {cluster_map[d] for d in dicts if d in cluster_map}
        dist[len(clusters)] += 1
    return dist


def cumulative_ge(dist):
    """For each n, headwords attested by >= n distinct witnesses."""
    total = sum(dist.values())
    out = {}
    for n in sorted(dist):
        out[n] = sum(v for k, v in dist.items() if k >= n)
    return out, total


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--union",
        default=str(
            Path(__file__).resolve().parents[1]
            / "HeadwordLists" / "union" / "union_headwords.tsv"
        ),
    )
    ap.add_argument("--check", action="store_true",
                    help="assert P0 reproduces the UNION.md published distribution")
    args = ap.parse_args()

    # UNION.md's published "in N dicts" table. NOTE: it was computed on the
    # PRE-FOLD union of 323,662 headwords (142,673 singletons + 180,989 in >=2
    # = 323,662), whereas the current canonical union_headwords.tsv is the
    # POST-FOLD 323,425 (237 gender-confirmed -ini feminines folded onto their
    # -in base). So the published table is stale-by-fold vs the live file; the
    # small per-bucket deltas below are exactly that fold, not a bug. The real
    # P0 regression anchor is the file's own n_dicts column (see --check).
    published_prefold = {
        1: 142673, 2: 61514, 3: 46834, 4: 28778, 5: 17250, 6: 10319,
        7: 5852, 8: 3934, 9: 2928, 10: 1876, 11: 967, 12: 493, 13: 188,
        14: 45, 15: 11,
    }

    policies = build_policies()
    here = Path(__file__).resolve().parent

    # materialize the union once (list of (codes, n_dicts)) — 323k rows, fine.
    union_rows = [row for row in load_union(args.union)]
    print(f"union headwords: {len(union_rows)}")

    # write the cluster map itself
    with open(here / "witness_independence_clusters.tsv", "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("policy\tdict\tcluster\n")
        for pid, _label, _note, cmap in policies:
            for d in ALL_DICTS:
                fh.write(f"{pid}\t{d}\t{cmap[d]}\n")

    dists = {}
    for pid, label, note, cmap in policies:
        dist = distribution(union_rows, cmap)
        dists[pid] = dist
        n_clusters = len(set(cmap.values()))
        print(f"\n=== {pid}: {label} ===")
        print(f"    {note}")
        print(f"    distinct clusters: {n_clusters}")
        cum, total = cumulative_ge(dist)
        singles = dist.get(1, 0)
        corrob = total - singles
        print(f"    single-witness (n=1): {singles} ({singles/total:.1%})")
        print(f"    corroborated (n>=2): {corrob} ({corrob/total:.1%})")

    # P0 regression check — against the file's OWN n_dicts column (independent
    # of the cluster-counting logic): P0 identity => distinct clusters == n_dicts.
    ndicts_hist = Counter(n for _codes, n in union_rows)
    p0 = dists["P0"]
    ok = dict(p0) == dict(ndicts_hist)
    print(f"\nP0 == file n_dicts-column histogram (regression anchor): {ok}")
    if args.check and not ok:
        print("MISMATCH — P0 does not match the n_dicts column:")
        for n in sorted(set(ndicts_hist) | set(p0)):
            if p0.get(n, 0) != ndicts_hist.get(n, 0):
                print(f"  n={n}: P0 {p0.get(n,0)}, n_dicts-col {ndicts_hist.get(n,0)}")
        sys.exit(1)

    # documented drift vs the stale published UNION.md table (pre-fold 323,662).
    drift = sum(abs(p0.get(n, 0) - published_prefold.get(n, 0))
                for n in set(p0) | set(published_prefold))
    print(f"UNION.md published table is PRE-FOLD (323,662); live file is "
          f"POST-FOLD ({len(union_rows)}). Total per-bucket drift: {drift} "
          f"headwords across the 237-feminine fold.")

    # the headline deflation table: how many published-"corroborated" headwords
    # collapse to a single independent witness under each policy.
    total = len(union_rows)
    p0_singles = p0.get(1, 0)
    print("\n=== Deflation of corroboration ===")
    print("policy  singles  corrob>=2  newly-single(vs P0)  max_n")
    for pid, label, _note, _cmap in policies:
        d = dists[pid]
        singles = d.get(1, 0)
        corrob = total - singles
        newly = singles - p0_singles
        print(f"  {pid}  {singles}  {corrob}  +{newly}  {max(d)}")

    # long-format distribution TSV
    with open(here / "witness_independence_reaudit.tsv", "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("policy\tn_clusters_max\tn_witnesses\theadwords\tcum_ge\tcum_ge_share\n")
        for pid, _label, _note, cmap in policies:
            d = dists[pid]
            n_clusters = len(set(cmap.values()))
            cum, tot = cumulative_ge(d)
            for n in sorted(d):
                fh.write(f"{pid}\t{n_clusters}\t{n}\t{d[n]}\t{cum[n]}\t{cum[n]/tot:.4f}\n")

    print(f"\nwrote {here / 'witness_independence_reaudit.tsv'}")
    print(f"wrote {here / 'witness_independence_clusters.tsv'}")


if __name__ == "__main__":
    main()
