#!/usr/bin/env python
"""build_gold_koch.py — freeze a Sa->Ru BLI gold set from Kochergina.

Two independence requirements, both violated by the obvious default source:

1. **Gold content** must not come from `corpus_lexicon.jsonl` itself.
   `corpus_lexicon.jsonl`'s own 3-layer Sa->Ru glossary
   (`glossary/surface_glossary.jsonl`) is a direct group-by/count aggregation OF
   `corpus_lexicon.jsonl` (see `build_surface_glossary.py`) -- using it as BLI gold
   would score the lexicon against itself (P@1 -> ~1.0 trivially). Kochergina
   (`src/koch.jsonl`, 29,177 entries) is an independently authored dictionary never
   derived from the corpus, so it is the non-circular gold CONTENT source, per
   H1521's own fallback clause ("Kochergina verified vocabulary ... as fallback").

2. **"High-frequency" selection** must also not be measured from
   `corpus_lexicon.jsonl` -- ranking candidate gold lemmas by their OWN frequency
   in the file being evaluated makes `coverage` trivially 1.0 by construction (every
   selected lemma is guaranteed present). Instead this uses VisualDCS's independent
   `dcs_lemma_summary.json` frequency band (Hellwig's DCS ~2021 whole-corpus counts,
   a different, much larger corpus than the 1.09M-pair translated subset here) as the
   frequency ranking, so `coverage` measures a real property of corpus_lexicon.jsonl
   (whether it happens to include a given independently-frequent lemma) rather than
   a tautology.

Selects the N=400 koch lemmas with the highest DCS freqBand (ties broken
alphabetically for determinism), skips bound/compound second members (koch slp1
starting with '-'), and skips any lemma whose koch gloss yields zero extractable
Russian content words (>=4 Cyrillic letters) after stripping Sanskrit/Devanagari
residue and short grammatical particles -- those can't support a word-overlap match
either way.

Usage: python build_gold_koch.py <koch.jsonl> <dcs_lemma_summary.json> <out.tsv> [--n 400]
"""
import argparse
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

CONTENT_RE = re.compile(r'[а-яёА-ЯЁ]{4,}')

# Kochergina notation filler that is Cyrillic, >=4 letters, and would otherwise
# leak into every entry's token set as a false "content word".
STOP_TOKENS = {
    'кого-л', 'чего-л', 'что-л', 'какой-л', 'каком-л', 'которого-л',
    'напротив', 'например', 'иногда', 'обычно', 'также', 'только', 'весьма',
    'очень', 'более', 'менее', 'часто', 'редко', 'вообще', 'обыкн', 'преим',
}


def gloss_tokens(text):
    toks = {t.lower() for t in CONTENT_RE.findall(text or '')}
    return toks - STOP_TOKENS


def load_koch(path):
    """slp1 -> list of raw gloss strings (bound forms starting with '-' excluded)."""
    by_slp1 = collections.defaultdict(list)
    with open(path, encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            slp1 = d.get('slp1') or ''
            if not slp1 or slp1.startswith('-'):
                continue
            gloss = d.get('gloss') or ''
            if gloss:
                by_slp1[slp1].append(gloss)
    return by_slp1


def load_dcs_freq_bands(path):
    """slp1 -> DCS freqBand (1..5), from VisualDCS's independent dcs_lemma_summary.json."""
    with open(path, encoding='utf-8-sig') as f:
        d = json.load(f)
    return {slp1: rec['freqBand'] for slp1, rec in d['lemmas'].items()}


def build(koch_path, dcs_summary_path, n):
    koch = load_koch(koch_path)
    print(f'[gold] {len(koch)} standalone koch lemmas', file=sys.stderr)
    bands = load_dcs_freq_bands(dcs_summary_path)
    ranked = sorted(
        (slp1 for slp1 in koch if slp1 in bands),
        key=lambda slp1: (-bands[slp1], slp1))
    print(f'[gold] {len(ranked)} koch lemmas found in the independent DCS frequency table',
          file=sys.stderr)

    rows = []
    for slp1 in ranked:
        toks = set()
        for gloss in koch[slp1]:
            toks |= gloss_tokens(gloss)
        if not toks:
            continue
        rows.append((slp1, bands[slp1], sorted(toks)))
        if len(rows) >= n:
            break
    print(f'[gold] {len(rows)} lemmas kept (had >=1 content-word gloss token)',
          file=sys.stderr)
    return rows


def write_tsv(rows, out_path, koch_path, dcs_summary_path, n):
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Frozen Sa->Ru BLI gold set for H1521 (RussianTranslation/src/eval/bli_eval.py)\n')
        f.write(f'# Content source: {os.path.basename(koch_path)} (independent Kochergina\n')
        f.write('# dictionary, NOT derived from corpus_lexicon.jsonl -- see build_gold_koch.py\n')
        f.write('# docstring for why the 3-layer surface_glossary was rejected as circular).\n')
        f.write(f'# Frequency source: {os.path.basename(dcs_summary_path)} (VisualDCS, Hellwig\n')
        f.write('# DCS ~2021 whole-corpus counts -- independent of corpus_lexicon.jsonl, so\n')
        f.write('# `coverage` measured downstream is a real number, not a tautology).\n')
        f.write(f'# Selection: top {n} koch lemmas by DCS freqBand desc (ties: slp1 asc),\n')
        f.write('# standalone forms only (no bound "-X" compound members), gloss reduced to\n')
        f.write('# Russian content-word tokens (Cyrillic, len>=4, notation filler stripped).\n')
        f.write('slp1\tfreq\tru_gold_tokens\n')
        for slp1, band, toks in rows:
            f.write(f'{slp1}\t{band}\t{"|".join(toks)}\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('koch')
    ap.add_argument('dcs_summary')
    ap.add_argument('out')
    ap.add_argument('--n', type=int, default=400)
    args = ap.parse_args()
    rows = build(args.koch, args.dcs_summary, args.n)
    write_tsv(rows, args.out, args.koch, args.dcs_summary, args.n)
    print(f'[gold] wrote {len(rows)} rows -> {args.out}', file=sys.stderr)


if __name__ == '__main__':
    main()
