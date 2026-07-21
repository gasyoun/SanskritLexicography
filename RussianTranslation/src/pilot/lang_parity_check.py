#!/usr/bin/env python
"""Mechanical gate for LANG_PARITY.md — see that doc for the policy this enforces.

  python src/pilot/lang_parity_check.py                       # check, exit 1 on any violation
  python src/pilot/lang_parity_check.py --update-hash <id>     # after re-verifying an entry,
                                                                # refresh its verified_sha256 snapshot

This does NOT diff behavior between languages — it only checks that every ledger
entry has a verdict (and the verdict's required field), and that no file a SHARED /
INTENTIONAL-DIVERGENCE / GAP entry depends on has drifted since it was last verified.
Drift means a human must re-open the entry and re-affirm (or correct) its verdict.
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


def load_ledger(path=LEDGER_MD):
    text = open(path, encoding='utf-8').read()
    m = FENCE_RE.search(text)
    if not m:
        raise SystemExit('no ```json lang_parity_ledger fenced block found in %s' % path)
    return json.loads(m.group(1)), text, m.span(1)


def load_coverage(path=LEDGER_MD):
    """Parse the optional lang_parity_coverage block ({exempt: {path: reason}}). Absent => {}."""
    m = COVERAGE_FENCE_RE.search(open(path, encoding='utf-8').read())
    return json.loads(m.group(1)) if m else {}


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


def update_hash(entry_id):
    entries, text, span = load_ledger()
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
    open(LEDGER_MD, 'w', encoding='utf-8', newline='\n').write(new_text)
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
