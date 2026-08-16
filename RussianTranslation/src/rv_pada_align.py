#!/usr/bin/env python
r"""Pāda-granular alignment of PWG's Ṛgveda citations to Elizarenkova's published Russian.

H2850 (MG crosswalk-review point P8). The rule this module enforces:

    Where a published Russian translation already exists for a cited Ṛgvedic locus,
    the pipeline ALIGNS to it at pāda granularity and NEVER re-translates it.

Three pieces, in order of importance:

1. **The pāda-granular join.** ``align(quote_slp1, mandala, hymn, verse)`` takes the
   Sanskrit PWG actually quotes (SLP1 with Vedic accents, straight out of ``{#…#}``)
   and returns exactly the published Russian line(s) for the pāda(s) that quotation
   covers. Quotations routinely span two pādas — ``ṚV. 7,84,1`` in ``parigā`` quotes
   pādas c+d — so a verse-granular join is not good enough. A verse-granular read is
   also how a session ends up attributing to a translator a rendering she never made
   (SanskritLexicography FINDINGS §544, `guda` at RV 10.163.3).

2. **The agreement verdict.** ``verdict(...)`` scores the PWG Russian gloss governing a
   citation against the published Russian for the pādas quoted: ``agrees`` /
   ``diverges`` / ``undecidable``. The machine verdict is a SCREEN (lexical support
   found / not found), carried in ``verdict_basis="screen"``; hand-adjudicated rows
   carry ``verdict_basis="hand"``. Divergences are recorded, never smoothed over —
   PWG glossing `gā` «прийти, достигнуть, настигнуть» while Elizarenkova reads
   `jigāti` at 7.84.1 as «кружит около» is the finding, not a bug.

3. **The build-time refusal.** ``emit_citation_ru()`` RAISES ``PublishedTranslationExists``
   when a caller offers a machine translation for a locus that already has published
   Russian. This is a refusal in code, not a convention in prose: conventions of this
   shape have not held before (H2849's P7 precedent — a correct ruling went unapplied
   at 1,071 sites). ``gate`` runs the refusal over the whole store and exits non-zero
   on any violation.

Substrate: [rvlinks](https://github.com/sanskrit-lexicon/rvlinks), cloned as a sibling
repo — ``rvhymns/rv<MM>.<HHH>.html``, all 1 028 hymns, with ``<p class="ru">`` carrying
Elizarenkova one line per pāda (``<BR>``-separated). Resolution order for its location:
``$RVLINKS_DIR``, then a ``rvlinks/`` sibling of the repo checkout, then of its parent.

Rights, recorded once per the org's standing policy (rights uncertainty is not a stop):
the Russian in rvlinks is Elizarenkova's published translation, REPRODUCED (not
org-produced); the repo's own footer credits only the compilation ("Translations compiled
by Dr. Mārcis Gasūns"). No redistribution licence is asserted by that repo. This module
reads it locally and emits pāda-level quotations for lexicographic comparison; it does not
republish the corpus.

Usage::

    python src/rv_pada_align.py --selftest
    python src/rv_pada_align.py card                      # the ṚV. 7,84,1 specimen
    python src/rv_pada_align.py card --locus 10,163,3
    python src/rv_pada_align.py report [--store PATH] [--out reports/rv_pada_alignment.jsonl]
    python src/rv_pada_align.py sample --n 50 [--seed 20260816]
    python src/rv_pada_align.py gate [--store PATH]        # build-time refusal, exit 3 on violation
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import random
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# --------------------------------------------------------------------------- rvlinks location


def rvlinks_dir():
    """Directory holding rvlinks' ``rvhymns/``; None when the sibling repo is absent."""
    env = os.environ.get('RVLINKS_DIR')
    candidates = []
    if env:
        candidates.append(env)
    repo = os.path.dirname(os.path.dirname(HERE))          # …/SanskritLexicography
    parent = os.path.dirname(repo)                          # …/GitHub
    candidates += [
        os.path.join(repo, 'rvlinks'),
        os.path.join(parent, 'rvlinks'),
        os.path.join(os.path.dirname(parent), 'rvlinks'),
    ]
    for c in candidates:
        if c and os.path.isdir(os.path.join(c, 'rvhymns')):
            return c
    return None


# --------------------------------------------------------------------------- SLP1 -> IAST

_ACCENT = re.compile(r'[/\\^]')
_S2I_FALLBACK = {
    'A': 'ā', 'I': 'ī', 'U': 'ū', 'f': 'ṛ', 'F': 'ṝ', 'x': 'ḷ', 'X': 'ḹ',
    'E': 'ai', 'O': 'au', 'M': 'ṃ', 'H': 'ḥ', 'K': 'kh', 'G': 'gh', 'N': 'ṅ',
    'C': 'ch', 'J': 'jh', 'Y': 'ñ', 'w': 'ṭ', 'W': 'ṭh', 'q': 'ḍ', 'Q': 'ḍh',
    'R': 'ṇ', 'T': 'th', 'D': 'dh', 'P': 'ph', 'B': 'bh', 'S': 'ś', 'z': 'ṣ',
}


def slp1_iast(s):
    """SLP1 -> IAST, Vedic accents dropped. Prefers the canonical site implementation."""
    try:
        pilot = os.path.join(HERE, 'pilot')
        if pilot not in sys.path:
            sys.path.insert(0, pilot)
        from build_article_site import slp1_iast as _canonical  # noqa: PLC0415
        return _canonical(s)
    except Exception:
        s = _ACCENT.sub('', s or '')
        return ''.join(_S2I_FALLBACK.get(c, c) for c in s)


# --------------------------------------------------------------------------- locus parsing

# Sub-works cited under the ṚV. siglum that are NOT the Saṃhitā and have no rvlinks
# hymn page: the Prātiśākhya, the Anukramaṇī, the Khilāni, the Vālakhilya (separately
# numbered), the Prātiśākhya's commentary, and the Bhāṣya.
_RV_SUBWORK = re.compile(
    r'^(PRĀT|PRAT|ANUKR|KHILA|KHIL|VĀL|VAL|BHĀṢYA|BHASHYA|SARVĀNUKR|SARVANUKR|PRĀTIŚ)',
    re.I,
)
_LOCUS_RE = re.compile(r'(\d+)\s*,\s*(\d+)\s*,\s*(\d+)')
_RV_HEAD = re.compile(r'^\s*(ṚV|RV|R̥V)\s*\.?\s*', re.I)


def parse_rv_locus(raw_ls, n_attr=None):
    """``(raw <ls> text, n= attribute)`` -> ``{'mandala','hymn','verse'}`` or None.

    Handles both PWG shapes: the full ``<ls>ṚV. 7,84,1.</ls>`` and the continuation
    ``<ls n="ṚV.">5,15,4.</ls>`` where the siglum lives only in the attribute.
    Returns None for anything that is not a Saṃhitā verse reference — a bare ``ṚV.``
    with no numbers, a hymn-level ``ṚV. 1,100`` reference, or a sub-work
    (``ṚV. PRĀT. 13,13``), which the rvlinks hymn pages do not cover.
    """
    text = (raw_ls or '').strip()
    attr = (n_attr or '').strip()
    is_rv = False
    body = text
    m = _RV_HEAD.match(text)
    if m:
        is_rv = True
        body = text[m.end():]
    elif _RV_HEAD.match(attr):
        is_rv = True
    if not is_rv:
        return None
    if _RV_SUBWORK.match(body.strip()) or _RV_SUBWORK.match(re.sub(_RV_HEAD, '', attr).strip()):
        return None
    lm = _LOCUS_RE.search(body)
    if not lm:
        return None
    mand, hymn, verse = (int(x) for x in lm.groups())
    if not (1 <= mand <= 10 and 1 <= hymn <= 999 and 1 <= verse <= 99):
        return None
    return {'mandala': mand, 'hymn': hymn, 'verse': verse,
            'locus': 'rv%02d.%03d.%02d' % (mand, hymn, verse)}


# --------------------------------------------------------------------------- rvlinks parsing

_VERSE_BLOCK = re.compile(
    r"<p class=\"stamp\">rv(\d\d)\.(\d\d\d)\.(\d\d)</p>(.*?)(?=<p class=\"stamp\">|<div>)",
    re.S,
)
_FIELD = re.compile(r"<p class=\"(sa|hn|ru|de|en)\">(.*?)</p>", re.S)
_TAG = re.compile(r'<[^>]+>')

_hymn_cache = {}


def _split_br(chunk):
    """Split an rvlinks field on its <BR>/<br /> line breaks; hard newlines are soft
    wraps inside a printed line and are joined, not treated as line boundaries."""
    parts = re.split(r'(?i)<br\s*/?>', chunk)
    out = []
    for p in parts:
        p = _TAG.sub('', p)
        p = re.sub(r'\s+', ' ', p).strip()
        if p:
            out.append(p)
    return out


def load_hymn(mandala, hymn, rvdir=None):
    """``rvhymns/rv<MM>.<HHH>.html`` -> ``{verse:int -> {'sa','hn','ru','de','en'}}``.

    ``ru``/``hn`` come back as LISTS of printed lines; the others as single strings.
    Returns ``{}`` when the hymn file is absent (rvlinks missing, or a khila).
    """
    key = (mandala, hymn)
    if key in _hymn_cache:
        return _hymn_cache[key]
    rvdir = rvdir or rvlinks_dir()
    if not rvdir:
        _hymn_cache[key] = {}
        return {}
    path = os.path.join(rvdir, 'rvhymns', 'rv%02d.%03d.html' % (mandala, hymn))
    if not os.path.exists(path):
        _hymn_cache[key] = {}
        return {}
    with open(path, encoding='utf-8') as fh:
        html = fh.read()
    verses = {}
    for vm in _VERSE_BLOCK.finditer(html):
        vno = int(vm.group(3))
        rec = {}
        for fm in _FIELD.finditer(vm.group(4)):
            name, chunk = fm.group(1), fm.group(2)
            if name in ('hn', 'ru'):
                rec[name] = _split_br(chunk)
            else:
                rec[name] = re.sub(r'\s+', ' ', _TAG.sub('', chunk)).strip()
        verses[vno] = rec
    _hymn_cache[key] = verses
    return verses


# --------------------------------------------------------------------------- metre / pāda split

# IAST vowel nuclei. `ḷ`/`ḹ` are deliberately EXCLUDED: in Ṛgvedic romanisation `ḷ` is
# the intervocalic retroflex lateral (īḷe, agnim īḷe), a consonant — counting it as a
# syllable would inflate every Agni hymn.
_SYLL = re.compile(r'ai|au|[aāiīuūṛṝeo]')
_NO_RU = re.compile(r'^[\s\-–—.]*(ru|-ru-)?[\s\-–—.]*$', re.I)

# Elizarenkova prints a speaker attribution as its own line in the dialogue hymns
# («Индра:», «Сарама:», «Р е к и:» — 163 lines over the 1 028 hymns). It renders no
# pāda, so counting it as one shifts every later line off its pāda by one: RV 3.33.9's
# «Склонитесь хорошенько…» (pāda d) was being returned for pāda c. Recognised
# narrowly — a capitalised stub of at most two words, or letters spaced out for
# typographic emphasis, ending in a colon — so that a real pāda line that happens to
# end in a colon («Царям, достойным жертв:») is left alone.
_SPEAKER = re.compile(r'^[А-ЯЁ][^.!?;:]{0,26}:$')


def _is_speaker_label(line):
    s = (line or '').strip()
    if not _SPEAKER.match(s):
        return False
    tokens = s[:-1].split()
    return len(tokens) <= 2 or all(len(t) == 1 for t in tokens)


def ru_pada_lines(rec):
    """The published Russian lines of a verse that actually render a pāda."""
    return [ln for ln in (rec or {}).get('ru', [])
            if not _NO_RU.match(ln) and not _is_speaker_label(ln)]


def syllables(text):
    """Syllable (vowel-nucleus) count of an IAST string."""
    return len(_SYLL.findall((text or '').lower()))


def _strip_metre_marks(line):
    return re.sub(r'[|‖।॥]+', ' ', line or '')


def _split_line(line, k):
    """Split one hemistich into ``k`` pādas at word boundaries, balancing syllables."""
    words = [w for w in _strip_metre_marks(line).split() if w]
    if k <= 1 or len(words) <= 1:
        return [' '.join(words)] if words else ['']
    counts = [syllables(w) for w in words]
    total = sum(counts)
    target = total / float(k)
    chunks, cur, cur_syl, remaining = [], [], 0, k
    for i, w in enumerate(words):
        cur.append(w)
        cur_syl += counts[i]
        words_left = len(words) - i - 1
        if remaining > 1 and words_left >= remaining - 1:
            over = cur_syl - target * (len(chunks) + 1)
            nxt = counts[i + 1] if i + 1 < len(words) else 0
            # close the pāda when adding the next word would overshoot the target
            # by more than keeping it would undershoot
            if cur_syl >= target * (len(chunks) + 1) or abs(over) <= abs(over + nxt):
                chunks.append(' '.join(cur))
                cur, remaining = [], remaining - 1
    if cur or len(chunks) < k:
        chunks.append(' '.join(cur))
    while len(chunks) < k:
        chunks.append('')
    if len(chunks) > k:                      # fold any overflow into the last pāda
        chunks = chunks[:k - 1] + [' '.join(chunks[k - 1:])]
    return chunks


def pada_split(hn_lines, n_padas):
    """Split the romanised verse into ``n_padas`` pādas, never across a hemistich break.

    Returns ``(padas, regularity)`` where ``regularity`` is the max deviation, in
    syllables, of any pāda from the mean. A regular Vedic verse (gāyatrī 8·8·8,
    anuṣṭubh/triṣṭubh/jagatī 4 equal pādas) lands at ≤2; anything larger means the
    line count we were handed does not match the metre and the join must not be
    trusted at pāda granularity.
    """
    lines = [ln for ln in (hn_lines or []) if _strip_metre_marks(ln).strip()]
    if not lines or n_padas < 1:
        return [], 99.0
    line_syl = [syllables(_strip_metre_marks(ln)) for ln in lines]
    total = float(sum(line_syl)) or 1.0
    target = total / n_padas
    # allocate pādas to hemistichs proportionally, ≥1 each, summing to n_padas
    alloc = [max(1, int(round(s / target))) if target else 1 for s in line_syl]
    while len(alloc) > n_padas:              # more hemistichs than pādas: merge tail
        lines = lines[:n_padas - 1] + [' '.join(lines[n_padas - 1:])]
        line_syl = [syllables(_strip_metre_marks(ln)) for ln in lines]
        alloc = [1] * len(lines)
    guard = 0
    while sum(alloc) != n_padas and guard < 50:
        guard += 1
        if sum(alloc) > n_padas:
            i = max(range(len(alloc)), key=lambda j: (alloc[j] > 1, -line_syl[j] / max(alloc[j], 1)))
            if alloc[i] > 1:
                alloc[i] -= 1
            else:
                break
        else:
            i = max(range(len(alloc)), key=lambda j: line_syl[j] / float(alloc[j]))
            alloc[i] += 1
    padas = []
    for ln, k in zip(lines, alloc):
        padas.extend(_split_line(ln, k))
    padas = [p for p in padas][:n_padas]
    while len(padas) < n_padas:
        padas.append('')
    sizes = [syllables(p) for p in padas]
    mean = sum(sizes) / float(len(sizes) or 1)
    regularity = max(abs(s - mean) for s in sizes) if sizes else 99.0
    return padas, regularity


PADA_LETTERS = 'abcdefgh'


# --------------------------------------------------------------------------- quote matching

_FOLD = {
    'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṝ': 'ṛ', 'ḹ': 'ḷ',
    'ṃ': 'm', 'ṁ': 'm', 'ḥ': 'h', 'ṅ': 'n', 'ñ': 'n', 'ṇ': 'n',
    'ś': 's', 'ṣ': 's', 'ṭ': 't', 'ḍ': 'd', 'ḷ': 'l',
}
_DROP = re.compile(r"[^a-zāīūṛṝḷḹṃṁḥṅñṇśṣṭḍ]")


def fold(text):
    """Normalise IAST for cross-edition comparison: no spaces, no punctuation, no
    quantity/place contrasts. PWG's text and rvlinks' differ in word division, sandhi
    and the odd consonant (PWG ``daghānā`` vs rvlinks ``dadhānā`` at 7.84.1); folding
    absorbs the systematic half so the residual mismatch is real, not orthographic."""
    t = (text or '').lower()
    t = _DROP.sub('', t)
    return ''.join(_FOLD.get(c, c) for c in t)


def _coverage(pada, quote):
    """Fraction of the pāda's folded characters that occur, in order, inside the quote."""
    p, q = fold(pada), fold(quote)
    if not p or not q:
        return 0.0
    sm = difflib.SequenceMatcher(None, p, q, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    return matched / float(len(p))


def _quote_covered_by(run_text, quote):
    """Fraction of the QUOTE matched, in order, by a joined run of pādas."""
    p, q = fold(run_text), fold(quote)
    if not p or not q:
        return 0.0
    sm = difflib.SequenceMatcher(None, q, p, autojunk=False)
    return sum(b.size for b in sm.get_matching_blocks()) / float(len(q))


def _fragment_score(quote, pada):
    """How well a short quotation sits INSIDE one pāda: the single longest common run,
    as a fraction of the quotation.

    Deliberately the LONGEST BLOCK, not the sum of blocks. Summing lets a handful of
    scattered two-character coincidences add up to a confident hit: ``(ā)gamyās`` at
    RV 1.163.13 scored 1.00 against pāda a (``upa prāgāt paramaṃ yat sadhastham``)
    that way, while the word it actually quotes — ``gamyā`` — is in pāda c. A quoted
    word is contiguous by construction, so contiguity is the right evidence.
    """
    q, p = fold(quote), fold(pada)
    if not q or not p:
        return 0.0
    return difflib.SequenceMatcher(None, q, p, autojunk=False).find_longest_match(
        0, len(q), 0, len(p)).size / float(len(q))


PADA_HIT = 0.62          # legacy per-pāda coverage, kept for the reported `coverage` row
PADA_WEAK = 0.45
FRAGMENT_HIT = 0.70      # longest-block share a fragment needs to claim a pāda
FRAGMENT_MIN = 4         # folded characters below which a fragment locates nothing
SPAN_RATIO = 0.75        # quote ≥ this fraction of a mean pāda -> "span" mode
TRIM_KEEP = 0.97         # a pāda may be trimmed off a span while this much of the
                         # quotation is still covered by what remains
PADA_EDGE = 0.50         # …or when the quotation covers less than this of that end pāda


def align(quote_slp1, mandala, hymn, verse, rvdir=None, quote_iast=None):
    """The pāda-granular join. Returns a dict; ``ru_lines`` are the published Russian
    for exactly the pādas the quotation covers, or ``[]`` with a stated reason."""
    locus = 'rv%02d.%03d.%02d' % (mandala, hymn, verse)
    out = {
        'locus': locus, 'padas': [], 'pada_index': [], 'ru_lines': [],
        'sa_padas': [], 'coverage': [], 'quote_coverage': 0.0,
        'confidence': 'none', 'reason': '', 'n_ru_lines': 0, 'regularity': None,
        'has_published_ru': False, 'mode': None, 'margin': None,
    }
    verses = load_hymn(mandala, hymn, rvdir)
    rec = verses.get(verse)
    if not rec:
        out['reason'] = ('rvlinks has no hymn page rv%02d.%03d' % (mandala, hymn)
                         if not verses else
                         'hymn rv%02d.%03d has only %d verses — PWG cites verse %d'
                         % (mandala, hymn, max(verses), verse))
        return out
    ru_lines = ru_pada_lines(rec)
    out['n_ru_lines'] = len(ru_lines)
    if not ru_lines:
        out['reason'] = 'rvlinks carries no Russian for this verse'
        return out
    out['has_published_ru'] = True
    padas, regularity = pada_split(rec.get('hn', []), len(ru_lines))
    out['regularity'] = round(regularity, 2)
    out['sa_padas'] = padas
    quote = quote_iast if quote_iast is not None else slp1_iast(quote_slp1)
    if not fold(quote):
        out['reason'] = 'no Sanskrit quoted with this citation'
        out['confidence'] = 'verse'
        out['padas'] = list(PADA_LETTERS[:len(ru_lines)])
        out['pada_index'] = list(range(len(ru_lines)))
        out['ru_lines'] = ru_lines
        return out
    # Two matching modes, because PWG quotes at two very different lengths: a half-verse
    # or more ("span" — which pādas does this quotation cover?), and a single word or
    # phrase ("contains" — which pāda is this fragment inside of?). Running only the
    # first silently drops every one-word citation; running only the second lets a long
    # quotation collapse onto whichever pāda scores best.
    mean_pada = sum(len(fold(p)) for p in padas) / float(len(padas) or 1)
    qlen = len(fold(quote))
    mode = 'span' if qlen >= SPAN_RATIO * mean_pada else 'contains'
    out['mode'] = mode
    margin = None
    lo = hi = None
    if mode == 'span':
        # The span a quotation covers is a CONTIGUOUS run of pādas, so choose the run
        # directly instead of unioning independent per-pāda hits: start from the whole
        # verse and trim whichever end can go while the remainder still carries the
        # quotation. Thresholding each pāda separately silently drops the pāda a
        # quotation only reaches into — RV 1.141.1 (`… devasya bhargaḥ`, pāda b) and
        # RV 1.116.8 (`… un ninyathuḥ`, pāda d) both lost their second pāda that way,
        # and a half-covered join was still reported at medium confidence.
        cov = [_coverage(p, quote) for p in padas]
        n = len(padas)
        base = _quote_covered_by(' '.join(padas), quote)
        lo, hi = 0, n - 1
        if base >= PADA_WEAK:
            guard = 0
            while hi > lo and guard < 4 * n:
                guard += 1
                left = _quote_covered_by(' '.join(padas[lo + 1:hi + 1]), quote)
                right = _quote_covered_by(' '.join(padas[lo:hi]), quote)
                # An end pāda also goes when the quotation barely touches IT — the
                # retention test alone keeps a pāda that contributes one stray character
                # the quotation happens to spell differently (RV 6.27.7: `parādāt` vs
                # `parādād` cost 4% of a 24-character quote, and pāda d rode along).
                drop_l = left >= TRIM_KEEP * base or cov[lo] < PADA_EDGE
                drop_r = right >= TRIM_KEEP * base or cov[hi] < PADA_EDGE
                if drop_l and (left >= right or not drop_r):
                    lo += 1
                elif drop_r:
                    hi -= 1
                else:
                    break
        else:
            lo = hi = None
    else:
        cov = [_fragment_score(quote, p) for p in padas]
        order = sorted(range(len(cov)), key=lambda i: cov[i], reverse=True)
        if len(fold(quote)) < FRAGMENT_MIN:
            out['coverage'] = [round(c, 3) for c in cov]
            nchar = len(fold(quote))
            out['reason'] = ('quoted fragment is %d character%s — too short to locate a '
                             'pāda' % (nchar, '' if nchar == 1 else 's'))
            return out
        if order and cov[order[0]] >= FRAGMENT_HIT:
            lo = hi = order[0]
            margin = cov[order[0]] - (cov[order[1]] if len(order) > 1 else 0.0)
    out['coverage'] = [round(c, 3) for c in cov]
    if lo is None:
        out['reason'] = 'quotation does not match any pāda of this verse'
        return out
    idx = list(range(lo, hi + 1))
    out['pada_index'] = idx
    out['padas'] = [PADA_LETTERS[i] for i in idx]
    out['ru_lines'] = [ru_lines[i] for i in idx if i < len(ru_lines)]
    joined = ' '.join(padas[i] for i in idx)
    # In fragment mode the score of record is the contiguous longest-block share, not the
    # sum of blocks — the same reason `_fragment_score` exists.
    out['quote_coverage'] = round(
        cov[lo] if mode == 'contains' else _quote_covered_by(joined, quote), 3)
    if regularity > 3.5:
        out['confidence'] = 'low'
        out['reason'] = ('published line count (%d) does not match the metre — '
                         'pāda boundaries unsafe' % len(ru_lines))
    elif mode == 'span':
        if regularity <= 2.0 and out['quote_coverage'] >= 0.80:
            out['confidence'] = 'high'
        elif out['quote_coverage'] >= 0.60:
            out['confidence'] = 'medium'
        else:
            out['confidence'] = 'low'
            out['reason'] = 'quotation only partly covered by the selected pādas'
    else:
        if out['quote_coverage'] >= 0.90 and (margin or 0.0) >= 0.15 and regularity <= 2.0:
            out['confidence'] = 'high'
        elif out['quote_coverage'] >= 0.80:
            out['confidence'] = 'medium'
        else:
            out['confidence'] = 'low'
            out['reason'] = 'fragment ambiguous between pādas'
    out['margin'] = round(margin, 3) if margin is not None else None
    return out


# --------------------------------------------------------------------------- agreement verdict

_RU_WORD = re.compile(r'[а-яёА-ЯЁ]+')
_RU_STOP = {
    'кого', 'чего', 'кому', 'чему', 'либо', 'нибудь', 'что', 'как', 'или', 'при',
    'над', 'под', 'для', 'без', 'себя', 'себе', 'тот', 'этот', 'весь', 'всё',
    'быть', 'etc', 'нечто', 'нечего', 'вместе', 'также', 'один', 'одна',
}
_STEM = 4


def _stems(text):
    out = set()
    for w in _RU_WORD.findall((text or '').lower()):
        if len(w) < 4 or w in _RU_STOP:
            continue
        out.add(w[:_STEM])
    return out


def verdict(gloss_ru, alignment):
    """``agrees`` / ``diverges`` / ``undecidable`` for one citation.

    Machine basis is a SCREEN: ``agrees`` means the gloss has lexical support in the
    published Russian for the quoted pādas; ``diverges`` means a confident pāda join
    found none. Neither replaces adjudication — it ranks the 1 526 so a human reads
    the divergences first.
    """
    if not alignment.get('has_published_ru'):
        return 'undecidable', 'no published Russian for this locus'
    if not alignment.get('ru_lines'):
        return 'undecidable', alignment.get('reason') or 'no pāda selected'
    if alignment.get('confidence') == 'low':
        return 'undecidable', alignment.get('reason') or 'low-confidence pāda join'
    gs = _stems(gloss_ru)
    if not gs:
        return 'undecidable', 'no Russian gloss governs this citation'
    rs = _stems(' '.join(alignment['ru_lines']))
    if gs & rs:
        return 'agrees', 'gloss stem(s) %s present in the published pāda(s)' % ', '.join(
            sorted(gs & rs))
    joined = ' '.join(alignment['ru_lines'])
    return 'diverges', 'PWG «%s» ↮ pāda(s) %s «%s»' % (
        (gloss_ru or '').strip(), ''.join(alignment['padas']),
        joined if len(joined) <= 160 else joined[:157] + '…')


# --------------------------------------------------------------------------- build-time refusal


class PublishedTranslationExists(Exception):
    """Raised when a machine translation is offered for a locus that has a published one."""


def has_published_ru(mandala, hymn, verse, rvdir=None):
    rec = load_hymn(mandala, hymn, rvdir).get(verse)
    if not rec:
        return False
    return bool(ru_pada_lines(rec))


def emit_citation_ru(locus, quote_slp1=None, machine_ru=None, rvdir=None, quote_iast=None):
    """The ONLY sanctioned way to put Russian next to a cited RV locus.

    * published Russian exists -> the aligned pāda line(s) are returned and any
      ``machine_ru`` the caller offered is REFUSED with ``PublishedTranslationExists``;
    * no published Russian -> ``machine_ru`` is passed through (that is the only case
      where re-translating a Ṛgvedic locus is legitimate).

    ``locus`` is either a ``parse_rv_locus`` dict or an ``(m, h, v)`` triple.
    """
    if isinstance(locus, dict):
        m, h, v = locus['mandala'], locus['hymn'], locus['verse']
    else:
        m, h, v = locus
    published = has_published_ru(m, h, v, rvdir)
    if published and machine_ru:
        raise PublishedTranslationExists(
            'rv%02d.%03d.%02d has a published Russian translation (Elizarenkova, via '
            'rvlinks); align to it at pāda granularity instead of emitting %r'
            % (m, h, v, (machine_ru or '')[:60]))
    if not published:
        return {'source': 'machine' if machine_ru else 'none',
                'ru_lines': [machine_ru] if machine_ru else [],
                'alignment': None}
    al = align(quote_slp1, m, h, v, rvdir, quote_iast=quote_iast)
    return {'source': 'elizarenkova', 'ru_lines': al['ru_lines'], 'alignment': al}


# --------------------------------------------------------------------------- store scan

LS_RE = re.compile(r'<ls\b([^>]*)>(.*?)</ls>', re.S)
N_ATTR_RE = re.compile(r'\bn\s*=\s*"([^"]*)"')
GLOSS_RE = re.compile(r'\{%(.*?)%\}', re.S)
QUOTE_RE = re.compile(r'\{#(.*?)#\}', re.S)


def default_store():
    """The ONE logical pwg_ru store, resolved through the repo's canonical resolver.

    ``canonical_store(local_default)`` redirects a LINKED worktree to the main
    checkout's copy — the store is gitignored and exists only there, so calling it
    without the argument (or falling back to ``HERE``) makes every worktree run die
    with a bare ``FileNotFoundError``.
    """
    local = os.path.join(HERE, 'pwg_ru_translated.jsonl')
    try:
        from store_path import canonical_store  # noqa: PLC0415
        return canonical_store(local)
    except Exception:
        return local


def iter_rv_citations(store=None):
    """Yield one record per Ṛgveda-Saṃhitā ``<ls>`` citation in the live store.

    ``quote`` is the ``{#…#}`` span that belongs to THIS citation — the one lying in the
    window between the end of the previous ``</ls>`` and the start of this ``<ls>`` (that
    is PWG's layout: quoted Sanskrit, then its source, then any parallel loci with no
    quotation of their own). Taking merely the *nearest preceding* ``{#…#}`` instead
    attaches one verse's text to the next verse's citation and produces confident
    nonsense — measured at ~6% of the corpus before this window was imposed.
    ``gloss`` is the nearest preceding ``{%…%}`` in the RUSSIAN field — the gloss the
    citation is evidence for.
    """
    store = store or default_store()
    with open(store, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            de, ru = row.get('de') or '', row.get('ru') or ''
            prev_end = 0
            for m in LS_RE.finditer(de):
                attrs, raw = m.group(1), re.sub(r'\s+', ' ', m.group(2)).strip()
                window_start, prev_end = prev_end, m.end()
                n_attr = (N_ATTR_RE.search(attrs) or [None, None])[1] if N_ATTR_RE.search(attrs) else None
                loc = parse_rv_locus(raw, n_attr)
                if not loc:
                    continue
                qm = list(QUOTE_RE.finditer(de[window_start:m.start()]))
                quote = qm[-1].group(1) if qm else ''
                # the gloss lives in the RU field; align by counting citations, not offsets
                gloss = ''
                ru_upto = ru[:_nth_ls_end(ru, _ls_ordinal(de, m.start()))]
                gm = list(GLOSS_RE.finditer(ru_upto))
                if gm:
                    gloss = re.sub(r'\s+', ' ', gm[-1].group(1)).strip()
                yield {
                    'key1': row.get('key1'), 'subcard': row.get('subcard'),
                    'iast': row.get('iast'), 'sense_tag': row.get('sense_tag'),
                    'raw_ls': raw, 'n_attr': n_attr, 'quote_slp1': quote.strip(),
                    'gloss_ru': gloss, 'ru_field': ru, **loc,
                }


def _ls_ordinal(text, pos):
    return sum(1 for m in LS_RE.finditer(text) if m.start() < pos)


def _nth_ls_end(text, n):
    for i, m in enumerate(LS_RE.finditer(text)):
        if i == n:
            return m.start()
    return len(text)


# --------------------------------------------------------------------------- CLI helpers


def _row_for(cit, rvdir=None):
    al = align(cit['quote_slp1'], cit['mandala'], cit['hymn'], cit['verse'], rvdir)
    vd, why = verdict(cit['gloss_ru'], al)
    return {
        'key1': cit['key1'], 'subcard': cit['subcard'], 'iast': cit['iast'],
        'raw_ls': cit['raw_ls'], 'locus': al['locus'],
        'quote_iast': slp1_iast(cit['quote_slp1']),
        'gloss_ru': cit['gloss_ru'],
        'padas': ''.join(al['padas']), 'ru_lines': al['ru_lines'],
        'sa_padas_selected': [al['sa_padas'][i] for i in al['pada_index']
                              if i < len(al['sa_padas'])],
        'coverage': al['coverage'], 'quote_coverage': al['quote_coverage'],
        'confidence': al['confidence'], 'mode': al['mode'], 'n_ru_lines': al['n_ru_lines'],
        'regularity': al['regularity'], 'has_published_ru': al['has_published_ru'],
        'scope': 'verse' if al['confidence'] == 'verse' else 'pāda',
        'verdict': vd,
        'verdict_basis': 'screen-verse' if al['confidence'] == 'verse' else 'screen',
        'verdict_why': why,
        'reason': al['reason'],
    }


def cmd_card(args):
    rvdir = rvlinks_dir()
    if not rvdir:
        print('rvlinks not found — set $RVLINKS_DIR'); return 2
    loc = args.locus
    m, h, v = (int(x) for x in loc.split(','))
    target = 'rv%02d.%03d.%02d' % (m, h, v)
    for cit in iter_rv_citations(args.store):
        if cit['locus'] != target:
            continue
        row = _row_for(cit, rvdir)
        print('=' * 78)
        print('%s  (%s · %s)' % (row['iast'] or row['key1'], row['key1'], row['subcard']))
        print('PWG gloss   : %s' % row['gloss_ru'])
        print('Citation    : %s  ->  %s' % (row['raw_ls'], row['locus']))
        print('Quoted      : %s' % row['quote_iast'])
        print('Pādas       : %s   (coverage %s, quote %.2f, %s confidence)'
              % (row['padas'] or '—', row['coverage'], row['quote_coverage'], row['confidence']))
        for letter, line in zip(row['padas'], row['ru_lines']):
            print('  %s) %s' % (letter, line))
        print('Verdict     : %s — %s' % (row['verdict'], row['verdict_why']))
        print('=' * 78)
    return 0


def cmd_report(args):
    rvdir = rvlinks_dir()
    rows, verdicts, conf = [], Counter(), Counter()
    entries, loci = set(), set()
    for cit in iter_rv_citations(args.store):
        row = _row_for(cit, rvdir)
        rows.append(row)
        verdicts[row['verdict']] += 1
        conf[row['confidence']] += 1
        entries.add(row['key1'])
        loci.add(row['locus'])
    print('RV Saṃhitā citations : %d' % len(rows))
    print('distinct entries     : %d' % len(entries))
    print('distinct loci        : %d' % len(loci))
    print('verdicts (all)       : %s' % dict(verdicts.most_common()))
    for sc in ('pāda', 'verse'):
        c = Counter(r['verdict'] for r in rows if r['scope'] == sc)
        print('verdicts (%-5s)    : %s' % (sc, dict(c.most_common())))
    print('join confidence      : %s' % dict(conf.most_common()))
    scoped = [r for r in rows if r['padas'] and r['scope'] == 'pāda']
    print('pāda-scoped joins    : %d (%.1f%%)' % (
        len(scoped), 100.0 * len(scoped) / max(len(rows), 1)))
    spanning = sum(1 for r in scoped if len(r['padas']) > 1)
    print('multi-pāda joins     : %d (%.1f%% of pāda-scoped)' % (
        spanning, 100.0 * spanning / max(len(scoped), 1)))
    print('no published Russian : %d' % sum(1 for r in rows if not r['has_published_ru']))
    print('reasons for no join  : %s' % dict(
        Counter(r['reason'] for r in rows if not r['padas']).most_common(6)))
    if args.out:
        out = args.out if os.path.isabs(args.out) else os.path.join(os.path.dirname(HERE), args.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='\n') as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
        print('wrote %s' % out)
    return 0


def cmd_sample(args):
    """Draw the pāda-selection audit sample, printing the WHOLE verse each time.

    An adjudicator has to see the pādas that were *not* picked, and their Russian, or
    the sample can only confirm the join with itself. Deterministic in ``--seed``, so
    the frozen listing under ``reports/`` is reproducible.
    """
    rvdir = rvlinks_dir()
    rows = [_row_for(c, rvdir) for c in iter_rv_citations(args.store)]
    pool = [r for r in rows if r['scope'] == 'pāda' and r['padas']]
    rnd = random.Random(args.seed)
    pick = rnd.sample(pool, min(args.n, len(pool)))
    pick.sort(key=lambda r: (r['key1'] or '', r['locus']))
    out = []
    out.append('pool: %d pāda-scoped joins of %d RV citations (seed %d)'
               % (len(pool), len(rows), args.seed))
    for i, r in enumerate(pick, 1):
        loc = r['locus']
        m, h, v = int(loc[2:4]), int(loc[5:8]), int(loc[9:11])
        rec = load_hymn(m, h, rvdir).get(v) or {}
        ru = ru_pada_lines(rec)
        padas, reg = pada_split(rec.get('hn', []), len(ru))
        out.append('--- %02d %s %s | sel=%s %s q=%.2f reg=%.1f'
                   % (i, loc, r['key1'], r['padas'], r['confidence'],
                      r['quote_coverage'], reg))
        out.append('    QUOTE: %s' % r['quote_iast'])
        for j, p in enumerate(padas):
            mark = '>>' if PADA_LETTERS[j] in r['padas'] else '  '
            out.append('  %s %s) %-46s | %s'
                       % (mark, PADA_LETTERS[j], p, ru[j] if j < len(ru) else ''))
    text = '\n'.join(out)
    print(text)
    if getattr(args, 'out', None):
        path = (args.out if os.path.isabs(args.out)
                else os.path.join(os.path.dirname(HERE), args.out))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(text + '\n')
        print('\nwrote %s' % path)
    return 0


def scan_violations(store=None, rvdir=None):
    """The build-time refusal, run over a store. Returns ``(stats, violations)``.

    A store row VIOLATES the rule when a Ṛgvedic locus that has published Russian
    carries quoted Sanskrit in the German column which has been rendered *away* in the
    Russian column — i.e. the pipeline emitted its own Russian for a verse Elizarenkova
    already translated, instead of passing the Sanskrit through so it can be aligned.
    The check is byte-level on the ``{#…#}`` span, so it cannot be satisfied by a
    paraphrase and cannot be fooled by re-wrapping.

    This is deliberately NOT ``emit_citation_ru`` called with ``machine_ru=None``: that
    call can never raise, so a gate built on it reports "0 violations" on any input
    whatsoever, including a store that violates the rule on every row. The negative
    control in the selftest (``test_gate_detects_a_violation``) exists to keep it honest.
    """
    rvdir = rvdir if rvdir is not None else rvlinks_dir()
    stats = Counter()
    violations = []
    for cit in iter_rv_citations(store):
        stats['citations'] += 1
        if not has_published_ru(cit['mandala'], cit['hymn'], cit['verse'], rvdir):
            continue
        stats['published'] += 1
        quote = (cit.get('quote_slp1') or '').strip()
        if not quote:
            continue
        stats['quoted'] += 1
        if quote in (cit.get('ru_field') or ''):
            stats['passed_through'] += 1
            continue
        violations.append({
            'key1': cit['key1'], 'subcard': cit['subcard'], 'locus': cit['locus'],
            'raw_ls': cit['raw_ls'], 'quote_slp1': quote,
            'why': ('rv locus has published Russian (Elizarenkova, via rvlinks) but the '
                    'quoted Sanskrit was not carried into the RU column — align to the '
                    'published pāda(s) instead of re-rendering the verse'),
        })
    return stats, violations


def cmd_gate(args):
    """Build-time refusal over the live store. Exit 3 on any violation."""
    rvdir = rvlinks_dir()
    if not rvdir:
        print('GATE SKIPPED: rvlinks not on this machine (set $RVLINKS_DIR)')
        return 0
    stats, violations = scan_violations(args.store, rvdir)
    print('gate: %d RV citations checked · %d with published Russian · %d of those quote '
          'Sanskrit · %d carried the quote through · %d violations'
          % (stats['citations'], stats['published'], stats['quoted'],
             stats['passed_through'], len(violations)))
    for v in violations[:20]:
        print('  VIOLATION %s (%s): %s' % (v['locus'], v['key1'], v['quote_slp1'][:70]))
    return 3 if violations else 0


# --------------------------------------------------------------------------- selftest


def selftest():
    from rv_pada_align_selftest import run  # noqa: PLC0415
    return run()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--selftest', action='store_true')
    sub = ap.add_subparsers(dest='cmd')
    for name in ('card', 'report', 'sample', 'gate'):
        p = sub.add_parser(name)
        p.add_argument('--store', default=None)
        if name == 'card':
            p.add_argument('--locus', default='7,84,1')
        if name == 'report':
            p.add_argument('--out', default=None)
        if name == 'sample':
            p.add_argument('--n', type=int, default=50)
            p.add_argument('--seed', type=int, default=20260816)
            p.add_argument('--out', default=None)
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.cmd:
        ap.print_help()
        return 1
    return {'card': cmd_card, 'report': cmd_report,
            'sample': cmd_sample, 'gate': cmd_gate}[args.cmd](args)


if __name__ == '__main__':
    raise SystemExit(main())
