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
import collections
import contextlib
import datetime
import glob
import json
import os
import shutil
import sys
import tempfile
import uuid

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import re
import pipeline_version
import dict_merge
import card_fields
import validate_final_card_schema
from promote_lock import PromoteClaim, ClaimBusy
from store_path import canonical_store
# H1624 G2: deterministic DE-side Rektion on every promoted sense (same extractor as
# annotate_government / government.html — never invented, never from RU).
from government_census import extract_government
# H1624 form-layer: number / gender / nom|voc / voice — sibling of Rektion.
from form_labels import extract_form_labels, extract_form_notes
from citation_edges import extract_citation_edges
from edition_rel import classify_edition_rel
from pilot import promotion_journal

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


def load_defect_keys(path):
    """Load a one-key-per-line defect list (audit requeue.defect.keys.txt format)."""
    keys = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            keys.append(line)
    return keys


def discover_defect_keys_path(glob_pattern, explicit_path=None):
    """Resolve the defect-keys file for a promote run (H1403 A3 / H1553).

    Order: explicit --defect-keys path; else requeue.defect.keys.txt next to the
    first matching wf_output under the glob; else pilot/output/requeue.defect.keys.txt.
    Returns None when no list is discoverable (promote proceeds; log skipped_no_list).
    """
    if explicit_path:
        return explicit_path if os.path.exists(explicit_path) else explicit_path
    candidates = []
    paths = sorted(glob.glob(os.path.join(ROOT, glob_pattern))) if glob_pattern else []
    if paths:
        candidates.append(os.path.join(os.path.dirname(paths[0]), 'requeue.defect.keys.txt'))
    candidates.append(os.path.join(ROOT, 'src', 'pilot', 'output', 'requeue.defect.keys.txt'))
    # also accept the older sibling name used in some docs
    candidates.append(os.path.join(ROOT, 'src', 'pilot', 'output', 'requeue.keys.defect'))
    for cand in candidates:
        if cand and os.path.exists(cand):
            return cand
    return None


def refuse_defect_keys(incoming_keys, defect_keys, force=False):
    """Return the sorted intersection of incoming and defect keys.

    Caller must refuse (non-zero exit, no store write) when the set is non-empty
    and force is False. Empty defect_keys means the guard is inert.
    """
    if not defect_keys:
        return []
    blocked = sorted(set(incoming_keys) & set(defect_keys))
    if blocked and force:
        return []  # force clears the refuse set for the gate (caller still may log)
    return blocked


def clean_keys_from_report(report):
    """Keys present in a workflow/audit report that are NOT requeue/null/defect."""
    all_keys = list(report.get('keys') or [])
    blocked = set(report.get('requeue') or [])
    blocked |= set(report.get('requeue_defect') or [])
    blocked |= set(report.get('null_cards') or [])
    blocked |= set(report.get('requeue_transient') or [])
    # also accept a positive clean list if the report already computed one
    if report.get('clean_keys') is not None:
        return sorted(set(report['clean_keys']))
    sample = report.get('judge_sample') or {}
    if sample.get('clean_sample_keys') is not None and report.get('keys'):
        # clean = all keys minus requeue/null — not just the judge sample
        pass
    return sorted(k for k in all_keys if k not in blocked)


def promote_ready_partial_clean(lease_or_report, *, dry_run=True, store=None,
                                gen_model_version=None, review_status='ai_translated',
                                wf_glob=None, force=False):
    """Promote only clean keys from a ready_partial audit report (H1403 A3 / H1553).

    Wave-1 fence: default dry_run=True. Production apply requires dry_run=False
    (CLI --apply). Tests use a fixture store only — never the live pwg_ru store.

    lease_or_report: audit report dict (or a lease-shaped dict with a nested
    'report' / 'audit_report' key). Returns a result dict describing what would
    land / what was refused; never writes when dry_run is True.
    """
    report = lease_or_report
    if isinstance(lease_or_report, dict) and 'report' in lease_or_report and 'keys' not in lease_or_report:
        report = lease_or_report['report']
    elif isinstance(lease_or_report, dict) and 'audit_report' in lease_or_report:
        report = lease_or_report['audit_report']

    clean = clean_keys_from_report(report or {})
    defect = list((report or {}).get('requeue_defect') or [])
    result = {
        'schema': 'pwg_ru.ready_partial_promote.v1',
        'dry_run': bool(dry_run),
        'clean_keys': clean,
        'defect_keys': sorted(defect),
        'promoted_keys': [],
        'refused_defect_keys': [],
        'store': store,
        'status': 'dry_run' if dry_run else 'pending',
    }
    if not clean:
        result['status'] = 'no_clean_keys'
        return result

    # Defect intersection among clean should be empty by construction; belt-and-braces.
    blocked = refuse_defect_keys(clean, defect, force=force)
    if blocked and not force:
        result['refused_defect_keys'] = blocked
        result['status'] = 'refused_defect'
        return result

    if dry_run:
        result['promoted_keys'] = list(clean)
        result['status'] = 'dry_run_ok'
        return result

    if not store:
        result['status'] = 'error_no_store'
        return result
    if not gen_model_version:
        result['status'] = 'error_no_model_version'
        return result

    # Apply path: filter a wf_output glob to clean keys and write via the normal
    # merge path. Callers (wave-1) should not reach here against the live store.
    paths = sorted(glob.glob(wf_glob)) if wf_glob else []
    if not paths:
        result['status'] = 'error_no_wf'
        return result
    best, conflicts, _null = collect_cards(paths)
    if conflicts:
        result['status'] = 'error_conflicts'
        result['conflicts'] = conflicts
        return result
    clean_set = set(clean)
    selected = {k: v for k, v in best.items() if k in clean_set}
    rows = []
    for subkey, entry in sorted(selected.items()):
        validate_promotion_entry(subkey, entry)
        for row in rows_for(subkey, entry, review_status, gen_model_version):
            rows.append(row)
    if not rows:
        result['status'] = 'error_no_rows'
        return result
    existing_rows = []
    if os.path.exists(store):
        with open(store, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    existing_rows.append(json.loads(line))
    # H2146: the clean-subset path never overrides human-reviewed rows — wave-1 agents
    # must not be able to strip a reviewer stamp; protected subcards keep their store rows.
    rows_to_write, downgraded, protected = merge_store_rows(existing_rows, rows)
    if protected:
        print('⚠ overlay-preserve: store keeps its HUMAN-REVIEWED rows for %d subcard(s); '
              'incoming machine attempt dropped: %s'
              % (len(protected), ', '.join(protected[:10])))
    claim_cm = PromoteClaim(store)
    with claim_cm:
        if os.path.exists(store):
            bak = _backup_path(store, True)
            _fsynced_backup(store, bak)
        _atomic_write_rows(store, rows_to_write)
    result['promoted_keys'] = sorted(selected)
    result['downgraded'] = downgraded
    result['protected'] = protected
    result['rows_written'] = len(rows_to_write)
    result['status'] = 'applied'
    return result


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
    """sub-card key -> {card, meta, wf_file}. Non-null wins; exact duplicates collapse.

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
            entry = {'card': card, 'meta': meta, 'wf_file': os.path.basename(path)}
            # carry result-ROW level partial/drift markers (autosplit merge puts them on the
            # row, the selfheal inline path on the card) so provenance can record them
            for m in ('partial', 'missing_senses', 'total_senses', 'fidelity_drift'):
                if r.get(m):
                    entry[m] = r[m]
            if key in best:
                # Recovered/copied workflow artifacts can contain the exact same successful
                # card.  Collapse those safely, but never choose arbitrarily between different
                # translations, generation metadata, or partial/drift markers.  wf_file is an
                # artifact location rather than generation provenance, so it is deliberately
                # excluded from the equivalence payload.
                fields = ('card', 'meta', 'partial', 'missing_senses',
                          'total_senses', 'fidelity_drift')
                prior = {name: best[key].get(name) for name in fields}
                current = {name: entry.get(name) for name in fields}
                if prior != current:
                    conflicts.append(key)
                continue
            best[key] = entry
    if en_skipped:
        print('  skipped %d EN wf file(s) (promote_en.py attaches those)' % en_skipped)
    null_keys -= set(best)                          # a key non-null somewhere isn't a null
    return best, conflicts, sorted(null_keys)


def clear_denials_for_promotion(best, blocked_subs=(), lang='ru', denylist=None,
                                timestamp=None):
    """B12 (H1339): a successful gate-passing promotion clears ONLY its matching temporary
    TM denial state.

    The denylist keys on the INPUT address (lang:raw_sha256) / fragment fsha, and used to be
    append-forever -- one defect requeue disabled TM reuse of that card permanently, even
    after the retranslation passed every gate and was promoted. For each subcard that
    actually LANDED (never a better-attempt-refused downgrade), unblock its input address
    and any frag_prov fragment SHAs -- but only those CURRENTLY denied, so no spurious
    unblock rows are ever written. Returns (addresses_cleared, fshas_cleared)."""
    pilot = os.path.join(HERE, 'pilot')
    if pilot not in sys.path:
        sys.path.insert(0, pilot)
    import translation_memory as tm
    denied = tm.load_denylist(denylist)
    addresses, fshas = [], []
    blocked = set(blocked_subs)
    for subkey, entry in best.items():
        if subkey in blocked:
            continue
        sha = ((entry.get('meta') or {}).get('input_hashes') or {}).get(subkey, {}).get('raw_sha256')
        if sha:
            address = '%s:%s' % (lang, sha)
            if address in denied['addresses']:
                addresses.append(address)
        for fp in ((entry.get('card') or {}).get('frag_prov') or []):
            fsha = fp.get('fsha')
            if fsha and fsha in denied['frags']:
                fshas.append(fsha)
    if addresses or fshas:
        tm.append_unblock(sorted(set(addresses)), sorted(set(fshas)),
                          reason='replaced_by_promotion', path=denylist,
                          timestamp=timestamp)
    return sorted(set(addresses)), sorted(set(fshas))


def model_tier(model_version):
    """The tier alias for a resolved model id: 'claude-sonnet-5' -> 'sonnet'.

    B20 (H1339): provenance.model was hardcoded 'sonnet' regardless of the actual
    generating model; derive it from the recorded exact version instead. Unknown shapes
    fall back to the legacy constant rather than fabricating a tier."""
    if isinstance(model_version, str) and model_version.startswith('claude-'):
        parts = model_version.split('-')
        if len(parts) >= 2 and parts[1]:
            return parts[1]
    return MODEL


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
        'model': model_tier(model_version),
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
    # H1226: carry the pre-restore {Tn} pairing accept() stamped on the card — candidate `got`
    # vs masked-skeleton `want`, brace-stripped — so the TNMASK false-flag rate is MEASURABLE
    # offline from a promoted row (H1150 returned DO_NOT_ARM with denominator 1 precisely because
    # the store dropped this transient pairing; only post-restore text survived). Additive +
    # backward-compatible: absent on pre-H1226 wf_output and never back-filled; carried ONLY when
    # well-formed (both `got` and `want` present as strings), never fabricated. The offline reader
    # is src/pilot/tnmask_offline.py; full rationale in pwg_ru/h1226 design note.
    tnmask = card.get('tnmask')
    if (isinstance(tnmask, dict)
            and isinstance(tnmask.get('got'), str)
            and isinstance(tnmask.get('want'), str)):
        prov['tnmask'] = {'got': tnmask['got'], 'want': tnmask['want']}
    # H858 Part B: a card whose `german` echo dropped a masked span is REPAIRED from the source
    # skeleton instead of being nulled -- so the row must say so. Without this stamp a
    # machine-re-injected citation is indistinguishable in the store from one the model echoed
    # correctly, and the repair's real-world precision could never be audited after the fact
    # (the exact H1150/H1226 "denominator 1" trap the tnmask pairing above exists to avoid).
    # Same discipline: carried only when well-formed, never fabricated, never back-filled.
    anchor = card.get('german_anchor')
    if isinstance(anchor, dict) and isinstance(anchor.get('reinjected'), list):
        prov['german_anchor'] = {'reinjected': [str(t) for t in anchor['reinjected']],
                                 'head': [str(t) for t in anchor.get('head') or []]}
    return prov


TN_RE = re.compile(r'\{T\d+\}')


class UnrestoredPlaceholder(Exception):
    """A card reached the promote path still carrying a `{Tn}` mask placeholder (C-01)."""


class PromotionContractError(Exception):
    """The candidate cannot independently prove schema, provenance, and key scope."""


HEX64_RE = re.compile(r'^[0-9a-f]{64}$')
SYNTHETIC_KEY_RE = re.compile(r'^(?:dq_canary_|zz~~synthetic|synthetic[_~-])', re.I)


def validate_promotion_entry(subkey, entry):
    """Second-line promotion validation, independent of audit/coordinator state."""
    card = entry.get('card') or {}
    meta = entry.get('meta') or {}
    if meta.get('execution_manifest_schema') != 'pwg.headless_execution_manifest.v2':
        raise PromotionContractError(
            '%s: v1/unbound workflow output is historical-only and cannot be promoted' % subkey)
    execution = meta.get('execution') or {}
    for name in ('profile_slot', 'config_dir_fingerprint', 'execution_route',
                 'executor_lane', 'validation_method', 'model_identifier'):
        if not isinstance(execution.get(name), str) or not execution[name].strip():
            raise PromotionContractError('%s: missing manifest-v2 execution.%s' % (subkey, name))
    try:
        validate_final_card_schema.validate_card(card)
    except ValueError as exc:
        raise PromotionContractError('%s: final-card schema: %s' % (subkey, exc))

    selected = meta.get('selected_keys')
    if not isinstance(selected, list) or selected.count(subkey) != 1:
        raise PromotionContractError(
            '%s: selected_keys must contain this key exactly once' % subkey)
    if len(selected) != len(set(selected)):
        raise PromotionContractError('%s: execution selected_keys contains duplicates' % subkey)
    hashes = (meta.get('input_hashes') or {}).get(subkey)
    if not isinstance(hashes, dict):
        raise PromotionContractError('%s: missing per-key input hashes' % subkey)
    for name in ('raw_sha256', 'portrait_sha256'):
        value = hashes.get(name)
        if not isinstance(value, str) or not HEX64_RE.fullmatch(value.lower()):
            raise PromotionContractError('%s: malformed %s' % (subkey, name))
    for name in ('generator', 'schema_version', 'generated_at'):
        if not isinstance(meta.get(name), str) or not meta[name].strip():
            raise PromotionContractError('%s: missing provenance field meta.%s' % (subkey, name))

    classes = meta.get('provenance_classes')
    provenance_class = classes.get(subkey) if isinstance(classes, dict) else meta.get('provenance_class')
    if provenance_class == 'synthetic_control' or SYNTHETIC_KEY_RE.search(subkey):
        raise PromotionContractError('%s: synthetic controls are never promotable' % subkey)
    if provenance_class != 'real':
        raise PromotionContractError('%s: unknown provenance_class %r'
                                     % (subkey, provenance_class))

    if meta.get('nominal'):
        keymap = meta.get('nominal_keymap') or {}
        mapped = keymap.get(subkey)
        if mapped and card.get('key1') not in (mapped, subkey):
            raise PromotionContractError(
                '%s: nominal keymap/card mismatch (%r != %r)'
                % (subkey, card.get('key1'), mapped))
    elif not isinstance(meta.get('root'), str) or not meta['root']:
        raise PromotionContractError('%s: root-backed result has no root' % subkey)


def _serialize_rows(rows):
    """Canonical bytes installed by every promotion store replacement."""
    return b''.join(
        (json.dumps(row, ensure_ascii=False) + '\n').encode('utf-8')
        for row in rows)


def _atomic_write_rows(path, rows):
    directory = os.path.dirname(os.path.abspath(path)) or '.'
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.%s.' % os.path.basename(path), suffix='.tmp', dir=directory)
    try:
        with os.fdopen(fd, 'wb') as fh:
            fh.write(_serialize_rows(rows))
            fh.flush()
            os.fsync(fh.fileno())
        promotion_journal.durable_replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def _atomic_write_report(path, report, fault_hook=None):
    """Write a byte-stable report with injectable write/replace death points."""
    payload = promotion_journal.stable_json_bytes(report)
    directory = os.path.dirname(os.path.abspath(path)) or '.'
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix='.%s.' % os.path.basename(path), suffix='.tmp', dir=directory)
    try:
        with os.fdopen(fd, 'wb') as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        promotion_journal.fault(fault_hook, 'report_write')
        promotion_journal.durable_replace(tmp, path)
        promotion_journal.fault(fault_hook, 'report_replace')
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def _fsynced_backup(source, destination):
    """Exclusively copy the live store; never overwrite a prior recovery artifact."""
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with open(source, 'rb') as src, os.fdopen(fd, 'wb') as dst:
            fd = None
            shutil.copyfileobj(src, dst, length=1024 * 1024)
            dst.flush()
            os.fsync(dst.fileno())
    except BaseException:
        if fd is not None:
            os.close(fd)
        try:
            os.unlink(destination)
        except FileNotFoundError:
            pass
        raise


def _backup_path(store, merge):
    """Return a collision-resistant backup path without weakening O_EXCL protection."""
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    kind = 'premerge' if merge else 'legacy'
    return '%s.%s.%s.p%d.%s.bak' % (
        store, kind, stamp, os.getpid(), uuid.uuid4().hex[:12])


def validate_store_target(path, init_store=False):
    if not os.path.isfile(path) and not init_store:
        raise PromotionContractError(
            'canonical store is missing: %s. A missing/misresolved production store must not '
            'disable merge, shrink, or backup guards; use --init-store only for a deliberate '
            'first run.' % path)
    if os.path.exists(path) and init_store:
        raise PromotionContractError(
            '--init-store is first-run only; store already exists: %s' % path)


def _attempt_quality(rows):
    """Rank one subcard's row-set for better-attempt-wins: higher tuple = better attempt.

    (complete, -missing): a complete card (no partial_card marker) beats any partial;
    among partials, fewer missing fragments/groups beat more. Ties favour the INCOMING
    attempt (deliberate retranslation replaces same-quality content)."""
    prov = [row.get('provenance') or {} for row in rows]
    partial = any(p.get('partial_card') for p in prov)
    missing = 0
    for p in prov:
        mf = p.get('missing_fragments')
        n = len(mf) if isinstance(mf, list) else int(p.get('missing_groups') or 0)
        missing = max(missing, n)
    return (0 if partial else 1, -missing)


def human_touched(row):
    """True when a HUMAN has ruled on this store row (H2146 / FINDINGS §513).

    Three independent signals, any one protects the row from silent machine
    replacement: a named ``reviewer``; a ``review_status`` outside the machine
    vocabulary (machine statuses are ``ai_*`` — ``approved``/``needs_review``/
    any future human status protects); or a non-empty ``editorial_decision*``
    field. rows_for() stamps machine rows ``reviewer: None`` +
    ``review_status='ai_translated'``, so machine output never self-protects."""
    if row.get('reviewer'):
        return True
    status = row.get('review_status')
    if isinstance(status, str) and status and not status.startswith('ai_'):
        return True
    return any(k.startswith('editorial_decision') and row[k] for k in row)


def merge_store_rows(existing_rows, promoted_rows, override_reviewed=False):
    """Replace the promoted subcards BETTER-ATTEMPT-WINS; retain every unrelated row.

    B08 (H1339): the merge used to be an unconditional replace-by-subcard, so promoting an
    older/regressed artifact (a partial heal over a complete card) silently downgraded
    complete store rows. This is the store-level port of H304 rule 3 (save_and_audit
    --merge): complete beats partial, fewer missing fragments beat more, and only a tie or
    an improvement lets the incoming rows land.

    H2146 (FINDINGS §513): the merge additionally REFUSES to replace a subcard any of
    whose existing rows a human has touched (``human_touched``) — attempt quality alone
    used to return an ``approved`` row to ``ai_translated``/``reviewer: None`` with the
    human stamp gone. ``override_reviewed=True`` (the operator's explicit
    ``--override-reviewed``) restores the pre-H2146 behaviour for a deliberate
    re-translation of reviewed content.

    Returns (merged_rows, downgraded_subcards, protected_subcards): ``downgraded`` lists
    incoming subcards refused because the store holds a strictly better attempt;
    ``protected`` lists incoming subcards refused because a human touched the existing
    rows. Both keep their existing rows untouched."""
    incoming = {}
    for row in promoted_rows:
        incoming.setdefault(row['subcard'], []).append(row)
    existing_by_sub = {}
    for row in existing_rows:
        existing_by_sub.setdefault(row.get('subcard'), []).append(row)
    downgraded = sorted(
        sub for sub, rows in incoming.items()
        if sub in existing_by_sub
        and _attempt_quality(rows) < _attempt_quality(existing_by_sub[sub]))
    protected = [] if override_reviewed else sorted(
        sub for sub in incoming
        if sub in existing_by_sub and sub not in set(downgraded)
        and any(human_touched(r) for r in existing_by_sub[sub]))
    blocked = set(downgraded) | set(protected)
    replaced_subs = set(incoming) - blocked
    kept = [row for row in existing_rows if row.get('subcard') not in replaced_subs]
    landed = [row for row in promoted_rows if row['subcard'] not in blocked]
    return kept + landed, downgraded, protected


def tn_residue(card, rec, sense):
    """Report every promoted field of this row that still holds a raw `{Tn}`.

    The field list is `card_fields.PROMOTED_PAIRS`, NOT a local literal: a local literal here
    that drifted from the restore side is precisely what put 670 placeholder rows into the
    canonical store. Levels resolve against the three objects the caller already holds.
    """
    holder = {'card': card, 'record': rec, 'sense': sense}
    found = []
    for level, name in card_fields.PROMOTED_PAIRS:
        value = holder[level].get(name)
        if isinstance(value, str) and TN_RE.search(value):
            found.append('%s.%s=%r' % (level, name, value[:60]))
    return found


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
            # C-01: refuse to promote a row that still carries a mask placeholder. Every field
            # below is read straight into the canonical store, and four of them were never
            # restored -- 670 rows landed with a raw {Tn}, 223 of them in the HEADWORD. The
            # restore side is driven from `card_fields`; this is the promote side's own
            # burden-of-proof check, so a future restore gap fails loudly HERE rather than
            # accumulating silently in canonical data.
            residue = tn_residue(card, rec, sense)
            if residue:
                raise UnrestoredPlaceholder(
                    '%s: refusing to promote a card with unrestored placeholders: %s'
                    % (subkey, '; '.join(residue)))
            de = sense.get('german')
            # Always stamp from DE at promote time so new windows do not wait on a
            # separate annotate_government backfill pass (H1624 G2). Empty list when
            # the sense governs nothing — same shape as schemas/pwg_ru_final_card.
            yield {
                'key1': key1,
                'subcard': subkey,
                'layer': layer,
                'iast': card.get('iast'),
                'h': rec.get('h'),
                'grammar': rec.get('grammar'),
                'sense_tag': sense.get('tag'),
                'ru': ru,
                'de': de,
                'government': extract_government(de),
                'form_labels': extract_form_labels(de),
                # Dedicated nom/voc form-note field (not Rektion; not mixed into
                # number/gender/voice consumers — H1624 form_notes).
                'form_notes': extract_form_notes(de),
                # H1624 G3: normalized DE citation edges (raw <ls> stays in de).
                'citation_edges': extract_citation_edges(de),
                # H1624 G4: edition-relationship flags (H180 typology machine class).
                # PW gender-correction needs a PWG peer; promote stamps the layer rule
                # default (restate for pw); annotate_edition_rel fills pw_correct later.
                'edition_rel': classify_edition_rel(
                    layer, sense.get('tag'), de,
                    key1=key1, subcard=subkey),
                'equivalence_type': sense.get('equivalence_type'),
                'source_type': sense.get('source_type'),
                'stratum': sense.get('stratum'),
                'differentia': sense.get('differentia'),
                'review_status': review_status,
                'reviewer': None,
                'provenance': prov,
            }


def collect_and_validate(paths, review_status, gen_model_version):
    """Collect + fully validate one promotion source set -> (best, rows, per_root).

    Factored out of main() so the batched multi-lease transaction (H1339 Phase 3) runs the
    IDENTICAL per-entry validation chain: validate_promotion_entry, the B20 model-identity
    cross-check, rows_for (with its C-01 residue refusal), and the zero-row refusal."""
    best, conflicts, null_keys = collect_cards(paths)
    if conflicts:
        raise PromotionContractError('duplicate non-null workflow keys: %s'
                                     % ', '.join(sorted(set(conflicts))[:20]))
    rows, per_root = [], {}
    for subkey, entry in sorted(best.items()):
        validate_promotion_entry(subkey, entry)
        exec_model = ((entry.get('meta') or {}).get('execution') or {}).get('model_identifier')
        if exec_model and exec_model != gen_model_version:
            raise PromotionContractError(
                '%s: --gen-model-version %r does not match the manifest '
                'execution.model_identifier %r' % (subkey, gen_model_version, exec_model))
        n = 0
        for row in rows_for(subkey, entry, review_status, gen_model_version):
            rows.append(row)
            n += 1
        if n == 0:
            raise PromotionContractError(
                '%s: passed collection but yielded no promotable Russian rows' % subkey)
        root = entry['meta'].get('root')
        per_root.setdefault(root, {'cards': 0, 'rows': 0})
        per_root[root]['cards'] += 1
        per_root[root]['rows'] += n
    return best, rows, null_keys, per_root


def batch_promote(batch, store, review_status, gen_model_version,
                  no_backup=False, steal_lock=False, lock_ttl_seconds=None,
                  report_path=None, journal_path=None, promotion_id=None,
                  fault_hook=None, store_claim_held=False, override_reviewed=False):
    """H1339 Phase 3: promote N leases' clean outputs in ONE store transaction.

    Replaces the per-lease subprocess loop (N x [full store read + duplicate scan +
    overwrite-guard re-read + full backup copy + full atomic rewrite] + interpreter
    startups) with exactly ONE claim -> read -> merge -> guard -> backup -> write. The
    contract, per the H1339 spec:

      1. every lease is validated independently (the identical single-lease chain) and its
         audit/provenance attribution is preserved per row (rows_for stamps per-card meta);
      2. one exclusive backup, at most one atomic store replacement;
      3. every lease's exact expected subcard set must LAND (a better-attempt refusal or a
         cross-lease overlap FAILS THE BUNDLE -- promoting freshly-audited content that the
         store already beats means something is operationally wrong; no current-row
         regression is possible because the merge is still better-attempt-wins);
      4. the card TM is NOT rebuilt here -- the caller (coordinator.promote_ready) rebuilds
         it once after the transaction, exactly as before;
      5. any failure before the atomic replace leaves the store byte-identical;
      6. idempotent and byte-stable: a rerun with the same inputs writes the same rows.
      7. every mutating bundle requires ``journal_path`` + ``promotion_id`` and
         a before-store backup; unjournaled/no-backup batch writes are refused.

    `batch` is a list of {'lease_id', 'glob' (ABSOLUTE or repo-relative), 'expected_subcards'}.
    Returns the per-lease report dict (also written to `report_path` when given)."""
    if not journal_path:
        raise PromotionContractError(
            'mutating batch promotion requires --journal')
    if not promotion_id:
        raise PromotionContractError(
            'mutating batch promotion requires a stable --promotion-id')
    if no_backup:
        raise PromotionContractError(
            'journaled batch promotion requires a recovery backup')
    validate_store_target(store)
    lease_best, lease_rows, lease_nulls, lease_paths = {}, {}, {}, {}
    all_rows, seen_subs = [], {}
    for item in batch:
        lease_id = item['lease_id']
        if lease_id in lease_best:
            raise PromotionContractError('duplicate lease_id in batch: %s' % lease_id)
        paths = sorted(glob.glob(item['glob'] if os.path.isabs(item['glob'])
                                 else os.path.join(ROOT, item['glob'])))
        if not paths:
            raise PromotionContractError('%s: no clean output matched %r'
                                         % (lease_id, item['glob']))
        best, rows, nulls, _per_root = collect_and_validate(
            paths, review_status, gen_model_version)
        expected = sorted(item.get('expected_subcards') or [])
        # H1386 P3g: an entry with no expected_subcards made the subcard-set gate a silent
        # no-op (the coordinator always supplies it; only a hand-written manifest can omit
        # it, which is exactly when the gate matters most).
        if not expected:
            raise PromotionContractError(
                '%s: batch entry has no expected_subcards -- refusing a vacuous '
                'subcard-set gate; supply the lease expectation explicitly' % lease_id)
        got = sorted(best)
        if got != expected:
            raise PromotionContractError(
                '%s: clean output subcards %s do not match the lease expectation %s'
                % (lease_id, got, expected))
        if nulls:
            # H1386 P3g: single mode prints these; batch mode silently dropped them.
            print('%s: null sub-cards skipped: %d (%s)'
                  % (lease_id, len(nulls), ', '.join(nulls[:10])))
        lease_nulls[lease_id] = nulls
        for sub in best:
            if sub in seen_subs:
                raise PromotionContractError(
                    'subcard %s appears in BOTH lease %s and lease %s -- divergent bundle'
                    % (sub, seen_subs[sub], lease_id))
            seen_subs[sub] = lease_id
        lease_best[lease_id] = best
        lease_rows[lease_id] = rows
        lease_paths[lease_id] = paths
        all_rows.extend(rows)

    bindings = {
        item['lease_id']: {
            'run_id': (str(item['run_id']) if item.get('run_id') is not None else None),
            'attempt_id': (str(item['attempt_id'])
                           if item.get('attempt_id') is not None else None),
        }
        for item in batch
    }
    current_clean = promotion_journal.aggregate_files(
        [path for paths in lease_paths.values() for path in paths])
    current_clean.update({
        'subcards': sorted(seen_subs),
        'subcard_count': len(seen_subs),
        'card_count': len(seen_subs),
        'sense_rows': len(all_rows),
    })
    current_lease_facts = {
        lease_id: {
            'binding': bindings[lease_id],
            'clean_output': promotion_journal.aggregate_files(lease_paths[lease_id]),
            'subcard_keys': sorted(lease_best[lease_id]),
            'subcards': len(lease_best[lease_id]),
        }
        for lease_id in sorted(lease_best)
    }
    ttl_kwargs = {'ttl_seconds': lock_ttl_seconds} if lock_ttl_seconds else {}
    claim = (contextlib.nullcontext() if store_claim_held
             else PromoteClaim(store, steal=steal_lock, **ttl_kwargs))
    with claim:
        # A journal that already sealed/committed these bytes is reconciled
        # before the live store is treated as a new "before" image.
        if journal_path and os.path.exists(journal_path):
            sealed = promotion_journal.load(journal_path)
            mismatches = []
            checks = {
                'promotion_id': (sealed['promotion_id'], promotion_id),
                'canonical store path': (
                    sealed['store']['path'], promotion_journal.canonical_path(store)),
                'review_status': (sealed['review_status'], review_status),
                'exact model': (sealed['model_identifier'], gen_model_version),
                'lease ids': (sealed['lease_ids'], sorted(lease_best)),
                'bindings': (sealed['bindings'], bindings),
                'clean output': (sealed['clean_output'], current_clean),
                'report path': (
                    sealed['report'].get('report_path'),
                    (promotion_journal.canonical_path(report_path)
                     if report_path else None)),
            }
            for label, (left, right) in checks.items():
                if left != right:
                    mismatches.append('%s (%r != %r)' % (label, left, right))
            for lease_id, facts in current_lease_facts.items():
                sealed_metrics = (sealed.get('leases') or {}).get(lease_id) or {}
                for name in ('clean_output', 'subcard_keys', 'subcards'):
                    if sealed_metrics.get(name) != facts[name]:
                        mismatches.append('%s.%s changed' % (lease_id, name))
            if mismatches:
                raise PromotionContractError(
                    'journal retry intent mismatch: %s' % '; '.join(mismatches))
            reconciled = promotion_journal.reconcile(
                journal_path, store_claim_held=True)
            if reconciled['action'] in ('adopt_store_commit',
                                         'already_store_committed',
                                         'terminal_complete'):
                sealed = promotion_journal.load(journal_path)
                sealed_backup = sealed['store'].get('backup')
                if sealed_backup and sealed_backup.get('path'):
                    if not os.path.isfile(sealed_backup['path']):
                        raise PromotionContractError(
                            'sealed promotion backup is missing: %s'
                            % sealed_backup['path'])
                    observed_backup = promotion_journal.file_fingerprint(
                        sealed_backup['path'])
                    if (observed_backup['sha256'] != sealed_backup['sha256']
                            or observed_backup['rows'] != sealed_backup['rows']):
                        raise PromotionContractError(
                            'sealed promotion backup hash/rows do not match')
                report = dict(sealed['report'])
                if report_path:
                    _atomic_write_report(report_path, report, fault_hook)
                return report

        existing_rows = []
        if os.path.exists(store):
            with open(store, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        existing_rows.append(json.loads(line))
        # H1386 D3: per-lease attribution needs the pre-merge per-subcard row counts --
        # the bundle-wide before/after stamped on every lease made a benign idempotent
        # replacement indistinguishable from a real landing in the per-lease consumers
        # (promotion_classification, bad_deltas, the windows100 GO gate).
        existing_count_by_sub = {}
        for row in existing_rows:
            sub = row.get('subcard')
            existing_count_by_sub[sub] = existing_count_by_sub.get(sub, 0) + 1
        rows_to_write, downgraded, protected = merge_store_rows(
            existing_rows, all_rows, override_reviewed=override_reviewed)
        if downgraded:
            raise PromotionContractError(
                'bundle failed, store unchanged: the store already holds a strictly '
                'better attempt for %d subcard(s) (%s) -- a freshly audited lease should '
                'never lose better-attempt-wins; inspect before promoting'
                % (len(downgraded), ', '.join(downgraded[:10])))
        if protected:
            # H2146: a coordinator window should never silently re-land a subcard a human
            # has ruled on -- that returns approved rows to ai_translated/reviewer: None.
            raise PromotionContractError(
                'bundle failed, store unchanged: %d subcard(s) carry HUMAN-REVIEWED store '
                'rows (%s) -- machine replacement would wipe the review overlay (FINDINGS '
                '§513). Re-run with override_reviewed/--override-reviewed only for a '
                'deliberate re-translation of reviewed content'
                % (len(protected), ', '.join(protected[:10])))
        landed_subs = {r['subcard'] for r in rows_to_write}
        for lease_id, best in lease_best.items():
            missing = sorted(set(best) - landed_subs)
            if missing:
                raise PromotionContractError(
                    '%s: expected subcard(s) did not land: %s' % (lease_id, missing))
        identities = [(r.get('key1'), r.get('subcard'), r.get('h'),
                       r.get('sense_tag'), r.get('de')) for r in rows_to_write]
        duplicates = [i for i, n in collections.Counter(identities).items() if n > 1]
        if duplicates:
            raise PromotionContractError(
                'promotion would create %d duplicate sense identity/identities'
                % len(duplicates))
        before = len(existing_rows)
        if before and len(rows_to_write) < before * 0.5:
            raise PromotionContractError(
                'would shrink store %d -> %d rows (>50%% loss)' % (before, len(rows_to_write)))
        before_fp = promotion_journal.file_fingerprint(store)
        expected_payload = _serialize_rows(rows_to_write)
        expected_fp = promotion_journal.bytes_fingerprint(store, expected_payload)

        # H1386 D3: per-lease rows_added / rows_replaced / store_delta. The bundle is
        # all-or-nothing (every incoming row landed or we raised above), so these are exact.
        def _lease_delta(lease_id, best):
            inc = lease_rows[lease_id]
            new_subs = {sub for sub in best if sub not in existing_count_by_sub}
            prior_rows = sum(existing_count_by_sub.get(sub, 0) for sub in best)
            return {
                'rows_added': sum(1 for r in inc if r['subcard'] in new_subs),
                'rows_replaced': sum(1 for r in inc if r['subcard'] not in new_subs),
                'store_delta': len(inc) - prior_rows,
            }

        per_lease_metrics = {
            lease_id: dict({
                'run_id': bindings[lease_id]['run_id'],
                'attempt_id': bindings[lease_id]['attempt_id'],
                'clean_output': current_lease_facts[lease_id]['clean_output'],
                'subcards': len(best),
                'subcard_keys': sorted(best),
                'rows': len(lease_rows[lease_id]),
                'null_subcards': lease_nulls.get(lease_id) or [],
            }, **_lease_delta(lease_id, best))
            for lease_id, best in lease_best.items()
        }
        bak = (_backup_path(store, True) if not os.path.exists(journal_path)
               else promotion_journal.load(journal_path)['store']['backup']['path'])
        store_record = {
            'path': promotion_journal.canonical_path(store),
            'before_sha256': before_fp['sha256'],
            'before_rows': before_fp['rows'],
            'before_bytes': before_fp['bytes'],
            'expected_after_sha256': expected_fp['sha256'],
            'expected_after_rows': expected_fp['rows'],
            'expected_after_bytes': expected_fp['bytes'],
            'backup_path': promotion_journal.canonical_path(bak),
            'backup': {
                'path': promotion_journal.canonical_path(bak),
                'sha256': before_fp['sha256'],
                'rows': before_fp['rows'],
                'bytes': before_fp['bytes'],
            },
        }
        report = {
            'schema': 'pwg.batch_promotion.v1',
            'promotion_id': promotion_id,
            'journal': promotion_journal.canonical_path(journal_path),
            'journal_phase': 'store_committed',
            'report_path': (promotion_journal.canonical_path(report_path)
                            if report_path else None),
            'model_identifier': gen_model_version,
            'review_status': review_status,
            'clean_output_sha256': current_clean['sha256'],
            'store_sha256': expected_fp['sha256'],
            'store_rows_before': before,
            'store_rows_after': len(rows_to_write),
            'leases': per_lease_metrics,
        }
        promotion_journal.prepare(
            journal_path,
            promotion_id=promotion_id,
            lease_ids=sorted(lease_best),
            run_ids={lease_id: metrics['run_id']
                     for lease_id, metrics in per_lease_metrics.items()
                     if metrics.get('run_id')},
            bindings=bindings,
            model_identifier=gen_model_version,
            review_status=review_status,
            clean_output=current_clean,
            store=store_record,
            leases=per_lease_metrics,
            report=report,
            fault_hook=fault_hook,
        )

        if bak:
            if os.path.exists(bak):
                observed_backup = promotion_journal.file_fingerprint(bak)
                if (observed_backup['sha256'] != before_fp['sha256']
                        or observed_backup['rows'] != before_fp['rows']):
                    raise PromotionContractError(
                        'prepared backup exists but does not match the sealed before store')
            else:
                _fsynced_backup(store, bak)
                print('backed up prior store -> %s' % os.path.basename(bak))
        _atomic_write_rows(store, rows_to_write)
        promotion_journal.fault(fault_hook, 'store_replace')
        promotion_journal.fault(fault_hook, 'after_store_replace_before_phase')
        if journal_path:
            promotion_journal.mark_store_committed(
                journal_path, store_claim_held=True)

    sealed = promotion_journal.load(journal_path)
    report = dict(sealed['report'])
    print('BATCH PROMOTE: %d lease(s), %d subcard(s), %d sense rows; store %d -> %d rows'
          % (len(batch), len(seen_subs), len(all_rows), before, len(rows_to_write)))
    for lease_id in sorted(report['leases']):
        row = report['leases'][lease_id]
        print('  %s: %d subcard(s), %d row(s)' % (lease_id, row['subcards'], row['rows']))
    # Journaled promotion deliberately leaves temporary denials in force here.
    # The coordinator first harvests corrected frag_prov rows while the rejected
    # cached fsha is still excluded, then atomically appends the unblock and seals
    # both sidecars at DERIVED_VALIDATED.
    if report_path:
        _atomic_write_report(report_path, report, fault_hook)
    return report


def selftest():
    import tempfile
    meta = {'root': 'pA', 'safe_root': 'p_a', 'generator': 'gen_opt_harness2.batched-masked',
            'schema_version': 'v1', 'rootmap_sha256': 'abc', 'generated_at': '2026-06-29T00:00:00Z',
            'selected_keys': ['p_a~~h5_00_pwg00'],
            'execution_manifest_schema': 'pwg.headless_execution_manifest.v2',
            'execution': {'profile_slot': 'c4', 'config_dir_fingerprint': 'f' * 64,
                          'execution_route': 'claude-cli-headless',
                          'executor_lane': 'serial-whole-card',
                          'validation_method': 'audit_window+final_schema',
                          'model_identifier': 'claude-sonnet-5'},
            'provenance_classes': {'p_a~~h5_00_pwg00': 'real'},
            'input_hashes': {'p_a~~h5_00_pwg00': {
                'raw_sha256': '1' * 64, 'portrait_sha256': '2' * 64}}}
    entry = {'card': {'key1': 'p_a~~h5_00_pwg00', 'iast': 'pā', 'notes': '', 'records': [
        {'h': 'pā', 'grammar': '', 'senses': [
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
    assert r.get('government') == [], 'plain DE with no Rektion must stamp government=[]'
    assert r.get('form_labels') == [], 'plain DE with no form labels must stamp form_labels=[]'
    assert r.get('form_notes') == [], 'plain DE with no nom/voc must stamp form_notes=[]'
    assert r.get('citation_edges') == [], 'plain DE with no <ls> must stamp citation_edges=[]'
    assert r.get('edition_rel', {}).get('subtype') == 'base', r.get('edition_rel')
    # H1624 G2: PW capitalized (Instr.) must be stamped at promote time from DE only
    gov_entry = {'card': {'key1': 'vas~~h0_zz_pw00', 'iast': 'vas', 'notes': '', 'records': [
        {'h': 'vas', 'grammar': '', 'senses': [
            {'tag': 'samava', 'russian': 'обёрнутый',
             'german': '<div n="m">— <ab>Caus.</ab> {#prativAsita#} {%gehüllt in%} '
                       '(<ab>Instr.</ab>).',
             'equivalence_type': 'explanatory', 'source_type': 'lexicographic',
             'stratum': '', 'differentia': ''},
        ]}]}, 'meta': dict(meta, root='vas', selected_keys=['vas~~h0_zz_pw00'],
                           provenance_classes={'vas~~h0_zz_pw00': 'real'},
                           input_hashes={'vas~~h0_zz_pw00': {
                               'raw_sha256': '1' * 64, 'portrait_sha256': '2' * 64}}),
                  'wf_file': 'wf_output.json'}
    grow = list(rows_for('vas~~h0_zz_pw00', gov_entry, 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]
    assert grow['government'] and grow['government'][0]['cases'] == ['instr'], grow
    assert grow['government'][0]['span'] == '(<ab>Instr.</ab>)', grow
    # H1624 form-layer: gender + number + voc on one DE sense
    form_entry = {'card': {'key1': 'deva~~h0_00_pwg00', 'iast': 'deva', 'notes': '', 'records': [
        {'h': 'deva', 'grammar': '', 'senses': [
            {'tag': '1', 'russian': 'бог',
             'german': '<lex>m.</lex> {%Gott%} (<ab>pl.</ab>) <ls>ṚV. 1,1,1</ls>. '
                       '(<ab>voc.</ab>) auch so.',
             'equivalence_type': 'equivalent', 'source_type': 'lexicographic',
             'stratum': '', 'differentia': ''},
        ]}]}, 'meta': dict(meta, root='deva', selected_keys=['deva~~h0_00_pwg00'],
                           provenance_classes={'deva~~h0_00_pwg00': 'real'},
                           input_hashes={'deva~~h0_00_pwg00': {
                               'raw_sha256': '1' * 64, 'portrait_sha256': '2' * 64}}),
                  'wf_file': 'wf_output.json'}
    frow = list(rows_for('deva~~h0_00_pwg00', form_entry, 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]
    axes = {(h['axis'], h['value']) for h in frow['form_labels']}
    assert ('gender', 'm') in axes and ('number', 'pl') in axes and ('case_form', 'voc') in axes, frow
    # Dedicated form_notes field for nom/voc
    assert frow['form_notes'] and frow['form_notes'][0]['case'] == 'voc', frow
    assert frow['form_notes'][0]['span'] == '(<ab>voc.</ab>)', frow
    # Rektion loc must NOT land in form_labels or form_notes
    assert not any(h.get('value') == 'loc' for h in frow['form_labels']), frow
    assert not any(n.get('case') in ('loc', 'instr', 'acc') for n in frow['form_notes']), frow
    # H1624 G3: citation_edges from DE <ls>
    cite_entry = {'card': {'key1': 'agni~~h0_00_pwg00', 'iast': 'agni', 'notes': '', 'records': [
        {'h': 'agni', 'grammar': '', 'senses': [
            {'tag': '1', 'russian': 'огонь',
             'german': '{%Feuer%} <ls>ṚV. 1,1,1</ls>; <ls n="MBH.">3,50</ls>.',
             'equivalence_type': 'equivalent', 'source_type': 'lexicographic',
             'stratum': '', 'differentia': ''},
        ]}]}, 'meta': dict(meta, root='agni', selected_keys=['agni~~h0_00_pwg00'],
                           provenance_classes={'agni~~h0_00_pwg00': 'real'},
                           input_hashes={'agni~~h0_00_pwg00': {
                               'raw_sha256': '1' * 64, 'portrait_sha256': '2' * 64}}),
                  'wf_file': 'wf_output.json'}
    crow = list(rows_for('agni~~h0_00_pwg00', cite_entry, 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]
    assert len(crow['citation_edges']) == 2, crow
    assert crow['citation_edges'][0]['siglum'] == 'ṚV', crow
    assert crow['citation_edges'][0]['resolver_status'] == 'map', crow
    assert crow['citation_edges'][0]['page'] == '1,1,1', crow
    # raw DE still holds the markup
    assert '<ls>ṚV. 1,1,1</ls>' in crow['de'], crow
    # H1624 G4: edition_rel on overlay layers
    sch_entry = {'card': {'key1': 'ap~~h0_zz_sch', 'iast': 'ap', 'notes': '', 'records': [
        {'h': 'ap', 'grammar': '', 'senses': [
            {'tag': 'anu_desid', 'russian': 'соглашаться',
             'german': '{%einstimmen%}',
             'equivalence_type': 'equivalent', 'source_type': 'lexicographic',
             'stratum': '', 'differentia': ''},
        ]}]}, 'meta': dict(meta, root='Ap', selected_keys=['ap~~h0_zz_sch'],
                           provenance_classes={'ap~~h0_zz_sch': 'real'},
                           input_hashes={'ap~~h0_zz_sch': {
                               'raw_sha256': '1' * 64, 'portrait_sha256': '2' * 64}}),
                  'wf_file': 'wf_output.json'}
    srow = list(rows_for('ap~~h0_zz_sch', sch_entry, 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]
    assert srow['layer'] == 'sch', srow
    assert srow['edition_rel']['subtype'] == 'derived_sense', srow['edition_rel']
    assert srow['edition_rel']['source_layers'] == ['sch'], srow['edition_rel']
    pw_entry = {'card': {'key1': 'g~~h0_zz_pw01', 'iast': 'g', 'notes': '', 'records': [
        {'h': 'g', 'grammar': '', 'senses': [
            {'tag': '1', 'russian': 'идти', 'german': '{%gehen%}',
             'equivalence_type': 'equivalent', 'source_type': 'lexicographic',
             'stratum': '', 'differentia': ''},
        ]}]}, 'meta': dict(meta, root='gA', selected_keys=['g~~h0_zz_pw01'],
                           provenance_classes={'g~~h0_zz_pw01': 'real'},
                           input_hashes={'g~~h0_zz_pw01': {
                               'raw_sha256': '1' * 64, 'portrait_sha256': '2' * 64}}),
                  'wf_file': 'wf_output.json'}
    prow = list(rows_for('g~~h0_zz_pw01', pw_entry, 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]
    assert prow['edition_rel']['subtype'] == 'restate', prow['edition_rel']
    assert prow['edition_rel']['direction'] == 'abridging', prow['edition_rel']
    assert list(rows_for('x~~h0_zz_pw01', dict(entry, meta=meta), 'ai_translated',
                         SELFTEST_MODEL_VERSION))[0]['layer'] == 'pw', 'addenda sub-card -> layer=pw'
    assert r['review_status'] == 'ai_translated', 'must not auto-approve (G5 gate)'
    p = r['provenance']
    assert p['model'] == 'sonnet' and p['rootmap_sha256'] == 'abc'
    assert p['model_version'] == SELFTEST_MODEL_VERSION, 'model VERSION recorded, not just the tier alias'
    assert p['input_raw_sha256'] == '1' * 64 and p['generated_at'], 'provenance must be complete'
    validate_promotion_entry('p_a~~h5_00_pwg00', entry)
    historical = {'card': entry['card'], 'wf_file': entry['wf_file'],
                  'meta': dict(meta, execution_manifest_schema=
                               'pwg.headless_execution_manifest.v1')}
    try:
        validate_promotion_entry('p_a~~h5_00_pwg00', historical)
    except PromotionContractError:
        pass
    else:
        raise AssertionError('historical v1 output passed new production promotion')
    synthetic = {'card': entry['card'], 'wf_file': entry['wf_file'],
                 'meta': dict(meta, provenance_classes={
                     'p_a~~h5_00_pwg00': 'synthetic_control'})}
    try:
        validate_promotion_entry('p_a~~h5_00_pwg00', synthetic)
    except PromotionContractError:
        pass
    else:
        raise AssertionError('synthetic control passed promotion validation')
    foreign = {'card': entry['card'], 'wf_file': entry['wf_file'],
               'meta': dict(meta, selected_keys=['some_other_key'])}
    try:
        validate_promotion_entry('p_a~~h5_00_pwg00', foreign)
    except PromotionContractError:
        pass
    else:
        raise AssertionError('foreign key passed promotion validation')
    # NOMINAL mode: meta.root is a window LABEL; the row must key to the true SLP1 headword
    # recovered from nominal_keymap[stem], NOT to the label (regression guard, H179 drain).
    nmeta = {'root': 'pril10_w1', 'nominal': True, 'nominal_keymap': {'k_ala': 'kAla'},
             'input_hashes': {'k_ala': {'raw_sha256': 'r', 'portrait_sha256': 'p'}}}
    ncard = {'key1': 'kAla', 'iast': 'kāla', 'notes': '',
             'records': [{'h': 'kāla', 'grammar': '',
                          'senses': [{'tag': '1', 'russian': 'время', 'german': 'Zeit'}]}]}
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
    # H1226: the pre-restore {Tn} pairing rides on provenance when the card carries it, is absent
    # (never fabricated) for pre-H1226 cards, and a malformed pairing is dropped rather than stored.
    assert 'tnmask' not in p, 'a card without tnmask must not fabricate one in provenance'
    tnentry = dict(entry, card=dict(entry['card'], tnmask={'got': 'T1 T2', 'want': 'T1 T2 T3'}))
    tp = list(rows_for('p_a~~h5_00_pwg00', tnentry, 'ai_translated',
                       SELFTEST_MODEL_VERSION))[0]['provenance']
    assert tp['tnmask'] == {'got': 'T1 T2', 'want': 'T1 T2 T3'}, \
        'the pre-restore {Tn} pairing must ride on the promoted row provenance'
    badentry = dict(entry, card=dict(entry['card'], tnmask={'got': 'T1'}))   # missing `want`
    bp = list(rows_for('p_a~~h5_00_pwg00', badentry, 'ai_translated',
                       SELFTEST_MODEL_VERSION))[0]['provenance']
    assert 'tnmask' not in bp, 'a malformed tnmask pairing must not be promoted'
    # H858 Part B: a card repaired by the german-anchor lane must SAY SO on every row it yields --
    # otherwise a machine-re-injected citation is indistinguishable in the store from one the model
    # echoed correctly, and the repair's real-world precision is unauditable after the fact. Same
    # discipline as tnmask above: never fabricated, and a malformed stamp is dropped.
    assert 'german_anchor' not in p, 'an unrepaired card must not fabricate a german_anchor stamp'
    garow = list(rows_for('p_a~~h5_00_pwg00',
                          dict(entry, card=dict(entry['card'],
                                                german_anchor={'reinjected': ['T4'], 'head': []})),
                          'ai_translated', SELFTEST_MODEL_VERSION))[0]['provenance']
    assert garow['german_anchor'] == {'reinjected': ['T4'], 'head': []}, \
        'a german-anchor repair must ride on the promoted row provenance'
    gabad = list(rows_for('p_a~~h5_00_pwg00',
                          dict(entry, card=dict(entry['card'], german_anchor={'head': []})),
                          'ai_translated', SELFTEST_MODEL_VERSION))[0]['provenance']
    assert 'german_anchor' not in gabad, 'a malformed german_anchor stamp must not be promoted'
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
    # Byte-equivalent recovered artifacts collapse; divergent cards/provenance fail closed.
    dupf = os.path.join(d, 'wf_output.duplicate.x.json')
    with open(dupf, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [
            {'key': 'p_a~~h5_00_pwg00', 'card': entry['card']}]}, f)
    best, duplicate_conflicts, _nulls = collect_cards([fullf, dupf])
    assert len(best) == 1 and duplicate_conflicts == [], \
        'byte-equivalent workflow cards must deduplicate without a conflict'
    divergent = os.path.join(d, 'wf_output.divergent.x.json')
    changed_card = json.loads(json.dumps(entry['card']))
    changed_card['records'][0]['senses'][0]['russian'] = 'выпить'
    with open(divergent, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [
            {'key': 'p_a~~h5_00_pwg00', 'card': changed_card}]}, f)
    _best, divergent_conflicts, _nulls = collect_cards([fullf, divergent])
    assert divergent_conflicts == ['p_a~~h5_00_pwg00'], \
        'different non-null translations for one key must conflict'
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
    # Missing stores fail closed; explicit first-run init is accepted only while absent.
    missing = os.path.join(d, 'missing-store.jsonl')
    try:
        validate_store_target(missing)
    except PromotionContractError:
        pass
    else:
        raise AssertionError('missing store passed without --init-store')
    validate_store_target(missing, init_store=True)
    with open(missing, 'w', encoding='utf-8') as f:
        f.write('')
    try:
        validate_store_target(missing, init_store=True)
    except PromotionContractError:
        pass
    else:
        raise AssertionError('--init-store overwrote an existing store')
    # Exact-subcard merge is idempotent; a second promotion replaces rather than duplicates.
    old = [{'key1': 'x', 'subcard': 'x~~a'}, {'key1': 'y', 'subcard': 'y~~a'}]
    new = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'new'}]
    once, dg1, pr1 = merge_store_rows(old, new)
    twice, dg2, pr2 = merge_store_rows(once, new)
    assert once == twice and len(once) == 2 and dg1 == [] and dg2 == []
    assert pr1 == [] and pr2 == [], 'unreviewed rows must not be protected'
    # B08 (H1339): the store merge is better-attempt-wins, the H304 rule ported to the
    # store level. A partial incoming attempt must NOT downgrade complete existing rows;
    # a complete incoming attempt replaces a partial; fewer missing fragments win among
    # partials; equal quality -> incoming wins (deliberate retranslation).
    complete_old = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'old-good', 'provenance': {}}]
    partial_new = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'new-partial',
                    'provenance': {'partial_card': True, 'missing_fragments': ['g1:f0']}}]
    merged, downgraded, _pr = merge_store_rows(complete_old, partial_new)
    assert merged == complete_old and downgraded == ['x~~a'], \
        'a partial attempt silently downgraded a complete store row'
    merged, downgraded, _pr = merge_store_rows(partial_new, complete_old)
    assert merged == complete_old and downgraded == [], \
        'a complete attempt must replace a partial store row'
    worse = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'p3',
              'provenance': {'partial_card': True,
                             'missing_fragments': ['g1:f0', 'g1:f1', 'g2:f0']}}]
    better = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'p1',
               'provenance': {'partial_card': True, 'missing_fragments': ['g1:f0']}}]
    merged, downgraded, _pr = merge_store_rows(worse, better)
    assert merged == better and downgraded == [], 'fewer missing fragments must win'
    merged, downgraded, _pr = merge_store_rows(better, worse)
    assert merged == better and downgraded == ['x~~a'], 'more missing fragments must lose'

    # H2146 (FINDINGS §513): human-touched store rows are PROTECTED from machine
    # replacement -- reviewer stamp, non-ai_* review_status, or editorial_decision*
    # each protect independently; --override-reviewed restores the old behaviour.
    machine_new = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'machine-redo',
                    'review_status': 'ai_translated', 'reviewer': None,
                    'provenance': {}}]
    for label, human_row in (
            ('approved+reviewer', {'key1': 'x', 'subcard': 'x~~a', 'ru': 'human-kept',
                                   'review_status': 'approved', 'reviewer': 'MG',
                                   'provenance': {}}),
            ('needs_review', {'key1': 'x', 'subcard': 'x~~a', 'ru': 'human-kept',
                              'review_status': 'needs_review', 'reviewer': None,
                              'provenance': {}}),
            ('editorial stamp', {'key1': 'x', 'subcard': 'x~~a', 'ru': 'human-kept',
                                 'review_status': 'ai_translated', 'reviewer': None,
                                 'editorial_decision_id': 'D42', 'provenance': {}})):
        merged, downgraded, protected = merge_store_rows([human_row], machine_new)
        assert merged == [human_row] and protected == ['x~~a'] and downgraded == [], \
            'human overlay (%s) must survive a machine re-promote' % label
        assert merged[0]['review_status'] == human_row['review_status'] \
            and merged[0].get('reviewer') == human_row.get('reviewer'), \
            'overlay fields must come back intact (%s)' % label
    # Explicit override lands the machine attempt (deliberate re-translation).
    approved = [{'key1': 'x', 'subcard': 'x~~a', 'ru': 'human-kept',
                 'review_status': 'approved', 'reviewer': 'MG', 'provenance': {}}]
    merged, downgraded, protected = merge_store_rows(
        approved, machine_new, override_reviewed=True)
    assert merged == machine_new and protected == [] and downgraded == [], \
        '--override-reviewed must land the machine attempt'
    # Unrelated subcards still merge normally next to a protected one.
    mixed_store = approved + [{'key1': 'y', 'subcard': 'y~~a', 'ru': 'old',
                               'review_status': 'ai_translated', 'provenance': {}}]
    incoming2 = machine_new + [{'key1': 'y', 'subcard': 'y~~a', 'ru': 'new',
                                'review_status': 'ai_translated', 'reviewer': None,
                                'provenance': {}}]
    merged, downgraded, protected = merge_store_rows(mixed_store, incoming2)
    assert protected == ['x~~a'] and downgraded == []
    assert any(r['subcard'] == 'y~~a' and r['ru'] == 'new' for r in merged), \
        'unprotected sibling subcards must still land'
    assert any(r['subcard'] == 'x~~a' and r['ru'] == 'human-kept' for r in merged)
    assert not human_touched({'review_status': 'ai_translated', 'reviewer': None}), \
        'machine rows must never self-protect'

    # H2146: store_write.locked_store_rewrite -- the shared mutator writer -- refuses
    # to write under a live PromoteClaim (lock serializes mutators against promotes).
    import store_write
    sw_store = os.path.join(d, 'sw-store.jsonl')
    store_write.locked_store_rewrite(sw_store, [{'subcard': 's1'}], tag='selftest')
    with PromoteClaim(sw_store):
        try:
            store_write.locked_store_rewrite(sw_store, [{'subcard': 's2'}], tag='selftest')
            raise AssertionError('locked_store_rewrite must raise ClaimBusy under a claim')
        except ClaimBusy:
            pass
    swb = store_write.locked_store_rewrite(sw_store, [{'subcard': 's3'}], tag='selftest')
    assert swb and os.path.isfile(swb), 'mutator rewrite must leave a unique backup'
    # Atomic failure leaves the old store intact and removes the temporary file.
    atomic = os.path.join(d, 'atomic.jsonl')
    with open(atomic, 'w', encoding='utf-8') as f:
        f.write('old\n')
    real_replace = promotion_journal.durable_replace
    try:
        promotion_journal.durable_replace = (
            lambda _src, _dst: (_ for _ in ()).throw(OSError('synthetic crash')))
        try:
            _atomic_write_rows(atomic, new)
        except OSError:
            pass
        else:
            raise AssertionError('atomic replace failure was swallowed')
    finally:
        promotion_journal.durable_replace = real_replace
    assert open(atomic, encoding='utf-8').read() == 'old\n'
    assert not [n for n in os.listdir(d) if n.endswith('.tmp')]
    # Backups are exclusive, collision-resistant copies. A failed copy leaves both the live
    # store and any earlier backup untouched and removes its incomplete destination.
    backup1 = _backup_path(atomic, True)
    backup2 = _backup_path(atomic, True)
    assert backup1 != backup2, 'two promotions must never share a backup name'
    _fsynced_backup(atomic, backup1)
    _fsynced_backup(atomic, backup2)
    assert open(backup1, encoding='utf-8').read() == 'old\n'
    assert open(backup2, encoding='utf-8').read() == 'old\n'
    try:
        _fsynced_backup(atomic, backup1)
    except FileExistsError:
        pass
    else:
        raise AssertionError('backup creation overwrote an existing recovery artifact')
    real_copyfileobj = shutil.copyfileobj
    failed_backup = _backup_path(atomic, False)
    try:
        shutil.copyfileobj = lambda *_args, **_kwargs: (_ for _ in ()).throw(
            OSError('synthetic backup failure'))
        try:
            _fsynced_backup(atomic, failed_backup)
        except OSError:
            pass
        else:
            raise AssertionError('backup copy failure was swallowed')
    finally:
        shutil.copyfileobj = real_copyfileobj
    assert open(atomic, encoding='utf-8').read() == 'old\n'
    assert not os.path.exists(failed_backup), 'partial backup survived a failed copy'
    # H1339 Phase 3: the batched multi-lease transaction — one claim/read/backup/write,
    # per-lease validation + attribution, all-or-nothing, idempotent, byte-stable.
    bd = tempfile.mkdtemp()
    bstore = os.path.join(bd, 'store.jsonl')
    keep_row = {'key1': 'y', 'subcard': 'y~~keep', 'h': 'y', 'sense_tag': '1',
                'de': 'x', 'ru': 'у', 'provenance': {}}
    with open(bstore, 'w', encoding='utf-8') as f:
        f.write(json.dumps(keep_row, ensure_ascii=False) + '\n')
    k2 = 'x~~h0_zz_pw01'
    meta2 = dict(meta, selected_keys=[k2],
                 provenance_classes={k2: 'real'},
                 input_hashes={k2: {'raw_sha256': '3' * 64, 'portrait_sha256': '4' * 64}})
    lease_files = {}
    for lease_id, key, m in (('L1', 'p_a~~h5_00_pwg00', meta), ('L2', k2, meta2)):
        d2 = os.path.join(bd, lease_id)
        os.makedirs(d2)
        fp = os.path.join(d2, 'wf_output.clean.%s.json' % lease_id)
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump({'meta': m, 'results': [{'key': key, 'card': entry['card']}]}, f)
        lease_files[lease_id] = (fp, key)
    batch = [{'lease_id': lid, 'run_id': 'run-' + lid,
              'attempt_id': 'attempt-' + lid,
              'glob': fp, 'expected_subcards': [key]}
             for lid, (fp, key) in lease_files.items()]
    unjournaled_before = open(bstore, 'rb').read()
    try:
        batch_promote(batch, bstore, 'ai_translated', SELFTEST_MODEL_VERSION)
        raise AssertionError('unjournaled mutating batch was accepted')
    except PromotionContractError as exc:
        assert 'requires --journal' in str(exc)
    assert open(bstore, 'rb').read() == unjournaled_before
    batch_journal = os.path.join(bd, 'batch.journal.json')
    batch_report = os.path.join(bd, 'batch.report.json')
    rep = batch_promote(
        batch, bstore, 'ai_translated', SELFTEST_MODEL_VERSION,
        journal_path=batch_journal, promotion_id='batch-selftest',
        report_path=batch_report)
    assert rep['leases']['L1']['subcards'] == 1 and rep['leases']['L2']['subcards'] == 1
    # H1386 D3: PER-LEASE delta figures, not the bundle-wide before/after stamped N times.
    for lid in ('L1', 'L2'):
        row = rep['leases'][lid]
        assert row['rows_added'] == row['rows'] and row['rows_replaced'] == 0, row
        assert row['store_delta'] == row['rows'], row
    bytes1 = open(bstore, 'rb').read()
    report_bytes1 = open(batch_report, 'rb').read()
    assert b'y~~keep' in bytes1, 'unrelated store row must survive the batch'
    rep2 = batch_promote(
        batch, bstore, 'ai_translated', SELFTEST_MODEL_VERSION,
        journal_path=batch_journal, promotion_id='batch-selftest',
        report_path=batch_report)
    assert open(bstore, 'rb').read() == bytes1, 'batch rerun must be byte-stable/idempotent'
    assert rep2 == rep, 'journal retry must return the sealed report'
    assert open(batch_report, 'rb').read() == report_bytes1, (
        'journal retry report must be byte-idempotent')
    # PREPARED and report-replace death points are independently recoverable.
    pstore = os.path.join(bd, 'prepared-store.jsonl')
    with open(pstore, 'w', encoding='utf-8') as f:
        f.write(json.dumps(keep_row, ensure_ascii=False) + '\n')
    pbefore = open(pstore, 'rb').read()
    pjournal = os.path.join(bd, 'prepared.journal.json')
    preport = os.path.join(bd, 'prepared.report.json')
    def _die_prepared(point):
        if point == 'prepared':
            raise RuntimeError('synthetic prepared death')
    try:
        batch_promote(
            batch, pstore, 'ai_translated', SELFTEST_MODEL_VERSION,
            journal_path=pjournal, promotion_id='prepared-selftest',
            report_path=preport, fault_hook=_die_prepared)
        raise AssertionError('prepared fault hook did not fire')
    except RuntimeError as exc:
        assert 'prepared death' in str(exc)
    assert open(pstore, 'rb').read() == pbefore
    assert promotion_journal.load(pjournal)['phase'] == 'prepared'
    def _die_report_replace(point):
        if point == 'report_replace':
            raise RuntimeError('synthetic report replace death')
    try:
        batch_promote(
            batch, pstore, 'ai_translated', SELFTEST_MODEL_VERSION,
            journal_path=pjournal, promotion_id='prepared-selftest',
            report_path=preport, fault_hook=_die_report_replace)
        raise AssertionError('report_replace fault hook did not fire')
    except RuntimeError as exc:
        assert 'report replace death' in str(exc)
    assert promotion_journal.load(pjournal)['phase'] == 'store_committed'
    preport_bytes = open(preport, 'rb').read()
    batch_promote(
        batch, pstore, 'ai_translated', SELFTEST_MODEL_VERSION,
        journal_path=pjournal, promotion_id='prepared-selftest',
        report_path=preport)
    assert open(preport, 'rb').read() == preport_bytes
    # Recover the exact death window: store replace succeeded, PREPARED ->
    # STORE_COMMITTED phase write did not. Re-entry adopts only the sealed after hash.
    jstore = os.path.join(bd, 'journal-store.jsonl')
    with open(jstore, 'w', encoding='utf-8') as f:
        f.write(json.dumps(keep_row, ensure_ascii=False) + '\n')
    jpath = os.path.join(bd, 'promotion.journal.json')
    rpath = os.path.join(bd, 'promotion.report.json')
    old_tm_dir = os.environ.get('PWG_RU_TM_DIR')
    os.environ['PWG_RU_TM_DIR'] = bd
    def _die_after_replace(point):
        if point == 'store_replace':
            raise RuntimeError('synthetic death after replace')
    try:
        try:
            batch_promote(
                batch, jstore, 'ai_translated', SELFTEST_MODEL_VERSION,
                journal_path=jpath, promotion_id='selftest-promotion',
                report_path=rpath, fault_hook=_die_after_replace)
            raise AssertionError('after-replace fault hook did not fire')
        except RuntimeError as exc:
            assert 'synthetic death' in str(exc)
        assert promotion_journal.load(jpath)['phase'] == 'prepared'
        assert promotion_journal.reconcile(jpath, adopt_after=False)[
            'action'] == 'adopt_store_commit'
        recovered = batch_promote(
            batch, jstore, 'ai_translated', SELFTEST_MODEL_VERSION,
            journal_path=jpath, promotion_id='selftest-promotion',
            report_path=rpath)
        assert recovered['promotion_id'] == 'selftest-promotion', recovered
        assert promotion_journal.load(jpath)['phase'] == 'store_committed'
        assert os.path.isfile(rpath), 'batch report must be atomic and present after retry'
    finally:
        if old_tm_dir is None:
            os.environ.pop('PWG_RU_TM_DIR', None)
        else:
            os.environ['PWG_RU_TM_DIR'] = old_tm_dir
    # all-or-nothing: a lease whose clean output diverges from its expectation fails the
    # WHOLE bundle with the store byte-identical.
    bad = [dict(batch[0]), dict(batch[1], expected_subcards=['not~~this'])]
    try:
        batch_promote(
            bad, bstore, 'ai_translated', SELFTEST_MODEL_VERSION,
            journal_path=os.path.join(bd, 'bad.journal.json'),
            promotion_id='bad-selftest')
        raise AssertionError('divergent lease expectation did not fail the bundle')
    except PromotionContractError:
        pass
    assert open(bstore, 'rb').read() == bytes1, 'failed bundle must leave the store unchanged'
    # Multi-sense replacement is one atomic subcard replacement: no stale old
    # sense may survive and no new sense may be dropped.
    multi_key = 'multi~~h0_00_pwg00'
    multi_meta = dict(
        meta, root='multi', selected_keys=[multi_key],
        provenance_classes={multi_key: 'real'},
        input_hashes={multi_key: {
            'raw_sha256': '7' * 64, 'portrait_sha256': '8' * 64}})
    multi_card = {
        'key1': multi_key, 'iast': 'multi', 'notes': '', 'records': [{
            'h': 'multi', 'grammar': '', 'senses': [
                {'tag': '1', 'russian': 'новый один', 'german': 'neu eins',
                 'equivalence_type': 'equivalent', 'source_type': 'attested',
                 'stratum': '', 'differentia': ''},
                {'tag': '2', 'russian': 'новый два', 'german': 'neu zwei',
                 'equivalence_type': 'equivalent', 'source_type': 'attested',
                 'stratum': '', 'differentia': ''},
            ],
        }],
    }
    multi_wf = os.path.join(bd, 'wf_output.multi.json')
    with open(multi_wf, 'w', encoding='utf-8') as f:
        json.dump({'meta': multi_meta, 'results': [
            {'key': multi_key, 'card': multi_card}]}, f)
    multi_store = os.path.join(bd, 'multi.store.jsonl')
    with open(multi_store, 'w', encoding='utf-8') as f:
        for tag, ru in (('1', 'старый один'), ('2', 'старый два')):
            f.write(json.dumps({
                'key1': 'multi', 'subcard': multi_key, 'h': 'multi',
                'sense_tag': tag, 'de': 'alt ' + tag, 'ru': ru,
                'provenance': {},
            }, ensure_ascii=False) + '\n')
    batch_promote(
        [{'lease_id': 'LM', 'run_id': 'run-LM', 'attempt_id': 'attempt-LM',
          'glob': multi_wf, 'expected_subcards': [multi_key]}],
        multi_store, 'ai_translated', SELFTEST_MODEL_VERSION,
        journal_path=os.path.join(bd, 'multi.journal.json'),
        promotion_id='multi-selftest')
    with open(multi_store, encoding='utf-8') as f:
        multi_rows = [json.loads(line) for line in f if line.strip()]
    assert len(multi_rows) == 2, multi_rows
    assert [row['ru'] for row in multi_rows] == ['новый один', 'новый два']
    # bundle-fails when the store already holds a strictly better attempt (a freshly
    # audited lease should never lose better-attempt-wins).
    partial_card = dict(entry['card'], partial=True, missing_fragments=['g1:f0'])
    fp1, key1 = lease_files['L1']
    with open(fp1, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [{'key': key1, 'card': partial_card}]}, f)
    try:
        batch_promote(
            batch, bstore, 'ai_translated', SELFTEST_MODEL_VERSION,
            journal_path=os.path.join(bd, 'downgrade.journal.json'),
            promotion_id='downgrade-selftest')
        raise AssertionError('a partial attempt over a complete store row did not fail the bundle')
    except PromotionContractError as exc:
        assert 'better attempt' in str(exc)
    assert open(bstore, 'rb').read() == bytes1, 'downgrade bundle must leave the store unchanged'
    print('batch promotion: 2-lease transaction, idempotent+byte-stable, all-or-nothing OK')

    # H1553 / H1403 A3: defect-key refusal + ready_partial clean-subset (temp store only).
    ddef = tempfile.mkdtemp()
    defect_list = os.path.join(ddef, 'requeue.defect.keys.txt')
    with open(defect_list, 'w', encoding='utf-8') as f:
        f.write('bad~~key\n')
        f.write('p_a~~h5_00_pwg00\n')
    assert load_defect_keys(defect_list) == ['bad~~key', 'p_a~~h5_00_pwg00']
    blocked = refuse_defect_keys(
        ['p_a~~h5_00_pwg00', 'ok~~key'], ['p_a~~h5_00_pwg00', 'other'], force=False)
    assert blocked == ['p_a~~h5_00_pwg00'], blocked
    assert refuse_defect_keys(['p_a~~h5_00_pwg00'], ['p_a~~h5_00_pwg00'], force=True) == []
    assert refuse_defect_keys(['ok~~key'], ['p_a~~h5_00_pwg00'], force=False) == []
    assert refuse_defect_keys(['ok~~key'], [], force=False) == []

    tstore = os.path.join(ddef, 'store.jsonl')
    # seed one row so apply has a merge target
    with open(tstore, 'w', encoding='utf-8') as f:
        f.write(json.dumps({
            'key1': 'keep', 'subcard': 'y~~keep', 'h': 'y', 'sense_tag': '1',
            'de': 'x', 'ru': 'y', 'review_status': 'ai_translated',
            'layer': 'pwg', 'provenance': {},
        }, ensure_ascii=False) + '\n')
    clean_report = {
        'keys': ['p_a~~h5_00_pwg00', 'bad~~key'],
        'requeue': ['bad~~key'],
        'requeue_defect': ['bad~~key'],
        'null_cards': [],
        'requeue_transient': [],
    }
    dry = promote_ready_partial_clean(clean_report, dry_run=True, store=tstore)
    assert dry['status'] == 'dry_run_ok' and dry['clean_keys'] == ['p_a~~h5_00_pwg00'], dry
    assert dry['promoted_keys'] == ['p_a~~h5_00_pwg00']
    # refuse when clean somehow intersects defect
    dirty_report = {
        'keys': ['p_a~~h5_00_pwg00'],
        'requeue': [],
        'requeue_defect': ['p_a~~h5_00_pwg00'],
        'null_cards': [],
    }
    # clean_keys_from_report excludes defect → no_clean_keys
    empty = promote_ready_partial_clean(dirty_report, dry_run=True, store=tstore)
    assert empty['status'] == 'no_clean_keys', empty
    # force path still dry-runs without writing
    force_dry = promote_ready_partial_clean(
        clean_report, dry_run=True, store=tstore, force=True)
    assert force_dry['status'] == 'dry_run_ok'
    before = open(tstore, 'rb').read()
    # apply with a real wf file for the clean key only
    wf_clean = os.path.join(ddef, 'wf_output.clean.json')
    with open(wf_clean, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [
            {'key': 'p_a~~h5_00_pwg00', 'card': entry['card']}]}, f)
    applied = promote_ready_partial_clean(
        clean_report, dry_run=False, store=tstore,
        gen_model_version=SELFTEST_MODEL_VERSION, wf_glob=wf_clean)
    assert applied['status'] == 'applied', applied
    assert 'p_a~~h5_00_pwg00' in applied['promoted_keys']
    after = open(tstore, 'rb').read()
    assert after != before and b'pA' in after or b'p_a' in after or b'\xd0' in after, \
        'applied promote must land rows in the temp store'
    # dry-run must not have been the writer for the earlier check — re-assert fence
    dry2 = promote_ready_partial_clean(clean_report, dry_run=True, store=tstore)
    assert dry2['status'] == 'dry_run_ok'
    print('H1553 defect refusal + ready_partial clean-subset (temp store) OK')
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
    ap.add_argument('--init-store', action='store_true',
                    help='explicitly initialize a missing store (first run only)')
    ap.add_argument('--no-backup', action='store_true')
    ap.add_argument('--force', action='store_true',
                    help='bypass the >50%%-shrink overwrite guard AND the defect-key refusal '
                         '(H1403 A3 / H1553). Only for a deliberate full rebuild or known-good '
                         'override of requeue.defect.keys.txt.')
    ap.add_argument('--merge', action='store_true',
                    help='MERGE into the existing store by SUB-CARD: replace only the sub-cards '
                         'present in THIS run, keep every other row (including a root\'s already-'
                         'translated sub-cards not in this run). Use for a per-root catch-up — the '
                         'default full overwrite WIPES any root whose wf_output file is no longer '
                         'on disk (the gam-RU loss mode).')
    ap.add_argument('--override-reviewed', action='store_true',
                    help='H2146: allow machine replacement of subcards whose store rows a '
                         'human has touched (reviewer set, non-ai_* review_status, or an '
                         'editorial_decision* stamp). Default preserves/refuses them '
                         '(FINDINGS §513); pass this only for a deliberate re-translation '
                         'of reviewed content.')
    ap.add_argument('--allow-raw-default-merge', action='store_true',
                    help='H2089: override the refuse of --merge into the default pwg_ru store '
                         'without --promotion-id. Prefer coordinator journaled --batch-manifest. '
                         'Env twin: PWG_ALLOW_RAW_MERGE_DEFAULT_STORE=1.')
    ap.add_argument('--steal-lock', action='store_true',
                    help='H336/H-1: bypass a live promotion claim on --store unconditionally. Only '
                         'for a claim you are certain is dead (crashed run) — no PID-liveness check '
                         'is possible across clones/machines, so this is the only override.')
    ap.add_argument('--lock-ttl-seconds', type=int, default=None,
                    help='override the promotion claim staleness TTL (default: promote_lock.'
                         'DEFAULT_TTL_SECONDS = 30 min)')
    ap.add_argument('--batch-manifest',
                    help='H1339 Phase 3: promote N leases in ONE store transaction. Path to '
                         'a JSON list of {lease_id, glob, expected_subcards}; implies the '
                         'same per-entry validation as single mode, better-attempt-wins, '
                         'one backup, one atomic replace, all-or-nothing.')
    ap.add_argument('--report', help='write the batch per-lease report JSON here')
    ap.add_argument('--journal',
                    help='recoverable pwg.promotion_journal.v1 path for --batch-manifest; '
                         'PREPARED is fsynced before store replacement')
    ap.add_argument('--promotion-id',
                    help='required stable coordinator promotion id for --journal; '
                         'retries must supply the identical id')
    ap.add_argument('--defect-keys',
                    help='H1553: path to a one-key-per-line defect list (audit '
                         'requeue.defect.keys.txt). When omitted, auto-discovers that file next '
                         'to the wf_output glob or under src/pilot/output/. Incoming keys in the '
                         'list are REFUSED unless --force.')
    ap.add_argument('--ready-partial-report',
                    help='H1553: path to an audit report JSON; promote only clean keys '
                         '(ready_partial clean-subset). Default is dry-run; pass --apply to write '
                         '(still uses --store; wave-1 agents must not target the live store).')
    ap.add_argument('--apply', action='store_true',
                    help='with --ready-partial-report: actually write the clean subset '
                         '(default is dry-run only)')
    args = ap.parse_args()
    if args.batch_manifest:
        if not args.journal or not args.promotion_id:
            sys.exit('REFUSED: --batch-manifest requires --journal and --promotion-id')
        if args.no_backup:
            sys.exit('REFUSED: journaled --batch-manifest requires a backup')
        # H1386 D5: flags the batch transaction does not implement are REFUSED, never
        # silently discarded -- a hand-run `--batch-manifest --dry-run` used to mutate the
        # canonical store (claim / backup / atomic replace / denylist unblock) with no
        # warning, because batch_promote ran before the single-mode dry-run check.
        for flag, name in ((args.dry_run, '--dry-run'), (args.force, '--force'),
                           (args.init_store, '--init-store')):
            if flag:
                sys.exit('REFUSED: %s is not supported with --batch-manifest' % name)
        try:
            batch = json.load(open(args.batch_manifest, encoding='utf-8'))
            report = batch_promote(
                batch, args.store, args.review_status, args.gen_model_version,
                no_backup=args.no_backup, steal_lock=args.steal_lock,
                lock_ttl_seconds=args.lock_ttl_seconds, report_path=args.report,
                journal_path=args.journal, promotion_id=args.promotion_id,
                override_reviewed=args.override_reviewed)
        except (PromotionContractError, UnrestoredPlaceholder,
                promotion_journal.JournalError) as exc:
            sys.exit('REFUSED: %s' % exc)
        except ClaimBusy as e:
            sys.exit(str(e))
        return report

    if args.journal and not args.batch_manifest:
        sys.exit('REFUSED: --journal currently requires --batch-manifest')
    # --promotion-id alone is allowed as the H2089 coordinator-intent token for
    # single-mode --merge into the default store (no journal write in that path).

    if args.ready_partial_report:
        try:
            with open(args.ready_partial_report, encoding='utf-8') as f:
                rp_report = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            sys.exit('REFUSED: cannot load --ready-partial-report: %s' % e)
        result = promote_ready_partial_clean(
            rp_report, dry_run=not args.apply, store=args.store,
            gen_model_version=args.gen_model_version,
            review_status=args.review_status,
            wf_glob=os.path.join(ROOT, args.glob) if args.glob else None,
            force=args.force)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result.get('status') in ('refused_defect', 'error_no_store',
                                    'error_no_model_version', 'error_no_wf',
                                    'error_conflicts', 'error_no_rows'):
            sys.exit(2)
        return result

    if args.merge and not explicit_glob_supplied(sys.argv[1:]):
        sys.exit(
            'refusing --merge with the implicit broad glob %r; pass --glob explicitly '
            '(normally src/pilot/output/wf_output.<window>.json)' % DEFAULT_GLOB)
    # H2089: single-mode --merge into the LIVE default store without a promotion id
    # is a coordinator bypass (silent route around journaled batch_promote). Refuse
    # unless override flag/env is set.
    if args.merge and not args.dry_run:
        _def = os.path.normpath(os.path.abspath(DEFAULT_STORE))
        _tgt = os.path.normpath(os.path.abspath(args.store))
        if _tgt == _def:
            override = (
                args.allow_raw_default_merge
                or os.environ.get('PWG_ALLOW_RAW_MERGE_DEFAULT_STORE') == '1'
            )
            if not args.promotion_id and not override:
                sys.exit(
                    'REFUSED: --merge into default pwg_ru store without --promotion-id '
                    '(H2089 route-bypass). Use coordinator --batch-manifest + --journal, '
                    'or pass --promotion-id, or --allow-raw-default-merge / '
                    'PWG_ALLOW_RAW_MERGE_DEFAULT_STORE=1'
                )
    try:
        validate_store_target(args.store, args.init_store)
    except PromotionContractError as exc:
        sys.exit('REFUSED: %s' % exc)

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

    # H1553 / H1403 A3: refuse keys the latest audit marked as content defect
    # (H255_NO_PWG_W02 promote-then-revert footgun). Fail closed only when a list
    # is discoverable; no list → proceed with a loud skipped_no_list note.
    defect_path = discover_defect_keys_path(args.glob, args.defect_keys)
    defect_keys = []
    if args.defect_keys and not os.path.exists(args.defect_keys):
        sys.exit('REFUSED: --defect-keys path does not exist: %s' % args.defect_keys)
    if defect_path and os.path.exists(defect_path):
        defect_keys = load_defect_keys(defect_path)
        print('defect_guard: loaded %d key(s) from %s' % (len(defect_keys), defect_path))
    else:
        print('defect_guard: skipped_no_list')
    blocked = refuse_defect_keys(list(best.keys()), defect_keys, force=False)
    if blocked and not args.force:
        sys.exit(
            'REFUSED: %d incoming key(s) are on the defect list (H1403 A3 / H1553). '
            'Re-translate or pass --force to override. Keys: %s'
            % (len(blocked), ', '.join(blocked[:20])
               + (' …' if len(blocked) > 20 else '')))
    if blocked and args.force:
        print('defect_guard: --force overrides %d defect key(s): %s'
              % (len(blocked), ', '.join(blocked[:10])
                 + (' …' if len(blocked) > 10 else '')))
    elif defect_keys and not blocked:
        print('defect_guard: no intersection with incoming keys')

    rows, per_root = [], {}
    for subkey, entry in sorted(best.items()):
        try:
            validate_promotion_entry(subkey, entry)
        except PromotionContractError as exc:
            sys.exit('REFUSED: %s' % exc)
        # B20 (H1339): the operator-typed --gen-model-version lands verbatim in permanent
        # store provenance; cross-check it against the manifest's sealed execution model
        # identity so a typo'd/wrong id can never masquerade as the generating model.
        exec_model = ((entry.get('meta') or {}).get('execution') or {}).get('model_identifier')
        if exec_model and exec_model != args.gen_model_version:
            sys.exit('REFUSED: %s: --gen-model-version %r does not match the manifest '
                     'execution.model_identifier %r' % (subkey, args.gen_model_version,
                                                        exec_model))
        n = 0
        for row in rows_for(subkey, entry, args.review_status, args.gen_model_version):
            rows.append(row)
            n += 1
        if n == 0:
            sys.exit('REFUSED: %s passed collection but yielded no promotable Russian rows'
                     % subkey)
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
        sys.exit('REFUSED: duplicate non-null workflow keys: %s'
                 % ', '.join(sorted(set(conflicts))[:20]))
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
            downgraded = []
            protected = []
            if args.merge and os.path.exists(args.store):
                promoted_subs = {r['subcard'] for r in rows}
                touched_roots = {r['key1'] for r in rows}
                existing_rows = []
                with open(args.store, encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        existing_rows.append(json.loads(line))
                rows_to_write, downgraded, protected = merge_store_rows(
                    existing_rows, rows, override_reviewed=args.override_reviewed)
                if downgraded:
                    # B08: better-attempt-wins refused these incoming subcards -- the store
                    # already holds a strictly better attempt (complete vs partial, or
                    # fewer missing fragments). Loud, never silent; existing rows kept.
                    print('\n⚠ better-attempt-wins: store keeps its BETTER existing rows for '
                          '%d subcard(s); incoming (worse) attempt dropped: %s'
                          % (len(downgraded), ', '.join(downgraded[:10])
                             + (' …' if len(downgraded) > 10 else '')))
                if protected:
                    # H2146: human-reviewed subcards are preserved, never silently
                    # machine-replaced (FINDINGS §513). --override-reviewed lands them.
                    print('\n⚠ overlay-preserve: store keeps its HUMAN-REVIEWED rows for '
                          '%d subcard(s); incoming machine attempt dropped (pass '
                          '--override-reviewed for a deliberate re-translation): %s'
                          % (len(protected), ', '.join(protected[:10])
                             + (' …' if len(protected) > 10 else '')))
                blocked_subs_ = set(downgraded) | set(protected)
                landed = len(rows) - sum(1 for r in rows if r['subcard'] in blocked_subs_)
                kept = len(rows_to_write) - landed
                print('\nMERGE: replacing %d sub-card(s) across root(s) %s; keeping %d existing row(s)'
                      % (len(promoted_subs - blocked_subs_), sorted(touched_roots), kept))
            else:
                # H2146 (FINDINGS §513): a full rebuild replaces the store with whatever
                # wf_output is on disk -- if the store holds HUMAN-REVIEWED rows, that
                # wipes the review overlay wholesale. Refuse; --force does NOT cover this
                # (it bypasses the shrink guard, a different hazard) -- only the explicit
                # --override-reviewed does.
                if os.path.exists(args.store) and not args.override_reviewed:
                    overlay_subs = set()
                    try:
                        with open(args.store, encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if not line:
                                    continue
                                row = json.loads(line)
                                if human_touched(row):
                                    overlay_subs.add(row.get('subcard'))
                    except (OSError, json.JSONDecodeError) as exc:
                        sys.exit('REFUSED: cannot verify the store overlay state before a '
                                 'full rebuild (%s) -- fix the store or use --merge' % exc)
                    if overlay_subs:
                        sys.exit(
                            'REFUSED: full (non---merge) rebuild would wipe HUMAN-REVIEWED '
                            'rows for %d subcard(s): %s (FINDINGS §513). Use --merge (which '
                            'preserves them), or --override-reviewed for a deliberate '
                            'rebuild over reviewed content.'
                            % (len(overlay_subs),
                               ', '.join(sorted(overlay_subs)[:10])
                               + (' …' if len(overlay_subs) > 10 else '')))
                rows_to_write = rows

            identities = [(r.get('key1'), r.get('subcard'), r.get('h'),
                           r.get('sense_tag'), r.get('de')) for r in rows_to_write]
            duplicates = [identity for identity, n in collections.Counter(identities).items()
                          if n > 1]
            if duplicates:
                sys.exit('REFUSED: promotion would create %d duplicate sense identity/identities'
                         % len(duplicates))

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
                bak = _backup_path(args.store, args.merge)
                _fsynced_backup(args.store, bak)
                print('\nbacked up prior store -> %s' % os.path.basename(bak))
            # Durable atomic write: fsynced temp plus write-through replace on Windows
            # (rename + directory fsync on POSIX), so a crash/kill cannot leave the
            # canonical store truncated.
            _atomic_write_rows(args.store, rows_to_write)
            print('wrote canonical translated store -> %s (%d rows, review_status=%s)'
                  % (args.store, len(rows_to_write), args.review_status))
            # B12 (H1339): the landed replacements clear their matching TEMPORARY TM
            # denials (input address + frag_prov fshas), so a once-flagged card whose
            # retranslation just passed every gate is TM-reusable again. Fail-open with a
            # loud note: a missed unblock only costs future cache misses -- it must never
            # fail a promotion that already committed.
            try:
                cleared_addr, cleared_frag = clear_denials_for_promotion(
                    best, blocked_subs=sorted(set(downgraded) | set(protected)))
                if cleared_addr or cleared_frag:
                    print('TM denylist: cleared %d card address(es) + %d fragment sha(s) '
                          'superseded by this promotion' % (len(cleared_addr), len(cleared_frag)))
            except Exception as exc:  # noqa: BLE001 -- deliberate fail-open, loudly
                print('⚠ TM denylist clearing skipped (%s) -- denials stay in place; '
                      'a future promotion or manual unblock can clear them' % exc)
            print('NOTE: rows are %s, NOT approved — export_interop keeps them out of the citable'
                  % args.review_status)
            print('      edition until G5 human review flips review_status to approved.')
    except ClaimBusy as e:
        sys.exit(str(e))


if __name__ == '__main__':
    main()
