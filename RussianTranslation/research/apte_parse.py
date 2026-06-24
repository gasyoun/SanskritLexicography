#-*- coding:utf-8 -*-
"""apte_parse.py — parse Apte Sanskrit-Hindi (.babylon) into an SLP1 root oracle + sidecar.

Resource (provided 2026-06-24): indic-dict/stardict-sanskrit .../apte-hi/apte-hi.babylon,
vendored (gitignored) at external/apte-hi.babylon. An independent Sanskrit-Hindi dictionary
(no S-H existed locally; only AP90 S-E + ApteES).

babylon record (blank-line separated): a headword line, then a data line of tab fields:
  f0 = headword<br>grammar      f1 = Hcode      f2 = parse (prefix-root, e.g. अभि-भू; '-' if none)
  f3 = POS tag (D=dhatu, NS=noun-subst, AV=avyaya, ...)   f4 = etymology<br>Hindi-gloss

Roles (all 4, per decision):
  (a) root oracle      — POS=D + empty parse -> primary dhatu; POS=D + parse -> prefixed verb
  (b) 3rd SPLIT/NESTED — the digitised babylon is a FLAT headword list => structurally SPLIT
  (c) Hindi gloss      — independent non-DE/EN sense cross-check (kept verbatim)
  (d) compound split   — noun etymology field (root+affix) [future]

Reuses sanskrit-util (Devanagari->IAST->SLP1) — no transcoder reinvention.

  python apte_parse.py demo            # BU family + stats + overlap with verbs01 roots
  python apte_parse.py write           # -> apte_roots.tsv (oracle) + apte_sidecar.tsv
"""
from __future__ import print_function
import os, sys, re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'WhitneyRoots', 'scripts'))
from sanskrit_util import to_slp1, deva_to_iast            # noqa: E402

BABYLON = os.path.join(HERE, 'external', 'apte-hi.babylon')
VERBS01_MAP = os.path.join(HERE, '..', '..', '..', 'PWG', 'verbs01', 'pwg_verb_filter_map.txt')


def slp1(dev):
    try:
        return to_slp1(deva_to_iast(dev))
    except Exception:
        return ''


def records(path):
    """Yield parsed dicts from the babylon file."""
    block = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('#'):
                continue
            if line.strip() == '':
                if block:
                    r = parse_block(block)
                    if r:
                        yield r
                    block = []
            else:
                block.append(line)
    if block:
        r = parse_block(block)
        if r:
            yield r


def parse_block(block):
    data = next((ln for ln in block if '\t' in ln), None)
    if not data:
        return None
    c = data.split('\t')
    if len(c) < 5:
        return None
    hw_dev = c[0].split('<br>')[0].strip().strip('"')
    parse_dev = c[2].strip()
    pos = c[3].strip()
    etym, _, gloss = c[4].partition('<br>')
    gloss = gloss.strip().strip('"')
    hw = slp1(hw_dev)
    if not hw:
        return None
    parts = []
    if parse_dev and parse_dev != '-':
        parts = [slp1(p) for p in parse_dev.split('-') if p]
    return {'hw_dev': hw_dev, 'hw': hw, 'pos': pos, 'parse_parts': parts,
            'etym': etym.strip(), 'gloss': gloss}


def load_verbs01_roots():
    s = set()
    try:
        with open(VERBS01_MAP, encoding='utf-8') as f:
            for line in f:
                m = re.search(r'k1=([^,]+),', line)
                if m:
                    s.add(m.group(1))
    except FileNotFoundError:
        pass
    return s


def build():
    roots, prefixed, sidecar = {}, {}, {}
    n = 0
    for r in records(BABYLON):
        n += 1
        hw = r['hw']
        if hw not in sidecar:                       # first sense wins for the sidecar gloss
            sidecar[hw] = r
        if r['pos'] == 'D':                         # dhatu
            if r['parse_parts']:                    # prefixed verb: [upa..., root]
                prefixed.setdefault(hw, r['parse_parts'])
            else:
                roots.setdefault(hw, r)             # primary dhatu
    return n, roots, prefixed, sidecar


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'demo'
    if not os.path.exists(BABYLON):
        print('missing %s — fetch apte-hi.babylon from indic-dict/stardict-sanskrit' % BABYLON)
        return
    n, roots, prefixed, sidecar = build()
    v01 = load_verbs01_roots()
    overlap = set(roots) & v01
    print('Apte S-H: %d sense-records, %d distinct headwords' % (n, len(sidecar)))
    print('  primary dhatus (root oracle): %d' % len(roots))
    print('  prefixed verbs (parse split): %d' % len(prefixed))
    print('  verbs01 PWG roots: %d ; Apte∩verbs01: %d ; Apte-only roots: %d'
          % (len(v01), len(overlap), len(set(roots) - v01)))
    if cmd == 'write':
        with open(os.path.join(HERE, 'apte_roots.tsv'), 'w', encoding='utf-8') as f:
            f.write('root_slp1\thw_dev\tin_verbs01\thindi_gloss\n')
            for hw in sorted(roots):
                f.write('%s\t%s\t%s\t%s\n' % (hw, roots[hw]['hw_dev'],
                        'Y' if hw in v01 else 'N', roots[hw]['gloss'][:80]))
        with open(os.path.join(HERE, 'apte_sidecar.tsv'), 'w', encoding='utf-8') as f:
            f.write('hw_slp1\tpos\tparse\thindi_gloss\n')
            for hw in sorted(sidecar):
                r = sidecar[hw]
                f.write('%s\t%s\t%s\t%s\n' % (hw, r['pos'],
                        '+'.join(r['parse_parts']), r['gloss'][:100]))
        print('  wrote apte_roots.tsv (%d) + apte_sidecar.tsv (%d)' % (len(roots), len(sidecar)))
    print('  BU-family sample:')
    for kw in ('BU', 'anuBU', 'aBiBU', 'praBU', 'saMBU'):
        r = sidecar.get(kw)
        if r:
            print('    %-8s pos=%-3s parse=%-10s %s'
                  % (kw, r['pos'], '+'.join(r['parse_parts']) or '-', r['gloss'][:48]))
        else:
            print('    %-8s (not found)' % kw)


if __name__ == '__main__':
    main()
