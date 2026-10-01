"""H4057 — GLM 5.3 Flash route qualification replay (offline, zero provider calls).

Replays representative PWG card classes and the kernel's failure paths through
the H4057 ``glm-flash`` adapter seam, and seals a qualification report plus the
bounded 30-card live qualification manifest builder.

Everything here is offline: the wire adapter is stubbed at ``invoke`` with
canned GLM-shaped responses, no credential is read or required, and no Claude
CLI or other executor is invoked.

Usage::

    python tools/h4057_glm_route_qualification.py replay \
        --report reports/H4057_glm_route_qualification.json
    python tools/h4057_glm_route_qualification.py build-manifest \
        --cards cards.jsonl --count 30 --out reports/H4057_glm_live_manifest.json

``build-manifest`` fails closed when the card list is missing: the canonical
``pwg_ru`` store is local-only (gitignored), so the sealed manifest is built on
the machine that holds the store, at the start of the authorized live run.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, 'src')
for _path in (SRC, os.path.join(SRC, 'pilot')):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import call_reservation  # noqa: E402  (hardened reservation ledger, reused)
from pwg_pipeline import evidence, kernel, model, providers  # noqa: E402
from pwg_pipeline.repository import open_repository, utc_now  # noqa: E402

SCHEMA = 'pwg.qualification.glm.v1'
MANIFEST_SCHEMA = 'pwg.qualification.manifest.v1'
REQUESTED_MODEL = providers.GLM_DEFAULT_MODEL

# --- representative PWG card classes (handoff work item 3) -------------------

CARD_CASES: list[dict] = [
    {
        'case': 'pure_gloss',
        'fragment_id': 'agni',
        'fragment_class': 'gloss',
        'source_string': '1. Glanz, Glühen; Feuer. 2. Opfer, Anrufung.',
        'context': 'PWG h-Nachtrag, Kurzschluss',
    },
    {
        'case': 'sanskrit_markup',
        'fragment_id': 'agnísikhā',
        'fragment_class': 'card',
        'source_string': 'f. Feuerflamme {#agni#}-Comp. {#śikhā#}',
        'context': 'keep {#...#} devanagari fences verbatim',
    },
    {
        'case': 'apparatus',
        'fragment_id': 'akṣara.1',
        'fragment_class': 'card',
        'source_string': 'n. Silbe; unzerstörbar. <ls>RV 1, 12, 3</ls>; '
                         'Nachtr. 2: auch unsterblich.',
        'context': 'keep <ls>...</ls> and render Nachtr. patch',
    },
    {
        'case': 'homonyms',
        'fragment_id': 'bhū',
        'fragment_class': 'card',
        'source_string': '1. (bhávati) sein, entstehen. 2. (bhauti) '
                         'das Seiende; 3. Bhū, Erde.',
        'context': 'preserve printed homonym numbering 1./2./3.',
    },
    {
        'case': 'long_card',
        'fragment_id': 'go',
        'fragment_class': 'card',
        'source_string': 'f. Kuh; Rind; Strahl; Sprache; Erde. '
                         + '; '.join('Sinn %d: Belegstelle %d' % (i, i)
                                     for i in range(1, 25)),
        'context': 'multi-sense long card, order-preserving',
    },
]


def glm_response(payload: dict, *, served_model: str | None = REQUESTED_MODEL,
                 usage: dict | None = None) -> providers.ProviderResponse:
    """A canned GLM-shaped raw reply (OpenAI wire: choices + usage)."""
    return providers.ProviderResponse(
        raw_text=json.dumps(payload, ensure_ascii=False, sort_keys=True),
        served_model=served_model,
        raw_usage=dict(usage) if usage is not None
        else {'prompt_tokens': 312, 'completion_tokens': 88,
              'total_tokens': 400})


class StubGlmAdapter(providers.GlmFlashAdapter):
    """The GLM seam with ``invoke`` stubbed: zero network, zero credential."""

    def __init__(self, response: providers.ProviderResponse | None = None,
                 raises: BaseException | None = None) -> None:
        self._response = response
        self._raises = raises
        self.dispatched: list[providers.ProviderRequest] = []

    def invoke(self, request: providers.ProviderRequest
               ) -> providers.ProviderResponse:
        self.dispatched.append(request)
        if self._raises is not None:
            raise self._raises
        assert self._response is not None
        return self._response


def ok_payload(case: dict) -> dict:
    return {'fragments': [{
        'fragment_id': case['fragment_id'],
        'target_string': 'RU<%s>' % case['source_string'],
    }]}


# --- adapter-level replays ---------------------------------------------------

def replay_card_cases() -> list[dict]:
    """Pure gloss, Sanskrit markup, apparatus, homonyms, long card."""
    receipts = []
    for case in CARD_CASES:
        adapter = StubGlmAdapter(glm_response(ok_payload(case)))
        request = adapter.prepare_request(
            [case], requested_model=REQUESTED_MODEL,
            max_output_tokens=kernel.DEFAULT_MAX_OUTPUT_TOKENS,
            timeout_ms=kernel.DEFAULT_TIMEOUT_MS)
        response = adapter.invoke(request)
        parsed = adapter.parse_result(response)
        usage = adapter.normalize_usage(response)
        target = parsed['fragments'][0]['target_string']
        receipts.append({
            'schema': SCHEMA, 'case': case['case'],
            'route': adapter.route,
            'requested_model': request.requested_model,
            'served_model': response.served_model,
            'request_sha256': request.sha256,
            'response_sha256': response.sha256,
            'source_sha256': evidence.canonical_sha256(case['source_string']),
            'markup_verbatim': case['source_string'] in target,
            'token_usage_evaluable': usage['cost_evaluable'],
            'token_counts': {'input': usage['input_tokens'],
                             'output': usage['output_tokens']},
            'cost_basis': usage['cost_basis'],
            'dispatches': len(adapter.dispatched),
        })
    return receipts


def replay_malformed_result() -> dict:
    """A prose-wrapped non-JSON reply must raise, not guess."""
    adapter = StubGlmAdapter(glm_response(
        {'fragments': [{'fragment_id': 'x'}]},
        served_model=REQUESTED_MODEL))
    request = adapter.prepare_request(
        [CARD_CASES[0]], requested_model=REQUESTED_MODEL,
        max_output_tokens=256, timeout_ms=1000)
    response = providers.ProviderResponse(
        raw_text='Sure! Here is your translation. Hope this helps!',
        served_model=REQUESTED_MODEL,
        raw_usage={'prompt_tokens': 10, 'completion_tokens': 5})
    try:
        adapter.parse_result(response)
        refused = False
        detail = ''
    except providers.ProviderError as exc:
        refused = True
        detail = str(exc)
    return {'schema': SCHEMA, 'case': 'malformed_result',
            'refused': refused, 'detail': detail,
            'request_sha256': request.sha256}


def replay_missing_usage() -> dict:
    """Token-less usage is unevaluable cost -- and never guessed to zero."""
    adapter = StubGlmAdapter(glm_response(ok_payload(CARD_CASES[0]), usage={}))
    request = adapter.prepare_request(
        [CARD_CASES[0]], requested_model=REQUESTED_MODEL,
        max_output_tokens=256, timeout_ms=1000)
    response = adapter.invoke(request)
    usage = adapter.normalize_usage(response)
    return {'schema': SCHEMA, 'case': 'missing_usage',
            'cost_evaluable': usage['cost_evaluable'],
            'cost_basis': usage['cost_basis'],
            'request_sha256': request.sha256,
            'response_sha256': response.sha256}


def replay_unknown_cost_fails_closed() -> dict:
    """No price card: worst-case estimate refuses; cost never borrowed."""
    try:
        providers.estimate_cost_usd(model.ROUTE_GLM, input_tokens=1000,
                                    max_output_tokens=2048)
        refused, detail = False, ''
    except providers.ProviderError as exc:
        refused, detail = True, str(exc)
    borrowed = {
        route: (route in providers.PRICE_PER_MTOK_USD)
        for route in (model.ROUTE_GLM, model.ROUTE_XAI, model.ROUTE_DEEPSEEK)
    }
    return {'schema': SCHEMA, 'case': 'unknown_cost_fails_closed',
            'estimate_refused': refused, 'detail': detail,
            'price_card_present': borrowed,
            'claude_price_borrowed': False}


# --- kernel-level scenarios over the real ledger -----------------------------

SYNTHETIC_PRICE_CARD = {'input': 1.0, 'output': 1.0}
# Qualification-only synthetic card (never a real-world price, never borrowed
# from another provider). ``assert_budget`` always bounds a campaign in
# dollars, so exercising the kernel's reservation/receipt mechanics for GLM
# offline needs *some* card; the sealed receipts below are stamped
# ``price_card: synthetic-qualification-only`` so no one can misread them as
# observed economics. The real z.ai card is a live-run prerequisite.


def _with_synthetic_price_card(scenario):
    def wrapped(workdir: str) -> dict:
        saved = providers.PRICE_PER_MTOK_USD.get(model.ROUTE_GLM)
        providers.PRICE_PER_MTOK_USD[model.ROUTE_GLM] = SYNTHETIC_PRICE_CARD
        try:
            result = scenario(workdir)
        finally:
            if saved is None:
                providers.PRICE_PER_MTOK_USD.pop(model.ROUTE_GLM, None)
            else:
                providers.PRICE_PER_MTOK_USD[model.ROUTE_GLM] = saved
        result['price_card'] = 'synthetic-qualification-only'
        return result
    return wrapped


def _scenario_env(workdir: str, name: str, *, max_calls: int = 4,
                  cost_ceiling_usd: float = 4.0):
    repository = open_repository(os.path.join(workdir, '%s.sqlite' % name))
    campaign_id = 'h4057-%s' % name
    repository.create_campaign(model.Campaign(
        campaign_id=campaign_id, scope='h4057-glm-qualification', language='ru',
        route=model.ROUTE_GLM, max_calls=max_calls,
        cost_ceiling_usd=cost_ceiling_usd, promotable=False,
        created_by='tools/h4057_glm_route_qualification.py'))
    ledger_path = os.path.join(workdir, '%s_reservations.json' % name)
    paid = kernel.PaidCallKernel(
        repository, campaign_id=campaign_id,
        evidence_dir=os.path.join(workdir, 'evidence', name),
        ledger_path=ledger_path)
    ledger = call_reservation.CallReservationLedger(
        ledger_path, campaign_id, max_calls=max_calls)
    job_id = '%s.job' % campaign_id
    repository.add_job(model.Job(
        job_id=job_id, campaign_id=campaign_id, kind='fragment',
        source_identity=CARD_CASES[0]['fragment_id'],
        source_hash=evidence.canonical_sha256(CARD_CASES[0]['source_string'])))
    repository.transition_job(job_id, model.PLANNED, model.PREPARED)
    repository.transition_job(job_id, model.PREPARED, model.RESERVED)
    repository.transition_job(job_id, model.RESERVED, model.RUNNING)
    return repository, paid, ledger, job_id, campaign_id


def _one_call(paid: kernel.PaidCallKernel, repository, adapter, ledger,
              job_id: str, ordinal: int) -> dict:
    outcome = paid.execute(
        adapter, job_ids=[job_id], job_payloads=[CARD_CASES[0]],
        requested_model=REQUESTED_MODEL,
        idempotency_key='h4057:%s:%d' % (job_id, ordinal),
        timeout_ms=kernel.DEFAULT_TIMEOUT_MS, max_output_tokens=256,
        estimated_input_tokens=200)
    repository.transition_job(job_id, model.RUNNING, model.CAPTURED)
    repository.transition_job(job_id, model.CAPTURED, model.AUDITED)
    return {'state': outcome.state, 'route': outcome.route,
            'requested_model': outcome.requested_model,
            'served_model': outcome.served_model,
            'failure_class': outcome.failure_class,
            'usage': outcome.usage,
            'request_sha256': outcome.request_sha256,
            'response_sha256': outcome.response_sha256,
            'ledger_spent_calls': ledger.spent(),
            'artifacts': sorted(outcome.artifacts)}


@_with_synthetic_price_card
def scenario_success(workdir: str) -> dict:
    repository, paid, ledger, job_id, campaign_id = _scenario_env(
        workdir, 'success')
    try:
        adapter = StubGlmAdapter(glm_response(ok_payload(CARD_CASES[0])))
        result = _one_call(paid, repository, adapter, ledger, job_id, 1)
        result.update({
            'schema': SCHEMA, 'scenario': 'success',
            'case': 'pure_gloss',
            'reservation_finalized_once':
                result['ledger_spent_calls'] == 1,
            'receipts_sealed': result['artifacts'],
        })
        return result
    finally:
        repository.close()


@_with_synthetic_price_card
def scenario_malformed(workdir: str) -> dict:
    repository, paid, ledger, job_id, campaign_id = _scenario_env(
        workdir, 'malformed')
    try:
        adapter = StubGlmAdapter(providers.ProviderResponse(
            raw_text='<html>gateway timeout page</html>',
            served_model=REQUESTED_MODEL,
            raw_usage={'prompt_tokens': 10, 'completion_tokens': 0}))
        result = _one_call(paid, repository, adapter, ledger, job_id, 1)
        result.update({
            'schema': SCHEMA, 'scenario': 'malformed_result',
            'call_state': result['state'],
            'ledger_spent_calls': result['ledger_spent_calls'],
        })
        return result
    finally:
        repository.close()


@_with_synthetic_price_card
def scenario_missing_usage(workdir: str) -> dict:
    repository, paid, ledger, job_id, campaign_id = _scenario_env(
        workdir, 'missing_usage')
    try:
        adapter = StubGlmAdapter(glm_response(ok_payload(CARD_CASES[0]),
                                              usage={}))
        raised, failure_class = '', None
        try:
            _one_call(paid, repository, adapter, ledger, job_id, 1)
        except kernel.GlobalStop as exc:
            raised, failure_class = str(exc), exc.failure_class
        return {'schema': SCHEMA, 'scenario': 'missing_usage',
                'global_stop_raised': bool(raised),
                'failure_class': failure_class,
                'detail': raised,
                'ledger_spent_calls': ledger.spent()}
    finally:
        repository.close()


@_with_synthetic_price_card
def scenario_route_substitution(workdir: str) -> dict:
    repository, paid, ledger, job_id, campaign_id = _scenario_env(
        workdir, 'route_substitution')
    try:
        adapter = StubGlmAdapter(glm_response(
            ok_payload(CARD_CASES[0]),
            served_model='glm-5.3-flash-turbo',
            usage={'prompt_tokens': 10, 'completion_tokens': 5}))
        raised, failure_class = '', None
        try:
            _one_call(paid, repository, adapter, ledger, job_id, 1)
        except kernel.GlobalStop as exc:
            raised, failure_class = str(exc), exc.failure_class
        return {'schema': SCHEMA, 'scenario': 'route_substitution',
                'global_stop_raised': bool(raised),
                'failure_class': failure_class,
                'detail': raised,
                'ledger_spent_calls': ledger.spent()}
    finally:
        repository.close()


def scenario_dollar_bound_refuses(workdir: str) -> dict:
    """A dollar-capped GLM campaign refuses BEFORE any reservation or I/O.

    Deliberately NOT decorated with the synthetic price card: this proves the
    real (card-less) state of the repository.
    """
    repository, paid, ledger, job_id, campaign_id = _scenario_env(
        workdir, 'dollar_bound', cost_ceiling_usd=4.0)
    try:
        adapter = StubGlmAdapter(glm_response(ok_payload(CARD_CASES[0])))
        raised, failure_class = '', None
        try:
            _one_call(paid, repository, adapter, ledger, job_id, 1)
        except kernel.KernelRefusal as exc:
            raised, failure_class = str(exc), exc.failure_class
        return {'schema': SCHEMA, 'scenario': 'dollar_bound_refuses',
                'refused': bool(raised),
                'failure_class': failure_class,
                'detail': raised,
                'dispatches': len(adapter.dispatched),
                'reservations_consumed': ledger.spent()}
    finally:
        repository.close()


# --- sealed 30-card manifest builder -----------------------------------------

def build_manifest(cards_path: str, out_path: str, count: int,
                   purpose: str) -> dict:
    """Deterministically select and seal ``count`` card identities.

    Input JSONL rows carry the exact dispatch payload fields
    (``fragment_id``, ``fragment_class``, ``source_string``, ``context``).
    Selection is stride-based over the sha256-ordered card list, so the same
    input always yields the same manifest. The output file is sealed with
    ``pwg.pipeline.evidence.seal`` and records its own card hashes.
    """
    if not os.path.exists(cards_path):
        raise SystemExit(
            'build-manifest: card list %s not found. The canonical pwg_ru'
            ' store is local-only; export the qualification cards on the'
            ' machine that holds the store, then seal here.' % cards_path)
    cards = []
    with open(cards_path, encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if line:
                cards.append(json.loads(line))
    if len(cards) < count:
        raise SystemExit('build-manifest: %d cards < %d requested'
                         % (len(cards), count))
    ordered = sorted(cards, key=lambda c: evidence.canonical_sha256(c))
    stride = len(ordered) / float(count)
    picked = [ordered[min(len(ordered) - 1, int(i * stride))]
              for i in range(count)]
    manifest = {
        'schema': MANIFEST_SCHEMA,
        'purpose': purpose,
        'route': model.ROUTE_GLM,
        'requested_model': REQUESTED_MODEL,
        'resolved_identity': {
            'opencode_default_model': 'zai-coding-plan/glm-5.3-flash',
            'wire_model_id': REQUESTED_MODEL,
            'source': '~/.config/opencode/opencode.jsonc (05-09-2026)',
        },
        'selection_rule': 'stride over sha256-ordered cards, seedless',
        'count': count,
        'input_cards': len(cards),
        'cards': [
            {'ordinal': i + 1,
             'fragment_id': c.get('fragment_id'),
             'fragment_class': c.get('fragment_class'),
             'source_sha256': evidence.canonical_sha256(
                 c.get('source_string') or ''),
             'payload_sha256': evidence.canonical_sha256(c)}
            for i, c in enumerate(picked)],
        'created_by': 'tools/h4057_glm_route_qualification.py',
        'reuse_of': 'quarantine sample cards may be substituted 1:1 by'
                    ' payload_sha256 before sealing; substitutions are'
                    ' recorded in the live run report',
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    receipt = evidence.seal(out_path, manifest)
    return {'manifest': manifest, 'receipt': receipt}


# --- main ---------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)

    p_replay = sub.add_parser('replay', help='run the offline replay suite')
    p_replay.add_argument('--report', default=os.path.join(
        ROOT, 'reports', 'H4057_glm_route_qualification.json'))

    p_manifest = sub.add_parser('build-manifest',
                                help='seal a bounded card manifest')
    p_manifest.add_argument('--cards', required=True)
    p_manifest.add_argument('--out', required=True)
    p_manifest.add_argument('--count', type=int, default=30)
    p_manifest.add_argument('--purpose', default='H4057 GLM live qualification')

    args = parser.parse_args(argv)

    if args.command == 'build-manifest':
        built = build_manifest(args.cards, args.out, args.count, args.purpose)
        print(json.dumps({'sealed': built['receipt']['path'],
                          'sha256': built['receipt']['sha256'],
                          'count': built['manifest']['count']},
                         ensure_ascii=False))
        return 0

    receipts: dict = {}
    with tempfile.TemporaryDirectory(prefix='h4057-qual-') as workdir:
        receipts['adapter_replays'] = replay_card_cases()
        receipts['malformed_result'] = replay_malformed_result()
        receipts['missing_usage'] = replay_missing_usage()
        receipts['unknown_cost_fails_closed'] = \
            replay_unknown_cost_fails_closed()
        receipts['kernel_scenarios'] = [
            scenario_success(workdir),
            scenario_malformed(workdir),
            scenario_missing_usage(workdir),
            scenario_route_substitution(workdir),
            scenario_dollar_bound_refuses(workdir),
        ]

    report = {
        'schema': SCHEMA,
        'generated_utc': utc_now(),
        'resolved_identity': {
            'opencode_default_model': 'zai-coding-plan/glm-5.3-flash',
            'wire_model_id': REQUESTED_MODEL,
            'route': model.ROUTE_GLM,
            'base_url': providers.GLM_BASE_URL,
            'key_env': providers.GLM_KEY_ENV,
            'identity_source': 'OpenCode configuration metadata,'
                               ' ~/.config/opencode/opencode.jsonc'
                               ' default model (05-09-2026)',
        },
        'executor': 'OxAlpha (opencode/z-ai/glm-5.3-flash)',
        'claude_cli_invocations': 0,
        'provider_calls': 0,
        'canonical_store_touched': False,
        'price_card': {
            'glm_flash': None,
            'policy': 'unknown cost stays unknown; a dollar-bounded campaign'
                      ' fails closed; no Claude/xAI/DeepSeek price is borrowed',
        },
        'gates': {
            'model_route_validity': 'separate gate - live canary still fenced'
                                    ' to xai/deepseek by its ruling',
            'mechanical_fidelity': 'this replay report',
            'independent_semantic_quality': 'not attempted here; requires the'
                                            ' authorized live run + independent'
                                            ' review',
        },
        'replays': receipts,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
    receipt = evidence.seal(args.report, report)
    passed = (
        all(r['markup_verbatim'] for r in receipts['adapter_replays'])
        and receipts['malformed_result']['refused']
        and not receipts['missing_usage']['cost_evaluable']
        and receipts['unknown_cost_fails_closed']['estimate_refused']
        and receipts['unknown_cost_fails_closed']['price_card_present'][
            model.ROUTE_GLM] is False
        and receipts['kernel_scenarios'][0]['state'] == model.CALL_SUCCEEDED
        and receipts['kernel_scenarios'][1]['state'] == model.CALL_MALFORMED
        and receipts['kernel_scenarios'][2]['failure_class']
        == kernel.FAILURE_UNEVALUABLE
        and receipts['kernel_scenarios'][3]['failure_class']
        == kernel.FAILURE_ROUTE
        and receipts['kernel_scenarios'][4]['refused']
        and receipts['kernel_scenarios'][4]['dispatches'] == 0
        and receipts['kernel_scenarios'][4]['reservations_consumed'] == 0
    )
    print(json.dumps({
        'sealed': receipt['path'], 'sha256': receipt['sha256'],
        'verdict': 'QUALIFIED_OFFLINE' if passed else 'FAILED',
    }, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
