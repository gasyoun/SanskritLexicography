#!/usr/bin/env python
"""Persistent economy ledger for the PWG->Russian headless generation runs.

A PURE, read-only reducer over the frozen `generation_api_probe_log.jsonl` outcome
rows. It answers ONE aggregate question honestly: how many subagents, and how many
dollars of token spend, did each *clean* promoted card actually cost — pooled across
windows and their requeues.

Deliberate honesty constraints baked in (from the H960 adversarial review):

  * The numerator of `agents_per_clean` is `agents_used` — the number of SUBAGENTS
    spawned for the run (`calls == agents_used` here). This is NOT the same as the
    `run_summary.calls` counter in run_observability.build_census (which counts
    model-call events). We name the metric `agents_per_clean` and never call it
    "calls per clean" without qualification.

  * A run with `audit_clean == 0` produced no clean card, so dividing by it is
    undefined. Such a run is reported as `wasted_calls`, NEVER as an agents_per_clean
    value. Its tokens still pool into the aggregate cost band (blunt total / total
    clean), but it contributes 0 to the clean denominator.

  * Three outcome rows (no_pwg_w08 / w08_rq1 / w09) had their structured outcome
    payload nulled and dumped into the free-text `note`. `subagent_tokens` and `clean`
    are recoverable from that note (so we still PRICE their tokens), but `agents_used`
    is NOT present in the note, so those rows are flagged `calls_per_clean_incomplete`
    and excluded from the agents_per_clean aggregate.

  * DEDUP is keyed on `run_id` (+ per-run provenance), NOT the window-name string:
    the label `no_pwg_w03` appears both as a fresh window and as a requeue of w02, so
    grouping by window would wrongly collapse distinct runs. An exact re-append of the
    same run_id is idempotent; a re-append carrying DIFFERENT figures is surfaced in
    `conflicting_run_ids` (mirrors run_observability.build_census's call_id dedup).

  * The cost band brackets [cache-read rate .. fresh-input rate] per token. The frozen
    log carries only the blunt `subagent_tokens` totalTokens (the billing cache-split
    is NOT recoverable), so the true billed cost lies somewhere inside the band. The
    band EXCLUDES the output premium: subagent_tokens includes OUTPUT tokens billed
    ~5x input (see parse_workflow_cost / h809_selftest cost formula), so the in-band
    ceiling (fresh-input rate) is NOT a true upper bound; `true_upper_output_rate_usd`
    prices every token at the output rate for an honest worst case.

Rates are IMPORTED from parse_workflow_cost.PRICE — never re-hardcoded here.

Offline / read-only. Run directly to print the ledger + coverage line:
    python src/pilot/economy_ledger.py                # print only
    python src/pilot/economy_ledger.py --write <path> # also write the durable JSON

Model: authored by Opus 4.8 (claude-opus-4-8) for handoff H960 (gap: economy-telemetry).
"""
import argparse
import datetime
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import parse_workflow_cost as pwc  # noqa: E402  (path insertion above must run first)

# Single source of truth for $/million-token rates — do NOT duplicate rates here.
PRICE = pwc.PRICE

SCHEMA = 'pwg.economy_ledger.v1'
FROZEN_LOG = os.path.join(HERE, 'generation_api_probe_log.jsonl')

# note key=int pattern (e.g. "subagent_tokens=1836200 clean=6 store=11562")
_NOTE_KV = re.compile(r'(\w+)=(-?\d+)\b')


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='milliseconds').replace('+00:00', 'Z')


def read_rows(path):
    """Read all jsonl rows (any kind) from the frozen log, read-only."""
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def parse_note_kv(note):
    """Recover the key=int pairs a nulled outcome row dumped into free text."""
    return {m.group(1): int(m.group(2)) for m in _NOTE_KV.finditer(note or '')}


def _normalize_outcome(row):
    """Turn one kind=='outcome' row into a normalized economy record.

    agents_used comes ONLY from the structured payload (the free-text note never
    carries it); tokens and clean fall back to the note when the structured payload
    was nulled. `provenance` records where the tokens came from.
    """
    outcome = row.get('outcome') or {}
    kv = parse_note_kv(row.get('note', ''))

    agents_used = outcome.get('agents_used')          # structured only; note has no such key
    clean = outcome.get('audit_clean')
    tokens = outcome.get('subagent_tokens')
    provenance = 'structured'
    if tokens is None:
        tokens = kv.get('subagent_tokens')
        provenance = 'nulled_note'
    if clean is None:
        clean = kv.get('clean')

    rec = {
        'run_id': row.get('run_id'),
        'window': row.get('window'),
        'handoff': row.get('handoff'),
        'agents_used': agents_used,
        'clean': clean,
        'tokens': tokens,
        'provenance': provenance,
        'is_requeue': bool(re.search(r'_rq\d+$', row.get('window') or '')),
        'flags': [],
    }

    # agents_per_clean: agents_used / clean, only when both known and clean>0
    if agents_used is None:
        rec['flags'].append('calls_per_clean_incomplete')
    if clean == 0:
        rec['flags'].append('wasted_calls')

    if agents_used is not None and clean and clean > 0:
        rec['agents_per_clean'] = round(agents_used / clean, 4)
        rec['status'] = 'priced'
    elif clean == 0:
        rec['agents_per_clean'] = None
        rec['status'] = 'wasted_calls'
    else:
        rec['agents_per_clean'] = None
        rec['status'] = 'incomplete'

    # cost band per clean — priced whenever tokens known and clean>0 (agents_used may
    # still be missing; tokens are priced regardless, per spec). clean==0 -> no division.
    if tokens is not None and clean and clean > 0:
        rec['cost_per_clean'] = _cost_band(tokens, clean)
    else:
        rec['cost_per_clean'] = None
    return rec


def _cost_band(tokens, clean):
    """Bounded per-clean $ band for `tokens` totalTokens over `clean` clean cards.

    floor = cache-read rate (every token a cheap cache hit); ceil = fresh-input rate.
    Both EXCLUDE the output premium; true_upper prices every token at the output rate.
    """
    floor = tokens * PRICE['cache_read'] / 1e6 / clean
    ceil = tokens * PRICE['input'] / 1e6 / clean
    true_upper = tokens * PRICE['output'] / 1e6 / clean
    return {
        'floor_usd': round(floor, 6),
        'ceil_usd': round(ceil, 6),
        'true_upper_output_rate_usd': round(true_upper, 6),
        'basis': 'floor=cache_read rate, ceil=fresh-input rate; EXCLUDES output premium',
    }


def dedup_outcomes(rows):
    """Group-then-dedup outcome rows keyed on run_id (first occurrence wins).

    An exact re-append of an already-seen run_id is idempotent; a re-append whose
    (tokens, clean, agents_used) differ is a conflicting duplicate, surfaced separately.
    Mirrors run_observability.build_census's call_id dedup. Keyed on run_id, NOT window,
    because one window label ('no_pwg_w03') is reused for a fresh window and a requeue.
    """
    seen = {}            # run_id -> signature of first occurrence
    ordered = []         # deduped records, input order
    conflicting = set()
    for row in rows:
        if row.get('kind') != 'outcome':
            continue
        rec = _normalize_outcome(row)
        rid = rec['run_id']
        sig = (rec['tokens'], rec['clean'], rec['agents_used'])
        if rid is None:
            ordered.append(rec)          # nothing to dedup on; keep as-is
            continue
        if rid not in seen:
            seen[rid] = sig
            ordered.append(rec)
        elif seen[rid] != sig:
            conflicting.add(rid)         # same run_id, different figures -> real conflict
        # exact re-append -> silently dropped (idempotent)
    return ordered, sorted(conflicting)


def build_ledger(rows, source_log=None):
    """Reduce raw log rows to the durable ledger payload (pure; no I/O)."""
    recs, conflicting = dedup_outcomes(rows)

    total = len(recs)
    structured_au = sum(1 for r in recs
                        if r['provenance'] == 'structured' and r['agents_used'] is not None)
    enter_rows = [r for r in recs
                  if r['agents_used'] is not None and r['clean'] and r['clean'] > 0]
    wasted_rows = [r for r in recs if r['clean'] == 0]
    nulled_rows = [r for r in recs if r['provenance'] == 'nulled_note']

    coverage_line = (
        '%d/%d outcome rows carry structured agents_used; '
        '%d/%d enter agents-per-clean '
        '(%d has clean=0 -> wasted_calls; %d nulled -> incomplete)'
        % (structured_au, total, len(enter_rows), total,
           len(wasted_rows), len(nulled_rows)))

    # --- agents_per_clean aggregates (only rows with structured agents_used & clean>0) ---
    def _apc(rows_subset):
        a = sum(r['agents_used'] for r in rows_subset)
        c = sum(r['clean'] for r in rows_subset)
        return (a, c, round(a / c, 6) if c else None)

    a_incl, c_incl, apc_incl = _apc(enter_rows)
    first_pass_rows = [r for r in enter_rows if not r['is_requeue']]
    a_fp, c_fp, apc_fp = _apc(first_pass_rows)

    # --- pooled cost band: ALL priced-token outcome rows' tokens over total clean ---
    # (blunt total / total clean; a clean==0 row adds tokens but 0 clean, honestly)
    priced = [r for r in recs if r['tokens'] is not None and r['clean'] is not None]
    total_tokens = sum(r['tokens'] for r in priced)
    total_clean = sum(r['clean'] for r in priced)
    pooled_band = _cost_band(total_tokens, total_clean) if total_clean else None

    wasted_agents = sum(r['agents_used'] for r in wasted_rows if r['agents_used'] is not None)
    wasted_tokens = sum(r['tokens'] for r in wasted_rows if r['tokens'] is not None)

    return {
        'schema': SCHEMA,
        'generated_at': utc_now(),
        'source_log': source_log or os.path.basename(FROZEN_LOG),
        'price_basis_usd_per_million': dict(PRICE),
        'price_basis_note':
            'rates imported from parse_workflow_cost.PRICE (Sonnet 5 list); NOT re-hardcoded here',
        'coverage': {
            'outcome_rows': total,
            'structured_agents_used': structured_au,
            'enter_agents_per_clean': len(enter_rows),
            'clean0_wasted': len(wasted_rows),
            'nulled_incomplete': len(nulled_rows),
            'line': coverage_line,
        },
        'aggregate': {
            'agents_per_clean_incl_requeues': apc_incl,
            'agents_per_clean_incl_requeues_label': 'total agents to fully drain incl. requeues',
            'agents_per_clean_incl_requeues_basis':
                '%d agents / %d clean over %d rows w/ structured agents_used & clean>0 '
                '(fresh windows + their requeues pooled)' % (a_incl, c_incl, len(enter_rows)),
            'agents_per_clean_first_pass': apc_fp,
            'agents_per_clean_first_pass_basis':
                '%d agents / %d clean over %d fresh (non-_rq) rows; LEXICAL _rq heuristic — '
                'wf_a2b29683-835/no_pwg_w03 is semantically a w02 requeue but carries a '
                'fresh-looking label, so first-pass is an approximation'
                % (a_fp, c_fp, len(first_pass_rows)),
            'cost_per_clean_band': pooled_band,
            'cost_per_clean_band_basis':
                'pooled %d subagent_tokens over %d clean cards (blunt total / total clean, '
                'all priced outcome rows incl. mixed lanes and the clean=0 wasted run)'
                % (total_tokens, total_clean),
            'total_tokens': total_tokens,
            'total_clean': total_clean,
            'wasted_agents': wasted_agents,
            'wasted_tokens': wasted_tokens,
        },
        'runs': recs,
        'wasted_calls': [
            {'run_id': r['run_id'], 'window': r['window'],
             'agents_used': r['agents_used'], 'tokens': r['tokens']}
            for r in wasted_rows],
        'conflicting_run_ids': conflicting,
        'provenance': {
            'token_basis':
                'subagent_tokens is the blunt workflow-notification totalTokens; the billing '
                'cache-read/fresh-input split is NOT recoverable from the frozen log, so the '
                'cost band brackets the two extremes rather than pricing the real split',
            'output_premium':
                'subagent_tokens INCLUDES output tokens billed ~5x input (parse_workflow_cost '
                'PRICE output=$15 vs input=$3); the in-band ceil (fresh-input rate) is therefore '
                'NOT a true upper bound — true_upper_output_rate_usd prices every token at output',
            'metric_naming':
                "agents_per_clean numerator == agents_used (subagents spawned); this is NOT "
                "run_observability's run_summary.calls model-call counter",
            'nulled_rows':
                'no_pwg_w08 / w08_rq1 / w09 had structured outcome nulled into note; tokens+clean '
                'recovered from the note and priced, but agents_used is unrecoverable -> incomplete',
        },
    }


def write_ledger(output_path, rows=None, source_log=None):
    """Atomically write the durable ledger JSON (mirrors run_observability.write_census)."""
    if rows is None:
        rows = read_rows(FROZEN_LOG)
    payload = build_ledger(rows, source_log=source_log)
    tmp = output_path + '.tmp.%d' % os.getpid()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, output_path)
    return payload


def gate(ledger, ceil_agents_per_clean=None, ceil_cost_per_clean=None, strict=False):
    """Return exit code 1 on an AGGREGATE breach (never per-card), else 0.

    Compares the headline `agents_per_clean_incl_requeues` and the in-band fresh-input
    `cost_per_clean_band.ceil_usd` against the supplied ceilings. Individual runs are
    NEVER gated — a single expensive/wasted window cannot flip the gate; only the pooled
    aggregate can.

    ``strict`` (default False) selects the missing-data policy — the ONE behavioural
    switch, added for the bounded-staged-run cost fail-closed contract (H963):

      * strict=False (LEGACY, unchanged): a requested ceiling whose ledger value is
        ``None`` — an all-wasted / all-nulled log yields ``None`` aggregates — is
        SKIPPED, so the gate passes on unevaluable data. Every existing caller
        (``main`` default, the standalone CLI, economy_ledger_selftest) keeps this
        exact behaviour: DO NOT make ``None`` start failing for them.

      * strict=True (OPT-IN, fail-closed): a requested ceiling that cannot be
        evaluated (its ledger value is ``None``) is itself a breach — missing or
        invalid accounting data is NEVER treated as within-ceiling. The breach text
        carries the distinct ``unevaluable`` marker so callers/tests can tell a
        fail-closed stop from an over-ceiling stop. A ceiling left at ``None`` (not
        requested) is never a breach in either mode.
    """
    agg = ledger['aggregate']
    breaches = []
    apc = agg.get('agents_per_clean_incl_requeues')
    band = agg.get('cost_per_clean_band') or {}
    cost = band.get('ceil_usd')
    if ceil_agents_per_clean is not None:
        if apc is None:
            if strict:
                breaches.append('agents_per_clean unevaluable (no clean cards / incomplete '
                                'accounting) but a ceiling of %.4f was requested — fail-closed'
                                % ceil_agents_per_clean)
        elif apc > ceil_agents_per_clean:
            breaches.append('agents_per_clean_incl_requeues %.4f > ceiling %.4f'
                            % (apc, ceil_agents_per_clean))
    if ceil_cost_per_clean is not None:
        if cost is None:
            if strict:
                breaches.append('cost_per_clean unevaluable (no priced clean cards / incomplete '
                                'accounting) but a ceiling of $%.4f was requested — fail-closed'
                                % ceil_cost_per_clean)
        elif cost > ceil_cost_per_clean:
            breaches.append('cost_per_clean ceil $%.4f > ceiling $%.4f'
                            % (cost, ceil_cost_per_clean))
    for b in breaches:
        sys.stderr.write('ECONOMY GATE BREACH: %s\n' % b)
    return 1 if breaches else 0


def summary_lines(ledger):
    """Human-readable economy summary. Every aggregate can be None when NO outcome row entered the
    agents-per-clean set (an all-wasted / all-nulled log — exactly the honest 'nothing clean' case the
    ledger exists to report), so each numeric line is guarded rather than %-formatted blindly."""
    cov = ledger['coverage']
    agg = ledger['aggregate']
    band = agg['cost_per_clean_band']
    lines = [cov['line']]
    incl = agg['agents_per_clean_incl_requeues']
    if incl is None:
        lines.append('agents_per_clean: n/a — no clean cards in scope (all runs wasted/nulled)')
    else:
        lines.append('%s: %.3f (%s)' % (agg['agents_per_clean_incl_requeues_label'], incl,
                                        agg['agents_per_clean_incl_requeues_basis']))
    fp = agg['agents_per_clean_first_pass']
    if fp is not None:
        lines.append('first-pass agents_per_clean: %.3f' % fp)
    if band is not None:
        lines.append('cost per clean: $%.4f .. $%.4f (fresh-input ceil, excludes output premium; '
                     'true upper $%.4f at output rate)'
                     % (band['floor_usd'], band['ceil_usd'], band['true_upper_output_rate_usd']))
    else:
        lines.append('cost per clean: n/a — no clean cards in scope')
    lines.append('wasted: %d agents / %d tokens on clean=0 runs'
                 % (agg['wasted_agents'], agg['wasted_tokens']))
    return lines


def main():
    ap = argparse.ArgumentParser(description='PWG->RU economy ledger (offline, read-only)')
    ap.add_argument('--log', default=FROZEN_LOG, help='frozen outcome log (read-only)')
    ap.add_argument('--write', metavar='PATH', help='also write the durable ledger JSON here')
    ap.add_argument('--ceil-agents-per-clean', type=float, default=None)
    ap.add_argument('--ceil-cost-per-clean', type=float, default=None)
    ap.add_argument('--strict', action='store_true',
                    help='fail closed: a requested ceiling that cannot be evaluated '
                         '(unevaluable/None accounting) breaches the gate instead of '
                         'being skipped. Default off = legacy standalone behaviour.')
    args = ap.parse_args()

    rows = read_rows(args.log)
    ledger = build_ledger(rows, source_log=os.path.basename(args.log))
    if args.write:
        write_ledger(args.write, rows=rows, source_log=os.path.basename(args.log))
        print('wrote', args.write)

    for line in summary_lines(ledger):
        print(line)

    return gate(ledger, args.ceil_agents_per_clean, args.ceil_cost_per_clean, strict=args.strict)


if __name__ == '__main__':
    sys.exit(main())
