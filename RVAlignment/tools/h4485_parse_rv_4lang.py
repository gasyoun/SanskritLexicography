#!/usr/bin/env python3
# coding=utf-8
"""H4485 — parse RV_sa-hn-ru-de-en_1.html (4-language RV alignment) into JSONL + sample TSV.

Source: yadisk RV/RV_sa-hn-ru-de-en.html (MG, June 2018), cleaned copy at
~/Documents/GitHub/rvlinks/RV_sa-hn-ru-de-en_1.html (sha256 00534391…231d0).
Structure per verse block:
    <p class="stamp">rvMM.HHH.VV</p>
    <p class="sa">…</p>   Vedic Devanagari (accented samhitapatha)
    <p class="hn">…</p>   IAST romanization
    <p class="ru">…</p>   Russian  (Elizarenkova; per CSS comment)
    <p class="de">…</p>   German   (Geldner;   per CSS comment)
    <p class="en">…</p>   English  (Griffith;  per CSS comment)

The parser is FAITHFUL: it never repairs or normalizes source characters
(private-use U+E003/E007/E009 are counted and reported, not rewritten).
Derived from the html only; the html itself stays local and is never committed.

Usage:
  python3 tools/h4485_parse_rv_4lang.py --input <html> --outdir <dir> [--sample 20]
  python3 tools/h4485_parse_rv_4lang.py --selftest
"""
from __future__ import annotations

import argparse
import html
import json
import os
import random
import re
import sys
import unicodedata

STAMP_RE = re.compile(r'<p class="stamp">rv(\d+)\.(\d+)\.(\d+)</p>')
BLOCK_RE = re.compile(r'<p class="(sa|hn|ru|de|en)">(.*?)</p>', re.S)
BR_RE = re.compile(r'<br\s*/?>', re.I)
TAG_RE = re.compile(r'<[^>]+>')
STAMP = ("sa", "hn", "ru", "de", "en")

DEV_RANGE = (0x0900, 0x097F)
CYR_RANGE = (0x0400, 0x04FF)


def clean_field(raw: str) -> str:
    """HTML block -> plain text: <br> -> newline, strip tags, unescape, trim."""
    text = BR_RE.sub("\n", raw)
    text = TAG_RE.sub("", text)
    text = html.unescape(text)
    lines = [re.sub(r"[ \t\u00a0]+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln).strip()


def has_script(text: str, lo: int, hi: int) -> bool:
    return any(lo <= ord(c) <= hi for c in text)


def parse_html(data: str):
    """Yield one dict per verse stamp block. Faithful to source characters."""
    stamps = list(STAMP_RE.finditer(data))
    if not stamps:
        raise ValueError("no stamp blocks found — wrong input file?")
    for i, m in enumerate(stamps):
        end = stamps[i + 1].start() if i + 1 < len(stamps) else len(data)
        block = data[m.end():end]
        fields = {c: "" for c in STAMP}
        for fm in BLOCK_RE.finditer(block):
            cls, raw = fm.group(1), fm.group(2)
            if cls in fields and not fields[cls]:
                fields[cls] = clean_field(raw)
        mandala, hymn, verse = (int(g) for g in m.groups())
        yield {
            "key": "rv%02d.%03d.%02d" % (mandala, hymn, verse),
            "mandala": mandala, "hymn": hymn, "verse": verse,
            **fields,
        }


def pua_inventory(text: str):
    inv = {}
    for c in text:
        if 0xE000 <= ord(c) <= 0xF8FF:
            k = "U+%04X" % ord(c)
            inv[k] = inv.get(k, 0) + 1
    return inv


def build_census(records):
    counts = {c: 0 for c in STAMP}
    empty = {c: 0 for c in STAMP}
    script_bad = {c: 0 for c in STAMP}
    pua = {}
    per_mandala = {}
    hymns = set()
    continuity_errors = []
    prev, expected_v = None, 1
    n_verses = 0
    for r in records:
        n_verses += 1
        hymns.add((r["mandala"], r["hymn"]))
        pm = per_mandala.setdefault(r["mandala"], {"hymns": set(), "verses": 0})
        pm["hymns"].add(r["hymn"])
        pm["verses"] += 1
        cur = (r["mandala"], r["hymn"])
        if cur != prev:
            prev, expected_v = cur, 1
        if r["verse"] != expected_v:
            continuity_errors.append("%s expected verse %d" % (r["key"], expected_v))
        expected_v += 1
        for c in STAMP:
            t = r[c]
            if t:
                counts[c] += 1
            else:
                empty[c] += 1
            if c == "sa":
                if t and not has_script(t, *DEV_RANGE):
                    script_bad[c] += 1
                for k, n in pua_inventory(t).items():
                    pua[k] = pua.get(k, 0) + n
            elif c == "ru":
                if t and (not has_script(t, *CYR_RANGE) or has_script(t, *DEV_RANGE)):
                    script_bad[c] += 1
            else:
                if t and (has_script(t, *DEV_RANGE) or has_script(t, *CYR_RANGE)):
                    script_bad[c] += 1
    mandala_table = [
        {"mandala": m,
         "hymns": len(per_mandala[m]["hymns"]),
         "verses": per_mandala[m]["verses"]}
        for m in sorted(per_mandala)
    ]
    return {
        "verses": n_verses,
        "hymns": len(hymns),
        "mandalas": [m["mandala"] for m in mandala_table],
        "counts": counts,
        "empty": empty,
        "script_bad": script_bad,
        "pua": pua,
        "continuity_errors": continuity_errors,
        "mandala_table": mandala_table,
    }


def pick_sample(records, n=20, seed=4485):
    """n verses: first verse of each mandala (10) + seeded random fill."""
    records = list(records)
    firsts = []
    seen_m = set()
    for r in records:
        if r["mandala"] not in seen_m and r["verse"] == 1:
            firsts.append(r)
            seen_m.add(r["mandala"])
    rng = random.Random(seed)
    rest = [r for r in records if id(r) not in {id(x) for x in firsts}]
    extra = rng.sample(rest, max(0, n - len(firsts)))
    return (firsts + extra)[:n]


def tsv_field(text: str) -> str:
    return text.replace("\\", "\\\\").replace("\t", " ").replace("\n", " ⏎ ")


def write_sample_tsv(sample, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("key\tmandala\thymn\tverse\tsa\thn\tru\tde\ten\n")
        for r in sample:
            f.write("\t".join([
                r["key"], str(r["mandala"]), str(r["hymn"]), str(r["verse"]),
                tsv_field(r["sa"]), tsv_field(r["hn"]), tsv_field(r["ru"]),
                tsv_field(r["de"]), tsv_field(r["en"]),
            ]) + "\n")


def validate_sample(sample):
    """Per-verse checks for the human-readable validation table."""
    rows = []
    for r in sample:
        checks = {
            "all_5_nonempty": all(r[c] for c in STAMP),
            "sa_deva": has_script(r["sa"], *DEV_RANGE),
            "hn_latin": r["hn"] and not has_script(r["hn"], *DEV_RANGE) and not has_script(r["hn"], *CYR_RANGE),
            "ru_cyr": has_script(r["ru"], *CYR_RANGE) and not has_script(r["ru"], *DEV_RANGE),
            "de_latin": r["de"] and not has_script(r["de"], *DEV_RANGE) and not has_script(r["de"], *CYR_RANGE),
            "en_latin": r["en"] and not has_script(r["en"], *DEV_RANGE) and not has_script(r["en"], *CYR_RANGE),
        }
        rows.append({"key": r["key"], **checks,
                     "pass": all(checks.values())})
    return rows


# ---------------------------------------------------------------- selftest
FIXTURE = """<html><body><table><tr><td>
<br /><p class="stamp">rv01.001.01</p>
<p class="sa">अ॒ग्निमी॑ळे पु॒रोहि॑तं॥ </p>
<p class="hn">agnim īḷe purohitam ||<br /></p>
<p class="ru">Агни призываю я.<BR>
Вторая строка.</p>
<p class="de">Agni berufe ich.</p>
<p class="en">I Laud Agni.</p>
<br /><p class="stamp">rv01.001.02</p>
<p class="sa">अ॒ग्निः पूर्वे॑भि॒रृषि॑भि॒रीड्यो॒॥ </p>
<p class="hn">agniḥ pūrvebhir ṛṣibhir īḍyo ||<br /></p>
<p class="ru">Агни достоин.<BR></p>
<p class="de">Agni war zu berufen.</p>
<p class="en">Agni was to be praised.</p>
</td></tr></table></body></html>"""


def selftest() -> int:
    failures = []
    recs = list(parse_html(FIXTURE))
    if len(recs) != 2:
        failures.append("fixture verse count %d != 2" % len(recs))
    r0 = recs[0]
    if r0["key"] != "rv01.001.01":
        failures.append("key %r" % r0["key"])
    if r0["sa"] != "अ॒ग्निमी॑ळे पु॒रोहि॑तं॥":
        failures.append("sa %r" % r0["sa"])
    if r0["hn"] != "agnim īḷe purohitam ||":
        failures.append("hn %r" % r0["hn"])
    if r0["ru"] != "Агни призываю я.\nВторая строка.":
        failures.append("ru newline handling: %r" % r0["ru"])
    if r0["de"] != "Agni berufe ich." or r0["en"] != "I Laud Agni.":
        failures.append("de/en %r %r" % (r0["de"], r0["en"]))
    # entity unescape
    recs2 = list(parse_html('<p class="stamp">rv02.003.04</p>'
                            '<p class="sa">x</p><p class="hn">a &amp; b</p>'
                            '<p class="ru">у</p><p class="de">d</p><p class="en">e</p>'))
    if recs2[0]["hn"] != "a & b":
        failures.append("entity unescape: %r" % recs2[0]["hn"])
    # census catches continuity + script issues
    bad = list(parse_html('<p class="stamp">rv01.001.01</p>'
                          '<p class="sa">x</p><p class="hn">a</p>'
                          '<p class="ru">у</p><p class="de">d</p><p class="en">e</p>'
                          '<p class="stamp">rv01.001.03</p>'
                          '<p class="sa">य</p><p class="hn">b</p>'
                          '<p class="ru">у</p><p class="de">d</p><p class="en">e</p>'))
    cen = build_census(bad)
    if len(cen["continuity_errors"]) != 1:
        failures.append("continuity: %r" % cen["continuity_errors"])
    if cen["script_bad"]["sa"] != 1:  # 'x' has no Devanagari
        failures.append("script_bad sa: %r" % cen["script_bad"])
    if cen["script_bad"]["ru"] != 0:
        failures.append("script_bad ru: %r" % cen["script_bad"])
    # faithful parse: PUA preserved, not repaired
    recs3 = list(parse_html('<p class="stamp">rv01.001.01</p>'
                            '<p class="sa">व॒\ue003 सु</p><p class="hn">vaḥ su</p>'
                            '<p class="ru">у</p><p class="de">d</p><p class="en">e</p>'))
    if "\ue003" not in recs3[0]["sa"]:
        failures.append("PUA must be preserved, not repaired")
    if failures:
        for f in failures:
            print("SELFTEST FAIL:", f)
        return 1
    print("SELFTEST PASS (9 checks: parse×5, entity, continuity, script-class, PUA-faithful)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", help="path to RV_sa-hn-ru-de-en_1.html")
    ap.add_argument("--outdir", help="output dir for JSONL + sample TSV")
    ap.add_argument("--sample", type=int, default=20)
    ap.add_argument("--seed", type=int, default=4485)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.input or not args.outdir:
        ap.error("--input and --outdir required (or --selftest)")
    data = open(args.input, encoding="utf-8").read()
    records = list(parse_html(data))
    cen = build_census(records)
    os.makedirs(args.outdir, exist_ok=True)
    jsonl_path = os.path.join(args.outdir, "rv_4lang_alignment.jsonl")
    with open(jsonl_path, "w", encoding="utf-8", newline="") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    sample = pick_sample(records, args.sample, args.seed)
    tsv_path = os.path.join(args.outdir, "rv_4lang_sample%d.tsv" % len(sample))
    write_sample_tsv(sample, tsv_path)
    rows = validate_sample(sample)
    summary = {
        "input": os.path.basename(args.input),
        "input_bytes": os.path.getsize(args.input),
        "census": cen,
        "sample_rows": rows,
        "sample_all_pass": all(r["pass"] for r in rows),
        "outputs": {"jsonl": jsonl_path, "sample_tsv": tsv_path},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    ok = (cen["verses"] == 10552 and cen["hymns"] == 1028
          and not cen["continuity_errors"]
          and all(v == 0 for v in cen["empty"].values())
          and all(v == 0 for v in cen["script_bad"].values())
          and summary["sample_all_pass"])
    print("PARSE VERDICT:", "PASS" if ok else "REVIEW", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
