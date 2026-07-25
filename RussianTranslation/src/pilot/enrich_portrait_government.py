#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Attach DE-side case-government (Rektion) to portrait senses (H1624 G2).

Sibling of enrich_portrait_derivation / enrich_portrait_grammar. Stamps each
sense with ``government: extract_government(de_source)`` where ``de_source`` is
the best available German text on the sense (prefer a full ``de``/``de_raw``/
``text`` field when present; else ``gloss_de`` + ``equivalents_de`` join).

The portrait input tree is local-only/gitignored; --selftest proves the attach
logic without writing. New portraits from microstructure.sense_node already
carry government at gen time — this script is the backfill for older portraits.

  python src/pilot/enrich_portrait_government.py <k1>           dry-run sample
  python src/pilot/enrich_portrait_government.py <k1> --apply   write portraits
  python src/pilot/enrich_portrait_government.py --selftest
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from government_census import extract_government  # noqa: E402


def de_source_for_sense(sense: dict) -> str:
    """Best DE text available on a portrait sense for government extraction."""
    for key in ('de_raw', 'de', 'text', 'german'):
        val = (sense or {}).get(key)
        if isinstance(val, str) and val.strip():
            return val
    parts = []
    for eq in (sense or {}).get('equivalents_de') or []:
        if eq:
            parts.append('{%s}' % eq if not str(eq).startswith('{%') else str(eq))
    gloss = (sense or {}).get('gloss_de') or ''
    if gloss:
        parts.append(gloss)
    return ' '.join(parts)


def attach_government_to_sense(sense: dict) -> dict:
    """Stamp sense['government'] from DE only. Mutates and returns sense."""
    sense['government'] = extract_government(de_source_for_sense(sense))
    return sense


def enrich_portrait_obj(port) -> object:
    """Attach government to every sense of a portrait object or list of them."""
    entries = port if isinstance(port, list) else [port]
    for entry in entries:
        for sense in entry.get('senses') or []:
            attach_government_to_sense(sense)
    return port


def run_key(key: str, apply: bool) -> None:
    from window_common import INP
    paths = sorted(glob.glob(os.path.join(INP, '%s~~*.portrait.json' % key)))
    if not paths:
        paths = sorted(glob.glob(os.path.join(INP, '%s.portrait.json' % key)))
    if not paths:
        sys.exit('no portraits for %r under %s (local-only store)' % (key, INP))
    n_senses = n_gov = 0
    sample = None
    for p in paths:
        port = json.load(open(p, encoding='utf-8'))
        enrich_portrait_obj(port)
        for entry in (port if isinstance(port, list) else [port]):
            for s in entry.get('senses') or []:
                n_senses += 1
                if s.get('government'):
                    n_gov += 1
                    if sample is None:
                        sample = (os.path.basename(p), s.get('n'), s.get('government'))
        if apply:
            json.dump(port, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    print('portraits=%d senses=%d with_government=%d apply=%s'
          % (len(paths), n_senses, n_gov, apply))
    if sample:
        print('sample: file=%s sense_n=%s government=%s' % sample)
    if not apply:
        print('(dry-run — pass --apply to write)')


def selftest() -> None:
    sense = {
        'n': '2',
        'gloss_de': 'sich heften auf (<ab>loc.</ab>) und Zuneigung',
        'equivalents_de': ['sich heften auf'],
    }
    attach_government_to_sense(sense)
    assert sense['government'] and sense['government'][0]['cases'] == ['loc'], sense
    # PW capitalized Instr. still caught via full de_raw
    sense2 = {
        'n': '1',
        'de_raw': '<ab>Caus.</ab> {#prativAsita#} {%gehüllt in%} (<ab>Instr.</ab>).',
        'gloss_de': 'gehüllt in',
    }
    attach_government_to_sense(sense2)
    assert sense2['government'][0]['cases'] == ['instr'], sense2
    assert sense2['government'][0]['span'] == '(<ab>Instr.</ab>)', sense2
    # plain sense -> empty list
    sense3 = {'n': '1', 'gloss_de': 'Gott', 'equivalents_de': ['Gott']}
    attach_government_to_sense(sense3)
    assert sense3['government'] == [], sense3
    port = {'senses': [dict(sense), dict(sense3)]}
    enrich_portrait_obj(port)
    assert port['senses'][0]['government'] and port['senses'][1]['government'] == []
    print('enrich_portrait_government --selftest: OK')


def main() -> None:
    argv = sys.argv[1:]
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        return
    if argv[0] in ('--selftest', 'selftest'):
        selftest()
        return
    key = argv[0]
    apply = '--apply' in argv[1:]
    run_key(key, apply)


if __name__ == '__main__':
    main()
