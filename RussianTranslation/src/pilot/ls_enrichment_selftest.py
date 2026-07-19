# -*- coding: utf-8 -*-
"""Fixture selftest for the H1307 <ls> link-enrichment (Pāṇini + Spr. (II)).

No network and no RU store are needed. The Pāṇini/edition-guard assertions are
pure resolver logic; the Spr. (II) full-text lookup uses the tracked, public
Indische Sprüche corpus (present in a normal checkout) and is skipped-with-note
only if that file is genuinely absent.

  python src/pilot/ls_enrichment_selftest.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path.insert(0, SRC)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import ls_resolver as lsr        # noqa: E402
import spr_fulltext as spr       # noqa: E402

_PANINI = 'https://ashtadhyayi.com/sutraani'
_BOESP2 = 'sanskrit-lexicon-scans.github.io/boesp2'
_BOESP1 = 'sanskrit-lexicon-scans.github.io/boesp1'


def fail(msg):
    raise AssertionError(msg)


def _href(n_attr, visible):
    return lsr.generate_href('pwg', n_attr, visible)


def test_panini_full_form():
    """Full 3-param P. adhyaya,pada,sutra -> the sutra deep link."""
    got = _href('', 'P. 1,1,14')
    if got != _PANINI + '/1/1/14':
        fail('P. 1,1,14 -> %r' % got)


def test_panini_continuation_ref():
    """The N14 card's continuation ref: n='P. 2,3,' + visible '10.' -> /2/3/10."""
    got = _href('P. 2,3,', '10.')
    if got != _PANINI + '/2/3/10':
        fail('continuation P. 2,3, + 10. -> %r' % got)


def test_panini_chapter_browse():
    """2-param chapter ref P. 2,3 -> the pada browse route; guarded so a bogus
    pada like P. 1,23 or an invalid pada P. 1,6 does NOT mislink."""
    if _href('', 'P. 2,3') != _PANINI + '/2/3':
        fail('P. 2,3 -> %r' % _href('', 'P. 2,3'))
    for bad in ('P. 1,6', 'P. 1,23', 'P. 9', 'P. II, S. 3'):
        if _href('', bad) is not None:
            fail('%s should NOT link, got %r' % (bad, _href('', bad)))


def test_spr_edition_guard():
    """Plain 1st-ed Spr. N must route to boesp1 and NEVER be resolved against the
    2nd-ed corpus; 2nd-ed Spr. (II) N routes to boesp2."""
    first = _href('', 'Spr. 1415')
    if not first or _BOESP1 not in first:
        fail('Spr. 1415 (1st ed) -> %r (expected boesp1)' % first)
    if spr.second_ed_num('', 'Spr. 1415') is not None:
        fail('1st-ed Spr. 1415 leaked into the 2nd-ed number guard')
    if spr.second_ed_num('', 'Spr. (I) 200') is not None:
        fail('Spr. (I) 200 leaked into the 2nd-ed number guard')
    second = _href('', 'Spr. (II) 5712')
    if not second or _BOESP2 not in second:
        fail('Spr. (II) 5712 -> %r (expected boesp2)' % second)


def test_spr_second_ed_number():
    """The 2nd-ed number is extracted for both the inline and continuation forms."""
    if spr.second_ed_num('', 'Spr. (II) 6145') != 6145:
        fail('inline Spr. (II) 6145 -> %r' % spr.second_ed_num('', 'Spr. (II) 6145'))
    if spr.second_ed_num('Spr. (II)', '6145.') != 6145:
        fail('continuation Spr. (II)+6145. -> %r' % spr.second_ed_num('Spr. (II)', '6145.'))


def test_spr_fulltext_lookup():
    """The Indische Sprüche corpus resolves a known saying to its IAST + German."""
    if not spr.available():
        print('  SKIP test_spr_fulltext_lookup: corpus absent on this machine')
        return
    rec = spr.saying(6145)
    if not rec:
        fail('saying(6145) missing from the corpus')
    if not rec.get('iast') or not rec.get('translation_de'):
        fail('saying(6145) lacks iast/translation_de: %r' % rec)
    tip = spr.tooltip('', 'Spr. (II) 6145')
    if not tip or not tip.startswith('Spr. (II) 6145:') or 'vipakṣaḥ' not in tip:
        fail('tooltip(Spr. (II) 6145) -> %r' % tip)
    # edition guard at the tooltip layer: a 1st-ed ref yields no 2nd-ed tooltip
    if spr.tooltip('', 'Spr. 1415') is not None:
        fail('1st-ed Spr. 1415 must not get a 2nd-ed full-text tooltip')


def main():
    tests = [
        test_panini_full_form,
        test_panini_continuation_ref,
        test_panini_chapter_browse,
        test_spr_edition_guard,
        test_spr_second_ed_number,
        test_spr_fulltext_lookup,
    ]
    for t in tests:
        t()
        print('  ok %s' % t.__name__)
    print('ls_enrichment_selftest: %d checks passed' % len(tests))


if __name__ == '__main__':
    main()
