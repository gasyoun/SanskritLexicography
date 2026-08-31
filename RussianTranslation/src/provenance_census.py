#!/usr/bin/env python
r"""Read-only provenance census over the pwg_ru store (H3750 / issue #1804, W3).

Answers one question per row: **is this row's provenance stamp a measurement, an
assertion, or absent?**

  measured  the ``provenance.pipeline`` block carries the three content hashes
            (``prompt_sha`` / ``glossary_sha`` / ``script_sha``) that
            ``pipeline_version.stamp()`` computes from the actual component bytes
            at generation time. The row can be tied to the bytes that produced it.
  asserted  the block carries only ``*_version`` strings plus ``backfilled: true``
            -- a version stamped retrospectively by ``pipeline_version.py backfill``
            with nothing behind it. The row states a provenance it never measured.
  absent    the row carries no input identity at all (no ``generated_at``, no
            ``input_raw_sha256``, no ``input_portrait_sha256``): it cannot be
            re-derived or checked against upstream drift.

The census also reconstructs, from git history, what each component's content SHA
*was* at a given moment, and tests that reconstruction against the rows that DO
carry measured hashes. That test is what decides whether a backfill of the asserted
era could ever be evidence-based rather than a second, larger assertion -- see
``--reconstruct``.

This module NEVER writes to the store. It reads, counts, and prints.

  python provenance_census.py                    -> markdown report on stdout
  python provenance_census.py --json             -> machine-readable summary
  python provenance_census.py --reconstruct      -> + the git-reconstruction probe
  python provenance_census.py --store PATH       -> census a specific store file
  python provenance_census.py --selftest
"""
import argparse
import fnmatch
import hashlib
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from store_path import canonical_store  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))          # RussianTranslation/


def _repo_toplevel(start=HERE):
    """This checkout's toplevel -- a linked worktree shares the object store with
    the main checkout, so either resolves the same history."""
    proc = subprocess.run(['git', '-C', start, 'rev-parse', '--show-toplevel'],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          encoding='utf-8', errors='replace')
    if proc.returncode:
        return os.path.normpath(os.path.join(ROOT, '..'))
    return os.path.normpath(proc.stdout.strip())


REPO = _repo_toplevel()
MANIFEST = os.path.join(HERE, 'pipeline_versions.json')
COMPONENTS = ('prompt', 'glossary', 'script')
SHA_FIELDS = tuple('%s_sha' % c for c in COMPONENTS)

MEASURED = 'measured'
ASSERTED = 'asserted'
ABSENT = 'absent'


# --- classification ---------------------------------------------------------
def classify(row):
    """(class, reason) for one store row. Pure; no I/O."""
    prov = row.get('provenance') or {}
    pipe = prov.get('pipeline') or {}
    has_input_identity = bool(prov.get('input_raw_sha256')
                              or prov.get('input_portrait_sha256'))
    if not has_input_identity and not prov.get('generated_at'):
        return ABSENT, 'no generated_at and no input hash'
    present = [f for f in SHA_FIELDS if pipe.get(f)]
    if len(present) == len(SHA_FIELDS):
        return MEASURED, 'prompt/glossary/script content hashes present'
    if not pipe:
        return ASSERTED, 'no pipeline block at all'
    if pipe.get('backfilled') is True:
        return ASSERTED, 'backfilled=true, %d/3 content hashes' % len(present)
    return ASSERTED, 'partial stamp, %d/3 content hashes' % len(present)


def era_of(generated_at):
    """Coarse era bucket: the generation month, or 'undated'."""
    if not generated_at:
        return 'undated'
    return str(generated_at)[:7]


def census(store_path):
    """Walk the store once. Returns the full summary dict."""
    counts = {MEASURED: 0, ASSERTED: 0, ABSENT: 0}
    per_era = {}
    reasons = {}
    stamps = {}          # measured (versions+shas) tuple -> window
    spans = {MEASURED: [None, None], ASSERTED: [None, None]}
    absent_rows = []
    generators = {}
    total = 0

    with open(store_path, encoding='utf-8') as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            total += 1
            row = json.loads(line)
            prov = row.get('provenance') or {}
            pipe = prov.get('pipeline') or {}
            cls, reason = classify(row)
            counts[cls] += 1
            reasons[(cls, reason)] = reasons.get((cls, reason), 0) + 1
            era = era_of(prov.get('generated_at'))
            per_era.setdefault(era, {MEASURED: 0, ASSERTED: 0, ABSENT: 0})
            per_era[era][cls] += 1
            gen = str(prov.get('generator'))
            generators.setdefault(gen, {MEASURED: 0, ASSERTED: 0, ABSENT: 0})
            generators[gen][cls] += 1

            ga = prov.get('generated_at')
            if cls in spans and ga:
                lo, hi = spans[cls]
                spans[cls] = [ga if lo is None else min(lo, ga),
                              ga if hi is None else max(hi, ga)]
            if cls == MEASURED:
                key = tuple(pipe.get(f) for f in
                            ('prompt_version', 'prompt_sha', 'glossary_version',
                             'glossary_sha', 'script_version', 'script_sha'))
                st = stamps.setdefault(key, {'rows': 0, 'first': None, 'last': None,
                                             'roots': set()})
                st['rows'] += 1
                if ga:
                    st['first'] = ga if st['first'] is None else min(st['first'], ga)
                    st['last'] = ga if st['last'] is None else max(st['last'], ga)
                st['roots'].add(prov.get('root'))
            if cls == ABSENT:
                absent_rows.append({'line': lineno, 'key1': row.get('key1'),
                                    'key': row.get('key'),
                                    'generator': prov.get('generator')})

    return {
        'store': store_path,
        'rows': total,
        'counts': counts,
        'share': {k: (round(100.0 * v / total, 2) if total else 0.0)
                  for k, v in counts.items()},
        'per_era': per_era,
        'per_generator': generators,
        'reasons': [{'class': c, 'reason': r, 'rows': n}
                    for (c, r), n in sorted(reasons.items(), key=lambda kv: -kv[1])],
        'spans': spans,
        'stamps': [{'prompt_version': k[0], 'prompt_sha': k[1],
                    'glossary_version': k[2], 'glossary_sha': k[3],
                    'script_version': k[4], 'script_sha': k[5],
                    'rows': v['rows'], 'first': v['first'], 'last': v['last'],
                    'roots': len(v['roots'])}
                   for k, v in sorted(stamps.items(), key=lambda kv: -kv[1]['rows'])],
        'absent_rows': absent_rows,
    }


# --- git reconstruction probe ----------------------------------------------
def _git(*args, **kw):
    proc = subprocess.run(['git', '-C', REPO, *args], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, encoding='utf-8',
                          errors='replace', **kw)
    if proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, proc.args,
                                            output=proc.stdout, stderr=proc.stderr)
    return proc.stdout


def component_patterns(manifest_path=MANIFEST):
    with open(manifest_path, encoding='utf-8') as fh:
        manifest = json.load(fh)
    return {name: manifest['components'][name]['files'] for name in COMPONENTS}


def pattern_scopes(patterns, prefix='RussianTranslation'):
    """The narrowest git pathspecs covering these glob patterns -- so `ls-tree`
    walks the component directories, not the whole RussianTranslation tree."""
    return sorted({'%s/%s' % (prefix, pat.split('*')[0].rstrip('/'))
                   for pat in patterns})


def component_sha_at(commit, patterns, prefix='RussianTranslation', cache=None):
    """The 16-hex component SHA as ``pipeline_version.component_sha`` would have
    computed it against the tree of ``commit``.

    Same recipe: sorted paths relative to RussianTranslation/, each folded in as
    ``relpath \0 bytes \0``. Returns 'na' when the tree matches no file.
    """
    listing = _git('ls-tree', '-r', commit, '--',
                   *pattern_scopes(patterns, prefix))
    entries = []
    for line in listing.splitlines():
        if not line.strip():
            continue
        meta, path = line.split('\t', 1)
        blob_sha = meta.split()[2]
        rel = path[len(prefix) + 1:] if path.startswith(prefix + '/') else path
        if any(fnmatch.fnmatch(rel, pat) for pat in patterns):
            entries.append((rel, blob_sha))
    if not entries:
        return 'na'
    h = hashlib.sha256()
    for rel, blob_sha in sorted(entries):
        content = _blob(blob_sha, cache)
        h.update(rel.encode('utf-8'))
        h.update(b'\0')
        h.update(content)
        h.update(b'\0')
    return h.hexdigest()[:16]


def _blob(blob_sha, cache=None):
    """Blob bytes, memoized on the git object id (content-addressed, so the cache
    can never go stale)."""
    if cache is not None and blob_sha in cache:
        return cache[blob_sha]
    proc = subprocess.run(['git', '-C', REPO, 'cat-file', 'blob', blob_sha],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    content = proc.stdout
    if cache is not None:
        cache[blob_sha] = content
    return content


def commit_series(since, until, patterns_by_component, prefix='RussianTranslation'):
    """[{commit, date, prompt/glossary/script sha}] for every commit in the window
    that touched any component file, newest first. The reconstruction candidate set."""
    paths = set()
    for pats in patterns_by_component.values():
        paths.update(pattern_scopes(pats, prefix))
    log = _git('log', '--format=%H\t%cI', '--since=%s' % since,
               '--until=%s' % until, '--', *sorted(paths))
    cache = {}
    out = []
    for line in log.splitlines():
        if not line.strip():
            continue
        commit, date = line.split('\t')
        entry = {'commit': commit[:8], 'date': date}
        for name, pats in patterns_by_component.items():
            entry['%s_sha' % name] = component_sha_at(commit, pats, prefix, cache)
        out.append(entry)
    return out


def _utc(iso):
    """'2026-07-04T20:36:49Z' / '+03:00' offsets -> comparable UTC string."""
    import datetime as _dt
    if not iso:
        return None
    txt = iso.replace('Z', '+00:00')
    try:
        dt = _dt.datetime.fromisoformat(txt)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return iso
    return dt.astimezone(_dt.timezone.utc).isoformat().replace('+00:00', 'Z')


def reconstruction_probe(summary, since='2026-06-01', until='2026-09-01'):
    """Test the git reconstruction against the rows that carry measured hashes.

    Every measured stamp is a ground truth: at a known instant, the component bytes
    hashed to a known value. If walking git history reproduces those values, the
    same walk can date the asserted era. If it does not, no git-derived backfill of
    that era is evidence -- it is a second assertion.
    """
    patterns = component_patterns()
    series = commit_series(since, until, patterns)
    seen = {name: {e['%s_sha' % name] for e in series} for name in COMPONENTS}
    checks = []
    for stamp in summary['stamps']:
        row = {'first': stamp['first'], 'rows': stamp['rows']}
        # LOOSE test: does the recorded sha occur at ANY commit in the window?
        # This is deliberately generous -- an upper bound on recoverability.
        for name in COMPONENTS:
            sha = stamp['%s_sha' % name]
            row[name] = {'sha': sha, 'reproduced': sha in seen[name]}
        # STRICT test: the commit that was the newest component commit at the
        # moment the row was generated -- what a dated backfill would actually use.
        first_utc = _utc(stamp['first'])
        prior = None
        for e in series:                      # newest first
            if first_utc and (_utc(e['date']) or '') <= first_utc:
                prior = e
                break
        row['strict_commit'] = prior['commit'] if prior else None
        row['strict_match'] = (
            {name: (prior['%s_sha' % name] == stamp['%s_sha' % name])
             for name in COMPONENTS} if prior else None)
        checks.append(row)
    reproduced = sum(1 for c in checks
                     if all(c[n]['reproduced'] for n in COMPONENTS))
    partial = sum(1 for c in checks
                  if any(c[n]['reproduced'] for n in COMPONENTS)) - reproduced
    strict_all = sum(1 for c in checks
                     if c['strict_match'] and all(c['strict_match'].values()))
    strict_any = sum(1 for c in checks
                     if c['strict_match'] and any(c['strict_match'].values()))
    earliest = _git('log', '--format=%cI', '--reverse').splitlines()
    return {
        'window': [since, until],
        'commits_touching_components': len(series),
        'series': series,
        'checks': checks,
        'stamps_total': len(checks),
        'stamps_fully_reproduced': reproduced,
        'stamps_partially_reproduced': partial,
        'stamps_strict_all_three': strict_all,
        'stamps_strict_any': strict_any,
        'shallow': _git('rev-parse', '--is-shallow-repository').strip(),
        'earliest_commit': earliest[0].strip() if earliest else None,
    }


# --- input-identity corroboration ------------------------------------------
def sidecar_index(root=ROOT):
    """basename -> {every input hash the surviving wf_output sidecar records}.

    The workflow sidecars (`wf_output.*.json`, including the pre-cutover ones
    parked in `archive/legacy_runtime_2026-07-04/`) are a SECOND, independent
    record of which source bytes went into each card. They carry no component
    hashes, so they cannot repair an asserted stamp -- but they can confirm the
    half of provenance the asserted era does have.
    """
    index = {}
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if not (name.startswith('wf_output') and name.endswith('.json')):
                continue
            try:
                with open(os.path.join(dirpath, name), encoding='utf-8') as fh:
                    data = json.load(fh)
            except (ValueError, OSError):
                continue
            meta = data.get('meta') if isinstance(data, dict) else None
            hashes = set()
            for entry in ((meta or {}).get('input_hashes') or {}).values():
                if isinstance(entry, dict):
                    for v in entry.values():
                        if isinstance(v, str):
                            hashes.add(v)
            if hashes:
                index.setdefault(name, set()).update(hashes)
    return index


def corroborate(store_path, root=None):
    """Per class: rows whose store input hash is independently confirmed by the
    surviving workflow sidecar named in the row's own ``wf_file``.

    The sidecars are gitignored runtime artifacts that live beside the store they
    describe, so the search root follows the STORE (the main checkout), never this
    module's own worktree -- the H255 lesson in `store_path.py`, applied to the
    sidecar layer.
    """
    root = root or os.path.normpath(os.path.join(os.path.dirname(store_path), '..'))
    index = sidecar_index(root)
    out = {}
    with open(store_path, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            prov = row.get('provenance') or {}
            cls = classify(row)[0]
            slot = out.setdefault(cls, {'rows': 0, 'sidecar_present': 0,
                                        'input_confirmed': 0, 'input_conflict': 0})
            slot['rows'] += 1
            wf = prov.get('wf_file')
            hashes = index.get(wf) if wf else None
            if not hashes:
                continue
            slot['sidecar_present'] += 1
            raw = prov.get('input_raw_sha256')
            if raw is None:
                continue
            if raw in hashes:
                slot['input_confirmed'] += 1
            else:
                slot['input_conflict'] += 1
    return {'sidecars': len(index), 'by_class': out}


# --- rendering --------------------------------------------------------------
def render_markdown(summary, probe=None, corr=None):
    c, s = summary['counts'], summary['share']
    L = []
    L.append('rows: %d' % summary['rows'])
    L.append('')
    L.append('| class | rows | share |')
    L.append('|---|---:|---:|')
    for cls in (MEASURED, ASSERTED, ABSENT):
        L.append('| %s | %d | %.2f %% |' % (cls, c[cls], s[cls]))
    L.append('')
    L.append('| era | measured | asserted | absent |')
    L.append('|---|---:|---:|---:|')
    for era in sorted(summary['per_era']):
        e = summary['per_era'][era]
        L.append('| %s | %d | %d | %d |' % (era, e[MEASURED], e[ASSERTED], e[ABSENT]))
    L.append('')
    L.append('measured span: %s .. %s' % tuple(summary['spans'][MEASURED]))
    L.append('asserted span: %s .. %s' % tuple(summary['spans'][ASSERTED]))
    L.append('')
    L.append('| prompt | glossary | script | rows | first | last |')
    L.append('|---|---|---|---:|---|---|')
    for st in summary['stamps']:
        L.append('| %s/%s | %s/%s | %s/%s | %d | %s | %s |' % (
            st['prompt_version'], st['prompt_sha'], st['glossary_version'],
            st['glossary_sha'], st['script_version'], st['script_sha'],
            st['rows'], st['first'], st['last']))
    if probe:
        L.append('')
        L.append('reconstruction: loose %d/%d, strict %d/%d measured stamps '
                 'reproduced from %d commits (earliest commit %s, shallow=%s)' % (
                     probe['stamps_fully_reproduced'], probe['stamps_total'],
                     probe['stamps_strict_all_three'], probe['stamps_total'],
                     probe['commits_touching_components'],
                     probe['earliest_commit'], probe['shallow']))
    if corr:
        L.append('')
        L.append('| class | rows | sidecar present | input confirmed | conflict |')
        L.append('|---|---:|---:|---:|---:|')
        for cls, d in sorted(corr['by_class'].items()):
            L.append('| %s | %d | %d | %d | %d |' % (
                cls, d['rows'], d['sidecar_present'], d['input_confirmed'],
                d['input_conflict']))
    return '\n'.join(L)


# --- selftest ---------------------------------------------------------------
def selftest():
    measured = {'provenance': {'generated_at': '2026-08-01T00:00:00Z',
                               'input_raw_sha256': 'a' * 64,
                               'pipeline': {'prompt_sha': 'p', 'glossary_sha': 'g',
                                            'script_sha': 's'}}}
    asserted = {'provenance': {'generated_at': '2026-06-30T00:00:00Z',
                               'input_raw_sha256': 'b' * 64,
                               'pipeline': {'backfilled': True,
                                            'prompt_version': '1.0.0'}}}
    absent = {'provenance': {'generated_at': None, 'input_raw_sha256': None,
                             'input_portrait_sha256': None, 'pipeline': {
                                 'backfilled': True}}}
    partial = {'provenance': {'generated_at': '2026-07-01T00:00:00Z',
                              'input_raw_sha256': 'c' * 64,
                              'pipeline': {'prompt_sha': 'p'}}}
    assert classify(measured)[0] == MEASURED
    assert classify(asserted)[0] == ASSERTED
    assert classify(absent)[0] == ABSENT, classify(absent)
    assert classify(partial)[0] == ASSERTED, 'a partial stamp is not a measurement'
    assert era_of('2026-06-29T11:40:48Z') == '2026-06'
    assert era_of(None) == 'undated'
    # a row with input identity but no timestamp is still classifiable, not absent
    no_date = {'provenance': {'generated_at': None, 'input_raw_sha256': 'd' * 64,
                              'pipeline': {'prompt_sha': 'p', 'glossary_sha': 'g',
                                           'script_sha': 's'}}}
    assert classify(no_date)[0] == MEASURED
    print('provenance_census selftest: OK')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--store', default=None,
                    help='store path (default: the canonical pwg_ru store)')
    ap.add_argument('--json', action='store_true', help='machine-readable summary')
    ap.add_argument('--reconstruct', action='store_true',
                    help='run the git-reconstruction probe against measured stamps')
    ap.add_argument('--corroborate', action='store_true',
                    help='check store input hashes against the wf_output sidecars')
    ap.add_argument('--since', default='2026-06-01')
    ap.add_argument('--until', default='2026-09-01')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    store = args.store or canonical_store(
        os.path.join(HERE, 'pwg_ru_translated.jsonl'))
    if not os.path.isfile(store):
        print('store not found: %s' % store, file=sys.stderr)
        return 2
    summary = census(store)
    probe = (reconstruction_probe(summary, args.since, args.until)
             if args.reconstruct else None)
    corr = corroborate(store) if args.corroborate else None
    if args.json:
        out = dict(summary)
        out['absent_rows'] = summary['absent_rows'][:50]
        if probe:
            out['reconstruction'] = probe
        if corr:
            out['corroboration'] = corr
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(summary, probe, corr))
    return 0


if __name__ == '__main__':
    sys.exit(main())
