#!/usr/bin/env python
"""Print the residual (not-fully-English) selected_keys for a root's EN store.

  python src/pilot/en_residual_keys.py <root>

A key is "done" iff EVERY translation slot in its card carries a non-empty
`english` — coverage-complete, not merely ">=1 English sense". The old ">=1"
rule counted a 1/40-sense card as done and hid 39 untranslated senses (FL4;
same class as ru_coverage's per-root denominator idea, applied within a card).
The denominator is the card's own senses that carry a German source side (each
is a slot that must be translated); the numerator is those that also carry
English. Prints comma-joined missing keys (LF, no trailing CR) to stdout so a
requeue can `--keys="$(python ... <root>)"`. Empty output => root at 100%.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


def en_coverage(card):
    """(english_slots, total_slots) for a card. A slot = a sense carrying a German source
    side (what must be translated) OR an English side already. A card with no records/senses
    (or a null card) has 0 slots."""
    if not card or not card.get("records"):
        return 0, 0
    total = eng = 0
    for r in card["records"]:
        for s in r.get("senses", []):
            if s.get("german") or s.get("english"):
                total += 1
                if s.get("english"):
                    eng += 1
    return eng, total


def card_done(card):
    """Coverage-complete: at least one slot and every slot has English. A null card, an
    empty card, or a partially-translated card (e.g. 1/40) is NOT done."""
    eng, total = en_coverage(card)
    return total > 0 and eng == total


def missing(root):
    path = os.path.join(REPO, f"wf_output.en.{root}.json")
    if not os.path.exists(path):
        sys.exit(f"no store: {path}")
    d = json.load(open(path, encoding="utf-8"))
    have = {e["key"] for e in d["results"] if card_done(e.get("card"))}
    return [k for k in d["meta"]["selected_keys"] if k not in have]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: en_residual_keys.py <root>")
    print(",".join(missing(sys.argv[1])), end="")
