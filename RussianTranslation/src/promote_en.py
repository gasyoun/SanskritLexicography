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
import datetime
import difflib
import glob
import json
import os
import re
import sys
import uuid
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pipeline_version
from promote_lock import PromoteClaim, ClaimBusy
from store_path import canonical_store
# C6/C9/P9 + H2224 OPT-1: reuse the RU lane's EXACT guards (single source — a look-alike copy
# is precisely the drift that C3 was). TN_RE + UnrestoredPlaceholder refuse a card with an
# unrestored {Tn} placeholder; _fsynced_backup is the O_EXCL fsynced copier so an EN backup can
# never overwrite a recovery copy; _atomic_write_rows is the fsync-before-replace store writer
# (H1421 P9). B08/B20/H1553 twins: model_tier, defect-key helpers, PromotionContractError —
# EN remains attach-overlay (not a full RU promote clone).
from promote_final_cards import (
    TN_RE, UnrestoredPlaceholder, PromotionContractError,
    _fsynced_backup, _atomic_write_rows, model_tier,
    load_defect_keys, discover_defect_keys_path, refuse_defect_keys,
    clean_keys_from_report)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# Resolve the PERSISTENT store (parity with promote_final_cards.py): an EN-attach run in an
# isolated `git worktree` must rewrite the MAIN checkout's store, not a discarded worktree copy
# (the H255 w06 loss vector). See store_path.canonical_store.
DEFAULT_STORE = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))
DEFAULT_GLOB = 'wf_output.en.*.json'
_KEEP = re.compile(r'[^0-9A-Za-z{}#%]')

# Tier + VERSION must both be recorded (models change — a bare 'sonnet'/'opus' is ambiguous later).
# The harness pins the ALIAS model:'sonnet'/'opus'; the wf_output meta does NOT capture the resolved
# version, so we record it here. These defaults are the versions the aliases resolved to for the
# FU1 run (2026-06-30); override per run with --gen-model-version / --judge-model-version if the
# alias mapping has changed since.
GEN_MODEL_VERSION = 'claude-sonnet-4-6'      # alias 'sonnet' -> Sonnet 4.6
JUDGE_MODEL_VERSION = 'claude-opus-4-8'      # alias 'opus'   -> Opus 4.8


def _en_backup_path(store):
    """C9: a collision-resistant `.preEN` backup name — microsecond stamp + pid + uuid, so two
    lock-serialized runs in the SAME second get distinct names (second-resolution collided, and a
    plain open('w') then clobbered the earlier recovery copy). Paired with _fsynced_backup's
    O_EXCL open so an existing backup is never overwritten. Mirrors promote_final_cards._backup_path."""
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    return '%s.preEN.%s.p%d.%s.bak' % (store, stamp, os.getpid(), uuid.uuid4().hex[:12])


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
                  attach(). model = tier derived from gen_model_version (B20 / model_tier);
                  model_version = the exact id the operator sealed.

    B20 (H1339 / H2224): when meta.execution.model_identifier is present, it must equal
    gen_model_version or PromotionContractError is raised (same refuse as RU promote).
    """
    idx = defaultdict(list)
    prov = {}
    tier = model_tier(gen_model_version)
    for path in paths:
        try:
            res = load_wf(path)
        except (OSError, json.JSONDecodeError) as e:
            print('  skip (unreadable): %s (%s)' % (os.path.basename(path), e))
            continue
        meta = res.get('meta') or {}
        # B20: operator --gen-model-version must match the sealed execution identity when present.
        exec_model = ((meta.get('execution') or {}).get('model_identifier'))
        if exec_model and exec_model != gen_model_version:
            raise PromotionContractError(
                '%s: --gen-model-version %r does not match the manifest '
                'execution.model_identifier %r' % (
                    os.path.basename(path), gen_model_version, exec_model))
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
                    # B20 twin: derive tier from the sealed version (never hardcode 'sonnet').
                    'model': tier,
                    'model_version': gen_model_version,
                    'judge': None,
                    'generated_at': generated_at,
                    'rootmap_sha256': rootmap_sha256,
                    'input_sha256': ih.get('raw_sha256'),
                    'mw_used': None,
                    # semver of OUR tooling at promotion time — orthogonal to model_version;
                    # mirrors provenance.pipeline on the RU side (promote_final_cards.py) so a
                    # later bugfix can flag which EN rows predate it too (pipeline_version.py).
                    'pipeline': pipeline_version.stamp(model_version=gen_model_version),
                }
                # Partial-card marker — needed for B08 better-attempt ranking against store EN.
                partial = card.get('partial') or r.get('partial')
                if partial:
                    prov[sub]['partial_card'] = True
                    for m in ('missing_fragments', 'missing_groups', 'total_groups'):
                        if card.get(m) is not None:
                            prov[sub][m] = card[m]
                # H1226: carry the pre-restore {Tn} pairing accept() stamped on the card (shared
                # harness -> EN cards get it too), so a TNMASK expansion is measurable offline from
                # an EN promoted row as well — parity with the RU lane (promote_final_cards.py). The
                # generation-side stamping is SHARED across languages; consuming it in only one lane
                # would be a real GAP. Additive, backward-compatible, carried only when well-formed.
                tnmask = card.get('tnmask')
                if (isinstance(tnmask, dict)
                        and isinstance(tnmask.get('got'), str)
                        and isinstance(tnmask.get('want'), str)):
                    prov[sub]['tnmask'] = {'got': tnmask['got'], 'want': tnmask['want']}
    return idx, prov


def _en_attempt_quality(en_prov):
    """Rank one EN attach attempt for better-attempt-wins (B08 twin of RU _attempt_quality).

    (complete, -missing): a complete EN provenance (no partial_card) beats any partial;
    among partials, fewer missing fragments/groups beat more. Ties favour INCOMING
    (deliberate retranslation replaces same-quality EN).
    """
    prov = en_prov or {}
    partial = bool(prov.get('partial_card'))
    missing = 0
    mf = prov.get('missing_fragments')
    if isinstance(mf, list):
        missing = len(mf)
    else:
        missing = int(prov.get('missing_groups') or 0)
    return (0 if partial else 1, -missing)


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
    """Attach EN + en_provenance onto store rows (join on German).

    B08 (H1339 / H2224): better-attempt-wins — when a row already carries `en` whose
    en_provenance ranks strictly better than the incoming attempt, keep the store EN
    (do not silently downgrade a complete attach with a partial re-run). Ties favour
    incoming (deliberate retranslation). Rows with no EN match keep any prior `en`
    (only a successful attach replaces).
    """
    prov = prov or {}
    judge = judge or {}
    stats = defaultdict(int)
    for r in rows:
        sub = r.get('subcard')
        existing_en = r.get('en')
        existing_prov = r.get('en_provenance')
        if sub not in idx:
            stats['no-en-file'] += 1
            continue
        en, how = match_en(norm_de(r.get('de')), idx[sub], threshold)
        stats[how] += 1
        if en is not None:
            # C6: parity with promote_final_cards' RU-side C-01 guard — never write a card still
            # carrying a {Tn} mask placeholder into the canonical store.
            if TN_RE.search(en):
                raise UnrestoredPlaceholder(
                    '%s: refusing to promote an EN sense with an unrestored placeholder: %r'
                    % (sub, en[:80]))
            block = dict(prov.get(sub) or {
                'model': model_tier(GEN_MODEL_VERSION), 'judge': None})
            if sub in judge:
                block['judge'] = judge[sub]
                stats['judged'] += 1
            # B08: store keeps a strictly better existing EN attempt.
            if (existing_en is not None
                    and _en_attempt_quality(block)
                    < _en_attempt_quality(existing_prov)):
                stats['better-attempt-kept'] += 1
                # leave r['en'] / r['en_provenance'] untouched
                continue
            r['en'] = en
            r['en_provenance'] = block
            stats['attached'] += 1
        # unmatched: leave any prior en in place (no wipe on partial re-run)
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
                        'input_sha256': 'cafe', 'mw_used': None,
                        'pipeline': pipeline_version.stamp(model_version='claude-sonnet-4-6')}}
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
    assert p0.get('pipeline') and p0['pipeline'].get('schema') == pipeline_version.PIPELINE_SCHEMA, \
        'en_provenance carries a pipeline stamp, mirroring the RU side'
    assert p0['judge'] and p0['judge']['model'] == 'opus' and p0['judge']['verdict'] == 'ok', 'judge folded'
    assert p0['judge']['model_version'] == 'claude-opus-4-8', 'judge model VERSION recorded'
    assert 'en_provenance' not in rows[2], 'no provenance on unmatched rows'
    # re-run without judge replaces with fresh block (judge null); same-quality → incoming wins
    attach(rows, idx, 0.92, prov=prov)
    assert rows[0]['en_provenance']['judge'] is None, 're-run without --judge resets judge to null'
    # C6: an EN candidate still carrying a {Tn} mask placeholder must be REFUSED (parity with the
    # RU C-01 UnrestoredPlaceholder guard), never written into the tri-lingual store.
    bad_rows = [{'subcard': 'p_a~~h0', 'sense_tag': '1', 'de': 'trinken', 'ru': 'пить'}]
    bad_idx = {'p_a~~h0': [(norm_de('trinken'), 'to drink from a {T3}')]}
    try:
        attach(bad_rows, bad_idx, 0.92)
        assert False, 'C6: a {Tn} residue in the EN candidate must be refused, not attached'
    except UnrestoredPlaceholder:
        pass
    assert 'en' not in bad_rows[0], 'C6: a refused row must carry no partial EN'
    # B08 (H2224): better-attempt-wins — store complete EN must not be downgraded by a partial.
    store_row = {
        'subcard': 'p_a~~h0', 'sense_tag': '1', 'de': 'trinken', 'ru': 'пить',
        'en': 'to drink (complete)',
        'en_provenance': {'model': 'sonnet', 'model_version': 'claude-sonnet-4-6',
                          'judge': None},  # complete (no partial_card)
    }
    partial_prov = {
        'p_a~~h0': {
            'model': 'sonnet', 'model_version': 'claude-sonnet-4-6', 'judge': None,
            'partial_card': True, 'missing_groups': 2,
        }
    }
    partial_idx = {'p_a~~h0': [(norm_de('trinken'), 'to drink (partial)')]}
    st = attach([store_row], partial_idx, 0.92, prov=partial_prov)
    assert store_row['en'] == 'to drink (complete)', 'B08: complete store EN beats partial incoming'
    assert st['better-attempt-kept'] == 1
    # equal quality → incoming wins (deliberate retranslation)
    eq_row = {
        'subcard': 'p_a~~h0', 'sense_tag': '1', 'de': 'trinken', 'ru': 'пить',
        'en': 'old complete',
        'en_provenance': {'model': 'sonnet', 'model_version': 'claude-sonnet-4-6'},
    }
    attach([eq_row], idx, 0.92, prov=prov)
    assert eq_row['en'] == 'to drink', 'B08: same-quality EN is replaced by incoming'
    # B20: model_tier from sealed version (not hardcoded sonnet-only)
    assert model_tier('claude-opus-4-8') == 'opus'
    assert model_tier('claude-sonnet-4-6') == 'sonnet'
    # B20: execution.model_identifier mismatch refuses at en_index
    import tempfile as _tf_b20
    with _tf_b20.TemporaryDirectory() as _d:
        _wf = os.path.join(_d, 'wf_output.en.b20.json')
        with open(_wf, 'w', encoding='utf-8') as f:
            json.dump({
                'meta': {
                    'execution': {'model_identifier': 'claude-sonnet-4-6'},
                    'generated_at': '2026-08-02T00:00:00Z',
                    'input_hashes': {'k~~0': {'raw_sha256': 'aa'}},
                },
                'results': [{
                    'key': 'k~~0',
                    'card': {'records': [{'senses': [
                        {'german': 'trinken', 'english': 'to drink'}]}]},
                }],
            }, f)
        try:
            en_index([_wf], gen_model_version='claude-opus-4-8')
            assert False, 'B20: mismatched gen-model-version must refuse'
        except PromotionContractError as exc:
            assert 'does not match' in str(exc)
        ok_idx, ok_prov = en_index([_wf], gen_model_version='claude-sonnet-4-6')
        assert ok_idx['k~~0'] and ok_prov['k~~0']['model'] == 'sonnet'
        assert ok_prov['k~~0']['model_version'] == 'claude-sonnet-4-6'
    # H1553 defect refuse helpers (single-sourced from RU)
    assert refuse_defect_keys(['a~~1', 'b~~2'], ['b~~2'], force=False) == ['b~~2']
    assert refuse_defect_keys(['a~~1', 'b~~2'], ['b~~2'], force=True) == []
    assert clean_keys_from_report({
        'keys': ['a~~1', 'b~~2', 'c~~3'],
        'requeue_defect': ['b~~2'],
        'requeue': ['c~~3'],
    }) == ['a~~1']
    # C9: the backup name must be collision-resistant (two names in the SAME second differ) and the
    # O_EXCL fsynced copier must refuse an existing destination — so two lock-serialized runs can't
    # clobber the earlier recovery copy.
    import tempfile as _tf
    assert _en_backup_path('/x/store.jsonl') != _en_backup_path('/x/store.jsonl'), \
        'C9: two backup names generated back-to-back must be unique (µs+pid+uuid)'
    with _tf.TemporaryDirectory() as _d:
        _store = os.path.join(_d, 'store.jsonl')
        open(_store, 'w', encoding='utf-8').write('{}\n')
        _bak = _en_backup_path(_store)
        _fsynced_backup(_store, _bak)
        assert os.path.exists(_bak), 'C9: backup must be written'
        try:
            _fsynced_backup(_store, _bak)     # same destination again
            assert False, 'C9: the O_EXCL backup must refuse an existing destination'
        except FileExistsError:
            pass
    # P9 (H1421): the EN store write now reuses the RU lane's fsynced _atomic_write_rows (single
    # source) rather than a bare open('w')+os.replace with no fsync — a crash/power-loss between
    # the write and the rename can no longer leave a non-durable/truncated tri-lingual store. Pin
    # that the exact writer main() calls fsyncs BEFORE it renames, and round-trips the rows.
    import promote_final_cards as _pfc
    assert _atomic_write_rows is _pfc._atomic_write_rows, \
        'P9: the EN store writer must BE the RU lane primitive (single source, not a look-alike copy)'
    fsynced = []
    real_fsync = os.fsync

    def _spy_fsync(fd):
        fsynced.append(fd)
        return real_fsync(fd)
    os.fsync = _spy_fsync
    try:
        with _tf.TemporaryDirectory() as _d:
            _s = os.path.join(_d, 'store.jsonl')
            _atomic_write_rows(_s, [{'subcard': 'p_a~~h0', 'ru': 'пить', 'en': 'to drink'}])
            assert fsynced, 'P9: the EN store write must fsync before os.replace (durability)'
            _back = [json.loads(l) for l in open(_s, encoding='utf-8') if l.strip()]
            assert _back == [{'subcard': 'p_a~~h0', 'ru': 'пить', 'en': 'to drink'}], \
                'P9: rows must round-trip through the durable writer'
    finally:
        os.fsync = real_fsync
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
                         '(default %(default)s — the alias the harness pinned resolved to). '
                         'B20: when wf meta.execution.model_identifier is set, must match or refuse.')
    ap.add_argument('--judge-model-version', default=JUDGE_MODEL_VERSION,
                    help='resolved judge model version recorded in en_provenance.judge.model_version '
                         '(default %(default)s)')
    ap.add_argument('--defect-keys',
                    help='H1553/H2224: path to a one-key-per-line defect list (audit '
                         'requeue.defect.keys.txt). When omitted, auto-discovers next to the first '
                         'matched EN wf_output or under pilot/output/. Intersection with incoming '
                         'EN sub-cards is REFUSED unless --force.')
    ap.add_argument('--force', action='store_true',
                    help='H1553: override defect-key refusal (same semantics as promote_final_cards).')
    ap.add_argument('--ready-partial-report',
                    help='H1553 residual: path to an audit report JSON; only clean keys '
                         '(not requeue/defect/null) are attached. Combine with --dry-run to preview.')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-backup', action='store_true')
    ap.add_argument('--steal-lock', action='store_true',
                    help='H336/H-1: bypass a live promotion claim on --store unconditionally. Only '
                         'for a claim you are certain is dead (crashed run) — no PID-liveness check '
                         'is possible across clones/machines, so this is the only override.')
    ap.add_argument('--lock-ttl-seconds', type=int, default=None,
                    help='override the promotion claim staleness TTL (default: promote_lock.'
                         'DEFAULT_TTL_SECONDS = 30 min)')
    args = ap.parse_args()

    if not os.path.exists(args.store):
        sys.exit('no RU store at %s — run promote_final_cards.py first' % args.store)
    paths = sorted(glob.glob(os.path.join(ROOT, args.glob)))
    if not paths:
        sys.exit('no EN wf_output files matched %s under %s' % (args.glob, ROOT))
    print('store: %s' % os.path.relpath(args.store, ROOT))
    print('ingesting %d EN wf_output file(s)' % len(paths))

    rows = [json.loads(l) for l in open(args.store, encoding='utf-8') if l.strip()]
    try:
        idx, prov = en_index(paths, gen_model_version=args.gen_model_version)
    except PromotionContractError as exc:
        # B20: model-identity mismatch — refuse before any attach/write.
        sys.exit('EN promotion refused: %s' % exc)
    print('gen model: %s (%s)' % (model_tier(args.gen_model_version), args.gen_model_version))

    # H1553 / H2224: refuse EN sub-cards the latest audit marked as content defect.
    defect_path = discover_defect_keys_path(args.glob, args.defect_keys)
    defect_keys = []
    if args.defect_keys and not os.path.exists(args.defect_keys):
        sys.exit('REFUSED: --defect-keys path does not exist: %s' % args.defect_keys)
    if defect_path and os.path.exists(defect_path):
        defect_keys = load_defect_keys(defect_path)
        print('defect_guard: loaded %d key(s) from %s' % (len(defect_keys), defect_path))
    else:
        print('defect_guard: skipped_no_list')
    blocked = refuse_defect_keys(list(idx.keys()), defect_keys, force=False)
    if blocked and not args.force:
        sys.exit(
            'REFUSED: %d incoming EN key(s) are on the defect list (H1403 A3 / H1553). '
            'Re-translate or pass --force to override. Keys: %s'
            % (len(blocked), ', '.join(blocked[:20])
               + (' …' if len(blocked) > 20 else '')))
    if blocked and args.force:
        print('defect_guard: --force overrides %d defect key(s): %s'
              % (len(blocked), ', '.join(blocked[:10])
                 + (' …' if len(blocked) > 10 else '')))
    elif defect_keys and not blocked:
        print('defect_guard: no intersection with incoming keys')

    # H1553 residual: optional clean-subset filter from an audit report.
    if args.ready_partial_report:
        try:
            with open(args.ready_partial_report, encoding='utf-8') as f:
                report = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            sys.exit('REFUSED: cannot load --ready-partial-report: %s' % e)
        clean = set(clean_keys_from_report(report))
        before = len(idx)
        for k in list(idx.keys()):
            if k not in clean:
                del idx[k]
                prov.pop(k, None)
        print('ready_partial: kept %d/%d EN sub-card(s) (clean keys only)'
              % (len(idx), before))
        if not idx:
            sys.exit('REFUSED: ready_partial filter left zero EN sub-cards to attach')

    judge = load_judge(args.judge, judge_model_version=args.judge_model_version) if args.judge else None
    if args.judge:
        print('judge verdicts: %d (from %s); judge model: opus (%s)'
              % (len(judge), os.path.basename(args.judge), args.judge_model_version))
    en_senses = sum(len(v) for v in idx.values())
    try:
        stats = attach(rows, idx, args.threshold, prov=prov, judge=judge)
    except UnrestoredPlaceholder as exc:
        # C6: refuse loudly, before any backup/store write, exactly like the RU lane.
        sys.exit('EN promotion refused: %s' % exc)

    eligible = len(rows) - stats['no-en-file']
    print('\n=== EN MERGE COVERAGE ===')
    print('store rows              : %d' % len(rows))
    print('EN sub-cards / senses   : %d / %d' % (len(idx), en_senses))
    print('rows with EN sub-card   : %d' % eligible)
    print('  en attached           : %d (exact %d, exact-ambig %d, fuzzy %d)' % (
        stats['attached'], stats['exact'], stats['exact-ambiguous'], stats['fuzzy']))
    if stats.get('better-attempt-kept'):
        print('  better-attempt kept   : %d (store EN ranked higher — B08)'
              % stats['better-attempt-kept'])
    if args.judge:
        print('  with opus judge block : %d' % stats['judged'])
    print('  unmatched (left absent): %d (below-threshold %d, fuzzy-ambig %d, no-en-sense %d, no-de-key %d)' % (
        stats['below-threshold'] + stats['fuzzy-ambiguous'] + stats['no-en-sense'] + stats['no-de-key'],
        stats['below-threshold'], stats['fuzzy-ambiguous'], stats['no-en-sense'], stats['no-de-key']))
    print('rows with no EN file yet: %d (roots beyond the EN run — EN absent, expected)' % stats['no-en-file'])

    if args.dry_run:
        print('\n(dry run — store not written)')
        return

    # H336/H-1 (LANG_PARITY: SHARED with promote_final_cards.py): claim the store across
    # the backup+write window so two concurrent promote_en runs can't race the same LWW
    # write, and give each run its own timestamped backup instead of clobbering one
    # '.preEN.bak'. See promote_lock.py for why staleness is TTL-only, not PID-based.
    ttl_kwargs = {'ttl_seconds': args.lock_ttl_seconds} if args.lock_ttl_seconds else {}
    try:
        with PromoteClaim(args.store, steal=args.steal_lock, **ttl_kwargs):
            if not args.no_backup:
                # C9: collision-resistant name (µs+pid+uuid) + O_EXCL fsynced copy, so two
                # lock-serialized runs in the SAME second can no longer clobber the earlier recovery
                # copy — second-resolution + a plain open('w') did exactly that, silently.
                bak = _en_backup_path(args.store)
                _fsynced_backup(args.store, bak)
                print('\nbacked up store -> %s' % os.path.basename(bak))
            # Durable atomic write: the RU lane's _atomic_write_rows — mkstemp temp,
            # fh.flush() + os.fsync() BEFORE os.replace (H1421 P9). The old bare
            # open('w')+os.replace was atomic but NOT durable: a crash/power-loss between the
            # write and the metadata flush could leave a non-durable/truncated store even after
            # the rename. Under --no-backup this write is the ONLY thing standing between an
            # interrupted write and total loss, so it must be genuinely durable. Single-sourced
            # with the RU bridge, so both lanes write the store byte-identically ('\n' newlines).
            _atomic_write_rows(args.store, rows)
            print('wrote tri-lingual store -> %s (%d rows, %d now carry en)'
                  % (os.path.relpath(args.store, ROOT), len(rows), stats['attached']))
            print('NEXT: re-run `python src/annotate_dcs_freq.py` to (re)attach the dcs_freq block.')
    except ClaimBusy as e:
        sys.exit(str(e))


if __name__ == '__main__':
    main()
