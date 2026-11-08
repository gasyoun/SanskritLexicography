"""H7222 pass 2 of the NCC name-authority table (split for the token gate).

Two additions to the H7215 adjudicator, both structural (no hand-listed
names, no external evidence required):

  author-vs-work filter   a structural candidate cluster (`-ya`/`-iya`/plural
                          suffix or d<=1 spelling) that failed the body-alias
                          and crosswalk gates is accepted only when the
                          candidate cluster is a WORK filing.  A cluster is a
                          PERSON filing when
                            head-role      the first prose paragraph opens
                                           with a kinship/role predicate
                                           (son/father/mother/grandson/
                                           disciple/pupil/preceptor/teacher/
                                           alias/king/... of) and not with a
                                           genre siglum or work formula
                                           ("med.", "jy.", "or", "name of",
                                           "by", "ascribed", "cited", "see",
                                           ...); or
                            bare-work-list no member has a head paragraph and
                                           every subentry is a bare work title
                                           (the person's bibliography, e.g.
                                           "--Kṛṣṇaguṇāmṛta.") or a
                                           "C. <title> on <base>" (their own
                                           commentary).  Inclusion and
                                           attribution subentries ("included
                                           in", "from ...", "by ...") mark a
                                           work filing instead.
                          Everything else is a work filing (the NCC default).
                          The deciding head/subentry is quoted in the TSV
                          evidence column, so each verdict is auditable from
                          the table alone.

  class-bound recheck     the H7202/H7215 d<=1 index intersects single-
                          deletion signatures, which is symmetric: one
                          deletion on each side also collides, so the index
                          admits distance <= 2 while the class is published
                          as d<=1 and filter-pass carries no body evidence.
                          Every unevidenced d<=1 candidate is re-checked with
                          Damerau-Levenshtein <= 1 (adjacent transposition
                          allowed) before the identity is accepted.

The table is cumulative: rows whose t:<fold> nodes the table itself resolved
out of the edge population are carried forward unchanged, so a re-run against
post-authority edges does not drop every MERGE row.
"""
import csv
import json
import os
import re
from collections import Counter

_PARA_RE = re.compile(r'<p>.*?</p>', re.S)
_TAG_RE = re.compile(r'<[^>]+>')
# a head that OPENS with a kinship/role predicate (<=3 leading words, so
# "chief teacher of ..." and "Icchārāma son of ..." both fire)
_ROLE_RE = re.compile(
    r'^(?:[^\s]+\s+){0,3}?(?:(?:son|father|mother|brother|sister|grandson|'
    r'granddaughter|grandfather|grandmother|disciple|pupil|preceptor|'
    r'teacher|successor|king|queen|minister|patron|wife|husband|uncle|'
    r'nephew|descendant|ancestor|student|chief|poet)(?:\s+of\b|\b)'
    r'|\balias\b)', re.I)
# a head that OPENS as a work description instead (genre siglum or the prose
# formulas NCC uses to introduce a text/attribution)
_WORK_START_RE = re.compile(
    r'^(?:med\.|jy\.|dh\.|ny\.|gr\.|sr\.|śr\.|vedānta|mīm\.|alaṃk\.|alaṁk\.|'
    r'tantra|jain|bud\.|pāli|pkt\.|sāh\.|kāvya|nāṭaka|stotra|saṃgīta|śilpa|'
    r'gaṇita|or\b|name of|by\b|ascribed|attributed|cited|quoted|see\b|the\b|'
    r'in\b|based|extracted|another|wrongly|probably|diff\.|unidentified|'
    r'consists|refers)', re.I)
# subentry = a person's own commentary on another base ("C. <title> on <base>")
_SUB_OWN_COMMENTARY_RE = re.compile(r'^C\.\s+\S.*\s+on\s+\S', re.I)
# subentry = inclusion / attribution note, i.e. the cluster is a WORK
_SUB_WORK_RE = re.compile(
    r'\b(?:by|from|included|extracted|name of|based on|ascribed|attributed|'
    r'cited|quoted|cf\.|another name|commentary on)\b', re.I)
# trailing reference furniture: "See ...", "[Page...", "Cf. ..."
_SUB_REF_RE = re.compile(r'\s+(?:See\b|\[Page\b|Cf\.\s)')

HEADER = ['fold', 'edge_n', 'as_base_n', 'as_comm_n', 'raw_sample',
          'verdict', 'class', 'merge_cluster', 'merge_title', 'evidence',
          'source']


def _paras(body):
    out = []
    for mo in _PARA_RE.finditer(body or ''):
        t = _TAG_RE.sub('', mo.group(0)).strip()
        if t:
            out.append(t)
    return out


def person_filing(ms):
    """Author-vs-work filter over one candidate cluster's entries.

    Returns (kind, clause, quote) with kind in {'person', 'work', 'unknown'}.
    """
    heads, subs = [], []
    for m in ms:
        ps = _paras(m['body_html'])
        first = ps[0] if ps else ''
        if first.startswith(('-', '–')):
            subs.extend(p for p in ps if p.startswith(('-', '–')))
        else:
            heads.append(first)
    for h in heads:
        if _ROLE_RE.match(h) and not _WORK_START_RE.match(h):
            return 'person', 'head-role', h[:70]
    if heads:
        return 'work', 'head-work', heads[0][:70]
    if not subs:
        return 'unknown', 'empty-entry', ''
    for p in subs:
        t = _SUB_REF_RE.split(p.lstrip('-–— ').strip(), 1)[0].strip()
        if _SUB_OWN_COMMENTARY_RE.match(t):
            continue
        if _SUB_WORK_RE.search(t) or len(t.split()) > 8:
            return 'work', 'empty-head-subentry', p[:70]
    return 'person', 'bare-work-list', subs[0][:70]


def dl1(a, b):
    """True when Damerau-Levenshtein(a, b) <= 1 (one edit or adjacent swap)."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        if len(diff) == 1:
            return True
        return (len(diff) == 2 and diff[1] == diff[0] + 1
                and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]])
    short, long_ = (a, b) if len(a) < len(b) else (b, a)
    i = 0
    while i < len(short) and short[i] == long_[i]:
        i += 1
    return short[i:] == long_[i + 1:]


def filter_decision(ms, fo, stage_ev, d1_stage, cluster_folds):
    """(verdict, class, evidence) for an unevidenced structural candidate.

    `cluster_folds` is the candidate cluster's fold set (for the d<=1 class
    bound); `fo` is the t-node fold (also the 8-char floor operand).
    """
    kind, clause, quote = person_filing(ms)
    if kind == 'person':
        return ('REJECT', 'person-filing',
                '%s; author-filter: person filing (%s: %r)'
                % (stage_ev, clause, quote))
    if d1_stage and not any(dl1(fo, x) for x in cluster_folds):
        return ('REJECT', 'variant-no-evidence',
                '%s; author-filter: work filing (%s: %r), but the pair is '
                'outside the d<=1 class (signature coincidence, distance > 1)'
                % (stage_ev, clause, quote))
    if kind == 'work' and len(fo) >= 8:
        return ('MERGE', 'filter-pass',
                '%s; author-filter: work filing (%s: %r)'
                % (stage_ev, clause, quote))
    return ('REJECT', 'variant-no-evidence',
            '%s; author-filter: %s (fold %d < 8 chars)'
            % (stage_ev, 'work filing' if kind == 'work' else 'undecided',
               len(fo)))


def carry_forward(path, out_rows, stats):
    """Cumulative table: keep rows whose t-node the table already resolved."""
    if not os.path.exists(path):
        return 0
    carried = 0
    with open(path, encoding='utf-8') as f:
        prev = list(csv.DictReader(f, delimiter='\t'))
    have = {r['fold'] for r in out_rows}
    for r in sorted(prev, key=lambda x: x['fold']):
        if r['fold'] in have:
            continue
        out_rows.append(dict(
            fold=r['fold'], edge_n=int(r['edge_n']),
            as_base_n=int(r['as_base_n']), as_comm_n=int(r['as_comm_n']),
            raw_sample=r['raw_sample'], verdict=r['verdict'],
            klass=r['class'], merge_cluster=r['merge_cluster'],
            merge_title=r['merge_title'], evidence=r['evidence'],
            source=r['source']))
        stats[r['verdict'] + ':' + r['class']] += 1
        carried += 1
        have.add(r['fold'])
    return carried


def _write(path, rows):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(HEADER)
        for r in rows:
            w.writerow([r['fold'], r['edge_n'], r['as_base_n'], r['as_comm_n'],
                        r['raw_sample'], r['verdict'], r['klass'],
                        r['merge_cluster'], r['merge_title'], r['evidence'],
                        r['source']])


def write_table(path, out_rows):
    _write(path, out_rows)


def write_summary(path, out_rows, stats, nodes, tn, carried):
    pass2_rows = sorted((r for r in out_rows if r['source'] == 'h7222-pass2'),
                        key=lambda r: r['fold'])
    merged = [r for r in out_rows if r['verdict'] == 'MERGE'
              and r['source'] != 'seed:h7202-fold-alias']
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
        carried_rows=carried,
        pass2=dict(rows=len(pass2_rows),
                   filter_pass=sum(1 for r in pass2_rows
                                   if r['klass'] == 'filter-pass'),
                   person_filing=sum(1 for r in pass2_rows
                                     if r['klass'] == 'person-filing'),
                   outside_d1=sum(1 for r in pass2_rows
                                  if 'outside the d<=1 class' in r['evidence']),
                   undecided=sum(1 for r in pass2_rows
                                 if r['klass'] == 'variant-no-evidence'
                                 and 'outside the d<=1 class'
                                 not in r['evidence'])),
    )
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return pass2_rows


def write_pass2(path, pass2_rows):
    _write(path, pass2_rows)
