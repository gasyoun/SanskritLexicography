"""Count the grammatical-annex parallel — AK kanda 3 vs semdom top-level 9.

A58 paper section 6 evidence table (H774), quantifying the finding stated in
prose in data/SEMDOM_AK_CROSSWALK_2026.md: both the Amarakosha and SIL's
semantic domains bolt a formal, non-semantic annex onto a semantic taxonomy —
AK's kanda-3 vargas (words organized by form/lexical relation) and semdom's
top-level 9 "Grammar". This script derives every number in that table from the
two live sources; nothing is hand-copied.

Counterpart branch pairings are the ones documented in the companion doc
(avyaya ~ 9.2.2 + 9.2.5-9.2.7; visheshyanighna ~ 9.1.4 + 9.2.1); nanartha and
sankirna deliberately have NO counterpart — the asymmetries are findings, not
gaps. Pairings live here as data so the table is auditable.

Inputs: semdom.json (fetched/cached by semdom_varga_crosswalk.load_semdom) and
../../AMAR/amar.txt — same sources, parsers reused via import.

Usage: python data/semdom_ak_annex_table.py [path/to/semdom.json] [path/to/amar.txt]
Emits the markdown table + summary lines to stdout.
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from semdom_varga_crosswalk import (  # noqa: E402
    AMAR_DEFAULT,
    EXCLUDED,
    VARGAS,
    load_semdom,
    load_vargas,
)

# The documented counterpart branches (companion doc, "The grammatical vargas
# and semdom's own Grammar annex"). None = the annex bucket has no semdom
# counterpart, which is itself reported.
ANNEX_PAIRS = {
    "AK-3.1": ["9.1.4", "9.2.1"],          # visheshyanighna: adjectives
    "AK-3.2": [],                           # sankirna: miscellany
    "AK-3.3": [],                           # nanartha: homonyms
    "AK-3.4": ["9.2.2", "9.2.5", "9.2.6", "9.2.7"],  # avyaya: indeclinables
}
NO_COUNTERPART_WHY = {
    "AK-3.2": "no counterpart: a miscellany tail, not a category",
    "AK-3.3": "no counterpart: semdom handles polysemy by multiple listing, not a bucket",
}


def subtree_codes(domains, code):
    """The domain code plus all its descendants (prefix match on 'code.')."""
    return [k for k in domains if k == code or k.startswith(code + ".")]


def main():
    semdom_path = sys.argv[1] if len(sys.argv) > 1 else None
    amar_path = Path(sys.argv[2]) if len(sys.argv) > 2 else AMAR_DEFAULT

    domains = load_semdom(semdom_path)
    order, counts = load_vargas(amar_path)
    assert len(domains) == 1792, f"expected 1792 domains, got {len(domains)}"
    total_synsets = sum(counts.values())
    assert total_synsets == 5590, f"expected 5590 synsets, got {total_synsets}"

    by_id = {vid: (slp1, iast) for vid, slp1, iast, _ in VARGAS}
    annex_ids = sorted(EXCLUDED)
    assert set(ANNEX_PAIRS) == set(annex_ids), "pairing keys != excluded vargas"

    top9 = subtree_codes(domains, "9")
    rows = []
    annex_synsets = 0
    for vid in annex_ids:
        slp1, iast = by_id[vid]
        n = counts[slp1]
        annex_synsets += n
        branches = []
        branch_domains = 0
        for code in ANNEX_PAIRS[vid]:
            subtree = subtree_codes(domains, code)
            assert subtree, f"unknown semdom code {code} in {vid}"
            assert all(c in top9 for c in subtree), f"{code} not under top-level 9"
            branches.append(f"{code} {domains[code]['value']}")
            branch_domains += len(subtree)
        rows.append((vid, iast, n, branches, branch_domains))

    assert annex_synsets == sum(
        counts[s] for v, s, _, k in VARGAS if k == 3
    ), "annex total != kanda-3 total"

    def pct(x, whole):
        return f"{100 * x / whole:.1f}%"

    print("| AK grammatical varga | synsets | % of kosha "
          "| semdom 9.x counterpart (subtree) | domains | % of semdom |")
    print("|---|---|---|---|---|---|")
    for vid, iast, n, branches, bd in rows:
        why = NO_COUNTERPART_WHY.get(vid)
        cell = " + ".join(branches) if branches else f"— ({why})"
        dcell = str(bd) if branches else "0"
        pcell = pct(bd, len(domains)) if branches else "0%"
        print(f"| {vid} {iast} | {n} | {pct(n, total_synsets)} "
              f"| {cell} | {dcell} | {pcell} |")
    paired_domains = sum(bd for _, _, _, br, bd in rows if br)
    print(f"| **kāṇḍa 3 total** | **{annex_synsets}** "
          f"| **{pct(annex_synsets, total_synsets)}** "
          f"| **semdom top-level 9 (whole annex)** | **{len(top9)}** "
          f"| **{pct(len(top9), len(domains))}** |")
    print()
    print(f"annex share: AK {annex_synsets}/{total_synsets} synsets "
          f"({pct(annex_synsets, total_synsets)}) vs semdom {len(top9)}/{len(domains)} "
          f"domains ({pct(len(top9), len(domains))}); "
          f"paired 9.x subtree domains: {paired_domains}")
    # nanartha is a polysemy register, which semdom absorbs structurally by
    # listing a word under several domains — comparing form-class annexes
    # proper means setting it aside.
    nanartha = counts[by_id["AK-3.3"][0]]
    formclass = annex_synsets - nanartha
    print(f"form-class annex proper (kāṇḍa 3 minus nānārtha): "
          f"AK {formclass}/{total_synsets} ({pct(formclass, total_synsets)}) "
          f"vs semdom {len(top9)}/{len(domains)} ({pct(len(top9), len(domains))})")


if __name__ == "__main__":
    main()
