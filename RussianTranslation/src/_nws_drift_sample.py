#!/usr/bin/env python
"""Sampled NWS-vs-csl-orig drift (first-pass D2). Every Nth scraped a-card."""
import os, sys, glob, json, collections
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
import dict_merge as dm, corpus_gate as cg
import _nws_drift as D

STEP = int(sys.argv[1]) if len(sys.argv)>1 else 20
OUT = D.OUT
files = sorted(f for f in glob.glob(os.path.join(OUT,'*.json'))
               if os.path.basename(f) not in D.CONTROL)
files = files[::STEP]
sch_idx, pw_idx = dm.index('sch'), dm.index('pw')
def joined(idx,k): return ' '.join('\n'.join(b[1:]) for b in idx.get(cg.form_key(k),[]))

n=0; sch=collections.Counter(); pw=collections.Counter(); sims=[]
changed=[]; missing=[]; pwlen=[]
for f in files:
    try: d=json.load(open(f,encoding='utf-8'))
    except Exception: continue
    k=d.get('key1');
    if not k: continue
    n+=1
    nws_sch,nws_pw=bool(d.get('sch')),bool(d.get('pw_len'))
    o_sch,o_pw=joined(sch_idx,k),joined(pw_idx,k)
    os_has,op_has=bool(o_sch.strip()),bool(o_pw.strip())
    sch[('both' if nws_sch and os_has else 'nws_only' if nws_sch else 'orig_only' if os_has else 'neither')]+=1
    pw[('both' if nws_pw and op_has else 'nws_only' if nws_pw else 'orig_only' if op_has else 'neither')]+=1
    if nws_sch and os_has:
        s=D.jaccard(D.tokens(d['sch']),D.tokens(o_sch)); sims.append(s)
        if s<0.5 and len(changed)<10: changed.append((k,round(s,2)))
    if nws_pw and op_has: pwlen.append((d['pw_len'],len(o_pw)))
    if os_has and not nws_sch and len(missing)<10: missing.append(k)

print(f"=== NWS drift vs csl-orig — SAMPLED every {STEP}th a-card ({n} cards) ===")
print("\n-- SCH (Schmidt) coverage --")
for kk in ('both','nws_only','orig_only','neither'):
    print("  %-9s %6d (%4.1f%%)"%(kk,sch[kk],100*sch[kk]/n))
if sims:
    b=collections.Counter()
    for s in sims:
        b['identical (>=.95)' if s>=.95 else 'minor (.8-.95)' if s>=.8 else 'moderate (.5-.8)' if s>=.5 else 'major (<.5)']+=1
    print(f"\n-- SCH content drift (Jaccard, {len(sims)} in-both) --")
    for lab in ('identical (>=.95)','minor (.8-.95)','moderate (.5-.8)','major (<.5)'):
        print("  %-18s %6d (%4.1f%%)"%(lab,b[lab],100*b[lab]/len(sims)))
    print("  mean Jaccard: %.3f"%(sum(sims)/len(sims)))
    print("  sample changed (key,sim):",changed)
print("\n-- PW (Boehtlingk) coverage --")
for kk in ('both','nws_only','orig_only','neither'):
    print("  %-9s %6d (%4.1f%%)"%(kk,pw[kk],100*pw[kk]/n))
if pwlen:
    big=sum(1 for a,b2 in pwlen if b2 and abs(a-b2)/max(b2,1)>0.5)
    print("  pw len |d|>50%% (coarse): %d/%d (%.1f%%)"%(big,len(pwlen),100*big/len(pwlen)))
print("\n  SCH orig_only sample (Cologne has, NWS lacks):",missing)
