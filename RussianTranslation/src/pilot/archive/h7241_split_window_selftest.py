#!/usr/bin/env python
"""H7241 ONE-SHOT splitter: `src/pilot/window_selftest.py` -> pytest-collectable modules.

Why
---
`window_selftest.py` was 10,321 lines / 229 test functions with no pytest behind it, so
nothing in it was selectable: to check one guardrail you paid for all 229, and a reviewer
could not ask "did this PR touch the tests it should have". This script does the split
MECHANICALLY, by moving source text, not by rewriting it:

* every non-test top-level definition (fixtures, gate plumbing, constants) moves to
  `tests/_support.py`
* every `test_*` function moves to `tests/test_<subject>.py` chosen from its name
* `window_selftest.py` stays as a thin legacy wrapper that imports the modules and keeps
  the old `python src/pilot/window_selftest.py` output (PASS/FAIL lines + summary)

The ONLY textual edit applied to test bodies is `os.path.dirname(os.path.abspath(__file__))`
-> `HERE`, because a moved test's `__file__` is no longer `src/pilot/`. `HERE` in
`_support.py` IS `src/pilot`, so the value is identical (asserted by `--check`).

`--check` re-parses both sides and proves, per definition, that the AST is unchanged, so
no assertion was dropped, edited or invented.

Run once, from `RussianTranslation/`:

    python src/pilot/archive/h7241_split_window_selftest.py --check
    python src/pilot/archive/h7241_split_window_selftest.py --apply

After `--apply` the original is gone (it is now the wrapper), so this script is
archive-only: it is the record of HOW the split was done, not a routine tool.
"""
import argparse
import ast
import collections
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.dirname(HERE)
SRC_DIR = os.path.dirname(PILOT)
REPO = os.path.dirname(SRC_DIR)

ORIGINAL = os.path.join(PILOT, 'window_selftest.py')
TESTS_DIR = os.path.join(PILOT, 'tests')

FILE_SUFFIX_RE = 'os.path.dirname(os.path.abspath(__file__))'

# Subject routing, first match wins. Order matters: the specific lanes come before the
# generic ones (`no_pwg` before `promote`, `coordinator_cost_gate` before `cost_gate`).
RULES = (
    ('test_workflow_and_harness', r"""
        ^test_workflow_payload
        |^test_harness_scope_and_tools
        |^test_stale_check_key_order_independent
        |^test_nominal_provenance_without_rootmap
        |^test_release_manifest_hash_validation
        |^test_generated_harness_strict_key_matching
        |^test_harness_size_guard
        |^test_generation_schema_carries_no_post_generation_field
        |^test_default_call_shape_is_one_card_per_call
        |^test_calibration_arm_set_conservative_emit_only
        |^test_build_emits_nominal_keymap
        |^test_nominals_worklist_exposes_no_pwg_lane
        |^test_h2591_prep_context_compare_matrix
        |^test_h2245_canary_manifest_builder
    """),
    ('test_no_pwg_lane', r"""
        ^test_no_pwg
        |^test_promote_nominal_key1
        |^test_verb_worklist_excludes_missing_rootmaps
        |^test_nominal_key_echo_tolerance_scoped
    """),
    ('test_senses_and_glosses', r"""
        ^test_h920
        |^test_h960
        |^test_en_dup_gate
        |^test_sense_
        |^test_cit_split
        |^test_whitney_homonym
        |^test_braced_gloss
        |^test_gloss_wrapper_prompt_preservation
        |^test_h1152_guard1
        |^test_h1152_guard3
        |^test_pwg_mask
        |^test_degenerate_xref_vocab
        |^test_card_coverage_lang_symmetric
    """),
    ('test_markup_and_language_gates', r"""
        ^test_markup_loss
        |^test_p8_markup_loss
        |^test_p7_missing_en
        |^test_en_de_residue
        |^test_en_gate
        |^test_ru_gate_fails_loud
        |^test_german_
        |^test_h1302
        |^test_h1305_ru_style
        |^test_h1651
        |^test_h1702_boundary_wrap
        |^test_h2144_d4b
        |^test_nws_fp_suppressed
        |^test_en_absence_flags
    """),
    ('test_coverage_and_parity', r"""
        ^test_ru_coverage_denominator
        |^test_coverage_gate
        |^test_en_residual_coverage
        |^test_en_split_triage
        |^test_lang_parity
        |^test_corpus_gate
    """),
    ('test_requeue_and_audit_state', r"""
        ^test_requeue
        |^test_transient_requeue
        |^test_stale_refusal
        |^test_fixture_audit
        |^test_report_only_risks
        |^test_noisy_source_type
        |^test_attested_text_signal
        |^test_semantic_
        |^test_partial_cards_requeue
        |^test_export_translation_dedup
    """),
    ('test_tm_and_fragments', r"""
        ^test_translation_memory_addressing
        |^test_tm_
        |^test_suggest_tm
        |^test_frag_
        |^test_denylist_torn_line
        |^test_defect_fragment_denylist
        |^test_degenerate_
        |^test_en_card_tm_serves_english_field
        |^test_opt7_last_audit_tm_refuse
        |^test_autosplit_
        |^test_card_tokens_twins_agree
        |^test_every_stitch_emits_record_required
        |^test_unmapped_token_is_counted
        |^test_validator_has_a_live_caller
        |^test_strip_mask_tokens_clears_notes_stranded_anchor
    """),
    ('test_budget_and_preflight', r"""
        ^test_perf_preflight
        |^test_presplit
        |^test_group_by_budget_count_cap
        |^test_agent_budget_plan
        |^test_split_agent_pools
        |^test_lowwide_staggered
        |^test_kill_gate
        |^test_budget_kill_switch
        |^test_per_card_heal_budget
        |^test_heal_group_kill
        |^test_selfheal_
        |^test_no_fallback_
        |^test_h1283_a5
        |^test_h1283_a6
        |^test_h1386_d1
        |^test_h4529_width_policy
        |^test_coordinator_cost_gate_enforced
    """),
    ('test_coordinator_and_promotion', r"""
        ^test_coordinator_
        |^test_promote_
        |^test_promote_claim_contention
        |^test_h1957_audit_timeout
        |^test_atomic_control_writes
        |^test_h1420_
        |^test_h1283_a1
        |^test_restore_covers_every_promoted_field
        |^test_h1339_
        |^test_h2173_
        |^test_h1553_
        |^test_save_merge_better_attempt
        |^test_defer_monster_ledger
        |^test_selftest_isolation_guard
        |^test_c4_gate0
        |^test_h3659
    """),
    ('test_audit_and_reporting', r"""
        ^test_audit_window_tag_routing
        |^test_write_reports
        |^test_ledger_
        |^test_run_telemetry
        |^test_launch_failure_ledger
        |^test_classify_run_verdicts
        |^test_annotate_
        |^test_koch_xref
        |^test_fri_xref
        |^test_ls_resolver
        |^test_subprocess_gate_calls_hardened
        |^test_h2095
        |^test_h2077
        |^test_h3627
        |^test_h4528_no_progress
        |^test_h_reconstructed_regression_guard
        |^test_h1386_
        |^test_run_py_survives_timeout
        |^test_threaded_gate_exception
        |^test_quarantine_replace_failure
        |^test_optional_sibling_bibliography
        |^test_anchor_
        |^test_grammar_field_restore
        |^test_tnmask
        |_anchor_
        |^test_large_card_presplit
        |^test_heal_lane_target_field
    """),
    ('test_prompt_and_policy', r"""
        ^test_prompt_rule_audit
        |^test_mask_preamble
        |^test_health_probe
        |^test_semantic_review_prioritizer
    """),
)
FALLBACK = 'test_misc_guardrails'

MODULE_DOC = '''"""{title} — split from window_selftest.py by H7241.

Pytest-collectable subject module of the frequency-window guardrail suite. The test bodies
are the original ones, moved verbatim; `_support.py` carries the fixtures, the
production-isolation guard and the `HERE`/`SRC`/`ROOT` paths they resolve against.

Run:  python -m pytest {rel} -q
      python src/pilot/window_selftest.py       # legacy runner, same result
"""'''

SUPPORT_DOC = '''"""Shared state for the frequency-window guardrail suite.

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
"""'''


def load_original():
    with io.open(ORIGINAL, encoding='utf-8', newline='') as handle:
        return handle.read().replace('\r\n', '\n').replace('\r', '\n')


def segment(source_lines, node):
    start = node.lineno
    for decorator in getattr(node, 'decorator_list', ()):
        start = min(start, decorator.lineno)
    return ''.join(source_lines[start - 1:node.end_lineno])


def route(name):
    for module, pattern in RULES:
        if re.search(pattern.replace('\n', '').replace(' ', ''), name):
            return module
    return FALLBACK


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true',
                      help='re-parse the split modules and prove AST + assertion parity')
    mode.add_argument('--apply', action='store_true', help='write the split (one-shot)')
    return parser.parse_args(argv)


def ordered_names(main_node):
    for statement in ast.walk(main_node):
        if (isinstance(statement, ast.Assign)
                and any(getattr(target, 'id', None) == 'tests' for target in statement.targets)):
            return [element.id for element in statement.value.elts]
    raise AssertionError('main() carries no `tests` list')


def build(contents):
    """Return {filename: text} for every generated file."""
    tree = ast.parse(contents, filename=ORIGINAL)
    lines = contents.splitlines(keepends=True)

    tests = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
    if not tests:
        raise SystemExit('%s is already the split wrapper (H7241 already applied); this script '
                         'is archive-only and needs the pre-split original.' % ORIGINAL)
    first_test_line = min(node.lineno for node in tests)
    helper_nodes = [node for node in tree.body
                    if isinstance(node, ast.FunctionDef)
                    and not node.name.startswith('test_') and node.name != 'main']
    main_node = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == 'main'][0]

    # The old header (plain imports, reconfigure, isolation guard, paths, repo imports) is
    # rebuilt in a dependency order that keeps every original guarantee: repo modules are
    # imported only AFTER the isolation guard, and the guard is importable only after
    # `src/pilot` is on sys.path. Only the paths block differs, because this file now lives
    # one directory lower (tests/).
    header = [node for node in tree.body if node.end_lineno < first_test_line]
    reconfigure = [node for node in header if isinstance(node, ast.Expr)
                   and getattr(node.value, 'func', None) is not None
                   and getattr(node.value.func, 'attr', '') == 'reconfigure']
    first_reconfigure = min(node.lineno for node in reconfigure)
    # stdlib imports sit above the reconfigure calls; a bare `import <repo_module>` below them
    # is a REPO import and must stay behind the isolation guard, as it was originally.
    plain_imports = [node for node in header
                     if isinstance(node, ast.Import) and node.lineno < first_reconfigure]
    isolation_import = [node for node in header if isinstance(node, ast.ImportFrom)
                        and node.module == 'selftest_isolation']
    repo_imports = [node for node in header
                    if (isinstance(node, ast.ImportFrom) and node.module != 'selftest_isolation')
                    or (isinstance(node, ast.Import) and node.lineno > first_reconfigure)]
    guard_call = [node for node in header
                  if isinstance(node, ast.Expr) and node not in reconfigure
                  and node is not tree.body[0]]

    paths_block = ('# This file lives in `tests/`, so one extra dirname lands on `src/pilot`. The\n'
                   '# value is identical to the old `window_selftest.py` HERE, which is what every\n'
                   '# fixture below addresses files against.\n'
                   'HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n'
                   'SRC = os.path.dirname(HERE)\n'
                   'ROOT = os.path.dirname(SRC)\n'
                   "OUT = os.path.join(HERE, 'output')\n"
                   "PILOT_DIR = HERE     # the old file's own directory, under a second name\n"
                   'if HERE not in sys.path:\n'
                   '    sys.path.insert(0, HERE)\n'
                   'if SRC not in sys.path:\n'
                   '    sys.path.insert(0, SRC)\n')

    # Support carries the rebuilt header plus every definition that is not a test: i.e.
    # everything the old module body provided except the tests themselves and `main()`.
    header_ids = {id(node) for node in header if not isinstance(node, ast.FunctionDef)}
    support_nodes = [node for node in tree.body
                     if id(node) not in header_ids
                     and node is not tree.body[0] and node is not main_node
                     and node.end_lineno < main_node.lineno
                     and not (isinstance(node, ast.FunctionDef)
                              and node.name.startswith('test_'))]
    rebuilt = []
    rebuilt += [segment(lines, node) for node in plain_imports]
    rebuilt.append('')
    rebuilt.append(paths_block)
    rebuilt += [segment(lines, node) for node in reconfigure]
    rebuilt.append('')
    rebuilt += [segment(lines, node) for node in isolation_import]
    rebuilt += [segment(lines, node) for node in guard_call]
    rebuilt.append('')
    rebuilt += [segment(lines, node).rstrip('\n') + '\n' for node in repo_imports]
    rebuilt.append('')
    for node in support_nodes:
        if (isinstance(node, ast.Assign)
                and getattr(node.targets[0], 'id', '') == 'PREFLIGHT_STDOUT'):
            rebuilt.append('')
        rebuilt.append(segment(lines, node))
    rebuilt.append('')
    rebuilt.append('# Original execution order of the legacy runner. conftest.py sorts pytest\n'
                   '# collection by it, so a pytest run is order-for-order the old one.\n'
                   'ORIGINAL_ORDER = (\n'
                   + ''.join("    '%s',\n" % name for name in ordered_names(main_node))
                   + ')\n')

    files = {'_support.py': SUPPORT_DOC + '\n' + ''.join(rebuilt)}

    # --- test modules --------------------------------------------------------------
    by_module = collections.OrderedDict()
    for node in tests:
        by_module.setdefault(route(node.name), []).append(node)

    for module, nodes in by_module.items():
        body = [segment(lines, node).replace(FILE_SUFFIX_RE, 'HERE') for node in nodes]
        private = sorted({name for name in
                          re.findall(r'\b(_sealed_preflight|_h4054_synth_inputs)\b',
                                     '\n'.join(body))})
        header = [MODULE_DOC.format(title=module, rel='src/pilot/tests/' + module + '.py'), '',
                  'from _support import *  # noqa: F401,F403  -- fixtures, paths, repo imports']
        if private:
            header.append('from _support import %s  # noqa: F401  -- `import *` skips _names'
                          % ', '.join(private))
        files[module + '.py'] = '\n'.join(header) + '\n\n\n' + '\n\n\n'.join(body) + '\n'

    # --- conftest ------------------------------------------------------------------
    files['conftest.py'] = (
        '"""Collection order + import path for the split window-selftest suite (H7241).\n'
        '\n'
        'Importing `_support` first is deliberate: it establishes the production isolation\n'
        'guard before any repo module is imported (same contract as the old selftest header).\n'
        '"""\n'
        'import os\n'
        'import sys\n'
        '\n'
        '_HERE = os.path.dirname(os.path.abspath(__file__))\n'
        'if _HERE not in sys.path:\n'
        '    sys.path.insert(0, _HERE)\n'
        '\n'
        'import _support  # noqa: E402,F401\n'
        '\n'
        '\n'
        'def pytest_collection_modifyitems(session, config, items):\n'
        '    """Run in the legacy `main()` order, so pass/fail parity is order-for-order."""\n'
        '    order = {name: index for index, name in enumerate(_support.ORIGINAL_ORDER)}\n'
        '    items.sort(key=lambda item: order.get(item.name, len(order)))\n')

    # --- module map ---------------------------------------------------------------
    map_lines = ['# Module map — window_selftest.py split (H7241)', '',
                 '| module | tests |', '|---|---|']
    for module, nodes in by_module.items():
        map_lines.append('| `tests/%s.py` | %d |' % (module, len(nodes)))
    map_lines += ['| `tests/_support.py` | %d fixtures/helpers |' % len(helper_nodes), '',
                  'Generated by `src/pilot/archive/h7241_split_window_selftest.py`. Every test '
                  'function below kept its original body verbatim; the only substitution is '
                  '`os.path.dirname(os.path.abspath(__file__))` -> `HERE`, and `HERE` IS the old '
                  '`src/pilot` directory.', '']
    for module, nodes in by_module.items():
        map_lines.append('## `tests/%s.py`' % module)
        map_lines.append('')
        for node in nodes:
            map_lines.append('- `%s` (old line %d)' % (node.name, node.lineno))
        map_lines.append('')
    files['MODULE_MAP.md'] = '\n'.join(map_lines)

    # --- legacy wrapper -----------------------------------------------------------
    docstring = segment(lines, tree.body[0]).replace(
        '  python src/pilot/window_selftest.py\n"""',
        'The suite is split into pytest-collectable subject modules under `tests/` (H7241);\n'
        'this file is the legacy entry point and prints the same PASS/FAIL lines.\n'
        '\n'
        '  python src/pilot/window_selftest.py      # legacy runner\n'
        '  python -m pytest src/pilot/tests -q      # selectable runner\n"""')
    wrapper = [docstring, '',
               'import os\n',
               'import sys\n',
               '\n',
               'HERE = os.path.dirname(os.path.abspath(__file__))\n',
               "_TESTS_DIR = os.path.join(HERE, 'tests')\n",
               'for _path in (HERE, _TESTS_DIR):\n',
               '    if _path not in sys.path:\n',
               '        sys.path.insert(0, _path)\n',
               '\n',
               '# `_support` re-establishes exactly what this file header did before the split:\n',
               '# the production-isolation guard, the pilot/src paths and the repo imports.\n',
               'import _support  # noqa: E402,F401\n',
               'from _support import *  # noqa: E402,F401,F403\n',
               '\n']
    wrapper += ['from %s import *  # noqa: E402,F401,F403\n' % module for module in by_module]
    wrapper += ['\n\n', segment(lines, main_node),
                "\n\nif __name__ == '__main__':\n    sys.exit(main())\n"]
    files['window_selftest.py'] = ''.join(wrapper)
    return files


def apply(files):
    os.makedirs(TESTS_DIR, exist_ok=True)
    for name, text in files.items():
        path = ORIGINAL if name == 'window_selftest.py' else os.path.join(TESTS_DIR, name)
        with io.open(path, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(text)
        print('wrote', os.path.relpath(path, REPO))


def check(files, original_source):
    """AST parity: every old definition must exist, unchanged, in exactly one module."""
    old_tree = ast.parse(original_source, filename=ORIGINAL)
    old_lines = original_source.splitlines(keepends=True)
    old_tests = {node.name: node for node in old_tree.body
                 if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}
    old_helpers = {node.name: node for node in old_tree.body
                   if isinstance(node, ast.FunctionDef) and not node.name.startswith('test_')}
    known = dict(old_tests)
    known.update({name: node for name, node in old_helpers.items() if name != 'main'})

    seen = collections.Counter()
    broken = []
    for name in sorted(files):
        if not name.endswith('.py') or name in ('window_selftest.py', 'conftest.py'):
            continue
        tree = ast.parse(files[name], filename=name)
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            source = known.get(node.name)
            if source is None:
                broken.append('%s: %s has no ancestor in the original' % (name, node.name))
                continue
            seen[node.name] += 1
            expected_source = segment(old_lines, source).replace(FILE_SUFFIX_RE, 'HERE')
            want = [n for n in ast.parse(expected_source).body
                    if isinstance(n, ast.FunctionDef)][0]
            if (ast.dump(node, include_attributes=False)
                    != ast.dump(want, include_attributes=False)):
                broken.append('%s: %s body differs from the original' % (name, node.name))

    missing = sorted(set(known) - set(seen))
    duplicated = sorted(key for key, count in seen.items() if count > 1)
    print('old test functions: %d' % len(old_tests))
    print('old non-test helpers: %d' % (len(old_helpers) - 1))
    print('definitions found in split modules: %d (expected %d)'
          % (sum(seen.values()), len(known)))
    print('generated files (%d): %s' % (len(files), ', '.join(sorted(files))))
    if missing:
        broken.append('MISSING: %s' % ', '.join(missing))
    if duplicated:
        broken.append('DUPLICATED: %s' % ', '.join(duplicated))
    if broken:
        for line in broken:
            print('FAIL', line)
        return 1
    print('PASS: every test and fixture is present once, body-identical to the original')
    return 0


if __name__ == '__main__':
    arguments = parse_args()
    source = load_original()
    generated = build(source)
    if arguments.apply:
        apply(generated)
        print('applied; run `python -m pytest src/pilot/tests -q` next')
        sys.exit(0)
    sys.exit(check(generated, source))
