#!/usr/bin/env python
"""pwg_ru pipeline versioning — stamp WHICH tooling produced a translation.

Orthogonal to the Claude model version (``provenance.model_version``) and to the
project CHANGELOG release. Each translation records the semver of three
output-affecting component families, declared in ``pipeline_versions.json``:

  prompt   — pwg_ru_prompts/  (translate / judge / corpus-check prompts)
  glossary — glossaries/      (domain vocab + de-ru translation aids)
  script   — src/ deterministic mask / harvest / gate / promotion code

Semver by re-run impact, per component:
  MAJOR  breaking output change → rows below this MUST be re-translated
  MINOR  quality improvement    → re-run recommended
  PATCH  cosmetic               → no re-run needed

The manifest records the content SHA each version was frozen at. ``check`` warns
when files changed but the version was not bumped (forgotten-bump guard), and
``freeze`` records the current SHA after you deliberately bump a version.
``stale`` lists store rows whose stamped version is below a component's
``min_valid`` re-run threshold (rows with no pipeline stamp count as stale).

  python pipeline_version.py show          → current versions + SHA drift
  python pipeline_version.py check          → exit 1 if any component drifted
  python pipeline_version.py freeze          → record current SHAs into manifest
  python pipeline_version.py stale --store X → rows needing re-translation
  python pipeline_version.py stamp-md DIR    → refresh .md footers from the store
  python pipeline_version.py backfill --prompt V --glossary V --script V
                                             → stamp legacy unversioned rows (asserted, not guessed)
  python pipeline_version.py --selftest
"""
import argparse
import glob
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
MANIFEST = os.path.join(HERE, 'pipeline_versions.json')
PIPELINE_SCHEMA = 'pwg_ru.pipeline.v1'
COMPONENTS = ('prompt', 'glossary', 'script')


# --- semver -----------------------------------------------------------------
def parse_semver(v):
    """'3.2.1' -> (3, 2, 1). Tolerant of missing parts; non-numeric -> (0,0,0)."""
    if not v:
        return (0, 0, 0)
    parts = str(v).split('.')
    out = []
    for i in range(3):
        try:
            out.append(int(parts[i]))
        except (IndexError, ValueError):
            out.append(0)
    return tuple(out)


def semver_lt(a, b):
    return parse_semver(a) < parse_semver(b)


# --- manifest + hashing -----------------------------------------------------
def load_manifest(path=MANIFEST):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_manifest(manifest, path=MANIFEST):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write('\n')
    os.replace(tmp, path)


def component_files(patterns, root=ROOT):
    """Sorted absolute paths matched by the component's glob patterns."""
    files = set()
    for pat in patterns:
        files.update(glob.glob(os.path.join(root, pat)))
    return sorted(f for f in files if os.path.isfile(f))


def component_sha(patterns, root=ROOT):
    """16-hex content hash over the component's file SET.

    Relative path is folded in before content so a rename/add/remove registers
    even when total bytes are unchanged. Matches the 16-hex convention already
    used by run_batch._prompt_set_sha. Returns 'na' when no files match.
    """
    files = component_files(patterns, root)
    if not files:
        return 'na'
    h = hashlib.sha256()
    for f in files:
        rel = os.path.relpath(f, root).replace('\\', '/')
        h.update(rel.encode('utf-8'))
        h.update(b'\0')
        with open(f, 'rb') as fh:
            h.update(fh.read())
        h.update(b'\0')
    return h.hexdigest()[:16]


def stamp(manifest=None, model_version=None, root=ROOT):
    """Build the ``provenance.pipeline`` dict to embed in a translated row.

    Flat keys per component (``<name>_version`` / ``<name>_sha``) plus an echoed
    ``model_version`` for convenience; the canonical model id still lives in
    ``provenance.model_version``.
    """
    manifest = manifest or load_manifest()
    out = {'schema': PIPELINE_SCHEMA}
    for name in COMPONENTS:
        comp = manifest['components'][name]
        out['%s_version' % name] = comp['version']
        out['%s_sha' % name] = component_sha(comp['files'], root)
    if model_version:
        out['model_version'] = model_version
    return out


def check(manifest=None, root=ROOT):
    """Return the list of drifted components: files changed since the SHA was
    frozen but the version was not bumped. Unfrozen (sha=null) components never
    drift — freeze them once to arm the guard."""
    manifest = manifest or load_manifest()
    drifts = []
    for name in COMPONENTS:
        comp = manifest['components'][name]
        recorded = comp.get('sha')
        current = component_sha(comp['files'], root)
        if recorded and recorded != current:
            drifts.append({'component': name, 'version': comp['version'],
                           'recorded_sha': recorded, 'current_sha': current})
    return drifts


def freeze(manifest=None, root=ROOT):
    """Record each component's current content SHA into the manifest. Call after
    a deliberate version bump so the drift guard tracks the new baseline."""
    manifest = manifest or load_manifest()
    changed = []
    for name in COMPONENTS:
        comp = manifest['components'][name]
        cur = component_sha(comp['files'], root)
        if comp.get('sha') != cur:
            changed.append((name, comp.get('sha'), cur))
            comp['sha'] = cur
    return manifest, changed


# --- staleness (re-run targeting) -------------------------------------------
def row_pipeline(row):
    prov = row.get('provenance') or {}
    return prov.get('pipeline') or {}


def stale_reasons(pipeline, manifest):
    """Components whose STAMPED version is below min_valid → the row needs re-run.

    A row with no pipeline stamp at all (legacy, pre-versioning) is 'unversioned',
    NOT stale: we return [] so a deploy does not flag every historical row. Handle
    unversioned rows via the separate missing-stamp count. A row that carries a
    stamp but is missing one component key is treated as below-threshold for it."""
    if not pipeline:
        return []
    reasons = []
    for name in COMPONENTS:
        comp = manifest['components'][name]
        min_valid = comp.get('min_valid') or '0.0.0'
        stamped = pipeline.get('%s_version' % name)
        if stamped is None or semver_lt(stamped, min_valid):
            reasons.append('%s<%s (have %s)' % (name, min_valid, stamped or 'none'))
    return reasons


def iter_store(path):
    with open(path, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if line:
                yield lineno, json.loads(line)


def find_stale(store_path, manifest=None):
    manifest = manifest or load_manifest()
    stale = []
    total = unversioned = 0
    for lineno, row in iter_store(store_path):
        total += 1
        pipeline = row_pipeline(row)
        if not pipeline:
            unversioned += 1
            continue
        reasons = stale_reasons(pipeline, manifest)
        if reasons:
            stale.append((lineno, row.get('key1'), row.get('ord'), reasons))
    return total, stale, unversioned


# --- markdown footer --------------------------------------------------------
def md_footer(pipeline, model_version=None, generated_at=None):
    """One-line provenance footer for a rendered .md card."""
    model = model_version or pipeline.get('model_version') or 'unknown-model'
    bits = 'pipeline prompt v%s · glossary v%s · script v%s' % (
        pipeline.get('prompt_version', '?'),
        pipeline.get('glossary_version', '?'),
        pipeline.get('script_version', '?'))
    tail = ' · %s' % generated_at if generated_at else ''
    return '_%s · %s%s_' % (bits, model, tail)


FOOTER_MARK = '_pipeline prompt v'


def apply_md_footer(md_path, pipeline, model_version=None, generated_at=None):
    """Append or refresh the pipeline footer at the end of a card .md. Idempotent:
    an existing footer line is replaced, not duplicated. Returns True if written."""
    with open(md_path, encoding='utf-8') as f:
        text = f.read()
    footer = md_footer(pipeline, model_version, generated_at)
    lines = text.rstrip('\n').split('\n')
    while lines and lines[-1].strip() == '':
        lines.pop()
    if lines and lines[-1].startswith(FOOTER_MARK):
        if lines[-1] == footer:
            return False
        lines[-1] = footer
    else:
        lines.append('')
        lines.append(footer)
    new = '\n'.join(lines) + '\n'
    if new == text:
        return False
    tmp = md_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new)
    os.replace(tmp, md_path)
    return True


# --- CLI --------------------------------------------------------------------
def cmd_show(_args):
    manifest = load_manifest()
    drifts = {d['component']: d for d in check(manifest)}
    print('=== pwg_ru pipeline versions ===')
    for name in COMPONENTS:
        comp = manifest['components'][name]
        cur = component_sha(comp['files'], ROOT)
        state = 'DRIFT (files changed, version NOT bumped)' if name in drifts \
            else ('unfrozen' if not comp.get('sha') else 'ok')
        print('  %-9s v%-8s min_valid=%-8s sha=%s  [%s]'
              % (name, comp['version'], comp.get('min_valid'), cur, state))
    if drifts:
        print('\nWARNING: %d component(s) drifted — bump the version and run '
              '`freeze`, or `freeze` to accept as-is:' % len(drifts))
        for d in drifts.values():
            print('  %s: recorded %s → now %s'
                  % (d['component'], d['recorded_sha'], d['current_sha']))


def cmd_check(_args):
    drifts = check()
    if not drifts:
        print('pipeline_version: no drift'); return 0
    for d in drifts:
        print('DRIFT %s v%s: recorded %s → now %s'
              % (d['component'], d['version'], d['recorded_sha'], d['current_sha']))
    print('\nBump the changed component(s) in pipeline_versions.json, then `freeze`.')
    return 1


def cmd_freeze(_args):
    manifest, changed = freeze()
    if not changed:
        print('pipeline_version: already frozen at current content'); return 0
    save_manifest(manifest)
    for name, old, new in changed:
        print('froze %s: %s → %s' % (name, old or 'null', new))
    return 0


def cmd_stale(args):
    store = args.store
    if not os.path.exists(store):
        sys.exit('no store %r' % store)
    total, stale, unversioned = find_stale(store)
    print('store rows: %d | stale (stamped below min_valid → re-translate): %d '
          '| unversioned legacy (no stamp): %d' % (total, len(stale), unversioned))
    for lineno, key1, ord_, reasons in stale[:30]:
        print('  line=%s ord=%s key1=%s  %s' % (lineno, ord_, key1, '; '.join(reasons)))
    if len(stale) > 30:
        print('  ... %d more' % (len(stale) - 30))
    return 0


def cmd_stamp_md(args):
    """Refresh .md footers from the authoritative store. Matches card files by
    <key1>.merged.md (and <key1>.md) in the given dir(s)."""
    manifest = load_manifest()
    store = args.store
    if not os.path.exists(store):
        sys.exit('no store %r' % store)
    prov_by_key = {}
    for _ln, row in iter_store(store):
        key1 = row.get('key1')
        if not key1:
            continue
        prov = row.get('provenance') or {}
        pipeline = prov.get('pipeline')
        if pipeline and key1 not in prov_by_key:
            prov_by_key[key1] = (pipeline, prov.get('model_version'),
                                 prov.get('generated_at'))
    written = 0
    for d in args.dirs:
        for md in glob.glob(os.path.join(d, '*.md')):
            base = os.path.basename(md)
            key1 = base[:-len('.merged.md')] if base.endswith('.merged.md') \
                else base[:-len('.md')]
            hit = prov_by_key.get(key1)
            if not hit:
                continue
            if apply_md_footer(md, hit[0], hit[1], hit[2]):
                written += 1
    print('stamp-md: refreshed footer on %d card(s)' % written)
    return 0


def backfill_store(store_path, versions, manifest=None):
    """Stamp unversioned legacy rows with EXPLICITLY-ASSERTED component versions,
    marked ``backfilled: true``. Never guesses: the caller states which tooling
    version produced these rows. Rows that already carry a pipeline stamp are left
    untouched. Returns (changed, rows)."""
    manifest = manifest or load_manifest()
    rows, changed = [], 0
    for _ln, row in iter_store(store_path):
        prov = row.get('provenance')
        if isinstance(prov, dict) and not prov.get('pipeline'):
            pl = {'schema': PIPELINE_SCHEMA, 'backfilled': True}
            for name in COMPONENTS:
                pl['%s_version' % name] = versions[name]
            if prov.get('model_version'):
                pl['model_version'] = prov['model_version']
            prov['pipeline'] = pl
            changed += 1
        rows.append(row)
    return changed, rows


def cmd_backfill(args):
    versions = {'prompt': args.prompt, 'glossary': args.glossary, 'script': args.script}
    if not all(versions.values()):
        sys.exit('backfill requires --prompt, --glossary and --script versions '
                 '(no guessing — assert the tooling version these legacy rows were made with)')
    if not os.path.exists(args.store):
        sys.exit('no store %r' % args.store)
    changed, rows = backfill_store(args.store, versions)
    if not changed:
        print('backfill: no unversioned rows to stamp'); return 0
    if args.dry_run:
        print('backfill: would stamp %d unversioned row(s) with prompt=%s glossary=%s script=%s'
              % (changed, versions['prompt'], versions['glossary'], versions['script']))
        return 0
    import shutil, datetime
    backup = args.store + '.backup.' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    shutil.copy2(args.store, backup)
    tmp = args.store + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    os.replace(tmp, args.store)
    print('backfill: stamped %d row(s) (backfilled=true) → %s; backup: %s'
          % (changed, os.path.basename(args.store), os.path.basename(backup)))
    return 0


def selftest():
    import tempfile
    d = tempfile.mkdtemp()
    # fake repo with one file per component
    os.makedirs(os.path.join(d, 'pwg_ru_prompts'))
    os.makedirs(os.path.join(d, 'glossaries'))
    os.makedirs(os.path.join(d, 'src'))
    open(os.path.join(d, 'pwg_ru_prompts', '1.txt'), 'w').write('p')
    open(os.path.join(d, 'glossaries', 'g.tsv'), 'w').write('g')
    open(os.path.join(d, 'src', 's.py'), 'w').write('s')
    manifest = {
        'components': {
            'prompt': {'version': '1.2.0', 'min_valid': '1.0.0', 'sha': None,
                       'files': ['pwg_ru_prompts/*.txt']},
            'glossary': {'version': '1.0.0', 'min_valid': '1.0.0', 'sha': None,
                         'files': ['glossaries/*.tsv']},
            'script': {'version': '2.0.0', 'min_valid': '2.0.0', 'sha': None,
                       'files': ['src/s.py']},
        }
    }
    # semver
    assert parse_semver('3.2.1') == (3, 2, 1)
    assert semver_lt('1.0.0', '1.0.1') and not semver_lt('2.0.0', '1.9.9')
    # stamp
    st = stamp(manifest, model_version='claude-sonnet-5', root=d)
    assert st['prompt_version'] == '1.2.0' and st['script_version'] == '2.0.0'
    assert st['model_version'] == 'claude-sonnet-5'
    assert len(st['prompt_sha']) == 16
    # no drift while unfrozen
    assert check(manifest, root=d) == []
    # freeze, then edit a file → drift on exactly that component
    frozen, changed = freeze(manifest, root=d)
    assert len(changed) == 3 and check(frozen, root=d) == []
    open(os.path.join(d, 'pwg_ru_prompts', '1.txt'), 'w').write('p-EDITED')
    drifts = check(frozen, root=d)
    assert len(drifts) == 1 and drifts[0]['component'] == 'prompt', drifts
    # staleness: a row below min_valid and a fresh row
    stale = stale_reasons({'prompt_version': '0.9.0', 'glossary_version': '1.0.0',
                           'script_version': '2.0.0'}, frozen)
    assert stale == ['prompt<1.0.0 (have 0.9.0)'], stale
    assert stale_reasons({}, frozen) == []  # unversioned legacy row is NOT stale
    # a stamp missing one component key IS below-threshold for that component
    assert stale_reasons({'prompt_version': '1.2.0', 'glossary_version': '1.0.0'},
                         frozen) == ['script<2.0.0 (have none)']
    fresh = stale_reasons({'prompt_version': '1.2.0', 'glossary_version': '1.0.0',
                           'script_version': '2.0.0'}, frozen)
    assert fresh == [], fresh
    # md footer idempotence
    card = os.path.join(d, 'agni.merged.md')
    open(card, 'w', encoding='utf-8').write('# agni\n\nbody\n')
    assert apply_md_footer(card, st, 'claude-sonnet-5', '2026-07-04T00:00:00')
    assert not apply_md_footer(card, st, 'claude-sonnet-5', '2026-07-04T00:00:00')
    body = open(card, encoding='utf-8').read()
    assert body.count(FOOTER_MARK) == 1, 'footer must not duplicate'
    # backfill: unversioned row gets a backfilled stamp; already-stamped row untouched
    store = os.path.join(d, 'store.jsonl')
    with open(store, 'w', encoding='utf-8') as f:
        f.write(json.dumps({'key1': 'a', 'provenance': {'model_version': 'm'}}) + '\n')
        f.write(json.dumps({'key1': 'b', 'provenance': {'pipeline': {'prompt_version': '1.0.0'}}}) + '\n')
    n, rows = backfill_store(store, {'prompt': '1.0.0', 'glossary': '1.0.0', 'script': '1.0.0'}, frozen)
    assert n == 1, n
    assert rows[0]['provenance']['pipeline']['backfilled'] is True
    assert rows[0]['provenance']['pipeline']['prompt_version'] == '1.0.0'
    assert 'backfilled' not in rows[1]['provenance']['pipeline']  # pre-stamped untouched
    print('pipeline_version selftest OK')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    sub.add_parser('show')
    sub.add_parser('check')
    sub.add_parser('freeze')
    sp = sub.add_parser('stale')
    sp.add_argument('--store', default=os.path.join(HERE, 'pwg_ru_translated.jsonl'))
    sm = sub.add_parser('stamp-md')
    sm.add_argument('dirs', nargs='+')
    sm.add_argument('--store', default=os.path.join(HERE, 'pwg_ru_translated.jsonl'))
    bf = sub.add_parser('backfill')
    bf.add_argument('--store', default=os.path.join(HERE, 'pwg_ru_translated.jsonl'))
    bf.add_argument('--prompt'); bf.add_argument('--glossary'); bf.add_argument('--script')
    bf.add_argument('--dry-run', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    handler = {'show': cmd_show, 'check': cmd_check, 'freeze': cmd_freeze,
               'stale': cmd_stale, 'stamp-md': cmd_stamp_md,
               'backfill': cmd_backfill}.get(args.cmd)
    if not handler:
        ap.print_help(); return 0
    return handler(args)


if __name__ == '__main__':
    sys.exit(main() or 0)
