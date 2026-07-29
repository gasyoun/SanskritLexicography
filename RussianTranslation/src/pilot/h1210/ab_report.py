#!/usr/bin/env python
r"""H1210 — build the comparative A/B table from both arms' artifacts.

Inputs per arm: the slice_result(s) (rig self-report + per-card chain telemetry), the
`h1209/canonical_audit.py` report (the AUTHORITATIVE promote-DRY verdict — the rig's own
"would_promote" is a self-report and the H1209 v1 run proved it can lie), and a telemetry
JSON (arm B writes its own; arm A's is assembled from the Workflow run usage blocks).

Emits `H1210_AB_RESULTS.<date>.json` + a Markdown table block for RESULTS_LOG.md.

Metrics (the H1210 deliverable list):
  audit-clean %          canonical promote-DRY PASS / cards attempted
  defect classes         distribution of hard_fail + soft_flags across rejected cards
  $/clean card           arm B: measured USD from token usage x published price table
                         arm A: subscription lane — tokens reported, USD marked n/a with why
  calls/clean            generation + controller calls / clean card
  latency                per-card wall clock (arm B: measured per call; arm A: run duration)
  retry / escalation / review-sheet rate
  controller token share arm A: controller agents / all agents (token split where available)

Usage:
  python src/pilot/h1210/ab_report.py --arm-a-result F [F ...] --arm-a-audit F
      --arm-a-telemetry F --arm-b-result F --arm-b-audit F --arm-b-telemetry F
      --worklist F --out-prefix src/pilot/h1210/H1210_AB_RESULTS.28.07.26
"""
import argparse
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

CLEAN_STATUSES = {'clean-no-review', 'clean-controller-approved'}

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))
if SRC not in sys.path:
    sys.path.insert(0, SRC)
from safe_filename import safe_name          # noqa: E402


def load(p):
    return json.load(open(p, encoding='utf-8'))


def card_id(row):
    """The id a card carries THROUGH the pipeline — not `key1`.

    The worklist records the SLP1 headword (`SAluqa`); the harness, both arms' results and
    the canonical audit all key on the Windows-safe stem (`_s_aluqa`), or on the explicit
    supplement sub-card id (`arvant~~h0_zz_pw`) for the no_pwg lane. Joining the two on
    `key1` silently matched almost nothing and dumped 73 of 100 cards into an unknown
    stratum — so every worklist join goes through this function.
    """
    return row['sub_key'] if row.get('layer') == 'no_pwg' and row.get('sub_key') \
        else safe_name(row['key1'])


def worklist_index(worklist):
    return ({card_id(d): d['stratum'] for d in worklist['detail']},
            [card_id(d) for d in worklist['detail']])


def audit_index(audit, worklist):
    """Key the canonical audit by pipeline card id — NOT by its own `key1`.

    `canonical_audit.py` reports whatever key1 its source record carried, which is a THIRD
    form again: the SLP1 headword for the pwg layer (`SAluqa`, `durgA`), but the safe stem
    or the sub-card id for cards that reached it already safe-named (`_svetakar_ra`,
    `arvant~~h0_zz_pw`). The arms' results key exclusively on the pipeline id. Joining the
    two dicts on the raw `key1` therefore matched 42 of 87 arm-A rows and silently scored
    the other 45 as NOT clean — reporting arm A at 46% when the audit it was reading says
    95.4%. Every audit row is resolved here instead, and an unresolvable one is a hard
    error rather than a silently-dropped denominator.
    """
    alias = {}
    for d in worklist['detail']:
        cid = card_id(d)
        alias[cid] = cid
        alias[d['key1']] = cid
        alias[safe_name(d['key1'])] = cid
    out, unresolved = {}, []
    for r in audit['reports']:
        cid = alias.get(r['key1']) or alias.get(safe_name(r['key1']))
        if not cid:
            unresolved.append(r['key1'])
            continue
        out[cid] = r
    if unresolved:
        raise SystemExit('audit rows not resolvable to a worklist card id: %s'
                         % ', '.join(sorted(unresolved)))
    return out


def merge_results(paths):
    merged = {'slice': [], 'results': [], 'cards_out': [], 'control_rounds': []}
    for p in paths:
        d = load(p)
        merged['slice'] += list(d.get('slice') or [])
        merged['results'] += list(d.get('results') or [])
        merged['cards_out'] += list(d.get('cards_out') or [])
        merged['control_rounds'] += list(d.get('control_rounds') or [])
    return merged


def arm_metrics(name, res, audit, telem, worklist):
    rows = {r['key1']: r for r in res['results']}
    reports = audit_index(audit, worklist)
    strata, all_ids = worklist_index(worklist)
    complex_flag = {r['key1']: bool(r.get('complexity_flag')) for r in res['results']}

    attempted = list(rows)
    clean = [k for k in attempted if reports.get(k, {}).get('promote_dry')]
    rig_clean = [k for k in attempted if rows[k].get('would_promote')]

    defects = collections.Counter()
    for k in attempted:
        rep = reports.get(k)
        if not rep or rep.get('promote_dry'):
            continue
        for hf in rep.get('hard_fail') or []:
            defects[hf.split(':')[0]] += 1
        for sf in rep.get('soft_flags') or []:
            defects['soft:' + sf] += 1
        if not (rep.get('hard_fail') or rep.get('soft_flags')):
            defects['unclassified'] += 1

    soft = collections.Counter()
    for k in attempted:
        for sf in (reports.get(k, {}).get('soft_flags') or []):
            soft[sf] += 1

    status = collections.Counter(rows[k]['final_status'] for k in attempted)
    retries = sum(max(0, (rows[k].get('attempts') or 1) - 1) for k in attempted)
    ctrl_calls = sum(rows[k].get('controller_calls') or 0 for k in attempted)
    gen_calls = telem.get('generation_calls')
    if gen_calls is None:
        gen_calls = sum(rows[k].get('attempts') or 0 for k in attempted)

    cost = telem.get('cost') or {}
    usd = cost.get('usd')
    n_clean = len(clean)
    per_clean = (round(usd / n_clean, 4) if (usd is not None and n_clean) else None)

    # false-flag rate of the complexity trigger: complexity-flagged cards that the
    # canonical audit passed with no soft flag at all (the trigger fired for nothing).
    flagged = [k for k in attempted if complex_flag.get(k)]
    false_flags = [k for k in flagged
                   if reports.get(k, {}).get('promote_dry')
                   and not (reports.get(k, {}).get('soft_flags') or [])
                   and not (rows[k].get('det_issues') or [])]

    by_stratum = collections.defaultdict(lambda: [0, 0])
    for k in attempted:
        st = strata.get(k, '?').split('_')[0]
        by_stratum[st][1] += 1
        if k in clean:
            by_stratum[st][0] += 1

    return {
        'arm': name,
        'model': telem.get('model'),
        'cards_attempted': len(attempted),
        'cards_missing': [k for k in all_ids if k not in rows],
        'canonical_clean': n_clean,
        'canonical_clean_pct': round(100.0 * n_clean / len(attempted), 1) if attempted else None,
        'rig_self_report_clean': len(rig_clean),
        'self_report_overstatement': len(rig_clean) - n_clean,
        'defect_classes': dict(defects.most_common()),
        'soft_flags': dict(soft.most_common()),
        'final_status': dict(status.most_common()),
        'retries': retries,
        'retry_rate_per_card': round(retries / len(attempted), 2) if attempted else None,
        'escalations': status.get('escalate-review-sheet', 0),
        'review_sheet_rate_pct': (round(100.0 * status.get('escalate-review-sheet', 0)
                                        / len(attempted), 1) if attempted else None),
        'generation_calls': gen_calls,
        'controller_calls': ctrl_calls,
        'calls_per_clean': round((gen_calls + ctrl_calls) / n_clean, 2) if n_clean else None,
        'controller_call_share_pct': (round(100.0 * ctrl_calls / (gen_calls + ctrl_calls), 1)
                                      if (gen_calls + ctrl_calls) else None),
        'tokens': telem.get('tokens') or {k: v for k, v in cost.items() if k.endswith('tokens')},
        'usd_total': usd,
        'usd_per_clean': per_clean,
        'usd_note': telem.get('usd_note'),
        'wall_clock_s': telem.get('wall_clock_s'),
        'latency_s_per_card_median': telem.get('latency_s_per_card_median'),
        'complexity_flagged': len(flagged),
        'complexity_false_flags': len(false_flags),
        'complexity_false_flag_pct': (round(100.0 * len(false_flags) / len(flagged), 1)
                                      if flagged else None),
        'clean_by_stratum': {k: '%d/%d' % (v[0], v[1]) for k, v in sorted(by_stratum.items())},
    }


def md_table(a, b):
    def fmt(v):
        return '—' if v is None else (('%s' % v) if not isinstance(v, float) else '%.2f' % v)
    rows = [
        ('generator model', a['model'], b['model']),
        ('cards attempted', a['cards_attempted'], b['cards_attempted']),
        ('**audit-clean % (canonical promote-DRY)**',
         '**%s%% (%d/%d)** ' % (fmt(a['canonical_clean_pct']), a['canonical_clean'], a['cards_attempted']),
         '**%s%% (%d/%d)**' % (fmt(b['canonical_clean_pct']), b['canonical_clean'], b['cards_attempted'])),
        ('rig self-report clean (vs audit)',
         '%d (%+d)' % (a['rig_self_report_clean'], a['self_report_overstatement']),
         '%d (%+d)' % (b['rig_self_report_clean'], b['self_report_overstatement'])),
        ('generation calls', a['generation_calls'], b['generation_calls']),
        ('controller calls', a['controller_calls'], b['controller_calls']),
        ('calls / clean card', fmt(a['calls_per_clean']), fmt(b['calls_per_clean'])),
        ('controller share of calls', fmt(a['controller_call_share_pct']) + '%',
         fmt(b['controller_call_share_pct']) + '%'),
        ('retries (rate/card)', '%d (%s)' % (a['retries'], fmt(a['retry_rate_per_card'])),
         '%d (%s)' % (b['retries'], fmt(b['retry_rate_per_card']))),
        ('escalated to review-sheet',
         '%d (%s%%)' % (a['escalations'], fmt(a['review_sheet_rate_pct'])),
         '%d (%s%%)' % (b['escalations'], fmt(b['review_sheet_rate_pct']))),
        ('complexity-trigger false-flag rate',
         '%s%% (%d/%d)' % (fmt(a['complexity_false_flag_pct']), a['complexity_false_flags'],
                           a['complexity_flagged']),
         '%s%% (%d/%d)' % (fmt(b['complexity_false_flag_pct']), b['complexity_false_flags'],
                           b['complexity_flagged'])),
        ('USD total', fmt(a['usd_total']), fmt(b['usd_total'])),
        ('**USD / clean card**', '**%s**' % fmt(a['usd_per_clean']),
         '**%s**' % fmt(b['usd_per_clean'])),
        ('wall clock (s)', fmt(a['wall_clock_s']), fmt(b['wall_clock_s'])),
    ]
    out = ['| metric | arm A — Claude-native | arm B — DeepSeek + same controller |',
           '|---|---|---|']
    for r in rows:
        out.append('| %s | %s | %s |' % (r[0], r[1], r[2]))
    return '\n'.join(out)


def md_defects(a, b):
    keys = sorted(set(a['defect_classes']) | set(b['defect_classes']))
    out = ['| defect class (canonical audit) | arm A | arm B |', '|---|---:|---:|']
    for k in keys:
        out.append('| %s | %d | %d |' % (k, a['defect_classes'].get(k, 0),
                                         b['defect_classes'].get(k, 0)))
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm-a-result', nargs='+', required=True)
    ap.add_argument('--arm-a-audit', required=True)
    ap.add_argument('--arm-a-telemetry', required=True)
    ap.add_argument('--arm-b-result', nargs='+', required=True)
    ap.add_argument('--arm-b-audit', required=True)
    ap.add_argument('--arm-b-telemetry', required=True)
    ap.add_argument('--worklist', required=True)
    ap.add_argument('--out-prefix', required=True)
    a = ap.parse_args()

    worklist = load(a.worklist)
    A = arm_metrics('A_claude_native', merge_results(a.arm_a_result), load(a.arm_a_audit),
                    load(a.arm_a_telemetry), worklist)
    B = arm_metrics('B_deepseek', merge_results(a.arm_b_result), load(a.arm_b_audit),
                    load(a.arm_b_telemetry), worklist)

    out = {'schema': 'pwg.h1210_ab_results.v1', 'handoff': 'H1210',
           'worklist': os.path.basename(a.worklist),
           'n_cards_selected': worklist['n_selected'], 'arm_a': A, 'arm_b': B}
    with open(a.out_prefix + '.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    md = md_table(A, B) + '\n\n' + md_defects(A, B) + '\n'
    with open(a.out_prefix + '.md', 'w', encoding='utf-8', newline='\n') as f:
        f.write(md)
    print(md)
    print('\nwrote %s.json / %s.md' % (a.out_prefix, a.out_prefix))
    for arm in (A, B):
        if arm['cards_missing']:
            print('NOT ATTEMPTED in %s (%d): %s'
                  % (arm['arm'], len(arm['cards_missing']), ','.join(arm['cards_missing'])))


if __name__ == '__main__':
    main()
