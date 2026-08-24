"""PR-B regression: consolidated corpus_gate index loaders keep their shapes."""
import os
import sys
import tempfile

ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import corpus_gate as cg  # noqa: E402


def _seed_sources(td):
    def w(name, lines):
        with open(os.path.join(td, name), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines) + '\n')
    w('koch.jsonl', [
        '{"slp1": "agni", "gloss": "огонь"}',
        '{"slp1": "vaHnis", "gloss": "пламя"}',
    ])
    w('fri.jsonl', [
        '{"slp1": "agni", "gloss": "огонь, бог огня"}',
    ])
    w('grin12.jsonl', [
        '{"slp1": "agni", "gloss": "пожар"}',
    ])
    w('apte_hi.jsonl', [
        '{"slp1": "agniH", "stem": "agni", "pos": "m.", '
        '"gloss": "अग्नि", "dev": "अग्नि", "attribution": "Apte"}',
    ])
    w('kosha_syn.jsonl', ['{"slp1": "agni", "syn_dev": ["पावक", "विश्वपाणि"]}}'.replace('}}', '}')])
    w('meulenbeld_plants.jsonl', [
        '{"slp1": "plava", "stem": "", "binomials": ["Sida cordifolia"]}',
    ])


def test_loader_shapes_and_caches(tmp_path=None):
    with tempfile.TemporaryDirectory() as td:
        old_here = cg.HERE
        cg.HERE = td
        try:
            _seed_sources(td)
            idx = cg.load_index()
            assert set(cg.SOURCES_PRESENT) == {'koch', 'fri'}
            assert idx[cg.form_key('agni')]['koch'] == ['огонь']
            assert idx[cg.form_key('agni')]['fri'] == ['огонь, бог огня']
            indep, kow = cg.lookup(idx, 'agni')
            codes = [d['code'] for d in indep]
            assert codes == ['koch', 'fri'], codes
            assert kow == []

            sidx = cg.load_specialist_index()
            assert sidx[cg.form_key('agni')]['grin12'] == ['пожар']
            assert sidx is cg._INDEX_CACHE['specialist']

            sense_idx = cg.load_sense_index()
            fk_stem = cg.form_key('agni')
            recs = sense_idx[fk_stem]['apte_hi']
            # slp1 ('agniH') and stem ('agni') collapse to ONE form_key here, so
            # the row is appended once — same as the pre-consolidation loader.
            assert len(recs) == 1
            assert {r['pos'] for r in recs} == {'m.'}
            w2 = '{"slp1": "vaHniH", "stem": "vaHni", "pos": "f.", "gloss": "g", "dev": "d", "attribution": "a"}'
            with open(os.path.join(td, 'apte_hi.jsonl'), 'a', encoding='utf-8') as f:
                f.write(w2 + '\n')
            cg._INDEX_CACHE.pop('sense', None)
            recs2 = cg.load_sense_index()[cg.form_key('vaHni')]['apte_hi']
            assert len(recs2) == 1  # distinct slp1/stem keys, single appended rec

            kidx = cg.load_kosha_index()
            assert kidx[fk_stem] == {'पावक', 'विश्वपाणि'}
            assert sorted(cg.lookup_synonyms('agni')) == ['पावक', 'विश्वपाणि']

            pidx = cg.load_plant_index()
            assert pidx[cg.form_key('plava')] == ['Sida cordifolia']
            assert cg.lookup_binomials('plava') == ['Sida cordifolia']

            # absent sources degrade to empty structures, not exceptions
            cg.HERE = td
            empty_idx = cg._load_gloss_index(['nosuch'])
            assert empty_idx == {}
            assert list(cg._iter_jsonl_path(os.path.join(td, 'missing'))) == []
        finally:
            cg.HERE = old_here
            cg._INDEX_CACHE.clear()
            cg.SOURCES_PRESENT.clear()
