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
import os, re, sys, json, tempfile
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from safe_filename import candidate_names

HERE = os.path.dirname(os.path.abspath(__file__))
# H1386 P3f: PWG_INPUT_DIR points a hermetic harness at a sandbox input dir.
INP = os.environ.get('PWG_INPUT_DIR') or os.path.join(HERE, 'pilot', 'input')
OUTP = os.path.join(HERE, 'pilot', 'output')


# An owner citation that CLOSES a gloss: `Name : page` at the very end of a
# segment.  Name starts uppercase and carries NO period (real owners — MW,
# BHSD, Graßmann 1873 (1996), Vishva Bandhu 1972, Vedic Hymns I, NṚV 2A — have
# none), which stops the name from swallowing the preceding sentence or an
# internal dotted ref (Hoernle 1893-1912 (II) 30.81, EI Vol. XV, MaiSaṃ 3.8.4).
# It also stops at `;` so the trailing-tag variant used for prefix/compound
# sub-entries (`gloss … <DIATAG> ; SOURCE:page >`, e.g. aYj) keeps only the
# SOURCE, not the diasystem tag, as the owner.
#
# H4539: a condensed cross-ref entry carries grammar + a bracketed x-ref BEFORE
# the closing cite (`Adj f [f zu árvant ] Hillebrandt 1885 : 72 (s.v. árvant )`).
# A first-capital-anchored name used to start at «Adj» and swallow the whole
# prefix into the owner, so `owner_surname` became «Adj f [f zu árvant ]
# Hillebrandt» and the F12 gate failed a CARD that was correct (H4213 canary).
# A real owner name never contains `[`/`]`, so excluding the brackets stops the
# name at the x-ref and the match starts at the real owner — the last
# `Name : page` token — leaving the grammar in the gloss.
OWNER = re.compile(
    r'(?P<name>[A-ZÀ-ÖØ-ÞĀ-ỿ][^>:.;\[\]]*?)\s:\s(?P<page>\d+[A-Za-z]?)'
    r'(?P<sv>\s*\((?:[^()]|\([^()]*\))*\))?\s*$')
BARE = re.compile(r'^[,;]?\s*' + OWNER.pattern)

# diasystem first-tokens, to peel a leading lemma off a TAG segment (cosmetic)
DIASET = {'Gen', 'Ved', 'Tan', 'Buddh', 'Śā', 'Jin', 'Epigr', 'Kāv', 'Reg',
          'Class', 'Gramm', 'Lex', 'Skt', 'Pkt', 'Soc', 'Astr', 'Med', 'Math',
          'Ling', 'Phil'}


def path_stems(key):
    stems = []
    if '~~' in (key or ''):
        stems.append(key)          # root-split sub-card keys are already safe stems
    stems.extend(candidate_names(key))
    stems.append(key)              # legacy whole-card merged outputs used literal keys
    out, seen = [], set()
    for stem in stems:
        if stem and stem not in seen:
            out.append(stem)
            seen.add(stem)
    return out


def resolve_key_path(directory, key, suffix):
    for stem in path_stems(key):
        path = os.path.join(directory, stem + suffix)
        if os.path.exists(path):
            return path
    return None


def nws_fragment(key):
    """The raw NWS string from <key>.raw.txt (the net-new NWS addendum layer).

    Stops at the next `=== LAYER:` marker so it does NOT swallow the appended
    `NWS — PRE-PARSED OWNER MAP` layer (which _pilot_gen_merged.py writes after
    the addendum); over-capturing it would make split()/check() re-parse the
    map as if it were source content."""
    p = resolve_key_path(INP, key, '.raw.txt')
    if not p:
        return None
    txt = open(p, encoding='utf-8').read()
    m = re.search(r'=== LAYER: NWS(?! — PRE-PARSED)[^\n]*===\s*\n(.*?)(?=\n+=== LAYER:|\Z)',
                  txt, re.S)
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
    p = resolve_key_path(OUTP, key, '.merged.md')
    if not p:
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


# A locator must match a whole token, not a substring: the 4-char Sanskrit
# locator «apāṃ» is contained in the compounds «apāṃpitta»/«apāṃnidhi», which
# would mis-locate a bare cross-reference (`apāṃ napāt → s.v. napāt`) onto an
# unrelated MW row. Require non-letter boundaries on both sides.
_LET = 'A-Za-zÀ-ÿĀ-ỿ'


def located_in(cand, row):
    return any(c and re.search(r'(?<![%s])%s(?![%s])' % (_LET, re.escape(c), _LET), row)
               for c in cand)


def check_result(key):
    frag = nws_fragment(key)
    if frag is None:
        return {'key': key, 'verdict': 'NO-RAW', 'returncode': 1,
                'lines': ['  no raw input for %s' % key], 'rejected': False}
    if not frag:
        return {'key': key, 'verdict': 'NO-NWS', 'returncode': 1,
                'lines': ['  no NWS fragment for %s' % key], 'rejected': False}
    entries = split(frag)
    rows = card_rows(key)
    if rows is None:
        lines = ['  no merged card output/%s.merged.md — split only:' % key]
        for e in entries:
            lines.append('   %-26s | %s' % (' / '.join(e['owners']), e['gloss'][:70]))
        return {'key': key, 'verdict': 'NO-CARD', 'returncode': 1,
                'lines': lines, 'rejected': False}
    bad, miss = 0, 0
    locs = locators(entries)
    lines = ['  %s: %d NWS entries vs %d card NWS rows' % (key, len(entries), len(rows))]
    for e, cand in zip(entries, locs):
        exp = [owner_surname(o) for o in e['owners']]
        # rows located by ANY of this entry's fragment-unique tokens
        hit = [r for r in rows if located_in(cand, r)]
        if not hit:
            miss += 1
            lines.append('   ?  no unique locator for owner %s — verify by hand (gloss: %s)'
                         % ('/'.join(exp), e['gloss'][:50]))
            continue
        # PASS if ANY located row is correctly attributed
        if not any(any(s and s in row_owner(r) for s in exp) for r in hit):
            bad += 1
            lines.append('   ✗  «%s» card owner=[%s]  expected=[%s]'
                         % (cand[0], row_owner(hit[0]), '/'.join(exp)))
    verdict = 'CLEAN' if not bad else 'MISATTRIBUTION'
    lines.append('  → %s (%d mismatch%s%s)' % (
        verdict, bad, '' if bad == 1 else 'es',
        ', %d unlocated' % miss if miss else ''))
    return {'key': key, 'verdict': verdict, 'returncode': 1 if bad else 0,
            'lines': lines, 'rejected': False}


def check(key):
    res = check_result(key)
    for line in res['lines']:
        print(line)
    return res['returncode']


# aMSa ground truth (hand-derived, _aMSa_nws_correct_parse.md) for selftest
AMSA_OWNERS = ['MW : 1', 'Graßmann 1873 (1996) : 1', 'NṚV 1 : 3',
               'Vishva Bandhu 1972 : 1', 'Rivelex (1) : 1', 'Renou 1997 : 940',
               'Renou 1934 : 173', 'Vishva Bandhu 1972 : 8 (s.v. aṃśena)',
               'Sarma 1966 : 165', 'Meyer 1926 : 940', 'Olivelle 2015 : 1',
               'Keller 2006 : 198', 'Hoernle 1908 : 241', 'TAK 1 : 73',
               'BHSD : 1', 'Sircar 1966 : 18', 'TAK 1 : 73 (s.v. aṃśa)']

# H4539 regression fixture: the condensed cross-ref entry that made the OWNER
# regex swallow `Adj f [f zu árvant ]` into the owner (H4213 canary
# h4213can091108282902, arvant~~h0_zz_nws00).  Kept INLINE — pilot/input is
# gitignored, so a worktree/CI selftest must not depend on the runtime fixture.
ARVANT_FRAGMENT = (
    'árvant Gen , unsp > Adj mfn low, inferior, vile. UṇS . MW : 93 > '
    'Ved , unsp > Adj mfn rennend, eilend, schnell. Subst m der Eilende, '
    'schnell fahrende. [ von Göttern. ] der Renner, das Ross. [ theils das '
    'Streitross, theils das Rennpferd im Wettlaufe, theils das Ross überhaupt, '
    'und dann oft neben dem Rinde genannt. ] Wagen (wol bildlich). vom Wagen- '
    'oder Rosselenker. scheint fast e. Theil der Opferhandlung zu bezeichnen. '
    'Graßmann 1873 (1996) : 116 > Ved , unsp > Adj mf(atī)n rasch dahineilend. '
    'ṚV 7,87,1 . Subst m Renner, Ross. ṚV 1,118,2 . Hillebrandt 1885 : 72 > '
    'Ved , unsp > Subst m Streitross, Rennpferd. ṚV 1,64,13 . árvatā : mit dem '
    'Ross, zu Ross. ṚV 1,116,17 . árvati : zu Ross, im Streit. ṚV 2,33,1 . '
    'Ritter, Reiter. ṚV 10,40,5 . Geldner 1907 : 16 > '
    'árvatī Ved , unsp > Adj f [f zu árvant ] Hillebrandt 1885 : 72 '
    '(s.v. árvant ) >')
ARVANT_SURNAMES = ['MW', 'Graßmann', 'Hillebrandt', 'Geldner', 'Hillebrandt']

# The canary card is linguistically CORRECT (the f-entry sits under lemma
# árvatī, tag [NWS: Hillebrandt]); the audit, not the card, was wrong.  Rows
# copied verbatim from the quarantined merged card (…merged.REJECTED.md).
ARVANT_CARD = (
    '| # | German (PWG) | Russian | type | src | stratum |\n'
    '|---|---|---|---|---|---|\n'
    '| [NWS: MW]) | Gen, unsp. Adj mfn low, inferior, vile. UṇS. MW : 93. | '
    'Gen, unsp. Adj mfn низкий, ничтожный, презренный. UṇS. MW : 93. | '
    'equivalent | lexicographic | – |\n'
    '| [NWS: Graßmann]) | Ved, unsp. Adj mfn rennend, eilend, schnell. Subst m '
    'der Eilende, schnell fahrende. [ von Göttern. ] der Renner, das Ross. '
    '[ theils das Streitross, theils das Rennpferd im Wettlaufe, theils das '
    'Ross überhaupt, und dann oft neben dem Rinde genannt. ] Wagen (wol '
    'bildlich). vom Wagen- oder Rosselenker. scheint fast e. Theil der '
    'Opferhandlung zu bezeichnen. Graßmann 1873 (1996) : 116. | Ved, unsp. Adj '
    'mfn бегущий, спешащий, быстрый. Graßmann 1873 (1996) : 116. | '
    'explanatory | lexicographic | Vedic |\n'
    '| [NWS: Hillebrandt]) | Ved, unsp. Adj mf(atī)n rasch dahineilend. '
    'ṚV 7,87,1. Subst m Renner, Ross. ṚV 1,118,2. Hillebrandt 1885 : 72. | '
    'Ved, unsp. Adj mf(atī)n быстро мчащийся. Hillebrandt 1885 : 72. | '
    'equivalent | attested | Vedic |\n'
    '| [NWS: Geldner]) | Ved, unsp. Subst m Streitross, Rennpferd. ṚV 1,64,13. '
    'árvatā : mit dem Ross, zu Ross. ṚV 1,116,17. árvati : zu Ross, im Streit. '
    'ṚV 2,33,1. Ritter, Reiter. ṚV 10,40,5. Geldner 1907 : 16. | Ved, unsp. '
    'Subst m боевой конь. Geldner 1907 : 16. | equivalent | attested | Vedic |\n'
    '| [NWS: Hillebrandt]) | Ved, unsp. Adj f [ f zu árvant ] Hillebrandt 1885 '
    ': 72 (s.v. árvant ). | Ved, unsp. Adj f [f к árvant] Hillebrandt 1885 : '
    '72 (s.v. árvant). | explanatory | lexicographic | Vedic |\n')


def selftest():
    ok = True
    # 1. aMSa ground truth — needs the gitignored pilot/input fixture.
    amsa_frag = nws_fragment('aMSa')
    if amsa_frag is None:
        print('  aMSa ground truth: skipped (pilot/input/aMSa.raw.txt absent)')
    else:
        entries = split(amsa_frag)
        got = [(' / '.join(e['owners'])) for e in entries]
        amsa_ok = (got == AMSA_OWNERS)
        for i, (g, want) in enumerate(zip(got, AMSA_OWNERS + [''] * 99)):
            mark = 'ok' if g == want else '✗'
            print('  %2d %-3s got=%-32s want=%s' % (i + 1, mark, g, want))
        if len(got) != len(AMSA_OWNERS):
            print('  ✗ entry count %d != %d' % (len(got), len(AMSA_OWNERS)))
            amsa_ok = False
        ok = ok and amsa_ok

    # 2. H4539: condensed cross-ref — owner is the LAST Name:page token and the
    #    grammar/cross-ref prefix stays in the gloss.
    arv = split(ARVANT_FRAGMENT)
    arv_sur = [owner_surname(e['owners'][0]) if e['owners'] else None for e in arv]
    arv_ok = (len(arv) == 5 and arv_sur == ARVANT_SURNAMES
              and arv[-1]['owners'] == ['Hillebrandt 1885 : 72 (s.v. árvant)']
              and arv[-1]['gloss'].startswith('Adj f [f zu árvant ]'))
    print('  condensed cross-ref owner (H4539) %s — owners=%s' %
          ('ok' if arv_ok else '✗', '/'.join(str(s) for s in arv_sur)))
    ok = ok and arv_ok

    old_inp, old_outp = INP, OUTP
    try:
        with tempfile.TemporaryDirectory() as tmp:
            globals()['INP'] = os.path.join(tmp, 'input')
            globals()['OUTP'] = os.path.join(tmp, 'output')
            os.makedirs(INP, exist_ok=True)
            os.makedirs(OUTP, exist_ok=True)
            # 3. root-split literal stem resolver
            key = 'foo~~h0_00_pwg00'
            open(os.path.join(INP, key + '.raw.txt'), 'w', encoding='utf-8').write(
                '=== LAYER: NWS ===\nfoo Gen > uniquegloss MW : 1\n')
            open(os.path.join(OUTP, key + '.merged.md'), 'w', encoding='utf-8').write(
                '| tag | russian | src |\n| NWS | uniquegloss | [NWS: MW] |\n')
            res = check_result(key)
            lit_ok = res['verdict'] == 'CLEAN'
            print('  root-split literal stem resolver %s' %
                  ('ok' if lit_ok else '✗ got %s' % res['verdict']))
            ok = ok and lit_ok
            # 4. H4539: check_result CLEAN on the canary card (was MISATTRIBUTION)
            akey = 'arvant~~h0_zz_nws00'
            open(os.path.join(INP, akey + '.raw.txt'), 'w', encoding='utf-8').write(
                '=== LAYER: NWS ===\n' + ARVANT_FRAGMENT + '\n')
            open(os.path.join(OUTP, akey + '.merged.md'), 'w', encoding='utf-8').write(
                ARVANT_CARD)
            ares = check_result(akey)
            cr_ok = ares['verdict'] == 'CLEAN'
            print('  condensed cross-ref check_result (H4539) %s — %s' %
                  ('ok' if cr_ok else '✗', ares['lines'][-1].strip()))
            ok = ok and cr_ok
    finally:
        globals()['INP'] = old_inp
        globals()['OUTP'] = old_outp
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
