#!/usr/bin/env python
r"""H2226 OPT-4 selftest: H1209/H1210 JS templates take field + controller prompt from payload.

Proves without a live Workflow run:
  1. The three JS surfaces no longer hardcode German->Russian / s.russian access paths
     outside of payload-driven TARGET_FIELD / CONTROLLER_PROMPT.
  2. prep_slice + build_args + inject_payload builds a RU script under the Workflow cap
     with field=russian and a Russian controller prompt.
  3. The same pipeline with field=english builds (no second scaffold tree) and injects
     an English controller prompt + field=english.

Usage:
  python src/pilot/h1209/js_field_param_selftest.py
"""
import json
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.dirname(HERE)
H1210 = os.path.join(PILOT, 'h1210')
RT = os.path.dirname(PILOT)
MANIFEST = os.path.join(PILOT, 'h1209_slice3.manifest.json')

FAILS = []


def check(name, cond, detail=''):
    print(('  ok   ' if cond else '  FAIL ') + name + ((' — ' + detail) if detail and not cond else ''))
    if not cond:
        FAILS.append(name)


def load_mod(name, path):
    import importlib.util as ilu
    spec = ilu.spec_from_file_location(name, path)
    mod = ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_templates_parameterized():
    surfaces = [
        os.path.join(HERE, 'wf_template.js'),
        os.path.join(H1210, 'wf_template_ab.js'),
        os.path.join(H1210, 'control_template.js'),
    ]
    for path in surfaces:
        text = open(path, encoding='utf-8').read()
        base = os.path.basename(path)
        check('%s reads PAYLOAD.field' % base, 'PAYLOAD.field' in text)
        check('%s has TARGET_FIELD' % base, 'const TARGET_FIELD' in text)
        check('%s has CONTROLLER_PROMPT' % base, 'CONTROLLER_PROMPT' in text)
        # No remaining hardcoded controller language pair outside the default helper.
        # The default helper is allowed to mention German->Russian as the russian branch.
        hard_ctrl = re.findall(
            r"QUALITY CONTROLLER for a PWG German->Russian", text)
        # Exactly one default path may still contain the RU string (defaultControllerPrompt).
        check('%s does not hardcode controller pair outside default helper'
              % base, len(hard_ctrl) <= 1, 'count=%d' % len(hard_ctrl))
        if base != 'control_template.js':
            # Gate must use TARGET_FIELD bracket access, not s.russian literals in active code.
            # Comments may still say "russian"; ban the active access form.
            check('%s gate uses s[TARGET_FIELD] not s.russian'
                  % base, 's[TARGET_FIELD]' in text and "s.russian" not in text)


def test_prep_inject_ru_and_en():
    if not os.path.isfile(MANIFEST):
        check('h1209_slice3.manifest.json present', False)
        return
    prep = load_mod('prep_slice_h2226', os.path.join(HERE, 'prep_slice.py'))
    inject = load_mod('inject_h2226', os.path.join(HERE, 'inject_payload.py'))
    build = load_mod('build_args_h2226', os.path.join(HERE, 'build_args.py'))

    man = json.load(open(MANIFEST, encoding='utf-8'))
    # Keep the RU canary small: first 3 keys only (matches the historical 3-card slice).
    keys = [k for b in man['batches'] for k in b][:3]
    check('manifest has >=3 keys for RU canary rebuild', len(keys) >= 3, 'n=%d' % len(keys))

    tmp = tempfile.mkdtemp(prefix='h2226_js_field_')
    for field, want_pair in (('russian', 'German->Russian'),
                             ('english', 'German->English')):
        m = dict(man)
        m['field'] = field
        # EN schema: rename sense.russian -> english in output_schema if present so
        # build_args can still derive a worker_schema. For inject we only need field +
        # controller_prompt; schema rename is best-effort.
        if field == 'english' and 'output_schema' in m:
            blob = json.dumps(m['output_schema'])
            if '"russian"' in blob and '"english"' not in blob.replace('english', ''):
                m['output_schema'] = json.loads(
                    blob.replace('"russian"', '"english"'))
        pl_path = os.path.join(tmp, 'payload_%s.json' % field)
        prep.write_payloads(m, pl_path, keys=keys, manifest_name=os.path.basename(MANIFEST))
        pl = json.load(open(pl_path, encoding='utf-8'))
        check('%s payload.field' % field, pl.get('field') == field)
        check('%s controller_prompt carries pair' % field,
              want_pair in (pl.get('controller_prompt') or ''))
        check('%s controller_prompt has {key1}' % field,
              '{key1}' in (pl.get('controller_prompt') or ''))

        args_path = os.path.join(tmp, 'args_%s.json' % field)
        # build_args needs output_schema — use the (possibly rewritten) man.
        man_path = os.path.join(tmp, 'man_%s.json' % field)
        with open(man_path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(m, f, ensure_ascii=False)
        # Inline the two transforms build_args.main does (avoid argv).
        payload = json.load(open(pl_path, encoding='utf-8'))
        for c in payload['cards']:
            c.pop('placeholder_map', None)
        defs = m['output_schema']['$defs']
        payload['worker_schema'] = {
            'type': 'object', 'additionalProperties': False,
            'required': ['card', 'self_report'],
            'properties': {'card': {'$ref': '#/$defs/card'},
                           'self_report': build.SELF_REPORT},
            '$defs': defs,
        }
        with open(args_path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(payload, f, ensure_ascii=False)

        out_js = os.path.join(tmp, 'wf_%s.js' % field)
        inject.inject(os.path.join(HERE, 'wf_template.js'), args_path, out_js)
        emitted = open(out_js, encoding='utf-8').read()
        check('%s inject under WORKFLOW_SCRIPT_CAP' % field,
              len(emitted.encode('utf-8')) <= inject.WORKFLOW_SCRIPT_CAP)
        # Payload is embedded as a JSON literal; field must appear in the script body.
        check('%s injected script carries field=%s' % (field, field),
              '"field": "%s"' % field in emitted or '"field":"%s"' % field in emitted)
        check('%s injected script carries %s controller pair' % (field, want_pair),
              want_pair in emitted)
        # EN must not leave a Russian-only controller hardcode as the sole path.
        if field == 'english':
            check('EN inject uses English label in controller_prompt',
                  'the English faithfully' in emitted)

    # Also inject h1210 arm-A template once (RU) to prove marker/compat.
    args_ru = os.path.join(tmp, 'args_russian.json')
    out_ab = os.path.join(tmp, 'wf_ab_ru.js')
    inject.inject(os.path.join(H1210, 'wf_template_ab.js'), args_ru, out_ab)
    check('h1210 wf_template_ab injects', os.path.isfile(out_ab) and os.path.getsize(out_ab) > 1000)

    # control_template: synthetic payload with english field.
    ctrl_payload = {
        'schema': 'h1210.control.v1', 'arm': 'B_test', 'round': 1,
        'field': 'english',
        'controller_prompt': prep.controller_prompt_for_field('english'),
        'cards': [{'key1': 'k1', 'senses': [{'tag': '1', 'german': 'g', 'english': 'e'}]}],
    }
    ctrl_args = os.path.join(tmp, 'ctrl_en.json')
    with open(ctrl_args, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(ctrl_payload, f, ensure_ascii=False)
    # control_template uses the same marker; inject_payload works on any template with it.
    out_ctrl = os.path.join(tmp, 'ctrl_en.js')
    inject.inject(os.path.join(H1210, 'control_template.js'), ctrl_args, out_ctrl)
    ctrl_js = open(out_ctrl, encoding='utf-8').read()
    check('control_template EN inject carries German->English',
          'German->English' in ctrl_js)


def test_canonical_audit_ru_fixture():
    """Existing RU 3-card canary result still audits clean (promote-DRY instrument)."""
    report_path = os.path.join(HERE, 'canonical_audit2.report.json')
    result_path = os.path.join(HERE, 'slice_result2.json')
    if not (os.path.isfile(report_path) and os.path.isfile(result_path) and os.path.isfile(MANIFEST)):
        check('RU canary fixtures present', False)
        return
    # Re-run canonical_audit against committed fixtures.
    audit = load_mod('canonical_audit_h2226', os.path.join(HERE, 'canonical_audit.py'))
    # Use the module's CLI entry if present; otherwise call audit_card loop.
    # Prefer subprocess-free: replicate main path.
    man = json.load(open(MANIFEST, encoding='utf-8'))
    sr = json.load(open(result_path, encoding='utf-8'))
    field = man.get('field') or 'russian'
    check('RU canary slice has 3 results', len(sr.get('results') or []) == 3)
    statuses = [r.get('final_status') for r in sr['results']]
    check('RU canary all clean statuses',
          all(s in ('clean-no-review', 'clean-controller-approved') for s in statuses),
          'statuses=%r' % statuses)
    # Authoritative audit on each card_out.
    cards_out = {c['key1']: c['card'] for c in sr.get('cards_out') or []}
    rows = {r['key1']: r for r in sr['results']}
    ok_all = True
    for k, card in cards_out.items():
        if k not in man.get('inputs', {}):
            continue
        inp = man['inputs'][k]
        pmap = man['placeholder_maps'][k]
        rep = audit.audit_card(card, inp, pmap, rows[k], field)
        # fidelity_translation / fidelity_german should be ok for a green canary.
        ft = rep.get('fidelity_translation') or {}
        fg = rep.get('fidelity_german') or {}
        if ft.get('ok') is False or fg.get('ok') is False:
            ok_all = False
            print('    card %s: fidelity_german=%s fidelity_translation=%s'
                  % (k, fg.get('ok'), ft.get('ok')))
    check('canonical_audit RU fixture fidelity ok', ok_all)


def main():
    print('H2226 js_field_param_selftest')
    test_templates_parameterized()
    test_prep_inject_ru_and_en()
    test_canonical_audit_ru_fixture()
    print('js_field_param_selftest: %d check(s) failed' % len(FAILS))
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
