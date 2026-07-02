#!/usr/bin/env python
r"""gen_fidelity_judge_en.py — emit a self-contained Opus EN-fidelity-judge workflow.

The EN analog of gen_fidelity_judge.py. Inlines the EN stratified sample into a Workflow JS so the
script is self-contained (workflow scripts have no filesystem access). Each agent judges a batch of
cards' DE->EN faithfulness and returns the SAME {key, ok, severity, issues, note} verdict schema as
the RU judge (judge_ab_score: BAD = ok=false || severity>=3), so fidelity_aggregate.py consumes the
verdicts unchanged.

Ground truth (FU1 locked decision 6): faithful to the PWG **German** sense. Monier-Williams is a
cross-check only, never the standard. Markup/sigla preservation and PWG sense-order integrity are
HARD sub-checks; divergence from MW is a SOFT note, never a fail.

  python src/fidelity_sample_en.py --n 100             # writes the EN sample
  python src/pilot/gen_fidelity_judge_en.py [--batch 6]  # writes src/pilot/run_fidelity_judge_en.js
  # run run_fidelity_judge_en.js via the Workflow tool (Opus), save result.verdicts; then:
  python src/pilot/fidelity_aggregate.py <verdicts.json> --sample src/pilot/output/fidelity_sample_en.jsonl
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'output')
SAMPLE = os.path.join(OUT, 'fidelity_sample_en.jsonl')
HARNESS = os.path.join(HERE, 'run_fidelity_judge_en.js')
CAP = 600  # cap de/en per sense for judging (gloss meaning is up front; citations are markup)

RUBRIC = (
    "You are a proofreader for an English rendering of the Boehtlingk-Roth Sanskrit-German "
    "dictionary (PWG, Petersburger Woerterbuch). For each card you get a headword (iast) and its "
    "senses; each sense has the German source gloss (de) and a proposed English rendering (en). "
    "Judge whether the English FAITHFULLY renders the German sense.\n\n"
    "GROUND TRUTH: the German source. Monier-Williams or any other dictionary is NOT the standard "
    "here — do NOT flag a rendering merely because it differs from how MW would word it.\n\n"
    "BAD criteria (set ok=false or severity>=3):\n"
    "1. semantic — the English distorts, inverts, or loses the meaning of the German gloss.\n"
    "2. anchors (HARD) — Sanskrit {#..#}, citations <ls>, abbreviations <ab>, sub-glosses "
    "{%..%} were dropped, garbled, or altered.\n"
    "3. order (HARD) — PWG sense order was changed/re-sorted (senses must stay in source order).\n"
    "4. hallucination — the English adds a meaning not present in the German.\n"
    "5. truncation — the English omits sense content (allowance: de/en are capped at CAPCHARS "
    "chars for judging — do NOT penalize a cut at the very end).\n"
    "6. fluency — ungrammatical or non-idiomatic English, or a German calque left untranslated.\n\n"
    "NOT an error (do NOT mark BAD):\n"
    "- preserved German abbreviations (Bed., Schol., vgl., ebend., u. s. w.) — a PWG convention;\n"
    "- preserved Latin euphemisms (inire feminam, legere, seminis profectui) left verbatim;\n"
    "- preserved French/scientific terms and a {%German%} echo kept beside the English;\n"
    "- wording that simply differs from Monier-Williams (cross-check only — a SOFT note at most).\n\n"
    "ISSUE LABELS: tag `issues` using ONLY these words, one label per distinct defect; put "
    "specifics in `note`, not in `issues` (this is the canonical pwg_ru/DharmaMitra crosswalk "
    "vocabulary from FU1_PLAN.md):\n"
    "  addition              — the English adds a meaning/attribution not in the German "
    "(criterion 4 hallucination)\n"
    "  mw-tm-contamination   — the addition is traceable to Monier-Williams wording/detail the "
    "German does not attest — use this INSTEAD OF addition when MW is the traceable source\n"
    "  term-mistranslation   — a specific word/term is wrong, or an ambiguous/polysemous term is "
    "mishandled (criterion 1 semantic)\n"
    "  grammar               — ungrammatical or non-idiomatic English (criterion 6 fluency)\n"
    "  omission              — sense content is dropped (criterion 5 truncation; not the "
    "CAPCHARS length-cap allowance)\n"
    "  register-drift        — tone/register shifts from the source (also criterion 6 fluency)\n"
    "  markup-loss           — a {%..%}/<div> wrapper is dropped while the prose survives "
    "(part of criterion 2 anchors, when meaning is otherwise intact)\n"
    "The `order` criterion (3, PWG sense-order integrity) is its own HARD structural check and "
    "has no single-word class here — describe it in `note` if it fires.\n\n"
    "severity: 0-1 clean, 2 nitpick, 3 real defect, 4-5 gross. Return ONE verdict PER CARD (by its "
    "key): {key, ok(bool), severity(0-5), issues([str]), note(one phrase)}."
).replace('CAPCHARS', str(CAP))

VERDICTS_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["verdicts"],
    "properties": {"verdicts": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["key", "ok", "severity", "issues", "note"],
        "properties": {
            "key": {"type": "string"},
            "ok": {"type": "boolean"},
            "severity": {"type": "integer", "minimum": 0, "maximum": 5},
            "issues": {"type": "array", "items": {"type": "string"}},
            "note": {"type": "string"},
        }}}},
}

TEMPLATE = """// AUTO-DERIVED EN-fidelity-judge workflow (gen_fidelity_judge_en.py). Opus judges DE->EN faithfulness.
export const meta = {
  name: 'pwgen-fidelity-judge',
  description: 'Opus DE->EN fidelity judge over a stratified pwg_en sample (faithful-to-German)',
  phases: [{ title: 'Judge' }],
}
const BATCHES = %(batches)s
const RUBRIC = %(rubric)s
const SCHEMA = %(schema)s
phase('Judge')
const results = await parallel(BATCHES.map((batch, i) => () =>
  agent(RUBRIC + '\\n\\nCARDS (JSON):\\n' + JSON.stringify(batch),
        { label: 'judge-en-' + i, phase: 'Judge', schema: SCHEMA, model: 'opus' })))
const verdicts = results.filter(Boolean).flatMap(r => (r && r.verdicts) || [])
return { verdicts, judged: verdicts.length, batch_count: BATCHES.length }
"""


def trim(card):
    senses = []
    for s in (card.get('senses') or [])[:8]:
        senses.append({'tag': s.get('tag'),
                       'de': (s.get('de') or '')[:CAP],
                       'en': (s.get('en') or '')[:CAP]})
    return {'key': card['key'], 'iast': card.get('iast'), 'stratum': card.get('stratum'),
            'senses': senses}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', type=int, default=6)
    ap.add_argument('--sample', default=SAMPLE)
    ap.add_argument('--out', default=HARNESS)
    args = ap.parse_args()
    cards = [trim(json.loads(l)) for l in open(args.sample, encoding='utf-8') if l.strip()]
    batches = [cards[i:i + args.batch] for i in range(0, len(cards), args.batch)]
    js = TEMPLATE % {
        'batches': json.dumps(batches, ensure_ascii=False),
        'rubric': json.dumps(RUBRIC, ensure_ascii=False),
        'schema': json.dumps(VERDICTS_SCHEMA),
    }
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(js)
    print('wrote %s | %d cards in %d batches of <=%d' % (args.out, len(cards), len(batches), args.batch))


if __name__ == '__main__':
    main()
