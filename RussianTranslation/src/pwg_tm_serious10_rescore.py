#!/usr/bin/env python
"""H3611 - re-score the 10 H2877 sidecar repairs with a real paid judge.

Protocol is H3299's, not a new one: the judge labels each row with exactly ONE
`defect_class` drawn from `pwg_tm_quality.SEVERITY_RUBRIC`, and `serious_error`
is DERIVED from that table locally - never asked of the model, never re-judged
per fragment class. Each row is judged in its own call, blind: the judge sees
the source and the (repaired) target and nothing else. It is not told that a
repair happened, what the previous target was, or what H2877 classified it as.

Two judges run:

  * `x-ai/grok-4.5`  - the INDEPENDENT gate. Same judge model as the H2684
    before-score, so its result is directly comparable. This is the only score
    that may be cited as independent.
  * `x-ai/grok-4.6`  - the self-score MG authorised on 28-08-2026. Grok 4.6
    generated the Wave-1 targets, so `pwg_tm_quality.independence_errors`
    rejects it by design (`FORBIDDEN_INDEPENDENT_JUDGES`). It is recorded in
    its own file, flagged non-independent, and used only for a 4.5-vs-4.6
    agreement measurement.

Key values come from the environment or the gitignored `src/.env` (R5.2) and
are never printed. Wave-1 bytes are never opened for writing.

  python src/pwg_tm_serious10_rescore.py --selftest
  python src/pwg_tm_serious10_rescore.py run --sidecar <path> --out <dir>
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_quality as Q  # noqa: E402

HANDOFF = 'H3611'
BASE = 'https://openrouter.ai/api/v1'
INDEPENDENT_JUDGE = 'x-ai/grok-4.5'
AUTHORISED_SELF_JUDGE = 'x-ai/grok-4.6'
ENV_FILE = os.path.join(HERE, '.env')

DEFECT_CLASSES = tuple(sorted(Q.SEVERITY_RUBRIC))

SYSTEM_PROMPT = (
    'You are an independent adjudicator for a German-to-Russian scholarly '
    'dictionary translation memory (Petersburger Woerterbuch, Boehtlingk-Roth). '
    'You judge one fragment at a time, against its German source only. '
    'You never see, and must never assume, how the target was produced.\n\n'
    'House conventions that are CORRECT and must not be penalised:\n'
    '- Sanskrit in `{#...#}`, literary sigla in `<ls>...</ls>`, and '
    'lexicographic abbreviations in `<ab>...</ab>` are kept VERBATIM in the '
    'target. An `<ab>` token identical to its source is correct, not '
    'untranslated.\n'
    '- `{%...%}` spans hold natural-language gloss prose and are the part '
    'that gets translated into Russian.\n\n'
    'Return STRICT JSON only, no prose outside it, with exactly these keys:\n'
    '  "defect_class": one of __CLASSES__\n'
    '  "fidelity": "pass" or "fail"   (is the target faithful to the source, '
    'with nothing invented and nothing silently dropped?)\n'
    '  "equivalence": "correct" or "fail"   (does the target carry the same '
    'meaning a Russian lexicographer would accept?)\n'
    '  "notes": one short English sentence naming the exact span at fault, or '
    'why it is clean.\n\n'
    'Definitions of defect_class you must use:\n'
    '  none                            - faithful and equivalent\n'
    '  placeholder_rendered_as_content - an argument-slot placeholder such as '
    '"Jmd" rendered as a content phrase\n'
    '  wrong_lexical_meaning           - a gloss translated to the wrong sense\n'
    '  sense_absent_or_inverted        - a sense dropped or reversed\n'
    '  sanskrit_dropped_or_altered     - `{#...#}` or `<ls>` content changed\n'
    '  unfaithful_to_source            - target asserts something the source '
    'does not\n'
    '  german_residue                  - a `{%...%}` span left in German\n'
    '  markup_drift                    - a preserved span altered in form\n'
    '  register_or_style               - meaning holds, register is off\n'
    '  target_typo                     - a typo in the Russian only\n\n'
    'Pick the SINGLE most severe applicable class. Do NOT output a severity '
    'or seriousness field: severity is derived from defect_class downstream.'
).replace('__CLASSES__', ', '.join(DEFECT_CLASSES))

USER_TEMPLATE = (
    'Fragment class: %(fragment_class)s\n'
    'Headword (SLP1): %(key1)s\n\n'
    'GERMAN SOURCE:\n%(source)s\n\n'
    'RUSSIAN TARGET:\n%(target)s\n\n'
    'Return the JSON object now.'
)


def load_key(env_file=None):
    """Key from the environment, else the gitignored .env. Never printed."""
    key = os.environ.get('OPENROUTER_API_KEY')
    if key:
        return key, 'process env'
    path = env_file or ENV_FILE
    if not os.path.exists(path):
        return None, 'absent'
    for line in io.open(path, encoding='utf-8'):
        line = line.strip()
        if line.startswith('#') or '=' not in line:
            continue
        name, _, value = line.partition('=')
        if name.strip() == 'OPENROUTER_API_KEY':
            value = value.strip().strip('"').strip("'")
            if value:
                return value, os.path.basename(path)
    return None, 'not in .env'


def blind_item(row):
    """What the judge sees. Everything H2877 knows is withheld."""
    loc = row.get('source_locator') or {}
    return {
        'record_id': row['record_id'],
        'fragment_class': row.get('fragment_class'),
        'key1': loc.get('key1') or (row.get('entry_id') or '').split(':')[-1],
        'source': row.get('source_string') or '',
        'target': row.get('target_after') or row.get('target_string') or '',
    }


JSON_BLOCK = re.compile(r'\{.*\}', re.S)


def parse_verdict(text):
    """Tolerate a fenced or prose-wrapped JSON object; fail loud otherwise."""
    match = JSON_BLOCK.search(text or '')
    if not match:
        raise ValueError('no JSON object in judge reply: %r' % (text or '')[:200])
    return json.loads(match.group(0))


def normalise_verdict(raw):
    dc = str(raw.get('defect_class') or '').strip()
    if dc not in Q.SEVERITY_RUBRIC:
        raise ValueError('judge returned unknown defect_class %r' % dc)
    fid = str(raw.get('fidelity') or '').strip().lower()
    eq = str(raw.get('equivalence') or '').strip().lower()
    if fid not in ('pass', 'fail'):
        raise ValueError('bad fidelity %r' % fid)
    if eq not in ('correct', 'fail'):
        raise ValueError('bad equivalence %r' % eq)
    return {
        'defect_class': dc,
        'fidelity': fid,
        'equivalence': eq,
        # DERIVED from the pinned rubric - never taken from the model.
        'serious_error': bool(Q.rubric_serious(dc)),
        'notes': str(raw.get('notes') or '').strip()[:400],
    }


def call_judge(key, model, item, timeout=180, retries=3):
    body = {
        'model': model,
        'temperature': 0,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': USER_TEMPLATE % item},
        ],
        'usage': {'include': True},
    }
    data = json.dumps(body).encode('utf-8')
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(
            BASE + '/chat/completions', data=data,
            headers={'Authorization': 'Bearer ' + key,
                     'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode('utf-8'))
            text = payload['choices'][0]['message']['content']
            usage = payload.get('usage') or {}
            return parse_verdict(text), {
                'input_tokens': usage.get('prompt_tokens', 0),
                'output_tokens': usage.get('completion_tokens', 0),
                'cost_usd': usage.get('cost', 0.0),
                'provider_model': payload.get('model'),
            }
        except (urllib.error.URLError, KeyError, ValueError, TimeoutError) as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError('judge %s failed after %d attempts: %r'
                       % (model, retries, last))


def judge_all(key, model, rows, judge_tag):
    out, spend = [], {'input_tokens': 0, 'output_tokens': 0, 'cost_usd': 0.0,
                      'calls': 0}
    for i, row in enumerate(rows):
        item = blind_item(row)
        verdict, usage = call_judge(key, model, item)
        verdict = normalise_verdict(verdict)
        verdict['judge_id'] = '%s-row-%02d' % (judge_tag, i)
        verdict['judge_model'] = judge_tag
        out.append({
            'schema': 'pwg.tm.serious10.rescore.v1',
            'handoff': HANDOFF,
            'record_id': row['record_id'],
            'entry_id': row.get('entry_id'),
            'fragment_class': row.get('fragment_class'),
            'source_string': row.get('source_string'),
            'target_scored': item['target'],
            'h2877_codes': row.get('codes'),
            'adjudication': verdict,
        })
        for field in ('input_tokens', 'output_tokens', 'cost_usd'):
            spend[field] += usage.get(field) or 0
        spend['calls'] += 1
        print('  %-2d %-10s %-32s %s' % (
            i, row.get('fragment_class', '')[:10],
            verdict['defect_class'],
            'SERIOUS' if verdict['serious_error'] else 'ok'))
    return out, spend


def summarise(rows):
    n = len(rows)
    serious = sum(1 for r in rows if r['adjudication']['serious_error'])
    fid = sum(1 for r in rows if r['adjudication']['fidelity'] == 'pass')
    eq = sum(1 for r in rows if r['adjudication']['equivalence'] == 'correct')
    classes = {}
    for r in rows:
        dc = r['adjudication']['defect_class']
        classes[dc] = classes.get(dc, 0) + 1
    return {'n': n, 'serious': serious, 'fidelity_pass': fid,
            'equivalence_correct': eq, 'defect_classes': classes}


def agreement(a_rows, b_rows):
    by_a = {r['record_id']: r['adjudication'] for r in a_rows}
    same_class = same_sev = 0
    disagreements = []
    for r in b_rows:
        a = by_a.get(r['record_id'])
        b = r['adjudication']
        if a is None:
            continue
        if a['defect_class'] == b['defect_class']:
            same_class += 1
        else:
            disagreements.append({
                'record_id': r['record_id'],
                'entry_id': r.get('entry_id'),
                INDEPENDENT_JUDGE: a['defect_class'],
                AUTHORISED_SELF_JUDGE: b['defect_class'],
            })
        if a['serious_error'] == b['serious_error']:
            same_sev += 1
    total = len(b_rows) or 1
    return {'n': len(b_rows),
            'defect_class_agreement': round(same_class / total, 4),
            'severity_agreement': round(same_sev / total, 4),
            'disagreements': disagreements}


def write_jsonl(path, rows):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + '\n')


def cmd_run(args):
    key, where = load_key(args.env_file)
    if not key:
        raise SystemExit('OPENROUTER_API_KEY not set (looked in env and %s)'
                         % (args.env_file or ENV_FILE))
    print('key source: %s' % where)
    rows = [json.loads(line) for line in io.open(args.sidecar, encoding='utf-8')
            if line.strip()]
    print('rows to re-score: %d' % len(rows))
    os.makedirs(args.out, exist_ok=True)

    print('\n== independent judge %s ==' % INDEPENDENT_JUDGE)
    ind_rows, ind_spend = judge_all(key, INDEPENDENT_JUDGE, rows, 'grok-4.5')
    ind_errors = Q.independence_errors(ind_rows)
    ind_consistency = Q.check_severity_consistency(ind_rows)

    self_rows, self_spend, self_errors, self_consistency = [], {}, [], []
    if not args.skip_self_score:
        print('\n== authorised self-score %s ==' % AUTHORISED_SELF_JUDGE)
        self_rows, self_spend = judge_all(
            key, AUTHORISED_SELF_JUDGE, rows, 'grok-4.6')
        self_errors = Q.independence_errors(self_rows)
        self_consistency = Q.check_severity_consistency(self_rows)

    write_jsonl(os.path.join(args.out, 'serious10_rescore_grok45.jsonl'), ind_rows)
    if self_rows:
        write_jsonl(os.path.join(args.out, 'serious10_rescore_grok46.jsonl'),
                    self_rows)

    receipt = {
        'schema': 'pwg.tm.serious10.rescore.receipt.v1',
        'handoff': HANDOFF,
        'repairs_from': 'H2877',
        'protocol': 'H3299 pinned severity rubric; serious_error DERIVED, blind, one call per row',
        'route': 'openrouter',
        'independent': {
            'judge_model': INDEPENDENT_JUDGE,
            'independence_errors': ind_errors,
            'severity_consistency_violations': ind_consistency,
            'scores': summarise(ind_rows),
            'spend': ind_spend,
            'cost_evaluable': True,
        },
        'authorised_self_score': {
            'judge_model': AUTHORISED_SELF_JUDGE,
            'authorised_by': 'MG 28-08-2026',
            'is_independent': False,
            'why_not': ('Grok 4.6 generated the Wave-1 targets; '
                        'pwg_tm_quality.FORBIDDEN_INDEPENDENT_JUDGES rejects it'),
            'independence_errors_expected_nonempty': len(self_errors),
            'severity_consistency_violations': self_consistency,
            'scores': summarise(self_rows) if self_rows else None,
            'spend': self_spend,
        },
        'agreement': agreement(ind_rows, self_rows) if self_rows else None,
        'total_cost_usd': round((ind_spend.get('cost_usd') or 0)
                                + (self_spend.get('cost_usd') or 0), 6),
    }
    rp = os.path.join(args.out, 'serious10_rescore_receipt.json')
    with io.open(rp, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=2)
        fh.write('\n')

    ind = receipt['independent']
    print('\nindependent %s: serious %d/%d, fidelity %d, equivalence %d'
          % (INDEPENDENT_JUDGE, ind['scores']['serious'], ind['scores']['n'],
             ind['scores']['fidelity_pass'], ind['scores']['equivalence_correct']))
    print('independence_errors (must be empty): %r' % ind_errors)
    print('severity consistency violations: %r' % ind_consistency)
    if self_rows:
        s = receipt['authorised_self_score']['scores']
        print('self-score %s: serious %d/%d (NOT independent, %d guard errors)'
              % (AUTHORISED_SELF_JUDGE, s['serious'], s['n'], len(self_errors)))
        print('agreement: class %.2f severity %.2f'
              % (receipt['agreement']['defect_class_agreement'],
                 receipt['agreement']['severity_agreement']))
    print('total cost USD: %s' % receipt['total_cost_usd'])
    print('wrote %s' % rp)
    return 0


def cmd_packet(args):
    """Emit the blind packet + the judging brief for a SESSION-run judge.

    H2684's own independent gate was session-drafted, not an API call (its
    cost ledger records `calls: 65` with zero tokens and
    `cost_evaluable: false`). This path reproduces that: a Grok 4.5 session
    reads one self-contained file and returns the same JSON `run` expects, so
    the re-score does not depend on any account having credit.
    """
    rows = [json.loads(line) for line in io.open(args.sidecar, encoding='utf-8')
            if line.strip()]
    os.makedirs(args.out, exist_ok=True)
    items = [blind_item(r) for r in rows]
    pk = os.path.join(args.out, 'serious10_blind_packet.jsonl')
    write_jsonl(pk, items)

    brief = os.path.join(args.out, 'serious10_judge_brief.md')
    lines = [
        '# Blind judging brief - 10 PWG TM fragments',
        '',
        '_Created: 28-08-2026 - Last updated: 28-08-2026_',
        '',
        'Judge model required: **Grok 4.5 (`grok-4.5`)**. Grok 4.6 may NOT run '
        'this as an independent gate - it generated the targets, and '
        '`pwg_tm_quality.independence_errors` refuses it.',
        '',
        '## Rules',
        '',
        SYSTEM_PROMPT,
        '',
        '## Output',
        '',
        'Return one JSON object per fragment, in packet order, as a JSON array. '
        'Each object carries `record_id`, `defect_class`, `fidelity`, '
        '`equivalence`, `notes`. Do NOT output a seriousness field.',
        '',
        '## The 10 fragments',
        '',
    ]
    for i, item in enumerate(items):
        lines += [
            '### %d. `%s` (%s, headword `%s`)' % (
                i, item['record_id'][:52], item['fragment_class'], item['key1']),
            '',
            '**German source:**',
            '',
            '```', item['source'], '```',
            '',
            '**Russian target:**',
            '',
            '```', item['target'], '```',
            '',
        ]
    lines += ['_Dr. Mārcis Gasūns_', '']
    with io.open(brief, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lines))

    print('blind packet: %d rows -> %s' % (len(items), pk))
    print('judging brief -> %s' % brief)
    leaked = [k for it in items for k in it
              if k in ('target_before', 'codes', 'actions', 'judge_before')]
    print('H2877 state leaked into the packet: %d fields' % len(leaked))
    return 0


def selftest():
    assert INDEPENDENT_JUDGE == 'x-ai/grok-4.5'
    # The guard must accept 4.5 and reject 4.6 - the whole point of two files.
    ok = [{'adjudication': {'judge_model': 'grok-4.5'}}]
    bad = [{'adjudication': {'judge_model': 'grok-4.6'}}]
    assert Q.independence_errors(ok) == []
    assert Q.independence_errors(bad), 'grok-4.6 must be refused as independent'

    # serious_error is derived, never read from the model's reply.
    v = normalise_verdict({'defect_class': 'german_residue', 'fidelity': 'pass',
                           'equivalence': 'correct', 'notes': 'x',
                           'serious_error': True})
    assert v['serious_error'] is False, 'rubric must override the model'
    v = normalise_verdict({'defect_class': 'placeholder_rendered_as_content',
                           'fidelity': 'pass', 'equivalence': 'fail',
                           'notes': 'x', 'serious_error': False})
    assert v['serious_error'] is True
    try:
        normalise_verdict({'defect_class': 'invented', 'fidelity': 'pass',
                           'equivalence': 'correct'})
    except ValueError:
        pass
    else:
        raise AssertionError('unknown defect_class must fail loud')

    assert parse_verdict('```json\n{"a": 1}\n```') == {'a': 1}
    row = {'record_id': 'r', 'fragment_class': 'sense',
           'entry_id': 'pwg.entry:gam', 'source_string': 'S',
           'target_before': 'BEFORE', 'target_after': 'AFTER',
           'codes': ['T2'], 'actions': [{'how': 'revert_to_source'}]}
    item = blind_item(row)
    assert item['target'] == 'AFTER'
    leaked = set(item) & {'target_before', 'codes', 'actions', 'judge_before'}
    assert not leaked, 'blind item leaks H2877 state: %r' % leaked
    print('pwg_tm_serious10_rescore selftest OK - guard, derived severity, blindness')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selftest', action='store_true')
    sub = ap.add_subparsers(dest='cmd')
    run = sub.add_parser('run')
    run.add_argument('--sidecar', required=True)
    run.add_argument('--out', required=True)
    run.add_argument('--env-file')
    run.add_argument('--skip-self-score', action='store_true')
    pk = sub.add_parser('packet')
    pk.add_argument('--sidecar', required=True)
    pk.add_argument('--out', required=True)
    args = ap.parse_args(argv)
    if args.selftest or not args.cmd:
        return selftest()
    if args.cmd == 'run':
        return cmd_run(args)
    if args.cmd == 'packet':
        return cmd_packet(args)
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
