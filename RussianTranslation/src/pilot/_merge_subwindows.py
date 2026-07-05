"""Reassemble split sub-window Workflow results into one root-scoped wf_output.json.

F-harness-size-limit workaround (EVOLUTION_TIMELINE.md): the pril10_w1 nominal
harness (8 largest PWG entries) is ~1MB, over the Workflow tool's 512KB scriptPath
cap, so it was split into 3 key-disjoint sub-windows (wA/wB/wC) run separately.
This merges their .result payloads back into a single pril10_w1 wf_output.json,
identical in shape to what an un-split run would have returned.

Usage: python _merge_subwindows.py out.json partA.json partB.json partC.json
"""
import sys, json

def main():
    out_path, parts = sys.argv[1], sys.argv[2:]
    metas, results, seen = [], [], set()
    for p in parts:
        with open(p, encoding='utf-8') as f:
            payload = json.load(f)
        metas.append(payload['meta'])
        for r in payload['results']:
            if r['key'] in seen:
                raise SystemExit('duplicate key across sub-windows: %r' % r['key'])
            seen.add(r['key'])
            results.append(r)
    # Single canonical META for the whole window: take the first, restore the full
    # key list + merged keymap so downstream (audit/promote) sees one pril10_w1 window.
    meta = dict(metas[0])
    all_keys, keymap, input_hashes = [], {}, {}
    for m in metas:
        all_keys += m['selected_keys']
        keymap.update(m.get('nominal_keymap') or {})
        # MUST merge input_hashes from EVERY sub-window: audit_window.py stale-checks
        # each key against meta.input_hashes; carrying only chunk-1's map fails the
        # check for every other chunk's keys (the documented `i`-split reassembly bug,
        # RUN_LOG 2026-06-29). Union all per-key hash maps.
        input_hashes.update(m.get('input_hashes') or {})
    meta['selected_keys'] = all_keys
    meta['input_hashes'] = input_hashes
    if meta.get('nominal'):
        meta['nominal_keymap'] = keymap
    meta['split_subwindows'] = [
        {'keys': m['selected_keys'], 'generated_at': m['generated_at']} for m in metas
    ]
    ok = sum(1 for r in results if r.get('card'))
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': results}, f, ensure_ascii=False, indent=1)
    print('wrote %s | root=%s | cards=%d ok=%d null=%d | keys=%d'
          % (out_path, meta['root'], len(results), ok, len(results) - ok, len(all_keys)))
    null_keys = [r['key'] for r in results if not r.get('card')]
    if null_keys:
        print('null keys (will requeue):', null_keys)

if __name__ == '__main__':
    main()
