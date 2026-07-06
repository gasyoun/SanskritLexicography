#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""synth_score.py — score the H180 Arm-A vs Arm-B bake-off on the machine-checkable
axes (SYNTHESIS_PILOT_10.md). The human axes (coherence, fluency) go to the
deferred 4th HTML sheet; this computes the rest against the layered store.

For each of the 10 pilot words:
  * SOURCE set  = every <ls> citation across all the word's sub-cards (the store).
  * Arm A       = the after-translation re-glue (build_reglue.py) — lossless by
                  construction, so its citation set == SOURCE (fidelity 1.0,
                  hallucination 0). Reported as the control.
  * Arm B       = the synthesized German entry (synth_outputs/<key1>.de_synth.txt).
                  fidelity        = |B ∩ SOURCE| / |SOURCE|   (senses/citations kept)
                  hallucination   = |B \\ SOURCE|              (citations NOT in source — MUST be 0)
                  redundancy      = duplicate <ls> citations within B
                  provenance-loss = inherent to B (layers merged) — flagged, not scored here

Citations are compared on a normalized <ls> siglum+locus token so trivial
whitespace/markup differences don't count as loss or hallucination.

NO model call — pure comparison. Reads only local files.

Inputs : src/pwg_ru_translated.jsonl, pwg_ru/reglue/synth_outputs/<key1>.de_synth.txt
Output : pwg_ru/reglue/synth_outputs/ARMB_SCORES.tsv  (+ printed table)

Run: python src/synth_score.py
"""
import sys, os, io, json, re, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")
OUTDIR = os.path.join(ROOT, "pwg_ru", "reglue", "synth_outputs")
SCORES = os.path.join(OUTDIR, "ARMB_SCORES.tsv")

PILOT10 = ["dah", "As", "car", "siD", "viS", "Ap", "DA", "Cid", "gA", "Sam"]
LS_RE = re.compile(r"<ls\b[^>]*>(.*?)</ls>", re.S)
WS_RE = re.compile(r"\s+")


def norm_ls(cit):
    """Normalize an <ls> body to a comparable token (collapse whitespace, drop
    trailing punctuation)."""
    t = WS_RE.sub(" ", cit).strip().strip(".,;: ")
    return t


def ls_multiset(text):
    return collections.Counter(norm_ls(c) for c in LS_RE.findall(text) if norm_ls(c))


def load_source():
    src = collections.defaultdict(str)
    for line in io.open(STORE, encoding="utf-8"):
        line = line.strip()
        if line:
            d = json.loads(line)
            if d["key1"] in PILOT10:
                src[d["key1"]] += " " + d.get("de", "")
    return src


def main():
    src = load_source()
    rows = []
    print(f"{'key1':6s} {'src_cit':>7s} {'B_cit':>6s} {'kept':>5s} {'fidelity':>8s} "
          f"{'halluc':>6s} {'redund':>6s}")
    for key1 in PILOT10:
        source_ms = ls_multiset(src.get(key1, ""))
        source_set = set(source_ms)
        p = os.path.join(OUTDIR, key1 + ".de_synth.txt")
        if not os.path.exists(p):
            print(f"{key1:6s}   (Arm-B synthesis not found — agent pending?)")
            rows.append((key1, len(source_set), "-", "-", "-", "-", "-"))
            continue
        b_text = io.open(p, encoding="utf-8").read()
        b_ms = ls_multiset(b_text)
        b_set = set(b_ms)
        kept = len(b_set & source_set)
        fidelity = kept / len(source_set) if source_set else 0.0
        halluc = len(b_set - source_set)
        redund = sum(v - 1 for v in b_ms.values() if v > 1)
        rows.append((key1, len(source_set), len(b_set), kept,
                     round(fidelity, 3), halluc, redund))
        print(f"{key1:6s} {len(source_set):7d} {len(b_set):6d} {kept:5d} "
              f"{fidelity:8.3f} {halluc:6d} {redund:6d}")

    with io.open(SCORES, "w", encoding="utf-8") as fh:
        fh.write("key1\tsource_citations\tB_citations\tkept\tfidelity\thallucination\tredundancy\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {SCORES}")
    print("NOTE: Arm A (re-glue) is lossless by construction — fidelity 1.0, "
          "hallucination 0 (citations copied verbatim). Coherence + fluency are the "
          "human axes (deferred 4th HTML sheet).")


if __name__ == "__main__":
    main()
