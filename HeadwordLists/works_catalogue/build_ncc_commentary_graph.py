"""NCC commentary edge graph, dual rankings and four-set coverage (H7202).

Rebuilds the 2022 VisualDCS commentary tree (Commentary_tree_NCC_2022.xls,
3,355 works, builder undocumented) from the NCC bodies themselves, as a
commentary EDGE graph in two variants:

  strict -- marker-tagged relations only ("C. on X" / "Comm. on X" /
            "tika on X" entry-side markers and "C. <Title>" list-side
            markers) where BOTH endpoints resolve to catalogue entries;
            deduped on (base-work x commentary-title).  Conservative floor.
  fuzzy  -- every extracted relation: strict pairs plus relative targets
            ("the previous title", "same") resolved to their context, so
            recall-goals strings cannot silently vanish.  Recall ceiling.

Every edge carries per-edge provenance (`ncc` / `acc`): the late sa-tail and
all ha- works have no NCC bodies (the export, and the 2022 database behind it,
end at vol 39 p. 378 `Suhodita` -- H7078), so commentary relations on those
bases are backfilled from the ACC bodies (a -> h complete) and tagged `acc`.
ACC commentary records that no NCC entry and no crosswalk row covers become
synthetic `acc:<L>` nodes so their edges still count -- never blended silently.

Two rankings per variant, per grill decisions #1 (both, equally weighted):
raw subtree size with an l1..l7 level profile (the 2022-tree metric, l7 =
depth >= 7) and true PageRank on the commentary digraph (all edges, not the
primary forest).  The 2022 xls top-20 is the canary.

Work identity: match_key spelling class + pure-see-ref variants +
works_crosswalk tiers A/B (C/D parked per the 22-10 grill).  Each commentary
joins exactly one primary base (shallowest base chain, catalogue-order
tie-break) so raw tree sizes are the 2022-tree quantity; PageRank keeps
every edge.

Coverage joins the top-N canon (five cuts N=50/100/250/500/1000 + cumulative
curve) against DCS 288, PD 164 adjudicated sigla, the PWG lsextract citation
inventory (occurrence-weighted, full alphabet) and ACC k1/crosswalk.

Rights: NCC CC BY-NC 4.0 (permission on record), ACC CC BY-SA 4.0.  No
combined public dump is produced; the TSV carries per-work provenance counts.

Modules (split for the token-size gate, estate tool Uprava PR #5383):
extraction in ncc_commentary_extract.py, graph/identity/coverage in
ncc_commentary_graph.py; this file is the CLI + assembly.

Usage (defaults = Mac estate checkout; override any input):
    python build_ncc_commentary_graph.py
"""
import argparse
import csv
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from ncc_commentary_extract import (ACC_TXT, CROSSWALK, NCC_JSONL, XLS_2022,
                                    TitleIndex, acc_backfill_edges, fold,
                                    load_ncc, ncc_edges, parse_acc,
                                    resolve_target, sa_tail_ha, title_node)
from ncc_commentary_graph import (ENTRIES_BY_ID, _order_cache, build_clusters,
                                  build_graph, coverage_tables, order_key,
                                  order_key_by_id, pagerank, set_entries,
                                  tree_profile, load_coverage_sets)

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ncc', default=NCC_JSONL)
    ap.add_argument('--acc', default=ACC_TXT)
    ap.add_argument('--xls', default=XLS_2022)
    ap.add_argument('--crosswalk', default=CROSSWALK)
    ap.add_argument('--out', default=os.path.join(HERE, 'ncc_commentary_ranking.tsv'))
    ap.add_argument('--edges', default=os.path.join(HERE, 'ncc_commentary_edges.tsv'))
    ap.add_argument('--report', default=os.path.join(HERE, 'ncc_commentary_report.json'))
    ap.add_argument('--precision-sample', type=int, default=60)
    ap.add_argument('--seed', type=int, default=20261022)
    ap.add_argument('--skip-acc', action='store_true')
    args = ap.parse_args()

    print('loading NCC …', file=sys.stderr)
    entries = load_ncc(args.ncc)
    set_entries(entries)
    index = TitleIndex(entries)

    print('building work clusters …', file=sys.stderr)
    dsu, cluster_stats, L_map, alias_folds = build_clusters(entries, index, args.crosswalk)
    # canonical cluster id = min member by catalogue order (the DSU's own
    # string-min can disagree with order_key and split identities between
    # the edge table and the ranking rows)
    canon = {}
    for r in entries:
        root = dsu.find(r['ncc_id'])
        cur = canon.get(root)
        if cur is None or order_key(ENTRIES_BY_ID, r['ncc_id']) < order_key(ENTRIES_BY_ID, cur):
            canon[root] = r['ncc_id']

    def cf(nid):
        return canon[dsu.find(nid)]

    members = defaultdict(list)
    for r in entries:
        members[cf(r['ncc_id'])].append(r)
    # fold -> representative entry, only where the fold is unambiguous
    fold_map = {}
    for c, ms in members.items():
        folds = {fold(m['iast']) for m in ms if m['iast']}
        for m in ms:
            folds |= alias_folds.get(m['ncc_id'], set())
        rep = min(ms, key=lambda r: order_key(ENTRIES_BY_ID, r['ncc_id']))
        for fo in folds:
            if not fo:
                continue
            cur = fold_map.get(fo)
            if cur is None or cur == 'AMBIG':
                fold_map[fo] = rep
            elif cur['ncc_id'] != rep['ncc_id']:
                fold_map[fo] = 'AMBIG'   # ambiguous fold: unusable

    def resolve(raw):
        return resolve_target(raw, index, fold_map)

    print('extracting NCC relations …', file=sys.stderr)
    body_folds = []
    ncc_e = ncc_edges(entries, resolve, index, body_folds=body_folds)

    # ACC backfill: commentary = crosswalk-joined cluster or synthetic node
    acc_records = []
    acc_rows = []
    if not args.skip_acc:
        print('parsing ACC records …', file=sys.stderr)
        acc_records = parse_acc(args.acc)
        acc_rows = acc_backfill_edges(acc_records, index, cf, L_map)
        print(f'ACC backfill edges resolved: {len(acc_rows)}', file=sys.stderr)

    def to_row(e):
        c, comm_raw = e.get('commentary'), e.get('comm_raw')
        b, base_raw = e.get('base_entry'), e.get('base_title_raw')
        c_cluster = cf(c['ncc_id']) if c else (title_node(comm_raw) if comm_raw else None)
        b_cluster = cf(b['ncc_id']) if b else (title_node(base_raw) if base_raw else None)
        return dict(
            commentary_cluster=c_cluster,
            commentary_title=c['iast'] if c else (comm_raw or ''),
            commentary_acc_L='',
            base_cluster=b_cluster,
            base_title=b['iast'] if b else (base_raw or ''),
            base_title_raw=base_raw or '',
            side=e.get('side', ''), marker=e.get('marker', ''),
            resolved=e.get('resolved', False),
            provenance='ncc')

    ncc_rows = [to_row(e) for e in ncc_e]
    # strict = both endpoints resolved to catalogue entries (incl. the
    # named-tika route and crosswalk-joined ACC backfill);
    # fuzzy = every relation, unresolved titles as synthetic `t:<fold>` nodes
    strict_rows = [r for r in ncc_rows if r['resolved']] + acc_rows
    fuzzy_rows = ncc_rows + acc_rows

    def dedupe(rows):
        seen, out = set(), []
        for r in rows:
            if not r['base_cluster'] or not r['commentary_cluster']:
                continue
            key = (r['base_cluster'], r['commentary_cluster'], r['provenance'])
            if key not in seen:
                seen.add(key)
                out.append(r)
        return out

    strict_dedup = dedupe(strict_rows)
    fuzzy_dedup = dedupe(fuzzy_rows)
    acc_only = sum(1 for r in strict_dedup if r['provenance'] == 'acc')
    print(f'edges: strict {len(strict_dedup)} (ncc {len(strict_dedup)-acc_only} + acc {acc_only}), '
          f'fuzzy {len(fuzzy_dedup)}', file=sys.stderr)

    graphs, prs, profiles = {}, {}, {}
    for variant, rows in (('strict', strict_dedup), ('fuzzy', fuzzy_dedup)):
        g = build_graph(rows)
        graphs[variant] = g
        prs[variant] = pagerank(g['nodes'], g['all_edges'])
        profiles[variant] = tree_profile(g)

    universe = sorted(graphs['strict']['nodes'] | graphs['fuzzy']['nodes'],
                      key=order_key_by_id)

    rep_title, rep_numid, aliases, title_fold_set = {}, {}, {}, {}
    for c, ms in members.items():
        ms_sorted = sorted(ms, key=lambda r: order_key(ENTRIES_BY_ID, r['ncc_id']))
        rep_title[c] = ms_sorted[0]['iast']
        rep_numid[c] = ms_sorted[0]['ncc_numid']
        aliases[c] = [m['iast'] for m in ms_sorted[1:9]]
        title_fold_set[c] = {fold(m['iast']) for m in ms if m['iast']}
        for m in ms:
            title_fold_set[c] |= alias_folds.get(m['ncc_id'], set())
    # register synthetic fuzzy title nodes
    for r in fuzzy_dedup:
        for cl, t in ((r['commentary_cluster'], r['commentary_title']),
                      (r['base_cluster'], r['base_title'])):
            if cl and cl.startswith('t:') and cl not in rep_title:
                rep_title[cl] = t
                rep_numid[cl] = ''
                aliases[cl] = []
                title_fold_set[cl] = {fold(t)} if t else set()
    acc_flag = {c: False for c in members}
    with open(args.crosswalk, encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            nid = row.get('ncc_id')
            if nid and nid in ENTRIES_BY_ID:
                acc_flag[cf(nid)] = True
    # register synthetic acc:<L> nodes so every graph node has identity data
    known_L = {n.split(':', 1)[1] for n in universe if n.startswith('acc:')}
    acc_L_to_title = {r['L']: r['title'] for r in acc_records}
    for L in known_L:
        c = 'acc:' + L
        t = acc_L_to_title.get(L, L)
        rep_title[c] = t
        rep_numid[c] = ''
        aliases[c] = []
        title_fold_set[c] = {fold(t)}
    # in-edge counts exclude self-cluster edges (an entry's own body listing
    # its own cluster's works) -- they are not commentaries received
    acc_in = Counter(r['base_cluster'] for r in strict_dedup
                     if r['provenance'] == 'acc' and r['base_cluster'] != r['commentary_cluster'])
    ncc_in = Counter(r['base_cluster'] for r in strict_dedup
                     if r['provenance'] == 'ncc' and r['base_cluster'] != r['commentary_cluster'])

    def sort_key(c):
        return (-profiles['strict'].get(c, (0, Counter()))[0],
                -profiles['fuzzy'].get(c, (0, Counter()))[0],
                -prs['strict'].get(c, 0.0),
                rep_title.get(c, c))

    universe.sort(key=sort_key)
    ranked = dict(order=universe, title_fold_set=title_fold_set, acc_flag=acc_flag)

    def lvl_str(levels):
        def col(i):
            if i < 7:
                return levels.get(i, 0)
            return sum(v for k, v in levels.items() if k >= 7)
        return '|'.join(str(col(i)) for i in range(1, 8))

    with open(args.out, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['rank', 'work_id', 'title', 'numid', 'aliases',
                    'strict_tree_size', 'strict_l1_l7', 'strict_pagerank',
                    'fuzzy_tree_size', 'fuzzy_l1_l7', 'fuzzy_pagerank',
                    'in_edges_ncc', 'in_edges_acc', 'in_acc_crosswalk'])
        for i, c in enumerate(universe, 1):
            ss, sl = profiles['strict'].get(c, (0, Counter()))
            fs, fl = profiles['fuzzy'].get(c, (0, Counter()))
            w.writerow([i, c, rep_title.get(c, c), rep_numid.get(c, ''),
                        '|'.join(aliases.get(c, [])),
                        ss, lvl_str(sl), f"{prs['strict'].get(c, 0.0):.3e}",
                        fs, lvl_str(fl), f"{prs['fuzzy'].get(c, 0.0):.3e}",
                        ncc_in.get(c, 0), acc_in.get(c, 0),
                        1 if acc_flag.get(c) else 0])

    # edge table: strict rows + fuzzy-only rows, per-edge provenance
    strict_keys = {(r['base_cluster'], r['commentary_cluster'], r['provenance'])
                   for r in strict_dedup}
    with open(args.edges, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['variant', 'provenance', 'marker', 'side',
                    'commentary_id', 'commentary_title', 'base_id', 'base_title',
                    'base_title_raw', 'acc_L'])
        for variant, rows in (('strict', strict_dedup), ('fuzzy', fuzzy_dedup)):
            for r in sorted(rows, key=lambda r: (r['provenance'], r['base_title'],
                                                 r['commentary_title'])):
                if variant == 'fuzzy' and (r['base_cluster'], r['commentary_cluster'],
                                           r['provenance']) in strict_keys:
                    continue
                w.writerow([variant, r['provenance'], r['marker'], r['side'],
                            r['commentary_cluster'], r['commentary_title'],
                            r['base_cluster'], r['base_title'],
                            r['base_title_raw'], r['commentary_acc_L']])

    # hand-adjudication sample of strict edges
    sample_n = 0
    if args.precision_sample and strict_dedup:
        rng = random.Random(args.seed)
        sample = rng.sample(strict_dedup, min(args.precision_sample, len(strict_dedup)))
        ctx_by_key = {}
        for e in ncc_e:
            ck = e['commentary']['iast'] if e.get('commentary') else (e.get('comm_raw') or '')
            ctx_by_key[(e['marker'], e.get('base_title_raw', ''), ck)] = e.get('ctx_title', '')
        with open(args.out + '.precision_sample.tsv', 'w', encoding='utf-8',
                  newline='') as f:
            w = csv.writer(f, delimiter='\t', lineterminator='\n')
            w.writerow(['commentary_title', 'base_title', 'base_title_raw',
                        'side', 'marker', 'context_title', 'HAND_VERDICT'])
            for r in sample:
                w.writerow([r['commentary_title'], r['base_title'], r['base_title_raw'],
                            r['side'], r['marker'],
                            ctx_by_key.get((r['marker'], r['base_title_raw'],
                                            r['commentary_title']), ''), ''])
        sample_n = len(sample)

    # canary: 2022 xls top-20 vs rebuild
    canary = []
    try:
        import xlrd
        sh = xlrd.open_workbook(args.xls).sheet_by_index(0)
        xls_rows = []
        for r in range(1, sh.nrows):
            name = str(sh.cell_value(r, 0)).strip()
            try:
                total = int(float(sh.cell_value(r, 1)))
            except (TypeError, ValueError):
                total = 0
            if name:
                xls_rows.append((name, total))
        cluster_by_fold = defaultdict(set)
        for c, folds in title_fold_set.items():
            for fo in folds:
                cluster_by_fold[fo].add(c)
        for name, total in sorted(xls_rows, key=lambda x: -x[1])[:20]:
            cands = cluster_by_fold.get(fold(name), set())
            name_fold = fold(name)
            folds_all = {fo for c in cands for fo in title_fold_set[c]}
            # needles: the xls name fold itself, cluster folds containing it
            # or contained in it (synonym families), then the longest rest
            related = {fo for fo in folds_all if len(fo) >= 8 and
                       (name_fold in fo or fo in name_fold)}
            rest = {fo for fo in folds_all if len(fo) >= 8} - related
            needles = list(related) + sorted(rest, key=len, reverse=True)[:5]
            mentions = 0
            if needles:
                for bf in body_folds:
                    if any(n in bf for n in needles):
                        mentions += 1
            best = max(cands, key=lambda c: profiles['strict'].get(c, (0, Counter()))[0],
                       default=None)
            canary.append(dict(
                xls_name=name, xls_total=total,
                rebuilt_strict=max((profiles['strict'].get(c, (0, Counter()))[0]
                                    for c in cands), default=0),
                rebuilt_fuzzy=max((profiles['fuzzy'].get(c, (0, Counter()))[0]
                                   for c in cands), default=0),
                in_edges_strict=ncc_in.get(best, 0) if best else 0,
                in_edges_acc=acc_in.get(best, 0) if best else 0,
                mention_entries=mentions,
                matched=bool(cands)))
    except ImportError:
        canary = [dict(error='xlrd unavailable; canary skipped')]

    sets = load_coverage_sets(acc_records=acc_records or None)
    cut_table, cum = coverage_tables(ranked, sets)

    stats = dict(
        ncc_entries=len(entries),
        clusters=len(members),
        cluster_identity=cluster_stats,
        ncc_edge_instances=len(ncc_e),
        strict_edges_dedup=len(strict_dedup),
        strict_edges_acc=acc_only,
        fuzzy_edges_dedup=len(fuzzy_dedup),
        strict_nodes=len(graphs['strict']['nodes']),
        fuzzy_nodes=len(graphs['fuzzy']['nodes']),
        ranked_works=len(universe),
        precision_sample_size=sample_n,
        precision_sample_file=args.out + '.precision_sample.tsv',
        canary_top20=canary,
        coverage_cuts=cut_table,
        coverage_curve_every10={s: cum[s][::3] for s in cum},
    )
    with open(args.report, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: v for k, v in stats.items()
                      if k not in ('canary_top20', 'coverage_cuts',
                                   'coverage_curve_every10')},
                     ensure_ascii=False, indent=1), file=sys.stderr)
    print('coverage cuts:', json.dumps(cut_table), file=sys.stderr)
    print('canary:', json.dumps(canary, ensure_ascii=False)[:2000], file=sys.stderr)
    print('OK ->', args.out, file=sys.stderr)


if __name__ == '__main__':
    main()
