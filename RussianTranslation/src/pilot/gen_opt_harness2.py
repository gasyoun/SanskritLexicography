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
        [--selfheal [--selfheal-budget=12]]   # budget = citation-weighted units (1+<ls>) per heal call
        [--binary-split]                      # bisect a failing batch instead of flat-retrying it
        [--output-budget=N]                   # size batches by citation-weighted output, not input bytes
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
from autosplit_requeue import plan as split_plan     # deterministic per-card sense/citation split
sys.path.insert(0, SRC)
from safe_filename import safe_name
from whitney_grammar import grammar_for
from nominal_grammar import nominal_grammar_for

SELFHEAL = False   # --selfheal: on a card the batch can't translate, auto-split it in-harness
                   #  (deterministic split precomputed here) and translate the fragments, then
                   #  stitch back — no manual requeue. Default OFF so existing runs are unchanged.
SELFHEAL_GROUP_BUDGET = 12   # --selfheal-budget=N: fragments are grouped (in document order) into
                   #  this many "citation-weighted units" (1 + <ls> count) per heal agent() call —
                   #  citation count, NOT byte size, drives StructuredOutput complexity, and masking
                   #  already shrinks fragment bytes far below what predicts failure (a dense card's
                   #  own fragments can total <4KB and still be the exact complexity that failed as
                   #  a whole card). A single fragment at/above the budget (e.g. a tier-2 citation
                   #  chunk near autosplit_requeue.LS_BUDGET=18) still gets its own call; several
                   #  light (low-<ls>) fragments share one call, cutting a 13-fragment card to a
                   #  handful of calls instead of 13, without recombining the dense units that
                   #  caused the original failure.
BINARY_SPLIT = False   # --binary-split: when a whole batch call fails/comes back malformed (not
                   #  just individual cards inside it), bisect the still-pending cards into two
                   #  halves and retry each half recursively (own 2-attempt budget each) instead
                   #  of re-submitting the identical full batch — isolates a single poison card
                   #  without re-billing the cards around it. Bottoms out at single cards, which
                   #  fall through to --selfheal as before. Gated: default OFF, behavior-identical
                   #  to the pre-existing retry loop when off.
OUTPUT_BUDGET = None   # --output-budget=N: size the main batches by estimated OUTPUT complexity
                   #  (citation-weighted units, 1 + <ls> count per card — same metric as
                   #  --selfheal-budget) instead of INPUT bytes (skeleton+portrait). Input bytes
                   #  don't predict StructuredOutput failure (TOKEN_LEVER_FINDING_2026-06-30: the
                   #  portrait-slim byte lever was a non-lever); citation density does. None =
                   #  unchanged byte-budget behavior.


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
        elif a == '--selfheal':
            globals()['SELFHEAL'] = True     # gated: default OFF -> existing runs unchanged
        elif a.startswith('--selfheal-budget='):
            globals()['SELFHEAL_GROUP_BUDGET'] = int(a.split('=', 1)[1])
        elif a == '--binary-split':
            globals()['BINARY_SPLIT'] = True
        elif a.startswith('--output-budget='):
            globals()['OUTPUT_BUDGET'] = int(a.split('=', 1)[1])
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


def _group_by_budget(items, sizer, budget):
    """Greedily group `items` (kept in order) into batches whose summed sizer() stays
    <= budget; a single oversize item still gets its own group (never dropped)."""
    groups, cur, sz = [], [], 0
    for it in items:
        isz = sizer(it)
        if cur and sz + isz > budget:
            groups.append(cur); cur, sz = [], 0
        cur.append(it); sz += isz
    if cur:
        groups.append(cur)
    return groups


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
    # BOTH EN and RU paths: keep only the essential per-sense fields required (tag +
    # source german + the translation). The 4 annotator fields (equivalence_type,
    # source_type, stratum, differentia) become optional. On the citation-dense
    # main-head pwg cards, requiring all 7 fields (2 of them enums) per sense —
    # dozens of senses per card — is a huge structured-output surface where one
    # truncated/mismatched field invalidates the whole card and burns the
    # StructuredOutput retry cap (this recovered many dense heads on the EN run).
    # The annotator fields stay best-effort (the model still fills them on most
    # cards; they are re-derivable downstream). validate_final_card_schema.py was
    # relaxed to match, so RU cards with a missing annotator field still validate.
    schema['$defs']['sense']['required'] = ['tag', 'german', field]
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

    # --selfheal: precompute a per-card fragment fallback (deterministic sense/citation split).
    # The JS uses it only for cards the batch could not translate; each fragment is masked here
    # so the in-harness path reuses the same {Tn} restore. Only cards that actually split (>=2
    # fragments) get a fallback; unsplittable cards fall through (the batch retry already tried).
    # Fragments are then GROUPED (by masked-skeleton bytes, document order preserved) into
    # SELFHEAL_GROUP_BUDGET-sized batches, so the JS heal issues one agent() call per GROUP
    # instead of per fragment (a 13-fragment card was costing 13 calls / ~2.2M tok; grouping
    # amortizes the ~30k fixed system-prompt overhead across several fragments per call).
    frags, phf = {}, {}
    if SELFHEAL:
        for k in keys:
            pl = split_plan(read_text(input_paths(k)[0]))
            if len(pl) < 2:
                print('  selfheal: %s has no fallback (card does not split — <2 fragments)' % k)
                continue
            fl = []
            for _si, _pi, t in pl:
                fsk, fph, _ = pwg_mask.mask(t)
                if pwg_mask.restore(fsk, fph) != t:
                    fl = []
                    # loud, not silent: the card will have NO heal fallback at run time,
                    # so a batch failure on it is unrecoverable in-harness
                    print('  selfheal: %s fallback DROPPED (fragment mask round-trip lossy)' % k)
                    break
                fl.append({'skeleton': fsk, 'ls': t.count('<ls'), 'sk': t.count('{#'), 'ph': fph})
            if not fl:
                continue
            groups = _group_by_budget(fl, lambda it: 1 + it['ls'], SELFHEAL_GROUP_BUDGET)
            frags[k] = [[{'skeleton': it['skeleton'], 'ls': it['ls'], 'sk': it['sk']} for it in g]
                        for g in groups]
            phf[k] = [[it['ph'] for it in g] for g in groups]

    # --output-budget=N: size batches by citation-weighted OUTPUT complexity (1 + <ls> per
    # card) instead of input bytes — bytes don't predict StructuredOutput failure (a dense
    # card's masked bytes can be small while its sense/citation count is what blows the
    # retry cap). None (default) keeps the original input-byte budget, byte-identical output.
    if OUTPUT_BUDGET is not None:
        batches = _group_by_budget(keys, lambda k: 1 + inputs[k]['ls'], OUTPUT_BUDGET)
    else:
        batches = _group_by_budget(
            keys, lambda k: len(inputs[k]['skeleton']) + len(inputs[k]['portrait']), budget)

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
        'selfheal': SELFHEAL, 'selfheal_group_budget': SELFHEAL_GROUP_BUDGET if SELFHEAL else None,
        'selfheal_cards': {k: len(v) for k, v in frags.items()} if SELFHEAL else {},
        'binary_split': BINARY_SPLIT, 'output_budget': OUTPUT_BUDGET,
    }

    js = """// AUTO-DERIVED v2 (batched + masked, canonical output) from run_pilot_wf.js - root=%(root)s.
// Several masked cards per agent call; {Tn} restored to source markup in-JS so the
// returned result is a canonical wf_output.json. See TLONLY_PROTOTYPE.md.
export const meta = {
  name: '%(name_prefix)s-opt2-%(root)s',
  description: 'batched+masked translation-only PWG->%(tgt_lang)s; amortized per-call overhead + masked I/O, {Tn} restored in-JS to canonical cards',
  phases: [{ title: 'Translate', detail: '%(gen_label)s: N masked cards per call -> rich cards; {Tn} restored to markup' }],
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
const FRAGS = %(frags)s
const PHF = %(phf)s
const BINARY_SPLIT = %(binary_split)s
const META = %(meta)s

const restore = (t, ph) => (t || '').replace(/\\{T(\\d+)\\}/g, (m, n) => (ph[+n - 1] !== undefined ? ph[+n - 1] : m))
const countOf = (card, re) => { let n = 0; for (const rec of (card.records || [])) for (const s of (rec.senses || [])) n += ((s.german || '').match(re) || []).length; return n }
// Failure ledger: key -> last-known reason a card/fragment is unresolved. Every path that
// nulls a card MUST leave a reason here — a bare null is indistinguishable downstream
// between a hard agent() throw, a fidelity reject, and the model omitting the card,
// which is exactly the ambiguity that made a week of failures undiagnosable. Surfaced
// per-row (results[].error) and in summary.failures.
const FAIL = {}
const noteFail = (k, why) => { FAIL[k] = String(why).slice(0, 300) }
// Masked-token multiset of a text: the {Tn} placeholders it carries, order-insensitive.
// Two texts with equal token multisets restore to identical citation/markup content.
const tokensOf = t => ((t || '').match(/\\{T\\d+\\}/g) || []).sort().join(' ')
const cardTokens = card => { let a = []; for (const rec of (card.records || [])) for (const s of (rec.senses || [])) a = a.concat((s.german || '').match(/\\{T\\d+\\}/g) || []); return a.sort().join(' ') }
// Index a returned cards[] by its self-declared key1 (the prompt requires key1 to echo the
// '=== CARD <key> ===' header). Used to match responses by KEY first, position second —
// positional-only matching silently misassigns every card after an omitted/reordered one.
const byKey1 = cards => { const m = {}; for (const c of cards) if (c && c.key1 !== undefined && !(c.key1 in m)) m[c.key1] = c; return m }
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
  const ls = countOf(c, /<ls\\b/g), sk = countOf(c, /\\{#/g)
  if (ls !== INPUTS[k].ls || sk !== INPUTS[k].sk) {
    noteFail(k, 'fidelity-reject: <ls> ' + ls + '/' + INPUTS[k].ls + ', {# ' + sk + '/' + INPUTS[k].sk)
    return null
  }
  return c
}

// Resolve one heal GROUP (indices into `grp`), trying the whole group up to 3 attempts;
// if it still has >1 unresolved fragment, bisect and resolve each half independently with
// its own fresh 3-attempt budget — this is the safety net a grouped call needs: a live run
// on brU showed a 2-fragment group (ud) fail all 3 attempts and lose BOTH fragments, where
// the pre-grouping one-fragment-per-call design would only have risked one. Bisection falls
// back toward that safer granularity only when a group actually struggles, so the happy path
// (group succeeds) keeps the full cost saving. Returns a {idx: card} map, or null if any
// fragment never resolved even as a singleton.
async function healGroup(k, idxs, grp, label) {
  const resolved = {}
  const fkey = fi => k + '_f' + fi
  // Accept a returned fragment only if its masked-token multiset matches the fragment's
  // skeleton — the heal path previously accepted fragments UNCHECKED (the main path's
  // accept() fidelity guard had no heal-side sibling), so a misaligned/mangled fragment
  // could be stitched into a partial card with no gate downstream reading it.
  const acceptFrag = (c, fi) => {
    if (!c) return false
    if (cardTokens(c) !== tokensOf(grp[fi].skeleton)) {
      noteFail(fkey(fi), 'fragment-fidelity-reject: {Tn} multiset mismatch')
      return false
    }
    resolved[fi] = c
    return true
  }
  let pending = idxs.slice()
  for (let att = 0; att < 3 && pending.length; att++) {
    const blocks = pending.map(i => '\\n\\n=== CARD ' + fkey(i) + ' (fragment ' + (i + 1) + '/' + grp.length + ') ===\\n--- masked German (translatable only; {Tn}=masked span) ---\\n' + grp[i].skeleton).join('')
    const prompt = PREAMBLE + GRAMMAR + CONV_TR + blocks
    const res = await agent(prompt, { label: label + '[' + pending.length + ']' + (att ? '(r' + att + ')' : ''), phase: 'Translate', schema: CARDS_SCHEMA, model: '%(model)s', tools: [] })
    if (res && Array.isArray(res.cards)) {
      const km = byKey1(res.cards)
      // match by echoed key1 first; fall back to position within the pending set
      pending.forEach((fi, idx) => { acceptFrag(km[fkey(fi)] !== undefined ? km[fkey(fi)] : res.cards[idx], fi) })
    } else {
      pending.forEach(fi => noteFail(fkey(fi), res ? 'malformed-response (no cards[])' : 'agent-returned-null'))
    }
    pending = pending.filter(fi => !resolved[fi])
  }
  if (pending.length > 1) {
    const mid = Math.ceil(pending.length / 2)
    // Guard each half independently: an unguarded Promise.all rejects wholesale when one
    // half hard-throws, discarding the OTHER half's already-resolved fragments — the same
    // one-late-failure-wipes-earlier-work class fixed at the selfHeal and translateBatch
    // levels (PR #38/#40), recurring inside the bisection itself.
    const [a, b] = await Promise.all([
      healGroup(k, pending.slice(0, mid), grp, label + '/A').catch(e => { pending.slice(0, mid).forEach(fi => noteFail(fkey(fi), 'heal-hard-failure: ' + (e && e.message || e))); return null }),
      healGroup(k, pending.slice(mid), grp, label + '/B').catch(e => { pending.slice(mid).forEach(fi => noteFail(fkey(fi), 'heal-hard-failure: ' + (e && e.message || e))); return null }),
    ])
    if (a) Object.assign(resolved, a.resolved)
    if (b) Object.assign(resolved, b.resolved)
    pending = pending.filter(fi => !resolved[fi])
  }
  // Partial credit WITHIN the group too: return what resolved plus the exact missing
  // fragment indices — the old contract (null unless ALL fragments resolved) discarded a
  // group's resolved siblings over one stubborn fragment, the same all-or-nothing shape
  // PR #40 removed one level up.
  return { resolved, missing: pending }
}

// --selfheal fallback: a card the batch could not translate is split (deterministically,
// precomputed in FRAGS) into fragments, GROUPED into budget-sized batches (fragment-grouping
// tier), then each group is translated in ONE agent() call (several fragments per call, same
// multi-card-per-prompt pattern as translateBatch) and the fragments' senses are stitched into
// one card. Groups that never resolve (even solo, after healGroup's own bisection) are SKIPPED,
// not fatal to the whole card — a giant flat headword with no rootmap (e.g. large nominal
// stems like kAla/ka/SrI) can need 40+ groups, where requiring every one to succeed drives
// joint success probability toward zero even at a high per-group success rate. A partial
// result (missing_groups > 0) is still returned so downstream sense-coverage gates
// (audit_coverage.py / ru_coverage.py) can measure and flag exactly what's missing — the same
// philosophy the pipeline already uses for partial per-root RU coverage, just applied within
// one oversized card. Only returns null if NOTHING resolved at all. A partial card carries
// partial:true + missing_fragments (exact 'gN:fM' ids) + missing_groups/total_groups so a
// follow-up can requeue JUST the failed pieces instead of re-running the whole card.
async function selfHeal(k) {
  const groups = FRAGS[k]; if (!groups || !groups.length) { noteFail(k, 'no-selfheal-fallback (card did not split or a fragment mask was lossy)'); return null }
  const senses = []
  const missingFragments = []   // 'g<gi+1>:f<fi>' identifiers — persisted on the card so a
                                // targeted requeue of JUST the failed fragments is possible
                                // from wf_output alone (the inline path previously recorded
                                // only a count, making a follow-up a full re-run)
  for (let gi = 0; gi < groups.length; gi++) {
    const grp = groups[gi]
    const gph = (PHF[k] || [])[gi] || []
    // A hard agent() failure inside healGroup (thrown, not returned — see translateBatch's
    // comment) must be caught HERE, per group: uncaught, it unwinds out of this whole loop and
    // discards every earlier group's already-accumulated senses along with it (observed live —
    // 45 agent calls ran, several groups plausibly succeeded, yet the card still came back with
    // ZERO senses because one later group's hard failure wiped the local `senses` array before
    // selfHeal could return anything).
    let r = null
    try { r = await healGroup(k, grp.map((_, i) => i), grp, 'heal:' + k + '#g' + (gi + 1)) }
    catch (e) { r = null; noteFail(k, 'heal-group-hard-failure g' + (gi + 1) + ': ' + (e && e.message || e)) }
    if (!r) { for (let i = 0; i < grp.length; i++) missingFragments.push('g' + (gi + 1) + ':f' + i); continue }
    for (const fi of (r.missing || [])) missingFragments.push('g' + (gi + 1) + ':f' + fi)
    for (let i = 0; i < grp.length; i++) {
      const card = r.resolved[i]
      if (!card) continue
      const ph = gph[i] || []
      for (const rec of (card.records || [])) for (const s of (rec.senses || [])) {
        if (s.german !== undefined) s.german = restore(s.german, ph)
        if (s.%(field)s !== undefined) s.%(field)s = restore(s.%(field)s, ph)
        senses.push(s)
      }
    }
  }
  if (!senses.length) { if (!FAIL[k]) noteFail(k, 'selfheal-nothing-resolved'); return null }
  const stitched = { key1: k, records: [{ senses }] }
  if (!missingFragments.length) {
    // fidelity check only meaningful on a COMPLETE heal — a partial result legitimately has
    // fewer citations than the source. Per-fragment token checks already gated each piece;
    // this whole-card count is the belt over those suspenders.
    if (countOf(stitched, /<ls\\b/g) !== INPUTS[k].ls || countOf(stitched, /\\{#/g) !== INPUTS[k].sk) {
      noteFail(k, 'stitched-fidelity-reject: complete heal, but restored <ls>/{# counts drift from source')
      return null
    }
  } else {
    stitched.partial = true
    stitched.missing_fragments = missingFragments
    stitched.missing_groups = new Set(missingFragments.map(x => x.split(':')[0])).size
    stitched.total_groups = groups.length
    log('heal:' + k + ' partial — ' + missingFragments.length + ' fragment(s) missing (' + missingFragments.join(', ') + ')')
  }
  return stitched
}

phase('Translate')
// Try a group of cards up to 2 full-group attempts, retrying ONLY the cards still
// unresolved (positional within the shrinking pending set) — one missing/garbled card
// must not re-bill the rest. Returns { resolved, pending } (pending = still-unresolved).
// With BINARY_SPLIT off this is the whole retry story (unchanged from before); with it on,
// a group of >1 cards that still fails after 2 attempts is bisected and each half gets its
// own fresh 2-attempt budget — isolates a single poison card instead of re-billing the
// group around it identically on every retry.
async function resolveGroup(pending, label) {
  const resolved = {}
  let cur = pending.slice()
  for (let attempt = 0; attempt < 2 && cur.length; attempt++) {
    // lean mode: NWS_RULE is non-empty and injected only when the batch has an NWS card
    // (full mode: NWS_RULE is '' and the NWS rule already lives inside CONV_TR).
    const nws = (NWS_RULE && cur.some(k => INPUTS[k].nws)) ? ('\\n\\n' + NWS_RULE + '\\n') : ''
    const prompt = PREAMBLE + GRAMMAR + CONV_TR + nws + cur.map(cardBlock).join('')
    const res = await agent(prompt, { label: label + '[' + cur.length + ']' + (attempt ? '(retry)' : ''), phase: 'Translate', schema: CARDS_SCHEMA, model: '%(model)s', tools: [] })
    if (res && Array.isArray(res.cards)) {
      // Match responses by their echoed key1 FIRST, position second. Positional-only
      // matching shifts every card after an omitted/reordered one onto the wrong key;
      // accept()'s count guard catches MOST such shifts, but two cards with equal
      // <ls>/{# counts would swap silently — content under the wrong headword.
      const km = byKey1(res.cards)
      cur.forEach((k, i) => {
        const cand = km[k] !== undefined ? km[k] : res.cards[i]
        if (cand === undefined || cand === null) { noteFail(k, 'missing-from-response'); return }
        const c = accept(cand, k)
        if (c) resolved[k] = c
      })
    } else {
      cur.forEach(k => noteFail(k, res ? 'malformed-response (no cards[])' : 'agent-returned-null'))
    }
    cur = cur.filter(k => !resolved[k])
  }
  if (BINARY_SPLIT && cur.length > 1) {
    const mid = Math.ceil(cur.length / 2)
    // Each half guarded independently — an unguarded Promise.all rejects wholesale on one
    // half's hard throw and discards the other half's resolved cards (see healGroup).
    const empty = h => ({ resolved: {}, pending: h })
    const [a, b] = await Promise.all([
      resolveGroup(cur.slice(0, mid), label + '/A').catch(e => { cur.slice(0, mid).forEach(k => noteFail(k, 'batch-hard-failure: ' + (e && e.message || e))); return empty(cur.slice(0, mid)) }),
      resolveGroup(cur.slice(mid), label + '/B').catch(e => { cur.slice(mid).forEach(k => noteFail(k, 'batch-hard-failure: ' + (e && e.message || e))); return empty(cur.slice(mid)) }),
    ])
    Object.assign(resolved, a.resolved, b.resolved)
    cur = cur.filter(k => !resolved[k])
  }
  return { resolved, pending: cur }
}
async function translateBatch(batch, bi) {
  // A hard agent() failure (e.g. StructuredOutput retry cap exceeded, not just a malformed
  // response our own retry/heal loops already catch) throws instead of returning. Guard
  // resolveGroup AND selfHeal INDEPENDENTLY — a caller that wraps both in one try/catch
  // (as an earlier version of this fix did) swallows a whole-batch failure before --selfheal
  // ever runs, which defeats the fallback for exactly the cards that need it most (observed
  // live: a huge single-card nominal batch hard-failed the main attempt and the heal path,
  // with its precomputed fragment groups, never even got a chance to run). Both paths degrade
  // to "unresolved" on a hard failure — requeue-able, not fatal, and selfHeal still gets tried.
  const resolved = {}, healed = {}
  try {
    let pending = batch.slice()
    try {
      const r = await resolveGroup(batch, 'b' + bi)
      Object.assign(resolved, r.resolved); pending = r.pending
    } catch (e) {
      // fall through to --selfheal below with the full batch still pending
      log('b' + bi + ': whole-batch hard failure (' + (e && e.message || e) + ') — falling through to selfheal')
      batch.forEach(k => noteFail(k, 'batch-hard-failure: ' + (e && e.message || e)))
    }
    // self-healing tier: split-translate-stitch the cards the batch gave up on (no-op unless
    // --selfheal populated FRAGS). Runs only for the few still-failing cards.
    for (const k of pending) {
      let c = null
      try { c = await selfHeal(k) } catch (e) { c = null; noteFail(k, 'selfheal-hard-failure: ' + (e && e.message || e)) }
      if (c) { resolved[k] = c; healed[k] = 1 }
    }
  } catch (e) {
    // ABSOLUTE BACKSTOP — nothing above should throw, but if it does, the batch must
    // still return one row per input key. An uncaught throw here makes parallel() yield
    // null for the whole batch slot, and every key in it VANISHES from the results
    // (save_and_audit.py then drops the null slot on save — the exact silent-loss mode
    // this harness exists to prevent). Cards resolved before the throw are kept.
    batch.forEach(k => { if (!resolved[k] && !FAIL[k]) noteFail(k, 'batch-crash: ' + (e && e.message || e)) })
    log('b' + bi + ': unexpected batch crash (' + (e && e.message || e) + ') — returning accounted rows')
  }
  return batch.map(k => {
    const row = { key: k, card: resolved[k] || null, judge: null, judge_sonnet: null, escalated: !!healed[k] }
    if (!row.card && FAIL[k]) row.error = FAIL[k]
    return row
  })
}
const grouped = await parallel(BATCHES.map((b, i) => () => translateBatch(b, i)))
// TOTAL ACCOUNTING INVARIANT: every selected key appears in `results` exactly once, no
// matter what failed above. parallel() resolves a thrown thunk to null — flat() would
// carry that null into results (crashing the summary below and silently dropping the
// batch's keys at save time). Synthesize accounted null rows for any such batch, then
// backfill any key that STILL isn't present (belt over suspenders).
const out = []
const seen = new Set()
grouped.forEach((rows, i) => {
  if (Array.isArray(rows)) {
    for (const r of rows) if (r && r.key && !seen.has(r.key)) { out.push(r); seen.add(r.key) }
  } else {
    log('b' + i + ': batch thunk resolved null — synthesizing accounted rows for its ' + BATCHES[i].length + ' key(s)')
    for (const k of BATCHES[i]) if (!seen.has(k)) { out.push({ key: k, card: null, judge: null, judge_sonnet: null, escalated: false, error: FAIL[k] || 'batch-thunk-null' }); seen.add(k) }
  }
})
for (const k of META.selected_keys) if (!seen.has(k)) { out.push({ key: k, card: null, judge: null, judge_sonnet: null, escalated: false, error: FAIL[k] || 'unaccounted-key (should be impossible — report this)' }); seen.add(k) }
// Compact summary first so the orchestrator can read counts (ok/null/healed + the exact
// null keys to requeue) WITHOUT parsing the full results blob. results are still carried
// for save_and_audit/promote (the workflow runtime can't write files -> must be returned).
// `failures` maps every null key to its last-known reason; `partial_keys` lists healed
// cards that carry partial:true (usable but incomplete — see missing_fragments on the card).
const _ok = out.filter(r => r.card).length
const _failures = {}
for (const r of out) if (!r.card) _failures[r.key] = r.error || FAIL[r.key] || 'unknown'
const summary = { root: META.root, lang: META.lang, cards: out.length, ok: _ok,
                  null: out.length - _ok, healed: out.filter(r => r.escalated).length,
                  null_keys: out.filter(r => !r.card).map(r => r.key),
                  partial_keys: out.filter(r => r.card && r.card.partial).map(r => r.key),
                  failures: _failures }
return { meta: META, summary, results: out }
""" % {
        'root': root, 'field': field, 'tr': json.dumps(tr, ensure_ascii=True),
        # Language-aware meta + model pin. EN path pins Sonnet 5 explicitly
        # (the bare 'sonnet' alias resolved to 4.6 on a prior run); RU path
        # keeps the 'sonnet' alias unchanged so the autonomous RU runs are untouched.
        'name_prefix': 'pwgen' if lang == 'en' else 'pwgru',
        'tgt_lang': 'English' if lang == 'en' else 'Russian',
        'gen_label': 'Sonnet 5' if lang == 'en' else 'Sonnet',
        'model': 'claude-sonnet-5' if lang == 'en' else 'sonnet',
        'preamble': json.dumps(MASK_PREAMBLE.replace('`russian`', '`%s`' % field), ensure_ascii=True),
        'grammar': json.dumps(single_grammar, ensure_ascii=True),
        'grammars': json.dumps(grammars, ensure_ascii=True),
        'nws': json.dumps(nws_block, ensure_ascii=True),
        'schema': json.dumps(batch_schema, ensure_ascii=True),
        'batches': json.dumps(batches), 'inputs': json.dumps(inputs, ensure_ascii=True),
        'phmaps': json.dumps(phmaps, ensure_ascii=True), 'meta': json.dumps(meta, ensure_ascii=True),
        'frags': json.dumps(frags, ensure_ascii=True), 'phf': json.dumps(phf, ensure_ascii=True),
        'binary_split': json.dumps(BINARY_SPLIT),
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
    # Write LF (not CRLF): the Workflow-tool approval rejects scripts containing
    # raw \r control chars, so a CRLF harness cannot be launched on Windows.
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    mode = ('NOMINAL%s' % ('' if grammar_on else '/no-grammar')) if nominal else (
        'LEAN(rejected)' if lean else 'NWS-GATE' if nws_gate else 'full')
    print('wrote', out, len(js), 'bytes |', len(keys), 'cards in', len(batches), 'batches',
          '(sizes', [len(b) for b in batches], ') | mode', mode)


if __name__ == '__main__':
    main()
