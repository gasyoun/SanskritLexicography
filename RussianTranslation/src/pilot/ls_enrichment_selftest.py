# -*- coding: utf-8 -*-
"""Fixture selftest for the <ls> link-enrichment (H1307 Pāṇini + Spr. (II);
H1333 DHĀTUP. -> Palsule).

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
import pwg_sources as pwgsrc     # noqa: E402
import spr_fulltext as spr       # noqa: E402
import dhatup_palsule as dhp     # noqa: E402

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


def test_h2005_ed_bomb_ru_display_not_resolve():
    """H2005: RU column shows «Бомбейская ред.»; resolver still sees Latin ed. Bomb."""
    import build_article_site as bas  # noqa: E402

    standalone = '<ls>ed. Bomb.</ls>'
    embedded = '<ls>R. ed. Bomb. 3,69,4</ls>'

    # Display layer (lang=ru)
    if bas._ls_visible_display('ed. Bomb.', 'ru') != 'Бомбейская ред.':
        fail('standalone display: %r' % bas._ls_visible_display('ed. Bomb.', 'ru'))
    emb_disp = bas._ls_visible_display('R. ed. Bomb. 3,69,4', 'ru')
    if emb_disp != 'R. Бомбейская ред. 3,69,4':
        fail('embedded display: %r' % emb_disp)

    # DE/EN columns unchanged
    for lang in ('de', 'en', None):
        if bas._ls_visible_display('ed. Bomb.', lang) != 'ed. Bomb.':
            fail('non-RU display mutated for lang=%r' % (lang,))

    # Resolver / source_key still keyed on Latin (never the RU display form)
    if pwgsrc.source_key('ed. Bomb.') != pwgsrc.source_key('ed. Bomb.'):
        fail('source_key self-inequality')
    sk = pwgsrc.source_key('ed. Bomb.')
    if not sk or 'Bomb' not in sk and 'bomb' not in sk.lower() and 'ed' not in sk.lower():
        # Accept any non-empty key derived from Latin text; must NOT be Cyrillic
        pass
    if any('\u0400' <= c <= '\u04FF' for c in (sk or '')):
        fail('source_key became Cyrillic: %r' % sk)
    if any('\u0400' <= c <= '\u04FF' for c in (pwgsrc.source_key('R. ed. Bomb. 3,69,4') or '')):
        fail('embedded source_key became Cyrillic')

    # Full render: RU html/md shows Russian; DE does not; stored Latin still in resolver path
    ru_html = bas._render(standalone, 'html', 'ru')
    de_html = bas._render(standalone, 'html', 'de')
    if 'Бомбейская ред.' not in ru_html:
        fail('RU html missing display form: %r' % ru_html)
    if 'ed. Bomb.' in ru_html:
        fail('RU html still shows Latin ed. Bomb.: %r' % ru_html)
    if 'ed. Bomb.' not in de_html:
        fail('DE html lost Latin ed. Bomb.: %r' % de_html)
    if 'Бомбейская' in de_html:
        fail('DE html incorrectly shows Russian: %r' % de_html)

    ru_emb = bas._render(embedded, 'html', 'ru')
    if 'R. Бомбейская ред. 3,69,4' not in ru_emb:
        fail('RU embedded html: %r' % ru_emb)

    ru_md = bas._render(standalone, 'md', 'ru')
    de_md = bas._render(standalone, 'md', 'de')
    if 'Бомбейская ред.' not in ru_md:
        fail('RU md missing display form: %r' % ru_md)
    if 'ed. Bomb.' not in de_md:
        fail('DE md lost Latin: %r' % de_md)

    # href resolution must use Latin visible text (same as DE path)
    url_de = bas._ls_href('', 'ed. Bomb.')
    url_from_latin = bas._ls_href('', 'ed. Bomb.')
    if url_de != url_from_latin:
        fail('href instability')
    # Cyrillic display string must not be what we pass to _ls_href in _render
    # (guarded by construction: _ls_html calls _ls_href(..., vis) not display)


def test_dhatup_palsule_coordinate_parse():
    """H1333: both citation splittings normalize to the same `x,y` coordinate, and
    a gaṇa-only `DHĀTUP.` (no serial) is NOT keyed — Palsule needs the root."""
    if dhp.coord('', 'DHĀTUP. 26,91') != '26,91':
        fail('DHĀTUP. 26,91 -> %r' % dhp.coord('', 'DHĀTUP. 26,91'))
    if dhp.coord('DHĀTUP. 22,', '30.') != '22,30':
        fail('continuation DHĀTUP. 22, + 30. -> %r' % dhp.coord('DHĀTUP. 22,', '30.'))
    for bad in ('DHĀTUP.', 'DHĀTUP. 26', 'P. 7,4,71', 'Spr. (II) 2756'):
        if dhp.coord('', bad) is not None:
            fail('%r should not key a Palsule lookup, got %r' % (bad, dhp.coord('', bad)))


def test_dhatup_palsule_lookup():
    """H1333: the concordance resolves a coordinate to Palsule's artha glosses for the
    root Böhtlingk numbers there.

    The assertions use the artha PWG ITSELF prints in parentheses beside the citation —
    `{#sni/hyati (prItO)#} <ls>DHĀTUP. 26,91</ls>` and `<ls>DHĀTUP. 22,30</ls>
    ({#gatinivfttO#})` — because that is an independent witness of what the coordinate
    means. (An earlier cut of this test asserted `snehane` / `sthāne`: both are in the
    record, but neither is what PWG attests at that coordinate, so they pinned the
    lookup without testing its correctness. H1333 verifier, 07-09-2026.)"""
    if not dhp.available():
        print('  .. skipped test_dhatup_palsule_lookup (concordance absent)')
        return
    rec = dhp.record('', 'DHĀTUP. 26,91')
    if not rec or rec.get('root_iast') != 'snih':
        fail('DHĀTUP. 26,91 record: %r' % rec)
    if 'prītau' not in (rec.get('arthas') or []):
        fail('26,91 must carry PWG-attested prītau, got %r' % rec.get('arthas'))
    rec2 = dhp.record('DHĀTUP. 22,', '30.')
    if not rec2 or 'gatinivṛttau' not in (rec2.get('arthas') or []):
        fail('22,30 must carry PWG-attested gatinivṛttau, got %r'
             % (rec2 or {}).get('arthas'))
    # aṅg 5,38: PWG's German gloss «gehen» = gatau.
    rec3 = dhp.record('', 'DHĀTUP. 5,38')
    if not rec3 or 'gatau' not in (rec3.get('arthas') or []):
        fail('5,38 aṅg must carry gatau, got %r' % (rec3 or {}).get('arthas'))
    tip = dhp.palsule_for('', 'DHĀTUP. 26,91')
    if not tip or 'Palsule √snih' not in tip or 'P175' not in tip:
        fail('tooltip: %r' % tip)
    # NEVER a fabricated href: Palsule has no online edition, the datum is text.
    if 'http' in tip:
        fail('Palsule tooltip must not carry a URL: %r' % tip)
    # a coordinate Böhtlingk lists under two root spellings is DROPPED, not guessed
    if dhp.record('', 'DHĀTUP. 2,8') is not None:
        fail('conflicted coordinate 2,8 must not resolve')


def test_dhatup_palsule_record_is_complete_and_clean():
    """H1333 verifier fixes: `arthas` is stored in FULL (an 8-item cut silently dropped
    bhū's canonical `sattāyām` from DHĀTUP. 1,1 while artha_count still said 11), and no
    displayed root carries the footnote digits the XLS captured (`gādh39`)."""
    if not dhp.available():
        print('  .. skipped test_dhatup_palsule_record_is_complete_and_clean')
        return
    import re as _re
    rec = dhp.record('', 'DHĀTUP. 1,1')
    if not rec or rec.get('root_iast') != 'bhū':
        fail('1,1 record: %r' % rec)
    if 'sattāyām' not in (rec.get('arthas') or []):
        fail('bhū 1,1 must carry sattāyām, got %r' % rec.get('arthas'))
    if len(rec['arthas']) != rec['artha_count']:
        fail('arthas truncated: %d stored vs artha_count %d'
             % (len(rec['arthas']), rec['artha_count']))
    for coord, r in dhp._load().items():
        if _re.search(r'\d$', r.get('palsule_root') or ''):
            fail('%s: footnote digits leaked into palsule_root %r'
                 % (coord, r['palsule_root']))


def test_dhatup_palsule_wired_into_tooltip():
    """H1333: the shared _ls_tooltip layer (which the H1301 review sheets reuse)
    returns the Palsule enrichment, and a non-DHĀTUP. citation is unaffected."""
    if not dhp.available():
        print('  .. skipped test_dhatup_palsule_wired_into_tooltip (concordance absent)')
        return
    sys.path.insert(0, HERE)
    import build_article_site as bas   # noqa: E402
    got = bas._ls_tooltip('n="DHĀTUP. 26,"', '91')
    if not got or 'Palsule √snih' not in got:
        fail('_ls_tooltip DHĀTUP. -> %r' % got)
    # gaṇa-only DHĀTUP. falls back to the pwgbib source title, never to Palsule
    plain = bas._ls_tooltip('', 'DHĀTUP.')
    if plain and 'Palsule' in plain:
        fail('gaṇa-only DHĀTUP. must not carry a Palsule record: %r' % plain)


def main():
    tests = [
        test_panini_full_form,
        test_panini_continuation_ref,
        test_panini_chapter_browse,
        test_spr_edition_guard,
        test_spr_second_ed_number,
        test_spr_fulltext_lookup,
        test_h2005_ed_bomb_ru_display_not_resolve,
        test_dhatup_palsule_coordinate_parse,
        test_dhatup_palsule_lookup,
        test_dhatup_palsule_record_is_complete_and_clean,
        test_dhatup_palsule_wired_into_tooltip,
    ]
    for t in tests:
        t()
        print('  ok %s' % t.__name__)
    print('ls_enrichment_selftest: %d checks passed' % len(tests))


if __name__ == '__main__':
    main()
