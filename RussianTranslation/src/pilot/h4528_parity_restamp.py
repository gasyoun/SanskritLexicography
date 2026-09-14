#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4528_parity_restamp.py — the H4528 LANG_PARITY re-derivation receipt (same class as
h2254_/h2504_/h4438_parity_restamp.py).

H4528 armed the H2878 no-output-progress watchdog on the headless worker's
token-streaming spawn and split its kill into `no_progress_kill`. Every touched file is
language-agnostic spawn / kill / classification plumbing, so every ledger entry that tracks
one of them keeps its SHARED verdict. This driver:

1. appends one dated re-derivation sentence to the note of every entry the check reports as
   drifted (never rewriting an existing sentence);
2. adds the H4528 entry itself (SHARED) if it is not there yet;
3. re-stamps each affected entry through `lang_parity_check.update_hash`, the tool's own
   writer, so the ledger keeps its canonical serialisation.

Idempotent: a second run finds no drift and no missing entry, and writes nothing.
Usage: python src/pilot/h4528_parity_restamp.py
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lang_parity_check as lpc  # noqa: E402

ENTRY_ID = 'whole_card_no_progress_watchdog_h4528'
STAMP = ('H4528 (14-09-2026, Opus 5 `claude-opus-5`): re-derived, SHARED stands. The drift is '
         'the no-output-progress watchdog wiring only -- an opt-in token-streaming spawn shape '
         '(`execution.cli_token_stream`, default OFF), a content-line progress filter, the '
         '`no_progress_kill` kill class and its telemetry. No language branch is added and no '
         'target-language field is read; RU and EN spawns take the identical argv and kill path.')
NEW_ENTRY = {
    'id': ENTRY_ID,
    'mechanism': ('No-output-progress watchdog armed on the token-streaming generation spawn '
                  '(content-line liveness filter, `no_progress_kill` class distinct from the '
                  'hard-ceiling `timeout`, CLI-lines-only classification text)'),
    'files': [
        'src/pilot/headless_worker.py',
        'src/pilot/proc_tree.py',
        'src/pilot/execution_contract.py',
        'src/pilot/cli_stream.py',
        'src/pilot/max_account_orchestrator.py',
        'src/pilot/h963_c4_gate0_probe.py',
    ],
    'languages': ['ru', 'en'],
    'verdict': 'SHARED',
    'note': ('H4528 (14-09-2026, Opus 5 `claude-opus-5`). The watchdog acts on the CLI child '
             'process, below the language layer: the spawn argv, the progress window, the '
             'content-line filter (`cli_stream.is_progress_line` reads NDJSON `type` only) and '
             'the kill classification are identical for a Russian and an English window, and '
             'the manifest target-language field is never consulted. `no_progress_kill` joins '
             '`INFRA_FAILURE_REASONS`, so the audit\'s transient-vs-defect split treats it like '
             '`timeout` on both languages. Tests: headless_worker_selftest test_h4528_* (six), '
             'window_selftest test_h4528_no_progress_kill_is_infra_not_a_content_defect.'),
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
