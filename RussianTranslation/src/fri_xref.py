#!/usr/bin/env python
"""fri_xref.py — resolve fri (Frisch 1956) bare Latin cross-reference glosses to
their target's real gloss (H404, H397 generalization to a second source).

Unlike koch, fri's redirect convention is NOT `см. X` — koch_xref.is_bare_xref
measures 0.0% for fri. fri instead redirects with Latin apparatus markers
(`v.` = vide, `cf.` = confer, `q.v.` = quod vide), e.g. `akārya v. akartavya;`
or `arpitavant (cf. arpita) ; давший, подавший` (the second case is NOT bare —
it carries its own Russian gloss too, so it stays untouched here). Measured:
340/8,151 (4.2%) of fri entries are bare Latin-marker redirects with no Russian
meaning of their own — material by H397's ~2% bar, unlike kna (0.2%),
smirnov (1.0%), kow (0.0%), which this module does not touch.

fri's targets are given directly in IAST-like romanization (not Devanagari, so
no self-header crosswalk is needed like koch_xref's): `build_src.iast_to_slp1`
(existing prior art, reused not reinvented) converts the target token, then the
same corpus_gate.form_key join used everywhere else finds it in fri's own
key1 index (built straight from each entry's own `slp1` JSON field — fri
carries a real slp1 per entry, unlike koch's Devanagari-embedded-in-gloss
format). Resolution rate is lower than koch's 92.3% (measured: 111/340 =
32.6%) because many targets are phonological stem variants (`aṅk-`, `aṅg-`,
...), verb-root cross-forms (`√stabh v. stambh`), or bare pronouns (`vayam`,
`asau`) that were never given their own headword entry — genuinely
unresolvable, not a code gap; left `silent`, never fabricated.

  python fri_xref.py --report
  python fri_xref.py --selftest
"""
import argparse, json, os, re, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import corpus_gate as cg
import build_src as bs
import koch_xref as kx  # reuses has_meaning() — same Russian-token detector, no reinvention

FRI_PATH = os.path.join(HERE, 'fri.jsonl')
XREF_MARK = kx.XREF_MARK  # same «см.→» provenance-prefix convention as koch_xref

_LATIN_XREF_RE = re.compile(r'\b(?:v\.|cf\.|q\.\s*v\.)\s*')
_ROMAN_NUM_RE = re.compile(r'^(?:I{1,3}|IV|V)\s+')
_TARGET_RE = re.compile(r"[a-zA-Zāīūṛṝḷḹṅñṭḍṇśṣḥṃṁ\-']+")

has_meaning = kx.has_meaning  # source-agnostic; reused verbatim


def is_bare_xref(gloss):
    """A fri gloss that carries a v./cf./q.v. redirect marker and no Russian
    meaning of its own."""
    return bool(gloss) and bool(_LATIN_XREF_RE.search(gloss)) and not has_meaning(gloss)


def extract_target(gloss):
    """First IAST-ish target token after a v./cf./q.v. marker, or None. Rejects a
    match immediately followed by a non-terminating letter (any script) — a small
    number of fri.jsonl rows carry known Cyrillic/Latin mojibake corruption
    (e.g. `v. II apaгa;` — a stray Cyrillic г mid-word, see build_src.py's "key
    hygiene" note); without this guard the regex silently truncates at the first
    non-Latin char and resolves against the WRONG, shorter headword instead of
    refusing. len(target)>=2 alone doesn't catch this — `apa` is a real 2-letter+
    token, just not the one actually written."""
    m = _LATIN_XREF_RE.search(gloss)
    if not m:
        return None
    rest = _ROMAN_NUM_RE.sub('', gloss[m.end():])
    tm = _TARGET_RE.match(rest)
    if not tm:
        return None
    if tm.end() < len(rest) and rest[tm.end()].isalpha():
        return None  # match truncated by an unexpected letter — corrupted token, refuse
    target = tm.group(0).strip().rstrip('-')
    return target if len(target) >= 2 else None


def load_fri_raw(path=FRI_PATH):
    entries = []
    if not os.path.exists(path):
        return entries
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def build_key1_index(entries):
    """form_key(slp1) -> [glosses], straight from fri's own slp1 field (no
    embedded-headword crosswalk needed — fri's targets are already roman)."""
    idx = defaultdict(list)
    for e in entries:
        k = cg.form_key(e.get('slp1', ''))
        if k:
            idx[k].append(e.get('gloss', ''))
    return idx


def resolve_one(gloss, key1_glosses):
    """Resolve one bare fri redirect to its target's real gloss. One hop only
    (fri's chains are rare and the targets are shallow stem/pronoun lookups,
    not multi-level redirect ladders like koch's). Returns (gloss_or_None, key1_or_None)."""
    target = extract_target(gloss)
    if not target:
        return None, None
    slp1 = bs.iast_to_slp1(target)
    k = cg.form_key(slp1)
    if not k:
        return None, None
    for g in key1_glosses.get(k) or []:
        if has_meaning(g):
            return g, k
    return None, None


_KEY1_GLOSSES = None


def _ensure_loaded():
    global _KEY1_GLOSSES
    if _KEY1_GLOSSES is None:
        _KEY1_GLOSSES = build_key1_index(load_fri_raw())
    return _KEY1_GLOSSES


def resolve_fri_lane(glosses):
    """Given the fri gloss list for one key1, replace each bare v./cf./q.v.
    pointer with its resolved target gloss (XREF_MARK-prefixed), leaving
    unresolvable ones untouched (stay `silent` downstream). Returns
    (new_glosses, n_resolved)."""
    key1_glosses = _ensure_loaded()
    out, n_resolved = [], 0
    for g in glosses:
        if not is_bare_xref(g):
            out.append(g)
            continue
        resolved, _k = resolve_one(g, key1_glosses)
        if resolved:
            out.append(XREF_MARK + resolved)
            n_resolved += 1
        else:
            out.append(g)
    return out, n_resolved


def report():
    entries = load_fri_raw()
    if not entries:
        sys.stderr.write('fri.jsonl not found at %s — nothing to report.\n' % FRI_PATH)
        raise SystemExit(2)
    key1_glosses = build_key1_index(entries)
    n_total = len(entries)
    n_bare = n_resolved = 0
    for e in entries:
        g = e.get('gloss', '')
        if not is_bare_xref(g):
            continue
        n_bare += 1
        resolved, _k = resolve_one(g, key1_glosses)
        if resolved:
            n_resolved += 1
    print('=== fri xref resolution ===')
    print('fri entries              : %d' % n_total)
    print('unique key1s             : %d' % len(key1_glosses))
    print('bare v./cf./q.v. xrefs    : %d (%.1f%% of dict)' % (n_bare, 100.0 * n_bare / n_total))
    print('  resolved                : %d (%.1f%%)' % (n_resolved, 100.0 * n_resolved / max(1, n_bare)))
    print('  unresolved (stay silent): %d' % (n_bare - n_resolved))


def selftest():
    assert has_meaning('огонь, бог огня')
    assert not has_meaning('akārya v. akartavya;')
    assert is_bare_xref('akārya v. akartavya;')
    assert not is_bare_xref('II akṣa n. (cf. caturakṣa) ; орган чувства; -° глаз')

    assert extract_target('akārya v. akartavya;') == 'akartavya'
    assert extract_target('akṣi n., v. akṣan;') == 'akṣan'
    assert extract_target('III akṣa n. (cf. caturakṣa) ; орган чувства') == 'caturakṣa'
    assert extract_target('II aparī f., v. II apara;') == 'apara', 'roman-numeral prefix skipped'
    assert extract_target('огонь, пламя') is None
    assert extract_target('aparī f., v. II apaгa;') is None, \
        'mojibake mid-word (Cyrillic г) must refuse, not truncate to a wrong shorter token'

    key1_glosses = defaultdict(list, {
        cg.form_key('akartavya'): ['akartavya; тот, который не должен быть сделан'],
        cg.form_key('anfRa'): ['anṛṇa; лишенный долга'],
    })
    resolved, k = resolve_one('akārya v. akartavya;', key1_glosses)
    assert resolved == 'akartavya; тот, который не должен быть сделан', resolved
    assert k == cg.form_key('akartavya')

    r2, k2 = resolve_one('anṛṇyavant v. anṛṇa;', key1_glosses)
    assert r2 == 'anṛṇa; лишенный долга', r2

    r3, _k3 = resolve_one('foo v. nonexistent;', key1_glosses)
    assert r3 is None

    global _KEY1_GLOSSES
    _saved = _KEY1_GLOSSES
    _KEY1_GLOSSES = key1_glosses
    try:
        new_glosses, n = resolve_fri_lane(['akārya v. akartavya;', 'огонь настоящий', 'foo v. nonexistent;'])
    finally:
        _KEY1_GLOSSES = _saved
    assert n == 1, (n, new_glosses)
    assert new_glosses[0].startswith(XREF_MARK) and 'не должен быть сделан' in new_glosses[0]
    assert new_glosses[1] == 'огонь настоящий'
    assert new_glosses[2] == 'foo v. nonexistent;'

    print('fri_xref selftest OK')


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
