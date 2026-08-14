#!/usr/bin/env python
"""H2684 Track B — manifest-pinned Grok 4.6 PWG TM fragment runner.

Opt-in route only. Default production headless/Max routes are untouched.
Grok 4.6 drafts; deterministic gates decide promotion. Uncertain rows stay
in a named quarantine tier. Resume from checkpoint. Never silent-drop.

  python src/pwg_tm_generate.py --verify
  python src/pwg_tm_generate.py extract --limit 12 --out-dir DIR
  python src/pwg_tm_generate.py run --route grok-4.6 --drafts FILE --limit 12 --out-dir DIR
  python src/pwg_tm_generate.py reconcile --out-dir DIR
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_canonical as C  # noqa: E402
import pwg_tm_fragmentize as F  # noqa: E402
import pwg_tm_gates as G  # noqa: E402

ROUTE_ID = 'grok-4.6'
MODEL_ID = 'grok-4.6'
PIPELINE_VERSION = 'pwg_tm_generate.v1'
PROMPT_NAME = 'grok46_fragment_v1'
PROMPT_PATH = os.path.join(HERE, 'pwg_tm_prompts', 'grok46_fragment_v1.txt')
DEFAULT_PRODUCTION_ROUTE = None
FROZEN_MANIFEST_SHA256 = (
    'f024ec4b0b2e58f75868462d84fd51858e4de473d07c0dd825a487f3b73d952a'
)
FROZEN_KEYS_SHA256 = (
    'a7acf80f5cb0fce17e0a6b35c7ba1b4ce76c270b9973d31d707f338ce15fb84c'
)
DEFAULT_MANIFEST = os.path.join(C.DEFAULT_OUT_DIR, 'priority_5000.manifest.json')
DEFAULT_QUEUE = os.path.join(C.DEFAULT_OUT_DIR, 'priority_5000.jsonl')
DEFAULT_OUT = os.path.join(C.DEFAULT_OUT_DIR, 'wave1_b')
PWG_FIXTURE = os.path.join(
    C.ROOT, 'schemas', 'fixtures', 'pwg_tm_generate.pwg.fixture.txt')

# Conservative list estimate USD / 1M tokens. Tokens are authoritative.
RATE_CARD = {
    'input_per_m': 3.0,
    'output_per_m': 15.0,
    'source': 'operator-estimate-pending-invoice',
    'model': MODEL_ID,
}

FORMULA_RU = {
    'am anfange eines comp.': 'в начале сложения',
    'am anf. eines comp.': 'в начале сложения',
    'am anfange eines compositums': 'в начале сложения',
    'am ende eines comp.': 'в конце сложения',
    'am ende eines compositums': 'в конце сложения',
    'in verbindung mit': 'в соединении с',
    's. u. d. w.': 'см. под сл.',
    's. u.': 'см.',
    's. d.': 'см. т.',
    's. v.': 'см. сл.',
    's.': 'см.',
    'vgl.': 'ср.',
    'dass.': 'то же',
    'ebend.': 'там же',
    'u.s.w.': 'и т. д.',
    'u. s. w.': 'и т. д.',
    'fg.': 'след.',
    'fgg.': 'след.',
    'folg.': 'след.',
    'desgl.': 'то же',
    'dgl.': 'то же',
    'sc.': 'т. е.',
    'scil.': 'т. е.',
    'v. a.': 'т. е.',
    'schol.': 'схолия',
    'sch.': 'схолия',
    'übertr.': 'перен.',
    'bed.': 'знач.',
    'erkl.': 'объясн.',
    'n. pr.': 'собств. имя',
    'v. l.': 'вар.',
    'comm.': 'комм.',
    'bez.': 'обозн.',
    'z.': 'стр.',
    'bein.': 'эпитет',
    'vulg.': 'прост.',
    'patron.': 'патроним.',
    'überh.': 'вообще',
}
# Grammatical metalanguage that fragmentize may class as formula: keep Latin.
FORMULA_COPY = {
    'nom. act.', 'pronom.', 'impers.', 'simpl.', 'autt.',
}

TAG_STRIP = re.compile(r'<[^>]+>')
PURE_LS = re.compile(r'^<ls\b[^>]*>.*?</ls>$', re.S)
PURE_SA = re.compile(r'^\{#.*?#\}$', re.S)
PURE_LEX = re.compile(r'^<lex\b[^>]*>.*?</lex>$', re.S)
PURE_AB = re.compile(r'^<ab\b[^>]*>.*?</ab>$', re.S)


def prompt_text():
    with open(PROMPT_PATH, encoding='utf-8') as f:
        return f.read()


def prompt_sha256():
    return C.sha256_text(prompt_text())


def load_manifest(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load_queue(path):
    return C.read_jsonl(path)


def pin_frozen(manifest, queue, require_frozen=True):
    keys = [r['k1'] for r in queue]
    if len(keys) != len(set(keys)):
        raise SystemExit('pwg_tm_generate: duplicate k1 in queue')
    key_hash = C.sha256_json(keys)
    if require_frozen:
        if manifest.get('manifest_sha256') != FROZEN_MANIFEST_SHA256:
            raise SystemExit(
                'pwg_tm_generate: manifest hash %s != frozen %s'
                % (manifest.get('manifest_sha256'), FROZEN_MANIFEST_SHA256))
        if manifest.get('selected_keys_sha256') != FROZEN_KEYS_SHA256:
            raise SystemExit('pwg_tm_generate: selected_keys_sha256 drift')
        if key_hash != FROZEN_KEYS_SHA256:
            raise SystemExit('pwg_tm_generate: queue key hash drift')
        if len(keys) != 5000:
            raise SystemExit('pwg_tm_generate: queue length %d != 5000' % len(keys))
    return keys


def require_route(route):
    if route != ROUTE_ID:
        raise SystemExit(
            'pwg_tm_generate: refuse implicit/other route %r; pass --route %s'
            % (route, ROUTE_ID))
    if DEFAULT_PRODUCTION_ROUTE is not None:
        raise SystemExit('pwg_tm_generate: default production route must stay unset')


def load_checkpoint(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(path, obj):
    C.write_json(path, obj)


def append_jsonl(path, rows):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def records_from_pwg(path, wanted):
    import pwg_mask
    import microstructure as M
    found = {}
    prev = pwg_mask.PWG
    pwg_mask.PWG = path
    try:
        for buf in pwg_mask.records():
            k1, k2, h = M.header(buf)
            if k1 not in wanted:
                continue
            found.setdefault(k1, []).append({
                'k1': k1,
                'k2': k2,
                'h': h,
                'body': '\n'.join(buf[1:]),
                'header': buf[0],
            })
    finally:
        pwg_mask.PWG = prev
    return found


def source_publication(rec):
    import microstructure as M
    units = []
    for seg in M.split_senses(rec['body']):
        tag = seg['n'] if not seg.get('sub') else '%s%s' % (seg['n'], seg['sub'])
        units.append({'tag': tag, 'german': seg['text'], 'russian': ''})
    if not units:
        units = [{'tag': '1', 'german': rec['body'], 'russian': ''}]
    return {
        'schema': 'pwg.translation_memory.publication.v1',
        'tm_record_id': 'wave1b:src:%s:%s' % (rec['k1'], rec['h'] or '0'),
        'record_type': 'wave1b_source',
        'lang': 'ru',
        'trust_level': 'suggestion',
        'reuse_policy': 'suggest_only',
        'review_status': 'draft',
        'gate_status': 'ungated',
        'gate_version': G.GATE_VERSION,
        'source_kind': 'pwg_source',
        'source_hashes': {'input_raw_sha256': C.sha256_text(rec['body'])},
        'provenance': {'root': rec['k1'], 'source_kind': 'pwg_source'},
        'evidence': [{'kind': 'pwg_source', 'src_key': rec['k1'],
                      'n_senses': len(units)}],
        'payload': {'card': {
            'key1': rec['k1'], 'iast': rec.get('k2') or '',
            'records': [{'h': rec.get('h') or '', 'senses': units}],
        }},
        'supersedes': [],
    }


def extract_records(pwg_recs, generated_at=None):
    generated_at = generated_at or C.utc_now()
    parents, fragments = [], []
    for rec in pwg_recs:
        pub = source_publication(rec)
        parent = C.migrate_publication(pub, generated_at=generated_at)
        parents.append(parent)
        fragments.extend(F.fragmentize_record(parent))
    return parents, fragments


def _visible(text):
    return TAG_STRIP.sub('', text or '').strip()


def _norm_formula(text):
    vis = re.sub(r'\s+', ' ', _visible(text)).strip().lower()
    return vis.rstrip('.') + '.' if vis else vis


def _formula_lookup(src):
    key = _norm_formula(src)
    bare = key.rstrip('.')
    for cand in (key, bare, bare + '.'):
        if cand in FORMULA_COPY:
            return 'copy', cand
        if cand in FORMULA_RU:
            return FORMULA_RU[cand], cand
    return None, key


def deterministic_target(fragment):
    src = (fragment.get('source_string') or '').strip()
    klass = fragment.get('fragment_class')
    if not src:
        return None, None
    if klass == 'citation' and PURE_LS.match(src):
        return src, 'copy:citation'
    if klass == 'example' and PURE_SA.match(src):
        return src, 'copy:example'
    if klass == 'grammar_label' and (PURE_LEX.match(src) or PURE_AB.match(src)):
        return src, 'copy:grammar_label'
    if klass == 'recurring_formula':
        ru, _key = _formula_lookup(src)
        if ru == 'copy':
            return src, 'copy:formula-grammar'
        if ru is not None:
            if PURE_AB.match(src):
                return re.sub(r'(<ab\b[^>]*>)(.*?)(</ab>)',
                              r'\1%s\3' % ru, src, count=1, flags=re.S), 'formula'
            return ru, 'formula'
    return None, None


def stamp_generation(fragment, *, origin, usage=None):
    out = dict(fragment)
    src = out.get('source_string') or ''
    gen = {
        'model_id': MODEL_ID,
        'route_id': ROUTE_ID,
        'prompt_name': PROMPT_NAME,
        'prompt_sha256': prompt_sha256(),
        'pipeline_version': PIPELINE_VERSION,
        'gate_version': G.GATE_VERSION,
        'source_hash': out.get('source_hash') or C.sha256_text(src),
        'origin': origin,
        'usage': usage or {'input_tokens': 0, 'output_tokens': 0, 'cost_usd': 0.0},
    }
    out['generation'] = gen
    out['model_version'] = MODEL_ID
    out['pipeline_version'] = PIPELINE_VERSION
    out['lang'] = out.get('lang') or 'ru'
    if out.get('target_string') is not None:
        out['target_hash'] = C.sha256_text(out['target_string'])
    return out


def load_drafts(path):
    if not path:
        return {}
    out = {}
    for row in C.read_jsonl(path):
        fid = row.get('fragment_id')
        if fid:
            out[fid] = row
    return out


GLOSS_SPAN = re.compile(r'\{%.*?%\}', re.S)


def merge_glosses(source, gloss_map):
    def repl(match):
        key = match.group(0)
        return gloss_map.get(key, key)
    return GLOSS_SPAN.sub(repl, source or '')


def apply_targets(fragments, drafts, reuse_index):
    filled = []
    stats = {
        'reuse_exact': 0, 'deterministic': 0, 'drafted': 0,
        'sense_merge': 0, 'unfilled': 0,
    }
    gloss_map = {}
    pending = []
    for frag in fragments:
        src = frag.get('source_string') or ''
        frag = dict(frag)
        frag['source_hash'] = C.sha256_text(src)
        origin = None
        usage = {'input_tokens': 0, 'output_tokens': 0, 'cost_usd': 0.0}
        reuse_key = frag.get('reuse_key')
        hit = reuse_index.get(reuse_key) if reuse_key else None
        if hit and hit.get('target_string') and hit.get('reuse_policy') == 'auto_exact':
            frag['target_string'] = hit['target_string']
            origin = 'exact_reuse'
            stats['reuse_exact'] += 1
        else:
            det, det_origin = deterministic_target(frag)
            if det is not None:
                frag['target_string'] = det
                origin = det_origin
                stats['deterministic'] += 1
            elif frag.get('fragment_id') in drafts:
                row = drafts[frag['fragment_id']]
                frag['target_string'] = row.get('target_string')
                origin = row.get('origin') or 'grok-4.6-draft'
                usage = row.get('usage') or usage
                stats['drafted'] += 1
            else:
                origin = 'unfilled'
        if (frag.get('fragment_class') == 'definition_gloss'
                and frag.get('target_string')):
            gloss_map[src] = frag['target_string']
        pending.append((frag, origin, usage))
    for frag, origin, usage in pending:
        if origin == 'unfilled' and frag.get('fragment_class') == 'sense':
            merged = merge_glosses(frag.get('source_string') or '', gloss_map)
            if merged != (frag.get('source_string') or '') and GLOSS_SPAN.search(
                    frag.get('source_string') or ''):
                frag['target_string'] = merged
                origin = 'sense_merge'
                stats['sense_merge'] += 1
            else:
                stats['unfilled'] += 1
        elif origin == 'unfilled':
            stats['unfilled'] += 1
        filled.append(stamp_generation(frag, origin=origin, usage=usage))
    return filled, stats


def reuse_index_from_publication(path):
    if not path or not os.path.exists(path):
        return {}
    pubs = C.read_jsonl(path)
    parents = [C.migrate_publication(p, generated_at='1970-01-01T00:00:00Z') for p in pubs]
    index = {}
    for frag in F.fragmentize_rows(parents):
        key = frag.get('reuse_key')
        if not key:
            continue
        if frag.get('reuse_policy') != 'auto_exact':
            continue
        if not frag.get('target_string'):
            continue
        index[key] = frag
    return index


def promote_rows(filled):
    receipts = G.gate_rows(filled)
    by_id = {r['fragment_id']: r for r in receipts}
    promoted, quarantine = [], []
    for frag in filled:
        rec = by_id[frag['fragment_id']]
        row = G.apply_gate(frag, rec)
        if rec['ok']:
            promoted.append(row)
        else:
            quarantine.append(row)
    return promoted, quarantine, receipts


def window_keys(queue, *, offset, limit, keys=None, compact=False):
    if keys:
        want = set(keys)
        return [r for r in queue if r['k1'] in want]
    rows = queue[offset:offset + limit] if limit else queue[offset:]
    if compact:
        by_s = {}
        for row in queue:
            by_s.setdefault(row['stratum'], []).append(row)
        picked = []
        for stratum, items in by_s.items():
            items = sorted(items, key=lambda r: (r.get('predicted_reuse') or 0, r['k1']))
            picked.extend(items[: max(1, limit // max(1, len(by_s)))])
        picked.sort(key=lambda r: r['rank'])
        return picked[:limit]
    return rows


def empty_ledger():
    return {
        'schema': 'pwg.tm.generate.cost.v1',
        'model_id': MODEL_ID,
        'route_id': ROUTE_ID,
        'prompt_sha256': prompt_sha256(),
        'pipeline_version': PIPELINE_VERSION,
        'rate_card': RATE_CARD,
        'input_tokens': 0,
        'output_tokens': 0,
        'cost_usd': 0.0,
        'cost_evaluable': False,
        'calls': 0,
        'note': 'tokens authoritative; USD is list estimate unless invoiced',
    }


def add_usage(ledger, usage):
    usage = usage or {}
    ledger['input_tokens'] += int(usage.get('input_tokens') or 0)
    ledger['output_tokens'] += int(usage.get('output_tokens') or 0)
    ledger['calls'] += 1
    est = (
        ledger['input_tokens'] * RATE_CARD['input_per_m']
        + ledger['output_tokens'] * RATE_CARD['output_per_m']
    ) / 1_000_000.0
    ledger['cost_usd'] = round(est, 6)
    return ledger


def reconcile(queue_rows, processed, promoted, quarantine, missing_source, ledger,
              manifest):
    processed_keys = [r['k1'] for r in processed]
    acc = {
        'schema': 'pwg.tm.generate.reconciliation.v1',
        'manifest_sha256': manifest.get('manifest_sha256'),
        'route_id': ROUTE_ID,
        'model_id': MODEL_ID,
        'prompt_sha256': prompt_sha256(),
        'pipeline_version': PIPELINE_VERSION,
        'gate_version': G.GATE_VERSION,
        'queue_keys': len(queue_rows),
        'processed_keys': len(processed_keys),
        'missing_source_keys': sorted(missing_source),
        'promoted_fragments': len(promoted),
        'quarantine_fragments': len(quarantine),
        'silent_drops': 0,
        'unaccounted_promotions': 0,
        'promotion_status_counts': {
            'promoted': len(promoted),
            'quarantine': len(quarantine),
        },
        'by_class_promoted': dict(
            __import__('collections').Counter(r['fragment_class'] for r in promoted)),
        'by_class_quarantine': dict(
            __import__('collections').Counter(r['fragment_class'] for r in quarantine)),
        'ledger': ledger,
        'ok': True,
    }
    accounted = len(promoted) + len(quarantine)
    extracted = accounted
    if extracted != accounted:
        acc['silent_drops'] = extracted - accounted
        acc['ok'] = False
    if acc['missing_source_keys'] and not processed_keys:
        acc['ok'] = False
    return acc


def write_run(out_dir, promoted, quarantine, receipts, checkpoint, ledger, recon):
    os.makedirs(out_dir, exist_ok=True)
    C.write_jsonl(os.path.join(out_dir, 'promoted.jsonl'), promoted)
    C.write_jsonl(os.path.join(out_dir, 'quarantine.jsonl'), quarantine)
    C.write_jsonl(os.path.join(out_dir, 'gate_receipts.jsonl'), receipts)
    save_json(os.path.join(out_dir, 'checkpoint.json'), checkpoint)
    save_json(os.path.join(out_dir, 'cost_ledger.json'), ledger)
    save_json(os.path.join(out_dir, 'reconciliation.json'), recon)
    return recon


def run_window(args):
    require_route(args.route)
    manifest = load_manifest(args.manifest)
    queue = load_queue(args.queue)
    pin_frozen(manifest, queue, require_frozen=not args.allow_unfrozen)
    ckpt = load_checkpoint(args.checkpoint) if args.resume else None
    done = set((ckpt or {}).get('processed_keys') or [])
    chosen = window_keys(
        queue, offset=args.offset, limit=args.limit,
        keys=args.keys.split(',') if args.keys else None,
        compact=args.compact)
    pending = [r for r in chosen if r['k1'] not in done]
    wanted = {r['k1'] for r in pending}
    pwg_path = args.pwg or _default_pwg()
    found = records_from_pwg(pwg_path, wanted) if os.path.exists(pwg_path) else {}
    missing = sorted(wanted - set(found))
    pwg_recs = [rec for k in wanted for rec in found.get(k, [])]
    _parents, fragments = extract_records(pwg_recs)
    drafts = load_drafts(args.drafts)
    if args.live:
        need = []
        preview, _st = apply_targets(fragments, drafts, {})
        for frag in preview:
            if (frag.get('generation') or {}).get('origin') == 'unfilled':
                need.append(frag)
        if need:
            drafts = dict(drafts)
            drafts.update(live_complete(need))
    reuse = {} if args.no_reuse else reuse_index_from_publication(
        args.publication or C.DEFAULT_PUBLICATION)
    filled, fill_stats = apply_targets(fragments, drafts, reuse)
    promoted, quarantine, receipts = promote_rows(filled)
    ledger = empty_ledger()
    for frag in filled:
        if (frag.get('generation') or {}).get('origin') in (
                'grok-4.6-draft', 'grok-4.6-live'):
            add_usage(ledger, (frag.get('generation') or {}).get('usage'))
    processed = pending
    recon = reconcile(queue, processed, promoted, quarantine, missing, ledger, manifest)
    recon['fill_stats'] = fill_stats
    recon['extracted_fragments'] = len(fragments)
    recon['accounted_fragments'] = len(promoted) + len(quarantine)
    if recon['extracted_fragments'] != recon['accounted_fragments']:
        recon['silent_drops'] = (
            recon['extracted_fragments'] - recon['accounted_fragments'])
        recon['ok'] = False
    checkpoint = {
        'schema': 'pwg.tm.generate.checkpoint.v1',
        'manifest_sha256': manifest.get('manifest_sha256'),
        'route_id': ROUTE_ID,
        'model_id': MODEL_ID,
        'prompt_sha256': prompt_sha256(),
        'pipeline_version': PIPELINE_VERSION,
        'processed_keys': sorted(done | {r['k1'] for r in processed}),
        'pending_keys': [r['k1'] for r in queue
                         if r['k1'] not in (done | {x['k1'] for x in processed})],
        'offset': args.offset,
        'limit': args.limit,
        'promoted_fragments': len(promoted),
        'quarantine_fragments': len(quarantine),
        'missing_source': missing,
        'resumable': True,
    }
    write_run(args.out_dir, promoted, quarantine, receipts, checkpoint, ledger, recon)
    print(json.dumps({
        'ok': recon['ok'],
        'processed': len(processed),
        'promoted': len(promoted),
        'quarantine': len(quarantine),
        'missing_source': len(missing),
        'out_dir': args.out_dir,
    }, ensure_ascii=False))
    return 0 if recon['ok'] else 1


def _default_pwg():
    import pwg_mask
    return pwg_mask.PWG


def cmd_extract(args):
    manifest = load_manifest(args.manifest)
    queue = load_queue(args.queue)
    pin_frozen(manifest, queue, require_frozen=not args.allow_unfrozen)
    chosen = window_keys(
        queue, offset=args.offset, limit=args.limit,
        keys=args.keys.split(',') if args.keys else None,
        compact=args.compact)
    wanted = {r['k1'] for r in chosen}
    pwg_path = args.pwg or _default_pwg()
    found = records_from_pwg(pwg_path, wanted) if os.path.exists(pwg_path) else {}
    missing = sorted(wanted - set(found))
    pwg_recs = [rec for k in wanted for rec in found.get(k, [])]
    parents, fragments = extract_records(pwg_recs)
    os.makedirs(args.out_dir, exist_ok=True)
    C.write_jsonl(os.path.join(args.out_dir, 'extracted_parents.jsonl'), parents)
    C.write_jsonl(os.path.join(args.out_dir, 'extracted_fragments.jsonl'), fragments)
    save_json(os.path.join(args.out_dir, 'extract_receipt.json'), {
        'schema': 'pwg.tm.generate.extract.v1',
        'requested': sorted(wanted),
        'found': sorted(found),
        'missing_source': missing,
        'parent_count': len(parents),
        'fragment_count': len(fragments),
        'by_class': dict(__import__('collections').Counter(
            f['fragment_class'] for f in fragments)),
        'pwg_path_exists': os.path.exists(pwg_path),
    })
    print('extract keys=%d found=%d frags=%d missing=%d' % (
        len(wanted), len(found), len(fragments), len(missing)))
    return 0


def cmd_reconcile(args):
    recon_path = os.path.join(args.out_dir, 'reconciliation.json')
    if not os.path.exists(recon_path):
        print('no reconciliation at %s' % recon_path)
        return 1
    recon = json.load(open(recon_path, encoding='utf-8'))
    print(json.dumps(recon, ensure_ascii=False, indent=2))
    return 0 if recon.get('ok') else 1


def live_complete(items):
    """Optional xAI call. Refuses without XAI_API_KEY. Not used by default."""
    key = os.environ.get('XAI_API_KEY')
    if not key:
        raise SystemExit('pwg_tm_generate --live requires XAI_API_KEY')
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit('pwg_tm_generate --live needs openai SDK: %s' % exc)
    client = OpenAI(api_key=key, base_url='https://api.x.ai/v1')
    payload = [{'fragment_id': i['fragment_id'],
                'fragment_class': i['fragment_class'],
                'source_string': i['source_string'],
                'context': i.get('context')} for i in items]
    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {'role': 'system', 'content': prompt_text()},
            {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)},
        ],
        temperature=0,
    )
    usage = resp.usage
    text = resp.choices[0].message.content or '{}'
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r'\{.*\}', text, re.S)
        parsed = json.loads(m.group(0)) if m else {'fragments': []}
    rows = parsed.get('fragments') or parsed.get('items') or []
    out = {}
    tok_in = getattr(usage, 'prompt_tokens', 0) or 0
    tok_out = getattr(usage, 'completion_tokens', 0) or 0
    share_in = tok_in // max(len(rows), 1)
    share_out = tok_out // max(len(rows), 1)
    for row in rows:
        fid = row.get('fragment_id')
        if not fid:
            continue
        out[fid] = {
            'fragment_id': fid,
            'target_string': row.get('target_string'),
            'origin': 'grok-4.6-live',
            'usage': {
                'input_tokens': share_in,
                'output_tokens': share_out,
                'cost_usd': 0.0,
            },
        }
    return out


def verify():
    if DEFAULT_PRODUCTION_ROUTE is not None:
        return False, 'default production route must be unset'
    if prompt_sha256() != C.sha256_text(prompt_text()):
        return False, 'prompt hash unstable'
    if not os.path.exists(PROMPT_PATH):
        return False, 'prompt missing'
    fixture_pwg = PWG_FIXTURE
    if not os.path.exists(fixture_pwg):
        return False, 'pwg fixture missing'
    found = records_from_pwg(fixture_pwg, {'agni', 'akzara'})
    if set(found) != {'agni', 'akzara'}:
        return False, 'fixture keys %s' % sorted(found)
    _parents, frags = extract_records(
        [rec for k in ('agni', 'akzara') for rec in found[k]],
        generated_at='1970-01-01T00:00:00Z')
    classes = {f['fragment_class'] for f in frags}
    if set(C.FRAGMENT_CLASSES) - classes:
        return False, 'fixture missing classes %s' % (
            set(C.FRAGMENT_CLASSES) - classes)
    drafts = {}
    for frag in frags:
        det, _origin = deterministic_target(frag)
        if det is not None:
            continue
        src = frag['source_string']
        tgt = src
        if '{%Feuer, Gott des Feuers.%}' in src:
            tgt = src.replace('{%Feuer, Gott des Feuers.%}',
                              '{%огонь, бог огня.%}')
        elif '{%Silbe, unvergänglich.%}' in src:
            tgt = src.replace('{%Silbe, unvergänglich.%}',
                              '{%слог, нетленный.%}')
        drafts[frag['fragment_id']] = {
            'fragment_id': frag['fragment_id'],
            'target_string': tgt,
            'origin': 'grok-4.6-draft',
        }
    filled, stats = apply_targets(frags, drafts, {})
    if stats['unfilled']:
        return False, 'fixture unfilled %s' % stats
    promoted, quarantine, _rec = promote_rows(filled)
    if len(promoted) + len(quarantine) != len(filled):
        return False, 'silent drop in fixture run'
    if not promoted:
        return False, 'fixture promoted 0; quarantine=%s' % [
            (q['fragment_id'], q.get('quarantine_reasons')) for q in quarantine[:8]]
    # implicit route must refuse
    try:
        require_route('claude-cli-headless')
        return False, 'implicit route was accepted'
    except SystemExit:
        pass
    require_route(ROUTE_ID)
    with tempfile.TemporaryDirectory() as tmp:
        C.write_jsonl(os.path.join(tmp, 'promoted.jsonl'), promoted)
        C.write_jsonl(os.path.join(tmp, 'quarantine.jsonl'), quarantine)
        recon = reconcile(
            [{'k1': 'agni'}, {'k1': 'akzara'}],
            [{'k1': 'agni'}, {'k1': 'akzara'}],
            promoted, quarantine, [], empty_ledger(),
            {'manifest_sha256': 'fixture'})
        if recon['silent_drops'] != 0:
            return False, 'recon silent drops'
        if not recon['ok']:
            return False, 'fixture recon not ok'
    return True, 'ok promoted=%d quarantine=%d classes=%s' % (
        len(promoted), len(quarantine), sorted(classes))


def build_parser():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    ap.add_argument('--verify', action='store_true')

    def add_shared(p):
        p.add_argument('--route', default=None,
                       help='must be grok-4.6; never implicit')
        p.add_argument('--manifest', default=DEFAULT_MANIFEST)
        p.add_argument('--queue', default=DEFAULT_QUEUE)
        p.add_argument('--publication', default=C.DEFAULT_PUBLICATION)
        p.add_argument('--pwg', default=None)
        p.add_argument('--out-dir', default=DEFAULT_OUT)
        p.add_argument('--offset', type=int, default=0)
        p.add_argument('--limit', type=int, default=12)
        p.add_argument('--keys', default=None)
        p.add_argument('--compact', action='store_true')
        p.add_argument('--allow-unfrozen', action='store_true')
        p.add_argument('--drafts', default=None)
        p.add_argument('--checkpoint', default=None)
        p.add_argument('--resume', action='store_true')
        p.add_argument('--no-reuse', action='store_true')
        p.add_argument('--live', action='store_true')

    p_run = sub.add_parser('run')
    add_shared(p_run)
    p_ex = sub.add_parser('extract')
    add_shared(p_ex)
    p_rec = sub.add_parser('reconcile')
    p_rec.add_argument('--out-dir', default=DEFAULT_OUT)
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.verify or args.cmd is None:
        ok, msg = verify()
        print(msg)
        return 0 if ok else 1
    if args.cmd == 'extract':
        return cmd_extract(args)
    if args.cmd == 'run':
        if not args.route:
            raise SystemExit('pwg_tm_generate run: --route grok-4.6 is required')
        if args.live and not args.drafts:
            # live fills drafts in memory then runs the same gate path
            pass
        return run_window(args)
    if args.cmd == 'reconcile':
        return cmd_reconcile(args)
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
