"""Classify every Agent tool_use in the session: dispatched-to-model vs refused-before-dispatch.

The H2539 contract caps *Agent calls*, so the qualification report must state a
truthful count.  A call the harness refused (unknown subagent_type, guard block)
never reached a model and spent nothing; conflating it with a real dispatch would
either overstate spend or understate it.  This reads the tool_result paired with
each Agent tool_use by id and prints the verdict.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TRANSCRIPT = Path(
    r'C:\Users\user\.claude\projects'
    r'\C--Users-user-Documents-GitHub-SanskritLexicography-RussianTranslation'
    r'\5bf8a098-2789-4744-85c7-9dd00b88319a.jsonl')


def content_blocks(event):
    message = event.get('message')
    if not isinstance(message, dict):
        return []
    blocks = message.get('content')
    return blocks if isinstance(blocks, list) else []


def main():
    agent_uses = {}
    results = {}
    for lineno, line in enumerate(
            TRANSCRIPT.read_text(encoding='utf-8').splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        for block in content_blocks(event):
            if not isinstance(block, dict):
                continue
            if block.get('type') == 'tool_use' and block.get('name') == 'Agent':
                agent_uses[block.get('id')] = (lineno, event.get('timestamp'),
                                               block.get('input') or {})
            elif block.get('type') == 'tool_result':
                results[block.get('tool_use_id')] = (
                    block.get('is_error'), block.get('content'))

    for index, (use_id, (lineno, ts, payload)) in enumerate(
            agent_uses.items(), start=1):
        is_error, content = results.get(use_id, (None, None))
        if isinstance(content, list):
            text = ' '.join(
                part.get('text', '') for part in content
                if isinstance(part, dict))
        else:
            text = content if isinstance(content, str) else ''
        text = ' '.join(text.split())
        refused = bool(is_error) or 'not found' in text or 'BLOCKED' in text
        verdict = 'REFUSED-BEFORE-DISPATCH (no model contact, no spend)' \
            if refused else 'DISPATCHED TO MODEL'
        print('--- Agent call #%d  line=%s  ts=%s' % (index, lineno, ts))
        print('    subagent_type = %r' % payload.get('subagent_type'))
        print('    is_error      = %r' % (is_error,))
        print('    verdict       = %s' % verdict)
        print('    result_head   = %s' % (text[:190] or '<empty>'))
    print('\ntotal Agent tool_use blocks = %d' % len(agent_uses))


if __name__ == '__main__':
    main()
