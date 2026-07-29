#!/usr/bin/env python
"""Sibling-repo root resolution, hardened against git worktrees (H1902).

Eleven `RussianTranslation/src/` modules locate the checkout's sibling repos
(csl-orig, csl-pywork, SamudraManthanam, ...) by walking three directories up
from the calling module: `RussianTranslation/src/../../.. == GitHub/`. That
guess is true only in the canonical checkout. A worktree created the way the
org's shared-tree rule *requires* (`git worktree add ../<Repo>-h<id>-<pid>`)
lands beside `GitHub/`, not inside it -- so the naive guess resolves to a
directory holding no sibling repos, and every optional lookup silently
degrades to "not found" instead of failing (FINDINGS #503, issue #875).

  python sibling_root.py show        print the resolved root + how it was found
  python sibling_root.py --selftest  prove both warn and raise directions

  python sibling_root.py lookup <abbrev>     resolve one abbreviation
"""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))


def _git_dirs(cwd):
    """(git-common-dir, git-dir), both absolute, or (None, None) outside git."""
    try:
        common = subprocess.check_output(
            ['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
            cwd=cwd, stderr=subprocess.DEVNULL, encoding='utf-8').strip()
        gdir = subprocess.check_output(
            ['git', 'rev-parse', '--path-format=absolute', '--git-dir'],
            cwd=cwd, stderr=subprocess.DEVNULL, encoding='utf-8').strip()
        return common, gdir
    except (OSError, subprocess.CalledProcessError):
        return None, None


def sibling_root():
    """Return (root, pinned).

    `root` is the best-guess `GitHub/` directory holding the sibling repos.
    `pinned` is True when that guess is an explicit assertion that the
    siblings exist here -- an operator-set `CSL_SIBLING_ROOT`, or a linked
    worktree auto-resolved back to its main checkout -- and False for the
    historical three-levels-up guess (right in the canonical checkout, and
    also what a fresh CI clone that checks out only this one repo hits).
    """
    override = os.environ.get('CSL_SIBLING_ROOT')
    if override:
        return os.path.normpath(override), True

    common_dir, git_dir = _git_dirs(HERE)
    if common_dir and git_dir and os.path.normpath(common_dir) != os.path.normpath(git_dir):
        # Linked worktree: git-common-dir is `<main-checkout>/.git`. Its parent
        # is the main checkout's working tree (e.g. `GitHub/SanskritLexicography`),
        # and THAT directory's parent is `GitHub/` itself, holding every sibling repo.
        main_checkout = os.path.dirname(common_dir)
        return os.path.normpath(os.path.dirname(main_checkout)), True

    return os.path.normpath(os.path.join(HERE, '..', '..', '..')), False


def _raise_or_warn(path, what, pinned):
    """Pure decision logic behind require_sibling(), factored out so the
    selftest can exercise both directions without depending on the ambient
    process actually running inside/outside a git worktree."""
    if pinned:
        raise FileNotFoundError(
            '%s not found at %r under a PINNED sibling root -- the sibling '
            'repo is expected to be checked out here' % (what, path))
    sys.stderr.write('%s not found (%s); degrading, not failing (unpinned root)\n' % (what, path))
    return False


def require_sibling(path, what):
    """True if `path` exists. False + a stderr warning if it doesn't and the
    root was an unpinned guess (CI, a fresh clone -- expected, not an error).
    Raises FileNotFoundError if it doesn't and the root was PINNED: an
    operator who set `CSL_SIBLING_ROOT`, or a worktree auto-resolved to its
    main checkout, is asserting the sibling repos are checked out there, so a
    missing table under that root is a build defect, not an optional
    degradation (FINDINGS #503).
    """
    if os.path.exists(path):
        return True
    _, pinned = sibling_root()
    return _raise_or_warn(path, what, pinned)


def cmd_show(_args):
    root, pinned = sibling_root()
    print('root=%s pinned=%s' % (root, pinned))


def selftest():
    import tempfile
    checks = []
    missing = os.path.join(tempfile.gettempdir(), 'sibling_root_selftest_missing_%d' % os.getpid())

    # 1. unpinned + missing -> warn to stderr, return False, never raise
    try:
        ok = _raise_or_warn(missing, 'selftest table', pinned=False)
        checks.append(('unpinned missing warns+returns False', ok is False))
    except Exception as ex:
        checks.append(('unpinned missing warns+returns False', False))
        print('  unexpected raise: %r' % ex)

    # 2. pinned + missing -> raise FileNotFoundError
    try:
        _raise_or_warn(missing, 'selftest table', pinned=True)
        checks.append(('pinned missing raises', False))
    except FileNotFoundError:
        checks.append(('pinned missing raises', True))

    # 3. an existing path never raises or warns via require_sibling(), pinned or not
    saved = os.environ.pop('CSL_SIBLING_ROOT', None)
    try:
        checks.append(('existing path -> True (ambient root)', require_sibling(HERE, 'this dir') is True))
        os.environ['CSL_SIBLING_ROOT'] = tempfile.gettempdir()
        checks.append(('existing path -> True (env-pinned root)', require_sibling(HERE, 'this dir') is True))
    finally:
        os.environ.pop('CSL_SIBLING_ROOT', None)
        if saved is not None:
            os.environ['CSL_SIBLING_ROOT'] = saved

    # 4. CSL_SIBLING_ROOT env override wins and is reported as pinned
    saved = os.environ.pop('CSL_SIBLING_ROOT', None)
    try:
        os.environ['CSL_SIBLING_ROOT'] = tempfile.gettempdir()
        root, pinned = sibling_root()
        checks.append(('env override -> pinned root', pinned is True and root == os.path.normpath(tempfile.gettempdir())))
    finally:
        os.environ.pop('CSL_SIBLING_ROOT', None)
        if saved is not None:
            os.environ['CSL_SIBLING_ROOT'] = saved

    bad = 0
    for name, ok in checks:
        print(('PASS ' if ok else 'FAIL ') + name)
        bad += 0 if ok else 1
    print('sibling_root: %d/%d checks pass' % (len(checks) - bad, len(checks)))
    return 1 if bad else 0


def main():
    args = sys.argv[1:]
    if not args or args[0] == 'show':
        cmd_show(args[1:])
        return
    if args[0] == '--selftest':
        sys.exit(selftest())
    print(__doc__)


if __name__ == '__main__':
    main()
