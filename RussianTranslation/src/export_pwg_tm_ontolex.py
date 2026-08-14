#!/usr/bin/env python
"""OntoLex-Lemon / vartrans / lexicog / PROV-O exporter (H2685 Track C).

  python src/export_pwg_tm_ontolex.py
  python src/export_pwg_tm_ontolex.py --validate-shacl
  python src/export_pwg_tm_ontolex.py --selftest
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_canonical as C  # noqa: E402
import pwg_tm_export_core as X  # noqa: E402
import pwg_tm_migrate_v1 as M  # noqa: E402

DEFAULT_OUT = os.path.join(X.DEFAULT_RELEASE, 'pwg_tm.ontolex.ttl')
SHACL_PATH = os.path.join(X.SCHEMA_DIR, 'pwg_tm_ontolex.shacl.ttl')


def export(canonical, out_path, limit=None, created=None):
    rows = X.load_canonical(canonical, limit=limit)
    stamp = X.created_stamp(rows, created)
    ttl = X.build_ontolex(rows, stamp)
    X.write_text(out_path, ttl)
    return rows, out_path, ttl


def validate_shacl(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    ok, msg = X.validate_shacl_structural(text)
    extra = []
    if os.path.exists(SHACL_PATH):
        extra.append('shapes=' + os.path.relpath(SHACL_PATH, C.ROOT).replace('\\', '/'))
    pyshacl = _try_pyshacl(path)
    if pyshacl:
        extra.append(pyshacl)
    return ok, msg + ((' [' + '; '.join(extra) + ']') if extra else '')


def _try_pyshacl(data_path):
    if not os.path.exists(SHACL_PATH):
        return 'pyshacl=no-shapes'
    try:
        import pyshacl  # noqa: F401
        from pyshacl import validate
    except ImportError:
        return 'pyshacl=not-installed (stdlib structural shapes used)'
    try:
        conforms, _graph, report = validate(
            data_path, shacl_graph=SHACL_PATH,
            inference='rdfs', abort_on_first=False)
    except Exception as exc:
        return 'pyshacl=error %s' % exc
    if conforms:
        return 'pyshacl=pass'
    return 'pyshacl=FAIL %s' % report[:400]


def selftest():
    pubs = C.read_jsonl(M.fixture_path())
    wrapped = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z') for p in pubs]
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'canonical.v1.jsonl')
        dest = os.path.join(tmp, 'out.ttl')
        C.write_jsonl(src, wrapped)
        _rows, _p, ttl = export(src, dest, created='1970-01-01T00:00:00Z')
        ok, msg = validate_shacl(dest)
        assert ok, msg
        again = X.build_ontolex(wrapped, '1970-01-01T00:00:00Z')
        assert ttl == again, 'Turtle not deterministic'
        assert 'vartrans:Translation' in ttl
        assert 'lexicog:Entry' in ttl  # fixture has a multi-sense fragment
        assert 'prov:Activity' in ttl
    print('export_pwg_tm_ontolex selftest OK --', msg)
    return 0


def main():
    ap = argparse.ArgumentParser(description='OntoLex export of PWG TM canonical JSONL')
    ap.add_argument('--in', dest='inp', default=X.DEFAULT_CANONICAL)
    ap.add_argument('--out', dest='out', default=DEFAULT_OUT)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--created', default=None)
    ap.add_argument('--validate-shacl', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.validate_shacl and os.path.exists(a.out) and not a.limit:
        ok, msg = validate_shacl(a.out)
        print(msg)
        return 0 if ok else 1
    if not os.path.exists(a.inp):
        sys.exit('canonical JSONL not found: %s' % a.inp)
    rows, dest, _ttl = export(a.inp, a.out, limit=a.limit, created=a.created)
    print('export_pwg_tm_ontolex: %d records -> %s' % (len(rows), dest))
    if a.validate_shacl:
        ok, msg = validate_shacl(dest)
        print(msg)
        return 0 if ok else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
