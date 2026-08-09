#!/usr/bin/env python
r"""One definition of "where a literal loss-marker scan is allowed to look" (H2253, #1073).

Two gates judge the same cards for the same two defects — [`canary_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/canary_gate.py)
(one synthetic canary window) and [`ci_gate_runner.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/ci_gate_runner.py)
(every ``wf_output*.json`` in a pwg-ru-data PR). H2174 fixed the self-trip in the
first and left the second reading the whole card, so the SAME curated fixture that
the canary gate had just been taught to pass still failed CI. This module exists so
that the next fix cannot land on one side only.

**The two scopes are deliberately different, and must stay different.**

``SAN-LOSS`` / ``UNMAPPED`` are the model's own vocabulary for "I dropped a sense".
The curated canary portrait (`pwg_ru/h994/canary/…portrait.json`) *contains those
literals as prompt input* — it is a silent-SAN-LOSS control — so every real canary
run paraphrases them back into the card's free-text ``notes``. Scanning a whole card
for them therefore makes the gate UNPASSABLE for the one fixture it exists to judge
(observed in H1447 22-07 and H2011 02-08; the H2160 "inert by construction" class,
inverted — always-fail instead of always-pass). So the marker scan reads
**translated content only** and never free-text commentary, at any depth.

``{Tn}`` residue is the opposite kind of defect: an unrestored mask placeholder is a
pipeline bug wherever it survives, including in a note, and no fixture feeds ``{Tn}``
in as prompt input. Its scope is the **whole card**, on purpose. Do not "align" the
two scopes — that symmetry is what a copy-paste would produce, and it would either
re-break the canary or blind the residue check.

Sense loss is still caught for the canary by the sense-count check in
`canary_gate.judge_payload`, which is that fixture's actual detector.
"""
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.dirname(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    # C-01 single source, the same import canary_gate uses. A second literal
    # ``re.compile(r'\{T\d+\}')`` here is exactly the copy-paste this module exists
    # to prevent.
    from promote_final_cards import TN_RE  # noqa: E402
except ImportError:                        # pragma: no cover — standalone/vendored use
    TN_RE = re.compile(r'\{T\d+\}')

LITERAL_MARKERS = ('SAN-LOSS', 'UNMAPPED')
SAN_LOSS_RE = re.compile('|'.join(LITERAL_MARKERS))

#: Free-text keys excluded from the marker scan at ANY depth. These carry human or
#: model commentary ABOUT a card (portrait notes, provenance prose), never the
#: translated content the gate is protecting.
FREE_TEXT_KEYS = ('notes', 'note', 'commentary', 'comment', 'provenance', 'rationale')


def translated_content(card):
    """The card subtree a literal-marker scan may read: ``records`` minus free text.

    ``records``/``senses`` and their target-language strings are the translated
    content. Everything else in a card (``key1``, ``iast``, ``notes``) is input echo
    or commentary. Free-text keys are stripped recursively rather than only at the
    top level, so a future card shape that moves commentary INTO a record cannot
    silently re-open the self-trip.
    """
    def strip(node):
        if isinstance(node, dict):
            return {k: strip(v) for k, v in node.items() if k not in FREE_TEXT_KEYS}
        if isinstance(node, list):
            return [strip(v) for v in node]
        return node
    return strip((card or {}).get('records') or [])


def content_blob(card):
    """Serialized translated content — the marker scan's ONLY input."""
    return json.dumps(translated_content(card), ensure_ascii=False)


def whole_blob(card):
    """Serialized whole card — the ``{Tn}`` residue scan's input (see module docstring)."""
    return json.dumps(card or {}, ensure_ascii=False)


def marker_hits(card):
    """Literal SAN-LOSS/UNMAPPED markers in TRANSLATED CONTENT -> list of markers."""
    blob = content_blob(card)
    return [m for m in LITERAL_MARKERS if m in blob]


def tn_hits(card):
    """Unrestored ``{Tn}`` placeholders anywhere in the card -> list of hits."""
    return TN_RE.findall(whole_blob(card))


def selftest():
    """Pins BOTH directions of #1073: the real false positive and a true positive."""
    # (1) The real canary shape: markers live in free-text notes, content is clean.
    canary = {'key1': 'k', 'notes': 'Synthetic D-Q silent-SAN-LOSS canary card (H994)',
              'records': [{'h': '1', 'senses': [{'tag': 's1', 'russian': 'да',
                                                 'german': 'ja'}]}]}
    assert marker_hits(canary) == [], marker_hits(canary)
    assert tn_hits(canary) == [], tn_hits(canary)

    # (2) TRUE POSITIVE — a marker in translated content still trips. Without this the
    #     fix above would be indistinguishable from deleting the check.
    lost = {'key1': 'k', 'records': [{'senses': [{'tag': 's1', 'russian': 'SAN-LOSS'}]}]}
    assert marker_hits(lost) == ['SAN-LOSS'], marker_hits(lost)
    unmapped = {'records': [{'senses': [{'tag': 's1', 'russian': 'x', 'german': 'UNMAPPED'}]}]}
    assert unmapped and marker_hits(unmapped) == ['UNMAPPED'], marker_hits(unmapped)

    # (3) Free text nested INSIDE a record is excluded too — the scope is recursive.
    nested = {'records': [{'notes': 'flagged SAN-LOSS by the judge',
                           'senses': [{'tag': 's1', 'russian': 'да'}]}]}
    assert marker_hits(nested) == [], marker_hits(nested)
    nested_sense = {'records': [{'senses': [{'tag': 's1', 'russian': 'да',
                                             'note': 'UNMAPPED per judge'}]}]}
    assert marker_hits(nested_sense) == [], marker_hits(nested_sense)

    # (4) {Tn} keeps the WHOLE-CARD scope — including free text, unlike the markers.
    tn_in_notes = {'notes': 'residue {T3} left by the masker',
                   'records': [{'senses': [{'tag': 's1', 'russian': 'да'}]}]}
    assert tn_hits(tn_in_notes) == ['{T3}'], tn_hits(tn_in_notes)
    tn_in_content = {'records': [{'senses': [{'tag': 's1', 'russian': 'x {T9}'}]}]}
    assert tn_hits(tn_in_content) == ['{T9}'], tn_hits(tn_in_content)

    # (5) Empty / malformed cards are inert, never a crash.
    for junk in (None, {}, {'records': None}, {'records': []}):
        assert marker_hits(junk) == [] and tn_hits(junk) == []

    print('marker_scan selftest: PASS (canary false-positive, marker true-positive, '
          'recursive free-text exclusion, {Tn} whole-card scope, malformed-card inertness)')
    return 0


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    sys.exit(selftest())
