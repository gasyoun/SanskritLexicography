#!/usr/bin/env python
r"""Build the Workflow `args`/inject payload from the prep_slice payload + manifest.

Two deterministic transformations, previously done by hand in-session (v1):
  1. Drop `placeholder_map` from each card — the Workflow script's gates are mask-level
     ({Tn} multiset equality), so the 90 KB of restoration payloads never enter the
     tool-call surface; restoration + the authoritative audit happen Python-side
     (canonical_audit.py) after the run.
  2. Derive `worker_schema` from the manifest's own `output_schema`: the worker returns
     ONE card (not a `cards[]` batch) plus the H1209 self-report block (architecture
     point 3: a mandatory "unsure" field is one of the three hard-case triggers).

Usage:
  python build_args.py <slice_payload.json> <manifest.json> <out_args.json>
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

SELF_REPORT = {
    'type': 'object', 'additionalProperties': False, 'required': ['unsure'],
    'properties': {
        'unsure': {'type': 'boolean',
                   'description': 'true if you were not confident about any sense/placeholder in this card'},
        'hardest_sense_tag': {'type': 'string',
                              'description': 'tag of the sense you were least sure of, or empty'},
        'note': {'type': 'string',
                 'description': 'one-line reason for any uncertainty, or empty'},
    },
}


def main():
    payload_path, manifest_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    payload = json.load(open(payload_path, encoding='utf-8'))
    man = json.load(open(manifest_path, encoding='utf-8'))
    for c in payload['cards']:
        c.pop('placeholder_map', None)
    defs = man['output_schema']['$defs']
    payload['worker_schema'] = {
        'type': 'object', 'additionalProperties': False,
        'required': ['card', 'self_report'],
        'properties': {'card': {'$ref': '#/$defs/card'}, 'self_report': SELF_REPORT},
        '$defs': defs,
    }
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('wrote %s: %d cards, worker_schema derived from manifest output_schema'
          % (out_path, len(payload['cards'])))


if __name__ == '__main__':
    main()
