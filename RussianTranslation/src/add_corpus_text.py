#!/usr/bin/env python
"""Add a new verse-aligned text to the corpus lexicon (incremental, resumable).

Pipeline for a new parallel text — see ADDING_TEXTS.md for the full guide:

  1. Put the text at SamudraManthanam/web/corpus_builder/jsonl/<work>.jsonl
     (verse-aligned JSONL: one line per segment, fields {group, seg, text, lang,
     passage}; seg='sa' Sanskrit verse, seg='ru' Russian translation, seg='comm*'
     commentary). The Russian MUST contain Cyrillic — placeholder '…' is skipped.
  2. python add_corpus_text.py <work> [--genre "..."] [--date YEAR]
                                       [--period "..."] [--workers 8]

What it does:
  - validates the source (counts sa/ru segments, warns if mostly placeholder),
  - (re)stratifies: regenerates corpus_strata.json (picks up the file if a
    build_strata RULE matches its name); if unmatched, injects a stratum from
    --genre/--date (else exits telling you to add a RULE),
  - aligns ONLY that work via DeepSeek (resumable — skips groups already done;
    appends to corpus_lexicon.jsonl),
  - runs the integrity audit and prints the coverage delta.

Idempotent: re-running only aligns groups not already in the lexicon.
"""
import argparse, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SM = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'SamudraManthanam',
                                   'web', 'corpus_builder', 'jsonl'))
STRATA_PATH = os.path.join(HERE, 'corpus_strata.json')
CYR = re.compile('[Ѐ-ӿԀ-ԯⷠ-ⷿꙀ-ꚟ]')
PY = sys.executable


def run(script_args):
    print('  $ python %s' % ' '.join(script_args))
    subprocess.run([PY] + script_args, cwd=HERE, check=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('work', help='work name (file basename, with or without .jsonl)')
    ap.add_argument('--genre', help='Renou genre, if no build_strata RULE matches')
    ap.add_argument('--date', type=int, help='median date (year; negative = BCE)')
    ap.add_argument('--period', help='period bucket (default: derived from --date)')
    ap.add_argument('--workers', default='8')
    a = ap.parse_args()
    work = a.work[:-6] if a.work.endswith('.jsonl') else a.work
    src = os.path.join(SM, work + '.jsonl')
    if not os.path.exists(src):
        sys.exit('source not found: %s' % src)

    # 1. validate
    sa = ru = ru_cyr = 0
    for line in open(src, encoding='utf-8'):
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get('deleted'):
            continue
        if e.get('seg') == 'sa':
            sa += 1
        elif e.get('seg') == 'ru':
            ru += 1
            if CYR.search(e.get('text') or ''):
                ru_cyr += 1
    print('source %s: %d sa, %d ru (%d with Cyrillic = real translations)' % (work, sa, ru, ru_cyr))
    if ru_cyr == 0:
        sys.exit('no Cyrillic ru segments — nothing translatable to align.')
    if ru and ru_cyr < ru * 0.5:
        print('  WARNING: %.0f%% of ru segments are placeholders (no Cyrillic) — they are skipped.'
              % (100.0 * (ru - ru_cyr) / ru))

    # 2. stratify
    print('restratifying...')
    run(['build_strata.py'])
    strata = json.load(open(STRATA_PATH, encoding='utf-8'))
    if work not in strata:
        if not (a.genre and a.date is not None):
            sys.exit('work %r is not matched by any build_strata RULE.\n'
                     'Either add a RULE in build_strata.py (preferred — keeps it reproducible),\n'
                     'or pass --genre "..." and --date YEAR to inject an ad-hoc stratum.' % work)
        import build_strata
        strata[work] = {'genre': a.genre, 'genre_code': 'GX', 'date_median': a.date,
                        'date_lo95': a.date, 'date_hi95': a.date,
                        'period': a.period or build_strata.period(a.date),
                        'source': 'manual (add_corpus_text)', 'groups': 0, 'size': 1}
        json.dump(strata, open(STRATA_PATH, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1, sort_keys=True)
        print('  injected ad-hoc stratum: %s · %s · ~%s' % (a.genre, strata[work]['period'], a.date))

    # 3. align only this work (resumable)
    print('aligning %s (DeepSeek, resumable)...' % work)
    run(['build_corpus_lexicon.py', 'build', work + '.jsonl', str(10**9), a.workers])

    # 4. audit + coverage
    print('auditing...')
    run(['_audit.py'])
    run(['corpus_harvest.py', 'coverage'])
    print('done. New attestations are live in corpus_lexicon.jsonl.')


if __name__ == '__main__':
    main()
