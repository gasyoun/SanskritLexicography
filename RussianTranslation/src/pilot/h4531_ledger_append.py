#!/usr/bin/env python
"""H4531: append this pass's launch failure to the LAUNCH_FUCKUPS.md JSON register.

A script rather than a hand edit because the register is one fenced JSON array inside a
569-line narrative file: a hand-placed brace is exactly how that array stops parsing.
Idempotent -- re-running it does not duplicate the entry.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'LAUNCH_FUCKUPS.md')
FENCE = re.compile(r'```json launch_failure_ledger\n(.*?)\n```', re.DOTALL)

ENTRY = {
    'id': 'H4531_BATCHES_SUBMIT_401_2026-09-11',
    'handoff': 'H4531',
    'date': '2026-09-11',
    'title': ('Batches API first submit refused 401 invalid-key; the pre-submit '
              'reservation burned the whole 23-call ceiling at $0 spend'),
    'lane': ('anthropic-batches transport (new), root d_a, 23 one-card requests, '
             'claude-sonnet-5, run_id h4531-batches-probe'),
    'model': 'claude-sonnet-5',
    'orchestrator': 'Opus 5 (claude-opus-5[1m]) unattended handoff worker + h4531_batches_probe.py',
    'expected': {
        'agents': 'one Message Batch of 23 single-card requests, async, retrieved within 24 h',
        'tokens': 'ESTIMATE ~92k input / ~27.6k output, ~$0.35 at the 50 % batch schedule',
    },
    'actual': {
        'agents': 'zero requests processed; the provider refused the batch create call',
        'tokens': '0 tokens, $0 billed; ledger max_calls=23 calls_spent=23 '
                  'finalized_calls=0 pending_calls=23',
    },
    'passes': 1,
    'symptoms': ('anthropic.AuthenticationError: 401 {"type": "authentication_error", '
                 '"message": "API key is invalid."} raised from '
                 'client.messages.batches.create. The independent zero-token probe '
                 'h4531_auth_probe.py returns rc=4 with authenticated=false, '
                 'model_available=false, reason AuthenticationError:http_401 against the '
                 'same credential, so the failure is the key and not the Batches endpoint. '
                 'The credential was read from the prepared secrets file, never typed.'),
    'classification': 'external-api',
    'root_cause': ('The prepared ANTHROPIC_API_KEY in the lane secrets file is no longer '
                   'valid (rotated, revoked, or from a different workspace). Secondary, and '
                   'the part that is ours: AnthropicBatchesCall.submit reserves one ledger '
                   'call per request BEFORE the provider call -- correct and required by the '
                   'money contract -- so a failure that bills nothing still consumes the '
                   'entire ceiling, and the retry cannot reuse the run. Inherited from '
                   'anthropic_messages_route, which documents the same irreversibility.'),
    'guardrail': ('h4531_auth_probe.py now exists as a zero-token authenticated GET and is '
                  'the documented first step of the probe runbook, turning this class of '
                  'ceiling burn into a $0 rc=4. The reservation is deliberately NOT released '
                  'on a provider refusal: a release path mis-scoped by one failure class '
                  'would let a genuinely billable failure look free. A retry uses a fresh '
                  'run directory (a fresh run_id), never a raised ceiling on the burnt run.'),
    'residual_status': 'open-paused',
    'residual_risk': ('H4531 cannot reach a GO/NO-GO verdict until a valid key reaches '
                      'C:\\Users\\user\\.secrets\\anthropic.env (human, ~2 min). The H1403 '
                      'ledger #8 / A8 Batches blind spot therefore stays OPEN; no DEAD_ENDS '
                      'entry was written, because nothing about the route was measured. The '
                      'burnt ledger run h4531-batches-probe keeps 23 pending reservations '
                      'against $0 of real spend -- do not read them as cost.'),
}


def main():
    text = io.open(LEDGER, encoding='utf-8', newline='').read()
    match = FENCE.search(text)
    if not match:
        raise SystemExit('no fenced launch_failure_ledger block in %s' % LEDGER)
    entries = json.loads(match.group(1))
    if any(row.get('id') == ENTRY['id'] for row in entries):
        print('entry %s already present' % ENTRY['id'])
        return 0
    entries.append(ENTRY)
    body = json.dumps(entries, ensure_ascii=False, indent=1)
    updated = text[:match.start(1)] + body + text[match.end(1):]
    io.open(LEDGER, 'w', encoding='utf-8', newline='\n').write(updated)
    print('appended %s (%d entries)' % (ENTRY['id'], len(entries)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
