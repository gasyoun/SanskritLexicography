#!/usr/bin/env python
"""NWS-scrape watcher — emits a status bar every N% (default 5%).

Counts the gitignored cards in pilot/nws/*.json against the cached key list,
measures a LIVE rate window (never trusts a frozen mtime — a reaped scrape looks
"done" by elapsed time), and prints a bar each time it crosses a new bucket.

  python _nws_watch.py                 watch the a-section, bar each 5%
  python _nws_watch.py 10              bar each 10%
  python _nws_watch.py --once          print the current bar once and exit
  python _nws_watch.py --supervise     also relaunch the scrape if it stalls

State (last bucket + rate samples) persists to pilot/nws/_watch_state.json, so a
reaped/restarted watcher resumes its bucket tracking instead of re-announcing.
"""
import os, sys, json, time, glob, collections, subprocess
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pilot', 'nws')
STATE = os.path.join(OUT, '_watch_state.json')
KEYS = os.path.join(OUT, '_keys_a.txt')
POLL = 30          # seconds between samples
STALL = 180        # seconds with no new write → consider the scrape dead
RELAUNCH = ['python', 'nws_scrape.py', 'section', 'a', '1']


def snapshot():
    fs = glob.glob(os.path.join(OUT, '*.json'))
    n = len(fs)
    extra = 0
    for f in fs:
        try:
            if json.load(open(f, encoding='utf-8')).get('has_nws_extra'):
                extra += 1
        except Exception:
            pass
    newest = (time.time() - max(os.path.getmtime(f) for f in fs)) if fs else 1e9
    total = sum(1 for _ in open(KEYS, encoding='utf-8')) if os.path.exists(KEYS) else 0
    return n, extra, newest, total


def bar(pct, width=40):
    fill = int(round(width * pct / 100))
    return '[' + '#' * fill + '·' * (width - fill) + ']'


def fmt_eta(sec):
    if sec is None or sec == float('inf'):
        return '—'
    h, rem = divmod(int(sec), 3600)
    m, _ = divmod(rem, 60)
    return ('%dh%02dm' % (h, m)) if h else ('%dm' % m)


def line(n, extra, newest, total, rate_cpm, eta, tag=''):
    pct = 100 * n / total if total else 0
    stall = '  ⚠ STALLED (no write %.0fs — relaunch: python nws_scrape.py section a 1)' % newest if newest > STALL else ''
    ex = ('%d (%.0f%%)' % (extra, 100 * extra / n)) if n else '0'
    print('%s %s %5.1f%%  %d/%d  NWS-extra %s  %.0f cards/min  ETA %s%s%s'
          % (time.strftime('%H:%M:%S'), bar(pct), pct, n, total, ex,
             rate_cpm, fmt_eta(eta), ('  '+tag) if tag else '', stall))
    sys.stdout.flush()


def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE, encoding='utf-8'))
        except Exception:
            pass
    return {'last_bucket': -1, 'samples': []}


def save_state(st):
    json.dump(st, open(STATE, 'w', encoding='utf-8'))


def rate_eta(samples, n, total):
    """cards/min over the live window + ETA to total."""
    if len(samples) >= 2:
        (t0, c0), (t1, c1) = samples[0], samples[-1]
        dt, dc = t1 - t0, c1 - c0
        if dt > 0 and dc > 0:
            cpm = 60 * dc / dt
            eta = (total - n) / (dc / dt) if total > n else 0
            return cpm, eta
    return 0.0, None


def main():
    args = sys.argv[1:]
    once = '--once' in args
    supervise = '--supervise' in args
    step = next((float(a) for a in args if a.replace('.', '').isdigit()), 5.0)

    if once:
        n, extra, newest, total = snapshot()
        cpm, eta = rate_eta(load_state().get('samples', []), n, total)
        line(n, extra, newest, total, cpm, eta)
        return

    st = load_state()
    samples = collections.deque(st.get('samples', []), maxlen=20)
    print('watching NWS a-section, bar every %g%%%s (Ctrl-C to stop)'
          % (step, '  [supervise on]' if supervise else ''))
    while True:
        n, extra, newest, total = snapshot()
        if not total:
            print('no key cache yet — start the scrape first'); return
        samples.append([time.time(), n])
        st['samples'] = list(samples)
        cpm, eta = rate_eta(samples, n, total)
        bucket = int((100 * n / total) // step)
        if bucket > st.get('last_bucket', -1):
            line(n, extra, newest, total, cpm, eta, tag='◆ %g%% mark' % (bucket * step))
            st['last_bucket'] = bucket
        save_state(st)
        if n >= total:
            line(n, extra, newest, total, cpm, eta, tag='✅ COMPLETE')
            return
        if supervise and newest > STALL:
            print('  ↻ stalled — relaunching scrape')
            subprocess.Popen(RELAUNCH, cwd=HERE)
            time.sleep(POLL)
        time.sleep(POLL)


if __name__ == '__main__':
    main()
