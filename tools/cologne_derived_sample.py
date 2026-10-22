#!/usr/bin/env python3
"""Derived-site freshness sample for the Cologne entry census (H7223).

Takes MW **added records** (``kind=add``) from ``reports/cologne_entry_census.tsv``
and asks the two derived sites whether they already carry them:

  michaelmeyer.fr          direct fetch of the meta page; the MW section is
                           located by ``<h2 id="mw">`` and the headword is
                           matched after diacritic/comma/hyphen folding
  sanskritdictionary.com   direct fetch; Cloudflare answers a managed challenge
                           from this machine (403 "Just a moment..."), so the
                           site's rows are written as BLOCKED-CF unless a
                           CF-safe results file is merged in with
                           ``--sd-results`` (one JSON entry per headword).

Why additions: the headword's presence in the MW section is a clean binary fact
— it does not depend on gloss wording, abbreviation expansion ("l˚" -> "law") or
Cologne's editorial markup, all of which make text-marker matching noisy (the
first draft of this script failed its own 2019 controls 4/4 for exactly that
reason). A page with no MW section, or a 404, is SKIPPED: absence of a page is
not evidence of staleness, because the meta site only carries the headwords it
digitised.

Verdicts:

  PRESENT       the MW section of the derived page carries the added headword
  ABSENT        the page exists but its MW section does not carry the headword
                -> the derived MW copy predates that addition
  BLOCKED-CF    the site never answered (Cloudflare wall); not counted as
                staleness
  FETCH-FAIL    transport error; not counted as staleness

Controls are 2019/2021 additions (the csl-orig import era): any site carrying
Cologne's MW text at all must show them PRESENT, which separates "site is
stale" from "method does not work on this site".

Deterministic picks (sorted census rows, first N per year). Receipts keep the
page sha256 + the MW-section excerpt under ``reports/cologne_derived_receipts/``.

Usage:
  python3 tools/cologne_derived_sample.py --census reports/cologne_entry_census.tsv
"""
import argparse
import collections
import gzip
import csv
import hashlib
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "HeadwordLists" / "works_catalogue"))
from flatten_acc_hi1 import slp1_to_iast  # noqa: E402 — canonical repo converter

SITE_MM = "michaelmeyer.fr"
SITE_SD = "sanskritdictionary.com"
MM_URL = "https://michaelmeyer.fr/sanskrit/meta/terms/{iast}"
SD_URL = "https://sanskritdictionary.com/?q={iast}&iencoding=iast"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 cologne-census-sample/1.0")


def norm(text: str) -> str:
    """Visible-text normalisation shared by page and excerpt sides."""
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u00ad", "").replace("\u200b", "")
    return re.sub(r"\s+", " ", text).strip()


def fold(text: str) -> str:
    """Diacritic-, case- and punctuation-insensitive key for headword matching."""
    text = unicodedata.normalize("NFD", html.unescape(text or ""))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z]", "", text.lower())


def fetch(url: str, timeout: int = 30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace"), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, (e.read()[:4000].decode("utf-8", "replace") if e.fp else ""), url
    except Exception as e:  # noqa: BLE001 — the failure class is the receipt
        return 0, f"{type(e).__name__}: {e}", url


def is_cf_wall(http: int, body: str) -> bool:
    b = (body or "").lower()
    # codeql[py/incomplete-url-substring-sanitization] — page-body marker, not URL sanitisation
    return (http in (403, 503) and ("just a moment" in b or "challenges.cloudflare.com" in b)) or http == 0


def mw_section(body: str) -> str:
    """Visible text of the ``<h2 id="mw">`` section ('' when the page has none)."""
    m = re.search(r'<h2 id="mw"', body or "")
    if not m:
        return ""
    seg = body[m.start():]
    nxt = seg.find("<h2", 10)
    if nxt > 0:
        seg = seg[:nxt]
    return norm(seg)


def pick_candidates(rows, year_counts, kind="add", dict_code="mw"):
    out, seen = [], set()
    for year, count in year_counts:
        picked = 0
        for r in rows:
            if picked >= count:
                break
            if (r["dc_year"] != year or r["dict"] != dict_code or r["kind"] != kind
                    or not r["headword"].isascii() or len(r["headword"]) < 4):
                continue
            if r["headword"] in seen:
                continue
            seen.add(r["headword"])
            out.append(r)
            picked += 1
    return out


def sd_probe() -> dict:
    http, body, url = fetch(SD_URL.format(iast="dharma"))
    return {"site": SITE_SD, "url": url, "http": http, "cf_wall": is_cf_wall(http, body),
            "page_sha256": hashlib.sha256(body.encode("utf-8", "replace")).hexdigest(),
            "page_bytes": len(body.encode("utf-8", "replace")), "excerpt": norm(body)[:200]}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--census", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=ROOT / "reports" / "cologne_derived_sample_receipts.tsv")
    ap.add_argument("--receipts-dir", type=Path, default=ROOT / "reports" / "cologne_derived_receipts")
    ap.add_argument("--samples", type=int, default=20)
    ap.add_argument("--controls", type=int, default=4)
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--edge-after", default=None,
                    help="also probe MW additions committed on/after this date (YYYY-MM-DD), role=edge")
    ap.add_argument("--edge-limit", type=int, default=12)
    ap.add_argument("--sd-results", type=Path, default=None,
                    help="JSON {headword: {http, text}} of CF-safe sanskritdictionary.com fetches to merge")
    args = ap.parse_args()

    if args.census.suffix == ".gz":
        fh = gzip.open(args.census, "rt", encoding="utf-8")
    else:
        fh = args.census.open(encoding="utf-8")
    with fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    rows.sort(key=lambda r: (r["dc_year"], r["dict"], r["L"], r["commit"]))
    sample_cands = pick_candidates(rows, [("2026", 14), ("2025", 14), ("2024", 14)])
    control_cands = pick_candidates(rows, [("2021", 3), ("2019", 3)])

    sd_merge = json.loads(args.sd_results.read_text(encoding="utf-8")) if args.sd_results else {}
    probe = sd_probe()
    sd_blocked = probe["cf_wall"]
    print(f"sanskritdictionary.com probe: http={probe['http']} cf_wall={sd_blocked}")

    header = ("site\tdc_year\tdict\tL\theadword\tiast\tkind\trole\tmarker\thttp\tverdict\treceipt\n")
    lines, receipts = [header], []
    args.receipts_dir.mkdir(parents=True, exist_ok=True)

    def emit(site, row, role, http, verdict, receipt):
        slug = re.sub(r"[^A-Za-z0-9_.-]", "_", row["headword"])
        rdir = args.receipts_dir / ("michaelmeyer" if site == SITE_MM else "sanskritdictionary")
        rdir.mkdir(parents=True, exist_ok=True)
        rpath = rdir / f"{slug}.json"
        receipt["role"] = role
        receipt["verdict"] = verdict
        rpath.write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        receipts.append(receipt)
        rel = rpath.relative_to(ROOT)
        lines.append("\t".join([site, row["dc_year"], row["dict"], row["L"], row["headword"],
                                row["iast"], row["kind"], role, row["marker"], str(http),
                                verdict, str(rel)]) + "\n")
        print(f"{site:23} {row['iast']:22} {row['dc_year']} {role:8} http={http:3} "
              f"marker={row['marker']!r} -> {verdict}")

    def process(row, role):
        iast = slp1_to_iast(row["headword"])
        row = dict(row, iast=iast, marker="")
        url = MM_URL.format(iast=urllib.parse.quote(iast))
        http, body, final = fetch(url)
        if http != 200:
            print(f"SKIP {iast} http={http} (no page; not counted)")
            return False
        section = mw_section(body)
        if not section:
            print(f"SKIP {iast} (page has no MW section; not counted)")
            return False
        found = fold(iast) in fold(section)
        receipt = {
            "site": SITE_MM, "url": final, "http": http,
            "page_sha256": hashlib.sha256(body.encode("utf-8", "replace")).hexdigest(),
            "page_bytes": len(body.encode("utf-8", "replace")),
            "dc_year": row["dc_year"], "dict": row["dict"], "L": row["L"],
            "headword": row["headword"], "iast": iast, "marker": "",
            "marker_found": found, "mw_section": True, "excerpt": section[:320],
        }
        emit(SITE_MM, row, role, http, "PRESENT" if found else "ABSENT", receipt)
        time.sleep(args.sleep)

        if row["headword"] in sd_merge:
            e = sd_merge[row["headword"]]
            shttp = int(e.get("http", 0))
            text = fold(e.get("text", ""))
            sfound = fold(iast) in text
            receipt = {"site": SITE_SD, "url": SD_URL.format(iast=iast), "http": shttp,
                       "page_sha256": hashlib.sha256(text.encode()).hexdigest(),
                       "marker": "", "marker_found": sfound, "excerpt": text[:280]}
            emit(SITE_SD, row, role, shttp, "PRESENT" if sfound else "ABSENT", receipt)
        else:
            receipt = dict(probe, headword=row["headword"], iast=iast, marker="")
            verdict = "BLOCKED-CF" if sd_blocked else "FETCH-FAIL"
            emit(SITE_SD, row, role, probe["http"], verdict, receipt)
        return True

    done_samples = done_controls = 0
    for row in sample_cands:
        if done_samples >= args.samples:
            break
        done_samples += process(row, "sample")
    for row in control_cands:
        if done_controls >= args.controls:
            break
        done_controls += process(row, "control")

    if args.edge_after:
        edge_rows = [r for r in rows if r["dict"] == "mw" and r["kind"] == "add"
                     and r["commit_date"] >= args.edge_after and r["headword"].isascii()]
        edge_rows.sort(key=lambda r: (r["commit_date"], r["L"]), reverse=True)
        seen_edge, edge_cands = set(), []
        for r in edge_rows:
            if r["headword"] in seen_edge:
                continue
            seen_edge.add(r["headword"])
            edge_cands.append(r)
        done_edge = 0
        for row in edge_cands:
            if done_edge >= args.edge_limit:
                break
            done_edge += process(row, "edge")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(lines), encoding="utf-8")
    (args.receipts_dir / "probe.json").write_text(
        json.dumps(probe, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    summary = collections.Counter((r["site"], r["role"], r["verdict"]) for r in receipts)
    for key, n in sorted(summary.items()):
        print("SUMMARY", key, n)
    print(f"wrote {args.out} ({len(lines) - 1} rows) and {args.receipts_dir}")


if __name__ == "__main__":
    main()
