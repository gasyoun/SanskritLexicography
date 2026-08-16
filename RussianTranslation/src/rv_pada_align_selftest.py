#!/usr/bin/env python
r"""Selftest for rv_pada_align.py (H2850) — locus parsing, pāda split, the join,
the agreement verdict, and the build-time refusal against a re-translation.

Runs offline against fixtures; the rvlinks-backed cases self-skip (and say so)
when the sibling repo is not on this machine::

    python src/rv_pada_align_selftest.py
    python src/rv_pada_align.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import rv_pada_align as rp  # noqa: E402

FAILURES = []


def check(name, got, want):
    if got == want:
        print('  ok   %s' % name)
    else:
        print('  FAIL %s\n       got  %r\n       want %r' % (name, got, want))
        FAILURES.append(name)


def check_true(name, cond, detail=''):
    if cond:
        print('  ok   %s' % name)
    else:
        print('  FAIL %s %s' % (name, detail))
        FAILURES.append(name)


# --------------------------------------------------------------------------- fixtures

# rv07.084.01 as rvlinks carries it (triṣṭubh, 4 pādas, 4 published Russian lines).
HN_784_1 = [
    'ā vāṃ rājānāv adhvare vavṛtyāṃ havyebhir indrāvaruṇā namobhiḥ |',
    'pra vāṃ ghṛtācī bāhvor dadhānā pari tmanā viṣurūpā jigāti ||',
]
RU_784_1 = [
    'Вас, о два царя, я хотел бы привлечь к обряду',
    'Жертвами, о Индра-Варуна, поклонениями.',
    'Полная жира (жертвенная ложка,) которую держат в руках,',
    '(Принимая) разные формы, кружит около вас.',
]
# What PWG actually quotes for ṚV. 7,84,1 under parigā sense 2 — pādas c+d.
QUOTE_784_1 = r'pra vA^M Gf\tAcI^ bA\hvordaGA^nA\ pari\ tmanA\ vizu^rUpA jigAti'

# rv01.001.01, gāyatrī: 3 pādas, 3 published Russian lines, 2 hemistichs (8+8 | 8).
HN_1_1_1 = [
    'agnim īḷe purohitaṃ yajñasya devam ṛtvijam |',
    'hotāraṃ ratnadhātamam ||',
]


def test_locus_parsing():
    print('locus parsing')
    check('full siglum', rp.parse_rv_locus('ṚV. 7,84,1.')['locus'], 'rv07.084.01')
    check('continuation via n=', rp.parse_rv_locus('5,15,4.', 'ṚV.')['locus'], 'rv05.015.04')
    check('mandala 10', rp.parse_rv_locus('ṚV. 10,163,3')['locus'], 'rv10.163.03')
    check('Prātiśākhya refused', rp.parse_rv_locus('ṚV. PRĀT. 13,13.'), None)
    check('Anukramaṇī refused', rp.parse_rv_locus('ṚV. ANUKR. 1,1.'), None)
    check('bare siglum refused', rp.parse_rv_locus('ṚV.'), None)
    check('hymn-level refused', rp.parse_rv_locus('ṚV. 1,100'), None)
    check('other work refused', rp.parse_rv_locus('AV. 7,84,1'), None)
    check('mandala 11 refused', rp.parse_rv_locus('ṚV. 11,1,1'), None)


def test_syllables_and_split():
    print('metre + pāda split')
    check('triṣṭubh hemistich = 22 syllables',
          rp.syllables(HN_784_1[0].replace('|', '')), 22)
    check('ḷ is a consonant, not a syllable (agnim īḷe …) = 16',
          rp.syllables(HN_1_1_1[0].replace('|', '')), 16)
    padas, reg = rp.pada_split(HN_784_1, 4)
    check('4 pādas from 2 hemistichs', len(padas), 4)
    check_true('pāda c is the ghṛtācī half-line',
               rp.fold(padas[2]).startswith(rp.fold('pra vāṃ ghṛtācī')), padas[2])
    check_true('pāda d is pari tmanā …',
               rp.fold(padas[3]).startswith(rp.fold('pari tmanā')), padas[3])
    check_true('triṣṭubh split is regular (max deviation ≤ 2)', reg <= 2.0, reg)
    g, greg = rp.pada_split(HN_1_1_1, 3)
    check('gāyatrī = 3 pādas', len(g), 3)
    check('gāyatrī pāda sizes 8·8·8', [rp.syllables(p) for p in g], [8, 8, 8])
    check_true('gāyatrī split is regular', greg <= 2.0, greg)


def test_join_is_pada_granular():
    print('the join (offline fixture)')
    padas, _ = rp.pada_split(HN_784_1, 4)
    cov = [rp._coverage(p, rp.slp1_iast(QUOTE_784_1)) for p in padas]
    check_true('pāda a not selected (%.2f)' % cov[0], cov[0] < rp.PADA_HIT, cov)
    check_true('pāda b not selected (%.2f)' % cov[1], cov[1] < rp.PADA_HIT, cov)
    check_true('pāda c selected (%.2f)' % cov[2], cov[2] >= rp.PADA_HIT, cov)
    check_true('pāda d selected (%.2f)' % cov[3], cov[3] >= rp.PADA_HIT, cov)
    check_true('PWG daghānā vs rvlinks dadhānā survives folding',
               cov[2] >= 0.85, cov[2])


def test_verdict():
    print('agreement verdict')
    al = {'has_published_ru': True, 'confidence': 'high',
          'padas': ['c', 'd'], 'ru_lines': RU_784_1[2:], 'reason': ''}
    vd, why = rp.verdict('прийти, достигнуть, настигнуть кого-либо', al)
    check('specimen diverges', vd, 'diverges')
    check_true('divergence names the pādas', 'cd' in why, why)
    vd2, _ = rp.verdict('кружиться около, обходить кругом', al)
    check('lexical support -> agrees', vd2, 'agrees')
    vd3, _ = rp.verdict('прийти', {'has_published_ru': False, 'ru_lines': [], 'padas': []})
    check('no published Russian -> undecidable', vd3, 'undecidable')
    vd4, _ = rp.verdict('прийти', {'has_published_ru': True, 'confidence': 'low',
                                   'ru_lines': RU_784_1, 'padas': list('abcd'),
                                   'reason': 'line count vs metre'})
    check('low-confidence join -> undecidable', vd4, 'undecidable')


def test_build_time_refusal():
    print('build-time refusal')
    rvdir = rp.rvlinks_dir()
    if not rvdir:
        print('  skip (rvlinks not on this machine)')
        return
    raised = False
    try:
        rp.emit_citation_ru((7, 84, 1), QUOTE_784_1,
                            machine_ru='Он приходит к вам, принимая разные формы.')
    except rp.PublishedTranslationExists as exc:
        raised = True
        check_true('refusal names the locus', 'rv07.084.01' in str(exc), str(exc))
    check_true('machine translation over a published locus is REFUSED', raised)
    got = rp.emit_citation_ru((7, 84, 1), QUOTE_784_1)
    check('aligned emit is sourced from Elizarenkova', got['source'], 'elizarenkova')
    check('aligned emit returns exactly pādas c+d', got['ru_lines'], RU_784_1[2:])
    # A locus rvlinks has no Russian for is the ONLY case where machine RU passes.
    check('has_published_ru is true for 7.84.1', rp.has_published_ru(7, 84, 1), True)
    check('has_published_ru is false for a nonexistent hymn', rp.has_published_ru(1, 999, 1), False)
    free = rp.emit_citation_ru((1, 999, 1), '', machine_ru='машинный перевод')
    check('no published Russian -> machine RU allowed', free['source'], 'machine')


def test_gate_detects_a_violation():
    """Negative control: the gate must FIRE on a store that breaks the rule.

    Without this, `gate` reporting "0 violations" over the live store would be worthless
    — the previous implementation called `emit_citation_ru(..., machine_ru=None)`, which
    can never raise, so it printed a clean bill of health for any input at all.
    """
    print('build-time gate (fixture store)')
    rvdir = rp.rvlinks_dir()
    if not rvdir:
        print('  skip (rvlinks not on this machine)')
        return
    quote = QUOTE_784_1
    cite = '\n<ls>ṚV. 7,84,1.</ls>'
    clean = {
        'key1': 'gA', 'subcard': 'fixture-clean', 'iast': 'gā', 'sense_tag': '2',
        'de': '{%kommen%} {#' + quote + '#}' + cite,
        'ru': '{%прийти, достигнуть%} {#' + quote + '#}' + cite,
    }
    dirty = dict(clean, subcard='fixture-dirty',
                 ru='{%прийти, достигнуть%} «Он приходит к вам, принимая разные формы.»'
                    + cite)
    tmp = os.path.join(tempfile.gettempdir(), 'rv_pada_align_gate_fixture')
    os.makedirs(tmp, exist_ok=True)
    ok_path = os.path.join(tmp, 'clean.jsonl')
    bad_path = os.path.join(tmp, 'dirty.jsonl')
    for path, row in ((ok_path, clean), (bad_path, dirty)):
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + '\n')
    st_ok, v_ok = rp.scan_violations(ok_path, rvdir)
    check('quote carried through -> no violation', len(v_ok), 0)
    check('… and the row was actually examined', st_ok['quoted'], 1)
    st_bad, v_bad = rp.scan_violations(bad_path, rvdir)
    check('quote re-rendered as Russian -> violation', len(v_bad), 1)
    check_true('violation names the locus',
               v_bad and v_bad[0]['locus'] == 'rv07.084.01', v_bad)
    check('gate exits 3 on the violating store',
          rp.cmd_gate(argparse.Namespace(store=bad_path)), 3)
    check('gate exits 0 on the clean store',
          rp.cmd_gate(argparse.Namespace(store=ok_path)), 0)


def test_live_specimen():
    print('live specimen (rvlinks)')
    rvdir = rp.rvlinks_dir()
    if not rvdir:
        print('  skip (rvlinks not on this machine)')
        return
    al = rp.align(QUOTE_784_1, 7, 84, 1)
    check('specimen pādas', al['padas'], ['c', 'd'])
    check('specimen confidence', al['confidence'], 'high')
    check('specimen Russian', al['ru_lines'], RU_784_1[2:])
    # FINDINGS §544: a verse-granular read of rv10.163.03 attributes «прямая кишка»
    # to gudā́bhyaḥ, which is not what she wrote — the pāda join must not repeat it.
    al2 = rp.align(r'gudA\ByaH', 10, 163, 3)
    check('10.163.3 gudābhyaḥ is pāda a, not the whole verse', al2['padas'], ['a'])
    check('10.163.3 gudābhyaḥ = «кишок», not «прямая кишка»',
          al2['ru_lines'], ['Из внутренностей, из твоих кишок,'])
    check('single-word citation uses the contains mode', al2['mode'], 'contains')
    # 7.84.4: rvlinks prints only 3 Russian lines for a 4-pāda triṣṭubh (pāda c is
    # missing from the reproduction). The join must refuse rather than shift the lines.
    al3 = rp.align(r'ami^tA SUro^ dayate\ vasU^ni', 7, 84, 4)
    check('truncated published verse -> low confidence', al3['confidence'], 'low')
    check('… and undecidable, not a silent mis-join', rp.verdict('раздавать', al3)[0],
          'undecidable')


def run():
    for t in (test_locus_parsing, test_syllables_and_split, test_join_is_pada_granular,
              test_verdict, test_build_time_refusal, test_gate_detects_a_violation,
              test_live_specimen):
        t()
    print()
    if FAILURES:
        print('FAILED %d: %s' % (len(FAILURES), ', '.join(FAILURES)))
        return 1
    print('rv_pada_align selftest: all checks passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(run())
