#!/usr/bin/env python
"""root_glue_translated.py — glue-after-translate: reassemble a split root's TRANSLATED
sub-cards into one NESTED Russian article.

The inverse of `_pilot_gen_merged.py --root-split`. That hook exploded a giant root into
per-prefix sub-cards (+ <safe>.rootmap.json); each sub-card is translated independently by
the pipeline → pilot/output/<subkey>.merged.md. This reads the rootmap + those translated
files and stitches them back, head (simple verb) first then the prefixed verbs, into one
<safe>.NESTED.md — the reading/print view, lossless re-grouping of the SPLIT cards.

Order: by seg_index (the PWG record order). For canonical Pāṇinian order instead, the
parse-string sort lives in research/root_glue.parse_sort_key.

  python root_glue_translated.py BU          # -> pilot/output/<safe>.NESTED.md
  python root_glue_translated.py BU --dir pilot/output
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from safe_filename import safe_name
import pipeline_version

HERE = os.path.dirname(os.path.abspath(__file__))
# H1386 P3f: PWG_INPUT_DIR points a hermetic harness at a sandbox input dir.
INP = os.environ.get('PWG_INPUT_DIR') or os.path.join(HERE, 'pilot', 'input')
OUT = os.path.join(HERE, 'pilot', 'output')


def body_of(md):
    """Drop a leading '# title' line from a translated sub-card so it nests cleanly."""
    return re.sub(r'\A\s*#[^\n]*\n+', '', md).strip()


def glue(root, outdir):
    rmpath = os.path.join(INP, safe_name(root) + '.rootmap.json')
    if not os.path.exists(rmpath):
        sys.exit('no rootmap %s — run: _pilot_gen_merged.py --root-split %s' % (rmpath, root))
    rm = json.load(open(rmpath, encoding='utf-8'))
    # order: PWG homonyms first (hom → seg_index → part), then headword-level supplements.
    subs = sorted(rm['sub_cards'],
                  key=lambda s: (1,) if s['kind'] == 'supplement'
                  else (0, s.get('hom', 0), s['seg_index'], s.get('part', 0)))
    n_hom = 1 + max((s.get('hom', 0) for s in subs), default=0)
    cur_hom = None
    parts = ['# %s — собранная статья корня (NESTED, из %d под-карточек)'
             % (root, len(subs)), '',
             '_Склейка переведённых под-карточек обратно в одну вложенную статью '
             '(простой глагол + дополнения → приставочные глаголы)._', '']
    have = miss = 0
    for s in subs:
        mdp = os.path.join(outdir, s['subkey'] + '.merged.md')
        sec = s.get('section', '')
        if n_hom > 1 and s['kind'] != 'supplement' and s.get('hom', 0) != cur_hom:
            cur_hom = s.get('hom', 0)
            parts.append('# Омоним %d (корень {#%s#})' % (cur_hom + 1, root))
            parts.append('')
        if s['kind'] in ('head', 'supplement'):
            if sec.startswith('pwg'):
                if s.get('batch_of') is not None:
                    head = ('## Простой глагол (корень {#%s#}) — значение %s, цитатный пакет %d/%d'
                            % (root, s.get('batch_of'), s.get('batch_index', 0) + 1,
                               s.get('batch_count', 1)))
                else:
                    head = '## Простой глагол (корень {#%s#}) — значения, часть %d' % (root, s.get('part', 0) + 1)
            elif sec.startswith('pwkvn'):
                head = '## PWKVN'
            elif sec.startswith('pw'):
                head = '## PW — Böhtlingk (kürzere Fassung)'
            elif sec.startswith('sch'):
                head = '## SCH — Schmidt, Nachträge 1928'
            elif sec.startswith('nws'):
                head = '## NWS — словник источников (%s)' % sec
            else:
                head = '## Простой глагол (корень {#%s#})' % root
        elif s['kind'] == 'secondary':
            # caus./desid./intens./partic. of the SIMPLE root — its own derived stem, NOT a
            # prefixed verb. Belongs with the simple verb, never under the last prefix.
            lab = s.get('label') or s.get('section') or 'вторичная основа'
            head = '## Вторичная основа корня {#%s#}: %s' % (root, lab)
        else:
            head = '## {#%s#}-{#%s#}  (приставка %s)' % (s['upasarga'], root, s['upasarga'])
        parts.append(head)
        if os.path.exists(mdp):
            parts.append(body_of(open(mdp, encoding='utf-8').read()))
            have += 1
        else:
            parts.append('_[перевод под-карточки `%s` ещё не готов в этом сэмпле]_' % s['subkey'])
            miss += 1
        parts.append('')
    # one pipeline-provenance footer for the whole assembled card (sub-cards carry none, so
    # nothing scatters mid-document). Versions come from the current tooling; the model id
    # stays authoritative in the JSONL store.
    parts.append(pipeline_version.md_footer(pipeline_version.stamp()))
    nested = os.path.join(outdir, safe_name(root) + '.NESTED.md')
    open(nested, 'w', encoding='utf-8').write('\n'.join(parts) + '\n')
    print('glue-after-translate  %s: %d sub-cards (%d translated, %d pending) -> %s'
          % (root, len(subs), have, miss, os.path.relpath(nested, HERE)))
    return nested


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    root = sys.argv[1]
    outdir = OUT
    if '--dir' in sys.argv:
        outdir = os.path.join(HERE, sys.argv[sys.argv.index('--dir') + 1])
    glue(root, outdir)


if __name__ == '__main__':
    main()
