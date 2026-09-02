"""Pin the G5 print-ready predicate against the schema the live store actually writes.

The bug this guards (H215 / #1712): `release_readiness.py` and
`preflight_remaining_gates.py` inlined

    row.get('ok') and row.get('placeholders_ok') and row.get('key_match')

which no row in the live 11 603-row store satisfies — those three fields are absent
on every one of them. G5 read `print_ready=0` forever and looked like a human review
backlog. Two classes of check here:

  1. the predicate itself accepts a live-shaped approved row and still rejects the
     things it must reject;
  2. NO gate module re-inlines the raw conjunction (a source check) — that is the
     drift, and it is invisible to a behavioural test on a store fixture that
     happens to carry legacy flags.
"""
import io
import json
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import store_flags  # noqa: E402

# A row shaped exactly like the live store: review_status + key1/subcard/ru, and NONE
# of the three legacy flags. This is the row the old conjunction scored as not ready.
LIVE_APPROVED = {
    'review_status': 'approved', 'key1': 'agni', 'subcard': 'a', 'ru': 'огонь',
    'layer': 'sense', 'provenance': 'pwg', 'reviewer': 'mg',
}
LEGACY_APPROVED = dict(LIVE_APPROVED, ok=True, placeholders_ok=True, key_match=True)


def test_live_shaped_approved_row_is_print_ready():
    """The #1712 regression: no legacy flags, still print-ready."""
    assert store_flags.is_print_ready(LIVE_APPROVED)
    assert store_flags.is_print_ready(LEGACY_APPROVED)
    assert store_flags.is_print_ready(dict(LIVE_APPROVED, review_status='human_reviewed'))


def test_unreviewed_rows_are_not_print_ready():
    assert not store_flags.is_print_ready(dict(LIVE_APPROVED, review_status='ai_translated'))
    assert not store_flags.is_print_ready(dict(LIVE_APPROVED, review_status='needs_review'))
    assert not store_flags.is_print_ready({'key1': 'agni', 'subcard': 'a', 'ru': 'огонь'})


def test_explicit_false_flags_still_reject():
    """A fallback that ignored an explicit False would launder known-bad rows."""
    assert not store_flags.is_print_ready(dict(LEGACY_APPROVED, ok=False))
    assert not store_flags.is_print_ready(dict(LEGACY_APPROVED, placeholders_ok=False))
    assert not store_flags.is_print_ready(dict(LEGACY_APPROVED, key_match=False))


def test_structural_evidence_is_required_when_flags_are_absent():
    assert not store_flags.is_print_ready(dict(LIVE_APPROVED, ru=''))
    assert not store_flags.is_print_ready(
        {'review_status': 'approved', 'key1': 'agni', 'ru': 'огонь'})


GATE_MODULES = ['release_readiness.py', 'preflight_remaining_gates.py']
INLINED = re.compile(r"get\('placeholders_ok'\)|get\(\"placeholders_ok\"\)")


def test_no_gate_reinlines_the_conjunction():
    for name in GATE_MODULES:
        path = os.path.join(SRC, name)
        assert os.path.exists(path), '%s is missing' % name
        src = io.open(path, encoding='utf-8').read()
        assert not INLINED.search(src), '%s re-inlines the raw flag conjunction' % name
        assert 'store_flags' in src, '%s does not import store_flags' % name


def test_review_counts_over_a_live_shaped_store(tmp_path, monkeypatch):
    """release_readiness.review_counts() must count a live-shaped approved row."""
    store = tmp_path / 'store.jsonl'
    with io.open(str(store), 'w', encoding='utf-8') as f:
        for row in (LIVE_APPROVED,
                    dict(LIVE_APPROVED, review_status='ai_translated'),
                    dict(LIVE_APPROVED, review_status='approved', key1='agn2')):
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    monkeypatch.setenv('PWG_RU_STORE', str(store))
    monkeypatch.setenv('PWG_RU_REVIEW_CSV', str(tmp_path / 'absent.csv'))
    sys.modules.pop('release_readiness', None)
    import release_readiness
    try:
        assert release_readiness.review_counts()['print_ready'] == 2
    finally:
        sys.modules.pop('release_readiness', None)


def test_print_ready_rejects_apparatus_as_gloss():
    """H2876 gate wired (02-09-2026): pure apparatus rendered as gloss is not print-ready."""
    bad = dict(LIVE_APPROVED, de='eines', ru='поручать кому-л.')
    assert not store_flags.row_metalanguage_ok(bad)
    assert not store_flags.machine_ok(bad)
    assert not store_flags.is_print_ready(bad)
    assert store_flags.is_print_ready(dict(LIVE_APPROVED, de='Name eines Baumes', ru='название дерева'))
