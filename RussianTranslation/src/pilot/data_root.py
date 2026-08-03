#!/usr/bin/env python
"""--data-root resolver: map one pwg-ru-data checkout onto the pipeline's env seams.

H2175 step 4 (nonstop multilane wave 1). The pipeline already resolves every data
surface through independent, env-overridable seams (store_path.py `$PWG_RU_STORE` /
`$PWG_RU_TM_DIR`, coordinator.py `$PWG_COORDINATOR_DIR` / `$PWG_INPUT_DIR`,
audit_window.py / window_reports.py `$PWG_OUTPUT_DIR`, economy_ledger.py
`$PWG_ECONOMY_LOG`). `--data-root <dir>` is a thin shim over those seams — it sets
the env vars to the standard gasyoun/pwg-ru-data layout and changes NO resolver:
with the flag absent everything resolves exactly as before (the wave-1 "default =
current local layout, so nothing breaks" contract).

Standard pwg-ru-data layout (ARCHITECTURE_RussianTranslation_pwg_nonstop_multilane.md):

    <root>/
    ├─ layers/     PW SCH PWKVN NWS German dictionary layers
    ├─ tm/         translation-memory store + sidecars (promoter-only writes)
    ├─ manifests/  per-window manifest-v2 + plans (+ coordinator state under
    │              manifests/coordinator/)
    ├─ raws/       card raw inputs (window input portraits)
    ├─ telemetry/  per-call usage ledger rows, economy probe log
    ├─ gatelogs/   live-gate + canary receipts, audit reports, window status
    └─ parked/     park-and-skip queue (R4.2)

Precedence: an explicit `--data-root` WINS over ambient env (a flag visible in the
command line beats inherited shell state), but `apply()` never overrides a value the
caller passed explicitly as its own CLI flag (--coord-dir etc. — the caller decides
that; see bounded_staged_run.main()).
"""
import os
import sys

# Imported by pipeline modules (bounded_staged_run/coordinator/headless_worker),
# sometimes under a captured/StringIO stdout — guard, don't crash the importer.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, 'reconfigure'):
        _stream.reconfigure(encoding='utf-8')

# env var -> path relative to the data root (joined with os.path.join, '/'-split)
ENV_LAYOUT = {
    'PWG_RU_STORE': 'tm/pwg_ru_translated.jsonl',
    'PWG_RU_TM_DIR': 'tm',
    'PWG_INPUT_DIR': 'raws',
    'PWG_OUTPUT_DIR': 'gatelogs',
    'PWG_ECONOMY_LOG': 'telemetry/generation_api_probe_log.jsonl',
    'PWG_COORDINATOR_DIR': 'manifests/coordinator',
    'PWG_PARKED_DIR': 'parked',
}

# directories a lane is allowed to create on first use (never the store file itself:
# an absent store at a claimed root is a wiring error, not a bootstrap case)
SUBDIRS = ('layers', 'tm', 'manifests', 'raws', 'telemetry', 'gatelogs', 'parked')

# non-env conveniences resolved for callers that take paths, not env
REL = {
    'coord_dir': 'manifests/coordinator',
    'manifests_dir': 'manifests',
    'telemetry_dir': 'telemetry',
    'gatelogs_dir': 'gatelogs',
    'parked_dir': 'parked',
    'layers_dir': 'layers',
}


def _join(root, rel):
    return os.path.join(os.path.abspath(root), *rel.split('/'))


def resolve(root, key):
    """Absolute path of a REL/ENV_LAYOUT entry under `root`."""
    rel = REL.get(key) or ENV_LAYOUT.get(key)
    if not rel:
        raise KeyError('data_root.resolve: unknown key %r' % key)
    return _join(root, rel)


def apply(root, env=None, ensure_dirs=False):
    """Set the pipeline env seams for `root`. Returns the dict of values set.

    An explicit data root OVERRIDES ambient env values — the operator wrote the flag
    in this command line; stale shell exports must not silently win over it.
    """
    if env is None:
        env = os.environ
    if not os.path.isdir(root):
        raise SystemExit('data_root: --data-root %s is not a directory' % root)
    if ensure_dirs:
        for sub in SUBDIRS:
            os.makedirs(_join(root, sub), exist_ok=True)
    values = {var: _join(root, rel) for var, rel in ENV_LAYOUT.items()}
    env.update(values)
    return values


def add_arg(ap):
    """Attach the shared --data-root argument to an argparse parser."""
    ap.add_argument('--data-root', default=None,
                    help='pwg-ru-data checkout root (H2175). Maps the standard layout '
                         'onto the PWG_RU_STORE / PWG_RU_TM_DIR / PWG_INPUT_DIR / '
                         'PWG_OUTPUT_DIR / PWG_ECONOMY_LOG env seams before any path '
                         'resolution. Absent = current local layout, unchanged.')
    return ap


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        env = {}
        # 1. apply() maps the documented layout and returns what it set
        got = apply(d, env=env, ensure_dirs=True)
        assert env['PWG_RU_STORE'] == os.path.join(
            os.path.abspath(d), 'tm', 'pwg_ru_translated.jsonl'), env['PWG_RU_STORE']
        assert env['PWG_RU_TM_DIR'] == os.path.join(os.path.abspath(d), 'tm')
        assert env['PWG_INPUT_DIR'] == os.path.join(os.path.abspath(d), 'raws')
        assert env['PWG_OUTPUT_DIR'] == os.path.join(os.path.abspath(d), 'gatelogs')
        assert set(got) == set(ENV_LAYOUT), got
        # 2. ensure_dirs creates the standard skeleton, including parked/
        for sub in SUBDIRS:
            assert os.path.isdir(os.path.join(d, sub)), sub
        # 3. an explicit data root overrides ambient env (flag beats stale export)
        env2 = {'PWG_RU_STORE': 'stale-export.jsonl'}
        apply(d, env=env2)
        assert env2['PWG_RU_STORE'].endswith('pwg_ru_translated.jsonl'), env2
        # 4. resolve() covers both tables; unknown key raises
        assert resolve(d, 'coord_dir') == os.path.join(
            os.path.abspath(d), 'manifests', 'coordinator')
        assert resolve(d, 'PWG_RU_TM_DIR') == os.path.join(os.path.abspath(d), 'tm')
        try:
            resolve(d, 'nope')
            raise AssertionError('unknown key must raise')
        except KeyError:
            pass
    # 5. a non-directory root fails loudly, not by silently resolving nothing
    try:
        apply(os.path.join('definitely', 'absent', 'root'), env={})
        raise AssertionError('absent root must SystemExit')
    except SystemExit:
        pass
    print('data_root selftest: PASS (layout mapping, skeleton dirs, flag-beats-env, '
          'absent-root refusal)')
    return True


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--resolve', metavar='ROOT',
                    help='print the env mapping for a root without applying it')
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.resolve:
        import json
        print(json.dumps({var: _join(a.resolve, rel) for var, rel in ENV_LAYOUT.items()},
                         ensure_ascii=False, indent=1))
    else:
        ap.print_help()
