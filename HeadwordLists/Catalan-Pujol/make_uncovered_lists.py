import sys, re, os, unicodedata
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
# Repo-relative paths. Override the two deps with env vars if your clone differs.
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su

ORIG=os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
CAT=os.path.join(HERE, "61267-Sanskrit-Catalan-Words-List.txt")
OUT=os.path.join(HERE, "Catalan-uncovered-by-CDSL.txt")

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

# union of k1 across ALL dict dirs in csl-orig
allkeys=set(); ndicts=0
bs=chr(92)
for d in sorted(os.listdir(ORIG)):
    path=os.path.join(ORIG,d,d+'.txt')
    if not os.path.isfile(path): continue
    ndicts+=1
    for line in open(path,encoding='utf-8'):
        m=re.search(r'<k1>([^<]+)',line)
        if m:
            k=su.strip_slp1_accents(m.group(1).strip()).replace('˚','').replace('/','').replace(bs,'')
            allkeys.add(ascii_clean(k))
print("CDSL dicts scanned:",ndicts,"  union k1 keys:",len(allkeys))

# map normalized cat key -> original headwords (preserve first occurrence order)
from collections import OrderedDict
keymap=OrderedDict()
total=0
for line in open(CAT,encoding='utf-8-sig'):
    hw=line.rstrip('\n')
    if not hw.strip(): continue
    total+=1
    s=norm_cat(hw)
    if not s: continue
    keymap.setdefault(s,[]).append(hw.strip())

uncovered=[(k,hws) for k,hws in keymap.items() if k not in allkeys]
print("total lines:",total,"  unique keys:",len(keymap))
print("uncovered keys:",len(uncovered))

# categorize originals (flatten — one row per original headword)
def categorize(hw, key):
    h=hw.strip().strip(' ,;')
    body=re.sub(r'\([^)]*\)','',h)
    has_root='√' in body
    n_hyph=body.replace('√','').strip('-').count('-')
    # stray/suspect chars
    if re.search(r'[•·∙]', h) or re.search(r'[^\sA-Za-z0-9√˚\-,;ḥṃṁṅñṭḍṇśṣĀ-ɏā-ūṛṝḷḹáàéíóúäöǜ-ͯ]', h):
        return 'suspect-char'
    if has_root and n_hyph>=1:
        return 'prefixed-root'
    if has_root:
        return 'root'
    if n_hyph>=2:
        return 'long-compound(3+)'
    if n_hyph==1:
        return 'compound(2)'
    return 'simple'

from collections import Counter
cat_counter=Counter()
rows=[]
for key,hws in uncovered:
    for hw in hws:
        c=categorize(hw,key)
        cat_counter[c]+=1
        rows.append((hw,key,c))

print("\nCategory breakdown of uncovered headwords:")
for c,n in cat_counter.most_common():
    print("  %-18s %5d"%(c,n))

# write full list grouped by category
with open(OUT,'w',encoding='utf-8') as f:
    f.write("# Catalan dictionary headwords NOT found in any CDSL dictionary\n")
    f.write("# (accent- and compound-insensitive k1 match against all %d CDSL dicts in csl-orig/v02)\n"%ndicts)
    f.write("# total uncovered headwords: %d  (unique normalized keys: %d)\n\n"%(len(rows),len(uncovered)))
    order=['suspect-char','simple','compound(2)','long-compound(3+)','root','prefixed-root']
    seen_order=[c for c in order if c in cat_counter]+[c for c in cat_counter if c not in order]
    bykey={}
    for hw,key,c in rows: bykey.setdefault(c,[]).append((hw,key))
    for c in seen_order:
        f.write("\n## %s  (%d)\n"%(c,cat_counter[c]))
        for hw,key in sorted(bykey[c], key=lambda x:x[1]):
            f.write("%-40s\t%s\n"%(hw,key))
print("\nwrote",OUT)

# write one Markdown file per category
OUTDIR=os.path.join(HERE, "Catalan-uncovered")
os.makedirs(OUTDIR,exist_ok=True)
SLUG={'suspect-char':'00-suspect-char','simple':'01-simple','compound(2)':'02-compound-2',
      'long-compound(3+)':'03-long-compound-3plus','root':'04-root','prefixed-root':'05-prefixed-root'}
DESC={
 'suspect-char':"File/encoding artifacts — stray leading symbols, mojibake, a spurious leading `U` on prefixed roots, abbreviated cross-reference stubs ending in a bullet, inline periphrastic notation (`+ √…`), and parenthetical residue. **Not real missing words** — clean-up candidates to feed back to the Catalan editors.",
 'simple':"Single, non-compound lemmas absent from every CDSL dictionary: rare derivatives, orthographic variants, solid sandhi-forms, and a few truncated stem fragments. Spot-checked as genuinely absent from MW (e.g. `āmraka-`, `bhikṣāśana-`, `ārṇa-`).",
 'compound(2)':"Two-member compounds written solid; MW headwords only a selection of compounds, so these are listed under a parent lemma or omitted. Genuine lexical content.",
 'long-compound(3+)':"Three-or-more-member compounds; heavily **Advaita-Vedānta / philosophical** vocabulary that MW does not headword separately.",
 'root':"Roots (mostly **denominative / causative** verbs such as `√nāthaya`, `√dolaya`, `√kuṇṭh`) that Cologne/Whitney do not list as roots — a lemmatisation-policy difference, not a gap.",
 'prefixed-root':"Preverb + root combinations (`abhi-saṃ-ā-√gam`) that CDSL keeps only inside MW entries, never as separate `<k1>` keys.",
}
for c in seen_order:
    rows_c=sorted(bykey[c], key=lambda x:x[1])
    path=os.path.join(OUTDIR, SLUG.get(c,c.replace('(','').replace(')','').replace('+','plus').replace(' ','-'))+'.md')
    with open(path,'w',encoding='utf-8') as f:
        f.write("# Catalan → CDSL-uncovered: `%s`  (%d headwords)\n\n"%(c,cat_counter[c]))
        f.write("> Headwords from the *Diccionari Sànscrit–Català* not found as a `<k1>` key in any of the %d CDSL dictionaries (`csl-orig/v02`), accent- and compound-insensitive.\n>\n"%ndicts)
        f.write("> **Category:** %s\n\n"%DESC.get(c,''))
        f.write("See [`../Sanskrit-Catalan-Wordlist-vs-Cologne.md`](../Sanskrit-Catalan-Wordlist-vs-Cologne.md) §4 for the full breakdown.\n\n")
        f.write("| # | Catalan headword | normalised SLP1 key |\n|---:|---|---|\n")
        for i,(hw,key) in enumerate(rows_c,1):
            f.write("| %d | `%s` | `%s` |\n"%(i,hw.replace('|','\\|'),key))
    print("wrote",path)
print("\nper-category md files in",OUTDIR)
