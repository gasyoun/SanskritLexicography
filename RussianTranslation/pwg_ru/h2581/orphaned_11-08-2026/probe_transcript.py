"""Probe the session transcript structure to find Agent tool_use blocks."""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TRANSCRIPT = (
    r'C:\Users\user\.claude\projects'
    r'\C--Users-user-Documents-GitHub-SanskritLexicography-RussianTranslation'
    r'\e405c30c-fb72-4b6b-a236-e775b57a3207.jsonl'
)

DISPATCH_RE = re.compile(r'^toolu(?:se)?_[A-Za-z0-9_-]{8,180}$')


def scan_block(block, lineno, depth=0):
    """Recursively scan a dict/list for Agent tool_use entries."""
    if isinstance(block, dict):
        if block.get('type') == 'tool_use' and block.get('name') == 'Agent':
            uid = block.get('id', '')
            if DISPATCH_RE.match(uid):
                prompt = (block.get('input') or {}).get('prompt', '')
                print(f'  [depth={depth}] line={lineno} id={uid!r} prompt={prompt[:60]!r}',
                      file=sys.stderr)
                return uid
        for v in block.values():
            r = scan_block(v, lineno, depth + 1)
            if r:
                return r
    elif isinstance(block, list):
        for item in block:
            r = scan_block(item, lineno, depth + 1)
            if r:
                return r
    return None


def main():
    agent_uses = []
    total_lines = 0
    parse_errors = 0

    with open(TRANSCRIPT, 'r', encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            total_lines += 1
            try:
                ev = json.loads(line)
            except Exception:
                parse_errors += 1
                continue
            uid = scan_block(ev, lineno)
            if uid:
                agent_uses.append((lineno, uid))

    print(f'Total lines: {total_lines}, parse errors: {parse_errors}', file=sys.stderr)
    print(f'Found {len(agent_uses)} Agent tool_use(s).', file=sys.stderr)

    # Also dump top-level keys from last 5 lines to understand structure
    print('--- Last 5 event types/keys ---', file=sys.stderr)
    lines = []
    with open(TRANSCRIPT, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
    for line in lines[-5:]:
        try:
            ev = json.loads(line)
            if isinstance(ev, dict):
                keys = list(ev.keys())[:8]
                print(f'  keys={keys}', file=sys.stderr)
        except Exception:
            pass

    if agent_uses:
        print(agent_uses[-1][1])
    else:
        print('NOT_FOUND')
        sys.exit(1)


if __name__ == '__main__':
    main()
