"""NCC name-authority adjudication of the fuzzy t:<fold> nodes (H7215).

Implements the C3 §4 name-authority-table method (paper
Uprava/papers/A68/sweeps/2026-10-14-C3-acc-ncc-correlation.md §4: bare school
filings, -ya/-īya title variants, Sanskritised BHS titles,
work-under-author-name) over the 13,890 synthetic fuzzy title nodes of the
H7202 commentary graph.  Every node gets a verdict; every MERGE carries an
evidence string.  Guard (handoff H7215): no merge without body-text or
crosswalk evidence.

Evidence classes, in ladder order (first hit wins):

  annotated-title  the raw target string is a real title + annotation junk
                   the H7202 extractor's STOP_CUT missed (". See ZDMG",
                   ". BP. p", ". MT"); the title core exactly equals ONE
                   cluster fold.  Evidence: the source body's own marker text.
  body-alias       the candidate cluster's own entry body declares the raw
                   string as an alias (or/also/alias/see/cf./named/v./=),
                   uniquely across the catalogue.
  crosswalk        a works_crosswalk row into the candidate cluster carries
                   the ACC key fold equal to the t-fold.
  suffix-variant   t-fold + (-ya/-īya) or t-fold minus them equals ONE cluster
                   fold AND body-alias or crosswalk evidence holds (C3's
                   vikramorvasi -> vikramorvasiya class); structural
                   uniqueness alone never merges (guard).
  spelling-variant edit distance <= 1 (sandhi a.h~as, consonant doubling,
                   single-vowel) to ONE cluster fold, length >= 8, AND
                   body-alias or crosswalk evidence.

Everything else is rejected with a named class: artifact-short,
artifact-roman, artifact-series (library sigla / page / volume noise),
generic-title (bare genre word: tika/bhasya/vrtti/... the "C. <genre word>"
list-side usage), ambiguous (>=2 structural candidates -- the homograph
trap, H7202's rival-claimant rule), variant-no-evidence (structural
candidate exists, evidence gate failed -- auditable, revisitable),
no-candidate.

Seeds (handoff): H7202's FOLD_ALIASES is carried as the first table row
(source=seed:h7202-fold-alias, verdict MERGE -- the build keeps resolving it
via FOLD_ALIASES; the row records it in the authority table).  The TRUE:weak
precision-sample bin and the C3 §2 42-miss bin calibrate the class
vocabulary (documented in the H7215 sweep paper); they are strict-edge /
ACC-surface rows respectively, not t-nodes, so they have no table rows.

Usage:
    python3 ncc_name_authority.py            # writes the TSV + a summary
Inputs default to the estate checkout like build_ncc_commentary_graph.py
(ESTATE_ROOT env overrides).  Deterministic: same inputs -> byte-identical
TSV (no RNG, sorted iteration everywhere).
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from ncc_commentary_extract import (CROSSWALK, NCC_JSONL, TitleIndex, clean_body,
                                    fold, load_ncc, match_key_of)
from ncc_commentary_graph import (ENTRIES_BY_ID, build_clusters, order_key,
                                  set_entries)

HERE = os.path.dirname(os.path.abspath(__file__))
EDGES_TSV = os.path.join(HERE, 'ncc_commentary_edges.tsv')
OUT_TSV = os.path.join(HERE, 'ncc_name_authority_adjudication.tsv')
OUT_SUMMARY = os.path.join(HERE, 'ncc_name_authority_summary.json')

from ncc_name_authority_lib import (GENRE_FOLDS, ROMAN_RE, SEED_FOLDS,
                                    SEED_ROWS, annot_token_ok,
                                    del1_variants, fold_regex)




def main():
    print('loading NCC …', file=sys.stderr)
    entries = load_ncc(NCC_JSONL)
    set_entries(entries)
    index = TitleIndex(entries)
    dsu, cluster_stats, L_map, alias_folds = build_clusters(entries, index, CROSSWALK)

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

    # cluster fold universe: member title folds + leading-or alias folds
    cluster_folds = defaultdict(set)
    member_title_folds = defaultdict(set)   # member iast folds only
    cluster_rep = {}
    for c, ms in members.items():
        ms_sorted = sorted(ms, key=lambda r: order_key(ENTRIES_BY_ID, r['ncc_id']))
        cluster_rep[c] = ms_sorted[0]
        for m in ms:
            if m['iast']:
                cluster_folds[c].add(fold(m['iast']))
                member_title_folds[c].add(fold(m['iast']))
    for nid, folds in alias_folds.items():
        cluster_folds[cf(nid)] |= folds

    fold2clusters = defaultdict(set)
    fold_bucket = defaultdict(set)   # first-4 bucket: prefix relations
    for c, fs in cluster_folds.items():   # require a shared first-4
        for fo in fs:
            if len(fo) >= 4:
                fold2clusters[fo].add(c)
                fold_bucket[fo[:4]].add(fo)

    # edit-distance<=1 index (deletion-signature intersection)
    d1_index = defaultdict(set)
    for fo, cs in fold2clusters.items():
        for sig in del1_variants(fo):
            d1_index[sig] |= cs

    # crosswalk: cluster -> ACC key folds that map into it
    xw_acc_folds = defaultdict(set)
    xw_rows = defaultdict(list)
    with open(CROSSWALK, encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            nid = row.get('ncc_id')
            if nid in ENTRIES_BY_ID:
                c = cf(nid)
                ak = fold(row.get('acc_match_key', ''))
                if ak:
                    xw_acc_folds[c].add(ak)
                xw_rows[c].append(row)

    # t: nodes from the shipped fuzzy edge table
    tn = Counter()
    as_base = Counter()
    as_comm = Counter()
    raws = defaultdict(Counter)
    with open(EDGES_TSV, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            for idc, tc, ctr in (('commentary_id', 'commentary_title', as_comm),
                                 ('base_id', 'base_title', as_base)):
                if r[idc].startswith('t:'):
                    tn[r[idc]] += 1
                    raws[r[idc]][r[tc]] += 1

    # candidate cluster bodies (cleaned + folded) computed lazily per cluster
    body_fold_cache = {}
    def cluster_body_folds(c):
        if c not in body_fold_cache:
            fs = []
            for m in members.get(c, []):
                fs.append(fold(clean_body(m['body_html'])))
            body_fold_cache[c] = fs
        return body_fold_cache[c]

    def body_alias_clusters(core):
        """Clusters whose OWN body declares `core` as an alias near
        or/also/alias/see/cf./v./named/called (never the 'on' marker
        context).  Candidate set bounded by the fold2clusters owners of the
        core."""
        rx = fold_regex(core)
        hits = []
        for c in fold2clusters.get(core, set()):
            for m in members.get(c, []):
                body = clean_body(m['body_html'])
                for mo in rx.finditer(body):
                    left = body[max(0, mo.start() - 30):mo.start()].lower()
                    if re.search(r'(?:or|also|alias|see|cf\.|v\.|named|called)\s*(?:the\s+)?$', left) \
                       or re.search(r'=$', left.strip()):
                        hits.append(c)
                        break
                if hits and hits[-1] == c:
                    break
        return sorted(set(hits))

    def crosswalk_evidence(tfo, cluster):
        for ak in sorted(xw_acc_folds.get(cluster, ())):
            if ak == tfo or (len(ak) >= 8 and tfo in ak) or (len(tfo) >= 8 and ak in tfo):
                return ('crosswalk acc_key_fold=%s into %s'
                        % (ak, cluster_rep[cluster]['iast']))
        return None

    out_rows = []
    for seed in SEED_ROWS:
        out_rows.append(seed)

    stats = Counter()
    nodes = sorted(tn)
    for node in nodes:
        fo = node[2:]
        n = tn[node]
        raw_sample = raws[node].most_common(1)[0][0]
        base_n, comm_n = as_base[node], as_comm[node]
        row = dict(fold=fo, edge_n=n, as_base_n=base_n, as_comm_n=comm_n,
                   raw_sample=raw_sample, verdict='', klass='',
                   merge_cluster='', merge_title='', evidence='',
                   source='h7215-ladder')

        def finish(verdict, klass, cluster=None, evidence=''):
            row['verdict'] = verdict
            row['klass'] = klass
            if cluster is not None:
                row['merge_cluster'] = cluster
                row['merge_title'] = cluster_rep[cluster]['iast']
            row['evidence'] = evidence
            out_rows.append(row)
            stats[verdict + ':' + klass] += 1

        if len(fo) < 4:
            finish('REJECT', 'artifact-short')
            continue
        if ROMAN_RE.match(fo):
            finish('REJECT', 'artifact-roman')
            continue
        if fo in GENRE_FOLDS:
            finish('REJECT', 'generic-title')
            continue
        if fo in SEED_FOLDS:
            # the H7202 FOLD_ALIASES row already owns this fold; a body-alias
            # challenger is the rival claimant shape H7202 adjudicated
            finish('REJECT', 'rival-claimant',
                   evidence='H7202 committed %r elsewhere; this cluster '
                            'self-declares the string (the adjudicated rival)'
                            % SEED_FOLDS[fo])
            continue

        # --- annotated-title: the raw target is a real title + annotation
        # junk the H7202 STOP_CUT missed (". See ZDMG", ". MT", " I").
        # Cut at RAW token boundaries only (never inside a word), require the
        # core fold to name exactly one cluster, every tail token to look
        # like annotation (series siglum, page/volume, see/ibid, numeral).
        tokens = [t for t in re.split(r'\s+', raw_sample) if t]
        ann_hit = None
        for cut in range(len(tokens) - 1, 0, -1):
            core_fold = fold(' '.join(tokens[:cut]))
            if len(core_fold) < 6:
                continue   # core floor = the fold_map resolution floor
            tail = tokens[cut:]
            cs = fold2clusters.get(core_fold)
            if not cs or len(cs) != 1:
                continue
            if all(annot_token_ok(t) for t in tail):
                ann_hit = (core_fold, ' '.join(tail), next(iter(cs)))
                break
        if ann_hit is not None:
            core, rest, c = ann_hit
            if core in GENRE_FOLDS:
                finish('REJECT', 'generic-title',
                       evidence='core %r is a genre word' % core)
                continue
            finish('MERGE', 'annotated-title', c,
                   'raw %r = title core %r (fold %s, unique cluster) + '
                   'annotation tail %r; source-body marker text'
                   % (raw_sample, cluster_rep[c]['iast'], core, rest))
            continue

        # --- exact fold: owned by one or more clusters but unresolved by the
        # build (fold_map ambiguity or fold/key skew).  Title ownership beats
        # alias claims: a cluster whose OWN member title carries the fold IS
        # the named work; alias-declaring rivals (the H7202 stuti trap) only
        # win when no title-owner exists, and then only on unique body or
        # crosswalk evidence.
        exact_cs = fold2clusters.get(fo, set())
        if exact_cs:
            title_owners = [c for c in exact_cs if fo in member_title_folds[c]]
            if len(title_owners) == 1:
                c = title_owners[0]
                finish('MERGE', 'title-owner', c,
                       'raw %r names the work exactly; fold owned as member '
                       'title by exactly one cluster (%s)'
                       % (raw_sample, cluster_rep[c]['iast']))
            elif len(title_owners) > 1:
                finish('REJECT', 'ambiguous',
                       evidence='title owners: %s'
                       % ', '.join(sorted(cluster_rep[c]['iast']
                                          for c in title_owners)[:4]))
            else:
                # truncated short forms (asval, apast, para) never merge on a
                # self-declaration alone -- too little string
                ba = body_alias_clusters(fo) if len(fo) >= 8 else []
                if len(ba) == 1:
                    c = ba[0]
                    finish('MERGE', 'body-alias', c,
                           'body of %s declares %r as alias'
                           % (cluster_rep[c]['iast'], raw_sample))
                else:
                    finish('REJECT', 'ambiguous' if len(ba) > 1 else 'no-evidence',
                           evidence='fold owned only via alias chains; %s'
                           % ('ambiguous body-alias' if len(ba) > 1
                              else 'no body-alias/crosswalk evidence'))
            continue

        # --- suffix variants (-ya/-īya, Latin plural -s), C3 class
        suf_cands = set()
        for cand in (fo + 'ya', fo + 'iya'):
            suf_cands |= fold2clusters.get(cand, set())
        if fo.endswith('ya'):
            suf_cands |= fold2clusters.get(fo[:-2], set())
        if fo.endswith('iya'):
            suf_cands |= fold2clusters.get(fo[:-3], set())
        if fo.endswith('s') and len(fo) >= 7:
            suf_cands |= fold2clusters.get(fo[:-1], set())
        if len(suf_cands) == 1:
            c = next(iter(suf_cands))
            ba = body_alias_clusters(fo)
            xw = crosswalk_evidence(fo, c)
            if ba == [c] or (xw and not ba):
                finish('MERGE', 'suffix-variant', c,
                       ('body-alias in %s' % cluster_rep[c]['iast']) if ba == [c]
                       else xw)
            else:
                finish('REJECT', 'variant-no-evidence',
                       evidence='suffix candidate %s lacks body-alias/crosswalk'
                       % cluster_rep[c]['iast'])
            continue
        if len(suf_cands) > 1:
            finish('REJECT', 'ambiguous',
                   evidence='suffix candidates: %s'
                   % ', '.join(sorted(cluster_rep[c]['iast'] for c in suf_cands)[:4]))
            continue

        # --- edit distance <= 1 spelling variant (BHS sandhi/doubling class)
        d1_hits = set()
        for sig in del1_variants(fo) | {fo}:
            d1_hits |= d1_index.get(sig, set())
        d1_hits -= exact_cs   # exact handled above
        d1_hits = {c for c in d1_hits
                   if any(abs(len(x) - len(fo)) <= 1 and x != fo
                          for x in cluster_folds[c])}
        if len(d1_hits) == 1 and len(fo) >= 8:
            c = next(iter(d1_hits))
            near = min(cluster_folds[c], key=lambda x: abs(len(x) - len(fo)))
            ba = body_alias_clusters(fo)
            xw = crosswalk_evidence(fo, c)
            if ba == [c] or (xw and not ba):
                finish('MERGE', 'spelling-variant', c,
                       ('fold %s ~ %s (d<=1); body-alias in %s'
                        % (fo, near, cluster_rep[c]['iast'])) if ba == [c]
                       else 'fold %s ~ %s (d<=1); %s' % (fo, near, xw))
            else:
                finish('REJECT', 'variant-no-evidence',
                       evidence='d<=1 candidate %s (%s~%s) lacks '
                                'body-alias/crosswalk'
                                % (cluster_rep[c]['iast'], fo, near))
            continue
        if len(d1_hits) > 1:
            finish('REJECT', 'ambiguous',
                   evidence='d<=1 candidates: %s'
                   % ', '.join(sorted(cluster_rep[c]['iast'] for c in d1_hits)[:4]))
            continue

        # --- structural candidate exists but ambiguity/evidence failed;
        # otherwise no candidate at all
        pref = {c for f2 in fold_bucket.get(fo[:4], ())
                if (f2.startswith(fo) or fo.startswith(f2))
                and abs(len(f2) - len(fo)) <= 8
                for c in fold2clusters[f2]}
        if pref:
            finish('REJECT', 'ambiguous' if len(pref) > 1 else 'no-evidence',
                   evidence='structural: %s'
                   % ', '.join(sorted(cluster_rep[c]['iast'] for c in list(pref)[:4])))
        else:
            finish('REJECT', 'no-candidate')

    with open(OUT_TSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['fold', 'edge_n', 'as_base_n', 'as_comm_n', 'raw_sample',
                    'verdict', 'class', 'merge_cluster', 'merge_title',
                    'evidence', 'source'])
        for r in out_rows:
            w.writerow([r['fold'], r['edge_n'], r['as_base_n'], r['as_comm_n'],
                        r['raw_sample'], r['verdict'], r['klass'],
                        r['merge_cluster'], r['merge_title'], r['evidence'],
                        r['source']])

    merged = [r for r in out_rows if r['verdict'] == 'MERGE' and r['source'] == 'h7215-ladder']
    summary = dict(
        t_nodes_total=len(nodes),
        t_edges_total=sum(tn.values()),
        rows_written=len(out_rows),
        verdicts=dict(stats),
        merges=len(merged),
        merge_edge_weight=sum(r['edge_n'] for r in merged),
        merge_by_class=dict(Counter(r['klass'] for r in merged)),
        top_merges=sorted(([r['edge_n'], r['fold'], r['merge_title'], r['klass']]
                           for r in merged), reverse=True)[:20],
    )
    with open(OUT_SUMMARY, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
