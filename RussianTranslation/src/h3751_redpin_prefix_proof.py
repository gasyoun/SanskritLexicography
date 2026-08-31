#!/usr/bin/env python
r"""H3751 RED proof -- run the #1801 fixture pins against PRE-FIX `pwg_page_index.py`.

The wave bar (ruling 10) is a pin *verified RED against pre-fix master*, not a green-only
test. This loads the pre-fix `annotate_cards` straight out of git (default: the master tip
this unit branched from) and replays `pwg_page_index.SELFTEST_SOURCE` plus the same rows
through it, printing what the old homograph-pooled selection produced.

    python src/h3751_redpin_prefix_proof.py [--rev 7435178e0]

Exit 0 when the old code DISAGREES with the fixed expectations on at least one row (the
pin has teeth); exit 1 if the old code already agreed everywhere -- which would mean the
pin proves nothing and must be strengthened. The store writer is stubbed out, so this
never touches the canonical store.
"""
import argparse
import importlib.util
import io
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_page_index as fixed  # noqa: E402

DEFAULT_REV = '7435178e0'
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
GIT_PATH = 'RussianTranslation/src/pwg_page_index.py'


class RevisionUnavailable(RuntimeError):
    """The pre-fix revision is not in this clone (a shallow CI checkout, typically)."""


def load_prefix_module(rev, workdir):
    proc = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (rev, GIT_PATH)],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          encoding='utf-8', errors='replace')
    if proc.returncode:
        raise RevisionUnavailable(proc.stderr.strip() or 'git show failed for %s' % rev)
    src = proc.stdout
    path = os.path.join(workdir, 'pwg_page_index_prefix.py')
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(src)
    spec = importlib.util.spec_from_file_location('pwg_page_index_prefix', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # never let the replay reach a real store
    mod.locked_store_rewrite = lambda store, rows, tag=None: None
    return mod


def fixture_rows():
    return [
        {'key1': 'vasa', 'subcard': 'vasa~~h0_00_pwg00'},
        {'key1': 'vasa', 'subcard': 'vasa~~h1_00_pwg00'},
        {'key1': 'vasa', 'subcard': 'vasa~~h2_00_pwg00'},
        {'key1': 'vasa', 'subcard': 'vasa~~h3_00_pwg00'},
        {'key1': 'vasa', 'subcard': 'vasa~~h9_00_pwg00'},
        {'key1': 'akArya', 'subcard': 'ak_arya~~h1_00_pwg00'},
        {'key1': 'akArya', 'subcard': 'ak_arya'},
    ]


EXPECTED = ['6-0001', '6-0500', '6-0900', '7-0100', None, '1-0199', '1-0009']


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--rev', default=DEFAULT_REV, help='pre-fix revision to replay')
    args = ap.parse_args()

    try:
        old_rows, counters = replay_prefix_selection(args.rev, fixed.SELFTEST_SOURCE)
    except RevisionUnavailable as exc:
        # Deliberately NOT wired into CI, whose checkout is shallow. Reported loudly rather
        # than swallowed, so a "skip" can never be mistaken for a pass.
        print('SKIPPED: revision %s is not in this clone (%s).' % (args.rev, exc))
        print('Run in a full clone, or `git fetch --unshallow` first.')
        return 2
    got = [r.get('column') for r in old_rows]

    print('pre-fix rev      : %s' % args.rev)
    print('pre-fix counters : matched=%d unmatched=%d total=%d' % counters)
    print('%-28s %-10s %-10s %s' % ('subcard', 'pre-fix', 'fixed', 'verdict'))
    disagreements = 0
    for r, old_col, exp in zip(fixture_rows(), got, EXPECTED):
        agree = old_col == exp
        disagreements += 0 if agree else 1
        print('%-28s %-10s %-10s %s' % (r['subcard'], old_col, exp,
                                        'same' if agree else 'RED (pin has teeth)'))
    print('rows where pre-fix disagrees with the pin: %d / %d' % (disagreements, len(EXPECTED)))
    if not disagreements:
        print('FAIL: the pin is green on pre-fix code and proves nothing')
        return 1
    print('PASS: the pin is RED against %s' % args.rev)
    return 0


def replay_prefix_selection(rev, source_text):
    """Re-run the pre-fix `annotate_cards`; hand back the mutated rows and its counters.

    `annotate_cards` writes through `locked_store_rewrite`, which is stubbed here, so the
    mutated rows are otherwise unreachable -- capture them from the stub instead.
    """
    import json
    captured = {}
    with tempfile.TemporaryDirectory() as td:
        old = load_prefix_module(rev, td)
        old.locked_store_rewrite = lambda store, rows, tag=None: captured.setdefault('rows', rows)
        src = os.path.join(td, 'pwg_fixture.txt')
        with io.open(src, 'w', encoding='utf-8', newline='\n') as f:
            f.write(source_text)
        store = os.path.join(td, 'fixture_store.jsonl')
        with io.open(store, 'w', encoding='utf-8', newline='\n') as f:
            for r in fixture_rows():
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        counters = old.annotate_cards(old.parse_source(src), store)
    return captured['rows'], counters


if __name__ == '__main__':
    sys.exit(main())
