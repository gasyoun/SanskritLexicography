"""The operator facade (H3714 Wave 1, implementation step 7.1).

``init`` ``import`` ``plan`` ``execute`` ``audit`` ``apply`` ``review``
``promote`` ``replay`` ``shadow-sync`` ``validate`` ``canary``

This is the only supported operator entry point (R1.2).  Legacy CLIs keep
working through the shims described in [`compat.py`](compat.py) and print a
deprecation notice; they do not gain new capability.

The ``canary`` command is the one paid surface, and it is fenced hard: at most
one xAI plus one DeepSeek request, ``max_calls=2``, USD 4 total, no retry, a
non-promotable scratch-only campaign, and no canonical-path access.  An
unavailable provider stops its own track and its unused call is never consumed
as a retry by the other one.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Sequence

if __package__ in (None, ''):  # pragma: no cover - direct-script invocation
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'pwg_pipeline'

from . import audit as audit_module  # noqa: E402
from . import apply as apply_module  # noqa: E402
from . import (compat, import_legacy, kernel, model, promotion,  # noqa: E402
               providers, replay as replay_module, review as review_module,
               validation)
from .evidence import seal, sha256_text, tree_digest  # noqa: E402
from .repository import open_repository  # noqa: E402

SCHEMA = 'pwg.pipeline.cli.v1'

CANARY_MAX_CALLS = 2
CANARY_COST_CEILING_USD = 4.0
CANARY_PROVIDERS: tuple[str, ...] = ('xai', 'deepseek')
CANARY_PROMPT = {
    'fragment_id': 'canary-1',
    'fragment_class': 'definition_gloss',
    'source_string': 'Feuer, Gott des Feuers',
    'context': None,
}

EXIT_OK = 0
EXIT_REFUSED = 2
EXIT_STOP = 3


def _emit(value: Any) -> None:
    sys.stdout.write(json.dumps(value, ensure_ascii=False, indent=2,
                                sort_keys=True) + '\n')


def _database(args: argparse.Namespace) -> str:
    return os.path.abspath(args.database)


def cmd_init(args: argparse.Namespace) -> int:
    repository = open_repository(_database(args))
    try:
        campaign = model.Campaign(
            campaign_id=args.campaign, scope=args.scope, language=args.language,
            route=args.route, max_calls=args.max_calls,
            cost_ceiling_usd=args.cost_ceiling_usd,
            promotable=bool(args.promotable), created_by=args.created_by)
        repository.create_campaign(campaign)
        _emit({'schema': SCHEMA, 'command': 'init',
               'campaign_id': campaign.campaign_id,
               'schema_version': repository.schema_version(),
               'promotable': campaign.promotable,
               'max_calls': campaign.max_calls,
               'cost_ceiling_usd': campaign.cost_ceiling_usd})
    finally:
        repository.close()
    return EXIT_OK


def cmd_import(args: argparse.Namespace) -> int:
    repository = open_repository(_database(args))
    try:
        mapping: dict[str, list[str]] = {}
        for entry in args.source or []:
            kind, _, path = entry.partition('=')
            if not path:
                sys.stderr.write('--source needs <kind>=<path>\n')
                return EXIT_REFUSED
            mapping.setdefault(kind, []).append(path)
        report = import_legacy.import_tree(repository, mapping,
                                           campaign_id=args.campaign)
        _emit(report)
    finally:
        repository.close()
    return EXIT_OK


def cmd_plan(args: argparse.Namespace) -> int:
    repository = open_repository(_database(args))
    try:
        planned = repository.jobs_in_state(args.campaign, model.PLANNED)
        _emit({'schema': SCHEMA, 'command': 'plan',
               'campaign_id': args.campaign, 'planned_jobs': planned,
               'count': len(planned)})
    finally:
        repository.close()
    return EXIT_OK


def cmd_execute(args: argparse.Namespace) -> int:
    sys.stderr.write(
        'execute: Wave 1 routes live execution through `canary` (fenced) or a'
        ' frozen `replay`; unfenced production execution stays on the legacy'
        ' lane until the cutover gate passes.\n')
    return EXIT_REFUSED


def cmd_audit(args: argparse.Namespace) -> int:
    repository = open_repository(_database(args))
    try:
        before = tree_digest(args.evidence_dir) if os.path.isdir(
            args.evidence_dir) else None
        verdicts = []
        for job_id in repository.jobs_in_state(args.campaign, model.CAPTURED):
            verdicts.append(job_id)
        after = tree_digest(args.evidence_dir) if before is not None else None
        _emit({'schema': SCHEMA, 'command': 'audit',
               'campaign_id': args.campaign,
               'auditable_jobs': verdicts,
               'evidence_tree_unchanged': before == after,
               'audit_version': audit_module.AUDIT_VERSION})
    finally:
        repository.close()
    return EXIT_OK


def cmd_apply(args: argparse.Namespace) -> int:
    repository = open_repository(_database(args))
    try:
        intents = repository.intents(args.campaign)
        _emit({'schema': SCHEMA, 'command': 'apply', 'intent': args.intent,
               'recorded_intents': [
                   {'job_id': row['job_id'], 'intent': row['intent'],
                    'applied': bool(row['applied_at'])} for row in intents],
               'legal_intents': {key: sorted(value) for key, value
                                 in apply_module.LEGAL_INTENTS.items()}})
    finally:
        repository.close()
    return EXIT_OK


def cmd_promote(args: argparse.Namespace) -> int:
    repository = open_repository(_database(args))
    try:
        open_rows = repository.open_promotions(args.campaign)
        _emit({'schema': SCHEMA, 'command': 'promote',
               'open_promotions': open_rows,
               'authority': 'coordinator journal only',
               'canonical_fence': list(promotion.CANONICAL_FENCE)})
    finally:
        repository.close()
    return EXIT_OK


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        report = validation.validate_jsonl(
            args.canonical, require_provenance=not args.no_provenance,
            require_schema=args.require_schema)
    except validation.ValidationError as exc:
        sys.stderr.write('validate: %s\n' % exc)
        return EXIT_STOP
    fence = validation.fence_report(report)
    if args.out:
        seal(args.out, {'report': {k: v for k, v in report.items()
                                   if k != 'rows_detail'},
                        'fence': fence,
                        'rows_detail': report['rows_detail']})
    _emit(fence if args.fence_existing else
          {k: v for k, v in report.items() if k != 'rows_detail'})
    return EXIT_OK


def cmd_replay(args: argparse.Namespace) -> int:
    try:
        report = replay_module.replay_matrix(args.matrix, exact=args.exact)
    except replay_module.ReplayMismatch as exc:
        sys.stderr.write('replay: %s\n' % exc)
        return EXIT_STOP
    _emit(report)
    return EXIT_OK if report['exact'] else EXIT_STOP


def cmd_shadow_sync(args: argparse.Namespace) -> int:
    repository = open_repository(_database(args))
    try:
        mismatches = repository.shadow_mismatches(args.route)
        _emit({'schema': SCHEMA, 'command': 'shadow-sync', 'route': args.route,
               'compare_only': True, 'execution_authority': False,
               'promotion_authority': False,
               'unexplained_mismatches': len(mismatches),
               'mismatch_keys': [row['legacy_key'] for row in mismatches]})
        return EXIT_OK if not mismatches else EXIT_STOP
    finally:
        repository.close()


def cmd_review(args: argparse.Namespace) -> int:
    if args.review_command == 'verify':
        try:
            _emit(review_module.verify(args.packet, args.receipt))
        except review_module.ReviewRefusal as exc:
            sys.stderr.write('review verify: %s\n' % exc)
            return EXIT_REFUSED
        return EXIT_OK
    _emit({'schema': SCHEMA, 'command': 'review',
           'required_sections': list(review_module.REQUIRED_SECTIONS),
           'schema_summary': review_module.schema_summary()})
    return EXIT_OK


def cmd_compat(args: argparse.Namespace) -> int:
    _emit(compat.coverage())
    return EXIT_OK


def cmd_canary(args: argparse.Namespace) -> int:
    """The one paid surface. Two calls, USD 4, no retry, nothing promotable."""
    names = [name.strip() for name in args.providers.split(',') if name.strip()]
    unknown = [name for name in names if name not in CANARY_PROVIDERS]
    if unknown:
        sys.stderr.write('canary: unknown provider(s): %s\n' % ', '.join(unknown))
        return EXIT_REFUSED
    if args.max_calls > CANARY_MAX_CALLS:
        sys.stderr.write('canary: --max-calls may not exceed %d\n'
                         % CANARY_MAX_CALLS)
        return EXIT_REFUSED
    if args.cost_ceiling_usd > CANARY_COST_CEILING_USD:
        sys.stderr.write('canary: --cost-ceiling-usd may not exceed %.2f\n'
                         % CANARY_COST_CEILING_USD)
        return EXIT_REFUSED
    if len(names) > args.max_calls:
        sys.stderr.write('canary: %d providers do not fit in --max-calls %d\n'
                         % (len(names), args.max_calls))
        return EXIT_REFUSED
    if args.promotable:
        sys.stderr.write('canary: a Wave-1 canary is never promotable\n')
        return EXIT_REFUSED

    workdir = os.path.abspath(args.workdir)
    os.makedirs(workdir, exist_ok=True)
    repository = open_repository(os.path.join(workdir, 'canary.sqlite'))
    envelopes: list[dict[str, Any]] = []
    stopped: list[dict[str, Any]] = []
    try:
        for name in names:
            adapter = providers.adapter_for(name)
            campaign_id = 'canary-%s' % name
            # One campaign per provider, each with exactly one call: an
            # unavailable provider can never release its slot to the other.
            repository.create_campaign(model.Campaign(
                campaign_id=campaign_id, scope='wave1-canary', language='ru',
                route=adapter.route, max_calls=1,
                cost_ceiling_usd=args.cost_ceiling_usd / max(len(names), 1),
                promotable=False, created_by='pwg_pipeline.cli.canary'))
            job_id = '%s.job' % campaign_id
            repository.add_job(model.Job(
                job_id=job_id, campaign_id=campaign_id, kind='fragment',
                source_identity=CANARY_PROMPT['fragment_id'],
                source_hash=sha256_text(CANARY_PROMPT['source_string'])))
            paid = kernel.PaidCallKernel(
                repository, campaign_id=campaign_id,
                evidence_dir=os.path.join(workdir, 'evidence', name),
                ledger_path=os.path.join(workdir, 'call_reservations.json'))
            repository.transition_job(job_id, model.PLANNED, model.PREPARED)
            repository.transition_job(job_id, model.PREPARED, model.RESERVED)
            repository.transition_job(job_id, model.RESERVED, model.RUNNING)
            try:
                outcome = paid.execute(
                    adapter, job_ids=[job_id], job_payloads=[CANARY_PROMPT],
                    requested_model=(args.model or adapter.default_model),
                    idempotency_key='%s:canary:1' % campaign_id,
                    timeout_ms=args.timeout_ms,
                    max_output_tokens=args.max_output_tokens,
                    estimated_input_tokens=200)
            except kernel.GlobalStop as exc:
                stopped.append({'provider': name, 'class': 'global_stop',
                                'detail': str(exc)})
                continue
            except kernel.KernelRefusal as exc:
                stopped.append({'provider': name, 'class': exc.failure_class,
                                'detail': str(exc)})
                continue
            envelope = {
                'provider': name,
                'route': outcome.route,
                'requested_model': outcome.requested_model,
                'served_model': outcome.served_model,
                'state': outcome.state,
                'usage': outcome.usage,
                'failure_class': outcome.failure_class,
                'request_sha256': outcome.request_sha256,
                'response_sha256': outcome.response_sha256,
                'promotable': False,
                'retries': 0,
            }
            if outcome.failure_class == kernel.FAILURE_UNAVAILABLE:
                stopped.append({'provider': name, 'class': 'unavailable',
                                'detail': 'adapter track stopped; its unused'
                                          ' call is not released to any other'
                                          ' provider'})
            envelopes.append(envelope)
            seal(os.path.join(workdir, 'envelope.%s.json' % name), envelope)

        total_cost = sum(float(env['usage'].get('observed_cost_usd') or 0.0)
                         for env in envelopes)
        billed = [env for env in envelopes
                  if env['state'] == model.CALL_SUCCEEDED]
        report = {
            'schema': 'pwg.pipeline.canary.v1',
            'providers_requested': names,
            'max_calls': args.max_calls,
            'cost_ceiling_usd': args.cost_ceiling_usd,
            'calls_made': len(envelopes),
            'successful_calls': len(billed),
            'observed_cost_usd': round(total_cost, 6),
            'within_ceiling': total_cost <= args.cost_ceiling_usd + 1e-9,
            'promotions': 0,
            'retries': 0,
            'stopped_tracks': stopped,
            'envelopes': envelopes,
            'verdict': ('GO' if billed and len(billed) == len(names)
                        and total_cost <= args.cost_ceiling_usd + 1e-9
                        else 'INCONCLUSIVE' if not billed else 'PARTIAL'),
        }
        seal(os.path.join(workdir, 'canary_report.json'), report)
        _emit(report)
        return EXIT_OK if report['verdict'] == 'GO' else EXIT_STOP
    finally:
        repository.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='pwg_pipeline',
        description='PWG translation control plane (H3714 Wave 1 facade)')
    parser.add_argument('--database', default='pwg_pipeline.sqlite',
                        help='campaign database path')
    sub = parser.add_subparsers(dest='command', required=True)

    init = sub.add_parser('init', help='create a campaign')
    init.add_argument('--campaign', required=True)
    init.add_argument('--scope', default='pwg-tm')
    init.add_argument('--language', default='ru')
    init.add_argument('--route', default=model.ROUTE_XAI, choices=model.ROUTES)
    init.add_argument('--max-calls', type=int, default=0)
    init.add_argument('--cost-ceiling-usd', type=float, default=0.0)
    init.add_argument('--promotable', action='store_true')
    init.add_argument('--created-by', default='operator')
    init.set_defaults(func=cmd_init)

    importer = sub.add_parser('import', help='import legacy state as evidence')
    importer.add_argument('--campaign')
    importer.add_argument('--source', action='append',
                          help='<source_kind>=<path>, repeatable')
    importer.set_defaults(func=cmd_import)

    plan = sub.add_parser('plan', help='list planned jobs')
    plan.add_argument('--campaign', required=True)
    plan.set_defaults(func=cmd_plan)

    execute = sub.add_parser('execute', help='(fenced in Wave 1)')
    execute.add_argument('--campaign')
    execute.set_defaults(func=cmd_execute)

    audit_parser = sub.add_parser('audit', help='pure verdict computation')
    audit_parser.add_argument('--campaign', required=True)
    audit_parser.add_argument('--evidence-dir', default='evidence')
    audit_parser.set_defaults(func=cmd_audit)

    apply_parser = sub.add_parser('apply', help='explicit effects')
    apply_parser.add_argument('--campaign', required=True)
    apply_parser.add_argument('--intent', choices=model.APPLY_INTENTS)
    apply_parser.set_defaults(func=cmd_apply)

    promote = sub.add_parser('promote', help='journaled promotion state')
    promote.add_argument('--campaign', required=True)
    promote.set_defaults(func=cmd_promote)

    validate = sub.add_parser('validate', help='recursive read-only validation')
    validate.add_argument('--canonical', required=True)
    validate.add_argument('--recursive', action='store_true',
                          help='accepted for symmetry; validation is always'
                               ' recursive')
    validate.add_argument('--read-only', action='store_true',
                          help='accepted for symmetry; never mutates')
    validate.add_argument('--fence-existing', action='store_true')
    validate.add_argument('--require-schema', action='store_true')
    validate.add_argument('--no-provenance', action='store_true')
    validate.add_argument('--out')
    validate.set_defaults(func=cmd_validate)

    replay = sub.add_parser('replay', help='exact frozen-campaign replay')
    replay.add_argument('--matrix', required=True)
    replay.add_argument('--exact', action='store_true', default=True)
    replay.set_defaults(func=cmd_replay)

    shadow = sub.add_parser('shadow-sync', help='compare only, never execute')
    shadow.add_argument('--route', default=model.ROUTE_CLAUDE_SHADOW,
                        choices=model.ROUTES)
    shadow.add_argument('--compare-only', action='store_true', default=True)
    shadow.set_defaults(func=cmd_shadow_sync)

    review = sub.add_parser('review', help='independent review packet/receipt')
    review.add_argument('review_command', nargs='?', default='describe',
                        choices=('describe', 'verify'))
    review.add_argument('--packet')
    review.add_argument('--receipt')
    review.set_defaults(func=cmd_review)

    compat_parser = sub.add_parser('compat', help='legacy shim coverage')
    compat_parser.set_defaults(func=cmd_compat)

    canary = sub.add_parser('canary', help='bounded non-promotable canary')
    canary.add_argument('--providers', default=','.join(CANARY_PROVIDERS))
    canary.add_argument('--max-calls', type=int, default=CANARY_MAX_CALLS)
    canary.add_argument('--cost-ceiling-usd', type=float,
                        default=CANARY_COST_CEILING_USD)
    canary.add_argument('--no-retry', action='store_true', default=True,
                        help='accepted for symmetry; Wave 1 never retries')
    canary.add_argument('--non-promotable', action='store_true', default=True)
    canary.add_argument('--promotable', action='store_true')
    canary.add_argument('--model', default=None)
    canary.add_argument('--timeout-ms', type=int, default=60000)
    canary.add_argument('--max-output-tokens', type=int, default=256)
    canary.add_argument('--workdir', default='canary_out')
    canary.set_defaults(func=cmd_canary)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        # A captured in-process stream (tests, embedding) has no reconfigure.
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return int(args.func(args))


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
