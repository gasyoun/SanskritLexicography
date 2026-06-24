#!/usr/bin/env python
"""scale_preflight.py — non-mutating COVERAGE + COST guardrails before a scale-up run.

Complements preflight_remaining_gates.py (which gates the PRINT RELEASE: review/gold/
roadmap/interop). This gates the *translation run*: given the next N headwords of the
frequency queue, it answers three questions BEFORE any model call is spent —

  1. COVERAGE   — does every queued key resolve to a real card, and what is the
                  heavy/light split + dict/corpus reuse for the batch? (from scale_route)
  2. SPLIT-READY — any card too big for a single pass (bytes > --ceiling) that does NOT
                  yet have a pilot/input/<safe>.rootmap.json is a BLOCKER: it would
                  overwhelm the translator. The root segmenter must run on it first.
  3. COST       — projected input/output tokens, and an Opus-API USD REFERENCE vs --budget.
                  We run on Claude Max (≈$0 marginal); USD is comparison-only. See PILOT_COST.md §7.

Reuses freq_route's manifest (scale_manifest.freq.json) + scale_route's per-section
manifests + safe_filename.safe_name (no reinvention). Read-only; never touches the
active pipeline files.

  python scale_preflight.py --top 500 --budget 400                       # main path: Opus judges, cache on
  python scale_preflight.py --top 500 --judge-model sonnet               # cheaper ALTERNATIVE (validate first)
  python scale_preflight.py --top 500 --translate-model opus --no-cache  # the all-Opus "before"

Cost knobs (defaults = the config we run — Sonnet translate, Opus judges, Opus repass, cache
on): --translate-model/--judge-model/--repass-model {opus,sonnet,haiku}, --judges N,
--repass-rate F, --prompt-tok N, --no-cache. The Sonnet-judge alternative must be validated
against Opus on real cards first — see judge_ab.py.
"""
import argparse, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from safe_filename import safe_name

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pilot', 'output')
INP = os.path.join(HERE, 'pilot', 'input')
FREQ = os.path.join(OUT, 'scale_manifest.freq.json')
PWG = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'pwg', 'pwg.txt'))
_DIVP = re.compile(r'^<div n="p">')


def div_p_counts(keys):
    """One streaming pass over pwg.txt -> {key1: max <div n=p> count over its records}.

    Distinguishes the two oversize classes: verbal roots (>0 prefix divs, splittable by
    `--root-split`) from polysemous non-root cards (0 divs, need head/sense chunking)."""
    want = set(keys)
    out = {}
    cur = None
    n = 0
    with open(PWG, encoding='utf-8') as f:
        for ln in f:
            if ln.startswith('<L>'):
                if cur in want:
                    out[cur] = max(out.get(cur, 0), n)
                m = re.search(r'<k1>([^<]*)', ln)
                cur = m.group(1) if m else None
                n = 0
            elif cur in want and _DIVP.match(ln):
                n += 1
        if cur in want:
            out[cur] = max(out.get(cur, 0), n)
    return out

# --- Cost model (transparent + CLI-overridable; verify $/Mtok against current pricing) ---
OUTPUT_RATIO = 1.2                  # a full translation ≈ 1.2× the source content tokens
# $ per Mtok: (input, cached-input-read, output). Cached read ≈ 0.1× input (Anthropic).
MODELS = {
    'opus':   (15.0, 1.5,  75.0),
    'sonnet': (3.0,  0.3,  15.0),
    'haiku':  (0.80, 0.08,  4.0),
}
# Baseline for the "before" comparison: 4 full Opus passes, no prompt caching.
BASE_PASSES, BASE_IN, BASE_OUT = 4, 15.0, 75.0


def build_pipeline(a):
    """The per-pass pipeline as configured. Each pass runs `factor` times per sub-card on the
    given `paths`, on `model`, emitting `out_factor`× a full translation's output tokens
    (judges emit only a small verdict). Defaults = the config we run: Sonnet translate +
    **Opus judges** + Opus repass, prompt-cache on. A Sonnet judge (--judge-model sonnet) is a
    documented cheaper ALTERNATIVE, validated against Opus by the judge A/B before trusting it."""
    return [
        {'name': 'translate', 'model': a.translate_model, 'factor': 1.0,
         'out_factor': 1.0,  'paths': {'heavy', 'light'}},
        {'name': 'judge',     'model': a.judge_model,     'factor': float(a.judges),
         'out_factor': 0.15, 'paths': {'heavy'}},
        {'name': 'repass',    'model': a.repass_model,    'factor': a.repass_rate,
         'out_factor': 1.0,  'paths': {'heavy'}},
    ]

_section_cache = {}


def load_section(letter):
    if letter in _section_cache:
        return _section_cache[letter]
    path = os.path.join(OUT, 'scale_manifest.%s.json' % letter)
    d = {}
    if os.path.exists(path):
        for e in json.load(open(path, encoding='utf-8')):
            d[e['key1']] = e
    _section_cache[letter] = d
    return d


def route(key1):
    """(path, covered) from the per-section scale_route manifest, defaulting to heavy."""
    e = load_section(key1[:1].lower()).get(key1)
    if e is None:
        return 'heavy', False        # unknown -> assume worst case (heavy, uncovered)
    return e.get('path', 'heavy'), bool(e.get('covered'))


def subcard_count(key1):
    """If this root was already split, how many sub-cards? (drives per-sub-card passes.)"""
    rm = os.path.join(INP, safe_name(key1) + '.rootmap.json')
    if os.path.exists(rm):
        return len(json.load(open(rm, encoding='utf-8')).get('sub_cards', []))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--top', type=int, default=500, help='how many queue cards to pre-flight')
    ap.add_argument('--ceiling', type=int, default=8000, help='bytes above which a card needs --root-split')
    ap.add_argument('--budget', type=float, default=None, help='USD ceiling; over-budget => non-zero exit')
    ap.add_argument('--chars-per-tok', type=float, default=3.0)
    ap.add_argument('--manifest', default=FREQ)
    ap.add_argument('--strict', action='store_true', help='also fail if any split-ready blocker exists')
    # Per-pass model + prompt-caching knobs (defaults = the cheap-judge / cached config we run).
    ap.add_argument('--translate-model', default='sonnet', choices=sorted(MODELS))
    ap.add_argument('--judge-model', default='opus', choices=sorted(MODELS),
                    help='main path = opus; sonnet is the cheaper alternative (validate via judge_ab.py first)')
    ap.add_argument('--repass-model', default='opus', choices=sorted(MODELS))
    ap.add_argument('--judges', type=int, default=2, help='QA judges per heavy card')
    ap.add_argument('--repass-rate', type=float, default=0.2, help='expected re-translate fraction (rejects)')
    ap.add_argument('--prompt-tok', type=int, default=3000, help='locked system prompt tokens, per call')
    ap.add_argument('--no-cache', dest='cache', action='store_false', help='disable prompt caching')
    a = ap.parse_args()
    pipeline = build_pipeline(a)

    if not os.path.exists(a.manifest):
        print('NO freq manifest at %s — run: python freq_route.py' % a.manifest)
        return 2
    rows = json.load(open(a.manifest, encoding='utf-8'))[:a.top]
    if not rows:
        print('empty manifest'); return 2

    heavy = light = covered = 0
    in_tok = out_tok = cost = base_cost = 0.0
    per_pass = {p['name']: {'in': 0.0, 'out': 0.0, 'cost': 0.0} for p in pipeline}
    oversize_unsplit = []   # (key1, bytes) oversize and no rootmap yet
    splits_ready = 0
    for r in rows:
        k1, b = r['key1'], r.get('bytes', 0)
        path, cov = route(k1)
        heavy += path == 'heavy'; light += path == 'light'; covered += cov
        subs = subcard_count(k1)
        oversize = b > a.ceiling
        if oversize and subs is None:
            oversize_unsplit.append((k1, b))
        if oversize and subs is not None:
            splits_ready += 1
        # token estimate: split roots cost per sub-card; others one card.
        units = subs if subs else 1
        content_in = b / a.chars_per_tok
        content_out = content_in * OUTPUT_RATIO
        for p in pipeline:
            if path not in p['paths']:
                continue
            pin, pcached, pout = MODELS[p['model']]
            f = p['factor']
            sys_tok = a.prompt_tok * units * f         # the locked system prompt — cacheable
            cont_in = content_in * f                   # the card content — unique, full price
            out_p = content_out * p['out_factor'] * f
            sys_cost = sys_tok / 1e6 * (pcached if a.cache else pin)
            c = sys_cost + cont_in / 1e6 * pin + out_p / 1e6 * pout
            in_tok += sys_tok + cont_in; out_tok += out_p; cost += c
            per_pass[p['name']]['in'] += sys_tok + cont_in
            per_pass[p['name']]['out'] += out_p
            per_pass[p['name']]['cost'] += c
        # "before" baseline: 4 full Opus passes, no caching.
        base_ci = (content_in + a.prompt_tok * units) * BASE_PASSES
        base_co = content_out * BASE_PASSES
        base_cost += base_ci / 1e6 * BASE_IN + base_co / 1e6 * BASE_OUT

    # Classify the oversize-unsplit cards: verbal roots (--root-split) vs non-root (sense-chunk).
    dp = div_p_counts([k for k, _ in oversize_unsplit]) if oversize_unsplit else {}
    roots = [(k, b, dp.get(k, 0)) for k, b in oversize_unsplit if dp.get(k, 0) > 0]
    nonroots = [(k, b) for k, b in oversize_unsplit if dp.get(k, 0) == 0]

    print('# scale-up pre-flight — top %d of %s\n' % (len(rows), os.path.basename(a.manifest)))
    print('## 1. Coverage')
    print('   heavy (full+judge): %d   light (single pass): %d' % (heavy, light))
    print('   covered (dict/corpus/KOW reuse): %d (%.0f%%)'
          % (covered, 100.0 * covered / len(rows)))
    print('   note: keys absent from a scale_route section manifest are counted heavy/uncovered (worst case).')
    print('## 2. Split-readiness (bytes > %d need sizing first)' % a.ceiling)
    print('   already split (rootmap present): %d' % splits_ready)
    print('   2a. VERBAL ROOTS oversize, not yet split: %d  -> --root-split (prefix segmentation)' % len(roots))
    for k1, b, n in roots[:10]:
        print('      %-14s %6d bytes  %d <div p>  ->  python _pilot_gen_merged.py --root-split %s' % (k1, b, n, k1))
    if len(roots) > 10:
        print('      … +%d more' % (len(roots) - 10))
    print('   2b. NON-ROOT oversize (0 prefix divs): %d  -> head/sense-chunk, NOT --root-split' % len(nonroots))
    for k1, b in nonroots[:10]:
        print('      %-14s %6d bytes  (polysemous noun/particle — needs the head sense-splitter)' % (k1, b))
    if len(nonroots) > 10:
        print('      … +%d more' % (len(nonroots) - 10))
    blockers = oversize_unsplit
    print('## 3. Cost projection (estimate; verify $/Mtok)')
    print('   config: translate=%s · judge=%s ×%d · repass=%s ×%.2f · prompt-cache=%s'
          % (a.translate_model, a.judge_model, a.judges, a.repass_model, a.repass_rate,
             'on' if a.cache else 'off'))
    for name in ('translate', 'judge', 'repass'):
        d = per_pass.get(name)
        if d:
            print('     %-9s in %5.1fM  out %4.1fM  $%-6.0f' % (name, d['in'] / 1e6, d['out'] / 1e6, d['cost']))
    print('   TOTAL  input ≈ %.1fM | output ≈ %.1fM | cost ≈ $%.0f%s'
          % (in_tok / 1e6, out_tok / 1e6, cost, '' if a.budget is None else '  (budget $%.0f)' % a.budget))
    save = 100.0 * (1 - cost / base_cost) if base_cost else 0.0
    print('   for comparison: ORIGINAL estimate (%d full Opus passes, no cache) ≈ $%.0f  → this config = %.0f%% less'
          % (BASE_PASSES, base_cost, save))
    print('   caveat: oversize-unsplit cards costed as 1 unit (LOWER bound); prompt-cache models '
          'cached reads at ~0.1× input and ignores the one-time per-window cache-write surcharge.')
    print('   NOTE: Opus-API pay-per-token REFERENCE only. Translation runs on Claude Max '
          '(≈$0 marginal); the binding limit is the Max weekly token quota, not USD. See PILOT_COST.md §7.')
    over_budget = a.budget is not None and cost > a.budget
    print('\n## Verdict')
    print('   coverage      : OK')
    print('   split-ready   : %s (%d blockers)' % ('PASS' if not blockers else 'BLOCKED', len(blockers)))
    print('   budget        : %s' % ('n/a' if a.budget is None else ('OVER' if over_budget else 'OK')))
    fail = over_budget or (a.strict and blockers)
    if over_budget:
        verdict = 'PRE-FLIGHT FAIL (over budget)'
    elif blockers:
        verdict = ('NOT READY: split %d oversize card(s) first%s'
                   % (len(blockers), ' [fatal under --strict]' if not a.strict else ''))
    else:
        verdict = 'CLEARED FOR SCALE-UP'
    print('   => %s' % verdict)
    return 1 if fail else 0


if __name__ == '__main__':
    raise SystemExit(main())
