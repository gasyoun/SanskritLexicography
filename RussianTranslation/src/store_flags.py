#!/usr/bin/env python
"""One definition of "is this store row machine-clean" — shared by the batch driver
and by every release gate that asks the same question.

Why this module exists (H215 / issue #1712, 14-08-2026). The pwg_ru store used to
carry three per-row boolean flags stamped by the batch validator: `ok`,
`placeholders_ok`, `key_match`. The merged/promoted pipeline stopped writing them —
promoted sense-level rows survive the deterministic promote path instead, and merged
rows never used the `{Tn}` placeholder skeleton — so on the live store all three are
*absent* on all 11 603 rows, not False.

`run_batch.py` adapted: it grew `_row_key_match` / `_row_placeholders_ok` fallbacks
that read the legacy flag when present and fall back to the structural evidence when
it is not. The two release gates did not: they kept the raw

    row.get('ok') and row.get('placeholders_ok') and row.get('key_match')

conjunction, which on the current schema is unsatisfiable. G5 therefore reported
`print_ready=0` and stayed blocked no matter how many rows a human approved — three
rows were already `review_status='approved'` and still scored zero. That read for
weeks as a human review backlog; it was a schema-drift bug.

Keeping the predicate in one place is the actual fix. `test_store_flags.py` pins it
against a row shaped like the live store, so the same drift fails a test instead of
silently blocking a release.
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from sanskrit_util import classify_german_metalanguage  # canonical shim (H2876)

PRINT_READY_STATUSES = {'approved', 'human_reviewed'}


def row_key_match(row):
    """True when the row's key binding is sound.

    Legacy rows carry the batch `key_match` flag. Promoted sense-level rows have
    already survived the deterministic promote path and no longer carry it, so their
    key binding is evidenced by `key1` + `subcard`.
    """
    if row.get('key_match') is not None:
        return bool(row.get('key_match'))
    return bool(row.get('key1') and row.get('subcard'))


def row_placeholders_ok(row):
    """True when placeholder integrity holds.

    Merged-pipeline rows do not use the old `{Tn}` placeholder skeleton, so absence
    of the legacy flag is neutral rather than a validation failure; a non-empty `ru`
    is the evidence that the row rendered.
    """
    if row.get('placeholders_ok') is not None:
        return bool(row.get('placeholders_ok'))
    return bool(row.get('ru'))


def machine_ok(row):
    """The machine-cleanliness half of print-readiness (no human judgment in it)."""
    if row.get('ok') is not None:
        return bool(row.get('ok') and row_placeholders_ok(row) and row_key_match(row))
    return bool(row_placeholders_ok(row) and row_key_match(row))


def is_print_ready(row):
    """A store row a human has passed AND the machine considers clean.

    This is the G5 predicate. Call it — never re-inline the flag conjunction, which
    is how the two gates drifted from the store schema in the first place.
    """
    return row.get('review_status') in PRINT_READY_STATUSES and machine_ok(row)


# ---- H2876: German apparatus metalanguage must never be rendered as gloss ----
# H2787's independent n=400 gate measured arm B's dominant serious-error class:
# German grammatical apparatus (`eines`, `im Comp. vorangehend`, `so`,
# `Ergänzung`) read as ordinary prose and "translated" (`{%eines%}` →
# «поручать кому-л.», `{%die%}` → «боги») — invisible to the `{Tn}` placeholder
# gate because the span IS legal German text. The detector is the canonical
# sanskrit-util classify_german_metalanguage (via the src/sanskrit_util.py shim);
# this module only owns the ROW predicate, not a second token table.

_GM_LETTERS = re.compile('[A-Za-zäöüßÄÖÜ]')


def row_apparatus_as_gloss(row):
    """True when the row's DE source is pure apparatus metalanguage but the RU
    field renders it as an ordinary gloss (the H2787 arm-B defect class).

    "Pure apparatus" = classify_german_metalanguage spans cover every letter of
    the DE source (an `uncertain` span counts as apparatus per the H2876 fence:
    treat as not-gloss, log). A mixed source (apparatus + real prose) is NOT
    flagged here — only whole-span apparatus reused as a translation unit is.
    """
    de = (row.get('de') or row.get('source_string') or '').strip()
    ru = (row.get('ru') or row.get('target_string') or '').strip()
    if not de or not ru:
        return False
    spans = classify_german_metalanguage(de)
    if not spans:
        return False
    residue = list(de)
    for sp in spans:
        for i in range(sp['start'], sp['end']):
            residue[i] = ' '
    if _GM_LETTERS.search(''.join(residue)):
        return False                       # real prose remains — not pure apparatus
    for sp in spans:
        if sp['category'] == 'uncertain':
            print('store_flags: uncertain metalanguage %r treated as not-gloss '
                  '(key1=%s)' % (sp['text'], row.get('key1')), file=sys.stderr)
    return True


def row_metalanguage_ok(row):
    """The gate-facing form: False exactly when row_apparatus_as_gloss(row)."""
    return not row_apparatus_as_gloss(row)
