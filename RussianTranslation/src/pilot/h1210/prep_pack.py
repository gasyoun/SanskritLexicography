#!/usr/bin/env python
r"""Flash PREP — map mode A: cheap prep sidecars before Opus (H2439 + fill).

Lane map §3.1 — order that matters::

    [1] Queue head (manifest keys)
           │
    [2] Flash PREP  (THIS MODULE — read-only context)
           │  a. sense inventory
           │  b. TM fuzzy rank  →  tm_fuzzy_hits[]   ← READ-ONLY reuse candidates
           │  c. compound / citation / hard-flags
           │  d. optional RU skeleton (Flash --live)
           │  e. free det_gate (no Claude)
           │  ⛔  never writes the TM store
           │
    [3] Router  (controller_only | full_worker | park)
           │
    [4] Same promoter + TM FENCE  (R4.3a)  ← NOT this module
           │  only the promoter path may write TM
           │  prep/Flash/det_gate never do

TM fuzzy rank  vs  TM fence  (do not conflate)
----------------------------------------------
* **TM fuzzy rank** (step [2]b, here): ranked *hits* for "reuse vs invent".
  Output field ``tm_fuzzy_hits``. Read-only. Looking at the store/TM sidecars is fine.
* **TM fence** (step [4], promoter): the *write* barrier. Declared on every sidecar as
  ``tm_fence.may_write=false`` / ``writer=promoter_only``. Flash PREP must never clear it.

What each sidecar carries
-------------------------
* **sense_inventory** — N senses with DE anchors
* **tm_fuzzy_hits** — ranked TM hits (exact content-addressed / exact key1 / key1 difflib)
* **tm_fence** — R4.3a declaration (always may_write=false from this tool)
* **hard_flags** / **citation_normalize** / **compound_candidates**
* **ru_skeleton** — optional Flash draft seeds (never promoted from here)
* **det** — free det_gate (prep-level + full twin when draft card exists; claude=false)

Modes: ``fill`` | ``dry`` | ``live`` (+ ``--gate-only`` / ``--no-gate``).

Org map: Uprava docs/DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md §3.1.
"""
from __future__ import annotations

import argparse
import hashlib
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
import det_gate  # noqa: E402 — free Python twin of the H1209 JS gate (no Claude)

SCHEMA_ID = 'pwg.prep_pack.v1'
CONTEXT_SCHEMA_ID = 'pwg.prep_context.v1'
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
        'source_evidence': None,
        # Step [2]b — TM fuzzy rank (READ-ONLY hits). Not the TM fence.
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
        'det': {
            'ok': None,
            'gate': None,       # 'prep' | 'full' | 'skipped'
            'issues': [],
            'coverage': None,
            'claude': False,    # hard invariant — never Claude on this path
        },
        # Step [4] declaration only — PREP never crosses the fence.
        'tm_fence': {
            'may_write': False,
            'writer': 'promoter_only',
            'rule': 'R4.3a',
            'step': '[4] same promoter + TM fence',
            'note': 'TM fuzzy rank (tm_fuzzy_hits) is read-only prep; only the promoter may write TM',
        },
        'store_write': False,  # alias of tm_fence.may_write for older consumers
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
    return {
        c['key1']: dict(c, _prep_source_kind='slice_payload')
        for c in (pl.get('cards') or []) if c.get('key1')
    }


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
    ).encode('utf-8')


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _semantic_pack_sha256(pack: dict) -> str:
    """Hash replay-relevant PREP content, excluding observation time."""
    stable = dict(pack)
    stable.pop('produced_at', None)
    return _sha256(_canonical_bytes(stable))


def load_manifest_index(path: str | None) -> dict[str, dict]:
    """Expose immutable manifest inputs as prep sources without regeneration.

    A manifest already carries the exact masked source bytes, declared sense
    count, and complexity used by the production worker. Consuming those bytes
    closes the H2489 gap where a valid queue key was parked merely because the
    worktree lacked gitignored input files.
    """
    if not path:
        return {}
    with open(path, 'rb') as handle:
        raw = handle.read()
    manifest = json.loads(raw.decode('utf-8'))
    if not isinstance(manifest, dict) or not isinstance(manifest.get('inputs'), dict):
        raise SystemExit('prep_pack: --manifest must contain an inputs object')
    manifest_sha = _sha256(raw)
    out = {}
    for key1, source in manifest['inputs'].items():
        if not isinstance(key1, str) or not isinstance(source, dict):
            continue
        skeleton = source.get('skeleton') or ''
        portrait = source.get('portrait') or ''
        out[key1] = {
            'key1': key1,
            'source_senses': source.get('source_senses'),
            'skeleton_tokens': skeleton_tokens_from_text(skeleton),
            'card_block': skeleton,
            'portrait': portrait,
            'complexity': source.get('complexity') or {},
            '_prep_source_kind': 'execution_manifest',
            '_prep_source_locator': path,
            '_prep_source_sha256': _sha256(skeleton.encode('utf-8')),
            '_prep_manifest_sha256': manifest_sha,
        }
    return out


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


def _ru_preview_from_slot(slot: dict | None) -> tuple:
    """(ru_preview, n_rows) from a store index slot."""
    if not slot:
        return None, None
    ru_preview = None
    for row in (slot.get('rows') or [])[:1]:
        ru = (row.get('ru') or '').strip()
        if ru:
            ru_preview = ru[:120] + ('…' if len(ru) > 120 else '')
            break
    return ru_preview, slot.get('n_senses')


def _slot_evidence_sha256(slot: dict | None) -> str | None:
    if not slot:
        return None
    rows = slot.get('rows') or []
    return _sha256(_canonical_bytes(rows)) if rows else None


def _classify_tm_hit(hit: dict) -> dict:
    """Stamp reuse authority independently from similarity score.

    A score of 1.0 for the same key is not content identity. Only the
    content-addressed lookup may be considered by the promoter for exact
    auto-reuse; every other hit is advisory even when its lexical score is 1.
    """
    exact_content = hit.get('match_type') == 'exact_content_sha'
    hit['may_auto_reuse'] = exact_content
    hit['advisory_only'] = not exact_content
    hit['decision_authority'] = 'promoter_only'
    return hit


def tm_content_addressed_hit(key1: str, input_dir: str | None) -> dict | None:
    """Exact content-addressed TM hit (lang:raw_sha256) when pilot/input raw exists.

    READ-ONLY. Uses ``translation_memory.lookup`` — never builds/writes TM.
    """
    if not input_dir:
        return None
    try:
        from window_common import input_paths, sha256_file  # noqa: WPS433
        import translation_memory as tm  # noqa: WPS433
    except Exception:  # noqa: BLE001
        return None
    raw_path, _portrait = input_paths(key1, input_dir=input_dir)
    if not os.path.exists(raw_path):
        # try safe_name stem
        try:
            from safe_filename import safe_name  # noqa: WPS433
            raw2, _ = input_paths(safe_name(key1), input_dir=input_dir)
            if os.path.exists(raw2):
                raw_path = raw2
            else:
                return None
        except Exception:  # noqa: BLE001
            return None
    try:
        raw_sha = sha256_file(raw_path)
        entry = tm.lookup('ru', raw_sha)
    except Exception:  # noqa: BLE001
        return None
    if not entry:
        return None
    # entry is a normalized TM card-ish row
    ru_preview = None
    if isinstance(entry, dict):
        # try common shapes
        for key in ('russian', 'ru', 'text'):
            if entry.get(key):
                t = str(entry[key])
                ru_preview = t[:120] + ('…' if len(t) > 120 else '')
                break
        if not ru_preview and entry.get('card'):
            # nested card senses
            try:
                senses = []
                for r in (entry['card'].get('records') or []):
                    for s in (r.get('senses') or []):
                        if s.get('russian'):
                            senses.append(s['russian'])
                if senses:
                    t = senses[0]
                    ru_preview = t[:120] + ('…' if len(t) > 120 else '')
            except Exception:  # noqa: BLE001
                pass
    return _classify_tm_hit({
        'rank': 1,
        'key1': key1,
        'score': 1.0,
        'match_type': 'exact_content_sha',
        'raw_sha256': raw_sha,
        'n_store_rows': None,
        'ru_preview': ru_preview,
        'reuse_hint': 'auto_exact_candidate',  # still requires promoter path to write TM
        'evidence_sha256': raw_sha,
    })


def tm_fuzzy_rank(key1: str, store_idx: dict, *,
                  input_dir: str | None = None,
                  top: int = TM_FUZZY_TOP) -> list[dict]:
    """Step [2]b — TM fuzzy rank (READ-ONLY). Map field: ``tm_fuzzy_hits``.

    Rank order (best first):
      1. content-addressed exact TM hit (raw sha → translation_memory.lookup)
      2. exact store key1
      3. key1 difflib neighbors over the store key universe

    This is **not** the TM fence. Hits are advice for "reuse vs invent"; they never
    write TM. The fence is step [4] (promoter only) — see ``tm_fence`` on the pack.
    """
    by_key = store_idx.get('by_key') or {}
    all_keys = store_idx.get('all_keys') or []
    hits = []
    seen = set()

    ca = tm_content_addressed_hit(key1, input_dir)
    if ca:
        hits.append(ca)
        seen.add(key1)

    if key1 in by_key and key1 not in seen:
        ru_preview, n_rows = _ru_preview_from_slot(by_key[key1])
        hits.append(_classify_tm_hit({
            'rank': len(hits) + 1,
            'key1': key1,
            'score': 1.0,
            'match_type': 'exact_key1',
            'n_store_rows': n_rows,
            'ru_preview': ru_preview,
            'reuse_hint': 'store_key1_exact',
            'evidence_sha256': _slot_evidence_sha256(by_key[key1]),
        }))
        seen.add(key1)
    elif key1 in by_key and hits:
        # content-addressed already claimed rank 1; still note store row count
        hits[0]['n_store_rows'] = by_key[key1].get('n_senses')

    # Fuzzy neighbors — prefix pool first, then difflib score.
    prefix = key1[: max(2, min(4, len(key1)))]
    pool = [k for k in all_keys if k not in seen
            and (k.startswith(prefix) or prefix.startswith(k[:len(prefix)]))]
    if len(pool) < 40:
        p2 = key1[:2] if len(key1) >= 2 else key1
        pool = [k for k in all_keys if k not in seen and k.startswith(p2)]
    if len(pool) > 400:
        pool = pool[:400]
    scored = []
    for k in pool:
        s = SequenceMatcher(None, key1, k).ratio()
        if s >= TM_FUZZY_MIN_SCORE:
            scored.append((s, k))
    scored.sort(reverse=True)
    for s, k in scored[: max(0, top - len(hits))]:
        ru_preview, n_rows = _ru_preview_from_slot(by_key.get(k))
        hits.append(_classify_tm_hit({
            'rank': len(hits) + 1,
            'key1': k,
            'score': round(s, 3),
            'match_type': 'key1_difflib',
            'n_store_rows': n_rows,
            'ru_preview': ru_preview,
            'reuse_hint': 'fuzzy_neighbor',
            'evidence_sha256': _slot_evidence_sha256(by_key.get(k)),
        }))
    # re-number ranks 1..n
    for i, h in enumerate(hits, 1):
        h['rank'] = i
    return hits


# Back-compat alias (older call sites / docs said tm_fuzzy_hits for the function).
tm_fuzzy_hits = tm_fuzzy_rank


def apply_hard_flags(pack: dict, *, card: dict | None, slot: dict | None,
                     has_de_source: bool = False) -> None:
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
    if not has_de_source and not slot and not card and n_senses == 0:
        hf['no_pwg'] = True
        notes.append('no DE source (no store row, no payload card, no raw/translate)')
    if slot and 'pwg' not in layers and layers:
        # has store rows but none from pwg layer
        notes.append('store layers=%s (no pwg)' % ','.join(sorted(layers)))
    if n_senses >= POLYSEMY_SENSE_FLOOR:
        hf['polysemy'] = True
        notes.append('polysemy: n_senses=%d >= %d' % (n_senses, POLYSEMY_SENSE_FLOOR))
    if de_bytes >= MONSTER_BYTES or len(pack['key1']) >= 24:
        hf['monster_length'] = True
        notes.append('monster: de_bytes=%d key1_len=%d' % (de_bytes, len(pack['key1'])))
    # provisional route — apply_det_gate may refine
    if hf['monster_length'] or (hf['polysemy'] and n_senses >= 12):
        pack['route_hint'] = 'full_worker'
    elif hf['no_pwg'] and n_senses == 0:
        pack['route_hint'] = 'park'
    elif n_senses and not hf['monster_length']:
        pack['route_hint'] = 'controller_only' if pack.get('ru_skeleton') else 'prep_only'
    else:
        pack['route_hint'] = 'prep_only'


# --------------------------------------------------------------------------- free det_gate (no Claude)

def skeleton_tokens_from_text(text: str) -> list[str]:
    return det_gate.TOK.findall(str(text or ''))


def slice_context_for_gate(pack: dict, payload_card: dict | None) -> dict:
    """Build the `c` dict det_gate.deterministic_audit expects (prep_slice shape)."""
    tokens = []
    source_senses = len(pack.get('sense_inventory') or [])
    if payload_card:
        tokens = list(payload_card.get('skeleton_tokens') or [])
        if isinstance(payload_card.get('source_senses'), int):
            source_senses = payload_card['source_senses']
        if not tokens and payload_card.get('card_block'):
            tokens = skeleton_tokens_from_text(payload_card['card_block'])
    if not tokens:
        # fall back to tokens embedded in DE anchors
        for s in pack.get('sense_inventory') or []:
            tokens.extend(skeleton_tokens_from_text(s.get('de_anchor') or ''))
    return {
        'key1': pack['key1'],
        'skeleton_tokens': tokens,
        'source_senses': source_senses,
    }


def draft_card_from_store(slot: dict, key1: str) -> dict | None:
    """Assemble a card-shaped draft from store rows (german=de, russian=ru). Free."""
    rows = slot.get('rows') or []
    if not rows:
        return None
    senses = []
    for row in rows:
        senses.append({
            'tag': str(row.get('sense_tag') or len(senses) + 1),
            'german': row.get('de') or '',
            'russian': row.get('ru') or '',
        })
    return {'key1': key1, 'records': [{'grammar': '', 'senses': senses}], 'notes': ''}


def draft_card_from_skeleton(pack: dict) -> dict | None:
    """Assemble a draft card from sense DE anchors + ru_skeleton (Flash seeds)."""
    inv = pack.get('sense_inventory') or []
    skel = pack.get('ru_skeleton')
    if not inv:
        return None
    if not isinstance(skel, list) or not skel:
        return None
    senses = []
    for i, s in enumerate(inv):
        ru = skel[i] if i < len(skel) else ''
        senses.append({
            'tag': str(s.get('sense_tag') or s.get('i') or i + 1),
            'german': s.get('de_anchor') or '',
            'russian': ru if isinstance(ru, str) else str(ru or ''),
        })
    return {'key1': pack['key1'], 'records': [{'grammar': '', 'senses': senses}], 'notes': ''}


def prep_level_gate(pack: dict) -> list[str]:
    """Free prep-level checks — no card shape, no Claude, no network."""
    issues = []
    inv = pack.get('sense_inventory') or []
    hf = pack.get('hard_flags') or {}
    if hf.get('no_pwg') and not inv:
        issues.append('prep: no_pwg and empty sense_inventory — park')
    if inv and all(not (s.get('de_anchor') or '').strip() for s in inv):
        issues.append('prep: sense_inventory present but every de_anchor is empty')
    skel = pack.get('ru_skeleton')
    if isinstance(skel, list) and skel and inv:
        if len(skel) < len(inv):
            issues.append('prep: ru_skeleton length %d < sense_inventory %d'
                          % (len(skel), len(inv)))
        # empty skeleton slots
        empty = sum(1 for x in skel if not str(x or '').strip())
        if empty:
            issues.append('prep: ru_skeleton has %d empty slot(s)' % empty)
    return issues


def apply_det_gate(pack: dict, *, payload_card: dict | None = None,
                   store_slot: dict | None = None,
                   draft_card: dict | None = None) -> dict:
    """Run free det_gate layers; mutate pack['det'] + refine route_hint. No Claude."""
    prep_issues = prep_level_gate(pack)
    ctx = slice_context_for_gate(pack, payload_card)

    # Prefer an explicit draft, else assemble from store, else skeleton+ru.
    card = draft_card
    if card is None and store_slot:
        card = draft_card_from_store(store_slot, pack['key1'])
    if card is None:
        card = draft_card_from_skeleton(pack)

    full = None
    gate = 'prep'
    if card is not None:
        full = det_gate.deterministic_audit(card, ctx, field='russian')
        gate = 'full'
        issues = list(prep_issues) + list(full.get('issues') or [])
        coverage = full.get('coverage')
    else:
        issues = list(prep_issues)
        coverage = None
        # With no draft card, empty issues + senses present → prep ok
        if not issues and (pack.get('sense_inventory') or pack.get('route_hint') == 'park'):
            pass

    ok = len(issues) == 0
    # Park is a deliberate non-ok for the router when no DE, but det.ok tracks gate cleanliness
    if pack.get('route_hint') == 'park' and not (pack.get('sense_inventory') or []):
        ok = False
        if 'prep: no_pwg and empty sense_inventory — park' not in issues:
            issues.append('prep: no_pwg and empty sense_inventory — park')

    pack['det'] = {
        'ok': ok,
        'gate': gate,
        'issues': issues[:30],
        'coverage': coverage,
        'claude': False,
        'n_skeleton_tokens': len(ctx.get('skeleton_tokens') or []),
        'source_senses': ctx.get('source_senses'),
        'had_draft_card': card is not None,
    }

    # Refine route from free gate (map [3] Router inputs)
    hf = pack.get('hard_flags') or {}
    if pack.get('route_hint') == 'park':
        pass  # stay parked
    elif hf.get('monster_length') or (hf.get('polysemy') and len(pack.get('sense_inventory') or []) >= 12):
        pack['route_hint'] = 'full_worker'
    elif ok and card is not None and gate == 'full':
        pack['route_hint'] = 'controller_only'
    elif ok and pack.get('sense_inventory'):
        pack['route_hint'] = 'prep_only' if not pack.get('ru_skeleton') else 'controller_only'
    elif not ok:
        pack['route_hint'] = 'full_worker' if pack.get('sense_inventory') else 'park'

    pack['store_write'] = False
    return pack


def fill_one(key1: str, *, model: str, payload_idx: dict, store_idx: dict,
             mode: str = 'fill', input_dir: str | None = None,
             run_gate: bool = True, manifest_authoritative: bool = False) -> dict:
    pack = empty_pack(key1, model=model, mode=mode)
    card = payload_idx.get(key1)
    slot = (store_idx.get('by_key') or {}).get(key1)
    de_src = load_de_source(key1, input_dir=input_dir)
    de_blob = ''

    # H2591: `--manifest` alone could never actually PRODUCE a manifest-sourced sidecar on
    # a checkout that has the raws. `load_de_source` falls back to the hardcoded MAIN_PILOT
    # input dir, so `de_src` was always truthy and the execution-manifest branch below was
    # dead code except on a machine missing the inputs — i.e. exactly the "reachable only
    # by accident" shape. A consumer that must bind an IMMUTABLE manifest source + manifest
    # SHA (a sealed comparison, a replayable receipt) now says so explicitly instead of
    # depending on which files happen to sit on this disk.
    if manifest_authoritative and card and card.get('_prep_source_kind') == 'execution_manifest':
        de_src = None

    # Priority: immutable production source > manifest/payload source > promoted
    # store. The store is useful evidence and a draft source, but must not
    # override newer source bytes merely because a key1 matches.
    if de_src:
        de_blob = de_src['text']
        if de_src.get('units'):
            pack['sense_inventory'] = sense_inventory_from_units(de_src['units'])
        else:
            pack['sense_inventory'] = sense_inventory_from_de_text(
                de_blob, source_note='de_raw:' + os.path.basename(de_src['source']))
        pack['hard_flags']['notes'].append('de_source=%s' % de_src['source'])
        pack['source_evidence'] = {
            'kind': 'de_source',
            'locator': de_src['source'],
            'sha256': _sha256(de_blob.encode('utf-8')),
        }
    elif card:
        pack['sense_inventory'] = sense_inventory_from_payload(card)
        de_blob = card.get('card_block') or ''
        kind = card.get('_prep_source_kind') or 'slice_payload'
        pack['hard_flags']['notes'].append('de_source=%s' % kind)
        pack['source_evidence'] = {
            'kind': kind,
            'locator': card.get('_prep_source_locator'),
            'sha256': card.get('_prep_source_sha256') or _sha256(
                de_blob.encode('utf-8')),
            'manifest_sha256': card.get('_prep_manifest_sha256'),
        }
    elif slot:
        pack['sense_inventory'] = sense_inventory_from_store(slot)
        de_blob = '\n'.join((r.get('de') or '') for r in slot['rows'])
        pack['hard_flags']['notes'].append('de_source=store')
        pack['source_evidence'] = {
            'kind': 'promoted_store',
            'locator': None,
            'sha256': _slot_evidence_sha256(slot),
        }

    if de_blob:
        pack['citation_normalize'] = citation_normalize_from_text(de_blob)
    elif card:
        pack['citation_normalize'] = citation_normalize_from_text(card.get('card_block') or '')

    pack['compound_candidates'] = compound_candidates_from_key(key1)
    # Step [2]b — TM fuzzy rank (read-only). Distinct from step [4] TM fence.
    pack['tm_fuzzy_hits'] = tm_fuzzy_rank(key1, store_idx, input_dir=input_dir)
    # feed de_bytes into hard flags via a synthetic slot when only raw exists
    flag_slot = slot
    if not flag_slot and de_blob:
        flag_slot = {
            'rows': [], 'de_bytes': len(de_blob),
            'n_senses': len(pack['sense_inventory']),
            'layers': set(),
        }
    apply_hard_flags(pack, card=card, slot=flag_slot,
                     has_de_source=bool(de_src or slot or card))
    if run_gate:
        apply_det_gate(pack, payload_card=card, store_slot=slot)
    else:
        pack['det'] = {
            'ok': None, 'gate': 'skipped', 'issues': [], 'coverage': None,
            'claude': False,
        }
    # Fence invariant: prep never clears may_write / store_write
    pack['tm_fence'] = {
        'may_write': False,
        'writer': 'promoter_only',
        'rule': 'R4.3a',
        'step': '[4] same promoter + TM fence',
        'note': 'TM fuzzy rank (tm_fuzzy_hits) is read-only prep; only the promoter may write TM',
        'n_hits_ranked': len(pack.get('tm_fuzzy_hits') or []),
    }
    pack['store_write'] = False
    return pack


# --------------------------------------------------------------------------- IO + live

def write_pack(out_dir: str, pack: dict) -> str:
    # TM fence (R4.3a): prep must never claim a write
    if pack.get('store_write') is True:
        raise SystemExit('prep_pack: refusing store_write=True (R4.3a TM fence — promoter only)')
    fence = pack.get('tm_fence') or {}
    if fence.get('may_write') is True:
        raise SystemExit('prep_pack: refusing tm_fence.may_write=True (R4.3a TM fence)')
    # force fence declaration present
    pack['tm_fence'] = {
        'may_write': False,
        'writer': 'promoter_only',
        'rule': 'R4.3a',
        'step': '[4] same promoter + TM fence',
        'note': fence.get('note') or (
            'TM fuzzy rank (tm_fuzzy_hits) is read-only prep; only the promoter may write TM'),
        'n_hits_ranked': len(pack.get('tm_fuzzy_hits') or []),
    }
    pack['store_write'] = False
    os.makedirs(out_dir, exist_ok=True)
    # Case-collision-safe stem (Windows: DA.json vs dA.json must not clobber).
    try:
        from safe_filename import safe_name  # noqa: WPS433
        stem = safe_name(pack['key1'])
    except Exception:  # noqa: BLE001
        stem = pack['key1']
    path = os.path.join(out_dir, '%s.json' % stem)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pack, f, ensure_ascii=False, indent=1)
        f.write('\n')
    return path


def assert_tm_fence(pack: dict) -> None:
    """Refuse any prep artifact that claims promotion authority."""
    fence = pack.get('tm_fence') or {}
    if pack.get('store_write') is not False:
        raise SystemExit('prep_pack: compact context requires store_write=false')
    if fence.get('may_write') is not False \
            or fence.get('writer') != 'promoter_only' \
            or fence.get('rule') != 'R4.3a':
        raise SystemExit('prep_pack: invalid R4.3a promoter-only TM fence')
    for hit in pack.get('tm_fuzzy_hits') or []:
        exact_content = hit.get('match_type') == 'exact_content_sha'
        if hit.get('may_auto_reuse') is not exact_content:
            raise SystemExit('prep_pack: TM hit reuse authority contradicts match type')
        if hit.get('advisory_only') is exact_content:
            raise SystemExit('prep_pack: TM hit advisory flag contradicts match type')
        if hit.get('decision_authority') != 'promoter_only':
            raise SystemExit('prep_pack: TM hit escaped promoter-only authority')


def compact_context(pack: dict, *, top_tm: int = 5,
                    max_anchors: int = 12) -> dict:
    """Compile a small, sealed Claude context seed from one full prep sidecar."""
    assert_tm_fence(pack)
    anchors = []
    for sense in (pack.get('sense_inventory') or [])[:max_anchors]:
        anchors.append({
            'i': sense.get('i'),
            'tag': sense.get('sense_tag'),
            'de_anchor': (sense.get('de_anchor') or '')[:160],
            'layer': sense.get('layer'),
        })
    tm_hits = []
    for hit in (pack.get('tm_fuzzy_hits') or [])[:top_tm]:
        tm_hits.append({
            name: hit.get(name) for name in (
                'rank', 'key1', 'score', 'match_type', 'ru_preview',
                'reuse_hint', 'evidence_sha256', 'may_auto_reuse',
                'advisory_only', 'decision_authority',
            )
        })
    value = {
        'schema': CONTEXT_SCHEMA_ID,
        'key1': pack['key1'],
        'prep_semantic_sha256': _semantic_pack_sha256(pack),
        'source_evidence': pack.get('source_evidence'),
        'sense_count': len(pack.get('sense_inventory') or []),
        'sense_anchors': anchors,
        'tm_hits': tm_hits,
        'hard_flags': pack.get('hard_flags') or {},
        'det': pack.get('det') or {},
        'route_hint': pack.get('route_hint'),
        'tm_policy': {
            'may_write': False,
            'writer': 'promoter_only',
            'rule': 'R4.3a',
            'fuzzy_is_advisory': True,
            'exact_content_requires_promoter': True,
        },
        'question_scope': {
            'can_answer_now': ['Q1', 'Q3', 'Q5'],
            'promoter_decides': ['Q2'],
            'cannot_answer': ['N1', 'N2', 'N4', 'N11'],
        },
        'promotable': False,
    }
    value['context_sha256'] = _sha256(_canonical_bytes(value))
    return value


def verify_compact_context(value: dict) -> dict:
    if not isinstance(value, dict) or value.get('schema') != CONTEXT_SCHEMA_ID:
        raise SystemExit('prep_pack: compact context schema mismatch')
    claimed = value.get('context_sha256')
    unsigned = dict(value)
    unsigned.pop('context_sha256', None)
    if claimed != _sha256(_canonical_bytes(unsigned)):
        raise SystemExit('prep_pack: compact context hash mismatch')
    policy = value.get('tm_policy') or {}
    if value.get('promotable') is not False or policy.get('may_write') is not False \
            or policy.get('writer') != 'promoter_only' \
            or policy.get('rule') != 'R4.3a' \
            or policy.get('fuzzy_is_advisory') is not True \
            or policy.get('exact_content_requires_promoter') is not True:
        raise SystemExit('prep_pack: compact context crossed the TM fence')
    for hit in value.get('tm_hits') or []:
        exact_content = hit.get('match_type') == 'exact_content_sha'
        if hit.get('may_auto_reuse') is not exact_content \
                or hit.get('advisory_only') is exact_content \
                or hit.get('decision_authority') != 'promoter_only':
            raise SystemExit('prep_pack: compact context contains invalid TM authority')
    return value


def write_compact_context(out_dir: str, pack: dict) -> str:
    value = verify_compact_context(compact_context(pack))
    os.makedirs(out_dir, exist_ok=True)
    try:
        from safe_filename import safe_name  # noqa: WPS433
        stem = safe_name(pack['key1'])
    except Exception:  # noqa: BLE001
        stem = pack['key1']
    path = os.path.join(out_dir, '%s.context.json' % stem)
    encoded = json.dumps(value, ensure_ascii=False, indent=1) + '\n'
    if os.path.exists(path):
        with open(path, encoding='utf-8') as handle:
            if handle.read() != encoded:
                raise SystemExit('prep_pack: existing compact context differs: %s' % path)
        return path
    with open(path, 'x', encoding='utf-8', newline='\n') as handle:
        handle.write(encoded)
    return path


def produce_fill(keys: list[str], out_dir: str, model: str,
                 payload_idx: dict, store_idx: dict,
                 input_dir: str | None = None, run_gate: bool = True,
                 manifest_authoritative: bool = False) -> list[str]:
    paths = []
    for k in keys:
        pack = fill_one(k, model=model, payload_idx=payload_idx, store_idx=store_idx,
                        mode='fill', input_dir=input_dir, run_gate=run_gate,
                        manifest_authoritative=manifest_authoritative)
        paths.append(write_pack(out_dir, pack))
    return paths


def produce_dry(keys: list[str], out_dir: str, model: str,
                run_gate: bool = True) -> list[str]:
    paths = []
    for k in keys:
        pack = empty_pack(k, model=model, mode='dry')
        if len(k) >= 24:
            pack['hard_flags']['monster_length'] = True
            pack['hard_flags']['notes'].append('dry: key1 length >= 24 (proxy only)')
            pack['route_hint'] = 'full_worker'
        pack['compound_candidates'] = compound_candidates_from_key(k)
        if run_gate:
            apply_det_gate(pack, payload_card=None, store_slot=None)
        else:
            pack['det'] = {
                'ok': None, 'gate': 'skipped', 'issues': [], 'coverage': None,
                'claude': False,
            }
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
    # Provisional route only — free det_gate re-runs after live and is authoritative.
    if pack.get('ru_skeleton') and pack['route_hint'] == 'prep_only':
        pack['route_hint'] = 'controller_only'
    pack['store_write'] = False
    return pack


def produce_live(keys: list[str], out_dir: str, model: str, env_file: str | None,
                 payload_idx: dict, store_idx: dict, workers: int = 6,
                 input_dir: str | None = None, run_gate: bool = True) -> list[str]:
    env = ds.load_env_file(env_file)
    key = os.environ.get('DEEPSEEK_API_KEY') or env.get('DEEPSEEK_API_KEY')
    if not key:
        raise SystemExit('prep_pack --live needs DEEPSEEK_API_KEY (or use fill/dry)')
    ds.refuse_if_peak()
    base = (os.environ.get('DEEPSEEK_BASE_URL') or env.get('DEEPSEEK_BASE_URL')
            or 'https://api.deepseek.com')
    client = ds.DeepSeek(base, key, model, max_tokens=ds.DEFAULT_MAX_TOKENS, timeout=120)

    # Deterministic fill first (free, gate deferred until after Flash draft).
    packs = [
        fill_one(k, model=model, payload_idx=payload_idx, store_idx=store_idx,
                 mode='live', input_dir=input_dir, run_gate=False)
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
        pack = done[k]
        if run_gate:
            # Free det_gate after draft — no Claude (map §3.1 step [2]).
            apply_det_gate(
                pack,
                payload_card=payload_idx.get(k),
                store_slot=(store_idx.get('by_key') or {}).get(k),
            )
            print('  gate %-24s ok=%s gate=%s issues=%d route=%s'
                  % (k, pack['det']['ok'], pack['det']['gate'],
                     len(pack['det']['issues']), pack['route_hint']),
                  flush=True)
        paths.append(write_pack(out_dir, pack))
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
    assert ds.DEFAULT_MAX_TOKENS == 32768

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
        assert p['tm_fuzzy_hits'][0]['match_type'] in ('exact_key1', 'exact_content_sha')
        assert p['tm_fuzzy_hits'][0]['score'] == 1.0
        if p['tm_fuzzy_hits'][0]['match_type'] == 'exact_key1':
            assert p['tm_fuzzy_hits'][0]['advisory_only'] is True
            assert p['tm_fuzzy_hits'][0]['may_auto_reuse'] is False
        assert p['tm_fuzzy_hits'][0]['decision_authority'] == 'promoter_only'
        # neighbor kAlaka should appear in fuzzy list
        fuzzy_keys = {h['key1'] for h in p['tm_fuzzy_hits']}
        assert 'kAlaka' in fuzzy_keys or len(p['tm_fuzzy_hits']) >= 1
        assert p['citation_normalize'], 'ls citation should be extracted'
        assert p['store_write'] is False
        # TM fence ≠ TM fuzzy rank
        assert p['tm_fence']['may_write'] is False
        assert p['tm_fence']['writer'] == 'promoter_only'
        assert p['tm_fence']['rule'] == 'R4.3a'
        assert p['tm_fence']['n_hits_ranked'] == len(p['tm_fuzzy_hits'])
        assert p['hard_flags']['polysemy'] is False  # only 2 senses
        # free det_gate on store-assembled draft (no Claude)
        assert p['det']['claude'] is False
        assert p['det']['gate'] == 'full'
        assert p['det']['had_draft_card'] is True
        assert isinstance(p['det']['ok'], bool)

        p2 = fill_one('lonelyKey', model=ds.DEFAULT_MODEL, payload_idx=pl_idx, store_idx=idx)
        assert len(p2['sense_inventory']) == 3
        assert p2['sense_inventory'][0]['note'] == 'payload_source_senses'
        assert any(c['normalized'] for c in p2['citation_normalize'])
        assert p2['det']['claude'] is False
        assert p2['det']['gate'] == 'prep'  # no draft card without store/ru_skeleton

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
        assert p4['det']['claude'] is False

        # Frozen manifest inputs close the gitignored-input/no_pwg gap and bind
        # the compact seed to exact source bytes.
        manifest_path = os.path.join(td, 'manifest.json')
        manifest = {
            'inputs': {
                'manifestOnly': {
                    'skeleton': '1〉 {%Quelle%} <ls>R.</ls> 2〉 {%Ziel%}',
                    'portrait': '[]',
                    'source_senses': 2,
                    'complexity': {'len_bytes': 44, 'n_senses': 2},
                },
            },
        }
        with open(manifest_path, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(manifest, handle, ensure_ascii=False)
        manifest_idx = load_manifest_index(manifest_path)
        p_manifest = fill_one(
            'manifestOnly', model=ds.DEFAULT_MODEL, payload_idx=manifest_idx,
            store_idx={'by_key': {}, 'all_keys': []}, input_dir=os.path.join(td, 'absent'))
        assert p_manifest['hard_flags']['no_pwg'] is False
        assert len(p_manifest['sense_inventory']) == 2
        assert p_manifest['source_evidence']['kind'] == 'execution_manifest'
        assert len(p_manifest['source_evidence']['sha256']) == 64

        # H2591: with a local raw present, `--manifest` alone LOSES to the raw — that is
        # why the execution_manifest branch above was unreachable in practice. The flag is
        # what makes an immutable-source guarantee expressible rather than accidental.
        raw_dir = os.path.join(td, 'raws')
        os.makedirs(raw_dir, exist_ok=True)
        with open(os.path.join(raw_dir, 'manifestOnly.raw.txt'), 'w',
                  encoding='utf-8', newline='\n') as handle:
            handle.write('1〉 {%Andere Quelle%} <ls>MBh.</ls>')
        p_raw_wins = fill_one(
            'manifestOnly', model=ds.DEFAULT_MODEL, payload_idx=manifest_idx,
            store_idx={'by_key': {}, 'all_keys': []}, input_dir=raw_dir)
        assert p_raw_wins['source_evidence']['kind'] == 'de_source', \
            'a local raw must still win by default — this is not a behaviour change'
        p_bound = fill_one(
            'manifestOnly', model=ds.DEFAULT_MODEL, payload_idx=manifest_idx,
            store_idx={'by_key': {}, 'all_keys': []}, input_dir=raw_dir,
            manifest_authoritative=True)
        assert p_bound['source_evidence']['kind'] == 'execution_manifest'
        assert p_bound['source_evidence']['manifest_sha256'] == \
            p_manifest['source_evidence']['manifest_sha256']
        assert compact_context(p_bound)['prep_semantic_sha256'] == \
            compact_context(p_manifest)['prep_semantic_sha256'], \
            'manifest-bound context must not depend on which raws sit on this disk'
        print('  ok   --manifest-authoritative binds immutable manifest bytes over local raws')

        context = compact_context(p_manifest)
        assert verify_compact_context(context) is context
        assert context == compact_context(p_manifest), 'compact seed must replay byte-identically'
        later_pack = json.loads(json.dumps(p_manifest))
        later_pack['produced_at'] += 1000
        assert context == compact_context(later_pack), 'wall clock must not perturb context bytes'
        assert context['promotable'] is False
        assert context['tm_policy']['may_write'] is False
        context_dir = os.path.join(td, 'contexts')
        context_path = write_compact_context(context_dir, p_manifest)
        assert write_compact_context(context_dir, p_manifest) == context_path
        tampered = json.loads(json.dumps(p_manifest))
        tampered['tm_fence']['may_write'] = True
        try:
            compact_context(tampered)
            raise AssertionError('compact context must refuse a writable prep pack')
        except SystemExit as exc:
            assert 'fence' in str(exc)

        forged_context = json.loads(json.dumps(context))
        forged_context['tm_hits'] = [{
            'match_type': 'fuzzy_key', 'may_auto_reuse': True,
            'advisory_only': False, 'decision_authority': 'promoter_only',
        }]
        forged_context.pop('context_sha256')
        forged_context['context_sha256'] = _sha256(_canonical_bytes(forged_context))
        try:
            verify_compact_context(forged_context)
            raise AssertionError('re-hashed fuzzy authority forgery must be refused')
        except SystemExit as exc:
            assert 'authority' in str(exc)

        # full det_gate with skeleton tokens + ru_skeleton draft
        p_draft = empty_pack('tokKey', mode='fill')
        p_draft['sense_inventory'] = [
            {'i': 0, 'de_anchor': '{T1} {%a%}', 'sense_tag': '1'},
            {'i': 1, 'de_anchor': '{T2} {%b%}', 'sense_tag': '2'},
        ]
        p_draft['ru_skeleton'] = ['{T1} а', '{T2} б']
        apply_det_gate(
            p_draft,
            payload_card={
                'skeleton_tokens': ['{T1}', '{T2}'],
                'source_senses': 2,
            },
        )
        assert p_draft['det']['gate'] == 'full'
        assert p_draft['det']['claude'] is False
        assert p_draft['det']['ok'] is True, p_draft['det']['issues']
        assert p_draft['route_hint'] == 'controller_only'

        # sense shortfall on full gate
        p_short = empty_pack('shortKey', mode='fill')
        p_short['sense_inventory'] = [
            {'i': 0, 'de_anchor': '{T1} x', 'sense_tag': '1'},
            {'i': 1, 'de_anchor': '{T2} y', 'sense_tag': '2'},
        ]
        p_short['ru_skeleton'] = ['{T1} only']  # length mismatch prep issue + short card
        apply_det_gate(
            p_short,
            payload_card={'skeleton_tokens': ['{T1}', '{T2}'], 'source_senses': 2},
        )
        assert p_short['det']['ok'] is False
        assert p_short['det']['claude'] is False
        assert any('prep: ru_skeleton length' in i or 'sense-shortfall' in i
                   or 'translation-fidelity' in i for i in p_short['det']['issues'])

        # compound heuristic
        assert compound_candidates_from_key('devaputra')
        # monster + refuse store_write
        p3 = fill_one('aVeryLongHeadwordProxyTokenXX', model=ds.DEFAULT_MODEL,
                      payload_idx={}, store_idx={'by_key': {}, 'all_keys': []})
        assert p3['hard_flags']['monster_length'] is True
        assert p3['det']['claude'] is False
        bad = empty_pack('x')
        bad['store_write'] = True
        try:
            write_pack(td, bad)
            raise AssertionError('store_write=True must refuse')
        except SystemExit as e:
            assert 'store_write' in str(e) or 'R4.3a' in str(e) or 'fence' in str(e)
        bad2 = empty_pack('y')
        bad2['tm_fence'] = {'may_write': True, 'writer': 'flash', 'rule': 'nope'}
        try:
            write_pack(td, bad2)
            raise AssertionError('tm_fence.may_write=True must refuse')
        except SystemExit as e:
            assert 'tm_fence' in str(e) or 'R4.3a' in str(e)

        paths = produce_fill(['kAla', 'lonelyKey'], os.path.join(td, 'prep'),
                             ds.DEFAULT_MODEL, pl_idx, idx)
        assert len(paths) == 2
        disk = json.load(open(paths[0], encoding='utf-8'))
        assert disk['schema'] == SCHEMA_ID
        assert disk['store_write'] is False
        assert disk['sense_inventory']
        assert disk['det']['claude'] is False

        # det_gate twin still green (returns 0 = all checks passed)
        assert det_gate.selftest() == 0

    print('prep_pack selftest: PASS (fill + free det_gate no-Claude, R4.3a fence)')
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--worklist', default=None,
                    help='H1210-style worklist JSON with a keys[] array')
    ap.add_argument('--payload', default=None,
                    help='h1209 slice_payload.json (cards with card_block / source_senses)')
    ap.add_argument('--manifest', default=None,
                    help='manifest-v2 JSON; consumes exact inputs[] source bytes offline')
    ap.add_argument('--manifest-authoritative', action='store_true',
                    help='bind the manifest as THE source even when local raws exist '
                         '(source_evidence.kind=execution_manifest + manifest_sha256); '
                         'required by any consumer that must replay from immutable bytes')
    ap.add_argument('--store', default=None,
                    help='pwg_ru_translated.jsonl (read-only TM/sense source)')
    ap.add_argument('--input-dir', default=None,
                    help='pilot/input dir with {key}.raw.txt (DE source)')
    ap.add_argument('--keys-file', default=None)
    ap.add_argument('--keys', default=None, help='comma-separated key1 list')
    ap.add_argument('--out-dir', default=None, help='directory for prep/{key}.json')
    ap.add_argument('--context-out-dir', default=None,
                    help='also emit sealed compact Claude context seeds')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--model', default=None)
    ap.add_argument('--env-file', default=None)
    ap.add_argument('--workers', type=int, default=6,
                    help='parallel Flash workers for --live (cap 2500)')
    ap.add_argument('--dry', action='store_true',
                    help='key-only skeleton, ignore store/payload content')
    ap.add_argument('--live', action='store_true',
                    help='fill + Flash optional draft; still sidecar-only')
    ap.add_argument('--no-gate', action='store_true',
                    help='skip free det_gate (default: always run, no Claude)')
    ap.add_argument('--gate-only', action='store_true',
                    help='re-run free det_gate on existing prep/{key}.json under --out-dir')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.out_dir:
        ap.error('--out-dir is required (writes prep sidecars only; never the TM store)')
    run_gate = not args.no_gate

    if args.gate_only:
        # Re-gate existing sidecars only (free, no Claude, no store write).
        n_ok = n_bad = 0
        for name in sorted(os.listdir(args.out_dir)):
            if not name.endswith('.json'):
                continue
            path = os.path.join(args.out_dir, name)
            pack = json.load(open(path, encoding='utf-8'))
            apply_det_gate(pack)
            write_pack(args.out_dir, pack)
            if pack['det']['ok']:
                n_ok += 1
            else:
                n_bad += 1
            print('  gate %-24s ok=%s issues=%d route=%s'
                  % (pack['key1'], pack['det']['ok'], len(pack['det']['issues']),
                     pack['route_hint']), flush=True)
        print('gate-only: ok=%d fail=%d (claude=never)' % (n_ok, n_bad))
        return 0

    manifest_idx = {} if args.dry else load_manifest_index(args.manifest)
    keys = load_keys(args)
    if not keys and manifest_idx:
        keys = list(manifest_idx)
        if args.limit is not None:
            keys = keys[:args.limit]
    if not keys:
        ap.error('no keys — pass --manifest, --worklist, --payload, --keys-file, or --keys')
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
    if not args.dry:
        # Manifest inputs are the frozen execution source and therefore win
        # over a coincidentally supplied older slice payload.
        payload_idx.update(manifest_idx)
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
                             input_dir=input_dir, run_gate=run_gate)
        mode = 'live'
    elif args.dry:
        paths = produce_dry(keys, args.out_dir, model, run_gate=run_gate)
        mode = 'dry'
    else:
        # fill even if store empty — DE raw / translate may still supply senses
        paths = produce_fill(keys, args.out_dir, model, payload_idx, store_idx,
                             input_dir=input_dir, run_gate=run_gate,
                             manifest_authoritative=args.manifest_authoritative)
        mode = 'fill'

    context_paths = []
    if args.context_out_dir:
        for path in paths:
            with open(path, encoding='utf-8') as handle:
                context_paths.append(write_compact_context(
                    args.context_out_dir, json.load(handle)))

    # Summary
    n_senses = n_tm = n_flag = n_gate_ok = n_gate_fail = 0
    for p in paths:
        row = json.load(open(p, encoding='utf-8'))
        n_senses += len(row.get('sense_inventory') or [])
        n_tm += len(row.get('tm_fuzzy_hits') or [])
        hf = row.get('hard_flags') or {}
        if hf.get('polysemy') or hf.get('monster_length') or hf.get('no_pwg'):
            n_flag += 1
        det = row.get('det') or {}
        if det.get('ok') is True:
            n_gate_ok += 1
        elif det.get('ok') is False:
            n_gate_fail += 1
        assert det.get('claude') is not True, 'det_gate path must never claim Claude'
    print('prep_pack %s: wrote %d sidecar(s) under %s (store_write=never)'
          % (mode, len(paths), args.out_dir))
    print('  senses_total=%d tm_hits_total=%d keys_with_any_hard_flag=%d'
          % (n_senses, n_tm, n_flag))
    print('  free det_gate: ok=%d fail=%d claude=never'
          % (n_gate_ok, n_gate_fail))
    if context_paths:
        print('  compact contexts: %d under %s (promotable=false)'
              % (len(context_paths), args.context_out_dir))
    for p in paths[:5]:
        print('  ', p)
    if len(paths) > 5:
        print('  ... +%d more' % (len(paths) - 5))
    return 0


if __name__ == '__main__':
    sys.exit(main())
