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

# Claude Sonnet 5 (claude-sonnet-5) standard LIST rates, $ per million tokens
# (cache-write = 5m TTL = 1.25x input; cache-read = 0.1x input). Confirmed 12-07-2026
# via the /claude-api skill (H809 W2). NOTE: these are numerically identical to the
# prior Sonnet 4.x list rates ($3/$15) — Sonnet 4.6 and Sonnet 5 share the same list
# pricing — so the golden-window $ total (42,316,604 tokens -> $79.83) is UNCHANGED.
# The Sonnet 5 introductory promo ($2.00 input / $10.00 output, through 2026-08-31)
# is deliberately NOT applied here: this table is list-rate basis (the promo is a
# time-boxed discount, not the standing rate). Apply the promo only for an as-run
# reconciliation, and see COST_CEIL_* in perf_preflight.py — the promo would move
# $/agent ~-33% (>20%), which is a FLAG-for-human event, not an auto-retune.
PRICE = {'input': 3.00, 'output': 15.00, 'cache_write': 3.75, 'cache_read': 0.30}

# --- cache writes are TTL-priced; a single 'cache_write' rate cannot be right ------
# H2158 (02-08-2026): a cache write bills by the TTL bucket it lands in --
#   5-minute TTL = 1.25x base input;  1-hour TTL = 2.0x base input.
# PRICE['cache_write'] above is the FIVE-MINUTE rate, and it is kept only as the
# legacy alias for callers with no TTL information. The pwg_ru CLI-headless lane
# puts EVERY write in `ephemeral_1h_input_tokens` (FINDINGS §284), so pricing its
# writes at 3.75 understates that line by 1.6x -- $0.6967 against the vendor's own
# $0.800499 on the H2158 `nakzatra` envelope. The prose knew this and the constant
# did not; the two are now single-sourced so they cannot diverge again (§289).
# Rates are DERIVED from PRICE['input'] rather than restated, so a base-rate edit
# carries into both automatically.
CACHE_WRITE_TTL_MULT = {'5m': 1.25, '1h': 2.00}
PRICE['cache_write_5m'] = PRICE['input'] * CACHE_WRITE_TTL_MULT['5m']   # 3.75
PRICE['cache_write_1h'] = PRICE['input'] * CACHE_WRITE_TTL_MULT['1h']   # 6.00


def cache_write_rate(ttl):
    """$/Mtok for a cache write in TTL bucket `ttl` ('5m' or '1h')."""
    try:
        return PRICE['input'] * CACHE_WRITE_TTL_MULT[ttl]
    except KeyError:
        raise ValueError("unknown cache-write TTL %r (expected '5m' or '1h')" % (ttl,))


def split_cache_creation(usage):
    """Split one usage dict's cache-creation tokens into (tokens_5m, tokens_1h, ttl_known).

    The TTL breakdown lives in `usage['cache_creation']` as
    `ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens`. Envelopes predating
    that field carry only the `cache_creation_input_tokens` total: those return
    ttl_known=False and are attributed to the 5m bucket, which preserves every
    historical figure computed before this split existed. Never guess 1h -- an
    unproven 1h attribution would inflate old runs by 1.6x.
    """
    total = usage.get('cache_creation_input_tokens', 0) or 0
    breakdown = usage.get('cache_creation')
    if isinstance(breakdown, dict):
        t5 = breakdown.get('ephemeral_5m_input_tokens', 0) or 0
        t1 = breakdown.get('ephemeral_1h_input_tokens', 0) or 0
        if t5 or t1:
            return t5, t1, True
    return total, 0, False


def usage_cost(usage, unknown_ttl='5m'):
    """$ for ONE raw usage dict, pricing each cache write at its own TTL rate.

    The single place any caller should turn a usage envelope into money -- route
    comparisons included, so both arms of an A/B are priced off one table.

    `unknown_ttl` decides only what to do with a legacy envelope carrying no TTL
    breakdown, and the right answer differs by caller (H2190):

      '5m' (default) -- REPORTING on historical transcripts. Keeps every figure
            computed before the split existed, and refuses to inflate an old run
            by 1.6x on an attribution nothing measured.
      '1h' -- COST GATES that refuse over a ceiling (`--refuse-over-cost` and kin).
            Fail CLOSED: an under-refusal spends real money, while an over-refusal
            only asks a human to look. Never default a gate to '5m'.

    When it matters which was used, report both -- `tally()` emits `cost` and
    `cost_unknown_at_1h` side by side rather than quietly picking one.
    """
    t5, t1, known = split_cache_creation(usage)
    if not known and unknown_ttl == '1h':
        t5, t1 = 0, t5
    return ((usage.get('input_tokens', 0) or 0) * PRICE['input']
            + (usage.get('output_tokens', 0) or 0) * PRICE['output']
            + t5 * PRICE['cache_write_5m']
            + t1 * PRICE['cache_write_1h']
            + (usage.get('cache_read_input_tokens', 0) or 0) * PRICE['cache_read']) / 1e6


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
    t = {'input': 0, 'cache_write': 0, 'cache_write_5m': 0, 'cache_write_1h': 0,
         'cache_read': 0, 'output': 0, 'turns': 0, 'cache_write_ttl_unknown': 0}
    for u in usage_records(path):
        t['input'] += u.get('input_tokens', 0) or 0
        t['cache_write'] += u.get('cache_creation_input_tokens', 0) or 0
        t5, t1, known = split_cache_creation(u)
        t['cache_write_5m'] += t5
        t['cache_write_1h'] += t1
        if not known:
            t['cache_write_ttl_unknown'] += t5
        t['cache_read'] += u.get('cache_read_input_tokens', 0) or 0
        t['output'] += u.get('output_tokens', 0) or 0
        t['turns'] += 1
    # logged output_tokens under-reports structured tool-call output; use the larger
    # of (logged, est-from-tool-call-chars) so cost isn't undercounted.
    t['output_est'] = max(t['output'], tooluse_output_chars(path) // 4)
    # each write priced at ITS OWN TTL rate; TTL-less legacy envelopes stay on 5m,
    # so historical totals are unchanged by the split (see split_cache_creation).
    base = (t['input'] * PRICE['input'] + t['output_est'] * PRICE['output']
            + t['cache_read'] * PRICE['cache_read']) / 1e6
    t['cost'] = base + (t['cache_write_5m'] * PRICE['cache_write_5m']
                        + t['cache_write_1h'] * PRICE['cache_write_1h']) / 1e6
    # the same tally with every TTL-less write repriced at the 1h rate: the
    # fail-closed figure a cost GATE must read (H2190). Equal to `cost` whenever
    # the TTL is known for every write, so the gap IS the unmeasured exposure.
    t['cost_unknown_at_1h'] = base + (
        (t['cache_write_5m'] - t['cache_write_ttl_unknown']) * PRICE['cache_write_5m']
        + (t['cache_write_1h'] + t['cache_write_ttl_unknown']) * PRICE['cache_write_1h']) / 1e6
    t['total_tokens'] = t['input'] + t['cache_write'] + t['cache_read'] + t['output_est']
    return t


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: parse_workflow_cost.py <transcript_dir> [...]')
    print('%-26s %8s %10s %10s %10s %9s %10s %9s' %
          ('run', 'input', 'cache_wr', 'of which1h', 'cache_rd', 'out(est)', 'total', '$cost'))
    for path in sys.argv[1:]:
        t = tally(path)
        print('%-26s %8d %10d %10d %10d %9d %10d %9.4f' %
              (os.path.basename(path), t['input'], t['cache_write'], t['cache_write_1h'],
               t['cache_read'], t['output_est'], t['total_tokens'], t['cost']))
        if t['cache_write_ttl_unknown']:
            print('%-26s   (%d cache-write tokens carried no TTL breakdown -> priced at the '
                  '5m rate $%.2f/Mtok; at the 1h rate the run costs $%.4f. A cost GATE must '
                  'read the larger figure.)'
                  % ('', t['cache_write_ttl_unknown'], PRICE['cache_write_5m'],
                     t['cost_unknown_at_1h']))


if __name__ == '__main__':
    main()
