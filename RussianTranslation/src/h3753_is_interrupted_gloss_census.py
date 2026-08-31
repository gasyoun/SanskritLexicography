#!/usr/bin/env python
"""H3753 W6 step 1 — census of <is>-interrupted gloss spans in the PWG TM source.

GAPS.md §18: pwg_tm_fragmentize.py's GLOSS_RE (`\\{%.*?%\\}`) matches each
`{%...%}` run independently, so a gloss whose halves sit on either side of an
`<is>...</is>` span (source/siglum text, e.g. `{%die%} <is>Viveqa Devaa.h</is>
{%zur Gottheit habend%}`) is emitted as two unrelated fragments instead of one.

  python h3753_is_interrupted_gloss_census.py

Reads the live publication JSONL (same source pwg_tm_fragmentize.py consumes),
walks every sense's German text via pwg_tm_canonical.sense_units, and counts
gloss-pairs separated only by whitespace + one <is>...</is> run.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_canonical as C  # noqa: E402

IS_INTERRUPT_RE = re.compile(
    r'(\{%.*?%\})\s*(<is\b[^>]*>.*?</is>)\s*(\{%.*?%\})', re.S)


def find_interruptions(german):
    """Return non-overlapping (gloss_a, is_run, gloss_b) interruption events.

    Chained interruptions (A <is> B <is> C) are walked left-to-right so a
    3-gloss chain counts as 2 events but 1 affected sense/record.
    """
    events = []
    pos = 0
    text = german or ''
    while True:
        m = IS_INTERRUPT_RE.search(text, pos)
        if not m:
            break
        events.append(m.groups())
        pos = m.end(1)  # allow the trailing gloss to open a NEXT pair (chain)
    return events


def main():
    pub_path = C.DEFAULT_PUBLICATION
    pubs = C.read_jsonl(pub_path)
    parents = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z')
               for p in pubs]

    total_senses = 0
    interrupted_events = 0
    interrupted_senses = 0
    interrupted_records = set()
    samples = []

    for parent in parents:
        pub = parent.get('source_publication') or parent
        record_hit = False
        for tag, german, russian, rec_h, ordinal in C.sense_units(pub):
            total_senses += 1
            events = find_interruptions(german)
            if events:
                interrupted_senses += 1
                interrupted_events += len(events)
                record_hit = True
                if len(samples) < 20:
                    samples.append({
                        'entry_id': parent.get('entry_id'),
                        'tag': tag,
                        'homonym': rec_h,
                        'events': len(events),
                        'first_event': events[0],
                    })
        if record_hit:
            interrupted_records.add(parent.get('record_id'))

    report = {
        'schema': 'h3753.is_interrupted_gloss_census.v1',
        'source': os.path.relpath(pub_path, C.ROOT).replace('\\', '/'),
        'parent_record_count': len(parents),
        'total_senses': total_senses,
        'senses_with_is_interrupted_glosses': interrupted_senses,
        'records_with_is_interrupted_glosses': len(interrupted_records),
        'is_interruption_events': interrupted_events,
        'sample': samples,
    }
    out_path = os.path.join(
        C.ROOT, 'docs', 'CENSUS_H3753_IS_INTERRUPTED_GLOSSES_31-08-2026.json')
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'sample'},
                      ensure_ascii=False, indent=2))
    print('wrote', out_path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
