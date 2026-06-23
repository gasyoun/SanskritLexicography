#!/usr/bin/env python
"""Deterministic splitter for the NWS "Kleines Zitat" condensed addendum.

The NWS fragment packs many sub-dictionaries into one string with the format

    [LEMMA] TAG > gloss .. SOURCE:page >  [LEMMA] TAG > gloss .. SOURCE:page > ...

where the diasystem TAG *precedes* each gloss and the source citation *closes*
it (comes AFTER the gloss).  A reader (human or LLM) who flips that to
`SOURCE > TAG > gloss` slides every owner one entry forward — failure F12, which
the QA judge shared and false-cleared.  This parser owns the reading-direction
mechanically, so it does NOT share that blind spot.  Use it to AUDIT a merged
card's NWS attributions, not to translate.

Key fact exploited: a TAG segment never ends in a `Name : page` citation; a
gloss segment always does.  So splitting on ` > ` and pairing
(tag-segment, following gloss-segment-that-ends-in-a-cite) recovers the entries
without needing to know the tag vocabulary.

  python nws_split.py split  <key>       parsed (tag, gloss, owner) triples
  python nws_split.py check  <key>       diff splitter owners vs the merged card
  python nws_split.py selftest           validate parser on aMSa ground truth
"""
import os, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from safe_filename import safe_name

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(HERE, 'pilot', 'input')
OUTP = os.path.join(HERE, 'pilot', 'output')


# An owner citation that CLOSES a gloss: `Name : page` at the very end of a
# segment.  Name starts uppercase and carries NO period (real owners — MW,
# BHSD, Graßmann 1873 (1996), Vishva Bandhu 1972, Vedic Hymns I, NṚV 2A — have
# none), which stops the name from swallowing the preceding sentence or an
# internal dotted ref (Hoernle 1893-1912 (II) 30.81, EI Vol. XV, MaiSaṃ 3.8.4).
# It also stops at `;` so the trailing-tag variant used for prefix/compound
# sub-entries (`gloss … <DIATAG> ; SOURCE:page >`, e.g. aYj) keeps only the
# SOURCE, not the diasystem tag, as the owner.
OWNER = re.compile(
    r'(?P<name>[A-ZÀ-ÖØ-ÞĀ-ỿ][^>:.;]*?)\s:\s(?P<page>\d+[A-Za-z]?)'
    r'(?P<sv>\s*\(s\.v\.[^)]*\))?\s*$')
BARE = re.compile(r'^[,;]?\s*' + OWNER.pattern)

# diasystem first-tokens, to peel a leading lemma off a TAG segment (cosmetic)
DIASET = {'Gen', 'Ved', 'Tan', 'Buddh', 'Śā', 'Jin', 'Epigr', 'Kāv', 'Reg',
          'Class', 'Gramm', 'Lex', 'Skt', 'Pkt', 'Soc', 'Astr', 'Med', 'Math',
          'Ling', 'Phil'}


def nws_fragment(key):
    """The raw NWS string from <key>.raw.txt (text after the NWS layer marker)."""
    p = os.path.join(INP, safe_name(key) + '.raw.txt')
    if not os.path.exists(p):
        return ''
    txt = open(p, encoding='utf-8').read()
    m = re.search(r'=== LAYER: NWS[^\n]*===\s*\n(.*)\Z', txt, re.S)
    return (m.group(1).strip() if m else '')


def cite_of(seg):
    m = OWNER.search(seg)
    if not m:
        return None
    sv = ''
    if m.group('sv'):
        sv = ' ' + re.sub(r'\s*\)', ')', re.sub(r'\(\s*', '(', m.group('sv').strip()))
    return '%s : %s%s' % (m.group('name').strip(), m.group('page'), sv)


def lemma_tag(seg):
    """Peel an optional leading lemma off a TAG segment -> (lemma, tag)."""
    toks = seg.split()
    for i, t in enumerate(toks):
        if t in DIASET:
            return (' '.join(toks[:i]).strip(), ' '.join(toks[i:]).strip())
    return ('', seg.strip())


def split(fragment):
    """-> list of {lemma, tag, gloss, owners[]} in source order."""
    segs = [s.strip() for s in re.split(r'\s*>\s*', fragment) if s.strip()]
    entries, i, n = [], 0, len(segs)
    while i < n:
        lemma, tag = lemma_tag(segs[i])
        i += 1
        gloss_parts, owner = [], None
        while i < n:                       # accumulate gloss until a cite closes it
            g = segs[i]
            i += 1
            gloss_parts.append(g)
            if OWNER.search(g):
                owner = cite_of(g)
                break
        owners = [owner] if owner else []
        while i < n and BARE.match(segs[i]):   # extra co-owners sharing the gloss
            owners.append(cite_of(segs[i]))
            i += 1
        entries.append({'lemma': lemma, 'tag': tag,
                        'gloss': ' > '.join(gloss_parts).strip(), 'owners': owners})
    return entries


# ---- audit a card against the deterministic parse --------------------------

STOP = {'Subst', 'Adj', 'mfn', 'part', 'portion', 'share', 'thing', 'object',
        'food', 'light', 'fire', 'name', 'gold', 'water', 'earth', 'time'}


# Tokens kept VERBATIM in the card (sigla rule) so they survive translation and
# can locate the row: an internal citation (siglum + roman/number, e.g. «ṚV V,58,3»,
# «DurghVṛ 7.1,24») and a Sanskrit/IAST term (e.g. «nivṛtti»).
SA_DIA = re.compile(r'[āīūṛṝḷḹṅñṭḍṇśṣṃḥ]')
INTREF = re.compile(r'[A-ZÀ-ÖŚṚṢṬĀ][\wĀ-ỿ’.]*\.?\s+[IVXLC\d][\d.,]*')


def locators(entries):
    """Per entry, the set of fragment-UNIQUE tokens that can locate its card row.
    Unique (df==1) so the audit can't match the wrong row (the «Anteil»/«degree»
    collision). Draws from gloss words, internal citations AND Sanskrit terms — all
    kept verbatim in the card — so a stopword-only («fire, light») or Sanskrit-only
    («nivṛtti») gloss is still locatable. Falls back to the lemma."""
    from collections import Counter
    cands, df = [], Counter()
    for e in entries:
        g = e['gloss']
        c = {w for w in re.findall(r'[A-Za-zÀ-ÿĀ-ỿ]{6,}', g)
             if not w.isupper() and w not in STOP}
        c |= {t for t in re.findall(r'[A-Za-zÀ-ÿĀ-ỿ]{3,}', g) if SA_DIA.search(t)}
        c |= {m.group(0).strip() for m in INTREF.finditer(g)}
        cands.append(c)
        for t in c:
            df[t] += 1
    out = []
    for e, c in zip(entries, cands):
        uniq = sorted((t for t in c if df[t] == 1), key=len, reverse=True)
        # unique tokens give a collision-proof locate; when an entry has none
        # (e.g. duplicate glosses sharing one owner) fall back to all its tokens —
        # still owner-verified by check(), so a true misattribution still fails
        out.append(uniq or sorted(c, key=len, reverse=True)
                   or ([e['lemma']] if e['lemma'] else []))
    return out


def card_rows(key):
    p = os.path.join(OUTP, safe_name(key) + '.merged.md')
    if not os.path.exists(p):
        legacy = key + '.merged.md'
        try:
            has_legacy = legacy in set(os.listdir(OUTP))
        except OSError:
            has_legacy = False
        p = os.path.join(OUTP, legacy) if has_legacy else p   # legacy pilot output name
    if not os.path.exists(p):
        return None
    rows = []
    for ln in open(p, encoding='utf-8'):
        if ln.lstrip().startswith('|') and 'NWS' in ln:
            rows.append(ln.rstrip('\n'))
    return rows


def row_owner(row):
    m = re.search(r'\[NWS:\s*([^\]]+)\]', row)        # aMSa-style explicit label
    if m:
        return m.group(1).strip()
    # anna-style: owner cite sits inline; take the last Name:page in the row
    cands = re.findall(r'[A-ZÀ-ÖØ-ÞĀ-ỿ][\w’.()/\- ]*?\s*:\s*\d+[A-Za-z]?', row)
    return cands[-1].strip() if cands else ''


def owner_surname(owner):
    return re.split(r'\s*[:(]| \d', owner.strip())[0].strip()


def check(key):
    frag = nws_fragment(key)
    if not frag:
        print('  no NWS fragment for %s' % key); return 1
    entries = split(frag)
    rows = card_rows(key)
    if rows is None:
        print('  no merged card output/%s.merged.md — split only:' % key)
        for e in entries:
            print('   %-26s | %s' % (' / '.join(e['owners']), e['gloss'][:70]))
        return 0
    bad, miss = 0, 0
    locs = locators(entries)
    print('  %s: %d NWS entries vs %d card NWS rows' % (key, len(entries), len(rows)))
    for e, cand in zip(entries, locs):
        exp = [owner_surname(o) for o in e['owners']]
        # rows located by ANY of this entry's fragment-unique tokens
        hit = [r for r in rows if any(c and c in r for c in cand)]
        if not hit:
            miss += 1
            print('   ?  no unique locator for owner %s — verify by hand (gloss: %s)'
                  % ('/'.join(exp), e['gloss'][:50]))
            continue
        # PASS if ANY located row is correctly attributed
        if not any(any(s and s in row_owner(r) for s in exp) for r in hit):
            bad += 1
            print('   ✗  «%s» card owner=[%s]  expected=[%s]'
                  % (cand[0], row_owner(hit[0]), '/'.join(exp)))
    verdict = 'CLEAN' if not bad else 'MISATTRIBUTION'
    print('  → %s (%d mismatch%s%s)' % (
        verdict, bad, '' if bad == 1 else 'es',
        ', %d unlocated' % miss if miss else ''))
    return 1 if bad else 0


# aMSa ground truth (hand-derived, _aMSa_nws_correct_parse.md) for selftest
AMSA_OWNERS = ['MW : 1', 'Graßmann 1873 (1996) : 1', 'NṚV 1 : 3',
               'Vishva Bandhu 1972 : 1', 'Rivelex (1) : 1', 'Renou 1997 : 940',
               'Renou 1934 : 173', 'Vishva Bandhu 1972 : 8 (s.v. aṃśena)',
               'Sarma 1966 : 165', 'Meyer 1926 : 940', 'Olivelle 2015 : 1',
               'Keller 2006 : 198', 'Hoernle 1908 : 241', 'TAK 1 : 73',
               'BHSD : 1', 'Sircar 1966 : 18', 'TAK 1 : 73 (s.v. aṃśa)']


def selftest():
    entries = split(nws_fragment('aMSa'))
    got = [(' / '.join(e['owners'])) for e in entries]
    ok = (got == AMSA_OWNERS)
    for i, (g, want) in enumerate(zip(got, AMSA_OWNERS + [''] * 99)):
        mark = 'ok' if g == want else '✗'
        print('  %2d %-3s got=%-32s want=%s' % (i + 1, mark, g, want))
    if len(got) != len(AMSA_OWNERS):
        print('  ✗ entry count %d != %d' % (len(got), len(AMSA_OWNERS)))
        ok = False
    print('SELFTEST', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'selftest'
    if cmd == 'selftest':
        sys.exit(selftest())
    key = sys.argv[2]
    if cmd == 'split':
        for e in split(nws_fragment(key)):
            print('  [%s] %s%s' % (' / '.join(e['owners']) or '?',
                                   ('<%s> ' % e['lemma']) if e['lemma'] else '',
                                   e['gloss'][:90]))
    elif cmd == 'check':
        sys.exit(check(key))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
