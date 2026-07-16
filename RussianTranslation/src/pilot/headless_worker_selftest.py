#!/usr/bin/env python
import json
import subprocess
import sys
import tempfile
import os
from types import SimpleNamespace

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import headless_worker as h
import gen_opt_harness2 as generator


def manifest():
    return {
        'schema': 'pwg.headless_execution_manifest.v1',
        'meta': {'root': 'fixture', 'lang': 'ru', 'selected_keys': ['agni'],
                 'nominal_keymap': None, 'gen_model': 'claude-sonnet-5'},
        'field': 'russian', 'model': 'claude-sonnet-5',
        'prompt': {'preamble': 'P', 'grammar': 'G', 'grammars': {},
                   'translation': 'T', 'nws_rule': ''},
        'output_schema': {'type': 'object'}, 'batches': [['agni']],
        'inputs': {'agni': {'skeleton': '{T1} Feuer', 'portrait': '{}',
                            'ls': 1, 'sk': 0, 'nws': 0}},
        'placeholder_maps': {'agni': ['<ls>RV.</ls>']},
        'fragment_groups': {}, 'fragment_placeholder_maps': {}, 'fragment_tm': {},
        'runtime': {'binary_split': True, 'per_card_heal_budget': True,
                    'per_card_heal_factor': 1.5, 'per_card_heal_headroom': 3,
                    'kill_timeout_no_bisect': True, 'whole_attempts': 2,
                    'fragment_attempts': 3},
        'tm_resolved': {}, 'degenerate_resolved': {}, 'suggestions': {},
        'presplit_keys': [],
    }


def proc(returncode=0, stdout='', stderr=''):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def execute(test_manifest, runner):
    """Use a real, portable executable path while the runner fakes its output."""
    return h.execute(test_manifest, claude=sys.executable, runner=runner)


def success_runner(argv, **kwargs):
    assert '--json-schema' in argv and '--model' in argv
    card = {'key1': 'agni', 'records': [{'grammar': '{T1} m.', 'senses': [
        {'tag': '1', 'german': '{T1} Feuer', 'russian': '{T1} огонь'}]}]}
    wrapper = {'structured_output': {'cards': [card]}}
    return proc(stdout=json.dumps(wrapper))


def main():
    payload, status, code = execute(manifest(), success_runner)
    assert code == 0 and status['classification'] == 'success'
    assert payload['results'][0]['card']['records'][0]['senses'][0]['german'].startswith('<ls>')
    assert payload['results'][0]['card']['records'][0]['grammar'].startswith('<ls>')
    assert payload['meta']['gen_model'] == 'claude-sonnet-5'

    def auth_runner(argv, **kwargs):
        return proc(1, stderr='API Error: 401 Invalid authentication credentials')
    assert execute(manifest(), auth_runner)[2] == h.EXIT_AUTH

    def rate_runner(argv, **kwargs):
        return proc(1, stderr='429 rate limit reset_at=1999999999')
    assert execute(manifest(), rate_runner)[2] == h.EXIT_RATE_LIMIT

    def malformed_runner(argv, **kwargs):
        return proc(stdout='not json')
    payload, status, code = execute(manifest(), malformed_runner)
    assert code == 0 and status['classification'] == 'completed_with_residuals'

    def missing_runner(argv, **kwargs):
        return proc(stdout=json.dumps({'structured_output': {'cards': []}}))
    payload, status, code = execute(manifest(), missing_runner)
    assert code == 0 and payload['summary']['null_keys'] == ['agni']

    def timeout_runner(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, 1)
    payload, status, code = execute(manifest(), timeout_runner)
    assert code == 0 and payload['summary']['kill_timeouts'] == 1

    presplit = manifest()
    presplit['batches'] = []
    presplit['presplit_keys'] = ['agni']
    presplit['inputs']['agni'].update({'skeleton': '{T1}{T2}', 'ls': 2})
    presplit['fragment_groups'] = {'agni': [[
        {'skeleton': '{T1}', 'ls': 1, 'sk': 0, 'fsha': 'a', 'si': 1},
        {'skeleton': '{T1}', 'ls': 1, 'sk': 0, 'fsha': 'b', 'si': 2},
    ]]}
    presplit['fragment_placeholder_maps'] = {
        'agni': [[['<ls>A</ls>'], ['<ls>B</ls>']]]}
    presplit['placeholder_maps']['agni'] = ['<ls>A</ls>', '<ls>B</ls>']

    def fragment_runner(argv, **kwargs):
        cards = []
        for index in (0, 1):
            key = 'agni_f%d' % index
            if key in kwargs['input']:
                cards.append({'key1': key, 'records': [{'senses': [{
                    'tag': str(index + 1), 'german': '{T1}',
                    'russian': '{T1}'}]}]})
        return proc(stdout=json.dumps({'structured_output': {'cards': cards}}))

    payload, status, code = execute(presplit, fragment_runner)
    assert code == 0 and status['classification'] == 'success'
    card = payload['results'][0]['card']
    assert payload['summary']['presplit'] == 1 and payload['summary']['healed'] == 1
    assert not card.get('partial') and len(card['records'][0]['senses']) == 2

    calls = {'n': 0}
    def partial_runner(argv, **kwargs):
        calls['n'] += 1
        card = {'key1': 'agni_f0', 'records': [{'senses': [
            {'tag': '1', 'german': '{T1}', 'russian': '{T1}'}]}]}
        return proc(stdout=json.dumps({'structured_output': {'cards': [card]}}))
    payload, _status, code = execute(presplit, partial_runner)
    assert code == 0 and payload['results'][0]['card']['partial']
    assert payload['results'][0]['card']['missing_fragments']

    def fragment_timeout(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, 1)
    payload, _status, code = execute(presplit, fragment_timeout)
    assert code == 0 and payload['summary']['null'] == 1
    assert payload['summary']['heal_agents_spent'] == 1  # timeout-no-bisect

    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, 'fixture.raw.txt')
        portrait = os.path.join(td, 'fixture.portrait.json')
        with open(raw, 'w', encoding='utf-8') as f:
            f.write('Feuer')
        with open(portrait, 'w', encoding='utf-8') as f:
            json.dump({'key1': 'agni'}, f)
        original = generator.input_paths
        generator.input_paths = lambda key: (raw, portrait)
        try:
            js, batches, built = generator.build(
                'fixture', ['agni'], None, 12000, nominal=True, grammar_on=False,
                tm_path=None, suggest_tm_path=None, return_manifest=True)
        finally:
            generator.input_paths = original
        assert built['schema'] == 'pwg.headless_execution_manifest.v1'
        assert built['batches'] == batches and built['model'] == 'claude-sonnet-5'
        assert json.dumps(built['inputs'], ensure_ascii=True) in js
        start = js.index('function restoreCard(card, k)')
        end = js.index('// Per-card grammar', start)
        restore_card_js = js[start:end]
        # RESTORE_SPEC is injected from the same constant the harness interpolates (C-01), not
        # re-typed here: the whole point of the constant is that no second list exists. The
        # slice above starts at `function restoreCard`, so the const declared above it is not
        # carried in -- supply it exactly as the real harness would.
        import card_fields
        node_script = r"""
const PH = {agni: ['<lex>m.</lex>']}
const restore = (t, ph) => (t || '').replace(/\{T(\d+)\}/g, (_m, n) => ph[Number(n)-1])
const RESTORE_SPEC = %s
%s
const card = {iast: '{T1}', records: [{h: '{T1}', grammar: '{T1}', senses: [
  {tag: '{T1}', german: '{T1}', russian: '{T1}', differentia: '{T1}'}]}]}
console.log(JSON.stringify(restoreCard(card, 'agni')))
""" % (card_fields.js_restore_spec('russian'), restore_card_js)
        node = subprocess.run(['node', '-e', node_script], capture_output=True,
                              text=True, encoding='utf-8')
        assert node.returncode == 0, node.stderr
        restored = json.loads(node.stdout)
        rec = restored['records'][0]
        sense = rec['senses'][0]
        assert rec['grammar'] == '<lex>m.</lex>'
        assert sense['german'] == '<lex>m.</lex>'
        # C-01: the JS lane must unmask EVERY field the promote path reads, not just three.
        # card.iast / record.h / sense.tag / sense.differentia used to survive as raw {Tn} and
        # were promoted verbatim -- 670 store rows, 223 of them a {Tn} headword.
        for where, value in (('card.iast', restored['iast']), ('record.h', rec['h']),
                             ('sense.tag', sense['tag']),
                             ('sense.differentia', sense['differentia']),
                             ('sense.russian', sense['russian'])):
            assert value == '<lex>m.</lex>', '%s left unrestored by the JS lane: %r' % (where, value)

    # D-A (H818 Windows acceptance): the launcher resolver must bypass the Windows .cmd
    # batch shim (cmd.exe corrupts the --json-schema arg) and pass native/POSIX through.
    _name, _which, _glob = h.os.name, h.shutil.which, h.glob.glob
    try:
        h.os.name = 'posix'
        assert h.claude_argv_prefix('/usr/bin/claude') == ['/usr/bin/claude']
        h.os.name = 'nt'
        assert h.claude_argv_prefix(r'C:\p\claude.exe') == [r'C:\p\claude.exe']
        h.shutil.which = lambda _n: r'C:\node.exe'
        h.glob.glob = lambda pat: ([r'C:\p\node_modules\@anthropic-ai\claude-code\cli-wrapper.cjs']
                                   if 'cli*.cjs' in pat else [])
        assert h.claude_argv_prefix(r'C:\p\claude.cmd') == [
            r'C:\node.exe', r'C:\p\node_modules\@anthropic-ai\claude-code\cli-wrapper.cjs']
        h.shutil.which = lambda _n: None
        try:
            h.claude_argv_prefix(r'C:\p\claude.cmd')
        except FileNotFoundError:
            pass
        else:
            raise AssertionError('unresolved .cmd shim must fail closed')
    finally:
        h.os.name, h.shutil.which, h.glob.glob = _name, _which, _glob
    print('  D-A claude_argv_prefix: posix/.exe passthrough, .cmd->node-direct, unresolved shim refused')

    # D-J: a timeout must terminate the ENTIRE process tree, not just the immediate child. The
    # Windows claude launcher (node cli-wrapper.cjs) spawnSync's the native binary as a CHILD, so
    # killing only the node process orphans it (the multi-minute 'hang'). Mirror the real
    # python -> node(wrapper) -> native-binary depth with parent -> child -> GRANDCHILD: each level
    # records its PID and writes a '.done<n>' marker ONLY if it survives its sleep. A correct
    # tree-kill leaves NONE of the three PIDs alive and NONE of the three markers written.
    import time as _time

    def _alive(pid):
        if os.name == 'nt':
            out = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid, '/NH'],
                                  capture_output=True, text=True,
                                  creationflags=h.windows_hidden_flags()).stdout or ''   # no flicker
            return str(pid) in out.split()
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    with tempfile.TemporaryDirectory() as td:
        mk = os.path.join(td, 'm')
        grand = ('import time,sys,os;'
                 'open(sys.argv[1]+".pid3","w").write(str(os.getpid()));'
                 'time.sleep(6);open(sys.argv[1]+".done3","w").write("1")')
        child = ('import subprocess,sys,os,time;'
                 'open(sys.argv[1]+".pid2","w").write(str(os.getpid()));'
                 'subprocess.Popen([sys.executable,"-c",%r,sys.argv[1]]);'
                 'time.sleep(30)') % grand
        parent = ('import subprocess,sys,os,time;'
                  'open(sys.argv[1]+".pid1","w").write(str(os.getpid()));'
                  'subprocess.Popen([sys.executable,"-c",%r,sys.argv[1]]);'
                  'time.sleep(30)') % child
        t0 = _time.monotonic()
        try:
            h.run_tree_kill([sys.executable, '-c', parent, mk], timeout=3, capture_output=True)
            assert False, 'expected TimeoutExpired'
        except subprocess.TimeoutExpired:
            pass
        assert _time.monotonic() - t0 < 25, 'tree kill did not bound the timeout'
        for _ in range(60):     # wait for the full 3-level tree to have recorded its PIDs
            if all(os.path.exists('%s.pid%d' % (mk, i)) for i in (1, 2, 3)):
                break
            _time.sleep(0.1)
        _time.sleep(5)          # > the grandchild's 6 s sleep offset: an orphan would have written .done3
        for i in (1, 2, 3):
            assert os.path.exists('%s.pid%d' % (mk, i)), 'level %d never started (test setup broken)' % i
        pids = [int(open('%s.pid%d' % (mk, i)).read()) for i in (1, 2, 3)]
        survived_marker = [i for i in (1, 2, 3) if os.path.exists('%s.done%d' % (mk, i))]
        assert not survived_marker, 'level(s) %s SURVIVED the tree kill (orphaned)' % survived_marker
        still_alive = [p for p in pids if _alive(p)]
        assert not still_alive, 'tree PID(s) still alive after kill (orphaned): %s' % still_alive
    print('  D-J tree-kill: parent->child->grandchild all gone (no orphan); timeout bounded + raised once')
    print('headless_worker_selftest: PASS')


if __name__ == '__main__':
    main()
