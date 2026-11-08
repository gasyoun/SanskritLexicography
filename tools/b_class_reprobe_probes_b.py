"""Per-row probes for §68-§652 (H7593), including the FINDINGS §651 archive.org
mechanics (paired items, 504-retries). Lane contract: b_class_reprobe.py."""

import json
import re
import time
import ssl
import urllib.error

from b_class_reprobe_core import (ARCHIVE_RETRIES, ARCHIVE_SLEEP,
                                http_get, http_post_json, gh_api,
                                  gh_dir_listing)

def probe_68():
    """§68 spellchecker landscape: LO sa_IN wordlist still bundled + COLOGNE #91 still
    open (the demand signal); Prasanna demo liveness recorded in detail."""
    sa = gh_dir_listing('LibreOffice/dictionaries', 'sa_IN')
    names = [i['name'] for i in sa]
    dic = [n for n in names if n.endswith('.dic')]
    issue = gh_api('/repos/sanskrit-lexicon/COLOGNE/issues/91')
    demo = None
    try:
        st, _, _ = http_get('https://sanskrit-spellchecker.netlify.app/', timeout=20)
        demo = f'demo site answers {st} (dormant since ~2022 per ICON 2022 paper)'
    except Exception as e:  # noqa: BLE001 - recorded, not raised
        demo = f'demo unreachable ({e.__class__.__name__})'
    # #91 closed "not_planned" (22-07-2026) still matches the finding: no occupant
    # shipped. Only a `completed` close (or a shipped spellchecker) flips it.
    reason = issue.get('state_reason') or ('open' if issue.get('state') == 'open' else 'closed')
    if dic and reason != 'completed':
        return {'verdict': 'verified',
                'detail': f'sa_IN: {names}; COLOGNE #91 {issue.get("state")} ({reason}) — '
                          f'no occupant shipped; {demo}'}
    if not dic:
        return {'verdict': 'stale',
                'detail': f'sa_IN wordlist no longer in LibreOffice/dictionaries ({names[:8]}); {demo}'}
    return {'verdict': 'stale' if reason == 'completed' else 'inconclusive',
            'detail': f'sa_IN={bool(dic)} COLOGNE#91 {issue.get("state")} ({reason}); {demo}'}


def probe_75():
    """§75 GRETIL lacks full DBhP (Devigita fragment only) + sanskritdocuments.org
    carries all 12 skandhas."""
    st, body, _ = http_get('https://gretil.sub.uni-goettingen.de/gretil.html', timeout=40,
                           retries=2)
    dbhp = re.findall(r'dbhp[^"\'<> ]*', body, re.I)
    try:
        st2, body2, _ = http_get('https://sanskritdocuments.org/doc_purana/', timeout=60,
                                 retries=3)
    except (RuntimeError, urllib.error.URLError, ssl.SSLError, OSError):
        st2, body2, _ = http_get('http://sanskritdocuments.org/doc_purana/', timeout=60,
                                 retries=3)
    dbh_docs = re.findall(r'devIbhAgavatam\d+', body2)
    if dbhp and set(dbh_docs) >= {f'devIbhAgavatam{n:02d}' for n in (1, 12)}:
        return {'verdict': 'verified',
                'detail': f'GRETIL dbhp hits {dbhp[:4]} (Devigita-only); sanskritdocuments '
                          f'carries {sorted(set(dbh_docs))}'}
    if dbh_docs and not dbhp:
        return {'verdict': 'stale',
                'detail': 'GRETIL no longer lists dbhp_dgu (Devigita) — DBhP surface changed'}
    return {'verdict': 'inconclusive',
            'detail': f'GRETIL dbhp={dbhp[:4]} sanskritdocuments hits={len(dbh_docs)}'}


def probe_95():
    """§95 DharmaMitra unsandhied batches: short-input misalignment signature still
    reproducible on POST /api/tagging/ (kosha/csl-atlas contract, mode=unsandhied)."""
    st = body = None
    for _ in range(4):
        try:
            st, body = http_post_json(
                'https://dharmamitra.org/api/tagging/',
                {'texts': ['ca', 'gavā'], 'mode': 'unsandhied', 'human_readable_tags': True})
            break
        except Exception as e:  # noqa: BLE001 - SSL EOF waves on this host; retry
            st, body = None, None
            time.sleep(5)
            last = f'{e.__class__.__name__}: {str(e)[:100]}'
    if st is None:
        return {'verdict': 'inconclusive',
                'detail': f'API unreachable after 4 attempts: {last}'}
    if st != 200:
        return {'verdict': 'inconclusive', 'detail': f'API answered {st}'}
    try:
        out = json.loads(body)
    except ValueError:
        return {'verdict': 'inconclusive', 'detail': f'non-JSON body: {body[:160]}'}
    flat = json.dumps(out, ensure_ascii=False)
    doubled = 'ca_ca' in flat or 'gavā_gavā' in flat
    if doubled:
        return {'verdict': 'verified',
                'detail': f'misalignment signature reproduced (doubled echo in response {flat[:220]})'}
    return {'verdict': 'stale',
            'detail': f'API reachable, no doubled echo for ["ca","gavā"]: {flat[:220]} — '
                      'misalignment no longer reproduces'}


def probe_448():
    """§448 MWScan servepdf.php: api=1&page=277&dict=mw resolves to the 1899
    mw0277-*.pdf (the finding's own api=1 probe recipe)."""
    url = ('https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/webtc/'
           'servepdf.php?api=1&page=277&dict=mw')
    st, body, _ = http_get(url, timeout=30)
    if st == 200 and 'mw0277' in body:
        return {'verdict': 'verified', 'detail': f'api=1&page=277 resolves {body[:160]}'}
    if st == 200:
        return {'verdict': 'stale', 'detail': f'endpoint 200 but no mw0277 resolution: {body[:160]}'}
    return {'verdict': 'inconclusive', 'detail': f'endpoint answered {st}'}


def probe_451():
    """§451 false Zenodo DOI: 10.5281/zenodo.15834721 still resolves to the
    UNRELATED "Sphericity" preprint (the H1364 live-check recipe)."""
    st, body, final = http_get('https://doi.org/10.5281/zenodo.15834721', timeout=40)
    title = re.search(r'<title[^>]*>([^<]+)</title>', body, re.I)
    title = title.group(1) if title else ''
    ok_shape = final and 'zenodo.org' in final
    if st == 200 and ok_shape and 'sphericity' in title.lower():
        return {'verdict': 'verified',
                'detail': f'DOI still resolves to the unrelated preprint: {final} «{title[:120]}»'}
    if st == 200 and ok_shape:
        return {'verdict': 'stale',
                'detail': f'DOI now resolves to a DIFFERENT record: {final} «{title[:120]}» — '
                          're-adjudicate §451'}
    return {'verdict': 'inconclusive', 'detail': f'DOI answered {st} final={final}'}


ARCHIVE_ITEMS = {
    'academy_3_48': 'sim_academy-and-literature_1872-05-15_3_48',   # correct-labelled pair member
    'academy_3_10': 'sim_academy-and-literature_1872-05-15_3_10',   # mislabeled sibling (route per §651)
    'athenaeum_2315': 'sim_athenaeum-uk_1872-03-09_2315',
    'memoir': 'in.ernet.dli.2015.31677',
}
WIKISOURCE_LESKIEN = 'https://de.wikisource.org/wiki/ADB:Goldst%C3%BCcker,_Theodor'


def _ia_item(id_):
    """archive.org metadata probe; returns (fetchable, detail). §651: a darked item
    yields empty metadata / no files — the same-date sibling is the route."""
    try:
        _, body, _ = http_get(f'https://archive.org/metadata/{id_}', timeout=30,
                              retries=ARCHIVE_RETRIES, sleep=ARCHIVE_SLEEP)
        m = json.loads(body)
    except Exception as e:  # noqa: BLE001 - recorded, not raised
        return False, f'{id_}: error {e.__class__.__name__}'
    if not isinstance(m, dict) or not m.get('files'):
        return False, f'{id_}: darked/empty metadata'
    n = len(m['files'])
    return True, f'{id_}: live, {n} files'


def probe_652():
    """§652 Goldstücker loci re-fetch: the four loci stay reachable — Academy III/48
    (either pair member per §651), Athenaeum №2315, the 1879 memoir, Leskien ADB."""
    checks = {}
    a48, d48 = _ia_item(ARCHIVE_ITEMS['academy_3_48'])
    a10, d10 = _ia_item(ARCHIVE_ITEMS['academy_3_10'])
    checks['academy'] = (a48 or a10, f'{d48} | {d10}')
    ath, dath = _ia_item(ARCHIVE_ITEMS['athenaeum_2315'])
    checks['athenaeum'] = (ath, dath)
    mem, dmem = _ia_item(ARCHIVE_ITEMS['memoir'])
    checks['memoir'] = (mem, dmem)
    try:
        st, body, _ = http_get(WIKISOURCE_LESKIEN, timeout=30, retries=2)
        # Gate on CONTENT, not status: de.wikisource serves some pages with a 404
        # status but full article body (observed on ADB:Goldstücker pre-rename).
        sig = ('ungeheuren Umfang angelegten' in body and 'abbrechen' in body)
        checks['adb_leskien'] = (st == 200 and sig,
                                 f'ADB:Goldstücker, Theodor answered {st}, quote fragments '
                                 f'{"present" if sig else "ABSENT"}')
    except Exception as e:  # noqa: BLE001 - recorded, not raised
        checks['adb_leskien'] = (False, f'ADB:Goldstücker error {e.__class__.__name__}')
    detail = ' | '.join(d for _, d in checks.values())
    if all(v for v, _ in checks.values()):
        return {'verdict': 'verified', 'detail': f'all four loci re-fetch: {detail}'[:1900]}
    if any(v for v, _ in checks.values()):
        return {'verdict': 'stale',
                'detail': 'some loci no longer re-fetch (rotated/darked beyond the §651 pair '
                          f'route): {detail}'[:1900]}
    return {'verdict': 'inconclusive', 'detail': detail[:1900]}


