#!/usr/bin/env python
"""Shared, --lang-parameterized card-coverage kernel (the FL4 "coverage-complete" rule).

Single source for "is every translatable slot of a card filled in language L?", so the rule
cannot be implemented once per language and drift (H1425 W1). `field` is the per-sense target
field name: 'russian' or 'english'. A slot = a sense carrying a German source side (what MUST be
translated) OR a target side already; a card is done iff it has >=1 slot and EVERY slot carries
`field` — NOT the old ">=1 translated sense" rule, which counted a 1/40-sense card as done and hid
39 untranslated senses (FL4). Lang-symmetric by construction: the exact same function serves both.

Consumed by en_residual_keys.py (field='english'). ru_coverage.py measures a DIFFERENT, coarser
thing — per-root sub-card PRESENCE in the store — and does not yet apply this per-slot rule, so it
retains the FL4 blindspot this kernel fixes (wiring it in is a tracked H1425 follow-up).
"""


def slot_coverage(card, field):
    """(translated_slots, total_slots) for one card in language `field`. Null/empty card -> (0, 0)."""
    if not card or not card.get('records'):
        return 0, 0
    total = done = 0
    for rec in card.get('records') or []:
        for sense in rec.get('senses') or []:
            if sense.get('german') or sense.get(field):
                total += 1
                if sense.get(field):
                    done += 1
    return done, total


def card_done(card, field):
    """Coverage-complete in `field`: >=1 slot AND every slot carries a non-empty target (FL4)."""
    done, total = slot_coverage(card, field)
    return total > 0 and done == total
