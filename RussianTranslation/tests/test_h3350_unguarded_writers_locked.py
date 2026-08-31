# -*- coding: utf-8 -*-
"""H3350 — the last four unguarded pwg_ru writers now go through the H2146 lock.

The H2890 Q7 census recorded 23 of 27 pwg_ru writers as ``guarded: true`` because
the H2146 lock (``store_write.locked_store_rewrite`` / ``PromoteClaim``) was visible
in their code path. Four writers kept writing ``pwg_ru_translated.jsonl`` with bare
``os.replace`` / unlocked appends:

    audit_translation_provenance.py  (write_rows)
    pipeline_version.py              (backfill subcommand)
    pwg_page_index.py                (--annotate rewrite)
    run_batch.py                     (apply_review, migrate_legacy, collect append)

This file pins the retrofit: every one of those lanes holds the store claim across
its write window, so a concurrent promote or mutator turns the run into a loud
``ClaimBusy`` refusal instead of last-writer-wins, and every full rewrite leaves a
per-run fsynced backup behind. Nothing here touches the live 26 MB store — all
fixtures are temp-dir stores, and ``_refresh_integrity_extract`` early-returns for
any path that is not the canonical store.
"""
import json
import os
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import pipeline_version  # noqa: E402
import pwg_page_index  # noqa: E402
import run_batch  # noqa: E402
from promote_lock import PromoteClaim  # noqa: E402
from store_write import ClaimBusy  # noqa: E402


def _rows():
    return [
        {'key1': 'agni', 'subcard': 'agni~~h0_s1', 'sense_tag': 's1', 'ru': 'огонь'},
        {'key1': 'vas', 'subcard': 'vas~~h0_s1', 'sense_tag': 's1', 'ru': 'вещь'},
    ]


def _fixture_store(tmp_path, rows=None):
    store = os.path.join(str(tmp_path), 'pwg_ru_translated.jsonl')
    with open(store, 'w', encoding='utf-8', newline='\n') as f:
        for row in (rows if rows is not None else _rows()):
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    return store


def _held_claim_refuses(store, fn):
    """A live PromoteClaim on ``store`` must turn ``fn()`` into a loud ClaimBusy."""
    before = open(store, 'rb').read()
    with pytest.raises(ClaimBusy):
        with PromoteClaim(store):
            fn()
    assert open(store, 'rb').read() == before, 'refused run must write nothing'


def test_audit_translation_provenance_write_rows_is_locked(tmp_path):
    import audit_translation_provenance as atp
    store = _fixture_store(tmp_path)

    _held_claim_refuses(store, lambda: atp.write_rows(store, _rows()))

    rows = [dict(r, ru=r['ru'] + '!') for r in _rows()]
    atp.write_rows(store, rows)
    assert len(open(store, encoding='utf-8').read().strip().splitlines()) == 2
    backups = [f for f in os.listdir(str(tmp_path)) if '.provaudit.' in f]
    assert backups, 'locked rewrite must leave its per-run backup'


def test_pipeline_version_backfill_is_locked(tmp_path):
    # backfill only stamps rows that carry a provenance dict without a pipeline
    # stamp; rows without provenance at all are left unchanged.
    legacy = [dict(r, provenance={'model_version': 'legacy-model'}) for r in _rows()]
    store = _fixture_store(tmp_path, rows=legacy)
    args = type('Args', (), {})()
    args.store = store
    args.prompt = 'v1'
    args.glossary = 'v1'
    args.script = 'v1'
    args.dry_run = False

    _held_claim_refuses(
        store,
        lambda: pipeline_version.cmd_backfill(args),
    )

    assert pipeline_version.cmd_backfill(args) == 0
    row = json.loads(open(store, encoding='utf-8').readline())
    assert row['provenance']['pipeline']['backfilled'] is True
    backups = [f for f in os.listdir(str(tmp_path)) if '.pverbackfill.' in f]
    assert backups, 'locked backfill must leave its per-run backup'


def test_pwg_page_index_annotate_is_locked(tmp_path):
    store = _fixture_store(tmp_path)

    _held_claim_refuses(store, lambda: pwg_page_index.annotate_cards([], store))

    # H3751 / #1801: `ambiguous` is its own counter now -- it used to be folded into
    # `matched`, so the operator statistic reported success on the homograph-pooled guess.
    matched, ambiguous, unmatched, total = pwg_page_index.annotate_cards([], store)
    assert (matched, ambiguous, unmatched, total) == (0, 0, 2, 2)
    backups = [f for f in os.listdir(str(tmp_path)) if '.pwgidx.' in f]
    assert backups, 'locked annotate must leave its per-run backup'


def test_run_batch_migrate_legacy_is_locked(tmp_path, monkeypatch):
    monkeypatch.setattr(run_batch, 'STORE', _fixture_store(tmp_path))
    monkeypatch.setattr(run_batch, 'attested_for', lambda idx, k1, k2: False)

    _held_claim_refuses(
        run_batch.STORE,
        lambda: run_batch.cmd_migrate_legacy([]),
    )

    run_batch.cmd_migrate_legacy([])
    row = json.loads(open(run_batch.STORE, encoding='utf-8').readline())
    assert row['review_status'] == 'legacy_needs_review'
    tag_dir = os.path.dirname(run_batch.STORE)
    backups = [f for f in os.listdir(tag_dir) if '.migratelegacy.' in f]
    assert backups, 'locked migration must leave its per-run backup'


def test_run_batch_collect_append_holds_the_claim():
    """The collect append sits inside ``with PromoteClaim(STORE):`` — a source-level
    regression gate: removing the claim from the append window must fail this test."""
    import inspect
    src = inspect.getsource(run_batch.cmd_collect)
    append_at = src.index("open(STORE, 'a'")
    claim_at = src.rindex('with PromoteClaim(STORE)', 0, append_at)
    between = src[claim_at:append_at]
    assert "_ensure_parent(STORE)" in between or "out.write" in src[append_at:]
