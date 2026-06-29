#!/usr/bin/env python
"""Sum the real token split + $ cost of a workflow run from its transcript dir.

The workflow notification only reports a blunt totalTokens. The per-agent
transcript JSONL records the billing-relevant split (fresh input, cache-create,
cache-read, output) per assistant turn — which is what actually costs money, since
cache-read is ~10x cheaper than fresh input. This sums them and prices them.

  python src/pilot/parse_workflow_cost.py <transcript_dir> [<transcript_dir2> ...]
"""
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Claude Sonnet 4.x standard rates, $ per million tokens (cache-write = 5m TTL).
PRICE = {'input': 3.00, 'output': 15.00, 'cache_write': 3.75, 'cache_read': 0.30}


def usage_records(path):
    for jf in glob.glob(os.path.join(path, '*.jsonl')):
        for line in open(jf, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except ValueError:
                continue
            u = o.get('usage')
            if not isinstance(u, dict) and isinstance(o.get('message'), dict):
                u = o['message'].get('usage')
            if isinstance(u, dict) and ('input_tokens' in u or 'output_tokens' in u):
                yield u


def tooluse_output_chars(path):
    """Sum chars of StructuredOutput tool-call arguments — the model's real
    generated output, which the logged usage.output_tokens under-reports for
    structured runs. Estimated tokens = chars / 4."""
    chars = 0
    for jf in glob.glob(os.path.join(path, '*.jsonl')):
        for line in open(jf, encoding='utf-8'):
            try:
                o = json.loads(line)
            except ValueError:
                continue
            msg = o.get('message') if isinstance(o.get('message'), dict) else o
            content = msg.get('content')
            if isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get('type') == 'tool_use':
                        chars += len(json.dumps(b.get('input', {}), ensure_ascii=False))
    return chars


def tally(path):
    t = {'input': 0, 'cache_write': 0, 'cache_read': 0, 'output': 0, 'turns': 0}
    for u in usage_records(path):
        t['input'] += u.get('input_tokens', 0) or 0
        t['cache_write'] += u.get('cache_creation_input_tokens', 0) or 0
        t['cache_read'] += u.get('cache_read_input_tokens', 0) or 0
        t['output'] += u.get('output_tokens', 0) or 0
        t['turns'] += 1
    # logged output_tokens under-reports structured tool-call output; use the larger
    # of (logged, est-from-tool-call-chars) so cost isn't undercounted.
    t['output_est'] = max(t['output'], tooluse_output_chars(path) // 4)
    t['cost'] = (t['input'] * PRICE['input'] + t['output_est'] * PRICE['output']
                 + t['cache_write'] * PRICE['cache_write'] + t['cache_read'] * PRICE['cache_read']) / 1e6
    t['total_tokens'] = t['input'] + t['cache_write'] + t['cache_read'] + t['output_est']
    return t


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: parse_workflow_cost.py <transcript_dir> [...]')
    print('%-26s %8s %10s %10s %9s %10s %9s' %
          ('run', 'input', 'cache_wr', 'cache_rd', 'out(est)', 'total', '$cost'))
    for path in sys.argv[1:]:
        t = tally(path)
        print('%-26s %8d %10d %10d %9d %10d %9.4f' %
              (os.path.basename(path), t['input'], t['cache_write'],
               t['cache_read'], t['output_est'], t['total_tokens'], t['cost']))


if __name__ == '__main__':
    main()
