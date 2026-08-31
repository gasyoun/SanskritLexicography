#!/usr/bin/env python
"""Evidence-carrying wrapper around the changelog duplicate-entry gate (W1, C8-3).

[#1803](https://github.com/gasyoun/SanskritLexicography/issues/1803) row `C8-3`: the
changelog-lint gate inspects only the **root** changelog, so
[`RussianTranslation/CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md)
is unguarded — and this repo's dual-changelog layout (see `CLAUDE.md` § *Dual changelog*)
means the unguarded half is a first-class file, not a stray. The gate's green line was
indistinguishable from "the other changelog was checked too".

**Why a wrapper rather than an edit.**
[`scripts/changelog_duplicate_bullets.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/scripts/changelog_duplicate_bullets.py)
is a **copy of the canonical `github-spine/changelog_guard/` script** (its own CI workflow
says so). Editing the copy here would fork it from the canonical source for a
repo-specific concern. So the checker stays byte-identical and this wrapper adds the W1
accounting around it: what was compared, what exists and was **not** compared, and the
sidecar.

W1 scope: no predicate changes. This wrapper does **not** start failing on the sibling
changelog — extending the gate's scope is a separate decision with its own red. It makes
the gap *countable*: every changelog in the tree is a named input, and the unexamined ones
carry `units: 0` plus a warning naming them.

    python scripts/changelog_dupe_evidence_gate.py
    python scripts/changelog_dupe_evidence_gate.py --evidence /tmp/x.evidence.json
"""
import argparse
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PILOT = os.path.join(REPO, 'RussianTranslation', 'src', 'pilot')
for _p in (HERE, PILOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import changelog_duplicate_bullets as cdb                           # noqa: E402
import gate_evidence as ge                                          # noqa: E402

#: Sibling changelogs the root-only gate does not reach. Discovered, not hardcoded —
#: this list is only the search roots.
SIBLING_DIRS = ('RussianTranslation', 'ReverseDictionary',
                'Digital_Sanskrit_Lexicography-BOOK')


def count_entries(text):
    """Top-level entries inside `##` sections — the unit the gate compares.

    Read-only re-derivation for accounting only; it is deliberately NOT a second
    predicate and never affects the verdict.
    """
    n, in_section = 0, False
    for line in text.splitlines():
        if cdb.SECTION_RE.match(line):
            in_section = True
            continue
        if in_section and cdb.BULLET_RE.match(line):
            n += 1
    return n


def find_changelogs(repo):
    found = []
    for rel in ('',) + SIBLING_DIRS:
        directory = os.path.join(repo, rel) if rel else repo
        for name in cdb.CHANGELOG_NAMES:
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                found.append(path)
                break
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--repo', default=REPO)
    ap.add_argument('--evidence', default=None)
    args = ap.parse_args(argv)
    evidence_path = args.evidence or ge.default_sidecar('changelog_duplicate_bullets')

    ev = ge.GateEvidence('changelog_duplicate_bullets',
                         'duplicated changelog entries, root changelog (C8-3)')

    changelogs = find_changelogs(args.repo)
    root = next((p for p in changelogs
                 if os.path.dirname(p) == os.path.normpath(args.repo)), None)

    if root is None:
        ev.add_input('root_changelog', path=os.path.join(args.repo, 'CHANGELOG.md'),
                     units=0, exists=False)
        ev.add_predicate('entry_uniqueness', evaluations=0, hits=0)
        ev.set_verdict('pass')
        ev.declare_expected_empty('no_changelog_in_repo',
                                  'this repo ships no changelog, so no entry can repeat')
        ev.assert_nonvacuous()
        ev.emit(evidence_path)
        print('no changelog found in %s — nothing to check' % args.repo)
        return 0

    with open(root, encoding='utf-8') as fh:
        text = fh.read()
    compared = count_entries(text)
    ev.add_input('root_changelog', path=root, units=compared)

    # The C8-3 gap, made countable: every OTHER changelog in the tree is named,
    # hashed, and stamped units=0 — present, and not compared by this gate.
    for path in changelogs:
        if path == root:
            continue
        ev.add_input('unexamined_changelog:%s'
                     % os.path.relpath(path, args.repo).replace('\\', '/'),
                     path=path, units=0)
        ev.warnings.append(
            'C8-3: %s exists and is NOT compared by this gate (root-only scope)'
            % os.path.relpath(path, args.repo).replace('\\', '/'))

    dupes, skipped = cdb.find_duplicates(text, cdb.load_allowlist(args.repo))
    ev.add_predicate('entry_uniqueness', evaluations=compared, hits=len(dupes),
                     detail=skipped or None)
    ev.note('scope', 'root changelog only (C8-3 unfixed by design in W1)')
    ev.set_verdict('fail' if dupes else 'pass')
    try:
        ev.assert_nonvacuous()
    except ge.VacuousGateError as exc:
        ev.set_verdict('fail')
        ev.emit(evidence_path)
        print('CHANGELOG DUPLICATE GATE: %s' % exc)
        return 1
    ev.emit(evidence_path)

    # The human-readable report is the checker's own. It resolves the repo from its
    # own __file__, so it is only meaningful for the default repo; a --repo run (the
    # W1 pins) takes its exit code from the verdict just recorded.
    if os.path.normpath(args.repo) == os.path.normpath(REPO):
        cdb.main()
    print(ev.summary())
    return 1 if dupes else 0


if __name__ == '__main__':
    sys.exit(main())
