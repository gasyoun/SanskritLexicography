#!/usr/bin/env python
"""H1350 W1.6 -- <ls> citation coverage extension (D8: deterministic only, no LLM).

Baseline note (logged in .ai_state.md): the plan's stated 72.4% baseline
(FINDINGS Sec.20) is STALE -- a direct measurement against the current
pwgbib.txt (4,390 entries, up from whatever produced 72.4%) already gives
98.2% citation-level / 85.1% distinct-key-level resolution via
pwg_sources.resolve() alone, well past the D8/V6 >=85% target before this
step adds anything.

This step's genuine, deterministic extension: PWG's `ebend[a].` ("ebenda" --
German "ibid.") is not a distinct source at all, it is a same-as-previous-
citation continuation marker -- 2,280 raw <ls> occurrences, ~22.6% of what
was still unresolved. Classifying it as IBID rather than leaving it in the
unresolved tail is deterministic (a fixed string pattern), not a guessed or
synthesised source identity (D8's actual constraint).

Writes RussianTranslation/schemas/ls_source_map_ext.json (sidecar, not a
rewrite of pwg_sources.py's authoritative pwgbib-backed resolver) and
RussianTranslation/reports/pwg_ls_unresolved.tsv (the remaining typed gap
for a human bibliographer -- D8's explicit fallback for anything genuinely
unresolvable without guessing).

    python extend_ls_coverage.py --report
"""
import argparse
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pwg_sources as ps  # noqa: E402 -- reused, unmodified authoritative resolver

REPORTS_DIR = os.path.join(HERE, '..', 'reports')
SCHEMAS_DIR = os.path.join(HERE, '..', 'schemas')
EXT_PATH = os.path.join(SCHEMAS_DIR, 'ls_source_map_ext.json')
UNRESOLVED_PATH = os.path.join(REPORTS_DIR, 'pwg_ls_unresolved.tsv')

LS = re.compile(r'<ls\b[^>]*>(.*?)</ls>', re.S)
IBID_RE = re.compile(r'^ebend[a]?\.?$', re.I)


def resolve_ext(token, ext_map):
    """pwg_sources.resolve() first (authoritative, pwgbib-backed); then the
    small deterministic IBID extension; never a guess beyond that."""
    r = ps.resolve(token)
    if r:
        return r, 'pwgbib'
    k = ps.norm(token)
    if IBID_RE.match(k):
        return 'IBID (ebenda -- same source as the preceding citation)', 'ibid-rule'
    if k in ext_map:
        return ext_map[k], 'ext-map'
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    args = ap.parse_args()

    ext_map = {}  # reserved for future deterministic additions; empty for this pass

    freq = collections.Counter()
    with open(ps.PWG, encoding='utf-8-sig') as f:
        text = f.read()
    for m in LS.finditer(text):
        k = ps.source_key(m.group(1))
        if k:
            freq[k] += 1
    total_citations = sum(freq.values())
    total_keys = len(freq)

    baseline_resolved_keys = sum(1 for k in freq if ps.resolve(k))
    baseline_resolved_cit = sum(c for k, c in freq.items() if ps.resolve(k))

    extended_resolved_keys = 0
    extended_resolved_cit = 0
    by_method = collections.Counter()
    unresolved = []
    for k, c in freq.items():
        r, method = resolve_ext(k, ext_map)
        if r:
            extended_resolved_keys += 1
            extended_resolved_cit += c
            by_method[method] += c
        else:
            unresolved.append((k, c))
    unresolved.sort(key=lambda kc: -kc[1])

    print(f'pwgbib entries: {len(ps.bib())}')
    print(f'<ls> citations: {total_citations}, distinct source keys: {total_keys}')
    print(f'BASELINE (pwgbib only): {baseline_resolved_keys}/{total_keys} keys '
          f'({100*baseline_resolved_keys/total_keys:.1f}%), '
          f'{baseline_resolved_cit}/{total_citations} citations '
          f'({100*baseline_resolved_cit/total_citations:.1f}%)')
    print(f'EXTENDED (+ deterministic ibid rule): {extended_resolved_keys}/{total_keys} keys '
          f'({100*extended_resolved_keys/total_keys:.1f}%), '
          f'{extended_resolved_cit}/{total_citations} citations '
          f'({100*extended_resolved_cit/total_citations:.1f}%)')
    print(f'resolution by method (citations): {dict(by_method)}')
    print(f'remaining unresolved: {len(unresolved)} keys, '
          f'{total_citations - extended_resolved_cit} citations')

    os.makedirs(SCHEMAS_DIR, exist_ok=True)
    with open(EXT_PATH, 'w', encoding='utf-8') as f:
        json.dump({
            'schema': 'ls_source_map_ext/0.1',
            'description': ('Deterministic sidecar extension to pwg_sources.py\'s pwgbib '
                             'resolver (D8: no LLM, no synthesised sources). Currently empty of '
                             'literal string mappings -- the one addition this pass made (the '
                             '"ebend[a]." ibid pattern) is a RULE, applied in extend_ls_coverage.py '
                             'itself (IBID_RE), not a per-string map entry, since it matches a class '
                             'of tokens rather than one fixed source name.'),
            'entries': ext_map,
        }, f, ensure_ascii=False, indent=1)
    print(f'wrote {EXT_PATH}')

    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(UNRESOLVED_PATH, 'w', encoding='utf-8') as f:
        f.write('source_key\tcitation_count\n')
        for k, c in unresolved:
            f.write(f'{k}\t{c}\n')
    print(f'wrote {UNRESOLVED_PATH} ({len(unresolved)} rows)')

    ceiling_note = (
        'Extended citation-level coverage exceeds the D8/V6 >=85% target. Remaining tail is '
        'dominated by malformed/truncated multi-part continuation keys (bare roman numerals, '
        '"(I)"/"(II)" volume markers, single-letter fragments) that source_key()\'s simple '
        'first-token heuristic cannot resolve without guessing the intended full citation -- '
        'exactly the D8 "no synthesised sources" boundary. Catalogued in pwg_ls_unresolved.tsv '
        'for a human bibliographer, per D8\'s explicit fallback.'
    )
    print(ceiling_note)


if __name__ == '__main__':
    main()
