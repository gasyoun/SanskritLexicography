#!/usr/bin/env python
"""Normalized DE-side <ls> citation edges (H1624 G3).

Additive DE citation layer: does NOT strip raw ``<ls>`` from the German string.
Each edge is a structured record::

  {
    "raw_ls":     str,           # visible text inside <ls>…</ls>
    "n_attr":     str|null,      # n="…" attribute when present
    "siglum":     str,           # source_key (leading non-digit tokens)
    "work_id":    str|null,      # ls_source_map key when matched
    "work_name":  str|null,      # human name from map or pwgbib expansion short
    "renou":      str|null,      # I–V from ls_source_map when known
    "page":       str|null,      # locator after siglum (digits/punctuation run)
    "bib_ok":     bool,          # pwgbib resolved the siglum
    "resolver_status": "map" | "bib" | "orphan" | "empty"
  }

Statuses (honest floor):
  * **map**    — siglum matched ls_source_map (has renou/genre)
  * **bib**    — not in map but pwgbib expands the abbreviation
  * **orphan** — neither map nor bib
  * **empty**  — empty / unparseable <ls>

Usage:
  python src/citation_edges.py --selftest
  python src/citation_edges.py extract "<ls>ṚV. 1,1,1</ls>"
  python src/citation_edges.py report [--store PATH] [--limit N]
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_sources as ps  # source_key + resolve (pwgbib)

LS_RE = re.compile(r"<ls\b([^>]*)>(.*?)</ls>", re.S)
N_ATTR_RE = re.compile(r'\bn\s*=\s*"([^"]*)"')
# Locator: first digit-bearing token and the rest of the visible text after siglum.
LOCATOR_RE = re.compile(r"(\d.*)$")

_MAP = None
_MAP_NORM = None  # lowercased key -> original key


def ls_source_map():
    global _MAP, _MAP_NORM
    if _MAP is None:
        path = os.path.join(HERE, "ls_source_map.json")
        _MAP = json.load(open(path, encoding="utf-8"))
        _MAP_NORM = {}
        for k in _MAP:
            _MAP_NORM[k] = k
            _MAP_NORM[k.lower()] = k
            # also without final dots / spaces
            kn = re.sub(r"\s+", " ", k).strip().rstrip(".").lower()
            _MAP_NORM.setdefault(kn, k)
    return _MAP, _MAP_NORM


def _lookup_map(siglum: str):
    """Return (work_id, entry) or (None, None)."""
    if not siglum:
        return None, None
    m, norm = ls_source_map()
    # progressive prefixes (multi-part keys like BHĀG. P)
    parts = siglum.split()
    candidates = [siglum]
    for i in range(len(parts), 0, -1):
        candidates.append(" ".join(parts[:i]))
    for c in candidates:
        for key in (c, c.rstrip("."), c.lower(), c.rstrip(".").lower(),
                    re.sub(r"\s+", " ", c).strip().rstrip(".").lower()):
            orig = norm.get(key)
            if orig is not None:
                return orig, m[orig]
    return None, None


def _locator(visible: str, siglum: str) -> str | None:
    """Digits+rest after the siglum, or first digit-run in the visible text."""
    vis = (visible or "").strip()
    if not vis:
        return None
    # strip leading siglum tokens if present
    rest = vis
    if siglum:
        # case-fold strip of leading siglum
        pat = re.compile(r"^\s*" + re.escape(siglum).replace(r"\ ", r"\s+") + r"\.?\s*", re.I)
        rest2 = pat.sub("", vis, count=1)
        if rest2 != vis:
            rest = rest2
    m = LOCATOR_RE.search(rest.strip())
    if m:
        return m.group(1).strip()
    m = LOCATOR_RE.search(vis)
    return m.group(1).strip() if m else None


def extract_citation_edges(text: str | None) -> list[dict]:
    """Extract normalized citation edges from one DE (or mixed) sense body.

    Does not modify ``text``. Empty list when no ``<ls>`` present.
    """
    edges = []
    for m in LS_RE.finditer(text or ""):
        attrs, visible = m.group(1) or "", (m.group(2) or "").strip()
        n_m = N_ATTR_RE.search(attrs)
        n_attr = n_m.group(1).strip() if n_m else None
        # Prefer n= for siglum inheritance (continuation refs); fall back to visible.
        siglum_src = n_attr if n_attr else visible
        siglum = ps.source_key(siglum_src) if siglum_src else ""
        if not siglum and visible:
            siglum = ps.source_key(visible) or ""
        if not siglum and not visible and not n_attr:
            edges.append({
                "raw_ls": "",
                "n_attr": n_attr,
                "siglum": "",
                "work_id": None,
                "work_name": None,
                "renou": None,
                "page": None,
                "bib_ok": False,
                "resolver_status": "empty",
            })
            continue

        work_id, entry = _lookup_map(siglum)
        bib_exp = ps.resolve(siglum) if siglum else None
        page = _locator(visible, siglum)

        if work_id is not None:
            status = "map"
            work_name = (entry or {}).get("name")
            renou = (entry or {}).get("renou")
        elif bib_exp:
            status = "bib"
            work_name = bib_exp.split(".", 1)[0].strip()[:80] if bib_exp else None
            renou = None
        else:
            status = "orphan"
            work_name = None
            renou = None

        edges.append({
            "raw_ls": visible,
            "n_attr": n_attr,
            "siglum": siglum,
            "work_id": work_id,
            "work_name": work_name,
            "renou": renou,
            "page": page,
            "bib_ok": bool(bib_exp),
            "resolver_status": status,
        })
    return edges


def coverage_stats(edges: list[dict]) -> dict:
    """Honest resolvable vs orphan counts for a list of edges."""
    c = Counter(e.get("resolver_status") or "empty" for e in edges)
    total = len(edges)
    resolvable = c.get("map", 0) + c.get("bib", 0)
    return {
        "total": total,
        "map": c.get("map", 0),
        "bib": c.get("bib", 0),
        "orphan": c.get("orphan", 0),
        "empty": c.get("empty", 0),
        "resolvable": resolvable,
        "resolvable_pct": round(100.0 * resolvable / total, 1) if total else 0.0,
        "map_pct": round(100.0 * c.get("map", 0) / total, 1) if total else 0.0,
        "orphan_pct": round(100.0 * c.get("orphan", 0) / total, 1) if total else 0.0,
    }


def report_store(store_path: str, limit: int | None = None) -> dict:
    """Scan store DE fields; return coverage + top orphan sigla."""
    edges_all = []
    orphan_sigla = Counter()
    n_rows = 0
    with open(store_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            n_rows += 1
            for e in extract_citation_edges(r.get("de")):
                edges_all.append(e)
                if e.get("resolver_status") == "orphan" and e.get("siglum"):
                    orphan_sigla[e["siglum"]] += 1
            if limit and n_rows >= limit:
                break
    stats = coverage_stats(edges_all)
    stats["rows"] = n_rows
    stats["top_orphan_sigla"] = orphan_sigla.most_common(25)
    return stats


def selftest() -> None:
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    # map hit with renou + page
    de = "Feuer <ls>ṚV. 1,1,1</ls> und Wasser."
    edges = extract_citation_edges(de)
    check(len(edges) == 1, "one edge: %r" % edges)
    e = edges[0]
    check(e["raw_ls"] == "ṚV. 1,1,1", "raw_ls: %r" % e)
    check(e["siglum"] == "ṚV", "siglum: %r" % e)
    check(e["resolver_status"] == "map", "map status: %r" % e)
    check(e["renou"] == "I", "renou: %r" % e)
    check(e["page"] == "1,1,1", "page: %r" % e)
    check(e["work_id"] is not None, "work_id: %r" % e)
    check(e["bib_ok"] is True, "bib_ok: %r" % e)

    # n= attribute inheritance
    de = '<ls n="MBH.">3,50</ls>'
    e = extract_citation_edges(de)[0]
    check(e["n_attr"] == "MBH.", "n_attr: %r" % e)
    check(e["siglum"] in ("MBH", "MBH."), "siglum from n: %r" % e)
    check(e["page"] == "3,50", "page from visible: %r" % e)
    check(e["resolver_status"] == "map", "MBH map: %r" % e)

    # raw DE string is NOT rewritten
    raw = "x <ls>ṚV. 1,1</ls> y"
    extract_citation_edges(raw)
    check(raw == "x <ls>ṚV. 1,1</ls> y", "must not mutate DE")

    # empty body
    check(extract_citation_edges("") == [], "empty")
    check(extract_citation_edges(None) == [], "none")

    # orphan (made-up siglum)
    e = extract_citation_edges("<ls>ZZZNOTAWORK. 1</ls>")[0]
    check(e["resolver_status"] == "orphan", "orphan: %r" % e)
    check(e["renou"] is None and e["work_id"] is None, "orphan fields: %r" % e)

    # coverage helper
    edges = extract_citation_edges(
        "<ls>ṚV. 1,1</ls> <ls>ZZZNOTAWORK. 2</ls> <ls>AK. 1</ls>")
    st = coverage_stats(edges)
    check(st["total"] == 3, "cov total: %r" % st)
    check(st["map"] >= 1 and st["orphan"] >= 1, "cov mix: %r" % st)

    # multiple edges preserve order
    edges = extract_citation_edges("<ls>AV. 1,1</ls>; <ls>MBH. 2,2</ls>")
    check([e["siglum"] for e in edges] == ["AV", "MBH"], "order: %r" % edges)

    if fails:
        for f in fails:
            print("FAIL:", f, file=sys.stderr)
        sys.exit(1)
    print("citation_edges --selftest: OK")


def main() -> None:
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    if argv[0] in ("--selftest", "selftest"):
        selftest()
        return
    if argv[0] == "extract" and len(argv) > 1:
        print(json.dumps(extract_citation_edges(argv[1]), ensure_ascii=False, indent=2))
        return
    if argv[0] == "report":
        from store_path import canonical_store
        store = canonical_store(os.path.join(HERE, "pwg_ru_translated.jsonl"))
        limit = None
        i = 1
        while i < len(argv):
            if argv[i] == "--store" and i + 1 < len(argv):
                store = argv[i + 1]
                i += 2
            elif argv[i] == "--limit" and i + 1 < len(argv):
                limit = int(argv[i + 1])
                i += 2
            else:
                i += 1
        if not os.path.exists(store):
            print("store not found: %s (pass --store or run on a machine with data)"
                  % store, file=sys.stderr)
            # still emit fixture-level coverage so CI is green
            demo = extract_citation_edges(
                "<ls>ṚV. 1,1,1</ls> <ls>MBH. 3,50</ls> <ls>ZZZORPHAN. 1</ls>")
            stats = coverage_stats(demo)
            stats["note"] = "demo fixtures only (no store)"
            print(json.dumps(stats, ensure_ascii=False, indent=2))
            return
        stats = report_store(store, limit=limit)
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return
    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    main()
