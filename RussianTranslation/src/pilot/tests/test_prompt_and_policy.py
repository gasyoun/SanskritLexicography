"""test_prompt_and_policy — split from window_selftest.py by H7241.

Pytest-collectable subject module of the frequency-window guardrail suite. The test bodies
are the original ones, moved verbatim; `_support.py` carries the fixtures, the
production-isolation guard and the `HERE`/`SRC`/`ROOT` paths they resolve against.

Run:  python -m pytest src/pilot/tests/test_prompt_and_policy.py -q
      python src/pilot/window_selftest.py       # legacy runner, same result
"""

from _support import *  # noqa: F401,F403  -- fixtures, paths, repo imports


def test_prompt_rule_audit_template():
    report = build_report([DEFAULT_TEMPLATE])
    if report.get('missing_rule_count'):
        missing = []
        for target in report['targets']:
            for rule in target.get('missing') or []:
                missing.append('%s:%s' % (os.path.basename(target['path']), rule['id']))
        fail('prompt-rule audit missing required rules: %s' % ', '.join(missing))
    coverage = set(report.get('live_manual_coverage') or [])
    expected = {'Apresjan', 'Hartmann', 'Gonda/Vogel', 'Tubb',
                'Baalbaki', 'Apte/Gillon/Inglese-Geupel',
                'Mitrenina/Zaliznyak-Paducheva/Ruppel'}
    if not expected.issubset(coverage):
        fail('prompt-rule audit missing manual coverage labels: %s' %
             ', '.join(sorted(expected - coverage)))



def test_mask_preamble_carries_task_shape():
    """H3144 / FINDINGS §498: the generation prompt must keep its TASK SHAPE block.

    The production spawn passes `--permission-mode plan` alongside `--json-schema`. Without
    this block the model refuses to emit structured output on plan-mode grounds, the CLI
    returns rc 0 with no `structured_output`, and the harness misreports the paid call as
    `malformed_output` (19-08-2026, c1 canary). MG ruled option B — keep plan mode, fix the
    prompt — so the block IS the fix and nothing else guards it.

    Asserted on the shared source, which feeds BOTH the manifest-v2 preamble and the
    generated JS harness, so one check covers both lanes.
    """
    from gen_opt_harness2 import MASK_PREAMBLE as preamble

    if not preamble.startswith('=== TASK SHAPE (read first) ==='):
        fail('MASK_PREAMBLE must OPEN with the TASK SHAPE block (the model reads first, '
             'and refuses before reaching a later block): %r' % preamble[:80])

    # Each clause answers one of the three objections the model actually raised.
    required = [
        ('read-only', 'plan mode restricts to read-only actions'),
        ('single turn', 'plan mode wants the turn ended by question/approval'),
        ('no planning step, clarifying question, or approval round',
         'AskUserQuestion/ExitPlanMode do not exist in a headless -p session'),
    ]
    for needle, why in required:
        if needle not in preamble:
            fail('MASK_PREAMBLE lost the %r clause (%s) — the next paid window will refuse '
                 'and be misfiled as malformed_output' % (needle, why))

    # The refusal was triggered by a bare tool-demand, and the CLI's own retry proved that
    # shape cannot win. Never reintroduce it here.
    for banned in ('You MUST call', 'call this tool now', 'ignore plan mode', 'exit plan mode'):
        if banned.lower() in preamble.lower():
            fail('MASK_PREAMBLE must not demand the tool call or claim to lift plan mode '
                 '(%r) — that is the exact shape the model refused twice' % banned)



def test_health_probe_asks_an_honest_question():
    """H4527 (15-09-2026) — H4213 §6.3 option (b): the readiness probe asks ONE honest question
    whose true answer is `{"ok": true}`, over reference text that makes it true.

    Supersedes the H3157 (a) prepend of the production TASK SHAPE block and the H4277 provenance
    bridge. With both in place the probe kept answering `{"ok": false}` on healthy routes — four
    refusals against two passes between 10-09 and 15-09, the last two WITH the lane's
    `--safe-mode`, which rules the profile surface out. The 15-09 14:27Z transcript names the
    reason in the model's own words: an embedded "READINESS CHECK" block claiming shared
    authority, over-justifying itself as "not a bypass", an "ignore this" sample block, and a card
    task with no cards — "the shape of a prompt injection". The model was right.

    What H3157 wanted the probe to detect is detected upstream on the cohort-acceptance route:
    `bounded_staged_run --execute --only-profile <p>` runs `canary_gate.enforce` (production
    preamble + a real synthetic card, same profile, <= 6 h) before `probe_fleet`. It is NOT
    covered on `max_account_orchestrator staged-run`, which has no canary, nor under
    `--skip-canary-gate` / a multi-profile run on one receipt — routed to Uprava H4916 (see
    `_probe_prompt`'s docstring). The probe keeps its spawn shape, ceilings and payload size, and
    `{"ok": true}` stays the only passing answer; only the text it reasons about is now a
    question with a true answer instead of an order dressed as a task.
    """
    import max_account_orchestrator as mao

    prompt = mao._probe_prompt(6491)

    if not prompt.startswith(mao._PROBE_QUESTION):
        fail('the probe prompt must OPEN with the readiness question — nothing may be prepended '
             'to it (H4527: the prepended production block read as the injection frame)')
    if '"ok" is true if the text mentions it' not in prompt:
        fail('the readiness question no longer maps its true answer onto the schema field')
    head, sep, reference = prompt.partition('--- reference text ---')
    if not sep:
        fail('the probe lost the reference-text marker between the question and its text')
    # The answer must actually BE true: the reference text names what the question asks about.
    if 'Petersburg Sanskrit dictionary' not in reference:
        fail('the reference text no longer contains what the question asks about — the '
             'correct answer would be false and every reading a NO-GO')
    # Payload parity with every production_v4 reading (preamble 2 896 + bridge 1 342 + 6 491
    # filler = 10 729 B): the probe must not become cheaper to pass than the series its
    # ceilings were read from.
    if len(prompt.encode('utf-8')) < 10729:
        fail('probe prompt fell below the 10 729-byte production_v4 size (%d B)'
             % len(prompt.encode('utf-8')))



def test_health_probe_carries_no_injection_shape():
    """H4527 (15-09-2026): pin the ABSENCE of every feature the refusing calls named.

    The 07-09 and 15-09 transcripts list them: a block claiming the same issuer as the text
    above it, a card task that declares zero cards, an order to return one fixed string and
    "nothing else", a pre-emptive "not a bypass", an "ignore"/"inert" sample block, and the
    production TASK SHAPE block promising cards that never arrive. A later "hardening" that
    re-adds any of them re-introduces the false NO-GO loudly and offline, not at ~$0.07 and one
    of two rationed daily readings per profile.
    """
    import max_account_orchestrator as mao

    prompt = mao._probe_prompt(6491)
    for banned in ('SAME ISSUER', 'ZERO cards', 'nothing else', 'bypass', 'inert sample',
                   'ignore', 'do not analyse', 'TASK SHAPE', '=== CARD', 'READINESS CHECK'):
        if banned in prompt:
            fail('the probe prompt carries %r again — a feature the refusing call named as the '
                 'prompt-injection signature (H4527, 15-09-2026 transcript)' % banned)
    for gone in ('_PROBE_PROVENANCE_BRIDGE', '_production_task_shape_preamble'):
        if hasattr(mao, gone):
            fail('%s is back in max_account_orchestrator — H4527 retired it' % gone)



def test_prompt_rule_audit_missing_blocks():
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.js', delete=False) as f:
        path = f.name
        f.write('const CHECKS = "Apresjan only";\n')
    try:
        report = build_report([path])
        if not report.get('missing_rule_count'):
            fail('prompt-rule missing fixture did not report missing rules')
    finally:
        os.remove(path)

