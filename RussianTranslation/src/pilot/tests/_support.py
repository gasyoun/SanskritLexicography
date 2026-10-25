"""Shared state for the frequency-window guardrail suite.

Split out of `window_selftest.py` by H7241. Importing this module is what the old file's
header did, in the same order and with the same values:

* production isolation is ESTABLISHED here, not assumed -- `guard()` pins every redirectable
  production path to scratch (store, coordinator dir, TM sidecars, events log) BEFORE any
  repo import, and arms an exit tripwire over the production files that have no override
  (see `selftest_isolation.py`)
* `HERE` is `src/pilot`, NOT this file's directory: the fixtures below address files
  relative to the pilot dir exactly as they did before the split
* `PILOT_DIR` is the same value under a name test modules can read without implying it is
  their own `__file__`

Nothing else in here is new code.
"""
import hashlib
import contextlib
import datetime
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import xml.etree.ElementTree as ET
# This file lives in `tests/`, so one extra dirname lands on `src/pilot`. The
# value is identical to the old `window_selftest.py` HERE, which is what every
# fixture below addresses files against.
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(SRC)
OUT = os.path.join(HERE, 'output')
PILOT_DIR = HERE     # the old file's own directory, under a second name
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from selftest_isolation import guard as _isolation_guard  # noqa: E402
_isolation_guard()
from workflow_payload import workflow_payload
from window_common import harness_meta
from window_provenance import current_root_provenance, stale_check
from prompt_rule_audit import (
    DEFAULT_TEMPLATE,
    audit_card_result,
    audit_cards,
    build_report,
    braced_gloss_risks,
    semantic_risks,
)
from fix_german_connectives import fix_text as fix_german_text
import audit_coverage
from sense_count import (                                    # H920 SAN-LOSS guard
    count_source_senses,
    output_sense_count,
    scan_sense_shortfall,
    sense_shortfall,
)
def fail(message):
    raise AssertionError(message)
def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()
@contextlib.contextmanager
def gam_pilot_fixture():
    """Provide the small/dense gam pilot files required by preflight tests.

    Older checkouts carried these as ignored runtime artifacts. Keep the tests
    hermetic by materializing only the stems they need, then restoring any
    pre-existing local files.
    """
    inp = os.path.join(HERE, 'input')
    os.makedirs(inp, exist_ok=True)
    dense_key = 'gam~~h0_00_pwg00'
    small_key = 'gam~~h0_03_sec_3'
    files = {
        'gam.rootmap.json': json.dumps({
            'schema': 'pwg.rootmap.fixture.v1',
            'root': 'gam',
            'sub_cards': [{'subkey': dense_key}, {'subkey': small_key}],
        }, ensure_ascii=False),
        dense_key + '.raw.txt': (
            '=== LAYER: PWG - MAIN ENTRY ===\n'
            '{#gam#}¦ dense citation fixture '
            + ' '.join('<ls>RV. %03d</ls>' % i for i in range(1, 151))
            + ' 〉 end.\n'
        ),
        dense_key + '.portrait.json': json.dumps({'key1': 'gam', 'lex': 'm.'}),
        small_key + '.raw.txt': (
            '=== LAYER: PWG - MAIN ENTRY ===\n'
            '{#gam#}¦ gehen <ls>RV. 1</ls>.\n'
        ),
        small_key + '.portrait.json': json.dumps({'key1': 'gam', 'lex': 'm.'}),
        'ab.raw.txt': (
            '=== LAYER: PWG - MAIN ENTRY ===\n'
            '{#ab#}¦ <ab>vgl.</ab> {#a#}.\n'
        ),
        'ab.portrait.json': json.dumps({'key1': 'ab', 'lex': 'indecl.'}),
    }
    backup = {}
    try:
        for name, text in files.items():
            path = os.path.join(inp, name)
            backup[path] = open(path, encoding='utf-8').read() if os.path.exists(path) else None
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
        yield
    finally:
        for path, old in backup.items():
            if old is None:
                try:
                    os.remove(path)
                except OSError:
                    pass
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(old)
@contextlib.contextmanager
def matrix_pilot_fixture():
    """Provide deterministic multi-root preflight inputs and a tiny TM sidecar."""
    inp = os.path.join(HERE, 'input')
    os.makedirs(inp, exist_ok=True)

    def small_raw(root):
        return '=== LAYER: PWG - MAIN ENTRY ===\n1) {#%s#} {%%gehen%%}.\n' % root

    def dense_raw(root, offset):
        return ('=== LAYER: PWG - MAIN ENTRY ===\n' +
                '\n'.join('%d) {#%s#} {%%gehen%%} <ls>RV. %d</ls>.'
                          % (i, root, offset + i)
                          for i in range(1, 26)) + '\n')

    roots = {
        'gam': ['gam~~h0_03_sec_3'],
        'han': ['han~~h0_00_pwg00'],
        'vid': ['vid~~h0_00_pwg00'],
        'as': ['as~~h0_%02d_pwg00' % i for i in range(12)],
    }
    files = {}
    for root, keys in roots.items():
        files[root + '.rootmap.json'] = json.dumps({
            'schema': 'pwg.rootmap.fixture.v1',
            'root': root,
            'sub_cards': [{'subkey': key} for key in keys],
        }, ensure_ascii=False)
        for idx, key in enumerate(keys):
            raw = dense_raw(root, idx * 100) if root == 'as' else small_raw(root)
            files[key + '.raw.txt'] = raw
            files[key + '.portrait.json'] = json.dumps({'key1': root, 'lex': 'm.'})

    backup = {}
    try:
        for name, text in files.items():
            path = os.path.join(inp, name)
            backup[path] = open(path, encoding='utf-8').read() if os.path.exists(path) else None
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
        with tempfile.TemporaryDirectory() as tmp:
            han_key = roots['han'][0]
            han_raw = os.path.join(inp, han_key + '.raw.txt')
            han_body = files[han_key + '.raw.txt']
            tm_sidecar = os.path.join(tmp, 'translation_memory.ru.json')
            with open(tm_sidecar, 'w', encoding='utf-8') as f:
                json.dump({
                    'schema': 'pwg.translation_memory.v1',
                    'lang': 'ru',
                    'entries': {
                        'ru:%s' % sha256(han_raw): {
                            'src_key': han_key,
                            # Schema-complete TM card (B03/H1339): notes + record h/grammar
                            # are required; the serve guard refuses legacy-shaped cards.
                            'card': {
                                'key1': 'han',
                                'iast': 'han',
                                'notes': '',
                                'records': [{'h': '', 'grammar': '', 'senses': [{
                                    'tag': '1',
                                    'german': han_body,
                                    'russian': han_body,
                                }]}],
                            },
                        },
                    },
                }, f, ensure_ascii=False)
            yield tm_sidecar
    finally:
        for path, old in backup.items():
            if old is None:
                try:
                    os.remove(path)
                except OSError:
                    pass
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(old)
@contextlib.contextmanager
def no_pwg_dictionary_fixture():
    """Provide a minimal isolated CDSL universe for no-PWG tests.

    The real indexes live in an untracked sibling ``csl-orig`` checkout, which GitHub
    runners do not have. Replace every local-data entry point used by these tests so
    their result is identical with or without that sibling, then restore the process
    caches and paths exactly as they were.
    """
    import corpus_gate as cg
    import dict_merge as dm

    def record(lid, key, body):
        return ['<L>%s<pc>1<k1>%s<k2>%s<h>1<e>1' % (lid, key, key), body]

    fixture_idx = {
        'pwg': {
            cg.form_key('agni'): [record('1', 'agni', '{#agni#}¦ {%Feuer%}.')],
        },
        'pw': {
            cg.form_key('Bagavat'): [
                record('2', 'Bagavat', '{#Bagavat#}¦ {%ehrwürdig, glückselig%}.'),
            ],
        },
        'sch': {
            cg.form_key('Akulita'): [
                record('3', 'Akulita', '{#Akulita#}¦ {%nicht gekrümmt%}.'),
            ],
        },
        'pwkvn': {},
    }
    old_idx = dm._IDX
    old_ididx = dm._IDIDX
    old_v02 = dm.V02
    old_nws_dir = dm.NWS_DIR
    with tempfile.TemporaryDirectory() as tmp:
        try:
            dm._IDX = fixture_idx
            dm._IDIDX = {}
            dm.V02 = os.path.join(tmp, 'v02')
            dm.NWS_DIR = os.path.join(tmp, 'nws')
            os.makedirs(dm.V02)
            os.makedirs(dm.NWS_DIR)
            yield
        finally:
            dm._IDX = old_idx
            dm._IDIDX = old_ididx
            dm.V02 = old_v02
            dm.NWS_DIR = old_nws_dir
def manifest_files(edition_dir):
    files = {}
    for dirpath, _dirs, names in os.walk(edition_dir):
        for name in names:
            if name == 'release_manifest.json':
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, edition_dir).replace('\\', '/')
            files[rel] = {'sha256': sha256(path), 'bytes': os.path.getsize(path)}
    return dict(sorted(files.items()))
def load_gate_statuses(edition_dir):
    statuses = {}
    path = os.path.join(edition_dir, 'roadmap', 'quality_gates.jsonl')
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                statuses[row.get('id')] = row.get('status')
    return statuses
def write_minimal_edition(edition_dir):
    os.makedirs(edition_dir, exist_ok=True)
    shutil.copytree(os.path.join(ROOT, 'schemas'), os.path.join(edition_dir, 'schemas'))
    shutil.copytree(os.path.join(ROOT, 'roadmap'), os.path.join(edition_dir, 'roadmap'))
    for name in ('CITATION.cff', 'DOI_PLAN.md'):
        shutil.copy2(os.path.join(ROOT, name), os.path.join(edition_dir, name))
    with open(os.path.join(edition_dir, 'assembled_cards.jsonl'), 'w', encoding='utf-8') as f:
        f.write(json.dumps({'key1': 'agni', 'records': [{'lossless': True}]}, ensure_ascii=False) + '\n')
    with open(os.path.join(edition_dir, 'reverse_index.jsonl'), 'w', encoding='utf-8') as f:
        f.write(json.dumps({'ru': 'огонь', 'key1': 'agni'}, ensure_ascii=False) + '\n')
    with open(os.path.join(edition_dir, 'tei_lex0.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?><TEI><text><body><entry xml:id="agni"/></body></text></TEI>\n')
    ET.parse(os.path.join(edition_dir, 'tei_lex0.xml'))
    with open(os.path.join(edition_dir, 'ontolex.ttl'), 'w', encoding='utf-8') as f:
        f.write('@prefix ontolex: <http://www.w3.org/ns/lemon/ontolex#> .\n')
        f.write('<agni> a ontolex:LexicalEntry .\n')
    manifest = {
        'edition_id': os.path.basename(edition_dir),
        'gate_statuses': load_gate_statuses(edition_dir),
        'files': manifest_files(edition_dir),
    }
    with open(os.path.join(edition_dir, 'release_manifest.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
def run(cmd, expect):
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    if proc.returncode != expect:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        fail('%s returned %d, expected %d' % (' '.join(cmd), proc.returncode, expect))
    return proc
def sealed_card(key, senses=None):
    """A schema-complete final card. Promotion validates the card itself now, so a bare
    {'key1': k} stub no longer stands in for one (CARD_REQUIRED = key1/iast/records/notes).

    `senses` defaults to EMPTY: a fixture that only needs a structurally valid card should
    not also mint sense identities, or promoting the same artifact from two paths (a
    lease's wf_output and its clean_output are the same rows) trips the duplicate-identity
    guard on content the test never cared about. Pass senses explicitly when the test is
    about sense content."""
    return {'key1': key, 'iast': key, 'notes': '',
            'records': [{'h': key, 'grammar': '',
                         'senses': list(senses or [{'tag': '1', 'german': 'Feuer',
                                                    'russian': 'огонь'}])}]}
def sealed_wf_meta(keys, root='test', nominal=False):
    """A manifest-v2 `meta` block that satisfies validate_promotion_entry.

    Promotion is now a sealed contract: v1/unbound workflow output is historical-only and
    cannot be promoted, and the six `execution.*` fields plus per-key input hashes and
    provenance must all be present. Fixtures that only need "a promotable result" build
    their meta from here rather than each re-deriving the contract (and drifting from it).
    Every field below is one the validator names explicitly.
    """
    h = '0' * 64
    return {
        'execution_manifest_schema': 'pwg.headless_execution_manifest.v2',
        'execution': {
            'profile_slot': 'c4',
            'config_dir_fingerprint': h,
            'execution_route': 'claude-cli-headless',
            'executor_lane': 'serial-whole-card',
            'validation_method': 'window_selftest-fixture',
            'model_identifier': 'claude-sonnet-5',
        },
        'selected_keys': list(keys),
        'input_hashes': {k: {'raw_sha256': h, 'portrait_sha256': h} for k in keys},
        'generator': 'window_selftest',
        'schema_version': 'v2',
        'generated_at': '2026-07-26T00:00:00Z',
        'provenance_classes': {k: 'real' for k in keys},
        'nominal': nominal,
        'root': root,
    }
PREFLIGHT_STDOUT = json.dumps({
    'schema': 'pwg.performance_preflight.v1',
    'root': 'test',
    'cost_gate': {'over_ceiling': False},
})
def _sealed_preflight(tmp, root='test', keys=()):
    """A real, self-validating preflight artifact for coordinator fixtures.

    `register_prepared_lease` hashes this path and `validate_lease_preflight` re-checks the
    hash and the cost gate before a lease may consume runtime, so a fixture cannot pass a
    placeholder string any more. `write_synthetic_preflight` is the shipped builder for
    exactly this -- explicit zero-work evidence, validated on write.
    """
    import max_account_orchestrator as _mao
    return _mao.write_synthetic_preflight(os.path.join(tmp, 'preflight.json'), root, list(keys))
def semantic_card_risk_ids(russian, german='{%nachgehen%}'):
    card = {'card': {'key1': 'x', 'iast': 'x', 'notes': '', 'records': [{
        'h': 'x', 'grammar': 'ind.', 'senses': [{
            'tag': '1', 'german': german, 'russian': russian,
            'equivalence_type': 'explanatory', 'source_type': 'lexicographic',
            'stratum': '', 'differentia': ''}]}]}}
    return {risk['id'] for risk in semantic_risks(card)}
def _h4054_synth_inputs(gh, d, specs):
    """Write the H4054 synthetic raw/portrait fixtures and return a monkeypatched
    gh.input_paths serving exactly those keys (H823-test pattern)."""
    real_ip = gh.input_paths
    paths = {}
    for key, n_ls in specs:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        lines = ['=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n',
                 '{#%s#}¦ <lex>Adj.</lex>\n' % key.split('~~')[0]]
        for i in range(1, n_ls + 1):
            lines.append('— %d〉 {%%Bedeutung %d%%} <ls>Ref. %d</ls>.\n' % (i, i, i))
        if n_ls == 0:
            lines.append('— 1〉 {%Bedeutung eins%}.\n')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(''.join(lines))
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        paths[key] = (rp, pp)
    return (lambda k, input_dir=None: paths[k] if k in paths else real_ip(k))
# Original execution order of the legacy runner. conftest.py sorts pytest
# collection by it, so a pytest run is order-for-order the old one.
ORIGINAL_ORDER = (
    'test_h4529_width_policy_and_pool_split',
    'test_restore_covers_every_promoted_field',
    'test_h1339_b21_promoted_pairs_cover_store_write_set',
    'test_h1339_b02_stitched_card_schema_complete',
    'test_h1339_b03_tm_cards_schema_complete',
    'test_h1339_b04_b09_worktree_safe_resolution',
    'test_h1339_b10_b19_audit_chain_routing',
    'test_h1339_b11_b12_denylist_lifecycle_and_crash_refusal',
    'test_h1386_c3_frag_unblock_serves_replacement',
    'test_h1386_p3d_p3e_run_py_inproc_exit_semantics',
    'test_h1386_p3h_stale_check_pins_v2_execution',
    'test_h1339_b13_b15_telemetry_and_siglum_precision',
    'test_every_stitch_emits_record_required',
    'test_unmapped_token_is_counted',
    'test_validator_has_a_live_caller',
    'test_strip_mask_tokens_clears_notes_stranded_anchor',
    'test_translation_memory_addressing',
    'test_tm_pre_resolves_cards',
    'test_tm_card_sane_rejects_zero_marker_drift',
    'test_en_card_tm_serves_english_field_c3',
    'test_generated_harness_strict_key_matching',
    'test_tm_auto_no_sidecar_metadata',
    'test_suggest_tm_does_not_skip_agents',
    'test_tm_publication_fixtures_validate',
    'test_degenerate_passthrough_accounted',
    'test_degenerate_passthrough_no_german_in_target',
    'test_degenerate_passthrough_rejects_glosses',
    'test_perf_preflight_small_tm_and_no_tm',
    'test_perf_preflight_dense_presplit',
    'test_presplit_group_call_weight_caps_portrait_plus_bytes_h2248',
    'test_presplit_group_call_weight_zero_allowance_degrades_to_one_per_call_h2248',
    'test_perf_preflight_presplit_counts_fragments_not_one',
    'test_perf_preflight_degenerate_zero_agent',
    'test_perf_preflight_multi_root_matrix_and_order',
    'test_perf_preflight_fragment_tm_empty_warning',
    'test_perf_preflight_partitions_mixed_monster_window',
    'test_verb_worklist_excludes_missing_rootmaps',
    'test_coordinator_state_dashboard_and_cap',
    'test_coordinator_nominal_reservations',
    'test_coordinator_runtime_state_machine_and_cas',
    'test_coordinator_fail_closed_audit_states',
    'test_coordinator_promotion_revalidates_artifacts',
    'test_coordinator_expired_leases_release_cap',
    'test_coordinator_lock_replaces_stale_dead_owner',
    'test_coordinator_lock_creates_parent_dir',
    'test_coordinator_defect_requeue_uses_no_tm_and_out',
    'test_transient_requeue_no_tm_flag_h4527',
    'test_coordinator_requeue_attempt_manifests',
    'test_coordinator_mixed_lane_public_state_sequence',
    'test_promote_nominal_key1',
    'test_build_emits_nominal_keymap',
    'test_generation_schema_carries_no_post_generation_field',
    'test_no_pwg_supplement_chain_cards_render',
    'test_nominals_worklist_exposes_no_pwg_lane',
    'test_no_pwg_source_profile_promotes',
    'test_calibration_arm_set_conservative_emit_only',
    'test_frag_tm_reuse',
    'test_card_tokens_twins_agree',
    'test_frag_tm_v2_supersedes_v1',
    'test_degenerate_source_identity',
    'test_no_fallback_batch_isolation',
    'test_cit_split_never_tears_open_span',
    'test_sense_split_never_tears_open_span',
    'test_cit_split_caps_single_line_monster_sense',
    'test_selfheal_fragment_si_threaded_and_tags_normalized',
    'test_heal_lane_target_field_fidelity_wired',
    'test_autosplit_stitch_topup_rejects_target_field_drop',
    'test_autosplit_merge_rejects_target_field_drop',
    'test_sense_dense_card_presplit',
    'test_kill_gate_wired',
    'test_no_fallback_single_gets_ceil_kill_budget',
    'test_presplit_cite_floor_and_single_ceil',
    'test_default_call_shape_is_one_card_per_call',
    'test_large_card_presplit_and_heal_under_one_card_default',
    'test_presplit_cite_floor_is_not_masked_by_batch_budget',
    'test_nominal_key_echo_tolerance_scoped',
    'test_selfheal_no_fallback_preserves_upstream_reason',
    'test_group_by_budget_count_cap',
    'test_presplit_card_uses_amortized_grouping',
    'test_kill_gate_recalibrated_envelope',
    'test_agent_budget_plan_separates_translate_and_heal_pools',
    'test_split_agent_pools_all_heal_runtime',
    'test_lowwide_staggered_dispatch',
    'test_budget_kill_switch_wired',
    'test_harness_size_guard',
    'test_perf_preflight_cost_gate',
    'test_launch_failure_ledger_complete',
    'test_launch_failure_ledger_rejects_incomplete_entry',
    'test_autosplit_topup_targets_and_reassembles',
    'test_workflow_payload_nested',
    'test_workflow_payload_missing_results_hard_fail',
    'test_sense_dupe_norm_strips_trailing_period',
    'test_sense_dupe_batch_override',
    'test_sense_dupe_cross_level_exempt',
    'test_export_translation_dedup',
    'test_requeue_transient_vs_defect_state',
    'test_harness_scope_and_tools',
    'test_stale_check_key_order_independent',
    'test_nominal_provenance_without_rootmap',
    'test_atomic_control_writes_preserve_previous_file',
    'test_no_pwg_residual_registry_and_audit_command',
    'test_no_pwg_preparation_advances_past_omitted_chunks',
    'test_no_pwg_require_senses_gate',
    'test_no_pwg_card_source_profile_taxonomy',
    'test_no_pwg_supplement_card_renders_without_pwg',
    'test_h920_sense_count_top_level_ordinals',
    'test_h920_sense_shortfall_gate_flags_dropped_sense',
    'test_h920_no_pwg_portrait_stamps_source_senses',
    'test_h920_en_missing_sense_hard_flag',
    'test_en_dup_gate_preserves_sanskrit_referent_c2',
    'test_h960_accept_sanloss_soft_gate',
    'test_tnmask_persist_and_offline_detect',
    'test_h960_dropped_sanskrit_span',
    'test_no_pwg_worklist_runnable_lane',
    'test_h3659_input_sidecars_parked_beside_manifest',
    'test_no_pwg_layer_and_profile_survive_promotion',
    'test_prompt_rule_audit_template',
    'test_prompt_rule_audit_missing_blocks',
    'test_mask_preamble_carries_task_shape',
    'test_gloss_wrapper_prompt_preservation_h4270',
    'test_health_probe_asks_an_honest_question',
    'test_health_probe_carries_no_injection_shape',
    'test_semantic_risk_checker',
    'test_h1152_guard1_en_polyseme_checklist',
    'test_braced_gloss_audit',
    'test_german_residue_keeps_retained_markup',
    'test_german_connective_fix',
    'test_h1302_german_prose_residue_scan',
    'test_h1305_ru_style_mechanical',
    'test_h1651_wrapper_defect_gate',
    'test_h1651_live_gate_cyrillic_and_guillemet',
    'test_h1702_boundary_wrap_gate',
    'test_h2144_d4b_bracket_normalize',
    'test_semantic_review_prioritizer',
    'test_noisy_source_type_not_requeue',
    'test_report_only_risks_never_requeue',
    'test_attested_text_signal_redesign',
    'test_nws_fp_suppressed',
    'test_en_gate_strict_has_teeth',
    'test_en_gate_dup_has_teeth',
    'test_run_py_survives_timeout_and_oserror',
    'test_ru_gate_fails_loud_on_unparseable_child',
    'test_pwg_mask_latin_cue_behind_ab_tag',
    'test_markup_loss_soft_flag_ru',
    'test_p8_markup_loss_not_masked_by_unrelated_div',
    'test_markup_loss_soft_flag_en',
    'test_en_de_residue_french_guard',
    'test_h1152_guard3_xref_only_and_nws_de_locked',
    'test_p7_missing_en_not_fired_on_xref_only_residue',
    'test_ru_coverage_denominator_not_silently_exempt',
    'test_coverage_gate_multi_layer_and_presplit',
    'test_en_residual_coverage_complete',
    'test_en_split_triage_keeps_missing_input',
    'test_whitney_homonym_safety',
    'test_stale_refusal_preserves_requeue',
    'test_fixture_audit_does_not_clobber_live_status',
    'test_release_manifest_hash_validation',
    'test_h3627_structured_output_exhaustion_is_parked_not_window_fatal',
    'test_h3627_aborted_window_still_yields_its_paid_cards',
    'test_h3627_salvage_never_publishes_an_infra_starved_window',
    'test_h4528_no_progress_kill_is_infra_not_a_content_defect',
    'test_lang_parity_ledger_complete',
    'test_lang_parity_coverage',
    'test_card_coverage_lang_symmetric',
    'test_degenerate_xref_vocab_single_source',
    'test_lang_parity_hash_crlf_independent',
    'test_lang_parity_ledger_refuses_duplicate_keys',
    'test_lang_parity_ledger_refuses_duplicate_entry_ids',
    'test_frag_groups_presplit_parity',
    'test_defect_fragment_denylist_round_trip',
    'test_opt7_last_audit_tm_refuse_without_no_tm',
    'test_write_reports_emits_defect_fsha_file',
    'test_ledger_stamps_gen_model',
    'test_ledger_stamps_host_profile_b8',
    'test_h1553_wall_clock_auto_derive',
    'test_h1553_stage_boundary_emit',
    'test_save_merge_better_attempt_wins',
    'test_defer_monster_ledger_dedupes',
    'test_coordinator_cost_gate_enforced',
    'test_pwg_mask_bom_source_keeps_first_record',
    'test_pwg_mask_truncated_final_record_not_silent',
    'test_subprocess_gate_calls_hardened',
    'test_ls_resolver_rv_av_anchored',
    'test_frag_tm_fidelity_gate_and_override',
    'test_corpus_gate_evidence_and_db_markers',
    'test_promote_claim_contention',
    'test_annotate_evidence_relation_semantics',
    'test_annotate_genres_sense_join',
    'test_koch_xref_resolution',
    'test_fri_xref_resolution',
    'test_audit_window_tag_routing',
    'test_denylist_torn_line_fails_loud',
    'test_per_card_heal_budget_wired',
    'test_heal_group_kill_timeout_does_not_bisect',
    'test_run_telemetry_counters_returned',
    'test_partial_cards_requeue_and_stay_out_of_clean_sample',
    'test_h2077_947_infra_partial_is_not_a_content_defect',
    'test_h2095_956_en_absence_flags_exempt_infra_partial',
    'test_h2095_structured_error_does_not_crash_the_audit',
    'test_classify_run_verdicts',
    'test_h2173_g5_malformed_result_rows_are_accounted',
    'test_h2173_g8_promote_refuses_route_foreign_artifact',
    'test_h2173_g10_classify_run_reads_the_live_lane',
    'test_h2173_g10_probe_gate_defaults_and_live_boundary',
    'test_h2173_g10_declared_budgets_are_read_or_labelled',
    'test_grammar_field_restore_behavioral',
    'test_threaded_gate_exception_requeues_full_window',
    'test_quarantine_replace_failure_preserves_previous_destination',
    'test_selftest_isolation_guard',
    'test_optional_sibling_bibliography_degrades',
    'test_c4_gate0_probe_run_scope',
    'test_german_anchor_selftest',
    'test_german_anchor_repair_behavioral',
    'test_h3675_target_anchor_selftest',
    'test_h3675_target_anchor_repair_behavioral',
    'test_h_reconstructed_regression_guard',
    'test_h1283_a1_pid_alive_and_dirlock_owner',
    'test_h1420_p2_win32_openprocess_error_leans_alive',
    'test_h1420_p11_record_output_binds_run_id',
    'test_h1420_p10_promote_rebuilds_tm_in_finally',
    'test_h1957_audit_timeout_actually_kills_the_child',
    'test_h1283_a5_max_wide_default_bounded',
    'test_h1283_a6_prep_slice_flattens_batches',
    'test_h1386_d1_medium50_script_size_cap',
    'test_frag_prov_glob_honors_coordinator_dir_c7',
    'test_pwg_mask_german_homograph_not_latin_c8',
    'test_pwg_mask_gloss_lang_g1',
    'test_h2245_canary_manifest_builder',
    'test_h2591_prep_context_compare_matrix',
)
