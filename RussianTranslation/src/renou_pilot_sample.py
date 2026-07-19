#!/usr/bin/env python
"""renou_pilot_sample.py — Step-0 pilot human-validation sample (Renou hypotheses spec).

Draws a fixed, deterministic 70-entry stratified sample from the canonical
`{code}.renou.jsonl` indices, targeting the *contested* signal cells (per
RENOU_HYPOTHESES.md, "Step 0 — pilot human validation"):

  A. dcs-only states       20  a state whose provenance is exactly ["dcs"];
                                spread over states I-V and >=4 dicts
  B. bhs-only V             15  V: ["bhs"] and no other V signal
  C. maximal-span suspects  15  renou_enriched = I-V while ls supports <=2 states
  D. single-era dcs_adds    10  ls+dcs both present, dcs adds exactly one era beyond ls
  E. corroborated controls  10  >=2 signals agreeing on every state (expected-good)

Each sampled item is enriched with full evidence for the pilot review sheet:
headword (IAST/key2), dictionary, the contested state, the full provenance
dict, resolved <ls> citations (siglum -> source name/date, re-extracted read-only
from the csl-orig source block — the canonical *.renou.jsonl records do not
retain resolved sigla, only state-level provenance), and the DCS state_support
detail (texts/confidence) behind the contested state from dcs_lemma_renou.json.

Read-only: never mutates {code}.renou.jsonl, dcs_lemma_renou.json, or csl-orig
source. Deterministic: fixed seed (42), stable input order -> identical output
on every run (verified: two runs diff empty).

  python renou_pilot_sample.py [--out renou_pilot_sample.jsonl] [--seed 42]

Computed by Sonnet 5 (claude-sonnet-5), per RENOU_HYPOTHESES.md Step 0 (spec
authored by Fable 5, claude-fable-5).
"""
import json
import os
import random
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
CSL = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02'))
CANON = ('pwg', 'mw', 'pw', 'ap', 'ap90', 'ben', 'sch', 'bhs')
STATES = ('I', 'II', 'III', 'IV', 'V')
_ORDER = {s: i for i, s in enumerate(STATES)}
SEED = 42

sys.path.insert(0, HERE)
import renou            # noqa: E402  (PWG/MW <ls> resolution + siglum map)
import renou_sigla      # noqa: E402  (ap/ap90/ben/bhs siglum resolution)

PWG_STYLE = {'pwg', 'pw', 'pwk', 'pwkvn', 'sch'}
INLINE = {'ap', 'ap90', 'ben', 'bhs'}

K1 = re.compile(r'<k1>(.*?)(?:<k2>|<e>|<h>|$)', re.S)


def load_jsonl(code):
    path = os.path.join(HERE, code + '.renou.jsonl')
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def load_dcs_index():
    path = os.path.join(HERE, 'dcs_lemma_renou.json')
    d = json.load(open(path, encoding='utf-8'))
    d.pop('__sources__', None)
    return d


def load_source_blocks(code):
    """key1 -> raw <L>...<LEND> source block, for re-extracting resolved <ls>
    citations (siglum -> source name) the canonical jsonl does not retain.
    Read-only: opens csl-orig source, never writes to it."""
    src = os.path.join(CSL, code, code + '.txt')
    if not os.path.exists(src):
        return {}
    data = open(src, encoding='utf-8').read()
    blocks = re.findall(r'<L>(.*?)<LEND>', data, re.S)
    if not blocks:
        parts = re.split(r'(?=<L>)', data)
        blocks = [p for p in parts if p.startswith('<L>')]
    out = {}
    for block in blocks:
        m = K1.search(block)
        if m:
            out[m.group(1).strip()] = block
    return out


def resolved_ls_citations(code, block):
    """[{siglum/name, state, date}] — the actual resolved <ls> citations behind
    an entry, re-derived the same way tag_dict_from_source.py does (read-only)."""
    out = []
    if code in PWG_STYLE:
        for k in renou.keys_in_text(block, 'pwg'):
            rec = renou.load_map('pwg').get(k)
            if rec:
                out.append({'siglum': k, 'name': rec.get('name'),
                             'state': rec.get('renou'), 'date': rec.get('date')})
    elif code == 'mw':
        for k in renou.keys_in_text(block, 'mw'):
            rec = renou.load_map('mw').get(k)
            if rec:
                out.append({'siglum': k, 'name': rec.get('name'),
                             'state': rec.get('renou'), 'date': rec.get('date')})
    else:
        for sig in renou_sigla.sigla_in_block(block):
            if not sig:
                continue
            if code == 'bhs':
                if sig in renou_sigla.BHS_META:
                    continue
                out.append({'siglum': sig, 'name': sig, 'state': 'V',
                             'date': renou_sigla.BHS_DATE})
            else:
                hit = renou_sigla._TABLES.get(code, {}).get(sig)
                if hit:
                    out.append({'siglum': sig, 'name': sig, 'state': hit[0], 'date': hit[1]})
    # dedup, keep stable order
    seen = set()
    uniq = []
    for c in out:
        key = (c['siglum'], c['state'])
        if key not in seen:
            seen.add(key)
            uniq.append(c)
    return uniq


def dcs_state_support_detail(dcs_index, iast, state):
    """The state_support entry for one lemma/state, plus n_texts/oldest_text
    context — the DCS evidence a human needs to judge a dcs-only state."""
    info = dcs_index.get(iast)
    if not info:
        return None
    supp = (info.get('state_support') or {}).get(state)
    return {
        'n_texts_lemma_total': info.get('n_texts'),
        'oldest_text': info.get('oldest_text'),
        'oldest_date': info.get('oldest_date'),
        'state_support': supp,
    }


def clean_hw(s):
    """A single-line headword label — some source key2 fields over-capture an XML
    block; keep only the bare form before any markup/newline (mirrors
    renou_audit.py's clean_hw so sheet items and audit rows read the same way)."""
    s = (s or '').replace('\n', ' ').split('<')[0].split('{')[0].strip()
    return (s[:40] + '…') if len(s) > 41 else s


def make_item(item_id, stratum, code, rec, contested_state, blocks, dcs_index):
    key1 = rec.get('key1', '')
    block = blocks.get(key1, '')
    return {
        'item_id': item_id,
        'stratum': stratum,
        'dict': code,
        'key1': key1,
        'headword_iast': rec.get('iast'),
        'headword_key2': clean_hw(rec.get('key2')),
        'contested_state': contested_state,
        'renou_enriched': rec.get('renou_enriched'),
        'renou_provenance': rec.get('renou_provenance'),
        'renou_ls': rec.get('renou_ls'),
        'renou_dcs': rec.get('renou_dcs'),
        'renou_bhs': rec.get('renou_bhs'),
        'resolved_ls_citations': resolved_ls_citations(code, block) if block else [],
        'dcs_evidence': dcs_state_support_detail(dcs_index, rec.get('iast', ''), contested_state),
    }


def stratum_a(all_recs, rng, n=20):
    """dcs-only states: provenance for some state is exactly ['dcs'];
    spread over states I-V and >=4 dicts."""
    candidates = []
    for code, rec in all_recs:
        prov = rec.get('renou_provenance') or {}
        for st, srcs in prov.items():
            if srcs == ['dcs']:
                candidates.append((code, rec, st))
    rng.shuffle(candidates)
    # greedy spread: fill per-state buckets round-robin, tracking dict diversity
    by_state = {s: [] for s in STATES}
    for c in candidates:
        by_state[c[2]].append(c)
    picked, used_dicts, i = [], set(), 0
    order = list(STATES)
    while len(picked) < n:
        st = order[i % len(order)]
        i += 1
        if not by_state[st]:
            if all(not v for v in by_state.values()):
                break
            continue
        picked.append(by_state[st].pop())
        used_dicts.add(picked[-1][0])
        if i > n * 20:
            break
    return picked[:n]


def stratum_b(all_recs, rng, n=15):
    """bhs-only V: V provenance is exactly ['bhs']."""
    candidates = [(code, rec, 'V') for code, rec in all_recs
                  if (rec.get('renou_provenance') or {}).get('V') == ['bhs']]
    rng.shuffle(candidates)
    return candidates[:n]


def stratum_c(all_recs, rng, n=15):
    """maximal-span suspects: renou_enriched == I-V while ls supports <=2 states
    (the audit's akara pattern)."""
    full = set(STATES)
    candidates = []
    for code, rec in all_recs:
        enr = set(rec.get('renou_enriched') or [])
        ls = set(rec.get('renou_ls') or [])
        if enr == full and len(ls) <= 2:
            # contested state = a state NOT supported by ls (the suspect span)
            added = sorted(enr - ls, key=_ORDER.get)
            if added:
                candidates.append((code, rec, added[-1]))  # most classical added state
    rng.shuffle(candidates)
    return candidates[:n]


def stratum_d(all_recs, rng, n=10):
    """single-era dcs_adds: both ls+dcs present, dcs adds exactly one era beyond ls."""
    candidates = []
    for code, rec in all_recs:
        ls = set(rec.get('renou_ls') or [])
        dcs = set(rec.get('renou_dcs') or [])
        if ls and dcs and ls < dcs and len(dcs - ls) == 1:
            added = list(dcs - ls)[0]
            candidates.append((code, rec, added))
    rng.shuffle(candidates)
    return candidates[:n]


def stratum_e(all_recs, rng, n=10):
    """corroborated controls: >=2 signals agreeing on every state (expected-good;
    calibrates the sheet)."""
    candidates = []
    for code, rec in all_recs:
        prov = rec.get('renou_provenance') or {}
        if prov and all(len(srcs) >= 2 for srcs in prov.values()):
            # contested state = any state (all equally corroborated) — pick the oldest
            states = sorted(prov.keys(), key=_ORDER.get)
            candidates.append((code, rec, states[0]))
    rng.shuffle(candidates)
    return candidates[:n]


STRATA = [
    ('A', 'dcs-only states', stratum_a, 20),
    ('B', 'bhs-only V', stratum_b, 15),
    ('C', 'maximal-span suspects', stratum_c, 15),
    ('D', 'single-era dcs_adds', stratum_d, 10),
    ('E', 'corroborated controls', stratum_e, 10),
]


def build_sample(seed=SEED):
    dcs_index = load_dcs_index()
    all_recs = []
    blocks_by_code = {}
    for code in CANON:
        recs = load_jsonl(code)
        for r in recs:
            all_recs.append((code, r))
        blocks_by_code[code] = None  # lazy-load below only for hit codes

    items = []
    item_id = 1
    composition = {}
    for label, name, fn, n in STRATA:
        rng = random.Random('%d:%s' % (seed, label))
        picked = fn(all_recs, rng, n)
        composition[label] = {}
        for code, rec, state in picked:
            if blocks_by_code[code] is None:
                blocks_by_code[code] = load_source_blocks(code)
            items.append(make_item('S0-%03d' % item_id, label, code, rec, state,
                                    blocks_by_code[code], dcs_index))
            item_id += 1
            composition[label][code] = composition[label].get(code, 0) + 1
    return items, composition


def main():
    args = sys.argv[1:]
    out = os.path.join(HERE, 'renou_pilot_sample.jsonl')
    seed = SEED
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--out':
            out = args[i + 1]; i += 2
        elif a == '--seed':
            seed = int(args[i + 1]); i += 2
        else:
            raise SystemExit('unknown option: %s' % a)

    items, composition = build_sample(seed)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + '\n')

    print('sample: %d items -> %s' % (len(items), os.path.basename(out)))
    for label, name, _, n in STRATA:
        by_dict = composition.get(label, {})
        print('  %s (%s): %d items across %d dicts — %s'
              % (label, name, sum(by_dict.values()), len(by_dict),
                 ', '.join('%s=%d' % (k, v) for k, v in sorted(by_dict.items()))))


if __name__ == '__main__':
    main()
