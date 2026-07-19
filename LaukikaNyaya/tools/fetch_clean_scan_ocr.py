# -*- coding: utf-8 -*-
"""
Fetches page images for the handfulofpopular01/02/03jacoiala archive.org
items (University of California Libraries scans of Jacob's three
"handfuls", IIIF-served) and OCRs each with local Tesseract (requires the
`san` + `eng` trained-data packs). Writes raw/<ident>_ocr_san_eng.txt with
`=== PAGE N ===` markers, consumed by build_laukika_nyaya_clean_scan.py.

Unlike the original YKTn_... bound-combined scan (see
raw/jacob_1907-1911_archiveorg_djvu.txt), this item's own djvu.txt OCR
derivative does not recognize Devanagari at all (English-only OCR engine) --
the page IMAGES are high quality, so this script re-OCRs them locally with
a Sanskrit-aware Tesseract pass instead of relying on archive.org's own
text layer. See LaukikaNyaya/README.md "clean-scan reconciliation" for the
full writeup, including why the primary YKTn_ item's own image-serving
backend was (at time of writing) down -- see Uprava/SERVER_OUTAGES.md --
while this alternate item's IIIF backend worked.

Run (idempotent -- skips already-fetched/OCR'd pages):
    python fetch_clean_scan_ocr.py 01 1 80
    python fetch_clean_scan_ocr.py 02 1 112
    python fetch_clean_scan_ocr.py 03 1 186
"""
import sys
import os
import subprocess
import time
import urllib.request

VOL_IDS = {
    "01": "handfulofpopular01jacoiala",
    "02": "handfulofpopular02jacoiala",
    "03": "handfulofpopular03jacoiala",
}


def fetch_page(vol, page_num, outdir):
    ident = VOL_IDS[vol]
    fname = f"{ident}_{page_num:04d}.jp2"
    url = (f"https://iiif.archive.org/image/iiif/2/{ident}%2f{ident}_jp2.zip"
           f"%2f{ident}_jp2%2f{fname}/full/pct:65/0/default.jpg")
    outpath = os.path.join(outdir, f"p{page_num:04d}.jpg")
    if os.path.exists(outpath) and os.path.getsize(outpath) > 1000:
        return True
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            if len(data) > 1000:
                with open(outpath, "wb") as f:
                    f.write(data)
                return True
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return False


def ocr_page(outdir, page_num):
    imgpath = os.path.join(outdir, f"p{page_num:04d}.jpg")
    txtbase = os.path.join(outdir, f"p{page_num:04d}")
    if not os.path.exists(imgpath):
        return False
    subprocess.run(["tesseract", imgpath, txtbase, "-l", "san+eng", "--psm", "6"],
                    capture_output=True, timeout=60)
    return os.path.exists(txtbase + ".txt")


def concat_volume(vol, count, outdir, raw_out_path):
    blocks = []
    for p in range(1, count + 1):
        txt_path = os.path.join(outdir, f"p{p:04d}.txt")
        if not os.path.exists(txt_path):
            blocks.append(f"=== PAGE {p} MISSING (fetch failed) ===")
            continue
        with open(txt_path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        blocks.append(f"=== PAGE {p} ===")
        blocks.append(text.rstrip())
    with open(raw_out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(blocks) + "\n")


def main():
    vol = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    end = int(sys.argv[3]) if len(sys.argv) > 3 else None
    here = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(here, "_scratch_pages", f"vol{vol}")
    os.makedirs(outdir, exist_ok=True)
    ok_fetch, ok_ocr = 0, 0
    for p in range(start, (end or start) + 1):
        if fetch_page(vol, p, outdir):
            ok_fetch += 1
            if ocr_page(outdir, p):
                ok_ocr += 1
        if p % 20 == 0:
            print(f"progress: {p}/{end} fetched={ok_fetch} ocred={ok_ocr}")
    print(f"DONE vol{vol}: fetched={ok_fetch} ocred={ok_ocr} range={start}-{end}")
    if end:
        raw_path = os.path.join(here, "..", "raw", f"{VOL_IDS[vol]}_ocr_san_eng.txt")
        concat_volume(vol, end, outdir, raw_path)
        print(f"Concatenated -> {raw_path}")


if __name__ == "__main__":
    main()
