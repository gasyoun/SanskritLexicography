#!/usr/bin/env python
r"""nominals_worklist.py — build the RU translation worklist for a nominal core (H179).

Sibling of `verb_worklist.py`, for the nominal lexical-core tiers. Where the verb
worklist reads the vetted verb-root file and expands each root through a rootmap into
homonym/sense/prefix sub-cards, a **nominal** headword has no rootmap — it generates a
single flat card (`_pilot_gen_merged.py` accepts any headword key via `form_key`). So
this adapter is simpler: take a nominal SLP1 wordlist (produced by
`extract_lexical_cores.py`), join each word to the merged PWG headword index, order the
hits, and emit a worklist the existing runner consumes unchanged.

Verb lemmas in a core (POS='v', or present in the verbs01 verb-root universe) are NOT
queued here — they belong to the standing verb drain (H151). They are counted and set
aside so the coverage report is honest, never silently dropped.

Coverage (a hit = the form-key resolves to a PWG headword, exactly as
`_pilot_gen_merged.gen_card` looks it up). A miss = not a PWG headword under its
form-key (a different stem/homonym key, or genuinely absent). Cumulative dedup:
words already promoted into the RU store are excluded (never re-translate a lower tier's
word — mandatory per H179).

Usage:
  python src/pilot/nominals_worklist.py src/pilot/lexical_cores/pril5.slp1.txt
  python src/pilot/nominals_worklist.py .../pril5.slp1.txt --top 30
  python src/pilot/nominals_worklist.py .../pril5.slp1.txt --report src/pilot/lexical_cores/pril5.coverage.md

Writes: src/pilot/output/nominal_batch_worklist.json (gitignored, regenerable).
Optional --report writes a committed human-readable coverage table.
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(os.path.dirname(HERE))                    # RussianTranslation/
SRC = os.path.join(RT, 'src')
PREVERB = os.path.normpath(os.path.join(RT, '..', '..', 'PWG', 'verbs01', 'pwg_preverb1.txt'))
MANIFEST = os.path.join(HERE, 'output', 'scale_manifest.freq.json')
STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')
OUT = os.path.join(HERE, 'output', 'nominal_batch_worklist.json')

if SRC not in sys.path:
    sys.path.insert(0, SRC)

import corpus_gate as cg                                       # noqa: E402
import dict_merge as dm                                        # noqa: E402

CASE = re.compile(r';; Case \d+: L=\d+, k1=(\S+), k2=\S+, code=\S+,')


def read_wordlist(path):
    """-> list of SLP1 words (dedup, order preserved). Pulls POS + period_spread from
    the sibling .tsv when present (written by extract_lexical_cores.py)."""
    words, seen = [], set()
    with open(path, encoding='utf-8') as f:
        for line in f:
            w = line.strip()
            if w and w not in seen:
                seen.add(w)
                words.append(w)
    meta = {}
    tsv = re.sub(r'\.slp1\.txt$', '.tsv', path)
    if os.path.exists(tsv):
        with open(tsv, encoding='utf-8') as f:
            header = f.readline()
            for line in f:
                parts = line.rstrip('\n').split('\t')
                if len(parts) >= 4:
                    meta[parts[0]] = {'iast': parts[1], 'pos': parts[2], 'spread': int(parts[3])}
    return words, meta


def verb_universe(path=PREVERB):
    roots = set()
    if not os.path.exists(path):
        return roots
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = CASE.match(line)
            if m:
                roots.add(m.group(1))
    return roots


def store_roots(path=STORE):
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                done.add(json.loads(line).get('key1'))
    return done


def build_worklist(wordlist_path, manifest=MANIFEST, store=STORE, preverb=PREVERB):
    words, meta = read_wordlist(wordlist_path)
    freq = {it['key1']: it for it in json.load(open(manifest, encoding='utf-8'))}
    done = store_roots(store)
    verbs = verb_universe(preverb)
    pwg = dm.index('pwg')                                      # form_key -> PWG record bufs
    # The 3 other local layers a headword can carry WITHOUT a PWG record (H206, per
    # PWG_LAYER_COMBINATIONS.md / FINDINGS.md §61 — ~36% of the local union has zero
    # PWG record). Indexed here (not just via dm.merged()) so a miss can be tagged with
    # exactly which layer(s) it hit, cheaply, before any per-key merge() call.
    OTHER_LAYERS = (('pw', dm.index('pw')), ('sch', dm.index('sch')), ('pwkvn', dm.index('pwkvn')))

    core_verbs, hits, misses = [], [], []
    for w in words:
        m = meta.get(w, {})
        is_verb = (m.get('pos') == 'v') or (w in verbs)
        if is_verb:
            core_verbs.append(w)                              # -> verb drain (H151), not here
            continue
        fk = cg.form_key(w)
        rec = {'key1': w, 'form_key': fk,
               'iast': m.get('iast', ''), 'spread': m.get('spread', 0),
               'score': freq.get(w, {}).get('score'), 'band': freq.get(w, {}).get('band')}
        (hits if fk in pwg else misses).append(rec)

    # H206 fix: a "PWG miss" is NOT automatically a non-word — check the 3 other local
    # layers before writing it off. Split misses into:
    #   - other_layer_hits: real record in PW/SCH/PWKVN, tagged with which layer(s)
    #     (dropped-but-translatable candidates once the render path supports them —
    #     see BLOCKED note below).
    #   - true_misses: absent from EVERY local layer (genuinely not a CDSL word).
    # NOTE (@DECIDE, see PIPELINE_HISTORY.md): `_pilot_gen_merged.gen_card()` hard-
    # requires a non-empty PWG buf (`if not pwg_bufs: return None`) — the PWG portrait/
    # microstructure step (`microstructure.portrait()`) is written against the PWG
    # record shape specifically. There is currently NO card-building path for a
    # PW/SCH/PWKVN-only headword, so `other_layer_hits` are surfaced here (tagged,
    # counted, reported) but are deliberately NOT added to `runnable_remaining` — doing
    # so would queue keys the existing runner cannot render, not fix the drop. They are
    # promoted into the runnable queue only once that render-path gap is resolved.
    other_layer_hits, true_misses = [], []
    for r in misses:
        fk = r['form_key']
        layers = [code for code, idx in OTHER_LAYERS if fk in idx]
        if layers:
            r2 = dict(r)
            r2['other_layers'] = layers
            other_layer_hits.append(r2)
        else:
            true_misses.append(r)

    promoted = [h for h in hits if h['key1'] in done]
    remaining = [h for h in hits if h['key1'] not in done]

    # Order: DCS composite score desc where present; unscored fall to the back ranked by
    # Leonchenko period-spread desc, then alpha. Deterministic total order.
    def sort_key(r):
        has = r['score'] is not None
        return (0 if has else 1, -(r['score'] or 0), -r['spread'], r['key1'])
    remaining.sort(key=sort_key)

    return {
        'source': os.path.relpath(wordlist_path, RT).replace('\\', '/'),
        'total_lemmas': len(words),
        'core_verbs_deferred_to_H151': sorted(core_verbs),
        'core_verbs_count': len(core_verbs),
        'nominal_candidates': len(hits) + len(misses),
        'pwg_hits': len(hits),
        'pwg_misses': len(misses),
        'miss_keys': [r['key1'] for r in misses],
        # H206: misses split by whether they carry a real record in another local
        # layer. `other_layer_hits` are BLOCKED from `runnable_remaining` pending the
        # gen_card() no-PWG render-path gap (see @DECIDE note above / PIPELINE_HISTORY.md)
        # — surfaced here so they are visible and re-promotable the moment that gap
        # closes, instead of silently vanishing into the undifferentiated miss count.
        'other_layer_hit_count': len(other_layer_hits),
        'other_layer_hits': [{'key1': r['key1'], 'iast': r['iast'], 'layers': r['other_layers']}
                              for r in other_layer_hits],
        'true_miss_count': len(true_misses),
        'true_miss_keys': [r['key1'] for r in true_misses],
        'already_promoted': sorted(h['key1'] for h in promoted),
        'already_promoted_count': len(promoted),
        'runnable_remaining': [r['key1'] for r in remaining],
        'runnable_count': len(remaining),
        'runnable_detail': remaining,
        'coverage_pct': round(100.0 * len(hits) / max(1, len(hits) + len(misses)), 1),
    }


def write_report(payload, path):
    src = payload['source']
    lines = []
    lines.append('# Nominal core coverage — %s' % src)
    lines.append('')
    lines.append('_Auto-generated by `src/pilot/nominals_worklist.py --report`._')
    lines.append('')
    lines.append('| metric | count |')
    lines.append('|---|---:|')
    lines.append('| total lemmas in core | %d |' % payload['total_lemmas'])
    lines.append('| core verbs → verb drain (H151) | %d |' % payload['core_verbs_count'])
    lines.append('| nominal candidates | %d |' % payload['nominal_candidates'])
    lines.append('| PWG hits | %d |' % payload['pwg_hits'])
    lines.append('| PWG misses | %d |' % payload['pwg_misses'])
    lines.append('| — of which real in PW/SCH/PWKVN (H206, BLOCKED, see below) | %d |'
                 % payload['other_layer_hit_count'])
    lines.append('| — of which true misses (absent from every local layer) | %d |'
                 % payload['true_miss_count'])
    lines.append('| nominal coverage | %.1f%% |' % payload['coverage_pct'])
    lines.append('| already promoted (cumulative dedup) | %d |' % payload['already_promoted_count'])
    lines.append('| **runnable (to translate)** | **%d** |' % payload['runnable_count'])
    lines.append('')
    lines.append('## Top 40 runnable (score desc, period-spread tiebreak)')
    lines.append('')
    lines.append('| # | key1 | IAST | DCS score | band | period-spread |')
    lines.append('|---:|---|---|---:|---:|---:|')
    for i, r in enumerate(payload['runnable_detail'][:40], 1):
        lines.append('| %d | %s | %s | %s | %s | %d |'
                     % (i, r['key1'], r['iast'],
                        '%.1f' % r['score'] if r['score'] is not None else '—',
                        r['band'] if r['band'] is not None else '—', r['spread']))
    lines.append('')
    if payload['other_layer_hits']:
        lines.append('## PWG misses WITH a real PW/SCH/PWKVN record (%d) — H206, BLOCKED pending render-path fix'
                     % payload['other_layer_hit_count'])
        lines.append('')
        lines.append('These lemmas have NO PWG headword under their `form_key` but DO have a real record')
        lines.append('in another local layer — dropped-but-translatable, not non-words. They are NOT yet')
        lines.append('in `runnable_remaining`: `_pilot_gen_merged.gen_card()` hard-requires a non-empty PWG')
        lines.append('buf and returns `None` otherwise, so today\'s runner cannot build a card for a')
        lines.append('PW/SCH/PWKVN-only headword. See `PIPELINE_HISTORY.md` and the standing `@DECIDE`.')
        lines.append('')
        lines.append('| key1 | IAST | layer(s) |')
        lines.append('|---|---|---|')
        for r in payload['other_layer_hits']:
            lines.append('| %s | %s | %s |' % (r['key1'], r['iast'], '/'.join(r['layers'])))
        lines.append('')
    if payload['true_miss_keys']:
        lines.append('## True misses (%d) — absent from every local layer' % payload['true_miss_count'])
        lines.append('')
        lines.append('These are core lemmas whose `form_key` resolves to NO local layer (PWG, PW, SCH,')
        lines.append('or PWKVN) — a different stem/homonym key, or genuinely absent. Review before')
        lines.append('assuming a gap.')
        lines.append('')
        lines.append('> ' + ', '.join(payload['true_miss_keys']))
        lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('wordlist', help='path to an SLP1 wordlist (one lemma per line)')
    ap.add_argument('--top', type=int, default=0, help='print the next N runnable nominals')
    ap.add_argument('--report', help='also write a committed coverage markdown to this path')
    ap.add_argument('--json', action='store_true', help='print the full worklist JSON to stdout')
    args = ap.parse_args()

    payload = build_worklist(args.wordlist)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    print('%s: %d lemmas | verbs->H151: %d | nominals: %d (hits %d / miss %d, %.1f%% cov) | '
          'promoted: %d | RUNNABLE: %d'
          % (payload['source'], payload['total_lemmas'], payload['core_verbs_count'],
             payload['nominal_candidates'], payload['pwg_hits'], payload['pwg_misses'],
             payload['coverage_pct'], payload['already_promoted_count'], payload['runnable_count']))
    if payload['other_layer_hit_count']:
        print('  H206: %d of those misses have a real PW/SCH/PWKVN record (BLOCKED from RUNNABLE — '
              'see @DECIDE in PIPELINE_HISTORY.md); %d are true misses (absent everywhere)'
              % (payload['other_layer_hit_count'], payload['true_miss_count']))
    print('worklist written: %s' % OUT)
    if args.report:
        write_report(payload, args.report)
        print('coverage report written: %s' % args.report)
    if args.top:
        print('top %d runnable nominals:' % min(args.top, payload['runnable_count']))
        for r in payload['runnable_detail'][:args.top]:
            sc = '%.1f' % r['score'] if r['score'] is not None else '—'
            print('  %-14s score=%s band=%s spread=%d' % (r['key1'], sc, r['band'], r['spread']))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
