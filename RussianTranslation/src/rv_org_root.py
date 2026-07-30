#!/usr/bin/env python
"""rv_org_root.py -- locate the org root (the directory holding VisualDCS/), for the RV layer.

Thin compatibility wrapper: `find_github_root` now delegates to the single canonical
resolver in `sibling_root.py` (H1902 -- all 11 `src/` modules that used to guess
`os.path.join(HERE, '..', '..', '..')` now share ONE helper, not two). `$GITHUB_ROOT` is
kept as a legacy alias for `$CSL_SIBLING_ROOT` so existing call sites/env setups still work.
"""
import os

from sibling_root import sibling_root

MARKER = 'VisualDCS'


def find_github_root(start):
    """-> the directory containing VisualDCS/ (or another sibling-repo marker),
    searching upward from `start`. See `sibling_root.sibling_root` for the resolution
    order; `$GITHUB_ROOT` is honoured here as a legacy alias for `$CSL_SIBLING_ROOT`."""
    legacy = os.environ.get('GITHUB_ROOT')
    if legacy and not os.environ.get('CSL_SIBLING_ROOT'):
        return os.path.normpath(legacy)
    return sibling_root(start)


def vedaweb_dir(start):
    return os.path.join(find_github_root(start), MARKER, 'non-derived', 'vedaweb')
