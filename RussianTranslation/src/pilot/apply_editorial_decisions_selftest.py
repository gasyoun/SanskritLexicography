#!/usr/bin/env python
"""Selftests for apply_editorial_decisions.py (H1556 Track D / VERIFICATION D1–D3)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import apply_editorial_decisions as aed  # noqa: E402

PASS = 0
FAIL = 0


def ok(name: str) -> None:
    global PASS
    PASS += 1
    print('ok  ', name)


def fail(name: str, detail: str = '') -> None:
    global FAIL
    FAIL += 1
    print('FAIL', name, detail)


def write_json(path: str, obj) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def write_store(path: str, rows) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def test_d1_missing_votes_pending_exit0() -> None:
    """D1: missing votes → status pending_votes, exit 0."""
    with tempfile.TemporaryDirectory() as td:
        missing = os.path.join(td, 'nope.decisions.json')
        store = os.path.join(td, 'store.jsonl')
        write_store(store, [{'key': 'foo', 'senses': []}])
        report = aed.build_report(
            abbrev_path=missing,
            style_path=os.path.join(td, 'also_missing.json'),
            store_path=store,
            dry_run=True,
        )
        if report.get('status') != 'pending_votes':
            fail('test_d1_missing_votes_pending_exit0', 'status=%r' % report.get('status'))
            return
        # CLI path
        proc = subprocess.run(
            [
                sys.executable,
                os.path.join(HERE, 'apply_editorial_decisions.py'),
                '--abbrev-decisions', missing,
                '--style-decisions', os.path.join(td, 'also_missing.json'),
                '--store', store,
            ],
            cwd=HERE,
            capture_output=True,
            text=True,
            encoding='utf-8',
        )
        if proc.returncode != 0:
            fail('test_d1_missing_votes_pending_exit0', 'cli rc=%s stderr=%s' % (
                proc.returncode, proc.stderr[:300]))
            return
        if 'pending_votes' not in proc.stdout:
            fail('test_d1_missing_votes_pending_exit0', 'stdout missing pending_votes')
            return
    ok('test_d1_missing_votes_pending_exit0')


def test_d2_synthetic_nonempty_delta() -> None:
    """D2: synthetic decisions + fixture store → non-empty delta report."""
    with tempfile.TemporaryDirectory() as td:
        store = os.path.join(td, 'store.jsonl')
        write_store(store, [
            {'key': 'gam~~h0_00', 'senses': [{'ru': 'идти'}]},
            {'key': 'as~~h0_00', 'senses': [{'ru': 'быть'}]},
            {'key': 'untouched', 'senses': [{'ru': 'x'}]},
        ])
        decisions = os.path.join(td, 'synth.decisions.json')
        write_json(decisions, {
            'sheet_id': 'h1556_synth',
            'items': [
                {'id': 'gam|gam~~h0_00|1', 'decision': 'approve', 'note': 'ok'},
                {'id': 'as|as~~h0_00|1', 'decision': 'reject', 'note': 'fix later'},
                {'id': 'missing|no_such_key|1', 'decision': 'approve', 'note': ''},
                {'id': 'defer|gam~~h0_00|2', 'decision': 'defer', 'note': ''},
            ],
        })
        report = aed.build_report(
            abbrev_path=decisions,
            style_path=None,
            store_path=store,
            dry_run=True,
        )
        if report.get('status') != 'dry_run':
            fail('test_d2_synthetic_nonempty_delta', 'status=%r' % report.get('status'))
            return
        if report.get('tokens_that_would_change', 0) < 2:
            fail('test_d2_synthetic_nonempty_delta', 'tokens=%r' % report.get('tokens_that_would_change'))
            return
        counts = report.get('counts') or {}
        if counts.get('approve') != 2 or counts.get('reject') != 1:
            fail('test_d2_synthetic_nonempty_delta', 'counts=%r' % counts)
            return
        if counts.get('missing_from_store', 0) < 1:
            fail('test_d2_synthetic_nonempty_delta', 'expected missing_from_store')
            return
        md = aed.render_markdown(report)
        if 'tokens_that_would_change' not in md:
            fail('test_d2_synthetic_nonempty_delta', 'md missing tokens line')
            return
    ok('test_d2_synthetic_nonempty_delta')


def test_d3_write_requires_env_gate() -> None:
    """D3: cannot write store without PWG_RU_ALLOW_EDITORIAL_APPLY=1."""
    with tempfile.TemporaryDirectory() as td:
        store = os.path.join(td, 'store.jsonl')
        write_store(store, [{'key': 'k1', 'senses': [{'ru': 'a'}]}])
        decisions = os.path.join(td, 'd.json')
        write_json(decisions, {
            'sheet_id': 'gate',
            'items': [{'id': 'r|k1|1', 'decision': 'approve', 'note': ''}],
        })
        # Ensure env is off for the refusal path.
        old = os.environ.pop(aed.ENV_ALLOW_APPLY, None)
        try:
            try:
                aed.build_report(
                    abbrev_path=decisions,
                    style_path=None,
                    store_path=store,
                    dry_run=False,
                )
                fail('test_d3_write_requires_env_gate', 'expected SystemExit')
                return
            except SystemExit as exc:
                msg = str(exc)
                if aed.ENV_ALLOW_APPLY not in msg and 'refuse' not in msg.lower():
                    fail('test_d3_write_requires_env_gate', 'unexpected exit: %s' % msg)
                    return
            # With env set, apply stamps the temp store.
            os.environ[aed.ENV_ALLOW_APPLY] = '1'
            report = aed.build_report(
                abbrev_path=decisions,
                style_path=None,
                store_path=store,
                dry_run=False,
            )
            if report.get('status') != 'applied':
                fail('test_d3_write_requires_env_gate', 'status=%r' % report.get('status'))
                return
            rows = aed.iter_store_rows(store)
            if not rows or rows[0].get('editorial_decision') != 'approve':
                fail('test_d3_write_requires_env_gate', 'row not stamped: %r' % rows)
                return
        finally:
            if old is None:
                os.environ.pop(aed.ENV_ALLOW_APPLY, None)
            else:
                os.environ[aed.ENV_ALLOW_APPLY] = old
    ok('test_d3_write_requires_env_gate')


def test_extract_store_key() -> None:
    if aed.extract_store_key('gam|gam~~h0_00|1') != 'gam~~h0_00':
        fail('test_extract_store_key', aed.extract_store_key('gam|gam~~h0_00|1'))
        return
    if aed.extract_store_key('bare_key') != 'bare_key':
        fail('test_extract_store_key', 'bare')
        return
    ok('test_extract_store_key')


def main() -> int:
    test_extract_store_key()
    test_d1_missing_votes_pending_exit0()
    test_d2_synthetic_nonempty_delta()
    test_d3_write_requires_env_gate()
    print()
    print('%d/%d passed (H1556 Track D selftest)' % (PASS, PASS + FAIL))
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
