#!/usr/bin/env python
"""renou_audit.py — inter-signal agreement audit of the Renou I–V tags.

Validation by *inter-signal agreement* (no human labels): for every dictionary's
canonical `{code}.renou.jsonl` it cross-tabulates the four provenance signals and
quantifies the dominant accuracy risk — `dcs` over-tagging. Because the DCS index
is keyed by bare lemma string, homographs collapse to one entry carrying the union
of all their eras (`akāra`, the letter, inherits I–V), and the per-state evidence
depth is discarded downstream. This tool re-joins each entry to `dcs_lemma_renou.json`
to recover lemma breadth + `n_texts`, treats `<ls>` (the lexicographer's own
citation) as the trusted anchor, and flags `dcs`-only states that ls/bhs do not
corroborate, ranked by over-tag risk.

  python renou_audit.py [--dir .] [--index dcs_lemma_renou.json]
                        [--out renou_audit_report.md] [--suspects N]

Headline metrics per dictionary:
  • ls∩dcs agreement among entries carrying BOTH signals
    (exact / dcs-adds-eras / dcs-misses-eras / conflict)
  • share of dcs state-assignments that are dcs-only (no ls, no bhs)
  • over-tag load: entries inheriting a maximal (5-state) dcs lemma
  • top suspect entries: dcs blows a tight ls span up to I–V on a high-frequency lemma
"""
import json, os, sys, glob, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

STATES = ('I', 'II', 'III', 'IV', 'V')
_ORDER = {s: i for i, s in enumerate(STATES)}
HERE = os.path.dirname(os.path.abspath(__file__))
# the canonical per-dictionary indices documented in RENOU.md; other *.renou.jsonl
# (assembled_cards, pwg_ru_translated) are derived card stores, not dict audits.
CANON = ('pwg', 'mw', 'pw', 'ap', 'ap90', 'ben', 'sch', 'bhs')


def load_dcs_index(path):
    d = json.load(open(path, encoding='utf-8'))
    d.pop('__sources__', None)
    return d


def relation(ls, dcs):
    """How dcs relates to the ls anchor (both non-empty sets)."""
    if ls == dcs:
        return 'exact'
    if ls < dcs:
        return 'dcs_adds'        # dcs widens the era span beyond what ls cites
    if dcs < ls:
        return 'dcs_misses'      # dcs narrower than ls
    return 'conflict'            # overlapping but neither contains the other


def audit_dict(path, dcs_index):
    code = os.path.basename(path).split('.')[0]
    st = {
        'code': code, 'entries': 0, 'ls_tagged': 0, 'dcs_hit': 0, 'both': 0,
        'rel': collections.Counter(),
        # dcs state-assignments by corroboration
        'dcs_state_total': 0, 'dcs_only_state': 0, 'dcs_corrob_state': 0,
        'dcs_only_by_state': collections.Counter(),
        'inherit_5state_lemma': 0,
        'suspects': [],
        # register axis
        'reg_entries': 0, 'reg_cov': collections.Counter(),
        'reg_by_src': {}, 'reg_low_info': 0,
    }
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        e = json.loads(line)
        st['entries'] += 1
        ls = set(e.get('renou_ls') or [])
        dcs = set(e.get('renou_dcs') or [])
        bhs = bool(e.get('renou_bhs'))
        prov = e.get('renou_provenance') or {}
        if ls:
            st['ls_tagged'] += 1
        if dcs:
            st['dcs_hit'] += 1
        if ls and dcs:
            st['both'] += 1
            st['rel'][relation(ls, dcs)] += 1

        # register axis: coverage + per-register provenance breakdown
        regs = e.get('renou_register') or []
        rp = e.get('renou_register_provenance') or {}
        if regs:
            st['reg_entries'] += 1
        if len(regs) >= 10:
            st['reg_low_info'] += 1
        for r in regs:
            st['reg_cov'][r] += 1
            srcs = set(rp.get(r, []))
            bucket = ('both' if {'ls', 'dcs'} <= srcs
                      else 'ls' if 'ls' in srcs else 'dcs' if 'dcs' in srcs else 'other')
            st['reg_by_src'].setdefault(r, collections.Counter())[bucket] += 1

        # corroboration of each dcs-assigned state
        for s in dcs:
            st['dcs_state_total'] += 1
            corrob = (s in ls) or (s == 'V' and bhs)
            if corrob:
                st['dcs_corrob_state'] += 1
            else:
                st['dcs_only_state'] += 1
                st['dcs_only_by_state'][s] += 1

        # over-tag load + suspect ranking. breadth = the entry's *emitted* dcs span
        # (post-policy); n_texts comes from the lemma index for frequency ranking.
        info = dcs_index.get(e.get('iast', ''))
        n_texts = info['n_texts'] if info else 0
        if len(dcs) == 5:
            st['inherit_5state_lemma'] += 1
        # a suspect: dcs widens a *tight* ls span (<=2 eras) to a broad one (>=4),
        # on a high-frequency lemma — the homograph/register-inflation signature.
        if ls and dcs and ls < dcs and len(ls) <= 2 and len(dcs) >= 4:
            added = sorted(dcs - ls, key=_ORDER.get)
            st['suspects'].append({
                'hw': clean_hw(e.get('key2') or e.get('iast')),
                'ls': sorted(ls, key=_ORDER.get), 'dcs': sorted(dcs, key=_ORDER.get),
                'added': added, 'n_texts': n_texts,
            })
    # dedup suspect rows by (headword, ls→dcs pattern); count affected entries
    # (a frequent headword like `ca` recurs once per sense — collapse to one row).
    agg = {}
    for r in st['suspects']:
        key = (r['hw'], tuple(r['ls']), tuple(r['dcs']))
        a = agg.get(key)
        if a is None:
            agg[key] = dict(r, count=1)
        else:
            a['count'] += 1
    st['suspects'] = sorted(agg.values(),
                            key=lambda r: (-r['n_texts'], -r['count'], -len(r['added'])))
    return st


def clean_hw(s):
    """A single-line headword label: some source key2 fields over-captured an XML
    block — keep only the bare form before any markup/newline."""
    s = (s or '').replace('\n', ' ').split('<')[0].split('{')[0].strip()
    return (s[:24] + '…') if len(s) > 25 else s


def fmt_pct(a, b):
    return '%.1f%%' % (100.0 * a / b) if b else '—'


def render(stats, n_suspects):
    L = ['# Renou tag audit — inter-signal agreement', '',
         'Automatic validation (no human labels). `<ls>` = trusted anchor; the focus',
         'is `dcs` over-tagging from homograph collapse in the lemma-keyed DCS index.', '']

    L += ['## ls∩dcs agreement (entries carrying BOTH signals)', '',
          '`exact` = same era span · `dcs_adds` = dcs widens beyond ls (the over-tag',
          'direction) · `dcs_misses` = dcs narrower · `conflict` = overlap, neither contains.', '',
          '| Dict | both | exact | dcs_adds | dcs_misses | conflict |',
          '|---|--:|--:|--:|--:|--:|']
    for s in stats:
        b = s['both']
        L.append('| %s | %d | %s | %s | %s | %s |' % (
            s['code'].upper(), b,
            fmt_pct(s['rel']['exact'], b), fmt_pct(s['rel']['dcs_adds'], b),
            fmt_pct(s['rel']['dcs_misses'], b), fmt_pct(s['rel']['conflict'], b)))

    L += ['', '## dcs state-assignments by corroboration', '',
          'Every (entry, state) pair `dcs` asserts: is that state also backed by `<ls>`',
          '(or `bhs` for V)? `dcs-only` states are unverified by any other signal.', '',
          '| Dict | dcs states | corroborated | dcs-only | dcs-only I·II·III·IV·V | entries tagged all 5 states |',
          '|---|--:|--:|--:|---|--:|']
    for s in stats:
        t = s['dcs_state_total']
        by = s['dcs_only_by_state']
        L.append('| %s | %d | %s | %s | %s | %d (%s of dcs-hit) |' % (
            s['code'].upper(), t,
            fmt_pct(s['dcs_corrob_state'], t), fmt_pct(s['dcs_only_state'], t),
            '·'.join(str(by.get(x, 0)) for x in STATES),
            s['inherit_5state_lemma'], fmt_pct(s['inherit_5state_lemma'], s['dcs_hit'])))

    L += ['', '## Top over-tag suspects', '',
          'Entries where `dcs` widens a tight ls span (≤2 eras) to ≥4, ranked by the',
          "lemma's DCS text frequency (homograph/register inflation is strongest on the",
          'most frequent lemmas).', '']
    for s in stats:
        if not s['suspects']:
            continue
        n_aff = sum(r['count'] for r in s['suspects'])
        L.append('### %s — %d distinct patterns over %d entries' % (
            s['code'].upper(), len(s['suspects']), n_aff))
        L.append('| headword | ls | dcs | added by dcs | lemma n_texts | entries |')
        L.append('|---|---|---|---|--:|--:|')
        for r in s['suspects'][:n_suspects]:
            L.append('| %s | %s | %s | %s | %d | %d |' % (
                r['hw'], '·'.join(r['ls']), '·'.join(r['dcs']),
                '·'.join(r['added']), r['n_texts'], r['count']))
        L.append('')

    L += render_registers(stats)
    return '\n'.join(L) + '\n'


# registers worth a focused inter-signal column (editorially salient / corpus-thin)
_KEY_REGS = ('bhasya', 'jaina', 'epig', 'natya', 'kavya')


def render_registers(stats):
    L = ['## Register axis (Renou subsections)', '',
         'Orthogonal to the state. Coverage = entries carrying ≥1 register; `low-info` =',
         'entries in ≥10 registers (era-neutral, register-uninformative). The state',
         'columns above are unaffected by this axis.', '',
         '| Dict | with-register | low-info | bhasya | jaina | épig | kavya |',
         '|---|--:|--:|--:|--:|--:|--:|']
    for s in stats:
        cov = s['reg_cov']
        L.append('| %s | %s | %d | %d | %d | %d | %d |' % (
            s['code'].upper(), fmt_pct(s['reg_entries'], s['entries']),
            s['reg_low_info'], cov.get('bhasya', 0), cov.get('jaina', 0),
            cov.get('epig', 0), cov.get('kavya', 0)))

    L += ['', '### Per-register provenance (ls-only · dcs-only · both)', '',
          'Which signal supports each editorially-key register. `ls` is the trusted',
          'citation route (the only source for `jaina`/`épig`); `dcs` is corpus attestation.', '']
    for s in stats:
        rows = [r for r in _KEY_REGS if s['reg_by_src'].get(r)]
        if not rows:
            continue
        L.append('**%s** — %s' % (s['code'].upper(), ' · '.join(
            '%s: %d/%d/%d (ls/dcs/both)' % (
                r, s['reg_by_src'][r].get('ls', 0), s['reg_by_src'][r].get('dcs', 0),
                s['reg_by_src'][r].get('both', 0)) for r in rows)))
    return L


def main():
    args = sys.argv[1:]
    d = HERE
    index_path = os.path.join(HERE, 'dcs_lemma_renou.json')
    out = os.path.join(HERE, 'renou_audit_report.md')
    n_suspects = 15
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--dir':
            d = args[i + 1]; i += 2
        elif a == '--index':
            index_path = args[i + 1]; i += 2
        elif a == '--out':
            out = args[i + 1]; i += 2
        elif a == '--suspects':
            n_suspects = int(args[i + 1]); i += 2
        else:
            raise SystemExit('unknown option: %s' % a)

    dcs_index = load_dcs_index(index_path)
    paths = [p for p in sorted(glob.glob(os.path.join(d, '*.renou.jsonl')))
             if os.path.basename(p).split('.')[0] in CANON]
    if not paths:
        raise SystemExit('no canonical {code}.renou.jsonl in %s' % d)
    order = {c: i for i, c in enumerate(CANON)}
    paths.sort(key=lambda p: order[os.path.basename(p).split('.')[0]])
    stats = [audit_dict(p, dcs_index) for p in paths]

    # console summary
    for s in stats:
        print('%-5s entries %6d · ls %5d · dcs %6d · dcs-only states %s · 5-state inherit %s'
              % (s['code'].upper(), s['entries'], s['ls_tagged'], s['dcs_hit'],
                 fmt_pct(s['dcs_only_state'], s['dcs_state_total']),
                 fmt_pct(s['inherit_5state_lemma'], s['dcs_hit'])))
        print('      register: %s of entries · bhasya %d · jaina %d · épig %d · low-info %d'
              % (fmt_pct(s['reg_entries'], s['entries']), s['reg_cov'].get('bhasya', 0),
                 s['reg_cov'].get('jaina', 0), s['reg_cov'].get('epig', 0), s['reg_low_info']))
    open(out, 'w', encoding='utf-8').write(render(stats, n_suspects))
    print('\n→ %s' % out)


if __name__ == '__main__':
    main()
