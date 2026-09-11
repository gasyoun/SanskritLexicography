#!/usr/bin/env python3
"""Body parity fold-diff (H4535). Fold = strip tags + [Page...] markers,
NFKD -> drop combining marks -> keep letters only -> lowercase."""
import json, re, unicodedata

TAG = re.compile(r'<[^>]*>')
PAGE = re.compile(r'\[Page[^]]*\]')

def fold(s):
    s = TAG.sub('', s)
    s = PAGE.sub('', s)
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = ''.join(ch for ch in s if ch.isalpha())
    return s.lower()

y = {int(k): v for k, v in json.load(open('/var/folders/17/xycv_hps0w5_b67s84q43vr40000gp/T/opencode/h4535/verify-glm/yadisk_recs.json')).items()}
spans = json.load(open('/var/folders/17/xycv_hps0w5_b67s84q43vr40000gp/T/opencode/h4535/verify-glm/cslorig_spans.json'))

def csl_body(L):
    parts = spans[str(L)]
    # drop the meta line and <LEND> line
    lines = parts[0].splitlines()
    lines = [l for l in lines if not l.startswith('<L>') and not l.startswith('<LEND>')]
    return '\n'.join(lines)

diffs, equals = [], 0
for L in sorted(y):
    yf = fold(y[L]['body'])
    cf = fold(csl_body(L))
    if yf == cf:
        equals += 1
    else:
        diffs.append(L)
print(f"folded equal: {equals}/453; differing Ls: {diffs}")

for L in diffs:
    yf, cf = fold(y[L]['body']), fold(csl_body(L))
    print(f"\n--- L{L} (len yadisk={len(yf)}, csl={len(cf)}, delta={len(cf)-len(yf)}) ---")
    # locate first divergence
    i = 0
    while i < min(len(yf), len(cf)) and yf[i] == cf[i]:
        i += 1
    lo = max(0, i-60); hi = i+80
    print(f"yadisk @{i}: ...{yf[lo:hi]}...")
    print(f"csl    @{i}: ...{cf[lo:hi]}...")
    # common suffix length
    j = 0
    while j < min(len(yf), len(cf)) and yf[-1-j] == cf[-1-j]:
        j += 1
    print(f"common prefix={i}, common suffix={j}, yadisk-mid={repr(yf[i:len(yf)-j])[:200]}, csl-mid={repr(cf[i:len(cf)-j])[:300]}")
