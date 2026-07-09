#!/usr/bin/env python
"""part_b_xref_discovery.py — H404 Part B: discover + count "see X"-style redirect
conventions across the CDSL English/German dictionaries (MW, PWG, GRA, PWKVN,
AP90). Discovery-first per the handoff — each dictionary's marker is sampled and
verified against real text before counting, not assumed to generalize from koch's
`см.`. Read-only over csl-orig (sibling repo); never writes there.

Record model: each csl-orig v02 text file is a stream of `<L>...<h>N` header
lines followed by the entry body (until the next `<L>` or EOF); `<LEND>` closes
a record where present, otherwise the next `<L>` line is the boundary. This
mirrors PWG's own `<L>...<h>`/`<hom>` convention (the same "hom" numbering
`_ls_extract.py`/`build_src.py` already parse elsewhere in this repo).

Discovered markers (sampled ~20-30 entries per dict, see module docstring
history / PIPELINE_CAPABILITY_AUDIT_2026-07-08.md §W2b for the worked samples):
  MW     <ab>q.v.</ab>            "quod vide" bare pointer
  PWG    <ab n="siehe">s.</ab> / <ab>vgl.</ab>   German siehe/vergleiche
  GRA    <ab n="siehe">s.</ab> ... <ab n="vorige">v.</ab>   "s. d. v." idiom
  PWKVN  <ab>Vgl.</ab>            German vergleiche (mostly co-occurs with a
                                  real definition already present -> rarely bare)
  AP90   NO discovered redirect-to-another-headword convention. Its `[cf. ...]`
         brackets are Indo-European ETYMOLOGY (cognate comparison), not a
         pointer to a fuller definition elsewhere in AP90 — structurally
         different from every other marker here. Reported as a genuine null
         result, not forced into the same shape.

Count only — NOT a resolution pass. Part B step 4 gates resolution ("only where
clearly worth it") on the org's csl-orig correction-workflow (any change to the
canonical dictionary text needs snapshot -> updateByLine.py -> validate ->
queue -> batch PR, never a direct rewrite); building a resolver here would be
scope creep past what this discovery pass owes. Report the count, flag the
correction-workflow fork explicitly, let a human decide whether resolution is
worth commissioning as its own handoff.

  python part_b_xref_discovery.py --report
"""
import argparse, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
GITHUB = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
CSL_ORIG = os.path.join(GITHUB, 'csl-orig', 'v02')

_TAG_RE = re.compile(r'<[^>]+>')
_SANSKRIT_RE = re.compile(r'\{#.*?#\}')            # {#SLP1 citation#} -- not meaning
_GLOSS_RE = re.compile(r'\{%.*?%\}')               # {%German gloss%} -- IS meaning (PWG/PWKVN/GRA)
_SIGLUM_RE = re.compile(r'\{[@\d].*?[@\d]?\}|\{[^{}]*\}')  # {@word@} / {123,4} citation braces

DICTS = {
    'mw': {
        'path': os.path.join(CSL_ORIG, 'mw', 'mw.txt'),
        'lang': 'en',
        'marker_re': re.compile(r'<ab>q\.\s*v\.</ab>'),
        'desc': '<ab>q.v.</ab> ("quod vide")',
    },
    'pwg': {
        'path': os.path.join(CSL_ORIG, 'pwg', 'pwg.txt'),
        'lang': 'de',
        'marker_re': re.compile(r'<ab n="siehe">s\.</ab>|<ab>[Vv]gl\.</ab>'),
        'desc': '<ab n="siehe">s.</ab> / <ab>vgl.</ab> ("siehe"/"vergleiche")',
    },
    'gra': {
        'path': os.path.join(CSL_ORIG, 'gra', 'gra.txt'),
        'lang': 'de',
        'marker_re': re.compile(r'<ab n="siehe">s\.</ab>\s*<ab n="das">d\.</ab>\s*<ab n="vorige">v\.</ab>'),
        'desc': '<ab n="siehe">s.</ab> <ab n="das">d.</ab> <ab n="vorige">v.</ab> ("s. d. v." idiom)',
    },
    'pwkvn': {
        'path': os.path.join(CSL_ORIG, 'pwkvn', 'pwkvn.txt'),
        'lang': 'de',
        'marker_re': re.compile(r'<ab>[Vv]gl\.</ab>'),
        'desc': '<ab>Vgl.</ab> ("vergleiche")',
    },
    'ap90': {
        'path': os.path.join(CSL_ORIG, 'ap90', 'ap90.txt'),
        'lang': 'en',
        'marker_re': None,  # no discovered redirect-to-headword convention -- see module docstring
        'desc': 'NONE discovered — [cf. ...] is etymology, not a same-dict redirect',
    },
}


def iter_records(path):
    """Yield (header_line, body_text) for each `<L>...` record. Body runs until
    the next `<L>` header or `<LEND>`, whichever comes first."""
    if not os.path.exists(path):
        return
    header, body = None, []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('<L>'):
                if header is not None:
                    yield header, '\n'.join(body)
                header, body = line, []
            elif line.strip() == '<LEND>':
                if header is not None:
                    yield header, '\n'.join(body)
                header, body = None, []
            else:
                if header is not None:
                    body.append(line)
        if header is not None:
            yield header, '\n'.join(body)


def has_own_meaning(body, lang):
    """A record body carries a definition of its own (not just apparatus/markup)."""
    t = _SANSKRIT_RE.sub(' ', body)
    if lang == 'de':
        # PWG/GRA/PWKVN definitions live inside {%...%} spans; a bare "s./vgl."
        # pointer has none.
        return bool(_GLOSS_RE.search(t))
    # MW/AP90: strip tags/citations/braces, require >=1 real alphabetic word
    # of length >=3 outside of what's left (loose, English/Latin apparatus).
    t = _TAG_RE.sub(' ', t)
    t = _SIGLUM_RE.sub(' ', t)
    words = re.findall(r'[A-Za-z]{3,}', t)
    # drop common apparatus/bibliographic tokens that survive stripping
    stop = {'the', 'and', 'from', 'cf', 'ib', 'ibid'}
    return any(w.lower() not in stop for w in words)


def is_bare_redirect(body, lang, marker_re):
    if marker_re is None:
        return False
    return bool(marker_re.search(body)) and not has_own_meaning(body, lang)


def count_dict(code, info, limit=None):
    n_total = n_bare = n_marker_present = 0
    for _header, body in iter_records(info['path']):
        n_total += 1
        if limit and n_total > limit:
            break
        if info['marker_re'] and info['marker_re'].search(body):
            n_marker_present += 1
            if is_bare_redirect(body, info['lang'], info['marker_re']):
                n_bare += 1
    return n_total, n_marker_present, n_bare


def report(limit=None):
    print('=== Part B — CDSL English/German dictionary redirect discovery (H404) ===')
    print('%-8s %10s %8s %14s %14s %s' % ('dict', 'records', 'lang', 'marker-present', 'bare(no-defn)', 'marker'))
    for code, info in DICTS.items():
        if not os.path.exists(info['path']):
            print('%-8s  MISSING SOURCE (%s)' % (code, info['path']))
            continue
        n_total, n_marker, n_bare = count_dict(code, info, limit=limit)
        pct_marker = 100.0 * n_marker / max(1, n_total)
        pct_bare = 100.0 * n_bare / max(1, n_total)
        print('%-8s %10d %8s %11d(%.1f%%) %11d(%.1f%%)  %s'
              % (code, n_total, info['lang'], n_marker, pct_marker, n_bare, pct_bare, info['desc']))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--limit', type=int, default=None, help='cap records scanned per dict (smoke test)')
    args = ap.parse_args()
    if args.report:
        return report(limit=args.limit)
    ap.print_help()


if __name__ == '__main__':
    main()
