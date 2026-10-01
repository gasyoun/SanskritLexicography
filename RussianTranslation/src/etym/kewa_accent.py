"""Accent stripping for KEWA's IAST, without destroying the letter s-acute.

KEWA prints the Vedic udatta as a combining acute over the accented *vowel*
(`aksa/h` -> a with acute).  Naive NFD + "drop every U+0301" also destroys
**s-acute** (IAST for palatal sh), because that letter decomposes to s + acute
as well - which silently turns every `sh` word into an `s` word before the join.

So the acute is dropped only when the base letter it sits on is a vowel:
a i u e o, and the vocalic r / l (base letter plus the dot-below).
"""
from __future__ import annotations

import unicodedata

ACCENTS = "̀́̂"      # grave, acute, circumflex - the accent marks
DOT_BELOW = "̣"
PLAIN_VOWELS = set("aiueoAIUEO")


def _is_vowel_base(base: str, marks: str) -> bool:
    if base in PLAIN_VOWELS:
        return True
    # vocalic r / l are written base + dot-below in IAST
    return base in "rlRL" and DOT_BELOW in marks


def strip_vowel_accents(s: str) -> str:
    """Drop udatta/grave/circumflex marks over vowels; keep every letter mark."""
    d = unicodedata.normalize("NFD", s)
    out: list[str] = []
    i = 0
    n = len(d)
    while i < n:
        base = d[i]
        j = i + 1
        while j < n and unicodedata.combining(d[j]):
            j += 1
        marks = d[i + 1:j]
        if _is_vowel_base(base, marks):
            marks = "".join(m for m in marks if m not in ACCENTS)
        out.append(base + marks)
        i = j
    return unicodedata.normalize("NFC", "".join(out))
