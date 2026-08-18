#!/usr/bin/env python
"""h2856_e5_translation_drift.py — E5 three-way translation drift: PWG-de skeleton
vs PWG-ru gloss vs Kochergina.

H2856 / EPISTEMIC_REACH_MEMO.md §3 E5: "The Russian gloss diverges from the
German original systematically (sense-splitting, register normalization), and
divergence is larger on headwords where PWG-ru and Kochergina disagree."

Inputs:
  src/pwg_ru_translated.jsonl   — per-sense `de` (German skeleton) + `ru` (Russian
                                   gloss) rows, keyed by key1/sense_tag/layer
  src/koch.jsonl                — 29,177 Kochergina (1987) Russian glosses, keyed
                                   by `slp1`
  src/pwg_ru_relationships.jsonl — restate/add/relocate/correct relationship
                                   records between PW/PWG layers within a card
                                   (the memo's "sense-split axis" feed)

Method:
  - sense-count delta: (distinct PWG-ru sense_tags for a headword) - 1, since
    Kochergina is ~always a single undifferentiated gloss per headword — the
    sense-SPLITTING signal proper.
  - gloss-length ratio: len(PWG-ru text) / len(Kochergina gloss), a coarse
    elaboration-ratio proxy.
  - PWG-ru <-> Kochergina disagreement: 1 - Jaccard(stemmed Russian content
    tokens), reusing corpus_gate.py's own `ru_tokens` stemming convention
    (inlined here rather than imported, to avoid corpus_gate.py's module-level
    side effects — it opens several index files and a corpus DB connection at
    import time that this script does not need).
  - register-shift proxy: density of PWG editorial-apparatus tags (<ab>, <lex>)
    per 100 chars of the PWG-ru gloss (Kochergina glosses carry none of these
    by construction, so this is a one-sided PWG-only signal, not a
    two-sided register comparison — recorded as a limitation, not hidden).
  - the sense-split axis: whether a headword has any pwg_ru_relationships.jsonl
    record (restate/add/relocate/correct) at all, and which op — this is a
    PW<->PWG *layer* signal (multi-source card assembly), not literally a
    German<->Russian signal; used here exactly as the memo routes it ("feeds
    the sense-split axis"), with that scope caveat stated plainly.

Output:
  research/h2856_translation_drift.jsonl
  research/H2856_E5_TRANSLATION_DRIFT.md
  research/figures/reach/h2856_v4_translation_drift_alluvial.svg

Computed by Sonnet 5 (claude-sonnet-5).
"""
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SRC = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(SRC)
RESEARCH = os.path.join(RT, 'research')
FIGDIR = os.path.join(RESEARCH, 'figures', 'reach')

PWG_RU = os.path.join(SRC, 'pwg_ru_translated.jsonl')
KOCH = os.path.join(SRC, 'koch.jsonl')
RELATIONSHIPS = os.path.join(SRC, 'pwg_ru_relationships.jsonl')

OUT_DATA = os.path.join(RESEARCH, 'h2856_translation_drift.jsonl')
OUT_REPORT = os.path.join(RESEARCH, 'H2856_E5_TRANSLATION_DRIFT.md')
OUT_FIG = os.path.join(FIGDIR, 'h2856_v4_translation_drift_alluvial.svg')

_RU_END = re.compile(r'(ого|ому|ыми|ами|ая|ое|ые|ый|ий|ом|ой|ах|ам|ов|у|ю|и|ы|а|я|о|е|ь|й|х|м)$')
_MARKUP = re.compile(r'<[^>]+>')
_PLACEHOLDER = re.compile(r'\{[^}]*\}')


def ru_tokens(text):
    """Stemmed lowercase Cyrillic content tokens (>=3 chars post-strip).
    Mirrors corpus_gate.py's ru_tokens() suffix-stripping convention."""
    text = _PLACEHOLDER.sub(' ', text)
    text = _MARKUP.sub(' ', text)
    toks = re.findall(r'[а-яёА-ЯЁ]{2,}', text.lower())
    return {_RU_END.sub('', t) for t in toks if len(_RU_END.sub('', t)) >= 3}


def ab_lex_density(text):
    n_tags = len(re.findall(r'<ab>|<lex>', text))
    plain_len = len(_MARKUP.sub('', text))
    return 100.0 * n_tags / plain_len if plain_len else 0.0


def jaccard(a, b):
    if not a and not b:
        return None
    u = a | b
    if not u:
        return None
    return len(a & b) / len(u)


def load_pwg_ru_by_key1():
    by_key1 = collections.defaultdict(list)
    with open(PWG_RU, encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            if d.get('layer') != 'pwg':
                continue
            by_key1[d['key1']].append(d)
    return by_key1


def load_koch():
    idx = {}
    with open(KOCH, encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            k = d.get('slp1')
            if k and k not in idx:
                idx[k] = d.get('gloss', '')
    return idx


def load_relationships_by_key1():
    by_key1 = collections.defaultdict(list)
    with open(RELATIONSHIPS, encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            r = d.get('relationship', {})
            by_key1[d['key1']].append(r.get('op', 'unknown'))
    return by_key1


def relationship_bucket(ops):
    if not ops:
        return 'direct (no PW-layer relationship record)'
    c = collections.Counter(ops)
    top = c.most_common(1)[0][0]
    return top


def drift_bucket(disagreement):
    if disagreement is None:
        return 'no_koch_content'
    if disagreement <= 0.5:
        return 'converge'
    if disagreement <= 0.8:
        return 'partial'
    return 'diverge'


def main():
    os.makedirs(FIGDIR, exist_ok=True)

    pwg_ru = load_pwg_ru_by_key1()
    print('pwg_ru (layer=pwg) distinct key1:', len(pwg_ru))
    koch = load_koch()
    print('koch.jsonl distinct slp1:', len(koch))
    rel = load_relationships_by_key1()
    print('pwg_ru_relationships distinct key1:', len(rel))

    matched = set(pwg_ru) & set(koch)
    print('key1 present in BOTH pwg_ru and koch:', len(matched))

    rows = []
    for k in sorted(matched):
        senses = [r for r in pwg_ru[k] if r.get('sense_tag') not in (None, 'note')]
        n_senses = len(set(r.get('sense_tag') for r in senses)) or 1
        ru_text = ' '.join(r.get('ru', '') for r in pwg_ru[k])
        koch_gloss = koch[k]
        plain_ru = _MARKUP.sub(' ', ru_text)
        plain_koch = _MARKUP.sub(' ', koch_gloss)
        gloss_ratio = (len(plain_ru.strip()) / len(plain_koch.strip())) if plain_koch.strip() else None
        ru_toks = ru_tokens(ru_text)
        koch_toks = ru_tokens(koch_gloss)
        overlap = jaccard(ru_toks, koch_toks)
        disagreement = (1 - overlap) if overlap is not None else None
        ops = rel.get(k, [])
        rows.append({
            'key1': k,
            'n_senses': n_senses,
            'sense_count_delta': n_senses - 1,
            'gloss_length_ratio': gloss_ratio,
            'jaccard_overlap': overlap,
            'disagreement': disagreement,
            'ab_lex_density_per_100chars': ab_lex_density(ru_text),
            'relationship_ops': ops,
            'relationship_bucket': relationship_bucket(ops),
            'drift_bucket': drift_bucket(disagreement),
        })

    with open(OUT_DATA, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    n = len(rows)
    split_n = sum(1 for r in rows if r['sense_count_delta'] > 0)
    merge_n = sum(1 for r in rows if r['sense_count_delta'] < 0)
    drop_n = sum(1 for r in rows if r['gloss_length_ratio'] is not None and r['gloss_length_ratio'] < 0.3)

    disagreements = [r['disagreement'] for r in rows if r['disagreement'] is not None]
    mean_disagreement = sum(disagreements) / len(disagreements) if disagreements else 0.0

    has_rel = [r['disagreement'] for r in rows if r['relationship_ops'] and r['disagreement'] is not None]
    no_rel = [r['disagreement'] for r in rows if not r['relationship_ops'] and r['disagreement'] is not None]
    mean_has_rel = sum(has_rel) / len(has_rel) if has_rel else None
    mean_no_rel = sum(no_rel) / len(no_rel) if no_rel else None

    drift_counts = collections.Counter(r['drift_bucket'] for r in rows)
    rel_counts = collections.Counter(r['relationship_bucket'] for r in rows)

    print('n matched:', n, 'split (delta>0):', split_n, 'merge (delta<0):', merge_n, 'drop (ratio<0.3):', drop_n)
    print('mean disagreement:', round(mean_disagreement, 3))
    print('mean disagreement | has relationship record:', mean_has_rel, '| no record:', mean_no_rel)
    print('drift buckets:', dict(drift_counts))
    print('relationship buckets:', dict(rel_counts))

    draw_alluvial(rows, OUT_FIG)
    write_report(n, split_n, merge_n, drop_n, mean_disagreement, mean_has_rel, mean_no_rel,
                 drift_counts, rel_counts, len(pwg_ru), len(koch))
    print('wrote', OUT_DATA)
    print('wrote', OUT_REPORT)
    print('wrote', OUT_FIG)


def draw_alluvial(rows, outpath):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    import matplotlib.patches as mpatches

    def sense_col(r):
        if r['n_senses'] == 1:
            return '1 sense'
        if r['n_senses'] <= 3:
            return '2-3 senses'
        return '4+ senses'

    col1 = collections.Counter(sense_col(r) for r in rows)
    col2 = collections.Counter(r['relationship_bucket'] for r in rows)
    col3 = collections.Counter(r['drift_bucket'] for r in rows)

    col1_order = ['1 sense', '2-3 senses', '4+ senses']
    col2_order = sorted(col2, key=lambda k: -col2[k])
    col3_order = ['converge', 'partial', 'diverge', 'no_koch_content']

    flow12 = collections.Counter((sense_col(r), r['relationship_bucket']) for r in rows)
    flow23 = collections.Counter((r['relationship_bucket'], r['drift_bucket']) for r in rows)

    n = len(rows)
    fig, ax = plt.subplots(figsize=(11, 6.5))

    def col_positions(order, counts, x):
        total = sum(counts.values())
        y = 0.0
        pos = {}
        for k in order:
            h = counts.get(k, 0) / total if total else 0
            pos[k] = (y, y + h)
            y += h
        return pos

    x1, x2, x3 = 0.0, 0.45, 0.9
    p1 = col_positions(col1_order, col1, x1)
    p2 = col_positions(col2_order, col2, x2)
    p3 = col_positions(col3_order, col3, x3)

    colors = plt.cm.tab10.colors

    def draw_flow(xa, xb, ya0, ya1, yb0, yb1, color):
        verts = [(xa, ya0), (xa + (xb - xa) * 0.5, ya0), (xa + (xb - xa) * 0.5, yb0), (xb, yb0),
                 (xb, yb1), (xa + (xb - xa) * 0.5, yb1), (xa + (xb - xa) * 0.5, ya1), (xa, ya1), (xa, ya0)]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                 Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
        path = Path(verts, codes)
        patch = mpatches.PathPatch(path, facecolor=color, edgecolor='none', alpha=0.55)
        ax.add_patch(patch)

    cursor1 = {k: p1[k][0] for k in col1_order}
    cursor2a = {k: p2[k][0] for k in col2_order}
    for i, (a, b) in enumerate(sorted(flow12, key=lambda ab: col1_order.index(ab[0]))):
        cnt = flow12[(a, b)]
        h = cnt / n
        draw_flow(x1, x2, cursor1[a], cursor1[a] + h, cursor2a[b], cursor2a[b] + h, colors[col1_order.index(a) % 10])
        cursor1[a] += h
        cursor2a[b] += h

    cursor2b = {k: p2[k][0] for k in col2_order}
    cursor3 = {k: p3[k][0] for k in col3_order}
    for a, b in sorted(flow23, key=lambda ab: col2_order.index(ab[0]) if ab[0] in col2_order else 99):
        cnt = flow23[(a, b)]
        h = cnt / n
        draw_flow(x2, x3, cursor2b[a], cursor2b[a] + h, cursor3[b], cursor3[b] + h,
                  colors[col2_order.index(a) % 10] if a in col2_order else 'grey')
        cursor2b[a] += h
        cursor3[b] += h

    for order, pos, x, label_side in ((col1_order, p1, x1, 'left'), (col2_order, p2, x2, 'mid'), (col3_order, p3, x3, 'right')):
        for k in order:
            y0, y1 = pos[k]
            ax.add_patch(mpatches.Rectangle((x - 0.01, y0), 0.02, y1 - y0, facecolor='black'))
            ax.text(x + (0.02 if label_side != 'right' else -0.02), (y0 + y1) / 2,
                    '%s (%d)' % (k, int(round((y1 - y0) * n))),
                    ha='left' if label_side != 'right' else 'right', va='center', fontsize=8)

    ax.set_xlim(-0.35, 1.3)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('E5: sense count -> PW-layer relationship -> PWG-ru vs Kochergina agreement (n=%d)' % n, fontsize=10)
    fig.tight_layout()
    fig.savefig(outpath, format='svg')
    plt.close(fig)


def write_report(n, split_n, merge_n, drop_n, mean_disagreement, mean_has_rel, mean_no_rel,
                  drift_counts, rel_counts, n_pwg_ru_keys, n_koch_keys):
    lines = []
    lines.append('# H2856 E5 — three-way translation drift (de -> ru -> Kochergina)')
    lines.append('')
    lines.append('_Created: 18-08-2026 · Last updated: 18-08-2026_')
    lines.append('')
    lines.append('Computed by Sonnet 5 (`claude-sonnet-5`). Driver: '
                  '[`src/h2856_e5_translation_drift.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h2856_e5_translation_drift.py). '
                  'Re-run: `python src/h2856_e5_translation_drift.py` from `RussianTranslation/`.')
    lines.append('')
    lines.append('## Inputs and join')
    lines.append('- `src/pwg_ru_translated.jsonl`, layer=`pwg` — %d distinct headwords' % n_pwg_ru_keys)
    lines.append('- `src/koch.jsonl` — %d distinct headwords (Kochergina 1987)' % n_koch_keys)
    lines.append('- `src/pwg_ru_relationships.jsonl` — PW<->PWG layer relationship records')
    lines.append('- Matched (present in both PWG-ru and Kochergina): **n=%d**' % n)
    lines.append('')
    lines.append('**Coverage caveat:** `pwg_ru_translated.jsonl` currently covers 254 distinct PWG '
                 'headwords total (pwg_ru is an in-progress translation effort, not yet run over '
                 'the full 106,082-headword PWG set — see '
                 '[`pwg_ru.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md)). '
                 'E5\'s population is therefore bounded by pwg_ru\'s current progress, not by data '
                 'availability for the full dictionary — the n=%d below will grow as pwg_ru does.' % n)
    lines.append('')
    lines.append('## Scope caveat — the relationship data is PW<->PWG, not de<->ru')
    lines.append('')
    lines.append('The memo routes `pwg_ru_relationships.jsonl`\'s restate/abridge typology as '
                 'feeding "the sense-split axis" of E5. In the committed data this typology is '
                 'actually recorded between the **PW and PWG dictionary layers** inside a pwg_ru '
                 'card (multi-source card assembly — `layer: "pw"` rows being restated/added/'
                 'relocated relative to the PWG base), not between the German skeleton and the '
                 'Russian gloss directly. Used exactly as the memo names it, with this scope stated '
                 'plainly rather than silently reframed as a de<->ru signal it is not.')
    lines.append('')
    lines.append('## Sense-splitting (PWG-ru sense count vs Kochergina\'s single gloss)')
    lines.append('')
    lines.append('| | n | share |')
    lines.append('|---|--:|--:|')
    lines.append('| split (PWG-ru has more distinguishable senses than 1) | %d | %.1f%% |' % (split_n, 100 * split_n / n))
    lines.append('| merge (n_senses < 1, does not occur by construction) | %d | %.1f%% |' % (merge_n, 100 * merge_n / n))
    lines.append('| drop (PWG-ru text <30%% the length of Kochergina\'s) | %d | %.1f%% |' % (drop_n, 100 * drop_n / n))
    lines.append('')
    lines.append('## PWG-ru <-> Kochergina disagreement')
    lines.append('')
    lines.append('Disagreement = 1 - Jaccard(stemmed Russian content tokens). Mean disagreement '
                 'across all %d matched headwords: **%.3f**.' % (n, mean_disagreement))
    lines.append('')
    lines.append('| bucket | n | share |')
    lines.append('|---|--:|--:|')
    for b in ('converge', 'partial', 'diverge', 'no_koch_content'):
        c = drift_counts.get(b, 0)
        lines.append('| %s | %d | %.1f%% |' % (b, c, 100 * c / n if n else 0))
    lines.append('')
    lines.append('## Does a PW<->PWG relationship record correlate with more PWG-ru/Kochergina disagreement?')
    lines.append('')
    if mean_has_rel is not None and mean_no_rel is not None:
        lines.append('Mean disagreement for headwords **with** a relationship record: **%.3f**; '
                     '**without**: **%.3f**.' % (mean_has_rel, mean_no_rel))
        direction = 'higher' if mean_has_rel > mean_no_rel else 'lower'
        lines.append('Headwords with a PW<->PWG relationship record show **%s** PWG-ru/Kochergina '
                     'disagreement than headwords without one — %s the memo\'s directional claim '
                     '(more internal editorial complexity co-occurs with more external translation '
                     'divergence).' % (direction, 'consistent with' if direction == 'higher' else 'contrary to'))
    else:
        lines.append('Insufficient overlap to compare (too few matched headwords carry a relationship record).')
    lines.append('')
    lines.append('Relationship-bucket distribution over the matched set:')
    lines.append('')
    lines.append('| bucket | n |')
    lines.append('|---|--:|')
    for k, c in rel_counts.most_common():
        lines.append('| %s | %d |' % (k, c))
    lines.append('')
    lines.append('## V4 — translation-drift alluvial')
    lines.append('')
    lines.append('sense count -> PW-layer relationship type -> PWG-ru/Kochergina agreement, ribbon width = share of the %d matched headwords.' % n)
    lines.append('')
    lines.append('![V4 alluvial](figures/reach/h2856_v4_translation_drift_alluvial.svg)')
    lines.append('')
    lines.append('## Evidence')
    lines.append('- Full per-headword table: [`research/h2856_translation_drift.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/h2856_translation_drift.jsonl) (%d rows)' % n)
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    with open(OUT_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
