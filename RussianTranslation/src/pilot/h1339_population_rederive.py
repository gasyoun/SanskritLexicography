#!/usr/bin/env python
r"""h1339_population_rederive.py — rederive the UNIQUE remaining runnable population (H1339 Phase 0).

Why this exists: H1283 REFUTED the "~10,199 remaining runnable headwords" inventory — the
three nominal lexical-core lists (pril5 / pril10 / sbornoe) are NESTED, not disjoint
(pril5 ∩ sbornoe == pril5), so adding their lengths double-counts. This script derives the
population ONCE, at the unique-lemma level, with explicit set semantics, and emits a
machine-checkable JSON + content hash so no future plan can silently re-inflate it.

Set semantics (dedup key = SLP1 `key1`, one classification per unique lemma):

  VERB lane      = verbs01 universe ∩ DCS-attested (scale_manifest.freq.json)
                   − promoted (store key1s). "Runnable NOW" additionally requires a
                   generated rootmap on disk — an EPHEMERAL generation-state filter
                   (inputs are regenerable via `_pilot_gen_merged.py --root-split`),
                   reported separately and NEVER subtracted from the population.
  NOMINAL union  = set-union of the three core lists (nested lists collapse here).
                   Verb lemmas (POS='v' or in the verbs01 universe) are excluded —
                   they belong to the verb lane (no double count across lanes).
  PWG-rooted     = union lemmas whose form_key hits dm.index('pwg'), − promoted.
  no-PWG lane    = union lemmas absent from PWG but present in PW/SCH/PWKVN
                   (H206/H214 supplement-chain lane), − promoted. Kept SEPARATE from
                   the PWG-rooted count (different-vintage source), never summed.
  true misses    = absent from every local layer. Not runnable, listed for audit.

Content hash = SHA-256 over the sorted, lane-tagged unique remaining key list, so two
derivations agree byte-for-byte or loudly don't.

Reads ONLY (no store/state writes): the freq manifest, the canonical RU store, the
verbs01 preverb list, the three committed core lists, and the local dictionary layers
via dict_merge. Gitignored inputs (manifest, store) are resolved worktree-safely: local
first, else the MAIN checkout via store_path.main_worktree_root (H255-class safety).

Usage (from RussianTranslation/):
  python src/pilot/h1339_population_rederive.py [--json OUT.json]
"""
import argparse
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(os.path.dirname(HERE))                    # RussianTranslation/
SRC = os.path.join(RT, 'src')

if SRC not in sys.path:
    sys.path.insert(0, SRC)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import corpus_gate as cg                                        # noqa: E402
import dict_merge as dm                                         # noqa: E402
from store_path import canonical_store, main_worktree_root      # noqa: E402
from verb_worklist import verb_universe, store_roots, has_rootmap  # noqa: E402
from nominals_worklist import read_wordlist                     # noqa: E402

PREVERB = os.path.normpath(os.path.join(RT, '..', '..', 'PWG', 'verbs01', 'pwg_preverb1.txt'))
CORES = ['pril5', 'pril10', 'sbornoe']
CORES_DIR = os.path.join(HERE, 'lexical_cores')


def _worktree_safe(rel_from_rt):
    """Resolve a gitignored artifact: this checkout first, else the MAIN checkout (linked worktree)."""
    local = os.path.join(RT, *rel_from_rt.split('/'))
    if os.path.exists(local):
        return local
    main = main_worktree_root(RT)
    if main:
        cand = os.path.join(main, 'RussianTranslation', *rel_from_rt.split('/'))
        if os.path.exists(cand):
            return cand
    return local


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def derive(manifest_path, store_path_, preverb, cores_dir, rootmap_dir):
    freq = {it['key1']: it for it in json.load(open(manifest_path, encoding='utf-8'))}
    done = store_roots(store_path_)
    verbs = verb_universe(preverb)

    # --- VERB lane ---------------------------------------------------------
    attested = sorted(k for k in verbs if k in freq)
    verb_promoted = sorted(k for k in attested if k in done)
    verb_remaining = sorted(k for k in attested if k not in done)
    verb_runnable_now = [k for k in verb_remaining if has_rootmap(k, rootmap_dir)]

    # --- NOMINAL union (nested cores collapse to one set) ------------------
    union, per_core, core_sizes = {}, {}, {}
    for core in CORES:
        path = os.path.join(cores_dir, core + '.slp1.txt')
        words, meta = read_wordlist(path)
        core_sizes[core] = len(words)
        for w in words:
            union.setdefault(w, {'cores': [], 'meta': meta.get(w, {})})
            union[w]['cores'].append(core)
            if meta.get(w):
                union[w]['meta'] = meta[w]
    per_core = {c: core_sizes[c] for c in CORES}

    pwg = dm.index('pwg')
    other = [('pw', dm.index('pw')), ('sch', dm.index('sch')), ('pwkvn', dm.index('pwkvn'))]

    nom_verbs, pwg_hits, no_pwg, true_miss = [], [], [], []
    for w, info in union.items():
        if info['meta'].get('pos') == 'v' or w in verbs:
            nom_verbs.append(w)
            continue
        fk = cg.form_key(w)
        if fk in pwg:
            pwg_hits.append(w)
        else:
            layers = [code for code, idx in other if fk in idx]
            (no_pwg if layers else true_miss).append(w)

    pwg_promoted = sorted(w for w in pwg_hits if w in done)
    pwg_remaining = sorted(w for w in pwg_hits if w not in done)
    no_pwg_promoted = sorted(w for w in no_pwg if w in done)
    no_pwg_remaining = sorted(w for w in no_pwg if w not in done)

    # cross-lane overlap proofs (all must be empty / true)
    overlap_verb_nominal = sorted(set(verb_remaining) & set(pwg_remaining) | set(verb_remaining) & set(no_pwg_remaining))
    overlap_pwg_nopwg = sorted(set(pwg_remaining) & set(no_pwg_remaining))

    tagged = (['verb\t' + k for k in verb_remaining]
              + ['nominal_pwg\t' + k for k in pwg_remaining]
              + ['nominal_no_pwg\t' + k for k in no_pwg_remaining])
    content_hash = hashlib.sha256('\n'.join(sorted(tagged)).encode('utf-8')).hexdigest()

    store_rows = 0
    with open(store_path_, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                store_rows += 1

    return {
        'inputs': {
            'manifest': manifest_path.replace('\\', '/'),
            'manifest_sha256': sha256_file(manifest_path),
            'store': store_path_.replace('\\', '/'),
            'store_sha256': sha256_file(store_path_),
            'store_rows': store_rows,
            'store_unique_key1': len(done),
            'preverb': preverb.replace('\\', '/'),
            'cores': {c: os.path.join(cores_dir, c + '.slp1.txt').replace('\\', '/') for c in CORES},
            'rootmap_dir': rootmap_dir.replace('\\', '/'),
        },
        'dedup_key': 'key1 (SLP1), one classification per unique lemma; lanes disjoint by construction',
        'verb_lane': {
            'universe_verbs01': len(verbs),
            'dcs_attested': len(attested),
            'promoted': len(verb_promoted),
            'remaining': len(verb_remaining),
            'runnable_now_has_rootmap': len(verb_runnable_now),
            'rootmaps_on_disk_note': 'has_rootmap is generation STATE (regenerable inputs), not population',
        },
        'nominal_union': {
            'per_core_raw_sizes': per_core,
            'union_unique_lemmas': len(union),
            'nested_double_count_avoided': sum(per_core.values()) - len(union),
            'verbs_excluded_to_verb_lane': len(nom_verbs),
            'pwg_hits': len(pwg_hits),
            'pwg_promoted': len(pwg_promoted),
            'pwg_remaining': len(pwg_remaining),
            'no_pwg_layer_hits': len(no_pwg),
            'no_pwg_promoted': len(no_pwg_promoted),
            'no_pwg_remaining': len(no_pwg_remaining),
            'true_misses': len(true_miss),
        },
        'overlap_proofs': {
            'verb_remaining_x_nominal_remaining': overlap_verb_nominal,
            'pwg_remaining_x_no_pwg_remaining': overlap_pwg_nopwg,
        },
        'unique_remaining_total_headwords': len(verb_remaining) + len(pwg_remaining) + len(no_pwg_remaining),
        'lane_totals_do_not_sum_rule': 'no_pwg lane rests on different-vintage source; report separately, never one production number',
        'content_hash_sha256_sorted_tagged_remaining': content_hash,
        'remaining_keys': {
            'verb': verb_remaining,
            'nominal_pwg': pwg_remaining,
            'nominal_no_pwg': no_pwg_remaining,
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--json', help='write the full payload JSON here (default: stdout summary only)')
    ap.add_argument('--manifest', default=_worktree_safe('src/pilot/output/scale_manifest.freq.json'))
    ap.add_argument('--store', default=canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl')))
    ap.add_argument('--preverb', default=PREVERB)
    ap.add_argument('--cores-dir', default=CORES_DIR)
    ap.add_argument('--rootmap-dir', default=os.path.join(HERE, 'input'))
    a = ap.parse_args()

    payload = derive(a.manifest, a.store, a.preverb, a.cores_dir, a.rootmap_dir)

    v, n = payload['verb_lane'], payload['nominal_union']
    print('H1339 population rederive (dedup key = key1; lanes disjoint):')
    print('  store: %d rows / %d unique key1  (%s)' % (
        payload['inputs']['store_rows'], payload['inputs']['store_unique_key1'],
        payload['inputs']['store_sha256'][:12]))
    print('  VERB lane:    universe %d | attested %d | promoted %d | REMAINING %d (runnable-now %d; rootmaps are regenerable state)'
          % (v['universe_verbs01'], v['dcs_attested'], v['promoted'], v['remaining'], v['runnable_now_has_rootmap']))
    print('  NOMINAL union: %s raw -> %d unique (nested overlap collapsed: %d) | verbs->verb lane %d'
          % ('+'.join(str(n['per_core_raw_sizes'][c]) for c in CORES), n['union_unique_lemmas'],
             n['nested_double_count_avoided'], n['verbs_excluded_to_verb_lane']))
    print('    PWG-rooted:  hits %d | promoted %d | REMAINING %d' % (n['pwg_hits'], n['pwg_promoted'], n['pwg_remaining']))
    print('    no-PWG lane: hits %d | promoted %d | REMAINING %d (separate lane, never summed)' % (
        n['no_pwg_layer_hits'], n['no_pwg_promoted'], n['no_pwg_remaining']))
    print('    true misses: %d' % n['true_misses'])
    print('  overlap proofs: verb x nominal = %d | pwg x no-pwg = %d (both must be 0)'
          % (len(payload['overlap_proofs']['verb_remaining_x_nominal_remaining']),
             len(payload['overlap_proofs']['pwg_remaining_x_no_pwg_remaining'])))
    print('  UNIQUE REMAINING TOTAL (all lanes, headwords): %d' % payload['unique_remaining_total_headwords'])
    print('  content hash: %s' % payload['content_hash_sha256_sorted_tagged_remaining'])

    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)
        print('payload written: %s' % a.json)


if __name__ == '__main__':
    main()
