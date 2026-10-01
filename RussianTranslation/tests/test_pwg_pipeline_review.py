"""H3714 Wave 1 — independent review and the cutover verdict (V12).

The receipt has to be hash-bound and signed by somebody other than the
implementer, and an unsigned wave must report ``PARTIAL`` rather than quietly
claiming ``GO``.
"""
import os
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from pwg_pipeline import faults, review, wave1_evidence  # noqa: E402
from pwg_pipeline.evidence import seal  # noqa: E402

SECTIONS = {name: {'present': True} for name in review.REQUIRED_SECTIONS
            if name != 'schema_summary'}


def make_packet(commit='abc123', implementer='implementer'):
    return review.build_packet(commit=commit, implementer=implementer,
                               replay_report=SECTIONS['replay'],
                               fault_matrix=SECTIONS['fault_matrix'],
                               validation_fence=SECTIONS['validation_fence'],
                               shadow=SECTIONS['shadow'],
                               canary=SECTIONS['canary'],
                               shim_parity=SECTIONS['shim_parity'],
                               writer_disable=SECTIONS['writer_disable'],
                               rollback=SECTIONS['rollback'])


def test_a_packet_is_hash_bound_over_every_required_section():
    packet = make_packet()
    assert set(review.REQUIRED_SECTIONS) <= set(packet)
    assert len(packet['bundle_sha256']) == 64


def test_a_packet_missing_a_section_is_refused():
    with pytest.raises(review.ReviewRefusal):
        review.build_packet(
            commit='c', implementer='i', replay_report={}, fault_matrix={'a': 1},
            validation_fence={'a': 1}, shadow={'a': 1}, canary={'a': 1},
            shim_parity={'a': 1}, writer_disable={'a': 1}, rollback={'a': 1})


def test_the_implementer_may_not_sign_their_own_receipt():
    packet = make_packet(implementer='claude-opus-4-8')
    with pytest.raises(review.ReviewRefusal):
        review.sign(packet, reviewer='claude-opus-4-8')
    receipt = review.sign(packet, reviewer='someone-else')
    assert receipt['bundle_sha256'] == packet['bundle_sha256']


def test_verify_round_trips_a_signed_receipt(tmp_path):
    packet = make_packet()
    receipt = review.sign(packet, reviewer='reviewer', findings=['none'])
    packet_path = str(tmp_path / 'packet.json')
    receipt_path = str(tmp_path / 'receipt.json')
    review.seal_packet(packet_path, packet)
    seal(receipt_path, receipt)
    verified = review.verify(packet_path, receipt_path)
    assert verified['verified'] is True
    assert verified['reviewer'] == 'reviewer'


def test_verify_refuses_a_receipt_bound_to_another_commit(tmp_path):
    packet = make_packet(commit='aaa')
    other = make_packet(commit='bbb')
    receipt = review.sign(other, reviewer='reviewer')
    packet_path = str(tmp_path / 'packet.json')
    receipt_path = str(tmp_path / 'receipt.json')
    review.seal_packet(packet_path, packet)
    seal(receipt_path, receipt)
    with pytest.raises(review.ReviewRefusal):
        review.verify(packet_path, receipt_path)


def test_verify_refuses_a_rejection_disposition(tmp_path):
    packet = make_packet()
    receipt = review.sign(packet, reviewer='reviewer', disposition='rejected')
    packet_path = str(tmp_path / 'packet.json')
    receipt_path = str(tmp_path / 'receipt.json')
    review.seal_packet(packet_path, packet)
    seal(receipt_path, receipt)
    with pytest.raises(review.ReviewRefusal):
        review.verify(packet_path, receipt_path)


def test_verify_refuses_a_missing_artifact(tmp_path):
    with pytest.raises(review.ReviewRefusal):
        review.verify(str(tmp_path / 'nope.json'), str(tmp_path / 'nope2.json'))


def test_the_schema_summary_carries_the_whole_contract():
    summary = review.schema_summary()
    assert summary['promotion_phases'][-1] == 'complete'
    assert summary['fault_points'] == list(faults.FAULT_POINTS)
    assert any('canonical.v1.jsonl' in row for row in summary['canonical_fence'])


def test_an_unsigned_or_uncanaried_wave_is_partial_not_go():
    assert review.cutover_verdict(
        offline_green=True, replay_exact=True, faults_green=True,
        validation_fenced=True, shadow_clean=True, canary_green=False,
        receipt_verified=True)['verdict'] == 'PARTIAL'
    assert review.cutover_verdict(
        offline_green=True, replay_exact=True, faults_green=True,
        validation_fenced=True, shadow_clean=True, canary_green=True,
        receipt_verified=False)['verdict'] == 'PARTIAL'


def test_only_a_full_green_wave_authorizes_the_writer_disable():
    verdict = review.cutover_verdict(
        offline_green=True, replay_exact=True, faults_green=True,
        validation_fenced=True, shadow_clean=True, canary_green=True,
        receipt_verified=True)
    assert verdict['verdict'] == 'GO'
    assert verdict['authorizes_writer_disable'] is True


def test_a_failing_offline_gate_is_no_go():
    verdict = review.cutover_verdict(
        offline_green=True, replay_exact=False, faults_green=True,
        validation_fenced=True, shadow_clean=True, canary_green=True,
        receipt_verified=True)
    assert verdict['verdict'] == 'NO-GO'
    assert verdict['authorizes_writer_disable'] is False


def test_every_fault_boundary_names_the_test_that_pins_it():
    uncovered = [point for point in faults.FAULT_POINTS
                 if point not in wave1_evidence.FAULT_COVERAGE]
    assert uncovered == []


def test_the_evidence_bundle_builds_offline(tmp_path):
    summary = wave1_evidence.build(
        commit='test', implementer='pytest',
        matrix=os.path.join(ROOT, 'tests', 'fixtures', 'pwg_pipeline'),
        canonical=str(tmp_path / 'absent.jsonl'), out_dir=str(tmp_path / 'out'))
    assert summary['replay_exact'] is True
    assert summary['shadow_unexplained_mismatches'] == 0
    # Without the canonical artifact the fence is honestly reported as absent,
    # which is not a pass -- so the verdict cannot be GO.
    assert summary['verdict']['validation_fenced'] is False
    assert summary['verdict']['verdict'] == 'NO-GO'


def test_the_canary_readiness_section_never_dials(monkeypatch):
    from pwg_pipeline import providers
    monkeypatch.delenv(providers.XAI_KEY_ENV, raising=False)
    monkeypatch.delenv(providers.DEEPSEEK_KEY_ENV, raising=False)
    section = wave1_evidence.canary_section()
    assert section['executed'] is False
    assert section['max_calls'] == 2
    assert section['cost_ceiling_usd'] == 4.0
    assert 'NOT RUN' in section['disposition']
