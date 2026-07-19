#!/usr/bin/env python
"""Smoke tests for frequency-window architecture guardrails.

This script intentionally uses ignored runtime files and temporary directories
only. It does not require a fresh Max run.

  python src/pilot/window_selftest.py
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

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(SRC)
OUT = os.path.join(HERE, 'output')

if HERE not in sys.path:
    sys.path.insert(0, HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

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
                            'card': {
                                'key1': 'han',
                                'iast': 'han',
                                'records': [{'h': None, 'senses': [{
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


def test_workflow_payload_nested():
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        path = f.name
        json.dump({'outer': {'meta': {'root': 'sTA'}, 'results': [
            {'key': 'k1', 'card': {'ok': True}},
            {'key': 'k2', 'card': None},
        ]}}, f)
    try:
        _payload, meta, _results, keys, nulls = workflow_payload(path)
    finally:
        os.remove(path)
    if meta.get('root') != 'sTA' or keys != ['k1', 'k2'] or nulls != ['k2']:
        fail('workflow_payload nested extraction failed')


def test_harness_scope_and_tools():
    meta = harness_meta()  # canonical opt2 harness (window_common.OPT_HARNESS)
    if not meta.get('ok'):
        if meta.get('error') == 'missing harness':
            return  # ignored runtime artifact absent in a fresh worktree
        fail('optimized harness missing or invalid: %s' % meta.get('error'))
    text = open(meta['path'], encoding='utf-8').read()
    # Every schema-bearing model call must carry tools: [] (the yuj file-read-blowup guard).
    # Since the kill gate (H155 follow-up) the call sites go through agentKill(prompt, {..}),
    # not a bare agent(prompt, {..}); count both so the guard still holds whichever is used.
    agent_calls = text.count('agentKill(prompt, {') + text.count('agent(prompt, {')
    tool_guards = text.count('tools: []')
    if agent_calls != tool_guards or not tool_guards:
        fail('optimized harness tools guard mismatch: %d agent calls, %d guards' %
             (agent_calls, tool_guards))
    is_nominal = bool((meta.get('meta') or {}).get('nominal'))
    current = current_root_provenance(meta.get('root'), meta.get('selected_keys'),
                                      nominal=is_nominal)
    if not current.get('ok'):
        if 'no rootmap' in (current.get('error') or ''):
            return  # live ignored input/rootmap artifacts are absent in this checkout
        fail('current root provenance unavailable: %s' % current.get('error'))
    if not is_nominal and meta.get('rootmap_sha256') != current.get('rootmap_sha256'):
        fail('optimized harness rootmap hash does not match current rootmap')
    if is_nominal and meta.get('rootmap_sha256') is not None:
        fail('nominal optimized harness must not pretend to have a rootmap hash')
    if meta.get('selected_keys') != current.get('selected_keys'):
        fail('optimized harness selected_keys do not match current rootmap selection')


def test_stale_check_key_order_independent():
    """stale_check must compare workflow result-key order against meta.selected_keys as a
    SET, not a positional list — the harness assembles results TM-lane-first then
    DEGENERATE-lane then per-batch-completion order, which never matches the rootmap's
    declared order even when every key is present exactly once."""
    meta = harness_meta()
    if not meta.get('ok'):
        if meta.get('error') == 'missing harness':
            return  # ignored runtime artifact absent in a fresh worktree
        fail('optimized harness missing or invalid: %s' % meta.get('error'))
    root = meta.get('root')
    is_nominal = bool((meta.get('meta') or {}).get('nominal'))
    current = current_root_provenance(root, meta.get('selected_keys'), nominal=is_nominal)
    if not current.get('ok'):
        if 'no rootmap' in (current.get('error') or ''):
            return  # live ignored input/rootmap artifacts are absent in this checkout
        fail('current root provenance unavailable: %s' % current.get('error'))
    workflow_meta = {
        'root': root,
        'safe_root': current['safe_root'],
        'rootmap_sha256': current['rootmap_sha256'],
        'selected_keys': current['selected_keys'],
        'input_hashes': current['input_hashes'],
        'nominal': is_nominal,
    }
    reordered_keys = list(reversed(current['selected_keys']))
    check = stale_check(root, workflow_meta, reordered_keys)
    if any('do not match' in err for err in check.get('errors') or []):
        fail('stale_check flagged reordered-but-identical key set as a mismatch')
    if check['stale']:
        fail('stale_check treated an order-only difference as stale: %s' % check.get('errors'))


def test_nominal_provenance_without_rootmap():
    """Nominal windows use selected headword keys directly; lack of a rootmap is expected."""
    import gen_opt_harness2 as gh
    from window_common import input_paths
    keys = ['_selftest_nominal_prov']
    rp, pp = input_paths(keys[0])
    old_raw = open(rp, encoding='utf-8').read() if os.path.exists(rp) else None
    old_portrait = open(pp, encoding='utf-8').read() if os.path.exists(pp) else None
    try:
        os.makedirs(os.path.dirname(rp), exist_ok=True)
        with open(rp, 'w', encoding='utf-8') as f:
            f.write('<L>1<pc>1<k1>a<k2>a<h>1\n<body>{#a#} x</body>\n')
        with open(pp, 'w', encoding='utf-8') as f:
            json.dump({'key1': 'a', 'lex': 'm.'}, f)
        current = current_root_provenance('nominal_selftest', keys, nominal=True)
        if not current.get('ok') or current.get('rootmap_sha256') is not None:
            fail('nominal provenance must succeed without a rootmap')
        workflow_meta = {
            'root': 'nominal_selftest',
            'safe_root': current['safe_root'],
            'rootmap_sha256': None,
            'selected_keys': keys,
            'input_hashes': current['input_hashes'],
            'nominal': True,
        }
        check = stale_check('nominal_selftest', workflow_meta, list(reversed(keys)))
        if check['stale']:
            fail('nominal stale_check must not require a rootmap: %s' % check.get('errors'))
        manifest = {'schema': 'pwg.headless_execution_manifest.v1',
                    'meta': dict(workflow_meta)}
        check = stale_check(None, workflow_meta, keys, execution_manifest=manifest)
        if check['stale']:
            fail('manifest-bound nominal provenance must pass without a rootmap: %s'
                 % check.get('errors'))
        duplicate = stale_check(
            None, workflow_meta, keys + keys, execution_manifest=manifest)
        if not duplicate['stale'] or duplicate.get('duplicate_keys') != {keys[0]: 2}:
            fail('manifest provenance must reject duplicate result keys exactly')
        missing = stale_check(None, workflow_meta, [], execution_manifest=manifest)
        if not missing['stale'] or keys[0] not in (missing.get('missing_keys') or []):
            fail('manifest provenance must reject missing result keys')
        foreign = stale_check(
            None, workflow_meta, keys + ['foreign'], execution_manifest=manifest)
        if not foreign['stale'] or 'foreign' not in (foreign.get('unexpected_keys') or []):
            fail('manifest provenance must reject foreign result keys')
        wrong_root_meta = dict(workflow_meta, root='wrong')
        wrong_root = stale_check(
            None, wrong_root_meta, keys, execution_manifest=manifest)
        if not wrong_root['stale'] or not any(
                'execution manifest root' in err for err in wrong_root.get('errors') or []):
            fail('manifest provenance must reject workflow root drift')
        drifted_manifest = {'schema': manifest['schema'],
                            'meta': json.loads(json.dumps(workflow_meta))}
        drifted_manifest['meta']['input_hashes'][keys[0]]['raw_sha256'] = 'drift'
        hash_drift = stale_check(
            None, workflow_meta, keys, execution_manifest=drifted_manifest)
        if not hash_drift['stale'] or not any(
                'input hashes' in err for err in hash_drift.get('errors') or []):
            fail('manifest provenance must reject input-hash drift')
    finally:
        for path, old in ((rp, old_raw), (pp, old_portrait)):
            if old is None:
                try:
                    os.remove(path)
                except OSError:
                    pass
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(old)


def test_no_pwg_card_source_profile_taxonomy():
    """H214: the per-card source-material classifier. The portrait's explicit no-PWG flag wins,
    so a root-split supplement sub-card (empty portrait) is NOT mis-tagged as no-PWG; and the
    supplement PW matcher must not fire on 'PWG'."""
    import gen_opt_harness2 as gh
    no_pwg_portrait = json.dumps([{'portrait_kind': 'no_pwg_supplement_chain',
                                   'source_profile': 'no_pwg_supplement_chain', 'key1': 'k'}])
    cases = [
        ('=== LAYER: PW — Böhtlingk ===\n\nfoo', no_pwg_portrait, 'no_pwg_supplement_chain'),
        ('=== LAYER: PW — Böhtlingk ===\n\nfoo', '[]', 'pwg_supplement_subcard'),
        ('=== LAYER: NWS — Halle ===\n\nfoo', '[]', 'pwg_supplement_subcard'),
        ('=== LAYER: PWG — MAIN ENTRY ===\n\nx\n\n=== LAYER: PW — y ===\n\nz', '[]', 'pwg_with_supplements'),
        ('=== LAYER: PWG — MAIN ENTRY ===\n\nx', '[]', 'pwg_only'),
        ('=== LAYER: PWG-ROOT HEAD — root=gam ===\n\nx', None, 'pwg_only'),
        ('no layer markers here', None, None),
    ]
    for raw, port, want in cases:
        got = gh.card_source_profile(raw, port)
        if got != want:
            fail('card_source_profile(%r) = %r, expected %r' % (raw[:30], got, want))


def test_no_pwg_supplement_card_renders_without_pwg():
    """H214: a PW-only lemma (Bagavat) and a SCH-only lemma (Akulita) render standalone
    supplement-chain sub-cards (raw + portrait) with NO fabricated PWG layer; a PWG key
    (agni) is left to the normal path (gen_no_pwg_card returns None)."""
    import _pilot_gen_merged as pg
    import gen_opt_harness2 as gh
    import dict_merge as dm
    old_out = pg.OUT
    with no_pwg_dictionary_fixture(), tempfile.TemporaryDirectory() as tmp:
        pg.OUT = tmp
        try:
            pwg_idx = dm.index('pwg')
            if pg.gen_no_pwg_card('agni', pwg_idx, verbose=False) is not None:
                fail('gen_no_pwg_card must return None for a PWG-present key (agni)')
            for key, want_layer in (('Bagavat', 'pw'), ('Akulita', 'sch')):
                n = pg.gen_no_pwg_card(key, pwg_idx, verbose=False)
                if not n:
                    fail('gen_no_pwg_card(%s) produced no sub-cards' % key)
                sub = '%s~~h0_zz_%s' % (pg.safe_name(key), want_layer)
                rp = os.path.join(pg.OUT, sub + '.raw.txt')
                pp = os.path.join(pg.OUT, sub + '.portrait.json')
                if not (os.path.exists(rp) and os.path.exists(pp)):
                    fail('expected no-PWG sub-card files for %s (%s)' % (key, sub))
                raw = open(rp, encoding='utf-8').read()
                port = open(pp, encoding='utf-8').read()
                if '=== LAYER: PWG' in raw:
                    fail('%s no-PWG card must NOT contain a PWG layer' % key)
                if '=== LAYER:' not in raw:
                    fail('%s no-PWG card missing a LAYER marker' % key)
                p0 = json.loads(port)[0]
                if p0.get('portrait_kind') != 'no_pwg_supplement_chain' or p0.get('key1') != key:
                    fail('%s portrait must be a no_pwg_supplement_chain sidecar keyed to the headword' % key)
                if p0.get('senses') != []:
                    fail('%s no-PWG portrait must not fabricate a sense tree' % key)
                if gh.card_source_profile(raw, port) != 'no_pwg_supplement_chain':
                    fail('%s sub-card must classify as no_pwg_supplement_chain' % key)
                if dm.layer_of(sub) != want_layer:
                    fail('%s sub-card id must encode layer %s' % (key, want_layer))
        finally:
            pg.OUT = old_out


def test_h920_sense_count_top_level_ordinals():
    """H920: count_source_senses counts DISTINCT top-level source senses (N〉 close-glyph and
    line-anchored N) markers), never citation numbers or lettered sub-senses. Calibrated on
    the real darvI (3-sense PW source), aklizwa (single keyed supplement sense), and a_sakta
    (unnumbered adjective) evidence."""
    darvi = ('=== LAYER: PW ===\n\n{T1} und {T2}¦ {T3}\n'
             '{T6}— 1〉 {%Löffel%}.\n{T7}— 2〉 {%die Haube einer Schlange%}.\n'
             '{T8}— 3〉 {T4} {T5} eines Landes.')
    cases = [
        (darvi, 3),                                             # darvI: 3 top-level senses
        ('{#aklizwa#}¦ 3〉 {%keine Pein verursachend%} <ls>KAP. 2,33</ls>.', 1),  # single keyed sense
        ('{#aSakta#}¦ <lex>Adj.</lex> {%nicht könnend%} <ls n="Chr.">94,27</ls>.', 0),  # unnumbered
        ('<ls>MBH. 5,163,4</ls>. 2,33 1,5', 0),                # citation numbers are NOT senses
        ('1) a\n2) b\n3) c', 3),                               # line-anchored N) form
        ('— 2〉 x\n— 2〉 x (batch repeat)', 1),                  # a repeated ordinal counts once
    ]
    for text, want in cases:
        got = count_source_senses(text)
        if got != want:
            fail('count_source_senses(%r) = %d, expected %d' % (text[:40], got, want))


def test_h920_sense_shortfall_gate_flags_dropped_sense():
    """H920: the audit_window SAN-LOSS gate flags a card whose OUTPUT sense count falls short
    of its input portrait's declared source_senses (the darvI 2/3 shape), passes a complete
    card, and is CONSERVATIVE — it skips null cards and portraits that predate the source_senses
    stamp (never a false positive)."""
    import audit_window
    with tempfile.TemporaryDirectory() as tmp:
        def portrait(name, **extra):
            json.dump([dict({'portrait_kind': 'no_pwg_supplement_chain', 'senses': []}, **extra)],
                      open(os.path.join(tmp, name + '.portrait.json'), 'w', encoding='utf-8'),
                      ensure_ascii=False)
        portrait('darv_i~~h0_zz_pw', key1='darvI', source_senses=3)   # 3 source senses
        portrait('ok~~h0_zz_pw', key1='ok', source_senses=2)          # complete
        portrait('legacy~~h0_zz_pw', key1='legacy')                   # pre-H920, no count
        results = [
            {'key': 'darv_i~~h0_zz_pw',                               # 2 of 3 -> SAN-LOSS
             'card': {'key1': 'darvI', 'records': [{'senses': [{'tag': '2'}, {'tag': '3'}]}]}},
            {'key': 'ok~~h0_zz_pw',                                   # 2 of 2 -> clean
             'card': {'records': [{'senses': [{'tag': '1'}, {'tag': '2'}]}]}},
            {'key': 'legacy~~h0_zz_pw',                               # no expected count -> skipped
             'card': {'records': [{'senses': [{'tag': '1'}]}]}},
            {'key': 'null~~h0_zz_pw', 'card': None, 'error': 'kill-timeout'},  # null -> skipped
        ]
        # pure scan
        short = scan_sense_shortfall(results, tmp)
        if [s['key'] for s in short] != ['darv_i~~h0_zz_pw']:
            fail('scan_sense_shortfall should flag ONLY darvI, got %r' % short)
        if short[0]['expected'] != 3 or short[0]['actual'] != 2 or short[0]['dropped'] != 1:
            fail('darvI shortfall math wrong: %r' % short[0])
        # the wired audit gate
        gate = audit_window.run_sense_shortfall_gate(results, tmp, set())
        if gate['returncode'] != 1 or gate['requeue'] != ['darv_i~~h0_zz_pw']:
            fail('SAN-LOSS gate must FAIL and requeue only darvI, got %r' % gate)
        if 'SAN-LOSS' not in gate['stdout'] or 'dropped 1' not in gate['stdout']:
            fail('SAN-LOSS gate stdout must report the drop: %r' % gate['stdout'])
        # protected keys are never requeued
        if audit_window.run_sense_shortfall_gate(results, tmp, {'darv_i~~h0_zz_pw'})['requeue']:
            fail('a protected key must not be requeued by the SAN-LOSS gate')
        # a fully-clean window passes
        clean = audit_window.run_sense_shortfall_gate(results[1:], tmp, set())
        if clean['returncode'] != 0 or clean['requeue']:
            fail('SAN-LOSS gate must PASS a window with no shortfall, got %r' % clean)


def test_h920_no_pwg_portrait_stamps_source_senses():
    """H920: gen_no_pwg_card stamps a deterministic source_senses count into each sub-card's
    portrait (matching count_source_senses on that sub-card's raw), while still fabricating NO
    sense tree (senses stays []). A source with >=2 numbered senses also carries the explicit
    sense-completeness rule so the model is told to render every sense."""
    import _pilot_gen_merged as pg
    import dict_merge as dm
    # unit: the sense-completeness rule fires only for multi-sense sources and never inflates
    # the deterministic count (the rule text carries no 〉 / leading-digit lines).
    multi = '=== LAYER: PW ===\n\n{#x#}¦\n— 1〉 {%a%}.\n— 2〉 {%b%}.\n— 3〉 {%c%}.'
    ruled = pg._with_sense_rule(multi, count_source_senses(multi))
    if 'SENSE-COMPLETENESS RULE' not in ruled or 'all 3' not in ruled:
        fail('multi-sense supplement must carry the H920 sense-completeness rule')
    if count_source_senses(ruled) != 3:
        fail('the sense-completeness rule must not inflate the deterministic count')
    if pg._with_sense_rule('=== LAYER: PW ===\n\nsingle sense, no marker', 0) \
            != '=== LAYER: PW ===\n\nsingle sense, no marker':
        fail('a source with <2 senses must NOT get the sense-completeness rule')
    # end-to-end: render a real no-PWG card and assert the portrait is enriched + consistent.
    old_out = pg.OUT
    with no_pwg_dictionary_fixture(), tempfile.TemporaryDirectory() as tmp:
        pg.OUT = tmp
        try:
            pwg_idx = dm.index('pwg')
            for key, layer in (('Bagavat', 'pw'), ('Akulita', 'sch')):
                if not pg.gen_no_pwg_card(key, pwg_idx, verbose=False):
                    fail('gen_no_pwg_card(%s) produced no sub-cards' % key)
                sub = '%s~~h0_zz_%s' % (pg.safe_name(key), layer)
                raw = open(os.path.join(pg.OUT, sub + '.raw.txt'), encoding='utf-8').read()
                p0 = json.loads(open(os.path.join(pg.OUT, sub + '.portrait.json'), encoding='utf-8').read())[0]
                if 'source_senses' not in p0:
                    fail('%s portrait must carry the H920 source_senses count' % sub)
                if p0['source_senses'] != count_source_senses(raw):
                    fail('%s portrait source_senses (%r) must equal count_source_senses(raw) (%d)'
                         % (sub, p0['source_senses'], count_source_senses(raw)))
                if p0.get('senses') != []:
                    fail('%s no-PWG portrait must still fabricate no sense tree' % sub)
        finally:
            pg.OUT = old_out


def test_h920_en_missing_sense_hard_flag():
    """H920: the EN auditor emits a HARD MISSING-SENSE flag when an output card falls short of
    its portrait's source_senses (SHARED with the RU gate via sense_count.py), distinct from the
    per-sense SAN-LOSS gloss-token flag; a complete card carries no such flag."""
    import audit_window_en as en
    with tempfile.TemporaryDirectory() as tmp:
        json.dump([{'source_senses': 3}],
                  open(os.path.join(tmp, 'darv_i~~h0_zz_pw.portrait.json'), 'w', encoding='utf-8'))
        json.dump([{'source_senses': 2}],
                  open(os.path.join(tmp, 'ok~~h0_zz_pw.portrait.json'), 'w', encoding='utf-8'))
        old_dir = en.INPUT_DIR
        en.INPUT_DIR = tmp
        try:
            short = en.audit_card(
                {'key': 'darv_i~~h0_zz_pw',
                 'card': {'records': [{'h': 'darvī', 'senses': [
                     {'tag': '2', 'german': '2〉 x', 'english': 'the hood of a snake'},
                     {'tag': '3', 'german': '3〉 y', 'english': 'name of a country'}]}]}},
                None, False)
            flags = [f for _, f in short['flags']]
            if not any(f.startswith('MISSING-SENSE') for f in flags):
                fail('EN auditor must emit MISSING-SENSE on a 2/3 card, got %r' % flags)
            if not any(en.is_hard(f) for f in flags if f.startswith('MISSING-SENSE')):
                fail('MISSING-SENSE must be a HARD flag')
            ok = en.audit_card(
                {'key': 'ok~~h0_zz_pw',
                 'card': {'records': [{'h': 'ok', 'senses': [
                     {'tag': '1', 'german': '1〉 a', 'english': 'first'},
                     {'tag': '2', 'german': '2〉 b', 'english': 'second'}]}]}},
                None, False)
            if any(f.startswith('MISSING-SENSE') for _, f in ok['flags']):
                fail('a complete 2/2 card must NOT get MISSING-SENSE')
        finally:
            en.INPUT_DIR = old_dir


def test_h960_accept_sanloss_soft_gate():
    """H960: the harness stamps the deterministic (cross-reference-hardened) source_senses into
    each input, and accept() carries the SAN-LOSS shortfall guard — H920's deferred deepest fix.
    SOFT by default (SANLOSS_HARD_REJECT=false): a whole-dropped sense is COUNTED as telemetry but
    the card is kept; the owner-gated flip rejects+requeues it. The behavioral half runs the REAL
    emitted accept()+countOf (see accept_sensecount_test.js), so it can't drift from the generator."""
    import gen_opt_harness2 as gh
    saved_ip, saved_kill = gh.input_paths, gh.KILL
    d = tempfile.mkdtemp()
    try:
        # darv_i: 3 line-opening senses -> source_senses 3. xref: only cross-reference ordinals
        # ("zu {#ASraya#} 1〉 und 6〉") -> hardened source_senses 0 (the FP-regression shape).
        raws = {
            'darv_i~~h0_zz_pw': '=== LAYER: PW ===\n\n{#darvI#}¦\n— 1〉 {%a%}.\n— 2〉 {%b%}.\n— 3〉 {%c%}.',
            'xref~~h0_zz_pw': '=== LAYER: PW ===\n\nNom. abstr. zu {#ASraya#} 1〉 und 6〉.',
        }
        keys = list(raws)
        paths = {}
        for k, raw in raws.items():
            rp = os.path.join(d, k + '.raw.txt')
            pp = os.path.join(d, k + '.portrait.json')
            with open(rp, 'w', encoding='utf-8') as f:
                f.write(raw)
            with open(pp, 'w', encoding='utf-8') as f:
                f.write('[]')
            paths[k] = (rp, pp)
        gh.input_paths = lambda k, input_dir=None: paths[k]
        gh.KILL = False
        js, _ = gh.build('zz_sanloss', keys, None, 12000,
                         nominal=True, grammar_on=False, tm_path=None)
        # (1) the soft gates (sanloss + grammar-{Tn}) + owner-gated hard paths + telemetry are emitted
        for needle in ('const SANLOSS_HARD_REJECT = false', 'SANLOSS_SHORTFALLS',
                       'sanloss-reject', 'sanloss_shortfalls',
                       'const TNMASK_HARD_REJECT = false', 'TNMASK_MISMATCHES',
                       'tnmask-reject', 'tnmask_mismatches'):
            if needle not in js:
                fail('accept() SAN-LOSS / {Tn} soft gate not emitted (missing %r)' % needle)
        # (2) the deterministic source_senses count is stamped into the runtime INPUTS
        if '"source_senses": 3' not in js:
            fail('darv_i source_senses (3) must be stamped into the emitted INPUTS')
        if '"source_senses": 0' not in js:
            fail('cross-reference xref source_senses must harden to 0 in the emitted INPUTS')
        # (3) behavioral: the REAL accept() rejects/keeps a shortfall exactly as specified
        harness = os.path.join(d, 'sanloss_harness.js')
        with open(harness, 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        test_js = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'accept_sensecount_test.js')
        p = subprocess.run(['node', test_js, harness],
                           capture_output=True, text=True, encoding='utf-8', timeout=30)
        if p.returncode:
            fail('accept() SAN-LOSS behavioral test failed:\n%s\n%s' % (p.stdout, p.stderr))
    finally:
        gh.input_paths, gh.KILL = saved_ip, saved_kill
        shutil.rmtree(d, ignore_errors=True)


def test_tnmask_persist_and_offline_detect():
    """H1226: accept() PERSISTS the pre-restore {Tn} pairing (candidate `got` vs masked-skeleton
    `want`) on the accepted card, and promote carries it to the row's provenance, so a SOFT
    (un-rejected) TNMASK expansion becomes MEASURABLE offline from a promoted row -- H1150 returned
    DO_NOT_ARM (denominator 1) precisely because the store dropped this transient pairing.
    Two-part pin: (1) the behavioral half runs the REAL emitted accept()+tokensOf+cardTokens
    (tnmask_persist_test.js, extraction pattern -> cannot drift from the generator); (2) the
    end-to-end half proves detection through the REAL promote_final_cards.rows_for + the offline
    reader -- GREEN with the field, RED (not measurable) without it."""
    import gen_opt_harness2 as gh
    saved_ip, saved_kill = gh.input_paths, gh.KILL
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, 'tnp~~h0_zz_pw.raw.txt')
        pp = os.path.join(d, 'tnp~~h0_zz_pw.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write('=== LAYER: PW ===\n\n{#tnp#}¦ {%m%}\n— 1〉 {%a%}.')
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        gh.input_paths = lambda k, input_dir=None: (rp, pp)
        gh.KILL = False
        js, _ = gh.build('zz_tnmask', ['tnp~~h0_zz_pw'], None, 12000,
                         nominal=True, grammar_on=False, tm_path=None)
        # (1a) the persistence line is emitted into the real accept(), and the arming consts are
        #      byte-unchanged (this handoff persists provenance; it never arms).
        if 'c.tnmask = {' not in js:
            fail('accept() must persist the pre-restore {Tn} pairing (c.tnmask) — H1226')
        for needle in ('const TNMASK_HARD_REJECT = false', 'const SANLOSS_HARD_REJECT = false'):
            if needle not in js:
                fail('H1226 must leave the soft-guard arming consts unchanged (missing %r)' % needle)
        # (1b) behavioral: the REAL accept() stamps got/want; an expansion is flagged, clean isn't.
        harness = os.path.join(d, 'tnmask_harness.js')
        with open(harness, 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        test_js = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'tnmask_persist_test.js')
        p = subprocess.run(['node', test_js, harness],
                           capture_output=True, text=True, encoding='utf-8', timeout=30)
        if p.returncode:
            fail('tnmask persistence behavioral test failed:\n%s\n%s' % (p.stdout, p.stderr))
    finally:
        gh.input_paths, gh.KILL = saved_ip, saved_kill
        shutil.rmtree(d, ignore_errors=True)
    # (2) offline detection end-to-end through the REAL promote path (red/green).
    import promote_final_cards as pfc
    import tnmask_offline as tno
    meta = {'root': 'tnp', 'nominal': True, 'nominal_keymap': {'tnp~~h0_zz_pw': 'tnp'},
            'input_hashes': {'tnp~~h0_zz_pw': {'raw_sha256': 'r', 'portrait_sha256': 'p'}}}
    base_card = {'key1': 'tnp', 'iast': 'tnp', 'notes': '',
                 'records': [{'h': 'tnp', 'grammar': '',
                              'senses': [{'tag': '1', 'russian': 'x', 'german': 'y'}]}]}
    exp_card = dict(base_card, tnmask={'got': 'T1', 'want': 'T1 T2'})   # a soft expansion
    row = list(pfc.rows_for('tnp~~h0_zz_pw',
                            {'card': exp_card, 'meta': meta, 'wf_file': 'wf.json'},
                            'ai_translated', pfc.SELFTEST_MODEL_VERSION))[0]
    if not tno.tnmask_measurable(row):
        fail('promoted row must carry the H1226 {Tn} pairing when the card has one')
    if tno.tnmask_mismatch(row) is not True:
        fail('GREEN: an expansion must be detectable offline from the promoted row')
    stripped = json.loads(json.dumps(row))          # the SAME row, field removed = pre-H1226
    stripped['provenance'].pop('tnmask', None)
    if tno.tnmask_mismatch(stripped) is not None:
        fail('RED: without the field the promoted row must be NOT MEASURABLE, never a silent clean')
    tno.selftest()                                  # pin the reader itself (fail-loud, no I/O)


def test_grammar_field_restore_behavioral():
    """H1151 pin for the H858 grammar-{Tn} stranding class (live on gokzuraka, 13-07-2026).
    The C-01 centralization (card_fields.js_restore_spec) already restores record.grammar in
    both lanes; this behavioral test extracts the REAL restore()/restoreCard()/RESTORE_SPEC
    from a freshly generated harness (grammar_restore_test.js) so a future edit that drops
    `grammar` (or `h`) from the record-level restore fails HERE, not as silent store rows."""
    import gen_opt_harness2 as gh
    saved_ip, saved_kill = gh.input_paths, gh.KILL
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, 'gok~~h0_zz_pw.raw.txt')
        pp = os.path.join(d, 'gok~~h0_zz_pw.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write('=== LAYER: PW ===\n\n{#gok#}¦ {%m%}\n— 1〉 {%a%}.')
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        gh.input_paths = lambda k, input_dir=None: (rp, pp)
        gh.KILL = False
        js, _ = gh.build('zz_grestore', ['gok~~h0_zz_pw'], None, 12000,
                         nominal=True, grammar_on=False, tm_path=None)
        harness = os.path.join(d, 'grestore_harness.js')
        with open(harness, 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        test_js = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'grammar_restore_test.js')
        p = subprocess.run(['node', test_js, harness],
                           capture_output=True, text=True, encoding='utf-8', timeout=30)
        if p.returncode:
            fail('grammar-field restore behavioral test failed:\n%s\n%s' % (p.stdout, p.stderr))
    finally:
        gh.input_paths, gh.KILL = saved_ip, saved_kill
        shutil.rmtree(d, ignore_errors=True)


def test_h960_dropped_sanskrit_span():
    """H960 (H911 backlog #3): a {#..#} Sanskrit span present in the German source but dropped from
    the Russian translation is flagged (dropped_sanskrit_span). The harness/tm fidelity gates count
    {#..#} only in the german echo, never the translation field, so an intra-sense span that
    survives the echo but vanishes from the Russian passes clean. LOW / report-only (never in
    HIGH_CONFIDENCE_RISKS -> never requeues). Structural HEAD labels (headword/preverb/root) are
    excluded — the measured 95%-false-positive class — so only a genuine intra-sense drop fires."""
    import prompt_rule_audit as pr
    def ids(ru, de):
        return [r['id'] for r in pr.markup_sigla_risks({}, ru, de, '', '3')]
    # POSITIVE: a genuine mid-sense span drop fires.
    if 'dropped_sanskrit_span' not in ids('делает что-то несмотря', 'делает что-то {#kar#} несмотря'):
        fail('dropped_sanskrit_span must fire on a genuine mid-sense {#..#} drop')
    # CONTROL: span retained -> silent.
    if 'dropped_sanskrit_span' in ids('делает {#kar#} несмотря', 'делает {#kar#} несмотря'):
        fail('dropped_sanskrit_span must NOT fire when the span is retained')
    # CONTROL: a headword-label drop (the darvI FP class) is excluded.
    if 'dropped_sanskrit_span' in ids('имя собственное страны', '{#darvI#} <ab>N. pr.</ab> eines Landes'):
        fail('a headword-label {#..#} drop must be excluded (95% FP class)')
    # CONTROL: a √-root label drop is excluded.
    if 'dropped_sanskrit_span' in ids('мерить', '√{#mA#} messen'):
        fail('a root-label {#..#} drop must be excluded')
    # report-only: never high-confidence (never drives a requeue), and LOW severity.
    if 'dropped_sanskrit_span' in pr.HIGH_CONFIDENCE_RISKS:
        fail('dropped_sanskrit_span must stay out of HIGH_CONFIDENCE_RISKS (report-only)')
    row = [r for r in pr.markup_sigla_risks({}, 'делает что-то несмотря', 'делает что-то {#kar#} несмотря', '', '3')
           if r['id'] == 'dropped_sanskrit_span'][0]
    if row['level'] != 'low' or row.get('high_confidence'):
        fail('dropped_sanskrit_span must be LOW / non-high-confidence, got %r' % row)


def test_no_pwg_worklist_runnable_lane():
    """H214: the worklist exposes a no_pwg_runnable lane for PW/SCH/PWKVN-only lemmas and does
    NOT reclassify a true miss (absent from every layer) as runnable, nor mix it into the
    PWG-rooted runnable count."""
    import nominals_worklist as nw
    with no_pwg_dictionary_fixture(), tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'sample.slp1.txt')
        manifest = os.path.join(tmp, 'scale_manifest.freq.json')
        store = os.path.join(tmp, 'store.jsonl')      # isolated empty store: the runnable/promoted
        with open(path, 'w', encoding='utf-8') as f:  # split must not depend on the live store
            f.write('Bagavat\nAkulita\nZZzznotaword\n')      # pw-only, sch-only, true miss
        with open(manifest, 'w', encoding='utf-8') as f:
            json.dump([
                {'key1': 'Bagavat', 'score': 3, 'band': 1},
                {'key1': 'Akulita', 'score': 2, 'band': 1},
                {'key1': 'ZZzznotaword', 'score': 1, 'band': 1},
            ], f)
        open(store, 'w', encoding='utf-8').close()
        payload = nw.build_worklist(path, manifest=manifest, store=store)
    runnable = set(payload['no_pwg_runnable'])
    if 'Bagavat' not in runnable or 'Akulita' not in runnable:
        fail('no_pwg_runnable must contain the PW/SCH-only lemmas: %s' % sorted(runnable))
    if 'ZZzznotaword' in runnable or 'ZZzznotaword' not in set(payload['true_miss_keys']):
        fail('a true miss must stay a true miss, never runnable')
    if runnable & set(payload['runnable_remaining']):
        fail('no-PWG runnable must stay separate from the PWG-rooted runnable lane')


def test_no_pwg_layer_and_profile_survive_promotion():
    """H214: layer label + source_profile survive sub-card id -> provenance -> promoted rows,
    for a no-PWG card AND a mixed (pwg_with_supplements) card, in one nominal window."""
    import promote_final_cards as pf
    meta = {
        'root': 'no_pwg_selftest', 'safe_root': 'no_pwg_selftest', 'generator': 'g',
        'schema_version': 'v', 'rootmap_sha256': None, 'generated_at': '2026-07-06T00:00:00Z',
        'nominal': True,
        'nominal_keymap': {'_bagavat~~h0_zz_pw00': 'Bagavat', 'x~~h0_00_pwg00': 'x'},
        'source_profiles': {'_bagavat~~h0_zz_pw00': 'no_pwg_supplement_chain',
                            'x~~h0_00_pwg00': 'pwg_with_supplements'},
        'input_hashes': {'_bagavat~~h0_zz_pw00': {'raw_sha256': 'r', 'portrait_sha256': 'p'},
                         'x~~h0_00_pwg00': {'raw_sha256': 'r2', 'portrait_sha256': 'p2'}},
    }

    def one(subkey, key1, ru):
        card = {'key1': key1, 'iast': key1,
                'records': [{'h': '1', 'senses': [{'tag': '1', 'russian': ru, 'german': 'x'}]}]}
        entry = {'card': card, 'meta': meta, 'wf_file': 't'}
        return list(pf.rows_for(subkey, entry, 'ai_translated', pf.SELFTEST_MODEL_VERSION))[0]

    r = one('_bagavat~~h0_zz_pw00', 'Bagavat', 'блаженный')
    if r['key1'] != 'Bagavat' or r['layer'] != 'pw':
        fail('no-PWG row must key to the headword and carry layer=pw: %r' % r)
    if r['provenance'].get('source_profile') != 'no_pwg_supplement_chain':
        fail('no-PWG provenance marker did not reach the promoted row')
    m = one('x~~h0_00_pwg00', 'x', 'слово')
    if m['layer'] != 'pwg' or m['provenance'].get('source_profile') != 'pwg_with_supplements':
        fail('mixed card must carry layer=pwg + source_profile=pwg_with_supplements: %r' % m)


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


def test_h1152_guard1_en_polyseme_checklist():
    """H1152 guard 1 (H1070 finding #1: r155 'braut'->betroth, r119 'Vergleich'->comparison):
    a German-homograph/polyseme checklist under term-mistranslation in the EN fidelity judge
    rubric, plus a matching HARD RULE in tr_en.txt telling the generator to pick the sense the
    Sanskrit lemma licenses, never the frequent German sense. Markup stays intact and the
    English reads fluently for this error class, so no deterministic gate can catch it --
    this guard is judge-rubric + generation-prompt only, pinned here as a content check."""
    import gen_fidelity_judge_en as jen
    for term in ('Vergleich', 'braut', 'Braut', 'gelten', 'Zug', 'anführen'):
        if term not in jen.RUBRIC:
            fail('EN judge RUBRIC missing German-polyseme checklist term %r' % term)
    if 'term-mistranslation' not in jen.RUBRIC or 'polysem' not in jen.RUBRIC.lower():
        fail('EN judge RUBRIC term-mistranslation line is missing the polyseme checklist')
    tr = open(os.path.join(HERE, 'tr_en.txt'), encoding='utf-8').read()
    if 'sense the sanskrit lemma licenses' not in tr.lower():
        fail('tr_en.txt is missing the polyseme prompt rule (pick the sense the Sanskrit '
             'lemma licenses, never the frequent sense)')
    if 'polysemous german gloss' not in tr.lower():
        fail('tr_en.txt is missing the POLYSEMOUS GERMAN GLOSSES hard rule')


def test_semantic_risk_checker():
    clean_card = {
        'key': 'ap',
        'card': {
            'key1': 'ap',
            'iast': 'ap',
            'records': [{
                'h': '2',
                'grammar': 'f.',
                'senses': [{
                    'tag': '1',
                    'german': 'Wasser, Gewässer',
                    'russian': 'вода, воды',
                    'equivalence_type': 'equivalent',
                    'source_type': 'attested',
                    'stratum': 'Vedic',
                    'differentia': 'вода — основной корпусный перевод; воды — pluralia tantum.',
                }, {
                    'tag': '2',
                    'german': 'Amarakośa: Stern',
                    'russian': 'звезда',
                    'equivalence_type': 'equivalent',
                    'source_type': 'lexicographic',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
            'notes': '',
        },
    }
    clean = audit_card_result(clean_card)
    if clean['risk_count']:
        fail('clean semantic-risk fixture produced risks: %s' %
             ', '.join(r['id'] for r in clean['risks']))

    bad_card = {
        'card': {
            'key1': 'agni',
            'iast': 'agni',
            'corpus_synonyms': {'candidates': ['огонь', 'пламя']},
            'records': [{
                'h': '1',
                'grammar': 'm.',
                'senses': [{
                    'tag': '1',
                    'german': 'Feuer, Brand',
                    'russian': 'agni der',
                    'stratum': '',
                }],
            }, {
                'h': '2',
                'grammar': 'm.',
                'senses': [{
                    'tag': '2',
                    'german': 'Glanz',
                    'russian': 'agni der',
                    'equivalence_type': 'equivalent',
                    'source_type': 'lexicographic',
                    'stratum': 'Epic',
                    'differentia': '',
                }, {
                    'tag': '3',
                    'german': '{%Schein%}',
                    'russian': 'agni der',
                    'equivalence_type': 'equivalent',
                    'source_type': 'attested',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
        },
    }
    ids = {risk['id'] for risk in semantic_risks(bad_card)}
    expected = {
        'missing_required_sense_field',
        'missing_equivalence_type',
        'missing_source_type',
        'untranslated_german_residue',
        'collapsed_synonym_string',
        'likely_circular_gloss',
        'identical_russian_glosses',
        'missing_apresjan_discrimination',
        'suspicious_attested_without_text_signal',
        'suspicious_lexicographic_with_text_signal',
    }
    if not expected.issubset(ids):
        fail('semantic-risk checker missed: %s' % ', '.join(sorted(expected - ids)))

    formula_card = {
        'card': {
            'key1': 'iti',
            'iast': 'iti',
            'records': [{
                'h': '1',
                'grammar': 'ind.',
                'senses': [{
                    'tag': '1',
                    'german': 'iti arthaḥ',
                    'russian': 'смысл',
                    'equivalence_type': 'explanatory',
                    'source_type': 'lexicographic',
                    'stratum': '',
                    'differentia': '',
                }, {
                    'tag': '2',
                    'german': 'iti śeṣaḥ',
                    'russian': 'остаток',
                    'equivalence_type': 'explanatory',
                    'source_type': 'lexicographic',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
        },
    }
    formula_ids = {risk['id'] for risk in semantic_risks(formula_card)}
    if not {'formula_iti_arthah', 'formula_iti_sesah'}.issubset(formula_ids):
        fail('formula semantic-risk fixture missed fixed-rendering findings')


def test_braced_gloss_audit():
    untranslated = braced_gloss_risks('{%Schulter%}', '{%Schulter%}', '1')
    ids = {risk['id'] for risk in untranslated}
    if 'untranslated_braced_german_gloss' not in ids:
        fail('braced gloss audit missed untranslated German gloss')
    kept_latin = braced_gloss_risks('das lat. {%ansa%}', 'лат. {%ansa%}', '1')
    kept_binomial = braced_gloss_risks('{%Trapa bispinosa%}', '{%Trapa bispinosa%}', '1')
    if kept_latin or kept_binomial:
        fail('braced gloss audit flagged literal Latin/binomial preservation')
    translated_latin = braced_gloss_risks(
        'das lat. {%ansa%}', 'лат. {%ручка%}', '1')
    translated_english = braced_gloss_risks(
        'Wils. übersetzt durch {%leaving, abandoning%}',
        'Уилсон переводит как {%оставление, покидание%}', '1')
    ids = {risk['id'] for risk in translated_latin + translated_english}
    if 'foreign_gloss_translated' not in ids:
        fail('braced gloss audit missed translated Latin/English literal gloss')

    # B&R Latin euphemisms / French / Sanskrit-token braces must NOT be flagged as
    # untranslated German (the convention keeps them verbatim).
    for ger in ('{%inire feminam%}', '{%legere%}', '{%inveteratus%}',
                "{%un homme de l'extraction la plus basse%}", '{%abhi%}',
                '{%upanis%}', '{%āgamya%}', '{%sequi, obsequi%}'):
        leftover = {r['id'] for r in braced_gloss_risks(ger, ger, '1')}
        if 'untranslated_braced_german_gloss' in leftover:
            fail('braced gloss audit wrongly flagged non-German literal: %s' % ger)
    # Side-by-side: German kept in {%...%} BESIDE its Russian rendering is required.
    side = braced_gloss_risks('{%herfallen über%}', 'нападать на ({%herfallen über%})', '1')
    if {r['id'] for r in side} & {'untranslated_braced_german_gloss'}:
        fail('braced gloss audit flagged required side-by-side German echo')

    # gam~~h0_20_ava / gam~~h0_38_sam_a (2026-07-03): short/colloquial German that collides
    # with a FRENCH_WORDS entry ("du") or matches LATIN_BINOMIAL's over-permissive
    # Capitalized-word+lowercase-word shape ("Jmd zusammenkommen", "Jmd" being the common B&R
    # abbreviation for "jemand") must be recognized as German and NOT flagged
    # foreign_gloss_translated merely for being correctly translated into Russian.
    colloquial = braced_gloss_risks(
        '{%wie kommst du darauf? woraus schliessest du dieses?%}',
        '{%как ты до этого дошёл? из чего ты это заключаешь?%}', '1')
    if {r['id'] for r in colloquial} & {'foreign_gloss_translated'}:
        fail('braced gloss audit misclassified colloquial German (du) as foreign literal')
    abbrev = braced_gloss_risks('{%Jmd zusammenkommen%}', '{%встречаться с кем-л.%}', '1')
    if {r['id'] for r in abbrev} & {'foreign_gloss_translated'}:
        fail('braced gloss audit misclassified "Jmd ..." (LATIN_BINOMIAL shape) as Latin')

    # gam~~h0_38_sam_a (2026-07-03): a correctly-translated short gloss ({%mit%} -> {%с%})
    # was flagged untranslated because the "leaked" check did a raw substring search across
    # the WHOLE Russian text, including verbatim {#Sanskrit#} citation spans -- "mit" is a
    # literal substring of the unrelated SLP1 citation token "miTunO" (lowercased "mituno").
    sanskrit_collision = braced_gloss_risks(
        '{%mit%} (<ab>instr.</ab>) {#yadA vE miTunO samAgacCataH#} (fleischlich)',
        '{%с%} (<ab>instr.</ab>) {#yadA vE miTunO samAgacCataH#} (плотски)', '1')
    if {r['id'] for r in sanskrit_collision} & {'untranslated_braced_german_gloss'}:
        fail('braced gloss audit flagged a gloss that only collided with an embedded '
             'Sanskrit citation substring, not a real leak')


def semantic_card_risk_ids(russian, german='{%nachgehen%}'):
    card = {'card': {'key1': 'x', 'iast': 'x', 'notes': '', 'records': [{
        'h': 'x', 'grammar': 'ind.', 'senses': [{
            'tag': '1', 'german': german, 'russian': russian,
            'equivalence_type': 'explanatory', 'source_type': 'lexicographic',
            'stratum': '', 'differentia': ''}]}]}}
    return {risk['id'] for risk in semantic_risks(card)}


def test_german_residue_keeps_retained_markup():
    # German inside retained {%...%} / <ab> spans with a Russian rendering beside it
    # is side-by-side, not residue; bare German connectives outside markup still flag.
    clean = semantic_card_risk_ids(
        'подражать ({%den Umständen gemäss%}: сообразно обстоятельствам)')
    if 'untranslated_german_residue' in clean:
        fail('residue audit flagged required side-by-side German')
    leak = semantic_card_risk_ids('— Vgl. upAgama und gam mit upa')
    if 'untranslated_german_residue' not in leak:
        fail('residue audit missed genuine untranslated German connectives')


def test_german_connective_fix():
    # safe lone connectives / fixed phrase in free text are substituted
    assert fix_german_text('{#X#} und {#Y#} mit {#Z#}')[0] == '{#X#} и {#Y#} с {#Z#}'
    assert fix_german_text('(<ab>s.</ab> auch d.)')[0] == '(<ab>s.</ab> также d.)'
    assert fix_german_text('fehlerhaft für {#aDijagAma#}')[0] == 'ошибочно вместо {#aDijagAma#}'
    # protected spans are NEVER touched: retained {%..%} markup and «..» German quotes
    if fix_german_text('{%und%}')[1] or fix_german_text('«Von Sternen und Mond»')[1]:
        fail('connective fix touched a protected span ({%..%} or «..»)')
    # ambiguous multi-word German phrase is left for review (no lone-connective match)
    if fix_german_text('aber nur in der Saṃhitā')[1]:
        fail('connective fix wrongly altered an ambiguous German phrase')


def test_h1302_german_prose_residue_scan():
    # H1302: the store-wide German-prose-residue detector + deterministic --store fixer.
    from german_residue_scan import scan_text
    from fix_german_connectives import fix_ru_store

    def classes(text):
        return {(tok, cls) for tok, _ctx, cls in scan_text(text)}

    # prose `zu` in a citation (Schol. zu <ls>) is flagged and deterministically fixable (class a)
    zu = classes('5) {%извлекать%}: {#tApasA#}\n<ab>Schol.</ab> zu <ls>ŚĀK. 14.</ls>')
    if ('zu', 'a') not in zu:
        fail('H1302: citation `zu` not flagged as class-a residue')
    # `mit Ergänzung von` outside markup is flagged class a
    if not any('Erg' in t and c == 'a' for t, c in classes('{%примирить%} mit Ergänzung von {#saha grIveRa#})')):
        fail('H1302: `mit Ergänzung von` not flagged as class-a residue')
    # a protected German gloss {%…%} and a «…» verbatim quote are NEVER flagged
    if classes('{%родственник, друг%} «nahe stehend» <ab>vgl.</ab> {#Api#}'):
        fail('H1302: detector flagged a protected {%…%} / «…» span')
    # grammatical German prose "mit dem <ab>acc.</ab>" is class-b (needs retranslation, not a sub)
    if not any(c == 'b' for _, c in classes('{%думать о%}; mit dem <ab>acc.</ab>: {#aBi#}')):
        fail('H1302: "mit dem <ab>acc.</ab>" not flagged as class-b retranslate')
    # author proper names with German orthography are whitelisted (class c), never residue
    if not any(c == 'c' for _, c in classes('Кауз.: оживлять. [NWS: Graßmann 1873 (1996) : 491]') or [(None, 'x')]):
        # [NWS:…] is masked entirely; a bare "Böhtlingk 1840" still whitelists to c
        if not any(c == 'c' for _, c in classes('первоначальном состоянии. Böhtlingk 1840 : 548')):
            fail('H1302: proper-name author not whitelisted (class c)')
    # the deterministic --store fixer repairs the two rejected-card patterns exactly
    if fix_ru_store('<ab>Schol.</ab> zu <ls>ŚĀK. 14.</ls>')[0] != '<ab>Schol.</ab> к <ls>ŚĀK. 14.</ls>':
        fail('H1302: --store fixer did not turn citation `zu` into «к»')
    if fix_ru_store('{%примирить%} mit Ergänzung von {#saha#}')[0] != '{%примирить%} с восполнением {#saha#}':
        fail('H1302: --store fixer did not turn `mit Ergänzung von` into «с восполнением»')
    # the fixer NEVER touches a protected span
    if fix_ru_store('{%mit und ohne%} «und»')[1]:
        fail('H1302: --store fixer touched a protected {%…%} / «…» span')


def test_h1305_ru_style_mechanical():
    # H1305 + review fix: hard style rules inspect structured Russian senses only;
    # ambiguous narrative R2/R3 prose warns but never enters FLAGGED_JSON.
    from ru_style_sweep import audit_workflow_results, scan_violations, style_diagnostics, sweep_text

    # ё-word flagged (R1)
    if 'R1_yo' not in scan_violations('пришёл поздно'):
        fail('H1305: ё-carrying word not flagged R1_yo')
    # standalone «всё» passes clean (whitelisted)
    if scan_violations('всё хорошо, Всё в порядке'):
        fail('H1305: whitelisted «всё»/«Всё» incorrectly flagged')
    # the «всё-таки» edge case is NOT whitelisted -- defaults to е, so IS flagged
    if 'R1_yo' not in scan_violations('он всё-таки пришёл'):
        fail('H1305: «всё-таки» edge case incorrectly treated as whitelisted')
    # metalanguage «вместо» flagged (R2)
    if 'R2_vmesto' not in scan_violations('ошибочно вместо {#X#}'):
        fail('H1305: metalanguage «вместо» not flagged R2_vmesto')
    # metalanguage «в значении» flagged (R3)
    if 'R3_vznach' not in scan_violations('употребляется в значении «зуб»'):
        fail('H1305: metalanguage «в значении» not flagged R3_vznach')
    # Ordinary prose stays natural and is diagnostic-only, not a hard violation.
    for prose, rule in (
            ('Он выступил вместо брата.', 'R2_vmesto'),
            ('«в отдельные случаи [вместо того чтобы быть непрерывным]»', 'R2_vmesto'),
            ('при māraṇa вместо abhra', 'R2_vmesto'),
            ('Он понял знак в значении обещания.', 'R3_vznach')):
        diagnostic = style_diagnostics(prose)
        if rule in diagnostic['violations'] or rule not in diagnostic['ambiguous_rules']:
            fail('H1305 review: narrative prose was not classified ambiguous: %s' % prose)
    # `ed. Bomb.` INSIDE <ls>...</ls> (standalone or embedded) is NEVER a violation --
    # rewriting it would break src/pwg_sources.py's citation-key resolution.
    if scan_violations('(так <ls>ed. Bomb.</ls>)'):
        fail('H1305: in-<ls> standalone `ed. Bomb.` incorrectly flagged')
    if scan_violations('<ls>R. ed. Bomb. 3,69,4</ls>'):
        fail('H1305: in-<ls> embedded `ed. Bomb.` citation incorrectly flagged')
    # a genuine free-prose `ed. Bomb.` OUTSIDE any <ls> tag IS flagged (R4)
    if 'R4_bomb' not in scan_violations('<ls>Mālatīm.</ls> (ed. Bomb.) 304,1.'):
        fail('H1305: free-prose `ed. Bomb.` not flagged R4_bomb')
    # a clean row (no violations of any kind) scans empty
    if scan_violations('обычный чистый русский текст без нарушений'):
        fail('H1305: clean text incorrectly flagged')
    # sweep_text actually applies the fix a flagged violation predicts
    fixed, counts = sweep_text('ошибочно вместо {#X#}, читает <ls>ed. Bomb.</ls>')
    if 'вм.' not in fixed or 'ed. Bomb.' not in fixed:
        fail('H1305: sweep_text did not apply the terse form / kept in-<ls> siglum verbatim')
    if counts.get('R2_vmesto') != 1 or counts.get('R4_bomb') != 0:
        fail('H1305: sweep_text per-rule counts do not match the expected split')

    # The workflow gate consumes card.records[].senses[].russian directly. Notes,
    # differentia and German text cannot false-flag an otherwise-clean translation.
    results = [{
        'key': 'clean-notes',
        'card': {'notes': 'Переводчик пришёл.', 'records': [{'senses': [{
            'german': 'вместо', 'russian': 'чистый текст', 'differentia': 'пришёл',
        }]}]},
    }, {
        'key': 'multi-hard',
        'card': {'records': [{'senses': [
            {'russian': 'пришёл'},
            {'russian': 'ошибочно вместо {#X#}'},
        ]}]},
    }, {
        'key': 'narrative',
        'card': {'records': [{'senses': [{'russian': 'Он выступил вместо брата.'}]}]},
    }]
    _, flagged, warned = audit_workflow_results(results)
    if flagged != ['multi-hard']:
        fail('H1305 review: structured workflow flags wrong keys: %r' % flagged)
    if warned != ['narrative']:
        fail('H1305 review: ambiguous workflow warning wrong keys: %r' % warned)


def test_semantic_review_prioritizer():
    high = {
        'key': 'high',
        'card': {
            'key1': 'high',
            'iast': 'high',
            'records': [{
                'h': '1',
                'grammar': 'm.',
                'senses': [{
                    'tag': '1',
                    'german': '<ls>ṚV.</ls> Feuer',
                    'russian': 'мужской Ригведа {#agni',
                    'equivalence_type': 'equivalent',
                    'source_type': 'attested',
                    'stratum': 'Vedic',
                    'differentia': '',
                }],
            }],
            'notes': '',
        },
    }
    medium = {
        'key': 'medium',
        'card': {
            'key1': 'medium',
            'iast': 'medium',
            'records': [{
                'h': '1',
                'grammar': 'm.',
                'senses': [{
                    'tag': '1',
                    'german': 'Glanz, Schimmer',
                    'russian': 'блеск',
                    'equivalence_type': 'equivalent',
                    'source_type': 'lexicographic',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
            'notes': '',
        },
    }
    low = {
        'key': 'low',
        'card': {
            'key1': 'low',
            'iast': 'low',
            'records': [{
                'h': '1',
                'grammar': 'm.',
                'senses': [{
                    'tag': '1',
                    'german': 'Schein',
                    'russian': 'свет',
                    'equivalence_type': '',
                    'source_type': 'lexicographic',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
            'notes': '',
        },
    }
    formula = {
        'key': 'formula',
        'card': {
            'key1': 'formula',
            'iast': 'formula',
            'records': [{
                'h': '1',
                'grammar': 'ind.',
                'senses': [{
                    'tag': '1',
                    'german': 'iti arthaḥ',
                    'russian': 'смысл',
                    'equivalence_type': 'explanatory',
                    'source_type': 'lexicographic',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
            'notes': '',
        },
    }
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        path = f.name
        json.dump({'results': [medium, low, high, formula]}, f, ensure_ascii=False)
    try:
        report = audit_cards(path, review_limit=3)
        queue = report['review_queue']['items']
        queued_keys = [item['key'] for item in queue]
        if queued_keys[0] != 'high' or 'low' in queued_keys:
            fail('review queue did not prioritize high/medium risk before low risk')
        high_ids = {risk['id'] for card in report['cards'] if card['key'] == 'high'
                    for risk in card['risks']}
        expected_high = {
            'translated_grammar_siglum',
            'translated_source_siglum',
            'unbalanced_sanskrit_delimiters',
        }
        if not expected_high.issubset(high_ids):
            fail('markup/sigla leakage fixture missed: %s' %
                 ', '.join(sorted(expected_high - high_ids)))
        inv = {row['id']: row for row in report['formula_inventory']}
        if inv['formula_iti_arthah']['occurrences'] != 1 or inv['formula_iti_arthah']['missing_rendering'] != 1:
            fail('formula inventory did not count missing iti arthaḥ rendering')
        run([sys.executable, os.path.join(SRC, 'pilot', 'prompt_rule_audit.py'),
             '--cards', path, '--fail-on-high-risk'], expect=1)
    finally:
        os.remove(path)


def test_noisy_source_type_not_requeue():
    # A sense that DOES assert a meaning ({%..%} gloss span) but is marked attested with no
    # citation/stratum/lexicographic signal is the genuine review target — it must produce
    # the hint yet never enter the requeue set (REPORT_ONLY_RISKS, F-gate-nws-fp).
    noisy = {
        'key': 'noisy',
        'card': {
            'key1': 'noisy',
            'iast': 'noisy',
            'records': [{
                'h': '1',
                'grammar': 'm.',
                'senses': [{
                    'tag': '1',
                    'german': '{%Glanz%}',
                    'russian': 'блеск',
                    'equivalence_type': 'equivalent',
                    'source_type': 'attested',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
        },
    }
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        path = f.name
        json.dump({'results': [noisy]}, f, ensure_ascii=False)
    try:
        report = audit_cards(path, review_limit=3)
        ids = {risk['id'] for card in report['cards'] for risk in card['risks']}
        if 'suspicious_attested_without_text_signal' not in ids:
            fail('noisy source-type fixture did not produce expected review hint')
        if report.get('high_confidence_count') or report.get('requeue_keys'):
            fail('source-type review hint became high-confidence/requeue')
    finally:
        os.remove(path)


def test_report_only_risks_never_requeue():
    """The report-only semantic hints must be structurally barred from the requeue set:
    disjoint from HIGH_CONFIDENCE_RISKS (the only thing requeue_keys is built from)."""
    from prompt_rule_audit import HIGH_CONFIDENCE_RISKS, REPORT_ONLY_RISKS
    overlap = REPORT_ONLY_RISKS & HIGH_CONFIDENCE_RISKS
    if overlap:
        fail('REPORT_ONLY_RISKS leaked into the requeue-driving set: %s'
             % ', '.join(sorted(overlap)))
    if 'suspicious_attested_without_text_signal' not in REPORT_ONLY_RISKS:
        fail('suspicious_attested_without_text_signal must be report-only')


def test_attested_text_signal_redesign():
    """FL5 redesign of suspicious_attested_without_text_signal:
    - a pure cross-reference / erratum sense (no {%..%} gloss span) never fires, even with
      no card-level signal (it asserts no meaning to attest);
    - a lexicographic citation counts as a text signal for an attested meaning;
    - a real meaning gloss ({%..%}) marked attested with zero signal still fires (kept)."""
    def ids_for(sense):
        card = {'key': 'x', 'card': {'key1': 'x', 'iast': 'x', 'records': [
            {'h': '1', 'grammar': 'verb', 'senses': [sense]}]}}
        return {r['id'] for r in semantic_risks(card)}

    FLAG = 'suspicious_attested_without_text_signal'

    # 1) Cross-reference sense: {#paryanu#} <ab>s.</ab> {#paryanubanDa#} — no gloss span.
    crossref = {'tag': '1', 'german': '<div n="p">— {#paryanu#} <ab>s.</ab> {#paryanubanDa#} .',
                'russian': '<div n="p">— {#paryanu#} <ab>s.</ab> {#paryanubanDa#} .',
                'equivalence_type': 'explanatory', 'source_type': 'attested',
                'stratum': '', 'differentia': ''}
    if FLAG in ids_for(crossref):
        fail('cross-reference sense (no meaning claim) wrongly flagged as attested-without-signal')

    # 2) Erratum sense: <ab>Z.</ab> 3 lies ... — no gloss span, editorial correction.
    erratum = {'tag': 'corr', 'german': '<hom>1.</hom> {#nI#}¦ <ab>Z.</ab> 19. Lies: 3 <ab>st.</ab> 8.<info n="rev"/>',
               'russian': 'читай: 3 вместо 8', 'equivalence_type': 'explanatory',
               'source_type': 'attested', 'stratum': '', 'differentia': ''}
    if FLAG in ids_for(erratum):
        fail('erratum sense (no meaning claim) wrongly flagged as attested-without-signal')

    # 3) Lexicographic citation grounds an attested meaning gloss -> no flag.
    lexcite = {'tag': '1', 'german': 'Amarakośa: {%Stern%}', 'russian': 'звезда',
               'equivalence_type': 'equivalent', 'source_type': 'attested',
               'stratum': '', 'differentia': ''}
    if FLAG in ids_for(lexcite):
        fail('attested meaning with a lexicographic citation wrongly flagged')

    # 4) Genuine target survives: a {%..%} meaning gloss, attested, with no signal at all.
    genuine = {'tag': '1', 'german': '<lex>adj.</lex> {%sich rasch bewegend, eilend%}',
               'russian': '<lex>adj.</lex> {%быстро движущийся%}', 'equivalence_type': 'equivalent',
               'source_type': 'attested', 'stratum': '', 'differentia': ''}
    if FLAG not in ids_for(genuine):
        fail('a genuine attested meaning gloss without any signal must still surface the hint')


def test_nws_fp_suppressed():
    """Card-level text signal (head sense has <ls>) suppresses per-sense FP.
    Also: [NWS: OWNER] in equivalence_type counts as text signal."""
    # Case A: _zz_pw*-style card — head has <ls>, simple senses do not.
    pw_card = {
        'key': 'han~~h0_zz_pw00',
        'card': {
            'key1': 'han~~h0_zz_pw00',
            'iast': 'han',
            'records': [{
                'h': '1',
                'grammar': 'verb',
                'senses': [
                    {'tag': 'head', 'german': '<ls>R. ed. Bomb. 4,24,33</ls>',
                     'russian': 'введение', 'equivalence_type': 'explanatory',
                     'source_type': 'attested', 'stratum': '', 'differentia': ''},
                    {'tag': '1', 'german': '{%schlagen%}',
                     'russian': 'бить', 'equivalence_type': 'equivalent',
                     'source_type': 'attested', 'stratum': '', 'differentia': ''},
                    {'tag': '2', 'german': '{%abschlagen%}',
                     'russian': 'отбивать', 'equivalence_type': 'equivalent',
                     'source_type': 'attested', 'stratum': '', 'differentia': ''},
                ],
            }],
        },
    }
    # Case B: NWS sense — [NWS: OWNER] in equivalence_type only.
    nws_card = {
        'key': 'a~~h0_zz_nws00',
        'card': {
            'key1': 'a~~h0_zz_nws00',
            'iast': 'a',
            'records': [{
                'h': '1',
                'grammar': '',
                'senses': [{
                    'tag': 'NWS',
                    'german': '{#a#} [Gen , unsp] ohne Band',
                    'russian': 'без оков',
                    'equivalence_type': '[NWS: Graßmann 1873 (1996) : 81]',
                    'source_type': 'attested',
                    'stratum': '',
                    'differentia': '',
                }],
            }],
        },
    }
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        path = f.name
        json.dump({'results': [pw_card, nws_card]}, f, ensure_ascii=False)
    try:
        report = audit_cards(path, review_limit=5)
        ids = {risk['id'] for card in report['cards'] for risk in card['risks']}
        if 'suspicious_attested_without_text_signal' in ids:
            fail('F-gate-nws-fp: suspicious_attested_without_text_signal fired on '
                 'a card with card-level text signal or NWS owner citation')
    finally:
        os.remove(path)


def test_stale_refusal_preserves_requeue():
    os.makedirs(OUT, exist_ok=True)
    requeue_path = os.path.join(OUT, 'requeue.keys.txt')
    old = open(requeue_path, encoding='utf-8').read() if os.path.exists(requeue_path) else None
    sentinel = 'SELFTEST_SENTINEL\n'
    with open(requeue_path, 'w', encoding='utf-8') as f:
        f.write(sentinel)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        wf_path = f.name
        json.dump({'results': [{'key': 'not-current', 'card': {'ok': True}}]}, f)
    try:
        run([sys.executable, os.path.join(SRC, 'pilot', 'audit_window.py'),
             wf_path, '--root', 'sTA', '--write-requeue'], expect=2)
        got = open(requeue_path, encoding='utf-8').read()
        if got != sentinel:
            fail('stale audit overwrote requeue.keys.txt')
    finally:
        os.remove(wf_path)
        if old is None:
            try:
                os.remove(requeue_path)
            except FileNotFoundError:
                pass
        else:
            with open(requeue_path, 'w', encoding='utf-8') as f:
                f.write(old)


def test_fixture_audit_does_not_clobber_live_status():
    """FL8: a fixture/self-test audit run must NEVER overwrite the live singleton status files
    (window_status.json / audit_window.report.json). A temp-file wf auto-enables the guard, and
    --ephemeral forces it; either way the live OUT singletons are byte-identical afterward."""
    live = [os.path.join(OUT, 'window_status.json'),
            os.path.join(OUT, 'audit_window.report.json'),
            os.path.join(OUT, 'window_ledger.jsonl')]

    def snap(p):
        return open(p, 'rb').read() if os.path.exists(p) else None

    before = {p: snap(p) for p in live}
    fixture = {'meta': {'root': 'zzfixture'}, 'results': [
        {'key': 'zzfixture~~h0_00_pwg00', 'card': {'iast': 'zz', 'records': [
            {'h': '1', 'senses': [{'tag': '1', 'german': '{%Wasser%}', 'russian': 'вода',
             'equivalence_type': 'equivalent', 'source_type': 'attested',
             'stratum': '', 'differentia': ''}]}]}}]}
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        wf_path = f.name
        json.dump(fixture, f, ensure_ascii=False)
    try:
        # No expect() — a fixture may audit clean/blocked/stale; the guarantee under test is
        # only that the live singletons are not touched, whatever the exit code.
        subprocess.run([sys.executable, os.path.join(SRC, 'pilot', 'audit_window.py'),
                        wf_path, '--ephemeral'],
                       cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        after = {p: snap(p) for p in live}
        for p in live:
            if before[p] != after[p]:
                fail('ephemeral audit clobbered the live status file %s' % os.path.basename(p))
    finally:
        os.remove(wf_path)


def test_release_manifest_hash_validation():
    with tempfile.TemporaryDirectory() as tmp:
        edition = os.path.join(tmp, 'edition_selftest')
        write_minimal_edition(edition)
        run([sys.executable, os.path.join(SRC, 'validate_release.py'), edition], expect=0)
        with open(os.path.join(edition, 'reverse_index.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps({'ru': 'дым', 'key1': 'dhUma'}, ensure_ascii=False) + '\n')
        run([sys.executable, os.path.join(SRC, 'validate_release.py'), edition], expect=1)


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


def test_sense_dupe_batch_override():
    """The cross-part sense-duplicate exemption must be reproducible from the committed
    rootmap_overrides.json, NOT from a gitignored hand-edited rootmap (PROCESS_AUDIT rec 15)."""
    from audit_sense_dupes import allowed_batch_duplicate, rootmap_meta
    keys = ['x~~h0_00_pwg00', 'x~~h0_00_pwg01']
    declared = {k: {'batch_of': '1c'} for k in keys}
    if not allowed_batch_duplicate('1c', keys, declared):
        fail('a declared citation-split duplicate must be permitted')
    if allowed_batch_duplicate('1c', keys, {}):
        fail('an undeclared cross-part duplicate must NOT be permitted')
    # The committed override file must actually reach rootmap_meta() (jan 1c), independent
    # of whatever the gitignored jan.rootmap.json currently holds.
    entry = rootmap_meta().get('jan~~h0_00_pwg00') or {}
    if entry.get('batch_of') != '1c':
        fail('committed rootmap_overrides.json (jan 1c) not merged into rootmap_meta')


def test_sense_dupe_cross_level_exempt():
    """A flagged cross-part duplicate is legitimate when the root declares the (homonym, tag) as
    known cross-LEVEL sense-number reuse (verb vs derived-noun vs prefix-participle). siD h1 is
    the committed case (SIDH_DUPE_INVESTIGATION.md)."""
    from audit_sense_dupes import is_dupe_exempt, dupe_exempt_map
    exempt = dupe_exempt_map()
    keys = {'si_d~~h1_00_pwg00', 'si_d~~h1_00_pwg02'}
    if not is_dupe_exempt('h1', '3', keys, exempt):
        fail('declared siD cross-level reuse (h1 sense 3) must be exempt')
    if is_dupe_exempt('h1', '5', keys, exempt):
        fail('an undeclared tag must NOT be exempt')
    if is_dupe_exempt('h1', '3', {'si_d~~h1_00_pwg00', 'jan~~h1_00_pwg00'}, exempt):
        fail('a cross-root collision must never be exempt')


def test_requeue_transient_vs_defect_state():
    """Null cards (transient) must classify transient_only; a gate defect -> needs_requeue;
    a pre-split report (no requeue_defect key) must stay needs_requeue (PROCESS_AUDIT rec 3/10)."""
    from window_reports import audit_state
    base = {'root': 'zztest', 'keys': ['k1'], 'crashed': [], 'glue': {}}
    transient = dict(base, requeue=['k1'], requeue_transient=['k1'], requeue_defect=[])
    if audit_state(transient) != 'transient_only':
        fail('all-null requeue must classify as transient_only')
    defect = dict(base, requeue=['k1', 'k2'], requeue_transient=['k1'], requeue_defect=['k2'])
    if audit_state(defect) != 'needs_requeue':
        fail('a gate-defect requeue must classify as needs_requeue')
    legacy = dict(base, requeue=['k1'])  # pre-split report: no requeue_defect key
    if audit_state(legacy) != 'needs_requeue':
        fail('pre-split reports must remain needs_requeue (no silent transient downgrade)')
    import requeue_from_audit as rq
    with tempfile.TemporaryDirectory() as tmp:
        old_inp = rq.INP
        old_deny = rq.translation_memory.denylist_path
        try:
            rq.INP = tmp
            raw = os.path.join(tmp, 'k1.raw.txt')
            with open(raw, 'w', encoding='utf-8') as f:
                f.write('source')
            deny = os.path.join(tmp, 'deny.jsonl')
            rq.translation_memory.denylist_path = lambda out=None: deny
            no_fshas = os.path.join(tmp, 'no_fshas.txt')   # keep the frag channel out of scope
            n_en, _ = rq.append_tm_denylist('zz', ['k1'], 'defect', lang='en',
                                            fsha_file=no_fshas)
            n_ru, _ = rq.append_tm_denylist('zz', ['k1'], 'defect', lang='ru',
                                            fsha_file=no_fshas)
            if (n_en, n_ru) != (1, 1):
                fail('denylist should append one row per lang')
            rows = [json.loads(line) for line in open(deny, encoding='utf-8')]
            if rows[0]['lang'] != 'en' or not rows[0]['address'].startswith('en:'):
                fail('EN denylist address must carry en:<sha>')
            if rows[1]['lang'] != 'ru' or not rows[1]['address'].startswith('ru:'):
                fail('RU denylist address must carry ru:<sha>')
        finally:
            rq.INP = old_inp
            rq.translation_memory.denylist_path = old_deny


def test_export_translation_dedup():
    """Homograph fix: translations attach ONCE per key1, labelled by store homonym; a second
    same-key1 (homograph) entry must NOT repeat them (was the preview multiplication)."""
    from export_interop import card_glosses
    translations = {'dA': [{'ru': 'давать', 'subcard': 'dA~~h0_00_pwg00'},
                           {'ru': 'резать', 'subcard': 'dA~~h3_00_pwg00'}]}
    card = {'key1': 'dA', 'attested_senses': {}, 'records': []}
    emitted = set()
    t1 = [r for r in card_glosses(card, translations, emitted) if r[0] == 'approved_translation']
    t2 = [r for r in card_glosses(card, translations, emitted) if r[0] == 'approved_translation']
    if len(t1) != 2:
        fail('first homograph entry must carry both translations')
    if t2:
        fail('a second same-key1 entry must NOT repeat translations (homograph dedup)')
    if not (t1[0][1].startswith('h0-') and t1[1][1].startswith('h3-')):
        fail('each translation sense must be labelled by its store homonym')


def test_en_gate_strict_has_teeth():
    """FL2: the EN gate's --strict must FAIL on a null card (missing EN) and write a report;
    report-only (no --strict) must still exit 0. A null card used to slide through clean."""
    fixture = {'meta': {'root': 'zz'}, 'results': [
        {'key': 'zz~~h0_00_pwg00', 'card': {'iast': 'zz', 'records': [
            {'h': '1', 'senses': [{'tag': '1', 'german': '{%Wasser%}', 'english': 'water'}]}]}},
        {'key': 'zz~~h0_01_pwg01', 'card': None},
    ]}
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        wf_path = f.name
        json.dump(fixture, f, ensure_ascii=False)
    report_path = wf_path + '.report.json'
    en_audit = os.path.join(HERE, 'audit_window_en.py')
    try:
        # report-only: exit 0 even with a null card
        run([sys.executable, en_audit, wf_path, '--no-mw'], expect=0)
        # strict: null card must fail, and the report must record it
        run([sys.executable, en_audit, wf_path, '--no-mw', '--strict', '--report', report_path],
            expect=1)
        rep = json.load(open(report_path, encoding='utf-8'))
        if 'zz~~h0_01_pwg01' not in (rep.get('null_keys') or []):
            fail('EN gate report did not record the null key')
        if not rep.get('strict_reasons'):
            fail('EN gate report did not record a strict failure reason')
    finally:
        os.remove(wf_path)
        if os.path.exists(report_path):
            os.remove(report_path)


def test_en_gate_dup_has_teeth():
    """H169 defect 1: two senses in one record sharing identical english used to slide
    through clean — the only within-record duplicate signal was the soft SAME-GLOSS flag,
    gated on >=3 content words, so a short duplicate ("to go" / "to go") produced zero flags
    and --strict passed. DUP must fire HARD regardless of gloss length."""
    fixture = {'meta': {'root': 'zz'}, 'results': [
        {'key': 'zz~~h0_00_pwg00', 'card': {'iast': 'zz', 'records': [
            {'h': 'zz', 'senses': [
                {'tag': '1', 'german': '{%gehen%}', 'english': 'to go'},
                {'tag': '2', 'german': '{%gehen%}', 'english': 'to go'}]}]}},
    ]}
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        wf_path = f.name
        json.dump(fixture, f, ensure_ascii=False)
    report_path = wf_path + '.report.json'
    en_audit = os.path.join(HERE, 'audit_window_en.py')
    try:
        # report-only: still exits 0 even with the hard DUP flag present
        run([sys.executable, en_audit, wf_path, '--no-mw'], expect=0)
        run([sys.executable, en_audit, wf_path, '--no-mw', '--strict', '--report', report_path],
            expect=1)
        rep = json.load(open(report_path, encoding='utf-8'))
        if not any(fl['flag'].startswith('DUP') for ff in rep['files'] for fl in ff['flags']):
            fail('EN gate did not emit a DUP flag for two identical-english senses')
        if not any('hard flag' in r for r in rep.get('strict_reasons') or []):
            fail('EN gate report did not record a strict failure reason for the DUP hard flag')
    finally:
        os.remove(wf_path)
        if os.path.exists(report_path):
            os.remove(report_path)


def test_ru_gate_fails_loud_on_unparseable_child():
    """H169 defect 2: the RU gate used to recover child-auditor verdicts by regex-scraping
    prose stdout (`| flagged: ...`) — any wording drift in audit_translation.py /
    audit_coverage.py / audit_sense_dupes.py made the parser return [] and silently drop
    flagged cards from the requeue while the gate reported clean. The fixed parser must
    return None (never []) when the strict `FLAGGED_JSON:` verdict line is missing or
    malformed, so the caller can fail loud instead of passing silently."""
    from audit_window import parse_flagged_json
    drifted_stdout = 'FAIL: 2/5 units clean | flagged: root_a, root_b\n'
    if parse_flagged_json(drifted_stdout) is not None:
        fail('parser must return None (unparseable) when the child emits no FLAGGED_JSON '
             'line, not silently treat wording drift as a clean pass')
    malformed = 'FLAGGED_JSON: {not valid json\n'
    if parse_flagged_json(malformed) is not None:
        fail('parser must return None on malformed JSON, not crash or silently drop flags')
    clean_line = 'PASS: 5/5 units clean\nFLAGGED_JSON: []\n'
    if parse_flagged_json(clean_line) != []:
        fail('parser did not parse a genuinely clean FLAGGED_JSON: [] line')
    flagged_line = 'FAIL: 3/5 units clean | flagged: root_a, root_b\nFLAGGED_JSON: ["root_a", "root_b"]\n'
    if parse_flagged_json(flagged_line) != ['root_a', 'root_b']:
        fail('parser did not parse a well-formed FLAGGED_JSON line correctly')


def test_pwg_mask_latin_cue_behind_ab_tag():
    """Regression (review 2026-07-04): a Latin/Greek cue inside an <ab> span
    (e.g. `<ab>lat.</ab> {%ignis%}`) is masked to a {Tn} placeholder in mask()
    step 1, so classify_pct used to see "{T5}" instead of "lat." and misread the
    following {%...%} cognate as German — leaking Latin verbatim into the
    translator prompt. The cue must be recovered from the placeholder so the
    Latin gloss is masked, while a genuine German gloss stays inline. SHARED
    (masking runs before any --lang branch; identical for RU and EN)."""
    import pwg_mask
    body = 'Feuer <ab>lat.</ab> {%ignis%} und Wasser'
    sk, ph, st = pwg_mask.mask(body)
    if st['pct_la'] != 1 or st['pct_de'] != 0:
        fail('Latin cue behind <ab> not caught: %r' % st)
    if '{%ignis%}' in sk:
        fail('Latin gloss leaked into skeleton unmasked: %r' % sk)
    if pwg_mask.restore(sk, ph) != body:
        fail('mask round-trip not lossless after Latin-cue fix')
    # a genuine German gloss (no Latin cue) must still be kept inline for translation
    sk2, ph2, st2 = pwg_mask.mask('das <ab>Subst.</ab> {%Feuer%}')
    if st2['pct_de'] != 1 or st2['pct_la'] != 0:
        fail('German gloss wrongly masked as Latin: %r' % st2)


def test_markup_loss_soft_flag_ru():
    """S7 rec 1 (RU): a dropped {%..%} gloss wrapper is a SOFT, report-only signal —
    markup_wrapper_dropped fires at low severity and is NEVER a requeue trigger; a retained
    side-by-side {%German%} echo (required by the side-by-side convention) must NOT fire it."""
    from prompt_rule_audit import HIGH_CONFIDENCE_RISKS, semantic_risks

    def risks(german, russian):
        card = {'card': {'key1': 'x', 'iast': 'x', 'notes': '', 'records': [{
            'h': 'x', 'grammar': 'ind.', 'senses': [{
                'tag': '1', 'german': german, 'russian': russian,
                'equivalence_type': 'explanatory', 'source_type': 'lexicographic',
                'stratum': '', 'differentia': ''}]}]}}
        return semantic_risks(card)

    if 'markup_wrapper_dropped' in HIGH_CONFIDENCE_RISKS:
        fail('markup_wrapper_dropped must stay out of the requeue set (report-only)')
    dropped = [r for r in risks('{%nachgehen%}', 'следовать за')
               if r['id'] == 'markup_wrapper_dropped']
    if not dropped:
        fail('markup_wrapper_dropped did not fire on a dropped {%..%} wrapper')
    if dropped[0].get('level') != 'low' or dropped[0].get('high_confidence'):
        fail('markup_wrapper_dropped must be soft (low, non-high-confidence)')
    kept = risks('{%herfallen über%}', 'нападать на ({%herfallen über%})')
    if any(r['id'] == 'markup_wrapper_dropped' for r in kept):
        fail('markup_wrapper_dropped wrongly fired on a retained side-by-side {%..%} echo')


def test_markup_loss_soft_flag_en():
    """S7 rec 1 (EN): dropped {%..%} gloss wrappers are the dominant EN residual; the EN gate
    must flag them as SOFT MARKUP-LOSS — counted in the report but never hard, so --strict
    still exits 0 when MARKUP-LOSS is the only issue on a non-null card."""
    from audit_window_en import is_hard
    if is_hard('MARKUP-LOSS'):
        fail('MARKUP-LOSS must be a SOFT flag, never hard')
    fixture = {'meta': {'root': 'zz'}, 'results': [
        {'key': 'zz~~h0_00_pwg00', 'card': {'iast': 'zz', 'records': [
            {'h': '1', 'senses': [{'tag': '1',
             'german': '{%to fall upon%} {%to attack%}',
             'english': 'to fall upon, to attack'}]}]}},
    ]}
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        wf_path = f.name
        json.dump(fixture, f, ensure_ascii=False)
    report_path = wf_path + '.report.json'
    en_audit = os.path.join(HERE, 'audit_window_en.py')
    try:
        run([sys.executable, en_audit, wf_path, '--no-mw', '--strict', '--report', report_path],
            expect=0)
        rep = json.load(open(report_path, encoding='utf-8'))
        if rep.get('flag_counts', {}).get('MARKUP-LOSS', 0) < 1:
            fail('EN gate did not count the dropped {%..%} wrappers as MARKUP-LOSS')
        if rep.get('strict_reasons'):
            fail('a soft MARKUP-LOSS must not produce a strict failure reason')
    finally:
        os.remove(wf_path)
        if os.path.exists(report_path):
            os.remove(report_path)


def test_en_de_residue_french_guard():
    """EN analogue of the 2026-07-03 RU 'du'-vs-French collision fix (prompt_rule_audit.py):
    'des' is both a German article ("des Todes") and a French partitive article (as in "de
    basse extraction", a stock B&R euphemism for "of low birth"). gen_fidelity_judge_en.py's
    prompt explicitly preserves French literals verbatim, so a bare 'des' hit alongside
    another confirming French word must NOT fire DE-RESIDUE; genuine German residue ('des
    Todes', no other French markers) still must."""
    from audit_window_en import audit_sense
    _, soft_french = audit_sense('{%des basse extraction%}', 'des basse extraction')
    if any(s.startswith('DE-RESIDUE') for s in soft_french):
        fail('DE-RESIDUE wrongly fired on a preserved French literal ("des basse extraction")')
    _, soft_german = audit_sense('{%Todesangst%}', 'fear of des Todes')
    if not any(s.startswith('DE-RESIDUE') for s in soft_german):
        fail('DE-RESIDUE did not fire on genuine German residue ("des Todes")')


def test_h1152_guard3_xref_only_and_nws_de_locked():
    """H1152 guard 3 (H1070 finding #3, 12/170 FU1 rows): two deterministic "nothing was
    really translated here" shapes, flagged SOFT so a coverage consumer stops counting them
    as ordinary translated prose. Neither is a fidelity defect (markup/meaning stay intact),
    so neither may ever become a HARD flag."""
    from audit_window_en import audit_sense
    # XREF-ONLY: no {%..%} gloss wrapper -> only the cross-reference apparatus survives.
    hard_xref, soft_xref = audit_sense('Vgl. {#foo#} fgg.', 'Cf. {#foo#} and foll.')
    if 'XREF-ONLY' not in soft_xref:
        fail('XREF-ONLY did not fire on a pure cross-reference row (Vgl. ... fgg.)')
    if hard_xref:
        fail('a pure cross-reference row must never produce a HARD flag: %r' % hard_xref)
    # CONTROL: a real {%..%} gloss beside a cross-ref word must NOT fire XREF-ONLY.
    _, soft_real = audit_sense('{%to speak%} Vgl. {#foo#}', 'to speak; cf. {#foo#}')
    if 'XREF-ONLY' in soft_real:
        fail('XREF-ONLY wrongly fired on a row carrying real gloss prose')
    # NWS-DE-LOCKED: German trapped inside a {#..#} span never reached the translator.
    hard_locked, soft_locked = audit_sense('{#der Bote kommt#}', '{#der Bote kommt#}')
    if 'NWS-DE-LOCKED' not in soft_locked:
        fail('NWS-DE-LOCKED did not fire on German text trapped inside a {#..#} span')
    if hard_locked:
        fail('NWS-DE-LOCKED shape must never produce a HARD flag: %r' % hard_locked)
    # CONTROL: genuine Sanskrit/IAST inside {#..#} must NOT fire NWS-DE-LOCKED.
    _, soft_san = audit_sense('{%to speak%} {#vac#}', 'to speak {#vac#}')
    if 'NWS-DE-LOCKED' in soft_san:
        fail('NWS-DE-LOCKED wrongly fired on genuine Sanskrit inside a {#..#} span')


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
    """FL4: en_residual_keys 'done' means coverage-complete, not '>=1 English sense'. A card
    with 1 of 2 senses translated is a residual (its 1 untranslated sense must not be hidden);
    a fully-translated card is done; a null/empty card is never done."""
    from en_residual_keys import card_done, en_coverage
    partial = {'records': [{'senses': [{'german': 'a', 'english': 'x'}, {'german': 'b'}]}]}
    if en_coverage(partial) != (1, 2):
        fail('en_coverage miscounted the partial card')
    if card_done(partial):
        fail('a 1/2-sense card must NOT count as done (the FL4 1/40 bug)')
    full = {'records': [{'senses': [{'german': 'a', 'english': 'x'},
                                    {'german': 'b', 'english': 'y'}]}]}
    if not card_done(full):
        fail('a fully-translated card must count as done')
    if card_done(None) or card_done({'records': []}):
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


def test_autosplit_topup_targets_and_reassembles():
    """Item-1 (ka): a partial card's missing_fragments drive a TARGETED top-up, not a full
    re-split. Using ka's real 81-fragment / 41-group plan: mark 2 groups missing (the rest
    resolved via frag_prov), assert topup_fragments targets ONLY those 2 groups' fragments,
    then feed synthetic recoveries and assert stitch_topup reassembles a COMPLETE ka card."""
    import autosplit_requeue as ar
    import translation_memory as tm
    from window_common import input_paths, read_text
    if not os.path.exists(input_paths('ka')[0]):
        return  # ka input not present in this checkout — nothing to assert
    raw = read_text(input_paths('ka')[0])
    groups = ar.frag_groups(raw)
    if len(groups) < 3:
        return
    lang, field = 'ru', 'russian'
    missing_gi = {len(groups) - 1, len(groups) - 2}     # the last 2 groups fail

    def senses_for(text, marker):
        return [{'tag': '1', 'german': text[:16], 'russian': marker,
                 'equivalence_type': 'equivalent', 'source_type': 'attested',
                 'stratum': '', 'differentia': ''}]

    frag_prov, missing_ids = [], []
    for gi, g in enumerate(groups):
        for fi, (si, pi, text) in enumerate(g):
            if gi in missing_gi:
                missing_ids.append('g%d:f%d' % (gi + 1, fi))
            else:
                frag_prov.append({'fsha': tm.frag_address(lang, text),
                                  'senses': senses_for(text, 'resolved')})
    partial_card = {'key1': 'ka', 'iast': 'ka', 'partial': True,
                    'missing_fragments': missing_ids, 'frag_prov': frag_prov,
                    'records': [{'h': '1', 'senses': []}]}
    wf = {'meta': {'root': 'ka', 'lang': lang},
          'results': [{'key': 'ka', 'card': partial_card}]}
    fd, wf_path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    with open(wf_path, 'w', encoding='utf-8') as f:
        json.dump(wf, f, ensure_ascii=False)
    try:
        cards = ar.topup_fragments(wf_path, lang)
    finally:
        os.remove(wf_path)
    if len(cards) != 1:
        fail('topup_fragments did not surface the single partial ka card')
    c = cards[0]
    expected_missing = sum(len(groups[gi]) for gi in missing_gi)
    if len(c['missing']) != expected_missing:
        fail('topup targeted %d fragments, expected %d (the 2 missing groups only)'
             % (len(c['missing']), expected_missing))
    if len(c['missing']) >= len(c['plan']):
        fail('topup did not reduce the fragment set — it re-planned the whole card')

    # feed synthetic recoveries for the missing fragments -> expect a COMPLETE card
    manifest_card = {'orig': c['orig'], 'iast': c['iast'], 'h': c['h'],
                     'plan': [{'s': r['s'], 'p': r['p'], 'fsha': r['fsha'],
                               'fk': r['fk'], 'missing': r['missing']} for r in c['plan']],
                     'resolved': c['resolved']}
    got = {ar.fk_of('ka', si, pi): senses_for(text, 'recovered')
           for (si, pi, text) in c['missing']}
    results, still_missing = ar.stitch_topup([manifest_card], got, field)
    row = results[0]
    if row['partial'] or not row['card']:
        fail('topup-merge left ka partial after every missing fragment was recovered')
    if still_missing:
        fail('no fragments should remain missing after full recovery')
    n_senses = len({r['s'] for r in c['plan']})
    if len(row['card']['records'][0]['senses']) != n_senses:
        fail('reassembled ka is missing senses: %d vs %d source sense-ords'
             % (len(row['card']['records'][0]['senses']), n_senses))

    # a still-failing missing fragment must keep the card partial (never silently complete)
    partial_got = dict(got)
    a_missing = ar.fk_of('ka', c['missing'][0][0], c['missing'][0][1])
    partial_got[a_missing] = None
    presults, pmissing = ar.stitch_topup([manifest_card], partial_got, field)
    if not presults[0]['partial'] or a_missing not in (pmissing.get('ka') or []):
        fail('a still-failing fragment must keep the card partial with its fk recorded')


def test_whitney_homonym_safety():
    """FL1: requesting a Whitney homonym a root lacks must return EMPTY, never fall back to
    ALL homonyms — attaching a different homonym's grammar is a silent wrong-root error."""
    from whitney_grammar import grammar_for
    all_vas = grammar_for('vas')
    if len(all_vas) < 2:
        return  # whitney_grammar.json unbuilt in this env — nothing to assert
    first = all_vas[0]['homonym']
    exact = grammar_for('vas', first)
    if len(exact) != 1 or exact[0]['homonym'] != first:
        fail('an exact homonym request must return only that homonym')
    if grammar_for('vas', '999') != []:
        fail('a nonexistent homonym must return empty, not fall back to all homonyms')
    if grammar_for('zzqqx_no_such_root', '1') != []:
        fail('an unknown root must return empty')


def test_translation_memory_addressing():
    """TM sidecar: content-addressing rules — only sub-cards with one agreed source SHA and a
    complete translation are cached; SHA-disagreement / missing-translation / no-SHA are
    skipped (never guessed), and reconstruction rebuilds the wf-card sense shape."""
    import translation_memory as tm
    tm.selftest()   # raises AssertionError on any rule violation


def test_tm_pre_resolves_cards():
    """--tm plumbing end-to-end: a card whose source SHA is in the TM is pre-resolved (emitted
    in TM_RESOLVED, excluded from every translate lane), and the total-accounting invariant
    (tm ∪ batched ∪ presplit == selected, disjoint) holds. Uses a real root's on-disk inputs."""
    import gen_opt_harness2 as gh
    from window_common import rootmap_path, input_paths, sha256_file, read_text
    root = 'gam'
    rmpath, _ = rootmap_path(root)
    if not rmpath:
        return  # inputs not present in this checkout — nothing to assert
    rootmap, keys = gh.selected_keys(root, None)
    keys = [k for k in keys if os.path.exists(input_paths(k)[0])][:6]
    if len(keys) < 3:
        return
    cached = keys[:2]
    fd, tmfile = tempfile.mkstemp(suffix='.json'); os.close(fd)
    try:
        entries = {}
        for k in cached:
            raw_path = input_paths(k)[0]
            sha = sha256_file(raw_path)
            entries['ru:%s' % sha] = {'card': {'key1': k, 'iast': None,
                'records': [{'h': None, 'senses': [{'tag': '1', 'german': read_text(raw_path), 'russian': 'р',
                    'equivalence_type': 'equivalent', 'source_type': 'attested',
                    'stratum': '', 'differentia': ''}]}]}, 'src_key': k}
        with open(tmfile, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.translation_memory.v1', 'lang': 'ru',
                       'entries': entries}, f, ensure_ascii=False)
        js, batches = gh.build(root, keys, rootmap, 12000, tm_path=tmfile)
        import re as _re
        meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
        tm_hits = set(meta['tm_hits'])
        if tm_hits != set(cached):
            fail('TM should pre-resolve exactly the cached keys, got %s' % sorted(tm_hits))
        batched = {k for b in meta['batches'] for k in b}
        if tm_hits & batched:
            fail('a TM-resolved card must not also be in a translate batch')
        if tm_hits & set(meta['presplit_keys']):
            fail('a TM-resolved card must not also be in the presplit lane')
        union = tm_hits | batched | set(meta['presplit_keys'])
        if union != set(keys):
            fail('accounting: tm ∪ batched ∪ presplit must equal selected keys')
        inputs = json.loads(_re.search(r'^const INPUTS = (.*)$', js, _re.M).group(1))
        ph = json.loads(_re.search(r'^const PH = (.*)$', js, _re.M).group(1))
        if tm_hits & set(inputs):
            fail('TM-resolved cards must not be inlined in INPUTS: %s' % sorted(tm_hits & set(inputs)))
        if tm_hits & set(ph):
            fail('TM-resolved cards must not be inlined in PH: %s' % sorted(tm_hits & set(ph)))
        if set(inputs) != batched | set(meta['presplit_keys']):
            fail('INPUTS must contain exactly agent-reachable keys')
    finally:
        try:
            os.remove(tmfile)
        except OSError:
            pass


def test_tm_card_sane_rejects_zero_marker_drift():
    """A cached card with zero citations/Sanskrit markers must not satisfy a cited source."""
    import gen_opt_harness2 as gh
    raw = '{#agni#}¦ Feuer <ls>RV. 1</ls>.'
    card = {'records': [{'senses': [{'tag': '1', 'german': 'Feuer',
                                     'russian': 'огонь'}]}]}
    ok, why = gh.tm_card_sane(card, 'ru', 'russian', raw)
    if ok or '<ls>' not in why:
        fail('zero-<ls> cached card must be refused for cited source, got ok=%r why=%r' %
             (ok, why))
    raw2 = '{#agni#}¦ Feuer.'
    card2 = {'records': [{'senses': [{'tag': '1', 'german': 'Feuer',
                                      'russian': 'огонь'}]}]}
    ok2, why2 = gh.tm_card_sane(card2, 'ru', 'russian', raw2)
    if ok2 or '{#' not in why2:
        fail('zero-{# cached card must be refused for Sanskrit-marked source, got ok=%r why=%r' %
             (ok2, why2))


def test_generated_harness_strict_key_matching():
    """Generated JS must not positionally assign a returned full card to another key."""
    import gen_opt_harness2 as gh
    raw = '<L>1<pc>1<k1>a<k2>a<h>1\n{#a#}¦ {%eins%}.\n'
    d = tempfile.mkdtemp()
    keys = ['zz_key_a', 'zz_key_b']
    saved_ip = gh.input_paths
    try:
        for k in keys:
            with open(os.path.join(d, k + '.raw.txt'), 'w', encoding='utf-8') as f:
                f.write(raw)
            with open(os.path.join(d, k + '.portrait.json'), 'w', encoding='utf-8') as f:
                f.write('{}')
        gh.input_paths = lambda k, input_dir=None: (
            os.path.join(d, k + '.raw.txt'), os.path.join(d, k + '.portrait.json'))
        js, _batches = gh.build('zz', keys, None, 12000, nominal=True,
                                grammar_on=False, tm_path=None)
        # km[k] (the exact expected key) is always the PRIMARY match. H220 added a
        # nominal-only SLP1-echo fallback (re-key via nominal_keymap), so the binding is
        # `let cand = km[k]` now — still key-based, never positional.
        if 'let cand = km[k]' not in js:
            fail('full-card lane must use strict key lookup (km[k]), not positional fallback')
        if 'res.cards[i]' in js or 'res.cards[idx], fi' in js:
            fail('generated harness still has unsafe positional response assignment')
        if 'missing-or-mismatched-key' not in js:
            fail('missing/mismatched full-card keys must get an explicit failure reason')
        if 'missing-or-mismatched-fragment-key' not in js:
            fail('missing/mismatched fragment keys must get an explicit failure reason')
    finally:
        gh.input_paths = saved_ip
        shutil.rmtree(d, ignore_errors=True)


def test_tm_auto_no_sidecar_metadata():
    """Default CLI semantics are --tm=auto: if the sidecar is missing, generation continues
    normally and records the no-op in META instead of silently changing lanes."""
    import re as _re
    import gen_opt_harness2 as gh
    from window_common import rootmap_path, input_paths
    root = 'gam'
    rmpath, _ = rootmap_path(root)
    if not rmpath:
        return
    rootmap, keys = gh.selected_keys(root, None)
    keys = [k for k in keys if os.path.exists(input_paths(k)[0])][:3]
    if not keys:
        return
    missing_tm = os.path.join(tempfile.gettempdir(), 'missing_pwg_tm_selftest_%s.json' % os.getpid())
    try:
        os.remove(missing_tm)
    except OSError:
        pass
    js, _batches = gh.build(root, keys, rootmap, 12000, tm_path=missing_tm, tm_auto=True)
    meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
    if not meta.get('tm_auto'):
        fail('META.tm_auto must be true for --tm=auto/default generation')
    if meta.get('tm_available'):
        fail('META.tm_available must be false when the auto sidecar is absent')
    if meta.get('tm_cards') != 0 or meta.get('tm_hits'):
        fail('missing auto TM sidecar must not pre-resolve any cards')
    owed = {k for b in meta['batches'] for k in b} | set(meta['presplit_keys']) | set(meta['degenerate_passthrough_keys'])
    if owed != set(keys):
        fail('missing auto TM sidecar must keep every selected key owed/accounted')


def test_suggest_tm_does_not_skip_agents():
    """Suggestion TM is prompt context only: it must appear in META/SUGGEST_TM but leave
    tm_hits empty and keep the selected key owed by a normal translate lane."""
    import re as _re
    import gen_opt_harness2 as gh
    from window_common import rootmap_path, input_paths
    root = 'gam'
    rmpath, _ = rootmap_path(root)
    if not rmpath:
        return
    rootmap, keys = gh.selected_keys(root, None)
    keys = [k for k in keys if os.path.exists(input_paths(k)[0])][:1]
    if not keys:
        return
    with tempfile.TemporaryDirectory() as tmp:
        suggest = os.path.join(tmp, 'translation_memory.suggest.ru.jsonl')
        with open(suggest, 'w', encoding='utf-8') as f:
            f.write(json.dumps({'schema': 'pwg.translation_memory.suggest.v1',
                                'lang': 'ru', 'key': keys[0],
                                'score_de_fragment': 0.4,
                                'score_sa_headword': 1.0,
                                'score_semantic_tag': 0.7,
                                'score_combined': 0.88,
                                'trust_level': 'suggestion', 'reuse_policy': 'suggest_only',
                                'source_kind': 'curated_sa_ru_terminology',
                                'provenance_note': 'fixture curated term',
                                'text': 'advisory only'}, ensure_ascii=False) + '\n')
            f.write(json.dumps({'schema': 'pwg.translation_memory.suggest.v1',
                                'lang': 'ru', 'key': keys[0],
                                'trust_level': 'suggestion', 'reuse_policy': 'suggest_only',
                                'source_kind': 'mw_seed',
                                'score_combined': 1.0,
                                'text': 'must be filtered'}, ensure_ascii=False) + '\n')
        js, _batches = gh.build(root, keys, rootmap, 12000, tm_path=None, suggest_tm_path=suggest)
        meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
        suggest_const = json.loads(_re.search(r'^const SUGGEST_TM = (.*)$', js, _re.M).group(1))
        if meta.get('tm_hits') or meta.get('tm_cards') != 0:
            fail('suggestion TM must not create exact TM hits')
        if meta.get('suggest_tm_cards') != keys:
            fail('suggestion TM metadata must list the advisory key')
        if keys[0] not in suggest_const:
            fail('generated harness must emit SUGGEST_TM advisory rows')
        if len(suggest_const[keys[0]]) != 1:
            fail('malformed/raw-MW RU suggestion row must be filtered before prompt injection')
        if suggest_const[keys[0]][0].get('score_de_fragment') != 0.4:
            fail('separate fuzzy evidence scores must survive load/render round-trip')
        for needle in ('score_de_fragment', 'score_sa_headword', 'score_semantic_tag',
                       "'de='", "'sa='", "'tag='"):
            if needle not in js:
                fail('suggestion prompt must render separate evidence-channel scores')
        owed = {k for b in meta['batches'] for k in b} | set(meta['presplit_keys']) | set(meta['degenerate_passthrough_keys'])
        if keys[0] not in owed:
            fail('suggestion TM must not remove the key from agent work lanes')


def test_tm_publication_fixtures_validate():
    """Tracked fixtures pin the publication-grade TM row contract."""
    import translation_memory as tm
    valid = os.path.join(SRC, 'fixtures', 'translation_memory_valid.fixture.jsonl')
    invalid = os.path.join(SRC, 'fixtures', 'translation_memory_invalid.fixture.jsonl')
    rows = [json.loads(line) for line in open(valid, encoding='utf-8') if line.strip()]
    ok, why = tm.validate_suggestion_row(rows[0], lang='ru')
    if not ok:
        fail('valid suggestion fixture rejected: %s' % why)
    ok, why = tm.validate_frag_entry(rows[1], lang='ru')
    if not ok:
        fail('valid fragment fixture rejected: %s' % why)
    bad = [json.loads(line) for line in open(invalid, encoding='utf-8') if line.strip()]
    reasons = []
    for row in bad:
        ok, why = tm.validate_suggestion_row(row, lang='ru')
        if ok:
            fail('invalid suggestion fixture unexpectedly passed')
        reasons.append(why)
    if 'raw MW English seed is forbidden for RU' not in reasons:
        fail('invalid fixture must pin raw MW English rejection')
    if 'score_de_fragment must be a number 0..1' not in reasons:
        fail('invalid fixture must pin score-channel range validation')


def test_degenerate_passthrough_accounted():
    """A safely-degenerate cross-reference stub is emitted as an accounted, SCHEMA-VALID no-LLM row
    and is excluded from translation lanes. N-3/R7 (C-07): the card MUST pass
    validate_final_card_schema (record h + grammar present, not null) so one xref stub can no longer
    make save_and_audit refuse a whole paid window -- and this assertion must never silently skip on
    an absent file fixture."""
    import re as _re
    import gen_opt_harness2 as gh
    import validate_final_card_schema as vs
    # Inline stub -> no filesystem dependency, so the schema assertion below can never be skipped.
    card = gh.degenerate_passthrough_card('ab~~h0_zz_pw', '=== LAYER: PW ===\n\nvgl. {#agni#}',
                                          '[]', 'russian')
    if not card or not card.get('degenerate_passthrough'):
        fail('inline vgl.-stub should qualify for conservative degenerate pass-through')
    vs.validate_card(card)                     # R7/C-07: raises on any schema violation
    rec = card['records'][0]
    if rec.get('h') is None or 'grammar' not in rec:
        fail('degenerate record must carry a non-null h and a grammar field (RECORD_REQUIRED)')
    # File-fixture-dependent accounting -- an EXPLICIT conditional, never a silent top-of-function return.
    from window_common import input_paths, read_text
    rp, pp = input_paths('ab')
    if os.path.exists(rp) and os.path.exists(pp):
        js, batches = gh.build('ab', ['ab'], None, 12000, nominal=True, tm_path=None)
        meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
        if meta.get('degenerate_passthrough_keys') != ['ab']:
            fail('META.degenerate_passthrough_keys must account for the stub key')
        if batches or meta.get('presplit_keys'):
            fail('a degenerate pass-through key must not also enter an agent translation lane')
        if 'const DEGENERATE_RESOLVED' not in js or 'degenerate_passthrough: true' not in js:
            fail('generated harness must emit explicit degenerate pass-through rows')


def test_degenerate_passthrough_rejects_glosses():
    import gen_opt_harness2 as gh
    import perf_preflight as pp
    raw = """=== LAYER: PWG — MAIN ENTRY ===
{#agni#}¦ {%Feuer%}, <ls>RV.</ls>
"""
    if gh.degenerate_passthrough_card('agni', raw, '{"key1":"agni"}', 'russian'):
        fail('cards with German gloss blocks must not enter deterministic pass-through')
    if pp.near_degenerate_reason('agni', raw, '{"key1":"agni"}', 'russian'):
        fail('cards with German gloss blocks must not be suggested as near-degenerate stubs')
    correction = """=== LAYER: PWG — MAIN ENTRY ===
{#as#}¦ <ab>vgl.</ab> mit {#aBi#} <ab>Z.</ab> 9 <ab>v. u.</ab> lies: {#etattrikam#}.
"""
    if gh.degenerate_passthrough_card('as', correction, '{"key1":"as"}', 'russian'):
        fail('editorial correction prose (lies:) must stay out of deterministic pass-through')
    if 'editorial correction prose' not in (pp.near_degenerate_reason('as', correction, '{"key1":"as"}', 'russian') or ''):
        fail('preflight should explain why correction prose is report-only')
    strike = """=== LAYER: PWG — MAIN ENTRY ===
{#vid#}¦ <ab>Z.</ab> 5 ist ein {#tasya#} zu streichen.
"""
    if gh.degenerate_passthrough_card('vid', strike, '{"key1":"vid"}', 'russian'):
        fail('editorial correction prose (streichen) must stay out of deterministic pass-through')


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


def test_verb_worklist_excludes_missing_rootmaps():
    import verb_worklist as vw
    with tempfile.TemporaryDirectory() as tmp:
        preverb = os.path.join(tmp, 'pwg_preverb1.txt')
        manifest = os.path.join(tmp, 'scale_manifest.freq.json')
        store = os.path.join(tmp, 'pwg_ru_translated.jsonl')
        rootmaps = os.path.join(tmp, 'input')
        os.makedirs(rootmaps, exist_ok=True)
        with open(preverb, 'w', encoding='utf-8') as f:
            f.write(';; Case 1: L=1, k1=SrI, k2=x, code=x,\n')
            f.write(';; Case 2: L=2, k1=dah, k2=x, code=x,\n')
        with open(manifest, 'w', encoding='utf-8') as f:
            json.dump([
                {'key1': 'SrI', 'score': 99.0, 'band': 5, 'bytes': 900},
                {'key1': 'dah', 'score': 10.0, 'band': 5, 'bytes': 100},
            ], f)
        with open(store, 'w', encoding='utf-8') as f:
            f.write('')
        with open(os.path.join(rootmaps, 'dah.rootmap.json'), 'w', encoding='utf-8') as f:
            json.dump({'meta': {'root': 'dah'}, 'items': []}, f)

        payload = vw.build_worklist(preverb=preverb, manifest=manifest,
                                    store=store, rootmap_dir=rootmaps)
        if payload.get('remaining') != ['SrI', 'dah']:
            fail('verb_worklist must preserve the raw score-ranked backlog')
        if payload.get('runnable_remaining') != ['dah']:
            fail('verb_worklist --top must be backed by runnable roots only')
        if payload.get('blocked_missing_rootmap') != ['SrI']:
            fail('missing-rootmap roots must remain visible in blocked_missing_rootmap')
        if payload.get('remaining_count') != 2 or payload.get('runnable_count') != 1:
            fail('verb_worklist count fields must distinguish backlog from runnable queue')
        if payload.get('remaining_bytes') != 1000 or payload.get('runnable_bytes') != 100:
            fail('verb_worklist byte fields must distinguish backlog from runnable queue')


def test_coordinator_state_dashboard_and_cap():
    import coordinator
    old = os.environ.get('PWG_COORDINATOR_DIR')
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        try:
            state = coordinator.default_state()
            for i in range(3):
                state['leases'].append({
                    'id': 'lease%d' % i,
                    'lane': 'lane%d' % i,
                    'kind': 'verb',
                    'owner': 'selftest',
                    'target': 'root%d' % i,
                    'state': 'prepared',
                    'artifact_dir': os.path.join(tmp, 'artifacts', 'lease%d' % i),
                })
            coordinator.save_state(state)
            loaded = coordinator.load_state()
            if len(coordinator.reserved_translation_leases(loaded)) != 3:
                fail('coordinator must count exactly three reserved translation leases')
            if coordinator.running_translation_leases(loaded):
                fail('prepared leases must not consume runtime slots')
            dash = json.load(open(os.path.join(tmp, 'dashboard.json'), encoding='utf-8'))
            if dash.get('schema') != coordinator.DASHBOARD_SCHEMA:
                fail('coordinator dashboard schema missing')
            if (dash.get('reserved_translation_leases') != 3
                    or dash.get('running_translation_leases') != 0
                    or dash.get('active_translation_leases') != 0
                    or dash.get('runtime_limit') != 3
                    or dash.get('runtime_mode') != 'standard'):
                fail('coordinator dashboard must distinguish reserved and running state')
            coordinator.begin_run_leases(loaded, ['lease0', 'lease1', 'lease2'])
            if len(coordinator.active_translation_leases(loaded)) != 3:
                fail('deprecated active alias must equal the running count')
            state['leases'][0]['state'] = 'promoted'
            coordinator.save_state(state)
            if len(coordinator.reserved_translation_leases(coordinator.load_state())) != 2:
                fail('promoted leases must not count against reserved work')
        finally:
            if old is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old


def test_coordinator_nominal_reservations():
    """Nominal batches own every canonical key, including migrated legacy leases."""
    import coordinator
    old_coord = os.environ.get('PWG_COORDINATOR_DIR')
    old_here = coordinator.HERE
    old_store = coordinator.promote_final_cards.DEFAULT_STORE
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = os.path.join(tmp, 'coord')
        coordinator.HERE = os.path.join(tmp, 'pilot')
        os.makedirs(os.path.join(coordinator.HERE, 'input'))
        store = os.path.join(tmp, 'store.jsonl')
        open(store, 'w', encoding='utf-8').close()
        coordinator.promote_final_cards.DEFAULT_STORE = store
        manifest = os.path.join(tmp, 'manifest.json')
        with open(manifest, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.headless_execution_manifest.v1',
                       'meta': {'selected_keys': ['c_safe'],
                                'nominal_keymap': {'c_safe': 'c'}}}, f)
        try:
            state = coordinator.default_state()
            state['leases'] = [
                {'id': 'details-legacy', 'kind': 'nominal', 'state': 'prepared',
                 'details': {'keys': ['a', 'b']}},
                {'id': 'manifest-legacy', 'kind': 'nominal', 'state': 'prepared',
                 'execution_manifest': manifest},
            ]
            coordinator.save_state(state)
            migrated = coordinator.load_state()
            if migrated['leases'][0].get('reserved_keys') != ['a', 'b']:
                fail('legacy details.keys reservation was not migrated')
            if migrated['leases'][1].get('reserved_keys') != ['c']:
                fail('legacy manifest nominal_keymap reservation was not migrated')
            if coordinator.active_reserved_nominal_keys(migrated) != {'a', 'b', 'c'}:
                fail('active nominal reservations did not include every batch key')

            cards = os.path.join(tmp, 'cards.jsonl')
            with open(cards, 'w', encoding='utf-8') as f:
                for key in ('b', 'd'):
                    f.write(json.dumps({'key1': key}) + '\n')
                    stem = coordinator.safe_name(key)
                    open(os.path.join(coordinator.HERE, 'input', stem + '.raw.txt'),
                         'w', encoding='utf-8').close()
                    open(os.path.join(coordinator.HERE, 'input', stem + '.portrait.json'),
                         'w', encoding='utf-8').close()
            if coordinator.nominal_candidates(migrated, batch_size=5, cards_path=cards) != ['d']:
                fail('nominal candidate selection reused a non-first reserved batch key')

            try:
                coordinator.register_prepared_lease(
                    'overlap', 'test', ['b', 'd'], 'harness.js', manifest, 'preflight.json')
            except SystemExit as exc:
                if 'already active' not in str(exc):
                    raise
            else:
                fail('overlapping prepared nominal lease was accepted')

            # An unresolved active legacy lease blocks every new nominal claim; terminal history
            # is harmless and must not freeze the queue forever.
            state = coordinator.load_state()
            state['leases'].append({'id': 'unknown', 'kind': 'nominal', 'state': 'prepared'})
            coordinator.save_state(state)
            try:
                coordinator.active_reserved_nominal_keys(coordinator.load_state())
            except SystemExit as exc:
                if 'unresolved reservations' not in str(exc):
                    raise
            else:
                fail('unresolved active legacy lease did not fail closed')
            state = coordinator.load_state()
            state['leases'][-1]['state'] = 'blocked'
            coordinator.save_state(state)
            if coordinator.active_reserved_nominal_keys(coordinator.load_state()) != {'a', 'b', 'c'}:
                fail('terminal unresolved legacy lease incorrectly blocked reservations')

            barrier = threading.Barrier(2)
            outcomes = []

            def register_race(lease_id):
                barrier.wait()
                try:
                    coordinator.register_prepared_lease(
                        lease_id, 'test', ['e', 'f'], 'harness.js', manifest,
                        'preflight.json')
                    outcomes.append('accepted')
                except SystemExit:
                    outcomes.append('rejected')

            racers = [threading.Thread(target=register_race, args=('race%d' % i,))
                      for i in range(2)]
            for racer in racers:
                racer.start()
            for racer in racers:
                racer.join(5)
            if sorted(outcomes) != ['accepted', 'rejected']:
                fail('simultaneous overlapping nominal reservations were not serialized')
        finally:
            coordinator.HERE = old_here
            coordinator.promote_final_cards.DEFAULT_STORE = old_store
            if old_coord is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old_coord


def test_coordinator_runtime_state_machine_and_cas():
    """Runtime caps, probe authorization, lock responsiveness, and stale completions."""
    import coordinator
    from types import SimpleNamespace

    old_coord = os.environ.get('PWG_COORDINATOR_DIR')
    original_run = coordinator.run_cmd
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        try:
            state = coordinator.default_state()
            for i in range(5):
                state['leases'].append({
                    'id': 'run%d' % i, 'kind': 'verb', 'target': 'root%d' % i,
                    'state': 'prepared', 'artifact_dir': os.path.join(tmp, 'a%d' % i),
                })
            coordinator.begin_run_leases(state, ['run0', 'run1', 'run2'])
            try:
                coordinator.begin_run_leases(state, ['run3'])
            except SystemExit as exc:
                if 'runtime cap' not in str(exc):
                    raise
            else:
                fail('standard runtime accepted a fourth lease')

            state = coordinator.default_state()
            for i in range(5):
                state['leases'].append({
                    'id': 'stage%d' % i, 'kind': 'verb', 'target': 'root%d' % i,
                    'state': 'prepared', 'artifact_dir': os.path.join(tmp, 's%d' % i),
                })
            receipt = os.path.join(tmp, 'receipt.json')
            with open(receipt, 'w', encoding='utf-8') as f:
                json.dump({
                    'schema': coordinator.PROBE_RECEIPT_SCHEMA,
                    'generated_at': coordinator.utc_now(), 'run_id': 'acceptance-1',
                    'model': coordinator.PROBE_MODEL, 'policy': coordinator.PROBE_POLICY,
                    'go': True, 'lease_ids': ['stage%d' % i for i in range(5)],
                    'healthy_profiles': ['c1', 'c2', 'c3', 'c4'],
                    'probe_latency_ms': {'c1': 10, 'c2': 11, 'c3': 12, 'c4': 13},
                }, f)
            coordinator.begin_run_leases(
                state, ['stage0', 'stage1', 'stage2', 'stage3'], mode='staged',
                run_id='acceptance-1', probe_receipt=receipt)
            try:
                coordinator.begin_run_leases(
                    state, ['stage4'], mode='staged', run_id='acceptance-1',
                    probe_receipt=receipt)
            except SystemExit as exc:
                if 'runtime cap' not in str(exc):
                    raise
            else:
                fail('staged runtime accepted a fifth lease')
            if len(coordinator.running_translation_leases(state)) != 4:
                fail('fresh four-profile receipt did not authorize four runtime slots')
            coordinator.save_state(state)
            coordinator.release_run(SimpleNamespace(
                lease_id='stage0', confirm_dead=True, reason='selftest worker died'))
            released = coordinator.load_state()['leases'][0]
            if released['state'] != 'prepared' or not released.get('run_attempts'):
                fail('release-run did not restore and record the prepared lease')
            stale_receipt = os.path.join(tmp, 'stale-receipt.json')
            stale_payload = json.load(open(receipt, encoding='utf-8'))
            stale_payload['generated_at'] = (
                datetime.datetime.now(datetime.timezone.utc) -
                datetime.timedelta(hours=7)).isoformat(
                    timespec='seconds').replace('+00:00', 'Z')
            with open(stale_receipt, 'w', encoding='utf-8') as f:
                json.dump(stale_payload, f)
            try:
                coordinator.validate_probe_receipt(
                    stale_receipt, ['stage0'], 'acceptance-1')
            except SystemExit as exc:
                if 'stale' not in str(exc):
                    raise
            else:
                fail('stale staged probe evidence did not fail closed')

            # Two independent dispatchers racing disjoint batches may both validate against an
            # empty snapshot, but the state lock must serialize the commit and keep the cap <=3.
            state = coordinator.default_state()
            for i in range(5):
                state['leases'].append({
                    'id': 'race%d' % i, 'kind': 'verb', 'target': 'root%d' % i,
                    'state': 'prepared', 'artifact_dir': os.path.join(tmp, 'r%d' % i),
                })
            coordinator.save_state(state)
            barrier = threading.Barrier(2)
            race_results = []

            def begin_race(lease_ids):
                barrier.wait()
                try:
                    coordinator.begin_run(SimpleNamespace(
                        lease_id=lease_ids, mode='standard', run_id=None,
                        probe_receipt=None))
                    race_results.append('accepted')
                except SystemExit:
                    race_results.append('rejected')

            racers = [threading.Thread(target=begin_race, args=(['race0', 'race1', 'race2'],)),
                      threading.Thread(target=begin_race, args=(['race3', 'race4'],))]
            for racer in racers:
                racer.start()
            for racer in racers:
                racer.join(5)
            running = coordinator.running_translation_leases(coordinator.load_state())
            if len(running) > 3 or sorted(race_results) != ['accepted', 'rejected']:
                fail('simultaneous begin-run batches exceeded the standard runtime cap')

            # A blocked preparation must not hold the coordinator lock. Recovering it while
            # the fake subprocess is still alive makes its later completion stale; CAS must
            # refuse that completion rather than overwrite the recovered lease.
            state = coordinator.default_state()
            state['leases'] = [{
                'id': 'prep', 'kind': 'verb', 'target': 'gam', 'state': 'claimed',
                'artifact_dir': os.path.join(tmp, 'prep'),
            }]
            coordinator.save_state(state)
            entered = threading.Event()
            release = threading.Event()
            errors = []

            def blocking_run(cmd, cwd=coordinator.REPO, check=True, timeout=None):
                if not 0 < timeout <= coordinator.PREPARE_TIMEOUT_SECONDS:
                    fail('prepare subprocess did not receive the explicit 10-minute timeout')
                script = os.path.basename(cmd[1])
                if script == 'perf_preflight.py':
                    entered.set()
                    release.wait(5)
                    return SimpleNamespace(returncode=0, stdout='{}', stderr='')
                harness = next(value.split('=', 1)[1] for value in cmd if value.startswith('--out='))
                manifest = next(value.split('=', 1)[1] for value in cmd
                                if value.startswith('--manifest-out='))
                os.makedirs(os.path.dirname(harness), exist_ok=True)
                open(harness, 'w', encoding='utf-8').close()
                with open(manifest, 'w', encoding='utf-8') as f:
                    json.dump({'schema': 'pwg.headless_execution_manifest.v1', 'meta': {}}, f)
                return SimpleNamespace(returncode=0, stdout='', stderr='')

            coordinator.run_cmd = blocking_run

            def do_prepare():
                try:
                    coordinator.prepare(SimpleNamespace(
                        lease_id='prep', allow_over_cost=False, profile_slot=None,
                        config_dir=None, executor_lane='serial-whole-card'))
                except BaseException as exc:
                    errors.append(exc)

            worker = threading.Thread(target=do_prepare)
            worker.start()
            if not entered.wait(5):
                fail('blocking preparation fixture did not start')
            with coordinator.DirLock(coordinator.paths()['lock'], wait_seconds=1):
                if coordinator.load_state()['leases'][0]['state'] != 'preparing':
                    fail('preparing operation token was not persisted before subprocess launch')
            coordinator.recover_operation(SimpleNamespace(
                lease_id='prep', confirm_dead=True))
            release.set()
            worker.join(5)
            if worker.is_alive():
                fail('blocking preparation fixture did not finish')
            if not errors or 'stale preparing completion' not in str(errors[0]):
                fail('stale preparation completion did not fail compare-and-swap')
            if coordinator.load_state()['leases'][0]['state'] != 'claimed':
                fail('stale preparation completion overwrote recovered lease state')

            # The same lock/CAS contract applies to the 30-minute audit phase.
            audit_dir = os.path.join(tmp, 'audit')
            os.makedirs(audit_dir)
            audit_manifest = os.path.join(audit_dir, 'manifest.json')
            with open(audit_manifest, 'w', encoding='utf-8') as f:
                json.dump({'schema': 'pwg.headless_execution_manifest.v1',
                           'meta': {'selected_keys': ['k'], 'input_hashes': {}}}, f)
            result_path = os.path.join(audit_dir, 'result.json')
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump({'results': [{'key': 'k', 'card': {'key1': 'k'}}]}, f)
            state = coordinator.default_state()
            state['leases'] = [{
                'id': 'audit', 'kind': 'verb', 'target': 'gam', 'state': 'prepared',
                'artifact_dir': audit_dir, 'execution_manifest': audit_manifest,
            }]
            coordinator.begin_run_leases(state, ['audit'])
            coordinator.save_state(state)
            audit_entered = threading.Event()
            audit_release = threading.Event()
            audit_errors = []

            def blocking_audit(cmd, cwd=coordinator.REPO, check=True, timeout=None):
                if timeout != coordinator.AUDIT_TIMEOUT_SECONDS:
                    fail('audit subprocess did not receive the explicit 30-minute timeout')
                adir = cmd[cmd.index('--out-dir') + 1]
                audit_entered.set()
                audit_release.wait(5)
                with open(os.path.join(adir, 'window_status.json'), 'w', encoding='utf-8') as f:
                    json.dump({'state': 'blocked'}, f)
                with open(os.path.join(adir, 'audit_window.report.json'),
                          'w', encoding='utf-8') as f:
                    json.dump({}, f)
                return SimpleNamespace(returncode=2, stdout='', stderr='')

            coordinator.run_cmd = blocking_audit

            def do_audit():
                try:
                    coordinator.record_output(SimpleNamespace(
                        lease_id='audit', workflow_result=result_path,
                        allow_stale=False, transcript_dir=None))
                except BaseException as exc:
                    audit_errors.append(exc)

            audit_worker = threading.Thread(target=do_audit)
            audit_worker.start()
            if not audit_entered.wait(5):
                fail('blocking audit fixture did not start')
            with coordinator.DirLock(coordinator.paths()['lock'], wait_seconds=1):
                if coordinator.load_state()['leases'][0]['state'] != 'auditing':
                    fail('auditing operation token was not persisted before subprocess launch')
            coordinator.recover_operation(SimpleNamespace(
                lease_id='audit', confirm_dead=True))
            audit_release.set()
            audit_worker.join(5)
            if audit_worker.is_alive():
                fail('blocking audit fixture did not finish')
            if not audit_errors or 'stale auditing completion' not in str(audit_errors[0]):
                fail('stale audit completion did not fail compare-and-swap')
            if coordinator.load_state()['leases'][0]['state'] != 'running':
                fail('stale audit completion overwrote recovered runtime state')
        finally:
            coordinator.run_cmd = original_run
            if old_coord is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old_coord


def test_coordinator_fail_closed_audit_states():
    import coordinator
    card = {'key': 'k', 'card': {'key1': 'k'}}
    cases = {
        'clean': ('ready', True),
        'needs_requeue': ('ready_partial', True),
        'transient_only': ('ready_partial', True),
        'blocked': ('blocked', False),
        'stale_artifact': ('stale_artifact', False),
        'partial': ('partial', False),
        'unknown': ('unknown', False),
    }
    for state_name, expected in cases.items():
        got = coordinator.recorded_lease_state(state_name, [], [card])
        if got != expected:
            fail('coordinator audit state %s mapped to %r, expected %r' %
                 (state_name, got, expected))
    if coordinator.recorded_lease_state('clean', ['bad provenance'], [card]) != (
            'blocked', False):
        fail('a nominally clean audit with validation errors must fail closed')
    if coordinator.recorded_lease_state('clean', [], []) != ('blocked', False):
        fail('an empty clean audit must fail closed')
    if coordinator.recorded_lease_state('needs_requeue', [], []) != (
            'needs_requeue', False):
        fail('an all-requeue audit must remain requeueable but non-promotable')


def test_coordinator_promotion_revalidates_artifacts():
    import coordinator
    from types import SimpleNamespace
    old = os.environ.get('PWG_COORDINATOR_DIR')
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        try:
            adir = os.path.join(tmp, 'artifacts', 'lease')
            os.makedirs(adir)
            wf = os.path.join(adir, 'wf.json')
            clean = os.path.join(adir, 'clean.json')
            status_path = os.path.join(adir, 'window_status.json')
            report_path = os.path.join(adir, 'audit_window.report.json')
            payload = {'results': [{'key': 'k', 'card': {'key1': 'k'}}]}
            for path, value in ((wf, payload), (clean, payload),
                                (status_path, {'state': 'clean', 'requeue_keys': []}),
                                (report_path, {'workflow': wf, 'requeue': [], 'crashed': [],
                                               'stale_check': {'ok': True}})):
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(value, f)
            state = coordinator.default_state()
            state['leases'] = [{
                'id': 'lease', 'kind': 'nominal', 'target': 'n', 'state': 'ready',
                'artifact_dir': adir, 'wf_output': wf, 'clean_output': clean,
                'clean_output_sha256': 'tampered', 'clean_count': 1,
                'audit_state': 'clean', 'audit_returncode': 0,
                'status_path': status_path, 'audit_report': report_path,
            }]
            coordinator.save_state(state)
            try:
                coordinator.promote_ready(SimpleNamespace(
                    gen_model_version='claude-sonnet-5'))
                fail('promotion accepted a clean artifact whose hash was tampered')
            except SystemExit as e:
                if 'clean output hash' not in str(e):
                    raise
        finally:
            if old is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old


def test_atomic_control_writes_preserve_previous_file():
    import window_common
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'control.json')
        window_common.atomic_write_json(path, {'version': 1})
        original_replace = window_common.os.replace
        window_common.os.replace = lambda *_args: (_ for _ in ()).throw(
            OSError('injected replace failure'))
        try:
            try:
                window_common.atomic_write_json(path, {'version': 2})
                fail('atomic writer did not surface an injected replace failure')
            except OSError:
                pass
        finally:
            window_common.os.replace = original_replace
        if json.load(open(path, encoding='utf-8')) != {'version': 1}:
            fail('failed atomic replacement damaged the previous control artifact')
        leftovers = [name for name in os.listdir(tmp) if name != 'control.json']
        if leftovers:
            fail('failed atomic replacement left temporary files: %r' % leftovers)
        window_common.atomic_write_json(path, {'version': 2})
        if json.load(open(path, encoding='utf-8')) != {'version': 2}:
            fail('successful atomic replacement did not publish the new artifact')


def test_no_pwg_residual_registry_and_audit_command():
    import no_pwg_scale_plan as plan
    from types import SimpleNamespace
    with tempfile.TemporaryDirectory() as tmp:
        registry = os.path.join(tmp, 'residuals.jsonl')
        rows = [
            {'schema': 'pwg.no_pwg_residual.v1', 'key': 'a~~h0_zz_pw',
             'status': 'blocked', 'reason': 'repeat', 'source_window': 'w1',
             'updated_at': '2026-07-15T00:00:00Z'},
            {'schema': 'pwg.no_pwg_residual.v1', 'key': 'a~~h0_zz_pw',
             'status': 'resolved', 'reason': 'fixed', 'source_window': 'w2',
             'updated_at': '2026-07-15T01:00:00Z'},
            {'schema': 'pwg.no_pwg_residual.v1', 'key': 'b~~h0_zz_pw',
             'status': 'blocked', 'reason': 'repeat', 'source_window': 'w1',
             'updated_at': '2026-07-15T00:00:00Z'},
        ]
        with open(registry, 'w', encoding='utf-8') as f:
            for row in rows:
                f.write(json.dumps(row) + '\n')
        latest = plan.read_residuals(registry)
        if latest['a~~h0_zz_pw']['status'] != 'resolved':
            fail('latest residual registry row must win')
        eligible, skipped = plan.filter_residual_subcards(
            ['a~~h0_zz_pw', 'b~~h0_zz_pw'],
            {'b~~h0_zz_pw': latest['b~~h0_zz_pw']})
        if eligible != ['a~~h0_zz_pw'] or [r['key'] for r in skipped] != ['b~~h0_zz_pw']:
            fail('blocked residual filtering or explicit retry eligibility is wrong')
        command = plan.audit_command(
            'src/pilot/output/wf_output.no_pwg_w11.json', 'no_pwg_w11',
            'src/pilot/output/manifest.json')
        required = ('wf_output.no_pwg_w11.json', '--root "no_pwg_w11"',
                    '--write-requeue', '--window-tag "no_pwg_w11"',
                    '--execution-manifest')
        if any(piece not in command for piece in required):
            fail('no-PWG audit command is incomplete: %s' % command)

        original_run = plan.run_cmd
        original_existing = plan.existing_subcards
        original_store = plan.read_store_keys
        plan.run_cmd = lambda *_args, **_kwargs: ''
        plan.existing_subcards = lambda _head: ['b~~h0_zz_pw']
        plan.read_store_keys = lambda: set()
        try:
            omitted = plan.prepare_window(
                SimpleNamespace(prefix='fixture_w', blocked_residuals={
                    'b~~h0_zz_pw': latest['b~~h0_zz_pw']}),
                1, ['b'], [], False)
        finally:
            plan.run_cmd = original_run
            plan.existing_subcards = original_existing
            plan.read_store_keys = original_store
        if not omitted.get('omitted') or omitted.get('subcards'):
            fail('a no-PWG head with only blocked residuals must be omitted')


def test_no_pwg_preparation_advances_past_omitted_chunks():
    import no_pwg_scale_plan as plan

    def residual(key):
        return {'schema': 'pwg.no_pwg_residual.v1', 'key': key,
                'status': 'blocked', 'reason': 'repeat failure',
                'source_window': 'old', 'updated_at': '2026-07-15T00:00:00Z'}

    originals = {name: getattr(plan, name) for name in
                 ('read_queue', 'read_store_heads', 'read_still_null',
                  'read_residuals', 'prepare_window')}
    with tempfile.TemporaryDirectory() as tmp:
        registry = os.path.join(tmp, 'residuals.jsonl')
        manifest = os.path.join(tmp, 'plan.json')
        blocked = {'a~~x': residual('a~~x'), 'b~~x': residual('b~~x')}
        plan.read_queue = lambda: [
            {'key1': 'a'}, {'key1': 'b'}, {'key1': 'c'}]
        plan.read_store_heads = lambda: set()
        plan.read_still_null = lambda: []
        plan.read_residuals = lambda _path: blocked

        def prepare_some(args, index, heads, _still_null, _tail_mode):
            head = heads[0]
            if head == 'a':
                return {'omitted': True, 'root': 'fixture_w%02d' % index,
                        'headwords': heads,
                        'residual_skipped': plan.residual_summary([blocked['a~~x']])}
            return {'root': 'fixture_w%02d' % index, 'mode': 'queue',
                    'headwords': heads, 'subcards': [head + '~~x'],
                    'harness': 'run.js', 'workflow_output': 'wf.json',
                    'preflight': {}, 'headless': {'projected_calls': 1},
                    'residual_skipped': []}

        try:
            plan.prepare_window = prepare_some
            plan.main(['--window-size', '1', '--limit-windows', '1',
                       '--start-index', '900', '--force-index',
                       '--prefix', 'fixture_w', '--manifest', manifest,
                       '--residual-file', registry])
            payload = json.load(open(manifest, encoding='utf-8'))
            if payload['prepared_windows'] != 1 or payload['prepared_headwords'] != 1:
                fail('an omitted chunk consumed the requested preparation quota')
            if payload['windows'][0]['root'] != 'fixture_w901':
                fail('planner did not advance to the first eligible deterministic index')
            if [row['root'] for row in payload['omitted_windows']] != ['fixture_w900']:
                fail('omitted chunk was not reported completely')
            if payload['residual_skipped'][0]['reason'] != 'repeat failure':
                fail('omitted residual reason was lost from the plan manifest')

            def prepare_none(args, index, heads, _still_null, _tail_mode):
                key = heads[0] + '~~x'
                row = blocked.get(key) or residual(key)
                blocked[key] = row
                return {'omitted': True, 'root': 'blocked_w%02d' % index,
                        'headwords': heads,
                        'residual_skipped': plan.residual_summary([row])}

            plan.prepare_window = prepare_none
            blocked_manifest = os.path.join(tmp, 'blocked-plan.json')
            plan.main(['--window-size', '1', '--limit-windows', '1',
                       '--start-index', '910', '--force-index',
                       '--prefix', 'blocked_w', '--manifest', blocked_manifest,
                       '--residual-file', registry])
            payload = json.load(open(blocked_manifest, encoding='utf-8'))
            if payload['prepared_windows'] != 0 or payload['windows']:
                fail('an entirely blocked queue must prepare zero windows')
            if len(payload['omitted_windows']) != 3:
                fail('an entirely blocked queue must report every omitted chunk')
        finally:
            for name, value in originals.items():
                setattr(plan, name, value)


def test_coordinator_expired_leases_release_cap():
    """A killed/offline pre-prepare claim must not hold one global translation lane
    forever, while an already-prepared harness remains a durable operator artifact."""
    import coordinator
    old = os.environ.get('PWG_COORDINATOR_DIR')
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        try:
            expired_at = (datetime.datetime.now(datetime.timezone.utc) -
                          datetime.timedelta(seconds=1)).isoformat(
                              timespec='seconds').replace('+00:00', 'Z')
            future_at = (datetime.datetime.now(datetime.timezone.utc) +
                         datetime.timedelta(hours=1)).isoformat(
                             timespec='seconds').replace('+00:00', 'Z')
            state = coordinator.default_state()
            state['leases'] = [
                {'id': 'old-claim', 'lane': 'a', 'kind': 'verb', 'owner': 'selftest',
                 'target': 'gam', 'state': 'claimed', 'expires_at': expired_at},
                {'id': 'old-prepared', 'lane': 'b', 'kind': 'verb', 'owner': 'selftest',
                 'target': 'tyaj', 'state': 'prepared', 'expires_at': expired_at},
                {'id': 'live', 'lane': 'b', 'kind': 'verb', 'owner': 'selftest',
                 'target': 'dah', 'state': 'prepared', 'expires_at': future_at},
            ]
            coordinator.save_state(state)
            loaded = coordinator.load_state()
            reserved = coordinator.reserved_translation_leases(loaded)
            if [l.get('id') for l in reserved] != ['old-prepared', 'live']:
                fail('only expired pre-prepare coordinator claims must release reservations')
            if coordinator.running_translation_leases(loaded):
                fail('durable prepared leases must not consume runtime')
            if loaded['leases'][0].get('state') != 'expired':
                fail('expired coordinator claim must be marked terminal')
            if loaded['leases'][1].get('state') != 'prepared':
                fail('prepared coordinator leases must not expire just because the TTL passed')
            if coordinator.active_targets(loaded) != {'tyaj', 'dah'}:
                fail('only the expired claim target must be reclaimable')
            coordinator.save_state(loaded)
            persisted = coordinator.load_state()
            if persisted['leases'][0].get('state') != 'expired':
                fail('expired coordinator claim state must persist to disk')
        finally:
            if old is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old


def test_coordinator_lock_replaces_stale_dead_owner():
    import coordinator
    with tempfile.TemporaryDirectory() as tmp:
        lock_path = os.path.join(tmp, '.state.lock')
        os.mkdir(lock_path)
        old_ts = (datetime.datetime.now(datetime.timezone.utc) -
                  datetime.timedelta(hours=2)).isoformat(timespec='seconds').replace('+00:00', 'Z')
        with open(os.path.join(lock_path, 'owner.json'), 'w', encoding='utf-8') as f:
            json.dump({'pid': 999999999, 'created_at': old_ts}, f)
        with coordinator.DirLock(lock_path, ttl_seconds=1):
            if not os.path.exists(os.path.join(lock_path, 'owner.json')):
                fail('coordinator lock did not recreate owner metadata')


def test_coordinator_lock_creates_parent_dir():
    import coordinator
    with tempfile.TemporaryDirectory() as tmp:
        lock_path = os.path.join(tmp, 'missing', 'coordinator', '.state.lock')
        with coordinator.DirLock(lock_path, ttl_seconds=1):
            if not os.path.exists(os.path.join(lock_path, 'owner.json')):
                fail('coordinator lock must create its parent directory before locking')


def test_coordinator_defect_requeue_uses_no_tm_and_out():
    import requeue_from_audit as rq

    with tempfile.TemporaryDirectory() as tmp:
        inp = os.path.join(tmp, 'input')
        os.makedirs(inp)
        with open(os.path.join(inp, 'a.raw.txt'), 'w', encoding='utf-8') as f:
            f.write('raw')
        rqfile = os.path.join(tmp, 'requeue.defect.keys.txt')
        with open(rqfile, 'w', encoding='utf-8') as f:
            f.write('a\n')
        out = os.path.join(tmp, 'run_pilot_wf.requeue.js')
        manifest_out = os.path.join(tmp, 'execution_manifest.requeue.json')

        captured = {}

        class FakeProc:
            returncode = 0
            stdout = 'wrote fake harness'
            stderr = ''

        def fake_run(cmd, **_kwargs):
            captured['cmd'] = cmd
            return FakeProc()

        old_inp, old_run = rq.INP, rq.subprocess.run
        old_deny = rq.append_tm_denylist
        old_argv = sys.argv[:]
        rq.INP = inp
        rq.subprocess.run = fake_run
        rq.append_tm_denylist = lambda *_args, **_kwargs: (1, 0)
        sys.argv = ['requeue_from_audit.py', 'nominal_selftest', '--defect',
                    '--nominal', '--no-grammar', '--requeue-file=%s' % rqfile,
                    '--out=%s' % out, '--manifest-out=%s' % manifest_out]
        try:
            rq.main()
        finally:
            rq.INP = old_inp
            rq.subprocess.run = old_run
            rq.append_tm_denylist = old_deny
            sys.argv = old_argv
        cmd = captured.get('cmd') or []
        if '--no-tm' not in cmd:
            fail('defect requeue must pass --no-tm')
        if '--nominal' not in cmd or '--no-grammar' not in cmd:
            fail('nominal requeue flags must pass through')
        if '--out=%s' % out not in cmd:
            fail('coordinator requeue must use an explicit harness output path')
        if '--manifest-out=%s' % manifest_out not in cmd:
            fail('coordinator requeue must bind the harness to its exact manifest')


def test_coordinator_requeue_attempt_manifests():
    import coordinator
    import window_provenance
    from types import SimpleNamespace
    from window_common import input_paths

    old_coord = os.environ.get('PWG_COORDINATOR_DIR')
    original_run = coordinator.run_cmd
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        artifacts = os.path.join(tmp, 'artifacts', 'lease')
        os.makedirs(artifacts)
        input_dir = os.path.join(tmp, 'input')
        os.makedirs(input_dir)
        input_hashes = {}
        for key in ('a~~x', 'b~~x'):
            raw_path, portrait_path = input_paths(key, input_dir=input_dir)
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write('raw ' + key)
            with open(portrait_path, 'w', encoding='utf-8') as f:
                json.dump({'key': key}, f)
            input_hashes[key] = {
                'raw_sha256': coordinator.sha256_file(raw_path),
                'portrait_sha256': coordinator.sha256_file(portrait_path),
            }
        initial_manifest = os.path.join(artifacts, 'execution_manifest.lease.json')
        original = {
            'schema': 'pwg.headless_execution_manifest.v1',
            'meta': {'root': 'no_pwg_fixture', 'nominal': True,
                     'selected_keys': ['a~~x', 'b~~x'], 'input_hashes': input_hashes},
        }
        with open(initial_manifest, 'w', encoding='utf-8') as f:
            json.dump(original, f)
        original_bytes = open(initial_manifest, 'rb').read()
        audit_report = os.path.join(artifacts, 'audit_window.report.json')
        report = {
            'keys': ['a~~x', 'b~~x'], 'requeue': ['a~~x', 'b~~x'],
            'requeue_transient': ['a~~x'], 'requeue_defect': ['b~~x'],
            'requeue_defect_fshas': ['frag-b'],
        }
        with open(audit_report, 'w', encoding='utf-8') as f:
            json.dump(report, f)
        pending = coordinator.pending_from_report(
            report, audit_report, original['meta']['selected_keys'])
        orphan = os.path.join(artifacts, 'requeue', 'rq01-defect')
        os.makedirs(orphan)
        state = coordinator.default_state()
        state['leases'] = [{
            'id': 'lease', 'kind': 'nominal', 'target': 'a',
            'state': 'promoted_partial', 'artifact_dir': artifacts,
            'execution_manifest': initial_manifest,
            'origin_execution_manifest': initial_manifest,
            'origin_execution_manifest_sha256': coordinator.sha256_file(initial_manifest),
            'pending_requeue': pending,
        }]
        coordinator.save_state(state)

        class FakeProc:
            stdout = 'generated requeue harness\n'

        fail_once = [True]

        def fake_run(cmd, **_kwargs):
            out = next(arg.split('=', 1)[1] for arg in cmd if arg.startswith('--out='))
            manifest = next(arg.split('=', 1)[1] for arg in cmd
                            if arg.startswith('--manifest-out='))
            rqfile = next(arg.split('=', 1)[1] for arg in cmd
                          if arg.startswith('--requeue-file='))
            keys = [line.strip() for line in open(rqfile, encoding='utf-8') if line.strip()]
            if fail_once[0]:
                fail_once[0] = False
                raise SystemExit('synthetic generation failure')
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, 'w', encoding='utf-8') as f:
                f.write('// generated\n')
            with open(manifest, 'w', encoding='utf-8') as f:
                json.dump({'schema': 'pwg.headless_execution_manifest.v1',
                           'meta': {'root': 'no_pwg_fixture', 'nominal': True,
                                    'selected_keys': keys,
                                    'input_hashes': {key: input_hashes[key] for key in keys}}}, f)
            return FakeProc()

        coordinator.run_cmd = fake_run
        try:
            try:
                coordinator.prepare_requeue(SimpleNamespace(
                    lease_id='lease', transient=True, defect=False))
                fail('synthetic requeue generation failure was not propagated')
            except SystemExit as exc:
                if 'synthetic' not in str(exc):
                    raise
            lease = coordinator.load_state()['leases'][0]
            failed_dir = os.path.join(artifacts, 'requeue', 'rq02-transient')
            if os.path.exists(failed_dir) or lease.get('requeue_attempt'):
                fail('caught generation failure consumed an attempt or left its directory')
            if lease.get('state') != 'blocked' or 'synthetic generation failure' not in (
                    lease.get('operation_error') or ''):
                fail('unexpected requeue generation failure was not recorded as blocked')
            if set(coordinator.pending_key_set(lease['pending_requeue'])) != {'a~~x', 'b~~x'}:
                fail('caught generation failure changed the pending backlog')

            # Continue the artifact-sequencing half of this selftest from an explicit operator
            # reset; production blocked states are never retried silently.
            state = coordinator.load_state()
            state['leases'][0]['state'] = 'promoted_partial'
            state['leases'][0].pop('operation_error', None)
            coordinator.save_state(state)

            coordinator.prepare_requeue(SimpleNamespace(
                lease_id='lease', transient=True, defect=False))
            lease = coordinator.load_state()['leases'][0]
            if lease['requeue_attempt'] != 2 or 'rq02-transient' not in lease['current_artifact_dir']:
                fail('requeue did not advance past the preserved orphan directory')
            if not os.path.isdir(orphan) or not lease.get('orphaned_requeue_attempts'):
                fail('orphaned requeue attempt was deleted or not recorded')
            if json.load(open(lease['execution_manifest'], encoding='utf-8'))[
                    'meta']['selected_keys'] != ['a~~x']:
                fail('requeue attempt manifest was not narrowed to its exact keys')
            if open(initial_manifest, 'rb').read() != original_bytes:
                fail('requeue preparation modified the original execution manifest')
            if len(lease['execution_manifest_history']) != 2:
                fail('initial and first-attempt manifests were not retained in history')
            remaining = lease['current_attempt']['remaining_pending']
            if remaining['transient'] or remaining['defect'] != ['b~~x']:
                fail('unselected defect lane was not carried into the attempt')
            attempt_manifest = json.load(open(lease['execution_manifest'], encoding='utf-8'))
            old_inp = window_provenance.INP
            window_provenance.INP = input_dir
            try:
                if not window_provenance.stale_check(
                        None, attempt_manifest['meta'], ['a~~x'],
                        execution_manifest=attempt_manifest)['ok']:
                    fail('one-key requeue did not validate against its attempt manifest')
                if window_provenance.stale_check(
                        None, attempt_manifest['meta'], ['a~~x'],
                        execution_manifest=original)['ok']:
                    fail('one-key requeue unexpectedly validated against the two-key original')
            finally:
                window_provenance.INP = old_inp

            latest_dir = lease['current_artifact_dir']
            latest_report_path = os.path.join(latest_dir, 'audit_window.report.json')
            latest_report = {
                'keys': ['a~~x'], 'requeue': [],
                'requeue_transient': [], 'requeue_defect': [],
                'requeue_defect_fshas': [],
            }
            with open(latest_report_path, 'w', encoding='utf-8') as f:
                json.dump(latest_report, f)
            latest_pending = coordinator.pending_from_report(
                latest_report, latest_report_path, ['a~~x'])
            carried = coordinator.merge_pending_requeue(
                lease, remaining, latest_pending,
                coordinator.ensure_origin_manifest(lease))
            if coordinator.recorded_lease_state('clean', [], [{'card': {}}], carried) != (
                    'ready_partial', True):
                fail('a clean transient retry with carried defect work must stay ready_partial')
            state = coordinator.load_state()
            state['leases'][0]['state'] = 'promoted_partial'
            state['leases'][0]['pending_requeue'] = carried
            coordinator.save_state(state)
            coordinator.prepare_requeue(SimpleNamespace(
                lease_id='lease', transient=False, defect=True))
            lease = coordinator.load_state()['leases'][0]
            if lease['requeue_attempt'] != 3 or 'rq03-defect' not in lease['current_artifact_dir']:
                fail('carried defect lane did not receive the next attempt')
            if lease['current_attempt']['selected_keys'] != ['b~~x']:
                fail('carried defect key was not selected after transient recovery')
            if coordinator.pending_key_set(lease['current_attempt']['remaining_pending']):
                fail('final defect attempt retained a phantom pending sibling')
            fsha_path = os.path.join(lease['current_artifact_dir'],
                                     'requeue.defect.fshas.txt')
            if open(fsha_path, encoding='utf-8').read().strip() != 'frag-b':
                fail('defect fragment denylist evidence was not materialized per attempt')
            if len(lease['execution_manifest_history']) != 3:
                fail('repeated requeue did not preserve every prior manifest')

            reverse = coordinator.pending_without_kind(pending, 'defect')
            if reverse['transient'] != ['a~~x'] or reverse['defect']:
                fail('defect-first recovery did not preserve the transient sibling')
            unresolved_report_path = os.path.join(tmp, 'unresolved.json')
            unresolved_report = {
                'keys': ['a~~x'], 'requeue': ['a~~x'],
                'requeue_transient': ['a~~x'], 'requeue_defect': [],
            }
            with open(unresolved_report_path, 'w', encoding='utf-8') as f:
                json.dump(unresolved_report, f)
            unresolved = coordinator.pending_from_report(
                unresolved_report, unresolved_report_path, ['a~~x'])
            mixed_unresolved = coordinator.merge_pending_requeue(
                lease, remaining, unresolved, coordinator.ensure_origin_manifest(lease))
            if coordinator.recorded_lease_state(
                    'transient_only', [], [], mixed_unresolved) != ('needs_requeue', False):
                fail('an unresolved transient retry hid its carried defect sibling')

            foreign_report_path = os.path.join(tmp, 'foreign.json')
            foreign_report = {
                'keys': ['foreign'], 'requeue': ['foreign'],
                'requeue_transient': ['foreign'], 'requeue_defect': [],
            }
            with open(foreign_report_path, 'w', encoding='utf-8') as f:
                json.dump(foreign_report, f)
            foreign = coordinator.pending_from_report(
                foreign_report, foreign_report_path, ['foreign'])
            try:
                coordinator.validate_pending_requeue(
                    lease, foreign, coordinator.ensure_origin_manifest(lease))
                fail('foreign pending key escaped the origin manifest')
            except SystemExit as exc:
                if 'escapes origin' not in str(exc):
                    raise

            tampered_report_path = os.path.join(tmp, 'tampered.json')
            with open(tampered_report_path, 'w', encoding='utf-8') as f:
                json.dump(unresolved_report, f)
            tampered = coordinator.pending_from_report(
                unresolved_report, tampered_report_path, ['a~~x'])
            with open(tampered_report_path, 'w', encoding='utf-8') as f:
                json.dump(dict(unresolved_report, marker='changed'), f)
            try:
                coordinator.validate_pending_requeue(
                    lease, tampered, coordinator.ensure_origin_manifest(lease))
                fail('changed pending source report was accepted')
            except SystemExit as exc:
                if 'hash changed' not in str(exc):
                    raise

            invalid_reports = [
                ({'keys': ['a~~x'], 'requeue': ['a~~x', 'a~~x'],
                  'requeue_transient': ['a~~x', 'a~~x'], 'requeue_defect': []},
                 'duplicate'),
                ({'keys': ['a~~x'], 'requeue': ['a~~x'],
                  'requeue_transient': ['a~~x'], 'requeue_defect': ['a~~x']},
                 'overlap'),
                ({'keys': ['a~~x', 'b~~x'], 'requeue': ['a~~x', 'b~~x'],
                  'requeue_transient': ['a~~x'], 'requeue_defect': []},
                 'do not equal'),
            ]
            for invalid, expected in invalid_reports:
                try:
                    coordinator.report_requeue_parts(invalid, invalid['keys'])
                    fail('invalid split requeue report was accepted')
                except SystemExit as exc:
                    if expected not in str(exc):
                        raise

            history_only = {'execution_manifest_history': [
                {'attempt': 7, 'artifact_dir': os.path.join(tmp, 'gone-rq07')}]}
            if coordinator.next_requeue_attempt(history_only, os.path.join(tmp, 'empty'))[0] != 8:
                fail('attempt allocation ignored the maximum recorded historical attempt')

            state = coordinator.load_state()
            state['leases'][0]['state'] = 'ready_partial'
            coordinator.save_state(state)
            try:
                coordinator.prepare_requeue(SimpleNamespace(
                    lease_id='lease', transient=True, defect=False))
                fail('unpromoted ready_partial lease was allowed to prepare a requeue')
            except SystemExit as exc:
                if 'promote' not in str(exc):
                    fail('ready_partial refusal did not explain the promotion prerequisite')
        finally:
            coordinator.run_cmd = original_run
            if old_coord is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old_coord


def test_coordinator_mixed_lane_public_state_sequence():
    import coordinator
    from types import SimpleNamespace

    old_coord = os.environ.get('PWG_COORDINATOR_DIR')
    original_run = coordinator.run_cmd
    original_store = coordinator.promote_final_cards.DEFAULT_STORE
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['PWG_COORDINATOR_DIR'] = tmp
        store = os.path.join(tmp, 'store.jsonl')
        open(store, 'w', encoding='utf-8').close()
        coordinator.promote_final_cards.DEFAULT_STORE = store
        initial_dir = os.path.join(tmp, 'artifacts', 'lease')
        os.makedirs(initial_dir)
        origin_manifest = os.path.join(initial_dir, 'execution_manifest.lease.json')
        origin = {
            'schema': 'pwg.headless_execution_manifest.v1',
            'meta': {'root': 'nominal_mixed', 'nominal': True,
                     'selected_keys': ['a~~x', 'b~~x'], 'input_hashes': {}},
        }
        with open(origin_manifest, 'w', encoding='utf-8') as f:
            json.dump(origin, f)
        state = coordinator.default_state()
        state['leases'] = [{
            'id': 'lease', 'kind': 'nominal', 'target': 'mixed', 'state': 'prepared',
            'artifact_dir': initial_dir, 'current_artifact_dir': initial_dir,
            'execution_manifest': origin_manifest,
            'origin_execution_manifest': origin_manifest,
            'origin_execution_manifest_sha256': coordinator.sha256_file(origin_manifest),
        }]
        coordinator.save_state(state)

        audit_specs = [{
            'state': 'needs_requeue', 'returncode': 1,
            'requeue': ['a~~x', 'b~~x'],
            'transient': ['a~~x'], 'defect': ['b~~x'],
        }, {
            'state': 'clean', 'returncode': 0, 'requeue': [],
            'transient': [], 'defect': [],
        }, {
            'state': 'clean', 'returncode': 0, 'requeue': [],
            'transient': [], 'defect': [],
        }]

        def fake_run(cmd, cwd=coordinator.REPO, check=True, timeout=None):
            script = os.path.basename(cmd[1]) if len(cmd) > 1 else ''
            if script == 'audit_window.py':
                spec = audit_specs.pop(0)
                wf = cmd[2]
                adir = cmd[cmd.index('--out-dir') + 1]
                status = {'state': spec['state'], 'requeue_keys': spec['requeue']}
                report = {
                    'workflow': wf, 'keys': json.load(open(
                        cmd[cmd.index('--execution-manifest') + 1], encoding='utf-8'))[
                            'meta']['selected_keys'],
                    'requeue': spec['requeue'],
                    'requeue_transient': spec['transient'],
                    'requeue_defect': spec['defect'],
                    'requeue_defect_fshas': ['frag-b'] if spec['defect'] else [],
                    'crashed': [], 'stale_check': {'ok': True},
                }
                with open(os.path.join(adir, 'window_status.json'), 'w', encoding='utf-8') as f:
                    json.dump(status, f)
                with open(os.path.join(adir, 'audit_window.report.json'),
                          'w', encoding='utf-8') as f:
                    json.dump(report, f)
                return SimpleNamespace(returncode=spec['returncode'], stdout='', stderr='')
            if script == 'promote_final_cards.py':
                with open(store, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({'promoted': True}) + '\n')
            return SimpleNamespace(returncode=0, stdout='', stderr='')

        def result_file(name, keys):
            path = os.path.join(tmp, name)
            payload = {'results': [
                {'key': key, 'card': {'key1': key, 'records': []}} for key in keys]}
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(payload, f)
            return path

        def record(path):
            state = coordinator.load_state()
            coordinator.begin_run_leases(state, ['lease'])
            coordinator.save_state(state)
            coordinator.record_output(SimpleNamespace(
                lease_id='lease', workflow_result=path, allow_stale=False,
                transcript_dir=None))

        def set_attempt(number, kind, key, remaining):
            adir = os.path.join(initial_dir, 'requeue', 'rq%02d-%s' % (number, kind))
            os.makedirs(adir)
            manifest = os.path.join(adir, 'execution_manifest.json')
            attempt = dict(origin)
            attempt['meta'] = dict(origin['meta'], selected_keys=[key])
            with open(manifest, 'w', encoding='utf-8') as f:
                json.dump(attempt, f)
            state = coordinator.load_state()
            lease = state['leases'][0]
            lease.update({
                'state': 'requeue_prepared', 'current_artifact_dir': adir,
                'execution_manifest': manifest, 'requeue_attempt': number,
                'current_attempt': {
                    'number': number, 'kind': kind, 'artifact_dir': adir,
                    'execution_manifest': manifest, 'selected_keys': [key],
                    'remaining_pending': remaining,
                },
            })
            coordinator.save_state(state)

        coordinator.run_cmd = fake_run
        try:
            record(result_file('initial.json', ['a~~x', 'b~~x']))
            lease = coordinator.load_state()['leases'][0]
            if lease['state'] != 'needs_requeue':
                fail('mixed initial audit did not enter needs_requeue')
            pending = lease['pending_requeue']
            if pending['transient'] != ['a~~x'] or pending['defect'] != ['b~~x']:
                fail('record-output did not persist both provenance-bound retry lanes')

            carried_b = coordinator.pending_without_kind(pending, 'transient')
            set_attempt(1, 'transient', 'a~~x', carried_b)
            record(result_file('retry-a.json', ['a~~x']))
            lease = coordinator.load_state()['leases'][0]
            if lease['state'] != 'ready_partial' or lease['pending_requeue']['defect'] != ['b~~x']:
                fail('clean transient retry did not retain the defect backlog')
            coordinator.promote_ready(SimpleNamespace(
                gen_model_version='claude-sonnet-5', lease_id=['lease']))
            lease = coordinator.load_state()['leases'][0]
            if lease['state'] != 'promoted_partial':
                fail('mixed backlog promotion did not remain promoted_partial')

            set_attempt(2, 'defect', 'b~~x', coordinator.empty_pending_requeue())
            record(result_file('retry-b.json', ['b~~x']))
            lease = coordinator.load_state()['leases'][0]
            if lease['state'] != 'ready' or coordinator.pending_key_set(
                    lease['pending_requeue']):
                fail('final clean defect retry did not drain the pending backlog')
            coordinator.promote_ready(SimpleNamespace(
                gen_model_version='claude-sonnet-5', lease_id=['lease']))
            if coordinator.load_state()['leases'][0]['state'] != 'promoted':
                fail('drained mixed retry sequence did not finish promoted')
            if audit_specs:
                fail('mixed-lane integration did not consume every planned audit')
        finally:
            coordinator.run_cmd = original_run
            coordinator.promote_final_cards.DEFAULT_STORE = original_store
            if old_coord is None:
                os.environ.pop('PWG_COORDINATOR_DIR', None)
            else:
                os.environ['PWG_COORDINATOR_DIR'] = old_coord


def test_promote_nominal_key1():
    import promote_final_cards as pfc
    entry = {
        'card': {'key1': 'agni', 'iast': 'agni', 'records': [
            {'h': 'agni', 'senses': [{'tag': '1', 'russian': 'огонь', 'german': 'Feuer'}]},
        ]},
        'meta': {'nominal': True, 'root': 'nominal_batch',
                 'input_hashes': {'agni': {'raw_sha256': 'r', 'portrait_sha256': 'p'}}},
        'wf_file': 'wf_output.nominal.json',
    }
    rows = list(pfc.rows_for('agni', entry, 'ai_translated', pfc.SELFTEST_MODEL_VERSION))
    if not rows or rows[0]['key1'] != 'agni':
        fail('nominal promotion must preserve the assembled-card key1')
    mapped = {
        'card': {'key1': 'af_rin', 'records': [
            {'h': 'afRin', 'senses': [{'tag': '1', 'russian': 'свободный', 'german': 'frei'}]},
        ]},
        'meta': {'nominal': True, 'root': 'nominal_batch',
                 'nominal_keymap': {'af_rin': 'afRin'}},
        'wf_file': 'wf_output.nominal.json',
    }
    rows = list(pfc.rows_for('af_rin', mapped, 'ai_translated', pfc.SELFTEST_MODEL_VERSION))
    if not rows or rows[0]['key1'] != 'afRin':
        fail('nominal promotion must map safe runtime keys back to assembled key1')


def test_build_emits_nominal_keymap():
    """Producer-side twin of test_promote_nominal_key1: build(nominal=True) MUST emit
    meta.nominal + meta.nominal_keymap. Without them promote_final_cards.rows_for falls
    back to meta.root (the window LABEL, e.g. pril10_w1) and mis-keys every nominal card.
    The consumer test hand-builds its meta, so it cannot catch build() dropping the fields;
    this test does (guards PR #155 against a silent regression)."""
    import re as _re
    import gen_opt_harness2 as gh
    from window_common import input_paths
    key = 'ab'
    rp, pp = input_paths(key)
    if not (os.path.exists(rp) and os.path.exists(pp)):
        return  # fixture-gated, same as the sibling nominal build() tests
    js, _batches = gh.build(key, [key], None, 12000, nominal=True, tm_path=None)
    meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
    if meta.get('nominal') is not True:
        fail('build(nominal=True) must set meta.nominal=True (else promote falls back to the window label)')
    keymap = meta.get('nominal_keymap')
    if not isinstance(keymap, dict) or key not in keymap:
        fail('build(nominal=True) must emit meta.nominal_keymap mapping each safe key to its SLP1 headword')
    slp1 = gh._slp1_lex_for_key(key)[0] or key
    if keymap[key] != slp1:
        fail('nominal_keymap must map the safe key to the portrait SLP1 (%r), got %r' % (slp1, keymap[key]))
    # Negative: a non-nominal (batched) build must NOT carry the nominal routing fields.
    js2, _b2 = gh.build(key, [key], None, 12000, nominal=False, tm_path=None)
    meta2 = json.loads(_re.search(r'const META = (\{.*?\})\n', js2, _re.S).group(1))
    if meta2.get('nominal'):
        fail('batched (non-nominal) build must not set meta.nominal')
    if meta2.get('nominal_keymap') is not None:
        fail('batched (non-nominal) build must leave meta.nominal_keymap null')


def test_generation_schema_carries_no_post_generation_field():
    """H428: the per-call StructuredOutput schema (build()'s batch_schema) must never carry
    a field that a deterministic annotator adds AFTER generation (government, labels, renou,
    renou_oldest, evidence, evidence_summary, stats, renou_oldest_sense) -- those fields
    pushed the full reachable schema to 10,940 chars, over the Workflow tool's safety-
    classifier size threshold, blocking every agent() call pre-generation at 0 tokens
    (Uprava/FINDINGS.md §30). Pins the fix so a future annotator field added to
    schemas/pwg_ru_final_card.schema.json cannot silently regress this without also being
    added to _POST_GENERATION_*_FIELDS."""
    import gen_opt_harness2 as gh
    schema = gh.load_json(os.path.join(gh.REPO, 'schemas', 'pwg_ru_final_card.schema.json'))
    schema['$defs']['sense']['required'] = ['tag', 'german', 'russian']
    defs = gh._strip_post_generation_fields(schema['$defs'])
    reachable = gh._reachable_defs(defs, 'card')
    banned = (gh._POST_GENERATION_CARD_FIELDS + gh._POST_GENERATION_RECORD_FIELDS
              + gh._POST_GENERATION_SENSE_FIELDS)
    for def_name in ('card', 'record', 'sense'):
        props = reachable.get(def_name, {}).get('properties', {})
        for f in banned:
            if f in props:
                fail('generation schema $defs[%r] still carries post-generation field %r' % (def_name, f))
    # evidence_item/evidence_summary/stats become unreachable once sense.evidence and
    # card.evidence_summary/stats are stripped -- pin that they actually drop out, since a
    # dangling $defs entry is exactly the H130 orphan-defs dead weight this fix removes.
    for orphan in ('evidence_item', 'evidence_summary', 'stats'):
        if orphan in reachable:
            fail('%r should be unreachable from card once post-generation fields are stripped' % orphan)
    size = len(json.dumps({
        'type': 'object', 'additionalProperties': False, 'required': ['cards'],
        'properties': {'cards': {'type': 'array', 'minItems': 1, 'items': {'$ref': '#/$defs/card'}}},
        '$defs': reachable,
    }))
    if size > 5000:
        fail('slimmed generation schema grew to %d chars (was 1,698 at H428) -- '
             're-measure against the Workflow tool safety-classifier threshold' % size)


def test_no_pwg_supplement_chain_cards_render():
    """H214: PWG-missing lemmas with PW/SCH/PWKVN/NWS records are runnable.

    Synthetic indexes and a temp input directory prove the generator path without
    requiring csl-orig or touching live pilot/input artifacts.
    """
    import _pilot_gen_merged as pg
    from safe_filename import safe_name
    old_out = pg.OUT
    with no_pwg_dictionary_fixture(), tempfile.TemporaryDirectory() as tmp:
        pg.OUT = tmp
        try:
            bagavat_n = pg.gen_no_pwg_card('Bagavat', {}, verbose=False)
            akulita_n = pg.gen_no_pwg_card('Akulita', {}, verbose=False)
            if not bagavat_n:
                fail('Bagavat should render as a no-PWG supplement-chain card')
            if not akulita_n:
                fail('Akulita should render as a SCH-only no-PWG supplement-chain card')
            bagavat_stem = safe_name('Bagavat')
            akulita_stem = safe_name('Akulita')
            bagavat_files = [n for n in os.listdir(tmp) if n.startswith(bagavat_stem + '~~h0_zz_')]
            akulita_files = [n for n in os.listdir(tmp) if n.startswith(akulita_stem + '~~h0_zz_')]
            if not any('_zz_pw' in n and n.endswith('.raw.txt') for n in bagavat_files):
                fail('Bagavat must emit a PW-labeled no-PWG sub-card')
            if not any('_zz_sch' in n and n.endswith('.raw.txt') for n in akulita_files):
                fail('Akulita must emit a SCH-labeled no-PWG sub-card')
            for stem in (bagavat_stem + '~~h0_zz_pw', akulita_stem + '~~h0_zz_sch'):
                raw_path = os.path.join(tmp, stem + '.raw.txt')
                portrait_path = os.path.join(tmp, stem + '.portrait.json')
                if not os.path.exists(raw_path) or not os.path.exists(portrait_path):
                    fail('missing no-PWG generated files for %s' % stem)
                raw = open(raw_path, encoding='utf-8').read()
                portrait = json.load(open(portrait_path, encoding='utf-8'))
                if '=== LAYER: PWG' in raw:
                    fail('%s must not fabricate a PWG layer' % stem)
                if not portrait or portrait[0].get('source_profile') != 'no_pwg_supplement_chain':
                    fail('%s portrait must carry source_profile=no_pwg_supplement_chain' % stem)
                if portrait[0].get('senses') != []:
                    fail('%s portrait must not fabricate a PWG sense tree' % stem)
        finally:
            pg.OUT = old_out


def test_nominals_worklist_exposes_no_pwg_lane():
    import nominals_worklist as nw
    with no_pwg_dictionary_fixture(), tempfile.TemporaryDirectory() as tmp:
        wordlist = os.path.join(tmp, 'sample.slp1.txt')
        manifest = os.path.join(tmp, 'scale_manifest.freq.json')
        store = os.path.join(tmp, 'store.jsonl')
        with open(wordlist, 'w', encoding='utf-8') as f:
            f.write('Bagavat\nAkulita\nnotalocalword\n')
        with open(manifest, 'w', encoding='utf-8') as f:
            json.dump([
                {'key1': 'Bagavat', 'score': 3, 'band': 1},
                {'key1': 'Akulita', 'score': 2, 'band': 1},
                {'key1': 'notalocalword', 'score': 1, 'band': 1},
            ], f)
        open(store, 'w', encoding='utf-8').close()
        payload = nw.build_worklist(wordlist, manifest=manifest, store=store)
    got = set(payload.get('no_pwg_runnable') or [])
    if not {'Bagavat', 'Akulita'}.issubset(got):
        fail('PW/SCH-only misses must enter no_pwg_runnable, got %s' % sorted(got))
    if 'notalocalword' not in payload.get('true_miss_keys', []):
        fail('true misses must remain misses, not no-PWG runnable')
    for field in ('no_pwg_runnable_count', 'no_pwg_promoted_count', 'no_pwg_runnable_detail'):
        if field not in payload:
            fail('nominals_worklist payload missing %s' % field)
    if any(k in payload.get('runnable_remaining', []) for k in got):
        fail('no-PWG runnable keys must stay separate from PWG-rooted runnable_remaining')


def test_no_pwg_source_profile_promotes():
    import gen_opt_harness2 as gh
    import promote_final_cards as pfc
    old_input_paths = gh.input_paths
    with tempfile.TemporaryDirectory() as tmp:
        key = 'bagavat~~h0_zz_pw'
        raw_path = os.path.join(tmp, key + '.raw.txt')
        portrait_path = os.path.join(tmp, key + '.portrait.json')
        with open(raw_path, 'w', encoding='utf-8') as f:
            f.write('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n{#Bagavat#}¦ selig.\n')
        with open(portrait_path, 'w', encoding='utf-8') as f:
            json.dump([{'portrait_kind': 'no_pwg_supplement_chain',
                        'source_profile': 'no_pwg_supplement_chain',
                        'key1': 'Bagavat', 'iast': 'bhagavat', 'layers': ['pw'],
                        'senses': []}], f)
        gh.input_paths = lambda k, input_dir=None: (
            os.path.join(tmp, k + '.raw.txt'), os.path.join(tmp, k + '.portrait.json'))
        try:
            js, _batches = gh.build('no_pwg_sample', [key], None, 12000, nominal=True,
                                    grammar_on=False, tm_path=None)
        finally:
            gh.input_paths = old_input_paths
        import re as _re
        meta = json.loads(_re.search(r'const META = (\{.*?\})\n', js, _re.S).group(1))
        if meta.get('source_profile') != 'no_pwg_supplement_chain':
            fail('all-no-PWG harness must stamp window source_profile')
        if (meta.get('source_profiles') or {}).get(key) != 'no_pwg_supplement_chain':
            fail('harness must stamp per-card no-PWG source profile')
        entry = {
            'card': {'key1': key, 'iast': 'bhagavat', 'records': [
                {'senses': [{'tag': '1', 'russian': 'бхагават', 'german': '{#Bagavat#}¦ selig.'}]},
            ]},
            'meta': meta,
            'wf_file': 'wf_output.no_pwg.json',
        }
        rows = list(pfc.rows_for(key, entry, 'ai_translated', pfc.SELFTEST_MODEL_VERSION))
        if not rows:
            fail('no-PWG promotion fixture yielded no rows')
        row = rows[0]
        if row['key1'] != 'Bagavat':
            fail('no-PWG nominal promotion must map runtime key back to true key1')
        if row['layer'] != 'pw':
            fail('no-PWG promoted row must preserve layer=pw')
        if row['provenance'].get('source_profile') != 'no_pwg_supplement_chain':
            fail('promoted provenance must preserve source_profile=no_pwg_supplement_chain')


def test_calibration_arm_set_conservative_emit_only():
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = os.path.join(tmp, 'perf_smoke_preflight')
        proc = run([sys.executable, 'src/pilot/calibrate_perf_harness.py', 'gam',
                    '--keys=gam~~h0_03_sec_3', '--arm-set', 'conservative',
                    '--emit-only', '--out-dir=%s' % out_dir], 0)
        manifest_path = os.path.join(out_dir, 'manifest.json')
        if not os.path.exists(manifest_path):
            fail('calibration emit-only must write manifest.json')
        manifest = json.load(open(manifest_path, encoding='utf-8'))
        arms = {(a['output_budget'], a['selfheal_budget'], a['tm_mode'])
                for a in manifest.get('arms', [])}
        expected = {(90, 12, 'auto'), (90, 12, 'off'), (110, 12, 'auto'), (110, 12, 'off')}
        if arms != expected:
            fail('conservative arm set mismatch: %s' % sorted(arms))
        if 'cache cooldown' not in manifest.get('cache_warning', ''):
            fail('calibration manifest must keep the cache-cooldown warning')
        if any(name.endswith('.js') for name in os.listdir(out_dir)):
            fail('emit-only calibration must not generate harness JS files')
        if 'cache cooldown' not in proc.stdout:
            fail('calibration CLI must print the cache-cooldown warning')


def test_frag_tm_reuse():
    """Fragment-level --tm: a card that plan()-splits into >=2 fragments, with ONE fragment
    in the fragment sidecar, emits a FRAG_TM group-shape mirroring FRAGS where exactly the
    cached fragment slot is filled (served at runtime with NO agent call) and the rest are
    null. The card itself stays in a translate lane (reuse is inside selfHeal, not card
    removal), so the whole-card accounting invariant is untouched."""
    import re as _re
    import gen_opt_harness2 as gh
    import translation_memory as tm
    from autosplit_requeue import plan as split_plan
    from window_common import rootmap_path, input_paths, read_text
    root = 'gam'
    rmpath, _ = rootmap_path(root)
    if not rmpath:
        return  # inputs not present in this checkout — nothing to assert
    rootmap, keys = gh.selected_keys(root, None)
    keys = [k for k in keys if os.path.exists(input_paths(k)[0])]
    # pick the first card that actually splits into >=2 deterministic fragments
    target, plan0 = None, None
    for k in keys:
        pl = split_plan(read_text(input_paths(k)[0]))
        if len(pl) >= 2:
            target, plan0 = k, pl
            break
    if not target:
        return
    d = tempfile.mkdtemp()
    try:
        # card-level TM: empty (so `target` is NOT a whole-card hit); fragment sidecar caches
        # exactly plan0[0]. The sidecar MUST sit next to the card TM under the exact basename.
        tmfile = os.path.join(d, 'translation_memory.ru.json')
        with open(tmfile, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg.translation_memory.v1', 'lang': 'ru', 'entries': {}}, f)
        fsha0 = tm.frag_address('ru', plan0[0][2])
        senses0 = [{'tag': '1', 'german': plan0[0][2][:20], 'russian': 'кэш',
                    'equivalence_type': 'equivalent', 'source_type': 'attested',
                    'stratum': '', 'differentia': ''}]
        with open(os.path.join(d, 'translation_memory.frag.ru.jsonl'), 'w', encoding='utf-8') as f:
            f.write(json.dumps({'schema': 'pwg.translation_memory.frag.v1', 'lang': 'ru',
                                'fsha': fsha0, 'src_key': target, 'senses': senses0},
                               ensure_ascii=False) + '\n')
        js, _batches = gh.build(root, [target], rootmap, 12000, tm_path=tmfile)

        def const(name):
            return json.loads(_re.search(r'^const %s = (.*)$' % name, js, _re.M).group(1))
        meta = const('META')
        frags, frag_tm = const('FRAGS'), const('FRAG_TM')
        if target not in frag_tm:
            fail('the card with a cached fragment must appear in FRAG_TM')
        if target not in meta.get('frag_tm_cards', []):
            fail('meta.frag_tm_cards must list the reusing card')
        if meta.get('frag_tm_fragments') != 1:
            fail('exactly one fragment should be cached, got %r' % meta.get('frag_tm_fragments'))
        # shape mirrors FRAGS exactly
        gv, fv = frags[target], frag_tm[target]
        if [len(g) for g in gv] != [len(g) for g in fv]:
            fail('FRAG_TM group shape must mirror FRAGS')
        filled = [(gi, fi) for gi, g in enumerate(fv) for fi, slot in enumerate(g) if slot]
        if filled != [(0, 0)]:
            fail('only the first fragment (the cached one) must be filled, got %s' % filled)
        # the filled slot carries the cached senses; its FRAGS sibling carries the matching fsha
        if fv[0][0][0]['russian'] != 'кэш':
            fail('cached fragment slot must carry the sidecar senses')
        if gv[0][0].get('fsha') != fsha0:
            fail('FRAGS fragment must carry the content address used for the cache lookup')
        # whole-card accounting: reuse happens INSIDE selfHeal, so the card is still owed by a
        # translate lane (batch or presplit), never silently dropped.
        batched = {k for b in meta['batches'] for k in b}
        if target not in (batched | set(meta['presplit_keys'])):
            fail('a fragment-reusing card must still be owed by a translate lane')
    finally:
        shutil.rmtree(d, ignore_errors=True)


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


def test_cit_split_never_tears_open_span():
    """SAN-LOSS hypothesis (2026-07-04 vid drain): autosplit_requeue._cit_parts split a
    (sub)sense purely on running <ls> counts per line, with NO awareness of {#...#} span
    state. A well-formed <ls>...</ls> span can never straddle a cut (a NEW <ls> can only
    open once the PREVIOUS one has closed, and the algorithm never lets the running count
    exceed budget), but a {#...#} span never contributes to that count at all — so a
    {#...#} block that is still open when a LATER, unrelated <ls> tag pushes the running
    <ls> count over budget got torn across the cut. A torn {#...#} span can no longer be
    matched by pwg_mask's PAIRED regex (needs a complete open+close pair), so its Sanskrit
    content passed through UNMASKED as ordinary translatable prose — the model then
    paraphrases or drops it, producing SAN-LOSS on exactly the citation-dense giant heads
    that need tier-2 splitting. Fixed via _span_open(): defer the cut until the accumulated
    fragment text is <ls>/{#..#} balanced. This constructs the vulnerable shape (a
    {#...#} span straddling what would otherwise be the cut point) and asserts every
    returned fragment is internally balanced."""
    from autosplit_requeue import plan as split_plan
    raw = (
        '<ls n="1">a</ls>\n'
        '{#Sanskrit quote start\n'
        '<ls n="2">b</ls>\n'
        'quote end#}\n'
        '<ls n="3">c</ls>\n'
    )
    parts = split_plan(raw, ls_budget=1)
    if len(parts) < 2:
        fail('fixture did not force a split — adjust ls_budget/fixture')
    for _si, _pi, text in parts:
        if text.count('<ls') != text.count('</ls>'):
            fail('a returned fragment has an unbalanced <ls>/</ls> pair — span torn across '
                 'a cut: %r' % text)
        if text.count('{#') != text.count('#}'):
            fail('a returned fragment has an unbalanced {#/#} pair — Sanskrit span torn '
                 'across a cut: %r' % text)


def test_cit_split_caps_single_line_monster_sense():
    """H191/B2: a single physical line with many complete citations must still be
    sub-split; line-boundary splitting alone emitted >90-citation fragments."""
    import autosplit_requeue as ar
    raw = 'Ein einziger Sinn. ' + ' '.join(
        '<ls n="SRC.%d">citation %d</ls>' % (i, i) for i in range(150))
    parts = ar.plan(raw, ls_budget=18)
    if len(parts) < 2:
        fail('150-citation one-line fixture must split into multiple fragments')
    for _si, _pi, text in parts:
        if text.count('<ls') > 18:
            fail('fragment exceeds citation budget: %d <ls>' % text.count('<ls'))
        if text.count('<ls') != text.count('</ls>'):
            fail('line-level splitter tore an <ls> span')


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


def test_sense_dense_card_presplit():
    """H155 (2026-07-04): a SENSE-dense card must presplit even when its CITATION weight
    (1+<ls>) is FAR below the output budget. A PW addenda card compresses a whole root article
    (base verb + Caus/Desid + every prefix combination) into dozens of terse senses carrying
    few citations, so the citation metric (1+<ls>) ranks it as one of the LIGHTEST cards while
    its real output surface (dozens of {tag,german,russian} sense objects) is the HEAVIEST — it
    deterministically blows the whole-card StructuredOutput retry cap (tyaj~~h0_zz_pw: 35 senses
    in 11 <ls>, weight 12, stalled ~7 min retrying the identical call). The fragment-count
    trigger (frag count > SENSE_PRESPLIT_BUDGET) routes it straight to the proven fragment lane,
    same as the citation giants — independent of the citation trigger and of byte/citation
    batching mode. Uses a synthetic card (30 senses, 1 <ls>) so it never depends on a specific
    corpus fixture."""
    import gen_opt_harness2 as gh
    senses = '\n'.join('<div n="1">— %d〉 {%%Bedeutung %d%%}.' % (i, i)
                       for i in range(1, 31))
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n' + senses + '\n')
    key = 'zz~~synthetic_sense_dense'
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')  # empty portrait — exactly the real tyaj~~h0_zz_pw shape
        saved_ip = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        try:
            # citation weight 1+<ls>=2 is far below OUTPUT_BUDGET(90): only the SENSE trigger
            # can route this card. nominal mode makes the key its own card (no rootmap needed).
            js, batches = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
            import re as _re
            presplit = json.loads(_re.search(r'^const PRESPLIT = (.*)$', js, _re.M).group(1))
            batched = {k for b in batches for k in b}
            if key not in presplit:
                fail('a sense-dense card (30 senses, 1 <ls>) must be routed to presplit by the '
                     'fragment-count trigger; got PRESPLIT=%r batches=%r' % (presplit, batches))
            if key in batched:
                fail('a presplit card must be pulled OUT of the whole-card batch lane, got it in '
                     '%r' % (batches,))
            # the citation trigger alone must NOT explain it (proves the sense trigger is load-
            # bearing): with the sense trigger disabled, the card falls back to a batch.
            saved_sb = gh.SENSE_PRESPLIT_BUDGET
            gh.SENSE_PRESPLIT_BUDGET = None
            try:
                js2, batches2 = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
                presplit2 = json.loads(_re.search(r'^const PRESPLIT = (.*)$', js2, _re.M).group(1))
            finally:
                gh.SENSE_PRESPLIT_BUDGET = saved_sb
            if key in presplit2:
                fail('with --sense-presplit-budget=off the citation-light card must NOT presplit '
                     '(only the sense trigger should route it); got PRESPLIT=%r' % presplit2)
        finally:
            gh.input_paths = saved_ip
    finally:
        shutil.rmtree(d, ignore_errors=True)


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


def test_nominal_key_echo_tolerance_scoped():
    """H220: nominal / no-PWG windows must tolerate the model echoing the CLEAN SLP1 headword
    (nominal_keymap[stem], e.g. 'CAyA') instead of the mangled sub-card stem
    (_c_ay_a~~h0_zz_pw) in key1 — recovering the card by re-keying it to the stem, but ONLY
    when the SLP1 maps to exactly one pending stem (unambiguous). This must be GATED on
    META.nominal so PWG root windows keep strict key matching (paired with
    test_generated_harness_strict_key_matching). Static guard on the generated harness."""
    import re as _re
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '{#CAya#}¦ {%Schatten%}.\n')
    key = '_c_ay_a~~h0_zz_pw'
    d = tempfile.mkdtemp()
    try:
        rp = os.path.join(d, key + '.raw.txt')
        pp = os.path.join(d, key + '.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(raw)
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[{"portrait_kind":"no_pwg_supplement_chain","key1":"CAyA","iast":"chāyā","senses":[]}]')
        saved_ip = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp) if k == key else saved_ip(k)
        try:
            js, _b = gh.build('zz', [key], None, 12000, nominal=True, grammar_on=False, tm_path=None)
        finally:
            gh.input_paths = saved_ip
        # the recovery is gated on META.nominal + nominal_keymap (inert for root windows)
        if 'META.nominal && META.nominal_keymap' not in js:
            fail('nominal key-echo tolerance must be gated on META.nominal so root windows stay strict')
        # unambiguous rival check (never re-key a SLP1 that maps to >1 pending stem) + re-key to stem
        if 'const rivals = cur.filter(x => NKM[x] === slp1)' not in js:
            fail('key-echo recovery must guard on an UNAMBIGUOUS SLP1->stem mapping within the batch')
        if 'rivals.length === 1' not in js or 'cand.key1 = k' not in js:
            fail('recovery must require exactly one rival stem and re-key the card to the stem')
        # H255/H834: also accept the SLP1 headword with the sub-card suffix kept
        # ('avyAhata~~h0_zz_pw' for the stem 'avy_ahata~~h0_zz_pw'), still gated + unambiguous.
        if 'km[slp1 + sfx]' not in js:
            fail('key-echo recovery must also accept the SLP1 headword carrying the ~~<layer> '
                 'suffix (the H255 avy_ahata failure), not only the bare SLP1')
        # strict key lookup (km[k]) is still the FIRST attempt — tolerance is a fallback, not positional
        if 'let cand = km[k]' not in js:
            fail('strict key lookup km[k] must remain the primary match; tolerance is a fallback only')
        meta = json.loads(_re.search(r'^const META = (\{.*\})\n', js, _re.M).group(1))
        if not meta.get('nominal') or meta.get('nominal_keymap', {}).get(key) != 'CAyA':
            fail('nominal harness must carry nominal_keymap[stem]=SLP1 for the re-key (got %r)'
                 % meta.get('nominal_keymap'))
    finally:
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
    """H189 (MG: '>~60s per subcard suspicious; >3 min unacceptable'): the kill envelope
    must be the tightened one — floor <= 45s, ceil <= 180s (3 min) — never a regression
    back to the 2 min floor / 8 min ceiling that let pril10_w1 fragments run 6.5 min."""
    import gen_opt_harness2 as gh
    if gh.KILL_FLOOR_MS > 45000:
        fail('KILL_FLOOR_MS must be <= 45000 (was 120000) so a tiny subcard is killed '
             'near MG\'s ~60s suspicion line; got %d' % gh.KILL_FLOOR_MS)
    if gh.KILL_CEIL_MS > 180000:
        fail('KILL_CEIL_MS must be <= 180000 (3 min hard ceiling, was 480000); got %d'
             % gh.KILL_CEIL_MS)


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
        test_js = os.path.join(os.path.dirname(os.path.abspath(__file__)),
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


def test_run_telemetry_counters_returned():
    """H462: the two decisive numbers of every launch post-mortem — the kill-timeout count
    and the 'Connection closed mid-response' count — existed only as console.log strings
    and were hand-counted from transcripts into LAUNCH_FUCKUPS.md ('58 of 61 kill-timeouts',
    '3 conn-errors'); every H437/H442 code-vs-infra conclusion leaned on numbers the payload
    never returned. The harness summary must RETURN kill_timeouts / conn_errors / heal_calls /
    kill_bisect_blocked so the orchestrator and classify_run.py read them mechanically.
    Counters only — this pin also guards that the counting stays OUT of control flow."""
    import re as _re
    import gen_opt_harness2 as gh
    raw = ('=== LAYER: PW — Böhtlingk kürzere Fassung ===\n\n'
           '<hom>1.</hom> √{#gam#}¦ <ls>X. 1</ls>.\n'
           '<div n="1">— 1〉 {%verlassen%} <ls>Y. 2</ls>.\n')
    key = 'zz~~synthetic_telemetry'
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
            for tok in ('let KILL_TIMEOUTS = 0', 'let CONN_ERRORS = 0', 'let HEAL_CALLS = 0',
                        'let KILL_BISECT_BLOCKED = 0', 'const isConn ='):
                if tok not in js:
                    fail('telemetry counter token %r missing from the harness' % tok)
            # the counters must be RETURNED in summary, not just logged
            for field in ('kill_timeouts: KILL_TIMEOUTS', 'conn_errors: CONN_ERRORS',
                          'heal_calls: HEAL_CALLS', 'kill_bisect_blocked: KILL_BISECT_BLOCKED'):
                if field not in js:
                    fail('summary must return telemetry field %r — hand-counting kill-timeouts '
                         'from transcripts is exactly what H462 removes' % field)
            # counting must live in agentKill's catch (central, one site) and re-throw:
            # the counters observe, they never swallow or reroute the error.
            if not _re.search(r'catch \(e\) \{ if \(isKill\(e\)\) KILL_TIMEOUTS\+\+; '
                              r'else if \(isConn\(e\)\) CONN_ERRORS\+\+; throw e \}', js):
                fail('agentKill must count kills/conn-errors in its catch and RE-THROW — '
                     'telemetry must not change control flow')
            # heal-lane spend is derived once from the heal: label prefix; both the dedicated
            # pool and telemetry must use that exact lane decision.
            if "const healLane = !!(opts && opts.label && /^heal:/.test(String(opts.label)))" not in js:
                fail('agentKill must classify heal calls via the heal: label prefix')
            if 'if (healLane) HEAL_CALLS++' not in js:
                fail('agentKill must count heal-lane calls from the shared lane decision')
            # a KillTimeout must never double-count as a connection error
            if 'e instanceof KillTimeout' not in js.split('const isConn =', 1)[1].split('\n', 1)[0]:
                fail('isConn must exclude KillTimeout so a kill is never double-counted as a conn error')
        finally:
            gh.input_paths = saved_ip
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_partial_cards_requeue_and_stay_out_of_clean_sample():
    """Partial-only output is transient; an independent content defect wins."""
    import audit_window as aw
    import window_reports as wr

    fixture = [
        {'key': 'partial_only', 'card': {'partial': True,
                                         'missing_fragments': ['g1:f9']}},
        {'key': 'partial_defect', 'card': {'partial': True,
                                           'missing_fragments': ['g2:f3']}},
    ]
    partial_cards, failure_reasons = aw.collect_harness_quality(fixture)
    transient, defect, _ = aw.classify_harness_requeues(
        [], partial_cards, {'partial_defect'}, failure_reasons)
    if transient != {'partial_only'} or defect != {'partial_defect'}:
        fail('partial requeue precedence drifted: transient=%r defect=%r' %
             (transient, defect))

    report = {'root': 'zz', 'keys': ['clean', 'partial_only', 'partial_defect'],
              'null_cards': [], 'requeue': sorted(transient | defect)}
    saved_merged_exists = wr.merged_exists
    try:
        wr.merged_exists = lambda key: True
        sample = wr.build_judge_sample(report, rate=1.0, minimum=0, seed='partial-test')
    finally:
        wr.merged_exists = saved_merged_exists
    if sample['clean_sample_keys'] != ['clean']:
        fail('partial keys leaked into clean judge candidates: %r' %
             sample['clean_sample_keys'])


def test_classify_run_verdicts():
    """H462: classify_run.py mechanizes the code-vs-infra rule H442 applied by hand
    ('if connection errors recur, record as infra-confounded, not a code failure') from
    the payload summary ALONE. Pin the four verdict shapes: clean, infra-confounded (the
    H442 launch-3 signature), code-failure (nulls with a quiet network), and the honest
    refusal on a pre-H462 payload that carries no counters."""
    import classify_run as cr
    base = {'agents_spent': 58,
            'translate_agents_spent': 18, 'max_translate_agents': 28,
            'translate_budget_tripped': False,
            'heal_agents_spent': 40, 'max_heal_agents': 55,
            'heal_budget_tripped': False,
            'kill_timeouts': 0, 'conn_errors': 0, 'heal_calls': 40,
            'kill_bisect_blocked': 0, 'null_keys': [], 'budget_kill_switch_tripped': False}
    v, _, sig = cr.classify(dict(base))
    if v != 'clean':
        fail('all-ok summary must classify clean; got %r' % v)
    if sig['partial_cards'] != 0 or sig['partial_keys']:
        fail('historical summary without partial_keys must remain compatible')
    for field in ('translate_agents_spent', 'max_translate_agents',
                  'translate_budget_tripped', 'heal_agents_spent',
                  'max_heal_agents', 'heal_budget_tripped'):
        if sig[field] != base[field]:
            fail('classifier must preserve split-pool signal %s' % field)
    # H442 launch 3: 58/58 agents, 7 kill-timeouts, 2 conn-errors, 12 nulls, tripped
    infra = dict(base, kill_timeouts=7, conn_errors=2,
                 null_keys=['k%d' % i for i in range(12)], budget_kill_switch_tripped=True)
    v, reasons, sig = cr.classify(infra)
    if v != 'infra-confounded':
        fail('the H442 launch-3 signature must classify infra-confounded; got %r' % v)
    if sig['infra_kill_threshold'] != max(3, math.ceil(0.25 * 58)):
        fail('kill threshold must be max(3, 25%% of agents_spent)')
    # nulls + trip with a QUIET network = the harness is the suspect
    code = dict(base, null_keys=['a', 'b'], budget_kill_switch_tripped=True)
    v, _, _ = cr.classify(code)
    if v != 'code-failure':
        fail('nulls with no infra signal must classify code-failure; got %r' % v)
    partial = dict(base, partial_keys=['p1'])
    v, reasons, sig = cr.classify(partial)
    if v != 'code-failure' or sig['partial_cards'] != 1 or sig['partial_keys'] != ['p1']:
        fail('partial-only output must classify code-failure with partial signals; got %r %r' %
             (v, sig))
    if '1 partial card(s)' not in ' '.join(reasons):
        fail('partial-only code-failure reason must name the incomplete card count')
    partial_infra = dict(base, partial_keys=['p1'], conn_errors=1)
    v, _, _ = cr.classify(partial_infra)
    if v != 'infra-confounded':
        fail('partial output plus an infra signal must classify infra-confounded; got %r' % v)
    # kill-timeouts alone (no conn errors) past the 25%% ceiling are ALSO infra
    kills = dict(base, kill_timeouts=58, null_keys=['a'], budget_kill_switch_tripped=True)
    v, _, _ = cr.classify(kills)
    if v != 'infra-confounded':
        fail('mass kill-timeouts (58/58) must classify infra-confounded; got %r' % v)
    # pre-H462 payload: no counters -> unclassifiable, never a guessed verdict
    old = {'agents_spent': 61, 'null_keys': ['a'], 'budget_kill_switch_tripped': True}
    v, reasons, _ = cr.classify(old)
    if v != 'unclassifiable':
        fail('a summary without H462 counters must be unclassifiable; got %r' % v)
    if 'kill_timeouts' not in ' '.join(reasons):
        fail('unclassifiable reason must name the missing counter fields')


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


def test_harness_size_guard():
    """H189 / F-harness-size-limit: the generator must surface an oversize harness at
    generation with a concrete key-disjoint split, so the Workflow scriptPath cap is not
    discovered at launch (pril10_w1: 1.03 MB, unlaunchable). Small harness -> no split."""
    import gen_opt_harness2 as gh
    keys = ['k%d' % i for i in range(9)]
    over, lines = gh.harness_size_report('kAla', keys, True, 1_030_000, 480_000)
    if not over or not lines:
        fail('a 1.03 MB harness over the 480 KB cap must report oversize with a split')
    split_cmds = [ln for ln in lines if '--keys=' in ln]
    if len(split_cmds) < 2:
        fail('oversize report must suggest >=2 key-disjoint sub-windows; got %d' % len(split_cmds))
    # every original key must appear in exactly one sub-window (disjoint, complete)
    seen = []
    for ln in split_cmds:
        seen += ln.split('--keys=')[1].split(' --out=')[0].split(',')
    if sorted(seen) != sorted(keys):
        fail('the suggested split must partition the keys exactly once each; got %r' % seen)
    under, lines2 = gh.harness_size_report('kAla', keys, True, 100_000, 480_000)
    if under or lines2:
        fail('a harness under the cap must not report oversize')


def test_perf_preflight_cost_gate():
    """H189: the preflight cost gate must FLAG a window whose estimated $ per translated
    card exceeds the ceiling (a window of kAla-class monsters — exactly pril10_w1) and must
    PASS a cheap high-card-count window (e.g. `as`: many cards, low per-card cost). The
    per-card ratio is the load-bearing, model-independent signal."""
    import perf_preflight as pp
    # pril10_w1-shape: 8 cards, ~69 fragment-group agents (post-fix) -> ~$4/card >> ceiling
    monster = {'agent_expected_after_tm': 69, 'selected_keys': ['k%d' % i for i in range(8)],
               'tm_cards': 0, 'degenerate_passthrough_keys': []}
    cg = pp.cost_estimate(monster)
    if not cg['over_ceiling'] or cg['est_cost_per_card_usd'] <= cg['per_card_ceiling_usd']:
        fail('a window of 8 monster cards costing ~$4/card must trip the cost gate; got %r' % cg)
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


def test_launch_failure_ledger_complete():
    """Launch failures must be classified with expected/actual economics before a
    handoff closes; H220 must stay represented because that incident was previously
    easier to find in .ai_state/RUN_LOG than in the narrative history."""
    import check_launch_ledger as cl
    entries = cl.load_ledger()
    violations = cl.check_entries(entries)
    if violations:
        fail('launch failure ledger has violations: %r' % violations)
    missing = cl.check_requested(entries, handoff='H220')
    if missing:
        fail('H220 must have a launch failure ledger entry: %r' % missing)


def test_launch_failure_ledger_rejects_incomplete_entry():
    """A ledger block that omits classification / metrics must fail loudly, so the
    closeout ritual cannot silently decay into narrative-only notes."""
    import check_launch_ledger as cl
    bad = [{
        'id': 'BAD',
        'date': '2026-07-07',
        'title': 'incomplete',
        'lane': 'verb batch',
        'model': 'claude-sonnet-5',
        'orchestrator': 'Workflow',
        'expected': {'agents': '1'},
        'actual': {'agents': '2'},
        'passes': 1,
        'symptoms': 'nulls',
        'root_cause': 'unknown',
        'guardrail': 'none',
        'residual_status': 'fixed',
        'residual_risk': 'none',
    }]
    violations = cl.check_entries(bad)
    if not any('classification' in v for v in violations):
        fail('incomplete launch ledger entry must reject missing classification: %r' % violations)
    if not any('expected.tokens' in v for v in violations):
        fail('incomplete launch ledger entry must reject missing expected.tokens: %r' % violations)
    if not any('actual.tokens' in v for v in violations):
        fail('incomplete launch ledger entry must reject missing actual.tokens: %r' % violations)


def test_frag_groups_presplit_parity():
    """H304: frag_groups must reconstruct the SAME partition the harness used to mint the
    gN:fM ids. A presplit card groups at PRESPLIT_GROUP_CITE_BUDGET with a sense count_cap
    (H189), not at SELFHEAL_GROUP_BUDGET — reconstructing with the heal budget mis-maps the
    ids for exactly the giant cards topup exists for."""
    import autosplit_requeue as ar
    from gen_opt_harness2 import _group_by_budget
    fixture = [(si, 0, 'sense %d <ls>A</ls> <ls>B</ls>' % si) for si in range(1, 41)]
    old_plan = ar.plan
    ar.plan = lambda raw, ls_budget=None: fixture
    try:
        meta = {'presplit_keys': ['X'], 'presplit_group_cite_budget': 60,
                'presplit_group_sense_cap': 18, 'selfheal_group_budget': 12}
        sizer = lambda f: 1 + f[2].count('<ls')
        want_presplit = _group_by_budget(fixture, sizer, 60, count_cap=18)
        want_heal = _group_by_budget(fixture, sizer, 12)
        if want_presplit == want_heal:
            fail('fixture too small — presplit and heal partitions must differ for the test')
        got_presplit = ar.frag_groups('ignored', meta=meta, key='X')
        if got_presplit != want_presplit:
            fail('frag_groups(presplit key) does not match the harness presplit partition '
                 '(%d vs %d groups)' % (len(got_presplit), len(want_presplit)))
        got_heal = ar.frag_groups('ignored', meta=meta, key='Y')
        if got_heal != want_heal:
            fail('frag_groups(non-presplit key) must keep the heal-budget partition')
        got_legacy = ar.frag_groups('ignored')
        if got_legacy != want_heal:
            fail('frag_groups without meta must keep the pre-H304 heal-budget behavior')
    finally:
        ar.plan = old_plan


def test_defect_fragment_denylist_round_trip():
    """H304 gate-outcome memory: a defect card's frag_prov fshas (requeue.defect.fshas.txt)
    are appended to the TM denylist by requeue_from_audit, card addresses are denylisted from
    their raw input sha, and the runtime loaders then refuse to serve either class — a
    gate-flagged card/fragment is never re-served by --tm=auto."""
    import requeue_from_audit as rfa
    import translation_memory as tm
    tmp = tempfile.mkdtemp()
    inp = os.path.join(tmp, 'input')
    os.makedirs(inp)
    deny_path = os.path.join(tmp, 'denylist.jsonl')
    key = 'h304root~~h0'
    raw_path = os.path.join(inp, key + '.raw.txt')
    with open(raw_path, 'w', encoding='utf-8') as f:
        f.write('flagged raw card')
    card_address = 'ru:%s' % sha256(raw_path)
    fsha_good = tm.frag_address('ru', 'clean fragment')
    fsha_bad = tm.frag_address('ru', 'flagged fragment')
    fsha_file = os.path.join(tmp, 'requeue.defect.fshas.txt')
    with open(fsha_file, 'w', encoding='utf-8') as f:
        f.write(fsha_bad + '\n')
    old_dp = rfa.translation_memory.denylist_path
    old_inp = rfa.INP
    rfa.translation_memory.denylist_path = lambda path=None: deny_path
    rfa.INP = inp
    try:
        n, nf = rfa.append_tm_denylist('h304root', [key], 'defect', lang='ru',
                                       fsha_file=fsha_file)
    finally:
        rfa.translation_memory.denylist_path = old_dp
        rfa.INP = old_inp
    if (n, nf) != (1, 1):
        fail('append_tm_denylist defect deny count: got %r, want (1, 1)' % ((n, nf),))
    deny = tm.load_denylist(deny_path)
    if card_address not in deny['addresses']:
        fail('defect card address missing from the loaded denylist address set')
    if fsha_bad not in deny['frags']:
        fail('defect fsha missing from the loaded denylist frag set')
    card_tm = os.path.join(tmp, 'translation_memory.ru.json')
    with open(card_tm, 'w', encoding='utf-8') as f:
        json.dump({'schema': tm.CARD_SCHEMA, 'lang': 'ru', 'entries': {
            card_address: {'id': card_address,
                           'card': {'records': [{'senses': [{'russian': 'bad cached card'}]}]},
                           'trust_level': tm.TRUST_MACHINE,
                           'gate_status': 'machine_gated',
                           'reuse_policy': 'auto_exact'}}}, f, ensure_ascii=False)
    if tm.load_tm('ru', card_tm, denylist=deny_path):
        fail('denylisted defect card still served by load_tm')
    senses = [{'tag': '1', 'german': 'x', 'russian': 'y'}]
    sidecar = os.path.join(tmp, 'translation_memory.frag.ru.jsonl')
    with open(sidecar, 'w', encoding='utf-8') as f:
        for fsha in (fsha_good, fsha_bad):
            f.write(json.dumps({'schema': tm.FRAG_SCHEMA_V2, 'fsha': fsha, 'senses': senses,
                                'owners': [['x', '']]}) + '\n')   # R6: v2 (live-reusable)
    cache = tm.load_frag_tm('ru', sidecar, denylist=deny_path)
    if fsha_bad in cache:
        fail('denylisted fragment still served by load_frag_tm')
    if fsha_good not in cache:
        fail('clean fragment wrongly dropped by the denylist')
    # transient requeues must not denylist anything
    n, nf = rfa.append_tm_denylist('h304root', [], 'transient', lang='ru')
    if (n, nf) != (0, 0):
        fail('transient requeue must never append denylist rows')


def test_write_reports_emits_defect_fsha_file():
    """H304: --write-requeue also persists requeue.defect.fshas.txt so requeue_from_audit
    can denylist the flagged fragments without re-reading the wf_output."""
    from window_reports import write_reports
    tmp = tempfile.mkdtemp()
    report = {'workflow': 'wf.json', 'root': 'h304root', 'keys': ['k1'],
              'null_cards': [], 'requeue': ['k1'], 'crashed': [],
              'gates': {}, 'glue': None, 'collect': {},
              'requeue_transient': [], 'requeue_defect': ['k1'],
              'requeue_defect_fshas': ['a' * 64, 'b' * 64],
              'judge_sample': {'keys': [], 'sample_count': 0, 'seed': None,
                               'clean_key_count': 0}}
    write_reports(report, True, out_dir=tmp)
    p = os.path.join(tmp, 'requeue.defect.fshas.txt')
    if not os.path.exists(p):
        fail('requeue.defect.fshas.txt not written by write_reports')
    got = [ln.strip() for ln in open(p, encoding='utf-8') if ln.strip()]
    if got != ['a' * 64, 'b' * 64]:
        fail('defect fsha file content mismatch: %r' % got)


def test_ledger_stamps_gen_model():
    """H390 Phase 1: the window ledger row carries `gen_model`, read from the run's
    own workflow_meta (gen_opt_harness2 stamps meta.gen_model). Without this the
    Fable-vs-Sonnet A/B question is uncomputable — the model that generated a window
    is invisible to every per-window rate. Also pins that a run with no workflow_meta
    degrades to gen_model=None rather than raising."""
    from window_reports import write_reports
    base = {'null_cards': [], 'requeue': [], 'crashed': [], 'gates': {},
            'glue': None, 'collect': {}, 'requeue_transient': [], 'requeue_defect': [],
            'judge_sample': {'keys': [], 'sample_count': 0, 'seed': None,
                             'clean_key_count': 0}}

    def ledger_row_for(report):
        tmp = tempfile.mkdtemp()
        write_reports(report, True, out_dir=tmp)
        ledger = os.path.join(tmp, 'window_ledger.jsonl')
        if not os.path.exists(ledger):
            fail('window_ledger.jsonl not written by write_reports')
        rows = [json.loads(ln) for ln in open(ledger, encoding='utf-8') if ln.strip()]
        if len(rows) != 1:
            fail('expected exactly one ledger row, got %d' % len(rows))
        return rows[0]

    stamped = dict(base, workflow='wf.json', root='h390stamped', keys=['k1'],
                   workflow_meta={'gen_model': 'claude-fable-5'})
    row = ledger_row_for(stamped)
    if 'gen_model' not in row:
        fail('ledger row missing gen_model key entirely')
    if row['gen_model'] != 'claude-fable-5':
        fail('ledger gen_model mismatch: %r' % row.get('gen_model'))

    # No workflow_meta at all -> None, never a KeyError.
    bare = dict(base, workflow='wf.json', root='h390bare', keys=['k1'])
    row = ledger_row_for(bare)
    if row.get('gen_model') is not None:
        fail('bare-run ledger gen_model should be None, got %r' % row.get('gen_model'))


def test_save_merge_better_attempt_wins():
    """H304: 'latest requeue wins' is WRONG — a requeue can regress a card (gam h0_63_sam_0
    went 2->3->7 missing fragments). --merge must keep the better prior attempt: complete
    beats partial, fewer missing fragments beat more; a complete fresh card still replaces."""
    from window_common import REPO as repo_root
    save = os.path.join(repo_root, 'save_and_audit.py')
    root, tag = 'h304tmp', 'sftest'
    out_path = os.path.join(repo_root, 'wf_output.%s.%s.json' % (tag, root))
    tmp = tempfile.mkdtemp()

    def wf(card):
        return {'result': {'meta': {'root': root},
                           'results': [{'key': 'k1', 'card': card}]}}

    def save_run(name, card, *extra):
        p = os.path.join(tmp, name)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(wf(card), f)
        run([sys.executable, save, root, p, tag, '--no-audit'] + list(extra), expect=0)

    def valid_card(marker, **extra):
        card = {'key1': 'k1', 'iast': 'k1', 'notes': '', 'senses_marker': marker,
                'records': [{'h': 'k1', 'grammar': '', 'senses': [
                    {'tag': '1', 'german': 'Deutsch', 'russian': 'русский'}]}]}
        card.update(extra)
        return card

    try:
        complete = valid_card('first-complete')
        save_run('a.json', complete)
        worse = valid_card('regression', partial=True,
                           missing_fragments=['g1:f0', 'g1:f1'])
        save_run('b.json', worse, '--merge')
        got = json.load(open(out_path, encoding='utf-8'))
        card = got['results'][0]['card']
        if card.get('partial') or card.get('senses_marker') != 'first-complete':
            fail('--merge let a partial attempt regress a complete card')
        fresh = valid_card('second-complete')
        save_run('c.json', fresh, '--merge')
        got = json.load(open(out_path, encoding='utf-8'))
        if got['results'][0]['card'].get('senses_marker') != 'second-complete':
            fail('an equal-quality fresh card must still replace (ties go to new)')
    finally:
        if os.path.exists(out_path):
            os.remove(out_path)


def test_defer_monster_ledger_dedupes():
    """H304 cap-and-defer: the deferred-monsters ledger is append-only and deduped on
    (target, reason, UTC day) so a daily coordinator sweep cannot flood it."""
    from window_common import defer_monster
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, 'deferred_monsters.jsonl')
    row = defer_monster('kAla', 'cost_gate_over_ceiling',
                        estimate={'est_cost_usd': 79.83}, keys=['kAla~~h0_00'], path=p)
    if not row or row.get('schema') != 'pwg.deferred_monsters.v1':
        fail('first defer_monster call must write a schema-stamped row')
    if defer_monster('kAla', 'cost_gate_over_ceiling', path=p) is not None:
        fail('same (target, reason, day) must dedupe to None')
    if defer_monster('kAla', 'defer-calibrate', path=p) is None:
        fail('a different reason for the same target must append')
    lines = [ln for ln in open(p, encoding='utf-8') if ln.strip()]
    if len(lines) != 2:
        fail('ledger must hold exactly 2 rows, got %d' % len(lines))


def test_coordinator_cost_gate_enforced():
    """H304: coordinator prepare refuses a cost-gate-flagged window (parks it in the
    deferred ledger) unless --allow-over-cost; a clean window passes untouched."""
    import coordinator as co
    tmp = tempfile.mkdtemp()
    flagged = os.path.join(tmp, 'preflight.json')
    with open(flagged, 'w', encoding='utf-8') as f:
        json.dump({'reports': [{'root': 'kAla',
                                'cost_gate': {'over_ceiling': True, 'est_cost_usd': 79.83,
                                              'est_cost_per_card_usd': 4.0},
                                'cost_partition': {'run_now': ['a'],
                                                   'defer_monster': ['b', 'c']}}]}, f)
    clean = os.path.join(tmp, 'preflight_clean.json')
    with open(clean, 'w', encoding='utf-8') as f:
        json.dump({'reports': [{'root': 'vah', 'cost_gate': {'over_ceiling': False}}]}, f)
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


def test_pwg_mask_bom_source_keeps_first_record():
    """Hardening (H316; FL6 / CODE_REVIEW 2026-07-04): a UTF-8 BOM on the PWG
    source used to leave the first line as BOM+'<L>...', which
    startswith('<L>') misses -- the FIRST record of the dictionary was silently
    dropped. records() now reads utf-8-sig (a no-op on BOM-less files).
    SHARED (stage-0 masking, before any --lang branch)."""
    import tempfile
    import pwg_mask
    body = ('<L>1<pc>1,1<k1>agni<k2>agni\nFeuer\n<LEND>\n'
            '<L>2<pc>1,1<k1>ap<k2>ap\nWasser\n<LEND>\n')
    for bom, label in ((b'\xef\xbb\xbf', 'BOM'), (b'', 'no-BOM')):
        tf = tempfile.NamedTemporaryFile('wb', suffix='.txt', delete=False)
        tf.write(bom + body.encode('utf-8'))
        tf.close()
        old = pwg_mask.PWG
        pwg_mask.PWG = tf.name
        try:
            recs = list(pwg_mask.records())
        finally:
            pwg_mask.PWG = old
            os.unlink(tf.name)
        if len(recs) != 2:
            fail('%s source: expected 2 records, got %d' % (label, len(recs)))
        if not recs[0][0].startswith('<L>1'):
            fail('%s source: first record dropped/mangled: %r' % (label, recs[0][0]))


def test_pwg_mask_truncated_final_record_not_silent():
    """Hardening (H316): a final record opened with <L> but never closed by
    <LEND> (truncated source) must not be yielded downstream -- but it must not
    vanish silently either: records() warns on stderr."""
    import contextlib
    import io
    import tempfile
    import pwg_mask
    body = ('<L>1<pc>1,1<k1>agni<k2>agni\nFeuer\n<LEND>\n'
            '<L>2<pc>1,1<k1>ap<k2>ap\nWasser\n')  # no closing <LEND>
    tf = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8')
    tf.write(body)
    tf.close()
    old = pwg_mask.PWG
    pwg_mask.PWG = tf.name
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            recs = list(pwg_mask.records())
    finally:
        pwg_mask.PWG = old
        os.unlink(tf.name)
    if len(recs) != 1:
        fail('truncated source: expected 1 complete record, got %d' % len(recs))
    if 'truncated final record' not in err.getvalue():
        fail('truncated final record dropped SILENTLY -- warning missing')


def test_subprocess_gate_calls_hardened():
    """Hardening (H316): Windows cp1252 pitfall + hang guard. Gate/driver
    subprocess.run calls that capture child output must pass encoding='utf-8';
    shell-outs wrapping potentially long children must carry a timeout. Static
    wiring pin so a refactor cannot silently regress either."""
    checks = [
        (os.path.join(SRC, 'make_edition_cut.py'), "encoding='utf-8'"),
        (os.path.join(SRC, 'preflight_remaining_gates.py'), "encoding='utf-8'"),
        (os.path.join(SRC, 'release_readiness.py'), "encoding='utf-8'"),
        (os.path.normpath(os.path.join(SRC, '..', 'save_and_audit.py')), 'timeout=1800'),
        (os.path.join(HERE, 'audit_window.py'), 'timeout=1800'),
        (os.path.join(HERE, 'autosplit_requeue.py'), 'timeout=600'),
    ]
    for path, needle in checks:
        with open(path, encoding='utf-8') as f:
            src_txt = f.read()
        if 'subprocess.run' in src_txt and needle not in src_txt:
            fail('%s: expected %r on its subprocess.run call(s)'
                 % (os.path.basename(path), needle))


def test_ls_resolver_rv_av_anchored():
    """H321 item #5: Ṛgveda/Atharva disambiguation must be ANCHORED on the leading
    citation abbreviation, not a bare `'rv' in kl or 'ṛ' in kl` substring that
    mis-routes any citation merely CONTAINING those characters (parv., gṛ., kṛ.)
    to the RV hymn URL."""
    import ls_resolver as L
    # RV-family abbreviations → rv; AV / everything else → av (default).
    for key, want in [('ṚV.', True), ('RV.', True), ('ṛv.', True),
                      ('AV.', False), ('Nir.', False),
                      ('parv.', False), ('Gṛ.', False), ('kṛ.', False)]:
        got = L._is_rv_prefix(key)
        if got != want:
            fail('_is_rv_prefix(%r) = %r, want %r (anchored, not substring)' % (key, got, want))
    # The fragile substring form must be gone from the source.
    src_txt = open(os.path.join(SRC, 'ls_resolver.py'), encoding='utf-8').read()
    if "'rv' in kl" in src_txt or "'ṛ' in kl" in src_txt:
        fail('ls_resolver still uses the substring RV/AV disambiguation')
    # The two pattern-engine excepts must surface, not silently `pass`.
    if src_txt.count('except Exception:\n            pass') or '_warn_swallowed' not in src_txt:
        fail('ls_resolver pattern-engine excepts must surface via _warn_swallowed, not pass')
    # Live resolution still correct for genuine RV/AV samhita citations.
    if 'rvhymns' not in (L.generate_href('pwg', 'ṚV. ', '10,85,24') or ''):
        fail('ṚV. citation must still resolve to the rv hymns URL')
    if 'avhymns' not in (L.generate_href('pwg', 'AV. ', '11,4,26') or ''):
        fail('AV. citation must still resolve to the av hymns URL')


def test_frag_tm_fidelity_gate_and_override():
    """H321 item #3b: build_frags must NOT harvest a corrupt/blanked frag_prov
    (first-seen-wins previously let a hand-edited wf_output poison content-addressed
    fragment reuse), load_frag_tm must not SERVE such a row, and a later good harvest
    must be able to override a previously-cached corrupt row."""
    import translation_memory as tm
    # 1) frag_senses_sane: blank/malformed senses are rejected.
    if tm.frag_senses_sane([{'tag': '1', 'russian': 'фу'}], 'ru') is not True:
        fail('a sane ru fragment sense must pass frag_senses_sane')
    if tm.frag_senses_sane([{'tag': '1', 'russian': '  '}], 'ru') is not False:
        fail('a blank-translation fragment sense must fail frag_senses_sane')
    if tm.frag_senses_sane([], 'ru') is not False:
        fail('empty senses must fail frag_senses_sane')

    d = tempfile.mkdtemp()
    old_repo = tm.REPO
    try:
        tm.REPO = d
        good_src = '=== h ===\n1) foo <ls>ṚV.</ls>'
        bad_src = '=== h ===\n1) bar <ls>AV.</ls>'
        good_fsha = tm.frag_address('ru', good_src)
        bad_fsha = tm.frag_address('ru', bad_src)
        good_senses = [{'tag': '1', 'german': 'foo', 'russian': 'фу'}]
        blank_senses = [{'tag': '1', 'german': 'bar', 'russian': ''}]
        wf = {'meta': {'lang': 'ru', 'root': 'zz'}, 'results': [
            {'key': 'zz~~h0', 'card': {'key1': 'zz', 'records': [{'senses': good_senses}],
                                       'frag_prov': [{'fsha': good_fsha, 'senses': good_senses,
                                                      'owners': [['zz', '']]},   # R6: v2 (live-reusable)
                                                     {'fsha': bad_fsha, 'senses': blank_senses,
                                                      'owners': [['zz', '']]}]}}]}
        with open(os.path.join(d, 'wf_output.sc.zz.json'), 'w', encoding='utf-8') as f:
            json.dump(wf, f, ensure_ascii=False)
        sidecar = os.path.join(d, 'frag.ru.jsonl')
        _p, added, _tot = tm.build_frags('wf_output.sc.*.json', 'ru', out=sidecar)
        served = tm.load_frag_tm('ru', sidecar)
        if good_fsha not in served:
            fail('a sane fragment must be harvested and served')
        if bad_fsha in served:
            fail('a corrupt (blank-sense) fragment must NOT be harvested/served')

        # 2) Later-good override: pre-seed a CORRUPT row for an fsha, then harvest a
        # good one for the same fsha — the good row must win at serve.
        d2 = tempfile.mkdtemp()
        try:
            tm.REPO = d2
            sidecar2 = os.path.join(d2, 'frag.ru.jsonl')
            with open(sidecar2, 'w', encoding='utf-8') as f:
                f.write(json.dumps({'schema': tm.FRAG_SCHEMA, 'lang': 'ru', 'fsha': good_fsha,
                                    'senses': [{'tag': '1', 'russian': ''}],  # corrupt
                                    'trust_level': tm.TRUST_MACHINE,
                                    'harvested_at': '2026-01-01T00:00:00Z'}, ensure_ascii=False) + '\n')
            if tm.load_frag_tm('ru', sidecar2):
                fail('serve-time filter must drop a corrupt historical row (empty served map)')
            with open(os.path.join(d2, 'wf_output.sc.zz.json'), 'w', encoding='utf-8') as f:
                json.dump(wf, f, ensure_ascii=False)
            tm.build_frags('wf_output.sc.*.json', 'ru', out=sidecar2)
            served2 = tm.load_frag_tm('ru', sidecar2)
            if good_fsha not in served2:
                fail('a later GOOD harvest must override a previously-cached corrupt row')
        finally:
            shutil.rmtree(d2, ignore_errors=True)
    finally:
        tm.REPO = old_repo
        shutil.rmtree(d, ignore_errors=True)


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


def test_promote_claim_contention():
    """H336/H-1: the O_EXCL promotion claim file — a second claimant on a live claim
    must retry/error cleanly (not silently proceed to race the read-guard-write window),
    a stale (TTL-expired) claim is reclaimed with NO PID-liveness check (meaningless
    across clones/machines — the whole point of this claim over coordinator.DirLock),
    and --steal-lock bypasses even a fresh claim. Pins promote_lock.py's own selftest
    into the aggregate suite rather than re-deriving the contention scenario here."""
    import promote_lock
    promote_lock.selftest()


def test_annotate_evidence_relation_semantics():
    """H337 (W2): the per-sense evidence relation classifier. Pins annotate_evidence.py's
    own pure-function selftest (provides = exact Russian equivalent; supports = token
    containment >= corpus_gate.THRESHOLD; a citation-only sense yields nothing; a source
    with no usable meaning tokens is SILENT not contradicts; the lemma summary is
    lemma-scoped and shared across a lemma's rows). No gate-source file IO, so it runs in
    CI where the gitignored src/*.jsonl dictionaries are absent."""
    import annotate_evidence
    annotate_evidence.selftest()


def test_annotate_genres_sense_join():
    """H339 (W4): per-sense citation genre join (annotate_genres.py). Pins its own
    pure-function selftest — coarse-bucket rollup keyed off the curated genre label's
    leading word (Kāvya/Veda/Epic/Śāstra/Purāṇa/Kośa), an unmapped-only citation set
    stays [] (unknown, never conflated with 'only genre X'), and multi-genre senses
    keep every cited bucket."""
    import annotate_genres
    annotate_genres.selftest()


def test_koch_xref_resolution():
    """H397 (H337 follow-up): koch's bare `см. X` cross-reference resolver — the
    Devanagari self-header crosswalk, one-hop resolution, chain-safe cycle guard, and
    the resolve_koch_lane() wrapper annotate_evidence.gather() calls. Pins
    koch_xref.py's own pure-function selftest (no koch.jsonl file IO, so it runs in CI
    where the gitignored src/*.jsonl dictionaries are absent)."""
    import koch_xref
    koch_xref.selftest()


def test_fri_xref_resolution():
    """H404 (H397 generalization): fri's bare Latin-apparatus (v./cf./q.v.) redirect
    resolver — targets are already roman (build_src.iast_to_slp1 reused, no Devanagari
    crosswalk needed), one hop, and the resolve_fri_lane() wrapper
    annotate_evidence.gather() calls. Pins fri_xref.py's own pure-function selftest
    (no fri.jsonl file IO, so it runs in CI where the gitignored src/*.jsonl
    dictionaries are absent)."""
    import fri_xref
    fri_xref.selftest()


def test_audit_window_tag_routing():
    """H336/H-2: --window-tag routes window_status/report/requeue/judge-sample to
    src/pilot/output/<tag>/ instead of the flat singletons, so two accounts auditing
    different windows in ONE clone cannot clobber each other's status. Untagged
    invocation must still write the flat singletons (backward compatible)."""
    from safe_filename import safe_name
    tag_dir = os.path.join(OUT, safe_name('selftest_tag_zzqq'))
    if os.path.isdir(tag_dir):
        shutil.rmtree(tag_dir)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.json', delete=False) as f:
        wf_path = f.name
        json.dump({'meta': {'rootmap_sha256': None}, 'results': []}, f)
    try:
        proc = run([sys.executable, os.path.join(SRC, 'pilot', 'audit_window.py'),
                   wf_path, '--root', 'zzqq', '--window-tag', 'selftest_tag_zzqq',
                   '--allow-stale'], expect=0)
        status_path = os.path.join(tag_dir, 'window_status.json')
        report_path = os.path.join(tag_dir, 'audit_window.report.json')
        if not os.path.exists(status_path):
            fail('--window-tag must write window_status.json under output/<tag>/, got:\n%s'
                 % proc.stdout)
        if not os.path.exists(report_path):
            fail('--window-tag must write audit_window.report.json under output/<tag>/')
        live_status = os.path.join(OUT, 'window_status.json')
        live_before = (open(live_status, encoding='utf-8').read()
                      if os.path.exists(live_status) else None)
        # A bare --root run (no tag) must be unaffected by the tag dir's existence.
        if live_before is not None:
            got = json.loads(open(live_status, encoding='utf-8').read())
            if got.get('root') == 'zzqq':
                fail('a tagged run must not also overwrite the flat OUT singleton')
    finally:
        os.remove(wf_path)
        if os.path.isdir(tag_dir):
            shutil.rmtree(tag_dir)


def test_denylist_torn_line_fails_loud():
    """P0.1 / H336-H3: translation_memory.load_denylist must FAIL loudly on a torn/
    undecodable JSONL line instead of continuing with a partial deny set — a silently-dropped
    denylist row is a correctness hole (a gate-rejected address quietly becomes TM-reusable
    again), the scariest single entry in the H335 collision matrix."""
    import translation_memory as tm
    d = tempfile.mkdtemp()
    path = os.path.join(d, 'denylist.jsonl')
    good = {'schema': 'pwg.translation_memory.denylist.v1', 'kind': 'card',
            'address': 'ru:deadbeef', 'key': 'x~~h0', 'root': 'x', 'lang': 'ru',
            'reason': 'requeue_defect', 'blocked_at': '2026-07-08T00:00:00Z'}
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(good, ensure_ascii=False) + '\n')
        f.write('{"kind": "card", "address": "ru:TORN_MID_LINE\n')   # deliberately truncated/torn
    proc = subprocess.run(
        [sys.executable, '-c',
         "import sys; sys.path.insert(0, %r); import translation_memory as tm; "
         "tm.load_denylist(%r)" % (HERE, path)],
        capture_output=True, text=True, encoding='utf-8')
    if proc.returncode == 0:
        fail('load_denylist must fail on a torn line, got success:\n%s\n%s'
             % (proc.stdout, proc.stderr))
    if 'DenylistError' not in proc.stderr or 'torn/undecodable denylist line' not in proc.stderr:
        fail('load_denylist must surface a DenylistError for a torn line, got:\n%s' % proc.stderr)


def test_strip_mask_tokens_clears_notes_stranded_anchor():
    # H858: the model sometimes MENTIONS a masking placeholder in its free-text
    # `notes` ("Masked span {T1} is a citation reference…"). Rendered verbatim
    # into the .merged.md blockquote, that mention made stage2_pregate misfire a
    # STRANDED-ANCHOR on an otherwise-clean card (7/15 no_pwg_w09 false positives).
    import _pilot_collect as pc
    if pc.strip_mask_tokens('Masked span {T1} is a citation.') != 'Masked span is a citation.':
        fail('strip_mask_tokens did not strip {T1} + tidy the gap')
    if pc.strip_mask_tokens('echoed {Tn} literal') != 'echoed literal':
        fail('strip_mask_tokens did not strip the literal {Tn} example token')
    if pc.strip_mask_tokens('plain note, no tokens') != 'plain note, no tokens':
        fail('strip_mask_tokens altered clean text')
    # integration: notes mentioning {T1} must not leak a placeholder into the render
    md = pc.render({'key': 'x~~h0_zz_pw', 'card': {
        'key1': 'x', 'iast': 'x', 'notes': 'Masked span {T1} is a citation reference.',
        'records': [{'h': '0', 'grammar': 'm.', 'senses': [
            {'tag': '1', 'german': 'a', 'russian': 'b', 'equivalence_type': 'equivalent',
             'source_type': 'lexicographic', 'stratum': '', 'differentia': ''}]}]}})
    if '{T1}' in md or '{Tn}' in md:
        fail('render() leaked a {Tn} masking token from notes into merged.md')


def test_restore_covers_every_promoted_field():
    """C-01: restore's field set and promote's read set are ONE constant, not two lists.

    The defect: `restore_card` unmasked 3 fields while `rows_for` promoted 6, so card.iast /
    record.h / sense.tag / sense.differentia reached the canonical store with their {Tn}
    intact -- 670 rows, 223 of them a raw {Tn} in the HEADWORD field. Two independently
    hand-maintained lists could drift; one constant cannot.
    """
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    import card_fields
    # Both language lanes: every field the promoter reads must have been unmasked first.
    for field in ('russian', 'english'):
        promoted = set(card_fields.promoted_pairs(field))
        restored = set(card_fields.restored_pairs(field))
        missing = promoted - restored
        if missing:
            fail('fields promoted but never restored (%s): %s' % (field, sorted(missing)))
    # The JS lane cannot import Python, so its list is interpolated from the same constant.
    spec = json.loads(card_fields.js_restore_spec('russian'))
    if set(spec['record']) != set(card_fields.RECORD_MASKED):
        fail('js_restore_spec record set drifted from RECORD_MASKED')
    if 'h' not in spec['record']:
        fail('the JS lane must restore record.h -- it is promoted verbatim')

    # And the restore actually reaches those fields, end to end.
    card = {'iast': '{T1}', 'records': [{'h': '{T1}', 'grammar': '{T1}', 'senses': [
        {'tag': '{T1}', 'german': '{T1}', 'russian': '{T1}', 'differentia': '{T1}'}]}]}
    card_fields.restore_card_fields(card, 'russian', lambda t: t.replace('{T1}', 'X'))
    rec, sense = card['records'][0], card['records'][0]['senses'][0]
    for where, value in (('card.iast', card['iast']), ('record.h', rec['h']),
                         ('record.grammar', rec['grammar']), ('sense.tag', sense['tag']),
                         ('sense.german', sense['german']), ('sense.russian', sense['russian']),
                         ('sense.differentia', sense['differentia'])):
        if value != 'X':
            fail('%s was not restored (still %r)' % (where, value))


def test_every_stitch_emits_record_required():
    """C-02: the stitch must emit `h`/`grammar`, and must not collapse distinct homonyms.

    The defect: both stitch lanes built `records: [{senses}]`, discarding record-level h and
    grammar unconditionally, so promote wrote `h: null` -- 468 store rows over 20 sub-cards.
    That also violates schemas/pwg_ru_final_card.schema.json (record.required =
    {h, grammar, senses}), which nothing checked on live output (C-04).
    """
    import headless_worker as hw
    senses = [{'tag': '1'}, {'tag': '2'}, {'tag': '3'}]
    owners = [('1. bhid', 'm.'), ('1. bhid', 'm.'), ('2. bhid', 'f.')]
    records = hw.stitch_records(senses, owners)
    if len(records) != 2:
        fail('two distinct owners must yield two records, got %d' % len(records))
    if records[0]['h'] != '1. bhid' or records[1]['h'] != '2. bhid':
        fail('stitch dropped or reordered the record-level h: %r' % records)
    if records[0]['grammar'] != 'm.' or records[1]['grammar'] != 'f.':
        fail('stitch dropped the record-level grammar: %r' % records)
    for rec in records:
        for key in ('h', 'grammar', 'senses'):
            if key not in rec:
                fail('stitched record missing schema-required %r' % key)
    if [s['tag'] for r in records for s in r['senses']] != ['1', '2', '3']:
        fail('stitch must preserve document order of senses')
    # A single owner stays ONE record -- no gratuitous fragmentation.
    if len(hw.stitch_records(senses, [('h', 'g')] * 3)) != 1:
        fail('one owner must yield exactly one record')

    import autosplit_requeue as ar
    split_records = ar._stitch_owned_senses(senses, owners)
    if [(r['h'], r['grammar']) for r in split_records] != [
            ('1. bhid', 'm.'), ('2. bhid', 'f.')]:
        fail('autosplit stitch lost record owners: %r' % split_records)
    topup_manifest = [{
        'orig': 'bhid', 'iast': 'bhid', 'notes': '',
        'owners_by_tag': {'1': ['1. bhid', 'm.'], '2': ['2. bhid', 'f.']},
        'default_owner': ['1. bhid', 'm.'],
        'plan': [
            {'s': 0, 'p': 0, 'fsha': 'a', 'fk': 'old', 'missing': False},
            {'s': 1, 'p': 0, 'fsha': 'b', 'fk': 'new', 'missing': True}],
        'resolved': {'a': [{'tag': '1', 'german': 'g1', 'russian': 'r1'}]}}]
    new_fragment = {'records': [{'h': '2. bhid', 'grammar': 'f.', 'senses': [
        {'tag': '2', 'german': 'g2', 'russian': 'r2'}]}]}
    rows, missing = ar.stitch_topup(topup_manifest, {'new': new_fragment}, 'russian')
    recs = rows[0]['card']['records']
    if missing or [(r['h'], r['grammar']) for r in recs] != [
            ('1. bhid', 'm.'), ('2. bhid', 'f.')]:
        fail('top-up stitch lost a record boundary/owner: %r %r' % (rows, missing))


def test_unmapped_token_is_counted():
    """C-42: an out-of-range {Tn} is counted, not silently passed through.

    The defect: `restore_text` returned `match.group(0)` for an index the map does not
    address, with no counter, no log and no reject -- so `ban_d~~h0_11_ni` and
    `ban_d~~h0_21_upasam_0` reached the canonical store carrying a raw {T196}/{T235} on cards
    that reported success. Cause is a masking-scope vs restore-scope index mismatch (article
    masked whole, restored per sub-card), not model hallucination.
    """
    import headless_worker as hw
    unmapped = []
    out = hw.restore_text('a {T1} b {T99} c', ['<ls>x</ls>'], unmapped)
    if '<ls>x</ls>' not in out:
        fail('an in-range token must still restore')
    if unmapped != ['{T99}']:
        fail('an out-of-range token must be counted, got %r' % unmapped)
    if '{T99}' not in out:
        fail('behaviour change: the out-of-range token must still pass through verbatim')
    clean = []
    hw.restore_text('a {T1} b', ['x'], clean)
    if clean:
        fail('a fully-mapped text must report no unmapped tokens, got %r' % clean)


def test_validator_has_a_live_caller():
    """C-04 dead-validator canary: the record contract must run on LIVE output.

    `validate_final_card_schema` is the ONLY component encoding record.required =
    {h, grammar, senses}, and its only caller was a CI step feeding it a hand-made PASSING
    fixture. A green check certified a contract no real card was measured against -- which is
    precisely why C-01's 670 placeholder rows and C-02's 468 null-h rows accumulated with no
    signal. This asserts the validator is reachable from the save chain, and that it still
    refuses a record missing `h`.
    """
    from window_common import REPO as repo_root
    save = os.path.join(repo_root, 'save_and_audit.py')
    text = open(save, encoding='utf-8').read()
    if 'validate_final_card_schema' not in text:
        fail('save_and_audit.py has no reference to validate_final_card_schema -- the '
             'validator is dead again (C-04)')
    if 'validate_card(' not in text:
        fail('save_and_audit.py imports the validator but never calls validate_card()')

    audit_path = os.path.join(SRC, 'pilot', 'audit_window.py')
    audit_text = open(audit_path, encoding='utf-8').read()
    if 'run_final_schema_gate' not in audit_text or 'validate_card(' not in audit_text:
        fail('audit_window.py does not validate real workflow cards')

    promote_path = os.path.join(SRC, 'promote_final_cards.py')
    promote_text = open(promote_path, encoding='utf-8').read()
    if 'validate_promotion_entry' not in promote_text or 'validate_card(' not in promote_text:
        fail('promote_final_cards.py lacks independent final-schema validation')

    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    import validate_final_card_schema as v
    if v.RECORD_REQUIRED != {'h', 'grammar', 'senses'}:
        fail('RECORD_REQUIRED was relaxed: %r' % (v.RECORD_REQUIRED,))
    # The contract must actually reject the shape C-02 was writing.
    bad = {'key1': 'k', 'iast': 'k', 'notes': '', 'records': [{'senses': [
        {'tag': '1', 'german': 'g', 'russian': 'r', 'equivalence_type': 'equivalent',
         'source_type': 'attested', 'stratum': '', 'differentia': ''}]}]}
    try:
        v.validate_card(bad)
    except ValueError:
        pass
    else:
        fail('validate_card accepted a record with no h/grammar -- the C-02 shape')

    import audit_window
    good = {'key1': 'k', 'iast': 'k', 'notes': '', 'records': [{
        'h': 'k', 'grammar': '', 'senses': [{
            'tag': '1', 'german': 'g', 'russian': 'r',
            'equivalence_type': 'equivalent', 'source_type': 'attested',
            'stratum': '', 'differentia': ''}]}]}
    ok_gate = audit_window.run_final_schema_gate([{'key': 'k', 'card': good}])
    if ok_gate.get('returncode') != 0 or ok_gate.get('requeue'):
        fail('audit final-schema gate rejected a valid card: %r' % ok_gate)
    bad_gate = audit_window.run_final_schema_gate([{'key': 'k', 'card': bad}])
    if bad_gate.get('returncode') != 1 or bad_gate.get('requeue') != ['k']:
        fail('audit final-schema gate did not requeue an invalid live card: %r' % bad_gate)


def test_h_reconstructed_regression_guard():
    """D-1 (H1149): `cohort_clean_rates.assert_h_reconstructed_regression` must FAIL
    LOUD the instant the store's `h_reconstructed` count silently drifts off 468, and
    stay green at 468 -- the exact failure mode this guards against already happened
    once (PR #510's underlying `h is None` count fell 468 -> 0 and became invisible to
    the only query that could find it, Uprava FINDINGS §95). "A guard that passes on a
    mutated store is not a guard" (H1149) -- so this test builds a SYNTHETIC store (not
    the real gitignored canonical one, so it stays deterministic off-disk everywhere)
    and proves both directions: 467 markers -> AssertionError; 468 -> clean pass; a
    467-count WITH an authorized re-translation manifest documenting exactly that
    decrease -> accepted.
    """
    import cohort_clean_rates as ccr

    with tempfile.TemporaryDirectory() as tmp:
        store = os.path.join(tmp, 'pwg_ru_translated.jsonl')

        def write_store(n_marked, total=500):
            with open(store, 'w', encoding='utf-8') as f:
                for i in range(total):
                    row = {
                        'key1': 'k%d' % i, 'subcard': 'k%d~~h0_00_pwg00' % i, 'layer': 'pwg',
                        'h': 'h%d' % (i % 14),
                        'provenance': ({'h_reconstructed': True} if i < n_marked else {}),
                    }
                    f.write(json.dumps(row, ensure_ascii=False) + '\n')

        write_store(468)
        got = ccr.assert_h_reconstructed_regression(store, expected=468)
        if got != 468:
            fail('guard mis-measured a clean 468 store: got %r' % got)

        write_store(467)  # simulate ONE silently dropped marker
        try:
            ccr.assert_h_reconstructed_regression(store, expected=468)
        except AssertionError:
            pass
        else:
            fail('h_reconstructed regression guard did NOT fail at 467 -- not a real guard')

        write_store(468)  # restore
        ccr.assert_h_reconstructed_regression(store, expected=468)

        # An authorized re-translation manifest documenting the SAME decrease is accepted.
        write_store(467)
        manifest = os.path.join(tmp, 'retranslation_manifest.json')
        with open(manifest, 'w', encoding='utf-8') as f:
            json.dump({'schema': 'pwg_ru.h_reconstructed_retranslation_manifest.v1',
                       'new_count': 467, 'note': 'selftest fixture'}, f)
        got = ccr.assert_h_reconstructed_regression(store, expected=468, manifest_path=manifest)
        if got != 467:
            fail('guard did not accept an authorized documented decrease: got %r' % got)

        # A manifest that does NOT match the actual count is NOT an excuse.
        write_store(466)
        try:
            ccr.assert_h_reconstructed_regression(store, expected=468, manifest_path=manifest)
        except AssertionError:
            pass
        else:
            fail('guard accepted a manifest whose new_count does not match the actual '
                 'measured count -- an unrelated manifest must not paper over a real drop')


def test_card_tokens_twins_agree():
    """R2/C-17 (closes N-4): the JS `cardTokens` fidelity collector is DRIVEN by the Python-owned
    card_fields.js_token_fidelity_spec(), so the two twins cannot drift. Proven three ways: the
    generated JS interpolates the exact spec; cardTokens iterates it (not a hard-coded field list);
    and changing the Python-owned spec changes the generated JS collector."""
    import re as _re
    import gen_opt_harness2 as gh
    import card_fields as cf

    def _gen():
        d = tempfile.mkdtemp()
        rp = os.path.join(d, 'agni~~h0_zz_pw.raw.txt')
        pp = os.path.join(d, 'agni~~h0_zz_pw.portrait.json')
        with open(rp, 'w', encoding='utf-8') as f:
            f.write('=== LAYER: PW ===\n\n{#agni#}¦ m. {%a%}\n— 1〉 Feuer.')
        with open(pp, 'w', encoding='utf-8') as f:
            f.write('[]')
        saved = gh.input_paths
        gh.input_paths = lambda k, input_dir=None: (rp, pp)
        try:
            js, _ = gh.build('zz', ['agni~~h0_zz_pw'], None, 12000, nominal=True,
                             grammar_on=False, tm_path=None)
        finally:
            gh.input_paths = saved
        return js

    js = _gen()
    m = _re.search(r'const TOKEN_FIDELITY_SPEC = (\{.*?\})\n', js)
    if not m:
        fail('generated JS does not interpolate TOKEN_FIDELITY_SPEC')
    if m.group(1) != cf.js_token_fidelity_spec():
        fail('JS TOKEN_FIDELITY_SPEC != card_fields.js_token_fidelity_spec(): %s' % m.group(1))
    if 'TOKEN_FIDELITY_SPEC.record' not in js or 'TOKEN_FIDELITY_SPEC.sense' not in js:
        fail('cardTokens is not driven by the interpolated TOKEN_FIDELITY_SPEC')
    saved = cf.TOKEN_FIDELITY_FIELDS
    cf.TOKEN_FIDELITY_FIELDS = (('record', 'grammar'), ('sense', 'german'), ('sense', 'tag'))
    try:
        m2 = _re.search(r'const TOKEN_FIDELITY_SPEC = (\{.*?\})\n', _gen())
        if not m2 or '"tag"' not in m2.group(1) or m2.group(1) == m.group(1):
            fail('JS collector did not follow the Python-owned spec change: %s' % (m2 and m2.group(1)))
    finally:
        cf.TOKEN_FIDELITY_FIELDS = saved
    print('  R2/N-4: JS cardTokens is driven by card_fields.js_token_fidelity_spec() (twins cannot drift)')


def test_frag_tm_v2_supersedes_v1():
    """R6: fragment-TM v2 schema. A v1 (ownerless) row is readable for audit but NEVER live-reusable;
    a valid v2 row with the same fsha supersedes it; and an existing v1 does NOT block a v2 harvest.
    Owners count/shape are validated."""
    import json as _json
    import translation_memory as tm
    d = tempfile.mkdtemp()
    path = os.path.join(d, 'translation_memory.frag.ru.jsonl')
    sense = {'tag': '1', 'german': 'Feuer', 'russian': 'огонь'}
    v1 = {'schema': tm.FRAG_SCHEMA, 'lang': 'ru', 'fsha': 'X', 'n_senses': 1, 'senses': [sense],
          'trust_level': tm.TRUST_MACHINE, 'gate_status': 'machine_gated',
          'reuse_policy': 'auto_exact', 'source_kind': 'frag_prov'}
    with open(path, 'w', encoding='utf-8') as f:
        f.write(_json.dumps(v1) + '\n')
    if tm.load_frag_tm('ru', path) != {}:
        fail('a v1 (ownerless) row must not be live-served')
    if 'X' not in tm.load_frag_tm('ru', path, live_only=False):
        fail('a v1 row must stay readable for historical audit (live_only=False)')
    wf = os.path.join(d, 'wf_output.zz.json')
    card = {'key1': 'agni', 'frag_prov': [{'fsha': 'X', 'senses': [sense],
                                           'owners': [['2. agni', 'm.']]}]}
    with open(wf, 'w', encoding='utf-8') as f:
        _json.dump({'meta': {'lang': 'ru', 'root': 'zz'},
                    'results': [{'key': 'agni', 'card': card}]}, f)
    saved_repo = tm.REPO
    tm.REPO = d
    try:
        _p, added, _total = tm.build_frags(os.path.basename(wf), 'ru', out=path)
    finally:
        tm.REPO = saved_repo
    if added != 1:
        fail('an existing v1 must NOT block a v2 harvest (added=%d)' % added)
    served = tm.load_frag_tm('ru', path)
    if 'X' not in served or served['X'].get('owners') != [['2. agni', 'm.']]:
        fail('the v2 row must be live-served with its owners: %r' % served.get('X'))
    if served['X'].get('schema') != tm.FRAG_SCHEMA_V2:
        fail('served row must be v2')
    if not tm._valid_owners([sense], [['h', 'g']]) or tm._valid_owners([sense], [['h']]) \
            or tm._valid_owners([sense, sense], [['h', 'g']]):
        fail('_valid_owners count/shape validation is wrong')
    # null-owner hardening: BOTH members must be strings ('' valid, None fails). A null-owner row is
    # NOT live-served (so no warm stitch -- JS or headless -- can restore a null owner) but stays
    # audit-readable, exactly like a v1 row.
    if not tm._valid_owners([sense], [['', '']]):
        fail('empty-string owner members must be valid')
    if tm._valid_owners([sense], [[None, 'g']]) or tm._valid_owners([sense], [['h', None]]):
        fail('a null owner member ([None,g] / [h,None]) must be rejected')
    for pair in ([None, 'g'], ['h', None]):
        npath = os.path.join(d, 'nullowner.frag.ru.jsonl')
        with open(npath, 'w', encoding='utf-8') as f:
            f.write(_json.dumps({'schema': tm.FRAG_SCHEMA_V2, 'lang': 'ru', 'fsha': 'N',
                                 'senses': [sense], 'owners': [pair],
                                 'trust_level': tm.TRUST_MACHINE, 'gate_status': 'machine_gated',
                                 'reuse_policy': 'auto_exact'}) + '\n')
        if tm.load_frag_tm('ru', npath) != {}:
            fail('a null-owner row %r must NOT be live-served' % pair)
        if 'N' not in tm.load_frag_tm('ru', npath, live_only=False):
            fail('a null-owner row %r must stay audit-readable' % pair)
    print('  R6: frag-TM v2 supersedes v1; null-owner ([None,g]/[h,None]) rejected from live serve, '
          'audit-readable; owners validated')


def test_degenerate_source_identity():
    """R7: a degenerate card's (h, grammar) is the PROVEN source-record identity, not a schema
    default; an unprovable identity is REJECTED rather than emitted with a fabricated h."""
    import gen_opt_harness2 as gh
    import validate_final_card_schema as vs
    card = gh.degenerate_passthrough_card('ab~~h0_zz_pw', '=== LAYER: PW ===\n\nvgl. {#agni#}',
                                          '[]', 'russian')
    if not card or card['records'][0].get('h') != '' or card['records'][0].get('grammar') != '':
        fail('a clean single-head xref must prove h="" (no source homonym head): %r' % card)
    vs.validate_card(card)
    if gh.degenerate_passthrough_card('ab', '=== LAYER: PW ===\n\nvgl. {#agni#}',
                                      '[]', 'russian') is None:
        fail('a bare-root key with a clean stub is a provable identity -- must NOT be rejected')
    if gh._degenerate_record_identity('ab~~h1_zz_pw', 'vgl. <div n="2"> agni') is not None:
        fail('a residual homonym head must be rejected (ambiguous owning record)')
    if gh._degenerate_record_identity('ab~~h0_zz_pw', 'vgl.') != ('', ''):
        fail('a clean stub must prove ("","")')
    print('  R7: degenerate (h,grammar) is proven source identity; unprovable identity is rejected')


def test_h1283_a1_pid_alive_and_dirlock_owner():
    """A1 (H1283): pid_alive is a real liveness probe (os.kill(pid,0) is broken on win32);
    DirLock.__exit__ spares a lock that has been re-owned by another pid."""
    import coordinator as coord
    import json as _json
    import tempfile as _tf
    import shutil as _sh
    if not coord.pid_alive(os.getpid()):
        fail('A1: pid_alive(own pid) must be True')
    if coord.pid_alive(2 ** 31 - 1):
        fail('A1: pid_alive(impossible pid) must be False')
    if coord.pid_alive(0) or coord.pid_alive(None) or coord.pid_alive('nope'):
        fail('A1: pid_alive of 0/None/non-numeric must be False')
    d = _tf.mkdtemp()
    try:
        lockpath = os.path.join(d, 'L')
        with coord.DirLock(lockpath, ttl_seconds=9999, wait_seconds=1):
            with open(os.path.join(lockpath, 'owner.json'), 'w', encoding='utf-8') as f:
                _json.dump({'pid': os.getpid() + 1, 'created_at': coord.utc_now()}, f)
        if not os.path.isdir(lockpath):
            fail('A1: DirLock.__exit__ deleted a lock owned by a different pid')
    finally:
        _sh.rmtree(d, ignore_errors=True)
    print('  A1: pid_alive is a real liveness probe; DirLock spares a foreign-owned lock')


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
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'h1209', 'prep_slice.py')
    text = open(src, encoding='utf-8').read()
    if '[b[0] for b in' in text:
        fail('A6: prep_slice still takes only the first key of each batch ([b[0] for b in ...])')
    if "for b in m['batches'] for k in b" not in text:
        fail("A6: prep_slice must flatten all batch keys ([k for b in m['batches'] for k in b])")
    print('  A6: prep_slice flattens every batch key')


def main():
    tests = [
        test_restore_covers_every_promoted_field,
        test_every_stitch_emits_record_required,
        test_unmapped_token_is_counted,
        test_validator_has_a_live_caller,
        test_strip_mask_tokens_clears_notes_stranded_anchor,
        test_translation_memory_addressing,
        test_tm_pre_resolves_cards,
        test_tm_card_sane_rejects_zero_marker_drift,
        test_generated_harness_strict_key_matching,
        test_tm_auto_no_sidecar_metadata,
        test_suggest_tm_does_not_skip_agents,
        test_tm_publication_fixtures_validate,
        test_degenerate_passthrough_accounted,
        test_degenerate_passthrough_rejects_glosses,
        test_perf_preflight_small_tm_and_no_tm,
        test_perf_preflight_dense_presplit,
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
        test_cit_split_caps_single_line_monster_sense,
        test_selfheal_fragment_si_threaded_and_tags_normalized,
        test_sense_dense_card_presplit,
        test_kill_gate_wired,
        test_no_fallback_single_gets_ceil_kill_budget,
        test_presplit_cite_floor_and_single_ceil,
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
        test_no_pwg_card_source_profile_taxonomy,
        test_no_pwg_supplement_card_renders_without_pwg,
        test_h920_sense_count_top_level_ordinals,
        test_h920_sense_shortfall_gate_flags_dropped_sense,
        test_h920_no_pwg_portrait_stamps_source_senses,
        test_h920_en_missing_sense_hard_flag,
        test_h960_accept_sanloss_soft_gate,
        test_tnmask_persist_and_offline_detect,
        test_h960_dropped_sanskrit_span,
        test_no_pwg_worklist_runnable_lane,
        test_no_pwg_layer_and_profile_survive_promotion,
        test_prompt_rule_audit_template,
        test_prompt_rule_audit_missing_blocks,
        test_semantic_risk_checker,
        test_h1152_guard1_en_polyseme_checklist,
        test_braced_gloss_audit,
        test_german_residue_keeps_retained_markup,
        test_german_connective_fix,
        test_h1302_german_prose_residue_scan,
        test_h1305_ru_style_mechanical,
        test_semantic_review_prioritizer,
        test_noisy_source_type_not_requeue,
        test_report_only_risks_never_requeue,
        test_attested_text_signal_redesign,
        test_nws_fp_suppressed,
        test_en_gate_strict_has_teeth,
        test_en_gate_dup_has_teeth,
        test_ru_gate_fails_loud_on_unparseable_child,
        test_pwg_mask_latin_cue_behind_ab_tag,
        test_markup_loss_soft_flag_ru,
        test_markup_loss_soft_flag_en,
        test_en_de_residue_french_guard,
        test_h1152_guard3_xref_only_and_nws_de_locked,
        test_ru_coverage_denominator_not_silently_exempt,
        test_coverage_gate_multi_layer_and_presplit,
        test_en_residual_coverage_complete,
        test_en_split_triage_keeps_missing_input,
        test_whitney_homonym_safety,
        test_stale_refusal_preserves_requeue,
        test_fixture_audit_does_not_clobber_live_status,
        test_release_manifest_hash_validation,
        test_lang_parity_ledger_complete,
        test_lang_parity_hash_crlf_independent,
        test_frag_groups_presplit_parity,
        test_defect_fragment_denylist_round_trip,
        test_write_reports_emits_defect_fsha_file,
        test_ledger_stamps_gen_model,
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
        test_classify_run_verdicts,
        test_grammar_field_restore_behavioral,
        test_h_reconstructed_regression_guard,
        test_h1283_a1_pid_alive_and_dirlock_owner,
        test_h1283_a5_max_wide_default_bounded,
        test_h1283_a6_prep_slice_flattens_batches,
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
