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

# DCS over-tag policy. A lemma's corpus states are filtered: a state backed only by
# a thin, low-confidence tail (fewer than DCS_MIN_SUPPORT texts AND no authoritative
# genre/name-hint text) is dropped before it tags a headword — this removes the
# homograph/date-fallback noise the inter-signal audit surfaced. The DCS index is
# lossless (`state_support`); this is the consumption-time threshold, so it is tunable
# without rescanning. _TRUSTED = confidences that justify keeping a single-text state.
DCS_MIN_SUPPORT = 2
_TRUSTED_CONF = ('high', 'medium')


def filter_dcs_states(index_entry, min_support=DCS_MIN_SUPPORT):
    """Apply the min-support policy to one dcs_lemma_renou.json entry.

    Keep a state iff it is attested in ≥ `min_support` corpus texts, OR at least one
    of those texts is confidently typed (authoritative DCS genre / curated name hint).
    Back-compatible: an old index entry without `state_support` is returned unchanged.
    """
    states = list(index_entry.get('renou') or [])
    support = index_entry.get('state_support')
    if not support:
        return states
    return [st for st in states
            if support.get(st, {}).get('n', 0) >= min_support
            or support.get(st, {}).get('conf') in _TRUSTED_CONF]


def dcs_oldest(index_entry, kept_states):
    """The earliest-attested *kept* dcs state, for `renou_dcs_oldest`. The index's
    raw `renou_oldest` may name a state the min-support policy just pruned; fall back
    to the earliest surviving state (by chronological state order). '' when none survive."""
    if not kept_states:
        return ''
    raw = (index_entry or {}).get('renou_oldest') or ''
    if raw in kept_states:
        return raw
    return min(kept_states, key=lambda s: _ORDER.get(s, 99))


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
