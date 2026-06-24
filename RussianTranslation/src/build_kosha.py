#!/usr/bin/env python
"""Build the non-Cologne Sanskrit synonym-kosha sources for the pwg_ru gate.

Parses the indic-dict Sanskrit→Sanskrit kosha `.babylon` exports (traditional
synonym/homonym lexica: Amarakosha variants, Abhidhanachintamani supplements,
namamalika, etc.) into an SLP1-keyed synonym index. These feed the gate's
SANSKRIT-SIDE sense-corroboration channel (`skd_vcp_synonyms`, Rule 5 of
pwg_ru_prompts/4_korpus_proverka.txt) — they confirm WHICH sense a PWG headword
carries via its Sanskrit synonym set; they are NEVER Russian glosses and never
decide correctness.

Only koshas NOT already in csl-orig are built here (Sabdakalpadruma=skd,
Vacaspatyam=vcp, Abhidhanachintamani=abch, Abhidhanaratnamala=armh are Cologne →
use csl-orig). Rights: free use with attribution (indic-dict maintainer, email
2026-06-24); see INDIC_DICT_EVALUATION.md.

Usage:  python build_kosha.py [path-to-babylon-dir]
Output: kosha_syn.jsonl   each line = {"source","slp1","dev","syn_dev","syn_slp1"}
"""
import json, os, re, sys
from build_indic import dev_to_slp1, is_devanagari

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(HERE, '..', 'research', 'external')
SRC = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC

# non-Cologne sa-sa SYNONYM/homonym koshas (file slug == gate code). Excluded
# (not synonym sources, verified by sampling): amara-sudhA (Paninian derivation /
# prakriyA, amarasudha.in — useful for paradigm/derivation work, NOT synonyms),
# laxaNa-sangraha (nyAya definitions), ekAkSharanAmamAlA (verse-only, no parseable
# group), e-bhAratI-sampat (yielded ~3 rows, not a synonym lexicon).
KOSHAS = [
    'amara-onto', 'anekArthadhvanimanjarI', 'nAmamAlikA',
    'vaiShNava-koshaH', 'shaiva-kosha',
    'abhidhAnachintAmaNiparishiShTa', 'abhidhAnachintAmaNishilonCha',
    'bhUtasankhyA_kp_shukla', 'upasargArthachandrikA',
    'jhaLkI-bhIma-nyAya-koshaH',
]

# amara-onto carries an explicit "समानार्थक:a,b,c" (synonym) field — harvest it.
_SAMAN = re.compile(r'समानार्थक[\s:：]*([^<\n]+)')
_DEV_TOKEN = re.compile(r'[ऀ-ॿ]+')
MAX_SYN = 24

def devtokens(s):
    return [t for t in _DEV_TOKEN.findall(s or '') if is_devanagari(t) and len(t) > 1]

def parse_block(blk):
    """One babylon block -> a synonym GROUP (list of distinct Devanagari forms)."""
    lines = [ln for ln in blk.split('\n') if ln.strip()]
    if len(lines) < 2 or lines[0].startswith('#'):
        return []
    group = [h.strip() for h in lines[0].split('|') if is_devanagari(h.strip())]
    body = ' '.join(lines[1:])
    m = _SAMAN.search(body)
    if m:
        group += [t.strip() for t in re.split(r'[,，]', m.group(1)) if is_devanagari(t.strip())]
    # dedup, keep order
    seen, out = set(), []
    for g in group:
        if g not in seen:
            seen.add(g); out.append(g)
    return out

def build(slug):
    path = os.path.join(SRC, slug + '.babylon')
    if not os.path.exists(path):
        print('  SKIP %-30s (not found)' % slug); return 0
    with open(path, encoding='utf-8') as f:
        blocks = re.split(r'\r?\n\r?\n', f.read())
    rows = 0
    out_path = os.path.join(HERE, 'kosha_syn.jsonl')
    with open(out_path, 'a', encoding='utf-8', newline='') as o:   # main() truncates first
        for blk in blocks:
            group = parse_block(blk)
            if len(group) < 2:        # need at least one synonym to be useful
                continue
            for i, member in enumerate(group):
                slp1 = dev_to_slp1(member)
                if not slp1 or not slp1[0].isascii() or not slp1[0].isalpha():
                    continue
                others = [g for j, g in enumerate(group) if j != i][:MAX_SYN]
                o.write(json.dumps({
                    'source': slug, 'slp1': slp1, 'dev': member,
                    'syn_dev': others,
                    'syn_slp1': [dev_to_slp1(g) for g in others],
                }, ensure_ascii=False) + '\n')
                rows += 1
    print('%-30s rows=%6d' % (slug, rows))
    return rows

if __name__ == '__main__':
    if not os.path.isdir(SRC):
        sys.exit('babylon source dir not found: %s' % SRC)
    # truncate once via the first kosha's 'w' mode, then append
    out_path = os.path.join(HERE, 'kosha_syn.jsonl')
    if os.path.exists(out_path):
        os.remove(out_path)
    total = sum(build(s) for s in KOSHAS)
    print('TOTAL synonym rows: %d' % total)
