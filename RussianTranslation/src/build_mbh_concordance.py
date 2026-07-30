#!/usr/bin/env python
r"""Mahābhārata: PWG's continuous Calcutta śloka number → the corpus keying (H1652).

PWG (Böhtlingk-Roth) cites the **Calcutta edition (1834–39)**, which numbers
ślokas continuously within each parvan — `MBH. 5,7331` is Udyogaparva śloka 7331,
with no adhyāya coordinate. SamudraManthanam's `corpus.db` keys the **BORI/Poona
critical** edition's `parvan.adhyāya.verse`. Reuse of the Russian translation of
record therefore needs a Calcutta↔critical map, which is the last remaining
`unmapped_locus_scheme` GAP in `citation_tm.py`. MG ruled 21-07-2026 (weekly
`@DECIDE` sheet): **build it**.

The candidate map, and why it looked cheap
------------------------------------------
CommentaryStrategies already ships an eighteen-parvan **Nīlakaṇṭha vulgate ↔
critical** verse concordance (`data/edition_comparison_mbh/*/concordance.json`,
built by its `scripts/compare_editions_mbh.py`). Calcutta and the Nīlakaṇṭha
vulgate are the same recension family, so the missing piece looked like nothing
more than a cumulative sum: add up the vulgate's per-adhyāya verse counts, and
continuous śloka N falls in the adhyāya whose running total brackets it. That
deterministic sum is `build` below, committed as `mbh_vulgate_cumulative.tsv`.

Why it does NOT close the gap
-----------------------------
`validate` tests the chain end-to-end against the PWG store itself, and it
fails — see `pwg_ru/H1652_MBH_CALCUTTA_VALIDATION_2026-07-26.md` for the full
tables. Headline: of 1 327 store citations whose headword stem is long enough to
locate, the cumulative map puts only **11.2 %** within ±2 verses of where the
headword actually occurs (uniform-random null: 2.5 %); a per-parvan linear
rescale fitted on half the anchors reaches **16.3 %** on the held-out half; and
on the strictest subset — 43 citations whose stem occurs exactly once in the
whole parvan, so the true verse is not a judgement call — it is **1/43 (2.3 %)**.
The sanatana.in vulgate e-text is also materially shorter than the text PWG
counts in 8 of 18 parvans (Vanaparvan: 11 859 verses against a PWG citation
reaching 17 471), so for some citations no ordinal exists at all.

The chain below the failing step is sound and was verified independently: vulgate
`6.26.47` → critical `6.24.47` → `06_mahabharata-bhishmaparva:6.24.47#sa` is
`karmaṇyevādhikāraste…` = Bhagavadgītā 2.47, exactly as it should be. What fails
is the *first* step: PWG's Calcutta numbering is not the cumulative ordinal of
this vulgate witness. Closing the GAP needs the Calcutta text itself (or a
published Calcutta↔critical concordance) plus a content-based alignment of the
H1656 kind — not arithmetic over a different witness.

So `citation_tm.MBH.` stays `unmapped_locus_scheme`. The cumulative table is
committed anyway: it is the deterministic half a successor would otherwise
rebuild, and `selftest` pins it — but it is **REJECTED FOR REUSE** and no code
may key a citation through it.

  python src/build_mbh_concordance.py build      [--cs-dir DIR]   # local only
  python src/build_mbh_concordance.py validate   [--report PATH]  # local only
  python src/build_mbh_concordance.py selftest                    # CI gate
"""
import argparse
import bisect
import collections
import csv
import json
import os
import random
import re
import sqlite3
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
from sibling_root import sibling_root  # noqa: E402
GITHUB = sibling_root(HERE)

CS_DIR = os.environ.get('MBH_EDITION_COMPARISON_DIR', os.path.join(
    GITHUB, 'CommentaryStrategies', 'data', 'edition_comparison_mbh'))
CORPUS_DB = os.environ.get('SAMUDRA_CORPUS_DB', os.path.join(
    GITHUB, 'SamudraManthanam', 'web', 'corpus.db'))
# The store is gitignored and lives in whichever checkout generated it — a
# worktree has none, so allow an explicit override rather than failing there.
RU_STORE = os.environ.get('PWG_RU_STORE', os.path.join(HERE, 'pwg_ru_translated.jsonl'))

OUT_CUM = os.path.join(HERE, 'mbh_vulgate_cumulative.tsv')

# Minimum folded-stem length for an anchor to be locatable by substring at all.
MIN_STEM = 5
SEED = 20260726


# --- shared helpers ----------------------------------------------------------

def nfold(s):
    """Diacritics/length stripped, nasals folded → n — the same canonicalisation
    family `sanskrit_util.nfold` applies when the concordances are built."""
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z]', '', re.sub(r'[ṃṅñṇm]', 'n', s.lower()))


def parvan_dirs(cs_dir):
    """parva_no → directory name, read from each concordance's own `_meta`."""
    out = {}
    if not os.path.isdir(cs_dir):
        return out
    for d in sorted(os.listdir(cs_dir)):
        p = os.path.join(cs_dir, d, 'concordance.json')
        if os.path.isfile(p):
            with open(p, encoding='utf-8') as fh:
                out[json.load(fh)['_meta']['parva_no']] = d
    return out


def load_concordance(cs_dir, dirname):
    """→ (ordered [(adhyāya, verse)] of the vulgate, {(adhyāya,verse): critical})."""
    with open(os.path.join(cs_dir, dirname, 'concordance.json'), encoding='utf-8') as fh:
        doc = json.load(fh)
    per, v2c = collections.defaultdict(list), {}
    for r in doc['concordance']:
        v = r.get('vulgate')
        if not v:
            continue
        _, a, ve = (int(x) for x in v.split('.'))
        per[a].append(ve)
        if r.get('critical'):
            v2c[(a, ve)] = tuple(int(x) for x in r['critical'].split('.'))
    seq = [(a, ve) for a in sorted(per) for ve in sorted(per[a])]
    return seq, v2c


# --- build -------------------------------------------------------------------

def cmd_build(args):
    """Cumulative adhyāya-length table over the vulgate side of the concordances.

    One row per (parvan, adhyāya): the continuous-ordinal span that adhyāya would
    occupy if PWG's Calcutta number were this witness's running count. It is not
    — see `validate` — so the table is documentation of a rejected hypothesis and
    a head start for a successor, never a lookup path."""
    cs_dir = args.cs_dir or CS_DIR
    dirs = parvan_dirs(cs_dir)
    if not dirs:
        sys.exit('no MBH concordances under %s (local-only input; absent in CI)' % cs_dir)
    rows = []
    for pno in sorted(dirs):
        seq, _ = load_concordance(cs_dir, dirs[pno])
        per = collections.Counter(a for a, _ in seq)
        run = 0
        for a in sorted(per):
            n = per[a]
            rows.append({'parvan': pno, 'adhyaya': a, 'n_verses': n,
                         'first_continuous': run + 1, 'last_continuous': run + n})
            run += n
        print('parvan %2d (%-20s): %4d adhyāyas, %6d vulgate verses'
              % (pno, dirs[pno], len(per), run))
    with open(OUT_CUM, 'w', encoding='utf-8', newline='\n') as fh:
        w = csv.DictWriter(fh, delimiter='\t', lineterminator='\n',
                           fieldnames=['parvan', 'adhyaya', 'n_verses',
                                       'first_continuous', 'last_continuous'])
        w.writeheader()
        w.writerows(rows)
    print('wrote %s (%d rows) — REJECTED FOR REUSE, see the module docstring'
          % (OUT_CUM, len(rows)))


# --- validate ----------------------------------------------------------------

_LS = re.compile(r'<ls\b([^>]*)>(.*?)</ls>', re.S)
_N_ATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')


def store_anchors(path=RU_STORE):
    """Every distinct two-number `MBH. P,N` citation in the store, with the
    headword of the card that carries it."""
    out = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            hw = rec.get('iast') or ''
            if not hw:
                continue
            seen = set()
            for fld in ('de', 'ru'):
                v = rec.get(fld)
                if not isinstance(v, str):
                    continue
                for m in _LS.finditer(v):
                    nm = _N_ATTR.search(m.group(1) or '')
                    s = ((nm.group(1) if nm else '') or (m.group(2) or '')).strip()
                    if not re.match(r'^\s*MBH\.', s, re.I):
                        continue
                    nums = [int(x) for x in re.findall(r'\d+', s)]
                    if len(nums) != 2 or (nums[0], nums[1]) in seen:
                        continue
                    seen.add((nums[0], nums[1]))
                    out.append((nums[0], nums[1], hw, s.strip()))
    return out


def _mbh_sanskrit(db):
    """canonical_id → IAST line, for every MBH `#sa` row. One full pass: the
    fts5 `canonical_id` column is UNINDEXED, so per-key queries each cost a
    table scan and a naive loop takes hours."""
    con = sqlite3.connect('file:%s?mode=ro' % db, uri=True)
    try:
        return {cid: txt for cid, txt in
                con.execute('select canonical_id, line_text from corpus_lines')
                if cid and cid.endswith('#sa') and 'mahabharata' in cid}
    finally:
        con.close()


def _segment_index(sa, work):
    """critical (adhyāya, verse) → canonical_id, expanding `a.v-w` range keys
    (the RU translations group several ślokas into one segment)."""
    idx, pref = {}, work + ':'
    for cid in sa:
        if not cid.startswith(pref):
            continue
        parts = cid[len(pref):-3].split('.')
        if len(parts) != 3 or not parts[1].isdigit():
            continue
        m = re.match(r'^(\d+)(?:-(\d+))?$', parts[2])
        if not m:
            continue
        a = int(parts[1])
        for v in range(int(m.group(1)), int(m.group(2) or m.group(1)) + 1):
            idx.setdefault((a, v), cid)
    return idx


def _nearest(pos, n):
    k = bisect.bisect_left(pos, n)
    cand = [p for p in (pos[k - 1] if k else None, pos[k] if k < len(pos) else None)
            if p is not None]
    return min(cand, key=lambda p: abs(p - n))


def cmd_validate(args):
    """Test the cumulative hypothesis against the PWG store.

    For each citation `MBH. P,N` on a card headed by stem S: take N as the
    vulgate ordinal, walk to the critical verse, and ask where S actually occurs
    in that parvan. Reported against a uniform-random null, because a substring
    test has a non-zero background rate and the raw hit share must never be read
    on its own."""
    cs_dir = args.cs_dir or CS_DIR
    dirs = parvan_dirs(cs_dir)
    if not dirs:
        sys.exit('no MBH concordances under %s' % cs_dir)
    if not os.path.exists(CORPUS_DB):
        sys.exit('corpus.db absent (%s) — validation needs the local corpus' % CORPUS_DB)
    if not os.path.exists(RU_STORE):
        sys.exit('RU store absent (%s) — validation needs the local store' % RU_STORE)

    sa = _mbh_sanskrit(CORPUS_DB)
    works = {}
    for cid in sa:
        w = cid.split(':')[0]
        works[int(w.split('_')[0])] = w

    texts, segs = {}, {}
    for pno, d in sorted(dirs.items()):
        seq, v2c = load_concordance(cs_dir, d)
        idx = _segment_index(sa, works[pno])
        t, g = [], []
        for (a, ve) in seq:
            crit = v2c.get((a, ve))
            cid = idx.get((crit[1], crit[2])) if crit else None
            t.append(nfold(sa.get(cid) or '') if cid else '')
            g.append(cid)
        texts[pno], segs[pno] = t, g

    anchors = store_anchors()
    rng = random.Random(SEED)
    poscache = {}

    def positions(pno, stem):
        key = (pno, stem)
        if key not in poscache:
            poscache[key] = [j for j, t in enumerate(texts[pno], 1) if stem in t]
        return poscache[key]

    usable, unique, over = [], [], 0
    for pno, N, hw, _raw in anchors:
        stem = nfold(hw)
        if len(stem) < MIN_STEM or pno not in texts:
            continue
        pos = positions(pno, stem)
        if not pos:
            continue
        if N > len(texts[pno]):
            over += 1
        usable.append((pno, N, pos))
        if len(pos) == 1 and len(stem) >= 6:
            unique.append((pno, N, hw, pos[0], len(texts[pno])))

    def share(items, pick):
        o = [abs(_nearest(pos, pick(pno, N)) - pick(pno, N)) for pno, N, pos in items]
        n = len(o) or 1
        return (len(o),
                100.0 * sum(1 for x in o if x <= 2) / n,
                100.0 * sum(1 for x in o if x <= 10) / n)

    def ident(_pno, n):
        return n

    n_id, id2, id10 = share(usable, ident)
    null = [(pno, rng.randrange(1, len(texts[pno]) + 1), pos) for pno, _, pos in usable]
    n_nu, nu2, nu10 = share(null, ident)

    lines = []
    lines.append('anchors usable: %d (of %d MBH citations in the store)'
                 % (n_id, len(anchors)))
    lines.append('IDENTITY  n=%d  within ±2 %.1f%%  within ±10 %.1f%%' % (n_id, id2, id10))
    lines.append('NULL      n=%d  within ±2 %.1f%%  within ±10 %.1f%%' % (n_nu, nu2, nu10))
    lines.append('PWG number past the end of the whole vulgate parvan: %d' % over)

    # per-parvan linear rescale, fitted on half, scored on the held-out half
    bypar = collections.defaultdict(list)
    for it in usable:
        bypar[it[0]].append(it)
    fits, test = {}, []
    for pno, items in sorted(bypar.items()):
        order = list(range(len(items)))
        rng.shuffle(order)
        half = len(order) // 2
        tr = [items[i] for i in order[:half]]
        te = [items[i] for i in order[half:]]
        L = len(texts[pno])
        best, bs = -1, 1.0
        for s in [x / 200.0 for x in range(60, 281)]:          # 0.30 .. 1.40
            hit = 0
            for _, N, pos in tr:
                j = max(1, min(L, int(round(s * N))))
                if abs(_nearest(pos, j) - j) <= 2:
                    hit += 1
            if hit > best:
                best, bs = hit, s
        fits[pno] = bs
        test += te
    def scaled(pno, n):
        return max(1, min(len(texts[pno]), int(round(fits[pno] * n))))

    n_sc, sc2, sc10 = share(test, scaled)
    n_bl, bl2, bl10 = share(test, ident)
    lines.append('SCALE held-out  n=%d  within ±2 %.1f%%  within ±10 %.1f%% '
                 '(identity on the same held-out half: %.1f%% / %.1f%%)'
                 % (n_sc, sc2, sc10, bl2, bl10))

    ex = sum(1 for pno, N, _hw, j, L in unique if 1 <= N <= L and abs(N - j) <= 2)
    lines.append('UNIQUE-OCCURRENCE anchors: %d, of which within ±2: %d (%.1f%%)'
                 % (len(unique), ex, 100.0 * ex / (len(unique) or 1)))
    verdict = ('REJECTED — the cumulative map does not reconstruct PWG\'s Calcutta '
               'numbering; MBH. stays unmapped_locus_scheme')
    lines.append('VERDICT: %s' % verdict)

    for ln in lines:
        print(ln)
    if args.report:
        with open(args.report, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write('\n'.join(lines) + '\n')
        print('wrote %s' % args.report)


# --- selftest ----------------------------------------------------------------

def cmd_selftest(_args):
    """CI gate over the COMMITTED table — no local stores, no corpus, no network.

    Two duties: the table is structurally sound, AND the resolver still refuses
    to use it. The second is the load-bearing one — a future edit that quietly
    keys MBH citations through this rejected table must fail here."""
    fails = []

    def check(cond, msg):
        (print('  ok  - %s' % msg) if cond else fails.append(msg))

    with open(OUT_CUM, encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh, delimiter='\t'))
    check(len(rows) > 2000, 'cumulative table has %d adhyāya rows (>2000)' % len(rows))
    parv = {int(r['parvan']) for r in rows}
    check(parv == set(range(1, 19)), 'all 18 parvans present (%d)' % len(parv))

    per = collections.defaultdict(list)
    for r in rows:
        per[int(r['parvan'])].append(r)
    contiguous = True
    for pno, rs in sorted(per.items()):
        run = 0
        for r in rs:
            n = int(r['n_verses'])
            if int(r['first_continuous']) != run + 1 or int(r['last_continuous']) != run + n:
                contiguous = False
                break
            run += n
        if not contiguous:
            break
    check(contiguous, 'continuous spans are gapless and consistent with n_verses')
    check(all(int(r['n_verses']) > 0 for r in rows), 'every adhyāya has ≥1 verse')

    totals = {p: int(rs[-1]['last_continuous']) for p, rs in per.items()}
    # The measured shortfalls that sink the hypothesis — pinned so a silent
    # regeneration against a different (longer) witness is noticed, not absorbed.
    check(totals[3] < 17471,
          'Vanaparvan total %d is below the PWG citation reaching 17471 '
          '(the shortfall this table documents)' % totals[3])
    check(totals[5] < 7656,
          'Udyogaparvan total %d is below the PWG citation reaching 7656' % totals[5])

    sys.path.insert(0, HERE)
    import citation_tm                                            # noqa: E402
    rec = citation_tm.lookup('MBH.', '5,7331')
    check(rec['status'] == 'unmapped_locus_scheme',
          'MBH. 5,7331 still unmapped_locus_scheme (validation REJECTED the map)')
    check(rec.get('canonical_id') is None,
          'a rejected map never populates canonical_id for MBH.')

    print()
    if fails:
        for f in fails:
            print('  FAIL - %s' % f)
        sys.exit('%d selftest check(s) FAILED' % len(fails))
    print('build_mbh_concordance selftest: all checks green')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd')
    b = sub.add_parser('build', help='cumulative adhyāya table (needs the local sibling repo)')
    b.add_argument('--cs-dir', help='CommentaryStrategies data/edition_comparison_mbh')
    v = sub.add_parser('validate', help='test the map against the store (needs local stores)')
    v.add_argument('--cs-dir')
    v.add_argument('--report', help='also write the numbers to this path')
    sub.add_parser('selftest', help='CI gate over the committed table')
    args = ap.parse_args()
    if args.cmd == 'build':
        cmd_build(args)
    elif args.cmd == 'validate':
        cmd_validate(args)
    elif args.cmd == 'selftest':
        cmd_selftest(args)
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
