#!/usr/bin/env python
"""sanskrit_util shim — pwg_ru's import path to the ONE canonical implementation.

Loads the sibling checkout of sanskrit-lexicon/sanskrit-util
(../../../sanskrit-util/py/sanskrit_util/__init__.py, the WhitneyRoots shim
pattern) when it is present, and otherwise falls back to the byte-identical
vendored copy `_sanskrit_util_vendored.py` (needed in CI, where sibling repos
are not checked out). Either way `import sanskrit_util` yields the same module
contents, so pwg_ru consumers (store_flags, pwg_tm_fragmentize) never keep a
second private token table — the H2876 requirement.

Vendored-copy sync: the copy is re-synced from the package by the
/cologne-sanskrit-util-sync batch skill after a version bump, like every other
registered consumer in SHARED_CODE.md §1–2. Do not hand-edit the vendored file.
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SIBLING = os.path.normpath(os.path.join(
    _HERE, '..', '..', '..', 'sanskrit-util', 'py', 'sanskrit_util', '__init__.py'))
_VENDORED = os.path.join(_HERE, '_sanskrit_util_vendored.py')

# The API surface pwg_ru actually consumes; a sibling checkout that predates it
# (e.g. the package PR not yet merged/pulled) is STALE — fall back to vendored
# rather than importing a copy without the German-metalanguage family.
_REQUIRED = 'classify_german_metalanguage'


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = None
SANSKRIT_UTIL_SOURCE = 'vendored'
if os.path.exists(_SIBLING):
    _cand = _load(_SIBLING, '_sanskrit_util_sibling')
    if hasattr(_cand, _REQUIRED):
        _mod = _cand
        SANSKRIT_UTIL_SOURCE = 'sibling'
if _mod is None:
    _mod = _load(_VENDORED, '_sanskrit_util_impl')

_names = getattr(_mod, '__all__', None) or [n for n in dir(_mod) if not n.startswith('_')]
for _n in _names:
    globals()[_n] = getattr(_mod, _n)
__version__ = _mod.__version__
__all__ = list(_names) + ['SANSKRIT_UTIL_SOURCE', '__version__']
