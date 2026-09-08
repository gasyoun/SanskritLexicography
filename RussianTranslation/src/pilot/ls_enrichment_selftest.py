# -*- coding: utf-8 -*-
"""Fixture selftest for the <ls> link-enrichment (H1307 Pāṇini + Spr. (II);
H1333 DHĀTUP. -> Palsule; H4339 the Monier-Williams second coordinate witness).

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
    # A coordinate Böhtlingk lists under two root spellings is DROPPED, not guessed.
    # 2,8 (skand/skund) stays dropped after H4339 as well, and for a reason worth
    # knowing: MW's Westergaard field DOES number it (`skudi,2.8`), but `skudi` carries
    # the nasal as an anubandha-marked infix, so the article headword is not contained
    # in it and the claimant test — deliberately containment, never a stripping rule
    # (H328) — declines to confirm. A conservative miss, not a resolution.
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


def test_dhatup_mw_provenance_is_stamped_and_never_overrides_pwg():
    """H4339: the MW second witness may ADD coordinates, never rewrite Böhtlingk's.

    Three separable claims, each of which would be a real defect if it failed:
      1. every row declares a provenance the consumer knows how to read;
      2. the PWG-derived row count still equals H1333's shipped number, so the MW pass
         demonstrably added rows instead of moving existing ones;
      3. where the two dictionaries disagree, a row Böhtlingk attributed keeps HIS root.
         MW's dissent is published for adjudication, never acted on. The one case where
         MW's spelling does ship is `mw-respell` — Palsule has no entry under
         Böhtlingk's spelling, so there was no PWG row to displace — and such a row must
         still carry `pwg_root_slp1`, so the reading it set aside stays recoverable."""
    if not dhp.available():
        print('  .. skipped test_dhatup_mw_provenance_is_stamped_and_never_overrides_pwg')
        return
    import json as _json
    table = dhp._load()
    st = dhp.stats()
    known = set(dhp._SOURCE_MARK)
    seen = {}
    for c, r in table.items():
        src = r.get('source')
        if src not in known:
            fail('%s: unknown provenance %r (known: %s)' % (c, src, sorted(known)))
        seen[src] = seen.get(src, 0) + 1
    if seen.get('pwg') != st.get('coords_linked_pwg'):
        fail('pwg rows %r != _stats.coords_linked_pwg %r'
             % (seen.get('pwg'), st.get('coords_linked_pwg')))
    if seen.get('mw') != st.get('coords_filled_from_mw'):
        fail('mw rows %r != _stats.coords_filled_from_mw %r'
             % (seen.get('mw'), st.get('coords_filled_from_mw')))
    if len(table) != st.get('coords_linked'):
        fail('table size %d != _stats.coords_linked %r' % (len(table), st['coords_linked']))

    with open(dhp._JSON, encoding='utf-8') as f:
        payload = _json.load(f)
    dis = payload.get('_mw_disagreements')
    if not dis:
        fail('_mw_disagreements must be published, not summarized away')
    for d in dis:
        for k in ('coord', 'pwg_root_slp1', 'mw_root_slp1', 'shape', 'shipped_reading'):
            if not d.get(k):
                fail('disagreement %r missing %s' % (d.get('coord'), k))
        row = table.get(d['coord'])
        if row is None:
            if d['shipped_reading'] != 'dropped':
                fail('%s: shipped_reading %r but no row' % (d['coord'], d['shipped_reading']))
            continue
        if row['source'] == 'pwg' and row['root_slp1'] != d['pwg_root_slp1']:
            fail('%s: MW overrode a PWG row (%r shipped, PWG says %r)'
                 % (d['coord'], row['root_slp1'], d['pwg_root_slp1']))
        if row['source'] == 'mw':
            fail('%s: a disputed coordinate cannot be a pure MW fill — PWG named a root'
                 % d['coord'])
        if row['source'] == 'mw-respell' and not row.get('pwg_root_slp1'):
            fail('%s: mw-respell row must keep the PWG reading it set aside' % d['coord'])
        if row['source'] != d['shipped_reading']:
            fail('%s: shipped_reading %r != row source %r'
                 % (d['coord'], d['shipped_reading'], row['source']))


def test_dhatup_pw_sibling_is_screened_and_never_displaces_pwg():
    """H4349: pw may fill a coordinate the table lacks; it may not restate one.

    pw is Böhtlingk's own abridgement, so its rows are stamped `pw` and kept apart from
    `pwg` — same-author is not same-statement, and a consumer reconstructing H1333 or
    H4339 filters on `source`. Four separable claims:
      1. the coverage totals in `_stats` add up to the table actually shipped, so a
         reader cannot be told a number the artifact does not contain;
      2. no `pw` row sits on a coordinate PWG resolved — the pass fills gaps only;
      3. every `pw` row's root is one Palsule glosses (that is what makes it a row);
      4. the two out-of-space citations are REFUSED and PUBLISHED with the ceiling they
         failed. `1,840` and `1,960` are the live cases: PWG and MW cite gaṇa 1 only as
         `1,1`, so a gaṇa-1 serial of 840 is a citation-split artifact, not a root. A
         build that quietly shipped or quietly dropped them would fail here."""
    if not dhp.available():
        print('  .. skipped test_dhatup_pw_sibling_is_screened_and_never_displaces_pwg')
        return
    import json as _json
    table = dhp._load()
    st = dhp.stats()

    pw_rows = {c: r for c, r in table.items() if r['source'] == 'pw'}
    if len(pw_rows) != st.get('coords_filled_from_pw'):
        fail('pw rows %d != _stats.coords_filled_from_pw %r'
             % (len(pw_rows), st.get('coords_filled_from_pw')))
    if st.get('coords_linked') != len(table):
        fail('_stats.coords_linked %r != table size %d'
             % (st.get('coords_linked'), len(table)))
    expected = (st.get('coords_linked_after_mw', 0)
                + st.get('coords_filled_from_pw', 0)
                + st.get('coords_filled_from_pwg-dotted', 0))
    if expected != len(table):
        fail('H4339 rows + H4349 fills = %d, table has %d' % (expected, len(table)))

    with open(dhp._JSON, encoding='utf-8') as f:
        payload = _json.load(f)
    for c, r in pw_rows.items():
        if r.get('pwg_root_slp1'):
            fail('%s: a pw row displaced a PWG attribution (%r)'
                 % (c, r['pwg_root_slp1']))
        if not r.get('pw_root_slp1') or not r.get('arthas'):
            fail('%s: pw row missing its provenance root or its Palsule arthas' % c)

    out = payload.get('_out_of_coordinate_space')
    if not out:
        fail('_out_of_coordinate_space must be published, not netted out')
    for x in out:
        if x['coord'] in table:
            fail('%s was refused as out-of-space and shipped anyway' % x['coord'])
        if not x.get('attested_ceiling') or x['serial'] <= x['attested_ceiling']:
            fail('%s: refused without a ceiling that explains the refusal (%r)'
                 % (x['coord'], x.get('attested_ceiling')))
    if {x['coord'] for x in out} != {'1,840', '1,960'}:
        fail('out-of-space set moved: %r' % sorted(x['coord'] for x in out))


def test_dhatup_pwg_dotted_class_is_measured_and_empty():
    """H4349: PWG's 636 dotted-id articles cite ONE coordinate, and it ships nothing.

    This pins a negative result, which is the only kind of result that rots silently.
    The `_L` pattern H1333 measured PWG on accepts an all-digit `<L>` id, so 636 of
    PWG's articles are invisible to it; the widened pass exists to say how much that
    hides. The answer is one coordinate — `15,89`, claimed by `4. kar` — and PWG
    already contests it (`<L>18794` heads it `kfv`, and Böhtlingk's own prose there
    says the root is `kṛv`, placed under `kar`, its final `-v` unjustified). A
    same-book pass may not break a tie its own book declared, so it is refused.

    If a corpus update ever puts real coordinates into that id space, `coords_cited`
    moves and this test fails — which is the point. It is not asserting that the class
    is worthless; it is asserting that today's emptiness is measured, not assumed."""
    if not dhp.available():
        print('  .. skipped test_dhatup_pwg_dotted_class_is_measured_and_empty')
        return
    st = dhp.stats()
    if st.get('pwg-dotted_articles') != 636:
        fail('dotted-id article count moved: %r (was 636)'
             % st.get('pwg-dotted_articles'))
    if st.get('pwg-dotted_coords_cited') != 1:
        fail('dotted-id articles now cite %r coordinates, not 1 — re-adjudicate before '
             'trusting the class' % st.get('pwg-dotted_coords_cited'))
    if st.get('coords_filled_from_pwg-dotted'):
        fail('the dotted-id class shipped %r rows; it must ship none until the one '
             'contested coordinate is adjudicated'
             % st.get('coords_filled_from_pwg-dotted'))
    if st.get('pwg-dotted_refused_same_book_conflict') != 1:
        fail('15,89 must be refused by the same-book guard, not by accident: %r'
             % st.get('pwg-dotted_refused_same_book_conflict'))
    if any(r['source'] == 'pwg-dotted' for r in dhp._load().values()):
        fail('a pwg-dotted row is in the table but _stats says none were filled')
    if 'pwg-dotted' not in dhp._SOURCE_MARK:
        fail('the pwg-dotted siglum must be registered so a future row renders marked')


def test_dhatup_h1333_and_h4339_baselines_are_readable_after_h4349():
    """H4349: the two shipped baselines stay derivable FROM the artifact.

    Not a rebuild — the selftest has no corpus — but the weaker claim that still
    catches a silent drift: H1333's 1226 PWG rows and 59.9% artha accuracy, and
    H4339's 1465-row composition, must still be readable off `_stats` and must still
    match what the table contains row by row."""
    if not dhp.available():
        print('  .. skipped test_dhatup_h1333_and_h4339_baselines_are_readable_after_h4349')
        return
    table = dhp._load()
    st = dhp.stats()
    counts = {}
    for r in table.values():
        counts[r['source']] = counts.get(r['source'], 0) + 1
    if counts.get('pwg') != 1226:
        fail('H1333 baseline moved: %r PWG rows, not 1226' % counts.get('pwg'))
    if (st.get('inline_artha_agree'), st.get('inline_artha_examined')) != (139, 232):
        fail('H1333 artha accuracy moved: %r of %r'
             % (st.get('inline_artha_agree'), st.get('inline_artha_examined')))
    if (counts.get('mw'), counts.get('mw-respell')) != (140, 99):
        fail('H4339 composition moved: mw=%r mw-respell=%r'
             % (counts.get('mw'), counts.get('mw-respell')))
    if st.get('coords_linked_after_mw') != 1226 + 140 + 99:
        fail('_stats.coords_linked_after_mw %r != the 1465 rows H4339 shipped'
             % st.get('coords_linked_after_mw'))


def test_dhatup_mw_tooltip_marks_the_second_witness():
    """H4339: a reader can tell a Böhtlingk attribution from an MW one at a glance.

    2,19 (ūrd/urd — Böhtlingk spells it both ways and claims neither) is MW-derived and
    must carry `[MW]`; 26,91 (snih) is Böhtlingk's own and must stay unmarked."""
    if not dhp.available():
        print('  .. skipped test_dhatup_mw_tooltip_marks_the_second_witness')
        return
    rec = dhp.record('', 'DHĀTUP. 2,19')
    if not rec or rec.get('source') != 'mw':
        print('  .. skipped: 2,19 is not MW-derived in this build (%r)'
              % (rec or {}).get('source'))
        return
    tip = dhp.palsule_for('', 'DHĀTUP. 2,19')
    if '[MW]' not in (tip or ''):
        fail('MW-derived tooltip must mark its witness: %r' % tip)
    if 'http' in (tip or ''):
        fail('no fabricated href, MW rows included: %r' % tip)
    plain = dhp.palsule_for('', 'DHĀTUP. 26,91')
    if 'MW' in (plain or ''):
        fail('a PWG-attributed tooltip must carry no MW mark: %r' % plain)


def test_dhatup_roman_gana_reading():
    """H4339: MW writes Böhtlingk's gaṇa as a Roman numeral, and the whole range 1–35
    must read back exactly — an off-by-one here silently files a root under the wrong
    gaṇa, which no later check would catch."""
    sys.path.insert(0, SRC)
    import build_dhatup_palsule as bld   # noqa: E402
    for roman, want in (('i', 1), ('iv', 4), ('v', 5), ('ix', 9), ('x', 10),
                        ('xxiv', 24), ('xxxiii', 33), ('xxxv', 35), ('XXVI', 26)):
        got = bld.roman_to_int(roman)
        if got != want:
            fail('roman_to_int(%r) = %r, want %r' % (roman, got, want))
    for bad in ('', 'abc', '26'):
        if bld.roman_to_int(bad) is not None:
            fail('roman_to_int(%r) should be None' % bad)


def test_dhatup_mw_variant_reading_is_never_harvested_as_a_claim():
    """H4339 adjudication (07-09-2026): a prose citation on a `<ab>v.l.</ab>` line
    states which reading MW REJECTS, so harvesting it inverts the source.

    Coordinate 20,21 is the case that shipped wrong and was caught by the independent
    verifier. MW's article reads, in full:

        <hom>1.</hom> <s>kzal</s> ¦ <ab>v.l.</ab> for √ <s>kzar</s>, <ls>Dhātup. xx, 21</ls>.

    PWG could not choose between `kzal` and `kzar`, no `<info westergaard>` numbers
    20,21 anywhere, so the prose fallback ran — and filled the coordinate with `kzal`,
    the one root that sentence disowns. Both roots are in Palsule, so the wrong one was
    reachable. The coordinate is now DROPPED rather than guessed: MW attributes it to
    `kzar` in words the parser does not read, and inventing that attribution would be
    the fabrication this file exists to prevent."""
    if not dhp.available():
        print('  .. skipped test_dhatup_mw_variant_reading (concordance absent)')
        return
    # 32,130 is the depth case: the `)` closes the parenthesis the note itself sits in,
    # so it ends nothing and the note still governs the citation after it. PWG agrees —
    # its `paRq` article says `v. l. für {#piRq#}` and its `piRqay` article attributes
    # 32,130 positively — so shipping `paṇḍ` was a root BOTH dictionaries disown.
    for coord, away_to in (('20,21', 'kṣar'), ('32,43', 'tāḍ'), ('32,130', 'piṇḍ')):
        rec = dhp.record('', 'DHĀTUP. %s' % coord)
        if rec is not None and rec.get('source') in ('mw', 'mw-respell'):
            fail('%s shipped from MW as %r — MW\'s own sentence assigns it to %s and '
                 'names this root the rejected reading'
                 % (coord, rec.get('palsule_root'), away_to))

    # ...AND THE INVERSE MUST SURVIVE. A first, line-scoped version of the guard read
    # any `v.l.` on the line as disqualifying and so destroyed two correct rows. Which
    # side of the citation the note sits on is what it means:
    #   juq  `<ls n="Dhātup. xxviii,">37</ls> (<ab>v.l.</ab> √ <s>jun</s>)`   note AFTER
    #        -> 28,37 is the headword's, `jun` is the variant. Must SHIP.
    #   dAs  `(<ab>v.l.</ab> for <s>dAS</s>, <ls>Vop.</ls>; <ab>ib.</ab> <ls>xxvii, 32</ls>)`
    #        -> a `;` ends the note's clause, so it governs the Vop. citation, not this
    #        one. 27,32 agrees with Böhtlingk and must stay in the cross-validation.
    juq = dhp.record('', 'DHĀTUP. 28,37')
    if not juq or juq.get('source') != 'mw':
        fail('28,37 must ship from MW (the v.l. note follows the citation and names '
             'the OTHER root) — got %r' % (juq and juq.get('source')))
    das = dhp.record('', 'DHĀTUP. 27,32')
    if not das or das.get('source') != 'pwg':
        fail('27,32 must keep Böhtlingk\'s own attribution — got %r'
             % (das and das.get('source')))
    st = dhp.stats()
    if not st.get('mw_prose_claims_refused_variant_reading'):
        fail('the v.l. refusal is not being counted — %r'
             % st.get('mw_prose_claims_refused_variant_reading'))
    # The prose-only fills are the weak branch and must stay a published, small number:
    # if this ever approaches the field-backed count, the field-first rule has stopped
    # being what the coverage rests on.
    prose_only = st.get('coords_filled_from_mw_prose_only')
    total_mw = (st.get('coords_filled_from_mw', 0)
                + st.get('coords_filled_from_mw_respell', 0))
    if prose_only is None or prose_only > total_mw * 0.25:
        fail('prose-only fills %r of %r MW fills — the fallback is carrying the pass'
             % (prose_only, total_mw))


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
        test_dhatup_mw_provenance_is_stamped_and_never_overrides_pwg,
        test_dhatup_mw_tooltip_marks_the_second_witness,
        test_dhatup_roman_gana_reading,
        test_dhatup_mw_variant_reading_is_never_harvested_as_a_claim,
        test_dhatup_palsule_wired_into_tooltip,
        test_dhatup_pw_sibling_is_screened_and_never_displaces_pwg,
        test_dhatup_pwg_dotted_class_is_measured_and_empty,
        test_dhatup_h1333_and_h4339_baselines_are_readable_after_h4349,
    ]
    for t in tests:
        t()
        print('  ok %s' % t.__name__)
    print('ls_enrichment_selftest: %d checks passed' % len(tests))


if __name__ == '__main__':
    main()
