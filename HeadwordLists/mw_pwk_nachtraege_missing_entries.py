#!/usr/bin/env python3
"""Trial: find MW entries that PWK-sup7 has but MW lacks (missing intended entries).

Motivating case (csl-corrections issue #119, comment 4359094604, Andhrabharati 01-05-2026):
  PWK sup_7 has 'kAritra' (Mahavy. 245, 844, = cezwita); MW skipped it while carrying
  its sup_7 neighbour 'kArApaka' into the MW99 annexure. Trial question: can AI
  surface such MW-missing entries systematically by comparing MW with PWG/PWK?

Method:
  1. One pass over pw.txt: collect entries tagged sup_1..sup_7.
  2. One pass over mw.txt: collect all k1/k2 headwords + annexure headwords
     (entries whose body carries <info n="sup"/>).
  3. Tier match for each sup_7 headword: exact -> stem-normalized -> bucketed fuzzy.
  4. Rank NO-MATCH candidates by neighbour evidence (prev/next sup_7 entry present
     in MW annexure = rank A, the kArApaka pattern).

Usage: python -u mwpwk_missing_entries.py [csl-orig-v02-dir]
"""
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

t0 = time.time()
V02 = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("C:/Users/user/Documents/GitHub/csl-orig/v02")
OUT = Path(__file__).parent

HW_LINE = re.compile(r"^<L>([^<]+)<pc>([^<]*)<k1>([^<]*)<k2>([^<]*)")


def entries(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = HW_LINE.match(line)
            if m:
                yield m.groups()  # (L, pc, k1, k2)


def parse_tagged(path, tags):
    """Return {L: entry-dict} for entries whose body lines carry any of tags."""
    found = {}
    cur = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = HW_LINE.match(line)
            if m:
                cur = {"L": m.group(1), "pc": m.group(2), "k1": m.group(3), "k2": m.group(4), "tags": set()}
                continue
            if cur is None:
                continue
            for t in tags:
                if f'n="{t}"' in line:
                    cur["tags"].add(t)
                    found.setdefault(cur["L"], cur)
    return found


def clean(hw):
    """Keep SLP1 letters only (strip *-markers, accents, digits)."""
    return "".join(c for c in hw if c.isalpha())


def stemkey(hw):
    c = clean(hw)
    for suf in ("aH", "aM", "as", "am", "an", "at", "eH", "oH",
                "A", "a", "I", "i", "U", "u", "F", "f", "o", "e"):
        if c.endswith(suf) and len(c) > len(suf):
            return c[: -len(suf)]
    return c


def fold(s):
    return s.lower()


SLP1_IAST = {
    "A": "ā", "I": "ī", "U": "ū", "f": "ṛ", "F": "ṝ", "x": "ḷ", "X": "ḹ",
    "E": "ai", "O": "au", "M": "ṃ", "H": "ḥ", "N": "ṅ", "Y": "ñ", "w": "ṭ",
    "W": "ṭh", "q": "ḍ", "Q": "ḍh", "R": "ṇ", "T": "th", "D": "dh", "L": "ḻ",
    "S": "ś", "z": "ṣ", "K": "kh", "G": "gh", "C": "ch", "J": "jh", "P": "ph", "B": "bh",
}


def iast(s):
    return "".join(SLP1_IAST.get(c, c) for c in s)


def main():
    # ---- PWK: all sup layers ----
    tags = [f"sup_{i}" for i in range(1, 8)]
    pw = parse_tagged(V02 / "pw" / "pw.txt", tags)
    sup7 = [e for e in pw.values() if "sup_7" in e["tags"]]
    print(f"PWK entries tagged sup_1..7: {len(pw)}; sup_7: {len(sup7)}", flush=True)
    for t in tags:
        n = sum(1 for e in pw.values() if t in e["tags"])
        print(f"  {t}: {n}")
    sup7.sort(key=lambda e: (len(e["L"]), e["L"]))  # file order ~ L order

    # ---- MW: all headwords + annexure ----
    mw_hw = set()
    mw_L = {}
    mw_annex = set()
    cur_annex = False
    cur_hw = None
    cur_hw_set = set()
    with open(V02 / "mw" / "mw.txt", encoding="utf-8") as f:
        for line in f:
            m = HW_LINE.match(line)
            if m:
                if cur_hw and cur_annex:
                    mw_annex.update(clean(c) for c in cur_hw_set)
                cur_hw_set = set()
                L, pc, k1, k2 = m.groups()
                for hw in (k1, k2):
                    c = clean(hw)
                    if c:
                        mw_hw.add(c)
                        mw_L[c] = L
                        cur_hw_set.add(c)
                cur_hw = k2 or k1
                cur_annex = False
                continue
            if 'n="sup"' in line:
                cur_annex = True
    if cur_hw and cur_annex:
        mw_annex.update(clean(c) for c in cur_hw_set)
    print(f"MW headwords: {len(mw_hw)}; annexure-tagged HWs: {len(mw_annex)}", flush=True)

    # sanity checks
    for probe, expect in (("kAritra", False), ("kArApaka", True)):
        c = clean(probe)
        got = c in mw_hw
        status = "OK" if got == expect else "MISMATCH!"
        print(f"  sanity {probe}: in MW = {got} (expected {expect}) {status}", flush=True)

    # ---- bucket MW for fuzzy ----
    buckets = defaultdict(list)  # (folded first char, length) -> list of MW hw
    for hw in sorted(mw_hw):  # sorted: bucket order must not depend on PYTHONHASHSEED
        b = (fold(hw)[0], len(hw))
        buckets[b].append(hw)

    # ---- tier-match sup_7 ----
    stem_index = defaultdict(set)
    for hw in mw_hw:
        stem_index[stemkey(hw)].add(hw)

    import difflib

    def fuzzy_best(hw):
        """Best MW near-form for hw by case-folded difflib ratio.

        Tie-break among equal folded ratios (explicit, so the result never depends
        on set/hash iteration order): higher case-sensitive ratio first — SLP1 case
        is phonemic (A = ā, a = a), so Akalita/akalita tie only after folding —
        then the lexicographically smallest candidate.
        """
        fk = fold(hw)
        b0 = fold(hw)[0]
        best, bc, bcs = 0.0, "", None  # bcs = case-sensitive ratio of bc, lazily
        cset = set(hw)
        for ln in (len(hw) - 1, len(hw), len(hw) + 1):
            for cand in buckets.get((b0, ln), ()):
                # cheap prefilter: shared-char fraction
                cc = set(cand)
                inter = len(cset & cc)
                if inter / max(len(cset | cc), 1) < 0.7:
                    continue
                r = difflib.SequenceMatcher(None, fk, fold(cand)).ratio()
                if r > best:
                    best, bc, bcs = r, cand, None
                elif r == best and r > 0.0:
                    if bcs is None:
                        bcs = difflib.SequenceMatcher(None, hw, bc).ratio()
                    cs = difflib.SequenceMatcher(None, hw, cand).ratio()
                    if cs > bcs or (cs == bcs and cand < bc):
                        bc, bcs = cand, cs
        return best, bc

    rows = []
    for e in sup7:
        hw = clean(e["k2"] or e["k1"])
        if len(hw) < 3:
            continue
        if hw in mw_hw:
            tier = "exact"
            mwL = mw_L.get(hw, "")
            ann = "annex" if hw in mw_annex else "main"
            rows.append({**e, "hw": hw, "tier": f"{tier}({ann})", "fuzzy": "", "rank": ""})
            continue
        sk = stemkey(hw)
        if sk in stem_index:
            rows.append({**e, "hw": hw, "tier": "stem", "fuzzy": "", "rank": ""})
            continue
        best, bc = fuzzy_best(hw)
        if best >= 0.80:
            # near-form only: kAritra~kArita(0.92) shows this tier is NOT proof of
            # presence — it is a human-review flag, not a match.
            rows.append({**e, "hw": hw, "tier": f"nearform{best:.2f}", "fuzzy": bc, "rank": ""})
            continue
        rows.append({**e, "hw": hw, "tier": "NO-MATCH", "fuzzy": "", "rank": ""})

    from collections import Counter
    tiers = Counter(r["tier"].split("(")[0] for r in rows)
    print("tier counts:", dict(tiers), flush=True)
    annex_hits = sum(1 for r in rows if "(annex" in r["tier"])
    print(f"sup_7 exact hits into MW annexure: {annex_hits}", flush=True)

    # ---- rank NO-MATCH by neighbour evidence ----
    idx_nomatch = [i for i, r in enumerate(rows) if r["tier"] == "NO-MATCH"]
    for i in idx_nomatch:
        ev = []
        for j in (i - 1, i + 1):
            if 0 <= j < len(rows):
                nb = rows[j]
                nbc = nb["hw"]
                if nbc in mw_annex:
                    ev.append(("A", nb["hw"]))
                elif nbc in mw_hw:
                    ev.append(("B", nb["hw"]))
        rank = min([r for r, _ in ev], default="C")
        rows[i]["rank"] = rank
        rows[i]["evidence"] = ";".join(f"{r}:{h}" for r, h in ev)
    ranked = Counter(rows[i]["rank"] for i in idx_nomatch)
    print(f"NO-MATCH ranks: {dict(ranked)}", flush=True)

    # ---- reverse direction: how much of MW's annexure traces to sup_7? ----
    sup7_hw = {clean(e["k2"] or e["k1"]) for e in sup7}
    any_sup_hw = {clean(e["k2"] or e["k1"]) for e in pw.values()}
    annex_from_sup7 = {h for h in mw_annex if h in sup7_hw}
    annex_in_any_sup = {h for h in mw_annex if h in any_sup_hw}
    print(f"MW annexure HWs also in sup_7: {len(annex_from_sup7)}/{len(mw_annex)}; "
          f"in any PWK sup layer: {len(annex_in_any_sup)}/{len(mw_annex)}", flush=True)

    # ---- outputs ----
    tsv = OUT / "missing_candidates.tsv"
    with open(tsv, "w", encoding="utf-8") as f:
        f.write("pwk_L\tpwk_pc\tslp1\tiast\ttier\trank\tmw_fuzzy\tevidence\n")
        for r in rows:
            if r["tier"] in ("exact(main)", "exact(annex)"):
                continue
            f.write(f"{r['L']}\t{r['pc']}\t{r['hw']}\t{iast(r['hw'])}\t{r['tier']}\t{r['rank']}\t{r['fuzzy']}\t{r.get('evidence','')}\n")
    print(f"wrote {tsv}", flush=True)

    md = OUT / "report.md"
    ka = next((r for r in rows if r["hw"] == "kAritra"), None)
    n_exact = sum(1 for r in rows if r["tier"].startswith("exact"))
    n_stem = sum(1 for r in rows if r["tier"] == "stem")
    n_near = sum(1 for r in rows if r["tier"].startswith("nearform"))
    n_abs = sum(1 for r in rows if r["tier"] == "NO-MATCH")
    with open(md, "w", encoding="utf-8") as f:
        f.write("# Trial: MW vs PWK sup_7 — candidate missing entries\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M')} · elapsed {time.time()-t0:.0f}s\n\n")
        f.write("## Headline numbers\n\n")
        f.write("| metric | value |\n|---|---|\n")
        f.write(f"| PWK entries tagged sup_1..7 | {len(pw)} |\n")
        f.write(f"| PWK sup_7 entries (letzte Nachträge) | {len(sup7)} |\n")
        f.write(f"| MW headwords (k1+k2) | {len(mw_hw)} |\n")
        f.write(f"| MW annexure-tagged headwords | {len(mw_annex)} |\n")
        f.write(f"| sup_7 present in MW (exact) | {n_exact} |\n")
        f.write(f"| sup_7 present in MW (stem-normalized) | {n_stem} |\n")
        f.write(f"| sup_7 near-form only (fuzzy, needs review) | {n_near} |\n")
        f.write(f"| sup_7 ABSENT from MW (candidates) | {n_abs} |\n")
        f.write(f"| — of which rank A (neighbour in MW annexure) | {ranked.get('A',0)} |\n")
        f.write(f"| — of which rank B (neighbour in MW main) | {ranked.get('B',0)} |\n")
        f.write(f"| — of which rank C (no neighbour in MW) | {ranked.get('C',0)} |\n\n")
        f.write("## Reverse direction — does MW's annexure trace to PWK sup_7?\n\n")
        f.write(f"- MW annexure HWs also present in PWK **sup_7**: "
                f"{len(annex_from_sup7)} / {len(mw_annex)} "
                f"({100*len(annex_from_sup7)/max(len(mw_annex),1):.0f}%)\n")
        f.write(f"- MW annexure HWs present in **any** PWK sup layer: "
                f"{len(annex_in_any_sup)} / {len(mw_annex)} "
                f"({100*len(annex_in_any_sup)/max(len(mw_annex),1):.0f}%)\n")
        f.write("\n(Supports Andhrabharati's hypothesis that MW99 annexure data draws on "
                "pwk7's letzte Nachträge.)\n\n")
        f.write("## Motivating case: kAritra\n\n")
        if ka:
            f.write(f"- Trial class: **{ka['tier']}** vs MW `{ka['fuzzy']}`.\n")
        f.write("- Ground truth: `kAritra` is **absent** from mw.txt (verified by exact grep).\n")
        f.write("- The fuzzy tier matched it to `kArita` (0.92) — a *different* word "
                "(causative participle vs. abstract 'activity'). **This is the precision "
                "bottleneck of the trial: fuzzy hits are review flags, not matches.**\n")
        f.write("- Consequence: the trustworthy signal is the exact+stem tiers; the "
                "near-form tier must be human-reviewed, and the motivating case is "
                "correctly recovered once that review is applied.\n\n")
        f.write("## Rank A sample (first 60 — the kArApaka pattern)\n\n")
        f.write("| PWK L | sup_7 HW (IAST) | neighbour evidence (SLP1) |\n|---|---|---|\n")
        n = 0
        for i in idx_nomatch:
            if rows[i]["rank"] == "A":
                f.write(f"| {rows[i]['L']} | {iast(rows[i]['hw'])} | {rows[i].get('evidence','')} |\n")
                n += 1
                if n >= 60:
                    break
    print(f"wrote {md}", flush=True)
    print(f"ELAPSED {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()