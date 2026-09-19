#!/usr/bin/env python3
"""H4807 — Wisdomlib Sanskrit-dictionary glosses vs csl-orig MW/AP90: borrowed vs own.

Two lanes over the remote-extracted gloss blocks (slug, source, gloss):
  A. Attribution census  — wisdomlib pages carry explicit per-gloss "Source :"
     attributions; classify Cologne-MW / Cologne-AP90 / Cologne-other / wisdomlib
     own / other-external -> provenance share table (all blocks).
  B. Text verification   — for Cologne-MW and Cologne-AP90 attributed blocks,
     join headword (slug -> IAST -> SLP1 via canonical sanskrit_util, tiered:
     exact / hyphen-stripped / accentless / folded) to the MW + AP90 English
     gloss TM (mw_en_tm.py + h4807_ap90_glosses.py over read-only csl-orig),
     then compare normalized gloss keys (form_key):
       G1 exact | G2 containment | G3 word-overlap >= 0.6 | G4 no match
     Borrowed = G1-G3. Defects: D1 headword-miss, D2 attributed-but-no-match,
     D3 sample-level mis-attribution (gloss matches a different headword).

Usage:
  python3 tools/h4807_gloss_provenance.py --glosses data/h4807_gloss_provenance/h4807_skt_glosses.tsv.gz
  python3 tools/h4807_gloss_provenance.py --selftest
"""
import argparse
import gzip
import json
import os
import random
import re
import sys
import unicodedata
import urllib.parse
from collections import Counter, defaultdict

# --- sanskrit-util (canonical shared lib; never fork its tables) ---
_SANSKRIT_UTIL_CANDIDATES = [
    os.environ.get("SANSKRIT_UTIL_PY", ""),
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "..", "..", "sanskrit-util", "py"),
    os.path.expanduser("~/Documents/GitHub/sanskrit-util/py"),
]
for _c in _SANSKRIT_UTIL_CANDIDATES:
    if _c and os.path.isdir(os.path.join(_c, "sanskrit_util")):
        sys.path.insert(0, _c)
        break
try:
    from sanskrit_util import (to_slp1, from_slp1, norm, strip_slp1_accents)  # type: ignore
except ImportError:
    sys.exit("FATAL: sanskrit_util not found (set SANSKRIT_UTIL_PY)")

HERE = os.path.dirname(os.path.abspath(__file__))
MW_JSON = os.path.join(HERE, "..", "RussianTranslation", "src", "mw_en_tm.json")
AP_JSON = os.path.join(HERE, "h4807_ap90_glosses.json")

STOP = {"the", "a", "an", "of", "in", "to", "with", "and", "or", "is", "for",
        "as", "on", "be", "it", "its", "by", "from", "at", "that", "which",
        "b", "c", "d", "cf"}

CLASS_ORDER = ["cologne_mw", "cologne_ap90", "cologne_other", "wisdom_own",
               "other_external"]


def classify(source):
    s = source.lower()
    if "cologne digital sanskrit dictionaries" in s:
        if "monier-williams" in s or "monier williams" in s:
            return "cologne_mw"
        if "apte" in s:
            return "cologne_ap90"
        return "cologne_other"
    if "practical sanskrit-english dictionary" in s:
        # wisdomlib attributes Apte 1890 (== csl-orig ap90) as DDSA
        return "cologne_ap90"
    if "wisdom library" in s:
        return "wisdom_own"
    return "other_external"


def form_key(s):
    t = unicodedata.normalize("NFKD", s)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"[^a-z ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def jaccard(a, b):
    wa = set(a.split()) - STOP
    wb = set(b.split()) - STOP
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


_NAV = re.compile(r"\[\s*«previous.*?next»\s*\]", re.S | re.I)
_GLOSSARY_HDR = re.compile(r"\b\w+\s+in\s+Sanskrit\s+glossary\b", re.I)
_BRACK = re.compile(r"\[[^\[\]]*\]")   # MW inline markup [..]; looped for nesting
_HDR = re.compile(r"^\s*[^\s:(]+\s*\([^)]*\)\s*:?\s*—?\s*")


def clean_wl_gloss(g):
    """wisdomlib block -> gloss prose: drop nav brackets, section header, MW
    inline markup brackets (mirror of mw_en_tm clean_body bracket drop)."""
    g = _NAV.sub(" ", g)
    g = _GLOSSARY_HDR.sub(" ", g)
    for _ in range(3):
        g = _BRACK.sub(" ", g)
    g = _HDR.sub(" ", g, count=1)
    return g


class TmIndex:
    """MW/AP90 English gloss TM: exact, cleaned, accentless, folded key indexes."""

    def __init__(self, tm_json):
        self.exact = {}
        self.accentless = defaultdict(list)
        self.folded = defaultdict(list)
        self.segs = {}
        with open(tm_json, encoding="utf-8") as f:
            tm = json.load(f)
        for k, v in tm.items():
            self.exact[k] = k
            self.accentless[strip_slp1_accents(k)].append(k)
            self.folded[form_key(from_slp1(strip_slp1_accents(k)))].append(k)
            self.segs[k] = [x for x in (form_key(p) for p in re.split(r"[;|]", v)) if x]

    def lookup(self, slp1):
        """Tiers: 1 exact | 2 hyphen/space/digit-stripped | 3 accentless
        | 4 wisdomlib-slug geminate-vowel repair | 5 canonical folded."""
        s2 = re.sub(r"[-\s0-9]", "", slp1)
        if s2 in self.exact:
            return s2, 2
        acc = strip_slp1_accents(s2)
        cands = self.accentless.get(acc)
        if cands:
            return cands[0], 3
        gem = (s2.replace("aa", "A").replace("ii", "I").replace("uu", "U")
                 .replace("Aa", "A").replace("II", "I").replace("UU", "U"))
        if gem != s2:
            acc2 = strip_slp1_accents(gem)
            cands = self.accentless.get(gem) or self.accentless.get(acc2)
            if cands:
                return cands[0], 4
        fold = form_key(from_slp1(acc))
        cands = self.folded.get(fold)
        if cands:
            return cands[0], 5
        return None, 0


def gloss_verdict(gloss_key, seg_keys):
    if not gloss_key or not seg_keys:
        return 4, ""
    for sk in seg_keys:
        if sk == gloss_key:
            return 1, sk
    for sk in seg_keys:
        if sk and gloss_key and (sk in gloss_key or gloss_key in sk):
            ratio = min(len(sk), len(gloss_key)) / max(len(sk), len(gloss_key), 1)
            if ratio >= 0.6 or min(len(sk), len(gloss_key)) >= 15:
                return 2, sk
    best, bsk = 0.0, ""
    for sk in seg_keys:
        j = jaccard(gloss_key, sk)
        if j > best:
            best, bsk = j, sk
    if best >= 0.6:
        return 3, bsk
    return 4, ""


def slug_to_slp1(slug):
    try:
        iast = urllib.parse.unquote(slug)
    except Exception:
        return None
    try:
        slp1 = to_slp1(iast)
        return slp1 or None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glosses", required=True)
    ap.add_argument("--outdir", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data",
        "h4807_gloss_provenance"))
    ap.add_argument("--limit", type=int, default=0, help="smoke-run cap")
    ap.add_argument("--sample", type=int, default=50)
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    mw = TmIndex(MW_JSON)
    ap90 = TmIndex(AP_JSON)
    sys.stderr.write("TM loaded mw=%d ap90=%d\n" % (len(mw.exact), len(ap90.exact)))

    src_census = Counter()
    cls_census = Counter()
    rows_mwap = []
    total = 0
    opener = gzip.open if args.glosses.endswith(".gz") else open
    with opener(args.glosses, "rt", encoding="utf-8") as f:
        header = f.readline()
        assert header.startswith("slug\tsource\tgloss"), header
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 3:
                continue
            if args.limit and total >= args.limit:
                break
            total += 1
            slug, source, gloss = p[0], p[1], p[2]
            src_census[source] += 1
            cls = classify(source)
            cls_census[cls] += 1
            if cls in ("cologne_mw", "cologne_ap90"):
                tm = mw if cls == "cologne_mw" else ap90
                slp1 = slug_to_slp1(slug)
                hw, hw_tier = (None, 0)
                if slp1:
                    hw, hw_tier = tm.lookup(slp1)
                gk = form_key(clean_wl_gloss(gloss))
                if hw is None:
                    rows_mwap.append((slug, cls, source, gloss, "D1_headword_miss",
                                      0, hw_tier, "", "", gk))
                else:
                    gt, seg = gloss_verdict(gk, tm.segs[hw])
                    verdict = "match_G%d" % gt if gt < 4 else "D2_no_text_match"
                    rows_mwap.append((slug, cls, source, gloss, verdict,
                                      gt, hw_tier, hw, seg, gk))
    sys.stderr.write("rows=%d\n" % total)

    # sample50: balanced MW/AP from G1-G3 matches + D2 defect rows, revalidated
    rng = random.Random(42)
    ok_rows = [r for r in rows_mwap if r[4].startswith("match_G")]
    half = args.sample // 2
    samp = []
    mw_ok = [r for r in ok_rows if r[1] == "cologne_mw"]
    ap_ok = [r for r in ok_rows if r[1] == "cologne_ap90"]
    samp += rng.sample(mw_ok, min(half, len(mw_ok)))
    samp += rng.sample(ap_ok, min(half, len(ap_ok)))
    remain = args.sample - len(samp)
    if remain > 0:
        rest = [r for r in ok_rows if r not in samp]
        samp += rng.sample(rest, min(remain, len(rest)))
    # D3 probe on sample no-match/defect rows: exact key elsewhere in same TM?
    d3 = []
    for r in samp:
        if r[4] in ("D1_headword_miss", "D2_no_text_match"):
            tm = mw if r[1] == "cologne_mw" else ap90
            hits = [k for k, segs in tm.segs.items() if r[9] in segs]
            d3.append((r[0], "D3_misattrib" if hits else "D3_no_other_home",
                       ";".join(hits[:5])))
    reval = 0
    for r in samp:
        if r[4].startswith("match_G"):
            tm = mw if r[1] == "cologne_mw" else ap90
            hw = tm.lookup(slug_to_slp1(r[0]))[0] if slug_to_slp1(r[0]) else None
            gt, _ = gloss_verdict(r[9], tm.segs[hw] if hw else [])
            if ("match_G%d" % gt) == r[4]:
                reval += 1

    # ---- outputs ----
    out_tsv = os.path.join(args.outdir, "h4807_mwap_match.tsv.gz")
    with gzip.open(out_tsv, "wt", encoding="utf-8") as f:
        f.write("slug\tclass\tsource\tverdict\tgloss_tier\thw_tier\thw_slp1\t"
                "matched_seg\tgloss\n")
        for r in rows_mwap:
            f.write("\t".join(str(x) for x in (
                r[0], r[1], r[2], r[4], r[5], r[6], r[7], r[8], r[3].replace("\t", " "))) + "\n")
    samp_tsv = os.path.join(args.outdir, "h4807_sample%d.tsv" % args.sample)
    with open(samp_tsv, "w", encoding="utf-8") as f:
        f.write("slug\tclass\tverdict\thw_slp1\tmatched_seg\tgloss\n")
        for r in samp:
            f.write("\t".join(str(x) for x in (
                r[0], r[1], r[4], r[7], r[8], r[3].replace("\t", " "))) + "\n")
    stats = {
        "gloss_blocks_total": total,
        "class_census": dict(cls_census),
        "top_sources": [[s, n] for s, n in src_census.most_common(30)],
        "mwap_attributed": len(rows_mwap),
        "mw_attributed": cls_census["cologne_mw"],
        "ap90_attributed": cls_census["cologne_ap90"],
        "verdict_census": dict(Counter(r[4] for r in rows_mwap)),
        "sample_rows": len(samp),
        "sample_revalidated": reval,
        "sample_d3": [[a, b, c] for a, b, c in d3],
    }
    with open(os.path.join(args.outdir, "h4807_stats.json"), "w",
              encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: stats[k] for k in (
        "gloss_blocks_total", "class_census", "mwap_attributed",
        "verdict_census", "sample_rows", "sample_revalidated")},
        ensure_ascii=False, indent=1))
    ok = (reval == sum(1 for r in samp if r[4].startswith("match_G"))
          and (total > 1000 or bool(args.limit)))
    print("SELFTEST/%s" % ("PASS" if ok else "FAIL"))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except AttributeError:
        pass
    main()
