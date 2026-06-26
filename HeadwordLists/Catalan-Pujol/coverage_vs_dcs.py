"""Catalan-Pujol wordlist vs the DCS *corpus* (not the CDSL dictionaries).

coverage_by_dict.py / match_rate.py ask "is each Catalan lemma in a CDSL
dictionary?". This asks the orthogonal question: "is it actually *attested in
texts*?" using the DCS lemma index (VisualDCS/dcs_lemma_summary.json, SLP1-keyed,
freqBand 1-5). It then cross-tabs dictionary-coverage x corpus-attestation, and
surfaces the two interesting corners: corpus-attested lemmas that NO CDSL
dictionary covers, and dictionary-listed lemmas the corpus never attests.

Same normalisation as coverage_by_dict.py (strip root/accent/hyphen, IAST->SLP1,
accent-strip, ASCII) so the keys line up across all three analyses.
"""
import sys, re, os, unicodedata, json
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su

ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
DCS = os.environ.get("DCS_LEMMA_SUMMARY",
                     os.path.normpath(os.path.join(HERE, "..", "..", "..", "VisualDCS", "dcs_lemma_summary.json")))
CAT = os.path.join(HERE, "61267-Sanskrit-Catalan-Words-List.txt")
DICTS = ['mw', 'pw', 'pwg', 'mw72', 'ap90', 'cae', 'yat', 'wil', 'bur', 'gra', 'bor', 'vcp', 'shs', 'ben', 'mwe']

def ascii_clean(k):
    k = unicodedata.normalize('NFD', k)
    return ''.join(c for c in k if ord(c) < 128 and not unicodedata.combining(c))

def norm_cat(w):
    w = re.sub(r'\([^)]*\)', '', w).strip().strip(' ,;')
    w = w.replace('√', '').replace('˚', '')
    w = re.sub(r'\d+$', '', w).strip()
    w = unicodedata.normalize('NFC', w).replace('-', '')
    try: slp = su.to_slp1(w)
    except Exception: return ''
    if not slp: return ''
    return ascii_clean(su.strip_slp1_accents(slp))

def norm_key(k):
    bs = chr(92)
    k = su.strip_slp1_accents(k).replace('˚', '').replace('/', '').replace(bs, '')
    return ascii_clean(k)

def load_k1(d):
    path = os.path.join(ORIG, d, d + '.txt'); keys = set()
    if not os.path.exists(path): return keys
    for line in open(path, encoding='utf-8'):
        m = re.search(r'<k1>([^<]+)', line)
        if m: keys.add(norm_key(m.group(1).strip()))
    return keys

# --- Catalan keys ---
cat = set()
for line in open(CAT, encoding='utf-8-sig'):
    s = norm_cat(line.rstrip('\n'))
    if s: cat.add(s)
print("unique Catalan keys:", len(cat))

# --- DCS attestation (key -> max freqBand) ---
dcs_raw = json.load(open(DCS, encoding='utf-8'))
print("DCS corpus:", dcs_raw.get('corpusRelease', '?'), "|", dcs_raw['lemmaCount'], "lemmas")
dcs = {}
for k, v in dcs_raw['lemmas'].items():
    nk = norm_key(k)
    if nk:
        dcs[nk] = max(dcs.get(nk, 0), v.get('freqBand', 0))

attested = cat & set(dcs)
print("\n=== Catalan lemmas attested in the DCS corpus ===")
print("attested: %d / %d = %.1f%%" % (len(attested), len(cat), 100 * len(attested) / len(cat)))
print("NOT attested (dictionary-only): %d = %.1f%%" % (len(cat) - len(attested), 100 * (len(cat) - len(attested)) / len(cat)))
print("\nby DCS frequency band (5=most frequent):")
for b in (5, 4, 3, 2, 1):
    n = sum(1 for k in attested if dcs[k] == b)
    print("  band %d: %6d  (%.1f%% of list)" % (b, n, 100 * n / len(cat)))

# --- dictionary union x corpus cross-tab ---
covered = set()
for d in DICTS:
    covered |= cat & load_k1(d)
both = cat & covered & set(dcs)
dict_only = (cat & covered) - set(dcs)
dcs_only = (cat & set(dcs)) - covered
neither = cat - covered - set(dcs)
print("\n=== dictionary coverage x corpus attestation (of %d Catalan keys) ===" % len(cat))
print("  in a CDSL dict AND DCS-attested : %6d  (%.1f%%)" % (len(both), 100 * len(both) / len(cat)))
print("  in a CDSL dict, NOT DCS         : %6d  (%.1f%%)  <- listed but unattested in the corpus" % (len(dict_only), 100 * len(dict_only) / len(cat)))
print("  DCS-attested, in NO CDSL dict   : %6d  (%.1f%%)  <- corpus-real gaps in CDSL" % (len(dcs_only), 100 * len(dcs_only) / len(cat)))
print("  neither dict nor DCS            : %6d  (%.1f%%)" % (len(neither), 100 * len(neither) / len(cat)))

print("\n--- sample: DCS-attested but in NO CDSL dictionary (top by band) ---")
for k in sorted(dcs_only, key=lambda x: -dcs[x])[:25]:
    print("  band %d  %s" % (dcs[k], k))
