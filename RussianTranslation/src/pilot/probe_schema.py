#!/usr/bin/env python
"""Schema-carrying probe builder for pwg_ru Workflow launches (H532).

Why: the H462 load-representative probe is representative in SIZE, not LATENCY.
`probe_log.py prompt` emits a bare German->Russian ask with no CARDS_SCHEMA
StructuredOutput and no CONV_TR system prompt -- but every production card
carries both, and they add most of the per-card latency. On 10-07-2026 a
24.5 s bare probe authorized a launch whose real cards all exceeded 146 s
(9 of 12 at the 180 s KILL_CEIL): the gate passed while production timed out.

This module builds a probe prompt with the REAL production shape by extracting
PREAMBLE + GRAMMAR + CONV_TR + CARDS_SCHEMA live from the launcher
(`run_pilot_wf.h317_w1b.split.js`), so the probe can never drift from what the
launcher actually sends. One synthetic masked band-4-shaped card is appended.

  python src/pilot/probe_schema.py emit --launcher src/pilot/run_pilot_wf.h317_w1b.split.js \
      --out-prompt probe_prompt.txt --out-schema probe_schema.json

The Workflow session then fires ONE agent() call:
  agent(<prompt>, {schema: <schema>, model: 'sonnet', tools: []})
times it, and records the reading with:
  python src/pilot/probe_log.py append --kind warmup --schema-carrying \
      --latency-ms <ms> --conn-errors 0 --payload-bytes <bytes> ...

Gate ceiling (see probe_log.SCHEMA_LATENCY_CEIL_MS): a single schema-carrying
card must complete in < 90 s. Reasoning: production batches 1-6 cards per call
under a 180 s KILL_CEIL; a lone representative card needing >= half the ceiling
leaves no headroom for real batches (latency grows with output size), and the
healthy-day expectation for one card is well under 60 s. 90 s = KILL_CEIL / 2,
a documented safety factor of 2.
"""
import argparse
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LAUNCHER = os.path.join(HERE, 'run_pilot_wf.h317_w1b.split.js')

# One synthetic masked card, shaped like the launcher's cardBlock():
# '=== CARD <key> ===' + masked skeleton + portrait. Deterministic; band-4-ish
# multi-sense density; {Tn} placeholders exactly as the masker emits them.
SYNTH_KEY = 'probe~~h532'
SYNTH_SKELETON = (
    "1. m. {T1} — 1) der Zustand des Wassers, Verfassung, Lage {T2}; auch übertragen von "
    "Verhältnissen des Lebens und der Gesellschaft {T3}. — 2) mit näherer Bestimmung im "
    "Instrumental oder im vorangehenden Compositum: die durch das Bestimmungswort bezeichnete "
    "Lage, der Fall {T4} {T5}. — 3) Mittel, Hilfsmittel, Ausweg {T6}; insbesondere das rechte "
    "Mittel zur Erreichung eines Zweckes {T7}. — 4) Anordnung, Bestimmung, Regel, Gesetz {T8}; "
    "getroffene Übereinkunft, Vertrag {T9} {T10}. — 5) Entschluss, fester Vorsatz {T11}; die "
    "Entschlossenheit als Eigenschaft des Handelnden {T12}. — 6) Zustand der Dinge, Sachlage, "
    "Umstände {T13}; in den Rechtsbüchern: der rechtlich massgebende Zustand {T14} {T15}."
)
SYNTH_PORTRAIT = (
    "band: 4 (long multi-sense nominal; legal + abstract senses)\n"
    "records: 1; senses: 6; masked spans: 15 ({T1}..{T15})\n"
    "sources cited (masked): lexicographic + attested mix; strata: Epic / early-Classical through Medieval"
)


def extract_consts(launcher_path):
    """Pull the live PREAMBLE/GRAMMAR/CONV_TR strings + CARDS_SCHEMA object out of the launcher."""
    src = io.open(launcher_path, encoding='utf-8').read()
    out = {}
    for name in ('PREAMBLE', 'GRAMMAR', 'CONV_TR'):
        m = re.search(r'^const %s = ("(?:[^"\\]|\\.)*")' % name, src, re.M)
        if not m:
            raise SystemExit('cannot extract const %s from %s' % (name, launcher_path))
        # The literal is a JSON-compatible double-quoted string (\uXXXX escapes).
        out[name] = json.loads(m.group(1))
    m = re.search(r'^const CARDS_SCHEMA = (\{.*\})\s*$', src, re.M)
    if not m:
        raise SystemExit('cannot extract const CARDS_SCHEMA from %s' % launcher_path)
    out['CARDS_SCHEMA'] = json.loads(m.group(1))
    return out


def build_prompt(consts):
    card_block = ('\n\n=== CARD ' + SYNTH_KEY + ' ===\n'
                  '--- masked German (translatable only; {Tn}=masked span) ---\n'
                  + SYNTH_SKELETON +
                  '\n--- portrait (evidence) ---\n' + SYNTH_PORTRAIT)
    return consts['PREAMBLE'] + consts['GRAMMAR'] + consts['CONV_TR'] + card_block


def cmd_emit(a):
    consts = extract_consts(a.launcher)
    prompt = build_prompt(consts)
    io.open(a.out_prompt, 'w', encoding='utf-8', newline='\n').write(prompt)
    io.open(a.out_schema, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(consts['CARDS_SCHEMA'], ensure_ascii=False))
    n = len(prompt.encode('utf-8'))
    print('prompt: %s (%d bytes)' % (a.out_prompt, n))
    print('schema: %s' % a.out_schema)
    print('fire ONE agent(prompt, {schema, model: "sonnet", tools: []}), time it, then:', file=sys.stderr)
    print('  python src/pilot/probe_log.py append --kind warmup --schema-carrying '
          '--latency-ms <ms> --conn-errors <n> --payload-bytes %d ...' % n, file=sys.stderr)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('emit', help='write the schema-carrying probe prompt + schema JSON')
    p.add_argument('--launcher', default=DEFAULT_LAUNCHER)
    p.add_argument('--out-prompt', default=os.path.join(HERE, 'probe_schema_prompt.txt'))
    p.add_argument('--out-schema', default=os.path.join(HERE, 'probe_schema_schema.json'))
    p.set_defaults(func=cmd_emit)
    a = ap.parse_args()
    sys.exit(a.func(a))


if __name__ == '__main__':
    main()
