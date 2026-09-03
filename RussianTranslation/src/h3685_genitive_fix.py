#!/usr/bin/env python
"""H3685 - manual Russian rewording of the 3 pwg_ru genitive-leak rows left
open by H3500 (src/h3500_defect_scan.py class2_is_genitive_leaks).

Each row's German source (`de` field, NEVER touched) uses a genuine German
genitive apostrophe-s ("Arjuna's", "Savitar's", "Indra's"); the Russian
translation pass left that span untranslated instead of rendering a Russian
genitive, so a bare English possessive leaked into `ru`. The replacement
below re-derives the Russian wording directly from the surrounding `de`
context (not invented inflection) and only touches the flagged span:

  di_s~~h0_22_samud  "wodurch sie die Schwiegertochter Arjuna's wurde, 489."
                     -> "...она стала невесткой Арджуны, 489."
  su~~h1_00_pwg00    "(von Savitar's Wirkung)"
                     -> "(о воздействии Савитара)" (natural RU noun+genitive
                        order; German has genitive-noun order)
  vad~~h0_08_anu     "Laṅkā erklang wie Indra's Stadt"
                     -> "...звучал подобно городу Индры" (same reorder)

Exact-substring match against the known BEFORE text guards against silent
corruption if the store has drifted since H3500/H3685 were written - the
script refuses (exit 1) rather than fuzzy-patching.

H4040 (04-09-2026): ``--write`` no longer rewrites the store with a raw
tmp+``os.replace`` — it routes through ``store_write.locked_store_rewrite``
(the H2146 lock: PromoteClaim across the read-guard-write window, unique
fsynced backup, atomic LF-only replace), and the default store resolves
through ``store_path.canonical_store`` so a worktree run never writes a
worktree-local copy (H255 loss mode).

  python src/h3685_genitive_fix.py [STORE] [--write] [--ledger PATH]
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from store_path import canonical_store  # noqa: E402
from store_write import locked_store_rewrite  # noqa: E402

DEFAULT_STORE = canonical_store(os.path.join(HERE, "pwg_ru_translated.jsonl"))
DEFAULT_LEDGER = os.path.join(HERE, "h3685_genitive_fix_ledger.jsonl")

# (key1, subcard, sense_tag) -> (before_substring, after_substring)
FIXES = {
    ("diS", "di_s~~h0_22_samud", "2"): (
        "стала невесткой\n<is>Arjuna's</is> 489.",
        "стала невесткой <is>Арджуны</is>, 489.",
    ),
    ("su", "su~~h1_00_pwg00", "3."): (
        "(о <is>Savitar's</is> воздействии)",
        "(о воздействии <is>Савитара</is>)",
    ),
    ("vad", "vad~~h0_08_anu", "1"): (
        "{%звучал подобно%} <is>Indra's</is> {%городу%}",
        "{%звучал подобно%} {%городу%} <is>Индры</is>",
    ),
}


def repair(rows):
    events = []
    by_key = {}
    for i, r in enumerate(rows):
        by_key[(r.get("key1"), r.get("subcard"), r.get("sense_tag"))] = i

    for target, (before, after) in FIXES.items():
        idx = by_key.get(target)
        if idx is None:
            raise SystemExit(f"REFUSING: row not found for {target} - "
                              "store has drifted since this fix was written")
        ru = rows[idx].get("ru") or ""
        if before not in ru:
            raise SystemExit(f"REFUSING: expected BEFORE text not found in "
                              f"{target} - store has drifted, inspect "
                              "manually before re-running")
        if ru.count(before) != 1:
            raise SystemExit(f"REFUSING: BEFORE text is not unique in "
                              f"{target} ({ru.count(before)} occurrences)")
        new_ru = ru.replace(before, after)
        events.append({
            "key1": target[0], "subcard": target[1], "sense_tag": target[2],
            "before": before, "after": after,
        })
        rows[idx] = dict(rows[idx])
        rows[idx]["ru"] = new_ru
    return rows, events


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("store", nargs="?", default=DEFAULT_STORE)
    ap.add_argument("--write", action="store_true",
                    help="mutate the store (default: dry run)")
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    args = ap.parse_args()

    with io.open(args.store, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]

    repaired, events = repair(list(rows))
    print(json.dumps({"store": args.store, "fixes_applied": len(events),
                      "mode": "write" if args.write else "dry-run"},
                     ensure_ascii=False, indent=1))
    for e in events:
        print(f"  {e['key1']} {e['subcard']} {e['sense_tag']!r}: "
              f"{e['before']!r} -> {e['after']!r}")

    if args.write:
        # H4040: the H2146 lock (PromoteClaim + unique fsynced backup + atomic
        # replace) replaces the raw tmp+os.replace write. sort_keys is kept so
        # the payload bytes stay identical to the historical serialization.
        locked_store_rewrite(
            args.store, repaired, tag='h3685',
            serialize=lambda row: json.dumps(row, ensure_ascii=False,
                                             sort_keys=True))
        with io.open(args.ledger, "w", encoding="utf-8", newline="\n") as f:
            for e in events:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        print(f"WROTE {args.store}; ledger -> {args.ledger}")
    else:
        print("dry run: no changes written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
