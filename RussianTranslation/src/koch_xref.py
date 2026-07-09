#!/usr/bin/env python
"""koch_xref.py — resolve koch bare `см. X` cross-reference glosses to their target's
real meaning gloss (H397, H337 evidence-lane follow-up).

H337 measured koch: 4,048 / 29,177 (13.9%) entries carry no usable Russian meaning
gloss, and 3,471 of those are `см. X` redirects (e.g. `-aSrika` -> "см. अश्रि अश्रिक
-aśrika" = "see aśri"). `annotate_evidence.py` classifies these as `silent` via
`source_meaning_tokens()` returning empty — correct but lossy: the real meaning lives
under the target headword. This module resolves the pointer one (or two, chain-safe)
hops and returns the target's real gloss, so the koch lane recovers signal instead of
reporting silence for a resolvable redirect.

Resolution strategy: koch glosses are Devanagari script, not the SLP1/IAST the store
joins on, so there is no direct key1 lookup for a `см. X` target out of the box. But
~94% of koch entries open with their OWN Devanagari headword followed by `/iast/`
(`रूपधारिन् /rūpa-dhārin/ ...`) — that self-describing prefix, harvested across the
whole koch.jsonl, doubles as a Devanagari -> SLP1 crosswalk with no external
transliterator needed (reuses koch's own data, per the prior-art rule). A `см. X`
target's Devanagari token is looked up in that crosswalk, then joined into koch's own
key1 index for the resolved gloss.

Deterministic, offline (no gate-source file IO happens at import time — lazy-loaded on
first `resolve_koch_lane()` call, so `--selftest` stays pure-function / CI-safe like
annotate_evidence.py's own selftest).

  python koch_xref.py --report      # koch.jsonl xref resolution stats (no store write)
  python koch_xref.py --selftest
"""
import argparse, json, os, re, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import corpus_gate as cg

KOCH_PATH = os.path.join(HERE, 'koch.jsonl')
MAX_HOPS = 2          # depth cap: A -> B (hop 1) -> C (hop 2); never further
XREF_MARK = '«см.→» '   # «см.→» — provenance prefix on a resolved gloss

_TAG_RE = re.compile(r'<[^>]+>')
_PLACEHOLDER_RE = re.compile(r'\{T\d+\}')
_RU_END = cg._RU_END                              # reuse the shared stemming suffix regex
_CM_RE = re.compile(r'см\.\s*')
_DEVA_RE = re.compile(r'[ऀ-ॿ]+')
_HEAD_RE = re.compile(r'^([^\s/]+)\s*/([^/]+)/')  # leading "<devanagari> /<iast>/" self-header


def has_meaning(text):
    """True if `text` carries >=1 usable Russian content token (cf.
    annotate_evidence.source_meaning_tokens — duplicated narrowly here to avoid a
    circular import; same regex, same >=3-char-after-stemming rule)."""
    if not text:
        return False
    t = _PLACEHOLDER_RE.sub(' ', text)
    t = _TAG_RE.sub(' ', t)
    for tok in re.findall(r'[а-яёА-ЯЁ]{2,}', t.lower()):
        if len(_RU_END.sub('', tok)) >= 3:
            return True
    return False


def is_bare_xref(gloss):
    """A koch gloss that carries a `см.` redirect and no meaning of its own —
    the H337 `silent`-via-xref case this module recovers."""
    return bool(gloss) and 'см.' in gloss and not has_meaning(gloss)


def extract_targets(gloss):
    """Devanagari token(s) immediately following each `см.` occurrence, in order."""
    out = []
    for m in _CM_RE.finditer(gloss):
        dm = _DEVA_RE.match(gloss[m.end():].lstrip())
        if dm:
            out.append(dm.group(0))
    return out


def load_koch_raw(path=KOCH_PATH):
    entries = []
    if not os.path.exists(path):
        return entries
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def build_resolution_index(entries):
    """devanagari-headword -> slp1 (first-wins on the rare homograph collision), and
    form_key(slp1) -> [glosses] (koch's own key1 index, mirrors corpus_gate.load_index's
    aggregation for the koch lane alone)."""
    head_to_slp1 = {}
    key1_to_glosses = defaultdict(list)
    collisions = 0
    for e in entries:
        g = e.get('gloss', '')
        slp1 = e.get('slp1', '')
        m = _HEAD_RE.match(g)
        if m:
            dev = m.group(1)
            if dev in head_to_slp1 and head_to_slp1[dev] != slp1:
                collisions += 1
            else:
                head_to_slp1.setdefault(dev, slp1)
        k = cg.form_key(slp1)
        if k:
            key1_to_glosses[k].append(g)
    return head_to_slp1, key1_to_glosses, collisions


def resolve_one(gloss, head_to_slp1, key1_to_glosses, depth=0, visited=None):
    """Resolve one bare `см. X` gloss to a target's real gloss, chain-safe.
    Returns (resolved_gloss_or_None, target_key1_or_None, hops_used)."""
    if visited is None:
        visited = set()
    if depth >= MAX_HOPS:
        return None, None, depth
    targets = extract_targets(gloss)
    if not targets:
        return None, None, depth
    slp1 = head_to_slp1.get(targets[0])
    if not slp1:
        return None, None, depth              # target headword not in koch's own crosswalk
    k = cg.form_key(slp1)
    if not k or k in visited:
        return None, None, depth              # cycle guard
    visited.add(k)
    for g in key1_to_glosses.get(k) or []:
        if has_meaning(g):
            return g, k, depth + 1
    for g in key1_to_glosses.get(k) or []:      # target itself a further bare xref: one more hop
        if is_bare_xref(g):
            sub_g, sub_k, sub_depth = resolve_one(g, head_to_slp1, key1_to_glosses, depth + 1, visited)
            if sub_g:
                return sub_g, sub_k, sub_depth
    return None, None, depth


_HEAD_MAP = None
_KEY1_GLOSSES = None
_COLLISIONS = 0


def _ensure_loaded():
    global _HEAD_MAP, _KEY1_GLOSSES, _COLLISIONS
    if _HEAD_MAP is None:
        _HEAD_MAP, _KEY1_GLOSSES, _COLLISIONS = build_resolution_index(load_koch_raw())
    return _HEAD_MAP, _KEY1_GLOSSES


def resolve_koch_lane(glosses):
    """Given the koch gloss list for one key1 (as assembled by corpus_gate.load_index),
    replace each bare `см. X` pointer with its resolved target gloss (provenance-marked
    with XREF_MARK), leaving unresolvable pointers untouched (they stay `silent`
    downstream — never fabricate). Returns (new_glosses, n_resolved)."""
    head_map, key1_glosses = _ensure_loaded()
    out, n_resolved = [], 0
    for g in glosses:
        if not is_bare_xref(g):
            out.append(g)
            continue
        resolved, _k, _hops = resolve_one(g, head_map, key1_glosses)
        if resolved:
            out.append(XREF_MARK + resolved)
            n_resolved += 1
        else:
            out.append(g)
    return out, n_resolved


def report():
    entries = load_koch_raw()
    if not entries:
        sys.stderr.write('koch.jsonl not found at %s — nothing to report.\n' % KOCH_PATH)
        raise SystemExit(2)
    head_map, key1_glosses, collisions = build_resolution_index(entries)
    n_total = len(entries)
    n_bare = 0
    n_resolved = 0
    n_unresolved = 0
    for e in entries:
        g = e.get('gloss', '')
        if not is_bare_xref(g):
            continue
        n_bare += 1
        resolved, _k, _hops = resolve_one(g, head_map, key1_glosses)
        if resolved:
            n_resolved += 1
        else:
            n_unresolved += 1
    print('=== koch xref resolution ===')
    print('koch entries          : %d' % n_total)
    print('devanagari head map   : %d (collisions: %d, first-wins)' % (len(head_map), collisions))
    print('bare `см. X` xrefs     : %d' % n_bare)
    print('  resolved            : %d (%.1f%%)' % (n_resolved, 100.0 * n_resolved / max(1, n_bare)))
    print('  unresolved (stay silent): %d' % n_unresolved)


# ---- selftest (pure functions only — no koch.jsonl IO, so it runs in CI) --------------
def selftest():
    assert has_meaning('огонь, бог огня')
    assert not has_meaning('см. अश्रि अश्रिक -aśrika')
    assert not has_meaning('(A. pr. /ghaṭṭate/) см. घट्ट् II घट्ट् I -ghaṭṭ')
    assert is_bare_xref('см. रूपधर')
    assert is_bare_xref('रूपधारिन् /rūpa-dhārin/ см. रूपधर'), 'см. not at string start is still bare'
    assert not is_bare_xref('तापनीय /tāpanīya/ 1) золотой 2) см. उपानिषद्'), 'has a real sense besides the xref'

    assert extract_targets('см. अश्रि अश्रिक -aśrika') == ['अश्रि']
    assert extract_targets('रूपधारिन् /rūpa-dhārin/ см. रूपधर') == ['रूपधर']
    assert extract_targets('огонь, пламя') == []

    head_map = {'रूपधर': 'rUpaDara', 'अश्रि': 'aSri', 'चक्र': 'cakra'}
    fake_entries = [
        {'slp1': 'rUpaDara', 'gloss': 'रूपधर /rūpa-dhara/ m. принявший облик'},
        {'slp1': 'aSri', 'gloss': 'अश्रि /aśri/ f. край, грань'},
        {'slp1': 'cakra', 'gloss': 'चक्र /cakra/ см. रूपधर'},          # a target that is ITSELF a bare xref
    ]
    key1_glosses = defaultdict(list)
    for e in fake_entries:
        key1_glosses[cg.form_key(e['slp1'])].append(e['gloss'])

    resolved, k, hops = resolve_one('см. रूपधर', head_map, key1_glosses)
    assert resolved == 'रूपधर /rūpa-dhara/ m. принявший облик', resolved
    assert k == cg.form_key('rUpaDara') and hops == 1

    resolved2, _k2, hops2 = resolve_one('см. अश्रि अश्रिक -aśrika', head_map, key1_glosses)
    assert resolved2 == 'अश्रि /aśri/ f. край, грань', resolved2

    # unresolvable: target not in the head map at all
    r3, _k3, _h3 = resolve_one('см. नास्ति', head_map, key1_glosses)
    assert r3 is None

    # cycle guard: A -> см. A (self-pointing garbage) must terminate, not fabricate
    head_map_cyc = {'A': 'a'}
    key1_glosses_cyc = defaultdict(list, {cg.form_key('a'): ['см. A']})
    r4, _k4, _h4 = resolve_one('см. A', head_map_cyc, key1_glosses_cyc)
    assert r4 is None, 'a pure self-cycle must never resolve'

    global _HEAD_MAP, _KEY1_GLOSSES
    _saved = (_HEAD_MAP, _KEY1_GLOSSES)
    _HEAD_MAP, _KEY1_GLOSSES = head_map, key1_glosses
    try:
        new_glosses, n = resolve_koch_lane(['см. रूपधर', 'огонь настоящий', 'см. नास्ति'])
    finally:
        _HEAD_MAP, _KEY1_GLOSSES = _saved
    assert n == 1, (n, new_glosses)
    assert new_glosses[0].startswith(XREF_MARK) and 'принявший облик' in new_glosses[0]
    assert new_glosses[1] == 'огонь настоящий'
    assert new_glosses[2] == 'см. नास्ति'          # unresolved -> left untouched, still silent

    print('koch_xref selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.report:
        return report()
    ap.print_help()


if __name__ == '__main__':
    main()
