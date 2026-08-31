#!/usr/bin/env python
"""MW <k2> compound-segmentation lookup builder.

Streams csl-orig/v02/mw/mw.txt (read-only) and extracts every entry whose <k2>
headword contains an em-dash (—), which marks inter-member boundaries in Jim
Funderburk's MW compound segmentation (182k+ entries, 63.5% of MW).

  python src/mw_compounds.py --build     materializes src/mw_compounds.json
  python src/mw_compounds.py --show agni  show compound record for SLP1 key

Programmatic: `from mw_compounds import compound_for; compound_for('aMSakaraRa')`.
"""
import sys
import os
import json
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
from sibling_root import sibling_root  # noqa: E402
GITHUB = sibling_root(HERE)
MW_TXT = os.path.normpath(
    os.path.join(GITHUB, 'csl-orig', 'v02', 'mw', 'mw.txt'))
LOCAL = os.path.join(HERE, 'mw_compounds.json')

# em-dash as used in <k2> compound boundaries
_EMDASH = '—'

# MW lists spelling/accent VARIANTS of the whole headword inside one <k2>,
# separated by '; ': `gaRa—kAri; gaRakAri`, `cit—pa/ti; cit—pati/`. They must be
# separated before the em-dash split, never after — see _parse_members.
_VARIANT_SEP = ';'

# Vedic accent and punctuation marks that may trail SLP1 member strings in k2.
# Strip these so 'putra/' → 'putra', 'soma^' → 'soma', etc.
_ACCENT_STRIP = str.maketrans('', '', "/'^ -;|")

_K1_RE = re.compile(r'<k1>(.*?)<')
_K2_RE = re.compile(r'<k2>(.*?)<')


def _clean_member(s):
    """Strip Vedic accent/punctuation marks from an SLP1 member string."""
    return s.strip().translate(_ACCENT_STRIP)


def _segmented_variant(k2_raw):
    """The <k2> variant that carries the segmentation, or '' if none does.

    A <k2> may list several spellings of the headword (`gaRa—kAri; gaRakAri`),
    and only some of them are segmented. Take the first segmented one.
    """
    for variant in k2_raw.split(_VARIANT_SEP):
        if _EMDASH in variant:
            return variant
    return ''


def _parse_members(k2_raw):
    """Split k2 on em-dash; return cleaned list of member strings (SLP1).

    The variant list is separated FIRST. Splitting on the em-dash first and
    cleaning second welded MW's variants into a member that is not a word —
    `gaRa—kAri; gaRakAri` yielded `gaRa` + `kArigaRakAri`, because _clean_member
    strips both ';' and the space (SanskritLexicography#801). The bogus member
    also inflated the arity, so `nominal_grammar._irregularities` emitted
    `compound:3_members` and the Zaliznyak index `+3` for a two-member compound.
    """
    return [_clean_member(m)
            for m in _segmented_variant(k2_raw).split(_EMDASH)
            if _clean_member(m)]


def build():
    if not os.path.exists(MW_TXT):
        sys.exit('MW source not found: %s (clone sanskrit-lexicon/csl-orig as a sibling)' % MW_TXT)
    lookup = {}
    n_scanned = n_compound = 0
    for line in open(MW_TXT, encoding='utf-8'):
        if '<k1>' not in line:
            continue
        m1 = _K1_RE.search(line)
        m2 = _K2_RE.search(line)
        if not (m1 and m2):
            continue
        k1 = m1.group(1)
        k2 = m2.group(1)
        n_scanned += 1
        if _EMDASH in k2:
            members = _parse_members(k2)
            if len(members) >= 2:
                # keep first record only (same k1 may recur with sub-entries)
                if k1 not in lookup:
                    lookup[k1] = members
                n_compound += 1
    json.dump(lookup, open(LOCAL, 'w', encoding='utf-8'), ensure_ascii=False,
              separators=(',', ':'))
    print('wrote %s — %d compound entries (of %d k1 scanned)'
          % (LOCAL, len(lookup), n_scanned))


_CACHE = None


def _load():
    global _CACHE
    if _CACHE is None:
        if not os.path.exists(LOCAL):
            build()
        _CACHE = json.load(open(LOCAL, encoding='utf-8'))
    return _CACHE


def compound_for(k1_slp1):
    """Return list of SLP1 compound members for k1, or None if not a compound."""
    return _load().get(k1_slp1)


_SELFTEST = [
    # (k2 as MW writes it, expected members) — #801 regression fixtures
    ('gaRa—kAri; gaRakAri', ['gaRa', 'kAri']),
    ('cit—pa/ti; cit—pati/', ['cit', 'pati']),
    ('paYca—viDa/; paYca—viDa', ['paYca', 'viDa']),
    ('gaRakAri; gaRa—kAri', ['gaRa', 'kAri']),   # unsegmented variant listed first
    ('a-kAma—karzaRa', ['akAma', 'karzaRa']),    # hyphen is a bound juncture, not a boundary
    ('putra/—kAma^', ['putra', 'kAma']),
    ('agni', []),                                 # not segmented at all
]


def selftest():
    bad = 0
    for k2, want in _SELFTEST:
        got = _parse_members(k2)
        if got != want:
            bad += 1
            print('FAIL %r -> %r, want %r' % (k2, got, want))
    print('mw_compounds: %d/%d fixtures pass' % (len(_SELFTEST) - bad, len(_SELFTEST)))
    return 1 if bad else 0


def main():
    args = sys.argv[1:]
    if '--selftest' in args:
        sys.exit(selftest())
    if '--build' in args:
        build()
        return
    if '--show' in args:
        idx = args.index('--show')
        if idx + 1 >= len(args):
            print('Usage: --show <SLP1>')
            return
        k1 = args[idx + 1]
        members = compound_for(k1)
        if members is None:
            print('not a compound in MW: %r' % k1)
        else:
            print('%s  →  %s' % (k1, '  +  '.join(members)))
        return
    print(__doc__)


if __name__ == '__main__':
    main()
