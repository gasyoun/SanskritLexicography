#!/usr/bin/env python
"""H1350 W1.5 -- bounded (<=50-card) LLM sanity check of the corrected <> splitter.

Stratified sample from the W1.4 audit's "changed" records (records/reports/
pwg_sense_glyph_audit.json): asks DeepSeek (--backend openai, no Anthropic
key -- see reference_no_anthropic_key_use_deepseek memory) whether the
CORRECTED sense count reads correctly against the raw German card text.
Deterministic-first wave -- this is the one bounded, gated, skippable
network step (D12). Reuses the deepseek() call pattern + .env key loading
from build_corpus_lexicon.py rather than reinventing HTTP retry/backoff.

Stop condition (b), IMPLEMENTATION.md/PLAN.md autonomy contract: on no
backend / network, log "sanity check skipped -- no backend" to .ai_state.md
Dev Notes and continue with the rest of the wave -- never a hard stop.

    python sanity_glyph_resegment.py [--n 50]
"""
import argparse
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pwg_mask  # noqa: E402
import microstructure as ms  # noqa: E402

REPORTS_DIR = os.path.join(HERE, '..', 'reports')
AUDIT_PATH = os.path.join(REPORTS_DIR, 'pwg_sense_glyph_audit.json')

_LOCAL_ENV = os.path.join(HERE, '.env')
_MAIN_TREE_ENV = r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\.env'
ENV_PATH = _LOCAL_ENV if os.path.exists(_LOCAL_ENV) else _MAIN_TREE_ENV

SYS_PROMPT = (
    'You are checking a philological markup-parsing decision, not translating. '
    'You will see a PWG (Bohtlingk-Roth Sanskrit-German dictionary) card body in raw German/Sanskrit '
    'mixed text, and a claimed top-level sense count. Read the card and judge whether that many '
    'distinct numbered senses genuinely appear in the text (the source marks a new sense with a digit, '
    'letter, or Greek letter immediately followed by ")" or the glyph "〉"). '
    'Reply ONLY as JSON: {"agrees": true|false, "your_count": <int>, "note": "<one short sentence>"}.'
)


def load_key():
    if not os.path.exists(ENV_PATH):
        return None
    for line in open(ENV_PATH, encoding='utf-8'):
        if line.strip().startswith('DEEPSEEK_API_KEY='):
            return line.split('=', 1)[1].strip()
    return None


def sample_records(n, seed=1350):
    if not os.path.exists(AUDIT_PATH):
        return []
    with open(AUDIT_PATH, encoding='utf-8') as f:
        audit = json.load(f)
    changed = audit.get('per_record_deltas', [])
    if not changed:
        return []
    rng = random.Random(seed)
    return rng.sample(changed, min(n, len(changed)))


def body_for(record_id):
    """(kept for callers; run() itself now uses ONE streaming pass)"""
    for buf in pwg_mask.records():
        m = pwg_mask.HEADER_RE.match(buf[0])
        if m and m.group(1) == record_id:
            return '\n'.join(buf)
    return None


def collect_bodies(wanted_ids):
    """H4408: ONE streaming pass over pwg_mask.records() collecting bodies only
    for the sampled record ids. The old body_for() restarted the whole-dict
    generator PER record (69MB rescan x N paid calls)."""
    wanted = set(wanted_ids)
    bodies = {}
    for buf in pwg_mask.records():
        m = pwg_mask.HEADER_RE.match(buf[0])
        if m and m.group(1) in wanted:
            bodies[m.group(1)] = '\n'.join(buf)
            if len(bodies) == len(wanted):
                break
    return bodies


CACHE_NAME = 'pwg_glyph_sanity.cache.jsonl'


def cache_path():
    return os.path.join(REPORTS_DIR, CACHE_NAME)


def load_cache(path=None):
    """record_id -> verdict/error row from previous (possibly crashed) runs."""
    path = path or cache_path()
    seen = {}
    if not os.path.exists(path):
        return seen
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue                       # torn tail line from a crash
            rid = row.get('record_id')
            if rid:
                seen[rid] = row
    return seen


class CacheWriter:
    """Append-only JSONL verdict log: fsync per row so a crash at record N
    loses nothing already paid (resume skips every cached record_id)."""

    def __init__(self, path=None):
        os.makedirs(REPORTS_DIR, exist_ok=True)
        self.path = path or cache_path()
        self.fh = open(self.path, 'a', encoding='utf-8')

    def add(self, row):
        self.fh.write(json.dumps(row, ensure_ascii=False) + '\n')
        self.fh.flush()
        os.fsync(self.fh.fileno())

    def close(self):
        self.fh.close()


def run(n, sample=None, post_fn=None):
    """DeepSeek-verify n sampled corrected records; resumable via the JSONL cache.

    `sample`/`post_fn` are injectable for the offline --selftest (no network, no
    audit file, no key needed there).
    """
    post = post_fn
    key = None
    if post is None:
        key = load_key()
        if not key:
            return None, 'no DEEPSEEK_API_KEY found (checked %s and %s)' % (_LOCAL_ENV, _MAIN_TREE_ENV)
        try:
            import requests
        except ImportError:
            return None, 'requests module unavailable'

        def post(user):
            r = requests.post(
                'https://api.deepseek.com/chat/completions',
                headers={'Authorization': 'Bearer ' + key},
                json={'model': 'deepseek-v4-flash', 'temperature': 0,
                      'response_format': {'type': 'json_object'},
                      'messages': [{'role': 'system', 'content': SYS_PROMPT},
                                   {'role': 'user', 'content': user}]},
                timeout=(10, 60))
            r.raise_for_status()
            return json.loads(r.json()['choices'][0]['message']['content'])

    if sample is None:
        sample = sample_records(n)
        if not sample:
            return None, 'no changed records in pwg_sense_glyph_audit.json to sample -- run audit_sense_glyph.py first'

    bodies = collect_bodies(rec['record_id'] for rec in sample)
    cache = load_cache()
    results = []
    writer = CacheWriter()
    try:
        for rec in sample:
            rid = rec['record_id']
            if rid in cache:                    # resume: zero re-paid verdicts
                results.append(cache[rid])
                continue
            buf_text = bodies.get(rid)
            if buf_text is None:
                continue
            user = ('Claimed top-level sense count (corrected splitter): %d\n\nCard:\n%s'
                    % (rec['new_sense_count'], buf_text[:2500]))
            try:
                verdict = post(user)
            except Exception as exc:  # noqa: BLE001 -- classify as a skipped sample, not a hard stop
                row = {'record_id': rid, 'error': str(exc)[:200]}
            else:
                row = {'record_id': rid, 'key1': rec.get('key1'),
                       'claimed_count': rec.get('new_sense_count'), **verdict}
            writer.add(row)                     # durable before the next paid call
            results.append(row)
    finally:
        writer.close()
    return results, None


def _selftest():
    """Offline proof of the H4408 guarantees: ONE records() pass per run, and a
    crash at record N resumes with zero re-paid verdicts (JSONL cache)."""
    import tempfile
    tmp = tempfile.mkdtemp(prefix='glyph_sanity_selftest_')
    old_reports = REPORTS_DIR
    failures = []
    try:
        globals()['REPORTS_DIR'] = tmp

        # hermetic pwg_mask.records() stub (3 tiny cards)
        calls = {'n': 0}
        orig_records = pwg_mask.records

        def fake_records(limit=None):
            calls['n'] += 1
            for rid in ('1', '2', '3'):
                yield ['<L>%s<pc>p<k1>k<k2>k' % rid, 'card %s body' % rid]

        pwg_mask.records = fake_records

        sample = [{'record_id': rid, 'key1': 'k', 'new_sense_count': 2}
                  for rid in ('1', '2', '3')]

        # transport that KILLS the process on the 2nd call (simulated mid-run
        # death -- a KeyboardInterrupt escapes run()'s per-record guard, like a
        # real crash would; the JSONL rows already written must survive)
        state = {'posts': 0}

        def crashing_post(user):
            state['posts'] += 1
            if state['posts'] == 2:
                raise KeyboardInterrupt('simulated mid-run crash')
            return {'agrees': True, 'your_count': 2, 'note': 'ok'}

        try:
            run(3, sample=sample, post_fn=crashing_post)
        except KeyboardInterrupt:
            pass
        if calls['n'] != 1:
            failures.append('run #1 made %d records() passes, want 1' % calls['n'])
        cached = load_cache()
        if len(cached) != 1:            # verdict 1 written + fsynced before the crash
            failures.append('cache after crash: %d rows, want 1' % len(cached))
        if 'agrees' not in cached.get('1', ()):
            failures.append('the pre-crash paid verdict did not survive')

        # resume: cached record 1 must NOT be re-posted; only 2 and 3 are paid
        counting = {'n': 0}

        def counting_post(user):
            counting['n'] += 1
            return {'agrees': True, 'your_count': 2, 'note': 'ok'}

        res, skip = run(3, sample=sample, post_fn=counting_post)
        if skip:
            failures.append('resume run skipped: %s' % skip)
        if counting['n'] != 2:
            failures.append('resume re-posted paid verdicts: %d posts, want exactly 2 (records 2,3)'
                            % counting['n'])
        if calls['n'] != 2:
            failures.append('run #2 made %d total records() passes (want exactly 1 per run)' % calls['n'])
        ok_rows = [r for r in res if 'agrees' in r]
        if [r['record_id'] for r in ok_rows] != ['1', '2', '3']:
            failures.append('resume results wrong: %r' % res)
    finally:
        pwg_mask.records = orig_records
        globals()['REPORTS_DIR'] = old_reports
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    if failures:
        for f in failures:
            print('FAIL:', f, file=sys.stderr)
        sys.exit(1)
    print('glyph sanity selftest: OK (one streaming pass; crash resume = 0 re-paid verdicts)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=50)
    ap.add_argument('--selftest', action='store_true',
                    help='offline resume/one-pass proof (no network, no key)')
    args = ap.parse_args()

    if args.selftest:
        _selftest()
        return

    results, skip_reason = run(args.n)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    out_path = os.path.join(REPORTS_DIR, 'pwg_glyph_sanity.json')

    if skip_reason:
        print('SANITY CHECK SKIPPED: %s' % skip_reason)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg_glyph_sanity/0.1', 'skipped': True, 'reason': skip_reason}, f, indent=1)
        print('wrote %s (skipped)' % out_path)
        sys.exit(0)

    scored = [r for r in results if 'agrees' in r]
    agree = sum(1 for r in scored if r['agrees'])
    print(f'sampled: {len(results)}  scored: {len(scored)}  agree: {agree}')
    rate = (agree / len(scored) * 100) if scored else 0.0
    print(f'agreement rate: {rate:.1f}%')

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'schema': 'pwg_glyph_sanity/0.1', 'skipped': False,
                    'sampled': len(results), 'scored': len(scored), 'agree': agree,
                    'agreement_rate_pct': round(rate, 1), 'results': results},
                   f, ensure_ascii=False, indent=1)
    print(f'wrote {out_path}')


if __name__ == '__main__':
    main()
