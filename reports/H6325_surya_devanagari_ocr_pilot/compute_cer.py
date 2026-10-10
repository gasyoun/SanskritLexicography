#!/usr/bin/env python3
"""H6325 per-plate CER comparison: surya vs baseline engines on the SAME plates.

Metrics per plate x engine:
  CER      = levenshtein(ref_norm, out_norm) / len(ref_norm)   (ordered text zones)
  DevRecall = |ref_dev_set ∩ out_dev_codepoints| / |ref_dev_set|  (set-based, tree letters included)

Normalization: NFC, whitespace collapsed to single spaces, stripped. Case kept.
Usage: compute_cer.py <reference.json> <out_root>  (out_root contains <engine>/<id>.txt)
Writes results.json + results.tsv next to itself.
"""
import json
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DEVRANGE = range(0x0900, 0x0980)  # Devanagari block


def norm(s: str) -> str:
    return " ".join(unicodedata.normalize("NFC", s).split())


def lev(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(ref: str, out: str) -> float:
    ref_n, out_n = norm(ref), norm(out)
    if not ref_n:
        return 0.0 if not out_n else 1.0
    return lev(ref_n, out_n) / len(ref_n)


def main() -> None:
    ref_path = Path(sys.argv[1])
    out_root = Path(sys.argv[2])
    here = Path(__file__).parent
    refs = json.loads(ref_path.read_text(encoding="utf-8"))["plates"]
    engines = sorted(d.name for d in out_root.iterdir() if d.is_dir() and d.name != "raw_json")

    results = {"engines": engines, "plates": []}
    for plate in refs:
        pid = plate["id"]
        ref_text = "\n".join(plate["ordered_text"])
        ref_dev = set(plate["dev_letters"])
        row = {"id": pid, "file": plate["file"], "cer": {}, "dev_recall": {}, "raw_len": {}}
        for eng in engines:
            f = out_root / eng / f"{pid}.txt"
            out = f.read_text(encoding="utf-8") if f.exists() else ""
            row["cer"][eng] = round(cer(ref_text, out), 4)
            out_dev = {ch for ch in unicodedata.normalize("NFC", out) if ord(ch) in DEVRANGE}
            row["dev_recall"][eng] = round(len(ref_dev & out_dev) / len(ref_dev), 4) if ref_dev else None
            row["raw_len"][eng] = len(out.strip())
        results["plates"].append(row)

    # means
    results["mean_cer"] = {
        eng: round(sum(r["cer"][eng] for r in results["plates"]) / len(results["plates"]), 4)
        for eng in engines
    }
    results["mean_dev_recall"] = {
        eng: round(
            sum(r["dev_recall"][eng] for r in results["plates"] if r["dev_recall"][eng] is not None)
            / max(1, sum(1 for r in results["plates"] if r["dev_recall"][eng] is not None)),
            4,
        )
        for eng in engines
    }
    (here / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    with (here / "results.tsv").open("w", encoding="utf-8") as fh:
        fh.write("plate\t" + "\t".join(f"CER:{e}" for e in engines) + "\t" + "\t".join(f"DevRec:{e}" for e in engines) + "\n")
        for r in results["plates"]:
            fh.write(r["id"] + "\t" + "\t".join(str(r["cer"][e]) for e in engines) + "\t" + "\t".join(str(r["dev_recall"][e]) for e in engines) + "\n")
    print(json.dumps(results["mean_cer"], ensure_ascii=False))
    print(json.dumps(results["mean_dev_recall"], ensure_ascii=False))


if __name__ == "__main__":
    main()
