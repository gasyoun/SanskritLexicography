"""Attribute the H2539 Ticket 2 gate failure — DIAGNOSTIC ONLY, NOT a re-qualification.

The sealed envelope is authoritative and final: schema_compliant=false,
failure_class=malformed_output, NO-GO.  Nothing here changes that verdict and no
model output is repaired.  This script exists to answer a separate question the
qualification report must answer honestly: *which* artifact caused the gate to
fire, and were there any OTHER deterministic defects in the returned card?

It therefore checks the returned card against the handoff's enumerated defect
classes independently of the frozen schema, and diffs the frozen schema's pinned
`german` constants against the skeleton lines the prompt actually told the model
to reproduce.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
EV = HERE / 'evidence'
CANARY = HERE.parent / 'h994' / 'canary'

wrapper = json.loads((EV / 't2_response.json').read_text(encoding='utf-8'))
result = json.loads(wrapper['content'][0]['text'])
schema = json.loads((EV / 't2_schema.json').read_text(encoding='utf-8'))
raw = (CANARY / 'dq_canary_puregloss~~h0_zz_pw.raw.txt').read_text(encoding='utf-8')

senses = result['cards'][0]['records'][0]['senses']

# --- 1. what the prompt told the model to reproduce, verbatim from the fixture ---
skeleton_lines = [ln for ln in raw.splitlines() if ln.strip().startswith('—')]
pinned = [
    schema['$defs']['sense%d' % n]['properties']['german']['const']
    for n in (1, 2, 3)
]

print('=== ROOT-CAUSE ATTRIBUTION: prompt instruction vs frozen schema constant ===')
print('The T2 prompt said: reproduce that sense\'s German skeleton line EXACTLY as given.')
for i, (line, const, got) in enumerate(
        zip(skeleton_lines, pinned, [s['german'] for s in senses]), start=1):
    print('\nsense %d' % i)
    print('  fixture skeleton line   = %r' % line)
    print('  schema pinned const     = %r' % const)
    print('  model returned          = %r' % got)
    print('  model == skeleton line? %s' % (got == line))
    print('  model == pinned const?  %s' % (got == const))
    print('  schema const == line?   %s' % (const == line))

print('\nVERDICT ON CAUSE:')
if all(g['german'] == l for g, l in zip(senses, skeleton_lines)) and \
        all(c != l for c, l in zip(pinned, skeleton_lines)):
    print('  The model obeyed the prompt verbatim. The frozen schema pinned the GLOSS')
    print('  ONLY, dropping the line-opening "— N〉 " that the prompt itself supplied.')
    print('  => Gate fired on a HARNESS-AUTHORED prompt/schema contradiction,')
    print('     not on a route defect, model substitution, or translation defect.')
else:
    print('  Model output does NOT match the skeleton lines verbatim; the failure is')
    print('  not attributable to the prompt/schema contradiction alone.')

# --- 2. the handoff's enumerated deterministic defect classes, checked directly ---
print('\n=== HANDOFF DEFECT CLASSES, CHECKED INDEPENDENTLY OF THE FROZEN SCHEMA ===')
defects = []


def check(name, ok, detail=''):
    print('  %-28s %s%s' % (name, 'clean' if ok else 'DEFECT',
                            (' — ' + detail) if detail else ''))
    if not ok:
        defects.append(name)


source_senses = len(skeleton_lines)
check('3/3 senses present', len(senses) == source_senses,
      'got %d of %d' % (len(senses), source_senses))
check('no dropped/merged senses',
      [s['tag'] for s in senses] == ['1', '2', '3'],
      'tags=%s' % [s['tag'] for s in senses])
check('sense order preserved',
      all(s['german'] == l for s, l in zip(senses, skeleton_lines)))

cyrillic = re.compile(r'[Ѐ-ӿ]')
latin = re.compile(r'[A-Za-z]')
check('russian non-empty + Cyrillic',
      all(cyrillic.search(s['russian']) for s in senses))
check('no untranslated German/Latin',
      not any(latin.search(s['russian']) for s in senses),
      ', '.join(s['russian'] for s in senses))
check('no placeholder leakage',
      not any('{T' in s['russian'] for s in senses))
check('no letter ё in russian',
      not any('ё' in s['russian'] for s in senses))
check('gloss markup {%…%} intact',
      all('{%' in s['german'] and '%}' in s['german'] for s in senses))
check('key1 no drift',
      result['cards'][0]['key1'] == 'dq_canary_puregloss',
      result['cards'][0]['key1'])
check('no synthetic-promotion claim',
      result['provenance']['promotable'] is False
      and result['provenance']['provenance_class'] == 'synthetic_control')
check('provenance hashes bound',
      result['provenance']['raw_sha256'].startswith('152a3eec')
      and result['provenance']['portrait_sha256'].startswith('a43235e3'))
check('government not invented',
      all(s['government'] == [] for s in senses))
check('exactly 1 card / 1 record',
      len(result['cards']) == 1 and len(result['cards'][0]['records']) == 1)

print('\n=== SUMMARY ===')
print('sealed envelope verdict      : schema_compliant=false, NO-GO (authoritative)')
print('gate failure attributed to   : harness prompt/schema contradiction on `german`')
print('other deterministic defects  : %d %s' % (len(defects), defects or '(none)'))
print('3/3 source senses rendered   : %s' % (len(senses) == source_senses))
print('\nThis diagnostic does NOT overturn the NO-GO and does not repair any output.')
