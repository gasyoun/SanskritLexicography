#!/usr/bin/env python
"""rv_org_root.py -- locate the org root (the directory holding VisualDCS/), for the RV layer.

Every RV script that reads the read-only VisualDCS vedaweb feed needs this, and each had
hardcoded `os.path.join(HERE, '..', '..', '..')` -- i.e. "this repo is checked out at
GitHub/SanskritLexicography/RussianTranslation, so three levels up is GitHub/".

That assumption is false exactly where the repo's own CLAUDE.md requires the work to
happen: a `git worktree` lives OUTSIDE GitHub/ (e.g. Documents/SL-h1910-<pid>/), so three
levels up is Documents/ and the feed is not found. Fixed once here rather than a fourth
time in the next script (org CLAUDE.md: one canonical source per family).

$GITHUB_ROOT overrides, for a checkout in neither place.
"""
import os

MARKER = 'VisualDCS'
MAX_UP = 6


def find_github_root(start):
    """-> the directory containing VisualDCS/, searching upward from `start`.

    Falls back to the historical three-levels-up guess so behaviour in the canonical
    checkout is unchanged even if the marker directory is absent.
    """
    env = os.environ.get('GITHUB_ROOT')
    if env and os.path.isdir(os.path.join(env, MARKER)):
        return env
    d = os.path.abspath(start)
    for _ in range(MAX_UP):
        d = os.path.dirname(d)
        if os.path.isdir(os.path.join(d, MARKER)):
            return d
        sibling = os.path.join(d, 'GitHub')
        if os.path.isdir(os.path.join(sibling, MARKER)):
            return sibling
    return os.path.normpath(os.path.join(start, '..', '..', '..'))


def vedaweb_dir(start):
    return os.path.join(find_github_root(start), MARKER, 'non-derived', 'vedaweb')
