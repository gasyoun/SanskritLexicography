"""Huet/INRIA 'Sanskrit Heritage' wordlist (21562-huet-velthius.txt) vs CDSL + DCS.

A non-Cologne control alongside the Catalan-Pujol study: how much of an independent
Sanskrit headword spine — the INRIA Heritage reader's stem list
(https://sanskrit.inria.fr/DICO/reader.fr.html), an older export — is covered by
the CDSL dictionaries and attested in the DCS corpus.

The file is in Huet's VH (Velthuis) transliteration; sanskrit-util has no Velthuis
decoder, so VH is mapped to IAST here (the only new code) and then transcoded with
su.to_slp1 + the same accent/ASCII normalisation as the Catalan scripts so the keys
line up across all studies.
"""
import sys, re, os, unicodedata, json
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su
ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
DCS = os.environ.get("DCS_LEMMA_SUMMARY", os.path.normpath(os.path.join(HERE, "..", "..", "VisualDCS", "dcs_lemma_summary.json")))
HUET = os.path.join(HERE, "21562-huet-velthius.txt")
DICTS = ['mw', 'pw', 'pwg', 'mw72', 'ap90', 'cae', 'yat', 'wil', 'bur', 'gra', 'bor', 'vcp', 'shs', 'ben', 'mwe']

# Huet VH (Velthuis) -> IAST, longest tokens first (greedy left-to-right).
VH = [('.rr', 'ṝ'), ('.ll', 'ḹ'), ('aa', 'ā'), ('ii', 'ī'), ('uu', 'ū'),
      ('~n', 'ñ'), ('~m', 'ṃ'), ('.r', 'ṛ'), ('.l', 'ḷ'), ('.m', 'ṃ'), ('.h', 'ḥ'),
      ('.t', 'ṭ'), ('.d', 'ḍ'), ('.n', 'ṇ'), ('.s', 'ṣ'), ('z', 'ś'), ('f', 'ṅ')]
def vh_to_iast(w):
    out, i = [], 0
    while i < len(w):
        for vh, ia in VH:
            if w.startswith(vh, i):
                out.append(ia); i += len(vh); break
        else:
            out.append(w[i]); i += 1
    return ''.join(out)

def ascii_clean(k):
    k = unicodedata.normalize('NFD', k)
    return ''.join(c for c in k if ord(c) < 128 and not unicodedata.combining(c))
def norm_key(k):
    bs = chr(92)
    return ascii_clean(su.strip_slp1_accents(k).replace('˚', '').replace('/', '').replace(bs, ''))
def norm_huet(w):
    w = w.strip().strip(' ,;').replace('-', '').replace('_', '').replace('$', '')
    if not w:
        return ''
    ia = unicodedata.normalize('NFC', vh_to_iast(w))
    try:
        slp = su.to_slp1(ia)
    except Exception:
        return ''
    return norm_key(slp) if slp else ''
def load_k1(d):
    p = os.path.join(ORIG, d, d + '.txt'); s = set()
    if os.path.exists(p):
        for l in open(p, encoding='utf-8'):
            m = re.search(r'<k1>([^<]+)', l)
            if m: s.add(norm_key(m.group(1).strip()))
    return s

if __name__ == "__main__":
    # quick transcoder self-check
    for vh, want in [('a.mza', 'aMSa'), ('akalafka', 'akalaNka'), ('akaa.n.da', 'akARqa'),
                     ('akani.s.thataa', 'akanizWatA'), ('akaaraprazle.sa', 'akArapraSleza')]:
        got = norm_huet(vh)
        print(f"  check {vh:<18} -> {got:<16} {'OK' if got == want else 'WANT ' + want}")

    huet = set(); n = 0
    for line in open(HUET, encoding='utf-8-sig'):
        k = norm_huet(line.rstrip('\n'))
        if k: huet.add(k); n += 1
    print(f"\nHuet lines: {n}  unique normalised keys: {len(huet)}")

    # dictionary coverage (greedy marginal)
    dsets = {d: load_k1(d) for d in DICTS}
    dsets = {d: s for d, s in dsets.items() if s}
    covered, remaining, order = set(), set(dsets), []
    while remaining:
        best = max(remaining, key=lambda d: len((huet & dsets[d]) - covered))
        add = len((huet & dsets[best]) - covered)
        if add == 0: break
        covered |= huet & dsets[best]; remaining.discard(best)
        order.append((best, add, len(covered), 100 * len(covered) / len(huet)))
    print("\nGreedy CDSL coverage:")
    for d, a, c, p in order:
        print(f"  {d:<5} +{a:<6} cum {c:<6} {p:5.1f}%")
    print(f"  uncovered by all: {len(huet) - len(covered)} ({100 - 100 * len(covered) / len(huet):.1f}%)")

    # DCS attestation
    dcs = set()
    for k in json.load(open(DCS, encoding='utf-8'))['lemmas']:
        nk = norm_key(k)
        if nk: dcs.add(nk)
    att = huet & dcs
    cov = huet & covered
    print(f"\nDCS corpus-attested: {len(att)} ({100 * len(att) / len(huet):.1f}%)")
    print(f"in a CDSL dict: {len(cov)} ({100 * len(cov) / len(huet):.1f}%)")
    print(f"DCS-attested but in NO CDSL dict: {len(att - covered)} ({100 * len((att - covered)) / len(huet):.1f}%)")
