import json, os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
TOTAL = 78139                    # verse-groups (sa+ru) across the whole corpus
COST_PER_ALIGN = 6.0 / 133838   # empirical DeepSeek $/alignment
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corpus_lexicon.jsonl')


def stat():
    if not os.path.exists(P):
        return 0, 0
    groups, n = set(), 0
    for line in open(P, encoding='utf-8'):
        try:
            groups.add(json.loads(line)['group']); n += 1
        except Exception:
            pass
    return len(groups), n


def bar(pct, w=22):
    f = int(round(w * pct / 100.0))
    return '[' + '#' * f + '·' * (w - f) + ']'


def emit(tag, g, n, t0, g0, n0):
    # rate / eta measured over THIS watch window (t0,g0,n0) — never the
    # append-only file's stale ctime. spent = cumulative real $ on disk.
    el = max(time.time() - t0, 1e-9)
    dg = g - g0
    pct = 100.0 * g / TOTAL
    spent = n * COST_PER_ALIGN
    if dg > 0:
        rate = dg / el                                  # groups/sec, live
        eta_h = (TOTAL - g) / rate / 3600.0
        apg = (n - n0) / dg                             # align/group, live window
        need = (TOTAL - g) * apg * COST_PER_ALIGN       # $ still to spend
        tail = 'rate=%.0f grp/min  eta=%.1fh  need=$%.2f  total=$%.2f' % (
            rate * 60, eta_h, need, spent + need)
    else:
        tail = 'rate=… (warming up)'
    print('%s %s %.1f%%  g=%d/%d  n=%d  spent=$%.2f  %s'
          % (tag, bar(pct), pct, g, TOTAL, n, spent, tail))


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else 'now'
    g0, n0 = stat()
    t0 = time.time()
    if arg == 'now':
        # quick honest snapshot: 25 s self-window to measure a live rate
        time.sleep(25)
        g, n = stat(); emit('NOW', g, n, t0, g0, n0); sys.exit()
    target = float(arg)
    last, stale = n0, 0
    while True:
        time.sleep(30)
        g, n = stat()
        if 100.0 * g / TOTAL >= target:
            emit('MILESTONE', g, n, t0, g0, n0); break
        stale = stale + 1 if n == last else 0
        last = n
        if stale >= 12:                                 # ~6 min no growth → done/stalled
            emit('STALLED', g, n, t0, g0, n0); break
        emit('···', g, n, t0, g0, n0)
