"""NCC commentary graph library (H7202) -- work clusters, primary forest,
PageRank, tree profiles, coverage sets.  Split out of the single-file build
script for the token-size gate (estate tool, Uprava PR #5383).
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from ncc_commentary_extract import (ACC_TXT, CAP, CROSSWALK, DCS_JSON, PD_TSV,
                                    PWG_BIB, PWG_LS, clean_body, fold, su)

ENTRIES_BY_ID = {}


def set_entries(entries):
    """Install the entry lookup table (in place, so imported references
    stay valid) and clear the catalogue-order cache."""
    ENTRIES_BY_ID.clear()
    ENTRIES_BY_ID.update({r['ncc_id']: r for r in entries})
    _order_cache.clear()

# ---------------------------------------------------------------- identity
class DSU:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


SEE_ONLY_RE = re.compile(r'^(?:See|V\.|Vide|Vid\.|=)\s+([' + CAP + r'][^.;<]{2,80})', re.U)


def build_clusters(entries, index, crosswalk_path):
    dsu = DSU()
    for r in entries:
        dsu.find(r['ncc_id'])
    by_key = defaultdict(list)
    for r in entries:
        if r['match_key']:
            by_key[r['match_key']].append(r['ncc_id'])
    for ids in by_key.values():
        for i in ids[1:]:
            dsu.union(ids[0], i)
    see_pairs = 0
    alias_folds = defaultdict(set)
    for r in entries:
        clean = clean_body(r['body_html'])
        if len(clean) <= 120:
            m = SEE_ONLY_RE.match(clean)
            if m:
                tgt = index.resolve(m.group(1))
                if tgt is not None and tgt['ncc_id'] != r['ncc_id']:
                    dsu.union(r['ncc_id'], tgt['ncc_id'])
                    see_pairs += 1
        # leading alias chain: "or <alt> or <alt> ..." body start (NCC lists
        # variant titles this way; e.g. Amarakosa = namalinganusasana).
        # The folds feed title_fold_set / fold_map (alias-name targets still
        # resolve); NO union -- alias strings are homograph-unsafe ("or
        # trikANDa" for the lexicon once swallowed the unrelated vol-8
        # Trikanda work, dragging Amarakosa into a false commentary chain).
        if clean.startswith('or '):
            m = re.match(r'^or\s+([^.]{3,200})', clean)
            if m:
                for a in re.split(r'\s+or\s+', m.group(1))[:3]:
                    a = a.strip().rstrip('.')
                    if len(a) >= 3:
                        alias_folds[r['ncc_id']].add(fold(a))
    L_to_ids = defaultdict(list)
    with open(crosswalk_path, encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            # tiers A/B confirmed (grill 22-10); C/D parked
            if row.get('match_tier') in ('A', 'B') and row.get('ncc_id'):
                L_to_ids[row['acc_L']].append(row['ncc_id'])
    cw_union = 0
    for ids in L_to_ids.values():
        for i in ids[1:]:
            dsu.union(ids[0], i)
            cw_union += 1
    return dsu, dict(see_pairs=see_pairs, cw_union=cw_union), dict(L_to_ids), alias_folds


# ---------------------------------------------------------------- graph
def order_key(entries_by_id, nid):
    r = entries_by_id.get(nid)
    if r is None:                       # synthetic acc:<L> node
        return (10**12, nid)
    try:
        num = int(r['ncc_numid'])
    except (TypeError, ValueError):
        num = 10**12
    return (num, r['ncc_id'])


def build_graph(edge_rows):
    nodes, all_edges, seen = set(), [], set()
    for e in edge_rows:
        c, b = e['commentary_cluster'], e['base_cluster']
        if not c or not b or c == b:
            continue
        nodes.add(c)
        nodes.add(b)
        if (c, b) not in seen:
            seen.add((c, b))
            all_edges.append((c, b, e.get('provenance', 'ncc')))
    # primary forest: Kruskal-style union-find in catalogue order keeps a
    # spanning forest of the (possibly cyclic) relation digraph
    dsu2 = DSU()
    forest = []
    for c, b, prov in sorted(all_edges, key=lambda x: (order_key_by_id(x[0]), order_key_by_id(x[1]))):
        if dsu2.find(c) != dsu2.find(b):
            dsu2.union(c, b)
            forest.append((c, b, prov))
    # topo order over the forest: bases (upstream) before their commentaries,
    # i.e. indegree on the commentary side of each forest edge c -> b
    indeg = defaultdict(int)
    dependents = defaultdict(list)
    nodes_f = set()
    for c, b, _ in forest:
        indeg[c] += 1
        dependents[b].append(c)
        nodes_f.add(c)
        nodes_f.add(b)
    stack = sorted((n for n in nodes_f if indeg[n] == 0), key=order_key_by_id)
    topo, deg = [], dict(indeg)
    while stack:
        n = stack.pop(0)
        topo.append(n)
        for d in dependents.get(n, ()):
            deg[d] -= 1
            if deg[d] == 0:
                stack.append(d)
    primary, depth = {}, {}
    bases_of = defaultdict(list)
    for c, b, _ in forest:
        bases_of[c].append(b)
    for n in topo:
        bases = bases_of.get(n, [])
        if not bases:
            primary[n], depth[n] = None, 0
        else:
            # shallowest base wins: a direct commentary of a root stays at its
            # l1 even when it also glosses a deeper sub-commentary (2022-tree
            # semantics); catalogue order breaks ties
            primary[n] = min(bases, key=lambda b: (depth.get(b, 0),
                                                   order_key_by_id(b)))
            depth[n] = depth[primary[n]] + 1
    children = defaultdict(list)
    for n, p in primary.items():
        if p:
            children[p].append(n)
    return dict(nodes=nodes, all_edges=all_edges, forest=forest, topo=topo,
                primary=primary, depth=depth, children=children)


_order_cache = {}


def order_key_by_id(nid):
    if nid not in _order_cache:
        _order_cache[nid] = order_key(ENTRIES_BY_ID, nid)
    return _order_cache[nid]


def pagerank(nodes, edges, d=0.85, iters=200, tol=1e-12):
    idx = {n: i for i, n in enumerate(sorted(nodes))}
    n = len(idx)
    if n == 0:
        return {}
    out = [[] for _ in range(n)]
    for c, b, _ in edges:
        out[idx[c]].append(idx[b])
    r = [1.0 / n] * n
    for _ in range(iters):
        dangling = sum(r[i] for i in range(n) if not out[i])
        base = (1 - d) / n + d * dangling / n
        new = [base] * n
        for i in range(n):
            if out[i]:
                share = d * r[i] / len(out[i])
                for j in out[i]:
                    new[j] += share
        delta = sum(abs(a - b) for a, b in zip(r, new))
        r = new
        if delta < tol * n:
            break
    return {nod: r[idx[nod]] for nod in nodes}


def tree_profile(graph):
    """(subtree size, {level: count}) per node over the primary forest;
    level = depth below the root of the work's own tree (l7 = >=7)."""
    children, depth, topo = graph['children'], graph['depth'], graph['topo']
    memo = {}
    for n in reversed(topo):
        size, levels = 0, Counter()
        base_d = depth[n]
        for ch in children.get(n, ()):
            cs, cl = memo[ch]
            size += cs + 1
            # levels are RELATIVE to the node (the 2022 tree's l1 = direct
            # commentaries), not absolute forest depth; a child's own relative
            # levels shift +1 when seen from the parent
            levels[depth[ch] - base_d] += 1
            levels.update({k + 1: v for k, v in cl.items()})
        memo[n] = (size, levels)
    return memo


# ---------------------------------------------------------------- coverage
def load_coverage_sets(acc_records=None):
    sets = {}
    with open(DCS_JSON, encoding='utf-8') as f:
        sets['dcs288'] = {fold(t['name']) for t in json.load(f)}
    pd_titles = set()
    with open(PD_TSV, encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            if row.get('class') == 'primary' and row.get('display_title'):
                pd_titles.add(fold(row['display_title']))
    sets['pd164'] = pd_titles
    pwg = set()
    with open(PWG_LS, encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 3 or not parts[1]:
                continue
            lead = re.split(r'[,(]|\s+ed\b|\s+nach\b', parts[2])[0].strip()
            lead = re.sub(r"[.'’ʻ]", '', lead)
            if 3 <= len(lead) <= 60 and lead.upper() == lead:
                fo = fold(lead)
                if len(fo) >= 4:
                    pwg.add(fo)
    with open(PWG_BIB, encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 4 or ' = ' not in parts[3]:
                continue
            lead = parts[3].split(' = ', 1)[1]
            lead = re.split(r'\s+in\s+|\s+nach\s+|\s+Handschrift|Hdschr|\(', lead)[0].strip()
            lead = re.sub(r"[.'’ʻ]", '', lead)
            fo = fold(lead)
            if len(fo) >= 4:
                pwg.add(fo)
    sets['pwg'] = pwg
    acc_keys = set()
    if acc_records:
        for r in acc_records:
            if r['key']:
                acc_keys.add(r['key'])
    else:
        with open(ACC_TXT, encoding='utf-8') as f:
            txt = f.read()
        for k1 in re.findall(r'<k1>([^<]*)', txt):
            k = su.slp1_simplify(k1)
            if k:
                acc_keys.add(k)
    with open(CROSSWALK, encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            if row.get('acc_match_key'):
                acc_keys.add(row['acc_match_key'])
    sets['acc'] = acc_keys
    return sets


def coverage_tables(ranked, sets):
    cuts = [50, 100, 250, 500, 1000]
    order = ranked['order']
    title_folds = ranked['title_fold_set']
    acc_flag = ranked['acc_flag']
    cum = {s: [] for s in sets}
    for n in range(10, min(1000, len(order)) + 1, 10):
        row = {'n': n}
        for s in sets:
            top = order[:n]
            if s == 'acc':
                hit = sum(1 for w in top if acc_flag.get(w) or
                          (title_folds.get(w) and title_folds[w] & sets['acc']))
            else:
                hit = sum(1 for w in top if title_folds.get(w) and title_folds[w] & sets[s])
            row[s] = round(100 * hit / n, 1)
        for s in sets:
            cum[s].append((n, row[s]))
    cut_table = {s: [(n, v) for n, v in cum[s] if n in cuts] for s in sets}
    return cut_table, cum

