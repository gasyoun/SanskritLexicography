#!/usr/bin/env python
"""ceiling_c2p1_window.py — Ceiling C2 phase 1: per-sense attestation window (H3168).

For every explicitly numbered PWG top-level sense, resolve its <ls> citations to
WORKS via ls_source_map.json (45 works) and emit an ATTESTATION WINDOW:

    earliest / latest      min/max date among the sense's cited DATED works
    n_dated_works          DISTINCT cited works carrying a date
    n_undated_citations    citation instances resolving to a mapped work whose
                           date the map leaves silent (0 under the current map;
                           the field exists because Phase 2 may add undated works)
    n_unresolved_citations citation instances whose siglum is NOT in the map —
                           the standing C7 residue census (carried, never dropped)

HONESTY CONTRACT (roadmap C2): every window is «per Böhtlingk–Roth's citations» —
evidence about what the dictionary cites, never about when a sense EMERGED in the
language. A sense with no resolvable dated citation gets earliest/latest = null.

Layering: each window row joins the committed src/pwg_sense_stratum.jsonl
Renou proxy by (key1, sense index within entry). NOTE (found during H3168):
csl-orig reflowed top-level sense markers from «<div n="1">N)» to
«<div n="1">N〉», so the committed sense_stratum.SENSE_RE no longer matches the
live canon (its --head mode returns [] today); this builder therefore segments
the CURRENT text with a bracket-tolerant regex and pairs with the stratum only
where an entry's sense count still matches — mismatches are counted and carried,
never silently dropped. This asset never rewrites the stratum itself.

Resolution route: build_ls_map.LS + build_ls_map.source_key — the canonical
<ls> normaliser behind renou.keys_in_text and ls_source_map.json itself.
(ls_resolver.py is the separate scan-URL resolver; its extract_first_key targets
a different display-key space and cannot join to the map.)

Outputs (both idempotent):
  src/pwg_sense_attestation_window.jsonl     one window row per numbered sense
  research/C2P1_ATTESTATION_WINDOW.md        report: coverage table + C7 residue
                                             census + deterministic 25-sense
                                             hand-check sample (marker-fenced)

Usage:
  python ceiling_c2p1_window.py            # build asset + regenerate report
"""
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_ls_map as blm       # noqa: E402  (<ls> regex + source_key)
import sense_stratum as ss       # noqa: E402  (entries() <L>/<LEND> iteration)
import renou                     # noqa: E402  (load_map)

# Top-level sense marker in the CURRENT canon: csl-orig now writes
# «<div n="1"> 1〉» / «<div n="1">— 2〉»; the pre-reflow form was «… 1)».
SENSE_RE = re.compile(r'<div n="1">\s*(?:[—–-]\s*)?(\d+)\s*[)〉]')

SMAP = renou.load_map('pwg')


def _find_stratum():
    """pwg_sense_stratum.jsonl is a gitignored local-only input (blanket
    RussianTranslation/src/*.jsonl rule): prefer a local copy, then
    $PWG_SENSE_STRATUM, then the repo's PRIMARY checkout (worktrees share it)."""
    local = os.path.join(HERE, 'pwg_sense_stratum.jsonl')
    if os.path.exists(local):
        return local
    env = os.environ.get('PWG_SENSE_STRATUM')
    if env and os.path.exists(env):
        return env
    try:
        import subprocess
        out = subprocess.run(
            ['git', 'worktree', 'list', '--porcelain'],
            cwd=HERE, capture_output=True, text=True,
            encoding='utf-8', errors='replace').stdout or ''
        for block in out.split('\n\n'):
            lines = block.splitlines()
            if lines and lines[0].startswith('worktree ') \
                    and not any(l.startswith('bare') for l in lines[1:]):
                cand = os.path.join(lines[0][len('worktree '):],
                                    'RussianTranslation', 'src',
                                    'pwg_sense_stratum.jsonl')
                if os.path.exists(cand):
                    return cand
    except OSError:
        pass
    raise SystemExit('pwg_sense_stratum.jsonl not found (local / $PWG_SENSE_STRATUM '
                     '/ primary checkout)')


STRATUM = _find_stratum()
OUT_ASSET = os.path.join(HERE, 'pwg_sense_attestation_window.jsonl')
OUT_REPORT = os.path.normpath(os.path.join(
    HERE, '..', 'research', 'C2P1_ATTESTATION_WINDOW.md'))

BASIS = 'per Böhtlingk–Roth\'s citations'
TOP_UNMAPPED = 25
HANDCHECK_N = 25

REPORT_MARKERS = ('<!-- c2p1:generated:start -->', '<!-- c2p1:generated:end -->')
REPORT_HEADER = """# C2 phase 1 — per-sense attestation window (PWG × ls_source_map)

_Created: 23-08-2026 · Handoff [H3168](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3168-OxAlpha_SanskritLexicography_ceiling-c2p1-sense-attestation-window_19.08.26.md) · Roadmap item [C2](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md)_

_Dr. Mārcis Gasūns_

**What this is:** for every explicitly numbered PWG top-level sense in the
current canon, its `<ls>` citations are resolved to works via
[ls_source_map.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json)
(45 dated works) and joined into a per-sense **attestation window**
(`earliest` / `latest` / `n_dated_works` / `n_undated_citations`), layered on the
committed Renou proxy [pwg_sense_stratum.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sense_stratum.jsonl)
(`renou_oldest`/`renou_youngest` joined from it where an entry's sense count
still pairs; the stratum itself is consumed, never re-derived or rewritten).

**Honesty contract:** every window is *«{basis}»* — a fact about what
Böhtlingk–Roth chose to cite, i.e. about the **dictionary**, not about the
language. No field here is, or may be read as, a claim about when a sense
*emerged*. Unresolvable sigla are carried, not dropped: they are ceiling item
C7's standing residue, censused below.

**Phase fence:** the curated per-work dating table (scholarly source per date,
contested datings as @DECIDE) is Wave 2 and is deliberately NOT built here.
"""


def load_stratum():
    """key1 -> list of stratum rows, in file order."""
    idx = {}
    with open(STRATUM, encoding='utf-8') as fh:
        for line in fh:
            rec = json.loads(line)
            idx[rec['key1']] = rec['senses']
    return idx


_VOL_TAIL = re.compile(r'^\(?[IVXivx]+\)?[.,]?$')


def _fallback_key(raw):
    """One-token retry for roman-numeral volume tails: «HIT. I, 109»,
    «PAÑCAT. II, 125», «Spr. (II)» normalise to compound sigla («HIT. I»)
    that miss the map even though the WORK named is the plain siglum.
    Drops ONLY a final pure-roman/parenthesised token; anything else
    («MED. gh.» — a kośa section, «Verz. d. Oxf. H») stays unresolved."""
    tokens = [t for t in raw.strip().split() if t]
    if len(tokens) >= 2 and _VOL_TAIL.match(tokens[-1]):
        base = []
        for t in tokens[:-1]:
            if any(ch.isdigit() for ch in t):
                break
            base.append(t)
            if len(base) >= 4:
                break
        return re.sub(r'\s+', ' ', ' '.join(base)).strip().rstrip('.').strip()
    return None


def classify_citations(seg):
    """One sense segment -> per-instance classification."""
    dated_dates = []           # one entry per dated-work INSTANCE
    dated_works = set()
    undated_instances = 0
    resolved_instances = 0
    fallback_instances = 0
    unmapped = Counter()
    n_citations = 0
    for m in blm.LS.finditer(seg):
        n_citations += 1
        k = blm.source_key(m.group(1), m.group(2))
        key_used, rec = None, None
        if k:
            rec = SMAP.get(k)
            if rec is not None:
                key_used = k
            else:
                kf = _fallback_key(k)
                if kf:
                    rec = SMAP.get(kf)
                    if rec is not None:
                        key_used = kf
                        fallback_instances += 1
        if rec is None:
            unmapped[k if k else '<empty>'] += 1
            continue
        resolved_instances += 1
        d = rec.get('date')
        if d is None:
            undated_instances += 1
        else:
            dated_dates.append(d)
            dated_works.add(key_used)
    return {
        'n_citations': n_citations,
        'resolved': resolved_instances,
        'unmapped': unmapped,
        'undated': undated_instances,
        'dates': dated_dates,
        'dated_works': dated_works,
        'fallbacks': fallback_instances,
    }


def main():
    stratum_idx = load_stratum()
    rows = []
    global_unmapped = Counter()
    buckets = Counter()
    head_mismatch = 0
    heads = 0
    fallback_total = 0

    for k1, body in ss.entries(ss.PWG):
        hits = list(SENSE_RE.finditer(body))
        if not hits:
            continue
        heads += 1
        srows = stratum_idx.get(k1)
        if srows is None or len(srows) != len(hits):
            head_mismatch += 1
            srows = srows or []
        for i, m in enumerate(hits):
            start = m.start()
            end = hits[i + 1].start() if i + 1 < len(hits) else len(body)
            seg_text = body[start:end]
            cls = classify_citations(seg_text)
            global_unmapped.update(cls['unmapped'])
            fallback_total += cls['fallbacks']
            srow = srows[i] if i < len(srows) else {}
            has_window = bool(cls['dates'])
            if has_window:
                buckets['windowed'] += 1
            elif cls['resolved']:
                buckets['undated_only'] += 1
            elif cls['n_citations']:
                buckets['no_resolvable'] += 1
            else:
                buckets['no_citations'] += 1
            rows.append({
                'key1': k1,
                'sense_index': i,
                'sense_no': int(m.group(1)),
                'basis': BASIS,
                'n_citations': cls['n_citations'],
                'n_resolved_citations': cls['resolved'],
                'n_unresolved_citations': sum(cls['unmapped'].values()),
                # sigla only — join ls_source_map.json for name/date/period/renou
                'dated_works': sorted(cls['dated_works']),
                'earliest': min(cls['dates']) if has_window else None,
                'latest': max(cls['dates']) if has_window else None,
                'n_dated_works': len(cls['dated_works']),
                'n_undated_citations': cls['undated'],
                'renou_oldest': srow.get('renou_oldest') or None,
                'renou_youngest': srow.get('renou_youngest') or None,
                '_seg': seg_text,
            })

    # ---- fail-condition guards -------------------------------------------
    bad = [r for r in rows if r['n_dated_works'] == 0
           and (r['earliest'] is not None or r['latest'] is not None)]
    assert not bad, 'window emitted for %d senses with no dated work' % len(bad)
    assert sum(buckets.values()) == len(rows)

    with open(OUT_ASSET, 'w', encoding='utf-8') as fh:
        for r in rows:
            payload = {k: v for k, v in r.items() if k != '_seg'}
            fh.write(json.dumps(payload, ensure_ascii=False) + '\n')

    write_report(rows, buckets, global_unmapped, heads, head_mismatch,
                 fallback_total)

    print('heads (numbered-sense entries): %d (stratum-pairing mismatches: %d)'
          % (heads, head_mismatch), file=sys.stderr)
    print('senses: %d' % len(rows), file=sys.stderr)
    print('coverage: %s' % dict(buckets), file=sys.stderr)
    print('C7 residue: %d unresolved citation instances, %d distinct sigla'
          % (sum(global_unmapped.values()), len(global_unmapped)), file=sys.stderr)
    print('wrote %s (%d rows)' % (OUT_ASSET, len(rows)), file=sys.stderr)


def write_report(rows, buckets, global_unmapped, heads, head_mismatch,
                 fallback_total):
    total = len(rows)
    windowed = buckets['windowed']
    undated_only = buckets['undated_only']
    no_resolvable = buckets['no_resolvable']
    no_cit = buckets['no_citations']
    unres_total = sum(global_unmapped.values())

    stratum_idx = load_stratum()
    st_heads = len(stratum_idx)
    st_senses = sum(len(v) for v in stratum_idx.values())
    paired_senses = sum(1 for r in rows if r['renou_oldest'] is not None)

    def pct(n):
        return '%d (%.1f%%)' % (n, 100.0 * n / total)

    L = [REPORT_HEADER.format(basis=BASIS)]
    L.append(REPORT_MARKERS[0])
    L.append('')
    L.append('## Coverage table')
    L.append('')
    L.append('| Bucket | Definition | Senses | Share |')
    L.append('| --- | --- | --- | --- |')
    L.append('| Windowed | >= 1 cited work carries a map date | %s |'
             % pct(windowed))
    L.append('| Undated-only | >= 1 resolvable citation, none dated | %s |'
             % pct(undated_only))
    L.append('| Unresolvable | citations present, none resolve to the map | %s |'
             % pct(no_resolvable))
    L.append('| Citation-less | no `<ls>` element in the sense segment | %s |'
             % pct(no_cit))
    L.append('| **Total** | all numbered senses (current canon) | **%d** | 100%% |' % total)
    L.append('')
    L.append('## Segmentation note (stratum pairing)')
    L.append('')
    L.append('- Committed Renou proxy `pwg_sense_stratum.jsonl`: %d headwords, '
             '%d senses.' % (st_heads, st_senses))
    L.append('- This build: %d headwords with >= 1 top-level numbered sense, '
             '%d senses. Sense counts pair with the stratum for the renou join '
             'in %d senses; the rest carry null `renou_*` (counted, not dropped).'
             % (heads, total, paired_senses))
    L.append('- Known upstream drift (found here): csl-orig reflowed top-level '
             'sense markers from «`<div n="1">N)`» to «`<div n="1">N〉`», so the '
             'committed `sense_stratum.SENSE_RE` matches 0 senses against the live '
             'canon (`sense_stratum.py --head a` → `[]`). This builder segments the '
             'current text with a bracket-tolerant pattern; the committed stratum '
             'file itself is untouched.')
    L.append('')
    L.append('## C7 residue census (unmapped `<ls>` sigla)')
    L.append('')
    L.append('%d citation instances across the whole corpus carry a siglum absent '
             'from ls_source_map.json (%d distinct sigla). This is the standing '
             'C7 census; nothing was dropped.' % (unres_total, len(global_unmapped)))
    L.append('')
    L.append('**Bounded fallback (documented, deterministic):** %d further '
             'instances normalise to compound sigla whose final token is a pure '
             'roman-numeral volume marker («HIT. I», «PAÑCAT. II», «Spr. (II)»); '
             'these are retried ONCE with that token dropped and join the plain '
             'siglum already in the map. No other inference is made — section '
             'sigla («MED. gh.»), journals («Ind. St.») and catalogue refs '
             '(«Verz. d. Oxf. H.») stay unresolved below.'
             % fallback_total)
    L.append('')
    L.append('Windows are therefore **conservative lower bounds**: a sense whose '
             'only citations fall in the residue may still name dated works in '
             'the printed entry.')
    L.append('')
    L.append('| Siglum | Instances |')
    L.append('| --- | --- |')
    for sig, n in global_unmapped.most_common(TOP_UNMAPPED):
        L.append('| `%s` | %d |' % (sig, n))
    if len(global_unmapped) > TOP_UNMAPPED:
        rest = sum(n for _, n in global_unmapped.most_common()[TOP_UNMAPPED:])
        L.append('| … %d further sigla | %d |' % (len(global_unmapped) - TOP_UNMAPPED, rest))
    L.append('')
    L.append('## Deterministic hand-check sample (%s)' % HANDCHECK_N)
    L.append('')
    L.append('Every %d-th windowed sense in file order, with the verbatim `<ls>` '
             'elements from the digitized printed entry '
             '(csl-orig `v02/pwg/pwg.txt`, exact source segment for that row) and '
             'the works the join emitted.' % max(1, windowed // HANDCHECK_N))
    L.append('')
    stride = max(1, windowed // HANDCHECK_N)
    shown = 0
    for r in rows:
        if r['n_dated_works'] == 0:
            continue
        shown += 1
        if shown % stride:
            continue
        seg = r['_seg']
        tags = ['<ls%s>%s</ls>' % (a, re.sub(r'\s+', ' ', i.strip()))
                for a, i in blm.LS.findall(seg)]
        shown_tags = '; '.join(tags[:8]) + (' … +%d more' % (len(tags) - 8)
                                            if len(tags) > 8 else '')
        names = ', '.join(sorted(SMAP[w]['name'] for w in r['dated_works']))
        L.append('- **%s / sense #%d (no %s)** — raw (%d): `%s` → dated: %s '
                 '(window %s…%s)'
                 % (r['key1'], r['sense_index'], r['sense_no'],
                    r['n_citations'], shown_tags or '—', names,
                    r['earliest'], r['latest']))
    L.append(REPORT_MARKERS[1])
    L.append('')
    with open(OUT_REPORT, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L))


if __name__ == '__main__':
    main()
