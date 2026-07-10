#!/usr/bin/env python
"""Schema-carrying probe builder for pwg_ru Workflow launches (H532; real-card fix 11-07-2026).

Why: the H462 load-representative probe is representative in SIZE, not LATENCY.
`probe_log.py prompt` emits a bare German->Russian ask with no CARDS_SCHEMA
StructuredOutput and no CONV_TR system prompt -- but every production card
carries both, and they add most of the per-card latency. On 10-07-2026 a
24.5 s bare probe authorized a launch whose real cards all exceeded 146 s
(9 of 12 at the 180 s KILL_CEIL): the gate passed while production timed out.

11-07-2026 -- schema-carrying was still not SIZE-representative. The H532 build appended
one SYNTHETIC ~900 B skeleton card; it measured 45.9 s (GO, < 90 s) and STILL
under-predicted -- run wf_5a3baf30-e44 came back 0/12 clean, every real card at
2.5-8.9 KB hitting the 180 s KILL_CEIL. A hand-written synthetic card is not a
real band-4 card. So the probe now uses the launcher's OWN largest real masked
card (`INPUTS[k].skeleton` + `.portrait`, chosen by max skeleton length, the same
quantity `skelBytesOfKeys` bounds the kill budget on), built with the exact
`cardBlock()` shape. The probe can no longer be smaller than the heaviest card
the window will actually send.

This module builds a probe prompt with the REAL production shape by extracting
PREAMBLE + GRAMMAR + CONV_TR + CARDS_SCHEMA + INPUTS live from the launcher
(`run_pilot_wf.h317_w1b.split.js`), so the probe can never drift from what the
launcher actually sends.

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
a documented safety factor of 2. Using the LARGEST real card makes this a
worst-case single-card reading -- exactly the card most likely to trip the ceiling.
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


def extract_consts(launcher_path):
    """Pull the live PREAMBLE/GRAMMAR/CONV_TR strings + CARDS_SCHEMA + INPUTS out of the launcher."""
    src = io.open(launcher_path, encoding='utf-8').read()
    out = {}
    for name in ('PREAMBLE', 'GRAMMAR', 'CONV_TR'):
        m = re.search(r'^const %s = ("(?:[^"\\]|\\.)*")' % name, src, re.M)
        if not m:
            raise SystemExit('cannot extract const %s from %s' % (name, launcher_path))
        # The literal is a JSON-compatible double-quoted string (\uXXXX escapes).
        out[name] = json.loads(m.group(1))
    for name in ('CARDS_SCHEMA', 'INPUTS'):
        m = re.search(r'^const %s = (\{.*\})\s*$' % name, src, re.M)
        if not m:
            raise SystemExit('cannot extract const %s from %s' % (name, launcher_path))
        out[name] = json.loads(m.group(1))
    # 11-07-2026: the probe replicates cardBlock() but omits GRAMMARS[k] and suggestionBlock(k).
    # Those are empty for a nominal / no-suggest-TM window; warn if this launcher isn't.
    for name in ('GRAMMARS', 'SUGGEST_TM'):
        m = re.search(r'^const %s = (\{.*?\})\s*$' % name, src, re.M)
        if m:
            try:
                obj = json.loads(m.group(1))
            except ValueError:
                obj = None
            if obj:
                print('WARN: launcher %s is non-empty; the probe omits its contribution '
                      'to cardBlock() and may under-represent.' % name, file=sys.stderr)
    return out


def pick_card(inputs, key=None):
    """Choose the representative card: an explicit --key, else the largest skeleton
    (max INPUTS[k].skeleton length -- the exact quantity skelBytesOfKeys sums for the
    kill budget, so the largest card is the worst case for the 180 s KILL_CEIL)."""
    if key is not None:
        if key not in inputs:
            raise SystemExit('key %r not in launcher INPUTS (%d keys)' % (key, len(inputs)))
        return key
    return max(inputs, key=lambda k: len(inputs[k].get('skeleton', '')))


def build_prompt(consts, key):
    """Replicate the launcher's cardBlock(key) exactly (GRAMMARS[k]/suggestionBlock empty
    in this window), then PREAMBLE + GRAMMAR + CONV_TR + that block -- the singleton-batch
    production prompt for the heaviest real card."""
    inp = consts['INPUTS'][key]
    card_block = ('\n\n=== CARD ' + key + ' ===\n'
                  '--- masked German (translatable only; {Tn}=masked span) ---\n'
                  + inp['skeleton'] +
                  '\n--- portrait (evidence) ---\n' + inp['portrait'])
    return consts['PREAMBLE'] + consts['GRAMMAR'] + consts['CONV_TR'] + card_block


def cmd_emit(a):
    consts = extract_consts(a.launcher)
    key = pick_card(consts['INPUTS'], a.key)
    skel = len(consts['INPUTS'][key]['skeleton'])
    prompt = build_prompt(consts, key)
    io.open(a.out_prompt, 'w', encoding='utf-8', newline='\n').write(prompt)
    io.open(a.out_schema, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(consts['CARDS_SCHEMA'], ensure_ascii=False))
    n = len(prompt.encode('utf-8'))
    print('card:   %s (skeleton %d chars -- the largest real card in this window)' % (key, skel))
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
    p.add_argument('--key', help='use this INPUTS key instead of the largest skeleton')
    p.add_argument('--out-prompt', default=os.path.join(HERE, 'probe_schema_prompt.txt'))
    p.add_argument('--out-schema', default=os.path.join(HERE, 'probe_schema_schema.json'))
    p.set_defaults(func=cmd_emit)
    a = ap.parse_args()
    sys.exit(a.func(a))


if __name__ == '__main__':
    main()
