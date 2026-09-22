#!/usr/bin/env python
"""Mechanical gate for LANG_PARITY.md — see that doc for the policy this enforces.

  python src/pilot/lang_parity_check.py                       # check, exit 1 on any violation
  python src/pilot/lang_parity_check.py --update-hash <id>     # after re-verifying an entry,
                                                                # refresh its verified_sha256 snapshot

This does NOT diff behavior between languages — it only checks that every ledger
entry has a verdict (and the verdict's required field), and that no file a SHARED /
INTENTIONAL-DIVERGENCE / GAP entry depends on has drifted since it was last verified.
Drift means a human must re-open the entry and re-affirm (or correct) its verdict.
Both the check and --update-hash refuse a ledger block that repeats a JSON key at any
level (a merge/replay artifact) instead of silently keeping the last copy.
"""
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))  # .../RussianTranslation
LEDGER_MD = os.path.join(REPO_ROOT, 'LANG_PARITY.md')
FENCE_RE = re.compile(r'```json lang_parity_ledger\r?\n(.*?)```', re.DOTALL)
COVERAGE_FENCE_RE = re.compile(r'```json lang_parity_coverage\r?\n(.*?)```', re.DOTALL)

VALID_VERDICTS = {'SHARED', 'INTENTIONAL-DIVERGENCE', 'GAP'}

# --- Coverage guard -------------------------------------------------------
# The drift check only re-verifies files ALREADY in the ledger. A brand-new
# language-aware file (a fresh `*_en.py` reimplementation, or a new gate that branches
# on `--lang`) could silently escape parity tracking entirely — the exact hole the
# C1–C9 bug-hunt's EN findings (audit_window_en.py, promote_en.py) grew in. The coverage
# guard closes it: every language-aware pipeline file must be EITHER tracked by a ledger
# entry OR listed in the `exempt` map (with a one-line reason) of the lang_parity_coverage
# block in LANG_PARITY.md. Detection logic lives here (code); curated exceptions live in
# that block (data).
COVERAGE_DIRS = ('src', 'src/pilot')            # non-recursive: where the runtime lane lives
LANG_SIGNAL = [
    re.compile(r"""['"]english['"]"""),
    re.compile(r"\blang\s*==\s*['\"]en['\"]"),
    re.compile(r"\blang\s*=\s*['\"]en['\"]"),
    re.compile(r"--lang\b"),
    re.compile(r"\bFIELD\["),
    re.compile(r"_FRAG_TRANSLATION_FIELD|CARD_FIELD"),
    re.compile(r"\blang\s*==\s*['\"]ru['\"]"),
]


# --- Duplicate-key refusal ------------------------------------------------
# Plain json.loads keeps the LAST value of a repeated key and drops the rest without a
# word. On 22-09-2026 the recovered PR #2305 (H4530) replayed an old re-hash hunk on a
# newer base and appended 7 duplicate keys with STALE hashes inside
# `headless_execution_manifest_h818.verified_sha256`; the checker read the stale last
# values and reported 8 "changed since last parity verification" drifts instead of the
# real cause, and master stayed red until #2306 (H5259). The ledger is hand-merged JSON,
# so a repeated key is always a merge/replay artifact: refuse it at parse time.
class DuplicateKeyError(SystemExit):
    """A ledger block repeats a JSON key. A SystemExit like this module's other refusals
    (the CLI exits 1 with the message); its own type so callers and the selftest can tell
    it apart from them."""


class _DupObject(dict):
    """A parsed JSON object that repeats a key at or below itself; `dups` = [(path, key)]."""
    dups = ()


def _nested_dups(value, path):
    if isinstance(value, _DupObject):
        return [(path + p, k) for p, k in value.dups]
    if isinstance(value, list):
        return [d for i, v in enumerate(value) for d in _nested_dups(v, path + (i,))]
    return []


def _refuse_duplicate_keys(pairs):
    """object_pairs_hook. json calls it innermost-object-first, so the object that holds
    the repeat cannot see which entry it belongs to: it marks itself instead of raising,
    the mark bubbles up through every enclosing object, and parse_ledger_json() raises
    once the whole block is parsed, naming the entry id, where and which key."""
    obj, dups = {}, []
    for k, v in pairs:
        dups += _nested_dups(v, (k,))
        if k in obj:
            dups.append(((), k))
        obj[k] = v
    if not dups:
        return obj
    marked = _DupObject(obj)
    marked.dups = dups
    return marked


def _where(path):
    return ''.join('[%d]' % p if isinstance(p, int) else ('.' if i else '') + p
                   for i, p in enumerate(path)) or 'its top level'


def parse_ledger_json(raw, path=LEDGER_MD, block='lang_parity_ledger'):
    """json.loads for a LANG_PARITY.md block that refuses a repeated key at ANY level."""
    data = json.loads(raw, object_pairs_hook=_refuse_duplicate_keys)
    dups = _nested_dups(data, ())
    if not dups:
        return data
    lines = []
    for p, key in dups:
        if p and isinstance(p[0], int) and isinstance(data, list) and isinstance(data[p[0]], dict):
            lines.append('entry %r: key %r repeated in %s'
                         % (data[p[0]].get('id', '<entry %d>' % p[0]), key, _where(p[1:])))
        else:
            lines.append('key %r repeated in %s' % (key, _where(p)))
    raise DuplicateKeyError(
        '%s: the ```json %s block repeats %d JSON key(s) -- refusing to load it:\n  - %s\n'
        'A repeated key is a merge/replay artifact (e.g. an old hunk re-applied on a newer '
        'base appends a second copy). Plain JSON parsing would silently keep the LAST copy, and '
        'a stale hash there reads as false "changed since last parity verification" drift. '
        'Fix by hand: delete the stale copy of each repeated key, re-check the entry\'s verdict, '
        'then run `python src/pilot/lang_parity_check.py --update-hash <id>`.'
        % (path, block, len(dups), '\n  - '.join(lines)))


def load_ledger(path=LEDGER_MD):
    text = open(path, encoding='utf-8').read()
    m = FENCE_RE.search(text)
    if not m:
        raise SystemExit('no ```json lang_parity_ledger fenced block found in %s' % path)
    return parse_ledger_json(m.group(1), path), text, m.span(1)


def load_coverage(path=LEDGER_MD):
    """Parse the optional lang_parity_coverage block ({exempt: {path: reason}}). Absent => {}."""
    m = COVERAGE_FENCE_RE.search(open(path, encoding='utf-8').read())
    return parse_ledger_json(m.group(1), path, 'lang_parity_coverage') if m else {}


def candidate_files():
    """Every language-aware pipeline .py under COVERAGE_DIRS (non-recursive, selftests excluded)."""
    cands = []
    for base in COVERAGE_DIRS:
        d = os.path.join(REPO_ROOT, base)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith('.py') or fn.endswith('_selftest.py') or fn.endswith('_test.py'):
                continue
            rel = base + '/' + fn
            try:
                text = open(os.path.join(d, fn), encoding='utf-8').read()
            except OSError:
                continue
            if fn.endswith('_en.py') or any(s.search(text) for s in LANG_SIGNAL):
                cands.append(rel)
    return cands


def coverage_violations(candidates, tracked, exempt):
    """Pure set logic (filesystem-free, so the selftest can exercise it directly)."""
    v = []
    for c in sorted(set(candidates) - set(tracked) - set(exempt)):
        v.append('coverage: %s is a language-aware pipeline file but is neither ledger-tracked nor '
                 'exempt — add a LANG_PARITY entry (SHARED / INTENTIONAL-DIVERGENCE / GAP), or list it '
                 'in the lang_parity_coverage `exempt` map with a one-line reason.' % c)
    for f, reason in sorted(exempt.items()):
        if not str(reason).strip():
            v.append('coverage: exempt file %s has an empty reason (name what it does + why no RU/EN '
                     'drift is possible)' % f)
        if f in set(tracked):
            v.append('coverage: %s is BOTH ledger-tracked and exempt — drop it from `exempt` (the '
                     'ledger entry is authoritative)' % f)
    return v


def coverage_check(entries, coverage):
    """Coverage guard: no language-aware pipeline file may escape the ledger unclassified."""
    tracked = {f for e in entries for f in e.get('files', [])}
    exempt = coverage.get('exempt', {}) or {}
    v = coverage_violations(candidate_files(), tracked, exempt)
    for f in sorted(exempt):
        if not os.path.exists(os.path.join(REPO_ROOT, f)):
            v.append('coverage: exempt file %s no longer exists — drop it from `exempt`' % f)
    return v


def file_sha256(rel_path):
    p = os.path.join(REPO_ROOT, rel_path)
    if not os.path.exists(p):
        return None
    # Normalize CRLF->LF so the hash matches the git-blob content regardless of
    # core.autocrlf on the checkout OS (Windows disk bytes vs Linux/CI bytes).
    data = open(p, 'rb').read().replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()


def check(entries):
    violations = []
    for e in entries:
        eid = e.get('id', '<missing id>')
        verdict = e.get('verdict')
        if verdict not in VALID_VERDICTS:
            violations.append('%s: verdict %r is not one of %s' % (eid, verdict, sorted(VALID_VERDICTS)))
            continue
        if verdict == 'INTENTIONAL-DIVERGENCE' and not e.get('note', '').strip():
            violations.append('%s: INTENTIONAL-DIVERGENCE requires a non-empty note (the one-line why)' % eid)
        if verdict == 'GAP' and not e.get('tracking', '').strip():
            violations.append('%s: GAP requires a non-empty tracking reference (task id / handoff / PR)' % eid)
        snapshot = e.get('verified_sha256', {})
        for rel_path in e.get('files', []):
            recorded = snapshot.get(rel_path)
            if recorded is None:
                violations.append('%s: file %s has no recorded verified_sha256 entry' % (eid, rel_path))
                continue
            current = file_sha256(rel_path)
            if current is None:
                violations.append('%s: tracked file %s no longer exists — update or retire this entry' % (eid, rel_path))
            elif current != recorded:
                violations.append(
                    '%s: %s changed since last parity verification (recorded %s..., now %s...) — '
                    're-check the %s verdict still holds, then run '
                    '`python src/pilot/lang_parity_check.py --update-hash %s`'
                    % (eid, rel_path, recorded[:12], current[:12], verdict, eid))
    return violations


def update_hash(entry_id, path=None):
    # load_ledger() refuses a repeated key BEFORE anything is rewritten: re-serializing here
    # would silently drop every copy but the last, which is the defect this gate reports.
    path = path or LEDGER_MD
    entries, text, span = load_ledger(path)
    found = False
    for e in entries:
        if e.get('id') == entry_id:
            found = True
            for rel_path in e.get('files', []):
                h = file_sha256(rel_path)
                if h is None:
                    raise SystemExit('cannot update-hash: %s no longer exists' % rel_path)
                e.setdefault('verified_sha256', {})[rel_path] = h
    if not found:
        raise SystemExit('no ledger entry with id %r' % entry_id)
    new_block = json.dumps(entries, indent=2, ensure_ascii=False)
    new_text = text[:span[0]] + new_block + '\n' + text[span[1]:]
    open(path, 'w', encoding='utf-8', newline='\n').write(new_text)
    print('updated verified_sha256 for %r' % entry_id)


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == '--update-hash':
        if len(argv) < 2:
            sys.exit('usage: --update-hash <entry_id>')
        update_hash(argv[1])
        return
    entries, _, _ = load_ledger()
    violations = check(entries) + coverage_check(entries, load_coverage())
    if violations:
        print('LANG PARITY LEDGER: %d violation(s)' % len(violations))
        for v in violations:
            print('  - ' + v)
        sys.exit(1)
    print('LANG PARITY LEDGER: %d entries, all verdicts complete, no drift; coverage: '
          '%d language-aware files, all tracked or exempt' % (len(entries), len(candidate_files())))


if __name__ == '__main__':
    main()
