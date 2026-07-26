#!/usr/bin/env python
"""Make a selftest's isolation from production data EXPLICIT, instead of incidental.

WHY THIS EXISTS
---------------
Three defects in two days, all the same shape -- a test reached production data because
the thing keeping it away was never anybody's job:

* #726 -- `window_selftest`'s coordinator-requeue case ran a real `--defect` requeue
  without `--no-residual`, appending a junk row to the tracked `no_pwg_residuals.jsonl`
  (the registry that decides which keys are BLOCKED from requeue) on EVERY suite run.
* #729 -- the c4 gate probe read an append-only log by a constant `RUN_ID`, so it could
  pair its own warm-up with a stale `measured` from days earlier.
* the live-store exposure -- `coordinator.promote_ready` moved from shelling out to
  `--batch-manifest` to calling `promote_final_cards.batch_promote` IN-PROCESS. The
  fixtures' isolation *was* that subprocess boundary (they stub `run_cmd`), and
  `DEFAULT_STORE` resolves via `store_path.canonical_store` to the MAIN WORKTREE's real
  `pwg_ru_translated.jsonl` unless `PWG_RU_STORE` is set -- which no selftest set. The
  promotion tests read the live ~11.6k-row store and, on a fixture whose sense identities
  did not happen to collide with real rows, would have WRITTEN it.

In each case isolation rode on something incidental: a subprocess boundary, a default
filename, an env var nobody owned. Remove the incidental thing and the test silently
starts touching production.

THE TWO HALVES
--------------
`isolate()` -- **belt.** Point every redirectable production path at a scratch directory
BEFORE the modules that read them are imported (several resolve their constants at import
time). Refuse outright if a caller has already pointed one INSIDE the repo.

`tripwire()` / `verify_tripwire()` -- **braces.** Hash the production paths that have NO
override (the residual ledger is the live example -- its path is computed from `__file__`)
and re-check them at exit. This is what catches the next instance of this class, including
one nobody predicted: it does not care WHY a file changed, only that it did.

Belt alone would not have caught #726 (no override to set). Braces alone would report the
damage after it happened. Together, the common case is prevented and the unknown case is
caught loudly, in the run that caused it.

USAGE
-----
At the very top of a selftest, before importing repo modules::

    from selftest_isolation import guard
    guard()

`guard()` does both halves and registers the exit check. `PWG_SELFTEST_ALLOW_PRODUCTION=1`
disables it -- for the deliberate case only, and it says so on stderr.
"""
import atexit
import hashlib
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)              # .../RussianTranslation
TOPLEVEL = os.path.dirname(REPO)         # the checkout root

ESCAPE_HATCH = 'PWG_SELFTEST_ALLOW_PRODUCTION'

# Redirectable production paths: env var -> ('file'|'dir', scratch basename).
# Each is resolved by its module at IMPORT time, so `isolate()` must run first.
REDIRECTABLE = (
    ('PWG_RU_STORE', 'file', 'store.jsonl'),          # the canonical translated store
    ('PWG_COORDINATOR_DIR', 'dir', 'coordinator'),    # lease state, artifacts, locks
    ('PWG_RU_TM_DIR', 'dir', 'tm'),                   # TM caches + denylist sidecars
    ('PWG_EVENTS_PATH', 'file', 'events.jsonl'),      # append-only run telemetry
)

# Production paths with NO override, relative to RussianTranslation/. These cannot be
# redirected, so they are watched instead. Add to this list rather than hoping.
WATCHED = (
    'src/pilot/no_pwg_residuals.jsonl',               # C-49 residual registry (#726)
    'src/pilot/RUN_LOG.md',
    'src/pilot/GENERATION_API_PROBE_LOG.md',
    'RESULTS_LOG.md',
)


def _digest(path):
    """A content digest, or None when the file is absent (absence is itself a state)."""
    try:
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def _inside_repo(path):
    try:
        return os.path.commonpath([os.path.abspath(path), TOPLEVEL]) == TOPLEVEL
    except ValueError:                                # different drive on Windows
        return False


def disabled():
    return os.environ.get(ESCAPE_HATCH) == '1'


def isolate(scratch_root=None):
    """Point every redirectable production path at scratch. Returns {env: path}.

    A value already set OUTSIDE the repo is left alone -- the caller has isolated it their
    own way. A value already set INSIDE the repo is a hard refusal: that is the failure
    mode this module exists to prevent, and silently overriding it would hide a real
    mistake in the caller.
    """
    root = scratch_root or os.path.join(tempfile.gettempdir(), 'pwg_selftest_scratch')
    os.makedirs(root, exist_ok=True)
    pinned = {}
    for env, kind, basename in REDIRECTABLE:
        current = os.environ.get(env)
        if current:
            if _inside_repo(current):
                raise SystemExit(
                    'selftest isolation: %s points INSIDE the checkout (%s). A selftest must '
                    'never read or write production data; set it to a scratch path, or set '
                    '%s=1 if this is deliberate.' % (env, current, ESCAPE_HATCH))
            pinned[env] = current
            continue
        target = os.path.join(root, basename)
        if kind == 'dir':
            os.makedirs(target, exist_ok=True)
        elif not os.path.exists(target):
            # A MISSING store is itself refused downstream ("a missing/misresolved
            # production store must not disappear silently"), so the stand-in must exist.
            open(target, 'a', encoding='utf-8').close()
        os.environ[env] = target
        pinned[env] = target
    return pinned


def tripwire():
    """Digest every watched production path. Feed the result to `verify_tripwire`."""
    return {rel: _digest(os.path.join(REPO, rel)) for rel in WATCHED}


def verify_tripwire(before, on_violation=None):
    """Re-digest and report any watched path the run changed. Returns the changed list."""
    changed = []
    for rel, was in sorted(before.items()):
        now = _digest(os.path.join(REPO, rel))
        if now != was:
            changed.append(rel)
    if changed and on_violation:
        on_violation(changed)
    return changed


def _report(changed):
    sys.stderr.write(
        '\nSELFTEST ISOLATION VIOLATION: this run modified %d tracked production file(s):\n'
        % len(changed))
    for rel in changed:
        sys.stderr.write('  - %s\n' % rel)
    sys.stderr.write(
        'A selftest must not touch production data. Either redirect the write (add an env '
        'override + an entry in selftest_isolation.REDIRECTABLE) or stub it in the fixture. '
        'See issues #726 / #729 for what this class costs when it goes unnoticed.\n')


def guard(scratch_root=None):
    """Isolate, then arm the exit tripwire. The one call a selftest needs."""
    if disabled():
        sys.stderr.write('selftest isolation: DISABLED via %s=1 — production data is reachable\n'
                         % ESCAPE_HATCH)
        return {}
    pinned = isolate(scratch_root)
    before = tripwire()

    def _check():
        changed = verify_tripwire(before, _report)
        if changed:
            # Exit non-zero even if every assertion passed: a green suite that corrupted the
            # residual registry is not a passing run.
            os._exit(9)

    atexit.register(_check)
    return pinned


# ---------------------------------------------------------------------------
def selftest():
    """Fail-loud, no I/O outside a temp dir."""
    import shutil
    d = tempfile.mkdtemp()
    saved = {env: os.environ.get(env) for env, _k, _b in REDIRECTABLE}
    try:
        for env, _k, _b in REDIRECTABLE:
            os.environ.pop(env, None)

        # 1. every redirectable path is pinned to scratch, and the artifacts exist
        pinned = isolate(os.path.join(d, 'scratch'))
        assert set(pinned) == {env for env, _k, _b in REDIRECTABLE}, pinned
        for env, kind, _b in REDIRECTABLE:
            path = os.environ[env]
            assert not _inside_repo(path), (env, path)
            assert os.path.isdir(path) if kind == 'dir' else os.path.isfile(path), (env, path)

        # 2. a value already outside the repo is respected, not clobbered
        mine = os.path.join(d, 'mine.jsonl')
        open(mine, 'a', encoding='utf-8').close()
        os.environ['PWG_RU_STORE'] = mine
        assert isolate(os.path.join(d, 'scratch'))['PWG_RU_STORE'] == mine

        # 3. THE PIN: a value pointing inside the checkout is refused, not overridden --
        #    silently fixing it would hide the caller's mistake.
        os.environ['PWG_RU_STORE'] = os.path.join(REPO, 'pwg_ru_translated.jsonl')
        try:
            isolate(os.path.join(d, 'scratch'))
        except SystemExit as exc:
            assert 'INSIDE the checkout' in str(exc), exc
        else:
            raise AssertionError('a production store path inside the repo must be refused')
        os.environ.pop('PWG_RU_STORE', None)

        # 4. the tripwire notices a watched file changing, and is quiet when nothing does
        before = tripwire()
        assert verify_tripwire(before) == []
        watched = os.path.join(REPO, WATCHED[0])
        forged = dict(before)
        forged[WATCHED[0]] = 'not-the-real-digest'
        assert verify_tripwire(forged) == [WATCHED[0]], 'a changed watched file must be reported'
        assert os.path.exists(watched) or True     # absence is a valid state, not an error

        # 5. absence vs presence is itself tracked (a deleted registry is a violation too)
        missing = dict(before)
        missing['src/pilot/no_pwg_residuals.jsonl'] = None
        if before['src/pilot/no_pwg_residuals.jsonl'] is not None:
            assert 'src/pilot/no_pwg_residuals.jsonl' in verify_tripwire(missing)

        print('selftest_isolation selftest: 5/5 OK')
    finally:
        for env, value in saved.items():
            if value is None:
                os.environ.pop(env, None)
            else:
                os.environ[env] = value
        shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    selftest()
