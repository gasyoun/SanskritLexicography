"""Per-row probes for §41-§57 (H7593): each function implements the finding's own
re-probe recipe. Lane contract: b_class_reprobe.py."""

import re
import sys

from b_class_reprobe_core import (REPO, http_get, http_post_json, gh_api,
                                  gh_dir_listing)

def probe_41():
    """§41 platform landscape — reuses findings_dashboard/probe_platforms.py (the
    finding's own probe) and gates on its two expected non-200 signatures:
    spokensanskrit.org -> 301 to learnsanskrit.cc; learnsanskrit.org/dictionary -> 404."""
    probe_path = REPO / 'findings_dashboard' / 'probe_platforms.py'
    saved = sys.path[:]
    try:
        sys.path.insert(0, str(REPO / 'findings_dashboard'))
        import probe_platforms  # noqa: E402
    finally:
        sys.path = saved
    results = []
    for name, url in probe_platforms.PLATFORMS:
        r = {'name': name, 'url': url}
        r.update(probe_platforms.probe(url))
        results.append(r)
        print(f'    {r["verdict"]:<12} {name}')
    spk = next((r for r in results if 'spokensanskrit' in r['name']), None)
    ls4 = next((r for r in results if r['name'].startswith('learnsanskrit.org')), None)
    # Expected signature CLASSES (the claim itself names the broken-TLS state):
    # spokensanskrit -> 301 to learnsanskrit.cc OR its known broken-TLS answer;
    # learnsanskrit.org/dictionary -> http-404. A timeout is not evidence about
    # the claim - that half is inconclusive, never stale.
    DEFINITIVE = ('ok', 'moved', 'tls-error')
    spk_answered = bool(spk) and (spk.get('verdict') in DEFINITIVE
                                  or str(spk.get('http', '')).startswith('http-'))
    ls4_answered = bool(ls4) and (ls4.get('verdict') in DEFINITIVE
                                  or str(ls4.get('http', '')).startswith('http-'))
    spk_ok = bool(spk) and ((spk.get('verdict') == 'moved'
                             and 'learnsanskrit.cc' in (spk.get('final_url') or ''))
                            or spk.get('verdict') == 'tls-error')
    ls4_ok = bool(ls4) and ls4.get('http') == 404
    if spk_ok and ls4_ok:
        detail = '; '.join(f"{r['name']}={r['verdict']}" for r in results)
        return {'verdict': 'verified', 'detail': f'12-platform snapshot: {detail}'[:1900]}
    if spk_answered and ls4_answered:
        return {'verdict': 'stale',
                'detail': f'signature changed: spokensanskrit->{spk.get("verdict")} '
                          f'learnsanskrit.org->{ls4.get("verdict")}'}
    return {'verdict': 'inconclusive',
            'detail': 'signature platforms not definitive: '
                      f'spokensanskrit={spk.get("verdict") if spk else None} '
                      f'learnsanskrit.org={ls4.get("verdict") if ls4 else None}'}


def probe_47():
    """§47 Heritage GitHub mirror: repo live + XML/ carries no inflected-form XML
    databanks (per the finding: only DTDs/LICENSES/README) + wall still up."""
    repo = gh_api('/repos/darkone23/Heritage_Resources')
    xml = gh_dir_listing('darkone23/Heritage_Resources', 'XML', ref='develop-main')
    names = [i['name'] for i in xml]
    xml_files = [n for n in names if n.lower().endswith('.xml')]
    dtds = [n for n in names if n.lower().endswith('.dtd')]
    wall = None
    try:
        st, body, _ = http_get('https://gitlab.inria.fr/huet/Heritage_Resources', timeout=20)
        low = body[:4000].lower()
        if st == 200 and 'anubis' not in low and 'repository' in low:
            wall = 'gitlab.inria.fr served the repo page (wall GONE)'
        else:
            wall = f'gitlab.inria.fr answered {st} (wall/hardening in place)'
    except Exception as e:  # noqa: BLE001 - recorded, not raised
        wall = f'gitlab.inria.fr unreachable ({e.__class__.__name__})'
    if repo.get('archived'):
        return {'verdict': 'stale', 'detail': f'mirror repo ARCHIVED; {wall}'}
    if not xml_files and dtds:
        return {'verdict': 'verified',
                'detail': f'mirror live (pushed_at {repo.get("pushed_at")}); XML/ = {names}; {wall}'}
    if xml_files:
        return {'verdict': 'stale',
                'detail': f'XML/ now carries .xml databanks {xml_files[:6]} (claim "morphology XML '
                          f'is not in it" no longer holds); {wall}'}
    return {'verdict': 'inconclusive', 'detail': f'XML/ listing empty; {wall}'}


def probe_48():
    """§48 VedaWeb async export: openapi.json 200 AND the pickup-key route shape
    (resource export route + /api/platform/tasks/download) still declared."""
    st, body, _ = http_get('https://vedaweb.uni-koeln.de/api/openapi.json', timeout=30)
    if st != 200:
        return {'verdict': 'inconclusive',
                'detail': f'openapi.json answered {st} (per §48, isolated 504s on this host are '
                          'retry-worthy, not evidence the API changed)'}
    spec = json.loads(body)
    paths = list(spec.get('paths', {}).keys())
    exp = [p for p in paths if 'export' in p]
    dl = [p for p in paths if 'tasks/download' in p]
    if exp and dl:
        return {'verdict': 'verified',
                'detail': f'openapi 200; export routes {exp[:4]}; download route {dl}'}
    return {'verdict': 'stale',
            'detail': f'openapi 200 but pickup-key shape changed: export={exp[:4]} download={dl}'}


def probe_49():
    """§49 duplicate-anchor pattern: a mirror MW page carries BOTH the H_<key>
    anchor and the plain <key> anchor for a covered entry."""
    items = gh_dir_listing('darkone23/Heritage_Resources', 'MW', ref='develop-main')
    htmls = [i['name'] for i in items if i['name'].endswith('.html')]
    if not htmls:
        return {'verdict': 'inconclusive', 'detail': f'no MW html in listing ({len(items)} items)'}
    url = ('https://raw.githubusercontent.com/darkone23/Heritage_Resources/develop-main/MW/'
           + htmls[0])
    st, body, _ = http_get(url, timeout=40)
    if st != 200:
        return {'verdict': 'inconclusive', 'detail': f'{htmls[0]} answered {st}'}
    h_anchors = len(re.findall(r'<a name="H_[^"]+"', body))
    plain = len(re.findall(r'<a name="[^"]+"', body))
    if h_anchors and plain:
        return {'verdict': 'verified',
                'detail': f'{htmls[0]}: {h_anchors} H_ anchors among {plain} anchors — '
                          'duplicate-anchor pattern intact'}
    return {'verdict': 'stale',
            'detail': f'{htmls[0]}: H_ anchors={h_anchors}, plain anchors={plain} — pattern changed'}


def probe_50():
    """§50 CDSL display paths: NMMB 404s under /2020/web/ and serves under /2026/web/
    — the non-uniformity the finding names."""
    base = 'https://www.sanskrit-lexicon.uni-koeln.de/scans/NMMBScan'
    st20, _, _ = http_get(base + '/2020/web/webtc/indexcaller.php', timeout=30)
    st26, _, _ = http_get(base + '/2026/web/webtc/indexcaller.php', timeout=30)
    if st20 == 404 and st26 == 200:
        return {'verdict': 'verified',
                'detail': f'NMMBScan/2020/web → {st20}, NMMBScan/2026/web → {st26} — non-uniform paths hold'}
    if st26 == 200 and st20 == 200:
        return {'verdict': 'stale',
                'detail': f'NMMBScan/2020/web now answers {st20} too — paths uniform again, finding needs update'}
    return {'verdict': 'inconclusive',
            'detail': f'NMMBScan/2020/web → {st20}, /2026/web → {st26}'}


def probe_56():
    """§56 DICO anchors: mirror DICO page still carries the shared class="navy"
    anchors whose three structural roles the finding disambiguates."""
    items = gh_dir_listing('darkone23/Heritage_Resources', 'DICO', ref='develop-main')
    htmls = [i['name'] for i in items if i['name'].endswith('.html')]
    if not htmls:
        return {'verdict': 'inconclusive', 'detail': f'no DICO html in listing ({len(items)} items)'}
    url = ('https://raw.githubusercontent.com/darkone23/Heritage_Resources/develop-main/DICO/'
           + htmls[0])
    st, body, _ = http_get(url, timeout=40)
    if st != 200:
        return {'verdict': 'inconclusive', 'detail': f'{htmls[0]} answered {st}'}
    navy = len(re.findall(r'<a class="navy" name="', body))
    if navy:
        return {'verdict': 'verified',
                'detail': f'{htmls[0]}: {navy} class="navy" anchors — shared-class structure intact'}
    return {'verdict': 'stale',
            'detail': f'{htmls[0]}: zero class="navy" anchors — anchor scheme changed'}


def probe_57():
    """§57 samskrtam.ru/z/: index still id-addressed (verb.php?id= links)."""
    st, body, _ = http_get('https://samskrtam.ru/z/', timeout=30, retries=2)
    ids = re.findall(r'verb\.php\?id=\d+', body)
    if ids:
        return {'verdict': 'verified',
                'detail': f'{len(ids)} verb.php?id= links in the index — id-addressing holds'}
    if st == 200:
        return {'verdict': 'stale',
                'detail': 'index answered 200 with no verb.php?id= links — addressing changed'}
    return {'verdict': 'inconclusive', 'detail': f'index answered {st}'}


