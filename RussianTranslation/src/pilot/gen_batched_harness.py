#!/usr/bin/env python
"""PROTOTYPE generator — BATCHED translation-only harness.

The tlonly A/B (TLONLY_PROTOTYPE.md) showed the dominant cost is the FIXED
per-card subagent overhead (large system prompt + schema, paid once per card),
not the card text. So this harness amortizes that overhead: it MASKS each card
(pwg_mask, reused from the tlonly prototype) and then GROUPS several cards into a
single agent() call (one system prompt + schema per BATCH instead of per card),
returning an array of cards.

Usage:  python src/pilot/gen_batched_harness.py <root> --keys=k1,k2 [--budget=7000]
Writes: src/pilot/run_pilot_wf.batched.js  +  src/pilot/output/tlonly_phmaps.json
"""
import datetime
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from window_common import INP, REPO, OUT, input_paths, load_json, read_text, rootmap_path, sha256_file, write_text
import pwg_mask
from gen_tlonly_harness import extract_conv, TLCARD
from safe_filename import safe_name


def die(msg):
    sys.exit('FAIL: %s' % msg)


def parse_args(argv):
    if not argv:
        die('usage: gen_batched_harness.py <root> --keys=k1,k2 [--budget=N]')
    root, keyfilter, budget = argv[0], None, 7000
    for a in argv[1:]:
        if a.startswith('--keys='):
            keyfilter = set(filter(None, a.split('=', 1)[1].split(',')))
        elif a.startswith('--budget='):
            budget = int(a.split('=', 1)[1])
    return root, keyfilter, budget


def selected_keys(root, keyfilter):
    path, _ = rootmap_path(root)
    if not path:
        die('no rootmap for %r' % root)
    keys = [s['subkey'] for s in (load_json(path).get('sub_cards') or [])]
    if keyfilter:
        keys = [k for k in keys if k in keyfilter or k.split('~~')[-1] in keyfilter]
        if not keys:
            die('no sub-cards matched --keys')
    return path, keys


# Each batch returns {cards: [card, ...]} so several headwords share one call.
BATCH_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["cards"],
    "properties": {"cards": {"type": "array", "minItems": 1, "items": TLCARD}},
}

TASK = """TASK — translation only, MULTIPLE headwords per call. Below are SEVERAL \
PWG headwords, each in its own '=== CARD <key> ===' block. Each card's record(s) \
have all untranslatable markup removed and replaced by {Tn} placeholder tokens \
(Sanskrit {#..#}, refs <ls>, abbrevs <ab>, italic <is>, grammar <lex>); you see \
ONLY the translatable German gloss prose plus {Tn} tokens and the sense numbering.

For EACH card, and EACH record/sense in it, return its Russian rendering:
- Translate the German gloss prose into Russian per the conventions above.
- Keep the {Tn} tokens EXACTLY as-is where you refer to a masked span; never invent, \
renumber, drop, expand, or alter a {Tn}; never type Sanskrit/sigla/{#..#}/<..> markup \
yourself (Python restores the {Tn} deterministically). Do NOT echo the German.
- Use each card's portrait corpus candidates as primary evidence; discriminate \
near-synonyms à la Apresjan with a brief differentia; mark equivalence_type and \
source_type per sense; render EVERY sense in order — skip nothing.
- Return one object per headword in `cards`, with `key1` set so each maps back to \
its '=== CARD <key> ===' block. Return ALL headwords given, none omitted.

Return ONLY the structured object."""


def build(root, keys, rootmap, budget):
    conv = extract_conv()
    inputs, phmaps, input_hashes = {}, {}, {}
    for k in keys:
        rp, pp = input_paths(k)
        if not (os.path.exists(rp) and os.path.exists(pp)):
            die('missing input for %s' % k)
        raw = read_text(rp)
        skeleton, ph, _ = pwg_mask.mask(raw)
        if pwg_mask.restore(skeleton, ph) != raw:
            die('mask round-trip not lossless for %s' % k)
        inputs[k] = {'skeleton': skeleton, 'portrait': read_text(pp)}
        phmaps[k] = ph
        input_hashes[k] = {'raw_sha256': sha256_file(rp), 'portrait_sha256': sha256_file(pp)}

    # Greedy bin-packing into batches by cumulative skeleton+portrait chars.
    batches, cur, cur_sz = [], [], 0
    for k in keys:
        sz = len(inputs[k]['skeleton']) + len(inputs[k]['portrait'])
        if cur and cur_sz + sz > budget:
            batches.append(cur)
            cur, cur_sz = [], 0
        cur.append(k)
        cur_sz += sz
    if cur:
        batches.append(cur)

    meta = {
        'schema_version': 'pwg_ru.workflow_meta.v1', 'generator': 'gen_batched_harness.prototype',
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec='seconds').replace('+00:00', 'Z'),
        'root': root, 'safe_root': safe_name(root), 'mode': 'batched',
        'selected_keys': keys, 'batches': batches, 'batch_count': len(batches),
        'rootmap_sha256': sha256_file(rootmap), 'input_hashes': input_hashes,
    }
    js = """// PROTOTYPE — BATCHED translation-only harness (N cards per agent call).
export const meta = {
  name: 'pwgru-batched-%(root)s',
  description: 'PROTOTYPE: batched translation-only Russian rendering of masked PWG German; amortizes per-call prompt+schema overhead. Token A/B vs the per-card echo harness',
  phases: [{ title: 'Translate', detail: 'Sonnet: N masked cards per call -> array of cards' }],
}

const CONV = %(conv)s
const TASK = %(task)s
const BATCH_SCHEMA = %(schema)s
const BATCHES = %(batches)s
const INPUTS = %(inputs)s
const META = %(meta)s

const cardBlock = k => '\\n\\n=== CARD ' + k + ' ===\\n--- masked German (translatable only; {Tn}=masked span) ---\\n' + INPUTS[k].skeleton + '\\n--- portrait (evidence) ---\\n' + INPUTS[k].portrait

phase('Translate')
async function translateBatch(batch, bi) {
  const prompt = CONV + '\\n\\n' + TASK + batch.map(cardBlock).join('')
  for (let attempt = 0; attempt < 2; attempt++) {
    const res = await agent(prompt, { label: 'batch' + bi + '[' + batch.length + ']' + (attempt ? '(retry)' : ''), phase: 'Translate', schema: BATCH_SCHEMA, model: 'sonnet', tools: [] })
    if (res && Array.isArray(res.cards)) {
      const byKey = {}
      for (const c of res.cards) if (c && c.key1) byKey[c.key1] = c
      return batch.map(k => ({ key: k, card: byKey[k] || byKey[(k.split('~~').pop())] || res.cards[batch.indexOf(k)] || null }))
    }
  }
  return batch.map(k => ({ key: k, card: null }))
}
const grouped = await parallel(BATCHES.map((b, i) => () => translateBatch(b, i)))
const out = grouped.flat()
return { meta: META, results: out }
""" % {
        'root': root, 'conv': json.dumps(conv, ensure_ascii=True),
        'task': json.dumps(TASK, ensure_ascii=True), 'schema': json.dumps(BATCH_SCHEMA, ensure_ascii=True),
        'batches': json.dumps(batches), 'inputs': json.dumps(inputs, ensure_ascii=True),
        'meta': json.dumps(meta, ensure_ascii=True),
    }
    return js, phmaps, batches


def main():
    root, keyfilter, budget = parse_args(sys.argv[1:])
    rootmap, keys = selected_keys(root, keyfilter)
    js, phmaps, batches = build(root, keys, rootmap, budget)
    out_js = os.path.join(REPO, 'src', 'pilot', 'run_pilot_wf.batched.js')
    write_text(out_js, js)
    write_text(os.path.join(OUT, 'tlonly_phmaps.json'), json.dumps(phmaps, ensure_ascii=False))
    print('wrote', out_js, len(js), 'bytes |', len(keys), 'cards in', len(batches), 'batches',
          '(sizes', [len(b) for b in batches], ')')


if __name__ == '__main__':
    main()
