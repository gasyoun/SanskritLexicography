#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""slp1_norm.py — shared SLP1 join-key normalizer (H180 Deliverable 4, §3 caveat).

The learner-apparatus edition-delta measured (LEARNER_APPARATUS_SPEC.md §3) that
raw set-diffs between dictionaries are inflated by orthographic drift, chiefly
final/internal anusvara `M` vs `m` (AP90 `ABAsanaM` == AP `ABAsanam`). Every
student-dict join and every edition-delta MUST route through this one function so
the learner signal does not inherit OCR/citation-form noise.

Normalization (SLP1 is case-significant — case is preserved):
  * NFC, strip surrounding whitespace
  * drop combining accents / svara marks
  * strip stray citation punctuation ( slash, backslash, pipe, space ) and
    leading/trailing '-'
    (student jsonls store suffix entries as '-AKyAyin')
  * strip a trailing homonym number ('aja3' -> 'aja')
  * collapse anusvara: all 'M' -> 'm' (the measured dominant drift)

Deliberately NOT a transcoder — inputs are already SLP1 (csl-orig <k1>, the
extracted student jsonls' `slp1` field). For IAST/Devanagari inputs use
build_src.iast_to_slp1 / dev_to_slp1 first.
"""
import re
import unicodedata
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

_ACCENT = re.compile(r"[̀-ͯ॑-॔]")
_PUNCT = re.compile(r"[/\\| ]")
_HOMONYM = re.compile(r"\d+$")


def slp1_norm(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s.strip())
    s = _ACCENT.sub("", s)
    s = _PUNCT.sub("", s)
    s = s.strip("-").strip()
    s = _HOMONYM.sub("", s)      # homonym-number strip
    s = s.replace("M", "m")      # anusvara collapse
    return s


if __name__ == "__main__":
    # self-test: the measured AP90/AP anusvara pair must collapse equal
    assert slp1_norm("ABAsanaM") == slp1_norm("ABAsanam") == "ABAsanam"
    assert slp1_norm("-AKyAyin") == "AKyAyin"
    assert slp1_norm("aja3") == "aja"
    assert slp1_norm("saMskftam") == "samskftam"  # internal M collapses too
    print("slp1_norm self-test OK")
