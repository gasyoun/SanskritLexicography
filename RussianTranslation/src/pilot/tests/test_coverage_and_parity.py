"""test_coverage_and_parity — split from window_selftest.py by H7241.

Pytest-collectable subject module of the frequency-window guardrail suite. The test bodies
are the original ones, moved verbatim; `_support.py` carries the fixtures, the
production-isolation guard and the `HERE`/`SRC`/`ROOT` paths they resolve against.

Run:  python -m pytest src/pilot/tests/test_coverage_and_parity.py -q
      python src/pilot/window_selftest.py       # legacy runner, same result
"""

from _support import *  # noqa: F401,F403  -- fixtures, paths, repo imports


def test_lang_parity_ledger_complete():
    """LANG_PARITY.md's ledger must have a verdict for every entry (SHARED /
    INTENTIONAL-DIVERGENCE with a note / GAP with a tracking ref), and no tracked
    file may have drifted since its entry was last verified. See LANG_PARITY.md."""
    import lang_parity_check
    entries, _, _ = lang_parity_check.load_ledger()
    violations = lang_parity_check.check(entries)
    if violations:
        fail('LANG_PARITY.md has %d unresolved parity violation(s):\n  %s'
             % (len(violations), '\n  '.join(violations)))



def test_lang_parity_hash_crlf_independent():
    """file_sha256() must normalize CRLF->LF so verified_sha256 snapshots match the git-blob
    content regardless of core.autocrlf on the checkout OS (Windows disk bytes carry CRLF;
    Linux/CI checkouts and git blobs carry LF) — see LANG_PARITY.md fix, 2026-07-04."""
    import tempfile
    import lang_parity_check
    with tempfile.TemporaryDirectory() as tmp:
        lf_path = os.path.join(tmp, 'lf.txt')
        crlf_path = os.path.join(tmp, 'crlf.txt')
        with open(lf_path, 'wb') as f:
            f.write(b'line one\nline two\n')
        with open(crlf_path, 'wb') as f:
            f.write(b'line one\r\nline two\r\n')
        old_root = lang_parity_check.REPO_ROOT
        lang_parity_check.REPO_ROOT = tmp
        try:
            lf_hash = lang_parity_check.file_sha256('lf.txt')
            crlf_hash = lang_parity_check.file_sha256('crlf.txt')
        finally:
            lang_parity_check.REPO_ROOT = old_root
        if lf_hash != crlf_hash:
            fail('file_sha256 is not CRLF/LF-independent: %s != %s' % (lf_hash, crlf_hash))



def test_lang_parity_ledger_refuses_duplicate_keys():
    """H5259 follow-up (22-09-2026): recovered PR #2305 replayed an old re-hash hunk on a newer
    base and appended 7 duplicate keys with stale hashes inside one entry's verified_sha256.
    Plain json.loads keeps the LAST copy silently, so the checker reported 8 misleading
    "changed since last parity verification" drifts instead of the cause. The loader must
    refuse a repeated key at any level, naming the entry and the key as a merge/replay
    artifact, and --update-hash must refuse too -- leaving the file byte-identical rather
    than silently deduping it on the rewrite."""
    import tempfile
    import lang_parity_check as lpc
    good, stale = 'a' * 64, 'b' * 64
    entry = ('[{"id": "dup_entry", "verdict": "SHARED", "files": ["x.py"], '
             '"verified_sha256": {%s}}]')
    with tempfile.TemporaryDirectory() as tmp:
        md = os.path.join(tmp, 'LANG_PARITY.md')

        def write(block):
            with open(md, 'w', encoding='utf-8', newline='\n') as f:
                f.write('# ledger\n\n```json lang_parity_ledger\n%s\n```\n' % block)

        write(entry % ('"x.py": "%s"' % good))                  # control: clean ledger loads
        if lpc.load_ledger(md)[0][0]['verified_sha256'] != {'x.py': good}:
            fail('a clean ledger no longer loads through the strict parser')
        write(entry % ('"x.py": "%s", "x.py": "%s"' % (good, stale)))
        before = open(md, 'rb').read()
        for label, call in (('load_ledger', lambda: lpc.load_ledger(md)),
                            ('--update-hash', lambda: lpc.update_hash('dup_entry', path=md))):
            try:
                call()
            except lpc.DuplicateKeyError as exc:
                msg = str(exc)
            else:
                fail('%s accepted a repeated verified_sha256 key (kept the stale last copy)'
                     % label)
            for needle in ("entry 'dup_entry'", "key 'x.py'", 'verified_sha256', 'merge/replay'):
                if needle not in msg:
                    fail('%s refusal does not name %s: %s' % (label, needle, msg))
        if open(md, 'rb').read() != before:
            fail('--update-hash rewrote a ledger it refused (silent dedupe)')
    # Any level: an entry's own field, and the lang_parity_coverage `exempt` map.
    for raw, needle in (('[{"id": "e1", "verdict": "SHARED", "verdict": "GAP"}]',
                         "entry 'e1': key 'verdict' repeated in its top level"),
                        ('{"exempt": {"src/a.py": "r1", "src/a.py": "r2"}}',
                         "key 'src/a.py' repeated in exempt")):
        try:
            lpc.parse_ledger_json(raw)
        except lpc.DuplicateKeyError as exc:
            if needle not in str(exc):
                fail('duplicate-key refusal does not say %r: %s' % (needle, exc))
        else:
            fail('parse_ledger_json accepted a repeated key: %s' % raw)



def test_lang_parity_ledger_refuses_duplicate_entry_ids():
    """H5259 verifier gap (22-09-2026): the duplicate-KEY refusal cannot see a replay that
    re-appends a WHOLE entry -- two list items with one id and no key repeated inside either.
    check() would evaluate both copies (the stale one reads as drift) and --update-hash would
    re-stamp every match, so the duplicate would persist silently. The loader, --update-hash
    and parity_restamp must refuse it naming the id as a merge/replay artifact; a second
    ```json lang_parity_ledger fence (only the first is ever read) must be refused too."""
    import tempfile
    import lang_parity_check as lpc
    import parity_restamp
    one = ('{"id": "%s", "verdict": "SHARED", "files": ["x.py"], '
           '"verified_sha256": {"x.py": "%s"}}')
    clean = '[%s, %s]' % (one % ('e_a', 'a' * 64), one % ('e_b', 'a' * 64))
    dup = '[%s, %s, %s]' % (one % ('e_a', 'a' * 64), one % ('e_b', 'a' * 64),
                            one % ('e_a', 'b' * 64))
    fence = '```json lang_parity_ledger\n%s\n```\n'
    with tempfile.TemporaryDirectory() as tmp:
        md = os.path.join(tmp, 'LANG_PARITY.md')

        def write(body):
            with open(md, 'w', encoding='utf-8', newline='\n') as f:
                f.write('# ledger\n\n' + body)

        write(fence % clean)                                    # control: distinct ids load
        if [e['id'] for e in lpc.load_ledger(md)[0]] != ['e_a', 'e_b']:
            fail('a ledger with distinct entry ids no longer loads')
        for label, body, needles in (
                ('duplicate entry id', fence % dup,
                 ("entry id 'e_a' repeated at list positions 0, 2", 'merge/replay')),
                ('second ledger fence', fence % clean + '\n' + fence % clean,
                 ('2 ```json lang_parity_ledger fenced blocks', 'merge/replay'))):
            write(body)
            before = open(md, 'rb').read()
            calls = [('load_ledger', lambda: lpc.load_ledger(md)),
                     ('--update-hash', lambda: lpc.update_hash('e_a', path=md))]
            old_ledger = parity_restamp.LEDGER
            parity_restamp.LEDGER = type(old_ledger)(md)
            calls.append(('parity_restamp.load_ledger', parity_restamp.load_ledger))
            try:
                for name, call in calls:
                    try:
                        call()
                    except lpc.DuplicateKeyError as exc:
                        msg = str(exc)
                    else:
                        fail('%s accepted a %s' % (name, label))
                    for needle in needles:
                        if needle not in msg:
                            fail('%s refusal of a %s does not say %r: %s'
                                 % (name, label, needle, msg))
            finally:
                parity_restamp.LEDGER = old_ledger
            if open(md, 'rb').read() != before:
                fail('a refused %s ledger was rewritten' % label)
    # The id check is ledger-only: the coverage block is a map, not an entry list.
    if lpc.parse_ledger_json('{"exempt": {"a": "r"}}', block='lang_parity_coverage') != {
            'exempt': {'a': 'r'}}:
        fail('the coverage block must not go through the entry-id check')



def test_ru_coverage_denominator_not_silently_exempt():
    """FL3: a corrupt EN denominator must FAIL the coverage gate (not be silently skipped),
    and a RU root with no denominator must be surfaced as UNVERIFIABLE (the gam 6/127 blind
    spot), never exempted."""
    import io
    import contextlib
    import ru_coverage
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, 'wf_output.en.aa.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps({'meta': {'selected_keys': ['aa~~h0_00_pwg00']}}))
        with open(os.path.join(tmp, 'wf_output.en.bb.json'), 'w', encoding='utf-8') as f:
            f.write('{ broken json')
        store = os.path.join(tmp, 'store.jsonl')
        with open(store, 'w', encoding='utf-8') as f:
            f.write(json.dumps({'key1': 'aa', 'subcard': 'aa~~h0_00_pwg00'}) + '\n')
            f.write(json.dumps({'key1': 'cc', 'subcard': 'cc~~h0_00_pwg00'}) + '\n')
        old_repo, old_store, old_argv = ru_coverage.REPO, ru_coverage.RU_STORE, sys.argv
        ru_coverage.REPO, ru_coverage.RU_STORE = tmp, store
        try:
            intended, corrupt = ru_coverage.intended_by_root()
            if not any(r == 'bb' for r, _ in corrupt):
                fail('corrupt EN denominator not detected')
            if 'aa' not in intended:
                fail('valid EN denominator dropped')
            sys.argv = ['ru_coverage']
            buf = io.StringIO()
            rc = 0
            try:
                with contextlib.redirect_stdout(buf):
                    ru_coverage.main()
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else 1
            out = buf.getvalue()
            if rc != 1:
                fail('ru_coverage did not FAIL on a corrupt EN denominator (silent exemption)')
            if 'UNVERIFIABLE' not in out:
                fail('a RU root with no EN denominator was not surfaced as UNVERIFIABLE')
        finally:
            ru_coverage.REPO, ru_coverage.RU_STORE, sys.argv = old_repo, old_store, old_argv



def test_coverage_gate_multi_layer_and_presplit():
    """audit_coverage.raw_markers() must not mistake <div n="p"> (a STRUCTURAL prefix/
    secondary-conjugation divider elsewhere in this codebase -- root_units.py,
    scale_preflight.py's _DIVP, verify_root_glue.py) for a numbered sense boundary when a
    sub-card bundles several independent '=== LAYER: ... ===' blocks (PW/SCH/PWKVN addenda,
    e.g. gam~~h0_zz_pw04: 3 layers, 5 raw '<div n=' tags, all cross-reference continuations
    -> the correct count is 3, one per layer, not 5). Also: a presplit/fragment-reassembled
    card's granular per-fragment row count must skip the LOW/OVER thresholds entirely (its
    row count is not comparable to a coarse raw marker count)."""
    three_layer_raw = (
        '=== LAYER: PW ===\n\n'
        '√gam mit aByud 1〉 aByudgata aufgegangen (Sonne) <ls>X. 1</ls>.\n\n'
        '=== LAYER: PW ===\n\n'
        '√gam mit aBi Caus. auch zukommen lassen <ls>Y. 2</ls>.\n'
        '<div n="p">— Mit nis Caus. auch verlieren <ls>Z. 3</ls>.\n\n'
        '=== LAYER: PW ===\n\n'
        '√gam mit aBi Caus. II. 5.\n'
        '<div n="p">— Mit A II. Agamya so v. a. fuer <ls>W. 4</ls>.\n'
        '<div n="p">— Mit aByud II. 3.\n'
        '<div n="p">— Mit nis Caus. II. 5.\n'
        '<div n="p">— Mit upanis hinausgehen zu <ls>V. 5</ls>.\n'
    )
    bodies = audit_coverage.layer_bodies(three_layer_raw)
    if len(bodies) != 3:
        fail('expected 3 layer blocks, got %d' % len(bodies))
    counts = [audit_coverage.layer_sense_count(b) for b in bodies]
    if counts != [1, 1, 1]:
        fail('layer_sense_count must floor a pure-cross-reference layer at 1 sense, not count '
             'every <div n="p"> continuation: got %r' % counts)

    with tempfile.TemporaryDirectory() as tmp:
        in_dir = os.path.join(tmp, 'pilot', 'input')
        os.makedirs(in_dir)
        with open(os.path.join(in_dir, 'zz~~h0_zz_pw04.raw.txt'), 'w', encoding='utf-8') as f:
            f.write(three_layer_raw)
        with open(os.path.join(in_dir, 'zz~~presplit_card.raw.txt'), 'w', encoding='utf-8') as f:
            f.write('=== LAYER: PW ===\n\n√gam 1〉 aufgegangen <ls>X. 1</ls>.\n')
        old_in = audit_coverage.IN
        audit_coverage.IN = in_dir
        try:
            rm = audit_coverage.raw_markers('zz~~h0_zz_pw04')
            if rm != 3:
                fail('multi-layer raw_markers must count 1 sense per addenda layer (3), got %r'
                     % rm)

            wf = os.path.join(tmp, 'wf_output.json')
            with open(wf, 'w', encoding='utf-8') as f:
                json.dump({'results': [
                    {'key': 'zz~~h0_zz_pw04', 'presplit': False,
                     'card': {'records': [{'senses': [{}, {}, {}]}]}},
                    {'key': 'zz~~presplit_card', 'presplit': True,
                     'card': {'records': [{'senses': [{}] * 20}]}},
                ]}, f)
            import io, contextlib
            old_argv = sys.argv
            sys.argv = ['audit_coverage', wf]
            buf = io.StringIO()
            rc = 0
            try:
                with contextlib.redirect_stdout(buf):
                    audit_coverage.main()
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else 1
            finally:
                sys.argv = old_argv
            out = buf.getvalue()
            if rc != 0:
                fail('multi-layer addenda card + presplit card must both pass: %s' % out)
            if 'COVERAGE-LOW' in out or 'COVERAGE-OVER' in out:
                fail('coverage gate still flagged a multi-layer/presplit card: %s' % out)
            if 'presplit' not in out:
                fail('presplit card must be labeled as such, not silently ok: %s' % out)
        finally:
            audit_coverage.IN = old_in



def test_en_residual_coverage_complete():
    """FL4: EN 'done' means coverage-complete, not '>=1 English sense'. A card with 1 of 2 senses
    translated is a residual (its 1 untranslated sense must not be hidden); a fully-translated card
    is done; a null/empty card is never done. The rule now lives in the shared card_coverage kernel
    (H1425 W1) — this test pins the EN consumer path (field='english')."""
    from card_coverage import card_done, slot_coverage
    partial = {'records': [{'senses': [{'german': 'a', 'english': 'x'}, {'german': 'b'}]}]}
    if slot_coverage(partial, 'english') != (1, 2):
        fail('slot_coverage miscounted the partial card')
    if card_done(partial, 'english'):
        fail('a 1/2-sense card must NOT count as done (the FL4 1/40 bug)')
    full = {'records': [{'senses': [{'german': 'a', 'english': 'x'},
                                    {'german': 'b', 'english': 'y'}]}]}
    if not card_done(full, 'english'):
        fail('a fully-translated card must count as done')
    if card_done(None, 'english') or card_done({'records': []}, 'english'):
        fail('a null/empty card must never count as done')



def test_en_split_triage_keeps_missing_input():
    """FL4: a residual (null) card whose source input file is absent must stay VISIBLE in
    triage with a missing_input marker, not be silently skipped."""
    import en_split_triage as est
    with tempfile.TemporaryDirectory() as tmp:
        wf = {'meta': {'selected_keys': ['aa~~h0_00', 'bb~~h0_00']},
              'results': [
                  {'key': 'aa~~h0_00', 'card': {'records': [
                      {'senses': [{'german': 'g', 'english': 'e'}]}]}},
                  {'key': 'bb~~h0_00', 'card': None}]}
        with open(os.path.join(tmp, 'wf_output.en.zz.json'), 'w', encoding='utf-8') as f:
            json.dump(wf, f, ensure_ascii=False)
        aa_raw = os.path.join(tmp, 'aa.raw.txt')
        with open(aa_raw, 'w', encoding='utf-8') as f:
            f.write('<ls>x</ls> Wasser')

        def fake_paths(key):
            if key == 'aa~~h0_00':
                return aa_raw, aa_raw + '.portrait'
            return os.path.join(tmp, 'nope_%s.txt' % key), ''

        old_repo, old_ip = est.REPO, est.input_paths
        est.REPO, est.input_paths = tmp, fake_paths
        try:
            rows = est.scan()
        finally:
            est.REPO, est.input_paths = old_repo, old_ip
    by = {k: f for _r, k, f, _p in rows}
    if 'bb~~h0_00' not in by:
        fail('missing-input null card was dropped from triage (FL4)')
    if not by['bb~~h0_00'].get('missing_input'):
        fail('missing-input residual not marked missing_input')
    if by['aa~~h0_00'].get('missing_input'):
        fail('a present-input card wrongly marked missing_input')



def test_corpus_gate_evidence_and_db_markers():
    """H321 item #4 (FL7): corpus_gate must distinguish 'evidence not built/available'
    from 'consulted and empty' — an absent evidence source or a DB failure previously
    degraded to a bare [] indistinguishable from a genuinely uncovered headword."""
    import corpus_gate as cg
    saved_db = cg.CORPUS_DB
    saved_present = set(cg.SOURCES_PRESENT)
    try:
        cg.SOURCES_PRESENT.clear()
        cg.CORPUS_DB = os.path.join(tempfile.gettempdir(), 'zz_no_such_corpus.db')
        if cg.evidence_status() != 'evidence_unavailable':
            fail('no INDEP source loaded must report evidence_unavailable, not ok')
        ex, st = cg.corpus_examples_with_status('agni')
        if ex != [] or st != 'db_absent':
            fail('absent DB must yield ([], "db_absent"), got (%r, %r)' % (ex, st))
        card = cg.build_card({}, 'agni', None, 'огонь')
        if card.get('evidence_status') != 'evidence_unavailable' or card.get('corpus_status') != 'db_absent':
            fail('build_card must surface evidence_status + corpus_status markers')
        # back-compat: corpus_examples still returns a bare list.
        if cg.corpus_examples('agni') != []:
            fail('corpus_examples must stay a list-returning wrapper')
    finally:
        cg.CORPUS_DB = saved_db
        cg.SOURCES_PRESENT.clear()
        cg.SOURCES_PRESENT.update(saved_present)



def test_lang_parity_coverage():
    """Parity-coverage guard: no language-aware pipeline file may escape the LANG_PARITY ledger
    unclassified — the hole the C1–C9 EN findings grew in (a new `*_en.py` / `--lang` gate that is
    neither tracked nor exempt). (1) the real repo must be coverage-clean; (2) the pure set logic
    must flag an untracked candidate and clear it once tracked OR exempt; (3) exempt hygiene."""
    import lang_parity_check as lp
    entries, _, _ = lp.load_ledger()
    viol = lp.coverage_check(entries, lp.load_coverage())
    if viol:
        fail('parity-coverage guard is not clean:\n  ' + '\n  '.join(viol))
    # pure-logic escape / clear
    if not lp.coverage_violations({'src/pilot/new_en.py'}, set(), {}):
        fail('coverage_violations must flag an untracked language-aware candidate')
    if lp.coverage_violations({'src/pilot/new_en.py'}, {'src/pilot/new_en.py'}, {}):
        fail('a ledger-tracked candidate must not be flagged')
    if lp.coverage_violations({'src/pilot/new_en.py'}, set(), {'src/pilot/new_en.py': 'a reason'}):
        fail('an exempt candidate must not be flagged')
    # exempt hygiene: empty reason + both-tracked-and-exempt are violations
    if not lp.coverage_violations(set(), set(), {'src/x.py': ''}):
        fail('an empty exempt reason must be a violation')
    if not lp.coverage_violations({'src/x.py'}, {'src/x.py'}, {'src/x.py': 'r'}):
        fail('a file both ledger-tracked and exempt must be a violation')
    # detector sanity: the known EN reimplementation must be seen as language-aware
    if 'src/pilot/audit_window_en.py' not in set(lp.candidate_files()):
        fail('candidate_files must detect audit_window_en.py as a language-aware candidate')

