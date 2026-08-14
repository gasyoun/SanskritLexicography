#!/usr/bin/env python
"""TEI Lex-0 exporter over PWG TM canonical JSONL (H2685 Track C).

  python src/export_pwg_tm_tei.py
  python src/export_pwg_tm_tei.py --validate
  python src/export_pwg_tm_tei.py --selftest
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

DEFAULT_OUT = os.path.join(X.DEFAULT_RELEASE, 'pwg_tm.tei.lex0.xml')
RNG_PATH = os.path.join(X.SCHEMA_DIR, 'pwg_tm_tei_lex0.rng')
SCH_PATH = os.path.join(X.SCHEMA_DIR, 'pwg_tm_tei_lex0.sch')


def export(canonical, out_path, limit=None, created=None):
    rows = X.load_canonical(canonical, limit=limit)
    stamp = X.created_stamp(rows, created)
    xml = X.build_tei(rows, stamp, canonical)
    X.write_text(out_path, xml)
    return rows, out_path


def validate_path(path):
    ok, msg = X.validate_tei(path)
    extra = []
    if os.path.exists(RNG_PATH):
        extra.append('rng=' + os.path.relpath(RNG_PATH, C.ROOT).replace('\\', '/'))
    if os.path.exists(SCH_PATH):
        extra.append('schematron=' + os.path.relpath(SCH_PATH, C.ROOT).replace('\\', '/'))
    jing = _try_jing(path)
    if jing:
        extra.append(jing)
    return ok, msg + ((' [' + '; '.join(extra) + ']') if extra else '')


def _try_jing(path):
    """Optional jing RNG check. Absence is not a fail (Windows has no jing)."""
    import shutil
    import subprocess
    jing = shutil.which('jing')
    if not jing or not os.path.exists(RNG_PATH):
        return 'jing=not-installed (stdlib structural validator used)'
    try:
        proc = subprocess.run(
            [jing, RNG_PATH, path],
            capture_output=True, text=True, encoding='utf-8', timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 'jing=error %s' % exc
    if proc.returncode == 0:
        return 'jing=pass'
    return 'jing=FAIL %s' % (proc.stdout or proc.stderr or proc.returncode)


def selftest():
    pubs = C.read_jsonl(M.fixture_path())
    wrapped = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z') for p in pubs]
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'canonical.v1.jsonl')
        dest = os.path.join(tmp, 'out.xml')
        C.write_jsonl(src, wrapped)
        export(src, dest, created='1970-01-01T00:00:00Z')
        ok, msg = validate_path(dest)
        assert ok, msg
        again = X.build_tei(wrapped, '1970-01-01T00:00:00Z', src)
        with open(dest, encoding='utf-8') as f:
            assert f.read() == again, 'TEI not deterministic'
    print('export_pwg_tm_tei selftest OK --', msg)
    return 0


def main():
    ap = argparse.ArgumentParser(description='TEI Lex-0 export of PWG TM canonical JSONL')
    ap.add_argument('--in', dest='inp', default=X.DEFAULT_CANONICAL)
    ap.add_argument('--out', dest='out', default=DEFAULT_OUT)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--created', default=None)
    ap.add_argument('--validate', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.validate and os.path.exists(a.out) and not a.limit:
        ok, msg = validate_path(a.out)
        print(msg)
        return 0 if ok else 1
    if not os.path.exists(a.inp):
        sys.exit('canonical JSONL not found: %s' % a.inp)
    rows, dest = export(a.inp, a.out, limit=a.limit, created=a.created)
    print('export_pwg_tm_tei: %d records -> %s' % (len(rows), dest))
    if a.validate:
        ok, msg = validate_path(dest)
        print(msg)
        return 0 if ok else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
