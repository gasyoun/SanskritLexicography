#!/usr/bin/env python3
"""H7595 sweep v2 (read-only, multi-space)."""
import json, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GH = Path.home() / "Documents/GitHub"
SL_FIND = GH / "FINDINGS.md" if False else GH / "SanskritLexicography" / "FINDINGS.md"
UPR_FIND = GH / "Uprava" / "FINDINGS.md"
SHADOW = {80, 86, 87, 102, 103, 448, 449, 450, 451}

def sh(a):
    return subprocess.run(a, capture_output=True, text=True).stdout

def slug(t):
    s = re.sub(r"[^\w\- ]", "", t.lower())
    return s.replace(" ", "-")

def load_heads(path, pats):
    heads, anchors, renum = {}, {}, {}
    for i, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for pat in pats:
            m = pat.match(ln)
            if m:
                n = int(m.group(1))
                heads[n] = i
                anchors[n] = slug(ln.lstrip("# ").rstrip())
    return heads, anchors

def load_renum(path):
    renum = {}
    for ln in path.read_text(encoding="utf-8").splitlines():
        for m in re.finditer(r"Renumbered (?:from )?§(\d+)\s*(?:→|->)\s*§?(\d+)", ln):
            renum[int(m.group(1))] = int(m.group(2))
    return renum

sl_heads, sl_anchors = load_heads(SL_FIND, [re.compile(r"^#{1,3} §(\d+)\.")])
upr_heads, upr_anchors = load_heads(UPR_FIND, [
    re.compile(r"^## §(\d+) —"),
    re.compile(r"^[🔴🟠🟡🟢⚪🔵] \*\*§(\d+)\."),
])
sl_renum = load_renum(SL_FIND)
upr_renum = load_renum(UPR_FIND)
upr_max = max(upr_heads)
sl_max = max(sl_heads)

# --- citation classification --------------------------------------------------
def resolve_space(name, pre):
    """pre = up-to-40-char text before the word FINDINGS."""
    p = pre.strip()
    if re.search(r"(?i)\buprava\b|\bupr\b", p):
        return "Uprava"
    if re.search(r"(?i)\bsl\b|\bsanskritlexicography\b", p):
        return "SL"
    if name == "Uprava":
        return "Uprava"
    return "SL"

def classify(n, space, name):
    heads = upr_heads if space == "Uprava" else sl_heads
    other = sl_heads if space == "Uprava" else upr_heads
    renum = upr_renum if space == "Uprava" else sl_renum
    if n in heads:
        return "OK", None
    if n in other:
        return "FOREIGN-VALID", None
    if n in renum:
        return "STALE-RENUM", renum[n]
    if n in upr_renum:
        return "STALE-RENUM", upr_renum[n]
    if n in sl_renum:
        return "STALE-RENUM", sl_renum[n]
    if n == sl_max + 1 or n == upr_max + 1:
        return "NEXT-NUM", None
    return "STALE", None

# --- main sweep loop ----------------------------------------------------------
REPOS = [
    ("SL", GH / "SanskritLexicography", "origin/master"),
    ("Uprava", GH / "Uprava", "origin/main"),
    ("kosha", GH / "kosha", "origin/main"),
    ("csl-atlas", GH / "csl-atlas", "origin/main"),
]

stale = defaultdict(list)
toc_bad = []
counts = Counter()
per_num = defaultdict(Counter)
for name, path, ref in REPOS:
    out = sh(["git", "-C", str(path), "grep", "-nE", "§[0-9]+", ref, "--", "."])
    for raw in out.splitlines():
        if not raw.startswith(ref + ":"):
            continue
        rest = raw[len(ref) + 1:]
        m = re.match(r"(.+?):(\d+):(.*)", rest)
        if not m:
            continue
        f, lno, content = m.group(1), int(m.group(2)), m.group(3)
        is_data = f.endswith((".tsv", ".json", ".jsonl", ".csv"))
        is_hist = (f.startswith("handoffs/") or "CHANGELOG" in f
                   or "ARCHIVE" in f or f == "DANGER_FACTS.md")
        for fm in re.finditer(r"(?i)(?P<pre>[\w. -]{0,40})FINDINGS\s+§(?P<n>\d+)", content):
            n = int(fm.group("n"))
            counts[("CITES", name)] += 1
            space = resolve_space(name, fm.group("pre"))
            cls, rep = classify(n, space, name)
            counts[(cls, name)] += 1
            if cls in ("STALE", "STALE-RENUM", "NEXT-NUM"):
                tag = ("DATA" if is_data else "HIST" if is_hist else "PROSE")
                tag = ("DATA" if is_data else "HIST" if is_hist else "PROSE")
                per_num[(cls, tag)][n] += 1
                stale[tag].append([name, f, lno, n, rep, space, content.strip()[:150]])
            elif cls == "FOREIGN-VALID":
                counts[("FOREIGN", name)] += 1
        if name == "SL" and f == "FINDINGS.md":
            for am in re.finditer(r"\]\(#([0-9][0-9a-z-]*)\)", content):
                frag = am.group(1)
                fn = re.match(r"(\d+)-", frag)
                if fn and int(fn.group(1)) in sl_anchors and frag != sl_anchors[int(fn.group(1))]:
                    toc_bad.append([f, lno, int(fn.group(1)), frag, sl_anchors[int(fn.group(1))]])
                    counts[("TOC-ANCHOR", name)] += 1
print(json.dumps({
    "heads": {"SL": len(sl_heads), "Uprava": len(upr_heads)},
    "max": {"SL": sl_max, "Uprava": upr_max},
    "renum_SL": {str(k): v for k, v in sl_renum.items()},
    "renum_Uprava": {str(k): v for k, v in upr_renum.items()},
    "counts": {f"{k[0]}|{k[1]}": v for k, v in counts.items()},
    "per_num": {f"{k[0]}|{k[1]}": dict(v.most_common(12)) for k, v in per_num.items()},
    "toc_bad_total": len(toc_bad),
    "toc_bad": toc_bad[:30],
    "stale_rows": {k: v[:400] for k, v in stale.items()},
}, ensure_ascii=False, indent=1))
