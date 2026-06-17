#!/usr/bin/env python
"""NWS scraper — Nachtragswörterbuch des Sanskrit (Halle), rate-limited.

The site is a Rails app; the /search endpoint returns a JS response assigning
$nws_lemmas / $pw_lemmas / $sch_lemmas. Access requires a session cookie + the
csrf-token + the AJAX header. We keep ONLY the NWS fragment (the net-new value;
pw + Schmidt we already hold locally) and flag whether it adds anything beyond
pw/Schmidt. Polite: identified UA, sequential, configurable delay.

NOTE: NWS has no stated licence and rests on an old Cologne PW/Schmidt snapshot;
scraped output is gitignored and provisional pending the Halle data request.

  python nws_scrape.py [delay_s] [key1 ...]   default delay 3s, default 5 a-cards
"""
import os, re, sys, time, json
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


def main():
    args = sys.argv[1:]
    delay = 2.0
    for a in list(args):
        if a.replace('.', '').isdigit():
            delay = float(a); args.remove(a)
    if args and args[0] == 'section':
        words = section_keys(args[1] if len(args) > 1 else 'a')
    else:
        words = args or ['agni', 'arTa', 'aMSa', 'amfta', 'anna']
    os.makedirs(OUT, exist_ok=True)
    todo = [w for w in words if not os.path.exists(os.path.join(OUT, w + '.json'))]   # resumable
    s, token = session()
    if not token:
        sys.exit('could not establish session / csrf-token')
    print('session ok; %d headwords, %d already done, %d to fetch; delay %.1fs'
          % (len(words), len(words) - len(todo), len(todo), delay))
    n = extra_n = 0
    for w in todo:
        ia = iast(w)
        html = ''
        for attempt in (1, 2, 3):
            try:
                html = fetch(s, token, ia)
                # success = the JS result structure is present (an EMPTY result is
                # valid — '$nws_lemmas = $("");' — and must be kept, not retried);
                # only a Rails error page ('was rejected') is a real failure.
                if html and '_lemmas = $(' in html and 'was rejected' not in html[:2000]:
                    break
                html = ''
            except Exception:
                html = ''
            try:                                 # refresh session, tolerate failure
                s, token = session()
            except Exception:
                pass
            time.sleep(delay * 2)                # back off
        if not html:
            print('  skip %s (no result after retries; will retry next run)' % ia)
            time.sleep(delay); continue          # leave un-written → resumable retry
        nws, pw, sch = frag('nws', html), frag('pw', html), frag('sch', html)
        ex = bool(nws) and nws not in (pw, sch)
        json.dump({'key1': w, 'iast': ia, 'nws': nws, 'sch': sch,
                   'pw_len': len(pw), 'has_nws_extra': ex},
                  open(os.path.join(OUT, w + '.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        n += 1; extra_n += 1 if ex else 0
        if n % 50 == 0 or n <= 5:
            print('  [%d/%d] %-12s nws=%-4d %s  (NWS-extra so far: %d)'
                  % (n, len(todo), ia, len(nws), '★' if ex else ' ', extra_n))
        time.sleep(delay)
    print('done: fetched %d, with NWS-extra %d → %s' % (n, extra_n, OUT))


if __name__ == '__main__':
    main()
