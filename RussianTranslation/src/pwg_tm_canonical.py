#!/usr/bin/env python
"""Shared PWG TM canonical v1 helpers (H2683 Track A).

IDs, lossless publication wrapping, and a stdlib schema check. Callers:
pwg_tm_migrate_v1.py, pwg_tm_fragmentize.py, pwg_tm_priority.py.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# PR-A: the JSON/JSONL implementations live in rt_io; re-exported here so
# every `import pwg_tm_canonical as C` consumer keeps its surface.
from rt_io import (  # noqa: E402,F401
    load_json,
    read_jsonl,
    save_json,
    write_json,
    write_jsonl,
)

ROOT = os.path.normpath(os.path.join(HERE, '..'))
SCHEMA_PATH = os.path.join(ROOT, 'schemas', 'pwg_tm_canonical.schema.json')
DEFAULT_PUBLICATION = os.path.join(
    ROOT, 'release', 'translation_memory', 'translation_memory.ru.publication.jsonl')
DEFAULT_OUT_DIR = os.path.join(ROOT, 'release', 'pwg_tm_canonical')

SCHEMA = 'pwg.tm.canonical.v1'
SCHEMA_VERSION = '1.0.0'
PIPELINE_VERSION = 'pwg_tm_canonical.v1'
EXPECTED_PUBLICATION_COUNT = 2392
EXPECTED_EXACT_CARD = 2175
EXPECTED_EXACT_FRAGMENT = 217

FRAGMENT_CLASSES = (
    'sense',
    'definition_gloss',
    'grammar_label',
    'citation',
    'example',
    'recurring_formula',
)
TRUST_LEVELS = {
    'reviewed_exact', 'machine_exact', 'legacy_promoted',
    'suggestion', 'corpus_translation_witness',
}
REUSE_POLICIES = {'auto_exact', 'suggest_only', 'blocked', 'defect'}
CONFIDENCE_OF = {
    'reviewed_exact': 'reviewed',
    'machine_exact': 'machine_gated',
    'legacy_promoted': 'legacy',
    'suggestion': 'suggestion',
}

RIGHTS_FACTS = (
    'PWG (Bohtlingk-Roth) is a 19th-century public-domain German dictionary.',
    'Target rendering is this project\'s own machine translation of that PD source.',
    'Rights uncertainty is recorded, not a release stop (R5/R20).',
)


def sha256_text(text):
    return hashlib.sha256((text or '').encode('utf-8')).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_json(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return sha256_text(blob)


def load_schema():
    with open(SCHEMA_PATH, encoding='utf-8') as f:
        return json.load(f)


def utc_now():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def record_id_of(tm_record_id):
    return 'pwg.tm.v1:' + (tm_record_id or '')


def lemma_of(pub):
    """Locator lemma only. Never a invented sense link."""
    card = ((pub.get('payload') or {}).get('card')) or {}
    key1 = card.get('key1') or ''
    if key1 and '~~' not in key1:
        return key1
    root = (pub.get('provenance') or {}).get('root') or ''
    if root:
        return root
    ev = (pub.get('evidence') or [{}])[0]
    src = ev.get('src_key') or key1
    if src and '~~' in src:
        return src.split('~~', 1)[0]
    return key1 or src or ''


def src_key_of(pub):
    ev = (pub.get('evidence') or [{}])[0]
    if ev.get('src_key'):
        return ev['src_key']
    card = ((pub.get('payload') or {}).get('card')) or {}
    return card.get('key1') or ''


def homonym_of(pub):
    card = ((pub.get('payload') or {}).get('card')) or {}
    recs = card.get('records') or []
    homs = []
    for rec in recs:
        h = (rec.get('h') or '').strip()
        if h:
            homs.append(h)
    if len(set(homs)) == 1:
        return homs[0]
    return None


def entry_id_of(lemma, homonym=None):
    if not lemma:
        return 'pwg.entry:unresolved'
    if homonym:
        return 'pwg.entry:%s:%s' % (lemma, homonym)
    return 'pwg.entry:%s' % lemma


def sense_units(pub):
    """Yield (tag, german, russian, rec_h, ordinal) without inventing alignments."""
    payload = pub.get('payload') or {}
    card = payload.get('card') or {}
    recs = card.get('records')
    if recs:
        n = 0
        for rec in recs:
            for sense in rec.get('senses') or []:
                n += 1
                yield (
                    sense.get('tag') or '',
                    sense.get('german') or '',
                    sense.get('russian') or '',
                    rec.get('h') or '',
                    n,
                )
        return
    for i, sense in enumerate(payload.get('senses') or [], 1):
        yield (
            sense.get('tag') or '',
            sense.get('german') or '',
            sense.get('russian') or '',
            '',
            i,
        )


def sense_id_of(entry_id, tag, ordinal, mapped):
    if not mapped:
        return 'pwg.sense:unresolved:%s:%d' % (entry_id.replace('pwg.entry:', ''), ordinal)
    slug = re.sub(r'[^A-Za-z0-9_.-]+', '_', str(tag or 'none')).strip('_') or 'none'
    return 'pwg.sense:%s:%s:%d' % (entry_id.replace('pwg.entry:', ''), slug, ordinal)


def fragment_id_of(fragment_class, parent_record_id, local_index, source_string):
    payload = {
        'class': fragment_class,
        'parent': parent_record_id,
        'i': local_index,
        'src': source_string or '',
    }
    return 'pwg.frag.v1:%s:%s' % (fragment_class, sha256_json(payload))


def reuse_key_of(fragment_class, source_string, structural_context):
    payload = {
        'class': fragment_class,
        'src': _norm_reuse(source_string),
        'ctx': structural_context or '',
        'pipe': PIPELINE_VERSION,
    }
    return 'pwg.reuse.v1:' + sha256_json(payload)


def _norm_reuse(text):
    return re.sub(r'\s+', ' ', (text or '').strip())


def join_surfaces(pub):
    de_parts, ru_parts = [], []
    for _tag, de, ru, _h, _i in sense_units(pub):
        de_parts.append(de)
        ru_parts.append(ru)
    return '\n'.join(de_parts), '\n'.join(ru_parts)


def confidence_tier(trust_level):
    return CONFIDENCE_OF.get(trust_level, 'uncertain')


def default_rights():
    return {
        'source_status': 'public_domain',
        'translation_status': 'own_machine_translation_of_pd_source',
        'block_class': None,
        'uncertainty': 'none_recorded',
        'facts': list(RIGHTS_FACTS),
    }


def wrap_provenance(pub, generated_at):
    src = copy.deepcopy(pub.get('provenance') or {})
    agents = [
        {'id': 'agent:pwg_tm_migrate_v1', 'type': 'prov:SoftwareAgent',
         'label': PIPELINE_VERSION},
    ]
    model = src.get('model') or src.get('model_version')
    if model:
        agents.append({'id': 'agent:model:' + str(model), 'type': 'prov:SoftwareAgent',
                       'label': str(model)})
    entities = [
        {'id': pub.get('tm_record_id') or 'tm-record', 'type': 'prov:Entity',
         'hash': (pub.get('source_hashes') or {}).get('input_raw_sha256')
         or (pub.get('source_hashes') or {}).get('fragment_sha256')},
    ]
    return {
        'agents': agents,
        'activities': [{
            'id': 'activity:migrate_v1',
            'type': 'prov:Activity',
            'started': generated_at,
            'ended': generated_at,
        }],
        'entities': entities,
        'generated_at': generated_at,
        'pipeline_version': PIPELINE_VERSION,
        'source': src,
    }


def migrate_publication(pub, generated_at=None):
    """Wrap one publication.v1 row. Source/target strings and hashes are copies."""
    generated_at = generated_at or utc_now()
    original = copy.deepcopy(pub)
    lemma = lemma_of(pub)
    hom = homonym_of(pub)
    src_key = src_key_of(pub)
    units = list(sense_units(pub))
    mapped = len(units) == 1
    entry_id = entry_id_of(lemma, hom if mapped else None)
    if mapped:
        sense_id = sense_id_of(entry_id, units[0][0], units[0][4], True)
        alignment = 'mapped'
    else:
        sense_id = sense_id_of(entry_id, '', 0, False)
        alignment = 'unresolved'
    rec_id = record_id_of(pub.get('tm_record_id'))
    source_string, target_string = join_surfaces(pub)
    frag_id = fragment_id_of('sense', rec_id, 0, source_string)
    card = ((pub.get('payload') or {}).get('card')) or {}
    return {
        'schema': SCHEMA,
        'schema_version': SCHEMA_VERSION,
        'record_kind': 'publication',
        'record_id': rec_id,
        'entry_id': entry_id,
        'sense_id': sense_id,
        'fragment_id': frag_id,
        'fragment_class': 'sense',
        'sense_alignment': alignment,
        'lang': pub.get('lang') or 'ru',
        'script': 'Latn',
        'transliteration': 'slp1+iast',
        'source_locator': {
            'dictionary': 'PWG',
            'key1': card.get('key1') or '',
            'lemma_slp1': lemma,
            'iast': card.get('iast') or '',
            'src_key': src_key,
            'homonym': hom,
        },
        'source_string': source_string,
        'source_hash': sha256_text(source_string),
        'target_string': target_string,
        'target_hash': sha256_text(target_string),
        'structural_markup': {
            'n_senses': len(units),
            'record_type': pub.get('record_type'),
            'source_kind': pub.get('source_kind'),
        },
        'trust_level': pub.get('trust_level'),
        'reuse_policy': pub.get('reuse_policy'),
        'confidence_tier': confidence_tier(pub.get('trust_level')),
        'gate_status': pub.get('gate_status'),
        'gate_version': pub.get('gate_version'),
        'review_status': pub.get('review_status'),
        'source_hashes': copy.deepcopy(pub.get('source_hashes') or {}),
        'provenance': wrap_provenance(pub, generated_at),
        'evidence': copy.deepcopy(pub.get('evidence') or []),
        'rights': default_rights(),
        'supersedes': list(pub.get('supersedes') or []),
        'superseded_by': [],
        'source_publication': original,
        'tm_record_id': pub.get('tm_record_id'),
        'model_version': (pub.get('provenance') or {}).get('model_version')
        or (pub.get('provenance') or {}).get('model'),
        'pipeline_version': PIPELINE_VERSION,
    }


def lost_publication_fields(original, wrapped):
    """Return field paths present on the source row but missing from the wrap."""
    kept = wrapped.get('source_publication')
    if kept != original:
        return _diff_paths(original, kept, '$')
    return []


def _diff_paths(expected, got, prefix):
    if expected == got:
        return []
    if type(expected) is not type(got):
        return [prefix]
    if isinstance(expected, dict):
        out = []
        for key, val in expected.items():
            path = prefix + '.' + str(key)
            if key not in got:
                out.append(path)
            else:
                out.extend(_diff_paths(val, got[key], path))
        return out
    if isinstance(expected, list):
        if len(expected) != len(got):
            return [prefix]
        out = []
        for i, val in enumerate(expected):
            out.extend(_diff_paths(val, got[i], '%s[%d]' % (prefix, i)))
        return out
    return [prefix]


def validate_canonical(row):
    """Stdlib required-field check. Returns (ok, reason)."""
    if not isinstance(row, dict):
        return False, 'not an object'
    if row.get('schema') != SCHEMA:
        return False, 'bad schema'
    if row.get('schema_version') != SCHEMA_VERSION:
        return False, 'bad schema_version'
    kind = row.get('record_kind')
    if kind not in ('publication', 'fragment'):
        return False, 'bad record_kind'
    required = [
        'record_id', 'entry_id', 'sense_id', 'fragment_id', 'fragment_class',
        'sense_alignment', 'lang', 'source_locator', 'source_string',
        'source_hash', 'reuse_policy',
    ]
    if kind == 'publication':
        required.extend([
            'tm_record_id', 'source_publication', 'source_hashes', 'provenance',
            'evidence', 'rights', 'supersedes', 'superseded_by', 'trust_level',
            'gate_status', 'review_status', 'target_string', 'target_hash',
        ])
    else:
        required.extend(['reuse_key', 'parent_record_id', 'context'])
    for key in required:
        if key not in row:
            return False, 'missing ' + key
    if row.get('fragment_class') not in FRAGMENT_CLASSES:
        return False, 'bad fragment_class'
    if row.get('sense_alignment') not in ('mapped', 'unresolved'):
        return False, 'bad sense_alignment'
    if row.get('reuse_policy') not in REUSE_POLICIES:
        return False, 'bad reuse_policy'
    if kind == 'publication':
        if row.get('trust_level') not in TRUST_LEVELS:
            return False, 'bad trust_level'
        if not isinstance(row.get('source_publication'), dict):
            return False, 'source_publication not object'
        if not isinstance(row.get('provenance'), dict):
            return False, 'provenance not object'
        if not isinstance(row.get('evidence'), list) or not row.get('evidence'):
            return False, 'missing evidence'
        loc = row.get('source_locator') or {}
        if loc.get('dictionary') != 'PWG':
            return False, 'source_locator.dictionary'
    return True, ''


def validate_jsonschema(row, schema=None):
    try:
        import jsonschema
    except ImportError:
        return True, 'jsonschema-not-installed'
    schema = schema if schema is not None else load_schema()
    try:
        jsonschema.validate(row, schema)
    except jsonschema.ValidationError as exc:
        return False, exc.message
    return True, ''


def reconcile(source_rows, wrapped_rows):
    receipt = {
        'schema': 'pwg.tm.canonical.reconciliation.v1',
        'in_count': len(source_rows),
        'out_count': len(wrapped_rows),
        'in_types': dict(Counter(r.get('record_type') for r in source_rows)),
        'out_kinds': dict(Counter(r.get('record_kind') for r in wrapped_rows)),
        'orphan_source_ids': [],
        'orphan_canonical_ids': [],
        'duplicate_record_ids': [],
        'duplicate_tm_record_ids': [],
        'lost_field_records': 0,
        'lost_field_samples': [],
        'invalid': [],
        'unresolved_sense_alignment': 0,
        'ok': False,
    }
    src_ids = [r.get('tm_record_id') for r in source_rows]
    wrap_tm = [r.get('tm_record_id') for r in wrapped_rows]
    wrap_ids = [r.get('record_id') for r in wrapped_rows]
    src_set, wrap_set = set(src_ids), set(wrap_tm)
    receipt['orphan_source_ids'] = sorted(src_set - wrap_set)
    receipt['orphan_canonical_ids'] = sorted(wrap_set - src_set)
    receipt['duplicate_tm_record_ids'] = sorted(
        tid for tid, n in Counter(src_ids).items() if n > 1)
    receipt['duplicate_record_ids'] = sorted(
        rid for rid, n in Counter(wrap_ids).items() if n > 1)
    by_tm = {r.get('tm_record_id'): r for r in source_rows}
    for wrapped in wrapped_rows:
        ok, why = validate_canonical(wrapped)
        if not ok:
            receipt['invalid'].append({'record_id': wrapped.get('record_id'), 'why': why})
        original = by_tm.get(wrapped.get('tm_record_id'))
        if original is not None:
            lost = lost_publication_fields(original, wrapped)
            if lost:
                receipt['lost_field_records'] += 1
                if len(receipt['lost_field_samples']) < 8:
                    receipt['lost_field_samples'].append({
                        'tm_record_id': wrapped.get('tm_record_id'),
                        'paths': lost[:12],
                    })
        if wrapped.get('sense_alignment') == 'unresolved':
            receipt['unresolved_sense_alignment'] += 1
    receipt['ok'] = (
        receipt['in_count'] == receipt['out_count']
        and not receipt['orphan_source_ids']
        and not receipt['orphan_canonical_ids']
        and not receipt['duplicate_record_ids']
        and not receipt['duplicate_tm_record_ids']
        and receipt['lost_field_records'] == 0
        and not receipt['invalid']
    )
    return receipt
