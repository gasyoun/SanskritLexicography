"""Recursive full-row validation (H3714 Wave 1, implementation step 2).

The current reconciliation reports success while 79 canonical rows carry nested
``{Tn}`` residue at depth (plan, audit verdict 6).  This validator traverses
*every* nested dictionary, list, and string and reports JSONPath-like locations,
so a defect in a middle row can no longer hide behind an aggregate count.

It is read-only by construction: it opens files for reading, never writes, and
reports the defective rows as a fence rather than repairing them (R4.3, fence
item 1).  When schema validation is *required* and ``jsonschema`` is missing it
fails closed rather than silently downgrading (V7).
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Iterator, Mapping, Sequence

from .evidence import sha256_file

SCHEMA = 'pwg.pipeline.validation.v1'
VALIDATOR_VERSION = 'pwg_pipeline.validation.v1'

# Unresolved translation-memory placeholder, e.g. {T3}. The canonical pipeline
# resolves these before publication; one left at any depth is a defect.
PLACEHOLDER_RE = re.compile(r'\{T\d+\}')

# Registered sentinels that must never survive into a promotable row.
SENTINELS: tuple[str, ...] = ('__TODO__', '__PLACEHOLDER__', '__UNRESOLVED__')

REQUIRED_PROVENANCE: tuple[str, ...] = ('generation', 'provenance')
SHA_RE = re.compile(r'^[0-9a-f]{64}$')

# Defect codes. Stable strings: a report is evidence and gets compared.
UNRESOLVED_PLACEHOLDER = 'unresolved_placeholder'
REGISTERED_SENTINEL = 'registered_sentinel'
MISSING_PROVENANCE = 'missing_provenance'
DUPLICATE_IDENTITY = 'duplicate_identity'
BROKEN_HASH_LINEAGE = 'broken_hash_lineage'
ROUTE_MODEL_MISMATCH = 'route_model_mismatch'
INVALID_ROW = 'invalid_row'
SCHEMA_UNAVAILABLE = 'schema_validation_unavailable'


class ValidationError(RuntimeError):
    """A fail-closed refusal: validation could not be performed as required."""


def walk(value: Any, path: str = '$') -> Iterator[tuple[str, Any]]:
    """Yield ``(jsonpath, value)`` for every node, including the root."""
    yield path, value
    if isinstance(value, Mapping):
        for key in value:
            child = '%s.%s' % (path, key) if _plain_key(key) \
                else "%s['%s']" % (path, key)
            yield from walk(value[key], child)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            yield from walk(item, '%s[%d]' % (path, index))


def _plain_key(key: Any) -> bool:
    return isinstance(key, str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', key)


def scan_value(value: Any, path: str = '$') -> list[dict[str, Any]]:
    """Every placeholder/sentinel defect anywhere inside ``value``."""
    findings: list[dict[str, Any]] = []
    for location, node in walk(value, path):
        if not isinstance(node, str):
            continue
        for match in PLACEHOLDER_RE.finditer(node):
            findings.append({
                'code': UNRESOLVED_PLACEHOLDER,
                'path': location,
                'token': match.group(0),
            })
        for sentinel in SENTINELS:
            if sentinel in node:
                findings.append({
                    'code': REGISTERED_SENTINEL,
                    'path': location,
                    'token': sentinel,
                })
    return findings


def _identity_of(row: Mapping[str, Any]) -> str | None:
    for key in ('tm_record_id', 'fragment_id', 'record_id', 'id', 'entry_id'):
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def validate_row(row: Any, *, index: int,
                 require_provenance: bool = True) -> list[dict[str, Any]]:
    """Every defect in one row, with exact JSON paths."""
    prefix = '$[%d]' % index
    if not isinstance(row, Mapping):
        return [{'code': INVALID_ROW, 'path': prefix,
                 'detail': 'row is %s, not an object' % type(row).__name__}]
    findings = scan_value(row, prefix)
    if require_provenance and not any(key in row for key in REQUIRED_PROVENANCE):
        findings.append({
            'code': MISSING_PROVENANCE, 'path': prefix,
            'detail': 'row carries none of %s' % ', '.join(REQUIRED_PROVENANCE)})
    findings.extend(_hash_lineage_findings(row, prefix))
    findings.extend(_route_model_findings(row, prefix))
    for finding in findings:
        finding.setdefault('row_index', index)
        identity = _identity_of(row)
        if identity:
            finding.setdefault('identity', identity)
    return findings


def _hash_lineage_findings(row: Mapping[str, Any],
                           prefix: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for location, node in walk(row, prefix):
        if not location.endswith(('sha256', '_hash')):
            continue
        if node is None:
            continue
        if not isinstance(node, str) or not SHA_RE.match(node):
            findings.append({
                'code': BROKEN_HASH_LINEAGE, 'path': location,
                'detail': 'not a lowercase sha256 hex digest'})
    return findings


def _route_model_findings(row: Mapping[str, Any],
                          prefix: str) -> list[dict[str, Any]]:
    """A sealed row must not claim one route while naming another's model."""
    findings: list[dict[str, Any]] = []
    for location, node in walk(row, prefix):
        if not isinstance(node, Mapping):
            continue
        route = node.get('route_id') or node.get('route')
        served = node.get('served_model') or node.get('model_id')
        requested = node.get('requested_model')
        if route and requested and served and requested != served:
            findings.append({
                'code': ROUTE_MODEL_MISMATCH, 'path': location,
                'detail': 'requested %r but served %r on route %r'
                          % (requested, served, route)})
    return findings


def iter_jsonl(path: str) -> Iterator[tuple[int, Any]]:
    """Stream a JSONL file; the canonical artifact is ~24 MB (never load whole)."""
    with open(path, encoding='utf-8') as handle:
        for index, line in enumerate(handle):
            stripped = line.strip()
            if not stripped:
                continue
            yield index, json.loads(stripped)


def _jsonschema_or_fail(require_schema: bool):
    if not require_schema:
        return None
    try:
        import jsonschema  # noqa: F401  (presence check only)
    except ImportError as exc:
        raise ValidationError(
            'schema validation was required but jsonschema is unavailable: %s'
            % exc)
    return jsonschema


def validate_jsonl(path: str, *, require_provenance: bool = True,
                   require_schema: bool = False,
                   max_reported_rows: int | None = None) -> dict[str, Any]:
    """Recursively validate every row of a JSONL artifact, read-only.

    Returns a sealed-report-shaped dict; the caller decides whether to fence
    the defective rows or refuse.  The file is never modified.
    """
    _jsonschema_or_fail(require_schema)
    before_digest = sha256_file(path)
    rows = 0
    defective: dict[int, dict[str, Any]] = {}
    counts: dict[str, int] = {}
    occurrences = 0
    identities: dict[str, int] = {}
    duplicate_findings: list[dict[str, Any]] = []
    for index, row in iter_jsonl(path):
        rows += 1
        findings = validate_row(row, index=index,
                                require_provenance=require_provenance)
        if isinstance(row, Mapping):
            identity = _identity_of(row)
            if identity is not None:
                if identity in identities:
                    duplicate_findings.append({
                        'code': DUPLICATE_IDENTITY, 'path': '$[%d]' % index,
                        'identity': identity, 'row_index': index,
                        'detail': 'first seen at row %d' % identities[identity]})
                else:
                    identities[identity] = index
        if not findings:
            continue
        occurrences += len(findings)
        for finding in findings:
            counts[finding['code']] = counts.get(finding['code'], 0) + 1
        if max_reported_rows is None or len(defective) < max_reported_rows:
            defective[index] = {
                'row_index': index,
                'identity': _identity_of(row) if isinstance(row, Mapping) else None,
                'findings': findings,
            }
    for finding in duplicate_findings:
        counts[finding['code']] = counts.get(finding['code'], 0) + 1
        occurrences += 1
        defective.setdefault(int(finding['row_index']), {
            'row_index': finding['row_index'],
            'identity': finding.get('identity'),
            'findings': [],
        })['findings'].append(finding)
    after_digest = sha256_file(path)
    if before_digest != after_digest:
        raise ValidationError(
            'the validated artifact changed during a read-only pass: %s' % path)
    return {
        'schema': SCHEMA,
        'validator_version': VALIDATOR_VERSION,
        'path': os.path.abspath(path).replace('\\', '/'),
        'sha256': after_digest,
        'rows': rows,
        'defective_rows': len(defective),
        'occurrences': occurrences,
        'by_code': dict(sorted(counts.items())),
        'schema_validation': 'required' if require_schema else 'not_required',
        'read_only': True,
        'rows_detail': [defective[key] for key in sorted(defective)],
    }


def fence_report(report: Mapping[str, Any]) -> dict[str, Any]:
    """A fence: named defective rows, unchanged digest, no repair proposed."""
    return {
        'schema': 'pwg.pipeline.fence.v1',
        'validator_version': report.get('validator_version'),
        'path': report.get('path'),
        'sha256': report.get('sha256'),
        'rows': report.get('rows'),
        'fenced_rows': report.get('defective_rows'),
        'fenced_occurrences': report.get('occurrences'),
        'by_code': report.get('by_code'),
        'mutation': 'none',
        'disposition': 'reported and fenced; repair is out of Wave-1 scope',
        'identities': sorted(
            {str(row.get('identity')) for row in report.get('rows_detail', [])
             if row.get('identity')}),
    }


def is_clean(report: Mapping[str, Any]) -> bool:
    return int(report.get('defective_rows') or 0) == 0


def validate_rows(rows: Sequence[Any], *,
                  require_provenance: bool = True) -> dict[str, Any]:
    """In-memory twin of :func:`validate_jsonl` for candidate promotion rows."""
    defective: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    occurrences = 0
    for index, row in enumerate(rows):
        findings = validate_row(row, index=index,
                                require_provenance=require_provenance)
        if not findings:
            continue
        occurrences += len(findings)
        for finding in findings:
            counts[finding['code']] = counts.get(finding['code'], 0) + 1
        defective.append({'row_index': index,
                          'identity': _identity_of(row)
                          if isinstance(row, Mapping) else None,
                          'findings': findings})
    return {
        'schema': SCHEMA,
        'validator_version': VALIDATOR_VERSION,
        'rows': len(rows),
        'defective_rows': len(defective),
        'occurrences': occurrences,
        'by_code': dict(sorted(counts.items())),
        'rows_detail': defective,
    }


__all__ = [
    'SCHEMA', 'VALIDATOR_VERSION', 'PLACEHOLDER_RE', 'SENTINELS',
    'ValidationError', 'walk', 'scan_value', 'validate_row', 'validate_rows',
    'validate_jsonl', 'iter_jsonl', 'fence_report', 'is_clean',
    'UNRESOLVED_PLACEHOLDER', 'REGISTERED_SENTINEL', 'MISSING_PROVENANCE',
    'DUPLICATE_IDENTITY', 'BROKEN_HASH_LINEAGE', 'ROUTE_MODEL_MISMATCH',
    'INVALID_ROW', 'SCHEMA_UNAVAILABLE',
]
