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


DEVA_CHAIN = re.compile(r'[ऀ-ॿ]+(?:\+[ऀ-ॿ]+)+')


def etym_chain(etym):
    """Extract the [root, affix1, affix2, ...] Pāṇinian derivation chain from the
    etymology field (अंश्+ण्वुल् -> ['अंश्','ण्वुल्']; final element = the deriving suffix)."""
    m = DEVA_CHAIN.search(re.sub(r'<[^>]*>', '', etym or ''))
    return m.group(0).split('+') if m else None


def _compute():
    """-> (upa: upasarga->roots, suf: pratyaya_deva->roots, mwsuf: surface->count, aff_iast)."""
    upa, suf, aff_iast = {}, {}, {}
    for r in records(BABYLON):
        if r['pos'] == 'D' and len(r['parse_parts']) >= 2:      # prefixed verb
            root = r['parse_parts'][-1]
            for u in r['parse_parts'][:-1]:
                upa.setdefault(u, set()).add(root)
        parts = etym_chain(r['etym'])                            # nominal derivation
        if parts and len(parts) >= 2:
            aff = parts[-1]                                      # the deriving (outermost) suffix
            try:
                aff_iast[aff] = deva_to_iast(aff)
            except Exception:
                aff_iast[aff] = aff
            suf.setdefault(aff, set()).add(slp1(parts[0]))
    mwsuf = {}                                  # MW surface-suffix counts (complementary lens)
    try:
        import mw_deriv
        for recs in mw_deriv.load().values():
            b = mw_deriv.best(recs)
            if b and b['method'].startswith('wsfx'):
                s = b['method'].split(':')[1] if ':' in b['method'] else b['method']
                mwsuf[s] = mwsuf.get(s, 0) + 1
    except Exception as e:
        print('  (MW wsfx cross unavailable: %s)' % e)
    return upa, suf, mwsuf, aff_iast


def crossmap():
    """Join the two suffix lenses through affix_map.tsv (pratyaya <-> surface <-> MW wsfx).
    Shows how Apte's formation-affix names line up with MW's surface morphemes, and where
    each lens has coverage the other lacks."""
    upa, suf, mwsuf, aff_iast = _compute()
    rows = []
    with open(os.path.join(HERE, 'affix_map.tsv'), encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            c = line.rstrip('\n').split('\t')
            if len(c) < 7:
                continue
            surf_i, surf_d, prat_i, prat_d, mwk, kind, fn = c[:7]
            apte = sum(len(suf.get(p, set())) for p in prat_d.split('|'))
            mw = sum(mwsuf.get(k, 0) for k in mwk.split('|') if k != '-')
            rows.append((surf_i, prat_i, prat_d.split('|')[0], mwk, kind, fn, apte, mw))
    print('Affix map — Pāṇinian pratyaya <-> surface suffix <-> MW wsfx '
          '(Apte = #distinct roots; MW = #headwords):')
    print('  %-7s %-9s %-9s %-8s %-9s %6s %6s  %s'
          % ('surf', 'pratyaya', 'देव', 'mw_wsfx', 'kind', 'Apte', 'MW', 'function'))
    for surf_i, prat_i, prat_d, mwk, kind, fn, apte, mw in rows:
        print('  -%-6s %-9s %-9s %-8s %-9s %6d %6d  %s'
              % (surf_i, prat_i, prat_d, mwk, kind, apte, mw, fn))
    krt = [r for r in rows if 'kṛt' in r[4]]
    print('\n  Reading: the two lenses OVERLAP on transparent taddhita (-tva/-tā/-vat/-tara…),')
    print('  but Apte alone covers the kṛt formation affixes (kta/ghañ/lyuṭ/ṇvul…, MW wsfx="-"')
    print('  because those are lexicalised headwords); and MW counts ≫ Apte on -tva/-tā/-vat')
    print('  (Apte rarely cites a transparent taddhita; MW flags every one).')
    print('  kṛt rows with no MW-wsfx counterpart: %d' % sum(1 for r in krt if r[3] == '-'))


def productivity():
    """Two affix-productivity lenses: upasarga×root + kṛt/taddhita-suffix×root (Apte),
    cross-listed with MWderivations' wsfx surface-suffix counts."""
    upa, suf, mwsuf, aff_iast = _compute()
    up = sorted(upa.items(), key=lambda kv: -len(kv[1]))
    sf = sorted(suf.items(), key=lambda kv: -len(kv[1]))
    mw = sorted(mwsuf.items(), key=lambda kv: -kv[1])
    print('Apte productivity:  %d upasargas, %d kṛt/taddhita suffixes' % (len(up), len(sf)))
    print('  top upasargas (by # distinct roots):')
    for u, roots in up[:15]:
        print('    %-8s %4d roots' % (u, len(roots)))
    print('  top Apte suffixes (pratyaya, by # distinct roots):')
    for a, roots in sf[:15]:
        print('    %-10s %-7s %4d roots' % (a, aff_iast.get(a, ''), len(roots)))
    if mw:
        print('  top MW surface-suffixes (wsfx, by count) — complementary lens:')
        for s, c in mw[:12]:
            print('    %-8s %5d' % (s, c))
    with open(os.path.join(HERE, 'apte_productivity.tsv'), 'w', encoding='utf-8') as f:
        f.write('kind\taffix\tiast\tn_distinct_roots\n')
        for u, roots in up:
            f.write('upasarga\t%s\t\t%d\n' % (u, len(roots)))
        for a, roots in sf:
            f.write('suffix\t%s\t%s\t%d\n' % (a, aff_iast.get(a, ''), len(roots)))
    print('  wrote apte_productivity.tsv (%d upasargas + %d suffixes)' % (len(up), len(sf)))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'demo'
    if cmd in ('productivity', 'crossmap'):
        if not os.path.exists(BABYLON):
            print('missing %s' % BABYLON); return
        (crossmap if cmd == 'crossmap' else productivity)(); return
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
