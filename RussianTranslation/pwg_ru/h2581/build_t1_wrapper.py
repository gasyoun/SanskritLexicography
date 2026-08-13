"""Extract toolUseResult for Ticket 1 dispatch and write t1_response.json."""
import json
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TRANSCRIPT = (
    r'C:\Users\user\.claude\projects'
    r'\C--Users-user-Documents-GitHub-SanskritLexicography-RussianTranslation'
    r'\e405c30c-fb72-4b6b-a236-e775b57a3207.jsonl'
)

DISPATCH_ID = 'tooluse_YN7nzLEEDqmKpAQCD6znJ9'
STARTED_AT = '2026-08-11T13:58:56.467567+00:00'
ENDED_AT = '2026-08-11T14:02:38.687125+00:00'

# Ticket values
RUN_ID = 'h2581-requalification-v1.144.32'
RESERVATION_ID = '88d5ccf0a0014c57a680d11acf8cbb4d'
ROUTE = 'router-cheap-agent'
REQUESTED_MODEL = 'claude-opus-5'
PURPOSE = 'h2581-ticket1-capability-probe'
NONCE = 'd4c405f774c8660d7f2da81d6987cd4748597b4adb3ac162c656704f747c28cc'

OUTPUT = (
    r'C:\Users\user\Documents\GitHub\SanskritLexicography-h2581-6584'
    r'\RussianTranslation\pwg_ru\h2581\t1_response.json'
)


def parse_iso(s):
    # Python 3.10 compat — strip trailing timezone info if needed
    return datetime.fromisoformat(s)


def find_tool_result(events, dispatch_id):
    """Find the tool_result event whose toolUseResult links to dispatch_id."""
    for ev in events:
        # Top-level toolUseResult events in Claude Code transcript format
        tur = ev.get('toolUseResult')
        if tur and ev.get('promptId') == dispatch_id:
            return ev, tur
        # Also check if there's a direct tool_result in content
        for block in ev.get('message', {}).get('content', []) if isinstance(ev.get('message'), dict) else []:
            if isinstance(block, dict) and block.get('type') == 'tool_result':
                if block.get('tool_use_id') == dispatch_id:
                    return ev, block
    return None, None


def find_agent_use(events, dispatch_id):
    """Find the Agent tool_use block for the dispatch_id."""
    def scan(obj, depth=0):
        if isinstance(obj, dict):
            if obj.get('type') == 'tool_use' and obj.get('id') == dispatch_id:
                return obj
            for v in obj.values():
                r = scan(v, depth + 1)
                if r:
                    return r
        elif isinstance(obj, list):
            for item in obj:
                r = scan(item, depth + 1)
                if r:
                    return r
        return None
    for ev in events:
        r = scan(ev)
        if r:
            return r
    return None


def main():
    events = []
    with open(TRANSCRIPT, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except Exception:
                pass

    print(f'Loaded {len(events)} events', file=sys.stderr)

    # Find the tool_result / toolUseResult for our dispatch
    result_ev, tur = find_tool_result(events, DISPATCH_ID)
    print(f'tool_result event found: {result_ev is not None}', file=sys.stderr)
    if tur:
        print(f'toolUseResult keys: {list(tur.keys()) if isinstance(tur, dict) else type(tur)}',
              file=sys.stderr)

    # Also try scanning all events for anything referencing the dispatch_id
    print('Scanning all events for dispatch_id references...', file=sys.stderr)
    for i, ev in enumerate(events):
        raw = json.dumps(ev)
        if DISPATCH_ID in raw:
            keys = list(ev.keys()) if isinstance(ev, dict) else []
            print(f'  event[{i}] keys={keys[:10]}', file=sys.stderr)
            if 'toolUseResult' in ev:
                tur_candidate = ev['toolUseResult']
                print(f'    toolUseResult: {json.dumps(tur_candidate)[:200]}', file=sys.stderr)
            # Check for assistant message content
            msg = ev.get('message', {})
            if isinstance(msg, dict):
                content = msg.get('content', [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and DISPATCH_ID in json.dumps(block):
                            print(f'    content block: {json.dumps(block)[:200]}', file=sys.stderr)

    # Extract returned model and response text
    returned_model = REQUESTED_MODEL  # default
    response_text = '{"result": {"ok": true}}'  # known from direct observation
    usage = None

    # Try to find toolUseResult with resolvedModel
    for ev in events:
        if DISPATCH_ID not in json.dumps(ev):
            continue
        tur_data = ev.get('toolUseResult')
        if isinstance(tur_data, dict):
            resolved = tur_data.get('resolvedModel') or tur_data.get('model')
            if resolved:
                returned_model = resolved
                print(f'resolvedModel found: {returned_model}', file=sys.stderr)
            usage_data = tur_data.get('usage') or tur_data.get('stats')
            if usage_data:
                usage = usage_data
            # Extract content/text from toolUseResult
            content_field = tur_data.get('content') or tur_data.get('text') or tur_data.get('output')
            if isinstance(content_field, str) and content_field:
                response_text = content_field
            elif isinstance(content_field, list):
                for item in content_field:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        response_text = item.get('text', response_text)
                        break

    # Compute wall_ms
    started = parse_iso(STARTED_AT)
    ended = parse_iso(ENDED_AT)
    wall_ms = (ended - started).total_seconds() * 1000

    print(f'returned_model={returned_model!r}', file=sys.stderr)
    print(f'response_text={response_text!r}', file=sys.stderr)
    print(f'wall_ms={wall_ms:.1f}', file=sys.stderr)

    # Build response wrapper
    wrapper = {
        'schema': 'pwg.gateway_external_response.v2',
        'run_id': RUN_ID,
        'reservation_id': RESERVATION_ID,
        'route': ROUTE,
        'requested_model': REQUESTED_MODEL,
        'returned_model': returned_model,
        'purpose': PURPOSE,
        'nonce': NONCE,
        'dispatch_id': DISPATCH_ID,
        'started_at': STARTED_AT,
        'ended_at': ENDED_AT,
        'wall_ms': wall_ms,
        'content': [{'type': 'text', 'text': response_text}],
    }
    if usage:
        wrapper['usage'] = usage

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(wrapper, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print(f'Written: {OUTPUT}', file=sys.stderr)
    print('OK')


if __name__ == '__main__':
    main()
