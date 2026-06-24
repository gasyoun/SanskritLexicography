#!/usr/bin/env python
"""Build the indic-dict Hindi sense-signal sources for the pwg_ru stage-4 gate.

Parses the StarDict `.babylon` exports of the indic-dict Indic-gloss dictionaries
(Sanskrit headword, Hindi gloss) into normalized, SLP1-keyed JSONL — one file per
source. These are a SOFT, THIRD-LANGUAGE *sense* signal (which sense is primary),
never a correctness vote on the Russian; see INDIC_DICT_EVALUATION.md and
SAMUDRA_INTEGRATION.md §2.

Rights: free use with attribution, granted by the indic-dict maintainer by email
(2026-06-24). Outputs are DATA and .gitignored (src/*.jsonl); this script is the
committed, regenerable contract. The source `.babylon` files live, also gitignored,
in research/external/ (large; fetched from indic-dict/stardict-sanskrit).

Usage:  python build_indic.py [path-to-babylon-dir]
Output: apte_hi.jsonl  vedic_rituals_hi.jsonl
        each line = {"source","slp1","dev","pos","gloss","attribution"}
"""
import json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(HERE, '..', 'research', 'external')
SRC = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC

# source file (in SRC)  ->  (gate code, attribution string)
SOURCES = [
    ('apte-hi.babylon', 'apte_hi',
     'Apte (Sanskrit→Hindi), via indic-dict/stardict-sanskrit; free use w/ attribution'),
    ('vedic-rituals-hi.babylon', 'vedic_rituals_hi',
     'Vedic-rituals Hindi glossary, via indic-dict/stardict-sanskrit; free use w/ attribution'),
]

# --- Devanagari -> SLP1 (same minimal transducer as build_src.recover_key) ----
_DEV_V = {'अ':'a','आ':'A','इ':'i','ई':'I','उ':'u','ऊ':'U','ऋ':'f','ॠ':'F',
          'ऌ':'x','ॡ':'X','ए':'e','ऐ':'E','ओ':'o','औ':'O'}
_DEV_M = {'ा':'A','ि':'i','ी':'I','ु':'u','ू':'U','ृ':'f','ॄ':'F','ॢ':'x',
          'ॣ':'X','े':'e','ै':'E','ो':'o','ौ':'O'}
_DEV_C = {'क':'k','ख':'K','ग':'g','घ':'G','ङ':'N','च':'c','छ':'C','ज':'j',
          'झ':'J','ञ':'Y','ट':'w','ठ':'W','ड':'q','ढ':'Q','ण':'R','त':'t',
          'थ':'T','द':'d','ध':'D','न':'n','प':'p','फ':'P','ब':'b','भ':'B',
          'म':'m','य':'y','र':'r','ल':'l','व':'v','श':'S','ष':'z','स':'s',
          'ह':'h','ळ':'L'}
_DEV_SIGN = {'ं':'M','ः':'H','ँ':'M','ऽ':"'"}
_DEV_VIRAMA = '्'
_DEV_NUKTA = {'क़':'k','ख़':'K','ग़':'g','ज़':'j','ड़':'q','ढ़':'Q','फ़':'P','य़':'y'}

def dev_to_slp1(s):
    """Minimal Devanagari->SLP1 (consonant carries inherent 'a' unless a virama
    or matra follows). Drops the Hindi nukta (q-dots) to its base consonant."""
    for a, b in (('क़','क'),('ख़','ख'),('ग़','ग'),('ज़','ज'),('ड़','ड'),('ढ़','ढ'),('फ़','फ'),('य़','य')):
        s = s.replace(a, b)
    out = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        if ch in _DEV_C:
            out.append(_DEV_C[ch]); i += 1
            if i < n and s[i] == _DEV_VIRAMA:
                i += 1
            elif i < n and s[i] in _DEV_M:
                out.append(_DEV_M[s[i]]); i += 1
            elif i < n and s[i] in _DEV_SIGN and s[i] != 'ऽ':
                out.append('a' + _DEV_SIGN[s[i]]); i += 1
            else:
                out.append('a')
        elif ch in _DEV_V:
            out.append(_DEV_V[ch]); i += 1
        elif ch in _DEV_SIGN:
            out.append(_DEV_SIGN[ch]); i += 1
        elif ch in _DEV_M:
            out.append(_DEV_M[ch]); i += 1
        else:
            i += 1   # drop avagraha-internal punctuation, latin, spaces
    return ''.join(out)

def is_devanagari(tok):
    return bool(tok) and all('ऀ' <= c <= 'ॿ' or c in '्ािीुूृॄॢॣेैोौंःँऽ़' for c in tok)

def to_stem(slp1):
    """Reduce an apte-hi *citation* key (nominative singular) to the bare stem
    PWG keys on. apte-hi prints े.g. अग्निः→'agniH', फलम्→'…am'; PWG keys 'agni',
    '…a'. Strip the nom-sg visarga and the neuter -am; leave fem -A/-I, consonant
    stems (rAjan) and already-bare stems untouched. Conservative — only the two
    endings that demonstrably differ, so it never collides distinct stems."""
    if not slp1:
        return slp1
    if slp1.endswith('H') and len(slp1) > 1:      # devaH→deva, agniH→agni, arTaH→arTa
        return slp1[:-1]
    if slp1.endswith('am') and len(slp1) > 2:     # Palam→Pala (neuter nom-sg)
        return slp1[:-1]
    return slp1

# Hindi part-of-speech markers seen in these sources (best-effort capture).
_POS = re.compile(r'(पुं|स्त्री|क्रि\.वि|क्रि|अव्य|वि|पु\.|न\.|न |भू\.क\.कृ|सर्व)')

def clean(s):
    return re.sub(r'\s+', ' ', s.replace('<br>', ' / ').replace('\t', ' | ')
                  .replace('"', '').strip(' /|')).strip()

def parse_entry(headline, defline):
    """One babylon block -> (slp1, primary_dev, pos, gloss) or None."""
    syns = [h.strip() for h in headline.split('|') if h.strip()]
    primary = next((h for h in syns if is_devanagari(h)), syns[0] if syns else '')
    slp1 = dev_to_slp1(primary)
    if not slp1 or not slp1[0].isalpha() or not slp1[:1].isascii():
        return None
    pos = ''
    if '\t' in defline:
        # apte-hi: [hw<br>pos] \t H1 \t - \t code \t [etym<br>gloss]
        fields = defline.split('\t')
        head = fields[0]
        m = _POS.search(head.split('<br>')[-1])
        pos = m.group(1).strip() if m else ''
        tail = fields[-1]
        gloss = tail.split('<br>', 1)[1] if '<br>' in tail else tail
    else:
        # vedic-rituals-hi: [pos<br> gloss]   (headword often repeated first)
        body = defline
        m = _POS.search(body.split('<br>')[0])
        pos = m.group(1).strip() if m else ''
        gloss = body.split('<br>', 1)[1] if '<br>' in body else body
    return slp1, primary, pos, clean(gloss)

def build(fname, code, attribution):
    path = os.path.join(SRC, fname)
    out_path = os.path.join(HERE, code + '.jsonl')
    if not os.path.exists(path):
        print('  SKIP %-18s (not found: %s)' % (code, path)); return 0
    n_blocks = n_out = n_nokey = 0
    with open(path, encoding='utf-8') as f:
        text = f.read()
    blocks = re.split(r'\r?\n\r?\n', text)
    with open(out_path, 'w', encoding='utf-8', newline='') as o:
        for blk in blocks:
            lines = [ln for ln in blk.split('\n') if ln.strip()]
            if len(lines) < 2 or lines[0].startswith('#'):
                continue
            n_blocks += 1
            rec = parse_entry(lines[0].strip(), ' '.join(lines[1:]).strip())
            if not rec:
                n_nokey += 1; continue
            slp1, dev, pos, gloss = rec
            if not gloss:
                n_nokey += 1; continue
            o.write(json.dumps({'source': code, 'slp1': slp1, 'stem': to_stem(slp1),
                                'dev': dev, 'pos': pos, 'gloss': gloss,
                                'attribution': attribution}, ensure_ascii=False) + '\n')
            n_out += 1
    print('%-18s <- %-26s blocks=%6d out=%6d no-key/empty=%5d'
          % (code, fname, n_blocks, n_out, n_nokey))
    return n_out

if __name__ == '__main__':
    if not os.path.isdir(SRC):
        sys.exit('babylon source dir not found: %s' % SRC)
    total = sum(build(f, c, a) for f, c, a in SOURCES)
    print('TOTAL keyed Hindi sense entries: %d' % total)
