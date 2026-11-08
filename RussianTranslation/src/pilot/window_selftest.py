"""Smoke tests for frequency-window architecture guardrails.

This script intentionally uses ignored runtime files and temporary directories
only. It does not require a fresh Max run.

The suite is split into pytest-collectable subject modules under `tests/` (H7241);
this file is the legacy entry point and prints the same PASS/FAIL lines.

  python src/pilot/window_selftest.py      # legacy runner
  python -m pytest src/pilot/tests -q      # selectable runner
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_TESTS_DIR = os.path.join(HERE, 'tests')
for _path in (HERE, _TESTS_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# `_support` re-establishes exactly what this file header did before the split:
# the production-isolation guard, the pilot/src paths and the repo imports.
import _support  # noqa: E402,F401
from _support import *  # noqa: E402,F401,F403

from test_workflow_and_harness import *  # noqa: E402,F401,F403
from test_no_pwg_lane import *  # noqa: E402,F401,F403
from test_senses_and_glosses import *  # noqa: E402,F401,F403
from test_audit_and_reporting import *  # noqa: E402,F401,F403
from test_markup_and_language_gates import *  # noqa: E402,F401,F403
from test_coordinator_and_promotion import *  # noqa: E402,F401,F403
from test_prompt_and_policy import *  # noqa: E402,F401,F403
from test_requeue_and_audit_state import *  # noqa: E402,F401,F403
from test_coverage_and_parity import *  # noqa: E402,F401,F403
from test_tm_and_fragments import *  # noqa: E402,F401,F403
from test_budget_and_preflight import *  # noqa: E402,F401,F403


def main():
    tests = [
        test_h4529_width_policy_and_pool_split,
        test_restore_covers_every_promoted_field,
        test_h1339_b21_promoted_pairs_cover_store_write_set,
        test_h1339_b02_stitched_card_schema_complete,
        test_h1339_b03_tm_cards_schema_complete,
        test_h1339_b04_b09_worktree_safe_resolution,
        test_h1339_b10_b19_audit_chain_routing,
        test_h1339_b11_b12_denylist_lifecycle_and_crash_refusal,
        test_h1386_c3_frag_unblock_serves_replacement,
        test_h1386_p3d_p3e_run_py_inproc_exit_semantics,
        test_h1386_p3h_stale_check_pins_v2_execution,
        test_h1339_b13_b15_telemetry_and_siglum_precision,
        test_every_stitch_emits_record_required,
        test_unmapped_token_is_counted,
        test_validator_has_a_live_caller,
        test_strip_mask_tokens_clears_notes_stranded_anchor,
        test_translation_memory_addressing,
        test_tm_pre_resolves_cards,
        test_tm_card_sane_rejects_zero_marker_drift,
        test_en_card_tm_serves_english_field_c3,
        test_generated_harness_strict_key_matching,
        test_tm_auto_no_sidecar_metadata,
        test_suggest_tm_does_not_skip_agents,
        test_tm_publication_fixtures_validate,
        test_degenerate_passthrough_accounted,
        test_degenerate_passthrough_no_german_in_target,
        test_degenerate_passthrough_rejects_glosses,
        test_perf_preflight_small_tm_and_no_tm,
        test_perf_preflight_dense_presplit,
        test_presplit_group_call_weight_caps_portrait_plus_bytes_h2248,
        test_presplit_group_call_weight_zero_allowance_degrades_to_one_per_call_h2248,
        test_perf_preflight_presplit_counts_fragments_not_one,
        test_perf_preflight_degenerate_zero_agent,
        test_perf_preflight_multi_root_matrix_and_order,
        test_perf_preflight_fragment_tm_empty_warning,
        test_perf_preflight_partitions_mixed_monster_window,
        test_verb_worklist_excludes_missing_rootmaps,
        test_coordinator_state_dashboard_and_cap,
        test_coordinator_nominal_reservations,
        test_coordinator_runtime_state_machine_and_cas,
        test_coordinator_fail_closed_audit_states,
        test_coordinator_promotion_revalidates_artifacts,
        test_coordinator_expired_leases_release_cap,
        test_coordinator_lock_replaces_stale_dead_owner,
        test_coordinator_lock_creates_parent_dir,
        test_coordinator_defect_requeue_uses_no_tm_and_out,
        test_transient_requeue_no_tm_flag_h4527,
        test_coordinator_requeue_attempt_manifests,
        test_coordinator_mixed_lane_public_state_sequence,
        test_promote_nominal_key1,
        test_build_emits_nominal_keymap,
        test_generation_schema_carries_no_post_generation_field,
        test_no_pwg_supplement_chain_cards_render,
        test_nominals_worklist_exposes_no_pwg_lane,
        test_no_pwg_source_profile_promotes,
        test_calibration_arm_set_conservative_emit_only,
        test_frag_tm_reuse,
        test_card_tokens_twins_agree,
        test_frag_tm_v2_supersedes_v1,
        test_degenerate_source_identity,
        test_no_fallback_batch_isolation,
        test_cit_split_never_tears_open_span,
        test_sense_split_never_tears_open_span,
        test_cit_split_caps_single_line_monster_sense,
        test_selfheal_fragment_si_threaded_and_tags_normalized,
        test_heal_lane_target_field_fidelity_wired,
        test_autosplit_stitch_topup_rejects_target_field_drop,
        test_autosplit_merge_rejects_target_field_drop,
        test_sense_dense_card_presplit,
        test_kill_gate_wired,
        test_no_fallback_single_gets_ceil_kill_budget,
        test_presplit_cite_floor_and_single_ceil,
        test_default_call_shape_is_one_card_per_call,
        test_large_card_presplit_and_heal_under_one_card_default,
        test_presplit_cite_floor_is_not_masked_by_batch_budget,
        test_nominal_key_echo_tolerance_scoped,
        test_selfheal_no_fallback_preserves_upstream_reason,
        test_group_by_budget_count_cap,
        test_presplit_card_uses_amortized_grouping,
        test_kill_gate_recalibrated_envelope,
        test_agent_budget_plan_separates_translate_and_heal_pools,
        test_split_agent_pools_all_heal_runtime,
        test_lowwide_staggered_dispatch,
        test_budget_kill_switch_wired,
        test_harness_size_guard,
        test_perf_preflight_cost_gate,
        test_launch_failure_ledger_complete,
        test_launch_failure_ledger_rejects_incomplete_entry,
        test_autosplit_topup_targets_and_reassembles,
        test_workflow_payload_nested,
        test_workflow_payload_missing_results_hard_fail,
        test_sense_dupe_norm_strips_trailing_period,
        test_sense_dupe_batch_override,
        test_sense_dupe_cross_level_exempt,
        test_export_translation_dedup,
        test_requeue_transient_vs_defect_state,
        test_harness_scope_and_tools,
        test_stale_check_key_order_independent,
        test_nominal_provenance_without_rootmap,
        test_atomic_control_writes_preserve_previous_file,
        test_no_pwg_residual_registry_and_audit_command,
        test_no_pwg_preparation_advances_past_omitted_chunks,
        test_no_pwg_require_senses_gate,
        test_no_pwg_card_source_profile_taxonomy,
        test_no_pwg_supplement_card_renders_without_pwg,
        test_h920_sense_count_top_level_ordinals,
        test_h920_sense_shortfall_gate_flags_dropped_sense,
        test_h920_no_pwg_portrait_stamps_source_senses,
        test_h920_en_missing_sense_hard_flag,
        test_en_dup_gate_preserves_sanskrit_referent_c2,
        test_h960_accept_sanloss_soft_gate,
        test_tnmask_persist_and_offline_detect,
        test_h960_dropped_sanskrit_span,
        test_no_pwg_worklist_runnable_lane,
        test_h3659_input_sidecars_parked_beside_manifest,
        test_no_pwg_layer_and_profile_survive_promotion,
        test_prompt_rule_audit_template,
        test_prompt_rule_audit_missing_blocks,
        # H3157: `test_mask_preamble_carries_task_shape` was authored with the option-B fix but
        # never added to this list, so the guard that two separate docs describe as "pinning"
        # the TASK SHAPE block had never executed. An unregistered test is indistinguishable
        # from a passing one in every report that matters.
        test_mask_preamble_carries_task_shape,
        test_gloss_wrapper_prompt_preservation_h4270,
        test_health_probe_asks_an_honest_question,
        test_health_probe_carries_no_injection_shape,
        test_semantic_risk_checker,
        test_h1152_guard1_en_polyseme_checklist,
        test_braced_gloss_audit,
        test_german_residue_keeps_retained_markup,
        test_german_connective_fix,
        test_h1302_german_prose_residue_scan,
        test_h1305_ru_style_mechanical,
        test_h1651_wrapper_defect_gate,
        test_h1651_live_gate_cyrillic_and_guillemet,
        test_h1702_boundary_wrap_gate,
        test_h2144_d4b_bracket_normalize,
        test_semantic_review_prioritizer,
        test_noisy_source_type_not_requeue,
        test_report_only_risks_never_requeue,
        test_attested_text_signal_redesign,
        test_nws_fp_suppressed,
        test_en_gate_strict_has_teeth,
        test_en_gate_dup_has_teeth,
        test_run_py_survives_timeout_and_oserror,
        test_ru_gate_fails_loud_on_unparseable_child,
        test_pwg_mask_latin_cue_behind_ab_tag,
        test_markup_loss_soft_flag_ru,
        test_p8_markup_loss_not_masked_by_unrelated_div,
        test_markup_loss_soft_flag_en,
        test_en_de_residue_french_guard,
        test_h1152_guard3_xref_only_and_nws_de_locked,
        test_p7_missing_en_not_fired_on_xref_only_residue,
        test_ru_coverage_denominator_not_silently_exempt,
        test_coverage_gate_multi_layer_and_presplit,
        test_en_residual_coverage_complete,
        test_en_split_triage_keeps_missing_input,
        test_whitney_homonym_safety,
        test_stale_refusal_preserves_requeue,
        test_fixture_audit_does_not_clobber_live_status,
        test_release_manifest_hash_validation,
        test_h3627_structured_output_exhaustion_is_parked_not_window_fatal,
        test_h3627_aborted_window_still_yields_its_paid_cards,
        test_h3627_salvage_never_publishes_an_infra_starved_window,
        test_h4528_no_progress_kill_is_infra_not_a_content_defect,
        test_lang_parity_ledger_complete,
        test_lang_parity_coverage,
        test_card_coverage_lang_symmetric,
        test_degenerate_xref_vocab_single_source,
        test_lang_parity_hash_crlf_independent,
        test_lang_parity_ledger_refuses_duplicate_keys,
        test_lang_parity_ledger_refuses_duplicate_entry_ids,
        test_frag_groups_presplit_parity,
        test_defect_fragment_denylist_round_trip,
        test_opt7_last_audit_tm_refuse_without_no_tm,
        test_write_reports_emits_defect_fsha_file,
        test_ledger_stamps_gen_model,
        test_ledger_stamps_host_profile_b8,
        test_h1553_wall_clock_auto_derive,
        test_h1553_stage_boundary_emit,
        test_save_merge_better_attempt_wins,
        test_defer_monster_ledger_dedupes,
        test_coordinator_cost_gate_enforced,
        test_pwg_mask_bom_source_keeps_first_record,
        test_pwg_mask_truncated_final_record_not_silent,
        test_subprocess_gate_calls_hardened,
        test_ls_resolver_rv_av_anchored,
        test_frag_tm_fidelity_gate_and_override,
        test_corpus_gate_evidence_and_db_markers,
        test_promote_claim_contention,
        test_annotate_evidence_relation_semantics,
        test_annotate_genres_sense_join,
        test_koch_xref_resolution,
        test_fri_xref_resolution,
        test_audit_window_tag_routing,
        test_denylist_torn_line_fails_loud,
        test_per_card_heal_budget_wired,
        test_heal_group_kill_timeout_does_not_bisect,
        test_run_telemetry_counters_returned,
        test_partial_cards_requeue_and_stay_out_of_clean_sample,
        test_h2077_947_infra_partial_is_not_a_content_defect,
        test_h2095_956_en_absence_flags_exempt_infra_partial,
        test_h2095_structured_error_does_not_crash_the_audit,
        test_classify_run_verdicts,
        test_h2173_g5_malformed_result_rows_are_accounted,
        test_h2173_g8_promote_refuses_route_foreign_artifact,
        test_h2173_g10_classify_run_reads_the_live_lane,
        test_h2173_g10_probe_gate_defaults_and_live_boundary,
        test_h2173_g10_declared_budgets_are_read_or_labelled,
        test_grammar_field_restore_behavioral,
        test_threaded_gate_exception_requeues_full_window,
        test_quarantine_replace_failure_preserves_previous_destination,
        test_selftest_isolation_guard,
        test_optional_sibling_bibliography_degrades,
        test_c4_gate0_probe_run_scope,
        test_german_anchor_selftest,
        test_german_anchor_repair_behavioral,
        test_h3675_target_anchor_selftest,
        test_h3675_target_anchor_repair_behavioral,
        test_h_reconstructed_regression_guard,
        test_h1283_a1_pid_alive_and_dirlock_owner,
        test_h1420_p2_win32_openprocess_error_leans_alive,
        test_h1420_p11_record_output_binds_run_id,
        test_h1420_p10_promote_rebuilds_tm_in_finally,
        test_h1957_audit_timeout_actually_kills_the_child,
        test_h1283_a5_max_wide_default_bounded,
        test_h1283_a6_prep_slice_flattens_batches,
        test_h1386_d1_medium50_script_size_cap,
        test_frag_prov_glob_honors_coordinator_dir_c7,
        test_pwg_mask_german_homograph_not_latin_c8,
        test_pwg_mask_gloss_lang_g1,
        test_h2245_canary_manifest_builder,
        test_h2591_prep_context_compare_matrix,
    ]
    # Per-test isolation. This used to be a bare `for test in tests: test()`, so the FIRST
    # failure aborted the process and every later test silently never ran. That is not
    # hypothetical: `test_lang_parity_ledger_complete` sits at position 105 of 131 and is
    # RED BY DESIGN -- the parity verdicts need human reaffirmation, which is deliberately not
    # something an agent does (`--update-hash` is a human's call). So the last 27 tests (20.6%)
    # were dark INDEFINITELY, including `test_frag_groups_presplit_parity`, the whole
    # `pwg_mask` pair and four heal-lane tests. A real regression hiding behind the known-red
    # gate was indistinguishable from the gate itself.
    #
    # This isolates each test and reports ran/defined, so "the suite is green" can no longer
    # mean "the suite stopped early". It does NOT touch the parity gate: that test still fails,
    # loudly, and the run still exits non-zero. It just no longer takes the other 26 with it.
    passed, failed = [], []
    for test in tests:
        try:
            test()
        except BaseException as exc:      # noqa: BLE001 -- a failing test must not hide the rest
            failed.append(test.__name__)
            print('FAIL: %s -- %s: %s' % (test.__name__, exc.__class__.__name__, exc))
        else:
            passed.append(test.__name__)
            print('PASS:', test.__name__)

    ran = len(passed) + len(failed)
    print('window selftest: ran %d/%d defined -- %d passed, %d failed'
          % (ran, len(tests), len(passed), len(failed)))
    if ran != len(tests):
        # Unreachable while every test is isolated; kept so that a future early-exit (an
        # os._exit, a signal) is reported as darkness rather than read as success.
        print('DARK: %d test(s) defined but never ran' % (len(tests) - ran))
    if failed:
        print('FAILED (%d): %s' % (len(failed), ', '.join(failed)))
        return 1
    print('window selftest OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
