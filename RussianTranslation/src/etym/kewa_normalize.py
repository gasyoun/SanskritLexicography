"""Normalize the OCRed KEWA heading index into one row per heading (H3169, C4).

Emits `kewa_index_normalized.tsv` (one row per *heading*, not per printed
block) plus a JSON noise census.  This is the *modern IE* lane of the ceiling
C4 etymology layer; the *traditional* lane (Cologne 19th-c. extractors) is
built elsewhere and the two are never merged into one field.

Only headings, volume and page pointers are carried.  No KEWA article text is
read, and none is emitted.

Two facts about the source drive the design:

* the second slashed key column is **Harvard-Kyoto**, not SLP1 (see
  [`kewa_hk.py`](kewa_hk.py)) - it is audited here, never joined on;
* the index survived a Russian-locale spreadsheet round-trip that turned three
  page ranges into dates and five leading-hyphen headings into `#IMYA?`.

Usage:
    python kewa_normalize.py [--src PATH] [--outdir DIR]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "sanskrit-util", "py"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sanskrit_util import to_slp1  # noqa: E402  canonical transcoder, never a local copy

from kewa_hk import hk_to_slp1  # noqa: E402
from kewa_parse import iter_rows, strip_accents  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_SRC = "C:/Users/user/Documents/GitHub/SamudraManthanam/Index/lib/x86_64-win64/Data/KEWA.txt"

IMG_PAGE = re.compile(r"/(?P<vol>\d)-(?P<p1>\d{3})(?:-(?P<p2>\d{2,3}))?-(?P<idx>\d{2})\.jpg$")
PAGE_OK = re.compile(r"^\d+(?:-\d+)?$")
CYRILLIC = re.compile(r"[\u0400-\u04FF]")
LATIN_UPPER = re.compile(r"[A-Z]")
BREVE = "\u0306"
MACRON_C = "\u0304"
COLS = ["kewa_seq", "vol", "page", "heading_idx", "deva", "iast_printed",
        "iast_plain", "slp1", "hk_file", "hk_slp1", "key_source", "flags"]


def repair_page(page_raw: str, img: str) -> tuple[str, str]:
    """Return (page, flag).

    Three page fields were destroyed by a Russian-locale spreadsheet round-trip
    that read `10-11` as a date (`10.noya`).  The image filename kept the truth.
    """
    if PAGE_OK.match(page_raw) and not CYRILLIC.search(page_raw):
        return page_raw, ""
    m = IMG_PAGE.search(img)
    if not m:
        return page_raw, "page-corrupt-unrepairable"
    p1 = str(int(m.group("p1")))
    p2 = m.group("p2")
    if p2 is not None:
        return f"{p1}-{int(p2)}", "page-date-coerced-repaired"
    return p1, "page-date-coerced-repaired"


def split_machine_forms(raw_forms: list[str]) -> list[str]:
    """The machine-key field sometimes packs two forms into one slash group."""
    out: list[str] = []
    for f in raw_forms:
        for part in f.split(","):
            part = part.strip()
            if part:
                out.append(part)
    return out


def join_key(s: str) -> tuple[str, list[str]]:
    """Strip the bound-form markers KEWA prints, and say which were there."""
    flags: list[str] = []
    s = s.strip()
    if s.startswith("-"):
        flags.append("bound-suffix")
    if s.endswith("-"):
        flags.append("bound-prefix-or-stem")
    return s.strip("-").strip(), flags


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=DEFAULT_SRC)
    ap.add_argument("--outdir", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "etym"))
    args = ap.parse_args()

    outdir = os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)

    census: collections.Counter = collections.Counter()
    rows_out = []
    n_blocks = 0

    for row in iter_rows(args.src):
        if row.seq == -1:
            census["block:unparsed-line-shape"] += 1
            continue
        n_blocks += 1
        page, pflag = repair_page(row.page, row.img)
        if pflag:
            census[f"block:{pflag}"] += 1
        block_spreadsheet_error = bool(
            CYRILLIC.search(" ".join(row.deva) + " ".join(row.iast_accented)))
        if block_spreadsheet_error:
            census["block:spreadsheet-name-error"] += 1

        forms = split_machine_forms(row.file_forms)
        n_deva, n_iast = len(row.deva), len(row.iast_accented)
        n = n_deva or n_iast
        if n == 0 and not forms:
            census["block:no-heading-at-all"] += 1
            continue

        key_source = "machine-key"
        if len(forms) == 2 * n and n:
            iast_keys, hk_keys = forms[:n], forms[n:]
        elif len(forms) == n and n:
            iast_keys, hk_keys = forms, [""] * n
        elif forms and not n:
            iast_keys, hk_keys, n = forms, [""] * len(forms), len(forms)
        else:
            iast_keys = [strip_accents(x) for x in row.iast_accented] or forms
            hk_keys = [""] * len(iast_keys)
            n = len(iast_keys)
            key_source = "printed-iast-fallback"
            census["block:machine-key-unalignable"] += 1

        if n_deva and n_iast and n_deva != n_iast:
            census["block:printed-iast-collapses-variants"] += 1

        for i in range(n):
            flags: list[str] = []
            if block_spreadsheet_error:
                flags.append("spreadsheet-name-error")
            deva = row.deva[i] if i < n_deva else ""
            printed = row.iast_accented[i] if i < n_iast else ""
            iast = unicodedata.normalize("NFC", strip_accents(iast_keys[i]))
            if BREVE in iast or MACRON_C in iast:
                flags.append("combining-mark-residue")
                iast = iast.replace(BREVE, "")
            if LATIN_UPPER.search(iast):
                if iast[0] == "Z" or LATIN_UPPER.search(iast[1:]):
                    flags.append("legacy-font-latin-leak")
                else:
                    flags.append("proper-name-capital")
            key_src, kflags = join_key(iast.lower())
            flags.extend(kflags)
            slp1 = to_slp1(key_src)

            hk_raw, _ = join_key(hk_keys[i] if i < len(hk_keys) else "")
            hk_slp1 = hk_to_slp1(hk_raw) if hk_raw else ""
            if hk_raw:
                if hk_slp1 == slp1:
                    census["heading:machine-key-hk-confirmed"] += 1
                else:
                    flags.append("machine-key-anomalous")
                if hk_raw != slp1:
                    census["heading:hk-differs-from-slp1"] += 1

            for f in flags:
                census[f"heading:{f}"] += 1
            census["heading:total"] += 1

            rows_out.append({
                "kewa_seq": row.seq, "vol": row.vol, "page": page,
                "heading_idx": i, "deva": deva, "iast_printed": printed,
                "iast_plain": iast, "slp1": slp1, "hk_file": hk_raw,
                "hk_slp1": hk_slp1, "key_source": key_source,
                "flags": "|".join(flags),
            })

    census["block:total"] = n_blocks

    tsv = os.path.join(outdir, "kewa_index_normalized.tsv")
    with open(tsv, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(COLS) + "\n")
        for r in rows_out:
            fh.write("\t".join(str(r[c]) for c in COLS) + "\n")

    # The normalized index carries the printed headings themselves, so it stays
    # local-only while the Mayrhofer permission terms are untranscribed (see the
    # memo, Rights).  The manifest is what gets committed in its place: enough
    # to verify a regenerated copy byte-for-byte.
    digest = hashlib.sha256(open(tsv, "rb").read()).hexdigest()
    mf = os.path.join(outdir, "kewa_index_normalized.manifest.json")
    with open(mf, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"file": "kewa_index_normalized.tsv", "rows": len(rows_out),
                   "columns": COLS, "sha256": digest,
                   "source": os.path.basename(args.src),
                   "committed": False,
                   "why_not_committed": ("carries KEWA heading text; regenerate "
                                         "with kewa_normalize.py")},
                  fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    cj = os.path.join(outdir, "kewa_noise_census.json")
    with open(cj, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(dict(sorted(census.items())), fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"blocks: {n_blocks}  headings: {len(rows_out)}")
    for k, v in sorted(census.items()):
        print(f"  {k}: {v}")
    print(f"wrote {tsv}\nwrote {cj}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
