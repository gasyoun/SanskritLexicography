"""Level B of H742: AK synset -> candidate SIL semantic domain, via the WordNet bridge.

Pipeline per papers/SEMDOM_KOSHA_CROSSWALK_SCOPING.md section 3: each Amarakosha
`eid` synset's SLP1 lemmas are looked up in MW (csl-orig mw.txt); English gloss
content words go through Princeton WordNet (noun synsets, first 3 senses); WN
offsets map to semdom codes via the GWC-2023 release table
(lmorgadodacosta/sil-semantic-domains-wordnet-mapping, CC BY-SA 4.0); candidate
domains are ranked by the number of distinct supporting gloss words.

Outputs (next to this script):
  semdom_ak_candidates.tsv   — all 5,590 synsets, top-6 candidates each (IDs only)
  semdom_ak_gold_sample.json — stratified 200-synset annotation packet (working
                               file for the dual-annotation pass; includes gloss
                               snippets, NOT for release)

Usage: python data/semdom_ak_bridge.py [amar.txt] [mw.txt] [bridge.tsv] [semdom.json]
Requires: nltk with the wordnet corpus downloaded.
"""

import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from nltk.corpus import wordnet as wn  # noqa: E402

HERE = Path(__file__).resolve().parent
GH = HERE.parent.parent
AMAR = GH / "AMAR" / "amar.txt"
MW = GH / "csl-orig" / "v02" / "mw" / "mw.txt"
BRIDGE = HERE / "wn-links-semdom-words-all.tsv"
SEMDOM = HERE / "semdom.json"

# Vargas in file order -> canonical IDs (must match semdom_varga_crosswalk.py).
VARGA_IDS = [
    "AK-1.1", "AK-1.2", "AK-1.3", "AK-1.4", "AK-1.5", "AK-1.6", "AK-1.7",
    "AK-1.8", "AK-1.9", "AK-1.10", "AK-2.1", "AK-2.2", "AK-2.3", "AK-2.4",
    "AK-2.5", "AK-2.6", "AK-2.7", "AK-2.8", "AK-2.9", "AK-2.10", "AK-3.1",
    "AK-3.2", "AK-3.3", "AK-3.4",
]
THEMATIC = set(VARGA_IDS[:20])

STOP = set(
    """the a an of or and in to with for by on as is are was be being been it its
    this that these those from at into upon also etc very much more most other
    another any some all one two three four five six seven eight nine ten first
    second third name names kind kinds sort sorts species particular certain
    epithet epithets called so term terms word words applied according said any
    esp especially chiefly common general properly regarded considered person
    thing things man men woman women female male having made used denoting
    belonging relating peculiar proper title king son daughter wife author work
    plant tree class collection various several verse text lit fig ifc comp
    gen loc nom acc instr dat abl du sg pl pr aor perf fut impf cl mfn ind
    """.split()
)


def parse_amar(path):
    """Yield (varga_id, eid, [slp1 lemmas]) in file order."""
    out = []
    vi = -1
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith(";v{"):
                vi += 1
                continue
            m = re.match(r"<eid>(\d+)<syns><s>(.*?)</s>", ln)
            if m and vi >= 0:
                eid = int(m.group(1))
                lemmas = []
                for tok in m.group(2).split(","):
                    tok = tok.strip()
                    if "-" in tok:
                        tok = tok.rsplit("-", 1)[0]  # strip gender code
                    if tok:
                        lemmas.append(tok)
                out.append((VARGA_IDS[vi], eid, lemmas))
    return out


def parse_mw(path):
    """Return {slp1 k1: concatenated English gloss text} (first 3 entries per key)."""
    glosses = defaultdict(list)
    key = None
    body = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            if ln.startswith("<L>"):
                m = re.search(r"<k1>([^<]+)", ln)
                key = m.group(1) if m else None
                body = []
            elif ln.startswith("<LEND>"):
                if key and body and len(glosses[key]) < 3:
                    glosses[key].append(" ".join(body))
                key = None
            elif key is not None:
                t = ln.strip()
                t = re.sub(r"<s1?>.*?</s1?>", " ", t)
                t = re.sub(r"<ls>.*?</ls>", " ", t)
                t = re.sub(r"<ab>.*?</ab>", " ", t)
                t = re.sub(r"<[^>]+>", " ", t)
                t = t.replace("¦", " ")
                if t:
                    body.append(t)
    return {k: " ".join(v) for k, v in glosses.items()}


def load_bridge(path):
    """offset-pos ('01234567-n') -> set of semdom codes, English rows only."""
    m = defaultdict(set)
    with open(path, encoding="utf-8") as f:
        for ln in f:
            parts = ln.rstrip("\n").split("\t")
            if len(parts) >= 4 and "eng" in parts[3]:
                m[parts[1]].add(parts[0])
    return m


def gloss_words(text):
    return [
        w for w in re.findall(r"[a-z]+", text.lower())
        if len(w) >= 3 and w not in STOP
    ]


def candidates_for(lemmas, mw_gloss, bridge):
    """Rank semdom codes by number of distinct supporting gloss words."""
    votes = defaultdict(set)
    words = []
    for lem in lemmas[:12]:
        g = mw_gloss.get(lem)
        if g:
            words.extend(gloss_words(g)[:40])
    for w in dict.fromkeys(words):  # unique, order kept
        for syn in wn.synsets(w, "n")[:3]:
            off = f"{syn.offset():08d}-n"
            for code in bridge.get(off, ()):
                votes[code].add(w)
    ranked = sorted(votes.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    return [(code, len(ws), sorted(ws)[:6]) for code, ws in ranked[:6]], len(words) > 0


def main():
    amar = Path(sys.argv[1]) if len(sys.argv) > 1 else AMAR
    mw_path = Path(sys.argv[2]) if len(sys.argv) > 2 else MW
    bridge_path = Path(sys.argv[3]) if len(sys.argv) > 3 else BRIDGE
    semdom_path = Path(sys.argv[4]) if len(sys.argv) > 4 else SEMDOM

    synsets = parse_amar(amar)
    assert len(synsets) == 5590, f"expected 5590 synsets, got {len(synsets)}"
    print(f"AK synsets: {len(synsets)}")

    mw_gloss = parse_mw(mw_path)
    print(f"MW keys: {len(mw_gloss)}")

    bridge = load_bridge(bridge_path)
    print(f"bridge offsets (eng): {len(bridge)}")

    with open(semdom_path, encoding="utf-8") as f:
        dom = {it["key"]: it for it in json.load(f)["items"]}

    rows = []
    n_glossed = n_cand = 0
    for varga, eid, lemmas in synsets:
        cands, glossed = candidates_for(lemmas, mw_gloss, bridge)
        n_glossed += glossed
        n_cand += bool(cands)
        rows.append({
            "varga": varga, "eid": eid, "lemmas": lemmas,
            "glossed": glossed, "candidates": cands,
        })
    print(f"synsets with an MW gloss: {n_glossed} ({n_glossed/len(rows):.1%})")
    print(f"synsets with >=1 candidate domain: {n_cand} ({n_cand/len(rows):.1%})")

    with open(HERE / "semdom_ak_candidates.tsv", "w", encoding="utf-8", newline="") as f:
        f.write("varga\teid\tn_lemmas\tglossed\tcandidates\n")
        for r in rows:
            cs = ";".join(f"{c}:{n}" for c, n, _ in r["candidates"])
            f.write(f"{r['varga']}\t{r['eid']}\t{len(r['lemmas'])}\t"
                    f"{int(r['glossed'])}\t{cs}\n")

    # Stratified gold sample: >=5 per thematic varga, 200 total, proportional rest.
    rng = random.Random(42)
    by_varga = defaultdict(list)
    for r in rows:
        if r["varga"] in THEMATIC and r["candidates"]:
            by_varga[r["varga"]].append(r)
    counts = {v: len(items) for v, items in by_varga.items()}
    total = sum(counts.values())
    # >=5 per varga where the varga has 5 candidate-bearing synsets at all
    # (vyomavarga has only 2 synsets total — it contributes what it has).
    alloc = {v: min(5, counts[v]) for v in by_varga}
    rest = 200 - sum(alloc.values())
    frac = {v: counts[v] / total * rest for v in by_varga}
    for v in sorted(frac, key=lambda v: -frac[v]):
        take = min(int(round(frac[v])), counts[v] - alloc[v])
        alloc[v] += max(0, take)
    # trim/pad to exactly 200
    diff = 200 - sum(alloc.values())
    for v in sorted(counts, key=lambda v: -counts[v]):
        while diff != 0 and 5 <= alloc[v] + (1 if diff > 0 else -1) <= counts[v]:
            alloc[v] += 1 if diff > 0 else -1
            diff += -1 if diff > 0 else 1
        if diff == 0:
            break

    sample = []
    for v in by_varga:
        sample.extend(rng.sample(by_varga[v], alloc[v]))
    sample.sort(key=lambda r: (r["varga"], r["eid"]))
    assert len(sample) == 200, f"gold sample is {len(sample)}, not 200"

    packet = []
    for r in sample:
        packet.append({
            "varga": r["varga"], "eid": r["eid"],
            "lemmas": r["lemmas"][:10],
            "gloss_snippets": [
                mw_gloss[l][:200] for l in r["lemmas"][:4] if l in mw_gloss
            ][:3],
            "candidates": [
                {"code": c, "name": dom[c]["value"] if c in dom else "?",
                 "votes": n, "words": ws}
                for c, n, ws in r["candidates"]
            ],
        })
    with open(HERE / "semdom_ak_gold_sample.json", "w", encoding="utf-8") as f:
        json.dump(packet, f, ensure_ascii=False, indent=1)
    print(f"gold sample: 200 synsets, alloc per varga: "
          f"{dict(sorted(alloc.items()))}")


if __name__ == "__main__":
    main()
