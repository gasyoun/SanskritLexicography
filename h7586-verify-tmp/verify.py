# -*- coding: utf-8 -*-
# H7586 independent verification: Vacaspatyam vol V n->p boundary claims (PR #2492)
import json, gzip, io, sys
from statistics import mean

TDIR = 'h7586-verify-tmp/'
TRANS = str.maketrans('०१२३४५६७८९', '0123456789')

meta = json.load(open(TDIR + 'v5_pages.json', encoding='utf-8'))
pages = meta['pages']
idx = json.load(gzip.open(TDIR + 'v5_pgidx.json.gz', 'rt', encoding='utf-8'))
t = gzip.open(TDIR + 'v5_search.txt.gz', 'rt', encoding='utf-8').read()

# idx has 978 rows; trailing extras must be empty (zero-length at EOF) -> real = first len(pages)
extra = idx[len(pages):]
assert all(iv[0] == iv[1] for iv in extra), extra
idx = idx[:len(pages)]
assert len(pages) == len(idx), (len(pages), len(idx))
print('text length (chars):', len(t))

# per-page stats keyed by printed page number
stats = {}  # pn -> dict(leaf, L, D)
dups = []
for k, (p, iv) in enumerate(zip(pages, idx)):
    raw = p['pageNumber']
    pn = raw.translate(TRANS).strip() if isinstance(raw, str) else ''
    try:
        pn = int(pn)
    except ValueError:
        continue
    s, e = iv[0], iv[1]
    seg = t[s:e]
    rec = {'leaf': p['leafNum'], 'L': len(seg), 'D': seg.count('\u0964')}
    if pn in stats:
        dups.append(pn)
    stats[pn] = rec
print('pages with parseable pageNumber:', len(stats), '| duplicate pns:', dups[:10])

# ---- CLAIM 2a: strict +1 continuity over 4100..4260, zero gaps ----
seq = sorted(pn for pn in stats if 4100 <= pn <= 4260)
missing = [n for n in range(4100, 4261) if n not in stats]
gaps = [(a, b) for a, b in zip(seq, seq[1:]) if b - a != 1]
print('in-range pages found:', len(seq), 'range first/last:', seq[0], seq[-1])
print('missing in 4100..4260:', missing)
print('non-+1 steps:', gaps)

# ---- CLAIM 2b: window means ----
w1 = [stats[n] for n in range(4100, 4177)]
w2 = [stats[n] for n in range(4177, 4261)]
mL1, mD1 = mean(r['L'] for r in w1), mean(r['D'] for r in w1)
mL2, mD2 = mean(r['L'] for r in w2), mean(r['D'] for r in w2)
print('W1 4100-4176 n=%d: meanL=%.1f meanDanda=%.2f' % (len(w1), mL1, mD1))
print('W2 4177-4260 n=%d: meanL=%.1f meanDanda=%.2f' % (len(w2), mL2, mD2))

# ---- CLAIM 1: heads of printed 4176 / 4177 ----
def seg_of(pn):
    for k, p in enumerate(pages):
        raw = p['pageNumber']
        q = (raw.translate(TRANS).strip() if isinstance(raw, str) else '')
        try:
            q = int(q)
        except ValueError:
            continue
        if q == pn:
            return t[idx[k][0]:idx[k][1]]
    raise KeyError(pn)

for pn in (4176, 4177):
    seg = seg_of(pn)
    print('--- printed p.%d head (first 200 chars):' % pn)
    print(repr(seg[:200]))
    print('    head 150 zone for running-head terms:', {w: seg[:150].find(w) for w in ('\u092a\u0915\u094d\u0924\u093f', '\u092a\u0919\u094d\u0915', '\u092a\u091a', '\u0928\u094d\u092f\u093e\u0938', '\u0928\u094d\u092f')})

# ---- CLAIM 1b: pakti/paGka/paca in running-head zone for printed 4178..4182 ----
for pn in range(4178, 4183):
    seg = seg_of(pn)
    zone = seg[:150]
    hits = {w: zone.find(w) for w in ('\u092a\u0915\u094d\u0924\u093f', '\u092a\u0919\u094d\u0915', '\u092a\u091a') if zone.find(w) >= 0}
    print('p.%d running-head hits:' % pn, hits, '| head40:', repr(zone[:40]))

# ---- CLAIM 1c: context — last n-words on 4176 tail, first p-words on 4177 ----
t4176, t4177 = seg_of(4176), seg_of(4177)
print('4176 tail 160:', repr(t4176[-160:]))
print('4177 head 300:', repr(t4177[:300]))
