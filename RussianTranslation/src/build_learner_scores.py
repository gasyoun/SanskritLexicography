#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_learner_scores.py — Deliverable 4 of H180 (LEARNER_APPARATUS_SPEC.md).

Score every PWG headword by descendant-dictionary retention, so the descendants
can VOTE on which senses a Russian learner needs. Three axes (MG's correction):

  learner_score   = Σ w_i · present_i   over the SMALL Russian student tier
                    (Kochergina weighted 1.0 — "above all")   <- THE learner signal
  support_score   = mean present() over the MEDIUM scholarly single-language tier
  scholarly_score = mean present() over the BIG abridged-scholarly tier
                    (reported, NEVER gates admission — PW/MW/AP aren't for students)

All joins run through slp1_norm() (anusvara + homonym-strip), per the measured
edition-delta caveat, so the learner signal doesn't inherit OCR/citation noise.

NO re-translation, NO workflow call. Every dict is already on disk — CONSUME,
don't re-parse the sources: the five student dicts are the pre-extracted jsonls,
the MEDIUM/BIG tiers are csl-orig <k1> keys.

Inputs  : ../../csl-orig/v02/pwg/pwg.txt        (PWG headword universe, <k1>)
          src/{koch,kow,kna,smirnov,fri}.jsonl  (SMALL Russian student tier)
          ../../csl-orig/v02/{cae,ccs,md}        (MEDIUM)
          ../../csl-orig/v02/{pw,mw,ap}          (BIG)
Output  : pwg_ru/learner_scores.tsv
          pwg_ru/edition_deltas.tsv             (AP90->AP, MW72->MW, normalized)

Run: python src/build_learner_scores.py
"""
import sys, os, io, json, re

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slp1_norm import slp1_norm  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # RussianTranslation/
CSL = os.path.normpath(os.path.join(ROOT, "..", "..", "csl-orig", "v02"))
OUT_TSV = os.path.join(ROOT, "pwg_ru", "learner_scores.tsv")
OUT_DELTA = os.path.join(ROOT, "pwg_ru", "edition_deltas.tsv")

K1_RE = re.compile(r"<k1>(.*?)<")

# SMALL — Russian student tier = THE learner signal (weights from the spec)
STUDENT = [("KCH", "koch", 1.00), ("KOW", "kow", 0.70), ("KNA", "kna", 0.70),
           ("SMI", "smirnov", 0.60), ("FRI", "fri", 0.50)]
MEDIUM = ["cae", "ccs", "md"]        # scholarly single-language
BIG = ["pw", "mw", "ap"]             # abridged-but-scholarly (reported, non-gating)


def csl_keys(dictcode):
    """Normalized <k1> key set for a csl-orig dictionary."""
    path = os.path.join(CSL, dictcode, dictcode + ".txt")
    keys = set()
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            m = K1_RE.search(line)
            if m:
                k = slp1_norm(m.group(1))
                if k:
                    keys.add(k)
    return keys


def student_keys(stem):
    """Normalized slp1 key set for an extracted student jsonl."""
    path = os.path.join(HERE, stem + ".jsonl")
    keys = set()
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            k = slp1_norm(json.loads(line).get("slp1", ""))
            if k:
                keys.add(k)
    return keys


def main():
    print("loading PWG headword universe ...")
    pwg = sorted(csl_keys("pwg"))
    print(f"  PWG headwords (normalized): {len(pwg)}")

    print("loading SMALL Russian student tier ...")
    student = {}
    for code, stem, w in STUDENT:
        student[code] = (w, student_keys(stem))
        print(f"  {code:4s} w={w:.2f} keys={len(student[code][1])}")

    print("loading MEDIUM + BIG csl-orig tiers ...")
    medium = {c.upper(): csl_keys(c) for c in MEDIUM}
    big = {c.upper(): csl_keys(c) for c in BIG}
    for c, s in list(medium.items()) + list(big.items()):
        print(f"  {c:4s} keys={len(s)}")

    wsum = sum(w for _, _, w in STUDENT)
    n_med, n_big = len(MEDIUM), len(BIG)

    rows = []
    for k in pwg:
        present = [code for code, (w, ks) in student.items() if k in ks]
        learner = sum(w for code, (w, ks) in student.items() if k in ks)
        support = sum(1 for ks in medium.values() if k in ks) / n_med
        scholar = sum(1 for ks in big.values() if k in ks) / n_big
        med_present = [c for c, ks in medium.items() if k in ks]
        big_present = [c for c, ks in big.items() if k in ks]
        rows.append((k, round(learner, 3), round(learner / wsum, 3),
                     round(support, 3), round(scholar, 3),
                     ",".join(present + med_present + big_present) or "-"))

    rows.sort(key=lambda r: (-r[1], r[0]))
    with io.open(OUT_TSV, "w", encoding="utf-8") as fh:
        fh.write("key1\tlearner_score\tlearner_norm\tsupport_score\tscholarly_score\tdicts_present\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")

    # summary buckets
    kept_any = sum(1 for r in rows if r[1] > 0)
    kept_koch = sum(1 for r in rows if "KCH" in r[5])
    kept_2plus = sum(1 for r in rows
                     if sum(c in r[5] for c in ("KCH", "KOW", "KNA", "SMI", "FRI")) >= 2)
    print(f"\nPWG headwords: {len(rows)}")
    print(f"  learner-core (>=1 Russian dict) : {kept_any} ({100*kept_any//len(rows)}%)")
    print(f"  kept by Kochergina              : {kept_koch}")
    print(f"  kept by >=2 Russian dicts        : {kept_2plus}")
    print(f"wrote {OUT_TSV}")

    edition_deltas()


def edition_deltas():
    """AP90->AP and MW72->MW headword add/keep/drop, normalized (§3)."""
    print("\ncomputing edition deltas (normalized) ...")
    with io.open(OUT_DELTA, "w", encoding="utf-8") as fh:
        fh.write("pair\told_uniq\tnew_uniq\tkept\tadded\tdropped\n")
        for old, new in [("ap90", "ap"), ("mw72", "mw")]:
            o, n = csl_keys(old), csl_keys(new)
            kept = len(o & n)
            added = len(n - o)
            dropped = len(o - n)
            fh.write(f"{old.upper()}->{new.upper()}\t{len(o)}\t{len(n)}\t{kept}\t{added}\t{dropped}\n")
            print(f"  {old.upper()}->{new.upper()}: kept={kept} added={added} dropped={dropped}")
    print(f"wrote {OUT_DELTA}")


if __name__ == "__main__":
    main()
