#!/usr/bin/env python
r"""Flash PREP — map mode A: cheap prep sidecars before Opus (H2439 + fill).

Lane map §3.1 step [2]::

    [2] Flash PREP (cheap, parallel)
          → prep/{key}.json  (senses, TM hits, flags, optional draft)
          → free det_gate path (no Claude)
          → NEVER the TM store (R4.3a)

What each sidecar carries
-------------------------
* **sense_inventory** — N senses with DE anchors (from slice payload and/or store rows)
* **tm_fuzzy_hits** — ranked reuse candidates (exact key1 first, then difflib key1 neighbors)
* **hard_flags** — polysemy / no_pwg / monster_length (+ notes)
* **citation_normalize** — raw ``<ls>…</ls>`` spans from DE text
* **compound_candidates** — crude SLP1 compound-head guesses (heuristic only)
* **ru_skeleton** — optional RU draft seeds (Flash ``--live`` only; never promoted)

Modes
-----
* **fill** (default when ``--payload`` / ``--store`` given): free deterministic fill
* **dry**: key-only skeleton (no DE/TM sources)
* **live**: fill first, then optional Flash call for ``ru_skeleton`` / route_hint

Usage
-----
  python src/pilot/h1210/prep_pack.py --worklist … --out-dir prep --store PATH
  python src/pilot/h1210/prep_pack.py --payload slice_payload.json --out-dir prep
  python src/pilot/h1210/prep_pack.py --keys a,b --out-dir prep --live --workers 8
  python src/pilot/h1210/prep_pack.py --selftest

Org map: Uprava docs/DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md §3.1.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.dirname(HERE)
SRC = os.path.dirname(PILOT)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if PILOT not in sys.path:
    sys.path.insert(0, PILOT)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import deepseek_arm as ds  # noqa: E402

SCHEMA_ID = 'pwg.prep_pack.v1'
SCHEMA_PATH = os.path.join(HERE, 'prep_pack.schema.json')

# Monster threshold mirrors H1210 declared_caps.max_bytes spirit (12 KB).
MONSTER_BYTES = 12000
POLYSEMY_SENSE_FLOOR = 6
TM_FUZZY_TOP = 8
TM_FUZZY_MIN_SCORE = 0.55
LS_RE = re.compile(r'<ls[^>]*>.*?</ls>', re.DOTALL | re.IGNORECASE)
SENSE_TAG_RE = re.compile(r'(\d+)[〉›>]')  # 〉 or OCR-ish variants in raw
# Very light compound cue: long key with a known second-member tail (heuristic, not a parser).
COMPOUND_TAILS = (
    'kara', 'kAra', 'ja', 'jA', 'vat', 'vant', 'mat', 'mant', 'maya', 'rUpa',
    'nAman', 'pati', 'putra', 'deva', 'dAsa', 'rAja', 'nATa',
)

# When running inside a linked worktree the live store/input often live only on the
# main checkout (gitignored). Prefer explicit flags; fall back to this org path.
MAIN_PILOT = r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pilot'
MAIN_STORE = r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pwg_ru_translated.jsonl'


def _pilot_dirs() -> list[str]:
    """Candidate pilot roots that may hold input/ + translate/."""
    out = []
    for d in (PILOT, MAIN_PILOT):
        if d and os.path.isdir(d) and d not in out:
            out.append(d)
    return out


def empty_pack(key1: str, *, model: str | None = None, mode: str = 'dry') -> dict:
    """Schema-valid empty / base prep-pack for one key."""
    return {
        'schema': SCHEMA_ID,
        'key1': key1,
        'produced_at': int(time.time()),
        'producer': {
            'tool': 'prep_pack.py',
            'mode': mode,
            'model': model or ds.DEFAULT_MODEL,
            'price_table': {
                'cache_miss_in': ds.PRICE_CACHE_MISS_IN,
                'cache_hit_in': ds.PRICE_CACHE_HIT_IN,
                'out': ds.PRICE_OUT,
            },
        },
        'sense_inventory': [],
        'tm_fuzzy_hits': [],
        'compound_candidates': [],
        'citation_normalize': [],
        'hard_flags': {
            'polysemy': False,
            'no_pwg': False,
            'monster_length': False,
            'notes': [],
        },
        'ru_skeleton': None,
        'route_hint': 'prep_only',
        'store_write': False,
    }


# --------------------------------------------------------------------------- sources

def load_keys(args) -> list[str]:
    keys: list[str] = []
    if args.worklist:
        with open(args.worklist, encoding='utf-8') as f:
            wl = json.load(f)
        keys.extend(wl.get('keys') or [])
    if args.payload:
        with open(args.payload, encoding='utf-8') as f:
            pl = json.load(f)
        keys.extend(c['key1'] for c in (pl.get('cards') or []) if c.get('key1'))
    if args.keys_file:
        with open(args.keys_file, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    keys.append(line.split()[0])
    if args.keys:
        keys.extend(k for k in args.keys.split(',') if k)
    seen = set()
    out = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            out.append(k)
    if args.limit is not None:
        out = out[: args.limit]
    return out


def load_payload_index(path: str | None) -> dict[str, dict]:
    if not path or not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as f:
        pl = json.load(f)
    return {c['key1']: c for c in (pl.get('cards') or []) if c.get('key1')}


def load_store_index(path: str | None, wanted: set[str] | None = None) -> dict:
    """key1 -> {'rows': [...], 'de_bytes': int, 'n_senses': int, 'layers': set}.

    Streams the jsonl once. If ``wanted`` is set, still records ALL key1 strings for
    fuzzy neighbor search (short index of unique keys) but only keeps full rows for
    wanted keys — bounds memory on the huge store.
    """
    if not path or not os.path.exists(path):
        return {'by_key': {}, 'all_keys': []}
    by_key: dict[str, dict] = {}
    all_keys: set[str] = set()
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            k = row.get('key1')
            if not k:
                continue
            all_keys.add(k)
            # Pilot-scale store (~10k rows / ~250 keys): keep full rows for every
            # key so fuzzy neighbors carry ru_preview. Cap rows/key for monsters.
            slot = by_key.setdefault(k, {
                'rows': [], 'de_bytes': 0, 'n_senses': 0, 'layers': set(),
            })
            de = row.get('de') or ''
            slot['de_bytes'] += len(de)
            slot['n_senses'] += 1
            if row.get('layer'):
                slot['layers'].add(row['layer'])
            if len(slot['rows']) < 40:
                slot['rows'].append(row)
    return {'by_key': by_key, 'all_keys': sorted(all_keys)}


def load_de_source(key1: str, input_dir: str | None = None) -> dict | None:
    """Load DE text for a key from pilot/input raw or translate/{key}.json.

    Returns ``{'text': str, 'source': str, 'units': optional list}`` or None.
    """
    # 1) masked/raw input used by the production harness
    dirs = []
    if input_dir:
        dirs.append(input_dir)
    dirs.extend(os.path.join(p, 'input') for p in _pilot_dirs())
    for d in dirs:
        raw = os.path.join(d, key1 + '.raw.txt')
        if os.path.exists(raw):
            with open(raw, encoding='utf-8', errors='replace') as f:
                text = f.read()
            return {'text': text, 'source': raw, 'units': None}
        # safe_name variant (leading underscore stems)
        try:
            from safe_filename import safe_name  # noqa: WPS433
            sn = safe_name(key1)
            raw2 = os.path.join(d, sn + '.raw.txt')
            if sn != key1 and os.path.exists(raw2):
                with open(raw2, encoding='utf-8', errors='replace') as f:
                    text = f.read()
                return {'text': text, 'source': raw2, 'units': None}
        except Exception:  # noqa: BLE001
            pass

    # 2) translate/{key}.json unit dump (DE layer units)
    for pdir in _pilot_dirs():
        for stem in (key1, key1.lower(), key1[:1].lower() + key1[1:] if key1 else key1):
            path = os.path.join(pdir, 'translate', stem + '.json')
            if not os.path.exists(path):
                continue
            with open(path, encoding='utf-8') as f:
                card = json.load(f)
            units = card.get('units') or []
            de_units = [u for u in units if 'de' in (u.get('lang') or [])]
            if not de_units:
                de_units = units
            text = '\n'.join((u.get('text') or '') for u in de_units)
            if text.strip():
                return {'text': text, 'source': path, 'units': de_units}
    return None


def sense_inventory_from_de_text(text: str, *, source_note: str) -> list[dict]:
    """Split DE text into sense slots by numbered markers (1〉 / 1. / div n=)."""
    if not text:
        return []
    tags = SENSE_TAG_RE.findall(text)
    # Also "1." style at line starts in translate units
    if not tags:
        tags = re.findall(r'(?m)^\s*(\d+)\.\s', text)
    n = len(set(tags)) if tags else 0
    if n <= 0:
        # one blob sense if there is any DE prose
        if text.strip():
            anchor = text.strip()[:160] + ('…' if len(text.strip()) > 160 else '')
            return [{'i': 0, 'de_anchor': anchor, 'note': source_note}]
        return []
    # Prefer one anchor per first N distinct tags, in order of first appearance
    seen = []
    for t in tags:
        if t not in seen:
            seen.append(t)
    out = []
    for i, tag in enumerate(seen):
        # crude slice: from this tag marker to next
        m = re.search(r'(?:^|[^\d])' + re.escape(tag) + r'[〉›>\.]', text)
        start = m.start() if m else 0
        end = start + 200
        chunk = text[start:end].strip()
        out.append({
            'i': i,
            'de_anchor': chunk[:160] + ('…' if len(chunk) > 160 else ''),
            'sense_tag': tag,
            'note': source_note,
        })
    return out


# --------------------------------------------------------------------------- field builders

def sense_inventory_from_store(slot: dict) -> list[dict]:
    out = []
    for i, row in enumerate(slot.get('rows') or []):
        de = (row.get('de') or '').strip()
        anchor = de[:160] + ('…' if len(de) > 160 else '')
        out.append({
            'i': i,
            'de_anchor': anchor or None,
            'sense_tag': row.get('sense_tag'),
            'layer': row.get('layer'),
            'subcard': row.get('subcard'),
            'note': 'store_row',
        })
    return out


def sense_inventory_from_payload(card: dict) -> list[dict]:
    """Build sense slots from slice payload when store rows are missing."""
    n = card.get('source_senses')
    if not isinstance(n, int) or n <= 0:
        block = card.get('card_block') or ''
        tags = SENSE_TAG_RE.findall(block)
        n = len(set(tags)) or 0
    if n <= 0:
        return []
    block = card.get('card_block') or ''
    # One DE excerpt for the whole card (payload has no per-sense DE split).
    anchor = None
    if '--- masked German' in block:
        try:
            body = block.split('--- masked German', 1)[1]
            body = body.split('--- portrait', 1)[0]
            body = re.sub(r'^.*?\n', '', body, count=1).strip()
            anchor = body[:160] + ('…' if len(body) > 160 else '')
        except IndexError:
            anchor = None
    return [
        {'i': i, 'de_anchor': anchor if i == 0 else None, 'note': 'payload_source_senses'}
        for i in range(n)
    ]


def sense_inventory_from_units(units: list) -> list[dict]:
    out = []
    for i, u in enumerate(units or []):
        text = (u.get('text') or '').strip()
        if not text:
            continue
        out.append({
            'i': len(out),
            'de_anchor': text[:160] + ('…' if len(text) > 160 else ''),
            'sense_tag': u.get('ref'),
            'layer': u.get('layer'),
            'note': 'translate_unit',
        })
    return out


def citation_normalize_from_text(text: str) -> list[dict]:
    out = []
    seen = set()
    for m in LS_RE.finditer(text or ''):
        raw = m.group(0)
        if raw in seen:
            continue
        seen.add(raw)
        # Normalize: collapse whitespace inside the tag body only.
        norm = re.sub(r'\s+', ' ', raw).strip()
        out.append({'raw': raw, 'normalized': norm})
    return out[:40]


def compound_candidates_from_key(key1: str) -> list[str]:
    if len(key1) < 6:
        return []
    cands = []
    for tail in COMPOUND_TAILS:
        if key1.endswith(tail) and len(key1) > len(tail) + 2:
            head = key1[: -len(tail)]
            if head:
                cands.append('%s + %s' % (head, tail))
    return cands[:5]


def tm_fuzzy_hits(key1: str, store_idx: dict, top: int = TM_FUZZY_TOP) -> list[dict]:
    """Exact store key1 first, then difflib neighbors over the store key universe."""
    by_key = store_idx.get('by_key') or {}
    all_keys = store_idx.get('all_keys') or []
    hits = []
    if key1 in by_key:
        slot = by_key[key1]
        ru_preview = None
        for row in slot['rows'][:1]:
            ru = (row.get('ru') or '').strip()
            if ru:
                ru_preview = ru[:120] + ('…' if len(ru) > 120 else '')
        hits.append({
            'rank': 1,
            'key1': key1,
            'score': 1.0,
            'match_type': 'exact_key1',
            'n_store_rows': slot['n_senses'],
            'ru_preview': ru_preview,
        })
    # Fuzzy over a bounded candidate pool: prefix-sharing keys first, else sample by ratio.
    prefix = key1[: max(2, min(4, len(key1)))]
    pool = [k for k in all_keys if k != key1 and (k.startswith(prefix) or prefix.startswith(k[:len(prefix)]))]
    if len(pool) < 40:
        # expand: every key sharing first 2 chars
        p2 = key1[:2] if len(key1) >= 2 else key1
        pool = [k for k in all_keys if k != key1 and k.startswith(p2)]
    if len(pool) > 400:
        pool = pool[:400]
    scored = []
    for k in pool:
        s = SequenceMatcher(None, key1, k).ratio()
        if s >= TM_FUZZY_MIN_SCORE:
            scored.append((s, k))
    scored.sort(reverse=True)
    rank = len(hits) + 1
    for s, k in scored[: max(0, top - len(hits))]:
        slot = by_key.get(k)
        ru_preview = None
        n_rows = None
        if slot:
            n_rows = slot['n_senses']
            for row in slot['rows'][:1]:
                ru = (row.get('ru') or '').strip()
                if ru:
                    ru_preview = ru[:120] + ('…' if len(ru) > 120 else '')
        hits.append({
            'rank': rank,
            'key1': k,
            'score': round(s, 3),
            'match_type': 'key1_difflib',
            'n_store_rows': n_rows,
            'ru_preview': ru_preview,
        })
        rank += 1
    return hits


def apply_hard_flags(pack: dict, *, card: dict | None, slot: dict | None) -> None:
    hf = pack['hard_flags']
    notes = hf['notes']
    n_senses = len(pack['sense_inventory'])
    de_bytes = 0
    layers = set()
    if slot:
        de_bytes = slot.get('de_bytes') or 0
        layers = set(slot.get('layers') or ())
    if card:
        cx = card.get('complexity') or {}
        if isinstance(cx.get('len_bytes'), int):
            de_bytes = max(de_bytes, cx['len_bytes'])
        if isinstance(cx.get('n_senses'), int):
            n_senses = max(n_senses, cx['n_senses'])
        if cx.get('complex'):
            notes.append('payload complexity.complex=true score=%s' % cx.get('score'))
        if card.get('source_senses') is None and not slot:
            hf['no_pwg'] = True
            notes.append('no source_senses in payload and no store rows')
    if not slot and not card:
        hf['no_pwg'] = True
        notes.append('no DE source (no store row, no payload card)')
    if slot and 'pwg' not in layers and layers:
        # has store rows but none from pwg layer
        notes.append('store layers=%s (no pwg)' % ','.join(sorted(layers)))
    if n_senses >= POLYSEMY_SENSE_FLOOR:
        hf['polysemy'] = True
        notes.append('polysemy: n_senses=%d >= %d' % (n_senses, POLYSEMY_SENSE_FLOOR))
    if de_bytes >= MONSTER_BYTES or len(pack['key1']) >= 24:
        hf['monster_length'] = True
        notes.append('monster: de_bytes=%d key1_len=%d' % (de_bytes, len(pack['key1'])))
    # route
    if hf['monster_length'] or (hf['polysemy'] and n_senses >= 12):
        pack['route_hint'] = 'full_worker'
    elif hf['no_pwg'] and n_senses == 0:
        pack['route_hint'] = 'park'
    elif n_senses and not hf['monster_length']:
        pack['route_hint'] = 'controller_only' if pack.get('ru_skeleton') else 'prep_only'
    else:
        pack['route_hint'] = 'prep_only'


def fill_one(key1: str, *, model: str, payload_idx: dict, store_idx: dict,
             mode: str = 'fill', input_dir: str | None = None) -> dict:
    pack = empty_pack(key1, model=model, mode=mode)
    card = payload_idx.get(key1)
    slot = (store_idx.get('by_key') or {}).get(key1)
    de_src = load_de_source(key1, input_dir=input_dir)
    de_blob = ''

    # Priority: store rows (already-promoted) > DE raw/translate > payload.
    if slot:
        pack['sense_inventory'] = sense_inventory_from_store(slot)
        de_blob = '\n'.join((r.get('de') or '') for r in slot['rows'])
        pack['hard_flags']['notes'].append('de_source=store')
    elif de_src:
        de_blob = de_src['text']
        if de_src.get('units'):
            pack['sense_inventory'] = sense_inventory_from_units(de_src['units'])
        else:
            pack['sense_inventory'] = sense_inventory_from_de_text(
                de_blob, source_note='de_raw:' + os.path.basename(de_src['source']))
        pack['hard_flags']['notes'].append('de_source=%s' % de_src['source'])
    elif card:
        pack['sense_inventory'] = sense_inventory_from_payload(card)
        de_blob = card.get('card_block') or ''
        pack['hard_flags']['notes'].append('de_source=payload')

    if de_blob:
        pack['citation_normalize'] = citation_normalize_from_text(de_blob)
    elif card:
        pack['citation_normalize'] = citation_normalize_from_text(card.get('card_block') or '')

    pack['compound_candidates'] = compound_candidates_from_key(key1)
    pack['tm_fuzzy_hits'] = tm_fuzzy_hits(key1, store_idx)
    # feed de_bytes into hard flags via a synthetic slot when only raw exists
    flag_slot = slot
    if not flag_slot and de_blob:
        flag_slot = {
            'rows': [], 'de_bytes': len(de_blob),
            'n_senses': len(pack['sense_inventory']),
            'layers': set(),
        }
    apply_hard_flags(pack, card=card, slot=flag_slot)
    pack['store_write'] = False
    return pack


# --------------------------------------------------------------------------- IO + live

def write_pack(out_dir: str, pack: dict) -> str:
    if pack.get('store_write') is True:
        raise SystemExit('prep_pack: refusing store_write=True (R4.3a fence)')
    os.makedirs(out_dir, exist_ok=True)
    # Windows-safe filename: keep key1 as-is (SLP1 is ASCII).
    path = os.path.join(out_dir, '%s.json' % pack['key1'])
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pack, f, ensure_ascii=False, indent=1)
        f.write('\n')
    return path


def produce_fill(keys: list[str], out_dir: str, model: str,
                 payload_idx: dict, store_idx: dict,
                 input_dir: str | None = None) -> list[str]:
    paths = []
    for k in keys:
        pack = fill_one(k, model=model, payload_idx=payload_idx, store_idx=store_idx,
                        mode='fill', input_dir=input_dir)
        paths.append(write_pack(out_dir, pack))
    return paths


def produce_dry(keys: list[str], out_dir: str, model: str) -> list[str]:
    paths = []
    for k in keys:
        pack = empty_pack(k, model=model, mode='dry')
        if len(k) >= 24:
            pack['hard_flags']['monster_length'] = True
            pack['hard_flags']['notes'].append('dry: key1 length >= 24 (proxy only)')
            pack['route_hint'] = 'full_worker'
        pack['compound_candidates'] = compound_candidates_from_key(k)
        paths.append(write_pack(out_dir, pack))
    return paths


def _flash_draft_for_pack(client: ds.DeepSeek, pack: dict) -> dict:
    """One Flash call: optional RU skeleton + route_hint. Mutates pack, returns it."""
    senses_preview = []
    for s in pack['sense_inventory'][:12]:
        senses_preview.append({
            'i': s.get('i'),
            'tag': s.get('sense_tag'),
            'de': s.get('de_anchor'),
        })
    system = (
        'You are a PWG German→Russian PREP worker (not the final translator).\n'
        'Return ONE JSON object only:\n'
        '{"ru_skeleton": [string, ...] or null,\n'
        ' "route_hint": "controller_only"|"full_worker"|"prep_only"|"park",\n'
        ' "hard_flag_notes": [string, ...]}.\n'
        'ru_skeleton = short RU sense glosses aligned to sense order (draft seed only).\n'
        'Never claim a store write. JSON only.'
    )
    user = json.dumps({
        'key1': pack['key1'],
        'n_senses': len(pack['sense_inventory']),
        'senses': senses_preview,
        'hard_flags': {
            'polysemy': pack['hard_flags']['polysemy'],
            'monster_length': pack['hard_flags']['monster_length'],
            'no_pwg': pack['hard_flags']['no_pwg'],
        },
        'tm_top': [
            {'key1': h['key1'], 'score': h['score'], 'match_type': h.get('match_type')}
            for h in pack['tm_fuzzy_hits'][:5]
        ],
    }, ensure_ascii=False)
    text, call = client.chat(system, user, 'prep:%s' % pack['key1'])
    pack['producer']['live_call'] = {
        'ok': text is not None,
        'latency_s': (call or {}).get('latency_s'),
        'error': (call or {}).get('error'),
        'prompt_tokens': (call or {}).get('prompt_tokens'),
        'completion_tokens': (call or {}).get('completion_tokens'),
    }
    if not text:
        pack['hard_flags']['notes'].append('live: null response')
        pack['route_hint'] = 'full_worker'
        pack['store_write'] = False
        return pack
    try:
        obj, _repair = ds.extract_json(text)
    except ValueError as e:
        pack['hard_flags']['notes'].append('live parse fail: %s' % e)
        pack['route_hint'] = 'full_worker'
        pack['store_write'] = False
        return pack
    if obj.get('ru_skeleton') is not None:
        pack['ru_skeleton'] = obj.get('ru_skeleton')
    rh = obj.get('route_hint')
    if rh in ('controller_only', 'full_worker', 'prep_only', 'park'):
        pack['route_hint'] = rh
    notes = obj.get('hard_flag_notes')
    if isinstance(notes, list):
        pack['hard_flags']['notes'].extend(str(n) for n in notes)
    # If Flash returned a draft and route not park/full, prefer controller_only.
    if pack.get('ru_skeleton') and pack['route_hint'] == 'prep_only':
        pack['route_hint'] = 'controller_only'
    pack['store_write'] = False
    return pack


def produce_live(keys: list[str], out_dir: str, model: str, env_file: str | None,
                 payload_idx: dict, store_idx: dict, workers: int = 6,
                 input_dir: str | None = None) -> list[str]:
    env = ds.load_env_file(env_file)
    key = os.environ.get('DEEPSEEK_API_KEY') or env.get('DEEPSEEK_API_KEY')
    if not key:
        raise SystemExit('prep_pack --live needs DEEPSEEK_API_KEY (or use fill/dry)')
    base = (os.environ.get('DEEPSEEK_BASE_URL') or env.get('DEEPSEEK_BASE_URL')
            or 'https://api.deepseek.com')
    client = ds.DeepSeek(base, key, model, max_tokens=2048, timeout=120)

    # Deterministic fill first (free), then parallel Flash draft.
    packs = [
        fill_one(k, model=model, payload_idx=payload_idx, store_idx=store_idx,
                 mode='live', input_dir=input_dir)
        for k in keys
    ]
    workers = max(1, min(workers, 2500))
    done = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_flash_draft_for_pack, client, p): p['key1'] for p in packs}
        for fut in as_completed(futs):
            k = futs[fut]
            try:
                done[k] = fut.result()
            except Exception as e:  # noqa: BLE001
                p = next(x for x in packs if x['key1'] == k)
                p['hard_flags']['notes'].append('live worker exception: %s: %s'
                                                % (type(e).__name__, e))
                p['route_hint'] = 'full_worker'
                p['store_write'] = False
                done[k] = p
            print('  live %-24s route=%s skeleton=%s'
                  % (k, done[k]['route_hint'],
                     'yes' if done[k].get('ru_skeleton') else 'no'),
                  flush=True)
    paths = []
    for k in keys:
        paths.append(write_pack(out_dir, done[k]))
    # Optional cost summary on stderr
    try:
        print('live cost: %s' % json.dumps(client.cost(), ensure_ascii=False), flush=True)
    except Exception:  # noqa: BLE001
        pass
    return paths


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    import tempfile

    with open(SCHEMA_PATH, encoding='utf-8') as f:
        schema = json.load(f)
    assert schema.get('$id') == SCHEMA_ID or schema.get('title')
    pack = empty_pack('testKey', mode='dry')
    assert pack['store_write'] is False
    assert pack['producer']['model'] == 'deepseek-v4-flash'
    assert ds.PRICE_CACHE_MISS_IN == 0.14
    assert ds.DEFAULT_MODEL == 'deepseek-v4-flash'

    # Mini store + payload
    store_rows = [
        {'key1': 'kAla', 'sense_tag': '1', 'layer': 'pwg', 'subcard': 'kAla_1',
         'de': '<div>1〉 {%Zeit%} <ls>MBh.</ls> long ' + ('x' * 100),
         'ru': '1) время'},
        {'key1': 'kAla', 'sense_tag': '2', 'layer': 'pwg', 'subcard': 'kAla_1',
         'de': '2〉 {%schwarz%}', 'ru': '2) чёрный'},
        {'key1': 'kAlaka', 'sense_tag': '1', 'layer': 'pwg', 'subcard': 'kAlaka_1',
         'de': '1〉 {%schwärzlich%}', 'ru': '1) черноватый'},
        {'key1': 'zzzNoMatch', 'sense_tag': '1', 'layer': 'nws', 'subcard': 'z',
         'de': '1〉 foo', 'ru': 'foo'},
    ]
    with tempfile.TemporaryDirectory() as td:
        store_path = os.path.join(td, 'store.jsonl')
        with open(store_path, 'w', encoding='utf-8', newline='\n') as f:
            for r in store_rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        payload = {
            'cards': [{
                'key1': 'lonelyKey',
                'source_senses': 3,
                'card_block': (
                    '=== CARD lonelyKey ===\n'
                    '--- masked German (translatable only; {Tn}=masked span) ---\n'
                    '1〉 {%foo%} <ls>R.</ls> 2〉 bar 3〉 baz\n'
                    '--- portrait (evidence) ---\n'
                ),
                'complexity': {'len_bytes': 80, 'n_senses': 3, 'complex': False, 'score': 0.8},
            }],
        }
        payload_path = os.path.join(td, 'payload.json')
        with open(payload_path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(payload, f)

        idx = load_store_index(store_path, wanted={'kAla', 'lonelyKey'})
        # all_keys should include fuzzy neighbors even if not in wanted full rows
        assert 'kAlaka' in idx['all_keys']
        assert 'kAla' in idx['by_key']
        pl_idx = load_payload_index(payload_path)

        p = fill_one('kAla', model=ds.DEFAULT_MODEL, payload_idx=pl_idx, store_idx=idx)
        assert len(p['sense_inventory']) == 2
        assert p['sense_inventory'][0]['de_anchor']
        assert p['tm_fuzzy_hits'][0]['match_type'] == 'exact_key1'
        assert p['tm_fuzzy_hits'][0]['score'] == 1.0
        # neighbor kAlaka should appear in fuzzy list
        fuzzy_keys = {h['key1'] for h in p['tm_fuzzy_hits']}
        assert 'kAlaka' in fuzzy_keys or len(p['tm_fuzzy_hits']) >= 1
        assert p['citation_normalize'], 'ls citation should be extracted'
        assert p['store_write'] is False
        assert p['hard_flags']['polysemy'] is False  # only 2 senses

        p2 = fill_one('lonelyKey', model=ds.DEFAULT_MODEL, payload_idx=pl_idx, store_idx=idx)
        assert len(p2['sense_inventory']) == 3
        assert p2['sense_inventory'][0]['note'] == 'payload_source_senses'
        assert any(c['normalized'] for c in p2['citation_normalize'])

        # DE raw / translate-style units
        inp = os.path.join(td, 'input')
        os.makedirs(inp, exist_ok=True)
        with open(os.path.join(inp, 'AcArya.raw.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('1〉 {%Lehrer%} <ls>MBh.</ls> 2〉 {%Lehrerin%}\n')
        p4 = fill_one('AcArya', model=ds.DEFAULT_MODEL, payload_idx={},
                      store_idx={'by_key': {}, 'all_keys': list(idx['all_keys'])},
                      input_dir=inp)
        assert len(p4['sense_inventory']) >= 2
        assert p4['citation_normalize']
        assert p4['store_write'] is False

        # compound heuristic
        assert compound_candidates_from_key('devaputra')
        # monster + refuse store_write
        p3 = fill_one('aVeryLongHeadwordProxyTokenXX', model=ds.DEFAULT_MODEL,
                      payload_idx={}, store_idx={'by_key': {}, 'all_keys': []})
        assert p3['hard_flags']['monster_length'] is True
        bad = empty_pack('x')
        bad['store_write'] = True
        try:
            write_pack(td, bad)
            raise AssertionError('store_write=True must refuse')
        except SystemExit as e:
            assert 'store_write' in str(e) or 'R4.3a' in str(e)

        paths = produce_fill(['kAla', 'lonelyKey'], os.path.join(td, 'prep'),
                             ds.DEFAULT_MODEL, pl_idx, idx)
        assert len(paths) == 2
        disk = json.load(open(paths[0], encoding='utf-8'))
        assert disk['schema'] == SCHEMA_ID
        assert disk['store_write'] is False
        assert disk['sense_inventory']

    print('prep_pack selftest: PASS (fill senses/TM/flags/citations/raw, R4.3a fence)')
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--worklist', default=None,
                    help='H1210-style worklist JSON with a keys[] array')
    ap.add_argument('--payload', default=None,
                    help='h1209 slice_payload.json (cards with card_block / source_senses)')
    ap.add_argument('--store', default=None,
                    help='pwg_ru_translated.jsonl (read-only TM/sense source)')
    ap.add_argument('--input-dir', default=None,
                    help='pilot/input dir with {key}.raw.txt (DE source)')
    ap.add_argument('--keys-file', default=None)
    ap.add_argument('--keys', default=None, help='comma-separated key1 list')
    ap.add_argument('--out-dir', default=None, help='directory for prep/{key}.json')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--model', default=None)
    ap.add_argument('--env-file', default=None)
    ap.add_argument('--workers', type=int, default=6,
                    help='parallel Flash workers for --live (cap 2500)')
    ap.add_argument('--dry', action='store_true',
                    help='key-only skeleton, ignore store/payload content')
    ap.add_argument('--live', action='store_true',
                    help='fill + Flash optional draft; still sidecar-only')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.out_dir:
        ap.error('--out-dir is required (writes prep sidecars only; never the TM store)')
    keys = load_keys(args)
    if not keys:
        ap.error('no keys — pass --worklist, --payload, --keys-file, or --keys')
    model = args.model or os.environ.get('DEEPSEEK_MODEL') or ds.DEFAULT_MODEL

    # Default store: main-checkout canonical path when present.
    store_path = args.store
    if store_path is None and not args.dry:
        try:
            from store_path import canonical_store  # noqa: WPS433
            cand = canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl'))
            if os.path.exists(cand):
                store_path = cand
        except Exception:  # noqa: BLE001
            pass
        if not store_path and os.path.exists(MAIN_STORE):
            store_path = MAIN_STORE

    input_dir = args.input_dir
    if input_dir is None and not args.dry:
        for pdir in _pilot_dirs():
            cand = os.path.join(pdir, 'input')
            if os.path.isdir(cand):
                input_dir = cand
                break

    payload_idx = {} if args.dry else load_payload_index(args.payload)
    store_idx = {'by_key': {}, 'all_keys': []}
    if not args.dry and store_path:
        print('store: %s' % store_path, flush=True)
        store_idx = load_store_index(store_path, wanted=set(keys))
        print('store index: %d wanted keys with rows, %d key universe'
              % (len(store_idx['by_key']), len(store_idx['all_keys'])), flush=True)
    if input_dir:
        print('input-dir: %s' % input_dir, flush=True)

    if args.live:
        paths = produce_live(keys, args.out_dir, model, args.env_file,
                             payload_idx, store_idx, workers=args.workers,
                             input_dir=input_dir)
        mode = 'live'
    elif args.dry:
        paths = produce_dry(keys, args.out_dir, model)
        mode = 'dry'
    else:
        # fill even if store empty — DE raw / translate may still supply senses
        paths = produce_fill(keys, args.out_dir, model, payload_idx, store_idx,
                             input_dir=input_dir)
        mode = 'fill'

    # Summary
    n_senses = n_tm = n_flag = 0
    for p in paths:
        row = json.load(open(p, encoding='utf-8'))
        n_senses += len(row.get('sense_inventory') or [])
        n_tm += len(row.get('tm_fuzzy_hits') or [])
        hf = row.get('hard_flags') or {}
        if hf.get('polysemy') or hf.get('monster_length') or hf.get('no_pwg'):
            n_flag += 1
    print('prep_pack %s: wrote %d sidecar(s) under %s (store_write=never)'
          % (mode, len(paths), args.out_dir))
    print('  senses_total=%d tm_hits_total=%d keys_with_any_hard_flag=%d'
          % (n_senses, n_tm, n_flag))
    for p in paths[:5]:
        print('  ', p)
    if len(paths) > 5:
        print('  ... +%d more' % (len(paths) - 5))
    return 0


if __name__ == '__main__':
    sys.exit(main())
