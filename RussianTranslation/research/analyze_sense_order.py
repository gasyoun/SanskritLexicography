#!/usr/bin/env python
"""analyze_sense_order.py — quantify the sense-ordering claims of HANDOFF_sense_ordering.md.

Reuses the existing Renou infrastructure (src/renou.py + src/ls_source_map.json),
which already maps every <ls> source siglum to a Renou state (I-V) AND a numeric
`date`. Runs three analyses against csl-orig PWG source:

  #1  renou-vs-printed-order divergence  — for every multi-sense entry, compare
      PWG's printed <div> sense order against the order you'd get by sorting senses
      on their oldest citation date. Answers: "how much would a renou_oldest re-sort
      fight the source?"  (the pwg_ru build decision)

  #3  within-sense citation chronology   — for every sense with >=2 dated citations,
      test whether the citations are printed oldest->newest (Veda -> classical).
      Answers: "do the European dicts really thread citations chronologically
      *inside* a sense?"

  #2  probe-word scale  — same sense-1-is-oldest test restricted to a 40-word
      polysemous probe set, for a focused cross-check of the qualitative reads.

Output: a markdown report (research/sense_order_metrics.md) + raw JSON.

Usage:  python analyze_sense_order.py [path/to/pwg.txt]
"""
import json, os, re, sys, statistics

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'src')
sys.path.insert(0, SRC)
import renou  # noqa: E402

SMAP = renou.load_map('pwg')

DEFAULT_PWG = os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'pwg', 'pwg.txt')

# Top-level PWG sense marker: <div n="1"> optionally "— " then "N) ".
SENSE_RE = re.compile(r'<div n="1">\s*(?:[—-]\s*)?(\d+)\)')
LS_RE = re.compile(r'<ls\b[^>]*>(.*?)</ls>', re.S)

PROBE = [  # polysemous headwords (SLP1 k1) whose senses span Vedic->classical
    'arTa', 'Darma', 'guRa', 'rasa', 'kAla', 'pada', 'BAva', 'tantra', 'tattva',
    'karman', 'karaRa', 'vftti', 'mAtra', 'aMSa', 'aRu', 'akzara', 'aNga', 'gati',
    'grAma', 'dravya', 'liNga', 'varRa', 'vAc', 'vidyA', 'yoga', 'yajYa', 'kzetra',
    'mUrti', 'naya', 'nyAya', 'pakza', 'prakfti', 'rUpa', 'sAra', 'sADana', 'sUtra',
    'tejas', 'vaMSa', 'viDi', 'vyaya',
]


def entries(path):
    """Yield (k1, body) per <L>..<LEND> record."""
    buf, k1 = [], None
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            if line.startswith('<L>'):
                m = re.search(r'<k1>([^<]*)', line)
                k1 = m.group(1) if m else None
                buf = [line]
            elif line.startswith('<LEND>'):
                if k1 is not None:
                    yield k1, ''.join(buf)
                buf, k1 = [], None
            else:
                buf.append(line)


def split_senses(body):
    """Return [(sense_no, text), ...] for top-level numbered senses, or [] if the
    entry has no explicit numbered senses (monosemous / undivided)."""
    hits = list(SENSE_RE.finditer(body))
    if len(hits) < 2:
        return []
    out = []
    for i, m in enumerate(hits):
        start = m.start()
        end = hits[i + 1].start() if i + 1 < len(hits) else len(body)
        out.append((int(m.group(1)), body[start:end]))
    return out


def citation_dates(text):
    """Ordered list of citation dates (textual order) for recognised <ls> in text."""
    dates = []
    for m in LS_RE.finditer(text):
        for k in renou.keys_in_text(m.group(0), 'pwg'):
            rec = SMAP.get(k)
            if rec and rec.get('date') is not None:
                dates.append(rec['date'])
    return dates


def kendall_tau(seq):
    """Kendall tau of a sequence vs its sorted order; 1.0 = already ascending."""
    n = len(seq)
    if n < 2:
        return None
    conc = disc = 0
    for i in range(n):
        for j in range(i + 1, n):
            if seq[i] < seq[j]:
                conc += 1
            elif seq[i] > seq[j]:
                disc += 1
    tot = conc + disc
    return (conc - disc) / tot if tot else None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PWG
    path = os.path.abspath(path)

    # ---- accumulators ----
    a1 = {'entries_multisense': 0, 'entries_>=2_dated': 0, 'sense1_is_oldest': 0,
          'taus': [], 'sense1_rank_when_resorted': []}
    a3 = {'senses_>=2_dated': 0, 'monotone': 0, 'weak_taus': [],
          'adj_pairs': 0, 'adj_nondec': 0}
    probe_rows = []
    probe_set = set(PROBE)

    for k1, body in entries(path):
        senses = split_senses(body)
        if not senses:
            continue
        a1['entries_multisense'] += 1

        dated = []  # (sense_no, oldest_date, position_index)
        for pos, (no, text) in enumerate(senses):
            ds = citation_dates(text)
            # analysis #3: within-sense chronology
            if len(ds) >= 2:
                a3['senses_>=2_dated'] += 1
                t = kendall_tau(ds)
                if t is not None:
                    a3['weak_taus'].append(t)
                    if t == 1.0:
                        a3['monotone'] += 1
                for x, y in zip(ds, ds[1:]):
                    a3['adj_pairs'] += 1
                    if x <= y:
                        a3['adj_nondec'] += 1
            if ds:
                dated.append((pos, min(ds)))

        # analysis #1: cross-sense ordering
        if len(dated) >= 2:
            a1['entries_>=2_dated'] += 1
            positions = [p for p, _ in dated]
            oldest_dates = [d for _, d in dated]
            # is the first printed dated-sense the globally oldest?
            if oldest_dates[0] == min(oldest_dates):
                a1['sense1_is_oldest'] += 1
            t = kendall_tau(oldest_dates)
            if t is not None:
                a1['taus'].append(t)
            # where would printed-sense-1 land if re-sorted by date? (rank, 1-based)
            order = sorted(range(len(dated)), key=lambda i: oldest_dates[i])
            a1['sense1_rank_when_resorted'].append(order.index(0) + 1)

        if k1 in probe_set and len(dated) >= 2:
            oldest_dates = [d for _, d in dated]
            probe_rows.append({
                'k1': k1, 'n_dated_senses': len(dated),
                'sense1_oldest': oldest_dates[0] == min(oldest_dates),
                'sense1_date': oldest_dates[0], 'min_date': min(oldest_dates),
                'tau': kendall_tau(oldest_dates),
            })

    # ---- derive ----
    def pct(a, b):
        return round(100.0 * a / b, 1) if b else None

    report = {
        'source': path,
        'analysis_1_cross_sense_order': {
            'entries_with_numbered_senses': a1['entries_multisense'],
            'entries_with_>=2_dated_senses': a1['entries_>=2_dated'],
            'pct_printed_sense1_is_oldest_attested':
                pct(a1['sense1_is_oldest'], a1['entries_>=2_dated']),
            'mean_kendall_tau_printed_vs_date':
                round(statistics.mean(a1['taus']), 3) if a1['taus'] else None,
            'note': 'tau=1 -> printed order already = oldest-first; tau=0 -> uncorrelated.',
        },
        'analysis_3_within_sense_chronology': {
            'senses_with_>=2_dated_citations': a3['senses_>=2_dated'],
            'pct_senses_fully_chronological(tau=1)':
                pct(a3['monotone'], a3['senses_>=2_dated']),
            'mean_within_sense_kendall_tau':
                round(statistics.mean(a3['weak_taus']), 3) if a3['weak_taus'] else None,
            'pct_adjacent_citation_pairs_nondecreasing':
                pct(a3['adj_nondec'], a3['adj_pairs']),
        },
        'analysis_2_probe': {
            'n_probe_words_with_>=2_dated_senses': len(probe_rows),
            'pct_probe_sense1_is_oldest':
                pct(sum(r['sense1_oldest'] for r in probe_rows), len(probe_rows)),
            'rows': sorted(probe_rows, key=lambda r: r['k1']),
        },
    }
    out_json = os.path.join(HERE, 'sense_order_metrics.json')
    with open(out_json, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print('\nwrote', out_json, file=sys.stderr)


if __name__ == '__main__':
    main()
