#!/usr/bin/env python
"""nominal_style.py — verify Renou's "style nominal" thesis on the DCS corpus.

Renou's central diachronic claim (Histoire de la langue sanskrite, esp. chap. IV) is that
Sanskrit progressively replaces the **personal/finite verb** with a **nominal style** —
action-nouns (-ana, -ti, -tā/-tva), participles, long compounds — and that this nominalisation
is most extreme in the śāstra/sūtra/bhāṣya registers ("l'aspect en a été durci par le long
entraînement au genre sūtra, par l'accentuation du style nominal", p. 133).

That claim is about *running text*, not headwords, so it is testable on the DCS corpus
(CoNLL-U, UPOS + VerbForm). The decisive measure is **finite-verb density** = share of
tokens that are finite verbs (UPOS=VERB & VerbForm=Fin). Renou predicts it (a) falls across
the states I→IV, and (b) is lowest in sūtra / bhāṣya / vyākaraṇa, higher in epic / kāvya.

Reuses build_dcs_renou.build_text_states() for the text→state / text→register typing, then
scans each text's CoNLL-U for the morphological counts.

  python nominal_style.py            # state + register tables (corpus-weighted)
  python nominal_style.py --texts    # per-text finite-verb density (spot-check)
"""
import os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import build_dcs_renou as bdr

STATES = ('I', 'II', 'III', 'IV', 'V')


def count_file(path):
    """(tokens, finite, part, conv, noun, adj) for one CoNLL-U file."""
    tok = fin = part = conv = noun = adj = 0
    with open(path, encoding='utf-8') as f:
        for line in f:
            if not line or line[0] in '#\n':
                continue
            c = line.split('\t')
            if len(c) < 6 or not c[0].isdigit():
                continue
            tok += 1
            upos, feats = c[3], c[5]
            if upos == 'NOUN':
                noun += 1
            elif upos == 'ADJ':
                adj += 1
            if upos in ('VERB', 'AUX'):
                # DCS marks finite verbs by Mood=/Person= (no VerbForm); non-finite
                # carry VerbForm=Part / Conv / Inf / Gdv.
                if 'VerbForm=Part' in feats:
                    part += 1
                elif 'VerbForm=' in feats:        # Conv (absolutive) / Inf / Gdv
                    conv += 1
                elif 'Mood=' in feats or 'Person=' in feats:
                    fin += 1
    return tok, fin, part, conv, noun, adj


def scan():
    texts = bdr.build_text_states()
    FILES = bdr.FILES
    per_text = {}
    names = sorted(d for d in os.listdir(FILES) if os.path.isdir(os.path.join(FILES, d)))
    for i, name in enumerate(names):
        d = os.path.join(FILES, name)
        agg = [0, 0, 0, 0, 0, 0]
        for fn in os.listdir(d):
            if fn.endswith('.conllu'):
                for j, v in enumerate(count_file(os.path.join(d, fn))):
                    agg[j] += v
        per_text[name] = agg
        if (i + 1) % 50 == 0:
            print('  scanned %d/%d texts' % (i + 1, len(names)), file=sys.stderr)
    return texts, per_text


def agg_by(texts, per_text, key):
    """key(textmeta) -> list of keys; returns {k: [tok,fin,part,conv,noun,adj,n_texts]}."""
    out = collections.defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0])
    for name, meta in texts.items():
        if name not in per_text:
            continue
        for k in key(meta):
            row = out[k]
            for j in range(6):
                row[j] += per_text[name][j]
            row[6] += 1
    return out


def pct(a, b):
    return 100.0 * a / b if b else 0.0


def report(texts, per_text):
    def line(label, r):
        tok, fin, part, conv, noun, adj, n = r
        if not tok:
            return
        print('%-12s %3d texts  fin %5.2f%%  part %5.2f%%  conv %4.2f%%  '
              'noun+adj %5.1f%%  (%d tok)'
              % (label, n, pct(fin, tok), pct(part, tok), pct(conv, tok),
                 pct(noun + adj, tok), tok))

    print('=== finite-verb density by Renou STATE (corpus-weighted) ===')
    by_s = agg_by(texts, per_text, lambda m: [m['renou']] if m['renou'] else [])
    for s in STATES:
        if s in by_s:
            line(s, by_s[s])

    print('\n=== finite-verb density by REGISTER (corpus-weighted) ===')
    by_r = agg_by(texts, per_text, lambda m: list((m.get('registers') or {}).keys()))
    for r, row in sorted(by_r.items(), key=lambda kv: pct(kv[1][1], kv[1][0])):
        line(r, row)


def report_texts(texts, per_text):
    rows = []
    for name, meta in texts.items():
        if name in per_text and per_text[name][0] >= 500:
            rows.append((pct(per_text[name][1], per_text[name][0]), name,
                         meta['renou'], per_text[name][0]))
    rows.sort()
    print('=== per-text finite-verb %% (≥500 tok), lowest first ===')
    for fv, name, st, tok in rows[:15] + [('...',) * 4] + rows[-10:]:
        if fv == '...':
            print('  ...'); continue
        print('  %5.2f%%  [%s] %-45s %d tok' % (fv, st or '?', name[:45], tok))


def main():
    texts, per_text = scan()
    if '--texts' in sys.argv:
        report_texts(texts, per_text)
    else:
        report(texts, per_text)


if __name__ == '__main__':
    main()
