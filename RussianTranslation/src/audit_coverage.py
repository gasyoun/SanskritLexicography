#!/usr/bin/env python
"""audit_coverage.py — FREE deterministic coverage gate (zero LLM tokens).

Part of the "Python at max, LLM at minimum" QA strategy (TOKEN_OPTIMIZATION_2026-06-27.md):
the LLM judge's only irreplaceable job is catching *mistranslation*; everything mechanical
is checked in Python for free. This gate catches the most common non-mechanical failure the
markup gate misses — a card that silently DROPS or FABRICATES senses.

For each card in wf_output.json vs its <stem>.raw.txt it compares:
  raw sense markers  = max(count '〉' U+3009 sense glyph, count '<div n=')   [PWG sense divs]
  card senses        = sum(len(record.senses)) in the produced card
and flags:
  COVERAGE-LOW(c/r)  card has < 0.80 * raw senses   (senses silently dropped)
  COVERAGE-OVER(c/r) card has > 1.50 * raw senses   (senses fabricated / over-split)
Cards with 0 raw markers (NWS / supplement / single-gloss cards) are not sense-divided —
coverage is reported as 'n/a', never failed.

  python audit_coverage.py wf_output.json            # audits every card in the workflow output

Exit non-zero if any card is flagged (CI-usable); re-queue flagged cards.
"""
import json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
# H1386 P3f: PWG_INPUT_DIR points a hermetic harness at a sandbox input dir.
IN = os.environ.get('PWG_INPUT_DIR') or os.path.join(HERE, 'pilot', 'input')

LOW, OVER = 0.80, 1.50
DIVN = re.compile(r'<div n=')
NUMBERED_DIVN = re.compile(r'<div n="(\d+)">')
LAYER_RE = re.compile(r'=== LAYER:.*?===\n', re.S)


def find_results(o):
    if isinstance(o, dict):
        if isinstance(o.get('results'), list):
            return o['results']
        for v in o.values():
            r = find_results(v)
            if r is not None:
                return r
    if isinstance(o, list):
        for v in o:
            r = find_results(v)
            if r is not None:
                return r
    return None


def layer_bodies(t):
    """Split a raw.txt into its independent '=== LAYER: ... ===' blocks. Most sub-cards carry
    exactly one layer; PW/SCH/PWKVN addenda cards bundle several independent revision entries
    into one sub-card file (e.g. gam~~h0_zz_pw04: 3 layers). Falls back to the whole text as a
    single block if no header is found."""
    parts = [b for b in LAYER_RE.split(t) if b.strip()]
    return parts or [t]


def layer_sense_count(body):
    """One layer's raw sense-marker count, counting only real sense boundaries.

    <div n="p"> is a STRUCTURAL prefix/secondary-conjugation divider elsewhere in this
    codebase (root_units.py, scale_preflight.py's _DIVP, verify_root_glue.py), never a sense
    number -- only the 'N〉' glyph and numbered <div n="N"> mark an actual new sense (a long
    citation list can reopen the same numeral across several continuation paragraphs, so
    distinct labels are counted, not raw occurrences). A layer with neither (pure
    cross-reference addenda, e.g. '-- Mit X, see II.5') still contributes its own
    translatable unit, floored at 1 rather than silently counting as zero senses."""
    nums = set(re.findall(r'(\d+)〉', body)) | set(NUMBERED_DIVN.findall(body))
    return len(nums) or 1


def raw_markers(stem):
    p = os.path.join(IN, stem + '.raw.txt')
    if not os.path.exists(p):
        return None
    t = open(p, encoding='utf-8').read()
    bodies = layer_bodies(t)
    if len(bodies) == 1:
        # Preserve the original single-layer heuristic verbatim (raw '<div n=' occurrence
        # count, including 'p' divs) to avoid changing behavior for the vast majority of
        # ordinary sub-cards; only multi-layer addenda cards get the layer-aware count below.
        # A genuine 0 here (no markers at all) must stay 0, not None -- the caller treats
        # None as NO-RAW/fail and 0 as the legitimate 'not sense-divided' case.
        body = bodies[0]
        return max(body.count('〉'), len(DIVN.findall(body)))
    return sum(layer_sense_count(b) for b in bodies)


def main():
    wf = sys.argv[1] if len(sys.argv) > 1 else 'wf_output.json'
    results = find_results(json.load(open(wf, encoding='utf-8'))) or []
    print('=== coverage audit (%d cards) ===' % len(results))
    print('%-28s %-8s %-8s %s' % ('unit', 'raw', 'card', 'flag'))
    fails = []
    for res in results:
        k = res.get('key')
        c = res.get('card') or {}
        cs = sum(len(rec.get('senses', [])) for rec in c.get('records', []))
        rm = raw_markers(k)
        if not c:
            print('%-28s %-8s %-8s %s' % (k, '-', '0', 'NO-CARD')); fails.append(k); continue
        if not rm:
            flag = 'NO-RAW' if rm is None else 'ok (not sense-divided)'
            print('%-28s %-8s %-8d %s' % (k, 'n/a', cs, flag))
            if rm is None:
                fails.append(k)
            continue
        if res.get('presplit'):
            # Presplit/fragment-reassembled cards (a huge head split into per-fragment
            # translation units, e.g. gam~~h0_63_sam_0) produce one JSON sense row per
            # fragment chunk by construction, not one per raw numbered sense -- that row
            # count is not comparable to the coarse raw <div>/glyph count and was tripping
            # COVERAGE-OVER as a false positive. A dropped/missing fragment is already caught
            # by audit_window.py's partial-card check, so skip the LOW/OVER thresholds here
            # rather than duplicate that signal with a confusing mismatch.
            print('%-28s %-8d %-8d %s' % (k, rm, cs, 'ok (presplit — granular fragment rows)'))
            continue
        # absolute-difference guard: a ±1 sense gap on a tiny card is sub-sense splitting /
        # merging, not a real drop/fabrication — require a meaningful absolute gap too.
        flag = ''
        if cs < rm * LOW and (rm - cs) >= 2:
            flag = 'COVERAGE-LOW(%d/%d)' % (cs, rm)
        elif cs > rm * OVER and (cs - rm) >= 3:
            flag = 'COVERAGE-OVER(%d/%d)' % (cs, rm)
        print('%-28s %-8d %-8d %s' % (k, rm, cs, flag or 'ok'))
        if flag:
            fails.append(k)
    print('\n%s: %d/%d covered%s' % (
        'PASS' if not fails else 'FAIL', len(results) - len(fails), len(results),
        '' if not fails else ' | flagged: ' + ', '.join(fails)))
    # Machine-readable verdict line — the parent audit_window.py parses THIS strictly rather
    # than scraping the prose summary above, so a future wording tweak here can never silently
    # drop flagged cards from the requeue (H169 defect 2).
    print('FLAGGED_JSON: %s' % json.dumps(fails))
    sys.exit(0 if not fails else 1)


if __name__ == '__main__':
    main()
