#!/usr/bin/env python
"""Who ran the unauthorised 11-08-2026 H2581 dispatch? Read-only.

Extracts session identity from the prior session's transcript and the human
turns that framed the dispatch, so the question "who made that call" is answered
from the record rather than by inference.
"""

import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TRANSCRIPT = (
    r'C:\Users\user\.claude\projects'
    r'\C--Users-user-Documents-GitHub-SanskritLexicography-RussianTranslation'
    r'\e405c30c-fb72-4b6b-a236-e775b57a3207.jsonl')
DISPATCH_LINE = 275


def text_of(event):
    message = event.get('message') or {}
    content = message.get('content')
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [b.get('text', '') for b in content
                 if isinstance(b, dict) and b.get('type') == 'text']
        return '\n'.join(p for p in parts if p)
    return ''


def main():
    meta_keys = ('sessionId', 'version', 'gitBranch', 'cwd', 'userType',
                 'isSidechain', 'timestamp')
    first = None
    users = []
    models = {}
    with open(TRANSCRIPT, 'r', encoding='utf-8') as handle:
        for lineno, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict):
                continue
            if first is None:
                first = {k: event.get(k) for k in meta_keys}
            if event.get('type') == 'assistant':
                model = (event.get('message') or {}).get('model')
                if model:
                    models[model] = models.get(model, 0) + 1
            if event.get('type') == 'user' and not event.get('isSidechain'):
                body = text_of(event)
                if body and not body.startswith('<'):
                    users.append((lineno, event.get('timestamp'), body))

    print('=== session identity (first event) ===')
    for key, value in (first or {}).items():
        print('  %-12s %s' % (key, value))
    print()
    print('=== assistant models seen ===')
    for model, count in sorted(models.items(), key=lambda kv: -kv[1]):
        print('  %-28s %d turns' % (model, count))
    print()
    print('=== human turns (non-sidechain), %d total ===' % len(users))
    for lineno, stamp, body in users:
        marker = '  <-- BEFORE DISPATCH' if lineno < DISPATCH_LINE else ''
        snippet = ' '.join(body.split())[:300]
        print('\n  [line %s | %s]%s\n    %s' % (lineno, stamp, marker, snippet))
    return 0


if __name__ == '__main__':
    sys.exit(main())
