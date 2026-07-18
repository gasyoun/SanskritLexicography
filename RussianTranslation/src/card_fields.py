#!/usr/bin/env python
r"""Single source of truth for WHICH final-card fields are masked, restored and promoted.

WHY THIS EXISTS (H963 correction packet, C-01)
----------------------------------------------
`restore_card` (`pilot/headless_worker.py`) and its JS twin `restoreCard`
(`pilot/gen_opt_harness2.py`) unmasked THREE things -- `record.grammar`, `sense.german` and
the per-sense translation field. The promote path (`promote_final_cards.rows_for`) read SIX
-- `card.iast`, `record.h`, `sense.tag`, `sense.russian`, `sense.german`,
`sense.differentia`. The two lists were authored independently, and they drifted: four
fields were promoted to the canonical store with their `{Tn}` placeholders never restored.

The observed cost, measured against the 11,605-row store: 670 rows carry a raw `{Tn}`
(`sense_tag` 376, `h` 223, `differentia` 72, plus the 2 C-42 rows in `ru`/`de`) -- including
223 rows whose HEADWORD reads literally `{T104}`. Nothing failed loudly, because the only
component that encodes the record contract never runs on live output (C-04).

The defect was not a *wrong* list. It was TWO lists. So this module holds ONE, and both the
restore side and the promote side are driven from it;
`window_selftest.test_restore_covers_every_promoted_field` asserts
PROMOTED subset-of RESTORED **by construction from this constant**, so they cannot drift apart
again. A new promoted field that nobody remembers to restore is now a test failure, not 670
silently corrupted rows.

LEVELS
------
Each entry is a `(level, name)` pair naming where the field sits in a final card:

    card    -> card[name]
    record  -> card['records'][i][name]
    sense   -> card['records'][i]['senses'][j][name]

THE TRANSLATION FIELD IS LANGUAGE-DEPENDENT
-------------------------------------------
`gen_opt_harness2.py:890` picks `field = 'english' if lang == 'en' else 'russian'`, so the
per-sense target field is a parameter, not a constant. Everything else is fixed. Callers pass
the active `field`; `german` is always restored (it is the source-side gloss the fidelity
guards compare against) and is de-duplicated when it *is* the target field.

NOT A SCHEMA
------------
`schemas/pwg_ru_final_card.schema.json` states the *contract* (`record.required =
{h, grammar, senses}`). This module states which fields carry `{Tn}` placeholders and must
therefore be unmasked before promotion. They are related but distinct: `senses` is required
by the schema and is not a masked text field.
"""
import json

# Card-level masked fields.
CARD_MASKED = ('iast',)

# Record-level masked fields. `h` is the homonym discriminator -- free lexicographic text
# ("2. bhid", "PW 3 (с anu, отсылка к entry 5)"), NOT a mechanical function of the key, which
# is why a lost `h` cannot be synthesised later (C-02's boundary forbids exactly that).
RECORD_MASKED = ('h', 'grammar')

# Sense-level masked fields that do not depend on the target language.
SENSE_MASKED_COMMON = ('tag', 'german', 'differentia')

# What the promote path reads out of a card and writes to a store row, EXCLUDING the
# target-language field (which `promoted_pairs` appends). Stated independently of the restore
# list on purpose: the selftest then compares two separately-authored facts rather than
# tautologically comparing a list to itself.
PROMOTED_COMMON = (
    ('card', 'iast'),
    ('record', 'h'),
    ('sense', 'tag'),
    ('sense', 'german'),
    ('sense', 'differentia'),
)


def promoted_pairs(field='russian'):
    """Every `(level, name)` the promote path reads for target-language field `field`.

    `field='russian'` is exactly `promote_final_cards.rows_for`; `field='english'` is its
    `promote_en` counterpart. Language-parameterised rather than hardcoded, so the RU and EN
    lanes cannot acquire two different answers to "what gets promoted" -- which is the same
    class of drift as C-01 itself.
    """
    pairs = list(PROMOTED_COMMON)
    if field and ('sense', field) not in pairs:
        pairs.append(('sense', field))
    return tuple(pairs)


# Backwards-compatible alias for the RU store's promote path.
PROMOTED_PAIRS = promoted_pairs('russian')


# C-17: the masked fields whose {Tn} tokens must MATCH the source skeleton for a card to pass the
# fragment-fidelity guard. This is the SOURCE-mirror subset -- the model echoes the German
# skeleton's placeholders back into `record.grammar` and `sense.german`; the output-only fields
# (h/iast/tag/differentia) are not in the skeleton and must NOT enter the multiset. Python
# `card_token_multiset` and JS `cardTokens` both derive from this one tuple, so they cannot drift
# (the C-17 defect: Python omitted `grammar` while JS included it -> a grammar-{Tn} card was
# fidelity-rejected on the Python/headless lane and accepted on JS).
TOKEN_FIDELITY_FIELDS = (('record', 'grammar'), ('sense', 'german'))


def js_token_fidelity_spec():
    """`TOKEN_FIDELITY_FIELDS` as a JSON literal, for interpolation into the JS harness."""
    return json.dumps({
        'record': [n for lvl, n in TOKEN_FIDELITY_FIELDS if lvl == 'record'],
        'sense': [n for lvl, n in TOKEN_FIDELITY_FIELDS if lvl == 'sense'],
    })


def sense_masked(field):
    """Sense-level masked fields for target-language field `field` (e.g. 'russian')."""
    out = list(SENSE_MASKED_COMMON)
    if field and field not in out:
        out.append(field)
    return tuple(out)


def restored_pairs(field):
    """Every `(level, name)` that MUST be unmasked before a card may be promoted."""
    return (tuple(('card', f) for f in CARD_MASKED)
            + tuple(('record', f) for f in RECORD_MASKED)
            + tuple(('sense', f) for f in sense_masked(field)))


def js_restore_spec(field):
    """The same field set as a JSON literal, for interpolation into the JS harness.

    The JS lane cannot import Python, so the constant is INTERPOLATED into it rather than
    duplicated by hand -- duplicating it by hand is the original defect.
    """
    return json.dumps({
        'card': list(CARD_MASKED),
        'record': list(RECORD_MASKED),
        'sense': list(sense_masked(field)),
    })


def restore_card_fields(card, field, restore_text):
    """Unmask every field in `restored_pairs(field)`, in place, via `restore_text`.

    `restore_text` is injected (rather than imported) so the caller keeps ownership of the
    placeholder map and of what an out-of-range `{Tn}` means (C-42).
    """
    pairs = restored_pairs(field)
    card_fields = [n for lvl, n in pairs if lvl == 'card']
    record_fields = [n for lvl, n in pairs if lvl == 'record']
    sense_fields = [n for lvl, n in pairs if lvl == 'sense']

    for name in card_fields:
        if isinstance(card.get(name), str):
            card[name] = restore_text(card[name])
    for record in card.get('records') or []:
        for name in record_fields:
            if isinstance(record.get(name), str):
                record[name] = restore_text(record[name])
        for sense in record.get('senses') or []:
            for name in sense_fields:
                if isinstance(sense.get(name), str):
                    sense[name] = restore_text(sense[name])
    return card
