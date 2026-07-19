#!/usr/bin/env python
r"""Content-addressed translation memory (TM) sidecar for the PWG bulk translation harness.

WHY THIS EXISTS
---------------
`resumeFromRunId` REPLAYS a Workflow verbatim (it re-serves the cached failure, it does
NOT re-roll a stochastic StructuredOutput failure), and a FRESH Workflow run re-translates
the whole card from scratch — discarding every fragment that already succeeded in a prior
run. So neither path reuses a prior run's *good* work (brU's first failure burned ~860k
tokens re-doing 12 of 13 already-good fragments). Card-level `--merge` in
`save_and_audit`/`promote_final_cards` preserves an already-promoted card in the STORE, but
only if the operator scopes `--keys` to the missing ones by hand, and it is keyed on the
sub-card KEY (a rootmap reshape that renames a key defeats it).

This TM closes that gap. It is a **content-addressed** cache: a card is keyed by
`f"{lang}:{input_raw_sha256}"` — the SHA-256 of its exact masked-input source. Both sides
compute the same address:
  * harvest  : from each store row's recorded `provenance.input_raw_sha256`;
  * generate : `gen_opt_harness2.py --tm` computes `sha256_file(<key>.raw.txt)`.
So `gen_opt_harness2.py --tm` pre-resolves any card whose source is byte-identical to one
already translated — ZERO tokens, automatically, WITHOUT hand-scoping `--keys`, and
surviving key renames (the address is the source content, not the key). Two different
sub-cards with byte-identical source (a duplicated sub-entry) reuse one translation
(cross-card reuse).

Version safety is intrinsic: if a card's source changes, its SHA changes, the address
misses, and the card is re-translated — a stale translation can never be reused.

GRANULARITY (two levels)
------------------------
CARD level (`build` / `load_tm` / `frag_address`-less path): one address per sub-card, keyed
on the whole masked source. The coarsest unit whose source string is byte-identical at both
harvest and generation (the raw `.raw.txt`), so content-addressing is exact with no guesswork.

FRAGMENT level (`build_frags` / `load_frag_tm` / `frag_address`, added 2026-07-02): one address
per deterministic `autosplit_requeue.plan()` fragment, so a partially-failed giant flat headword
(kAla/ka/SrI) re-runs only its still-missing fragments and the same meaning shared byte-for-byte
across a root and its derived noun is reused. This does NOT try to align the store's per-sense
`de` to plan() fragments (the discarded approach — headers + citation-batching gave ~3/7 exact);
instead the harness's selfHeal records fragment→senses ground truth (`frag_prov`) at the instant
of a successful heal, and `build_frags` harvests it. See the fragment-TM section below.

USAGE
-----
  python src/pilot/translation_memory.py build        [--lang ru|en] [--store PATH] [--out PATH]
  python src/pilot/translation_memory.py stats        [--lang ru|en] [--tm PATH]
  python src/pilot/translation_memory.py lookup <input_raw_sha256> [--lang ru|en] [--tm PATH]
  python src/pilot/translation_memory.py build-frags  [--lang ru|en] [--glob 'wf_output*.json'] [--out PATH]
  python src/pilot/translation_memory.py frag-stats   [--lang ru|en] [--out PATH]
  python src/pilot/translation_memory.py build-suggestions [--lang ru|en] [--terminology PATH]
  python src/pilot/translation_memory.py export-publication [--lang ru] [--out-dir release/translation_memory]
  python src/pilot/translation_memory.py speed-report [--lang ru] [--keys k1,k2]
  python src/pilot/translation_memory.py validate     [--lang ru|en] [--tm PATH] [--frag-tm PATH] [--suggest-tm PATH]
  python src/pilot/translation_memory.py selftest

The card TM file (default src/pilot/translation_memory.<lang>.json) is DERIVED from the
local-only, gitignored store; the fragment sidecar (translation_memory.frag.<lang>.jsonl) is
harvested from wf_output cards' `frag_prov`. Both are gitignored + regenerable — never a
deliverable. Refresh both after every promotion (card TM) / heal run (fragment TM), or they
go stale (stale = misses, never wrong reuse — you only lose the savings).
"""
import argparse
import datetime
import glob as _glob
import hashlib
import json
import os
import sys
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)

if HERE not in sys.path:
    sys.path.insert(0, HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from window_common import append_jsonl_line  # noqa: E402
from store_path import canonical_store, canonical_sidecar  # noqa: E402

# ONE logical store shared across worktrees (H818 D-E): resolve via canonical_store so a
# git-worktree run's post-promotion TM rebuild targets the MAIN checkout store, exactly like
# promote_final_cards.DEFAULT_STORE. Previously this was a worktree-local path that did not
# exist under a linked worktree, so `promote_ready`'s `translation_memory.py build` (no --store)
# failed "store not found" after a successful promotion, aborting the staged-run.
DEFAULT_STORE = canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl'))
FIELD = {'ru': 'ru', 'en': 'en'}                    # store column holding the translation
TRUST_REVIEWED = 'reviewed_exact'
TRUST_MACHINE = 'machine_exact'
TRUST_SUGGESTION = 'suggestion'
REUSABLE_POLICIES = {'auto_exact'}
BLOCKED_POLICIES = {'blocked', 'defect'}
BAD_GATE_STATUSES = {'blocked', 'defect', 'failed', 'rejected'}
REVIEWED_STATUSES = {'approved', 'human_reviewed'}
MACHINE_STATUSES = {'ai_translated', 'machine_gated', 'machine_exact', None, ''}
TRUST_RANK = {TRUST_REVIEWED: 30, TRUST_MACHINE: 20, 'legacy_promoted': 10,
              TRUST_SUGGESTION: 0}
SUGGEST_SCHEMA = 'pwg.translation_memory.suggest.v1'
CARD_SCHEMA = 'pwg.translation_memory.v1'
FRAG_SCHEMA = 'pwg.translation_memory.frag.v1'
FRAG_SCHEMA_V2 = 'pwg.translation_memory.frag.v2'   # R6: adds a per-sense owners[] array


def _valid_owners(senses, owners):
    """R6: a v2 `owners[]` is a list parallel to `senses`, each element an `[h, grammar]` pair whose
    members are BOTH strings ('' is valid -- the proven-empty homonym head / defaulted grammar -- but
    None is NOT: a null member is exactly the C-02 null owner this schema exists to keep out of a warm
    stitch). Malformed/missing/null-member owners disqualify a row from live v2 reuse; the row stays
    audit-readable (live_only=False) but is never served warm, so no stitch can restore a null owner."""
    if not isinstance(owners, list) or not isinstance(senses, list):
        return False
    if len(owners) != len(senses):
        return False
    for pair in owners:
        if not (isinstance(pair, (list, tuple)) and len(pair) == 2):
            return False
        if not all(isinstance(x, str) for x in pair):   # BOTH members must be str; None fails
            return False
    return True
PUBLICATION_SCHEMA = 'pwg.translation_memory.publication.v1'
SCORE_FIELDS = ('score_de_fragment', 'score_sa_headword', 'score_semantic_tag')
OPTIONAL_SUGGEST_FIELDS = (
    'score_combined', 'score', 'curator_id', 'reviewer_id', 'review_status',
    'source_id', 'source_uri', 'source_hash', 'mw_source_key', 'term_id',
)
SUGGEST_PROFILES = {
    'semantic': {'score_semantic_tag': 0.60, 'score_de_fragment': 0.25, 'score_sa_headword': 0.15},
    'german': {'score_de_fragment': 0.60, 'score_semantic_tag': 0.25, 'score_sa_headword': 0.15},
    'sanskrit': {'score_sa_headword': 0.60, 'score_semantic_tag': 0.25, 'score_de_fragment': 0.15},
    'balanced': {'score_de_fragment': 1 / 3, 'score_sa_headword': 1 / 3, 'score_semantic_tag': 1 / 3},
}
_LOAD_TM_CACHE = {}


class DenylistError(RuntimeError):
    """A TM denylist cannot be trusted."""


# B04 (H1339): the four sidecar resolvers route through store_path.canonical_sidecar --
# ONE logical sidecar set per checkout tree, shared with every linked worktree, exactly
# like the store itself (an explicit `out`/`--out` still wins, as does $PWG_RU_TM_DIR).
# Before this, a fresh-worktree run silently saw NO sidecars: 0 TM hits, full
# re-translation cost, and its post-promotion TM rebuild vanished with the worktree.
def tm_path(lang, out=None):
    return out or canonical_sidecar(os.path.join(HERE, 'translation_memory.%s.json' % lang))


def suggest_tm_path(lang, out=None):
    return out or canonical_sidecar(
        os.path.join(HERE, 'translation_memory.suggest.%s.jsonl' % lang))


def denylist_path(out=None):
    return out or canonical_sidecar(os.path.join(HERE, 'translation_memory.denylist.jsonl'))


def _file_signature(path):
    if not path or not os.path.exists(path):
        return (os.path.abspath(path) if path else None, None, None)
    st = os.stat(path)
    return (os.path.abspath(path), st.st_mtime_ns, st.st_size)


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='seconds').replace('+00:00', 'Z')


def trust_counts(rows):
    return dict(Counter((r or {}).get('trust_level') or 'legacy_promoted'
                        for r in (rows or [])))


def _tm_metadata_from_rows(rows, source_kind='pwg_store'):
    statuses = {(r.get('review_status') or '') for r in rows}
    gate_statuses = {(r.get('gate_status') or '') for r in rows}
    policies = {(r.get('reuse_policy') or '') for r in rows}
    blocked = bool((statuses | gate_statuses) & BAD_GATE_STATUSES or
                   policies & BLOCKED_POLICIES)
    if blocked:
        trust = TRUST_MACHINE
        review_status = sorted([s for s in statuses if s])[-1] if any(statuses) else 'blocked'
        bad_gates = sorted(gate_statuses & BAD_GATE_STATUSES)
        gate_status = bad_gates[0] if bad_gates else 'defect'
        reuse_policy = 'defect'
    elif rows and all((r.get('review_status') or '') in REVIEWED_STATUSES for r in rows):
        trust = TRUST_REVIEWED
        review_status = sorted(statuses & REVIEWED_STATUSES)[0]
        gate_status = 'human_reviewed'
        reuse_policy = 'auto_exact'
    else:
        trust = TRUST_MACHINE
        review_status = sorted([s for s in statuses if s])[-1] if any(statuses) else 'legacy_promoted'
        gate_status = sorted([s for s in gate_statuses if s])[-1] if any(gate_statuses) else 'legacy_promoted'
        reuse_policy = 'auto_exact'
    return {
        'trust_level': trust,
        'gate_status': gate_status,
        'gate_version': rows[0].get('gate_version') or 'legacy',
        'review_status': review_status,
        'reuse_policy': reuse_policy,
        'source_kind': source_kind,
        'supersedes': rows[0].get('supersedes'),
    }


def _entry_time(row):
    for key in ('harvested_at', 'built_at', 'generated_at', 'updated_at'):
        if row.get(key):
            return str(row.get(key))
    return ''


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def reusable(row):
    if not row:
        return False
    if row.get('reuse_policy') in BLOCKED_POLICIES:
        return False
    if row.get('gate_status') in BAD_GATE_STATUSES:
        return False
    if row.get('trust_level') == TRUST_SUGGESTION:
        return False
    return bool(row.get('card') or row.get('senses'))


def best_reusable(rows):
    candidates = [r for r in rows if reusable(r)]
    if not candidates:
        return None
    superseded = {s for r in candidates for s in _as_list(r.get('supersedes')) if s}
    candidates = [r for r in candidates if not r.get('id') or r.get('id') not in superseded]
    if not candidates:
        return None
    return max(candidates, key=lambda r: (
        TRUST_RANK.get(r.get('trust_level') or 'legacy_promoted', 10),
        _entry_time(r),
    ))


def load_denylist(path=None):
    p = denylist_path(path)
    out = {'addresses': set(), 'frags': set()}
    if not os.path.exists(p):
        return out
    with open(p, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                # H336/H-3 / P0.1: a torn denylist cannot be trusted. Continuing here can
                # silently re-enable TM reuse of gate-rejected cards/fragments, so make the
                # caller fix the append/merge before any TM lookup proceeds.
                raise DenylistError(
                    'torn/undecodable denylist line %d in %s (%s): %r' %
                    (lineno, p, e, line[:200]))
            kind = row.get('kind')
            value = row.get('address') or row.get('fsha') or row.get('value')
            if kind in ('card', 'address') and value:
                out['addresses'].add(value)
            elif kind in ('fragment', 'frag', 'fsha') and value:
                out['frags'].add(value)
    return out


def _iter_store(store_path):
    with open(store_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def reconstruct_cards(store_path, lang):
    """Group store sense-rows back into per-sub-card card objects, addressed by source SHA.

    Returns { address: entry } where address == f"{lang}:{input_raw_sha256}" and entry is
    { 'card': <card obj shaped like a wf_output card>, 'src_key', 'raw_sha256', 'model',
      'model_version', 'root', 'n_senses' }.

    A sub-card is included only if EVERY one of its senses (a) has a non-empty translation in
    the requested `lang` and (b) shares one recorded `input_raw_sha256` — a card whose rows
    disagree on the source hash is ambiguous (mid-reshape) and is skipped, not guessed.
    Rows without a recorded `input_raw_sha256` cannot be content-addressed and are skipped.
    """
    field = FIELD[lang]
    by_sub = defaultdict(list)
    for row in _iter_store(store_path):
        sub = row.get('subcard')
        if sub:
            by_sub[sub].append(row)

    entries, skipped = {}, Counter()
    for sub, rows in by_sub.items():
        if any((r.get('provenance') or {}).get('partial_card') or
               (r.get('provenance') or {}).get('missing_fragments') or
               (r.get('provenance') or {}).get('missing_groups')
               for r in rows):
            skipped['partial-card'] += 1
            continue
        shas = {(r.get('provenance') or {}).get('input_raw_sha256') for r in rows}
        shas.discard(None)
        if not shas:
            skipped['no-raw-sha'] += 1
            continue
        if len(shas) > 1:
            skipped['sha-disagreement'] += 1
            continue
        raw_sha = next(iter(shas))
        # A card with ANY blank sense is NOT content-addressed into the exact TM.
        # H321 (code review 2026-07-04 item #3a) proposed caching such cards
        # "per-sense" to avoid re-translating a giant card that has one blank
        # xref sense — but measured 0/2313 sub-cards in the live store carry a
        # blank non-partial sense (zero incidence), and the change is unsafe:
        # tm_card_sane refuses any card with a blank sense at SERVE, so caching
        # it would either churn (cached-then-refused) or force serving an
        # incomplete card as complete. Kept as-is deliberately; consistent with
        # the serve-time guard and the audit completeness gates.
        if any(not (r.get(field) or '').strip() for r in rows):
            skipped['incomplete-%s' % lang] += 1
            continue
        # B03 (H1339, P0): a sense_tag the schema would refuse (None/empty) cannot be
        # reconstructed into a servable card -- skip the sub-card rather than fabricate a
        # tag; the serve-time guard refuses such a card anyway, so caching it only churns.
        if any(not isinstance(r.get('sense_tag'), str) or not r.get('sense_tag')
               for r in rows):
            skipped['invalid-sense-tag'] += 1
            continue
        # Rebuild records grouped by homonym head `h`, senses in stored order.
        recs = defaultdict(list)
        rec_order = []
        rec_grammar = {}
        for r in rows:
            h = r.get('h')
            if h not in recs:
                rec_order.append(h)
                # first stored grammar of the h-group owns the record ('' when null)
                rec_grammar[h] = r.get('grammar') or ''
            sense = {
                'tag': r.get('sense_tag'),
                'german': r.get('de') or '',
                field if lang == 'en' else 'russian': r.get(field),
            }
            # B03: optional sense fields are validated WHEN PRESENT by the final-card
            # schema (a present-but-None differentia/equivalence_type is a refusal), so a
            # null store value must OMIT the key, never emit it as None.
            for opt in ('equivalence_type', 'source_type', 'stratum', 'differentia'):
                value = r.get(opt)
                if value is not None:
                    sense[opt] = value
            recs[h].append(sense)
        card = {
            'key1': sub,
            'iast': rows[0].get('iast') or sub,
            # B03: notes (card) and h/grammar (record) are schema-REQUIRED -- a TM card
            # missing them was refused by the save gate, poisoning the whole window on the
            # first TM hit. h is coerced to str exactly as the C-07 degenerate stub does.
            'notes': '',
            'records': [{'h': (h or ''), 'grammar': rec_grammar[h], 'senses': recs[h]}
                        for h in rec_order],
        }
        prov0 = rows[0].get('provenance') or {}
        address = '%s:%s' % (lang, raw_sha)
        meta = _tm_metadata_from_rows(rows)
        entries[address] = {
            'id': address,
            'card': card,
            'src_key': sub,
            'raw_sha256': raw_sha,
            'model': prov0.get('model'),
            'model_version': prov0.get('model_version'),
            'root': prov0.get('root'),
            'n_senses': len(rows),
            **meta,
        }
    return entries, skipped


def build(store_path, lang, out=None):
    entries, skipped = reconstruct_cards(store_path, lang)
    payload = {
        'schema': CARD_SCHEMA,
        'lang': lang,
        'address': 'sha256(input raw) == provenance.input_raw_sha256',
        'built_at': _utc_now(),
        'store': os.path.basename(store_path),
        'count': len(entries),
        'trust_counts': trust_counts(entries.values()),
        'entries': entries,
    }
    path = tm_path(lang, out)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)
    return path, len(entries), skipped


def _normalize_card_entry(address, row):
    row = dict(row or {})
    row.setdefault('id', address)
    row.setdefault('trust_level', TRUST_MACHINE)
    row.setdefault('gate_status', 'legacy_promoted')
    row.setdefault('gate_version', 'legacy')
    row.setdefault('review_status', 'legacy_promoted')
    row.setdefault('reuse_policy', 'auto_exact')
    row.setdefault('source_kind', 'pwg_store')
    row.setdefault('supersedes', None)
    return row


def load_tm(lang, tm=None, denylist=None):
    """Return the best reusable {address: entry} map for a built TM, or {} if none exists."""
    path = tm_path(lang, tm)
    if not os.path.exists(path):
        return {}
    deny_path = denylist_path(denylist)
    cache_key = (lang, _file_signature(path), _file_signature(deny_path))
    cached = _LOAD_TM_CACHE.get(cache_key)
    if cached is not None:
        return dict(cached)
    deny = load_denylist(denylist)
    with open(path, encoding='utf-8') as f:
        rows = (json.load(f) or {}).get('entries') or {}
    by_addr = defaultdict(list)
    for address, row in rows.items():
        if address in deny['addresses']:
            continue
        by_addr[address].append(_normalize_card_entry(address, row))
    out = {}
    for address, candidates in by_addr.items():
        best = best_reusable(candidates)
        if best:
            out[address] = best
    _LOAD_TM_CACHE.clear()
    _LOAD_TM_CACHE[cache_key] = dict(out)
    return out


def lookup(lang, raw_sha256, tm=None):
    return load_tm(lang, tm).get('%s:%s' % (lang, raw_sha256))


# ------------------------------------------------------------------- fragment-level TM
# SUB-CARD reuse. The card-level TM above reuses a whole sub-card only when its ENTIRE
# masked source is byte-identical to a cached one. The fragment TM reuses ONE fragment
# inside a still-failing giant card (kAla/ka/SrI: one card, 40+ heal groups) and the same
# meaning across a root and its derived noun — the higher-value increment.
#
# ADDRESS. A fragment is keyed by the SHA-256 of the EXACT deterministic `plan()` chunk
# text that was translated — INCLUDING the header that `autosplit_requeue.plan()` attaches
# to fragment 0 (a verb's conjugation-table header is genuine translated source, not
# scaffolding). Both sides compute the SAME chunk: `split_plan(read_text(raw))` is
# deterministic, so harvest and generation see byte-identical fragment text -> identical
# address. (The earlier "3/7 exact" mismatch was an artifact of comparing to the store's
# per-sense `de`, which carries no header; we never do that here — we capture fragment ->
# senses at the moment of a successful heal, so there is no alignment guesswork and nothing
# to strip.) Version safety is intrinsic, exactly as for the card TM: a changed source ->
# a different chunk -> a different address -> a miss -> re-translation; a stale fragment can
# never be reused. LS_BUDGET is part of the chunking, so a changed AUTOSPLIT_LS_BUDGET
# re-chunks -> new addresses -> misses (correct: different chunking is a different fragment).
#
# GROUND TRUTH. The sidecar is harvested from wf_output cards' `frag_prov` channel, which
# `gen_opt_harness2`'s selfHeal emits per FRESHLY-resolved fragment ({fsha, restored
# senses}) — recorded at the instant of success, after the per-fragment {Tn}-multiset
# fidelity guard passed. The sidecar is DERIVED (gitignored + regenerable), never a
# deliverable, and append-only+deduped by fsha (first-seen wins).
FRAG_SEP = '\x00frag\x00'


def frag_address(lang, frag_source):
    """The content address of one plan() fragment: sha256(lang + NUL 'frag' NUL + source).

    The single source of truth for the address formula — imported by gen_opt_harness2 so
    the SHA embedded in the harness (and echoed into frag_prov at harvest) is computed the
    exact same way it is recomputed at injection time."""
    return hashlib.sha256((lang + FRAG_SEP + frag_source).encode('utf-8')).hexdigest()


def frag_tm_path(lang, out=None):
    # B04 (H1339): canonical-sidecar resolution, same as tm_path/suggest_tm_path/denylist_path.
    return out or canonical_sidecar(os.path.join(HERE, 'translation_memory.frag.%s.jsonl' % lang))


# frag_prov senses are CARD-shaped (harvested from wf_output cards), so the
# translation lives under 'russian'/'english' — NOT the store column names in FIELD.
_FRAG_TRANSLATION_FIELD = {'ru': 'russian', 'en': 'english'}


def frag_senses_sane(senses, lang):
    """A frag_prov `senses[]` is usable only if it is a non-empty list of sense
    objects each carrying a non-empty translation in `lang`.

    The fragment sidecar is content-addressed on the fragment SOURCE and was
    previously harvested first-seen-wins with NO fidelity check (code review
    2026-07-04): a hand-edited or corrupt `wf_output*.json` — blanked or
    malformed senses — permanently poisoned fragment reuse, and a later good
    harvest of the same fsha could never override it. This gate is applied at
    BOTH harvest (never cache garbage; let a good row override a cached bad one)
    and serve (never hand a corrupt historical row to the harness)."""
    if not isinstance(senses, list) or not senses:
        return False
    field = _FRAG_TRANSLATION_FIELD.get(lang, 'russian')
    for s in senses:
        if not isinstance(s, dict) or not (s.get(field) or '').strip():
            return False
    return True


def _normalize_frag_row(row):
    row = dict(row or {})
    row.setdefault('id', row.get('fsha'))
    row.setdefault('trust_level', TRUST_MACHINE)
    row.setdefault('gate_status', 'legacy_promoted')
    row.setdefault('gate_version', 'legacy')
    row.setdefault('review_status', 'legacy_promoted')
    row.setdefault('reuse_policy', 'auto_exact')
    row.setdefault('source_kind', 'frag_prov')
    row.setdefault('supersedes', None)
    return row


def load_frag_tm(lang, path=None, denylist=None, live_only=True):
    """Return { fsha: {'senses': [...], 'owners': [...], ...} } for the fragment sidecar, or {} if
    none exists. Best reusable row wins (reviewed > machine > legacy; blocked ignored). R6: by
    default (`live_only`) only frag-TM v2 rows with a valid per-sense `owners[]` are served; a v1
    (ownerless) row is readable for historical audit (`live_only=False`) but never live-reusable, so
    a warm stitch can never regenerate a null-`h` row. A valid v2 row supersedes an ownerless v1 row
    with the same fsha (it is the only served candidate)."""
    p = frag_tm_path(lang, path)
    out = {}
    if not os.path.exists(p):
        return out
    deny = load_denylist(denylist)
    by_fsha = defaultdict(list)
    with open(p, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            fsha = row.get('fsha')
            # Serve-time fidelity filter: a corrupt/blanked historical row is
            # never handed to the harness, regardless of when it was harvested.
            if not (fsha and fsha not in deny['frags']
                    and frag_senses_sane(row.get('senses'), lang)):
                continue
            if live_only and not (row.get('schema') == FRAG_SCHEMA_V2
                                  and _valid_owners(row.get('senses'), row.get('owners'))):
                # R6: a v1 (ownerless) or malformed-owners row is readable for historical audit
                # (live_only=False) but NEVER live-reusable -- a warm stitch must not regenerate a
                # null-`h` row. A valid v2 row for the same fsha supersedes it here by being the only
                # served candidate.
                continue
            by_fsha[fsha].append(_normalize_frag_row(row))
    for fsha, candidates in by_fsha.items():
        best = best_reusable(candidates)
        if best:
            out[fsha] = best
    return out


def build_frags(glob_pattern, lang, out=None):
    """Harvest per-fragment ground truth from wf_output cards' `frag_prov` channel into the
    append-only fragment sidecar. Idempotent: a fragment already present (by fsha) is never
    duplicated. Returns (path, added, total)."""
    path = frag_tm_path(lang, out)
    # seen[fsha] = the highest schema version already cached for that fsha (2 = frag-TM v2 with valid
    # owners, 1 = v1/ownerless). A harvest is skipped only when the cache already holds a version >=
    # the new one, so a v2 harvest SUPERSEDES a cached v1 (R6) while a v1 re-harvest of a cached v1
    # is still deduped. Corrupt/blank rows are absent from `seen`, so a later good harvest overrides.
    seen = {}
    if os.path.exists(path):
        with open(path, encoding='utf-8') as _f:
            for _line in _f:
                _line = _line.strip()
                if not _line:
                    continue
                try:
                    _row = json.loads(_line)
                except json.JSONDecodeError:
                    continue
                _fsha = _row.get('fsha')
                if not _fsha or not frag_senses_sane(_row.get('senses'), lang) or not reusable(_row):
                    continue      # defect/blocked/suggestion rows are not a real cache hit (overridable)
                _ver = 2 if (_row.get('schema') == FRAG_SCHEMA_V2
                             and _valid_owners(_row.get('senses'), _row.get('owners'))) else 1
                seen[_fsha] = max(seen.get(_fsha, 0), _ver)
    files = sorted(_glob.glob(os.path.join(REPO, glob_pattern)))
    new_rows, added, refused = [], 0, 0
    for fp in files:
        try:
            with open(fp, encoding='utf-8') as f:
                wrapper = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        res = wrapper.get('result') if isinstance(wrapper, dict) else None
        if isinstance(res, str):
            try:
                res = json.loads(res)
            except json.JSONDecodeError:
                print('warning: skipping malformed nested result JSON in %s' %
                      os.path.basename(fp), file=sys.stderr)
                continue
        if res is None:
            res = wrapper
        if not isinstance(res, dict):
            print('warning: skipping non-object workflow result in %s' %
                  os.path.basename(fp), file=sys.stderr)
            continue
        meta = res.get('meta') or {}
        if (meta.get('lang') or 'ru') != lang:
            continue
        root = meta.get('root')
        input_hashes = meta.get('input_hashes') or {}
        for r in res.get('results') or []:
            card = (r or {}).get('card')
            if not card:
                continue
            for fpv in card.get('frag_prov') or []:
                fsha, senses = fpv.get('fsha'), fpv.get('senses')
                owners = fpv.get('owners')       # R6: per-sense [h, grammar]; absent for a v1 emit
                if not fsha or not senses:
                    continue
                is_v2 = _valid_owners(senses, owners)   # R6: a valid owners[] promotes the row to v2
                if not frag_senses_sane(senses, lang):
                    # Never cache a corrupt/blanked fragment (poison guard).
                    refused += 1
                    print('warning: refusing corrupt frag_prov %s (senses fail %s fidelity) in %s'
                          % (fsha[:12], lang, os.path.basename(fp)), file=sys.stderr)
                    continue
                if seen.get(fsha, 0) >= (2 if is_v2 else 1):
                    # Already cached at a version >= this harvest: idempotent skip. A cached v1 does
                    # NOT block a v2 harvest (2 > 1 -> supersede, R6); a cached CORRUPT row is absent
                    # from `seen`, so a good row still overrides it.
                    continue
                src_key = r.get('key')
                raw_sha = ((input_hashes.get(src_key) or {}).get('raw_sha256')
                           if src_key else None)
                seen[fsha] = 2 if is_v2 else 1
                added += 1
                new_rows.append({
                    'schema': FRAG_SCHEMA_V2 if is_v2 else FRAG_SCHEMA, 'lang': lang, 'fsha': fsha,
                    'src_key': src_key, 'root': root, 'raw_sha256': raw_sha,
                    'n_senses': len(senses), 'senses': senses,
                    'owners': owners if is_v2 else None,   # R6: v2 carries per-sense [h, grammar]
                    'wf_file': os.path.basename(fp), 'source_wf_file': os.path.basename(fp),
                    'fragment_address_formula': "sha256(lang + '\\x00frag\\x00' + fragment_source)",
                    'splitter_version': 'autosplit_requeue.plan.v1',
                    'trust_level': TRUST_MACHINE, 'gate_status': 'machine_gated',
                    'gate_version': 'frag_prov_v2' if is_v2 else 'frag_prov_v1',
                    'review_status': 'ai_translated',
                    'reuse_policy': 'auto_exact', 'source_kind': 'frag_prov',
                    'supersedes': None, 'harvested_at': _utc_now(),
                })
    for row in new_rows:
        append_jsonl_line(path, row)
    return path, added, len(seen)


# --------------------------------------------------------------------------- suggestions
def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _score_value(row, key, default=None):
    v = row.get(key, default)
    if v is None or v == '':
        return None
    if isinstance(v, str):
        try:
            v = float(v)
        except ValueError:
            return None
    return v if _is_number(v) else None


def suggestion_profile_score(row, profile='semantic'):
    if profile not in SUGGEST_PROFILES:
        raise ValueError('unknown suggestion profile %r (%s)' %
                         (profile, '|'.join(sorted(SUGGEST_PROFILES))))
    weights = SUGGEST_PROFILES[profile]
    score = 0.0
    seen = False
    for key, weight in weights.items():
        value = _score_value(row, key)
        if value is None:
            continue
        score += value * weight
        seen = True
    if not seen:
        score = _score_value(row, 'score_combined', _score_value(row, 'score', 0.0)) or 0.0
    return round(score, 6)


def rank_suggestions(rows, profile='semantic', limit=None):
    ranked = []
    for idx, row in enumerate(rows or []):
        r = dict(row)
        r['rank_profile'] = profile
        r['rank_score'] = suggestion_profile_score(r, profile)
        ranked.append((r['rank_score'], _score_value(r, 'score_combined', 0.0) or 0.0,
                       str(r.get('source_kind') or ''), str(r.get('key') or r.get('root') or ''),
                       -idx, r))
    out = [r for *_ignore, r in sorted(ranked, reverse=True)]
    return out[:limit] if limit else out


def _copy_score_fields(src, dst):
    for key in SCORE_FIELDS + OPTIONAL_SUGGEST_FIELDS:
        if key in src and src.get(key) not in (None, ''):
            dst[key] = src[key]
    if 'score_combined' not in dst:
        combined = _score_value(src, 'score')
        if combined is not None:
            dst['score_combined'] = combined
    if 'score' not in dst and 'score_combined' in dst:
        dst['score'] = dst['score_combined']


def validate_suggestion_row(row, lang=None):
    if not isinstance(row, dict):
        return False, 'row is not an object'
    if row.get('schema') != SUGGEST_SCHEMA:
        return False, 'bad schema'
    if lang is not None and row.get('lang') != lang:
        return False, 'wrong lang'
    if row.get('trust_level') != TRUST_SUGGESTION:
        return False, 'trust_level must be suggestion'
    if row.get('reuse_policy') != 'suggest_only':
        return False, 'reuse_policy must be suggest_only'
    if not (row.get('key') or row.get('root') or row.get('address')):
        return False, 'missing key/root/address'
    if not isinstance(row.get('text'), str) or not row.get('text').strip():
        return False, 'missing text'
    if row.get('lang') == 'ru' and row.get('source_kind') == 'mw_seed':
        return False, 'raw MW English seed is forbidden for RU'
    if row.get('lang') == 'ru' and row.get('source_kind') == 'curated_sa_ru_terminology':
        if not (row.get('provenance_note') or row.get('source_id') or row.get('source_uri')):
            return False, 'curated RU terminology needs provenance'
    numeric = SCORE_FIELDS + ('score_combined', 'score')
    seen_score = False
    for key in numeric:
        if key not in row:
            continue
        value = _score_value(row, key)
        if value is None or not 0 <= value <= 1:
            return False, '%s must be a number 0..1' % key
        seen_score = True
    if not seen_score:
        return False, 'missing evidence score'
    return True, ''


def validate_card_entry(address, row, lang=None):
    if not isinstance(row, dict):
        return False, 'entry is not an object'
    if not isinstance(address, str) or ':' not in address:
        return False, 'bad address'
    if lang and not address.startswith(lang + ':'):
        return False, 'wrong address lang'
    if not isinstance(row.get('card'), dict):
        return False, 'missing card'
    if row.get('trust_level') == TRUST_SUGGESTION:
        return False, 'suggestion cannot be exact TM'
    if row.get('reuse_policy') not in REUSABLE_POLICIES | BLOCKED_POLICIES:
        return False, 'bad reuse_policy'
    if row.get('gate_status') in BAD_GATE_STATUSES and row.get('reuse_policy') != 'defect':
        return False, 'bad gate must use defect policy'
    return True, ''


def validate_frag_entry(row, lang=None):
    if not isinstance(row, dict):
        return False, 'row is not an object'
    if row.get('schema') not in (FRAG_SCHEMA, FRAG_SCHEMA_V2):
        return False, 'bad schema'
    if row.get('schema') == FRAG_SCHEMA_V2 and not _valid_owners(row.get('senses'), row.get('owners')):
        return False, 'v2 row with malformed owners'
    if lang and row.get('lang') != lang:
        return False, 'wrong lang'
    if not row.get('fsha'):
        return False, 'missing fsha'
    if not isinstance(row.get('senses'), list) or not row.get('senses'):
        return False, 'missing senses'
    if row.get('trust_level') == TRUST_SUGGESTION:
        return False, 'fragment TM cannot be suggestion'
    return True, ''


def load_suggestions(lang, path=None, return_stats=False):
    p = suggest_tm_path(lang, path)
    out = defaultdict(list)
    stats = Counter()
    if not os.path.exists(p):
        return ({}, stats) if return_stats else {}
    with open(p, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                stats['bad-json'] += 1
                continue
            ok, why = validate_suggestion_row(row, lang=lang)
            if not ok:
                stats[why] += 1
                continue
            key = row.get('key') or row.get('root') or row.get('address')
            if key:
                out[key].append(row)
                stats['ok'] += 1
    return (dict(out), stats) if return_stats else dict(out)


def load_ranked_suggestions(lang, path=None, profile='semantic', limit=5,
                            return_stats=False):
    rows, stats = load_suggestions(lang, path, return_stats=True)
    ranked = {key: rank_suggestions(vals, profile=profile, limit=limit)
              for key, vals in rows.items()}
    return (ranked, stats) if return_stats else ranked


def _terminology_rows(path, lang):
    """Read curated terminology as JSON object/list or JSONL rows.

    Minimal accepted shapes:
      {"gam": "идти"} / {"gam": {"text": "идти", "score_combined": 0.9, ...}}
      {"key": "gam", "text": "идти", ...} per JSONL line or list item.
    """
    if not path:
        return []
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    rows = []
    text = open(path, encoding='utf-8').read().strip()
    if not text:
        return []
    if text[0] in '[{':
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, dict):
            if (data.get('key') or data.get('root') or data.get('slp1')) and \
                    (data.get('text') or data.get('ru') or data.get('term')):
                rows.append(dict(data))
            else:
                for k, v in data.items():
                    if isinstance(v, dict):
                        row = dict(v)
                        row.setdefault('key', row.get('root') or k)
                    else:
                        row = {'key': k, 'text': v}
                    rows.append(row)
        elif isinstance(data, list):
            rows.extend([dict(v) for v in data if isinstance(v, dict)])
        else:
            for line in text.splitlines():
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    out = []
    for row in rows:
        key = row.get('key') or row.get('root') or row.get('slp1')
        text = row.get('text') or row.get('ru') or row.get('term')
        if not key or not text:
            continue
        built = {
            'schema': SUGGEST_SCHEMA,
            'lang': lang, 'key': key, 'root': row.get('root') or key,
            'trust_level': TRUST_SUGGESTION, 'reuse_policy': 'suggest_only',
            'source_kind': 'curated_sa_ru_terminology',
            'provenance_note': row.get('provenance_note') or row.get('source') or 'curated_terminology',
            'text': text,
            'built_at': _utc_now(),
        }
        _copy_score_fields(row, built)
        if not any(k in built for k in SCORE_FIELDS) and 'score_combined' not in built:
            built['score_sa_headword'] = 1.0
            built['score_combined'] = 1.0
            built['score'] = 1.0
        out.append(built)
    return out


def build_suggestions(lang, mw_tm=None, terminology=None, out=None):
    """Build a suggestion-only sidecar. V1 seeds EN from mw_en_tm.json; RU emits an empty,
    schema-valid file unless a curated Sanskrit->Russian terminology feed is provided."""
    path = suggest_tm_path(lang, out)
    rows = []
    if mw_tm and lang != 'en':
        raise ValueError('MW English suggestions are allowed only for --lang en; '
                         'for RU use --terminology with curated Sanskrit-to-Russian terms')
    if mw_tm and os.path.exists(mw_tm):
        data = json.load(open(mw_tm, encoding='utf-8'))
        for root, text in sorted(data.items()):
            if not text:
                continue
            rows.append({
                'schema': SUGGEST_SCHEMA,
                'lang': lang, 'key': root, 'root': root, 'score_sa_headword': 1.0,
                'score_combined': 1.0, 'score': 1.0,
                'trust_level': TRUST_SUGGESTION, 'reuse_policy': 'suggest_only',
                'source_kind': 'mw_seed', 'provenance_note': 'seeded_from_mw',
                'text': text,
                'built_at': _utc_now(),
            })
    if terminology:
        rows.extend(_terminology_rows(terminology, lang))
    with open(path, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    return path, len(rows)


# --------------------------------------------------------------------------- publication
def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text):
    return _sha256_bytes((text or '').encode('utf-8'))


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _jsonl_rows(path):
    if not path or not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _row_provenance(row):
    prov = dict(row.get('provenance') or {})
    for key in ('model', 'model_version', 'root', 'source_kind', 'source_wf_file',
                'wf_file', 'splitter_version', 'fragment_address_formula',
                'built_at', 'harvested_at', 'gate_version'):
        if row.get(key) not in (None, '') and key not in prov:
            prov[key] = row.get(key)
    return prov


def _publication_card_record(address, row):
    row = _normalize_card_entry(address, row)
    raw_sha = row.get('raw_sha256') or address.split(':', 1)[-1]
    record = {
        'schema': PUBLICATION_SCHEMA,
        'tm_record_id': 'exact-card:%s' % address,
        'record_type': 'exact_card',
        'lang': address.split(':', 1)[0],
        'trust_level': row.get('trust_level'),
        'reuse_policy': row.get('reuse_policy'),
        'review_status': row.get('review_status'),
        'gate_status': row.get('gate_status'),
        'gate_version': row.get('gate_version'),
        'source_kind': row.get('source_kind'),
        'source_hashes': {'input_raw_sha256': raw_sha},
        'provenance': _row_provenance(row),
        'evidence': [{
            'kind': 'content_addressed_card',
            'address': address,
            'src_key': row.get('src_key'),
            'n_senses': row.get('n_senses', 0),
        }],
        'payload': {'card': row.get('card')},
        'supersedes': row.get('supersedes'),
    }
    return record


def _publication_fragment_record(row):
    row = _normalize_frag_row(row)
    fsha = row.get('fsha')
    record = {
        'schema': PUBLICATION_SCHEMA,
        'tm_record_id': 'exact-fragment:%s:%s' % (row.get('lang'), fsha),
        'record_type': 'exact_fragment',
        'lang': row.get('lang'),
        'trust_level': row.get('trust_level'),
        'reuse_policy': row.get('reuse_policy'),
        'review_status': row.get('review_status'),
        'gate_status': row.get('gate_status'),
        'gate_version': row.get('gate_version'),
        'source_kind': row.get('source_kind'),
        'source_hashes': {
            'fragment_sha256': fsha,
            'input_raw_sha256': row.get('raw_sha256'),
        },
        'provenance': _row_provenance(row),
        'evidence': [{
            'kind': 'content_addressed_fragment',
            'fsha': fsha,
            'src_key': row.get('src_key'),
            'n_senses': len(row.get('senses') or []),
            'splitter_version': row.get('splitter_version'),
        }],
        'payload': {'senses': row.get('senses')},
        'supersedes': row.get('supersedes'),
    }
    return record


def _publication_suggestion_record(row):
    key = row.get('key') or row.get('root') or row.get('address')
    text_hash = _sha256_text(row.get('text') or '')
    source_hash = row.get('source_hash') or text_hash
    record = {
        'schema': PUBLICATION_SCHEMA,
        'tm_record_id': 'suggestion:%s:%s:%s' % (row.get('lang'), key, source_hash[:16]),
        'record_type': 'suggestion',
        'lang': row.get('lang'),
        'trust_level': TRUST_SUGGESTION,
        'reuse_policy': 'suggest_only',
        'review_status': row.get('review_status') or 'advisory',
        'gate_status': row.get('gate_status') or 'suggestion_only',
        'gate_version': row.get('gate_version') or 'suggestion_v1',
        'source_kind': row.get('source_kind'),
        'source_hashes': {
            'suggestion_text_sha256': text_hash,
            'source_hash': row.get('source_hash'),
        },
        'provenance': _row_provenance(row),
        'evidence': [{
            'kind': 'fuzzy_suggestion',
            'key': key,
            'term_id': row.get('term_id'),
            'source_id': row.get('source_id'),
            'source_uri': row.get('source_uri'),
            'score_de_fragment': _score_value(row, 'score_de_fragment'),
            'score_sa_headword': _score_value(row, 'score_sa_headword'),
            'score_semantic_tag': _score_value(row, 'score_semantic_tag'),
            'score_combined': _score_value(row, 'score_combined',
                                           _score_value(row, 'score')),
        }],
        'payload': {'text': row.get('text'), 'key': key, 'root': row.get('root')},
        'supersedes': row.get('supersedes'),
    }
    return record


def validate_publication_record(row, lang=None):
    required = ('schema', 'tm_record_id', 'record_type', 'lang', 'trust_level',
                'reuse_policy', 'review_status', 'gate_status', 'source_hashes',
                'provenance', 'evidence')
    for key in required:
        if key not in row:
            return False, 'missing %s' % key
    if row.get('schema') != PUBLICATION_SCHEMA:
        return False, 'bad schema'
    if lang and row.get('lang') != lang:
        return False, 'wrong lang'
    if row.get('record_type') not in ('exact_card', 'exact_fragment', 'suggestion'):
        return False, 'bad record_type'
    if not isinstance(row.get('source_hashes'), dict):
        return False, 'source_hashes not object'
    if not isinstance(row.get('provenance'), dict):
        return False, 'provenance not object'
    if not isinstance(row.get('evidence'), list) or not row.get('evidence'):
        return False, 'missing evidence'
    return True, ''


def _write_json(path, obj):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def _write_jsonl(path, rows):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def export_publication(lang, out_dir, tm=None, frag_tm=None, suggest_tm=None,
                       store=None):
    os.makedirs(out_dir, exist_ok=True)
    built_at = _utc_now()
    records, source_files = [], {}

    card_path = tm_path(lang, tm)
    if os.path.exists(card_path):
        payload = json.load(open(card_path, encoding='utf-8'))
        source_files['card_tm'] = {'path': os.path.relpath(card_path, REPO),
                                   'sha256': _sha256_file(card_path)}
        for address, row in sorted((payload.get('entries') or {}).items()):
            records.append(_publication_card_record(address, row))

    frag_path = frag_tm_path(lang, frag_tm)
    if os.path.exists(frag_path):
        source_files['fragment_tm'] = {'path': os.path.relpath(frag_path, REPO),
                                       'sha256': _sha256_file(frag_path)}
        for row in _jsonl_rows(frag_path):
            if (row.get('lang') or lang) == lang:
                records.append(_publication_fragment_record(row))

    suggest_path = suggest_tm_path(lang, suggest_tm)
    suggestions, suggest_stats = load_suggestions(lang, suggest_path, return_stats=True)
    if os.path.exists(suggest_path):
        source_files['suggestion_tm'] = {'path': os.path.relpath(suggest_path, REPO),
                                         'sha256': _sha256_file(suggest_path),
                                         'loader_stats': dict(suggest_stats)}
    for key in sorted(suggestions):
        for row in suggestions[key]:
            records.append(_publication_suggestion_record(row))

    store_path = store or DEFAULT_STORE
    if store_path and os.path.exists(store_path):
        source_files['store'] = {'path': os.path.relpath(store_path, REPO),
                                 'sha256': _sha256_file(store_path)}

    out_jsonl = os.path.join(out_dir, 'translation_memory.%s.publication.jsonl' % lang)
    _write_jsonl(out_jsonl, records)
    counts = Counter(r.get('record_type') for r in records)
    trust = Counter(r.get('trust_level') for r in records)
    bad = Counter()
    for row in records:
        ok, why = validate_publication_record(row, lang=lang)
        bad['ok' if ok else why] += 1
    manifest = {
        'schema': 'pwg.translation_memory.publication_manifest.v1',
        'lang': lang,
        'built_at': built_at,
        'artifact': os.path.basename(out_jsonl),
        'artifact_sha256': _sha256_file(out_jsonl),
        'record_count': len(records),
        'record_counts': dict(counts),
        'trust_counts': dict(trust),
        'validation': dict(bad),
        'source_files': source_files,
    }
    manifest_path = os.path.join(out_dir, 'manifest.%s.json' % lang)
    _write_json(manifest_path, manifest)
    datasheet_path = os.path.join(out_dir, 'DATASHEET.%s.md' % lang)
    with open(datasheet_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# PWG Translation Memory Publication Datasheet (%s)\n\n' % lang)
        f.write('_Generated: %s_\n\n' % built_at)
        f.write('This tracked artifact is the publication-grade layer over the local, gitignored TM caches.\n\n')
        f.write('- Records: %d\n' % len(records))
        f.write('- Record counts: `%s`\n' % json.dumps(dict(counts), ensure_ascii=False, sort_keys=True))
        f.write('- Trust counts: `%s`\n' % json.dumps(dict(trust), ensure_ascii=False, sort_keys=True))
        f.write('- Artifact SHA-256: `%s`\n\n' % manifest['artifact_sha256'])
        f.write('Fuzzy suggestions are advisory evidence only; exact-card and exact-fragment rows carry reuse policy and gate status.\n')
    return out_jsonl, manifest_path, datasheet_path, manifest


def export_terminology(lang, out_dir, suggest_tm=None):
    os.makedirs(out_dir, exist_ok=True)
    built_at = _utc_now()
    suggest_path = suggest_tm_path(lang, suggest_tm)
    suggestions = load_suggestions(lang, suggest_path)
    terms = []
    seen = set()
    for key in sorted(suggestions):
        for row in suggestions[key]:
            if row.get('source_kind') != 'curated_sa_ru_terminology':
                continue
            term_id = row.get('term_id') or 'sa-ru:%s:%s' % (
                key, (row.get('source_hash') or _sha256_text(row.get('text') or ''))[:16])
            if term_id in seen:
                continue
            seen.add(term_id)
            terms.append({
                'term_id': term_id,
                'lang': lang,
                'slp1_key': key,
                'root': row.get('root') or key,
                'ru': row.get('text'),
                'source_kind': row.get('source_kind'),
                'source_id': row.get('source_id'),
                'source_uri': row.get('source_uri'),
                'source_hash': row.get('source_hash') or _sha256_text(row.get('text') or ''),
                'curator_id': row.get('curator_id'),
                'reviewer_id': row.get('reviewer_id'),
                'provenance_note': row.get('provenance_note'),
                'scores': {k: _score_value(row, k) for k in SCORE_FIELDS
                           if _score_value(row, k) is not None},
            })
    terms_path = os.path.join(out_dir, 'sa_ru_terminology.%s.jsonl' % lang)
    _write_jsonl(terms_path, terms)
    manifest = {
        'schema': 'pwg.sa_ru_terminology.manifest.v1',
        'lang': lang,
        'built_at': built_at,
        'artifact': os.path.basename(terms_path),
        'artifact_sha256': _sha256_file(terms_path),
        'term_count': len(terms),
        'source_suggestion_tm': (os.path.relpath(suggest_path, REPO)
                                 if os.path.exists(suggest_path) else None),
        'doi_status': 'planned_separate_dataset',
    }
    _write_json(os.path.join(out_dir, 'manifest.%s.json' % lang), manifest)
    _write_json(os.path.join(out_dir, 'datapackage.%s.json' % lang), {
        'profile': 'data-package',
        'name': 'pwg-sa-ru-terminology',
        'title': 'Curated Sanskrit-to-Russian Terminology for PWG Translation Memory',
        'licenses': [{'name': 'CC-BY-SA-4.0'}],
        'resources': [{
            'name': 'sa_ru_terminology',
            'path': os.path.basename(terms_path),
            'format': 'jsonl',
            'mediatype': 'application/x-ndjson',
        }],
    })
    with open(os.path.join(out_dir, 'DATASHEET.%s.md' % lang), 'w',
              encoding='utf-8', newline='\n') as f:
        f.write('# Curated Sanskrit-to-Russian Terminology Datasheet (%s)\n\n' % lang)
        f.write('_Generated: %s_\n\n' % built_at)
        f.write('Separate DOI-bound dataset track for curated Sanskrit-to-Russian terminology used by PWG TM suggestions.\n\n')
        f.write('- Terms: %d\n' % len(terms))
        f.write('- DOI status: planned separate dataset; registration happens after release review.\n')
    return terms_path, manifest


def speed_report(lang, suggest_tm=None, keys=None, out=None):
    suggest_path = suggest_tm_path(lang, suggest_tm)
    suggestions = load_suggestions(lang, suggest_path)
    selected = set(k for k in (keys or []) if k)
    if selected:
        suggestions = {k: v for k, v in suggestions.items() if k in selected}
    profiles = ['none'] + sorted(SUGGEST_PROFILES)
    report = {
        'schema': 'pwg.translation_memory.fuzzy_speed_report.v1',
        'lang': lang,
        'built_at': _utc_now(),
        'suggestion_tm': os.path.relpath(suggest_path, REPO) if os.path.exists(suggest_path) else None,
        'keys': sorted(selected) if selected else 'all',
        'profiles': {},
        'note': 'Static speed proxy: suggestion prompt coverage/bytes. Runtime wall-clock and tokens come from workflow summaries.',
    }
    for profile in profiles:
        if profile == 'none':
            rows_by_key = {}
        else:
            rows_by_key = {k: rank_suggestions(v, profile=profile, limit=5)
                           for k, v in suggestions.items()}
        rows = [r for vals in rows_by_key.values() for r in vals]
        report['profiles'][profile] = {
            'suggestion_cards': len(rows_by_key),
            'suggestion_rows': len(rows),
            'suggestion_text_chars': sum(len(r.get('text') or '') for r in rows),
            'estimated_agent_call_delta': 0,
            'null_count': None,
            'partial_count': None,
            'wall_clock_seconds': None,
            'token_count': None,
        }
    if out:
        _write_json(out, report)
    return report


# --------------------------------------------------------------------------- validation
def validate_tm_file(lang, path=None, kind='card'):
    """Validate a TM sidecar without importing third-party JSON Schema tooling.

    Returns (ok_count, skipped Counter). This is intentionally stricter than the
    runtime loaders for malformed rows, but it still treats blocked/defect rows
    as valid publication records: invalid for reuse does not mean invalid data.
    """
    stats = Counter()
    if kind == 'card':
        p = tm_path(lang, path)
        if not os.path.exists(p):
            raise FileNotFoundError(p)
        payload = json.load(open(p, encoding='utf-8'))
        if payload.get('schema') != CARD_SCHEMA:
            raise ValueError('bad card TM schema: %r' % payload.get('schema'))
        if payload.get('lang') != lang:
            raise ValueError('bad card TM lang: %r' % payload.get('lang'))
        for address, row in (payload.get('entries') or {}).items():
            ok, why = validate_card_entry(address, _normalize_card_entry(address, row), lang=lang)
            stats['ok' if ok else why] += 1
        return stats['ok'], stats
    if kind == 'fragment':
        p = frag_tm_path(lang, path)
        if not os.path.exists(p):
            raise FileNotFoundError(p)
        with open(p, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    stats['bad-json'] += 1
                    continue
                ok, why = validate_frag_entry(_normalize_frag_row(row), lang=lang)
                stats['ok' if ok else why] += 1
        return stats['ok'], stats
    if kind == 'suggestion':
        _rows, stats = load_suggestions(lang, path, return_stats=True)
        return stats['ok'], stats
    if kind == 'publication':
        p = path
        if not p or not os.path.exists(p):
            raise FileNotFoundError(p)
        with open(p, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    stats['bad-json'] += 1
                    continue
                ok, why = validate_publication_record(row, lang=lang)
                stats['ok' if ok else why] += 1
        return stats['ok'], stats
    raise ValueError('unknown TM kind: %s' % kind)


def validation_ok(stats):
    return not any(k != 'ok' and v for k, v in stats.items())


# --------------------------------------------------------------------------- selftest
def selftest():
    import tempfile
    # Two sub-cards; the second row-set disagrees on the source sha (must be skipped),
    # the third is missing a translation (must be skipped), the fourth has no sha (skipped),
    # and the fifth is a partial selfheal card (usable as output evidence, but not exact TM).
    rows = [
        {'subcard': 'x~~h0_1', 'key1': 'x', 'iast': 'xa', 'h': 'xa', 'sense_tag': '1',
         'ru': 'один', 'de': 'eins', 'equivalence_type': 'equivalent', 'source_type': 'attested',
         'stratum': '', 'differentia': '',
         'provenance': {'input_raw_sha256': 'AAA', 'model': 'sonnet', 'model_version': 'claude-sonnet-5', 'root': 'x'}},
        {'subcard': 'x~~h0_1', 'key1': 'x', 'iast': 'xa', 'h': 'xa', 'sense_tag': '2',
         'ru': 'два', 'de': 'zwei', 'equivalence_type': 'equivalent', 'source_type': 'attested',
         'stratum': '', 'differentia': '',
         'provenance': {'input_raw_sha256': 'AAA', 'model': 'sonnet', 'model_version': 'claude-sonnet-5', 'root': 'x'}},
        {'subcard': 'y~~h0_1', 'key1': 'y', 'iast': 'ya', 'h': 'ya', 'sense_tag': '1',
         'ru': 'три', 'de': 'drei', 'provenance': {'input_raw_sha256': 'BBB'}},
        {'subcard': 'y~~h0_1', 'key1': 'y', 'iast': 'ya', 'h': 'ya', 'sense_tag': '2',
         'ru': 'четыре', 'de': 'vier', 'provenance': {'input_raw_sha256': 'CCC'}},   # sha disagreement
        {'subcard': 'z~~h0_1', 'key1': 'z', 'iast': 'za', 'h': 'za', 'sense_tag': '1',
         'ru': '', 'de': 'fuenf', 'provenance': {'input_raw_sha256': 'DDD'}},         # missing ru
        {'subcard': 'w~~h0_1', 'key1': 'w', 'iast': 'wa', 'h': 'wa', 'sense_tag': '1',
         'ru': 'шесть', 'de': 'sechs', 'provenance': {}},                             # no sha
        {'subcard': 'p~~h0_1', 'key1': 'p', 'iast': 'pa', 'h': 'pa', 'sense_tag': '1',
         'ru': 'семь', 'de': 'sieben',
         'provenance': {'input_raw_sha256': 'EEE', 'partial_card': True,
                        'missing_fragments': ['g1:f2']}},                              # partial
    ]
    fd, store = tempfile.mkstemp(suffix='.jsonl'); os.close(fd)
    fd, out = tempfile.mkstemp(suffix='.json'); os.close(fd)
    try:
        with open(store, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        entries, skipped = reconstruct_cards(store, 'ru')
        assert set(entries) == {'ru:AAA'}, entries
        e = entries['ru:AAA']
        assert e['n_senses'] == 2, e
        assert e['card']['key1'] == 'x~~h0_1', e['card']
        senses = e['card']['records'][0]['senses']
        assert [s['tag'] for s in senses] == ['1', '2'], senses
        assert senses[0]['russian'] == 'один' and senses[0]['german'] == 'eins', senses
        assert skipped['sha-disagreement'] == 1, skipped
        assert skipped['incomplete-ru'] == 1, skipped
        assert skipped['no-raw-sha'] == 1, skipped
        assert skipped['partial-card'] == 1, skipped
        # build + load + lookup round-trip
        path, n, _ = build(store, 'ru', out=out)
        assert n == 1, n
        assert lookup('ru', 'AAA', tm=out)['src_key'] == 'x~~h0_1'
        assert lookup('ru', 'ZZZ', tm=out) is None
        assert e['trust_level'] == TRUST_MACHINE and e['gate_status'] == 'legacy_promoted', e
        _frag_selftest()
        _trust_selftest()
        _suggest_selftest()
        _validation_selftest()
        _publication_selftest()
        # H818 D-E: DEFAULT_STORE resolves through store_path.canonical_store (same as
        # promote_final_cards), so a git-worktree run's post-promotion `translation_memory.py
        # build` (no --store) targets the MAIN checkout store instead of a vanishing worktree-local
        # path. Prove: (a) DEFAULT_STORE == canonical_store(base); (b) explicit --store still wins;
        # (c) both RU and EN build codepaths work from an explicit store.
        os.environ.pop('PWG_RU_STORE', None)
        assert DEFAULT_STORE == canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl')), DEFAULT_STORE
        fd2, bstore = tempfile.mkstemp(suffix='.jsonl'); os.close(fd2)
        fd3, ruout = tempfile.mkstemp(suffix='.json'); os.close(fd3)
        fd4, enout = tempfile.mkstemp(suffix='.json'); os.close(fd4)
        try:
            with open(bstore, 'w', encoding='utf-8') as f:
                f.write(json.dumps(
                    {'subcard': 'b~~h0_1', 'key1': 'b', 'iast': 'ba', 'h': 'ba', 'sense_tag': '1',
                     'ru': 'вода', 'en': 'water', 'de': 'Wasser', 'equivalence_type': 'equivalent',
                     'source_type': 'attested', 'stratum': '', 'differentia': '',
                     'provenance': {'input_raw_sha256': 'FFF', 'model': 'sonnet',
                                    'model_version': 'claude-sonnet-5', 'root': 'b'}},
                    ensure_ascii=False) + '\n')
            _, nru, _ = build(bstore, 'ru', out=ruout)   # explicit --store (bstore) wins
            _, nen, _ = build(bstore, 'en', out=enout)   # existing EN codepath unaffected
            assert nru == 1 and nen == 1, (nru, nen)
            assert lookup('ru', 'FFF', tm=ruout)['src_key'] == 'b~~h0_1'
            assert lookup('en', 'FFF', tm=enout)['src_key'] == 'b~~h0_1'
        finally:
            for p in (bstore, ruout, enout):
                try:
                    os.unlink(p)
                except OSError:
                    pass
        print('  D-E: DEFAULT_STORE via canonical_store; explicit --store wins; RU+EN build OK')
        print('translation_memory selftest OK')
    finally:
        for p in (store, out):
            try:
                os.remove(p)
            except OSError:
                pass


def _frag_selftest():
    import tempfile
    # 1) Address is deterministic, lang-separated, and header-sensitive (no stripping).
    src = '=== header ===\n1) foo <ls>ṚV.</ls>'
    assert frag_address('ru', src) == frag_address('ru', src), 'address not deterministic'
    assert frag_address('ru', src) != frag_address('en', src), 'lang must separate the address'
    assert frag_address('ru', src) != frag_address('ru', src.split('\n', 1)[1]), \
        'header is part of the fragment source — the address must change if it is stripped'
    # 2) build_frags harvests frag_prov from wf_output, dedups by fsha, is idempotent.
    d = tempfile.mkdtemp()
    fsha = frag_address('ru', src)
    senses = [{'tag': '1', 'german': 'foo <ls>ṚV.</ls>', 'russian': 'фу', 'source_type': 'attested'}]
    wf = {'meta': {'lang': 'ru', 'root': 'zz'}, 'results': [
        {'key': 'zz~~h0_00_pwg00', 'card': {'key1': 'zz', 'records': [{'senses': senses}],
                                            'frag_prov': [{'fsha': fsha, 'senses': senses,
                                                           'owners': [['zz', '']]}]}},
        {'key': 'zz~~h0_01', 'card': None},                       # null card: no frag_prov
    ]}
    en_wf = {'meta': {'lang': 'en', 'root': 'zz'}, 'results': [
        {'key': 'zz~~h9', 'card': {'frag_prov': [{'fsha': 'EN', 'senses': senses}]}}]}
    old_repo = globals()['REPO']
    try:
        globals()['REPO'] = d                                    # build_frags globs under REPO
        with open(os.path.join(d, 'wf_output.sc.zz.json'), 'w', encoding='utf-8') as f:
            json.dump(wf, f, ensure_ascii=False)
        with open(os.path.join(d, 'wf_output.en.zz.json'), 'w', encoding='utf-8') as f:
            json.dump(en_wf, f, ensure_ascii=False)
        with open(os.path.join(d, 'wf_output.bad.zz.json'), 'w', encoding='utf-8') as f:
            json.dump({'result': '{"broken"'}, f, ensure_ascii=False)
        sidecar = os.path.join(d, 'frag.ru.jsonl')
        with open(sidecar, 'w', encoding='utf-8') as f:
            f.write(json.dumps({'schema': FRAG_SCHEMA_V2, 'lang': 'ru', 'owners': [['zz', '']],
                                'fsha': fsha, 'senses': [{'tag': 'old', 'russian': 'старое'}],
                                'trust_level': TRUST_MACHINE, 'gate_status': 'legacy_promoted',
                                'harvested_at': '2026-01-01T00:00:00Z'}, ensure_ascii=False) + '\n')
            f.write(json.dumps({'schema': FRAG_SCHEMA_V2, 'lang': 'ru', 'owners': [['zz', '']],
                                'fsha': fsha, 'senses': [{'tag': 'new', 'russian': 'новое'}],
                                'trust_level': TRUST_REVIEWED, 'gate_status': 'human_reviewed',
                                'harvested_at': '2026-01-02T00:00:00Z'}, ensure_ascii=False) + '\n')
            f.write(json.dumps({'schema': 'pwg.translation_memory.frag.v1', 'lang': 'ru',
                                'fsha': 'blocked', 'senses': senses,
                                'trust_level': TRUST_MACHINE, 'gate_status': 'defect'},
                               ensure_ascii=False) + '\n')
        _p, added, total = build_frags('wf_output*.json', 'ru', out=sidecar)
        assert added == 0 and total == 1, (added, total)          # existing fsha deduped
        cache = load_frag_tm('ru', sidecar)
        assert set(cache) == {fsha}, cache
        assert cache[fsha]['senses'][0]['russian'] == 'новое', cache
        # idempotent re-harvest adds nothing
        _p, added2, total2 = build_frags('wf_output*.json', 'ru', out=sidecar)
        assert added2 == 0 and total2 == 1, (added2, total2)
    finally:
        globals()['REPO'] = old_repo
        import shutil
        shutil.rmtree(d, ignore_errors=True)


def _trust_selftest():
    good_old = {'id': 'old', 'trust_level': TRUST_MACHINE, 'gate_status': 'legacy_promoted',
                'reuse_policy': 'auto_exact', 'card': {'records': [1]}, 'built_at': '2026-01-01T00:00:00Z'}
    good_new = {'id': 'new', 'trust_level': TRUST_MACHINE, 'gate_status': 'machine_gated',
                'reuse_policy': 'auto_exact', 'card': {'records': [2]}, 'built_at': '2026-01-02T00:00:00Z'}
    reviewed = {'id': 'rev', 'trust_level': TRUST_REVIEWED, 'gate_status': 'human_reviewed',
                'reuse_policy': 'auto_exact', 'card': {'records': [3]}, 'built_at': '2026-01-01T00:00:00Z'}
    blocked = {'id': 'bad', 'trust_level': TRUST_REVIEWED, 'gate_status': 'defect',
               'reuse_policy': 'auto_exact', 'card': {'records': [4]}}
    assert best_reusable([good_old, good_new])['id'] == 'new'
    assert best_reusable([good_new, reviewed])['id'] == 'rev'
    assert best_reusable([blocked]) is None
    superseded = dict(good_new, id='newer', supersedes='old')
    assert best_reusable([good_old, superseded])['id'] == 'newer', \
        'string supersedes must be treated as one id, not iterated character-by-character'
    mixed_rows = [
        {'review_status': 'approved', 'gate_status': 'human_reviewed'},
        {'review_status': 'rejected', 'gate_status': 'defect'},
    ]
    mixed = _tm_metadata_from_rows(mixed_rows)
    assert mixed['reuse_policy'] == 'defect' and mixed['gate_status'] == 'defect', mixed
    clean_machine = _tm_metadata_from_rows([
        {'review_status': 'ai_translated', 'gate_status': 'machine_gated'},
        {'review_status': 'ai_translated', 'gate_status': 'machine_gated'},
    ])
    assert clean_machine['trust_level'] == TRUST_MACHINE
    assert clean_machine['reuse_policy'] == 'auto_exact', clean_machine
    all_reviewed = _tm_metadata_from_rows([
        {'review_status': 'approved', 'gate_status': 'machine_gated'},
        {'review_status': 'human_reviewed', 'gate_status': 'machine_gated'},
    ])
    assert all_reviewed['trust_level'] == TRUST_REVIEWED, all_reviewed


def _suggest_selftest():
    import tempfile
    d = tempfile.mkdtemp()
    try:
        mw = os.path.join(d, 'mw.json')
        out = os.path.join(d, 'suggest.jsonl')
        with open(mw, 'w', encoding='utf-8') as f:
            json.dump({'gam': 'go, move'}, f)
        path, n = build_suggestions('en', mw_tm=mw, out=out)
        assert path == out and n == 1, (path, n)
        got = load_suggestions('en', out)
        assert got['gam'][0]['trust_level'] == TRUST_SUGGESTION, got
        assert got['gam'][0]['reuse_policy'] == 'suggest_only', got
        try:
            build_suggestions('ru', mw_tm=mw, out=out)
            raise AssertionError('RU must not accept direct MW English suggestions')
        except ValueError:
            pass
        term = os.path.join(d, 'terminology.jsonl')
        with open(term, 'w', encoding='utf-8') as f:
            f.write(json.dumps({'key': 'gam', 'text': 'идти', 'source': 'curated',
                                'score_de_fragment': 0.2, 'score_sa_headword': 1.0,
                                'score_semantic_tag': 0.8, 'score_combined': 0.91,
                                'curator_id': 'fixture-curator'},
                               ensure_ascii=False) + '\n')
        _path, n2 = build_suggestions('ru', terminology=term, out=out)
        assert n2 == 1, n2
        got_ru = load_suggestions('ru', out)
        assert got_ru['gam'][0]['source_kind'] == 'curated_sa_ru_terminology', got_ru
        assert got_ru['gam'][0]['score_de_fragment'] == 0.2, got_ru
        assert got_ru['gam'][0]['score_sa_headword'] == 1.0, got_ru
        assert got_ru['gam'][0]['score_semantic_tag'] == 0.8, got_ru
        with open(out, 'a', encoding='utf-8') as f:
            f.write(json.dumps({'schema': SUGGEST_SCHEMA, 'lang': 'ru', 'key': 'bad',
                                'trust_level': TRUST_SUGGESTION,
                                'reuse_policy': 'suggest_only',
                                'source_kind': 'mw_seed',
                                'text': 'raw MW English must not enter RU',
                                'score_combined': 1.0}, ensure_ascii=False) + '\n')
            f.write(json.dumps({'schema': SUGGEST_SCHEMA, 'lang': 'ru', 'key': 'bad2',
                                'trust_level': TRUST_SUGGESTION,
                                'reuse_policy': 'suggest_only',
                                'source_kind': 'curated_sa_ru_terminology',
                                'text': 'missing provenance',
                                'score_combined': 1.0}, ensure_ascii=False) + '\n')
        filtered, stats = load_suggestions('ru', out, return_stats=True)
        assert 'bad' not in filtered and 'bad2' not in filtered, filtered
        assert stats['raw MW English seed is forbidden for RU'] == 1, stats
        assert stats['curated RU terminology needs provenance'] == 1, stats
        ranked_sem = rank_suggestions([
            {'key': 'x', 'text': 'sem', 'score_de_fragment': 0.1, 'score_sa_headword': 0.1,
             'score_semantic_tag': 1.0, 'score_combined': 0.1},
            {'key': 'x', 'text': 'de', 'score_de_fragment': 1.0, 'score_sa_headword': 0.1,
             'score_semantic_tag': 0.1, 'score_combined': 0.1},
            {'key': 'x', 'text': 'sa', 'score_de_fragment': 0.1, 'score_sa_headword': 1.0,
             'score_semantic_tag': 0.1, 'score_combined': 0.1},
        ], profile='semantic')
        ranked_de = rank_suggestions([dict(r) for r in ranked_sem], profile='german')
        ranked_sa = rank_suggestions([dict(r) for r in ranked_sem], profile='sanskrit')
        assert ranked_sem[0]['text'] == 'sem', ranked_sem
        assert ranked_de[0]['text'] == 'de', ranked_de
        assert ranked_sa[0]['text'] == 'sa', ranked_sa
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)


def _validation_selftest():
    import tempfile
    d = tempfile.mkdtemp()
    try:
        card = os.path.join(d, 'tm.ru.json')
        with open(card, 'w', encoding='utf-8') as f:
            json.dump({'schema': CARD_SCHEMA, 'lang': 'ru', 'entries': {
                'ru:AAA': {'id': 'ru:AAA', 'card': {'records': [{'senses': [{'russian': 'x'}]}]},
                           'trust_level': TRUST_MACHINE, 'gate_status': 'machine_gated',
                           'reuse_policy': 'auto_exact'},
                'ru:BAD': {'id': 'ru:BAD', 'card': {'records': [{'senses': [{'russian': 'x'}]}]},
                           'trust_level': TRUST_MACHINE, 'gate_status': 'defect',
                           'reuse_policy': 'defect'},
            }}, f, ensure_ascii=False)
        ok, stats = validate_tm_file('ru', card, kind='card')
        assert ok == 2 and validation_ok(stats), stats
        frag = os.path.join(d, 'frag.ru.jsonl')
        with open(frag, 'w', encoding='utf-8') as f:
            f.write(json.dumps({'schema': FRAG_SCHEMA, 'lang': 'ru', 'fsha': 'FFF',
                                'senses': [{'tag': '1', 'russian': 'x'}],
                                'trust_level': TRUST_MACHINE,
                                'reuse_policy': 'auto_exact'}, ensure_ascii=False) + '\n')
            f.write('{"broken"\n')
        ok, stats = validate_tm_file('ru', frag, kind='fragment')
        assert ok == 1 and stats['bad-json'] == 1, stats
        suggest = os.path.join(d, 'suggest.ru.jsonl')
        with open(suggest, 'w', encoding='utf-8') as f:
            f.write(json.dumps({'schema': SUGGEST_SCHEMA, 'lang': 'ru', 'key': 'gam',
                                'trust_level': TRUST_SUGGESTION,
                                'reuse_policy': 'suggest_only',
                                'source_kind': 'curated_sa_ru_terminology',
                                'provenance_note': 'fixture',
                                'text': 'идти',
                                'score_de_fragment': 0.1,
                                'score_sa_headword': 1.0,
                                'score_semantic_tag': 0.9}, ensure_ascii=False) + '\n')
            f.write(json.dumps({'schema': SUGGEST_SCHEMA, 'lang': 'ru', 'key': 'bad',
                                'trust_level': TRUST_SUGGESTION,
                                'reuse_policy': 'suggest_only',
                                'source_kind': 'curated_sa_ru_terminology',
                                'provenance_note': 'fixture',
                                'text': 'bad',
                                'score_combined': 2.0}, ensure_ascii=False) + '\n')
        ok, stats = validate_tm_file('ru', suggest, kind='suggestion')
        assert ok == 1 and stats['score_combined must be a number 0..1'] == 1, stats
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)


def _publication_selftest():
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        card = os.path.join(d, 'tm.ru.json')
        frag = os.path.join(d, 'frag.ru.jsonl')
        suggest = os.path.join(d, 'suggest.ru.jsonl')
        outdir = os.path.join(d, 'release_tm')
        with open(card, 'w', encoding='utf-8') as f:
            json.dump({'schema': CARD_SCHEMA, 'lang': 'ru', 'entries': {
                'ru:AAA': {'id': 'ru:AAA', 'card': {'records': [{'senses': [{'russian': 'x'}]}]},
                           'raw_sha256': 'AAA', 'trust_level': TRUST_REVIEWED,
                           'gate_status': 'human_reviewed', 'review_status': 'approved',
                           'reuse_policy': 'auto_exact'},
                'ru:BAD': {'id': 'ru:BAD', 'card': {'records': [{'senses': [{'russian': 'bad'}]}]},
                           'raw_sha256': 'BAD', 'trust_level': TRUST_MACHINE,
                           'gate_status': 'defect', 'review_status': 'rejected',
                           'reuse_policy': 'defect'},
            }}, f, ensure_ascii=False)
        with open(frag, 'w', encoding='utf-8') as f:
            f.write(json.dumps({'schema': FRAG_SCHEMA, 'lang': 'ru', 'fsha': 'FFF',
                                'senses': [{'tag': '1', 'russian': 'x'}],
                                'trust_level': TRUST_MACHINE, 'gate_status': 'machine_gated',
                                'review_status': 'ai_translated',
                                'reuse_policy': 'auto_exact'}, ensure_ascii=False) + '\n')
        with open(suggest, 'w', encoding='utf-8') as f:
            f.write(json.dumps({'schema': SUGGEST_SCHEMA, 'lang': 'ru', 'key': 'gam',
                                'trust_level': TRUST_SUGGESTION,
                                'reuse_policy': 'suggest_only',
                                'source_kind': 'curated_sa_ru_terminology',
                                'provenance_note': 'fixture',
                                'text': 'идти',
                                'score_de_fragment': 0.1,
                                'score_sa_headword': 1.0,
                                'score_semantic_tag': 0.9}, ensure_ascii=False) + '\n')
        pub, manifest_path, datasheet_path, manifest = export_publication(
            'ru', outdir, tm=card, frag_tm=frag, suggest_tm=suggest, store=None)
        assert os.path.exists(pub) and os.path.exists(manifest_path) and os.path.exists(datasheet_path)
        assert manifest['record_counts']['exact_card'] == 2, manifest
        assert manifest['record_counts']['exact_fragment'] == 1, manifest
        assert manifest['record_counts']['suggestion'] == 1, manifest
        ok, stats = validate_tm_file('ru', pub, kind='publication')
        assert ok == 4 and validation_ok(stats), stats
        reusable_cache = load_tm('ru', card)
        assert set(reusable_cache) == {'ru:AAA'}, reusable_cache
        terms_path, term_manifest = export_terminology('ru', os.path.join(d, 'terms'),
                                                       suggest_tm=suggest)
        assert os.path.exists(terms_path) and term_manifest['term_count'] == 1, term_manifest
        rep = speed_report('ru', suggest_tm=suggest, keys=['gam'])
        assert rep['profiles']['none']['suggestion_rows'] == 0, rep
        assert rep['profiles']['semantic']['suggestion_rows'] == 1, rep
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build'); b.add_argument('--lang', default='ru'); b.add_argument('--store', default=DEFAULT_STORE); b.add_argument('--out', default=None)
    s = sub.add_parser('stats'); s.add_argument('--lang', default='ru'); s.add_argument('--tm', default=None)
    lk = sub.add_parser('lookup'); lk.add_argument('sha'); lk.add_argument('--lang', default='ru'); lk.add_argument('--tm', default=None)
    bf = sub.add_parser('build-frags'); bf.add_argument('--lang', default='ru'); bf.add_argument('--glob', default='wf_output*.json'); bf.add_argument('--out', default=None)
    fs = sub.add_parser('frag-stats'); fs.add_argument('--lang', default='ru'); fs.add_argument('--out', default=None)
    bs = sub.add_parser('build-suggestions'); bs.add_argument('--lang', default='ru'); bs.add_argument('--mw-tm', default=None); bs.add_argument('--terminology', default=None); bs.add_argument('--out', default=None)
    ep = sub.add_parser('export-publication'); ep.add_argument('--lang', default='ru'); ep.add_argument('--out-dir', default=os.path.join(REPO, 'release', 'translation_memory')); ep.add_argument('--tm', default=None); ep.add_argument('--frag-tm', default=None); ep.add_argument('--suggest-tm', default=None); ep.add_argument('--store', default=DEFAULT_STORE)
    et = sub.add_parser('export-terminology'); et.add_argument('--lang', default='ru'); et.add_argument('--out-dir', default=os.path.join(REPO, 'release', 'sa_ru_terminology')); et.add_argument('--suggest-tm', default=None)
    sr = sub.add_parser('speed-report'); sr.add_argument('--lang', default='ru'); sr.add_argument('--suggest-tm', default=None); sr.add_argument('--keys', default=''); sr.add_argument('--out', default=None)
    val = sub.add_parser('validate'); val.add_argument('--lang', default='ru'); val.add_argument('--tm', default=None); val.add_argument('--frag-tm', default=None); val.add_argument('--suggest-tm', default=None); val.add_argument('--publication', default=None)
    sub.add_parser('selftest')
    args = ap.parse_args()

    if args.cmd == 'selftest':
        return selftest()
    if args.lang not in FIELD:
        sys.exit('unknown --lang %r (ru|en)' % args.lang)
    if args.cmd == 'build':
        if not os.path.exists(args.store):
            sys.exit('store not found: %s' % args.store)
        path, n, skipped = build(args.store, args.lang, out=args.out)
        print('wrote %s (%d content-addressed cards, lang=%s)' % (path, n, args.lang))
        print('  trust:', trust_counts(load_tm(args.lang, path).values()))
        if skipped:
            print('  skipped sub-cards:', dict(skipped))
    elif args.cmd == 'stats':
        entries = load_tm(args.lang, args.tm)
        senses = sum(e.get('n_senses', 0) for e in entries.values())
        roots = Counter(e.get('root') for e in entries.values())
        print('TM lang=%s: %d cards, %d senses, %d roots' % (args.lang, len(entries), senses, len(roots)))
        print('  trust:', trust_counts(entries.values()))
        for root, c in roots.most_common(12):
            print('  %-10s %d cards' % (root, c))
    elif args.cmd == 'lookup':
        e = lookup(args.lang, args.sha, args.tm)
        print(json.dumps(e, ensure_ascii=False, indent=2) if e else '(miss)')
    elif args.cmd == 'build-frags':
        path, added, total = build_frags(args.glob, args.lang, out=args.out)
        print('wrote %s (+%d new fragment(s), %d total, lang=%s)' % (path, added, total, args.lang))
    elif args.cmd == 'frag-stats':
        cache = load_frag_tm(args.lang, args.out)
        senses = sum(len(e.get('senses') or []) for e in cache.values())
        roots = Counter(e.get('root') for e in cache.values())
        print('frag TM lang=%s: %d fragments, %d senses, %d roots' % (args.lang, len(cache), senses, len(roots)))
        print('  trust:', trust_counts(cache.values()))
        for root, c in roots.most_common(12):
            print('  %-10s %d fragments' % (root, c))
    elif args.cmd == 'build-suggestions':
        try:
            path, n = build_suggestions(args.lang, mw_tm=args.mw_tm,
                                        terminology=args.terminology, out=args.out)
        except (ValueError, FileNotFoundError) as e:
            sys.exit(str(e))
        print('wrote %s (%d suggestion(s), lang=%s)' % (path, n, args.lang))
    elif args.cmd == 'export-publication':
        pub, manifest_path, datasheet_path, manifest = export_publication(
            args.lang, args.out_dir, tm=args.tm, frag_tm=args.frag_tm,
            suggest_tm=args.suggest_tm, store=args.store)
        print('wrote publication TM -> %s (%d rows)' % (pub, manifest['record_count']))
        print('wrote manifest       -> %s' % manifest_path)
        print('wrote datasheet      -> %s' % datasheet_path)
    elif args.cmd == 'export-terminology':
        terms_path, manifest = export_terminology(args.lang, args.out_dir,
                                                  suggest_tm=args.suggest_tm)
        print('wrote terminology -> %s (%d terms)' %
              (terms_path, manifest['term_count']))
    elif args.cmd == 'speed-report':
        keys = [k for k in args.keys.split(',') if k]
        report = speed_report(args.lang, suggest_tm=args.suggest_tm, keys=keys,
                              out=args.out)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.cmd == 'validate':
        checks = []
        for kind, path in (('card', args.tm), ('fragment', args.frag_tm),
                           ('suggestion', args.suggest_tm),
                           ('publication', args.publication)):
            if path is None:
                default = {'card': tm_path, 'fragment': frag_tm_path,
                           'suggestion': suggest_tm_path,
                           'publication': lambda _lang: os.path.join(
                               REPO, 'release', 'translation_memory',
                               'translation_memory.%s.publication.jsonl' % _lang)}[kind](args.lang)
                if not os.path.exists(default):
                    continue
                path = default
            ok, stats = validate_tm_file(args.lang, path, kind=kind)
            checks.append((kind, path, ok, stats))
        if not checks:
            sys.exit('no TM sidecar found or specified')
        bad = False
        for kind, path, ok, stats in checks:
            print('%s TM validation: %s (%d ok) stats=%s' %
                  (kind, path, ok, dict(stats)))
            if not validation_ok(stats):
                bad = True
        if bad:
            sys.exit(1)


if __name__ == '__main__':
    main()
