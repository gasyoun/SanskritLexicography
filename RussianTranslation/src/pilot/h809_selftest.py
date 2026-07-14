#!/usr/bin/env python
"""Standalone selftests for the H809 scale-unblock fixes (W2 cost-rate formula, W3
no_pwg window-index auto-select + collision guard).

Kept OUT of window_selftest.py deliberately: window_selftest.py is a LANG_PARITY-
tracked SHARED file, and at the time of writing origin/master carries unresolved
parity debt on gen_opt_harness2.py (H811) that is bundled into the same ledger keys.
Editing window_selftest.py would either inherit that red gate or force blessing
another session's unverified change. These tests are parity-free, so they live here
and are run directly:  python src/pilot/h809_selftest.py

Model: authored by Opus 4.8 (claude-opus-4-8) for handoff H809.
"""
import io
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def fail(message):
    raise AssertionError(message)


def test_cost_rate_table_sonnet5_formula():
    """W2: pin the cost FORMULA (not a hardcoded $), so a future rate edit that breaks
    the cache-multiplier or the per-agent derivation fails loudly.

      - cache_write == 1.25 x input (5m TTL);  cache_read == 0.1 x input
      - Sonnet 5 (claude-sonnet-5) LIST rates are $3 input / $15 output
      - PER_AGENT_USD == round(as_run_usd / 230, 3); Sonnet 5 list rates ($3/$15) are
        numerically identical to the prior Sonnet 4.x rates, so as-run $79.83 -> $0.347
        is UNCHANGED, and the golden-window token total 42,316,604 must not drift.
    """
    import parse_workflow_cost as pwc
    import perf_preflight as pp
    p = pwc.PRICE
    if round(p['cache_write'], 6) != round(1.25 * p['input'], 6):
        fail('cache_write must be 1.25x input (5m TTL): %s vs %s'
             % (p['cache_write'], 1.25 * p['input']))
    if round(p['cache_read'], 6) != round(0.10 * p['input'], 6):
        fail('cache_read must be 0.1x input: %s vs %s' % (p['cache_read'], 0.10 * p['input']))
    if (p['input'], p['output']) != (3.00, 15.00):
        fail('Sonnet 5 list input/output must be $3/$15, got %s/%s' % (p['input'], p['output']))
    AS_RUN_USD = 79.83                  # pril10_w1 as-run (rates identical under Sonnet 5 list)
    if pp.PER_AGENT_USD != round(AS_RUN_USD / 230, 3):
        fail('PER_AGENT_USD must equal round($79.83/230, 3)=0.347, got %s' % pp.PER_AGENT_USD)
    if pp.PER_AGENT_TOKENS != 184000:
        fail('PER_AGENT_TOKENS must stay 184000, got %s' % pp.PER_AGENT_TOKENS)


def test_no_pwg_window_index_autoselect():
    """W3: `used_window_indices` derives the used set from disk (counting `_rqN`
    requeues as their base index), `next_free_index` picks max+1 (floored at 2), and an
    explicit colliding `--start-index` is refused (naming the next-free index) unless
    `--force-index`. `--plan-only` never blocks."""
    import no_pwg_scale_plan as nps
    tmp = tempfile.mkdtemp()
    here = os.path.join(tmp, 'here')
    out = os.path.join(tmp, 'out')
    os.makedirs(here)
    os.makedirs(out)
    for name in ('run_pilot_wf.no_pwg_w01.js', 'run_pilot_wf.no_pwg_w04.js',
                 'run_pilot_wf.no_pwg_w05_rq1.js'):
        open(os.path.join(here, name), 'w').close()
    for name in ('wf_output.no_pwg_w02.json', 'wf_output.no_pwg_w03.json'):
        open(os.path.join(out, name), 'w').close()
    used = nps.used_window_indices('no_pwg_w', here=here, out=out)
    if used != {1, 2, 3, 4, 5}:
        fail('used_window_indices must yield {1..5} (w05_rq1 counts as 5), got %s' % sorted(used))
    if nps.next_free_index('no_pwg_w', here=here, out=out) != 6:
        fail('next_free_index must be 6, got %s'
             % nps.next_free_index('no_pwg_w', here=here, out=out))
    empty = tempfile.mkdtemp()
    if nps.next_free_index('no_pwg_w', here=empty, out=empty) != 2:
        fail('next_free_index on empty dirs must floor at 2')


def test_no_pwg_promotion_command_is_scoped_and_executable():
    """A plan must never tell an operator to merge the repo-root default glob."""
    import no_pwg_scale_plan as nps
    cmd = nps.promotion_command(
        'src/pilot/output/wf_output.no_pwg_w07.json', 'claude-sonnet-5')
    expected = (
        'python src/promote_final_cards.py --merge '
        '--glob "src/pilot/output/wf_output.no_pwg_w07.json" '
        '--gen-model-version claude-sonnet-5')
    if cmd != expected:
        fail('promotion command drifted: %r' % cmd)
    try:
        nps.promotion_command('wf_output.json', 'sonnet')
    except ValueError:
        pass
    else:
        fail('promotion command must refuse a non-exact model alias')


def main():
    tests = [
        test_cost_rate_table_sonnet5_formula,
        test_no_pwg_window_index_autoselect,
        test_no_pwg_promotion_command_is_scoped_and_executable,
    ]
    for t in tests:
        t()
        print('PASS:', t.__name__)
    print('h809 selftest OK')


if __name__ == '__main__':
    main()
