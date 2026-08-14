#!/usr/bin/env python
"""Zero-loss ledger: every scholarly field path vs JSONL/TMX/TEI/OntoLex.

  python src/pwg_tm_export_loss.py --all-formats
  python src/pwg_tm_export_loss.py --selftest
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

DEFAULT_TMX = os.path.join(X.DEFAULT_RELEASE, 'pwg_tm.de-ru.tmx')
DEFAULT_TEI = os.path.join(X.DEFAULT_RELEASE, 'pwg_tm.tei.lex0.xml')
DEFAULT_TTL = os.path.join(X.DEFAULT_RELEASE, 'pwg_tm.ontolex.ttl')
DEFAULT_LEDGER = os.path.join(X.DEFAULT_RELEASE, 'loss_ledger.json')


def run(canonical, tmx, tei, ttl, out, limit=None):
    rows = X.load_canonical(canonical, limit=limit)
    with open(ttl, encoding='utf-8') as f:
        ttl_text = f.read()
    report = X.loss_report(rows, tmx, tei, ttl_text)
    report['inputs'] = {
        'canonical': os.path.relpath(canonical, C.ROOT).replace('\\', '/'),
        'tmx': os.path.relpath(tmx, C.ROOT).replace('\\', '/'),
        'tei': os.path.relpath(tei, C.ROOT).replace('\\', '/'),
        'ttl': os.path.relpath(ttl, C.ROOT).replace('\\', '/'),
        'canonical_sha256': C.sha256_file(canonical),
        'tmx_sha256': C.sha256_file(tmx),
        'tei_sha256': C.sha256_file(tei),
        'ttl_sha256': C.sha256_file(ttl),
    }
    C.write_json(out, report)
    return report


def selftest():
    pubs = C.read_jsonl(M.fixture_path())
    wrapped = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z') for p in pubs]
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'canonical.v1.jsonl')
        tmx = os.path.join(tmp, 'out.tmx')
        tei = os.path.join(tmp, 'out.xml')
        ttl = os.path.join(tmp, 'out.ttl')
        led = os.path.join(tmp, 'loss.json')
        C.write_jsonl(src, wrapped)
        X.write_text(tmx, X.build_tmx(wrapped, src, '1970-01-01T00:00:00Z'))
        X.write_text(tei, X.build_tei(wrapped, '1970-01-01T00:00:00Z', src))
        X.write_text(ttl, X.build_ontolex(wrapped, '1970-01-01T00:00:00Z'))
        report = run(src, tmx, tei, ttl, led)
        assert report['ok'], report['lost'][:3]
        assert report['records'] == 2
    print('pwg_tm_export_loss selftest OK -- 0 lost fields on fixture')
    return 0


def main():
    ap = argparse.ArgumentParser(description='PWG TM export loss ledger')
    ap.add_argument('--canonical', default=X.DEFAULT_CANONICAL)
    ap.add_argument('--tmx', default=DEFAULT_TMX)
    ap.add_argument('--tei', default=DEFAULT_TEI)
    ap.add_argument('--ttl', default=DEFAULT_TTL)
    ap.add_argument('--out', default=DEFAULT_LEDGER)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--all-formats', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.all_formats:
        sys.exit('pass --all-formats (or --selftest)')
    for path in (a.canonical, a.tmx, a.tei, a.ttl):
        if not os.path.exists(path):
            sys.exit('missing input: %s' % path)
    report = run(a.canonical, a.tmx, a.tei, a.ttl, a.out, limit=a.limit)
    print('pwg_tm_export_loss: records=%d accounted=%d lost=%d ok=%s -> %s' % (
        report['records'], report['accounted_checks'],
        report['lost_count'], report['ok'], a.out))
    if report['lost']:
        print('first losses:', json_preview(report['lost'][:3]))
    return 0 if report['ok'] else 1


def json_preview(obj):
    import json
    return json.dumps(obj, ensure_ascii=False)[:500]


if __name__ == '__main__':
    sys.exit(main())
