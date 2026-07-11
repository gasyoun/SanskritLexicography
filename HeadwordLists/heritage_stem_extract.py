"""Extract the CURRENT Heritage/DICO stem inventory from the GitHub-mirror HTML
(HeadwordLists/heritage_mirror/DICO/*.html), as a fallback source for Phase 1 of
HERITAGE_INRIA_ROADMAP.md (the Phase-0 @DO manual browser download of the current
site export takes priority when it exists; this script is the mirror-only fallback).

Normalizes DICO's anchor-key conventions (see HERITAGE_MIRROR_INVENTORY.md) so the
result is comparable to the 2014 export used by huet_coverage.py:
  - leading 'U'  (proper-noun marker)      -> stripped
  - leading '-'  (bound affix/suffix, not a free stem) -> entry dropped
  - trailing '#N' (homonym disambiguator)  -> stripped (dedup after strip)
"""
import sys, os, re, glob
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
MIRROR_DICO = os.path.join(HERE, "heritage_mirror", "DICO")
OUT = os.path.normpath(os.path.join(HERE, "heritage_current_stems.txt"))

ANCHOR_RE = re.compile(r'<a class="navy" name="([^"]*)"')

def extract():
    keys = set()
    dropped_affix = 0
    files = sorted(glob.glob(os.path.join(MIRROR_DICO, "*.html")))
    if not files:
        sys.exit(f"No DICO html found under {MIRROR_DICO} — clone the mirror first (Phase 0).")
    for fp in files:
        text = open(fp, encoding='utf-8').read()
        for raw in ANCHOR_RE.findall(text):
            k = raw
            if k.startswith('-'):
                dropped_affix += 1
                continue
            if k.startswith('U'):
                k = k[1:]
            k = re.sub(r'#\d+$', '', k)
            if k:
                keys.add(k)
    return keys, dropped_affix, len(files)

if __name__ == "__main__":
    keys, dropped_affix, nfiles = extract()
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        for k in sorted(keys):
            f.write(k + '\n')
    print(f"DICO pages scanned: {nfiles}")
    print(f"bound-affix anchors dropped ('-' prefix): {dropped_affix}")
    print(f"unique current stem keys (VH, post-normalisation): {len(keys)}")
    print(f"written: {OUT}")
