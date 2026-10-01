#!/usr/bin/env python3
"""H4800 -- Sanskrityatina reverse-stock master word list vs union headwords
(16-dict, H4797), joined by form_key.

The registered `sanskrityatina-reverse-index` dataset is the 24-line coding
LEGEND of the 187,992-headword stock -- the per-headword coded list did not
survive (H4475 section 5, reverse-index meta backlog item 2).  The closest
recoverable per-headword artifact of the same 04_Reverse workshop is the
`IAST-hyphenation_b7.xlsm` working workbook (2014, gitignored raw/): sheet
`All_TEXT_NEW` = 252,134 IAST words, each optionally prefixed by a one-letter
source tag, plus sheet `>15` repeating the 35,619 long words with the tag in
an explicit column (used as the tag-splitter oracle).

This builder joins that 252,134-word master list to the 16-dict union
headword index (`HeadwordLists/union-16dicts/union_headwords_16.tsv`,
417,184 bare-SLP1 keys, H4797) with the identical key pipeline both sides
via sanskrit-util:  `slp1_form_key(to_slp1(word))`.  The 15-dict union
(`HeadwordLists/union/union_headwords.tsv`) is carried as a secondary flag.

Outputs (beside the datasets, LF, UTF-8, deterministic/idempotent):
  sanskrityatina_reverse_stock_union16_join.tsv
      all master rows + in_union16/in_union15 flags + union16 n_dicts/dicts,
      committed input order (# ascending)
  sanskrityatina_reverse_stock_union16_residue.tsv
      in_union16=0 rows only -- the workshop-only residue (forms attested in
      the Sanskrityatina workshop stock but absent from all 16 union dicts)
  H4800_HAND_SAMPLE_20.tsv
      deterministic stratified 20-row hand-verification sample
      (10 in-union + 10 residue, stride-sampled)
  sanskrityatina_reverse_stock_union16_provenance.json
      inputs + sha256, counts, per-tag coverage, unmapped characters, caveats

Usage:
  python3 tools/h4800_reverse_stock_vs_union16.py [--xlsm PATH] [--selftest]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent.parent          # .../sanskrityatina/
SANSKRIT_UTIL_CANDIDATES = [
    HERE / ".." / ".." / ".." / "sanskrit-util" / "py",   # sibling-clone default
    Path.home() / "Documents" / "GitHub" / "sanskrit-util" / "py",
]
DEFAULT_XLSM = HERE / "raw" / "IAST-hyphenation_b7.xlsm"
SL_ROOT = HERE / ".." / ".."
UNION16_TSV = SL_ROOT / "HeadwordLists" / "union-16dicts" / "union_headwords_16.tsv"
UNION15_TSV = SL_ROOT / "HeadwordLists" / "union" / "union_headwords.tsv"

JOIN_TSV = HERE / "sanskrityatina_reverse_stock_union16_join.tsv"
RESIDUE_TSV = HERE / "sanskrityatina_reverse_stock_union16_residue.tsv"
SAMPLE_TSV = HERE / "H4800_HAND_SAMPLE_20.tsv"
PROVENANCE = HERE / "sanskrityatina_reverse_stock_union16_provenance.json"

OUT_COLS = ("n", "tag", "word", "slp1", "form_key", "norm",
            "in_union16", "in_union15", "u16_n_dicts", "u16_dicts")

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
TAG_RE = re.compile(r"^([A-Z]) (\S.*)$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.iter(f"{NS}t"))
            for si in root.iter(f"{NS}si")]


def sheet_rows(zf: zipfile.ZipFile, target: str, ss: list[str]):
    """Yield rows as lists of cell strings (stdlib streaming)."""
    with zf.open(target) as fh:
        for _ev, el in ET.iterparse(fh, events=("end",)):
            if el.tag != f"{NS}row":
                continue
            vals = []
            for c in el.iter(f"{NS}c"):
                v = c.find(f"{NS}v")
                if v is None:
                    isn = c.find(f"{NS}is")
                    vals.append("".join(t.text or "" for t in isn.iter(f"{NS}t"))
                                if isn is not None else "")
                elif c.get("t") == "s":
                    vals.append(ss[int(v.text)])
                else:
                    vals.append(v.text)
            yield vals
            el.clear()


def clean_word(raw: str) -> str:
    # strip BOM / zero-width noise and outer whitespace; keep inner chars.
    # the workbook mixes NBSP (U+00A0) and space (U+0020) after the tag
    # letter (the >15 sheet uses NBSP) -- normalize to space first.
    return (raw.replace("\ufeff", "").replace("\u200b", "")
               .replace("\xa0", " ").strip())


def split_tag(raw: str) -> tuple[str, str]:
    m = TAG_RE.match(raw)
    if m:
        return m.group(1), m.group(2).strip()
    return "", raw.strip()


def load_master(xlsm_path: Path):
    """Parse All_TEXT_NEW (sheet1). Returns (rows, n_long_words)."""
    zf = zipfile.ZipFile(xlsm_path)
    ss = load_shared_strings(zf)
    rows: list[dict] = []
    n_long = 0
    for vals in sheet_rows(zf, "xl/worksheets/sheet1.xml", ss):
        if len(vals) < 2 or vals[0].strip() == "#":
            continue
        if not vals[0].strip().isdigit():
            continue
        raw = clean_word(vals[1])
        if not raw:
            continue
        tag, word = split_tag(raw)
        if len(word) > 15:
            n_long += 1
        rows.append({"n": int(vals[0]), "tag": tag, "word": word,
                     "raw": raw})
    rows.sort(key=lambda r: r["n"])
    return rows, n_long


def selftest(xlsm_path: Path) -> int:
    """(1) tag-splitter oracle: on the >15 sheet the tag and the bare word
    are explicit columns -- our splitter must reproduce them.
    (2) master # must be a contiguous 1..N run.
    (3) union16 header must match the expected 3-column contract."""
    zf = zipfile.ZipFile(xlsm_path)
    ss = load_shared_strings(zf)
    agree = disagree = 0
    examples = []
    for vals in sheet_rows(zf, "xl/worksheets/sheet3.xml", ss):
        # sheet columns: №№№ | # | word | Len | Char_book | Слово отдельно |
        #                Преобразование | Количество цифр | # | New_W
        # tagged rows carry 11 cells (Char_book=tag letter); untagged rows
        # carry 10 cells and the word reappears at index 4 (col 5 = the
        # digit-hyphenation transform, not the word).
        if len(vals) < 10 or vals[0].strip() == "№№№":
            continue
        combined = clean_word(vals[2])
        if len(vals) >= 11:
            cb = vals[4].strip()
            solo = clean_word(vals[5])
        else:
            cb = ""
            solo = clean_word(vals[4])
        tag, word = split_tag(combined)
        if (tag, word) == (cb, solo):
            agree += 1
        else:
            disagree += 1
            if len(examples) < 5:
                examples.append((combined, tag, word, cb, solo))
    total = agree + disagree
    rate = agree / total if total else 0.0
    print(f"selftest splitter oracle: {agree}/{total} agree "
          f"({100.0 * rate:.2f}%)")
    for e in examples:
        print(f"  DIS: combined={e[0]!r} split=({e[1]!r},{e[2]!r}) "
              f"oracle=({e[3]!r},{e[4]!r})")
    ok = total > 0 and rate >= 0.999

    rows, _ = load_master(xlsm_path)
    ns = [r["n"] for r in rows]
    contiguous = ns == list(range(1, len(ns) + 1))
    print(f"selftest master contiguity: {len(ns)} rows, 1..{ns[-1] if ns else 0}"
          f" contiguous={contiguous}")
    ok = ok and contiguous and len(ns) > 0

    header = UNION16_TSV.open(encoding="utf-8").readline().rstrip("\n").split("\t")
    hdr_ok = header == ["slp1", "n_dicts", "dicts"]
    print(f"selftest union16 header: {header} ok={hdr_ok}")
    ok = ok and hdr_ok

    print("SELFTEST PASS" if ok else "SELFTEST FAIL")
    return 0 if ok else 1


def stride_pick(rows: list[dict], want: int) -> list[dict]:
    if len(rows) <= want:
        return list(rows)
    step = len(rows) / want
    return [rows[min(int(i * step), len(rows) - 1)] for i in range(want)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsm", type=Path, default=DEFAULT_XLSM,
                    help="IAST-hyphenation_b7.xlsm (default: gitignored raw/)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest(args.xlsm)

    for cand in SANSKRIT_UTIL_CANDIDATES:
        if cand.is_dir():
            sys.path.insert(0, str(cand))
            break
    else:
        print("FATAL: sanskrit-util sibling clone not found", file=sys.stderr)
        return 2
    from sanskrit_util import SLP1_ALPHABET, slp1_form_key, to_slp1  # noqa: PLC0415

    if not args.xlsm.is_file():
        print(f"FATAL: xlsm not found: {args.xlsm} (refetch: rclone copy "
              f"'yadisk:Sanskrityatina/04_Reverse/IAST-hyphenation_b7.xlsm' "
              f"raw/)", file=sys.stderr)
        return 2
    if not UNION16_TSV.is_file() or not UNION15_TSV.is_file():
        print("FATAL: union TSVs not found under HeadwordLists/",
              file=sys.stderr)
        return 2

    # -- union key maps (identical pipeline both sides) --------------------
    # slp1_form_key folds case/nasals, so distinct union lemmas can collide
    # (e.g. 'aMsala' vs 'aMsAla').  On collision the more corroborated row
    # (higher n_dicts) is kept for display -- deterministic, and the count
    # of collided keys is reported in the provenance.
    def union_map(path: Path):
        m: dict[str, tuple[str, str]] = {}
        collided = 0
        with path.open(encoding="utf-8") as fh:
            header = fh.readline().rstrip("\n").split("\t")
            i_slp1 = header.index("slp1")
            i_nd = header.index("n_dicts")
            i_d = header.index("dicts")
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) <= i_d or not p[i_slp1]:
                    continue
                k = slp1_form_key(p[i_slp1])
                prev = m.get(k)
                if prev is None or int(p[i_nd]) > int(prev[0]):
                    if prev is not None:
                        collided += 1
                    m[k] = (p[i_nd], p[i_d])
        return m, collided

    u16, u16_collided = union_map(UNION16_TSV)
    u15, u15_collided = union_map(UNION15_TSV)

    # -- master rows -> keys ------------------------------------------------
    rows, n_long = load_master(args.xlsm)
    unmapped: Counter = Counter()
    norm_counts: Counter = Counter()
    allowed = set(SLP1_ALPHABET)  # uppercase IS legitimate SLP1 (z=ṣ S=ś T=th)
    key_dupes: Counter = Counter()
    import unicodedata
    for r in rows:
        # workshop markup normalization to the union's bare-lemma key space
        # (same contract as H4797's key2 normalization: documented, counted
        # per class, never guessed):
        #   'hyph' -- workshop sandhi/compound hyphen marks ('--', '-')
        #   'acc'  -- Vedic pitch accents (NFD combining acute/grave), which
        #             union k1 lemmas never carry
        #   'space'-- stray inner spaces after tag-split (never valid inside
        #             a single headword)
        w = r["word"]
        flags = []
        if "-" in w:
            w = w.replace("-", "")
            flags.append("hyph")
        nfd = unicodedata.normalize("NFD", w)
        stripped = "".join(ch for ch in nfd if ch not in ("\u0300", "\u0301"))
        if stripped != nfd:  # only when an accent was REMOVED;
            # NFC-recompose so ṛ/ṃ/ṇ/ṣ/ḥ stay precomposed for to_slp1
            # (NFD alone hands back decomposed base+dot-below pairs the
            #  transcoder cannot read)
            w = unicodedata.normalize("NFC", stripped)
            flags.append("acc")
        if " " in w:
            w = w.replace(" ", "")
            flags.append("space")
        r["norm"] = "|".join(flags)
        for f in flags:
            norm_counts[f] += 1
        slp1 = to_slp1(w)
        if any(c not in allowed for c in slp1):
            unmapped[r["word"]] += 1
        r["slp1"] = slp1
        k = slp1_form_key(slp1)
        r["form_key"] = k
        key_dupes[k] += 1
        hit16 = u16.get(k)
        hit15 = u15.get(k)
        r["in_union16"] = "1" if hit16 else "0"
        r["in_union15"] = "1" if hit15 else "0"
        r["u16_n_dicts"] = hit16[0] if hit16 else ""
        r["u16_dicts"] = hit16[1] if hit16 else ""

    # -- write join + residue + sample + provenance (byte-stable) ----------
    for out in (JOIN_TSV, RESIDUE_TSV, SAMPLE_TSV, PROVENANCE):
        tmp = out.with_suffix(out.suffix + ".tmp")
        tmp.write_text("", encoding="utf-8")
        tmp.unlink()

    with JOIN_TSV.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(OUT_COLS) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]) for c in OUT_COLS) + "\n")

    residue = [r for r in rows if r["in_union16"] == "0"]
    with RESIDUE_TSV.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(OUT_COLS) + "\n")
        for r in residue:
            fh.write("\t".join(str(r[c]) for c in OUT_COLS) + "\n")

    hit = [r for r in rows if r["in_union16"] == "1"]
    sample = stride_pick(hit, 10) + stride_pick(residue, 10)
    with SAMPLE_TSV.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(OUT_COLS) + "\n")
        for r in sample:
            fh.write("\t".join(str(r[c]) for c in OUT_COLS) + "\n")

    # -- coverage -----------------------------------------------------------
    by_tag: Counter = Counter(r["tag"] or "(none)" for r in rows)
    by_tag_hit: Counter = Counter(r["tag"] or "(none)" for r in rows
                                  if r["in_union16"] == "1")
    coverage_by_tag = {
        t: {"words": by_tag[t], "in_union16": by_tag_hit[t],
            "residue": by_tag[t] - by_tag_hit[t],
            "coverage_pct": round(100.0 * by_tag_hit[t] / by_tag[t], 2)}
        for t in sorted(by_tag)
    }
    # n_dicts corroboration histogram over matched rows
    nd_hist: Counter = Counter()
    for r in hit:
        nd_hist[int(r["u16_n_dicts"])] += 1

    prov = {
        "handoff": "H4800",
        "generated": "19-09-2026",
        "executor": "OxAlpha (opencode/z-ai/glm-5.3-flash)",
        "join_key": "sanskrit-util slp1_form_key -- master = "
                    "slp1_form_key(to_slp1(word)); union16 key = "
                    "slp1_form_key(bare slp1 column); identical pipeline "
                    "both sides",
        "inputs": {
            "xlsm_master": {
                "path": str(args.xlsm),
                "sha256": sha256(args.xlsm),
                "source": "yadisk:Sanskrityatina/04_Reverse/"
                          "IAST-hyphenation_b7.xlsm (2014-09-10)",
                "sheet": "All_TEXT_NEW",
                "data_rows": len(rows),
            },
            "union16": {
                "path": str(UNION16_TSV),
                "sha256": sha256(UNION16_TSV),
                "unique_keys": len(u16),
                "form_key_collided_union_rows": u16_collided,
            },
            "union15": {
                "path": str(UNION15_TSV),
                "sha256": sha256(UNION15_TSV),
                "unique_keys": len(u15),
                "form_key_collided_union_rows": u15_collided,
            },
        },
        "results": {
            "master_words": len(rows),
            "in_union16": len(hit),
            "residue_vs_union16": len(residue),
            "coverage_pct": round(100.0 * len(hit) / len(rows), 2)
            if rows else 0.0,
            "in_union15": sum(1 for r in rows if r["in_union15"] == "1"),
            "words_longer_than_15": n_long,
            "normalization_counts": dict(norm_counts),
            "unmapped_words_total": sum(unmapped.values()),
            "unmapped_examples": [
                {"word": w, "chars": sorted(set(
                    c for c in to_slp1(w) if c not in allowed))}
                for w in list(unmapped)[:15]
            ],
            "form_keys_with_multiple_raw_words":
                sum(1 for v in key_dupes.values() if v > 1),
            "coverage_by_tag": coverage_by_tag,
            "n_dicts_histogram_matched": {str(k): v for k, v in
                                          sorted(nd_hist.items())},
        },
        "caveats": [
            "The 187,992-headword CODED stock has NO surviving per-headword "
            "list (legend only -- H4475 section 5, meta backlog item 2); "
            "this join measures the recoverable per-headword artifact of the "
            "same 04_Reverse workshop: the 252,134-word IAST-hyphenation_b7 "
            "master word list. Class-level stock numbers stay legend-only.",
            "The one-letter source tags (M 19,956 / H 2,556 / G 2,491 / ...) "
            "are carried verbatim as opaque provenance; their dictionary "
            "mapping is undocumented in the workbook.",
            "Workshop markup is normalized to the union's bare-lemma key "
            "space exactly as H4797 normalized accented key2 forms: sandhi "
            "hyphens ('--'), Vedic pitch accents, and stray inner spaces "
            "are stripped, flagged in the `norm` column and counted per "
            "class (results.normalization_counts) -- never silently.",
            "Workbook noise (junk forms like 'uṃṃ') is data: rows are "
            "counted, never silently dropped; form_key folds case/nasals "
            "exactly as on the union side.",
            "Words with characters outside the SLP1 alphabet after "
            "transcoding are counted (unmapped) and cannot key-match.",
        ],
    }
    PROVENANCE.write_text(json.dumps(prov, ensure_ascii=False, indent=2,
                                     sort_keys=False) + "\n",
                          encoding="utf-8")

    # -- summary ------------------------------------------------------------
    print(f"master words          : {len(rows)}")
    print(f"  in union16          : {len(hit)} "
          f"({prov['results']['coverage_pct']}%)")
    print(f"  residue vs union16  : {len(residue)}")
    print(f"  in union15 (subset) : {prov['results']['in_union15']}")
    print(f"  len>15 words        : {n_long}")
    for t, v in coverage_by_tag.items():
        print(f"  tag {t:<7} {v['in_union16']:>6}/{v['words']:<6} "
              f"residue {v['residue']}")
    if unmapped:
        print(f"unmapped-char words   : {sum(unmapped.values())} "
              f"(counted, not matched)")
    print("OK: join + residue + hand sample + provenance written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
