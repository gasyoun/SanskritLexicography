#!/usr/bin/env python3
"""Independent verifier scanner for csl-orig v02/snp/snp.txt (H4535)."""
import re, sys, json

path = sys.argv[1]
lines = open(path, encoding='utf-8').read().splitlines()

# structure census
meta = re.compile(r'^<L>(\d+)<pc>([^<]*)<k1>([^<]*)<k2>([^<]*)$')
lend = sum(1 for l in lines if l.startswith('<LEND>'))
nl = sum(1 for l in lines if l.startswith('<L>'))
print(f"^<L> meta lines: {nl}; ^<LEND>: {lend}")

# parse meta lines; be permissive then strict
recs = {}
odd = []
for l in lines:
    if not l.startswith('<L>'): continue
    m = meta.match(l)
    if not m:
        odd.append(l[:120]); continue
    L = int(m.group(1))
    if L in recs: odd.append(f"dup L={L}")
    recs[L] = {'pc': m.group(2), 'k1': m.group(3), 'k2': m.group(4)}
print(f"parsed meta records: {len(recs)}; odd lines: {len(odd)}")
for o in odd[:5]: print("  ODD:", o)

Ls = sorted(recs)
gaps = sorted(set(range(1, len(Ls)+1)) - set(Ls)); extras = sorted(set(Ls) - set(range(1, len(Ls)+1)))
print(f"L range {Ls[0]}..{Ls[-1]}; gaps {gaps}; extras {extras}")

# k1 == k2 check (SLP1 equality)
mism = [(L, r['k1'], r['k2']) for L, r in recs.items() if r['k1'] != r['k2']]
print(f"k1!=k2 mismatches: {len(mism)}")
for m in mism[:10]: print("  ", m)

# k2_2 (IAST?) sanity just to record
json.dump({str(k): v for k, v in recs.items()}, open('/var/folders/17/xycv_hps0w5_b67s84q43vr40000gp/T/opencode/h4535/verify-glm/cslorig_recs.json', 'w'))
print("saved cslorig_recs.json")

# find body span for each L (lines between <L>.. and <LEND>) for later folding
spans = {}
cur = None; buf = []
for l in lines:
    if l.startswith('<L>'):
        m = re.match(r'^<L>(\d+)<', l)
        cur = int(m.group(1)); buf = [l]
    elif l.startswith('<LEND>'):
        if cur is not None:
            buf.append(l); spans.setdefault(cur, []).append(list(buf))
        cur = None; buf = []
    elif cur is not None:
        buf.append(l)
multi = {L: v for L, v in spans.items() if len(v) > 1}
print(f"entries with >1 span per L: {multi}")
json.dump({str(k): ['\n'.join(s) for s in v] for k, v in spans.items()}, open('/var/folders/17/xycv_hps0w5_b67s84q43vr40000gp/T/opencode/h4535/verify-glm/cslorig_spans.json', 'w'))
print("saved cslorig_spans.json")
