#!/usr/bin/env python
r"""rv_wordlevel_gold_labels.py -- the adjudicated verdicts for the layer-B gold sample.

Annotator: **Opus 5 (`claude-opus-5[1m]`)**, 29-07-2026, H1844 step 11. A model annotator
is permitted here by the precedent already in `gold/` (`saru_gloss_labels_opus.jsonl` /
`_sonnet.jsonl` / `_haiku.jsonl`), on the condition followed here: the annotator is NAMED
with tier and exact version, and the verdicts are committed as data so a human can audit
or overturn any one of them.

Each verdict answers exactly one question, per
[`gold/HUMAN_GOLD_PROTOCOL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md):
*is the proposed span the rendering of that Sanskrit token in that translation?*

Judging convention, stated so it can be checked:
  * `correct`   -- the span is the word (or the head word of the phrase) that renders the
                   token. A single word drawn from a multi-word rendering counts, since the
                   aligner emits single-word spans by construction (`ágnīṣomā` -> `Агни`).
                   A preverb rendered inside the verb counts (`ā́` -> `привезут`).
  * `incorrect` -- the span renders a DIFFERENT token of the same stanza. This is the
                   dominant failure and it is not a near miss: the aligner repeatedly
                   returns the stanza's salient proper noun (Agni, Soma, Nāsatya, Pajra,
                   Brahmaṇaspati) whatever the source token was.

Only rows the annotator actually read are listed. `score` reports n honestly; unlabelled
rows stay `verdict: null` and are excluded rather than assumed.

  python src/rv_wordlevel_gold_labels.py apply
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
GOLD_DIR = os.path.normpath(os.path.join(HERE, '..', 'gold'))
GOLD_PATH = os.path.join(GOLD_DIR, 'rv_wordlevel_gold.jsonl')

ANNOTATOR = 'Opus 5 (claude-opus-5[1m])'

E = 'elizarenkova_ru_1989'
G = 'geldner_de_1951'
R = 'grassmann_de_1876'
F = 'griffith_en_1896'

# (location, translator, form, verdict)
VERDICTS = [
    ('1.10.9', E, 'ā́śrutkarṇa', 'incorrect'),
    ('1.14.7', G, 'pátnīvataḥ', 'correct'),
    ('1.14.7', F, 'sujihva', 'incorrect'),
    ('1.22.20', F, 'diví', 'incorrect'),
    ('1.23.5', F, 'jyótiṣaḥ', 'incorrect'),
    ('1.39.3', G, 'gurú', 'incorrect'),
    ('1.39.3', R, 'vanínaḥ', 'correct'),
    ('1.39.3', R, 'ā́śāḥ', 'incorrect'),
    ('1.43.3', R, 'yáthā', 'correct'),
    ('1.52.5', F, 'sasruḥ', 'incorrect'),
    ('1.72.2', E, 'sántam', 'incorrect'),
    ('1.72.2', E, 'śramayúvaḥ', 'correct'),
    ('1.72.2', E, 'padavyàḥ', 'incorrect'),
    ('1.72.2', G, 'cā́ru', 'incorrect'),
    ('1.72.2', R, 'śramayúvaḥ', 'correct'),
    ('1.72.2', R, 'cā́ru', 'incorrect'),
    ('1.72.2', F, 'agnéḥ', 'correct'),
    ('1.84.10', E, 'vásvīḥ', 'incorrect'),
    ('1.84.10', F, 'viṣūvátaḥ', 'incorrect'),
    ('1.84.10', F, 'sayā́varīḥ', 'incorrect'),
    ('1.93.3', E, 'ágnīṣomā', 'correct'),
    ('1.96.3', G, 'víśaḥ', 'incorrect'),
    ('1.101.10', E, 'ā́', 'correct'),
    ('1.116.11', E, 'vām', 'incorrect'),
    ('1.116.11', E, 'rā́dhyam', 'incorrect'),
    ('1.116.11', E, 'abhiṣṭimát', 'incorrect'),
    ('1.116.11', E, 'ápagūḷham', 'incorrect'),
    ('1.116.11', G, 'abhiṣṭimát', 'incorrect'),
    ('1.116.11', G, 'darśatā́t', 'incorrect'),
    ('1.117.13', E, 'sahá', 'incorrect'),
    ('1.126.4', E, 'śóṇāḥ', 'incorrect'),
    ('1.126.4', E, 'madacyútaḥ', 'incorrect'),
    ('1.126.4', E, 'kakṣī́vantaḥ', 'correct'),
    ('1.126.4', R, 'śréṇim', 'incorrect'),
    ('1.126.4', F, 'kr̥śanā́vataḥ', 'incorrect'),

    ('5.52.7', G, 'nadī́nām', 'incorrect'),
    ('5.52.7', F, 'pā́rthivāḥ', 'incorrect'),
    ('5.64.7', E, 'dhāvatam', 'incorrect'),
    ('5.64.7', G, 'rúśadgavi', 'correct'),
    ('5.64.7', G, 'ā́', 'incorrect'),
    ('5.64.7', R, 'devákṣatre', 'incorrect'),
    ('5.64.7', F, 'devákṣatre', 'incorrect'),
    ('5.64.7', F, 'ā́', 'incorrect'),
    ('5.64.7', F, 'dhāvatam', 'incorrect'),
    ('5.64.7', F, 'bíbhratau', 'incorrect'),
    ('5.64.7', F, 'arcanā́nasam', 'incorrect'),
    ('5.86.1', E, 'vā́ṇīḥ', 'incorrect'),
    ('6.7.3', G, 'vājī́', 'incorrect'),
    ('6.18.7', E, 'sámokāḥ', 'incorrect'),
    ('6.18.7', G, 'sá', 'correct'),
    ('6.24.1', E, 'r̥jīṣī́', 'incorrect'),
    ('6.24.1', E, 'arcatryàḥ', 'incorrect'),
    ('6.39.4', E, 'arúcaḥ', 'incorrect'),
    ('6.39.4', E, 'r̥tayúgbhiḥ', 'correct'),
    ('6.39.4', R, 'arúcaḥ', 'incorrect'),
    ('6.39.4', F, 'arúcaḥ', 'incorrect'),
    ('6.39.4', F, 'ayám', 'correct'),
    ('6.47.6', F, 'kaláśe', 'incorrect'),
    ('6.47.6', F, 'samaré', 'incorrect'),
    ('6.47.11', R, 'puruhūtám', 'incorrect'),
    ('6.50.8', E, 'dátravān', 'incorrect'),
    ('6.50.8', G, 'yajatáḥ', 'correct'),
    ('6.50.8', G, 'dátravān', 'incorrect'),
    ('6.50.8', F, 'dátravān', 'incorrect'),
    ('6.68.6', E, 'bhanákti', 'incorrect'),
    ('6.68.6', R, 'áśastīḥ', 'incorrect'),
    ('6.75.17', E, 'bāṇā́ḥ', 'incorrect'),
    ('6.75.17', E, 'viśikhā́ḥ', 'incorrect'),
    ('6.75.17', G, 'bāṇā́ḥ', 'incorrect'),
]


def apply_labels(path=GOLD_PATH):
    index = {(loc, tr, form): verdict for loc, tr, form, verdict in VERDICTS}
    rows, applied, unmatched = [], 0, set(index)
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            key = (rec['location'], rec['translator'], rec['form'])
            if key in index:
                rec['verdict'] = index[key]
                rec['annotator'] = ANNOTATOR
                applied += 1
                unmatched.discard(key)
            rows.append(rec)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        for rec in rows:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    return applied, sorted(unmatched), len(rows)


def main():
    ap = argparse.ArgumentParser(description='apply layer-B gold verdicts (H1844 step 11)')
    ap.add_argument('cmd', choices=['apply'], nargs='?', default='apply')
    ap.parse_args()
    applied, unmatched, total = apply_labels()
    print('gold labels: %d of %d declared verdicts applied to %d rows'
          % (applied, len(VERDICTS), total))
    if unmatched:
        print('  UNMATCHED (key not found in the gold file) -- these are a bug, not a result:')
        for k in unmatched:
            print('    %s' % (k,))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
