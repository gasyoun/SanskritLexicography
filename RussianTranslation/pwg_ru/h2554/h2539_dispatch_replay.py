"""Replay H2539's two successful Agent dispatches without exposing content."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'src' / 'pilot'))

import gateway_attestation as att  # noqa: E402


DISPATCHES = {
    't1': 'tooluse_rPsnu7gf1HKhyNeOSzZY79',
    't2': 'toolu_01FkaoZN4NaJmmuAbjZD2iAZ',
}


def prompt_hash(ticket):
    return hashlib.sha256(ticket['request']['prompt'].encode('utf-8')).hexdigest()


def observed_dispatch_prompt(transcript, dispatch_id):
    matches = []
    for line in transcript.read_text(encoding='utf-8').splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = event.get('message') if isinstance(event, dict) else None
        blocks = message.get('content') if isinstance(message, dict) else None
        for block in blocks if isinstance(blocks, list) else []:
            if (isinstance(block, dict) and block.get('type') == 'tool_use'
                    and block.get('name') == 'Agent'
                    and block.get('id') == dispatch_id):
                matches.append((block.get('input') or {}).get('prompt'))
    if len(matches) != 1 or not isinstance(matches[0], str):
        raise RuntimeError('dispatch prompt is not unique: %s' % dispatch_id)
    return matches[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('transcript', type=Path)
    args = parser.parse_args()
    evidence = HERE.parent / 'h2539' / 'evidence'
    rows = []
    for name, dispatch_id in DISPATCHES.items():
        ticket = json.loads((evidence / ('%s_ticket.json' % name)).read_text(
            encoding='utf-8'))
        legacy = json.loads((evidence / ('%s_attestation.json' % name)).read_text(
            encoding='utf-8'))
        observed_prompt = observed_dispatch_prompt(args.transcript, dispatch_id)
        expected_prompt = ticket['request']['prompt']
        observed_hash = hashlib.sha256(
            observed_prompt.encode('utf-8')).hexdigest()
        exact = att.build_dispatch_attestation(
            transcript_path=str(args.transcript), dispatch_id=dispatch_id,
            run_id=ticket['run_id'], reservation_id=ticket['reservation_id'],
            requested_model=ticket['requested_model'],
            ticket_sha256=ticket['ticket_sha256'],
            request_prompt_sha256=observed_hash,
            started_at=legacy['started_at'], ended_at=legacy['ended_at'])
        legacy_scope = att.classify_legacy_attestation(legacy)
        rows.append({
            'ticket': name,
            'dispatch_id': dispatch_id,
            'dispatch_status': exact['dispatch_status'],
            'attested_model': exact['attested_model'],
            'model_matches_request': exact['model_matches_request'],
            'agent_id': exact['agent_id'],
            'is_sidechain': exact['is_sidechain'],
            'ticket_sha256': exact['ticket_sha256'],
            'request_prompt_sha256': exact['request_prompt_sha256'],
            'ticket_prompt_sha256': prompt_hash(ticket),
            'legacy_prompt_relation': (
                'exact' if observed_prompt == expected_prompt else
                'contained_not_exact' if expected_prompt in observed_prompt else
                'unbound'),
            'exact_attestation_sha256': exact['attestation_sha256'],
            'legacy_scope': legacy_scope['attestation_scope'],
            'legacy_dispatch_attested': legacy_scope['dispatch_attested'],
        })
    print(json.dumps({
        'schema': 'pwg.h2554_h2539_dispatch_replay.v1',
        'transcript_sha256': hashlib.sha256(
            args.transcript.read_bytes()).hexdigest(),
        'tickets': rows,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
