#!/usr/bin/env python
"""June-22 real-conditions pilot test driver — run on YOUR machine when the Max
subscription quota resets. Two phases, one command each:

  python run_real_test.py prep [N] [OFFSET]   # default N=10, OFFSET=0
      Picks the batch = scale_manifest.a.json[OFFSET : OFFSET+N], reports which
      cards are FRESH (no pilot/output/<key>.merged.md) vs protected (hand-authored
      aMSa/anna/ap), writes the batch to _realtest_batch.json, and sets OFFSET/LIMIT
      in run_pilot_wf.js so the workflow translates exactly that window.

  --- then run the translate→judge workflow on your Max ---
      run_pilot_wf.js is a Claude Code workflow (agent()/pipeline()/phase()); run it
      through your usual workflow harness and SAVE its JSON result to wf_output.json.
      (This driver cannot invoke the Max-subscription harness for you.)

  python run_real_test.py audit wf_output.json
      Renders cards via _pilot_collect.py directly to <safe>.merged.md (never
      overwriting a protected hand-authored card), runs `nws_split.py check` on each,
      and reports: judge pass rate + NWS-attribution (F12) clean count + any misattrib.

      GATE: a fresh card whose NWS owners disagree with the deterministic
      nws_split parse (F12 slide) is REJECTED — its <safe>.merged.md is moved
      aside to <safe>.merged.REJECTED.md (so merged_exists() treats it as
      not-done and the next `prep` re-queues it) and the command exits non-zero.
      Protected hand-authored cards are audited but never quarantined.

Context: on 2026-06-19 the loop was validated manually on card `ap` (nws_split audit
CLEAN); run_pilot_wf.js HARD RULE 5 now encodes the NWS one-row-per-owner format the
auditor needs. See .ai_state.md / changelog [Unreleased].
"""
import os, re, sys, json, subprocess

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))          # .../src/pilot
SRC = os.path.dirname(HERE)                                 # .../src
sys.path.insert(0, SRC)

from safe_filename import safe_name

OUT = os.path.join(HERE, 'output')
MANIFEST = os.path.join(OUT, 'scale_manifest.a.json')
WF = os.path.join(HERE, 'run_pilot_wf.js')
BATCH_FILE = os.path.join(OUT, '_realtest_batch.json')
COLLECT = os.path.join(SRC, '_pilot_collect.py')
NWS_SPLIT = os.path.join(SRC, 'nws_split.py')
PROTECTED = {'aMSa', 'anna', 'ap'}                          # hand-authored — never overwrite


def exact_file_exists(directory, name):
    """Case-sensitive existence check, even on case-insensitive filesystems."""
    try:
        return name in set(os.listdir(directory))
    except OSError:
        return False


def merged_exists(key):
    return (exact_file_exists(OUT, safe_name(key) + '.merged.md')
            or exact_file_exists(OUT, key + '.merged.md'))


def quarantine(key):
    """Move a slid card aside so merged_exists() treats it as not-done and the
    next prep re-queues it. Returns True if a card file was moved."""
    for nm in (safe_name(key) + '.merged.md', key + '.merged.md'):
        if exact_file_exists(OUT, nm):
            src = os.path.join(OUT, nm)
            dst = os.path.join(OUT, nm[:-len('.merged.md')] + '.merged.REJECTED.md')
            if os.path.exists(dst):
                os.remove(dst)
            os.replace(src, dst)
            return True
    return False


def find_results(o):
    if isinstance(o, dict):
        if isinstance(o.get('results'), list):
            return o['results']
        for v in o.values():
            r = find_results(v)
            if r is not None:
                return r
    if isinstance(o, list):
        for v in o:
            r = find_results(v)
            if r is not None:
                return r
    return None


def cmd_prep(args):
    n = int(args[0]) if len(args) > 0 else 10
    offset = int(args[1]) if len(args) > 1 else 0
    if not os.path.exists(MANIFEST):
        sys.exit('no %s — run: python scale_route.py a' % os.path.basename(MANIFEST))
    keys = [e['key1'] for e in json.load(open(MANIFEST, encoding='utf-8'))]
    batch = keys[offset:offset + n]
    if not batch:
        sys.exit('empty batch (offset %d beyond %d keys)' % (offset, len(keys)))

    fresh = [k for k in batch if not merged_exists(k) and k not in PROTECTED]
    prot = [k for k in batch if k in PROTECTED or merged_exists(k)]
    json.dump({'offset': offset, 'limit': n, 'batch': batch, 'fresh': fresh,
               'protected': prot}, open(BATCH_FILE, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    # write OFFSET/LIMIT into the workflow so it translates exactly this window
    js = open(WF, encoding='utf-8').read()
    js2 = re.sub(r'const OFFSET = \d+', 'const OFFSET = %d' % offset, js, count=1)
    js2 = re.sub(r'const LIMIT = \d+', 'const LIMIT = %d' % n, js2, count=1)
    if js2 != js:
        open(WF, 'w', encoding='utf-8').write(js2)

    print('=== PREP: a-section batch [%d, %d) — %d card(s) ===' % (offset, offset + n, len(batch)))
    print('  batch    :', ' '.join(batch))
    print('  fresh    : %d (%s)' % (len(fresh), ' '.join(fresh) or '—'))
    print('  protected: %d (%s)  ← will NOT be overwritten' % (len(prot), ' '.join(prot) or '—'))
    print('  run_pilot_wf.js set to OFFSET=%d LIMIT=%d' % (offset, n))
    print('  batch saved → %s' % os.path.basename(BATCH_FILE))
    print('\nNEXT (on your Max):')
    print('  1) run the workflow run_pilot_wf.js through your harness; save its JSON → wf_output.json')
    print('  2) python run_real_test.py audit wf_output.json')


def _run(argv, protected=None):
    env = os.environ.copy()
    env['PILOT_COLLECT_PROTECTED'] = ','.join(sorted(protected or PROTECTED))
    return subprocess.run([sys.executable] + argv, cwd=SRC, capture_output=True,
                          text=True, encoding='utf-8', env=env)


def cmd_audit(args):
    if not args:
        sys.exit('usage: python run_real_test.py audit <wf_output.json>')
    wf_out = args[0]
    if not os.path.exists(wf_out):
        sys.exit('no workflow output %r' % wf_out)
    batch_meta = json.load(open(BATCH_FILE, encoding='utf-8')) if os.path.exists(BATCH_FILE) else {}
    batch = batch_meta.get('batch')
    protected = PROTECTED | set(batch_meta.get('protected') or [])

    # 1) render cards + judge summary
    print('=== 1. collect (render + judge summary) ===')
    r = _run([COLLECT, os.path.abspath(wf_out)], protected=protected)
    print(r.stdout.rstrip())
    if r.returncode:
        print(r.stderr.rstrip()); sys.exit('collect failed')

    # which keys were produced (from the workflow output)
    raw = json.load(open(wf_out, encoding='utf-8'))
    res = find_results(raw) or []
    keys = [c.get('key') for c in res if c.get('key')] or (batch or [])

    # 2) _pilot_collect.py writes <safe>.merged.md directly. For protected
    #    hand-authored cards, audit the existing card but never overwrite it.
    print('\n=== 2. NWS attribution audit (nws_split) ===')
    clean = misattr = noidx = 0
    bad_cards, rejected = [], []
    for k in keys:
        if k in protected:
            print('  %-12s protected — keeping hand-authored card' % k)
        a = _run([NWS_SPLIT, 'check', k], protected=protected)
        out = a.stdout + a.stderr
        verdict = ('CLEAN' if 'CLEAN' in out else
                   'MISATTRIBUTION' if 'MISATTRIBUTION' in out else
                   'NO-NWS' if 'no NWS fragment' in out else '??')
        tail = out.strip().splitlines()[-1] if out.strip() else ''
        print('  %-12s %s' % (k, tail or verdict))
        if verdict == 'CLEAN':
            clean += 1
        elif verdict == 'MISATTRIBUTION':
            misattr += 1; bad_cards.append(k)
            if k not in protected and quarantine(k):   # GATE: reject the slid card
                rejected.append(k)
        else:
            noidx += 1

    print('\n=== REPORT ===')
    print('  cards audited      : %d' % len(keys))
    print('  NWS audit CLEAN    : %d' % clean)
    print('  F12 misattribution : %d %s' % (misattr, ('→ ' + ' '.join(bad_cards)) if bad_cards else ''))
    print('  no-NWS / other     : %d' % noidx)
    print('  judge pass rate    : see "publishable" line in section 1 above')

    gate_fail = [k for k in bad_cards if k not in protected]
    if gate_fail:
        print('\n  GATE: FAIL — %d card(s) rejected (F12 slide): %s' % (len(rejected), ' '.join(rejected)))
        if any(k in protected for k in bad_cards):
            print('  (note: %s is protected & misattributed — fix the hand-authored card by hand)'
                  % ' '.join(k for k in bad_cards if k in protected))
        sys.exit(1)
    print('\n  GATE: PASS — no F12 misattribution in fresh cards')


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'prep':
        cmd_prep(sys.argv[2:])
    elif cmd == 'audit':
        cmd_audit(sys.argv[2:])
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
