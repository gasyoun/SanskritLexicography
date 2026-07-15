#!/usr/bin/env python
r"""Deterministic source-sense counting + the SAN-LOSS (whole-dropped-sense) guard (H920).

The pipeline had NO deterministic guard comparing the number of senses the SOURCE
declares to the number of senses the model actually emitted. The only whole-card
completeness check is the harness `accept()` <ls>/{# token-count match
(gen_opt_harness2.py), which is blind to a dropped sense that carries neither a
citation nor a masked Sanskrit span — exactly the shape of a citation-free PW/SCH/
NWS supplement gloss. Live evidence (H818 fc1): `darv_i~~h0_zz_pw` had a 3-sense
PW source

    — 1〉 {%Löffel%}.
    — 2〉 {%die Haube einer Schlange%}.
    — 3〉 {#darvI#} <ab>N. pr.</ab> eines Landes.

the model dropped sense 1 ("Löffel/spoon"), emitted senses {2,3}, and accept()
passed it clean (ls 0==0, sk 3==3 — the dropped gloss carried neither). The harness
even computed `inputs[k]['senses'] = raw.count('〉') == 3` but never consumed it.

This module is the deterministic, language-agnostic guard the no_pwg / supplement
lane was missing. It is imported by BOTH audit paths (audit_window.py for RU,
audit_window_en.py for EN) and by _pilot_gen_merged.py (to stamp `source_senses`
into the no_pwg portrait at input-generation time). Pure — no model calls, no
network, no side effects.
"""
import json
import os
import re

# A top-level source sense OPENS its line: the sense-ordinal `N〉` (PWG/PW sense-close
# glyph, digit + U+3009 RIGHT ANGLE BRACKET) — or the line-anchored `N)` split notation
# used by the deterministic splitter (autosplit_requeue._SENSE) — is the FIRST ordinal on
# its line, preceded only by "opening" material: leading whitespace, a sense dash (— / – /
# -), the headword pipe ¦, a structural tag (<div..>), a {Tn} mask token, or a masked/
# unmasked headword ref {#..#}¦.
#
# H960 hardening (cross-reference false-positive fix). The pre-H960 counter did a naive
# `\d+〉` findall over the whole blob, which counted every sense-ordinal glyph — including
# CROSS-REFERENCES into ANOTHER entry's numbering ("pra 1〉 = {#sUd#} 3〉", "gehört zu 4〉",
# "Nom. abstr. zu {#ASraya#} 1〉 und 6〉", "pari 5〉") — as if this card declared that many
# senses. On a promoted-store corpus scan ~4.78% of cards carried such a mid-prose ordinal,
# so the naive count over-stated `source_senses` and would spuriously flag a faithful card
# as SAN-LOSS (H960 verify evidence: gam~~h2_31_pari 2->1, s_ud~~h0_05_pra 4->2,
# _a_srayatva 2->0). A mid-line ordinal is never a sense of THIS card, so it is skipped;
# only the FIRST ordinal per line can open a sense (any later N〉 on the same line is by
# construction a cross-reference). Sub-senses (lettered a)/b), or `Nc`) remain uncounted —
# only distinct top-level ARABIC ordinals, so merging one sense's lettered sub-senses never
# mis-flags a shortfall. Under-counting (a genuinely-numbered sense whose marker is not
# line-opening) is the safe direction: it lowers the expected count, never a false shortfall.
_ORD = re.compile(r'(\d+)\s*[\)〉]')
_OPEN_PREFIX = re.compile(r'^[\s—–\-|¦]*(?:(?:\{T\d+\}|<[^>]*>|\{#[^#]*#\}¦?)[\s—–\-|¦]*)*$')


def source_sense_ordinals(text):
    """The set of distinct TOP-LEVEL arabic sense ordinals a raw/masked source blob
    declares. An ordinal is counted only when it OPENS its line (preceded solely by the
    opening material in _OPEN_PREFIX); a mid-line ordinal is a cross-reference into another
    entry's numbering and is skipped. Empty when the source carries no line-opening
    numbering (a single unnumbered supplement sense) — the caller treats an empty/singleton
    set as "nothing to compare"."""
    ords = set()
    for line in (text or '').split('\n'):
        m = _ORD.search(line)
        if m and _OPEN_PREFIX.match(line[:m.start()]):
            ords.add(int(m.group(1)))
    return ords


def count_source_senses(text):
    """Number of distinct top-level source senses (see source_sense_ordinals).

    Deterministic and conservative: counts only line-opening top-level senses (never a
    mid-prose cross-reference ordinal), so it is a LOWER BOUND on the senses the model
    must emit — never an over-count that could spuriously flag a faithfully-merged card.
    Equals 3 on the darvI evidence; unlike the harness's coarse `raw.count('〉')`, it does
    NOT inflate on cross-reference ordinals (H960 hardening — see _OPEN_PREFIX)."""
    return len(source_sense_ordinals(text))


def output_sense_count(card):
    """Number of senses actually present in a generated card (records[].senses[]).
    Language-agnostic — counts sense objects, independent of ru/en gloss field."""
    if not isinstance(card, dict):
        return 0
    return sum(len([s for s in (rec.get('senses') or []) if isinstance(s, dict)])
               for rec in (card.get('records') or []))


def sense_shortfall(card, expected):
    """Positive count of senses dropped from `card` versus an `expected` source-sense
    count, or 0 when there is no shortfall (or `expected` is unknown/<1). This is the
    SAN-LOSS signal: expected > output means whole source senses were dropped."""
    try:
        expected = int(expected)
    except (TypeError, ValueError):
        return 0
    if expected < 1:
        return 0
    actual = output_sense_count(card)
    return expected - actual if actual < expected else 0


def _portrait_paths(input_dir, key):
    # gen writes the sidecar as `<subcard-key>.portrait.json` (the key is already
    # safe-name encoded); try that first, then a defensive safe_name() re-encoding.
    names = [key + '.portrait.json']
    try:
        from safe_filename import safe_name
        alt = safe_name(key) + '.portrait.json'
        if alt not in names:
            names.append(alt)
    except Exception:
        pass
    return [os.path.join(input_dir, n) for n in names]


def portrait_source_senses(input_dir, key):
    """Read the declared `source_senses` for a sub-card from its input portrait sidecar
    (`<input_dir>/<key>.portrait.json`), or None when the sidecar is absent or predates
    the H920 enrichment. None means "no expected count available" — the guard then makes
    no claim (conservative: never a false shortfall)."""
    if not input_dir:
        return None
    for path in _portrait_paths(input_dir, key):
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding='utf-8') as f:
                port = json.load(f)
        except (OSError, ValueError):
            return None
        for entry in (port if isinstance(port, list) else [port]):
            if isinstance(entry, dict) and entry.get('source_senses') is not None:
                return entry.get('source_senses')
        return None
    return None


def scan_sense_shortfall(results, input_dir):
    """Deterministic SAN-LOSS scan over a window's translated results.

    For every result row that produced a card, compare the input portrait's declared
    `source_senses` to the card's output sense count; a shortfall is a whole-dropped
    sense the accept() <ls>/{# guard is blind to. Null cards (card is None) are left to
    the existing null-requeue path. Returns a list of
    {key, expected, actual, dropped} dicts, one per short card (empty when clean)."""
    short = []
    for row in results or []:
        if not isinstance(row, dict):
            continue
        key = row.get('key')
        card = row.get('card')
        if not key or not isinstance(card, dict):
            continue
        expected = portrait_source_senses(input_dir, key)
        if expected is None:
            continue
        dropped = sense_shortfall(card, expected)
        if dropped > 0:
            short.append({'key': key, 'expected': int(expected),
                          'actual': output_sense_count(card), 'dropped': dropped})
    return short


def _selftest():
    # darvI evidence: 3-sense PW source -> count 3.
    darvi = ('=== LAYER: PW ===\n\n{T1} und {T2}¦ {T3}\n'
             '{T6}— 1〉 {%Löffel%}.\n'
             '{T7}— 2〉 {%die Haube einer Schlange%}.\n'
             '{T8}— 3〉 {T4} {T5} eines Landes.')
    assert count_source_senses(darvi) == 3, count_source_senses(darvi)
    # aklizwa pwkvn: single `3〉` supplement sense -> 1 (keyed to PW sense 3, not senses 1-3).
    akl = '{#aklizwa#}¦ 3〉 {%keine Pein verursachend%} <ls>KAP. 2,33</ls>.'
    assert count_source_senses(akl) == 1, count_source_senses(akl)
    # unnumbered adjective supplement -> 0 (nothing to compare).
    asakta = '{#aSakta#}¦ <lex>Adj.</lex> {%nicht könnend%} <ls n="Chr.">94,27</ls>.'
    assert count_source_senses(asakta) == 0, count_source_senses(asakta)
    # citation numbers must NOT be counted as senses (no bare `〉`).
    assert count_source_senses('<ls>MBH. 5,163,4</ls>. 2,33 1,5') == 0
    # line-anchored N) form (split_plan notation).
    assert count_source_senses('1) a\n2) b\n3) c') == 3
    # H960 cross-reference FP regression (real promoted-store shapes, verify evidence):
    # a mid-prose ordinal points into ANOTHER entry's numbering and must NOT be counted.
    # gam~~h2_31_pari: one addendum sense whose prose cross-refs the base numbering -> 1.
    assert count_source_senses('pari 5〉 {%...%}, gehört zu 4〉.') == 0, \
        count_source_senses('pari 5〉 {%...%}, gehört zu 4〉.')
    # s_ud~~h0_05_pra: two line-opening senses, each cross-referencing the base root -> 2.
    assert count_source_senses('— 1〉 = {#sUd#} 3〉\n— 2〉 = {#sUd#} 4〉') == 2, \
        count_source_senses('— 1〉 = {#sUd#} 3〉\n— 2〉 = {#sUd#} 4〉')
    # _a_srayatva (main lane): one unnumbered abstract-noun sense that cross-refs 1〉/6〉 -> 0.
    assert count_source_senses('Nom. abstr. zu {#ASraya#} 1〉 und 6〉.') == 0, \
        count_source_senses('Nom. abstr. zu {#ASraya#} 1〉 und 6〉.')
    # shortfall math: darvI-shaped card (2 of 3 senses).
    card2 = {'records': [{'senses': [{'tag': '2'}, {'tag': '3'}]}]}
    assert sense_shortfall(card2, 3) == 1
    assert sense_shortfall(card2, 2) == 0
    assert sense_shortfall(card2, None) == 0
    assert output_sense_count(card2) == 2
    print('sense_count selftest OK')


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    _selftest()
