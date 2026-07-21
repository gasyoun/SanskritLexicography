#!/usr/bin/env python
r"""H1209 controller-worker canary — slice prep.

Reconstructs, from a `gen_opt_harness2.py --manifest-out` execution manifest, the EXACT
per-card worker prompt the production harness would send (harness `cardBlock` line ~264 +
the `PREAMBLE + GRAMMAR + CONV_TR + nws + cardBlock` assembly line ~573), so the
controller-worker Workflow reuses the production translation invariants verbatim rather
than re-deriving them. Also computes the deterministic per-card complexity score (one of
the three controller "hard-case" triggers, H1209 architecture point 3) and carries the
placeholder map + expected sense count for the deterministic post-run audit.

Output: a compact `slice_payload.json` the Workflow tool consumes via `args` (Workflow
scripts have no filesystem access).

Usage:
  python prep_slice.py <manifest.json> <out_payload.json> [--keys k1,k2] [--chunk N]

H1386 D1 (the medium50 start-today enabler): the shared PREAMBLE + GRAMMAR + CONV_TR +
nws boilerplate (~12 KB) is hoisted into ONE payload-level `prompt_common` (schema v3);
each card carries only its `card_block`, and the Workflow template assembles
`prompt_common + card_block` per card (mirroring how gen_opt_harness2 shares PREAMBLE
across a batch). `--chunk N` splits a big manifest into N cap-sized sub-payloads
(`<out>.chunk01.json`, ...), each independently runnable; merge the chunk slice_results
with canonical_audit (it accepts several slice_result files). Pre-fix, a 50-card
medium50 build duplicated the boilerplate 50x (~612 KB alone) and died only at Workflow
submission against the 512 KB scriptPath cap.
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

PAYLOAD_SCHEMA = 'h1209.controller_worker_slice.v3'


def prompt_common(m):
    """The boilerplate shared by EVERY card's prompt: PREAMBLE + GRAMMAR + CONV_TR + nws.
    Hoisted once per payload (H1386 D1) -- the per-card assembly is prompt_common +
    card_block, byte-identical to the v2 per-card prompt."""
    p = m['prompt']
    return (p['preamble'] + (p.get('grammar', '') or '') + p['translation']
            + (p.get('nws_rule', '') or ''))


def card_block(m, key):
    """The per-card tail of the worker prompt.

    Mirrors gen_opt_harness2.py:
      cardBlock(k) = GRAMMARS[k] + '\n\n=== CARD k ===\n--- masked German ... ---\n'
                     + skeleton + suggestionBlock(k) + '\n--- portrait (evidence) ---\n' + portrait
    suggestionBlock is empty when no suggestions were resolved (slice has none).
    """
    p = m['prompt']
    grammars_k = (p.get('grammars', {}) or {}).get(key, '') or ''
    inp = m['inputs'][key]
    skeleton = inp['skeleton']
    portrait = inp.get('portrait', '') or ''
    return (
        grammars_k
        + '\n\n=== CARD ' + key + ' ===\n'
        + '--- masked German (translatable only; {Tn}=masked span) ---\n'
        + skeleton
        + '\n--- portrait (evidence) ---\n'
        + portrait
    )


def reconstruct_prompt(m, key):
    """The exact single-card worker prompt (v2 assembly) -- kept as the identity oracle:
    prompt_common(m) + card_block(m, key) must equal this, byte for byte."""
    return prompt_common(m) + card_block(m, key)


def placeholder_tokens(text):
    """The {Tn} tokens present, as a list (order preserved)."""
    return re.findall(r'\{T\d+\}', text)


def complexity_features(m, key):
    """Deterministic hard-case score. Cheap, transparent, no model call.

    Features (H1209 arch pt.3; H858 markup / H920 sense-loss defect classes made explicit):
      len_bytes      skeleton size
      n_senses       authoritative source sense count
      n_placeholders masked-span count (markup + Sanskrit + sigla density)
      cite_density   <ls> source-citations per sense
      rare_markup    <ab>/<lex>/<is> count (abbreviations / lexicographic / italic)
      sanskrit_spans {#..#} Sanskrit spans (transliteration-fidelity risk)
    """
    inp = m['inputs'][key]
    skeleton = inp['skeleton']
    pmap = m['placeholder_maps'][key]
    joined = '\n'.join(pmap)
    n_senses = inp.get('senses') or inp.get('source_senses') or len(re.findall(r'\d+〉', skeleton)) or 1
    n_ls = joined.count('<ls')
    n_ab = joined.count('<ab')
    n_lex = joined.count('<lex')
    n_is = joined.count('<is')
    n_skt = len(re.findall(r'\{#.*?#\}', joined))
    feats = {
        'len_bytes': len(skeleton),
        'n_senses': n_senses,
        'n_placeholders': len(placeholder_tokens(skeleton)),
        'cite_density': round(n_ls / max(n_senses, 1), 2),
        'rare_markup': n_ab + n_lex + n_is,
        'sanskrit_spans': n_skt,
    }
    # Transparent weighted score, normalized to roughly [0, ~10]. Not tuned — the point of
    # the canary is to MEASURE the false-flag rate of this trigger before tightening it.
    score = (
        feats['len_bytes'] / 2000.0
        + feats['n_senses'] / 5.0
        + feats['n_placeholders'] / 40.0
        + feats['cite_density'] / 2.0
        + feats['rare_markup'] / 10.0
        + feats['sanskrit_spans'] / 20.0
    )
    feats['score'] = round(score, 2)
    # Absolute trigger threshold for the slice; a card at/above this is controller-deep-reviewed
    # even if the worker self-reports confident and the deterministic gates pass.
    feats['complex'] = score >= 4.0
    return feats


def _build_card(m, k):
    feats = complexity_features(m, k)
    inp = m['inputs'][k]
    return {
        'key1': k,
        # H1386 D1: card_block ONLY -- the shared boilerplate lives once in prompt_common.
        'card_block': card_block(m, k),
        'skeleton_tokens': placeholder_tokens(inp['skeleton']),
        # v2: the sense gate consumes the H960 cross-reference-hardened source_senses
        # (shortfall-only, the canonical SAN-LOSS direction) — NEVER the naive `senses`
        # glyph count (nakzatra: senses=7 counts a PW cross-reference `3〉` as a sense;
        # gating on equality to it forced workers to displace source spans into
        # card.notes, an unrestorable field — the v1 slice's 2/3 canonical rejects).
        'source_senses': inp.get('source_senses'),
        'ls': inp.get('ls'), 'sk': inp.get('sk'),
        'placeholder_map': m['placeholder_maps'][k],
        'complexity': feats,
    }


def _chunk_out_path(out_path, i, n):
    base, ext = os.path.splitext(out_path)
    return '%s.chunk%02d%s' % (base, i, ext or '.json')


def write_payloads(m, out_path, keys=None, chunk=None, manifest_name=''):
    """Build and write the v3 payload(s). Returns the list of written paths.

    keys  -- optional explicit subset (order preserved); default: every batch key.
    chunk -- optional N-way contiguous split into <out>.chunkNN.json sub-payloads,
             each carrying the same prompt_common + its card subset (H1386 D1)."""
    # A6 (H1283): flatten EVERY key of each batch. Taking only b[0] silently dropped all
    # but the first card of every multi-card batch — invisible on the 1-card/batch canary
    # slice, but on a production medium50 manifest (multi-card batches) every other card
    # vanished with no error. Matches window_selftest's owed-key set ({k for b in batches for k}).
    all_keys = [k for b in m['batches'] for k in b]
    if keys:
        missing = [k for k in keys if k not in set(all_keys)]
        if missing:
            sys.exit('prep_slice: --keys not in the manifest batches: %s' % ','.join(missing))
        use_keys = list(keys)
    else:
        use_keys = all_keys
    common = prompt_common(m)
    cards = [_build_card(m, k) for k in use_keys]
    header = {
        'schema': PAYLOAD_SCHEMA,
        'source_manifest': manifest_name,
        'model_worker': m.get('model', 'claude-sonnet-5'),
        'field': m.get('field', 'russian'),
        'prompt_common': common,
    }
    if chunk and chunk > 1:
        n = min(chunk, len(cards)) or 1
        per = (len(cards) + n - 1) // n
        groups = [cards[i * per:(i + 1) * per] for i in range(n)]
        groups = [g for g in groups if g]
        paths = []
        for i, group in enumerate(groups, 1):
            payload = dict(header, chunk={'index': i, 'of': len(groups)}, cards=group)
            p = _chunk_out_path(out_path, i, len(groups))
            with open(p, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(payload, f, ensure_ascii=False, indent=1)
                f.write('\n')
            paths.append(p)
        return paths
    payload = dict(header, cards=cards)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write('\n')
    return [out_path]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('manifest')
    ap.add_argument('out_payload')
    ap.add_argument('--keys', default=None,
                    help='comma-separated subset of manifest keys to include')
    ap.add_argument('--chunk', type=int, default=None,
                    help='split into N cap-sized sub-payloads (<out>.chunkNN.json)')
    a = ap.parse_args()
    m = json.load(open(a.manifest, encoding='utf-8'))
    keys = [k for k in (a.keys or '').split(',') if k] or None
    paths = write_payloads(m, a.out_payload, keys=keys, chunk=a.chunk,
                           manifest_name=os.path.basename(a.manifest))
    for p in paths:
        payload = json.load(open(p, encoding='utf-8'))
        for c in payload['cards']:
            print('%-10s card_block=%dB tokens=%d source_senses=%s ls=%s sk=%s complexity=%.2f%s'
                  % (c['key1'], len(c['card_block']), len(c['skeleton_tokens']),
                     c['source_senses'], c['ls'], c['sk'], c['complexity']['score'],
                     ' [COMPLEX]' if c['complexity']['complex'] else ''))
        print('wrote %s (%d cards, prompt_common=%dB shared once)'
              % (p, len(payload['cards']), len(payload['prompt_common'])))


if __name__ == '__main__':
    main()
