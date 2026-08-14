#!/usr/bin/env python
"""Hierarchical reuse for the PWG cache-economy contract (H2702).

Order:
  1. exact whole-card TM
  2. complete exact fragment TM
  3. deterministic evidence retrieval
  4. provider prefix cache (advisory; next step is generation)
  5. generation

Experimental TM lives only under the sealed run directory and cannot
shadow or promote into canonical paths. Fuzzy matches stay advisory.
"""
from __future__ import annotations

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
SRC = os.path.dirname(HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import cache_identity as ident  # noqa: E402
import translation_memory as tm  # noqa: E402

EXPERIMENTAL_FLAG = 'experimental'


class ReuseError(ValueError):
    pass


def assert_under_run(path, run_dir):
    path = os.path.abspath(path)
    run_dir = os.path.abspath(run_dir)
    try:
        common = os.path.commonpath([path, run_dir])
    except ValueError as exc:
        raise ReuseError('experimental path escapes run directory') from exc
    if common != run_dir:
        raise ReuseError('experimental path escapes run directory: %s' % path)
    return path


def experimental_tm_path(run_dir, name='card.json'):
    return assert_under_run(os.path.join(run_dir, 'tm', name), run_dir)


def _lookup_card(lang, raw_sha256, tm_file):
    if not tm_file or not os.path.isfile(tm_file):
        return None
    return tm.lookup(lang, raw_sha256, tm=tm_file)


def _lookup_frags(lang, frag_sources, frag_file):
    if not frag_file or not os.path.isfile(frag_file) or not frag_sources:
        return None
    loaded = tm.load_frag_tm(lang, path=frag_file)
    hits = []
    for source in frag_sources:
        address = tm.frag_address(lang, source)
        row = loaded.get(address)
        if not row:
            return None
        hits.append(row)
    return hits


def resolve(item, *, run_dir, lang='xx',
            canonical_card_tm=None, canonical_frag_tm=None,
            experimental_card_tm=None, experimental_frag_tm=None,
            evidence=None):
    """Resolve one work item. Never writes canonical paths.

    ``item`` needs ``raw_sha256`` (whole-card) and optional ``fragments``
    (exact plan() chunk texts). ``lang`` is an address namespace, not a
    content branch.
    """
    run_dir = os.path.abspath(run_dir)
    if experimental_card_tm:
        assert_under_run(experimental_card_tm, run_dir)
    if experimental_frag_tm:
        assert_under_run(experimental_frag_tm, run_dir)

    raw_sha = item.get('raw_sha256')
    fragments = list(item.get('fragments') or [])

    card_hit = _lookup_card(lang, raw_sha, canonical_card_tm) if raw_sha else None
    if card_hit:
        return {
            'tier': 'whole_card_tm',
            'source': 'canonical',
            'calls': 0,
            'hit': card_hit,
            'advisory': False,
        }

    exp_card = _lookup_card(lang, raw_sha, experimental_card_tm) if raw_sha else None
    if exp_card:
        # Experimental may fill a miss; it never overrides a canonical hit
        # (canonical already returned). It also cannot be promoted.
        if exp_card.get(EXPERIMENTAL_FLAG) is not True:
            raise ReuseError('experimental TM row missing experimental=true')
        return {
            'tier': 'whole_card_tm',
            'source': 'experimental',
            'calls': 0,
            'hit': exp_card,
            'advisory': False,
            'promotable': False,
        }

    frag_hit = _lookup_frags(lang, fragments, canonical_frag_tm)
    if frag_hit:
        return {
            'tier': 'fragment_tm',
            'source': 'canonical',
            'calls': 0,
            'hit': frag_hit,
            'advisory': False,
        }
    exp_frags = _lookup_frags(lang, fragments, experimental_frag_tm)
    if exp_frags:
        if any(row.get(EXPERIMENTAL_FLAG) is not True for row in exp_frags):
            raise ReuseError('experimental fragment missing experimental=true')
        return {
            'tier': 'fragment_tm',
            'source': 'experimental',
            'calls': 0,
            'hit': exp_frags,
            'advisory': False,
            'promotable': False,
        }

    evidence = list(evidence or item.get('evidence') or [])
    if evidence:
        return {
            'tier': 'evidence',
            'source': 'deterministic',
            'calls': 0,
            'hit': evidence,
            'advisory': True,
            'next': 'provider_cache',
        }

    if item.get('provider_cache_hint'):
        return {
            'tier': 'provider_cache',
            'source': 'provider',
            'calls': 1,
            'hit': None,
            'advisory': True,
            'next': 'generation',
        }

    return {
        'tier': 'generation',
        'source': None,
        'calls': 1,
        'hit': None,
        'advisory': False,
    }


def selftest():
    import json
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        run_dir = os.path.join(tmp, 'run')
        os.makedirs(os.path.join(run_dir, 'tm'), exist_ok=True)
        try:
            assert_under_run(os.path.join(tmp, 'escape.json'), run_dir)
            raise AssertionError('namespace escape was allowed')
        except ReuseError:
            pass

        raw = 'card-bytes'
        raw_sha = ident.sha256_bytes(raw)
        address = 'xx:%s' % raw_sha
        canon = os.path.join(tmp, 'translation_memory.xx.json')
        with open(canon, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump({
                'entries': {
                    address: {
                        'address': address,
                        'raw_sha256': raw_sha,
                        'trust_level': 'legacy_promoted',
                        'senses': [{'gloss': 'ok'}],
                    }
                }
            }, handle)

        # Isolated experimental file with the same address must not win.
        exp = experimental_tm_path(run_dir, 'translation_memory.xx.json')
        os.makedirs(os.path.dirname(exp), exist_ok=True)
        with open(exp, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump({
                'entries': {
                    address: {
                        'address': address,
                        'raw_sha256': raw_sha,
                        'trust_level': 'legacy_promoted',
                        'experimental': True,
                        'senses': [{'gloss': 'shadow'}],
                    }
                }
            }, handle)

        hit = resolve(
            {'raw_sha256': raw_sha},
            run_dir=run_dir,
            lang='xx',
            canonical_card_tm=canon,
            experimental_card_tm=exp,
        )
        if hit['source'] != 'canonical' or hit['hit']['senses'][0]['gloss'] != 'ok':
            raise AssertionError('canonical card must beat experimental')
        if hit['calls'] != 0:
            raise AssertionError('TM hit must be zero-call')

        miss_sha = ident.sha256_bytes('other-card')
        only_exp = resolve(
            {'raw_sha256': miss_sha},
            run_dir=run_dir,
            lang='xx',
            canonical_card_tm=canon,
            experimental_card_tm=exp,
        )
        if only_exp['tier'] != 'generation':
            raise AssertionError('experimental must not serve a different address')

        # Experimental-only miss on canonical, hit on experimental.
        exp_only_sha = ident.sha256_bytes('exp-only')
        exp_addr = 'xx:%s' % exp_only_sha
        with open(exp, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump({
                'entries': {
                    exp_addr: {
                        'address': exp_addr,
                        'raw_sha256': exp_only_sha,
                        'trust_level': 'legacy_promoted',
                        'experimental': True,
                        'senses': [{'gloss': 'exp'}],
                    }
                }
            }, handle)
        exp_hit = resolve(
            {'raw_sha256': exp_only_sha},
            run_dir=run_dir,
            lang='xx',
            canonical_card_tm=canon,
            experimental_card_tm=exp,
        )
        if exp_hit['source'] != 'experimental' or exp_hit.get('promotable') is not False:
            raise AssertionError('experimental hit must stay non-promotable')

        gen = resolve({'raw_sha256': ident.sha256_bytes('absent')},
                      run_dir=run_dir, lang='xx', canonical_card_tm=canon)
        if gen['tier'] != 'generation' or gen['calls'] != 1:
            raise AssertionError('miss must fall through to generation')

        ev = resolve(
            {'raw_sha256': ident.sha256_bytes('absent'),
             'evidence': [{'kind': 'example', 'sha256': ident.sha256_bytes('e')}]},
            run_dir=run_dir, lang='xx', canonical_card_tm=canon,
        )
        if ev['tier'] != 'evidence' or ev['next'] != 'provider_cache':
            raise AssertionError('evidence tier lost')

    print('cache_reuse selftest: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(selftest())
