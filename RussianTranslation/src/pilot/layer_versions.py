#!/usr/bin/env python
"""Layer-version log — WHICH upstream commit / scrape each source layer was drawn from.

Answers M.G.'s question "do we log when each layer was added?". Orthogonal to
``pipeline_version.py`` (semver of OUR tooling) and to ``provenance.model_version``
(the Claude model): this stamps the UPSTREAM the pwg_ru corpus consumes —

  pwg / pw / sch / pwkvn  — csl-orig (git): the repo HEAD + the last commit that
                            touched ``v02/<code>/<code>.txt`` (+ record/headword counts).
  nws                      — Halle scrape (not git): scraped-card count, net-new
                            (has_nws_extra) count, and a hash of the cached key list.

Each ``snapshot`` appends one immutable record to ``pilot/layer_version_log.jsonl``
(append-only) so a later run can answer "when did pw last move under us, and to
which commit?" — the temporal companion to ``watch_upstream.py``, which reports the
*delta* between two such snapshots.

  python layer_versions.py snapshot        compute + append today's upstream state
  python layer_versions.py show            print the latest logged snapshot
  python layer_versions.py show --all      print every logged snapshot (compact)
  python layer_versions.py --selftest

Reuses ``dict_merge`` for the csl-orig layer indexes and the NWS cache layout —
does NOT re-parse csl-orig or re-enumerate NWS itself.
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import dict_merge as dm            # noqa: E402  — csl-orig layer indexes + NWS layout
from window_common import append_jsonl_line  # noqa: E402

LOG = os.path.join(HERE, 'layer_version_log.jsonl')
NWS_DIR = dm.NWS_DIR
CSL_ORIG = os.environ.get('PWG_RU_CSL_ORIG') or os.path.dirname(dm.V02)   # .../csl-orig (env-overridable for CI)
NWS_CONTROL = ('_watch_state.json', '_status.txt', '_progress.log')


# --- git helpers (csl-orig is READ-ONLY here — only rev-parse / log) ---------
def _git(*args, cwd=CSL_ORIG):
    try:
        r = subprocess.run(['git', '-C', cwd, *args],
                           capture_output=True, text=True, encoding='utf-8', timeout=30)
        return r.stdout.strip() if r.returncode == 0 else ''
    except Exception:
        return ''


def csl_head():
    """Full + short HEAD sha of the csl-orig checkout, or 'unknown'."""
    full = _git('rev-parse', 'HEAD') or 'unknown'
    short = _git('rev-parse', '--short', 'HEAD') or 'unknown'
    return full, short


def file_last_commit(rel_path):
    """(sha, iso-date, subject) of the last commit touching a csl-orig file, or ('','','')."""
    out = _git('log', '-1', '--format=%H%x1f%cI%x1f%s', '--', rel_path)
    if not out:
        return '', '', ''
    parts = out.split('\x1f')
    while len(parts) < 3:
        parts.append('')
    return parts[0], parts[1], parts[2]


# --- layer snapshots --------------------------------------------------------
def cologne_layers(counts=False):
    """Per csl-orig layer: last commit that touched the file (+ optional record/headword
    counts). ``counts`` re-parses all 4 layer files via ``dict_merge.index`` (minutes on
    the large PWG file) — off by default so the monthly snapshot stays cheap; the git
    metadata alone answers "which commit is this layer at?"."""
    out = {}
    for code, role, blurb in dm.LAYERS:
        rel = 'v02/%s/%s.txt' % (code, code)
        sha, date, subj = file_last_commit(rel)
        rec = {
            'role': role,
            'file': rel,
            'last_commit': sha,
            'last_commit_date': date,
            'last_commit_subject': subj,
        }
        if counts:
            idx = dm.index(code)                   # {form_key: [record, ...]} — expensive
            rec['records'] = sum(len(v) for v in idx.values())
            rec['headwords'] = len(idx)
        else:
            rec['records'] = None
            rec['headwords'] = None
        out[code] = rec
    return out


def _nws_scan():
    """One scandir pass over the NWS cache → (card_paths, latest_mtime). scandir caches
    stat on Windows, so the mtime is free — no per-file os.stat (the 168k-file cost)."""
    paths, latest = [], 0.0
    if not os.path.isdir(NWS_DIR):
        return paths, latest
    with os.scandir(NWS_DIR) as it:
        for e in it:
            name = e.name
            if not name.endswith('.json') or name in NWS_CONTROL or name.startswith('_keys_'):
                continue
            paths.append(e.path)
            try:
                m = e.stat().st_mtime
                if m > latest:
                    latest = m
            except OSError:
                pass
    return paths, latest


def _nws_cards():
    return _nws_scan()[0]


def nws_snapshot(counts=False):
    """NWS is scraped, not git: card count, latest-card mtime, and a hash of the cached
    key list (so a re-enumeration that adds/drops keys registers). ``counts`` additionally
    reads every card for the net-new (has_nws_extra) tally — expensive at ~168k files, so
    off by default; ``net_new_cards`` is None when skipped."""
    cards, latest_mtime = _nws_scan()
    extra = None
    if counts:
        extra = 0
        for f in cards:
            try:
                with open(f, 'rb') as fh:
                    if b'"has_nws_extra": true' in fh.read():
                        extra += 1
            except OSError:
                pass
    keys_file = os.path.join(NWS_DIR, '_keys_all.txt')
    keys_sha = 'na'
    if os.path.exists(keys_file):
        with open(keys_file, 'rb') as fh:
            keys_sha = hashlib.sha256(fh.read()).hexdigest()[:16]
    return {
        'source': dm.NWS_LAYER[2],
        'scraped_cards': len(cards),
        'net_new_cards': extra,
        'keys_all_sha': keys_sha,
        'latest_card_at': (datetime.datetime.fromtimestamp(latest_mtime).isoformat(timespec='seconds')
                           if latest_mtime else None),
    }


def build_snapshot(counts=False):
    full, short = csl_head()
    return {
        'schema': 'pwg_ru.layer_versions.v1',
        'at': datetime.datetime.now().isoformat(timespec='seconds'),
        'csl_orig_head': full,
        'csl_orig_head_short': short,
        'cologne': cologne_layers(counts=counts),
        'nws': nws_snapshot(counts=counts),
    }


# --- log I/O ----------------------------------------------------------------
def append_log(record, path=LOG):
    append_jsonl_line(path, record)


def read_log(path=LOG):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


# --- CLI --------------------------------------------------------------------
def cmd_snapshot(args):
    rec = build_snapshot(counts=getattr(args, 'counts', False))
    append_log(rec)
    print('layer_versions: appended snapshot @ %s (csl-orig %s)'
          % (rec['at'], rec['csl_orig_head_short']))
    _print_snapshot(rec)
    return 0


def _print_snapshot(rec):
    print('  csl-orig HEAD: %s' % rec['csl_orig_head_short'])
    for code, info in rec['cologne'].items():
        cnt = ('%6d rec / %5d hw' % (info['records'], info['headwords'])
               if info.get('records') is not None else '(counts skipped)')
        print('    %-6s %-11s last=%s (%s) %s'
              % (code, info['role'], (info['last_commit'] or 'unknown')[:12],
                 (info['last_commit_date'] or '?')[:10], cnt))
    n = rec['nws']
    nn = '%d net-new' % n['net_new_cards'] if n['net_new_cards'] is not None else 'net-new skipped'
    print('    %-6s %-11s %d cards (%s) keys_sha=%s'
          % ('nws', 'external', n['scraped_cards'], nn, n['keys_all_sha']))


def cmd_show(args):
    log = read_log()
    if not log:
        print('layer_versions: no log yet — run `snapshot` first'); return 0
    if args.all:
        for rec in log:
            print('%s  csl-orig %s  nws %d/%d'
                  % (rec['at'], rec.get('csl_orig_head_short', '?'),
                     rec['nws']['net_new_cards'], rec['nws']['scraped_cards']))
        return 0
    rec = log[-1]
    print('=== latest layer-version snapshot (%d logged) ===' % len(log))
    print('  at: %s' % rec['at'])
    _print_snapshot(rec)
    return 0


def selftest():
    import tempfile
    # snapshot shape (uses the real repo indexes — cheap, read-only)
    rec = build_snapshot()
    assert rec['schema'] == 'pwg_ru.layer_versions.v1'
    assert set(rec['cologne']) == {c for c, _, _ in dm.LAYERS}
    for code, info in rec['cologne'].items():
        assert 'last_commit' in info and 'headwords' in info, (code, info)
    assert 'scraped_cards' in rec['nws'] and 'net_new_cards' in rec['nws']
    # append/read round-trip on a temp log
    d = tempfile.mkdtemp()
    p = os.path.join(d, 'log.jsonl')
    append_log({'at': 't1', 'x': 1}, p)
    append_log({'at': 't2', 'x': 2}, p)
    got = read_log(p)
    assert [r['x'] for r in got] == [1, 2], got
    # file_last_commit tolerates a bogus path (empty, no crash)
    assert file_last_commit('v02/__nope__/__nope__.txt') == ('', '', '')
    print('layer_versions selftest OK (csl-orig HEAD %s, %d layers)'
          % (rec['csl_orig_head_short'], len(rec['cologne'])))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    sn = sub.add_parser('snapshot')
    sn.add_argument('--counts', action='store_true',
                    help='also record per-layer record/headword counts (re-parses all '
                         '4 csl-orig files — minutes; off by default)')
    sh = sub.add_parser('show')
    sh.add_argument('--all', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    handler = {'snapshot': cmd_snapshot, 'show': cmd_show}.get(args.cmd)
    if not handler:
        ap.print_help(); return 0
    return handler(args)


if __name__ == '__main__':
    sys.exit(main() or 0)
