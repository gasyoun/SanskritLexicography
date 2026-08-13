#!/usr/bin/env python
"""H2674 W0 live N=3 stream canary.

Spend-auth is the H2674 handoff. Logs every call to JSONL. Stops on
401/402, peak fence, or IncompleteRead after 3 retries. No TM / store write.
Does not flip DEFAULT_MODEL.

Usage:
  python experiments/H2674_w0_stream/run_canary.py --env-file ../../ORS-FAQ/.env
"""
import argparse
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.abspath(os.path.join(HERE, '..', '..'))
H1210 = os.path.join(RT, 'src', 'pilot', 'h1210')
if H1210 not in sys.path:
    sys.path.insert(0, H1210)

import deepseek_arm as ds  # noqa: E402

CANARY_KEYS = ('yaTepsita', 'viSvaha', 'viSa')
SYSTEM = (
    'Return ONE JSON object only: '
    '{"key1": string, "ok": true, "note": string}. No markdown.'
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--env-file', default=None)
    ap.add_argument('--model', default=ds.DEFAULT_MODEL)
    ap.add_argument('--reasoning-effort', default='high', choices=ds.ALLOWED_EFFORTS)
    ap.add_argument('--max-tokens', type=int, default=ds.DEFAULT_MAX_TOKENS)
    ap.add_argument('--timeout', type=int, default=600)
    ap.add_argument('--out', default=os.path.join(HERE, 'canary.jsonl'))
    a = ap.parse_args()

    env = ds.load_env_file(a.env_file)
    key = os.environ.get('DEEPSEEK_API_KEY') or env.get('DEEPSEEK_API_KEY')
    if not key:
        sys.exit('FAIL: no DEEPSEEK_API_KEY in env or --env-file')
    base = (os.environ.get('DEEPSEEK_BASE_URL') or env.get('DEEPSEEK_BASE_URL')
            or 'https://api.deepseek.com')
    if a.model != ds.DEFAULT_MODEL:
        print('WARN: canary model override %s (DEFAULT_MODEL still %s)'
              % (a.model, ds.DEFAULT_MODEL), file=sys.stderr)
    ds.refuse_if_peak()
    client = ds.DeepSeek(base, key, a.model, a.max_tokens, timeout=a.timeout,
                         reasoning_effort=a.reasoning_effort)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    n_ok = n_fail = 0
    t0 = time.time()
    with open(a.out, 'w', encoding='utf-8', newline='\n') as journal:
        for k in CANARY_KEYS:
            user = json.dumps({'key1': k, 'task': 'stream-hold canary'}, ensure_ascii=False)
            text, rec = client.chat(SYSTEM, user, 'canary:%s' % k)
            err = (rec or {}).get('error') or ''
            row = {
                'key1': k,
                'ok': text is not None and 'IncompleteRead' not in err,
                'text_len': len(text or ''),
                'call': rec,
            }
            if (rec or {}).get('fence') == '401/402':
                journal.write(json.dumps(row, ensure_ascii=False) + '\n')
                journal.flush()
                sys.exit('REFUSE: DeepSeek 401/402 on %s' % k)
            if 'IncompleteRead' in err:
                journal.write(json.dumps(row, ensure_ascii=False) + '\n')
                journal.flush()
                sys.exit('FAIL: IncompleteRead after retries on %s: %s' % (k, err))
            if text is None:
                n_fail += 1
            else:
                n_ok += 1
            journal.write(json.dumps(row, ensure_ascii=False) + '\n')
            journal.flush()
            print('  %s ok=%s transport=%s attempts=%s reasoning=%s $partial=%s'
                  % (k, row['ok'], rec.get('transport'), rec.get('transport_attempts'),
                     rec.get('reasoning_tokens'), rec.get('error') or '-'),
                  flush=True)
    wall = time.time() - t0
    summary = {
        'schema': 'pwg.h2674_w0_canary.v1',
        'n': len(CANARY_KEYS),
        'ok': n_ok,
        'fail': n_fail,
        'wall_s': round(wall, 1),
        'model': a.model,
        'default_model_unchanged': ds.DEFAULT_MODEL == 'deepseek-v4-flash',
        'transport': ds.TRANSPORT,
        'max_tokens': a.max_tokens,
        'cost': client.cost(),
        'price_card': client.price_card,
    }
    summary_path = os.path.splitext(a.out)[0] + '.summary.json'
    with open(summary_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('wrote', a.out)
    print('wrote', summary_path)
    print(json.dumps(summary, ensure_ascii=False))
    if n_fail or n_ok != 3:
        sys.exit('FAIL: canary %d/3 ok' % n_ok)
    if not summary['default_model_unchanged']:
        sys.exit('FAIL: DEFAULT_MODEL flipped')
    print('canary PASS 3/3')
    return 0


if __name__ == '__main__':
    sys.exit(main())
