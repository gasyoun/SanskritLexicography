#!/usr/bin/env python
"""Freeze the Wave-1 5,000-headword priority manifest (H2683 Track A).

Reuses pwg_freq_order.tsv (DCS/archive frequency), headword_index.tsv
(98,639 indexed rows), lexical-core SLP1 lists, and the publication TM
for citation/reuse signals. Does not rebuild a frequency table.

  python src/pwg_tm_priority.py --verify --limit 5000
  python src/pwg_tm_priority.py --limit 5000 --out-dir DIR
"""
from __future__ import annotations

import argparse
import math
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_canonical as C  # noqa: E402

HEADWORD_INDEX = os.path.join(HERE, 'headword_index.tsv')
FREQ_ORDER = os.path.join(HERE, 'pwg_freq_order.tsv')
SENSE_LOCI_SAMPLE = os.path.join(HERE, 'pwg_sense_loci.sample.tsv')
CORE_DIR = os.path.join(HERE, 'pilot', 'lexical_cores')
CORE_FILES = ('pril10.slp1.txt', 'pril5.slp1.txt', 'sbornoe.slp1.txt')

WEIGHTS = {
    'corpus_token_frequency': 0.40,
    'corpus_attestation': 0.15,
    'pwg_citation_degree': 0.15,
    'predicted_fragment_reuse': 0.10,
    'lexical_core_or_dcs': 0.10,
    'stratification': 0.10,
}
QUOTAS = {
    'attested_high': 3600,
    'lexical_core': 500,
    'complex': 400,
    'rare_attested': 300,
    'index_tail': 200,
}
EXPECTED_INDEX_ROWS = 98639


def _load_index(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        header = f.readline().rstrip('\n').split('\t')
        idx = {c: i for i, c in enumerate(header)}
        for line in f:
            p = line.rstrip('\n').split('\t')
            k1 = p[idx['k1']]
            if not k1:
                continue
            hom = (p[idx['hom']] if 'hom' in idx and idx['hom'] < len(p) else '').strip()
            members = p[idx['compound_members']] if 'compound_members' in idx and idx['compound_members'] < len(p) else ''
            n_members = 0
            if '+' in members:
                n_members = members.count('+') + 1
            elif members.strip():
                n_members = 1
            rows.append({
                'k1': k1,
                'hom': hom,
                'compound_members': n_members,
                'lex': p[idx['lex']] if 'lex' in idx and idx['lex'] < len(p) else '',
            })
    return rows


def _load_freq(path):
    out = {}
    with open(path, encoding='utf-8') as f:
        header = f.readline().rstrip('\n').split('\t')
        idx = {c: i for i, c in enumerate(header)}
        for line in f:
            p = line.rstrip('\n').split('\t')
            k1 = p[idx['k1_slp1']]
            ca = p[idx['count_all']].strip()
            ps = p[idx['periods_sum']].strip()
            out[k1] = {
                'slice_order': int(p[idx['slice_order']]),
                'count_all': int(ca) if ca else None,
                'periods_sum': int(ps) if ps else 0,
            }
    return out


def _load_core(path):
    keys = set()
    if not os.path.exists(path):
        return keys
    with open(path, encoding='utf-8') as f:
        for line in f:
            k = line.strip()
            if k:
                keys.add(k)
    return keys


def _load_loci_counts(path):
    counts = Counter()
    if not os.path.exists(path):
        return counts
    with open(path, encoding='utf-8') as f:
        header = f.readline().rstrip('\n').split('\t')
        idx = {c: i for i, c in enumerate(header)}
        for line in f:
            p = line.rstrip('\n').split('\t')
            k1 = p[idx['slp1']] if 'slp1' in idx else p[0]
            loci = p[idx['ls_loci']] if 'ls_loci' in idx and idx['ls_loci'] < len(p) else ''
            n = len([x for x in loci.split(';') if x.strip()]) if loci else 0
            if n:
                counts[k1] += n
    return counts


def _tm_signals(publication_path):
    cite = Counter()
    reuse = Counter()
    if not publication_path or not os.path.exists(publication_path):
        return cite, reuse
    for pub in C.read_jsonl(publication_path):
        lemma = C.lemma_of(pub)
        if not lemma:
            continue
        de, _ru = C.join_surfaces(pub)
        n_ls = len(_RE_LS.findall(de))
        n_gl = len(_RE_GL.findall(de))
        n_sa = len(_RE_SA.findall(de))
        n_ab = len(_RE_AB.findall(de))
        cite[lemma] += n_ls
        reuse[lemma] += n_ls + n_gl + n_sa + n_ab
    return cite, reuse


_RE_LS = re.compile(r'<ls\b')
_RE_GL = re.compile(r'\{%')
_RE_SA = re.compile(r'\{#')
_RE_AB = re.compile(r'<(?:ab|lex)\b')


def _norm(value, ceiling):
    if not ceiling:
        return 0.0
    return math.log1p(value) / math.log1p(ceiling)


def score_rows(index_rows, freq, cores, loci, tm_cite, tm_reuse):
    by_k1 = {}
    for row in index_rows:
        rec = by_k1.setdefault(row['k1'], {
            'k1': row['k1'],
            'n_index_rows': 0,
            'n_homonyms': 0,
            'max_compound_members': 0,
        })
        rec['n_index_rows'] += 1
        if row['hom']:
            rec['n_homonyms'] += 1
        if row['compound_members'] > rec['max_compound_members']:
            rec['max_compound_members'] = row['compound_members']
    max_freq = max((v['count_all'] or 0) for v in freq.values()) or 1
    max_per = max((v['periods_sum'] or 0) for v in freq.values()) or 1
    cite_values = []
    for k1 in by_k1:
        cite_values.append(tm_cite.get(k1, 0) + loci.get(k1, 0))
    max_cite = max(cite_values) if cite_values else 1
    max_reuse = max(tm_reuse.values()) if tm_reuse else 1
    scored = []
    for k1, rec in by_k1.items():
        f = freq.get(k1) or {}
        count_all = f.get('count_all')
        periods = f.get('periods_sum') or 0
        attested = count_all is not None
        cite = tm_cite.get(k1, 0) + loci.get(k1, 0)
        reuse = tm_reuse.get(k1, 0)
        if not reuse:
            reuse = 1 + rec['max_compound_members'] + (1 if rec['n_homonyms'] else 0)
        core = 0.0
        core_hit = []
        if k1 in cores['pril10']:
            core, core_hit = 1.0, ['pril10']
        elif k1 in cores['pril5']:
            core, core_hit = 0.7, ['pril5']
        elif k1 in cores['sbornoe']:
            core, core_hit = 0.5, ['sbornoe']
        elif attested:
            core = 0.3
        complex_flag = rec['max_compound_members'] >= 2 or rec['n_homonyms'] > 0 or cite >= 8
        strat = 0.0
        if complex_flag and not (attested and (count_all or 0) >= 1000):
            strat += 0.6
        if core_hit and not attested:
            strat += 0.4
        freq_n = _norm(count_all or 0, max_freq)
        attest_n = _norm(periods, max_per)
        cite_n = _norm(cite, max_cite or 1)
        reuse_n = _norm(reuse, max_reuse or 1)
        composite = (
            WEIGHTS['corpus_token_frequency'] * freq_n
            + WEIGHTS['corpus_attestation'] * attest_n
            + WEIGHTS['pwg_citation_degree'] * cite_n
            + WEIGHTS['predicted_fragment_reuse'] * reuse_n
            + WEIGHTS['lexical_core_or_dcs'] * core
            + WEIGHTS['stratification'] * min(1.0, strat)
        )
        rec.update({
            'count_all': count_all,
            'periods_sum': periods,
            'slice_order': f.get('slice_order'),
            'attested': attested,
            'citation_degree': cite,
            'predicted_reuse': reuse,
            'core_membership': core_hit,
            'complex': complex_flag,
            'score': round(composite, 10),
            'freq_component': round(freq_n, 6),
            'attest_component': round(attest_n, 6),
            'cite_component': round(cite_n, 6),
            'reuse_component': round(reuse_n, 6),
            'core_component': core,
            'strat_component': round(min(1.0, strat), 6),
        })
        scored.append(rec)
    scored.sort(key=lambda r: (-r['score'], r['k1']))
    return scored


def _pick(pool, already, n, pred):
    out = []
    for row in pool:
        if len(out) >= n:
            break
        if row['k1'] in already:
            continue
        if pred(row):
            out.append(row)
    return out


def select(scored, limit):
    already = set()
    chosen = []
    strata = {}

    def take(label, rows):
        for row in rows:
            already.add(row['k1'])
            item = dict(row)
            item['stratum'] = label
            chosen.append(item)
            strata[row['k1']] = label

    take('attested_high', _pick(
        scored, already, QUOTAS['attested_high'],
        lambda r: r['attested'] and (r['count_all'] or 0) > 0))
    take('lexical_core', _pick(
        scored, already, QUOTAS['lexical_core'],
        lambda r: bool(r['core_membership'])))
    take('complex', _pick(
        scored, already, QUOTAS['complex'],
        lambda r: r['complex']))
    take('rare_attested', _pick(
        scored, already, QUOTAS['rare_attested'],
        lambda r: r['attested'] and (r['count_all'] or 0) > 0))
    take('index_tail', _pick(
        scored, already, QUOTAS['index_tail'],
        lambda r: True))
    if len(chosen) < limit:
        take('composite_fill', _pick(
            scored, already, limit - len(chosen), lambda r: True))
    chosen.sort(key=lambda r: (-r['score'], r['k1']))
    chosen = chosen[:limit]
    for i, row in enumerate(chosen, 1):
        row['rank'] = i
    excluded = []
    selected_keys = {r['k1'] for r in chosen}
    for row in scored:
        if row['k1'] in selected_keys:
            continue
        reason = 'below_cutoff'
        if not row['attested'] and not row['core_membership']:
            reason = 'unattested_not_core'
        elif not row['attested']:
            reason = 'unattested_quota_full'
        elif row['complex']:
            reason = 'complex_quota_full'
        excluded.append({'k1': row['k1'], 'reason': reason, 'score': row['score']})
    return chosen, excluded


def build(limit, publication=None, out_dir=None):
    publication = publication or C.DEFAULT_PUBLICATION
    index_rows = _load_index(HEADWORD_INDEX)
    freq = _load_freq(FREQ_ORDER)
    cores = {
        'pril10': _load_core(os.path.join(CORE_DIR, CORE_FILES[0])),
        'pril5': _load_core(os.path.join(CORE_DIR, CORE_FILES[1])),
        'sbornoe': _load_core(os.path.join(CORE_DIR, CORE_FILES[2])),
    }
    loci = _load_loci_counts(SENSE_LOCI_SAMPLE)
    tm_cite, tm_reuse = _tm_signals(publication)
    scored = score_rows(index_rows, freq, cores, loci, tm_cite, tm_reuse)
    chosen, excluded = select(scored, limit)
    inputs = {
        'headword_index': {
            'path': os.path.relpath(HEADWORD_INDEX, C.ROOT).replace('\\', '/'),
            'sha256': C.sha256_file(HEADWORD_INDEX),
            'rows': len(index_rows),
            'unique_k1': len(scored),
        },
        'pwg_freq_order': {
            'path': os.path.relpath(FREQ_ORDER, C.ROOT).replace('\\', '/'),
            'sha256': C.sha256_file(FREQ_ORDER),
            'rows': len(freq),
        },
        'lexical_cores': {
            name: {
                'path': os.path.relpath(os.path.join(CORE_DIR, fname), C.ROOT).replace('\\', '/'),
                'sha256': C.sha256_file(os.path.join(CORE_DIR, fname)),
                'size': len(cores[name]),
            }
            for name, fname in zip(('pril10', 'pril5', 'sbornoe'), CORE_FILES)
            if os.path.exists(os.path.join(CORE_DIR, fname))
        },
        'pwg_sense_loci_sample': {
            'path': os.path.relpath(SENSE_LOCI_SAMPLE, C.ROOT).replace('\\', '/'),
            'sha256': C.sha256_file(SENSE_LOCI_SAMPLE) if os.path.exists(SENSE_LOCI_SAMPLE) else None,
            'keys_with_loci': len(loci),
        },
        'publication_tm': {
            'path': os.path.relpath(publication, C.ROOT).replace('\\', '/') if os.path.exists(publication) else None,
            'sha256': C.sha256_file(publication) if os.path.exists(publication) else None,
        },
    }
    reason_counts = dict(Counter(r['reason'] for r in excluded))
    manifest = {
        'schema': 'pwg.tm.priority.manifest.v1',
        'wave': 1,
        'limit': limit,
        'selected_count': len(chosen),
        'universe_unique_k1': len(scored),
        'universe_index_rows': len(index_rows),
        'weights': dict(WEIGHTS),
        'quotas': dict(QUOTAS),
        'inputs': inputs,
        'stratum_counts': dict(Counter(r['stratum'] for r in chosen)),
        'attested_selected': sum(1 for r in chosen if r['attested']),
        'core_selected': sum(1 for r in chosen if r['core_membership']),
        'exclusion_reason_counts': reason_counts,
        'excluded_count': len(excluded),
        'excluded_keys_sha256': C.sha256_json(sorted(r['k1'] for r in excluded)),
        'selected_keys_sha256': C.sha256_json([r['k1'] for r in chosen]),
    }
    manifest['manifest_sha256'] = C.sha256_json({
        k: manifest[k] for k in (
            'schema', 'wave', 'limit', 'weights', 'quotas', 'inputs',
            'selected_keys_sha256',
        )
    })
    if out_dir:
        C.write_json(os.path.join(out_dir, 'priority_%d.manifest.json' % limit), manifest)
        C.write_jsonl(os.path.join(out_dir, 'priority_%d.jsonl' % limit), [
            {
                'rank': r['rank'],
                'k1': r['k1'],
                'score': r['score'],
                'stratum': r['stratum'],
                'count_all': r['count_all'],
                'periods_sum': r['periods_sum'],
                'citation_degree': r['citation_degree'],
                'predicted_reuse': r['predicted_reuse'],
                'core_membership': r['core_membership'],
                'complex': r['complex'],
                'attested': r['attested'],
            }
            for r in chosen
        ])
        C.write_json(os.path.join(out_dir, 'priority_%d.denominators.json' % limit), {
            'index_rows': len(index_rows),
            'unique_k1': len(scored),
            'freq_matched': sum(1 for r in scored if r['attested']),
            'selected': len(chosen),
            'stratum_counts': manifest['stratum_counts'],
            'exclusion_reason_counts': reason_counts,
        })
    return chosen, excluded, manifest


def verify(limit):
    if not os.path.exists(HEADWORD_INDEX) or not os.path.exists(FREQ_ORDER):
        return False, 'missing frequency/index assets'
    chosen, excluded, manifest = build(limit, out_dir=None)
    keys = [r['k1'] for r in chosen]
    if len(keys) != limit:
        return False, 'selected %d != limit %d' % (len(keys), limit)
    if len(set(keys)) != limit:
        return False, 'duplicate headwords in selection'
    if manifest['universe_index_rows'] != EXPECTED_INDEX_ROWS:
        return False, 'index rows %d != %d' % (
            manifest['universe_index_rows'], EXPECTED_INDEX_ROWS)
    if not manifest.get('manifest_sha256'):
        return False, 'missing manifest hash'
    if not all(r.get('rank') == i for i, r in enumerate(chosen, 1)):
        return False, 'ranks not contiguous'
    again, _ex, man2 = build(limit, out_dir=None)
    if [r['k1'] for r in again] != keys:
        return False, 'queue not reproducible'
    if man2['manifest_sha256'] != manifest['manifest_sha256']:
        return False, 'manifest hash not stable'
    if man2['selected_keys_sha256'] != manifest['selected_keys_sha256']:
        return False, 'selected-key hash drift'
    if not excluded:
        return False, 'exclusion ledger empty'
    return True, 'ok %d unique; universe %d k1 / %d index rows; hash %s' % (
        limit, manifest['universe_unique_k1'], manifest['universe_index_rows'],
        manifest['manifest_sha256'][:16])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=5000)
    ap.add_argument('--publication', default=C.DEFAULT_PUBLICATION)
    ap.add_argument('--out-dir', default=C.DEFAULT_OUT_DIR)
    ap.add_argument('--verify', action='store_true')
    args = ap.parse_args(argv)
    if args.verify:
        ok, msg = verify(args.limit)
        print(msg)
        return 0 if ok else 1
    chosen, _excluded, manifest = build(
        args.limit, publication=args.publication, out_dir=args.out_dir)
    print('selected %d -> %s hash=%s' % (
        len(chosen), args.out_dir, manifest['manifest_sha256']))
    return 0 if len(chosen) == args.limit else 1


if __name__ == '__main__':
    sys.exit(main())
