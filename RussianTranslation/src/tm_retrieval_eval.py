#!/usr/bin/env python
r"""H2686 / H1457 Track A6 -- live retrieval measurement.

Neural Fuzzy Repair framing (Bulte & Tezcan 2019, P19-1175): translate a frozen
fragment batch twice -- (a) no-TM, (b) graded fragment-TM as fuzzy context --
and report quality, serious-error, edit, latency, token and cost deltas.

MEASUREMENT ONLY. This never wires retrieval into the production decode loop
and never rewrites Wave 1.

    python tm_retrieval_eval.py selftest
    python tm_retrieval_eval.py freeze [--sample P] [--adjudication P] [--n-per-class N]
    python tm_retrieval_eval.py run --engine none|deepseek [--batch P] [--out P]

`--engine none` writes the documented block (no fabricated numbers).
`--engine deepseek` is the live path. Mocks stay inside `selftest` and are
refused by the live report renderer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
REPO = os.path.normpath(os.path.join(ROOT, '..'))
GITHUB = os.path.normpath(os.path.join(REPO, '..'))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

DEFAULT_GRADE_GOLD = os.path.join(ROOT, 'gold', 'grade_gold.jsonl')
DEFAULT_SAMPLE = os.path.join(
    ROOT, 'release', 'pwg_tm_canonical', 'wave1_b_receipt', 'sample400.jsonl')
DEFAULT_ADJ = os.path.join(
    ROOT, 'release', 'pwg_tm_canonical', 'wave1_b_receipt', 'adjudication400.jsonl')
DEFAULT_PUBLICATION = os.path.join(
    ROOT, 'release', 'translation_memory', 'translation_memory.ru.publication.jsonl')
DEFAULT_BATCH = os.path.join(HERE, 'RETRIEVAL_EVAL_BATCH.jsonl')
DEFAULT_MANIFEST = os.path.join(HERE, 'RETRIEVAL_EVAL_MANIFEST.json')
DEFAULT_LIVE_JSON = os.path.join(HERE, 'RETRIEVAL_EVAL_LIVE.json')
DEFAULT_OUT = os.path.join(HERE, 'RETRIEVAL_EVAL.md')
DEFAULT_LEDGER = os.path.join(HERE, 'RETRIEVAL_EVAL_COST.json')

VERSION = '0.2.0'
ENGINE_NONE = 'none'
ENGINE_DEEPSEEK = 'deepseek'
LIVE_ENGINES = (ENGINE_DEEPSEEK,)
TRANSLATABLE = (
    'definition_gloss', 'sense', 'recurring_formula', 'example', 'grammar_label',
)
DEEPSEEK_MODEL = 'deepseek-v4-flash'
TRANSLATE_MAX_TOKENS = 512
JUDGE_MAX_TOKENS = 256
RETRIEVE_K = 3


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(s):
    return hashlib.sha256((s or '').encode('utf-8')).hexdigest()


def load_jsonl(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            ins = cur[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (ca != cb)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def norm_edit(hyp, ref):
    if hyp is None:
        hyp = ''
    if ref is None:
        ref = ''
    denom = max(len(hyp), len(ref), 1)
    return levenshtein(hyp, ref) / denom


def candidate_env_files():
    return [
        os.path.join(HERE, '.env'),
        os.path.join(GITHUB, 'SanskritLexicography', 'RussianTranslation', 'src', '.env'),
        os.path.join(GITHUB, 'ORS-FAQ', '.env'),
    ]


def load_deepseek_key():
    env = os.environ.get('DEEPSEEK_API_KEY')
    if env:
        return env, 'environ'
    for path in candidate_env_files():
        if not os.path.isfile(path):
            continue
        for line in open(path, encoding='utf-8'):
            if line.strip().startswith('DEEPSEEK_API_KEY='):
                val = line.split('=', 1)[1].strip().strip('"').strip("'")
                if val:
                    return val, path
    return None, None


def cmd_batch(a):
    """Legacy grade-A gold batch (H1457). Kept so older commands still work."""
    if not os.path.exists(a.grade_gold):
        sys.exit('frozen gold not found: %s (run build_grade_gold.py build first)'
                 % a.grade_gold)
    rows = load_jsonl(a.grade_gold)
    a_rows = sorted((r for r in rows if r.get('grade') == 'A'),
                    key=lambda r: r.get('id', 0))
    batch = a_rows[:a.n]
    out_rows = []
    for r in batch:
        out_rows.append({
            'slp1': r.get('slp1'),
            'sa': r.get('sa'),
            'source_string': r.get('sa'),
            'ru_reference': r.get('ru'),
            'target_reference': r.get('ru'),
            'kind': r.get('kind'),
            'period': r.get('period'),
            'fragment_class': 'gold_sa_ru',
            'pair_type': 'sa-ru',
        })
    write_jsonl(a.out, out_rows)
    print('batch: %d grade-A rows -> %s' % (len(out_rows), a.out))
    return 0


def _adj_map(path):
    out = {}
    if not os.path.exists(path):
        return out
    for row in load_jsonl(path):
        fid = row.get('fragment_id') or row.get('record_id')
        if fid:
            out[fid] = row.get('adjudication') or {}
    return out


def _is_copy_through(row):
    src = (row.get('source_string') or '').strip()
    tgt = (row.get('target_string') or '').strip()
    return bool(src) and src == tgt


def freeze_batch(sample_path, adj_path, n_per_class=4, seed_key='fragment_id'):
    """Deterministic stratified hold-out from H2684 sample400 + adjudication.

    Only rows whose German source differs from the Russian target enter the
    live translate batch (copy-through citations are TM-reuse inventory, not
    a translation arm).
    """
    if not os.path.exists(sample_path):
        sys.exit('H2684 sample not found: %s' % sample_path)
    adj = _adj_map(adj_path)
    by_class = defaultdict(list)
    copy_n = 0
    for row in load_jsonl(sample_path):
        fid = row.get('fragment_id')
        klass = row.get('fragment_class') or 'unknown'
        if _is_copy_through(row):
            copy_n += 1
            continue
        if klass not in TRANSLATABLE:
            continue
        rec = {
            'fragment_id': fid,
            'entry_id': row.get('entry_id'),
            'slp1': (row.get('source_locator') or {}).get('lemma_slp1')
                    or (row.get('source_locator') or {}).get('key1'),
            'fragment_class': klass,
            'source_string': row.get('source_string') or '',
            'target_reference': row.get('target_string') or '',
            'promotion_status': row.get('promotion_status'),
            'confidence_tier': row.get('confidence_tier'),
            'freq_count': ((row.get('source_locator') or {}).get('freq_count')
                           or (row.get('context') or {}).get('freq_count')),
            'complex': bool((row.get('context') or {}).get('complex')
                            or row.get('complex')),
            'pair_type': 'de-ru',
            'adjudication': adj.get(fid) or {},
        }
        by_class[klass].append(rec)
    batch = []
    for klass in TRANSLATABLE:
        rows = sorted(by_class[klass], key=lambda r: r.get(seed_key) or '')
        batch.extend(rows[:n_per_class])
    batch.sort(key=lambda r: (r['fragment_class'], r['fragment_id'] or ''))
    return batch, {
        'n': len(batch),
        'n_per_class': n_per_class,
        'copy_through_excluded': copy_n,
        'per_class_pool': {k: len(v) for k, v in by_class.items()},
        'per_class_drawn': dict(Counter(r['fragment_class'] for r in batch)),
        'sample_sha256': sha256_file(sample_path),
        'adjudication_sha256': sha256_file(adj_path) if os.path.exists(adj_path) else None,
    }


def cmd_freeze(a):
    batch, meta = freeze_batch(a.sample, a.adjudication, n_per_class=a.n_per_class)
    write_jsonl(a.out, batch)
    manifest = {
        'schema': 'pwg.tm.retrieval_eval.manifest.v1',
        'version': VERSION,
        'created': '14-08-2026',
        'batch_path': os.path.relpath(a.out, ROOT).replace('\\', '/'),
        'batch_sha256': sha256_file(a.out),
        'gold_path': os.path.relpath(DEFAULT_GRADE_GOLD, ROOT).replace('\\', '/'),
        'gold_sha256': sha256_file(DEFAULT_GRADE_GOLD),
        'wave1_immutable': True,
        **meta,
    }
    with open(a.manifest, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('freeze: %d cards (%s) -> %s' % (len(batch), meta['per_class_drawn'], a.out))
    print('freeze: manifest %s sha256=%s' % (a.manifest, manifest['batch_sha256']))
    return 0


def _walk_publication_pairs(rec):
    """Yield (de, ru) from the publication exact-card payload."""
    payload = rec.get('payload') or {}
    card = payload.get('card') or payload
    records = card.get('records') or []
    for block in records:
        for sense in block.get('senses') or []:
            de = sense.get('german') or ''
            ru = sense.get('russian') or ''
            if de and ru:
                yield de, ru
    src = rec.get('de') or rec.get('source') or rec.get('source_string') or ''
    tgt = rec.get('ru') or rec.get('target') or rec.get('target_string') or ''
    if src and tgt:
        yield src, tgt


def publication_tm_rows(path, limit=800):
    if not os.path.exists(path):
        return []
    rows = []
    for rec in load_jsonl(path):
        rid = rec.get('tm_record_id') or rec.get('record_id') or rec.get('id')
        for i, (src, tgt) in enumerate(_walk_publication_pairs(rec)):
            rows.append({
                'fragment_id': '%s:%d' % (rid or sha256_text(src), i),
                'source_string': src,
                'target_string': tgt,
                'fragment_class': rec.get('fragment_class') or rec.get('record_type') or 'publication',
                'origin': 'publication_tm',
            })
            if len(rows) >= limit:
                return rows
    return rows


def sample_tm_rows(sample_path, exclude_ids):
    rows = []
    if not os.path.exists(sample_path):
        return rows
    for rec in load_jsonl(sample_path):
        fid = rec.get('fragment_id')
        if fid in exclude_ids:
            continue
        src = rec.get('source_string') or ''
        tgt = rec.get('target_string') or ''
        if not src or not tgt:
            continue
        rows.append({
            'fragment_id': fid,
            'source_string': src,
            'target_string': tgt,
            'fragment_class': rec.get('fragment_class'),
            'origin': rec.get('promotion_status') or 'sample400',
            'promotion_status': rec.get('promotion_status'),
        })
    return rows


def retrieve_labse(card, tm_rows, k=RETRIEVE_K):
    """Advisory kNN on source_string via LaBSE. Exact source match ranks first."""
    import nn_api
    src = card.get('source_string') or ''
    exact = []
    rest = []
    for row in tm_rows:
        if (row.get('source_string') or '') == src:
            exact.append(dict(row, retrieve_score=1.0, retrieve_kind='exact'))
        else:
            rest.append(row)
    if not nn_api.embed_available() or not rest:
        # Repair retriever: character 4-gram cosine. Advisory only — not QE.
        def ngrams(s, n=4):
            s = (s or '').lower()
            return [s[i:i + n] for i in range(max(0, len(s) - n + 1))]

        def ncos(a, b):
            from collections import Counter
            ca, cb = Counter(ngrams(a)), Counter(ngrams(b))
            keys = set(ca) | set(cb)
            if not keys:
                return 0.0
            dot = sum(ca[k] * cb[k] for k in keys)
            na = sum(v * v for v in ca.values()) ** 0.5
            nb = sum(v * v for v in cb.values()) ** 0.5
            if na == 0 or nb == 0:
                return 0.0
            return dot / (na * nb)

        ranked = [dict(row, retrieve_score=round(ncos(src, row.get('source_string') or ''), 4),
                       retrieve_kind='char4gram')
                  for row in rest]
        ranked.sort(key=lambda r: r['retrieve_score'], reverse=True)
        same = [r for r in ranked if r.get('fragment_class') == card.get('fragment_class')]
        other = [r for r in ranked if r.get('fragment_class') != card.get('fragment_class')]
        ordered = exact + same + other
        seen = set()
        out = []
        for row in ordered:
            fid = row.get('fragment_id')
            if fid in seen:
                continue
            seen.add(fid)
            out.append(row)
            if len(out) >= k:
                break
        return out
    q = nn_api.embed([src])[0]
    cand_txt = [r.get('source_string') or '' for r in rest]
    vecs = nn_api.embed(cand_txt)
    ranked = []
    for row, vec in zip(rest, vecs):
        ranked.append(dict(row, retrieve_score=round(nn_api.cosine(q, vec), 4),
                           retrieve_kind='labse'))
    ranked.sort(key=lambda r: r['retrieve_score'], reverse=True)
    same = [r for r in ranked if r.get('fragment_class') == card.get('fragment_class')]
    other = [r for r in ranked if r.get('fragment_class') != card.get('fragment_class')]
    ordered = exact + same + other
    # de-dupe by fragment_id
    seen = set()
    out = []
    for row in ordered:
        fid = row.get('fragment_id')
        if fid in seen:
            continue
        seen.add(fid)
        out.append(row)
        if len(out) >= k:
            break
    return out


def fuzzy_context(card, tm_index, k=1):
    """H1457 exact-slp1 helper, kept for selftest."""
    if tm_index is None:
        return []
    if isinstance(tm_index, dict) and not tm_index.get('_rows'):
        hit = tm_index.get(card.get('slp1'))
        return [hit] if hit else []
    rows = tm_index.get('_rows') if isinstance(tm_index, dict) else tm_index
    return retrieve_labse(card, rows or [], k=k)


def run_arm(cards, translate_fn, judge_fn, tm_index=None, retrieve_k=RETRIEVE_K):
    rows = []
    t0 = time.perf_counter()
    total_tokens = 0
    total_cost = 0.0
    exact_reuse = 0
    fragment_reuse = 0
    for card in cards:
        if tm_index is None:
            context = []
        elif isinstance(tm_index, dict) and not tm_index.get('_rows'):
            hit = tm_index.get(card.get('slp1'))
            context = [hit] if hit else []
        else:
            rows_tm = tm_index.get('_rows') if isinstance(tm_index, dict) else tm_index
            context = retrieve_labse(card, rows_tm or [], k=retrieve_k)
        if any((isinstance(c, dict) and c.get('retrieve_kind') == 'exact')
               or (isinstance(c, str) and c) for c in context):
            exact_reuse += 1
        if context:
            fragment_reuse += 1
        t1 = time.perf_counter()
        out = translate_fn(card, context)
        dt = time.perf_counter() - t1
        quality = judge_fn(card, out)
        tokens = out.get('tokens', 0) or 0
        cost = float(out.get('cost_usd') or 0.0)
        total_tokens += tokens
        total_cost += cost
        hyp = out.get('text') or ''
        ref = card.get('target_reference') or card.get('ru_reference') or ''
        qe_score = out.get('qe_labse')
        if qe_score is None:
            try:
                import nn_api
                if nn_api.qe_available('labse'):
                    qe_score = nn_api.qe(card.get('source_string') or card.get('sa') or '',
                                         hyp, backend='labse')
            except Exception:
                qe_score = None
        judge = quality if isinstance(quality, dict) else {'quality': quality}
        rows.append({
            'fragment_id': card.get('fragment_id'),
            'slp1': card.get('slp1'),
            'fragment_class': card.get('fragment_class'),
            'output': hyp,
            'wall_clock_s': round(dt, 4),
            'tokens': tokens,
            'cost_usd': round(cost, 6),
            'quality': judge.get('quality'),
            'serious_error': bool(judge.get('serious_error')),
            'equivalence': judge.get('equivalence'),
            'edit': round(norm_edit(hyp, ref), 4),
            'qe_labse': qe_score,
            'n_context': len(context),
            'retrieve_kinds': [
                (c.get('retrieve_kind') if isinstance(c, dict) else 'legacy')
                for c in context
            ],
            'route': out.get('route'),
            'model': out.get('model'),
        })
    n = len(rows) or 1
    quals = [r['quality'] for r in rows if r['quality'] is not None]
    return {
        'rows': rows,
        'n': len(rows),
        'total_wall_clock_s': round(time.perf_counter() - t0, 4),
        'total_tokens': total_tokens,
        'total_cost_usd': round(total_cost, 6),
        'mean_quality': (sum(quals) / len(quals)) if quals else float('nan'),
        'mean_edit': sum(r['edit'] for r in rows) / n,
        'serious_error_n': sum(1 for r in rows if r['serious_error']),
        'serious_error_rate': sum(1 for r in rows if r['serious_error']) / n,
        'exact_reuse_n': exact_reuse,
        'fragment_reuse_n': fragment_reuse,
    }


def _import_deepseek():
    h1210 = os.path.join(HERE, 'pilot', 'h1210')
    if h1210 not in sys.path:
        sys.path.insert(0, h1210)
    import deepseek_arm
    return deepseek_arm


def _cost_usd(ds, rec, model):
    card = rec.get('price_card')
    _name, prices = ds.prices_for(model, card=card)
    miss = rec.get('cache_miss_tokens') or 0
    hit = rec.get('cache_hit_tokens') or 0
    out = rec.get('completion_tokens') or 0
    if not (miss or hit):
        miss = rec.get('prompt_tokens') or 0
    return (miss / 1e6 * prices['cache_miss_in']
            + hit / 1e6 * prices['cache_hit_in']
            + out / 1e6 * prices['out'])


def make_deepseek_fns(key, model=DEEPSEEK_MODEL):
    ds = _import_deepseek()
    ds.refuse_if_peak()
    translator = ds.DeepSeek('https://api.deepseek.com', key, model, TRANSLATE_MAX_TOKENS)
    judge = ds.DeepSeek('https://api.deepseek.com', key, model, JUDGE_MAX_TOKENS)
    ledger = []

    def _record(kind, rec):
        cost = _cost_usd(ds, rec, model)
        rec['cost_usd'] = cost
        row = {
            'kind': kind,
            'requested_model': rec.get('requested_model'),
            'served_model': rec.get('served_model'),
            'model_matches_request': rec.get('model_matches_request'),
            'latency_s': rec.get('latency_s'),
            'prompt_tokens': rec.get('prompt_tokens'),
            'completion_tokens': rec.get('completion_tokens'),
            'cache_hit_tokens': rec.get('cache_hit_tokens'),
            'cache_miss_tokens': rec.get('cache_miss_tokens'),
            'price_card': rec.get('price_card'),
            'cost_usd': round(cost, 8),
            'transport': rec.get('transport'),
            'error': rec.get('error'),
        }
        ledger.append(row)
        return row

    sys_tr = (
        'You translate PWG German dictionary fragments into Russian. '
        'Preserve XML-like tags (<ls>, <ab>, <lex>) and {%...%} wrappers. '
        'Return JSON {"text": "<russian fragment>"}. No commentary.'
    )

    def translate_fn(card, context):
        src = card.get('source_string') or card.get('sa') or ''
        parts = []
        if context:
            parts.append('FUZZY TM MATCHES (advisory; may be the wrong sense):')
            for i, hit in enumerate(context, 1):
                if isinstance(hit, str):
                    parts.append('%d. %s' % (i, hit))
                else:
                    parts.append('%d. DE: %s\n   RU: %s'
                                 % (i, hit.get('source_string'), hit.get('target_string')))
            parts.append('')
        parts.append('SOURCE:\n%s' % src)
        text, rec = translator.chat(sys_tr, '\n'.join(parts),
                                    'tr-%s' % (card.get('fragment_id') or card.get('slp1')))
        _record('translate', rec)
        hyp = ''
        if rec.get('error') and not text:
            hyp = ''
        else:
            try:
                parsed = json.loads(text or '')
                hyp = parsed.get('text') or ''
            except Exception:
                hyp = (text or '').strip()
        tokens = (rec.get('prompt_tokens') or 0) + (rec.get('completion_tokens') or 0)
        return {
            'text': hyp,
            'tokens': tokens,
            'cost_usd': rec.get('cost_usd') or 0.0,
            'route': 'deepseek',
            'model': rec.get('served_model') or model,
            'transport': rec,
        }

    sys_j = (
        'Score a source-to-Russian translation. '
        'Return JSON with keys: quality (0..1 float), serious_error (bool), '
        'equivalence (correct|partial|wrong), notes (short string). '
        'serious_error = wrong sense, invented meaning, or destroyed markup. '
        'If reference is null this is reference-free QE: judge the hypothesis '
        'against the source only.'
    )

    def judge_fn(card, out):
        src = card.get('source_string') or card.get('sa') or ''
        ref = card.get('target_reference') or card.get('ru_reference')
        payload = {
            'source': src,
            'hypothesis': out.get('text'),
        }
        if card.get('qe_reference_free'):
            payload['reference'] = None
        else:
            payload['reference'] = ref
        user = json.dumps(payload, ensure_ascii=False)
        text, rec = judge.chat(sys_j, user,
                               'jd-%s' % (card.get('fragment_id') or card.get('slp1')))
        _record('judge', rec)
        try:
            parsed = json.loads(text)
        except Exception:
            parsed = {'quality': None, 'serious_error': True,
                      'equivalence': 'wrong', 'notes': 'judge-json-fail'}
        q = parsed.get('quality')
        try:
            q = float(q) if q is not None else None
        except (TypeError, ValueError):
            q = None
        return {
            'quality': q,
            'serious_error': bool(parsed.get('serious_error')),
            'equivalence': parsed.get('equivalence'),
            'notes': parsed.get('notes'),
            'tokens': (rec.get('prompt_tokens') or 0) + (rec.get('completion_tokens') or 0),
            'cost_usd': rec.get('cost_usd') or 0.0,
        }

    return translate_fn, judge_fn, ledger


def _per_class(rows, key):
    buckets = defaultdict(list)
    for r in rows:
        buckets[r.get('fragment_class') or 'unknown'].append(r)
    out = {}
    for klass, items in sorted(buckets.items()):
        quals = [i['quality'] for i in items if i.get('quality') is not None]
        out[klass] = {
            'n': len(items),
            'mean_quality': (sum(quals) / len(quals)) if quals else None,
            'mean_edit': sum(i['edit'] for i in items) / len(items),
            'serious_error_n': sum(1 for i in items if i.get('serious_error')),
        }
    return out


def _render_blocked_md(n_cards):
    lines = []
    lines.append('# RETRIEVAL_EVAL — H2686 / H1457 A6 retrieval measurement')
    lines.append('')
    lines.append('_Created: 22-07-2026 · Last updated: 14-08-2026_')
    lines.append('')
    lines.append('Harness: `tm_retrieval_eval.py` (Grok 4.6, `grok-4.6`), H2686 Track D. '
                 'Requested engine=`none`. Cards in the named batch: %d.' % n_cards)
    lines.append('')
    lines.append('## Status: BLOCKED — `--engine none` makes no live call')
    lines.append('')
    lines.append('No fabricated quality, latency, token or cost numbers are reported. '
                 'Run `--engine deepseek` when a key is reachable.')
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    lines.append('')
    return '\n'.join(lines)


def _render_live_md(meta, no_tm, with_tm):
    if meta.get('engine') not in LIVE_ENGINES:
        raise ValueError('live renderer refuses engine=%r' % meta.get('engine'))
    if meta.get('mock'):
        raise ValueError('live renderer refuses mock results')
    lines = []
    lines.append('# RETRIEVAL_EVAL — H2686 live no-TM vs graded-fragment-TM')
    lines.append('')
    lines.append('_Created: 22-07-2026 · Last updated: 14-08-2026_')
    lines.append('')
    lines.append('Harness: [`tm_retrieval_eval.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_retrieval_eval.py) '
                 '(Grok 4.6, `grok-4.6`). Engine **%s** / model **%s**. '
                 'Frozen batch sha256 `%s`. Gold sha256 `%s`.'
                 % (meta['engine'], meta.get('model'), meta.get('batch_sha256'),
                    meta.get('gold_sha256')))
    lines.append('')
    lines.append('Wave 1 is immutable. This measurement does not rewrite promoted '
                 'or quarantined Wave-1 fragments.')
    lines.append('')
    lines.append('## Status: LIVE')
    lines.append('')
    lines.append('| Arm | n | mean quality | serious error | mean edit | tokens | wall s | cost USD | exact reuse | fragment reuse |')
    lines.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for name, arm in (('no-TM', no_tm), ('fragment-TM', with_tm)):
        lines.append('| %s | %d | %s | %d/%d (%.1f%%) | %.3f | %d | %.2f | %.6f | %d | %d |' % (
            name, arm['n'],
            ('%.3f' % arm['mean_quality']) if arm['mean_quality'] == arm['mean_quality'] else 'nan',
            arm['serious_error_n'], arm['n'], 100 * arm['serious_error_rate'],
            arm['mean_edit'], arm['total_tokens'], arm['total_wall_clock_s'],
            arm['total_cost_usd'], arm['exact_reuse_n'], arm['fragment_reuse_n']))
    dq = (with_tm['mean_quality'] - no_tm['mean_quality']
          if (with_tm['mean_quality'] == with_tm['mean_quality']
              and no_tm['mean_quality'] == no_tm['mean_quality']) else float('nan'))
    de = with_tm['mean_edit'] - no_tm['mean_edit']
    ds = with_tm['serious_error_rate'] - no_tm['serious_error_rate']
    lines.append('')
    lines.append('Deltas (TM − no-TM): quality **%+.3f**, edit **%+.3f**, '
                 'serious-error rate **%+.3f**, tokens **%+d**, wall **%+.2f s**, '
                 'cost **%+.6f USD**.'
                 % (dq, de, ds,
                    with_tm['total_tokens'] - no_tm['total_tokens'],
                    with_tm['total_wall_clock_s'] - no_tm['total_wall_clock_s'],
                    with_tm['total_cost_usd'] - no_tm['total_cost_usd']))
    lines.append('')
    lines.append('## Per fragment class (TM arm)')
    lines.append('')
    lines.append('| Class | n | mean quality | mean edit | serious error |')
    lines.append('|---|---:|---:|---:|---:|')
    for klass, st in _per_class(with_tm['rows'], 'fragment_class').items():
        mq = 'nan' if st['mean_quality'] is None else '%.3f' % st['mean_quality']
        lines.append('| %s | %d | %s | %.3f | %d |'
                     % (klass, st['n'], mq, st['mean_edit'], st['serious_error_n']))
    lines.append('')
    lines.append('## Route / cost provenance')
    lines.append('')
    lines.append('- Translate+judge route: `%s`' % meta.get('route'))
    lines.append('- Requested model: `%s`' % meta.get('model'))
    lines.append('- Price card: `%s`' % meta.get('price_card'))
    lines.append('- Ledger calls: **%d** (translate + judge, both arms)' % meta.get('ledger_calls', 0))
    lines.append('- Total cost USD: **%.6f**' % meta.get('total_cost_usd', 0.0))
    lines.append('- Mock: **%s**' % meta.get('mock'))
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    lines.append('')
    return '\n'.join(lines)


def cmd_run(a):
    if not os.path.exists(a.batch):
        sys.exit('eval batch not found: %s (run `freeze` first)' % a.batch)
    cards = load_jsonl(a.batch)
    if a.engine == ENGINE_NONE:
        md = _render_blocked_md(len(cards))
        with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
            f.write(md)
        print('run: --engine none -> no live call; %s' % a.out)
        return 0

    if a.engine != ENGINE_DEEPSEEK:
        sys.exit('run: --engine %s not implemented' % a.engine)

    key, key_src = load_deepseek_key()
    if not key:
        # one backend/route repair: look again at ORS-FAQ after the sibling
        repair = os.path.join(GITHUB, 'ORS-FAQ', '.env')
        if os.path.isfile(repair) and repair not in candidate_env_files():
            pass
        sys.exit('run: no DEEPSEEK_API_KEY in env or known .env paths; '
                 'one route repair already searched environ + %s'
                 % candidate_env_files())

    translate_fn, judge_fn, ledger = make_deepseek_fns(key, model=a.model)
    exclude = {c.get('fragment_id') for c in cards}
    tm_rows = sample_tm_rows(a.sample, exclude) + publication_tm_rows(a.publication)
    tm_index = {'_rows': tm_rows}

    print('run: live deepseek n=%d tm_rows=%d key_src=%s' % (
        len(cards), len(tm_rows), 'environ' if key_src == 'environ' else 'file'))
    no_tm = run_arm(cards, translate_fn, judge_fn, tm_index=None)
    with_tm = run_arm(cards, translate_fn, judge_fn, tm_index=tm_index)

    price_card = None
    served = set()
    for rec in ledger:
        price_card = rec.get('price_card') or price_card
        if rec.get('served_model'):
            served.add(rec['served_model'])
    total_cost = sum(float(r.get('cost_usd') or 0) for r in ledger)
    meta = {
        'schema': 'pwg.tm.retrieval_eval.live.v1',
        'version': VERSION,
        'engine': ENGINE_DEEPSEEK,
        'route': 'https://api.deepseek.com/chat/completions',
        'model': a.model,
        'served_models': sorted(served),
        'price_card': price_card,
        'mock': False,
        'batch_sha256': sha256_file(a.batch),
        'gold_sha256': sha256_file(DEFAULT_GRADE_GOLD),
        'sample_sha256': sha256_file(a.sample) if os.path.exists(a.sample) else None,
        'tm_index_n': len(tm_rows),
        'ledger_calls': len(ledger),
        'total_cost_usd': round(total_cost, 6),
        'wave1_immutable': True,
    }
    payload = {'meta': meta, 'no_tm': no_tm, 'with_tm': with_tm, 'ledger': ledger}
    with open(a.live_json, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write('\n')
    with open(a.ledger, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'meta': meta, 'calls': ledger}, f, ensure_ascii=False, indent=2)
        f.write('\n')
    md = _render_live_md(meta, no_tm, with_tm)
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(md)
    print('run: LIVE no-TM Q=%.3f se=%d/%d | TM Q=%.3f se=%d/%d cost=%.6f -> %s'
          % (no_tm['mean_quality'], no_tm['serious_error_n'], no_tm['n'],
             with_tm['mean_quality'], with_tm['serious_error_n'], with_tm['n'],
             total_cost, a.out))
    return 0


def _mock_translate_no_context(card, context):
    time.sleep(0.001)
    return {'text': card.get('slp1', '') + '_baseline', 'tokens': 10, 'cost_usd': 0.0}


def _mock_translate_with_context(card, context):
    time.sleep(0.001)
    suffix = '_ctx' if context else '_baseline'
    return {'text': card.get('slp1', '') + suffix, 'tokens': 12 if context else 10,
            'cost_usd': 0.0}


def _mock_judge(card, out):
    return {'quality': 0.9 if str(out.get('text', '')).endswith('_ctx') else 0.6,
            'serious_error': False, 'equivalence': 'partial'}


def selftest():
    cards = [{'slp1': 'karman', 'ru_reference': 'действие', 'source_string': 'Werk',
              'target_reference': 'действие', 'fragment_class': 'definition_gloss',
              'fragment_id': 'a'},
             {'slp1': 'yoga', 'ru_reference': 'йога', 'source_string': 'Yoga',
              'target_reference': 'йога', 'fragment_class': 'definition_gloss',
              'fragment_id': 'b'}]
    tm_index = {'karman': 'действие (TM match)'}

    no_tm = run_arm(cards, _mock_translate_no_context, _mock_judge)
    with_tm = run_arm(cards, _mock_translate_with_context, _mock_judge, tm_index=tm_index)

    assert no_tm['mean_quality'] < with_tm['mean_quality'], \
        'the mock context-aided arm must score higher, got %s vs %s' % (no_tm, with_tm)
    assert with_tm['total_tokens'] >= no_tm['total_tokens']
    assert all('wall_clock_s' in r for r in no_tm['rows'])
    assert all('edit' in r for r in no_tm['rows'])
    assert len(fuzzy_context({'slp1': 'karman'}, tm_index)) == 1
    assert len(fuzzy_context({'slp1': 'nonexistent'}, tm_index)) == 0
    assert abs(norm_edit('abc', 'abc')) < 1e-9
    assert norm_edit('abc', 'axc') > 0

    try:
        _render_live_md({'engine': 'none', 'mock': False}, no_tm, with_tm)
        raise AssertionError('live renderer must refuse engine=none')
    except ValueError:
        pass
    try:
        _render_live_md({'engine': ENGINE_DEEPSEEK, 'mock': True,
                         'batch_sha256': 'x', 'gold_sha256': 'y',
                         'route': 'r', 'model': 'm', 'price_card': 'p',
                         'ledger_calls': 0, 'total_cost_usd': 0}, no_tm, with_tm)
        raise AssertionError('live renderer must refuse mock=True')
    except ValueError:
        pass

    print('tm_retrieval_eval selftest OK -- run_arm deltas, freeze guards, '
          'live renderer refuses mocks')
    return 0


def main():
    ap = argparse.ArgumentParser(
        description='H2686 A6 -- live retrieval measurement (TM as fuzzy context)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    b = sub.add_parser('batch', help='legacy grade-A gold batch')
    b.add_argument('--grade-gold', dest='grade_gold', default=DEFAULT_GRADE_GOLD)
    b.add_argument('--n', type=int, default=20)
    b.add_argument('--out', default=DEFAULT_BATCH)

    fr = sub.add_parser('freeze', help='freeze paired DE-RU batch from H2684 sample400')
    fr.add_argument('--sample', default=DEFAULT_SAMPLE)
    fr.add_argument('--adjudication', default=DEFAULT_ADJ)
    fr.add_argument('--n-per-class', dest='n_per_class', type=int, default=4)
    fr.add_argument('--out', default=DEFAULT_BATCH)
    fr.add_argument('--manifest', default=DEFAULT_MANIFEST)

    r = sub.add_parser('run', help='run the no-TM vs with-TM measurement')
    r.add_argument('--batch', default=DEFAULT_BATCH)
    r.add_argument('--engine', choices=[ENGINE_NONE, ENGINE_DEEPSEEK], default=ENGINE_NONE)
    r.add_argument('--model', default=DEEPSEEK_MODEL)
    r.add_argument('--sample', default=DEFAULT_SAMPLE)
    r.add_argument('--publication', default=DEFAULT_PUBLICATION)
    r.add_argument('--out', default=DEFAULT_OUT)
    r.add_argument('--live-json', dest='live_json', default=DEFAULT_LIVE_JSON)
    r.add_argument('--ledger', default=DEFAULT_LEDGER)

    sub.add_parser('selftest', help='deterministic mock-engine asserts')

    a = ap.parse_args()
    if a.cmd == 'batch':
        return cmd_batch(a)
    if a.cmd == 'freeze':
        return cmd_freeze(a)
    if a.cmd == 'run':
        return cmd_run(a)
    if a.cmd == 'selftest':
        return selftest()
    return 1


if __name__ == '__main__':
    sys.exit(main())
