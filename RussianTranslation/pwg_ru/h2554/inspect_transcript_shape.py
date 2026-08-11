"""Print only structural Agent-dispatch links from a Claude transcript.

The probe deliberately omits prompts, tool inputs, results, and message text.  It
exists to answer one question offline: which stable identifiers connect an
Agent ``tool_use`` to its ``tool_result`` and to served-model assistant events?
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def blocks(event):
    message = event.get('message')
    content = message.get('content') if isinstance(message, dict) else None
    return content if isinstance(content, list) else []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('transcript', type=Path)
    args = parser.parse_args()
    events = []
    agent_ids = set()
    for lineno, line in enumerate(
            args.transcript.read_text(encoding='utf-8').splitlines(), start=1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        events.append((lineno, event))
        for block in blocks(event):
            if (isinstance(block, dict) and block.get('type') == 'tool_use'
                    and block.get('name') == 'Agent'):
                agent_ids.add(block.get('id'))

    for lineno, event in events:
        matched = []
        for block in blocks(event):
            if not isinstance(block, dict):
                continue
            if block.get('id') in agent_ids:
                matched.append('tool_use:%s' % block.get('id'))
                prompt = (block.get('input') or {}).get('prompt')
                if isinstance(prompt, str):
                    structural_prompt_hash = hashlib.sha256(
                        prompt.encode('utf-8')).hexdigest()
            if block.get('tool_use_id') in agent_ids:
                matched.append('tool_result:%s' % block.get('tool_use_id'))
        structural = {
            key: event.get(key) for key in (
                'type', 'uuid', 'parentUuid', 'timestamp', 'isSidechain',
                'agentId', 'parentToolUseID', 'toolUseID')
            if key in event
        }
        if 'structural_prompt_hash' in locals():
            structural['tool_use_prompt_sha256'] = structural_prompt_hash
            del structural_prompt_hash
        message = event.get('message')
        if isinstance(message, dict):
            structural['message_role'] = message.get('role')
            structural['message_model'] = message.get('model')
            structural['message_keys'] = sorted(message)
        tool_result = event.get('toolUseResult')
        if isinstance(tool_result, dict):
            structural['toolUseResult_keys'] = sorted(tool_result)
            structural['toolUseResult_types'] = {
                key: type(value).__name__ for key, value in tool_result.items()
            }
            structural['toolUseResult_status'] = tool_result.get('status')
            structural['toolUseResult_resolvedModel'] = tool_result.get(
                'resolvedModel')
            structural['toolUseResult_agentId'] = tool_result.get('agentId')
            result_prompt = tool_result.get('prompt')
            if isinstance(result_prompt, str):
                structural['toolUseResult_prompt_sha256'] = hashlib.sha256(
                    result_prompt.encode('utf-8')).hexdigest()
        structural['event_keys'] = sorted(event)
        if matched or any(event.get(key) in agent_ids for key in (
                'parentToolUseID', 'toolUseID')):
            print('%s\t%s\t%s' % (
                lineno, ','.join(matched) or 'linked-event',
                json.dumps(structural, ensure_ascii=False, sort_keys=True)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
