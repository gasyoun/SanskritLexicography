#!/usr/bin/env python
r"""CI gate runner for pwg-ru-data pull requests (H2175 step 13, ruling R3.3).

Runs INSIDE a pwg-ru-data checkout (the gates.yml workflow), against the diff
``merge-base(base, HEAD)..HEAD``. Enforces the Lane-C landing contract:

  1. **Telemetry required** — a PR that touches ``tm/**`` MUST also add/modify a
     usage file under ``telemetry/`` (the usage-telemetry block; a cloud window
     that "forgot" its telemetry is refused, per the architecture risk table).
  2. **Deterministic card gates** — every added/modified ``wf_output*.json`` under
     ``gatelogs/`` must pass the store-corruption checks: non-empty ``russian`` on
     every sense, zero ``{Tn}`` mask residue, zero SAN-LOSS/UNMAPPED literals.
  3. **No store bypass** — a PR may stage cards in ``gatelogs/``, but ``tm/``
     content changes are the promoter's monopoly: flag tm changes for human/CI
     visibility (the label step downstream turns green only when 1-2 hold).

Exit 0 = gates green (workflow applies the ``gates-green`` label; auto-merge
consumes that in Wave 2). Any failure prints the exact violations and exits 1.
"""
import argparse
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# H2253 (#1073): the marker/residue scopes are DEFINED ONCE, in marker_scan, and shared
# with canary_gate. This runner used to json.dumps() the whole card for both checks, so
# the curated canary fixture — which carries the literal "SAN-LOSS" in its free-text
# ``notes`` by construction — failed CI here even after H2174 had taught canary_gate to
# pass it. Two gates, one card, two answers. See marker_scan's docstring for why the
# marker scope (translated content) and the {Tn} scope (whole card) must stay different.
import marker_scan  # noqa: E402

#: RussianTranslation/ — the root the committed canary fixtures are addressed from.
RT_ROOT = os.path.dirname(os.path.dirname(HERE))


def changed_files(base_ref, cwd='.'):
    proc = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=ACMR',
                           base_ref + '...HEAD'],
                          capture_output=True, text=True, encoding='utf-8', cwd=cwd)
    if proc.returncode:
        raise SystemExit('ci_gate_runner: git diff failed: %s' % proc.stderr[-500:])
    return [l.strip().replace('\\', '/') for l in proc.stdout.splitlines() if l.strip()]


def check_wf_payload(path):
    """Deterministic card checks on one wf_output file -> violation list."""
    violations = []
    try:
        wf = json.load(open(path, encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return ['%s: unreadable wf_output (%s)' % (path, exc)]
    results = wf.get('results') or []
    if not results:
        violations.append('%s: wf_output with zero results' % path)
    for r in results:
        key = r.get('key') or '?'
        card = r.get('card') or {}
        if marker_scan.tn_hits(card):
            violations.append('%s: %s carries unrestored {Tn} residue' % (path, key))
        if marker_scan.marker_hits(card):
            violations.append('%s: %s carries SAN-LOSS/UNMAPPED' % (path, key))
        for rec in card.get('records') or []:
            for sense in rec.get('senses') or []:
                if not sense.get('russian'):
                    violations.append('%s: %s has an empty russian sense (%s)'
                                      % (path, key, sense.get('tag')))
    usage = (wf.get('summary') or {}).get('usage')
    if not usage:
        violations.append('%s: missing summary.usage telemetry block' % path)
    return violations


def run_gates(files, cwd='.'):
    tm_changes = [f for f in files if f.startswith('tm/')]
    telemetry_changes = [f for f in files if f.startswith('telemetry/')]
    wf_payloads = [f for f in files
                   if f.startswith('gatelogs/') and 'wf_output' in os.path.basename(f)
                   and f.endswith('.json')]
    violations = []
    if tm_changes and not telemetry_changes:
        violations.append('tm/** changed (%d files) with NO telemetry/** in the same '
                          'PR — the usage-telemetry block is required (R3.3)'
                          % len(tm_changes))
    for f in wf_payloads:
        violations.extend(check_wf_payload(os.path.join(cwd, f)))
    return violations, {'tm': len(tm_changes), 'telemetry': len(telemetry_changes),
                        'wf_payloads': len(wf_payloads)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base', help='base ref (e.g. origin/main)')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.base:
        ap.error('--base is required')
    files = changed_files(args.base)
    violations, counts = run_gates(files)
    print('ci gates: %d changed files (%s)' % (len(files), counts))
    if violations:
        for v in violations:
            print('  ✗ %s' % v)
        return 1
    print('  ✓ gates green')
    return 0


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ok_wf = {'summary': {'usage': {'input_tokens': 1}}, 'results': [
            {'key': 'k', 'card': {'records': [{'senses': [
                {'tag': 's1', 'russian': 'да'}]}]}}]}
        bad_wf = {'summary': {}, 'results': [
            {'key': 'k2', 'card': {'records': [{'senses': [
                {'tag': 's1', 'russian': 'x {T3}'},
                {'tag': 's2', 'russian': ''}]}]}}]}
        os.makedirs(os.path.join(td, 'gatelogs'))
        for name, wf in (('wf_output.ok.json', ok_wf), ('wf_output.bad.json', bad_wf)):
            with open(os.path.join(td, 'gatelogs', name), 'w', encoding='utf-8',
                      newline='\n') as f:
                json.dump(wf, f, ensure_ascii=False)
        # (1) tm change without telemetry -> violation; with telemetry -> clean
        v1, _ = run_gates(['tm/pwg_ru_translated.jsonl'], cwd=td)
        assert v1 and 'usage-telemetry' in v1[0]
        v2, _ = run_gates(['tm/pwg_ru_translated.jsonl', 'telemetry/x.usage.jsonl'],
                          cwd=td)
        assert not v2, v2
        # (2) clean payload passes; dirty payload lists exact violations
        v3, c3 = run_gates(['gatelogs/wf_output.ok.json'], cwd=td)
        assert not v3 and c3['wf_payloads'] == 1
        v4, _ = run_gates(['gatelogs/wf_output.bad.json'], cwd=td)
        kinds = ' | '.join(v4)
        assert '{Tn}' in kinds and 'empty russian' in kinds and \
            'missing summary.usage' in kinds, v4
        # (3) unreadable payload is a violation, not a crash
        with open(os.path.join(td, 'gatelogs', 'wf_output.junk.json'), 'w',
                  encoding='utf-8') as f:
            f.write('{nope')
        v5, _ = run_gates(['gatelogs/wf_output.junk.json'], cwd=td)
        assert v5 and 'unreadable' in v5[0]

        # (4) #1073 REGRESSION, pinned on the REAL committed canary payloads — not a
        #     hand-written card. The previous selftest passed throughout the defect's
        #     life precisely because its fixtures carried no ``notes`` key at all, so
        #     a synthetic pin here would re-create that blind spot. Both files carry
        #     the literal "SAN-LOSS" in card.notes and clean translated content.
        for real in ('pwg_ru/h1447/h1447_canary_wf_output.json',
                     'pwg_ru/h2174/out.canary.json'):
            src = os.path.join(RT_ROOT, real)
            if not os.path.isfile(src):          # fixture pruned -> skip, never fake a pass
                print('  (skip %s — not in this checkout)' % real)
                continue
            card = json.load(open(src, encoding='utf-8'))['results'][0]['card']
            assert 'SAN-LOSS' in json.dumps(card, ensure_ascii=False), \
                '%s no longer self-describes — this regression needs a new fixture' % real
            assert not marker_scan.marker_hits(card), \
                '%s: free-text notes still trip the marker gate (#1073)' % real
            assert not marker_scan.tn_hits(card), real

        # (5) TRUE POSITIVE through the FULL runner path: a marker in translated
        #     content must still fail a payload, or (4) would just be a deleted check.
        loss_wf = {'summary': {'usage': {'input_tokens': 1}}, 'results': [
            {'key': 'k3', 'card': {'notes': 'clean', 'records': [{'senses': [
                {'tag': 's1', 'russian': 'SAN-LOSS'}]}]}}]}
        with open(os.path.join(td, 'gatelogs', 'wf_output.loss.json'), 'w',
                  encoding='utf-8', newline='\n') as f:
            json.dump(loss_wf, f, ensure_ascii=False)
        v6, _ = run_gates(['gatelogs/wf_output.loss.json'], cwd=td)
        assert any('SAN-LOSS/UNMAPPED' in x for x in v6), v6
    print('ci_gate_runner selftest: PASS (telemetry-required rule, card gates, '
          'unreadable-payload violation, #1073 real-canary regression + marker '
          'true-positive)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
