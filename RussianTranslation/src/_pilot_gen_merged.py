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

DEFAULT = ['arTa', 'agni', 'amfta', 'aMSa', 'anna', 'akzara']


ROLE = {'pw': 'PW — Böhtlingk kürzere Fassung (revision of PWG; may correct gender/sense)',
        'sch': 'SCH — Schmidt Nachträge 1928 (pure addenda to PW; °=new vs pw, *=first attestation)',
        'pwkvn': 'PWKVN — PWK variant supplement (keyed to PW sense numbers)',
        'nws': 'NWS — Nachtragswörterbuch (Halle, cumulative addendum; condensed "Kleines Zitat" '
               '— render the new lemma/sense/grammar + keep its sigla)'}


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
        gloss = re.sub(r'\s+', ' ', e.get('gloss') or '').strip()
        for o in (e.get('owners') or []):            # drop a trailing copy of the cite
            if gloss.endswith(o):
                gloss = gloss[:-len(o)].rstrip(' .;,')
        lemma = (' {#%s#}' % e['lemma']) if e.get('lemma') else ''
        tag = (' [%s]' % e['tag']) if e.get('tag') else ''
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


def manifest_keys(section):
    p = os.path.join(HERE, 'pilot', 'output', 'scale_manifest.%s.json' % section)
    if not os.path.exists(p):
        sys.exit('no manifest %s — run: python scale_route.py %s' % (os.path.basename(p), section))
    return [e['key1'] for e in json.load(open(p, encoding='utf-8'))]


def main():
    args = sys.argv[1:]
    limit = None
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
        """True only if a current MERGED input already exists. The superseded
        PWG-only _pilot_gen.py writes the SAME <safe>.raw.txt name in '=== RECORD'
        format — those must be regenerated, not skipped as done."""
        p = os.path.join(OUT, safe_name(key) + '.raw.txt')
        try:
            with open(p, encoding='utf-8') as f:
                return '=== LAYER:' in f.read(200)
        except OSError:
            return False

    # resumable in scaled runs: skip only keys already written in merged format
    todo = [k for k in keys if not (scaled and is_merged(k))]
    print('merged pilot: %d key(s)%s, %d to generate'
          % (len(keys), ' [scaled, resumable]' if scaled else '', len(todo)))

    n = missing = with_nws = 0
    errored = []                       # keys unwritable on this FS (e.g. '|' in arI|a)
    lc_tot = {'pw': 0, 'sch': 0, 'pwkvn': 0, 'nws': 0}
    for j, key in enumerate(todo, 1):
        try:
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
    if scaled and n:
        print('  layer coverage: PW %d (%.0f%%)  SCH %d (%.0f%%)  PWKVN %d (%.0f%%)  NWS-extra %d (%.0f%%)'
              % (lc_tot['pw'], 100 * lc_tot['pw'] / n, lc_tot['sch'], 100 * lc_tot['sch'] / n,
                 lc_tot['pwkvn'], 100 * lc_tot['pwkvn'] / n, with_nws, 100 * with_nws / n))


if __name__ == '__main__':
    main()
