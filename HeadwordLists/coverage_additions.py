"""Coverage additions (PRINT_READINESS item B), ranked by DCS frequency band.

Candidate headwords to ADD to the printed union list: DCS-corpus lemmas (attested in
real texts) that are NOT in the cross-dict union (i.e. in no CDSL dictionary), ranked
by DCS frequency band (5 = most frequent → add first). This is the comprehensive,
corpus-grounded version of B; the Catalan §5 "177" and the Huet residue are subsets.

Keys are normalised the same way (accent-stripped ASCII SLP1) so the DCS index and the
union line up. Output: union/coverage_additions.tsv (band-sorted) + summary.
"""
import sys, re, os, json, collections
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su
import unicodedata
DCS = os.environ.get("DCS_LEMMA_SUMMARY",
                     os.path.normpath(os.path.join(HERE, "..", "..", "VisualDCS", "dcs_lemma_summary.json")))
UNION = os.path.join(HERE, "union", "union_headwords.tsv")
OUT = os.path.join(HERE, "union", "coverage_additions.tsv")

def ascii_clean(k):
    k = unicodedata.normalize('NFD', k)
    return ''.join(c for c in k if ord(c) < 128 and not unicodedata.combining(c))
def norm_key(k):
    bs = chr(92)
    return ascii_clean(su.strip_slp1_accents(k).replace('˚', '').replace('/', '').replace(bs, ''))
def iast(s):
    try: return su.from_slp1(s)
    except Exception: return s

def main():
    # union headwords (normalised) — the current CDSL coverage baseline. Add back the
    # folded feminines (they are covered by CDSL, just folded under the masculine in the
    # display) so they are not falsely reported as missing.
    union = set()
    with open(UNION, encoding="utf-8") as f:
        next(f)
        for ln in f:
            nk = norm_key(ln.split("\t", 1)[0])
            if nk: union.add(nk)
    folded = os.path.join(HERE, "union", "folded_feminines.tsv")
    if os.path.exists(folded):
        with open(folded, encoding="utf-8") as f:
            next(f)
            for ln in f:
                nk = norm_key(ln.split("\t", 1)[0])
                if nk: union.add(nk)
    # DCS lemmas (normalised) -> max band, + attested flag
    raw = json.load(open(DCS, encoding="utf-8"))
    dcs = {}
    for k, v in raw["lemmas"].items():
        if not v.get("attested", True):
            continue
        nk = norm_key(k)
        if nk:
            dcs[nk] = max(dcs.get(nk, 0), v.get("freqBand", 0))
    additions = {k: b for k, b in dcs.items() if k not in union}

    PREVERB = ('aBisaM', 'aBi', 'aDi', 'anu', 'antar', 'apa', 'api', 'ava', 'A', 'ud', 'upa',
               'ni', 'nis', 'nir', 'parA', 'pari', 'pra', 'prati', 'vi', 'sam', 'saM', 'su')
    def kind(k):
        # DCS lemmatises causatives/denominatives as -ay stems, and keeps prefixed/
        # desiderative verb roots; CDSL stores these under the simple root, so they are
        # lemmatisation artifacts, NOT genuine missing headwords (cf. Catalan §5).
        if k.endswith('ay'):
            return 'verb-deriv'      # causative / denominative -ay stem
        if re.search(r'(at|ant|vas|mas)$', k) and len(k) <= 7:
            return 'infl?'           # likely inflected/participle stem
        # prefixed verb root: a preverb + a short consonant-final remainder (e.g. namaskf,
        # aBisaMbuD, avatf, paripf, SuSrUz)
        for p in PREVERB:
            if k.startswith(p) and 1 <= len(k) - len(p) <= 4 and k[-1] not in 'aAiIuUeEoO':
                return 'prefixed-verb?'
        if k.endswith('kf') or re.search(r'(z|s)$', k) and len(k) <= 6:
            return 'verb?'           # -kṛ compounds / desiderative-ish
        if len(k) <= 2 or (len(k) <= 5 and k[-1] in 'MH'):
            return 'bija/letter'     # bare seed-syllable / alphabet letter (īṃ, hrīṃ, c, t)
        if re.search(r'(cid|cana|tas|taH|tu)$', k):
            return 'indecl?'         # adverb / indeclinable (kadācid, kathaṃcana, viśeṣataḥ)
        return 'nominal'             # the genuine candidate additions
    ARTIFACT = {'verb-deriv', 'infl?', 'prefixed-verb?', 'verb?', 'bija/letter', 'indecl?'}

    rows = sorted(additions.items(), key=lambda kv: (-kv[1], kind(kv[0]) != 'nominal', kv[0]))
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("dcs_band\tkind\tslp1\tiast\n")
        for k, b in rows:
            fh.write(f"{b}\t{kind(k)}\t{k}\t{iast(k)}\n")

    nominal = {k: b for k, b in additions.items() if kind(k) not in ARTIFACT}
    byband = collections.Counter(additions.values())
    nomband = collections.Counter(nominal.values())
    print(f"union (normalised) headwords: {len(union)}")
    print(f"DCS attested lemmas: {len(dcs)}")
    print(f"coverage additions (DCS-attested, NOT in any CDSL dict): {len(additions)}  "
          f"| genuine nominal: {len(nominal)}  | verb-deriv/infl artifacts: {len(additions) - len(nominal)}")
    print("by DCS band — total (genuine nominal) — 5 = most frequent → add first:")
    for b in (5, 4, 3, 2, 1):
        print(f"  band {b}: {byband.get(b, 0):>6}  ({nomband.get(b, 0)} nominal)")
    print(f"\nwrote {OUT}")

if __name__ == "__main__":
    main()
