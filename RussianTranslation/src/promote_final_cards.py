#!/usr/bin/env python
r"""Promote translated workflow cards into the canonical translated store (the print bridge).

The keystone convergence step. Until now the translated wf_output.*.json cards were STRANDED:
export_interop.py builds the citable TEI/OntoLex edition from src/assembled_cards.jsonl and the
translated store src/pwg_ru_translated.jsonl, but NOTHING wrote the harness translations into that
store. This script does: it ingests every wf_output*.json, extracts each non-null card's senses,
stamps per-card provenance, and writes one store row per sense keyed by the HEADWORD key1 (the
join key export_interop uses — wf cards key on the sub-card key `root~~h0_..`, but meta.root is the
plain SLP1 headword that matches assembled_cards.jsonl).

Rows are written with review_status='ai_translated' — NOT 'approved'. export_interop's
approved_store() gate only exports {approved, human_reviewed}, so promoted translations reach the
store (and unblock G5 review counting) WITHOUT silently publishing unreviewed AI as a citable
edition. G5 human review flips a row to 'approved', and only then does it export.

Supersede mode (default): the new store replaces the old run_batch store (which is entirely
'legacy_needs_review' and therefore exported zero rows anyway). The prior file is backed up to
<store>.legacy.bak unless --no-backup.

  python src/promote_final_cards.py --gen-model-version claude-sonnet-5
                                                   # promote -> src/pwg_ru_translated.jsonl
  python src/promote_final_cards.py --dry-run        # report coverage, write nothing
  python src/promote_final_cards.py --glob 'wf_output.sd.*.json'   # a subset

Coverage is reported honestly: per-root card counts plus a WARNING for roots whose per-root file
is a requeue subset (the full Slice-C originals were overwritten; re-run or recover them, then
re-run this script — it is idempotent and supersede-safe).
"""
import argparse
import datetime
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pipeline_version
import dict_merge
from promote_lock import PromoteClaim, ClaimBusy
from store_path import canonical_store

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # the RussianTranslation repo root
# Resolve the PERSISTENT store, not this checkout's copy: a drain window run in an isolated
# `git worktree` must promote into the MAIN checkout's store, or every promotion is discarded
# with the worktree (the H255 w06 loss — 29 sub-cards gone). See store_path.canonical_store.
DEFAULT_STORE = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))
DEFAULT_GLOB = 'wf_output*.json'
MODEL = 'sonnet'                                    # the harness pins model:'sonnet' (gen_opt_harness2)
# Tier + VERSION must both be recorded (models change — a bare 'sonnet' is ambiguous later;
# same convention as promote_en.py). The wf_output meta does not reliably carry the resolved
# version, so normal promotion must pass --gen-model-version explicitly.
SELFTEST_MODEL_VERSION = 'claude-sonnet-5'


def explicit_glob_supplied(argv):
    """Whether argv explicitly scopes promotion inputs with --glob."""
    return any(arg == '--glob' or arg.startswith('--glob=') for arg in argv)


def load_wf(path):
    with open(path, encoding='utf-8') as f:
        wrapper = json.load(f)
    result = wrapper.get('result')
    if isinstance(result, str):
        result = json.loads(result)
    if result is None:
        result = wrapper
    return result


def collect_cards(paths):
    """sub-card key -> {card, meta, wf_file}. Non-null wins; both-non-null keeps first + logs.

    EN wf files are EXCLUDED: this is the RU bridge (rows_for reads sense['russian']), but
    DEFAULT_GLOB 'wf_output*.json' also matches wf_output.en.* — and those sort BEFORE the
    RU files, so first-seen-wins used to let an EN card shadow the RU card for the same
    sub-key, yielding ZERO rows for it (no 'russian' field) in a full rebuild. EN attachment
    is promote_en.py's job."""
    best, conflicts, null_keys, en_skipped = {}, [], set(), 0
    for path in paths:
        try:
            res = load_wf(path)
        except (OSError, json.JSONDecodeError) as e:
            print('  skip (unreadable): %s (%s)' % (os.path.basename(path), e))
            continue
        meta = res.get('meta') or {}
        if meta.get('lang') == 'en' or os.path.basename(path).startswith('wf_output.en.'):
            en_skipped += 1
            continue
        for r in res.get('results') or []:
            key = r.get('key')
            card = r.get('card')
            if not key:
                continue
            if not card:
                null_keys.add(key)
                continue
            if key in best:
                conflicts.append(key)
                continue                            # keep first-seen non-null
            entry = {'card': card, 'meta': meta, 'wf_file': os.path.basename(path)}
            # carry result-ROW level partial/drift markers (autosplit merge puts them on the
            # row, the selfheal inline path on the card) so provenance can record them
            for m in ('partial', 'missing_senses', 'total_senses', 'fidelity_drift'):
                if r.get(m):
                    entry[m] = r[m]
            best[key] = entry
    if en_skipped:
        print('  skipped %d EN wf file(s) (promote_en.py attaches those)' % en_skipped)
    null_keys -= set(best)                          # a key non-null somewhere isn't a null
    return best, conflicts, sorted(null_keys)


def provenance(entry, subkey, model_version):
    meta = entry['meta']
    hashes = (meta.get('input_hashes') or {}).get(subkey) or {}
    card = entry.get('card') or {}
    # H214: prefer the PER-CARD source-material profile; fall back to the window-level marker
    # for older harness outputs that only carried meta.source_profile.
    profiles = meta.get('source_profiles')
    source_profile = (profiles.get(subkey) if isinstance(profiles, dict)
                      else meta.get('source_profile'))
    prov = {
        'model': MODEL,
        'model_version': model_version,
        'generator': meta.get('generator'),
        'schema_version': meta.get('schema_version'),
        'root': meta.get('root'),
        'safe_root': meta.get('safe_root'),
        # H214: per-card source-material profile ('no_pwg_supplement_chain' |
        # 'pwg_with_supplements' (MIXED) | 'pwg_only' | 'pwg_supplement_subcard' | None) —
        # pairs with the first-class `layer` field so the QA chain / export know each row's
        # vintage. Filter 'pwg_with_supplements' to find every mixed card.
        'source_profile': source_profile,
        'rootmap_sha256': meta.get('rootmap_sha256'),
        'input_raw_sha256': hashes.get('raw_sha256'),
        'input_portrait_sha256': hashes.get('portrait_sha256'),
        'generated_at': meta.get('generated_at'),
        'wf_file': entry['wf_file'],
        'promoted_by': 'promote_final_cards.py',
        # semver of OUR tooling at promotion time — orthogonal to model_version;
        # lets a later bugfix flag which rows need re-translation (see pipeline_version.py).
        'pipeline': pipeline_version.stamp(model_version=model_version),
    }
    # A partial card is USABLE but INCOMPLETE — record that on every row it yields, or a
    # store consumer cannot distinguish it from a complete card (audit_coverage only flags
    # below 80% of source senses, so a 39/41-group partial reads as 'complete' everywhere
    # downstream without this marker).
    partial = card.get('partial') or entry.get('partial')
    if partial:
        prov['partial_card'] = True
        for m in ('missing_fragments', 'missing_groups', 'total_groups'):
            if card.get(m) is not None:
                prov[m] = card[m]
        for m in ('missing_senses', 'total_senses'):
            if entry.get(m) is not None:
                prov[m] = entry[m]
    if entry.get('fidelity_drift'):
        prov['fidelity_drift'] = True
    return prov


def rows_for(subkey, entry, review_status, model_version):
    card = entry['card']
    meta = entry['meta']
    if meta.get('nominal'):
        keymap = meta.get('nominal_keymap') or {}
        key1 = keymap.get(subkey) or keymap.get(card.get('key1')) or card.get('key1') or subkey.split('~~', 1)[0]
    else:
        key1 = meta.get('root')                    # the join key into assembled_cards.jsonl
    prov = provenance(entry, subkey, model_version)
    # Explicit source LAYER (pwg/pw/sch/pwkvn/nws) parsed from the sub-card key. Until now
    # the layer was ONLY encoded in the key suffix; making it a first-class field lets the
    # deferred addenda re-glue / typology (H180) group rows by layer without re-parsing keys.
    layer = dict_merge.layer_of(subkey)
    for rec in card.get('records') or []:
        for sense in rec.get('senses') or []:
            ru = sense.get('russian')
            if not ru:
                continue
            yield {
                'key1': key1,
                'subcard': subkey,
                'layer': layer,
                'iast': card.get('iast'),
                'h': rec.get('h'),
                'sense_tag': sense.get('tag'),
                'ru': ru,
                'de': sense.get('german'),
                'equivalence_type': sense.get('equivalence_type'),
                'source_type': sense.get('source_type'),
                'stratum': sense.get('stratum'),
                'differentia': sense.get('differentia'),
                'review_status': review_status,
                'reviewer': None,
                'provenance': prov,
            }


def selftest():
    import tempfile
    meta = {'root': 'pA', 'safe_root': 'p_a', 'generator': 'gen_opt_harness2.batched-masked',
            'schema_version': 'v1', 'rootmap_sha256': 'abc', 'generated_at': '2026-06-29T00:00:00Z',
            'input_hashes': {'p_a~~h5_00_pwg00': {'raw_sha256': 'r1', 'portrait_sha256': 'p1'}}}
    entry = {'card': {'key1': 'p_a~~h5_00_pwg00', 'iast': 'pā', 'records': [
        {'h': 'pā', 'senses': [
            {'tag': '1', 'russian': 'пить', 'german': 'trinken', 'equivalence_type': 'equivalent',
             'source_type': 'attested', 'stratum': 'Vedic', 'differentia': ''},
            {'tag': '2', 'russian': '', 'german': 'x'},          # no russian -> skipped
        ]}]}, 'meta': meta, 'wf_file': 'wf_output.sc.pA.json'}
    rows = list(rows_for('p_a~~h5_00_pwg00', entry, 'ai_translated',
                         SELFTEST_MODEL_VERSION))
    assert len(rows) == 1, 'a sense without russian must be skipped'
    r = rows[0]
    assert r['key1'] == 'pA', 'key1 must be the HEADWORD meta.root, not the sub-card key'
    assert r['subcard'] == 'p_a~~h5_00_pwg00' and r['ru'] == 'пить' and r['de'] == 'trinken'
    assert r['layer'] == 'pwg', 'base sub-card must carry an explicit layer=pwg'
    assert list(rows_for('x~~h0_zz_pw01', dict(entry, meta=meta), 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]['layer'] == 'pw', 'addenda sub-card -> layer=pw'
    assert r['review_status'] == 'ai_translated', 'must not auto-approve (G5 gate)'
    p = r['provenance']
    assert p['model'] == 'sonnet' and p['rootmap_sha256'] == 'abc'
    assert p['model_version'] == SELFTEST_MODEL_VERSION, 'model VERSION recorded, not just the tier alias'
    assert p['input_raw_sha256'] == 'r1' and p['generated_at'], 'provenance must be complete'
    # NOMINAL mode: meta.root is a window LABEL; the row must key to the true SLP1 headword
    # recovered from nominal_keymap[stem], NOT to the label (regression guard, H179 drain).
    nmeta = {'root': 'pril10_w1', 'nominal': True, 'nominal_keymap': {'k_ala': 'kAla'},
             'input_hashes': {'k_ala': {'raw_sha256': 'r', 'portrait_sha256': 'p'}}}
    ncard = {'key1': 'kAla', 'iast': 'kāla',
             'records': [{'h': 'kāla', 'senses': [{'tag': '1', 'russian': 'время', 'german': 'Zeit'}]}]}
    nrow = list(rows_for('k_ala', {'card': ncard, 'meta': nmeta, 'wf_file': 'wf_output.json'},
                         'ai_translated', SELFTEST_MODEL_VERSION))[0]
    assert nrow['key1'] == 'kAla', 'nominal card must key to true SLP1 headword, not the window label'
    assert nrow['subcard'] == 'k_ala' and nrow['layer'] == 'pwg'
    assert 'partial_card' not in p, 'complete card carries no partial marker'
    # a partial (selfheal) card must be marked on every row it yields
    pentry = dict(entry)
    pentry['card'] = dict(entry['card'], partial=True, missing_fragments=['g2:f1'],
                          missing_groups=1, total_groups=3)
    pr = list(rows_for('p_a~~h5_00_pwg00', pentry, 'ai_translated',
                       SELFTEST_MODEL_VERSION))[0]['provenance']
    assert pr['partial_card'] is True and pr['missing_fragments'] == ['g2:f1'], \
        'partial cards must be distinguishable in the store'
    # collect_cards: a non-null card wins over a null for the same sub-card key.
    d = tempfile.mkdtemp()
    nullf = os.path.join(d, 'wf_output.sc.x.json')
    fullf = os.path.join(d, 'wf_output.x.json')
    with open(nullf, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [{'key': 'p_a~~h5_00_pwg00', 'card': None}]}, f)
    with open(fullf, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [{'key': 'p_a~~h5_00_pwg00', 'card': entry['card']}]}, f)
    best, _conf, nulls = collect_cards([nullf, fullf])
    assert 'p_a~~h5_00_pwg00' in best, 'non-null must win over null for the same key'
    assert nulls == [], 'a key non-null in any file is not a null'
    # EN wf files must NOT shadow RU cards: 'wf_output.en.*' sorts before 'wf_output.sc.*',
    # and its cards carry 'english' not 'russian' -> zero rows -> silent RU loss on rebuild.
    enf = os.path.join(d, 'wf_output.en.x.json')
    en_meta = dict(meta, lang='en')
    en_card = {'key1': 'p_a~~h5_00_pwg00', 'records': [
        {'h': 'pā', 'senses': [{'tag': '1', 'english': 'to drink', 'german': 'trinken'}]}]}
    with open(enf, 'w', encoding='utf-8') as f:
        json.dump({'meta': en_meta, 'results': [{'key': 'p_a~~h5_00_pwg00', 'card': en_card}]}, f)
    best, _conf, _nulls = collect_cards(sorted([enf, fullf, nullf]))
    got = best['p_a~~h5_00_pwg00']
    assert got['meta'].get('lang') != 'en', 'EN wf file must be excluded from the RU bridge'
    assert list(rows_for('p_a~~h5_00_pwg00', got, 'ai_translated',
                         SELFTEST_MODEL_VERSION)), 'RU rows survive the EN sibling'
    assert explicit_glob_supplied(['--merge', '--glob', 'src/pilot/output/wf_output.w01.json'])
    assert explicit_glob_supplied(['--glob=src/pilot/output/wf_output.w01.json', '--merge'])
    assert not explicit_glob_supplied(['--merge'])
    print('promote_final_cards selftest OK')


def main():
    if '--selftest' in sys.argv[1:]:
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument('--glob', default=DEFAULT_GLOB, help='wf_output glob, relative to repo root')
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--review-status', default='ai_translated')
    ap.add_argument('--gen-model-version', default=None, required='--selftest' not in sys.argv[1:],
                    help='resolved model version recorded in provenance.model_version '
                         '(exact model id required; do not guess from the model alias)')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-backup', action='store_true')
    ap.add_argument('--force', action='store_true',
                    help='bypass the >50%%-shrink overwrite guard (only for a deliberate full rebuild)')
    ap.add_argument('--merge', action='store_true',
                    help='MERGE into the existing store by SUB-CARD: replace only the sub-cards '
                         'present in THIS run, keep every other row (including a root\'s already-'
                         'translated sub-cards not in this run). Use for a per-root catch-up — the '
                         'default full overwrite WIPES any root whose wf_output file is no longer '
                         'on disk (the gam-RU loss mode).')
    ap.add_argument('--steal-lock', action='store_true',
                    help='H336/H-1: bypass a live promotion claim on --store unconditionally. Only '
                         'for a claim you are certain is dead (crashed run) — no PID-liveness check '
                         'is possible across clones/machines, so this is the only override.')
    ap.add_argument('--lock-ttl-seconds', type=int, default=None,
                    help='override the promotion claim staleness TTL (default: promote_lock.'
                         'DEFAULT_TTL_SECONDS = 30 min)')
    args = ap.parse_args()
    if args.merge and not explicit_glob_supplied(sys.argv[1:]):
        sys.exit(
            'refusing --merge with the implicit broad glob %r; pass --glob explicitly '
            '(normally src/pilot/output/wf_output.<window>.json)' % DEFAULT_GLOB)

    # Provenance: make the resolved store path explicit — a worktree run promotes into the MAIN
    # checkout's store (store_path.canonical_store), never a discarded worktree copy (H255 w06 / H805).
    _local = os.path.join(HERE, 'pwg_ru_translated.jsonl')
    if os.path.normpath(args.store) != os.path.normpath(_local):
        print("store: %s\n       (canonical/shared — not this checkout's %s)"
              % (args.store, os.path.relpath(_local, ROOT)), file=sys.stderr)

    paths = sorted(glob.glob(os.path.join(ROOT, args.glob)))
    if not paths:
        sys.exit('no wf_output files matched %s under %s' % (args.glob, ROOT))
    print('ingesting %d wf_output file(s)' % len(paths))
    best, conflicts, null_keys = collect_cards(paths)

    rows, per_root = [], {}
    for subkey, entry in sorted(best.items()):
        n = 0
        for row in rows_for(subkey, entry, args.review_status, args.gen_model_version):
            rows.append(row)
            n += 1
        root = entry['meta'].get('root')
        per_root.setdefault(root, {'cards': 0, 'rows': 0})
        per_root[root]['cards'] += 1
        per_root[root]['rows'] += n

    # Coverage report — honest about partial (requeue-subset) roots.
    print('\n=== PROMOTION COVERAGE ===')
    print('non-null cards promoted : %d' % len(best))
    print('sense rows              : %d' % len(rows))
    print('distinct headwords      : %d' % len(per_root))
    print('null sub-cards skipped  : %d' % len(null_keys))
    if conflicts:
        print('duplicate non-null keys : %d (kept first-seen)' % len(conflicts))
    thin = sorted(r for r, v in per_root.items() if v['cards'] <= 5)
    if thin:
        print('\n⚠ roots with <=5 promoted cards (likely a requeue-subset / partial file — the full')
        print('  output was overwritten; re-run that root and re-run this script to complete it):')
        print('  ' + ', '.join('%s(%d)' % (r, per_root[r]['cards']) for r in thin))

    if args.dry_run:
        # A dry run never writes, so it needs no claim — but SKIP the merge-preview read of
        # args.store here too (it would be a second, unlocked reader of a file a real promote
        # run might be mid-write on); dry-run coverage above is computed from wf_output alone.
        print('\n(dry run — no store written)')
        return

    # H336/H-1: claim the store for the ENTIRE read-guard-write window — merge-read,
    # overwrite guard, backup, final write — so two concurrent promote runs can never
    # interleave. See promote_lock.py for why this is TTL-only, not PID-based.
    ttl_kwargs = {'ttl_seconds': args.lock_ttl_seconds} if args.lock_ttl_seconds else {}
    try:
        claim_cm = PromoteClaim(args.store, steal=args.steal_lock, **ttl_kwargs)
        with claim_cm:
            # --merge: replace only the SUB-CARDS present in this run, keep every other row.
            # Sub-card granularity (not root) is deliberate: a per-root CATCH-UP promotes only
            # the missing sub-cards, disjoint from the ones already in the store — a root-level
            # replace would delete the existing sub-cards (the exact gam-RU loss we are fixing).
            # Guards against the full-overwrite wipe when only a subset of wf_output is on disk.
            kept = 0
            if args.merge and os.path.exists(args.store):
                promoted_subs = {r['subcard'] for r in rows}
                touched_roots = {r['key1'] for r in rows}
                keep_rows = []
                with open(args.store, encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        e = json.loads(line)
                        if e.get('subcard') not in promoted_subs:
                            keep_rows.append(e)
                kept = len(keep_rows)
                print('\nMERGE: replacing %d sub-card(s) across root(s) %s; keeping %d existing row(s)'
                      % (len(promoted_subs), sorted(touched_roots), kept))
                rows_to_write = keep_rows + rows
            else:
                rows_to_write = rows

            # OVERWRITE GUARD: refuse to shrink the store to a small fraction of its current
            # size. A default (non-merge) run rebuilds the store from whatever wf_output files
            # are on disk; if most are gone (or only a subset is present) this silently WIPES
            # the store — a 10,122-row store was once overwritten to 472. Require --force to
            # shrink >50%.
            if os.path.exists(args.store) and not args.force:
                try:
                    with open(args.store, encoding='utf-8') as f:
                        existing = sum(1 for line in f if line.strip())
                except OSError:
                    existing = 0
                if existing and len(rows_to_write) < existing * 0.5:
                    sys.exit('REFUSED: would shrink store %d -> %d rows (>50%% loss). Use --merge '
                             'for a per-root catch-up, or --force if a full rebuild is truly '
                             'intended.' % (existing, len(rows_to_write)))

            if os.path.exists(args.store) and not args.no_backup:
                # H336/H-1: a UNIQUE timestamped backup name — the old fixed '.premerge.bak'
                # meant a second concurrent promote (even serialized seconds apart by this same
                # claim) would overwrite the first run's only recovery copy of the pre-merge
                # store. Each promote now keeps its own backup.
                stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
                bak = args.store + ('.premerge.%s.bak' % stamp if args.merge
                                    else '.legacy.%s.bak' % stamp)
                os.replace(args.store, bak)
                print('\nbacked up prior store -> %s' % os.path.basename(bak))
            # Atomic write: stream to a temp file then os.replace, so a crash/kill mid-write
            # can never leave the canonical store truncated (the store this project has lost
            # before). Matches the tmp+replace pattern in run_batch.apply_review.
            tmp = args.store + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                for row in rows_to_write:
                    f.write(json.dumps(row, ensure_ascii=False) + '\n')
            os.replace(tmp, args.store)
            print('wrote canonical translated store -> %s (%d rows, review_status=%s)'
                  % (args.store, len(rows_to_write), args.review_status))
            print('NOTE: rows are %s, NOT approved — export_interop keeps them out of the citable'
                  % args.review_status)
            print('      edition until G5 human review flips review_status to approved.')
    except ClaimBusy as e:
        sys.exit(str(e))


if __name__ == '__main__':
    main()
