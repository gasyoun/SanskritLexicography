#!/usr/bin/env python
"""audit_translation.py — deterministic, judge-independent fidelity gate for translated cards.

Complements run_real_test.py (the Opus judge) and nws_split.py (owner-map parse) with a cheap
format-invariant check that scales to the full freq run (you cannot eyeball 142k units). For
every <stem>.merged.md vs its <stem>.raw.txt source it checks the HARD invariants:

  LS   every <ls>…</ls> literary-source citation is preserved (output keeps >=90% — the source
       sigla are demonstrable usage and must survive verbatim).
  SAN  every {#…#} Sanskrit span is preserved (>=85% of the distinct spans).
  RU   the output actually contains Russian (Cyrillic) when the source had {%…%} gloss prose
       to translate (else the card is empty / untranslated).

Reports per-unit s/o counts and flags; exits non-zero if any unit fails (CI-usable).

  python audit_translation.py [manifest.json]   # default: scale_manifest.freqtest.json
  python audit_translation.py --wf wf_output.json
"""
import json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, 'pilot', 'input')
OUT = os.path.join(HERE, 'pilot', 'output')

LS = re.compile(r'<ls\b')
SAN = re.compile(r'\{#.*?#\}')
GER = re.compile(r'\{%.*?%\}')
CYR = re.compile(r'[а-яёА-ЯЁ]')

LS_KEEP, SAN_KEEP = 0.90, 0.85


def body(t):
    return t.split('===\n\n', 1)[1] if '===\n\n' in t else t


def audit_unit(stem):
    rawp, outp = os.path.join(IN, stem + '.raw.txt'), os.path.join(OUT, stem + '.merged.md')
    if not os.path.exists(rawp):
        return stem, None, ['NO-RAW']
    if not os.path.exists(outp):
        return stem, None, ['NO-OUTPUT']
    rb = body(open(rawp, encoding='utf-8').read())
    out = open(outp, encoding='utf-8').read()
    sls, ols = len(LS.findall(rb)), len(LS.findall(out))
    ssan, osan = len(set(SAN.findall(rb))), len(set(SAN.findall(out)))
    cyr = bool(CYR.search(out))
    # absolute-difference guard: losing a single <ls>/{#} span on a tiny card (where the model
    # collapsed a compound or merged a duplicate) is below the ratio but not a real apparatus
    # loss — require >=2 absolute missing too. The giant-head citation dump (e.g. 7/125) still
    # trips it; a 3/4 tiny card no longer false-flags.
    flags = []
    if sls > 0 and ols < sls * LS_KEEP and (sls - ols) >= 2:
        flags.append('LS-LOSS(%d/%d)' % (ols, sls))
    if ssan > 0 and osan < ssan * SAN_KEEP and (ssan - osan) >= 2:
        flags.append('SAN-LOSS(%d/%d)' % (osan, ssan))
    if GER.search(rb) and not cyr:
        flags.append('NO-RUSSIAN')
    return stem, (sls, ols, ssan, osan, cyr), flags


def find_results(o):
    if isinstance(o, dict):
        if isinstance(o.get('results'), list):
            return o['results']
        for v in o.values():
            r = find_results(v)
            if r is not None:
                return r
    if isinstance(o, list):
        for v in o:
            r = find_results(v)
            if r is not None:
                return r
    return None


def stems_from_wf(path):
    results = find_results(json.load(open(path, encoding='utf-8'))) or []
    return [r.get('key') for r in results if r.get('key')]


def stems_from_manifest(path):
    return [e['key1'] for e in json.load(open(path, encoding='utf-8'))]


def main():
    args = sys.argv[1:]
    if args[:1] == ['--wf']:
        if len(args) < 2:
            sys.exit('usage: python audit_translation.py --wf <wf_output.json>')
        stems = stems_from_wf(args[1])
    else:
        mpath = args[0] if args else os.path.join(OUT, 'scale_manifest.freqtest.json')
        stems = stems_from_manifest(mpath)
    print('=== translation fidelity audit (%d units) ===' % len(stems))
    print('%-24s %-10s %-10s %-5s %s' % ('unit', 'ls s/o', 'san s/o', 'ru', 'flags'))
    fails = []
    for s in stems:
        stem, nums, flags = audit_unit(s)
        if nums is None:
            print('%-24s %s' % (stem[:24], ' '.join(flags)))
            fails.append(stem)
            continue
        sls, ols, ssan, osan, cyr = nums
        print('%-24s %-10s %-10s %-5s %s' % (
            stem[:24], '%d/%d' % (sls, ols), '%d/%d' % (ssan, osan),
            'Y' if cyr else 'n', ' '.join(flags) if flags else 'ok'))
        if flags:
            fails.append(stem)
    print('\n%s: %d/%d units clean%s'
          % ('PASS' if not fails else 'FAIL', len(stems) - len(fails), len(stems),
             '' if not fails else ' | flagged: ' + ', '.join(fails)))
    # Machine-readable verdict line — the parent audit_window.py parses THIS strictly rather
    # than scraping the prose summary above, so a future wording tweak here can never silently
    # drop flagged cards from the requeue (H169 defect 2).
    print('FLAGGED_JSON: %s' % json.dumps(fails))
    sys.exit(0 if not fails else 1)


if __name__ == '__main__':
    main()
