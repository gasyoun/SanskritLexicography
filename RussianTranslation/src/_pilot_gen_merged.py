#!/usr/bin/env python
"""Pilot input — the FULL layered card (PWG + PW + SCH + PWKVN + NWS net-new).

Extends _pilot_gen.py from PWG-only to the whole supplement chain, so the translator
produces ONE Russian entry that is the union of all layers. Per card key:
  • PWG base record(s) + their Nachträge   → microstructure portrait + labeled raw
  • PW (revision) / SCH (Schmidt) / PWKVN   → raw, layer-labeled (from dict_merge)
  • NWS net-new fragment                    → the ~2013 cumulative addendum (if any)

Output: src/pilot/input/<safe>.portrait.json + <safe>.raw.txt (gitignored), where
<safe> = safe_name(key) — the shared reversible Windows-safe stem, so SLP1's
case-sensitive keys (api/Api/ApI, as/As/aS) and PWG keys containing characters
like "|" don't collide or become unwritable on Windows.

  python _pilot_gen_merged.py [key ...]              default: a small NWS-exercising batch
  python _pilot_gen_merged.py --manifest a           whole a-section, coverage-first order
  python _pilot_gen_merged.py --manifest a --limit 300   first 300 of that order (scale slice)
  python _pilot_gen_merged.py --root-split BU gam        explode giant roots into per-prefix sub-cards
  python _pilot_gen_merged.py --manifest freq --root-split   freq queue, auto-splitting giant roots

--manifest reads scale_route.py's scale_manifest.<section>.json (run scale_route first),
so input generation follows the same coverage-first HEAVY/LIGHT ordering the scale driver
uses. Resumable: keys whose .raw.txt already exists are skipped.
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import microstructure as M
import dict_merge as dm
import corpus_gate as cg
import nws_split
from safe_filename import safe_name

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pilot', 'input')

sys.path.insert(0, os.path.join(HERE, '..', 'research'))
import root_segment_proto as RS                 # the lossless <div n="p"> root slicer

# Only explode genuinely GIANT roots (the ones that kill a single-pass translation);
# small records with 1-2 prefix divisions stay whole.
MIN_SPLIT = int(os.environ.get('ROOT_SPLIT_MIN', '8'))

DEFAULT = ['arTa', 'agni', 'amfta', 'aMSa', 'anna', 'akzara']


ROLE = {'pw': 'PW — Böhtlingk kürzere Fassung (revision of PWG; may correct gender/sense)',
        'sch': 'SCH — Schmidt Nachträge 1928 (pure addenda to PW; °=new vs pw, *=first attestation)',
        'pwkvn': 'PWKVN — PWK variant supplement (keyed to PW sense numbers)',
        'nws': 'NWS — Nachtragswörterbuch (Halle, cumulative addendum; condensed "Kleines Zitat" '
               '— render the new lemma/sense/grammar + keep its sigla)'}


# A roman-numeral co-owner cite (e.g. `Hillebrandt 1885 : IV`) that nws_split's
# digit-only OWNER can't tag rides onto the next entry — into the gloss as a
# leading `<tag> ; Name : page > …` bleed, into the tag as a stray `; Name :
# page`, and leaving a punctuation-only lemma. The owner stays correct; these
# strip the cosmetic contamination so the translator sees a clean gloss/tag
# (mirrors compile_translatable.mask_nws_gloss for the owner-map consumer path).
_BLEED_LEAD = re.compile(r'^[\s,;]*[^>]*?;\s*[A-ZÀ-ÖØ-ÞĀ-ỿ][^>:]*?\s:\s[\dIVXLCDM]+[A-Za-z]?\s*>\s*')
_BLEED_TAG = re.compile(r'\s*[;,]?\s*[A-ZÀ-ÖØ-ÞĀ-ỿ][^;,]*?\s:\s(?:\d+[A-Za-z]?|[IVXLCDM]+)')


def nws_owner_map(key):
    """The AUTHORITATIVE deterministic NWS (owner, gloss) pairing from nws_split —
    so the translator NEVER re-derives owners (kills F12 by construction). Reads the
    just-written <safe>.raw.txt so it sees exactly what `nws_split.py check` will."""
    frag = nws_split.nws_fragment(key)
    if not frag:
        return ''
    entries = nws_split.split(frag)
    if not entries:
        return ''
    lines = []
    for i, e in enumerate(entries, 1):
        owner = ' / '.join(e.get('owners') or []) or '?'
        gloss = _BLEED_LEAD.sub('', re.sub(r'\s+', ' ', e.get('gloss') or '').strip())
        for o in (e.get('owners') or []):            # drop a trailing copy of the cite
            if gloss.endswith(o):
                gloss = gloss[:-len(o)].rstrip(' .;,')
        lem = (e.get('lemma') or '').strip()
        lemma = (' {#%s#}' % lem) if re.search(r'[\wĀ-ỿ]', lem) else ''   # drop punct-only lemma
        tg = _BLEED_TAG.sub('', e.get('tag') or '').strip(' ;,')          # drop bled-in cite
        tag = (' [%s]' % tg) if tg else ''
        lines.append('%2d. [NWS: %s]%s%s %s' % (i, owner, lemma, tag, gloss))
    return '\n'.join(lines)


def gen_card(key, pwg_idx, verbose=True):
    """Write <key>.portrait.json + <key>.raw.txt for one headword. Returns the
    per-layer record counts (incl. 'nws'), or None if the key is absent from PWG."""
    fk = cg.form_key(key)
    pwg_bufs = pwg_idx.get(fk, [])
    if not pwg_bufs:
        if verbose:
            print('  MISSING in PWG: %s' % key)
        return None

    # 1) PWG portrait (corpus evidence) + labeled raw records (main + Nachträge)
    portraits = [M.portrait(buf) for buf in pwg_bufs]
    json.dump(portraits, open(os.path.join(OUT, safe_name(key) + '.portrait.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    sections = []
    for i, buf in enumerate(pwg_bufs):
        role = ('PWG — MAIN ENTRY (Böhtlingk-Roth, large)' if i == 0 else
                'PWG — NACHTRÄGE/ADDENDA #%d — patches keyed to the main sense numbers; '
                'render in full' % i)
        sections.append('=== LAYER: %s ===\n\n%s' % (role, '\n'.join(buf[1:])))

    # 2) PW / SCH / PWKVN + NWS net-new layers (all from the merge), each labeled.
    #    dm.merged() now owns the NWS fold — it appends the external addendum last
    #    when (and only when) it adds beyond pw/Schmidt (has_nws_extra).
    layer_counts = {'pwg': len(pwg_bufs)}
    for L in dm.merged(key):
        code = L['layer']
        if code == 'pwg':
            continue
        layer_counts[code] = len(L['records'])
        for r in L['records']:
            sections.append('=== LAYER: %s ===\n\n%s' % (ROLE.get(code, code.upper()), r))

    raw_path = os.path.join(OUT, safe_name(key) + '.raw.txt')
    open(raw_path, 'w', encoding='utf-8').write('\n\n'.join(sections))

    # 3) append the AUTHORITATIVE deterministic NWS owner map (reads the file just
    #    written, so it matches the F12 gate exactly). The translator emits one row
    #    per entry with the owner verbatim — it does NOT re-derive owners.
    if layer_counts.get('nws'):
        omap = nws_owner_map(key)
        if omap:
            n_entries = omap.count('\n') + 1
            sections.append(
                '=== LAYER: NWS — PRE-PARSED OWNER MAP (AUTHORITATIVE, %d entries) ===\n\n'
                'Deterministic owner-to-gloss pairing (kills F12). Emit EXACTLY one card row\n'
                'per numbered entry below, in this order; copy its [NWS: OWNER] VERBATIM as the\n'
                'row’s last citation; translate the gloss from its own language; keep IAST/sigla.\n'
                'Do NOT re-derive owners from the raw fragment above.\n\n%s' % (n_entries, omap))
            open(raw_path, 'w', encoding='utf-8').write('\n\n'.join(sections))
            layer_counts['nws_map'] = n_entries
    if verbose:
        ns = sum(len([s for s in p['senses'] if s['n'] != '0']) for p in portraits)
        print('  %-10s PWG rec=%d senses=%d | PW=%d SCH=%d PWKVN=%d | NWS-extra=%s'
              % (key, len(pwg_bufs), ns, layer_counts.get('pw', 0), layer_counts.get('sch', 0),
                 layer_counts.get('pwkvn', 0), 'yes' if layer_counts.get('nws') else 'no'))
    return layer_counts


def gen_root_split(key, pwg_idx, verbose=True):
    """--root-split: explode a GIANT root record into one single-pass-sized sub-card per
    prefix (the fix for 'translation pass dies on bhū/vid'). The HEAD sub-card (simple verb)
    carries the PW/SCH/PWKVN/NWS supplements + owner map exactly as gen_card; each PREFIX
    sub-card is just its <div n="p"> block. Writes <safe>~~NN[_upa].raw.txt per sub-card and
    <safe>.rootmap.json (root_key/upasarga/seg_index, parse order) so root_glue can reassemble.
    Returns sub-card count, or None if the key is absent / not giant (caller falls back)."""
    fk = cg.form_key(key)
    bufs = pwg_idx.get(fk, [])
    if not bufs:
        return None
    datalines = [l for l in bufs[0] if not (l.startswith('<L>') or l.startswith('<LEND>'))]
    cards = RS.segment(datalines)
    npfx = sum(1 for c in cards if c['kind'] == 'prefix')
    if npfx < MIN_SPLIT:
        return None                                 # not giant — let gen_card handle it whole
    root = safe_name(key)
    submap = []
    for seg, c in enumerate(cards):
        upa = c['upasarga']
        sub = '%s~~%02d%s' % (root, seg, '_' + safe_name(upa) if upa else '')
        if c['kind'] == 'prefix':
            hdr = ('PWG-ROOT SUBCARD — root=%s upasarga=%s seg=%d (prefixed verb, nested in '
                   'the %s root article; root_key links it back)' % (key, upa, seg, key))
            secs = ['=== LAYER: %s ===\n\n%s' % (hdr, '\n'.join(c['lines']))]
        else:
            hdr = ('PWG-ROOT HEAD — root=%s seg=%d (simple verb + senses; the supplement '
                   'layers attach to this head card)' % (key, seg))
            secs = ['=== LAYER: %s ===\n\n%s' % (hdr, '\n'.join(c['lines']))]
            for L in dm.merged(key):                # PW / SCH / PWKVN / NWS on the head only
                if L['layer'] == 'pwg':
                    continue
                for r in L['records']:
                    secs.append('=== LAYER: %s ===\n\n%s' % (ROLE.get(L['layer'], L['layer'].upper()), r))
            omap = nws_owner_map(key)
            if omap:
                secs.append(
                    '=== LAYER: NWS — PRE-PARSED OWNER MAP (AUTHORITATIVE, %d entries) ===\n\n'
                    'Emit EXACTLY one card row per numbered entry; copy its [NWS: OWNER] VERBATIM;\n'
                    'translate the gloss from its own language; keep IAST/sigla. Do NOT re-derive '
                    'owners.\n\n%s' % (omap.count('\n') + 1, omap))
        open(os.path.join(OUT, sub + '.raw.txt'), 'w', encoding='utf-8').write('\n\n'.join(secs))
        json.dump([], open(os.path.join(OUT, sub + '.portrait.json'), 'w', encoding='utf-8'))
        submap.append({'subkey': sub, 'seg_index': seg, 'kind': c['kind'],
                       'upasarga': upa, 'root_key': key})
    json.dump({'root': key, 'safe': root, 'sub_cards': submap},
              open(os.path.join(OUT, root + '.rootmap.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    if verbose:
        print('  %-10s ROOT-SPLIT → %d sub-cards (1 head + %d prefix) → %s~~*.raw.txt + rootmap'
              % (key, len(cards), npfx, root))
    return len(cards)


def manifest_keys(section):
    p = os.path.join(HERE, 'pilot', 'output', 'scale_manifest.%s.json' % section)
    if not os.path.exists(p):
        sys.exit('no manifest %s — run: python scale_route.py %s' % (os.path.basename(p), section))
    return [e['key1'] for e in json.load(open(p, encoding='utf-8'))]


def main():
    args = sys.argv[1:]
    limit = None
    root_split = '--root-split' in args
    if root_split:
        args.remove('--root-split')
    if '--limit' in args:
        i = args.index('--limit'); limit = int(args[i + 1]); del args[i:i + 2]
    if '--manifest' in args:
        i = args.index('--manifest'); section = args[i + 1]; del args[i:i + 2]
        keys = manifest_keys(section)
        scaled = True
    else:
        keys = args or DEFAULT
        scaled = False
    if limit is not None:
        keys = keys[:limit]

    os.makedirs(OUT, exist_ok=True)
    pwg_idx = dm.index('pwg')

    def is_merged(key):
        """Done (skip) iff a current MERGED input exists AND (it has no NWS layer
        or it already carries the owner map). Regenerate: (a) superseded PWG-only
        _pilot_gen.py outputs ('=== RECORD' format, no '=== LAYER:'), and (b) merged
        inputs written before the owner-map feed (have an NWS layer but no map)."""
        p = os.path.join(OUT, safe_name(key) + '.raw.txt')
        try:
            with open(p, encoding='utf-8') as f:
                t = f.read()
        except OSError:
            return False
        if '=== LAYER:' not in t[:200]:
            return False
        has_nws = '=== LAYER: NWS' in t
        return (not has_nws) or ('PRE-PARSED OWNER MAP' in t)

    # resumable in scaled runs: skip only keys already written in merged format
    todo = [k for k in keys if not (scaled and is_merged(k))]
    print('merged pilot: %d key(s)%s, %d to generate'
          % (len(keys), ' [scaled, resumable]' if scaled else '', len(todo)))

    n = missing = with_nws = split_roots = split_subcards = 0
    errored = []                       # keys unwritable on this FS (e.g. '|' in arI|a)
    lc_tot = {'pw': 0, 'sch': 0, 'pwkvn': 0, 'nws': 0}
    for j, key in enumerate(todo, 1):
        try:
            if root_split:
                nsub = gen_root_split(key, pwg_idx, verbose=not scaled)
                if nsub is not None:   # giant root -> exploded into sub-cards; skip whole-card gen
                    split_roots += 1
                    split_subcards += nsub
                    continue
            lc = gen_card(key, pwg_idx, verbose=not scaled)
        except OSError as e:           # one bad key must not kill an 11k-card run
            errored.append(key)
            print('  SKIP (unwritable: %s): %r' % (e.strerror or e, key))
            continue
        if lc is None:
            missing += 1
            continue
        n += 1
        for code in lc_tot:
            lc_tot[code] += 1 if lc.get(code) else 0
        if lc.get('nws'):
            with_nws += 1
        if scaled and j % 200 == 0:
            print('  [%d/%d] generated; NWS-extra so far %d' % (j, len(todo), with_nws))
            sys.stdout.flush()

    print('wrote %d merged pilot inputs → %s%s%s'
          % (n, OUT, (' (%d missing in PWG)' % missing) if missing else '',
             (' (%d unwritable: %s)' % (len(errored), errored)) if errored else ''))
    if root_split and split_roots:
        print('  ROOT-SPLIT: %d giant root(s) exploded into %d sub-cards (+ rootmap.json each)'
              % (split_roots, split_subcards))
    if scaled and n:
        print('  layer coverage: PW %d (%.0f%%)  SCH %d (%.0f%%)  PWKVN %d (%.0f%%)  NWS-extra %d (%.0f%%)'
              % (lc_tot['pw'], 100 * lc_tot['pw'] / n, lc_tot['sch'], 100 * lc_tot['sch'] / n,
                 lc_tot['pwkvn'], 100 * lc_tot['pwkvn'] / n, with_nws, 100 * with_nws / n))


if __name__ == '__main__':
    main()
