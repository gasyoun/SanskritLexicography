#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4527b_parity_restamp.py — the second H4527 LANG_PARITY re-derivation receipt (same class as
h4527_/h4861_/h4528_parity_restamp.py).

H4527 pass 2 (15-09-2026) replaced the readiness probe's text: `_probe_prompt` no longer prepends
the production TASK SHAPE block (H3157 a) or the H4277 provenance bridge, and asks one honest
question over the domain filler instead ("does the text below mention the Petersburg Sanskrit
dictionary?", true by construction). Two selftests were re-pinned
(`test_health_probe_asks_an_honest_question`, `test_health_probe_carries_no_injection_shape`) and
two comments were corrected (`gen_opt_harness2.MASK_PREAMBLE`, `latency_payload_sweep` docstring),
and probe event rows gained one hash-only field, `probe_prompt_sha` (`run_observability.ALLOWED`).
None of it adds a language branch or reads a target-language field: the probe carries no card and
no `--lang` input, and the MASK_PREAMBLE edit is a comment. Every drifted entry keeps its verdict.
This driver:

1. appends one dated re-derivation sentence to the note of every entry the check reports as
   drifted (never rewriting an existing sentence);
2. appends a supersession sentence to `probe_provenance_bridge_h4277`, whose mechanism this pass
   retired (the entry stays, as history, with its SHARED verdict — the replacement is shared too);
3. adds the H4527 question entry itself (SHARED) if it is not there yet;
4. re-stamps each affected entry through `lang_parity_check.update_hash`, the tool's own writer.

Idempotent in content: a second run finds no drift and no missing entry and changes no note
(`update_hash` still rewrites the ledger file with identical hashes). ONE-SHOT RECEIPT: it stamps
whatever the check reports as drifted, so running it after some later, unrelated change would
mis-attribute that drift to this pass. Re-derive later drift with its own receipt, never this one.
Usage: python src/pilot/h4527b_parity_restamp.py
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lang_parity_check as lpc  # noqa: E402

ENTRY_ID = 'probe_honest_question_h4527'
BRIDGE_ID = 'probe_provenance_bridge_h4277'
STAMP = ('H4527 pass 2 (15-09-2026, Opus 5 `claude-opus-5`): re-derived, verdict stands. The '
         'drift is the readiness probe\'s TEXT only -- one honest question over the fixed English '
         'filler replaces the TASK SHAPE prepend and the H4277 bridge -- plus two re-pinned '
         'selftests, two corrected comments (MASK_PREAMBLE, latency_payload_sweep) and one '
         'hash-only probe event field (`probe_prompt_sha`, run_observability.ALLOWED). No '
         'language branch, no target-language field read; RU and EN share one readiness probe.')
SUPERSEDED = ('SUPERSEDED by `probe_honest_question_h4527` (H4527 pass 2, 15-09-2026): with the '
              'bridge in place the probe still refused four times against two passes (10-09..15-09), '
              'the last two with `--safe-mode`, and the 14:27Z transcript named the bridge\'s own '
              'sentences as the injection signature. `_PROBE_PROVENANCE_BRIDGE` is deleted; its '
              'pin became `test_health_probe_carries_no_injection_shape`.')
NEW_ENTRY = {
    'id': ENTRY_ID,
    'mechanism': ('Readiness probe text: `_probe_prompt` asks one honest question whose true '
                  'answer is `{"ok": true}` ("does the text below mention the Petersburg Sanskrit '
                  'dictionary?") over >= payload + 4 238 B of fixed domain filler; nothing is '
                  'prepended'),
    'files': [
        'src/pilot/max_account_orchestrator.py',
        'src/pilot/window_selftest.py',
    ],
    'languages': ['ru', 'en'],
    'verdict': 'SHARED',
    'note': ('H4527 pass 2 (15-09-2026, Opus 5 `claude-opus-5`). `_probe_prompt` takes one '
             'argument, `payload_bytes`; no `lang` parameter, no target-language field, no card. '
             'The question and filler are fixed English prose asked of the model, never '
             'translated, so a Russian and an English window are gated by the byte-identical '
             'probe. On the cohort-acceptance route (`bounded_staged_run --execute '
             '--only-profile`) the production TASK SHAPE check it used to duplicate is carried by '
             'the canary gate, which renders the lane\'s own `mask_preamble(field)` for either '
             'language; `staged-run` has no canary and is routed to Uprava H4916 -- a gap for '
             'both languages alike, so parity is unaffected. Tests: `test_health_probe_asks_an_honest_question`, '
             '`test_health_probe_carries_no_injection_shape`, max_account_orchestrator_selftest '
             'D-P pin.'),
}


def main():
    entries, _text, _span = lpc.load_ledger()
    drifted = sorted({v.split(':', 1)[0] for v in lpc.check(entries)})
    changed = False
    for entry in entries:
        note = entry.get('note') or ''
        if entry.get('id') in drifted and STAMP not in note:
            note = (note.rstrip() + ' ' + STAMP).strip()
        if entry.get('id') == BRIDGE_ID and SUPERSEDED not in note:
            note = (note.rstrip() + ' ' + SUPERSEDED).strip()
        if note != (entry.get('note') or ''):
            entry['note'] = note
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
