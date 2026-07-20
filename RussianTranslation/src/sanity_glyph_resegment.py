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
    for buf in pwg_mask.records():
        m = pwg_mask.HEADER_RE.match(buf[0])
        if m and m.group(1) == record_id:
            return '\n'.join(buf)
    return None


def run(n):
    key = load_key()
    if not key:
        return None, 'no DEEPSEEK_API_KEY found (checked %s and %s)' % (_LOCAL_ENV, _MAIN_TREE_ENV)

    try:
        import requests
    except ImportError:
        return None, 'requests module unavailable'

    sample = sample_records(n)
    if not sample:
        return None, 'no changed records in pwg_sense_glyph_audit.json to sample -- run audit_sense_glyph.py first'

    results = []
    for rec in sample:
        buf_text = body_for(rec['record_id'])
        if buf_text is None:
            continue
        user = ('Claimed top-level sense count (corrected splitter): %d\n\nCard:\n%s'
                % (rec['new_sense_count'], buf_text[:2500]))
        try:
            r = requests.post(
                'https://api.deepseek.com/chat/completions',
                headers={'Authorization': 'Bearer ' + key},
                json={'model': 'deepseek-chat', 'temperature': 0,
                      'response_format': {'type': 'json_object'},
                      'messages': [{'role': 'system', 'content': SYS_PROMPT},
                                   {'role': 'user', 'content': user}]},
                timeout=(10, 60))
            r.raise_for_status()
            content = r.json()['choices'][0]['message']['content']
            verdict = json.loads(content)
        except Exception as exc:  # noqa: BLE001 -- classify as a skipped sample, not a hard stop
            results.append({'record_id': rec['record_id'], 'error': str(exc)[:200]})
            continue
        results.append({'record_id': rec['record_id'], 'key1': rec['key1'],
                         'claimed_count': rec['new_sense_count'], **verdict})
    return results, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=50)
    args = ap.parse_args()

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
