#!/usr/bin/env python
r"""H1651: pwg_ru store wrapper-defect sweep (D1 Cyrillic-in-{#..#}, D3 gloss-wrapper drift).

D1 -- {#..#} is the Sanskrit/SLP1 citation wrapper: transliterated Sanskrit is always
Latin+diacritics, never Cyrillic. A Cyrillic word inside {#..#} means the model wrapped a
Russian gloss in the Sanskrit delimiter instead of the gloss delimiter {%..%}. A store audit
(26-07-2026) found 34 live instances, all pure-Cyrillic gloss content -- no genuine Sanskrit
was ever mixed in, so the repair is a mechanical delimiter swap, never a requeue: keep the
content, change {# #} -> {% %}. The live gate (prompt_rule_audit.markup_sigla_risks,
`cyrillic_in_sanskrit_wrapper`, HIGH_CONFIDENCE) stops this class recurring in future
generations; this script is the one-time backfill for the rows already in the store.

D3 -- 338 rows where the DE {%..%} gloss-wrapper convention became RU guillemets <<...>>
instead of {%..%}. Report-only here (`--d3-report`): the mechanical substitution is withheld
until the convention is ruled (see H1651 handoff D3).

Usage::

    python src/wrapper_defect_sweep.py --d1-report          # store dry-run, D1 only
    python src/wrapper_defect_sweep.py --d1-apply           # safe store apply, D1 only
    python src/wrapper_defect_sweep.py --d3-report          # store dry-run, D3 count only
    python src/wrapper_defect_sweep.py --selftest
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
PILOT = os.path.join(HERE, 'pilot')
if PILOT not in sys.path:
    sys.path.insert(0, PILOT)

from store_path import canonical_store  # noqa: E402
from ru_style_sweep import (  # noqa: E402
    _create_verified_backup, _file_sha256, _read_rows, _row_label, _write_rows_atomic,
)
import prompt_rule_audit as pra  # noqa: E402

SANSKRIT_SPAN_CONTENT = pra.SANSKRIT_SPAN_CONTENT
CYR_WORD = pra.CYR_WORD
BRACED_GLOSS = pra.BRACED_GLOSS
GUILLEMET = pra.GUILLEMET_GLOSS


def d1_repair_text(text):
    """Swap {#Cyrillic#} -> {%Cyrillic%}; genuine Sanskrit {#..#} spans are untouched."""
    if not text or '{#' not in text:
        return text, 0

    counter = []

    def repl(match):
        content = match.group(1)
        if CYR_WORD.search(content):
            counter.append(1)
            return '{%' + content + '%}'
        return match.group(0)

    new_text = SANSKRIT_SPAN_CONTENT.sub(repl, text)
    return new_text, len(counter)


def d1_scan_row(row):
    return d1_repair_text(row.get('ru') or '')[1]


def d3_scan_row(row):
    """Count DE {%..%} gloss positions whose RU counterpart rendered as <<...>> guillemets
    instead of {%..%} -- report-only count, no repair (D3 needs a convention ruling first).

    A raw "DE has a gloss AND RU has any guillemet" test overcounts: guillemets are also
    legitimate ordinary Russian quotation marks unrelated to a converted gloss. Instead,
    count only the {%..%} wrappers RU is actually missing relative to DE (the
    `markup_wrapper_dropped` deficit already tracked by prompt_rule_audit.markup_sigla_risks),
    capped at how many guillemet spans RU actually has to have absorbed them -- the
    conservative, positionally-blind estimate of how many DE gloss positions could plausibly
    have landed as a guillemet instead of vanishing outright."""
    de = row.get('de') or ''
    ru = row.get('ru') or ''
    missing = len(BRACED_GLOSS.findall(de)) - len(BRACED_GLOSS.findall(ru))
    if missing <= 0:
        return 0
    return min(missing, len(GUILLEMET.findall(ru)))


def run_d1(apply_=False, backup_dir=None):
    store = os.path.abspath(canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl')))
    print('resolved store  : %s' % store)
    if not os.path.exists(store):
        raise FileNotFoundError('STORE ABSENT: %s' % store)
    initial_hash = _file_sha256(store)
    rows = _read_rows(store)
    touched_rows, total_spans, samples = [], 0, []
    for row in rows:
        original = row.get('ru') or ''
        repaired, n = d1_repair_text(original)
        if n:
            total_spans += n
            touched_rows.append(_row_label(row))
            if len(samples) < 10:
                samples.append((_row_label(row), original[:100], repaired[:100]))
            if apply_:
                row['ru'] = repaired
    print('mode            : %s' % ('APPLY' if apply_ else 'DRY RUN'))
    print('rows            : %d' % len(rows))
    print('rows touched    : %d' % len(touched_rows))
    print('spans repaired  : %d' % total_spans)
    for label, before, after in samples:
        print('  %-32s %r -> %r' % (label, before, after))
    if apply_ and total_spans:
        backup = _write_rows_atomic(store, rows, initial_hash, backup_dir=backup_dir)
        print('backup          : %s' % backup['path'])
        print('backup sha256   : %s' % backup['sha256'])
        print('wrote           : %s' % store)
    elif not apply_:
        print('(dry run -- pass --d1-apply to write)')
    return {'rows_touched': touched_rows, 'spans': total_spans}


def run_d3_report():
    store = os.path.abspath(canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl')))
    print('resolved store  : %s' % store)
    rows = _read_rows(store)
    hit_rows, total = [], 0
    for row in rows:
        n = d3_scan_row(row)
        if n:
            total += n
            hit_rows.append(_row_label(row))
    print('D3 candidate rows: %d' % len(hit_rows))
    print('D3 guillemet spans: %d' % total)
    return {'rows': hit_rows, 'spans': total}


def selftest():
    fixed, n = d1_repair_text('{#полагать, думать#}: {#mfto vetti#}')
    assert n == 1, (fixed, n)
    assert fixed == '{%полагать, думать%}: {#mfto vetti#}', fixed
    # genuine Sanskrit span untouched
    fixed, n = d1_repair_text('{#mfto vetti#} значит "знать"')
    assert n == 0 and fixed == '{#mfto vetti#} значит "знать"', fixed
    # already-correct {%..%} gloss untouched, mixed with a real Sanskrit span
    text = '{%полагать%}: {#mfto vetti#}'
    fixed, n = d1_repair_text(text)
    assert n == 0 and fixed == text, fixed
    # multiple Cyrillic spans in one row all repaired
    text = '{#жечь#} {#гореть#} {#kar#}'
    fixed, n = d1_repair_text(text)
    assert n == 2 and fixed == '{%жечь%} {%гореть%} {#kar#}', (fixed, n)
    # empty / no-wrapper text is a no-op
    assert d1_repair_text('') == ('', 0)
    assert d1_repair_text('просто текст') == ('просто текст', 0)
    print('wrapper_defect_sweep selftest: PASS')
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selftest', action='store_true')
    parser.add_argument('--d1-report', action='store_true')
    parser.add_argument('--d1-apply', action='store_true')
    parser.add_argument('--d3-report', action='store_true')
    parser.add_argument('--backup-dir')
    parser.add_argument('--json-out')
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return 0
    result = None
    if args.d1_report:
        result = run_d1(apply_=False)
    elif args.d1_apply:
        result = run_d1(apply_=True, backup_dir=args.backup_dir)
    elif args.d3_report:
        result = run_d3_report()
    else:
        parser.error('pass one of --d1-report/--d1-apply/--d3-report/--selftest')
    if args.json_out and result is not None:
        with open(args.json_out, 'w', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
