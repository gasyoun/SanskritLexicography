#!/usr/bin/env python
"""PROTOTYPE generator — translation-only model I/O (Python owns ALL markup).

Contrast with gen_opt_harness.py (the production harness):
  - production: model reads the FULL raw (citations + Sanskrit + markup) and
    ECHOES the german field verbatim in its output. ~60% of output is echo, ~28%+
    of input is <ls> citation lists, and the model can corrupt a delimiter.
  - this prototype: the raw is masked with pwg_mask (every <ls>/<ab>/<is>/{#..#}
    span -> {Tn} placeholder; lossless restore). The model sees ONLY translatable
    German + the {Tn} tokens, and returns ONLY the Russian per sense (NO german
    echo). Python restores the {Tn} tokens and welds the german back at assembly
    (assemble_tlonly.py). The model therefore can neither read nor type markup —
    the corruption class is impossible by construction.

Usage:  python src/pilot/gen_tlonly_harness.py <root> --keys=k1,k2
Writes: src/pilot/run_pilot_wf.tlonly.js  +  src/pilot/output/tlonly_phmaps.json
"""
import datetime
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from window_common import INP, REPO, SRC, OUT, input_paths, load_json, read_text, rootmap_path, sha256_file, write_text

sys.path.insert(0, SRC)
from safe_filename import safe_name
import pwg_mask

GENERATOR_VERSION = 'gen_tlonly_harness.prototype'


def die(msg):
    sys.exit('FAIL: %s' % msg)


def extract_conv():
    src = read_text(os.path.join(REPO, 'src', 'pilot', 'run_pilot_wf.js'))
    m = re.search(r'const CONV = `(.*?)`\n', src, re.S)
    if not m:
        die('could not extract CONV block from run_pilot_wf.js')
    return m.group(1)


def parse_args(argv):
    if not argv:
        die('usage: gen_tlonly_harness.py <root> --keys=k1,k2')
    root = argv[0]
    keyfilter = None
    for a in argv[1:]:
        if a.startswith('--keys='):
            keyfilter = set(filter(None, a.split('=', 1)[1].split(',')))
    return root, keyfilter


def selected_keys(root, keyfilter):
    path, _stem = rootmap_path(root)
    if not path:
        die('no rootmap for %r' % root)
    rm = load_json(path)
    keys = [s['subkey'] for s in (rm.get('sub_cards') or [])]
    if keyfilter:
        keys = [k for k in keys if k in keyfilter or k.split('~~')[-1] in keyfilter]
        if not keys:
            die('no sub-cards matched --keys')
    return path, keys


# Reduced schema: NO german field — the model returns ONLY the Russian per sense.
TLCARD = {
    "type": "object", "additionalProperties": False,
    "required": ["key1", "records"],
    "properties": {
        "key1": {"type": "string", "minLength": 1},
        "records": {
            "type": "array", "minItems": 1,
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["h", "senses"],
                "properties": {
                    "h": {"type": "string"},
                    "grammar": {"type": "string"},
                    "senses": {
                        "type": "array", "minItems": 1,
                        "items": {
                            "type": "object", "additionalProperties": False,
                            "required": ["tag", "russian"],
                            "properties": {
                                "tag": {"type": "string"},
                                "russian": {"type": "string"},
                                "equivalence_type": {"type": "string"},
                                "source_type": {"type": "string"},
                                "stratum": {"type": "string"},
                                "differentia": {"type": "string"},
                            }}}}}}}}

TASK = """TASK — translation only. Below is ONE PWG headword's record(s) with all \
untranslatable markup already REMOVED and replaced by {Tn} placeholder tokens \
(Sanskrit {#..#}, source refs <ls>, abbreviations <ab>, italic <is>, grammar <lex> \
are each a {Tn}). You see ONLY the translatable German gloss prose plus the {Tn} \
tokens and the sense numbering (1)/2) senses, a)/b) sub-senses).

For EACH record (homonym) and EACH sense/sub-sense, return its Russian rendering:
- Translate the German gloss prose into Russian per the conventions above.
- Keep the {Tn} tokens EXACTLY as-is wherever you need to refer to a masked span \
(a cited Sanskrit form, an abbreviation, a source) — never invent, renumber, drop, \
expand, or alter a {Tn}; never type any Sanskrit, siglum, or {#..#}/<..> markup \
yourself. Python restores the {Tn} tokens deterministically.
- Do NOT echo the German. Do NOT reproduce citations. Return ONLY the Russian (plus \
any {Tn} tokens it needs), the matching sense `tag`, and the metadata fields.
- Use the portrait corpus candidates as primary evidence for word choice; discriminate \
near-synonyms à la Apresjan and state a brief differentia. Mark equivalence_type and \
source_type (attested vs lexicographic) per sense. Render EVERY sense, in order — skip nothing.

Return ONLY the structured object."""


def build(root, keys, rootmap):
    conv = extract_conv()
    inputs, phmaps, input_hashes = {}, {}, {}
    for k in keys:
        raw_path, portrait_path = input_paths(k)
        if not (os.path.exists(raw_path) and os.path.exists(portrait_path)):
            die('missing input for %s' % k)
        raw = read_text(raw_path)
        skeleton, ph, _stats = pwg_mask.mask(raw)
        if pwg_mask.restore(skeleton, ph) != raw:
            die('mask round-trip not lossless for %s' % k)
        inputs[k] = {'skeleton': skeleton, 'portrait': read_text(portrait_path)}
        phmaps[k] = ph
        input_hashes[k] = {'raw_sha256': sha256_file(raw_path),
                           'portrait_sha256': sha256_file(portrait_path)}
    meta = {
        'schema_version': 'pwg_ru.workflow_meta.v1',
        'generator': GENERATOR_VERSION,
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec='seconds').replace('+00:00', 'Z'),
        'root': root, 'safe_root': safe_name(root), 'mode': 'tlonly',
        'selected_keys': keys, 'rootmap_sha256': sha256_file(rootmap),
        'input_hashes': input_hashes,
    }
    js = """// PROTOTYPE — translation-only harness (Python owns all markup via pwg_mask {Tn}).
export const meta = {
  name: 'pwgru-tlonly-%(root)s',
  description: 'PROTOTYPE: translation-only Russian rendering of masked PWG German (model never sees/emits markup); token A/B vs the production echo harness',
  phases: [{ title: 'Translate', detail: 'Sonnet: Russian per sense from masked German; {Tn} kept verbatim' }],
}

const CONV = %(conv)s
const TASK = %(task)s
const TLCARD = %(schema)s
const CARDS = %(cards)s
const INPUTS = %(inputs)s
const META = %(meta)s

const block = k => '\\n\\n=== MASKED SOURCE (skeleton — translatable German + {Tn} tokens; the COMPLETE and ONLY input; do NOT call tools, do NOT add senses) ===\\n' + INPUTS[k].skeleton + '\\n\\n=== PORTRAIT (evidence: per-sense strata, citations resolved, corpus candidates) ===\\n' + INPUTS[k].portrait

phase('Translate')
async function translateOne(k) {
  const prompt = CONV + '\\n\\n' + TASK + block(k)
  for (let attempt = 0; attempt < 2; attempt++) {
    const card = await agent(prompt, { label: 'tl:' + k + (attempt ? '(retry)' : ''), phase: 'Translate', schema: TLCARD, model: 'sonnet', tools: [] })
    if (card) return { key: k, card }
  }
  return { key: k, card: null }
}
const out = await parallel(CARDS.map(k => () => translateOne(k)))
return { meta: META, results: out }
""" % {
        'root': root,
        'conv': json.dumps(conv, ensure_ascii=True),
        'task': json.dumps(TASK, ensure_ascii=True),
        'schema': json.dumps(TLCARD, ensure_ascii=True),
        'cards': json.dumps(keys),
        'inputs': json.dumps(inputs, ensure_ascii=True),
        'meta': json.dumps(meta, ensure_ascii=True),
    }
    return js, phmaps


def main():
    root, keyfilter = parse_args(sys.argv[1:])
    rootmap, keys = selected_keys(root, keyfilter)
    js, phmaps = build(root, keys, rootmap)
    out_js = os.path.join(REPO, 'src', 'pilot', 'run_pilot_wf.tlonly.js')
    write_text(out_js, js)
    write_text(os.path.join(OUT, 'tlonly_phmaps.json'),
               json.dumps(phmaps, ensure_ascii=False))
    print('wrote', out_js, len(js), 'bytes |', len(keys), 'cards | mode tlonly')


if __name__ == '__main__':
    main()
