#!/usr/bin/env python
r"""softguard_falseflag_measure.py -- H1150 W1-B: offline false-flag rate for the
SANLOSS_* / TNMASK_* soft guards, against frozen evidence, driving the REAL accept()
extracted verbatim out of a generated harness (the accept_sensecount_test.js technique --
Uprava FINDINGS Section 82 names hand-copying the guard as the anti-pattern this avoids).

Both guards are TELEMETRY-ONLY today (`SANLOSS_HARD_REJECT = false`,
`TNMASK_HARD_REJECT = false` in gen_opt_harness2.py) -- this script MEASURES, it never
arms. It does not import or touch either const.

Evidence sources (Ruling: frozen, not live -- D-3 blocks live traffic):
  1. pwg_ru/h963/campaign_cards.jsonl, SHA-pinned via artifact_manifest.sha256 (verified
     first -- see verify_manifest()). Empirically near-empty: 1 synthetic canary (zero
     <ls>, zero {#, by construction -- cannot exercise either soft guard) + 2 null
     kill-timeout real cards (no output, unmeasurable). Reported, not silently dropped.
  2. The promoted store (src/pwg_ru_translated.jsonl, resolved via store_path.canonical_
     store -- the SAME resolver cohort_clean_rates.py / promote_final_cards.py use, so a
     worktree run reads the persistent MAIN-checkout store, never a vanishing local one).
     11603 rows / 2489 cards (grouped by `subcard`). This is the actual "second source"
     the handoff names -- the h963 campaign alone has no usable real-card evidence.

SANLOSS methodology: for each promoted card (subcard group), concatenate its senses'
`de` (German source, already restored) fields in store order, and recompute
`count_source_senses` -- the REAL, IMPORTED (not hand-copied) H960-hardened production
function from sense_count.py -- to get `exp`. `emitted` = number of stored senses. Feed
`(ls, sk, exp, senses)` into a harness-generated, verbatim-extracted `accept()` (Node) to
get the REAL SANLOSS_SHORTFALLS/fidelity-gate verdict -- not a hand-rolled comparison.

Denominator discipline: only cards whose reconstructed `raw` echo re-passes the harness's
own <ls>/{# fidelity gate are counted (accept() returns non-null) -- a card that would be
rejected there never reaches the SANLOSS counter in production either.

Ground-truth limit (stated plainly, repeated in the memo): this reconstruction is BLIND to
a genuine historical drop -- a truly dropped sense's text is, by definition, absent from
the promoted store, so it can never inflate the recomputed `exp` above what's visible. Any
flag this method finds can therefore ONLY arise from either (a) the source's own numbering
declaring more distinct top-level ordinals than the pipeline chose to split into separate
stored senses (a genuine false-flag mechanism -- see the per-flag classification below), or
(b) a reconstruction-boundary artifact of concatenating per-sense store rows in place of the
true undivided original raw text (checked per-case; see classification rationale). It CANNOT
independently prove the guard would never false-flag on a genuine drop's complement, nor can
it recover the historical false/true-positive status of any sense actually missing from the
store today -- those are outside what frozen, already-promoted evidence can answer.

TNMASK methodology: TNMASK's real accept() check runs BEFORE restoreCard, comparing the
PRE-restore candidate's {Tn} multiset to the masked source skeleton's. The promoted store
holds only POST-restore text -- the pre-restore candidate + masked skeleton pairing is not
preserved anywhere for any real (non-synthetic) historical card. A repo-wide grep (this
session) found zero non-zero tnmask_mismatches/sanloss_shortfalls readings anywhere except
h963's own campaign_windows.jsonl (which reads 0/0, on the near-empty campaign above), and
zero residual literal `{T\d+}` tokens survive in any of the 11603 promoted rows (an
independent corroboration of the H1110 C-42 finding: canonical-store raw {Tn} rows = 0).
There is therefore NO usable frozen evidence to compute a TNMASK false-flag rate from; this
script reports that fact rather than fabricating a rate from a sample of ~0.

Usage:
    python src/pilot/softguard_falseflag_measure.py --out ../pwg_ru/h1112/softguard_falseflag_rate.json

No paid calls, no LLM generation, no store mutation. Reads the promoted store; writes only
the output JSON (and a temp dir for the harness/case files, cleaned up on exit).
"""
import argparse
import collections
import hashlib
import json
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))          # .../RussianTranslation/src/pilot
SRC = os.path.dirname(HERE)                                 # .../RussianTranslation/src
RT = os.path.dirname(SRC)                                   # .../RussianTranslation

if SRC not in sys.path:
    sys.path.insert(0, SRC)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from store_path import canonical_store                      # noqa: E402  -- shared resolver
from sense_count import count_source_senses                 # noqa: E402  -- REAL, imported

H963 = os.path.join(RT, 'pwg_ru', 'h963')
MANIFEST = os.path.join(H963, 'artifact_manifest.sha256')


# ---------------------------------------------------------------------------------------
# Step 1: verify the h963 SHA manifest FIRST. Windows checkouts land these files CRLF
# (core.autocrlf=true) while the manifest was cut against the LF blob git stores -- so a
# byte-for-byte read of the working tree spuriously mismatches every text file. We hash
# git's own blob content (`git show HEAD:<path>`), which is what was actually committed
# and is immune to the local checkout's line-ending translation, exactly as sha256sum -c
# would if run on a checkout with core.autocrlf=false/input.
# ---------------------------------------------------------------------------------------
def verify_manifest():
    lines = []
    with open(MANIFEST, 'r', encoding='utf-8') as f:
        for raw in f:
            raw = raw.rstrip('\r\n')
            if raw.strip():
                lines.append(raw)
    results = {'ok': [], 'missing_gitignored': [], 'mismatch': [], 'malformed': []}
    for line in lines:
        parts = line.split(None, 1)
        if len(parts) != 2:
            results['malformed'].append(line)
            continue
        expected, relpath = parts
        relpath = relpath.strip()
        repo_root = os.path.dirname(RT)  # SanskritLexicography checkout root
        full = os.path.join(repo_root, relpath)
        if not os.path.isfile(full):
            # Known class: src/pilot/output/h963_c4_* -- gitignored campaign scratch,
            # documented ABSENT-by-design in H963_OFFLINE_LAUNCH_READINESS_REPORT (the
            # `src/pilot/output/` row: "ABSENT -- live plan/lease state"). Not evidence
            # this measurement consumes (see module docstring): only the three committed
            # pwg_ru/h963/*.jsonl rows feed the measurement below.
            results['missing_gitignored'].append(relpath)
            continue
        blob = subprocess.run(['git', '-C', repo_root, 'show', 'HEAD:' + relpath],
                               capture_output=True).stdout
        actual = hashlib.sha256(blob).hexdigest()
        if actual == expected:
            results['ok'].append(relpath)
        else:
            results['mismatch'].append({'path': relpath, 'expected': expected, 'actual': actual})
    return results


# ---------------------------------------------------------------------------------------
# Step 2: SANLOSS -- group the promoted store by card, recompute exp via the real,
# imported count_source_senses, and run the REAL harness-extracted accept() over each
# eligible card via Node.
# ---------------------------------------------------------------------------------------
def load_store_cards(store_path):
    cards = collections.OrderedDict()
    with open(store_path, encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            cards.setdefault(row.get('subcard'), []).append(row)
    return cards


def build_eligible_cases(cards):
    """Cards with a positive deterministic source-sense count -- accept()'s own
    `if (exp > 0)` gate; exp<=0 (cross-reference-only / unnumbered supplement) is skipped
    by the real guard and never eligible to flag."""
    cases = []
    skipped_exp0 = 0
    for subcard, rows in cards.items():
        concat_de = '\n'.join(r.get('de') or '' for r in rows)
        exp = count_source_senses(concat_de)
        if exp <= 0:
            skipped_exp0 += 1
            continue
        cases.append({
            'key': subcard,
            'ls': concat_de.count('<ls'),
            'sk': concat_de.count('{#'),
            'source_senses': exp,
            'senses': [{'german': r.get('de') or '', 'russian': r.get('ru') or ''} for r in rows],
            'emitted': len(rows),
        })
    return cases, skipped_exp0


def generate_dummy_harness(tmpdir):
    """A real gen_opt_harness2.build() harness (no LLM call, offline) -- mirrors
    window_selftest.py's test_h960_accept_sanloss_soft_gate harness-build pattern. Its
    INPUTS are throwaway; only the emitted accept()/countOf/countOfField/tokensOf/
    cardTokens FUNCTION CODE is used downstream (extracted verbatim by the .js runner)."""
    import gen_opt_harness2 as gh
    raw = '=== LAYER: PW ===\n\n{#dummy#}\xa6\n— 1〉 {%a%}.\n— 2〉 {%b%}.'
    rp = os.path.join(tmpdir, 'dummy~~h0_zz_pw.raw.txt')
    pp = os.path.join(tmpdir, 'dummy~~h0_zz_pw.portrait.json')
    with open(rp, 'w', encoding='utf-8') as f:
        f.write(raw)
    with open(pp, 'w', encoding='utf-8') as f:
        f.write('[]')
    gh.input_paths = lambda k, input_dir=None: (rp, pp)
    gh.KILL = False
    js, _ = gh.build('zz_dummy', ['dummy~~h0_zz_pw'], None, 12000,
                      nominal=True, grammar_on=False, lang='ru', tm_path=None)
    out = os.path.join(tmpdir, 'dummy_harness.js')
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    return out


def run_real_accept(harness_path, cases, tmpdir):
    cases_path = os.path.join(tmpdir, 'cases.json')
    out_path = os.path.join(tmpdir, 'results.json')
    with open(cases_path, 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False)
    runner = os.path.join(HERE, 'softguard_falseflag_accept_run.js')
    p = subprocess.run(['node', runner, harness_path, cases_path, out_path],
                        capture_output=True, text=True, encoding='utf-8', timeout=120)
    if p.returncode:
        raise RuntimeError('softguard_falseflag_accept_run.js failed:\n%s\n%s' % (p.stdout, p.stderr))
    with open(out_path, encoding='utf-8') as f:
        return json.load(f)


# ---------------------------------------------------------------------------------------
# Manual classification of the SANLOSS flags found in the frozen 2026-07-18 evidence.
# EVERY flagged key was hand-inspected against its own stored `de`/`ru` text (both
# fields, not just the German echo) before this table was written -- see the H1150 memo
# for the full excerpts. All 8 are Nachtrag/corrigenda cards: ONE stored/translated
# sense bundles textual-correction points across MULTIPLE distinct sub-lemma blocks
# (each opened by its own "-- {#XX#}" marker), and every "extra" ordinal
# count_source_senses finds is verbatim present, complete and translated, inside that
# same stored row -- nothing is missing. This is a genuine false-flag mechanism distinct
# from the already-hardened H960 mid-prose cross-reference class (gam~~h2_31_pari,
# s_ud~~h0_05_pra, _a_srayatva -- verified NOT flagged by the current counter, confirming
# the H960 fix still holds): here the "extra" ordinals are each legitimately
# line-opening in their OWN sub-block, so H960's is-line-opening hardening correctly
# keeps them -- the counter has no way to know the sub-blocks are different headwords'
# corrections bundled by the pipeline into one stored unit, not one card's own numbered
# senses. If a NEW flagged key ever appears on a future run, this dict has no entry for
# it and the report writer below fails loud rather than silently guessing.
# ---------------------------------------------------------------------------------------
SANLOSS_CLASSIFICATION = {
    'car~~h1_20_vi': ('false_flag',
        'vi_main bundles source ordinals 4) and 6) into one stored sense (both content-complete '
        'in de/ru); count_source_senses correctly finds 5 distinct line-opening ordinals '
        '{1,3,4,6,11} across the 4 stored senses, but two of them (4,6) were bundled by the '
        'pipeline into vi_main rather than split. Nothing is missing from de/ru.'),
    'd_a~~h10_00_pwg00': ('false_flag',
        'The single stored sense (tag "3") bundles a Nachtrag correction under {#ava#} sense 1) '
        'and another under {#vi#} sense 3) -- two different compound-verb sub-lemmas\' corrections '
        'in one stored unit. Both point 1) and point 3) content are verbatim present in de/ru.'),
    'd_a~~h13_00_pwg00': ('false_flag',
        'The single stored sense (tag "1") bundles corrections across {#dA#} (points 1, 2), '
        '{#aByA#} (point 1), {#upA#} and {#vyA#} (unnumbered prose) -- one stored unit spanning '
        'four sub-lemmas. All numbered content is verbatim present in de/ru.'),
    'iz~~h14_00_pwg00': ('false_flag',
        'The single stored sense (tag "I.3") bundles a correction under the base entry (point 2) '
        'and another under {#prati#} (point 1). Both are verbatim present in de/ru; the guard '
        'counts 2 distinct ordinals from what the pipeline stored as one unit.'),
    'n_i~~h5_10_pari': ('false_flag',
        'sense_tag "3-corr-8" is itself a single stored unit bundling ordinals 3) and 8) '
        '("3) read as 8) ...", a corrigenda directive) -- both present verbatim. Combined with '
        'tags "2" and "4-corr", 4 distinct ordinals are found across 3 stored senses.'),
    'n_i~~h5_11_pra': ('false_flag',
        'The single stored sense ("root-subcard-pra") bundles points 2) and 6) of the {#pra#} '
        'sub-lemma\'s corrigenda into one stored unit. Both present verbatim in de/ru.'),
    'vas~~h13_00_pwg00': ('false_flag',
        'The single stored sense (tag "5") bundles corrections across {#vas#} itself (point 1), '
        '{#aDi#} (point 2), {#ni#} (point 1, a numeric duplicate), and {#vi#} (point 2, '
        'duplicate) -- one stored unit, four sub-lemma corrections. All present verbatim.'),
    'y_a~~h5_00_pwg00': ('false_flag',
        'The single stored sense (tag "1") bundles FOUR sub-lemmas\' corrections -- {#yA#} '
        'itself (point 10), {#samA#} (point 3), {#nis#} (point 1), {#vi#} (point 2) -- into one '
        'stored unit. This is the most extreme bundling case found; all four points\' content is '
        'verbatim present and translated in de/ru. Nothing is missing.'),
}


def classify_sanloss(flagged_results):
    examples = []
    true_drop = false_flag = 0
    for r in flagged_results:
        key = r['key']
        if key not in SANLOSS_CLASSIFICATION:
            raise RuntimeError(
                'SANLOSS flag on %r has no manual classification on record -- inspect its de/ru '
                'text and add a SANLOSS_CLASSIFICATION entry before trusting this report (never '
                'guess a verdict programmatically).' % key)
        verdict, rationale = SANLOSS_CLASSIFICATION[key]
        if verdict == 'true_drop':
            true_drop += 1
        else:
            false_flag += 1
        detail = r['sanloss_detail'][0] if r['sanloss_detail'] else {}
        examples.append({
            'key': key, 'verdict': verdict, 'rationale': rationale,
            'expected': detail.get('expected'), 'emitted': detail.get('emitted'),
            'dropped': detail.get('dropped'),
        })
    return examples, true_drop, false_flag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(RT, 'pwg_ru', 'h1112', 'softguard_falseflag_rate.json'))
    args = ap.parse_args()

    print('=== Step 1: verify h963 artifact_manifest.sha256 ===')
    manifest = verify_manifest()
    print('  git-blob-verified OK:', len(manifest['ok']))
    print('  missing (gitignored scratch, not consumed by this measurement):', len(manifest['missing_gitignored']))
    print('  MISMATCH:', len(manifest['mismatch']))
    if manifest['mismatch']:
        print('FATAL: hash mismatch against committed evidence -- STOPPING per the handoff rail.')
        for m in manifest['mismatch']:
            print('  ', m)
        sys.exit(1)
    if manifest['malformed']:
        print('FATAL: malformed manifest line(s):', manifest['malformed'])
        sys.exit(1)

    store_path = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))
    print('\n=== Step 2: load promoted store ===')
    print('  store:', store_path)
    cards = load_store_cards(store_path)
    total_rows = sum(len(v) for v in cards.values())
    print('  rows:', total_rows, '| cards:', len(cards))

    print('\n=== Step 3: SANLOSS -- recompute exp via the real count_source_senses ===')
    cases, skipped_exp0 = build_eligible_cases(cards)
    print('  cards with exp>0 (eligible):', len(cases), '| skipped (exp<=0):', skipped_exp0)

    with tempfile.TemporaryDirectory() as tmpdir:
        harness = generate_dummy_harness(tmpdir)
        print('  generated harness:', harness)
        results = run_real_accept(harness, cases, tmpdir)

    n_rejected_fidelity = sum(1 for r in results if not r['accepted'])
    survived = [r for r in results if r['accepted']]
    flagged = [r for r in survived if r['sanloss_shortfalls'] > 0]
    tnmask_hits = [r for r in survived if r['tnmask_mismatches'] > 0]
    print('  rejected by ls/sk fidelity gate (excluded from denominator):', n_rejected_fidelity)
    print('  SANLOSS-eligible denominator (survived fidelity):', len(survived))
    print('  SANLOSS flagged:', len(flagged))
    print('  TNMASK hits in this pass (expected 0 -- see module docstring, no-op by construction):',
          len(tnmask_hits))

    examples, true_drop, false_flag = classify_sanloss(flagged)
    assert true_drop + false_flag == len(flagged)

    sanloss = {
        'denominator': len(survived),
        'denominator_note': (
            'cards from the promoted store with a deterministic source_senses > 0 (accept()\'s '
            'own exp>0 gate) whose reconstructed raw (concatenated stored-sense `de` text) '
            're-passes the real <ls>/{# fidelity gate under this reconstruction (%d of %d '
            'eligible cards rejected there and excluded -- see the memo\'s reconstruction-'
            'boundary caveat).' % (n_rejected_fidelity, len(cases))
        ),
        'flagged': len(flagged),
        'true_drop': true_drop,
        'false_flag': false_flag,
        'flag_incidence_rate': round(len(flagged) / len(survived), 4) if survived else None,
        'false_flag_rate_of_flags': round(false_flag / len(flagged), 4) if flagged else None,
        'examples': examples,
        'mechanism': (
            'Nachtrag/corrigenda cards where the pipeline stores textual-correction points from '
            'MULTIPLE distinct sub-lemma blocks (each opened by its own "-- {#XX#}" marker) as '
            'ONE translated sense. count_source_senses correctly finds each sub-block\'s own '
            'line-opening ordinal (by design -- H960 hardening only excludes MID-PROSE cross-'
            'references, not legitimately line-opening ordinals in a different sub-block), so the '
            'distinct-ordinal count exceeds the stored sense count even though no content is '
            'missing.'
        ),
        'recommendation': 'FIX_COUNTER_FIRST',
        'fix_suggestion': (
            'Partition count_source_senses\' ordinal search by "-- {#headword#}" sub-lemma '
            'boundary (the same marker restoreCard/promote already key subcards on) before '
            'stamping source_senses for a card, or -- cheaper -- have accept() additionally check '
            'whether every "extra" ordinal\'s content is verbatim present somewhere in the '
            'emitted card before counting it as a shortfall. Either closes the observed class '
            'without weakening H960\'s existing cross-reference hardening.'
        ),
    }

    tnmask = {
        'denominator': 1,
        'denominator_note': (
            'The ONLY frozen (source, pre-restore-emitted) evidence available for TNMASK is '
            'H994\'s dq_canary_puregloss synthetic control inside h963\'s campaign (1 non-null '
            'translated card; the other real h963 cards are null kill-timeouts, unmeasurable). '
            'The canary carries ZERO {Tn} spans by construction ("pure-gloss ... zero <ls>, zero '
            '{#..#}") so it cannot exercise a TNMASK multiset mismatch either way -- it proves '
            'nothing about the false-flag rate. TNMASK\'s check runs on the PRE-restore candidate '
            'vs the masked source skeleton; the promoted store holds only POST-restore text, so '
            'no real (non-synthetic) historical card retains that pairing. A repo-wide search '
            'found zero non-zero tnmask_mismatches readings anywhere and zero residual literal '
            '{Tn} tokens across all 11603 promoted rows (independently corroborating the H1110 '
            'C-42 finding).'
        ),
        'flagged': 0,
        'true_drop': 0,
        'false_flag': 0,
        'examples': [],
        'mechanism': 'not measurable from frozen evidence -- see denominator_note',
        'recommendation': 'DO_NOT_ARM',
        'reason': (
            'Insufficient evidence, not a favorable-looking guard: zero usable frozen '
            '(pre-restore-candidate, masked-skeleton) pairs exist to compute a false-flag rate '
            'from. Arming a guard with no measured false-flag rate is not defensible regardless '
            'of how the guard is expected to behave.'
        ),
    }

    out = {
        'schema': 'pwg_ru.softguard_falseflag_rate.v1',
        'measured': '2026-07-18',
        'manifest_verification': {
            'verified_ok': len(manifest['ok']),
            'missing_gitignored_not_consumed': manifest['missing_gitignored'],
            'mismatch': manifest['mismatch'],
        },
        'store': {'path': store_path, 'rows': total_rows, 'cards': len(cards)},
        'sanloss': sanloss,
        'tnmask': tnmask,
        'limit': (
            'Frozen evidence is a sample of ONE route (pwg PWG->RU headword translation) under '
            'ONE payload regime (the h963/current gen_opt_harness2.py masked-inline batching '
            'prompt). This rate BOUNDS the false-flag class observable in that frozen sample; it '
            'does NOT prove the live rate under other routes, payload shapes, or model behavior '
            'not represented in the 11603-row promoted store. A human decides whether that bound '
            'is enough to arm on -- this measurement recommends but never arms (SANLOSS_HARD_'
            'REJECT and TNMASK_HARD_REJECT are both left `= false`, unchanged, by this script).'
        ),
        'arming_note': (
            'This report MEASURES; it does not ARM. SANLOSS_HARD_REJECT and TNMASK_HARD_REJECT '
            'in gen_opt_harness2.py are both untouched by this script and remain `false`. Arming '
            'either is a human @DECIDE, owner-gated at the const, and pinned as a literal-needle '
            'assertion by window_selftest.py.'
        ),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tmp = args.out + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, args.out)
    print('\nwrote', args.out)
    print('SANLOSS: flagged=%d true_drop=%d false_flag=%d denom=%d -> %s' % (
        sanloss['flagged'], sanloss['true_drop'], sanloss['false_flag'], sanloss['denominator'],
        sanloss['recommendation']))
    print('TNMASK: flagged=%d true_drop=%d false_flag=%d denom=%d -> %s' % (
        tnmask['flagged'], tnmask['true_drop'], tnmask['false_flag'], tnmask['denominator'],
        tnmask['recommendation']))


if __name__ == '__main__':
    main()
