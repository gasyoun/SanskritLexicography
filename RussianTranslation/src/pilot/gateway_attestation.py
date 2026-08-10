"""Observed served-model + usage attestation for the router.cheap Agent bridge (H2537).

Why this module exists
----------------------
[`gateway_external.py`](gateway_external.py) seals a **public response wrapper**
that the operator hand-constructs around an interactive Agent-tool call.  Two of
its fields are load-bearing for qualification evidence:

* ``returned_model`` — the model that actually served the call, and
* ``usage`` — the token accounting behind any cost claim.

Neither is observable at the Agent-tool surface: that tool returns text only.  So
before H2537 both were *operator assertions* that the bridge then hash-sealed,
and ``record_external`` additionally forced ``returned_model`` to equal the
requested model (see ``_validate_response_binding``) while writing
``model_matches_request: True`` unconditionally.  The envelope schema pinned that
field to ``{"const": true}``, i.e. the artifact format could not express "the
router substituted a different model" even if it had been detected.  A sealed
envelope therefore *looked* like cryptographic proof of route/model binding while
its central claim was untested.

This module supplies the missing independent observation from a source the
harness itself writes: the local Claude Code session transcript
(``~/.claude/projects/<project-slug>/<session-uuid>.jsonl``).  Each assistant
event there carries ``message.model`` — the model string returned by the serving
endpoint — and a full ``message.usage`` block (input/output/cache tokens,
``service_tier``).  Subagent (Agent-tool) turns are flagged ``isSidechain: true``.

What this is and is not
-----------------------
*Is*: a second, independently-written record of what the endpoint reported,
produced by the harness rather than by the operator's prose.  It makes model
substitution and token usage **detectable**, and lets a cost claim rest on
counted tokens instead of an unknown-cost waiver.

*Is not*: cryptographic proof from the router.  ``message.model`` is the
endpoint's own claim as recorded by the client.  A dishonest or misconfigured
gateway could still report a model it did not run.  Attestation narrows the trust
boundary from "operator asserted it" to "the harness observed the endpoint assert
it"; it does not eliminate it.  Callers must not describe an attested envelope as
proof of physical model identity.

Deliberately absent: any HTTPS client, ``c4`` alias, Max fallback, alternative
model, or read of ``ANTHROPIC_AUTH_TOKEN``.  This module only reads local JSONL
that already exists on disk, and never writes to a transcript.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from gateway_route import canonical_json_bytes, sha256_bytes  # noqa: E402

ATTESTATION_SCHEMA = 'pwg.gateway_external_attestation.v2'
LEGACY_ATTESTATION_SCHEMA = 'pwg.gateway_external_attestation.v1'
DISPATCH_SCHEME = 'claude-agent-tool-use.v1'
DISPATCH_ID_RE = re.compile(r'^toolu(?:se)?_[A-Za-z0-9_-]{8,180}$')

#: ``message.model`` value the harness writes on locally-synthesised events
#: (API error notices, meta messages).  Never a served model.
SYNTHETIC_MODEL = '<synthetic>'


class AttestationError(RuntimeError):
    """Raised when a transcript cannot support a truthful attestation."""


def default_project_dir(cwd=None):
    """Return the Claude Code transcript directory for ``cwd``.

    The harness slugifies the absolute working directory by replacing each path
    separator and colon with ``-``.
    """
    target = os.path.abspath(cwd or os.getcwd())
    slug = target.replace(':', '-').replace(os.sep, '-').replace('/', '-')
    return os.path.join(
        os.path.expanduser('~'), '.claude', 'projects', slug)


def parse_utc(value, name):
    """Parse an ISO-8601 instant into an aware UTC datetime."""
    if not isinstance(value, str) or not value:
        raise AttestationError('%s is missing' % name)
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise AttestationError('%s is malformed: %s' % (name, value)) from exc
    if parsed.tzinfo is None:
        raise AttestationError('%s must carry a timezone' % name)
    return parsed.astimezone(dt.timezone.utc)


def _usage_public(usage):
    """Project a transcript usage block onto the fields we attest.

    Only counted token fields and the service tier are retained; nothing here is
    derived, inferred, or defaulted to zero when absent.
    """
    if not isinstance(usage, dict):
        return None
    fields = (
        'input_tokens',
        'output_tokens',
        'cache_creation_input_tokens',
        'cache_read_input_tokens',
        'service_tier',
    )
    out = {}
    for key in fields:
        if key in usage:
            out[key] = usage[key]
    return out or None


def _sum_tokens(turns, key):
    total = 0
    seen = False
    for turn in turns:
        usage = turn.get('usage') or {}
        value = usage.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        total += value
        seen = True
    return total if seen else None


def read_turns(transcript_path):
    """Yield every assistant turn in a transcript as a normalised dict.

    Unparseable lines are counted, never guessed at.  Locally-synthesised
    ``<synthetic>`` events are returned but flagged, so callers can exclude them
    from served-model reasoning without silently dropping evidence.
    """
    if not os.path.isfile(transcript_path):
        raise AttestationError('transcript not found: %s' % transcript_path)
    turns = []
    unparseable = 0
    with open(transcript_path, 'r', encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                unparseable += 1
                continue
            if not isinstance(event, dict) or event.get('type') != 'assistant':
                continue
            message = event.get('message')
            if not isinstance(message, dict):
                continue
            model = message.get('model')
            if not isinstance(model, str) or not model:
                continue
            turns.append({
                'uuid': event.get('uuid'),
                'timestamp': event.get('timestamp'),
                'model': model,
                'is_sidechain': bool(event.get('isSidechain')),
                'is_synthetic': model == SYNTHETIC_MODEL,
                'usage': _usage_public(message.get('usage')),
            })
    return turns, unparseable


def _content_blocks(event):
    message = event.get('message')
    content = message.get('content') if isinstance(message, dict) else None
    return content if isinstance(content, list) else []


def read_events(transcript_path):
    """Read transcript objects without projecting away dispatch identifiers."""
    if not os.path.isfile(transcript_path):
        raise AttestationError('transcript not found: %s' % transcript_path)
    events = []
    unparseable = 0
    with open(transcript_path, 'r', encoding='utf-8') as handle:
        for lineno, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                unparseable += 1
                continue
            if isinstance(event, dict):
                events.append((lineno, event))
    return events, unparseable


def _dispatch_prompt_sha256(prompt):
    if not isinstance(prompt, str) or not prompt:
        raise AttestationError('Agent tool_use prompt is missing')
    return sha256_bytes(prompt.encode('utf-8'))


def _normalise_result_usage(usage):
    public = _usage_public(usage)
    return public or None


def build_dispatch_attestation(*, transcript_path, dispatch_id, run_id,
                               reservation_id, requested_model,
                               ticket_sha256, request_prompt_sha256,
                               started_at=None, ended_at=None):
    """Bind one ticket to exactly one completed Agent tool dispatch.

    Identity comes from the harness relation itself: one Agent ``tool_use.id``
    and one ``tool_result.tool_use_id``.  Served model and usage come only from
    that result event's ``toolUseResult`` record; adjacent turns are irrelevant.
    """
    if not isinstance(dispatch_id, str) or not DISPATCH_ID_RE.fullmatch(dispatch_id):
        raise AttestationError('dispatch_id is malformed')
    if not isinstance(ticket_sha256, str) or not re.fullmatch(
            r'[0-9a-f]{64}', ticket_sha256):
        raise AttestationError('ticket_sha256 is malformed')
    if not isinstance(request_prompt_sha256, str) or not re.fullmatch(
            r'[0-9a-f]{64}', request_prompt_sha256):
        raise AttestationError('request_prompt_sha256 is malformed')
    if started_at is not None:
        parse_utc(started_at, 'started_at')
    if ended_at is not None:
        parse_utc(ended_at, 'ended_at')
    if started_at is not None and ended_at is not None and (
            parse_utc(ended_at, 'ended_at') < parse_utc(started_at, 'started_at')):
        raise AttestationError('ended_at precedes started_at')

    events, unparseable = read_events(transcript_path)
    if unparseable:
        raise AttestationError(
            'transcript has %d unparseable line(s); exact dispatch uniqueness '
            'cannot be proved' % unparseable)
    uses = []
    results = []
    for lineno, event in events:
        for block in _content_blocks(event):
            if not isinstance(block, dict):
                continue
            if (block.get('type') == 'tool_use'
                    and block.get('name') == 'Agent'
                    and block.get('id') == dispatch_id):
                uses.append((lineno, event, block))
            if (block.get('type') == 'tool_result'
                    and block.get('tool_use_id') == dispatch_id):
                results.append((lineno, event, block))
    if len(uses) != 1:
        raise AttestationError(
            'dispatch_id must identify exactly one Agent tool_use; found %d'
            % len(uses))
    if len(results) != 1:
        raise AttestationError(
            'dispatch_id must identify exactly one tool_result; found %d'
            % len(results))

    use_line, use_event, use_block = uses[0]
    result_line, result_event, result_block = results[0]
    prompt = (use_block.get('input') or {}).get('prompt')
    observed_prompt_sha256 = _dispatch_prompt_sha256(prompt)
    if observed_prompt_sha256 != request_prompt_sha256:
        raise AttestationError('Agent tool_use prompt does not match ticket request')
    if result_block.get('is_error') is True:
        raise AttestationError('Agent tool_result is an error/refusal')
    if result_event.get('sourceToolAssistantUUID') != use_event.get('uuid'):
        raise AttestationError('tool_result source does not match tool_use event')
    detail = result_event.get('toolUseResult')
    if not isinstance(detail, dict):
        raise AttestationError('tool_result lacks structured toolUseResult evidence')
    if detail.get('status') != 'completed':
        raise AttestationError('Agent dispatch is not completed')
    model = detail.get('resolvedModel')
    agent_id = detail.get('agentId')
    if not isinstance(model, str) or not model:
        raise AttestationError('completed Agent result lacks resolvedModel')
    if not isinstance(agent_id, str) or not agent_id:
        raise AttestationError('completed Agent result lacks agentId')

    record = {
        'schema': ATTESTATION_SCHEMA,
        'attestation_scope': 'dispatch',
        'dispatch_scheme': DISPATCH_SCHEME,
        'dispatch_id': dispatch_id,
        'ticket_sha256': ticket_sha256,
        'request_prompt_sha256': request_prompt_sha256,
        'transcript_sha256': sha256_bytes(open(transcript_path, 'rb').read()),
        'transcript_basename': os.path.basename(transcript_path),
        'run_id': run_id,
        'reservation_id': reservation_id,
        'requested_model': requested_model,
        'started_at': started_at,
        'ended_at': ended_at,
        'tool_use_line': use_line,
        'tool_result_line': result_line,
        'tool_use_event_uuid': use_event.get('uuid'),
        'tool_result_event_uuid': result_event.get('uuid'),
        'is_sidechain': bool(use_event.get('isSidechain')),
        'agent_id': agent_id,
        'dispatch_status': detail['status'],
        'attested_model': model,
        'model_matches_request': model == requested_model,
        'usage_totals': _normalise_result_usage(detail.get('usage')),
        'unparseable_lines': 0,
    }
    record['attestation_sha256'] = sha256_bytes(canonical_json_bytes(record))
    return record


def classify_legacy_attestation(record):
    """Truthfully label H2539 v1 evidence without upgrading its scope."""
    if not isinstance(record, dict) or record.get('schema') != LEGACY_ATTESTATION_SCHEMA:
        raise AttestationError('not a legacy v1 attestation')
    return {
        'schema': LEGACY_ATTESTATION_SCHEMA,
        'attestation_scope': 'legacy_window',
        'dispatch_attested': False,
        'promotable': False,
        'run_id': record.get('run_id'),
        'reservation_id': record.get('reservation_id'),
        'model_matches_request': record.get('model_matches_request'),
    }


def select_window(turns, started_at, ended_at, sidechain_only=True):
    """Return served turns whose timestamp falls inside the closed window."""
    start = parse_utc(started_at, 'started_at')
    end = parse_utc(ended_at, 'ended_at')
    if end < start:
        raise AttestationError('ended_at precedes started_at')
    selected = []
    for turn in turns:
        if turn['is_synthetic']:
            continue
        if sidechain_only and not turn['is_sidechain']:
            continue
        stamp = turn.get('timestamp')
        if not isinstance(stamp, str):
            continue
        try:
            when = parse_utc(stamp, 'turn timestamp')
        except AttestationError:
            continue
        if start <= when <= end:
            selected.append(turn)
    return selected


def build_window_attestation_legacy(*, transcript_path, started_at, ended_at,
                                    run_id, reservation_id, requested_model,
                                    sidechain_only=True):
    """Build a canonical, hashable attestation record for one Agent call.

    ``models_observed`` holds every distinct served-model string seen in the
    window.  A single unanimous value yields ``attested_model``; anything else
    leaves it ``None`` with ``ambiguous`` set, because guessing which turn served
    the ticketed call would re-introduce exactly the assumption this module
    exists to remove.
    """
    turns, unparseable = read_turns(transcript_path)
    window = select_window(turns, started_at, ended_at,
                           sidechain_only=sidechain_only)
    models = sorted({turn['model'] for turn in window})
    attested_model = models[0] if len(models) == 1 else None
    usage_present = [t for t in window if t.get('usage')]
    record = {
        'schema': LEGACY_ATTESTATION_SCHEMA,
        'transcript_sha256': sha256_bytes(
            open(transcript_path, 'rb').read()),
        'transcript_basename': os.path.basename(transcript_path),
        'run_id': run_id,
        'reservation_id': reservation_id,
        'requested_model': requested_model,
        'started_at': started_at,
        'ended_at': ended_at,
        'sidechain_only': bool(sidechain_only),
        'turns_in_window': len(window),
        'turns_with_usage': len(usage_present),
        'unparseable_lines': unparseable,
        'models_observed': models,
        'attested_model': attested_model,
        'ambiguous': attested_model is None,
        'model_matches_request': (
            None if attested_model is None
            else attested_model == requested_model),
        'usage_totals': {
            'input_tokens': _sum_tokens(window, 'input_tokens'),
            'output_tokens': _sum_tokens(window, 'output_tokens'),
            'cache_creation_input_tokens': _sum_tokens(
                window, 'cache_creation_input_tokens'),
            'cache_read_input_tokens': _sum_tokens(
                window, 'cache_read_input_tokens'),
        },
        'turns': window,
    }
    record['attestation_sha256'] = sha256_bytes(canonical_json_bytes(record))
    return record


def build_attestation(**kwargs):
    """Compatibility name for the v2 exact-dispatch builder."""
    return build_dispatch_attestation(**kwargs)


def _parser():
    parser = argparse.ArgumentParser(
        description='Attest served model + usage for one Agent call from the '
                    'local harness transcript (read-only).')
    parser.add_argument('--transcript', help='path to the session .jsonl')
    parser.add_argument('--project-dir',
                        help='transcript directory (defaults to the slug of cwd)')
    parser.add_argument('--session-id', help='session uuid, selects <uuid>.jsonl')
    parser.add_argument('--dispatch-id', required=True)
    parser.add_argument('--ticket', required=True,
                        help='immutable gateway ticket JSON')
    parser.add_argument('--started-at')
    parser.add_argument('--ended-at')
    parser.add_argument('--out', required=True, help='attestation json path')
    return parser


def resolve_transcript(args):
    if args.transcript:
        return args.transcript
    project_dir = args.project_dir or default_project_dir()
    if not args.session_id:
        raise AttestationError(
            'provide --transcript, or --session-id to resolve within %s'
            % project_dir)
    return os.path.join(project_dir, '%s.jsonl' % args.session_id)


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        transcript = resolve_transcript(args)
        with open(args.ticket, 'r', encoding='utf-8') as handle:
            ticket = json.load(handle)
        binding = ticket.get('dispatch_binding') or {}
        record = build_dispatch_attestation(
            transcript_path=transcript,
            dispatch_id=args.dispatch_id,
            started_at=args.started_at,
            ended_at=args.ended_at,
            run_id=ticket.get('run_id'),
            reservation_id=ticket.get('reservation_id'),
            requested_model=ticket.get('requested_model'),
            ticket_sha256=ticket.get('ticket_sha256'),
            request_prompt_sha256=binding.get('request_prompt_sha256'),
        )
    except AttestationError as exc:
        sys.stderr.write('attestation refused: %s\n' % exc)
        return 2
    with open(args.out, 'wb') as handle:
        handle.write(canonical_json_bytes(record))
    print('attestation written: %s' % args.out)
    print('  dispatch_id=%s status=%s attested_model=%s'
          % (record['dispatch_id'], record['dispatch_status'],
             record['attested_model']))
    print('  model_matches_request=%s attestation_sha256=%s'
          % (record['model_matches_request'], record['attestation_sha256']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
