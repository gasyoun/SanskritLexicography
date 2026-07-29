#!/usr/bin/env python
r"""rv_wordlevel_gold.py -- the 300-token layer-B gold sample and its precision report
(H1844 step 11, deliverable W1.9 / ruling R14).

R14 sets the bar: precision >= 85 % scored SEPARATELY per target language (ru / de / en),
on a 300-token sample stratified by corpus frequency. Below the bar on one or two
languages, those ship flagged `low_confidence` and are excluded from the contradiction
gate; below on all three, that is stop condition 3 -- ship spine A alone and report.

Protocol: [`gold/HUMAN_GOLD_PROTOCOL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md).
Annotator provenance is recorded per row, following the precedent already in `gold/`
(`saru_gloss_labels_opus.jsonl` / `_sonnet.jsonl` / `_haiku.jsonl`): a model annotator is
allowed here, but it is NAMED with tier and exact version, never left implicit.

Frequency stratification uses the lemma's own `occurrence_count` from
`rv_lemma_occurrences.jsonl` -- the corpus frequency is already carried on the spine, so
no frequency table is rebuilt (ARCHITECTURE Sec.1: the anchors are already on the tokens).

  python src/rv_wordlevel_gold.py sample --arm mbert --arm-file pwg_ru/h1844/wordlevel.mbert.jsonl
  python src/rv_wordlevel_gold.py sheet  --gold gold/rv_wordlevel_gold.jsonl
  python src/rv_wordlevel_gold.py score  --gold gold/rv_wordlevel_gold.jsonl
  python src/rv_wordlevel_gold.py selftest
"""
import argparse
import collections
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.normpath(os.path.join(HERE, '..'))
PWG_RU_DIR = os.path.join(RT_ROOT, 'pwg_ru')
GOLD_DIR = os.path.join(RT_ROOT, 'gold')

STANZA_PATH = os.path.join(PWG_RU_DIR, 'rv_stanza_translations.jsonl')
LEMMA_PATH = os.path.join(PWG_RU_DIR, 'rv_lemma_occurrences.jsonl')
GOLD_OUT = os.path.join(GOLD_DIR, 'rv_wordlevel_gold.jsonl')
SHEET_OUT = os.path.join(GOLD_DIR, 'rv_wordlevel_gold_adjudication.md')
REPORT_OUT = os.path.join(GOLD_DIR, 'rv_wordlevel_precision_report.md')

TARGETS = ['de', 'ru', 'en']
PRECISION_BAR = 0.85
DEFAULT_N = 300
DEFAULT_SEED = 1844

# Frequency strata over the lemma's RV occurrence_count. Stratifying by frequency is R14's
# requirement; these cuts are the standard hapax / rare / mid / frequent split.
STRATA = [('hapax', 1, 1), ('rare', 2, 9), ('mid', 10, 99), ('frequent', 100, 10 ** 9)]


def stratum_of(count):
    for name, lo, hi in STRATA:
        if lo <= count <= hi:
            return name
    return STRATA[-1][0]


def load_lemma_frequency():
    """lemma -> occurrence_count, straight off the spine."""
    freq = {}
    with open(LEMMA_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                freq[rec['lemma']] = rec['occurrence_count']
    return freq


def load_arm(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def draw(rows, freq, n, seed):
    """n rows, balanced across the three target languages and stratified by corpus
    frequency inside each language."""
    per_target = n // len(TARGETS)
    rng = random.Random(seed)
    picked = []
    for target in TARGETS:
        pool = [r for r in rows if r['target'] == target]
        buckets = collections.defaultdict(list)
        for r in pool:
            buckets[stratum_of(freq.get(r['lemma'], 0))].append(r)
        present = [s for s, _, _ in STRATA if buckets[s]]
        if not present:
            continue
        base, extra = divmod(per_target, len(present))
        for i, s in enumerate(present):
            k = min(base + (1 if i < extra else 0), len(buckets[s]))
            chosen = rng.sample(buckets[s], k)
            for r in chosen:
                picked.append({**r, 'frequency_stratum': s,
                               'lemma_occurrence_count': freq.get(r['lemma'], 0)})
    picked.sort(key=lambda r: ([int(x) for x in r['location'].split('.')],
                               r['token_index'], r['translator']))
    return picked


def cmd_sample(a):
    freq = load_lemma_frequency()
    rows = load_arm(a.arm_file)
    picked = draw(rows, freq, a.n, a.seed)
    os.makedirs(GOLD_DIR, exist_ok=True)
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        for r in picked:
            f.write(json.dumps({
                'location': r['location'], 'token_index': r['token_index'],
                'form': r['form'], 'lemma': r['lemma'],
                'translator': r['translator'], 'target': r['target'],
                'span': r['span'], 'confidence': r['confidence'],
                'low_confidence': r['low_confidence'],
                'frequency_stratum': r['frequency_stratum'],
                'lemma_occurrence_count': r['lemma_occurrence_count'],
                'arm': a.arm, 'aligner_model': r.get('aligner_model'),
                'verdict': None, 'annotator': None,
            }, ensure_ascii=False) + '\n')
    by_target = collections.Counter(r['target'] for r in picked)
    by_stratum = collections.Counter(r['frequency_stratum'] for r in picked)
    print('gold sample: %d rows -> %s' % (len(picked), a.out))
    print('  by target : %s' % dict(by_target))
    print('  by stratum: %s' % dict(by_stratum))
    return 0


def cmd_sheet(a):
    """Compact adjudication sheet: the stanza is printed ONCE, then each token->span
    proposal under it, so an annotator reads each context a single time."""
    gold = load_arm(a.gold)
    stanzas = {}
    with open(STANZA_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                stanzas[rec['location']] = rec
    by_loc = collections.defaultdict(list)
    for r in gold:
        by_loc[(r['location'], r['translator'])].append(r)

    lines = ['# Layer-B word-level gold — adjudication sheet', '',
             '_Created: 29-07-2026 · Last updated: 29-07-2026_', '',
             'One block per (stanza × translator). Judge each `form → span` proposal: is that '
             'span the rendering of that Sanskrit token in this translation?', '']
    for (loc, translator), items in sorted(
            by_loc.items(), key=lambda kv: ([int(x) for x in kv[0][0].split('.')], kv[0][1])):
        text = (stanzas[loc]['translations'][translator]['text'] or '').replace('\n', ' / ')
        lines.append('## %s · %s' % (loc, translator))
        lines.append('')
        lines.append('> %s' % text)
        lines.append('')
        for r in sorted(items, key=lambda r: r['token_index']):
            lines.append('- `%s` (%s, freq %d) → **%s**  _conf %.3f%s_'
                         % (r['form'], r['lemma'], r['lemma_occurrence_count'], r['span'],
                            r['confidence'], ', low_confidence' if r['low_confidence'] else ''))
        lines.append('')
    os.makedirs(GOLD_DIR, exist_ok=True)
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print('adjudication sheet: %d blocks, %d proposals -> %s'
          % (len(by_loc), len(gold), a.out))
    return 0


def cmd_score(a):
    gold = load_arm(a.gold)
    labelled = [r for r in gold if r['verdict'] in ('correct', 'incorrect')]
    if not labelled:
        sys.exit('no adjudicated rows in %s -- fill `verdict` with correct/incorrect first'
                 % a.gold)

    per_target = {}
    for target in TARGETS:
        rows = [r for r in labelled if r['target'] == target]
        if not rows:
            continue
        ok = sum(1 for r in rows if r['verdict'] == 'correct')
        per_target[target] = {'n': len(rows), 'correct': ok, 'precision': ok / len(rows)}

    by_stratum = {}
    for s, _, _ in STRATA:
        rows = [r for r in labelled if r['frequency_stratum'] == s]
        if rows:
            ok = sum(1 for r in rows if r['verdict'] == 'correct')
            by_stratum[s] = {'n': len(rows), 'precision': ok / len(rows)}

    mutual = [r for r in labelled if not r['low_confidence']]
    flagged = [r for r in labelled if r['low_confidence']]

    passed = [t for t, v in per_target.items() if v['precision'] >= PRECISION_BAR]
    failed = [t for t, v in per_target.items() if v['precision'] < PRECISION_BAR]

    print('layer-B precision (bar %.0f%% per language, R14)' % (PRECISION_BAR * 100))
    for t in TARGETS:
        v = per_target.get(t)
        if v:
            print('  %-3s n=%3d  correct=%3d  precision=%.1f%%  %s'
                  % (t, v['n'], v['correct'], 100 * v['precision'],
                     'PASS' if v['precision'] >= PRECISION_BAR else 'FAIL'))
    print('  languages passing: %s ; failing: %s' % (passed or 'none', failed or 'none'))
    if not passed:
        print('  -> STOP CONDITION 3 (all three below the bar): ship spine A alone, mark '
              'layer B low_confidence, report. Do not tune blind.')

    _write_report(a, per_target, by_stratum, mutual, flagged, passed, failed, len(gold))
    print('  -> %s' % a.out)
    return 0


def _write_report(a, per_target, by_stratum, mutual, flagged, passed, failed, n_total):
    def prec(rows):
        if not rows:
            return float('nan')
        return sum(1 for r in rows if r['verdict'] == 'correct') / len(rows)

    lines = []
    lines.append('# Layer-B word-level precision report (H1844 step 11, W1.9 / R14)')
    lines.append('')
    lines.append('_Created: 29-07-2026 · Last updated: 29-07-2026_')
    lines.append('')
    lines.append('Bar: **precision ≥ %.0f %% per target language** on a frequency-stratified '
                 'token sample (R14). Scored over the adjudicated rows of '
                 '[`gold/rv_wordlevel_gold.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/rv_wordlevel_gold.jsonl).'
                 % (PRECISION_BAR * 100))
    lines.append('')
    lines.append('| Target language | n | Correct | Precision | Verdict |')
    lines.append('|---|--:|--:|--:|---|')
    for t in TARGETS:
        v = per_target.get(t)
        if v:
            lines.append('| %s | %d | %d | %.1f %% | %s |'
                         % (t, v['n'], v['correct'], 100 * v['precision'],
                            'PASS' if v['precision'] >= PRECISION_BAR else '**FAIL**'))
    lines.append('')
    lines.append('| Frequency stratum | n | Precision |')
    lines.append('|---|--:|--:|')
    for s, v in by_stratum.items():
        lines.append('| %s | %d | %.1f %% |' % (s, v['n'], 100 * v['precision']))
    lines.append('')
    lines.append('| Confidence signal | n | Precision |')
    lines.append('|---|--:|--:|')
    lines.append('| mutual-argmax confirmed | %d | %.1f %% |' % (len(mutual), 100 * prec(mutual)))
    lines.append('| flagged `low_confidence` | %d | %.1f %% |' % (len(flagged), 100 * prec(flagged)))
    lines.append('')
    lines.append('## Verdict')
    lines.append('')
    if not passed:
        lines.append('**All three languages fall below the %.0f %% bar — stop condition 3.** '
                     'Per PLAN §4 the response is fixed in advance and is not a judgment call '
                     'made after seeing the number: ship spine A alone, mark layer B '
                     '`low_confidence`, exclude it from the contradiction gate, and report. '
                     'The 0.20 confidence gate is NOT re-tuned to rescue the number — that is '
                     'the blind tuning R14 and risk K2 exist to forbid.' % (PRECISION_BAR * 100))
    elif failed:
        lines.append('Languages **%s** clear the bar and ship normally. Languages **%s** fall '
                     'below it and ship flagged `low_confidence`, excluded from the '
                     'contradiction gate (R14 marked default).'
                     % (', '.join(passed), ', '.join(failed)))
    else:
        lines.append('All languages clear the %.0f %% bar; layer B ships unflagged.'
                     % (PRECISION_BAR * 100))
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    lines.append('')
    os.makedirs(GOLD_DIR, exist_ok=True)
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))


def selftest():
    assert stratum_of(1) == 'hapax'
    assert stratum_of(2) == 'rare' and stratum_of(9) == 'rare'
    assert stratum_of(10) == 'mid' and stratum_of(99) == 'mid'
    assert stratum_of(100) == 'frequent' and stratum_of(99999) == 'frequent'

    rows = []
    for i in range(400):
        rows.append({'location': '1.1.%d' % (i + 1), 'token_index': i % 5,
                     'form': 'f%d' % i, 'lemma': 'l%d' % i,
                     'translator': 'griffith_en_1896' if i % 3 == 2 else (
                         'elizarenkova_ru_1989' if i % 3 == 1 else 'grassmann_de_1876'),
                     'target': TARGETS[i % 3], 'span': 's%d' % i,
                     'confidence': 0.5, 'low_confidence': False})
    freq = {'l%d' % i: (1 if i % 4 == 0 else (5 if i % 4 == 1 else (50 if i % 4 == 2 else 500)))
            for i in range(400)}
    got = draw(rows, freq, 300, DEFAULT_SEED)
    assert len(got) == 300, len(got)
    per_t = collections.Counter(r['target'] for r in got)
    assert set(per_t) == set(TARGETS) and all(v == 100 for v in per_t.values()), per_t
    strata = collections.Counter(r['frequency_stratum'] for r in got)
    assert len(strata) == 4, strata          # every stratum represented
    again = draw(rows, freq, 300, DEFAULT_SEED)
    assert [r['form'] for r in got] == [r['form'] for r in again], 'seed must be stable'
    other = draw(rows, freq, 300, DEFAULT_SEED + 1)
    assert [r['form'] for r in got] != [r['form'] for r in other], 'seed must matter'

    print('rv_wordlevel_gold selftest OK -- frequency strata, language-balanced '
          'frequency-stratified draw, seed stability')
    return 0


def main():
    ap = argparse.ArgumentParser(description='Layer-B gold sample + precision (H1844 step 11)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    sa = sub.add_parser('sample', help='draw the frequency-stratified gold sample')
    sa.add_argument('--arm', required=True)
    sa.add_argument('--arm-file', required=True)
    sa.add_argument('--n', type=int, default=DEFAULT_N)
    sa.add_argument('--seed', type=int, default=DEFAULT_SEED)
    sa.add_argument('--out', default=GOLD_OUT)

    sh = sub.add_parser('sheet', help='render the compact adjudication sheet')
    sh.add_argument('--gold', default=GOLD_OUT)
    sh.add_argument('--out', default=SHEET_OUT)

    sc = sub.add_parser('score', help='per-language precision against the R14 bar')
    sc.add_argument('--gold', default=GOLD_OUT)
    sc.add_argument('--out', default=REPORT_OUT)

    sub.add_parser('selftest')

    a = ap.parse_args()
    return {'sample': cmd_sample, 'sheet': cmd_sheet, 'score': cmd_score}.get(
        a.cmd, lambda _a: selftest())(a)


if __name__ == '__main__':
    sys.exit(main())
