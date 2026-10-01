"""Legacy import and shadow comparison (H3714 Wave 1, implementation step 6).

Five state authorities overlap today -- coordinator JSON, orchestrator SQLite,
supervisor checkpoints, call ledgers, and the promotion journal (plan, audit
verdict 2).  Import brings them into the campaign database as *evidence*, keyed
by source path plus content hash, so the migration is comparable rather than a
sixth authority.

Two rules make the import safe to re-run:

1. A repeat of the same path with identical content is a no-op.
2. The same path with a changed payload is a **refusal**, not an overwrite.

``shadow_sync`` compares legacy and pipeline lifecycle projections and holds
zero execution and zero promotion authority: it only records rows.
"""
from __future__ import annotations

import json
import os
import sqlite3
from typing import Any, Iterable, Mapping

from . import model
from .evidence import canonical_sha256, sha256_file
from .repository import Repository

SCHEMA = 'pwg.pipeline.import.v1'

KIND_COORDINATOR = 'coordinator_state'
KIND_ORCHESTRATOR = 'orchestrator_sqlite'
KIND_CALL_LEDGER = 'call_ledger'
KIND_PROMOTION_JOURNAL = 'promotion_journal'
KIND_REGISTRY = 'registry_projection'
KIND_TM_CHECKPOINT = 'pwg_tm_checkpoint'
KIND_COST_LEDGER = 'cost_ledger'
KIND_GATE = 'gate_result'
KIND_PROMOTED = 'promoted_artifact'
KIND_QUARANTINE = 'quarantine_artifact'
KIND_REFILL_RECEIPT = 'refill_receipt'

SOURCE_KINDS: tuple[str, ...] = (
    KIND_COORDINATOR, KIND_ORCHESTRATOR, KIND_CALL_LEDGER,
    KIND_PROMOTION_JOURNAL, KIND_REGISTRY, KIND_TM_CHECKPOINT,
    KIND_COST_LEDGER, KIND_GATE, KIND_PROMOTED, KIND_QUARANTINE,
    KIND_REFILL_RECEIPT,
)


class ImportRefusal(RuntimeError):
    """An import identity changed payload, or a source was unreadable."""


def _row_count(path: str) -> int:
    if path.endswith('.sqlite') or path.endswith('.db'):
        try:
            connection = sqlite3.connect('file:%s?mode=ro' % path.replace('\\', '/'),
                                         uri=True)
        except sqlite3.Error:
            return 0
        try:
            tables = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
            total = 0
            for (name,) in tables:
                if not name.replace('_', '').isalnum():
                    continue
                total += int(connection.execute(
                    'SELECT COUNT(*) FROM "%s"' % name).fetchone()[0])
            return total
        finally:
            connection.close()
    if path.endswith('.jsonl'):
        with open(path, encoding='utf-8') as handle:
            return sum(1 for line in handle if line.strip())
    try:
        with open(path, encoding='utf-8') as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return 0
    if isinstance(value, list):
        return len(value)
    if isinstance(value, Mapping):
        return len(value)
    return 1


def import_source(repository: Repository, *, source_kind: str, path: str,
                  campaign_id: str | None = None) -> dict[str, Any]:
    """Import one legacy source as immutable, hash-keyed evidence."""
    model.require_choice(source_kind, SOURCE_KINDS, 'import.source_kind')
    if not os.path.exists(path):
        raise ImportRefusal('legacy source does not exist: %s' % path)
    digest = sha256_file(path)
    import_id, was_new = repository.record_import(
        source_kind=source_kind, source_path=os.path.abspath(path),
        content_sha256=digest, campaign_id=campaign_id,
        row_count=_row_count(path))
    return {
        'schema': SCHEMA,
        'import_id': import_id,
        'source_kind': source_kind,
        'source_path': os.path.abspath(path).replace('\\', '/'),
        'content_sha256': digest,
        'imported': was_new,
    }


def import_tree(repository: Repository, mapping: Mapping[str, Iterable[str]], *,
                campaign_id: str | None = None) -> dict[str, Any]:
    """Import many sources: ``{source_kind: [path, ...]}``."""
    results: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for source_kind, paths in sorted(mapping.items()):
        for path in sorted(paths):
            if not os.path.exists(path):
                skipped.append({'source_kind': source_kind, 'path': path,
                                'reason': 'absent'})
                continue
            results.append(import_source(repository, source_kind=source_kind,
                                         path=path, campaign_id=campaign_id))
    return {
        'schema': SCHEMA,
        'imported': sum(1 for row in results if row['imported']),
        'already_present': sum(1 for row in results if not row['imported']),
        'skipped': skipped,
        'sources': results,
    }


def legacy_projection(value: Mapping[str, Any]) -> dict[str, str]:
    """Flatten a legacy lifecycle record into comparable ``key -> value`` rows."""
    flat: dict[str, str] = {}

    def walk(node: Any, prefix: str) -> None:
        if isinstance(node, Mapping):
            for key in sorted(node):
                walk(node[key], '%s.%s' % (prefix, key) if prefix else str(key))
        elif isinstance(node, list):
            for index, item in enumerate(node):
                walk(item, '%s[%d]' % (prefix, index))
        else:
            flat[prefix] = json.dumps(node, ensure_ascii=False, sort_keys=True)

    walk(value, '')
    return flat


def shadow_sync(repository: Repository, *, route: str,
                legacy: Mapping[str, Any], pipeline: Mapping[str, Any],
                explanations: Mapping[str, str] | None = None
                ) -> dict[str, Any]:
    """Compare a legacy lifecycle record with the pipeline's, recording rows.

    Zero execution and zero promotion authority: the only side effect is a row
    in ``shadow_observations``.  A mismatch with a recorded explanation is not a
    failure; an *unexplained* one is (V9).
    """
    model.require_choice(route, model.ROUTES, 'shadow.route')
    left = legacy_projection(legacy)
    right = legacy_projection(pipeline)
    explanations = dict(explanations or {})
    keys = sorted(set(left) | set(right))
    matched = 0
    for key in keys:
        if repository.record_shadow(
                route=route, legacy_key=key,
                legacy_value=left.get(key), pipeline_value=right.get(key),
                explanation=explanations.get(key)):
            matched += 1
    mismatches = repository.shadow_mismatches(route)
    return {
        'schema': 'pwg.pipeline.shadow.v1',
        'route': route,
        'compared_keys': len(keys),
        'matched': matched,
        'unexplained_mismatches': len(mismatches),
        'mismatch_keys': [row['legacy_key'] for row in mismatches],
        'legacy_sha256': canonical_sha256(dict(legacy)),
        'pipeline_sha256': canonical_sha256(dict(pipeline)),
    }


__all__ = [
    'SCHEMA', 'SOURCE_KINDS', 'ImportRefusal', 'import_source', 'import_tree',
    'shadow_sync', 'legacy_projection',
    'KIND_COORDINATOR', 'KIND_ORCHESTRATOR', 'KIND_CALL_LEDGER',
    'KIND_PROMOTION_JOURNAL', 'KIND_REGISTRY', 'KIND_TM_CHECKPOINT',
    'KIND_COST_LEDGER', 'KIND_GATE', 'KIND_PROMOTED', 'KIND_QUARANTINE',
    'KIND_REFILL_RECEIPT',
]
