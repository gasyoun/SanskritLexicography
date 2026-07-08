#!/usr/bin/env python
"""Cite Elizarenkova's published Russian Rig-Veda rendering for an RV location.

Advisory/citation-context witness ONLY (H361) — surfaces the published Russian
translation for a Rig-Veda stanza a PWG/MW headword cites (e.g. `<ls>RV.1.1.1</ls>`),
for scholarly context alongside the headword card. Never written into
headword_index.tsv or any other reviewed store data; this is a read-only lookup
over a committed external feed.

Source: VedaWeb 2.0 (Universitaet zu Koeln) export of Elizarenkova, Tatyana.
1989/1995/1999. Rigveda: Izbrannye gimny (Rigveda: Selected Hymns), Vols 1-3.
Moskau: Nauka. CC BY 4.0, confirmed 08-07-2026 (see VisualDCS/non-derived/vedaweb/README.md).

**Distinct from** the Elizarenkova text already inside SamudraManthanam's parallel
corpus (grey-rights, not redistributable) -- do not conflate the two sources; this
module reads only the VedaWeb-sourced, explicitly-licensed copy.

  python src/vedaweb_ru_witness.py 1.1.1          exact RV location (mandala.hymn.stanza)
  python src/vedaweb_ru_witness.py --hymn 1.1     every stanza in a hymn
  python src/vedaweb_ru_witness.py --citation     print the full bibliographic citation
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FEED = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..', '..', 'VisualDCS', 'non-derived', 'vedaweb', 'elizarenkova_ru_1989_1999.json',
)


def load_feed():
    path = os.path.normpath(FEED)
    if not os.path.exists(path):
        print(
            f"ERROR: feed not found at {path}\n"
            "Expected VisualDCS as a sibling of SanskritLexicography "
            "(see VisualDCS/non-derived/vedaweb/README.md for retrieval).",
            file=sys.stderr,
        )
        sys.exit(1)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def by_location(feed):
    return {entry['location']: entry['text'] for entry in feed.get('contents', [])}


def print_citation(feed):
    citation = feed.get('citation')
    if isinstance(citation, list):
        for block in citation:
            print(block)
    else:
        print(citation)


def main():
    args = sys.argv[1:]
    if not args or '--citation' in args:
        feed = load_feed()
        if '--citation' in args:
            print_citation(feed)
            return
        print(__doc__)
        return

    feed = load_feed()
    locs = by_location(feed)

    if args[0] == '--hymn':
        if len(args) < 2:
            print("usage: --hymn <mandala.hymn>", file=sys.stderr)
            sys.exit(1)
        prefix = args[1] + '.'
        matches = sorted(
            (loc for loc in locs if loc.startswith(prefix)),
            key=lambda loc: int(loc.split('.')[-1]),
        )
        if not matches:
            print(f"No stanzas found for hymn {args[1]}", file=sys.stderr)
            sys.exit(1)
        for loc in matches:
            print(f"[{loc}] {locs[loc]}")
        return

    location = args[0]
    text = locs.get(location)
    if text is None:
        print(f"No Elizarenkova rendering found for location {location!r}", file=sys.stderr)
        sys.exit(1)
    print(f"[{location}] {text}")


if __name__ == '__main__':
    main()
