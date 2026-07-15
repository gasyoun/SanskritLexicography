#!/usr/bin/env python
"""Standalone selftests for economy_ledger.py (H960 gap: economy-telemetry).

Kept OUT of window_selftest.py deliberately (that file is a LANG_PARITY-tracked shared
file the parent session owns). Parity-free; run directly:

    python src/pilot/economy_ledger_selftest.py

Model: authored by Opus 4.8 (claude-opus-4-8) for handoff H960.
"""
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import economy_ledger as el
import parse_workflow_cost as pwc


def fail(message):
    raise AssertionError(message)


def approx(a, b, tol=1e-9):
    return a is not None and b is not None and abs(a - b) <= tol


def outcome_row(run_id, window, agents_used=None, clean=None, tokens=None, note=''):
    """Build a synthetic kind=='outcome' row. Passing agents_used/clean/tokens=None
    with a `note` mimics the w08/w09 nulled-into-free-text rows."""
    return {
        'ts': '2026-07-14T00:00:00Z', 'kind': 'outcome', 'run_id': run_id,
        'window': window, 'handoff': 'HTEST',
        'outcome': {'cards': None, 'audit_clean': clean, 'agents_used': agents_used,
                    'subagent_tokens': tokens, 'kill_timeouts': None, 'conn_errors': None,
                    'budget_kill_switch_tripped': False},
        'note': note,
    }


# ---------------------------------------------------------------------------
# 1. synthetic: agents_per_clean + [floor,ceil,true_upper] band == hand-computed
# ---------------------------------------------------------------------------
def test_synthetic_agents_per_clean_and_band():
    rows = [outcome_row('r_full', 'no_pwg_wA', agents_used=10, clean=5, tokens=1_000_000)]
    led = el.build_ledger(rows)
    run = led['runs'][0]

    if run['agents_per_clean'] != 2.0:
        fail('agents_per_clean must be 10/5=2.0, got %s' % run['agents_per_clean'])
    if run['status'] != 'priced':
        fail('full row must be status=priced, got %s' % run['status'])

    # hand-computed band for 1,000,000 tokens over 5 clean:
    #   floor = 1e6 * 0.30 / 1e6 / 5 = 0.06 ; ceil = 1e6 * 3.00 /1e6 /5 = 0.60
    #   true_upper = 1e6 * 15.00 /1e6 /5 = 3.00
    band = run['cost_per_clean']
    if not approx(band['floor_usd'], 0.06):
        fail('band floor must be 0.06, got %s' % band['floor_usd'])
    if not approx(band['ceil_usd'], 0.60):
        fail('band ceil must be 0.60, got %s' % band['ceil_usd'])
    if not approx(band['true_upper_output_rate_usd'], 3.00):
        fail('band true_upper must be 3.00, got %s' % band['true_upper_output_rate_usd'])
    if 'EXCLUDES output premium' not in band['basis']:
        fail('band basis must flag the excluded output premium')


# ---------------------------------------------------------------------------
# 2. clean==0 -> excluded from division, reported wasted, tokens still pooled
# ---------------------------------------------------------------------------
def test_clean_zero_is_wasted_never_divided():
    rows = [
        outcome_row('r_full', 'no_pwg_wA', agents_used=10, clean=5, tokens=1_000_000),
        outcome_row('r_wasted', 'medium_wB', agents_used=8, clean=0, tokens=500_000),
    ]
    led = el.build_ledger(rows)
    wasted = [r for r in led['runs'] if r['run_id'] == 'r_wasted'][0]
    if wasted['status'] != 'wasted_calls':
        fail('clean=0 must be status=wasted_calls, got %s' % wasted['status'])
    if wasted['agents_per_clean'] is not None:
        fail('clean=0 must NEVER carry an agents_per_clean value')
    if wasted['cost_per_clean'] is not None:
        fail('clean=0 must NEVER carry a per-run cost (no division by zero)')
    if 'wasted_calls' not in wasted['flags']:
        fail('clean=0 must be flagged wasted_calls')

    # reported in the wasted_calls list with its agents+tokens
    wl = led['wasted_calls']
    if not any(w['run_id'] == 'r_wasted' and w['agents_used'] == 8 and w['tokens'] == 500_000
               for w in wl):
        fail('wasted run must appear in wasted_calls with agents+tokens')
    if led['aggregate']['wasted_agents'] != 8 or led['aggregate']['wasted_tokens'] != 500_000:
        fail('aggregate wasted_agents/tokens must total the clean=0 rows')

    # tokens still POOL into the aggregate band (1.5M over 5 clean), but agents_per_clean
    # aggregate excludes the wasted run entirely (only the full run's 10/5 counts).
    agg = led['aggregate']
    if agg['total_tokens'] != 1_500_000 or agg['total_clean'] != 5:
        fail('pooled band must include wasted tokens (1.5M) over 5 clean, got %s/%s'
             % (agg['total_tokens'], agg['total_clean']))
    if not approx(agg['agents_per_clean_incl_requeues'], 2.0):
        fail('agents_per_clean aggregate must exclude the wasted run (10/5=2.0), got %s'
             % agg['agents_per_clean_incl_requeues'])


# ---------------------------------------------------------------------------
# 3. nulled-into-note row -> incomplete on agents, but tokens ARE priced
# ---------------------------------------------------------------------------
def test_nulled_row_incomplete_but_priced():
    rows = [outcome_row(
        'r_nulled', 'no_pwg_w08',
        note='cards=21 ok=2 clean=4 defect=1 subagent_tokens=800000 duration_ms=5')]
    led = el.build_ledger(rows)
    run = led['runs'][0]

    if run['provenance'] != 'nulled_note':
        fail('nulled row provenance must be nulled_note, got %s' % run['provenance'])
    if run['agents_used'] is not None:
        fail('agents_used must stay None (note carries no agents_used key)')
    if 'calls_per_clean_incomplete' not in run['flags']:
        fail('nulled row must be flagged calls_per_clean_incomplete')
    if run['agents_per_clean'] is not None:
        fail('nulled row must NOT produce an agents_per_clean value')
    if run['status'] != 'incomplete':
        fail('nulled row status must be incomplete, got %s' % run['status'])

    # but clean+tokens recovered from the note -> band IS priced.
    # floor = 800000*0.30/1e6/4 = 0.06 ; ceil = 800000*3.00/1e6/4 = 0.60
    band = run['cost_per_clean']
    if band is None:
        fail('nulled row tokens MUST still be priced (clean+tokens recovered from note)')
    if not approx(band['floor_usd'], 0.06) or not approx(band['ceil_usd'], 0.60):
        fail('nulled row band must be [0.06,0.60], got %s' % band)


# ---------------------------------------------------------------------------
# 4. DEDUP keyed on run_id, NOT window; conflicting re-append surfaced
# ---------------------------------------------------------------------------
def test_dedup_on_run_id_not_window():
    # same window label reused for two distinct runs (fresh + requeue) -> both kept
    rows = [
        outcome_row('r_fresh', 'no_pwg_w03', agents_used=10, clean=5, tokens=1_000_000),
        outcome_row('r_requeue', 'no_pwg_w03', agents_used=6, clean=6, tokens=600_000),
    ]
    led = el.build_ledger(rows)
    if len(led['runs']) != 2:
        fail('window-label collision must NOT collapse distinct run_ids, got %d rows'
             % len(led['runs']))

    # exact re-append of the SAME run_id is idempotent -> deduped to one
    rows2 = rows + [outcome_row('r_fresh', 'no_pwg_w03', agents_used=10, clean=5, tokens=1_000_000)]
    led2 = el.build_ledger(rows2)
    if len(led2['runs']) != 2:
        fail('exact re-append of a run_id must be idempotent, got %d rows' % len(led2['runs']))
    if led2['conflicting_run_ids']:
        fail('an exact re-append is NOT a conflict, got %s' % led2['conflicting_run_ids'])

    # re-append of same run_id with DIFFERENT figures -> conflict surfaced
    rows3 = rows + [outcome_row('r_fresh', 'no_pwg_w03', agents_used=99, clean=5, tokens=1_000_000)]
    led3 = el.build_ledger(rows3)
    if led3['conflicting_run_ids'] != ['r_fresh']:
        fail('conflicting re-append must surface run_id, got %s' % led3['conflicting_run_ids'])


# ---------------------------------------------------------------------------
# 5. ledger IMPORTS PRICE (single source of truth), never duplicates rates
# ---------------------------------------------------------------------------
def test_ledger_imports_price_not_duplicated():
    if el.PRICE is not pwc.PRICE:
        fail('economy_ledger.PRICE must BE parse_workflow_cost.PRICE (same object), not a copy')
    src = open(os.path.join(HERE, 'economy_ledger.py'), encoding='utf-8').read()
    # no re-hardcoded rate literals: the module must not contain its own PRICE dict
    if "PRICE = {" in src or "'cache_read': 0.30" in src:
        fail('economy_ledger must not re-hardcode a rate table; import pwc.PRICE only')


# ---------------------------------------------------------------------------
# 6. gate fires on AGGREGATE breach only, never per-card
# ---------------------------------------------------------------------------
def test_gate_is_aggregate_only():
    # one cheap run + one absurdly expensive single run; aggregate stays modest.
    rows = [
        outcome_row('r_cheap', 'no_pwg_wA', agents_used=2, clean=100, tokens=1_000_000),
        outcome_row('r_spike', 'no_pwg_wB', agents_used=50, clean=1, tokens=1_000_000),
    ]
    led = el.build_ledger(rows)
    # aggregate agents_per_clean = (2+50)/(100+1) = 52/101 = 0.5148 -> under a ceiling of 5
    if el.gate(led, ceil_agents_per_clean=5.0) != 0:
        fail('a single per-card spike must NOT flip the aggregate gate')
    # but a ceiling below the aggregate breaches
    if el.gate(led, ceil_agents_per_clean=0.4) != 1:
        fail('aggregate above ceiling must breach the gate')
    # cost gate: aggregate ceil band per clean is small; a tiny ceiling breaches
    if el.gate(led, ceil_cost_per_clean=0.0001) != 1:
        fail('cost ceiling below aggregate must breach')
    if el.gate(led, ceil_cost_per_clean=1e6) != 0:
        fail('a huge cost ceiling must pass')


# ---------------------------------------------------------------------------
# 7. atomic write round-trips to a tempfile (mirrors write_census)
# ---------------------------------------------------------------------------
def test_write_ledger_roundtrip():
    rows = [outcome_row('r_full', 'no_pwg_wA', agents_used=10, clean=5, tokens=1_000_000)]
    d = tempfile.mkdtemp()
    out = os.path.join(d, 'economy_ledger.v1.json')
    el.write_ledger(out, rows=rows, source_log='synthetic.jsonl')
    payload = json.load(open(out, encoding='utf-8'))
    if payload['schema'] != 'pwg.economy_ledger.v1':
        fail('written ledger must carry schema pwg.economy_ledger.v1, got %s' % payload['schema'])
    if payload['runs'][0]['agents_per_clean'] != 2.0:
        fail('written ledger figures must survive the round-trip')


# ---------------------------------------------------------------------------
# 8. INTEGRATION: real frozen log reproduces the pinned figures exactly
# ---------------------------------------------------------------------------
def test_integration_real_frozen_log():
    rows = el.read_rows(el.FROZEN_LOG)   # read-only
    led = el.build_ledger(rows)

    # -- coverage line: the exact refinement-1 string --
    expected_line = ('6/9 outcome rows carry structured agents_used; '
                     '5/9 enter agents-per-clean '
                     '(1 has clean=0 -> wasted_calls; 3 nulled -> incomplete)')
    if led['coverage']['line'] != expected_line:
        fail('coverage line drifted:\n  got: %s\n  exp: %s'
             % (led['coverage']['line'], expected_line))
    cov = led['coverage']
    if (cov['outcome_rows'], cov['structured_agents_used'], cov['enter_agents_per_clean'],
            cov['clean0_wasted'], cov['nulled_incomplete']) != (9, 6, 5, 1, 3):
        fail('coverage counts drifted: %s' % cov)

    # -- per-run w07 -> 38/5 = 7.6 --
    w07 = [r for r in led['runs'] if r['run_id'] == 'wf_5ed6f8e0-b0b'][0]
    if w07['agents_per_clean'] != 7.6:
        fail('w07 (wf_5ed6f8e0-b0b) agents_per_clean must be 38/5=7.6, got %s'
             % w07['agents_per_clean'])

    agg = led['aggregate']

    # -- headline aggregate: 139 agents / 49 clean = 2.836735 (incl requeues) --
    if agg['agents_per_clean_incl_requeues'] != round(139 / 49, 6):
        fail('agents_per_clean incl requeues must be 139/49=2.836735, got %s'
             % agg['agents_per_clean_incl_requeues'])
    if agg['agents_per_clean_incl_requeues_label'] != 'total agents to fully drain incl. requeues':
        fail('headline aggregate MUST be labeled "total agents to fully drain incl. requeues"')

    # -- first-pass: 95 agents / 27 clean = 3.518519 --
    if agg['agents_per_clean_first_pass'] != round(95 / 27, 6):
        fail('first-pass agents_per_clean must be 95/27=3.518519, got %s'
             % agg['agents_per_clean_first_pass'])

    # -- pooled cost band: 13,739,312 tokens / 59 clean --
    if agg['total_tokens'] != 13_739_312 or agg['total_clean'] != 59:
        fail('pooled totals must be 13,739,312 tokens / 59 clean, got %s/%s'
             % (agg['total_tokens'], agg['total_clean']))
    band = agg['cost_per_clean_band']
    # hand-pinned REAL numbers (recomputed honestly from the frozen log; the audit's cited
    # $0.073-$0.731 did NOT reconstruct — these are what the log actually yields):
    if band['floor_usd'] != 0.069861:
        fail('pooled floor must be $0.069861 (cache-read rate), got %s' % band['floor_usd'])
    if band['ceil_usd'] != 0.698609:
        fail('pooled ceil must be $0.698609 (fresh-input rate), got %s' % band['ceil_usd'])
    if band['true_upper_output_rate_usd'] != 3.493045:
        fail('true upper (output rate) must be $3.493045, got %s'
             % band['true_upper_output_rate_usd'])
    # the band figures must also equal the formula recomputed straight from PRICE
    # (formula pin: a rate edit breaks this loudly, like h809_selftest's cache-multiplier pin)
    if not approx(band['ceil_usd'], round(13_739_312 * pwc.PRICE['input'] / 1e6 / 59, 6)):
        fail('band ceil must equal tokens*input_rate/1e6/clean from PRICE')
    if not approx(band['floor_usd'], round(13_739_312 * pwc.PRICE['cache_read'] / 1e6 / 59, 6)):
        fail('band floor must equal tokens*cache_read_rate/1e6/clean from PRICE')

    # -- wasted (row 6, h317_w1b): 58 agents / 1,798,042 tokens, 0 clean --
    if agg['wasted_agents'] != 58 or agg['wasted_tokens'] != 1_798_042:
        fail('wasted totals must be 58 agents / 1,798,042 tokens, got %s/%s'
             % (agg['wasted_agents'], agg['wasted_tokens']))

    # -- no spurious conflicts on the real log (all 9 run_ids distinct) --
    if led['conflicting_run_ids']:
        fail('real log must yield no conflicting_run_ids, got %s' % led['conflicting_run_ids'])


def test_all_wasted_summary_does_not_crash():
    # Every row clean=0 -> no outcome row enters the agents-per-clean set, so the aggregate
    # agents_per_clean / cost band are None. summary_lines() (the main() print path) must render the
    # honest 'n/a' summary, not raise `TypeError: must be real number, not NoneType` — this is the
    # exact 'everything wasted' case the ledger exists to report honestly.
    rows = [
        outcome_row('w1', 'no_pwg_wA', agents_used=8, clean=0, tokens=500_000),
        outcome_row('w2', 'no_pwg_wB', agents_used=6, clean=0, tokens=300_000),
    ]
    led = el.build_ledger(rows)
    agg = led['aggregate']
    if agg['agents_per_clean_incl_requeues'] is not None or agg['cost_per_clean_band'] is not None:
        fail('an all-wasted log must yield None aggregates, got %r' % agg)
    lines = el.summary_lines(led)           # must NOT raise on the None aggregates
    joined = '\n'.join(lines)
    if 'n/a' not in joined or 'wasted: 14 agents' not in joined:
        fail('all-wasted summary must report n/a + the wasted totals, got:\n%s' % joined)


def main():
    tests = [
        test_synthetic_agents_per_clean_and_band,
        test_clean_zero_is_wasted_never_divided,
        test_nulled_row_incomplete_but_priced,
        test_dedup_on_run_id_not_window,
        test_ledger_imports_price_not_duplicated,
        test_gate_is_aggregate_only,
        test_write_ledger_roundtrip,
        test_integration_real_frozen_log,
        test_all_wasted_summary_does_not_crash,
    ]
    for t in tests:
        t()
        print('PASS:', t.__name__)
    print('economy_ledger selftest OK')


if __name__ == '__main__':
    main()
