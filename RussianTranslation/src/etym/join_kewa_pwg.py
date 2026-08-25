"""Join the normalized KEWA heading index to PWG headwords (H3169, ceiling C4).

The join is *dhatu-aware* on purpose.  KEWA heads its verbal articles with a
**finite form** (`bhavati`, `aksnoti`) where PWG keys the **root** (`BU`,
`akzR`), and it heads its nominal articles with the **nominative singular**
(`amsah`) where PWG keys the **stem** (`aMSa`).  A surface-string join
therefore drops the entire verbal core *and* most of the nominal core - so
every match carries a `match_basis` saying how it was reached, and unmatched
stays a reportable class rather than being pushed onto a near-miss headword.

Match ladder, first hit wins:

| `match_basis` | how |
|---|---|
| `exact` | the KEWA key is itself a PWG key1 headword |
| `sandhi/diacritic-normalized` | final visarga / anusvara / neuter -m dropped, then exact |
| `inflected-form->stem` | a form->lemma witness analyses it as a **nominal** form of a PWG headword |
| `finite-form->root` | no nominal reading lands in PWG, but a **verbal** one does - the dhatu step |
| `ambiguous-multi` | the chosen route reaches >1 distinct PWG headword |
| `unmatched` | none of the above - reported, never collapsed onto a near miss |

**Why the rule route outranks the witness route.** Adjudication of the seeded
sample caught `aknaH` (KEWA अक्नः) being sent to the root `aYc` by DCS while
PWG's own headword `akna` sat one visarga away.  A truncation that lands on a
PWG headword is an identity on the same lexeme; a form->lemma analysis is a
morphological claim that may pick a different one.  Identity wins, and the
witness route is still recorded in `lemma_route` so nothing is lost.

No length or sibilant folding is used anywhere (Uprava DEAD_ENDS section 7:
folding collapses the minimal pairs that define Sanskrit lexical identity).

Usage:
    python join_kewa_pwg.py [--github-root DIR] [--outdir DIR]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = "C:/Users/user/Documents/GitHub"
PWG_KEY1 = "SanskritLexicography/HeadwordLists/now-2026/PWG-unique-key1-106082.txt"
DCS = "SanskritRussian/dcs_form2lemma.tsv"
VIDYUT = "SanskritRussian/vidyut_form2lemma.tsv"

SLP1_OK = set("aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh")
LANE = "modern-IE"   # never merged with the traditional (Cologne) lane
COLS = ["lane", "kewa_seq", "vol", "page", "heading_idx", "kewa_slp1", "match_basis",
        "pwg_key1", "witness", "n_candidates", "lemma_route", "routes_agree",
        "flags"]


def load_pwg(path: str) -> set[str]:
    with open(path, encoding="utf-8") as fh:
        return {line.strip() for line in fh if line.strip()}


def load_form2lemma(path: str, pos_col: int, verb_tokens: set[str]):
    """form -> {"verbal": {lemmas}, "nominal": {lemmas}}.

    The split matters: DCS tags participles and agent nouns VERB as readily as
    it tags a 3sg present, so "the witness said VERB" is not "this is a finite
    form".  Keeping the two lemma sets apart lets the join prefer the nominal
    reading and fall back to the root, which is the dhatu-aware step the C4
    ruling asks for.

    A missing sibling clone is a documented degradation, not a crash: the
    summary records `present=false` so a later reader can tell a real zero from
    an absent witness.
    """
    forms: dict[str, dict[str, set[str]]] = collections.defaultdict(
        lambda: {"verbal": set(), "nominal": set()})
    if not os.path.exists(path):
        return forms, False
    with open(path, encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) <= pos_col:
                continue
            form, lemma, pos = parts[0], parts[1], parts[pos_col]
            if not form or not lemma:
                continue
            slot = "verbal" if pos.strip().lower() in verb_tokens else "nominal"
            forms[form][slot].add(lemma)
    return forms, True


def rule_variants(key: str) -> list[str]:
    """Morphological truncations of a citation form - never a folding."""
    out: list[str] = []
    if len(key) > 1 and key[-1] in "HmM":
        out.append(key[:-1])
    return out


# Truncations the join deliberately does NOT apply, used only to size the
# unmatched residue.  Applying them would need a morphological witness per row;
# counting them says how much of the residue is a witness gap rather than a
# real absence from PWG.
DIAGNOSTIC_TRUNCATIONS = {
    "present-stem->root": ("ati", "ate", "oti", "ute", "Ati", "Iti"),
    "feminine-in-stem": ("I",),
}


def diagnose_unmatched(key: str, pwg: set[str]) -> str:
    for ending in DIAGNOSTIC_TRUNCATIONS["present-stem->root"]:
        if key.endswith(ending) and key[: -len(ending)] in pwg:
            return "present-stem->root"
    if key.endswith("I") and len(key) > 1:
        stem = key[:-1]
        if stem + "in" in pwg or stem in pwg or stem + "a" in pwg:
            return "feminine-in-stem"
    return "no-nearby-pwg-headword"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--github-root", default=DEFAULT_ROOT)
    ap.add_argument("--indir", default=os.path.join(HERE, "..", "..", "data", "etym"))
    ap.add_argument("--outdir", default=os.path.join(HERE, "..", "..", "data", "etym"))
    args = ap.parse_args()

    root = args.github_root
    indir, outdir = os.path.abspath(args.indir), os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)

    pwg = load_pwg(os.path.join(root, PWG_KEY1))
    dcs_forms, dcs_ok = load_form2lemma(os.path.join(root, DCS), 2, {"verb", "aux"})
    vid_forms, vid_ok = load_form2lemma(os.path.join(root, VIDYUT), 2, {"verb"})
    print(f"PWG key1 headwords: {len(pwg)}")
    print(f"DCS form->lemma: {len(dcs_forms)} (present={dcs_ok})")
    print(f"vidyut form->lemma: {len(vid_forms)} (present={vid_ok})")

    src = os.path.join(indir, "kewa_index_normalized.tsv")
    with open(src, encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        rows = [dict(zip(header, line.rstrip("\n").split("\t"))) for line in fh]

    census: collections.Counter = collections.Counter()
    out = []
    for r in rows:
        key = r["slp1"]
        flags = [f for f in r["flags"].split("|") if f]
        row = {"lane": LANE, "kewa_seq": r["kewa_seq"], "vol": r["vol"], "page": r["page"],
               "heading_idx": r["heading_idx"], "kewa_slp1": key,
               "pwg_key1": "", "witness": "", "n_candidates": 0}

        if not key or any(ch not in SLP1_OK for ch in key):
            flags.append("key-unusable")
            census["key-unusable"] += 1
            census["unmatched"] += 1
            out.append({**row, "match_basis": "unmatched", "flags": "|".join(flags)})
            continue

        # The witness route is always computed, even when a higher rung wins -
        # it is what `lemma_route` reports, and its disagreement with the
        # chosen rung is itself a reviewable signal.
        verbal: set[str] = set()
        nominal: set[str] = set()
        wits: list[str] = []
        for name, table in (("dcs", dcs_forms), ("vidyut", vid_forms)):
            if key in table:
                verbal |= table[key]["verbal"]
                nominal |= table[key]["nominal"]
                wits.append(name)
        nom_pwg = sorted(lem for lem in nominal if lem in pwg)
        vrb_pwg = sorted(lem for lem in verbal if lem in pwg)
        lemma_hits = nom_pwg or vrb_pwg
        lemma_basis = ("inflected-form->stem" if nom_pwg
                       else "finite-form->root" if vrb_pwg else "")
        if len(lemma_hits) > 1:
            lemma_basis = "ambiguous-multi"

        basis, hits, witness = "unmatched", [], ""
        if key in pwg:
            basis, hits, witness = "exact", [key], "PWG-key1"
        else:
            for v in rule_variants(key):
                if v not in pwg:
                    continue
                # The -as trap, caught in adjudication: `enaH` truncates to
                # `ena`, which IS a PWG headword - but a different lexeme.  The
                # word is `enas`, and the witness says so.  Whenever the
                # truncation plus `s` is one of the witness lemmas, that neuter
                # -as stem wins over the homograph.
                as_stem = v + "s"
                if as_stem in lemma_hits:
                    basis, hits, witness = "inflected-form->stem", [as_stem], "+".join(wits)
                    flags.append("as-stem-disambiguated")
                    census["as-stem-disambiguated"] += 1
                else:
                    basis, hits, witness = "sandhi/diacritic-normalized", [v], "rule"
                break
            if basis == "unmatched" and lemma_hits:
                basis, hits, witness = lemma_basis, lemma_hits, "+".join(wits)

        lemma_route = "|".join(lemma_hits)
        if not lemma_hits:
            routes_agree = ""
        elif basis in ("inflected-form->stem", "finite-form->root", "ambiguous-multi"):
            routes_agree = "same-route"
        else:
            routes_agree = "1" if set(hits) == set(lemma_hits) else "0"
            if routes_agree == "0":
                flags.append("routes-disagree")
                census["routes-disagree"] += 1

        census[basis] += 1
        if basis == "unmatched":
            census[f"unmatched-diagnostic:{diagnose_unmatched(key, pwg)}"] += 1
        out.append({**row, "match_basis": basis, "pwg_key1": "|".join(hits),
                    "witness": witness, "n_candidates": len(hits),
                    "lemma_route": lemma_route, "routes_agree": routes_agree,
                    "flags": "|".join(flags)})

    tsv = os.path.join(outdir, "kewa_pwg_crosswalk.tsv")
    with open(tsv, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(COLS) + "\n")
        for r in out:
            fh.write("\t".join(str(r.get(c, "")) for c in COLS) + "\n")

    total = len(out)
    matched = total - census["unmatched"]
    summary = {
        "rows": total,
        "matched": matched,
        "matched_pct": round(100.0 * matched / total, 2) if total else 0.0,
        "by_match_basis": dict(sorted(census.items())),
        "sources": {
            "pwg_key1": PWG_KEY1, "pwg_key1_rows": len(pwg),
            "dcs_form2lemma": DCS, "dcs_present": dcs_ok,
            "vidyut_form2lemma": VIDYUT, "vidyut_present": vid_ok,
        },
    }
    cj = os.path.join(outdir, "kewa_pwg_crosswalk_summary.json")
    with open(cj, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {tsv}")
    print(f"wrote {cj}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
