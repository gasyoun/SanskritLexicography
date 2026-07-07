#!/usr/bin/env python
r"""H215 Slice 3 (part 1) -- the L0 verse/segment layer of the Sa->Ru TM.

Slices 1-2 shipped the L1 (word/phrase) layer as TMX: one <tu> per aligned
Sanskrit content word <-> Russian rendering (`corpus_lexicon.jsonl`, DeepSeek).
This adds the missing **L0** layer -- one first-class unit per *verse*: the whole
Sanskrit segment <-> its whole Russian translation segment (the TMX `segtype`
"block"/citation unit, and the anchor every L1 word-pair hangs off).

Where L0 comes from: the same verse-aligned corpus that DeepSeek word-aligned to
*produce* L1 -- `SamudraManthanam/web/corpus_builder/jsonl/<work>.jsonl`. Each
`group` there is one verse and carries `seg=sa` (Sanskrit), `seg=ru` (the Russian
translation) and `seg=comm1..` (Russian commentary notes). We emit:

  * one L0 `translation` unit per group  (sa.text  <-> ru.text)
  * one L0 `commentary`  unit per note    (sa.text  <-> commN.text)

`group` is the join key back to the L1 units in `corpus_lexicon.jsonl` (every L1
row carries the same `group`), so tm_align.py can score each L1 word-pair against
its parent L0 verse, and build_tmx.py can emit both layers into one TMX.

  python build_l0.py build                 SamudraManthanam corpus -> corpus_l0.jsonl
  python build_l0.py build --work W        one work only (e.g. bhagavadgita-sementsov)
  python build_l0.py build --no-comm       translations only, skip commentary notes
  python build_l0.py build --sample N      first N groups (reviewable slice)
  python build_l0.py status                unit / work / token counts of an L0 file
  python build_l0.py selftest              fixture -> build -> assert

RIGHTS: L0 pairs the SAME in-copyright named modern Russian translations as L1, so
`corpus_l0.jsonl` is written under the gitignored `release/corpus_tm/` exactly like
the lexicon and the TMX. Only this generator + the README are committed. No public
release before per-translator clearance (H215 Slice 5, /publish-safety-check).

Model provenance: deterministic (pure parse/clean/group -- no LLM call, no clock in
the record, so the same corpus yields byte-identical L0).
"""
import argparse
import collections
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
# same corpus source build_corpus_lexicon.py reads (verse-aligned Sa<->Ru).
SM = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'SamudraManthanam',
                                   'web', 'corpus_builder', 'jsonl'))
DEFAULT_OUT = os.path.join(ROOT, 'release', 'corpus_tm', 'corpus_l0.jsonl')
STRATA_PATH = os.path.join(HERE, 'corpus_strata.json')

VERSION = '0.1.0'

CYR = re.compile('[Ѐ-ӿԀ-ԯⷠ-ⷿꙀ-ꚟ]')
# Sanskrit-segment noise: the corpus interleaves Cyrillic edition tags ("БхГ 1.1"),
# daoas, and verse numbers into the sa text/slp1 (see the source's `text` field).
_CYR_RUN = re.compile('[Ѐ-ӿԀ-ԯЁёА-я]+')
_DANDA = re.compile('[।॥]')
_MULTISPACE = re.compile(r'\s+')


def has_cyr(s):
    return bool(s) and bool(CYR.search(s))


def load_strata():
    if os.path.exists(STRATA_PATH):
        return json.load(open(STRATA_PATH, encoding='utf-8'))
    return {}


def clean_sa(s):
    """Strip the edition/citation noise the corpus interleaves into a Sanskrit
    segment -- Cyrillic reference tags ('БхГ 1.1'), daoas, and bare verse
    numbers -- leaving just the transliterated verse words. Works on both the
    IAST `text` and the SLP1 `slp1` field (same noise shape in each)."""
    if not s:
        return ''
    s = _CYR_RUN.sub(' ', s)          # drop 'БхГ 1.1' style edition tags
    s = _DANDA.sub(' ', s)            # drop | and ||
    s = re.sub(r'\d+', ' ', s)        # drop bare verse numbers left behind
    s = re.sub(r'[.,;:*]', ' ', s)    # drop the '.' left by a '1.1' number, stray punct
    s = _MULTISPACE.sub(' ', s)
    return s.strip()


def clean_ru(s):
    """The Russian translation segment is already clean Cyrillic prose; only
    collapse whitespace / drop stray daoas. Em-dashes and guillemets are kept
    (they are part of the translation, not noise)."""
    if not s:
        return ''
    s = _DANDA.sub(' ', s)
    s = _MULTISPACE.sub(' ', s)
    return s.strip()


def sa_tokens(slp1_clean):
    """Whitespace SLP1 tokens of a cleaned Sanskrit verse (for token counts and
    the aligner). Empty tokens dropped."""
    return [t for t in slp1_clean.split() if t]


def l0id(group, seg):
    """Stable, content-derived L0 id -- deterministic (no clock), disjoint from
    build_tmx's 'cl-' L1 tuids by the 'l0-' prefix."""
    basis = '%s\x1f%s' % (group, seg)
    return 'l0-' + hashlib.sha256(basis.encode('utf-8')).hexdigest()[:16]


def iter_groups(path):
    """Yield (group, {seg: record}) for one work's corpus jsonl, skipping deleted
    rows. Mirrors build_corpus_lexicon.pairs_of's grouping."""
    by_group = collections.OrderedDict()
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            if e.get('deleted'):
                continue
            by_group.setdefault(e.get('group'), {})[e.get('seg')] = e
    for g, d in by_group.items():
        yield g, d


def units_for_group(group, d, work, strata, with_comm=True):
    """Emit the L0 units for one verse group: the sa<->ru translation, plus a
    sa<->commN unit per Russian commentary note. Applies the never-invent guards
    (Sanskrit present, Russian carries Cyrillic) so an untranslated placeholder
    can never become an L0 pair."""
    sa = d.get('sa')
    if not (sa and sa.get('text')):
        return
    sa_iast = clean_sa(sa.get('text'))
    sa_slp1 = clean_sa(sa.get('slp1') or '')
    if not (sa_iast or sa_slp1):
        return
    st = strata.get(work, {})
    passage = sa.get('passage', '') or ''
    base = {'work': work, 'group': group,
            'genre': st.get('genre'), 'period': st.get('period'),
            'date': st.get('date_median')}

    def emit(seg, kind):
        rec = d.get(seg)
        if not rec:
            return None
        ru = clean_ru(rec.get('text'))
        if not has_cyr(ru):            # untranslated placeholder -> never emit
            return None
        toks = sa_tokens(sa_slp1)
        return {**base, 'l0id': l0id(group, seg), 'seg': seg, 'kind': kind,
                'passage': rec.get('passage', passage) or passage,
                'sa': sa_iast, 'slp1': sa_slp1, 'ru': ru,
                'n_sa_tok': len(toks),
                'n_ru_tok': len(re.findall(r'[Ѐ-ӿ]+', ru)),
                'speaker_sa': (sa.get('author') or '').strip() or None,
                'speaker_ru': (rec.get('author') or '').strip() or None}

    u = emit('ru', 'translation')
    if u:
        yield u
    if with_comm:
        for seg in sorted(s for s in d if s and s.startswith('comm')):
            cu = emit(seg, 'commentary')
            if cu:
                yield cu


def build(out_path, work=None, with_comm=True, sample=None, sm=SM):
    if not os.path.isdir(sm):
        sys.exit('corpus source not found: %s\n(SamudraManthanam must be a sibling '
                 'repo -- see build_corpus_lexicon.py SM path)' % sm)
    strata = load_strata()
    if work:
        files = [work + '.jsonl']
    else:
        files = sorted(f for f in os.listdir(sm) if f.endswith('.jsonl'))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    dist = collections.Counter()
    works = set()
    n = 0
    with open(out_path, 'w', encoding='utf-8', newline='\n') as out:
        for fn in files:
            fp = os.path.join(sm, fn)
            if not os.path.exists(fp):
                sys.stderr.write('skip (missing): %s\n' % fn)
                continue
            wname = fn[:-len('.jsonl')]
            for group, d in iter_groups(fp):
                for u in units_for_group(group, d, wname, strata, with_comm):
                    out.write(json.dumps(u, ensure_ascii=False) + '\n')
                    dist[u['kind']] += 1
                    works.add(u['work'])
                    n += 1
                    if sample and n >= sample:
                        break
                if sample and n >= sample:
                    break
            if sample and n >= sample:
                break
    print('build_l0: %d L0 units (%d translation, %d commentary) over %d works -> %s'
          % (n, dist['translation'], dist['commentary'], len(works), out_path))
    return 0 if n else 1


def status(path):
    if not os.path.exists(path):
        sys.exit('L0 file not found: %s (run `build_l0.py build` first)' % path)
    dist = collections.Counter()
    works = set()
    sa_tok = ru_tok = n = 0
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            dist[r.get('kind')] += 1
            works.add(r.get('work'))
            sa_tok += r.get('n_sa_tok', 0)
            ru_tok += r.get('n_ru_tok', 0)
            n += 1
    print('corpus_l0: %d units (%d translation, %d commentary), %d works'
          % (n, dist['translation'], dist['commentary'], len(works)))
    if n:
        print('  mean tokens/unit: sa %.1f  ru %.1f' % (sa_tok / n, ru_tok / n))
    return 0


# ---------------------------------------------------------------------- selftest
FIXTURE = [
    # a clean verse group: sa + ru translation + one commentary note
    {'group': 'bg:1.1', 'seg': 'sa', 'passage': '1.1', 'author': 'dhrtarastra uvaca',
     'text': 'dharmakṣetre kurukṣetre samavetā yuyutsavaḥ । БхГ 1.1 kimakurvata ॥1 БхГ 1.1॥',
     'slp1': 'Darmakzetre kurukzetre samavetA yuyutsavaH । БхГ 1.1 kimakurvata ॥1 БхГ 1.1॥'},
    {'group': 'bg:1.1', 'seg': 'ru', 'passage': '1.1', 'author': 'Дхритараштра сказал',
     'text': 'Что свершали на поле дхармы, на поле Куру, сойдясь для битвы?'},
    {'group': 'bg:1.1', 'seg': 'comm1', 'passage': '1.1.comm1',
     'text': 'дхармакшетра — поле дхармы, священное место.'},
    # an UNTRANSLATED group: ru placeholder with no Cyrillic -> must be dropped
    {'group': 'bg:1.2', 'seg': 'sa', 'passage': '1.2', 'text': 'dṛṣṭvā tu ॥2॥',
     'slp1': 'dfzwvA tu ॥2॥'},
    {'group': 'bg:1.2', 'seg': 'ru', 'passage': '1.2', 'text': '…'},
    # a group with no Sanskrit -> must be dropped
    {'group': 'bg:1.3', 'seg': 'ru', 'passage': '1.3', 'text': 'сирота без санскрита'},
]


def selftest():
    import tempfile
    assert clean_sa('samavetā yuyutsavaḥ । БхГ 1.1 kimakurvata ॥1 БхГ 1.1॥') \
        == 'samavetā yuyutsavaḥ kimakurvata', 'sa clean failed: %r' \
        % clean_sa('samavetā yuyutsavaḥ । БхГ 1.1 kimakurvata ॥1 БхГ 1.1॥')
    assert has_cyr('поле') and not has_cyr('dharma')
    assert l0id('g', 's') == l0id('g', 's'), 'l0id not deterministic'
    assert l0id('g', 'ru') != l0id('g', 'comm1'), 'l0id must separate segs'

    d = tempfile.mkdtemp(prefix='l0_selftest_')
    src = os.path.join(d, 'bg.jsonl')
    with open(src, 'w', encoding='utf-8') as f:
        for r in FIXTURE:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    strata = {'bg': {'genre': 'Epic', 'period': 'Classical', 'date_median': -300}}

    groups = dict(iter_groups(src))
    units = []
    for g, dd in groups.items():
        units.extend(units_for_group(g, dd, 'bg', strata))
    # 1.1 -> translation + commentary = 2; 1.2 dropped (placeholder ru); 1.3 dropped (no sa)
    assert len(units) == 2, 'expected 2 L0 units, got %d' % len(units)
    tr = [u for u in units if u['kind'] == 'translation'][0]
    assert tr['sa'] == 'dharmakṣetre kurukṣetre samavetā yuyutsavaḥ kimakurvata', tr['sa']
    assert tr['slp1'].startswith('Darmakzetre'), tr['slp1']
    assert 'БхГ' not in tr['slp1'] and '।' not in tr['slp1'], 'noise leaked into slp1'
    assert tr['ru'].startswith('Что свершали'), tr['ru']
    assert tr['n_sa_tok'] == 5, 'sa tokens: %d' % tr['n_sa_tok']
    assert tr['genre'] == 'Epic' and tr['date'] == -300, 'strata not attached'
    assert tr['speaker_ru'] == 'Дхритараштра сказал'
    cm = [u for u in units if u['kind'] == 'commentary'][0]
    assert cm['ru'].startswith('дхармакшетра'), cm['ru']
    assert cm['sa'] == tr['sa'], 'commentary shares the verse Sanskrit'
    print('build_l0 selftest OK -- clean, guards (2/3 groups kept), strata, seg split, det. ids')
    return 0


def main():
    ap = argparse.ArgumentParser(description='L0 verse-segment layer for the Sa->Ru TM (H215 Slice 3)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    b = sub.add_parser('build', help='SamudraManthanam corpus -> corpus_l0.jsonl')
    b.add_argument('--out', dest='out', default=DEFAULT_OUT)
    b.add_argument('--work', default=None, help='one work only (basename w/o .jsonl)')
    b.add_argument('--no-comm', dest='comm', action='store_false', help='skip commentary notes')
    b.add_argument('--sample', type=int, default=None, help='first N units only')
    b.add_argument('--sm', default=SM, help='override SamudraManthanam corpus dir')

    s = sub.add_parser('status', help='counts of an existing L0 file')
    s.add_argument('--in', dest='inp', default=DEFAULT_OUT)

    sub.add_parser('selftest', help='fixture -> build -> assert')

    a = ap.parse_args()
    if a.cmd == 'build':
        return build(a.out, work=a.work, with_comm=a.comm, sample=a.sample, sm=a.sm)
    if a.cmd == 'status':
        return status(a.inp)
    if a.cmd == 'selftest':
        return selftest()
    return 1


if __name__ == '__main__':
    sys.exit(main())
