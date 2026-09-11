#!/usr/bin/env python3
"""Containment test: any yadisk content ABSENT from csl-orig (H4535 adversarial).
Per entry, align folded letter streams with difflib; 'delete' opcodes =
letters present in yadisk but missing from csl at that alignment."""
import json, re, unicodedata, difflib

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
    lines = spans[str(L)][0].splitlines()
    return '\n'.join(l for l in lines if not l.startswith('<L>') and not l.startswith('<LEND>'))

loss_entries = []
for L in sorted(y):
    yf, cf = fold(y[L]['body']), fold(csl_body(L))
    sm = difflib.SequenceMatcher(None, yf, cf, autojunk=False)
    deletes, inserts, replaces = [], [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'delete': deletes.append(yf[i1:i2])
        elif op == 'insert': inserts.append(cf[j1:j2])
        elif op == 'replace': replaces.append((yf[i1:i2], cf[j1:j2]))
    # 'replace' with letter->letter substitutions = potential lost+gained pairs
    real_del = [d for d in deletes if d.strip()]
    real_rep = [r for r in replaces if r[0].strip()]
    if real_del or real_rep:
        loss_entries.append((L, real_del, real_rep, inserts))

if not loss_entries:
    print("CONTAINMENT CLEAN: no yadisk letter content missing from csl-orig in any of the 453 entries (delete/replace opcodes empty).")
else:
    print(f"{len(loss_entries)} entries with yadisk-side content not in csl:")
    for L, d, r, ins in loss_entries:
        print(f"  L{L}: deletes={d[:5]} replaces={r[:5]} (csl inserts={ins[:5]})")
