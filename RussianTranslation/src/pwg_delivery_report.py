#!/usr/bin/env python
"""Derived PWG delivery report (H4052): delivered translation outcomes vs staging-only work.

One derived report over the EXISTING readers — release_readiness.review_counts /
gold_counts, store_flags.is_print_ready, store_path.canonical_store — plus the durable
surfaces (canonical store, pwg-ru-data TM mirror, mirror_refresh_ledger). No new
dashboard framework; this is a point-in-time digest with an explicit evidence rule:

    Missing evidence is UNKNOWN (None), never zero.

The delivered-translation assertion (classify_receipt / is_delivered_translation) is the
regression-guarded core: a receipt whose stage is staging, reconciliation, or unknown —
including a merged docs-only staging PR — can never satisfy "delivered translation".
Only a promotion-journal-terminal stage (store_committed/complete) backed by a changed
canonical-store fingerprint and a promotion id counts. H4052 regression pins the
H3679 (STAGED ONLY) and H3690 (lineage reconcile) receipts as NOT delivered.

Usage:
    python src/pwg_delivery_report.py                      # print report to stdout
    python src/pwg_delivery_report.py --out-json PATH --out-md PATH
    python src/pwg_delivery_report.py --selftest
"""
import argparse
import collections
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import release_readiness  # noqa: E402  (existing reader: review/gold counters)
import store_flags        # noqa: E402  (existing reader: the G5 print-ready predicate)
import store_path         # noqa: E402  (existing reader: canonical store resolution)

SEVEN_KEYS = (
    # safe name, SLP1 key1, class, reason code (evidence: FINDINGS §614 / H3663 §4)
    ('jar_ayu', 'jarAyu', 'defect', 'wrapper_never_emitted (FINDINGS §614)'),
    ('r_ama_wa', 'rAmaWa', 'defect', 'wrappers_intact_other_defect (H3663 §4)'),
    ('_s_ulin', 'SUlin', 'defect', 'wrapper_never_emitted (FINDINGS §614)'),
    ('ut_ta', 'utTa', 'defect', 'wrappers_intact_other_defect (H3663 §4)'),
    ('y_atu', 'yAtu', 'defect', 'wrappers_intact_other_defect (H3663 §4)'),
    ('v_as_a', 'vAsA', 'defect', 'wrappers_intact_other_defect (H3663 §4)'),
    ('ut_t_apana', 'utTApana', 'transient', 'transient_retry_heal_exhausted (H3663 §3)'),
)

# Terminal stages of the pwg.promotion_journal.v1 ladder that mean bytes reached the
# canonical store. Everything else is preparation, staging, reconciliation or unknown.
DELIVERY_TERMINAL_STAGES = {'store_committed', 'complete'}
KNOWN_NONDELIVERY_STAGES = {
    'selected': 'selected',
    'prepared': 'staged',
    'staged': 'staged_only',
    'staged_only': 'staged_only',
    'reconciled': 'reconciliation',
    'reconciliation': 'reconciliation',
}


def sha256_file(path):
    """Hex sha256 of a file, or None when it is absent (unknown, never a fake hash)."""
    if not path or not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def classify_receipt(receipt):
    """One evidence-backed classification of a work receipt.

    Returns 'delivered_translation' only for a promotion-journal-terminal stage backed
    by BOTH a changed canonical-store fingerprint AND a promotion id. Staging receipts
    (merged docs PRs included), reconciliation receipts and unknowns are classified as
    what they are — never as delivery.
    """
    if not isinstance(receipt, dict):
        return 'unknown'
    stage = (receipt.get('stage') or '').strip().lower()
    if stage in DELIVERY_TERMINAL_STAGES:
        fingerprint_changed = bool(receipt.get('store_fingerprint_changed'))
        promotion_id = (receipt.get('promotion_id') or '').strip()
        if fingerprint_changed and promotion_id:
            return 'delivered_translation'
        return 'unknown'
    if stage in KNOWN_NONDELIVERY_STAGES:
        return KNOWN_NONDELIVERY_STAGES[stage]
    return 'unknown'


def is_delivered_translation(receipt):
    """The assertion other gates may call. Unknown and staged are NOT delivered."""
    return classify_receipt(receipt) == 'delivered_translation'


def resolve_store_surface():
    """(path, surface) — env override, then canonical store, then the pwg-ru-data mirror."""
    env = os.environ.get('PWG_RU_STORE')
    if env:
        return env, 'PWG_RU_STORE override'
    default = os.path.join(HERE, 'pwg_ru_translated.jsonl')
    canonical = store_path.canonical_store(default)
    if os.path.isfile(canonical):
        return canonical, 'canonical store (store_path.canonical_store)'
    try:
        mirror = os.path.join(store_path.canonical_data_repo(HERE), 'tm',
                              'pwg_ru_translated.jsonl')
    except (OSError, RuntimeError):
        mirror = None
    if mirror and os.path.isfile(mirror):
        return mirror, 'pwg-ru-data durable TM mirror'
    return None, 'unknown'


def store_census(store_path_str):
    """Count sense rows, subcards, headwords, statuses, print-ready, last generation.

    Returns None when the surface itself is absent — the whole census is then unknown.
    """
    if not store_path_str or not os.path.isfile(store_path_str):
        return None
    rows = 0
    headwords = set()
    subcards = set()
    statuses = collections.Counter()
    print_ready = 0
    last_generated_at = None
    generated_rows = 0
    with open(store_path_str, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            rows += 1
            key1 = row.get('key1')
            subcard = row.get('subcard')
            if key1:
                headwords.add(key1)
            if key1 and subcard:
                subcards.add((key1, subcard))
            statuses[(row.get('review_status') or 'unknown')] += 1
            if store_flags.is_print_ready(row):
                print_ready += 1
            prov = row.get('provenance') or {}
            gen_at = prov.get('generated_at')
            if gen_at:
                generated_rows += 1
                if last_generated_at is None or gen_at > last_generated_at:
                    last_generated_at = gen_at
    return {
        'sense_rows': rows,
        'headwords': len(headwords),
        'subcards': len(subcards),
        'review_status_counts': dict(sorted(statuses.items())),
        'print_ready': print_ready,
        'last_generated_at': last_generated_at,
        'rows_with_generated_at': generated_rows,
    }


def seven_key_dispositions(census_keys):
    """One evidence-backed disposition per Lane A seven-key chain key."""
    out = []
    for safe, slp1, klass, reason in SEVEN_KEYS:
        present = census_keys is not None and slp1 in census_keys
        out.append({
            'safe_name': safe,
            'key1': slp1,
            'class': klass,
            'in_store': present,
            'reason_code': reason,
            'translated_paid': 'once, H3663 c1 chunks (29-08)',
            'deterministic_repair': 'ineligible — wrappers never emitted / intact (FINDINGS §614; PR #789 rule)',
            'retranslation': 'NOT executed — staged only (H3679, PR #1978); fire not run (H3690 reconciled lineage only, PR #1981)',
            'disposition': 'residual_unfired' if not present else 'present_in_store_recheck_lane_docs',
            'evidence': [
                'RussianTranslation/pwg_ru/h3663/H3663_LANE_A_16KEY_C1_WINDOW_29-08-2026.md §4/§10',
                'RussianTranslation/pwg_ru/h3679/H3679_LANE_A_TAIL_7KEY_C1_RERUN_STAGED_29-08-2026.md',
                'pwg-ru-data raws/ (14 fire inputs, commit dd1af94)',
                'Uprava GTD @DO: Fire H3679 paid c1 window (active owner)',
            ],
        })
    return out


def read_mirror_ledger(data_repo):
    """Last durable mirror-refresh ledger entry, or None (unknown)."""
    path = os.path.join(data_repo, 'tm', 'mirror_refresh_ledger.jsonl')
    if not os.path.isfile(path):
        return None
    last = None
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                last = json.loads(line)
    return last


def build_report(data_repo=None):
    """Assemble the delivery digest. Every absent surface is None/unknown, never 0."""
    store_path_str, surface = resolve_store_surface()
    census = store_census(store_path_str)
    census_keys = set()
    if census and store_path_str:
        with open(store_path_str, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    if row.get('key1'):
                        census_keys.add(row['key1'])

    review_csv = release_readiness.REVIEW_CSV
    gold_csv = release_readiness.GOLD_CSV
    gold_labels = release_readiness.GOLD_LABELS
    review = release_readiness.review_counts() if os.path.isfile(review_csv) else None
    gold = release_readiness.gold_counts() if (
        os.path.isfile(gold_csv) or os.path.isfile(gold_labels)) else None

    tm_ru = os.path.join(store_path.canonical_sidecar(
        os.path.join(HERE, 'pilot', 'translation_memory.ru.json')))
    tm_count = None
    if os.path.isfile(tm_ru):
        try:
            with open(tm_ru, encoding='utf-8') as f:
                tm = json.load(f)
            tm_count = len(tm) if isinstance(tm, (dict, list)) else None
        except (ValueError, OSError):
            tm_count = None

    ledger = read_mirror_ledger(data_repo) if data_repo else None
    ledger_history = []
    ledger_path = os.path.join(data_repo or '', 'tm', 'mirror_refresh_ledger.jsonl')
    if os.path.isfile(ledger_path):
        with open(ledger_path, encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                ledger_history.append({
                    'handoff': r.get('handoff'), 'ts': r.get('ts'),
                    'src_rows': r.get('src_rows'),
                    'mirror_rows_before': r.get('mirror_rows_before'),
                    'mirror_rows_after': r.get('mirror_rows_after'),
                    'mirror_sha_after': (r.get('mirror_sha_after') or '')[:16] or None,
                })
    raws_dir = os.path.join(data_repo, 'raws') if data_repo else None
    seven_stems = {s for s, _, _, _ in SEVEN_KEYS}
    seven_input_files = sorted(
        p for p in (os.listdir(raws_dir) if raws_dir and os.path.isdir(raws_dir) else [])
        if p.split('.')[0] in seven_stems)

    staged_receipt = {
        'handoff': 'H3679', 'stage': 'staged', 'paid_calls': 0,
        'artifacts': ['PR #1978 merged (docs/inputs/chunk manifests)'],
        'store_fingerprint_changed': False, 'promotion_id': None,
    }
    reconcile_receipt = {
        'handoff': 'H3690', 'stage': 'reconciled', 'paid_calls': 0,
        'artifacts': ['PR #1981 merged (lineage verdict doc)'],
        'store_fingerprint_changed': False, 'promotion_id': None,
    }

    report = {
        'generated_for': 'H4052 — PWG delivery metrics and truthful partial closeouts',
        'surface': surface,
        'store_sha256': sha256_file(store_path_str) if store_path_str else None,
        'census': census,
        'delivery_funnel_store_level': {
            'sense_rows': census['sense_rows'] if census else None,
            'approved': census['review_status_counts'].get('approved') if census else None,
            'print_ready': census['print_ready'] if census else None,
            'review_queue': review,
            'gold': gold,
            'tm_fragments': tm_count,
            'released_edition': False if census else None,
            'released_note': 'no edition cut exists; G10 blocked (release_readiness local gates)',
        },
        'lane_a_seven_key_chain': {
            'selected': len(SEVEN_KEYS),
            'called_paid': 0,
            'called_evidence': 'H3679 close: STAGED ONLY, zero paid calls; no durable '
                               'probe-log receipts for this lane after 30-08 00:00Z',
            'audit_clean_new_windows': 0,
            'promoted': 0,
            'approved': 0,
            'released': 0,
            'fire_inputs_durable': len(seven_input_files),
            'fire_inputs_files': seven_input_files,
            'blocked_keys': seven_key_dispositions(census_keys),
        },
        'receipt_classification': {
            'H3679': classify_receipt(staged_receipt),
            'H3690': classify_receipt(reconcile_receipt),
        },
        'durable_events': {
            'last_mirror_refresh_ledger_entry': ledger,
            'mirror_refresh_ledger_history': ledger_history,
            'last_row_generated_at': census['last_generated_at'] if census else None,
            'note': 'generated_at is the paid generation timestamp; the store rows carry '
                    'no promoted_at, so promotion time is bounded by the mirror ledger.',
        },
        'source_hashes': {
            'store': report_store_hash(store_path_str),
            'review_csv': sha256_file(review_csv),
            'gold_csv': sha256_file(gold_csv),
            'gold_labels': sha256_file(gold_labels),
        },
        'delta': {
            'audit_04_09_baseline': {
                'sense_rows': 11519,
                'approved_print_ready': 3,
                'review_decisions': 5,
                'gold_complete': '0/320',
                'store_sha256': '79d72dbcb4b33fc88d9e907dec9ecaa0e56ebfb72495a5115ce951a623f8ca65',
            },
            'h3690_reconcile_29_08': {'durable_mirror_rows': 11462},
            'comparable': bool(census),
            'explanation': None,
        },
        'unknown_surfaces': [name for name, val in (
            ('review_queue_csv', review), ('gold_csv', gold), ('tm_fragments', tm_count)
        ) if val is None],
    }
    if census and report['store_sha256']:
        base = report['delta']['audit_04_09_baseline']
        if census['sense_rows'] == base['sense_rows'] and \
                report['store_sha256'] == base['store_sha256']:
            report['delta']['explanation'] = (
                'reproduces the 04-09 audit baseline exactly (rows and sha256). '
                'The durable mirror has held 11 519 rows since 29-08 11:24Z (H3663 '
                'refreshes) and converged byte-exact to the Windows canonical on 02-09 '
                '(H3947 refresh, mirror_sha 58c21726... -> 79d72dbc...); the H3690 '
                '"11 462 durable base" verdict is superseded by the append-only '
                'ledger, and the fire-time (a)/(b) store-base gate is satisfied on '
                'durable evidence.')
        else:
            report['delta']['explanation'] = (
                'differs from the 04-09 audit baseline - newer digest; sha256 %s vs %s'
                % (report['store_sha256'], base['store_sha256']))
    else:
        report['delta']['explanation'] = 'no store surface readable on this box — census unknown'
    return report


def report_store_hash(store_path_str):
    return sha256_file(store_path_str) if store_path_str else None


def render_md(r):
    """Compact human digest of the JSON report."""
    c = r.get('census') or {}
    f = r['delivery_funnel_store_level']
    lines = [
        '# PWG delivery report (derived, H4052)',
        '',
        'Surface: `%s` · store sha256 `%s`' % (r['surface'], r['store_sha256'] or 'unknown'),
        '',
        '| measure | value |',
        '|---|---|',
        '| store sense rows | %s |' % c.get('sense_rows', 'unknown'),
        '| headwords (distinct key1) | %s |' % c.get('headwords', 'unknown'),
        '| subcards (distinct key1+subcard) | %s |' % c.get('subcards', 'unknown'),
        '| approved | %s |' % f.get('approved', 'unknown'),
        '| print-ready (store_flags predicate) | %s |' % f.get('print_ready', 'unknown'),
        '| review queue | %s |' % (json.dumps(f['review_queue']) if f['review_queue'] else 'unknown (surface absent on this box)'),
        '| gold labels | %s |' % (json.dumps(f['gold']) if f['gold'] else 'unknown (surface absent on this box)'),
        '| TM fragments | %s |' % (f['tm_fragments'] if f['tm_fragments'] is not None else 'unknown (surface absent on this box)'),
        '| released edition | no (G10 blocked) |',
        '| last row generated_at | %s |' % (r['durable_events']['last_row_generated_at'] or 'unknown'),
        '| last mirror ledger entry | %s |' % json.dumps(r['durable_events']['last_mirror_refresh_ledger_entry']) if r['durable_events']['last_mirror_refresh_ledger_entry'] else '| last mirror ledger entry | unknown |',
        '',
        '## Lane A seven-key chain — one disposition per key',
        '',
        '| key | class | in store | disposition | reason code |',
        '|---|---|---|---|---|',
    ]
    for k in r['lane_a_seven_key_chain']['blocked_keys']:
        lines.append('| `%s` | %s | %s | %s | %s |' % (
            k['safe_name'], k['class'], k['in_store'], k['disposition'], k['reason_code']))
    lines += [
        '',
        'Chain funnel: selected=%(selected)d · paid calls=%(called_paid)d '
        '(staged only, H3679) · audit-clean new=0 · promoted=0 · approved=0 · released=0 · '
        'durable fire inputs=%(fire_inputs_durable)d/7 keys' % r['lane_a_seven_key_chain'],
        '',
        'Receipt classification (delivered-translation assertion): %s' % json.dumps(r['receipt_classification']),
        '',
        'Delta: %s' % r['delta']['explanation'],
        '',
        'Unknown surfaces (missing evidence is unknown, never zero): %s' % (', '.join(r['unknown_surfaces']) or 'none'),
        '',
        'Remaining work owner: Uprava GTD `@DO` — Fire H3679 paid c1 window '
        '(7 held Lane A keys), active and bounded.',
        '',
        '_Dr. Mārcis Gasūns_',
    ]
    return '\n'.join(lines) + '\n'


def selftest():
    import tempfile
    # 1. regression (H4052 acceptance): a STAGED ONLY receipt can NEVER satisfy the
    #    delivered-translation assertion — even with a merged PR and zero paid calls.
    staged = {'handoff': 'H3679', 'stage': 'staged_only', 'paid_calls': 0,
              'artifacts': ['PR #1978 merged'], 'store_fingerprint_changed': False,
              'promotion_id': None}
    assert classify_receipt(staged) == 'staged_only'
    assert not is_delivered_translation(staged)
    # 2. reconciliation receipt (H3690) is not delivery either.
    rec = {'handoff': 'H3690', 'stage': 'reconciled', 'store_fingerprint_changed': False,
           'promotion_id': None}
    assert classify_receipt(rec) == 'reconciliation'
    assert not is_delivered_translation(rec)
    # 3. a docs-only receipt (stage omitted, PR merged) is unknown -> not delivered.
    assert not is_delivered_translation({'artifacts': ['docs PR merged']})
    # 4. unknown stage fails closed.
    assert not is_delivered_translation({'stage': 'something_else'})
    # 5. positive control: terminal stage + changed store fingerprint + promotion id.
    delivered = {'stage': 'complete', 'store_fingerprint_changed': True,
                 'promotion_id': 'h3663-lane-a'}
    assert classify_receipt(delivered) == 'delivered_translation'
    assert is_delivered_translation(delivered)
    # 6. negative control: claims terminal but the store fingerprint did NOT change.
    noop = {'stage': 'complete', 'store_fingerprint_changed': False,
            'promotion_id': 'x'}
    assert classify_receipt(noop) == 'unknown'
    assert not is_delivered_translation(noop)
    # 7. census counts rows/subcards/headwords separately on a synthetic store.
    with tempfile.TemporaryDirectory() as d:
        sp = os.path.join(d, 'store.jsonl')
        rows = [
            {'key1': 'a', 'subcard': 'a', 'review_status': 'approved', 'ru': 'x', 'de': 'y'},
            {'key1': 'a', 'subcard': 'a2', 'review_status': 'approved', 'ru': 'x', 'de': 'y'},
            {'key1': 'b', 'subcard': 'b1', 'review_status': 'ai_translated', 'ru': 'x', 'de': 'y'},
        ]
        with open(sp, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        c = store_census(sp)
        assert c['sense_rows'] == 3 and c['headwords'] == 2 and c['subcards'] == 3, c
        assert c['review_status_counts'] == {'ai_translated': 1, 'approved': 2}
    # 8. absent census surface is None (unknown), never zero.
    assert store_census(os.path.join('no', 'such', 'store.jsonl')) is None
    # 9. sha of an absent file is None.
    assert sha256_file(None) is None and sha256_file('no/such/file') is None
    print('pwg_delivery_report selftest: PASS (staged/reconciled/unknown never satisfy '
          'delivered-translation; census rows/subcards/headwords counted separately; '
          'absent surfaces unknown)')
    return True


def main():
    ap = argparse.ArgumentParser(description='derived PWG delivery report (H4052)')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--data-repo', default=store_path.canonical_data_repo(HERE),
                    help='pwg-ru-data durable data repo root')
    ap.add_argument('--out-json', default=None)
    ap.add_argument('--out-md', default=None)
    args = ap.parse_args()
    if args.selftest:
        return 0 if selftest() else 1
    report = build_report(args.data_repo)
    blob = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=False)
    if args.out_json:
        os.makedirs(os.path.dirname(os.path.abspath(args.out_json)) or '.', exist_ok=True)
        with open(args.out_json, 'w', encoding='utf-8') as f:
            f.write(blob + '\n')
    if args.out_md:
        os.makedirs(os.path.dirname(os.path.abspath(args.out_md)) or '.', exist_ok=True)
        with open(args.out_md, 'w', encoding='utf-8') as f:
            f.write(render_md(report))
    print(blob)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
