#!/usr/bin/env python
"""Production harness v2 — BATCHED + MASKED, canonical output.

Folds the two measured wins (TLONLY_PROTOTYPE.md) into the production path:
  - BATCHING: several cards per agent() call (amortizes the ~27k-token system-prompt
    cache-create that dominates cost — measured -89% on small cards).
  - MASKING: each card's raw is pwg_mask-skeletonized so the model reads/echoes the
    compact {Tn} form, not full citation lists. {Tn} restored to exact source markup
    IN THE JS before returning, so the result is already a canonical wf_output.json
    (rich per-card schema unchanged) — no new operator assembly step, audit_window.py
    consumes it as-is.

Quality parity: reuses the FULL production CONV+TR prompt (all HARD RULES, NWS owner
map, Nachträge, microstructure) with a MASKED/BATCHED preamble that overrides only the
input-format + markup-verbatim specifics ("keep {Tn} verbatim" instead of "{#..#}/<ls>").

Usage:  python src/pilot/gen_opt_harness2.py <root> [--keys=k1,k2] [--budget=9000]
Writes: src/pilot/run_pilot_wf.opt2.js
"""
import datetime
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from window_common import INP, REPO, SRC, input_paths, load_json, read_text, rootmap_path, sha256_file, write_text
import pwg_mask
sys.path.insert(0, SRC)
from safe_filename import safe_name
from whitney_grammar import grammar_for


def grammar_text(root):
    """Compact, token-light grammar block for the root (Whitney), injected ONCE per run.
    The whole root's sub-cards share its conjugation, so this is far cheaper than a
    per-portrait block. Empty string if the root has no Whitney record (e.g. non-roots)."""
    recs = grammar_for(root)
    if not recs:
        return ''
    lines = ['=== GRAMMAR (Whitney) — the root\'s conjugation; use to inform grammatical '
             'notes and FLAG irregular/defective forms; NEVER let grammar override a corpus- '
             'or German-attested sense ===']
    amb = len(recs) > 1
    for r in recs:
        hom = ('/%s' % r['homonym']) if r['homonym'] else ''
        forms = ', '.join('%s' % f['form'] for f in r['attested_forms'][:6])
        secs = ', '.join('%s §%s' % (k, v) for k, v in list(r['section_refs'].items())[:8])
        lines.append('root %s%s (Whitney no.%s): class %s%s, PPP %s, periods %s'
                     % (r['root_iast'], hom, r['whitney_no'], r['class'],
                        ' [class uncertain]' if r['class_uncertain'] else '', r['ppp'],
                        '/'.join(r['period_tags'])))
        if r['irregularities']:
            lines.append('  irregularities: %s' % '; '.join(r['irregularities']))
        if forms:
            lines.append('  corpus-attested forms: %s' % forms)
        if secs:
            lines.append('  Whitney §§ per form-category: %s' % secs)
    if amb:
        lines.append('(NOTE: %d Whitney homonyms — pick the one matching the sense; '
                     'do not conflate.)' % len(recs))
    return '\n'.join(lines) + '\n\n'


def die(msg):
    sys.exit('FAIL: %s' % msg)


def parse_args(argv):
    if not argv:
        die('usage: gen_opt_harness2.py <root> [--keys=..] [--budget=N]')
    root, keyfilter, budget = argv[0], None, 9000
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


def extract_conv_tr():
    src = read_text(os.path.join(REPO, 'src', 'pilot', 'run_pilot_wf.js'))
    m = re.search(r'const TR = `(.*?)`\n', src, re.S)
    if not m:
        die('could not extract TR block from run_pilot_wf.js')
    return m.group(1)  # TR already embeds ${CONV}; we resolve CONV below


def conv_text():
    src = read_text(os.path.join(REPO, 'src', 'pilot', 'run_pilot_wf.js'))
    m = re.search(r'const CONV = `(.*?)`\n', src, re.S)
    if not m:
        die('could not extract CONV block')
    return m.group(1)


MASK_PREAMBLE = """=== MASKED + BATCHED REGIME (read first — overrides input-format details below) ===
You are given SEVERAL headwords at once, each in its own '=== CARD <key> ===' block.
Each card's source German has been MASKED: every untranslatable span (Sanskrit {#..#},
source refs <ls>, abbreviations <ab>, italic <is>, grammar <lex>) is replaced by a {Tn}
placeholder token. You see ONLY the translatable German gloss prose + {Tn} tokens + the
sense numbering. A Python post-step restores every {Tn} to its exact original markup.

Therefore, wherever the rules below say "keep {#..#}/<ls>/<ab> verbatim" or "reproduce
the markup delimiters EXACTLY", that now means: **keep every {Tn} placeholder verbatim,
unchanged and in its original order** — never invent, renumber, drop, expand, merge, or
alter a {Tn}, and never type any Sanskrit, siglum, or markup yourself. In the `german`
field, reproduce the masked skeleton you were given for that sense EXACTLY (its German +
its {Tn} tokens). In the `russian` field, put your translation, placing the relevant {Tn}
tokens where the source cited a masked span. Translate EACH card; return one object per
headword in `cards`, with `key1` matching its '=== CARD <key> ===' header. Omit nothing.

"""


def build(root, keys, rootmap, budget):
    conv = conv_text()
    tr = extract_conv_tr().replace('${CONV}', conv)
    schema = load_json(os.path.join(REPO, 'schemas', 'pwg_ru_final_card.schema.json'))
    defs = schema['$defs']
    card_ref = {'$ref': '#/$defs/card'}
    batch_schema = {
        'type': 'object', 'additionalProperties': False, 'required': ['cards'],
        'properties': {'cards': {'type': 'array', 'minItems': 1, 'items': card_ref}},
        '$defs': defs,
    }

    inputs, phmaps, input_hashes = {}, {}, {}
    for k in keys:
        rp, pp = input_paths(k)
        if not (os.path.exists(rp) and os.path.exists(pp)):
            die('missing input for %s' % k)
        raw = read_text(rp)
        skel, ph, _ = pwg_mask.mask(raw)
        if pwg_mask.restore(skel, ph) != raw:
            die('mask round-trip not lossless for %s' % k)
        inputs[k] = {'skeleton': skel, 'portrait': read_text(pp),
                     'ls': raw.count('<ls'), 'sk': raw.count('{#')}
        phmaps[k] = ph
        input_hashes[k] = {'raw_sha256': sha256_file(rp), 'portrait_sha256': sha256_file(pp)}

    batches, cur, sz = [], [], 0
    for k in keys:
        ksz = len(inputs[k]['skeleton']) + len(inputs[k]['portrait'])
        if cur and sz + ksz > budget:
            batches.append(cur); cur, sz = [], 0
        cur.append(k); sz += ksz
    if cur:
        batches.append(cur)

    meta = {
        'schema_version': 'pwg_ru.workflow_meta.v1', 'generator': 'gen_opt_harness2.batched-masked',
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec='seconds').replace('+00:00', 'Z'),
        'root': root, 'safe_root': safe_name(root), 'mode': 'batched_masked',
        'selected_keys': keys, 'batches': batches, 'batch_count': len(batches),
        'rootmap_sha256': sha256_file(rootmap), 'input_hashes': input_hashes,
    }

    js = """// AUTO-DERIVED v2 (batched + masked, canonical output) from run_pilot_wf.js - root=%(root)s.
// Several masked cards per agent call; {Tn} restored to source markup in-JS so the
// returned result is a canonical wf_output.json. See TLONLY_PROTOTYPE.md.
export const meta = {
  name: 'pwgru-opt2-%(root)s',
  description: 'batched+masked translation-only PWG->Russian; amortized per-call overhead + masked I/O, {Tn} restored in-JS to canonical cards',
  phases: [{ title: 'Translate', detail: 'Sonnet: N masked cards per call -> rich cards; {Tn} restored to markup' }],
}

const CONV_TR = %(tr)s
const PREAMBLE = %(preamble)s
const GRAMMAR = %(grammar)s
const CARDS_SCHEMA = %(schema)s
const BATCHES = %(batches)s
const INPUTS = %(inputs)s
const PH = %(phmaps)s
const META = %(meta)s

const restore = (t, ph) => (t || '').replace(/\\{T(\\d+)\\}/g, (m, n) => (ph[+n - 1] !== undefined ? ph[+n - 1] : m))
const countOf = (card, re) => { let n = 0; for (const rec of (card.records || [])) for (const s of (rec.senses || [])) n += ((s.german || '').match(re) || []).length; return n }
function restoreCard(card, k) {
  const ph = PH[k] || []
  for (const rec of (card.records || [])) for (const s of (rec.senses || [])) {
    if (s.german !== undefined) s.german = restore(s.german, ph)
    if (s.russian !== undefined) s.russian = restore(s.russian, ph)
  }
  return card
}
const cardBlock = k => '\\n\\n=== CARD ' + k + ' ===\\n--- masked German (translatable only; {Tn}=masked span) ---\\n' + INPUTS[k].skeleton + '\\n--- portrait (evidence) ---\\n' + INPUTS[k].portrait

const accept = (c, k) => {
  if (!c) return null
  c = restoreCard(c, k)
  // Fidelity guard: restored <ls>/{#..#} counts MUST match the source — a mismatch
  // means misalignment / dropped {Tn}. Reject -> deterministic requeue, never emit garbled.
  if (countOf(c, /<ls\\b/g) !== INPUTS[k].ls || countOf(c, /\\{#/g) !== INPUTS[k].sk) return null
  return c
}

phase('Translate')
async function translateBatch(batch, bi) {
  // Retry ONLY the cards still unresolved (positional within the shrinking pending
  // set), not the whole batch — one missing/garbled card must not re-bill the rest.
  const resolved = {}
  let pending = batch.slice()
  for (let attempt = 0; attempt < 2 && pending.length; attempt++) {
    const prompt = PREAMBLE + GRAMMAR + CONV_TR + pending.map(cardBlock).join('')
    const res = await agent(prompt, { label: 'b' + bi + '[' + pending.length + ']' + (attempt ? '(retry)' : ''), phase: 'Translate', schema: CARDS_SCHEMA, model: 'sonnet', tools: [] })
    if (res && Array.isArray(res.cards)) {
      pending.forEach((k, i) => { const c = accept(res.cards[i], k); if (c) resolved[k] = c })
    }
    pending = pending.filter(k => !resolved[k])
  }
  return batch.map(k => ({ key: k, card: resolved[k] || null, judge: null, judge_sonnet: null, escalated: false }))
}
const grouped = await parallel(BATCHES.map((b, i) => () => translateBatch(b, i)))
const out = grouped.flat()
return { meta: META, results: out }
""" % {
        'root': root, 'tr': json.dumps(tr, ensure_ascii=True),
        'preamble': json.dumps(MASK_PREAMBLE, ensure_ascii=True),
        'grammar': json.dumps(grammar_text(root), ensure_ascii=True),
        'schema': json.dumps(batch_schema, ensure_ascii=True),
        'batches': json.dumps(batches), 'inputs': json.dumps(inputs, ensure_ascii=True),
        'phmaps': json.dumps(phmaps, ensure_ascii=True), 'meta': json.dumps(meta, ensure_ascii=True),
    }
    for bad in ['readFileSync', 'fileURLToPath', 'import.meta']:
        if bad in js:
            die('residual node-ism: %s' % bad)
    return js, batches


def main():
    root, keyfilter, budget = parse_args(sys.argv[1:])
    rootmap, keys = selected_keys(root, keyfilter)
    js, batches = build(root, keys, rootmap, budget)
    out = os.path.join(REPO, 'src', 'pilot', 'run_pilot_wf.opt2.js')
    write_text(out, js)
    print('wrote', out, len(js), 'bytes |', len(keys), 'cards in', len(batches), 'batches',
          '(sizes', [len(b) for b in batches], ')')


if __name__ == '__main__':
    main()
