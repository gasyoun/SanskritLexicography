"""Scan the full scraped NWS corpus for HIGH-PRECISION source-data defects
(website-fixable), independent of owner-attribution.

Excess CLOSING parens are excluded as a known NWS convention (enumerated senses
`1) ... 2) ...` add lone `)`). The real-defect direction is excess OPENING
parens (the vṛtrakhādá signature) and unbalanced editorial brackets.

Run: python _nws_defect_scan.py
"""
import json, os, sys, glob, re
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

NWS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pilot', 'nws')

buckets = {
    'excess_open_paren':   [],   # count('(') > count(')')  — vṛtrakhādá direction
    'double_open_paren':   [],   # "((" / "( ("
    'unbalanced_bracket':  [],   # count('[') != count(']')
    'cross_ref_garble':    [],   # "(s. (" / "(s.v. (" — the vṛtrakhādá cross-ref shape
    'replacement_char':    [],   # mojibake U+FFFD
}

def snip(t, needle=None, w=55):
    if needle:
        i = t.find(needle)
        if i >= 0:
            return t[max(0, i-w):i+w]
    return t[:2*w]

CROSS = re.compile(r'\(\s*s\.?(?:v\.?)?\s+\(')   # ( s. (   or  ( s.v. (
DBL   = re.compile(r'\(\s*\(')

n = 0
for path in glob.iglob(os.path.join(NWS_DIR, '*.json')):
    base = os.path.basename(path)
    if base.startswith('_keys') or base.startswith('_nws'):
        continue
    try:
        d = json.load(open(path, encoding='utf-8'))
    except Exception:
        continue
    t = d.get('nws') or ''
    if not t:
        continue
    n += 1
    k1 = d.get('key1', ''); ia = d.get('iast', '')
    op, cl = t.count('('), t.count(')')

    if op > cl:
        buckets['excess_open_paren'].append((k1, ia, op - cl, snip(t)))
    if DBL.search(t):
        buckets['double_open_paren'].append((k1, ia, 0, snip(t, '(')))
    if t.count('[') != t.count(']'):
        buckets['unbalanced_bracket'].append((k1, ia, t.count('[') - t.count(']'), snip(t)))
    m = CROSS.search(t)
    if m:
        buckets['cross_ref_garble'].append((k1, ia, 0, snip(t, m.group(0))))
    if '�' in t:
        buckets['replacement_char'].append((k1, ia, 0, snip(t, '�')))

print('scanned NWS-content entries:', n)
print()
for name, hits in buckets.items():
    print('=== %s : %d ===' % (name, len(hits)))
    for k1, ia, delta, s in hits[:40]:
        d = ' (+%d)' % delta if delta else ''
        print('  [%s | %s]%s  …%s…' % (k1, ia, d, s.replace('\n', ' ')))
    if len(hits) > 40:
        print('  … and %d more' % (len(hits) - 40))
    print()
