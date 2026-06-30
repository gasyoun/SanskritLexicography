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

Usage:  python src/pilot/gen_opt_harness2.py <root> [--keys=k1,k2] [--budget=12000] [--out=PATH]
Writes: src/pilot/run_pilot_wf.opt2.js  (or --out=PATH — use a per-root/per-chat path to
        avoid the gen->copy race when several chats generate harnesses concurrently)
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
from nominal_grammar import nominal_grammar_for


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


def nominal_grammar_text(slp1, lex):
    """Compact nominal grammar block for a non-root headword, injected once per batch.

    Parallel to grammar_text() for verb roots. Returns an empty string if lex is
    unknown/missing. For compounds, includes MW member segmentation.
    """
    if not slp1 or not lex:
        return ''
    try:
        rec = nominal_grammar_for(slp1, lex)
    except Exception:
        return ''
    lines = ['=== GRAMMAR (Whitney nominal) — the headword\'s declension class and §§; '
             'use to inform grammatical notes and flag irregular forms; '
             'NEVER let grammar override a corpus- or German-attested sense ===']
    lines.append('headword %s [%s]: %s, Whitney %s (paradigm %s)'
                 % (slp1, lex, rec['stem_class'],
                    rec['declension_sections'], rec.get('paradigm_section') or '—'))
    if rec.get('compound_members'):
        lines.append('  compound members (MW k2): %s → %s'
                     % (slp1, ' + '.join(rec['compound_members'])))
        lines.append('  compound formation: %s' % rec['compound_sections'])
    if rec.get('irregularities'):
        lines.append('  flags: %s' % '; '.join(rec['irregularities']))
    lines.append('  derivation ref: %s' % rec['derivation_sections'])
    return '\n'.join(lines) + '\n\n'


def die(msg):
    sys.exit('FAIL: %s' % msg)


def parse_args(argv):
    if not argv:
        die('usage: gen_opt_harness2.py <root> [--keys=..] [--budget=N] [--lean] '
            '[--nominal] [--no-grammar]')
    # budget = bytes (skeleton+portrait) packed per agent call. Higher = fewer agent calls =
    # fewer ~30k-token fixed-framework payments per root (the dominant cost). 12000 measured
    # ~-25% agent calls vs the old 9000 while keeping batches within the tested 13-14-card range;
    # the post-restore fidelity guard nulls any degraded card -> requeue, so it can't silently
    # corrupt. Further bumps (16-18k) are available but should be retry-rate-validated on a Max
    # run first. See TOKEN_LEVER_FINDING_2026-06-30.md (portrait-slim was a non-lever).
    root, keyfilter, budget, lean, nws_gate = argv[0], None, 12000, False, False
    nominal, grammar_on = False, True
    keylist = None                     # ordered keys (nominal mode preserves order)
    out_path = None                    # --out=PATH overrides the default opt2.js (avoids the
    lang, mw_tm = 'ru', None           # --lang en + --mw-tm=PATH: PWG->English pilot (MG 2026-06-30)
    for a in argv[1:]:                 # gen->copy race when several chats generate at once)
        if a.startswith('--keys='):
            keylist = [k for k in a.split('=', 1)[1].split(',') if k]
            keyfilter = set(keylist)
        elif a.startswith('--budget='):
            budget = int(a.split('=', 1)[1])
        elif a.startswith('--out='):
            out_path = a.split('=', 1)[1]
        elif a.startswith('--lang='):
            lang = a.split('=', 1)[1].strip().lower()
        elif a.startswith('--mw-tm='):
            mw_tm = a.split('=', 1)[1]
        elif a == '--lean':
            lean = True
        elif a == '--nws-gate':
            nws_gate = True
        elif a == '--nominal':
            nominal = True
        elif a == '--no-grammar':
            grammar_on = False
    if lang not in ('ru', 'en'):
        die('unknown --lang %r (ru|en)' % lang)
    if lang == 'en' and mw_tm is None:
        mw_tm = os.path.join(SRC, 'mw_en_tm.json')      # default MW translation-memory feed
    return root, keyfilter, keylist, budget, lean, nws_gate, nominal, grammar_on, out_path, lang, mw_tm


def extract_nws(tr):
    """Pull HARD RULE 5 (the long NWS owner-map block) out of TR so the JS injects it only
    into NWS-bearing batches. SAFE — does not touch the markup-fidelity rule. (rule3 intact)"""
    nws_m = re.search(r'5\. NWS LAYER.*?(?=\n\nRENDERING GUIDANCE)', tr, re.S)
    if not nws_m:
        die('could not locate HARD RULE 5 (NWS) block')
    nws_block = nws_m.group(0)
    tr2 = tr.replace(nws_block, '5. NWS LAYER — present only for NWS sub-source cards; '
                     'when an NWS owner-map block appears in a card, follow its rule shown there.')
    return tr2, nws_block


def compress_rule3(tr):
    """Compress HARD RULE 3 (markup-verbatim) to a {Tn}-verbatim line. REJECTED by the A/B
    (regressed markup fidelity — AB_TEST_LEAN_TR.md); kept only behind --lean for the record."""
    tr2, n = re.subn(
        r'3\. SIGLA UNTOUCHED.*?(?=\n4\. ALL RECORDS)',
        '3. KEEP {Tn} VERBATIM — every untranslatable span (Sanskrit, sigla, abbreviations) is '
        'masked as a {Tn} placeholder; keep every {Tn} unchanged and in its original order, and '
        'never type any Sanskrit, siglum, or markup yourself (Python restores them).\n',
        tr, count=1, flags=re.S)
    if n != 1:
        die('could not compress HARD RULE 3 (markup-verbatim) block')
    return tr2


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


# POS priority shared with enrich_portrait_nominal_grammar (prefer concrete gender).
_GENDER_PRIORITY = ('m.', 'f.', 'n.', 'm.n.', 'm.f.', 'f.n.', 'm.f.n.',
                    'adj.', 'adv.', 'indecl.', 'ind.', 'interj.')


def _slp1_lex_for_key(k):
    """Read (SLP1 key1, lex tag) from a card's portrait JSON.

    The card key `k` is a safe-name FILE stem (input files are stored under
    safe_name(SLP1); input_paths uses the literal stem). The true SLP1 — needed
    for the compound join and the grammar display — is the portrait's `key1`
    field, NOT the mangled stem. Returns ('', '') if the portrait is unreadable.
    """
    _, pp = input_paths(k)
    try:
        port = load_json(pp)
    except Exception:
        return '', ''
    e = port[0] if isinstance(port, list) and port else port
    slp1 = e.get('key1') or e.get('slp1') or ''
    val = e.get('lex') or e.get('pos') or e.get('gender') or ''
    if isinstance(val, (list, tuple)):
        tags = [str(t).strip() for t in val if str(t).strip()]
        lex = next((g for g in _GENDER_PRIORITY if g in tags), tags[0] if tags else '')
    else:
        lex = str(val).strip()
    return slp1, lex


def _card_grammar_text(k):
    """Per-card nominal grammar block, keyed by the portrait's true SLP1 (key1)."""
    slp1, lex = _slp1_lex_for_key(k)
    return nominal_grammar_text(slp1, lex)


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


def _rename_sense_field(schema, old, new):
    """Deep-copy the card schema with the per-sense translation field renamed (russian->
    english) wherever it appears in `properties` / `required`. Used for the --lang en path."""
    import copy
    s = copy.deepcopy(schema)

    def walk(d):
        if isinstance(d, dict):
            props = d.get('properties')
            if isinstance(props, dict) and old in props:
                props[new] = props.pop(old)
            req = d.get('required')
            if isinstance(req, list) and old in req:
                d['required'] = [new if x == old else x for x in req]
            for v in d.values():
                walk(v)
        elif isinstance(d, list):
            for x in d:
                walk(x)
    walk(s)
    return s


def mw_tm_block(root, mw_tm_path):
    """The MW English translation-memory block injected once per root (en pilot). '' if none."""
    if not mw_tm_path or not os.path.exists(mw_tm_path):
        return ''
    tm = load_json(mw_tm_path).get(root)
    if not tm:
        return ''
    return ('=== MW REFERENCE (English translation memory — Monier-Williams\' own glosses for '
            'this root; candidate vocabulary, ADJUDICATE against the German + corpus, follow '
            'PWG\'s sense order, do not copy blindly) ===\n%s\n\n' % tm)


def build(root, keys, rootmap, budget, lean=False, nws_gate=False,
          nominal=False, grammar_on=True, lang='ru', mw_tm_path=None):
    field = 'english' if lang == 'en' else 'russian'   # the per-sense translation field
    nws_block = ''
    if lang == 'en':
        # PWG->English pilot: a self-contained EN prompt (tr_en.txt). The masked-inline
        # regime + field mechanics are carried by MASK_PREAMBLE (no file-reading block to
        # neutralize, no lean/nws variants — full mode only).
        tr = read_text(os.path.join(REPO, 'src', 'pilot', 'tr_en.txt'))
    else:
        conv = conv_text()
        tr = extract_conv_tr().replace('${CONV}', conv)
        # CRITICAL: the production TR tells the model "INPUTS for headword KEY (read both):
        # KEYFILE.raw.txt / .portrait.json" — i.e. to READ files. In the masked-inline regime
        # that makes the model call file tools and list the input dir (the yuj retry/cost blowup,
        # 2026-06-29). Strip it so the only inputs are the inlined masked cards.
        tr, n = re.subn(
            r'INPUTS for headword KEY \(read both\):.*?\.portrait\.json[^\n]*',
            'INPUTS for each headword are INLINED below per card (its masked German skeleton + '
            'portrait). Do NOT open files, do NOT call any tools, do NOT list directories, do NOT '
            'supply senses from memory — translate EXACTLY what is inlined, nothing else.',
            tr, count=1, flags=re.S)
        if n != 1:
            die('could not neutralize the TR file-reading block (expected 1 match, got %d)' % n)
        # A/B variants. --nws-gate: safe (rule 3 kept, only NWS gated). --lean: also compresses
        # rule 3 (REJECTED — regressed fidelity; kept for the record only).
        if lean:
            tr = compress_rule3(tr)
            tr, nws_block = extract_nws(tr)
        elif nws_gate:
            tr, nws_block = extract_nws(tr)
    schema = load_json(os.path.join(REPO, 'schemas', 'pwg_ru_final_card.schema.json'))
    if field != 'russian':
        schema = _rename_sense_field(schema, 'russian', field)
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
                     'ls': raw.count('<ls'), 'sk': raw.count('{#'),
                     'nws': 1 if 'NWS' in raw else 0}
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

    # Grammar injection. Root mode: one shared GRAMMAR block (the root conjugation,
    # identical across sub-cards) before CONV_TR; GRAMMARS empty. Nominal mode: each
    # headword has its OWN block (distinct stem class / compound members), so inject
    # PER CARD via GRAMMARS and leave the shared block empty. --no-grammar = arm A.
    if nominal:
        single_grammar = ''
        grammars = {k: _card_grammar_text(k) for k in keys} if grammar_on else {}
    else:
        single_grammar = grammar_text(root) if grammar_on else ''
        grammars = {}
    if lang == 'en':                                    # inject MW TM once per root (root mode)
        single_grammar = mw_tm_block(root, mw_tm_path) + single_grammar

    meta = {
        'schema_version': 'pwg_ru.workflow_meta.v1', 'generator': 'gen_opt_harness2.batched-masked',
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec='seconds').replace('+00:00', 'Z'),
        'root': root, 'safe_root': safe_name(root), 'lang': lang,
        'mode': 'nominal_masked' if nominal else 'batched_masked',
        'grammar_layer': ('nominal' if nominal else 'root') if grammar_on else 'none',
        'selected_keys': keys, 'batches': batches, 'batch_count': len(batches),
        'rootmap_sha256': sha256_file(rootmap) if rootmap else None,
        'input_hashes': input_hashes,
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
const GRAMMARS = %(grammars)s
const NWS_RULE = %(nws)s
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
    if (s.%(field)s !== undefined) s.%(field)s = restore(s.%(field)s, ph)
  }
  return card
}
// Per-card grammar (nominal mode): each headword carries its own block. Empty in root
// mode (the shared GRAMMAR is injected once before CONV_TR) and in the --no-grammar arm.
const cardBlock = k => (GRAMMARS[k] || '') + '\\n\\n=== CARD ' + k + ' ===\\n--- masked German (translatable only; {Tn}=masked span) ---\\n' + INPUTS[k].skeleton + '\\n--- portrait (evidence) ---\\n' + INPUTS[k].portrait

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
    // lean mode: NWS_RULE is non-empty and injected only when the batch has an NWS card
    // (full mode: NWS_RULE is '' and the NWS rule already lives inside CONV_TR).
    const nws = (NWS_RULE && pending.some(k => INPUTS[k].nws)) ? ('\\n\\n' + NWS_RULE + '\\n') : ''
    const prompt = PREAMBLE + GRAMMAR + CONV_TR + nws + pending.map(cardBlock).join('')
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
        'root': root, 'field': field, 'tr': json.dumps(tr, ensure_ascii=True),
        'preamble': json.dumps(MASK_PREAMBLE.replace('`russian`', '`%s`' % field), ensure_ascii=True),
        'grammar': json.dumps(single_grammar, ensure_ascii=True),
        'grammars': json.dumps(grammars, ensure_ascii=True),
        'nws': json.dumps(nws_block, ensure_ascii=True),
        'schema': json.dumps(batch_schema, ensure_ascii=True),
        'batches': json.dumps(batches), 'inputs': json.dumps(inputs, ensure_ascii=True),
        'phmaps': json.dumps(phmaps, ensure_ascii=True), 'meta': json.dumps(meta, ensure_ascii=True),
    }
    for bad in ['readFileSync', 'fileURLToPath', 'import.meta']:
        if bad in js:
            die('residual node-ism: %s' % bad)
    return js, batches


def main():
    root, keyfilter, keylist, budget, lean, nws_gate, nominal, grammar_on, out_path, lang, mw_tm = parse_args(sys.argv[1:])
    if nominal:
        # No rootmap: the headword keys ARE the cards, in the order given.
        if not keylist:
            die('--nominal requires an explicit --keys=k1,k2,... list')
        rootmap, keys = None, keylist
    else:
        rootmap, keys = selected_keys(root, keyfilter)
        if keylist:
            keys = [k for k in keylist if k in set(keys)]
    js, batches = build(root, keys, rootmap, budget, lean, nws_gate, nominal, grammar_on, lang, mw_tm)
    out = os.path.abspath(out_path) if out_path else os.path.join(REPO, 'src', 'pilot', 'run_pilot_wf.opt2.js')
    write_text(out, js)
    mode = ('NOMINAL%s' % ('' if grammar_on else '/no-grammar')) if nominal else (
        'LEAN(rejected)' if lean else 'NWS-GATE' if nws_gate else 'full')
    print('wrote', out, len(js), 'bytes |', len(keys), 'cards in', len(batches), 'batches',
          '(sizes', [len(b) for b in batches], ') | mode', mode)


if __name__ == '__main__':
    main()
