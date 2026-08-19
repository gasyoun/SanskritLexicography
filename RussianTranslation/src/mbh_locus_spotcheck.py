#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mbh_locus_spotcheck.py — is the vulgate coordinate the right verse? (H3152, VERIFICATION §3)

The coordinate a Mahābhārata citation now shows comes from csl-atlas's **fitted
index**: PWG prints a continuous Calcutta śloka number, and the index maps it to a
vulgate ``parvan.adhyaya.shloka``. A fit is not a lookup, so it needs a measured
accuracy, and a rate without a background means nothing — that is the whole lesson
of [H1652](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1652_MBH_CALCUTTA_VALIDATION_2026-07-26.md),
where a candidate map scored 11.2 % against a 2.5 % null and was rejected.

The test
--------
For each sampled citation, take the headword the citation stands under, fold both
it and the verse the coordinate points at, and ask whether the verse **contains**
the headword. Then ask the same question of a **random verse of the same parvan**.
The difference between the two is the signal; the hit rate on its own is not.

Sample: fixed seed, stratified over parvans, only citations whose headword is long
enough to be locatable (a two-character stem matches everywhere and would inflate
both columns equally while adding noise).

Why Mahābhārata only
--------------------
VERIFICATION §3 asked for 20 ``MBH.`` + 20 ``ṚV.`` + 10 ``AV.``. Only the
Mahābhārata stratum is a **measurement**: Ṛgveda and Atharvaveda coordinates are
not fitted at all — ``ṚV. 4,3,13`` is parsed into maṇḍala/hymn/verse and formatted
into a URL by a deterministic pattern, with nothing to be accurate *about*. There
is no index to validate there, so sampling it would produce a number that looks
like evidence and answers no question. The Ṛgveda risk is a different one — a
*wrongly invented* address — and it is held by
[`ls_split.splittable`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_split.py)
and ``nws_citation_wrap``'s range check, both pinned by selftests.

Run::

    python src/mbh_locus_spotcheck.py --n 50
    python src/mbh_locus_spotcheck.py --n 50 --json out.json
"""
import sys, os, io, json, re, random, argparse, subprocess, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("LS_RESOLVER_QUIET", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import mbh_locus                                                   # noqa: E402
from build_mbh_verse_pages import iter_verses, can_build           # noqa: E402
from ls_links import LS_RE, LsLinks                                # noqa: E402
from store_path import canonical_store                             # noqa: E402

try:
    from sanskrit_util import nfold
except Exception:                                     # vendored fallback
    def nfold(s):
        s = (s or "").lower()
        s = re.sub(r"[āaà]", "a", s)
        s = re.sub(r"[īi]", "i", s)
        s = re.sub(r"[ūu]", "u", s)
        s = re.sub(r"[ṛṝr]", "r", s)
        s = re.sub(r"[ṅñṇnṃ]", "n", s)
        s = re.sub(r"[śṣs]", "s", s)
        s = re.sub(r"[ṭt]", "t", s)
        s = re.sub(r"[ḍd]", "d", s)
        s = re.sub(r"[ḥh]", "h", s)
        return re.sub(r"[^a-z]", "", s)

_MBH_CITE = re.compile(r"MBH\.?\s*(\d{1,2})\s*,\s*(\d{1,5})", re.I)

#: below this many folded characters a stem matches almost any verse
MIN_STEM = 5


def load_verses():
    """``{(parvan, adhyaya, shloka): folded_iast}`` plus a per-parvan verse list."""
    by_locus, by_parvan = {}, collections.defaultdict(list)
    for parvan, adhyaya, shloka, _vid, iast in iter_verses():
        folded = nfold(iast)
        by_locus[(parvan, adhyaya, shloka)] = folded
        by_parvan[parvan].append(folded)
    return by_locus, by_parvan


def sample_citations(n, seed, store=None):
    """``[(headword_iast, parvan, calcutta_n)]`` — stratified, reproducible."""
    ll = LsLinks(etext=False)
    pool = []
    with io.open(store or canonical_store(HERE), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            iast = (d.get("iast") or "").strip()
            if len(nfold(iast)) < MIN_STEM:
                continue
            for tag in LS_RE.findall(d.get("ru") or ""):
                _n, visible = ll.parts(tag)
                m = _MBH_CITE.match((visible or "").strip())
                if m:
                    pool.append((iast, int(m.group(1)), int(m.group(2))))
    rng = random.Random(seed)
    rng.shuffle(pool)
    # stratify: spread across parvans rather than letting one dominate
    by_parvan = collections.defaultdict(list)
    for item in pool:
        by_parvan[item[1]].append(item)
    out, i = [], 0
    parvans = sorted(by_parvan)
    while len(out) < n and any(by_parvan.values()):
        p = parvans[i % len(parvans)]
        if by_parvan[p]:
            out.append(by_parvan[p].pop())
        i += 1
    return out[:n]


def run(n=50, seed=3152):
    ok, why = can_build()
    if not ok:
        print("REFUSED: %s" % why)
        return None
    by_locus, by_parvan = load_verses()
    idx = mbh_locus.MbhLocusIndex()
    rng = random.Random(seed + 1)

    hits = bg_hits = evaluable = 0
    misses, unplaced = [], 0
    for iast, parvan, cn in sample_citations(n, seed):
        loc = idx.resolve(parvan, cn)
        if not loc.vulgate:
            unplaced += 1
            continue
        try:
            p, a, s = (int(x) for x in loc.vulgate.split("."))
        except ValueError:
            unplaced += 1
            continue
        verse = by_locus.get((p, a, s))
        if verse is None:
            unplaced += 1
            continue
        evaluable += 1
        stem = nfold(iast)
        hit = stem in verse
        if hit:
            hits += 1
        else:
            misses.append({"headword": iast, "cited": "MBH. %d,%d" % (parvan, cn),
                           "coordinate": loc.vulgate,
                           "verse_head": verse[:70]})
        pool = by_parvan.get(p) or []
        if pool and stem in rng.choice(pool):
            bg_hits += 1

    rate = hits / float(evaluable or 1)
    bg = bg_hits / float(evaluable or 1)
    return {"n_requested": n, "seed": seed, "evaluable": evaluable,
            "unplaced": unplaced, "hits": hits, "rate": round(rate, 3),
            "background_hits": bg_hits, "background_rate": round(bg, 3),
            "lift": round(rate - bg, 3), "misses": misses}


def render(r):
    if not r:
        return "not run"
    out = [
        "MBh coordinate spot-check (VERIFICATION §3)",
        "",
        "sample requested        : %d (seed %d)" % (r["n_requested"], r["seed"]),
        "evaluable               : %d" % r["evaluable"],
        "unplaced by the index   : %d" % r["unplaced"],
        "",
        "headword found at the coordinate : %d/%d = %.1f%%"
        % (r["hits"], r["evaluable"], 100 * r["rate"]),
        "same check, RANDOM verse of the same parvan (background) : %d/%d = %.1f%%"
        % (r["background_hits"], r["evaluable"], 100 * r["background_rate"]),
        "lift over background             : %+.1f pp" % (100 * r["lift"]),
        "",
    ]
    if r["rate"] <= r["background_rate"]:
        out.append("VERDICT: NOT above background — the coordinate must not be "
                   "shown as an address (VERIFICATION §5, stop condition 2).")
    else:
        out.append("VERDICT: above background — the coordinate carries real "
                   "signal, and is shown with ≈ because it is a fit, not a lookup.")
    if r["misses"]:
        out.append("")
        out.append("misses, in full (%d):" % len(r["misses"]))
        for m in r["misses"]:
            out.append("  %-16s %-14s -> %-12s  %s…"
                       % (m["headword"], m["cited"], m["coordinate"],
                          m["verse_head"][:52]))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=3152)
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    r = run(a.n, a.seed)
    print(render(r))
    if r and a.json:
        with io.open(a.json, "w", encoding="utf-8") as fh:
            json.dump(r, fh, ensure_ascii=False, indent=1)
        print("\nwrote %s" % a.json)
    return 0 if r else 2


if __name__ == "__main__":
    sys.exit(main())
