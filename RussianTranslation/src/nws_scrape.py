#!/usr/bin/env python
"""NWS scraper — Nachtragswörterbuch des Sanskrit (Halle), rate-limited.

The site is a Rails app; the /search endpoint returns a JS response assigning
$nws_lemmas / $pw_lemmas / $sch_lemmas. Access requires a session cookie + the
csrf-token + the AJAX header. We keep ONLY the NWS fragment (the net-new value;
pw + Schmidt we already hold locally) and flag whether it adds anything beyond
pw/Schmidt. Polite: identified UA, sequential, configurable delay.

NOTE: NWS has no stated licence and rests on an old Cologne PW/Schmidt snapshot;
scraped output is gitignored and provisional pending the Halle data request.

  python nws_scrape.py [delay_s] [key1 ...]            default 3s, 5 sample a-cards
  python nws_scrape.py section a 1                     whole a-section, 1s, 1 worker
  python nws_scrape.py section a 1 --workers 8         8 concurrent workers (~8 req/s)

Each worker keeps its OWN session (cookie+csrf); writes are atomic + resumable, so
parallel workers never collide and a reaped run continues from the cards on disk.
Be a good citizen: this is a small academic server — keep aggregate req/s modest.
"""
import os, re, sys, time, json, threading
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import requests
import corpus_gate as cg

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pilot', 'nws')
BASE = 'https://nws.uzi.uni-halle.de'
UA = 'pwg_ru-research/1.0 (Sanskrit lexicography, non-commercial; contact via samskrtam.ru)'
FRAG = re.compile(r'\$%s_lemmas = \$\("(.*?)"\);', re.S)


def iast(key1):
    return ''.join(cg._S2I.get(c, c) for c in cg.form_key(key1))


def safe_name(key1):
    """Case-collision-safe filename stem. SLP1 is case-sensitive (aMSa != AMSa,
    s != S=ś) but Windows filesystems are case-INSENSITIVE, so the raw key as a
    filename silently merges case variants. Encode each uppercase letter as '_'+
    lowercase ('_' never occurs in SLP1 keys) → an all-lowercase, injective stem
    with no case-insensitive collisions. aMSa→a_m_sa, AMSa→_a_m_sa."""
    return ''.join('_' + c.lower() if c.isupper() else c for c in key1)


def session():
    s = requests.Session()
    s.headers['User-Agent'] = UA
    r = s.get(BASE + '/?lang=en', timeout=30)
    m = re.search(r'name="csrf-token" content="([^"]+)"', r.text)
    return s, (m.group(1) if m else '')


def fetch(s, token, word):
    r = s.get(BASE + '/search', params={'utf8': '✓', 'q': word, 'lang': 'en'},
              headers={'X-CSRF-Token': token, 'X-Requested-With': 'XMLHttpRequest',
                       'Referer': BASE + '/?lang=en'}, timeout=30)
    return r.text


def frag(name, html):
    m = re.compile(r'\$%s_lemmas = \$\("(.*?)"\);' % name, re.S).search(html)
    if not m:
        return ''
    s = m.group(1).replace('\\n', ' ').replace('\\"', '"').replace('\\/', '/').replace("\\'", "'")
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def section_keys(section):
    """All SLP1 form-keys for a letter-section across the 4 local layers (the
    complete set we'd translate). Cached to a file so reap-restarts are instant
    (rebuilding the 4 dict indexes costs ~90s)."""
    os.makedirs(OUT, exist_ok=True)
    cache = os.path.join(OUT, '_keys_%s.txt' % section)
    if os.path.exists(cache):
        return [l.strip() for l in open(cache, encoding='utf-8') if l.strip()]
    import dict_merge as dm
    keys = set()
    for code, _, _ in dm.LAYERS:
        for k in dm.index(code):
            if k and (section == 'all' or k[:1].lower() == section.lower()):
                keys.add(k)
    keys = sorted(keys)
    open(cache, 'w', encoding='utf-8').write('\n'.join(keys))
    return keys


# --- per-thread session (requests.Session is not safe to share across threads) ---
_tl = threading.local()


def tl_session(force=False):
    s = getattr(_tl, 's', None)
    if force or s is None:
        _tl.s, _tl.tok = session()
    return _tl.s, _tl.tok


def scrape_one(word, delay):
    """Fetch + write one headword. Thread-safe (own session, atomic write).
    Returns 'extra' / 'plain' / 'skip' (skip = no result; left un-written → retried)."""
    out_path = os.path.join(OUT, safe_name(word) + '.json')
    if os.path.exists(out_path):
        return 'plain'
    ia = iast(word)
    html = ''
    for _ in (1, 2, 3):
        try:
            s, tok = tl_session()
            html = fetch(s, tok, ia)
            # an EMPTY result ('$nws_lemmas = $("");') is valid — keep it; only a
            # Rails error page ('was rejected') is a real failure.
            if html and '_lemmas = $(' in html and 'was rejected' not in html[:2000]:
                break
            html = ''
        except Exception:
            html = ''
        try:
            tl_session(force=True)               # refresh session, tolerate failure
        except Exception:
            pass
        time.sleep(delay * 2)                    # back off
    if not html:
        time.sleep(delay)
        return 'skip'                            # leave un-written → resumable retry
    nws, pw, sch = frag('nws', html), frag('pw', html), frag('sch', html)
    ex = bool(nws) and nws not in (pw, sch)
    tmp = out_path + '.%d.tmp' % threading.get_ident()   # per-thread tmp name
    with open(tmp, 'w', encoding='utf-8') as f:           # close BEFORE replace
        json.dump({'key1': word, 'iast': ia, 'nws': nws, 'sch': sch,
                   'pw_len': len(pw), 'has_nws_extra': ex}, f,
                  ensure_ascii=False, indent=1)
    for _ in range(6):                                    # atomic; retry transient Win locks
        try:
            os.replace(tmp, out_path)
            break
        except PermissionError:
            time.sleep(0.2)
    else:
        try:
            os.remove(tmp)
        except OSError:
            pass
        time.sleep(delay)
        return 'skip'
    time.sleep(delay)
    return 'extra' if ex else 'plain'


def main():
    args = sys.argv[1:]
    workers = 1
    if '--workers' in args:
        i = args.index('--workers')
        workers = int(args[i + 1]); del args[i:i + 2]
    delay = 2.0
    for a in list(args):
        if a.replace('.', '').isdigit():
            delay = float(a); args.remove(a)
    if args and args[0] == 'section':
        words = section_keys(args[1] if len(args) > 1 else 'a')
    else:
        words = args or ['agni', 'arTa', 'aMSa', 'amfta', 'anna']
    os.makedirs(OUT, exist_ok=True)
    todo = [w for w in words if not os.path.exists(os.path.join(OUT, safe_name(w) + '.json'))]   # resumable
    s, token = session()                          # validate connectivity up front
    if not token:
        sys.exit('could not establish session / csrf-token')
    print('session ok; %d headwords, %d done, %d to fetch; %d worker(s), %.1fs/req each (~%.1f req/s)'
          % (len(words), len(words) - len(todo), len(todo), workers, delay, workers / max(delay, 0.1)))
    counts = {'extra': 0, 'plain': 0, 'skip': 0}
    lock = threading.Lock()
    done = [0]

    def run(w):
        try:
            r = scrape_one(w, delay)
        except Exception:
            r = 'skip'                            # never let one word kill the pool
        with lock:
            counts[r] += 1
            done[0] += 1
            if done[0] % 100 == 0:
                print('  [%d/%d] extra=%d skip=%d'
                      % (done[0], len(todo), counts['extra'], counts['skip']))
                sys.stdout.flush()

    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            list(ex.map(run, todo))
    else:
        for w in todo:
            run(w)
    print('done: %d fetched (NWS-extra %d), %d skipped → %s'
          % (counts['extra'] + counts['plain'], counts['extra'], counts['skip'], OUT))


if __name__ == '__main__':
    main()
