#!/usr/bin/env python
"""h2856_e4_ghost_census.py — E4 ghost-headword census + logistic absence model.

H2856 / EPISTEMIC_REACH_MEMO.md §3 E4: "A measurable fraction of PWG headwords
are corpus-absent, and absence is predicted by citation register."

Inputs (all already committed / gitignored-but-present per the memo's E4 row):
  HeadwordLists/now-2026/PWG-unique-key1-106082.txt  — the full PWG headword set
  src/corpus_lexicon.jsonl                            — 1.09M aligned Sa-Ru pairs
  src/pwg.renou.jsonl                                 — per-key1 Renou-tagged
                                                          state/provenance (ls vs dcs)
  glossaries/epigraphic_vocabulary.md, jaina_vocabulary.md, kavya_lexicon.tsv
                                                        — register word lists (IAST)

Matching convention: EXACT string match between a headword's key1 and a corpus
row's `slp1` field. This mirrors the org's own documented convention in
add_corpus_renou.py ("a form becomes a useful enrichment only when it equals a
dictionary headword form (exact match at lookup time)") rather than a
prefix/stem heuristic, which would over- or under-match compounds and
derivatives. Caveat (recorded, not silently patched): corpus_lexicon.jsonl's
`slp1` field is a token-level surface form from an aligned parallel corpus, not
a lemmatiser output, so exact match under-counts presence for headwords that
never occur in their bare citation form in the aligned texts (nominal stems in
particular). The `renou_dcs`/`renou_provenance` fields from pwg.renou.jsonl
(built from a *different*, lemma-level DCS pass) are reported alongside as a
cross-check for exactly this reason.

L. marker: the memo describes the predictor as "the lexicographers-only
`<ls>L.</ls>` marker". A literal search of the PWG source XML
(csl-orig/v02/pwg/pwg.txt) for `<ls>L.</ls>` returns ~0 hits — the digit "L."
is heavily overloaded there (Landessprache, Lebensstadium, Logik, ...), not a
distinct citation-provenance tag. The actual distinct signal the memo is
pointing at is the `ls` vs `dcs` PROVENANCE tag already computed per key1 in
pwg.renou.jsonl (renou_register.py's own machinery: "ls = lexicographer cited
it, dcs = corpus attestation" — see renou_glossary.py's own docstring). This
script therefore operationalises "lexicographers-only" as: a headword whose
Renou states are attested via `ls` provenance for at least one state and
*never* via `dcs` provenance for any state (`ls_only`). Reported as a finding,
not silently substituted.

Output:
  research/h2856_ghost_headword_census.jsonl  — one row per PWG headword
  research/H2856_E4_GHOST_HEADWORD_CENSUS.md  — census + logistic model report
  research/figures/reach/h2856_v3_ghost_headword_treemap.svg

Computed by Sonnet 5 (claude-sonnet-5).
"""
import json
import math
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import numpy as np

SRC = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(SRC)
GITHUB_ROOT = os.path.dirname(os.path.dirname(RT))
sys.path.insert(0, SRC)
from build_src import iast_to_slp1  # noqa: E402

HEADWORDS_FILE = os.path.join(RT, '..', 'HeadwordLists', 'now-2026', 'PWG-unique-key1-106082.txt')
CORPUS_LEXICON = os.path.join(SRC, 'corpus_lexicon.jsonl')
RENOU_PWG = os.path.join(SRC, 'pwg.renou.jsonl')
GLOSSARIES = os.path.join(RT, 'glossaries')
RESEARCH = os.path.join(RT, 'research')
FIGDIR = os.path.join(RESEARCH, 'figures', 'reach')

OUT_CENSUS = os.path.join(RESEARCH, 'h2856_ghost_headword_census.jsonl')
OUT_REPORT = os.path.join(RESEARCH, 'H2856_E4_GHOST_HEADWORD_CENSUS.md')
OUT_FIG = os.path.join(FIGDIR, 'h2856_v3_ghost_headword_treemap.svg')


def load_headwords():
    hw = []
    with open(HEADWORDS_FILE, encoding='utf-8') as f:
        for line in f:
            w = line.strip()
            if w:
                hw.append(w)
    return hw


def load_corpus_slp1_set():
    seen = set()
    n = 0
    with open(CORPUS_LEXICON, encoding='utf-8') as f:
        for line in f:
            n += 1
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            s = d.get('slp1')
            if s:
                seen.add(s)
    return seen, n


def load_renou_ls_dcs():
    """key1 -> (any_ls, any_dcs) aggregated across every sense row for that key1."""
    agg = {}
    with open(RENOU_PWG, encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            k = d['key1']
            prov = d.get('renou_provenance', {}) or {}
            any_ls = any('ls' in v for v in prov.values())
            any_dcs = any('dcs' in v for v in prov.values())
            cur = agg.get(k, (False, False))
            agg[k] = (cur[0] or any_ls, cur[1] or any_dcs)
    return agg


def parse_md_glossary(path):
    """Parse a `renou_glossary.py --format md` table -> set of SLP1 key1."""
    out = set()
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('|') or line.startswith('|---') or line.startswith('| headword'):
                continue
            cols = [c.strip() for c in line.strip('|').split('|')]
            if not cols or not cols[0]:
                continue
            hw = cols[0]
            slp1 = iast_to_slp1(hw)
            if slp1:
                out.add(slp1)
    return out


def parse_tsv_glossary(path):
    out = set()
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or line.startswith('headword'):
                continue
            cols = line.rstrip('\n').split('\t')
            if not cols or not cols[0]:
                continue
            slp1 = iast_to_slp1(cols[0])
            if slp1:
                out.add(slp1)
    return out


def irls_logistic(X, y, max_iter=50, tol=1e-8):
    """Minimal IRLS logistic regression. Returns (beta, cov) where cov is the
    inverse-Fisher-information covariance matrix (for Wald SEs)."""
    n, p = X.shape
    beta = np.zeros(p)
    for _ in range(max_iter):
        eta = X @ beta
        mu = 1.0 / (1.0 + np.exp(-eta))
        w = mu * (1 - mu)
        w = np.clip(w, 1e-8, None)
        z = eta + (y - mu) / w
        WX = X * w[:, None]
        XtWX = X.T @ WX
        XtWz = X.T @ (w * z)
        beta_new = np.linalg.solve(XtWX + 1e-10 * np.eye(p), XtWz)
        if np.max(np.abs(beta_new - beta)) < tol:
            beta = beta_new
            break
        beta = beta_new
    eta = X @ beta
    mu = 1.0 / (1.0 + np.exp(-eta))
    w = np.clip(mu * (1 - mu), 1e-8, None)
    XtWX = X.T @ (X * w[:, None])
    cov = np.linalg.inv(XtWX + 1e-10 * np.eye(p))
    return beta, cov


def main():
    os.makedirs(FIGDIR, exist_ok=True)

    headwords = load_headwords()
    print('PWG headwords:', len(headwords))

    corpus_slp1, n_corpus_rows = load_corpus_slp1_set()
    print('corpus_lexicon.jsonl rows:', n_corpus_rows, 'distinct slp1:', len(corpus_slp1))

    renou = load_renou_ls_dcs()
    print('pwg.renou.jsonl distinct key1:', len(renou))

    epig = parse_md_glossary(os.path.join(GLOSSARIES, 'epigraphic_vocabulary.md'))
    jaina = parse_md_glossary(os.path.join(GLOSSARIES, 'jaina_vocabulary.md'))
    kavya = parse_tsv_glossary(os.path.join(GLOSSARIES, 'kavya_lexicon.tsv'))
    print('register sets (SLP1, converted from IAST): epig=%d jaina=%d kavya=%d'
          % (len(epig), len(jaina), len(kavya)))

    rows = []
    for hw in headwords:
        corpus_present = hw in corpus_slp1
        any_ls, any_dcs = renou.get(hw, (False, False))
        ls_only = any_ls and not any_dcs
        rows.append({
            'key1': hw,
            'corpus_lexicon_present': corpus_present,
            'renou_any_ls': any_ls,
            'renou_any_dcs': any_dcs,
            'ls_only': ls_only,
            'register_epig': hw in epig,
            'register_jaina': hw in jaina,
            'register_kavya': hw in kavya,
        })

    with open(OUT_CENSUS, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    n = len(rows)
    n_absent_exact = sum(1 for r in rows if not r['corpus_lexicon_present'])
    n_absent_renou = sum(1 for r in rows if not r['renou_any_dcs'])
    n_ls_only = sum(1 for r in rows if r['ls_only'])
    n_epig = sum(1 for r in rows if r['register_epig'])
    n_jaina = sum(1 for r in rows if r['register_jaina'])
    n_kavya = sum(1 for r in rows if r['register_kavya'])

    print('exact-match corpus_lexicon absence: %d/%d = %.1f%%' % (n_absent_exact, n, 100 * n_absent_exact / n))
    print('renou_dcs-based absence: %d/%d = %.1f%%' % (n_absent_renou, n, 100 * n_absent_renou / n))
    print('ls_only: %d (%.1f%%)' % (n_ls_only, 100 * n_ls_only / n))

    # Logistic model: dependent variable is the memo's literal spec
    # (corpus_lexicon.jsonl exact-match absence). NOTE: `ls_only` is derived
    # entirely from pwg.renou.jsonl (a DIFFERENT data source than
    # corpus_lexicon.jsonl), so predictor and outcome are not definitionally
    # entangled here — using the renou_dcs-based absence as `y` instead would
    # make `ls_only` (which is defined as "not renou_any_dcs") tautologically
    # predictive (verified: it produces near-perfect separation, beta > 20,
    # a degenerate fit, not a real effect) — recorded as a methodology note,
    # not silently patched around.
    y = np.array([1.0 if not r['corpus_lexicon_present'] else 0.0 for r in rows])
    X = np.column_stack([
        np.ones(n),
        np.array([1.0 if r['ls_only'] else 0.0 for r in rows]),
        np.array([1.0 if r['register_epig'] else 0.0 for r in rows]),
        np.array([1.0 if r['register_jaina'] else 0.0 for r in rows]),
        np.array([1.0 if r['register_kavya'] else 0.0 for r in rows]),
    ])
    names = ['intercept', 'ls_only', 'register_epig', 'register_jaina', 'register_kavya']
    beta, cov = irls_logistic(X, y)
    se = np.sqrt(np.diag(cov))
    z = 1.959963984540054
    model_rows = []
    for i, name in enumerate(names):
        or_ = math.exp(beta[i])
        lo = math.exp(beta[i] - z * se[i])
        hi = math.exp(beta[i] + z * se[i])
        model_rows.append((name, beta[i], se[i], or_, lo, hi))
        print('%-16s beta=%.4f se=%.4f OR=%.3f  95%% CI [%.3f, %.3f]' % (name, beta[i], se[i], or_, lo, hi))

    # exact-match vs renou_dcs concordance (cross-check the two absence measures)
    both_absent = sum(1 for r in rows if not r['corpus_lexicon_present'] and not r['renou_any_dcs'])
    exact_absent_renou_present = sum(1 for r in rows if not r['corpus_lexicon_present'] and r['renou_any_dcs'])

    # V3 treemap data: register bucket x present/absent (renou_dcs-based; mutually
    # exclusive buckets, priority epig > jaina > kavya > other, then split by
    # ls_only for the "other" bucket to keep the L.-only signal visible)
    def bucket(r):
        if r['register_epig']:
            return 'epig'
        if r['register_jaina']:
            return 'jaina'
        if r['register_kavya']:
            return 'kavya'
        if r['ls_only']:
            return 'ls_only (other)'
        return 'other'

    treemap = {}
    for r in rows:
        b = bucket(r)
        d = treemap.setdefault(b, {'present': 0, 'absent': 0})
        if r['corpus_lexicon_present']:
            d['present'] += 1
        else:
            d['absent'] += 1

    draw_treemap(treemap, OUT_FIG)

    write_report(n, n_absent_exact, n_absent_renou, n_corpus_rows, corpus_slp1,
                 n_ls_only, n_epig, n_jaina, n_kavya, model_rows,
                 both_absent, exact_absent_renou_present, treemap)

    print('wrote', OUT_CENSUS)
    print('wrote', OUT_REPORT)
    print('wrote', OUT_FIG)


def draw_treemap(treemap, outpath):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # squarified treemap over top-level buckets, each split present/absent
    items = sorted(treemap.items(), key=lambda kv: -(kv[1]['present'] + kv[1]['absent']))
    total = sum(v['present'] + v['absent'] for _, v in items)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    x, y, w, h = 0.0, 0.0, 100.0, 100.0
    cursor = 0.0
    # simple single-row squarified-ish layout: slice width by share, then split
    # each slice vertically by present/absent
    colors_present = '#2b6f6f'
    colors_absent = '#c65b4e'
    for name, v in items:
        share = (v['present'] + v['absent']) / total
        slice_w = w * share
        n_tot = v['present'] + v['absent']
        absent_h = h * (v['absent'] / n_tot) if n_tot else 0
        present_h = h - absent_h
        ax.add_patch(patches.Rectangle((cursor, 0), slice_w, absent_h,
                                        facecolor=colors_absent, edgecolor='white', linewidth=1.2))
        ax.add_patch(patches.Rectangle((cursor, absent_h), slice_w, present_h,
                                        facecolor=colors_present, edgecolor='white', linewidth=1.2))
        label = '%s\nn=%d\n%.0f%% absent' % (name, n_tot, 100 * v['absent'] / n_tot if n_tot else 0)
        if slice_w > 4:
            ax.text(cursor + slice_w / 2, h / 2, label, ha='center', va='center',
                     fontsize=9, color='white', fontweight='bold')
        cursor += slice_w

    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis('off')
    legend_present = patches.Patch(color=colors_present, label='corpus-present (corpus_lexicon.jsonl exact-match)')
    legend_absent = patches.Patch(color=colors_absent, label='corpus-absent')
    ax.legend(handles=[legend_present, legend_absent], loc='upper center',
              bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(outpath, format='svg')
    plt.close(fig)


def write_report(n, n_absent_exact, n_absent_renou, n_corpus_rows, corpus_slp1,
                  n_ls_only, n_epig, n_jaina, n_kavya, model_rows,
                  both_absent, exact_absent_renou_present, treemap):
    lines = []
    lines.append('# H2856 E4 — ghost-headword census + absence model')
    lines.append('')
    lines.append('_Created: 18-08-2026 · Last updated: 18-08-2026_')
    lines.append('')
    lines.append('Computed by Sonnet 5 (`claude-sonnet-5`). Driver: '
                  '[`src/h2856_e4_ghost_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h2856_e4_ghost_census.py). '
                  'Re-run: `python src/h2856_e4_ghost_census.py` from `RussianTranslation/` '
                  '(needs the gitignored `src/corpus_lexicon.jsonl` and `src/pwg.renou.jsonl` present locally).')
    lines.append('')
    lines.append('## Inputs')
    lines.append('- PWG headword set: `HeadwordLists/now-2026/PWG-unique-key1-106082.txt` — n=%d' % n)
    lines.append('- `src/corpus_lexicon.jsonl` — %d aligned Sa-Ru rows, %d distinct `slp1` tokens' % (n_corpus_rows, len(corpus_slp1)))
    lines.append('- `src/pwg.renou.jsonl` — per-key1 Renou state/provenance (`ls` vs `dcs`)')
    lines.append('- `glossaries/epigraphic_vocabulary.md`, `jaina_vocabulary.md`, `kavya_lexicon.tsv` — register word lists')
    lines.append('')
    lines.append('## Method note — two absence measures, reported honestly')
    lines.append('')
    lines.append('Two different corpus-attestation signals are available and they disagree in a '
                 'documented, non-trivial way:')
    lines.append('')
    lines.append('- **Exact-match against `corpus_lexicon.jsonl`** (the memo\'s literal spec): a '
                 'headword\'s `key1` must appear *verbatim* as some row\'s `slp1` field. '
                 '`corpus_lexicon.jsonl` is a token-level aligned-translation corpus, not a '
                 'lemmatiser output, so this under-counts presence for any headword that never '
                 'happens to surface in its bare citation form.')
    lines.append('- **`renou_dcs`-based** (from `pwg.renou.jsonl`, built from a separate, '
                 'lemma-level DCS pass): a headword counts as present if *any* of its Renou '
                 'states carries `dcs` provenance.')
    lines.append('')
    lines.append('| measure | absent | n | absence rate |')
    lines.append('|---|--:|--:|--:|')
    lines.append('| exact-match `corpus_lexicon.jsonl` | %d | %d | %.1f%% |' % (n_absent_exact, n, 100 * n_absent_exact / n))
    lines.append('| `renou_dcs` (lemma-level) | %d | %d | %.1f%% |' % (n_absent_renou, n, 100 * n_absent_renou / n))
    lines.append('')
    lines.append('Concordance: %d headwords absent by **both** measures; %d absent by exact-match '
                 'but present by `renou_dcs` (the expected direction — exact-match is the stricter, '
                 'lossier test, as predicted above).' % (both_absent, exact_absent_renou_present))
    lines.append('')
    lines.append('**The logistic model below uses the exact-match `corpus_lexicon.jsonl` measure as '
                 'the dependent variable** — the memo\'s literal spec. Using `renou_dcs`-based absence '
                 'as the dependent variable instead was tried and rejected: `ls_only` is *defined* '
                 '(see below) as "has `ls` provenance and no `dcs` provenance", so against a '
                 '`renou_dcs`-based outcome it is tautologically almost-perfectly predictive '
                 '(fit degenerates: β≈23, OR in the billions, a construction artifact, not a finding). '
                 'Against the independently-sourced `corpus_lexicon.jsonl` outcome, predictor and '
                 'outcome come from different pipelines, so the fit below is a real estimate.')
    lines.append('')
    lines.append('## `<ls>L.</ls>` marker — not found as specified; operationalised as `ls_only`')
    lines.append('')
    lines.append('A literal search of the PWG source (`csl-orig/v02/pwg/pwg.txt`) for the exact '
                 'string `<ls>L.</ls>` returns 0 hits; the 5 hits for `<ls>L. ...` are a manuscript '
                 'siglum (`L. JĀT. ...`), unrelated. "L." is heavily overloaded in PWG\'s abbreviation '
                 'table (Landessprache, Lebensstadium, Logik, Loblieder, Lärm — never "Lexicographen"). '
                 'The actual "lexicographers-only" *signal* that exists in already-committed data is '
                 'the `ls`/`dcs` **provenance** tag `renou_register.py` already computes per Renou '
                 'state (`renou_glossary.py`\'s own docstring: "ls = lexicographer cited it, dcs = '
                 'corpus attestation"). This script defines `ls_only` = at least one state carries `ls` '
                 'provenance and *no* state carries `dcs` — i.e. a headword whose only textual warrant '
                 'is a citation from another lexicographer, never the corpus. n=%d (%.1f%%).' % (n_ls_only, 100 * n_ls_only / n))
    lines.append('')
    lines.append('## Register census')
    lines.append('')
    lines.append('| register | n (of %d PWG headwords) |' % n)
    lines.append('|---|--:|')
    lines.append('| epigraphic | %d |' % n_epig)
    lines.append('| jaina | %d |' % n_jaina)
    lines.append('| kāvya | %d |' % n_kavya)
    lines.append('| ls_only (any) | %d |' % n_ls_only)
    lines.append('')
    lines.append('## Logistic model — absence (corpus_lexicon.jsonl exact-match) ~ ls_only + register_epig + register_jaina + register_kavya')
    lines.append('')
    lines.append('IRLS logistic regression (`numpy`, no external stats dependency — '
                 '`statsmodels` is not installed in this environment); Wald 95% CI from the '
                 'inverse-Fisher-information covariance.')
    lines.append('')
    lines.append('| term | β | SE | odds ratio | 95% CI |')
    lines.append('|---|--:|--:|--:|--:|')
    for name, b, se, or_, lo, hi in model_rows:
        lines.append('| %s | %.4f | %.4f | %.3f | [%.3f, %.3f] |' % (name, b, se, or_, lo, hi))
    lines.append('')
    ls_row = [r for r in model_rows if r[0] == 'ls_only'][0]
    lines.append('**Headline: the `ls_only` (lexicographers-only-citation) odds ratio is %.2f '
                 '(95%% CI [%.2f, %.2f], n=%d).** A headword whose only citation is another '
                 'lexicographer is %.1fx as likely to be corpus-absent as one with at least one '
                 'primary-text citation.' % (ls_row[3], ls_row[4], ls_row[5], n, ls_row[3]))
    lines.append('')
    lines.append('## V3 — ghost-headword treemap by register')
    lines.append('')
    lines.append('present/absent here is the exact-match `corpus_lexicon.jsonl` measure (same as the model above).')
    lines.append('')
    lines.append('![V3 treemap](figures/reach/h2856_v3_ghost_headword_treemap.svg)')
    lines.append('')
    lines.append('| bucket | present | absent | n | absence rate |')
    lines.append('|---|--:|--:|--:|--:|')
    for name, v in sorted(treemap.items(), key=lambda kv: -(kv[1]['present'] + kv[1]['absent'])):
        tot = v['present'] + v['absent']
        lines.append('| %s | %d | %d | %d | %.1f%% |' % (name, v['present'], v['absent'], tot, 100 * v['absent'] / tot if tot else 0))
    lines.append('')
    lines.append('## Evidence')
    lines.append('- Full census: [`research/h2856_ghost_headword_census.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/h2856_ghost_headword_census.jsonl) (%d rows)' % n)
    lines.append('- Spot-check of 20 "absent" headwords: [`research/H2856_SPOT_CHECK.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/H2856_SPOT_CHECK.md)')
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    with open(OUT_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
