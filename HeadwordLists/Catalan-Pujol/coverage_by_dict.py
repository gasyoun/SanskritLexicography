import sys, re, os, unicodedata
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su

ORIG=os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
CAT=os.path.join(HERE, "61267-Sanskrit-Catalan-Words-List.txt")

def ascii_clean(k):
    k=unicodedata.normalize('NFD',k)
    return ''.join(c for c in k if ord(c)<128 and not unicodedata.combining(c))

def norm_cat(w):
    w=re.sub(r'\([^)]*\)','',w).strip().strip(' ,;')
    w=w.replace('√','').replace('˚','')
    w=re.sub(r'\d+$','',w).strip()
    w=unicodedata.normalize('NFC',w).replace('-','')
    try: slp=su.to_slp1(w)
    except Exception: return ''
    if not slp: return ''
    return ascii_clean(su.strip_slp1_accents(slp))

def load_k1(d):
    path=os.path.join(ORIG,d,d+'.txt'); keys=set()
    if not os.path.exists(path): return keys
    bs=chr(92)
    for line in open(path,encoding='utf-8'):
        m=re.search(r'<k1>([^<]+)',line)
        if m:
            k=su.strip_slp1_accents(m.group(1).strip()).replace('˚','').replace('/','').replace(bs,'')
            keys.add(ascii_clean(k))
    return keys

cat=set(); nroot=0; naccent=0
for line in open(CAT,encoding='utf-8-sig'):
    hw=line.rstrip('\n')
    if not hw.strip(): continue
    if '√' in hw: nroot+=1
    nfd=unicodedata.normalize('NFD',hw)
    if re.search(r'[aeiouāīūṛṝ]́', nfd) or re.search(r'[aeiouāīūṛṝ]̀', nfd): naccent+=1
    s=norm_cat(hw)
    if s: cat.add(s)
print("unique cat keys:",len(cat),"  root entries:",nroot,"  vowel-accented entries:",naccent)

dicts={}
for d in ['mw','pw','pwg','mw72','ap90','cae','yat','wil','bur','gra','bor','vcp','shs','ben','mwe']:
    k=load_k1(d)
    if k: dicts[d]=k
covered=set(); order=[]; remaining=set(dicts)
while remaining:
    best=max(remaining,key=lambda d:len((cat&dicts[d])-covered))
    add=len((cat&dicts[best])-covered)
    if add==0: break
    covered|=cat&dicts[best]; order.append((best,add,len(covered),100*len(covered)/len(cat))); remaining.discard(best)
print("\nGreedy marginal coverage of the Catalan list:")
print("%-6s %8s %10s %8s"%("dict","adds","cumul","cum%"))
for d,a,c,p in order: print("%-6s %8d %10d %7.1f%%"%(d,a,c,p))
print("\nUncovered by all listed dicts:",len(cat)-len(covered), "(%.1f%%)"%(100-100*len(covered)/len(cat)))
