# -*- coding: utf-8 -*-
"""H2892 — a supersede without --override-reviewed must leave reviewed bytes alone.

H2146 added the protection: ``merge_store_rows`` refuses to replace a subcard whose
existing rows a human has touched, and ``store_write.locked_store_rewrite`` became
the one sanctioned rewrite path. The H2890 census then recorded 23 of 27 pwg_ru
writers as ``guarded: true`` — meaning the lock is *visible in the code path*.

Visible is not measured. What the census could not assert, and this file does, is
that a full supersede round trip — merge, then rewrite the whole store through the
lock — leaves the reviewed row **byte-identical on disk**. Field-level equality is
not enough: the store is JSONL and the promote path re-serializes every line, so a
key reorder or an ``ensure_ascii`` flip would preserve the values and still rewrite
every reviewed byte, which is exactly the class of change the H2891 digest tripwire
goes red on.

Nothing here touches the live 26 MB store. Every case builds its own fixture store
in a temp directory. ``store_write.py`` is deliberately NOT modified by this test —
the point is to pin the behaviour of the shipped lock, not to build a new one.
"""
import io
import json
import os
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import store_write  # noqa: E402
from promote_final_cards import human_touched, merge_store_rows  # noqa: E402

#: A row a human has ruled on: named reviewer AND an out-of-machine status.
#: Non-ASCII on purpose — a serializer that flips ensure_ascii would rewrite this
#: line's bytes while leaving every field value equal.
REVIEWED = {
    'key1': 'agni', 'subcard': 'agni~~h0_s1', 'sense_tag': 's1',
    'ru': 'огонь, жертвенный огонь', 'de': 'Feuer', 'en': 'fire',
    'review_status': 'approved', 'reviewer': 'mg', 'human_review': True,
    'layer': 'sense', 'provenance': {'source': 'pwg'},
}

#: An untouched machine row for a different subcard — the promote must land on it.
MACHINE = {
    'key1': 'agni', 'subcard': 'agni~~h0_s2', 'sense_tag': 's2',
    'ru': 'старый машинный перевод', 'de': 'alt', 'en': 'old',
    'review_status': 'ai_translated', 'reviewer': None,
    'layer': 'sense', 'provenance': {'source': 'pwg'},
}


def _attempt(subcard, ru):
    """A fresh machine attempt at ``subcard`` — what a promote brings in."""
    return {
        'key1': 'agni', 'subcard': subcard, 'sense_tag': subcard.rsplit('_', 1)[-1],
        'ru': ru, 'de': 'neu', 'en': 'new',
        'review_status': 'ai_translated', 'reviewer': None,
        'layer': 'sense', 'provenance': {'source': 'pwg'},
    }


def _write(store, rows, tag='h2892'):
    return store_write.locked_store_rewrite(store, rows, tag=tag)


def _lines(store):
    with io.open(store, 'rb') as fh:
        return fh.read().split(b'\n')


def _line_for(store, subcard):
    """The raw bytes of the one line whose row carries ``subcard``."""
    found = [line for line in _lines(store)
             if line and json.loads(line.decode('utf-8'))['subcard'] == subcard]
    assert len(found) == 1, 'expected exactly one line for %s, got %d' % (subcard, len(found))
    return found[0]


def test_the_fixture_row_is_actually_protected():
    """Guard the guard: if REVIEWED stopped being human_touched, every other
    assertion below would pass vacuously."""
    assert human_touched(REVIEWED)
    assert not human_touched(MACHINE)


def test_supersede_without_override_leaves_reviewed_bytes_identical(tmp_path):
    store = str(tmp_path / 'pwg_ru_translated.jsonl')
    _write(store, [REVIEWED, MACHINE])
    before = _line_for(store, REVIEWED['subcard'])

    promoted = [_attempt(REVIEWED['subcard'], 'НОВЫЙ машинный перевод'),
                _attempt(MACHINE['subcard'], 'новый машинный перевод')]
    merged, downgraded, protected = merge_store_rows(
        [REVIEWED, MACHINE], promoted, override_reviewed=False)

    assert protected == [REVIEWED['subcard']], (
        'the reviewed subcard must be refused, got protected=%r downgraded=%r'
        % (protected, downgraded))

    _write(store, merged)
    after = _line_for(store, REVIEWED['subcard'])
    assert after == before, (
        'the supersede rewrote the reviewed row.\nbefore: %r\nafter:  %r' % (before, after))

    landed = json.loads(_line_for(store, MACHINE['subcard']).decode('utf-8'))
    assert landed['ru'] == 'новый машинный перевод', (
        'the machine subcard must still be superseded — a lock that blocks '
        'everything moves the damage from the data to the pipeline')


def test_override_reviewed_does_rewrite_those_bytes(tmp_path):
    """The control. Without this, a merge that silently dropped every incoming
    row would pass the test above."""
    store = str(tmp_path / 'pwg_ru_translated.jsonl')
    _write(store, [REVIEWED, MACHINE])
    before = _line_for(store, REVIEWED['subcard'])

    promoted = [_attempt(REVIEWED['subcard'], 'НОВЫЙ машинный перевод')]
    merged, _downgraded, protected = merge_store_rows(
        [REVIEWED, MACHINE], promoted, override_reviewed=True)
    assert protected == []

    _write(store, merged)
    assert _line_for(store, REVIEWED['subcard']) != before, (
        '--override-reviewed must land the machine attempt (H2146)')


@pytest.mark.parametrize('stamp', [
    {'reviewer': 'mg'},
    {'review_status': 'approved'},
    {'review_status': 'human_reviewed'},
    {'editorial_decision': 'keep'},
    {'editorial_decision_ru': 'reworded'},
])
def test_every_arm_of_the_predicate_protects_the_bytes(tmp_path, stamp):
    """The census predicate has three independent arms. A regression that kept
    only the ``reviewer`` arm would still pass a single-fixture test.

    The ``editorial_decision*`` arm matches zero rows in the live store today —
    which is precisely why it needs a test rather than a measurement."""
    row = dict(MACHINE, subcard='agni~~h0_s9', sense_tag='s9')
    row.pop('reviewer', None)
    row.pop('review_status', None)
    row.update(stamp)
    assert human_touched(row), 'fixture must be human_touched: %r' % stamp

    store = str(tmp_path / 'pwg_ru_translated.jsonl')
    _write(store, [row])
    before = _line_for(store, row['subcard'])

    merged, _downgraded, protected = merge_store_rows(
        [row], [_attempt(row['subcard'], 'машинная замена')], override_reviewed=False)
    assert protected == [row['subcard']]

    _write(store, merged)
    assert _line_for(store, row['subcard']) == before


def test_machine_output_never_self_protects(tmp_path):
    """``rows_for()`` stamps machine rows ``reviewer: None`` +
    ``review_status='ai_translated'``. If either started reading as human, the
    protection would freeze the whole store and the pipeline would stall."""
    assert not human_touched({'reviewer': None, 'review_status': 'ai_translated'})
    assert not human_touched({'review_status': 'ai_retranslated'})
    assert not human_touched({'editorial_decision': ''})

    store = str(tmp_path / 'pwg_ru_translated.jsonl')
    _write(store, [MACHINE])
    merged, _downgraded, protected = merge_store_rows(
        [MACHINE], [_attempt(MACHINE['subcard'], 'замена')], override_reviewed=False)
    assert protected == []
    _write(store, merged)
    assert json.loads(_line_for(store, MACHINE['subcard']).decode('utf-8'))['ru'] == 'замена'


def test_extract_refresh_ignores_every_store_but_the_canonical_one(tmp_path):
    """The H2892 hook must fire on the live store and on nothing else.

    Every fixture in this file writes a temp store; if the hook did not
    discriminate, each of them would try to rebuild the committed projection —
    and a test run would dirty the working tree."""
    calls = []
    import build_integrity_extract

    original = build_integrity_extract.main
    build_integrity_extract.main = lambda argv=None: calls.append(argv) or 0
    try:
        store_write._refresh_integrity_extract(str(tmp_path / 'pwg_ru_translated.jsonl'))
        assert calls == [], 'a temp store must not trigger an extract rebuild'

        store_write._refresh_integrity_extract(build_integrity_extract.STORE)
        assert calls == [[]], 'the canonical store must trigger exactly one rebuild'
    finally:
        build_integrity_extract.main = original


def test_extract_refresh_never_breaks_a_completed_write(tmp_path, capsys):
    """The store is already fsynced and replaced by the time the hook runs. A
    missing csl_pyutil, a read-only tree — none of it may propagate."""
    import build_integrity_extract

    original = build_integrity_extract.main

    def boom(argv=None):
        raise SystemExit('csl_pyutil is not installed')

    build_integrity_extract.main = boom
    try:
        store_write._refresh_integrity_extract(build_integrity_extract.STORE)
    finally:
        build_integrity_extract.main = original
    assert 'could not be refreshed' in capsys.readouterr().err


def test_extract_refresh_can_be_opted_out(tmp_path, monkeypatch):
    calls = []
    import build_integrity_extract

    monkeypatch.setenv('PWG_SKIP_INTEGRITY_EXTRACT', '1')
    original = build_integrity_extract.main
    build_integrity_extract.main = lambda argv=None: calls.append(argv) or 0
    try:
        store_write._refresh_integrity_extract(build_integrity_extract.STORE)
    finally:
        build_integrity_extract.main = original
    assert calls == []


def test_the_lock_backs_up_before_it_rewrites(tmp_path):
    """A refusal is the first line of defence; the per-run backup is the second.
    H2892 asserts it survives, because the whole point of the writer lock is that
    a rewrite that does slip through is recoverable."""
    store = str(tmp_path / 'pwg_ru_translated.jsonl')
    assert _write(store, [REVIEWED]) is None, 'a fresh store must not fabricate a backup'
    original = io.open(store, 'rb').read()

    backup = _write(store, [MACHINE])
    assert backup and os.path.exists(backup)
    assert io.open(backup, 'rb').read() == original
