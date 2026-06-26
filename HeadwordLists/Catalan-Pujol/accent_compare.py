"""Do Pujol's Vedic accents agree with Cologne's?

Pujol marks udatta with a *combining acute on the vowel* in IAST (`áṃśa-`);
Cologne marks it with a `/` *after* the accented vowel in SLP1 `<k2>` (`a/MSa`).
Two different notations — this checks whether they put the accent in the SAME
PLACE on the shared lemmas. Accent position is expressed as a set of vowel
ordinals (1 = first vowel of the word) so the IAST/SLP1 notations are comparable.

Compares against GRA (Grassmann Rig-Veda, fully accented, the natural overlap for
Pujol's RV-derived accents) and MW. Reports agree / differ / one-side-only, with
disagreement examples.
"""
import sys, re, os, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su
ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
CAT = os.path.join(HERE, "61267-Sanskrit-Catalan-Words-List.txt")
SLP_VOWELS = set("aAiIuUfFxXeEoO")
ACUTE, GRAVE = '́', '̀'

def ascii_clean(k):
    k = unicodedata.normalize('NFD', k)
    return ''.join(c for c in k if ord(c) < 128 and not unicodedata.combining(c))

def slp_vowel_ordinal(slp_prefix):
    return sum(1 for c in slp_prefix if c in SLP_VOWELS)

def pujol_entry(hw):
    """-> (bare_slp1_key, frozenset_of_accent_vowel_ordinals) or None"""
    w = re.sub(r'\([^)]*\)', '', hw).strip().strip(' ,;').replace('√', '').replace('˚', '')
    w = re.sub(r'\d+$', '', w).strip()
    w = unicodedata.normalize('NFC', w).replace('-', '')
    nfd = unicodedata.normalize('NFD', w)
    base, acc_idx = [], []
    for ch in nfd:
        if unicodedata.combining(ch):
            if ch in (ACUTE, GRAVE) and base:
                acc_idx.append(len(base) - 1)
            continue
        base.append(ch)
    base_str = ''.join(base)
    try:
        key = ascii_clean(su.strip_slp1_accents(su.to_slp1(base_str)))
    except Exception:
        return None
    if not key:
        return None
    ords = set()
    for i in acc_idx:
        try:
            pre = su.to_slp1(''.join(base[:i + 1]))
        except Exception:
            continue
        ords.add(slp_vowel_ordinal(pre))
    return key, frozenset(ords)

def cologne_k2(dictcode):
    """-> {bare_key: set_of_frozenset(ords)}  — ALL accent variants per key, so a
    bare key shared by accent-homographs (bhara vs bhára) keeps both analyses."""
    path = os.path.join(ORIG, dictcode, dictcode + ".txt")
    out = collections.defaultdict(set)
    if not os.path.exists(path):
        return out
    for line in open(path, encoding='utf-8'):
        m = re.search(r'<k2>([^<]+)', line)
        if not m:
            continue
        k2 = m.group(1).strip()
        ords, vc = set(), 0
        for ch in k2:
            if ch in SLP_VOWELS:
                vc += 1
            elif ch == '/':
                ords.add(vc)            # udatta on the most recent vowel
        bare = ascii_clean(su.strip_slp1_accents(k2).replace('-', '').replace('°', '').replace('+', ''))
        if bare:
            out[bare].add(frozenset(ords))
    return out

# Pujol accent map: bare key -> set of accent-ordinal variants
puj = collections.defaultdict(set)
for line in open(CAT, encoding='utf-8-sig'):
    r = pujol_entry(line.rstrip('\n'))
    if r:
        puj[r[0]].add(r[1])
puj_acc = {k: v for k, v in puj.items() if any(s for s in v)}
print("Pujol lemmas with >=1 accent variant:", len(puj_acc))

def has_acc(variants):
    return any(s for s in variants)

for d in ('gra', 'mw'):
    col = cologne_k2(d)
    col_acc = {k: v for k, v in col.items() if has_acc(v)}
    shared = set(puj) & set(col)
    both = [k for k in shared if has_acc(puj[k]) and has_acc(col[k])]
    # agree = some Pujol accent variant matches some Cologne accent variant
    agree = [k for k in both if (puj[k] & col[k])]
    differ = [k for k in both if not (puj[k] & col[k])]
    pujol_only = [k for k in shared if has_acc(puj[k]) and not has_acc(col[k])]
    cologne_only = [k for k in shared if has_acc(col[k]) and not has_acc(puj[k])]
    print(f"\n=== Pujol vs {d.upper()} ===")
    print(f"  {d.upper()} accented <k2> lemmas: {len(col_acc)}")
    print(f"  shared lemmas (present both sides): {len(shared)}")
    print(f"  both sides accented: {len(both)}  ->  AGREE {len(agree)} ({100*len(agree)/max(1,len(both)):.1f}%)  DIFFER {len(differ)}")
    print(f"  accented in Pujol only (Cologne key unaccented): {len(pujol_only)}")
    print(f"  accented in {d.upper()} only (Pujol unaccented): {len(cologne_only)}")
    print(f"  --- sample real disagreements (no variant matches) ---")
    for k in sorted(differ)[:15]:
        print(f"    {k:<18} Pujol {sorted(map(sorted,puj[k]))}  vs {d.upper()} {sorted(map(sorted,col[k]))}")
