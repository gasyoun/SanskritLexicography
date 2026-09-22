#!/usr/bin/env python
"""H4531 bounded Anthropic Message Batches probe over one real PWG root.

Four phases, each resumable, each leaving a durable artifact -- so a 24 h async window
never depends on one session staying alive:

    build    manifest -> N one-card pwg.transport_request.v1 objects (free, offline)
    submit   reserve the hard ceiling in pwg.call_reservation.v1, THEN submit one batch
    collect  poll; when the batch has ended, retrieve and seal one envelope per request
    report   cost/latency table + gate verdict over the sealed envelopes

Cost discipline: ``--max-calls`` is the ledger ceiling and it is written before the first
submit, so an over-large request list is refused rather than billed. The probe is
synthetic and non-promotable by construction (``route_transport.build_request`` pins
``provenance_class=synthetic_control`` / ``promotable=false``), which is the
``--stop-before-promote`` discipline expressed in the artifact rather than in a flag.

Usage (from RussianTranslation/):

    python src/pilot/h4531_batches_probe.py build  --manifest pwg_ru/h4531/execution_manifest.h4531.json --out-dir pwg_ru/h4531/run
    python src/pilot/h4531_batches_probe.py submit --out-dir pwg_ru/h4531/run --max-calls 24
    python src/pilot/h4531_batches_probe.py collect --out-dir pwg_ru/h4531/run
    python src/pilot/h4531_batches_probe.py report --out-dir pwg_ru/h4531/run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import anthropic_batches_route as abr  # noqa: E402
import headless_worker as hw  # noqa: E402
from call_reservation import CallReservationLedger  # noqa: E402
from execution_contract import PRODUCTION_HARD_TIMEOUT_MS  # noqa: E402
from route_transport import (  # noqa: E402
    TransportRefusal,
    atomic_json,
    build_request,
    candidate_pass,
    file_sha256,
    read_json,
    verify_envelope,
)


MAX_OUTPUT_TOKENS = 4096
PURPOSE = 'h4531_batches_probe:one_card'
RUN_ID = 'h4531-batches-probe'


def paths(out_dir):
    root = os.path.abspath(out_dir)
    return {
        'root': root,
        'requests': os.path.join(root, 'transport_requests.json'),
        'ledger': os.path.join(root, 'call_reservation.json'),
        'receipt': os.path.join(root, 'batches_submission.json'),
        'poll_log': os.path.join(root, 'poll_log.jsonl'),
        'envelopes': os.path.join(root, 'envelopes'),
        'report': os.path.join(root, 'probe_report.json'),
    }


# --------------------------------------------------------------------------- build
def build_requests(manifest_path, model=abr.MODEL, limit=None):
    """One transport request per manifest batch, refusing any multi-card batch."""
    manifest = read_json(manifest_path, 'probe manifest')
    manifest_sha = file_sha256(manifest_path)
    schema = manifest.get('output_schema')
    batches = manifest.get('batches') or []
    requests = []
    for batch in batches:
        if len(batch) != 1:
            raise TransportRefusal(
                'H2152-rejected shape: batch %r carries %d cards; this probe is one card '
                'per batch REQUEST' % (batch, len(batch)))
        key = batch[0]
        prompt = hw.build_prompt(manifest, [key])
        request = build_request(
            prompt=prompt, output_schema=schema, requested_model=model,
            purpose='%s:%s' % (PURPOSE, key), manifest_sha256=manifest_sha,
            hard_timeout_ms=PRODUCTION_HARD_TIMEOUT_MS,
            max_output_tokens=MAX_OUTPUT_TOKENS)
        requests.append({'key': key, 'request': request})
        if limit and len(requests) >= limit:
            break
    return manifest, requests


def cmd_build(args):
    spot = paths(args.out_dir)
    os.makedirs(spot['root'], exist_ok=True)
    manifest, rows = build_requests(args.manifest, model=args.model, limit=args.limit)
    bundle = {
        'schema': 'pwg.batches_probe_requests.v1',
        'manifest_path': os.path.relpath(os.path.abspath(args.manifest)).replace('\\', '/'),
        'manifest_sha256': file_sha256(args.manifest),
        'manifest_schema': manifest.get('schema'),
        'root': (manifest.get('meta') or {}).get('root') or args.root,
        'requested_model': args.model,
        'card_count': len(rows),
        'prompt_bytes_total': sum(len(row['request']['prompt']) for row in rows),
        'rows': rows,
    }
    atomic_json(spot['requests'], bundle)
    print('built %d one-card requests (%d prompt bytes total) -> %s'
          % (len(rows), bundle['prompt_bytes_total'], spot['requests']))
    print('manifest_sha256: %s' % bundle['manifest_sha256'])
    return 0


def _load_requests(spot):
    bundle = read_json(spot['requests'], 'probe request bundle')
    return bundle, [row['request'] for row in bundle['rows']]


def _call(spot, max_calls=None):
    if max_calls is None:
        ledger = CallReservationLedger.open_existing(spot['ledger'], RUN_ID)
    else:
        ledger = CallReservationLedger(spot['ledger'], RUN_ID, max_calls=max_calls)
    client, _ = abr.api_client()
    note = abr.credential_note()
    if client is None:
        raise TransportRefusal('no Anthropic credential: %s' % note)
    print('credential: %s' % note)
    return abr.AnthropicBatchesCall(ledger, abr.sdk_transport(client)), ledger


# -------------------------------------------------------------------------- submit
def cmd_submit(args):
    spot = paths(args.out_dir)
    bundle, requests = _load_requests(spot)
    if args.max_calls < len(requests):
        raise TransportRefusal(
            'ceiling %d is below the %d requests in the bundle; raise the ceiling '
            'deliberately or build fewer cards' % (args.max_calls, len(requests)))
    call, ledger = _call(spot, max_calls=args.max_calls)
    receipt = call.submit(requests, spot['receipt'], model=bundle['requested_model'])
    print('batch submitted: requests=%d status=%s ceiling=%d spent=%d'
          % (receipt['request_count'], receipt['processing_status'],
             args.max_calls, ledger.spent()))
    print('batch_id recorded in %s (redacted from stdout on purpose)' % spot['receipt'])
    return 0


# ------------------------------------------------------------------------- collect
def cmd_collect(args):
    spot = paths(args.out_dir)
    bundle, requests = _load_requests(spot)
    call, _ = _call(spot)
    receipt = read_json(spot['receipt'], 'batches submission receipt')
    os.makedirs(spot['envelopes'], exist_ok=True)
    deadline = time.time() + args.wait_seconds
    status = call.poll(receipt)
    while not status['ended'] and time.time() < deadline:
        with open(spot['poll_log'], 'a', encoding='utf-8', newline='\n') as handle:
            handle.write(json.dumps({'epoch': time.time(), **status},
                                    ensure_ascii=False, sort_keys=True) + '\n')
        print('status=%s counts=%s' % (status['processing_status'], status['request_counts']))
        time.sleep(args.poll_seconds)
        status = call.poll(receipt)
    with open(spot['poll_log'], 'a', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps({'epoch': time.time(), **status},
                                ensure_ascii=False, sort_keys=True) + '\n')
    if not status['ended']:
        print('NOT ENDED after %ds: status=%s counts=%s -- rerun collect later'
              % (args.wait_seconds, status['processing_status'], status['request_counts']))
        return 3
    wall_ms = int((time.time() - receipt['submitted_epoch']) * 1000)
    envelopes = call.retrieve(requests, receipt, spot['envelopes'], wall_ms=wall_ms)
    print('retrieved %d envelopes; batch wall_ms=%d' % (len(envelopes), wall_ms))
    return 0


# -------------------------------------------------------------------------- report
def summarise(spot):
    bundle = read_json(spot['requests'], 'probe request bundle')
    receipt = read_json(spot['receipt'], 'batches submission receipt')
    rows = []
    for ordinal, custom_id in enumerate(receipt['custom_ids'], start=1):
        path = os.path.join(spot['envelopes'], '%s.envelope.json' % custom_id)
        if not os.path.isfile(path):
            continue
        envelope = verify_envelope(read_json(path, 'batches envelope'))
        usage = envelope.get('usage') or {}
        rows.append({
            'ordinal': ordinal,
            'key': bundle['rows'][ordinal - 1]['key'],
            'input_tokens': usage.get('input_tokens'),
            'output_tokens': usage.get('output_tokens'),
            'observed_cost_usd': envelope.get('observed_cost_usd'),
            'list_equivalent_usd': (envelope.get('accounting') or {}).get('list_equivalent_usd'),
            'schema_compliant': envelope.get('schema_compliant'),
            'audit_passed': envelope.get('audit_passed'),
            'audit_reasons': envelope.get('audit_reasons'),
            'failure_class': envelope.get('failure_class'),
            'candidate_pass': candidate_pass(envelope),
        })
    priced = [row for row in rows if isinstance(row['observed_cost_usd'], (int, float))]
    wall_ms = None
    if os.path.isfile(spot['poll_log']):
        with open(spot['poll_log'], encoding='utf-8') as handle:
            lines = [json.loads(line) for line in handle if line.strip()]
        ended = [line for line in lines if line.get('ended')]
        if ended:
            wall_ms = int((ended[0]['epoch'] - receipt['submitted_epoch']) * 1000)
    return {
        'schema': 'pwg.batches_probe_report.v1',
        'run_id': RUN_ID,
        'root': bundle['root'],
        'requested_model': bundle['requested_model'],
        'pricing_basis': abr.PRICING_BASIS,
        'manifest_sha256': bundle['manifest_sha256'],
        'batch_id_sha256_prefix': None if not receipt.get('batch_id') else
            __import__('hashlib').sha256(receipt['batch_id'].encode()).hexdigest()[:16],
        'request_count': receipt['request_count'],
        'envelope_count': len(rows),
        'batch_wall_ms': wall_ms,
        'cards_passing_gates': sum(1 for row in rows if row['candidate_pass']),
        'cards_failing_gates': sum(1 for row in rows if not row['candidate_pass']),
        'failure_classes': sorted({row['failure_class'] for row in rows
                                   if row['failure_class']}),
        'total_input_tokens': sum(row['input_tokens'] or 0 for row in rows),
        'total_output_tokens': sum(row['output_tokens'] or 0 for row in rows),
        'total_observed_cost_usd': round(sum(row['observed_cost_usd'] for row in priced), 6)
            if priced else None,
        'total_list_equivalent_usd': round(
            sum(row['list_equivalent_usd'] or 0 for row in priced), 6) if priced else None,
        'cost_evaluable_cards': len(priced),
        'rows': rows,
    }


def cmd_report(args):
    spot = paths(args.out_dir)
    report = summarise(spot)
    atomic_json(spot['report'], report)
    print(json.dumps({key: value for key, value in report.items() if key != 'rows'},
                     ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    common = dict(required=True)
    b = sub.add_parser('build')
    b.add_argument('--manifest', **common)
    b.add_argument('--out-dir', **common)
    b.add_argument('--model', default=abr.MODEL)
    b.add_argument('--root', default='d_a')
    b.add_argument('--limit', type=int, default=None)
    b.set_defaults(func=cmd_build)
    s = sub.add_parser('submit')
    s.add_argument('--out-dir', **common)
    s.add_argument('--max-calls', type=int, required=True)
    s.set_defaults(func=cmd_submit)
    c = sub.add_parser('collect')
    c.add_argument('--out-dir', **common)
    c.add_argument('--wait-seconds', type=int, default=600)
    c.add_argument('--poll-seconds', type=int, default=20)
    c.set_defaults(func=cmd_collect)
    r = sub.add_parser('report')
    r.add_argument('--out-dir', **common)
    r.set_defaults(func=cmd_report)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())
