"""Phase 2 of HERITAGE_INRIA_ROADMAP.md: entry-level MW<->Heritage crosswalk.

The mirror's MW/*.html marks Heritage-covered entries with a duplicate anchor —
<a name="H_<key>"> immediately before the plain <a name="<key>"> — the static-HTML
form of the README's "yellow areas show the entries covered by Heritage" (see
HERITAGE_MIRROR_INVENTORY.md). H_<key> and DICO/*.html's <a class="navy" name="<key>">
use the same VH-derived key, so a covered MW entry can be resolved to its DICO
anchor directly via a global DICO key->file index, without OCR or fuzzy matching.

Output: mw_heritage_crosswalk.tsv (mw_key1 [SLP1] \t covered_flag \t heritage_entry_anchor)
mw_key1 is produced with huet_coverage.py's validated VH->IAST->SLP1 transcoder
(reused, not reimplemented) so the crosswalk joins on the same key space as the
rest of the CDSL/DCS studies in this directory.
"""
import sys, os, re, glob, csv
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import huet_coverage as hc

MIRROR = os.path.join(HERE, "heritage_mirror")
OUT_TSV = os.path.join(HERE, "mw_heritage_crosswalk.tsv")

ENTRY_ANCHOR_RE = re.compile(r'<a name="((?:H_)?[^"]+)"></a>')
DICO_ANCHOR_RE = re.compile(r'<a class="navy" name="([^"]*)"')

def build_dico_index():
    """raw DICO anchor key (with U/# as-is) -> 'DICO/<file>#<key>'"""
    idx = {}
    for fp in sorted(glob.glob(os.path.join(MIRROR, "DICO", "*.html"))):
        fname = os.path.basename(fp)
        text = open(fp, encoding='utf-8').read()
        for k in DICO_ANCHOR_RE.findall(text):
            idx.setdefault(k, f"DICO/{fname}#{k}")
    return idx

def entries_in_file(text):
    """Yield (raw_key, covered) for each MW entry, grouping consecutive anchors
    that precede a Deva span (the MW hypertext's per-entry anchor cluster)."""
    for block in re.finditer(r'((?:<a name="[^"]+"></a>)+)(?:&#160;)*<span class="Deva">', text):
        names = ENTRY_ANCHOR_RE.findall(block.group(1))
        covered = any(n.startswith('H_') for n in names)
        plain = [n for n in names if not n.startswith('H_')]
        if not plain:
            continue
        yield plain[0], covered

def main():
    mw_files = sorted(glob.glob(os.path.join(MIRROR, "MW", "*.html")))
    if not mw_files:
        sys.exit(f"No MW html found under {MIRROR}/MW — clone the mirror first (Phase 0).")
    dico_idx = build_dico_index()

    rows = []  # (mw_key1_slp1, covered_flag, heritage_entry_anchor)
    seen_slp1 = set()
    n_entries = n_covered = n_resolved = 0
    for fp in mw_files:
        text = open(fp, encoding='utf-8').read()
        for raw_key, covered in entries_in_file(text):
            n_entries += 1
            slp1 = hc.norm_huet(raw_key)
            if not slp1 or slp1 in seen_slp1:
                continue
            seen_slp1.add(slp1)
            anchor = ""
            if covered:
                n_covered += 1
                anchor = dico_idx.get(raw_key, "")
                if not anchor:
                    # DICO indexes proper nouns with a leading 'U' the MW side lacks
                    anchor = dico_idx.get("U" + raw_key, "")
                if not anchor:
                    # MW's plain anchor drops the '#N' homonym suffix DICO keeps
                    # (e.g. MW "a.mzaka" vs DICO "a.mzaka#1"/"a.mzaka#2"); the
                    # bare key is ambiguous, so this picks the first homonym
                    # arbitrarily rather than leaving a resolvable entry blank.
                    for n in range(1, 10):
                        anchor = dico_idx.get(f"{raw_key}#{n}", "")
                        if anchor:
                            break
                if anchor:
                    n_resolved += 1
            rows.append((slp1, "1" if covered else "0", anchor))

    with open(OUT_TSV, 'w', encoding='utf-8', newline='\n') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(["mw_key1", "covered_flag", "heritage_entry_anchor"])
        for r in rows:
            w.writerow(r)

    print(f"MW pages scanned: {len(mw_files)}")
    print(f"MW entries seen (pre-dedup): {n_entries}")
    print(f"unique mw_key1 rows written: {len(rows)}")
    print(f"covered (Heritage) rows: {n_covered}  ({100*n_covered/len(rows):.1f}%)")
    print(f"covered rows resolved to a DICO anchor: {n_resolved} ({100*n_resolved/max(1,n_covered):.1f}% of covered)")
    print(f"written: {OUT_TSV}")

if __name__ == "__main__":
    main()
