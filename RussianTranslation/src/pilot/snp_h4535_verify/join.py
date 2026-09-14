#!/usr/bin/env python3
"""JOIN by L: pc + headword comparison yadisk vs csl-orig (H4535)."""
import json, re

y = {int(k): v for k, v in json.load(open('/var/folders/17/xycv_hps0w5_b67s84q43vr40000gp/T/opencode/h4535/verify-glm/yadisk_recs.json')).items()}
c = {int(k): v for k, v in json.load(open('/var/folders/17/xycv_hps0w5_b67s84q43vr40000gp/T/opencode/h4535/verify-glm/cslorig_recs.json')).items()}

only_y = sorted(set(y) - set(c)); only_c = sorted(set(c) - set(y))
print(f"only in yadisk: {only_y}; only in csl-orig: {only_c}")

pc_mism, hw_mism = [], []
for L in sorted(set(y) & set(c)):
    if y[L]['pc'] != c[L]['pc']:
        pc_mism.append((L, y[L]['pc'], c[L]['pc']))
    # yadisk key2 is SLP1 with §...§ display + key2; csl k1/k2 SLP1
    if y[L]['key2'] != c[L]['k1'] or y[L]['key2'] != c[L]['k2']:
        hw_mism.append((L, y[L]['key2'], c[L]['k1'], c[L]['k2']))

print(f"pc mismatches: {len(pc_mism)}")
for m in pc_mism[:20]: print("  ", m)
print(f"headword mismatches: {len(hw_mism)}")
for m in hw_mism[:20]: print("  ", m)
print(f"joined entries: {len(set(y) & set(c))}")
