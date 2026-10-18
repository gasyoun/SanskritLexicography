#!/usr/bin/env python3
"""H4747 — Indische Sprueche x DCS sent_id attestation layer.

Binds Böhtlingk Indische Sprüche per-saying records (IndischeSprueche/data/
indische_sprueche.jsonl, 2nd ed.) to DCS corpus loci by normalized text match.

Key design decisions (house prior art, do not re-derive):
- DCS `sent_id` is NOT unique within a chapter (FINDINGS §9 / DEAD_ENDS §6) —
  loci are keyed on the synthetic `sentence.id` PK; `sent_id` travels as a label.
- Böhtlingk prints continuous sandhi; DCS `text_sandhied` keeps annotator-chosen
  token boundaries ("jagan nujjahāra" vs "jagant ujjahāra"). Comparison therefore
  strips ALL spacing/punctuation and compares continuous letter streams.
- DCS stores a whole verse (or each pada) as its own sentence; matching is done
  pada-by-pada (split on `/` and `|`), plus a whole-verse exact class.
- Candidate recall: selective index of long normalized words (>=7 chars, capped
  40 sentence ids per form) built from sentence text; probe = up to 3 longest
  pada words; verify = continuous-stream substring test.

Usage:
  python3 h4747_build_dcs_loci.py --dcs-db <dcs_full.sqlite> \
      --out-dir ../attestation [--limit N] [--selftest]

Defaults: --dcs-db ../../VisualDCS/src/DCS-data-2026/dcs_full.sqlite relative to
the repo root's SIBLING VisualDCS checkout. The script refuses 0-byte/decoy or
small files (danger fact: VisualDCS/src/dcs_full.sqlite is a 0-byte decoy).
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date

SAYINGS_JSONL = os.path.join(os.path.dirname(__file__), "..", "data", "indische_sprueche.jsonl")
LETTERS = re.compile(r"[^a-zāīūṛṝḷḹñṅṇśṣṭḍḥṃ]+")
MIN_DB_BYTES = 500_000_000  # real dcs_full.sqlite is ~921 MB
MAX_LOCI_PER_PADA = 10
LONG_WORD = 7


def normalize(text: str) -> str:
    """Lowercase, fold ṁ→ṃ, drop everything that is not a letter."""
    return LETTERS.sub("", text.lower().replace("ṁ", "ṃ"))


def pada_split(iast: str) -> list[str]:
    """Split a saying's IAST into padas on / and | markers."""
    return [p for p in (s.strip() for s in re.split(r"[/|]+", iast)) if p]


def pada_words(pada: str) -> list[str]:
    """Normalized words of a pada (probe candidates)."""
    return [w for w in (normalize(t) for t in pada.split()) if len(w) >= LONG_WORD]


def selftest() -> None:
    assert normalize("Udyamena hi sidhyanti, kāryāṇi!") == "udyamenahisidhyantikāryāṇi"
    assert normalize("saṁsāra") == normalize("saṃsāra") == "saṃsāra"
    assert normalize("jagan nujjahāra") == "jagannujjahāra"
    assert pada_split("ab cd |/ef gh ||") == ["ab cd", "ef gh"]
    assert pada_words("udyamena hi sidhyanti kāryāṇi") == ["udyamena", "sidhyanti", "kāryāṇi"]
    # avagraha + danda stream parity: Böhtlingk vs DCS spacing must agree
    assert normalize("aṃśo 'pi duṣṭadiṣṭānāṃ") == normalize("aṃśo 'pi  duṣṭadiṣṭānāṃ")
    print("selftest: PASS")


def load_sayings(path: str, limit: int | None) -> list[dict]:
    sayings = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            padas = pada_split(r["iast"])
            r["_padas"] = padas
            r["_padas_norm"] = [normalize(p) for p in padas]
            r["_whole"] = "".join(r["_padas_norm"])
            r["_probe_words"] = [w for p in padas for w in pada_words(p)]
            sayings.append(r)
            if limit and len(sayings) >= limit:
                break
    return sayings


def load_dcs(db_path: str):
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = conn.execute(
        "SELECT s.id, s.sent_id, c.ref, s.text_sandhied FROM sentence s "
        "JOIN chapter c ON c.chapter_id = s.chapter_id"
    )
    ids, sent_ids, refs, streams = [], [], [], []
    word_index: dict[str, list[int]] = defaultdict(list)
    for i, (sid, sent_id, ref, text) in enumerate(cur):
        ids.append(sid)
        sent_ids.append(sent_id or "")
        refs.append(ref or "")
        streams.append(normalize(text or ""))
        for w in set(normalize(t) for t in (text or "").split()):
            if len(w) >= LONG_WORD and len(word_index[w]) < 40:
                word_index[w].append(i)
    conn.close()
    exact = {s: i for i, s in enumerate(streams) if s}
    return ids, sent_ids, refs, streams, word_index, exact


def verify(pada_norm: str, streams: list[str], cand: set[int]) -> list[int]:
    hits = []
    for i in sorted(cand):
        t = streams[i]
        if pada_norm and pada_norm in t:
            hits.append(i)
            if len(hits) >= MAX_LOCI_PER_PADA:
                break
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dcs-db", default=os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "VisualDCS", "src",
        "DCS-data-2026", "dcs_full.sqlite"))
    ap.add_argument("--out-dir", default=os.path.join(
        os.path.dirname(__file__), "..", "attestation"))
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return 0

    if not os.path.exists(args.dcs_db):
        print(f"FATAL: DCS db not found: {args.dcs_db}", file=sys.stderr)
        return 2
    if os.path.getsize(args.dcs_db) < MIN_DB_BYTES:
        print(f"FATAL: {args.dcs_db} looks like the 0-byte DECOY (danger fact); "
              "pass --dcs-db to the real DCS-data-2026/dcs_full.sqlite", file=sys.stderr)
        return 2

    sayings = load_sayings(os.path.abspath(SAYINGS_JSONL), args.limit)
    print(f"sayings loaded: {len(sayings)}", flush=True)
    ids, sent_ids, refs, streams, word_index, exact = load_dcs(os.path.abspath(args.dcs_db))
    print(f"dcs sentences loaded: {len(streams)}; index forms: {len(word_index)}", flush=True)

    tsv_rows = []          # (num, pada_no, status, sentence_id, sent_id, ref, dcs_text)
    attested: dict[int, list[dict]] = defaultdict(list)  # saying idx -> loci
    for si, r in enumerate(sayings):
        if r["_whole"] and r["_whole"] in exact:
            i = exact[r["_whole"]]
            loc = {"status": "exact_verse", "pada": None, "i": i}
            attested[si].append(loc)
            tsv_rows.append((r["num"], "", "exact_verse", ids[i], sent_ids[i], refs[i], streams[i]))
            continue
        for pi, pnorm in enumerate(r["_padas_norm"], 1):
            if not pnorm:
                continue
            words = sorted(set(r["_probe_words"]), key=len, reverse=True)[:3]
            cand: set[int] = set()
            for w in words:
                cand.update(word_index.get(w, ()))
            hits = verify(pnorm, streams, cand)
            if hits:
                for i in hits:
                    attested[si].append({"status": "pada", "pada": pi, "i": i})
                    tsv_rows.append((r["num"], pi, "pada", ids[i], sent_ids[i], refs[i], streams[i]))
            else:
                tsv_rows.append((r["num"], pi, "unattested", "", "", "", ""))

    n_say = len(sayings)
    n_att = len(attested)
    n_exact = sum(1 for v in attested.values() if any(l["status"] == "exact_verse" for l in v))
    status_counts = Counter(row[2] for row in tsv_rows)

    os.makedirs(args.out_dir, exist_ok=True)
    tsv_path = os.path.join(args.out_dir, "H4747_dcs_loci.tsv")
    with open(tsv_path, "w", encoding="utf-8") as f:
        f.write("num\tpada\tstatus\tdcs_sentence_id\tdcs_sent_id_label\tchapter_ref\tdcs_text_norm\n")
        for row in tsv_rows:
            f.write("\t".join(str(x) for x in row) + "\n")

    # coverage by source work (text before/after "N) " in source_attribution)
    def work_of(r):
        s = r.get("source_attribution") or ""
        s = re.sub(r"^\d+\)\s*", "", s).strip()
        return s[:40] if s else "(none)"
    cov_by_work: dict[str, Counter] = defaultdict(Counter)
    for si, r in enumerate(sayings):
        w = work_of(r)
        cov_by_work[w]["attested" if si in attested else "unattested"] += 1

    # 30-saying deterministic verification sample
    rng = random.Random(4747)
    att_idx = sorted(attested)
    sample = rng.sample(att_idx, min(30, len(att_idx)))

    rep_path = os.path.join(args.out_dir, "H4747_report.md")
    with open(rep_path, "w", encoding="utf-8") as f:
        f.write("# H4747 — Indische Sprüche × DCS locus attestation report\n\n")
        f.write(f"_Built: {date.today().isoformat()} · OxAlpha (opencode/z-ai/glm-5.3-flash)_\n\n")
        f.write("## Method\n\n")
        f.write("- Per-saying records: `IndischeSprueche/data/indische_sprueche.jsonl` (7,537, 2nd ed.).\n")
        f.write("- Match unit: pada (split on `/` `|`) as a normalized continuous letter stream\n")
        f.write("  (spacing/punctuation/avagraha stripped, `ṁ`→`ṃ`) — Böhtlingk prints continuous\n")
        f.write("  sandhi, DCS `text_sandhied` keeps annotator token boundaries, so spacing-sensitive\n")
        f.write("  matching would miss nearly everything.\n")
        f.write("- Whole-verse exact class checked first (`exact_verse`), then per-pada (`pada`).\n")
        f.write(f"- Candidate recall: long-word (≥{LONG_WORD}) inverted index over DCS sentences\n")
        f.write(f"  (≤{MAX_LOCI_PER_PADA} loci kept per pada), verified by substring containment.\n")
        f.write("- **Keying:** loci are keyed on the synthetic DCS `sentence.id` PK. `sent_id` is\n")
        f.write("  NOT unique within a chapter (FINDINGS §9 / DEAD_ENDS §6) and travels only as a\n")
        f.write("  `dcs_sent_id_label` column.\n\n")
        f.write("## Coverage\n\n")
        f.write(f"- sayings: {n_say}; with ≥1 DCS locus: {n_att} ({100*n_att/n_say:.1f}%)\n")
        f.write(f"- exact whole-verse matches: {n_exact}\n")
        f.write("- TSV row statuses: " + ", ".join(f"{k}={v}" for k, v in sorted(status_counts.items())) + "\n\n")
        f.write("## Coverage by source work (Böhtlingk's attribution, first 40 chars)\n\n")
        f.write("| source work | attested | unattested |\n|---|---:|---:|\n")
        for w, c in sorted(cov_by_work.items(), key=lambda kv: -sum(kv[1].values()))[:25]:
            f.write(f"| {w} | {c['attested']} | {c['unattested']} |\n")
        f.write("\n## 30-saying verification sample (seed=4747)\n\n")
        f.write("| num | source | loci (sentence_id · sent_id label · ref) | DCS text (norm, 70ch) | saying (70ch) |\n|---|---|---|---|---|\n")
        for si in sample:
            r = sayings[si]
            loci = " ; ".join(f"{ids[l['i']]} · {sent_ids[l['i']]} · {refs[l['i']]}" for l in attested[si][:3])
            dtx = streams[attested[si][0]["i"]][:70]
            say = r["_whole"][:70]
            f.write(f"| {r['num']} | {work_of(r)} | {loci} | {dtx} | {say} |\n")
        f.write("\n## Known limits / honest residual\n\n")
        f.write("- Unattested ≠ absent from the Indian tradition: DCS is a fixed corpus\n")
        f.write("  (the Bhagavadgītā is ABSENT from DCS; Nala is present), and Böhtlingk cites\n")
        f.write("  anthologies (SUBHĀṢ., etc.) that DCS does not carry.\n")
        f.write("- Sandhi-resolution variants (e.g. `jaganu...` vs `jagantu...`) and orthographic\n")
        f.write("  variants between Böhtlingk's IAST and DCS annotators reduce recall; no fuzzy\n")
        f.write("  matching was applied (honest exact/substring residual, by design).\n")
        f.write("- JSONL is the unproofed Excel-derived mirror (76 short of boesp2's 7,613);\n")
        f.write("  citation-facing work routes to boesp1/boesp2, per IndischeSprueche/README.md.\n")
        f.write("- The existing `Spr. N` `<ls>` citation crosswalk (PWG#87) is a DIFFERENT layer\n")
        f.write("  (dictionary-side citation hrefs); this TSV is the corpus-locus attestation layer.\n")
    print(f"attested: {n_att}/{n_say} ({100*n_att/n_say:.1f}%)  exact_verse: {n_exact}")
    print(f"wrote: {tsv_path}\nwrote: {rep_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
