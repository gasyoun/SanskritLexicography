"""Ingest Heritage (INRIA) DATA/*.tsv frequency tables and diff against VisualDCS's
M1-M8 CoNLL-U import (dcs_full.sqlite) and RussianTranslation's corpus_lexicon.jsonl.
Roadmap: HERITAGE_INRIA_ROADMAP.md Phase 3. Report: heritage_frequency_diff.md.

Heritage's DATA/*.tsv forms are in the WX transliteration scheme (confirmed from the
mirror's own XML/WX_morph.dtd comment: "Transliteration of forms according to UoH
scheme WX: a A i I u U q Q L e E o O M z H / k K g G f c C j J F t T d D N w W x X n
p P b B m y r l v S R s h"). WX and SLP1 agree on vowels, labials, semivowels and
gutturals/palatals (bar the nasals) but SWAP the dental/retroflex stop rows relative
to SLP1 -- WX uses w/W/x/X/n for the DENTAL row (t/th/d/dh/n) and t/T/d/D/N for the
RETROFLEX row (tt/tth/dd/ddh/nn), the opposite convention from SLP1. Cross-checked
against known words in the data: "waw" (w-a-w) -> SLP1 "tat" (तत्); "Xarma" (X-a-r-m-a)
-> SLP1 "Darma" (धर्म, dharma); "mahA", "sarva", "uvAca" round-trip unchanged since
those letters are shared between the two schemes.

Inputs are all gitignored/local-only (the Heritage mirror, VisualDCS's dcs_full.sqlite,
and RussianTranslation's corpus_lexicon.jsonl) -- this script is not runnable outside a
full local checkout of the three sibling data sources; heritage_frequency_diff.tsv is
the durable, committed output.
"""
import sys, os, sqlite3, json
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su

MIRROR = os.environ.get("HERITAGE_MIRROR_DATA", os.path.join(HERE, "heritage_mirror", "DATA"))
DCS_SQLITE = os.environ.get("DCS_FULL_SQLITE", os.path.normpath(os.path.join(HERE, "..", "..", "VisualDCS", "src", "DCS-data-2026", "dcs_full.sqlite")))
CORPUS_LEXICON = os.environ.get("CORPUS_LEXICON_JSONL", os.path.normpath(os.path.join(HERE, "..", "RussianTranslation", "src", "corpus_lexicon.jsonl")))
OUT_TSV = os.path.join(HERE, "heritage_frequency_diff.tsv")

# ---- WX -> SLP1, sourced from Heritage's own XML/WX_morph.dtd transliteration comment ----
_WX2SLP1 = {
    # vowels: a A i I u U q Q L e E o O M z H
    'a': 'a', 'A': 'A', 'i': 'i', 'I': 'I', 'u': 'u', 'U': 'U',
    'q': 'f', 'Q': 'F', 'L': 'x', 'e': 'e', 'E': 'E', 'o': 'o', 'O': 'O',
    'M': 'M', 'z': '~', 'H': 'H',
    # gutturals/palatals: k K g G f | c C j J F  (f=guttural nasal N, F=palatal nasal Y)
    'k': 'k', 'K': 'K', 'g': 'g', 'G': 'G', 'f': 'N',
    'c': 'c', 'C': 'C', 'j': 'j', 'J': 'J', 'F': 'Y',
    # retroflex: t T d D N  (SWAPPED vs SLP1's own t/d row)
    't': 'w', 'T': 'W', 'd': 'q', 'D': 'Q', 'N': 'R',
    # dental: w W x X n  (SWAPPED vs SLP1's own T/D row)
    'w': 't', 'W': 'T', 'x': 'd', 'X': 'D', 'n': 'n',
    # labials
    'p': 'p', 'P': 'P', 'b': 'b', 'B': 'B', 'm': 'm',
    # semivowels
    'y': 'y', 'r': 'r', 'l': 'l', 'v': 'v',
    # sibilants: S R s -> S z s
    'S': 'S', 'R': 'z', 's': 's',
    'h': 'h',
}
_UNMAPPED = {}


def wx_to_slp1(w):
    out = []
    for ch in w:
        if ch in _WX2SLP1:
            out.append(_WX2SLP1[ch])
        else:
            out.append(ch)
            _UNMAPPED[ch] = _UNMAPPED.get(ch, 0) + 1
    return ''.join(out)


def load_freq_tsv(path):
    rows = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line:
            continue
        parts = line.split('\t')
        try:
            cnt = int(parts[-1])
        except ValueError:
            continue
        rows.append(('\t'.join(parts[:-1]), cnt))
    return rows


def load_morph_freq_tsv(path):
    """(stem, tag, ..., count) rows -> aggregate count by stem (col 0)."""
    agg = {}
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line:
            continue
        parts = line.split('\t')
        try:
            cnt = int(parts[-1])
        except ValueError:
            continue
        agg[parts[0]] = agg.get(parts[0], 0) + cnt
    return sorted(agg.items(), key=lambda kv: -kv[1])


def transcode_series(rows):
    out = {}
    for k, c in rows:
        sk = wx_to_slp1(k)
        out[sk] = out.get(sk, 0) + c
    return sorted(out.items(), key=lambda kv: -kv[1])


def _avg_ranks(values):
    """1-based average ranks, descending (largest value = rank 1), ties share the mean rank."""
    order = sorted(range(len(values)), key=lambda i: -values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(value_pairs):
    """value_pairs: [(raw_a, raw_b), ...] over the SAME item set; ranks computed LOCALLY
    within this pair set (never borrowed from the two corpora's differently-sized full
    rankings -- that mismatch previously produced nonsense rho values outside [-1, 1])."""
    n = len(value_pairs)
    if n < 2:
        return None
    ra = _avg_ranks([p[0] for p in value_pairs])
    rb = _avg_ranks([p[1] for p in value_pairs])
    d2sum = sum((x - y) ** 2 for x, y in zip(ra, rb))
    return 1 - (6 * d2sum) / (n * (n ** 2 - 1))


def ranks_from_sorted(sorted_items):
    return {k: i + 1 for i, (k, c) in enumerate(sorted_items)}


if __name__ == "__main__":
    print("=== 1. Ingest the 7 Heritage DATA/*.tsv files ===")
    files = ['pada_freq.tsv', 'pada_morph_freq.tsv', 'pada_trans_freq.tsv',
             'comp_freq.tsv', 'comp_morph_freq.tsv', 'comp_trans_freq.tsv', 'word_freq.tsv']
    for fn in files:
        n = sum(1 for _ in open(os.path.join(MIRROR, fn), encoding='utf-8'))
        print(f"  {fn:<22} {n:>8} rows")

    word_freq = load_freq_tsv(os.path.join(MIRROR, 'word_freq.tsv'))
    pada_morph_lemma = load_morph_freq_tsv(os.path.join(MIRROR, 'pada_morph_freq.tsv'))
    comp_morph_lemma = load_morph_freq_tsv(os.path.join(MIRROR, 'comp_morph_freq.tsv'))

    print("\n=== 2. WX -> SLP1 transcode ===")
    word_freq_slp1 = transcode_series(word_freq)
    pada_lemma_slp1 = transcode_series(pada_morph_lemma)
    comp_lemma_slp1 = transcode_series(comp_morph_lemma)
    print(f"  unmapped chars seen: {_UNMAPPED if _UNMAPPED else '(none)'}")
    for wxk, c in word_freq[:8]:
        print(f"    {wxk:<12} -> {wx_to_slp1(wxk):<12} ({c})")

    print("\n=== 3. VisualDCS M1-M8 (dcs_full.sqlite) frequency ===")
    cur = sqlite3.connect(DCS_SQLITE).cursor()
    cur.execute("SELECT form, COUNT(*) c FROM token WHERE form IS NOT NULL GROUP BY form ORDER BY c DESC")
    dcs_form_rows = cur.fetchall()
    cur.execute("SELECT lemma, COUNT(*) c FROM token WHERE lemma IS NOT NULL GROUP BY lemma ORDER BY c DESC")
    dcs_lemma_rows = cur.fetchall()
    print(f"  distinct token.form: {len(dcs_form_rows)}  distinct token.lemma: {len(dcs_lemma_rows)}")

    def dcs_to_slp1(rows):
        out = {}
        for iast, c in rows:
            sk = su.to_slp1(iast)
            out[sk] = out.get(sk, 0) + c
        return sorted(out.items(), key=lambda kv: -kv[1])

    dcs_form_slp1 = dcs_to_slp1(dcs_form_rows)
    dcs_lemma_slp1 = dcs_to_slp1(dcs_lemma_rows)

    print("\n=== 4. corpus_lexicon.jsonl surface-form frequency ===")
    clex_counts = {}
    n_lines = 0
    for line in open(CORPUS_LEXICON, encoding='utf-8'):
        n_lines += 1
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        sk = rec.get('slp1')
        if sk:
            clex_counts[sk] = clex_counts.get(sk, 0) + 1
    clex_slp1 = sorted(clex_counts.items(), key=lambda kv: -kv[1])
    print(f"  lines: {n_lines}  distinct slp1 forms: {len(clex_slp1)}")

    print("\n=== 5. Series A: surface forms (word_freq vs DCS token.form vs corpus_lexicon) ===")
    dcs_form_rank = ranks_from_sorted(dcs_form_slp1); dcs_form_freq = dict(dcs_form_slp1)
    clex_rank = ranks_from_sorted(clex_slp1); clex_freq = dict(clex_slp1)
    joinA = [{
        'slp1': k, 'heritage_freq': c, 'heritage_rank': i + 1,
        'dcs_freq': dcs_form_freq.get(k, 0), 'dcs_rank': dcs_form_rank.get(k),
        'clex_freq': clex_freq.get(k, 0), 'clex_rank': clex_rank.get(k),
    } for i, (k, c) in enumerate(word_freq_slp1)]
    in_dcs = sum(1 for r in joinA if r['dcs_rank']); in_clex = sum(1 for r in joinA if r['clex_rank'])
    print(f"  {len(joinA)} forms; in DCS: {in_dcs} ({100*in_dcs/len(joinA):.1f}%); in corpus_lexicon: {in_clex} ({100*in_clex/len(joinA):.1f}%)")
    TOPN = 3000
    rhoA_dcs = spearman([(r['heritage_freq'], r['dcs_freq']) for r in joinA[:TOPN] if r['dcs_rank']])
    rhoA_clex = spearman([(r['heritage_freq'], r['clex_freq']) for r in joinA[:TOPN] if r['clex_rank']])
    print(f"  Spearman rho vs DCS: {rhoA_dcs:.4f}   vs corpus_lexicon: {rhoA_clex:.4f}")

    print("\n=== 6. Series B: lemmas (pada_morph_freq aggregated vs DCS token.lemma) ===")
    dcs_lemma_rank = ranks_from_sorted(dcs_lemma_slp1); dcs_lemma_freq = dict(dcs_lemma_slp1)
    joinB = [{
        'slp1_lemma': k, 'heritage_freq': c, 'heritage_rank': i + 1,
        'dcs_freq': dcs_lemma_freq.get(k, 0), 'dcs_rank': dcs_lemma_rank.get(k),
    } for i, (k, c) in enumerate(pada_lemma_slp1)]
    in_dcs_b = sum(1 for r in joinB if r['dcs_rank'])
    rhoB = spearman([(r['heritage_freq'], r['dcs_freq']) for r in joinB[:TOPN] if r['dcs_rank']])
    print(f"  {len(joinB)} lemmas; in DCS: {in_dcs_b} ({100*in_dcs_b/len(joinB):.1f}%); Spearman rho: {rhoB:.4f}")

    print("\n=== 7. Series C: compound first-members (comp_morph_freq aggregated vs DCS token.lemma) ===")
    joinC = [{
        'slp1_stem': k, 'heritage_freq': c, 'heritage_rank': i + 1,
        'dcs_freq': dcs_lemma_freq.get(k, 0), 'dcs_rank': dcs_lemma_rank.get(k),
    } for i, (k, c) in enumerate(comp_lemma_slp1)]
    in_dcs_c = sum(1 for r in joinC if r['dcs_rank'])
    rhoC = spearman([(r['heritage_freq'], r['dcs_freq']) for r in joinC[:TOPN] if r['dcs_rank']])
    print(f"  {len(joinC)} stems; in DCS: {in_dcs_c} ({100*in_dcs_c/len(joinC):.1f}%); Spearman rho: {rhoC:.4f}")

    print(f"\n=== 8. Writing {OUT_TSV} ===")
    with open(OUT_TSV, 'w', encoding='utf-8', newline='\n') as f:
        f.write("series\tkey_slp1\theritage_freq\theritage_rank\tdcs_freq\tdcs_rank\tcorpus_lexicon_freq\tcorpus_lexicon_rank\n")
        for r in joinA:
            f.write(f"surface_form\t{r['slp1']}\t{r['heritage_freq']}\t{r['heritage_rank']}\t{r['dcs_freq']}\t{r['dcs_rank'] or ''}\t{r['clex_freq']}\t{r['clex_rank'] or ''}\n")
        for r in joinB:
            f.write(f"pada_lemma\t{r['slp1_lemma']}\t{r['heritage_freq']}\t{r['heritage_rank']}\t{r['dcs_freq']}\t{r['dcs_rank'] or ''}\t\t\n")
        for r in joinC:
            f.write(f"compound_stem\t{r['slp1_stem']}\t{r['heritage_freq']}\t{r['heritage_rank']}\t{r['dcs_freq']}\t{r['dcs_rank'] or ''}\t\t\n")
    print(f"  wrote {len(joinA) + len(joinB) + len(joinC)} rows")
