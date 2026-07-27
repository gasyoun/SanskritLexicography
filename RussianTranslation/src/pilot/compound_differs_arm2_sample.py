#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H1703 — the SECOND blind arm for the PWG-vs-index compound `differs` queue,
stratified on the H1681 adjudicator's own rules.

The first arm (H1628, `…_stratified200`) was drawn along length × DCS-frequency ×
member-count, which cuts ACROSS the adjudicator's rules. Measured against the
refreshed verdicts it lands 139 of its cards in `same_split_pwg_lemma_form` and
0–16 in each of the others — so it prices one stratum of eight and leaves ~1,200
rows with no route to promotion, however the human votes.

A stratum needs **35 cards** to clear a 0.90 Wilson-95 % lower bound even if the
human agrees with every one (`wilson_lower(35, 35) = 0.901`); at 34 it cannot. So
this arm draws 35 per stratum the first arm cannot price, censuses in full any
stratum with fewer than 35 rows available, and samples **disjointly** from the
first arm's card ids so the two arms stay independent.

Blind by construction: the sheet shows the two member lists and the same neutral
badges as arm 1. The stratum, the rule, the agent's verdict and its reason are in
the frame TSV — never in the HTML — or the arm would be scoring the human against
the agent's own classification instead of pricing it.

  python src/pilot/compound_differs_arm2_sample.py --report    strata + allocation, writes nothing
  python src/pilot/compound_differs_arm2_sample.py --write     frame TSV + sheet HTML + content lock
  python src/pilot/compound_differs_arm2_sample.py --selftest  allocation + disjointness on fixtures
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
REPO = os.path.dirname(SRC)                                 # RussianTranslation
VERDICTS_TSV = os.path.join(REPO, 'research', 'pwg_compound_differs_adjudication.tsv')
FREQ_TSV = os.path.join(SRC, 'pwg_freq_order.tsv')
REVIEW_DIR = os.path.join(REPO, 'review')
LOCK_DIR = os.path.join(REVIEW_DIR, 'locks')

ARM1_SHEET_ID = 'sanskritlexicography-pwg-compound-differs_stratified200'
SHEET_ID = 'sanskritlexicography-pwg-compound-differs_rulestrat_arm2'
SAMPLE_FRAME_TSV = os.path.join(REVIEW_DIR, SHEET_ID + '_frame.tsv')
SHEET_HTML = os.path.join(REVIEW_DIR, SHEET_ID + '_review.html')

SEED = 1703             # H1703 — fixed for reproducibility of the sample frame
# 35 is not a round number: wilson_lower(35, 35) = 0.9010 and wilson_lower(34, 34)
# = 0.8983, so 35 is the smallest arm that can clear the 0.90 gate at all.
PER_STRATUM = 35
# A stratum already carrying this many arm-1 cards is priceable without a second arm.
PRICED_BY_ARM1 = 35
# Pinned, not `today`: the lock binds a content hash over the rendered HTML, so the
# sheet has to be byte-reproducible by whoever regenerates it (the HTML is gitignored;
# only the frame and the lock are committed).
GENERATED = '26-07-2026'

sys.path.insert(0, SRC)
from review_sheet_standard import pwg_entry_href, slp1_iast, standard_config  # noqa: E402
from review_binding import stamp, write_lock  # noqa: E402


def read_tsv(path):
    with io.open(path, encoding='utf-8') as fh:
        for row in csv.DictReader(fh, delimiter='\t'):
            yield row


def load_verdicts(path=VERDICTS_TSV):
    """One row per adjudicated card, deduped on the card id (first wins)."""
    seen, out = set(), []
    for r in read_tsv(path):
        if r['id'] in seen:
            continue
        seen.add(r['id'])
        out.append(r)
    return out


def load_arm1_ids(lock_dir=LOCK_DIR, sheet_id=ARM1_SHEET_ID):
    """The first arm's card ids, from its committed lock — the authoritative list.

    Falls back to its frame TSV only if the lock is absent, and says so: before
    H1703 the sheet shipped unbound, and a silent fallback would hide a regression
    of exactly that defect.
    """
    lock = os.path.join(lock_dir, sheet_id + '.lock.json')
    if os.path.exists(lock):
        with io.open(lock, encoding='utf-8') as fh:
            data = json.load(fh)
        ids = data.get('item_ids') or data.get('ids') or []
        if ids:
            return set(ids), 'lock'
    frame = os.path.join(REVIEW_DIR, sheet_id + '_frame.tsv')
    if os.path.exists(frame):
        ids = {('%s~~h%s' % (r['k1'], r['hom'])) if r['hom'] else r['k1']
               for r in read_tsv(frame)}
        return ids, 'frame(no lock!)'
    return set(), 'none'


def load_freq(path=FREQ_TSV):
    out = {}
    for r in read_tsv(path):
        try:
            out[r['k1_slp1']] = int(r['count_all'])
        except (KeyError, ValueError):
            continue
    return out


def length_bucket(k1):
    n = len(k1)
    return 'short(<=8)' if n <= 8 else ('medium(9-10)' if n <= 10 else 'long(>=11)')


def freq_bucket(k1, freq):
    n = freq.get(k1)
    if n is None:
        return 'no_dcs_freq'
    return 'low(1-2)' if n <= 2 else ('mid(3-9)' if n <= 9 else 'high(>=10)')


def vs_index_class(pwg_members, idx_members):
    return ('member_count_diff' if len(pwg_members) != len(idx_members)
            else 'same_count_diff_split')


def allocate(rows, arm1_ids, per_stratum=PER_STRATUM, priced_by_arm1=PRICED_BY_ARM1):
    """Per stratum: (rows, arm1 cards, available disjoint rows, target for arm 2).

    A stratum the first arm already prices gets 0. Otherwise the target is
    `per_stratum`, or the whole disjoint remainder when the stratum is smaller —
    censused, not sampled, so a small stratum is not left unpriceable by rounding.
    """
    by_stratum = {}
    for r in rows:
        by_stratum.setdefault(r['stratum'], []).append(r)
    plan = {}
    for stratum, rs in sorted(by_stratum.items(), key=lambda kv: -len(kv[1])):
        in_arm1 = sum(1 for r in rs if r['id'] in arm1_ids)
        avail = [r for r in rs if r['id'] not in arm1_ids]
        target = 0 if in_arm1 >= priced_by_arm1 else min(per_stratum, len(avail))
        plan[stratum] = {'rows': len(rs), 'arm1_cards': in_arm1,
                         'available': len(avail), 'target': target,
                         'census': 0 < target < per_stratum, '_pool': avail}
    return plan


def draw(plan, seed=SEED):
    rng = random.Random(seed)
    sample = []
    for stratum in sorted(plan):
        info = plan[stratum]
        if not info['target']:
            continue
        pool = sorted(info['_pool'], key=lambda r: r['id'])
        sample.extend(rng.sample(pool, info['target']))
    rng.shuffle(sample)
    return sample


def frame_rows(sample, freq):
    out = []
    for r in sample:
        pwg_m = [m.strip() for m in r['pwg_members'].split('+') if m.strip()]
        idx_m = [m.strip() for m in r['index_members'].split('+') if m.strip()]
        out.append({
            'id': r['id'], 'k1': r['k1'], 'hom': r['hom'],
            'stratum': r['stratum'], 'rule': r['rule'], 'agent_verdict': r['verdict'],
            'pwg_members': r['pwg_members'], 'index_members': r['index_members'],
            'vs_index_class': vs_index_class(pwg_m, idx_m),
            'length_bucket': length_bucket(r['k1']),
            'freq_bucket': freq_bucket(r['k1'], freq),
            'freq_count': freq.get(r['k1'], ''),
            'L_id': r.get('L_id', ''),
            'pwg_source_paren': r.get('pwg_source_paren', ''),
            'mw_k2_raw': r.get('mw_k2_raw', ''),
        })
    return out


FRAME_COLS = ['id', 'k1', 'hom', 'stratum', 'rule', 'agent_verdict', 'pwg_members',
              'index_members', 'vs_index_class', 'length_bucket', 'freq_bucket',
              'freq_count', 'L_id', 'pwg_source_paren', 'mw_k2_raw']


def write_frame_tsv(rows, path=SAMPLE_FRAME_TSV):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FRAME_COLS, delimiter='\t')
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, '') for c in FRAME_COLS})


def _esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_items(rows):
    """Cards for the voter. Carries NOTHING that would unblind the arm — no
    stratum, no rule, no agent verdict, no reason."""
    items = []
    for r in rows:
        display = slp1_iast(r['k1'])
        href = pwg_entry_href(r['k1'])
        title = display + (' (h%s)' % r['hom'] if r['hom'] else '')
        badges = [r['vs_index_class'], r['length_bucket'], r['freq_bucket']]
        if r.get('freq_count') != '':
            badges.append('DCS n=%s' % r['freq_count'])
        question = (
            '<p><b>PWG-членение:</b> <code>%s</code></p>'
            '<p><b>Членение в указателе (index):</b> <code>%s</code></p>'
            '<p style="opacity:.75">Класс расхождения: <code>%s</code></p>'
        ) % (_esc(r['pwg_members']) or '&mdash;',
             _esc(r['index_members']) or '&mdash;', _esc(r['vs_index_class']))
        panels = []
        src = []
        if r.get('pwg_source_paren'):
            src.append('<b>PWG (этимологическая скобка):</b> <code>%s</code>'
                       % _esc(r['pwg_source_paren']))
        if r.get('mw_k2_raw'):
            src.append('<b>MW &lt;k2&gt;:</b> <code>%s</code>' % _esc(r['mw_k2_raw']))
        if src:
            panels.append(('Источник (что реально написано в словарях)', '<br>'.join(src)))
        item = {
            'id': r['id'], 'filt': r['vs_index_class'], 'title': title,
            'badges': badges, 'question': question, 'panels': panels,
            'note_placeholder': 'Если верно ни PWG, ни индекс — укажите правильное членение здесь',
        }
        if href:
            item['title_href'] = href
        items.append(item)
    return items


def render_sheet(rows, generated=GENERATED):
    from csl_pyutil import render_review_sheet
    items = build_items(rows)
    config = {
        'sheet_id': SHEET_ID,
        'title': ('PWG vs указатель: расхождения членения сложных слов '
                  '(вторая слепая выборка, по правилам)'),
        'subtitle': (
            '%d карточек из очереди `differs` (4 246 карточек после починки обоих '
            'экстракторов, H1703). Выборка НЕ пересекается с первой (H1628, 200 '
            'карточек) и покрывает те слои очереди, которые первая выборка не может '
            'оценить статистически.' % len(rows)),
        'footer': (
            'Approve = PWG-членение верно (указатель будет обновлён под PWG). '
            'Reject = членение указателя верно, PWG-слой ошибается. '
            'Defer = нужен дополнительный контекст. '
            'Голоса НЕ закрывают очередь — они калибруют агента по слоям; '
            'продвижение остальных строк считается по нижней границе Уилсона.'),
        'approve_label': 'PWG верно',
        'reject_label': 'Индекс верно',
        'filters': [('member_count_diff', 'Разное число членов'),
                    ('same_count_diff_split', 'Одно число, другое членение')],
        'generated': generated,
        'save_as': r'RussianTranslation\review\%s_decisions.json' % SHEET_ID,
    }
    config.update(standard_config(save_as=config['save_as']))
    return render_review_sheet(items, config)


def report(plan, arm1_src, n_arm1):
    print('arm-1 ids: %d (from %s)' % (n_arm1, arm1_src))
    print()
    print('%-42s %6s %6s %6s %8s' % ('stratum', 'rows', 'arm1', 'avail', 'arm2'))
    total = 0
    for stratum in sorted(plan, key=lambda s: -plan[s]['rows']):
        i = plan[stratum]
        note = ''
        if not i['target']:
            note = '  (priced by arm 1)' if i['arm1_cards'] >= PRICED_BY_ARM1 else '  (nothing left)'
        elif i['census']:
            note = '  (censused in full)'
        print('%-42s %6d %6d %6d %8d%s'
              % (stratum, i['rows'], i['arm1_cards'], i['available'], i['target'], note))
        total += i['target']
    print()
    print('arm-2 total: %d cards' % total)


def selftest():
    rows = []
    for i in range(300):
        rows.append({'id': 'big%d' % i, 'k1': 'big%d' % i, 'hom': '',
                     'stratum': 'big', 'rule': 'big', 'verdict': 'pwg_members-right',
                     'pwg_members': 'a + b', 'index_members': 'a + c'})
    for i in range(20):
        rows.append({'id': 'small%d' % i, 'k1': 'small%d' % i, 'hom': '',
                     'stratum': 'small', 'rule': 'small', 'verdict': 'unresolved',
                     'pwg_members': 'a + b + c', 'index_members': 'a + b'})
    arm1 = {'big%d' % i for i in range(40)}          # big is already priced
    plan = allocate(rows, arm1)
    assert plan['big']['arm1_cards'] == 40 and plan['big']['target'] == 0, plan['big']
    assert plan['small']['target'] == 20 and plan['small']['census'], plan['small']

    arm1_thin = {'big%d' % i for i in range(5)}      # big now needs pricing
    plan2 = allocate(rows, arm1_thin)
    assert plan2['big']['target'] == PER_STRATUM, plan2['big']
    s1 = draw(plan2, seed=7)
    s2 = draw(plan2, seed=7)
    assert [r['id'] for r in s1] == [r['id'] for r in s2], 'draw must be deterministic'
    assert len(s1) == PER_STRATUM + 20, len(s1)
    assert not ({r['id'] for r in s1} & arm1_thin), 'arm 2 must be disjoint from arm 1'
    ids = [it['id'] for it in build_items(frame_rows(s1, {}))]
    assert len(set(ids)) == len(ids), 'duplicate card id'
    html_fields = ' '.join(json.dumps(it, ensure_ascii=False)
                           for it in build_items(frame_rows(s1, {})))
    for leak in ('stratum', 'agent_verdict', 'pwg_members-right', 'unresolved'):
        assert leak not in html_fields, 'card leaks %r — the arm would not be blind' % leak
    # 35 is the smallest arm that can clear the 0.90 gate
    sys.path.insert(0, HERE)
    from adjudicate_compound_differs import wilson_lower
    assert wilson_lower(35, 35) >= 0.9 > wilson_lower(34, 34), (
        wilson_lower(35, 35), wilson_lower(34, 34))
    print('selftest OK — allocation (priced/census/target), deterministic disjoint '
          'draw, unique card ids, no unblinding field on a card, 35-card floor')


def main():
    args = sys.argv[1:]
    if '--selftest' in args:
        selftest()
        return
    rows = load_verdicts()
    arm1_ids, src = load_arm1_ids()
    plan = allocate(rows, arm1_ids)
    if '--report' in args or not args:
        report(plan, src, len(arm1_ids))
        return
    if '--write' in args:
        freq = load_freq()
        sample = draw(plan)
        rows_out = frame_rows(sample, freq)
        ids = [r['id'] for r in rows_out]
        assert len(set(ids)) == len(ids), 'duplicate card id in the sample'
        assert not (set(ids) & arm1_ids), 'arm 2 overlaps arm 1'
        write_frame_tsv(rows_out)
        html = render_sheet(rows_out)
        html, chash = stamp(html)
        os.makedirs(REVIEW_DIR, exist_ok=True)
        with io.open(SHEET_HTML, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
        lock_path = write_lock(SHEET_ID, chash, ids, GENERATED, gate='G6-compound',
                               source_html=SHEET_HTML)
        report(plan, src, len(arm1_ids))
        print()
        print('wrote %d-card sample frame -> %s' % (len(rows_out), SAMPLE_FRAME_TSV))
        print('wrote review sheet -> %s' % SHEET_HTML)
        print('  %s' % chash)
        print('  lock -> %s' % lock_path)
        return
    sys.exit('usage: compound_differs_arm2_sample.py --report | --write | --selftest')


if __name__ == '__main__':
    main()
