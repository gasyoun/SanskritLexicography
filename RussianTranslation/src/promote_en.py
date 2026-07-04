#!/usr/bin/env python
r"""promote_en.py — attach EN translations onto the RU store, making it tri-lingual (de+ru+en).

The RU bridge (promote_final_cards.py) writes one store row per sense from the RU wf_output
files: each row carries `de` (German source) + `ru` (Russian) + provenance. The EN track lives
separately in per-root wf_output.en.<root>.json (per-sense `english`). This script JOINS them:
for every store row it finds the matching EN sense and attaches an `en` field plus an
`en_provenance` block, leaving the row otherwise untouched. The result is a single store carrying
de + ru + en per sense.

en_provenance (FU1 locked decision 5 — full per-sense provenance) records, alongside the plain-
string `en`:
  {model:'sonnet',                         # generation tier ALIAS (gen_opt_harness2 pins it)
   model_version:'claude-sonnet-4-6',      # the VERSION the alias resolved to — record it, models change
   judge: {model:'opus', model_version:'claude-opus-4-8', ok, severity, verdict, note} | null,  # via --judge
   generated_at, rootmap_sha256,           # from the EN wf_output meta (reproducibility anchors)
   input_sha256,                           # the sub-card's masked-input raw_sha256 (meta.input_hashes)
   mw_used: null}                          # MW-TM usage is not recorded per-sense in wf_output
The wf_output meta does NOT carry the resolved model version, so it is set here (defaults =
GEN_MODEL_VERSION / JUDGE_MODEL_VERSION); override per run with --gen-model-version /
--judge-model-version if the alias mapping changed.
`en` stays a plain string so export_interop.py is unaffected; en_provenance is a sibling field.

Join key — why not (subkey, sense_tag) or position:
  RU and EN are INDEPENDENT generation runs over the same masked PWG skeleton, so they do NOT
  agree on sense tags ('1-sub-einen Damm durchbrechen' vs '1-dam') NOR on sense segmentation
  (one run may split a sense the other merged). The one stable anchor is the German source text
  each sense carries verbatim. So the join is, within a sub-card:
    1. exact match on the normalized German (whitespace/punctuation-insensitive), else
    2. a difflib fuzzy match above --threshold (default 0.92), unambiguous by a margin, else
    3. leave `en` ABSENT — never fabricate a translation onto a row we could not match.

review_status is NOT changed (stays 'ai_translated' — the G5 gate). Run annotate_dcs_freq.py
AFTER this (it is language-agnostic and idempotent) to (re)attach the dcs_freq block.

  python src/promote_en.py                      # attach EN + en_provenance -> store
  python src/promote_en.py --dry-run            # report coverage, write nothing
  python src/promote_en.py --glob 'wf_output.en.pat.json'   # a subset
  python src/promote_en.py --judge verdicts.json            # fold Opus judge verdict into provenance
  python src/promote_en.py --selftest
"""
import argparse
import difflib
import glob
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
DEFAULT_GLOB = 'wf_output.en.*.json'
_KEEP = re.compile(r'[^0-9A-Za-z{}#%]')

# Tier + VERSION must both be recorded (models change — a bare 'sonnet'/'opus' is ambiguous later).
# The harness pins the ALIAS model:'sonnet'/'opus'; the wf_output meta does NOT capture the resolved
# version, so we record it here. These defaults are the versions the aliases resolved to for the
# FU1 run (2026-06-30); override per run with --gen-model-version / --judge-model-version if the
# alias mapping has changed since.
GEN_MODEL_VERSION = 'claude-sonnet-4-6'      # alias 'sonnet' -> Sonnet 4.6
JUDGE_MODEL_VERSION = 'claude-opus-4-8'      # alias 'opus'   -> Opus 4.8


def norm_de(g):
    """Whitespace/punctuation-insensitive key for the German source skeleton. Keeps alnum and
    the span markers ({}, #, %) so two senses differing only by a stray comma / newline / tag
    spacing between the two runs collapse to the same key, but distinct glosses stay distinct."""
    if not g:
        return ''
    return _KEEP.sub('', re.sub(r'\s+', ' ', g))


def load_wf(path):
    with open(path, encoding='utf-8') as f:
        wrapper = json.load(f)
    result = wrapper.get('result')
    if isinstance(result, str):
        result = json.loads(result)
    if result is None:
        result = wrapper
    return result


def en_index(paths, gen_model_version=GEN_MODEL_VERSION):
    """Returns (idx, prov):
      idx[sub]  = list of (norm_de, english) for every non-empty EN sense, in card order.
      prov[sub] = base provenance dict for that sub-card (model tier + model_version,
                  generated_at, rootmap_sha256, input_sha256, mw_used) — judge folded in by
                  attach(). model = the alias the harness pinned; model_version = what it resolved
                  to (recorded explicitly because the wf_output meta does not carry it)."""
    idx = defaultdict(list)
    prov = {}
    for path in paths:
        try:
            res = load_wf(path)
        except (OSError, json.JSONDecodeError) as e:
            print('  skip (unreadable): %s (%s)' % (os.path.basename(path), e))
            continue
        meta = res.get('meta') or {}
        generated_at = meta.get('generated_at')
        rootmap_sha256 = meta.get('rootmap_sha256')
        input_hashes = meta.get('input_hashes') or {}
        for r in res.get('results') or []:
            sub, card = r.get('key'), r.get('card')
            if not sub or not card:
                continue
            for rec in card.get('records') or []:
                for s in rec.get('senses') or []:
                    e = s.get('english')
                    if e and e.strip():
                        idx[sub].append((norm_de(s.get('german')), e))
            if sub in idx and sub not in prov:
                ih = input_hashes.get(sub) or {}
                prov[sub] = {
                    'model': 'sonnet',                 # alias the harness pinned
                    'model_version': gen_model_version,  # what it resolved to (e.g. claude-sonnet-4-6)
                    'judge': None,
                    'generated_at': generated_at,
                    'rootmap_sha256': rootmap_sha256,
                    'input_sha256': ih.get('raw_sha256'),
                    'mw_used': None,
                }
    return idx, prov


def load_judge(path, judge_model_version=JUDGE_MODEL_VERSION):
    """Opus judge verdicts (JSON {verdicts:[...]}/array/JSONL) -> sub-card key -> judge block.
    Records both the alias ('opus') and the resolved model_version (e.g. claude-opus-4-8)."""
    txt = open(path, encoding='utf-8').read().strip()
    try:
        obj = json.loads(txt)
        if isinstance(obj, dict):
            obj = obj.get('verdicts') or obj.get('results') or []
    except json.JSONDecodeError:
        obj = [json.loads(l) for l in txt.splitlines() if l.strip()]
    out = {}
    for v in obj:
        key = v.get('key') or v.get('key1')
        if not key:
            continue
        ok = v.get('ok', True)
        sev = int(v.get('severity', 0))
        out[key] = {'model': 'opus', 'model_version': judge_model_version,
                    'ok': ok, 'severity': sev,
                    'verdict': 'ok' if (ok and sev < 3) else 'bad',
                    'note': v.get('note', '')}
    return out


def match_en(de_key, candidates, threshold):
    """candidates: list of (norm_de, english) for the row's sub-card. Returns (english, how)
    or (None, reason)."""
    if not candidates:
        return None, 'no-en-sense'
    exact = [e for k, e in candidates if k and k == de_key]
    if len(exact) == 1:
        return exact[0], 'exact'
    if len(exact) > 1:
        return exact[0], 'exact-ambiguous'      # identical German repeated; first is as good
    if not de_key:
        return None, 'no-de-key'
    scored = sorted(
        ((difflib.SequenceMatcher(None, de_key, k).ratio(), e) for k, e in candidates if k),
        key=lambda x: x[0], reverse=True)
    if not scored or scored[0][0] < threshold:
        return None, 'below-threshold'
    if len(scored) > 1 and (scored[0][0] - scored[1][0]) < 0.02:
        return None, 'fuzzy-ambiguous'
    return scored[0][1], 'fuzzy'


def attach(rows, idx, threshold, prov=None, judge=None):
    prov = prov or {}
    judge = judge or {}
    stats = defaultdict(int)
    for r in rows:
        sub = r.get('subcard')
        r.pop('en', None)                         # idempotent re-run
        r.pop('en_provenance', None)
        if sub not in idx:
            stats['no-en-file'] += 1
            continue
        en, how = match_en(norm_de(r.get('de')), idx[sub], threshold)
        stats[how] += 1
        if en is not None:
            r['en'] = en
            block = dict(prov.get(sub) or {'model': 'sonnet', 'judge': None})
            if sub in judge:
                block['judge'] = judge[sub]
                stats['judged'] += 1
            r['en_provenance'] = block
            stats['attached'] += 1
    return stats


def selftest():
    rows = [
        {'subcard': 'p_a~~h0', 'sense_tag': '1', 'de': 'trinken', 'ru': 'пить'},
        {'subcard': 'p_a~~h0', 'sense_tag': '2', 'de': '<ab>Caus.</ab>, schützen', 'ru': 'защищать'},
        {'subcard': 'p_a~~h0', 'sense_tag': '3', 'de': 'ganz anderes', 'ru': 'иное'},
        {'subcard': 'zzz~~h9', 'sense_tag': '1', 'de': 'x', 'ru': 'ы'},   # no EN file
    ]
    # EN card: tag differs ('a'), German has a stray comma diff on sense 2 (fuzzy), no sense 3.
    idx = {'p_a~~h0': [
        (norm_de('trinken'), 'to drink'),
        (norm_de('<ab>Caus.</ab> schützen'), 'to protect'),
    ]}
    prov = {'p_a~~h0': {'model': 'sonnet', 'model_version': 'claude-sonnet-4-6', 'judge': None,
                        'generated_at': '2026-06-30T00:00:00Z', 'rootmap_sha256': 'deadbeef',
                        'input_sha256': 'cafe', 'mw_used': None}}
    judge = {'p_a~~h0': {'model': 'opus', 'model_version': 'claude-opus-4-8', 'ok': True,
                         'severity': 1, 'verdict': 'ok', 'note': 'fine'}}
    stats = attach(rows, idx, 0.92, prov=prov, judge=judge)
    assert rows[0].get('en') == 'to drink', 'exact German match'
    assert rows[1].get('en') == 'to protect', 'fuzzy German match across comma diff'
    assert 'en' not in rows[2], 'unmatched sense must be left absent, not fabricated'
    assert 'en' not in rows[3], 'row whose sub-card has no EN file stays EN-absent'
    assert rows[0]['ru'] == 'пить' and rows[0]['de'] == 'trinken', 'ru/de untouched'
    assert stats['attached'] == 2
    # provenance attached, en stays a plain string, judge folded in
    assert isinstance(rows[0].get('en'), str), 'en stays a plain string (export_interop unaffected)'
    p0 = rows[0].get('en_provenance')
    assert p0 and p0['model'] == 'sonnet' and p0['input_sha256'] == 'cafe', 'en_provenance attached'
    assert p0['model_version'] == 'claude-sonnet-4-6', 'gen model VERSION recorded (not just tier)'
    assert p0['judge'] and p0['judge']['model'] == 'opus' and p0['judge']['verdict'] == 'ok', 'judge folded'
    assert p0['judge']['model_version'] == 'claude-opus-4-8', 'judge model VERSION recorded'
    assert 'en_provenance' not in rows[2], 'no provenance on unmatched rows'
    # idempotent re-run without judge clears the stale judge block
    attach(rows, idx, 0.92, prov=prov)
    assert rows[0]['en_provenance']['judge'] is None, 're-run without --judge resets judge to null'
    print('promote_en selftest OK')


def main():
    if '--selftest' in sys.argv[1:]:
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument('--glob', default=DEFAULT_GLOB, help='EN wf_output glob, relative to repo root')
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--threshold', type=float, default=0.92,
                    help='minimum difflib ratio for a fuzzy German match (default 0.92)')
    ap.add_argument('--judge', default=None,
                    help='Opus EN-judge verdicts (JSON/JSONL) to fold into en_provenance.judge')
    ap.add_argument('--gen-model-version', default=GEN_MODEL_VERSION,
                    help='resolved generation model version recorded in en_provenance.model_version '
                         '(default %(default)s — the alias the harness pinned resolved to)')
    ap.add_argument('--judge-model-version', default=JUDGE_MODEL_VERSION,
                    help='resolved judge model version recorded in en_provenance.judge.model_version '
                         '(default %(default)s)')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-backup', action='store_true')
    args = ap.parse_args()

    if not os.path.exists(args.store):
        sys.exit('no RU store at %s — run promote_final_cards.py first' % args.store)
    paths = sorted(glob.glob(os.path.join(ROOT, args.glob)))
    if not paths:
        sys.exit('no EN wf_output files matched %s under %s' % (args.glob, ROOT))
    print('store: %s' % os.path.relpath(args.store, ROOT))
    print('ingesting %d EN wf_output file(s)' % len(paths))

    rows = [json.loads(l) for l in open(args.store, encoding='utf-8') if l.strip()]
    idx, prov = en_index(paths, gen_model_version=args.gen_model_version)
    print('gen model: sonnet (%s)' % args.gen_model_version)
    judge = load_judge(args.judge, judge_model_version=args.judge_model_version) if args.judge else None
    if args.judge:
        print('judge verdicts: %d (from %s); judge model: opus (%s)'
              % (len(judge), os.path.basename(args.judge), args.judge_model_version))
    en_senses = sum(len(v) for v in idx.values())
    stats = attach(rows, idx, args.threshold, prov=prov, judge=judge)

    eligible = len(rows) - stats['no-en-file']
    print('\n=== EN MERGE COVERAGE ===')
    print('store rows              : %d' % len(rows))
    print('EN sub-cards / senses   : %d / %d' % (len(idx), en_senses))
    print('rows with EN sub-card   : %d' % eligible)
    print('  en attached           : %d (exact %d, exact-ambig %d, fuzzy %d)' % (
        stats['attached'], stats['exact'], stats['exact-ambiguous'], stats['fuzzy']))
    if args.judge:
        print('  with opus judge block : %d' % stats['judged'])
    print('  unmatched (left absent): %d (below-threshold %d, fuzzy-ambig %d, no-en-sense %d, no-de-key %d)' % (
        stats['below-threshold'] + stats['fuzzy-ambiguous'] + stats['no-en-sense'] + stats['no-de-key'],
        stats['below-threshold'], stats['fuzzy-ambiguous'], stats['no-en-sense'], stats['no-de-key']))
    print('rows with no EN file yet: %d (roots beyond the EN run — EN absent, expected)' % stats['no-en-file'])

    if args.dry_run:
        print('\n(dry run — store not written)')
        return
    if not args.no_backup:
        bak = args.store + '.preEN.bak'
        with open(bak, 'w', encoding='utf-8') as f, open(args.store, encoding='utf-8') as src:
            f.write(src.read())
        print('\nbacked up store -> %s' % os.path.basename(bak))
    # Atomic write: temp file + os.replace so a crash/kill mid-write cannot truncate
    # the tri-lingual store (the "EN layer wiped" scar). Under --no-backup this is the
    # ONLY thing standing between an interrupted write and total loss.
    tmp = args.store + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    os.replace(tmp, args.store)
    print('wrote tri-lingual store -> %s (%d rows, %d now carry en)'
          % (os.path.relpath(args.store, ROOT), len(rows), stats['attached']))
    print('NEXT: re-run `python src/annotate_dcs_freq.py` to (re)attach the dcs_freq block.')


if __name__ == '__main__':
    main()
