"""H4053 — the report-only quarantine sample path selftest is a pytest gate."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import pwg_quarantine_sample30 as sample30  # noqa: E402


def test_six_offline_proofs():
    results = sample30.selftest()
    assert set(results) == {
        'reservation_before_io', 'resume_no_duplicate_spend', 'attribution',
        'input_preservation', 'dry_run_zero_io', 'no_promote_capability'}
    assert results['reservation_before_io']['refusal_class'] == \
        'budget_refusal'
    assert results['resume_no_duplicate_spend']['cards_delivered'] == \
        results['resume_no_duplicate_spend']['provider_dispatches_total']
    assert results['input_preservation']['guard_unchanged'] is True
    assert results['dry_run_zero_io'] == {'provider_calls': 0,
                                          'reservations': 0}
    assert results['no_promote_capability']['promotion_rows'] == 0


def test_freeze_is_deterministic(tmp_path):
    packet_a = sample30.freeze_sample(n=12)
    packet_b = sample30.freeze_sample(n=12)
    assert packet_a['cards'] == packet_b['cards']
    assert len(packet_a['cards']) == 12
    assert len({(c['subcard'], c['sense_tag']) for c in
                packet_a['cards']}) == 12
    assert all(c['review_class'] == 'unmeasured_pending_paid_read'
               and c['ru_quality_verdict'] == 'unknown_not_measured'
               for c in packet_a['cards'])
    assert packet_a['fresh_population']['flag_label'].startswith(
        'segmentation-change flag')
