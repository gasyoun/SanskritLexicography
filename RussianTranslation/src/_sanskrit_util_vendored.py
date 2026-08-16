# -*- coding: utf-8 -*-
"""sanskrit_util — shared Sanskrit string helpers for the CDSL / Sanskrit-Lexicon repos.

Single source of truth, consolidated from WhitneyRoots/scripts/sanskrit_util.py and the
reader.js / linguistics.js twins so the same key/transcode logic is not re-typed per repo.
The JS port in ../../js/index.mjs is byte-for-byte behaviour-identical (proved by the shared
vectors in ../../vectors/vectors.json).

Public API
----------
to_slp1(iast)            IAST -> SLP1
from_slp1(slp1)          SLP1 -> IAST
to_roman(nums)           [1,2,...] gaṇa numbers -> ['I','II',...]
deva_to_iast(s)          Devanāgarī -> IAST
deva_to_slp1(s)          Devanāgarī -> SLP1 (direct; ळ -> L, round-trip partner of from_slp1)
iast_to_devanagari(s)    IAST -> Devanāgarī (real transcode: to_slp1 -> slp1_to_devanagari)
norm(s)                  EXACT diacritic-insensitive lookup key (Devanāgarī-aware)
nfold(s)                 norm() + every nasal folded to 'n' (recall fallback)
form_key(s)              length-PRESERVING comparison key (ā≠a) for verb/PPP form matching
normalize_sanskrit(s)    LOSSY ASCII-folding search key (ā→a, ś→s, ṃ→m …) — v3-explorer style

SLP1-side helpers (the CDSL dictionaries are SLP1-native, so they cannot be keyed via the
IAST helpers above without a transcode):
SLP1_VOWELS / SLP1_MARKS / SLP1_CONSONANTS / SLP1_ALPHABET   valid SLP1 character classes (str)
strip_slp1_accents(slp1) drop the SLP1 accent/candrabindu marks (/ \\ ^ ~)
slp1_norm(slp1)          CDSL SLP1 HEADWORD key: strip accents + trailing homonym digits; case kept
slp1_form_key(slp1)      length-preserving COMPARE key for SLP1 forms (= form_key ∘ from_slp1)
slp1_to_devanagari(slp1) SLP1 -> Devanāgarī (real transcode: virāma conjuncts + mātrās; the
                         round-trip partner of deva_to_slp1)
slp1_simplify(slp1)      fuzzy-match key: fold all SLP1 distinctions to plain ASCII (R→n, K→kh, …)

German-apparatus helpers (the PWG/PW dictionaries carry German lexicographic
METALANGUAGE — grammar labels, recurring formulae, bare function words — that a
translation pipeline must never treat as ordinary gloss prose; H2787 measured this
as the dominant TM defect class):
classify_german_metalanguage(text)   -> list of span dicts {start, end, text, category}
GERMAN_GRAMMAR_AB / GERMAN_GRAMMAR_BARE / GERMAN_FORMULA_AB / GERMAN_FORMULA_PHRASES /
GERMAN_FUNCTION_WORDS / GERMAN_AMBIGUOUS_TOKENS   the harvested token inventories

Pick the right key:
  - norm / nfold        : reversible, diacritic-insensitive (search & index lookup)
  - form_key            : compare *generated* forms vs *recorded* forms (length matters)
  - normalize_sanskrit  : crude ASCII bucket; prefer norm() unless you specifically want ASCII
"""
import re
import unicodedata

__version__ = "0.6.0"

__all__ = [
    "to_slp1", "from_slp1", "to_roman", "deva_to_iast", "deva_to_slp1", "iast_to_devanagari",
    "norm", "nfold", "form_key", "normalize_sanskrit",
    # SLP1-side API (the CDSL dictionaries are SLP1-native)
    "SLP1_VOWELS", "SLP1_MARKS", "SLP1_CONSONANTS", "SLP1_ALPHABET",
    "strip_slp1_accents", "slp1_norm", "slp1_form_key", "slp1_to_devanagari",
    # MW fuzzy-match simplification
    "slp1_simplify",
    # CDSL raw-source-line display renderer (SLP1-in-markup -> readable IAST)
    "source_line_to_iast", "source_text_to_iast",
    # German lexicographic-apparatus (metalanguage) detection for the PWG/PW pipelines
    "classify_german_metalanguage",
    "GERMAN_GRAMMAR_AB", "GERMAN_GRAMMAR_BARE", "GERMAN_FORMULA_AB",
    "GERMAN_FORMULA_PHRASES", "GERMAN_FUNCTION_WORDS", "GERMAN_AMBIGUOUS_TOKENS",
]

# ---- IAST -> SLP1 (longest-key-first; aspirates + diphthongs are digraphs) ----
_SLP1 = {
    'ai': 'E', 'au': 'O', 'kh': 'K', 'gh': 'G', 'ch': 'C', 'jh': 'J', 'ṭh': 'W', 'ḍh': 'Q',
    'th': 'T', 'dh': 'D', 'ph': 'P', 'bh': 'B',
    'ā': 'A', 'ī': 'I', 'ū': 'U', 'ṛ': 'f', 'ṝ': 'F', 'ḷ': 'x', 'ḹ': 'X',
    'ṃ': 'M', 'ṁ': 'M', 'ḥ': 'H', 'ṅ': 'N', 'ñ': 'Y', 'ṭ': 'w', 'ḍ': 'q', 'ṇ': 'R',
    'ś': 'S', 'ṣ': 'z', 'ḻ': 'L',
    'a': 'a', 'i': 'i', 'u': 'u', 'e': 'e', 'o': 'o', 'k': 'k', 'g': 'g', 'c': 'c', 'j': 'j',
    't': 't', 'd': 'd', 'n': 'n', 'p': 'p', 'b': 'b', 'm': 'm', 'y': 'y', 'r': 'r', 'l': 'l',
    'v': 'v', 's': 's', 'h': 'h',
}


def to_slp1(iast):
    """IAST -> SLP1. Longest-key-first so aspirates/diphthongs (kh, ai) map as one phoneme."""
    out, i, s = [], 0, (iast or '')
    while i < len(s):
        two = s[i:i + 2]
        if two in _SLP1:
            out.append(_SLP1[two]); i += 2; continue
        out.append(_SLP1.get(s[i], s[i])); i += 1
    return ''.join(out)


_ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X'}


def to_roman(nums):
    """[1,4,10] -> ['I','IV','X']; numbers outside 1..10 are dropped."""
    return [_ROMAN[n] for n in nums if n in _ROMAN]


# ---- SLP1 -> IAST (inverse of _SLP1; SLP1 is one ASCII char per phoneme) ----
_FROM_SLP1 = {
    'A': 'ā', 'I': 'ī', 'U': 'ū', 'f': 'ṛ', 'F': 'ṝ', 'x': 'ḷ', 'X': 'ḹ',
    'E': 'ai', 'O': 'au', 'M': 'ṃ', 'H': 'ḥ',
    'K': 'kh', 'G': 'gh', 'N': 'ṅ', 'C': 'ch', 'J': 'jh', 'Y': 'ñ',
    'w': 'ṭ', 'W': 'ṭh', 'q': 'ḍ', 'Q': 'ḍh', 'R': 'ṇ',
    'T': 'th', 'D': 'dh', 'P': 'ph', 'B': 'bh',
    'S': 'ś', 'z': 'ṣ', 'L': 'ḻ',
}


def from_slp1(slp1):
    """SLP1 -> IAST. Used to render vidyut-prakriya output (SLP1) for the reader."""
    return ''.join(_FROM_SLP1.get(ch, ch) for ch in (slp1 or ''))


# ---- Devanāgarī -> IAST (port of reader.js deva2iast; inherent-'a' + virāma aware) ----
_DV_VOWEL = {
    'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū', 'ऋ': 'ṛ', 'ॠ': 'ṝ',
    'ऌ': 'ḷ', 'ॡ': 'ḹ', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
}
_DV_MATRA = {
    'ा': 'ā', 'ि': 'i', 'ी': 'ī', 'ु': 'u', 'ू': 'ū', 'ृ': 'ṛ', 'ॄ': 'ṝ', 'ॢ': 'ḷ',
    'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
}
_DV_CONS = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ṅ', 'च': 'c', 'छ': 'ch', 'ज': 'j',
    'झ': 'jh', 'ञ': 'ñ', 'ट': 'ṭ', 'ठ': 'ṭh', 'ड': 'ḍ', 'ढ': 'ḍh', 'ण': 'ṇ', 'त': 't',
    'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n', 'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh',
    'म': 'm', 'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'ś', 'ष': 'ṣ', 'स': 's',
    'ह': 'h', 'ळ': 'ḷ',
}
_DV_MARK = {'ं': 'ṃ', 'ः': 'ḥ', 'ँ': 'ṃ'}
_VIRAMA = '्'


def deva_to_iast(s):
    """Devanāgarī -> IAST. Inherent 'a' supplied after a bare consonant unless a virāma or
    mātrā follows; avagraha (ऽ) dropped. Mirror of reader.js deva2iast()."""
    s = s or ''
    out = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch in _DV_CONS:
            out.append(_DV_CONS[ch])
            nx = s[i + 1] if i + 1 < n else ''
            if nx == _VIRAMA:
                i += 1                       # bare consonant (conjunct)
            elif nx in _DV_MATRA:
                out.append(_DV_MATRA[nx]); i += 1
            else:
                out.append('a')             # inherent vowel
        elif ch in _DV_VOWEL:
            out.append(_DV_VOWEL[ch])
        elif ch in _DV_MARK:
            out.append(_DV_MARK[ch])
        elif ch == 'ऽ':
            pass                             # avagraha — drop
        else:
            out.append(ch)
        i += 1
    return ''.join(out)


# ---- Devanāgarī -> SLP1 (direct; the ळ→L vs x decision is made HERE) ----------------
# Why not just to_slp1(deva_to_iast(s)): deva_to_iast collapses ळ (U+0933, retroflex ḻa) onto
# vocalic ḷ — both render as IAST ḷ (U+1E37) — so to_slp1 would map the result to 'x' (vocalic
# ḷ), losing the distinction. SLP1 keeps them apart (ळ = 'L', the Vedic retroflex; ऌ = 'x'), and
# that can't be recovered after the IAST step. So transcode Devanāgarī → SLP1 directly: derive the
# maps from the IAST maps once (so they track to_slp1 exactly) and override ळ → 'L'. deva_to_slp1
# is therefore the round-trip partner of from_slp1 ('L' → ḻ), where to_slp1∘deva_to_iast is not.
_DV_VOWEL_SLP1 = {k: to_slp1(v) for k, v in _DV_VOWEL.items()}
_DV_MATRA_SLP1 = {k: to_slp1(v) for k, v in _DV_MATRA.items()}
_DV_CONS_SLP1 = {k: to_slp1(v) for k, v in _DV_CONS.items()}
_DV_CONS_SLP1['ळ'] = 'L'        # retroflex ḻa — NOT 'x' (vocalic ḷ, from ऌ); see note above
_DV_MARK_SLP1 = {k: to_slp1(v) for k, v in _DV_MARK.items()}


def deva_to_slp1(s):
    """Devanāgarī -> SLP1, direct (inherent 'a' supplied after a bare consonant unless a virāma or
    mātrā follows; avagraha ऽ dropped; danda/other non-Devanāgarī chars pass through). Unlike
    to_slp1(deva_to_iast(s)), ळ (U+0933) maps to 'L' (retroflex ḻa), not 'x' (vocalic ḷ) — so this
    is the round-trip partner of from_slp1. Same traversal as deva_to_iast (kept in lock-step)."""
    s = s or ''
    out = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch in _DV_CONS_SLP1:
            out.append(_DV_CONS_SLP1[ch])
            nx = s[i + 1] if i + 1 < n else ''
            if nx == _VIRAMA:
                i += 1                       # bare consonant (conjunct)
            elif nx in _DV_MATRA_SLP1:
                out.append(_DV_MATRA_SLP1[nx]); i += 1
            else:
                out.append('a')             # inherent vowel
        elif ch in _DV_VOWEL_SLP1:
            out.append(_DV_VOWEL_SLP1[ch])
        elif ch in _DV_MARK_SLP1:
            out.append(_DV_MARK_SLP1[ch])
        elif ch == 'ऽ':
            pass                             # avagraha — drop
        else:
            out.append(ch)
        i += 1
    return ''.join(out)


# ---- SLP1 -> Devanāgarī (real transcode: virāma conjuncts + mātrās) -----------------
# The round-trip partner of deva_to_slp1: for canonical SLP1, deva_to_slp1(slp1_to_devanagari(s))
# == s (proved on the full alphabet + 1000 real MW headwords by the round-trip property test).
# Unlike iast_to_devanagari (a display-only replace with no orthographic shaping), this supplies
# the virāma between clustered consonants and picks independent-vowel vs mātrā by position, so the
# output is well-formed Devanāgarī. The vowel/mātrā/consonant maps are INVERTED from the same
# Devanāgarī→SLP1 maps deva_to_slp1 uses (so the two stay in lock-step); only the 3 marks are given
# explicitly (M→anusvāra, H→visarga, ~→candrabindu) because both anusvāra and candrabindu map back
# to 'M' on the Devanāgarī→SLP1 side and cannot be inverted unambiguously.
#
# Not round-trip stable (documented, matching deva_to_slp1): candrabindu (~ → ँ → 'M' anusvāra) and
# avagraha (' → ऽ, which deva_to_slp1 drops). SLP1 accents (/ \ ^) pass through unchanged.
_SLP1_TO_DV_VOWEL = {v: k for k, v in _DV_VOWEL_SLP1.items()}       # 'A'->'आ', 'e'->'ए', 'E'->'ऐ', …
_SLP1_TO_DV_MATRA = {v: k for k, v in _DV_MATRA_SLP1.items()}       # 'A'->'ा', 'e'->'े', 'E'->'ै', …
_SLP1_TO_DV_MATRA['a'] = ''                                        # inherent 'a' takes no sign
_SLP1_TO_DV_CONS = {v: k for k, v in _DV_CONS_SLP1.items()}        # 'k'->'क', 'L'->'ळ', …
_SLP1_TO_DV_MARK = {'M': 'ं', 'H': 'ः', '~': 'ँ'}                  # anusvāra / visarga / candrabindu
_SLP1_VOWEL_SET = set(_SLP1_TO_DV_VOWEL)
_SLP1_CONS_SET = set(_SLP1_TO_DV_CONS)


def slp1_to_devanagari(slp1):
    """SLP1 -> Devanāgarī, a real transcode (not a display replace): supplies the virāma between
    clustered consonants and renders each vowel as an independent sign or a mātrā by position, so
    the result is well-formed Devanāgarī and is the round-trip partner of deva_to_slp1. Avagraha
    (') -> ऽ; SLP1 accents (/ \\ ^) pass through. See module note for the (documented) candrabindu /
    avagraha round-trip asymmetries."""
    s = slp1 or ''
    out = []
    pending_cons = False        # a consonant sign was emitted and still awaits its vowel/virāma
    for ch in s:
        if ch in _SLP1_CONS_SET:
            if pending_cons:
                out.append(_VIRAMA)                 # previous consonant had no vowel -> conjunct
            out.append(_SLP1_TO_DV_CONS[ch])
            pending_cons = True
        elif ch in _SLP1_VOWEL_SET:
            if pending_cons:
                out.append(_SLP1_TO_DV_MATRA[ch])   # attach as mātrā ('' for inherent 'a')
                pending_cons = False
            else:
                out.append(_SLP1_TO_DV_VOWEL[ch])   # independent vowel sign
        else:                                       # mark, avagraha, accent, digit, space, other
            if pending_cons:
                out.append(_VIRAMA)                 # close the bare consonant first
                pending_cons = False
            if ch == "'":
                out.append('ऽ')                     # avagraha
            else:
                out.append(_SLP1_TO_DV_MARK.get(ch, ch))
    if pending_cons:
        out.append(_VIRAMA)                         # trailing bare consonant
    return ''.join(out)


# ---- IAST -> Devanāgarī (real transcode via to_slp1 -> slp1_to_devanagari composition;
# virāma + mātrā aware. Previously a naive longest-key-first character substitution that
# never applied virāma/mātrā and emitted an independent vowel sign after every consonant
# (wrong on 9 of 9 basic words, e.g. 'ka' -> कअ instead of क). Fixed per H1394.) ----


def iast_to_devanagari(text):
    """IAST -> Devanagari via the to_slp1 -> slp1_to_devanagari composition (a real transcode:
    virama + matra aware). Previously a naive character-substitution that was wrong on 9 of 9
    basic words (e.g. 'ka' -> koa instead of ka-in-devanagari); fixed per the D1 SLP1-round-trip
    ruling."""
    return slp1_to_devanagari(to_slp1((text or '').lower()))


# ---- normalization keys ----------------------------------------------------
_DEVA_RE = re.compile('[ऀ-ॿ]')

# Whitespace stripped/collapsed IDENTICALLY to the JS port. JS String.trim() and JS \s strip the
# BOM/ZWNBSP U+FEFF (which sneaks in when a file is read without utf-8-sig — the CDSL BOM pitfall),
# while Python str.strip()/\s do not (and conversely Python strips U+0085 NEL, JS does not). Pin an
# explicit class so norm()/form_key()/slp1_norm() yield the SAME key in both languages.
_WS_CHARS = '\t\n\x0b\x0c\r \x85\xa0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff'
_WS_RUN = re.compile('[' + re.escape(_WS_CHARS) + ']+')


def norm(s):
    """EXACT diacritic-insensitive lookup key: (Devanāgarī->IAST if present), NFD, drop all
    combining marks, NFC, lower, strip. Mirror of reader.js norm()."""
    s = s or ''
    if _DEVA_RE.search(s):
        s = deva_to_iast(s)
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return unicodedata.normalize('NFC', s).lower().strip(_WS_CHARS)


def nfold(s):
    """NASAL-FOLDED recall key: norm() then fold every m/n (and homorganic nasals, already
    reduced to n/m by norm) to 'n'. FALLBACK index only — keeps am/an distinct on the exact
    key while letting anusvāra spellings reach homorganic forms. Mirror of reader.js nfold()."""
    return re.sub('[mn]', 'n', norm(s))


# ---- length-preserving comparison key (vidyut ↔ warnemyr ↔ DCS form matching) ----
# Unlike norm()/nfold(), form_key() PRESERVES vowel length (ā≠a): krānta ≠ kranta is a real
# difference when comparing generated vs recorded forms. It folds anusvāra + homorganic nasals
# -> n (krāṃta == krānta), strips the nom-sg visarga, and drops PITCH accents on a vowel — but
# keeps ś (= s + U+0301, same codepoint as the acute accent) and the retroflex/vocalic dots.
_FK_ACCENT = {'́', '̀', '॑', '॒'}   # acute, grave, Vedic svarita/anudātta
_FK_VOWELS = set('aāiīuūṛṝḷḹeēoō')


def form_key(s):
    """Length-preserving fold for comparing Sanskrit word forms. See module note above."""
    s = (s or '').strip(_WS_CHARS).lower()
    if s in ('-', '–', '—'):                    # warnemyr 'no recorded form' placeholder -> blank
        return ''
    s = re.sub('ḥ$', '', s)                     # nom-sg visarga
    s = re.sub('[ṃṁṅñṇ]', 'n', s)              # anusvāra + ṅ/ñ/ṇ -> n (precomposed, before NFD)
    out = []
    for ch in unicodedata.normalize('NFD', s):
        if ch in _FK_ACCENT:
            j = len(out) - 1                    # walk back past ALL combining marks to base letter
            while j >= 0 and unicodedata.combining(out[j]):
                j -= 1
            base = unicodedata.normalize('NFC', ''.join(out[j:])) if j >= 0 else ''
            if base in _FK_VOWELS:              # accent on a (long/vocalic) vowel -> drop; on s (->ś) -> keep
                continue
        out.append(ch)
    return unicodedata.normalize('NFC', ''.join(out))


# ---- lossy ASCII-folding search key (v3-explorer normalizeSanskrit) --------
_NS_MAP = {
    'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṝ': 'r', 'ḷ': 'l', 'ḹ': 'l',
    'ṅ': 'n', 'ñ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ś': 's', 'ṣ': 's',
    'ḥ': 'h', 'ṃ': 'm',
}
_NS_RE = re.compile('[āīūṛṝḷḹṅñṭḍṇśṣḥṃ]')


def normalize_sanskrit(text):
    """LOSSY ASCII-folding key (ā→a, ś→s, ṭ→t, ṃ→m …): collapses length, retroflex AND nasal
    in one pass. NOT reversible and NOT the same as norm(); kept for v3-explorer parity. Prefer
    norm() unless you specifically need a bare-ASCII bucket. Port of linguistics.js normalizeSanskrit()."""
    if not text:
        return ''
    s = unicodedata.normalize('NFD', text)
    s = re.sub('[̀-ͯ]', '', s)
    s = _NS_RE.sub(lambda m: _NS_MAP.get(m.group(0), m.group(0)), s)
    return s.lower()


# ---- SLP1-side API ---------------------------------------------------------
# The CDSL dictionaries store headwords in SLP1, where case is PHONEMIC (S=ś≠s,
# T=th≠t, …) — so the IAST helpers above can't key them without a transcode, and
# every CDSL repo had re-rolled its own SLP1 alphabet + headword normalizer.
# SLP1 character classes (strings; build a set() if you need membership tests).
SLP1_VOWELS = 'aAiIuUfFxXeEoO'      # f/F = vocalic ṛ/ṝ, x/X = vocalic ḷ/ḹ, E = ai, O = au
SLP1_MARKS = 'MH~'                  # anusvāra, visarga, candrabindu
SLP1_CONSONANTS = 'kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL'   # L = Vedic retroflex ḻa
SLP1_ALPHABET = SLP1_VOWELS + SLP1_MARKS + SLP1_CONSONANTS   # valid SLP1 letters (avagraha ' excluded)

_SLP1_ACCENTS = re.compile(r'[/\\^~]')   # udātta / anudātta / svarita / candrabindu
_SLP1_TRAILING_NUM = re.compile(r'\d+$')
# whitespace collapse uses the unified _WS_RUN / _WS_CHARS (defined with norm()) so SLP1 keys
# match the JS port on the BOM/NEL edge cases too.


def strip_slp1_accents(slp1):
    """Remove the SLP1 accent/candrabindu marks (/ \\ ^ ~) — the marks the CDSL headword
    convention drops before aligning lemmas across dictionaries."""
    return _SLP1_ACCENTS.sub('', slp1 or '')


def slp1_norm(slp1):
    """Canonical CDSL SLP1 HEADWORD key: strip accent marks, drop the trailing homonym-index
    digits, collapse whitespace. SLP1 case is PRESERVED (phonemic). This is the shared form of
    the per-repo normalize_lemma / normalizeSlp1Lemma headword normalizers."""
    s = strip_slp1_accents(slp1 or '')
    s = _SLP1_TRAILING_NUM.sub('', s)
    return _WS_RUN.sub(' ', s).strip(_WS_CHARS)


def slp1_form_key(slp1):
    """Length-preserving COMPARE key for SLP1 word forms (vidyut/DCS/dict cross-checks):
    SLP1 -> IAST -> form_key, so anusvāra folds to its homorganic nasal and the nom-sg visarga
    drops while vowel length and ś/retroflex survive. Unlike slp1_norm() it keeps homonym digits."""
    return form_key(from_slp1(strip_slp1_accents(slp1 or '')))


def slp1_simplify(slp1):
    """Fuzzy-match key: fold ALL SLP1 distinctions to plain ASCII — the lossy extreme of the SLP1
    key family (slp1_norm keeps case+everything; slp1_form_key keeps length+ś+dots; this keeps
    almost nothing). Designed for building and querying MW headword indexes (e.g. mw_en_tm.json).

    Works identically on both index side (MW headword keys) and query side (indic_transliteration /
    to_slp1 output) because both use **standard SLP1** where ``R=ṇ`` (retroflex nasal).

    ⚠️ Encoding trap: mw_en_tm.json uses standard SLP1, NOT an older Cologne convention. guṇa =
    ``guRa`` in MW. Forgetting ``R→n`` maps guṇa to gūna ("voided as ordure"). This handles it.

    Typical pattern::

        idx = {slp1_simplify(k): slp1_k for slp1_k in mw_data}
        hit = idx.get(slp1_simplify(query_token))
    """
    s = slp1 or ''
    s = (s.replace('K', 'kh').replace('G', 'gh')
          .replace('C', 'ch').replace('J', 'jh')
          .replace('T', 'th').replace('D', 'dh')
          .replace('P', 'ph').replace('B', 'bh'))
    s = s.replace('S', 's').replace('z', 's')
    s = s.replace('Y', 'n').replace('N', 'n').replace('R', 'n')   # R=ṇ is the critical case
    s = s.replace('A', 'a').replace('I', 'i').replace('U', 'u')
    s = s.replace('E', 'ai').replace('O', 'au')
    s = s.replace('f', 'r').replace('F', 'r').replace('x', 'l').replace('X', 'l')
    s = s.replace('M', 'm').replace('H', '')
    s = s.replace('W', 'th').replace('Q', 'dh')
    s = s.replace('w', 't').replace('q', 'd')
    s = s.replace('L', 'l')                                        # Vedic retroflex ḻa
    return s.lower()


# ---- CDSL raw source line -> readable IAST (display layer over from_slp1) ----
# A raw csl-orig line is SLP1 inside CDSL markup, unreadable to a human. These
# render it to IAST honoring each dictionary's encoding: MW <s>…</s>;
# PW/PWG/AP/WIL {#…#} (with the meaning language in {%…%}, left as-is);
# VCP/SKD whole-line SLP1 prose. The markup shell (tags, [Page…] markers, the ¦
# headword separator) is stripped. `code` is the csl-orig dict code
# (mw, ap, pwg, pw, wil, vcp, skd). Non-SLP1 spans — glosses, <ls> citations,
# grammar abbreviations like "f." — are preserved.
_PROSE_SLP1_DICTS = frozenset({'vcp', 'skd'})


def _strip_cdsl_markup(text):
    text = re.sub(r'<info[^>]*/?>', '', text, flags=re.I)  # metadata self-closing tags
    text = re.sub(r'\[Page[^\]]*\]', '', text)             # VCP/SKD page markers
    return re.sub(r'<[^>]+>', '', text)                    # any remaining tag shell


def _clean_cdsl(text):
    text = text.replace('¦', ' ')                    # ¦ headword/body separator
    text = re.sub(r'\s+([,.;:!?])', r'\1', text)          # pull punctuation back
    return re.sub(r'\s+', ' ', text).strip()


def source_line_to_iast(text, code):
    """One raw csl-orig source line -> readable IAST. `code` is the dict code."""
    if text is None:
        return ''
    c = (code or '').lower()
    if c in _PROSE_SLP1_DICTS:
        s = re.sub(r"[A-Za-z~']+", lambda m: from_slp1(m.group(0)), str(text))
        return _clean_cdsl(_strip_cdsl_markup(s))
    s = str(text)
    s = re.sub(r'\{[#@]([^#@]*)[#@]\}', lambda m: from_slp1(m.group(1)), s)   # {#…#}, {@…@}
    s = re.sub(r'(?i)<s\d?>([^<]*)</s\d?>', lambda m: from_slp1(m.group(1)), s)  # MW <s>…</s>
    s = re.sub(r'\{%([^%]*)%\}', lambda m: m.group(1), s)                     # meaning: unwrap, keep
    return _clean_cdsl(_strip_cdsl_markup(s))


def source_text_to_iast(text, code):
    """Multi-line snippet -> IAST, line by line (preserves line breaks)."""
    if text is None:
        return ''
    return '\n'.join(source_line_to_iast(line, code) for line in str(text).split('\n'))


# ---- German lexicographic-apparatus (metalanguage) detection -----------------
# The PWG/PW dictionaries write their APPARATUS in German: grammar labels
# (<ab>adj.</ab>, "m. f. n."), recurring formulae ("am Ende eines Comp.",
# "mit Ergänzung von", "vgl."), and bare function words reused as placeholders
# ("eines", "die"). A DE→RU translation pipeline that treats such a span as an
# ordinary gloss produces the H2787 arm-B defect class ("eines" → «поручать
# кому-л.», "die" → «боги»). The token inventories below are HARVESTED, not
# invented, from the pwg_ru sources that already owned them:
#   GERMAN_GRAMMAR_AB / GERMAN_FORMULA_AB / GERMAN_FORMULA_PHRASES
#       ← SanskritLexicography RussianTranslation/src/pwg_tm_fragmentize.py
#         (GRAMMAR_AB / FORMULA_AB / FORMULA_PHRASES), plus the H2684 repair
#         extras (demin., personif., Uebertr.) and the corpus-measured
#         "mit Ergänzung von" (82×) / "an der Spitze eines Comp." (43×) /
#         "im Comp.(,) vorangehend" formulae (H2787 defect list).
#   GERMAN_GRAMMAR_BARE ← compile_translatable.py GRAM (NWS-layer labels).
#   GERMAN_FUNCTION_WORDS ← microstructure.py FUNC_DE ∪ pwg_mask.py DE_FUNCTION.
# Ambiguity is explicit: "so" is both apparatus and a real gloss word, and a bare
# "Ergänzung" is apparatus only inside its formula frame — as sole content each
# classifies 'uncertain'; the CONSUMER treats uncertain as not-gloss and logs.
GERMAN_GRAMMAR_AB = frozenset({
    'adj.', 'adv.', 'm.', 'f.', 'n.', 'm. n.', 'f. n.', 'm. f.', 'm. f. n.',
    'partic.', 'part.', 'caus.', 'desid.', 'intens.', 'pass.', 'med.', 'act.',
    'nom.', 'acc.', 'instr.', 'dat.', 'abl.', 'gen.', 'loc.', 'voc.',
    'sg.', 'du.', 'pl.', 'inf.', 'abs.', 'ger.', 'impf.', 'perf.', 'aor.',
    'opt.', 'impv.', 'fut.', 'cond.', 'ppp.', 'pp.', 'subst.', 'interj.',
    'pron.', 'num.', 'indecl.', 'comp.', 'superl.', 'denomin.', 'desid',
    'partic', 'caus',
})
GERMAN_GRAMMAR_BARE = frozenset({
    'Subst', 'Adj', 'Adv', 'Indekl', 'PostP', 'mfn', 'ifc', 'NPr',
    'Pl', 'Sg', 'Du', 'Akk', 'Lok', 'Dat', 'Gen', 'Instr', 'Nom', 'Vok',
})
GERMAN_FORMULA_AB = frozenset({
    'vgl.', 's. u.', 's. d.', 's. v.', 's. u. d.', 'fgg.', 'fg.', 'dass.',
    'ebend.', 'u.s.w.', 'desgl.', 'dgl.', 'sc.', 'scil.', 's. u. d. W.',
    # H2684 one-bounded-repair extras (PWG_TM_GROK46_WAVE1_TRACK_B_14-08-2026.md)
    'demin.', 'personif.', 'uebertr.',
})
# Pattern STRINGS (compile with re.IGNORECASE); donor-shaped so
# pwg_tm_fragmentize.FORMULA_PHRASES can compile these verbatim.
GERMAN_FORMULA_PHRASES = (
    r'am Anf(?:ange|\.) eines Comp(?:ositums?|\.)?',
    r'am Ende eines Comp(?:ositums?|\.)?',
    r'an der Spitze eines Comp(?:ositums?|\.)?',
    r'mit Ergänzung von',
    r'im Comp\.(?:,? vorangehend[a-z]*)?',
    r'in Verbindung mit',
    r's\.\s*u\.\s*d\.\s*W\.',
)
GERMAN_FUNCTION_WORDS = frozenset(
    'der die das den dem des ein eine einen einem eines einer und oder aber auf '
    'in an zu von mit bei nach für so als wie am im zum zur ist sind war wird '
    'auch nur noch nicht wo wenn dass vor über unter durch ohne um bis'.split())
GERMAN_AMBIGUOUS_TOKENS = frozenset({'so', 'ergänzung'})

# Guards: no German letter directly before/after a match ("\b" mishandles umlauts,
# and JS "\b" would disagree — explicit classes keep the two ports identical).
_GM_L = '(?<![A-Za-zäöüßÄÖÜ])'
_GM_R = '(?![A-Za-zäöüßÄÖÜ])'
_GM_PHRASE_RES = tuple(re.compile(_GM_L + p + _GM_R, re.I) for p in GERMAN_FORMULA_PHRASES)


def _gm_token_pattern(tok):
    # '.' is literal; a single space matches any plain whitespace run (kept as
    # [ \t\n\r]+, NOT \s+, because Python and JS disagree on the \s class edges).
    return tok.replace('.', r'\.').replace(' ', '[ \t\n\r]+')


_GM_DOTTED_RE = re.compile(
    _GM_L + '(?:' + '|'.join(
        _gm_token_pattern(t) for t in sorted(GERMAN_GRAMMAR_AB | GERMAN_FORMULA_AB,
                                             key=lambda t: (-len(t), t))) + ')' + _GM_R,
    re.I)
_GM_BARE_RE = re.compile(
    _GM_L + '(?:' + '|'.join(sorted(GERMAN_GRAMMAR_BARE, key=lambda t: (-len(t), t)))
    + ')' + _GM_R)   # case-SENSITIVE: these are NWS-layer labels, exact form
_GM_WORD_RE = re.compile('[A-Za-zäöüßÄÖÜ]+')
_GM_WS_RUN = re.compile('[ \t\n\r]+')
# dot-ensured lowercase lookup sets for classifying a dotted match
_GM_FORMULA_NORM = frozenset(t if t.endswith('.') else t + '.' for t in GERMAN_FORMULA_AB)
_GM_GRAMMAR_NORM = frozenset(t if t.endswith('.') else t + '.' for t in GERMAN_GRAMMAR_AB)


def classify_german_metalanguage(text):
    """Detect German lexicographic-apparatus (metalanguage) spans in ``text``.

    Returns a list of span dicts ``{'start': int, 'end': int, 'text': str,
    'category': str}`` sorted by position, categories:

    - ``'grammar_label'``       — POS/case/number abbreviations (``adj.``, ``m. f. n.``, ``Akk``)
    - ``'recurring_formula'``   — editorial formulae (``vgl.``, ``am Ende eines Comp.``,
                                  ``mit Ergänzung von``, ``im Comp. vorangehend``, ``demin.``)
    - ``'function_word'``       — the WHOLE text is bare German function words
                                  (``eines``, ``die``) — an apparatus placeholder, not a gloss
    - ``'uncertain'``           — the whole text is an ambiguous token (``so``,
                                  ``Ergänzung``): apparatus in one reading, gloss in another.
                                  Consumers treat uncertain as NOT-gloss and log it.

    Mid-text function words ("Name eines Baumes") are NOT flagged — only a span
    consisting entirely of function/ambiguous words is apparatus; ordinary German
    gloss prose returns ``[]``. Offsets are code-unit-identical between the Python
    and JS ports for BMP text (all German apparatus is BMP).
    """
    s = text or ''
    spans = []

    def _keep(start, end, txt, category):
        for sp in spans:
            if start < sp['end'] and sp['start'] < end:
                return
        spans.append({'start': start, 'end': end, 'text': txt, 'category': category})

    for rx in _GM_PHRASE_RES:
        for m in rx.finditer(s):
            _keep(m.start(), m.end(), m.group(0), 'recurring_formula')
    for m in _GM_DOTTED_RE.finditer(s):
        tok = _GM_WS_RUN.sub(' ', m.group(0)).lower()
        if not tok.endswith('.'):
            tok += '.'
        cat = 'recurring_formula' if tok in _GM_FORMULA_NORM else 'grammar_label'
        _keep(m.start(), m.end(), m.group(0), cat)
    for m in _GM_BARE_RE.finditer(s):
        _keep(m.start(), m.end(), m.group(0), 'grammar_label')
    if spans:
        spans.sort(key=lambda sp: (sp['start'], sp['end']))
        return spans

    # nothing matched: is the WHOLE text an apparatus placeholder / ambiguous token?
    words = [w.lower() for w in _GM_WORD_RE.findall(s)]
    if words and all(w in GERMAN_FUNCTION_WORDS or w in GERMAN_AMBIGUOUS_TOKENS
                     for w in words):
        first = _GM_WORD_RE.search(s)
        start = first.start()
        end = len(s)
        while end > start and s[end - 1] in ' \t\n\r':
            end -= 1
        cat = ('uncertain'
               if all(w in GERMAN_AMBIGUOUS_TOKENS for w in words) else 'function_word')
        return [{'start': start, 'end': end, 'text': s[start:end], 'category': cat}]
    return []
