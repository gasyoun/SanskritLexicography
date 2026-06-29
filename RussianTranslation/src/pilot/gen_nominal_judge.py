#!/usr/bin/env python
"""Generate the blind pairwise A/B judge workflow for the nominal grammar A/B test.

Embeds the blinded judge input (rendering_1 vs rendering_2 per card, A/B identity
hidden) into a standalone workflow script. Each card → one Opus judge that picks
the better Russian rendering on {correctness, completeness, register, grammar-note
quality}, blind to which arm is which. Un-blind + tally happens in Python after.

  python src/pilot/gen_nominal_judge.py   ->  src/pilot/run_nominal_judge.js
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
JUDGE_IN = os.path.join(HERE, 'output', 'nominal_judge_input.json')
OUT = os.path.join(HERE, 'run_nominal_judge.js')

VERDICT_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'required': ['key', 'winner', 'correctness', 'completeness', 'register',
                 'grammar_notes', 'reason'],
    'properties': {
        'key': {'type': 'string'},
        'winner': {'enum': ['1', '2', 'tie']},
        'correctness': {'enum': ['1', '2', 'tie']},
        'completeness': {'enum': ['1', '2', 'tie']},
        'register': {'enum': ['1', '2', 'tie']},
        'grammar_notes': {'enum': ['1', '2', 'tie']},
        'reason': {'type': 'string'},
    },
}

PROMPT = """You are a blind expert judge of German→Russian lexicographic translation for a
Sanskrit dictionary (Petersburg Dictionary → Russian). You are shown ONE headword's German
source and TWO independent Russian renderings, labelled 1 and 2. You do NOT know how either
was produced. Decide which rendering is better, dimension by dimension. A grammatical note
(declension class, compound analysis like bahuvrīhi/tatpuruṣa, stem type) only counts in
favour of a rendering if it is CORRECT and RELEVANT — a wrong or irrelevant grammar note
counts AGAINST it. Sanskrit in {#..#}, sigla <ls>, and {%..%} German glosses must be kept
verbatim in both; do not penalise either for keeping them.

Return strict JSON for the schema. winner/correctness/completeness/register/grammar_notes
each ∈ {"1","2","tie"}. `reason`: one or two sentences, concrete.

=== HEADWORD: @@IAST@@ (@@KEY@@) ===

--- GERMAN SOURCE (per sense) ---
@@GERMAN@@

--- RENDERING 1 (Russian) ---
@@R1@@
--- RENDERING 1 grammatical/differentia notes ---
@@N1@@

--- RENDERING 2 (Russian) ---
@@R2@@
--- RENDERING 2 grammatical/differentia notes ---
@@N2@@
"""


def main():
    cards = json.load(open(JUDGE_IN, encoding='utf-8'))
    prompts = []
    for c in cards:
        p = PROMPT
        for tok, val in (('@@IAST@@', c['iast']), ('@@KEY@@', c['key']),
                         ('@@GERMAN@@', c['german_source']),
                         ('@@R1@@', c['rendering_1']), ('@@N1@@', c['notes_1']),
                         ('@@R2@@', c['rendering_2']), ('@@N2@@', c['notes_2'])):
            p = p.replace(tok, val)
        prompts.append({'key': c['key'], 'prompt': p})
    js = """// AUTO-GENERATED blind pairwise A/B judge for the nominal grammar A/B test.
export const meta = {
  name: 'nominal-grammar-ab-judge',
  description: 'blind pairwise Opus judge: nominal grammar layer ON vs OFF, 8 PWG headwords',
  phases: [{ title: 'Judge', detail: 'one Opus judge per card, blind to arm identity' }],
}

const VERDICT_SCHEMA = %(schema)s
const CARDS = %(cards)s

phase('Judge')
const verdicts = await parallel(CARDS.map((c, i) => () =>
  agent(c.prompt, { label: 'judge:' + c.key, phase: 'Judge', schema: VERDICT_SCHEMA, model: 'opus', tools: [] })
    .then(v => (v ? { ...v, key: c.key } : { key: c.key, winner: 'tie', error: true }))
))
return { verdicts }
""" % {
        'schema': json.dumps(VERDICT_SCHEMA, ensure_ascii=True),
        'cards': json.dumps(prompts, ensure_ascii=True),
    }
    open(OUT, 'w', encoding='utf-8').write(js)
    print('wrote', OUT, len(js), 'bytes |', len(prompts), 'judge cards')


if __name__ == '__main__':
    main()
