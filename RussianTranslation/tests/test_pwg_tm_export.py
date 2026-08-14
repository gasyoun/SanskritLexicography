"""H2685 Track C: lossless TMX / TEI Lex-0 / OntoLex exporters + loss ledger."""
import os
import sys
import tempfile

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import pwg_tm_canonical as C  # noqa: E402
import pwg_tm_export_core as X  # noqa: E402
import pwg_tm_export_loss as L  # noqa: E402
import pwg_tm_migrate_v1 as M  # noqa: E402
import export_pwg_tm_tei as TEI  # noqa: E402
import export_pwg_tm_ontolex as OL  # noqa: E402
import build_tmx  # noqa: E402

FIX = os.path.join(ROOT, 'schemas', 'fixtures',
                   'pwg_tm_canonical.publication.fixture.jsonl')


def _rows():
    pubs = C.read_jsonl(FIX)
    return [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z') for p in pubs]


def test_four_formats_round_trip_and_zero_loss():
    rows = _rows()
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'canonical.v1.jsonl')
        tmx = os.path.join(tmp, 'out.tmx')
        tei = os.path.join(tmp, 'out.xml')
        ttl = os.path.join(tmp, 'out.ttl')
        led = os.path.join(tmp, 'loss.json')
        C.write_jsonl(src, rows)
        X.write_text(tmx, X.build_tmx(rows, src, '1970-01-01T00:00:00Z'))
        X.write_text(tei, X.build_tei(rows, '1970-01-01T00:00:00Z', src))
        X.write_text(ttl, X.build_ontolex(rows, '1970-01-01T00:00:00Z'))
        ok, msg = X.validate_tmx_canonical(tmx)
        assert ok, msg
        ok, msg = X.validate_tei(tei)
        assert ok, msg
        ok, msg = X.validate_shacl_structural(open(ttl, encoding='utf-8').read())
        assert ok, msg
        report = L.run(src, tmx, tei, ttl, led)
        assert report['ok'], report['lost'][:5]
        assert report['records'] == 2


def test_exporters_are_deterministic():
    rows = _rows()
    a = X.build_tmx(rows, 'c.jsonl', '1970-01-01T00:00:00Z')
    b = X.build_tmx(rows, 'c.jsonl', '1970-01-01T00:00:00Z')
    assert a == b
    assert X.build_tei(rows, '1970-01-01T00:00:00Z', 'c.jsonl') == \
        X.build_tei(rows, '1970-01-01T00:00:00Z', 'c.jsonl')
    assert X.build_ontolex(rows, '1970-01-01T00:00:00Z') == \
        X.build_ontolex(rows, '1970-01-01T00:00:00Z')


def test_source_publication_stays_in_jsonl_and_hashed_elsewhere():
    rows = _rows()
    tmx = X.build_tmx(rows, 'c.jsonl', '1970-01-01T00:00:00Z')
    assert 'source_publication_hash' in tmx
    assert '"payload"' not in tmx
    ttl = X.build_ontolex(rows, '1970-01-01T00:00:00Z')
    assert 'pwglex:sourcePublicationHash' in ttl
    assert rows[0]['source_publication']['tm_record_id'] in \
        X.build_tei(rows, '1970-01-01T00:00:00Z', 'c.jsonl')


def test_cli_selftests():
    assert TEI.selftest() == 0
    assert OL.selftest() == 0
    assert L.selftest() == 0
    assert build_tmx.selftest() == 0


def test_corpus_tmx_validate_still_requires_cyrillic():
    """Existing sa-slp1 path must not be silently loosened."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'bad.tmx')
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<tmx version="1.4">\n'
                ' <header creationtool="x" creationtoolversion="1" segtype="phrase"\n'
                '   o-tmf="x" adminlang="en" srclang="sa-slp1" datatype="plaintext"\n'
                '   creationdate="20200101T000000Z" o-encoding="UTF-8"/>\n'
                ' <body>\n'
                ' <tu tuid="t1">\n'
                '  <tuv xml:lang="sa-slp1"><seg>deva</seg></tuv>\n'
                '  <tuv xml:lang="ru"><seg>deva</seg></tuv>\n'
                ' </tu>\n'
                ' </body>\n</tmx>\n')
        ok, msg = build_tmx.validate(path)
        assert not ok
        assert 'Cyrillic' in msg
