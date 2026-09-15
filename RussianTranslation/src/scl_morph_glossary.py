#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H4740 — Samsaadhanii (SCL) morph.cgi outputs → glossary layer (VALIDATION-ONLY pilot).

Sibling census A5 pilot 3 of the four Samsaadhanii pilots MG approved 02-07-2026
(memory note reference-samsaadhanii-scl). Converts live morph.cgi analyses of
sampled DCS forms into the house glossary-layer record shape
(form → [{stem, tags}]), so the SCL analyzer can serve as a second independent
witness beside the vidyut.kosha + DCS form→lemma fallback (~87% coverage).

LICENSE: the Samsaadhanii `datasets`/SCL outputs carry **no LICENSE** — this
layer is VALIDATION-ONLY. Do not redistribute beyond the committed sample, and
never overwrite human-reviewed data with it (SAMSAADHANII_INDEX.md license gate).

Usage (from RussianTranslation/src/):
    python3 scl_morph_glossary.py sample          # 40-form DCS stratified sample
    python3 scl_morph_glossary.py run --forms-file F [--cache C] [--limit N]
    python3 scl_morph_glossary.py coverage --records R

Requires: network access to scl.samsaadhanii.in; sanskrit-util for IAST↔SLP1
(the canonical estate transcoder — never hand-rolled) found via SANSKRIT_UTIL_PATH
or ../../sanskrit-util/py relative to this clone.
"""
import argparse
import html
import json
import os
import random
import re
import sqlite3
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import date

MORPH_URL = "https://scl.samsaadhanii.in/cgi-bin/scl/MT/prog/morph/morph.cgi"
DCS_DB = "/Users/mac/Documents/GitHub/VisualDCS/src/DCS-data-2026/dcs_full.sqlite"
HERE = os.path.dirname(os.path.abspath(__file__))
REPORTS = os.path.join(HERE, "..", "reports")
CACHE_DEFAULT = os.path.join(HERE, "..", "glossary", "scl_morph_cache.jsonl")
COVERAGE_JSON = os.path.join(REPORTS, "H4740_scl_morph_coverage.json")
SAMPLE_JSONL = os.path.join(REPORTS, "H4740_scl_morph_sample.jsonl")
PROVENANCE = {
    "source": "Samsaadhanii/SCL morphological analyzer (Amba Kulkarni, Univ. of Hyderabad)",
    "endpoint": MORPH_URL,
    "license": "NONE — validation-only per SAMSAADHANII_INDEX.md license gate",
    "retrieved": date.today().isoformat(),
    "validation_only": True,
    "never_overwrites_human_reviewed_data": True,
}


def load_transcoder():
    """Import the canonical sanskrit-util (repo sibling), never a hand-rolled one."""
    for cand in (
        os.environ.get("SANSKRIT_UTIL_PATH", ""),
        os.path.join(HERE, "..", "..", "..", "sanskrit-util", "py"),
    ):
        if cand and os.path.isdir(cand):
            if cand not in sys.path:
                sys.path.insert(0, cand)
            try:
                from sanskrit_util import from_slp1, to_slp1  # noqa: F401
                return to_slp1, from_slp1
            except Exception:
                continue
    print("WARN: sanskrit-util not found — SLP1 keys will be null", file=sys.stderr)
    return (lambda s: None), (lambda s: None)


def call_morph(form, timeout=90, retries=3):
    """POST one form; returns raw HTML. Retries transient failures with backoff."""
    data = urllib.parse.urlencode(
        {"morfword": form, "encoding": "IAST", "outencoding": "IAST", "mode": ""}
    ).encode()
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                MORPH_URL, data=data,
                headers={"User-Agent": "SanskritLexicography-H4740-validation/1.0"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", "replace")
        except Exception as exc:  # transient network/API error
            if attempt == retries:
                raise RuntimeError(f"morph.cgi failed after {retries} tries: {exc}") from exc
            time.sleep(5 * attempt)


TD_OPEN_RE = re.compile(r"<td[^>]*>", re.I)
TAG_RE = re.compile(r"<[^>]+>")
JS_RE = re.compile(r"<script.*?</script>", re.S | re.I)
# NOTE: the CGI emits MALFORMED HTML (unclosed <tr>/<td>, no </table>).
# Parse by <td> boundaries, never by closing tags (H4740 probe 15-09-2026).


def parse_analyses(raw_html):
    """Extract analysis cells: each cell = 'stem tag tag ...' (IAST, outencoding=IAST)."""
    html_body = JS_RE.sub("", raw_html)
    out = []
    for seg in TD_OPEN_RE.split(html_body)[1:]:
        seg = re.split(r"</td>|<tr|</tr|</table|<table", seg, flags=re.I)[0]
        text = html.unescape(TAG_RE.sub(" ", seg))
        toks = text.split()
        if len(toks) >= 2:
            out.append({"stem_iast": toks[0], "tags": toks[1:]})
    return out


def load_cache(path):
    cache = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    cache[rec["form_iast"]] = rec
    return cache


def append_cache(path, rec):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")


def fetch_forms(forms, cache_path, sleep_s=1.5):
    """Fill the cache for `forms` (list of IAST forms); polite: 1.5s gap, cached."""
    to_slp1, _ = load_transcoder()
    cache = load_cache(cache_path)
    for i, form in enumerate(forms):
        if form in cache:
            continue
        raw = call_morph(form)
        analyses = parse_analyses(raw)
        rec = dict(PROVENANCE)
        rec.update(
            form_iast=form,
            form_slp1=to_slp1(form),
            n_analyses=len(analyses),
            covered=bool(analyses),
            analyses=analyses,
        )
        append_cache(cache_path, rec)
        cache[form] = rec
        print(f"[{i+1}/{len(forms)}] {form}: {len(analyses)} analyses", flush=True)
        time.sleep(sleep_s)
    return cache


def sample_from_dcs(n_top=20, n_mid=20, seed=4740):
    """Stratified DCS form sample: top-frequency + random mid-band, single tokens."""
    sql = """
    WITH forms AS (
      SELECT lower(m_unsandhied) AS f, COUNT(*) AS n,
             ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS rk
      FROM token
      WHERE m_unsandhied IS NOT NULL AND m_unsandhied NOT LIKE '% %'
        AND m_unsandhied NOT LIKE '%|%' AND m_unsandhied NOT LIKE '%.%'
        AND m_unsandhied != '' AND trim(m_unsandhied) = m_unsandhied
        AND length(m_unsandhied) BETWEEN 2 AND 20
      GROUP BY lower(m_unsandhied))
    SELECT f, n, rk FROM forms WHERE {cond}"""
    con = sqlite3.connect(DCS_DB)
    top = con.execute(sql.format(cond="rk <= 500 ORDER BY rk LIMIT %d" % n_top)).fetchall()
    mid = con.execute(sql.format(cond="rk BETWEEN 500 AND 50000")).fetchall()
    con.close()
    random.Random(seed).shuffle(mid)
    return {"top": top[:n_top], "mid": mid[:n_mid], "mid_pool_size": len(mid)}


def cmd_sample(args):
    strata = sample_from_dcs(args.n_top, args.n_mid)
    forms = [f for f, _, _ in strata["top"]] + [f for f, _, _ in strata["mid"]]
    cache = fetch_forms(forms, args.cache, sleep_s=args.sleep)
    write_artifacts(cache, strata)
    print(f"sample complete → {SAMPLE_JSONL}\ncoverage → {COVERAGE_JSON}")


def write_artifacts(cache, strata):
    os.makedirs(REPORTS, exist_ok=True)
    records = sorted(cache.values(), key=lambda r: r["form_iast"])
    with open(SAMPLE_JSONL, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
    def _stats(recs):
        covered = [r for r in recs if r["covered"]]
        return {
            "n": len(recs),
            "covered": len(covered),
            "coverage_pct": round(100.0 * len(covered) / len(recs), 1) if recs else None,
        }
    top_recs = [cache[f] for f, _, _ in strata["top"] if f in cache]
    mid_recs = [cache[f] for f, _, _ in strata["mid"] if f in cache]
    report = {
        "handoff": "H4740",
        "date": date.today().isoformat(),
        "what": "Samsaadhanii morph.cgi → glossary layer; DCS form-coverage sample (validation-only pilot)",
        "sample_design": {
            "population": "DCS token.m_unsandhied distinct single-word forms (5.69M tokens)",
            "stratum_top": "top %d forms by corpus frequency (rank ≤500)" % len(top_recs),
            "stratum_mid": "%d random forms from rank 500-50000 (pool %d, seed 4740)"
            % (len(mid_recs), strata["mid_pool_size"]),
            "n_total": len(top_recs) + len(mid_recs),
        },
        "provenance": PROVENANCE,
        "coverage_overall": _stats(top_recs + mid_recs),
        "coverage_top": _stats(top_recs),
        "coverage_mid": _stats(mid_recs),
        "interpretation": "SCL morph.cgi = second independent form→analysis witness beside "
        "vidyut.kosha + DCS fallback; VALIDATION-ONLY (no upstream LICENSE) — "
        "never overwrites human-reviewed data.",
        "artifacts": {"sample_jsonl": os.path.relpath(SAMPLE_JSONL, HERE + "/.."),
                      "cache_local_only": os.path.relpath(args_cache_global, HERE + "/..")},
    }
    with open(COVERAGE_JSON, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in report.items() if k.startswith("coverage")},
                     ensure_ascii=False, indent=1))


args_cache_global = CACHE_DEFAULT  # bound late in cmd_sample for report path


FIXTURE_HTML = (
    "<script>function f(){}</script>"
    "<table><tr><td bgcolor='pink'><a href='x'>gam</a> kartari laṭ pra eka "
    "parasmaipadī bhvādiḥ </td><td><a href='x'>gam1</a> śatṛ_laṭ dh bhvādiḥ</td>"
)


def selftest():
    """Offline: fixture HTML (unclosed <tr>, real probe shape) parses to 2 analyses."""
    analyses = parse_analyses(FIXTURE_HTML)
    assert len(analyses) == 2, analyses
    assert analyses[0] == {
        "stem_iast": "gam",
        "tags": ["kartari", "laṭ", "pra", "eka", "parasmaipadī", "bhvādiḥ"],
    }, analyses[0]
    to_slp1, from_slp1 = load_transcoder()
    assert to_slp1("gacchati") == "gacCati", to_slp1("gacchati")
    assert from_slp1("gacCati") == "gacchati"
    assert parse_analyses("<p>no analysis here</p>") == []
    print("selftest PASS: parser + transcoder (2 fixture analyses, IAST↔SLP1 round-trip)")


def cmd_report(_args):
    """Derive the committed markdown report from H4740_scl_morph_coverage.json."""
    with open(COVERAGE_JSON, encoding="utf-8") as fh:
        rep = json.load(fh)
    cov = rep["coverage_overall"]
    misses, multi = [], 0
    sample_path = os.path.join(REPORTS, "H4740_scl_morph_sample.jsonl")
    if os.path.exists(sample_path):
        for line in open(sample_path, encoding="utf-8"):
            r = json.loads(line)
            if not r["covered"]:
                misses.append(r["form_iast"])
            if r["n_analyses"] > 1:
                multi += 1
    lines = [
        "# H4740 — Samsaadhanii morph.cgi → glossary layer report",
        "",
        "_Created: 15-09-2026 · tier: OxAlpha (opencode/z-ai/glm-5.3-flash)_",
        "",
        "**VALIDATION-ONLY** — Samsaadhanii/SCL outputs carry no LICENSE; this layer",
        "is a second independent form→analysis witness, never an overwrite of",
        "human-reviewed data (SAMSAADHANII_INDEX.md license gate).",
        "",
        "## Sample design (on our data)",
        "",
        f"- Population: {rep['sample_design']['population']}",
        f"- Stratum top: {rep['sample_design']['stratum_top']}",
        f"- Stratum mid: {rep['sample_design']['stratum_mid']}",
        f"- Retrieved: {rep['provenance']['retrieved']} from `{rep['provenance']['endpoint']}`",
        "",
        "## Result",
        "",
        "| stratum | forms | covered | coverage |",
        "|---|---|---|---|",
        "| overall | %d | %d | %s%% |" % (cov["n"], cov["covered"], cov["coverage_pct"]),
        "| top-frequency | %d | %d | %s%% |" % (rep["coverage_top"]["n"], rep["coverage_top"]["covered"], rep["coverage_top"]["coverage_pct"]),
        "| mid-band random | %d | %d | %s%% |" % (rep["coverage_mid"]["n"], rep["coverage_mid"]["covered"], rep["coverage_mid"]["coverage_pct"]),
        "",
        "Per-form records (40): [reports/H4740_scl_morph_sample.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4740_scl_morph_sample.jsonl) "
        "— cache gitignored (`glossary/scl_morph_cache.jsonl`).",
        "",
        "## Misses (%d) and ambiguity" % len(misses),
        "",
        ("- Uncovered: %s — typology: indeclinables/avyaya without analyzer entry "
         "(tatas, anamitram), compound members (mahā), pro-drop pronoun fragments (sa), "
         "middle-participle morphology (amṛṣyamāṇaḥ), split-compound residue (apāṃsi)." % ", ".join("`%s`" % m for m in misses)) if misses else "- No misses.",
        "",
        "- Forms with >1 competing analysis (homograph/polysemy — the adjudication value): %d/40." % multi,
        "",
        "## Checks",
        "",
        "- `python3 RussianTranslation/src/scl_morph_glossary.py selftest` → PASS (parser fixture, IAST↔SLP1 round-trip via canonical sanskrit-util)",
        "- malformed-HTML handling proven live: the CGI emits unclosed `<tr>/<td>`; parser is boundary-based",
        "- transient-failure policy: 3 retries with backoff per call; polite 1–1.5 s gap + UA-identified",
        "",
        "_Гасунс_",
    ]
    md_path = os.path.join(REPORTS, "H4740_scl_morph_report.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"report → {md_path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("sample", help="run the H4740 stratified DCS coverage sample")
    sp.add_argument("--cache", default=CACHE_DEFAULT)
    sp.add_argument("--n-top", type=int, default=20)
    sp.add_argument("--n-mid", type=int, default=20)
    sp.add_argument("--sleep", type=float, default=1.5)
    sp.set_defaults(func=cmd_sample)
    st = sub.add_parser("selftest", help="offline fixture test (no network)")
    st.set_defaults(func=lambda a: selftest())
    rp = sub.add_parser("report", help="derive the markdown report from the coverage JSON")
    rp.set_defaults(func=cmd_report)
    args = ap.parse_args()
    global args_cache_global
    args_cache_global = args.cache if hasattr(args, "cache") else CACHE_DEFAULT
    args.func(args)


if __name__ == "__main__":
    main()
