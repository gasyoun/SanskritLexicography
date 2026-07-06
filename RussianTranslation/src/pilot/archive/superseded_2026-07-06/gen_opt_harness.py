#!/usr/bin/env python
"""Generate the BALANCED-tier optimized pwg_ru harness.

Derives from the committed run_pilot_wf.js but rebuilds it as:
  - translate-only (Python gates + sampled semantic judge cover QA),
  - single-turn sparse cards with raw.txt + portrait.json inlined,
  - 1 automatic retry per card on transient API failure.

Usage:  python src/pilot/gen_opt_harness.py <root> [body|headtest] [--keys=k1,k2]
Writes: src/pilot/run_pilot_wf.opt.js, or run_pilot_wf.headtest.js for headtest.
"""
import datetime
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from window_common import INP, REPO, SRC, input_paths, load_json, read_text, rootmap_path, sha256_file, write_text

sys.path.insert(0, SRC)
from safe_filename import safe_name

GENERATOR_VERSION = 'gen_opt_harness.v2.provenance-no-tools'
DENSE_LS = 30


def die(message):
    sys.exit('FAIL: %s' % message)


def check(condition, message):
    if not condition:
        die(message)


def parse_args(argv):
    root = argv[0] if argv else 'tyaj'
    mode = argv[1] if len(argv) > 1 and not argv[1].startswith('--') else 'body'
    check(mode in ('body', 'headtest'), 'mode must be body or headtest, got %r' % mode)
    keyfilter = None
    for arg in argv[1:]:
        if arg.startswith('--keys='):
            keyfilter = set(filter(None, arg.split('=', 1)[1].split(',')))
    return root, mode, keyfilter


def selected_keys(root, mode, keyfilter):
    path, _stem = rootmap_path(root)
    check(path, 'no rootmap for %r under %s' % (root, INP))
    rm = load_json(path)
    subs = rm.get('sub_cards') or []
    keys = [s['subkey'] for s in subs]
    if mode == 'headtest':
        heads = [s['subkey'] for s in subs
                 if s.get('hom') == 0 and s.get('kind') == 'head'
                 and (s.get('section') == 'pwg00'
                      or str(s.get('section', '')).startswith('pwg00b'))]
        if not heads:
            heads = [s['subkey'] for s in subs
                     if s.get('hom') == 0 and s.get('kind') == 'head']
        keys = heads[:1] or keys[:1]
    if keyfilter:
        keys = [k for k in keys if k in keyfilter or k.split('~~')[-1] in keyfilter]
        check(keys, 'no sub-cards matched --keys=%s' % sorted(keyfilter))
    return path, keys


def inline_inputs(keys):
    inputs, dense, input_hashes = {}, [], {}
    for key in keys:
        raw_path, portrait_path = input_paths(key)
        check(os.path.exists(raw_path), 'missing raw input %s' % raw_path)
        check(os.path.exists(portrait_path), 'missing portrait input %s' % portrait_path)
        raw = read_text(raw_path)
        portrait = read_text(portrait_path)
        inputs[key] = {'raw': raw, 'portrait': portrait}
        input_hashes[key] = {
            'raw_sha256': sha256_file(raw_path),
            'portrait_sha256': sha256_file(portrait_path),
        }
        if raw.count('<ls') > DENSE_LS:
            dense.append(key)
    return inputs, dense, input_hashes


def replace_once(src, pattern, repl, label, flags=0):
    updated, count = re.subn(pattern, repl, src, flags=flags)
    check(count == 1, '%s replacement count was %d, expected 1' % (label, count))
    return updated


def build_harness(root, mode, keys, rootmap, inputs, dense, input_hashes):
    src = read_text(os.path.join(REPO, 'src', 'pilot', 'run_pilot_wf.js'))
    schema = read_text(os.path.join(REPO, 'schemas', 'pwg_ru_final_card.schema.json')).rstrip()
    meta = {
        'schema_version': 'pwg_ru.workflow_meta.v1',
        'generator': GENERATOR_VERSION,
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec='seconds').replace('+00:00', 'Z'),
        'root': root,
        'safe_root': safe_name(root),
        'mode': mode,
        'selected_keys': keys,
        'rootmap_sha256': sha256_file(rootmap),
        'input_hashes': input_hashes,
    }

    src = re.sub(r"^import .*\n", "", src, count=3, flags=re.M)
    src = replace_once(
        src,
        r"const HERE = dirname\(fileURLToPath\(import\.meta\.url\)\)\n"
        r"const FINAL_CARD_SCHEMA = JSON\.parse\(readFileSync\(join\(HERE, '\.\.', '\.\.', 'schemas', 'pwg_ru_final_card\.schema\.json'\), 'utf-8'\)\)\n",
        lambda _m: "const FINAL_CARD_SCHEMA = " + schema + "\n",
        'schema block')

    cards_block = (f"// OPTIMIZED (balanced): all {len(keys)} sub-cards of giant root {root}, "
                   f"single-turn inlined inputs, translate-only.\n"
                   "const CARDS = " + json.dumps(keys) + "\n"
                   "const INPUTS = " + json.dumps(inputs, ensure_ascii=True) + "\n"
                   "const META = " + json.dumps(meta, ensure_ascii=True) + "\n")
    src = replace_once(src, r"const SECTION = 'a'.*?\n\}\n", lambda _m: cards_block,
                       'CARDS block', flags=re.DOTALL)

    head_dir = ('\n\n=== THIS IS A CITATION-DENSE ROOT-HEAD CARD ===\n'
                'It packs many <ls> source citations per sense. You MUST reproduce EVERY '
                '<ls>...</ls> and EVERY {#...#} Sanskrit span VERBATIM - do NOT abridge, '
                'sample, or summarize the citation lists ("u.s.w." is only allowed where the '
                'SOURCE itself prints it). Losing citations fails the card.')

    if mode == 'headtest':
        tail = """phase('Translate')
const HEAD_DIR = HEAD_DIR_CONST
const fileBlock = k => '\\n\\n=== SOURCE (inlined - this is the COMPLETE and ONLY input for this card. Do NOT call any tools, do NOT read other files, do NOT add senses, sub-senses, or citations from memory or from sibling head-parts. Translate EXACTLY the senses that appear below, nothing more, nothing less) ===\\n--- ' + fileOf(k) + '.raw.txt ---\\n' + INPUTS[k].raw + '\\n--- ' + fileOf(k) + '.portrait.json ---\\n' + INPUTS[k].portrait
async function translateOne(k) {
  const prompt = TR.replace(/KEYFILE/g, fileOf(k)).replace(/KEY/g, k) + fileBlock(k) + HEAD_DIR
  for (let attempt = 0; attempt < 2; attempt++) {
    const card = await agent(prompt, { label: 'tr-head:' + k + (attempt ? '(retry)' : ''), phase: 'Translate', schema: CARD, model: 'sonnet', tools: [] })
    if (card) return { key: k, card, judge: null, judge_sonnet: null, escalated: false }
  }
  return { key: k, card: null, judge: null, judge_sonnet: null, escalated: false }
}
const out = await parallel(CARDS.map(k => () => translateOne(k)))
return { meta: META, results: out }
""".replace('HEAD_DIR_CONST', json.dumps(head_dir))
    else:
        tail = ("""phase('Translate')
const DENSE = new Set(DENSE_CONST)
const HEAD_DIR = HEAD_DIR_CONST
const fileBlock = k => '\\n\\n=== SOURCE (inlined - this is the COMPLETE and ONLY input for this card. Do NOT call any tools, do NOT read other files, do NOT add senses, sub-senses, or citations from memory or from sibling head-parts. Translate EXACTLY the senses that appear below, nothing more, nothing less) ===\\n--- ' + fileOf(k) + '.raw.txt ---\\n' + INPUTS[k].raw + '\\n--- ' + fileOf(k) + '.portrait.json ---\\n' + INPUTS[k].portrait
async function translateOne(k) {
  const dense = DENSE.has(k)
  const base = TR.replace(/KEYFILE/g, fileOf(k)).replace(/KEY/g, k)
  const prompt = dense ? (base + fileBlock(k) + HEAD_DIR) : (base + fileBlock(k))
  for (let attempt = 0; attempt < 2; attempt++) {
    const card = await agent(prompt, { label: (dense ? 'tr-dense:' : 'tr:') + k + (attempt ? '(retry)' : ''), phase: 'Translate', schema: CARD, model: 'sonnet', tools: [] })
    if (card) return { key: k, card, judge: null, judge_sonnet: null, escalated: false }
  }
  return { key: k, card: null, judge: null, judge_sonnet: null, escalated: false }
}
const out = await parallel(CARDS.map(k => () => translateOne(k)))
return { meta: META, results: out }
""".replace('DENSE_CONST', json.dumps(dense))
           .replace('HEAD_DIR_CONST', json.dumps(head_dir)))

    src = replace_once(src, r"phase\('Translate'\)\n.*$", lambda _m: tail,
                       'pipeline tail', flags=re.DOTALL)

    if mode != 'headtest':
        src = src.replace(
            'INPUTS for headword KEY (read both):',
            'INPUTS for headword KEY (reproduced INLINE below as the COMPLETE input - do NOT open files, do NOT call any tools, do NOT supply senses from memory):')

    src = src.replace("name: 'pwgru-pilot-a-section',", f"name: 'pwgru-opt-{root}',")
    for bad in ["readFileSync", "fileURLToPath", "import.meta", "console.error", "dirname("]:
        check(bad not in src, "residual node-ism: %s" % bad)
    agent_calls = len(re.findall(r'\bagent\(prompt,\s*\{', src))
    tool_guards = src.count('tools: []')
    check(agent_calls == tool_guards,
          'translate agent tools guard mismatch: %d agent calls, %d tools guards' %
          (agent_calls, tool_guards))
    check('const META = ' in src and 'return { meta: META, results: out }' in src,
          'workflow provenance meta missing')

    return (f"// AUTO-DERIVED (optimized/balanced) from src/pilot/run_pilot_wf.js - root={root}.\n"
            "// Translate-only, single-turn inlined inputs, 1 retry. Judge = free Python gates\n"
            "// (audit_window.py) on 100%, LLM-judge a 10% sample separately.\n"
            "// See TOKEN_OPTIMIZATION_2026-06-27.md.\n" + src)


def main(argv=None):
    root, mode, keyfilter = parse_args(list(sys.argv[1:] if argv is None else argv))
    rootmap, keys = selected_keys(root, mode, keyfilter)
    inputs, dense, input_hashes = inline_inputs(keys)
    src = build_harness(root, mode, keys, rootmap, inputs, dense, input_hashes)
    out = os.path.join(REPO, 'src', 'pilot',
                       'run_pilot_wf.headtest.js' if mode == 'headtest'
                       else 'run_pilot_wf.opt.js')
    write_text(out, src)
    print("wrote", out, len(src), "bytes |", len(keys), "cards | mode", mode)


if __name__ == '__main__':
    main()
