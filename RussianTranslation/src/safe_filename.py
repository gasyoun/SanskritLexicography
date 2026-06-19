#!/usr/bin/env python
"""Shared reversible filename stems for case-sensitive Sanskrit keys.

SLP1 keys are case-sensitive, while common Windows filesystems are not. Earlier
tools encoded uppercase as ``_`` + lowercase; keep that convention so existing
generated files remain readable, and additionally escape characters Windows
cannot store in filenames (notably ``|`` in a few PWG keys).
"""

import re

_RESERVED = {
    'CON', 'PRN', 'AUX', 'NUL',
    *(('COM%d' % i) for i in range(1, 10)),
    *(('LPT%d' % i) for i in range(1, 10)),
}
_SAFE = re.compile(r'[a-z0-9-]')


def _escape(ch):
    return '~%04x' % ord(ch)


def safe_name(key):
    """Return a reversible, Windows-safe, case-collision-safe filename stem."""
    out = []
    for ch in str(key):
        if 'A' <= ch <= 'Z':
            out.append('_' + ch.lower())
        elif _SAFE.fullmatch(ch):
            out.append(ch)
        else:
            out.append(_escape(ch))
    stem = ''.join(out) or '~0000'
    if stem.upper() in _RESERVED:
        stem = '~0000' + stem
    return stem


def legacy_safe_name(key):
    """The pre-2026-06-19 uppercase-only encoder, for compatibility checks."""
    return ''.join('_' + c.lower() if c.isupper() else c for c in str(key))


def candidate_names(key):
    """Prefer the new safe stem, then the legacy stem if it differs."""
    names = [safe_name(key)]
    old = legacy_safe_name(key)
    if old != names[0]:
        names.append(old)
    return names


def decode_safe_name(stem):
    """Decode stems produced by safe_name(); useful for audits/tests."""
    if stem.startswith('~0000') and stem[5:].upper() in _RESERVED:
        stem = stem[5:]
    out = []
    i = 0
    while i < len(stem):
        if stem[i] == '_' and i + 1 < len(stem):
            out.append(stem[i + 1].upper())
            i += 2
        elif stem[i] == '~' and i + 4 < len(stem):
            out.append(chr(int(stem[i + 1:i + 5], 16)))
            i += 5
        else:
            out.append(stem[i])
            i += 1
    return ''.join(out)
