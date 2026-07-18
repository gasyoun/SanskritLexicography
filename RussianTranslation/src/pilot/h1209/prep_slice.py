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
  python prep_slice.py <manifest.json> <out_payload.json>
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def reconstruct_prompt(m, key):
    """Reproduce the exact single-card worker prompt from the manifest components.

    Mirrors gen_opt_harness2.py:
      cardBlock(k) = GRAMMARS[k] + '\n\n=== CARD k ===\n--- masked German ... ---\n'
                     + skeleton + suggestionBlock(k) + '\n--- portrait (evidence) ---\n' + portrait
      prompt       = PREAMBLE + GRAMMAR + CONV_TR + nws + cardBlock(k)
    suggestionBlock is empty when no suggestions were resolved (slice has none).
    """
    p = m['prompt']
    preamble = p['preamble']
    grammar_top = p.get('grammar', '') or ''
    conv_tr = p['translation']
    nws = p.get('nws_rule', '') or ''
    grammars_k = (p.get('grammars', {}) or {}).get(key, '') or ''
    inp = m['inputs'][key]
    skeleton = inp['skeleton']
    portrait = inp.get('portrait', '') or ''
    card_block = (
        grammars_k
        + '\n\n=== CARD ' + key + ' ===\n'
        + '--- masked German (translatable only; {Tn}=masked span) ---\n'
        + skeleton
        + '\n--- portrait (evidence) ---\n'
        + portrait
    )
    return preamble + grammar_top + conv_tr + nws + card_block


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


def main():
    if len(sys.argv) != 3:
        sys.exit('usage: prep_slice.py <manifest.json> <out_payload.json>')
    manifest_path, out_path = sys.argv[1], sys.argv[2]
    m = json.load(open(manifest_path, encoding='utf-8'))
    keys = [b[0] for b in m['batches']]  # slice is 1 card/batch
    cards = []
    for k in keys:
        prompt = reconstruct_prompt(m, k)
        feats = complexity_features(m, k)
        inp = m['inputs'][k]
        cards.append({
            'key1': k,
            'prompt': prompt,
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
        })
    payload = {
        'schema': 'h1209.controller_worker_slice.v2',
        'source_manifest': os.path.basename(manifest_path),
        'model_worker': m.get('model', 'claude-sonnet-5'),
        'field': m.get('field', 'russian'),
        'cards': cards,
    }
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write('\n')
    for c in cards:
        print('%-10s prompt=%dB tokens=%d source_senses=%s ls=%s sk=%s complexity=%.2f%s'
              % (c['key1'], len(c['prompt']), len(c['skeleton_tokens']),
                 c['source_senses'], c['ls'], c['sk'], c['complexity']['score'],
                 ' [COMPLEX]' if c['complexity']['complex'] else ''))
    print('wrote', out_path)


if __name__ == '__main__':
    main()
