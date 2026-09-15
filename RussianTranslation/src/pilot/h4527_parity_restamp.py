#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4527_parity_restamp.py — the H4527 LANG_PARITY re-derivation receipt (same class as
h4861_/h4528_parity_restamp.py).

H4527 (15-09-2026) made the readiness probe spawn with the paid lane's `--safe-mode`:
`max_account_orchestrator._probe_call` now derives the flag from
`headless_worker.resolve_safe_mode({}, claude)` (the lane default, H2251) and records
`cli_safe_mode_effective` on the probe row (`run_observability.ALLOWED` gains that one
boolean). The probe prompt, schema, model, plan mode and the {"ok": true} content check are
untouched. The probe carries no card and reads no target-language field — the RU and EN lanes
share one readiness gate — so every ledger entry that tracks one of the touched files keeps its
SHARED verdict. This driver:

1. appends one dated re-derivation sentence to the note of every entry the check reports as
   drifted (never rewriting an existing sentence);
2. adds the H4527 entry itself (SHARED) if it is not there yet;
3. re-stamps each affected entry through `lang_parity_check.update_hash`, the tool's own
   writer, so the ledger keeps its canonical serialisation.

Idempotent: a second run finds no drift and no missing entry, and writes nothing.
Usage: python src/pilot/h4527_parity_restamp.py
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lang_parity_check as lpc  # noqa: E402

ENTRY_ID = 'probe_safe_mode_h4527'
STAMP = ('H4527 (15-09-2026, Opus 5 `claude-opus-5`): re-derived, SHARED stands. The drift is '
         'the readiness probe adopting the paid lane\'s `--safe-mode` via '
         '`headless_worker.resolve_safe_mode({}, claude)` plus one boolean event field '
         '(`cli_safe_mode_effective`). Spawn-shape only -- no prompt change, no language branch, '
         'no target-language field read; the RU and EN lanes share one readiness probe.')
NEW_ENTRY = {
    'id': ENTRY_ID,
    'mechanism': ('Readiness probe profile surface: `_probe_call` appends `--safe-mode` exactly '
                  'when `headless_worker.resolve_safe_mode({}, claude)` (the paid lane\'s own '
                  'resolver, default ON since H2251) says the lane would, and records '
                  '`cli_safe_mode_effective` on the probe row'),
    'files': [
        'src/pilot/max_account_orchestrator.py',
        'src/pilot/run_observability.py',
    ],
    'languages': ['ru', 'en'],
    'verdict': 'SHARED',
    'note': ('H4527 (15-09-2026, Opus 5 `claude-opus-5`). The probe is language-free by '
             'construction: zero cards, a fixed {"ok": true} schema, and no `--lang` input, so '
             'a Russian and an English window are gated by the byte-identical probe call. The '
             'flag is derived from the same resolver `headless_worker` uses for BOTH lanes\' '
             'generation spawns, so the probe and every lane it gates strip the same profile '
             'surface. Test: max_account_orchestrator_selftest "H4527 probe --safe-mode" pin '
             '(flag present and recorded when the resolver says ON, absent when the CLI lacks '
             'it -- equality with the lane both ways, never a literal).'),
}


def main():
    entries, _text, _span = lpc.load_ledger()
    drifted = sorted({v.split(':', 1)[0] for v in lpc.check(entries)})
    changed = False
    for entry in entries:
        if entry.get('id') in drifted and STAMP not in (entry.get('note') or ''):
            entry['note'] = ((entry.get('note') or '').rstrip() + ' ' + STAMP).strip()
            changed = True
    if not any(e.get('id') == ENTRY_ID for e in entries):
        entries.append(dict(NEW_ENTRY))
        changed = True
    if changed:
        _entries, text, span = lpc.load_ledger()
        block = json.dumps(entries, indent=2, ensure_ascii=False)
        with open(lpc.LEDGER_MD, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(text[:span[0]] + block + '\n' + text[span[1]:])
    for entry_id in drifted + [ENTRY_ID]:
        lpc.update_hash(entry_id)
    left = lpc.check(lpc.load_ledger()[0])
    print('re-derived %d drifted entr%s; %d violation(s) left'
          % (len(drifted), 'y' if len(drifted) == 1 else 'ies', len(left)))
    return 1 if left else 0


if __name__ == '__main__':
    sys.exit(main())
