#!/usr/bin/env python
"""renou.py — sense → Renou language-state(s) of Sanskrit, from <ls> citations.

Louis Renou (Histoire de la langue sanskrite, 1956) organises Sanskrit into five
language-states (the book's five chapters); we tag each dictionary *sense* by the
era(s) its source quotations belong to:

  I   Vedic            — Saṃhitā, Brāhmaṇa, Upaniṣad, Sūtra, Vedāṅga
  II  Pāṇinian         — the classical norm & grammarians' Sanskrit
  III Epic             — Mbh, Rām, Harivaṃśa, Gītā, Purāṇa, Smṛti, Tantra (+ prolongements)
  IV  Classical        — kāvya, drama, kathā, classical śāstra, kośa, later grammar
  V   Buddhist / Jaina — Buddhist Hybrid & Jaina Sanskrit

A sense is MULTI-LABEL: a meaning attested in several eras carries all of them
(e.g. ["I", "III"]). The *oldest* citation is flagged separately so one can ask
"in which era was this meaning first attested".

Mapping source → state lives in ls_source_map.json (PWG) / ls_source_map_mw.json
(MW), built by build_ls_map.py / build_ls_map_mw.py. The <ls> parsing here reuses
build_ls_map.source_key so citation normalisation is shared across the pipeline.

  import renou
  renou.states_for_text('… <ls n="ṚV">1,1</ls> … <ls n="M">2</ls> …')
  # → {'renou': ['I', 'III'], 'renou_oldest': 'I',
  #    'oldest_source': 'ṚV', 'oldest_date': -1125}
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import build_ls_map as blm        # PWG: <ls n="…">…</ls> parsing + source_key
import build_ls_map_mw as blm_mw   # MW:  <ls>SIGL vol, …</ls> parsing + source_key

HERE = os.path.dirname(os.path.abspath(__file__))
STATES = ('I', 'II', 'III', 'IV', 'V')
_ORDER = {s: i for i, s in enumerate(STATES)}
RENOU_NAME = {'I': 'Vedic', 'II': 'Pāṇinian', 'III': 'Epic',
              'IV': 'Classical', 'V': 'Buddhist/Jaina'}

_MAP_FILE = {'pwg': 'ls_source_map.json', 'mw': 'ls_source_map_mw.json'}
_CACHE = {}


def load_map(dict_name='pwg'):
    """source_key → record ({renou, date, name, …}) for the named dictionary."""
    if dict_name not in _CACHE:
        path = os.path.join(HERE, _MAP_FILE[dict_name])
        _CACHE[dict_name] = json.load(open(path, encoding='utf-8'))
    return _CACHE[dict_name]


def keys_in_text(text, dict_name='pwg'):
    """Every <ls> source key cited in a chunk of dictionary source text. The
    parser/normaliser differs per dictionary (PWG reads the n="" siglum; MW reads
    the leading siglum before the lowercase-roman volume ref)."""
    text = text or ''
    if dict_name == 'mw':
        return [blm_mw.source_key(m.group(1)) for m in blm_mw.LS.finditer(text)]
    return [blm.source_key(m.group(1), m.group(2)) for m in blm.LS.finditer(text)]


def states_for_keys(source_keys, dict_name='pwg'):
    """Resolve already-extracted <ls> source keys → Renou states.

    Returns the multi-label state list (ordered I→V) plus the oldest-citation
    flag. Keys absent from the map are ignored, so only recognised quotations
    contribute — uncited senses come back empty.
    """
    smap = load_map(dict_name)
    states, oldest = set(), None  # oldest = (key, date, state)
    for k in source_keys:
        rec = smap.get(k)
        if not rec:
            continue
        states.add(rec['renou'])
        d = rec.get('date')
        if d is not None and (oldest is None or d < oldest[1]):
            oldest = (k, d, rec['renou'])
    return {
        'renou': sorted(states, key=_ORDER.get),
        'renou_oldest': oldest[2] if oldest else '',
        'oldest_source': oldest[0] if oldest else '',
        'oldest_date': oldest[1] if oldest else None,
    }


def states_for_text(text, dict_name='pwg'):
    """Convenience: extract <ls> keys from source text, then classify."""
    return states_for_keys(keys_in_text(text, dict_name), dict_name)


if __name__ == '__main__':
    # tiny self-check
    demo = '<ls n="ṚV">1,1</ls> rest <ls n="M">2,5</ls> tail <ls n="ZZZ">9</ls>'
    import pprint
    pprint.pprint(states_for_text(demo))
