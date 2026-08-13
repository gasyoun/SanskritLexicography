"""Find the most recent Agent tool_use dispatch_id in the session transcript."""
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


def main():
    agent_uses = []
    with open(TRANSCRIPT, 'r', encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            ev_type = ev.get('type')
            # Tool-use events can appear at top level or nested in message content
            if ev_type == 'tool_use' and ev.get('name') == 'Agent':
                uid = ev.get('id', '')
                if DISPATCH_RE.match(uid):
                    prompt = (ev.get('input') or {}).get('prompt', '')
                    agent_uses.append((lineno, uid, prompt[:80]))
                    continue
            # Also check message content blocks
            for block in ev.get('content', []):
                if not isinstance(block, dict):
                    continue
                if block.get('type') == 'tool_use' and block.get('name') == 'Agent':
                    uid = block.get('id', '')
                    if DISPATCH_RE.match(uid):
                        prompt = (block.get('input') or {}).get('prompt', '')
                        agent_uses.append((lineno, uid, prompt[:80]))

    print(f'Found {len(agent_uses)} Agent tool_use(s):', file=sys.stderr)
    for lineno, uid, prompt_prefix in agent_uses:
        print(f'  line {lineno}: id={uid!r}  prompt={prompt_prefix!r}', file=sys.stderr)

    if agent_uses:
        # Print last one (most recent dispatch) to stdout for capture
        print(agent_uses[-1][1])
    else:
        print('NOT_FOUND')
        sys.exit(1)


if __name__ == '__main__':
    main()
