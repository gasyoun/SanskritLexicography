#!/usr/bin/env python
"""sibling_root.py -- locate GitHub/, the checkout holding every sibling repo this
pipeline reads optional tables from (csl-orig, csl-pywork, SamudraManthanam,
VisualDCS, WhitneyRoots, CommentaryStrategies, rvlinks, ...).

Eleven `RussianTranslation/src/` modules each independently guessed
`os.path.join(HERE, '..', '..', '..')` -- "this repo is checked out at
GitHub/SanskritLexicography/RussianTranslation, so three levels up is GitHub/".
That is true only in the canonical checkout. A `git worktree` -- which the org's
shared-tree rule REQUIRES for exactly this repo -- lands beside GitHub/, not
inside it, so the guess silently resolves to a directory with no sibling repos
and every optional table "disappears" without the build failing: a pinned G5
sheet re-issue built from a worktree shipped 0 `<ab>` spans instead of 253
(FINDINGS §503, H1847/H1902).

  python sibling_root.py --selftest    proves both require_sibling() directions

One canonical resolver, honoured by every module that used to guess:
  1. $CSL_SIBLING_ROOT, if set -- an explicit operator assertion (see
     `require_sibling`).
  2. auto-detect: walk upward from the caller's file looking for a directory
     holding one of the marker sibling repos.
  3. the historical three-levels-up guess, so canonical-checkout behaviour is
     unchanged even when no marker is found (e.g. a shallow/partial clone).
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

MARKERS = ('csl-orig', 'VisualDCS', 'SamudraManthanam')
MAX_UP = 6


def sibling_root(start):
    """-> best-guess path to GitHub/, searching upward from `start` (a file or dir)."""
    env = os.environ.get('CSL_SIBLING_ROOT')
    if env:
        return os.path.normpath(env)
    d = os.path.abspath(start)
    for _ in range(MAX_UP):
        d = os.path.dirname(d)
        if any(os.path.isdir(os.path.join(d, m)) for m in MARKERS):
            return d
    return os.path.normpath(os.path.join(start, '..', '..', '..'))


def require_sibling(path, what):
    """True if `path` exists.

    When `CSL_SIBLING_ROOT` is set, the operator is asserting the siblings
    exist, so a missing expected table is an ERROR, not a degradation --
    raises `FileNotFoundError` instead of returning False. Left unset, this
    just returns the plain bool and the caller keeps its own warn-and-continue
    path (CI, which checks out only this one repo, depends on that silence).
    """
    ok = os.path.exists(path)
    if not ok and os.environ.get('CSL_SIBLING_ROOT'):
        raise FileNotFoundError(
            '%s not found at %s -- CSL_SIBLING_ROOT=%r was set, asserting the '
            'siblings exist, so this is an error, not an optional-table '
            'degradation' % (what, path, os.environ['CSL_SIBLING_ROOT']))
    return ok


def _selftest():
    import tempfile
    failures = []

    # unset ⇒ require_sibling degrades to a plain bool, no raise
    os.environ.pop('CSL_SIBLING_ROOT', None)
    if require_sibling(os.path.join(tempfile.gettempdir(), 'no-such-file'), 'x') is not False:
        failures.append('unset: expected False, no raise')

    # set-but-missing ⇒ raise
    with tempfile.TemporaryDirectory() as td:
        os.environ['CSL_SIBLING_ROOT'] = td
        try:
            require_sibling(os.path.join(td, 'no-such-file'), 'x')
            failures.append('set-but-missing: expected FileNotFoundError, got none')
        except FileNotFoundError:
            pass
        finally:
            del os.environ['CSL_SIBLING_ROOT']

    # set-and-present ⇒ True, no raise
    with tempfile.TemporaryDirectory() as td:
        present = os.path.join(td, 'present')
        open(present, 'w').close()
        os.environ['CSL_SIBLING_ROOT'] = td
        try:
            if require_sibling(present, 'x') is not True:
                failures.append('set-and-present: expected True')
        finally:
            del os.environ['CSL_SIBLING_ROOT']

    if failures:
        for f in failures:
            print('FAIL:', f, file=sys.stderr)
        sys.exit(1)
    print('sibling_root selftest: OK (3/3)')


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
    else:
        print(__doc__)
