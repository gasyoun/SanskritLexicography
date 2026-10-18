"""Re-run the 164 top-title / 774 check on the flattened ACC surface (H6993).

Pre-flatten baseline (grill Q7, quoted): 164 hand-adjudicated PD primary
titles against 774 top-title records; 122 exact ACC headword matches (C3
sweep, reused fold).  This script re-derives the 122 and measures the same
164 titles against acc_works_flat.tsv (the <HI1> work surface).
"""
import csv
import gzip
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))

_SLP1 = {"K": "k", "G": "g", "C": "c", "J": "j", "W": "t", "Q": "d", "T": "t",
         "D": "d", "P": "p", "B": "b", "N": "n", "Y": "n", "R": "n", "S": "s",
         "z": "s", "q": "d", "w": "t", "M": "m", "H": "h", "A": "a", "I": "i",
         "U": "u", "f": "r", "F": "r", "x": "l", "X": "l", "E": "e", "O": "o"}


def c3fold(text):
    """C3 two-sided fold: parentheticals stripped, diacritics/vowel length
    dropped, IAST digraphs and SLP1 aspirates/retroflexes flattened."""
    s = re.sub(r"\([^)]*\)", "", text or "")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    for a, b in (("bh", "b"), ("dh", "d"), ("th", "t"), ("kh", "k"),
                 ("gh", "g"), ("ch", "c"), ("jh", "j"), ("ṭh", "t"),
                 ("ḍh", "d"), ("ph", "p"), ("ai", "e"), ("au", "o"),
                 ("ṃ", "m"), ("ḥ", "h")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z]", "", s)


def slp1_flat(s):
    return "".join(_SLP1.get(c, c) for c in s)


def main():
    pd_titles = []
    with open(os.path.join(HERE, "pd_top_titles_164.tsv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            pd_titles.append(r["display_title"].strip())
    assert len(pd_titles) == 164, len(pd_titles)

    k1 = set()
    with open(os.path.join(HERE, "acc.jsonl"), encoding="utf-8") as f:
        for line in f:
            k1.add(c3fold(slp1_flat(json.loads(line)["k1_slp1"])))
    pre = sum(1 for t in pd_titles if c3fold(t) in k1)

    flat = set()
    with open(os.path.join(HERE, "acc_works_flat.tsv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            flat.add(c3fold(r["title"]))
    post = sum(1 for t in pd_titles if c3fold(t) in flat)
    union = sum(1 for t in pd_titles if c3fold(t) in k1 or c3fold(t) in flat)
    recovered = [t for t in pd_titles if c3fold(t) not in k1 and c3fold(t) in flat]

    # P2 approved top-title list, measured from the committed verdicts
    p2_path = os.path.join(HERE, "p2_agent_verdicts.jsonl.gz")
    p2_measured = None
    if os.path.exists(p2_path):
        accs = set()
        with gzip.open(p2_path, "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r.get("decision") == "approve":
                    accs.add(str(r["acc_L"]))
        p2_measured = len(accs)

    out = {
        "pd_top_titles": len(pd_titles),
        "pre_flatten_acc_k1_match": pre,
        "pre_flatten_quoted_top_title_list_774": 774,
        "p2_approved_top_title_records_measured": p2_measured,
        "post_flatten_hi1_work_match": post,
        "union_record_or_hi1_match": union,
        "recovered_by_flatten": len(recovered),
        "recovered_titles": recovered,
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))
    with open(os.path.join(HERE, "top_title_check.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
