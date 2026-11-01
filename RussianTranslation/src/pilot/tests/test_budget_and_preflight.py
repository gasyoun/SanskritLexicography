"""test_budget_and_preflight — split from window_selftest.py by H7241.

Pytest-collectable subject module of the frequency-window guardrail suite. The test bodies
are the original ones, moved verbatim; `_support.py` carries the fixtures, the
production-isolation guard and the `HERE`/`SRC`/`ROOT` paths they resolve against.

Run:  python -m pytest src/pilot/tests/test_budget_and_preflight.py -q
      python src/pilot/window_selftest.py       # legacy runner, same result
"""

from _support import *  # noqa: F401,F403  -- fixtures, paths, repo imports


def test_perf_preflight_small_tm_and_no_tm():
    key = 'gam~~h0_03_sec_3'
    with gam_pilot_fixture():
        proc = run([sys.executable, 'src/pilot/perf_preflight.py', 'gam',
                    '--keys=%s' % key, '--json'], 0)
    report = json.loads(proc.stdout)
    if report['selected_keys'] != [key]:
        fail('perf_preflight must preserve the requested fixed key set')
    if report.get('schema') != 'pwg.performance_preflight.v1' or 'reports' in report:
        fail('single-root perf_preflight JSON must remain the plain v1 report shape')
    if 'tm_available' not in report or 'agent_expected_after_tm' not in report:
        fail('perf_preflight JSON missing TM/agent accounting fields')
    with gam_pilot_fixture():
        proc2 = run([sys.executable, 'src/pilot/perf_preflight.py', 'gam',
                     '--keys=%s' % key, '--no-tm', '--json'], 0)
    no_tm = json.loads(proc2.stdout)
    if no_tm['tm_auto'] or no_tm['tm_cards'] != 0:
        fail('--no-tm preflight must disable TM accounting')
    if no_tm['batch_count'] < 1 or no_tm['agent_expected_after_tm'] < 1:
        fail('small no-TM card should still be owed by a normal agent lane')



def test_perf_preflight_dense_presplit():
    key = 'gam~~h0_00_pwg00'
    with gam_pilot_fixture():
        proc = run([sys.executable, 'src/pilot/perf_preflight.py', 'gam',
                    '--keys=%s' % key, '--no-tm', '--json'], 0)
    report = json.loads(proc.stdout)
    if key not in report.get('presplit_keys', []):
        fail('dense key must report presplit routing in performance preflight')
    if report.get('agent_expected_after_tm', 0) < 1:
        fail('dense presplit key must report a nonzero expected agent lane')



def test_presplit_group_call_weight_caps_portrait_plus_bytes_h2248():
    """H2248 (#983): a presplit group's CALL WEIGHT — the card's portrait plus the group's
    fragment bytes — must stay within PRESPLIT_GROUP_CALL_WEIGHT.

    RED before the fix: the presplit sizer weighed only `1 + <ls>` (citation units) with a
    fragment count cap, and was blind to the portrait that `heal_group` re-sends on EVERY
    fragment call. On H2174's live w1 that hid 68-94% of each call's real weight, and packed
    `nakzatra`'s 3 236 B / citation-light mega-fragment into a group whose true weight was
    14 378 B — the heaviest call of the window, and the only one that died at the ceiling
    (300 024 ms). Every call that landed weighed <= 11 476 B.

    The fixture reproduces exactly that shape: a big portrait plus a byte-heavy but
    citation-light fragment that the citation sizer prices at almost nothing. Under the old
    grouping every fragment fits in one group (total cite weight is far under 60 and the
    count is under 18), so the group's weight lands ~14 KB and this test FAILS.
    """
    import gen_opt_harness2 as gh

    portrait = 'E' * 9761                      # nakzatra's real portrait size
    frags = ([{'skeleton': 'x' * n, 'ls': 1} for n in (73, 230, 212, 83)]
             + [{'skeleton': 'x' * n, 'ls': 1} for n in (335, 103, 672, 131, 140)]
             + [{'skeleton': 'x' * 3236, 'ls': 1}])   # the citation-light mega-fragment
    allow = max(0, gh.PRESPLIT_GROUP_CALL_WEIGHT - len(portrait))
    groups = gh._group_by_budget(frags, lambda it: 1 + it['ls'],
                                 gh.PRESPLIT_GROUP_CITE_BUDGET,
                                 count_cap=gh.PRESPLIT_GROUP_SENSE_CAP,
                                 extra_sizer=lambda it: len(it['skeleton']),
                                 extra_budget=allow)
    if not groups:
        fail('presplit grouping returned no groups')
    for gi, grp in enumerate(groups, 1):
        content = sum(len(it['skeleton']) for it in grp)
        weight = len(portrait) + content
        # A group holding ONE fragment is already the smallest call the lane can make;
        # an intrinsically oversize fragment is allowed to exceed (never dropped).
        if len(grp) > 1 and weight > gh.PRESPLIT_GROUP_CALL_WEIGHT:
            fail('presplit group #g%d weighs %d B (portrait %d + content %d), over the '
                 '%d B call-weight cap — the H2174 nakzatra#g2 shape (14 378 B) that died '
                 'at the kill ceiling' % (gi, weight, len(portrait), content,
                                          gh.PRESPLIT_GROUP_CALL_WEIGHT))
    # The mega-fragment must be isolated rather than packed beside its siblings.
    mega = [gi for gi, grp in enumerate(groups, 1)
            if any(len(it['skeleton']) == 3236 for it in grp)]
    if len(mega) != 1 or len(groups[mega[0] - 1]) != 1:
        fail('the 3 236 B citation-light fragment must get its own call, not ride along '
             'with siblings the citation sizer priced identically')



def test_presplit_group_call_weight_zero_allowance_degrades_to_one_per_call_h2248():
    """A card whose portrait ALONE exceeds the call-weight cap gets a 0 B content allowance.
    That must degrade to one fragment per call (the smallest call the lane can make), not
    silently read as "no cap" — the `if extra_budget` truthiness bug this guards against
    would have let exactly the largest-portrait cards regroup without any byte bound."""
    import gen_opt_harness2 as gh

    frags = [{'skeleton': 'x' * n, 'ls': 1} for n in (100, 200, 300)]
    groups = gh._group_by_budget(frags, lambda it: 1 + it['ls'], 60, count_cap=18,
                                 extra_sizer=lambda it: len(it['skeleton']),
                                 extra_budget=0)
    if [len(g) for g in groups] != [1, 1, 1]:
        fail('a 0 B content allowance must yield one fragment per call, got %r'
             % [len(g) for g in groups])



def test_perf_preflight_presplit_counts_fragments_not_one():
    """agent_expected_after_tm for a presplit giant must be its true fragment-GROUP count,
    not 1 — the old len(presplit) formula underestimated vid's real 102-agent run as 13.
    H189: the group count is now LOWER than the pre-H189 per-12-citation grouping (the
    presplit lane amortizes at PRESPLIT_GROUP_CITE_BUDGET=60), but it must still be >1 (a
    150+-<ls> giant does not collapse to a single call) — that's the invariant this guards."""
    key = 'gam~~h0_00_pwg00'
    with gam_pilot_fixture():
        proc = run([sys.executable, 'src/pilot/perf_preflight.py', 'gam',
                    '--keys=%s' % key, '--no-tm', '--json'], 0)
    report = json.loads(proc.stdout)
    if key not in report.get('presplit_keys', []):
        fail('fixture card must still route to presplit')
    if report.get('agent_expected_after_tm', 0) < 2:
        fail('a 150+-<ls> presplit giant needs several fragment-group calls, not ~1 — '
             'got agent_expected_after_tm=%r' % report.get('agent_expected_after_tm'))



def test_perf_preflight_degenerate_zero_agent():
    with gam_pilot_fixture():
        proc = run([sys.executable, 'src/pilot/perf_preflight.py', 'ab',
                    '--nominal', '--keys=ab', '--json'], 0)
    report = json.loads(proc.stdout)
    if report.get('degenerate_passthrough_keys') != ['ab']:
        fail('ab must report degenerate pass-through in performance preflight')
    if report.get('agent_expected_after_tm') != 0:
        fail('degenerate pass-through should report zero expected agents')



def test_perf_preflight_multi_root_matrix_and_order():
    with matrix_pilot_fixture() as tm_sidecar:
        proc = run([sys.executable, 'src/pilot/perf_preflight.py',
                    'gam', 'han', 'as', 'vid', '--tm=%s' % tm_sidecar, '--json'], 0)
    matrix = json.loads(proc.stdout)
    if matrix.get('schema') != 'pwg.performance_preflight.matrix.v1':
        fail('multi-root perf_preflight JSON must use the matrix wrapper')
    reports = {r['root']: r for r in matrix.get('reports', [])}
    for root in ['gam', 'han', 'as', 'vid']:
        if root not in reports:
            fail('multi-root matrix missing %s' % root)
    if reports['han'].get('agent_expected_after_tm') != 0:
        fail('han should be recognized as fully cached / zero-agent in the local TM preflight')
    if 'han' not in matrix.get('recommended_order', {}).get('skip_cached', []):
        fail('fully cached roots must be listed in skip_cached')
    # `as` carries presplit giants and is uncached in the local TM, so its true
    # agent_expected_after_tm must EXCEED its presplit-key count (the pre-fix len(presplit)
    # formula undercounted vid's real 102-agent run as 13) and it defers rather than
    # run_first. H189 note: the per-call count is now lower than pre-H189 (the presplit lane
    # amortizes at PRESPLIT_GROUP_CITE_BUDGET), but the no-undercount invariant still holds.
    # vid is NOT asserted: its classification depends on how much of it the local TM has
    # cached (a mostly-cached vid is legitimately cheap / run-now), same live-state caveat
    # as han's skip-cached above.
    as_r = reports['as']
    if as_r.get('agent_expected_after_tm', 0) <= len(as_r.get('presplit_keys', [])):
        fail('a presplit-giant root must count real fragment-GROUP calls, exceeding its '
             'len(presplit) — got agents=%r presplit=%r'
             % (as_r.get('agent_expected_after_tm'), len(as_r.get('presplit_keys', []))))
    if 'as' not in matrix.get('recommended_order', {}).get('defer', []):
        fail('an uncached presplit-giant root should defer-calibrate, not run_first')



def test_perf_preflight_fragment_tm_empty_warning():
    from window_common import rootmap_path, input_paths
    root = 'gam'
    key = 'gam~~h0_00_pwg00'
    with gam_pilot_fixture(), tempfile.TemporaryDirectory() as tmp:
        rmpath, _ = rootmap_path(root)
        if not rmpath or not os.path.exists(input_paths(key)[0]):
            return
        tm_sidecar = os.path.join(tmp, 'translation_memory.ru.json')
        with open(tm_sidecar, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.translation_memory.v1', 'lang': 'ru', 'entries': {}}, f)
        proc = run([sys.executable, 'src/pilot/perf_preflight.py', root,
                    '--keys=%s' % key, '--tm=%s' % tm_sidecar,
                    '--wf-glob=no_such_frag_prov_fixture_*.json', '--json'], 0)
        report = json.loads(proc.stdout)
        warnings = report.get('warnings') or []
        if key not in report.get('presplit_keys', []):
            fail('dense fixture must route to presplit for fragment-TM warning test')
        joined = '\n'.join(warnings)
        if 'build-frags --lang ru' not in joined:
            fail('empty fragment TM warning must include the build-frags command')
        if 'no fragment provenance available yet' not in joined:
            fail('empty fragment TM warning must state when no frag_prov source exists')



def test_perf_preflight_partitions_mixed_monster_window():
    import gen_opt_harness2 as gh
    import perf_preflight as pp
    import types
    with tempfile.TemporaryDirectory() as tmp:
        cheap, monster = 'h191cheap', 'h191monster'
        raws = {
            cheap: '=== LAYER: PWG — MAIN ENTRY ===\n{%kurzer deutscher Text%} ohne Citate.',
            monster: '=== LAYER: PWG — MAIN ENTRY ===\n{%Monster%} ' +
                     ' '.join('<ls n="T%d">Quelle %d</ls>' % (i, i) for i in range(220)),
        }
        for key, raw in raws.items():
            with open(os.path.join(tmp, key + '.raw.txt'), 'w', encoding='utf-8') as f:
                f.write(raw)
            with open(os.path.join(tmp, key + '.portrait.json'), 'w', encoding='utf-8') as f:
                f.write('{}')

        def fake_input_paths(k, input_dir=None):
            return os.path.join(tmp, k + '.raw.txt'), os.path.join(tmp, k + '.portrait.json')

        old_gh_ip, old_pp_ip = gh.input_paths, pp.input_paths
        gh.input_paths = fake_input_paths
        pp.input_paths = fake_input_paths
        args = types.SimpleNamespace(keys='%s,%s' % (cheap, monster), nominal=True,
                                     tm_auto=False, tm_path=None, lang='ru',
                                     budget=12000, no_grammar=True,
                                     wf_glob='no_such_fixture_*.json',
                                     cost_ceiling_per_card=2.0,
                                     cost_ceiling_window=25.0)
        try:
            report = pp.build_report(args, 'h191mix')
        finally:
            gh.input_paths = old_gh_ip
            pp.input_paths = old_pp_ip
        part = report.get('cost_partition') or {}
        if part.get('run_now') != [cheap]:
            fail('mixed preflight must leave the cheap card runnable, got %r' % part.get('run_now'))
        if part.get('defer_monster') != [monster]:
            fail('mixed preflight must quarantine the monster card, got %r' % part.get('defer_monster'))
        if 'human-budgeted lane' not in (part.get('recommendation') or ''):
            fail('partition recommendation must name the human-budgeted monster lane')



def test_no_fallback_batch_isolation():
    """Collateral-null fix (2026-07-04): a card with NO selfheal fallback (split_plan() < 2
    fragments) must never share a batch with a card that DOES have one. Mixed together, a
    whole-batch hard failure (StructuredOutput retry cap) drags the no-fallback card down
    with it even though its own content had nothing to do with the failure — only the
    fallback-having card can be rescued via selfHeal. Verified on real 'gam' fixtures: pick
    one splittable card and one unsplittable card, force them into the same output-budget
    window, and assert build() never puts them in the same batch."""
    import gen_opt_harness2 as gh
    from autosplit_requeue import plan as split_plan
    from window_common import rootmap_path, input_paths, read_text
    root = 'gam'
    rmpath, _ = rootmap_path(root)
    if not rmpath:
        return  # inputs not present in this checkout — nothing to assert
    rootmap, keys = gh.selected_keys(root, None)
    keys = [k for k in keys if os.path.exists(input_paths(k)[0])]
    fallback_key, nofallback_key = None, None
    for k in keys:
        pl = split_plan(read_text(input_paths(k)[0]))
        if len(pl) >= 2 and fallback_key is None:
            fallback_key = k
        elif len(pl) < 2 and nofallback_key is None:
            nofallback_key = k
        if fallback_key and nofallback_key:
            break
    if not (fallback_key and nofallback_key):
        return  # fixture set doesn't offer both shapes — nothing to assert
    # a generous shared OUTPUT_BUDGET so both cards would land in ONE batch under the
    # pre-fix (budget-only) grouping — the isolation must still keep them apart.
    saved_budget = gh.OUTPUT_BUDGET
    gh.OUTPUT_BUDGET = 1000
    try:
        js, batches = gh.build(root, [fallback_key, nofallback_key], rootmap, 100000, tm_path=None)
    finally:
        gh.OUTPUT_BUDGET = saved_budget
    for b in batches:
        if fallback_key in b and nofallback_key in b:
            fail('a no-selfheal-fallback card must never share a batch with a '
                 'fallback-having card — got both in %r' % (b,))
    if not any(nofallback_key in b for b in batches):
        fail('no-fallback key must still be owed by some batch')
    if not any(fallback_key in b for b in batches):
        fail('fallback key must still be owed by some batch')



def test_selfheal_fragment_si_threaded_and_tags_normalized():
    """Regression for the 2026-07-04 vid drain SENSE-DUPE false-positive: root vid's
    homonym head h0's giant single-sense part (h0_00_pwg00, source sense '1', 168 <ls>
    citations) was tier-2 split into many citation-batch fragments, all belonging to the
    SAME source sense — but FRAGS[k] (the fragment fallback fed to the JS selfHeal path)
    discarded split_plan()'s sense_ord (previously bound to `_si` and thrown away), so the
    JS heal path had no way to know the fragments shared a parent sense. Translating each
    fragment independently, the model fabricated fresh incrementing tags per fragment
    (2,3,4...) that then collided with a sibling rootmap part's REAL different senses in
    audit_sense_dupes.py's cross-part duplicate check — a deterministic tagging artifact,
    not model stochasticity (reproduced identically across 2 independent live requeue
    rounds). Fixed by threading sense_ord into FRAGS as 'si' (Python side, gen_opt_harness2)
    and normalizing every fragment's tag to its group's first-seen tag per si in JS
    selfHeal() (siTag/applyTag — verified by code inspection; window_selftest has no JS
    runtime). This test exercises the Python-side wiring: a citation-dense single-sense
    fixture card must produce >=2 FRAGS fragments that ALL carry the same si."""
    import re as _re
    import gen_opt_harness2 as gh
    from window_common import input_paths
    from autosplit_requeue import plan as split_plan
    key = '_selftest_giant~~h0_00_pwgtest'
    lines = ['Uebersicht der Citate zu diesem einzigen Sinn dieses Testkopfes.']
    for i in range(25):
        lines.append('Wort%d <ls n="RV.%d.1">citation text %d</ls> und mehr erlaeuternder Text.'
                     % (i, i, i))
    raw = '\n'.join(lines)
    rp, pp = input_paths(key)
    if os.path.exists(rp) or os.path.exists(pp):
        fail('selftest fixture key collides with a real input file — pick a different key')
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    try:
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('{}')
        pl = split_plan(raw)
        if len(pl) < 2:
            fail('fixture did not produce a multi-fragment plan — adjust the fixture')
        if len({si for si, _pi, _t in pl}) != 1:
            fail('fixture should be ONE giant sense split into citation batches (all si==0)')
        js, _batches = gh.build('_selftest_giant', [key], None, 100000, tm_path=None)
        frags = json.loads(_re.search(r'^const FRAGS = (.*)$', js, _re.M).group(1))
        if key not in frags:
            fail('selfheal fallback was not computed for the fixture card')
        sis = [frag.get('si') for grp in frags[key] for frag in grp]
        if len(sis) < 2:
            fail('fixture did not thread into >=2 FRAGS fragments')
        if any(si is None for si in sis):
            fail('FRAGS fragments are missing the si (sense_ord) field — the '
                 'fragment-tag-collision fix regressed')
        if len(set(sis)) != 1:
            fail('all fragments of one giant sense must share the SAME si, got %r' % sis)
    finally:
        for p in (rp, pp):
            if os.path.exists(p):
                os.remove(p)



def test_kill_gate_wired():
    """H155 follow-up (2026-07-04): the wall-clock kill gate must be wired into every
    schema-bearing agent() call so a stalled/doomed call (the ~7-min tyaj~~h0_zz_pw
    retry-cap loop, or any un-characterized future driver) is abandoned at KILL_FACTOR x
    its expected-for-complexity time and routed to the bounded fragment lane — instead of
    burning the full StructuredOutput retry cap. Static regression guard on the generated
    harness: the kill consts render, the budget helper + both call sites use agentKill,
    INPUTS carries the skeleton (the complexity signal), and --no-kill disables it."""
    import re as _re
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n'
           '<div n="1">— 1〉 {%verlassen%} <ls>Y. 2</ls>.\n')
    key = 'zz~~synthetic_kill'
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        saved_ip = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        try:
            js, _b = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
            # consts present with the calibrated defaults
            if 'const KILL = true' not in js:
                fail('kill gate must default ON (const KILL = true) in the generated harness')
            for c in ('KILL_FACTOR', 'KILL_BASE_MS', 'KILL_SLOPE_MS', 'KILL_FLOOR_MS', 'KILL_CEIL_MS'):
                if not _re.search(r'^const %s = [0-9.]+$' % c, js, _re.M):
                    fail('kill const %s missing/malformed in the generated harness' % c)
            # helper + BOTH call sites (resolveGroup main lane + healGroup fragment lane) use it
            n = js.count('agentKill(')
            if n < 3:
                fail('agentKill must appear 3x (definition + main-batch call + heal-group call); '
                     'got %d — a call site is unguarded' % n)
            if 'class KillTimeout' not in js or 'const isKill' not in js:
                fail('KillTimeout/isKill classifier must be present so a kill is distinguished '
                     'from a real hard failure')
            # the complexity signal (skeleton bytes) must be carried per card
            inputs = json.loads(_re.search(r'^const INPUTS = (\{.*?\})\nconst PH', js, _re.S | _re.M).group(1))
            if 'skeleton' not in inputs[key] or 'senses' not in inputs[key]:
                fail('INPUTS must carry skeleton (kill-budget signal) + senses; got keys %r'
                     % sorted(inputs[key]))
            meta = json.loads(_re.search(r'^const META = (\{.*\})\n', js, _re.M).group(1))
            if not meta.get('kill') or not meta.get('kill_gate'):
                fail('meta must record the kill-gate provenance (kill + kill_gate)')
            # --no-kill disables it
            saved_kill = gh.KILL
            gh.KILL = False
            try:
                js2, _b2 = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
            finally:
                gh.KILL = saved_kill
            if 'const KILL = false' not in js2:
                fail('--no-kill / KILL=False must render const KILL = false (disables the gate)')
        finally:
            gh.input_paths = saved_ip
    finally:
        shutil.rmtree(d, ignore_errors=True)



def test_no_fallback_single_gets_ceil_kill_budget():
    """H220: a SINGLE card with no selfheal fallback (single-fragment supplement / nominal
    card that does not split) must get the CEIL kill budget, not the byte-scaled one — the
    kill gate has no smaller lane to route it to, so an early kill on a tiny skeleton's budget
    is pure loss (the no-PWG w1 run killed 6/6 nulls at 53-104 s; all would have passed
    accept). Static guard: killBudgetForCur/hasFallback render, the resolveGroup main-lane
    agentKill call passes killBudgetForCur(cur), and the override returns KILL_CEIL_MS for a
    single no-fallback card while multi-card / splittable batches keep the byte-scaled gate."""
    import re as _re
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '{#mahat#}¦ <lex>Adv.</lex> {%gross werden%}.\n')
    key = 'zz~~h0_zz_pw'
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[{"portrait_kind":"no_pwg_supplement_chain","key1":"mahat","iast":"mahat","senses":[]}]')
        saved_ip = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        try:
            js, _b = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
        finally:
            gh.input_paths = saved_ip
        if 'const hasFallback = ' not in js or 'const killBudgetForCur = ' not in js:
            fail('killBudgetForCur/hasFallback helpers must render in the generated harness')
        if 'KILL_CEIL_MS : killBudgetMs(skelBytesOfKeys(cur))' not in js:
            fail('killBudgetForCur must return KILL_CEIL_MS for a no-fallback single, else the '
                 'byte-scaled budget')
        # the main-lane agentKill call (resolveGroup) must feed the override, not just skelBytes
        if 'skelBytesOfKeys(cur), killBudgetForCur(cur))' not in js:
            fail('resolveGroup agentKill call must pass killBudgetForCur(cur) as the budget '
                 'override — otherwise the byte-scaled gate still kills no-fallback singles')
        # this no-PWG card is single-fragment: FRAGS empty -> hasFallback false -> CEIL applies
        frags = json.loads(_re.search(r'^const FRAGS = (\{.*?\})\n', js, _re.S | _re.M).group(1))
        if frags.get(key):
            fail('a single no-PWG supplement card must have no FRAGS groups (no split); got %r'
                 % frags.get(key))
    finally:
        shutil.rmtree(d, ignore_errors=True)



def test_presplit_cite_floor_is_not_masked_by_batch_budget():
    """H2160: the per-card fail-solo citation trigger must NOT be suppressed by a LARGER
    batch budget.

    `PRESPLIT_SOLO_CITE_FLOOR` (40) encodes a per-CARD fact — a card carrying >=40
    citation-units cannot be emitted whole inside any acceptable wall-clock ceiling.
    `OUTPUT_BUDGET` (90) encodes an unrelated per-BATCH fact — how many citation-units
    to pack into one call. Combining them as `max(budget, floor)` let the larger BATCH
    number mask the per-card one, so with the default budget the floor was inert by
    construction ("For OUTPUT_BUDGET >= 40 (default 90) nothing changes").

    That is the medium50 `b0` defect measured 02-08-2026: w1's three cards score 80 / 79 /
    75 citation-units — all above the 40 fail-solo floor, all below the 90 batch budget —
    so `presplit_keys` came out `[]`, every card was attempted whole, and every whole-card
    call was abandoned at exactly `KILL_CEIL_MS` (180 044 ms under the old ceiling, then
    300 073 ms under the new one). A card is not made easier to emit whole by raising the
    number of cards you would have liked to batch beside it.

    RED before the fix: a 50-<ls> card under the default budget 90 does not presplit.
    """
    import re as _re
    import gen_opt_harness2 as gh
    senses = ''.join(
        '— %d〉 {%%Bedeutung %d%%} %s.\n' % (i + 1, i + 1,
                                                 ' '.join('<ls>Ref. %d.%d</ls>' % (i + 1, j + 1)
                                                          for j in range(10)))
        for i in range(5))
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '{#word#}¦ <lex>Adj.</lex>\n' + senses)
    key = 'zz~~h0_zz_pw'
    d = tempfile.mkdtemp()
    saved_ip, saved_ob = gh.input_paths, gh.OUTPUT_BUDGET
    saved_floor = gh.PRESPLIT_SOLO_CITE_FLOOR
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        # The medium50 shape: 51 citation-units — above the 40 fail-solo floor, below the
        # 90 batch budget. 5 senses keeps it under SENSE_PRESPLIT_BUDGET (20), so this
        # isolates the CITATION trigger from the orthogonal sense-density one.
        gh.OUTPUT_BUDGET = 90
        gh.PRESPLIT_SOLO_CITE_FLOOR = 40
        js, _b = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
        presplit = json.loads(_re.search(r'^const PRESPLIT = (.*)$', js, _re.M).group(1))
        if key not in presplit:
            fail('a card above the per-card fail-solo cite floor (40) must presplit even when '
                 'the BATCH budget (90) is larger — the batch number must not mask the per-card '
                 'one (H2160 medium50 b0); got PRESPLIT=%r' % presplit)
        # The floor must still be load-bearing in the other direction: raise it above the
        # card and the SAME card translates whole.
        gh.PRESPLIT_SOLO_CITE_FLOOR = 200
        js2, _b2 = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
        presplit2 = json.loads(_re.search(r'^const PRESPLIT = (.*)$', js2, _re.M).group(1))
        if key in presplit2:
            fail('with the fail-solo floor raised above the card, it must NOT presplit — proves '
                 'the trigger is driven by the per-card floor; got PRESPLIT=%r' % presplit2)
    finally:
        gh.input_paths = saved_ip
        gh.OUTPUT_BUDGET = saved_ob
        gh.PRESPLIT_SOLO_CITE_FLOOR = saved_floor
        shutil.rmtree(d, ignore_errors=True)



def test_presplit_cite_floor_and_single_ceil():
    """H255/H823: the CITATION presplit trigger must not misfire under --output-budget=1.
    With a 1-card batch budget, (1+<ls>) > budget fires on ANY citation-bearing card, force-
    routing tiny cards into the fragment heal lane whose byte-scaled kill budgets die on a slow
    API (the H255 presplit-cohort loss). PRESPLIT_SOLO_CITE_FLOOR gates the trigger so only
    genuine fail-solo giants presplit; dropping the floor reproduces the misfire. Also: a
    single-card batch now gets the CEIL kill budget regardless of a heal fallback (a lone card
    has no batch-mates to starve, and the heal lane is no better budgeted on a slow API)."""
    import re as _re
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '{#word#}¦ <lex>Adj.</lex>\n'
           '— 1〉 {%Bedeutung eins%} <ls>Ref. 1</ls> <ls>Ref. 2</ls>.\n'
           '— 2〉 {%Bedeutung zwei%} <ls>Ref. 3</ls> <ls>Ref. 4</ls>.\n'
           '— 3〉 {%Bedeutung drei%} <ls>Ref. 5</ls>.\n')
    key = 'zz~~h0_zz_pw'
    d = tempfile.mkdtemp()
    saved_ip, saved_ob = gh.input_paths, gh.OUTPUT_BUDGET
    saved_floor = gh.PRESPLIT_SOLO_CITE_FLOOR
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        # no-PWG lane (--output-budget=1): with the default floor (40) a 5-<ls> card must NOT presplit.
        gh.OUTPUT_BUDGET = 1
        gh.PRESPLIT_SOLO_CITE_FLOOR = 40
        js, _b = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
        presplit = json.loads(_re.search(r'^const PRESPLIT = (.*)$', js, _re.M).group(1))
        if key in presplit:
            fail('under --output-budget=1 with the cite floor, a low-<ls> card must NOT presplit '
                 '(it should translate whole); got PRESPLIT=%r' % presplit)
        if '(cur.length === 1) ? KILL_CEIL_MS' not in js:
            fail('killBudgetForCur must give ANY single-card batch the CEIL budget (H255/H823)')
        # dropping the floor (=1) reproduces the pre-fix misfire: the citation-bearing card presplits.
        gh.PRESPLIT_SOLO_CITE_FLOOR = 1
        js2, _b2 = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
        presplit2 = json.loads(_re.search(r'^const PRESPLIT = (.*)$', js2, _re.M).group(1))
        if key not in presplit2:
            fail('with the floor disabled (=1), --output-budget=1 must presplit the citation-'
                 'bearing card — proves the floor is load-bearing; got PRESPLIT=%r' % presplit2)
    finally:
        gh.input_paths = saved_ip
        gh.OUTPUT_BUDGET = saved_ob
        gh.PRESPLIT_SOLO_CITE_FLOOR = saved_floor
        shutil.rmtree(d, ignore_errors=True)



def test_selfheal_no_fallback_preserves_upstream_reason():
    """H220 observability: when selfHeal has no fragments to work with, it must NOT clobber a
    more specific upstream failure reason already recorded (kill-timeout / mismatched-key /
    fidelity-reject) with the generic 'no-selfheal-fallback' — that overwrite hid a kill-gate
    mass-kill behind a misleading message for a whole session."""
    import gen_opt_harness2 as gh
    raw = '=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n{#x#}¦ {%y%}.\n'
    key = 'zz~~h0_zz_pw'
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        saved_ip = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        try:
            js, _b = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
        finally:
            gh.input_paths = saved_ip
        if "if (!FAIL[k]) noteFail(k, 'no-selfheal-fallback" not in js:
            fail("selfHeal no-fallback branch must guard on !FAIL[k] so it preserves the specific "
                 "upstream reason (kill-timeout etc.) instead of overwriting it")
    finally:
        shutil.rmtree(d, ignore_errors=True)



def test_group_by_budget_count_cap():
    """H189: _group_by_budget's count_cap closes a group once it holds count_cap items
    regardless of summed size, so a run of many tiny (size-1) fragments can't pack an
    unbounded COUNT (== senses to emit) into one presplit-lane call. Default (no cap)
    keeps the size-only behavior every pre-H189 caller relied on."""
    import gen_opt_harness2 as gh
    items = [{'w': 1}] * 40
    sizer = lambda it: it['w']
    # size-only: 40 weight-1 items at budget 60 = 1 group (nothing caps count)
    if len(gh._group_by_budget(items, sizer, 60)) != 1:
        fail('size-only grouping of 40 size-1 items at budget 60 must be a single group')
    # count_cap=18: 40 -> ceil(40/18) = 3 groups even though total size (40) < budget (60)
    capped = gh._group_by_budget(items, sizer, 60, count_cap=18)
    if len(capped) != 3 or any(len(g) > 18 for g in capped):
        fail('count_cap=18 must yield 3 groups of <=18 for 40 items; got sizes %r'
             % [len(g) for g in capped])



def test_presplit_card_uses_amortized_grouping():
    """H189 core fix: a card routed to the presplit-PRIMARY lane is grouped at
    PRESPLIT_GROUP_CITE_BUDGET/PRESPLIT_GROUP_SENSE_CAP (amortizing the ~27k framework
    across many fragments per call), NOT the conservative SELFHEAL_GROUP_BUDGET. A
    30-sense/1-<ls> card must group by the sense cap (ceil(30/18)=2), not by the old
    per-12-citation budget (ceil(30/12)=3) — proving fewer, larger fragment-lane calls."""
    import re as _re
    import gen_opt_harness2 as gh
    senses = '\n'.join('<div n="1">— %d〉 {%%Bedeutung %d%%}.' % (i, i)
                       for i in range(1, 31))
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n' + senses + '\n')
    key = 'zz~~synthetic_amortize'
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        saved_ip = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        try:
            js, _b = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
            frags = json.loads(_re.search(r'^const FRAGS = (\{.*?\})\nconst PHF', js, _re.S | _re.M).group(1))
            groups = frags.get(key) or []
            if not (1 < len(groups) <= 2):
                fail('a 30-sense presplit card must group into 2 amortized fragment calls '
                     '(sense cap 18), not the old ~3 at budget 12; got %d groups' % len(groups))
            if any(len(g) > gh.PRESPLIT_GROUP_SENSE_CAP for g in groups):
                fail('no presplit group may exceed PRESPLIT_GROUP_SENSE_CAP fragments')
        finally:
            gh.input_paths = saved_ip
    finally:
        shutil.rmtree(d, ignore_errors=True)



def test_kill_gate_recalibrated_envelope():
    """H189/H2313: pin the shared production timeout and the tightened 45s floor.

    The ceiling bound was 180000 ('>3 min unacceptable', MG). Relaxed to 300000 on
    02-08-2026 by explicit human ruling (issue #983) after measurement showed the 3 min
    ceiling was itself the reason a paid window returned zero cards: 12 of 16 calls died at
    exactly 180 04x-180 23x ms, and it was not tunable from below because heal groups were
    already at ONE fragment. H2313 subsequently proved a real card-phase call completing
    successfully at 221712 ms under the 600000 ms shared ceiling. The regression guard must
    therefore compare against that single execution-contract constant instead of retaining
    a stale local 300000 ms ceiling."""
    import execution_contract as ec
    import gen_opt_harness2 as gh
    if gh.KILL_FLOOR_MS > 45000:
        fail('KILL_FLOOR_MS must be <= 45000 (was 120000) so a tiny subcard is killed '
             'near MG\'s ~60s suspicion line; got %d' % gh.KILL_FLOOR_MS)
    if gh.KILL_CEIL_MS != ec.PRODUCTION_HARD_TIMEOUT_MS:
        fail('KILL_CEIL_MS must equal the shared PRODUCTION_HARD_TIMEOUT_MS (%d, H2313); '
             'got %d' % (ec.PRODUCTION_HARD_TIMEOUT_MS, gh.KILL_CEIL_MS))



def test_agent_budget_plan_separates_translate_and_heal_pools():
    """H442/H462: the heal pool must let every per-card cap become reachable."""
    import agent_budget as ab
    groups = {'a': 2, 'b': 5, 'c': 1}
    plan = ab.derive_agent_budget(8, groups)
    expected_translate = int(math.ceil(8 * 3.0)) + 10
    expected_heal = sum(int(math.ceil(n * 1.5)) + 3 for n in groups.values())
    if plan.max_translate_agents != expected_translate:
        fail('translate pool must scale only from whole-card batches')
    if plan.max_heal_agents != expected_heal:
        fail('heal pool must equal the sum of per-card ceilings so the window cannot bind first')
    if plan.max_agents != expected_translate + expected_heal:
        fail('combined max_agents must be the sum of the two independently enforced pools')
    overridden = ab.derive_agent_budget(8, groups, max_agents_override=20)
    if overridden.max_agents != 20 or not overridden.max_translate_agents or not overridden.max_heal_agents:
        fail('--max-agents must remain a hard combined override allocated across active pools')
    disabled = ab.derive_agent_budget(8, groups, enabled=False)
    if disabled.max_agents is not None:
        fail('--no-kill-switch must disable both budget pools')



def test_split_agent_pools_all_heal_runtime():
    """Execute the generated JS with a null-returning mock agent.

    Two sense-dense cards route directly to recovery. Every call fails, so each card must
    stop at its own cap. The window heal pool is exactly the sum of those caps and therefore
    must *not* trip first — the production invariant H442 could not previously satisfy.
    """
    import gen_opt_harness2 as gh
    senses = '\n'.join('<div n="1">— %d〉 {%%Bedeutung %d%%}.' % (i, i)
                       for i in range(1, 31))
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n' + senses + '\n')
    keys = ['zz~~runtime_pool_a', 'zz~~runtime_pool_b']
    d = tempfile.mkdtemp()
    saved_ip = gh.input_paths
    saved_kill = gh.KILL
    try:
        paths = {}
        for key in keys:
            rp = os.path.join(d, key + '.raw.txt')
            pp = os.path.join(d, key + '.portrait.json')
            with open(rp, 'w', encoding='utf-8') as f:
                f.write(raw)
            with open(pp, 'w', encoding='utf-8') as f:
                f.write('[]')
            paths[key] = (rp, pp)
        gh.input_paths = lambda k, input_dir=None: paths[k]
        gh.KILL = False  # mock calls are immediate; exercise budgets, not wall time
        js, batches = gh.build(
            'zz_runtime_pool', keys, None, 12000,
            nominal=True, grammar_on=False, tm_path=None)
        if batches:
            fail('sense-dense runtime fixture must be presplit-only; got batches=%r' % batches)
        marker = 'return { meta: META, summary, results: out }'
        if marker not in js:
            fail('generated runtime return marker changed; update behavioral harness deliberately')
        runnable = (
            "const phase = () => {};\n"
            "const log = () => {};\n"
            "const agent = async () => null;\n"
            "const parallel = async thunks => Promise.all(thunks.map(async fn => { "
            "try { return await fn() } catch (_) { return null } }));\n" +
            js.replace(marker, 'console.log(JSON.stringify({ meta: META, summary, results: out }))'))
        script = os.path.join(d, 'runtime_pool_test.mjs')
        with open(script, 'w', encoding='utf-8', newline='\n') as f:
            f.write(runnable)
        p = subprocess.run(
            ['node', script], capture_output=True, text=True, encoding='utf-8', timeout=30)
        if p.returncode:
            fail('mock generated runtime failed:\n%s\n%s' % (p.stdout, p.stderr))
        payload = json.loads(p.stdout.strip().splitlines()[-1])
        summary = payload['summary']
        if summary['translate_agents_spent'] != 0:
            fail('presplit-only fixture must spend zero translate calls')
        if summary['heal_agents_spent'] != summary['max_heal_agents']:
            fail('all-heal fixture must stop exactly at the sum of per-card caps; got %r' % summary)
        if summary['heal_budget_tripped']:
            fail('window heal pool fired before/at a per-card cap — shared-counter bug returned')
        if summary['budget_kill_switch_tripped']:
            fail('no window pool should trip when each card stops at its own ceiling')
        if summary['null'] != len(keys):
            fail('null mock must leave every card explicitly requeueable')
    finally:
        gh.input_paths = saved_ip
        gh.KILL = saved_kill
        shutil.rmtree(d, ignore_errors=True)



def test_lowwide_staggered_dispatch():
    """H255/H811: --max-wide=N routes the top-level dispatch through boundedParallel (<=N units
    in flight, first N starts staggered by --stagger-ms) so a degraded generation API isn't hit
    ~10-wide; the default (0) falls back to the runtime parallel() with no regression. The
    behavioral half runs the REAL emitted boundedParallel (see boundedparallel_test.js)."""
    import gen_opt_harness2 as gh
    saved_ip, saved_kill = gh.input_paths, gh.KILL
    saved_wide, saved_stag = gh.MAX_WIDE, gh.STAGGER_MS
    d = tempfile.mkdtemp()
    try:
        keys = ['kk1~~h0_zz_pw', 'kk2~~h0_zz_pw']
        paths = {}
        for k in keys:
            rp = os.path.join(d, k + '.raw.txt')
            pp = os.path.join(d, k + '.portrait.json')
            with open(rp, 'w', encoding='utf-8') as f:
                f.write('=== LAYER: PW ===\n\n{#kk#} <lex>Adj.</lex> {%probe gloss%} <ls>Ref. 1,1</ls>.')
            with open(pp, 'w', encoding='utf-8') as f:
                f.write('[]')
            paths[k] = (rp, pp)
        gh.input_paths = lambda k, input_dir=None: paths[k]
        gh.KILL = False
        gh.MAX_WIDE, gh.STAGGER_MS = 3, 1500
        js, _ = gh.build('zz_lowwide', keys, None, 12000,
                         nominal=True, grammar_on=False, tm_path=None)
        if 'const MAX_WIDE = 3' not in js or 'const STAGGER_MS = 1500' not in js:
            fail('--max-wide/--stagger-ms did not emit the MAX_WIDE/STAGGER_MS constants')
        if 'async function boundedParallel' not in js:
            fail('boundedParallel helper not emitted')
        if 'boundedParallel(UNITS.map(u => u.run), MAX_WIDE, STAGGER_MS)' not in js:
            fail('top-level dispatch is not routed through boundedParallel')
        gh.MAX_WIDE, gh.STAGGER_MS = 0, 0
        js0, _ = gh.build('zz_default', keys, None, 12000,
                          nominal=True, grammar_on=False, tm_path=None)
        if 'const MAX_WIDE = 0' not in js0:
            fail('default harness must emit MAX_WIDE=0 (unbounded, no regression)')
        harness = os.path.join(d, 'lowwide_harness.js')
        with open(harness, 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        test_js = os.path.join(HERE,
                               'boundedparallel_test.js')
        p = subprocess.run(['node', test_js, harness],
                           capture_output=True, text=True, encoding='utf-8', timeout=30)
        if p.returncode:
            fail('boundedParallel behavioral test failed:\n%s\n%s' % (p.stdout, p.stderr))
    finally:
        gh.input_paths, gh.KILL = saved_ip, saved_kill
        gh.MAX_WIDE, gh.STAGGER_MS = saved_wide, saved_stag
        shutil.rmtree(d, ignore_errors=True)



def test_budget_kill_switch_wired():
    """The generated Workflow must enforce independent translate/heal call ceilings."""
    import re as _re
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n'
           '<div n="1">— 1〉 {%verlassen%} <ls>Y. 2</ls>.\n')
    key = 'zz~~synthetic_switch'
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        saved_ip = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        try:
            js, _b = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
            for tok in ('const KILL_SWITCH = true', 'const MAX_AGENTS =',
                        'const MAX_TRANSLATE_AGENTS =', 'const MAX_HEAL_AGENTS =',
                        'class BudgetExceeded', 'AGENTS_SPENT++',
                        'TRANSLATE_AGENTS_SPENT++', 'HEAL_AGENTS_SPENT++',
                        'TRANSLATE_BUDGET_TRIPPED', 'HEAL_BUDGET_TRIPPED'):
                if tok not in js:
                    fail('budget kill-switch token %r missing from the harness' % tok)
            # BudgetExceeded must NOT be treated as a kill (a kill routes to MORE fragment
            # calls — the opposite of a budget stop).
            if _re.search(r'isKill\s*=.*BudgetExceeded', js):
                fail('BudgetExceeded must not be classified as a kill (would spawn more agents)')
            meta = json.loads(_re.search(r'^const META = (\{.*\})\n', js, _re.M).group(1))
            expected_translate = meta.get('batch_count', 0)
            want_translate = (int(math.ceil(expected_translate * gh.MAX_AGENTS_FACTOR))
                              + gh.MAX_AGENTS_HEADROOM)
            if meta.get('max_translate_agents') != want_translate:
                fail('translate ceiling must be ceil(batch_count*factor)+headroom=%d; got %r'
                     % (want_translate, meta.get('max_translate_agents')))
            if meta.get('max_agents') != (meta.get('max_translate_agents', 0)
                                          + meta.get('max_heal_agents', 0)):
                fail('meta.max_agents must be the sum of the split pool ceilings')
            if meta.get('agent_budget_strategy') != 'split-pools-per-card-heal':
                fail('default generated runtime must declare the split-pool strategy')
            if hasattr(gh, 'MAX_AGENTS_FLOOR'):
                fail('the flat one-size-fits-all MAX_AGENTS_FLOOR must be gone — the ceiling '
                     'must scale with word size so a small-word runaway is caught, not clamped to 40')
            for field in ('budget_kill_switch_tripped', 'translate_budget_tripped',
                          'heal_budget_tripped', 'translate_agents_spent', 'heal_agents_spent'):
                if field not in js:
                    fail('run summary must expose %s' % field)
        finally:
            gh.input_paths = saved_ip
    finally:
        shutil.rmtree(d, ignore_errors=True)



def test_per_card_heal_budget_wired():
    """H442: the window MAX_AGENTS switch is a SHARED pool — it cannot stop ONE dense card
    from spending the whole window budget before the other cards run (H437 medium50: 3-4
    dense band-4 nominal singletons cascaded through heal bisection to 61/61 agents, leaving
    ~9 cards nulled `budget-kill-switch` UN-ATTEMPTED). The fix is a PER-CARD heal-call ceiling
    threaded through healGroup's recursion: once a card's own heal spend crosses
    ceil(nGroups*factor)+headroom, healGroup stops retrying/bisecting and returns a PARTIAL
    card so the dense card fails fast + cheap instead of draining the shared pool. This pins
    the wiring so a future edit can't silently drop the per-card ceiling back to unbounded."""
    import re as _re
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n'
           '<div n="1">— 1〉 {%verlassen%} <ls>Y. 2</ls>.\n')
    key = 'zz~~synthetic_percard'
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        saved_ip = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        try:
            js, _b = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
            # 1) the ceiling must be threaded THROUGH healGroup (5th arg) and its bisection
            #    recursion — a per-group check alone would let one group's deep bisect run away.
            for tok in ('async function healGroup(k, idxs, grp, label, budget)',
                        'const budgetExhausted =',
                        "label + '/A', budget)", "label + '/B', budget)",
                        'const PER_CARD_HEAL_BUDGET = true',
                        'per-card-heal-budget:'):
                if tok not in js:
                    fail('per-card heal budget token %r missing from the harness' % tok)
            # 2) selfHeal must build one shared {spent,max} per CARD (sized off its group count)
            #    and pass THAT object into every group's healGroup call.
            if 'const cardBudget' not in js or 'groups.length * PER_CARD_HEAL_FACTOR' not in js:
                fail('selfHeal must derive a per-card budget from the card group count')
            if "grp, 'heal:' + k + '#g' + (gi + 1), cardBudget)" not in js:
                fail('selfHeal must pass the per-card budget into healGroup')
            # 3) the bisection recursion must be gated on the budget, not fire unconditionally.
            if 'pending.length > 1 && !budgetExhausted()' not in js:
                fail('bisection must be skipped once the per-card heal budget is exhausted')
            # 4) META surfaces the calibrated knobs for run observability.
            meta = json.loads(_re.search(r'^const META = (\{.*\})\n', js, _re.M).group(1))
            if meta.get('per_card_heal_budget') is not True:
                fail('meta.per_card_heal_budget must be true when selfheal is on')
            if meta.get('per_card_heal_factor') != gh.PER_CARD_HEAL_FACTOR:
                fail('meta.per_card_heal_factor must echo the configured factor')
            if meta.get('per_card_heal_headroom') != gh.PER_CARD_HEAL_HEADROOM:
                fail('meta.per_card_heal_headroom must echo the configured headroom')
            # 5) --no-per-card-heal-budget restores the old unbounded per-card heal (max:null).
            saved_flag = gh.PER_CARD_HEAL_BUDGET
            try:
                gh.PER_CARD_HEAL_BUDGET = False
                js_off, _b2 = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
            finally:
                gh.PER_CARD_HEAL_BUDGET = saved_flag
            if 'const PER_CARD_HEAL_BUDGET = false' not in js_off:
                fail('--no-per-card-heal-budget must emit PER_CARD_HEAL_BUDGET = false')
            meta_off = json.loads(_re.search(r'^const META = (\{.*\})\n', js_off, _re.M).group(1))
            if meta_off.get('per_card_heal_budget') is not False:
                fail('meta.per_card_heal_budget must be false when disabled')
        finally:
            gh.input_paths = saved_ip
    finally:
        shutil.rmtree(d, ignore_errors=True)



def test_heal_group_kill_timeout_does_not_bisect():
    """H442 P0: after the first kill-timeout in healGroup, unresolved fragments requeue
    instead of recursively splitting into /A and /B calls that hit the same slow-call floor."""
    import re as _re
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n'
           '<div n="1">— 1〉 {%verlassen%} <ls>Y. 2</ls>.\n')
    key = 'zz~~synthetic_kill_no_bisect'
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        saved_ip = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        try:
            js, _b = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
            for tok in ('const KILL_TIMEOUT_NO_BISECT = true',
                        'let killedOut = false',
                        'killedOut = true',
                        'kill-timeout-no-bisect:',
                        'const killBisectBlocked = killedOut && KILL_TIMEOUT_NO_BISECT',
                        'pending.length > 1 && !budgetExhausted() && !killBisectBlocked'):
                if tok not in js:
                    fail('kill-timeout no-bisect token %r missing from the harness' % tok)
            if 'killDepth' in js or 'KILL_BISECT_MAX_DEPTH' in js or 'nextKillDepth' in js:
                fail('kill-timeout bisection depth cap must be replaced by immediate no-bisect')
            meta = json.loads(_re.search(r'^const META = (\{.*\})\n', js, _re.M).group(1))
            if meta.get('kill_timeout_no_bisect') is not True:
                fail('meta.kill_timeout_no_bisect must be true when kill+selfheal are on')
        finally:
            gh.input_paths = saved_ip
    finally:
        shutil.rmtree(d, ignore_errors=True)



def test_perf_preflight_cost_gate():
    """H189: the preflight cost gate must FLAG a window whose estimated $ per translated
    card exceeds the ceiling (a window of kAla-class monsters — exactly pril10_w1) and must
    PASS a cheap high-card-count window (e.g. `as`: many cards, low per-card cost). The
    per-card ratio is the load-bearing, model-independent signal."""
    import perf_preflight as pp
    # pril10_w1-shape: 8 cards, ~69 fragment-group agents (post-fix) -> ~$4/card >> ceiling.
    # B14 (H1339): a real monster window ALWAYS carries presplit telemetry (69 agents for 8
    # cards IS fragment fan-out); the estimate prices presplit fragment agents at the
    # pril10 monster calibration, so the gate keeps its teeth under lane-aware pricing.
    monster = {'agent_expected_after_tm': 69, 'selected_keys': ['k%d' % i for i in range(8)],
               'tm_cards': 0, 'degenerate_passthrough_keys': [],
               'presplit_keys': ['k%d' % i for i in range(8)], 'batch_count': 0}
    cg = pp.cost_estimate(monster)
    if not cg['over_ceiling'] or cg['est_cost_per_card_usd'] <= cg['per_card_ceiling_usd']:
        fail('a window of 8 monster cards costing ~$4/card must trip the cost gate; got %r' % cg)
    # B14: missing batch telemetry with presplit present falls CONSERVATIVELY to all-monster
    # pricing -- degraded telemetry can only over-price, never under-price, a monster.
    no_batchcount = dict(monster)
    no_batchcount.pop('batch_count')
    if not pp.cost_estimate(no_batchcount)['over_ceiling']:
        fail('missing batch telemetry must fall conservatively to monster pricing')
    # cheap high-count window: 98 cards, 24 agents -> pennies/card -> passes
    cheap = {'agent_expected_after_tm': 24, 'selected_keys': ['k%d' % i for i in range(98)],
             'tm_cards': 0, 'degenerate_passthrough_keys': []}
    if pp.cost_estimate(cheap)['over_ceiling']:
        fail('a large but cheap-per-card window must NOT trip the cost gate')
    # fully cached window: 0 agents -> $0 -> never gated
    cached = {'agent_expected_after_tm': 0, 'selected_keys': ['k1'], 'tm_cards': 1,
              'degenerate_passthrough_keys': []}
    if pp.cost_estimate(cached)['over_ceiling']:
        fail('a fully-cached (zero-agent) window must never trip the cost gate')



def test_coordinator_cost_gate_enforced():
    """H304: coordinator prepare refuses a cost-gate-flagged window (parks it in the
    deferred ledger) unless --allow-over-cost; a clean window passes untouched."""
    import coordinator as co
    tmp = tempfile.mkdtemp()
    flagged = os.path.join(tmp, 'preflight.json')
    with open(flagged, 'w', encoding='utf-8') as f:
        json.dump({'schema': 'pwg.performance_preflight.matrix.v1',
                   'reports': [{'root': 'kAla',
                                'cost_gate': {'over_ceiling': True, 'est_cost_usd': 79.83,
                                              'est_cost_per_card_usd': 4.0},
                                'cost_partition': {'run_now': ['a'],
                                                   'defer_monster': ['b', 'c']}}]}, f)
    clean = os.path.join(tmp, 'preflight_clean.json')
    with open(clean, 'w', encoding='utf-8') as f:
        json.dump({'schema': 'pwg.performance_preflight.matrix.v1',
                   'reports': [{'root': 'vah', 'cost_gate': {'over_ceiling': False}}]}, f)
    captured = []
    old = co.defer_monster
    co.defer_monster = lambda *a, **k: captured.append((a, k))
    try:
        try:
            co.enforce_cost_gate(flagged, 'kAla')
            fail('enforce_cost_gate must refuse an over-ceiling window')
        except SystemExit as e:
            if 'deferred_monsters' not in str(e):
                fail('cost-gate refusal must point at the deferred ledger: %s' % e)
        if len(captured) != 1:
            fail('refusal must park the window in the ledger exactly once')
        co.enforce_cost_gate(flagged, 'kAla', allow_over_cost=True)   # no raise
        if len(captured) != 2:
            fail('--allow-over-cost must still record the ledger row')
        co.enforce_cost_gate(clean, 'vah')
        if len(captured) != 2:
            fail('a clean window must not touch the ledger')
    finally:
        co.defer_monster = old



def test_h1283_a5_max_wide_default_bounded():
    """A5 (H1283): bounded dispatch is the DEFAULT — the highest throughput-per-effort lever."""
    import gen_opt_harness2 as gh
    if gh.MAX_WIDE != 3:
        fail('A5: gen_opt_harness2.MAX_WIDE default must be 3 (got %r)' % gh.MAX_WIDE)
    if gh.STAGGER_MS != 2000:
        fail('A5: gen_opt_harness2.STAGGER_MS default must be 2000 (got %r)' % gh.STAGGER_MS)
    print('  A5: MAX_WIDE=3 / STAGGER_MS=2000 is the default (0 remains an explicit opt-out)')



def test_h1283_a6_prep_slice_flattens_batches():
    """A6 (H1283): prep_slice must take EVERY key of each batch, not only the first."""
    src = os.path.join(HERE, 'h1209', 'prep_slice.py')
    text = open(src, encoding='utf-8').read()
    if '[b[0] for b in' in text:
        fail('A6: prep_slice still takes only the first key of each batch ([b[0] for b in ...])')
    if "for b in m['batches'] for k in b" not in text:
        fail("A6: prep_slice must flatten all batch keys ([k for b in m['batches'] for k in b])")
    print('  A6: prep_slice flattens every batch key')



def test_h1386_d1_medium50_script_size_cap():
    """H1386 D1: the medium50 start-today enabler. (1) prep_slice hoists the shared
    preamble/translation/nws boilerplate into ONE payload-level `prompt_common` instead of
    duplicating ~12 KB into every card's embedded prompt; (2) prep_slice --chunk N splits a
    big manifest into N cap-sized sub-payloads (--keys subsets); (3) inject_payload hard-
    refuses an emitted script over WORKFLOW_SCRIPT_CAP; (4) canonical_audit merges several
    chunk slice_results into one audit. Pre-fix, a 50-card build blew the 512 KB Workflow
    scriptPath cap at submission with no earlier warning."""
    import importlib.util as ilu
    h1209 = os.path.join(HERE, 'h1209')

    def load(name):
        spec = ilu.spec_from_file_location('h1386_' + name, os.path.join(h1209, name + '.py'))
        mod = ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    prep = load('prep_slice')
    tmp = tempfile.mkdtemp()
    boiler = 'B' * 4000
    keys = ['k%02d' % i for i in range(8)]
    man = {
        'model': 'claude-sonnet-5', 'field': 'russian',
        'batches': [[k] for k in keys],
        'prompt': {'preamble': boiler, 'grammar': 'G', 'translation': boiler, 'nws_rule': 'N'},
        'inputs': {k: {'skeleton': 'S-%s {T1}' % k, 'portrait': 'P', 'source_senses': 1,
                       'ls': 0, 'sk': 0} for k in keys},
        'placeholder_maps': {k: ['<x/>'] for k in keys},
    }
    man_path = os.path.join(tmp, 'man.json')
    with open(man_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(man, f)

    # (1) single payload: boilerplate hoisted once, cards carry card_block, not prompt.
    out1 = os.path.join(tmp, 'payload.json')
    prep.write_payloads(man, out1)
    payload = json.load(open(out1, encoding='utf-8'))
    if not (payload.get('prompt_common') or '').startswith(boiler):
        fail('D1: payload must carry the shared boilerplate once as prompt_common')
    for c in payload['cards']:
        if 'prompt' in c:
            fail('D1: per-card prompt still embeds the shared boilerplate')
        if boiler in (c.get('card_block') or ''):
            fail('D1: card_block must not duplicate the shared boilerplate')
    # the reconstructed per-card prompt must be byte-identical to the v2 assembly.
    want = prep.reconstruct_prompt(man, 'k00')
    got = payload['prompt_common'] + payload['cards'][0]['card_block']
    if got != want:
        fail('D1: prompt_common + card_block must equal the exact production prompt')

    # (2) a >=4-way chunk: every key exactly once, chunk files share prompt_common.
    outc = os.path.join(tmp, 'chunked.json')
    chunk_paths = prep.write_payloads(man, outc, chunk=4)
    if len(chunk_paths) != 4:
        fail('D1: --chunk 4 must write 4 sub-payloads, got %d' % len(chunk_paths))
    seen_keys = []
    for p in chunk_paths:
        pc = json.load(open(p, encoding='utf-8'))
        if pc.get('prompt_common') != payload['prompt_common']:
            fail('D1: chunk payload missing the shared prompt_common')
        seen_keys += [c['key1'] for c in pc['cards']]
    if sorted(seen_keys) != sorted(keys) or len(seen_keys) != len(keys):
        fail('D1: chunking must cover every key exactly once, got %r' % seen_keys)
    # --keys subset selection
    outk = os.path.join(tmp, 'subset.json')
    prep.write_payloads(man, outk, keys=['k03', 'k05'])
    pk = json.load(open(outk, encoding='utf-8'))
    if [c['key1'] for c in pk['cards']] != ['k03', 'k05']:
        fail('D1: --keys must subset the payload to exactly the named cards')

    # (3) inject_payload refuses an over-cap emitted script.
    inj = load('inject_payload')
    if not getattr(inj, 'WORKFLOW_SCRIPT_CAP', None):
        fail('D1: inject_payload must define WORKFLOW_SCRIPT_CAP')
    tpl_path = os.path.join(tmp, 'tpl.js')
    with open(tpl_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('const PAYLOAD = /*__PAYLOAD__*/ null /*__END__*/\n')
    big = os.path.join(tmp, 'big.json')
    with open(big, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'cards': [{'key1': 'x', 'card_block': 'Z' * (inj.WORKFLOW_SCRIPT_CAP + 100)}]}, f)
    try:
        inj.inject(tpl_path, big, os.path.join(tmp, 'over.js'))
        fail('D1: inject_payload accepted a script over WORKFLOW_SCRIPT_CAP')
    except SystemExit:
        pass
    inj.inject(tpl_path, out1, os.path.join(tmp, 'ok.js'))   # a small payload still lands

    # (4) canonical_audit merges several chunk slice_results into one result set.
    ca = load('canonical_audit')
    half1 = {'slice': ['k00'], 'results': [{'key1': 'k00', 'would_promote': True}],
             'cards_out': [{'key1': 'k00', 'card': None}]}
    half2 = {'slice': ['k01'], 'results': [{'key1': 'k01', 'would_promote': False}],
             'cards_out': [{'key1': 'k01', 'card': None}]}
    merged = ca.merge_slice_results([half1, half2])
    if merged['slice'] != ['k00', 'k01'] or len(merged['results']) != 2 \
            or len(merged['cards_out']) != 2:
        fail('D1: canonical_audit must merge chunk slice_results into one audit input')



def test_h4529_width_policy_and_pool_split():
    """H4529: width is telemetry-driven, and the two agent pools stay disjoint.

    Three invariants, all offline:

    1. The generator no longer OWNS the width numbers — `width_policy` does, and
       the pinned A5/H1283 defaults are what the harness still starts from.
    2. The policy narrows on the H255 w07 degraded fixture and refuses to widen
       without consecutive measured-healthy load-representative windows, so no
       code path can re-run the Slice-D/H317 unconditional width raise.
    3. `--max-agents` below the key count is refused at generation time with the
       C2_M50 ledger id in the message (H1610/H1618 total-vs-width footgun), and
       the H437 all-heal window gives every card its full per-card heal ceiling.
    """
    import agent_budget
    import gen_opt_harness2 as gen
    import width_policy

    assert gen.MAX_WIDE == width_policy.DEFAULT_MAX_WIDE == 3
    assert gen.STAGGER_MS == width_policy.DEFAULT_STAGGER_MS == 2000
    assert gen.WIDTH_DECISION is None, 'no telemetry => no decision => manifest key absent'

    degraded = {'keys_total': 36, 'null_keys': 31, 'kill_timeouts': 32, 'max_wide': 0}
    narrowed = width_policy.decide_width([degraded], current_max_wide=3)
    assert narrowed.action == 'narrow' and narrowed.max_wide < 3, narrowed

    healthy = {'keys_total': 12, 'null_keys': 0, 'kill_timeouts': 0, 'conn_errors': 0,
               'max_wide': 3}
    assert width_policy.decide_width([healthy] * 6, current_max_wide=3).max_wide == 3, \
        'the adaptive ceiling is the measured A5 default; above it is calibration, not policy'
    assert width_policy.decide_width([healthy], current_max_wide=2).action == 'hold'
    assert width_policy.decide_width([healthy, healthy], current_max_wide=2).action == 'widen'
    assert width_policy.probe_gate_verdict({'concurrency': 1}, 3)[0] == 'NO-GO', \
        'an isolated warm-up cannot clear a 3-wide window (H255 w07)'
    # The ceiling binds on every branch, including a caller that starts ABOVE it — otherwise
    # `hold` parks a width the policy would never have chosen and only a degraded window can
    # undo it (independent-verifier defect, 11-09-2026).
    assert width_policy.decide_width([], current_max_wide=5, ceiling=3).max_wide == 3
    assert width_policy.decide_width([healthy] * 4, current_max_wide=5, ceiling=3).max_wide == 3

    try:
        agent_budget.refuse_starvation_override(50, 1)
    except ValueError as exc:
        assert 'C2_M50_W1_MAX_AGENTS1_2026-07-24' in str(exc)
    else:
        raise AssertionError('--max-agents=1 on a 50-key window must be refused')
    assert agent_budget.refuse_starvation_override(50, 1, force=True).startswith('WARNING')

    all_heal = agent_budget.derive_agent_budget(12, {'k%d' % i: 12 for i in range(12)})
    per_card = agent_budget._per_card_heal_cap(12, 1.5, 3)
    assert all_heal.max_heal_agents == 12 * per_card, 'heal pool must be the SUM of card caps'
    assert all_heal.max_heal_agents - 11 * per_card == per_card, \
        'the last card to heal still has its whole per-card cap (the H437 starvation class)'

    width_policy.selftest()
    agent_budget.selftest()

