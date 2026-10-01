#!/usr/bin/env python
"""H3948 / FINDINGS §453 — selftest pinning microstructure.py's FOUR sense tiers.

READ-ONLY. Scans the corpus, writes nothing, touches no store.

PWG nests four enumeration tiers, outermost first::

    I〉      roman division   (H3948, new)
    1〉 1)   digit sense      (§447)
    a〉 a)   latin sub-sense  (§447)
    α〉      greek sub-sense  (H3948, new)

Two kinds of test live here:

  unit      synthetic bodies — nesting, the pre-sense head, childless roman
            divisions, backward-compatible sense ids, and every false-positive
            class the census found (ASCII 'δ)', '(Volume I)', 'S. 367)')
  corpus    the numbers this handoff is accountable for, recomputed live over
            all 123,366 <L> records: the 393-record H1350 probe class, the
            genuine per-tier counts, and the proof that the pre-H3948 parser
            saw none of them

Usage::

  python microstructure_four_tier_selftest.py            unit + corpus
  python microstructure_four_tier_selftest.py --no-corpus  unit only (fast)
  python microstructure_four_tier_selftest.py --prove-revert
        re-runs the same suite against a deliberately reverted (two-tier)
        parser and FAILS if the suite still passes -- the verification bar
        asks for a test that goes red when the fix is taken away.
"""
import os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import microstructure as ms                      # noqa: E402
import pwg_mask                                  # noqa: E402

# The exact §447 two-tier regexes, kept here so --prove-revert can put the
# pre-H3948 parser back in process without editing microstructure.py.
PRE_H3948_MARK = re.compile(r'(?<![^\s—])(?P<t>\d{1,2}|[a-z])[)〉]')
PRE_H3948_ADJACENT = re.compile(r'([)〉])(?=(?:\d{1,2}|[a-z])[)〉])')

# Measured over all 123,366 records by pwg_enum_tier_census.py (H3948).
EXPECT_GREEK_GENUINE = 1426
EXPECT_ROMAN_GENUINE = 29
EXPECT_PROBE_RECORDS = 393      # H1350 W1.2, .ai_state.md — reproduced exactly
EXPECT_PROBE_OCCURRENCES = 1546

# Two consumers pre-normalise the body differently, and H3948 does not change
# that: leaf_senses() un-glues marker chains with ADJACENT_MARKERS first,
# portrait()/split_senses() do not. So 'raw' below is what portrait() sees and
# 'norm' is what leaf_senses() sees. The gap is a MEASURED residual class, not
# a rule invented for it: 48 of the 393 probe records carry their four-tier
# marker only inside a glued chain ('1〉b〉α〉', 'c〉α〉'), so portrait() still
# leaves those unsplit. Un-gluing inside split_senses() would also re-split
# already-promoted digit/latin chains, i.e. rewrite live store rows — which is
# exactly what this handoff is fenced against.
EXPECT_GAINED_RAW = 345
EXPECT_GAINED_NORM = 393
EXPECT_GLUED_ONLY_RECORDS = 48

GLYPH = re.compile(r'〉')
OLD_RECOGNISED = re.compile(r'[0-9a-z]')


# --------------------------------------------------------------------------- #
# unit tests
# --------------------------------------------------------------------------- #

def ids(body):
    return [ms.sense_path(s) for s in ms.split_senses(body)]


def test_four_tier_nesting():
    body = 'foo I〉 bar 1〉 baz a〉 qux α〉 end II〉 tail'
    segs = ms.split_senses(body)
    got = [(s['div'], s['n'], s['sub'], s['sub2']) for s in segs]
    want = [
        (None, '0', None, None),     # pre-sense head
        ('I', '0', None, None),      # roman division WITH children -> head
        ('I', '1', None, None),
        ('I', '1', 'a', None),
        ('I', '1', 'a', 'α'),
        ('II', None, None, None),    # childless roman -> a leaf, not a head
    ]
    assert got == want, got


def test_childless_roman_stays_in_leaf_senses():
    """A roman division with no digit under it carries real sense text."""
    body = 'I〉 <ab>m.</ab> Held. II〉 <ab>f.</ab> Kraft.'
    segs = ms.split_senses(body)
    assert [s['n'] for s in segs] == [None, None], segs
    assert [ms.sense_path(s) for s in segs] == ['I', 'II'], segs


def test_pre_sense_head_is_still_n0():
    segs = ms.split_senses('Adj. allgemein 1〉 erste 2〉 zweite')
    assert segs[0]['n'] == '0' and segs[0]['div'] is None, segs[0]


def test_backward_compatible_sense_ids():
    """Every body the pre-H3948 parser could see keeps its exact old ids."""
    for body in (
        '1〉 eins a〉 erstens b〉 zweitens 2〉 zwei',
        '1) eins a) erstens 2) zwei',
        'Kopf 1〉 eins 2〉 zwei',
        'kein marker hier',
    ):
        new = ms.split_senses(body)
        for s in new:
            assert s['div'] is None and s['sub2'] is None, (body, s)
        old_ids = [(s['n'] or '') + (s['sub'] or '') for s in new]
        assert ids(body) == old_ids, body


def test_false_positive_ascii_greek():
    """'u. δ)' is a cross-reference, not a marker: greek is glyph-only."""
    assert ids('1〉 eins <ab>vgl.</ab> oben <ab>u.</ab> δ) und mehr') == ['1']


def test_false_positive_ascii_roman():
    """'(Volume I)' and friends: roman is glyph-only too."""
    assert ids('1〉 eins Lebensb. Volume I) noch text') == ['1']


def test_false_positive_three_digit():
    """digit width stays {1,2}: 'S. 367)' is a page reference."""
    assert ids('1〉 eins S. 367) weiter') == ['1']


def test_false_positive_open_paren_lookbehind():
    """A marker never opens after '(' — that is citation-internal."""
    assert ids('1〉 eins (3) weiter') == ['1']


def test_protected_spans_are_not_markers():
    """The corpus's single 'U〉' sits inside a {#…#} Sanskrit span."""
    assert ids('1〉 eins {#juhU〉ma/si#} weiter') == ['1']
    assert ids('1〉 eins <ls>Lebensb. 233 (3).</ls> weiter') == ['1']


def test_adjacent_markers_knows_all_four_tiers():
    """Glued chains: the corpus carries 'c〉α〉', '4〉b〉α〉', 'II〉1〉a〉'."""
    for glued, want in (
        ('c〉α〉', 'c〉 α〉'),
        ('4〉b〉α〉', '4〉 b〉 α〉'),
        ('II〉1〉a〉', 'II〉 1〉 a〉'),
        ('1〉2〉', '1〉 2〉'),
    ):
        got = ms.ADJACENT_MARKERS.sub(r'\1 ', glued)
        assert got == want, (glued, got)


def test_greek_and_roman_tokens_classify():
    assert ms.ROMAN_TOK.match('III') and not ms.ROMAN_TOK.match('a')
    assert ms.GREEK_TOK.match('α') and not ms.GREEK_TOK.match('I')


# --------------------------------------------------------------------------- #
# corpus tests — the numbers this handoff is accountable for
# --------------------------------------------------------------------------- #

def four_tier_marks(body):
    """Genuine roman/greek markers in `body`, as (offset, token)."""
    spans = ms.protected(body)
    out = []
    for m in ms.MARK.finditer(body):
        p = m.start()
        if any(a <= p < b for a, b in spans):
            continue
        tok = ms.mark_token(m)
        if ms.ROMAN_TOK.match(tok) or ms.GREEK_TOK.match(tok):
            out.append((p, tok))
    return out


def scan_corpus():
    """One pass over the corpus, returning everything the corpus tests need."""
    probe_records, probe_occ = 0, 0
    greek, roman = 0, 0
    greek_n, roman_n = 0, 0
    old_saw = 0
    gained_raw, gained_norm = 0, 0
    n_rec = 0
    for buf in pwg_mask.records():
        n_rec += 1
        body = '\n'.join(buf[1:])                       # what portrait() sees
        norm = ms.ADJACENT_MARKERS.sub(r'\1 ', body)    # what leaf_senses() sees
        spans = ms.protected(body)

        def inside(p):
            return any(a <= p < b for a, b in spans)

        # H1350's own probe: a '〉' whose immediately preceding character the
        # pre-H3948 MARK regex does not recognise.
        hits = [m.start() for m in GLYPH.finditer(body)
                if m.start() and not OLD_RECOGNISED.match(body[m.start() - 1])]
        if hits:
            probe_records += 1
            probe_occ += len(hits)

        old_marks = set(m.start() for m in PRE_H3948_MARK.finditer(body)
                        if not inside(m.start()))
        four_raw = four_tier_marks(body)
        four_norm = four_tier_marks(norm)
        for _, t in four_raw:
            if ms.ROMAN_TOK.match(t):
                roman += 1
            else:
                greek += 1
        for _, t in four_norm:
            if ms.ROMAN_TOK.match(t):
                roman_n += 1
            else:
                greek_n += 1
        if four_raw:
            gained_raw += 1
            old_saw += sum(1 for p, _ in four_raw if p in old_marks)
        if four_norm:
            gained_norm += 1
    return dict(n_rec=n_rec, probe_records=probe_records, probe_occ=probe_occ,
                greek=greek, roman=roman, greek_norm=greek_n, roman_norm=roman_n,
                old_saw=old_saw, gained_raw=gained_raw, gained_norm=gained_norm,
                glued_only=gained_norm - gained_raw)


CORPUS = {}


def test_corpus_probe_class_is_the_393_of_h1350():
    assert CORPUS['probe_records'] == EXPECT_PROBE_RECORDS, CORPUS
    assert CORPUS['probe_occ'] == EXPECT_PROBE_OCCURRENCES, CORPUS


def test_corpus_genuine_tier_counts():
    assert CORPUS['greek'] == EXPECT_GREEK_GENUINE, CORPUS
    assert CORPUS['roman'] == EXPECT_ROMAN_GENUINE, CORPUS


def test_pre_h3948_parser_saw_none_of_them():
    """Not one of the new markers was matched by the two-tier regex."""
    assert CORPUS['old_saw'] == 0, CORPUS


def test_every_probe_record_now_splits():
    """All 393 probe records split on the leaf_senses (un-glued) path …"""
    assert CORPUS['gained_norm'] == EXPECT_GAINED_NORM == EXPECT_PROBE_RECORDS, CORPUS


def test_glued_only_residual_is_measured_not_guessed():
    """… and exactly 48 of them do so ONLY there — the declared residual class."""
    assert CORPUS['gained_raw'] == EXPECT_GAINED_RAW, CORPUS
    assert CORPUS['glued_only'] == EXPECT_GLUED_ONLY_RECORDS, CORPUS


UNIT_TESTS = [v for k, v in sorted(globals().items())
              if k.startswith('test_') and not k.startswith('test_corpus')
              and k not in ('test_pre_h3948_parser_saw_none_of_them',
                            'test_every_probe_record_now_splits',
                            'test_glued_only_residual_is_measured_not_guessed')]
CORPUS_TESTS = [test_corpus_probe_class_is_the_393_of_h1350,
                test_corpus_genuine_tier_counts,
                test_pre_h3948_parser_saw_none_of_them,
                test_every_probe_record_now_splits,
                test_glued_only_residual_is_measured_not_guessed]


def run(tests, label):
    failed = []
    for t in tests:
        try:
            t()
            print('  ok    %s' % t.__name__)
        except Exception as e:
            failed.append((t.__name__, e))
            print('  FAIL  %s: %s' % (t.__name__, e))
    print('%s: %d/%d passed' % (label, len(tests) - len(failed), len(tests)))
    return failed


def revert_parser():
    """Put the pre-H3948 two-tier parser back, in process."""
    ms.MARK = PRE_H3948_MARK
    ms.ADJACENT_MARKERS = PRE_H3948_ADJACENT


def main():
    want_corpus = '--no-corpus' not in sys.argv
    prove_revert = '--prove-revert' in sys.argv

    print('H3948 four-tier segmentation selftest (READ-ONLY)')
    print('corpus: %s' % pwg_mask.PWG)
    print()
    print('unit tests')
    failed = run(UNIT_TESTS, 'unit')

    if want_corpus:
        if not os.path.exists(pwg_mask.PWG):
            print('\ncorpus tests SKIPPED — %s not present' % pwg_mask.PWG)
        else:
            print('\ncorpus scan (123,366 records) …')
            CORPUS.update(scan_corpus())
            print('  records=%(n_rec)d probe_records=%(probe_records)d '
                  'probe_occ=%(probe_occ)d greek=%(greek)d roman=%(roman)d '
                  'seen_by_old_parser=%(old_saw)d' % CORPUS)
            failed += run(CORPUS_TESTS, 'corpus')

    if prove_revert:
        print('\n--prove-revert: reverting to the §447 two-tier parser …')
        revert_parser()
        rev_failed = run(UNIT_TESTS, 'unit (reverted)')
        if want_corpus and os.path.exists(pwg_mask.PWG):
            CORPUS.update(scan_corpus())
            rev_failed += run(CORPUS_TESTS, 'corpus (reverted)')
        if not rev_failed:
            print('\nPROVE-REVERT FAILED: the suite still passes without the '
                  'H3948 parser — it pins nothing.', file=sys.stderr)
            return 1
        print('\nprove-revert OK: %d test(s) go red without the fix (%s)'
              % (len(rev_failed), ', '.join(n for n, _ in rev_failed)))

    if failed:
        print('\nSELFTEST FAILED: %d test(s)' % len(failed), file=sys.stderr)
        return 1
    print('\nselftest OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
