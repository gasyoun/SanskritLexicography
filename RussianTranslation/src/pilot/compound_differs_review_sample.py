#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H1628 — stratified sample + review sheet for the ~4.2k PWG-vs-index compound
`differs` queue flagged by enrich_portrait_derivation.py (H1624 G6).

Never auto-adjudicates: this only samples ~200 for a human vote. The
remaining ~4k stay `needs_human` in the sidecar until a future sampling round.

  python src/pilot/compound_differs_review_sample.py --report   dry-run: strata + counts, no files written
  python src/pilot/compound_differs_review_sample.py --write    writes the sample frame TSV + the review sheet HTML
  python src/pilot/compound_differs_review_sample.py --selftest verify classifier + bucketing on synthetic rows
"""
import csv
import io
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))          # src/pilot
SRC = os.path.dirname(HERE)                                 # src
REPO = os.path.dirname(SRC)                                  # RussianTranslation
DERIV_TSV = os.path.join(SRC, 'pwg_derivation_layer.tsv')
INDEX_TSV = os.path.join(SRC, 'headword_index.tsv')
FREQ_TSV = os.path.join(SRC, 'pwg_freq_order.tsv')
REVIEW_DIR = os.path.join(REPO, 'review')
SAMPLE_FRAME_TSV = os.path.join(REVIEW_DIR, 'sanskritlexicography-pwg-compound-differs_stratified200_frame.tsv')
SHEET_HTML = os.path.join(REVIEW_DIR, 'sanskritlexicography-pwg-compound-differs_stratified200_review.html')
SHEET_ID = 'sanskritlexicography-pwg-compound-differs_stratified200'
SEED = 1628          # H1628 — fixed for reproducibility of the sample frame
TARGET_TOTAL = 200
RARE_CLASS_QUOTA = 20   # guaranteed oversample of the rare member_count_diff class
# Pinned, not `today`: the lock binds a content hash over the rendered HTML, so the
# sheet has to be byte-reproducible by whoever regenerates it (the HTML is gitignored;
# only the frame and the lock are committed).
GENERATED = '26-07-2026'

sys.path.insert(0, SRC)
from review_sheet_standard import pwg_entry_href, slp1_iast, standard_config  # noqa: E402
from review_binding import stamp, write_lock  # noqa: E402


def _members(s):
    return [m.strip() for m in (s or '').split('+') if m.strip()]


def load_index_members(path=INDEX_TSV):
    m = {}
    with io.open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            m[(r['k1'], r['hom'])] = r.get('compound_members', '')
    return m


def load_freq(path=FREQ_TSV):
    m = {}
    with io.open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            try:
                m[r['k1_slp1']] = int(r['count_all'])
            except (KeyError, ValueError):
                continue
    return m


def load_differs(path=DERIV_TSV):
    rows = []
    with io.open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            if (r.get('compound_status') or '').strip() == 'differs':
                rows.append(r)
    return rows


def vs_index_class(pwg_members, idx_members):
    """Sub-classify a `differs` row by HOW PWG's split disagrees with the index
    (compound_status itself is constant 'differs' for this whole queue, so it
    cannot stratify on its own — this is the finer-grained class H1628 asked for)."""
    if len(pwg_members) != len(idx_members):
        return 'member_count_diff'
    return 'same_count_diff_split'


def length_bucket(k1):
    n = len(k1)
    if n <= 8:
        return 'short(<=8)'
    if n <= 10:
        return 'medium(9-10)'
    return 'long(>=11)'


def freq_bucket(k1, freq):
    n = freq.get(k1)
    if n is None:
        return 'no_dcs_freq'
    if n <= 2:
        return 'low(1-2)'
    if n <= 9:
        return 'mid(3-9)'
    return 'high(>=10)'


def dedupe_by_card_id(rows):
    """Collapse rows that would become the SAME review card.

    A card's id is `(k1, hom)` (rendered `k1~~h<hom>`), but `pwg_derivation_layer.tsv`
    can carry two rows for one such key. H1681 found the consequence in the shipped
    200-card frame: 200 rows but **199 distinct ids** (`duHsTita` twice), i.e. two
    cards sharing one id — `decisions.json` could carry only one verdict for them and
    the lock's id list would be one short of the card count. First row wins; the drops
    are counted and reported, never silent.
    """
    seen, out, dropped = set(), [], 0
    for r in rows:
        key = (r['k1'], r['hom'])
        if key in seen:
            dropped += 1
            continue
        seen.add(key)
        out.append(r)
    return out, dropped


def build_frame():
    """Return the full `differs` frame with strata columns attached (no sampling),
    one row per review-card id."""
    idx = load_index_members()
    freq = load_freq()
    rows, n_dropped = dedupe_by_card_id(load_differs())
    if n_dropped:
        print('deduped %d row(s) sharing a (k1, hom) card id' % n_dropped,
              file=sys.stderr)
    frame = []
    for r in rows:
        k1, hom = r['k1'], r['hom']
        pwg_m = _members(r['compound_members_pwg'])
        idx_m = _members(idx.get((k1, hom), ''))
        frame.append({
            'k1': k1, 'hom': hom,
            'pwg_members': ' + '.join(pwg_m),
            'index_members': ' + '.join(idx_m),
            'vs_index_class': vs_index_class(pwg_m, idx_m),
            'length_bucket': length_bucket(k1),
            'freq_bucket': freq_bucket(k1, freq),
            'freq_count': freq.get(k1, ''),
            'panini_sutras': r.get('panini_sutras') or '',
            'deriv_base': r.get('deriv_base') or '', 'deriv_suffix': r.get('deriv_suffix') or '',
            'ganas': r.get('ganas') or '',
        })
    return frame


def stratified_sample(frame, seed=SEED, total=TARGET_TOTAL, rare_quota=RARE_CLASS_QUOTA):
    """Two-stage stratified sample, deterministic under `seed`:
    1. `member_count_diff` (rare, ~76 rows / 1.8%) gets a guaranteed flat quota —
       proportional allocation would round it to ~1-2 items and bury a distinct
       failure mode the review sheet exists to surface.
    2. The remaining budget is allocated proportionally across
       (length_bucket x freq_bucket) cells within `same_count_diff_split`,
       largest-remainder rounding so the total lands exactly on target.
    """
    rng = random.Random(seed)
    rare = [r for r in frame if r['vs_index_class'] == 'member_count_diff']
    common = [r for r in frame if r['vs_index_class'] == 'same_count_diff_split']

    rare_n = min(rare_quota, len(rare))
    rare_sample = rng.sample(rare, rare_n)

    remaining = total - rare_n
    cells = {}
    for r in common:
        cells.setdefault((r['length_bucket'], r['freq_bucket']), []).append(r)

    raw_quota = {k: remaining * len(v) / len(common) for k, v in cells.items()}
    quota = {k: int(q) for k, q in raw_quota.items()}
    shortfall = remaining - sum(quota.values())
    # largest-remainder method for the rounding shortfall
    remainders = sorted(raw_quota.items(), key=lambda kv: kv[1] - int(kv[1]), reverse=True)
    for k, _ in remainders[:shortfall]:
        quota[k] += 1

    common_sample = []
    for k, members_ in cells.items():
        n = min(quota.get(k, 0), len(members_))
        common_sample.extend(rng.sample(members_, n))

    sample = rare_sample + common_sample
    rng.shuffle(sample)
    return sample


def write_frame_tsv(sample, path=SAMPLE_FRAME_TSV):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cols = ['k1', 'hom', 'pwg_members', 'index_members', 'vs_index_class',
            'length_bucket', 'freq_bucket', 'freq_count', 'panini_sutras',
            'deriv_base', 'deriv_suffix', 'ganas']
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter='\t')
        w.writeheader()
        for r in sample:
            w.writerow({c: r.get(c, '') for c in cols})


def _esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_items(sample):
    items = []
    for r in sample:
        k1, hom = r['k1'], r['hom']
        iid = '%s~~h%s' % (k1, hom) if hom else k1
        display = slp1_iast(k1)
        href = pwg_entry_href(k1)
        title = display + (' (h%s)' % hom if hom else '')
        badges = [r['vs_index_class'], r['length_bucket'], r['freq_bucket']]
        if r.get('freq_count'):
            badges.append('DCS n=%s' % r['freq_count'])
        question = (
            '<p><b>PWG-членение:</b> <code>%s</code></p>'
            '<p><b>Членение в указателе (index):</b> <code>%s</code></p>'
            '<p style="opacity:.75">Класс расхождения: <code>%s</code></p>'
        ) % (_esc(r['pwg_members']) or '&mdash;', _esc(r['index_members']) or '&mdash;',
             _esc(r['vs_index_class']))
        panels = []
        extra = []
        if r.get('deriv_suffix'):
            extra.append('<b>Суффикс:</b> %s (%s), база: %s' % (
                _esc(r['deriv_suffix']), _esc(r.get('deriv_base', '')), _esc(r.get('deriv_base', ''))))
        if r.get('panini_sutras'):
            extra.append('<b>Пāṇini:</b> %s' % _esc(r['panini_sutras']))
        if r.get('ganas'):
            extra.append('<b>Gaṇa:</b> %s' % _esc(r['ganas']))
        if extra:
            panels.append(('Дополнительно (deriv/pāṇini/gaṇa)', '<br>'.join(extra)))
        item = {
            'id': iid, 'filt': r['vs_index_class'], 'title': title, 'badges': badges,
            'question': question, 'panels': panels,
            'note_placeholder': 'Если верно ни PWG, ни индекс — укажите правильное членение здесь',
        }
        if href:
            item['title_href'] = href
        items.append(item)
    return items


def render_sheet(sample, generated):
    from csl_pyutil import render_review_sheet
    items = build_items(sample)
    config = {
        'sheet_id': SHEET_ID,
        'title': 'PWG vs указатель: расхождения членения сложных слов (стратифицированная выборка)',
        'subtitle': (
            '%d карточек из очереди `differs` (~4226 всего, H1624 G6 / H1282). '
            'Выборка стратифицирована по длине ключа, частоте DCS и классу расхождения — '
            'см. RESULTS_LOG.md для полной методологии.' % len(sample)),
        'footer': (
            'Approve = PWG-членение верно (указатель будет обновлён под PWG). '
            'Reject = членение указателя верно, PWG-слой ошибается (indeks остаётся, PWG помечается needs_correction). '
            'Defer = нужен дополнительный контекст — решение откладывается. '
            'Голоса НЕ закрывают всю очередь ~4.2k — только эти %d карточек; остальные остаются needs_human.'
            % len(sample)),
        'approve_label': 'PWG верно',
        'reject_label': 'Индекс верно',
        'filters': [('member_count_diff', 'Разное число членов'),
                    ('same_count_diff_split', 'Одно число, другое членение')],
        'generated': generated,
        'save_as': r'RussianTranslation\review\%s_decisions.json' % SHEET_ID,
    }
    config.update(standard_config(save_as=config['save_as']))
    return render_review_sheet(items, config)


def report(frame):
    from collections import Counter
    print('frame rows (all differs):', len(frame))
    print('vs_index_class:', dict(Counter(r['vs_index_class'] for r in frame)))
    print('length_bucket:', dict(Counter(r['length_bucket'] for r in frame)))
    print('freq_bucket:', dict(Counter(r['freq_bucket'] for r in frame)))


def selftest():
    assert vs_index_class(['a', 'b'], ['a', 'b']) == 'same_count_diff_split'
    assert vs_index_class(['a', 'b', 'c'], ['a', 'b']) == 'member_count_diff'
    assert length_bucket('a' * 5) == 'short(<=8)'
    assert length_bucket('a' * 9) == 'medium(9-10)'
    assert length_bucket('a' * 12) == 'long(>=11)'
    assert freq_bucket('x', {}) == 'no_dcs_freq'
    assert freq_bucket('x', {'x': 1}) == 'low(1-2)'
    assert freq_bucket('x', {'x': 5}) == 'mid(3-9)'
    assert freq_bucket('x', {'x': 50}) == 'high(>=10)'
    fake = []
    for i in range(500):
        fake.append({'k1': 'k%d' % i, 'hom': '', 'vs_index_class': 'same_count_diff_split',
                     'length_bucket': ['short(<=8)', 'medium(9-10)', 'long(>=11)'][i % 3],
                     'freq_bucket': ['no_dcs_freq', 'low(1-2)', 'mid(3-9)', 'high(>=10)'][i % 4],
                     'freq_count': '', 'panini_sutras': '', 'deriv_base': '', 'deriv_suffix': '', 'ganas': '',
                     'pwg_members': 'a + b', 'index_members': 'a + c'})
    for i in range(20):
        fake.append({'k1': 'rare%d' % i, 'hom': '', 'vs_index_class': 'member_count_diff',
                     'length_bucket': 'short(<=8)', 'freq_bucket': 'no_dcs_freq', 'freq_count': '',
                     'panini_sutras': '', 'deriv_base': '', 'deriv_suffix': '', 'ganas': '',
                     'pwg_members': 'a + b + c', 'index_members': 'a + b'})
    s1 = stratified_sample(fake, seed=42, total=60, rare_quota=10)
    s2 = stratified_sample(fake, seed=42, total=60, rare_quota=10)
    assert len(s1) == 60, len(s1)
    assert [r['k1'] for r in s1] == [r['k1'] for r in s2], 'sample must be deterministic under a fixed seed'
    assert sum(1 for r in s1 if r['vs_index_class'] == 'member_count_diff') == 10
    # the H1681 defect: two derivation-layer rows collapsing onto one card id
    dup = [{'k1': 'duHsTita', 'hom': ''}, {'k1': 'duHsTita', 'hom': ''},
           {'k1': 'duHsTita', 'hom': '2'}, {'k1': 'anya', 'hom': ''}]
    kept, dropped = dedupe_by_card_id(dup)
    assert dropped == 1 and len(kept) == 3, (kept, dropped)
    ids = [it['id'] for it in build_items(
        [dict(r, pwg_members='a + b', index_members='a + c',
              vs_index_class='same_count_diff_split', length_bucket='short(<=8)',
              freq_bucket='no_dcs_freq', freq_count='', panini_sutras='',
              deriv_base='', deriv_suffix='', ganas='') for r in kept])]
    assert len(set(ids)) == len(ids), ids
    print('selftest OK — classifier, buckets, deterministic stratified sampling '
          '(n=%d), card-id dedupe' % len(s1))


def main():
    args = sys.argv[1:]
    if '--selftest' in args:
        selftest()
        return
    frame = build_frame()
    if '--report' in args or not args:
        report(frame)
        return
    if '--write' in args:
        sample = stratified_sample(frame)
        ids = [it['id'] for it in build_items(sample)]
        assert len(set(ids)) == len(ids), 'duplicate card id in the sample'
        write_frame_tsv(sample)
        html = render_sheet(sample, generated=GENERATED)
        # H1404 binding: stamp the content hash into the HTML and commit the lock,
        # or `validate_decisions.py` refuses the export — AFTER the human has spent
        # the votes. H1681 found this sheet shipped unbound; MG ruled re-cut.
        html, chash = stamp(html)
        os.makedirs(REVIEW_DIR, exist_ok=True)
        with io.open(SHEET_HTML, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
        lock_path = write_lock(SHEET_ID, chash, ids, GENERATED, gate='G6-compound',
                               source_html=SHEET_HTML)
        print('wrote %d-row sample frame -> %s' % (len(sample), SAMPLE_FRAME_TSV))
        print('wrote review sheet -> %s' % SHEET_HTML)
        print('  %s' % chash)
        print('  lock -> %s' % lock_path)
        return
    sys.exit('usage: compound_differs_review_sample.py --report | --write | --selftest')


if __name__ == '__main__':
    main()
