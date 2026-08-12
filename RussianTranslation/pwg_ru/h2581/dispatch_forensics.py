#!/usr/bin/env python
"""Did the abandoned H2581 ticket-1 reservation actually reach a model?

Read-only forensics over the prior session's transcript. Settles whether the
pending, never-finalized reservation of 11-08-2026 corresponds to a real Agent
dispatch (money/quota actually spent) or to a reservation that was published
and then abandoned before any call.

Decisive test: an Agent ``tool_use`` whose prompt SHA-256 equals the ticket's
sealed ``request_prompt_sha256``, plus a matching ``tool_result``.
"""

import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TRANSCRIPT = (
    r'C:\Users\user\.claude\projects'
    r'\C--Users-user-Documents-GitHub-SanskritLexicography-RussianTranslation'
    r'\e405c30c-fb72-4b6b-a236-e775b57a3207.jsonl')
TICKET_PROMPT_SHA = 'b20a7dae56d3a8071ddef06a6aeae8e3e16f91d8da26b338c53a61564b3c6a7e'


def blocks(event):
    message = event.get('message')
    content = message.get('content') if isinstance(message, dict) else None
    return content if isinstance(content, list) else []


def main():
    if not os.path.isfile(TRANSCRIPT):
        print('TRANSCRIPT NOT FOUND: %s' % TRANSCRIPT)
        return 1
    uses, results, unparseable = [], {}, 0
    with open(TRANSCRIPT, 'r', encoding='utf-8') as handle:
        for lineno, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                unparseable += 1
                continue
            if not isinstance(event, dict):
                continue
            for block in blocks(event):
                if not isinstance(block, dict):
                    continue
                if block.get('type') == 'tool_use' and block.get('name') == 'Agent':
                    prompt = (block.get('input') or {}).get('prompt') or ''
                    uses.append({
                        'line': lineno,
                        'id': block.get('id'),
                        'prompt_sha256': hashlib.sha256(
                            prompt.encode('utf-8')).hexdigest(),
                        'prompt_len': len(prompt),
                    })
                if block.get('type') == 'tool_result':
                    detail = event.get('toolUseResult')
                    results[block.get('tool_use_id')] = {
                        'line': lineno,
                        'is_error': block.get('is_error'),
                        'status': (detail or {}).get('status')
                        if isinstance(detail, dict) else None,
                        'resolvedModel': (detail or {}).get('resolvedModel')
                        if isinstance(detail, dict) else None,
                    }

    print('transcript lines unparseable : %d' % unparseable)
    print('Agent tool_use blocks total  : %d' % len(uses))
    print('ticket request_prompt_sha256 : %s' % TICKET_PROMPT_SHA)
    print()
    matched = [u for u in uses if u['prompt_sha256'] == TICKET_PROMPT_SHA]
    for use in uses:
        result = results.get(use['id'], {})
        print('  line=%-6s id=%-30s sha=%s… len=%-6d -> result: %s'
              % (use['line'], use['id'], use['prompt_sha256'][:12],
                 use['prompt_len'],
                 ('status=%s is_error=%s model=%s'
                  % (result.get('status'), result.get('is_error'),
                     result.get('resolvedModel'))) if result else 'NO RESULT'))
    print()
    print('MATCHING the sealed ticket prompt: %d' % len(matched))
    if not matched:
        print('VERDICT: no Agent dispatch carried the ticket prompt — the '
              'reservation was published and ABANDONED before any model call.')
        return 0
    for use in matched:
        result = results.get(use['id'], {})
        print('VERDICT: dispatch %s status=%s model=%s'
              % (use['id'], result.get('status'), result.get('resolvedModel')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
