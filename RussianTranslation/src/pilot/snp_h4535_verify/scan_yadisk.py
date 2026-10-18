#!/usr/bin/env python3
"""Independent verifier scanner for yadisk 1974-SNP/snp.txt (H4535).
Written from scratch; does not reuse executor code."""
import re, sys, json, unicodedata
from collections import Counter

path = sys.argv[1]
raw = open(path, 'rb').read()
text = raw.decode('utf-8')

# --- entry split on <H1> ... </H1> ---
entries = re.findall(r'<H1>(.*?)</H1>', text, re.S)
print(f"H1 entry count: {len(entries)}")

recs = {}
problems = []
for i, ent in enumerate(entries):
    mh = re.search(r'<h>(.*?)</h>', ent, re.S)
    mk2 = re.search(r'<key2>(.*?)</key2>', ent, re.S)
    mb = re.search(r'<body>(.*?)</body>', ent, re.S)
    mt = re.search(r'<tail><L>(\d+)</L><pc>([^<]*)</pc></tail>', ent, re.S)
    if not (mh and mk2 and mb and mt):
        problems.append(f"entry#{i+1}: missing one of h/key2/body/tail: h={bool(mh)} key2={bool(mk2)} body={bool(mb)} tail={bool(mt)}")
        continue
    L = int(mt.group(1)); pc = mt.group(2); k2 = mk2.group(1)
    if L in recs:
        problems.append(f"duplicate L={L}")
    recs[L] = {'pc': pc, 'key2': k2, 'body': mb.group(1), 'h': mh.group(1), 'raw': ent}

# L range checks
Ls = sorted(recs)
print(f"L range: {Ls[0]}..{Ls[-1]}, n={len(Ls)}, unique={len(set(Ls))}")
expected = set(range(1, len(entries)+1))
gaps = sorted(expected - set(Ls)); extras = sorted(set(Ls) - expected)
print(f"gaps in 1..N: {gaps}; extras: {extras}")
print(f"scanner problems: {problems if problems else 'none'}")

# --- tag balance ---
tags = Counter()
for pat in [r'<H1>', r'</H1>', r'<h>', r'</h>', r'<key2>', r'</key2>', r'<body>', r'</body>']:
    tags[pat] = len(re.findall(re.escape(pat), text))
print("tag counts:", dict(tags))
op = len(re.findall(r'<i>', text)); cl = len(re.findall(r'</i>', text))
print(f"<i> pairs: open={op} close={cl} equal={op==cl}")

# check nothing outside H1 entries (trailing content)
outside = re.sub(r'<H1>.*?</H1>', '', text, flags=re.S).strip()
print(f"content outside <H1> blocks: {len(outside)} chars {repr(outside[:80])}")

json.dump({str(k): v for k, v in recs.items()}, open('/var/folders/17/xycv_hps0w5_b67s84q43vr40000gp/T/opencode/h4535/verify-glm/yadisk_recs.json', 'w'))
print("saved yadisk_recs.json")
