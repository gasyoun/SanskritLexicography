import sys, re, os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, r"C:/Users/user/Documents/GitHub/sanskrit-util/py")
import sanskrit_util as su

CAT = r"C:/Users/user/Documents/GitHub/CORRECTIONS/61267-Sanskrit-Catalan-Words-List.txt"
ORIG = r"C:/Users/user/Documents/GitHub/csl-orig/v02"

import unicodedata
def norm_cat(w, joinhyphen=True):
    w = re.sub(r'\([^)]*\)','', w)        # drop parentheticals
    w = w.strip().strip(' ,;')
    is_root = '√' in w
    w = w.replace('√','').replace('˚','')
    w = re.sub(r'\d+$','', w).strip()
    w = unicodedata.normalize('NFC', w)   # keep precomposed ś etc.
    if joinhyphen:
        w = w.replace('-','')   # join compound members / prefix+root
    else:
        w = w.strip('-')
    try: slp = su.to_slp1(w)
    except Exception: slp = ''
    if slp:
        slp = su.strip_slp1_accents(slp)
        # drop any residual combining Vedic accent left on the SLP1 (ascii) output
        slp = unicodedata.normalize('NFD', slp)
        slp = ''.join(c for c in slp if ord(c) < 128 and not unicodedata.combining(c))
    return slp, is_root

def load_k1(dictcode):
    path = os.path.join(ORIG, dictcode, dictcode + '.txt')
    keys = set()
    if not os.path.exists(path): return keys
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = re.search(r'<k1>([^<]+)', line)
            if m:
                k = su.strip_slp1_accents(m.group(1).strip()).replace('˚','').replace('/','').replace('\\','')
                keys.add(k)
    return keys

items=[]
with open(CAT,encoding='utf-8-sig') as f:
    for line in f:
        hw=line.rstrip('\n')
        if not hw.strip(): continue
        slp,isr=norm_cat(hw)
        items.append((hw,slp,isr))

mw=load_k1('mw'); pw=load_k1('pw'); pwg=load_k1('pwg'); mw72=load_k1('mw72')
union3=mw|pw|pwg
union_all = union3|mw72
for d in ['ap90','cae','yat','wil','bur','gra']:
    union_all |= load_k1(d)

valid=[(h,s) for h,s,r in items if s]
print("total lines:",len(items),"  valid keys:",len(valid))
print("matched in MW: %.1f%%" % (100*sum(1 for h,s in valid if s in mw)/len(valid)))
print("matched in union(mw,pw,pwg): %.1f%%" % (100*sum(1 for h,s in valid if s in union3)/len(valid)))
print("matched in union(all 10 dicts): %.1f%%" % (100*sum(1 for h,s in valid if s in union_all)/len(valid)))

unm=[(h,s) for h,s in valid if s not in union_all]
print("\nUNMATCHED vs all dicts:", len(unm))
single=[(h,s) for h,s in valid if '-' not in h.strip(' ,').rstrip('-').lstrip('√')]
comp=[(h,s) for h,s in valid if '-' in h.strip(' ,').rstrip('-').lstrip('√')]
print("single non-compound: %d, in MW %.1f%%, in all %.1f%%" % (len(single),100*sum(1 for h,s in single if s in mw)/len(single),100*sum(1 for h,s in single if s in union_all)/len(single)))
print("compound (has -): %d, in MW %.1f%%, in all %.1f%%" % (len(comp),100*sum(1 for h,s in comp if s in mw)/max(1,len(comp)),100*sum(1 for h,s in comp if s in union_all)/max(1,len(comp))))
print("\n--- 30 unmatched spread ---")
step=max(1,len(unm)//30)
for hw,slp in unm[::step][:30]:
    print("%-30r -> %s" % (hw,slp))
