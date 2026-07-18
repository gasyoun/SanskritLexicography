#!/usr/bin/env python
r"""H1209 canonical promote-DRY audit for the controller-worker slice output.

WHY: the Workflow rig's in-JS `deterministicAudit()` (wf_template.js) is deliberately
lenient — placeholder coverage is INFO-only, restoration never happens in-JS, and the
controller sees masked text. "would_promote" from the rig is therefore a SELF-report,
not a promote verdict. This script produces the AUTHORITATIVE verdict by applying the
same canonical gate battery the production harness applies at accept() time
(gen_opt_harness2.py, in accept() order) to the worker cards after canonical {Tn}
restoration via card_fields (C-01: the one restore/promote field set):

  1. TNMASK   {Tn} multiset over card_fields.TOKEN_FIDELITY_FIELDS (record.grammar +
              sense.german) vs the source skeleton — SOFT (telemetry; arming is
              TNMASK_HARD_REJECT, owner-gated).
  2. RESTORE  card_fields.restore_card_fields with {Tn} -> placeholder_map[n-1];
              an out-of-range {Tn} is kept verbatim (C-42 semantics, matches the JS
              `restore`).
  3. FIDELITY (HARD) restored `<ls`/`{#` counts summed over sense.german must equal
              the manifest's inputs[k].ls / inputs[k].sk — the accept() fidelity-reject.
  4. H1152-G2 (HARD) the identical counts over the target-language field (russian/
              english, read from the manifest) — a translation-only drop must not
              hide behind a clean source echo.
  5. SAN-LOSS (SOFT) emitted top-level sense count < inputs[k].source_senses (H920/H960;
              arming is SANLOSS_HARD_REJECT, owner-gated).
  6. SCHEMA   (HARD) validate_final_card_schema.validate_card on the restored card —
              audit_window.py's in-process final-schema gate.

Plus one H1209-specific finding class the slice surfaced: {Tn} parked in card.notes.
`notes` is NOT a restored field (card_fields: CARD_MASKED = ('iast',)) and
_pilot_collect.strip_mask_tokens strips {Tn} from notes at render time — so masked
source content moved into notes by a worker is silently DROPPED from every promoted/
rendered surface. The audit reports those tokens and whether they are duplicated in a
restorable field or genuinely lost.

Usage:
  python canonical_audit.py <slice_result.json> <manifest.json> [--out report.json]

Exit 0 always (this is a measuring instrument, not a gate); the verdict is the report.
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))          # .../src/pilot/h1209
SRC = os.path.dirname(os.path.dirname(HERE))               # .../src
sys.path.insert(0, SRC)

import card_fields                                         # C-01 single field set
import validate_final_card_schema                          # audit_window's schema gate

TOK = re.compile(r'\{T(\d+)\}')
LS = re.compile(r'<ls\b')
SK = re.compile(r'\{#')


def make_restore(pmap):
    """The JS `restore` twin: {Tn} -> pmap[n-1]; out-of-range kept verbatim (C-42)."""
    def restore_text(t):
        return TOK.sub(lambda m: pmap[int(m.group(1)) - 1]
                       if 0 <= int(m.group(1)) - 1 < len(pmap) else m.group(0), t)
    return restore_text


def tokens_of(text):
    return TOK.findall(text or '')


def card_token_multiset(card):
    """{Tn} multiset over TOKEN_FIDELITY_FIELDS — the JS cardTokens twin (C-17)."""
    toks = []
    rec_fields = [n for lvl, n in card_fields.TOKEN_FIDELITY_FIELDS if lvl == 'record']
    sense_fields = [n for lvl, n in card_fields.TOKEN_FIDELITY_FIELDS if lvl == 'sense']
    for rec in card.get('records') or []:
        for f in rec_fields:
            toks += tokens_of(rec.get(f))
        for s in rec.get('senses') or []:
            for f in sense_fields:
                toks += tokens_of(s.get(f))
    return sorted(toks, key=int)


def count_of(card, field, rx):
    """accept()'s countOf/countOfField twin: sum of rx matches over sense.<field>."""
    n = 0
    for rec in card.get('records') or []:
        for s in rec.get('senses') or []:
            n += len(rx.findall(s.get(field) or ''))
    return n


def audit_card(card_in, inp, pmap, wf_row, field):
    key = card_in['key1']
    skeleton_toks = tokens_of(inp['skeleton'])
    restore_text = make_restore(pmap)
    report = {'key1': key, 'wf_would_promote': wf_row.get('would_promote'),
              'wf_coverage': wf_row.get('coverage')}

    # --- gate 1: TNMASK multiset (pre-restore, SOFT) -------------------------------
    got = card_token_multiset(card_in)
    want = sorted(skeleton_toks, key=int)
    missing = sorted(set(want) - set(got), key=int)
    invented = sorted(set(got) - set(want), key=int)
    report['tnmask'] = {
        'match': got == want,
        'missing_from_fidelity_fields': ['{T%s}' % n for n in missing],
        'invented': ['{T%s}' % n for n in invented],
        'n_skeleton': len(want), 'n_output': len(got),
    }

    # --- H1209 finding class: {Tn} parked in card.notes (unrestorable) -------------
    notes_toks = sorted(set(tokens_of(card_in.get('notes'))), key=int)
    lost_via_notes = [n for n in notes_toks if n in missing]
    report['notes_parked'] = {
        'tokens': ['{T%s}' % n for n in notes_toks],
        'lost_content': ['{T%s}' % n for n in lost_via_notes],
        'lost_payload_preview': {
            '{T%s}' % n: (pmap[int(n) - 1][:80] if 0 <= int(n) - 1 < len(pmap) else '?')
            for n in lost_via_notes},
    }

    # --- gate 2: canonical restore -------------------------------------------------
    card = json.loads(json.dumps(card_in))                 # deep copy; card_in stays masked
    card_fields.restore_card_fields(card, field, restore_text)

    # --- gate 3: FIDELITY (HARD) on sense.german -----------------------------------
    ls_g, sk_g = count_of(card, 'german', LS), count_of(card, 'german', SK)
    fidelity_ok = (ls_g == inp['ls'] and sk_g == inp['sk'])
    report['fidelity_german'] = {'ok': fidelity_ok, 'ls': [ls_g, inp['ls']],
                                 'sk': [sk_g, inp['sk']]}

    # --- gate 4: H1152 guard 2 (HARD) on the target-language field -----------------
    ls_r, sk_r = count_of(card, field, LS), count_of(card, field, SK)
    trans_ok = (ls_r == inp['ls'] and sk_r == inp['sk'])
    report['fidelity_translation'] = {'field': field, 'ok': trans_ok,
                                      'ls': [ls_r, inp['ls']], 'sk': [sk_r, inp['sk']]}

    # --- gate 5: SAN-LOSS (SOFT) ----------------------------------------------------
    emitted = sum(len(rec.get('senses') or []) for rec in card.get('records') or [])
    exp = inp.get('source_senses') or 0
    report['sanloss'] = {'emitted': emitted, 'source_senses': exp,
                         'shortfall': (emitted < exp) if exp > 0 else False}

    # --- gate 6: SCHEMA (HARD) on the restored card --------------------------------
    try:
        validate_final_card_schema.validate_card(card)
        report['schema'] = {'ok': True}
    except Exception as e:                                 # validator raises ValueError; be
        report['schema'] = {'ok': False, 'error': str(e)}  # robust to any other raise too

    # --- verdict -------------------------------------------------------------------
    hard_fail = []
    if not fidelity_ok:
        hard_fail.append('fidelity-reject: <ls> %d/%d, {# %d/%d'
                         % (ls_g, inp['ls'], sk_g, inp['sk']))
    if not trans_ok:
        hard_fail.append('translation-fidelity-reject: <ls> %d/%d, {# %d/%d'
                         % (ls_r, inp['ls'], sk_r, inp['sk']))
    if not report['schema']['ok']:
        hard_fail.append('schema-reject: ' + report['schema']['error'])
    report['hard_fail'] = hard_fail
    report['soft_flags'] = ([] if report['tnmask']['match'] else ['tnmask-mismatch']) \
        + (['sanloss-shortfall'] if report['sanloss']['shortfall'] else []) \
        + (['content-lost-via-notes'] if lost_via_notes else [])
    report['promote_dry'] = not hard_fail
    report['restored_card'] = card
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slice_result')
    ap.add_argument('manifest')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    res = json.load(open(a.slice_result, encoding='utf-8'))
    man = json.load(open(a.manifest, encoding='utf-8'))
    field = man.get('field') or 'russian'                  # EN manifests carry 'english'
    wf_rows = {r['key1']: r for r in res['results']}

    reports = []
    for entry in res['cards_out']:
        key = entry['key1']
        reports.append(audit_card(entry['card'], man['inputs'][key],
                                  man['placeholder_maps'][key], wf_rows.get(key, {}),
                                  field))

    n_pass = sum(1 for r in reports if r['promote_dry'])
    print('=== H1209 canonical promote-DRY audit (authoritative) ===')
    print('%-10s %-6s %-8s %-14s %-14s %-8s %s'
          % ('card', 'wf', 'canon', 'german ls/sk', field + ' ls/sk', 'schema', 'flags'))
    for r in reports:
        fg, fr = r['fidelity_german'], r['fidelity_translation']
        print('%-10s %-6s %-8s %-14s %-14s %-8s %s' % (
            r['key1'],
            'DRY+' if r['wf_would_promote'] else 'DRY-',
            'PASS' if r['promote_dry'] else 'REJECT',
            '%d/%d %d/%d' % (fg['ls'][0], fg['ls'][1], fg['sk'][0], fg['sk'][1]),
            '%d/%d %d/%d' % (fr['ls'][0], fr['ls'][1], fr['sk'][0], fr['sk'][1]),
            'ok' if r['schema']['ok'] else 'FAIL',
            ','.join(r['soft_flags']) or '-'))
        for hf in r['hard_fail']:
            print('           ! %s' % hf)
        lost = r['notes_parked']['lost_content']
        if lost:
            print('           ~ content lost via notes (unrestorable field): %s'
                  % ' '.join(lost))
    print('canonical promote-DRY: %d/%d PASS (workflow self-report was %d/%d)'
          % (n_pass, len(reports),
             sum(1 for r in reports if r['wf_would_promote']), len(reports)))

    if a.out:
        with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'schema': 'h1209.canonical_audit.v1', 'reports': reports},
                      f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('wrote', a.out)


if __name__ == '__main__':
    main()
