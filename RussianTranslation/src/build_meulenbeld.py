#!/usr/bin/env python
"""Build a Sanskrit plant-name → Latin-binomial table from Meulenbeld (= SNP).

Meulenbeld's "Sanskrit Names of Plants and their Botanical Equivalents" is the
Cologne dictionary SNP (csl-orig/v02/snp). indic-dict ships it pre-extracted as a
`.babylon` (headword → identification with ALL-CAPS Latin binomials and Sanskrit
equivalents). We parse that convenient form into an SLP1-keyed lookup so the
translate stage can render/keep a botanical binomial deterministically instead of
leaving it untranslated (the `Hedysarum gangeticum` failure mode).

Source = SNP (Cologne); the indic-dict packaging is used only for convenience and
is covered by both our own data rights and indic-dict's free-use grant.

Usage:  python build_meulenbeld.py [path-to-babylon-dir]
Output: meulenbeld_plants.jsonl
        each line = {"slp1","dev","binomials","sa_equivalents","gloss"}
"""
import json, os, re, sys
from build_indic import dev_to_slp1, is_devanagari, to_stem

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(HERE, '..', 'research', 'external')
SRC = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
FILE = 'Meulenbeld-Sanskrit-Names-of-Plants.babylon'

# Botanical binomials are printed in CAPS: "CARPOPOGON PRURIENS", "HEDYSARUM
# GANGETICUM", sometimes a third token (var./subsp.). Require >=2 CAPS tokens so
# we don't catch stray single-word acronyms (MW, PW, HK = source sigla).
_BINOM = re.compile(r'\b[A-Z][A-ZÀ-Þ-]{2,}(?:\s+[A-ZÀ-Þ][A-Za-zÀ-ÿ-]{2,}){1,2}\b')
_DEV_TOKEN = re.compile(r'[ऀ-ॿ]+')
# source-siglum CAPS runs to ignore even if they look binomial
_STOP = {'MW', 'PW', 'HK', 'HB', 'KB', 'AVK', 'VSS'}

def clean(s):
    s = s.replace('<BR>', ' ').replace('<br>', ' ')
    s = re.sub(r'(?<=[A-Za-z])-\s+(?=[a-z])', '', s)   # mend line-wrap hyphens (Bal- samodendrum)
    return re.sub(r'\s+', ' ', s).strip()

def parse_block(blk):
    lines = [ln for ln in blk.split('\n') if ln.strip()]
    if len(lines) < 2 or lines[0].startswith('#'):
        return None
    heads = [h.strip() for h in lines[0].split('|') if is_devanagari(h.strip())]
    if not heads:
        return None
    primary = heads[0]
    slp1 = dev_to_slp1(primary)
    if not slp1 or not slp1[0].isascii() or not slp1[0].isalpha():
        return None
    body = clean(' '.join(lines[1:]))
    body = re.sub(r'<a\s+href=.*$', '', body)        # drop trailing scan link
    binoms = []
    for m in _BINOM.findall(body):
        m = m.strip()
        toks = m.split()
        if all(t in _STOP for t in toks):
            continue
        # title-case the binomial: Genus species
        norm = ' '.join([toks[0].capitalize()] + [t.lower() for t in toks[1:]])
        if norm not in binoms:
            binoms.append(norm)
    # Sanskrit equivalents flagged "= देवनागरी"
    sa_eq = [t for t in _DEV_TOKEN.findall(body) if is_devanagari(t) and len(t) > 1
             and dev_to_slp1(t) != slp1][:8]
    return {'slp1': slp1, 'stem': to_stem(slp1), 'dev': primary,
            'binomials': binoms, 'sa_equivalents': sa_eq,
            'gloss': body[:300]}

def build():
    path = os.path.join(SRC, FILE)
    if not os.path.exists(path):
        sys.exit('not found: %s' % path)
    with open(path, encoding='utf-8') as f:
        blocks = re.split(r'\r?\n\r?\n', f.read())
    out_path = os.path.join(HERE, 'meulenbeld_plants.jsonl')
    n = n_binom = 0
    with open(out_path, 'w', encoding='utf-8', newline='') as o:
        for blk in blocks:
            rec = parse_block(blk)
            if not rec:
                continue
            o.write(json.dumps(rec, ensure_ascii=False) + '\n')
            n += 1
            if rec['binomials']:
                n_binom += 1
    print('meulenbeld_plants.jsonl: %d headwords, %d with >=1 Latin binomial' % (n, n_binom))
    return n

if __name__ == '__main__':
    build()
