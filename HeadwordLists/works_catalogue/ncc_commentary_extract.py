"""NCC commentary extraction library (H7202) -- markers, target resolution,
edge extraction (NCC bodies + ACC backfill).  Split out of the single-file
build script for the token-size gate (estate tool, Uprava PR #5383): agent-
written source goes in reviewable modules; the generated TSVs carry a
.token-gate-ignore entry instead.

Canon CLI: build_ncc_commentary_graph.py (this package's entry point).
"""
import json
import os
import re
import sys
import unicodedata

ESTATE = os.environ.get('ESTATE_ROOT', '/Users/mac/Documents/GitHub')


def _load_sanskrit_util():
    try:
        import sanskrit_util  # noqa: F401
        return sys.modules['sanskrit_util']
    except ImportError:
        pass
    for cand in (os.environ.get('SANSKRIT_UTIL_PY'),
                 os.path.join(ESTATE, 'sanskrit-util', 'py')):
        if cand and os.path.isdir(cand):
            sys.path.insert(0, cand)
            try:
                import sanskrit_util  # noqa: F401
                return sys.modules['sanskrit_util']
            except ImportError:
                continue
    raise SystemExit('sanskrit-util not found; set SANSKRIT_UTIL_PY')


su = _load_sanskrit_util()

NCC_JSONL = os.path.join(ESTATE, 'SanskritLexicography/HeadwordLists/works_catalogue/ncc.jsonl')
ACC_TXT = os.path.join(ESTATE, 'csl-orig/v02/acc/acc.txt')
XLS_2022 = os.path.join(ESTATE, 'VisualDCS/non-derived/NCC/Commentary_tree_NCC_2022.xls')
DCS_JSON = os.path.join(ESTATE, 'VisualDCS/visual/dcs_texts_clean.json')
PD_TSV = os.path.join(ESTATE, 'csl-atlas/data/pd/pd_siglum_families.tsv')
PWG_LS = os.path.join(ESTATE, 'literarysource/pwg/lsextract_pwg_06.txt')
PWG_BIB = os.path.join(ESTATE, 'literarysource/pwg/pwgbib_input.txt')
CROSSWALK = os.path.join(ESTATE, 'SanskritLexicography/HeadwordLists/works_catalogue/works_crosswalk.tsv')

TAG_RE = re.compile(r'<[^>]+>')
PAGE_ARTIFACT_RE = re.compile(r'\[Page[^\]\s]*')

CAP = r'A-ZĀĪŪṚṜḶṢṆŚṬḌH'
# Entry-side commentary marker: "C. / Comm. / Commentary / tika / ... on X"
E_MARKER_RE = re.compile(
    r'\b([TṬ]ī[kK][āa]|Tika|ṭika|C|Comm|Commentary|commentary|ṭippaṇī|Ṭippaṇī|'
    r'Vivṛti|Vivaraṇa|Bhāṣya|Vyākhyā|Dīpikā|Uddyota)'
    r'\.?\s+(?:on|upon)\s+', re.U)
# List-side: "C. <Title>" / "C.: <Title>" after sentence/segment boundary.
L_MARKER_RE = re.compile(r'(?:^|[.;:]\s|\)\s)C\.\.?\s*(?::\s*)?([' + CAP + r'])', re.U)
REL_TARGET_RE = re.compile(
    r'^(?:the\s+)?(above|same|it|text|preceding|previous|prior|latter|former|'
    r'following|next|last|present|that|this|said)\b', re.I)
STOP_CUT_RE = re.compile(
    r'\s+(?:by|of|ed\.|eds\.|with|entitled|called|also|composed|written|'
    r'beginning|which|wherein|see)\b|[,;:("“]', re.U)
# Named-tika class: titles ENDING in an unambiguous commentary-genre term
# (prakasa/manjari/prabha are excluded -- too often base-work titles).
TIKA_SUFFIX_RE = re.compile(
    r'(ṭīkā|ṭīka|tīkā|tīka|ṭippaṇī|vyākhyā|vivṛti|vivaraṇa|bhāṣya|dīpikā|'
    r'pradīpikā|uddyota)$', re.I)


def fold(s):
    """C3 §2 fold for free text: strip diacritics/punct to plain a-z."""
    s = unicodedata.normalize('NFD', s)
    out = []
    for ch in s:
        if 0x0300 <= ord(ch) <= 0x036F:
            continue
        if ch.isascii() and ch.isalpha():
            out.append(ch.lower())
        elif ch in 'ṃṁ':
            out.append('m')
        elif ch == 'ṅ':
            out.append('n')
    return ''.join(out)


def clean_body(body_html):
    t = PAGE_ARTIFACT_RE.sub(' ', body_html)
    t = TAG_RE.sub(' ', t)
    t = t.replace('\\n', ' ')
    return re.sub(r'\s+', ' ', t).strip()


def match_key_of(text):
    """Estate-canonical key, same chain as parse_ncc.match_key_for (H1671)."""
    text = re.sub(r'\([^)]*\)', '', text).replace('_', '')
    return su.slp1_simplify(su.to_slp1(unicodedata.normalize('NFC', text).lower()))


def load_ncc(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f]


class TitleIndex:
    """match_key -> first catalogue entry; unique key-prefix fallback models
    the NCC truncation convention (`Asv...` for Asvalayana...).  Prefix
    lookup is a bisect over the sorted key list (the naive full scan cost
    7 min on 152k keys)."""

    def __init__(self, entries, key_of=None):
        self.key_of = key_of or match_key_of
        self.by_key = {}
        for r in entries:
            k = r.get('match_key') or self.key_of(r.get('iast', r.get('k1', '')))
            if k and k not in self.by_key:
                self.by_key[k] = r
        self._sorted = sorted(self.by_key)
        import bisect
        self._bisect = bisect

    def resolve(self, target):
        if not target:
            return None
        k = self.key_of(target)
        if not k:
            return None
        hit = self.by_key.get(k)
        if hit:
            return hit
        if len(k) >= 4:
            b = self._bisect
            lo = b.bisect_left(self._sorted, k)
            hi = b.bisect_left(self._sorted, k + '\uffff')
            if hi - lo == 1:
                return self.by_key[self._sorted[lo]]
        return None


def extract_target(seg):
    """Title-ish run after a marker: capital-led tokens, cut at punctuation,
    author/editor clauses and possessives ("C. on Gangesa's Tattvacintamani"
    targets the Tattvacintamani, not the author)."""
    m = re.match(r'(?:the\s+|this\s+|said\s+|a\s+|an\s+)?([' + CAP + r'][^,;:("“]{1,90})', seg.strip())
    if not m:
        return None
    raw = STOP_CUT_RE.split(m.group(1))[0].strip()
    raw = re.sub(r'\s+\d.*$', '', raw)          # trailing page/serial numbers
    if "'s" in raw:                              # possessive author clause
        raw = raw.rsplit("'s", 1)[1].strip()
    raw = raw.rstrip(".'’ ")
    return raw or None


# Generic-tail strip on unresolved targets: only purana kept.  The wider
# list (kavya/stotra/zataka) was tried and reverted this pass: "C. on the
# Amarazataka" (entry missing) stripped onto the Amara author cluster and
# stole ~100 edges -- a missing entry must stay a fuzzy t-node, not become
# a differently-suffixed real work.
GENERIC_TAILS = tuple(match_key_of(s) for s in ('purāṇa',))

# Authority aliases (H7202): target-title folds that resolve to the canonical
# work NCC files under a different name.  saundaryalahari -> anandalahari:
# the work NCC files as Anandalahari carries 92 "C. on the Saundaryalahari"
# marker targets; the only rival cluster declaring that alias string is a
# stuti whose body lists it as a leading-or alias, and it would otherwise
# steal all 92 edges.  Provenance: standard title identity, NCC anandalahari
# entries vs the 92 saundaryalahari targets (this pass's census).
FOLD_ALIASES = {
    'saundaryalahari': 'anandalahari',
}


def resolve_target(raw, index, fold_map, authority=None):
    """Five-stage target resolution: exact/unique-prefix match_key, authority
    alias, generic-suffix strip (Bhagavatapurana -> Bhagavata), the cluster
    fold map (merged synonym families), then the H7215 name-authority table
    (adjudicated t:<fold> -> catalogue entry match_key, body/crosswalk-
    evidenced merges only)."""
    hit = index.resolve(raw)
    if hit is not None:
        return hit
    k = match_key_of(raw)
    if k in FOLD_ALIASES:
        hit = index.by_key.get(FOLD_ALIASES[k])
        if hit:
            return hit
    for tail in GENERIC_TAILS:
        if tail and k.endswith(tail) and len(k) - len(tail) >= 4:
            hit = index.by_key.get(k[:-len(tail)])
            if hit:
                return hit
    if fold_map and len(k) >= 6:
        e = fold_map.get(k)
        if e is not None and e != 'AMBIG':
            return e
    if authority:
        tgt = authority.get(fold(raw))
        if tgt:
            hit = index.by_key.get(tgt)
            if hit:
                return hit
    return None


def load_authority(path, entries_by_key):
    """H7215 adjudication TSV -> {fold: match_key} over MERGE rows.  A row's
    merge_cluster is a canonical cluster id; its entry is found through any
    member (the adjudicator guarantees the cluster id is a catalogue
    ncc_id).  Unresolvable rows are skipped loudly -- the table must never
    silently degrade."""
    import csv as _csv
    authority = {}
    skipped = []
    with open(path, encoding='utf-8') as f:
        for row in _csv.DictReader(f, delimiter='\t'):
            if row.get('verdict') != 'MERGE':
                continue
            if row.get('source', '').startswith('seed:'):
                continue   # seed rows ride FOLD_ALIASES as before
            key = entries_by_key.get(row.get('merge_cluster', ''))
            if key is None:
                skipped.append(row.get('fold', ''))
                continue
            authority[row['fold']] = key
    if skipped:
        print('authority rows with unknown cluster id (skipped): %d %s'
              % (len(skipped), skipped[:5]), file=sys.stderr)
    return authority


SUFFIX_KEYS = tuple(sorted({match_key_of(s) for s in (
    'ṭīkā', 'ṭīka', 'tīkā', 'tīka', 'ṭippaṇī', 'vyākhyā', 'vivṛti',
    'vivaraṇa', 'bhāṣya', 'dīpikā', 'pradīpikā', 'uddyota')}))


def tika_title_base(match_key, index):
    """Named-tika strict route: strip the commentary-genre suffix from the
    work's own key and resolve the stem to a base entry (exact, vowel-restored,
    or unique short-extension prefix)."""
    for sk in SUFFIX_KEYS:
        if sk and match_key.endswith(sk) and len(match_key) > len(sk):
            stripped = match_key[:-len(sk)]
            break
    else:
        return None
    if len(stripped) < 4:
        return None
    for cand in (stripped, stripped + 'a', stripped + 'i', stripped + 'u'):
        hit = index.by_key.get(cand)
        if hit:
            return hit
    # unique shortest-extension: longest index key that prefixes the stem
    # with <=3 leftover chars (sandhi letters)
    b = index._bisect
    for L in range(len(stripped) - 1, max(4, len(stripped) - 4), -1):
        k = stripped[:L]
        i = b.bisect_left(index._sorted, k)
        if i < len(index._sorted) and index._sorted[i] == k:
            return index.by_key[k]
    return None


def title_node(raw):
    """Fuzzy-only synthetic node for an unresolved title string."""
    return 't:' + fold(raw)


def ncc_edges(entries, resolve, index, body_folds=None):
    """Walk entry bodies in `--`-subentry segments; emit relation candidates.
    `resolve` is the three-stage target resolver; `resolved` marks strict
    eligibility (both endpoints = catalogue entries)."""
    edges = []
    for r in entries:
        body = clean_body(r['body_html'])
        if body_folds is not None:
            body_folds.append(fold(body))
        segs = re.split(r'(?:^|\s)--(?=[' + CAP + r'])', body)
        ctx_titles = [r['iast']]
        prev_sub = None
        for si, seg in enumerate(segs):
            if si > 0:
                sm = re.match(r'([' + CAP + r'][^.,;:("“]{1,80})', seg)
                ctx_titles.append(sm.group(1).strip() if sm else ctx_titles[-1])
            ctx = ctx_titles[-1]
            # entry-side markers are trusted only inside the work-definition
            # clause (first 300 chars of the entry segment; full text of a
            # -- sub-entry segment).  Later prose ("the C. on X by Y") lists
            # the entry's commentaries -- reading those as entry-side made
            # base works into commentaries of their own glosses.
            e_scope = seg if si > 0 else seg[:300]
            for m in E_MARKER_RE.finditer(e_scope):
                raw = extract_target(seg[m.end():])
                if not raw:
                    continue
                if REL_TARGET_RE.match(raw):
                    base = resolve(prev_sub) if prev_sub else resolve(ctx)
                    edges.append(dict(commentary=r, base_entry=base,
                                      base_title_raw=raw, side='E', marker='rel',
                                      ctx_title=ctx, prev_sub=prev_sub,
                                      resolved=base is not None))
                    continue
                base = resolve(raw)
                edges.append(dict(commentary=r, base_entry=base, base_title_raw=raw,
                                  side='E', marker='e_on', ctx_title=ctx,
                                  prev_sub=prev_sub, resolved=base is not None))
            for m in L_MARKER_RE.finditer(seg):
                raw = extract_target(seg[m.end() - 1:])
                if not raw:
                    continue
                base = resolve(ctx)
                if REL_TARGET_RE.match(raw):
                    # "C. the previous title": the commentary is the previous
                    # sub-entry work (fuzzy-only context resolution)
                    comm = resolve(prev_sub) if prev_sub else None
                    if comm is not None and comm['ncc_id'] != r['ncc_id']:
                        edges.append(dict(commentary=comm, base_entry=base,
                                          base_title_raw=ctx, side='L',
                                          marker='l_rel', ctx_title=ctx,
                                          prev_sub=prev_sub,
                                          resolved=base is not None))
                    continue
                comm = resolve(raw)
                if comm is not None and comm['ncc_id'] == r['ncc_id']:
                    continue
                edges.append(dict(commentary=comm, comm_raw=raw if comm is None else None,
                                  base_entry=base,
                                  base_title_raw=ctx,
                                  side='L', marker='l_list', ctx_title=ctx,
                                  prev_sub=prev_sub,
                                  resolved=comm is not None and base is not None))
            if si > 0:
                prev_sub = ctx_titles[-1]
        # named-tika strict route: the entry title itself carries the genre
        # suffix and its stem resolves to the base
        if TIKA_SUFFIX_RE.search(r['iast']):
            base = tika_title_base(r['match_key'], index)
            if base is not None and base['ncc_id'] != r['ncc_id']:
                edges.append(dict(commentary=r, base_entry=base,
                                  base_title_raw=base['iast'], side='T',
                                  marker='tika_title', ctx_title=r['iast'],
                                  prev_sub=None, resolved=True))
    return edges


# ---------------------------------------------------------------- ACC side
ACC_REC_RE = re.compile(r'<L>([0-9.]+)<pc>[^<]*<k1>([^<]*)<k2>[^\n]*\n(.*?)<LEND>', re.S)
ACC_DEV_RE = re.compile(r'\{#([^#]+)#\}')
ACC_E_MARKER_RE = re.compile(
    r'\b([TṬ]ī[kK][āa]|tika|C|commentary|ṭīkā|ṭīka|Vivṛti|Vyākhyā|Bhāṣya)'
    r'\.?\s+(?:on|upon)\s+', re.U)
# ACC prose never uses "Comm." (census: 0 hits); its commentary signal is
# "C. on X", "tikA on X", "commentary on X" -- entry-side only.
ACC_L_MARKER_RE = re.compile(r'(?:^|[.;:]\s|\)\s)C\.\.?\s*(?::\s*)?([' + CAP + r'])', re.U)


def sa_tail_ha(simplified_key):
    """NCC frontier = vol 39 p. 378 `Suhodita` (H7078): bases filed later --
    the late sa- range and every ha- work -- have no NCC bodies."""
    return simplified_key.startswith('h') or (
        simplified_key.startswith('s') and simplified_key > 'suhodita')


def parse_acc(path):
    recs = []
    with open(path, encoding='utf-8') as f:
        txt = f.read()
    for m in ACC_REC_RE.finditer(txt):
        lid, k1, body = m.group(1), m.group(2), m.group(3)
        dev = ACC_DEV_RE.search(body)
        recs.append(dict(L=lid, k1=k1, key=su.slp1_simplify(k1),
                         title=dev.group(1) if dev else k1,
                         body=re.sub(r'\s+', ' ', TAG_RE.sub(' ', body))))
    return recs


def acc_backfill_edges(acc_records, ncc_index, cf, L_map):
    """Commentary edges on bases inside the NCC gap (late sa- + all ha-),
    from ACC bodies, per-edge provenance `acc`.  Both directions:
    entry-side ("C. on X" in record R -> R comments on X) and list-side
    ("C. <Title>" inside a gap record's body).  Commentary and base nodes
    join an NCC cluster through the crosswalk when it knows the ACC L-key,
    else become synthetic `acc:<L>` nodes."""
    acc_index = TitleIndex(acc_records,
                           key_of=lambda t: su.slp1_simplify(t) if t else '')
    edges = []
    for rec in acc_records:
        in_gap = sa_tail_ha(rec['key'])
        # entry-side: this record comments on X
        for em in ACC_E_MARKER_RE.finditer(rec['body']):
            raw = extract_target(rec['body'][em.end():])
            if not raw or REL_TARGET_RE.match(raw):
                continue
            base = acc_index.resolve(raw)
            if base is not None and sa_tail_ha(base['key']):
                edges.append(dict(commentary_L=rec['L'], commentary_title=rec['title'],
                                  base_L=base['L'], base_title=base['title'],
                                  side='E', marker='acc_on'))
        if not in_gap:
            continue
        # named-tika route on ACC titles (k1 already SLP1): strip the genre
        # suffix from this gap record's key and resolve the stem
        for sk in SUFFIX_KEYS:
            if sk and rec['key'].endswith(sk) and len(rec['key']) > len(sk):
                stem = rec['key'][:-len(sk)]
                if len(stem) >= 4:
                    base = acc_index.resolve(stem)
                    if base is not None and base['L'] != rec['L'] \
                       and sa_tail_ha(base['key']):
                        edges.append(dict(commentary_L=rec['L'],
                                          commentary_title=rec['title'],
                                          base_L=base['L'], base_title=base['title'],
                                          side='T', marker='acc_tika_title'))
                break
        # list-side: "<Title> comments on this record"
        for lm in ACC_L_MARKER_RE.finditer(rec['body']):
            raw = extract_target(rec['body'][lm.end() - 1:])
            if not raw or REL_TARGET_RE.match(raw):
                continue
            comm = acc_index.resolve(raw)
            if comm is not None and comm['L'] != rec['L']:
                edges.append(dict(commentary_L=comm['L'], commentary_title=comm['title'],
                                  base_L=rec['L'], base_title=rec['title'],
                                  side='L', marker='acc_list'))
    out, seen = [], set()
    for e in edges:
        key = (e['base_L'], e['commentary_L'])
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(
            commentary_cluster=cluster_for_L(e['commentary_L'], cf, L_map),
            commentary_title=e['commentary_title'],
            commentary_acc_L=e['commentary_L'],
            base_cluster=cluster_for_L(e['base_L'], cf, L_map),
            base_title=e['base_title'], base_title_raw=e['base_title'],
            side=e['side'], marker=e['marker'], provenance='acc'))
    return out


def cluster_for_L(acc_L, cf, L_map):
    ids = L_map.get(acc_L)
    if ids:
        return cf(ids[0])
    return 'acc:' + acc_L

