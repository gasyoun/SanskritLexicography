"""Tests for the H7073 edition/journal filter and seeded adjudication draw.

Run:  python HeadwordLists/works_catalogue/test_census_ncc_mss.py
  or: python -m pytest HeadwordLists/works_catalogue/test_census_ncc_mss.py
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census_ncc_mss as c


SIGLA = ['Adyar D.', 'IV', 'IM', 'MT', 'TD', 'Sup', 'JPTS', 'JRAS', 'Bk',
         'Ser', 'JAIPUR MUS.', 'FOO']
CAT_RE = c.catalogue_regex(sorted(SIGLA, key=len, reverse=True))


def units(body):
    got, _ = c.extract_units(body, CAT_RE)
    return got


def test_roman_volume_marker_is_not_a_catalogue():
    got = units('Adyar D. IV. 950.')
    assert ('Adyar D', '950') in got
    assert not any(cat == 'IV' for cat, _ in got)
    assert 'IV' not in CAT_RE.pattern


def test_journal_and_series_refs_are_removed():
    assert units('See JPTS. 1890, 91; JRAS. 1911, 197 ff.') == []
    assert units('Br. Mus. Pt.. Bk.. 1938, p. 2187.') == []
    assert units('Jaipur Mus. Ser. 2. p. 72.') == []


def test_page_prefixed_reference_is_removed():
    got, st = c.extract_units('TD. p.. 191b. 243a.', CAT_RE)
    assert got == []
    assert st['filtered']['page_ref_prefix'] == 1


def test_year_like_reference_is_removed():
    got, st = c.extract_units('FOO. 1890, p. 12.', CAT_RE)
    assert got == []
    assert st['filtered']['year_like'] == 1


def test_genuine_manuscript_units_survive():
    got = units('IM. 2427. MT. 1208. TD. 3824. Bodl. Sup. 39-41.')
    assert ('IM', '2427') in got
    assert ('MT', '1208') in got
    assert ('TD', '3824') in got
    assert ('Sup', '39') in got and ('Sup', '41') in got


def test_stats_separate_raw_from_post_filter():
    _, st = c.extract_units('Adyar D. IV. 950. See JPTS. 1890.', CAT_RE)
    assert st['raw_units'] == 2
    assert sum(st['filtered'].values()) == 1
    assert st['filtered']['journal_or_series'] == 1


def _rows():
    body = '<p>Adyar D. IV. 950. IM. 2427.</p>'
    return [
        {'ncc_id': '1_1_a_1', 'volume': '1', 'iast': 'A', 'body_html': body},
        {'ncc_id': '1_2_a_2', 'volume': '1', 'iast': 'B', 'body_html': body},
        {'ncc_id': '1_3_a_3', 'volume': '1', 'iast': 'C', 'body_html': body},
        {'ncc_id': '2_1_a_1', 'volume': '2', 'iast': 'D', 'body_html': body},
        {'ncc_id': '2_2_a_2', 'volume': '2', 'iast': 'E', 'body_html': body},
    ]


def _draw(tmp_path, seed):
    out = os.path.join(str(tmp_path), f'draw_{seed}.tsv')
    st = c.run_adjudication_sample(_rows(), CAT_RE, 3, out, seed=seed)
    with open(out, encoding='utf-8') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    return st, rows


def test_sampler_is_seeded_and_stratified(tmp_path):
    st1, first = _draw(tmp_path, 7)
    st2, second = _draw(tmp_path, 7)
    assert st1['seed'] == 7 and st1['sample'] == 3
    assert first == second
    assert {r['volume'] for r in first} == {'1', '2'}


def test_sampler_marks_unreviewed_rows(tmp_path):
    _, rows = _draw(tmp_path, 7)
    assert all(r['verdict'] == '' and r['reason'] == '' for r in rows)
    assert all(r['source_span'] for r in rows)


if __name__ == '__main__':
    import tempfile
    for name, fn in sorted(globals().items()):
        if name.startswith('test_') and callable(fn):
            if 'tmp_path' in fn.__code__.co_varnames:
                with tempfile.TemporaryDirectory() as d:
                    fn(d)
            else:
                fn()
            print('ok', name)
