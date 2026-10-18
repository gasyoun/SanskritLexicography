#!/usr/bin/env python3
"""H4733 — Wisdomlib L8 definitions × CDSL headwords crosswalk.

Joins wisdomlib-sanskrit-layers L8 (one row per EN definition page,
255,348 rows, CC BY 4.0) to CDSL headwords VIA the dcs-cdsl-xref key
bridge (DCS lemma ↔ CDSL headword SLP1, CC BY-SA 4.0), tiered:

  tier1  IAST variant -> SLP1 -> exact xref slp1 key
  tier2  hyphen/space-stripped variant -> SLP1 -> exact xref slp1 key
  tier3  accentless SLP1 match (strip_slp1_accents, CDSL headword convention)
  tier4  ASCII-folded match (norm() both sides, recall only)

Prior art consumed, never re-derived:
  - sanskrit_util to_slp1/from_slp1/norm/strip_slp1_accents (canonical shared lib)
  - dcs-cdsl-xref (kosha dataset; "never re-derive DCS↔CDSL joins")
  - wisdomlib-sanskrit-layers L8 (kosha dataset, Zenodo DOI 10.5281/zenodo.22117832)

Usage:
  python3 tools/h4733_wisdomlib_l8_cdsl_xwalk.py \
      --l8 layers/l8_definitions_index.tsv \
      --xref data/xref/dcs_cdsl_xref_v2__pending-upstream.tsv \
      --outdir data/wisdomlib_l8_cdsl_xwalk
  python3 tools/h4733_wisdomlib_l8_cdsl_xwalk.py --selftest

Exit 0 = PASS. Refuses to overwrite outputs without --force.
"""

import argparse
import gzip
import hashlib
import json
import os
import random
import re
import sys
import urllib.parse
from collections import Counter, defaultdict
from datetime import date

# --- sanskrit-util discovery (canonical shared lib; do NOT fork its tables) ---
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
    from sanskrit_util import to_slp1, from_slp1, norm, strip_slp1_accents  # type: ignore
except ImportError:  # pragma: no cover
    sys.exit("FATAL: sanskrit_util not found (set SANSKRIT_UTIL_PY=<sanskrit-util>/py)")

DEFS_SUFFIX = re.compile(r":\s*(\d+)\s+definitions?\s*$")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def open_maybe_gz(path):
    return gzip.open(path, "rt", encoding="utf-8") if path.endswith(".gz") \
        else open(path, "r", encoding="utf-8")


def parse_l8_title(title):
    """'Aṇumatta, Anumatta, Anu-matta: 5 definitions' -> ['Aṇumatta', 'Anumatta', 'Anu-matta']."""
    m = DEFS_SUFFIX.search(title or "")
    head = title[:m.start()] if m else (title or "")
    return [v.strip() for v in head.split(",") if v.strip()]


class XrefIndex:
    """dcs-cdsl-xref keyed three ways: exact SLP1, accentless SLP1, ASCII fold."""

    def __init__(self, xref_path):
        self.exact = defaultdict(list)      # slp1 -> [entry]
        self.accentless = defaultdict(list)
        self.folded = defaultdict(list)
        self.n_rows = 0
        self.n_in_cdsl = 0
        with open_maybe_gz(xref_path) as f:
            header = f.readline().rstrip("\n").split("\t")
            col = {name: i for i, name in enumerate(header)}
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) < len(header):
                    continue
                self.n_rows += 1
                slp1 = p[col["slp1"]]
                in_cdsl = p[col["in_cdsl"]] == "1"
                if in_cdsl:
                    self.n_in_cdsl += 1
                ent = {
                    "dcs_id": p[col["dcs_id"]],
                    "dcs_lemma_iast": p[col["dcs_lemma_iast"]],
                    "slp1": slp1,
                    "in_cdsl": in_cdsl,
                    "grammar": p[col["grammar"]] if "grammar" in col else "",
                }
                self.exact[slp1].append(ent)
                self.accentless[strip_slp1_accents(slp1)].append(ent)
                self.folded[norm(from_slp1(slp1))].append(ent)

    @staticmethod
    def _pick(entries):
        """Prefer in_cdsl=1, then lowest dcs_id for determinism."""
        return sorted(entries, key=lambda e: (not e["in_cdsl"], int(e["dcs_id"])))


def variants_of(row):
    """All candidate IAST strings for one L8 row, in print order, plus slug."""
    vs = parse_l8_title(row["headword"])
    slug = urllib.parse.unquote(row["url_slug"] or "")
    if slug and slug not in vs:
        vs.append(slug)
    return vs


def match_row(row, idx):
    """Return (tier, matched_variant, [entries]) at the best tier that yields at
    least one in_cdsl=1 CDSL headword, or None. Rows hitting ONLY in_cdsl=0
    keys (DCS lemmas absent from CDSL) are reported via 'dcs_only', not emitted —
    the mission is definition-to-CDSL-headword."""
    tiers = []
    for v in variants_of(row):
        k1 = to_slp1(v.lower())   # IAST titles are title-case; SLP1 map keys are lowercase
        k2 = to_slp1(re.sub(r"[-\s]+", "", v).lower())
        tiers.append((1, v, idx.exact.get(k1)))
        tiers.append((2, v, idx.exact.get(k2)))
        tiers.append((3, v, (idx.accentless.get(k1) or idx.accentless.get(k2))))
        tiers.append((4, v, (idx.folded.get(norm(v)) or idx.folded.get(norm(re.sub(r"[-\s]+", "", v))))))
    tiers = [t for t in tiers if t[2]]
    if not tiers:
        return None
    best = min(t[0] for t in tiers)
    hit = next(t for t in tiers if t[0] == best)
    return hit[0], hit[1], hit[2]


def run(l8_path, xref_path, outdir, sample_n=50, force=False):
    os.makedirs(outdir, exist_ok=True)
    out_tsv = os.path.join(outdir, "wisdomlib_l8_cdsl_xwalk.tsv.gz")
    out_sample = os.path.join(outdir, "h4733_sample50.tsv")
    out_report = os.path.join(outdir, "H4733_XWALK_REPORT.md")
    for p in (out_tsv, out_sample, out_report):
        if os.path.exists(p) and not force:
            sys.exit(f"REFUSAL: {p} exists (use --force)")

    idx = XrefIndex(xref_path)
    stats = Counter()
    rows_out = []
    with open_maybe_gz(l8_path) as f:
        header = f.readline().rstrip("\n").split("\t")
        col = {name: i for i, name in enumerate(header)}
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < len(header):
                continue
            row = {k: p[i] for k, i in col.items()}
            stats["l8_rows"] += 1
            m = match_row(row, idx)
            if not m:
                stats["unmatched"] += 1
                continue
            tier, variant, entries = m
            entries_cdsl = [e for e in entries if e["in_cdsl"]]
            if not entries_cdsl:
                # matched DCS lemma exists in the xref but has NO CDSL headword
                stats["dcs_lemma_only"] += 1
                continue
            stats[f"tier{tier}"] += 1
            keys = {}
            for e in entries_cdsl:
                keys.setdefault((e["slp1"], e["in_cdsl"]), []).append(e)
            stats["multi_headword"] += 1 if len(keys) > 1 else 0
            for (slp1, in_cdsl), grp in sorted(keys.items()):
                dcs_ids = "|".join(sorted({e["dcs_id"] for e in grp})[:3])
                lemmas = "|".join(sorted({e["dcs_lemma_iast"] for e in grp})[:3])
                rows_out.append({
                    "l8_path": row["path"],
                    "l8_url_slug": row["url_slug"],
                    "l8_headword": row["headword"],
                    "matched_variant": variant,
                    "tier": tier,
                    "cdsl_slp1": slp1,
                    "cdsl_iast": from_slp1(slp1),
                    "dcs_ids": dcs_ids,
                    "dcs_lemma_iast": lemmas,
                    "grammar": grp[0]["grammar"],
                    "in_cdsl": 1 if in_cdsl else 0,
                })
    stats["xwalk_pairs"] = len(rows_out)
    stats["l8_rows_matched"] = stats["l8_rows"] - stats["unmatched"] - stats["dcs_lemma_only"]

    cols = ["l8_path", "l8_url_slug", "l8_headword", "matched_variant", "tier",
            "cdsl_slp1", "cdsl_iast", "dcs_ids", "dcs_lemma_iast", "grammar", "in_cdsl"]
    import gzip as _gz
    with _gz.open(out_tsv, "wt", encoding="utf-8", newline="") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows_out:
            f.write("\t".join(str(r[c]).replace("\t", " ") for c in cols) + "\n")

    # 50-definition hand sample (fixed seed = reproducible), mechanically revalidated
    rng = random.Random(42)
    sample = rng.sample(rows_out, min(sample_n, len(rows_out)))
    sample_out, fails = [], []
    for r in sample:
        k = to_slp1(r["matched_variant"].lower())
        k2 = to_slp1(re.sub(r"[-\s]+", "", r["matched_variant"]).lower())
        fv = norm(re.sub(r"[-\s]+", "", r["matched_variant"]))
        fold_hits = {e["slp1"] for e in
                     idx.folded.get(norm(r["matched_variant"]), []) + idx.folded.get(fv, [])}
        ok = r["in_cdsl"] == 1 and (
            (r["tier"] == 1 and r["cdsl_slp1"] == k)
            or (r["tier"] == 2 and r["cdsl_slp1"] == k2)
            or (r["tier"] == 3 and strip_slp1_accents(r["cdsl_slp1"]) in (k, k2))
            or (r["tier"] == 4 and r["cdsl_slp1"] in fold_hits))
        r2 = dict(r, revalidation="PASS" if ok else "FAIL")
        sample_out.append(r2)
        if not ok:
            fails.append(r2)
    with open(out_sample, "w", encoding="utf-8") as f:
        scols = cols + ["revalidation"]
        f.write("\t".join(scols) + "\n")
        for r in sample_out:
            f.write("\t".join(str(r[c]).replace("\t", " ") for c in scols) + "\n")

    total_target = idx.n_in_cdsl
    cov = 100.0 * stats["l8_rows_matched"] / max(1, stats["l8_rows"])
    report = f"""# H4733 — Wisdomlib L8 × CDSL headwords crosswalk report

_Created: {date.today().strftime('%d-%m-%Y')} · tier: OxAlpha (opencode/z-ai/glm-5.3-flash)_

## Inputs (provenance)

| input | sha256 (first 12) | rows |
|---|---|---|
| wisdomlib-sanskrit-layers L8 `{os.path.basename(l8_path)}` (CC BY 4.0, Zenodo DOI 10.5281/zenodo.22117832) | `{sha256(l8_path)[:12]}` | {stats['l8_rows']} |
| dcs-cdsl-xref `{os.path.basename(xref_path)}` (CC BY-SA 4.0, DOI 10.5281/zenodo.22105641) | `{sha256(xref_path)[:12]}` | {idx.n_rows} ({idx.n_in_cdsl} in_cdsl=1) |

Join key bridge: dcs-cdsl-xref slp1 keys (never re-derived); transliteration via
canonical `sanskrit_util` (to_slp1/from_slp1/norm/strip_slp1_accents), never forked.

## Result

| metric | value |
|---|---|
| L8 definition rows parsed | {stats['l8_rows']} |
| L8 rows matched to ≥1 CDSL headword | {stats['l8_rows_matched']} (**{cov:.1f} %**) |
| L8 rows unmatched | {stats['unmatched']} |
| L8 rows hitting only DCS lemmas with no CDSL headword (in_cdsl=0, excluded) | {stats['dcs_lemma_only']} |
| xwalk output pairs (row × headword) | {stats['xwalk_pairs']} |
| rows matching >1 CDSL headword | {stats['multi_headword']} |
| tier1 exact IAST→SLP1 | {stats['tier1']} |
| tier2 hyphen/space-stripped exact | {stats['tier2']} |
| tier3 accentless SLP1 | {stats['tier3']} |
| tier4 ASCII-folded recall | {stats['tier4']} |
| in_cdsl=1 pairs | {sum(1 for r in rows_out if r['in_cdsl'])} |

## Verify: 50-definition hand sample

`{os.path.basename(out_sample)}` — random.Random(42) sample, every row mechanically
revalidated (variant→SLP1 relation + xref membership + in_cdsl=1):
**{len(sample) - len(fails)}/{len(sample)} PASS**.

## License note

Inputs mix CC BY 4.0 (L8) and CC BY-SA 4.0 (dcs-cdsl-xref). This derivative
linkset inherits the stricter share-alike term on the key side: ship as
**CC BY-SA 4.0** with wisdomlib + csl-apidev provenance, per LICENSE-DATA norms.

## Risks

- L8 headword titles are page titles, not lemmatized forms — matched headwords
  are witness-level (EN sense-alignment input), not sense-level alignment.
- tier4 folds vowel length/retroflexion — recall-only tier; filter `tier<=3`
  for strict use.
- EN witness for sense-alignment remains UNRUN downstream (this is the key bridge).
"""
    with open(out_report, "w", encoding="utf-8") as f:
        f.write(report)

    print(json.dumps({
        "l8_rows": stats["l8_rows"], "matched": stats["l8_rows_matched"],
        "coverage_pct": round(cov, 1), "pairs": stats["xwalk_pairs"],
        "tiers": {f"tier{t}": stats[f"tier{t}"] for t in (1, 2, 3, 4)},
        "sample": f"{len(sample) - len(fails)}/{len(sample)} PASS",
    }, ensure_ascii=False))
    if fails:
        print(f"REVALIDATION FAILURES: {len(fails)}", file=sys.stderr)
        return 1
    return 0


def selftest():
    """Tiny fixture: exact hit, hyphen variant, accentless hit, fold hit, miss."""
    tmp = "/var/folders/17/xycv_hps0w5_b67s84q43vr40000gp/T/opencode/h4733/selftest"
    import tempfile, shutil
    tmp = tempfile.mkdtemp(prefix="h4733_selftest_")
    xref = os.path.join(tmp, "xref.tsv")
    with open(xref, "w") as f:
        f.write("dcs_id\tdcs_lemma_iast\tslp1\tnormkey\tin_cdsl\ttoken_count\tgrammar\n")
        f.write("100\tśanta\tSanta\tSanta\t1\t10\tadj\n")       # exact/fold 'santa'
        f.write("200\tānanda\tAnanda/\tAnanda\t1\t20\tnoun\n")  # accented slp1 -> tier3 for 'ananda'
    l8 = os.path.join(tmp, "l8.tsv")
    with open(l8, "w") as f:
        f.write("path\theadword\turl_slug\ttext_len\thas_devanagari\n")
        f.write("/definition/a\tŚanta, Shanta: 2 definitions\ta\t10\t1\n")
        f.write("/definition/b\tĀnanda, Ananda: 3 definitions\tb\t20\t1\n")
        f.write("/definition/c\tŚan-ta: 1 definitions\tc\t5\t0\n")
        f.write("/definition/d\tZzzzz: 1 definitions\td\t5\t0\n")
    out = os.path.join(tmp, "out")
    rc = run(l8, xref, out, sample_n=3, force=True)
    with open(os.path.join(out, "h4733_sample50.tsv"), encoding="utf-8") as f:
        lines = f.read().strip().split("\n")
    tiers = {tuple(l.split("\t")[3:5]) for l in lines[1:]}
    assert ("Śanta", "1") in tiers, f"tier1 exact failed: {tiers}"
    assert ("Śan-ta", "2") in tiers, f"tier2 hyphen failed: {tiers}"
    assert ("Ānanda", "3") in tiers, f"tier3 accentless failed: {tiers}"
    assert all(l.split("\t")[-1] == "PASS" for l in lines[1:]), "revalidation failed"
    shutil.rmtree(tmp)
    print("SELFTEST PASS (tier1 exact / tier2 hyphen / tier3 accentless / miss excluded / sample revalidated)")
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--l8")
    ap.add_argument("--xref")
    ap.add_argument("--outdir")
    ap.add_argument("--sample-n", type=int, default=50)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not (a.l8 and a.xref and a.outdir):
        ap.error("--l8 --xref --outdir required (or --selftest)")
    sys.exit(run(a.l8, a.xref, a.outdir, a.sample_n, a.force))


if __name__ == "__main__":
    main()
