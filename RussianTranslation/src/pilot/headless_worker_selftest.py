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
        'tm_resolved': {}, 'degenerate_resolved': {}, 'suggestions': {},
        'presplit_keys': [],
    }


def proc(returncode=0, stdout='', stderr=''):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def success_runner(argv, **kwargs):
    assert '--json-schema' in argv and '--model' in argv
    card = {'key1': 'agni', 'records': [{'senses': [
        {'tag': '1', 'german': '{T1} Feuer', 'russian': '{T1} огонь'}]}]}
    wrapper = {'structured_output': {'cards': [card]}}
    return proc(stdout=json.dumps(wrapper))


def main():
    payload, status, code = h.execute(manifest(), runner=success_runner)
    assert code == 0 and status['classification'] == 'success'
    assert payload['results'][0]['card']['records'][0]['senses'][0]['german'].startswith('<ls>')
    assert payload['meta']['gen_model'] == 'claude-sonnet-5'

    def auth_runner(argv, **kwargs):
        return proc(1, stderr='API Error: 401 Invalid authentication credentials')
    assert h.execute(manifest(), runner=auth_runner)[2] == h.EXIT_AUTH

    def rate_runner(argv, **kwargs):
        return proc(1, stderr='429 rate limit reset_at=1999999999')
    assert h.execute(manifest(), runner=rate_runner)[2] == h.EXIT_RATE_LIMIT

    def malformed_runner(argv, **kwargs):
        return proc(stdout='not json')
    assert h.execute(manifest(), runner=malformed_runner)[2] == h.EXIT_MALFORMED

    def missing_runner(argv, **kwargs):
        return proc(stdout=json.dumps({'structured_output': {'cards': []}}))
    payload, status, code = h.execute(manifest(), runner=missing_runner)
    assert code == h.EXIT_CONTENT and payload['summary']['null_keys'] == ['agni']

    def timeout_runner(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, 1)
    assert h.execute(manifest(), runner=timeout_runner)[2] == h.EXIT_TIMEOUT

    bad = manifest(); bad['presplit_keys'] = ['agni']
    try:
        h.execute(bad, runner=success_runner)
    except ValueError as exc:
        assert 'presplit' in str(exc)
    else:
        raise AssertionError('presplit manifest was not refused')

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
    print('headless_worker_selftest: PASS')


if __name__ == '__main__':
    main()
