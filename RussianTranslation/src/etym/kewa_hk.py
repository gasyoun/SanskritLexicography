"""Harvard-Kyoto -> SLP1, for auditing the KEWA index's own machine key.

The KEWA index ships two slashed key columns per heading.  The second is
*labelled* nowhere and reads like SLP1, but it is **Harvard-Kyoto**: it writes
sh as `z`, retroflex s as `S`, retroflex n as `N`, the diphthongs as `ai`/`au`.
Joining it straight against csl-orig (SLP1) silently drops every headword that
contains one of those letters.  This module exists to prove that, not to become
a second transcoder - anything that needs IAST/Devanagari goes through
sanskrit-util.
"""
from __future__ import annotations

# Longest first; everything not listed maps to itself.
_PAIRS = [
    ("lRR", "X"), ("lR", "x"), ("RR", "F"),
    ("ai", "E"), ("au", "O"),
    ("kh", "K"), ("gh", "G"), ("ch", "C"), ("jh", "J"),
    ("Th", "W"), ("Dh", "Q"), ("th", "T"), ("dh", "D"),
    ("ph", "P"), ("bh", "B"),
    ("R", "f"), ("G", "N"), ("J", "Y"),
    ("T", "w"), ("D", "q"), ("N", "R"),
    ("z", "S"), ("S", "z"),
]
_MAXLEN = max(len(k) for k, _ in _PAIRS)
_MAP = dict(_PAIRS)


def hk_to_slp1(s: str) -> str:
    out = []
    i = 0
    n = len(s)
    while i < n:
        for ln in range(_MAXLEN, 0, -1):
            chunk = s[i:i + ln]
            if chunk in _MAP:
                out.append(_MAP[chunk])
                i += ln
                break
        else:
            out.append(s[i])
            i += 1
    return "".join(out)
