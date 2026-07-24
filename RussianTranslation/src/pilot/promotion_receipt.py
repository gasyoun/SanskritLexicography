#!/usr/bin/env python
"""Promotion receipt schema v1 + pure startup reconcile (H1554 Track B scaffold).

Offline / pure-function module. No coordinator wiring, no live store mutation, no
multi-profile scheduler (that is H1437). Wave-1 only lands:

  * ``AttemptRunBinding`` — run/attempt/lease identity for sealed work
  * ``PromotionReceipt`` — durable receipt after a wave's acceptance barrier
  * ``write_receipt`` / ``load_receipt`` / ``load_receipts``
  * ``reconcile_startup(receipts, observed_store_keys) -> ReconcilePlan``

Contract (ARCHITECTURE_RussianTranslation_full_audit_improvement.md §B):

  reconcile_startup → {promote_missing, skip_already_present, error_inconsistent}

H1437 may later rename/extend symbols; prefer their names if they land first.
This module is deliberately thin so H1437 can consume it without dual systems.

Authored for H1554 by Grok 4.5 (override of Opus 4.8 lock). Offline only.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_V1 = 'pwg_ru.promotion_receipt.v1'
RECEIPT_FILENAME_SUFFIX = '.promotion_receipt.json'

# Reconcile action kinds (stable string tags for fixtures + callers).
PROMOTE_MISSING = 'promote_missing'
SKIP_ALREADY_PRESENT = 'skip_already_present'
ERROR_INCONSISTENT = 'error_inconsistent'


@dataclass(frozen=True)
class AttemptRunBinding:
    """Identity of one sealed attempt under a scheduler run / lease."""

    run_id: str
    attempt_id: str
    lease_id: str

    def __post_init__(self) -> None:
        for name in ('run_id', 'attempt_id', 'lease_id'):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError('AttemptRunBinding.%s must be a non-empty string' % name)


@dataclass(frozen=True)
class PromotionReceipt:
    """Durable promotion receipt (schema v1).

    Written after a wave's acceptance barrier *claims* which keys should land;
    reconcile_startup compares this claim to the observed store key set on restart.
    """

    schema: str
    run_id: str
    attempt_id: str
    lease_id: str
    keys_accepted: tuple[str, ...]
    keys_rejected: tuple[str, ...]
    store_path: str
    row_count_before: int
    row_count_after: int
    tm_rebuild: bool
    created_at: str

    def binding(self) -> AttemptRunBinding:
        return AttemptRunBinding(
            run_id=self.run_id,
            attempt_id=self.attempt_id,
            lease_id=self.lease_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'schema': self.schema,
            'run_id': self.run_id,
            'attempt_id': self.attempt_id,
            'lease_id': self.lease_id,
            'keys_accepted': list(self.keys_accepted),
            'keys_rejected': list(self.keys_rejected),
            'store_path': self.store_path,
            'row_count_before': self.row_count_before,
            'row_count_after': self.row_count_after,
            'tm_rebuild': self.tm_rebuild,
            'created_at': self.created_at,
        }


@dataclass(frozen=True)
class ReconcileAction:
    """One reconcile decision for a single receipt's accepted-key set."""

    kind: str
    lease_id: str
    run_id: str
    attempt_id: str
    keys: tuple[str, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            'kind': self.kind,
            'lease_id': self.lease_id,
            'run_id': self.run_id,
            'attempt_id': self.attempt_id,
            'keys': list(self.keys),
            'reason': self.reason,
        }


@dataclass
class ReconcilePlan:
    """Partition of receipts into the three reconcile buckets."""

    promote_missing: list[ReconcileAction] = field(default_factory=list)
    skip_already_present: list[ReconcileAction] = field(default_factory=list)
    error_inconsistent: list[ReconcileAction] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            PROMOTE_MISSING: [a.to_dict() for a in self.promote_missing],
            SKIP_ALREADY_PRESENT: [a.to_dict() for a in self.skip_already_present],
            ERROR_INCONSISTENT: [a.to_dict() for a in self.error_inconsistent],
        }


def make_receipt(
    binding: AttemptRunBinding,
    *,
    keys_accepted: Sequence[str],
    keys_rejected: Sequence[str] | None = None,
    store_path: str,
    row_count_before: int,
    row_count_after: int,
    tm_rebuild: bool = False,
    created_at: str,
    schema: str = SCHEMA_V1,
) -> PromotionReceipt:
    """Build a validated PromotionReceipt from an AttemptRunBinding + payload."""
    return receipt_from_mapping({
        'schema': schema,
        'run_id': binding.run_id,
        'attempt_id': binding.attempt_id,
        'lease_id': binding.lease_id,
        'keys_accepted': list(keys_accepted),
        'keys_rejected': list(keys_rejected or ()),
        'store_path': store_path,
        'row_count_before': row_count_before,
        'row_count_after': row_count_after,
        'tm_rebuild': tm_rebuild,
        'created_at': created_at,
    })


def receipt_from_mapping(data: Mapping[str, Any]) -> PromotionReceipt:
    """Parse and validate a receipt mapping (JSON object)."""
    if not isinstance(data, Mapping):
        raise ValueError('receipt must be a mapping')
    schema = data.get('schema')
    if schema != SCHEMA_V1:
        raise ValueError('unsupported receipt schema %r (want %r)' % (schema, SCHEMA_V1))

    def _req_str(name: str) -> str:
        value = data.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError('receipt.%s must be a non-empty string' % name)
        return value

    def _req_keys(name: str) -> tuple[str, ...]:
        value = data.get(name)
        if value is None:
            value = []
        if not isinstance(value, list) or any(
                not isinstance(k, str) or not k.strip() for k in value):
            raise ValueError('receipt.%s must be a list of non-empty strings' % name)
        # Stable unique order: first occurrence wins; duplicates are a schema error.
        seen: set[str] = set()
        out: list[str] = []
        for key in value:
            if key in seen:
                raise ValueError('receipt.%s has duplicate key %r' % (name, key))
            seen.add(key)
            out.append(key)
        return tuple(out)

    def _req_int(name: str) -> int:
        value = data.get(name)
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError('receipt.%s must be an int' % name)
        if value < 0:
            raise ValueError('receipt.%s must be >= 0' % name)
        return value

    tm = data.get('tm_rebuild')
    if not isinstance(tm, bool):
        raise ValueError('receipt.tm_rebuild must be a bool')

    accepted = _req_keys('keys_accepted')
    rejected = _req_keys('keys_rejected')
    overlap = sorted(set(accepted) & set(rejected))
    if overlap:
        raise ValueError(
            'receipt keys_accepted and keys_rejected overlap: %s' % ', '.join(overlap[:10]))

    return PromotionReceipt(
        schema=schema,
        run_id=_req_str('run_id'),
        attempt_id=_req_str('attempt_id'),
        lease_id=_req_str('lease_id'),
        keys_accepted=accepted,
        keys_rejected=rejected,
        store_path=_req_str('store_path'),
        row_count_before=_req_int('row_count_before'),
        row_count_after=_req_int('row_count_after'),
        tm_rebuild=tm,
        created_at=_req_str('created_at'),
    )


def write_receipt(path: str, receipt: PromotionReceipt) -> str:
    """Atomically write a receipt JSON file. Returns the path written."""
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    payload = json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)
    payload += '\n'
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    return path


def load_receipt(path: str) -> PromotionReceipt:
    """Load one receipt file."""
    with open(path, encoding='utf-8') as fh:
        data = json.load(fh)
    return receipt_from_mapping(data)


def load_receipts(directory: str) -> list[PromotionReceipt]:
    """Load every ``*.promotion_receipt.json`` under *directory* (non-recursive).

    Sorted by basename for deterministic reconcile order.
    """
    directory = os.path.abspath(directory)
    if not os.path.isdir(directory):
        raise FileNotFoundError('receipts directory not found: %s' % directory)
    names = sorted(
        n for n in os.listdir(directory)
        if n.endswith(RECEIPT_FILENAME_SUFFIX) and os.path.isfile(os.path.join(directory, n))
    )
    return [load_receipt(os.path.join(directory, name)) for name in names]


def _row_count_invariant_reason(receipt: PromotionReceipt) -> str | None:
    """Return a human reason if the receipt's own row counts are inconsistent."""
    expected_delta = len(receipt.keys_accepted)
    actual_delta = receipt.row_count_after - receipt.row_count_before
    if receipt.row_count_after < receipt.row_count_before:
        return (
            'row_count_after (%d) < row_count_before (%d)'
            % (receipt.row_count_after, receipt.row_count_before)
        )
    # Accepted keys are the rows the receipt claims were added; rejected never land.
    if actual_delta != expected_delta:
        return (
            'row_count delta %d != len(keys_accepted) %d '
            '(before=%d after=%d)'
            % (actual_delta, expected_delta,
               receipt.row_count_before, receipt.row_count_after)
        )
    return None


def reconcile_startup(
    receipts: Sequence[PromotionReceipt],
    observed_store_keys: Iterable[str],
) -> ReconcilePlan:
    """Pure startup reconcile: compare sealed receipts to observed store keys.

    For each receipt's ``keys_accepted`` set:

    * all present  → ``skip_already_present`` (idempotent re-entry / double receipt)
    * all missing  → ``promote_missing`` (crash after receipt, before store write)
    * partial      → ``error_inconsistent`` (store/receipt drift; human/ops)

    Receipt-internal row-count invariants that fail also go to ``error_inconsistent``
    and suppress the presence-based action for that receipt (fail closed).
    """
    store = set(observed_store_keys)
    plan = ReconcilePlan()

    for receipt in receipts:
        keys = receipt.keys_accepted
        invariant = _row_count_invariant_reason(receipt)
        if invariant is not None:
            plan.error_inconsistent.append(ReconcileAction(
                kind=ERROR_INCONSISTENT,
                lease_id=receipt.lease_id,
                run_id=receipt.run_id,
                attempt_id=receipt.attempt_id,
                keys=keys,
                reason=invariant,
            ))
            continue

        if not keys:
            # Empty accept set: nothing to promote; treat as already consistent.
            plan.skip_already_present.append(ReconcileAction(
                kind=SKIP_ALREADY_PRESENT,
                lease_id=receipt.lease_id,
                run_id=receipt.run_id,
                attempt_id=receipt.attempt_id,
                keys=keys,
                reason='empty keys_accepted; nothing to promote',
            ))
            continue

        present = tuple(k for k in keys if k in store)
        missing = tuple(k for k in keys if k not in store)

        if present and missing:
            plan.error_inconsistent.append(ReconcileAction(
                kind=ERROR_INCONSISTENT,
                lease_id=receipt.lease_id,
                run_id=receipt.run_id,
                attempt_id=receipt.attempt_id,
                keys=keys,
                reason=(
                    'partial presence: present=%s missing=%s'
                    % (list(present), list(missing))
                ),
            ))
        elif missing:
            plan.promote_missing.append(ReconcileAction(
                kind=PROMOTE_MISSING,
                lease_id=receipt.lease_id,
                run_id=receipt.run_id,
                attempt_id=receipt.attempt_id,
                keys=keys,
                reason='accepted keys absent from store (crash after receipt?)',
            ))
        else:
            plan.skip_already_present.append(ReconcileAction(
                kind=SKIP_ALREADY_PRESENT,
                lease_id=receipt.lease_id,
                run_id=receipt.run_id,
                attempt_id=receipt.attempt_id,
                keys=keys,
                reason='all accepted keys already present in store',
            ))

    return plan


def main(argv: Sequence[str] | None = None) -> int:
    """Tiny CLI: load receipts from a dir and reconcile against a key list file."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split('\n\n', 1)[0])
    parser.add_argument('--receipts-dir', required=True,
                        help='Directory of *.promotion_receipt.json files')
    parser.add_argument(
        '--store-keys',
        required=True,
        help='Text file: one store key per line (fixture / offline only)',
    )
    parser.add_argument('--json', action='store_true', help='Emit plan as JSON')
    args = parser.parse_args(list(argv) if argv is not None else None)

    receipts = load_receipts(args.receipts_dir)
    with open(args.store_keys, encoding='utf-8') as fh:
        keys = [line.strip() for line in fh if line.strip() and not line.startswith('#')]
    plan = reconcile_startup(receipts, keys)
    if args.json:
        print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        d = plan.to_dict()
        for kind in (PROMOTE_MISSING, SKIP_ALREADY_PRESENT, ERROR_INCONSISTENT):
            print('%s: %d' % (kind, len(d[kind])))
            for action in d[kind]:
                print('  - lease=%s keys=%s reason=%s'
                      % (action['lease_id'], action['keys'], action['reason']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
