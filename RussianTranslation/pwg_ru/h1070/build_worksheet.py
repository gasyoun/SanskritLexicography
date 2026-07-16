#!/usr/bin/env python
r"""build_worksheet.py - H1070 EN gold-adjudication worksheet builder.

Assembles the two-tranche adjudication sample for the PWG->EN Fable-tier gold pass
(H1070), quoting Monier-Williams' own rendering per entry as the adversary baseline:

  tranche A ("pilot"):  the EXACT S7 judged frame, verbatim (src/pilot/output/
                        en_judge_set.s7.jsonl, 68 sense rows, 16 pilot roots,
                        generation Sonnet 4.6) - identical record IDs to
                        FABLE_JUDGE_S7, so its aggregate verdicts stay comparable.
  tranche B ("fu1"):    a FRESH 50-card stratified sample over the 30 FU1 roots
                        (generation Sonnet 5, 2026-07-01), drawn with the SAME policy
                        as fidelity_sample_en.py (imported, not copied), seed rotated
                        42->43 per the S7 memo's per-tranche gate recipe. Senses per
                        card capped at 3 (seeded pick) to keep the Fable reading pass
                        within budget; the cap is declared in the memo.

Per row it attaches MW's rendering from src/mw_en_tm.json: direct subcard headword
when the decoded prefix-chain + root joins to a TM key (mw_scope=subcard), else the
root-article block, truncated (mw_scope=root-article), else mw_scope=absent.

Inputs are gitignored store files that live in the CANONICAL shared tree, not in
worktrees - pass --repo-root to override the default canonical path. Read-only on
every input; writes only into this directory (worksheet.jsonl + worksheet.md).

Usage:
  python build_worksheet.py [--repo-root C:/Users/user/Documents/GitHub/SanskritLexicography]
                            [--seed 43] [--n-cards 50] [--senses-per-card 3]
"""
import argparse
import collections
import glob
import json
import os
import random
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))

FU1_ROOTS = ['nI', 'yA', 'dA', 'han', 'car', 'viS', 'jYA', 'vas', 'hA', 'vA',
             'diS', 'mA', 'vah', 'iz', 'muc', 'su', 'Ap', 'jan', 'banD', 'man',
             'Sru', 'siD', 'vac', 'ji', 'paS', 'brU', 'laB', 'jIv', 'As', 'gam']

MW_QUOTE_LIMIT = 420


def decode_safe_tag(tag):
    """Decode a Windows-safe key tag back to SLP1: '_x' -> 'X', trailing '_<digit>'
    variant indexes dropped ('a_di_0' -> 'aDi', 'up_ati' -> 'upAti')."""
    parts = tag.split('_')
    out = [parts[0]]
    for p in parts[1:]:
        if not p:
            continue
        if p[0].isdigit():
            break
        out.append(p[0].upper() + p[1:])
    return ''.join(out)


NON_PREFIX_TAGS = re.compile(r'^(pwg\d+|sec(_\d+)*|intro|verb|\d+)$')


def mw_for_key(key, root, tm):
    """(mw_text, mw_scope) for a subcard key like 'gam~~h0_06_ati'."""
    m = re.match(r'^[^~]+~~h\d+_\d+_(.+)$', key)
    tag = m.group(1) if m else ''
    if tag and not NON_PREFIX_TAGS.match(tag):
        cand = decode_safe_tag(tag) + root
        if cand in tm:
            return tm[cand], 'subcard:' + cand
    if root in tm:
        return tm[root], 'root-article:' + root
    return '', 'absent'


def load_s7_sample(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default=r'C:/Users/user/Documents/GitHub/SanskritLexicography')
    ap.add_argument('--seed', type=int, default=43)
    ap.add_argument('--n-cards', type=int, default=50)
    ap.add_argument('--senses-per-card', type=int, default=3)
    args = ap.parse_args()

    rt = os.path.join(args.repo_root, 'RussianTranslation')
    sys.path.insert(0, os.path.join(rt, 'src'))
    import fidelity_sample_en as fse  # reuse, don't copy (SHARED_CODE rule)

    tm = json.load(open(os.path.join(rt, 'src', 'mw_en_tm.json'), encoding='utf-8'))
    wf_dir = os.path.join(rt, 'archive', 'legacy_runtime_2026-07-04')

    # ---- tranche B: fresh FU1 50-card sample, same policy as fidelity_sample_en ----
    all_paths = sorted(glob.glob(os.path.join(wf_dir, 'wf_output.en.*.json')))
    fu1_paths = []
    for p in all_paths:
        try:
            meta = (fse.load_wf(p).get('meta') or {})
        except Exception:
            continue
        if meta.get('root') in FU1_ROOTS:
            fu1_paths.append(p)
    best = fse.collect_cards(fu1_paths)
    cards = []
    for subkey, entry in best.items():
        senses = fse.card_senses(entry['card'])
        if not senses:
            continue
        cards.append({'key': subkey, 'iast': entry['card'].get('iast'),
                      'root': entry['meta'].get('root'), 'wf_file': entry['wf_file'],
                      'stratum': fse.card_stratum(entry['card']), 'senses': senses})
    by_stratum = collections.defaultdict(list)
    for c in cards:
        by_stratum[c['stratum']].append(c)
    rng = random.Random(args.seed)
    total = len(cards)
    picked = []
    for stratum, group in sorted(by_stratum.items()):
        group = sorted(group, key=lambda c: c['key'])
        rng.shuffle(group)
        want = max(min(5, len(group)), round(args.n_cards * len(group) / total)) if total else 0
        picked.extend(group[:min(want, len(group))])
    rng.shuffle(picked)
    picked = picked[:args.n_cards] if len(picked) > args.n_cards else picked

    # sense cap (seeded, deterministic)
    for c in picked:
        if len(c['senses']) > args.senses_per_card:
            idx = sorted(rng.sample(range(len(c['senses'])), args.senses_per_card))
            c['senses'] = [c['senses'][i] for i in idx]

    # ---- tranche A: the exact S7 judged frame ----
    s7 = load_s7_sample(os.path.join(rt, 'src', 'pilot', 'output', 'en_judge_set.s7.jsonl'))

    rows, uid = [], 0
    for r in s7:
        root = r.get('key1') or ''
        mw_text, mw_scope = mw_for_key(r['subcard'], root, tm)
        uid += 1
        rows.append({
            'uid': 'r%03d' % uid, 'tranche': 'pilot',
            'gen_model': 'Sonnet 4.6 (claude-sonnet-4-6)',
            'key': r['subcard'], 'iast': r.get('headword'), 'root': root,
            'stratum': r.get('stratum'), 'tag': r.get('sense_tag'),
            'de': r.get('de'), 'en': r.get('en'),
            'mw': (mw_text or '')[:MW_QUOTE_LIMIT], 'mw_scope': mw_scope,
            's7_id': r.get('id'),
        })
    for c in picked:
        root = c.get('root') or ''
        mw_text, mw_scope = mw_for_key(c['key'], root, tm)
        for s in c['senses']:
            uid += 1
            rows.append({
                'uid': 'r%03d' % uid, 'tranche': 'fu1',
                'gen_model': 'Sonnet 5 (claude-sonnet-5)',
                'key': c['key'], 'iast': c.get('iast'), 'root': root,
                'stratum': c.get('stratum'), 'tag': s.get('tag'),
                'de': s.get('de'), 'en': s.get('en'),
                'mw': (mw_text or '')[:MW_QUOTE_LIMIT], 'mw_scope': mw_scope,
            })

    out_jsonl = os.path.join(HERE, 'worksheet.jsonl')
    with open(out_jsonl, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    out_md = os.path.join(HERE, 'worksheet.md')
    with open(out_md, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write('### %(uid)s [%(tranche)s] %(key)s (%(iast)s) stratum=%(stratum)s\n'
                    'DE: %(de)s\nEN: %(en)s\nMW [%(mw_scope)s]: %(mw)s\n\n' % r)

    n_by = collections.Counter(r['tranche'] for r in rows)
    mw_by = collections.Counter(r['mw_scope'].split(':')[0] for r in rows)
    print('rows: %d  by tranche: %s' % (len(rows), dict(n_by)))
    print('FU1 cards sampled: %d (population %d, seed %d)' % (len(picked), total, args.seed))
    print('mw scope: %s' % dict(mw_by))
    print('wrote %s / %s' % (out_jsonl, out_md))


if __name__ == '__main__':
    main()
