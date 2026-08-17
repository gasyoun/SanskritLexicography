#!/usr/bin/env python
r"""key1 / wrong-entry-ingestion repair proposals for the pwg_ru store
(FINDINGS s560 follow-through, issue #1767).

What the witnesses actually show (established 17-08-2026, this script's first
run + the vasa/bara row dumps): the store's defect is NOT primarily a degraded
key1. In 61 of 73 disagreement groups the card's own printed head ({#lemma#}|)
AGREES with key1 against the subcard — because the ingestion, looking up the
INTENDED lemma (preserved in the subcard prefix: vAsA, BAra, Apta, aSru...),
fetched the flattened-key LOOK-ALIKE entry instead (vasa, bara, apta, asru...)
and stored that entry's content under the intended lemma's subcard. Where one
flattened key covered several intended lemmas, the same wrong card was stored
VERBATIM once per lemma (key1 'vasa': the tiny vasa nom.-act. stub appears five
times, under vAsA/vAsa/vaSA/vaSa/vasA — whose real PWG entries are therefore
MISSING from the store).

The store is read-only and voted: this script derives PROPOSALS; a human votes
them in the sheet built by build_key1_repair_sheet.py; application (re-ingest +
quarantine) is a separate, gated pass.

Witnesses per card-group (rows sharing the subcard prefix before '~~'):
  key1     - stored key (matches what was actually FETCHED)
  subcard  - decode of the subcard prefix, '_c' -> uppercase C (the INTENDED
             lemma of the worklist)
  iast     - row iast via sanskrit_util.to_slp1 (canonical transcoder)
  de_head  - the lemma the card's German text PRINTS ({#lemma#}| / {%..%} for
             SCH) - ground truth for which entry the content belongs to

Classes emitted:
  wrong_entry_dup   - >=2 sibling groups of one key1 carry IDENTICAL content
                      under different intended lemmas: wrong-entry ingestion
                      PROVEN; every intended lemma except the printed one is
                      missing from the store
  wrong_entry       - single group, print+key1 agree against the intended
                      subcard lemma, and the two words are UNRELATED (advan
                      "eating" vs aDvan "road" - a pure d/D flattening
                      collision): wrong-entry ingestion suspected
  wrong_entry_xref  - same mechanism, but the ingested card itself PRINTS the
                      intended lemma (anukampa "s. anukampA" gender pair; asru
                      "s. aSru" spelling cross-ref): a related stub pointing at
                      the target (MG 17-08-2026: never label these two shapes
                      identically)
  junk_key1         - key1 carries subcard machinery (durg_a~~h0_zz_sch):
                      mechanical key fix, content unaffected
  variant_head      - the printed head lists several variants (cakraka,
                      cakrikA; ozaDi/ozaDI): one card for several forms,
                      likely NOT a defect - listed for human confirmation
  rename            - remaining disagreements: plain key correction proposed

  input  : pwg_ru_translated.jsonl (read-only; --store / PWG_RU_STORE)
  output : ../pwg_ru/key1_repair_proposals.jsonl

  python src/key1_repair_proposals.py --selftest
  python src/key1_repair_proposals.py
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GITHUB = os.path.normpath(os.path.join(REPO, '..', '..'))
sys.path.insert(0, os.path.join(GITHUB, 'sanskrit-util', 'py'))
from sanskrit_util import to_slp1     # noqa: E402  (canonical transcoder, SHARED_CODE)

STORE = os.environ.get('PWG_RU_STORE', os.path.join(
    GITHUB, 'SanskritLexicography', 'RussianTranslation', 'src', 'pwg_ru_translated.jsonl'))
OUT = os.path.join(REPO, 'pwg_ru', 'key1_repair_proposals.jsonl')

_SUBCARD_CAP = re.compile(r'_([a-z])')
_ACCENTS = re.compile(r'[/\\^~˚—.\s]')
_DE_SLP = re.compile(r'\{#([^#]+)#\}[^¦]{0,40}¦')
_DE_IAST = re.compile(r'\{%([^%]+)%\}[^¦]{0,40}¦')


def decode_subcard(subcard):
    pre = subcard.split('~~')[0]
    return _SUBCARD_CAP.sub(lambda m: m.group(1).upper(), pre)


def _clean(tok):
    return _ACCENTS.sub('', tok.strip())


def de_head_lemma(de, layer):
    if not de or '¦' not in de:
        return []
    head = de.split('¦', 1)[0] + '¦'
    pat = _DE_IAST if layer == 'sch' else _DE_SLP
    out = []
    for m in pat.finditer(head):
        for piece in re.split(r'[,;]| und | oder ', m.group(1)):
            tok = _clean(piece)
            if not tok or '˚' in piece:
                continue
            if layer == 'sch':
                tok = to_slp1(tok)
            if re.fullmatch(r'[a-zA-Z]+', tok):
                out.append(tok)
    return out


def iast_witness(iast):
    if not iast:
        return None
    tok = _clean(iast)
    if not tok:
        return None
    slp = to_slp1(tok)
    return slp if re.fullmatch(r'[a-zA-Z]+', slp) else None


_BODY_SLP = re.compile(r'\{#(.*?)#\}', re.S)
_BODY_IAST = re.compile(r'\{%(.*?)%\}', re.S)


def intended_in_body(grp, intended):
    """True when any row's de text prints the intended lemma as an exact
    Sanskrit token (cross-reference / gender-pair stubs: anukampa "s.
    anukampA", asru "s. aSru") - substring hits (agrAdvan) do not count."""
    for r in grp:
        de = r.get('de') or ''
        toks = set()
        for m in _BODY_SLP.finditer(de):
            toks.update(_clean(t) for t in re.split(r'[,;+\s]+', m.group(1)))
        for m in _BODY_IAST.finditer(de):
            for t in re.split(r'[,;+\s]+', m.group(1)):
                t = _clean(t)
                if re.fullmatch(r'[a-zA-ZāīūṛṝḷṅñṭḍṇśṣṃḥĀĪŪṚṜḶṄÑṬḌṆŚṢṂḤ]+', t):
                    toks.add(to_slp1(t))
        if intended in toks:
            return True
    return False


def content_sig(grp):
    """Order-independent content signature of a card-group's rows."""
    return tuple(sorted((str(r.get('sense_tag')), (r.get('de') or '').strip())
                        for r in grp))


def classify_key1(key1, subgroups):
    """subgroups: {subcard_decode: rows}. Yield proposal dicts (no 'ok' rows)."""
    heads_by_sub, iasts_by_sub = {}, {}
    for sd, grp in subgroups.items():
        hs = []
        for r in grp:
            hs.extend(de_head_lemma(r.get('de') or '', r['layer']))
        heads_by_sub[sd] = hs
        iasts_by_sub[sd] = [w for w in (iast_witness(r.get('iast')) for r in grp) if w]

    junk = not re.fullmatch(r'[a-zA-Z]+', key1)
    diff_subs = [sd for sd in subgroups if sd != key1]
    if not diff_subs and not junk:
        return   # every group's intended lemma == key1: nothing to judge here

    # proven duplication: identical content under >=2 different intended lemmas
    sigs = defaultdict(list)
    for sd, grp in subgroups.items():
        sigs[content_sig(grp)].append(sd)
    dup_sets = [sds for sds in sigs.values() if len(sds) >= 2 and len(set(sds)) >= 2]

    for sds in dup_sets:
        printed = sorted({h for sd in sds for h in heads_by_sub[sd]})
        yield {
            'class': 'wrong_entry_dup',
            'key1': key1,
            'intended_lemmas': sorted(sds),
            'printed_head': printed,
            'rows_affected': sum(len(subgroups[sd]) for sd in sds),
            'action': 're-ingest each intended lemma; quarantine the duplicated look-alike rows',
        }
    dup_flat = {sd for sds in dup_sets for sd in sds}

    for sd in sorted(subgroups):
        if sd in dup_flat:
            continue
        grp = subgroups[sd]
        heads = heads_by_sub[sd]
        if junk:
            yield {
                'class': 'junk_key1', 'key1': key1, 'intended_lemmas': [sd],
                'printed_head': sorted(set(heads)),
                'rows_affected': len(grp),
                'action': 'mechanical: set key1 to the decoded subcard lemma',
            }
            continue
        if sd == key1:
            continue
        if heads and sd in heads:
            yield {
                'class': 'variant_head', 'key1': key1, 'intended_lemmas': [sd],
                'printed_head': sorted(set(heads)),
                'rows_affected': len(grp),
                'action': 'one printed card covers several variant forms - confirm no defect',
            }
        elif heads and key1 in heads:
            # MG 17-08-2026: two different situations must not share one label.
            # If the ingested card ITSELF prints the intended lemma in its body
            # (anukampa "s. anukampA" - the m./f. pair; asru "s. aSru" - a
            # spelling cross-ref), the pair is RELATED and the stub even points
            # at the target. If not (advan "essend" vs aDvan "road"), the two
            # words share nothing but the d/D flattening collision.
            related = intended_in_body(grp, sd)
            yield {
                'class': 'wrong_entry_xref' if related else 'wrong_entry',
                'key1': key1, 'intended_lemmas': [sd],
                'printed_head': sorted(set(heads)),
                'rows_affected': len(grp),
                'action': 're-ingest the intended lemma; quarantine the '
                          + ('cross-ref stub rows (the stub already points at the target)'
                             if related else 'unrelated look-alike rows'),
            }
        else:
            yield {
                'class': 'rename', 'key1': key1, 'intended_lemmas': [sd],
                'printed_head': sorted(set(heads)),
                'rows_affected': len(grp),
                'action': 'set key1 to %s (no printed-head arbitration)' % sd,
            }


def selftest():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    check('decode', decode_subcard('_sud_davidy_a~~h0_zz_sch') == 'SudDavidyA')
    check('head-accent', de_head_lemma('{#a/tura#}¦ (3. {#a + tura#})', 'pwg') == ['atura'])
    check('head-sch', de_head_lemma('{%kalaśī%}¦ 1. f. Topf', 'sch') == ['kalaSI'])
    check('iast', iast_witness('ghaṭa') == 'Gawa')

    mk = lambda sd, tag, de: {'subcard': sd, 'sense_tag': tag, 'de': de, 'layer': 'pwg', 'iast': None}
    stub = '{#vasa#}¦ <ab>nom. act.</ab>'
    props = list(classify_key1('vasa', {
        'vAsA': [mk('vAsA', '1', stub)], 'vaSa': [mk('vaSa', '1', stub)]}))
    check('dup', [p['class'] for p in props] == ['wrong_entry_dup']
          and props[0]['intended_lemmas'] == ['vAsA', 'vaSa'])

    props = list(classify_key1('apta', {'Apta': [mk('Apta', '1', '{#apta#}¦ adj.')]}))
    check('wrong-entry', [p['class'] for p in props] == ['wrong_entry'])

    # MG 17-08-2026: a cross-ref/gender-pair stub is NOT the same defect as an
    # unrelated flattening collision - the two get distinct classes.
    props = list(classify_key1('anukampa', {'anukampA': [
        mk('anukampA', '1', '{#anukampa#}¦ <ab>s.</ab> {#anukampA#} .')]}))
    check('xref-related', [p['class'] for p in props] == ['wrong_entry_xref'])
    props = list(classify_key1('advan', {'aDvan': [
        mk('aDvan', '1', '{#advan#}¦ (von 1. {#ad#}) adj. essend; s. {#agrAdvan#} .')]}))
    check('collision-unrelated', [p['class'] for p in props] == ['wrong_entry'])

    props = list(classify_key1('cakrikA', {'cakrikA': [], 'cakraka': [
        mk('cakraka', '1', '{#cakraka#}, {#cakrikA#}¦ f.')]}))
    check('variant', any(p['class'] == 'variant_head' for p in props))

    props = list(classify_key1('durg_a~~h0_zz_sch', {'durgA': [mk('durgA', '1', '{%durgā%}¦ x')]}))
    check('junk', [p['class'] for p in props] == ['junk_key1'])

    props = list(classify_key1('Ap', {'Ap': [mk('Ap', '1', '{#Ap#}¦')]}))
    check('ok-silent', props == [])

    if fails:
        print('SELFTEST FAIL:', ', '.join(fails))
        return 1
    print('selftest: 11/11 ok')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--store', default=STORE)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    rows = [json.loads(l) for l in open(args.store, encoding='utf-8') if l.strip()]
    by_key1 = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_key1[r['key1']][decode_subcard(r['subcard'])].append(r)

    out = []
    for key1 in sorted(by_key1):
        for p in classify_key1(key1, by_key1[key1]):
            p['id'] = 'k1r-%03d' % (len(out) + 1)
            sd = p['intended_lemmas'][0]
            g0 = by_key1[key1].get(sd) or next(iter(by_key1[key1].values()))
            p['sample_de'] = re.sub(r'\s+', ' ', (g0[0].get('de') or ''))[:160]
            p['layers'] = sorted({r['layer'] for sd2 in p['intended_lemmas']
                                  for r in by_key1[key1].get(sd2, [])})
            out.append(p)

    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    counts = defaultdict(int)
    for p in out:
        counts[p['class']] += 1
    total_groups = sum(len(v) for v in by_key1.values())
    print('key1 clusters: %d | card-groups: %d | proposals: %d  (%s)' % (
        len(by_key1), total_groups, len(out),
        ', '.join('%s %d' % kv for kv in sorted(counts.items()))))
    print('rows implicated:', sum(p['rows_affected'] for p in out))
    print('->', OUT)
    return 0


if __name__ == '__main__':
    sys.exit(main())
