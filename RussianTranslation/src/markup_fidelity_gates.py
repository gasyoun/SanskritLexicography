#!/usr/bin/env python
r"""markup_fidelity_gates.py — shared lang-agnostic markup fidelity gates (OPT-2 / H2227).

WHY THIS EXISTS
---------------
`audit_window.py` orchestrates child auditors (including `audit_translation.py`) while
`audit_window_en.py` reimplemented the same HARD markup invariants per-sense against
`german` → `english`. That fork is the LANG_PARITY C1–C9 class of EN-only holes:
thresholds, abs-drop guards, and DUP keying drifted independently.

This module holds ONE implementation of the language-agnostic HARD gates:

  LS-LOSS   every <ls> open-tag must survive (target keeps >= LS_KEEP, abs drop >= 2)
  SAN-LOSS  every distinct {#…#} Sanskrit span must survive (>= SAN_KEEP, abs drop >= 2)
  AB-LOSS   <ab>/<lex>/<lang> open-tags must survive (abs drop >= 2)
  DUP       two senses in one record share identical *target-field* text (raw, not prose)

Parameterized by the target-language field name (`russian` / `english`) for the DUP /
MISSING-* surfaces that read sense[field]. Soft language-specific flags (NO-RUSSIAN,
DE-RESIDUE, MW-DIVERGE, …) stay in the thin wrappers.

Callers
-------
* `audit_window_en.py` — per-sense german vs english (all four families + soft MARKUP-LOSS)
* `audit_translation.py` — whole-card .raw.txt vs .merged.md (LS + SAN only; AB is owned by
  stage2_pregate on the RU path, so not double-emitted here)

Thresholds match the historical EN/RU pair (ratio + abs-drop guard for LS/SAN; abs-only
for AB). DUP keys on normalized RAW target text so senses distinguished only by a {#…#}
referent are not false-flagged (C2).

  python src/markup_fidelity_gates.py --selftest
"""
from __future__ import annotations

import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Open-tag counts (not full-span multisets) — matches audit_window_en / audit_translation.
LS_RE = re.compile(r'<ls\b')
SAN_RE = re.compile(r'\{#.*?#\}', re.S)
AB_RE = re.compile(r'<(?:ab|lex|lang)\b')
GLOSS_RE = re.compile(r'\{%.*?%\}', re.S)
DIVTAG_RE = re.compile(r'<div\b')

LS_KEEP = 0.90
SAN_KEEP = 0.85
MIN_ABS_LOSS = 2

# Structural sense tags that legitimately repeat trivial target prose ("With …").
HEADERLIKE_TAGS = ('header', 'gramm-forms', 'grammar', 'paradigm')

VALID_TARGET_FIELDS = frozenset({'russian', 'english'})


def _require_field(field: str) -> str:
    if field not in VALID_TARGET_FIELDS:
        raise ValueError(
            'markup_fidelity_gates: field must be one of %s, got %r'
            % (sorted(VALID_TARGET_FIELDS), field)
        )
    return field


def ls_san_ab_counts(text: str):
    """(ls_open_count, distinct_san_span_count, ab_lex_lang_open_count)."""
    t = text or ''
    return len(LS_RE.findall(t)), len(set(SAN_RE.findall(t))), len(AB_RE.findall(t))


def markup_span_flags(source: str, target: str, *, check_ab: bool = True) -> list:
    """HARD markup span-survival flags comparing source (German) vs target (RU/EN text).

    Returns a list of flag strings such as ``LS-LOSS(3/10)``. Empty when clean.
    ``check_ab=False`` keeps the historical audit_translation surface (AB lives on the
    RU path in stage2_pregate; EN owns AB here via check_ab=True).
    """
    g, e = source or '', target or ''
    flags = []
    sls, ols = len(LS_RE.findall(g)), len(LS_RE.findall(e))
    if sls > 0 and ols < sls * LS_KEEP and (sls - ols) >= MIN_ABS_LOSS:
        flags.append('LS-LOSS(%d/%d)' % (ols, sls))
    ssan, osan = len(set(SAN_RE.findall(g))), len(set(SAN_RE.findall(e)))
    if ssan > 0 and osan < ssan * SAN_KEEP and (ssan - osan) >= MIN_ABS_LOSS:
        flags.append('SAN-LOSS(%d/%d)' % (osan, ssan))
    if check_ab:
        sab, oab = len(AB_RE.findall(g)), len(AB_RE.findall(e))
        if sab > 0 and (sab - oab) >= MIN_ABS_LOSS:
            flags.append('AB-LOSS(%d/%d)' % (oab, sab))
    return flags


def markup_wrapper_soft_flags(source: str, target: str) -> list:
    """SOFT MARKUP-LOSS when {%…%} gloss wrappers or <div> pairs drop while prose may survive.

    Counts each class separately (P8 / H1422) so a dropped {%} cannot be masked by a gained
    <div> (net combined count unchanged).
    """
    g, e = source or '', target or ''
    sgl, ogl = len(GLOSS_RE.findall(g)), len(GLOSS_RE.findall(e))
    sdiv, odiv = len(DIVTAG_RE.findall(g)), len(DIVTAG_RE.findall(e))
    if (sgl > 0 and ogl < sgl) or (sdiv > 0 and odiv < sdiv):
        return ['MARKUP-LOSS(%d/%d)' % (ogl + odiv, sgl + sdiv)]
    return []


def missing_target_flag(has_gloss: bool, target_text: str, field: str = 'english'):
    """HARD MISSING-EN / MISSING-RU when source had gloss prose and the target field is empty."""
    _require_field(field)
    if has_gloss and not (target_text or '').strip():
        return 'MISSING-EN' if field == 'english' else 'MISSING-RU'
    return None


def dup_key(target_text: str) -> str:
    """Normalized RAW target key for within-record DUP (keep {#…#}/<ls> referents — C2)."""
    return re.sub(r'\s+', ' ', (target_text or '')).strip().lower()


def within_record_identical_target(
    senses,
    field: str = 'english',
    *,
    headerlike=HEADERLIKE_TAGS,
    soft_same_gloss_min_words: int = 3,
    content_word_count_fn=None,
):
    """Within-record identical-target-field check.

    Parameters
    ----------
    senses : iterable of sense dicts with ``tag`` + ``field`` keys
    field : ``'english'`` or ``'russian'`` — which sense field is the translation target
    content_word_count_fn : optional ``callable(sense) -> int`` for the soft SAME-GLOSS
        companion (gated on >= soft_same_gloss_min_words content words). If None, SAME-GLOSS
        is never emitted (HARD DUP still fires).

    Returns
    -------
    list of (tag, hard_flags, soft_flags) one entry per input sense, in order.
    """
    _require_field(field)
    seen = {}
    out = []
    for si, s in enumerate(senses or []):
        tag = str((s or {}).get('tag') or si)
        hard, soft = [], []
        key = dup_key((s or {}).get(field))
        headerlike_hit = any(hk in tag for hk in headerlike)
        if key and not headerlike_hit:
            if key in seen:
                hard.append('DUP(=%s)' % seen[key])
                if content_word_count_fn is not None:
                    n = content_word_count_fn(s)
                    if n >= soft_same_gloss_min_words:
                        soft.append('SAME-GLOSS(=%s)' % seen[key])
            else:
                seen[key] = tag
        out.append((tag, hard, soft))
    return out


def _selftest():
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    # LS / SAN ratio + abs guard
    g = '<ls>MBh.</ls> <ls>R.</ls> <ls>RV.</ls> {%gehen%}'
    e_ok = '<ls>MBh.</ls> <ls>R.</ls> <ls>RV.</ls> go'
    e_drop = '<ls>MBh.</ls> go'  # 1/3 kept, abs drop 2
    check(not markup_span_flags(g, e_ok), 'clean triple <ls> must not flag')
    fl = markup_span_flags(g, e_drop)
    check(any(f.startswith('LS-LOSS') for f in fl), '2 dropped <ls> must LS-LOSS: %r' % fl)

    # tiny abs-drop of 1 must NOT flag (ratio would trip without abs guard)
    g1 = '<ls>A.</ls> <ls>B.</ls> {%x%}'
    e1 = '<ls>A.</ls> x'  # 1/2, abs drop 1
    check(not markup_span_flags(g1, e1), 'single <ls> drop on tiny card must not false-flag')

    # SAN distinct
    gsan = '{#a#} {#b#} {#c#} {#a#} {%gloss%}'
    esan = '{#a#} gloss'
    fl = markup_span_flags(gsan, esan)
    check(any(f.startswith('SAN-LOSS') for f in fl), 'SAN-LOSS on dropped distinct spans: %r' % fl)

    # AB abs-only
    gab = '<ab>lat.</ab> <ab>griech.</ab> <lex>m.</lex> {%x%}'
    eab = '{%x%}'
    fl = markup_span_flags(gab, eab, check_ab=True)
    check(any(f.startswith('AB-LOSS') for f in fl), 'AB-LOSS expected: %r' % fl)
    fl = markup_span_flags(gab, eab, check_ab=False)
    check(not any(f.startswith('AB-LOSS') for f in fl), 'check_ab=False must suppress AB')

    # MARKUP-LOSS soft, per-class (P8)
    soft = markup_wrapper_soft_flags('{%a%} {%b%}', '<div n="1"/> <div n="2"/> x')
    check(any(f.startswith('MARKUP-LOSS') for f in soft), 'dropped {%} must soft MARKUP-LOSS')

    # DUP on raw field (C2)
    senses = [
        {'tag': '1', 'english': 'N. of a serpent-demon {#vAsuki#}'},
        {'tag': '2', 'english': 'N. of a serpent-demon {#takzaka#}'},
    ]
    rows = within_record_identical_target(senses, 'english')
    check(not any(h for _, h, _ in rows), 'C2: distinct {#} referent must not DUP: %r' % rows)
    senses2 = [
        {'tag': '1', 'english': 'to go'},
        {'tag': '2', 'english': 'to go'},
    ]
    rows = within_record_identical_target(
        senses2, 'english', content_word_count_fn=lambda s: 2
    )
    check(any(h and h[0].startswith('DUP') for _, h, _ in rows), 'identical english must DUP')
    # soft SAME-GLOSS needs >=3 content words
    check(not any(s for _, _, s in rows), 'SAME-GLOSS suppressed when word count < 3')

    # field parameterization for russian
    rows = within_record_identical_target(
        [{'tag': '1', 'russian': 'идти'}, {'tag': '2', 'russian': 'идти'}],
        'russian',
    )
    check(any(h and h[0].startswith('DUP') for _, h, _ in rows), 'DUP must key russian field')

    # MISSING-*
    check(missing_target_flag(True, '', 'english') == 'MISSING-EN', 'MISSING-EN')
    check(missing_target_flag(True, '', 'russian') == 'MISSING-RU', 'MISSING-RU')
    check(missing_target_flag(False, '', 'english') is None, 'no gloss -> no MISSING')

    if fails:
        print('SELFTEST FAIL (%d):' % len(fails))
        for f in fails:
            print('  -', f)
        return 1
    print('markup_fidelity_gates --selftest: %d checks OK' % 12)
    return 0


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
    sys.exit(0)
