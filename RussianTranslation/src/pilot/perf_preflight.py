#!/usr/bin/env python
"""Read-only performance preflight for pwg_ru optimized harness lanes.

Builds the same in-memory lane plan as gen_opt_harness2.py, then reports the
agent-cost reducers before an operator spends Workflow/Max tokens. It writes
nothing and never touches the RU store.
"""
import argparse
import contextlib
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gen_opt_harness2 as gh
import translation_memory  # noqa: F401  # pre-import before stdout capture; module reconfigures stdout.
from window_common import INP, input_paths, read_text


# --- H189 cost gate ----------------------------------------------------------------
# Empirical per-agent figures from the pril10_w1 blow-up (parse_workflow_cost.py over the
# three sub-window transcripts: 230 agents, 42,316,604 tokens, $79.83 at Sonnet 4.x rates):
#   184,000 tokens/agent (mean), $0.347/agent.
# agent_expected_after_tm is an optimistic FLOOR (one call per batch/fragment-group, no
# retries) — the real run spent 230 vs a 174 estimate (1.32x) — so a realism multiplier is
# applied before pricing. The $ figures inherit parse_workflow_cost.py's Sonnet 4.x rates
# (order-of-magnitude for Sonnet 5); the TOKEN estimate and the per-card RATIO are the
# model-independent, load-bearing parts of the gate.
PER_AGENT_TOKENS = 184000
PER_AGENT_USD = 0.347
REALISM_FACTOR = 1.35
COST_CEIL_PER_CARD_USD = 2.00   # a window whose est cost per TRANSLATED card exceeds this is
                                #  flagged: a healthy batched card is ~$0.07, but pril10_w1 was
                                #  ~$10-27/card — a window of kAla-class monsters must be gated
                                #  out of the bulk pipeline, not run silently.
COST_CEIL_WINDOW_USD = 25.00    # absolute per-window backstop regardless of card count


def cost_estimate(report, per_card_ceiling=COST_CEIL_PER_CARD_USD,
                  window_ceiling=COST_CEIL_WINDOW_USD, realism=REALISM_FACTOR):
    """H189: estimate tokens + $ + a per-card cost for a window and decide whether it
    exceeds a ceiling. Read-only accounting; the verdict lets an operator (or a wrapper via
    --refuse-over-cost) refuse to launch a window that would silently run into a
    $80 / 3-card outcome again."""
    agents = report.get('agent_expected_after_tm', 0) or 0
    est_agents = agents * realism
    est_tokens = int(round(est_agents * PER_AGENT_TOKENS))
    est_cost = round(est_agents * PER_AGENT_USD, 2)
    # cards that actually cost an agent() call — exclude TM-resolved and degenerate stubs.
    cards_to_translate = max(0, len(report.get('selected_keys', []))
                             - int(report.get('tm_cards', 0) or 0)
                             - len(report.get('degenerate_passthrough_keys', [])))
    per_card = round(est_cost / cards_to_translate, 2) if cards_to_translate else 0.0
    over_card = cards_to_translate > 0 and per_card > per_card_ceiling
    over_window = est_cost > window_ceiling
    return {
        'est_agents_with_realism': round(est_agents, 1),
        'realism_factor': realism,
        'est_tokens': est_tokens,
        'est_cost_usd': est_cost,
        'cards_to_translate': cards_to_translate,
        'est_cost_per_card_usd': per_card,
        'per_card_ceiling_usd': per_card_ceiling,
        'window_ceiling_usd': window_ceiling,
        'over_ceiling': bool(over_card or over_window),
        'verdict': 'OVER-CEILING' if (over_card or over_window) else 'ok',
        'rate_basis': 'Sonnet 4.x rates (order-of-magnitude); token estimate is model-independent',
    }


def split_csv(text):
    return [x.strip() for x in str(text).split(',') if x.strip()]


def const_json(js, name):
    m = re.search(r'^const %s = (.*)$' % re.escape(name), js, re.M)
    return json.loads(m.group(1)) if m else None


def default_tm_path(lang):
    return os.path.join(os.path.dirname(INP), 'translation_memory.%s.json' % lang)


def default_frag_path(lang, tm_path=None):
    base = os.path.dirname(tm_path or default_tm_path(lang))
    return os.path.join(base, 'translation_memory.frag.%s.jsonl' % lang)


def selected(root, keylist, nominal):
    if nominal:
        if not keylist:
            raise SystemExit('FAIL: --nominal requires --keys=k1,k2,...')
        return None, keylist
    rootmap, keys = gh.selected_keys(root, set(keylist) if keylist else None)
    if keylist:
        wanted = set(keys)
        keys = [k for k in keylist if k in wanted]
    return rootmap, keys


def near_degenerate_reason(key, raw, portrait, field):
    if gh.degenerate_passthrough_card(key, raw, portrait, field):
        return None
    if not (re.search(r'\{#[^}]+#\}', raw) or '<ls' in raw or '<ab>' in raw):
        return None
    if len(raw) > 1500 or '<div' in raw or re.search(r'\b\d+\)', raw):
        return None
    if '{%' in raw:
        return None
    body = re.sub(r'^=== LAYER:.*?===\s*', '', raw, flags=re.S).strip()
    if has_correction_prose(body):
        return 'editorial correction prose; keep in LLM lane'
    probe = re.sub(r'\{#[^}]*#\}', ' ', body)
    probe = re.sub(r'\{%[^}]*%\}', ' ', probe)
    probe = re.sub(r'<[^>]+>', ' ', probe)
    words = [w.lower().strip('.:,;()') for w in re.findall(r'[A-Za-zÄÖÜäöüß]+\.?', probe)]
    words = [w for w in words if w]
    if len(words) <= 12:
        return 'short reference-like stub, but words are outside the pass-through whitelist'
    return None


def has_correction_prose(text):
    return bool(re.search(r'\b(lies|lesen|streichen)\b', text, re.I))


def near_degenerate_candidates(keys, field):
    rows = []
    for key in keys:
        rp, pp = input_paths(key)
        if not (os.path.exists(rp) and os.path.exists(pp)):
            continue
        raw, portrait = read_text(rp), read_text(pp)
        reason = near_degenerate_reason(key, raw, portrait, field)
        if reason:
            rows.append({'key': key, 'reason': reason})
    return rows


def has_frag_provenance(glob_pattern):
    for fp in sorted(glob.glob(os.path.join(REPO, glob_pattern))):
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                for chunk in iter(lambda: f.read(1024 * 1024), ''):
                    if not chunk:
                        break
                    if '"frag_prov"' in chunk or "'frag_prov'" in chunk:
                        return True
        except OSError:
            continue
    return False


def recommendation(report):
    agents = report.get('agent_expected_after_tm', 0)
    if agents == 0:
        return 'skip-cached'
    if agents <= 15:
        return 'run-now-low'
    if agents <= 20:
        return 'run-next'
    return 'defer-calibrate'


def build_report(args, root):
    keylist = split_csv(args.keys) if args.keys else None
    rootmap, keys = selected(root, keylist, args.nominal)
    tm_path = (args.tm_path or default_tm_path(args.lang)) if args.tm_auto else None
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        js, _batches = gh.build(root, keys, rootmap, args.budget,
                                nominal=args.nominal, grammar_on=not args.no_grammar,
                                lang=args.lang, tm_path=tm_path, tm_auto=args.tm_auto)
    meta = const_json(js, 'META')
    frag_tm = const_json(js, 'FRAG_TM') or {}
    fragment_hit_groups = {
        key: sum(1 for group in groups if any(slot for slot in group))
        for key, groups in frag_tm.items()
    }
    field = 'english' if args.lang == 'en' else 'russian'
    tm_sidecar = tm_path or default_tm_path(args.lang)
    frag_sidecar = default_frag_path(args.lang, tm_sidecar)
    frag_cache = translation_memory.load_frag_tm(args.lang, frag_sidecar)
    warnings = []
    if meta.get('presplit_keys') and not frag_cache:
        warning = (
            'presplit keys need fragment fallback, but %s is empty; run '
            '`python src/pilot/translation_memory.py build-frags --lang %s` after a heal '
            'Workflow emits frag_prov'
            % (os.path.basename(frag_sidecar), args.lang)
        )
        if not has_frag_provenance(args.wf_glob):
            warning += '; no fragment provenance available yet'
        warnings.append(warning)
    report = {
        'schema': 'pwg.performance_preflight.v1',
        'root': root,
        'lang': args.lang,
        'nominal': bool(args.nominal),
        'selected_keys': keys,
        'tm_sidecar': tm_sidecar,
        'tm_available': os.path.exists(tm_sidecar),
        'tm_auto': bool(args.tm_auto),
        'tm_hits': meta.get('tm_hits', []),
        'tm_cards': meta.get('tm_cards', 0),
        'frag_tm_sidecar': frag_sidecar,
        'frag_tm_available': os.path.exists(frag_sidecar),
        'frag_tm_entries': len(frag_cache),
        'frag_tm_cards': meta.get('frag_tm_cards', []),
        'frag_tm_fragments': meta.get('frag_tm_fragments', 0),
        'fragment_hit_groups': fragment_hit_groups,
        'degenerate_passthrough_keys': meta.get('degenerate_passthrough_keys', []),
        'near_degenerate_candidates': near_degenerate_candidates(keys, field),
        'presplit_keys': meta.get('presplit_keys', []),
        'batch_count': meta.get('batch_count', 0),
        'agent_expected_after_tm': meta.get('agent_expected_after_tm', 0),
        'output_budget': meta.get('output_budget'),
        'selfheal_group_budget': meta.get('selfheal_group_budget'),
        'recommended_action': None,
        'warnings': warnings,
        'generator_log': [line for line in buf.getvalue().splitlines() if line.strip()],
    }
    report['recommended_action'] = recommendation(report)
    report['cost_gate'] = cost_estimate(
        report,
        per_card_ceiling=getattr(args, 'cost_ceiling_per_card', COST_CEIL_PER_CARD_USD),
        window_ceiling=getattr(args, 'cost_ceiling_window', COST_CEIL_WINDOW_USD))
    if report['cost_gate']['over_ceiling']:
        report['warnings'].append(
            'COST-GATE: est ~%d tokens / ~$%.2f (~$%.2f per translated card, ceiling $%.2f) — '
            'this window is dominated by expensive cards; split off the monster cards to a '
            'human-budgeted lane before launching (H189).'
            % (report['cost_gate']['est_tokens'], report['cost_gate']['est_cost_usd'],
               report['cost_gate']['est_cost_per_card_usd'],
               report['cost_gate']['per_card_ceiling_usd']))
    return report


def print_human(report):
    print('pwg_ru performance preflight: %s (%s)' % (report['root'], report['lang']))
    print('  selected_keys: %d' % len(report['selected_keys']))
    print('  card TM: %s | hits %d'
          % ('present' if report['tm_available'] else 'missing', report['tm_cards']))
    print('  fragment TM: %s | cards %d | fragments %d'
          % ('present' if report['frag_tm_available'] else 'missing',
             len(report['frag_tm_cards']), report['frag_tm_fragments']))
    print('  degenerate pass-through: %d' % len(report['degenerate_passthrough_keys']))
    if report['near_degenerate_candidates']:
        print('  near-degenerate candidates: %d' % len(report['near_degenerate_candidates']))
        for row in report['near_degenerate_candidates'][:12]:
            print('    - %s: %s' % (row['key'], row['reason']))
    print('  presplit: %d' % len(report['presplit_keys']))
    print('  batches: %d' % report['batch_count'])
    print('  agent_expected_after_tm: %d' % report['agent_expected_after_tm'])
    print('  recommendation: %s' % report['recommended_action'])
    cg = report.get('cost_gate') or {}
    print('  est cost: ~%d tokens / ~$%.2f  (~$%.2f per translated card; ceiling $%.2f; %s)'
          % (cg.get('est_tokens', 0), cg.get('est_cost_usd', 0.0),
             cg.get('est_cost_per_card_usd', 0.0), cg.get('per_card_ceiling_usd', 0.0),
             cg.get('verdict', 'ok')))
    for warning in report.get('warnings') or []:
        print('  WARNING: %s' % warning)


def recommended_order(reports):
    runnable = [r for r in reports if r['agent_expected_after_tm'] > 0]
    runnable.sort(key=lambda r: (r['agent_expected_after_tm'], len(r['selected_keys']), r['root']))
    skipped = [r['root'] for r in reports if r['agent_expected_after_tm'] == 0]
    deferred = [r['root'] for r in runnable if r['recommended_action'] == 'defer-calibrate']
    ordered = [r['root'] for r in runnable if r['recommended_action'] != 'defer-calibrate']
    return {'run_first': ordered, 'defer': deferred, 'skip_cached': skipped}


def print_matrix(reports):
    print('pwg_ru performance preflight matrix (%s)' % reports[0]['lang'])
    header = ('root', 'keys', 'tm', 'frag', 'deg', 'near', 'pre', 'batches', 'agents', '$est', '$/card', 'action')
    rows = []
    for r in reports:
        cg = r.get('cost_gate') or {}
        rows.append((
            r['root'], len(r['selected_keys']), r['tm_cards'], r['frag_tm_fragments'],
            len(r['degenerate_passthrough_keys']), len(r['near_degenerate_candidates']),
            len(r['presplit_keys']), r['batch_count'], r['agent_expected_after_tm'],
            '%.2f' % cg.get('est_cost_usd', 0.0), '%.2f' % cg.get('est_cost_per_card_usd', 0.0),
            r['recommended_action'] + ('!COST' if cg.get('over_ceiling') else ''),
        ))
    widths = [max(len(str(row[i])) for row in [header] + rows) for i in range(len(header))]
    fmt = '  '.join('%%-%ds' % w for w in widths)
    print(fmt % header)
    print(fmt % tuple('-' * w for w in widths))
    for row in rows:
        print(fmt % row)
    order = recommended_order(reports)
    if order['run_first']:
        print('recommended run order: %s' % ', '.join(order['run_first']))
    if order['skip_cached']:
        print('skip cached: %s' % ', '.join(order['skip_cached']))
    if order['defer']:
        print('defer until cache refresh/calibration: %s' % ', '.join(order['defer']))
    warnings = [(r['root'], w) for r in reports for w in (r.get('warnings') or [])]
    for root, warning in warnings:
        print('WARNING [%s]: %s' % (root, warning))


def main(argv=None):
    ap = argparse.ArgumentParser(description='Read-only optimized-harness performance preflight.')
    ap.add_argument('roots', nargs='+')
    ap.add_argument('--keys', default=None)
    ap.add_argument('--lang', default='ru', choices=('ru', 'en'))
    ap.add_argument('--nominal', action='store_true')
    ap.add_argument('--no-grammar', action='store_true')
    ap.add_argument('--budget', default=12000, type=int)
    ap.add_argument('--tm', dest='tm_path', default=None,
                    help='Optional TM sidecar path; defaults to src/pilot/translation_memory.<lang>.json.')
    ap.add_argument('--no-tm', dest='tm_auto', action='store_false',
                    help='Disable auto sidecar lookup for what-if accounting.')
    ap.add_argument('--wf-glob', default='wf_output*.json',
                    help='Workflow-output glob, relative to RussianTranslation/, used only for frag_prov warnings.')
    ap.add_argument('--cost-ceiling-per-card', type=float, default=COST_CEIL_PER_CARD_USD,
                    help='H189 cost gate: flag a window whose est $ per translated card exceeds this (default %(default)s).')
    ap.add_argument('--cost-ceiling-window', type=float, default=COST_CEIL_WINDOW_USD,
                    help='H189 cost gate: flag a window whose total est $ exceeds this (default %(default)s).')
    ap.add_argument('--refuse-over-cost', action='store_true',
                    help='H189 cost gate: exit nonzero if any window exceeds a cost ceiling (for automated callers).')
    ap.add_argument('--json', action='store_true')
    ap.set_defaults(tm_auto=True)
    args = ap.parse_args(argv)
    if len(args.roots) > 1 and args.keys:
        raise SystemExit('FAIL: --keys is root-specific; use one root per --keys preflight')
    if len(args.roots) > 1 and args.nominal:
        raise SystemExit('FAIL: --nominal requires one root/key namespace per preflight')
    reports = [build_report(args, root) for root in args.roots]
    over = [r for r in reports if r.get('cost_gate', {}).get('over_ceiling')]
    if args.json:
        if len(reports) == 1:
            payload = reports[0]
        else:
            payload = {
                'schema': 'pwg.performance_preflight.matrix.v1',
                'lang': args.lang,
                'roots': args.roots,
                'reports': reports,
                'recommended_order': recommended_order(reports),
            }
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        print()
    elif len(reports) == 1:
        print_human(reports[0])
    else:
        print_matrix(reports)
    if args.refuse_over_cost and over:
        sys.exit('FAIL: %d window(s) exceed the H189 cost ceiling ($%.2f/card, $%.2f/window): %s'
                 % (len(over), args.cost_ceiling_per_card, args.cost_ceiling_window,
                    ', '.join(r['root'] for r in over)))


if __name__ == '__main__':
    main()
