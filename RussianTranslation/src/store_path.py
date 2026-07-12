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
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# store path relative to a checkout toplevel (main worktree root)
STORE_REL = 'RussianTranslation/src/pwg_ru_translated.jsonl'


def _git(start_dir, *args):
    """Run `git -C <start_dir> <args>` and return stripped stdout ('' on any failure)."""
    return subprocess.run(
        ['git', '-C', start_dir, *args],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        encoding='utf-8', errors='replace',
    ).stdout.strip()


def main_worktree_root(start_dir):
    """Return the MAIN worktree toplevel if `start_dir` is inside a LINKED worktree, else None.

    A linked worktree's git common-dir is `<MAIN>/.git` while its own toplevel is the linked
    directory; the MAIN checkout's common-dir is `<TOP>/.git` (its parent == the toplevel). So
    `dirname(common-dir) != toplevel` iff we are in a linked worktree.
    """
    try:
        common = _git(start_dir, 'rev-parse', '--path-format=absolute', '--git-common-dir')
        top = _git(start_dir, 'rev-parse', '--show-toplevel')
    except Exception:
        return None
    if not common or not top:
        return None
    main = os.path.dirname(os.path.normpath(common))
    if os.path.normpath(main) == os.path.normpath(top):
        return None            # this IS the main checkout
    return main                # a linked worktree -> the main root


def canonical_store(local_default, store_rel=STORE_REL):
    """Resolve the persistent store path: env override -> main-worktree store -> local_default."""
    env = os.environ.get('PWG_RU_STORE')
    if env:
        return env
    main = main_worktree_root(os.path.dirname(os.path.abspath(local_default)))
    if main:
        return os.path.join(main, *store_rel.split('/'))
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
    print('store_path selftest: PASS (env-override wins, non-git falls back to local)')
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
