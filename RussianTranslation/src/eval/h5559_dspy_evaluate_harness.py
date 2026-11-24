#!/usr/bin/env python
"""h5559_dspy_evaluate_harness.py -- reusable OFFLINE DSPy Evaluate harness for
Sa->Ru prompts on the frozen BLI gold split (H5559).

_Created: 25-11-2026 · Last updated: 25-11-2026_
_Dr. Mārcis Gasūns_

DEV TOOL ONLY. `import dspy` lives exclusively in this file; consuming lanes
(cards / dictionary chain / KeySwap hints) copy the VERDICT, never this code
path (SKILLOPT_PIPELINE_MEMO estate ruling). No personal data; BLI gold only.

Subcommands (run from RussianTranslation/):

  build-split   derive the frozen split file from gold/gold_set.jsonl (idempotent,
                verifies against the committed file)
  render        LIVE  -- run one prompt over the split via dspy.Predict, temp 0,
                writing reports/H5559_predictions_<name>.jsonl (resumable: dspy cache)
  judge         LIVE  -- batched fidelity judge over a predictions file, merges
                verdicts in place
  evaluate      OFFLINE -- dspy.Evaluate over the frozen devset with a replay
                program + h5559_saru_metric => aggregate + per-item table.
                Zero network, zero LM: this is the offline-green core and the
                own-data canary (rerun => byte-identical scores).
  selftest      OFFLINE fixture run of the whole wiring (bare python, no dspy LM).

Metric contract: h5559_saru_metric.py (fidelity-judge + TM-match; IAST exactness
and case-government are hard fails; semantic-F1 alone is banned there, on record).

Usage:
  python src/eval/h5559_dspy_evaluate_harness.py selftest
  python src/eval/h5559_dspy_evaluate_harness.py build-split
  python src/eval/h5559_dspy_evaluate_harness.py render --prompt current
  python src/eval/h5559_dspy_evaluate_harness.py render --prompt variant
  python src/eval/h5559_dspy_evaluate_harness.py judge --file reports/H5559_predictions_current.jsonl
  python src/eval/h5559_dspy_evaluate_harness.py evaluate --file reports/H5559_predictions_current.jsonl
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.abspath(os.path.join(HERE, '..', '..'))
GOLD_PATH = os.path.join(RT, 'gold', 'gold_set.jsonl')
SPLIT_PATH = os.path.join(HERE, 'h5559_bli_gold_split.jsonl')
PROMPTS_PATH = os.path.join(HERE, 'h5559_prompts.json')
REPORTS = os.path.join(RT, 'reports')

LM_MODEL = 'gpt-oss:120b-cloud'
LM_API_BASE = 'http://localhost:11434/v1'   # local ollama OpenAI-compatible proxy
JUDGE_BATCH = 12
LIVE_THREADS = 6
LIVE_RETRIES = 3

sys.path.insert(0, HERE)
import h5559_saru_metric as M  # noqa: E402  (pure, stdlib-only)


# ---------------------------------------------------------------- split ----
def build_split(force=False):
    """Frozen devset beside this script: provenance meta line + one row per gold
    pair. Idempotent; refuses to drift from the committed file unless --force."""
    rows = []
    with open(GOLD_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            rows.append({'id': r['id'], 'slp1': r['slp1'], 'sa': r['sa'],
                         'ru': r['ru'], 'label': r['label']})
    meta = {
        '_meta': 'h5559_bli_gold_split.v1',
        'source': 'RussianTranslation/gold/gold_set.jsonl',
        'source_lock': 'review/locks/h215-gold-full-320-2026-08-14.lock.json',
        'n': len(rows),
        'note': ('Frozen Sa->Ru BLI gold split for the H5559 Evaluate harness; '
                 'derived unchanged from the frozen 320-row gold (H3172 card-3 '
                 'intent, ~300 items). No row re-cut, no label rewritten; the '
                 'H2401 500-frame stays label-free until its sheet is voted.'),
        'built': '25-11-2026',
    }
    payload = json.dumps(meta, ensure_ascii=False, sort_keys=True) + '\n' + \
        ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows)
    digest = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    if os.path.exists(SPLIT_PATH) and not force:
        on_disk = open(SPLIT_PATH, encoding='utf-8').read()
        if on_disk == payload:
            print(f'split OK (unchanged, sha256={digest[:12]}, n={len(rows)})')
            return digest
        print('split DRIFT: committed file differs from derivation -- inspect, '
              'then rerun with --force only if the source gold changed on purpose')
        sys.exit(2)
    with open(SPLIT_PATH, 'w', encoding='utf-8') as f:
        f.write(payload)
    print(f'split written n={len(rows)} sha256={digest[:12]}')
    return digest


def load_split():
    rows = []
    with open(SPLIT_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if '_meta' in r:
                continue
            rows.append(r)
    if not rows:
        sys.exit('empty split -- run build-split')
    return rows


def load_prompts():
    with open(PROMPTS_PATH, encoding='utf-8') as f:
        return json.load(f)


# ------------------------------------------------------------- live LM ----
def _make_lm():
    import dspy
    lm = dspy.LM('openai/' + LM_MODEL, api_base=LM_API_BASE, temperature=0,
                 max_tokens=2400, cache=True, api_key='ollama-local')
    dspy.configure(lm=lm)
    return lm


def _render_one(program, row):
    last = None
    for attempt in range(LIVE_RETRIES):
        try:
            out = program(sa=row['sa'], slp1=row['slp1'])
            return row['id'], (out.ru or '').strip()
        except Exception as e:  # transient API/lm errors: retry w/ backoff
            last = e
            time.sleep(2 ** attempt)
    return row['id'], f'__ERROR__:{type(last).__name__}'


def cmd_render(args):
    import dspy
    _make_lm()
    prompts = load_prompts()
    p = prompts[args.prompt]
    sig = dspy.Signature('sa, slp1 -> ru', p['instructions'])
    program = dspy.Predict(sig)
    rows = load_split()
    # resume support: keep already-good rows from an existing predictions file
    out_path = os.path.join(REPORTS, f'H5559_predictions_{args.prompt}.jsonl')
    done = {}
    if args.resume and os.path.exists(out_path):
        for line in open(out_path, encoding='utf-8'):
            r = json.loads(line)
            if not str(r.get('ru', '')).startswith('__ERROR__'):
                done[r['id']] = r
    todo = [r for r in rows if r['id'] not in done]
    print(f'render[{args.prompt}] model={LM_MODEL} temp=0 todo={len(todo)} '
          f'resumed={len(done)} threads={LIVE_THREADS}')
    results = dict(done)
    with cf.ThreadPoolExecutor(max_workers=LIVE_THREADS) as ex:
        for i, (rid, ru) in enumerate(ex.map(lambda r: _render_one(program, r), todo), 1):
            results[rid] = {**{k: v for k, v in
                               next(x for x in rows if x['id'] == rid).items()},
                            'ru_pred': ru, 'prompt': args.prompt,
                            'model': LM_MODEL, 'fidelity': None}
            if i % 40 == 0:
                print(f'  {i}/{len(todo)}')
    ordered = sorted(results.values(), key=lambda r: r['id'])
    with open(out_path, 'w', encoding='utf-8') as f:
        for r in ordered:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n')
    errs = sum(1 for r in ordered if str(r.get('ru_pred', '')).startswith('__ERROR__'))
    print(f'wrote {len(ordered)} rows -> {out_path} (errors={errs})')
    if errs:
        sys.exit(f'{errs} render errors -- rerun render --resume to retry them')


def _judge_batch(batch):
    payload = {
        'model': LM_MODEL, 'temperature': 0, 'max_tokens': 4200,
        'messages': [{'role': 'system', 'content': M.JUDGE_PROMPT},
                     {'role': 'user', 'content': json.dumps(
                         [{'id': r['id'], 'sa': r['sa'], 'ru_gold': r['ru'],
                           'ru_pred': r.get('ru_pred', '')} for r in batch],
                         ensure_ascii=False)}],
    }
    last = None
    for attempt in range(LIVE_RETRIES):
        try:
            req = urllib.request.Request(
                LM_API_BASE + '/chat/completions',
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read())
            text = data['choices'][0]['message']['content'].strip()
            if text.startswith('```'):
                text = text.strip('`').lstrip('json').strip()
            verdicts = json.loads(text)
            out = {}
            for v in verdicts:
                out[int(v['id'])] = int(v['score'])
            if len(out) != len(batch):
                raise ValueError(f'judge returned {len(out)} for batch {len(batch)}')
            return out
        except Exception as e:
            last = e
            time.sleep(2 ** attempt)
    print(f'  judge batch failed after {LIVE_RETRIES}: {type(last).__name__}: {last}')
    return {r['id']: None for r in batch}


def cmd_judge(args):
    rows = [json.loads(l) for l in open(args.file, encoding='utf-8')]
    batches = [rows[i:i + JUDGE_BATCH] for i in range(0, len(rows), JUDGE_BATCH)]
    print(f'judge {len(rows)} rows in {len(batches)} batches (threads=6, temp=0)')
    merged = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for out in ex.map(_judge_batch, batches):
            merged.update(out)
    missing = 0
    for r in rows:
        v = merged.get(r['id'])
        if v is None:
            missing += 1
        r['fidelity'] = v
    with open(args.file, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n')
    print(f'verdicts merged -> {args.file} (missing={missing})')
    if missing:
        sys.exit(f'{missing} rows lack a judge verdict -- rerun judge to fill them')


# ------------------------------------------------- OFFLINE evaluate core ----
def _score_rows(rows):
    scored = []
    for r in rows:
        s = M.score_example(r.get('ru_pred', ''), r['sa'], r['ru'], r.get('fidelity'))
        scored.append({**r, **s})
    return scored


def _aggregate(scored):
    n = len(scored)
    if not n:
        return {}
    return {
        'n': n,
        'score': round(sum(r['score'] for r in scored) / n, 4),
        'tm_match': round(sum(r['tm_match'] for r in scored) / n, 4),
        'fidelity_rate': round(sum(r['fidelity'] or 0 for r in scored) / n, 4),
        'hard_fail_rate': round(sum(r['hard_fail'] for r in scored) / n, 4),
        'iast_fail_n': sum(r['iast_fail'] for r in scored),
        'case_fail_n': sum(r['case_fail'] for r in scored),
        'no_verdict_n': sum(1 for r in scored if r.get('fidelity') is None),
    }


def cmd_evaluate(args):
    import dspy
    rows = [json.loads(l) for l in open(args.file, encoding='utf-8')]
    unjudged = sum(1 for r in rows if r.get('fidelity') is None)
    if unjudged:
        sys.exit(f'{unjudged} rows lack judge verdicts -- run `judge` first')
    preds = {r['id']: r for r in rows}
    examples = [dspy.Example(sa=r['sa'], slp1=r['slp1'], ru=r.get('ru_pred', ''),
                             id=r['id']).with_inputs('sa', 'slp1', 'id') for r in rows]

    def metric(example, pred, trace=None):
        src = preds[int(example.id)]
        s = M.score_example(pred.ru, src['sa'], src['ru'], src['fidelity'])
        return s['score']

    # drive dspy.Evaluate with a program that returns committed predictions:
    class Replay(dspy.Module):
        def forward(self, sa, slp1, id=None):  # noqa: A002 - dspy field name
            r = preds[int(id)]
            return dspy.Prediction(ru=r.get('ru_pred', ''))

    program = Replay()
    evaluate = dspy.Evaluate(devset=examples, metric=metric, num_threads=1,
                             display_progress=False, provide_trace=False)
    agg = evaluate(program)
    if isinstance(agg, dict):
        agg = agg.get('score', agg.get('mean', None))
    scored = _score_rows(rows)
    summary = _aggregate(scored)
    name = args.name or os.path.basename(args.file).replace(
        'H5559_predictions_', '').replace('.jsonl', '')
    summary['prompt'] = name
    summary['dspy_evaluate_mean'] = (
        round(float(agg) / 100.0, 4) if (agg is not None and float(agg) > 1.0)
        else (round(float(agg), 4) if agg is not None else None))
    summary['file_sha256'] = hashlib.sha256(
        open(args.file, 'rb').read()).hexdigest()[:16]
    out = os.path.join(REPORTS, f'H5559_scores_{name}.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'summary': summary, 'per_item': scored}, f,
                  ensure_ascii=False, sort_keys=True, indent=1)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    print(f'-> {out}')
    return summary


# ------------------------------------------------------------- selftest ----
def cmd_selftest(_args):
    """Offline wiring proof: metric gate behaviour on fixtures, no LM, no dspy."""
    checks = []
    # 1. hard fail fires on diacritic-stripping
    checks.append(('iast_mangle_detected',
                   M.iast_exactness_fail('юванам yuvanam', 'yuvānam')))
    checks.append(('iast_exact_passes',
                   not M.iast_exactness_fail('молодым yuvānam', 'yuvānam')))
    checks.append(('iast_hyphen_piece_ok',
                   not M.iast_exactness_fail('ко всем sarva-bhūteṣu',
                                             'sarva-bhūteṣu')))
    # 2. case-government slot rule
    checks.append(('case_wrong_gov_fails',
                   M.case_government_fail('под всем существам', 'ко всем существам')))
    checks.append(('case_same_slot_passes',
                   not M.case_government_fail('во всем', 'в')))  # gold no-gov? no: 'в' is gov
    checks.append(('case_no_gold_gov_passes',
                   not M.case_government_fail('о чём-то', 'молодым')))
    # 3. TM-match sanity
    checks.append(('tm_identical_one',
                   M.tm_match('ко всем существам', 'ко всем существам') == 1.0))
    checks.append(('tm_disjoint_zero',
                   M.tm_match('совсем другое', 'ко всем существам') == 0.0))
    # 4. score gating: perfect words + wrong case gov -> 0
    s = M.score_example('под всем', 'X', 'ко всем', fidelity=1)
    checks.append(('hard_fail_gates_zero', s['score'] == 0.0 and s['hard_fail']))
    s2 = M.score_example('ко всем существам', 'X', 'ко всем существам', fidelity=1)
    checks.append(('clean_row_full_score', s2['score'] == 1.0))
    # 5. semantic-F1 ban is documented on record
    doc = open(os.path.join(HERE, 'h5559_saru_metric.py'), encoding='utf-8').read()
    checks.append(('semantic_f1_ban_documented', 'semantic-F1 alone is banned' in doc))
    failed = [k for k, v in checks if not v]
    for k, v in checks:
        print(f'  {"PASS" if v else "FAIL"} {k}')
    print(f'selftest: {len(checks) - len(failed)}/{len(checks)} PASS '
          f'(offline, no LM, no dspy)')
    sys.exit(1 if failed else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build-split')
    b.add_argument('--force', action='store_true')
    r = sub.add_parser('render')
    r.add_argument('--prompt', choices=['current', 'variant'], required=True)
    r.add_argument('--resume', action='store_true')
    j = sub.add_parser('judge')
    j.add_argument('--file', required=True)
    e = sub.add_parser('evaluate')
    e.add_argument('--file', required=True)
    e.add_argument('--name', default=None)
    sub.add_parser('selftest')
    args = ap.parse_args()
    os.makedirs(REPORTS, exist_ok=True)
    {'build-split': lambda a: build_split(a.force),
     'render': cmd_render, 'judge': cmd_judge, 'evaluate': cmd_evaluate,
     'selftest': cmd_selftest}[args.cmd](args)


if __name__ == '__main__':
    main()
