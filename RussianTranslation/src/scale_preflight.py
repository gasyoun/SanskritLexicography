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

  python scale_preflight.py --top 500 --budget 400
  python scale_preflight.py --top 500 --ceiling 8000 --chars-per-tok 3 --strict
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
PROMPT_OVERHEAD_TOK = 3000          # the locked merged-translate system prompt, per call
OUTPUT_RATIO = 1.2                  # Russian card+JSON ≈ 1.2× the source content tokens
PASSES = {'heavy': 4, 'light': 1}   # heavy = translate + 2 judges + ~repass; light = 1 pass
# heavy path -> Opus, light path -> Sonnet ($/Mtok in,out). Override via flags.
PRICE = {'heavy': (15.0, 75.0), 'light': (3.0, 15.0)}

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
    a = ap.parse_args()

    if not os.path.exists(a.manifest):
        print('NO freq manifest at %s — run: python freq_route.py' % a.manifest)
        return 2
    rows = json.load(open(a.manifest, encoding='utf-8'))[:a.top]
    if not rows:
        print('empty manifest'); return 2

    heavy = light = covered = 0
    in_tok = out_tok = cost = 0.0
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
        per_unit_in = content_in / max(units, 1) + PROMPT_OVERHEAD_TOK
        ci = per_unit_in * units * PASSES[path]
        co = (content_in / max(units, 1)) * OUTPUT_RATIO * units * PASSES[path]
        pin, pout = PRICE[path]
        in_tok += ci; out_tok += co
        cost += ci / 1e6 * pin + co / 1e6 * pout

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
    print('   input  tokens ≈ %.1fM' % (in_tok / 1e6))
    print('   output tokens ≈ %.1fM' % (out_tok / 1e6))
    print('   projected cost ≈ $%.0f%s' % (cost, '' if a.budget is None else '  (budget $%.0f)' % a.budget))
    print('   caveat: not-yet-split oversize cards are costed as 1 unit; once chunked they cost more, '
          'so this is a LOWER bound for the batch.')
    print('   NOTE: Opus-API pay-per-token REFERENCE only. Translation runs on Claude Max '
          '(≈$0 marginal); the binding limit is the Max weekly token quota, not USD. See PILOT_COST.md §7.')
    over_budget = a.budget is not None and cost > a.budget
    print('\n## Verdict')
    print('   coverage      : OK')
    print('   split-ready   : %s (%d blockers)' % ('PASS' if not blockers else 'BLOCKED', len(blockers)))
    print('   budget        : %s' % ('n/a' if a.budget is None else ('OVER' if over_budget else 'OK')))
    fail = over_budget or (a.strict and blockers)
    print('   => %s' % ('PRE-FLIGHT FAIL' if fail else 'CLEARED FOR SCALE-UP'))
    return 1 if fail else 0


if __name__ == '__main__':
    raise SystemExit(main())
