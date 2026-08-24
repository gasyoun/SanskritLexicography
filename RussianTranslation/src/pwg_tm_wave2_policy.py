#!/usr/bin/env python
"""H2721 — apply H2686 Track D defaults to the next 5,000-headword wave.

Wave 1 bytes stay immutable. This module is the named policy the generator,
source lexicon, retriever, and priority queue consult. It does not rewrite
promoted or quarantined Wave-1 fragments.

  python src/pwg_tm_wave2_policy.py --selftest
"""
from __future__ import annotations

import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_canonical as C  # noqa: E402

WAVE = 2
WAVE1_IMMUTABLE = True
POLICY_ID = 'pwg.tm.wave2.defaults.v1'
H2686_RECEIPT = (
    'https://github.com/gasyoun/SanskritLexicography/blob/master/'
    'RussianTranslation/pwg_ru/PWG_TM_SEMANTIC_QE_RETRIEVAL_W2_14-08-2026.md'
)

# Measurement QE only. Production tm_grade --qe default stays proxy.
QE_MEASUREMENT_BACKEND = 'deepseek'
QE_MEASUREMENT_MODEL = 'deepseek-v4-flash'
RETRIEVER = 'char4gram'

# Per-class TM *context* (fuzzy neighbours in the prompt). Exact compatible
# address reuse is separate and still allowed except on the denylist.
TM_CONTEXT = {
    'recurring_formula': 'auto_fuzzy',
    'definition_gloss': 'advisory',
    'sense': 'off',
    'citation': 'exact_only',
    'example': 'exact_only',
    'grammar_label': 'exact_only',
}

# H2684 independent-gate serious-error class: unsafe short-gloss source reuse.
# Inner text of {%...%} or a bare token, lowercased.
# H3434 wave-3: R15 gate convicted bare function-word spans ({%an%} x7,
# {%einen%} x2, …) re-entering via exact-source reuse. Every added token is a
# pure German function word / article / pronoun slot admitted from the
# tracked-corpus census (canonical.v1.jsonl source-side spans; see
# wave3_receipt/denylist_census.json for the full measured table).
SHORT_GLOSS_DENYLIST = frozenset({
    'jmd', 'jmdm', 'jmdn', 'jemand',
    'die', 'der', 'das', 'den', 'dem', 'des',
    'gewachsen',
    'etwas', 'ein', 'einen', 'eine', 'sich', 'man', 'nicht',
    'als', 'und', 'oder', 'wie',
    'am', 'ans', 'im', 'in', 'zum', 'zur',
    'an', 'auf', 'aus', 'bei', 'bis', 'durch', 'für', 'gegen',
    'mit', 'nach', 'ohne', 'über', 'um', 'unter', 'von', 'vor',
    'zu', 'vom', 'beim',
})

_INNER = re.compile(r'\{%\s*(.*?)\s*%\}', re.S)
_STRIP = re.compile(r'[^a-zA-ZäöüÄÖÜß]+')


def source_token(source_string):
    src = (source_string or '').strip()
    if not src:
        return ''
    m = _INNER.search(src)
    core = (m.group(1) if m else src).strip().lower()
    core = _STRIP.sub('', core)
    return core


def is_denied_short_gloss(source_string):
    return source_token(source_string) in SHORT_GLOSS_DENYLIST


def tm_context_mode(fragment_class):
    return TM_CONTEXT.get(fragment_class or '', 'advisory')


def allow_fuzzy_context(fragment_class):
    return tm_context_mode(fragment_class) in ('auto_fuzzy', 'advisory')


def allow_exact_source_reuse(source_string, fragment_class=None):
    if is_denied_short_gloss(source_string):
        return False
    if fragment_class == 'sense':
        return False
    return True


def filter_context(card, hits):
    """Drop context the wave-2 policy forbids. Exact hits still pass unless
    the source is denylisted or the class is sense."""
    klass = (card or {}).get('fragment_class')
    mode = tm_context_mode(klass)
    if mode == 'off':
        return []
    out = []
    for hit in hits or []:
        if isinstance(hit, str):
            if mode == 'exact_only':
                continue
            out.append(hit)
            continue
        src = hit.get('source_string') or ''
        kind = hit.get('retrieve_kind')
        if is_denied_short_gloss(src):
            continue
        if mode == 'exact_only' and kind != 'exact':
            continue
        out.append(hit)
    return out


def load_wave1_keys(path=None):
    path = path or os.path.join(C.DEFAULT_OUT_DIR, 'priority_5000.jsonl')
    if not os.path.exists(path):
        return []
    return [row['k1'] for row in C.read_jsonl(path) if row.get('k1')]


def selftest():
    assert WAVE1_IMMUTABLE
    assert QE_MEASUREMENT_BACKEND == 'deepseek'
    assert QE_MEASUREMENT_BACKEND != 'comet'
    assert is_denied_short_gloss('{%Jmd%}')
    assert is_denied_short_gloss('{%die%}')
    assert is_denied_short_gloss('{%gewachsen%}')
    # H3434 wave-3 additions: bare function-word spans stay unfilled
    assert is_denied_short_gloss('{%an%}')
    assert is_denied_short_gloss('{%einen%}')
    assert is_denied_short_gloss('{%Etwas%}')
    assert is_denied_short_gloss('{%sich%}')
    assert is_denied_short_gloss('{%zu%}')
    assert not is_denied_short_gloss('{%Feuer, Gott des Feuers.%}')
    assert not allow_exact_source_reuse('{%Jmd%}', 'definition_gloss')
    assert allow_exact_source_reuse('{%Feuer.%}', 'definition_gloss')
    assert not allow_exact_source_reuse('{%Feuer.%}', 'sense')
    assert allow_fuzzy_context('recurring_formula')
    assert allow_fuzzy_context('definition_gloss')
    assert not allow_fuzzy_context('sense')
    assert tm_context_mode('citation') == 'exact_only'
    kept = filter_context(
        {'fragment_class': 'sense'},
        [{'source_string': 'gehen', 'retrieve_kind': 'char4gram'}])
    assert kept == []
    kept = filter_context(
        {'fragment_class': 'citation'},
        [{'source_string': '<ls>X</ls>', 'retrieve_kind': 'char4gram'},
         {'source_string': '<ls>X</ls>', 'retrieve_kind': 'exact'}])
    assert len(kept) == 1 and kept[0]['retrieve_kind'] == 'exact'
    print('pwg_tm_wave2_policy selftest OK — denylist, sense off, formula fuzzy')
    return 0


def main(argv=None):
    ap_ok = argv is None or argv == ['--selftest'] or (argv and argv[0] == '--selftest')
    if not ap_ok and argv:
        print('usage: pwg_tm_wave2_policy.py --selftest')
        return 2
    return selftest()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
