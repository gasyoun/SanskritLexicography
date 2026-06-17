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
    r = s.get(BASE + '/?lang=en', timeout=20)
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


def main():
    args = sys.argv[1:]
    delay = float(args[0]) if args and args[0].replace('.', '').isdigit() else 3.0
    words = [a for a in args if not a.replace('.', '').isdigit()] or \
            ['agni', 'arTa', 'aMSa', 'amfta', 'anna']
    os.makedirs(OUT, exist_ok=True)
    s, token = session()
    if not token:
        sys.exit('could not establish session / csrf-token')
    print('session ok (csrf %s…), delay %.1fs' % (token[:10], delay))
    for w in words:
        ia = iast(w)
        try:
            html = fetch(s, token, ia)
        except Exception as e:
            print('  %s: fetch error %s' % (w, e)); time.sleep(delay); continue
        nws, pw, sch = frag('nws', html), frag('pw', html), frag('sch', html)
        extra = bool(nws) and nws not in (pw, sch)
        json.dump({'key1': w, 'iast': ia, 'nws': nws, 'sch': sch,
                   'pw_len': len(pw), 'has_nws_extra': extra},
                  open(os.path.join(OUT, w + '.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('%-10s %-10s nws=%-4d pw=%-4d sch=%-3d %s' %
              (w, ia, len(nws), len(pw), len(sch), '★ NWS-extra' if extra else ''))
        if nws:
            print('   NWS: %s' % nws[:140])
        time.sleep(delay)
    print('→ %s' % OUT)


if __name__ == '__main__':
    main()
