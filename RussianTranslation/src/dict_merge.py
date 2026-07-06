#!/usr/bin/env python
"""Layered multi-dictionary merge — the spine of the complete pwg_ru.

Per the architecture: PWG is the base; PW (revision) + SCH/PWKVN (supplements) +
NWS (external, later) overlay it. This module indexes the local Cologne layers by
SLP1 headword and assembles, for any key, the union across dictionaries — each
record tagged with its source + role, so the translator/editor sees the fullest
picture and the conflicts (e.g. PWG gender vs PW gender).

  python dict_merge.py stats                 records + headword coverage per layer
  python dict_merge.py merge <key1>          the layered view of one headword
"""
import os, re, sys, json, glob, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pwg_mask
import corpus_gate as cg
from safe_filename import candidate_names

HERE = os.path.dirname(os.path.abspath(__file__))
V02 = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02'))
NWS_DIR = os.path.join(HERE, 'pilot', 'nws')       # scraped JSON, one file per headword

# Local Cologne csl layers, indexed from csl-orig/v02/<code>/<code>.txt by SLP1
# headword. These DEFINE the headword universe (nws_scrape enumerates them).
LAYERS = [
    ('pwg',   'base',       'PWG — Böhtlingk-Roth, large (1855-75)'),
    ('pw',    'revision',   'PW/PWK — Böhtlingk, kürzere Fassung (1879-89)'),
    ('sch',   'supplement', 'SCH — Schmidt, Nachträge (1928)'),
    ('pwkvn', 'supplement', 'PWKVN — PWK variant supplement'),
]

# NWS is folded in SEPARATELY (not in LAYERS): it is external, JSON-backed, and
# adds NO new headwords — its keys are derived from the layers above. We keep only
# its net-new fragment (has_nws_extra), looked up per-key on demand (no 168k-file
# index). Cumulative Halle addendum, ~2013; provisional pending the data request.
NWS_LAYER = ('nws', 'external',
             'NWS — Nachtragswörterbuch (Halle), cumulative addendum ~2013; net-new beyond pw/Schmidt')

# The canonical layer set carried on a promoted store row. PWG-internal cards (the
# base entry + Nachträge + per-preverb sub-cards) all share the base 'pwg' layer —
# they are NOT keyed apart at the sub-card granularity (Nachträge are folded into the
# PWG whole-card by _pilot_gen_merged.gen_card), so 'pwg_nachtr' is a raw-LAYER concept
# inside the .raw.txt, not a promoted-row layer. The overlay layers ARE keyed apart, by
# the `~~..._zz_<layer>` sub-card suffix the merge writes (_pilot_gen_merged, `sub =
# '%s~~h0_zz_%s'`).
LAYER_VALUES = ('pwg', 'pw', 'sch', 'pwkvn', 'nws')


def layer_of(subcard):
    """Classify a store row's `subcard` key into its source LAYER ∈ LAYER_VALUES.

    The overlay layers are encoded as a `_zz_<layer>` segment; everything else (the
    numbered `_NN_<preverb>` cards, incl. the `_00_pwgNN` base card) is the PWG base.
    Robust to the numeric suffixes (`pw00`, `nws01`) the merge appends per record.
    """
    if not subcard:
        return 'pwg'
    seg = subcard.rsplit('_zz_', 1)
    if len(seg) == 2:
        tail = seg[1]
        for code in ('pwkvn', 'nws', 'sch', 'pw'):     # order: match 'pwkvn' before 'pw'
            if tail.startswith(code):
                return code
    return 'pwg'


def nws_record(key1):
    """Net-new NWS fragment for a form-key, or '' — the single scraped card, read
    on demand. Returns the fragment only when it adds beyond the pw/Schmidt layers
    (has_nws_extra); otherwise NWS is redundant with what we already hold."""
    p = None
    for stem in candidate_names(cg.form_key(key1)):
        cand = os.path.join(NWS_DIR, stem + '.json')
        if os.path.exists(cand):
            p = cand
            break
    if p is None:
        return ''
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception:
        return ''
    return d.get('nws', '') if d.get('has_nws_extra') else ''


def records_of(code):
    path = os.path.join(V02, code, code + '.txt')
    if not os.path.exists(path):
        return
    buf = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if line.startswith('<L>'):
            buf = [line]
        elif line.startswith('<LEND>'):
            if buf:
                yield buf
            buf = []
        elif buf:
            buf.append(line)


_IDX = {}
def index(code):
    if code in _IDX:
        return _IDX[code]
    idx = collections.defaultdict(list)
    for buf in records_of(code):
        m = pwg_mask.HEADER_RE.match(buf[0])
        if m:
            idx[cg.form_key(m.group(3))].append(buf)
    _IDX[code] = idx
    return idx


# `{{Lbody=NNNN}}` is a Cologne ALTERNATE-HEADWORD pointer: an alt-spelling record (e.g.
# `<L>205646.1<k1>CAyA` body `{{Lbody=205646}}`) carries no independent gloss — its content is
# the body of the primary entry NNNN (`<L>205646<k1>CAya`). 12,186 PW records (~7%) are these.
# Left unresolved they reach the translator as a bare pointer and leak verbatim into `russian`
# (H214 no-PWG run finding, 2026-07-06). Resolve them to the referenced entry's real body.
_LBODY_RE = re.compile(r'\{\{Lbody=(\d+(?:\.\d+)?)\}\}')
_IDIDX = {}


def id_index(code):
    """L-id (HEADER_RE group 1, e.g. '205646' / '205646.1') -> that record's body text."""
    if code in _IDIDX:
        return _IDIDX[code]
    idx = {}
    for buf in records_of(code):
        m = pwg_mask.HEADER_RE.match(buf[0])
        if m:
            idx[m.group(1)] = '\n'.join(buf[1:])
    _IDIDX[code] = idx
    return idx


def resolve_lbody(code, body, _depth=0):
    """Resolve `{{Lbody=NNNN}}` alternate-headword pointers to the referenced entry's real
    body (bounded depth; an unresolvable or self-referential pointer is left untouched)."""
    if _depth > 3 or '{{Lbody=' not in body:
        return body
    idx = id_index(code)

    def sub(m):
        target = idx.get(m.group(1))
        if target is None or ('{{Lbody=%s}}' % m.group(1)) in target:
            return m.group(0)                    # unresolvable / self-ref -> leave as-is
        return resolve_lbody(code, target, _depth + 1)

    return _LBODY_RE.sub(sub, body)


def merged(key1):
    fk = cg.form_key(key1)
    out = []
    for code, role, blurb in LAYERS:
        recs = index(code).get(fk, [])
        if recs:
            out.append({'layer': code, 'role': role, 'blurb': blurb,
                        'records': [resolve_lbody(code, '\n'.join(b[1:])) for b in recs]})
    nws = nws_record(fk)               # external addendum, last; only if net-new
    if nws:
        code, role, blurb = NWS_LAYER
        out.append({'layer': code, 'role': role, 'blurb': blurb, 'records': [nws]})
    return out


def cmd_stats(args):
    print('%-7s %-11s %9s %9s' % ('layer', 'role', 'records', 'headwords'))
    for code, role, blurb in LAYERS:
        idx = index(code)
        print('%-7s %-11s %9d %9d   %s'
              % (code, role, sum(len(v) for v in idx.values()), len(idx), blurb))
    # NWS — counted from the scraped JSON (not a csl index). net-new = has_nws_extra.
    files = glob.glob(os.path.join(NWS_DIR, '*.json'))
    nws_total, nws_extra = 0, 0
    for f in files:
        if os.path.basename(f).startswith('_keys_') or os.path.basename(f) in ('_watch_state.json',):
            continue
        nws_total += 1
        try:
            with open(f, 'rb') as fh:
                if b'"has_nws_extra": true' in fh.read():
                    nws_extra += 1
        except OSError:
            pass
    print('%-7s %-11s %9s %9d   %s'
          % ('nws', NWS_LAYER[1], '%d*' % nws_extra, nws_total, NWS_LAYER[2]))
    print('  (* records = net-new fragments folded into merge; headwords = scraped cards on disk)')
    # how many PWG headwords gain extra material from a later layer
    pwg = set(index('pwg'))
    for code, role, _ in LAYERS[1:]:
        k = set(index(code))
        print('  %s: %d headwords; %d NOT in PWG (net-new), %d also in PWG (overlay)'
              % (code, len(k), len(k - pwg), len(k & pwg)))


def cmd_merge(args):
    key1 = args[0]
    layers = merged(key1)
    if not layers:
        print('no entry for %r in any layer' % key1); return
    print('=== %s — %d layer(s) ===' % (key1, len(layers)))
    for L in layers:
        print('\n## [%s · %s] %s  (%d record(s))' % (L['layer'].upper(), L['role'], L['blurb'], len(L['records'])))
        for r in L['records']:
            print('  ' + re.sub(r'\s+', ' ', r)[:600])


def cmd_selftest(_args):
    cases = {
        '_ap~~h0_00_pwg01': 'pwg',     # base card
        '_ap~~h0_01_a_bi': 'pwg',      # preverb sub-card, still PWG layer
        'dah~~h0_zz_pw00': 'pw',
        '_ap~~h0_zz_pw01': 'pw',
        '_ap~~h0_zz_pwkvn': 'pwkvn',   # must NOT match 'pw'
        '_ap~~h0_zz_sch': 'sch',
        'dah~~h0_zz_nws00': 'nws',
        '': 'pwg',
    }
    for sub, want in cases.items():
        got = layer_of(sub)
        assert got == want, 'layer_of(%r) = %r, expected %r' % (sub, got, want)
    assert set(cases.values()) <= set(LAYER_VALUES)
    print('dict_merge.layer_of selftest OK (%d cases)' % len(cases))

    # resolve_lbody: an alternate-headword pointer resolves to the referenced entry's real
    # body; a non-pointer body is unchanged; an unresolvable id is left intact (no crash).
    assert resolve_lbody('pw', 'plain gloss') == 'plain gloss'
    assert resolve_lbody('pw', '{{Lbody=999999999}}') == '{{Lbody=999999999}}'
    resolved = resolve_lbody('pw', '{{Lbody=205646}}')
    assert '{{Lbody=' not in resolved and 'Abschrift' in resolved, \
        'Lbody pointer must resolve to the primary entry body, got %r' % resolved[:120]
    # and it flows through merged(): no CAyA pw record leaks a raw pointer
    caya_pw = [r for L in merged('CAyA') if L['layer'] == 'pw' for r in L['records']]
    assert caya_pw and all('{{Lbody=' not in r for r in caya_pw), 'merged() must resolve Lbody'
    print('dict_merge.resolve_lbody selftest OK')


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    {'stats': cmd_stats, 'merge': cmd_merge,
     'selftest': cmd_selftest}.get(sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:])


if __name__ == '__main__':
    main()
