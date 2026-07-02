#!/usr/bin/env python3
"""Probe the §41 dictionary-platform landscape and write platform_status.json.

MUST run from the residential machine — GitHub Actions datacenter IPs are
blocked by several of these hosts (Uprava FINDINGS §1), so a GHA probe would
report false negatives. Scheduled monthly via Windows Task Scheduler through
monthly_refresh.py.

A non-200 verdict from THIS host is still ambiguous (host-specific blocks);
the dashboard labels results "as seen from the probe host".
"""

import json
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent

# The 12 platforms live-profiled in FINDINGS §41 (kosha/COMPARISON.md, 2026-07-02).
PLATFORMS = [
    ('michaelmeyer.fr (41 dicts)', 'https://michaelmeyer.fr/sanskrit'),
    ('CDSL simple search', 'https://www.sanskrit-lexicon.uni-koeln.de/simple/'),
    ('CDSL home', 'https://www.sanskrit-lexicon.uni-koeln.de/'),
    ('Heritage (Inria)', 'https://sanskrit.inria.fr/DICO/index.en.html'),
    ('Heritage mirror (UoHyd)', 'https://sanskrit.uohyd.ac.in/scl/'),
    ('DCS (plain HTTP; cert broken)', 'http://www.sanskrit-linguistics.org/dcs/'),
    ('VedaWeb (Tekst)', 'https://vedaweb.uni-koeln.de/'),
    ('learnsanskrit.cc', 'https://learnsanskrit.cc/'),
    ('spokensanskrit.org (301 expected)', 'https://spokensanskrit.org/'),
    ('learnsanskrit.org/dictionary (404 expected)', 'https://learnsanskrit.org/dictionary'),
    ('Ambuda dictionaries', 'https://ambuda.org/tools/dictionaries'),
    ('sanskritdictionary.com', 'https://sanskritdictionary.com/'),
]

UA = 'Mozilla/5.0 (findings-dashboard liveness probe; github.com/gasyoun/SanskritLexicography)'


def probe(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            ms = int((time.time() - t0) * 1000)
            final = r.geturl()
            moved = urlsplit(final).netloc != urlsplit(url).netloc
            return {'verdict': 'moved' if moved else 'ok',
                    'http': r.status, 'final_url': final, 'ms': ms}
    except urllib.error.HTTPError as e:
        return {'verdict': f'http-{e.code}', 'http': e.code,
                'ms': int((time.time() - t0) * 1000)}
    except urllib.error.URLError as e:
        reason = e.reason
        kind = ('tls-error' if isinstance(reason, ssl.SSLError)
                else 'timeout' if isinstance(reason, (socket.timeout, TimeoutError))
                else 'unreachable')
        return {'verdict': kind, 'error': str(reason)[:120]}
    except Exception as e:  # noqa: BLE001 — a liveness probe never crashes the run
        return {'verdict': 'error', 'error': f'{e.__class__.__name__}: {e}'[:120]}


def main():
    results = []
    for name, url in PLATFORMS:
        r = {'name': name, 'url': url}
        r.update(probe(url))
        print(f"  {r['verdict']:<12} {name}")
        results.append(r)
    out = {'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
           'probe_host': 'residential (local machine)', 'results': results}
    (HERE / 'platform_status.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    ok = sum(1 for r in results if r['verdict'] == 'ok')
    print(f'platform_status.json: {ok}/{len(results)} ok')


if __name__ == '__main__':
    main()
