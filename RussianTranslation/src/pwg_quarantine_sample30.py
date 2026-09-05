#!/usr/bin/env python
"""H4053 — bounded report-only translate path for the PWG glyph quarantine.

The missing entrypoint identified by H3791 (02-09-2026): "translate N
pre-selected keys, report only, never promote".  It accepts exactly a supplied
card list (the frozen 30-card nested sample, or an explicit key file), records
immutable input hashes, isolates every output under a caller-supplied evidence
directory, and has NO promote/apply capability at all: the campaign is created
``promotable=False`` and the module contains no store-writing code.

Key properties (each proven by the offline selftest against a fake provider):

* **max-call reservation before I/O** — the shared kernel reserves a slot in
  the ``pwg.call_reservation.v1`` ledger strictly before any dispatch; a
  ceiling refusal happens with zero provider calls on that slot.
* **resume without duplicate spend** — per-card idempotency keys plus a local
  run-state journal; a resumed run replays the existing reservation instead of
  spending a new slot and never re-dispatches a succeeded card.
* **output attribution** — every packet row carries call_id, reservation_id,
  request/response SHA-256, usage and served model.
* **preserved input bytes** — the keys/frozen packet and the store/mirror/
  queue surfaces are hashed before and after; the run refuses to end unless
  the guard surfaces are byte-identical (the store is only ever read).
* **unchanged canonical store/mirror/queue** — same guard; a store absent on
  this box is recorded as ``absent_read_only``, never fabricated.

Label discipline (H4053 work item 1): the quarantine population figure
(10,902 of 11,519 RU-store rows, 02-09 remeasure) is a *segmentation-change
flag*, NOT an observed bad-translation rate.  Every emitted row keeps
``ru_quality_verdict: unknown_not_measured`` until a real paid generation and
independent human review happen.

Offline usage::

    python src/pwg_quarantine_sample30.py freeze                 # packet only
    python src/pwg_quarantine_sample30.py selftest               # 6 proofs
    python src/pwg_quarantine_sample30.py run --frozen-packet \\
        reports/H4053_quarantine_sample30_frozen.json --dry-run \\
        --provider fake --max-calls 30 --cost-ceiling-usd 4.00 \\
        --workdir /tmp/h4053_replay --evidence-dir /tmp/h4053_evidence
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
for _path in (HERE, os.path.join(HERE, 'pilot')):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from pwg_pipeline import faults, kernel, model, providers, repository as repo_mod  # noqa: E402

SCHEMA = 'h4053.quarantine_sample30.v1'

DEFAULT_PARENT_SAMPLE = os.path.join(
    RT, 'reports', 'pwg_ru_glyph_quarantine_sample_2026-08-01.json')
DEFAULT_FRESH_QUARANTINE = os.path.join(
    RT, 'reports', 'pwg_ru_glyph_quarantine.jsonl')
DEFAULT_SENSE_AUDIT = os.path.join(RT, 'reports', 'pwg_sense_glyph_audit.json')
DEFAULT_FROZEN_PACKET = os.path.join(
    RT, 'reports', 'H4053_quarantine_sample30_frozen.json')

SAMPLE_N = 30
FREEZE_SEED = 20260904

# Review classes for the paid quality read. Mechanical quarantine flags
# pre-sort only `segmentation_only`; the other classes are assigned by the
# independent human review AFTER generation — never by this module.
REVIEW_CLASSES = (
    'segmentation_only', 'semantic_mistranslation', 'sanskrit_loss',
    'apparatus', 'ambiguous')
UNMEASURED = 'unmeasured_pending_paid_read'
NOT_MEASURED = 'unknown_not_measured'

SEGMENTATION_FLAG_LABEL = (
    'segmentation-change flag (10,902 of 11,519 RU-store rows, 02-09-2026'
    ' remeasure) — NOT an observed bad-translation rate')

EXIT_OK = 0
EXIT_STOP = 3


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(65536), b''):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def load_jsonl(path: str) -> list[dict]:
    rows = []
    with open(path, encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


# --- freeze ---------------------------------------------------------------

def _identity(card: dict) -> tuple:
    return (card.get('key1') or '', card.get('subcard') or '')


def freeze_sample(parent_sample_path: str = DEFAULT_PARENT_SAMPLE,
                  fresh_quarantine_path: str = DEFAULT_FRESH_QUARANTINE,
                  sense_audit_path: str = DEFAULT_SENSE_AUDIT,
                  n: int = SAMPLE_N, seed: int = FREEZE_SEED) -> dict:
    """Deterministic nested n-card sample from the 01-08 200-row sample.

    Parent identities are resolved against the fresh quarantine population
    (where identity still resolves).  Unavailable identities are listed
    explicitly and replaced by deterministic substitutions drawn from the
    fresh population with the same stratified round-robin used on 01-08.
    """
    import sample_glyph_quarantine as sgq

    with open(parent_sample_path, encoding='utf-8') as handle:
        parent = json.load(handle)
    fresh_rows = load_jsonl(fresh_quarantine_path)
    fresh_by_identity = {_identity(row): row for row in fresh_rows}
    fresh_order = {  # stable positional order for deterministic substitution
        _identity(row): index for index, row in enumerate(fresh_rows)}

    audit_by_key1: dict[str, list[dict]] = collections.defaultdict(list)
    if os.path.isfile(sense_audit_path):
        with open(sense_audit_path, encoding='utf-8') as handle:
            audit = json.load(handle)
        for delta in audit.get('per_record_deltas') or []:
            if delta.get('key1'):
                audit_by_key1[delta['key1']].append(delta)

    resolved, unavailable = [], []
    for index, card in enumerate(parent.get('sample') or []):
        fresh = fresh_by_identity.get(_identity(card))
        if fresh is None:
            unavailable.append({
                'key1': card.get('key1'), 'subcard': card.get('subcard'),
                'parent_index': index,
                'cause': 'identity absent from fresh quarantine population'})
        else:
            resolved.append((index, card, fresh))

    substitutions: list[dict] = []
    if unavailable:
        claimed = {_identity(row) for _, _, row in resolved}
        claimed.update(_identity(card) for card in unavailable)
        remaining = [row for row in fresh_rows
                     if _identity(row) not in claimed]
        remaining.sort(key=lambda row: fresh_order[_identity(row)])
        drawn = sgq.sample_stratified(remaining, len(unavailable), seed)
        for slot, row in enumerate(drawn):
            substitutions.append({
                'replaces_parent_index': unavailable[slot]['parent_index'],
                'key1': row.get('key1'), 'subcard': row.get('subcard'),
                'rule': 'same stratified round-robin over the fresh '
                        'population, deterministic order (subcard-sorted '
                        'positional index), seed %d' % seed})
            resolved.append((None, {}, row))

    picked: list[tuple] = []
    seen_identities: set[tuple] = set()
    for entry in resolved:
        fresh = entry[2]
        identity = (_identity(fresh), fresh.get('sense_tag') or '')
        if identity in seen_identities:
            continue  # the parent 200 contains a few duplicate identities;
            # a card-level quality read needs exactly one row per identity
        seen_identities.add(identity)
        picked.append(entry)
        if len(picked) >= n:
            break
    cards = []
    for parent_index, parent_card, fresh in picked:
        deltas = audit_by_key1.get(fresh.get('key1') or '') or []
        cards.append({
            'key1': fresh.get('key1'),
            'subcard': fresh.get('subcard'),
            'h': fresh.get('h'),
            'sense_tag': fresh.get('sense_tag'),
            'reason': fresh.get('reason'),
            'parent_sample_index': parent_index,
            'parent_class_01_08': parent_card.get('class'),
            'audit_deltas': len(deltas),
            'audit_resolved': bool(deltas),
            'input_hash': sha256_text(json.dumps(
                fresh, ensure_ascii=False, sort_keys=True)),
            'review_class': UNMEASURED,
            'ru_quality_verdict': NOT_MEASURED,
        })

    return {
        'schema': SCHEMA,
        'kind': 'frozen_nested_sample',
        'seed': seed,
        'n_requested': n,
        'n_frozen': len(cards),
        'parent_sample': {
            'path': os.path.relpath(parent_sample_path, RT).replace('\\', '/'),
            'date': parent.get('date'),
            'n': parent.get('n_sampled'),
            'seed': parent.get('seed'),
        },
        'fresh_population': {
            'path': os.path.relpath(fresh_quarantine_path, RT)
                        .replace('\\', '/'),
            'rows': len(fresh_rows),
            'flag_label': SEGMENTATION_FLAG_LABEL,
        },
        'unavailable_parent_identities': unavailable,
        'deterministic_substitutions': substitutions,
        'review_classes': list(REVIEW_CLASSES),
        'review_class_assignment': (
            'assigned only by independent human review after an actual paid '
            'generation; this packet ships every card as %s' % UNMEASURED),
        'cards': cards,
    }


def cmd_freeze(args: argparse.Namespace) -> int:
    packet = freeze_sample(args.parent_sample, args.fresh_quarantine,
                           args.sense_audit, args.n, args.seed)
    assert packet['n_frozen'] == args.n, (
        'freeze produced %d cards, expected %d'
        % (packet['n_frozen'], args.n))
    with open(args.out, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(packet, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print('frozen %d/%d cards -> %s' % (
        packet['n_frozen'], args.n, args.out))
    print('unavailable parent identities: %d; substitutions: %d' % (
        len(packet['unavailable_parent_identities']),
        len(packet['deterministic_substitutions'])))
    return EXIT_OK


# --- report-only run ------------------------------------------------------

def _load_cards(args: argparse.Namespace) -> tuple[list[dict], str, str]:
    """Return (cards, source_path, source_sha256) from packet or key file."""
    if bool(args.frozen_packet) == bool(args.keys_file):
        raise SystemExit('exactly one of --frozen-packet / --keys-file')
    source = args.frozen_packet or args.keys_file
    if args.frozen_packet:
        with open(source, encoding='utf-8') as handle:
            packet = json.load(handle)
        if packet.get('kind') != 'frozen_nested_sample':
            raise SystemExit('%s is not a frozen_nested_sample packet' % source)
        cards = packet['cards']
    else:
        cards = []
        with open(source, encoding='utf-8') as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('{'):
                    card = json.loads(line)
                else:
                    card = {'subcard': line, 'key1': line.split('~~')[0]}
                card.setdefault('input_hash', sha256_text(line))
                card.setdefault('review_class', UNMEASURED)
                card.setdefault('ru_quality_verdict', NOT_MEASURED)
                cards.append(card)
    return cards, source, sha256_file(source)


def _old_ru_join(store_path: str, subcard: str) -> dict:
    """Read-only old-RU lookup; never writes, never fabricates."""
    if not store_path or not os.path.isfile(store_path):
        return {'old_ru': None, 'old_ru_join': 'store_absent_read_only'}
    for row in load_jsonl(store_path):
        if row.get('subcard') == subcard:
            text = row.get('ru') or row.get('target_string') \
                or row.get('translation')
            return {'old_ru': text, 'old_ru_join': 'hit'}
    return {'old_ru': None, 'old_ru_join': 'miss'}


def _open_call_rows(repository_db: str) -> list[dict]:
    """Read-only listing of unfinalized calls across ALL campaigns."""
    import sqlite3
    connection = sqlite3.connect('file:%s?mode=ro' % repository_db, uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            'SELECT c.call_id, c.idempotency_key, c.state, j.campaign_id'
            ' FROM calls c'
            ' JOIN attempts a ON a.attempt_id = c.attempt_id'
            ' JOIN jobs j ON j.job_id = a.job_id'
            ' WHERE c.finalized_at IS NULL'
            ' ORDER BY c.call_id').fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def _base_key(effective_key: str) -> str:
    return effective_key.split(':resume')[0]


def _reconcile_interrupted(repository, repository_db: str, evidence_dir: str
                           ) -> tuple[dict[str, int], list[dict]]:
    """Close out call rows a crash left open, before any new spend.

    Sweeps every campaign in the run database, so a resumed run cannot
    re-dispatch a card an earlier run already sent to the provider.

    * A call with a sealed **response** receipt keeps its raw provider reply:
      it is left open for human reconciliation and its card is skipped this
      run — re-dispatching it could bill the provider twice.
    * A call with **no** response receipt provably never reached the provider
      (zero I/O): it is terminally accounted as ``interrupted_no_provider_io``
      and its card may re-execute under a derived resume key.  The original
      reservation stays spent — the ledger does not refund crashed slots.
    """
    retired: dict[str, int] = {}
    needs_human: list[dict] = []
    db = os.path.join(repository_db, 'sample.sqlite')
    if not os.path.isfile(db):
        return retired, needs_human
    for row in _open_call_rows(db):
        response_sealed = os.path.isfile(os.path.join(
            evidence_dir, row['call_id'], 'response.json'))
        if response_sealed:
            needs_human.append(row)
            continue
        current = repository.call_state(row['call_id'])
        repository.transition_call(row['call_id'], current, model.CALL_ERRORED)
        repository.finalize_call(
            row['call_id'], state=model.CALL_ERRORED,
            telemetry={'cost_evaluable': False, 'input_tokens': 0,
                       'output_tokens': 0, 'observed_cost_usd': 0.0},
            failure_class='interrupted_no_provider_io')
        retired[_base_key(row['idempotency_key'])] = \
            retired.get(_base_key(row['idempotency_key']), 0) + 1
    return retired, needs_human


def run_sample(cards: list[dict], *, workdir: str, evidence_dir: str,
               provider: str, requested_model: str, max_calls: int,
               cost_ceiling_usd: float, timeout_ms: int,
               max_output_tokens: int, store_path: str = '',
               mirror_path: str = '', queue_path: str = '',
               fault_hook: faults.FaultHook | None = None,
               adapter=None, dry_run: bool = False) -> dict:
    """One report-only sample run. Returns the sealed run receipt."""
    os.makedirs(workdir, exist_ok=True)
    os.makedirs(evidence_dir, exist_ok=True)
    state_path = os.path.join(workdir, 'run_state.jsonl')

    guard_paths = {'store': store_path, 'mirror': mirror_path,
                   'queue': queue_path}
    guard_before, guard_absent = {}, []
    for name, path in guard_paths.items():
        if path and os.path.isfile(path):
            guard_before[name] = {'path': path, 'sha256': sha256_file(path)}
        else:
            guard_absent.append(name)

    BASE_CAMPAIGN = 'h4053-quarantine-sample30'
    done: dict[str, dict] = {}
    if os.path.isfile(state_path):
        for row in load_jsonl(state_path):
            done[row['idempotency_key']] = row
    # Each resume run seals under a fresh campaign namespace (the artifact
    # table is content-addressed per campaign), while card idempotency keys
    # stay stable so the state file dedupes across runs.
    prior_campaigns = {row.get('campaign_id') for row in done.values()}
    campaign_id = BASE_CAMPAIGN + (
        '-r%d' % len(prior_campaigns) if done else '')
    plan = [{
        'job_id': '%s.job.%d' % (campaign_id, index),
        'idempotency_key': sha256_text('%s:%s:%s' % (
            BASE_CAMPAIGN, card.get('subcard'), card.get('input_hash'))),
        'card': card,
    } for index, card in enumerate(cards)]

    receipt: dict = {
        'schema': SCHEMA, 'kind': 'report_only_sample_run',
        'campaign_id': campaign_id, 'provider': provider,
        'requested_model': requested_model,
        'max_calls': max_calls, 'cost_ceiling_usd': cost_ceiling_usd,
        'dry_run': bool(dry_run), 'cards': len(cards),
        'resumed_skipped': 0, 'calls_dispatched': 0, 'calls_succeeded': 0,
        'calls_failed': 0, 'refusals': [], 'promotions': 0,
        'store_mutations': 0,
        'guard_before': guard_before, 'guard_absent_surfaces': guard_absent,
        'packet_path': None,
    }
    if dry_run:
        receipt['plan'] = [{'job_id': item['job_id'],
                            'idempotency_key': item['idempotency_key'],
                            'subcard': item['card'].get('subcard')}
                           for item in plan]
        return receipt

    repository = repo_mod.open_repository(
        os.path.join(workdir, 'sample.sqlite'))
    try:
        try:
            repository.campaign(campaign_id)
        except repo_mod.RepositoryError:
            repository.create_campaign(model.Campaign(
                campaign_id=campaign_id, scope='h4053-quarantine-sample30',
                language='ru', route=adapter.route, max_calls=max_calls,
                cost_ceiling_usd=cost_ceiling_usd, promotable=False,
                created_by='pwg_quarantine_sample30'))
        for item in plan:
            try:
                repository.job_state(item['job_id'])
            except repo_mod.RepositoryError:
                repository.add_job(model.Job(
                    job_id=item['job_id'], campaign_id=campaign_id,
                    kind='card',
                    source_identity=item['card'].get('subcard') or '',
                    source_hash=item['card'].get('input_hash')))
        paid = kernel.PaidCallKernel(
            repository, campaign_id=campaign_id,
            evidence_dir=evidence_dir,
            ledger_path=os.path.join(workdir, 'call_reservations.json'),
            fault_hook=fault_hook)

        retired_keys, needs_human = _reconcile_interrupted(
            repository, workdir, evidence_dir)
        human_keys = {_base_key(row['idempotency_key']) for row in needs_human}
        if needs_human:
            receipt['needs_human_reconciliation'] = [
                {'call_id': row['call_id'],
                 'campaign_id': row['campaign_id'],
                 'idempotency_key': row['idempotency_key']}
                for row in needs_human]

        rows = []
        state_handle = open(state_path, 'a', encoding='utf-8', newline='\n')
        try:
            for item in plan:
                card, key = item['card'], item['idempotency_key']
                if key in human_keys:
                    receipt['resumed_skipped'] += 1
                    prior = done.get(key)
                    if prior:
                        rows.append(prior['packet_row'])
                    continue
                if key in retired_keys:
                    key = '%s:resume%d' % (key, retired_keys[key])
                prior = done.get(item['idempotency_key'])
                if prior and prior.get('state') == model.CALL_SUCCEEDED:
                    receipt['resumed_skipped'] += 1
                    rows.append(prior['packet_row'])
                    continue
                payload = {
                    'fragment_id': card.get('subcard'),
                    'source_string': card.get('reason') or '',
                    'key1': card.get('key1'), 'h': card.get('h'),
                    'sense_tag': card.get('sense_tag'),
                }
                state = repository.job_state(item['job_id'])
                for step in (model.PREPARED, model.RESERVED, model.RUNNING):
                    if state == model.RUNNING:
                        break
                    repository.transition_job(item['job_id'], state, step)
                    state = step
                try:
                    outcome = paid.execute(
                        adapter, job_ids=[item['job_id']],
                        job_payloads=[payload],
                        requested_model=requested_model,
                        idempotency_key=key, timeout_ms=timeout_ms,
                        max_output_tokens=max_output_tokens)
                except kernel.KernelRefusal as exc:
                    receipt['refusals'].append({
                        'subcard': card.get('subcard'),
                        'failure_class': exc.failure_class,
                        'detail': str(exc)})
                    break
                fragments = (outcome.parsed or {}).get('fragments') or []
                candidate = fragments[0].get('target_string') \
                    if fragments else None
                packet_row = dict(card)
                packet_row.update(_old_ru_join(store_path,
                                               card.get('subcard') or ''))
                packet_row['candidate_ru'] = candidate
                packet_row['machine'] = {
                    'call_id': outcome.call_id, 'state': outcome.state,
                    'route': outcome.route,
                    'reservation_bound': True,
                    'request_sha256': outcome.request_sha256,
                    'response_sha256': outcome.response_sha256,
                    'usage': outcome.usage,
                    'failure_class': outcome.failure_class,
                    'served_model': outcome.served_model,
                }
                rows.append(packet_row)
                state_row = {
                    'idempotency_key': item['idempotency_key'],
                    'campaign_id': campaign_id,
                    'job_id': item['job_id'], 'subcard': card.get('subcard'),
                    'state': outcome.state, 'call_id': outcome.call_id,
                    'packet_row': packet_row}
                state_handle.write(json.dumps(
                    state_row, ensure_ascii=False, sort_keys=True) + '\n')
                state_handle.flush()
                if outcome.succeeded:
                    receipt['calls_succeeded'] += 1
                else:
                    receipt['calls_failed'] += 1
        finally:
            state_handle.close()

        accounting = repository.call_accounting(campaign_id)
        receipt['observed_cost_usd'] = float(
            accounting.get('observed_cost_usd') or 0.0)
        receipt['open_promotions'] = len(
            repository.open_promotions(campaign_id))
    finally:
        repository.close()

    receipt['calls_dispatched'] = (receipt['calls_succeeded']
                                   + receipt['calls_failed'])
    receipt['calls_dispatched'] += sum(
        1 for ref in receipt['refusals']
        if ref['failure_class'] == kernel.FAILURE_UNAVAILABLE)

    packet_path = os.path.join(evidence_dir, 'H4053_review_packet.json')
    packet = {
        'schema': SCHEMA, 'kind': 'review_packet_report_only',
        'label': SEGMENTATION_FLAG_LABEL,
        'quality_verdict': (
            'unmeasured: no paid generation has run'
            if receipt['calls_succeeded'] == 0 else
            'candidate text is machine output; independent human review '
            'required before any quality claim'),
        'promotions': 0, 'store_mutations': 0,
        'rows': rows,
    }
    with open(packet_path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(packet, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    receipt['packet_path'] = packet_path

    guard_after = {}
    for name, entry in guard_before.items():
        path = entry['path']
        guard_after[name] = sha256_file(path) if os.path.isfile(path) else None
    receipt['guard_after'] = {
        name: {'path': guard_before[name]['path'], 'sha256': digest}
        for name, digest in guard_after.items()}
    receipt['guard_unchanged'] = all(
        digest == guard_before[name]['sha256']
        for name, digest in guard_after.items())

    receipt_path = os.path.join(evidence_dir, 'H4053_run_receipt.json')
    with open(receipt_path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    return receipt


def cmd_run(args: argparse.Namespace) -> int:
    cards, _source, source_sha = _load_cards(args)
    if len(cards) > args.max_calls and not args.dry_run:
        # a resumed run may need fewer calls than cards; a fresh full run
        # cannot fit if nothing was ever spent
        done_keys = set()
        state_path = os.path.join(args.workdir, 'run_state.jsonl')
        if os.path.isfile(state_path):
            done_keys = {row['idempotency_key']
                         for row in load_jsonl(state_path)
                         if row.get('state') == model.CALL_SUCCEEDED}
        campaign_prefix = 'h4053-quarantine-sample30'
        fresh = [card for card in cards
                 if sha256_text('%s:%s:%s' % (
                     campaign_prefix, card.get('subcard'),
                     card.get('input_hash'))) not in done_keys]
        if len(fresh) > args.max_calls:
            sys.stderr.write(
                'run: %d cards still to spend exceed --max-calls %d\n'
                % (len(fresh), args.max_calls))
            return EXIT_STOP

    if args.provider == 'fake':
        adapter = providers.FakeAdapter()
    else:
        adapter = providers.adapter_for(args.provider)
    requested_model = args.model or getattr(
        adapter, 'default_model', 'fake-model')

    receipt = run_sample(
        cards, workdir=args.workdir, evidence_dir=args.evidence_dir,
        provider=args.provider, requested_model=requested_model,
        max_calls=args.max_calls, cost_ceiling_usd=args.cost_ceiling_usd,
        timeout_ms=args.timeout_ms,
        max_output_tokens=args.max_output_tokens,
        store_path=args.store, mirror_path=args.mirror,
        queue_path=args.queue, adapter=adapter, dry_run=args.dry_run)
    receipt['input_source_sha256'] = source_sha
    summary = {key: receipt[key] for key in (
        'schema', 'kind', 'dry_run', 'cards', 'calls_dispatched',
        'calls_succeeded', 'calls_failed', 'resumed_skipped', 'promotions',
        'store_mutations') if key in receipt}
    summary['guard_unchanged'] = receipt.get('guard_unchanged')
    print(json.dumps(summary, ensure_ascii=False))
    if receipt.get('packet_path'):
        print('packet -> %s' % receipt['packet_path'])
    if receipt['refusals']:
        for ref in receipt['refusals']:
            print('refusal: %s %s' % (ref['failure_class'], ref['detail']))
        return EXIT_STOP
    if not args.dry_run and not receipt['guard_unchanged']:
        sys.stderr.write('run: guard surface changed — refusing to end\n')
        return EXIT_STOP
    return EXIT_OK


# --- selftest -------------------------------------------------------------

def selftest() -> dict:
    """Six offline proofs against the fake provider. Zero network."""
    import tempfile

    results = {}

    class Crash:
        """FaultHook is Callable[[str], None]; fires once after N reservations."""

        def __init__(self, after_calls: int) -> None:
            self.seen = 0
            self.after_calls = after_calls

        def __call__(self, event: str) -> None:
            if event == faults.AFTER_RESERVATION:
                self.seen += 1
                if self.seen >= self.after_calls:
                    raise RuntimeError('simulated mid-run crash')

    def fresh_box(box: str) -> tuple[str, str, str]:
        workdir = os.path.join(box, 'work')
        evidence = os.path.join(box, 'evidence')
        store = os.path.join(box, 'store_fixture.jsonl')
        with open(store, 'w', encoding='utf-8') as handle:
            handle.write(json.dumps({'subcard': 'vid~~h0_zz_pw00',
                                     'ru': 'старый перевод'},
                                    ensure_ascii=False) + '\n')
        mirror = os.path.join(box, 'mirror_fixture.jsonl')
        queue = os.path.join(box, 'queue_fixture.jsonl')
        for path in (mirror, queue):
            with open(path, 'w', encoding='utf-8') as handle:
                handle.write('fixture\n')
        return workdir, evidence, store

    cards = [{'subcard': 'vid~~h0_zz_pw%02d' % index, 'key1': 'vid',
              'h': 'vid', 'sense_tag': '1',
              'reason': 'card sense-count changed',
              'input_hash': sha256_text('card-%d' % index),
              'review_class': UNMEASURED,
              'ru_quality_verdict': NOT_MEASURED}
             for index in range(6)]

    # 1. max-call reservation strictly before I/O.
    with tempfile.TemporaryDirectory() as box:
        workdir, evidence, store = fresh_box(box)
        adapter = providers.FakeAdapter()
        receipt = run_sample(
            cards, workdir=workdir, evidence_dir=evidence, provider='fake',
            requested_model='fake-model', max_calls=4, cost_ceiling_usd=4.0,
            timeout_ms=1000, max_output_tokens=256, store_path=store,
            adapter=adapter)
        assert adapter.calls == 4, adapter.calls
        assert len(receipt['refusals']) == 1, receipt['refusals']
        assert receipt['refusals'][0]['failure_class'] == \
            kernel.FAILURE_BUDGET
        results['reservation_before_io'] = {
            'provider_calls': adapter.calls, 'max_calls': 4,
            'refusal_class': receipt['refusals'][0]['failure_class']}

    # 2. resume without duplicate provider spend.
    with tempfile.TemporaryDirectory() as box:
        workdir, evidence, store = fresh_box(box)
        adapter = providers.FakeAdapter()
        hook = Crash(after_calls=3)
        try:
            run_sample(cards, workdir=workdir, evidence_dir=evidence,
                       provider='fake', requested_model='fake-model',
                       max_calls=6, cost_ceiling_usd=4.0, timeout_ms=1000,
                       max_output_tokens=256, store_path=store,
                       fault_hook=hook, adapter=adapter)
            raise AssertionError('crash hook did not fire')
        except RuntimeError as exc:
            assert 'crash' in str(exc)
        assert adapter.calls == 2  # card 3 never reached the provider
        ledger_path = os.path.join(workdir, 'call_reservations.json')
        adapter2 = providers.FakeAdapter()
        receipt = run_sample(cards, workdir=workdir, evidence_dir=evidence,
                             provider='fake', requested_model='fake-model',
                             max_calls=4, cost_ceiling_usd=4.0, timeout_ms=1000,
                             max_output_tokens=256, store_path=store,
                             adapter=adapter2)
        runs = json.load(open(ledger_path, encoding='utf-8'))['runs']
        spent_1, spent_2 = runs['h4053-quarantine-sample30']['calls_spent'], \
            runs['h4053-quarantine-sample30-r1']['calls_spent']
        packet = json.load(open(os.path.join(
            evidence, 'H4053_review_packet.json'), encoding='utf-8'))
        subcards = [row['subcard'] for row in packet['rows']]
        assert spent_1 == 3 and spent_2 == 4, (spent_1, spent_2)
        assert adapter2.calls == 4, adapter2.calls  # 4 dispatched, 2 skipped
        assert receipt['resumed_skipped'] == 2, receipt['resumed_skipped']
        assert len(subcards) == len(set(subcards)) == 6
        # no duplicate PROVIDER spend: 2 + 4 dispatches deliver 6 cards, each
        # translated exactly once; the interrupted slot stays forfeit.
        assert adapter.calls + adapter2.calls == 6
        results['resume_no_duplicate_spend'] = {
            'ledger_spent_after_crash': spent_1,
            'ledger_spent_after_resume': spent_2,
            'provider_dispatches_total': adapter.calls + adapter2.calls,
            'cards_delivered': len(set(subcards))}

    # 3. attribution + packet + 4. preserved input bytes / unchanged guards.
    with tempfile.TemporaryDirectory() as box:
        workdir, evidence, store = fresh_box(box)
        adapter = providers.FakeAdapter()
        receipt = run_sample(cards, workdir=workdir, evidence_dir=evidence,
                             provider='fake', requested_model='fake-model',
                             max_calls=6, cost_ceiling_usd=4.0, timeout_ms=1000,
                             max_output_tokens=256, store_path=store,
                             mirror_path=os.path.join(box,
                                                      'mirror_fixture.jsonl'),
                             queue_path=os.path.join(box,
                                                     'queue_fixture.jsonl'),
                             adapter=adapter)
        packet = json.load(open(receipt['packet_path'], encoding='utf-8'))
        row = packet['rows'][0]
        machine = row['machine']
        assert machine['call_id'] and machine['request_sha256'] \
            and machine['response_sha256'] and machine['usage'], machine
        assert row['old_ru'] == 'старый перевод', row['old_ru']
        assert row['candidate_ru'] and row['candidate_ru'].startswith('ru:')
        assert row['ru_quality_verdict'] == NOT_MEASURED
        assert receipt['guard_unchanged'] and receipt['promotions'] == 0 \
            and receipt['store_mutations'] == 0
        results['attribution'] = {'call_id_bound_rows': len(packet['rows']),
                                  'old_ru_join': row['old_ru_join']}
        results['input_preservation'] = {
            'guard_unchanged': receipt['guard_unchanged'],
            'surfaces': sorted(receipt['guard_before'])}

    # 5. dry run: zero provider calls, zero reservations.
    with tempfile.TemporaryDirectory() as box:
        workdir, evidence, store = fresh_box(box)
        adapter = providers.FakeAdapter()
        receipt = run_sample(cards, workdir=workdir, evidence_dir=evidence,
                             provider='fake', requested_model='fake-model',
                             max_calls=6, cost_ceiling_usd=4.0, timeout_ms=1000,
                             max_output_tokens=256, store_path=store,
                             adapter=adapter, dry_run=True)
        assert adapter.calls == 0 and not receipt['dry_run'] is None
        assert not os.path.isfile(os.path.join(
            workdir, 'call_reservations.json'))
        results['dry_run_zero_io'] = {'provider_calls': adapter.calls,
                                      'reservations': 0}

    # 6. no-promote negative control.
    with tempfile.TemporaryDirectory() as box:
        workdir, evidence, store = fresh_box(box)
        adapter = providers.FakeAdapter()
        receipt = run_sample(cards, workdir=workdir, evidence_dir=evidence,
                             provider='fake', requested_model='fake-model',
                             max_calls=6, cost_ceiling_usd=4.0, timeout_ms=1000,
                             max_output_tokens=256, store_path=store,
                             adapter=adapter)
        import sqlite3
        connection = sqlite3.connect(os.path.join(workdir, 'sample.sqlite'))
        promotable = connection.execute(
            'SELECT promotable FROM campaigns').fetchall()
        promotions = connection.execute(
            'SELECT COUNT(*) FROM promotions').fetchone()[0]
        connection.close()
        assert promotable == [(0,)], promotable
        assert promotions == 0
        source = open(os.path.abspath(__file__), encoding='utf-8').read()
        assert ('upsert_' 'promotion') not in source
        results['no_promote_capability'] = {
            'campaign_promotable_rows': promotable,
            'promotion_rows': promotions}

    return results


def cmd_selftest(_args: argparse.Namespace) -> int:
    started = time.time()
    results = selftest()
    for name, detail in results.items():
        print('PASS %s: %s' % (name, json.dumps(detail, ensure_ascii=False)))
    print('selftest 6/6 in %.1fs' % (time.time() - started))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='pwg_quarantine_sample30',
        description='H4053 report-only quarantine sample (never promotes)')
    sub = parser.add_subparsers(dest='command', required=True)

    freeze = sub.add_parser('freeze', help='freeze the nested 30-card packet')
    freeze.add_argument('--parent-sample', default=DEFAULT_PARENT_SAMPLE)
    freeze.add_argument('--fresh-quarantine', default=DEFAULT_FRESH_QUARANTINE)
    freeze.add_argument('--sense-audit', default=DEFAULT_SENSE_AUDIT)
    freeze.add_argument('--n', type=int, default=SAMPLE_N)
    freeze.add_argument('--seed', type=int, default=FREEZE_SEED)
    freeze.add_argument('--out', default=DEFAULT_FROZEN_PACKET)
    freeze.set_defaults(func=cmd_freeze)

    run = sub.add_parser('run', help='report-only translate run')
    run.add_argument('--frozen-packet', default='')
    run.add_argument('--keys-file', default='',
                     help='exact supplied key list (txt/jsonl)')
    run.add_argument('--provider', default='fake',
                     choices=['fake', 'glm', 'xai', 'deepseek'])
    run.add_argument('--model', default='')
    run.add_argument('--max-calls', type=int, required=True)
    run.add_argument('--cost-ceiling-usd', type=float, required=True)
    run.add_argument('--timeout-ms', type=int, default=120000)
    run.add_argument('--max-output-tokens', type=int, default=2048)
    run.add_argument('--workdir', required=True)
    run.add_argument('--evidence-dir', required=True)
    run.add_argument('--store', default=os.environ.get('PWG_RU_STORE', ''))
    run.add_argument('--mirror', default='')
    run.add_argument('--queue', default='')
    run.add_argument('--dry-run', action='store_true')
    run.set_defaults(func=cmd_run)

    selftest_parser = sub.add_parser(
        'selftest', help='six offline fake-provider proofs')
    selftest_parser.set_defaults(func=cmd_selftest)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main() or 0)
