#!/usr/bin/env python
r"""H1210 arm B — cheap external generation (DeepSeek) behind the SAME H1209 gate chain.

The A/B ruling (MG, 17-07-2026) fixes exactly one variable: the GENERATOR. Arm A is the
Claude-native rig (Opus controller + Sonnet workers, `wf_template_ab.js`); arm B replaces
the worker with DeepSeek (`deepseek-chat`, the OpenAI-compatible endpoint — no
ANTHROPIC_API_KEY is requested or needed, standing rule) and keeps EVERYTHING else:

  * the same per-card prompt      — `prompt_common + card_block` from prep_slice, verbatim
  * the same output schema        — `worker_schema` derived by build_args from the manifest
  * the same free deterministic gate — `det_gate.deterministic_audit`, the Python twin of
                                     the in-JS v2 gate (selftested against it)
  * the same <=2 free retries with the gate's own issues as controller feedback
  * the same sticky-rejection / escalate-to-review-sheet terminal states
  * the same authoritative verdict afterwards — `h1209/canonical_audit.py`

The Opus controller stage is NOT run here: it is identical for both arms and runs as one
control-only Workflow (`control_arm.js`) over whichever cards pass the free gate, so the
controller's model, prompt and spend are literally shared rather than merely matched.

Output: `arm_b.slice_result.json`, byte-compatible with the arm-A Workflow return value
(slice / results / cards_out), plus `arm_b.telemetry.json` (per-call latency, tokens, cost,
JSON-repair events).

Usage:
  python src/pilot/h1210/deepseek_arm.py <slice_payload.json> <manifest.json> <out_prefix>
        [--env-file PATH] [--model deepseek-chat] [--workers 6] [--max-tokens 8192]
        [--keys k1,k2] [--limit N] [--dry-run]

The API key is read from $DEEPSEEK_API_KEY, or from `--env-file` (a KEY=VALUE .env) — never
from a committed file, and never echoed into any artifact.
"""
import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import det_gate  # noqa: E402

# DeepSeek published list prices, USD per 1M tokens (deepseek-chat, standard window).
# Recorded here so the $/clean figure in RESULTS_LOG is reproducible and re-pricable.
PRICE_CACHE_MISS_IN = 0.27
PRICE_CACHE_HIT_IN = 0.07
PRICE_OUT = 1.10

MAX_ATTEMPTS = 3


def load_env_file(path):
    env = {}
    if not path or not os.path.exists(path):
        return env
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def extract_json(text):
    """Return the first complete JSON object in `text`.

    `deepseek-chat` with response_format=json_object normally returns bare JSON, but the
    measured failure mode (Uprava FINDINGS §68) is TRUNCATION on high-polysemy headwords —
    and occasionally a ```json fence. Both are recorded as repair events, not hidden.
    """
    t = text.strip()
    repair = None
    if t.startswith('```'):
        t = re.sub(r'^```[a-zA-Z]*\s*', '', t)
        t = re.sub(r'\s*```$', '', t)
        repair = 'code-fence'
    try:
        return json.loads(t), repair
    except ValueError:
        pass
    start = t.find('{')
    if start < 0:
        raise ValueError('no JSON object in response')
    depth, in_str, esc = 0, False, False
    for i in range(start, len(t)):
        ch = t[i]
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return json.loads(t[start:i + 1]), (repair or 'brace-scan')
    raise ValueError('truncated JSON (unbalanced braces, %d chars)' % len(t))


class DeepSeek:
    def __init__(self, base, key, model, max_tokens, timeout=600):
        self.url = base.rstrip('/') + '/chat/completions'
        self.key = key
        self.model = model
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.lock = threading.Lock()
        self.calls = []

    def chat(self, system, user, label):
        body = json.dumps({
            'model': self.model,
            'messages': [{'role': 'system', 'content': system},
                         {'role': 'user', 'content': user}],
            'response_format': {'type': 'json_object'},
            'temperature': 0.2,
            'max_tokens': self.max_tokens,
        }).encode('utf-8')
        req = urllib.request.Request(self.url, data=body, headers={
            'Authorization': 'Bearer ' + self.key, 'Content-Type': 'application/json'})
        t0 = time.time()
        last = None
        for attempt in range(1, 4):                 # transport-only retries, with backoff
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    payload = json.load(r)
                dt = time.time() - t0
                usage = payload.get('usage') or {}
                rec = {'label': label, 'latency_s': round(dt, 2), 'transport_attempts': attempt,
                       'prompt_tokens': usage.get('prompt_tokens'),
                       'completion_tokens': usage.get('completion_tokens'),
                       'cache_hit_tokens': usage.get('prompt_cache_hit_tokens'),
                       'cache_miss_tokens': usage.get('prompt_cache_miss_tokens'),
                       'finish_reason': (payload.get('choices') or [{}])[0].get('finish_reason')}
                with self.lock:
                    self.calls.append(rec)
                return payload['choices'][0]['message']['content'], rec
            # Deliberately broad: the measured failure on the first 100-card run was
            # `http.client.IncompleteRead`, which is an HTTPException — NOT an OSError or a
            # URLError — so a narrow tuple let it escape and killed the whole worker thread,
            # leaving its remaining cards unattempted with no row. A transport exception must
            # cost this call, never the thread.
            except Exception as e:  # noqa: BLE001 — see above
                last = e
                if attempt < 3:
                    time.sleep(2 ** attempt)
        dt = time.time() - t0
        rec = {'label': label, 'latency_s': round(dt, 2), 'transport_attempts': 3,
               'error': '%s: %s' % (type(last).__name__, last)}
        with self.lock:
            self.calls.append(rec)
        return None, rec

    def cost(self):
        miss = sum(c.get('cache_miss_tokens') or 0 for c in self.calls)
        hit = sum(c.get('cache_hit_tokens') or 0 for c in self.calls)
        out = sum(c.get('completion_tokens') or 0 for c in self.calls)
        # Older/absent cache split -> charge the whole prompt at cache-miss rate (never free).
        if not (miss or hit):
            miss = sum(c.get('prompt_tokens') or 0 for c in self.calls)
        return {
            'cache_miss_in_tokens': miss, 'cache_hit_in_tokens': hit, 'out_tokens': out,
            'usd': round(miss / 1e6 * PRICE_CACHE_MISS_IN + hit / 1e6 * PRICE_CACHE_HIT_IN
                         + out / 1e6 * PRICE_OUT, 4),
            'price_table': {'cache_miss_in': PRICE_CACHE_MISS_IN,
                            'cache_hit_in': PRICE_CACHE_HIT_IN, 'out': PRICE_OUT},
        }


SYSTEM_TMPL = (
    'You are a scholarly PWG German->Russian dictionary translation worker.\n'
    'Return ONE JSON object and nothing else. It must validate against this JSON Schema:\n'
    '%s\n'
    'Rules that override any instinct to be helpful:\n'
    '- Emit valid JSON only. No prose, no markdown fence, no commentary.\n'
    '- `card` is the translated card; `self_report.unsure` is mandatory and must be true if '
    'you were not confident about any sense or placeholder in this card.\n'
    '- Every {Tn} placeholder in the source must appear verbatim, in order, in the '
    "sense's german AND its russian. Never invent a {Tn}. Never move source content into "
    '`notes` — that field is not restored and its content is lost.\n'
    'The translation task itself follows in the user message; obey it exactly.'
)


def run_card(ds, c, common, schema, field):
    rec = {'key1': c['key1'], 'complexity': c['complexity'], 'attempts': 0,
           'self_report': None, 'det': None, 'controller': None, 'controller_calls': 0,
           'final_status': None, 'card': None, 'gen_calls': [], 'repairs': []}
    feedback = None
    system = SYSTEM_TMPL % json.dumps(schema, ensure_ascii=False)
    for attempt in range(1, MAX_ATTEMPTS + 1):
        rec['attempts'] = attempt
        user = common + c['card_block'] + (
            '\n\n=== CONTROLLER FEEDBACK (fix ONLY these, keep everything else verbatim) ===\n'
            + feedback if feedback else '')
        text, call = ds.chat(system, user, '%s#%d' % (c['key1'], attempt))
        rec['gen_calls'].append(call)
        if text is None:
            rec['final_status'] = 'worker-null-death'
            continue
        try:
            obj, repair = extract_json(text)
        except ValueError as e:
            rec['repairs'].append('attempt%d: %s' % (attempt, e))
            rec['final_status'] = 'worker-null-death'
            feedback = ('Your previous reply was not parseable JSON (%s). Reply with ONE '
                        'complete JSON object only.' % e)
            continue
        if repair:
            rec['repairs'].append('attempt%d: %s' % (attempt, repair))
        card = obj.get('card')
        if not isinstance(card, dict):
            rec['repairs'].append('attempt%d: no `card` object in reply' % attempt)
            rec['final_status'] = 'worker-null-death'
            feedback = 'Your reply had no top-level `card` object. Return {"card": {...}, "self_report": {...}}.'
            continue
        rec['self_report'] = obj.get('self_report')
        rec['card'] = card
        det = det_gate.deterministic_audit(card, c, field)
        rec['det'] = det
        flagged_unsure = bool((rec['self_report'] or {}).get('unsure'))
        need_review = bool(det['issues']) or flagged_unsure or c['complexity']['complex']
        if not need_review:
            rec['final_status'] = 'clean-no-review'
            break
        if det['issues']:
            rec['controller'] = {'ok': False, 'source': 'deterministic', 'issues': det['issues']}
            feedback = 'Deterministic gate failures:\n- ' + '\n- '.join(det['issues'])
            rec['final_status'] = ('escalate-review-sheet' if attempt == MAX_ATTEMPTS
                                   else rec['final_status'])
            continue
        # Free gate clean but review-worthy (complex / self-reported unsure): the shared Opus
        # controller decides, in the control-only Workflow — same stage arm A uses.
        rec['final_status'] = 'pending-controller'
        break
    if not rec['final_status']:
        rec['final_status'] = 'escalate-review-sheet'
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('payload')
    ap.add_argument('manifest')
    ap.add_argument('out_prefix')
    ap.add_argument('--env-file', default=None)
    ap.add_argument('--model', default=None)
    ap.add_argument('--base-url', default=None)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--max-tokens', type=int, default=8192)
    ap.add_argument('--keys', default=None)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    payload = json.load(open(a.payload, encoding='utf-8'))
    man = json.load(open(a.manifest, encoding='utf-8'))
    field = man.get('field') or 'russian'
    common = payload['prompt_common']
    cards = payload['cards']
    if a.keys:
        want = {k for k in a.keys.split(',') if k}
        cards = [c for c in cards if c['key1'] in want]
    if a.limit:
        cards = cards[:a.limit]

    # The worker schema is derived exactly as build_args.py derives arm A's.
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'h1209'))
    import build_args  # noqa: E402
    schema = {'type': 'object', 'additionalProperties': False,
              'required': ['card', 'self_report'],
              'properties': {'card': {'$ref': '#/$defs/card'},
                             'self_report': build_args.SELF_REPORT},
              '$defs': man['output_schema']['$defs']}

    env = load_env_file(a.env_file)
    key = os.environ.get('DEEPSEEK_API_KEY') or env.get('DEEPSEEK_API_KEY')
    base = (a.base_url or os.environ.get('DEEPSEEK_BASE_URL') or env.get('DEEPSEEK_BASE_URL')
            or 'https://api.deepseek.com')
    model = (a.model or os.environ.get('DEEPSEEK_MODEL') or env.get('DEEPSEEK_MODEL')
             or 'deepseek-chat')
    if a.dry_run:
        print('dry-run: %d card(s), model=%s base=%s key=%s, schema %d B, prompt_common %d B'
              % (len(cards), model, base, 'present' if key else 'MISSING',
                 len(json.dumps(schema)), len(common)))
        return
    if not key:
        sys.exit('FAIL: no DEEPSEEK_API_KEY in env or --env-file (arm B needs the external '
                 'generator; report it BLOCKED rather than substituting a model)')

    ds = DeepSeek(base, key, model, a.max_tokens)
    results = [None] * len(cards)
    lock = threading.Lock()
    done = [0]
    # Append-only journal: every finished card lands on disk the moment it finishes. The
    # first 100-card run completed 98 cards and then died in final aggregation, and because
    # results only existed in memory the whole run was lost. A crash may now cost the
    # in-flight cards, never the finished ones.
    journal_path = a.out_prefix + '.journal.jsonl'
    journal = open(journal_path, 'a', encoding='utf-8', newline='\n')

    def worker(i):
        r = run_card(ds, cards[i], common, schema, field)
        results[i] = r
        with lock:
            journal.write(json.dumps(r, ensure_ascii=False) + '\n')
            journal.flush()
            done[0] += 1
            print('  [%3d/%3d] %-24s %-22s attempts=%d'
                  % (done[0], len(cards), r['key1'], r['final_status'], r['attempts']),
                  flush=True)

    t0 = time.time()
    threads = []
    idx = [0]

    def pump():
        while True:
            with lock:
                if idx[0] >= len(cards):
                    return
                i = idx[0]
                idx[0] += 1
            try:
                worker(i)
            except Exception as e:  # noqa: BLE001 — a dead pump thread silently truncates
                results[i] = {'key1': cards[i]['key1'], 'complexity': cards[i]['complexity'],
                              'attempts': 0, 'self_report': None, 'det': None,
                              'controller': None, 'controller_calls': 0, 'card': None,
                              'final_status': 'driver-exception', 'gen_calls': [],
                              'repairs': ['%s: %s' % (type(e).__name__, e)]}
                print('  [ERR] %-24s %s: %s' % (cards[i]['key1'], type(e).__name__, e),
                      flush=True)

    for _ in range(max(1, min(a.workers, len(cards)))):
        t = threading.Thread(target=pump)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    journal.close()
    wall = time.time() - t0
    # A None row here means its thread died before writing one — keep it as an explicit
    # non-promotable row so the denominator stays 100 (no silent caps).
    for i, r in enumerate(results):
        if r is None:
            results[i] = {'key1': cards[i]['key1'], 'complexity': cards[i]['complexity'],
                          'attempts': 0, 'self_report': None, 'det': None, 'controller': None,
                          'controller_calls': 0, 'card': None, 'gen_calls': [],
                          'final_status': 'never-attempted',
                          'repairs': ['driver thread died before this card was attempted']}

    slice_result = {
        'slice': [c['key1'] for c in cards],
        'arm': 'B_deepseek',
        'generator': {'model': model, 'base_url': base, 'temperature': 0.2,
                      'max_tokens': a.max_tokens, 'response_format': 'json_object'},
        'results': [{
            'key1': r['key1'], 'attempts': r['attempts'],
            'complexity_score': r['complexity']['score'],
            'complexity_flag': r['complexity']['complex'],
            'self_report_unsure': (bool(r['self_report'].get('unsure'))
                                   if r['self_report'] else None),
            'self_report_note': ((r['self_report'] or {}).get('note', '')
                                 if r['self_report'] else None),
            'coverage': r['det']['coverage'] if r['det'] else None,
            'det_issues': r['det']['issues'] if r['det'] else None,
            'controller_calls': 0, 'controller_ok': None, 'controller_issues': None,
            'final_status': r['final_status'],
            'would_promote': r['final_status'] == 'clean-no-review',
            'repairs': r['repairs'],
        } for r in results],
        'cards_out': [{'key1': r['key1'], 'card': r['card']} for r in results],
    }
    telemetry = {
        'schema': 'pwg.h1210_arm_telemetry.v1', 'arm': 'B_deepseek', 'model': model,
        'cards': len(cards), 'wall_clock_s': round(wall, 1), 'workers': a.workers,
        'generation_calls': len(ds.calls),
        'calls': ds.calls, 'cost': ds.cost(),
        'per_card': [{'key1': r['key1'], 'attempts': r['attempts'],
                      'final_status': r['final_status'], 'repairs': r['repairs'],
                      'latency_s': [c.get('latency_s') for c in r['gen_calls']]}
                     for r in results],
    }
    for name, obj in (('slice_result', slice_result), ('telemetry', telemetry)):
        p = '%s.%s.json' % (a.out_prefix, name)
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('wrote', p)
    from collections import Counter
    print('arm B: %d cards, %.1f s wall, %d generation calls, $%.4f'
          % (len(cards), wall, len(ds.calls), telemetry['cost']['usd']))
    for st, n in sorted(Counter(r['final_status'] for r in results).items()):
        print('  %-24s %d' % (st, n))


if __name__ == '__main__':
    main()
