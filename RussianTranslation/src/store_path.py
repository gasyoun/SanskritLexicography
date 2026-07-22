#!/usr/bin/env python
r"""Canonical store-path resolver: ONE logical pwg_ru store, shared across all worktrees.

The translated store `src/pwg_ru_translated.jsonl` is a gitignored, local-only runtime
artifact. There is exactly ONE logical store for a checkout tree, not one per branch or
per worktree. But historically every consumer resolved it relative to its own directory
(`os.path.join(HERE, 'pwg_ru_translated.jsonl')`), so a drain window run in an isolated
`git worktree` — the *sanctioned* branch-contention path (see the repo CLAUDE.md main-tree
commit guard) — promoted into a WORKTREE-LOCAL copy of the store that was DISCARDED when the
worktree was removed. Every promotion in that worktree vanished silently.

That is exactly how the H255 `no_pwg_w06` window lost its 29 promoted sub-cards: it ran in an
isolated worktree, copied the shared 11,505-row store in, promoted to 11,558 there, and the
worktree (and its store) were removed after the PR merged — leaving the live store at 11,505
with no trace of w06 except the RUN_LOG record. See
`src/pilot/RUN_LOG.md` (the `no_pwg_w06` block) and the H805 handoff.

`canonical_store()` resolves the persistent store in priority order:

  1. `$PWG_RU_STORE`      -- explicit override. Already honored by run_batch.py /
                            release_readiness.py / preflight_remaining_gates.py; lets a test,
                            CI job, or a deliberately-isolated diagnostic run pin its own store.
  2. main-worktree store  -- if we are inside a LINKED git worktree, the store in the MAIN
                            checkout (the git common-dir's parent). This is the persistent home;
                            a worktree drain now promotes THERE, so nothing is dropped on cleanup.
                            `promote_final_cards.py`'s existing `PromoteClaim` lock serialises
                            concurrent promotions on that shared path.
  3. local_default        -- main checkout / non-git tree: the caller's own path, unchanged.

The default is loss-safety: a worktree run persists to the canonical store unless it *opts out*
by setting `$PWG_RU_STORE` to a scratch path.
"""
import functools
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# store path relative to a checkout toplevel (main worktree root)
STORE_REL = 'RussianTranslation/src/pwg_ru_translated.jsonl'


def _git(start_dir, *args):
    """Run `git -C <start_dir> <args>` and return stripped stdout.

    Failure must raise: callers may cache successful checkout identity, but must never cache a
    transient Git failure as the loss-unsafe conclusion that a linked worktree is standalone.
    """
    proc = subprocess.run(
        ['git', '-C', start_dir, *args],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        encoding='utf-8', errors='replace',
    )
    if proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, proc.args)
    output = proc.stdout.strip()
    if not output:
        raise RuntimeError('git returned an empty repository path')
    return output


@functools.lru_cache(maxsize=64)
def _main_worktree_root_cached(start_dir):
    """Return the MAIN worktree toplevel if `start_dir` is inside a LINKED worktree, else None.

    A linked worktree's git common-dir is `<MAIN>/.git` while its own toplevel is the linked
    directory; the MAIN checkout's common-dir is `<TOP>/.git` (its parent == the toplevel). So
    `dirname(common-dir) != toplevel` iff we are in a linked worktree.
    """
    common = _git(start_dir, 'rev-parse', '--path-format=absolute', '--git-common-dir')
    top = _git(start_dir, 'rev-parse', '--show-toplevel')
    main = os.path.dirname(os.path.normpath(common))
    if os.path.normpath(main) == os.path.normpath(top):
        return None            # this IS the main checkout
    return main                # a linked worktree -> the main root


def _has_git_marker(start_dir):
    """Cheap error-path check: is this directory nested under a .git file/directory?"""
    current = os.path.abspath(start_dir)
    while True:
        if os.path.exists(os.path.join(current, '.git')):
            return True
        parent = os.path.dirname(current)
        if parent == current:
            return False
        current = parent


def main_worktree_root(start_dir):
    """Resolve once per normalized directory for the lifetime of this Python process.

    Canonical store/sidecar helpers are hot during harness construction.  On Windows each
    uncached lookup launches two Git processes, so the old implementation spent seconds
    repeatedly rediscovering an immutable property of the checkout.
    """
    normalized = os.path.normcase(os.path.abspath(start_dir))
    try:
        return _main_worktree_root_cached(normalized)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        # Non-git directories legitimately fall back to the local path. Inside a checkout, however,
        # an unresolved identity must fail closed: using local_default for even one linked-worktree
        # store write recreates the H255 loss mode. Exceptions are not cached, so a retry can recover.
        if _has_git_marker(normalized):
            raise RuntimeError('cannot resolve Git worktree identity for %s' % normalized) from exc
        return None


def canonical_store(local_default, store_rel=STORE_REL):
    """Resolve the persistent store path: env override -> main-worktree store -> local_default."""
    env = os.environ.get('PWG_RU_STORE')
    if env:
        return env
    main = main_worktree_root(os.path.dirname(os.path.abspath(local_default)))
    if main:
        return os.path.join(main, *store_rel.split('/'))
    return local_default


# sidecar directory relative to a checkout toplevel (the TM caches / denylist home)
SIDECAR_REL = 'RussianTranslation/src/pilot'


def canonical_sidecar(local_default, sidecar_rel=SIDECAR_REL):
    """Resolve a gitignored `src/pilot` sidecar (TM caches, suggest TM, denylist) the same
    way `canonical_store` resolves the store: env dir override -> main-worktree copy ->
    local default.

    H1339 B04: the sidecars are BUILT FROM the one canonical store, so there is exactly ONE
    logical copy per checkout tree — but every resolver defaulted to its own checkout's
    `src/pilot`, and the sidecars are gitignored, so the sanctioned fresh-worktree workflow
    silently saw NO sidecars: 0 TM hits, full re-translation cost on every worktree run,
    and a worktree promote's TM rebuild landed in a directory that vanished with the
    worktree. `$PWG_RU_TM_DIR` pins a directory for tests/deliberately-isolated runs
    (deliberately its own variable — `$PWG_RU_STORE` names the store FILE)."""
    env = os.environ.get('PWG_RU_TM_DIR')
    name = os.path.basename(local_default)
    if env:
        return os.path.join(env, name)
    main = main_worktree_root(os.path.dirname(os.path.abspath(local_default)))
    if main:
        return os.path.join(main, *sidecar_rel.split('/'), name)
    return local_default


def selftest():
    import tempfile
    # 1. explicit env override always wins
    os.environ['PWG_RU_STORE'] = os.path.join('scratch', 'store.jsonl')
    got = canonical_store(os.path.join('whatever', 'pwg_ru_translated.jsonl'))
    assert got == os.path.join('scratch', 'store.jsonl'), got
    del os.environ['PWG_RU_STORE']
    # 2. a non-git directory -> local default unchanged, and no phantom "main worktree"
    with tempfile.TemporaryDirectory() as d:
        lp = os.path.join(d, 'pwg_ru_translated.jsonl')
        assert canonical_store(lp) == lp, canonical_store(lp)
        assert main_worktree_root(d) is None
    # 2b. repeated/lexically-equivalent paths share one cached Git resolution.
    _original_git = globals()['_git']
    calls = []
    try:
        _main_worktree_root_cached.cache_clear()
        globals()['_git'] = lambda start, *args: (
            calls.append((start, args)) or
            (os.path.join(start, '.git') if '--git-common-dir' in args else start))
        probe = os.path.join('scratch', 'checkout')
        assert main_worktree_root(probe) is None
        assert main_worktree_root(os.path.join(probe, '.')) is None
        assert len(calls) == 2, calls
    finally:
        globals()['_git'] = _original_git
        _main_worktree_root_cached.cache_clear()
    # 2c. a transient Git failure is not cached as a standalone-worktree result.
    calls = []
    try:
        _main_worktree_root_cached.cache_clear()
        marker_root = tempfile.mkdtemp(prefix='store_path_linked_')
        linked = os.path.join(marker_root, 'linked')
        main = os.path.join(marker_root, 'main')
        os.makedirs(linked)
        os.makedirs(main)
        with open(os.path.join(linked, '.git'), 'w', encoding='utf-8') as f:
            f.write('gitdir: synthetic')

        def fail_once_then_linked(start, *args):
            calls.append((start, args))
            if len(calls) == 1:
                raise OSError('synthetic transient Git failure')
            return (os.path.join(main, '.git') if '--git-common-dir' in args else
                    linked)

        globals()['_git'] = fail_once_then_linked
        try:
            main_worktree_root(linked)
            raise AssertionError('a Git failure inside a checkout must fail closed')
        except RuntimeError as exc:
            assert 'cannot resolve Git worktree identity' in str(exc), exc
        assert main_worktree_root(linked) == main
        assert main_worktree_root(linked) == main
        assert len(calls) == 3, calls
    finally:
        globals()['_git'] = _original_git
        _main_worktree_root_cached.cache_clear()
        if 'marker_root' in locals():
            import shutil
            shutil.rmtree(marker_root)
    # 3. inside a LINKED worktree -> resolve to the MAIN checkout store (H818 D-E: this is the
    # resolution translation_memory.DEFAULT_STORE now shares with promote_final_cards, so a
    # worktree run's post-promotion TM rebuild targets the MAIN store, not a vanishing local one).
    os.environ.pop('PWG_RU_STORE', None)
    _orig = globals()['main_worktree_root']
    try:
        globals()['main_worktree_root'] = lambda start: os.path.join('MAIN', 'checkout')
        got = canonical_store(os.path.join('WT', 'linked', 'pwg_ru_translated.jsonl'))
        assert got == os.path.join('MAIN', 'checkout', *STORE_REL.split('/')), got
    finally:
        globals()['main_worktree_root'] = _orig
    # 4. env override still beats the worktree resolution (explicit pin wins over everything)
    os.environ['PWG_RU_STORE'] = os.path.join('scratch', 's.jsonl')
    try:
        globals()['main_worktree_root'] = lambda start: os.path.join('MAIN', 'checkout')
        assert canonical_store(os.path.join('WT', 'x.jsonl')) == os.path.join('scratch', 's.jsonl')
    finally:
        globals()['main_worktree_root'] = _orig
        del os.environ['PWG_RU_STORE']
    # 5. canonical_sidecar (H1339 B04): env dir override -> main-worktree src/pilot -> local.
    os.environ.pop('PWG_RU_TM_DIR', None)
    with tempfile.TemporaryDirectory() as d:
        lp = os.path.join(d, 'translation_memory.ru.json')
        assert canonical_sidecar(lp) == lp, 'non-git tree must fall back to the local sidecar'
    try:
        globals()['main_worktree_root'] = lambda start: os.path.join('MAIN', 'checkout')
        got = canonical_sidecar(os.path.join('WT', 'src', 'pilot', 'translation_memory.ru.json'))
        want = os.path.join('MAIN', 'checkout', *SIDECAR_REL.split('/'),
                            'translation_memory.ru.json')
        assert got == want, got
        os.environ['PWG_RU_TM_DIR'] = os.path.join('scratch', 'tmdir')
        got = canonical_sidecar(os.path.join('WT', 'src', 'pilot', 'x.jsonl'))
        assert got == os.path.join('scratch', 'tmdir', 'x.jsonl'), got
    finally:
        globals()['main_worktree_root'] = _orig
        del os.environ['PWG_RU_TM_DIR']
    print('store_path selftest: PASS (env-override wins, worktree->main, non-git falls back '
          'to local; sidecars H1339-B04 likewise)')
    return True


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='canonical pwg_ru store-path resolver')
    ap.add_argument('--selftest', action='store_true', help='run the deterministic selftest')
    ap.add_argument('--resolve', metavar='LOCAL_DEFAULT',
                    help='print the resolved store for a given local-default path')
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.resolve:
        print(canonical_store(a.resolve))
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        print(canonical_store(os.path.join(here, 'pwg_ru_translated.jsonl')))
