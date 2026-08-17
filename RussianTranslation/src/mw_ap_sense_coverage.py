#!/usr/bin/env python
r"""Wave 4 (issue #1736, H2882): which MW / AP senses are ABSENT from the PWG family.

Compares, for every headword in the pwg_ru store (the 254-headword universe where
waves 1-3 established what the PWG family actually has), the sense inventories of
Monier-Williams (MW, 1899) and Apte (AP90, 1890) against the union of the family
layers in the store (pwg / pw / sch / pwkvn / nws), and classifies every MW/AP
sense unit into a THREE-way verdict -- the explicit "absent" vs "not linkable"
separation this wave exists for:

  matched          -- the sense shares >= 2 anchor points with some family sense
  unalignable      -- the sense exposes < 2 Sanskrit anchors: the method has no
                      fair chance of finding it, so NO absence claim is made
  absent_candidate -- the sense exposes >= 2 anchors and NONE overlap any family
                      sense of the same headword

Method (declared before the run; reuses the csl-atlas A09 "anchor on Sanskrit"
idea -- deterministic, translation-free): a sense is fingerprinted by the SLP1
Sanskrit material it cites (MW ``<s>..</s>``, AP/PWG ``{#..#}``) plus its
``<ls>`` citations normalized to (WORK, digits) anchors with roman numerals
converted. Gloss-text overlap is deliberately NOT used (FINDINGS s541 rejected
it). The costly error here is a FALSE "absent" (that is exactly the
label-vs-linkage confusion waves 1-3 repaired inside the family), so every
threshold is chosen to under-claim absence: over-matching is the cheap error,
thin fingerprints abstain instead of claiming.

Sense units:
  MW   -- one ``<L>`` record of csl-orig mw.txt (Cologne's own segmentation;
          no invented splitter),
  AP90 -- one ``{@N@}`` segment of the entry (the digitisation's printed sense
          numbers); the text before the first marker is segment "pre"
          (etymology/grammar header) and is reported separately.

  inputs : csl-orig/v02/mw/mw.txt, csl-orig/v02/ap90/ap90.txt   (read-only)
           pwg_ru_translated.jsonl                              (read-only store;
           not in git -- pass --store or PWG_RU_STORE, defaults to the canonical
           main-tree location)
  output : ../pwg_ru/mw_ap_sense_coverage.jsonl  (one row per MW/AP sense unit)
           ../pwg_ru/mw_ap_sense_coverage_summary.json

  python src/mw_ap_sense_coverage.py             # full run
  python src/mw_ap_sense_coverage.py --selftest  # fixture checks, no I/O
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GITHUB = os.path.normpath(os.path.join(REPO, '..', '..'))
MW_TXT = os.environ.get('MW_TXT', os.path.join(GITHUB, 'csl-orig', 'v02', 'mw', 'mw.txt'))
AP_TXT = os.environ.get('AP90_TXT', os.path.join(GITHUB, 'csl-orig', 'v02', 'ap90', 'ap90.txt'))
# The canonical store is deliberately not in git; default to the main-tree copy.
STORE = os.environ.get('PWG_RU_STORE', os.path.join(
    GITHUB, 'SanskritLexicography', 'RussianTranslation', 'src', 'pwg_ru_translated.jsonl'))
OUT_ROWS = os.path.join(REPO, 'pwg_ru', 'mw_ap_sense_coverage.jsonl')
OUT_SUMMARY = os.path.join(REPO, 'pwg_ru', 'mw_ap_sense_coverage_summary.json')

# ---------------------------------------------------------------- fingerprints

_S_MW = re.compile(r'<s>(.*?)</s>', re.S)
_S_BRACE = re.compile(r'\{#(.*?)#\}', re.S)
_LS = re.compile(r'<ls(?:\s+n="([^"]*)")?>(.*?)</ls>', re.S)
_WORD = re.compile(r'[a-zA-Z]+')
_ROMAN = re.compile(r'^[ivxlcdm]+$')

# ultra-common function words that anchor nothing
_STOP = {'iti', 'ca', 'na', 'vA', 'api', 'tu', 'hi', 'a'}

# sigla that converge after diacritic-strip + upper everywhere EXCEPT these
_WORK_ALIAS = {'MN': 'M'}          # MW cites Manu as Mn., PWG as M.

_ROMAN_VAL = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000}


def _roman_to_int(tok):
    total, prev = 0, 0
    for ch in reversed(tok):
        v = _ROMAN_VAL[ch]
        total = total - v if v < prev else total + v
        prev = max(prev, v)
    return total


def sanskrit_tokens(chunks, headword):
    """Informative SLP1 tokens from the Sanskrit-material chunks of one sense."""
    toks = set()
    for chunk in chunks:
        for w in _WORD.findall(chunk):
            if len(w) < 2 or w in _STOP or w == headword:
                continue
            toks.add(w)
    return toks


def _norm_work(name):
    s = unicodedata.normalize('NFD', name)
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    s = re.sub(r'[^A-Za-z]', '', s).upper()
    return _WORK_ALIAS.get(s, s)


def citation_anchors(text):
    """(WORK, (n1, n2, ...)) anchors from <ls> elements; roman numerals -> ints."""
    anchors = set()
    for n_attr, visible in _LS.findall(text):
        work_src = n_attr
        if not work_src:
            parts = []
            for tok in visible.split():
                bare = tok.strip('.,;')
                # sigla are capitalized (M., RV.); roman numerals are lowercase
                if bare and (bare[0].isdigit() or _ROMAN.match(bare)):
                    break
                parts.append(tok)
            work_src = ' '.join(parts)
        work = _norm_work(work_src)
        nums = []
        for tok in re.findall(r'[0-9]+|\b[ivxlcdm]+\b', visible):
            nums.append(_roman_to_int(tok) if _ROMAN.match(tok) else int(tok))
        if work and nums:
            anchors.add((work, tuple(nums)))
    return anchors


def fingerprint(text, headword, sanskrit_re):
    return {
        'tokens': sanskrit_tokens(sanskrit_re.findall(text), headword),
        'cits': citation_anchors(text),
    }


def score_pair(fp_a, fp_b):
    shared_t = fp_a['tokens'] & fp_b['tokens']
    shared_c = fp_a['cits'] & fp_b['cits']
    return len(shared_t) + 2 * len(shared_c), shared_t, shared_c


MATCH_MIN = 2          # >= 2 shared anchor points ==> matched
ANCHOR_MIN = 2         # < 2 own anchors ==> unalignable (abstain, never "absent")


def is_anchored(fp):
    return len(fp['tokens']) + len(fp['cits']) >= ANCHOR_MIN


def verdict(fp, family_fps):
    """(verdict, best_idx, best_score, shared_tokens, shared_cits)

    An absence claim additionally requires that the family side offered
    something to match against: if NO family sense of this lemma is anchored,
    the miss says nothing about the dictionary -- verdict family_thin, not
    absent_candidate (same abstention logic as placement=false in wave 1).
    """
    best = (0, set(), set(), None)
    for i, ffp in enumerate(family_fps):
        s, st, sc = score_pair(fp, ffp)
        if s > best[0]:
            best = (s, st, sc, i)
    n_anchor = len(fp['tokens']) + len(fp['cits'])
    if best[0] >= MATCH_MIN:
        return 'matched', best[3], best[0], best[1], best[2]
    if n_anchor < ANCHOR_MIN:
        return 'unalignable', None, best[0], set(), set()
    if not any(is_anchored(ffp) for ffp in family_fps):
        return 'family_thin', None, best[0], set(), set()
    return 'absent_candidate', None, best[0], set(), set()


# The store's key1 field is DEGRADED for 161 rows (case/aspiration/diacritic
# flattening: apta for Apta, gawa for Gawa) and even conflates distinct lemmas
# (key1 vasa merges vAsA/vAsa/vaSA/vaSa/vasA). The subcard prefix before "~~"
# encodes the faithful SLP1 lemma with "_c" for the capital letter C; decoding
# it recovers the true 261-lemma universe (verified: 11,442/11,603 rows agree
# with key1, every differing decode is the correct form).
_SUBCARD_CAP = re.compile(r'_([a-z])')


def true_lemma(subcard):
    pre = subcard.split('~~')[0]
    return _SUBCARD_CAP.sub(lambda m: m.group(1).upper(), pre)


# ------------------------------------------------------------------- parsers

_K1 = re.compile(r'<k1>(.*?)<')
_L_ID = re.compile(r'<L>(.*?)<')
_AP_SENSE = re.compile(r'\{@(?:--)?(\d+)@\}')


def iter_records(path):
    """Yield (L_id, k1, body) for every <L>..<LEND> record of a Cologne txt."""
    l_id = k1 = None
    body = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('<L>'):
                l_id = _L_ID.search(line).group(1)
                m = _K1.search(line)
                k1 = m.group(1) if m else ''
                body = []
            elif line.startswith('<LEND>'):
                if l_id is not None:
                    yield l_id, k1, ''.join(body)
                l_id = None
            elif l_id is not None:
                body.append(line)


def mw_units(path, universe):
    """MW sense unit == one <L> record (incl. .1/.2 subrecords)."""
    units = defaultdict(list)
    for l_id, k1, body in iter_records(path):
        if k1 in universe:
            units[k1].append((l_id, 'L', body))
    return units


def ap_units(path, universe):
    """AP90 sense unit == one {@N@} segment; text before the first is 'pre'."""
    units = defaultdict(list)
    for l_id, k1, body in iter_records(path):
        if k1 not in universe:
            continue
        marks = list(_AP_SENSE.finditer(body))
        if not marks:
            units[k1].append((l_id, 'entry', body))
            continue
        if marks[0].start() > 0:
            units[k1].append((l_id, 'pre', body[:marks[0].start()]))
        for i, m in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
            units[k1].append(('%s.%s' % (l_id, m.group(1)), 'num', body[m.end():end]))
    return units


# ------------------------------------------------------------------ selftest

def selftest():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    # tokenizer: accents/hyphens stripped by [a-zA-Z]+, stopwords + headword out
    t = sanskrit_tokens(['a/-karRa, AptabanDuBiH; iti ca', 'Ap'], 'Ap')
    check('tok-informative', t == {'karRa', 'AptabanDuBiH'})

    # citations: diacritic-strip + roman conversion + Mn->M alias
    c1 = citation_anchors('<ls>M. 2,109.</ls>')
    c2 = citation_anchors('<ls>Mn. ii, 109</ls>')
    check('cit-cross-dict', c1 == c2 == {('M', (2, 109))})
    check('cit-pan', citation_anchors('<ls>Pāṇ. vi, 2, 161</ls>')
          == {('PAN', (6, 2, 161))})

    # verdict tri-state and its conservative bias
    fam = [fingerprint('{#AptabanDuBiH#} <ls>M. 2,109.</ls>', 'Ap', _S_BRACE)]
    rich_hit = fingerprint('<s>AptabanDuBiH</s> <ls>Mn. ii, 109</ls>', 'Ap', _S_MW)
    check('v-matched', verdict(rich_hit, fam)[0] == 'matched')
    rich_miss = fingerprint('<s>somaH</s> <s>agniH</s> <ls>RV. x, 1</ls>', 'Ap', _S_MW)
    check('v-absent', verdict(rich_miss, fam)[0] == 'absent_candidate')
    thin_fam = [fingerprint('nur eine Glosse, kein Anker', 'Ap', _S_BRACE)]
    check('v-family-thin', verdict(rich_miss, thin_fam)[0] == 'family_thin')
    thin = fingerprint('a gloss with no anchors at all', 'Ap', _S_MW)
    check('v-abstain', verdict(thin, fam)[0] == 'unalignable')
    one_anchor_miss = fingerprint('<s>somaH</s> only', 'Ap', _S_MW)
    check('v-abstain-1anchor', verdict(one_anchor_miss, fam)[0] == 'unalignable')

    # AP segmentation
    marks = list(_AP_SENSE.finditer('PRE {@1@} A {@--2@} B'))
    check('ap-marks', [m.group(1) for m in marks] == ['1', '2'])

    # degraded-key1 repair via the subcard prefix
    check('lemma-cap', true_lemma('_ap~~h0_00_pwg01') == 'Ap')
    check('lemma-multi', true_lemma('_sud_davidy_a~~h0_zz_sch') == 'SudDavidyA')

    if fails:
        print('SELFTEST FAIL:', ', '.join(fails))
        return 1
    print('selftest: 11/11 ok')
    return 0


# ---------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--store', default=STORE)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    store_rows = [json.loads(l) for l in open(args.store, encoding='utf-8') if l.strip()]
    universe = sorted({true_lemma(r['subcard']) for r in store_rows})

    family = defaultdict(list)      # true lemma -> [(layer, subcard, sense_tag, fp)]
    fam_thin = 0
    for r in store_rows:
        lemma = true_lemma(r['subcard'])
        fp = fingerprint(r.get('de') or '', lemma, _S_BRACE)
        if len(fp['tokens']) + len(fp['cits']) == 0:
            fam_thin += 1
        family[lemma].append((r['layer'], r['subcard'], str(r.get('sense_tag')), fp))

    sources = {
        'mw': mw_units(MW_TXT, set(universe)),
        'ap90': ap_units(AP_TXT, set(universe)),
    }

    rows = []
    summary = {d: defaultdict(int) for d in sources}
    entry_absent = {d: [] for d in sources}
    for dict_code, units in sources.items():
        sanskrit_re = _S_MW if dict_code == 'mw' else _S_BRACE
        for k1 in universe:
            if not units.get(k1):
                entry_absent[dict_code].append(k1)
                continue
            fam = family[k1]
            fam_fps = [f[3] for f in fam]
            for unit_id, segment, text in units[k1]:
                fp = fingerprint(text, k1, sanskrit_re)
                v, bi, score, st, sc = verdict(fp, fam_fps)
                best = None
                if bi is not None:
                    layer, subcard, tag, _ = fam[bi]
                    best = {'layer': layer, 'subcard': subcard, 'sense_tag': tag}
                rows.append({
                    'dict': dict_code, 'key1': k1, 'unit': unit_id,
                    'segment': segment, 'verdict': v, 'score': score,
                    'n_tokens': len(fp['tokens']), 'n_cits': len(fp['cits']),
                    'shared_tokens': sorted(st)[:8],
                    'shared_cits': sorted('%s %s' % (w, ','.join(map(str, n)))
                                          for w, n in sc)[:4],
                    'best': best,
                    'text_head': re.sub(r'\s+', ' ', text).strip()[:140],
                })
                summary[dict_code][v] += 1
                if segment == 'pre':
                    summary[dict_code]['pre_' + v] += 1

    os.makedirs(os.path.dirname(OUT_ROWS), exist_ok=True)
    with open(OUT_ROWS, 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    summ = {
        'universe_headwords': len(universe),
        'family_senses': len(store_rows),
        'family_thin_fingerprints': fam_thin,
        'thresholds': {'match_min': MATCH_MIN, 'anchor_min': ANCHOR_MIN},
        'per_dict': {d: dict(v) for d, v in summary.items()},
        'entry_absent': {d: {'count': len(v), 'key1': v} for d, v in entry_absent.items()},
    }
    with open(OUT_SUMMARY, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(summ, f, ensure_ascii=False, indent=2)

    for d in sources:
        s = summary[d]
        total = sum(v for k, v in s.items() if not k.startswith('pre_'))
        print('%s: %d units | matched %d | unalignable %d | family_thin %d '
              '| absent_candidate %d | entry-absent headwords %d' % (
                  d, total, s['matched'], s['unalignable'], s['family_thin'],
                  s['absent_candidate'], len(entry_absent[d])))
    print('rows ->', OUT_ROWS)
    print('summary ->', OUT_SUMMARY)
    return 0


if __name__ == '__main__':
    sys.exit(main())
