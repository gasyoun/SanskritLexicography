"""NCC name-authority adjudication vocabulary and helpers (H7215).

Static side of the C3 §4 ladder: the seed rows, genre/series token lists,
annotation-tail test, diacritic-insensitive fold regex, deletion variants.
Split out of ncc_name_authority.py for the token-size gate (estate tool
convention, Uprava PR #5383).
"""
import re

# H7202's committed authority alias, recorded as table row #1.  The build
# still resolves it through FOLD_ALIASES (match_key stage); the row exists
# so the authority table is the one complete record of committed merges.
SEED_ROWS = [
    dict(fold='saundaryalahari', edge_n=92, as_base_n=92, as_comm_n=0,
         raw_sample='Saundaryalahari',
         verdict='MERGE', klass='seed-fold-alias',
         merge_cluster='anandalahari', merge_title='Ānandalaharī',
         evidence='H7202 FOLD_ALIASES: 92 "C. on the Saundaryalahari" marker '
                  'targets; NCC files the work as Anandalahari; only rival '
                  'claimant is a stuti self-declaring the alias',
         source='seed:h7202-fold-alias'),
]
SEED_FOLDS = {r['fold']: r['merge_cluster'] for r in SEED_ROWS}

# Genre/stem words: a remainder or whole fold in this set is a bare genre
# title ("C. tīkā", "C. vṛtti"), never a work identity.  Same vocabulary the
# H7202 marker routes use, plus the base-work nouns seen in the t-bin.
GENRE_FOLDS = {
    'tika', 'tika', 'vyakhya', 'bhasya', 'vrtti', 'tippani', 'dipika',
    'vivarana', 'vivrti', 'uddyota', 'pradipa', 'prakasa', 'pradipika',
    'manjari', 'prabha', 'glossa', 'commentary', 'comm', 'commentaries',
    'kavya', 'stotra', 'stuti', 'sutra', 'sutra', 'samhita', 'karika',
    'sutratika', 'tk', 'tikap', 'grantha', 'prakarana', 'karika',
}
# Library / edition series and page-volume tokens (annotation tails).
SERIES_TOKENS = {
    'bori', 'adar', 'adyar', 'trav', 'travuni', 'chani', 'bik', 'im', 'mt',
    'zdmg', 'ibid', 'jbor', 'js', 'ja', 'zdm', 'ksts', 'tss', 'ks', 'ksi',
    'md', 'ms', 'mss', 'p', 'pp', 'vol', 'no', 'ed', 'see', 'also', 'cf',
    'jain', 'law', 'pandey', 'nanjio', 'oppert', 'vidyabhushan', 'gackwad',
    'oriental', 'institute', 'series', 'library', 'university', 'press',
    'fort', 'madras', 'bombay', 'calcutta', 'benares', 'kasipuram',
    'madrasgovt', 'orissasahitya', 'academy', 'sanskrit', 'college',
    'research', 'department', 'dhar', 'nsp', 'kavyamala', 'km', 'ns',
    'anandasrama', 'asl', 'hel', 'bss', 'vss', 'ts', 'trs', 'bssoas',
    'on', 'and', 'an', 'or', 'with', 'for', 'of', 'the', 'gr', 'comp',
    'by', 'transl',
}
ROMAN_RE = re.compile(r'^(?=[ivxlcdm]+$)'
                      r'm{0,3}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$')


def annot_token_ok(tok):
    """Annotation-tail test for one raw token: series/see/page lexicon,
    roman numeral, short alpha (sigla: BP, MT, GD), or digits/punct junk."""
    t = fold_token(re.sub(r"[|()\[\]{}?,.;:'\"0-9]+", '', tok))
    if not t:                      # was digits/punct only
        return True
    return (t in SERIES_TOKENS or ROMAN_RE.match(t) is not None
            or len(t) <= 3)


def fold_token(s):
    """Lowercase ascii fold for annotation tokens (subset of the C3 fold:
    strip diacritics, keep a-z)."""
    out = []
    for ch in re.sub(r'[^\w\s]', '', s, flags=re.U):
        if ch.isascii() and ch.isalpha():
            out.append(ch.lower())
    return ''.join(out)


def fold_regex(core):
    """Diacritic-insensitive regex for a folded core over raw text."""
    cls = {'a': 'aā', 'i': 'iī', 'u': 'uū', 'r': 'rṛṝ', 'l': 'lḷḹ',
           't': 'tṭ', 'd': 'dḍ', 'n': 'nṅñṇ', 's': 'sśṣ', 'm': 'mṃṁ',
           'h': 'hḥ', 'e': 'e', 'o': 'o', 'k': 'k', 'g': 'g', 'c': 'c',
           'j': 'j', 'p': 'p', 'b': 'b', 'y': 'y', 'v': 'v', 'w': 'w'}
    parts = []
    for ch in core:
        if ch.isalpha():
            c = cls.get(ch, ch)
            parts.append('[' + c + c.upper() + ']')
        else:
            parts.append(re.escape(ch))
    return re.compile(''.join(parts), re.U)


def del1_variants(s):
    return {s[:i] + s[i + 1:] for i in range(len(s))}
