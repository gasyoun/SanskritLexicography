"""Generate the BALANCED-tier optimized pwg_ru harness (TOKEN_OPTIMIZATION_2026-06-27.md).

Derives from the committed run_pilot_wf.js but rebuilds it as:
  - translate-ONLY (no per-card LLM judge; the free Python gates + a separate
    sampled judge cover QA),
  - SINGLE-TURN: each sub-card's raw.txt + portrait.json are inlined into the
    prompt and the agent is told to call NO tools -> kills the 11-22 turn /
    4-12 Read cache_read explosion (Finding 1/2),
  - 1 automatic RETRY per card on transient API failure (Finding 4).

Usage:  python make_workflow_opt.py <root>      # e.g. tyaj
Writes: src/pilot/run_pilot_wf.opt.js
"""
import re, sys, json, os
sys.stdout.reconfigure(encoding='utf-8')
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
IN = base + r'\src\pilot\input'
src = open(base + r'\src\pilot\run_pilot_wf.js', encoding='utf-8').read()
schema = open(base + r'\schemas\pwg_ru_final_card.schema.json', encoding='utf-8').read().rstrip()

root = sys.argv[1] if len(sys.argv) > 1 else 'tyaj'
mode = sys.argv[2] if len(sys.argv) > 2 else 'body'   # 'body' = single-turn inlined; 'headtest' = 1 head, multi-turn, no-abridge
# The splitter writes rootmaps under the reversible safe-name stem (e.g. sTA -> s_t_a),
# while sub-card subkeys inside are already safe stems. Resolve the rootmap by safe
# name; fall back to the raw name so ASCII roots (tyaj, gam) keep working unchanged.
sys.path.insert(0, base + r'\src')
from safe_filename import safe_name
_rootmap = f'{IN}\\{safe_name(root)}.rootmap.json'
if not os.path.exists(_rootmap):
    _rootmap = f'{IN}\\{root}.rootmap.json'
rm = json.load(open(_rootmap, encoding='utf-8'))
keys = [s['subkey'] for s in rm['sub_cards']]
if mode == 'headtest':
    # keep only the densest head (homonym-0 head part)
    heads = [k for k in keys if k.endswith('_pwg00') and '~~h0_' in k]
    keys = heads[:1] or keys[:1]

# inline each card's two source files; classify by citation density
DENSE_LS = 30   # >30 <ls> in raw → citation-dense → multi-turn + no-abridge lane
INPUTS, DENSE = {}, []
for k in keys:
    raw = open(f'{IN}\\{k}.raw.txt', encoding='utf-8').read()
    por = open(f'{IN}\\{k}.portrait.json', encoding='utf-8').read()
    INPUTS[k] = {'raw': raw, 'portrait': por}
    if raw.count('<ls') > DENSE_LS:
        DENSE.append(k)

# 1) strip node imports
src = re.sub(r"^import .*\n", "", src, count=3, flags=re.M)

# 2) inline schema (drop HERE + readFileSync)
src, n = re.subn(
    r"const HERE = dirname\(fileURLToPath\(import\.meta\.url\)\)\n"
    r"const FINAL_CARD_SCHEMA = JSON\.parse\(readFileSync\(join\(HERE, '\.\.', '\.\.', 'schemas', 'pwg_ru_final_card\.schema\.json'\), 'utf-8'\)\)\n",
    (lambda _m: "const FINAL_CARD_SCHEMA = " + schema + "\n"), src)
assert n == 1, f"schema block ({n})"

# 3) CARDS + inlined INPUTS, in place of the SECTION/manifest block
cards_block = (f"// OPTIMIZED (balanced): all {len(keys)} sub-cards of giant root {root}, "
               f"single-turn inlined inputs, translate-only.\n"
               "const CARDS = " + json.dumps(keys) + "\n"
               "const INPUTS = " + json.dumps(INPUTS, ensure_ascii=True) + "\n")
src, n = re.subn(r"const SECTION = 'a'.*?\n\}\n", (lambda _m: cards_block), src, flags=re.DOTALL)
assert n == 1, f"CARDS block ({n})"

# head no-abridge directive (appended to the translate prompt for head cards)
HEAD_DIR = ('\n\n=== THIS IS A CITATION-DENSE ROOT-HEAD CARD ===\n'
            'It packs many <ls> source citations per sense. You MUST reproduce EVERY '
            '<ls>...</ls> and EVERY {#...#} Sanskrit span VERBATIM — do NOT abridge, '
            'sample, or summarize the citation lists ("u.s.w." is only allowed where the '
            'SOURCE itself prints it). Losing citations fails the card.')

if mode == 'headtest':
    # multi-turn (agent reads its own files) + no-abridge directive, translate-only, 1 retry
    tail = """phase('Translate')
async function translateOne(k) {
  const prompt = TR.replace(/KEYFILE/g, fileOf(k)).replace(/KEY/g, k) + HEAD_DIR_CONST
  for (let attempt = 0; attempt < 2; attempt++) {
    const card = await agent(prompt, { label: 'tr-head:' + k + (attempt ? '(retry)' : ''), phase: 'Translate', schema: CARD, model: 'sonnet' })
    if (card) return { key: k, card, judge: null, judge_sonnet: null, escalated: false }
  }
  return { key: k, card: null, judge: null, judge_sonnet: null, escalated: false }
}
const out = await parallel(CARDS.map(k => () => translateOne(k)))
return { results: out }
""".replace('HEAD_DIR_CONST', json.dumps(HEAD_DIR))
else:
    # PRODUCTION dual-lane, translate-only, 1 retry, NO routine LLM judge.
    #  - sparse cards  -> single-turn, inputs inlined, no tools  (cheap)
    #  - dense cards   -> multi-turn, read own files, no-abridge directive (heads etc.)
    tail = ("""phase('Translate')
const DENSE = new Set(DENSE_CONST)
const HEAD_DIR = HEAD_DIR_CONST
const fileBlock = k => '\\n\\n=== SOURCE (inlined — this is the COMPLETE and ONLY input for this card. Do NOT call any tools, do NOT read other files, do NOT add senses, sub-senses, or citations from memory or from sibling head-parts. Translate EXACTLY the senses that appear below, nothing more, nothing less) ===\\n--- ' + fileOf(k) + '.raw.txt ---\\n' + INPUTS[k].raw + '\\n--- ' + fileOf(k) + '.portrait.json ---\\n' + INPUTS[k].portrait
async function translateOne(k) {
  const dense = DENSE.has(k)
  const base = TR.replace(/KEYFILE/g, fileOf(k)).replace(/KEY/g, k)
  // BOTH lanes inline (single-turn, no file roaming -> no sense over-production).
  // dense cards additionally get the no-abridge directive to keep every citation.
  const prompt = dense ? (base + fileBlock(k) + HEAD_DIR) : (base + fileBlock(k))
  for (let attempt = 0; attempt < 2; attempt++) {
    const card = await agent(prompt, { label: (dense ? 'tr-dense:' : 'tr:') + k + (attempt ? '(retry)' : ''), phase: 'Translate', schema: CARD, model: 'sonnet' })
    if (card) return { key: k, card, judge: null, judge_sonnet: null, escalated: false }
  }
  return { key: k, card: null, judge: null, judge_sonnet: null, escalated: false }
}
const out = await parallel(CARDS.map(k => () => translateOne(k)))
return { results: out }
""".replace('DENSE_CONST', json.dumps(DENSE))
   .replace('HEAD_DIR_CONST', json.dumps(HEAD_DIR)))
src, n = re.subn(r"phase\('Translate'\)\n.*$", (lambda _m: tail), src, flags=re.DOTALL)
assert n == 1, f"pipeline tail ({n})"

# soften the TR "(read both)" cue: sparse cards have inputs inlined; dense cards open the files.
if mode != 'headtest':
    src = src.replace('INPUTS for headword KEY (read both):',
                      'INPUTS for headword KEY (reproduced INLINE below as the COMPLETE input — do NOT open files, do NOT call any tools, do NOT supply senses from memory):')

# meta: mark optimized
src = src.replace("name: 'pwgru-pilot-a-section',", f"name: 'pwgru-opt-{root}',")

for bad in ["readFileSync", "fileURLToPath", "import.meta", "console.error", "dirname("]:
    assert bad not in src, f"residual node-ism: {bad}"

src = (f"// AUTO-DERIVED (optimized/balanced) from src/pilot/run_pilot_wf.js — root={root}.\n"
       "// Translate-only, single-turn inlined inputs, 1 retry. Judge = free Python gates\n"
       "// (run_real_test.py audit + audit_translation.py) on 100%, LLM-judge a 10% sample\n"
       "// separately. See TOKEN_OPTIMIZATION_2026-06-27.md.\n" + src)

out = base + (r'\src\pilot\run_pilot_wf.headtest.js' if mode == 'headtest' else r'\src\pilot\run_pilot_wf.opt.js')
open(out, 'w', encoding='utf-8').write(src)
print("wrote", out, len(src), "bytes |", len(keys), "cards | mode", mode)
