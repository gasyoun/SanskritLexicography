#!/usr/bin/env python3
"""Monthly scripted re-probe of the 13 class-B findings (verifiability.json).

Every class-B row of epistemic_dashboard/verifiability.json holds a claim about a
live external host (the H1362 ruling's "B — re-probeable" class). This tool runs
each row's own re-probe recipe as a cheap scripted check and writes the verdict +
last-verified stamp back per row (`reprobe` key), so a B-row claim can never go
silently stale — the failure mode this lane exists to defeat (H7593). A `stale`
verdict is data recorded loudly, not a crash: the monthly refresh commits it and
the findings dashboard renders it.

MUST run from the residential machine — several target hosts (Cologne, Inria,
archive.org pair routes) treat datacenter IPs differently (Uprava FINDINGS §1;
same constraint as findings_dashboard/probe_platforms.py). Wired monthly via
findings_dashboard/monthly_refresh.py.

Verdict vocabulary:
  verified     live probe reproduces the claim's true-signature
  stale        host answered, but the claim's signature changed — finding needs
               re-adjudication (recorded loudly in the dashboard)
  inconclusive network/runtime failure — no evidence about the claim; the row
               simply keeps its previous stamp until a run sees it

archive.org rows follow FINDINGS §651 mechanics: paired same-date items (the
correct-labelled one may be darked — the sibling is the route), 504-retries, and
"verify the masthead, never the item id".
"""

import json
import os
import re
import shutil
import subprocess
import ssl
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
VERIF = REPO / 'epistemic_dashboard' / 'verifiability.json'

UA = 'Mozilla/5.0 (b-class reprobe; github.com/gasyoun/SanskritLexicography)'

VERDICTS = ('verified', 'stale', 'inconclusive')
B_IDS = ['41', '47', '48', '49', '50', '56', '57', '68', '75', '95', '448',
         '451', '652']

# FINDINGS §651 fetch mechanics: 504 waves get 4 attempts with 4-10 s sleeps.
ARCHIVE_RETRIES = 4
ARCHIVE_SLEEP = (4, 10)


def http_get(url, timeout=30, retries=1, sleep=(2, 6), headers=None):
    """GET with §651-style retries on 504/503/timeouts; returns (status, body, final_url)."""
    last = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers={'User-Agent': UA, **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read().decode('utf-8', 'replace'), r.geturl()
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'replace')[:2000]
            if e.code in (503, 504) and attempt < retries:
                last = f'HTTP {e.code} (attempt {attempt + 1})'
                time.sleep(sleep[0])
                continue
            return e.code, body, url
        except (urllib.error.URLError, socket.timeout, TimeoutError,
                ssl.SSLError, ConnectionError, OSError) as e:
            last = f'{e.__class__.__name__}: {str(e)[:120]}'
            if attempt < retries:
                time.sleep(sleep[0])
                continue
    raise RuntimeError(f'{url}: {last}')


def http_post_json(url, payload, timeout=90):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode('utf-8'),
        headers={'User-Agent': UA, 'Content-Type': 'application/json'},
        method='POST')
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode('utf-8', 'replace')


def gh_api(path):
    """GitHub API GET; attaches `gh auth token` / GITHUB_TOKEN when available (the
    unauthenticated 60/h cap is shared across the whole egress IP — the fleet IP
    burns it; FINDINGS §659 queue machinery hits the same wall). Legible failures."""
    headers = {'User-Agent': UA}
    tok = (os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
           or shutil.which('gh') and subprocess.run(
               ['gh', 'auth', 'token'], capture_output=True, text=True,
               timeout=10).stdout.strip() or '')
    if tok:
        headers['Authorization'] = 'Bearer ' + tok
    st, body, _ = http_get('https://api.github.com' + path, timeout=25, headers=headers)
    try:
        d = json.loads(body)
    except ValueError:
        raise RuntimeError(f'{path}: non-JSON ({body[:120]})')
    if isinstance(d, dict) and d.get('message') and 'rate limit' in d['message'].lower():
        raise RuntimeError(f'{path}: {d["message"][:160]}')
    return d


def gh_dir_listing(repo, dirpath, ref=None):
    p = f'/repos/{repo}/contents/{dirpath}' + (f'?ref={ref}' if ref else '')
    items = gh_api(p)
    if not isinstance(items, list):
        raise RuntimeError(f'{repo}/{dirpath}: not a dir listing')
    return items


def stamp():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def verify(cond):
    return 'verified' if cond else 'stale'



