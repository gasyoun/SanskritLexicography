#!/usr/bin/env python
r"""H1210 arm B — cheap external generation (DeepSeek) behind the SAME H1209 gate chain.

The A/B ruling (MG, 17-07-2026) fixes exactly one variable: the GENERATOR. Arm A is the
Claude-native rig (Opus controller + Sonnet workers, `wf_template_ab.js`); arm B replaces
the worker with DeepSeek (`deepseek-v4-flash` / Flash 0731 by default; override with
`--model` / `$DEEPSEEK_MODEL` — OpenAI-compatible endpoint, no ANTHROPIC_API_KEY,
standing rule) and keeps EVERYTHING else:

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
        [--env-file PATH] [--model deepseek-v4-flash] [--reasoning-effort high]
        [--workers 6] [--max-tokens 32768] [--timeout 600]
        [--keys k1,k2] [--limit N] [--dry-run]

The API key is read from $DEEPSEEK_API_KEY, or from `--env-file` (a KEY=VALUE .env) — never
from a committed file, and never echoed into any artifact.
"""
import argparse
import datetime
import json
import os
import re
import sys
import threading
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import det_gate  # noqa: E402

# DeepSeek published list prices, USD per 1M tokens, first-party.
# https://api-docs.deepseek.com/quick_start/pricing/
# Pre-switch flat card through 16-08-2026 16:00 UTC; after that, off-peak or peak.
# Pick the table from the REQUESTED model id — never apply Flash rates to a Pro run
# (H2652). H1210 historical arm-B used older `deepseek-chat` 0.27 / 0.07 / 1.10 —
# do not reprice that run with these constants.
# Org maps: Uprava docs/DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md (H2439)
# and docs/DEEPSEEK_V4_PRO_0813_ORG_LANE_MAP_2026-08.md (H2651).
PRICE_CARDS = {
    'pre-1608': {
        'deepseek-v4-flash': {'cache_miss_in': 0.14, 'cache_hit_in': 0.0028, 'out': 0.28},
        'deepseek-v4-pro': {'cache_miss_in': 0.435, 'cache_hit_in': 0.003625, 'out': 0.87},
    },
    'after-1608-offpeak': {
        'deepseek-v4-flash': {'cache_miss_in': 0.22, 'cache_hit_in': 0.007, 'out': 0.66},
        'deepseek-v4-pro': {'cache_miss_in': 0.66, 'cache_hit_in': 0.022, 'out': 1.98},
    },
    'after-1608-peak': {
        'deepseek-v4-flash': {'cache_miss_in': 0.44, 'cache_hit_in': 0.014, 'out': 1.32},
        'deepseek-v4-pro': {'cache_miss_in': 1.32, 'cache_hit_in': 0.044, 'out': 3.96},
    },
}
# Backward-compat: the pre-switch table. prep_pack selftest pins miss == 0.14.
PRICE_BY_MODEL = {k: dict(v) for k, v in PRICE_CARDS['pre-1608'].items()}
PRICE_CACHE_MISS_IN = PRICE_BY_MODEL['deepseek-v4-flash']['cache_miss_in']
PRICE_CACHE_HIT_IN = PRICE_BY_MODEL['deepseek-v4-flash']['cache_hit_in']
PRICE_OUT = PRICE_BY_MODEL['deepseek-v4-flash']['out']
DEFAULT_MODEL = 'deepseek-v4-flash'
DEFAULT_MAX_TOKENS = 32768
ALLOWED_EFFORTS = ('low', 'high', 'max')
TRANSPORT = 'openai-sdk-stream'

MAX_ATTEMPTS = 3

# Peak/off-peak switch (first-party pricing page). After this instant, peak hours
# cost 1.5–4.7× today's card (cache-hit up to ~12×). Standing PWG rule 13-08-2026:
# never pay peak; run off-peak or defer. Europe/CEST = UTC+2 in August:
# 01–04 UTC → 03–06 CEST, 06–10 UTC → 08–12 CEST.
PEAK_BILLING_START = datetime.datetime(2026, 8, 16, 16, 0, tzinfo=datetime.timezone.utc)
PEAK_WINDOWS_UTC = ((1, 4), (6, 10))  # [start, end) hours UTC


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def deepseek_is_peak(now=None):
    """True only after the 16-08-2026 16:00 UTC switch AND inside a peak window."""
    now = now or utcnow()
    if now < PEAK_BILLING_START:
        return False
    hour = now.hour
    return any(start <= hour < end for start, end in PEAK_WINDOWS_UTC)


def price_card_name(now=None):
    """Which PRICE_CARDS key applies at `now` (UTC)."""
    now = now or utcnow()
    if now < PEAK_BILLING_START:
        return 'pre-1608'
    if deepseek_is_peak(now):
        return 'after-1608-peak'
    return 'after-1608-offpeak'


def prices_for(model, now=None, card=None):
    """Return (price_card, {cache_miss_in, cache_hit_in, out}) for model at `now`."""
    card = card or price_card_name(now)
    table = PRICE_CARDS.get(card) or PRICE_CARDS['pre-1608']
    row = table.get(model) or table['deepseek-v4-flash']
    return card, dict(row)


def _selftest_peak():
    before = datetime.datetime(2026, 8, 16, 15, 59, tzinfo=datetime.timezone.utc)
    after_off = datetime.datetime(2026, 8, 16, 16, 30, tzinfo=datetime.timezone.utc)  # 16:30 UTC
    after_peak_am = datetime.datetime(2026, 8, 17, 2, 0, tzinfo=datetime.timezone.utc)
    after_peak_eu = datetime.datetime(2026, 8, 17, 8, 0, tzinfo=datetime.timezone.utc)  # 10:00 CEST
    failed = 0
    for now, want, name in (
        (before, False, 'pre-switch 15:59 UTC'),
        (after_off, False, 'post-switch off-peak 16:30 UTC'),
        (after_peak_am, True, 'post-switch 02:00 UTC / 04:00 CEST'),
        (after_peak_eu, True, 'post-switch 08:00 UTC / 10:00 CEST'),
    ):
        got = deepseek_is_peak(now)
        status = 'ok' if got == want else 'FAIL'
        if got != want:
            failed += 1
        print('  %s  peak=%s want=%s  %s' % (status, got, want, name))
    if failed:
        sys.exit('deepseek peak selftest: %d check(s) failed' % failed)
    print('deepseek peak selftest: 0 check(s) failed')


def _selftest_price():
    before = datetime.datetime(2026, 8, 16, 15, 59, tzinfo=datetime.timezone.utc)
    after_off = datetime.datetime(2026, 8, 16, 16, 30, tzinfo=datetime.timezone.utc)
    after_peak = datetime.datetime(2026, 8, 17, 2, 0, tzinfo=datetime.timezone.utc)
    failed = 0
    checks = (
        (before, 'pre-1608', 0.28, 0.14),
        (after_off, 'after-1608-offpeak', 0.66, 0.22),
        (after_peak, 'after-1608-peak', 1.32, 0.44),
    )
    for now, want_card, want_out, want_miss in checks:
        card, row = prices_for('deepseek-v4-flash', now)
        ok = card == want_card and row['out'] == want_out and row['cache_miss_in'] == want_miss
        if not ok:
            failed += 1
        print('  %s  card=%s want=%s out=%s  %s' % (
            'ok' if ok else 'FAIL', card, want_card, row['out'], now.isoformat()))
    if DEFAULT_MODEL != 'deepseek-v4-flash':
        failed += 1
        print('  FAIL  DEFAULT_MODEL=%s' % DEFAULT_MODEL)
    if DEFAULT_MAX_TOKENS != 32768:
        failed += 1
        print('  FAIL  DEFAULT_MAX_TOKENS=%s' % DEFAULT_MAX_TOKENS)
    if PRICE_CACHE_MISS_IN != 0.14:
        failed += 1
        print('  FAIL  PRICE_CACHE_MISS_IN=%s (compat pin is 0.14)' % PRICE_CACHE_MISS_IN)
    if failed:
        sys.exit('deepseek price selftest: %d check(s) failed' % failed)
    print('deepseek price selftest: 0 check(s) failed')


def _get(obj, name, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _usage_as_dict(usage):
    if usage is None:
        return {}
    if isinstance(usage, dict):
        details = usage.get('completion_tokens_details') or {}
        reasoning = (details.get('reasoning_tokens')
                     if isinstance(details, dict) else _get(details, 'reasoning_tokens'))
        return {
            'prompt_tokens': usage.get('prompt_tokens'),
            'completion_tokens': usage.get('completion_tokens'),
            'prompt_cache_hit_tokens': usage.get('prompt_cache_hit_tokens'),
            'prompt_cache_miss_tokens': usage.get('prompt_cache_miss_tokens'),
            'reasoning_tokens': reasoning,
        }
    details = _get(usage, 'completion_tokens_details')
    return {
        'prompt_tokens': _get(usage, 'prompt_tokens'),
        'completion_tokens': _get(usage, 'completion_tokens'),
        'prompt_cache_hit_tokens': _get(usage, 'prompt_cache_hit_tokens'),
        'prompt_cache_miss_tokens': _get(usage, 'prompt_cache_miss_tokens'),
        'reasoning_tokens': _get(details, 'reasoning_tokens') if details else None,
    }


def accumulate_stream(stream):
    """Fold an OpenAI-style chat.completions stream into content + usage.

    DeepSeek thinking mode sends delta.reasoning_content first, then content.
    Usage is on the last chunk when stream_options.include_usage is True.
    """
    content_parts = []
    reasoning_parts = []
    finish_reason = None
    served_model = None
    usage = {}
    n_chunks = 0
    for chunk in stream:
        n_chunks += 1
        served_model = _get(chunk, 'model') or served_model
        u = _get(chunk, 'usage')
        if u:
            usage = _usage_as_dict(u)
        for ch in (_get(chunk, 'choices') or []):
            finish_reason = _get(ch, 'finish_reason') or finish_reason
            delta = _get(ch, 'delta') or {}
            rc = _get(delta, 'reasoning_content')
            if rc:
                reasoning_parts.append(rc)
            c = _get(delta, 'content')
            if c:
                content_parts.append(c)
    return {
        'content': ''.join(content_parts),
        'reasoning': ''.join(reasoning_parts),
        'usage': usage,
        'finish_reason': finish_reason,
        'served_model': served_model,
        'n_chunks': n_chunks,
    }


def mock_long_thinking_stream(n_think=9000, chunk=100, content='{"ok":true}'):
    """Hermetic SSE stand-in: >8192 thinking tokens, no urllib IncompleteRead."""
    remaining = 'T' * n_think
    while remaining:
        piece, remaining = remaining[:chunk], remaining[chunk:]
        yield {
            'model': 'deepseek-v4-flash',
            'choices': [{'delta': {'reasoning_content': piece}, 'finish_reason': None}],
            'usage': None,
        }
    yield {
        'model': 'deepseek-v4-flash',
        'choices': [{'delta': {'content': content}, 'finish_reason': 'stop'}],
        'usage': None,
    }
    yield {
        'model': 'deepseek-v4-flash',
        'choices': [],
        'usage': {
            'prompt_tokens': 10,
            'completion_tokens': n_think + 5,
            'prompt_cache_hit_tokens': 0,
            'prompt_cache_miss_tokens': 10,
            'completion_tokens_details': {'reasoning_tokens': n_think},
        },
    }


def _selftest_stream():
    folded = accumulate_stream(mock_long_thinking_stream(9000))
    failed = 0
    if len(folded['reasoning']) <= 8192:
        failed += 1
        print('  FAIL  reasoning chars=%d (need >8192)' % len(folded['reasoning']))
    else:
        print('  ok  reasoning chars=%d' % len(folded['reasoning']))
    if folded['content'] != '{"ok":true}':
        failed += 1
        print('  FAIL  content=%r' % folded['content'])
    if (folded.get('usage') or {}).get('reasoning_tokens') != 9000:
        failed += 1
        print('  FAIL  usage reasoning_tokens=%s' % (folded.get('usage') or {}).get('reasoning_tokens'))

    class _Completions:
        def create(self, **kwargs):
            if not kwargs.get('stream'):
                raise AssertionError('stream=True required')
            return mock_long_thinking_stream(8500)

    class _Chat:
        completions = _Completions()

    class _Client:
        chat = _Chat()

    ds = DeepSeek('https://api.deepseek.com', 'sk-test', DEFAULT_MODEL,
                  DEFAULT_MAX_TOKENS, client=_Client())
    text, rec = ds.chat('sys', '{"ping":true}', 'mock-8k')
    if text != '{"ok":true}':
        failed += 1
        print('  FAIL  chat content=%r' % text)
    if rec.get('transport') != TRANSPORT:
        failed += 1
        print('  FAIL  transport=%s' % rec.get('transport'))
    if rec.get('reasoning_tokens') != 8500:
        failed += 1
        print('  FAIL  chat reasoning_tokens=%s' % rec.get('reasoning_tokens'))
    if rec.get('price_card') is None:
        failed += 1
        print('  FAIL  missing price_card')
    if DEFAULT_MODEL != 'deepseek-v4-flash':
        failed += 1
    if failed:
        sys.exit('deepseek stream selftest: %d check(s) failed' % failed)
    print('deepseek stream selftest: 0 check(s) failed')


def refuse_if_peak(now=None):
    """Exit before the first HTTP byte if this would be billed at peak.

    Escape: ALLOW_DEEPSEEK_PEAK=1 (must be explicit; never the default).
    """
    if os.environ.get('ALLOW_DEEPSEEK_PEAK') == '1':
        print('WARN: ALLOW_DEEPSEEK_PEAK=1 — peak billing not refused', file=sys.stderr)
        return
    now = now or utcnow()
    if not deepseek_is_peak(now):
        return
    sys.exit(
        'REFUSE: DeepSeek peak hours after 16-08-2026 16:00 UTC '
        '(01:00-04:00 and 06:00-10:00 UTC = 03:00-06:00 and 08:00-12:00 CEST). '
        'Defer the job or wait for off-peak. Override: ALLOW_DEEPSEEK_PEAK=1.'
    )


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

    DeepSeek with response_format=json_object normally returns bare JSON, but the
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


def _is_auth_or_unpaid(exc):
    status = getattr(exc, 'status_code', None)
    if status in (401, 402):
        return True
    return type(exc).__name__ in ('AuthenticationError', 'PermissionDeniedError')


class DeepSeek:
    def __init__(self, base, key, model, max_tokens, timeout=600, reasoning_effort=None,
                 client=None):
        self.base = (base or 'https://api.deepseek.com').rstrip('/')
        self.url = self.base + '/chat/completions'
        self.key = key
        self.model = model
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.reasoning_effort = reasoning_effort
        self._client = client
        card, prices = prices_for(model)
        self.price_card = card
        self.prices = prices
        self.lock = threading.Lock()
        self.calls = []

    def _make_client(self):
        if self._client is not None:
            return self._client
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError(
                'openai package required for DeepSeek.chat '
                '(pin: RussianTranslation/requirements.txt)'
            ) from e
        return OpenAI(
            api_key=self.key,
            base_url=self.base,
            timeout=self.timeout,
            max_retries=0,
        )

    def chat(self, system, user, label):
        create_kwargs = {
            'model': self.model,
            'messages': [{'role': 'system', 'content': system},
                         {'role': 'user', 'content': user}],
            'response_format': {'type': 'json_object'},
            'temperature': 0.2,
            'max_tokens': self.max_tokens,
            'stream': True,
            'stream_options': {'include_usage': True},
        }
        extra_body = {}
        if self.reasoning_effort:
            # Official DeepSeek thinking stream: reasoning_effort + extra_body.thinking.
            create_kwargs['reasoning_effort'] = self.reasoning_effort
            extra_body['thinking'] = {'type': 'enabled'}
        if extra_body:
            create_kwargs['extra_body'] = extra_body
        t0 = time.time()
        last = None
        card, prices = prices_for(self.model)
        self.price_card = card
        self.prices = prices
        for attempt in range(1, 4):                 # transport-only retries, with backoff
            try:
                client = self._make_client()
                stream = client.chat.completions.create(**create_kwargs)
                folded = accumulate_stream(stream)
                dt = time.time() - t0
                usage = folded.get('usage') or {}
                rec = {'label': label, 'latency_s': round(dt, 2),
                       'transport': TRANSPORT, 'transport_attempts': attempt,
                       'requested_model': self.model,
                       'served_model': folded.get('served_model'),
                       'model_matches_request': folded.get('served_model') == self.model,
                       'reasoning_effort': self.reasoning_effort,
                       'prompt_tokens': usage.get('prompt_tokens'),
                       'completion_tokens': usage.get('completion_tokens'),
                       'reasoning_tokens': usage.get('reasoning_tokens'),
                       'cache_hit_tokens': usage.get('prompt_cache_hit_tokens'),
                       'cache_miss_tokens': usage.get('prompt_cache_miss_tokens'),
                       'finish_reason': folded.get('finish_reason'),
                       'n_chunks': folded.get('n_chunks'),
                       'price_card': card,
                       'max_tokens': self.max_tokens}
                if rec['reasoning_tokens'] is None and folded.get('reasoning'):
                    rec['reasoning_chars'] = len(folded['reasoning'])
                with self.lock:
                    self.calls.append(rec)
                return folded.get('content') or None, rec
            # Deliberately broad: H2652's urllib path died on http.client.IncompleteRead
            # (an HTTPException, not OSError/URLError). The official SDK stream is the
            # replacement; any remaining transport exception must cost this call, never
            # the worker thread. 401/402 are spend-fence stops — no retry.
            except Exception as e:  # noqa: BLE001 — see above
                last = e
                if _is_auth_or_unpaid(e):
                    break
                if attempt < 3:
                    time.sleep(2 ** attempt)
        dt = time.time() - t0
        rec = {'label': label, 'latency_s': round(dt, 2), 'transport': TRANSPORT,
               'transport_attempts': 3 if last and not _is_auth_or_unpaid(last) else 1,
               'price_card': card, 'max_tokens': self.max_tokens,
               'error': '%s: %s' % (type(last).__name__, last) if last else 'unknown'}
        if last and _is_auth_or_unpaid(last):
            rec['fence'] = '401/402'
        with self.lock:
            self.calls.append(rec)
        return None, rec

    def cost(self):
        usd = 0.0
        miss = hit = out = 0
        cards = set()
        for c in self.calls:
            card = c.get('price_card') or self.price_card
            cards.add(card)
            _, p = prices_for(self.model, card=card)
            c_miss = c.get('cache_miss_tokens') or 0
            c_hit = c.get('cache_hit_tokens') or 0
            c_out = c.get('completion_tokens') or 0
            if not (c_miss or c_hit):
                c_miss = c.get('prompt_tokens') or 0
            miss += c_miss
            hit += c_hit
            out += c_out
            usd += (c_miss / 1e6 * p['cache_miss_in']
                    + c_hit / 1e6 * p['cache_hit_in']
                    + c_out / 1e6 * p['out'])
        p = self.prices
        return {
            'cache_miss_in_tokens': miss, 'cache_hit_in_tokens': hit, 'out_tokens': out,
            'usd': round(usd, 4),
            'price_table': dict(p),
            'price_model': self.model,
            'price_card': self.price_card if len(cards) <= 1 else 'mixed',
            'price_cards': sorted(x for x in cards if x),
            'reasoning_effort': self.reasoning_effort,
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
    if '--selftest-peak' in sys.argv:
        _selftest_peak()
        return
    if '--selftest-price' in sys.argv:
        _selftest_price()
        return
    if '--selftest-stream' in sys.argv:
        _selftest_stream()
        return
    if '--selftest' in sys.argv:
        _selftest_peak()
        _selftest_price()
        _selftest_stream()
        return
    ap = argparse.ArgumentParser()
    ap.add_argument('payload')
    ap.add_argument('manifest')
    ap.add_argument('out_prefix')
    ap.add_argument('--env-file', default=None)
    ap.add_argument('--model', default=None)
    ap.add_argument('--reasoning-effort', default=None, choices=ALLOWED_EFFORTS,
                    help='Pin thinking effort (low/high/max). Omit to leave the field off '
                         '(Flash default path). Required for a scientific Pro rematch.')
    ap.add_argument('--base-url', default=None)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--max-tokens', type=int, default=DEFAULT_MAX_TOKENS)
    ap.add_argument('--timeout', type=int, default=600)
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
             or DEFAULT_MODEL)
    if not a.dry_run:
        refuse_if_peak()
    effort = (a.reasoning_effort or os.environ.get('DEEPSEEK_REASONING_EFFORT')
              or env.get('DEEPSEEK_REASONING_EFFORT') or None)
    if a.dry_run:
        print('dry-run: %d card(s), model=%s effort=%s prices=%s base=%s key=%s, '
              'schema %d B, prompt_common %d B'
              % (len(cards), model, effort or '-',
                 PRICE_BY_MODEL.get(model, PRICE_BY_MODEL['deepseek-v4-flash']),
                 base, 'present' if key else 'MISSING',
                 len(json.dumps(schema)), len(common)))
        return
    if not key:
        sys.exit('FAIL: no DEEPSEEK_API_KEY in env or --env-file (arm B needs the external '
                 'generator; report it BLOCKED rather than substituting a model)')

    ds = DeepSeek(base, key, model, a.max_tokens, timeout=a.timeout,
                  reasoning_effort=effort)
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
        'transport': TRANSPORT, 'price_card': ds.price_card,
        'max_tokens': a.max_tokens,
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
