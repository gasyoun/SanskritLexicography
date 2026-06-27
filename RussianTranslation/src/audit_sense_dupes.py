"""audit_sense_dupes.py — deterministic cross-part duplicate-sense guard for root-split heads.

Catches the failure where a head-part agent over-produces (renders senses that belong to a
sibling part) or mis-tags a secondary-conjugation sub-sense (caus./pass.) as a plain numbered
sense — so the same numbered sense appears in two parts of the SAME homonym and the glued
article carries a duplicate. This is a cross-UNIT defect the per-card fidelity gate cannot see
(each unit looks fine on its own). Pure Python, zero tokens — the QA the bulk run leans on.

Usage:  python audit_sense_dupes.py wf_output.json
Exit 0 = clean, 1 = duplicate numbered sense within a homonym.
"""
import json, os, sys, re, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SKIP = {'gramm-forms', 'header', 'gramm-header', 'grammar', 'paradigm', 'vgl.', 'vgl'}
INP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pilot', 'input')
_SEC_HDR = re.compile(r'\((caus|pass|desid|intens|partic|inf)[a-z]* SECONDARY-CONJUGATION', re.I)


def section_of(key):
    """Deterministic: read the part's raw LAYER header. A secondary-conjugation part (caus./
    pass./…) RESTARTS sense numbering, so its 1/2/3 are a DIFFERENT space from the simple verb's.
    Namespacing by this means the guard never false-positives on a legitimate caus-renumber, yet
    still catches a simple-verb part that over-produces a sibling's sense."""
    p = os.path.join(INP, key + '.raw.txt')
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            m = _SEC_HDR.search(f.readline())
            if m:
                return m.group(1).lower()
    return ''


def find_results(o):
    if isinstance(o, dict):
        if isinstance(o.get('results'), list):
            return o['results']
        for v in o.values():
            r = find_results(v)
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find_results(v)
            if r:
                return r
    return None


def norm(tag):
    """Normalize a sense tag so 'caus. 2' and plain '2' stay DISTINCT but '2)'=='2'=='2 '."""
    t = (tag or '').strip().lower().replace('〉', '').rstrip(')').strip()
    return re.sub(r'\s+', ' ', t)


def homonym(key):
    m = re.search(r'~~(h\d+)', key or '')
    return m.group(1) if m else 'h?'


def main():
    wf = sys.argv[1] if len(sys.argv) > 1 else 'wf_output.json'
    results = find_results(json.load(open(wf, encoding='utf-8'))) or []
    # (homonym, normalized tag) -> set of subkeys that rendered it
    seen = collections.defaultdict(set)
    for r in results:
        key = r.get('key', '')
        if '_pwg' not in key:                 # only the PWG head-parts share a sense-number space
            continue
        sec = section_of(key)                 # '' for the simple verb, else caus/pass/…
        card = r.get('card') or {}
        for rec in card.get('records', []):
            for s in rec.get('senses', []):
                t = norm(s.get('tag'))
                if not t or t in SKIP:
                    continue
                # namespace: a bare number in a secondary-conjugation part is caus:N, not N
                if sec and not t.startswith(sec):
                    t = sec + ':' + t
                seen[(homonym(key), t)].add(key)

    dupes = {k: v for k, v in seen.items() if len(v) > 1}
    if not dupes:
        print('SENSE-DUPE GATE: PASS — no numbered sense rendered by >1 head-part per homonym')
        return 0
    print('SENSE-DUPE GATE: FAIL — %d duplicated sense(s):' % len(dupes))
    for (hom, t), keys in sorted(dupes.items()):
        print('  %s sense "%s" rendered by: %s' % (hom, t, ', '.join(sorted(keys))))
    return 1


if __name__ == '__main__':
    sys.exit(main())
