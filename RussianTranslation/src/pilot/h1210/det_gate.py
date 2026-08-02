#!/usr/bin/env python
r"""H1210 — Python twin of the H1209 v2 in-JS `deterministicAudit()` (wf_template.js).

The A/B is only meaningful if BOTH arms pass through the SAME free gate before the same
Opus controller sees the card. Arm A runs that gate inside the Workflow script (JS); arm B
generates with DeepSeek from Python, so it needs the identical gate here.

Ported line-for-line from `src/pilot/h1209/wf_template.js` (v2 gates, all HARD, each
triggering the free retry):

  1. german+grammar {Tn} multiset == skeleton   (canonical TNMASK, armed)
  2. russian {Tn} multiset == skeleton          (mask-level H1152 guard 2)
  3. sense SHORTFALL only: emitted < source_senses (canonical SAN-LOSS direction)
  4. empty russian

`coverage` stays reported for telemetry continuity with the arm-A rows.

Drift between this file and the JS is the C-01 class of defect, so `selftest` asserts the
two agree on hand-built fixtures covering every issue branch.

Usage: python src/pilot/h1210/det_gate.py selftest
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TOK = re.compile(r'\{T\d+\}')


def token_list(s):
    return TOK.findall(str(s or ''))


def fidelity_tokens(card):
    """{Tn} over the canonical TOKEN_FIDELITY_FIELDS (record.grammar + sense.german)."""
    toks = []
    for r in (card.get('records') or []):
        toks += token_list(r.get('grammar'))
        for s in (r.get('senses') or []):
            toks += token_list(s.get('german'))
    return toks


def translation_tokens(card, field='russian'):
    toks = []
    for r in (card.get('records') or []):
        for s in (r.get('senses') or []):
            toks += token_list(s.get(field))
    return toks


def output_sense_count(card):
    return sum(len(r.get('senses') or []) for r in (card.get('records') or []))


def multiset_diff(want, got):
    """Tokens still owed by `got` — the JS multisetDiff twin (key order preserved)."""
    need, order = {}, []
    for t in want:
        if t not in need:
            need[t] = 0
            order.append(t)
        need[t] += 1
    for t in got:
        if need.get(t):
            need[t] -= 1
    return [t for t in order if need.get(t)]


def deterministic_audit(card, c, field='russian'):
    """`c` is the prep_slice card dict (skeleton_tokens, source_senses). Returns
    {'issues': [...], 'coverage': float} exactly as the JS gate does."""
    issues = []
    want = c['skeleton_tokens']
    got_fid = fidelity_tokens(card)
    missing_fid = multiset_diff(want, got_fid)
    invented_fid = multiset_diff(got_fid, want)
    if missing_fid:
        issues.append(
            "fidelity: masked spans missing from senses' german: "
            + ','.join(missing_fid[:20])
            + ' — EVERY {Tn} from the source must appear in a sense\'s german AND ' + field + ','
            ' in source order; card.notes must NOT hold source {Tn} spans (notes is never'
            ' unmasked, so content parked there is LOST)')
    if invented_fid:
        issues.append('invented-placeholders in german: ' + ','.join(invented_fid[:10]))
    got_tr = translation_tokens(card, field)
    missing_tr = multiset_diff(want, got_tr)
    invented_tr = multiset_diff(got_tr, want)
    if missing_tr:
        issues.append(
            "translation-fidelity: masked spans missing from senses' " + field + ': '
            + ','.join(missing_tr[:20])
            + ' — the ' + field + ' text must carry the same {Tn} spans as the german'
            ' (citations/Sanskrit are language-independent)')
    if invented_tr:
        issues.append('invented-placeholders in ' + field + ': ' + ','.join(invented_tr[:10]))
    osc = output_sense_count(card)
    src = c.get('source_senses') or 0
    if src > 1 and osc < src:
        issues.append('sense-shortfall: output %d senses < source\'s %d declared top-level '
                      'senses — a sense was dropped (emitting MORE than %d is fine)'
                      % (osc, src, src))
    for r in (card.get('records') or []):
        for s in (r.get('senses') or []):
            if not str(s.get(field) or '').strip():
                issues.append('empty-%s: sense %s' % (field, s.get('tag') or '?'))
    got_set = set(got_fid)
    covered = len([t for t in want if t in got_set])
    coverage = round(covered / len(want), 2) if want else 1
    return {'issues': issues, 'coverage': coverage}


# ------------------------------------------------------------------------ selftest
def _card(senses, grammar='', notes=''):
    return {'records': [{'grammar': grammar, 'senses': senses}], 'notes': notes}


def selftest():
    fails = []

    def check(name, cond):
        print(('  ok   ' if cond else '  FAIL ') + name)
        if not cond:
            fails.append(name)

    c = {'skeleton_tokens': ['{T1}', '{T2}'], 'source_senses': 2}

    clean = _card([{'tag': '1', 'german': 'x {T1}', 'russian': 'х {T1}'},
                   {'tag': '2', 'german': 'y {T2}', 'russian': 'у {T2}'}])
    r = deterministic_audit(clean, c)
    check('clean card -> no issues, coverage 1.0', r['issues'] == [] and r['coverage'] == 1)

    drop_de = _card([{'tag': '1', 'german': 'x', 'russian': 'х {T1}'},
                     {'tag': '2', 'german': 'y {T2}', 'russian': 'у {T2}'}])
    r = deterministic_audit(drop_de, c)
    check('german span dropped -> fidelity issue',
          any(i.startswith('fidelity:') for i in r['issues']))
    check('german span dropped -> coverage 0.5', r['coverage'] == 0.5)

    drop_ru = _card([{'tag': '1', 'german': 'x {T1}', 'russian': 'х'},
                     {'tag': '2', 'german': 'y {T2}', 'russian': 'у {T2}'}])
    r = deterministic_audit(drop_ru, c)
    check('russian-only drop -> translation-fidelity issue (H1152 guard 2)',
          any(i.startswith('translation-fidelity:') for i in r['issues']))

    invented = _card([{'tag': '1', 'german': 'x {T1}{T9}', 'russian': 'х {T1}'},
                      {'tag': '2', 'german': 'y {T2}', 'russian': 'у {T2}'}])
    r = deterministic_audit(invented, c)
    check('invented placeholder -> invented issue',
          any(i.startswith('invented-placeholders in german') for i in r['issues']))

    short = _card([{'tag': '1', 'german': 'x {T1}{T2}', 'russian': 'х {T1}{T2}'}])
    r = deterministic_audit(short, c)
    check('sense shortfall -> sanloss issue',
          any(i.startswith('sense-shortfall') for i in r['issues']))

    over = _card([{'tag': '1', 'german': 'x {T1}', 'russian': 'х {T1}'},
                  {'tag': '2', 'german': 'y {T2}', 'russian': 'у {T2}'},
                  {'tag': '3', 'german': 'z', 'russian': 'з'}])
    r = deterministic_audit(over, c)
    check('over-emission is NEVER an issue (canonical SAN-LOSS direction)',
          not any(i.startswith('sense-shortfall') for i in r['issues']))

    empty = _card([{'tag': '1', 'german': 'x {T1}', 'russian': '  '},
                   {'tag': '2', 'german': 'y {T2}', 'russian': 'у {T2}'}])
    r = deterministic_audit(empty, c)
    check('empty russian -> empty-russian issue',
          any(i.startswith('empty-russian') for i in r['issues']))

    # H2226: EN target field path (same gate, different field name)
    en_clean = _card([{'tag': '1', 'german': 'x {T1}', 'english': 'x {T1}'},
                      {'tag': '2', 'german': 'y {T2}', 'english': 'y {T2}'}])
    r = deterministic_audit(en_clean, c, field='english')
    check('EN clean card -> no issues', r['issues'] == [] and r['coverage'] == 1)
    en_drop = _card([{'tag': '1', 'german': 'x {T1}', 'english': 'x'},
                     {'tag': '2', 'german': 'y {T2}', 'english': 'y {T2}'}])
    r = deterministic_audit(en_drop, c, field='english')
    check('EN target drop -> translation-fidelity names english',
          any('english' in i and i.startswith('translation-fidelity:') for i in r['issues']))
    en_empty = _card([{'tag': '1', 'german': 'x {T1}', 'english': '  '},
                      {'tag': '2', 'german': 'y {T2}', 'english': 'y {T2}'}])
    r = deterministic_audit(en_empty, c, field='english')
    check('empty english -> empty-english issue',
          any(i.startswith('empty-english') for i in r['issues']))

    # grammar carries fidelity tokens too (record-level TOKEN_FIDELITY_FIELDS)
    in_grammar = _card([{'tag': '1', 'german': 'x', 'russian': 'х {T1}'},
                        {'tag': '2', 'german': 'y {T2}', 'russian': 'у {T2}'}],
                       grammar='{T1}')
    r = deterministic_audit(in_grammar, c)
    check('record.grammar counts toward the fidelity multiset',
          not any(i.startswith('fidelity:') for i in r['issues']))

    # multiset, not set: a duplicated token does not cover two occurrences
    c2 = {'skeleton_tokens': ['{T1}', '{T1}'], 'source_senses': 1}
    dup = _card([{'tag': '1', 'german': '{T1}', 'russian': '{T1}{T1}'}])
    r = deterministic_audit(dup, c2)
    check('multiset semantics: one of two {T1} occurrences missing is an issue',
          any(i.startswith('fidelity:') for i in r['issues']))

    print('det_gate selftest: %d check(s) failed' % len(fails))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(selftest() if (len(sys.argv) > 1 and sys.argv[1] == 'selftest')
             else print(__doc__) or 0)
