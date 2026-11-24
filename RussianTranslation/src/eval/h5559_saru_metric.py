#!/usr/bin/env python
"""h5559_saru_metric.py -- metric definition for the H5559 Sa->Ru prompt Evaluate
harness (fidelity-judge + TM-match, IAST exactness + case-government as HARD FAILS).

_Created: 25-11-2026 · Last updated: 25-11-2026_
_Dr. Mārcis Gasūns_

Pure stdlib. NO dspy import, NO network -- this file is the metric CONTRACT and is
offline-green under a bare python3. The judge prompt text lives here; the judge CALL
lives in h5559_dspy_evaluate_harness.py (the only file with a dspy dependency).

Metric per example
------------------
  hard_fail  = iast_exactness_fail OR case_government_fail   -> score 0 (gated to zero)
  score      = 0.5 * fidelity + 0.5 * tm_match                (fidelity in {0,1})
  aggregate  = mean(score) over the devset

Component definitions
---------------------
* tm_match   Dice coefficient over Russian content tokens, house rule from
             src/eval/bli_eval.py (Cyrillic runs len>=4, lowercased): the same
             token shape that already produces P@1/MRR in this repo, so BLI
             numbers stay comparable across harnesses.
* fidelity   binary LLM judge verdict (JUDGE_PROMPT below, temp 0, batched):
             is the candidate a faithful Russian equivalent of the Sanskrit
             input, given the frozen gold pair as reference?
* iast_exactness (HARD FAIL) any Latin token in the prediction that either
             carries IAST diacritics or strips to an input token MUST be
             byte-identical to an input token. Catches diacritic-stripped
             mangling (yuvānam -> yuvanam) and invented transliterations --
             errors a semantic metric cannot see.
* case_government (HARD FAIL) if the gold equivalent GOVERNS with a Russian
             preposition (gold first token in GOV_PREPS), the prediction must
             govern in the SAME preposition slot (в/во, к/ко, с/со, о/об/обо
             are one slot each). A wrong governing preposition is a wrong case
             relation, i.e. a grammatical error, not a paraphrase -- hence a
             hard fail, not a partial score.

Why semantic-F1 alone is banned (recorded here so no consumer re-litigates it):
semantic similarity rewards fluent-but-wrong Russian -- a wrong-sense gloss of a
frequent headword scores high on embedding overlap while being unusable as a
dictionary equivalent, and it scores 1.0 on IAST mangling and wrong case
government, which carry zero semantic signal. Goodharting that number is exactly
the failure mode already ruled against in DECISIONS_PWG_RU_QUALITY_BAR.md and
H5555's metric note: fidelity-judge + TM-match with hard fails gates the fluent
mistranslations that semantic-F1 alone waves through.

Data fence: BLI gold pairs only; no personal data enters this metric.
"""
import re
import unicodedata

CONTENT_RE = re.compile(r'[а-яёА-ЯЁ]{4,}')
LATIN_RE = re.compile(r'[A-Za-z]+')
IAST_DIACRITICS = set('āīūṛṝḷṃḥśṣṭḍṇñṅĀĪŪṚṜḶṂḤŚṢṬḌÑṄ')
INPUT_SPLIT_RE = re.compile(r'[\s\-]+')

# Russian content tokens, house rule (bli_eval.py): len>=4, lowercased.
def ru_tokens(text):
    return {t.lower().replace('ё', 'е') for t in CONTENT_RE.findall(text or '')}


def tm_match(pred, gold):
    """Dice over Cyrillic content tokens. 0.0 when either side is empty."""
    p, g = ru_tokens(pred), ru_tokens(gold)
    if not p or not g:
        return 0.0
    return 2.0 * len(p & g) / (len(p) + len(g))


def _strip_iast(tok):
    decomposed = unicodedata.normalize('NFD', tok.lower())
    return ''.join(c for c in decomposed if not unicodedata.combining(c))


def iast_exactness_fail(pred, sa_input):
    """True iff the prediction contains a Latin token that looks like (a stripped
    form of) the Sanskrit input but is not byte-identical to an input token."""
    # hyphenated input compounds count piecewise: sarva-bhūteṣu owns both halves
    input_tokens = {t for t in INPUT_SPLIT_RE.split(sa_input or '') if t}
    input_stripped = {_strip_iast(t) for t in input_tokens}
    for tok in LATIN_RE.findall(pred or ''):
        has_iast = any(c in IAST_DIACRITICS for c in tok)
        stripped = _strip_iast(tok)
        looks_like_input = stripped in input_stripped
        if (has_iast or looks_like_input) and tok not in input_tokens:
            # allow multi-token input pieces joined by hyphen in input to appear
            # only byte-exact; anything else with IAST signal is a mangling.
            if looks_like_input or has_iast:
                return True
    return False


# Preposition government slots (hard-fail vocabulary).
_SLOT = {
    'в': 'v', 'во': 'v',
    'к': 'k', 'ко': 'k',
    'с': 's', 'со': 's',
    'о': 'o', 'об': 'o', 'обо': 'o',
}
GOV_PREPS = set(_SLOT) | {
    'на', 'при', 'над', 'под', 'между', 'через', 'перед', 'за', 'из',
    'до', 'от', 'для', 'по', 'у', 'про', 'без',
}


def _first_token(text):
    for t in (text or '').lower().replace('ё', 'е').split():
        return t.strip('.,;:!?()""')
    return ''


def case_government_fail(pred, gold):
    """True iff gold governs with a preposition and the prediction does not govern
    in the same slot. No gold preposition -> no constraint (pass)."""
    g = _first_token(gold)
    if g not in GOV_PREPS:
        return False
    p = _first_token(pred)
    if p not in GOV_PREPS:
        return True  # gold governs, prediction does not
    return _SLOT.get(g, g) != _SLOT.get(p, p)


def score_example(pred, sa_input, gold_ru, fidelity):
    """Deterministic composite. fidelity: 0/1 (or None -> treated as 0 by caller
    only after judge phase; evaluate-phase caller must pass an int)."""
    iast_fail = iast_exactness_fail(pred, sa_input)
    case_fail = case_government_fail(pred, gold_ru)
    hard = iast_fail or case_fail
    tm = tm_match(pred, gold_ru)
    fid = float(fidelity or 0)
    score = 0.0 if hard else (0.5 * fid + 0.5 * tm)
    return {
        'tm_match': round(tm, 4),
        'fidelity': fid,
        'iast_fail': iast_fail,
        'case_fail': case_fail,
        'hard_fail': hard,
        'score': round(score, 4),
    }


JUDGE_PROMPT = """Ты — судья качества словарных эквивалентов санскрит->русский.
Даны: санскритское слово/словосочетание (IAST), золотой русский эквивалент (эталон)
и кандидат — русский эквивалент, выданный моделью. Ответь 1, если кандидат является
верным русским эквивалентом входа (подходил бы как словарная глосса: верный смысл,
допустимая лексика, не выдуманный), и 0, если неверный смысл, галлюцинация,
нерелевантный перевод или пустой ответ. Оценивай по входу, эталон — только
навигационная опора. Отвечай СТРОГО JSON-массивом объектов
[{"id": <число>, "score": 0|1, "reason": "<короткая причина>"}] для всех элементов
пакета, без markdown и пояснений вокруг."""

DELTA = None  # reserved: future weighted variants register here, not ad hoc.
