#!/usr/bin/env python
"""probe_gold_strata.py — measure the candidate frame for the H2401 BLI gold set.

H2401 (ACL B1) needs a *stratified* human-annotated Sa->Ru gold set. H1521 already
shipped an automatic 400-lemma set (`gold_sa_ru_koch_400.tsv`) selected by DCS
frequency band alone, which gave P@1 = 0.402 / MRR = 0.539 / coverage = 0.995.
Its coverage of 0.995 is the tell that a top-band-only frame cannot answer the
question B1 actually asks -- how the lexicon behaves *across* frequency, POS and
polysemy -- because a top-band frame is nearly always present in the lexicon.

This probe measures, on the real assets and with NO writes to any gold file:

  1. the joint (frequency band x dominant POS) population of the candidate frame,
     i.e. Kochergina lemmas that also carry an independent DCS frequency signal;
  2. how many candidates survive the same gloss-extractability filter H1521 used
     (>= 1 Russian content token), per cell -- a cell with too few extractable
     glosses cannot be sampled at the target size and must be merged or reported;
  3. the polysemy distribution (Kochergina sense count) of the candidate frame,
     which is the third stratum axis B1 needs and H1521 did not use at all;
  4. per-cell presence in `corpus_lexicon.jsonl` (optional, streaming) so the
     protocol can state expected coverage per stratum BEFORE any annotation is
     paid for -- a stratum with near-zero lexicon presence yields no P@1 signal.

Read-only by construction: it opens the three inputs and prints JSON. Nothing in
this file writes to `gold_sa_ru_*.tsv` or to `corpus_lexicon.jsonl`.

Usage:
  python probe_gold_strata.py --koch ../koch.jsonl --dcs ../dcs_freq_dims.json
  python probe_gold_strata.py --koch ... --dcs ... --lexicon ../corpus_lexicon.jsonl
  python probe_gold_strata.py selftest
"""
import argparse
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

CONTENT_RE = re.compile(r'[а-яёА-ЯЁ]{4,}')

# Same notation-filler guard as build_gold_koch.py: Cyrillic, >=4 letters, and
# present in nearly every Kochergina entry, so it is not evidence of a gloss.
STOP_TOKENS = {
    'кого-л', 'чего-л', 'что-л', 'какой-л', 'каком-л', 'которого-л',
    'напротив', 'например', 'иногда', 'обычно', 'также', 'только', 'весьма',
    'напр', 'знач', 'нареч', 'прил', 'форма', 'формы', 'выраж',
}


def content_tokens(text):
    """Russian content-word tokens, notation filler removed."""
    return {t.lower() for t in CONTENT_RE.findall(text or '')} - STOP_TOKENS


def gloss_text(rec):
    """Best-effort gloss text from a Kochergina record of unknown field shape."""
    for key in ('ru', 'gloss', 'meaning', 'translation', 'text', 'body', 'value'):
        v = rec.get(key)
        if isinstance(v, str) and v.strip():
            return v
        if isinstance(v, list) and v:
            return ' ; '.join(str(x) for x in v)
    # Fall back to every string value, so a shape change degrades rather than lies.
    return ' ; '.join(v for v in rec.values() if isinstance(v, str))


def lemma_key(rec):
    for key in ('slp1', 'key', 'key1', 'lemma', 'headword', 'hw'):
        v = rec.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def sense_count(rec, gloss):
    """Polysemy proxy: explicit sense list if present, else numbered-sense markers.

    Kochergina glosses number senses `1)`, `2)` ...; where no numbering exists a
    single sense is assumed. This is a proxy and is labelled as such in the output.
    """
    for key in ('senses', 'meanings'):
        v = rec.get(key)
        if isinstance(v, list) and v:
            return len(v)
    markers = re.findall(r'(?<!\d)(\d{1,2})\)', gloss or '')
    if markers:
        try:
            return max(int(m) for m in markers)
        except ValueError:
            pass
    return 1


def polysemy_bucket(n):
    if n <= 1:
        return '1'
    if n <= 3:
        return '2-3'
    if n <= 6:
        return '4-6'
    return '7+'


def load_dcs(path):
    """Returns {slp1_lemma: {'band': int, 'pos': str, 'total': int}}.

    Handles BOTH DCS assets, because they are keyed in different schemes and
    picking the wrong one silently destroys ~75% of the join (measured by
    probe_key_scheme.py, H2401):

      * `dcs_lemma_summary.json` — **SLP1**-keyed (`{'lemmas': {slp1: {...}}}`),
        the asset H1521's build_gold_koch.py used. Carries `freqBand` but no POS.
      * `dcs_freq_dims.json` — **IAST**-keyed (`{'by_lemma': {iast: {...}}}`),
        carries the per-POS/genre/era dimensions. Its keys are transcoded to SLP1
        via the canonical `sanskrit-util.to_slp1` (SHARED_CODE §1 — never
        hand-roll the SLP1 table) so it can join Kochergina's SLP1 headwords.
    """
    with open(path, encoding='utf-8-sig') as f:
        data = json.load(f)

    if 'lemmas' in data and isinstance(data['lemmas'], dict):
        # SLP1-keyed frequency summary: bands only, POS unavailable here.
        return {slp1: {'band': int(rec.get('freqBand') or 0),
                       'pos': 'UNK',
                       'total': int(rec.get('count') or rec.get('freq') or 0)}
                for slp1, rec in data['lemmas'].items()}

    by_lemma = data.get('by_lemma', data)
    to_slp1 = _canonical_to_slp1()
    out = {}
    for lemma, dims in by_lemma.items():
        pos = dims.get('pos') or {}
        band_map = pos.get('band') or {}
        dominant = pos.get('dominant')
        band = band_map.get(dominant) if dominant else None
        if band is None and band_map:
            band = max(band_map.values())
        key = to_slp1(lemma)
        out[key] = {
            'band': int(band) if band is not None else 0,
            'pos': dominant or 'UNK',
            'total': int(pos.get('total') or 0),
        }
    return out


def _canonical_to_slp1():
    """The org's canonical IAST->SLP1 transcoder (SHARED_CODE §1), or a hard fail.

    Deliberately no hand-rolled fallback map: SHARED_CODE counted 62 copies of a
    re-typed SLP1 table as the org's single worst duplication, and a subtly wrong
    private map here would corrupt the frame silently rather than loudly.
    """
    for candidate in (
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'sanskrit-util', 'py'),
        r'C:\Users\user\Documents\GitHub\sanskrit-util\py',
    ):
        p = os.path.abspath(candidate)
        if os.path.isdir(p) and p not in sys.path:
            sys.path.insert(0, p)
    try:
        from sanskrit_util import to_slp1
    except ImportError as exc:  # pragma: no cover - environment problem, not logic
        raise SystemExit(
            'sanskrit-util is required to transcode IAST DCS keys to SLP1 '
            '(SHARED_CODE.md §1). Clone/install sanskrit-util rather than '
            'hand-rolling an SLP1 table here. Original error: %s' % exc)
    return to_slp1


def load_koch(path):
    """Yields (lemma, gloss, sense_count) for standalone Kochergina entries."""
    with open(path, encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            lemma = lemma_key(rec)
            if not lemma or lemma.startswith('-'):
                continue  # bound compound member: not a standalone gold candidate
            gloss = gloss_text(rec)
            yield lemma, gloss, sense_count(rec, gloss)


def lexicon_presence(path, wanted):
    """Streaming set-intersection: which of `wanted` lemmas appear in the lexicon.

    Streams the 290 MB file once and holds only the hit set (bounded by `wanted`),
    never the file. Mirrors bli_eval.py's streaming contract.
    """
    present = set()
    with open(path, encoding='utf-8-sig') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            for key in ('slp1', 'sa', 'source', 'key', 'lemma'):
                v = rec.get(key) if isinstance(rec, dict) else None
                if isinstance(v, str) and v in wanted:
                    present.add(v)
                    break
    return present


def merge_dcs(band_source, pos_source=None):
    """Band from the SLP1-keyed summary; POS from the IAST-keyed dims where present.

    Kept separate because the two assets disagree on both key scheme and payload:
    only `dcs_lemma_summary.json` has the `freqBand` H1521 selected on, and only
    `dcs_freq_dims.json` has the dominant POS this protocol strata on.
    """
    merged = {k: dict(v) for k, v in band_source.items()}
    if pos_source:
        for lemma, dims in pos_source.items():
            if lemma in merged:
                if dims.get('pos') and dims['pos'] != 'UNK':
                    merged[lemma]['pos'] = dims['pos']
            else:
                merged[lemma] = dict(dims)
    return merged


def build_report(koch_path, dcs_path, lexicon_path=None, dims_path=None):
    dcs = load_dcs(dcs_path)
    if dims_path:
        dcs = merge_dcs(dcs, load_dcs(dims_path))
    cells = collections.Counter()          # (band, pos) -> candidates
    cells_glossed = collections.Counter()  # (band, pos) -> with >=1 content token
    poly = collections.Counter()           # bucket -> count
    poly_by_band = collections.Counter()   # (band, bucket) -> count
    candidates = {}                        # lemma -> (band, pos, bucket)
    koch_total = 0
    joined = 0

    for lemma, gloss, nsense in load_koch(koch_path):
        koch_total += 1
        dim = dcs.get(lemma)
        if not dim:
            continue  # no independent frequency signal -> cannot be stratified
        joined += 1
        band, pos = dim['band'], dim['pos']
        toks = content_tokens(gloss)
        cells[(band, pos)] += 1
        bucket = polysemy_bucket(nsense)
        if toks:
            cells_glossed[(band, pos)] += 1
            poly[bucket] += 1
            poly_by_band[(band, bucket)] += 1
            candidates[lemma] = (band, pos, bucket)

    report = {
        'koch_standalone_entries': koch_total,
        'dcs_lemmas': len(dcs),
        'joined_candidates': joined,
        'glossable_candidates': len(candidates),
        'cells': [
            {'band': b, 'pos': p, 'candidates': cells[(b, p)],
             'glossable': cells_glossed[(b, p)]}
            for (b, p) in sorted(cells, key=lambda k: (-k[0], -cells[k]))
        ],
        'polysemy_buckets': dict(sorted(poly.items())),
        'polysemy_by_band': {f'band{b}|{k}': v
                             for (b, k), v in sorted(poly_by_band.items())},
        'polysemy_note': 'sense count is a proxy: explicit sense list if present, '
                         'else max numbered-sense marker in the gloss, else 1',
    }

    if lexicon_path:
        present = lexicon_presence(lexicon_path, set(candidates))
        by_cell_total = collections.Counter()
        by_cell_present = collections.Counter()
        for lemma, (b, p, _bucket) in candidates.items():
            by_cell_total[(b, p)] += 1
            if lemma in present:
                by_cell_present[(b, p)] += 1
        report['lexicon_presence'] = {
            'probed': len(candidates),
            'present': len(present),
            'by_cell': [
                {'band': b, 'pos': p, 'probed': by_cell_total[(b, p)],
                 'present': by_cell_present[(b, p)],
                 'rate': round(by_cell_present[(b, p)] / by_cell_total[(b, p)], 4)
                 if by_cell_total[(b, p)] else None}
                for (b, p) in sorted(by_cell_total, key=lambda k: (-k[0], k[1]))
            ],
        }
    return report


def selftest():
    """Fixture selftest: deterministic, no big assets, CI-safe."""
    import tempfile

    koch_rows = [
        {'slp1': 'gaja', 'ru': '1) слон 2) вожак стада'},
        {'slp1': 'nara', 'ru': 'человек, мужчина'},
        {'slp1': 'aSva', 'ru': '1) конь 2) лошадь 3) кобыла 4) скакун'},
        {'slp1': '-kAra', 'ru': 'делающий'},          # bound: must be skipped
        {'slp1': 'xyz', 'ru': 'напр знач'},           # filler only: not glossable
        {'slp1': 'nodcs', 'ru': 'нечто'},             # no DCS signal: not joined
    ]
    # SLP1-keyed summary (the H1521 asset shape): carries freqBand, no POS.
    dcs_summary = {'lemmas': {
        'gaja': {'freqBand': 5, 'count': 90},
        'nara': {'freqBand': 4, 'count': 40},
        'aSva': {'freqBand': 5, 'count': 80},
        '-kAra': {'freqBand': 3, 'count': 5},
        'xyz': {'freqBand': 2, 'count': 3},
    }}
    # IAST-keyed dims: POS only, and its keys must be transcoded to join at all.
    # 'aśva' -> 'aSva' exercises the transcode path; a raw-key join would miss it.
    dcs_dims = {'meta': {}, 'by_lemma': {
        'gaja': {'pos': {'dominant': 'NOUN', 'band': {'NOUN': 5}, 'total': 90}},
        'aśva': {'pos': {'dominant': 'NOUN', 'band': {'NOUN': 5}, 'total': 80}},
    }}
    lex_rows = [{'slp1': 'gaja', 'ru': 'слон'}, {'slp1': 'aSva', 'ru': 'конь'}]

    tmp = tempfile.mkdtemp()
    kp = os.path.join(tmp, 'koch.jsonl')
    dp = os.path.join(tmp, 'dcs_summary.json')
    xp = os.path.join(tmp, 'dcs_dims.json')
    lp = os.path.join(tmp, 'lex.jsonl')
    with open(kp, 'w', encoding='utf-8') as f:
        for r in koch_rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(dp, 'w', encoding='utf-8') as f:
        json.dump(dcs_summary, f, ensure_ascii=False)
    with open(xp, 'w', encoding='utf-8') as f:
        json.dump(dcs_dims, f, ensure_ascii=False)
    with open(lp, 'w', encoding='utf-8') as f:
        for r in lex_rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    rep = build_report(kp, dp, lp, xp)
    failures = []

    def check(label, got, want):
        if got != want:
            failures.append(f'{label}: got {got!r}, want {want!r}')

    check('koch_standalone_entries', rep['koch_standalone_entries'], 5)  # -kAra skipped
    check('joined_candidates', rep['joined_candidates'], 4)              # nodcs dropped
    check('glossable_candidates', rep['glossable_candidates'], 3)        # xyz filler dropped
    check('polysemy buckets', rep['polysemy_buckets'], {'1': 1, '2-3': 1, '4-6': 1})
    check('lexicon present', rep['lexicon_presence']['present'], 2)

    # The IAST->SLP1 transcode must actually land: 'aśva' in the dims file has to
    # reach the 'aSva' candidate as NOUN, or the merge silently degrades to UNK.
    pos_by_cell = {(c['band'], c['pos']): c['glossable'] for c in rep['cells']}
    check('band5 NOUN cell (gaja + aSva via transcode)', pos_by_cell.get((5, 'NOUN')), 2)
    check('band4 stays UNK (nara absent from dims)', pos_by_cell.get((4, 'UNK')), 1)

    if failures:
        print('SELFTEST FAIL')
        for f_ in failures:
            print('  -', f_)
        return 1
    print('SELFTEST PASS (3 glossable candidates, 2 lexicon hits, IAST->SLP1 merge OK)')
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--koch', required=True)
    ap.add_argument('--dcs', required=True,
                    help='dcs_lemma_summary.json (SLP1-keyed, carries freqBand)')
    ap.add_argument('--dims', default=None,
                    help='optional dcs_freq_dims.json (IAST-keyed) for dominant POS')
    ap.add_argument('--lexicon', default=None,
                    help='optional: stream corpus_lexicon.jsonl for per-cell presence')
    args = ap.parse_args()
    rep = build_report(args.koch, args.dcs, args.lexicon, args.dims)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
