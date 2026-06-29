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


def tally(path):
    t = {'input': 0, 'cache_write': 0, 'cache_read': 0, 'output': 0, 'turns': 0}
    for u in usage_records(path):
        t['input'] += u.get('input_tokens', 0) or 0
        t['cache_write'] += u.get('cache_creation_input_tokens', 0) or 0
        t['cache_read'] += u.get('cache_read_input_tokens', 0) or 0
        t['output'] += u.get('output_tokens', 0) or 0
        t['turns'] += 1
    t['cost'] = (t['input'] * PRICE['input'] + t['output'] * PRICE['output']
                 + t['cache_write'] * PRICE['cache_write'] + t['cache_read'] * PRICE['cache_read']) / 1e6
    t['total_tokens'] = t['input'] + t['cache_write'] + t['cache_read'] + t['output']
    return t


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: parse_workflow_cost.py <transcript_dir> [...]')
    print('%-46s %9s %11s %11s %9s %12s %9s' %
          ('run', 'input', 'cache_wr', 'cache_rd', 'output', 'total_tok', '$cost'))
    for path in sys.argv[1:]:
        t = tally(path)
        print('%-46s %9d %11d %11d %9d %12d %9.4f' %
              (os.path.basename(path), t['input'], t['cache_write'],
               t['cache_read'], t['output'], t['total_tokens'], t['cost']))


if __name__ == '__main__':
    main()
