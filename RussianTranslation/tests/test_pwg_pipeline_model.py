"""H3714 Wave 1 — domain model and legal transitions (implementation step 1.4).

Pins transition refusal and entity invariants before anything persists them.
"""
import os
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from pwg_pipeline import faults, model  # noqa: E402
from pwg_pipeline import validation  # noqa: E402

CLEAN_SHA = 'a' * 64


def test_every_job_state_is_reachable_from_planned():
    reachable = model.reachable_job_states(model.PLANNED)
    assert reachable == set(model.JOB_STATES)


def test_transition_graph_names_only_known_states():
    for state, following in model.JOB_TRANSITIONS.items():
        assert state in model.JOB_STATES
        for target in following:
            assert target in model.JOB_STATES


def test_terminal_job_states_have_no_forward_move():
    assert model.JOB_TRANSITIONS[model.COMPLETE] == frozenset()
    assert model.JOB_TRANSITIONS[model.FAILED] == frozenset()


def test_illegal_job_transition_is_refused():
    model.assert_job_transition(model.PLANNED, model.PREPARED)
    with pytest.raises(model.TransitionError):
        model.assert_job_transition(model.PLANNED, model.COMPLETE)
    with pytest.raises(model.TransitionError):
        model.assert_job_transition(model.COMPLETE, model.PLANNED)
    with pytest.raises(model.TransitionError):
        model.assert_job_transition('invented', model.PLANNED)


def test_promotion_path_is_forward_only():
    order = model.PROMOTION_STATES
    for current, following in zip(order, order[1:]):
        model.assert_job_transition(current, following)
    with pytest.raises(model.TransitionError):
        model.assert_job_transition(model.STORE_COMMITTED, model.APPLY_PREPARED)


def test_call_transitions_end_terminally():
    model.assert_call_transition(model.CALL_RESERVED, model.CALL_DISPATCHED)
    model.assert_call_transition(model.CALL_DISPATCHED, model.CALL_TIMED_OUT)
    for terminal in model.CALL_TERMINAL_STATES:
        assert model.CALL_TRANSITIONS[terminal] == frozenset()
    with pytest.raises(model.TransitionError):
        model.assert_call_transition(model.CALL_SUCCEEDED, model.CALL_DISPATCHED)


def test_a_call_cannot_exist_without_a_reservation():
    with pytest.raises(model.ModelError):
        model.Call(call_id='c', attempt_id='a', route=model.ROUTE_XAI,
                   requested_model='grok-4.6', reservation_id='',
                   idempotency_key='k')


def test_a_call_requires_an_idempotency_key():
    with pytest.raises(model.ModelError):
        model.Call(call_id='c', attempt_id='a', route=model.ROUTE_XAI,
                   requested_model='grok-4.6', reservation_id='r',
                   idempotency_key='')


def test_negative_accounting_is_refused_at_the_domain_edge():
    with pytest.raises(model.ModelError):
        model.Call(call_id='c', attempt_id='a', route=model.ROUTE_XAI,
                   requested_model='m', reservation_id='r',
                   idempotency_key='k', observed_cost_usd=-0.01)
    with pytest.raises(model.ModelError):
        model.Campaign(campaign_id='c', scope='s', language='ru',
                       route=model.ROUTE_XAI, max_calls=-1,
                       cost_ceiling_usd=1.0, promotable=False, created_by='t')


def test_job_cannot_be_its_own_parent():
    with pytest.raises(model.ModelError):
        model.Job(job_id='j1', campaign_id='c', kind='card',
                  source_identity='x', source_hash=CLEAN_SHA,
                  parent_job_id='j1')


def test_hashes_must_be_lowercase_sha256():
    with pytest.raises(model.ModelError):
        model.Artifact(artifact_id='a', campaign_id='c', kind='result',
                       path='p', sha256='NOTAHASH')
    with pytest.raises(model.ModelError):
        model.Artifact(artifact_id='a', campaign_id='c', kind='result',
                       path='p', sha256=CLEAN_SHA.upper())


def test_unknown_route_or_kind_is_refused():
    with pytest.raises(model.ModelError):
        model.Campaign(campaign_id='c', scope='s', language='ru',
                       route='openrouter-someday', max_calls=1,
                       cost_ceiling_usd=1.0, promotable=False, created_by='t')
    with pytest.raises(model.ModelError):
        model.Job(job_id='j', campaign_id='c', kind='paragraph',
                  source_identity='x', source_hash=CLEAN_SHA)


def test_only_the_two_paid_routes_are_billable():
    assert model.BILLABLE_ROUTES == frozenset(
        {model.ROUTE_XAI, model.ROUTE_DEEPSEEK})
    assert model.ROUTE_CLAUDE_SHADOW not in model.BILLABLE_ROUTES
    assert model.ROUTE_DETERMINISTIC not in model.BILLABLE_ROUTES


def test_fault_points_cover_every_named_irreversible_boundary():
    # The verification document names these boundaries; the contract is that
    # none may be silently dropped from the code.
    assert faults.FAULT_POINTS == (
        'after_reservation', 'after_provider_response', 'after_usage_capture',
        'after_artifact_seal', 'after_verdict_commit',
        'after_apply_intent_commit', 'after_store_backup', 'after_store_commit',
        'after_derived_rebuild', 'after_journal_advance',
        'before_campaign_commit')
    with pytest.raises(ValueError):
        faults.require_point('after_lunch')


def test_validator_version_is_pinned():
    assert validation.VALIDATOR_VERSION == 'pwg_pipeline.validation.v1'
