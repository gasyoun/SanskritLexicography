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

VALID_VERDICTS = {'SHARED', 'INTENTIONAL-DIVERGENCE', 'GAP'}


def load_ledger(path=LEDGER_MD):
    text = open(path, encoding='utf-8').read()
    m = FENCE_RE.search(text)
    if not m:
        raise SystemExit('no ```json lang_parity_ledger fenced block found in %s' % path)
    return json.loads(m.group(1)), text, m.span(1)


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
    violations = check(entries)
    if violations:
        print('LANG PARITY LEDGER: %d violation(s)' % len(violations))
        for v in violations:
            print('  - ' + v)
        sys.exit(1)
    print('LANG PARITY LEDGER: %d entries, all verdicts complete, no drift' % len(entries))


if __name__ == '__main__':
    main()
