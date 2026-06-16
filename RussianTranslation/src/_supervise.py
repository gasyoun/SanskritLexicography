#!/usr/bin/env python
"""Self-healing supervisor for the corpus-lexicon build.

The background build process gets killed every ~1-2h by something external
(machine sleep / session reap of a long-running task) — NOT a code error: at
each death the build was mid-work with no traceback. Since buildall is resumable
(skips groups already in the lexicon), re-launching it continues from where it
stopped. This loop does that automatically until 2 consecutive runs add no new
groups (all done, or genuinely stuck).

  python _supervise.py
"""
import subprocess, json, os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, 'corpus_lexicon.jsonl')


def groups():
    s = set()
    if os.path.exists(LEX):
        for line in open(LEX, encoding='utf-8'):
            try:
                s.add(json.loads(line)['group'])
            except Exception:
                pass
    return len(s)


stall = run = 0
while True:
    run += 1
    before = groups()
    print('[supervise] run %d start: %d groups' % (run, before), flush=True)
    try:
        subprocess.run([sys.executable, '-u', 'build_corpus_lexicon.py', 'buildall', '12'], cwd=HERE)
    except Exception as e:
        print('[supervise] run %d crashed: %s' % (run, e), flush=True)
    after = groups()
    print('[supervise] run %d end: %d -> %d groups (+%d)' % (run, before, after, after - before), flush=True)
    if after <= before:
        stall += 1
        if stall >= 2:
            print('[supervise] no progress x2 -> stopping at %d groups' % after, flush=True)
            break
    else:
        stall = 0
    time.sleep(3)
print('[supervise] FINISHED at %d groups' % groups(), flush=True)
