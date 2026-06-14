#!/usr/bin/env python
"""Build the pwg_ru corpus-gate dictionary sources from SamudraManthanam.

Reads the digitized Sanskrit->Russian dictionaries that ship inside the
SamudraManthanam parallel-corpus tool (sibling repo) and writes one normalized,
SLP1-keyed JSONL per source into this directory.

These outputs are DATA and are .gitignored (some sources are modern/copyright);
this script + README are the committed, regenerable contract.

Usage:  python build_src.py [path-to-SamudraManthanam]
Output: koch.jsonl kow.jsonl kna.jsonl fri.jsonl smirnov.jsonl
        each line = {"source","slp1","iast","gloss"}
"""
import json, os, sys, re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

DEFAULT_SM = r"C:\Users\user\Documents\GitHub\SamudraManthanam"
SM = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SM
JSONL = os.path.join(SM, "web", "corpus_builder", "jsonl")
OUT = os.path.dirname(os.path.abspath(__file__))

# source slug in SamudraManthanam  ->  our gate code
SOURCES = [
    ("kochergina",      "koch"),     # Кочергина 1987 (modern, primary independent)
    ("kossovich",       "kow"),      # Коссович 1854 (KOW, WIL-seeded human PWG->RU reference)
    ("knauer",          "kna"),      # Кнауэр 1908 (KNA, independent)
    ("frish",           "fri"),      # Фриш 1956 (FRI, independent)
    ("slovar-smirnova", "smirnov"),  # Смирнов Симфонический словарь (independent)
]

# IAST -> SLP1 (used only when the source has no slp1 key of its own).
_DIGRAPH = [("kh","K"),("gh","G"),("ch","C"),("jh","J"),("ṭh","W"),("ḍh","Q"),
            ("th","T"),("dh","D"),("ph","P"),("bh","B")]
_SINGLE = [("ā","A"),("ī","I"),("ū","U"),("ṝ","F"),("ṛ","f"),("ḹ","X"),("ḷ","x"),
           ("ṅ","N"),("ñ","Y"),("ṭ","w"),("ḍ","q"),("ṇ","R"),
           ("ś","S"),("ṣ","z"),("ḥ","H"),("ṃ","M"),("ṁ","M")]

def iast_to_slp1(s):
    if not s:
        return ""
    s = s.strip().strip("/").strip().strip("-").strip()
    s = re.sub(r"[̀-̏॑-॔]", "", s)  # drop combining accents
    for a, b in _DIGRAPH:
        s = s.replace(a, b)
    for a, b in _SINGLE:
        s = s.replace(a, b)
    return s

def field(text, i):
    parts = (text or "").split("\t")
    return parts[i].strip().strip("/").strip() if len(parts) > i else ""

def gloss_after(text, n):
    parts = (text or "").split("\t")
    return " ".join(p.strip() for p in parts[n:]).strip()

def extract(slug, code):
    path = os.path.join(JSONL, slug + ".jsonl")
    out_path = os.path.join(OUT, code + ".jsonl")
    n_in = n_out = n_nokey = 0
    with open(path, encoding="utf-8") as f, open(out_path, "w", encoding="utf-8", newline="") as o:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            if e.get("deleted"):
                continue
            n_in += 1
            slp1 = (e.get("slp1") or "").strip()
            iast = ((e.get("forms") or {}).get("iast") or "").strip()
            text = e.get("text") or ""
            if code in ("fri", "smirnov"):
                # tab-structured: dev / iast / (hk) / cyrillic / gloss...
                iast = iast or field(text, 1)
                gloss = gloss_after(text, 4) or gloss_after(text, 1)
            else:
                gloss = text
            if not slp1 and iast:
                slp1 = iast_to_slp1(iast)
            if not slp1:
                n_nokey += 1
                continue
            o.write(json.dumps({"source": code, "slp1": slp1, "iast": iast,
                                "gloss": gloss}, ensure_ascii=False) + "\n")
            n_out += 1
    print(f"{code:8s} <- {slug:18s} in={n_in:6d} out={n_out:6d} no-key={n_nokey}")
    return n_out

if __name__ == "__main__":
    if not os.path.isdir(JSONL):
        sys.exit(f"SamudraManthanam jsonl dir not found: {JSONL}")
    total = sum(extract(slug, code) for slug, code in SOURCES)
    print(f"TOTAL keyed entries: {total}")
